# Laporan TA — Muhammad Dwikhi Deandra Purnianto (3D Asset Designer & Database Schema Designer)

**Build aktif:** pada branch `laporan/iman` gunakan profil `dwikhi` dengan
sumber `Tugas_Akhir_Dwikhi_Draft.md`. Draf dan aset profil Iman tetap terpisah.

## Fokus / Lingkup Laporan
Berdasarkan pembagian peran (BAB II — Wawancara Stakeholder), kontribusi:
1. **Pemodelan & Penataan Aset 3D Gedung** langsung di **Unity Editor** (tanpa Blender).
2. **Konvensi Hierarki Prefab** — prefab gedung dengan child `Pointer` berisi GameObject `unity_object_name`.
3. **Perancangan Skema Database** Supabase PostgreSQL — 11 tabel untuk data kampus, Denah 2D, administrasi, audit, dan analitik beserta 10 foreign key.
4. **Row Level Security (RLS)** — rancangan kebijakan akses untuk seluruh 11 tabel; status deployment setiap kebijakan memerlukan bukti terpisah.
5. **Audit Logs** — rancangan tabel `audit_logs`. SQL lengkap tidak memuat `CREATE TRIGGER` sehingga trigger audit tidak diklaim aktif.

> Ruang lingkup: persimpangan aset 3D dan struktur data. Logika navigasi/engine = Faiz; API/integrasi web = Iman.

## Diagram Relevan
- **ERD Data Kampus dan Denah 2D** — delapan tabel yang saling berelasi.
- **ERD Tabel Pendukung dan Hubungan Akses Logis Administrator** — tiga tabel pendukung, koneksi CRUD administrator ke tabel data, serta pembeda eksplisit antara hubungan akses dan foreign key.
- **Use Case Pengelolaan Database melalui Panel Admin** dan **Activity Diagram CRUD Data melalui Panel Admin** — menunjukkan fungsi serta alur manipulasi data oleh administrator.
- **3.1 Hierarki Prefab Gedung dengan Child Pointer** — inti penataan aset.
- **2.9 Arsitektur**, **2.12 Use Case**, **2.13 Activity Pengelolaan Data**, **2.16 Sequence Sinkronisasi** — konteks bersama.
- Sumber diagram: `../../diagrams/`.

## Yang Perlu Ditambahkan Sendiri
- Tangkapan layar proses pemodelan aset di Unity Editor.
- Workflow aset → prefab → penamaan `unity_object_name`.
- Bukti penerapan DDL/RLS pada Supabase aktif dan hasil pengujian constraint yang belum tercakup oleh tangkapan kueri katalog serta hasil `SELECT` relasi Gedung Dewi Sartika–fasilitas.

## Acuan
- Kontrak konten bersama dan include: `../../content/README.md`
- PRD (bagian "Skema Database" & "Konvensi Struktur Scene Unity"): `../../PRD_Konsolidasi_TA.md`
- Kerangka laporan: `outline-laporan.md`
- Kode Unity & skema DB: repo eksternal (lihat `../../PANDUAN-TIM.md`).
