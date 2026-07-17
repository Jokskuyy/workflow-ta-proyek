"""Regression tests for the mandatory figure-narration validator rule."""

import importlib.util
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "skills" / "scripts" / "validate_docx_structure.py"
FINAL_DOCX = ROOT / "Tugas_Akhir_Formatted.docx"

spec = importlib.util.spec_from_file_location("validate_docx_structure", VALIDATOR_PATH)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

W = validator.W_NS


def paragraph(text, style="Normal", drawing=False):
    p = ET.Element(f"{{{W}}}p")
    p_pr = ET.SubElement(p, f"{{{W}}}pPr")
    p_style = ET.SubElement(p_pr, f"{{{W}}}pStyle")
    p_style.set(f"{{{W}}}val", style)
    run = ET.SubElement(p, f"{{{W}}}r")
    if drawing:
        ET.SubElement(run, f"{{{W}}}drawing")
    text_el = ET.SubElement(run, f"{{{W}}}t")
    text_el.text = text
    return p


def test_missing_figure_narration_is_fatal_finding():
    paragraphs = [
        paragraph("BAB 2. RANCANGAN PROYEK", "Heading1"),
        paragraph("Gambar 2.1 Arsitektur Sistem", "Caption"),
        paragraph("Arsitektur sistem terdiri atas tiga komponen utama."),
    ]

    findings = validator.collect_figure_narration_errors(paragraphs, bab1_idx=0)

    assert findings == [
        '[narration] Gambar 2.1 tidak memiliki paragraf narasi yang menyebut '
        '"Gambar 2.1" dalam bab yang sama.'
    ]


def test_mid_sentence_reference_satisfies_rule():
    paragraphs = [
        paragraph("BAB 2. RANCANGAN PROYEK", "Heading1"),
        paragraph("Gambar 2.1 Arsitektur Sistem", "Caption"),
        paragraph("Arsitektur sistem pada Gambar 2.1 memperlihatkan tiga komponen utama."),
    ]

    assert validator.collect_figure_narration_errors(paragraphs, bab1_idx=0) == []


def test_reference_at_sentence_start_is_rejected():
    paragraphs = [
        paragraph("BAB 2. RANCANGAN PROYEK", "Heading1"),
        paragraph("Gambar 2.1 Arsitektur Sistem", "Caption"),
        paragraph("Gambar 2.1 memperlihatkan tiga komponen utama."),
    ]

    findings = validator.collect_figure_narration_errors(paragraphs, bab1_idx=0)

    assert findings == [
        "[narration] Rujukan Gambar 2.1 mengawali kalimat; rujukan harus "
        "ditempatkan di tengah kalimat narasi."
    ]


def test_reference_in_different_chapter_does_not_satisfy_rule():
    paragraphs = [
        paragraph("BAB 2. RANCANGAN PROYEK", "Heading1"),
        paragraph("Gambar 2.1 Arsitektur Sistem", "Caption"),
        paragraph("BAB 3. IMPLEMENTASI PROYEK", "Heading1"),
        paragraph("Pembahasan pada Gambar 2.1 tidak berada di bab yang sama."),
    ]

    findings = validator.collect_figure_narration_errors(paragraphs, bab1_idx=0)

    assert len(findings) == 1
    assert findings[0].startswith("[narration] Gambar 2.1 tidak memiliki")


@pytest.mark.skipif(not FINAL_DOCX.exists(), reason="generated DOCX is not present")
def test_generated_document_has_no_figure_narration_errors():
    with zipfile.ZipFile(FINAL_DOCX) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    body = root.find(f"{{{W}}}body")
    paragraphs = list(body.findall(f".//{{{W}}}p"))
    bab1_idx = next(
        i
        for i, p in enumerate(paragraphs)
        if validator._content_style(p).lower() == "heading1"
        and "PENDAHULUAN" in validator._content_text(p).upper()
    )

    assert validator.collect_figure_narration_errors(paragraphs, bab1_idx) == []
