"""Property + unit/integration tests for the PURE Mesin_Merge helpers of the
dynamic-generation-pipeline spec.

Spec: .kiro/specs/dynamic-generation-pipeline

Covers tasks 8.2, 8.3, 8.4 (Properties 8-10), 9.2 (Property 16), 9.3 (path unit)
and 10.2 (merge selection-policy integration) against the helpers exposed by
``scratch/merge_draft_to_docx.py``:

  normalize_assoc_text, is_caption_text, find_template_matches,
  resolve_path, read_path_config, main.

All matching/path logic is pure, so 100+ Hypothesis iterations are cheap. The
path guard tests drive ``main`` with crafted argv that fail validation BEFORE
any heavy merge runs (a non-existent draft / missing output directory). The
existing image-injection suite is NOT modified; this is a brand-new file.
"""
import inspect
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Import the merge helpers from the canonical Mesin_Merge script.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / "scratch"
sys.path.insert(0, str(SCRATCH))

import merge_draft_to_docx as mrg  # noqa: E402

# --------------------------------------------------------------------------- #
# Strategies: descriptive phrases (>=15 chars when prefixed), caption/body texts.
# --------------------------------------------------------------------------- #
_WORDS = ["arsitektur", "sistem", "informasi", "diagram", "use", "case", "login",
          "gedung", "data", "modul", "integrasi", "backend", "unity", "sequence",
          "autentikasi", "rancangan", "tampilan", "halaman", "pengguna"]
_phrase = st.lists(st.sampled_from(_WORDS), min_size=2, max_size=6).map(" ".join)


def _t(s, upper, pad):
    """Case/whitespace transform that is safe w.r.t. the 15-char strip guard
    (leading/trailing pad is removed by strip; casing preserves length)."""
    core = s.upper() if upper else s.lower()
    return pad + core + pad


# =========================================================================== #
# Property 8: Pencocokan invarian terhadap kapitalisasi, spasi, nama berkas
# =========================================================================== #
# Feature: dynamic-generation-pipeline, Property 8: the matching decision does not
# change under capitalization/whitespace normalization, and does not depend on the
# target image filename (find_template_matches takes no target_img at all).
# Validates: Requirements 4.1, 4.2
@settings(max_examples=200, deadline=None)
@given(
    assoc_cap=st.booleans(), assoc_phrase=_phrase,
    cands=st.lists(st.tuples(st.booleans(), _phrase), min_size=0, max_size=6),
    upper=st.booleans(), pad=st.sampled_from(["", " ", "  ", "\t", " \t "]),
)
def test_property8_matching_invariant_to_case_and_whitespace(
    assoc_cap, assoc_phrase, cands, upper, pad
):
    assoc = ("Gambar 2.1 " + assoc_phrase) if assoc_cap else assoc_phrase
    candidates = []
    for i, (is_cap, ph) in enumerate(cands):
        text = ("Tabel 3.%d " % (i + 1) + ph) if is_cap else ph
        candidates.append((i, text))

    base = mrg.find_template_matches(assoc, candidates)
    transformed = mrg.find_template_matches(
        _t(assoc, upper, pad),
        [(idx, _t(txt, upper, pad)) for idx, txt in candidates],
    )
    # Decision is invariant to caps/whitespace normalization of any input.
    assert base == transformed


def test_property8_find_template_matches_has_no_target_img_param():
    """R4.2: matching depends only on assoc/paragraph text -- there is no
    target_img (image filename) parameter to special-case on."""
    params = inspect.signature(mrg.find_template_matches).parameters
    assert "target_img" not in params
    assert list(params) == ["assoc_text", "candidates"]


