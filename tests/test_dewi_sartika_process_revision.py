import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DRAFT = (ROOT / "Tugas_Akhir_Draft.md").read_text(encoding="utf-8")
MANIFEST = json.loads(
    (ROOT / "images" / "manifest.json").read_text(encoding="utf-8")
)["images"]


PROCESS_IMAGES = {
    "process_dewi_reference": "list_foto/refrensi_gedung_dewi_sartika.jpeg",
    "process_dewi_base": "pembuatan_gedung/bentuk_dasar_dewi_sartika.png",
    "process_dewi_ground_floor": (
        "pembuatan_gedung/pembentukan_lantai_dasar_Gedung_dewi_sartika.png"
    ),
    "process_dewi_material_create": (
        "pembuatan_gedung/Langkah_pembuatan_material_1.png"
    ),
    "process_dewi_material_texture": (
        "pembuatan_gedung/Langkah_pembuatan_material_2_(drag_and_drop_png).png"
    ),
    "process_dewi_material_apply": (
        "pembuatan_gedung/Langkah_pembuatan_material_3_(drag_and_drop_material).png"
    ),
    "process_dewi_environment": (
        "pembuatan_gedung/penambahan_environment_Gedung_dewi_sartika.png"
    ),
    "process_dewi_floor_groups": (
        "pembuatan_gedung/pembagian_gedung_dewi_sartika_per_lantai.png"
    ),
    "process_dewi_pointer_create": "pembuatan_gedung/Pembuatan_pointer_1.png",
    "process_dewi_pointer_target": "pembuatan_gedung/Pembuatan_pointer_2.png",
    "process_dewi_scene_placement": (
        "pembuatan_gedung/penempatan_gedung_dewi_sartika_di_scene_utama.png"
    ),
    "process_dewi_prefab_save": (
        "pembuatan_gedung/penyimpanan_prefab_gedung_dewi_sartika.png"
    ),
}


def test_section_32_follows_the_confirmed_implementation_order():
    headings = [
        "### 3.2.1 Implementasi Perancangan ERD dan Kebijakan Akses Data",
        "### 3.2.2 Implementasi Struktur Database dan Data Gedung Dewi Sartika",
        "### 3.2.3 Implementasi Pembuatan Visual Gedung Dewi Sartika",
        "### 3.2.4 Implementasi Prefab, Pointer, dan Penempatan pada Scene",
        "### 3.2.5 Implementasi Pemetaan Kode Lokasi dan Batas Integrasi",
    ]
    positions = [DRAFT.index(heading) for heading in headings]
    assert positions == sorted(positions)


def test_twelve_dewi_process_images_are_manifested_and_narrated_once():
    entries = {item["id"]: item for item in MANIFEST}
    for figure_id, relative_path in PROCESS_IMAGES.items():
        assert entries[figure_id]["file"] == relative_path
        assert entries[figure_id]["source"] == f"images/{relative_path}"
        assert (ROOT / "images" / relative_path).is_file()
        assert DRAFT.count(f"[FIGURE:{figure_id}]") == 1
        assert DRAFT.count(f"[FIGREF:{figure_id}]") == 1
        caption = entries[figure_id]["caption_match"]
        assert DRAFT.count(f"[FIGCAPTION:{caption}]") == 1


def test_process_images_are_kept_in_bab_three_not_appendix_three():
    body, appendix_tail = DRAFT.split("# LAMPIRAN 3.", 1)
    appendix_three = appendix_tail.split("# LAMPIRAN 4.", 1)[0]
    for figure_id in ("evidence_process_asset", "evidence_process_blender"):
        assert body.count(f"[FIGURE:{figure_id}]") == 1
        assert appendix_three.count(f"[FIGURE:{figure_id}]") == 0


def test_sql_artifacts_are_preserved_with_expected_hashes():
    expected = {
        "001_full_setup.sql": (
            "B440C517FC0289CBD6F546B4A3ED12D2ADC8E7B9F6CB8181F4FFF5A96681E61B"
        ),
        "002_seed_data.sql": (
            "2A2BF7A97A566B75546C29D8FE3025EB0D9C4F682BF49BE2E323D603E1D57B2F"
        ),
    }
    for name, digest in expected.items():
        data = (ROOT / "dokumentasi" / "sql" / name).read_bytes()
        assert hashlib.sha256(data).hexdigest().upper() == digest


def test_prototyping_diagram_is_sequential_not_forked():
    source = (
        ROOT / "diagrams" / "gambar-2.10-tahap-pengembangan.puml"
    ).read_text(encoding="utf-8")
    assert "\nfork\n" not in source
    phrases = [
        "Merancang ERD",
        "kebutuhan kebijakan RLS",
        "Membuat struktur database",
        "Membuat bentuk, lantai",
        "kelompok Pointer",
        "kode lokasi pada data",
        "alat pemeriksa",
    ]
    positions = [source.index(phrase) for phrase in phrases]
    assert positions == sorted(positions)


def test_uat_revision_explains_the_four_2d_map_tables():
    revision = (
        ROOT / "content" / "shared" / "testing" / "uat-revisions.md"
    ).read_text(encoding="utf-8")
    for table in (
        "campus_maps",
        "campus_map_nodes",
        "campus_map_edges",
        "campus_map_building_points",
    ):
        assert f"`{table}`" in revision
    assert "UAT-R03 dan UAT-R07" in revision
    assert "kebijakan baca untuk pengguna publik" in revision
    assert "pengelolaan bagi pengguna terautentikasi" in revision
