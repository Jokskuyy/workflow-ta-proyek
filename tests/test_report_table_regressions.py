from pathlib import Path
import json
import struct
from zipfile import ZipFile

from lxml import etree


ROOT = Path(__file__).resolve().parents[1]


def _table_body(table_id):
    text = (ROOT / "Tugas_Akhir_Draft.md").read_text(encoding="utf-8")
    section = text.split(f"[TABLE-ID:{table_id}]", 1)[1]
    body = section.split("[/TABLE]", 1)[0]
    return body.split("[TABLE]", 1)[1]


def _pipe_cells(line):
    return [cell.strip() for cell in line.split("|")]


def test_redundant_asset_metadata_tables_stay_removed():
    text = (ROOT / "Tugas_Akhir_Draft.md").read_text(encoding="utf-8")
    for table_id in (
        "metadata_bukti_aset_representatif",
        "metadata_tekstur_representatif",
        "inventaris_bukti_aset",
        "status_metadata_aset",
        "status_uji_visual_aset",
    ):
        assert f"[TABLE-ID:{table_id}]" not in text
        assert f"[TABREF:{table_id}]" not in text


def test_table_314_removes_status_column_only():
    rows = [line.strip() for line in _table_body("hasil_uji_integritas_db").splitlines() if line.strip()]
    assert _pipe_cells(rows[0]) == [
        "Cakupan", "Artefak yang Digunakan", "Informasi yang Ditampilkan", "Hubungan dengan Laporan"
    ]
    assert all(len(_pipe_cells(row)) == 4 for row in rows)
    assert "Status" not in rows[0]
    assert "Belum dieksekusi" not in "\n".join(rows)
    assert "Bukti yang Diperlukan" not in rows[0]


def test_approval_word_source_and_render_are_present_and_a4_ratio():
    source = ROOT / "images" / "lembar_persetujuan.jpeg"
    data = source.read_bytes()
    assert data.startswith(b"\xff\xd8\xff")
    from PIL import Image
    with Image.open(source) as image:
        width, height = image.size
    ratio = width / height
    assert 0.64 < ratio < 0.68


def test_built_docx_front_matter_order_and_latest_approval_media():
    docx = ROOT / "Tugas_Akhir_Formatted.docx"
    if not docx.exists():
        return
    source_mtime = max(
        (ROOT / "Tugas_Akhir_Draft.md").stat().st_mtime,
        (ROOT / "skills" / "scripts" / "patch_template.py").stat().st_mtime,
    )
    if docx.stat().st_mtime < source_mtime:
        return
    ns = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
    }
    with ZipFile(docx) as package:
        document = etree.fromstring(package.read("word/document.xml"))
        rels = etree.fromstring(package.read("word/_rels/document.xml.rels"))
        paragraphs = document.xpath(".//w:body/w:p", namespaces=ns)
        bab1_index = next(
            index for index, paragraph in enumerate(paragraphs)
            if "PENDAHULUAN" in "".join(paragraph.xpath(".//w:t/text()", namespaces=ns))
        )
        front = paragraphs[:bab1_index]
        drawings = [paragraph for paragraph in front if paragraph.xpath(".//w:drawing", namespaces=ns)]
        assert len(drawings) == 2  # cover plus the approval page
        assert not any(
            "LEMBAR PERSETUJUAN" in "".join(paragraph.xpath(".//w:t/text()", namespaces=ns))
            for paragraph in front
        )
        texts = [
            "".join(paragraph.xpath(".//w:t/text()", namespaces=ns)).strip()
            for paragraph in front
        ]
        assert "LAPORAN PROYEK" in texts
        assert "SURAT PERNYATAAN KEASLIAN" in texts
        assert (
            "PERNYATAAN MENGENAI SKRIPSI DAN SUMBER INFORMASI "
            "SERTA PELIMPAHAN HAK CIPTA"
        ) in texts
        assert "KATA PENGANTAR" in texts
        assert texts.index("LAPORAN PROYEK") < texts.index(
            "SURAT PERNYATAAN KEASLIAN"
        )
        assert texts.index(
            "SURAT PERNYATAAN KEASLIAN"
        ) < texts.index(
            "PERNYATAAN MENGENAI SKRIPSI DAN SUMBER INFORMASI "
            "SERTA PELIMPAHAN HAK CIPTA"
        ) < texts.index("ABSTRAK")
        assert texts.index("ABSTRACT") < texts.index("KATA PENGANTAR")
        approval_rid = drawings[1].xpath(".//a:blip/@r:embed", namespaces=ns)
        assert len(approval_rid) == 1
        relationship = next(
            node for node in rels
            if node.get("Id") == approval_rid[0]
        )
        target = relationship.get("Target")
        assert target.endswith(".jpeg")
        media_name = target.rsplit("/", 1)[-1]
        assert package.read(f"word/media/{media_name}") == (
            ROOT / "images" / "lembar_persetujuan.jpeg"
        ).read_bytes()


