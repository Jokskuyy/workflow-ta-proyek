"""Property + unit tests for the draft-sourced bibliography of the
writing-pipeline-improvements spec (R1, Option B).

Spec: .kiro/specs/writing-pipeline-improvements

Covers design Properties 1, 2, 3 plus R1.8 / R1.9 unit cases against:

  - ``scratch/merge_draft_to_docx.py``: ReferenceEntry, parse_bibliography_entries,
    parse_italic_spans, reference_key (PURE parser, R1.1/1.2/1.4/1.8).
  - ``skills/scripts/format_ta_proyek.py``: clean_bibliography_sdt (draft-sourced
    SDT renderer, R1.3 style invariant + R1.8 missing-section guard).

Draft is the single source of truth (no hardcoded references). The snapshot test
asserts the 8 current draft entries parse to the same text + italic spans as the
captured baseline ``tests/fixtures/wpi_baseline_bibliography.xml`` (Option B
format/style preservation, R1.9).
"""
import sys
from pathlib import Path

import lxml.etree
import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Imports: pure parser from the Mesin_Merge script; SDT writer from the formatter.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / "scratch"
SKILLS = ROOT / "skills" / "scripts"
FIXTURES = ROOT / "tests" / "fixtures"
for _p in (str(SCRATCH), str(SKILLS), str(FIXTURES)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import merge_draft_to_docx as mrg  # noqa: E402
import format_ta_proyek as fmt  # noqa: E402

NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
DRAFT = ROOT / "Tugas_Akhir_Draft.md"
BASELINE_BIB = FIXTURES / "wpi_baseline_bibliography.xml"


def W(tag):
    return f'{{{NS}}}{tag}'


def make_empty_sdt():
    """A minimal w:sdt with an empty w:sdtContent."""
    sdt = lxml.etree.Element(W('sdt'))
    lxml.etree.SubElement(sdt, W('sdtContent'))
    return sdt


# --------------------------------------------------------------------------- #
# Strategies.
# --------------------------------------------------------------------------- #
# Plain text free of any markup metacharacter and free of '#'/'-' edge tokens.
_PLAIN = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ,.()"
_plain1 = st.text(_PLAIN, min_size=1, max_size=20)


@st.composite
def entry_lines(draw):
    """A list of 1..k non-empty reference lines suitable for a draft section.

    Each line is already stripped, never empty, never starts with '#', and is
    never exactly '---', so parse_bibliography_entries keeps every line as one
    entry in order.
    """
    k = draw(st.integers(min_value=1, max_value=8))
    lines = []
    for _ in range(k):
        raw = draw(_plain1).strip()
        assume(raw)                      # non-empty after strip
        assume(not raw.startswith('#'))  # not a heading
        assume(raw != '---')             # not a horizontal rule
        lines.append(raw)
    return lines


@st.composite
def alternating_spans(draw):
    """A list of (text, is_italic) segments with strictly alternating italic
    flags and non-empty, markup-free text -> already canonical (no merging)."""
    n = draw(st.integers(min_value=1, max_value=6))
    start = draw(st.booleans())
    # text from _PLAIN never contains '*', so wrapping in '*...*' is unambiguous.
    texts = [draw(_plain1) for _ in range(n)]
    # Strictly alternating italic flags -> already canonical (no adjacent merge).
    flags = [(start if j % 2 == 0 else not start) for j in range(n)]
    return [(texts[j], flags[j]) for j in range(n)]


# =========================================================================== #
# Property 1: Parsing entri referensi mempertahankan jumlah dan urutan
# =========================================================================== #
# Feature: writing-pipeline-improvements, Property 1: Parsing entri referensi mempertahankan jumlah dan urutan
# Validates: Requirements 1.1, 1.4
@settings(max_examples=200, deadline=None)
@given(lines=entry_lines(), blanks=st.booleans())
def test_property1_entry_count_and_order(lines, blanks):
    # Optionally intersperse blank lines (must be ignored, not counted).
    body_lines = []
    for ln in lines:
        body_lines.append(ln)
        if blanks:
            body_lines.append("")
    draft = "# DAFTAR PUSTAKA\n\n" + "\n".join(body_lines) + "\n"
    result = mrg.parse_bibliography_entries(draft)

    assert result.section_found is True
    assert len(result) == len(lines)                       # exact count (R1.1)
    assert [e.raw for e in result] == lines                # same order (R1.4)


# =========================================================================== #
# Property 2: Fidelity Rentang_Miring (round-trip span)
# =========================================================================== #
# Feature: writing-pipeline-improvements, Property 2: Fidelity Rentang_Miring (round-trip span)
# Validates: Requirements 1.2
@settings(max_examples=200, deadline=None)
@given(spans=alternating_spans())
def test_property2_italic_span_roundtrip(spans):
    # Render to markdown: italic segments wrapped in '*...*', plain as-is.
    md = "".join(("*" + t + "*") if ital else t for t, ital in spans)
    parsed = mrg.parse_italic_spans(md)

    # Round-trip equivalence of (text, is_italic) segments.
    assert parsed == spans
    # Joined text equals raw with '*' markers stripped.
    assert "".join(t for t, _ in parsed) == "".join(t for t, _ in spans)
    assert "".join(t for t, _ in parsed) == md.replace("*", "")


# =========================================================================== #
# Property 3: Invarian gaya paragraf bibliografi
# =========================================================================== #
# Feature: writing-pipeline-improvements, Property 3: Invarian gaya paragraf bibliografi
# Validates: Requirements 1.3, 1.9
@settings(max_examples=200, deadline=None)
@given(spans_list=st.lists(alternating_spans(), min_size=1, max_size=6))
def test_property3_bibliography_paragraph_style_invariant(spans_list):
    entries = [
        mrg.ReferenceEntry(raw="".join(t for t, _ in s), spans=tuple(s),
                           authors=(), year=None)
        for s in spans_list
    ]
    sdt = make_empty_sdt()
    fmt.clean_bibliography_sdt(sdt, entries=entries)

    content = sdt.find(W('sdtContent'))
    paras = content.findall(W('p'))
    assert len(paras) == len(entries)

    for p in paras:
        pPr = p.find(W('pPr'))
        assert pPr is not None
        assert pPr.find(W('pStyle')).get(W('val')) == 'Normal'
        ind = pPr.find(W('ind'))
        assert ind.get(W('left')) == '567'
        assert ind.get(W('hanging')) == '567'
        sp = pPr.find(W('spacing'))
        assert sp.get(W('before')) == '0'
        assert sp.get(W('after')) == '120'
        assert sp.get(W('line')) == '240'
        assert sp.get(W('lineRule')) == 'auto'
        assert pPr.find(W('jc')).get(W('val')) == 'both'


# =========================================================================== #
# R1.8 unit: missing '# DAFTAR PUSTAKA' section -> warning, no fake entries.
# =========================================================================== #
def test_unit_missing_section_warns_and_writes_no_entries(capsys):
    # Draft text without the bibliography heading.
    draft_text = "# PENDAHULUAN\nIsi laporan tanpa daftar pustaka.\n"

    # Pre-seed the SDT with a sentinel paragraph that must remain untouched
    # (the body-paragraph references are the source of truth, R1.8).
    sdt = make_empty_sdt()
    content = sdt.find(W('sdtContent'))
    sentinel = lxml.etree.SubElement(content, W('p'))
    sentinel.set('id', 'sentinel')

    fmt.clean_bibliography_sdt(sdt, draft_path=draft_text)

    captured = capsys.readouterr().out
    assert '[WARN]' in captured
    assert 'tidak ditemukan' in captured
    # No fake entries written; the sentinel is preserved as-is.
    paras = content.findall(W('p'))
    assert len(paras) == 1
    assert paras[0].get('id') == 'sentinel'


def test_unit_parse_missing_section_returns_empty_not_found():
    result = mrg.parse_bibliography_entries("# INTRO\nno bibliography here\n")
    assert list(result) == []
    assert result.section_found is False


# =========================================================================== #
# R1.9 snapshot: the 8 current draft entries parse to the same text + italic
# spans as the captured baseline (Option B format/style preservation).
# =========================================================================== #
def _baseline_entry_spans():
    """Extract canonical (text, is_italic) spans per <w:p> from the baseline."""
    tree = lxml.etree.parse(str(BASELINE_BIB))
    out = []
    for p in tree.getroot().findall(W('p')):
        spans = []
        for r in p.findall(W('r')):
            t = r.find(W('t'))
            if t is None or t.text is None:
                continue
            rPr = r.find(W('rPr'))
            is_italic = rPr is not None and rPr.find(W('i')) is not None
            if spans and spans[-1][1] == is_italic:
                spans[-1] = (spans[-1][0] + t.text, is_italic)
            else:
                spans.append((t.text, is_italic))
        out.append([(t, i) for t, i in spans])
    return out


def test_unit_snapshot_draft_entries_match_baseline_spans():
    assert DRAFT.exists(), "draft missing"
    assert BASELINE_BIB.exists(), "baseline fixture missing"

    result = mrg.parse_bibliography_entries(str(DRAFT))
    assert result.section_found is True

    baseline = _baseline_entry_spans()
    assert len(result) == len(baseline) == 8

    for entry, base_spans in zip(result, baseline):
        # Text + italic-span structure must match the captured baseline.
        assert list(entry.spans) == base_spans
        # Exactly one italic span per APA entry (the journal/source name).
        assert sum(1 for _, ital in entry.spans if ital) == 1


def test_unit_reference_key_surname_and_year():
    result = mrg.parse_bibliography_entries(str(DRAFT))
    keys = [mrg.reference_key(e) for e in result]
    assert keys[0] == ('aliyah', '2024')
    assert ('siv', '2025') in keys
    assert ('putra', '2026') in keys


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
