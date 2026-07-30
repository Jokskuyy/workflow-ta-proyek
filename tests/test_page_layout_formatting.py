"""Regression tests for the canonical UPNVJ page layout and line spacing."""

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
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"


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
        {
            "orientation": "landscape",
            "margins": {"left": 1701, "top": 2268},
        },
    ])
    findings = validator.validate_page_layout(document)
    assert any("orientation='landscape'" in finding for finding in findings)
    assert any("margin left='1701'" in finding for finding in findings)
    assert any("margin top='2268'" in finding for finding in findings)
    assert any("expected 1701 twips (3 cm)" in finding for finding in findings)


def test_layout_validator_rejects_document_without_sections():
    document = ET.Element(qn("document"))
    ET.SubElement(document, qn("body"))
    assert validator.validate_page_layout(document) == [
        "[layout] no w:sectPr found; A4 size and margins are undefined."
    ]


def _numbered_chapter(text):
    paragraph = LET.Element(qn("p"))
    p_pr = LET.SubElement(paragraph, qn("pPr"))
    p_style = LET.SubElement(p_pr, qn("pStyle"))
    p_style.set(qn("val"), "Heading1")
    num_pr = LET.SubElement(p_pr, qn("numPr"))
    ilvl = LET.SubElement(num_pr, qn("ilvl"))
    ilvl.set(qn("val"), "0")
    num_id = LET.SubElement(num_pr, qn("numId"))
    num_id.set(qn("val"), "76")
    run = LET.SubElement(paragraph, qn("r"))
    LET.SubElement(run, qn("t")).text = text
    return paragraph


def _signed_scan(key):
    paragraph = LET.Element(qn("p"))
    p_pr = LET.SubElement(paragraph, qn("pPr"))
    LET.SubElement(p_pr, qn("jc")).set(qn("val"), "center")
    run = LET.SubElement(paragraph, qn("r"))
    drawing = LET.SubElement(run, qn("drawing"))
    inline = LET.SubElement(
        drawing,
        "{http://schemas.openxmlformats.org/drawingml/2006/"
        "wordprocessingDrawing}inline",
    )
    doc_pr = LET.SubElement(
        inline,
        "{http://schemas.openxmlformats.org/drawingml/2006/"
        "wordprocessingDrawing}docPr",
    )
    doc_pr.set("name", f"FRONT_MATTER_SCAN:iman:{key}")
    return paragraph


def _scan_anchor(text):
    paragraph = LET.Element(qn("p"))
    p_pr = LET.SubElement(paragraph, qn("pPr"))
    p_style = LET.SubElement(p_pr, qn("pStyle"))
    p_style.set(qn("val"), "FrontMatterHeading")
    run = LET.SubElement(paragraph, qn("r"))
    LET.SubElement(run, qn("t")).text = text
    return paragraph


def _page_number_relationships(reference_ids):
    targets = {
        "body_default_header": "ta-header-body-default.xml",
        "blank_header": "ta-header-blank.xml",
        "front_default_footer": "ta-footer-front-default.xml",
        "body_first_footer": "ta-footer-body-first.xml",
        "blank_footer": "ta-footer-blank.xml",
        "body_identity_footer": "ta-footer-body-identity.xml",
        "body_first_identity_footer": "ta-footer-body-first-identity.xml",
    }
    root = LET.Element(f"{{{PR}}}Relationships")
    for role, rid in reference_ids.items():
        relationship = LET.SubElement(root, f"{{{PR}}}Relationship")
        relationship.set("Id", rid)
        relationship.set("Target", targets[role])
    return root


