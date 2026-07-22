# Laporan TA Dwikhi Deandra Purnianto

Branch `laporan/dwikhi` mendokumentasikan peran Desainer Asset 3D dan Desainer Skema Database.

## Fokus Laporan

1. Pembuatan dan penataan asset 3D gedung serta fasilitas yang memiliki GameObject pada scene Unity menggunakan Unity Editor.
2. Penyusunan prefab, child `Pointer`, dan GameObject tujuan.
3. Perancangan ERD dan struktur empat tabel inti: `gedung`, `fasilitas`, `fakultas`, dan `program_studi`.
4. Pengelolaan seed gedung dan fasilitas.
5. Pemetaan `unity_object_name` antara record dan GameObject tujuan.
6. Penggunaan `DatabaseSyncChecker` buatan Faiz untuk memeriksa konsistensi asset dan data.

Tabel Denah 2D, Supabase Auth, RLS, layanan audit, frontend, API, runtime Unity, dan deployment hanya dijelaskan sebagai konteks integrasi. Iman menangani integrasi SQL ke repositori web. Faiz menangani kode pemeriksa, runtime Unity, navigasi, optimasi, dan build WebGL.

## Diagram Aktif

1. Arsitektur Integrasi Asset 3D dan Data.
2. Alur Perancangan Asset 3D dan Data.
3. Rancangan Hierarki Prefab dan Target Navigasi.
4. ERD Inti Data Gedung, Fasilitas, Fakultas, dan Program Studi.
5. Sequence Diagram Validasi Identifier Asset dan Data.

Sumber diagram berada di folder `diagrams/` dan menggunakan PlantUML sebagai sumber kanonik.

## Batas Klaim

1. Tidak ada klaim optimasi performa asset karena optimasi dilakukan pada runtime Unity melalui pekerjaan Faiz.
2. Seed final 19 gedung dan 311 fasilitas dibedakan dari snapshot Supabase aktif 19 gedung dan 331 fasilitas.
3. Hasil sinkronisasi 320 cocok, 3 hanya pada database, dan 14 hanya pada scene diperlakukan sebagai snapshot lama.
4. Provenance foto atau tekstur yang tidak tersedia dinyatakan sebagai keterbatasan.
5. RLS, Auth, dan layanan audit bukan kontribusi Dwikhi.

## Acuan

- Kontrak shared content: `content/README.md`.
- Kerangka laporan: `outline-laporan.md`.
- Fakta terstruktur: `project_facts.json`.
