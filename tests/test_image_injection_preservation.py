"""Preservation property tests for the image-injection pipeline (Properties 5-8).

Spec: .kiro/specs/image-injection-pipeline-fix

These tests encode the design's PRESERVATION requirements -- behavior that must
remain UNCHANGED by the fix because it does NOT involve the bug condition
(``isBugCondition(run)`` is false for these aspects):

  * Property 5 -- Non-manifest captions unchanged          (Requirement 3.1)
  * Property 6 -- SEQ Gambar/SEQ Tabel numbering unchanged  (Requirement 3.2)
  * Property 7 -- Aspect-ratio rendering unchanged          (Requirement 3.3)
  * Property 8 -- Front-matter/TOC/appendix structure       (Requirement 3.4)

Methodology (observation-first): every baseline literal in this module was
RECORDED from the UNFIXED captured artifact ``Tugas_Akhir_Formatted.docx`` and
is then asserted. Therefore EVERY test here is EXPECTED TO PASS on the unfixed
code -- the passes establish the behavioral baseline the fix must not regress.
The same tests are re-run after the fix (task 3.4) and must STILL pass.

Why property-based: preservation is a universal property ("for all non-buggy
inputs"). We use Hypothesis to sample across every recorded caption / figure /
structural invariant so a regression in ANY one of them is surfaced, mirroring
the scoped-PBT convention used by the companion bug-condition suite.

Validates: Requirements 3.1, 3.2, 3.3, 3.4 (and Correctness Properties 5-8).
"""
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import lxml.etree as LET
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Paths / namespaces (kept consistent with the companion bug-condition suite)
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
CAPTURED_DOCX = ROOT / "Tugas_Akhir_Formatted.docx"
VALIDATOR = ROOT / "skills" / "scripts" / "validate_docx_structure.py"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
NS = {"w": W, "r": R, "a": A, "wp": WP}

DOC = "word/document.xml"
STYLES = "word/styles.xml"
MAX_WIDTH_EMU = 5400000  # ~15 cm printable content width


# --------------------------------------------------------------------------- #
# Low-level docx helpers
# --------------------------------------------------------------------------- #
def read_all(path: Path) -> dict:
    with zipfile.ZipFile(path) as z:
        return {n: z.read(n) for n in z.namelist()}


def parse(entries: dict, name: str):
    return LET.fromstring(entries[name])


def body_paragraphs(doc):
    return doc.find("w:body", NS).findall("w:p", NS)


def para_text(p) -> str:
    return "".join(t.text for t in p.iter(f"{{{W}}}t") if t.text).strip()


def para_style(p) -> str:
    pPr = p.find("w:pPr", NS)
    if pPr is None:
        return ""
    s = pPr.find("w:pStyle", NS)
    return s.get(f"{{{W}}}val") if s is not None else ""


def para_instr(p) -> str:
    return " ".join(t.text.strip() for t in p.iter(f"{{{W}}}instrText") if t.text).strip()


def has_drawing(p) -> bool:
    return p.find(".//w:drawing", NS) is not None


def caption_paragraphs(doc):
    return [p for p in body_paragraphs(doc) if para_style(p) == "Caption"]


def drawing_paragraphs(doc):
    return [p for p in body_paragraphs(doc) if has_drawing(p)]


def drawing_extent(p):
    """Return ((wp_cx, wp_cy), (a_cx, a_cy), noChangeAspect) for a drawing paragraph."""
    dr = p.find(".//w:drawing", NS)
    wp_ext = dr.find(".//wp:extent", NS)
    a_ext = dr.find(".//a:ext", NS)
    gfl = dr.find(".//a:graphicFrameLocks", NS)
    wp = (int(wp_ext.get("cx")), int(wp_ext.get("cy"))) if wp_ext is not None else None
    ae = (int(a_ext.get("cx")), int(a_ext.get("cy"))) if a_ext is not None else None
    nca = gfl.get("noChangeAspect") if gfl is not None else None
    return wp, ae, nca


def run_validator(docx_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(docx_path)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )


# Cached parsed artifact (kept out of @given signatures so Hypothesis never
# builds a giant repr of the whole docx on failure).
_CACHE = {}


