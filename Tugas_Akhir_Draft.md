# PERANCANGAN ASET 3D DAN PENGELOLAAN BASIS DATA
# PADA SISTEM DENAH VIRTUAL UPNVJ KAMPUS PONDOK LABU

Dwikhi Deandra Purnianto
2210511131

INFORMATIKA
FAKULTAS ILMU KOMPUTER
UNIVERSITAS PEMBANGUNAN NASIONAL VETERAN JAKARTA
2026

# DAFTAR GAMBAR

<!-- Daftar Gambar dibuat otomatis dari caption ID-based pada body. -->

# DAFTAR TABEL

<!-- Daftar Tabel dibuat otomatis dari caption ID-based pada body. -->

# DAFTAR LAMPIRAN

LAMPIRAN 1. Surat Pernyataan Keaslian
LAMPIRAN 2. Dokumentasi Penyerahan Pakta Integritas kepada UPA TIK
LAMPIRAN 3. Bukti Pemodelan dan Penataan Aset 3D
LAMPIRAN 4. Skema Basis Data dan Bukti Pengelolaan Data
LAMPIRAN 5. Logbook dan Bukti Pengujian
LAMPIRAN 6. Mockup Antarmuka sebagai Konteks Integrasi

---

# BAB I PENDAHULUAN

## 1.1 Latar Belakang

<!-- PIPELINE:INCLUDE content/shared/bab1/latar-belakang-umum.md -->

Visualisasi lingkungan kampus dalam bentuk tiga dimensi dapat membantu penyajian hubungan spasial secara lebih interaktif dibandingkan denah statis. Penelitian terdahulu menunjukkan bahwa visualisasi gedung berbasis teknologi tiga dimensi dan WebGL dapat digunakan sebagai media informasi lokasi, sedangkan kajian mengenai *digital twin smart campus* menempatkan representasi digital lingkungan kampus sebagai bagian dari transformasi layanan pendidikan tinggi (Jamaludin et al. 2024; Muharam et al. 2023; Taurusta et al. 2024). Dalam proyek ini, manfaat visualisasi tersebut bergantung pada dua fondasi yang saling terkait, yaitu aset 3D yang merepresentasikan lingkungan fisik kampus dan struktur data yang menyimpan identitas gedung serta fasilitas secara konsisten.

Prefab Unity dapat menyimpan GameObject beserta komponen dan child-nya sebagai aset yang dapat digunakan kembali, sehingga hierarki dan konvensi penamaan menjadi bagian penting dalam pemeliharaan objek (Unity Technologies 2026a). Aset 3D yang tidak mengikuti struktur seragam akan menyulitkan proses integrasi dengan logika navigasi. Pada sisi lain, data gedung dan fasilitas yang tidak memiliki relasi, identitas integrasi, serta aturan akses yang jelas berisiko menimbulkan ketidaksesuaian antara informasi pada dashboard dan objek pada *scene* Unity. Oleh karena itu, perancangan aset 3D perlu dilakukan bersama perancangan skema basis data, khususnya melalui atribut `unity_object_name` sebagai penghubung antara baris data dan GameObject di Unity.

Pengelolaan data proyek juga membutuhkan pembatasan akses pada tingkat basis data. Penerapan *Row Level Security* (RLS) memungkinkan kebijakan akses dibedakan menurut peran pengguna, sedangkan mekanisme *audit log* menyediakan jejak perubahan untuk mendukung akuntabilitas pengelolaan data (Putra et al. 2026). Kedua mekanisme tersebut menjadi konteks sistem bagi data yang dikelola penulis, tetapi rancangan dan implementasinya tidak dinyatakan sebagai kontribusi penulis. Laporan ini berfokus pada pembuatan dan penataan seluruh aset 3D gedung dan fasilitas yang memiliki GameObject pada scene Unity, penyusunan prefab serta child `Pointer`, perancangan skema dan ERD, pengelolaan data gedung atau fasilitas, serta penjagaan konsistensi `unity_object_name` pada aset dan data.

## 1.2 Identifikasi Masalah

Berdasarkan latar belakang dan kebutuhan proyek, masalah yang menjadi fokus laporan ini diidentifikasi sebagai berikut:

1. Belum tersedia representasi aset 3D Kampus UPNVJ Pondok Labu yang ditata dengan hierarki dan konvensi penamaan seragam untuk mendukung denah virtual interaktif.
2. Data gedung, fasilitas, fakultas, dan program studi memerlukan skema relasional yang dapat menjaga integritas hubungan antardata.
3. Belum terdapat mekanisme identitas tunggal yang secara konsisten menghubungkan data gedung atau fasilitas pada basis data dengan GameObject yang sesuai pada *scene* Unity.
4. Record gedung dan fasilitas perlu dikelola secara konsisten agar nama, lokasi, foto, relasi, dan identifier integrasinya tetap sesuai dengan aset 3D.
5. Ketidaksesuaian `unity_object_name` antara basis data dan hierarki Unity perlu ditemukan serta diperbaiki sebelum digunakan pada build.

## 1.3 Batasan Masalah

Ruang lingkup laporan ini dibatasi agar pembahasan tetap sesuai dengan kontribusi 3D Asset Designer dan Database Schema Designer, yaitu sebagai berikut:

1. Objek yang direpresentasikan dibatasi pada aset 3D gedung dan fasilitas yang benar-benar memiliki GameObject pada scene Unity dan dikerjakan dalam lingkup kontribusi penulis.
2. Pembuatan dan penataan aset dilakukan langsung di Unity Editor tanpa membahas pemodelan menggunakan Blender.
3. Pembahasan aset mencakup geometri, material atau tekstur, prefab, hierarki, child `Pointer`, GameObject tujuan, dan konvensi penamaan.
4. Pembahasan basis data mencakup perancangan tabel dan relasi melalui ERD serta pengelolaan record `gedung` dan `fasilitas` yang terhubung dengan aset.
5. RLS dan trigger audit log dibahas sebagai konteks keamanan sistem, bukan sebagai rancangan atau implementasi penulis.
6. `unity_object_name` digunakan sebagai identifier integrasi yang ditetapkan dan diperbaiki penulis pada record basis data serta GameObject tujuan.
7. `DatabaseSyncChecker` digunakan penulis sebagai alat validasi; kode alat tersebut merupakan kontribusi 3D Simulator dan Engine Developer.
8. Logika NavMesh, navigasi, kontrol pemain, optimasi *engine*, API utama, dashboard React, autentikasi, komunikasi `SendMessage`, RLS, dan trigger audit berada di luar kontribusi utama penulis.
9. Aset disusun sebagai representasi visual berdasarkan observasi dan foto, bukan sebagai model *as-built* dengan ketelitian dimensi hasil pengukuran instrumental.

Pembagian tanggung jawab tim dirangkum pada [TABREF:peran_tanggung_jawab].

[TABLE-ID:peran_tanggung_jawab]
[TABLECAPTION:Peran dan Tanggung Jawab]

[TABLE]
Peran | Tanggung Jawab Utama
3D Asset Designer dan Database Schema Designer | Merancang aset visual 3D dan hierarki prefab beserta `Pointer`, merancang skema basis data Supabase PostgreSQL dan ERD, mengelola data serta pemetaan aset, dan menjaga konsistensi `unity_object_name`.
3D Simulator dan Engine Developer | Mengembangkan *runtime* Unity WebGL, termasuk `BuildingDatabase`, `NavigationReceiver`, `DatabaseSyncChecker`, navigasi NavMesh, interaksi pengguna, optimasi performa, dan proses *build* WebGL.
Full Stack Web Developer, System Integrator, dan DevOps Engineer | Mengembangkan Public Dashboard dan Admin Panel React, REST API pada Vercel Serverless Functions, integrasi Supabase Auth dan CRUD, *bridge* sisi React, pencatatan analitik aplikasi, pengujian web, serta deployment dan operasional layanan web; Express dan Umami dikelola sebagai jalur opsional.
[/TABLE]

## 1.4 Tujuan dan Manfaat

### 1.4.1 Tujuan

Tujuan penyusunan dan pelaksanaan proyek dalam lingkup laporan ini adalah sebagai berikut:

1. Membuat dan menata aset 3D gedung dan fasilitas Kampus UPNVJ Pondok Labu secara langsung di Unity Editor.
2. Menyusun hierarki prefab, child `Pointer`, dan GameObject tujuan dengan konvensi nama yang konsisten.
3. Merancang skema basis data relasional dan ERD untuk data gedung, fasilitas, fakultas, program studi, pengguna administrator, dan riwayat perubahan.
4. Mengelola record gedung serta fasilitas agar atribut dan relasinya sesuai dengan aset yang direpresentasikan.
5. Menetapkan dan memperbaiki `unity_object_name` pada basis data serta GameObject tujuan sebagai jembatan integrasi.
6. Menggunakan `DatabaseSyncChecker` yang dikembangkan anggota tim untuk memvalidasi konsistensi aset dan data.

### 1.4.2 Manfaat

Manfaat yang diharapkan dari kontribusi tersebut adalah sebagai berikut:

1. Bagi pengguna, aset 3D yang terstruktur dan data yang konsisten mendukung penyajian denah virtual serta informasi gedung dan fasilitas secara lebih mudah dipahami.
2. Bagi administrator, skema relasional dan record yang tertata memberikan dasar pengelolaan data gedung serta fasilitas secara terpusat.
3. Bagi tim pengembang, konvensi `unity_object_name` mengurangi ambiguitas ketika menghubungkan data pada dashboard, API, dan objek pada *scene* Unity.
4. Bagi institusi, rancangan tersebut dapat menjadi fondasi pengembangan layanan informasi spasial kampus yang lebih terpelihara dan berkelanjutan.

## 1.5 Jadwal Kegiatan

Kegiatan aktual penulis berlangsung selama enam bulan dan dirangkum pada [TABREF:jadwal_kegiatan]. Struktur tabel menggunakan periode enam bulan yang sama dengan jadwal proyek tim, sedangkan aktivitasnya dibatasi pada pekerjaan aset 3D, skema basis data, pengelolaan data, pemetaan identifier, validasi, dan dokumentasi Dwikhi.

[TABLE-ID:jadwal_kegiatan]
[TABLECAPTION:Jadwal Kegiatan Perancangan Aset 3D dan Basis Data]

[TABLE gantt]
Aktivitas | Bulan 1 | Bulan 2 | Bulan 3 | Bulan 4 | Bulan 5 | Bulan 6
Observasi lapangan dan identifikasi kebutuhan aset serta data | X | | | | | |
Pengambilan foto dan inventarisasi gedung serta fasilitas | X | X | | | | |
Perancangan skema database dan ERD | X | X | | | | |
Penetapan konvensi nama aset dan `unity_object_name` | X | X | X | | | |
Pemodelan aset 3D gedung dan fasilitas | | X | X | X | | |
Penerapan material dan tekstur | | X | X | X | | |
Penyusunan prefab, hierarki, `Pointer`, dan GameObject tujuan | | | X | X | | |
Penyusunan seed serta pengelolaan data gedung dan fasilitas | | | X | X | X | |
Pemetaan aset dengan `unity_object_name` | | | X | X | X | |
Pemeriksaan integritas database | | | | X | X | |
Validasi menggunakan `DatabaseSyncChecker` | | | | X | X | |
Pemeriksaan visual dan teknis aset | | | | X | X | X
Koreksi ketidaksesuaian aset dan data | | | | | X | X
Penyusunan dokumentasi dan laporan | X | X | X | X | X | X
Pengujian akhir dan finalisasi | | | | | X | X
[/TABLE]

## 1.6 Sistematika Penulisan

Laporan Tugas Akhir Proyek ini disusun dalam empat bab dengan sistematika sebagai berikut:

1. **BAB I PENDAHULUAN** menjelaskan latar belakang, identifikasi masalah, batasan masalah, tujuan dan manfaat, jadwal kegiatan, serta sistematika penulisan dengan penekanan pada aset 3D dan skema basis data.
2. **BAB II RANCANGAN PROYEK** menguraikan hasil observasi, kebutuhan sistem, rancangan aset dan konvensi *scene* Unity, rancangan basis data dan keamanan, pemetaan `unity_object_name`, serta rencana pengujian.
3. **BAB III IMPLEMENTASI PROYEK** menjelaskan profil mitra, metode implementasi aset 3D dan basis data, konfigurasi metadata, bukti implementasi, serta hasil pengujian yang relevan dengan kontribusi penulis.
4. **BAB IV PENUTUP** memuat kesimpulan berdasarkan hasil yang telah diverifikasi dan saran pengembangan lebih lanjut.

---

# BAB II RANCANGAN PROYEK
## 2.1 Observasi dan Analisis Kebutuhan Awal

<!-- PIPELINE:INCLUDE content/shared/bab2/observasi-dan-analisis-kebutuhan.md -->

### 2.1.1 Sumber Data dan Batas Observasi

<!-- PIPELINE:INCLUDE content/shared/bab2/sumber-data-dan-batas-observasi.md -->

### 2.1.2 Analisis Kebutuhan Pengguna dan Sistem yang Berjalan

<!-- PIPELINE:INCLUDE content/shared/bab2/analisis-kebutuhan-dan-sistem-berjalan.md -->

### 2.1.3 Hasil Wawancara Pemangku Kepentingan dan Implikasi Kebutuhan

<!-- PIPELINE:INCLUDE content/shared/bab2/wawancara-dan-implikasi-kebutuhan.md -->
## 2.2 Usulan Solusi

Solusi yang diusulkan adalah platform terintegrasi yang menggabungkan dashboard publik berbasis React, denah virtual Unity WebGL, Vercel Serverless Functions berbasis Node.js, basis data Supabase PostgreSQL, autentikasi, RLS, *audit log*, dan analitik Umami. Arsitektur tingkat tinggi sistem ditunjukkan pada [FIGREF:diagram_arsitektur].

[FIGURE:diagram_arsitektur]
[FIGCAPTION:Diagram Arsitektur Sistem]

