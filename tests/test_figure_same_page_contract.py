"""Regression tests for the mandatory same-page figure/caption contract."""

import importlib.util
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_docx_structure_same_page",
    ROOT / "skills" / "scripts" / "validate_docx_structure.py",
)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)

INJECT_SPEC = importlib.util.spec_from_file_location(
    "inject_all_images_same_page",
    ROOT / "skills" / "scripts" / "inject_all_images.py",
)
injector = importlib.util.module_from_spec(INJECT_SPEC)
INJECT_SPEC.loader.exec_module(injector)

W = validator.W_NS
WP = validator.WP_NS


def qn(namespace, name):
    return f"{{{namespace}}}{name}"


def make_body(*, height=5_000_000, drawing_keep=True, caption_keep=True):
    body = ET.Element(qn(W, "body"))

    drawing_p = ET.SubElement(body, qn(W, "p"))
    drawing_p_pr = ET.SubElement(drawing_p, qn(W, "pPr"))
    if drawing_keep:
        ET.SubElement(drawing_p_pr, qn(W, "keepNext"))
        ET.SubElement(drawing_p_pr, qn(W, "keepLines"))
    run = ET.SubElement(drawing_p, qn(W, "r"))
    drawing = ET.SubElement(run, qn(W, "drawing"))
    inline = ET.SubElement(drawing, qn(WP, "inline"))
    ET.SubElement(inline, qn(WP, "extent"), cx="5000000", cy=str(height))
    ET.SubElement(inline, qn(WP, "docPr"), id="1", name="FIGURE:arsitektur")

    caption_p = ET.SubElement(body, qn(W, "p"))
    caption_p_pr = ET.SubElement(caption_p, qn(W, "pPr"))
    ET.SubElement(caption_p_pr, qn(W, "pStyle"), {qn(W, "val"): "Caption"})
    if caption_keep:
        ET.SubElement(caption_p_pr, qn(W, "keepNext"))
        ET.SubElement(caption_p_pr, qn(W, "keepLines"))
    caption_run = ET.SubElement(caption_p, qn(W, "r"))
    ET.SubElement(caption_run, qn(W, "t")).text = "Gambar 2.1 Arsitektur Sistem"
    return body


def test_same_page_contract_accepts_adjacent_pair_with_keep_chain_and_room():
    printable = 8_000_000
    assert validator.collect_figure_same_page_errors(
        make_body(), printable
    ) == []


def test_same_page_contract_rejects_missing_keep_chain():
    errors = validator.collect_figure_same_page_errors(
        make_body(drawing_keep=False), 8_000_000
    )
    assert any("[C4]" in error and "keepNext" in error for error in errors)
    assert any("[C4]" in error and "keepLines" in error for error in errors)


def test_same_page_contract_rejects_pair_taller_than_printable_height():
    printable = 8_000_000
    height = printable - validator.FIGURE_CAPTION_RESERVE_EMU + 1
    errors = validator.collect_figure_same_page_errors(
        make_body(height=height), printable
    )
    assert any("[C4]" in error and "caption reserve" in error for error in errors)


def test_same_page_contract_rejects_nonadjacent_caption():
    body = make_body()
    body.insert(1, ET.Element(qn(W, "p")))
    errors = validator.collect_figure_same_page_errors(body, 8_000_000)
    assert any("[C4]" in error and "immediately followed" in error for error in errors)


def test_injector_page_aware_cap_reserves_caption_height():
    width, height = injector.scaled_dimensions(
        5_000_000,
        10_000_000,
        max_height_emu=4_000_000,
    )
    assert height <= 4_000_000
    assert width == 2_000_000
