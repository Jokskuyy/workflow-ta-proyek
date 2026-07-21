# Laporan TA — Muammar Faiz Khairul Anam (3D Simulator dan Engine Developer)

**Branch:** `laporan/faiz` — tulis laporan di `Tugas_Akhir_Draft.md` (root repo) saat berada di branch ini.

## Fokus / Lingkup Laporan
Berdasarkan pembagian peran, kontribusi:
1. **Sistem Navigasi Spasial** — NavMesh pathfinding lintas gedung dan multi-lantai (`NavigationGuide`, `NavigationReceiver`).
2. **Rendering Rute Visual** — subdivisi linear titik `NavMeshPath`, raycast vertikal, dan moving average; label nama tujuan dan jarak.
3. **Optimasi Runtime dan Build** — **Building Culling** berbasis jarak dan frustum, konfigurasi occlusion culling, serta **WebGL Settings Optimizer** (Brotli, IL2CPP, stripping). Dampak performa kuantitatif tetap menunggu benchmark yang terdokumentasi.
4. **Kontrol dan Interaksi** — **Pointer Lock** dan **joystick virtual** mobile.
5. **Konsumsi Data Engine** — `BuildingDatabase` menarik data via `HTTP GET /api/unity/data`.
6. **Editor Tool** — **DatabaseSyncChecker** (validasi `unity_object_name` DB vs scene) dan **CampusOcclusionInstaller** (konfigurasi serta bake occlusion scene).
7. **Orientasi Pengguna** — pemilihan spawn, minimap, penanda tujuan, dan tutorial adaptif desktop/mobile.
8. **Kontrak Penyelesaian Navigasi** — pengiriman event `OnNavigationCompleted` dengan payload `unity_object_name` ketika path lengkap dan ambang kedatangan efektif maksimal 2 m tercapai; penghentian manual tidak dianggap sebagai kedatangan.

> Ruang lingkup: logika *engine* dan *runtime* Unity. Dwikhi menangani ERD, skema, RLS, trigger, data dan pemetaan, serta aset 3D. Iman menangani React, REST API, integrasi Supabase, listener sisi React, deployment Vercel, dan pengujian web.

## Diagram Relevan
- **2.14 Activity: Integrasi Data Denah**
- **2.16 Sequence: Sinkronisasi Data & Unity**
- **3.1 Hierarki Prefab Gedung (Pointer)**
- **3.2 UI Database Sync Checker**
- **2.9 Arsitektur Sistem** *(konteks bersama)*
- Sumber diagram: `../../diagrams/`.

## Yang Perlu Ditambahkan Sendiri
- Diagram alur algoritma pathfinding (`NavMesh.SamplePosition` → `NavMesh.CalculatePath` → subdivisi linear → raycast → moving average → `LineRenderer`).
- Benchmark Building Culling menggunakan Unity Profiler pada posisi, durasi, dan lintasan yang sama. Capture NVIDIA Statistics Overlay yang sudah diterima dipakai sebagai bukti runtime pendahuluan, tetapi belum memenuhi syarat pembandingan performa kuantitatif.
- Rekaman Pointer Lock dan joystick mobile karena tangkapan layar diam hanya membuktikan tata letak.
- Log `SetDevice`, rekaman tutorial/kontrol lintas perangkat, serta log pengiriman `OnNavigationCompleted` dan pengujian ulang pembatalan manual. Tangkapan layar notifikasi React tidak digunakan karena bukan kontribusi Faiz.

### Jika perlu mengambil tangkapan layar override spawn

Override bukan *field* umum di bagian bawah Inspector. Pilih GameObject yang memuat `SpawnReceiver`, lalu pada komponen `Spawn Point Registry (Script)` buka *foldout* `Spawn Points` dengan mengeklik segitiga di sebelah kiri daftar. Buka elemen yang memiliki `Unity Object Name` `cipto_mangunkusumo`, `gerbang_belakang`, atau `gerbang_belakang2`; *field* yang dicari bernama `Nav Mesh Sample Radius Override` dan nilainya harus berturut-turut 120, 40, dan 40. Tangkapan layar detail tersebut sudah tersedia sebagai `konfigurasi_spawn_registry_override.png`; jika perlu mengambil ulang, lebarkan Inspector atau gunakan pencarian properti agar ketiga elemen dan nilainya terlihat.

## Baseline Implementasi Aktif
- Baseline historis: `C:\Users\Faiz\Proposal`, Unity `6000.2.6f1`.
- Implementasi final: `C:\Users\Faiz\Proposal\T_A---Copy`, Unity `6000.4.1f1` (revision `336a400b9ea2`), scene `Assets/Scene/SceneUtama.unity`, commit acuan `5f575c0`.
- Perkembangan final yang relevan mencakup `0d90ecb` (camera-aware culling), `7c630f0` (occlusion dan transisi spawn), `1845c65` (pemisahan event tiba dan pembatalan), `968d067` (hardening routing dan replay tutorial), `f82f465` (aktivasi kontrol dari selector spawn), serta `5f575c0` (routing final dan exception WebGL).
- Bukti occlusion menggunakan `MainCamera` aktif dan `MinimapCamera` nonaktif; kamera lain tidak dipersyaratkan sebagai bukti.
- Player Settings final menggunakan `Explicitly Thrown Exceptions Only` bersama WebAssembly 2023, sesuai konfigurasi yang diterapkan `WebGLOptimizer`.
- Fungsi *helper* Catmull-Rom masih terdapat pada skrip historis, tetapi tidak dipanggil oleh alur rendering final dan tidak boleh diklaim sebagai implementasi aktif.

## Acuan
- Kontrak konten bersama dan include: `../../content/README.md`
- PRD (bagian "Modul Unity (C#)", "Build & Performa WebGL", "Testing Decisions"): `../../PRD_Konsolidasi_TA.md`
- Kerangka laporan: `outline-laporan.md`
- Kode Unity: repo eksternal (lihat `../../PANDUAN-TIM.md`).
