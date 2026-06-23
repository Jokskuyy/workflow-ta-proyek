# Kerangka Laporan TA — Faiz (3D Simulator & Engine Developer)

> Format TA prototipe (4 bab). BAB I dan observasi (2.1) sebagian besar **sama** untuk semua anggota; penekanan berbeda mulai dari usulan solusi & implementasi engine.

## BAB I PENDAHULUAN
- 1.1 Latar Belakang *(bersama)*
- 1.2 Identifikasi Masalah *(tekankan: belum ada navigasi 3D interaktif & terpandu)*
- 1.3 Batasan Masalah *(fokus: logika navigasi, rendering rute, optimasi WebGL, kontrol)*
- 1.4 Tujuan dan Manfaat (1.4.1 Tujuan, 1.4.2 Manfaat)
- 1.5 Jadwal Kegiatan
- 1.6 Sistematika Penulisan

## BAB II RANCANGAN PROYEK
- 2.1 Observasi *(bersama)* — 2.1.1 Observasi Lapangan; 2.1.2 Analisis Sistem Berjalan; 2.1.3 Wawancara Stakeholder
- 2.2 Usulan Solusi
  - 2.2.1 Kebutuhan Fungsional *(navigasi otomatis, rute visual, jarak, joystick mobile)*
  - 2.2.2 Kebutuhan Teknis *(Unity 6 + URP, New Input System, NavMesh, WebGL)*
  - 2.2.3 Kebutuhan Non-Fungsional *(muat < 10 dtk, performa runtime, mobile-first)*
- 2.3 Rancangan Proyek
  - 2.3.1 Rencana Pengembangan *(prototyping)*
  - 2.3.2 Perancangan Sistem Navigasi (NavMesh & Pathfinding)
  - 2.3.3 Perancangan Rendering Rute (Catmull-Rom Centripetal + Raycast)
  - 2.3.4 Perancangan Optimasi Performa (Building Culling & WebGL Build)
  - 2.3.5 Perancangan Kontrol Pengguna (Pointer Lock & Joystick Virtual)
- 2.4 Rencana Pengujian Proyek *(Play Mode Test navigasi; uji performa WebGL; uji editor tool)*

## BAB III IMPLEMENTASI PROYEK
- 3.1 Profil Mitra *(bersama)*
- 3.2 Metode Implementasi
  - 3.2.1 BuildingDatabase (konsumsi /api/unity/data)
  - 3.2.2 NavigationReceiver & NavigationGuide
  - 3.2.3 Rendering Rute (Catmull-Rom + raycast subdivisi)
  - 3.2.4 Building Culling & WebGL Settings Optimizer
  - 3.2.5 Pointer Lock & Joystick Virtual Mobile
  - 3.2.6 Editor Tool: DatabaseSyncChecker
- 3.3 Konfigurasi & Metadata (3.3.1 Konfigurasi Build WebGL; 3.3.2 Konvensi Scene & NavMesh Bake)
- 3.4 Laporan Implementasi (3.4.1 Logbook; 3.4.2 Hasil & Bukti Navigasi; 3.4.3 Hasil & Bukti Optimasi)
- 3.5 Hasil Pengujian (3.5.1 Navigasi/Play Mode; 3.5.2 Performa WebGL; 3.5.3 Editor Tool)

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
- (buat sendiri) Diagram alur pathfinding & rendering rute, ilustrasi Building Culling, screenshot joystick/Pointer Lock

### Acuan
- PRD bagian "Modul Unity (C#)", "Build & Performa WebGL", "Testing Decisions": `../../PRD_Konsolidasi_TA.md`
