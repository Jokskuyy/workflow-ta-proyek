# PERANCANGAN ASSET 3D DAN PENGELOLAAN DATABASE
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
LAMPIRAN 3. Bukti Pemodelan dan Penataan Asset 3D
LAMPIRAN 4. Skema Database dan Bukti Pengelolaan Data
LAMPIRAN 5. Logbook dan Bukti Pengujian
LAMPIRAN 6. Mockup Antarmuka sebagai Konteks Integrasi

---

# BAB I PENDAHULUAN

## 1.1 Latar Belakang

<!-- PIPELINE:INCLUDE content/shared/bab1/latar-belakang-umum.md -->

Visualisasi lingkungan kampus dalam bentuk tiga dimensi dapat membantu penyajian hubungan spasial secara lebih interaktif dibandingkan denah statis. Penelitian terdahulu menunjukkan bahwa visualisasi gedung berbasis teknologi tiga dimensi dan WebGL dapat digunakan sebagai media informasi lokasi, sedangkan kajian mengenai *digital twin smart campus* menempatkan representasi digital lingkungan kampus sebagai bagian dari transformasi layanan pendidikan tinggi (Jamaludin et al. 2024; Muharam et al. 2023; Taurusta et al. 2024). Dalam proyek ini, manfaat visualisasi tersebut bergantung pada dua fondasi yang saling terkait, yaitu asset 3D yang merepresentasikan lingkungan fisik kampus dan struktur data yang menyimpan identitas gedung serta fasilitas secara konsisten.

Dalam *Unity*, *scene* merupakan ruang kerja yang memuat lingkungan aplikasi, sedangkan *GameObject* merupakan unit objek yang dapat diberi komponen dan disusun dalam hubungan induk-anak. *Prefab* adalah templat *GameObject* beserta komponen dan susunan *child*-nya yang dapat digunakan kembali, sehingga hierarki dan konvensi penamaan menjadi bagian penting dalam pemeliharaan objek (Unity Technologies 2026a). *Asset* 3D yang tidak mengikuti struktur seragam akan menyulitkan proses integrasi dengan logika navigasi. Pada sisi lain, data gedung dan fasilitas yang tidak memiliki relasi, identitas integrasi, serta aturan akses yang jelas berisiko menimbulkan ketidaksesuaian antara informasi pada *dashboard* dan objek pada *scene* *Unity*. Oleh karena itu, perancangan *asset* 3D perlu dilakukan bersama perancangan skema *database*, khususnya melalui atribut `unity_object_name` sebagai penghubung antara baris data dan *GameObject* di *Unity*.

Pengelolaan data proyek juga membutuhkan pembatasan akses pada tingkat *database*. *Row Level Security* (RLS) adalah mekanisme yang membatasi baris data yang boleh dibaca atau diubah berdasarkan peran pengguna. Pada tingkat rancangan, penulis menetapkan kebutuhan kebijakan RLS untuk membedakan akses baca publik dan perubahan terautentikasi. *Audit log* adalah catatan berurutan mengenai tindakan perubahan data agar pelaku, jenis perubahan, dan waktu kejadian dapat ditelusuri (Putra et al. 2026). Penulis merancang struktur tabel `audit_logs`, sedangkan pencatatan melalui layanan Dashboard diimplementasikan Iman. Definisi trigger audit database tidak diklaim karena bukti SQL atau eksekusinya tidak tersedia. Laporan ini berfokus pada pembuatan dan penataan seluruh *asset* 3D gedung dan fasilitas yang memiliki *GameObject* pada *scene* *Unity*, penyusunan *prefab* serta *child* `Pointer`, perancangan skema melalui *Entity Relationship Diagram* (ERD), yaitu diagram yang menggambarkan entitas dan hubungannya, pengelolaan data gedung atau fasilitas, serta penjagaan konsistensi `unity_object_name` pada *asset* dan data.

## 1.2 Identifikasi Masalah

Berdasarkan latar belakang dan kebutuhan proyek, masalah yang menjadi fokus laporan ini diidentifikasi sebagai berikut:

1. Belum tersedia representasi asset 3D Kampus UPNVJ Pondok Labu yang ditata dengan hierarki dan konvensi penamaan seragam untuk mendukung denah virtual interaktif.
2. Data gedung, fasilitas, fakultas, dan program studi memerlukan skema relasional yang dapat menjaga integritas hubungan antardata.
3. Belum terdapat mekanisme identitas tunggal yang secara konsisten menghubungkan data gedung atau fasilitas pada database dengan GameObject yang sesuai pada *scene* Unity.
4. Record gedung dan fasilitas perlu dikelola secara konsisten agar nama, lokasi, foto, relasi, dan identifier integrasinya tetap sesuai dengan asset 3D.
5. Ketidaksesuaian `unity_object_name` antara *database* dan hierarki *Unity* perlu ditemukan serta diperbaiki sebelum digunakan pada *build*. Dalam laporan ini, *build* berarti paket aplikasi *WebGL* yang dihasilkan dari proyek *Unity* untuk dijalankan pada peramban.

## 1.3 Batasan Masalah

Ruang lingkup laporan ini dibatasi agar pembahasan tetap sesuai dengan kontribusi Desainer Asset 3D dan Desainer Skema Database, yaitu sebagai berikut:

1. Objek yang direpresentasikan dibatasi pada asset 3D gedung dan fasilitas yang benar-benar memiliki GameObject pada scene Unity dan dikerjakan dalam lingkup kontribusi penulis.
2. Pembuatan dan penataan asset dilakukan langsung di Unity Editor tanpa membahas pemodelan menggunakan Blender.
3. Pembahasan *asset* mencakup geometri, material, tekstur, *prefab*, hierarki, *child* `Pointer`, *GameObject* tujuan, dan konvensi penamaan. Material mengatur tampilan permukaan objek, sedangkan tekstur merupakan gambar atau pola yang diterapkan pada material. [BUTUH SITASI]
4. Pembahasan database mencakup perancangan tabel dan relasi melalui ERD serta pengelolaan record `gedung` dan `fasilitas` yang terhubung dengan asset.
5. Penulis merancang kebutuhan kebijakan RLS dan struktur tabel `audit_logs`. Supabase Auth serta layanan pencatatan audit pada Dashboard dibahas sebagai konteks implementasi Iman; SQL produksi RLS dan trigger audit database tidak diklaim tanpa bukti.
6. `unity_object_name` digunakan sebagai identifier integrasi yang ditetapkan dan diperbaiki penulis pada record database serta GameObject tujuan.
7. `DatabaseSyncChecker` adalah alat pada *Unity Editor* yang membandingkan nama tujuan pada *database* dengan nama *GameObject* pada *scene*. Penulis menggunakan alat tersebut untuk validasi, sedangkan kode alat merupakan kontribusi *3D Simulator* dan *Engine Developer*.
8. Logika *NavMesh*, navigasi, kontrol pemain, optimasi *engine*, *API* utama, *dashboard* *React*, autentikasi, komunikasi `SendMessage`, penerapan SQL produksi RLS, layanan audit Dashboard, dan trigger audit database berada di luar implementasi utama penulis. Perancangan kebutuhan kebijakan RLS dan struktur tabel `audit_logs` tetap termasuk kontribusi penulis. *API* pada batasan ini berarti antarmuka pertukaran data antarkomponen perangkat lunak.
9. *Asset* disusun berdasarkan observasi visual, yaitu pengamatan bentuk dan kondisi melalui lokasi serta foto tanpa pengukuran dimensi menggunakan alat ukur. Hasilnya merupakan representasi visual, bukan model *as-built* dengan ketelitian dimensi arsitektural.

Pembagian tanggung jawab tim dirangkum pada [TABREF:peran_tanggung_jawab].

[TABLE-ID:peran_tanggung_jawab]
[TABLECAPTION:Peran dan Tanggung Jawab]

[TABLE]
Peran | Tanggung Jawab Utama
Desainer *Asset* 3D dan Desainer Skema *Database* | Merancang *asset* visual 3D dan hierarki *prefab* beserta `Pointer`, merancang skema *database* *Supabase* *PostgreSQL* dan ERD, merancang kebutuhan kebijakan RLS serta struktur tabel `audit_logs`, mengelola data serta pemetaan *asset*, dan menjaga konsistensi `unity_object_name`.
*3D Simulator* dan *Engine Developer* | Mengembangkan *runtime* *Unity* *WebGL*, termasuk `BuildingDatabase`, `NavigationReceiver`, `DatabaseSyncChecker`, navigasi *NavMesh*, interaksi pengguna, optimasi performa, dan proses *build* *WebGL*.
*Full Stack Web Developer*, *System Integrator*, dan *DevOps Engineer* | Mengembangkan Dashboard Publik dan Panel Admin *React*, *REST API* pada *Vercel Serverless Functions*, integrasi *Supabase Auth* dan *CRUD*, *bridge* sisi *React*, pencatatan analitik aplikasi, pengujian *web*, serta *deployment* dan operasional layanan *web*; *Express* dan *Umami* dikelola sebagai jalur opsional.
[/TABLE]

## 1.4 Tujuan dan Manfaat

### 1.4.1 Tujuan

Tujuan penyusunan dan pelaksanaan proyek dalam lingkup laporan ini adalah sebagai berikut:

1. Membuat dan menata asset 3D gedung dan fasilitas Kampus UPNVJ Pondok Labu secara langsung di Unity Editor.
2. Menyusun hierarki prefab, child `Pointer`, dan GameObject tujuan dengan konvensi nama yang konsisten.
3. Merancang skema database relasional dan ERD untuk data gedung, fasilitas, fakultas, program studi, pengguna administrator, dan riwayat perubahan, termasuk kebutuhan kebijakan RLS serta struktur tabel `audit_logs`.
4. Mengelola record gedung serta fasilitas agar atribut dan relasinya sesuai dengan asset yang direpresentasikan.
5. Menetapkan dan memperbaiki `unity_object_name` pada database serta GameObject tujuan sebagai jembatan integrasi.
6. Menggunakan `DatabaseSyncChecker` yang dikembangkan anggota tim untuk memvalidasi konsistensi asset dan data.

### 1.4.2 Manfaat

Manfaat yang diharapkan dari kontribusi tersebut adalah sebagai berikut:

1. Bagi pengguna, asset 3D yang terstruktur dan data yang konsisten mendukung penyajian denah virtual serta informasi gedung dan fasilitas secara lebih mudah dipahami.
2. Bagi administrator, skema relasional dan record yang tertata memberikan dasar pengelolaan data gedung serta fasilitas secara terpusat.
3. Bagi tim pengembang, konvensi `unity_object_name` mengurangi ambiguitas ketika menghubungkan data pada dashboard, API, dan objek pada *scene* Unity.
4. Bagi institusi, rancangan tersebut dapat menjadi fondasi pengembangan layanan informasi spasial kampus yang lebih terpelihara dan berkelanjutan.

## 1.5 Jadwal Kegiatan

Kegiatan aktual penulis berlangsung selama enam bulan dan dirangkum pada [TABREF:jadwal_kegiatan]. Struktur tabel menggunakan periode enam bulan yang sama dengan jadwal proyek tim, sedangkan aktivitasnya dibatasi pada pekerjaan asset 3D, skema database, pengelolaan data, pemetaan identifier, validasi, dan dokumentasi Dwikhi.

[TABLE-ID:jadwal_kegiatan]
[TABLECAPTION:Jadwal Kegiatan Perancangan Asset 3D dan Database]

[TABLE gantt]
Aktivitas | Bulan 1 | Bulan 2 | Bulan 3 | Bulan 4 | Bulan 5 | Bulan 6
Observasi lapangan dan identifikasi kebutuhan asset serta data | X | | | | | |
Pengambilan foto dan inventarisasi gedung serta fasilitas | X | X | | | | |
Perancangan skema database dan ERD | X | X | | | | |
Penetapan konvensi nama asset dan `unity_object_name` | X | X | X | | | |
Pemodelan asset 3D gedung dan fasilitas | | X | X | X | | |
Penerapan material dan tekstur | | X | X | X | | |
Penyusunan prefab, hierarki, `Pointer`, dan GameObject tujuan | | | X | X | | |
Penyusunan data awal (*seed*) serta pengelolaan data gedung dan fasilitas | | | X | X | X | |
Pemetaan asset dengan `unity_object_name` | | | X | X | X | |
Pemeriksaan integritas database | | | | X | X | |
Validasi menggunakan `DatabaseSyncChecker` | | | | X | X | |
Pemeriksaan visual dan teknis asset | | | | X | X | X
Koreksi ketidaksesuaian asset dan data | | | | | X | X
Penyusunan dokumentasi dan laporan | X | X | X | X | X | X
Pengujian akhir dan finalisasi | | | | | X | X
[/TABLE]

