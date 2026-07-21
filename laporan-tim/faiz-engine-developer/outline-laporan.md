# Kerangka Laporan TA — Faiz (3D Simulator dan Engine Developer)

> Format TA prototipe (4 bab). BAB I dan observasi (2.1) sebagian besar **sama** untuk semua anggota; penekanan berbeda mulai dari usulan solusi dan implementasi *engine*.

## BAB I PENDAHULUAN
- 1.1 Latar Belakang *(bersama)*
- 1.2 Identifikasi Masalah *(tekankan: kebutuhan navigasi 3D interaktif dan terpandu)*
- 1.3 Batasan Masalah *(fokus: logika navigasi, rendering rute, optimasi WebGL, kontrol)*
- 1.4 Tujuan dan Manfaat (1.4.1 Tujuan, 1.4.2 Manfaat)
- 1.5 Jadwal Kegiatan
- 1.6 Sistematika Penulisan

## BAB II RANCANGAN PROYEK
- 2.1 Observasi dan Analisis Kebutuhan Awal *(bersama)* — sumber data dan batas observasi; analisis kebutuhan pengguna dan sistem berjalan; wawancara pemangku kepentingan
- 2.2 Usulan Solusi
  - 2.2.1 Kebutuhan Fungsional *(navigasi otomatis, rute visual, jarak, joystick mobile)*
  - 2.2.2 Kebutuhan Teknis *(Unity 6 + URP, New Input System, NavMesh, WebGL)*
  - 2.2.3 Kebutuhan Non-Fungsional *(pemuatan adaptif, umpan balik pemuatan, performa runtime, dan lintas perangkat)*
- 2.3 Rancangan Proyek
  - 2.3.1 Rencana Pengembangan *(prototyping)*
  - 2.3.2 Perancangan Arsitektur Sistem
  - 2.3.3 Perancangan Aktor dan Batas Interaksi
  - 2.3.4 Perancangan Alur Data dan Sinkronisasi
  - 2.3.5 Perancangan Konsumsi Data dan Lifecycle Engine
  - 2.3.6 Perancangan Sistem Navigasi NavMesh
  - 2.3.7 Perancangan Rendering Rute (subdivisi linear + raycast + moving average)
  - 2.3.8 Perancangan Optimasi Performa (Building Culling berbasis jarak/frustum dan WebGL Build)
  - 2.3.9 Perancangan Kontrol Pengguna (Pointer Lock dan Joystick Virtual)
  - 2.3.10 Perancangan DatabaseSyncChecker
  - 2.3.11 Perancangan Pemilihan Titik Awal dan Minimap
  - 2.3.12 Perancangan Visual Tujuan dan Tutorial Adaptif
  - 2.3.13 Perancangan Occlusion Culling dan Transisi Overview–Gameplay
- 2.4 Rencana Pengujian Proyek
  - 2.4.1 Data dan Integrasi Runtime
  - 2.4.2 Navigasi, Rute, dan Penyelesaian Navigasi
  - 2.4.3 Interaksi, Spawn, Minimap, dan Tutorial
  - 2.4.4 Optimasi, Occlusion Culling, dan Build WebGL

## BAB III IMPLEMENTASI PROYEK
- 3.1 Profil Mitra dan Pemangku Kepentingan *(Humas sebagai mitra pengguna; UPA TIK sebagai koordinasi teknis/institusional)*
- 3.2 Metode Implementasi
  - 3.2.1 BuildingDatabase (konsumsi /api/unity/data)
  - 3.2.2 NavigationReceiver dan NavigationGuide
  - 3.2.3 Rendering Rute (subdivisi linear + raycast + moving average)
  - 3.2.4 Building Culling (jarak/frustum) dan WebGL Settings Optimizer
  - 3.2.5 Pointer Lock dan Joystick Virtual Mobile
  - 3.2.6 Editor Tool: DatabaseSyncChecker
  - 3.2.7 SpawnPointRegistry, SpawnSelectionUI, dan MinimapFollow
  - 3.2.8 DestinationHighlighter dan event OnNavigationCompleted
  - 3.2.9 GameTutorialController, GameTutorialUI, dan WebPlatformSync
  - 3.2.10 CampusOcclusionInstaller dan transisi Overview–Gameplay
- 3.3 Konfigurasi dan Metadata
  - 3.3.1 Konfigurasi Build WebGL
  - 3.3.2 Konvensi Scene dan NavMesh Bake
  - 3.3.3 Konvensi Identitas dan Metadata Tujuan
  - 3.3.4 Konfigurasi Komponen Engine
  - 3.3.5 Konfigurasi Spawn, Minimap, dan Tutorial Lintas Perangkat
  - 3.3.6 Konfigurasi Occlusion Culling dan Transisi Overview–Gameplay
- 3.4 Laporan Implementasi
  - 3.4.1 Logbook; 3.4.2 Navigasi; 3.4.3 Rendering Rute; 3.4.4 Optimasi WebGL
  - 3.4.5 Kontrol; 3.4.6 DatabaseSyncChecker; 3.4.7 Spawn/Minimap/Highlighter/Tutorial
  - 3.4.8 Occlusion dan Transisi; 3.4.9 Batas Kontribusi Penulis
- 3.5 Hasil Pengujian
  - 3.5.1 Black Box Testing *(fragment bersama)*
  - 3.5.2.1–3.5.2.4 pengujian modul Unity: data, navigasi, interaksi, serta optimasi
  - 3.5.3 User Acceptance Test *(fragment bersama)*
  - 3.5.4 Implementasi Hasil User Acceptance Test *(fragment bersama)*
  - 3.5.5 Analisis Kontribusi Faiz terhadap Tindak Lanjut UAT

## BAB IV PENUTUP
- 4.1 Kesimpulan
- 4.2 Saran

---

### Gambar Direkomendasikan
- Arsitektur Sistem (`../../diagrams/gambar-2.09-*`)
- Activity: Integrasi Data Denah (`../../diagrams/gambar-2.14-*`)
- Sequence: Sinkronisasi Data & Unity (`../../diagrams/gambar-2.16-*`)
- Hierarki Prefab Gedung (`../../diagrams/gambar-3.1-*`)
- UI Database Sync Checker (`../../diagrams/gambar-3.2-*`)
- (buat sendiri) Diagram alur pathfinding dan rendering rute, ilustrasi Building Culling/frustum/occlusion, tangkapan layar joystick/Pointer Lock, spawn, minimap, highlighter, tutorial, dan transisi overview

### Acuan
- PRD bagian "Modul Unity (C#)", "Build & Performa WebGL", "Testing Decisions": `../../PRD_Konsolidasi_TA.md`