Dalam arsitektur tersebut, kontribusi penulis menjadi lapisan penghubung antara representasi visual dan data. Aset 3D gedung dan fasilitas menyediakan bentuk serta susunan objek, sementara skema dan pengelolaan data menyediakan identitas, atribut, serta relasi gedung atau fasilitas. Field `unity_object_name` digunakan sebagai jembatan tunggal antara record `gedung` atau `fasilitas` dan GameObject tujuan di bawah child `Pointer` yang disusun penulis.

### 2.2.1 Identifikasi Kebutuhan Fungsional

Kebutuhan fungsional dalam lingkup aset 3D dan basis data dirumuskan sebagai berikut:

1. Sistem harus menyimpan data gedung beserta nama, deskripsi, lokasi, jumlah lantai, foto, dan `unity_object_name`.
2. Sistem harus menyimpan data fasilitas beserta tipe, lantai, warna kategori, relasi ke gedung, foto, dan `unity_object_name`.
3. Sistem harus menyimpan hubungan fakultas dengan gedung utama dan hubungan program studi dengan fakultas.
4. Administrator terautentikasi harus dapat melakukan operasi CRUD terhadap entitas data utama melalui komponen web yang disediakan anggota tim.
5. Pengguna anonim harus dapat membaca data publik tanpa memperoleh hak untuk mengubahnya.
6. Setiap operasi penambahan, perubahan, dan penghapusan data utama harus menghasilkan catatan pada tabel `audit_logs`.
7. Setiap `unity_object_name` yang digunakan untuk navigasi harus memiliki padanan GameObject pada *scene* Unity.
8. Tim teknis harus dapat mendeteksi data yang tidak memiliki padanan objek dan objek yang belum terdaftar pada basis data.

### 2.2.2 Identifikasi Kebutuhan Teknis

Kebutuhan teknis yang mendukung lingkup laporan ini adalah sebagai berikut:

1. Unity 6 dan Unity Editor digunakan untuk pemodelan, penataan aset, pembuatan prefab, dan penyusunan hierarki *scene*.
2. Supabase Cloud menyediakan PostgreSQL sebagai sistem manajemen basis data dan Supabase Auth sebagai konteks autentikasi.
3. RLS PostgreSQL digunakan oleh sistem untuk membatasi akses berdasarkan peran `anon` dan `authenticated`; rancangan dan implementasinya berada di luar kontribusi penulis.
4. Fungsi serta *trigger* PostgreSQL digunakan oleh sistem untuk mencatat mutasi data ke `audit_logs` dan dibahas hanya sebagai konteks pengelolaan data.
5. Vercel Serverless Functions menyediakan `/api/unity/data` untuk data runtime dan `/api/unity/names` untuk validasi nama oleh alat editor Unity.
6. `DatabaseSyncChecker` yang dikembangkan oleh 3D Simulator dan Engine Developer digunakan penulis untuk memvalidasi kecocokan `unity_object_name` antara basis data dan hierarki *scene*.
7. Aset gambar dan tekstur perlu disimpan dengan ukuran serta format yang sesuai dengan kebutuhan build WebGL. [TBD: konfirmasi format, resolusi, material, dan strategi optimasi aset yang digunakan Dwikhi]

### 2.2.3 Identifikasi Kebutuhan Non-Fungsional

Kebutuhan non-fungsional ditetapkan sebagai berikut:

1. **Integritas data**: foreign key, batasan unik, dan validasi nilai harus mencegah hubungan data yang tidak sah.
2. **Keamanan**: operasi tulis hanya dapat dilakukan dalam konteks pengguna terautentikasi dan kebijakan diterapkan pada tingkat basis data.
3. **Akuntabilitas**: perubahan data utama harus menghasilkan catatan yang memuat pelaku, aksi, tabel, rekaman, nilai lama, nilai baru, dan waktu kejadian.
4. **Konsistensi integrasi**: `unity_object_name` harus unik, stabil, dan cocok dengan nama GameObject tujuan.
5. **Keterpeliharaan**: struktur prefab dan skema data harus memungkinkan penambahan gedung atau fasilitas baru tanpa perubahan menyeluruh pada komponen lain.
6. **Performa aset**: model, material, dan tekstur perlu disiapkan agar tidak menambah beban build WebGL secara tidak terkendali. [TBD: metrik polygon, ukuran tekstur, ukuran build, dan pengaitan metrik dengan hasil pengujian pada perangkat yang didokumentasikan]

## 2.3 Rancangan Proyek

### 2.3.1 Rencana Pengembangan

Pengembangan mengikuti metode *prototyping* yang memungkinkan rancangan awal dievaluasi dan disempurnakan secara iteratif ketika kebutuhan pengguna belum seluruhnya rinci (Pricillia et al. 2021). Tahap pengembangan divisualisasikan pada [FIGREF:diagram_tahap_pengembangan].

[FIGURE:diagram_tahap_pengembangan]
[FIGCAPTION:Tahap Pengembangan]

Tahapan kerja dalam lingkup penulis direncanakan sebagai berikut:

1. Pengumpulan kebutuhan dilakukan melalui observasi aset fisik, inventarisasi data, dan koordinasi dengan pemangku kepentingan serta anggota tim.
2. Rancangan awal mencakup struktur prefab, child `Pointer`, konvensi `unity_object_name`, ERD, tipe data, dan relasi.
3. Aset, struktur prefab, skema, dan record gedung atau fasilitas disiapkan pada lingkungan pengembangan untuk memperoleh umpan balik teknis.
4. Hasil kerja dievaluasi melalui pemeriksaan visual, pengujian integritas referensial, dan validasi sinkronisasi nama; hasil RLS serta audit log digunakan sebagai konteks pengujian sistem bersama.
5. Rancangan diperbaiki berdasarkan temuan pengujian dan kebutuhan integrasi dari komponen web serta *engine*.

### 2.3.2 Perancangan Aset 3D Gedung dan Fasilitas

Rancangan aset menggunakan hierarki yang memisahkan geometri bangunan, objek per lantai, dan titik tujuan navigasi. Setiap gedung ditempatkan dalam satu objek atau prefab induk. Di bawah prefab tersebut terdapat child `Pointer` yang menjadi induk bagi GameObject tujuan dengan nama sesuai `unity_object_name`. Struktur ini memungkinkan logika navigasi mencari Transform tujuan tanpa bergantung pada nama tampilan yang dapat berubah.

Perancangan bentuk aset perlu mempertimbangkan keterbacaan representasi gedung, kesesuaian proporsi, konsistensi skala, pemakaian material, serta kebutuhan optimasi ketika aset dimuat pada aplikasi WebGL. ProBuilder mendukung pembuatan, penyuntingan, dan pemberian tekstur geometri langsung di dalam Unity, sehingga sesuai dengan metode pengerjaan aset yang terlihat pada bukti proses (Unity Technologies 2026b). Rancangan teknis setiap aset nantinya dibandingkan dengan bukti implementasi pada Subbab 3.2.1 dan spesifikasi akhir pada Subbab 3.3.3.

Scope aset mencakup seluruh aset 3D gedung dan fasilitas yang memiliki GameObject pada scene Unity dan dikerjakan penulis. Daftar record pada database tidak otomatis menjadi jumlah aset 3D karena sebagian data dapat digunakan sebagai informasi tanpa memiliki objek visual tersendiri. Sumber ukuran, target tingkat detail, konfigurasi collider, serta batas teknis setiap aset dicatat melalui dokumentasi Unity Editor dan bukti implementasi yang tersedia.

### 2.3.3 Perancangan Hierarki Prefab dan Konvensi Penamaan

Hierarki prefab dirancang untuk memisahkan geometri visual dari objek yang digunakan sebagai titik tujuan navigasi. Prefab menyimpan susunan GameObject, komponen, dan child sebagai aset yang dapat digunakan kembali (Unity Technologies 2026a). Pemisahan tersebut menjaga agar perubahan bentuk, material, atau susunan mesh tidak langsung mengubah identifier yang menghubungkan aset dengan data.

Konvensi awal yang digunakan adalah sebagai berikut:

1. Nama `unity_object_name` menggunakan huruf kecil dan garis bawah, misalnya `gedung_rektorat` atau `mht_201`.
2. Nama harus unik pada basis data dan tidak digunakan oleh dua GameObject tujuan yang berbeda.
3. Titik tujuan ditempatkan pada posisi yang aman dan dapat dijangkau sistem navigasi, bukan di dalam geometri penghalang.
4. Geometri visual dipisahkan dari objek tujuan agar perubahan material atau bentuk tidak mengubah identitas integrasi.
5. Prefab gedung harus mempertahankan struktur child `Pointer` ketika digunakan kembali pada *scene*.

Prefab dan hierarki aset gedung serta fasilitas dalam scope penulis disusun dengan memisahkan geometri dari child `Pointer` dan GameObject tujuan. Rincian objek per lantai serta variasi struktur aset dijelaskan menggunakan tangkapan hierarki yang tersedia pada BAB III. Sebelas pasangan render dan hierarki yang tersedia digunakan sebagai bukti representatif, bukan sebagai batas jumlah aset.

### 2.3.4 Perancangan Skema Basis Data, ERD, dan Pengelolaan Data

Entity Relationship Diagram merupakan representasi konseptual yang memperlihatkan entitas, atribut, dan hubungan sebagai dasar perancangan basis data (Afiifah et al. 2022). ERD proyek mencakup 11 tabel aktif. Bagian inti data akademik dan fasilitas divisualisasikan pada [FIGREF:diagram_erd], sedangkan relasi tabel denah navigasi didokumentasikan pada berkas `images/ERD_navigasi_peta_kampus.svg`. Tabel `admin_users`, `audit_logs`, dan `web_analytics_log` tetap termasuk dalam skema aktif meskipun tidak memiliki relasi langsung pada diagram inti.

[FIGURE:diagram_erd]
[FIGCAPTION:ERD Ringkas Data Akademik dan Fasilitas]

Skema proyek terdiri atas 11 tabel aktif. Struktur ringkasnya disajikan pada [TABREF:struktur_basis_data].

[TABLE-ID:struktur_basis_data]
[TABLECAPTION:Struktur Entitas Basis Data]

[TABLE]
Tabel | Fungsi | Relasi atau Batasan Utama
`gedung` | Menyimpan identitas dan informasi fisik gedung | Primary key `id`; `nama_gedung` dan `unity_object_name` unik; menjadi induk `fasilitas`
`fasilitas` | Menyimpan ruangan atau fasilitas di dalam gedung | Foreign key `id_gedung` ke `gedung`; `unity_object_name` unik
`fakultas` | Menyimpan profil fakultas | Foreign key `id_gedung_utama` ke `gedung`
`program_studi` | Menyimpan program studi dan akreditasi | Foreign key `id_fakultas` ke `fakultas`; kombinasi nama, jenjang, dan fakultas unik
`admin_users` | Menyimpan data administrator | Primary key `id`; `username` unik dan wajib diisi
`audit_logs` | Menyimpan jejak mutasi data | Menyimpan pelaku, aksi, tabel, ID rekaman, data lama, data baru, dan waktu
`campus_maps` | Menyimpan metadata denah 2D | `slug` unik; satu peta aktif melalui unique index parsial
`campus_map_nodes` | Menyimpan node jalur, pintu masuk, dan gerbang | Foreign key `map_id` ke `campus_maps`; koordinat berada pada rentang 0 sampai 1
`campus_map_edges` | Menyimpan hubungan antar-node denah | Foreign key ke node asal dan tujuan; kombinasi peta dan node unik
`campus_map_building_points` | Menyimpan posisi gedung pada denah | Foreign key ke peta, gedung, dan node masuk; kombinasi peta dan gedung unik
`web_analytics_log` | Menyimpan catatan kunjungan web | Data pengunjung, halaman, perangkat, dan waktu kunjungan
[/TABLE]

Penulis merancang entitas, atribut, relasi, serta batasan pada ERD dan mengelola record `gedung` atau `fasilitas` yang berhubungan langsung dengan aset. Pengelolaan tersebut mencakup pemeliharaan informasi tampilan, relasi lokasi, foto, dan `unity_object_name`; autentikasi, RLS, serta trigger audit tetap menjadi konteks komponen sistem lain.

Interaksi aktor terhadap data dirancang melalui *use case*. Legenda simbol yang digunakan dapat dilihat pada [FIGREF:diagram_use_case_legenda], sedangkan hubungan pengguna publik dan administrator dengan fungsi sistem disajikan pada [FIGREF:diagram_use_case].

[FIGURE:diagram_use_case_legenda]
[FIGCAPTION:Legenda Use Case Diagram]

[FIGURE:diagram_use_case]
[FIGCAPTION:Use Case Diagram]

Alur administrator dalam mengelola data dijelaskan secara visual pada [FIGREF:diagram_activity_kelola_data].

[FIGURE:diagram_activity_kelola_data]
[FIGCAPTION:Activity Diagram: Pengelolaan Data oleh Admin]

Alur integrasi data dengan komponen denah virtual ditunjukkan pada [FIGREF:diagram_activity_integrasi].

[FIGURE:diagram_activity_integrasi]
[FIGCAPTION:Activity Diagram: Integrasi Data Denah]

### 2.3.5 Konteks RLS dan Trigger Audit Log

Row Level Security merupakan mekanisme pembatasan akses baris pada basis data PostgreSQL yang dapat digunakan untuk membedakan operasi berdasarkan peran pengguna (PostgreSQL Global Development Group 2026b; Putra et al. 2026). Pada Supabase, tabel pada skema yang terekspos perlu mengaktifkan RLS dan menggunakan policy untuk menentukan akses per peran (Supabase 2026). Pada proyek ini, RLS dan *audit log* merupakan lapisan keamanan sistem yang memengaruhi record yang dikelola penulis, tetapi perancangan policy, fungsi, dan trigger tidak termasuk kontribusi penulis.

Dalam konteks integrasi, peran `anon` memperoleh akses baca terhadap data publik, sedangkan operasi pengelolaan dilakukan melalui pengguna terautentikasi. Mutasi pada tabel penting kemudian dicatat ke `audit_logs`. Laporan ini hanya menjelaskan dampak mekanisme tersebut terhadap pengelolaan data dan mengacu pada hasil pengujian bersama; nama policy, ekspresi akses, fungsi, serta trigger tidak digunakan sebagai bukti kontribusi Dwikhi.