## 1.6 Sistematika Penulisan

Laporan Tugas Akhir Proyek ini disusun dalam empat bab dengan sistematika sebagai berikut:

1. BAB I PENDAHULUAN menjelaskan latar belakang, identifikasi masalah, batasan masalah, tujuan dan manfaat, jadwal kegiatan, serta sistematika penulisan dengan penekanan pada asset 3D dan skema database.
2. BAB II RANCANGAN PROYEK menguraikan hasil observasi, kebutuhan sistem, rancangan asset dan konvensi *scene* Unity, rancangan database dan keamanan, pemetaan `unity_object_name`, serta rencana pengujian.
3. BAB III IMPLEMENTASI PROYEK menjelaskan profil mitra, metode implementasi asset 3D dan database, konfigurasi metadata, bukti implementasi, serta hasil pengujian yang relevan dengan kontribusi penulis.
4. BAB IV PENUTUP memuat kesimpulan berdasarkan hasil yang telah diverifikasi dan saran pengembangan lebih lanjut.

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

Solusi dalam lingkup penulis adalah rancangan asset 3D dan model data yang memiliki identifier bersama. Asset gedung dan fasilitas disusun pada Unity Editor, sedangkan informasi gedung, fasilitas, fakultas, dan program studi dimodelkan pada database PostgreSQL. Field `unity_object_name` menghubungkan record database dengan GameObject tujuan pada scene Unity. Hubungan komponen tersebut ditunjukkan pada [FIGREF:diagram_arsitektur].

[FIGURE:diagram_arsitektur]
[FIGCAPTION:Arsitektur Integrasi Asset 3D dan Data]

Arsitektur tersebut membedakan kontribusi setiap anggota. Pada arsitektur ini, *endpoint* adalah alamat khusus yang menyediakan fungsi atau data melalui *API* (Vercel 2026). *Structured Query Language* (SQL) adalah bahasa perintah untuk mendefinisikan dan mengelola data pada *database* (PostgreSQL Global Development Group 2026b). Dokumentasi resmi *Supabase* menjelaskan bahwa *Data REST API* dibentuk dari skema *database* dan menyediakan operasi *CRUD* melalui antarmuka *REST* (Supabase 2026). Dokumentasi *React* menjelaskan bahwa antarmuka dibangun dari komponen yang dapat digunakan kembali (React 2026), sedangkan *Vercel Functions* menyediakan eksekusi kode sisi server untuk menangani permintaan *API* (Vercel 2026). Dwikhi merancang model data inti, mengelola data gedung atau fasilitas, membuat *asset* 3D, dan menata *GameObject* tujuan. Iman mengintegrasikan rancangan *SQL* ke repositori *web* serta mengembangkan *React* dan *endpoint API*. Faiz mengembangkan *runtime Unity* dan `DatabaseSyncChecker`. *React* mengakses *Supabase* secara langsung untuk autentikasi dan operasi data. *Unity* mengambil data *runtime* melalui */api/unity/data*, sedangkan `DatabaseSyncChecker` mengambil daftar *identifier* melalui */api/unity/names*. Perintah navigasi dikirim *React* ke *Unity*, dan *Unity* mengirim *callback*, yaitu pemberitahuan balik bahwa proses telah selesai, kepada *React* setelah navigasi selesai secara normal.

### 2.2.1 Identifikasi Kebutuhan Fungsional

Kebutuhan fungsional dalam lingkup asset 3D dan database dirumuskan sebagai berikut:

1. Asset gedung dan fasilitas perlu merepresentasikan bentuk utama, pembagian lantai, bukaan, warna, dan elemen visual yang dapat dikenali dari observasi.
2. Asset perlu disusun sebagai prefab dengan pemisahan antara geometri visual dan GameObject tujuan navigasi.
3. Database perlu menyimpan data gedung, fasilitas, fakultas, dan program studi beserta hubungan antardata.
4. Data gedung dan fasilitas perlu dikelola melalui seed yang dapat diperiksa ulang secara struktural.
5. Setiap tujuan navigasi perlu menggunakan `unity_object_name` yang unik dan stabil pada database serta scene Unity.
6. Ketidaksesuaian antara identifier pada database dan nama GameObject perlu dapat ditemukan sebelum artefak Unity dibangun ulang.

### 2.2.2 Identifikasi Kebutuhan Teknis

Kebutuhan teknis yang mendukung lingkup laporan ini adalah sebagai berikut:

1. *Unity* 6 dan *Unity Editor* digunakan untuk membuat serta menata *asset*, *prefab*, material, tekstur, dan hierarki *scene* (Unity Technologies 2026a).
2. *ProBuilder* digunakan untuk membentuk dan menyunting geometri secara langsung pada *Unity Editor* (Unity Technologies 2026b).
3. *Supabase PostgreSQL* digunakan sebagai platform penyimpanan struktur dan data yang telah dirancang (Supabase 2026).
4. Berkas *SQL setup* dan *seed* digunakan sebagai sumber pemeriksaan struktur tabel, relasi, *constraint*, dan isi data (PostgreSQL Global Development Group 2026a; PostgreSQL Global Development Group 2026b).
5. Endpoint */api/unity/names* menyediakan daftar `unity_object_name` untuk kebutuhan pemeriksaan pada Unity Editor.
6. `DatabaseSyncChecker` yang dikembangkan Faiz digunakan Dwikhi untuk membandingkan identifier database dengan nama GameObject pada scene.
7. Autentikasi, penerapan SQL produksi RLS, API, pencatatan audit melalui layanan aplikasi, dan deployment merupakan komponen integrasi yang diimplementasikan di luar kontribusi penulis; kebutuhan kebijakan RLS tetap dirancang pada tingkat integrasi.

### 2.2.3 Identifikasi Kebutuhan Non-Fungsional

Kebutuhan nonfungsional ditetapkan sebagai berikut:

1. Integritas data dijaga melalui *primary key* sebagai identitas unik baris, *foreign key* sebagai penghubung antartabel, *unique constraint* sebagai pencegah nilai ganda, dan `NOT NULL` sebagai penanda kolom wajib (PostgreSQL Global Development Group 2026a).
2. Konsistensi integrasi dijaga melalui `unity_object_name` yang unik, stabil, dan sesuai dengan nama GameObject tujuan.
3. Keterpeliharaan didukung oleh pemisahan geometri visual, struktur prefab, titik tujuan, serta nama tampilan dan identifier internal.
4. Keterlacakan dijaga dengan menyimpan sumber rancangan, seed, inventaris asset, dan hasil pemeriksaan konsistensi.
5. Keterbacaan visual dijaga agar bentuk utama serta identitas gedung dapat dikenali sebagai representasi denah virtual tanpa mengklaim ketelitian dimensi arsitektural.

## 2.3 Rancangan Proyek

### 2.3.1 Alur Perancangan Asset dan Data

Pengembangan mengikuti metode *prototyping*, yaitu metode yang menghasilkan bentuk awal untuk ditinjau, diuji, dan diperbaiki secara bertahap ketika kebutuhan belum seluruhnya rinci (Pricillia et al. 2021). Dalam kontribusi Dwikhi, bentuk awal tersebut berupa model *asset*, hierarki *prefab*, rancangan skema, dan data awal yang disempurnakan berdasarkan hasil pemeriksaan. Alur kerja khusus penulis divisualisasikan pada [FIGREF:diagram_tahap_pengembangan].

[FIGURE:diagram_tahap_pengembangan]
[FIGCAPTION:Alur Perancangan Asset 3D dan Data]

Tahapan kerja dalam lingkup penulis terdiri atas:

1. Referensi *asset* diperoleh melalui observasi visual dan dokumentasi foto, sedangkan kebutuhan data diperoleh melalui inventarisasi informasi gedung dan fasilitas.
2. Pekerjaan asset dan data dilakukan secara paralel melalui pemodelan di Unity serta penyusunan entitas, atribut, dan relasi.
3. Prefab dan record data diberi identifier yang mengikuti konvensi `unity_object_name`.
4. Daftar identifier dibandingkan dengan seluruh nama GameObject pada scene menggunakan `DatabaseSyncChecker`.
5. Ketidaksesuaian diperbaiki pada data atau scene sesuai sumber masalah, kemudian hasilnya didokumentasikan.

### 2.3.2 Perancangan Asset 3D Gedung dan Fasilitas

Dalam pembahasan teknis *asset*, *mesh* adalah permukaan tiga dimensi yang tersusun dari titik-titik bernama *vertex* (Unity Technologies 2026b). *Shader* menentukan cara material ditampilkan oleh sistem, sedangkan *collider* merupakan batas tak terlihat yang dipakai untuk mendeteksi sentuhan atau benturan. [BUTUH SITASI] Istilah-istilah tersebut digunakan untuk menjelaskan struktur dan bukti *asset* yang dikerjakan Dwikhi, bukan untuk mengklaim optimasi *engine*.

Rancangan asset menggunakan hierarki yang memisahkan geometri bangunan, objek per lantai, dan titik tujuan navigasi. Setiap gedung ditempatkan dalam satu objek atau prefab induk. Di bawah prefab tersebut terdapat child `Pointer` yang menjadi induk bagi GameObject tujuan dengan nama sesuai `unity_object_name`. Struktur ini memungkinkan logika navigasi mencari Transform tujuan tanpa bergantung pada nama tampilan yang dapat berubah.

Perancangan bentuk asset mempertimbangkan keterbacaan representasi gedung, kesesuaian proporsi visual, konsistensi susunan lantai, serta pemakaian material dan tekstur. ProBuilder mendukung pembuatan, penyuntingan, dan pemberian tekstur geometri langsung di dalam Unity sehingga sesuai dengan metode pengerjaan asset yang digunakan (Unity Technologies 2026b). Rancangan asset dibandingkan dengan referensi visual serta bukti implementasi pada Subbab 3.2.1.

Lingkup asset mencakup asset 3D gedung dan fasilitas yang memiliki GameObject pada scene Unity dan dikerjakan penulis. Jumlah record pada database tidak otomatis sama dengan jumlah asset karena sebagian fasilitas direpresentasikan sebagai titik tujuan atau informasi, bukan model terpisah. Dokumentasi visual dan struktur prefab digunakan untuk menunjukkan keterlacakan asset yang tersedia.

### 2.3.3 Perancangan Hierarki Prefab dan Konvensi Penamaan

Hierarki prefab dirancang untuk memisahkan geometri visual dari objek yang digunakan sebagai titik tujuan navigasi. Prefab menyimpan susunan GameObject, komponen, dan child sebagai asset yang dapat digunakan kembali (Unity Technologies 2026a). Pemisahan tersebut menjaga agar perubahan bentuk, material, atau susunan mesh tidak langsung mengubah identifier yang menghubungkan asset dengan data.

Susunan konseptual prefab dan target navigasi ditunjukkan pada [FIGREF:diagram_hierarki_prefab].

[FIGURE:diagram_hierarki_prefab]
[FIGCAPTION:Rancangan Hierarki Prefab dan Target Navigasi]

Konvensi awal yang digunakan adalah sebagai berikut:

1. Nama `unity_object_name` menggunakan huruf kecil dan garis bawah, misalnya `gedung_rektorat` atau `mht_201`.
2. Nama harus unik pada database dan tidak digunakan oleh dua GameObject tujuan yang berbeda.
3. Titik tujuan ditempatkan pada posisi yang aman dan dapat dijangkau sistem navigasi, bukan di dalam geometri penghalang.
4. Geometri visual dipisahkan dari objek tujuan agar perubahan material atau bentuk tidak mengubah identitas integrasi.
5. Prefab gedung harus mempertahankan struktur child `Pointer` ketika digunakan kembali pada *scene*.

Prefab dan hierarki asset gedung serta fasilitas dalam scope penulis disusun dengan memisahkan geometri dari child `Pointer` dan GameObject tujuan. Rincian objek per lantai serta variasi struktur asset dijelaskan menggunakan tangkapan hierarki yang tersedia pada BAB III. Sebelas pasangan render dan hierarki yang tersedia digunakan sebagai bukti representatif, bukan sebagai batas jumlah asset.

### 2.3.4 Perancangan ERD dan Struktur Data Inti

*Entity Relationship Diagram* (ERD) merupakan diagram konseptual yang memperlihatkan entitas, atribut, dan hubungan sebagai dasar perancangan *database* (Afiifah et al. 2022). Dalam proyek ini, ERD membantu Dwikhi menentukan tabel, kolom, dan relasi sebelum data gedung serta fasilitas dikelola. Kontribusi rancangan inti Dwikhi mencakup `gedung`, `fasilitas`, `fakultas`, dan `program_studi` seperti ditunjukkan pada [FIGREF:diagram_erd].

