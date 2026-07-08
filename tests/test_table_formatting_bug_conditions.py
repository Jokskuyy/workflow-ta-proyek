"""Bug-condition exploration tests for ``format_all_tables`` (table-formatting-fix).

Spec: .kiro/specs/table-formatting-fix

These tests encode the EXPECTED post-fix behaviour described by the design's
``isBugCondition((tbl, page))`` specification and Correctness Properties 1-3:
for ANY table (any column count, any cell content) and the document's page
setup, the fixed ``format_all_tables`` MUST

  * set a fixed layout (``tblPr/tblLayout = fixed``) with a total preferred
    width (``tblPr/tblW type=dxa``) equal to the printable width
    (``pgSz@w - pgMar@left - pgMar@right`` = 7937 dxa for the real setup),
  * rewrite ``tblGrid/gridCol@w`` (and per-cell ``tcW``) so they sum exactly to
    the printable width,
  * mark row 0 as a repeating header (``trPr/tblHeader``), and
  * apply consistent ``tblPr/tblBorders`` and ``tblPr/tblCellMar``.

CRITICAL (exploration phase): On the UNFIXED code ``format_all_tables`` only
width-normalises the single hardcoded ``is_tabel_1_2`` table (exactly 6 columns
whose first cell text contains "Aktivitas"), using magic numbers that sum to
8000 dxa, and NEVER sets ``tblW``/``tblLayout``/``tblHeader``/``tblBorders``/
``tblCellMar`` on any table. Therefore EVERY test in this module is EXPECTED TO
FAIL right now -- the failure is the proof that the bug exists. Do NOT "fix" the
tests or the code at this stage. The very same tests are re-run after the fix
(task 3.4), at which point they must PASS.

Validates: Requirements 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4
(and Correctness Properties 1, 2, 3).
"""
import sys
from pathlib import Path

import lxml.etree as ET
import pytest
from hypothesis import HealthCheck, Phase, given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Import the function under test from the canonical Mesin_Format script.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SKILLS))

import format_ta_proyek as fmt  # noqa: E402

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}

# Real page setup taken from the project's document.xml section properties.
PAGE_W = 11906
MARGIN_LEFT = 2268
MARGIN_RIGHT = 1701
PRINTABLE = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT  # == 7937 dxa


# --------------------------------------------------------------------------- #
# Tiny lxml OOXML builders (build via the DOM -- no string escaping pitfalls).
# --------------------------------------------------------------------------- #
def qn(tag):
    return f"{{{W}}}{tag}"


def make_cell(text="", grid_span=None):
    tc = ET.Element(qn("tc"))
    if grid_span is not None:
        tcPr = ET.SubElement(tc, qn("tcPr"))
        gs = ET.SubElement(tcPr, qn("gridSpan"))
        gs.set(qn("val"), str(grid_span))
    p = ET.SubElement(tc, qn("p"))
    r = ET.SubElement(p, qn("r"))
    t = ET.SubElement(r, qn("t"))
    t.text = text
    return tc


def make_row(cell_texts, spans=None):
    tr = ET.Element(qn("tr"))
    spans = spans or [None] * len(cell_texts)
    for txt, span in zip(cell_texts, spans):
        tr.append(make_cell(txt, span))
    return tr


def make_table(rows_texts, grid_widths=None, row_spans=None):
    """Build a ``w:tbl`` with an empty tblPr, optional tblGrid, and rows."""
    tbl = ET.Element(qn("tbl"))
    ET.SubElement(tbl, qn("tblPr"))
    if grid_widths is not None:
        tblGrid = ET.SubElement(tbl, qn("tblGrid"))
        for w in grid_widths:
            gc = ET.SubElement(tblGrid, qn("gridCol"))
            gc.set(qn("w"), str(w))
    row_spans = row_spans or [None] * len(rows_texts)
    for texts, spans in zip(rows_texts, row_spans):
        tbl.append(make_row(texts, spans))
    return tbl