def test_measurement_figures_are_split_between_body_and_appendix():
    text = (ROOT / "Tugas_Akhir_Draft.md").read_text(encoding="utf-8")
    body = text.split("# BAB IV", 1)[0]
    appendix = text.split("# LAMPIRAN 3.", 1)[1].split("# LAMPIRAN 4.", 1)[0]
    keep = {
        "evidence_metrics_dewi",
        "evidence_metrics_ki_hadjar",
        "evidence_metrics_jenderal",
    }
    all_ids = {
        "evidence_metrics_abdul_rahman",
        "evidence_metrics_cipto",
        "evidence_metrics_dewi",
        "evidence_metrics_jenderal",
        "evidence_metrics_ki_hadjar",
        "evidence_metrics_myamin",
        "evidence_metrics_thamrin",
        "evidence_metrics_kartini",
        "evidence_metrics_soepomo",
        "evidence_metrics_soetomo",
        "evidence_metrics_ukm",
        "evidence_metrics_wahidin",
        "evidence_metrics_yos",
        "evidence_metrics_kantin",
        "evidence_metrics_lapangan_upacara",
        "evidence_metrics_lapangan_basket",
        "evidence_metrics_masjid",
        "evidence_metrics_parkir_belakang",
        "evidence_metrics_parkir_depan",
        "evidence_metrics_parkir_hukum",
    }
    for figure_id in keep:
        assert body.count(f"[FIGURE:{figure_id}]") == 1
        assert appendix.count(f"[FIGURE:{figure_id}]") == 0
    for figure_id in all_ids - keep:
        assert body.count(f"[FIGURE:{figure_id}]") == 0
        assert appendix.count(f"[FIGURE:{figure_id}]") == 1


def test_render_and_hierarchy_figures_use_three_representatives_in_body():
    text = (ROOT / "Tugas_Akhir_Draft.md").read_text(encoding="utf-8")
    body = text.split("# LAMPIRAN 3.", 1)[0]
    appendix = text.split("# LAMPIRAN 3.", 1)[1].split("# LAMPIRAN 4.", 1)[0]
    representative_ids = {
        "evidence_asset_jenderal",
        "evidence_hierarchy_jenderal",
        "evidence_asset_dewi",
        "evidence_hierarchy_dewi",
        "evidence_asset_ki_hadjar",
        "evidence_hierarchy_ki_hadjar",
    }
    for figure_id in representative_ids:
        assert body.count(f"[FIGURE:{figure_id}]") == 1
        assert appendix.count(f"[FIGURE:{figure_id}]") == 0

    appendix_ids = {
        "evidence_asset_cipto",
        "evidence_hierarchy_cipto",
        "evidence_asset_myamin",
        "evidence_hierarchy_myamin",
        "evidence_asset_wahidin",
        "evidence_hierarchy_wahidin",
        "evidence_asset_parkir_belakang",
        "evidence_hierarchy_parkir_belakang",
    }
    for figure_id in appendix_ids:
        assert body.count(f"[FIGURE:{figure_id}]") == 0
        assert appendix.count(f"[FIGURE:{figure_id}]") == 1


def test_technical_terms_table_starts_section_23():
    text = (ROOT / "Tugas_Akhir_Draft.md").read_text(encoding="utf-8")
    section = text.split("## 2.3 Rancangan Proyek", 1)[1].split("### 2.3.1", 1)[0]
    assert "[TABLE-ID:istilah_teknis_utama]" in section
    for term in (
        "*Seed*",
        "`audit_logs`",
        "`unity_object_name`",
        "*Foreign key*",
        "*Unique constraint*",
        "ERD",
        "*Prefab*",
        "*GameObject*",
        "*Mesh*",
        "*vertex*",
        "*Collider*",
        "API",
        "*endpoint*",
        "`DatabaseSyncChecker`",
    ):
        assert term in section


def test_old_dashboard_mockup_appendix_and_manifest_entries_are_removed():
    draft = (ROOT / "Tugas_Akhir_Draft.md").read_text(encoding="utf-8")
    manifest = (ROOT / "images" / "manifest.json").read_text(encoding="utf-8")
    assert "# LAMPIRAN 6." not in draft
    assert "[FIGURE:mockup_" not in draft
    assert '"id": "mockup_' not in manifest
    assert "unpacked_ta/" not in manifest


