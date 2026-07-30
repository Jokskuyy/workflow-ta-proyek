"""Regression tests for report-wide technical typography requirements."""

import importlib.util
import json
import os
import re
import sys
import zipfile
from pathlib import Path

import lxml.etree


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


mrg = _load_module("merge_draft_typography", SCRIPTS / "merge_draft_to_docx.py")
fmt = _load_module("format_ta_typography", SCRIPTS / "format_ta_proyek.py")
inj = _load_module("inject_images_typography", SCRIPTS / "inject_all_images.py")
build = _load_module("build_pipeline_typography", SCRIPTS / "build_pipeline.py")


def _run_properties(run):
    return run.find("w:rPr", NS)


def _text(run):
    return "".join(node.text or "" for node in run.findall("w:t", NS))


def _is_on(properties, name):
    element = properties.find(f"w:{name}", NS)
    return element is not None and element.get(f"{{{W}}}val", "1") not in {
        "0", "false", "off",
    }


def test_registry_terms_and_inline_code_render_times_italic():
    paragraph = lxml.etree.Element(f"{{{W}}}p")
    mrg.add_formatted_text(
        paragraph,
        "Backend dan Black Box Testing memakai `GET /api/health`.",
    )

    expected_italic = {"Backend", "Black Box Testing", "GET /api/health"}
    observed = {}
    for run in paragraph.findall("w:r", NS):
        text = "".join(node.text or "" for node in run.findall("w:t", NS))
        if text not in expected_italic:
            continue
        properties = _run_properties(run)
        fonts = properties.find("w:rFonts", NS)
        observed[text] = {
            "italic": properties.find("w:i", NS) is not None,
            "italic_cs": properties.find("w:iCs", NS) is not None,
            "ascii": fonts.get(f"{{{W}}}ascii"),
            "hansi": fonts.get(f"{{{W}}}hAnsi"),
            "size": properties.find("w:sz", NS).get(f"{{{W}}}val"),
        }

    assert observed.keys() == expected_italic
    assert all(values["italic"] and values["italic_cs"] for values in observed.values())
    assert all(values["ascii"] == "Times New Roman" for values in observed.values())
    assert all(values["hansi"] == "Times New Roman" for values in observed.values())
    assert all(values["size"] == "24" for values in observed.values())


def test_fenced_code_block_uses_courier_new_italic():
    paragraphs = mrg.build_code_block_elements({"lines": ["const status = true;"]})
    assert len(paragraphs) == 1
    properties = paragraphs[0].find("w:r/w:rPr", NS)
    fonts = properties.find("w:rFonts", NS)

    assert {
        fonts.get(f"{{{W}}}ascii"),
        fonts.get(f"{{{W}}}hAnsi"),
        fonts.get(f"{{{W}}}eastAsia"),
        fonts.get(f"{{{W}}}cs"),
    } == {"Courier New"}
    assert properties.find("w:i", NS) is not None
    assert properties.find("w:iCs", NS) is not None
    assert properties.find("w:sz", NS).get(f"{{{W}}}val") == "24"
    paragraph_properties = paragraphs[0].find("w:pPr", NS)
    spacing = paragraph_properties.find("w:spacing", NS)
    assert spacing.get(f"{{{W}}}line") == "240"
    assert spacing.get(f"{{{W}}}lineRule") == "auto"
    assert paragraph_properties.find("w:shd", NS) is None
    assert paragraph_properties.find("w:pBdr", NS) is None


