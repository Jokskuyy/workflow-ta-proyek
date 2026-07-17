"""Unit tests for the pure table-formatting helpers (table-formatting-fix).

Spec: .kiro/specs/table-formatting-fix (task 3.1)

These tests cover ``compute_printable_width(root, namespaces)`` -- a pure,
read-only helper that derives the printable page width (dxa) from the
document's body ``sectPr`` (``pgSz@w - pgMar@left - pgMar@right``).

Covered behaviours:
  * real page setup (11906 - 2268 - 1701) -> 7937 dxa,
  * safe per-value defaults when ``pgSz``/``pgMar`` (or their attributes) are
    missing or unparseable,
  * fallback to the last ``sectPr`` in the body when there is no direct-child
    body ``sectPr``,
  * read-only guarantee: the ``sectPr`` is never mutated (Property 4).

Validates: Requirements 2.1, 3.5 (Correctness Properties 1, 4).
"""
import sys
from pathlib import Path

import lxml.etree as ET

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
DEFAULT_PRINTABLE = 7937


def qn(tag):
    return f"{{{W}}}{tag}"


def make_body_sectPr(body, w=None, left=None, right=None, include_pgSz=True,
                     include_pgMar=True):
    """Append a body-level ``sectPr`` with optional pgSz/pgMar attributes."""
    sectPr = ET.SubElement(body, qn("sectPr"))
    if include_pgSz:
        pgSz = ET.SubElement(sectPr, qn("pgSz"))
        if w is not None:
            pgSz.set(qn("w"), str(w))
        pgSz.set(qn("h"), "16838")
    if include_pgMar:
        pgMar = ET.SubElement(sectPr, qn("pgMar"))
        if left is not None:
            pgMar.set(qn("left"), str(left))
        if right is not None:
            pgMar.set(qn("right"), str(right))
        pgMar.set(qn("top"), "1440")
        pgMar.set(qn("bottom"), "1440")
    return sectPr


def make_doc(builder=None):
    """Return a ``w:document/w:body`` doc; ``builder(body)`` customises the body."""
    doc = ET.Element(qn("document"))
    body = ET.SubElement(doc, qn("body"))
    if builder is not None:
        builder(body)
    return doc


def make_para_sectPr(body, w, left, right):
    """Append a paragraph-level sectPr (nested in pPr) -- NOT a body child."""
    p = ET.SubElement(body, qn("p"))
    pPr = ET.SubElement(p, qn("pPr"))
    sectPr = ET.SubElement(pPr, qn("sectPr"))
    pgSz = ET.SubElement(sectPr, qn("pgSz"))
    pgSz.set(qn("w"), str(w))
    pgMar = ET.SubElement(sectPr, qn("pgMar"))
    pgMar.set(qn("left"), str(left))
    pgMar.set(qn("right"), str(right))
    return sectPr


# --------------------------------------------------------------------------- #
# Happy path: real page setup -> 7937.
# --------------------------------------------------------------------------- #
def test_real_page_setup_returns_7937():
    doc = make_doc(lambda b: make_body_sectPr(b, PAGE_W, MARGIN_LEFT, MARGIN_RIGHT))
    assert fmt.compute_printable_width(doc, NS) == PRINTABLE == 7937


def test_custom_valid_setup_computed_correctly():
    doc = make_doc(lambda b: make_body_sectPr(b, 12240, 1440, 1440))
    assert fmt.compute_printable_width(doc, NS) == 12240 - 1440 - 1440


# --------------------------------------------------------------------------- #
# Defaults: missing values / elements / whole sectPr.
# --------------------------------------------------------------------------- #
def test_no_sectPr_at_all_uses_defaults():
    doc = make_doc()  # empty body, no sectPr
    assert fmt.compute_printable_width(doc, NS) == DEFAULT_PRINTABLE


def test_empty_sectPr_uses_defaults():
    doc = make_doc(lambda b: make_body_sectPr(b, include_pgSz=False,
                                              include_pgMar=False))
    assert fmt.compute_printable_width(doc, NS) == DEFAULT_PRINTABLE


def test_missing_attributes_use_per_value_defaults():
    # pgSz/pgMar present but their w/left/right attributes are absent.
    doc = make_doc(lambda b: make_body_sectPr(b, w=None, left=None, right=None))
    assert fmt.compute_printable_width(doc, NS) == DEFAULT_PRINTABLE


def test_partial_values_default_only_missing_ones():
    # Only pgSz@w provided; margins fall back to defaults (2268 / 1701).
    doc = make_doc(lambda b: make_body_sectPr(b, w=12000, left=None, right=None))
    assert fmt.compute_printable_width(doc, NS) == 12000 - MARGIN_LEFT - MARGIN_RIGHT


def test_unparseable_values_use_defaults():
    def builder(body):
        sectPr = ET.SubElement(body, qn("sectPr"))
        pgSz = ET.SubElement(sectPr, qn("pgSz"))
        pgSz.set(qn("w"), "not-a-number")
        pgMar = ET.SubElement(sectPr, qn("pgMar"))
        pgMar.set(qn("left"), "xxx")
        pgMar.set(qn("right"), "")
    doc = make_doc(builder)
    assert fmt.compute_printable_width(doc, NS) == DEFAULT_PRINTABLE