[FIGURE:diagram_erd]
[FIGCAPTION:ERD Inti Data Gedung, Fasilitas, Fakultas, dan Program Studi]

Struktur empat entitas inti disajikan pada [TABREF:struktur_basis_data].

[TABLE-ID:struktur_basis_data]
[TABLECAPTION:Struktur Entitas Database]

[TABLE]
Tabel | Fungsi | Relasi atau Batasan Utama
`gedung` | Menyimpan identitas dan informasi fisik gedung | Primary key `id`; `nama_gedung` dan `unity_object_name` unik; menjadi induk `fasilitas`
`fasilitas` | Menyimpan ruangan atau fasilitas di dalam gedung | Foreign key `id_gedung` ke `gedung`; `unity_object_name` unik
`fakultas` | Menyimpan profil fakultas | Foreign key `id_gedung_utama` ke `gedung`
`program_studi` | Menyimpan program studi dan akreditasi | Foreign key `id_fakultas` ke `fakultas`; kombinasi nama, jenjang, dan fakultas unik
[/TABLE]

Penulis merancang entitas, atribut, relasi, serta batasan pada ERD inti dan struktur tabel `audit_logs`, serta menetapkan kebutuhan kebijakan RLS pada tingkat rancangan. Berkas SQL kemudian diintegrasikan ke repositori web oleh Iman. Skema sistem terkini juga memiliki empat tabel Denah 2D dan tiga tabel pendukung untuk profil administrator, audit, dan analitik. Tujuh tabel tersebut dijelaskan sebagai konteks sistem dan tidak diklaim sebagai rancangan inti penulis. Layanan pencatatan audit Dashboard diimplementasikan Iman; trigger audit database dan penerapan SQL produksi RLS tidak diklaim tanpa bukti.

### 2.3.5 Perancangan Pengelolaan Seed dan Kualitas Data

*Seed* adalah kumpulan perintah atau data awal yang dipakai untuk mengisi *database* secara terstruktur dan dapat diulang. Dalam proyek ini, *seed* menjadi sumber data gedung, fakultas, program studi, dan fasilitas yang dapat ditinjau ulang oleh Dwikhi. Pengelolaannya mencakup pemeriksaan urutan dependensi, kesesuaian *foreign key*, kelengkapan kolom, keunikan *identifier*, konsistensi penamaan, dan ketersediaan deskripsi. Perubahan *seed* tidak dianggap telah diterapkan pada *Supabase* aktif sebelum tersedia bukti eksekusi dan pemeriksaan ulang data *live*.

Kualitas data dijaga dengan memisahkan nama tampilan dari identifier internal. Nama tampilan dapat diperbaiki agar mudah dicari tanpa mengubah `unity_object_name` yang telah dipakai scene. Record yang tidak memiliki pemetaan valid perlu ditinjau dan tidak boleh otomatis dianggap sebagai asset Unity yang tersedia.

### 2.3.6 Perancangan Pemetaan dan Validasi unity_object_name

Alur validasi identifier ditunjukkan pada [FIGREF:diagram_sequence_validasi]. Diagram tersebut memperlihatkan penggunaan `DatabaseSyncChecker` sebagai alat bantu pemeriksaan, bukan sebagai implementasi milik penulis.

[FIGURE:diagram_sequence_validasi]
[FIGCAPTION:Sequence Diagram Validasi Identifier Asset dan Data]

Kontrak pemetaan dirancang sebagai berikut:

1. Tabel `gedung` dan `fasilitas` menyimpan `unity_object_name` sebagai nilai unik.
2. Nilai tersebut digunakan oleh endpoint */api/unity/data* dan */api/unity/names*.
3. GameObject tujuan ditempatkan sebagai turunan `Pointer` dan menggunakan nama yang sama.
4. Pencocokan runtime dilakukan tanpa membedakan kapitalisasi, tetapi konvensi penulisan tetap menggunakan huruf kecil dan garis bawah.
5. Nama tampilan seperti `nama_gedung` dan `nama_fasilitas` tetap dipisahkan dari identifier internal sehingga perubahan redaksi tidak merusak pemetaan.
6. Ketidaksesuaian perlu ditemukan sebelum build melalui pemeriksaan otomatis dan ditindaklanjuti pada database atau *scene* sesuai sumber kesalahan.

## 2.4 Rencana Pengujian Proyek

Rencana pengujian disusun agar setiap bagian rancangan memiliki hasil pengujian yang dapat ditelusuri pada Subbab 3.5. Setiap skenario perlu mencantumkan input, prasyarat, hasil yang diharapkan, hasil aktual, status, dan lokasi bukti.

### 2.4.1 Pemeriksaan Visual dan Struktur Asset

Pemeriksaan asset dilakukan terhadap bukti representatif dengan membandingkan bentuk utama, jumlah lantai yang terlihat, susunan objek, material atau tekstur, struktur prefab, child `Pointer`, dan GameObject tujuan. Pemeriksaan ini mendokumentasikan kesesuaian struktur dan keterbacaan visual, bukan mengukur performa, frame rate, atau dampak asset terhadap ukuran build.

### 2.4.2 Verifikasi Struktural Skema dan Seed

*Constraint* adalah aturan pada *database* yang mencegah data disimpan dalam bentuk yang tidak sesuai. Aturan ini diterapkan melalui `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, dan `NOT NULL` yang telah dijelaskan pada kebutuhan nonfungsional (PostgreSQL Global Development Group 2026a). Dwikhi memverifikasi aturan tersebut dengan membaca definisi *SQL* dan memeriksa struktur *seed*, meliputi jumlah kolom *tuple*, keseimbangan tanda kutip, relasi ID, nilai wajib, dan keunikan `unity_object_name`. Verifikasi tersebut tidak disebut sebagai eksekusi *PostgreSQL* *live* karena *SQL setup* bersifat destruktif dan tidak dijalankan dalam penyusunan laporan.

### 2.4.3 Pemeriksaan Konsistensi Asset dan Data

Validasi konsistensi adalah pemeriksaan untuk memastikan satu nama integrasi mempunyai padanan yang semestinya pada data dan objek. Pemeriksaan ini membandingkan `unity_object_name` yang tersedia melalui */api/unity/names* dengan nama *GameObject* pada *scene* *Unity*. Hasilnya dikelompokkan menjadi *identifier* yang cocok, hanya tersedia pada *database*, atau hanya tersedia pada *scene*. Perbedaan tersebut disebut *mismatch* atau ketidaksesuaian. Dwikhi menggunakan `DatabaseSyncChecker` yang dikembangkan Faiz dan memperbaiki data atau penamaan *asset* sesuai sumber ketidaksesuaian. Setiap hasil pemeriksaan diperlakukan sebagai *snapshot*, yaitu rekaman kondisi pada satu waktu, sehingga *snapshot* lama dibedakan secara eksplisit dari kondisi *seed* final yang belum diterapkan pada *database live*.

### 2.4.4 Black Box dan UAT Produk Bersama

*Black Box Testing* adalah metode yang memeriksa fungsi sistem melalui masukan dan keluaran tanpa meninjau rincian kode internal (Maulida et al. 2025). Skenario bersama digunakan sebagai pengujian regresi untuk memastikan perubahan skema atau *asset* tidak merusak fungsi *dashboard*, *API*, dan navigasi. *User Acceptance Testing* (UAT) adalah pengujian oleh pihak yang berkepentingan untuk menilai kesesuaian sistem dengan kebutuhan penggunaan yang telah ditentukan (Aliyah et al. 2025). Dalam laporan Dwikhi, kedua hasil pengujian tersebut dipakai sebagai konteks pengaruh *asset* dan data terhadap produk bersama, bukan sebagai klaim kepemilikan seluruh implementasi sistem.

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

| Pemangku Kepentingan | Hubungan dengan Proyek | Batas Interpretasi |
| :---: | --- | --- |
| Humas UPNVJ | Menjadi mitra pengguna; satu perwakilan mengikuti UAT dan memberikan perspektif evaluasi informasi serta navigasi | Masukan dibatasi pada peserta UAT dan tidak dianggap sebagai persetujuan institusional |
| Pengguna layanan | Mahasiswa baru, orang tua atau wali, sivitas akademika, dan pengunjung eksternal menjadi kelompok penerima manfaat navigasi | Tidak seluruh kelompok tersebut menjadi peserta UAT |
| UPA TIK UPNVJ | Memberikan konteks koordinasi teknis, kebijakan data, kemungkinan integrasi, wawancara, dan penyerahan pakta integritas | Bukan mitra pengguna dan tidak dinyatakan telah menerima implementasi sistem |
| Tim pengembang | Mengembangkan komponen sesuai pembagian peran asset/data, *runtime* Unity, dan aplikasi web | Setiap laporan hanya mengklaim implementasi yang berada dalam ownership penulisnya |
## 3.2 Metode Implementasi

Implementasi menggunakan pendekatan iteratif sesuai rancangan *prototyping*. Lingkup penulis mencakup pembuatan dan penataan seluruh asset 3D gedung dan fasilitas yang memiliki GameObject pada scene Unity, hierarki prefab dan child `Pointer`, perancangan skema serta ERD, pengelolaan record gedung atau fasilitas, dan pemetaan `unity_object_name`. Uraian berikut membedakan kontribusi tersebut dari komponen integrasi milik anggota lain.

### 3.2.1 Implementasi Pembuatan dan Penataan Asset 3D Gedung dan Fasilitas di Unity Editor

Penulis membuat dan menata asset 3D gedung dan fasilitas secara langsung pada Unity Editor tanpa Blender. Bukti yang diserahkan mencakup referensi visual kondisi aktual, tangkapan proses pengerjaan pada Unity Editor, render, tangkapan hierarki, serta inventaris material dan tekstur. Sebelas pasangan render dan hierarki digunakan sebagai sampel bukti representatif, bukan sebagai batas jumlah asset. Dimensi presisi tidak dinyatakan karena observasi tidak menggunakan alat ukur. Pemeriksaan asset difokuskan pada keterbacaan bentuk, struktur hierarki, material atau tekstur yang tampak, serta kesesuaian nama objek tujuan.

Arsip bukti memuat 22 berkas referensi visual. Berkas tersebut merupakan dokumentasi lapangan, sudut tambahan, atau sumber visual untuk sebagian asset dan entitas database yang terkait. Cakupan foto tidak digunakan untuk menyimpulkan jumlah seluruh GameObject yang dikerjakan. Sumber, tanggal, lokasi, dan identitas pengambil gambar belum seluruhnya tersedia. Inventarisnya dirangkum pada [TABREF:inventaris_foto_referensi].

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
22 | Gedung Jenderal Soedirman | `refrensi_Gedung_jenderal_soedirman.png` | Sumber dan tanggal belum dicatat; digunakan sebagai referensi visual, bukan bukti pengukuran dimensi
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

Tampilan massa bangunan dan pola fasad Gedung Jenderal Soedirman dapat dibandingkan dengan asset yang dibuat melalui referensi visual pada [FIGREF:evidence_photo_jenderal_soedirman]. Asal sumber dan tanggal gambar belum tercatat sehingga gambar ini tidak digunakan untuk mengklaim dokumentasi lapangan pribadi atau ketelitian ukuran.

[FIGURE:evidence_photo_jenderal_soedirman]
[FIGCAPTION:Referensi Visual Gedung Jenderal Soedirman]

Tangkapan proses pada [FIGREF:evidence_process_asset] memperlihatkan Unity Editor dengan objek gedung yang sedang disunting, panel *Hierarchy*, panel *Project*, dan komponen ProBuilder pada *Inspector*. Bukti ini mendokumentasikan metode pembuatan dan penyesuaian geometri langsung di lingkungan Unity yang digunakan penulis pada asset gedung.

[FIGURE:evidence_process_asset]
[FIGCAPTION:Proses Pengerjaan Asset Gedung di Unity Editor]

Metode implementasi asset menggunakan pendekatan pemodelan berbasis referensi visual. Foto dan pengamatan langsung digunakan untuk mengenali massa bangunan, jumlah lantai, pola fasad, bukaan, warna, material, dan hubungan proporsional antarelemen. Geometri kemudian dibentuk dan disesuaikan secara visual di Unity Editor, dilanjutkan dengan penerapan material atau tekstur, pengelompokan objek, serta penyusunan asset pada hierarki. Pendekatan ini sesuai untuk kebutuhan representasi denah virtual, tetapi tidak digunakan untuk menyatakan ketelitian dimensi arsitektural.

Versi editor dan inventaris asset dicatat pada Subbab 3.3.3. Riwayat perubahan yang tersedia menunjukkan proses pengerjaan berlangsung bertahap, tetapi tanggal pembuatan setiap asset dan alasan rinci setiap perubahan tidak terdokumentasi secara lengkap. Keterbatasan tersebut dinyatakan sebagai batas keterlacakan proses dan tidak diubah menjadi klaim optimasi atau pengukuran performa.

### 3.2.2 Implementasi Hierarki Prefab dan Penamaan unity_object_name

Folder bukti memuat pasangan render dan tangkapan hierarki untuk sebagian asset gedung. Pada setiap prefab atau struktur objek yang dikerjakan, penulis mengelompokkan geometri dan objek per lantai, menyusun child `Pointer`, membuat GameObject tujuan, serta menetapkan nama yang sesuai dengan `unity_object_name`. Mekanisme penggunaan titik tujuan oleh API atau logika navigasi tetap menjadi kontribusi anggota integrator dan pengembang *engine*.

Secara teknis, implementasi mengikuti aturan berikut:

1. Setiap prefab gedung mempunyai child `Pointer`.
2. Di bawah `Pointer` terdapat GameObject kosong untuk titik tujuan gedung atau fasilitas.
3. Nama GameObject disamakan dengan nilai `unity_object_name` pada database.
4. Titik tujuan diletakkan pada posisi yang dapat dicapai oleh sistem navigasi.
5. Perubahan nama harus diselaraskan pada database dan *scene* sebelum build.

### 3.2.3 Implementasi Rancangan Skema dan Pengelolaan Data di Supabase

Rancangan data inti penulis mencakup tabel `gedung`, `fasilitas`, `fakultas`, dan `program_studi`. Keempat tabel tersebut membentuk hubungan data lokasi kampus yang digunakan sebagai dasar pengelolaan gedung, fasilitas, dan program studi. Penulis juga merancang struktur tabel `audit_logs` dan kebutuhan kebijakan RLS sebagai bagian dari rancangan integrasi. *Data Definition Language* (DDL) merupakan bagian *SQL* yang secara khusus mendefinisikan struktur seperti tabel, kolom, dan batasannya. [BUTUH SITASI] Berkas *setup* sistem yang kemudian diintegrasikan Iman ke repositori *web* memuat tujuh tabel tambahan untuk autentikasi, audit aplikasi, analitik lama, dan Denah 2D. Tabel tambahan tersebut merupakan konteks sistem dan tidak diklaim sebagai rancangan inti penulis. Potongan DDL berikut hanya menampilkan empat tabel inti yang dirancang Dwikhi. Berkas *setup* digunakan sebagai sumber dokumentasi struktural dan tidak dijalankan saat penyusunan laporan karena memuat operasi penghapusan tabel.

Pada pemetaan asset, Masjid memiliki representasi visual atau GameObject tersendiri, tetapi record datanya berada pada tabel `fasilitas` dengan `id_gedung = 6`, yaitu Gedung Ki Hadjar Dewantara. Record Gedung Soepomo, Gedung Soetomo, Yos Sudarso, RA Kartini, Lapangan Basket, dan entitas gedung lainnya tetap diperlakukan sebagai entitas database yang berbeda.

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

```