def make_doc(tables):
    """Wrap tables in a ``w:document/w:body`` carrying the real body sectPr."""
    doc = ET.Element(qn("document"))
    body = ET.SubElement(doc, qn("body"))
    for t in tables:
        body.append(t)
    sectPr = ET.SubElement(body, qn("sectPr"))
    pgSz = ET.SubElement(sectPr, qn("pgSz"))
    pgSz.set(qn("w"), str(PAGE_W))
    pgSz.set(qn("h"), "16838")
    pgMar = ET.SubElement(sectPr, qn("pgMar"))
    pgMar.set(qn("left"), str(MARGIN_LEFT))
    pgMar.set(qn("right"), str(MARGIN_RIGHT))
    pgMar.set(qn("top"), "1440")
    pgMar.set(qn("bottom"), "1440")
    return doc


# --------------------------------------------------------------------------- #
# Inspection helpers (read the formatted result).
# --------------------------------------------------------------------------- #
def gridcol_widths(tbl):
    grid = tbl.find("w:tblGrid", NS)
    if grid is None:
        return []
    return [int(gc.get(qn("w"), "0")) for gc in grid.findall("w:gridCol", NS)]


def total_tblW(tbl):
    tblPr = tbl.find("w:tblPr", NS)
    if tblPr is None:
        return None
    tblW = tblPr.find("w:tblW", NS)
    if tblW is None:
        return None
    return tblW.get(qn("type")), tblW.get(qn("w"))


def tbl_layout_type(tbl):
    tblPr = tbl.find("w:tblPr", NS)
    if tblPr is None:
        return None
    layout = tblPr.find("w:tblLayout", NS)
    return None if layout is None else layout.get(qn("type"))


def row0_has_tblHeader(tbl):
    first_tr = tbl.find("w:tr", NS)
    if first_tr is None:
        return False
    trPr = first_tr.find("w:trPr", NS)
    return trPr is not None and trPr.find("w:tblHeader", NS) is not None


def tblPr_has(tbl, child):
    tblPr = tbl.find("w:tblPr", NS)
    return tblPr is not None and tblPr.find(f"w:{child}", NS) is not None


def row_tcW_sum(tbl):
    """Sum tcW@w across the first row, honouring gridSpan (span counts once)."""
    first_tr = tbl.find("w:tr", NS)
    if first_tr is None:
        return None
    total = 0
    for tc in first_tr.findall("w:tc", NS):
        tcPr = tc.find("w:tcPr", NS)
        if tcPr is None:
            return None
        tcW = tcPr.find("w:tcW", NS)
        if tcW is None:
            return None
        total += int(tcW.get(qn("w"), "0"))
    return total


# =========================================================================== #
# Concrete case A - Non-6-column overflow (Requirement 1.1, 2.1)
# =========================================================================== #
def test_case_a_four_column_table_fitted_to_printable():
    """A 4-column table must be fitted to the printable width.

    On unfixed code the table is not the hardcoded 6-column "Aktivitas" match,
    so NO tblW/tblGrid is written and it overflows the page margins.
    """
    tbl = make_table(
        [["H1", "H2", "H3", "H4"], ["a", "b", "c", "d"]],
        grid_widths=[3000, 3000, 3000, 3000],
    )
    fmt.format_all_tables(make_doc([tbl]), NS)

    assert total_tblW(tbl) == ("dxa", str(PRINTABLE)), (
        f"[Case A] expected tblPr/tblW = {PRINTABLE} dxa but got {total_tblW(tbl)}; "
        "unfixed code writes no tblW for a non-'Aktivitas' 4-column table"
    )
    assert sum(gridcol_widths(tbl)) == PRINTABLE, (
        f"[Case A] expected gridCol widths to sum to {PRINTABLE} but got "
        f"{gridcol_widths(tbl)} (sum={sum(gridcol_widths(tbl))})"
    )


