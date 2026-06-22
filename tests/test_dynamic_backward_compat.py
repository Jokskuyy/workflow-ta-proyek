"""Backward-compatibility + integration + scope tests for the
dynamic-generation-pipeline spec.

Spec: .kiro/specs/dynamic-generation-pipeline

Covers:
  * 12.1 (Property 17) - the current document's caption-number SET equals the
    captured Dokumen_Referensi baseline (reads the existing docx; no rebuild).
  * 12.2 integration  - run the validator on the current docx via run_validator;
    expect exit 0 / VALIDATION SUCCESSFUL with no new fatal errors vs the
    reference validator summary. (No Word build is run here -- only the validator
    on the existing docx, to stay fast and deterministic.)
  * 12.3 scope guard  - the dynamic refactor's runtime scripts are the two
    generation scripts only; the validator + image injector still exist and the
    scratch/skills copies remain byte-identical (filecmp).
  * 7.4 format integration - a tiny in-memory document run through the pure
    helpers (chapter tracking + CaptionRegistry + parse_caption_text +
    rewrite_references) asserts per-chapter numbering, SEQ restart, verbatim
    descriptions and reference rewriting -- without invoking Word.

The existing image-injection suite is NOT modified; this is a brand-new file.
"""
import filecmp
import json
import sys
from pathlib import Path

import lxml.etree as ET
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Paths + imports.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / "scratch"
SKILLS = ROOT / "skills" / "scripts"
FIXTURES = ROOT / "tests" / "fixtures"
sys.path.insert(0, str(SCRATCH))
sys.path.insert(0, str(SKILLS))

import capture_reference_baseline as cap  # noqa: E402  (scratch/)
import format_ta_proyek as fmt  # noqa: E402  (skills/scripts/)

CURRENT_DOCX = ROOT / "Tugas_Akhir_Formatted.docx"
VALIDATOR = SCRATCH / "validate_docx_structure.py"
REF_CAPTIONS = FIXTURES / "reference_caption_numbers.json"
REF_VALIDATOR = FIXTURES / "reference_validator_summary.json"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


def make_par(text=None, style=None):
    p = ET.Element("{%s}p" % W)
    if style is not None:
        pPr = ET.SubElement(p, "{%s}pPr" % W)
        pStyle = ET.SubElement(pPr, "{%s}pStyle" % W)
        pStyle.set("{%s}val" % W, style)
    if text is not None:
        r = ET.SubElement(p, "{%s}r" % W)
        t = ET.SubElement(r, "{%s}t" % W)
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        t.text = text
    return p


# =========================================================================== #
# Property 17 (task 12.1): current caption numbers == Dokumen_Referensi baseline
# =========================================================================== #
# Feature: dynamic-generation-pipeline, Property 17: the set of caption numbers in
# the current output equals the captured reference set (order/duplication invariant).
# Validates: Requirements 8.4
@pytest.mark.skipif(not CURRENT_DOCX.exists(), reason="current formatted docx missing")
@pytest.mark.skipif(not REF_CAPTIONS.exists(), reason="reference caption fixture missing")
def test_property17_caption_numbers_match_reference_baseline():
    reference = set(json.loads(REF_CAPTIONS.read_text(encoding="utf-8"))["caption_numbers"])
    texts = cap.extract_caption_texts(CURRENT_DOCX)
    current = cap.collect_caption_numbers(texts)
    # The output caption-number set is identical to the reference set.
    assert current == reference


