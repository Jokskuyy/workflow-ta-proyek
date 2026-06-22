"""Property + unit tests for the PURE pipe-table parser and the alignment-aware
``build_table_element`` of the writing-pipeline-improvements spec.

Spec: .kiro/specs/writing-pipeline-improvements

Covers design Properties 10 and 11 against the helpers exposed by
``scratch/merge_draft_to_docx.py``:

  Alignment, is_pipe_table_separator, parse_alignment_row, detect_pipe_table,
  build_table_element.

The pipe-table parser and the table builder are pure, deterministic transforms
(lxml serialization only), so 100+ Hypothesis iterations are cheap.

  * Property 10 checks pipe-table STRUCTURE + per-column alignment: first row is
    a header (w:tblHeader), the separator row is never emitted as a data row,
    the data row count is preserved, and every cell in column j carries
    ``w:jc w:val`` equal to ``alignments[j]``.
  * Property 11 is a byte-for-byte PRESERVATION check: ``build_table_element``
    WITHOUT ``alignments`` (the [TABLE] path) must equal the frozen oracle
    ``tests/fixtures/oracle_writing.py::oracle_build_table_element`` exactly.
"""
import string
import sys
from pathlib import Path

import lxml.etree
from hypothesis import given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Import the parser/builder from the canonical Mesin_Merge script + the oracle.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / "scratch"
FIXTURES = ROOT / "tests" / "fixtures"
sys.path.insert(0, str(SCRATCH))
sys.path.insert(0, str(FIXTURES))

import merge_draft_to_docx as mrg  # noqa: E402
import oracle_writing as oracle  # noqa: E402

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _q(tag):
    return f"{{{W}}}{tag}"


# Separator-cell tokens and the w:jc value each one maps to.
_SEP_TOKENS = {
    "---": "left",      # DEFAULT
    ":---": "left",     # LEFT
    ":---:": "center",  # CENTER
    "---:": "right",    # RIGHT
    "----": "left",     # DEFAULT (longer dash run)
    ":----:": "center",
    "-----:": "right",
    ":-----": "left",
}

# Plain cell text: no '|', '*', '`', '[', '\\' so new tokenizer == oracle.
_PLAIN = st.text(alphabet=string.ascii_letters + string.digits + " ", min_size=0, max_size=8)
_PLAIN_NONEMPTY = st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=6)


def _row_line(cells):
    """Render a list of cell strings as a pipe row with outer pipes."""
    return "| " + " | ".join(cells) + " |"


@st.composite
def _pipe_tables(draw):
    """Generate a valid pipe table: (lines, expected_jc_vals, ndata_rows)."""
    ncols = draw(st.integers(min_value=1, max_value=5))
    sep_tokens = draw(st.lists(st.sampled_from(list(_SEP_TOKENS)), min_size=ncols, max_size=ncols))
    expected = [_SEP_TOKENS[t] for t in sep_tokens]

    header = [draw(_PLAIN_NONEMPTY) for _ in range(ncols)]
    ndata = draw(st.integers(min_value=1, max_value=4))
    rows = [[draw(_PLAIN_NONEMPTY) for _ in range(ncols)] for _ in range(ndata)]

    lines = [_row_line(header), _row_line(sep_tokens)]
    lines += [_row_line(r) for r in rows]
    return lines, expected, ndata


# --------------------------------------------------------------------------- #
# Property 10.
# --------------------------------------------------------------------------- #
# Feature: writing-pipeline-improvements, Property 10: Struktur dan perataan
# Tabel_Pipa — baris pertama ber-tblHeader, Baris_Pemisah tidak menjadi w:tr
# data, jumlah baris data = jumlah baris non-separator, dan setiap sel pada
# kolom-j memiliki w:jc sesuai alignments[j].
# Validates: Requirements 5.1, 5.2, 5.3
@settings(max_examples=150)
@given(spec=_pipe_tables())
def test_property10_pipe_table_structure_and_alignment(spec):
    lines, expected_vals, ndata = spec

    detected = mrg.detect_pipe_table(lines, 0)
    assert detected is not None, "a valid pipe table must be detected"
    end_idx, item = detected

    assert item["is_pipe"] is True
    assert item["type"] == "table"
    # The separator row is NOT carried into the item lines: header + data only.
    assert len(item["lines"]) == 1 + ndata
    # alignments map byte-for-byte to the expected w:jc values.
    assert [a.value for a in item["alignments"]] == expected_vals

    tbl = mrg.build_table_element(item)
    trs = tbl.findall(_q("tr"))

    # One w:tr per non-separator line (header + data rows), separator excluded.
    assert len(trs) == 1 + ndata
    # Data rows = non-separator rows minus the header row.
    assert len(trs) - 1 == ndata

    # First row is the header row (carries w:tblHeader); later rows do not.
    first_trPr = trs[0].find(_q("trPr"))
    assert first_trPr.find(_q("tblHeader")) is not None
    for tr in trs[1:]:
        assert tr.find(_q("trPr")).find(_q("tblHeader")) is None

    # Every cell in column j carries w:jc == alignments[j].
    for tr in trs:
        tcs = tr.findall(_q("tc"))
        assert len(tcs) == len(expected_vals)
        for j, tc in enumerate(tcs):
            jc = tc.find(_q("p")).find(_q("pPr")).find(_q("jc"))
            assert jc is not None
            assert jc.get(_q("val")) == expected_vals[j]