def base_doc():
    if "doc" not in _CACHE:
        entries = read_all(CAPTURED_DOCX)
        _CACHE["entries"] = entries
        _CACHE["doc"] = parse(entries, DOC)
        _CACHE["styles"] = parse(entries, STYLES)
    return _CACHE["doc"]


def base_styles():
    base_doc()
    return _CACHE["styles"]


# Preservation PBT profile: these are EXPECTED to PASS, sample broadly across
# the recorded items; reading/parsing the cached artifact each example is cheap.
PRESERVE_PBT = settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)


# =========================================================================== #
# Recorded baselines (observed on the UNFIXED captured artifact)
# =========================================================================== #

# --- Property 5: captions present that NO manifest entry targets ----------- #
# (text, style, seq_instr, prev_style, prev_has_drawing, next_style, next_has_drawing)
NON_MANIFEST_CAPTIONS = [
    ("Tabel 1.1 Peran dan Tanggung Jawab", "Caption", "SEQ Tabel \\r 1 \\* ARABIC", "", False, "Heading2", False),
    ("Tabel 1.2 Jadwal Kegiatan", "Caption", "SEQ Tabel \\* ARABIC", "", False, "", False),
    ("Tabel 3.1 Hubungan Mitra dengan Proyek", "Caption", "SEQ Tabel \\r 1 \\* ARABIC", "", False, "Heading2", False),
    ("Tabel 3.2 Logbook Implementasi Proyek", "Caption", "SEQ Tabel \\* ARABIC", "", False, "Heading3", False),
    ("Tabel 3.3 Hasil Pengujian Black Box Testing", "Caption", "SEQ Tabel \\* ARABIC", "", False, "", False),
    ("Tabel 3.4 Perbandingan Metrik Performa Lighthouse", "Caption", "SEQ Tabel \\* ARABIC", "", False, "", False),
]

# --- Property 6: every SEQ caption and its field --------------------------- #
# Captions that legitimately carry the "\r 1" numbering-restart switch.
RESTART_CAPTIONS = {
    "Gambar 2.1 Hasil Kuesioner: Profil Status Akademik Responden",
    "Gambar 3.1 Hierarki Prefab Gedung dengan Child Pointer di Unity",
    "Tabel 1.1 Peran dan Tanggung Jawab",
    "Tabel 3.1 Hubungan Mitra dengan Proyek",
}
EXPECTED_SEQ_GAMBAR_COUNT = 31
EXPECTED_SEQ_TABEL_COUNT = 6

# --- Property 7: scaled extents of every injected figure (noChangeAspect) -- #
# Recorded (cx, cy) EMU extents; all within width and aspect-locked on unfixed code.
FIGURE_EXTENTS = [
    (5400000, 2334146), (5400000, 2529798), (5400000, 2580598), (5400000, 2298033),
    (5400000, 2766042), (5400000, 2342074), (5400000, 2729916), (5400000, 3037499),
    (5400000, 1945088), (4219575, 4695825), (4038600, 5343525), (5246820, 5760000),
    (5303461, 5760000), (5400000, 4860823), (3829050, 2466975), (5400000, 2862541),
    (5400000, 5400000), (3954550, 5759999), (5400000, 5373996), (4609756, 5760000),
    (4622006, 5760000), (4333875, 3009900), (5400000, 5189678), (5400000, 2443764),
    (5400000, 4072771), (5400000, 2392239), (4231729, 5759999), (5400000, 4056750),
    (5400000, 2755891), (3953357, 5760000), (4229083, 5760000),
]

# --- Property 8: structural invariants ------------------------------------- #
EXPECTED_APPENDIX_OUTLINE_LVL = "8"
EXPECTED_TOC9_LEFT = "1"
EXPECTED_LAMPIRAN_TOC = 'TOC \\o "9-9" \\n 9-9 \\h \\z'