def test_degenerate_geometry_falls_back_to_default():
    # width smaller than the margins -> non-positive printable -> default.
    doc = make_doc(lambda b: make_body_sectPr(b, w=1000, left=2268, right=1701))
    assert fmt.compute_printable_width(doc, NS) == DEFAULT_PRINTABLE


# --------------------------------------------------------------------------- #
# Fallback to the last sectPr in the body.
# --------------------------------------------------------------------------- #
def test_fallback_to_last_sectPr_when_no_body_child_sectPr():
    # No direct body/sectPr; a paragraph-level sectPr is the only one present.
    doc = make_doc(lambda b: make_para_sectPr(b, 9000, 1000, 1000))
    assert fmt.compute_printable_width(doc, NS) == 9000 - 1000 - 1000


def test_prefers_body_child_sectPr_over_nested_sectPr():
    def builder(body):
        # A nested (paragraph-level) sectPr with different geometry first ...
        make_para_sectPr(body, 9000, 1000, 1000)
        # ... and the real body-level sectPr as a direct child.
        make_body_sectPr(body, PAGE_W, MARGIN_LEFT, MARGIN_RIGHT)
    doc = make_doc(builder)
    assert fmt.compute_printable_width(doc, NS) == PRINTABLE


def test_uses_last_sectPr_when_multiple_nested_present():
    def builder(body):
        make_para_sectPr(body, 9000, 1000, 1000)
        make_para_sectPr(body, 8000, 500, 500)  # last one wins
    doc = make_doc(builder)
    assert fmt.compute_printable_width(doc, NS) == 8000 - 500 - 500


# --------------------------------------------------------------------------- #
# Read-only guarantee (Property 4): sectPr is never mutated.
# --------------------------------------------------------------------------- #
def test_sectPr_not_mutated():
    doc = make_doc(lambda b: make_body_sectPr(b, PAGE_W, MARGIN_LEFT, MARGIN_RIGHT))
    body = doc.find("w:body", NS)
    sectPr = body.find("w:sectPr", NS)
    before = ET.tostring(sectPr)

    fmt.compute_printable_width(doc, NS)

    after = ET.tostring(body.find("w:sectPr", NS))
    assert before == after, "compute_printable_width must not mutate sectPr"


# =========================================================================== #
# Helpers for building w:tbl fragments (task 3.2).
# =========================================================================== #
def make_tbl(grid_widths=None, rows=None):
    """Build a ``w:tbl`` element.

    ``grid_widths`` -- optional iterable of ``gridCol@w`` values (ints/strings/
    ``None`` to omit the attribute). When ``None`` no ``w:tblGrid`` is created.
    ``rows`` -- optional list of rows; each row is a list of cell specs. A cell
    spec is either an int gridSpan or ``None`` (single column, no ``gridSpan``).
    """
    tbl = ET.Element(qn("tbl"))
    if grid_widths is not None:
        tblGrid = ET.SubElement(tbl, qn("tblGrid"))
        for w in grid_widths:
            gc = ET.SubElement(tblGrid, qn("gridCol"))
            if w is not None:
                gc.set(qn("w"), str(w))
    if rows is not None:
        for row_spec in rows:
            tr = ET.SubElement(tbl, qn("tr"))
            for span in row_spec:
                tc = ET.SubElement(tr, qn("tc"))
                if span is not None:
                    tcPr = ET.SubElement(tc, qn("tcPr"))
                    gs = ET.SubElement(tcPr, qn("gridSpan"))
                    gs.set(qn("val"), str(span))
    return tbl


# --------------------------------------------------------------------------- #
# count_table_columns: structural column count.
# --------------------------------------------------------------------------- #
def test_count_columns_from_grid():
    tbl = make_tbl(grid_widths=[1000, 2000, 3000])
    assert fmt.count_table_columns(tbl, NS) == 3


def test_count_columns_from_rows_when_no_grid():
    tbl = make_tbl(rows=[[None, None, None, None]])
    assert fmt.count_table_columns(tbl, NS) == 4


def test_count_columns_uses_max_row_when_ragged():
    tbl = make_tbl(rows=[[None, None], [None, None, None]])
    assert fmt.count_table_columns(tbl, NS) == 3


def test_count_columns_sums_gridspan():
    # Row with a cell spanning 3 columns + one normal cell -> 4 columns.
    tbl = make_tbl(rows=[[3, None]])
    assert fmt.count_table_columns(tbl, NS) == 4


def test_count_columns_prefers_grid_over_rows():
    tbl = make_tbl(grid_widths=[500, 500], rows=[[None, None, None]])
    assert fmt.count_table_columns(tbl, NS) == 2


def test_count_columns_empty_table_is_zero():
    tbl = make_tbl()
    assert fmt.count_table_columns(tbl, NS) == 0


