"""Regression tests for the canonical UPNVJ page layout and line spacing."""

from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import lxml.etree as LET
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import format_ta_proyek as formatter  # noqa: E402
import create_faiz_base_docx as faiz_base  # noqa: E402
import merge_draft_to_docx as merger  # noqa: E402
import inject_all_images as image_injector  # noqa: E402
import update_fields_com as fields_com  # noqa: E402
import validate_docx_structure as validator  # noqa: E402


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"


def qn(name):
    return f"{{{W}}}{name}"


def test_report_heading_caption_and_toc_styles_are_forced_to_black():
    styles = LET.Element(qn("styles"))
    for style_id in formatter.REPORT_BLACK_STYLE_IDS:
        style = LET.SubElement(styles, qn("style"))
        style.set(qn("type"), "paragraph")
        style.set(qn("styleId"), style_id)
        r_pr = LET.SubElement(style, qn("rPr"))
        color = LET.SubElement(r_pr, qn("color"))
        color.set(qn("val"), "2F5496")
        color.set(qn("themeColor"), "accent1")
        color.set(qn("themeShade"), "BF")

    formatter.ensure_report_style_colors(styles)

    for style in styles.findall(qn("style")):
        color = style.find(f"{qn('rPr')}/{qn('color')}")
        assert color is not None
        assert color.get(qn("val")) == "000000"
        assert color.get(qn("themeColor")) is None
        assert color.get(qn("themeTint")) is None
        assert color.get(qn("themeShade")) is None


def test_faiz_base_caption_style_is_explicit_tnr_12_regular():
    doc = Document()
    normal = doc.styles["Normal"]
    caption = doc.styles["Caption"]

    faiz_base._configure_caption_style(caption, normal)

    assert caption.base_style == normal
    assert caption.font.name == "Times New Roman"
    assert caption.font.size.pt == 12
    assert caption.font.bold is False
    assert caption.font.italic is False
    assert str(caption.font.color.rgb) == "000000"
    assert caption._element.rPr.find(qn("szCs")).get(qn("val")) == "24"
    assert caption.paragraph_format.alignment == WD_ALIGN_PARAGRAPH.CENTER
    assert caption.paragraph_format.line_spacing == 1.0
    assert caption.paragraph_format.space_before.pt == 6
    assert caption.paragraph_format.space_after.pt == 6


def test_caption_seq_result_matches_label_typography():
    paragraph = LET.Element(qn("p"))
    formatter.format_caption_paragraph_clean(
        paragraph,
        "Gambar",
        "2.",
        "Gambar",
        1,
        "Arsitektur Sistem",
        {"w": W},
        semantic_bookmark="fig_arsitektur",
        semantic_bookmark_id=42,
    )

    runs_by_text = {
        "".join(run.itertext()): run
        for run in paragraph.findall(qn("r"))
        if "".join(run.itertext())
    }
    prefix = runs_by_text["Gambar 2."]
    seq_result = runs_by_text["1"]
    description = runs_by_text[" Arsitektur Sistem"]

    for run, expected_bold in (
        (prefix, True),
        (seq_result, True),
        (description, False),
    ):
        r_pr = run.find(qn("rPr"))
        assert r_pr is not None
        fonts = r_pr.find(qn("rFonts"))
        assert fonts is not None
        for attribute in ("ascii", "hAnsi", "eastAsia", "cs"):
            assert fonts.get(qn(attribute)) == "Times New Roman"
        assert r_pr.find(qn("sz")).get(qn("val")) == "24"
        assert r_pr.find(qn("szCs")).get(qn("val")) == "24"
        assert r_pr.find(qn("color")).get(qn("val")) == "000000"
        assert r_pr.find(qn("i")).get(qn("val")) == "0"
        assert r_pr.find(qn("iCs")).get(qn("val")) == "0"
        assert r_pr.find(qn("position")) is None
        assert r_pr.find(qn("vertAlign")) is None
        bold = r_pr.find(qn("b"))
        assert bold is not None
        assert (bold.get(qn("val")) != "0") is expected_bold


def test_caption_label_span_matches_visible_word_field_result():
    assert fields_com.caption_label_span("Gambar 2.1 Arsitektur Sistem") == (0, 10)
    assert fields_com.caption_label_span("Tabel 3.24 Hasil Pengujian") == (0, 10)
    assert fields_com.caption_label_span("Daftar Gambar") is None
    assert fields_com.caption_label_span("Gambar tanpa nomor") is None


def test_semantic_ref_com_formatting_is_regular_tnr_12():
    class Dummy:
        pass

    semantic_font = Dummy()
    ordinary_font = Dummy()
    semantic_field = Dummy()
    semantic_field.Code = Dummy()
    semantic_field.Code.Text = " REF fig_arsitektur \\h \\* CHARFORMAT "
    semantic_field.Result = Dummy()
    semantic_field.Result.Font = semantic_font
    ordinary_field = Dummy()
    ordinary_field.Code = Dummy()
    ordinary_field.Code.Text = " PAGE "
    ordinary_field.Result = Dummy()
    ordinary_field.Result.Font = ordinary_font
    document = Dummy()
    document.Fields = [semantic_field, ordinary_field]

    assert fields_com.format_semantic_reference_fields(document) == 1
    assert semantic_font.Name == "Times New Roman"
    assert semantic_font.NameAscii == "Times New Roman"
    assert semantic_font.NameFarEast == "Times New Roman"
    assert semantic_font.NameBi == "Times New Roman"
    assert semantic_font.Size == 12
    assert semantic_font.SizeBi == 12
    assert semantic_font.Bold == 0
    assert semantic_font.BoldBi == 0
    assert semantic_font.Italic == 0
    assert semantic_font.ItalicBi == 0
    assert semantic_font.Superscript == 0
    assert semantic_font.Subscript == 0
    assert semantic_font.Position == 0
    assert not hasattr(ordinary_font, "Name")


