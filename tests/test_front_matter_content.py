"""Regression guards for Iman's role-specific front matter."""

import json
import importlib.util
import os
import re
import sys
import zipfile
from pathlib import Path

import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content" / "roles" / "iman" / "front-matter.json"
DRAFT = ROOT / "Tugas_Akhir_Draft.md"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
WP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"


def _load():
    return json.loads(SOURCE.read_text(encoding="utf-8"))


def _load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_front_matter_test",
        ROOT / "skills" / "scripts" / "validate_docx_structure.py",
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_patcher():
    spec = importlib.util.spec_from_file_location(
        "patch_front_matter_test",
        ROOT / "skills" / "scripts" / "patch_template.py",
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _word_count(text):
    return len(re.findall(r"\b[\w’'-]+\b", text, flags=re.UNICODE))


def test_front_matter_has_required_order_and_identity():
    data = _load()
    assert list(data) == [
        "cover",
        "report_title_page",
        "approval_page",
        "authenticity_statement",
        "publication_permission",
        "abstract_id",
        "abstract_en",
        "preface",
        "identity_footer",
    ]
    title = (
        "Pengembangan Dashboard Web, Integrasi Unity WebGL, dan Deployment "
        "Sistem Denah Virtual UPNVJ Kampus Pondok Labu"
    )
    assert data["cover"] == {
        "title": title,
        "author": "Muhammad Iman Nugraha",
        "nim": "2210511129",
        "year": "2026",
    }
    assert title in data["preface"]["opening"][0]
    assert data["publication_permission"]["date"] == "Jakarta, 24 Juli 2026"
    assert data["preface"]["date"] == "Jakarta, 24 Juli 2026"
    title_page = data["report_title_page"]
    assert title_page == {
        "heading": "LAPORAN PROYEK",
        "title": title,
        "author": "MUHAMMAD IMAN NUGRAHA",
        "nim": "2210511129",
        "program_study": "S1 INFORMATIKA",
        "faculty": "FAKULTAS ILMU KOMPUTER",
        "university": (
            "UNIVERSITAS PEMBANGUNAN NASIONAL “VETERAN” JAKARTA"
        ),
        "city": "JAKARTA",
        "year": "2026",
    }
    authenticity = data["authenticity_statement"]
    assert authenticity["heading"] == "SURAT PERNYATAAN KEASLIAN"
    assert authenticity["identity"] == {
        "Nama": "Muhammad Iman Nugraha",
        "NIM": "2210511129",
        "Program Studi": "S-1 Informatika",
        "Judul Proyek": title,
    }
    assert authenticity["date"] == "Jakarta, 24 Juli 2026"
    assert authenticity["declarant_label"] == "Yang menyatakan,"
    assert authenticity["signature_space_lines"] == 3
    assert authenticity["author"] == "Muhammad Iman Nugraha"
    assert authenticity["requires_physical_stamp"] is True
    assert authenticity["scan"]["embedded_page_number"] == "iv"
    assert "hasil kolaborasi tim" in authenticity["paragraphs"][0]
    assert "aturan serta ketentuan yang berlaku" in authenticity["paragraphs"][1]
    approval = data["approval_page"]
    assert approval["heading"] == "LEMBAR PENGESAHAN"
    assert approval["identity"]["Judul"] == title
    assert approval["identity"]["Nama"] == "Muhammad Iman Nugraha"
    assert approval["identity"]["NIM"] == "2210511129"
    assert approval["identity"]["Program Studi"] == "S1 Informatika"
    assert [item["role"] for item in approval["approved_by"]] == [
        "Penguji 1",
        "Penguji 2",
        "Pembimbing 1",
        "Pembimbing 2",
    ]
    assert approval["exam_date"] == "24 Juli 2026"
    assert approval["scan"]["embedded_page_number"] == "iii"
    publication = data["publication_permission"]
    assert publication["heading"] == (
        "PERNYATAAN PERSETUJUAN PUBLIKASI TUGAS AKHIR UNTUK "
        "KEPENTINGAN AKADEMIK"
    )
    assert publication["blank_identity_labels"] == [
        "Nama",
        "NIM",
        "Program Studi",
        "Fakultas",
    ]
    assert publication["title_blank_lines"] == 3
    assert publication["signature_space_lines"] == 3
    assert publication["scan"]["embedded_page_number"] == "v"
    for block in (approval, authenticity, publication):
        scan_path = ROOT / block["scan"]["image"]
        assert scan_path.is_file()
        assert scan_path.suffix.lower() == ".jpeg"
        assert block["scan"]["width_cm"] == 14.0
    assert "signature" not in data["preface"]
    assert "signature" not in authenticity
    assert "signature" not in publication
    assert data["identity_footer"] == {
        "author_year": "Muhammad Iman Nugraha, 2026",
        "title": title.upper(),
        "institution": (
            "UPN Veteran Jakarta, Fakultas Ilmu Komputer, S1 Informatika"
        ),
        "links": (
            "[www.upnvj.ac.id-www.library.upnvj.ac.id-"
            "www.repository.upnvj.ac.id]"
        ),
        "font": "Times New Roman",
        "size_pt": 8,
        "start": "BAB I",
        "end": "DAFTAR PUSTAKA",
    }


def test_report_title_source_uses_regular_title_case():
    title = _load()["cover"]["title"]
    first_line = DRAFT.read_text(encoding="utf-8").splitlines()[0]

    assert first_line == f"# {title}"
    assert title != title.upper()
    assert not re.search(r"(?<!\\)(?:\*|_)", first_line)


def test_abstracts_meet_length_labels_and_verified_results():
    data = _load()
    assert 200 <= _word_count(data["abstract_id"]["body"]) <= 250
    assert 200 <= _word_count(data["abstract_en"]["body"]) <= 250
    assert data["abstract_id"]["keywords_label"] == "Kata kunci:"
    assert data["abstract_en"]["keywords_label"] == "Keywords:"

    combined = data["abstract_id"]["body"] + " " + data["abstract_en"]["body"]
    for fact in ("129", "13", "24", "81,50", "86", "99", "100"):
        assert fact in combined
    assert "lima peserta" in data["abstract_id"]["body"]
    assert "five participants" in data["abstract_en"]["body"]


def test_preface_acknowledgements_are_complete_and_ordered():
    preface = _load()["preface"]
    acknowledgements = preface["acknowledgements"]
    assert len(acknowledgements) == 8
    expected_tokens = [
        ("Mamah", "Bapak"),
        ("Erly Krisnanik",),
        ("Ridwan Raafi’udin", "Novi Trisman Hadi"),
        ("Mochamad Fariz Satyawan", "Staf Program Studi", "pelaksanaan sidang"),
        ("Muhammad Dwikhi", "Muammar Faiz Khairul Anam Setiawan"),
        ("NYPD", "Dimari Aje Cuyy", "mtgim", "Semua Baik", "whychucksaysnah", "marqui de natra666"),
        ("Seluruh pihak",),
        ("diri sendiri",),
    ]
    for paragraph, tokens in zip(acknowledgements, expected_tokens):
        assert all(token in paragraph for token in tokens)


def test_appendices_start_after_front_matter_and_are_sequential():
    draft = DRAFT.read_text(encoding="utf-8")
    headings = re.findall(r"^# LAMPIRAN (\d+)\. (.+)$", draft, flags=re.MULTILINE)
    assert [int(number) for number, _ in headings] == list(range(1, 7))
    assert "Surat Pernyataan Keaslian" not in draft
    assert headings[0][1] == "Dokumentasi Penyerahan Pakta Integritas kepada UPA TIK"


def test_front_matter_builder_reserves_stamp_space_without_blank_toc_page():
    patcher = _load_patcher()
    elements = patcher._build_front_matter(_load())
    texts = [
        "".join(node.text or "" for node in element.findall(f".//{{{W_NS}}}t"))
        for element in elements
    ]

    declarant = elements[texts.index("Yang menyatakan,")]
    spacing = declarant.find(f"{{{W_NS}}}pPr/{{{W_NS}}}spacing")
    assert spacing is not None
    assert spacing.get(f"{{{W_NS}}}after") == "720"

    assert texts[-2:] == ["Muhammad Iman Nugraha", "2210511129"]
    assert not any(
        not text
        and element.find(
            f"{{{W_NS}}}pPr/{{{W_NS}}}pageBreakBefore"
        ) is not None
        for element, text in zip(elements, texts)
    )


def test_preface_only_acknowledgements_are_flush_left():
    patcher = _load_patcher()
    config = _load()
    elements = patcher._build_front_matter(config)
    opening_texts = set(config["preface"]["opening"])
    closing_texts = set(config["preface"]["closing"])
    acknowledgement_texts = {
        f"{index}. {text}"
        for index, text in enumerate(
            config["preface"]["acknowledgements"], start=1
        )
    }
    preface_body = {}
    for element in elements:
        text = "".join(
            node.text or "" for node in element.findall(f".//{{{W_NS}}}t")
        )
        if text in opening_texts | closing_texts | acknowledgement_texts:
            preface_body[text] = element

    assert len(preface_body) == 11
    for text in opening_texts | closing_texts:
        paragraph = preface_body[text]
        indent = paragraph.find(f"{{{W_NS}}}pPr/{{{W_NS}}}ind")
        assert indent is not None
        assert indent.get(f"{{{W_NS}}}left") == "0"
        assert indent.get(f"{{{W_NS}}}firstLine") == "567"
        assert indent.get(f"{{{W_NS}}}hanging") is None

    for text in acknowledgement_texts:
        paragraph = preface_body[text]
        indent = paragraph.find(f"{{{W_NS}}}pPr/{{{W_NS}}}ind")
        assert indent is not None
        assert indent.get(f"{{{W_NS}}}left") == "0"
        assert indent.get(f"{{{W_NS}}}firstLine") == "0"
        assert indent.get(f"{{{W_NS}}}hanging") is None


def test_signed_scan_builder_replaces_the_three_editable_pages():
    patcher = _load_patcher()
    scan_names = {
        "approval": "FRONT_MATTER_SCAN:iman:approval",
        "authenticity": "FRONT_MATTER_SCAN:iman:authenticity",
        "publication": "FRONT_MATTER_SCAN:iman:publication",
    }
    scans = {
        key: patcher._front_image_drawing_paragraph(
            f"rId{index}",
            index,
            5_040_000,
            7_900_000,
            {"l": "0", "t": "0", "r": "0", "b": "0"},
            f"{key} signed scan",
            name,
            align="center",
            keep_next=False,
        )
        for index, (key, name) in enumerate(scan_names.items(), start=1)
    }
    elements = patcher._build_front_matter(
        _load(),
        front_matter_scans=scans,
    )

    names = [
        drawing.get("name")
        for element in elements
        for drawing in element.findall(f".//{{{WP_NS}}}docPr")
    ]
    assert names == list(scan_names.values())
    assert not any(
        element.tag == f"{{{W_NS}}}tbl"
        and element.find(
            f"{{{W_NS}}}tblPr/{{{W_NS}}}tblCaption"
        ) is not None
        for element in elements
    )
    for key, heading in (
        ("approval", "LEMBAR PENGESAHAN"),
        ("authenticity", "SURAT PERNYATAAN KEASLIAN"),
        (
            "publication",
            "PERNYATAAN PERSETUJUAN PUBLIKASI TUGAS AKHIR "
            "UNTUK KEPENTINGAN AKADEMIK",
        ),
    ):
        scan_paragraph = scans[key]
        scan_index = elements.index(scan_paragraph)
        paragraph = elements[scan_index - 1]
        hidden = next(
            run for run in paragraph.findall(f"{{{W_NS}}}r")
            if "".join(run.itertext()) == heading
        )
        color = hidden.find(f"{{{W_NS}}}rPr/{{{W_NS}}}color")
        size = hidden.find(f"{{{W_NS}}}rPr/{{{W_NS}}}sz")
        assert color is not None
        assert color.get(f"{{{W_NS}}}val") == "FFFFFF"
        assert size is not None
        assert size.get(f"{{{W_NS}}}val") == "2"
        style = paragraph.find(
            f"{{{W_NS}}}pPr/{{{W_NS}}}pStyle"
        )
        assert style is not None
        assert style.get(f"{{{W_NS}}}val") == "FrontMatterHeading"


def test_front_matter_validator_requires_editable_approval_table():
    document = ET.Element(f"{{{W_NS}}}document")
    body = ET.SubElement(document, f"{{{W_NS}}}body")
    patcher = _load_patcher()
    for element in patcher._build_front_matter(_load()):
        body.append(ET.fromstring(patcher.lxml.etree.tostring(element)))
    toc = ET.SubElement(body, f"{{{W_NS}}}p")
    toc_run = ET.SubElement(toc, f"{{{W_NS}}}r")
    ET.SubElement(toc_run, f"{{{W_NS}}}t").text = "DAFTAR ISI"

    styles = ET.Element(f"{{{W_NS}}}styles")
    validator = _load_validator()
    findings = validator.validate_iman_front_matter(document, styles)
    approval_findings = [
        finding for finding in findings
        if "editable approval table" in finding
        or "publication permission" in finding
        or "obsolete front-matter drawing" in finding
    ]
    assert approval_findings == []

    toc_headings = {
        "LAPORAN PROYEK",
        "LEMBAR PENGESAHAN",
        "SURAT PERNYATAAN KEASLIAN",
        (
            "PERNYATAAN PERSETUJUAN PUBLIKASI TUGAS AKHIR UNTUK "
            "KEPENTINGAN AKADEMIK"
        ),
        "ABSTRAK",
        "ABSTRACT",
        "KATA PENGANTAR",
    }
    for paragraph in body.findall(f"{{{W_NS}}}p"):
        text = "".join(paragraph.itertext()).strip()
        if text not in toc_headings:
            continue
        style = paragraph.find(f"{{{W_NS}}}pPr/{{{W_NS}}}pStyle")
        assert style is not None
        assert style.get(f"{{{W_NS}}}val") == "FrontMatterHeading"

    approval_table = next(
        table for table in body.findall(f"{{{W_NS}}}tbl")
        if table.find(
            f"{{{W_NS}}}tblPr/{{{W_NS}}}tblCaption"
        ).get(f"{{{W_NS}}}val") == "FRONT_MATTER_APPROVAL"
    )
    body.remove(approval_table)
    findings = validator.validate_iman_front_matter(document, styles)
    assert (
        "[front-matter] editable approval table count is 0; expected 1."
    ) in findings


def test_front_matter_validator_rejects_undefined_daftar_isi_bookmark():
    document = ET.Element(f"{{{W_NS}}}document")
    body = ET.SubElement(document, f"{{{W_NS}}}body")

    heading = ET.SubElement(body, f"{{{W_NS}}}p")
    ET.SubElement(
        heading,
        f"{{{W_NS}}}bookmarkStart",
        {
            f"{{{W_NS}}}id": "1",
            f"{{{W_NS}}}name": "_TocDaftarIsi",
        },
    )
    heading_run = ET.SubElement(heading, f"{{{W_NS}}}r")
    ET.SubElement(heading_run, f"{{{W_NS}}}t").text = "DAFTAR ISI"
    ET.SubElement(
        heading,
        f"{{{W_NS}}}bookmarkEnd",
        {f"{{{W_NS}}}id": "1"},
    )

    entry = ET.SubElement(body, f"{{{W_NS}}}p")
    entry_properties = ET.SubElement(entry, f"{{{W_NS}}}pPr")
    ET.SubElement(
        entry_properties,
        f"{{{W_NS}}}pStyle",
        {f"{{{W_NS}}}val": "TOC1"},
    )
    entry_run = ET.SubElement(entry, f"{{{W_NS}}}r")
    ET.SubElement(entry_run, f"{{{W_NS}}}t").text = "DAFTAR ISI"
    field_run = ET.SubElement(entry, f"{{{W_NS}}}r")
    instruction = ET.SubElement(field_run, f"{{{W_NS}}}instrText")
    instruction.text = " PAGEREF _TocDaftarIsi \\h "

    validator = _load_validator()
    styles = ET.Element(f"{{{W_NS}}}styles")
    findings = validator.validate_iman_front_matter(document, styles)
    assert not any(
        "Daftar Isi TOC entry references an undefined bookmark" in finding
        for finding in findings
    )

    instruction.text = " PAGEREF _MissingBookmark \\h "
    findings = validator.validate_iman_front_matter(document, styles)
    assert (
        "[front-matter] Daftar Isi TOC entry references an undefined "
        "bookmark: ['_MissingBookmark']."
    ) in findings


def test_built_docx_front_matter_order_and_typography():
    configured = os.environ.get("TA_DOCX_PATH")
    if not configured:
        import pytest
        pytest.skip("Set TA_DOCX_PATH after a fresh build to inspect front matter.")
    output = Path(configured)
    assert output.is_file(), output

    module = _load_validator()
    with zipfile.ZipFile(output) as package:
        document = ET.fromstring(package.read("word/document.xml"))
        styles = ET.fromstring(package.read("word/styles.xml"))

    assert module.validate_iman_front_matter(document, styles) == []
