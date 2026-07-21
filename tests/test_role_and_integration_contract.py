"""Regression tests for Iman's role and cross-system integration contract."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROLE = "Full Stack Web Developer, System Integrator, dan DevOps Engineer"


def _read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_role_label_is_synced_across_canonical_sources():
    facts = json.loads(_read("project_facts.json"))
    iman = next(member for member in facts["team_members"]
                if member["name"] == "Muhammad Iman Nugraha")

    assert iman["role"] == f"Peran 1: {ROLE}"
    assert ROLE in _read("Tugas_Akhir_Draft.md")
    assert ROLE in _read("laporan-tim/iman-fullstack-integrator/README.md")
    assert ROLE in _read("laporan-tim/README.md")
    assert ROLE in _read("PANDUAN-TIM.md")
    assert ROLE in _read(".kiro/steering/konteks-proyek.md")


def test_humas_is_user_partner_and_upa_tik_is_technical_coordination():
    facts = json.loads(_read("project_facts.json"))
    draft = _read("Tugas_Akhir_Draft.md")

    assert facts["project_metadata"]["mitra"]["name"] == "Humas UPNVJ"
    assert facts["project_metadata"]["mitra"]["role"] == "Mitra pengguna dan peserta UAT"
    upa_tik = facts["project_metadata"]["institutional_coordination"]["upa_tik"]
    assert "Koordinasi teknis" in upa_tik["role"]
    assert "Humas Universitas Pembangunan Nasional" in draft
    assert "UPA TIK tetap dicatat secara terpisah sebagai pihak koordinasi teknis" in draft
    assert "tidak digunakan untuk mengklaim persetujuan formal" in draft
    assert "Dokumentasi Penyerahan Pakta Integritas kepada UPA TIK" in draft


def test_authentication_sequence_calls_supabase_auth_directly():
    diagram = _read("diagrams/gambar-2.15-sequence-autentikasi-admin.puml")
    draft = _read("Tugas_Akhir_Draft.md")

    assert "FE -> Auth : signInWithPassword(kredensial)" in diagram
    assert "Backend API" not in diagram
    assert "FE -> API" not in diagram
    assert "frontend React langsung ke Supabase Auth" in draft


def test_runtime_and_editor_endpoints_remain_distinct():
    draft = _read("Tugas_Akhir_Draft.md")

    assert "`GET /api/unity/data`" in draft
    assert "Endpoint `/api/unity/names` digunakan oleh `DatabaseSyncChecker` pada Unity Editor" in draft
    assert "React tidak mengirimkan data JSON ke Unity" in draft
    assert "Unity mengirim pemberitahuan `OnNavigationCompleted` beserta kode lokasi" in draft
    assert "React belum memasang listener" not in draft


def test_latest_web_snapshot_is_not_described_with_deprecated_paths():
    draft = _read("Tugas_Akhir_Draft.md")

    bab_ii_and_iii = draft.split("# BAB II", 1)[1].split("# BAB IV", 1)[0]
    assert "loader native Unity" in bab_ii_and_iii
    assert "tanpa dependency `react-unity-webgl`" in bab_ii_and_iii
    assert "Jalur analitik aktif" in bab_ii_and_iii
    assert "Playwright | Belum tersedia sebagai suite hasil" in bab_ii_and_iii


def test_architecture_diagram_matches_active_data_paths():
    diagram = _read("diagrams/gambar-2.09-arsitektur-sistem.puml")

    assert "React --> Supabase : Auth, query, CRUD, analitik" in diagram
    assert "UnityCanvas --> Serverless : HTTP GET /api/unity/data" in diagram
    assert "React --> Serverless" not in diagram
    assert "OnNavigationCompleted" in diagram
    assert "JSON unity_object_name" in diagram
    assert "tersedia, belum dikonsumsi" not in diagram
    assert 'rectangle "Layanan Operasional Opsional"' in diagram
    assert "React ..> Express : jalur analitik opsional" in diagram
    assert "Express --> Supabase" not in diagram


def test_use_case_and_activity_diagrams_match_current_ui_and_integration():
    use_case = _read("diagrams/gambar-2.12-use-case-diagram.puml")
    admin_activity = _read("diagrams/gambar-2.13-activity-pengelolaan-data-admin.puml")
    integration_activity = _read("diagrams/gambar-2.14-activity-integrasi-data-denah.puml")

    assert "Akreditasi" not in use_case
    assert "Kelola Data Fakultas" not in use_case
    assert "GET /api/unity/data" in use_case
    assert "GET /api/unity/names" in use_case
    assert "OnNavigationCompleted" in use_case
    assert "Kirim kredensial langsung ke Supabase Auth" in admin_activity
    assert "Trigger menulis Audit Log" not in admin_activity
    assert "service pencatatan audit aplikasi" in admin_activity
    assert "Skenario A" not in integration_activity
    assert "Hitung rute A*" in integration_activity
    assert "activeNavigationRef" in integration_activity


def test_navigation_completion_contract_is_active_and_target_validated():
    facts = json.loads(_read("project_facts.json"))
    draft = _read("Tugas_Akhir_Draft.md")
    snapshot = facts["web_implementation_snapshot"]
    verification = facts["testing_status"]["web_repository_verification"]

    assert snapshot["web_commit"] == "08ebc06"
    assert snapshot["current_web_commit"] == "08ebc06"
    assert snapshot["initial_navigation_completion_commit"] == "b572a48"
    assert snapshot["navigation_completion_followup_commit"] == "d2e8fdb"
    assert snapshot["unity_commit"] == "1845c65"
    assert verification["commit"] == "08ebc06"
    assert verification["results"]["vitest_test_files"] == 13
    assert verification["results"]["vitest_tests_passed"] == 129
    assert verification["results"]["navigation_completion_tests"] == 11
    assert "menyertakan unity_object_name" in snapshot["callback_status"]
    assert "tujuan aktif" in snapshot["callback_status"]
    assert 'type NavigationCompletedPayload = {' in draft
    listener_start = draft.index("window.addEventListener(")
    assert '"OnNavigationCompleted"' in draft[listener_start:listener_start + 150]
    assert "completedKey !== selectedKey" in draft
    assert "setHasReachedDestination(true)" in draft
    assert "setelah pembatalan diabaikan" in draft


def test_latest_lighthouse_audit_replaces_obsolete_baseline():
    facts = json.loads(_read("project_facts.json"))
    lighthouse = facts["testing_status"]["lighthouse_testing"]
    draft = _read("Tugas_Akhir_Draft.md")

    assert lighthouse["commit"] == "bdeb5bc"
    assert lighthouse["category_scores"]["mobile"]["performance"] == 86
    assert lighthouse["category_scores"]["desktop"]["performance"] == 99
    assert lighthouse["metrics"]["mobile"]["largest_contentful_paint_ms"] == 3681
    assert "Performance | 56/100" not in draft
    assert "Mobile | 86/100 | 100/100 | 100/100 | 100/100" in draft
    assert "pengujian lokal dengan kondisi yang disimulasikan" in draft


def test_database_and_unity_ownership_are_not_attributed_to_iman():
    facts = json.loads(_read("project_facts.json"))
    pointer = facts["integration_pointer_and_sync"]["pointer_mechanism"]["description"]
    sync_checker = facts["integration_pointer_and_sync"]["database_sync_checker"]["description"]

    assert pointer.startswith("Muhammad Dwikhi Deandra Purnianto menata hierarchy prefab")
    assert "dikembangkan Muammar Faiz Khairul Anam" in sync_checker


def test_code_appendix_contains_only_iman_owned_integration_evidence():
    draft = _read("Tugas_Akhir_Draft.md")
    appendix = draft.split("# LAMPIRAN 3. Kode Sumber Utama", 1)[1].split(
        "# LAMPIRAN 4.", 1
    )[0]

    assert "```csharp" not in appendix
    assert "public class DatabaseSyncChecker" not in appendix
    assert "api/unity/data.js" in appendix
    assert "api/unity/names.js" in appendix
    assert "trackingService.ts" in appendix
    assert "vercel.json" in appendix
    assert '"NavigationReceiver"' in appendix


def test_user_manual_keeps_unity_details_as_handoff_contract():
    draft = _read("Tugas_Akhir_Draft.md")
    handoff = draft.split("## C. Kontrak Handoff Data, Artefak Unity, dan Deployment", 1)[1]

    assert "Tools > UPNVJ > Check Database Sync" not in handoff
    assert "Window > AI > Navigation" not in handoff
    assert "Engine Developer mengelola scene, NavMesh, alat bantu editor, optimasi" in handoff
    assert "Artefak ditempatkan pada path versi" in handoff


def test_selected_ui_and_uat_revision_evidence_remains_curated():
    draft = _read("Tugas_Akhir_Draft.md")
    core_ui = {
        "ui_section_denah_kampus",
        "ui_webgl_canvas",
        "ui_search_overlay",
        "mockup_dashboard_admin",
        "api_test_health",
        "api_test_unity_data",
        "api_test_unity_names",
        "api_test_rls_unauthorized",
    }
    revision_evidence = {
        "uat_revisi_tutorial_faq",
        "uat_revisi_mode_selector",
        "uat_revisi_map_2d",
        "uat_revisi_spawn_3d",
        "uat_revisi_minimap_3d",
        "uat_revisi_notifikasi_tiba",
        "blackbox_bb20_rute_aktif",
        "blackbox_bb20_navigasi_selesai",
    }

    for image_id in core_ui | revision_evidence:
        assert draft.count(f"[FIGURE:{image_id}]") == 1
        assert draft.count(f"[FIGREF:{image_id}]") >= 1
    assert "RR03_pilih_spawn_2d.png" not in draft
    assert "screenshot Lighthouse" not in draft


def test_api_smoke_evidence_is_role_focused_and_preserves_rls_ownership():
    draft = _read("Tugas_Akhir_Draft.md")

    assert "[TABLE-ID:hasil_pengujian_api_deployment]" in draft
    assert "`GET /api/health`" in draft
    assert "`GET /api/unity/data`" in draft
    assert "`GET /api/unity/names`" in draft
    assert "HTTP 401; kode PostgreSQL `42501`" in draft
    assert "rancangan policy RLS tetap merupakan kontribusi Database Schema Designer" in draft
    assert "pemeriksaan dasar secara manual" in draft


def test_frontend_screenshots_use_current_deployment_and_preserve_live_data_limit():
    draft = _read("Tugas_Akhir_Draft.md")
    manifest = json.loads(_read("images/manifest.json"))
    images = {entry["id"]: entry for entry in manifest["images"]}

    expected_sources = {
        "ui_section_denah_kampus": "dokumentasi/frontend-terbaru/section-denah-kampus.png",
        "ui_webgl_canvas": "dokumentasi/frontend-terbaru/canvas-webgl-3d.png",
        "ui_search_overlay": "dokumentasi/frontend-terbaru/search-overlay-2d.png",
        "mockup_dashboard_admin": "dokumentasi/frontend-terbaru/admin-fasilitas.png",
    }
    for image_id, source in expected_sources.items():
        assert images[image_id]["source"] == source

    assert "331 fasilitas pada database Supabase aktif" in draft
    assert "pembersihan berkas seed menghasilkan 311 data" in draft
    assert "seed final belum terbukti telah diterapkan kembali" in draft
    assert "tangkapan layar pencarian tidak digunakan untuk menyatakan bahwa penambahan kata pencarian pada R01" in draft