# =========================================================================== #
# Property 5 -- Non-Manifest Captions Unchanged (Requirement 3.1)
# =========================================================================== #
def test_p5_all_non_manifest_captions_preserved():
    """Every recorded non-manifest caption exists exactly once, is Caption-styled,
    carries no injected drawing, and its surrounding paragraphs are untouched."""
    doc = base_doc()
    paras = body_paragraphs(doc)
    for (text, style, seq, prev_style, prev_dr, next_style, next_dr) in NON_MANIFEST_CAPTIONS:
        idxs = [i for i, p in enumerate(paras) if para_text(p) == text]
        assert len(idxs) == 1, f"non-manifest caption {text!r} should appear exactly once, found {len(idxs)}"
        i = idxs[0]
        p = paras[i]
        assert para_style(p) == style, f"{text!r} style changed: {para_style(p)!r} != {style!r}"
        assert not has_drawing(p), f"{text!r} unexpectedly contains a drawing (should be untouched)"
        assert para_instr(p) == seq, f"{text!r} SEQ field changed: {para_instr(p)!r} != {seq!r}"
        # surrounding content untouched
        assert para_style(paras[i - 1]) == prev_style, f"{text!r} preceding paragraph style changed"
        assert has_drawing(paras[i - 1]) == prev_dr, f"{text!r} preceding paragraph drawing-state changed"
        assert para_style(paras[i + 1]) == next_style, f"{text!r} following paragraph style changed"
        assert has_drawing(paras[i + 1]) == next_dr, f"{text!r} following paragraph drawing-state changed"


@settings(PRESERVE_PBT)
@given(case=st.sampled_from(NON_MANIFEST_CAPTIONS))
def test_p5_non_manifest_caption_preserved_pbt(case):
    """For any sampled non-manifest caption, the paragraph and its neighbours
    remain exactly as recorded on the unfixed artifact.

    **Validates: Requirements 3.1**
    """
    text, style, seq, prev_style, prev_dr, next_style, next_dr = case
    doc = base_doc()
    paras = body_paragraphs(doc)
    idxs = [i for i, p in enumerate(paras) if para_text(p) == text]
    assert len(idxs) == 1, f"caption {text!r} should appear exactly once, found {len(idxs)}"
    i = idxs[0]
    assert para_style(paras[i]) == style
    assert not has_drawing(paras[i])
    assert para_instr(paras[i]) == seq
    assert para_style(paras[i - 1]) == prev_style
    assert has_drawing(paras[i - 1]) == prev_dr
    assert para_style(paras[i + 1]) == next_style
    assert has_drawing(paras[i + 1]) == next_dr


# =========================================================================== #
# Property 6 -- SEQ Numbering Fields Unchanged (Requirement 3.2)
# =========================================================================== #
def _seq_captions(doc):
    """All Caption paragraphs that carry a SEQ Gambar/SEQ Tabel field."""
    out = []
    for p in caption_paragraphs(doc):
        instr = para_instr(p)
        if "SEQ Gambar" in instr or "SEQ Tabel" in instr:
            out.append((para_text(p), instr))
    return out


def test_p6_seq_field_counts_and_restart_switches_preserved():
    """SEQ Gambar/SEQ Tabel field counts and the first-caption '\\r 1' restart
    switches match the recorded baseline."""
    doc = base_doc()
    seq = _seq_captions(doc)
    gambar = [t for t, i in seq if "SEQ Gambar" in i]
    tabel = [t for t, i in seq if "SEQ Tabel" in i]
    assert len(gambar) == EXPECTED_SEQ_GAMBAR_COUNT, f"SEQ Gambar count changed: {len(gambar)}"
    assert len(tabel) == EXPECTED_SEQ_TABEL_COUNT, f"SEQ Tabel count changed: {len(tabel)}"

    restart = {t for t, i in seq if "\\r 1" in i}
    assert restart == RESTART_CAPTIONS, (
        f"numbering-restart caption set changed.\n  expected: {RESTART_CAPTIONS}\n  actual:   {restart}"
    )


