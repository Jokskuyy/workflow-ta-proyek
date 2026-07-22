"""Regression coverage for stable figure/table IDs and Word REF fields."""

import importlib.util
import json
import sys
from pathlib import Path

import lxml.etree as LET
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


mrg = _load(
    "semantic_merge",
    ROOT / "skills" / "scripts" / "merge_draft_to_docx.py",
)
fmt = _load(
    "semantic_format",
    ROOT / "skills" / "scripts" / "format_ta_proyek.py",
)
validator = _load(
    "semantic_validator",
    ROOT / "skills" / "scripts" / "validate_docx_structure.py",
)
sys.path.insert(0, str(ROOT / "skills" / "scripts"))
from alur_penulisan.draft_model import DraftModel  # noqa: E402
from alur_penulisan.figure_table import number_objects  # noqa: E402

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


def _write_manifest(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({
        "images": [{
            "id": "arsitektur",
            "file": "arsitektur.png",
            "caption_match": "Arsitektur Sistem",
            "inject_method": "post_com",
        }]
    }), encoding="utf-8")
    return path


def test_table_id_is_metadata_not_a_table_opener(tmp_path):
    draft = tmp_path / "draft.md"
    draft.write_text(
        "# BAB I PENDAHULUAN\n\n"
        "Rincian hasil ditampilkan pada [TABREF:hasil_uji].\n\n"
        "[TABLE-ID:hasil_uji]\n"
        "[TABLECAPTION:Hasil Pengujian]\n"
        "[TABLE]\nA | B\n1 | 2\n[/TABLE]\n",
        encoding="utf-8",
    )

    items = mrg.parse_markdown(draft, workspace_root=tmp_path)

    assert [item["type"] for item in items] == [
        "heading", "paragraph", "table_marker", "paragraph", "table"
    ]
    assert items[3]["text"] == "[TABLECAPTION:hasil_uji|Hasil Pengujian]"
    assert mrg.collect_unclosed_table_warnings(draft.read_text().splitlines()) == []


def test_semantic_figure_and_table_contract_is_valid(tmp_path):
    draft = tmp_path / "draft.md"
    draft.write_text(
        "# BAB II RANCANGAN PROYEK\n\n"
        "Susunan komponen ditampilkan pada [FIGREF:arsitektur].\n\n"
        "[FIGURE:arsitektur]\n"
        "[FIGCAPTION:Arsitektur Sistem]\n\n"
        "Rincian komponen disajikan pada [TABREF:komponen].\n\n"
        "[TABLE-ID:komponen]\n"
        "[TABLECAPTION:Komponen Sistem]\n"
        "[TABLE]\nKomponen | Fungsi\nA | B\n[/TABLE]\n",
        encoding="utf-8",
    )
    items = mrg.parse_markdown(draft, workspace_root=tmp_path)

    assert mrg.validate_figure_markers(items, _write_manifest(tmp_path)) == []


def test_semantic_reference_requires_known_adjacent_caption(tmp_path):
    items = [
        {"type": "heading", "level": 1, "text": "BAB II RANCANGAN"},
        {"type": "paragraph", "text": "Uraian pada [FIGREF:arsitektur] tersedia."},
        {"type": "paragraph", "text": "[FIGURE:arsitektur]"},
        {"type": "paragraph", "text": "Gambar 2.1 Arsitektur Sistem"},
    ]

    errors = mrg.validate_figure_markers(items, _write_manifest(tmp_path))

    assert any("requires an adjacent [FIGCAPTION" in error for error in errors)


def test_semantic_caption_parser_and_bookmark_are_stable():
    assert fmt.parse_caption_text(
        "[FIGCAPTION:arsitektur|Arsitektur Sistem]"
    ) == ("Gambar", None, "Arsitektur Sistem")
    first = fmt.make_crossref_bookmark("Gambar", "id_yang_sangat_panjang_" * 4)
    second = fmt.make_crossref_bookmark("Gambar", "id_yang_sangat_panjang_" * 4)
    assert first == second
    assert first.startswith("fig_")
    assert len(first) <= 40


