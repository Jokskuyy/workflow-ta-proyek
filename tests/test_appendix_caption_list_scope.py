"""Regression tests for excluding appendix captions from automatic lists."""

from pathlib import Path
import sys

from lxml import etree


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import format_ta_proyek as formatter  # noqa: E402


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


def _paragraph(body, text):
    paragraph = etree.SubElement(body, f"{{{W}}}p")
    run = etree.SubElement(paragraph, f"{{{W}}}r")
    node = etree.SubElement(run, f"{{{W}}}t")
    node.text = text
    return paragraph


def test_main_body_bookmark_starts_at_bab_i_and_ends_before_appendix_text():
    document = etree.Element(f"{{{W}}}document")
    body = etree.SubElement(document, f"{{{W}}}body")
    _paragraph(body, "DAFTAR GAMBAR")
    bab_i = _paragraph(body, "BAB I PENDAHULUAN")
    _paragraph(body, "Gambar 1.1 Contoh")
    appendix = _paragraph(body, "LAMPIRAN 1. Dokumen")
    _paragraph(body, "Gambar 1.2 Bukti Lampiran")

    assert formatter.ensure_main_body_bookmark(document, NS)

    starts = document.xpath(
        './/w:bookmarkStart[@w:name="_TA_MainBody"]', namespaces=NS
    )
    assert len(starts) == 1
    start = starts[0]
    bookmark_id = start.get(f"{{{W}}}id")
    ends = document.xpath(
        f'.//w:bookmarkEnd[@w:id="{bookmark_id}"]', namespaces=NS
    )
    assert len(ends) == 1
    assert start.getparent() is bab_i
    assert ends[0].getparent() is appendix
    assert appendix.index(ends[0]) < appendix.index(
        appendix.find("w:r", namespaces=NS)
    )


def test_figure_and_table_lists_use_main_body_bookmark():
    source = (SCRIPTS / "format_ta_proyek.py").read_text(encoding="utf-8")
    assert r'TOC \\h \\z \\c "Gambar" \\b _TA_MainBody' in source
    assert r'TOC \\h \\z \\c "Tabel" \\b _TA_MainBody' in source