ERD empat tabel inti, DDL dokumentasi, dan seed menjadi bukti perancangan data oleh penulis. Penulis juga mengelola record `gedung` dan `fasilitas`, termasuk atribut serta `unity_object_name` yang digunakan oleh asset. Iman menangani integrasi SQL ke repositori web dan penggunaan struktur tersebut oleh aplikasi. Bukti penerapan pada Supabase aktif dibedakan dari kondisi seed agar laporan tidak menyamakan rancangan lokal dengan data produksi.

### 3.2.4 Batas Integrasi Akses Data dan Pencatatan Audit

RLS dan Supabase Auth membatasi akses data pada sistem. Dalam lingkup Dwikhi, kebijakan RLS dirancang sebagai kebutuhan akses baca publik dan perubahan terautentikasi, bukan diklaim sebagai penerapan SQL produksi. Penulis juga merancang skema tabel `audit_logs`, sedangkan pencatatan audit dilakukan oleh layanan Dashboard yang diimplementasikan Iman. Berkas *setup* yang diperiksa tidak memuat definisi trigger audit database. Tangkapan Dashboard audit hanya digunakan sebagai konteks bahwa perubahan record dapat ditelusuri melalui sistem.

### 3.2.5 Implementasi Pemetaan unity_object_name pada Asset dan Database

Implementasi pemetaan dilakukan penulis dengan menerapkan identifier yang sama pada kolom `unity_object_name` di tabel `gedung` atau `fasilitas` dan pada GameObject tujuan di bawah child `Pointer`. Penulis menyiapkan serta memperbaiki nama pada asset dan data, kemudian menggunakan `DatabaseSyncChecker` buatan Faiz untuk menemukan ketidaksesuaian. Implementasi endpoint API oleh Iman dan kode alat pemeriksa oleh Faiz tidak dinyatakan sebagai kontribusi penulis.

Tahap implementasi pemetaan perlu didokumentasikan sebagai berikut:

1. Menginventarisasi asset gedung dan fasilitas yang memerlukan titik tujuan.
2. Menetapkan identifier berformat huruf kecil dan garis bawah serta memastikan nilainya unik.
3. Mengisikan identifier pada record database yang sesuai.
4. Membuat atau memperbarui GameObject tujuan di bawah child `Pointer` dengan nama yang sama.
5. Menjalankan pemeriksaan konsistensi melalui alat bantu tim.
6. Memperbaiki ketidaksesuaian pada asset atau data sesuai sumber kesalahan, kemudian melakukan pengujian ulang.

Kolom dan contoh nilai identifier pada tabel `gedung` dapat dilihat pada [FIGREF:evidence_unity_names_gedung]. Tangkapan tersebut memperlihatkan antara lain nilai `cipto_mangunkusumo`, `abdul_rahman_saleh`, `ki_hadjar_dewantara`, `thamrin`, `yamin`, `yos_sudarso`, `kartini`, `parkir_depan`, `parkir_belakang`, `dewi_sartika`, `lapangan_upacara`, `ukm`, dan `soetomo`. Karena nama tampilan gedung terpotong pada tangkapan, bukti ini digunakan untuk mengonfirmasi keberadaan kolom serta contoh nilai, bukan sebagai daftar pemetaan final.

[FIGURE:evidence_unity_names_gedung]
[FIGCAPTION:Contoh Nilai unity_object_name pada Tabel Gedung]

Penerapan identifier pada record fasilitas terlihat pada [FIGREF:evidence_unity_names_fasilitas]. Tangkapan tersebut juga menampilkan `id_gedung`, `lantai`, `foto_url`, dan beberapa nilai `unity_object_name` berawalan `wsh_`, tetapi nama fasilitas tidak terlihat lengkap sehingga pasangan record dan GameObject masih perlu dicatat dalam matriks pemetaan.

[FIGURE:evidence_unity_names_fasilitas]
[FIGCAPTION:Contoh Nilai unity_object_name pada Tabel Fasilitas]

Pemetaan pada prefab dan GameObject asset dalam scope penulis merupakan bagian dari pekerjaan penulis. Bukti hierarki Dewi Sartika memperlihatkan contoh objek tujuan `dewi_sartika`, sedangkan hasil pemeriksaan pada Subbab 3.5.5 menunjukkan bahwa keseluruhan data dan *scene* belum sepenuhnya konsisten. Daftar pemetaan lengkap per record, perubahan yang dilakukan, serta metadata pengujian ulang masih diperlukan untuk menunjukkan penyelesaian koreksi secara terukur.

## 3.3 Konfigurasi dan Metadata

### 3.3.1 Struktur Database dan Relasi

Konfigurasi database menggunakan foreign key untuk menjaga hubungan entitas dan batasan unik untuk menjaga identitas. Tabel `gedung` menjadi induk bagi `fasilitas`, tabel `fakultas` dapat merujuk gedung utama, dan tabel `program_studi` merujuk fakultas. Field `unity_object_name` pada `gedung` serta `fasilitas` menjadi metadata integrasi ke Unity.

Struktur constraint produksi yang tertangkap pada [FIGREF:evidence_constraint_inventory] menampilkan 12 baris hasil kueri katalog PostgreSQL. Bagian yang terbaca mengonfirmasi primary key pada `gedung`, `fakultas`, dan `fasilitas`; batasan unik `nama_gedung`, `nama_fakultas`, serta `unity_object_name` pada `gedung` dan `fasilitas`; foreign key `fakultas.id_gedung_utama` serta `fasilitas.id_gedung` ke `gedung.id`; dan aturan `ON DELETE SET NULL` pada dua relasi yang terlihat. Tangkapan ini membuktikan definisi constraint, bukan hasil percobaan memasukkan atau menghapus data yang melanggar aturan.

[FIGURE:evidence_constraint_inventory]
[FIGCAPTION:Inventaris Constraint Tabel Utama pada Supabase]

Nilai produksi setiap tipe fasilitas, aturan nilai `lantai`, format `foto_url`, kebijakan data kosong, dan riwayat perubahan skema belum seluruhnya tercatat dalam bukti yang tersedia. Karena berkas setup tidak dieksekusi ulang saat penyusunan laporan, status penerapan setiap perubahan pada Supabase aktif tidak disimpulkan dari DDL. Batas ini tidak mengurangi fungsi DDL sebagai bukti rancangan struktural, tetapi membatasi klaim mengenai kondisi produksi.

### 3.3.2 Konvensi Struktur Prefab dan Penamaan

Contoh struktur prefab dengan child `Pointer` dapat dilihat pada [FIGREF:impl_pointer_hierarchy].

[FIGURE:impl_pointer_hierarchy]
[FIGCAPTION:Hierarki Prefab Gedung dengan Child Pointer di Unity]

Validasi kecocokan nama dibantu oleh `DatabaseSyncChecker`, dengan antarmuka yang ditunjukkan pada [FIGREF:impl_sync_db_checker]. Alat ini mengambil daftar nama dari */api/unity/names*, menelusuri hierarki *scene*, dan mengelompokkan hasil yang cocok atau tidak cocok.

[FIGURE:impl_sync_db_checker]
[FIGCAPTION:Tampilan UI Database Sync Checker di Unity Editor]

Pada bukti [FIGREF:impl_sync_db_checker], pemeriksaan awal menampilkan 97 nama dari database, 57 nama ditemukan pada *scene*, 40 nama hanya terdapat pada database, dan 18 nama hanya terdapat pada *scene*. Angka tersebut menunjukkan kondisi awal yang belum konsisten, bukan hasil akhir implementasi. Versi *scene*, endpoint, database, daftar koreksi, dan hasil pengujian ulang belum tercatat pada bukti yang tersedia.

### 3.3.3 Inventaris dan Metadata Asset 3D

Inventaris asset digunakan untuk menelusuri nama prefab, struktur objek, material atau tekstur, serta keterkaitannya dengan target navigasi. Pencatatan ini berfungsi sebagai dokumentasi keadaan asset dan tidak digunakan untuk menyatakan optimasi performa. Evaluasi performa runtime, occlusion culling, dan build WebGL menjadi bagian pekerjaan pengembang engine.

Versi editor yang terlihat pada [FIGREF:evidence_unity_version] adalah Unity 6.4 dengan identifier `6000.4.1f1_8535861f39e1`. Bukti ini menetapkan lingkungan yang terlihat ketika data dikumpulkan dan digunakan sebagai konteks untuk membaca metrik asset.

[FIGURE:evidence_unity_version]
[FIGCAPTION:Versi Unity yang Digunakan pada Pengukuran Asset]

Perangkat yang digunakan saat inventarisasi ditunjukkan pada [FIGREF:evidence_test_device]. Tangkapan tersebut memperlihatkan prosesor 13th Gen Intel(R) Core(TM) i7-13620H, RAM terpasang 32 GB, GPU NVIDIA GeForce RTX 4060 Laptop GPU 8 GB, dan sistem operasi 64-bit. Informasi ini hanya mencatat lingkungan pengambilan bukti dan bukan hasil pengujian performa asset.

[FIGURE:evidence_test_device]
[FIGCAPTION:Spesifikasi Perangkat Pengujian Asset]

Inventaris pada [FIGREF:evidence_prefab_sizes] menampilkan ukuran berkas prefab gedung beserta berkas `.meta` yang berukuran jauh lebih kecil. Nilai yang terbaca untuk tiga asset terukur adalah 24,3 MB pada Ki Hajar Dewantara, 11,2 MB pada Dewi Sartika, dan 11,2 MB pada Jenderal Soedirman. Beberapa nama memiliki lebih dari satu versi berkas, sehingga ukuran tersebut digunakan sebagai nilai yang terlihat pada inventaris, bukan sebagai klaim bahwa seluruh prefab telah memiliki versi final yang sama.