### 2.3.6 Perancangan unity_object_name sebagai Jembatan Data

Alur sinkronisasi dimulai ketika administrator menyimpan `unity_object_name` melalui dashboard. Data diteruskan ke Supabase, tersedia melalui API, kemudian diambil oleh Unity.

Kontrak pemetaan dirancang sebagai berikut:

1. Tabel `gedung` dan `fasilitas` menyimpan `unity_object_name` sebagai nilai unik.
2. Nilai tersebut digunakan oleh endpoint `/api/unity/data` dan `/api/unity/names`.
3. GameObject tujuan ditempatkan sebagai turunan `Pointer` dan menggunakan nama yang sama.
4. Pencocokan runtime dilakukan tanpa membedakan kapitalisasi, tetapi konvensi penulisan tetap menggunakan huruf kecil dan garis bawah.
5. Nama tampilan seperti `nama_gedung` dan `nama_fasilitas` tetap dipisahkan dari identifier internal sehingga perubahan redaksi tidak merusak pemetaan.
6. Ketidaksesuaian perlu ditemukan sebelum build melalui pemeriksaan otomatis dan ditindaklanjuti pada basis data atau *scene* sesuai sumber kesalahan.

### 2.3.7 Keterkaitan Skema Data dengan Antarmuka

Antarmuka web bukan kontribusi utama penulis, tetapi menjadi konsumen skema data dan sarana administrator mengelola record. Oleh karena itu, pembahasan pada subbab ini dibatasi pada tiga rancangan yang memperlihatkan hubungan langsung antara struktur data dan antarmuka. Halaman utama pengelolaan data pada [FIGREF:mockup_dashboard_admin] menunjukkan konteks konsumsi entitas gedung oleh administrator.

[FIGURE:mockup_dashboard_admin]
[FIGCAPTION:Halaman Dashboard Admin]

Operasi penambahan record gedung dirancang melalui modal pada [FIGREF:mockup_modal_tambah_gedung]. Field yang tampil pada rancangan tersebut menjadi konteks bagi atribut yang perlu disediakan oleh skema basis data.

[FIGURE:mockup_modal_tambah_gedung]
[FIGCAPTION:Modal Tambah Data Gedung]

Data `gedung` dan `fasilitas` digunakan oleh bagian pencarian serta kartu aset yang dirancang pada [FIGREF:mockup_fasilitas_aset]. Rancangan ini memperlihatkan alasan relasi fasilitas-ke-gedung, nama tampilan, foto, dan metadata lokasi perlu disediakan secara konsisten.

[FIGURE:mockup_fasilitas_aset]
[FIGCAPTION:Bagian Fasilitas dan Aset]

Sembilan mockup lain dipindahkan ke Lampiran 6 sebagai konteks integrasi antarkomponen. Pemindahan tersebut menjaga fokus laporan pada kontribusi aset 3D dan basis data, tanpa mengklaim perancangan atau implementasi antarmuka sebagai pekerjaan penulis.

## 2.4 Rencana Pengujian Proyek

Rencana pengujian disusun agar setiap bagian rancangan memiliki hasil pengujian yang dapat ditelusuri pada Subbab 3.5. Setiap skenario perlu mencantumkan input, prasyarat, hasil yang diharapkan, hasil aktual, status, dan lokasi bukti.

### 2.4.1 Rencana Pengujian Aset 3D

Pengujian aset 3D direncanakan melalui pemeriksaan visual dan teknis terhadap posisi, skala, orientasi, material, tekstur, collider, susunan prefab, serta titik tujuan di dalam child `Pointer`. Pemeriksaan juga mencatat jumlah objek, jumlah polygon, jumlah material, ukuran tekstur, dan ukuran aset agar pengaruhnya terhadap build dapat dievaluasi. Unity Memory Profiler menyediakan kategori metrik seperti memori tekstur, memori mesh, jumlah material, dan jumlah objek yang dapat digunakan sebagai bukti pengukuran teknis (Unity Technologies 2026c).

[TBD: tetapkan checklist, versi scene, batas penerimaan, dan daftar aset yang akan diperiksa; spesifikasi perangkat uji sudah tersedia pada Subbab 3.3.3]

### 2.4.2 Rencana Pengujian Integritas dan Relasi Basis Data

Pengujian integritas direncanakan untuk memeriksa foreign key `fasilitas.id_gedung`, `fakultas.id_gedung_utama`, dan `program_studi.id_fakultas`, termasuk perilaku saat record induk diubah atau dihapus. Constraint pada PostgreSQL digunakan untuk menjaga validitas data melalui aturan seperti `NOT NULL`, `UNIQUE`, `PRIMARY KEY`, dan `FOREIGN KEY` (PostgreSQL Global Development Group 2026a). Pengujian batasan nilai memeriksa kolom wajib, keunikan `nama_gedung`, keunikan `unity_object_name`, dan batasan unik gabungan pada program studi.

### 2.4.3 Rencana Verifikasi Konteks RLS dan Audit Log

Verifikasi RLS menggunakan hasil pengujian sistem bersama untuk memastikan pengguna publik dapat membaca data yang diizinkan dan tidak dapat melakukan operasi tulis. Verifikasi *audit log* menggunakan bukti bersama untuk menelusuri pencatatan `INSERT`, `UPDATE`, dan `DELETE`. Fungsi trigger PostgreSQL dapat mengakses jenis operasi serta nilai baris `OLD` dan `NEW` (PostgreSQL Global Development Group 2026c), tetapi pemeriksaan policy atau kode trigger bukan pengujian kontribusi Dwikhi. Bukti yang digunakan pada laporan Dwikhi dibatasi pada hasil Black Box bersama dan tangkapan audit yang sudah tersedia.

### 2.4.4 Rencana Pengujian Konsistensi Aset dan Basis Data

Pengujian konsistensi direncanakan dengan membandingkan seluruh `unity_object_name` pada basis data terhadap GameObject tujuan pada hierarki Unity. Hasil pemeriksaan dikelompokkan menjadi nama yang cocok, nama yang hanya tersedia pada basis data, nama yang hanya tersedia pada *scene*, dan nama ganda. Dwikhi menggunakan `DatabaseSyncChecker` yang dikembangkan Faiz, sedangkan lingkup pekerjaan Dwikhi adalah menyiapkan serta memperbaiki nama pada aset dan data yang menjadi tanggung jawabnya.

### 2.4.5 Rencana Pengujian Fungsional dan UAT Bersama

Pengujian Black Box memeriksa fungsi sistem melalui masukan dan keluaran tanpa bergantung pada rincian kode internal (Maulida et al. 2025). Skenario bersama digunakan sebagai pengujian regresi untuk memastikan perubahan skema atau aset tidak merusak fungsi dashboard, API, dan navigasi. UAT digunakan untuk mengevaluasi penerimaan pengguna terhadap sistem berdasarkan kebutuhan yang telah ditentukan (Aliyah et al. 2025).

---

# BAB III IMPLEMENTASI PROYEK
## 3.1 Profil Mitra dan Pemangku Kepentingan

### 3.1.1 Nama Organisasi atau Lembaga Mitra

Humas Universitas Pembangunan Nasional “Veteran” Jakarta atau Humas UPNVJ.

### 3.1.2 Deskripsi Mitra

Humas UPNVJ menjadi mitra pengguna dalam proyek ini karena layanan navigasi ditujukan untuk membantu penyampaian informasi lokasi kepada mahasiswa baru, orang tua atau wali, sivitas akademika, dan pengunjung eksternal. Halaman resmi UPNVJ menjelaskan bahwa Humas UPNVJ mengoordinasikan strategi komunikasi digital bersama humas fakultas (UPNVJ 2026). Keterangan tersebut digunakan untuk menjelaskan hubungan Humas dengan penyampaian informasi kepada publik, bukan sebagai bukti bahwa sistem telah diterima sebagai layanan resmi institusi.

### 3.1.3 Hubungan Pemangku Kepentingan dengan Proyek

Humas UPNVJ berperan sebagai mitra pengguna dan satu perwakilannya mengikuti UAT untuk memberikan perspektif evaluasi terhadap informasi serta navigasi. Keikutsertaan tersebut tidak digunakan untuk mengklaim persetujuan formal, serah terima sistem, atau representasi seluruh pengguna UPNVJ. UPA TIK dicatat secara terpisah sebagai pihak koordinasi teknis, kebijakan data, kemungkinan integrasi institusional, dan penyerahan pakta integritas. Hubungan setiap pihak dirangkum pada [TABREF:hubungan_mitra_proyek].

[TABLE-ID:hubungan_mitra_proyek]
[TABLECAPTION:Hubungan Pemangku Kepentingan dengan Proyek]

[TABLE]
Pemangku Kepentingan | Hubungan dengan Proyek | Batas Interpretasi
Humas UPNVJ | Menjadi mitra pengguna; satu perwakilan mengikuti UAT dan memberikan perspektif evaluasi informasi serta navigasi | Masukan dibatasi pada peserta UAT dan tidak dianggap sebagai persetujuan institusional
Pengguna layanan | Mahasiswa baru, orang tua atau wali, sivitas akademika, dan pengunjung eksternal menjadi kelompok penerima manfaat navigasi | Tidak seluruh kelompok tersebut menjadi peserta UAT
UPA TIK UPNVJ | Memberikan konteks koordinasi teknis, kebijakan data, kemungkinan integrasi, wawancara, dan penyerahan pakta integritas | Bukan mitra pengguna dan tidak dinyatakan telah menerima implementasi sistem
Tim pengembang | Mengembangkan komponen sesuai pembagian peran aset/data, *runtime* Unity, dan aplikasi web | Setiap laporan hanya mengklaim implementasi yang berada dalam ownership penulisnya
[/TABLE]
## 3.2 Metode Implementasi

Implementasi menggunakan pendekatan iteratif sesuai rancangan *prototyping*. Lingkup penulis mencakup pembuatan dan penataan seluruh aset 3D gedung dan fasilitas yang memiliki GameObject pada scene Unity, hierarki prefab dan child `Pointer`, perancangan skema serta ERD, pengelolaan record gedung atau fasilitas, dan pemetaan `unity_object_name`. Uraian berikut membedakan kontribusi tersebut dari komponen integrasi milik anggota lain.

### 3.2.1 Implementasi Pembuatan dan Penataan Aset 3D Gedung dan Fasilitas di Unity Editor

Penulis membuat dan menata aset 3D gedung dan fasilitas secara langsung pada Unity Editor tanpa Blender. Bukti yang diserahkan mencakup berkas referensi visual kondisi aktual, tangkapan proses pengerjaan pada Unity Editor, render dan tangkapan hierarki yang tersedia, serta inventaris berkas material dan tekstur. Sebelas pasangan render dan hierarki yang tersedia digunakan sebagai sampel bukti representatif, bukan sebagai batas jumlah aset. Dimensi presisi tidak tersedia karena observasi tidak menggunakan alat ukur, sedangkan data teknis seperti triangle, material, collider, ukuran build, dan versi setiap aset dicatat dari bukti Unity yang tersedia.

Folder `images/list_foto/` memuat 21 berkas referensi visual. Berkas tersebut merupakan dokumentasi lapangan, sudut tambahan, atau sumber visual untuk sebagian aset dan entitas database yang terkait. Cakupan foto tidak digunakan untuk menyimpulkan jumlah seluruh GameObject yang dikerjakan. Sumber, tanggal, lokasi, dan identitas pengambil gambar belum seluruhnya tersedia. Inventarisnya dirangkum pada [TABREF:inventaris_foto_referensi].

[TABLE-ID:inventaris_foto_referensi]
[TABLECAPTION:Inventaris Berkas Referensi Visual Kondisi Aktual]

[TABLE]
No. | Objek yang Terdokumentasi | Berkas Bukti | Catatan Verifikasi
1 | Bagian depan Gedung M. Yamin | `Foto_depan_M.Yamin.jpg` | Sumber dan tanggal belum dicatat
2 | Gedung Cipto Mangunkusumo | `Foto_gedung_Cipto.jpg` | Sumber dan tanggal belum dicatat
3 | Gedung M. Yamin | `Foto_gedung_M.Yamin.jpg` | Sumber dan tanggal belum dicatat
4 | Gedung Muhammad Husni Thamrin | `Foto_gedung_Muh_Tamrin.jpg` | Sumber dan tanggal belum dicatat
5 | Gedung Soetomo | `Foto_gedung_Soetomo.jpg` | Entitas berbeda dari Soepomo; status GameObject mengikuti inventaris scene
6 | Gedung Wahidin Sudiro Husodo dari sisi depan | `Foto_gedung_wahidin.jpg` | Sumber dan tanggal belum dicatat
7 | Gedung Wahidin Sudiro Husodo dari sisi lain | `Foto_gedung_Wahidin_1.jpg` | Sumber dan tanggal belum dicatat
8 | Gerbang depan kampus | `Foto_gerbang_depan.jpg` | Objek konteks lingkungan
9 | Ruang Rektorat | `Foto_ruangan_rektorat.jpg` | Objek konteks interior
10 | Ruang Wi-Fi Gedung Abdul Rachman Saleh | `Foto_ruangan_Wifi_gedung_Abdul_Rachman.jpg` | Objek konteks interior
11 | Gedung Yos Sudarso | `gambar_Gedung_Yos_Sudarso.png` | Sumber gambar perlu diverifikasi
12 | Masjid | `gambar_masjid.png` | Tangkapan sumber eksternal; URL, tanggal akses, dan izin penggunaan perlu dicatat
13 | Gedung Abdul Rachman Saleh | `refrensi_gedung_abdul_rachman.jpeg` | Sumber dan tanggal belum dicatat
14 | Gedung Dewi Sartika | `refrensi_gedung_dewi_sartika.jpeg` | Sumber dan tanggal belum dicatat
15 | Gedung Cipto Mangunkusumo | `refrensi_gedung_dr.cipto.jpeg` | Sudut referensi tambahan; sumber dan tanggal belum dicatat
16 | Gedung Ki Hajar Dewantara | `refrensi_gedung_ki_hadjar_dewantara.jpeg` | Sumber dan tanggal belum dicatat
17 | Gedung M. Yamin | `refrensi_gedung_m.yamin.jpeg` | Sudut referensi tambahan; sumber dan tanggal belum dicatat
18 | Gedung Muhammad Husni Thamrin | `refrensi_gedung_muh husni tamrin.jpeg` | Sudut referensi tambahan; sumber dan tanggal belum dicatat
19 | Gedung R.A. Kartini | `refrensi_gedung_ra_kartini.jpeg` | Entitas database terpisah; status GameObject mengikuti inventaris scene
20 | Gedung Soepomo | `refrensi_gedung_soepomo.jpeg` | Sumber dan tanggal belum dicatat
21 | Gedung Soetomo | `refrensi_gedung_soetomo.jpeg` | Entitas berbeda dari Soepomo; status GameObject mengikuti inventaris scene
[/TABLE]

