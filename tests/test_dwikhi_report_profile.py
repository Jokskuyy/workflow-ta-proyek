"""Regression guards for the isolated Dwikhi report profile."""

import importlib.util
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "content" / "report-profiles.json"
DWIKHI_DRAFT = ROOT / "Tugas_Akhir_Dwikhi_Draft.md"
DWIKHI_FRONT = ROOT / "content" / "roles" / "dwikhi" / "front-matter.json"
DWIKHI_MANIFEST = ROOT / "images" / "dwikhi" / "manifest.json"
SQL = ROOT / "dokumentasi" / "sql" / "001_full_setup.sql"
SQL_SEED = ROOT / "dokumentasi" / "sql" / "002_seed_data.sql"
ERD_MAIN = ROOT / "diagrams" / "erd-dwikhi-data-kampus-denah-2d.puml"
ERD_SUPPORT = ROOT / "diagrams" / "erd-dwikhi-tabel-pendukung.puml"
USE_CASE_DATABASE = (
    ROOT / "diagrams" / "dwikhi-use-case-pengelolaan-database.puml"
)
ACTIVITY_CRUD = (
    ROOT / "diagrams" / "gambar-2.13-activity-pengelolaan-data-admin.puml"
)


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _table_rows(draft, table_id):
    match = re.search(
        rf"\[TABLE-ID:{re.escape(table_id)}\].*?\[TABLE\]\n(.*?)\n\[/TABLE\]",
        draft,
        flags=re.DOTALL,
    )
    assert match, f"table {table_id} is missing"
    return match.group(1).splitlines()


def _figure_ids(draft):
    return re.findall(r"^\[FIGURE:([^\]]+)\]$", draft, flags=re.MULTILINE)


def test_profiles_keep_iman_default_and_dwikhi_sources_isolated():
    profiles = json.loads(PROFILES.read_text(encoding="utf-8"))
    assert profiles["iman"] == {
        "draft": "Tugas_Akhir_Draft.md",
        "front_matter": "content/roles/iman/front-matter.json",
        "image_root": "images",
        "manifest": "images/manifest.json",
        "reconcile": "images/manifest_reconcile.json",
        "output": "Tugas_Akhir_Formatted.docx",
    }
    assert profiles["dwikhi"]["draft"] == "Tugas_Akhir_Dwikhi_Draft.md"
    assert profiles["dwikhi"]["front_matter"] != profiles["iman"]["front_matter"]
    assert profiles["dwikhi"]["image_root"] != profiles["iman"]["image_root"]
    assert profiles["dwikhi"]["manifest"] != profiles["iman"]["manifest"]
    assert profiles["dwikhi"]["output"] == "Tugas_Akhir_Dwikhi_Formatted.docx"

    pipeline = _load_module(
        "build_pipeline_profile_test",
        ROOT / "skills" / "scripts" / "build_pipeline.py",
    )
    assert pipeline.parse_args([]).profile == "iman"
    assert pipeline.parse_args([]).output is None
    assert pipeline.load_profile("iman")["draft"] == "Tugas_Akhir_Draft.md"
    assert pipeline.load_profile("dwikhi")["draft"] == (
        "Tugas_Akhir_Dwikhi_Draft.md"
    )


def test_formatter_bibliography_defaults_to_active_profile_draft(monkeypatch):
    formatter = _load_module(
        "format_ta_proyek_dwikhi_bibliography_test",
        ROOT / "skills" / "scripts" / "format_ta_proyek.py",
    )
    merger = _load_module(
        "merge_draft_to_docx_dwikhi_bibliography_test",
        ROOT / "skills" / "scripts" / "merge_draft_to_docx.py",
    )
    monkeypatch.setenv("TA_DRAFT_PATH", str(DWIKHI_DRAFT))

    namespace = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    sdt = formatter.lxml.etree.Element(f"{{{namespace}}}sdt")
    content = formatter.lxml.etree.SubElement(sdt, f"{{{namespace}}}sdtContent")
    formatter.clean_bibliography_sdt(sdt)

    expected = merger.parse_bibliography_entries(str(DWIKHI_DRAFT))
    rendered = content.findall(f"{{{namespace}}}p")
    assert rendered
    assert "".join(rendered[0].itertext()) == "".join(
        text for text, _ in expected[0].spans
    )


