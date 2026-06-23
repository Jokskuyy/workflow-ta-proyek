# Kerangka 4 Bab Laporan TA Proyek (UPNVJ FIK 2025)

> Sumber kanonik tunggal, **selaras dengan sistem terkini** (lihat `PRD_Konsolidasi_TA.md`).
> Dirujuk oleh `write-ta-proyek` dan `docx-ta-proyek`. Jangan menyalin ulang ke SKILL.md.
>
> Catatan: penekanan tiap sub-bab dapat berbeda per peran/branch
> (lihat `laporan-tim/<peran>/outline-laporan.md`). Struktur dasar tetap sama.

## BAB I PENDAHULUAN
1. 1.1 Latar Belakang — konteks Smart Campus, kesulitan navigasi spasial, peran kolaboratif.
2. 1.2 Identifikasi Masalah — daftar bernomor.
3. 1.3 Batasan Masalah — ruang lingkup (kampus Pondok Labu, batas peran, Supabase Auth, RLS, batas WebGL bridge).
4. 1.4 Tujuan dan Manfaat — 1.4.1 Tujuan, 1.4.2 Manfaat.
5. 1.5 Jadwal Kegiatan — Gantt/tabel.
6. 1.6 Sistematika Penulisan.

## BAB II RANCANGAN PROYEK
1. 2.1 Observasi — 2.1.1 Observasi Lapangan, 2.1.2 Analisis Sistem Berjalan, 2.1.3 Wawancara Stakeholder.
2. 2.2 Usulan Solusi
   a. 2.2.1 Identifikasi Kebutuhan Fungsional (User, Admin, Integrasi/API).
   b. 2.2.2 Identifikasi Kebutuhan Teknis — React SPA, **Vercel Serverless API (Node.js)**, Supabase DB, Umami, Unity WebGL. (Express.js = proxy Umami + rate limiter, BUKAN API utama.)
   c. 2.2.3 Identifikasi Kebutuhan Non-Fungsional — performa (< 10 dtk), mobile-first, keamanan (JWT/RLS/rate limiter), privasi, usabilitas/aksesibilitas, keterpeliharaan.
3. 2.3 Rancangan Proyek
   a. 2.3.1 Rencana Pengembangan (Prototyping).
   b. 2.3.2 Perancangan Information Architecture (IA).
   c. 2.3.3 Perancangan UML (Use Case, Activity, Sequence).
   d. 2.3.4 Perancangan Modul Keamanan & Analitik (RLS, trigger audit logs, reverse proxy Umami).
   e. 2.3.5 Perancangan Entity Relationship Diagram (ERD).
   f. 2.3.6 Perancangan Antarmuka (mockup Public Dashboard & Admin Panel).
4. 2.4 Rencana Pengujian Proyek — Backend/API integration test, Black Box, UAT, Lighthouse.

## BAB III IMPLEMENTASI PROYEK
1. 3.1 Profil Mitra — 3.1.1 Nama, 3.1.2 Deskripsi, 3.1.3 Hubungan.
2. 3.2 Metode Implementasi
   a. 3.2.1 Implementasi Back-end — Vercel Serverless Functions (Node.js), skema database, kode SQL.
   b. 3.2.2 Implementasi Front-end — React SPA, routing, komunikasi WebGL.
   c. 3.2.3 Implementasi Integrasi (WebGL Bridge React–Unity) — `SendMessage` satu arah + alur `unity_object_name` (Unity fetch `/api/unity/data`).
3. 3.3 Konfigurasi & Metadata Sistem
   a. 3.3.1 Basis Data — tabel & kunci yang dipetakan ke Unity.
   b. 3.3.2 Proxy Analytics (Umami) — Express.js (port 3001) → Umami (port 3000).
   c. 3.3.3 Web Manifest / Web Assets — konfigurasi aset & build WebGL (Brotli, IL2CPP).
4. 3.4 Laporan Implementasi Proyek
   a. 3.4.1 Logbook Implementasi Proyek.
   b. 3.4.2 Hasil & Bukti Implementasi Back-end.
   c. 3.4.3 Hasil & Bukti Implementasi Front-end.
5. 3.5 Hasil Pengujian Proyek
   a. 3.5.1 Black Box Testing.
   b. 3.5.2 Lighthouse Testing / Performance.
   c. 3.5.3 User Acceptance Test (UAT).
   d. 3.5.4 Implementasi Hasil UAT.

## BAB IV PENUTUP
1. 4.1 Kesimpulan.
2. 4.2 Saran (prospek keberlanjutan).
