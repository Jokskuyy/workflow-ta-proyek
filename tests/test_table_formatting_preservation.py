"""Preservation property tests for ``format_all_tables`` (table-formatting-fix).

Spec: .kiro/specs/table-formatting-fix

OBSERVATION-FIRST METHODOLOGY
-----------------------------
These tests capture the NON-buggy behaviours of ``format_all_tables`` that must
NOT change when the width-fitting / header-repeat / borders / padding fix is
applied. They encode Correctness Property 4 (Preservation) from the design:

    For any input where the bug condition does NOT hold (i.e. all behaviours
    OUTSIDE width-fitting, header-repeat, borders and padding), the fixed code
    SHALL produce the same result as the original code, preserving:
      * table centering (``tblPr/jc = center``),
      * header-row (row 0) cell vertical + horizontal centering
        (``tcPr/vAlign = center`` and ``pPr/jc = center``),
      * body-cell indentation clearing (``ind left/firstLine/right = 0``) with
        ``pPr`` children kept in valid ``PPR_ORDER``,
      * processing and counting of every ``w:tbl`` with the same
        ``Formatted N tables in document.xml.`` summary print, and
      * non-table content left untouched by the table-formatting stage.

CRITICAL (baseline phase): Unlike the bug-condition exploration tests, EVERY
test in this module is EXPECTED TO PASS on the UNFIXED code -- passing here
records the baseline behaviour that must be preserved. The very same tests are
re-run after the fix (task 3.5), at which point they must STILL pass (no
regressions).

To stay strictly within the preservation contract, the generators here never
produce the removed ``is_tabel_1_2`` special case (exactly 6 columns whose first
cell text contains "Aktivitas"): generated cell text is always of the form
``rRcC`` so body-cell alignment (``jc = left``) is stable across the fix.

Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5
(and Correctness Property 4).
"""
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

import lxml.etree as ET
from hypothesis import HealthCheck, given, settings
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


def make_doc(tables, extras_before=None, extras_after=None):
    """Wrap tables in ``w:document/w:body`` carrying the real body sectPr.

    ``extras_before`` / ``extras_after`` are lists of non-table elements placed
    around the tables so preservation of non-table content can be checked.
    """
    doc = ET.Element(qn("document"))
    body = ET.SubElement(doc, qn("body"))
    for e in extras_before or []:
        body.append(e)
    for t in tables:
        body.append(t)
    for e in extras_after or []:
        body.append(e)
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


def make_paragraph(text):
    p = ET.Element(qn("p"))
    pPr = ET.SubElement(p, qn("pPr"))
    ET.SubElement(pPr, qn("jc")).set(qn("val"), "both")
    r = ET.SubElement(p, qn("r"))
    ET.SubElement(r, qn("t")).text = text
    return p


def make_sdt(text):
    sdt = ET.Element(qn("sdt"))
    content = ET.SubElement(sdt, qn("sdtContent"))
    content.append(make_paragraph(text))
    return sdt


def make_drawing_paragraph():
    p = ET.Element(qn("p"))
    r = ET.SubElement(p, qn("r"))
    ET.SubElement(r, qn("drawing"))
    return p


# --------------------------------------------------------------------------- #
# Inspection helpers (read the formatted result).
# --------------------------------------------------------------------------- #
def tblPr_jc(tbl):
    tblPr = tbl.find("w:tblPr", NS)
    if tblPr is None:
        return None
    jc = tblPr.find("w:jc", NS)
    return None if jc is None else jc.get(qn("val"))


def cell_vAlign(tc):
    tcPr = tc.find("w:tcPr", NS)
    if tcPr is None:
        return None
    vAlign = tcPr.find("w:vAlign", NS)
    return None if vAlign is None else vAlign.get(qn("val"))


def paragraph_jc(p):
    pPr = p.find("w:pPr", NS)
    if pPr is None:
        return None
    jc = pPr.find("w:jc", NS)
    return None if jc is None else jc.get(qn("val"))


def paragraph_ind(p):
    pPr = p.find("w:pPr", NS)
    if pPr is None:
        return None
    ind = pPr.find("w:ind", NS)
    if ind is None:
        return None
    return {
        "left": ind.get(qn("left")),
        "firstLine": ind.get(qn("firstLine")),
        "right": ind.get(qn("right")),
    }


def ppr_children_in_order(p):
    """True if the pPr children respect the schema PPR_ORDER used by the script."""
    pPr = p.find("w:pPr", NS)
    if pPr is None:
        return True
    indices = []
    for child in pPr:
        local = child.tag.split("}")[-1]
        indices.append(fmt.PPR_ORDER.index(local) if local in fmt.PPR_ORDER else len(fmt.PPR_ORDER))
    return indices == sorted(indices)


def non_table_snapshot(doc):
    """Serialise every direct body child that is NOT a ``w:tbl`` (in order)."""
    body = doc.find("w:body", NS)
    snapshot = []
    for child in body:
        if child.tag == qn("tbl"):
            continue
        snapshot.append(ET.tostring(child))
    return snapshot


# --------------------------------------------------------------------------- #
# Hypothesis strategy: varied non-special table shapes.
# --------------------------------------------------------------------------- #
@st.composite
def table_specs(draw):
    """Generate varied table shapes: n_cols, n_rows, optional pre-existing
    tblGrid, optional gridSpan, and optionally ragged rows.

    Cell text is always ``rRcC`` so the table is never the removed
    ``is_tabel_1_2`` special case (which requires "Aktivitas" in cell 0)."""
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
    use_span = draw(st.booleans()) and n_cols >= 2 and n_rows >= 2
    ragged = draw(st.booleans()) and n_cols >= 2 and n_rows >= 2
    return n_cols, n_rows, grid_widths, use_span, ragged