def test_dwikhi_front_matter_uses_latest_identity_without_fake_signature():
    data = json.loads(DWIKHI_FRONT.read_text(encoding="utf-8"))
    assert data["cover"]["title"] == (
        "PERANCANGAN ASSET 3D DAN PENGELOLAAN DATABASE PADA SISTEM "
        "DENAH VIRTUAL UPNVJ KAMPUS PONDOK LABU"
    )
    assert data["cover"]["author"] == "Dwikhi Deandra Purnianto"
    assert data["cover"]["nim"] == "2210511131"
    assert "signature" not in data["declaration"]
    assert len(data["preface"]["acknowledgements"]) == 9
    assert (ROOT / data["approval_scan"]["image"]).is_file()
    assert data["identity_footer"] == {
        "author_year": "Dwikhi Deandra Purnianto, 2026",
        "title": (
            "PERANCANGAN ASSET 3D DAN PENGELOLAAN DATABASE PADA SISTEM "
            "DENAH VIRTUAL UPNVJ KAMPUS PONDOK LABU"
        ),
        "institution": (
            "UPN Veteran Jakarta, Fakultas Ilmu Komputer, S1 Informatika"
        ),
        "links": (
            "[www.upnvj.ac.id-www.library.upnvj.ac.id-"
            "www.repository.upnvj.ac.id]"
        ),
        "font": "Times New Roman",
        "size_pt": 8,
    }


def test_complete_sql_and_two_erds_match_eleven_tables_and_ten_foreign_keys():
    sql = SQL.read_text(encoding="utf-8")
    expected_tables = {
        "gedung",
        "fasilitas",
        "fakultas",
        "program_studi",
        "campus_maps",
        "campus_map_nodes",
        "campus_map_edges",
        "campus_map_building_points",
        "admin_users",
        "audit_logs",
        "web_analytics_log",
    }
    sql_tables = set(re.findall(
        r"CREATE TABLE public\.([a-z_]+)\s*\(",
        sql,
        flags=re.IGNORECASE,
    ))
    assert sql_tables == expected_tables
    assert len(re.findall(r"REFERENCES public\.", sql, flags=re.IGNORECASE)) == 10
    assert not re.search(r"CREATE\s+TRIGGER", sql, flags=re.IGNORECASE)

    main = ERD_MAIN.read_text(encoding="utf-8")
    support = ERD_SUPPORT.read_text(encoding="utf-8")
    declarations = re.findall(
        r'^entity "([a-z_]+)" as ',
        main + "\n" + support,
        flags=re.MULTILINE,
    )
    assert len(declarations) == 11
    assert set(declarations) == expected_tables
    assert len(re.findall(r"\|\|--o\{", main)) == 10
    assert not re.search(r"^\w+\s+\|\|--o\{", support, flags=re.MULTILINE)
    assert "actor_id adalah UUID biasa" in support
    for target in (
        "ref_gedung",
        "ref_fasilitas",
        "ref_fakultas",
        "ref_program_studi",
        "ref_campus_map",
    ):
        assert f"admin_users ..> {target}" in support
    assert "Hubungan akses ini bukan foreign key" in support

    assert hashlib.sha256(SQL.read_bytes()).hexdigest().upper() == (
        "B440C517FC0289CBD6F546B4A3ED12D2ADC8E7B9F6CB8181F4FFF5A96681E61B"
    )
    assert hashlib.sha256(SQL_SEED.read_bytes()).hexdigest().upper() == (
        "2A2BF7A97A566B75546C29D8FE3025EB0D9C4F682BF49BE2E323D603E1D57B2F"
    )