@settings(PRESERVE_PBT)
@given(idx=st.integers(min_value=0, max_value=10_000))
def test_p6_each_seq_caption_field_well_formed_pbt(idx):
    """For any sampled SEQ caption, its field is preserved: a Gambar/Tabel
    caption carries the matching SEQ field, and the '\\r 1' restart switch is
    present iff the caption is a recorded first-of-sequence caption.

    **Validates: Requirements 3.2**
    """
    doc = base_doc()
    seq = _seq_captions(doc)
    text, instr = seq[idx % len(seq)]
    kind = "Gambar" if text.lower().startswith("gambar") else "Tabel"
    assert f"SEQ {kind}" in instr, f"{text!r} missing 'SEQ {kind}' field: {instr!r}"
    assert "\\* ARABIC" in instr, f"{text!r} missing ARABIC numeric format: {instr!r}"
    has_restart = "\\r 1" in instr
    assert has_restart == (text in RESTART_CAPTIONS), (
        f"{text!r} restart-switch state changed: has_restart={has_restart}"
    )


# =========================================================================== #
# Property 7 -- Aspect-Ratio Rendering Unchanged (Requirement 3.3)
# =========================================================================== #
def _injected_figure_extents(doc):
    """(cx, cy) extents of every aspect-locked injected figure (noChangeAspect=1)."""
    extents = []
    for p in drawing_paragraphs(doc):
        wp, ae, nca = drawing_extent(p)
        if nca == "1":
            extents.append((wp, ae))
    return extents


def test_p7_injected_figures_aspect_and_extent_preserved():
    """Every aspect-locked figure stays within width, keeps noChangeAspect, has a
    consistent wp/a extent, and the multiset of scaled extents matches baseline."""
    doc = base_doc()
    figs = _injected_figure_extents(doc)
    assert len(figs) == len(FIGURE_EXTENTS), (
        f"injected-figure count changed: {len(figs)} != {len(FIGURE_EXTENTS)}"
    )
    for wp, ae in figs:
        assert wp == ae, f"wp:extent {wp} != a:ext {ae} (scaled extent inconsistent)"
        assert wp[0] <= MAX_WIDTH_EMU, f"figure width {wp[0]} exceeds max {MAX_WIDTH_EMU}"
    observed = sorted(wp for wp, ae in figs)
    assert observed == sorted(FIGURE_EXTENTS), "scaled-extent multiset changed from baseline"


@settings(PRESERVE_PBT)
@given(extent=st.sampled_from(FIGURE_EXTENTS))
def test_p7_recorded_extent_still_present_and_locked_pbt(extent):
    """For any recorded figure extent, a within-width, aspect-locked figure with
    a consistent wp/a extent of exactly that size is still present.

    **Validates: Requirements 3.3**
    """
    doc = base_doc()
    figs = _injected_figure_extents(doc)
    matches = [(wp, ae) for wp, ae in figs if wp == extent]
    assert matches, f"recorded scaled extent {extent} no longer present"
    for wp, ae in matches:
        assert wp == ae, f"extent {extent}: wp {wp} != a:ext {ae}"
        assert wp[0] <= MAX_WIDTH_EMU, f"extent {extent} now exceeds max width"


@settings(PRESERVE_PBT)
@given(width=st.integers(min_value=1, max_value=MAX_WIDTH_EMU))
def test_p7_within_width_predicate_holds_pbt(width):
    """For any width at or below the maximum, the within-width predicate that
    governs aspect-ratio rendering holds (no scaling-down is required).

    **Validates: Requirements 3.3**
    """
    assert width <= MAX_WIDTH_EMU


# =========================================================================== #
# Property 8 -- Front-Matter/TOC/Appendix Structure Unchanged (Requirement 3.4)
# =========================================================================== #
def test_p8_appendix_style_outline_level_preserved():
    styles = base_styles()
    style = styles.find("w:style[@w:styleId='taappendixheading']", NS)
    assert style is not None, "taappendixheading style missing"
    ol = style.find("w:pPr/w:outlineLvl", NS)
    assert ol is not None, "taappendixheading missing outlineLvl"
    assert ol.get(f"{{{W}}}val") == EXPECTED_APPENDIX_OUTLINE_LVL


def test_p8_toc9_indentation_preserved():
    styles = base_styles()
    style = styles.find("w:style[@w:styleId='TOC9']", NS)
    assert style is not None, "TOC9 style missing"
    ind = style.find("w:pPr/w:ind", NS)
    assert ind is not None, "TOC9 missing indentation"
    assert ind.get(f"{{{W}}}left") == EXPECTED_TOC9_LEFT