Karakter fasad, susunan lantai, bukaan, dan warna Gedung Cipto Mangunkusumo terdokumentasi pada [FIGREF:evidence_photo_cipto] sebagai salah satu referensi visual kondisi aktual.

[FIGURE:evidence_photo_cipto]
[FIGCAPTION:Referensi Aktual Gedung Cipto Mangunkusumo]

Perbedaan bentuk massa dan pola fasad gedung lainnya terlihat pada [FIGREF:evidence_photo_myamin], yang mendokumentasikan salah satu sisi Gedung M. Yamin.

[FIGURE:evidence_photo_myamin]
[FIGCAPTION:Referensi Aktual Gedung M. Yamin]

Referensi bangunan dengan komposisi vertikal dan bidang fasad yang berbeda diperlihatkan pada [FIGREF:evidence_photo_wahidin] melalui dokumentasi Gedung Wahidin Sudiro Husodo.

[FIGURE:evidence_photo_wahidin]
[FIGCAPTION:Referensi Aktual Gedung Wahidin Sudiro Husodo]

Tangkapan proses pada [FIGREF:evidence_process_asset] memperlihatkan Unity Editor dengan objek gedung yang sedang disunting, panel *Hierarchy*, panel *Project*, dan komponen ProBuilder pada *Inspector*. Bukti ini mendokumentasikan metode pembuatan dan penyesuaian geometri langsung di lingkungan Unity yang digunakan penulis pada aset gedung.

[FIGURE:evidence_process_asset]
[FIGCAPTION:Proses Pengerjaan Aset Gedung di Unity Editor]

Metode implementasi aset menggunakan pendekatan pemodelan berbasis referensi visual. Foto dan pengamatan langsung digunakan untuk mengenali massa bangunan, jumlah lantai, pola fasad, bukaan, warna, material, dan hubungan proporsional antarelemen. Geometri kemudian dibentuk dan disesuaikan secara visual di Unity Editor, dilanjutkan dengan penerapan material atau tekstur, pengelompokan objek, serta penyusunan aset pada hierarki. Pendekatan ini sesuai untuk kebutuhan representasi denah virtual, tetapi tidak digunakan untuk menyatakan ketelitian dimensi arsitektural.

Versi editor yang terlihat telah dicatat pada Subbab 3.3.3. Informasi yang masih perlu dilengkapi adalah [TBD: tanggal pengerjaan, path setiap prefab, daftar fitur atau tool Unity yang digunakan untuk setiap aset, jumlah triangle, material, collider, ukuran build, serta keputusan perubahan selama iterasi].

### 3.2.2 Implementasi Hierarki Prefab dan Penamaan unity_object_name

Folder bukti memuat pasangan render dan tangkapan hierarki untuk sebagian aset gedung. Pada setiap prefab atau struktur objek yang dikerjakan, penulis mengelompokkan geometri dan objek per lantai, menyusun child `Pointer`, membuat GameObject tujuan, serta menetapkan nama yang sesuai dengan `unity_object_name`. Mekanisme penggunaan titik tujuan oleh API atau logika navigasi tetap menjadi kontribusi anggota integrator dan pengembang *engine*.

Secara teknis, implementasi mengikuti aturan berikut:

1. Setiap prefab gedung mempunyai child `Pointer`.
2. Di bawah `Pointer` terdapat GameObject kosong untuk titik tujuan gedung atau fasilitas.
3. Nama GameObject disamakan dengan nilai `unity_object_name` pada basis data.
4. Titik tujuan diletakkan pada posisi yang dapat dicapai oleh sistem navigasi.
5. Perubahan nama harus diselaraskan pada basis data dan *scene* sebelum build.

### 3.2.3 Implementasi Rancangan Skema dan Pengelolaan Data di Supabase

Skema PostgreSQL yang didokumentasikan penulis mencakup 11 tabel, yaitu `gedung`, `fasilitas`, `fakultas`, `program_studi`, `admin_users`, `audit_logs`, `campus_maps`, `campus_map_nodes`, `campus_map_edges`, `campus_map_building_points`, dan `web_analytics_log`. Berkas SQL setup yang diserahkan penulis digunakan sebagai sumber dokumentasi dan tidak dijalankan saat penyusunan laporan karena memuat operasi `DROP TABLE`. Potongan DDL berikut menampilkan struktur inti untuk menjelaskan tabel, kolom, relasi, serta batasan; status penerapannya pada basis data produksi tetap dibedakan dari keberadaan berkas SQL.

Pada pemetaan aset, Masjid memiliki representasi visual atau GameObject tersendiri, tetapi record datanya berada pada tabel `fasilitas` dengan `id_gedung = 6`, yaitu Gedung Ki Hadjar Dewantara. Record Gedung Soepomo, Gedung Soetomo, Yos Sudarso, RA Kartini, Lapangan Basket, dan entitas gedung lainnya tetap diperlakukan sebagai entitas database yang berbeda.

```sql
CREATE TABLE gedung (
  id SERIAL PRIMARY KEY,
  nama_gedung VARCHAR(255) UNIQUE NOT NULL,
  deskripsi_gedung TEXT,
  lokasi TEXT,
  jumlah_lantai INT DEFAULT 1,
  foto_url VARCHAR(255),
  unity_object_name TEXT UNIQUE
);

CREATE TABLE fasilitas (
  id SERIAL PRIMARY KEY,
  nama_fasilitas VARCHAR(255) NOT NULL,
  deskripsi_fasilitas TEXT,
  tipe_fasilitas VARCHAR(100),
  color VARCHAR(50) DEFAULT 'gray',
  lantai INT DEFAULT 1,
  foto_url TEXT,
  id_gedung INT REFERENCES gedung(id) ON DELETE SET NULL,
  unity_object_name TEXT UNIQUE
);

CREATE TABLE fakultas (
  id SERIAL PRIMARY KEY,
  nama_fakultas VARCHAR(255) UNIQUE NOT NULL,
  deskripsi_fakultas TEXT,
  email VARCHAR(255),
  website VARCHAR(255),
  id_gedung_utama INT REFERENCES gedung(id) ON DELETE SET NULL
);

CREATE TABLE program_studi (
  id SERIAL PRIMARY KEY,
  nama_prodi VARCHAR(255) NOT NULL,
  jenjang VARCHAR(10),
  id_fakultas INT REFERENCES fakultas(id) ON DELETE CASCADE,
  akreditasi VARCHAR(50),
  CONSTRAINT unique_prodi_jenjang_fakultas
    UNIQUE (nama_prodi, jenjang, id_fakultas)
);

CREATE TABLE admin_users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  nama_lengkap VARCHAR(255),
  role VARCHAR(50) DEFAULT 'admin',
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE audit_logs (
  id BIGSERIAL PRIMARY KEY,
  actor_id UUID,
  actor_email TEXT,
  action TEXT,
  table_name TEXT,
  record_id TEXT,
  old_data JSONB,
  new_data JSONB,
  created_at TIMESTAMP DEFAULT now()
);
```

ERD, berkas SQL setup, dan struktur logis 11 tabel menjadi bukti perancangan skema oleh penulis. Dalam kapasitas Database/Asset Manager, penulis juga mengelola record `gedung` dan `fasilitas`, termasuk atribut serta `unity_object_name` yang digunakan oleh aset. Lampiran 4 diarahkan pada ERD, DDL dokumentasi, struktur data, contoh record yang dikelola, dan riwayat perubahan nilai; bukti penerapan ulang pada basis data Supabase aktif tetap dicatat terpisah.

### 3.2.4 Konteks Implementasi Row Level Security dan Trigger Audit Log

RLS pada sistem memisahkan akses publik dan akses pengelolaan, sedangkan antarmuka sistem menampilkan catatan mutasi data. Mekanisme tersebut memengaruhi record yang dikelola penulis, tetapi policy, fungsi, dan trigger tidak dirancang atau diimplementasikan oleh penulis. Berkas SQL setup yang diperiksa memuat kebijakan RLS, tetapi tidak memuat definisi trigger audit. Oleh karena itu, keberadaan trigger tidak disimpulkan dari berkas tersebut dan SQL RLS tidak disajikan sebagai hasil kerja Dwikhi.

Fungsi *audit log* pada PostgreSQL secara umum dapat membedakan `INSERT`, `UPDATE`, dan `DELETE` serta mengakses nilai `OLD` dan `NEW` sesuai jenis operasi (PostgreSQL Global Development Group 2026c). Tangkapan dashboard audit pada `dokumentasi/audit-log-admin-dashboard.png` digunakan sebagai konteks bahwa perubahan record dapat ditelusuri. Bukti ini tidak digunakan untuk mengatribusikan kode RLS atau trigger kepada penulis.

### 3.2.5 Implementasi Pemetaan unity_object_name pada Aset dan Basis Data

Implementasi pemetaan dilakukan penulis dengan menerapkan identifier yang sama pada kolom `unity_object_name` di tabel `gedung` atau `fasilitas` dan pada GameObject tujuan di bawah child `Pointer`. Penulis menyiapkan serta memperbaiki nama pada aset dan data, kemudian menggunakan `DatabaseSyncChecker` buatan Faiz untuk menemukan ketidaksesuaian. Implementasi endpoint API oleh Iman dan kode alat pemeriksa oleh Faiz tidak dinyatakan sebagai kontribusi penulis.

Tahap implementasi pemetaan perlu didokumentasikan sebagai berikut:

1. Menginventarisasi aset gedung dan fasilitas yang memerlukan titik tujuan.
2. Menetapkan identifier berformat huruf kecil dan garis bawah serta memastikan nilainya unik.
3. Mengisikan identifier pada record basis data yang sesuai.
4. Membuat atau memperbarui GameObject tujuan di bawah child `Pointer` dengan nama yang sama.
5. Menjalankan pemeriksaan konsistensi melalui alat bantu tim.
6. Memperbaiki ketidaksesuaian pada aset atau data sesuai sumber kesalahan, kemudian melakukan pengujian ulang.

Kolom dan contoh nilai identifier pada tabel `gedung` dapat dilihat pada [FIGREF:evidence_unity_names_gedung]. Tangkapan tersebut memperlihatkan antara lain nilai `cipto_mangunkusumo`, `abdul_rahman_saleh`, `ki_hadjar_dewantara`, `thamrin`, `yamin`, `yos_sudarso`, `kartini`, `parkir_depan`, `parkir_belakang`, `dewi_sartika`, `lapangan_upacara`, `ukm`, dan `soetomo`. Karena nama tampilan gedung terpotong pada tangkapan, bukti ini digunakan untuk mengonfirmasi keberadaan kolom serta contoh nilai, bukan sebagai daftar pemetaan final.

[FIGURE:evidence_unity_names_gedung]
[FIGCAPTION:Contoh Nilai unity_object_name pada Tabel Gedung]

Penerapan identifier pada record fasilitas terlihat pada [FIGREF:evidence_unity_names_fasilitas]. Tangkapan tersebut juga menampilkan `id_gedung`, `lantai`, `foto_url`, dan beberapa nilai `unity_object_name` berawalan `wsh_`, tetapi nama fasilitas tidak terlihat lengkap sehingga pasangan record dan GameObject masih perlu dicatat dalam matriks pemetaan.

[FIGURE:evidence_unity_names_fasilitas]
[FIGCAPTION:Contoh Nilai unity_object_name pada Tabel Fasilitas]

Pemetaan pada prefab dan GameObject aset dalam scope penulis merupakan bagian dari pekerjaan penulis. Bukti hierarki Dewi Sartika memperlihatkan contoh objek tujuan `dewi_sartika`, sedangkan hasil pemeriksaan pada Subbab 3.5.5 menunjukkan bahwa keseluruhan data dan *scene* belum sepenuhnya konsisten. Daftar pemetaan lengkap per record, perubahan yang dilakukan, serta metadata pengujian ulang masih diperlukan untuk menunjukkan penyelesaian koreksi secara terukur.

## 3.3 Konfigurasi dan Metadata

### 3.3.1 Struktur Basis Data dan Relasi

Konfigurasi basis data menggunakan foreign key untuk menjaga hubungan entitas dan batasan unik untuk menjaga identitas. Tabel `gedung` menjadi induk bagi `fasilitas`, tabel `fakultas` dapat merujuk gedung utama, dan tabel `program_studi` merujuk fakultas. Field `unity_object_name` pada `gedung` serta `fasilitas` menjadi metadata integrasi ke Unity.

Struktur constraint produksi yang tertangkap pada [FIGREF:evidence_constraint_inventory] menampilkan 12 baris hasil kueri katalog PostgreSQL. Bagian yang terbaca mengonfirmasi primary key pada `gedung`, `fakultas`, dan `fasilitas`; batasan unik `nama_gedung`, `nama_fakultas`, serta `unity_object_name` pada `gedung` dan `fasilitas`; foreign key `fakultas.id_gedung_utama` serta `fasilitas.id_gedung` ke `gedung.id`; dan aturan `ON DELETE SET NULL` pada dua relasi yang terlihat. Tangkapan ini membuktikan definisi constraint, bukan hasil percobaan memasukkan atau menghapus data yang melanggar aturan.

[FIGURE:evidence_constraint_inventory]
[FIGCAPTION:Inventaris Constraint Tabel Utama pada Supabase]