# The pure collector is order- and duplication-invariant: for any permutation /
# duplication of the caption texts it yields the same set, equal to the baseline.
if CURRENT_DOCX.exists() and REF_CAPTIONS.exists():
    _CAPTION_TEXTS = cap.extract_caption_texts(CURRENT_DOCX)
    _REFERENCE_SET = set(json.loads(REF_CAPTIONS.read_text(encoding="utf-8"))["caption_numbers"])

    @settings(max_examples=100, deadline=None,
              suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(data=st.data())
    def test_property17_collector_order_and_duplication_invariant(data):
        shuffled = data.draw(st.permutations(_CAPTION_TEXTS))
        dups = list(shuffled) + list(shuffled)  # duplicate every caption text
        assert cap.collect_caption_numbers(shuffled) == _REFERENCE_SET
        assert cap.collect_caption_numbers(dups) == _REFERENCE_SET


# =========================================================================== #
# 12.2 integration: run the validator on the current docx; expect success and no
# new fatal errors vs the reference summary. (Validator only -- no Word build.)
# =========================================================================== #
@pytest.mark.skipif(not CURRENT_DOCX.exists(), reason="current formatted docx missing")
@pytest.mark.skipif(not VALIDATOR.exists(), reason="validator script missing")
def test_integration_validator_on_current_docx_succeeds():
    exit_code, output = cap.run_validator(ROOT, VALIDATOR, CURRENT_DOCX)
    assert exit_code == 0, output[-2000:]
    assert "VALIDATION SUCCESSFUL" in output
    assert "VALIDATION FAILED" not in output

    summary = cap.summarize_validator_output(exit_code, output)
    assert summary["success"] is True
    assert summary["failed_marker_present"] is False
    assert summary["error_count"] == 0

    # No NEW fatal errors compared to the captured baseline.
    if REF_VALIDATOR.exists():
        ref = json.loads(REF_VALIDATOR.read_text(encoding="utf-8"))
        assert ref["exit_code"] == 0
        assert summary["exit_code"] == ref["exit_code"]
        assert summary["error_count"] <= ref["error_count"]


# =========================================================================== #
# 12.3 scope guard: runtime generation scripts are the two generation scripts;
# validator + injector are unchanged (scratch/skills copies byte-identical).
# =========================================================================== #
def test_scope_guard_generation_scripts_exist():
    # The two generation (refactored) scripts exist in both runtime locations.
    assert (SKILLS / "format_ta_proyek.py").exists()
    assert (SCRATCH / "merge_draft_to_docx.py").exists()
    assert (SKILLS / "merge_draft_to_docx.py").exists()


def test_scope_guard_validator_and_injector_still_present():
    # The non-goal scripts (validator + image injector) still exist in both dirs.
    for name in ("validate_docx_structure.py", "inject_all_images.py"):
        assert (SCRATCH / name).exists(), name
        assert (SKILLS / name).exists(), name


@pytest.mark.parametrize("name", [
    "merge_draft_to_docx.py",        # generation script: kept in sync (task 11)
    "validate_docx_structure.py",    # non-goal: unchanged
    "inject_all_images.py",          # non-goal: unchanged
])
def test_scope_guard_scratch_skills_copies_byte_identical(name):
    # The scratch and skills copies are byte-identical -- only location differs.
    assert filecmp.cmp(SCRATCH / name, SKILLS / name, shallow=False), name


# =========================================================================== #
# 7.4 format integration: tiny in-memory document run through the pure helpers.
# =========================================================================== #
def _simulate_format_pass(children):
    """Mimic Mesin_Format Phase 1 (chapter-aware caption pass) + Phase 2 build:
    walk children in reading order, track the enclosing BAB chapter, number
    captions per-chapter via CaptionRegistry, and record verbatim descriptions.
    Returns (registry, captions, rewritten_narratives)."""
    reg = fmt.CaptionRegistry()
    current = None
    captions = []  # (kind, new_number, default_val, is_first, desc)
    narratives = []
    for p in children:
        style = fmt._paragraph_style(p, NS)
        text = fmt._paragraph_text(p, NS)
        if style == "Heading1":
            n = fmt.parse_chapter_number(text)
            if n is not None:
                current = n
            continue
        parsed = fmt.parse_caption_text(text) if style == "Caption" else None
        if parsed is not None:
            label, old, desc = parsed
            chapter = current if current is not None else 1  # fallback rule
            if label == "Gambar":
                new_num, default_val, is_first = reg.next_figure(chapter, old)
            else:
                new_num, default_val, is_first = reg.next_table(chapter, old)
            captions.append((label, new_num, default_val, is_first, desc))
        elif style == "Normal":
            narratives.append(text)
    return reg, captions, narratives


def test_format_integration_three_phase_on_synthetic_document():
    children = [
        make_par("DAFTAR ISI", style="Heading1"),                       # front matter
        make_par("BAB II RANCANGAN PROYEK", style="Heading1"),          # chapter 2
        make_par("Gambar 2.1 Arsitektur Sistem", style="Caption"),      # fig 2.1
        make_par("Tabel 2.1 Spesifikasi Perangkat", style="Caption"),   # tbl 2.1
        make_par("Gambar 2.2 Diagram Use Case", style="Caption"),       # fig 2.2
        make_par("Analisis Sistem yang Sedang Berjalan", style="Normal"),  # R3.4: NOT a caption
        make_par("Lihat Gambar 2.1 dan Gambar 2.2 untuk detail.", style="Normal"),
        make_par("BAB III IMPLEMENTASI", style="Heading1"),             # chapter 3
        make_par("Gambar 3.5 Tampilan Login", style="Caption"),         # old 3.5 -> fig 3.1
        make_par("Seperti pada Gambar 3.5 ditunjukkan hasilnya.", style="Normal"),
    ]

    reg, captions, narratives = _simulate_format_pass(children)

    # Per-chapter numbering + SEQ restart (is_first) + verbatim descriptions.
    assert captions[0] == ("Gambar", "2.1", 1, True, "Arsitektur Sistem")
    assert captions[1] == ("Tabel", "2.1", 1, True, "Spesifikasi Perangkat")
    assert captions[2] == ("Gambar", "2.2", 2, False, "Diagram Use Case")
    # BAB III figure restarts at 1 (first figure in chapter 3), old 3.5 -> 3.1.
    assert captions[3] == ("Gambar", "3.1", 1, True, "Tampilan Login")

    # R3.4: the old named-section trigger is just narrative -- no caption created.
    assert ("Gambar", "3.5", 1, True, "Tampilan Login") not in captions
    assert sum(1 for c in captions if c[0] == "Gambar") == 3
    assert sum(1 for c in captions if c[0] == "Tabel") == 1

    # Registry remap derived from the document (Phase 2 source of truth).
    assert reg.fig_remap["2.1"] == "2.1"
    assert reg.fig_remap["3.5"] == "3.1"
    assert reg.tbl_remap["2.1"] == "2.1"

    # Phase 2: reference rewriter applies the registry-derived remap. Narratives
    # are selected by content (the "Analisis..." line is also a Normal paragraph).
    ref_para = next(t for t in narratives if t.startswith("Lihat Gambar"))
    n0, w0 = fmt.rewrite_references(ref_para, reg.fig_remap, reg.tbl_remap)
    assert n0 == "Lihat Gambar 2.1 dan Gambar 2.2 untuk detail."
    assert w0 == []
    old_para = next(t for t in narratives if t.startswith("Seperti pada"))
    n1, w1 = fmt.rewrite_references(old_para, reg.fig_remap, reg.tbl_remap)
    assert n1 == "Seperti pada Gambar 3.1 ditunjukkan hasilnya."
    assert w1 == []


def test_format_integration_fallback_without_bab_one():
    """Captions before any BAB heading fall back to chapter 1 (no exception)."""
    children = [
        make_par("KATA PENGANTAR", style="Heading1"),
        make_par("Gambar 1 Logo Institusi", style="Caption"),  # no enclosing BAB -> chap 1
        make_par("Tabel 1 Daftar Singkatan", style="Caption"),
    ]
    reg, captions, _ = _simulate_format_pass(children)
    assert captions[0][:4] == ("Gambar", "1.1", 1, True)
    assert captions[1][:4] == ("Tabel", "1.1", 1, True)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