# =========================================================================== #
# Property 9: Pencocokan hanya antar paragraf sejenis
# =========================================================================== #
# Feature: dynamic-generation-pipeline, Property 9: a caption-type assoc never
# matches a narrative paragraph and vice versa, even when the content matches.
# Validates: Requirements 4.5
@settings(max_examples=200, deadline=None)
@given(phrase=_phrase)
def test_property9_no_cross_type_match(phrase):
    caption = "Gambar 2.1 " + phrase
    narrative = phrase + " dijelaskan pada bagian implementasi sistem"

    # Caption assoc vs narrative candidate -> never matches (different kinds).
    assert mrg.find_template_matches(caption, [(0, narrative)]) == []
    # Narrative assoc vs caption candidate -> never matches either.
    assert mrg.find_template_matches(phrase, [(0, caption)]) == []

    # Sanity: same-type with the same content DOES match (content is otherwise
    # a valid match; only the type guard suppresses the cross-type cases above).
    assert mrg.find_template_matches(caption, [(0, "Tabel 9.9 " + phrase)]) == [0]


# =========================================================================== #
# Property 10: Tie-break kecocokan ganda memilih urutan dokumen pertama
# =========================================================================== #
# Feature: dynamic-generation-pipeline, Property 10: multiple candidate matches are
# returned in document order; the first (minimum index) is the selected one.
# Validates: Requirements 4.4
@settings(max_examples=150, deadline=None)
@given(phrase=_phrase, lead=st.integers(0, 4))
def test_property10_multiple_matches_document_order(phrase, lead):
    candidates = []
    idx = 0
    # Non-matching leading captions (distinct content) push the matches to
    # arbitrary, ascending document indices.
    for _ in range(lead):
        candidates.append((idx, "Gambar 8.%d lorem ipsum dolor sit amet" % (idx + 1)))
        idx += 1
    first_match = idx
    candidates.append((idx, "Gambar 1.1 " + phrase))
    idx += 1
    candidates.append((idx, "narasi panjang " + phrase + " untuk konteks"))  # body, no match
    idx += 1
    second_match = idx
    candidates.append((idx, "Tabel 3.1 " + phrase))
    idx += 1

    assoc = "Gambar 9.9 " + phrase  # caption type
    matches = mrg.find_template_matches(assoc, candidates)

    assert matches == [first_match, second_match]
    # Document order => ascending; the selected one is the minimum index.
    assert matches == sorted(matches)
    assert matches[0] == min(matches)


# =========================================================================== #
# Property 16: Resolusi path relatif terhadap akar ruang kerja
# =========================================================================== #
# Feature: dynamic-generation-pipeline, Property 16: resolve_path returns absolute
# paths as-is and anchors relative paths to workspace_root.
# Validates: Requirements 7.2, 7.3
_seg = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=8)


@settings(max_examples=200, deadline=None)
@given(segs=st.lists(_seg, min_size=1, max_size=4),
       root_segs=st.lists(_seg, min_size=1, max_size=3))
def test_property16_resolve_path(segs, root_segs):
    rel = "/".join(segs)
    workspace_root = Path(Path.cwd().anchor) / Path(*root_segs)

    # Relative path -> anchored to workspace_root.
    assert mrg.resolve_path(rel, workspace_root) == workspace_root / rel

    # Absolute path -> returned unchanged.
    abs_path = Path(Path.cwd().anchor) / rel
    assert abs_path.is_absolute()
    assert mrg.resolve_path(str(abs_path), workspace_root) == abs_path


# =========================================================================== #
# 9.3 unit: main() path validation -- argv > config > default precedence and
# guard exits (missing draft / missing output dir) BEFORE any heavy merge runs.
# =========================================================================== #
def _guard_no_merge(monkeypatch):
    """Make any accidental merge call fail loudly, proving the guards stop first."""
    def _boom(*_a, **_k):
        raise AssertionError("merge_draft_to_xml must not run when path is invalid")
    monkeypatch.setattr(mrg, "merge_draft_to_xml", _boom, raising=True)
    monkeypatch.setattr(mrg, "parse_markdown", _boom, raising=True)


def test_main_argv_takes_precedence_over_config(monkeypatch, capsys):
    _guard_no_merge(monkeypatch)
    monkeypatch.setattr(mrg, "read_path_config",
                        lambda _root: {"draft": "CONFIG_DRAFT_xyz.md"})
    with pytest.raises(SystemExit):
        mrg.main(["ARGV_DRAFT_xyz.md"])
    out = capsys.readouterr().out
    # argv wins: the argv draft path is the one reported missing, not the config one.
    assert "ARGV_DRAFT_xyz.md" in out
    assert "CONFIG_DRAFT_xyz.md" not in out


