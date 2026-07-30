"""Regression tests for Iman's role and cross-system integration contract."""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROLE = "Full Stack Web Developer, System Integrator, dan DevOps Engineer"


def _read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _numbered_items(section):
    return [
        match.group(1).strip()
        for match in re.finditer(r"(?m)^\d+\.\s+(.+)$", section)
    ]


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


def test_background_problem_objective_benefit_and_conclusion_chain_is_preserved():
    background = _read("content/shared/bab1/latar-belakang-umum.md")
    draft = _read("Tugas_Akhir_Draft.md")
    identification = draft.split("## 1.2 Identifikasi Masalah", 1)[1].split(
        "## 1.3 Batasan Masalah", 1
    )[0]
    objectives = draft.split("### 1.4.1 Tujuan", 1)[1].split(
        "### 1.4.2 Manfaat", 1
    )[0]
    benefits = draft.split("### 1.4.2 Manfaat", 1)[1].split(
        "## 1.5 Jadwal Kegiatan", 1
    )[0]
    conclusions = draft.split("## 4.1 Kesimpulan", 1)[1].split(
        "## 4.2 Saran", 1
    )[0]

    assert _numbered_items(identification) == [
        "Pengguna sasaran, yaitu sivitas akademika seperti mahasiswa, dosen, dan tenaga kependidikan serta pengunjung eksternal seperti calon mahasiswa, orang tua atau wali mahasiswa, dan tamu kampus, masih dapat mengalami kesulitan menemukan gedung atau fasilitas. Pada sampel kebutuhan awal, 14 dari 21 responden pernah mengalami kesulitan setidaknya satu kali dalam satu semester dan 90,5 persen responden paling sering meminta bantuan orang lain ketika mencari lokasi.",
        "Informasi gedung atau fasilitas, pencarian tujuan, dan panduan spasial belum terhubung dalam satu alur web pada ruang lingkup produk yang dikembangkan. Pengguna memerlukan pilihan panduan Denah 2D atau Denah 3D agar dapat memilih cara navigasi sesuai tingkat pengenalan kampus dan pengalaman menggunakan navigasi digital.",
        "Pengelola sistem memerlukan cara yang terkendali untuk memperbarui informasi gedung, fasilitas, dan tujuan navigasi. Informasi yang diperbarui perlu digunakan secara konsisten oleh Dashboard Publik, pencarian lokasi, Denah 2D, dan Denah 3D agar pengguna tidak menerima tujuan atau keterangan yang berbeda antarkomponen.",
    ]
    assert "disertai petunjuk penggunaan" not in identification

    assert _numbered_items(objectives) == [
        "Mengembangkan Dashboard Publik berbasis web yang membantu sivitas akademika dan pengunjung eksternal memperoleh informasi serta menemukan gedung atau fasilitas di Kampus Pondok Labu.",
        "Menghubungkan pencarian tujuan dengan panduan spasial melalui perhitungan rute pada Denah 2D dan pengiriman tujuan ke Denah 3D, sehingga pengguna dapat memilih cara navigasi yang sesuai dan memperoleh umpan balik ketika tujuan tercapai.",
        "Mengembangkan Panel Admin dan mekanisme integrasi data yang memungkinkan administrator memperbarui informasi melalui akses terkendali serta menjaga konsistensi data pada Dashboard Publik, pencarian, Denah 2D, dan Denah 3D.",
    ]

    assert _numbered_items(benefits) == [
        "Bagi sivitas akademika dan pengunjung eksternal, aplikasi menyediakan satu tempat untuk menelusuri informasi kampus, mencari gedung atau fasilitas, dan membuka denah virtual melalui browser.",
        "Bagi staf pengelola, Panel Admin menyediakan antarmuka untuk memperbarui konten sesuai hak akses tanpa mengubah kode aplikasi maupun file hasil build Unity selama kode lokasi tetap konsisten.",
        "Bagi Humas UPNVJ sebagai mitra pengguna, sistem yang dikembangkan dapat dievaluasi sebagai media informasi dan navigasi untuk membantu mahasiswa baru, orang tua atau wali, sivitas akademika, dan pengunjung eksternal.",
        "Bagi UPA TIK dan tim pengembang, REST API, penghubung React–Unity, serta konfigurasi deployment menyediakan spesifikasi teknis yang terdokumentasi dan dapat disesuaikan apabila sistem memperoleh persetujuan untuk dipindahkan ke infrastruktur institusi.",
    ]

    chain = [
        (
            "Empat belas responden atau 66,7 persen",
            "kesulitan menemukan gedung atau fasilitas",
            "membantu sivitas akademika dan pengunjung eksternal memperoleh informasi",
            "Menjawab kesulitan pengguna dalam memperoleh informasi dan menemukan lokasi",
        ),
        (
            "belum terhubungnya informasi gedung atau fasilitas, pencarian tujuan, dan panduan spasial",
            "pencarian tujuan, dan panduan spasial belum terhubung",
            "Menghubungkan pencarian tujuan dengan panduan spasial",
            "Menjawab kebutuhan akan alur yang menghubungkan pencarian dengan panduan spasial",
        ),
        (
            "diperbarui melalui akses yang terkendali",
            "cara yang terkendali untuk memperbarui informasi",
            "Panel Admin dan mekanisme integrasi data",
            "Menjawab kebutuhan pengelolaan informasi yang terkendali dan konsisten",
        ),
    ]
    for background_anchor, problem_anchor, objective_anchor, conclusion_anchor in chain:
        assert background_anchor in background
        assert problem_anchor in identification
        assert objective_anchor in objectives
        assert conclusion_anchor in conclusions

    conclusion_items = _numbered_items(conclusions)
    assert len(conclusion_items) == 4
    assert conclusion_items[-1] == (
        "Sebagai hasil tindak lanjut UAT dalam lingkup kontribusi penulis, "
        "perbaikan telah diterapkan pada pencarian React, Tutorial dan FAQ "
        "Denah 2D serta Denah 3D, pemilih mode dan Denah 2D, bantuan pada "
        "antarmuka web, serta validasi notifikasi kedatangan dari Unity ke "
        "React. Perbaikan tersebut diperiksa melalui kode sumber, sebelas "
        "pengujian otomatis React, sumber resmi, dan tangkapan layar aplikasi. "
        "Pemeriksaan pascaperbaikan ini bukan UAT ulang sehingga tidak "
        "mengubah nilai UAT awal sebesar 81,50 persen."
    )