def test_caption_style_is_explicit_times_new_roman_body_style():
    styles = lxml.etree.Element(f"{{{W}}}styles")
    style = fmt.ensure_caption_style(styles)

    assert style.find("w:basedOn", NS).get(f"{{{W}}}val") == "Normal"
    paragraph_properties = style.find("w:pPr", NS)
    assert paragraph_properties.find("w:jc", NS).get(f"{{{W}}}val") == "center"
    spacing = paragraph_properties.find("w:spacing", NS)
    assert spacing.get(f"{{{W}}}line") == "240"
    assert spacing.get(f"{{{W}}}lineRule") == "auto"
    indent = paragraph_properties.find("w:ind", NS)
    assert indent.get(f"{{{W}}}firstLine") == "0"
    assert indent.get(f"{{{W}}}left") == "0"

    run_properties = style.find("w:rPr", NS)
    fonts = run_properties.find("w:rFonts", NS)
    assert {
        fonts.get(f"{{{W}}}{name}")
        for name in ("ascii", "hAnsi", "eastAsia", "cs")
    } == {"Times New Roman"}
    assert run_properties.find("w:sz", NS).get(f"{{{W}}}val") == "24"
    assert run_properties.find("w:color", NS).get(f"{{{W}}}val") == "000000"
    assert not _is_on(run_properties, "b")
    assert not _is_on(run_properties, "i")


def test_caption_number_is_bold_and_description_is_regular():
    paragraph = lxml.etree.fromstring(
        f'<w:p xmlns:w="{W}"><w:pPr/></w:p>'
    )
    fmt.format_caption_paragraph_clean(
        paragraph,
        "Gambar",
        "2.",
        "Gambar",
        "1",
        "Deskripsi regular",
        NS,
    )

    runs = paragraph.findall("w:r", NS)
    field_result = next(
        run for run in runs if _text(run) == "1"
    )
    description = next(
        run for run in runs if "Deskripsi regular" in _text(run)
    )
    for run in (runs[0], field_result):
        properties = _run_properties(run)
        assert _is_on(properties, "b")
        assert not _is_on(properties, "i")
        assert properties.find("w:sz", NS).get(f"{{{W}}}val") == "24"
    description_properties = _run_properties(description)
    assert not _is_on(description_properties, "b")
    assert not _is_on(description_properties, "i")


def test_post_com_caption_italics_only_selected_term_span():
    document = lxml.etree.fromstring(
        f"""<w:document xmlns:w="{W}"><w:body><w:p>
        <w:pPr><w:pStyle w:val="Caption"/></w:pPr>
        <w:r><w:t xml:space="preserve">Gambar 3.</w:t></w:r>
        <w:r><w:fldChar w:fldCharType="begin"/></w:r>
        <w:r><w:instrText> SEQ Gambar \\* ARABIC </w:instrText></w:r>
        <w:r><w:fldChar w:fldCharType="separate"/></w:r>
        <w:r><w:t>4</w:t></w:r>
        <w:r><w:fldChar w:fldCharType="end"/></w:r>
        <w:r><w:t xml:space="preserve"> Hasil Black Box Testing aplikasi</w:t></w:r>
        </w:p></w:body></w:document>"""
    )

    assert inj.normalize_caption_typography(document) == 1
    assert inj.apply_post_com_technical_italics(
        document, ("Black Box Testing",)
    ) == 1

    runs = document.findall(".//w:p/w:r", NS)
    number_run = next(run for run in runs if _text(run) == "4")
    term_run = next(run for run in runs if _text(run) == "Black Box Testing")
    ordinary_runs = [
        run for run in runs
        if _text(run).strip() in {"Hasil", "aplikasi"}
    ]
    assert _is_on(_run_properties(number_run), "b")
    assert not _is_on(_run_properties(number_run), "i")
    assert _is_on(_run_properties(term_run), "i")
    assert not _is_on(_run_properties(term_run), "b")
    assert ordinary_runs
    assert all(not _is_on(_run_properties(run), "i") for run in ordinary_runs)


