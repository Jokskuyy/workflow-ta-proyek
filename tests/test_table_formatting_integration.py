"""Integration test for table width fitting through ``format_document_xmls``.

Spec: .kiro/specs/table-formatting-fix (Task 4 checkpoint)

This exercises the FULL document-formatting entry point ``format_document_xmls``
(not just the ``format_all_tables`` unit) on an unpacked ``word/document.xml``
that carries three cross-branch table shapes:

  * 2 columns  -> representative of ``laporan/dwikhi`` (ERD attribute tables),
  * 4 columns  -> representative of ``laporan/iman``   (comparison tables),
  * 6 columns  -> representative of ``laporan/faiz``   (jadwal / kegiatan tables).

After the pipeline runs, EVERY table must receive uniform fit-to-printable
treatment regardless of its column count or cell text:

  * ``tblPr/tblLayout type=fixed``,
  * ``tblPr/tblW`` == printable width (dxa),
  * ``sum(tblGrid/gridCol@w)`` == printable width,
  * row 0 marked as a repeating header (``trPr/tblHeader``).

Validates: Requirements 2.1, 2.2, 2.3, 2.4
(and Correctness Properties 1, 2, 3 exercised end-to-end via the real pipeline).
"""
import sys
from pathlib import Path

import lxml.etree as ET
import pytest

# --------------------------------------------------------------------------- #
# Import the pipeline entry point from the canonical Mesin_Format script.
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


def qn(tag):
    return f"{{{W}}}{tag}"


# --------------------------------------------------------------------------- #
# Minimal OOXML builders.
# --------------------------------------------------------------------------- #
def make_cell(text=""):
    tc = ET.Element(qn("tc"))
    p = ET.SubElement(tc, qn("p"))
    r = ET.SubElement(p, qn("r"))
    ET.SubElement(r, qn("t")).text = text
    return tc


def make_row(cell_texts):
    tr = ET.Element(qn("tr"))
    for txt in cell_texts:
        tr.append(make_cell(txt))
    return tr


def make_table(rows_texts, grid_widths=None):
    tbl = ET.Element(qn("tbl"))
    ET.SubElement(tbl, qn("tblPr"))
    if grid_widths is not None:
        tblGrid = ET.SubElement(tbl, qn("tblGrid"))
        for w in grid_widths:
            ET.SubElement(tblGrid, qn("gridCol")).set(qn("w"), str(w))
    for texts in rows_texts:
        tbl.append(make_row(texts))
    return tbl


def make_paragraph(text):
    p = ET.Element(qn("p"))
    pPr = ET.SubElement(p, qn("pPr"))
    ET.SubElement(pPr, qn("jc")).set(qn("val"), "both")
    r = ET.SubElement(p, qn("r"))
    ET.SubElement(r, qn("t")).text = text
    return p


def build_cross_branch_document():
    """Build a ``w:document`` with 2-, 4- and 6-column tables plus the real
    body sectPr, interleaved with narrative paragraphs."""
    doc = ET.Element(qn("document"))
    body = ET.SubElement(doc, qn("body"))

    # dwikhi: 2-column ERD attribute table (pre-existing uneven grid).
    body.append(make_paragraph("Tabel atribut ERD."))
    body.append(
        make_table(
            [["Atribut", "Tipe Data"], ["id_gedung", "uuid"], ["nama", "text"]],
            grid_widths=[3000, 5000],
        )
    )

    # iman: 4-column comparison table (no pre-existing grid).
    body.append(make_paragraph("Tabel perbandingan metode."))
    body.append(
        make_table(
            [["Kriteria", "Waterfall", "Prototype", "RAD"],
             ["Kecepatan", "Lambat", "Sedang", "Cepat"]],
        )
    )

    # faiz: 6-column jadwal kegiatan table.
    body.append(make_paragraph("Tabel jadwal kegiatan."))
    body.append(
        make_table(
            [["Kegiatan", "M1", "M2", "M3", "M4", "M5"],
             ["Perancangan", "x", "x", "", "", ""],
             ["Implementasi", "", "", "x", "x", "x"]],
            grid_widths=[2500, 1100, 1100, 1100, 1100, 1100],
        )
    )

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
# Inspection helpers.
# --------------------------------------------------------------------------- #
def gridcol_widths(tbl):
    grid = tbl.find("w:tblGrid", NS)
    return [] if grid is None else [int(gc.get(qn("w"), "0")) for gc in grid.findall("w:gridCol", NS)]


def total_tblW(tbl):
    tblPr = tbl.find("w:tblPr", NS)
    tblW = None if tblPr is None else tblPr.find("w:tblW", NS)
    return None if tblW is None else (tblW.get(qn("type")), tblW.get(qn("w")))


def tbl_layout_type(tbl):
    tblPr = tbl.find("w:tblPr", NS)
    layout = None if tblPr is None else tblPr.find("w:tblLayout", NS)
    return None if layout is None else layout.get(qn("type"))


def row0_has_tblHeader(tbl):
    first_tr = tbl.find("w:tr", NS)
    if first_tr is None:
        return False
    trPr = first_tr.find("w:trPr", NS)
    return trPr is not None and trPr.find("w:tblHeader", NS) is not None


def n_cols_of(tbl):
    return len(gridcol_widths(tbl))


@pytest.fixture
def unpacked_dir(tmp_path):
    """Write a minimal unpacked docx tree carrying the cross-branch document."""
    word = tmp_path / "word"
    word.mkdir()
    doc = build_cross_branch_document()
    ET.ElementTree(doc).write(
        str(word / "document.xml"), encoding="utf-8", xml_declaration=True
    )
    return tmp_path


def test_format_document_xmls_fits_all_cross_branch_tables(unpacked_dir):
    """2-, 4- and 6-column tables all receive uniform fit-to-printable treatment
    when the full ``format_document_xmls`` pipeline runs.

    Validates: Requirements 2.1, 2.2, 2.3, 2.4
    """
    fmt.format_document_xmls(str(unpacked_dir))

    tree = ET.parse(str(unpacked_dir / "word" / "document.xml"))
    root = tree.getroot()
    tables = root.findall(".//w:tbl", NS)

    # All three cross-branch shapes must be present and processed.
    col_counts = sorted(n_cols_of(t) for t in tables)
    assert col_counts == [2, 4, 6], (
        f"expected 2-, 4- and 6-column tables, got column counts {col_counts}"
    )

    for tbl in tables:
        n_cols = n_cols_of(tbl)
        assert tbl_layout_type(tbl) == "fixed", (
            f"[{n_cols}-col] expected tblLayout=fixed, got {tbl_layout_type(tbl)!r}"
        )
        assert total_tblW(tbl) == ("dxa", str(PRINTABLE)), (
            f"[{n_cols}-col] expected tblW=({PRINTABLE},dxa), got {total_tblW(tbl)}"
        )
        widths = gridcol_widths(tbl)
        assert sum(widths) == PRINTABLE, (
            f"[{n_cols}-col] expected gridCol sum {PRINTABLE}, got {sum(widths)} -> {widths}"
        )
        assert row0_has_tblHeader(tbl), (
            f"[{n_cols}-col] expected row 0 trPr/tblHeader (repeating header)"
        )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