def test_prototype_terms_only_describe_method_or_verbatim_sources():
    background = _read("content/shared/bab1/latar-belakang-umum.md")
    interview = _read("content/shared/bab2/wawancara-dan-implikasi-kebutuhan.md")
    draft = _read("Tugas_Akhir_Draft.md")
    methodology = draft.split("### 2.3.1 Rencana Pengembangan", 1)[1].split(
        "### 2.3.2 Perancangan Arsitektur Informasi", 1
    )[0]
    diagram = _read("diagrams/gambar-2.10-tahap-pengembangan.puml")

    assert not re.search(r"(?i)prototip|prototyp|purwarupa", background)
    assert not re.search(r"(?i)prototip|prototyp|purwarupa", interview)

    forbidden_product_phrases = [
        "Pengelola prototipe",
        "Prototipe menggunakan layanan proyek",
        "prototipe media informasi",
        "aset yang digunakan prototipe",
        "menghasilkan prototipe terintegrasi",
        "Prototipe terintegrasi dievaluasi",
        "judul prototipe saat pengujian",
    ]
    for phrase in forbidden_product_phrases:
        assert phrase not in draft

    assert "Metodologi penelitian dan pengembangan yang digunakan pada proyek ini adalah Prototyping" in methodology
    assert "Metode prototyping bersifat iteratif" in methodology
    assert "purwarupa yang dapat diperiksa dan diperbaiki" in methodology
    assert "3. Pembangunan Prototipe" in methodology
    assert "4. Evaluasi Prototipe" in methodology
    assert "Pemanfaatan metode prototype dalam perancangan sistem informasi" in draft

    assert "3. Pembangunan Prototipe per Peran" in diagram
    assert "4. Integrasi dan Evaluasi Prototipe" in diagram
    assert "Sistem terintegrasi setelah evaluasi dan perbaikan" in diagram
    assert "Prototipe terintegrasi siap dirilis" not in diagram

    assert "Pengguna memerlukan pilihan panduan Denah 2D atau Denah 3D" in draft
    assert "Perubahan tersebut juga perlu digunakan secara konsisten oleh informasi publik, pencarian lokasi, Denah 2D, dan Denah 3D" in background


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

    assert "FE -> Auth : Mengirim kredensial" in diagram
    assert "Backend API" not in diagram
    assert "FE -> API" not in diagram
    assert "antarmuka React mengirim kredensial langsung ke Supabase Auth" in draft