[FIGURE:evidence_prefab_sizes]
[FIGCAPTION:Ukuran Berkas Prefab Gedung pada Inventaris Asset]

Data inventaris yang terbaca dari tiga tangkapan Unity dirangkum pada [TABREF:metrik_tiga_aset]. Angka hanya menggambarkan objek yang dipilih ketika tangkapan dibuat dan tidak digunakan sebagai kriteria kelulusan atau perbandingan performa.

[TABLE-ID:metrik_tiga_aset]
[TABLECAPTION:Inventaris Teknis Tiga Asset Representatif]

[TABLE]
Asset | GameObject | Mesh Instance | Unique Mesh | Vertex | Ukuran Prefab yang Terlihat
Ki Hajar Dewantara | 860 | 583 | 318 | 703.694 | 24,3 MB
Dewi Sartika | 477 | 371 | 279 | 124.973 | 11,2 MB
Jenderal Soedirman | 2.809 | 2.108 | 885 | 1.308.941 | 11,2 MB
[/TABLE]

Rincian GameObject, mesh instance, unique mesh, dan vertex Ki Hajar Dewantara terlihat pada [FIGREF:evidence_metrics_ki_hadjar]. Nilai tersebut mendokumentasikan kondisi objek yang dipilih saat tangkapan dibuat.

[FIGURE:evidence_metrics_ki_hadjar]
[FIGCAPTION:Hasil Pengukuran GameObject, Mesh, dan Vertex Ki Hajar Dewantara]

Hasil pengukuran Dewi Sartika direkam pada [FIGREF:evidence_metrics_dewi] dengan 477 GameObject dan 124.973 vertex. Data ini menjadi baseline teknis untuk perbandingan dengan pemeriksaan asset berikutnya apabila tersedia.

[FIGURE:evidence_metrics_dewi]
[FIGCAPTION:Hasil Pengukuran GameObject, Mesh, dan Vertex Dewi Sartika]

Jumlah objek terbanyak di antara tiga tangkapan terlihat pada [FIGREF:evidence_metrics_jenderal], yaitu Jenderal Soedirman dengan 2.809 GameObject dan 1.308.941 vertex. Perbedaan angka diperlakukan sebagai deskripsi inventaris, bukan sebagai kesimpulan performa.

[FIGURE:evidence_metrics_jenderal]
[FIGCAPTION:Hasil Pengukuran GameObject, Mesh, dan Vertex Jenderal Soedirman]

Inventaris awal memuat 37 berkas gambar material dan tekstur. Pemeriksaan otomatis menunjukkan seluruh 37 berkas tersebut memiliki byte yang sama dengan berkas bernama sama pada proyek Unity sumber. Folder bukti kemudian memperoleh 30 berkas tambahan yang terdiri atas dua referensi tekstur permukaan, 21 referensi warna polos, satu berkas logo Mandiri, lima berkas model atau tekstur alat olahraga, dan satu berkas warna patung. Berdasarkan konfirmasi penulis, ke-21 referensi warna digunakan pada material Unity dan dua referensi tekstur permukaan diterapkan pada Gedung Utama/Jenderal Soedirman. Logo Mandiri digunakan pada asset gedung bank yang ditempatkan sebagai pelengkap visual lingkungan aktual dan tidak memiliki record pada database. Lima berkas `model1_alat_olahraga.png` sampai `model5_alat_olahraga.png` digunakan pada objek alat olahraga di depan Gedung Dewi Sartika, sedangkan `warna_patung.png` digunakan pada asset patung. Kecocokan byte berkas tambahan dengan proyek Unity sumber belum diverifikasi. Dengan demikian, jumlah seluruh berkas pada folder menjadi 67, sedangkan klaim kecocokan dengan proyek sumber tetap dibatasi pada 37 berkas awal. Pengelompokan bukti dirangkum pada [TABREF:inventaris_material_tekstur].

[TABLE-ID:inventaris_material_tekstur]
[TABLECAPTION:Inventaris Berkas Material, Tekstur, dan Referensi Warna]

[TABLE]
Kelompok | Jumlah | Berkas
Permukaan luar dan lingkungan | 8 | `aspal.png`, `atap.jpeg`, `batu_bata.png`, `Rumput.jpeg`, `rumput.png`, `semen.jpeg`, `tanah.jpeg`, `water.jpg`
Dinding dan kayu | 7 | `diding_tu_fik.png`, `dinding_kayu.jpg`, `dinding_rektorat.jpg`, `dinding_rektotat_2.jpg`, `kayu.jpeg`, `kayu_coklat_tua.jpg`, `tembok_tamrin.jpg`
Bukaan, pagar, dan ubin | 9 | `itemputih.png`, `jaring_besi.png`, `jendela.png`, `pintu_putih.jpg`, `ubin.png`, `ubin2.jpeg`, `ubin3.jpeg`, `ubin4.jpeg`, `ubin5.jpeg`
Fasilitas dan elemen interior | 8 | `generator.png`, `lapangan_basket.png`, `layar_videoron.jpg`, `loker.png`, `mushola_gedung_utama.jpg`, `papan_basket.png`, `perpus.png`, `perpus2.png`
Identitas dan logo | 6 | `logo_bni.png`, `Logo_Indomaret.png`, `LOGO_PKBN.jpg`, `logo_sekolah.png`, `Logo_upn.png`, `logo_mandiri.jpg`; logo Mandiri digunakan pada asset gedung bank sebagai pelengkap visual lingkungan aktual tanpa record database
Referensi tekstur permukaan tambahan | 2 | `lobby_utama_gedung_rektorat_upnvj.jpg`, `tembok_nama_lobby_gedung_utama.jpg`; diterapkan pada Gedung Utama/Jenderal Soedirman
Referensi warna polos tambahan | 21 | `material_warna_refrensi_1.png` sampai `material_warna_refrensi_21.png`; digunakan pada material Unity, tetapi pemetaan setiap berkas ke asset belum dirinci
Model atau tekstur alat olahraga | 5 | `model1_alat_olahraga.png` sampai `model5_alat_olahraga.png`; digunakan pada objek alat olahraga di depan Gedung Dewi Sartika
Warna patung | 1 | `warna_patung.png`; digunakan pada asset patung
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

Dua berkas tambahan yang memperlihatkan pola permukaan untuk konteks lobi dan gedung rektorat disajikan pada [FIGREF:evidence_material_lobby_rektorat] dan [FIGREF:evidence_material_tembok_lobby]. Berdasarkan konfirmasi penulis, kedua tekstur tersebut diterapkan pada Gedung Utama/Jenderal Soedirman. Bukti yang tersedia belum merinci pembagian penggunaan masing-masing tekstur pada setiap objek di gedung tersebut.

[FIGURE:evidence_material_lobby_rektorat]
[FIGCAPTION:Berkas Referensi Tekstur Lobi Utama Gedung Rektorat]

[FIGURE:evidence_material_tembok_lobby]
[FIGCAPTION:Berkas Referensi Tekstur Tembok Lobi Gedung Utama]

Metadata yang dapat diverifikasi langsung dari berkas bukti untuk tiga asset representatif dirangkum pada [TABREF:metadata_bukti_aset_representatif]. Resolusi dalam tabel adalah resolusi tangkapan bukti, bukan ukuran atau tingkat detail model.

[TABLE-ID:metadata_bukti_aset_representatif]
[TABLECAPTION:Metadata Bukti Tiga Asset Representatif]

[TABLE]
Asset | Foto Aktual | Render Asset | Hierarki | Status Bukti
Cipto Mangunkusumo | 5280 × 3016 piksel | 742 × 352 piksel | 693 × 840 piksel | Foto, render, dan hierarki tersedia
M. Yamin | 5296 × 3504 piksel | 472 × 482 piksel | 522 × 627 piksel | Foto, render, dan hierarki tersedia
Wahidin Sudiro Husodo | 3072 × 4096 piksel | 726 × 557 piksel | 645 × 831 piksel | Foto, render, dan hierarki tersedia
[/TABLE]

Enam contoh tekstur yang telah dimasukkan ke draft memiliki metadata berkas sebagaimana dirangkum pada [TABREF:metadata_tekstur_representatif].

[TABLE-ID:metadata_tekstur_representatif]
[TABLECAPTION:Metadata Berkas Tekstur Representatif]

[TABLE]
Berkas | Resolusi Bukti | Keterangan Terverifikasi
`diding_tu_fik.png` | 2048 × 1725 piksel | Berkas gambar tersedia pada inventaris
`atap.jpeg` | 198 × 225 piksel | Berkas gambar tersedia pada inventaris
`rumput.png` | 667 × 664 piksel | Berkas gambar tersedia pada inventaris
`jendela.png` | 1507 × 1003 piksel | Berkas gambar tersedia pada inventaris
`lobby_utama_gedung_rektorat_upnvj.jpg` | 1024 × 1024 piksel | Diterapkan pada Gedung Utama/Jenderal Soedirman
`tembok_nama_lobby_gedung_utama.jpg` | 1024 × 1024 piksel | Diterapkan pada Gedung Utama/Jenderal Soedirman
[/TABLE]

Keberadaan berkas gambar belum memberikan informasi lengkap mengenai sumber atau lisensi, konfigurasi Unity Material, shader, nilai tiling, resolusi impor, dan pemetaan material terhadap setiap asset. Laporan mencatat bahwa 21 referensi warna digunakan pada material Unity dan dua referensi tekstur diterapkan pada Gedung Utama/Jenderal Soedirman, tetapi belum merinci pemetaan setiap berkas warna ke objek tertentu. Pemetaan tujuh berkas tambahan telah dikonfirmasi pada tingkat objek atau lokasi, yaitu logo Mandiri pada asset gedung bank pelengkap lingkungan, lima berkas alat olahraga pada objek di depan Gedung Dewi Sartika, serta warna patung pada asset patung. Kecocokan byte dengan proyek Unity sumber tetap hanya terverifikasi untuk 37 berkas awal. Kekurangan metadata dicatat sebagai keterbatasan dokumentasi, bukan sebagai pekerjaan optimasi yang belum selesai.

## 3.4 Laporan Implementasi Proyek

### 3.4.1 Logbook Implementasi Proyek

Logbook implementasi disusun sebagai rekap bulanan berdasarkan hasil dokumentasi aktual. Rekap ini tidak menggunakan tanggal harian atau riwayat perubahan yang tidak tersedia, melainkan menghubungkan kegiatan, keluaran, dan bukti yang tersedia pada setiap tahap pelaksanaan.

Rekap kegiatan dan bukti pada setiap periode disajikan pada [TABREF:logbook_implementasi].

[TABLE-ID:logbook_implementasi]
[TABLECAPTION:Logbook Implementasi Asset 3D dan Pengelolaan Data]

[TABLE]
Periode | Kegiatan | Hasil | Bukti Dokumentasi | Status
Bulan 1 | Observasi, wawancara, pengambilan foto, dan identifikasi kebutuhan | Kebutuhan asset dan struktur data teridentifikasi | Notulensi wawancara, dokumen riset, dan arsip foto referensi | Selesai
Bulan 2 | Perancangan ERD, skema, dan pemodelan awal | Struktur database dan bentuk awal asset tersedia | ERD, SQL setup, dan screenshot proses Unity | Selesai
Bulan 3 | Pemodelan, material, tekstur, prefab, dan pengisian seed | Asset serta data gedung atau fasilitas mulai terhubung | Render asset, hierarki, inventaris material, dan seed SQL | Selesai
Bulan 4 | Penyelesaian hierarki, `Pointer`, serta pemetaan nama | GameObject tujuan dan `unity_object_name` tersusun | Hierarki prefab dan screenshot nama objek Unity | Selesai
Bulan 5 | Pemeriksaan constraint, asset, dan konsistensi nama | Temuan integritas dan mismatch terdokumentasi | Screenshot constraint, metrik asset, dan `DatabaseSyncChecker` | Selesai
Bulan 6 | Koreksi, pengujian akhir, dan penyusunan laporan | Bukti implementasi dan hasil pengujian dirangkum | Hasil Black Box, UAT, survei, dan dokumentasi final | Selesai
[/TABLE]

Rekap logbook tersebut menunjukkan hubungan antara aktivitas pada Gantt dan artefak yang tersedia. Status selesai menyatakan bahwa kegiatan dan bukti dokumentasinya telah dimasukkan ke draft; status tersebut tidak memperluas atribusi ke kode API, dashboard, navigasi, atau engine milik anggota lain.

### 3.4.2 Hasil dan Bukti Implementasi Asset 3D Gedung dan Fasilitas