def test_dwikhi_draft_claims_full_schema_and_keeps_2d_chronology():
    draft = DWIKHI_DRAFT.read_text(encoding="utf-8")
    plain = draft.replace("*", "")
    forbidden = [
        "perancangan empat tabel inti",
        "empat tabel inti dalam ERD",
        "tujuh tabel ekstensi yang tidak diklaim",
        "tidak diklaim sebagai rancangan inti penulis",
    ]
    assert not any(phrase in plain.lower() for phrase in forbidden)
    assert "skema lengkap 11 tabel" in plain
    assert "10 foreign key" in plain
    assert "setelah pengembangan dan tindak lanjut UAT" in plain
    assert "bukan sebagai kebutuhan awal" in plain
    assert "tidak memuat definisi trigger" in plain
    assert "tidak dijalankan saat penyusunan laporan" in plain
    assert "Keterkaitan Identifikasi Masalah dan Tujuan" in plain
    assert "Hasil SELECT Relasi Gedung Dewi Sartika dengan Fasilitas" in plain
    assert "FROM public.gedung AS g" in draft
    assert "FROM public.admin_users" in draft


def test_dwikhi_database_uml_covers_admin_crud_with_solid_include_relations():
    draft = DWIKHI_DRAFT.read_text(encoding="utf-8")
    use_case = USE_CASE_DATABASE.read_text(encoding="utf-8")
    activity = ACTIVITY_CRUD.read_text(encoding="utf-8")

    assert "Administrator" in use_case
    for phrase in (
        "Melihat Data",
        "Menambah Data",
        "Mengubah Data",
        "Menghapus Data",
        "Gedung, Fasilitas,",
        "Program Studi, atau Denah 2D",
        "Memeriksa Sesi",
        "Kebijakan RLS",
    ):
        assert phrase in use_case
    assert "<<include>>" in use_case
    assert "-->" in use_case
    assert "..>" not in use_case
    assert "Memilih modul dan operasi data" in activity
    assert "Menjalankan operasi data" in activity
    assert draft.count("[FIGURE:diagram_use_case_database]") == 1
    assert draft.count("[FIGURE:diagram_activity_crud_admin]") == 1


def test_wiki_tables_and_detailed_asset_evidence_are_preserved():
    draft = DWIKHI_DRAFT.read_text(encoding="utf-8")
    expected_table_ids = [
        "peran_tanggung_jawab",
        "keterkaitan_masalah_tujuan",
        "jadwal_kegiatan",
        "istilah_teknis_utama",
        "tahapan_prototipe_dwikhi",
        "struktur_basis_data",
        "hubungan_mitra_proyek",
        "inventaris_foto_referensi",
        "metrik_tiga_aset",
        "inventaris_material_tekstur",
        "logbook_implementasi",
        "status_bukti_basis_data",
        "inventaris_seed_fasilitas",
        "temuan_kualitas_seed_fasilitas",
        "hasil_uji_integritas_db",
        "hasil_uji_rls_audit",
    ]
    assert re.findall(r"^\[TABLE-ID:([^\]]+)\]$", draft, flags=re.MULTILINE) == (
        expected_table_ids
    )
    assert len(_table_rows(draft, "istilah_teknis_utama")) == 24
    assert len(_table_rows(draft, "keterkaitan_masalah_tujuan")) == 4
    assert len(_table_rows(draft, "tahapan_prototipe_dwikhi")) == 8
    assert len(_table_rows(draft, "inventaris_foto_referensi")) == 31
    assert len(_table_rows(draft, "metrik_tiga_aset")) == 21
    assert len(_table_rows(draft, "inventaris_material_tekstur")) == 11
    assert len(_table_rows(draft, "logbook_implementasi")) == 7

    forbidden_tables = {
        "metadata_bukti_aset_representatif",
        "metadata_tekstur_representatif",
        "inventaris_bukti_aset",
        "status_metadata_aset",
        "status_uji_visual_aset",
        "kelompok_implementasi_skema",
        "hasil_sync_checker_awal",
        "hasil_sync_checker_lanjutan",
    }
    assert not any(
        f"[TABLE-ID:{table_id}]" in draft for table_id in forbidden_tables
    )

    headings = [
        "### 3.2.1 Implementasi Perancangan ERD dan Kebijakan Akses Data",
        "### 3.2.2 Implementasi Struktur Database dan Data Gedung Dewi Sartika",
        "### 3.2.3 Implementasi Pembuatan Visual Gedung Dewi Sartika",
        "### 3.2.4 Implementasi Prefab, Pointer, dan Penempatan pada Scene",
        "### 3.2.5 Implementasi Pemetaan Kode Lokasi dan Batas Integrasi",
    ]
    offsets = [draft.index(heading) for heading in headings]
    assert offsets == sorted(offsets)

    process_ids = {
        "process_dewi_reference",
        "process_dewi_base",
        "process_dewi_ground_floor",
        "process_dewi_material_create",
        "process_dewi_material_texture",
        "process_dewi_material_apply",
        "process_dewi_environment",
        "process_dewi_floor_groups",
        "process_dewi_pointer_create",
        "process_dewi_pointer_target",
        "process_dewi_scene_placement",
        "process_dewi_prefab_save",
    }
    figure_ids = _figure_ids(draft)
    assert len(figure_ids) == len(set(figure_ids)) == 105
    assert process_ids.issubset(figure_ids)
    assert {
        "evidence_asset_jenderal",
        "evidence_hierarchy_jenderal",
        "evidence_asset_dewi",
        "evidence_hierarchy_dewi",
        "evidence_asset_ki_hadjar",
        "evidence_hierarchy_ki_hadjar",
    }.issubset(figure_ids)

    appendix_three = draft.split(
        "# LAMPIRAN 3. Bukti Pemodelan dan Penataan Asset 3D",
        maxsplit=1,
    )[1].split("# LAMPIRAN 4.", maxsplit=1)[0]
    assert len(_figure_ids(appendix_three)) == 58
    assert "mockup_" not in draft
    assert "# LAMPIRAN 6." not in draft