def test_post_com_reference_result_remains_regular():
    document = lxml.etree.fromstring(
        f"""<w:document xmlns:w="{W}"><w:body><w:p>
        <w:r><w:t xml:space="preserve">Uraian pada </w:t></w:r>
        <w:r><w:fldChar w:fldCharType="begin"/></w:r>
        <w:r><w:instrText> REF fig_example \\h </w:instrText></w:r>
        <w:r><w:fldChar w:fldCharType="separate"/></w:r>
        <w:r><w:rPr><w:b/><w:bCs/><w:i/><w:iCs/></w:rPr><w:t>Gambar 2.1</w:t></w:r>
        <w:r><w:fldChar w:fldCharType="end"/></w:r>
        <w:r><w:t xml:space="preserve"> ditampilkan.</w:t></w:r>
        </w:p></w:body></w:document>"""
    )

    assert inj.normalize_reference_field_typography(document) == 1
    field_runs = document.findall(".//w:p/w:r", NS)[1:6]
    for run in field_runs:
        properties = _run_properties(run)
        assert not _is_on(properties, "b")
        assert not _is_on(properties, "i")
        for name in ("b", "bCs", "i", "iCs"):
            assert properties.find(f"w:{name}", NS).get(f"{{{W}}}val") == "0"
        assert properties.find("w:sz", NS).get(f"{{{W}}}val") == "24"


def test_semantic_reference_result_remains_regular():
    paragraph = lxml.etree.fromstring(
        f"""<w:p xmlns:w="{W}"><w:r><w:rPr><w:b/><w:i/></w:rPr>
        <w:t>Uraian [FIGREF:contoh] berlanjut.</w:t></w:r></w:p>"""
    )
    replaced, unresolved = fmt.replace_semantic_references_in_paragraph(
        paragraph,
        {("FIGREF", "contoh"): {
            "bookmark": "fig_contoh", "display": "Gambar 2.3"
        }},
        NS,
    )
    assert replaced == 1
    assert unresolved == []
    reference = next(
        run for run in paragraph.findall("w:r", NS)
        if _text(run) == "Gambar 2.3"
    )
    properties = _run_properties(reference)
    assert not _is_on(properties, "b")
    assert not _is_on(properties, "i")
    for name in ("b", "bCs", "i", "iCs"):
        element = properties.find(f"w:{name}", NS)
        assert element is not None
        assert element.get(f"{{{W}}}val") == "0"
    fonts = properties.find("w:rFonts", NS)
    assert fonts.get(f"{{{W}}}ascii") == "Times New Roman"
    assert properties.find("w:sz", NS).get(f"{{{W}}}val") == "24"


def test_font_normalizer_replaces_monospace_and_theme_fonts(tmp_path):
    document = tmp_path / "word" / "document.xml"
    document.parent.mkdir()
    document.write_text(
        f"""<?xml version="1.0" encoding="utf-8"?>
        <w:document xmlns:w="{W}">
          <w:body><w:p>
            <w:r><w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Consolas"/></w:rPr><w:t>code</w:t></w:r>
            <w:r><w:rPr><w:rFonts w:asciiTheme="minorHAnsi"/></w:rPr><w:t>theme</w:t></w:r>
            <w:r><w:rPr><w:rFonts w:ascii="Symbol"/></w:rPr><w:t>symbol</w:t></w:r>
          </w:p></w:body>
        </w:document>""",
        encoding="utf-8",
    )

    fmt.fix_all_fonts_lxml(str(tmp_path))
    root = lxml.etree.parse(str(document)).getroot()
    fonts = root.findall(".//w:rFonts", NS)

    assert fonts[0].get(f"{{{W}}}ascii") == "Times New Roman"
    assert fonts[0].get(f"{{{W}}}hAnsi") == "Times New Roman"
    assert fonts[1].get(f"{{{W}}}ascii") == "Times New Roman"
    assert fonts[1].get(f"{{{W}}}asciiTheme") is None
    assert fonts[2].get(f"{{{W}}}ascii") == "Symbol"