def _page_number_parts(identity_footer=None):
    parts = {
        "word/ta-header-body-default.xml": formatter.build_page_number_part(
            "header", "right", True
        ),
        "word/ta-header-blank.xml": formatter.build_page_number_part(
            "header", "right", False
        ),
        "word/ta-footer-front-default.xml": formatter.build_page_number_part(
            "footer", "right", True
        ),
        "word/ta-footer-body-first.xml": formatter.build_page_number_part(
            "footer", "center", True
        ),
        "word/ta-footer-blank.xml": formatter.build_page_number_part(
            "footer", "center", False
        ),
    }
    if identity_footer:
        parts["word/ta-footer-body-identity.xml"] = (
            formatter.build_identity_footer_part(
                identity_footer,
                include_page=False,
            )
        )
        parts["word/ta-footer-body-first-identity.xml"] = (
            formatter.build_identity_footer_part(
                identity_footer,
                include_page=True,
            )
        )
    return parts


def test_page_numbering_creates_front_and_one_section_per_bab():
    document = LET.Element(qn("document"))
    body = LET.SubElement(document, qn("body"))
    body.append(LET.Element(qn("p")))
    for number in range(1, 4):
        body.append(_numbered_chapter(f"BAB {number}"))
        body.append(LET.Element(qn("p")))
    original = LET.SubElement(body, qn("sectPr"))

    reference_ids = {
        "body_default_header": "rId101",
        "blank_header": "rId102",
        "front_default_footer": "rId103",
        "body_first_footer": "rId104",
        "blank_footer": "rId105",
    }
    section_count = formatter.configure_report_sections(
        body, {"w": W}, original, reference_ids
    )

    sections = list(body.iter(qn("sectPr")))
    assert section_count == 4
    assert len(sections) == 4
    assert sections[0].find(qn("pgNumType")).get(qn("fmt")) == "lowerRoman"
    assert sections[0].find(qn("pgNumType")).get(qn("start")) == "1"
    assert sections[1].find(qn("pgNumType")).get(qn("fmt")) == "decimal"
    assert sections[1].find(qn("pgNumType")).get(qn("start")) == "1"
    assert sections[2].find(qn("pgNumType")).get(qn("start")) is None
    assert sections[3].find(qn("pgNumType")).get(qn("start")) is None

    findings = validator.validate_page_numbering(
        document,
        _page_number_relationships(reference_ids),
        _page_number_parts(),
    )
    assert findings == []


def test_signed_scan_pages_hide_word_footer_without_restarting_roman_numbers():
    document = LET.Element(qn("document"))
    body = LET.SubElement(document, qn("body"))
    body.append(LET.Element(qn("p")))
    for key in ("approval", "authenticity", "publication"):
        body.append(_scan_anchor(key))
        body.append(_signed_scan(key))
    body.append(LET.Element(qn("p")))
    body.append(_numbered_chapter("BAB I"))
    body.append(LET.Element(qn("p")))
    original = LET.SubElement(body, qn("sectPr"))
    reference_ids = {
        "body_default_header": "rId401",
        "blank_header": "rId402",
        "front_default_footer": "rId403",
        "body_first_footer": "rId404",
        "blank_footer": "rId405",
    }

    section_count = formatter.configure_report_sections(
        body,
        {"w": W},
        original,
        reference_ids,
    )

    sections = list(body.iter(qn("sectPr")))
    assert section_count == 6
    assert len(sections) == 6
    for section in sections[1:4]:
        pg_num = section.find(qn("pgNumType"))
        assert pg_num.get(qn("fmt")) == "lowerRoman"
        assert pg_num.get(qn("start")) is None
        assert section.find(qn("titlePg")) is None
    trailing_front_num = sections[4].find(qn("pgNumType"))
    assert trailing_front_num.get(qn("fmt")) == "lowerRoman"
    assert trailing_front_num.get(qn("start")) is None
    assert sections[4].find(qn("titlePg")) is None
    assert sections[5].find(qn("pgNumType")).get(qn("start")) == "1"

    assert validator.validate_page_numbering(
        document,
        _page_number_relationships(reference_ids),
        _page_number_parts(),
    ) == []