Nilai produksi setiap tipe fasilitas, aturan nilai `lantai`, format `foto_url`, kebijakan data kosong, constraint lain yang terpotong pada tangkapan, dan riwayat perubahan skema perlu dicatat agar skema dapat dipelihara. [TBD: isi keputusan konfigurasi produksi yang dibuat Dwikhi, tanggal atau versi berkas SQL setup, serta status penerapannya pada Supabase aktif]

### 3.3.2 Konvensi Struktur Prefab dan Penamaan

Contoh struktur prefab dengan child `Pointer` dapat dilihat pada [FIGREF:impl_pointer_hierarchy].

[FIGURE:impl_pointer_hierarchy]
[FIGCAPTION:Hierarki Prefab Gedung dengan Child Pointer di Unity]

Validasi kecocokan nama dibantu oleh `DatabaseSyncChecker`, dengan antarmuka yang ditunjukkan pada [FIGREF:impl_sync_db_checker]. Alat ini mengambil daftar nama dari `/api/unity/names`, menelusuri hierarki *scene*, dan mengelompokkan hasil yang cocok atau tidak cocok.

[FIGURE:impl_sync_db_checker]
[FIGCAPTION:Tampilan UI Database Sync Checker di Unity Editor]

Pada bukti [FIGREF:impl_sync_db_checker], pemeriksaan awal menampilkan 97 nama dari basis data, 57 nama ditemukan pada *scene*, 40 nama hanya terdapat pada basis data, dan 18 nama hanya terdapat pada *scene*. Angka tersebut menunjukkan kondisi awal yang belum konsisten, bukan hasil akhir implementasi. Versi *scene*, endpoint, basis data, daftar koreksi, dan hasil pengujian ulang belum tercatat pada bukti yang tersedia.

### 3.3.3 Spesifikasi dan Optimasi Aset 3D

Spesifikasi aset mencatat karakteristik teknis yang memengaruhi keterpeliharaan prefab dan beban aplikasi. Pencatatan dilakukan per aset atau per kelompok prefab agar perubahan versi dapat dibandingkan secara terukur. Metrik memori tekstur, mesh, material, dan objek dapat diperoleh melalui Unity Memory Profiler untuk mendukung evaluasi tersebut (Unity Technologies 2026c).

Parameter minimum yang perlu dicatat meliputi:

1. Nama aset atau prefab dan versi yang diuji.
2. Jumlah objek, mesh, vertex, triangle, dan collider.
3. Jumlah material serta resolusi dan format tekstur.
4. Skala, orientasi, posisi, dan struktur child utama.
5. Ukuran file sumber, prefab, dan perubahan ukuran build jika tersedia.
6. Tindakan optimasi seperti penggabungan mesh, penggunaan ulang material, kompresi tekstur, pengurangan detail, atau penghapusan objek yang tidak digunakan.

Versi editor yang terlihat pada [FIGREF:evidence_unity_version] adalah Unity 6.4 dengan identifier `6000.4.1f1_8535861f39e1`. Bukti ini menetapkan lingkungan yang terlihat ketika data dikumpulkan dan digunakan sebagai konteks untuk membaca metrik aset.

[FIGURE:evidence_unity_version]
[FIGCAPTION:Versi Unity yang Digunakan pada Pengukuran Aset]

Perangkat yang digunakan pada pengambilan metrik ditunjukkan pada [FIGREF:evidence_test_device]. Tangkapan tersebut memperlihatkan prosesor 13th Gen Intel(R) Core(TM) i7-13620H, RAM terpasang 32 GB, GPU NVIDIA GeForce RTX 4060 Laptop GPU 8 GB, dan sistem operasi 64-bit. Nama perangkat pada tangkapan tidak digunakan sebagai bukti atribusi akun atau kepemilikan hasil pengujian.

[FIGURE:evidence_test_device]
[FIGCAPTION:Spesifikasi Perangkat Pengujian Aset]

Inventaris pada [FIGREF:evidence_prefab_sizes] menampilkan ukuran berkas prefab gedung beserta berkas `.meta` yang berukuran jauh lebih kecil. Nilai yang terbaca untuk tiga aset terukur adalah 24,3 MB pada Ki Hajar Dewantara, 11,2 MB pada Dewi Sartika, dan 11,2 MB pada Jenderal Soedirman. Beberapa nama memiliki lebih dari satu versi berkas, sehingga ukuran tersebut digunakan sebagai nilai yang terlihat pada inventaris, bukan sebagai klaim bahwa seluruh prefab telah memiliki versi final yang sama.

[FIGURE:evidence_prefab_sizes]
[FIGCAPTION:Ukuran Berkas Prefab Gedung pada Inventaris Aset]

Hasil pengukuran teknis yang terbaca dari tiga tangkapan Unity dirangkum pada [TABREF:metrik_tiga_aset]. Jumlah triangle, material, dan collider tidak terlihat pada area hasil yang tertangkap sehingga tidak diisi berdasarkan perkiraan.

[TABLE-ID:metrik_tiga_aset]
[TABLECAPTION:Metrik Teknis Tiga Aset Representatif]

[TABLE]
Aset | GameObject | Mesh Instance | Unique Mesh | Vertex | Ukuran Prefab yang Terlihat
Ki Hajar Dewantara | 860 | 583 | 318 | 703.694 | 24,3 MB
Dewi Sartika | 477 | 371 | 279 | 124.973 | 11,2 MB
Jenderal Soedirman | 2.809 | 2.108 | 885 | 1.308.941 | 11,2 MB
[/TABLE]

Rincian GameObject, mesh instance, unique mesh, dan vertex Ki Hajar Dewantara terlihat pada [FIGREF:evidence_metrics_ki_hadjar]. Nilai tersebut mendokumentasikan kondisi objek yang dipilih saat tangkapan dibuat, tetapi belum menunjukkan jumlah triangle, material, collider, ataupun dampaknya terhadap frame rate dan ukuran build.

[FIGURE:evidence_metrics_ki_hadjar]
[FIGCAPTION:Hasil Pengukuran GameObject, Mesh, dan Vertex Ki Hajar Dewantara]

Hasil pengukuran Dewi Sartika direkam pada [FIGREF:evidence_metrics_dewi] dengan 477 GameObject dan 124.973 vertex. Data ini menjadi baseline teknis untuk perbandingan dengan pemeriksaan aset berikutnya apabila tersedia.

[FIGURE:evidence_metrics_dewi]
[FIGCAPTION:Hasil Pengukuran GameObject, Mesh, dan Vertex Dewi Sartika]

Kompleksitas tertinggi di antara tiga tangkapan terlihat pada [FIGREF:evidence_metrics_jenderal], yaitu Jenderal Soedirman dengan 2.809 GameObject dan 1.308.941 vertex. Angka tersebut belum cukup untuk menyimpulkan performa karena triangle, material, collider, perangkat uji, dan Build Report belum tersedia.

[FIGURE:evidence_metrics_jenderal]
[FIGCAPTION:Hasil Pengukuran GameObject, Mesh, dan Vertex Jenderal Soedirman]

Folder `images/list_material/` memuat 37 berkas gambar yang diserahkan sebagai inventaris material dan tekstur. Berkas tersebut dikelompokkan pada [TABREF:inventaris_material_tekstur] berdasarkan fungsi visual yang tersirat dari nama file. Pengelompokan ini belum menyatakan bahwa setiap berkas digunakan pada build final.

[TABLE-ID:inventaris_material_tekstur]
[TABLECAPTION:Inventaris Berkas Material dan Tekstur]

[TABLE]
Kelompok | Jumlah | Berkas
Permukaan luar dan lingkungan | 8 | `aspal.png`, `atap.jpeg`, `batu_bata.png`, `Rumput.jpeg`, `rumput.png`, `semen.jpeg`, `tanah.jpeg`, `water.jpg`
Dinding dan kayu | 7 | `diding_tu_fik.png`, `dinding_kayu.jpg`, `dinding_rektorat.jpg`, `dinding_rektotat_2.jpg`, `kayu.jpeg`, `kayu_coklat_tua.jpg`, `tembok_tamrin.jpg`
Bukaan, pagar, dan ubin | 9 | `itemputih.png`, `jaring_besi.png`, `jendela.png`, `pintu_putih.jpg`, `ubin.png`, `ubin2.jpeg`, `ubin3.jpeg`, `ubin4.jpeg`, `ubin5.jpeg`
Fasilitas dan elemen interior | 8 | `generator.png`, `lapangan_basket.png`, `layar_videoron.jpg`, `loker.png`, `mushola_gedung_utama.jpg`, `papan_basket.png`, `perpus.png`, `perpus2.png`
Identitas dan logo | 5 | `logo_bni.png`, `Logo_Indomaret.png`, `LOGO_PKBN.jpg`, `logo_sekolah.png`, `Logo_upn.png`
[/TABLE]

Salah satu pola permukaan dinding yang tersedia pada inventaris diperlihatkan pada [FIGREF:evidence_material_wall_fik] sebagai contoh tekstur dengan repetisi garis vertikal.

[FIGURE:evidence_material_wall_fik]
[FIGCAPTION:Contoh Tekstur Dinding FIK]

Contoh tekstur penutup bagian atas bangunan dapat dilihat pada [FIGREF:evidence_material_roof] dalam bentuk pola genteng berwarna cokelat.

[FIGURE:evidence_material_roof]
[FIGCAPTION:Contoh Tekstur Atap]

Representasi permukaan lingkungan pada inventaris ditunjukkan oleh [FIGREF:evidence_material_grass] sebagai salah satu alternatif tekstur rumput.

[FIGURE:evidence_material_grass]
[FIGCAPTION:Contoh Tekstur Rumput]

Elemen bukaan bangunan juga memiliki bukti tekstur tersendiri sebagaimana diperlihatkan pada [FIGREF:evidence_material_window].

[FIGURE:evidence_material_window]
[FIGCAPTION:Contoh Tekstur Jendela]

Metadata yang dapat diverifikasi langsung dari berkas bukti untuk tiga aset representatif dirangkum pada [TABREF:metadata_bukti_aset_representatif]. Resolusi dalam tabel adalah resolusi tangkapan bukti, bukan jumlah polygon atau resolusi model.

[TABLE-ID:metadata_bukti_aset_representatif]
[TABLECAPTION:Metadata Bukti Tiga Aset Representatif]

[TABLE]
Aset | Foto Aktual | Render Aset | Hierarki | Status Bukti
Cipto Mangunkusumo | 5280 × 3016 piksel | 742 × 352 piksel | 693 × 840 piksel | Foto, render, dan hierarki tersedia
M. Yamin | 5296 × 3504 piksel | 472 × 482 piksel | 522 × 627 piksel | Foto, render, dan hierarki tersedia
Wahidin Sudiro Husodo | 3072 × 4096 piksel | 726 × 557 piksel | 645 × 831 piksel | Foto, render, dan hierarki tersedia
[/TABLE]

Empat contoh tekstur yang telah dimasukkan ke draft memiliki metadata berkas sebagaimana dirangkum pada [TABREF:metadata_tekstur_representatif].

[TABLE-ID:metadata_tekstur_representatif]
[TABLECAPTION:Metadata Berkas Tekstur Representatif]

[TABLE]
Berkas | Resolusi Bukti | Keterangan Terverifikasi
`diding_tu_fik.png` | 2048 × 1725 piksel | Berkas gambar tersedia pada inventaris
`atap.jpeg` | 198 × 225 piksel | Berkas gambar tersedia pada inventaris
`rumput.png` | 667 × 664 piksel | Berkas gambar tersedia pada inventaris
`jendela.png` | 1507 × 1003 piksel | Berkas gambar tersedia pada inventaris
[/TABLE]

Keberadaan berkas gambar belum memberikan informasi mengenai konfigurasi Unity Material, shader, nilai tiling, resolusi impor yang dipakai saat build, sumber atau lisensi berkas, dan pemetaan material terhadap masing-masing aset. Versi Unity, perangkat pengujian, ukuran beberapa prefab, serta sebagian metrik GameObject, mesh, dan vertex kini tersedia. Jumlah triangle, material, collider, ukuran build, pengaitan setiap metrik dengan versi scene, dan hasil sesudah optimasi masih menjadi [TBD: lengkapi dari Inspector, Profiler, Build Report, dan path prefab].

## 3.4 Laporan Implementasi Proyek

### 3.4.1 Logbook Implementasi Proyek

Logbook implementasi disusun sebagai rekap bulanan berdasarkan hasil dokumentasi aktual. Rekap ini tidak menggunakan tanggal harian atau riwayat perubahan yang tidak tersedia, melainkan menghubungkan kegiatan, keluaran, dan bukti yang tersedia pada setiap tahap pelaksanaan.

Rekap kegiatan dan bukti pada setiap periode disajikan pada [TABREF:logbook_implementasi].

[TABLE-ID:logbook_implementasi]
[TABLECAPTION:Logbook Implementasi Aset 3D dan Pengelolaan Data]

[TABLE]
Periode | Kegiatan | Hasil | Bukti Dokumentasi | Status
Bulan 1 | Observasi, wawancara, pengambilan foto, dan identifikasi kebutuhan | Kebutuhan aset dan struktur data teridentifikasi | Notulensi wawancara, dokumen riset, dan `images/list_foto/` | Selesai
Bulan 2 | Perancangan ERD, skema, dan pemodelan awal | Struktur database dan bentuk awal aset tersedia | ERD, SQL setup, dan screenshot proses Unity | Selesai
Bulan 3 | Pemodelan, material, tekstur, prefab, dan pengisian seed | Aset serta data gedung atau fasilitas mulai terhubung | Render aset, hierarki, `images/list_material/`, dan seed SQL | Selesai
Bulan 4 | Penyelesaian hierarki, `Pointer`, serta pemetaan nama | GameObject tujuan dan `unity_object_name` tersusun | Hierarki prefab dan screenshot nama objek Unity | Selesai
Bulan 5 | Pemeriksaan constraint, aset, dan konsistensi nama | Temuan integritas dan mismatch terdokumentasi | Screenshot constraint, metrik aset, dan `DatabaseSyncChecker` | Selesai
Bulan 6 | Koreksi, pengujian akhir, dan penyusunan laporan | Bukti implementasi dan hasil pengujian dirangkum | Hasil Black Box, UAT, survei, dan dokumentasi final | Selesai
[/TABLE]

