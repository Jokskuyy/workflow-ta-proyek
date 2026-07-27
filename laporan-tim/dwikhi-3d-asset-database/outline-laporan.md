# Kerangka Laporan TA Dwikhi

## BAB I Pendahuluan

BAB I memakai konteks proyek bersama, lalu memfokuskan rumusan masalah, batasan, tujuan, dan manfaat pada asset 3D, rancangan data inti, kebutuhan kebijakan RLS, skema tabel `audit_logs`, seed, serta pemetaan `unity_object_name`.

## BAB II Rancangan Proyek

### 2.1 Observasi

Gunakan observasi bersama tanpa mengubah batas interpretasi kuesioner dan wawancara.

### 2.2 Usulan Solusi

1. Kebutuhan fungsional asset, prefab, data inti, seed, pemetaan identifier, dan pemeriksaan konsistensi.
2. Kebutuhan teknis Unity Editor, ProBuilder, PostgreSQL atau Supabase, prefab, material, seed, `/api/unity/names`, dan `DatabaseSyncChecker`.
3. Kebutuhan nonfungsional integritas data, konsistensi identifier, keterpeliharaan, keterlacakan, dan keterbacaan visual.

### 2.3 Rancangan Proyek

1. Alur Perancangan Asset dan Data.
2. Perancangan Asset 3D Gedung dan Fasilitas.
3. Perancangan Hierarki Prefab dan Konvensi Penamaan.
4. Perancangan ERD dan Struktur Data Inti.
5. Perancangan Pengelolaan Seed dan Kualitas Data.
6. Perancangan Pemetaan dan Validasi `unity_object_name`.

### 2.4 Rencana Pengujian

1. Pemeriksaan Visual dan Struktur Asset.
2. Verifikasi Struktural Skema dan Seed.
3. Pemeriksaan Konsistensi Asset–Data.
4. Black Box dan UAT produk bersama sebagai konteks.

## BAB III Implementasi Proyek

BAB III memuat bukti proses Unity Editor sebagai alat utama dan Blender untuk sebagian objek pendukung, hierarki prefab, empat tabel inti, pengelolaan seed, pemetaan identifier, inventaris material atau tekstur, perancangan kebutuhan RLS dan skema `audit_logs`, serta penggunaan alat pemeriksa buatan Faiz. Layanan audit Dashboard dijelaskan sebagai implementasi Iman; trigger audit database tidak diklaim tanpa bukti. Penggunaan Sketchfab tidak dinyatakan tanpa nama model, URL, pembuat, dan lisensi.

## BAB IV Penutup

Kesimpulan hanya merangkum bukti asset, struktur data inti, seed, serta snapshot validasi yang tersedia. Saran tidak mengubah kekurangan bukti menjadi klaim performa atau optimasi asset.