# --------------------------------------------------------------------------- #
# Property 11.
# --------------------------------------------------------------------------- #
@st.composite
def _bracket_table_items(draw):
    """Generate a [TABLE]-style item: {'type':'table','lines':[...]} with no
    'alignments' key, using only plain text so the new tokenizer matches the
    oracle for cell content."""
    nrows = draw(st.integers(min_value=1, max_value=5))
    ncols = draw(st.integers(min_value=1, max_value=5))
    outer = draw(st.booleans())

    lines = []
    for _ in range(nrows):
        cells = [draw(_PLAIN) for _ in range(ncols)]
        if outer:
            line = "| " + " | ".join(cells) + " |"
        else:
            line = " | ".join(cells)
        lines.append(line)
    return {"type": "table", "lines": lines}


# Feature: writing-pipeline-improvements, Property 11: Ekuivalensi Tabel_Kurung
# terhadap baseline — build_table_element (tanpa 'alignments') menghasilkan
# w:tbl identik byte-per-byte dengan oracle lama untuk data yang sama.
# Validates: Requirements 5.4, 5.5
@settings(max_examples=150)
@given(item=_bracket_table_items())
def test_property11_bracket_table_equals_oracle(item):
    assert "alignments" not in item  # the [TABLE] path never sets alignments
    new = lxml.etree.tostring(mrg.build_table_element(item))
    old = oracle.serialize(oracle.oracle_build_table_element(item))
    assert new == old


# --------------------------------------------------------------------------- #
# Unit tests — separator/alignment recognition and opt-in detection.
# --------------------------------------------------------------------------- #
def test_is_pipe_table_separator_examples():
    assert mrg.is_pipe_table_separator("|---|---|")
    assert mrg.is_pipe_table_separator(":---|---:|:---:")
    assert mrg.is_pipe_table_separator("---")
    assert not mrg.is_pipe_table_separator("| a | b |")
    assert not mrg.is_pipe_table_separator("")
    assert not mrg.is_pipe_table_separator("| --x | --- |")


def test_parse_alignment_row_mapping():
    aligns = mrg.parse_alignment_row("|:---|:---:|---:|---|")
    assert [a.value for a in aligns] == ["left", "center", "right", "left"]
    assert aligns[1] is mrg.Alignment.CENTER
    assert aligns[2] is mrg.Alignment.RIGHT


def test_detect_pipe_table_opt_in_returns_none_without_separator():
    # A line with '|' but no separator on the next line is NOT a pipe table.
    lines = ["| just | text |", "more text without separator", ""]
    assert mrg.detect_pipe_table(lines, 0) is None
    # No second line at all.
    assert mrg.detect_pipe_table(["| a | b |"], 0) is None
    # Column-count mismatch between header and separator -> not detected.
    assert mrg.detect_pipe_table(["| a | b |", "|---|"], 0) is None


def test_detect_pipe_table_stops_at_blank_line():
    lines = [
        "| H1 | H2 |",
        "|---|---:|",
        "| a | b |",
        "| c | d |",
        "",
        "| not | part |",
    ]
    end_idx, item = mrg.detect_pipe_table(lines, 0)
    assert item["lines"] == ["| H1 | H2 |", "| a | b |", "| c | d |"]
    assert end_idx == 4  # index of the blank line (first line after the table)
    assert [a.value for a in item["alignments"]] == ["left", "right"]


def test_parse_markdown_bracket_table_has_no_alignments():
    """Preservation/opt-in: [TABLE] blocks never become pipe tables."""
    md = (
        "# BAB I\n"
        "Intro paragraph.\n"
        "[TABLE]\n"
        "| A | B |\n"
        "| 1 | 2 |\n"
        "[/TABLE]\n"
    )
    tmp = ROOT / "tests" / "_tmp_bracket_table.md"
    tmp.write_text(md, encoding="utf-8")
    try:
        items = mrg.parse_markdown(str(tmp))
    finally:
        tmp.unlink()
    tables = [it for it in items if it["type"] == "table"]
    assert len(tables) == 1
    assert "alignments" not in tables[0]
    assert "is_pipe" not in tables[0]


def test_parse_markdown_detects_pipe_table_when_present():
    md = (
        "# BAB I\n"
        "Intro paragraph.\n"
        "| Nama | Nilai |\n"
        "|:---|---:|\n"
        "| a | 1 |\n"
        "| b | 2 |\n"
        "\n"
        "Closing paragraph.\n"
    )
    tmp = ROOT / "tests" / "_tmp_pipe_table.md"
    tmp.write_text(md, encoding="utf-8")
    try:
        items = mrg.parse_markdown(str(tmp))
    finally:
        tmp.unlink()
    tables = [it for it in items if it["type"] == "table"]
    assert len(tables) == 1
    assert tables[0].get("is_pipe") is True
    assert tables[0]["lines"] == ["| Nama | Nilai |", "| a | 1 |", "| b | 2 |"]
    assert [a.value for a in tables[0]["alignments"]] == ["left", "right"]
    # The closing paragraph after the blank line is still parsed normally.
    assert any(it["type"] == "paragraph" and it["text"] == "Closing paragraph." for it in items)