# --------------------------------------------------------------------------- #
# column_ratios_from_grid: grid-derived vs even proportions.
# --------------------------------------------------------------------------- #
def test_ratios_from_positive_grid():
    tbl = make_tbl(grid_widths=[1000, 3000])
    ratios = fmt.column_ratios_from_grid(tbl, NS, 2)
    assert ratios == [0.25, 0.75]
    assert abs(sum(ratios) - 1.0) < 1e-9


def test_ratios_even_when_no_grid():
    tbl = make_tbl(rows=[[None, None, None, None]])
    ratios = fmt.column_ratios_from_grid(tbl, NS, 4)
    assert ratios == [0.25, 0.25, 0.25, 0.25]


def test_ratios_even_when_grid_count_mismatches_n_cols():
    tbl = make_tbl(grid_widths=[1000, 2000])
    ratios = fmt.column_ratios_from_grid(tbl, NS, 3)
    assert ratios == [1 / 3, 1 / 3, 1 / 3]


def test_ratios_even_when_grid_sum_not_positive():
    tbl = make_tbl(grid_widths=[0, 0])
    ratios = fmt.column_ratios_from_grid(tbl, NS, 2)
    assert ratios == [0.5, 0.5]


def test_ratios_even_when_grid_width_unparseable():
    tbl = make_tbl(grid_widths=["abc", 1000])
    ratios = fmt.column_ratios_from_grid(tbl, NS, 2)
    assert ratios == [0.5, 0.5]


def test_ratios_single_column():
    tbl = make_tbl(grid_widths=[4321])
    assert fmt.column_ratios_from_grid(tbl, NS, 1) == [1.0]


def test_ratios_empty_for_non_positive_n_cols():
    tbl = make_tbl()
    assert fmt.column_ratios_from_grid(tbl, NS, 0) == []


def test_ratios_read_only_does_not_mutate_grid():
    tbl = make_tbl(grid_widths=[1000, 3000])
    before = ET.tostring(tbl)
    fmt.column_ratios_from_grid(tbl, NS, 2)
    assert ET.tostring(tbl) == before


# --------------------------------------------------------------------------- #
# distribute_width: exact-sum integer distribution.
# --------------------------------------------------------------------------- #
def test_distribute_even_sums_exactly_to_printable():
    widths = fmt.distribute_width(7937, [0.25, 0.25, 0.25, 0.25])
    assert sum(widths) == 7937
    assert all(isinstance(w, int) for w in widths)


def test_distribute_remainder_goes_to_last_column():
    # 7937 / 3 -> 2645 each, remainder 2 lands on the last column.
    widths = fmt.distribute_width(7937, [1 / 3, 1 / 3, 1 / 3])
    assert widths == [2645, 2645, 2647]
    assert sum(widths) == 7937


def test_distribute_proportional_sums_exactly():
    widths = fmt.distribute_width(7937, [0.25, 0.75])
    assert sum(widths) == 7937
    assert widths[1] > widths[0]


def test_distribute_single_column_gets_full_printable():
    assert fmt.distribute_width(7937, [1.0]) == [7937]


def test_distribute_empty_ratios_returns_empty():
    assert fmt.distribute_width(7937, []) == []


def test_distribute_degenerate_ratios_fall_back_to_even():
    widths = fmt.distribute_width(7937, [0.0, 0.0])
    assert sum(widths) == 7937
    assert widths[0] == 3968 and widths[1] == 3969


def test_distribute_overrides_replace_ratios():
    # overrides (same length, positive sum) win over the base ratios.
    widths = fmt.distribute_width(1000, [0.5, 0.5], overrides=[0.1, 0.9])
    assert sum(widths) == 1000
    assert widths == [100, 900]


def test_distribute_overrides_ignored_when_length_mismatch():
    widths = fmt.distribute_width(1000, [0.5, 0.5], overrides=[1.0])
    assert sum(widths) == 1000
    assert widths == [500, 500]


def test_distribute_overrides_ignored_when_non_positive_sum():
    widths = fmt.distribute_width(1000, [0.5, 0.5], overrides=[0.0, 0.0])
    assert sum(widths) == 1000
    assert widths == [500, 500]


def test_distribute_ratios_need_not_be_normalized():
    # Raw grid-like weights (not summing to 1) still distribute exactly.
    widths = fmt.distribute_width(7937, [1000.0, 3000.0])
    assert sum(widths) == 7937
    assert widths[1] > widths[0]


# --------------------------------------------------------------------------- #
# Integration of the two helpers (grid proportions -> exact widths).
# --------------------------------------------------------------------------- #
def test_grid_ratios_then_distribute_sums_to_printable():
    tbl = make_tbl(grid_widths=[3500, 900, 900, 900, 900, 900])
    n_cols = fmt.count_table_columns(tbl, NS)
    ratios = fmt.column_ratios_from_grid(tbl, NS, n_cols)
    widths = fmt.distribute_width(PRINTABLE, ratios)
    assert n_cols == 6
    assert sum(widths) == PRINTABLE == 7937


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-v"]))