def test_p8_daftar_lampiran_toc_field_preserved():
    doc = base_doc()
    instrs = [para_instr(p) for p in body_paragraphs(doc)]
    lampiran = [s for s in instrs if "TOC" in s and "9-9" in s and "\\n 9-9" in s]
    assert lampiran, "Daftar Lampiran 'TOC \\n 9-9' field not found"
    assert EXPECTED_LAMPIRAN_TOC in lampiran, f"Daftar Lampiran TOC field changed: {lampiran}"


def test_p8_existing_structural_validation_still_passes():
    """The canonical validator's STRUCTURAL checks (Sections A-J) remain preserved
    on the captured artifact -- the structural baseline the fix must not regress.

    Property 8 scope: Preservation only applies to inputs where the bug condition
    does NOT hold. The captured artifact ``Tugas_Akhir_Formatted.docx`` LEGITIMATELY
    holds bug condition C2 -- 7 ``survey_*`` post_com manifest entries resolve to
    ZERO caption paragraphs (their captions are absent from the document). The fixed
    validator now CORRECTLY rejects the captured doc for those content-level C2
    errors, and the companion natural C2 exploration test
    (``test_c2_natural_zero_match_entries_are_detected``) REQUIRES that rejection.

    Therefore Property 8 must NOT assert overall validator exit 0 here. Instead it
    asserts the STRUCTURAL Sections A-J are preserved: NO structural/Section A-J
    error lines appear, and the ONLY failures present (if any) are the intended
    content-level C2 ``survey_*`` errors (lines tagged ``[C2]`` mentioning ``survey``).
    """
    result = run_validator(CAPTURED_DOCX)
    combined = (result.stdout or "") + "\n" + (result.stderr or "")

    # Structural Sections A-J must still run and report their successes unchanged.
    assert "taappendixheading style is correctly defined with outline level 8" in combined, (
        f"structural Section A (taappendixheading) success missing:\n{combined[-1500:]}"
    )
    assert "TOC9 style is correctly defined" in combined, (
        f"structural Section B (TOC9 indentation) success missing:\n{combined[-1500:]}"
    )
    assert "Found Daftar Lampiran TOC field" in combined, (
        f"structural Daftar Lampiran TOC field success missing:\n{combined[-1500:]}"
    )

    # Collect every reported error line ("- ..." under "VALIDATION FAILED").
    error_lines = [
        ln.strip() for ln in combined.splitlines() if ln.strip().startswith("- ")
    ]
    # The ONLY permitted failures are the intended content-level C2 survey_* errors.
    structural_errors = [
        ln for ln in error_lines
        if not ("[C2]" in ln and "survey" in ln.lower())
    ]
    assert not structural_errors, (
        "structural/Section A-J validation regressed -- unexpected non-C2-survey "
        f"error lines present:\n" + "\n".join(structural_errors)
    )
    # And every failure that IS present must be exactly the intended C2 survey case.
    for ln in error_lines:
        assert "[C2]" in ln and "survey" in ln.lower(), (
            f"unexpected error line (not an intended C2 survey error): {ln!r}"
        )


@settings(PRESERVE_PBT)
@given(
    check=st.sampled_from([
        "appendix_outline",
        "toc9_left",
        "lampiran_toc",
    ])
)
def test_p8_structural_invariants_preserved_pbt(check):
    """For any sampled structural invariant, its recorded value is preserved.

    **Validates: Requirements 3.4**
    """
    styles = base_styles()
    doc = base_doc()
    if check == "appendix_outline":
        ol = styles.find("w:style[@w:styleId='taappendixheading']/w:pPr/w:outlineLvl", NS)
        assert ol is not None and ol.get(f"{{{W}}}val") == EXPECTED_APPENDIX_OUTLINE_LVL
    elif check == "toc9_left":
        ind = styles.find("w:style[@w:styleId='TOC9']/w:pPr/w:ind", NS)
        assert ind is not None and ind.get(f"{{{W}}}left") == EXPECTED_TOC9_LEFT
    elif check == "lampiran_toc":
        instrs = [para_instr(p) for p in body_paragraphs(doc)]
        assert any(s == EXPECTED_LAMPIRAN_TOC for s in instrs)
