# INTEGRASI DENAH VIRTUAL UNIVERSITAS PEMBANGUNAN NASIONAL VETERAN JAKARTA KAMPUS PONDOK LABU
# (PERANCANGAN ASET 3D DAN SKEMA BASIS DATA)

Muhammad Dwikhi Deandra Purnianto

2025

> CATATAN: Ini kerangka awal untuk peran **3D Asset Designer & Database Schema Designer**.
> Bagian BAB I dan 2.1 (Observasi) sebagian besar SAMA dengan anggota lain — boleh disalin
> dari branch `laporan/iman` lalu disesuaikan penekanannya. Acuan: `PRD_Konsolidasi_TA.md`,
> `laporan-tim/dwikhi-3d-asset-database/outline-laporan.md`.

# DAFTAR GAMBAR

[Diisi setelah gambar final ditentukan. Gambar relevan: Arsitektur Sistem, ERD,
Hierarki Prefab Gedung, Sequence Sinkronisasi Data & Unity.]

# DAFTAR TABEL

[Diisi menyusul.]

# DAFTAR LAMPIRAN

[Diisi menyusul.]

---

# BAB I PENDAHULUAN

## 1.1 Latar Belakang
[Bersama — Smart Campus, masalah navigasi & fragmentasi data. Lihat branch laporan/iman.]

## 1.2 Identifikasi Masalah
[Tekankan: belum tersedia aset 3D kampus yang akurat dan struktur data terpadu yang aman.]

## 1.3 Batasan Masalah
[Fokus: pemodelan/penataan aset 3D di Unity Editor + perancangan skema DB, RLS, dan audit log.]

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
[Tekankan kebutuhan aset 3D & keamanan data.]

## 2.2 Usulan Solusi
### 2.2.1 Identifikasi Kebutuhan Fungsional
[Data gedung/fasilitas, akurasi aset, audit.]
### 2.2.2 Identifikasi Kebutuhan Teknis
[Unity Editor, PostgreSQL/Supabase, RLS, trigger.]
### 2.2.3 Identifikasi Kebutuhan Non-Fungsional
[Integritas data, keamanan, keterpeliharaan aset.]

## 2.3 Rancangan Proyek
### 2.3.1 Rencana Pengembangan
### 2.3.2 Perancangan Aset & Konvensi Scene 3D
[Prefab gedung, child Pointer, penamaan unity_object_name.]
### 2.3.3 Perancangan Database & Keamanan
[ERD, normalisasi, RLS, trigger audit.]
### 2.3.4 Perancangan unity_object_name sebagai Jembatan Data

## 2.4 Rencana Pengujian Proyek
[Integritas data, RLS, konsistensi aset–DB.]

---

# BAB III IMPLEMENTASI PROYEK

## 3.1 Profil Mitra
[Bersama.]

## 3.2 Metode Implementasi
### 3.2.1 Implementasi Pemodelan & Penataan Aset 3D di Unity Editor
### 3.2.2 Implementasi Hierarki Prefab & Penamaan unity_object_name
### 3.2.3 Implementasi Skema Database (SQL DDL) di Supabase
### 3.2.4 Implementasi Row Level Security & Trigger Audit Logs

## 3.3 Konfigurasi & Metadata
### 3.3.1 Struktur Basis Data & Relasi
### 3.3.2 Aset & Konvensi Penamaan

## 3.4 Laporan Implementasi Proyek
### 3.4.1 Logbook Implementasi Proyek
### 3.4.2 Hasil & Bukti Implementasi Aset 3D
### 3.4.3 Hasil & Bukti Implementasi Database

## 3.5 Hasil Pengujian Proyek
### 3.5.1 Pengujian Integritas & Relasi Data
### 3.5.2 Pengujian RLS (akses anon vs authenticated)
### 3.5.3 Validasi Konsistensi Aset–Database

---

# BAB IV PENUTUP

## 4.1 Kesimpulan
[Tulis di sini.]

## 4.2 Saran
[Tulis di sini.]
