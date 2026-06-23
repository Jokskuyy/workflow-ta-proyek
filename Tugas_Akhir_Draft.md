# INTEGRASI DENAH VIRTUAL UNIVERSITAS PEMBANGUNAN NASIONAL VETERAN JAKARTA KAMPUS PONDOK LABU
# (SIMULASI NAVIGASI 3D DAN OPTIMASI ENGINE WEBGL)

Muammar Faiz Khairul Anam

2025

> CATATAN: Ini kerangka awal untuk peran **3D Simulator & Engine Developer**.
> Bagian BAB I dan 2.1 (Observasi) sebagian besar SAMA dengan anggota lain — boleh disalin
> dari branch `laporan/iman` lalu disesuaikan penekanannya. Acuan: `PRD_Konsolidasi_TA.md`,
> `laporan-tim/faiz-engine-developer/outline-laporan.md`.

# DAFTAR GAMBAR

[Diisi setelah gambar final ditentukan. Gambar relevan: Arsitektur Sistem,
Activity Integrasi Data Denah, Sequence Sinkronisasi Data & Unity,
Hierarki Prefab Gedung, UI Database Sync Checker.]

# DAFTAR TABEL

[Diisi menyusul.]

# DAFTAR LAMPIRAN

[Diisi menyusul.]

---

# BAB I PENDAHULUAN

## 1.1 Latar Belakang
[Bersama — Smart Campus, masalah navigasi spasial. Lihat branch laporan/iman.]

## 1.2 Identifikasi Masalah
[Tekankan: belum tersedia sistem navigasi 3D interaktif dan terpandu di browser.]

## 1.3 Batasan Masalah
[Fokus: logika navigasi, rendering rute, optimasi WebGL, dan kontrol pengguna.]

## 1.4 Tujuan dan Manfaat
### 1.4.1 Tujuan
[Tulis di sini.]
### 1.4.2 Manfaat
[Tulis di sini.]

## 1.5 Jadwal Kegiatan
[Tulis di sini.]

## 1.6 Sistematika Penulisan
[Tulis di sini.]

---

# BAB II RANCANGAN PROYEK

## 2.1 Observasi
[Bersama.]
### 2.1.1 Observasi Lapangan Kegiatan
### 2.1.2 Analisis Sistem yang Sedang Berjalan
### 2.1.3 Wawancara dengan Stakeholder
[Tekankan kebutuhan navigasi terpandu & performa mobile.]

## 2.2 Usulan Solusi
### 2.2.1 Identifikasi Kebutuhan Fungsional
[Navigasi otomatis, rute visual, jarak, joystick mobile.]
### 2.2.2 Identifikasi Kebutuhan Teknis
[Unity 6 + URP, New Input System, NavMesh, WebGL.]
### 2.2.3 Identifikasi Kebutuhan Non-Fungsional
[Muat < 10 dtk, performa runtime, mobile-first.]

## 2.3 Rancangan Proyek
### 2.3.1 Rencana Pengembangan
### 2.3.2 Perancangan Sistem Navigasi (NavMesh & Pathfinding)
### 2.3.3 Perancangan Rendering Rute (Catmull-Rom Centripetal + Raycast)
### 2.3.4 Perancangan Optimasi Performa (Building Culling & WebGL Build)
### 2.3.5 Perancangan Kontrol Pengguna (Pointer Lock & Joystick Virtual)

## 2.4 Rencana Pengujian Proyek
[Play Mode Test navigasi; uji performa WebGL; uji editor tool.]

---

# BAB III IMPLEMENTASI PROYEK

## 3.1 Profil Mitra
[Bersama.]

## 3.2 Metode Implementasi
### 3.2.1 Implementasi BuildingDatabase (konsumsi /api/unity/data)
### 3.2.2 Implementasi NavigationReceiver & NavigationGuide
### 3.2.3 Implementasi Rendering Rute (Catmull-Rom + raycast subdivisi)
### 3.2.4 Implementasi Building Culling & WebGL Settings Optimizer
### 3.2.5 Implementasi Pointer Lock & Joystick Virtual Mobile
### 3.2.6 Implementasi Editor Tool: DatabaseSyncChecker

## 3.3 Konfigurasi & Metadata
### 3.3.1 Konfigurasi Build WebGL (Brotli, IL2CPP, stripping)
### 3.3.2 Konvensi Scene & NavMesh Bake

## 3.4 Laporan Implementasi Proyek
### 3.4.1 Logbook Implementasi Proyek
### 3.4.2 Hasil & Bukti Implementasi Navigasi
### 3.4.3 Hasil & Bukti Optimasi Performa

## 3.5 Hasil Pengujian Proyek
### 3.5.1 Pengujian Navigasi (Play Mode Test)
### 3.5.2 Pengujian Performa WebGL
### 3.5.3 Pengujian Editor Tool (DatabaseSyncChecker)

---

# BAB IV PENUTUP

## 4.1 Kesimpulan
[Tulis di sini.]

## 4.2 Saran
[Tulis di sini.]