Rekap logbook tersebut menunjukkan hubungan antara aktivitas pada Gantt dan artefak yang tersedia. Status selesai menyatakan bahwa kegiatan dan bukti dokumentasinya telah dimasukkan ke draft; status tersebut tidak memperluas atribusi ke kode API, dashboard, navigasi, atau engine milik anggota lain.

### 3.4.2 Hasil dan Bukti Implementasi Aset 3D Gedung dan Fasilitas

Bukti yang diserahkan memuat render dan tangkapan hierarki aset 3D gedung serta fasilitas yang tersedia pada folder dokumentasi. Sebelas pasangan render dan hierarki yang tersedia digunakan sebagai sampel representatif. Ketersediaan bukti dirangkum pada [TABREF:inventaris_bukti_aset]. Status pada tabel menyatakan kepemilikan serta keberadaan berkas bukti, bukan bahwa seluruh aset telah lulus pengujian visual, performa, atau integrasi.

[TABLE-ID:inventaris_bukti_aset]
[TABLECAPTION:Inventaris Bukti Aset Gedung dan Hierarki]

[TABLE]
No. | Aset | Render Aset | Tangkapan Hierarki | Status Bukti
1 | Abdul Rachman Saleh | `asset_gedung Abdul_Rachman_Saleh.png` | `hierarki_asset gedung_Abdul Rachman_Saleh.png` | Tersedia
2 | Cipto Mangunkusumo | `asset_gedung_Cipto_Mangunkusumo.png` | `hierarki_asset gedung_Cipto Mangunkusumo.png` | Tersedia
3 | Dewi Sartika | `asset_gedung_Dewi_Sartika.png` | `hierarki_asset_gedung_Dewi_Sartika.png` | Tersedia
4 | Jenderal Soedirman | `asset_gedung_Jenderal_Soedirman.png` | `hierarki_asset_gedung_Jenderal_Soedirman.png` | Tersedia
5 | Ki Hajar Dewantara | `asset_gedung_Ki hajar_Dewantara.png` | `hierarki_asset_gedung_Ki_hajar_Dewantara.png` | Tersedia
6 | M. Yamin | `asset_gedung_M.Yamin.png` | `hierarki_asset_gedung_M.Yamin.png` | Tersedia
7 | Masjid | `asset_gedung_Masjid.png` | `hierarki_asset_gedung_Masjid.png` | Tersedia
8 | Muhammad Husni Thamrin | `asset_gedung_muh_husni_tamrin.png` | `hierarki_asset_gedung_Husni_Tamrin.png` | Tersedia
9 | Soepomo | `asset_gedung_Soepomo.png` | `hierarki_asset_gedung_Soepomo.png` | Tersedia
10 | Wahidin Sudiro Husodo | `asset_gedung_wahidin_Sudiro_Husodo.png` | `hierarki_asset_gedung_Wahidin_Sudiro_Husodo.png` | Tersedia
11 | Yos Sudarso | `asset_gedung_Yos Sudarsso.png` | `hierarki_asset_gedung_Yos_Sudarso.png` | Tersedia
[/TABLE]

Representasi aset Cipto Mangunkusumo yang tersedia sebagai bukti diperlihatkan pada [FIGREF:evidence_asset_cipto], sedangkan susunan objeknya terdokumentasi pada [FIGREF:evidence_hierarchy_cipto]. Pasangan bukti tersebut memungkinkan bentuk visual dibandingkan dengan struktur objek pada Unity.

[FIGURE:evidence_asset_cipto]
[FIGCAPTION:Aset 3D Gedung Cipto Mangunkusumo]

[FIGURE:evidence_hierarchy_cipto]
[FIGCAPTION:Hierarki Aset Gedung Cipto Mangunkusumo]

Hasil representasi Gedung M. Yamin ditunjukkan pada [FIGREF:evidence_asset_myamin], sementara daftar objek penyusunnya dapat ditelusuri melalui [FIGREF:evidence_hierarchy_myamin].

[FIGURE:evidence_asset_myamin]
[FIGCAPTION:Aset 3D Gedung M. Yamin]

[FIGURE:evidence_hierarchy_myamin]
[FIGCAPTION:Hierarki Aset Gedung M. Yamin]

Aset dengan susunan fasad yang lebih kompleks terlihat pada [FIGREF:evidence_asset_wahidin], dan struktur hierarkinya direkam pada [FIGREF:evidence_hierarchy_wahidin].

[FIGURE:evidence_asset_wahidin]
[FIGCAPTION:Aset 3D Gedung Wahidin Sudiro Husodo]

[FIGURE:evidence_hierarchy_wahidin]
[FIGCAPTION:Hierarki Aset Gedung Wahidin Sudiro Husodo]

Contoh lain hasil representasi gedung dapat dilihat pada [FIGREF:evidence_asset_dewi]. Dalam bukti hierarki pada [FIGREF:evidence_hierarchy_dewi], prefab Dewi Sartika menampilkan objek `CullingPoint`, child `Pointer`, dan objek tujuan `dewi_sartika` sehingga struktur integrasinya dapat ditelusuri secara visual.

[FIGURE:evidence_asset_dewi]
[FIGCAPTION:Aset 3D Gedung Dewi Sartika]

[FIGURE:evidence_hierarchy_dewi]
[FIGCAPTION:Hierarki Aset Gedung Dewi Sartika]

Bukti visual tersebut memperkuat dokumentasi keberadaan aset dan hierarki. Status kelengkapan metadata tiga aset pembanding visual serta tiga aset dengan pengukuran teknis dirangkum pada [TABREF:status_metadata_aset].

[TABLE-ID:status_metadata_aset]
[TABLECAPTION:Status Kelengkapan Metadata Aset Prioritas]

[TABLE]
Aset | Bukti Tersedia | Metadata Belum Tersedia | Status
Cipto Mangunkusumo | Foto aktual, render, hierarki | Versi prefab, vertex atau triangle, collider, material, ukuran file, hasil uji visual | Bukti visual tersedia; pengukuran teknis belum dilakukan
M. Yamin | Foto aktual, render, hierarki | Versi prefab, vertex atau triangle, collider, material, ukuran file, hasil uji visual | Bukti visual tersedia; pengukuran teknis belum dilakukan
Wahidin Sudiro Husodo | Foto aktual, render, hierarki | Versi prefab, vertex atau triangle, collider, material, ukuran file, hasil uji visual | Bukti visual tersedia; pengukuran teknis belum dilakukan
Ki Hajar Dewantara | Referensi visual, render, hierarki, ukuran prefab, GameObject, mesh, dan vertex | Triangle, material, collider, dan hasil uji visual | Pengukuran teknis parsial tersedia
Dewi Sartika | Referensi visual, render, hierarki, objek `Pointer`, ukuran prefab, GameObject, mesh, dan vertex | Triangle, material, collider, dan hasil uji visual | Struktur integrasi dan pengukuran teknis parsial tersedia
Jenderal Soedirman | Render, hierarki, ukuran prefab, GameObject, mesh, dan vertex | Foto aktual terverifikasi, triangle, material, collider, dan hasil uji visual | Pengukuran teknis parsial tersedia; referensi aktual belum ada
[/TABLE]

Aset lain dalam scope juga dibuat dan ditata penulis serta telah memiliki bukti render atau hierarki sesuai dokumentasi yang tersedia. Namun, seluruh aset belum memiliki catatan kondisi akhir, keputusan desain, masalah yang ditemukan, tindakan perbaikan, dan hasil pemeriksaan formal. Karena itu, subbab ini membedakan atribusi pekerjaan dari keberhasilan teknis seluruh aset.

### 3.4.3 Hasil dan Bukti Rancangan Skema serta Pengelolaan Data

Bukti basis data yang terdapat dalam repository laporan dirangkum pada [TABREF:status_bukti_basis_data]. Ringkasan ini difokuskan pada skema dan ERD yang dirancang penulis, pengelolaan record gedung atau fasilitas, serta pemetaan `unity_object_name`.

[TABLE-ID:status_bukti_basis_data]
[TABLECAPTION:Status Bukti Rancangan Skema dan Pengelolaan Data]

[TABLE]
Komponen | Bukti Tersedia | Temuan | Bukti yang Masih Diperlukan
ERD | Gambar ERD pada Subbab 2.3.4, berkas sumber SVG, dan `images/ERD_navigasi_peta_kampus.svg` | Empat tabel inti dan lima tabel denah dapat ditelusuri secara visual; `admin_users`, `audit_logs`, dan `web_analytics_log` tercatat sebagai tabel aktif tanpa relasi langsung pada diagram inti | Tanggal, versi, serta konfirmasi terhadap skema produksi
Struktur data dan constraint | Berkas SQL setup, representasi DDL pada Subbab 3.2.3, serta gambar inventaris constraint pada Subbab 3.3.1 | Primary key, beberapa unique constraint, foreign key, dan dua aturan `ON DELETE SET NULL` dapat ditelusuri; berkas SQL tidak dijalankan saat penyusunan laporan | Versi dan tanggal berkas SQL, seluruh baris constraint produksi, catatan keputusan desain, dan status penerapan pada Supabase aktif
Pengelolaan record | Gambar contoh nilai `unity_object_name` gedung dan fasilitas pada Subbab 3.2.5 serta inventaris seed 311 record | Kolom, contoh identifier, jumlah fasilitas per induk, dan temuan kualitas data dapat ditelusuri | Berkas seed, ekspor produksi, pasangan nama tampilan–identifier, serta bukti sebelum dan sesudah perubahan beserta tanggal
Pemetaan aset–data | Hierarki prefab serta gambar hasil `DatabaseSyncChecker` pada Subbab 3.3.2 dan 3.5.5 | Identifier dibandingkan antara record dan GameObject tujuan pada dua tangkapan dengan cakupan berbeda | Daftar pemetaan seluruh GameObject dalam scene, daftar koreksi, versi scene atau endpoint, tanggal, dan retest terkontrol
[/TABLE]

Inventaris seed terbaru yang diberikan penulis memuat 311 record fasilitas pada kelompok induk yang tercantum di dalam seed. Ringkasannya disajikan pada [TABREF:inventaris_seed_fasilitas] sebagai isi seed yang belum otomatis dianggap sama dengan data produksi atau kondisi lapangan terbaru.

[TABLE-ID:inventaris_seed_fasilitas]
[TABLECAPTION:Ringkasan Inventaris Fasilitas pada Seed Data]

[TABLE]
Referensi Seed | Induk Fasilitas | Jumlah Record | Cakupan Lantai
1 | Gedung Rektorat (Jenderal Soedirman) | 36 | Lantai 1–4
2 | Gedung Dr. Soepomo | 24 | Lantai 1–4
3 | Gedung Dr. Wahidin Sudiro Husodo | 38 | Lantai 1–4
4 | Gedung Dr. Cipto Mangunkusumo | 38 | Lantai 1–4
5 | Gedung Abdul Rahman Saleh | 25 | Lantai 1–4
6 | Gedung Ki Hadjar Dewantara | 25 | Lantai 1–4 dan satu record tanpa lantai yang ditentukan
7 | Gedung Muh. Husni Thamrin | 37 | Lantai 1–4
8 | Gedung Muhammad Yamin | 20 | Lantai 1–4
10 | Gedung R.A. Kartini | 24 | Lantai 1–4
13 | Gedung Dewi Sartika | 26 | Lantai 1–4
17 | Gedung Soetomo | 18 | Lantai 1–3 menurut record
Total | Kelompok induk yang tercantum dalam seed | 311 | Berdasarkan seed terbaru yang diberikan penulis
[/TABLE]

Pemeriksaan terhadap daftar tersebut menghasilkan catatan kualitas data yang dirangkum pada [TABREF:temuan_kualitas_seed_fasilitas]. Catatan dibedakan antara fakta pada seed terbaru dan hal yang masih memerlukan verifikasi terhadap data produksi atau kondisi lapangan.

[TABLE-ID:temuan_kualitas_seed_fasilitas]
[TABLECAPTION:Temuan Awal Kualitas Data pada Inventaris Fasilitas]

[TABLE]
Temuan | Bukti pada Inventaris | Dampak | Tindak Lanjut
Pemetaan Masjid | Masjid merupakan aset visual terpisah, sedangkan record fasilitasnya menggunakan `id_gedung = 6` | Nama aset visual dan induk database dapat berbeda bila tidak dicatat secara eksplisit | Pertahankan catatan pemetaan aset visual–record pada inventaris dan pengujian
Pemisahan entitas gedung | Gedung Soepomo, Gedung Soetomo, Yos Sudarso, RA Kartini, Lapangan Basket, parkir, lapangan, dan entitas lain dicatat sebagai record gedung yang berbeda; `id_gedung = 17` adalah Gedung Soetomo pada seed terbaru | Penyamaan nama atau fungsi dapat menghasilkan pemetaan yang salah | Cocokkan nama record gedung dengan GameObject dan data fasilitas pada saat sinkronisasi
Kemutakhiran nama belum terjamin | Pengumpulan lapangan dilakukan mandiri dengan informasi ruangan yang terbatas | Nama atau fungsi ruang dapat berbeda dari kondisi terbaru | Verifikasi melalui pengelola gedung, denah terbaru, atau sumber institusi serta catat tanggal verifikasi
[/TABLE]

Kontribusi penulis pada bagian basis data adalah perancangan skema dan ERD, pengelolaan record gedung atau fasilitas, serta pemetaan `unity_object_name`. RLS dan audit log hanya menjadi konteks sistem, sedangkan API, dashboard, dan autentikasi tetap diatribusikan kepada anggota integrator. Keberhasilan pengelolaan data akan dinilai melalui contoh perubahan record, integritas relasi, konsistensi nama, dan hasil retest, bukan melalui kepemilikan migration RLS atau trigger.

## 3.5 Hasil Pengujian Proyek

### 3.5.1 Pengujian Fungsional Bersama

