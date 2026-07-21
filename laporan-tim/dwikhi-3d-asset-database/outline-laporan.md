# Kerangka Laporan TA — Dwikhi (3D Asset Designer & Database/Asset Manager)

> Format TA prototipe (4 bab). BAB I dan observasi (2.1) sebagian besar **sama** untuk semua anggota; penekanan berbeda mulai dari usulan solusi & implementasi.

## BAB I PENDAHULUAN
- 1.1 Latar Belakang *(bersama)*
- 1.2 Identifikasi Masalah *(tekankan: belum ada aset 3D kampus & struktur data terpadu/aman)*
- 1.3 Batasan Masalah *(fokus: sebelas aset 3D di Unity Editor + prefab/Pointer + skema/ERD + pengelolaan data dan `unity_object_name`; RLS/audit hanya konteks sistem)*
- 1.4 Tujuan dan Manfaat (1.4.1 Tujuan, 1.4.2 Manfaat)
- 1.5 Jadwal Kegiatan
- 1.6 Sistematika Penulisan

## BAB II RANCANGAN PROYEK
- 2.1 Observasi *(bersama)* — 2.1.1 Observasi Lapangan; 2.1.2 Analisis Sistem Berjalan; 2.1.3 Wawancara Stakeholder
- 2.2 Usulan Solusi
  - 2.2.1 Kebutuhan Fungsional *(data gedung/fasilitas, akurasi aset, audit)*
  - 2.2.2 Kebutuhan Teknis *(Unity Editor, PostgreSQL/Supabase, pemetaan data; RLS dan trigger sebagai konteks sistem)*
  - 2.2.3 Kebutuhan Non-Fungsional *(integritas data, keamanan, keterpeliharaan aset)*
- 2.3 Rancangan Proyek
  - 2.3.1 Rencana Pengembangan *(prototyping)*
  - 2.3.2 Perancangan Aset & Konvensi Scene 3D *(sebelas aset, prefab gedung, child Pointer, penamaan)*
  - 2.3.3 Perancangan Database & Pengelolaan Data *(ERD, relasi, record gedung/fasilitas; RLS dan trigger audit sebagai konteks)*
  - 2.3.4 Perancangan unity_object_name sebagai Jembatan Data
- 2.4 Rencana Pengujian Proyek *(integritas data dan konsistensi aset–DB; RLS/audit mengacu pada pengujian bersama)*

## BAB III IMPLEMENTASI PROYEK
- 3.1 Profil Mitra *(bersama)*
- 3.2 Metode Implementasi
  - 3.2.1 Pembuatan & Penataan Sebelas Aset 3D di Unity Editor
  - 3.2.2 Hierarki Prefab, Child Pointer & Penamaan unity_object_name
  - 3.2.3 Skema Database, ERD & Pengelolaan Data di Supabase
  - 3.2.4 Konteks Row Level Security & Trigger Audit Logs
- 3.3 Konfigurasi & Metadata (3.3.1 Struktur Basis Data & Relasi; 3.3.2 Aset & Konvensi Penamaan)
- 3.4 Laporan Implementasi (3.4.1 Logbook; 3.4.2 Hasil & Bukti Sebelas Aset 3D; 3.4.3 Hasil & Bukti Skema serta Pengelolaan Data)
- 3.5 Hasil Pengujian (3.5.1 Integritas & Relasi; pengujian RLS/audit sebagai konteks bersama; konsistensi aset–DB menggunakan Database Sync Checker buatan Faiz)

## BAB IV PENUTUP
- 4.1 Kesimpulan
- 4.2 Saran

---

### Gambar Direkomendasikan
- Arsitektur Sistem (`../../diagrams/gambar-2.09-*`)
- ERD (`../../diagrams/gambar-2.17-erd`)
- Hierarki Prefab Gedung (`../../diagrams/gambar-3.1-hierarki-prefab-unity`)
- Sequence Sinkronisasi (`../../diagrams/gambar-2.16-*`)
- (buat sendiri) Screenshot pembuatan sebelas aset di Unity, workflow aset→prefab/Pointer, ERD, bukti pengelolaan data, perubahan `unity_object_name`, dan hasil validasi/retest

### Acuan
- PRD bagian "Skema Database" & "Konvensi Struktur Scene Unity": `../../PRD_Konsolidasi_TA.md`