# =========================================================================== #
# Concrete case B - Renamed first cell (Requirement 1.2, 2.2)
# =========================================================================== #
def test_case_b_renamed_first_cell_still_normalized():
    """A 6-column table whose first cell is "Kegiatan" (not "Aktivitas") must
    still be fitted -- detection must not depend on cell text."""
    header = ["Kegiatan", "M1", "M2", "M3", "M4", "M5"]
    body = ["Design", "x", "x", "x", "x", "x"]
    tbl = make_table([header, body], grid_widths=[2000] * 6)
    fmt.format_all_tables(make_doc([tbl]), NS)

    assert total_tblW(tbl) == ("dxa", str(PRINTABLE)), (
        f"[Case B] expected tblW = {PRINTABLE} dxa but got {total_tblW(tbl)}; "
        "renaming 'Aktivitas' -> 'Kegiatan' silently disables normalization"
    )
    assert sum(gridcol_widths(tbl)) == PRINTABLE, (
        f"[Case B] expected gridCol sum {PRINTABLE} but got "
        f"{sum(gridcol_widths(tbl))} ({gridcol_widths(tbl)})"
    )


# =========================================================================== #
# Concrete case C - Magic-number mismatch (Requirement 1.3, 2.3)
# =========================================================================== #
def test_case_c_aktivitas_table_sums_to_printable_not_8000():
    """The hardcoded "Aktivitas" 6-column table must sum to the printable
    width (7937), not the magic-number total (3500 + 5*900 = 8000)."""
    header = ["Aktivitas", "M1", "M2", "M3", "M4", "M5"]
    body = ["Design", "x", "x", "x", "x", "x"]
    tbl = make_table([header, body], grid_widths=[2000] * 6)
    fmt.format_all_tables(make_doc([tbl]), NS)

    widths = gridcol_widths(tbl)
    assert sum(widths) == PRINTABLE, (
        f"[Case C] expected gridCol sum {PRINTABLE} (printable) but got "
        f"{sum(widths)} -> {widths}; unfixed code uses magic numbers summing to 8000"
    )


# =========================================================================== #
# Concrete case D - Missing header repeat / borders / padding (Req 1.4, 2.4)
# =========================================================================== #
def test_case_d_header_borders_padding_applied():
    """Any table must get row-0 tblHeader plus tblBorders and tblCellMar."""
    tbl = make_table([["H1", "H2", "H3"], ["a", "b", "c"]], grid_widths=[2600, 2600, 2600])
    fmt.format_all_tables(make_doc([tbl]), NS)

    assert row0_has_tblHeader(tbl), (
        "[Case D] expected row 0 to have trPr/tblHeader (repeating header) -- "
        "unfixed code never sets it"
    )
    assert tblPr_has(tbl, "tblBorders"), (
        "[Case D] expected tblPr/tblBorders -- unfixed code never sets borders"
    )
    assert tblPr_has(tbl, "tblCellMar"), (
        "[Case D] expected tblPr/tblCellMar -- unfixed code never sets cell padding"
    )


# =========================================================================== #
# Concrete case E - Edge case: single-column table (Requirement 2.1)
# =========================================================================== #
def test_case_e_single_column_table():
    """A single-column table must get one gridCol at the full printable width
    and must not crash."""
    tbl = make_table([["Only"], ["value"]], grid_widths=[2500])
    fmt.format_all_tables(make_doc([tbl]), NS)  # must not raise

    widths = gridcol_widths(tbl)
    assert widths == [PRINTABLE], (
        f"[Case E] expected a single gridCol of {PRINTABLE} dxa but got {widths}"
    )
    assert total_tblW(tbl) == ("dxa", str(PRINTABLE)), (
        f"[Case E] expected tblW = {PRINTABLE} dxa but got {total_tblW(tbl)}"
    )