Bukti yang diserahkan memuat render dan tangkapan hierarki asset 3D gedung serta fasilitas yang tersedia pada folder dokumentasi. Sebelas pasangan render dan hierarki yang tersedia digunakan sebagai sampel representatif. Ketersediaan bukti dirangkum pada [TABREF:inventaris_bukti_aset]. Status pada tabel menyatakan kepemilikan serta keberadaan berkas bukti, bukan bahwa seluruh asset telah lulus pengujian visual, performa, atau integrasi.

[TABLE-ID:inventaris_bukti_aset]
[TABLECAPTION:Inventaris Bukti Asset Gedung dan Hierarki]

[TABLE]
No. | Asset | Render Asset | Tangkapan Hierarki | Status Bukti
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

Representasi asset Cipto Mangunkusumo yang tersedia sebagai bukti diperlihatkan pada [FIGREF:evidence_asset_cipto], sedangkan susunan objeknya terdokumentasi pada [FIGREF:evidence_hierarchy_cipto]. Pasangan bukti tersebut memungkinkan bentuk visual dibandingkan dengan struktur objek pada Unity.

[FIGURE:evidence_asset_cipto]
[FIGCAPTION:Asset 3D Gedung Cipto Mangunkusumo]

[FIGURE:evidence_hierarchy_cipto]
[FIGCAPTION:Hierarki Asset Gedung Cipto Mangunkusumo]

Hasil representasi Gedung M. Yamin ditunjukkan pada [FIGREF:evidence_asset_myamin], sementara daftar objek penyusunnya dapat ditelusuri melalui [FIGREF:evidence_hierarchy_myamin].

[FIGURE:evidence_asset_myamin]
[FIGCAPTION:Asset 3D Gedung M. Yamin]

[FIGURE:evidence_hierarchy_myamin]
[FIGCAPTION:Hierarki Asset Gedung M. Yamin]

Asset dengan susunan fasad yang lebih kompleks terlihat pada [FIGREF:evidence_asset_wahidin], dan struktur hierarkinya direkam pada [FIGREF:evidence_hierarchy_wahidin].

[FIGURE:evidence_asset_wahidin]
[FIGCAPTION:Asset 3D Gedung Wahidin Sudiro Husodo]

[FIGURE:evidence_hierarchy_wahidin]
[FIGCAPTION:Hierarki Asset Gedung Wahidin Sudiro Husodo]

Contoh lain hasil representasi gedung dapat dilihat pada [FIGREF:evidence_asset_dewi]. Dalam bukti hierarki pada [FIGREF:evidence_hierarchy_dewi], prefab Dewi Sartika menampilkan objek `CullingPoint`, child `Pointer`, dan objek tujuan `dewi_sartika` sehingga struktur integrasinya dapat ditelusuri secara visual.

[FIGURE:evidence_asset_dewi]
[FIGCAPTION:Asset 3D Gedung Dewi Sartika]

[FIGURE:evidence_hierarchy_dewi]
[FIGCAPTION:Hierarki Asset Gedung Dewi Sartika]

Bukti visual tersebut memperkuat dokumentasi keberadaan asset dan hierarki. Status kelengkapan metadata tiga asset pembanding visual serta tiga asset dengan pengukuran teknis dirangkum pada [TABREF:status_metadata_aset].

[TABLE-ID:status_metadata_aset]
[TABLECAPTION:Status Kelengkapan Metadata Asset Prioritas]

[TABLE]
Asset | Bukti Tersedia | Keterbatasan Dokumentasi | Status
Cipto Mangunkusumo | Foto aktual, render, hierarki | Versi prefab dan catatan keputusan perubahan tidak tersedia | Bukti visual dan struktur tersedia
M. Yamin | Foto aktual, render, hierarki | Versi prefab dan catatan keputusan perubahan tidak tersedia | Bukti visual dan struktur tersedia
Wahidin Sudiro Husodo | Foto aktual, render, hierarki | Versi prefab dan catatan keputusan perubahan tidak tersedia | Bukti visual dan struktur tersedia
Ki Hajar Dewantara | Referensi visual, render, hierarki, ukuran prefab, GameObject, mesh, dan vertex | Catatan keputusan perubahan belum lengkap | Inventaris visual dan teknis tersedia
Dewi Sartika | Referensi visual, render, hierarki, objek `Pointer`, ukuran prefab, GameObject, mesh, dan vertex | Catatan keputusan perubahan belum lengkap | Struktur integrasi dan inventaris teknis tersedia
Jenderal Soedirman | Referensi visual, render, hierarki, ukuran prefab, GameObject, mesh, dan vertex | Sumber dan tanggal referensi visual belum tersedia | Inventaris visual dan teknis tersedia
[/TABLE]

Asset lain dalam scope juga dibuat dan ditata penulis serta telah memiliki bukti render atau hierarki sesuai dokumentasi yang tersedia. Namun, seluruh asset belum memiliki catatan kondisi akhir, keputusan desain, masalah yang ditemukan, tindakan perbaikan, dan hasil pemeriksaan formal. Karena itu, subbab ini membedakan atribusi pekerjaan dari keberhasilan teknis seluruh asset.

### 3.4.3 Hasil dan Bukti Rancangan Skema serta Pengelolaan Data

Bukti database yang terdapat dalam repository laporan dirangkum pada [TABREF:status_bukti_basis_data]. Ringkasan ini difokuskan pada skema dan ERD yang dirancang penulis, pengelolaan record gedung atau fasilitas, serta pemetaan `unity_object_name`.

[TABLE-ID:status_bukti_basis_data]
[TABLECAPTION:Status Bukti Rancangan Skema dan Pengelolaan Data]

[TABLE]
Komponen | Bukti Tersedia | Temuan | Batas Interpretasi
ERD inti | Gambar ERD pada Subbab 2.3.4 dan sumber PlantUML | Empat tabel inti beserta relasi dan batasannya dapat ditelusuri | Tabel Denah 2D, autentikasi, audit aplikasi, dan analitik merupakan ekstensi sistem
Struktur data dan constraint | Berkas setup, representasi DDL pada Subbab 3.2.3, serta inventaris constraint pada Subbab 3.3.1 | Primary key, beberapa unique constraint, foreign key, dan dua aturan `ON DELETE SET NULL` dapat ditelusuri | Berkas setup tidak dijalankan saat penyusunan laporan sehingga tidak membuktikan kondisi produksi terkini
Pengelolaan record | Contoh nilai `unity_object_name` gedung dan fasilitas serta inventaris seed 311 record | Kolom, contoh identifier, jumlah fasilitas per induk, dan temuan kualitas data dapat ditelusuri | Seed final belum diterapkan ulang pada Supabase aktif
Pemetaan asset–data | Hierarki prefab serta hasil `DatabaseSyncChecker` pada Subbab 3.3.2 dan 3.5.5 | Identifier dibandingkan antara record dan GameObject tujuan pada dua tangkapan dengan cakupan berbeda | Kedua tangkapan tidak memiliki metadata versi dan waktu yang cukup untuk menjadi perbandingan sebelum dan sesudah
[/TABLE]

Pemeriksaan endpoint pada database aktif menunjukkan 19 gedung, 331 fasilitas, dan 323 identifier. Angka tersebut merupakan kondisi pada saat pemeriksaan lama. Seed final memuat 19 gedung dan 311 fasilitas setelah perapian data, tetapi belum diterapkan ulang pada Supabase aktif. Karena itu, laporan tidak menggunakan hasil pemeriksaan lama sebagai hasil pengujian seed final.

Inventaris seed final memuat 311 fasilitas pada kelompok induk yang tercantum di dalam seed. Ringkasannya disajikan pada [TABREF:inventaris_seed_fasilitas] sebagai isi seed yang belum otomatis dianggap sama dengan data produksi atau kondisi lapangan terbaru.

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
Pemetaan Masjid | Masjid merupakan asset visual terpisah, sedangkan record fasilitasnya menggunakan `id_gedung = 6` | Nama asset visual dan induk database dapat berbeda bila tidak dicatat secara eksplisit | Pertahankan catatan pemetaan asset visual–record pada inventaris dan pengujian
Pemisahan entitas gedung | Gedung Soepomo, Gedung Soetomo, Yos Sudarso, RA Kartini, Lapangan Basket, parkir, lapangan, dan entitas lain dicatat sebagai record gedung yang berbeda; `id_gedung = 17` adalah Gedung Soetomo pada seed terbaru | Penyamaan nama atau fungsi dapat menghasilkan pemetaan yang salah | Cocokkan nama record gedung dengan GameObject dan data fasilitas pada saat sinkronisasi
Kemutakhiran nama belum terjamin | Pengumpulan lapangan dilakukan mandiri dengan informasi ruangan yang terbatas | Nama atau fungsi ruang dapat berbeda dari kondisi terbaru | Verifikasi melalui pengelola gedung, denah terbaru, atau sumber institusi serta catat tanggal verifikasi
[/TABLE]

Kontribusi penulis pada bagian database adalah perancangan empat tabel inti dan ERD, kebutuhan kebijakan RLS, struktur tabel `audit_logs`, pengelolaan record gedung atau fasilitas, serta pemetaan `unity_object_name`. Supabase Auth, pencatatan audit melalui layanan aplikasi, API, serta Dashboard diatribusikan sebagai konteks implementasi Iman. Keberhasilan pengelolaan data dinilai melalui struktur relasi, kualitas seed, dan konsistensi nama, bukan melalui klaim penerapan SQL produksi atau trigger audit database.

## 3.5 Hasil Pengujian Proyek

### 3.5.1 Pengujian Fungsional Bersama

<!-- PIPELINE:INCLUDE content/shared/testing/blackbox.md -->

### 3.5.2 Pengujian Integritas dan Relasi Database

Skenario pengujian integritas memeriksa foreign key, kolom wajib, batasan unik, dan perilaku perubahan atau penghapusan record induk. Constraint seperti `NOT NULL`, `UNIQUE`, dan `FOREIGN KEY` perlu diuji pada migration yang sama dengan versi produk yang dilaporkan (PostgreSQL Global Development Group 2026a). Tangkapan kueri katalog telah mengonfirmasi sebagian struktur constraint produksi, tetapi berkas migration dan hasil percobaan pelanggaran constraint belum tersedia. Oleh karena itu, matriks pada [TABREF:hasil_uji_integritas_db] membedakan verifikasi struktur dari pengujian perilaku.

[TABLE-ID:hasil_uji_integritas_db]
[TABLECAPTION:Matriks Pengujian Integritas dan Relasi Database]

[TABLE]
Skenario | Input | Hasil yang Diharapkan | Hasil Aktual | Status | Bukti yang Diperlukan
Inventaris struktur constraint | Kueri katalog constraint pada tabel `gedung`, `fakultas`, `fasilitas`, dan `program_studi` | Primary key, unique constraint, foreign key, dan aturan penghapusan dapat ditelusuri | 12 baris ditampilkan; bagian yang terlihat mengonfirmasi beberapa PK, UNIQUE, FK, dan `ON DELETE SET NULL` | Bukti struktur tersedia | Gambar inventaris constraint pada Subbab 3.3.1, ekspor 12 baris penuh, serta migration terkait
Pemetaan record Masjid | Bandingkan nama asset visual, `id_gedung`, dan tabel `fasilitas` | Record fasilitas memiliki induk yang sesuai dengan skema data | Masjid merupakan asset visual terpisah dengan record fasilitas pada `id_gedung = 6` | Sesuai pada seed; produksi belum diverifikasi | Seed terbaru, ekspor produksi, dan bukti pemetaan asset
Pemetaan record Soetomo | Bandingkan nama gedung, `id_gedung`, dan tabel `gedung` | Record mengarah ke entitas gedung yang benar | Seed terbaru menetapkan `id_gedung = 17` sebagai Gedung Soetomo, terpisah dari Lapangan Basket | Sesuai pada seed; produksi belum diverifikasi | Seed terbaru, ekspor produksi, dan retest konsumsi data
FK fasilitas ke gedung | Insert `fasilitas.id_gedung` yang tidak ada | Operasi ditolak oleh foreign key | Belum dieksekusi | Menunggu eksekusi | Query, pesan galat, dan tangkapan Supabase
FK fakultas ke gedung utama | Insert `fakultas.id_gedung_utama` yang tidak ada | Operasi ditolak oleh foreign key | Belum dieksekusi | Menunggu eksekusi | Query, pesan galat, dan tangkapan Supabase
FK program studi ke fakultas | Insert `program_studi.id_fakultas` yang tidak ada | Operasi ditolak oleh foreign key | Belum dieksekusi | Menunggu eksekusi | Query, pesan galat, dan tangkapan Supabase
Keunikan nama objek | Insert dua nilai `unity_object_name` yang sama | Record kedua ditolak oleh unique constraint | Belum dieksekusi | Menunggu eksekusi | Query, pesan galat, dan nama constraint
Kolom wajib | Insert record tanpa kolom `NOT NULL` | Operasi ditolak | Belum dieksekusi | Menunggu eksekusi | Query dan pesan galat
Perilaku penghapusan induk | Hapus gedung atau fakultas yang masih dirujuk | Hasil mengikuti aturan `ON DELETE` pada migration aktual | `ON DELETE SET NULL` terlihat pada dua foreign key; perilaku belum dieksekusi | Struktur terverifikasi sebagian; eksekusi menunggu | DDL aktual, data sebelum dan sesudah, serta tangkapan hasil
[/TABLE]