def test_font_normalizer_preserves_courier_new_only_for_code_blocks(tmp_path):
    document = tmp_path / "word" / "document.xml"
    document.parent.mkdir()
    document.write_text(
        f"""<?xml version="1.0" encoding="utf-8"?>
        <w:document xmlns:w="{W}"><w:body>
          <w:p><w:pPr><w:pStyle w:val="CodeBlock"/></w:pPr>
            <w:r><w:rPr><w:rFonts w:ascii="Times New Roman"/></w:rPr><w:t>code</w:t></w:r>
          </w:p>
          <w:p><w:r><w:rPr><w:rFonts w:ascii="Courier New"/></w:rPr><w:t>body</w:t></w:r></w:p>
        </w:body></w:document>""",
        encoding="utf-8",
    )

    fmt.fix_all_fonts_lxml(str(tmp_path))
    root = lxml.etree.parse(str(document)).getroot()
    paragraphs = root.findall(".//w:p", NS)
    assert paragraphs[0].find(".//w:rFonts", NS).get(f"{{{W}}}ascii") == "Courier New"
    assert paragraphs[1].find(".//w:rFonts", NS).get(f"{{{W}}}ascii") == "Times New Roman"


def test_post_com_pass_restores_generated_technical_italics():
    document = lxml.etree.fromstring(
        f"""<w:document xmlns:w="{W}"><w:body><w:p>
        <w:r><w:t>Black Box Testing</w:t></w:r>
        <w:r><w:t>kalimat umum</w:t></w:r>
        </w:p></w:body></w:document>"""
    )

    changed = inj.apply_post_com_technical_italics(document, ("Black Box Testing",))
    runs = document.findall(".//w:r", NS)

    assert changed == 1
    assert runs[0].find("w:rPr/w:i", NS) is not None
    assert runs[0].find("w:rPr/w:iCs", NS) is not None
    assert runs[1].find("w:rPr", NS) is None


def test_post_com_pass_keeps_report_title_regular():
    title = (
        "Pengembangan Dashboard Web, Integrasi Unity WebGL, dan Deployment "
        "Sistem Denah Virtual UPNVJ Kampus Pondok Labu"
    )
    document = lxml.etree.fromstring(
        f"""<w:document xmlns:w="{W}"><w:body>
        <w:p><w:r><w:t>{title}</w:t></w:r></w:p>
        <w:p><w:pPr><w:pageBreakBefore/></w:pPr>
          <w:r><w:t>Deployment berikutnya.</w:t></w:r></w:p>
        </w:body></w:document>"""
    )

    assert inj.cover_report_title(document) == title
    changed = inj.apply_post_com_technical_italics(
        document,
        ("deployment",),
        protected_phrases=(title,),
    )
    paragraphs = document.findall(".//w:p", NS)

    assert changed == 1
    assert all(
        not _is_on(_run_properties(run), "i")
        for run in paragraphs[0].findall("w:r", NS)
    )
    assert _is_on(
        _run_properties(paragraphs[1].find("w:r", NS)),
        "i",
    )


def test_post_com_pass_does_not_override_code_block_font():
    document = lxml.etree.fromstring(
        f"""<w:document xmlns:w="{W}"><w:body>
        <w:p><w:pPr><w:pStyle w:val="CodeBlock"/></w:pPr>
          <w:r><w:rPr>
            <w:rFonts w:ascii="Courier New" w:hAnsi="Courier New"/>
            <w:i/><w:iCs/>
          </w:rPr><w:t>deployment</w:t></w:r>
        </w:p>
        </w:body></w:document>"""
    )

    changed = inj.apply_post_com_technical_italics(
        document, ("deployment",)
    )
    properties = document.find(".//w:r/w:rPr", NS)
    fonts = properties.find("w:rFonts", NS)

    assert changed == 0
    assert fonts.get(f"{{{W}}}ascii") == "Courier New"
    assert fonts.get(f"{{{W}}}hAnsi") == "Courier New"
    assert _is_on(properties, "i")
    assert _is_on(properties, "iCs")


