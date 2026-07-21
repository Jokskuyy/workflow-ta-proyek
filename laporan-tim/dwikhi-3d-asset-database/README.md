# Laporan TA — Muhammad Dwikhi Deandra Purnianto (3D Asset Designer & Database/Asset Manager)

**Branch:** `laporan/dwikhi` — tulis laporan di `Tugas_Akhir_Draft.md` (root repo) saat berada di branch ini.

## Fokus / Lingkup Laporan
Berdasarkan pembagian peran (BAB II — Wawancara Stakeholder), kontribusi:
1. **Pembuatan & Penataan Sebelas Aset 3D Gedung** langsung di **Unity Editor** (tanpa Blender), termasuk geometri, material atau tekstur, prefab, dan hierarki.
2. **Konvensi Hierarki Prefab** — menyusun child `Pointer` dan GameObject tujuan dengan nama yang sesuai dengan `unity_object_name`.
3. **Perancangan Skema Database dan ERD** Supabase PostgreSQL — `gedung`, `fasilitas`, `fakultas`, `program_studi`, `admin_users`, dan `audit_logs` beserta relasinya.
4. **Pengelolaan Data Gedung dan Fasilitas** — menjaga kelengkapan record serta pemetaan `unity_object_name` pada aset dan data.
5. **Validasi Konsistensi Aset–Data** — menggunakan `DatabaseSyncChecker` yang dikembangkan oleh 3D Simulator & Engine Developer untuk menemukan dan memperbaiki ketidaksesuaian.

> Ruang lingkup: persimpangan aset 3D dan pengelolaan data. Logika navigasi, engine, dan kode `DatabaseSyncChecker` = Faiz; API, dashboard, autentikasi, dan integrasi web = Iman. RLS serta trigger audit log hanya dibahas sebagai konteks sistem dan bukan kontribusi Dwikhi.

## Diagram Relevan
- **2.17 Entity-Relationship Diagram** — inti perancangan database.
- **3.1 Hierarki Prefab Gedung dengan Child Pointer** — inti penataan aset.
- **2.9 Arsitektur**, **2.12 Use Case**, **2.13 Activity Pengelolaan Data**, **2.16 Sequence Sinkronisasi** — konteks bersama.
- Sumber diagram: `../../diagrams/`.

## Yang Perlu Ditambahkan Sendiri
- Tangkapan layar proses pemodelan aset di Unity Editor.
- Workflow aset → prefab → penamaan `unity_object_name`.
- ERD atau dokumentasi skema yang dirancang.
- Bukti pengelolaan record gedung/fasilitas, perubahan `unity_object_name`, hasil pemeriksaan, koreksi, dan retest.

## Acuan
- Kontrak konten bersama dan include: `../../content/README.md`
- PRD (bagian "Skema Database" & "Konvensi Struktur Scene Unity"): `../../PRD_Konsolidasi_TA.md`
- Kerangka laporan: `outline-laporan.md`
- Kode Unity & skema DB: repo eksternal (lihat `../../PANDUAN-TIM.md`).