### 3.5.3 Verifikasi Konteks Akses Data dan Pencatatan Audit

Skenario database pada [TABREF:hasil_black_box] digunakan sebagai konteks untuk memastikan record yang dikelola penulis dibaca dan diubah melalui jalur sistem yang semestinya. Bagian ini tidak menguji atau mengatribusikan konfigurasi RLS, Supabase Auth, maupun layanan audit kepada Dwikhi. Ringkasan konteks hasil bersama disajikan pada [TABREF:hasil_uji_rls_audit].

[TABLE-ID:hasil_uji_rls_audit]
[TABLECAPTION:Ringkasan Verifikasi Konteks Akses Data dan Pencatatan Audit]

[TABLE]
Skenario Sistem | Hasil Aktual | Status Bersama | Relevansi terhadap Pekerjaan Dwikhi
Pembacaan data publik | Pengujian bersama melaporkan akses baca berjalan | Lulus pada pengujian bersama | Record gedung atau fasilitas dapat dikonsumsi sistem
Penolakan operasi anonim | Pengujian bersama melaporkan operasi tanpa autentikasi ditolak | Lulus pada pengujian bersama | Perubahan record dilakukan melalui jalur terautentikasi
Pengelolaan data terautentikasi | Fungsi dashboard diuji pada pengujian bersama | Lulus pada pengujian bersama | Penulis dapat mengelola data melalui komponen sistem yang tersedia
Pencatatan perubahan | Tangkapan dashboard memperlihatkan Create, Update, dan Delete yang dicatat melalui layanan aplikasi | Bukti konteks tersedia | Perubahan record dapat ditelusuri, tetapi implementasi layanan audit bukan kontribusi penulis
[/TABLE]

### 3.5.4 Pemeriksaan Visual dan Struktur Asset 3D

Pemeriksaan asset mencakup keterbandingan bentuk dengan referensi visual, keterbacaan material atau tekstur, struktur prefab, child `Pointer`, dan lokasi objek tujuan. Pemeriksaan tidak digunakan untuk menilai optimasi atau performa build karena aspek tersebut berada dalam scope pengembang engine.

Foto kondisi aktual, render asset, tangkapan hierarki, inventaris tekstur, ukuran prefab, dan pengukuran parsial tiga asset dapat digunakan sebagai input pemeriksaan. Namun, bukti tersebut belum memuat kriteria penerimaan, hasil aktual per butir, status lulus atau gagal, masalah yang ditemukan, dan hasil pengujian ulang. Oleh karena itu, status pada [TABREF:status_uji_visual_aset] menyatakan kesiapan bukti, bukan kelulusan asset.

[TABLE-ID:status_uji_visual_aset]
[TABLECAPTION:Status Pemeriksaan Visual dan Struktur Asset 3D]

[TABLE]
Cakupan | Input Bukti | Hasil yang Diharapkan | Hasil Aktual | Status | Batas Verifikasi
Cipto Mangunkusumo | Foto, render, hierarki | Bentuk dapat dibandingkan dan struktur dapat ditelusuri | Tiga jenis bukti tersedia | Terverifikasi secara visual | Asal-usul foto belum tercatat lengkap
M. Yamin | Foto, render, hierarki | Bentuk dapat dibandingkan dan struktur dapat ditelusuri | Tiga jenis bukti tersedia | Terverifikasi secara visual | Asal-usul foto belum tercatat lengkap
Wahidin Sudiro Husodo | Foto, render, hierarki | Bentuk dapat dibandingkan dan struktur dapat ditelusuri | Tiga jenis bukti tersedia | Terverifikasi secara visual | Asal-usul foto belum tercatat lengkap
Ki Hajar Dewantara, Dewi Sartika, dan Jenderal Soedirman | Render, hierarki, ukuran prefab, GameObject, mesh, dan vertex | Keberadaan asset dan struktur dapat ditelusuri | Inventaris visual dan teknis tersedia | Terverifikasi sebagai inventaris | Angka tidak digunakan sebagai hasil pengujian performa
Asset lain dalam scope | Render dan hierarki | Struktur asset dan objek tujuan dapat ditelusuri | Bukti render atau hierarki tersedia sesuai dokumentasi | Terverifikasi sesuai bukti yang tersedia | Tidak seluruh asset memiliki foto pembanding dengan asal-usul lengkap
[/TABLE]

### 3.5.5 Validasi Konsistensi Asset dan Database

Validasi konsistensi memeriksa bahwa setiap `unity_object_name` dalam cakupan memiliki tepat satu padanan GameObject tujuan dan tidak terdapat nama ganda. Pengujian juga perlu memastikan perbedaan kapitalisasi ditangani sesuai ketentuan integrasi saat Unity dijalankan tanpa mengabaikan konvensi penulisan proyek. Hasil yang terlihat pada [FIGREF:impl_sync_db_checker] dirangkum pada [TABREF:hasil_sync_checker_awal].

[TABLE-ID:hasil_sync_checker_awal]
[TABLECAPTION:Hasil Awal Pemeriksaan Konsistensi Nama]

[TABLE]
Indikator | Hasil Aktual | Interpretasi
Nama pada database | 97 | Cakupan data yang dibandingkan pada tangkapan
Ditemukan pada scene | 57 | Memiliki padanan yang ditemukan alat pemeriksa
Hanya pada database | 40 | Tidak ditemukan padanannya pada scene
Hanya pada scene | 18 | Tidak ditemukan padanannya pada database
Status keseluruhan | Belum konsisten | Masih terdapat mismatch pada kedua arah
[/TABLE]

Tangkapan awal memperlihatkan beberapa contoh nama yang belum cocok, tetapi tidak memuat versi endpoint, versi *scene*, waktu pengujian, atau hasil ekspor lengkap. Angka di atas karena itu diperlakukan sebagai kondisi pada satu tangkapan, bukan baseline terkontrol.

Pemeriksaan lain yang terlihat pada [FIGREF:evidence_sync_checker_lanjutan] mencakup 323 nama pada database, 320 nama ditemukan pada *scene*, 3 nama hanya terdapat pada database, dan 14 nama hanya terdapat pada *scene*. Bukti ini menunjukkan adanya pemeriksaan lanjutan dengan cakupan lebih besar, tetapi tidak dapat langsung dinyatakan sebagai perbaikan dari hasil sebelumnya karena total nama, versi *scene*, endpoint, dan tanggal tidak sama-sama tercatat.

[FIGURE:evidence_sync_checker_lanjutan]
[FIGCAPTION:Hasil Pemeriksaan Lanjutan Konsistensi Nama Asset dan Database]

Angka pemeriksaan lanjutan dirangkum pada [TABREF:hasil_sync_checker_lanjutan] tanpa mengubahnya menjadi klaim kelulusan.

[TABLE-ID:hasil_sync_checker_lanjutan]
[TABLECAPTION:Hasil Pemeriksaan Lanjutan Konsistensi Nama]

[TABLE]
Indikator | Hasil Aktual | Interpretasi
Nama pada database | 323 | Cakupan data yang dibandingkan pada tangkapan lanjutan
Ditemukan pada scene | 320 | Memiliki padanan yang ditemukan alat pemeriksa
Hanya pada database | 3 | Masih terdapat nama database tanpa padanan yang ditemukan
Hanya pada scene | 14 | Masih terdapat nama scene tanpa padanan database
Status keseluruhan | Belum sepenuhnya konsisten | Masih terdapat mismatch pada kedua arah dan metadata pengujian belum lengkap
[/TABLE]

`DatabaseSyncChecker` dikembangkan oleh Faiz dan digunakan Dwikhi untuk menemukan ketidaksesuaian. Daftar koreksi nama dan metadata pengujian ulang tidak tersedia pada bukti yang dihimpun. Oleh sebab itu, dua hasil pemeriksaan dipertahankan sebagai snapshot terpisah dan tidak dinyatakan sebagai bukti penyelesaian seluruh ketidaksesuaian.

### 3.5.6 User Acceptance Testing

<!-- PIPELINE:INCLUDE content/shared/testing/uat.md -->

### 3.5.7 Implementasi Hasil User Acceptance Testing

<!-- PIPELINE:INCLUDE content/shared/testing/uat-revisions.md -->

Kontribusi yang relevan dengan peran asset dan pengelolaan data terutama berkaitan dengan kelengkapan nama dan deskripsi fasilitas, konsistensi pemetaan objek, label ruang yang menggunakan nama tampilan, serta pemeriksaan kelengkapan data. Status implementasi dan hasil retest tidak boleh dinyatakan selesai sebelum bukti pada build produk yang sama tersedia.

---

# BAB IV PENUTUP

## 4.1 Kesimpulan

Kesimpulan yang dapat dirumuskan berdasarkan bukti yang telah tersedia adalah sebagai berikut:

1. Penulis membuat dan menata asset 3D gedung dan fasilitas yang memiliki GameObject pada scene Unity menggunakan observasi visual dan dokumentasi fotografis tanpa pengukuran dimensi instrumental. Sebelas pasangan render dan hierarki diposisikan sebagai sampel bukti representatif, bukan batas jumlah asset. Inventaris 37 material dan tekstur awal telah dicocokkan dengan proyek Unity sumber. Dari 30 berkas tambahan, dua referensi tekstur diterapkan pada Gedung Utama/Jenderal Soedirman, 21 referensi warna digunakan pada material Unity, logo Mandiri digunakan pada asset gedung bank pelengkap lingkungan, lima berkas alat olahraga digunakan pada objek di depan Gedung Dewi Sartika, dan satu berkas warna digunakan pada asset patung. Data GameObject, mesh, vertex, dan ukuran prefab untuk tiga asset digunakan sebagai dokumentasi keadaan asset, bukan hasil pengujian performa.
2. Penulis menyusun hierarki prefab, child `Pointer`, dan GameObject tujuan serta menetapkan `unity_object_name` untuk memisahkan geometri visual dari identifier navigasi. Hierarki Dewi Sartika memperlihatkan salah satu contoh penerapan melalui objek tujuan `dewi_sartika`.
3. Kontribusi database penulis meliputi perancangan empat tabel inti dalam ERD serta pengelolaan record gedung atau fasilitas. Setup sistem memuat tujuh tabel ekstensi yang tidak diklaim sebagai rancangan inti Dwikhi. Seed final memuat 19 gedung dan 311 fasilitas, sedangkan data Supabase aktif yang diperiksa masih memuat 19 gedung dan 331 fasilitas. Perbedaan ini dipertahankan secara eksplisit karena seed final belum diterapkan ulang pada database aktif.
4. Penulis merancang kebutuhan kebijakan RLS dan struktur tabel `audit_logs`. Supabase Auth serta layanan pencatatan audit Dashboard merupakan konteks implementasi Iman, sedangkan trigger audit database dan SQL produksi RLS tidak diklaim tanpa bukti. Hasil pengujian bersama hanya digunakan untuk memastikan jalur baca, perubahan data, dan pencatatan sistem tersedia.
5. Dwikhi menggunakan `DatabaseSyncChecker` buatan Faiz untuk memeriksa konsistensi nama. Tangkapan pertama mencatat 97 nama pada database, 57 ditemukan pada *scene*, 40 hanya terdapat pada database, dan 18 hanya terdapat pada *scene*. Tangkapan lain mencatat 323 nama, 320 ditemukan, 3 hanya pada database, dan 14 hanya pada *scene*. Kedua hasil belum dapat dibandingkan sebagai sebelum-sesudah karena versi *scene*, endpoint, waktu, dan daftar koreksi tidak tercatat bersama.

## 4.2 Saran

Saran pengembangan awal adalah sebagai berikut:

1. Menyimpan ERD, kamus data, dan catatan perubahan skema dengan versi yang dapat ditelusuri agar keputusan perancangan dapat direplikasi.
2. Menambahkan validasi format dan keunikan `unity_object_name` pada form administrator serta pada pipeline integrasi sebelum build.
3. Menetapkan checklist asset yang mencakup keterbandingan bentuk, struktur prefab, child `Pointer`, material atau tekstur, serta posisi dan nama objek tujuan.
4. Menggunakan `DatabaseSyncChecker` buatan Faiz sebagai pemeriksaan wajib setiap kali terdapat perubahan data gedung, fasilitas, atau hierarki *scene*.
5. Melengkapi rekap logbook bulanan, screenshot proses, contoh record sebelum dan sesudah perubahan, hasil pengujian, dan retest agar kontribusi penulis dapat ditelusuri secara akademik.