def test_post_com_pass_restores_front_matter_style_and_abstract_runs():
    document = lxml.etree.fromstring(
        f"""<w:document xmlns:w="{W}"><w:body>
        <w:p><w:pPr><w:pStyle w:val="frontmatterheading"/></w:pPr>
          <w:r><w:t>ABSTRAK</w:t></w:r></w:p>
        <w:p><w:r><w:t>Isi abstrak Indonesia.</w:t></w:r></w:p>
        <w:p><w:r><w:t>Kata kunci:</w:t></w:r>
          <w:r><w:t xml:space="preserve"> denah virtual</w:t></w:r></w:p>
        <w:p><w:pPr><w:pStyle w:val="frontmatterheading"/></w:pPr>
          <w:r><w:t>ABSTRACT</w:t></w:r></w:p>
        <w:p><w:r><w:t>English abstract body.</w:t></w:r></w:p>
        <w:p><w:r><w:t>Keywords:</w:t></w:r>
          <w:r><w:t xml:space="preserve"> virtual map</w:t></w:r></w:p>
        </w:body></w:document>"""
    )
    styles = lxml.etree.fromstring(
        f"""<w:styles xmlns:w="{W}">
        <w:style w:type="paragraph" w:styleId="frontmatterheading">
          <w:name w:val="front matter heading"/>
        </w:style></w:styles>"""
    )

    result = inj.restore_front_matter_after_com(document, styles)

    style = styles.find(
        "w:style[@w:styleId='FrontMatterHeading']", NS
    )
    assert style is not None
    assert style.find("w:basedOn", NS).get(f"{{{W}}}val") == "Normal"
    style_run_properties = style.find("w:rPr", NS)
    assert style_run_properties.find("w:rFonts", NS).get(
        f"{{{W}}}ascii"
    ) == "Times New Roman"
    assert style_run_properties.find("w:sz", NS).get(f"{{{W}}}val") == "24"
    assert _is_on(style_run_properties, "b")

    paragraph_styles = document.findall(".//w:pPr/w:pStyle", NS)
    assert {
        item.get(f"{{{W}}}val") for item in paragraph_styles
    } == {"FrontMatterHeading"}

    paragraphs = document.findall(".//w:p", NS)
    for paragraph_index in (1, 4):
        for run in paragraphs[paragraph_index].findall("w:r", NS):
            properties = run.find("w:rPr", NS)
            assert properties.find("w:rFonts", NS).get(
                f"{{{W}}}ascii"
            ) == "Times New Roman"
            assert properties.find("w:sz", NS).get(f"{{{W}}}val") == "24"
            assert not _is_on(properties, "b")

    for paragraph_index in (2, 5):
        runs = paragraphs[paragraph_index].findall("w:r", NS)
        assert _is_on(runs[0].find("w:rPr", NS), "b")
        assert not _is_on(runs[1].find("w:rPr", NS), "b")

    assert result == {
        "paragraph_styles": 2,
        "runs": 6,
        "preface": {
            "opening": 0,
            "acknowledgements": 0,
            "closing": 0,
            "signoff": 0,
        },
    }