def test_caption_bookmark_spans_prefix_and_seq_number_only():
    paragraph = LET.Element(f"{{{W}}}p")
    fmt.format_caption_paragraph_clean(
        paragraph,
        "Gambar",
        "2.",
        "Gambar",
        3,
        "Arsitektur Sistem",
        NS,
        semantic_bookmark="fig_arsitektur",
        semantic_bookmark_id=91,
    )

    children = list(paragraph)
    start_index = next(i for i, child in enumerate(children)
                       if child.tag == f"{{{W}}}bookmarkStart")
    end_index = next(i for i, child in enumerate(children)
                     if child.tag == f"{{{W}}}bookmarkEnd"
                     and child.get(f"{{{W}}}id") == "91")
    description_index = max(i for i, child in enumerate(children)
                            if child.find(f"{{{W}}}t") is not None)
    visible = "".join(
        element.text or "" for element in paragraph.iter(f"{{{W}}}t")
    )
    assert start_index < end_index < description_index
    assert "Gambar 2.3 Arsitektur Sistem" == visible
    assert "SEQ Gambar" in " ".join(
        element.text or "" for element in paragraph.iter(f"{{{W}}}instrText")
    )


def test_entire_figure_number_is_bold_12pt_but_description_is_not_bold():
    paragraph = LET.Element(f"{{{W}}}p")
    fmt.format_caption_paragraph_clean(
        paragraph,
        "Gambar",
        "3.",
        "Gambar",
        7,
        "Hierarki aset",
        NS,
    )

    number_run = next(
        run for run in paragraph.findall("w:r", NS)
        if "".join(run.itertext()) == "7"
    )
    number_props = number_run.find("w:rPr", NS)
    assert number_props.find("w:b", NS) is not None
    assert number_props.find("w:bCs", NS) is not None
    assert number_props.find("w:sz", NS).get(f"{{{W}}}val") == "24"

    description_run = next(
        run for run in paragraph.findall("w:r", NS)
        if "Hierarki aset" in "".join(run.itertext())
    )
    description_props = description_run.find("w:rPr", NS)
    assert description_props.find("w:b", NS) is None


def test_entire_table_number_is_bold_12pt_but_description_is_not_bold():
    paragraph = LET.Element(f"{{{W}}}p")
    fmt.format_caption_paragraph_clean(
        paragraph,
        "Tabel",
        "2.",
        "Tabel",
        4,
        "Rangkuman pengujian",
        NS,
    )

    number_runs = paragraph.findall("w:r", NS)[:6]
    visible = "".join(
        element.text or "" for element in paragraph.iter(f"{{{W}}}t")
    )
    assert visible == "Tabel 2.4 Rangkuman pengujian"
    for run in number_runs:
        props = run.find("w:rPr", NS)
        assert props is not None
        assert props.find("w:b", NS) is not None
        assert props.find("w:bCs", NS) is not None
        assert props.find("w:sz", NS).get(f"{{{W}}}val") == "24"
        assert props.find("w:szCs", NS).get(f"{{{W}}}val") == "24"

    description_run = paragraph.findall("w:r", NS)[-1]
    description_props = description_run.find("w:rPr", NS)
    assert description_props.find("w:b", NS) is None