def test_dwikhi_manifest_and_markers_use_both_erd_figures_once():
    draft = DWIKHI_DRAFT.read_text(encoding="utf-8")
    manifest = json.loads(DWIKHI_MANIFEST.read_text(encoding="utf-8"))
    items = {item["id"]: item for item in manifest["images"]}
    assert len(items) == len(manifest["images"])
    assert all(
        (ROOT / "images" / "dwikhi" / item["file"]).is_file()
        for item in manifest["images"]
    )
    expected = {
        "diagram_use_case_database": (
            "Use Case Pengelolaan Database melalui Panel Admin"
        ),
        "diagram_activity_crud_admin": (
            "Activity Diagram CRUD Data melalui Panel Admin"
        ),
        "diagram_erd_data_navigasi": "ERD Data Kampus dan Denah 2D",
        "diagram_erd_pendukung": (
            "ERD Tabel Pendukung dan Hubungan Akses Logis Administrator"
        ),
        "evidence_select_dewi_facilities": (
            "Hasil SELECT Relasi Gedung Dewi Sartika dengan Fasilitas"
        ),
    }
    for figure_id, caption in expected.items():
        assert items[figure_id]["caption_match"] == caption
        assert draft.count(f"[FIGURE:{figure_id}]") == 1
        assert draft.count(f"[FIGCAPTION:{caption}]") == 1
        assert draft.count(f"[FIGREF:{figure_id}]") >= 1
        assert (ROOT / "images" / "dwikhi" / items[figure_id]["file"]).is_file()
    assert "diagram_erd" not in items
    assert len(items) == 113
    assert not any(figure_id.startswith("mockup_") for figure_id in items)
    assert set(_figure_ids(draft)).issubset(items)


def test_image_contract_stays_at_fourteen_centimetres():
    injector = _load_module(
        "injector_dwikhi_profile_test",
        ROOT / "skills" / "scripts" / "inject_all_images.py",
    )
    validator = _load_module(
        "validator_dwikhi_profile_test",
        ROOT / "skills" / "scripts" / "validate_docx_structure.py",
    )
    assert injector.BODY_MAX_W_EMU == 5_040_000
    assert validator.MAX_WIDTH_EMU == 5_040_000