def test_identity_footer_stops_before_appendix_and_keeps_page_numbering():
    identity_footer = {
        "author_year": "Muhammad Iman Nugraha, 2026",
        "title": (
            "PENGEMBANGAN DASHBOARD WEB, INTEGRASI UNITY WEBGL, DAN "
            "DEPLOYMENT SISTEM DENAH VIRTUAL UPNVJ KAMPUS PONDOK LABU"
        ),
        "institution": (
            "UPN Veteran Jakarta, Fakultas Ilmu Komputer, S1 Informatika"
        ),
        "links": (
            "[www.upnvj.ac.id-www.library.upnvj.ac.id-"
            "www.repository.upnvj.ac.id]"
        ),
        "font": "Times New Roman",
        "size_pt": 8,
    }
    document = LET.Element(qn("document"))
    body = LET.SubElement(document, qn("body"))
    body.append(LET.Element(qn("p")))
    for number in range(1, 3):
        body.append(_numbered_chapter(f"BAB {number}"))
        body.append(LET.Element(qn("p")))
    appendix = LET.Element(qn("p"))
    appendix_p_pr = LET.SubElement(appendix, qn("pPr"))
    appendix_style = LET.SubElement(appendix_p_pr, qn("pStyle"))
    appendix_style.set(qn("val"), "taappendixheading")
    appendix_run = LET.SubElement(appendix, qn("r"))
    LET.SubElement(appendix_run, qn("t")).text = "LAMPIRAN 1. Bukti"
    body.append(appendix)
    original = LET.SubElement(body, qn("sectPr"))
    reference_ids = {
        "body_default_header": "rId301",
        "blank_header": "rId302",
        "front_default_footer": "rId303",
        "body_first_footer": "rId304",
        "blank_footer": "rId305",
        "body_identity_footer": "rId306",
        "body_first_identity_footer": "rId307",
    }

    section_count = formatter.configure_report_sections(
        body,
        {"w": W},
        original,
        reference_ids,
        split_appendix=True,
    )
    sections = list(body.iter(qn("sectPr")))
    assert section_count == 4
    assert len(sections) == 4
    assert sections[-1].find(qn("titlePg")) is None

    rels = _page_number_relationships(reference_ids)
    parts = _page_number_parts(identity_footer)
    assert validator.validate_page_numbering(document, rels, parts) == []
    assert validator.validate_identity_footer(
        document,
        rels,
        parts,
        identity_footer,
    ) == []


def test_page_numbering_validator_reports_restart_and_wrong_position():
    document = LET.Element(qn("document"))
    body = LET.SubElement(document, qn("body"))
    body.append(LET.Element(qn("p")))
    body.append(_numbered_chapter("BAB I"))
    body.append(LET.Element(qn("p")))
    original = LET.SubElement(body, qn("sectPr"))
    reference_ids = {
        "body_default_header": "rId201",
        "blank_header": "rId202",
        "front_default_footer": "rId203",
        "body_first_footer": "rId204",
        "blank_footer": "rId205",
    }
    formatter.configure_report_sections(body, {"w": W}, original, reference_ids)
    sections = list(body.iter(qn("sectPr")))
    sections[1].find(qn("pgNumType")).set(qn("start"), "9")
    parts = _page_number_parts()
    continuation = parts["word/ta-header-body-default.xml"]
    continuation.find(f".//{qn('jc')}").set(qn("val"), "left")

    findings = validator.validate_page_numbering(
        document,
        _page_number_relationships(reference_ids),
        parts,
    )
    assert any("BAB I must restart Arabic numbering at 1" in item for item in findings)
    assert any("continuation header PAGE field alignment='left'" in item for item in findings)