def test_runtime_and_editor_endpoints_remain_distinct():
    draft = _read("Tugas_Akhir_Draft.md")

    assert "`GET /api/unity/data`" in draft
    assert "Layanan `/api/unity/names` digunakan oleh alat pemeriksaan sinkronisasi pada Unity Editor" in draft
    assert "React tidak mengirimkan data JSON ke Unity" in draft
    assert "Unity mengirim notifikasi kedatangan (`OnNavigationCompleted`) beserta kode lokasi" in draft
    assert "React belum memasang listener" not in draft


def test_latest_web_snapshot_is_not_described_with_deprecated_paths():
    draft = _read("Tugas_Akhir_Draft.md")

    bab_ii_and_iii = draft.split("# BAB II", 1)[1].split("# BAB IV", 1)[0]
    assert "loader bawaan Unity" in bab_ii_and_iii
    assert "tanpa pustaka `react-unity-webgl`" in bab_ii_and_iii
    assert "Analitik utama" in bab_ii_and_iii
    assert "Playwright | Belum tersedia sebagai rangkaian hasil" in bab_ii_and_iii


def test_architecture_diagram_matches_active_data_paths():
    diagram = _read("diagrams/gambar-2.09-arsitektur-sistem.puml")

    assert "React --> Supabase : Autentikasi dan pengelolaan data" in diagram
    assert "UnityCanvas --> Serverless : Ambil data lokasi\\nGET /api/unity/data" in diagram
    assert "React --> Serverless" not in diagram
    assert "Notifikasi kedatangan" in diagram
    assert "kode lokasi Unity" in diagram
    assert "OnNavigationCompleted" not in diagram
    assert "unity_object_name" not in diagram
    assert "tersedia, belum dikonsumsi" not in diagram
    assert 'rectangle "Layanan Opsional"' in diagram
    assert "React ..> Express : Jalur analitik opsional" in diagram
    assert "Express --> Supabase" not in diagram


def test_use_case_and_activity_diagrams_match_current_ui_and_integration():
    use_case = _read("diagrams/gambar-2.12-use-case-diagram.puml")
    admin_activity = _read("diagrams/gambar-2.13-activity-pengelolaan-data-admin.puml")
    integration_activity = _read("diagrams/gambar-2.14-activity-integrasi-data-denah.puml")

    assert "Akreditasi" not in use_case
    assert "Kelola Data Fakultas" not in use_case
    assert "Mengakses Data" in use_case
    assert "Gedung dan Fasilitas" in use_case
    assert "GET /api/unity/data" not in use_case
    assert "GET /api/unity/names" not in use_case
    assert "OnNavigationCompleted" not in use_case
    assert "Mengirim kredensial" in admin_activity
    assert "Trigger menulis Audit Log" not in admin_activity
    assert "Mencatat riwayat melalui" in admin_activity
    assert "Skenario A" not in integration_activity
    assert "Menghitung rute A*" in integration_activity
    assert "Memvalidasi tujuan aktif" in integration_activity
    assert "activeNavigationRef" not in integration_activity


