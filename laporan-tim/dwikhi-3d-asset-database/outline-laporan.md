# Kerangka Laporan TA Dwikhi

## BAB I Pendahuluan

BAB I memakai konteks proyek bersama, lalu memfokuskan rumusan masalah, batasan, tujuan, dan manfaat pada aset 3D, rancangan data inti, seed, serta pemetaan `unity_object_name`.

## BAB II Rancangan Proyek

### 2.1 Observasi

Gunakan observasi bersama tanpa mengubah batas interpretasi kuesioner dan wawancara.

### 2.2 Usulan Solusi

1. Kebutuhan fungsional aset, prefab, data inti, seed, pemetaan identifier, dan pemeriksaan konsistensi.
2. Kebutuhan teknis Unity Editor, ProBuilder, PostgreSQL atau Supabase, prefab, material, seed, `/api/unity/names`, dan `DatabaseSyncChecker`.
3. Kebutuhan nonfungsional integritas data, konsistensi identifier, keterpeliharaan, keterlacakan, dan keterbacaan visual.

### 2.3 Rancangan Proyek

1. Alur Perancangan Aset dan Data.
2. Perancangan Aset 3D Gedung dan Fasilitas.
3. Perancangan Hierarki Prefab dan Konvensi Penamaan.
4. Perancangan ERD dan Struktur Data Inti.
5. Perancangan Pengelolaan Seed dan Kualitas Data.
6. Perancangan Pemetaan dan Validasi `unity_object_name`.

### 2.4 Rencana Pengujian

1. Pemeriksaan Visual dan Struktur Aset.
2. Verifikasi Struktural Skema dan Seed.
3. Pemeriksaan Konsistensi Aset–Data.
4. Black Box dan UAT produk bersama sebagai konteks.

## BAB III Implementasi Proyek

BAB III memuat bukti proses Unity Editor, hierarki prefab, empat tabel inti, pengelolaan seed, pemetaan identifier, inventaris material atau tekstur, serta penggunaan alat pemeriksa buatan Faiz. Konfigurasi akses dan audit aplikasi dijelaskan sebagai batas integrasi, bukan implementasi Dwikhi.

## BAB IV Penutup

Kesimpulan hanya merangkum bukti aset, struktur data inti, seed, serta snapshot validasi yang tersedia. Saran tidak mengubah kekurangan bukti menjadi klaim performa atau optimasi aset.
