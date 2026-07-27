import json
import sys
from pathlib import Path

import lxml.etree as LET


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import inject_all_images as inj  # noqa: E402


W = inj.WORD_NS
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
NS = {"w": W, "wp": WP}


def _paragraph(text="", style=None, figure_id=None):
    paragraph = LET.Element(f"{{{W}}}p")
    if style:
        ppr = LET.SubElement(paragraph, f"{{{W}}}pPr")
        pstyle = LET.SubElement(ppr, f"{{{W}}}pStyle")
        pstyle.set(f"{{{W}}}val", style)
    if figure_id:
        run = LET.SubElement(paragraph, f"{{{W}}}r")
        drawing = LET.SubElement(run, f"{{{W}}}drawing")
        docpr = LET.SubElement(drawing, f"{{{WP}}}docPr")
        docpr.set("name", f"FIGURE:{figure_id}")
    if text:
        run = LET.SubElement(paragraph, f"{{{W}}}r")
        node = LET.SubElement(run, f"{{{W}}}t")
        node.text = text
    return paragraph


def _has_property(paragraph, name):
    return paragraph.find(f"w:pPr/w:{name}", NS) is not None


def test_requested_bab3_figure_pairs_have_page_group_metadata():
    manifest = json.loads((ROOT / "images" / "manifest.json").read_text(encoding="utf-8"))
    items = {item["id"]: item for item in manifest["images"]}
    expected = {
        "evidence_asset_cipto": ("bab3_cipto_pair", 1),
        "evidence_hierarchy_cipto": ("bab3_cipto_pair", 2),
        "evidence_asset_myamin": ("bab3_myamin_pair", 1),
        "evidence_hierarchy_myamin": ("bab3_myamin_pair", 2),
        "evidence_asset_wahidin": ("bab3_wahidin_pair", 1),
        "evidence_hierarchy_wahidin": ("bab3_wahidin_pair", 2),
        "evidence_asset_jenderal": ("bab3_jenderal_pair", 1),
        "evidence_hierarchy_jenderal": ("bab3_jenderal_pair", 2),
    }

    grouped_ids = {item["id"] for item in manifest["images"] if item.get("page_group")}
    assert grouped_ids == set(expected)
    for item_id, (group_id, order) in expected.items():
        assert items[item_id]["page_group"] == group_id
        assert items[item_id]["page_group_order"] == order
        assert items[item_id]["max_height_cm"] == 7.5


def test_page_group_links_narrative_two_figures_and_two_captions():
    body = LET.Element(f"{{{W}}}body")
    narrative = _paragraph("Uraian pasangan gambar.")
    drawing_one = _paragraph(figure_id="asset")
    caption_one = _paragraph("Gambar 3.41 Asset", style="Caption")
    drawing_two = _paragraph(figure_id="hierarchy")
    caption_two = _paragraph("Gambar 3.42 Hierarki", style="Caption")
    following = _paragraph("Paragraf berikutnya.")
    for paragraph in (
        narrative,
        drawing_one,
        caption_one,
        drawing_two,
        caption_two,
        following,
    ):
        body.append(paragraph)

    count = inj.enforce_manifest_page_groups(
        body,
        [
            {"id": "asset", "page_group": "pair", "page_group_order": 1},
            {"id": "hierarchy", "page_group": "pair", "page_group_order": 2},
        ],
        NS,
    )

    assert count == 1
    assert _has_property(narrative, "pageBreakBefore")
    for paragraph in (narrative, drawing_one, caption_one, drawing_two, caption_two):
        assert _has_property(paragraph, "keepNext")
        assert _has_property(paragraph, "keepLines")
    last_keep_next = caption_two.find("w:pPr/w:keepNext", NS)
    assert last_keep_next.get(f"{{{W}}}val") == "0"
    assert list(body)[5] is following
