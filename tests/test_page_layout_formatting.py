"""Regression tests for the UPNVJ A4 + 4/3/3/3 cm page layout."""

from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import lxml.etree as LET


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import format_ta_proyek as formatter  # noqa: E402
import validate_docx_structure as validator  # noqa: E402


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def qn(name):
    return f"{{{W}}}{name}"


def test_layout_formatter_overwrites_bad_geometry_and_preserves_references():
    sect_pr = LET.Element(qn("sectPr"))
    header_ref = LET.SubElement(sect_pr, qn("headerReference"))
    header_ref.set(qn("type"), "default")
    pg_sz = LET.SubElement(sect_pr, qn("pgSz"))
    pg_sz.set(qn("w"), "16838")
    pg_sz.set(qn("h"), "11906")
    pg_sz.set(qn("orient"), "landscape")
    pg_mar = LET.SubElement(sect_pr, qn("pgMar"))
    for side in ("top", "right", "bottom", "left"):
        pg_mar.set(qn(side), "1440")

    formatter.apply_upnvj_page_layout(sect_pr)

    assert sect_pr.find(qn("headerReference")) is header_ref
    assert pg_sz.get(qn("w")) == "11906"
    assert pg_sz.get(qn("h")) == "16838"
    assert pg_sz.get(qn("orient")) is None
    assert pg_mar.get(qn("left")) == "2268"
    assert pg_mar.get(qn("top")) == "1701"
    assert pg_mar.get(qn("right")) == "1701"
    assert pg_mar.get(qn("bottom")) == "1701"


def _document_with_sections(section_specs):
    document = ET.Element(qn("document"))
    body = ET.SubElement(document, qn("body"))
    for spec in section_specs:
        paragraph = ET.SubElement(body, qn("p"))
        p_pr = ET.SubElement(paragraph, qn("pPr"))
        sect_pr = ET.SubElement(p_pr, qn("sectPr"))
        pg_sz = ET.SubElement(sect_pr, qn("pgSz"))
        pg_sz.set(qn("w"), str(spec.get("width", 11906)))
        pg_sz.set(qn("h"), str(spec.get("height", 16838)))
        if spec.get("orientation"):
            pg_sz.set(qn("orient"), spec["orientation"])
        pg_mar = ET.SubElement(sect_pr, qn("pgMar"))
        margins = spec.get("margins", {})
        for side, expected in validator.EXPECTED_MARGINS_DXA.items():
            pg_mar.set(qn(side), str(margins.get(side, expected)))
    return document


def test_layout_validator_accepts_every_compliant_section():
    document = _document_with_sections([{}, {}])
    assert validator.validate_page_layout(document) == []


def test_layout_validator_reports_wrong_margin_and_orientation():
    document = _document_with_sections([
        {"orientation": "landscape", "margins": {"left": 1701}},
    ])
    findings = validator.validate_page_layout(document)
    assert any("orientation='landscape'" in finding for finding in findings)
    assert any("margin left='1701'" in finding for finding in findings)
    assert any("expected 2268 twips (4 cm)" in finding for finding in findings)


def test_layout_validator_rejects_document_without_sections():
    document = ET.Element(qn("document"))
    ET.SubElement(document, qn("body"))
    assert validator.validate_page_layout(document) == [
        "[layout] no w:sectPr found; A4 size and margins are undefined."
    ]