def test_required_technical_terms_are_split_and_formatted_without_field_damage():
    root = LET.Element(f"{{{W}}}document")
    body = LET.SubElement(root, f"{{{W}}}body")
    paragraph = LET.SubElement(body, f"{{{W}}}p")
    run = LET.SubElement(paragraph, f"{{{W}}}r")
    text = LET.SubElement(run, f"{{{W}}}t")
    text.text = "Asset Pointer di Unity memakai child dewi_sartika pada database."

    field_run = LET.SubElement(paragraph, f"{{{W}}}r")
    instruction = LET.SubElement(field_run, f"{{{W}}}instrText")
    instruction.text = " REF Unity_Pointer \\h "

    count = fmt.apply_required_inline_term_formatting(root, NS)

    assert count == 6
    assert "".join(paragraph.itertext()) == (
        "Asset Pointer di Unity memakai child dewi_sartika pada database."
        " REF Unity_Pointer \\h "
    )
    assert instruction.getparent() is field_run
    formatted_texts = []
    for candidate in paragraph.findall("w:r", NS):
        props = candidate.find("w:rPr", NS)
        if props is None or props.find("w:i", NS) is None:
            continue
        assert props.find("w:iCs", NS) is not None
        assert props.find("w:sz", NS).get(f"{{{W}}}val") == "24"
        assert props.find("w:szCs", NS).get(f"{{{W}}}val") == "24"
        formatted_texts.append("".join(candidate.itertext()))
    assert formatted_texts == [
        "Asset", "Pointer", "Unity", "child", "dewi_sartika", "database"
    ]


def test_confirmed_product_names_and_acronyms_are_italic_12pt():
    root = LET.Element(f"{{{W}}}document")
    body = LET.SubElement(root, f"{{{W}}}body")
    paragraph = LET.SubElement(body, f"{{{W}}}p")
    run = LET.SubElement(paragraph, f"{{{W}}}r")
    text = LET.SubElement(run, f"{{{W}}}t")
    text.text = "Unity React Supabase PostgreSQL API SQL RLS UAT WebGL"

    count = fmt.apply_required_inline_term_formatting(root, NS)

    assert count == 9
    italic_texts = []
    for candidate in paragraph.findall("w:r", NS):
        props = candidate.find("w:rPr", NS)
        if props is None or props.find("w:i", NS) is None:
            continue
        assert props.find("w:iCs", NS) is not None
        assert props.find("w:sz", NS).get(f"{{{W}}}val") == "24"
        assert props.find("w:szCs", NS).get(f"{{{W}}}val") == "24"
        italic_texts.append("".join(candidate.itertext()))

    assert italic_texts == [
        "Unity", "React", "Supabase", "PostgreSQL", "API", "SQL", "RLS", "UAT", "WebGL"
    ]


def test_every_explicit_9pt_size_is_normalized_to_12pt():
    root = LET.Element(f"{{{W}}}document")
    body = LET.SubElement(root, f"{{{W}}}body")
    paragraph = LET.SubElement(body, f"{{{W}}}p")
    paragraph_props = LET.SubElement(paragraph, f"{{{W}}}pPr")
    style = LET.SubElement(paragraph_props, f"{{{W}}}pStyle")
    style.set(f"{{{W}}}val", "Normal")
    alignment = LET.SubElement(paragraph_props, f"{{{W}}}jc")
    alignment.set(f"{{{W}}}val", "left")
    indentation = LET.SubElement(paragraph_props, f"{{{W}}}ind")
    indentation.set(f"{{{W}}}left", "720")
    indentation.set(f"{{{W}}}firstLine", "0")
    run = LET.SubElement(paragraph, f"{{{W}}}r")
    run_props = LET.SubElement(run, f"{{{W}}}rPr")
    size = LET.SubElement(run_props, f"{{{W}}}sz")
    size.set(f"{{{W}}}val", "18")
    size_cs = LET.SubElement(run_props, f"{{{W}}}szCs")
    size_cs.set(f"{{{W}}}val", "18")
    text = LET.SubElement(run, f"{{{W}}}t")
    text.text = "SELECT * FROM gedung;"

    updated = fmt.normalize_nine_point_font_size(root, NS)

    assert updated == 2
    assert run_props.find("w:sz", NS).get(f"{{{W}}}val") == "24"
    assert run_props.find("w:szCs", NS).get(f"{{{W}}}val") == "24"