<!-- PIPELINE:INCLUDE content/shared/testing/blackbox.md -->

### 3.5.2 Pengujian Integritas dan Relasi Basis Data

Skenario pengujian integritas memeriksa foreign key, kolom wajib, batasan unik, dan perilaku perubahan atau penghapusan record induk. Constraint seperti `NOT NULL`, `UNIQUE`, dan `FOREIGN KEY` perlu diuji pada migration yang sama dengan versi produk yang dilaporkan (PostgreSQL Global Development Group 2026a). Tangkapan kueri katalog telah mengonfirmasi sebagian struktur constraint produksi, tetapi berkas migration dan hasil percobaan pelanggaran constraint belum tersedia. Oleh karena itu, matriks pada [TABREF:hasil_uji_integritas_db] membedakan verifikasi struktur dari pengujian perilaku.

[TABLE-ID:hasil_uji_integritas_db]
[TABLECAPTION:Matriks Pengujian Integritas dan Relasi Basis Data]

[TABLE]
Skenario | Input | Hasil yang Diharapkan | Hasil Aktual | Status | Bukti yang Diperlukan
Inventaris struktur constraint | Kueri katalog constraint pada tabel `gedung`, `fakultas`, `fasilitas`, dan `program_studi` | Primary key, unique constraint, foreign key, dan aturan penghapusan dapat ditelusuri | 12 baris ditampilkan; bagian yang terlihat mengonfirmasi beberapa PK, UNIQUE, FK, dan `ON DELETE SET NULL` | Bukti struktur tersedia | Gambar inventaris constraint pada Subbab 3.3.1, ekspor 12 baris penuh, serta migration terkait
Pemetaan record Masjid | Bandingkan nama aset visual, `id_gedung`, dan tabel `fasilitas` | Record fasilitas memiliki induk yang sesuai dengan skema data | Masjid merupakan aset visual terpisah dengan record fasilitas pada `id_gedung = 6` | Sesuai pada seed; produksi belum diverifikasi | Seed terbaru, ekspor produksi, dan bukti pemetaan aset
Pemetaan record Soetomo | Bandingkan nama gedung, `id_gedung`, dan tabel `gedung` | Record mengarah ke entitas gedung yang benar | Seed terbaru menetapkan `id_gedung = 17` sebagai Gedung Soetomo, terpisah dari Lapangan Basket | Sesuai pada seed; produksi belum diverifikasi | Seed terbaru, ekspor produksi, dan retest konsumsi data
FK fasilitas ke gedung | Insert `fasilitas.id_gedung` yang tidak ada | Operasi ditolak oleh foreign key | Belum dieksekusi | Menunggu eksekusi | Query, pesan galat, dan tangkapan Supabase
FK fakultas ke gedung utama | Insert `fakultas.id_gedung_utama` yang tidak ada | Operasi ditolak oleh foreign key | Belum dieksekusi | Menunggu eksekusi | Query, pesan galat, dan tangkapan Supabase
FK program studi ke fakultas | Insert `program_studi.id_fakultas` yang tidak ada | Operasi ditolak oleh foreign key | Belum dieksekusi | Menunggu eksekusi | Query, pesan galat, dan tangkapan Supabase
Keunikan nama objek | Insert dua nilai `unity_object_name` yang sama | Record kedua ditolak oleh unique constraint | Belum dieksekusi | Menunggu eksekusi | Query, pesan galat, dan nama constraint
Kolom wajib | Insert record tanpa kolom `NOT NULL` | Operasi ditolak | Belum dieksekusi | Menunggu eksekusi | Query dan pesan galat
Perilaku penghapusan induk | Hapus gedung atau fakultas yang masih dirujuk | Hasil mengikuti aturan `ON DELETE` pada migration aktual | `ON DELETE SET NULL` terlihat pada dua foreign key; perilaku belum dieksekusi | Struktur terverifikasi sebagian; eksekusi menunggu | DDL aktual, data sebelum dan sesudah, serta tangkapan hasil
[/TABLE]

### 3.5.3 Verifikasi Konteks RLS dan Trigger Audit Log

Skenario basis data pada [TABREF:hasil_black_box] digunakan sebagai konteks untuk memastikan record yang dikelola penulis tetap dibaca dan diubah melalui jalur sistem yang semestinya. Bagian ini tidak menguji atau mengatribusikan policy RLS maupun kode trigger kepada Dwikhi, sedangkan ringkasan hasil bersama disajikan pada [TABREF:hasil_uji_rls_audit].

[TABLE-ID:hasil_uji_rls_audit]
[TABLECAPTION:Ringkasan Verifikasi Konteks RLS dan Trigger Audit Log]

[TABLE]
Skenario Sistem | Hasil Aktual | Status Bersama | Relevansi terhadap Pekerjaan Dwikhi
Pembacaan data publik | Pengujian bersama melaporkan akses baca berjalan | Lulus pada pengujian bersama | Record gedung atau fasilitas dapat dikonsumsi sistem
Penolakan operasi anonim | Pengujian bersama melaporkan operasi tanpa autentikasi ditolak | Lulus pada pengujian bersama | Perubahan record dilakukan melalui jalur terautentikasi
Pengelolaan data terautentikasi | Fungsi dashboard diuji pada pengujian bersama | Lulus pada pengujian bersama | Penulis dapat mengelola data melalui komponen sistem yang tersedia
Pencatatan perubahan | Tangkapan dashboard memperlihatkan Create, Update, dan Delete | Bukti konteks tersedia | Perubahan record dapat ditelusuri, tetapi kode trigger bukan kontribusi penulis
[/TABLE]

### 3.5.4 Pengujian Visual dan Teknis Aset 3D

Pengujian aset memeriksa kesesuaian bentuk, posisi, skala, orientasi, material, tekstur, collider, struktur prefab, dan lokasi titik tujuan. Hasil pemeriksaan teknis dibandingkan dengan spesifikasi pada Subbab 3.3.3 untuk menunjukkan aset yang memenuhi kriteria serta tindakan optimasi yang dilakukan.

Foto kondisi aktual, render aset, tangkapan hierarki, inventaris tekstur, ukuran prefab, dan pengukuran parsial tiga aset dapat digunakan sebagai input pemeriksaan. Namun, bukti tersebut belum memuat kriteria penerimaan, hasil aktual per butir, status lulus atau gagal, masalah yang ditemukan, dan hasil pengujian ulang. Oleh karena itu, status pada [TABREF:status_uji_visual_aset] menyatakan kesiapan bukti, bukan kelulusan aset.

[TABLE-ID:status_uji_visual_aset]
[TABLECAPTION:Status Pengujian Visual dan Teknis Aset 3D]

[TABLE]
Cakupan | Input Bukti | Hasil yang Diharapkan | Hasil Aktual | Status | Bukti Lanjutan
Cipto Mangunkusumo | Foto, render, hierarki | Bentuk dapat dibandingkan dan struktur dapat ditelusuri | Tiga jenis bukti tersedia; checklist belum diisi | Bukti tersedia, belum dinilai formal | Versi scene, checklist, temuan, koreksi, retest
M. Yamin | Foto, render, hierarki | Bentuk dapat dibandingkan dan struktur dapat ditelusuri | Tiga jenis bukti tersedia; checklist belum diisi | Bukti tersedia, belum dinilai formal | Versi scene, checklist, temuan, koreksi, retest
Wahidin Sudiro Husodo | Foto, render, hierarki | Bentuk dapat dibandingkan dan struktur dapat ditelusuri | Tiga jenis bukti tersedia; checklist belum diisi | Bukti tersedia, belum dinilai formal | Versi scene, checklist, temuan, koreksi, retest
Ki Hajar Dewantara, Dewi Sartika, dan Jenderal Soedirman | Render, hierarki, ukuran prefab, GameObject, mesh, dan vertex | Kompleksitas aset tercatat dan dapat dibandingkan | Metrik parsial tiga aset tersedia; triangle, material, collider, dan kriteria batas belum tersedia | Pengukuran parsial, belum dinilai formal | Inspector lengkap, kriteria penerimaan, temuan, koreksi, dan retest
Aset lain dalam scope | Render dan hierarki | Visual, prefab, material, collider, dan titik tujuan memenuhi kriteria | Bukti render atau hierarki tersedia sesuai dokumentasi; checklist lengkap belum diisi | Bukti parsial, belum dinilai formal | Foto pembanding terverifikasi dan checklist seluruh aset yang memiliki GameObject
Performa build | Ukuran prefab, Profiler, atau Build Report serta gambar spesifikasi perangkat pada Subbab 3.3.3 | Metrik aset dan pengaruhnya terhadap build tercatat | Perangkat uji dan ukuran prefab tersedia; pengaruh terhadap build belum diukur | Belum diuji pada build | Profiler, versi scene, ukuran build sebelum-sesudah, dan Build Report
[/TABLE]

### 3.5.5 Validasi Konsistensi Aset dan Basis Data

Validasi konsistensi memeriksa bahwa setiap `unity_object_name` dalam cakupan memiliki tepat satu padanan GameObject tujuan dan tidak terdapat nama ganda. Pengujian juga perlu memastikan perbedaan kapitalisasi ditangani sesuai kontrak runtime tanpa mengabaikan konvensi penulisan proyek. Hasil yang terlihat pada [FIGREF:impl_sync_db_checker] dirangkum pada [TABREF:hasil_sync_checker_awal].

[TABLE-ID:hasil_sync_checker_awal]
[TABLECAPTION:Hasil Awal Pemeriksaan Konsistensi Nama]

[TABLE]
Indikator | Hasil Aktual | Interpretasi
Nama pada basis data | 97 | Cakupan data yang dibandingkan pada tangkapan
Ditemukan pada scene | 57 | Memiliki padanan yang ditemukan alat pemeriksa
Hanya pada basis data | 40 | Tidak ditemukan padanannya pada scene
Hanya pada scene | 18 | Tidak ditemukan padanannya pada basis data
Status keseluruhan | Belum konsisten | Masih terdapat mismatch pada kedua arah
[/TABLE]

Tangkapan awal memperlihatkan beberapa contoh nama yang belum cocok, tetapi tidak memuat versi endpoint, versi *scene*, waktu pengujian, atau hasil ekspor lengkap. Angka di atas karena itu diperlakukan sebagai kondisi pada satu tangkapan, bukan baseline terkontrol.

Pemeriksaan lain yang terlihat pada [FIGREF:evidence_sync_checker_lanjutan] mencakup 323 nama pada basis data, 320 nama ditemukan pada *scene*, 3 nama hanya terdapat pada basis data, dan 14 nama hanya terdapat pada *scene*. Bukti ini menunjukkan adanya pemeriksaan lanjutan dengan cakupan lebih besar, tetapi tidak dapat langsung dinyatakan sebagai perbaikan dari hasil sebelumnya karena total nama, versi *scene*, endpoint, dan tanggal tidak sama-sama tercatat.

[FIGURE:evidence_sync_checker_lanjutan]
[FIGCAPTION:Hasil Pemeriksaan Lanjutan Konsistensi Nama Aset dan Basis Data]

Angka pemeriksaan lanjutan dirangkum pada [TABREF:hasil_sync_checker_lanjutan] tanpa mengubahnya menjadi klaim kelulusan.

[TABLE-ID:hasil_sync_checker_lanjutan]
[TABLECAPTION:Hasil Pemeriksaan Lanjutan Konsistensi Nama]

[TABLE]
Indikator | Hasil Aktual | Interpretasi
Nama pada basis data | 323 | Cakupan data yang dibandingkan pada tangkapan lanjutan
Ditemukan pada scene | 320 | Memiliki padanan yang ditemukan alat pemeriksa
Hanya pada basis data | 3 | Masih terdapat nama basis data tanpa padanan yang ditemukan
Hanya pada scene | 14 | Masih terdapat nama scene tanpa padanan basis data
Status keseluruhan | Belum sepenuhnya konsisten | Masih terdapat mismatch pada kedua arah dan metadata pengujian belum lengkap
[/TABLE]

`DatabaseSyncChecker` dikembangkan oleh Faiz dan digunakan Dwikhi untuk menemukan mismatch. Hasil kerja Dwikhi yang masih perlu dibuktikan adalah daftar koreksi nama pada aset atau data serta retest terkontrol pada *scene*, endpoint, dan basis data dengan versi pengujian yang dicatat.

### 3.5.6 User Acceptance Testing

<!-- PIPELINE:INCLUDE content/shared/testing/uat.md -->

### 3.5.7 Implementasi Hasil User Acceptance Testing

<!-- PIPELINE:INCLUDE content/shared/testing/uat-revisions.md -->

Kontribusi yang relevan dengan peran aset dan pengelolaan data terutama berkaitan dengan kelengkapan nama dan deskripsi fasilitas, konsistensi pemetaan objek, label ruang yang menggunakan nama tampilan, serta pemeriksaan kelengkapan data. Status implementasi dan hasil retest tidak boleh dinyatakan selesai sebelum bukti pada build produk yang sama tersedia.

---

# BAB IV PENUTUP

## 4.1 Kesimpulan

Kesimpulan yang dapat dirumuskan berdasarkan bukti yang telah tersedia adalah sebagai berikut:

