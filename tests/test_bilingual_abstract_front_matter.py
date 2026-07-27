from pathlib import Path
import sys

import lxml.etree as LET


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
SCRATCH = ROOT / "scratch"
sys.path.insert(0, str(SCRATCH))
sys.path.insert(0, str(SCRIPTS))

import patch_template  # noqa: E402
import format_ta_proyek as formatter  # noqa: E402


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def qn(name):
    return f"{{{W}}}{name}"


def _paragraph(text):
    paragraph = LET.Element(qn("p"))
    run = LET.SubElement(paragraph, qn("r"))
    LET.SubElement(run, qn("t")).text = text
    return paragraph


def _text(paragraph):
    return "".join(node.text or "" for node in paragraph.iter(qn("t")))


def test_load_draft_front_matter_reads_bilingual_abstracts(tmp_path, monkeypatch):
    draft = tmp_path / "draft.md"
    draft.write_text(
        "# JUDUL\n"
        "# SUBJUDUL\n\n"
        "Nama Mahasiswa\n"
        "2210000000\n"
        "2026\n\n"
        "# SURAT PERNYATAAN KEASLIAN\n\n"
        "Yang bertanda tangan di bawah ini:\n\n"
        "Nama: Nama Mahasiswa\n\n"
        "NIM: 2210000000\n\n"
        "Pernyataan keaslian laporan.\n\n"
        "# ABSTRAK\n\n"
        "Isi *abstrak* Indonesia.\n\n"
        "Kata kunci: asset 3D, database.\n\n"
        "# ABSTRACT\n\n"
        "English abstract text.\n\n"
        "Keywords: 3D asset, database.\n\n"
        "# KATA PENGANTAR\n\n"
        "Paragraf pertama kata pengantar.\n\n"
        "Paragraf kedua kata pengantar.\n\n"
        "# DAFTAR GAMBAR\n\n"
        "# BAB I PENDAHULUAN\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("TA_DRAFT_PATH", str(draft))

    metadata = patch_template.load_draft_front_matter()

    assert metadata["abstract_id"] == "Isi *abstrak* Indonesia."
    assert metadata["keywords_id"] == "asset 3D, database."
    assert metadata["abstract_en"] == "English abstract text."
    assert metadata["keywords_en"] == "3D asset, database."
    assert metadata["originality_statement"] == [
        "Yang bertanda tangan di bawah ini:",
        "Nama: Nama Mahasiswa",
        "NIM: 2210000000",
        "Pernyataan keaslian laporan.",
    ]
    assert metadata["copyright_statement"] == []
    assert metadata["preface"] == [
        "Paragraf pertama kata pengantar.",
        "Paragraf kedua kata pengantar.",
    ]


def test_insert_bilingual_abstracts_uses_separate_pages_and_eleven_point_body():
    body = LET.Element(qn("body"))
    body.append(_paragraph("LEMBAR PERSETUJUAN"))
    toc = LET.SubElement(body, qn("sdt"))
    toc_content = LET.SubElement(toc, qn("sdtContent"))
    toc_content.append(_paragraph("DAFTAR ISI"))
    body.append(_paragraph("DAFTAR GAMBAR"))
    metadata = {
        "abstract_id": "Isi *abstrak* Indonesia.",
        "keywords_id": "asset 3D, database.",
        "abstract_en": "English abstract text.",
        "keywords_en": "3D asset, database.",
    }

    inserted = patch_template.insert_bilingual_abstracts(body, metadata, W)

    assert inserted == 6
    assert list(body).index(toc) == 7
    paragraphs = body.findall(qn("p"))
    assert [_text(paragraph) for paragraph in paragraphs] == [
        "LEMBAR PERSETUJUAN",
        "ABSTRAK",
        "Isi abstrak Indonesia.",
        "Kata kunci: asset 3D, database.",
        "ABSTRACT",
        "English abstract text.",
        "Keywords: 3D asset, database.",
        "DAFTAR GAMBAR",
    ]
    for heading_index in (1, 4):
        assert paragraphs[heading_index].find("w:pPr/w:pageBreakBefore", {"w": W}) is not None
    for body_index in (2, 3, 5, 6):
        sizes = {
            node.get(qn("val"))
            for node in paragraphs[body_index].findall(".//w:sz", {"w": W})
        }
        assert sizes == {"22"}
        assert not paragraphs[body_index].findall(".//w:i", {"w": W})


def test_formatter_restores_abstract_page_break_and_body_size_after_term_formatting():
    root = LET.Element(qn("document"))
    body = LET.SubElement(root, qn("body"))
    heading = patch_template._build_front_matter_paragraph(
        "ABSTRAK", W, style="Heading1", half_points=24,
        page_break_before=False, alignment="center", bold=True,
    )
    body.append(heading)
    body.append(patch_template._build_front_matter_paragraph(
        "asset *Unity* dan database", W, half_points=24,
    ))
    body.append(patch_template._build_front_matter_paragraph(
        "DAFTAR GAMBAR", W, style="Heading1", half_points=24,
    ))

    formatted = formatter.enforce_bilingual_abstract_layout(root, {"w": W})

    assert formatted == 1
    assert heading.find("w:pPr/w:pageBreakBefore", {"w": W}) is not None
    body_run_sizes = body.findall("w:p", {"w": W})[1].findall(".//w:sz", {"w": W})
    assert {node.get(f"{{{W}}}val") for node in body_run_sizes} == {"22"}


def test_second_cover_and_statement_are_inserted_before_approval():
    body = LET.Element(qn("body"))
    cover = _paragraph("COVER PERTAMA")
    approval = _paragraph("")
    drawing = LET.SubElement(approval, qn("r"))
    LET.SubElement(drawing, qn("drawing"))
    toc = _paragraph("DAFTAR ISI")
    body.extend([cover, approval, toc])
    metadata = {
        "title": "PERANCANGAN ASSET 3D DAN PENGELOLAAN DATABASE",
        "subtitle": "PADA SISTEM DENAH VIRTUAL UPNVJ KAMPUS PONDOK LABU",
        "name": "Dwikhi Deandra Purnianto",
        "nim": "2210511131",
        "year": "2026",
    }

    inserted = patch_template.insert_cover_two_and_statement(
        body, approval, metadata, W
    )

    # Fifteen paragraphs mirror the first-cover sequence, followed by the
    # two-paragraph blank statement page.
    assert inserted == 17
    texts = [_text(paragraph) for paragraph in body.findall(qn("p"))]
    assert texts.index("LAPORAN PROYEK") < texts.index(
        "PERNYATAAN MENGENAI SKRIPSI DAN SUMBER INFORMASI"
    )
    assert body.findall(qn("p"))[1].find(
        "w:pPr/w:pageBreakBefore", {"w": W}
    ) is not None

    second_cover = body.findall(qn("p"))[1:16]
    assert [_text(paragraph) for paragraph in second_cover][0] == "LAPORAN PROYEK"
    second_cover_text = " ".join(_text(paragraph) for paragraph in second_cover)
    assert metadata["title"] in second_cover_text
    assert metadata["subtitle"] in second_cover_text


def test_second_cover_reuses_first_cover_paragraph_positions():
    body = LET.Element(qn("body"))
    first_cover = []
    for index in range(15):
        paragraph = _paragraph(f"FIRST-{index}")
        ppr = LET.SubElement(paragraph, qn("pPr"))
        LET.SubElement(
            ppr, qn("jc"), {qn("val"): "center"}
        )
        LET.SubElement(
            ppr, qn("spacing"), {qn("after"): "120"}
        )
        if index == 4:
            drawing_run = LET.SubElement(paragraph, qn("r"))
            LET.SubElement(drawing_run, qn("drawing"))
        first_cover.append(paragraph)
        body.append(paragraph)
    approval = _paragraph("")
    approval_run = LET.SubElement(approval, qn("r"))
    LET.SubElement(approval_run, qn("drawing"))
    body.append(approval)

    metadata = {
        "title": "JUDUL TUGAS AKHIR",
        "subtitle": "SUBJUDUL TUGAS AKHIR",
        "name": "Dwikhi Deandra Purnianto",
        "nim": "2210511131",
        "year": "2026",
    }
    inserted = patch_template.insert_cover_two_and_statement(
        body, approval, metadata, W
    )

    assert inserted == 17
    paragraphs = body.findall(qn("p"))
    second_cover = paragraphs[15:30]
    assert _text(second_cover[0]) == "LAPORAN PROYEK"
    assert _text(second_cover[4]) == (
        "JUDUL TUGAS AKHIRSUBJUDUL TUGAS AKHIR"
    )
    assert not second_cover[4].find(".//w:drawing", {"w": W})
    assert _text(second_cover[7]) == metadata["name"]
    assert _text(second_cover[8]) == metadata["nim"]
    assert second_cover[0].find("w:pPr/w:pageBreakBefore", {"w": W}) is not None

    # The second cover uses the same center alignment and after-spacing as
    # the first cover's corresponding text lines.
    for first, second in zip((first_cover[0], first_cover[7]), (second_cover[0], second_cover[7])):
        assert LET.tostring(
            first.find("w:pPr/w:jc", {"w": W})
        ) == LET.tostring(second.find("w:pPr/w:jc", {"w": W}))
        assert LET.tostring(
            first.find("w:pPr/w:spacing", {"w": W})
        ) == LET.tostring(second.find("w:pPr/w:spacing", {"w": W}))


def test_authored_originality_statement_replaces_blank_statement_page():
    body = LET.Element(qn("body"))
    cover = _paragraph("COVER PERTAMA")
    approval = _paragraph("")
    approval_run = LET.SubElement(approval, qn("r"))
    LET.SubElement(approval_run, qn("drawing"))
    body.extend([cover, approval])
    metadata = {
        "title": "JUDUL TUGAS AKHIR",
        "subtitle": "SUBJUDUL TUGAS AKHIR",
        "name": "Dwikhi Deandra Purnianto",
        "nim": "2210511131",
        "year": "2026",
        "originality_statement": [
            "Yang bertanda tangan di bawah ini:",
            "Nama: Dwikhi Deandra Purnianto",
            "NIM: 2210511131",
            "Pernyataan keaslian laporan.",
            "Jakarta, [tanggal, bulan, tahun]",
            "Yang menyatakan,",
            "[Meterai dan tanda tangan]",
            "Dwikhi Deandra Purnianto",
        ],
    }

    inserted = patch_template.insert_cover_two_and_statement(
        body, approval, metadata, W
    )

    assert inserted == 24
    texts = [_text(paragraph) for paragraph in body.findall(qn("p"))]
    assert "SURAT PERNYATAAN KEASLIAN" in texts
    assert "PERNYATAAN MENGENAI SKRIPSI DAN SUMBER INFORMASI" not in texts
    heading = next(
        paragraph for paragraph in body.findall(qn("p"))
        if _text(paragraph) == "SURAT PERNYATAAN KEASLIAN"
    )
    assert heading.find(
        "w:pPr/w:pageBreakBefore", {"w": W}
    ) is not None
    signature = next(
        paragraph for paragraph in body.findall(qn("p"))
        if _text(paragraph) == "Yang menyatakan,"
    )
    assert signature.find("w:pPr/w:jc", {"w": W}).get(qn("val")) == "right"
    declaration = next(
        paragraph for paragraph in body.findall(qn("p"))
        if _text(paragraph) == "Pernyataan keaslian laporan."
    )
    assert declaration.find(
        "w:pPr/w:ind", {"w": W}
    ).get(qn("firstLine")) == "567"


def test_copyright_statement_page_is_inserted_after_originality_statement():
    body = LET.Element(qn("body"))
    cover = _paragraph("COVER PERTAMA")
    approval = _paragraph("")
    approval_run = LET.SubElement(approval, qn("r"))
    LET.SubElement(approval_run, qn("drawing"))
    body.extend([cover, approval])
    metadata = {
        "title": "JUDUL TUGAS AKHIR",
        "subtitle": "SUBJUDUL TUGAS AKHIR",
        "name": "Dwikhi Deandra Purnianto",
        "nim": "2210511131",
        "year": "2026",
        "originality_statement": [
            "Yang bertanda tangan di bawah ini:",
            "Nama: Dwikhi Deandra Purnianto",
        ],
        "copyright_statement": [
            "Dengan ini saya menyatakan bahwa skripsi dengan judul "
            "“Judul tugas akhir” adalah karya saya.",
            "Dengan ini saya melimpahkan hak cipta dari karya tulis saya "
            "kepada Universitas Pembangunan Nasional “Veteran” Jakarta.",
            "Jakarta, 23 Juli 2026",
            "Dwikhi Deandra Purnianto 2210511131",
        ],
    }

    patch_template.insert_cover_two_and_statement(body, approval, metadata, W)
    texts = [_text(paragraph) for paragraph in body.findall(qn("p"))]
    heading = (
        "PERNYATAAN MENGENAI SKRIPSI DAN SUMBER INFORMASI "
        "SERTA PELIMPAHAN HAK CIPTA"
    )
    assert heading in texts
    assert texts.index(heading) > texts.index("SURAT PERNYATAAN KEASLIAN")
    copyright_heading = next(
        paragraph for paragraph in body.findall(qn("p"))
        if _text(paragraph) == heading
    )
    assert copyright_heading.find(
        "w:pPr/w:pageBreakBefore", {"w": W}
    ) is not None


def test_blank_kata_pengantar_page_is_inserted_before_daftar_isi():
    body = LET.Element(qn("body"))
    body.append(_paragraph("ABSTRACT"))
    toc = _paragraph("DAFTAR ISI")
    body.append(toc)

    inserted = patch_template.insert_blank_front_heading(
        body, "KATA PENGANTAR", W
    )

    assert inserted == 2
    texts = [_text(paragraph) for paragraph in body.findall(qn("p"))]
    assert texts == ["ABSTRACT", "KATA PENGANTAR", "", "DAFTAR ISI"]
    assert body.findall(qn("p"))[1].find(
        "w:pPr/w:pageBreakBefore", {"w": W}
    ) is not None
    assert toc.find("w:pPr/w:pageBreakBefore", {"w": W}) is not None


def test_authored_kata_pengantar_page_is_inserted_before_daftar_isi():
    body = LET.Element(qn("body"))
    body.append(_paragraph("ABSTRACT"))
    toc = _paragraph("DAFTAR ISI")
    body.append(toc)

    inserted = patch_template.insert_preface_page(
        body,
        [
            "Paragraf pertama kata pengantar.",
            "1. Ucapan terima kasih pertama.",
            "Paragraf penutup kata pengantar.",
        ],
        W,
    )

    assert inserted == 4
    paragraphs = body.findall(qn("p"))
    assert [_text(paragraph) for paragraph in paragraphs] == [
        "ABSTRACT",
        "KATA PENGANTAR",
        "Paragraf pertama kata pengantar.",
        "1. Ucapan terima kasih pertama.",
        "Paragraf penutup kata pengantar.",
        "DAFTAR ISI",
    ]
    assert paragraphs[1].find(
        "w:pPr/w:pageBreakBefore", {"w": W}
    ) is not None
    assert toc.find("w:pPr/w:pageBreakBefore", {"w": W}) is not None
    for paragraph in paragraphs[2:5]:
        sizes = {
            node.get(qn("val"))
            for node in paragraph.findall(".//w:sz", {"w": W})
        }
        assert sizes == {"24"}
    assert paragraphs[2].find(
        "w:pPr/w:ind", {"w": W}
    ).get(qn("firstLine")) == "567"
    numbered_indent = paragraphs[3].find("w:pPr/w:ind", {"w": W})
    assert numbered_indent.get(qn("left")) == "567"
    assert numbered_indent.get(qn("hanging")) == "360"
    assert paragraphs[4].find(
        "w:pPr/w:ind", {"w": W}
    ).get(qn("firstLine")) == "567"