def test_inline_and_block_code_use_times_new_roman():
    paragraph = LET.Element(qn("p"))
    merger.add_formatted_text(paragraph, "Gunakan `NavigateTo`.")
    inline_code = next(
        run for run in paragraph.findall(qn("r"))
        if "NavigateTo" in "".join(run.itertext())
    )
    inline_fonts = inline_code.find(f"{qn('rPr')}/{qn('rFonts')}")
    assert inline_fonts.get(qn("ascii")) == "Times New Roman"
    assert inline_fonts.get(qn("hAnsi")) == "Times New Roman"
    assert inline_code.find(f"{qn('rPr')}/{qn('i')}") is not None
    assert inline_code.find(f"{qn('rPr')}/{qn('sz')}").get(qn("val")) == "24"
    assert inline_code.find(f"{qn('rPr')}/{qn('szCs')}").get(qn("val")) == "24"

    block = merger.build_code_block_elements({"lines": ["NavigateTo(target)"]})[0]
    block_fonts = block.find(f"{qn('r')}/{qn('rPr')}/{qn('rFonts')}")
    for attribute in ("ascii", "hAnsi", "eastAsia", "cs"):
        assert block_fonts.get(qn(attribute)) == "Times New Roman"
    block_rpr = block.find(f"{qn('r')}/{qn('rPr')}")
    assert block_rpr.find(qn("sz")).get(qn("val")) == "24"
    assert block_rpr.find(qn("szCs")).get(qn("val")) == "24"


def test_font_audit_rejects_theme_and_non_tnr_fonts():
    root = ET.Element(qn("document"))
    run = ET.SubElement(root, qn("r"))
    r_pr = ET.SubElement(run, qn("rPr"))
    fonts = ET.SubElement(r_pr, qn("rFonts"))
    fonts.set(qn("ascii"), "Calibri")
    fonts.set(qn("hAnsiTheme"), "minorHAnsi")
    findings = validator.validate_times_new_roman_fonts({
        "word/document.xml": ET.tostring(root),
    })
    assert any("Calibri" in finding for finding in findings)
    assert any("theme fonts are not allowed" in finding for finding in findings)


def test_post_com_font_normalizer_removes_theme_attributes():
    document = LET.Element(qn("document"))
    run = LET.SubElement(document, qn("r"))
    run_pr = LET.SubElement(run, qn("rPr"))
    fonts = LET.SubElement(run_pr, qn("rFonts"))
    fonts.set(qn("asciiTheme"), "minorHAnsi")
    fonts.set(qn("hAnsiTheme"), "minorHAnsi")

    assert image_injector.normalize_post_com_fonts(document) == 2
    for attribute in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
        assert fonts.get(qn(attribute)) is None
    for attribute in ("ascii", "hAnsi", "eastAsia", "cs"):
        assert fonts.get(qn(attribute)) == "Times New Roman"


def test_bold_audit_rejects_body_bold_but_allows_heading():
    document = ET.Element(qn("document"))
    body = ET.SubElement(document, qn("body"))

    chapter = ET.SubElement(body, qn("p"))
    chapter_pr = ET.SubElement(chapter, qn("pPr"))
    chapter_style = ET.SubElement(chapter_pr, qn("pStyle"))
    chapter_style.set(qn("val"), "Heading1")
    chapter_run = ET.SubElement(chapter, qn("r"))
    chapter_run_pr = ET.SubElement(chapter_run, qn("rPr"))
    ET.SubElement(chapter_run_pr, qn("b"))
    ET.SubElement(chapter_run, qn("t")).text = "BAB I PENDAHULUAN"

    body_paragraph = ET.SubElement(body, qn("p"))
    body_run = ET.SubElement(body_paragraph, qn("r"))
    body_run_pr = ET.SubElement(body_run, qn("rPr"))
    ET.SubElement(body_run_pr, qn("b"))
    ET.SubElement(body_run, qn("t")).text = "Gambar 2.1"

    findings = validator.validate_body_bold_usage(document)
    assert len(findings) == 1
    assert "Gambar 2.1" in findings[0]


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


def _page_number_relationships(reference_ids):
    targets = {
        "body_default_header": "ta-header-body-default.xml",
        "blank_header": "ta-header-blank.xml",
        "front_default_footer": "ta-footer-front-default.xml",
        "body_first_footer": "ta-footer-body-first.xml",
        "blank_footer": "ta-footer-blank.xml",
    }
    root = LET.Element(f"{{{PR}}}Relationships")
    for role, rid in reference_ids.items():
        relationship = LET.SubElement(root, f"{{{PR}}}Relationship")
        relationship.set("Id", rid)
        relationship.set("Target", targets[role])
    return root


def _page_number_parts():
    return {
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