1. Penulis membuat dan menata seluruh aset 3D gedung dan fasilitas yang memiliki GameObject pada scene Unity menggunakan observasi visual dan dokumentasi fotografis tanpa pengukuran dimensi instrumental. Sebelas pasangan render dan hierarki yang tersedia diposisikan sebagai sampel bukti representatif, bukan batas jumlah aset. Inventaris 37 berkas material dan tekstur, Unity 6.4, perangkat pengujian, ukuran prefab, serta GameObject, mesh, dan vertex untuk tiga aset telah tercatat; triangle, material, collider, Build Report, dan hasil optimasi masih diperlukan untuk penilaian teknis lengkap.
2. Penulis menyusun hierarki prefab, child `Pointer`, dan GameObject tujuan serta menetapkan `unity_object_name` untuk memisahkan geometri visual dari identifier navigasi. Hierarki Dewi Sartika memperlihatkan salah satu contoh penerapan melalui objek tujuan `dewi_sartika`.
3. Kontribusi basis data penulis meliputi perancangan 11 tabel aktif dalam ERD serta pengelolaan record gedung atau fasilitas. Seed terbaru memuat 19 entitas gedung dan 311 fasilitas. Masjid merupakan aset visual terpisah dengan record fasilitas pada `id_gedung = 6`, sedangkan Soepomo dan Soetomo merupakan entitas berbeda dan `id_gedung = 17` pada seed terbaru adalah Gedung Soetomo. Verifikasi data produksi dan pengujian perilaku constraint masih perlu dilengkapi.
4. RLS dan trigger audit log memengaruhi data yang dikelola penulis, tetapi keduanya merupakan konteks sistem dan bukan rancangan atau implementasi Dwikhi. Hasil pengujian bersama hanya digunakan untuk memastikan jalur baca, perubahan data, dan pencatatan sistem tersedia.
5. Dwikhi menggunakan `DatabaseSyncChecker` buatan Faiz untuk memeriksa konsistensi nama. Tangkapan pertama mencatat 97 nama pada basis data, 57 ditemukan pada *scene*, 40 hanya terdapat pada basis data, dan 18 hanya terdapat pada *scene*. Tangkapan lain mencatat 323 nama, 320 ditemukan, 3 hanya pada basis data, dan 14 hanya pada *scene*. Kedua hasil belum dapat dibandingkan sebagai sebelum-sesudah karena versi *scene*, endpoint, waktu, dan daftar koreksi tidak tercatat bersama.

## 4.2 Saran

Saran pengembangan awal adalah sebagai berikut:

1. Menyimpan ERD, kamus data, dan catatan perubahan skema dengan versi yang dapat ditelusuri agar keputusan perancangan dapat direplikasi.
2. Menambahkan validasi format dan keunikan `unity_object_name` pada form administrator serta pada pipeline integrasi sebelum build.
3. Menetapkan checklist teknis aset yang mencakup skala, pivot, collider, material, tekstur, jumlah polygon, dan posisi titik tujuan.
4. Menggunakan `DatabaseSyncChecker` buatan Faiz sebagai pemeriksaan wajib setiap kali terdapat perubahan data gedung, fasilitas, atau hierarki *scene*.
5. Melengkapi rekap logbook bulanan, screenshot proses, contoh record sebelum dan sesudah perubahan, hasil pengujian, dan retest agar kontribusi penulis dapat ditelusuri secara akademik.

---

# DAFTAR PUSTAKA

PostgreSQL Global Development Group (2026a). _PostgreSQL 18 documentation: Constraints_. https://www.postgresql.org/docs/18/ddl-constraints.html

PostgreSQL Global Development Group (2026b). _PostgreSQL 18 documentation: Row security policies_. https://www.postgresql.org/docs/18/ddl-rowsecurity.html

PostgreSQL Global Development Group (2026c). _PostgreSQL 18 documentation: Trigger functions_. https://www.postgresql.org/docs/18/plpgsql-trigger.html

Supabase (2026). _Row Level Security_. https://supabase.com/docs/guides/database/postgres/row-level-security

Unity Technologies (2026a). _Unity 6 Manual: Prefabs_. https://docs.unity3d.com/6000.0/Documentation/Manual/Prefabs.html

Unity Technologies (2026b). _Unity 6 Manual: ProBuilder_. https://docs.unity3d.com/6000.0/Documentation/Manual/com.unity.probuilder.html

Unity Technologies (2026c). _Unity 6 Manual: Memory Profiler module reference_. https://docs.unity3d.com/6000.0/Documentation/Manual/ProfilerMemory.html

Afiifah, K., Azzahra, Z. F., dan Anggoro, A. D. (2022). Analisis teknik Entity-Relationship Diagram dalam perancangan database: Sebuah literature review. _INTECH (Informatika dan Teknologi)_, 3(1), 8–11. https://doi.org/10.54895/intech.v3i1.1261

Aliyah, A., Hartono, N., dan Muin, A. A. (2025). Penggunaan User Acceptance Testing (UAT) pada pengujian sistem informasi pengelolaan keuangan dan inventaris barang. _Switch: Jurnal Sains dan Teknologi Informasi_, 3(2), 42–58. https://doi.org/10.62951/switch.v3i1.330

Jamaludin, J., dan Saepuloh, L. (2024). Tren riset twin digital smart campus. _Sang Pencerah: Jurnal Ilmiah Universitas Muhammadiyah Buton_, 10(2), 408–425. https://doi.org/10.35326/pencerah.v10i2.5317

Maulida, M., Zahro, F., Hakim, R., dan Akbar, M. S. (2025). Pengujian black box testing pada sistem website pemesanan online Toko Ayam Krispy. _Jurnal Media Akademik (JMA)_, 3(5). https://doi.org/10.62281/v3i5.1908

Muharam, Y., Anggara, M. B., dan Hanafi, T. J. (2023). Implementasi peta 3 dimensi menggunakan metode IMSDD (Interactive Multimedia System Design and Development) dan WebGL API berbasis web (Studi kasus di SMP Karya Pembangunan 2 Majalaya). _COMPUTING: Jurnal Informatika_, 10(1), 37–42. https://doi.org/10.55222/computing.v10i01.1155

Pricillia, T., dan Zulfachmi (2021). Perbandingan metode pengembangan perangkat lunak (Waterfall, Prototype, RAD). _Jurnal Bangkit Indonesia_, 10(1), 6–12. https://doi.org/10.52771/bangkitindonesia.v10i1.153

Putra, I. G. W. W., Dharma, E. M., dan Permana, P. T. H. (2026). Implementasi relational database dengan Row-Level Security (RLS) pada sistem inventory menggunakan Supabase dan React Native Expo (Studi kasus Bengkel Sari Merta). _JATI (Jurnal Mahasiswa Teknik Informatika)_, 10(2), 2443–2448. https://doi.org/10.36040/jati.v10i2.17551

Taurusta, C., Asiddiq, A. M., Suprianto, S., dan Setiawan, H. (2024). Visualisasi gedung kampus 1 Universitas Muhammadiyah Sidoarjo menggunakan augmented reality sebagai media informasi. _Journal of Technology and System Information_, 1(1), 55–70. https://doi.org/10.47134/jtsi.v1i1.2146

UPNVJ. (2022). Lokasi Kampus UPN Veteran Jakarta. https://www.upnvj.ac.id/id/tentang-upn/lokasi-kampus.html

UPNVJ. (2025a). Kantin. https://www.upnvj.ac.id/id/fasilitas/kantin.html

UPNVJ. (2026). Rapat koordinasi Humas UPNVJ 2026: Fokus strategi komunikasi digital dan media sosial perguruan tinggi. https://www.upnvj.ac.id/id/berita/2026/02/rapat-koordinasi-humas-upnvj-2026-fokus-strategi-komunikasi-digital-dan-media-sosial-perguruan-tinggi.html

---

# LAMPIRAN 1. Surat Pernyataan Keaslian

[TBD: masukkan format resmi surat pernyataan keaslian, tanggal, dan tanda tangan Dwikhi]

---

# LAMPIRAN 2. Dokumentasi Penyerahan Pakta Integritas kepada UPA TIK

Salinan pakta integritas yang telah diserahkan tidak berada dalam arsip penulis. Bukti yang tersedia berupa foto dokumentasi penyerahan dokumen kepada staf UPA TIK; lampiran ini tidak dimaksudkan sebagai pengganti salinan dokumen bertanda tangan atau surat keterangan resmi dari institusi. Identitas staf, nomor surat, tanggal pengesahan, dan status persetujuan tidak disimpulkan dari foto.

Foto kegiatan tersebut dirujuk pada [FIGREF:foto_penyerahan_pakta_upa_tik].

[FIGURE:foto_penyerahan_pakta_upa_tik]
[FIGCAPTION:Dokumentasi Penyerahan Pakta Integritas kepada UPA TIK]

---

# LAMPIRAN 3. Bukti Pemodelan dan Penataan Aset 3D

Bukti awal yang telah tersedia terdiri atas:

1. Dua puluh satu berkas referensi visual pada `images/list_foto/`, yang digunakan sebagai sampel dokumentasi kondisi gedung dan fasilitas.
2. Tiga puluh tujuh berkas material dan tekstur pada `images/list_material/`.
3. Sebelas render aset gedung, sebelas tangkapan hierarki sebagai sampel representatif, dan satu tangkapan proses pengerjaan pada `images/list_prefab_gedung_&_hierarki_dan_prroses_pengerjaan/`.
4. Satu tangkapan riwayat perubahan pada `images/riwayat_pengerjaan.png`.
5. Satu tangkapan Unity 6.4 pada `images/versi_unity.jpeg`.
6. Satu tangkapan spesifikasi perangkat pengujian pada `images/Perangkat_uji.png`.
7. Satu inventaris ukuran prefab pada `images/data/Ukuran__file_prefab.png`.
8. Tiga tangkapan pengukuran GameObject, mesh, dan vertex untuk Ki Hajar Dewantara, Dewi Sartika, dan Jenderal Soedirman.

[TBD: lengkapi identitas pengambil gambar, tanggal dan lokasi pengambilan, sumber gambar yang bukan foto lapangan terverifikasi, sumber atau lisensi material dan tekstur, triangle, jumlah material, collider, versi scene yang diuji, dan Build Report]

---

# LAMPIRAN 4. Skema Basis Data dan Bukti Pengelolaan Data

Bukti yang sudah tersedia adalah diagram empat tabel inti data akademik dan fasilitas, diagram lima tabel denah navigasi, berkas SQL setup, serta representasi struktur 11 tabel aktif pada Subbab 3.2.3. Bukti lain mencakup tangkapan 12 baris constraint produksi, contoh kolom dan nilai `unity_object_name`, serta inventaris seed terbaru berisi 311 record fasilitas pada 19 entitas gedung. Daftar rinci fasilitas per gedung dan lantai dimuat setelah paragraf ini. Lampiran masih memerlukan `[TBD: versi dan tanggal ERD serta berkas SQL setup]`, `[TBD: ekspor constraint produksi lengkap dan status penerapan DDL]`, `[TBD: kamus data dan catatan keputusan desain]`, `[TBD: ekspor produksi serta bukti sebelum dan sesudah koreksi atau pemetaan]`, `[TBD: daftar pemetaan nama tampilan dan unity_object_name pada seluruh GameObject dalam scope]`, serta `[TBD: retest terkontrol setelah koreksi]`. SQL policy RLS dan trigger audit tidak menjadi bukti wajib kontribusi Dwikhi.

<!-- PIPELINE:INCLUDE content/roles/dwikhi/facility-seed-inventory.md -->

---

# LAMPIRAN 5. Logbook dan Bukti Pengujian

Subbab 3.4.1 memuat rekap logbook bulanan yang disusun berdasarkan dokumentasi aktual, bukan logbook harian. Matriks pengujian integritas, visual aset, dan konsistensi nama telah disiapkan pada Subbab 3.5, sedangkan RLS serta audit log hanya diringkas dari pengujian sistem bersama. Bukti yang tersedia meliputi hasil Black Box dan UAT bersama pada `Hasil UAT/`, survei 21 responden, inventaris constraint, dua tangkapan `DatabaseSyncChecker` dengan cakupan berbeda, serta metrik parsial tiga aset. Lampiran ini masih memerlukan `[TBD: query serta pesan galat uji foreign key, unique constraint, NOT NULL, dan ON DELETE]`, `[TBD: checklist visual seluruh aset dalam scope]`, `[TBD: daftar koreksi mismatch]`, dan `[TBD: retest pada scene, endpoint, dan basis data dengan versi pengujian yang dicatat]`.

Instrumen UAT tertutup dan indeks bukti pengujian bersama disajikan setelah uraian ini. Instrumen tersebut merupakan bukti produk bersama dan tidak digunakan sebagai hasil pengujian teknis khusus aset atau basis data Dwikhi.

<!-- PIPELINE:INCLUDE content/shared/testing/appendix-instruments.md -->

---

# LAMPIRAN 6. Mockup Antarmuka sebagai Konteks Integrasi

Bagian lampiran ini memuat mockup yang tidak dibahas pada Subbab 2.3.7 karena tidak menunjukkan kontribusi utama penulis. Konteks autentikasi administrator diperlihatkan pada [FIGREF:mockup_login_admin].

[FIGURE:mockup_login_admin]
[FIGCAPTION:Halaman Login Admin]

Konteks perubahan dan penghapusan record gedung masing-masing diperlihatkan pada [FIGREF:mockup_modal_edit_gedung] dan [FIGREF:mockup_modal_hapus_gedung].

[FIGURE:mockup_modal_edit_gedung]
[FIGCAPTION:Modal Update Data Gedung]

[FIGURE:mockup_modal_hapus_gedung]
[FIGCAPTION:Modal Konfirmasi Hapus Data Gedung]

Komponen analitik pada area administrator diperlihatkan pada [FIGREF:mockup_admin_traffic] sebagai konteks komponen dashboard di luar lingkup basis data utama laporan ini.

[FIGURE:mockup_admin_traffic]
[FIGCAPTION:Traffic Website Admin]

Rancangan bagian pembuka halaman publik dan ringkasan lalu lintas masing-masing ditunjukkan pada [FIGREF:mockup_hero_section] dan [FIGREF:mockup_public_traffic].

[FIGURE:mockup_hero_section]
[FIGCAPTION:Hero Section]

[FIGURE:mockup_public_traffic]
[FIGCAPTION:Public Traffic Statistics Website]

Konsumsi data fasilitas secara lebih rinci dirancang melalui modal daftar pada [FIGREF:mockup_modal_list_fasilitas] dan modal detail pada [FIGREF:mockup_modal_detail_fasilitas].

[FIGURE:mockup_modal_list_fasilitas]
[FIGCAPTION:Modal List Fasilitas dan Aset]

[FIGURE:mockup_modal_detail_fasilitas]
[FIGCAPTION:Modal Fasilitas dan Aset]

Bagian penutup halaman publik diperlihatkan pada [FIGREF:mockup_footer] untuk melengkapi konteks rancangan antarmuka.

[FIGURE:mockup_footer]
[FIGCAPTION:Bagian Footer]
