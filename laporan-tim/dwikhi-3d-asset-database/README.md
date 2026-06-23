# Laporan TA — Muhammad Dwikhi Deandra Purnianto (3D Asset Designer & Database Schema Designer)

**Branch:** `laporan/dwikhi` — tulis laporan di `Tugas_Akhir_Draft.md` (root repo) saat berada di branch ini.

## Fokus / Lingkup Laporan
Berdasarkan pembagian peran (BAB II — Wawancara Stakeholder), kontribusi:
1. **Pemodelan & Penataan Aset 3D Gedung** langsung di **Unity Editor** (tanpa Blender).
2. **Konvensi Hierarki Prefab** — prefab gedung dengan child `Pointer` berisi GameObject `unity_object_name`.
3. **Perancangan Skema Database** Supabase PostgreSQL — `gedung`, `fasilitas`, `fakultas`, `program_studi`, `admin_users`, `audit_logs` beserta relasinya (ERD).
4. **Row Level Security (RLS)** — kebijakan akses (`anon` = SELECT, `authenticated` = CRUD).
5. **Trigger Audit Logs** — pencatatan otomatis setiap mutasi data.

> Ruang lingkup: persimpangan aset 3D dan struktur data. Logika navigasi/engine = Faiz; API/integrasi web = Iman.

## Diagram Relevan
- **2.17 Entity-Relationship Diagram** — inti perancangan database.
- **3.1 Hierarki Prefab Gedung dengan Child Pointer** — inti penataan aset.
- **2.9 Arsitektur**, **2.12 Use Case**, **2.13 Activity Pengelolaan Data**, **2.16 Sequence Sinkronisasi** — konteks bersama.
- Sumber diagram: `../../diagrams/`.

## Yang Perlu Ditambahkan Sendiri
- Tangkapan layar proses pemodelan aset di Unity Editor.
- Workflow aset → prefab → penamaan `unity_object_name`.
- SQL DDL skema, contoh policy RLS, dan kode trigger audit log.

## Acuan
- PRD (bagian "Skema Database" & "Konvensi Struktur Scene Unity"): `../../PRD_Konsolidasi_TA.md`
- Kerangka laporan: `outline-laporan.md`
- Kode Unity & skema DB: repo eksternal (lihat `../../PANDUAN-TIM.md`).