def build_table_from_spec(spec):
    n_cols, n_rows, grid_widths, use_span, ragged = spec
    rows_texts = []
    row_spans = []
    for r in range(n_rows):
        if use_span and r == 1:
            texts = [f"r{r}c0"] + [f"r{r}c{c}" for c in range(2, n_cols)]
            spans = [2] + [None] * (n_cols - 2)
        elif ragged and r == n_rows - 1:
            # Drop the last physical cell to produce a ragged body row.
            texts = [f"r{r}c{c}" for c in range(n_cols - 1)]
            spans = [None] * (n_cols - 1)
        else:
            texts = [f"r{r}c{c}" for c in range(n_cols)]
            spans = [None] * n_cols
        rows_texts.append(texts)
        row_spans.append(spans)
    return make_table(rows_texts, grid_widths=grid_widths, row_spans=row_spans)


PBT = settings(
    max_examples=80,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)


# =========================================================================== #
# Property 4a - Table centering preserved (Requirement 3.1)
# =========================================================================== #
@given(spec=table_specs())
@settings(PBT)
def test_preserve_table_centering(spec):
    """**Property 2: Preservation** - table stays horizontally centered.

    Validates: Requirements 3.1
    """
    tbl = build_table_from_spec(spec)
    fmt.format_all_tables(make_doc([tbl]), NS)
    assert tblPr_jc(tbl) == "center", (
        f"expected tblPr/jc=center, got {tblPr_jc(tbl)!r} (spec={spec})"
    )


# =========================================================================== #
# Property 4b - Header-row cell centering preserved (Requirement 3.2)
# =========================================================================== #
@given(spec=table_specs())
@settings(PBT)
def test_preserve_header_cell_centering(spec):
    """**Property 2: Preservation** - row-0 cells keep vAlign=center and jc=center.

    Validates: Requirements 3.2
    """
    tbl = build_table_from_spec(spec)
    fmt.format_all_tables(make_doc([tbl]), NS)

    first_tr = tbl.find("w:tr", NS)
    for tc in first_tr.findall("w:tc", NS):
        assert cell_vAlign(tc) == "center", (
            f"expected header cell vAlign=center, got {cell_vAlign(tc)!r} (spec={spec})"
        )
        for p in tc.findall("w:p", NS):
            assert paragraph_jc(p) == "center", (
                f"expected header paragraph jc=center, got {paragraph_jc(p)!r} (spec={spec})"
            )


# =========================================================================== #
# Property 4c - Body-cell indentation cleared + PPR_ORDER preserved (Req 3.3)
# =========================================================================== #
@given(spec=table_specs())
@settings(PBT)
def test_preserve_body_cell_indentation_and_order(spec):
    """**Property 2: Preservation** - body cells have zeroed indentation, valid
    PPR_ORDER, and left alignment (non-special tables).

    Validates: Requirements 3.3
    """
    tbl = build_table_from_spec(spec)
    fmt.format_all_tables(make_doc([tbl]), NS)

    rows = tbl.findall("w:tr", NS)
    for row in rows[1:]:  # body rows only
        for tc in row.findall("w:tc", NS):
            for p in tc.findall("w:p", NS):
                ind = paragraph_ind(p)
                assert ind == {"left": "0", "firstLine": "0", "right": "0"}, (
                    f"expected body ind zeroed, got {ind!r} (spec={spec})"
                )
                assert ppr_children_in_order(p), (
                    f"expected pPr children in PPR_ORDER (spec={spec})"
                )
                assert paragraph_jc(p) == "left", (
                    f"expected body paragraph jc=left, got {paragraph_jc(p)!r} (spec={spec})"
                )


# =========================================================================== #
# Property 4d - Every table counted + summary print preserved (Requirement 3.4)
# =========================================================================== #
@given(n_tables=st.integers(min_value=0, max_value=5), spec=table_specs())
@settings(PBT)
def test_preserve_table_count_and_summary(n_tables, spec):
    """**Property 2: Preservation** - every w:tbl is processed and the
    ``Formatted N tables in document.xml.`` summary reports the correct N.

    Validates: Requirements 3.4
    """
    tables = [build_table_from_spec(spec) for _ in range(n_tables)]
    doc = make_doc(tables)

    buf = io.StringIO()
    with redirect_stdout(buf):
        fmt.format_all_tables(doc, NS)
    output = buf.getvalue()

    assert f"Formatted {n_tables} tables in document.xml." in output, (
        f"expected summary reporting {n_tables} tables, got output={output!r}"
    )


# =========================================================================== #
# Property 4e - Non-table content left untouched by the table stage (Req 3.5)
# =========================================================================== #
@given(spec=table_specs())
@settings(PBT)
def test_preserve_non_table_content(spec):
    """**Property 2: Preservation** - the table-formatting stage leaves
    non-table content (paragraphs, drawings, SDTs, sectPr/pgSz/pgMar) identical.

    Validates: Requirements 3.5
    """
    tbl = build_table_from_spec(spec)
    extras_before = [make_paragraph("intro narrative"), make_drawing_paragraph()]
    extras_after = [make_sdt("DAFTAR ISI"), make_paragraph("closing narrative")]
    doc = make_doc([tbl], extras_before=extras_before, extras_after=extras_after)

    before = non_table_snapshot(doc)
    fmt.format_all_tables(doc, NS)
    after = non_table_snapshot(doc)

    assert before == after, (
        "non-table content changed after format_all_tables\n"
        f"before={before!r}\nafter={after!r}\n(spec={spec})"
    )


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-v"]))