def test_page_number_parts_are_idempotent(tmp_path):
    rels_dir = tmp_path / "word" / "_rels"
    rels_dir.mkdir(parents=True)
    rels_root = LET.Element(f"{{{PR}}}Relationships")
    LET.ElementTree(rels_root).write(
        rels_dir / "document.xml.rels", encoding="utf-8", xml_declaration=True
    )
    content_types_ns = formatter.CONTENT_TYPES_NS
    content_types = LET.Element(f"{{{content_types_ns}}}Types")
    LET.ElementTree(content_types).write(
        tmp_path / "[Content_Types].xml", encoding="utf-8", xml_declaration=True
    )

    first = formatter.ensure_page_number_parts(str(tmp_path))
    second = formatter.ensure_page_number_parts(str(tmp_path))

    assert first == second
    parsed_rels = LET.parse(rels_dir / "document.xml.rels").getroot()
    assert len(parsed_rels) == 5
    parsed_types = LET.parse(tmp_path / "[Content_Types].xml").getroot()
    overrides = parsed_types.findall(f"{{{content_types_ns}}}Override")
    assert len(overrides) == 5


def _styles_with_main_spacing(line="276", line_rule="auto"):
    styles = ET.Element(qn("styles"))
    for style_id in validator.REQUIRED_MAIN_LINE_SPACING_STYLES:
        style = ET.SubElement(styles, qn("style"))
        style.set(qn("type"), "paragraph")
        style.set(qn("styleId"), style_id)
        p_pr = ET.SubElement(style, qn("pPr"))
        spacing = ET.SubElement(p_pr, qn("spacing"))
        spacing.set(qn("before"), "0")
        spacing.set(qn("after"), "0")
        spacing.set(qn("line"), line)
        spacing.set(qn("lineRule"), line_rule)
    return styles


def _word_normalized_styles_with_default_spacing():
    styles = ET.Element(qn("styles"))
    doc_defaults = ET.SubElement(styles, qn("docDefaults"))
    p_pr_default = ET.SubElement(doc_defaults, qn("pPrDefault"))
    default_p_pr = ET.SubElement(p_pr_default, qn("pPr"))
    default_spacing = ET.SubElement(default_p_pr, qn("spacing"))
    default_spacing.set(qn("line"), "276")
    default_spacing.set(qn("lineRule"), "auto")

    for style_id in validator.REQUIRED_MAIN_LINE_SPACING_STYLES:
        style = ET.SubElement(styles, qn("style"))
        style.set(qn("type"), "paragraph")
        style.set(qn("styleId"), style_id)
        if style_id != "Normal":
            based_on = ET.SubElement(style, qn("basedOn"))
            based_on.set(qn("val"), "Normal")
        if style_id.startswith("Heading"):
            p_pr = ET.SubElement(style, qn("pPr"))
            spacing = ET.SubElement(p_pr, qn("spacing"))
            spacing.set(qn("before"), "240")
            spacing.set(qn("after"), "120")
    return styles


def test_formatter_uses_word_auto_value_for_1_15_lines():
    assert formatter.MAIN_LINE_SPACING_AUTO == "276"
    assert formatter.main_line_spacing_attrs() == {
        "before": "0",
        "after": "0",
        "line": "276",
        "lineRule": "auto",
    }
    assert formatter.main_line_spacing_attrs("240", "120")["line"] == "276"


def test_spacing_validator_accepts_all_compliant_main_styles():
    styles = _styles_with_main_spacing()
    assert validator.validate_main_line_spacing(styles) == []


def test_spacing_validator_accepts_word_normalized_inherited_spacing():
    styles = _word_normalized_styles_with_default_spacing()
    assert validator.validate_main_line_spacing(styles) == []


def test_spacing_validator_reports_legacy_1_5_value():
    styles = _styles_with_main_spacing(line="360")
    findings = validator.validate_main_line_spacing(styles)
    assert len(findings) == len(validator.REQUIRED_MAIN_LINE_SPACING_STYLES)
    assert all("expected line='276'" in finding for finding in findings)
    assert all("1.15 lines" in finding for finding in findings)