---

# DAFTAR PUSTAKA

Afiifah, K., Azzahra, Z. F., dan Anggoro, A. D. (2022). Analisis teknik Entity-Relationship Diagram dalam perancangan database: Sebuah literature review. _INTECH (Informatika dan Teknologi)_, 3(1), 8–11. https://doi.org/10.54895/intech.v3i1.1261

Aliyah, A., Hartono, N., dan Muin, A. A. (2025). Penggunaan User Acceptance Testing (UAT) pada pengujian sistem informasi pengelolaan keuangan dan inventaris barang. _Switch: Jurnal Sains dan Teknologi Informasi_, 3(2), 42–58. https://doi.org/10.62951/switch.v3i1.330

Jamaludin, J., dan Saepuloh, L. (2024). Tren riset twin digital smart campus. _Sang Pencerah: Jurnal Ilmiah Universitas Muhammadiyah Buton_, 10(2), 408–425. https://doi.org/10.35326/pencerah.v10i2.5317

Maulida, M., Zahro, F., Hakim, R., dan Akbar, M. S. (2025). Pengujian black box testing pada sistem website pemesanan online Toko Ayam Krispy. _Jurnal Media Akademik (JMA)_, 3(5). https://doi.org/10.62281/v3i5.1908

Muharam, Y., Anggara, M. B., dan Hanafi, T. J. (2023). Implementasi peta 3 dimensi menggunakan metode IMSDD (Interactive Multimedia System Design and Development) dan WebGL API berbasis web (Studi kasus di SMP Karya Pembangunan 2 Majalaya). _COMPUTING: Jurnal Informatika_, 10(1), 37–42. https://doi.org/10.55222/computing.v10i01.1155

PostgreSQL Global Development Group (2026a). _PostgreSQL 18 documentation: Constraints_. https://www.postgresql.org/docs/18/ddl-constraints.html

PostgreSQL Global Development Group (2026b). _PostgreSQL 18 documentation: The SQL language_. https://www.postgresql.org/docs/current/sql.html

Pricillia, T., dan Zulfachmi (2021). Perbandingan metode pengembangan perangkat lunak (Waterfall, Prototype, RAD). _Jurnal Bangkit Indonesia_, 10(1), 6–12. https://doi.org/10.52771/bangkitindonesia.v10i1.153

Putra, I. G. W. W., Dharma, E. M., dan Permana, P. T. H. (2026). Implementasi relational database dengan Row-Level Security (RLS) pada sistem inventory menggunakan Supabase dan React Native Expo (Studi kasus Bengkel Sari Merta). _JATI (Jurnal Mahasiswa Teknik Informatika)_, 10(2), 2443–2448. https://doi.org/10.36040/jati.v10i2.17551

React (2026). _Describing the UI_. https://react.dev/learn/describing-the-ui

Supabase (2026). _Data REST API_. https://supabase.com/docs/guides/api

Taurusta, C., Asiddiq, A. M., Suprianto, S., dan Setiawan, H. (2024). Visualisasi gedung kampus 1 Universitas Muhammadiyah Sidoarjo menggunakan augmented reality sebagai media informasi. _Journal of Technology and System Information_, 1(1), 55–70. https://doi.org/10.47134/jtsi.v1i1.2146

Unity Technologies (2026a). _Unity 6 Manual: Prefabs_. https://docs.unity3d.com/6000.0/Documentation/Manual/Prefabs.html

Unity Technologies (2026b). _Unity 6 Manual: ProBuilder_. https://docs.unity3d.com/6000.0/Documentation/Manual/com.unity.probuilder.html

UPNVJ. (2022). Lokasi Kampus UPN Veteran Jakarta. https://www.upnvj.ac.id/id/tentang-upn/lokasi-kampus.html

UPNVJ. (2025a). Kantin. https://www.upnvj.ac.id/id/fasilitas/kantin.html

UPNVJ. (2026). Rapat koordinasi Humas UPNVJ 2026: Fokus strategi komunikasi digital dan media sosial perguruan tinggi. https://www.upnvj.ac.id/id/berita/2026/02/rapat-koordinasi-humas-upnvj-2026-fokus-strategi-komunikasi-digital-dan-media-sosial-perguruan-tinggi.html

Vercel (2026). _Vercel Functions_. https://vercel.com/docs/functions

---

# LAMPIRAN 1. Surat Pernyataan Keaslian

Surat pernyataan keaslian mengikuti format resmi program studi. Tanggal dan tanda tangan basah dilengkapi pada dokumen administrasi final sebelum laporan diserahkan.

---

# LAMPIRAN 2. Dokumentasi Penyerahan Pakta Integritas kepada UPA TIK

Salinan pakta integritas yang telah diserahkan tidak berada dalam arsip penulis. Bukti yang tersedia berupa foto dokumentasi penyerahan dokumen kepada staf UPA TIK; lampiran ini tidak dimaksudkan sebagai pengganti salinan dokumen bertanda tangan atau surat keterangan resmi dari institusi. Identitas staf, nomor surat, tanggal pengesahan, dan status persetujuan tidak disimpulkan dari foto.

Foto kegiatan tersebut dirujuk pada [FIGREF:foto_penyerahan_pakta_upa_tik].

[FIGURE:foto_penyerahan_pakta_upa_tik]
[FIGCAPTION:Dokumentasi Penyerahan Pakta Integritas kepada UPA TIK]

---

# LAMPIRAN 3. Bukti Pemodelan dan Penataan Asset 3D

Bukti yang tersedia terdiri atas:

1. Dua puluh dua berkas referensi visual yang digunakan sebagai sampel dokumentasi kondisi gedung dan fasilitas.
2. Tiga puluh tujuh berkas material dan tekstur yang cocok dengan berkas pada proyek Unity sumber, ditambah 30 berkas yang terdiri atas dua tekstur Gedung Utama/Jenderal Soedirman, 21 referensi warna material, logo Mandiri untuk asset gedung bank pelengkap lingkungan, lima berkas alat olahraga di depan Gedung Dewi Sartika, dan satu berkas warna asset patung.
3. Sebelas render asset gedung, sebelas tangkapan hierarki sebagai sampel representatif, dan satu tangkapan proses pengerjaan.
4. Satu tangkapan riwayat perubahan.
5. Satu tangkapan versi Unity 6.4.
6. Satu tangkapan spesifikasi perangkat yang digunakan saat inventarisasi.
7. Satu inventaris ukuran prefab.
8. Tiga tangkapan pengukuran GameObject, mesh, dan vertex untuk Ki Hajar Dewantara, Dewi Sartika, dan Jenderal Soedirman.

Identitas pengambil gambar, tanggal dan lokasi sebagian foto, serta sumber atau lisensi beberapa material dan tekstur belum tercatat lengkap. Karena itu, bukti hanya digunakan untuk menunjukkan referensi visual, proses pembuatan, struktur asset, dan kecocokan berkas dengan proyek sumber. Bukti tidak digunakan untuk menyatakan kepemilikan sumber visual yang asal-usulnya tidak tersedia ataupun keberhasilan optimasi performa.

---

# LAMPIRAN 4. Skema Database dan Bukti Pengelolaan Data

Bukti yang tersedia adalah ERD empat tabel inti, rancangan kebutuhan kebijakan RLS, skema tabel `audit_logs`, berkas setup, DDL dokumentasi, inventaris constraint produksi, contoh nilai `unity_object_name`, serta inventaris seed final berisi 311 fasilitas pada 19 gedung. Daftar rinci fasilitas per gedung dan lantai dimuat setelah paragraf ini. Tanggal versi awal ERD, ekspor constraint produksi lengkap, catatan keputusan desain, ekspor data sebelum dan sesudah koreksi, serta daftar pemetaan seluruh GameObject tidak tersedia. Keterbatasan tersebut dinyatakan secara eksplisit dan tidak digantikan dengan klaim penerapan DDL, SQL produksi RLS, trigger audit, atau pengujian ulang pada database aktif. Layanan audit Dashboard tetap merupakan implementasi Iman.

<!-- PIPELINE:INCLUDE content/roles/dwikhi/facility-seed-inventory.md -->

---

# LAMPIRAN 5. Logbook dan Bukti Pengujian

Subbab 3.4.1 memuat rekap logbook bulanan yang disusun berdasarkan dokumentasi aktual, bukan logbook harian. Matriks verifikasi struktur data, pemeriksaan visual asset, dan konsistensi nama disajikan pada Subbab 3.5, sedangkan akses data serta audit aplikasi hanya diringkas dari pengujian sistem bersama. Bukti yang tersedia meliputi hasil Black Box dan UAT bersama, survei 21 responden, inventaris constraint, dua tangkapan `DatabaseSyncChecker` dengan cakupan berbeda, serta inventaris teknis tiga asset. Percobaan langsung pelanggaran foreign key, unique constraint, `NOT NULL`, dan `ON DELETE`, daftar koreksi ketidaksesuaian, serta pengujian ulang terkontrol tidak tersedia. Oleh karena itu, status pengujian dibatasi pada hasil yang memiliki bukti.

Instrumen UAT tertutup dan indeks bukti pengujian bersama disajikan setelah uraian ini. Instrumen tersebut merupakan bukti produk bersama dan tidak digunakan sebagai hasil pengujian teknis khusus asset atau database Dwikhi.

<!-- PIPELINE:INCLUDE content/shared/testing/appendix-instruments.md -->

---

# LAMPIRAN 6. Mockup Antarmuka sebagai Konteks Integrasi

Bagian lampiran ini memuat mockup antarmuka sebagai konteks penggunaan data oleh sistem dan bukan sebagai rancangan atau implementasi penulis. Konteks autentikasi administrator diperlihatkan pada [FIGREF:mockup_login_admin].

[FIGURE:mockup_login_admin]
[FIGCAPTION:Halaman Login Admin]

Konteks halaman utama administrator dan penambahan record gedung masing-masing diperlihatkan pada [FIGREF:mockup_dashboard_admin] dan [FIGREF:mockup_modal_tambah_gedung].

[FIGURE:mockup_dashboard_admin]
[FIGCAPTION:Halaman Dashboard Admin]

[FIGURE:mockup_modal_tambah_gedung]
[FIGCAPTION:Modal Tambah Data Gedung]

Konteks perubahan dan penghapusan record gedung masing-masing diperlihatkan pada [FIGREF:mockup_modal_edit_gedung] dan [FIGREF:mockup_modal_hapus_gedung].

[FIGURE:mockup_modal_edit_gedung]
[FIGCAPTION:Modal Update Data Gedung]

[FIGURE:mockup_modal_hapus_gedung]
[FIGCAPTION:Modal Konfirmasi Hapus Data Gedung]

Komponen analitik pada area administrator diperlihatkan pada [FIGREF:mockup_admin_traffic] sebagai konteks komponen dashboard di luar lingkup database utama laporan ini.

[FIGURE:mockup_admin_traffic]
[FIGCAPTION:Traffic Website Admin]

Rancangan bagian pembuka halaman publik dan ringkasan lalu lintas masing-masing ditunjukkan pada [FIGREF:mockup_hero_section] dan [FIGREF:mockup_public_traffic].

[FIGURE:mockup_hero_section]
[FIGCAPTION:Hero Section]

[FIGURE:mockup_public_traffic]
[FIGCAPTION:Public Traffic Statistics Website]

Kartu gedung dan fasilitas pada halaman publik diperlihatkan pada [FIGREF:mockup_fasilitas_aset] sebagai konteks penggunaan data inti yang dirancang penulis.

[FIGURE:mockup_fasilitas_aset]
[FIGCAPTION:Bagian Fasilitas dan Asset]

Konsumsi data fasilitas secara lebih rinci dirancang melalui modal daftar pada [FIGREF:mockup_modal_list_fasilitas] dan modal detail pada [FIGREF:mockup_modal_detail_fasilitas].

[FIGURE:mockup_modal_list_fasilitas]
[FIGCAPTION:Modal List Fasilitas dan Asset]

[FIGURE:mockup_modal_detail_fasilitas]
[FIGCAPTION:Modal Fasilitas dan Asset]

Bagian penutup halaman publik diperlihatkan pada [FIGREF:mockup_footer] untuk melengkapi konteks rancangan antarmuka.

[FIGURE:mockup_footer]
[FIGCAPTION:Bagian Footer]
