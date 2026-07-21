import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DRAFT = (ROOT / "Tugas_Akhir_Draft.md").read_text(encoding="utf-8")
MANIFEST = json.loads((ROOT / "images" / "manifest.json").read_text(encoding="utf-8"))["images"]

ACTIVE_DIAGRAMS = {
    "diagram_arsitektur": "gambar-2.09-arsitektur-sistem.puml",
    "diagram_tahap_pengembangan": "gambar-2.10-tahap-pengembangan.puml",
    "diagram_hierarki_prefab": "gambar-2.11-hierarki-prefab.puml",
    "diagram_sequence_validasi": "gambar-2.16-sequence-sinkronisasi-data-unity.puml",
    "diagram_erd": "gambar-2.17-erd.puml",
}

OBSOLETE_IDS = {
    "diagram_use_case_legenda",
    "diagram_use_case",
    "diagram_activity_kelola_data",
    "diagram_activity_integrasi",
    "diagram_sequence_autentikasi",
    "diagram_sequence_sinkronisasi",
}


def test_dwikhi_bab2_uses_only_five_role_focused_diagrams():
    manifest_ids = {entry["id"] for entry in MANIFEST}
    for diagram_id in ACTIVE_DIAGRAMS:
        assert DRAFT.count(f"[FIGURE:{diagram_id}]") == 1
        assert diagram_id in manifest_ids
    for diagram_id in OBSOLETE_IDS:
        assert f"[FIGURE:{diagram_id}]" not in DRAFT
        assert diagram_id not in manifest_ids


def test_active_plantuml_sources_use_required_contract_and_font():
    combined = []
    for source_name in ACTIVE_DIAGRAMS.values():
        source = (ROOT / "diagrams" / source_name).read_text(encoding="utf-8")
        combined.append(source)
        assert 'defaultFontName "Times New Roman"' in source
        assert not re.search(r"(?im)^\s*title\s+", source)
        assert "Segoe UI" not in source

    all_sources = "\n".join(combined)
    assert "/api/unity/data" in all_sources
    assert "/api/unity/names" in all_sources
    assert "Supabase Auth dan CRUD langsung" in all_sources
    assert "SendMessage" in all_sources
    assert "OnNavigationCompleted" in all_sources
    assert "DatabaseSyncChecker" in all_sources

    banned = (
        "API SIK",
        "data mahasiswa",
        "data dosen",
        "CRUD fakultas",
        "login melalui backend",
        "trigger audit",
        "Skenario A",
        "Skenario B",
        "Skenario C",
    )
    for phrase in banned:
        assert phrase.casefold() not in all_sources.casefold()


def test_erd_contains_only_four_core_tables():
    erd = (ROOT / "diagrams" / ACTIVE_DIAGRAMS["diagram_erd"]).read_text(encoding="utf-8")
    entities = set(re.findall(r'^entity\s+"([^"]+)"', erd, flags=re.MULTILINE))
    assert entities == {"gedung", "fasilitas", "fakultas", "program_studi"}
    assert "admin_users" not in erd
    assert "audit_logs" not in erd


def test_final_draft_has_no_technical_placeholders_or_asset_performance_claims():
    assert "[TBD:" not in DRAFT
    assert "Build Report" not in DRAFT
    assert "Memory Profiler" not in DRAFT
    assert "Performa build" not in DRAFT
    assert "hasil optimasi" not in DRAFT
    assert "Use Case seluruh aplikasi" not in DRAFT