def test_reference_token_becomes_ref_field_with_cached_value():
    paragraph = LET.Element(f"{{{W}}}p")
    run = LET.SubElement(paragraph, f"{{{W}}}r")
    text = LET.SubElement(run, f"{{{W}}}t")
    text.text = "Susunan pada [FIGREF:arsitektur] menjelaskan sistem."
    targets = {("FIGREF", "arsitektur"): {
        "bookmark": "fig_arsitektur",
        "display": "Gambar 2.3",
    }}

    count, unresolved = fmt.replace_semantic_references_in_paragraph(
        paragraph, targets, NS
    )

    assert count == 1
    assert unresolved == []
    assert "".join(paragraph.itertext()) == (
        "Susunan pada  REF fig_arsitektur \\h Gambar 2.3 menjelaskan sistem."
    )
    assert "REF fig_arsitektur \\h" in " ".join(
        element.text or "" for element in paragraph.iter(f"{{{W}}}instrText")
    )
    assert "[FIGREF:" not in "".join(
        element.text or "" for element in paragraph.iter(f"{{{W}}}t")
    )


def test_final_validator_accepts_semantic_bookmark_and_ref():
    document = ET.Element(f"{{{W}}}document")
    body = ET.SubElement(document, f"{{{W}}}body")
    narrative = ET.SubElement(body, f"{{{W}}}p")
    instruction = ET.SubElement(
        ET.SubElement(narrative, f"{{{W}}}r"), f"{{{W}}}instrText"
    )
    instruction.text = " REF fig_arsitektur \\h "
    caption = ET.SubElement(body, f"{{{W}}}p")
    start = ET.SubElement(caption, f"{{{W}}}bookmarkStart")
    start.set(f"{{{W}}}id", "7")
    start.set(f"{{{W}}}name", "fig_arsitektur")
    caption_text = ET.SubElement(
        ET.SubElement(caption, f"{{{W}}}r"), f"{{{W}}}t"
    )
    caption_text.text = "Gambar 2.1 Arsitektur Sistem"
    seq = ET.SubElement(ET.SubElement(caption, f"{{{W}}}r"), f"{{{W}}}instrText")
    seq.text = " SEQ Gambar \\r 1 \\* ARABIC "
    end = ET.SubElement(caption, f"{{{W}}}bookmarkEnd")
    end.set(f"{{{W}}}id", "7")

    assert validator.validate_semantic_cross_references(document) == []


def test_writing_workflow_preserves_semantic_ids_without_renumbering():
    markdown = (
        "# BAB II RANCANGAN\n\n"
        "Susunan ditampilkan pada [FIGREF:arsitektur].\n\n"
        "[FIGURE:arsitektur]\n"
        "[FIGCAPTION:Arsitektur Sistem]\n\n"
        "Rincian ditampilkan pada [TABREF:komponen].\n\n"
        "[TABLE-ID:komponen]\n"
        "[TABLECAPTION:Komponen Sistem]\n"
        "[TABLE]\nA | B\n1 | 2\n[/TABLE]\n"
    )

    numbered, findings = number_objects(DraftModel.from_markdown(markdown))

    assert numbered.to_markdown() == markdown
    assert findings == []


def test_table_html_breaks_become_word_line_breaks():
    paragraph = LET.Element(f"{{{W}}}p")

    mrg.add_table_cell_formatted_text(
        paragraph, "1. Langkah pertama.<br>2. Langkah kedua.<br/>3. Selesai."
    )

    assert "".join(
        element.text or "" for element in paragraph.iter(f"{{{W}}}t")
    ) == "1. Langkah pertama.2. Langkah kedua.3. Selesai."
    assert len(list(paragraph.iter(f"{{{W}}}br"))) == 2
    assert "<br" not in LET.tostring(paragraph, encoding="unicode")


def test_explicit_page_break_paragraph_survives_as_own_block():
    paragraph = fmt.make_explicit_page_break_paragraph(NS)

    page_break = paragraph.find(".//w:br", NS)
    assert page_break is not None
    assert page_break.get(f"{{{W}}}type") == "page"
    assert paragraph.find("w:pPr/w:pStyle", NS).get(f"{{{W}}}val") == "Normal"