def test_post_com_pass_restores_preface_indentation_groups():
    document = lxml.etree.Element(f"{{{W}}}document", nsmap={"w": W})
    body = lxml.etree.SubElement(document, f"{{{W}}}body")

    def add_paragraph(text, *, hanging=False, align=None):
        paragraph = lxml.etree.SubElement(body, f"{{{W}}}p")
        properties = lxml.etree.SubElement(paragraph, f"{{{W}}}pPr")
        if hanging:
            lxml.etree.SubElement(
                properties,
                f"{{{W}}}ind",
                {
                    f"{{{W}}}left": "567",
                    f"{{{W}}}hanging": "360",
                },
            )
        if align:
            lxml.etree.SubElement(
                properties, f"{{{W}}}jc", {f"{{{W}}}val": align}
            )
        run = lxml.etree.SubElement(paragraph, f"{{{W}}}r")
        lxml.etree.SubElement(run, f"{{{W}}}t").text = text
        return paragraph

    add_paragraph("KATA PENGANTAR")
    opening = [add_paragraph("Pembuka pertama."), add_paragraph("Pembuka kedua.")]
    acknowledgements = [
        add_paragraph(f"{index}. Ucapan terima kasih {index}.", hanging=True)
        for index in range(1, 9)
    ]
    closing = [add_paragraph("Penutup kata pengantar.")]
    signoff = [
        add_paragraph("Jakarta, 23 Juli 2026", align="left"),
        add_paragraph("Muhammad Iman Nugraha", align="left"),
        add_paragraph("2210511129", align="left"),
    ]
    add_paragraph("DAFTAR ISI")
    styles = lxml.etree.Element(f"{{{W}}}styles", nsmap={"w": W})

    result = inj.restore_front_matter_after_com(document, styles)

    assert result["preface"] == {
        "opening": 2,
        "acknowledgements": 8,
        "closing": 1,
        "signoff": 3,
    }
    for paragraph in opening + closing:
        indent = paragraph.find("w:pPr/w:ind", NS)
        assert indent.attrib == {
            f"{{{W}}}left": "0",
            f"{{{W}}}firstLine": "567",
        }
    for paragraph in acknowledgements + signoff:
        indent = paragraph.find("w:pPr/w:ind", NS)
        assert indent.attrib == {
            f"{{{W}}}left": "0",
            f"{{{W}}}firstLine": "0",
        }
    for paragraph in signoff:
        assert paragraph.find("w:pPr/w:jc", NS).get(f"{{{W}}}val") == "right"


def test_active_report_has_registry_terms_and_no_visible_hash_source():
    registry = json.loads((ROOT / "term_registry.json").read_text(encoding="utf-8"))
    assert registry["italic_terms"]

    paths = [ROOT / "Tugas_Akhir_Draft.md"]
    paths.extend((ROOT / "content" / "shared").rglob("*.md"))
    hashes = {
        "08ebc06", "b572a48", "d2e8fdb", "1845c65", "d30f7d1", "bdeb5bc",
    }
    hash_offenders = []
    bold_offenders = []
    for path in paths:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if any(value in line for value in hashes):
                hash_offenders.append(f"{path.relative_to(ROOT)}:{line_number}")
            if "**" in line:
                bold_offenders.append(f"{path.relative_to(ROOT)}:{line_number}")

    assert hash_offenders == []
    assert bold_offenders == []


def test_active_report_uses_clear_uml_and_data_mapping_terms():
    draft = (ROOT / "Tugas_Akhir_Draft.md").read_text(encoding="utf-8")
    manifest = json.loads(
        (ROOT / "images" / "manifest.json").read_text(encoding="utf-8")
    )
    captions = {entry["caption_match"] for entry in manifest["images"]}

    assert "2. Activity Diagram" in draft
    assert "3. Sequence Diagram" in draft
    assert "Diagram Aktivitas" not in draft
    assert "Diagram Urutan" not in draft
    assert "Squence Diagram" not in draft
    assert "Perancangan Pemetaan Data Integrasi" in draft
    assert "Pemetaan Data yang Digunakan Aplikasi dan API" in draft
    assert "Activity Diagram Integrasi Denah 2D dan 3D" in captions
    assert "Sequence Diagram Autentikasi Administrator" in captions

    table = draft.split("[TABLE-ID:kontrak_data_integrasi]", 1)[1].split(
        "[/TABLE]", 1
    )[0]
    assert "`" not in table


def test_build_pipeline_supports_non_destructive_output_path():
    assert build.parse_args([]).profile == "iman"
    assert build.parse_args([]).output is None
    assert build.load_profile("iman")["output"] == "Tugas_Akhir_Formatted.docx"
    assert build.parse_args(["--output", "scratch/qa.docx"]).output == "scratch/qa.docx"