# =========================================================================== #
# Property 1 (+3) - ANY table structure fitted to printable width
# =========================================================================== #
# Exploration PBT: EXPECTED to fail on unfixed code, so keep example count small
# and skip the wasteful shrinking phase for speed.
EXPLORE_PBT = settings(
    max_examples=25,
    deadline=None,
    phases=[Phase.explicit, Phase.reuse, Phase.generate],
    suppress_health_check=[HealthCheck.too_slow],
)


@st.composite
def table_specs(draw):
    """Generate varied table shapes: n_cols, n_rows, optional pre-existing
    tblGrid, and an optional gridSpan on the first body cell."""
    n_cols = draw(st.integers(min_value=1, max_value=6))
    n_rows = draw(st.integers(min_value=1, max_value=4))
    has_grid = draw(st.booleans())
    if has_grid:
        grid_widths = draw(
            st.lists(
                st.integers(min_value=500, max_value=4000),
                min_size=n_cols,
                max_size=n_cols,
            )
        )
    else:
        grid_widths = None
    # Optional gridSpan on the first cell of a body row (if room + >1 row).
    use_span = draw(st.booleans()) and n_cols >= 2 and n_rows >= 2
    return n_cols, n_rows, grid_widths, use_span


@given(spec=table_specs())
@settings(EXPLORE_PBT)
def test_property1_any_table_fitted_to_printable(spec):
    """**Property 1: Bug Condition** - Tables not fitted to printable width.

    For ANY generated table shape, after ``format_all_tables`` the table must
    have a fixed layout, a total width equal to the printable width, gridCol
    (and tcW) widths summing to the printable width, a header row, and
    consistent borders + padding. Fails on unfixed code for every shape that
    is not the hardcoded 6-column "Aktivitas" table.

    Validates: Requirements 2.1, 2.2, 2.3, 2.4
    """
    n_cols, n_rows, grid_widths, use_span = spec

    rows_texts = []
    row_spans = []
    for r in range(n_rows):
        if use_span and r == 1:
            # First body cell spans 2 columns -> one fewer physical <w:tc>.
            texts = [f"r{r}c0"] + [f"r{r}c{c}" for c in range(2, n_cols)]
            spans = [2] + [None] * (n_cols - 2)
        else:
            texts = [f"r{r}c{c}" for c in range(n_cols)]
            spans = [None] * n_cols
        rows_texts.append(texts)
        row_spans.append(spans)

    tbl = make_table(rows_texts, grid_widths=grid_widths, row_spans=row_spans)
    fmt.format_all_tables(make_doc([tbl]), NS)

    # --- Property 1: fixed layout + total width fits printable ---------------
    assert tbl_layout_type(tbl) == "fixed", (
        f"expected tblLayout=fixed, got {tbl_layout_type(tbl)!r} "
        f"(n_cols={n_cols}, n_rows={n_rows}, grid={grid_widths}, span={use_span})"
    )
    assert total_tblW(tbl) == ("dxa", str(PRINTABLE)), (
        f"expected tblW=({PRINTABLE},dxa), got {total_tblW(tbl)} "
        f"(n_cols={n_cols}, grid={grid_widths})"
    )
    widths = gridcol_widths(tbl)
    assert sum(widths) == PRINTABLE, (
        f"expected gridCol sum {PRINTABLE}, got {sum(widths)} -> {widths} "
        f"(n_cols={n_cols}, grid={grid_widths})"
    )
    assert row_tcW_sum(tbl) == PRINTABLE, (
        f"expected row tcW sum {PRINTABLE}, got {row_tcW_sum(tbl)} "
        f"(n_cols={n_cols}, span={use_span})"
    )

    # --- Property 3: header repeat + consistent borders/padding --------------
    assert row0_has_tblHeader(tbl), (
        f"expected row 0 trPr/tblHeader (n_cols={n_cols}, n_rows={n_rows})"
    )
    assert tblPr_has(tbl, "tblBorders"), f"expected tblPr/tblBorders (n_cols={n_cols})"
    assert tblPr_has(tbl, "tblCellMar"), f"expected tblPr/tblCellMar (n_cols={n_cols})"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