def test_active_uml_uses_academic_labels_and_times_new_roman():
    active_diagrams = [
        "diagrams/gambar-2.09-arsitektur-sistem.puml",
        "diagrams/gambar-2.10-tahap-pengembangan.puml",
        "diagrams/gambar-2.11-legenda-use-case.puml",
        "diagrams/gambar-2.12-use-case-diagram.puml",
        "diagrams/gambar-2.13-activity-pengelolaan-data-admin.puml",
        "diagrams/gambar-2.14-activity-integrasi-data-denah.puml",
        "diagrams/gambar-2.15-sequence-autentikasi-admin.puml",
        "diagrams/gambar-2.16-sequence-sinkronisasi-data-unity.puml",
    ]
    forbidden_internal_labels = {
        "Segoe UI",
        "activeNavigationRef",
        "CompleteNavigation",
        "signInWithPassword",
        "realNames",
        "isLoaded",
        "stopDistance",
    }

    for path in active_diagrams:
        diagram = _read(path)
        assert 'skinparam defaultFontName "Times New Roman"' in diagram
        for label in forbidden_internal_labels:
            assert label not in diagram


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
    assert "Smartphone | 86/100 | 100/100 | 100/100 | 100/100" in draft
    assert "pengujian lokal dengan kondisi yang disimulasikan" in draft


def test_database_and_unity_ownership_are_not_attributed_to_iman():
    facts = json.loads(_read("project_facts.json"))
    pointer = facts["integration_pointer_and_sync"]["pointer_mechanism"]["description"]
    sync_checker = facts["integration_pointer_and_sync"]["database_sync_checker"]["description"]

    assert pointer.startswith("Muhammad Dwikhi Deandra Purnianto menata hierarchy prefab")
    assert "dikembangkan Muammar Faiz Khairul Anam Setiawan" in sync_checker


def test_code_appendix_contains_only_iman_owned_integration_evidence():
    draft = _read("Tugas_Akhir_Draft.md")
    appendix = draft.split("# LAMPIRAN 2. Kode Sumber Utama", 1)[1].split(
        "# LAMPIRAN 3.", 1
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
    handoff = draft.split("## C. Prosedur Serah Terima Data, File Hasil Build Unity, dan Deployment", 1)[1]

    assert "Tools > UPNVJ > Check Database Sync" not in handoff
    assert "Window > AI > Navigation" not in handoff
    assert "3D Simulator dan Engine Developer mengelola aplikasi Unity, NavMesh, alat bantu editor, optimasi" in handoff
    assert "File hasil build ditempatkan pada folder versi" in handoff


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
        "uat_revisi_notifikasi_tiba",
        "blackbox_bb20_rute_aktif",
        "blackbox_bb20_navigasi_selesai",
    }

    for image_id in core_ui | revision_evidence:
        assert draft.count(f"[FIGURE:{image_id}]") == 1
        assert draft.count(f"[FIGREF:{image_id}]") >= 1
    assert "RR03_pilih_spawn_2d.png" not in draft
    assert "screenshot Lighthouse" not in draft


def test_uat_follow_up_is_composed_from_iman_role_scope():
    draft = _read("Tugas_Akhir_Draft.md")
    role_revision = _read("content/roles/iman/uat-revisions.md")

    assert "<!-- PIPELINE:INCLUDE content/roles/iman/uat-revisions.md -->" in draft
    assert "<!-- PIPELINE:INCLUDE content/shared/testing/uat-revisions.md -->" not in draft
    assert "Denah 2D berbasis React" in role_revision
    assert "penghubung notifikasi kedatangan dari Unity ke React" in role_revision
    assert "[FIGURE:uat_revisi_spawn_3d]" not in draft
    assert "[FIGURE:uat_revisi_minimap_3d]" not in draft


