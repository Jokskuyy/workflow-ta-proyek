"""Regression tests for the handoff typography contract."""

import importlib.util
import sys
from pathlib import Path

import lxml.etree as ET

ROOT = Path(__file__).resolve().parents[1]
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


mrg = _load("typography_merge", ROOT / "skills/scripts/merge_draft_to_docx.py")
fmt = _load("typography_format", ROOT / "skills/scripts/format_ta_proyek.py")


def _rpr(run):
    return run.find("w:rPr", NS)


def test_inline_code_is_times_new_roman_12_italic():
    p = ET.Element(f"{{{W}}}p")
    mrg.add_formatted_text(p, "nilai `unity_object_name`")
    run = next(r for r in p.findall("w:r", NS) if "unity_object_name" in "".join(r.itertext()))
    rpr = _rpr(run)
    fonts = rpr.find("w:rFonts", NS)
    assert fonts.get(f"{{{W}}}ascii") == "Times New Roman"
    assert rpr.find("w:i", NS) is not None
    assert rpr.find("w:sz", NS).get(f"{{{W}}}val") == "24"


def test_fenced_code_uses_codeblock_courier_new_12_italic():
    p = mrg.build_code_block_elements({"lines": ["SELECT 1;"]})[0]
    assert p.find("w:pPr/w:pStyle", NS).get(f"{{{W}}}val") == "CodeBlock"
    run = p.find("w:r", NS)
    rpr = _rpr(run)
    fonts = rpr.find("w:rFonts", NS)
    assert fonts.get(f"{{{W}}}ascii") == "Courier New"
    assert rpr.find("w:i", NS) is not None
    assert rpr.find("w:sz", NS).get(f"{{{W}}}val") == "24"
    assert p.find("w:pPr/w:jc", NS).get(f"{{{W}}}val") == "left"
    assert p.find("w:pPr/w:spacing", NS).get(f"{{{W}}}line") == "240"


def test_foreign_full_term_in_table_is_italic_but_acronyms_are_regular():
    root = ET.Element(f"{{{W}}}document")
    table = ET.SubElement(root, f"{{{W}}}tbl")
    cell = ET.SubElement(ET.SubElement(table, f"{{{W}}}tr"), f"{{{W}}}tc")
    paragraph = ET.SubElement(cell, f"{{{W}}}p")
    run = ET.SubElement(paragraph, f"{{{W}}}r")
    text = ET.SubElement(run, f"{{{W}}}t")
    text.text = "Full Stack Web Developer API SQL RLS UAT WebGL"
    fmt.apply_required_inline_term_formatting(root, NS)
    fmt.normalize_regular_technical_terms(root, NS)
    runs = [("".join(r.itertext()), _rpr(r)) for r in paragraph.findall("w:r", NS)]
    assert any("Full Stack Web Developer" in text and rpr.find("w:i", NS) is not None for text, rpr in runs)
    for acronym in ("API", "SQL", "RLS", "UAT", "WebGL"):
        matching = [(text, rpr) for text, rpr in runs if acronym in text]
        assert matching and all(rpr is None or rpr.find("w:i", NS) is None for _, rpr in matching)


def test_codeblock_style_is_defined_by_formatter():
    styles = ET.Element(f"{{{W}}}styles")
    fmt.ensure_codeblock_style(styles)
    style = styles.find("w:style[@w:styleId='CodeBlock']", NS)
    assert style is not None
    assert style.find("w:rPr/w:rFonts", NS).get(f"{{{W}}}ascii") == "Courier New"
    assert style.find("w:rPr/w:i", NS) is not None