def test_final_docx_has_no_visible_hash_or_non_times_text_fonts():
    configured_output = os.environ.get("TA_DOCX_PATH")
    if not configured_output:
        import pytest
        pytest.skip("Set TA_DOCX_PATH after a fresh build to inspect the final package.")
    output = Path(configured_output)
    assert output.is_file(), output

    visible_hashes = []
    forbidden_fonts = []
    visible_non_times_fonts = []
    technical_runs = 0
    italic_technical_runs = 0
    nonitalic_technical_runs = []
    reference_result_runs = []
    configured = {
        term.casefold()
        for term in json.loads((ROOT / "term_registry.json").read_text(encoding="utf-8"))["italic_terms"]
    }
    allowed_fonts = {"Times New Roman", "Courier New", "Symbol", "Wingdings", ""}

    known_hashes = {
        "08ebc06", "b572a48", "d2e8fdb", "1845c65", "d30f7d1", "bdeb5bc",
    }
    with zipfile.ZipFile(output) as package:
        for name in package.namelist():
            if not name.startswith("word/") or not name.endswith(".xml"):
                continue
            root = lxml.etree.fromstring(package.read(name))
            for text_node in root.findall(".//w:t", NS):
                text = text_node.text or ""
                if any(value in text for value in known_hashes):
                    visible_hashes.append(f"{name}: {text}")
            for fonts in root.findall(".//w:rFonts", NS):
                for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
                    value = fonts.get(f"{{{W}}}{attr}", "")
                    if value not in allowed_fonts:
                        forbidden_fonts.append(f"{name}: {attr}={value}")
            for run in root.findall(".//w:r", NS):
                text = "".join(node.text or "" for node in run.findall("w:t", NS))
                if text:
                    properties = run.find("w:rPr", NS)
                    fonts = properties.find("w:rFonts", NS) if properties is not None else None
                    if fonts is not None:
                        for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
                            value = fonts.get(f"{{{W}}}{attr}", "")
                            paragraph = run
                            while paragraph is not None and paragraph.tag != f"{{{W}}}p":
                                paragraph = paragraph.getparent()
                            paragraph_style = (
                                paragraph.find("w:pPr/w:pStyle", NS)
                                if paragraph is not None else None
                            )
                            is_code = (
                                paragraph_style is not None
                                and paragraph_style.get(f"{{{W}}}val") == "CodeBlock"
                            )
                            expected_font = "Courier New" if is_code else "Times New Roman"
                            if value and value != expected_font:
                                visible_non_times_fonts.append(
                                    f"{name}: {text!r} {attr}={value}; expected {expected_font}"
                                )
                if text.casefold() not in configured:
                    continue
                technical_runs += 1
                properties = run.find("w:rPr", NS)
                if properties is not None and properties.find("w:i", NS) is not None:
                    italic_technical_runs += 1
                else:
                    nonitalic_technical_runs.append(f"{name}: {text}")

            if name == "word/document.xml":
                for paragraph in root.findall(".//w:p", NS):
                    instruction = "".join(
                        node.text or ""
                        for node in paragraph.findall(".//w:instrText", NS)
                    )
                    if " REF " not in instruction:
                        continue
                    in_result = False
                    for run in paragraph.findall("w:r", NS):
                        field = run.find("w:fldChar", NS)
                        if field is not None:
                            kind = field.get(f"{{{W}}}fldCharType")
                            if kind == "separate":
                                in_result = True
                            elif kind == "end":
                                in_result = False
                            continue
                        result_text = "".join(
                            node.text or "" for node in run.findall("w:t", NS)
                        )
                        if not in_result or not result_text:
                            continue
                        properties = run.find("w:rPr", NS)
                        reference_result_runs.append(result_text)
                        for prop_name in ("b", "bCs", "i", "iCs"):
                            element = properties.find(f"w:{prop_name}", NS)
                            assert element is not None
                            assert element.get(f"{{{W}}}val") == "0"

    assert visible_hashes == []
    assert forbidden_fonts == []
    assert visible_non_times_fonts == []
    assert technical_runs > 0
    assert nonitalic_technical_runs == []
    assert italic_technical_runs == technical_runs
    assert reference_result_runs