def test_every_manifest_figure_uses_an_existing_file_under_images():
    manifest = json.loads(
        (ROOT / "images" / "manifest.json").read_text(encoding="utf-8")
    )["images"]
    images_root = (ROOT / "images").resolve()
    for entry in manifest:
        image_path = (images_root / entry["file"]).resolve()
        assert image_path.is_relative_to(images_root)
        assert image_path.is_file(), entry["id"]
        assert entry.get("source", "").startswith("images/"), entry["id"]


def test_narrative_uses_author_and_roles_instead_of_team_first_names():
    draft = (ROOT / "Tugas_Akhir_Draft.md").read_text(encoding="utf-8")
    narrative = draft.split("# BAB I", 1)[1]
    assert "Dwikhi" not in narrative
    assert "Iman" not in narrative
    assert "Faiz" not in narrative
    assert "penulis" in narrative
    assert "*Full Stack Web Developer*, *System Integrator*, dan *DevOps Engineer*" in narrative
    assert "*3D Simulator* dan *Engine Developer*" in narrative


def test_building_count_distinguishes_masjid_facility_asset():
    draft = (ROOT / "Tugas_Akhir_Draft.md").read_text(encoding="utf-8")
    assert "19 *asset* gedung dan satu *asset* fasilitas Masjid" in draft
    assert "19 entitas gedung" in draft
    assert "`id_gedung = 6` dan kode `masjid`" in draft
    assert "20 gedung" not in draft


def test_parkir_belakang_photo_render_and_hierarchy_are_manifested_and_referenced():
    manifest = (ROOT / "images" / "manifest.json").read_text(encoding="utf-8")
    draft = (ROOT / "Tugas_Akhir_Draft.md").read_text(encoding="utf-8")
    assert '"id": "evidence_photo_parkir_belakang"' in manifest
    assert '"id": "evidence_asset_parkir_belakang"' in manifest
    assert '"id": "evidence_hierarchy_parkir_belakang"' in manifest
    assert "list_foto/Refrensi_parkiran_belakang.png" in manifest
    assert "images/list_foto/Refrensi_parkiran_belakang.webp" in manifest
    assert draft.count("[FIGURE:evidence_photo_parkir_belakang]") == 1
    assert draft.count("[FIGURE:evidence_asset_parkir_belakang]") == 1
    assert draft.count("[FIGURE:evidence_hierarchy_parkir_belakang]") == 1
    assert draft.count("[FIGCAPTION:Referensi Aktual Parkir Belakang]") == 1
    assert draft.count("[FIGCAPTION:Asset 3D Parkir Belakang]") == 1
    assert draft.count("[FIGCAPTION:Hierarki Asset Parkir Belakang]") == 1
    assert "[TBD: render asset dan tangkapan hierarki Parkir Belakang]" not in draft


def test_interpretive_material_references_have_confirmed_mappings_without_tbd():
    draft = (ROOT / "Tugas_Akhir_Draft.md").read_text(encoding="utf-8")
    facts = (ROOT / "project_facts.json").read_text(encoding="utf-8")

    assert "`kaca.jpg` untuk kaca jendela interior" in draft
    assert "`material_warna_besi.png` untuk tulisan nama gedung" in draft
    assert "tidak ditampilkan secara eksplisit" in draft
    assert "[TBD: objek penerapan dan sumber/lisensi]" not in draft
    assert '"represents": "Material kaca jendela interior"' in facts
    assert '"represents": "Material tulisan nama gedung"' in facts
    assert '"displayed_explicitly": false' in facts


def test_dashboard_admin_uat_is_a_pipe_table_without_separator_data_row():
    text = (ROOT / "content" / "shared" / "testing" / "uat.md").read_text(
        encoding="utf-8"
    )
    section = text.split("[TABLE-ID:uat_dashboard_admin]", 1)[1]
    table = section.split("Nilai keseluruhan", 1)[0]

    assert "[TABLE]" not in table
    assert "[/TABLE]" not in table
    assert "| Dimensi | Jumlah Pernyataan" in table
    assert "| --- | :---: | :---: | :---: | :---: | --- |" in table


def test_uat_revision_id_column_requests_center_alignment():
    text = (
        ROOT / "content" / "shared" / "testing" / "uat-revisions.md"
    ).read_text(encoding="utf-8")
    section = text.split("[TABLE-ID:tindak_lanjut_uat]", 1)[1]
    table = section.split("Tindak lanjut UAT-R01", 1)[0]

    assert "[TABLE]" not in table
    assert "[/TABLE]" not in table
    assert "| ID | Masalah atau Kebutuhan Pengguna" in table
    assert "| :---: | --- | --- | --- | --- |" in table