def test_main_config_takes_precedence_over_default(monkeypatch, capsys):
    _guard_no_merge(monkeypatch)
    monkeypatch.setattr(mrg, "read_path_config",
                        lambda _root: {"draft": "CONFIG_DRAFT_xyz.md"})
    with pytest.raises(SystemExit):
        mrg.main([])  # no argv
    out = capsys.readouterr().out
    # config wins over the relative default "Tugas_Akhir_Draft.md".
    assert "CONFIG_DRAFT_xyz.md" in out
    assert "Tugas_Akhir_Draft.md" not in out


def test_main_missing_draft_exits(monkeypatch):
    _guard_no_merge(monkeypatch)
    monkeypatch.setattr(mrg, "read_path_config", lambda _root: {})
    with pytest.raises(SystemExit):
        mrg.main(["definitely_missing_draft_12345.md"])


def test_main_missing_output_dir_exits(monkeypatch, tmp_path):
    """An existing, readable draft but a non-existent output directory must halt
    before writing anything (R7.5)."""
    _guard_no_merge(monkeypatch)
    monkeypatch.setattr(mrg, "read_path_config", lambda _root: {})
    draft = tmp_path / "draft.md"
    draft.write_text("# draft\n", encoding="utf-8")
    bad_xml = tmp_path / "no_such_dir" / "document.xml"  # parent dir missing
    with pytest.raises(SystemExit):
        mrg.main([str(draft), str(bad_xml)])


def test_read_path_config_missing_returns_empty(tmp_path):
    # No merge_config.json present -> empty dict (callers fall back to defaults).
    assert mrg.read_path_config(tmp_path) == {}


# =========================================================================== #
# 10.2 integration (light): exercise the selection policy (0 / 1 / >1) on a small
# candidate list -- the policy merge_draft_to_xml applies, without a full run.
# =========================================================================== #
def test_integration_selection_policy_zero_match():
    """0 matches -> empty result (caller logs unmatched + continues, R4.3)."""
    candidates = [
        (0, "Gambar 2.1 Arsitektur Sistem Informasi Kampus"),
        (1, "Tabel 2.1 Spesifikasi Perangkat Keras Server"),
    ]
    assert mrg.find_template_matches("Gambar 9.9 Topik Yang Tidak Ada", candidates) == []


def test_integration_selection_policy_single_match():
    """Exactly 1 match -> that single index is injected (R4)."""
    candidates = [
        (0, "Gambar 2.1 Arsitektur Sistem Informasi Kampus"),
        (1, "narasi panjang tentang sesuatu yang lain sekali"),
    ]
    assert mrg.find_template_matches("Gambar 5.5 Arsitektur Sistem Informasi Kampus",
                                     candidates) == [0]


def test_integration_selection_policy_multiple_match_picks_min():
    """>1 matches -> document order; the caller picks the minimum index (R4.4)."""
    candidates = [
        (0, "Gambar 2.1 Diagram Use Case Sistem"),
        (1, "Tabel 2.2 sesuatu yang berbeda sekali isinya"),
        (2, "Gambar 2.3 Diagram Use Case Sistem"),
    ]
    matches = mrg.find_template_matches("Gambar 9.9 Diagram Use Case Sistem", candidates)
    assert matches == [0, 2]
    assert matches[0] == min(matches)  # tie-break selects first in document order


def test_integration_no_named_special_cases():
    """R4.2: removed special-cases (e.g. image20 / Dosen->Gedung) no longer apply;
    matching is purely text-driven, so unrelated content does not match."""
    candidates = [(0, "Gambar 2.1 Modal Tambah Data Gedung Baru")]
    # "Dosen" content must NOT match a "Gedung" caption (the old trick is gone).
    assert mrg.find_template_matches("Gambar 3.1 Data Dosen Pengajar Kelas",
                                     candidates) == []


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