def test_use_case_has_only_human_actors_and_shared_location_information():
    puml = _read("diagrams/gambar-2.12-use-case-diagram.puml")
    actor_lines = [
        line.strip()
        for line in puml.splitlines()
        if line.strip().startswith("actor ")
    ]

    assert len(actor_lines) == 2
    assert any('"Pengguna Publik"' in line for line in actor_lines)
    assert any('"Administrator"' in line for line in actor_lines)
    assert "Denah 3D\\nUnity WebGL" not in puml
    assert "Alat Pemeriksaan\\npada Unity Editor" not in puml
    assert "Mengakses Data\\nGedung dan Fasilitas" in puml
    assert "UC5 --> UCData : <<include>>" in puml
    assert "UC5 ..> UCData" not in puml
    assert puml.count("<<include>>") == 1
    assert "skinparam linetype ortho" in puml


def test_closed_uat_forms_and_administrative_letters_are_placed_in_appendices():
    draft = _read("Tugas_Akhir_Draft.md")
    manifest = json.loads(_read("images/manifest.json"))
    images = {entry["id"]: entry for entry in manifest["images"]}

    uat_form_ids = {
        "uat_closed_penguji_2_p1",
        "uat_closed_penguji_2_p2",
        "uat_closed_pembimbing_2_p1",
        "uat_closed_pembimbing_2_p2",
        "uat_closed_pembimbing_2_p3",
        "uat_closed_pembimbing_2_p4",
        "uat_closed_pembimbing_1_p1",
        "uat_closed_pembimbing_1_p2",
        "uat_closed_pembimbing_1_p3",
        "uat_closed_pembimbing_1_p4",
        "uat_closed_humas_p1",
        "uat_closed_humas_p2",
        "uat_closed_humas_p3",
        "uat_closed_humas_p4",
        "uat_closed_penguji_1_p1",
        "uat_closed_penguji_1_p2",
        "uat_closed_penguji_1_p3",
        "uat_closed_penguji_1_p4",
    }
    administrative_ids = {
        "admin_research_request_jan_2026",
        "admin_research_disposition_feb_2026",
        "admin_research_request_jul_2026",
        "admin_research_disposition_jul_2026",
        "admin_uat_request_jul_2026",
        "admin_uat_invitation_jul_2026_p1",
        "admin_uat_invitation_jul_2026_p2",
    }

    appendix_4 = draft.split(
        "# LAMPIRAN 4. Instrumen UAT Tertutup dan Indeks Bukti Pengujian", 1
    )[1].split("# LAMPIRAN 5.", 1)[0]
    appendix_6 = draft.split(
        "# LAMPIRAN 6. Dokumen Administratif Penelitian dan Pelaksanaan UAT", 1
    )[1]

    for image_id in uat_form_ids:
        assert image_id in images
        assert appendix_4.count(f"[FIGURE:{image_id}]") == 1
        assert appendix_4.count(f"[FIGREF:{image_id}]") >= 1
    for image_id in administrative_ids:
        assert image_id in images
        assert appendix_6.count(f"[FIGURE:{image_id}]") == 1
        assert appendix_6.count(f"[FIGREF:{image_id}]") >= 1

    appendix_1 = draft.split(
        "# LAMPIRAN 1. Dokumentasi Penyerahan Pakta Integritas kepada UPA TIK", 1
    )[1].split("# LAMPIRAN 2.", 1)[0]
    pakta_example = images["contoh_pakta_integritas_anggota_tim"]
    assert pakta_example["source"].endswith("surat_pakta_integritas_mahasiswa.jpeg")
    assert appendix_1.count("[FIGURE:contoh_pakta_integritas_anggota_tim]") == 1
    assert appendix_1.count("[FIGREF:contoh_pakta_integritas_anggota_tim]") >= 1
    assert "bukan milik penulis" in appendix_1
    assert "tidak digunakan sebagai bukti" in appendix_1
    assert "lembar_disposisi_halaman_2.jpg" not in {
        entry["source"] for entry in manifest["images"]
    }


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
    assert "pembersihan berkas data awal menghasilkan 311 data" in draft
    assert "berkas akhir belum terbukti diterapkan kembali" in draft
    assert "tangkapan layar pencarian tidak digunakan untuk menyatakan bahwa penambahan kata pencarian pada R01" in draft
