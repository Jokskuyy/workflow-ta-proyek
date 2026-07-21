# PENGEMBANGAN DASHBOARD WEB, INTEGRASI UNITY WEBGL, DAN DEPLOYMENT SISTEM DENAH VIRTUAL UPNVJ KAMPUS PONDOK LABU

Muhammad Iman Nugraha
2210511129

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
LAMPIRAN 3. Kode Sumber Utama
LAMPIRAN 4. Panduan Pengguna dan Kontrak Operasional
LAMPIRAN 5. Instrumen UAT Tertutup dan Indeks Bukti Pengujian
LAMPIRAN 6. Matriks Artefak dan Reproduksi Pengujian

# BAB I PENDAHULUAN

## 1.1 Latar Belakang

<!-- PIPELINE:INCLUDE content/shared/bab1/latar-belakang-umum.md -->

## 1.2 Identifikasi Masalah

Berdasarkan penjabaran latar belakang serta pengumpulan data awal yang telah diuraikan, identifikasi masalah dalam penelitian ini dirumuskan sebagai berikut:

1. Pengguna belum memiliki satu antarmuka web yang menyatukan informasi kampus, pencarian lokasi, dan akses ke denah virtual, sedangkan pengelola memerlukan antarmuka administratif untuk memperbarui konten secara terpusat.
2. Data yang digunakan aplikasi web dan Unity WebGL memerlukan jalur akses yang konsisten melalui integrasi Supabase, autentikasi, dan REST API tanpa menduplikasi atau mengambil alih rancangan skema database.
3. Hasil pencarian pada React perlu dihubungkan dengan Unity melalui kode lokasi yang konsisten. Aplikasi web juga memerlukan konfigurasi deployment yang dapat disesuaikan, baik untuk layanan hosting saat ini maupun untuk infrastruktur kampus pada masa mendatang.

## 1.3 Batasan Masalah

Untuk menjaga fokus, ruang lingkup, serta kelayakan penelitian, maka batasan masalah dalam pengembangan sistem integrasi denah virtual kampus dan dashboard profil Universitas Pembangunan Nasional Veteran Jakarta ditetapkan sebagai berikut:

1. Pengembangan sistem difokuskan pada integrasi antara backend, dashboard berbasis web, Denah 2D, dan visualisasi denah virtual 3D, tanpa mencakup pengembangan sistem akademik utama seperti sistem perkuliahan atau keuangan.
2. Cakupan area visualisasi dan data dibatasi pada lingkungan Kampus Universitas Pembangunan Nasional Veteran Jakarta Kampus Pondok Labu.
3. Sistem tidak mengelola data akademik utama seperti data mahasiswa, dosen, dan akreditasi. Apabila integrasi dengan sistem institusional dikembangkan pada masa mendatang, pertukaran data harus mengikuti kontrak dan izin resmi dari unit terkait.
4. Pengembangan pada sisi backend difokuskan pada perancangan dan implementasi REST API, integrasi layanan Supabase, serta penyediaan data untuk dashboard dan Unity WebGL. Perancangan skema database, kebijakan RLS, dan rancangan trigger basis data merupakan kontribusi Database Schema Designer. Pada aplikasi web, riwayat perubahan dicatat oleh layanan aplikasi setelah operasi CRUD.
5. REST API yang dikembangkan bersifat baca-saja untuk konsumen Unity dan integrator eksternal. Operasi Create, Read, Update, dan Delete pada Admin Panel dilakukan langsung melalui Supabase SDK dengan sesi Supabase Auth dan dibatasi oleh RLS.
6. Skema database, RLS, rancangan trigger basis data, aset 3D, dan hierarki `Pointer` digunakan sebagai bagian pendukung integrasi yang disediakan Database Schema Designer dan 3D Asset Designer. Aplikasi Unity, navigasi, alat bantu editor, optimasi, dan proses build Unity WebGL disediakan Engine Developer.
7. Lingkup penulis mencakup aplikasi React, REST API, integrasi Supabase Auth dan CRUD, penghubung perintah React ke Unity, penerimaan notifikasi kedatangan pada React, deployment artefak WebGL yang diterima dari Engine Developer, serta operasional layanan web. Integrasi tersebut dibatasi pada tujuan navigasi yang sedang aktif dan belum terhubung secara waktu nyata dengan seluruh sistem internal universitas.

Pembagian peran dan tanggung jawab pada proyek sistem dijelaskan lebih detail dalam [TABREF:peran_tanggung_jawab].

[TABLE-ID:peran_tanggung_jawab]
[TABLECAPTION:Peran dan Tanggung Jawab]

[TABLE]
Role | Tugas dan Tanggung Jawab
3D Asset Designer dan Database Schema Designer | Merancang aset visual 3D dan hierarchy prefab beserta `Pointer`, serta merancang skema database Supabase PostgreSQL, ERD, kebijakan RLS, dan rancangan trigger basis data.
3D Simulator dan Engine Developer | Mengembangkan runtime Unity WebGL, termasuk `BuildingDatabase`, `NavigationReceiver`, `DatabaseSyncChecker`, navigasi NavMesh, interaksi pengguna, optimasi performa, dan proses build WebGL.
Full Stack Web Developer, System Integrator, dan DevOps Engineer | Mengembangkan Public Dashboard dan Admin Panel React, REST API pada Vercel Serverless Functions, integrasi Supabase Auth dan CRUD, bridge React ke Unity, pencatatan analitik aplikasi, pengujian web, serta deployment dan operasional layanan web; Express dan Umami dikelola sebagai jalur opsional.
[/TABLE]

## 1.4 Tujuan dan Manfaat

### 1.4.1 Tujuan

Berdasarkan rumusan masalah pada Subbab 1.2, maka tujuan dari penelitian ini adalah sebagai berikut:

1. Mengembangkan Public Dashboard dan Admin Panel berbasis React untuk menyajikan informasi kampus, pencarian lokasi, autentikasi administrator, serta pengelolaan data konten.
2. Mengimplementasikan REST API berbasis Vercel Serverless Functions dan integrasi Supabase Auth untuk mendukung pertukaran data serta operasi CRUD sesuai kontrak data dan kebijakan akses yang disediakan Database Schema Designer.
3. Mengimplementasikan integrasi antarkomponen melalui endpoint data dan bridge perintah React ke Unity menggunakan kontrak `unity_object_name`.
4. Mengonfigurasi deployment dan operasional layanan web pada Vercel, termasuk aset Unity WebGL, environment variables, analitik aplikasi, health monitoring, serta kesiapan penyesuaian konfigurasi apabila layanan diintegrasikan dengan infrastruktur kampus pada tahap berikutnya.

### 1.4.2 Manfaat

Penelitian ini diharapkan dapat memberikan manfaat bagi berbagai pihak, antara lain:

1. Bagi pengguna publik, aplikasi menyediakan satu jalur akses untuk menelusuri informasi kampus, mencari gedung atau fasilitas, dan membuka denah virtual melalui peramban.
2. Bagi staf pengelola, Admin Panel menyediakan antarmuka untuk memperbarui konten sesuai hak akses tanpa mengubah kode aplikasi maupun artefak Unity selama kontrak `unity_object_name` tetap konsisten.
3. Bagi Humas UPNVJ sebagai mitra pengguna, aplikasi menjadi prototipe media informasi dan navigasi yang dapat dievaluasi untuk membantu mahasiswa baru, orang tua atau wali, sivitas akademika, dan pengunjung eksternal.
4. Bagi UPA TIK dan tim pengembang, REST API, bridge React–Unity, serta konfigurasi deployment menyediakan kontrak teknis yang terdokumentasi dan dapat disesuaikan apabila sistem memperoleh persetujuan untuk dipindahkan ke infrastruktur institusi.

## 1.5 Jadwal Kegiatan

Jadwal pelaksanaan proyek dirinci dalam bentuk Gantt Chart yang menyajikan alokasi waktu pengerjaan secara bertahap, sebagaimana disajikan pada [TABREF:jadwal_kegiatan]. Keseluruhan rangkaian kegiatan dilaksanakan dalam enam bulan.

[TABLE-ID:jadwal_kegiatan]
[TABLECAPTION:Jadwal Kegiatan]

[TABLE gantt]
Aktivitas | Bulan 1 | Bulan 2 | Bulan 3 | Bulan 4 | Bulan 5 | Bulan 6
Desain Arsitektur dan UI | X | | | | |
Pengembangan Backend | | X | X | | |
Pengembangan Frontend | | | X | X | |
Integrasi dan Pengujian Sistem | | | | X | X |
Revisi Final dan Penulisan Laporan | | | | | X | X
Dokumentasi | X | X | X | X | X | X
[/TABLE]

Alur pengerjaan dilaksanakan secara bertahap dengan beberapa kegiatan yang saling tumpang tindih. Tahapan-tahapan tersebut adalah:

1. Desain Arsitektur dan UI (Bulan 1): Tahap awal yang berfokus pada rancangan arsitektur sistem, kontrak integrasi, Use Case Diagram, ERD yang dirancang Database Schema Designer, dan rancangan awal antarmuka.
2. Pengembangan Backend (Bulan 2-3): Tahap implementasi kode sisi server, mencakup REST API Node.js dan integrasi layanan Supabase berdasarkan skema database yang dirancang Database Schema Designer.
3. Pengembangan Frontend (Bulan 3-4): Tahap implementasi kode sisi klien yang berfokus pada pembangunan Admin Dashboard dan Public Dashboard menggunakan React.js. Tahap ini berjalan bersamaan dengan sebagian pekerjaan backend.
4. Integrasi, Deployment, dan Pengujian Sistem (Bulan 4-5): Tahap penyatuan frontend, backend, dan Unity WebGL, konfigurasi deployment layanan web, serta validasi menggunakan skenario pengujian Black Box.
5. Revisi Final dan Penulisan Laporan (Bulan 5-6): Alokasi waktu khusus untuk perbaikan berdasarkan hasil pengujian, verifikasi ulang, dan penyusunan draf final laporan.
6. Dokumentasi (Bulan 1-6): Aktivitas ini dilakukan secara paralel sepanjang proyek untuk memastikan proses, desain, dan kode terdokumentasi dengan baik.

## 1.6 Sistematika Penulisan

Sistematika penulisan laporan Tugas Akhir Proyek ini disusun secara terperinci ke dalam empat bab utama guna memberikan alur pembahasan yang runtut dan sistematis:

1. **BAB I PENDAHULUAN**: Memaparkan latar belakang masalah navigasi spasial, identifikasi masalah, batasan penelitian, tujuan dan manfaat, jadwal kegiatan, serta sistematika penulisan.
2. **BAB II RANCANGAN PROYEK**: Menguraikan hasil observasi sistem berjalan, usulan solusi teknis berupa arsitektur terintegrasi, identifikasi kebutuhan fungsional dan teknis, rencana pengembangan prototyping, desain UML (Use Case, Activity, Sequence), kontrak data integrasi, rancangan antarmuka pengguna, serta rencana pengujian sistem.
3. **BAB III IMPLEMENTASI PROYEK**: Mendokumentasikan profil institusi mitra, metode pengembangan prototyping, detail implementasi sisi backend dan frontend (termasuk kode program), skema integrasi WebGL bridge, logbook aktivitas proyek, detail metadata sistem, serta hasil evaluasi pengujian fungsional (Black Box) dan penerimaan pengguna (UAT).
4. **BAB IV PENUTUP**: Menyajikan kesimpulan akhir dari hasil pengembangan sistem dan evaluasi pengujian, serta saran rekomendasi untuk pengembangan sistem berkelanjutan.

---

# BAB II RANCANGAN PROYEK

## 2.1 Observasi dan Analisis Kebutuhan Awal

Analisis kebutuhan awal menggunakan tiga sumber bukti, yaitu kuesioner pengalaman navigasi, tinjauan terhadap jalur informasi yang tersedia bagi pengguna, serta wawancara dan koordinasi dengan pemangku kepentingan. Pembahasan dibatasi pada bukti yang tersedia untuk proyek ini dan tidak dimaksudkan sebagai audit menyeluruh terhadap seluruh sistem informasi UPNVJ.

### 2.1.1 Sumber Data dan Batas Observasi

1. Kuesioner Pengguna
   Kuesioner diisi oleh 21 responden untuk memperoleh gambaran awal mengenai pengalaman mencari lokasi, penggunaan media navigasi, kebutuhan informasi, dan minat terhadap denah virtual 3D. Hasilnya digunakan untuk mengidentifikasi kebutuhan pengguna dalam ruang lingkup sampel dan tidak digeneralisasi sebagai representasi seluruh sivitas akademika UPNVJ.
2. Tinjauan Jalur Informasi dan Navigasi
   Tinjauan dilakukan terhadap media navigasi fisik yang dikenal responden serta situs resmi UPNVJ. Situs tersebut telah menyediakan halaman lokasi kampus dan informasi fasilitas secara terpisah (UPNVJ 2022; UPNVJ 2025a). Temuan ini digunakan untuk mengidentifikasi kebutuhan agregasi informasi dalam ruang lingkup proyek, bukan untuk menyatakan bahwa UPNVJ sama sekali tidak memiliki sistem, backend, atau layanan informasi terpusat.
3. Wawancara dan Koordinasi Pemangku Kepentingan
   Koordinasi dengan Kepala UPA TIK dan wawancara dengan Wakil Rektor Bidang Kemahasiswaan, Kerja Sama, dan Sistem Informasi digunakan untuk memahami batas akses data serta kemungkinan integrasi teknis. Kebutuhan navigasi tetap diturunkan dari kuesioner pengguna, sedangkan keterlibatan Humas UPNVJ sebagai mitra pengguna dibuktikan melalui UAT pada tahap evaluasi.

Ketiga sumber tersebut menjadi dasar analisis kebutuhan. Keputusan mengenai React, REST API, Supabase, Unity WebGL, dan Vercel dibahas sebagai rancangan solusi pada Subbab 2.2, bukan sebagai hasil observasi lapangan.

### 2.1.2 Analisis Kebutuhan Pengguna dan Sistem yang Berjalan

Sebanyak 20 dari 21 responden atau 95,2 persen merupakan sivitas akademika UPNVJ, sedangkan satu responden merupakan pengunjung eksternal. Komposisi pada [FIGREF:survey_01_profil] menunjukkan bahwa temuan terutama menggambarkan pengalaman pengguna internal dalam sampel yang diteliti.

[FIGURE:survey_01_profil]
[FIGCAPTION:Hasil Kuesioner: Profil Status Akademik Responden]

Penilaian terhadap papan penunjuk arah dan peta statis tidak menunjukkan penolakan yang dominan. Sebanyak 33,3 persen responden memberi nilai 1 atau 2, 23,8 persen memberi nilai 3, dan 42,9 persen memberi nilai 4 atau 5. Distribusi pada [FIGREF:survey_02_efektivitas] menunjukkan persepsi yang terbagi dengan nilai rata-rata sekitar 3,05 dari 5, sehingga kebutuhan sistem baru tidak dapat didasarkan pada klaim bahwa seluruh media yang tersedia tidak informatif.

[FIGURE:survey_02_efektivitas]
[FIGCAPTION:Hasil Kuesioner: Efektivitas Media Navigasi Kampus Saat Ini]

Dalam satu semester terakhir, sebanyak 57,1 persen responden mengalami kesulitan mencari lokasi sebanyak 1–3 kali, 9,5 persen mengalaminya lebih dari tiga kali, dan 33,3 persen tidak pernah mengalaminya. Dengan demikian, 14 dari 21 responden atau 66,7 persen pernah mengalami kesulitan setidaknya satu kali, sebagaimana disajikan pada [FIGREF:survey_03_frekuensi].

[FIGURE:survey_03_frekuensi]
[FIGCAPTION:Hasil Kuesioner: Frekuensi Kesulitan Menemukan Lokasi]

Ketika mencari lokasi, sebanyak 90,5 persen responden paling sering bertanya kepada orang di sekitar, petugas keamanan, atau layanan mahasiswa. Pola pada [FIGREF:survey_04_perilaku] menunjukkan bahwa bantuan interpersonal masih menjadi jalur utama dalam sampel, sedangkan papan penunjuk dan situs kampus digunakan oleh sebagian kecil responden.

[FIGURE:survey_04_perilaku]
[FIGCAPTION:Hasil Kuesioner: Perilaku Pengguna Saat Mencari Lokasi]

Sebanyak 76,2 persen responden memberi nilai 4 atau 5 terhadap pentingnya peta virtual 3D yang terintegrasi dengan informasi fasilitas. Penilaian pada [FIGREF:survey_05_urgensi] mendukung kebutuhan akan alternatif digital, tetapi tetap diperlakukan sebagai kebutuhan pengguna pada sampel, bukan bukti keberhasilan solusi yang belum diuji pada tahap observasi.

[FIGURE:survey_05_urgensi]
[FIGCAPTION:Hasil Kuesioner: Urgensi Kebutuhan Peta Virtual 3D]

Dalam rencana penggunaan, 9,5 persen responden menyatakan akan menggunakan denah setiap kali berada di kampus, 61,9 persen ketika mencari lokasi tertentu, 23,8 persen hanya sesekali, dan 4,8 persen tidak akan menggunakannya. Distribusi pada [FIGREF:survey_06_adopsi] menunjukkan bahwa fungsi pencarian lokasi merupakan konteks penggunaan yang paling relevan.

[FIGURE:survey_06_adopsi]
[FIGCAPTION:Hasil Kuesioner: Potensi Adopsi Denah Virtual 3D]

Informasi yang paling banyak dipilih untuk ditampilkan adalah nama gedung sebesar 95,2 persen, fasilitas dalam ruangan sebesar 52,4 persen, dan kapasitas ruangan sebesar 38,1 persen. Prioritas pada [FIGREF:survey_07_prioritas] menjadi dasar pemilihan data yang disajikan oleh frontend dan kontrak API.

[FIGURE:survey_07_prioritas]
[FIGCAPTION:Hasil Kuesioner: Prioritas Informasi Fasilitas Kampus]

Hasil kuesioner dan tinjauan sistem berjalan diringkas pada [TABREF:analisis_sistem_berjalan]. Matriks ini memisahkan kondisi yang teramati, kesenjangan dalam ruang lingkup proyek, dan implikasinya terhadap kontribusi penulis.

[TABLE-ID:analisis_sistem_berjalan]
[TABLECAPTION:Analisis Sistem yang Berjalan dan Implikasi Kebutuhan]

[TABLE]
Aspek | Kondisi Teramati atau Terverifikasi | Kesenjangan dalam Ruang Lingkup Proyek | Implikasi terhadap Kontribusi Penulis
Pencarian lokasi | Responden masih dominan meminta bantuan orang lain dan 66,7 persen pernah mengalami kesulitan setidaknya satu kali dalam satu semester | Belum tersedia satu jalur web proyek yang menghubungkan pencarian lokasi dengan denah virtual | Menyediakan Search Overlay React dan bridge perintah navigasi ke Unity
Informasi publik | Informasi lokasi dan fasilitas tersedia melalui beberapa halaman dan media | Pengguna proyek memerlukan agregasi informasi dan akses denah pada satu antarmuka | Mengembangkan Public Dashboard berbasis React
Pengelolaan konten | Data proyek memiliki aturan akses dan sumber yang berbeda sesuai kebijakan pemangku kepentingan | Konten yang digunakan dashboard dan API memerlukan antarmuka pengelolaan sesuai hak akses | Mengembangkan Admin Panel serta integrasi Supabase Auth dan CRUD
Distribusi data | React dan Unity membutuhkan bentuk data yang konsisten tetapi memiliki pola konsumsi berbeda | Konsumen web, runtime Unity, dan tooling editor memerlukan kontrak endpoint yang jelas | Menyediakan REST API dan membedakan `/api/unity/data` dari `/api/unity/names`
Deployment layanan | Implementasi proyek menggunakan layanan cloud dan memiliki jalur analitik aktif serta jalur self-hosted opsional | Konfigurasi hosting, secret, aset WebGL, analitik, dan health monitoring perlu terdokumentasi | Mengelola deployment Vercel, environment variables, header/cache aset, analitik Supabase, endpoint health, serta kesiapan Express/Umami opsional
[/TABLE]

Analisis tersebut tidak menyimpulkan bahwa UPNVJ secara institusional tidak memiliki backend atau sistem terpusat. Kesenjangan yang dimaksud adalah kebutuhan integrasi pada produk yang dikembangkan dalam proyek ini.

### 2.1.3 Hasil Wawancara Pemangku Kepentingan dan Implikasi Kebutuhan

Koordinasi dengan Asep Saeful Ridwan, S.Kom. selaku Kepala UPA TIK UPNVJ digunakan untuk memahami batas penggunaan sumber data institusi dan kemungkinan integrasi teknis. Koordinasi tersebut tidak digunakan untuk mengklaim bahwa UPA TIK merupakan mitra pengguna atau telah memberikan persetujuan penerapan sistem.

Wawancara dengan Dr. dr. Ria Maria Theresa, SpKJ., MH. selaku Wakil Rektor Bidang Kemahasiswaan, Kerja Sama, dan Sistem Informasi memberikan konteks bahwa pembagian data mentah dibatasi oleh kebijakan administratif. Oleh karena itu, kebutuhan navigasi dalam laporan ini didasarkan pada kuesioner pengguna, sedangkan wawancara digunakan untuk membatasi cara proyek mengakses dan menyajikan data.

Implikasi bagi penulis adalah membangun aplikasi dan kontrak integrasi yang tidak bergantung pada akses langsung ke seluruh sistem internal kampus. Humas UPNVJ ditempatkan sebagai mitra pengguna pada tahap evaluasi, sedangkan UPA TIK tetap menjadi pihak koordinasi teknis dan kebijakan data. Skema database dan kebijakan keamanannya merupakan kontribusi Database Schema Designer, sedangkan runtime Unity menjadi kontribusi Engine Developer. Pelaksanaan wawancara pemangku kepentingan didokumentasikan pada [FIGREF:foto_wawancara_warek].

[FIGURE:foto_wawancara_warek]
[FIGCAPTION:Dokumentasi Wawancara Pemangku Kepentingan]

## 2.2 Usulan Solusi

Berdasarkan analisis pada Subbab 2.1, proyek mengusulkan aplikasi web yang menggabungkan penyajian informasi kampus, pengelolaan konten, dan akses denah virtual dalam satu pengalaman pengguna. Solusi ini tidak dimaksudkan untuk menggantikan seluruh sistem institusional UPNVJ. Kontribusi penulis difokuskan pada antarmuka React, REST API, integrasi layanan, bridge React–Unity, serta deployment dan operasional layanan web.

Secara umum, solusi yang diusulkan memiliki karakteristik sebagai berikut:

1. Antarmuka Aplikasi Web
   a. Public Dashboard menyajikan informasi kampus, pemilih denah 2D atau tur 3D, pencarian lokasi, petunjuk interaksi, dan bantuan pemuatan.
   b. Admin Panel menyediakan autentikasi, pengelolaan data, konfigurasi denah 2D, audit log, dan analitik melalui halaman yang hanya dapat diakses setelah pengguna masuk.
2. Integrasi Berbasis Kontrak
   a. React menggunakan Supabase Auth dan Supabase SDK secara langsung untuk autentikasi, sesi, query, dan CRUD sesuai kebijakan akses yang tersedia.
   b. Vercel Serverless Functions menyediakan REST API bagi komponen yang memerlukan respons JSON, termasuk aplikasi Unity dan alat bantu Unity Editor.
3. Pemisahan Data dan Perintah Unity
   a. Unity menarik data runtime secara mandiri melalui `GET /api/unity/data`.
   b. React hanya mengirim kode tujuan melalui `SendMessage`; data gedung dan fasilitas tidak dikirim dari React ke Unity.
4. Deployment dan Operasional
   a. Implementasi saat ini menggunakan Vercel untuk React SPA, serverless API, dan penyajian artefak WebGL. Antarmuka analitik aktif menggunakan data Supabase, sedangkan Express dan Umami self-hosted dipertahankan sebagai jalur operasional opsional.
   b. Konfigurasi domain, environment variables, secret, dan konektivitas layanan dapat disesuaikan apabila sistem kelak diintegrasikan dengan infrastruktur kampus.
5. Batas Kolaborasi
   a. Penulis mengembangkan frontend, API, bridge sisi React, dan operasional layanan web.
   b. Skema database dan kontrol pada tingkat database disediakan Database Schema Designer, sedangkan runtime serta proses build Unity disediakan Simulator dan Engine Developer.

Karakteristik tersebut menempatkan aplikasi sebagai lapisan integrasi yang menghubungkan beberapa komponen tanpa mengaburkan batas kontribusi implementasinya. Struktur arsitektur sistem secara umum disajikan pada [FIGREF:diagram_arsitektur].

[FIGURE:diagram_arsitektur]
[FIGCAPTION:Diagram Arsitektur Sistem]

Sebagaimana diilustrasikan pada [FIGREF:diagram_arsitektur], interaksi frontend, backend, dan Unity WebGL berlangsung melalui tujuh alur berikut:

1. Pemuatan Aplikasi dan Aset: Browser memuat React SPA beserta artefak Unity WebGL dari Vercel Static Hosting. Penulis mengelola konfigurasi deployment, environment variables, serta header dan cache aset pada lapisan hosting tersebut.
2. Autentikasi dan Pengelolaan Data Frontend: React berinteraksi langsung dengan Supabase Auth melalui SDK untuk melakukan autentikasi administrator dan memperoleh sesi JWT. Public Dashboard dan Admin Panel melakukan query atau CRUD melalui Supabase SDK sesuai kebijakan RLS yang dirancang Database Schema Designer.
3. Penyediaan REST API: Vercel Serverless Functions menyediakan endpoint REST `/api/buildings`, `/api/rooms`, `/api/unity/data`, `/api/unity/names`, dan `/api/health`. Fungsi serverless mengambil data dari Supabase dan mengembalikannya dalam format JSON sesuai kebutuhan konsumennya.
4. Penarikan Data oleh Unity WebGL: Saat runtime dimulai, modul `BuildingDatabase` milik Unity memanggil `GET /api/unity/data` secara mandiri untuk memperoleh data gedung dan fasilitas. React tidak mengirimkan data JSON ke Unity. Endpoint `/api/unity/names` digunakan oleh `DatabaseSyncChecker` pada Unity Editor, bukan sebagai jalur data runtime.
5. Perintah dan Penyelesaian Navigasi: Ketika pengguna memilih lokasi pada mode 3D, frontend mengirim `unity_object_name` kepada Unity melalui `SendMessage`. Setelah pengguna tiba, Unity mengirim pemberitahuan `OnNavigationCompleted` beserta kode lokasi. React membandingkan kode tersebut dengan tujuan yang sedang aktif sebelum menampilkan notifikasi kedatangan. Pemberitahuan yang kosong, tidak valid, berbeda, atau diterima setelah pembatalan diabaikan.
6. Integrasi Analitik: Jalur aktif pada antarmuka mencatat dan mengagregasi `web_analytics_log` melalui Supabase. Express.js pada port 3001 menyediakan rate limiter dan endpoint proxy Umami sebagai jalur opsional untuk pengoperasian Umami self-hosted melalui Docker.
7. Batas Tanggung Jawab Integrasi: Penulis menangani frontend, REST API, penghubung pada sisi React, pencatatan audit oleh layanan aplikasi, dan operasional layanan web. Database Schema Designer menangani ERD, skema database, RLS, serta rancangan trigger basis data. 3D Asset Designer menangani aset 3D dan hierarki `Pointer`. Simulator dan Engine Developer menangani aplikasi Unity, pemetaan GameObject, navigasi, optimasi, dan proses build WebGL.

Fokus utama usulan solusi dalam laporan ini adalah pengembangan aplikasi Full Stack Web, integrasi antarsistem, dan operasional layanan web.

### 2.2.1 Identifikasi Kebutuhan Fungsional

Kebutuhan fungsional diturunkan dari kebutuhan pengguna, batas akses data, dan arsitektur integrasi pada Subbab 2.1 dan 2.2. Kebutuhan berikut difokuskan pada komponen yang dikembangkan atau diintegrasikan oleh penulis.

1. Kebutuhan Fungsional Pengguna Publik (User)
   a. Sistem harus menyajikan informasi utama kampus, statistik kunjungan, kartu gedung atau fasilitas, serta akses pencarian lokasi yang tersedia untuk publik.
   b. Sistem harus menyediakan pemilih mode denah 2D atau tur 3D sesuai dukungan hosting dan perangkat pengguna.
   c. Mode 2D harus menggunakan konfigurasi node, edge, dan entrance untuk menghitung serta menggambar rute menuju gedung yang dipilih.
   d. Mode 3D harus menyediakan canvas Unity WebGL beserta indikator pemuatan, pesan kesalahan, dan petunjuk interaksi.
   e. Sistem harus menyediakan pencarian gedung atau fasilitas pada antarmuka React dan menerjemahkan pilihan pengguna menjadi `buildingId` untuk denah 2D atau `unity_object_name` untuk tur 3D.
   f. Sistem harus menyediakan tombol bantuan atau petunjuk yang relevan pada area denah.
   g. Sistem harus mendukung Bahasa Indonesia dan Inggris serta menyimpan preferensi bahasa pada browser.
2. Kebutuhan Fungsional Administrator (Admin)
   a. Sistem harus mengautentikasi administrator melalui Supabase Auth dan mempertahankan sesi pada halaman admin yang dilindungi.
   b. Sistem harus menyediakan CRUD data gedung, fasilitas, program studi, dan konfigurasi jalur denah 2D melalui Supabase SDK sesuai kebijakan RLS. Data fakultas digunakan sebagai referensi pilihan pada formulir program studi dan tidak dikelola melalui tab CRUD terpisah.
   c. Sistem harus meminta konfirmasi sebelum penghapusan dan menampilkan status berhasil atau gagal dari setiap operasi.
   d. Sistem harus menampilkan audit log secara read-only dan menyajikan analitik yang tersedia bagi administrator.
3. Kebutuhan Fungsional API dan Bridge Unity
   a. Sistem harus menyediakan endpoint API `GET /api/unity/data` yang menyajikan data gedung dan fasilitas beserta `unity_object_name` dalam satu respons JSON terstruktur.
   b. Sistem harus menyediakan endpoint API `GET /api/unity/names` yang menyajikan array nama unik objek terdaftar untuk validasi sinkronisasi di Unity Editor.
   c. Sistem harus menyediakan endpoint `/api/buildings`, `/api/rooms`, dan `/api/health` untuk akses data dan pemeriksaan kondisi layanan sesuai kontrak masing-masing.
   d. Frontend harus mengirim `unity_object_name` ke method `NavigateTo` pada `NavigationReceiver` ketika pengguna memilih tujuan dan mengirim perintah berhenti ketika navigasi dibatalkan.
   e. Penghubung React–Unity tidak mengirim data gedung melalui `SendMessage`. Setelah navigasi selesai, React harus mencocokkan `unity_object_name` pada pemberitahuan `OnNavigationCompleted` dengan tujuan aktif sebelum menampilkan notifikasi kedatangan.
4. Kebutuhan Fungsional Deployment dan Operasional
   a. Sistem harus memisahkan konfigurasi layanan melalui environment variables dan tidak menanamkan secret ke dalam kode sumber.
   b. Hosting harus menyajikan React SPA, serverless API, serta artefak WebGL dengan header tipe konten dan cache yang sesuai.
   c. Operasional layanan harus menyediakan endpoint pemeriksaan kondisi layanan serta pembatasan jumlah permintaan pada helper Express untuk layanan analitik.

### 2.2.2 Identifikasi Kebutuhan Teknis

Kebutuhan teknis dipetakan berdasarkan fungsi setiap komponen dalam implementasi sebagai berikut:

1. Frontend Web
   a. React, TypeScript, dan Vite digunakan untuk membangun SPA, mengatur perpindahan halaman dan kondisi antarmuka, serta memisahkan Public Dashboard dari Admin Panel.
   b. Tailwind CSS dan Lucide React digunakan untuk penyusunan tampilan, sedangkan Recharts digunakan untuk grafik dan Fuse.js untuk pencarian toleran terhadap variasi kata.
   c. Unity WebGL loader API digunakan untuk memuat artefak engine ke elemen canvas, memantau progres, dan menyediakan method `SendMessage` melalui instance Unity.
2. Autentikasi dan Akses Data Aplikasi
   a. Supabase Auth menyediakan autentikasi dan sesi administrator.
   b. Supabase SDK digunakan React untuk query dan CRUD sesuai skema serta kebijakan RLS yang disediakan Database Schema Designer.
3. Backend dan Kontrak API
   a. Vercel Serverless Functions berbasis Node.js digunakan sebagai REST API utama.
   b. Setiap handler memvalidasi method HTTP, mengambil data melalui Supabase client, membentuk respons JSON, dan menangani kondisi kesalahan.
4. Analitik dan Helper Operasional
   a. Jalur analitik aktif menggunakan pencatatan dan agregasi `web_analytics_log` melalui Supabase.
   b. Express pada port 3001 menyediakan endpoint analitik Umami dan rate limiter sebagai jalur opsional; Umami dapat dijalankan secara self-hosted melalui Docker. Express bukan API utama yang dideploy melalui Vercel.
5. Hosting
   a. Vercel digunakan untuk menyajikan React SPA, Vercel Serverless Functions, dan artefak Unity WebGL.
   b. Environment variables, header respons, content type, cache aset, dan fallback routing SPA dikelola pada konfigurasi deployment.

### 2.2.3 Identifikasi Kebutuhan Non-Fungsional

Kebutuhan non-fungsional digunakan sebagai acuan kualitas aplikasi web dan operasional layanan. Pemenuhannya dievaluasi melalui pengujian web, pemeriksaan deployment, Lighthouse, Black Box, dan UAT.

1. Performa (Performance)
   a. React SPA harus tetap dapat digunakan sebelum pengguna mengaktifkan atau menunggu inisialisasi Unity WebGL.
   b. Pemuatan aset WebGL harus menampilkan progres dan pesan kondisi, menggunakan cache, serta menyesuaikan preload berdasarkan perangkat, preferensi Save-Data, dan kualitas koneksi yang dapat dideteksi browser.
   c. Performa halaman harus diukur secara berulang dengan Lighthouse pada mode mobile dan desktop sebagai dasar optimasi, bukan dinyatakan berhasil berdasarkan batas waktu yang tidak memiliki bukti pengukuran.
2. Kompatibilitas dan Aksesibilitas (Compatibility)
   a. Antarmuka harus responsif dan dapat diakses dengan baik melalui peramban perangkat seluler (mobile-first) sebagai platform utama pengguna, serta tetap optimal pada desktop.
   b. Antarmuka mendukung dua bahasa (Indonesia dan Inggris) dengan preferensi tersimpan secara persisten.
3. Keamanan (Security)
   a. Seluruh operasi modifikasi data pada Admin Panel wajib menggunakan sesi Supabase Auth yang valid.
   b. Frontend dan API harus mengikuti kebijakan RLS yang disediakan Database Schema Designer. Kunci dengan hak akses tinggi dan nilai rahasia tidak boleh dimasukkan ke dalam kode yang dikirim ke browser.
   c. Helper Express harus membatasi jumlah permintaan sesuai konfigurasi rate limiter.
4. Privasi (Privacy)
   a. Konfigurasi analitik harus membatasi data yang dikirim sesuai kebutuhan statistik penggunaan dan kebijakan layanan yang berlaku.
5. Usabilitas dan Aksesibilitas (Usability dan Accessibility)
   a. Sistem harus menampilkan loading screen, progres, pesan kesalahan, dan opsi mencoba kembali ketika engine 3D gagal dimuat.
   b. Search Overlay dan modal konfirmasi harus dapat dioperasikan menggunakan keyboard serta menyediakan label yang dapat dikenali teknologi bantu.
6. Keterpeliharaan (Maintainability)
   a. Perubahan data gedung atau fasilitas melalui Admin Panel dapat dikonsumsi pada pemuatan data berikutnya tanpa build ulang Unity selama nilai `unity_object_name` tetap sesuai dengan GameObject yang tersedia.
   b. Domain, kredensial layanan, versi artefak WebGL, dan konfigurasi hosting harus dapat disesuaikan tanpa mengubah kontrak data antarkomponen.

## 2.3 Rancangan Proyek

### 2.3.1 Rencana Pengembangan

Proses pengembangan proyek ini mengikuti model Prototyping yang terbagi ke dalam empat tahapan iteratif. Metode prototyping merupakan salah satu pendekatan pengembangan perangkat lunak yang bersifat iteratif dan berorientasi pada umpan balik pengguna, yang sangat berguna ketika kebutuhan sistem belum sepenuhnya spesifik (Syarif dan Risdiansyah 2024; Pricillia dan Zulfachmi 2021). Langkah-langkah dalam model pengembangan ini adalah sebagai berikut:

1. Pengumpulan Kebutuhan (Requirement Gathering)
   Melakukan wawancara pemangku kepentingan dan kuesioner awal untuk memetakan kebutuhan aplikasi web, kontrak API, integrasi denah, dan operasional layanan.
2. Membangun Prototyping Awal (Quick Design)
   Menyusun arsitektur aplikasi, kontrak data yang dikonsumsi, alur integrasi, dan mockup antarmuka Public Dashboard serta Admin Panel dengan mengacu pada ERD yang disediakan Database Schema Designer.
3. Evaluasi Prototipe (Evaluation dan Testing)
   Menguji komponen React, endpoint API, alur pengguna, bridge React–Unity, deployment, dan fungsi sistem menggunakan pengujian terotomasi serta Black Box Testing.
4. Iterasi Perbaikan (Iteration)
   Memperbaiki antarmuka, operasi CRUD sisi aplikasi, kontrak API, bridge, dan konfigurasi deployment berdasarkan hasil evaluasi. Perubahan skema atau kebijakan RLS dikoordinasikan dengan Database Schema Designer.

Tahapan pengembangan ini secara visual digambarkan pada [FIGREF:diagram_tahap_pengembangan].

[FIGURE:diagram_tahap_pengembangan]
[FIGCAPTION:Tahap Pengembangan]

### 2.3.2 Perancangan Information Architecture (IA)

Perancangan Information Architecture membagi aplikasi web ke dalam dua zona akses utama:

1. Halaman Publik (Public Route)
   a. Dashboard Utama (`/`): Menampilkan informasi utama kampus, statistik kunjungan, kartu aset gedung dan fasilitas, pemilih Denah 2D atau Denah 3D, pencarian lokasi, serta Tutorial dan FAQ.
   b. Pengaturan Bahasa: Toggle dinamis untuk memicu perubahan kamus bahasa lokal (ID/EN) yang diinjeksi ke komponen-komponen React.
2. Halaman Administratif Terlindungi
   a. Login (`/login`): Form otentikasi administrator terproteksi JWT.
   b. Admin Panel (`/admin`): Mengelola data gedung, fasilitas, program studi, dan konfigurasi denah 2D, serta menampilkan analitik dan audit log pada tab yang terpisah.

### 2.3.3 Perancangan Unified Modelling Language (UML)

Interaksi sistem dan diagram alir data dirancang menggunakan tiga jenis diagram UML. Unified Modelling Language (UML) merupakan standar pemodelan visual untuk menspesifikasikan, menggambarkan, membangun, dan mendokumentasikan artefak sistem perangkat lunak (Kurniawan 2018).

1. Use Case Diagram
   Aktor 'Pengguna Publik' dapat melihat informasi dan statistik kunjungan, mencari lokasi, membaca Tutorial/FAQ, serta memilih Denah 2D atau Denah 3D. Aktor 'Administrator' harus login sebelum mengelola gedung, fasilitas, program studi, dan konfigurasi Denah 2D atau meninjau analitik serta audit log. Legenda simbol use case ditunjukkan oleh [FIGREF:diagram_use_case_legenda], sedangkan diagram use case sistem terinci pada [FIGREF:diagram_use_case].

   [FIGURE:diagram_use_case_legenda]
   [FIGCAPTION:Legenda Use Case Diagram]

   [FIGURE:diagram_use_case]
   [FIGCAPTION:Use Case Diagram]

2. Activity Diagram
   Alur kerja pengelolaan data CRUD langsung melalui Supabase SDK digambarkan pada [FIGREF:diagram_activity_kelola_data], sedangkan pemilihan Denah 2D atau 3D beserta aliran perintah dan callback integrasinya digambarkan pada [FIGREF:diagram_activity_integrasi].

   [FIGURE:diagram_activity_kelola_data]
   [FIGCAPTION:Activity Diagram: Pengelolaan Data oleh Admin]

   [FIGURE:diagram_activity_integrasi]
   [FIGCAPTION:Activity Diagram: Integrasi Data Denah]

3. Sequence Diagram
   a. Autentikasi Admin: Menggambarkan proses login dari frontend React langsung ke Supabase Auth melalui `signInWithPassword`. Setelah sesi JWT dinyatakan valid, pengguna dapat membuka halaman Admin Panel seperti yang diilustrasikan pada [FIGREF:diagram_sequence_autentikasi].
   b. Sinkronisasi Data: Memetakan aliran pembaruan field `unity_object_name` dari Admin Dashboard, penyimpanan ke database Supabase, penarikan data JSON oleh Unity `BuildingDatabase` via HTTP request, dan pencocokan nama GameObject visual di scene, seperti yang diilustrasikan pada [FIGREF:diagram_sequence_sinkronisasi].

   [FIGURE:diagram_sequence_autentikasi]
   [FIGCAPTION:Sequence Diagram: Autentikasi Administrator]

   [FIGURE:diagram_sequence_sinkronisasi]
   [FIGCAPTION:Sequence Diagram: Sinkronisasi Data Gedung dan Unity]

### 2.3.4 Perancangan Integrasi Keamanan dan Analitik

Perancangan pada subbab ini membahas cara aplikasi menggunakan kontrol keamanan dan layanan analitik, bukan perancangan kebijakan database oleh penulis.

1. Autentikasi dan Sesi Aplikasi
   a. Halaman login React memanggil Supabase Auth melalui adapter aplikasi dan menyimpan status sesi pada `AuthContext`.
   b. `ProtectedRoute` hanya menampilkan Admin Panel setelah sesi tervalidasi, sedangkan logout menghapus sesi melalui Supabase Auth.
2. Konsumsi Kontrol Akses Database dan Audit Aplikasi
   a. React menjalankan query dan CRUD melalui Supabase SDK menggunakan konteks sesi pengguna.
   b. Pembatasan hak akses `anon` dan `authenticated` dilaksanakan oleh RLS yang dirancang Database Schema Designer (Putra et al. 2026). Pada implementasi yang diperiksa, layanan frontend mencatat audit setelah operasi CRUD. Laporan tidak menyatakan bahwa trigger basis data telah aktif karena bukti tersebut tidak ditemukan pada skema yang diperiksa.
3. Integrasi Analitik dan Rate Limiting
   a. Jalur analitik aktif mencatat dan mengagregasi `web_analytics_log` melalui Supabase, sedangkan Umami self-hosted dan helper Express tersedia sebagai jalur alternatif.
   b. Middleware rate limiter pada helper Express membatasi jumlah permintaan per alamat client dalam jendela waktu yang dikonfigurasi ketika jalur opsional tersebut dijalankan.

### 2.3.5 Perancangan Kontrak Data Integrasi

ERD, relasi antartabel, kebijakan RLS, dan rancangan trigger basis data merupakan kontribusi Database Schema Designer. Dalam lingkup System Integrator, penulis menetapkan kolom data yang dibutuhkan oleh antarmuka, API, dan penghubung React–Unity tanpa mengambil alih kepemilikan struktur database. Implementasi web mencatat audit melalui layanan aplikasi dan tidak digunakan sebagai bukti bahwa trigger database telah aktif. Pemetaan kontrak tersebut dirangkum pada [TABREF:kontrak_data_integrasi].

[TABLE-ID:kontrak_data_integrasi]
[TABLECAPTION:Kontrak Data yang Dikonsumsi Aplikasi dan API]

[TABLE]
Sumber Data | Field Utama yang Dikonsumsi | Penggunaan dalam Lingkup Penulis
`gedung` | `id`, `nama_gedung`, `deskripsi_gedung`, `lokasi`, `jumlah_lantai`, `foto_url`, `unity_object_name` | Kartu informasi, pencarian, CRUD Admin Panel, `/api/buildings`, dan payload gedung `/api/unity/data`
`fasilitas` | `id`, `nama_fasilitas`, `deskripsi_fasilitas`, `tipe_fasilitas`, `color`, `lantai`, `foto_url`, `id_gedung`, `unity_object_name` | Daftar fasilitas, pencarian, CRUD Admin Panel, `/api/rooms`, dan payload fasilitas `/api/unity/data`
`fakultas` | `id`, `nama_fakultas` | Referensi pilihan fakultas pada formulir program studi; tidak tersedia sebagai tab CRUD terpisah
`program_studi` | `id`, `nama_prodi`, `jenjang`, `id_fakultas`, `akreditasi` | CRUD program studi pada Admin Panel; tidak disajikan sebagai tabel pada halaman publik yang diverifikasi
`admin_users` | `username`, `nama_lengkap`, `role` | Metadata profil tambahan setelah autentikasi Supabase; bukan sumber password utama
`web_analytics_log` | hash pengunjung, path, perangkat, dan waktu kunjungan | Pencatatan page view dan agregasi statistik pada jalur analitik UI aktif
`audit_logs` | metadata aktor, aksi, tabel, record, waktu, data lama, dan data baru | Riwayat perubahan read-only pada Admin Panel
`campus_maps` dan tabel konfigurasi jalur | metadata peta, node, edge, marker gedung, dan entrance | Pemuatan denah 2D, perhitungan rute A*, dan editor konfigurasi denah pada Admin Panel
Supabase Auth | identitas pengguna dan sesi | Login, pemeriksaan akses Admin Panel, logout, dan konteks JWT untuk operasi CRUD
[/TABLE]

Kolom `unity_object_name` menjadi penghubung data antar-komponen. Frontend menggunakannya sebagai kode tujuan, API mengirimkannya kepada Unity, dan Unity memetakannya ke GameObject yang sesuai. Penulis menjaga konsistensi kode tersebut pada aplikasi dan API. Penataan serta pemeriksaan GameObject di Unity tetap menjadi kontribusi anggota terkait.

### 2.3.6 Perancangan Antarmuka

Rancangan antarmuka tidak mendokumentasikan seluruh halaman secara terpisah, melainkan memilih bukti visual yang langsung mendukung kontribusi penulis pada frontend dan integrasi sistem. Pilihan ini menjaga pembahasan tetap berfokus pada alur akses denah, pencarian React, bridge menuju Unity, dan pengelolaan konten oleh administrator.

1. Akses Denah dan Interaksi Publik
   Panel akses denah terbaru pada [FIGREF:ui_section_denah_kampus] menjadi titik masuk menuju pilihan Denah 2D atau Denah 3D serta menampilkan informasi cache aset WebGL. Pada mode 3D, canvas pada [FIGREF:ui_webgl_canvas] memperlihatkan runtime build aktif beserta bilah pencarian React, tombol bantuan, kontrol pergantian mode, minimap, dan petunjuk kontrol ringkas pada footer. Hasil pencarian pada mode 2D dalam [FIGREF:ui_search_overlay] membawa `buildingId` menuju gedung tujuan, sedangkan mode 3D menggunakan `unity_object_name` untuk bridge ke Unity; implementasi navigasi di dalam runtime Unity tetap menjadi tanggung jawab Engine Developer.

   [FIGURE:ui_section_denah_kampus]
   [FIGCAPTION:Panel Akses Denah 2D dan 3D]
   [FIGURE:ui_webgl_canvas]
[FIGCAPTION:Canvas Unity WebGL pada Build Aktif dengan Bantuan dan Bilah Pencarian React]
   [FIGURE:ui_search_overlay]
   [FIGCAPTION:Hasil Pencarian Lokasi pada Denah 2D]

2. Pengelolaan Konten Administrator
   Tampilan Admin Panel pada [FIGREF:mockup_dashboard_admin] menjadi bukti antarmuka React untuk menyaring dan menampilkan data fasilitas serta menyediakan tindakan tambah, ubah, dan hapus. Tangkapan layar memperlihatkan 331 fasilitas pada database Supabase aktif saat gambar diambil. Angka tersebut tidak disamakan dengan 311 data pada seed final karena penerapan ulang seed ke Supabase belum diverifikasi. Rincian autentikasi, pemanggilan Supabase SDK, dan pembatasan operasi berdasarkan RLS dijelaskan pada Subbab 3.2 sehingga tidak diperlukan tangkapan layar terpisah untuk setiap jendela CRUD.

   [FIGURE:mockup_dashboard_admin]
   [FIGCAPTION:Halaman Pengelolaan Fasilitas pada Admin Panel]

## 2.4 Rencana Pengujian Proyek

### 2.4.1 Pengujian API dan Integrasi Data

Pengujian API dirancang untuk memvalidasi handler Vercel Serverless Functions dan kontraknya dengan Supabase sebagai berikut:

1. Memastikan endpoint `/api/buildings`, `/api/rooms`, `/api/unity/data`, dan `/api/unity/names` mengembalikan status serta struktur JSON sesuai kontrak ketika data tersedia.
2. Memastikan `/api/unity/data` memisahkan array `gedung` dan `fasilitas`, sedangkan `/api/unity/names` hanya mengembalikan daftar `unityObjectNames` yang valid.
3. Memastikan method selain `GET` atau `OPTIONS` ditolak pada endpoint yang bersifat read-only dan kegagalan akses data menghasilkan respons kesalahan tanpa memaparkan kredensial.
4. Memastikan `/api/health` mengembalikan status layanan yang dapat digunakan untuk pemeriksaan operasional.
5. Menguji operasi query dan CRUD React melalui Supabase SDK menggunakan sesi terautentikasi serta memastikan kegagalan RLS ditampilkan sebagai kesalahan aplikasi. Pengujian ini tidak menggunakan endpoint POST, PUT, atau DELETE pada REST API.

### 2.4.2 Pengujian Web dan Operasional

Pengujian yang langsung berkaitan dengan kontribusi penulis direncanakan sebagai berikut:

1. Vitest dan React Testing Library digunakan untuk menguji utility, adapter autentikasi, komponen modal, translasi, perlindungan data, serta preload WebGL.
2. Integration test digunakan untuk memeriksa endpoint health, data gedung atau fasilitas, kontrak data Unity, dan kondisi kegagalan akses Supabase.
3. Alur pada browser diperiksa melalui Black Box Testing dan UAT. Playwright ditempatkan sebagai rencana pengujian lanjutan karena belum tersedia rangkaian pengujian dari awal sampai akhir yang dapat dilaporkan.
4. Lighthouse digunakan pada hasil build produksi melalui server pratinjau lokal untuk mengukur performa, aksesibilitas, praktik terbaik, dan SEO pada perangkat mobile serta desktop. Artefak JSON menjadi sumber angka, sedangkan hasil otomatis dibedakan dari pemeriksaan manual dan data pengguna nyata.
5. Pemeriksaan deployment memastikan React SPA, endpoint API, pengalihan halaman SPA, header keamanan, tipe konten, cache aset WebGL, dan endpoint pemeriksaan layanan tersedia sesuai konfigurasi.

### 2.4.3 Pengujian Fungsional (Black Box Testing)

Pengujian fungsional sistem menggunakan metode Black Box Testing untuk menguji 24 skenario pada dashboard admin, dashboard publik, API, dan integrasi navigasi Unity. Pengujian ini berfokus pada persyaratan fungsional perangkat lunak tanpa meninjau struktur kode internal program (Maulida et al. 2025). Cakupan skenario meliputi:

1. Autentikasi admin, proteksi Row-Level Security (RLS), dan pencatatan audit log.
2. Operasi Create, Read, Update, dan Delete (CRUD), validasi formulir, serta fitur tabel pada dashboard admin.
3. Agregasi kategori, pencarian, pergantian bahasa, penanganan kondisi pemuatan atau kesalahan, dan responsivitas dashboard publik.
4. Endpoint data denah, jembatan komunikasi React ke Unity, navigasi NavMesh, ketahanan `unity_object_name`, interupsi rute, dan pemuatan awal Unity WebGL.

### 2.4.4 User Acceptance Testing

User Acceptance Testing (UAT) dirancang untuk mengukur tingkat penerimaan dan penilaian peserta terhadap sistem yang dikembangkan. UAT dilaksanakan secara tertutup dengan peserta yang dipilih secara purposif berdasarkan keterlibatan dan kompetensinya dalam mengevaluasi proyek, yaitu dua dosen penguji, dua dosen pembimbing, dan satu perwakilan Humas UPNVJ. Pengujian ini tidak melibatkan sampel mahasiswa baru, orang tua atau wali, maupun pengunjung eksternal. Humas ditempatkan sebagai mitra pengguna, tetapi penilaian satu perwakilan tidak digunakan untuk mengklaim persetujuan formal atau mewakili seluruh pengguna UPNVJ (Aliyah et al. 2025).

Pengukuran dilakukan menggunakan skala Likert 1 sampai 5 melalui dua kuesioner terstruktur. Instrumen evaluasi Dashboard Publik memuat sembilan pernyataan dan instrumen evaluasi Dashboard Admin memuat sebelas pernyataan. Setiap instrumen diisi oleh empat peserta, dengan total lima peserta unik karena sebagian peserta mengevaluasi kedua instrumen. Istilah Dashboard Publik merujuk pada komponen aplikasi yang dinilai, bukan asal peserta pengujian. Persentase penerimaan dihitung dari perbandingan skor aktual terhadap skor maksimum, sedangkan masukan terbuka digunakan sebagai dasar penyusunan tindak lanjut pasca-uji.

---

# BAB III IMPLEMENTASI PROYEK

## 3.1 Profil Mitra

### 3.1.1 Nama Organisasi/Lembaga Mitra

Humas Universitas Pembangunan Nasional “Veteran” Jakarta (Humas UPNVJ).

### 3.1.2 Deskripsi Mitra

Humas UPNVJ menjadi mitra pengguna dalam proyek ini karena layanan navigasi ditujukan untuk membantu penyampaian informasi lokasi kepada mahasiswa baru, orang tua atau wali, sivitas akademika, dan pengunjung eksternal. Halaman resmi UPNVJ menjelaskan bahwa Humas UPNVJ mengoordinasikan strategi komunikasi digital bersama humas fakultas (UPNVJ 2026). Keterangan tersebut digunakan untuk menjelaskan hubungan Humas dengan penyampaian informasi kepada publik, bukan sebagai bukti bahwa sistem telah diterima sebagai layanan resmi institusi.

Universitas Pembangunan Nasional “Veteran” Jakarta (UPNVJ) berstatus Perguruan Tinggi Negeri sejak 6 Oktober 2014 berdasarkan Peraturan Presiden Nomor 120 Tahun 2014 (UPNVJ 2025b). Kampus Pondok Labu merupakan konteks penerapan proyek dan beralamat di Jalan R.S. Fatmawati Nomor 1, Jakarta Selatan. Halaman resmi lokasi kampus mencatat luas lahan 2,4 hektare, luas lantai bangunan 28.887 meter persegi, dan 71 ruang kuliah (UPNVJ 2022).

### 3.1.3 Hubungan Mitra dengan Proyek

Humas UPNVJ berperan sebagai mitra pengguna dan satu perwakilannya mengikuti UAT untuk memberikan perspektif evaluasi terhadap informasi serta navigasi. Keikutsertaan tersebut tidak digunakan untuk mengklaim persetujuan formal, serah terima sistem, atau representasi seluruh pengguna UPNVJ. UPA TIK tetap dicatat secara terpisah sebagai pihak koordinasi teknis, batas akses data, kemungkinan integrasi institusional, dan penyerahan pakta integritas. Hubungan setiap pihak dirangkum pada [TABREF:hubungan_mitra_proyek].

[TABLE-ID:hubungan_mitra_proyek]
[TABLECAPTION:Hubungan Pemangku Kepentingan dengan Proyek]

[TABLE]
Entitas | Hubungan dengan Proyek | Keluaran yang Relevan
Humas UPNVJ | Menjadi mitra pengguna; satu perwakilan mengikuti UAT dan memberikan perspektif evaluasi informasi serta navigasi | Masukan penerimaan pengguna yang dibatasi pada peserta UAT, tanpa klaim persetujuan institusional
Pengguna Publik | Memberikan data kebutuhan awal melalui kuesioner dan menggunakan Public Dashboard serta Denah 2D atau 3D | Antarmuka informasi, pencarian lokasi, petunjuk penggunaan, dan alternatif navigasi berbasis web
UPA TIK UPNVJ | Menjadi pihak koordinasi teknis untuk batas akses data, kemungkinan integrasi institusional, wawancara, dan penyerahan pakta integritas | Kontrak teknis dan batas penggunaan data tanpa mengklaim UPA TIK sebagai mitra pengguna atau penerima sistem
Tim Pengembang | Menyediakan komponen database, aset, runtime Unity, aplikasi web, dan deployment sesuai pembagian peran | Artefak lintas komponen yang terhubung melalui kontrak data dan deployment yang terdokumentasi
[/TABLE]

## 3.2 Metode Implementasi

Implementasi sistem dalam proyek ini dilakukan menggunakan pendekatan prototyping yang iteratif. Proses pengembangan difokuskan pada kontribusi penulis selaku Full Stack Web Developer, System Integrator, dan DevOps Engineer. Subbab ini menguraikan **metode dan teknik implementasi** (cara membangun) tiap komponen, sedangkan bukti keluaran dan hasil akhirnya disajikan pada Subbab 3.4.

### 3.2.1 Implementasi Back-end

Backend yang menjadi tanggung jawab penulis adalah REST API baca-saja berbasis Node.js pada folder `api/` dan dijalankan sebagai Vercel Serverless Functions. React tidak memakai endpoint tersebut untuk login atau operasi CRUD utama karena kedua proses itu dilakukan langsung melalui Supabase SDK. API digunakan oleh aplikasi Unity, alat bantu Unity Editor, pemeriksaan kondisi layanan, dan konsumen eksternal yang memerlukan akses data melalui HTTP.

Setiap fungsi API menerapkan CORS, menerima metode `GET` dan `OPTIONS`, serta menolak metode lain dengan status 405. Fungsi tersebut membuat Supabase client dari variabel lingkungan, lalu mengembalikan data JSON atau status 500 apabila query gagal. Potongan implementasi `/api/unity/data` berikut menunjukkan pengambilan data gedung dan fasilitas secara bersamaan tanpa memuat kredensial:

```javascript
const [gedungResult, fasilitasResult] = await Promise.all([
  supabase
    .from("gedung")
    .select("id, nama_gedung, deskripsi_gedung, lokasi, jumlah_lantai, unity_object_name")
    .order("id", { ascending: true }),
  supabase
    .from("fasilitas")
    .select("id, nama_fasilitas, deskripsi_fasilitas, tipe_fasilitas, id_gedung, lantai, foto_url, unity_object_name")
    .order("id_gedung", { ascending: true })
    .order("lantai", { ascending: true }),
]);

if (gedungResult.error) throw gedungResult.error;
if (fasilitasResult.error) throw fasilitasResult.error;

return res.status(200).json({
  gedung: gedungResult.data || [],
  fasilitas: fasilitasResult.data || [],
});
```

Kontrak endpoint pada implementasi yang diperiksa diringkas pada [TABREF:kontrak_endpoint_api].

[TABLE-ID:kontrak_endpoint_api]
[TABLECAPTION:Kontrak Endpoint Vercel Serverless Functions]

[TABLE]
Endpoint | Respons Utama | Konsumen atau Tujuan
`GET /api/health` | objek yang memuat status, pesan, dan waktu pemeriksaan | Pemeriksaan kondisi layanan
`GET /api/buildings` | daftar gedung beserta fasilitas terkait | Integrator eksternal dan kompatibilitas kontrak
`GET /api/rooms` | daftar fasilitas beserta data gedung | Integrator eksternal dan kompatibilitas kontrak
`GET /api/unity/data` | objek dengan array `gedung` dan `fasilitas` | `BuildingDatabase` pada runtime Unity
`GET /api/unity/names?type=gedung` atau `GET /api/unity/names?type=fasilitas` | array `unityObjectNames` | `DatabaseSyncChecker` pada Unity Editor
[/TABLE]

Supabase client pada fungsi serverless menggunakan URL proyek dan anon key dari variabel lingkungan deployment. Service role key tidak digunakan pada browser maupun fungsi Vercel yang bersifat baca-saja. Skema, relasi, dan RLS tetap menjadi tanggung jawab Database Schema Designer. Kontribusi penulis berada pada pemilihan kolom data, konsistensi bentuk respons, pembatasan metode HTTP, CORS, dan penanganan kesalahan.

### 3.2.2 Implementasi Front-end

Frontend diimplementasikan sebagai SPA menggunakan React 19, TypeScript, dan Vite 7. Provider aplikasi menyusun konteks bahasa, autentikasi, notifikasi, dan routing. Route `/` memuat Public Dashboard, `/login` dan `/admin/login` memuat halaman autentikasi, sedangkan `/admin` dibungkus `ProtectedRoute`. Komponen berat di bawah bagian awal halaman dimuat secara lazy agar initial render tidak menunggu seluruh modul.

1. Public Dashboard
   Public Dashboard mengambil data melalui Supabase SDK dan menyajikan informasi kampus, statistik kunjungan, kartu gedung atau fasilitas, Tutorial dan FAQ, pencarian lokasi, serta pemilih Denah 2D atau 3D. `DashboardContext` mengatur kondisi pemuatan, kesalahan, cache, dan pemuatan ulang data.
2. Admin Panel
   `AuthContext` memanggil adapter Supabase Auth, mempertahankan sesi, dan mengarahkan pengguna yang valid ke Admin Panel. Operasi CRUD gedung, fasilitas, program studi, dan konfigurasi denah 2D dilakukan melalui layanan aplikasi yang memanggil Supabase secara langsung. Validasi formulir, konfirmasi penghapusan, notifikasi, dan pembaruan cache memberikan umpan balik kepada administrator.
3. Denah 2D
   Mode 2D memuat konfigurasi peta aktif, node, edge, marker gedung, dan entrance dari Supabase. Setelah pengguna menentukan titik awal dan tujuan, frontend menggunakan `buildingId` untuk mencari entrance terkait, menjalankan algoritma A*, dan menggambar jalur sebagai SVG di atas gambar denah. Editor pada Admin Panel digunakan untuk mengatur marker, entrance, node, dan koneksi edge.
4. Pemuatan Unity WebGL
   Build Unity v0.8.6.1 dimuat menggunakan loader native Unity tanpa dependency `react-unity-webgl`. React membuat elemen canvas, menyiapkan URL loader, framework, WebAssembly, dan data, lalu menyimpan instance pada `window.unityInstance`. Potongan berikut berasal dari implementasi loader yang aktif:

```typescript
const unityConfig = {
  dataUrl: `${basePath}unity-builds/v0.8.6.1/Build/v0.8.6.1.data.unityweb`,
  frameworkUrl: `${basePath}unity-builds/v0.8.6.1/Build/v0.8.6.1.framework.js.unityweb`,
  codeUrl: `${basePath}unity-builds/v0.8.6.1/Build/v0.8.6.1.wasm.unityweb`,
  streamingAssetsUrl: "StreamingAssets",
  productVersion: "v0.8.6.1",
  matchWebGLToCanvasSize: true,
  devicePixelRatio: Math.min(window.devicePixelRatio || 1, 2),
};

const instance = await window.createUnityInstance(
  canvas,
  configWithProgress,
  configWithProgress.onProgress,
);
window.unityInstance = instance;
```

5. Preload dan Penanganan Kondisi
   `scheduleUnityPreload(10000)` menjadwalkan pengunduhan loader, framework, WebAssembly, dan data secara berurutan dengan prioritas rendah setelah halaman stabil. Preload otomatis dilewati pada perangkat mobile, mode Save-Data, koneksi 2G atau slow-2G, dan GitHub Pages. Ketika pengguna memulai mode 3D, antarmuka memeriksa dukungan WebGL, menampilkan progres dan pesan kesalahan, serta memanggil `Quit()` saat instance dilepas. Penanganan ini merupakan kontribusi frontend; implementasi joystick, NavMesh, dan kontrol di dalam runtime tetap menjadi kontribusi Simulator dan Engine Developer.

### 3.2.3 Implementasi Integrasi Front-end, Back-end, dan Unity WebGL

Sebagai System Integrator, penulis menghubungkan React, Supabase, Vercel Serverless Functions, dan artefak Unity WebGL melalui kontrak yang berbeda untuk autentikasi, data, serta perintah navigasi. Pemisahan ini mencegah frontend, API, dan runtime Unity menggunakan jalur data yang keliru.

1. Autentikasi dan Pengelolaan Data
   Halaman login React memanggil `signInWithPassword` melalui adapter Supabase Auth dan menerima sesi secara langsung. Setelah sesi dinyatakan valid, pengguna dapat membuka Admin Panel. Query, operasi CRUD, konfigurasi denah 2D, dan pencatatan audit dilakukan oleh layanan aplikasi melalui Supabase SDK sesuai RLS. Kontribusi penulis mencakup adapter, pengelolaan sesi, formulir, layanan data, penanganan respons, cache, dan umpan balik antarmuka.
2. Penyediaan Data melalui REST API
   Vercel Serverless Functions menyediakan kontrak JSON read-only. Endpoint `/api/unity/data` menyajikan data gedung dan fasilitas untuk runtime Unity, sedangkan `/api/unity/names` menyajikan daftar `unity_object_name` untuk `DatabaseSyncChecker` pada Unity Editor. React UI tidak bergantung pada `/api/buildings` atau `/api/rooms` untuk alur utamanya karena mengambil data langsung melalui Supabase SDK.
3. Penarikan Data Mandiri oleh Unity
   Saat Unity WebGL dimulai, `BuildingDatabase` yang dikembangkan Simulator dan Engine Developer memanggil `GET /api/unity/data`. Data nama tampilan dan `unity_object_name` disimpan sementara untuk digunakan oleh `NavigationReceiver`. React tidak mengirim data gedung atau fasilitas melalui `SendMessage`. Alur ini dipetakan pada [FIGREF:diagram_sequence_sinkronisasi].
4. Pengiriman Perintah Navigasi dari React
   `SearchOverlay` membentuk hasil yang memisahkan label tampilan, `buildingId`, dan `unityObjectName`. Pada mode 2D, `buildingId` digunakan frontend untuk menghitung rute A*. Pada mode 3D, React memanggil `window.unityInstance.SendMessage("NavigationReceiver", "NavigateTo", unityObjectName)`. Pembatalan rute menggunakan method `StopNavigation`.
5. Validasi Penyelesaian Navigasi
   Unity hanya mengirim pemberitahuan `OnNavigationCompleted` setelah pengguna benar-benar mencapai tujuan. Pembatalan navigasi, pergantian titik awal, atau tujuan yang tidak ditemukan tidak dianggap sebagai kondisi tiba. Pemberitahuan tersebut memuat `unity_object_name`, kemudian React membandingkannya dengan tujuan yang sedang aktif. Notifikasi kedatangan hanya ditampilkan apabila kedua data tersebut sesuai. Data yang kosong, tidak valid, atau berbeda diabaikan agar pengguna tidak menerima pemberitahuan yang keliru.
6. Deployment dan Batas Ownership
   Penulis mengelola deployment React SPA, Vercel Serverless Functions, variabel lingkungan, header dan cache aset, serta penyebaran artefak Unity WebGL yang diberikan oleh Engine Developer. Database Schema Designer tetap bertanggung jawab atas ERD, skema database, RLS, dan rancangan trigger basis data, sedangkan 3D Asset Designer bertanggung jawab atas aset 3D dan hierarki `Pointer`. Simulator dan Engine Developer bertanggung jawab atas `BuildingDatabase`, `NavigationReceiver`, `DatabaseSyncChecker`, navigasi, optimasi, dan proses build Unity WebGL. Implementasi web yang diperiksa mencatat audit melalui layanan aplikasi dan tidak membuktikan bahwa trigger basis data telah aktif.

### 3.2.4 Implementasi Deployment, Operasional Layanan, dan Kesiapan Integrasi Institusional

Pada tahap implementasi saat ini, Vercel digunakan untuk meng-host React SPA, Vercel Serverless Functions, dan artefak Unity WebGL v0.8.6.1. Supabase menyediakan data dan autentikasi. Jalur analitik antarmuka aktif juga menggunakan Supabase, sedangkan Express dan Umami tersedia sebagai jalur operasional opsional.

1. Deployment dan Konfigurasi Layanan
   Penulis mengelola environment variables, konfigurasi domain, fallback SPA, header keamanan, cache, serta content type artefak Unity WebGL. Artefak v0.8.6.1 yang telah dibangun oleh Engine Developer ditempatkan pada folder versi di layanan web; tahap kompilasi Unity dan optimasi engine tidak termasuk dalam kontribusi penulis.
2. Operasional dan Pemantauan
   Operasional layanan mencakup endpoint `/api/health`, pemeriksaan status respons aset WebGL, pengaturan cache, serta rate limiter pada helper Express. Docker Compose Umami dan endpoint proxy Express dipertahankan untuk jalur analitik alternatif, tetapi bukan dependensi jalur UI analitik yang aktif.
3. Kesiapan Integrasi Institusional
   Penggunaan Vercel pada tahap ini merupakan pilihan hosting implementasi proyek, bukan ketetapan arsitektur permanen. Apabila sistem kelak diintegrasikan dengan infrastruktur kampus, penyesuaian dapat dilakukan pada domain, environment variables, pengelolaan secret, konektivitas API, serta mekanisme identitas yang disetujui institusi. Kontrak REST API, struktur respons JSON, dan bridge React–Unity dipertahankan agar perubahan platform hosting tidak mengubah perilaku antarkomponen. Integrasi institusional tersebut belum diimplementasikan dan menjadi rencana pengembangan lanjutan.

## 3.3 Konfigurasi dan Kontrak Operasional Sistem

### 3.3.1 Environment Variables dan Kontrak Identifier

Konfigurasi dipisahkan antara nilai yang boleh digunakan browser dan rahasia khusus server. Pemetaan pada [TABREF:konfigurasi_environment] mencegah service role key atau kredensial Umami masuk ke bundle frontend.

[TABLE-ID:konfigurasi_environment]
[TABLECAPTION:Pemisahan Environment Variables Berdasarkan Lingkungan]

[TABLE]
Lingkungan | Variabel Utama | Penggunaan
Browser React dan Vercel API read-only | `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` | Membuat Supabase client dengan hak yang dibatasi RLS
Helper Express | `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `PORT`, `FRONTEND_URL` | Koneksi server, pemilihan port, dan whitelist origin; service role tidak boleh dibundle ke browser
Umami opsional | `UMAMI_API_URL`, `UMAMI_WEBSITE_ID`, `UMAMI_API_USER`, `UMAMI_API_PASSWORD`, `UMAMI_APP_SECRET` | Autentikasi helper Express ke layanan Umami self-hosted
Vite dan hosting | `BASE_URL` serta path versi build | Resolusi aset statis, denah, dan loader Unity WebGL
[/TABLE]

Kontrak lintas repository yang paling sensitif adalah `unity_object_name`. Nilai ini disimpan pada data gedung atau fasilitas, dikirim melalui `/api/unity/data`, dan digunakan Search Overlay sebagai payload `NavigateTo`. Fasilitas yang tidak memiliki identifier sendiri dapat menggunakan target gedung induknya pada pencarian. Perubahan identifier harus dikoordinasikan dengan GameObject pada project Unity dan diverifikasi sebelum artefak WebGL baru dipublikasikan.

Versi folder build juga diperlakukan sebagai kontrak deployment. Pada source deployment yang ditinjau 21 Juli 2026, build aktif adalah v0.8.6.1 sehingga path pada loader React, preloader, dan `vercel.json` harus menunjuk ke folder versi yang sama.

### 3.3.2 Analitik dan Helper Express

Implementasi analitik berada dalam masa transisi dan didokumentasikan berdasarkan jalur yang benar-benar aktif. `trackingService` mencatat page view ke `web_analytics_log`, sedangkan service agregasi pada React membaca tabel yang sama untuk membentuk statistik. Dengan demikian, Public Dashboard dan Admin Panel dapat menampilkan analitik tanpa menjalankan Express atau Umami.

Express pada port 3001 tetap tersedia sebagai server opsional. Server ini menerapkan whitelist CORS dan rate limiter in-memory sebanyak 100 permintaan per alamat client per menit, serta menyediakan endpoint `/api/analytics/*` yang berkomunikasi dengan Umami API. Docker Compose menyalakan Umami dan database internalnya. Jalur tersebut dipertahankan sebagai alternatif self-hosted dan tidak disebut sebagai jalur wajib frontend saat ini.

Pemisahan ini juga memperjelas batas kontribusi DevOps. Penulis mengelola konfigurasi dan kesiapan operasional Express/Umami, tetapi data analitik yang tampil pada antarmuka aktif berasal dari Supabase. Pada pengembangan berikutnya, kedua jalur perlu disatukan agar definisi dan pengelolaan data analitik tidak berbeda.

### 3.3.3 Konfigurasi Hosting Vercel dan Aset WebGL

Artefak Unity WebGL v0.8.6.1 dibangun oleh Simulator dan Engine Developer lalu diserahkan kepada penulis untuk ditempatkan pada `public/unity-builds/v0.8.6.1/`. Vercel digunakan karena mendukung Vercel Serverless Functions, fallback routing SPA, serta header content type, Content-Encoding, dan cache yang diperlukan aset Unity. Potongan konfigurasi berikut menunjukkan pola header untuk build aktif:

```json
{
  "headers": [
    {
      "source": "/unity-builds/v0.8.6.1/Build/(.*)\\.wasm\\.unityweb",
      "headers": [
        { "key": "Content-Type", "value": "application/wasm" },
        { "key": "Content-Encoding", "value": "br" },
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
      ]
    },
    {
      "source": "/unity-builds/v0.8.6.1/Build/(.*)\\.data\\.unityweb",
      "headers": [
        { "key": "Content-Type", "value": "application/octet-stream" },
        { "key": "Content-Encoding", "value": "br" },
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
      ]
    }
  ]
}
```

GitHub Pages tetap dapat menyajikan build React, tetapi pilihan tur 3D dinonaktifkan pada domain `github.io` karena jalur tersebut tidak digunakan untuk konfigurasi header build WebGL. Denah 2D tetap tersedia sebagai fallback. Jika sistem dipindahkan ke infrastruktur kampus, server tujuan harus menyediakan padanan fallback SPA, endpoint API, HTTPS, header aset, cache, environment variables, dan pengelolaan secret sebelum domain dialihkan.

## 3.4 Laporan Implementasi Proyek

Subbab ini menyajikan **bukti dan hasil keluaran** dari implementasi yang metodenya telah diuraikan pada Subbab 3.2, mencakup logbook aktivitas serta hasil nyata pada sisi frontend, backend, integrasi sistem, dan DevOps.

### 3.4.1 Logbook Implementasi Proyek

Ringkasan aktivitas pada [TABREF:logbook_implementasi] disusun berdasarkan artefak yang dapat ditelusuri pada repository aplikasi, konfigurasi deployment, dan hasil pengujian. Kolom terakhir tidak menggunakan klaim persetujuan pemangku kepentingan yang tidak dilengkapi bukti formal.

[TABLE-ID:logbook_implementasi]
[TABLECAPTION:Logbook Implementasi Proyek]

[TABLE]
Rentang Kegiatan | Aktivitas | Kontribusi Penulis | Bukti atau Artefak
Tahap kebutuhan dan desain | Analisis pengguna, arsitektur, IA, UML, dan antarmuka | Merumuskan kebutuhan aplikasi, API, bridge, deployment, serta mockup Public Dashboard dan Admin Panel | Draf kebutuhan, diagram arsitektur, diagram alur, dan rancangan UI
Tahap backend dan data aplikasi | Implementasi Vercel Functions, Auth adapter, service data, dan CRUD | Membuat endpoint read-only, mengintegrasikan Supabase Auth/SDK, serta menangani respons dan cache aplikasi | Folder `api/`, adapter Auth, service Supabase, dan kontrak endpoint
Tahap frontend | Implementasi React SPA, denah 2D, pemuat Unity, pencarian, dan Admin Panel | Membuat route, provider, komponen UI, A* frontend, loader native Unity, dan editor konfigurasi map | Komponen React, utility preload, service map, dan empat bukti UI terpilih
Tahap integrasi dan DevOps | Sinkronisasi kontrak data dan publikasi build | Menghubungkan `buildingId`/`unity_object_name`, memasang artefak v0.8.6.1, serta mengatur environment, header, cache, dan health handler | `vercel.json`, folder build versi, handler API, dan hasil Network browser
Tahap evaluasi | Pengujian web, Black Box, Lighthouse, dan UAT | Menjalankan atau mengompilasi bukti pengujian sesuai batas kontribusi serta mencatat keterbatasan hasil | Handoff verifikasi web, dokumen Black Box, laporan Lighthouse, dan berkas UAT
[/TABLE]

### 3.4.2 Hasil dan Bukti Implementasi Back-end

Backend API diimplementasikan pada Vercel Serverless Functions. Struktur respons `/api/unity/data` yang dibentuk handler dan dikonsumsi `BuildingDatabase` adalah sebagai berikut. Nilai record disamarkan karena bagian ini menjelaskan kontrak, bukan menyalin data produksi.

```json
{
  "gedung": [
    {
      "id": "<number>",
      "nama_gedung": "<string>",
      "deskripsi_gedung": "<string>",
      "lokasi": "<string>",
      "jumlah_lantai": "<number>",
      "unity_object_name": "<canonical_name>"
    }
  ],
  "fasilitas": [
    {
      "id": "<number>",
      "nama_fasilitas": "<string>",
      "deskripsi_fasilitas": "<string>",
      "tipe_fasilitas": "<string>",
      "lantai": "<number>",
      "id_gedung": "<number>",
      "foto_url": "<url_or_empty>",
      "unity_object_name": "<canonical_name_or_empty>"
    }
  ]
}
```

Respons aktual deployment pada [FIGREF:api_test_unity_data] menunjukkan bahwa request `GET /api/unity/data` memperoleh status `200 OK` dan mengembalikan objek JSON dengan array `gedung`. Record yang terlihat memuat `id`, `nama_gedung`, `deskripsi_gedung`, `lokasi`, `jumlah_lantai`, dan `unity_object_name`, sehingga bentuk respons aktual konsisten dengan kontrak yang digunakan runtime Unity. Waktu 2,86 detik dan ukuran 12,24 kB merupakan hasil satu request manual, bukan tolok ukur performa untuk seluruh kondisi jaringan.

[FIGURE:api_test_unity_data]
[FIGCAPTION:Respons Data Runtime Unity dari Vercel Serverless Function]

### 3.4.3 Hasil dan Bukti Implementasi Front-end

Frontend React SPA berhasil dibangun dan diperiksa pada 21 Juli 2026. Empat bukti antarmuka inti pada Subbab 2.3.6 diambil ulang dari aplikasi setelah revisi agar tidak mencampurkan tampilan lama dengan implementasi aktif. Gambar dipilih secara selektif agar pembahasan tetap berfokus pada fitur utama.

1. Public Dashboard menyediakan informasi kampus, tutorial/FAQ, pemilih denah 2D atau 3D, serta pencarian bersama. Mode 2D menghitung rute A* di frontend, sedangkan mode 3D mengirim `unity_object_name` kepada Unity.
2. Loader React menampilkan progres dan fallback, membatasi device pixel ratio, meneruskan tipe perangkat melalui `SetDevice`, serta menghentikan instance ketika komponen dilepas.
3. Admin Panel menyediakan halaman terlindungi untuk CRUD gedung, fasilitas, program studi, dan konfigurasi denah 2D, serta tab analitik dan audit.
4. Implementasi tidak menggunakan `react-unity-webgl`; integrasi dilakukan melalui loader native dan `window.unityInstance` sesuai build aktif v0.8.6.1.
5. Tangkapan layar Admin Panel mencatat 331 fasilitas pada database Supabase aktif, sedangkan pembersihan berkas seed menghasilkan 311 data. Perbedaan tersebut menunjukkan bahwa seed final belum terbukti telah diterapkan kembali ke database aktif. Oleh karena itu, tangkapan layar pencarian tidak digunakan untuk menyatakan bahwa penambahan kata pencarian pada R01 sudah tersedia di deployment.

### 3.4.4 Hasil dan Bukti Deployment dan Operasional Layanan

Layanan web menggunakan Vercel untuk React SPA, artefak Unity WebGL, dan Vercel Serverless Functions. Konfigurasi pada Subbab 3.3.3 menunjukkan pemetaan content type, Brotli, cache immutable, header keamanan, dan fallback SPA. Handler `/api/health` tersedia untuk pemeriksaan layanan, sedangkan Express/Umami tetap merupakan jalur opsional.

Pemeriksaan operasional pada [FIGREF:api_test_health] menunjukkan bahwa `GET /api/health` memperoleh status `200 OK` dan mengembalikan `success: true`, status `OK`, pesan `Server is running`, serta waktu respons. Bukti tersebut merupakan pemeriksaan manual pada lingkungan yang dipilih melalui aplikasi penguji API dan tidak diperlakukan sebagai pemantauan ketersediaan berkelanjutan.

[FIGURE:api_test_health]
[FIGCAPTION:Respons Health Check pada Deployment]

Pemeriksaan jaringan browser terhadap tiga aset utama build v0.8.0 menunjukkan bahwa seluruh permintaan memperoleh status 200. Hasil satu kali pengamatan tersebut ditranskripsikan pada [TABREF:webgl_network_loading] dan tidak digunakan sebagai tolok ukur untuk semua perangkat atau kondisi jaringan. Pengamatan dilakukan sebelum artefak diperbarui ke v0.8.6.1 sehingga ukuran dan waktu pada tabel tidak diterapkan pada build terbaru.

[TABLE-ID:webgl_network_loading]
[TABLECAPTION:Observasi Pemuatan Aset Utama Unity WebGL v0.8.0]

[TABLE]
Aset | Status | Ukuran Transfer yang Ditampilkan | Waktu yang Ditampilkan
`v0.8.0.framework.js.unityweb` | 200 | 72,5 kB | 351 ms
`v0.8.0.wasm.unityweb` | 200 | 6.528 kB | 1,95 detik
`v0.8.0.data.unityweb` | 200 | 76.864 kB | 15,92 detik
[/TABLE]

Data tersebut menunjukkan bahwa berkas data merupakan komponen transfer terbesar pada pengamatan yang dilakukan. Karena hasil hanya berasal dari satu kondisi browser, evaluasi performa perlu membedakan ukuran transfer, waktu unduh, dekompresi, inisialisasi Unity, dan kondisi cache. Apabila sistem dipindahkan ke infrastruktur UPNVJ, penyesuaian dapat dipusatkan pada domain, nilai rahasia, konektivitas layanan, header aset, dan kebijakan identitas tanpa mengubah kontrak REST API atau komunikasi React–Unity.

## 3.5 Hasil Pengujian Proyek

### 3.5.1 Pengujian Web dan API

Pemeriksaan teknis pada 21 Juli 2026 menunjukkan bahwa ESLint, pengujian unit dan komponen, serta build produksi aplikasi web berhasil dijalankan. Hasilnya dirangkum pada [TABREF:hasil_pengujian_web].

[TABLE-ID:hasil_pengujian_web]
[TABLECAPTION:Hasil Verifikasi Repository Aplikasi Web]

[TABLE]
Pemeriksaan | Hasil Terverifikasi | Batas Interpretasi
ESLint | Lulus | Tidak ditemukan kesalahan berdasarkan aturan pemeriksaan kode yang digunakan
Vitest dan React Testing Library | 13 file pengujian dan 129 pengujian lulus | Mencakup utility, adapter Auth, modal, translasi, perlindungan data, komponen, serta 11 pengujian validasi `OnNavigationCompleted`; bukan pengujian internal Unity runtime
Build produksi | `tsc -b` dan Vite build lulus | Pemeriksaan tipe dan penyusunan berkas aplikasi berhasil; peringatan data browser tidak termasuk kesalahan proyek
Playwright | Belum tersedia sebagai suite hasil | Alur browser masih dibuktikan melalui Black Box dan UAT; tidak ada angka E2E yang diklaim
[/TABLE]

Selain pengujian otomatis, empat pemeriksaan manual dijalankan melalui aplikasi penguji API terhadap deployment dan Supabase. Hasilnya dirangkum pada [TABREF:hasil_pengujian_api_deployment]. Status lulus ditentukan berdasarkan kesesuaian hasil aktual dengan hasil yang diharapkan. Oleh karena itu, respons `401 Unauthorized` ketika perubahan data dilakukan tanpa autentikasi menunjukkan bahwa kontrol akses bekerja, bukan bahwa endpoint gagal.

[TABLE-ID:hasil_pengujian_api_deployment]
[TABLECAPTION:Hasil Pengujian Manual API dan Integrasi Supabase]

[TABLE]
Skenario | Hasil yang Diharapkan | Hasil Aktual | Status
`GET /api/health` | HTTP 200 dan status layanan dapat dibaca | HTTP 200; `success: true`, status `OK`, pesan layanan, dan timestamp tersedia | Lulus
`GET /api/unity/data` | HTTP 200 dengan objek `gedung` dan `fasilitas` sesuai kontrak runtime | HTTP 200; respons JSON memuat data gedung beserta `unity_object_name` dan struktur kontrak runtime | Lulus
`GET /api/unity/names` | HTTP 200 dengan daftar `unityObjectNames` untuk Unity Editor | HTTP 200; daftar kode objek Unity diterima | Lulus
`POST /rest/v1/fasilitas` tanpa autentikasi | Mutasi ditolak oleh kebijakan akses data | HTTP 401; kode PostgreSQL `42501` menyatakan row melanggar row-level security policy | Lulus
[/TABLE]

Respons pada [FIGREF:api_test_unity_names] menunjukkan bahwa `GET /api/unity/names` memperoleh status `200 OK` dan mengembalikan daftar `unityObjectNames`. Endpoint tersebut digunakan oleh alat bantu Unity Editor untuk memeriksa kode objek, sedangkan aplikasi Unity saat dijalankan tetap menggunakan `/api/unity/data`.

[FIGURE:api_test_unity_names]
[FIGCAPTION:Respons Daftar Identifier untuk Tooling Unity Editor]

Skenario negatif pada [FIGREF:api_test_rls_unauthorized] mengirim data uji ke REST API Supabase tanpa kredensial yang memenuhi policy. Respons `401 Unauthorized` dengan kode `42501` membuktikan bahwa mutasi tersebut ditolak oleh RLS. Penulis menggunakan hasil ini untuk memverifikasi bahwa integrasi web tunduk pada kontrol akses yang tersedia; rancangan policy RLS tetap merupakan kontribusi Database Schema Designer.

[FIGURE:api_test_rls_unauthorized]
[FIGCAPTION:Penolakan Mutasi Tanpa Otorisasi oleh Supabase RLS]

Keempat pemeriksaan tersebut merupakan pemeriksaan dasar secara manual dan belum menggantikan pengujian deployment otomatis. Playwright belum digunakan untuk menguji autentikasi, CRUD terotorisasi, header produksi, dan integrasi Unity dari awal sampai akhir. Keterbatasan ini dipisahkan dari hasil 129 pengujian otomatis agar cakupan pengujian tidak dilebihkan.

### 3.5.2 Black Box Testing

<!-- PIPELINE:INCLUDE content/shared/testing/blackbox.md -->

Pengujian ulang BB-20 didokumentasikan melalui dua tangkapan layar berurutan karena perubahan terjadi ketika pengguna mendekati tujuan. Kondisi sebelum pengguna tiba terlihat pada [FIGREF:blackbox_bb20_rute_aktif], yang memperlihatkan garis rute masih aktif, jarak tersisa 16 meter, dan label Gedung Dewi Sartika, bukan kode internal `unity_object_name`.

[FIGURE:blackbox_bb20_rute_aktif]
[FIGCAPTION:Pengujian Ulang BB-20 Saat Navigasi Masih Aktif]

Kondisi setelah pengguna mencapai tujuan terlihat pada [FIGREF:blackbox_bb20_navigasi_selesai], yang memperlihatkan bahwa garis rute telah hilang dan notifikasi kedatangan menampilkan nama tujuan yang sama. Kedua tangkapan layar tersebut menjadi bukti visual pengujian ulang BB-20 sehingga status akhirnya dinyatakan lulus.

[FIGURE:blackbox_bb20_navigasi_selesai]
[FIGCAPTION:Pengujian Ulang BB-20 Setelah Navigasi Selesai]

### 3.5.3 Lighthouse Testing

Audit Lighthouse dijalankan pada 21 Juli 2026 sekitar pukul 08.15 WIB terhadap hasil build produksi melalui server pratinjau Vite pada `http://127.0.0.1:4173/`. Perintah `npm run lighthouse` membangun aplikasi, menjalankan server pratinjau, serta menghasilkan laporan untuk perangkat mobile dan desktop. Pengujian menggunakan Lighthouse 12.8.2, HeadlessChrome 150, simulasi pembatasan jaringan dan CPU, serta pembersihan data browser terpilih. Skor dari artefak JSON dirangkum pada [TABREF:performa_lighthouse].

[TABLE-ID:performa_lighthouse]
[TABLECAPTION:Hasil Audit Lighthouse Mobile dan Desktop]

[TABLE]
Mode | Performance | Accessibility | Best Practices | SEO
Mobile | 86/100 | 100/100 | 100/100 | 100/100
Desktop | 99/100 | 100/100 | 100/100 | 100/100
[/TABLE]

Metrik utama yang membentuk skor tersebut disajikan pada [TABREF:metrik_lighthouse]. Nilai dibulatkan untuk keterbacaan, sedangkan data mentah tetap tersedia pada `reports/lighthouse/latest-mobile.json` dan `reports/lighthouse/latest-desktop.json`.

[TABLE-ID:metrik_lighthouse]
[TABLECAPTION:Metrik Utama Lighthouse Mobile dan Desktop]

[TABLE]
Metrik | Mobile | Desktop | Interpretasi
First Contentful Paint | 2.444 ms | 541 ms | FCP mobile masih menjadi area optimasi
Largest Contentful Paint | 3.681 ms | 775 ms | LCP mobile merupakan hambatan utama; desktop sangat baik
Speed Index | 2.444 ms | 589 ms | Kecepatan tampilan desktop sangat baik dan mobile masih dapat ditingkatkan
Total Blocking Time | 89 ms | 6 ms | Keduanya berada di bawah 200 ms
Cumulative Layout Shift | 0 | 0 | Tidak terdeteksi pergeseran tata letak pada audit
Time to Interactive | 3.913 ms | 781 ms | Interaktivitas mobile masih dapat dipercepat
Total Byte Weight | 419.577 byte | 566.763 byte | Desktop lebih besar karena memakai aset hero desktop
[/TABLE]

Elemen LCP pada kedua mode adalah gambar hero pertama dengan teks alternatif "UPNVJ Campus 1". Pada mobile, berkas `hero1-mobile.webp` berukuran sekitar 32,2 KiB dan telah diminta sejak awal dengan prioritas tinggi. Hasil audit menunjukkan bahwa sekitar 88 persen waktu LCP terjadi setelah berkas tersedia, ketika browser menunggu gambar ditampilkan. Oleh karena itu, optimasi berikutnya lebih diarahkan pada proses tampilan, sekitar 75 KiB JavaScript yang tidak terpakai, kompresi dan ukuran responsif gambar hero, serta satu stylesheet sekitar 16 KiB yang masih menghambat tampilan awal.

Hasil tersebut berasal dari pengujian lokal dengan kondisi yang disimulasikan, bukan dari data penggunaan nyata. Seluruh 19 pemeriksaan otomatis Accessibility yang berlaku dinyatakan lulus, tetapi 10 pemeriksaan manual masih perlu dilakukan. Sembilan pemeriksaan otomatis SEO juga lulus dengan satu pemeriksaan manual tersisa, sedangkan kategori PWA tidak diuji. Audit halaman awal ini tidak mengukur seluruh proses pemuatan Unity WebGL setelah pengguna memilih Denah 3D.

### 3.5.4 User Acceptance Test (UAT)

<!-- PIPELINE:INCLUDE content/shared/testing/uat.md -->

### 3.5.5 Tindak Lanjut Hasil User Acceptance Test (UAT)

<!-- PIPELINE:INCLUDE content/shared/testing/uat-revisions.md -->

### 3.5.6 Dokumentasi Implementasi Revisi UAT

Dokumentasi pada subbab ini menjelaskan realisasi tindak lanjut UAT berdasarkan batas kontribusi penulis sebagai Full Stack Web Developer, System Integrator, dan DevOps Engineer. Pemeriksaan dilakukan melalui kode sumber, hasil pengujian otomatis, sumber resmi, serta tangkapan layar aplikasi pada 21 Juli 2026. Tangkapan layar tersebut digunakan untuk memeriksa hasil setelah perbaikan dan tidak diperlakukan sebagai kuesioner UAT kedua.

1. Perbaikan Data dan Pencarian
   Tindak lanjut UAT-R01 dilakukan dalam dua tahap. Tahap pertama menstandarkan 119 nama fasilitas dan memperbaiki deskripsi pada 189 data dengan menambahkan istilah umum, kepanjangan unit, serta kata pencarian seperti Korprodi/Koorprodi, Kaprodi, Kajur, Wadek, Warek, Kalab, dan TU. Tahap kedua menghapus 27 data yang belum memiliki `unity_object_name` valid dari 339 data awal. Pemeriksaan berikutnya juga menyelesaikan satu data duplikat sehingga berkas seed akhir memuat 311 fasilitas dengan kode objek yang unik dan tidak kosong.

   Fitur pencarian React memeriksa nama fasilitas, deskripsi fasilitas, nama gedung, deskripsi gedung, dan lokasi. Dengan cara ini, pengguna dapat menemukan fasilitas melalui istilah yang lebih familiar tanpa mengubah nama resmi atau kode objek untuk Unity. Tindak lanjut UAT-R09 menggunakan pemeriksaan struktural yang sama untuk menilai kelengkapan nama, deskripsi, hubungan dengan gedung, dan kode objek. Hasil pemeriksaan masih terbatas pada berkas seed; laporan tidak menyatakan bahwa data tersebut telah diterapkan kembali ke database Supabase aktif atau dicocokkan ulang dengan seluruh objek di Unity.

2. Onboarding dan Pilihan Pengalaman Navigasi
   Tindak lanjut UAT-R02 diwujudkan melalui bagian Tutorial dan FAQ yang membedakan panduan Denah 2D dan Denah 3D pada perangkat desktop maupun mobile. Pengguna juga dapat mengganti pilihan perangkat secara manual. Tutorial 2D menjelaskan cara menentukan lokasi awal, mencari tujuan, membaca garis rute, dan mengganti titik awal. Tutorial 3D menjelaskan proses pemuatan, kontrol gerak, kamera, dan pencarian. Setelah memilih titik awal di Denah 3D, pengguna memperoleh tutorial interaktif untuk berlatih bergerak, mengarahkan kamera, berlari, melompat, dan mencari lokasi. Tampilan pada [FIGREF:uat_revisi_tutorial_faq] memperlihatkan panduan langkah dan FAQ dalam satu bagian agar bantuan tersedia sebelum pengguna membuka denah.

[FIGURE:uat_revisi_tutorial_faq]
[FIGCAPTION:Tutorial dan FAQ Denah Kampus Setelah Revisi]

   Tindak lanjut UAT-R03 dan UAT-R05 tidak meminta pengguna membuat profil khusus. Sebagai gantinya, sistem menyesuaikan pengalaman melalui pilihan bahasa, perangkat, mode denah, tutorial, pencarian tujuan, dan lokasi awal. Pemilih pada [FIGREF:uat_revisi_mode_selector] memberi pengguna opsi Denah 2D untuk navigasi yang lebih sederhana atau Denah 3D untuk menjelajahi lingkungan kampus. Dengan pilihan ini, pengguna yang tidak terbiasa dengan kontrol permainan tetap dapat memakai Denah 2D tanpa harus memuat simulasi 3D.

[FIGURE:uat_revisi_mode_selector]
[FIGCAPTION:Pemilihan Mode Denah 2D atau 3D]

   Pada mode 2D, pengguna memilih gedung awal lalu mencari gedung atau fasilitas tujuan. Frontend kemudian menghitung rute A* melalui jaringan jalur dan pintu masuk gedung yang telah dikonfigurasi. Fasilitas diarahkan ke pintu masuk gedung induknya karena Denah 2D belum menampilkan rute di dalam ruangan; batasan ini juga dijelaskan pada FAQ. Verifikasi visual pada [FIGREF:uat_revisi_map_2d] menunjukkan nama lokasi, penanda titik awal, kolom pencarian, dan tombol untuk mengganti titik awal dalam satu tampilan.

[FIGURE:uat_revisi_map_2d]
[FIGCAPTION:Denah 2D dengan Titik Awal dan Label Lokasi]

   Tindak lanjut UAT-R07 menyediakan pemilihan titik awal pada kedua mode. Pada Denah 2D, pengguna memilih gedung tempat perjalanan dimulai. Pada Denah 3D, pengguna dapat memilih satu dari 16 titik awal yang telah disiapkan. Unity memeriksa agar titik yang dipilih berada pada area yang dapat dilalui sebelum memindahkan posisi pengguna. Tampilan pada [FIGREF:uat_revisi_spawn_3d] memperlihatkan lokasi penting kampus yang dapat dipilih sebelum pengalaman 3D dimulai.

[FIGURE:uat_revisi_spawn_3d]
[FIGCAPTION:Pemilihan Titik Awal pada Denah 3D]

3. Bantuan dan Integrasi Denah 3D
   Tindak lanjut UAT-R04 menambahkan label tujuan yang menampilkan nama lokasi dan jarak selama navigasi. Beberapa gedung dan area di dalam Denah 3D juga dilengkapi objek tulisan. Laporan ini tidak menyatakan bahwa seluruh 311 fasilitas sudah memiliki label tetap. UAT-R06 menambahkan minimap yang menunjukkan posisi, arah pengguna, dan tujuan aktif. Bukti pada [FIGREF:uat_revisi_minimap_3d] memperlihatkan bahwa minimap, kolom pencarian, tombol pergantian mode, dan tombol bantuan tersedia pada tampilan 3D.

[FIGURE:uat_revisi_minimap_3d]
[FIGCAPTION:Tampilan Denah 3D dengan Minimap dan Tombol Bantuan]

   Tindak lanjut UAT-R08 menambahkan tombol bantuan yang berisi petunjuk pencarian, pembatalan navigasi, pergantian mode, dan langkah yang dapat dilakukan apabila denah gagal dimuat. Jendela bantuan juga menampilkan nomor layanan kampus, yaitu 021-7699431 dan 021-7656971. Nomor tersebut diambil dari [halaman Hubungi Kami pada situs Penmaru UPNVJ](https://penmaru.upnvj.ac.id/id/contact.html) sehingga pengguna diarahkan ke kontak resmi kampus.

   Tindak lanjut UAT-R10 menambahkan notifikasi ketika pengguna telah mencapai tujuan. Setelah pengguna memilih lokasi, React mengirim kode lokasi (`unity_object_name`) kepada Unity untuk memulai navigasi. Ketika pengguna benar-benar tiba, Unity mengirim pemberitahuan kembali kepada React. React kemudian memeriksa apakah lokasi yang dilaporkan Unity sama dengan tujuan yang dipilih. Jika sama, sistem menampilkan notifikasi "Tiba di Tujuan". Notifikasi tidak ditampilkan apabila navigasi dibatalkan atau data yang diterima tidak sesuai.

   Hasil penerapan fitur tersebut terlihat pada [FIGREF:uat_revisi_notifikasi_tiba], yang menunjukkan notifikasi "Tiba di Tujuan" dengan nama Gedung Dewi Sartika setelah navigasi selesai. Perilaku ini juga diperiksa melalui sebelas pengujian otomatis untuk memastikan notifikasi hanya muncul pada kondisi kedatangan yang benar.

[FIGURE:uat_revisi_notifikasi_tiba]
[FIGCAPTION:Notifikasi Tiba di Tujuan Setelah Navigasi Selesai]

   Kesepuluh tindak lanjut tersebut menunjukkan bahwa masukan UAT telah diterjemahkan menjadi perbaikan data, panduan penggunaan, pilihan mode, navigasi, bantuan, dan integrasi antarkomponen. Nilai UAT awal tetap dipertahankan sebagai hasil pengujian tertutup. Pemeriksaan visual dan teknis setelah perbaikan tidak dihitung sebagai pengulangan kuesioner terhadap lima peserta UAT.

---

# BAB IV PENUTUP

## 4.1 Kesimpulan

Berdasarkan hasil pengembangan, implementasi, dan pengujian sistem integrasi denah virtual kampus dan dashboard profil UPNVJ Kampus Pondok Labu, dapat ditarik beberapa kesimpulan sebagai berikut:

1. Penulis berhasil mengembangkan Public Dashboard dan Admin Panel berbasis React yang menyediakan informasi kampus, tutorial dan bantuan, pencarian, denah 2D, serta pemuatan denah 3D Unity WebGL. REST API baca-saja pada Vercel Serverless Functions menyediakan kontrak data bagi runtime Unity dan konsumen eksternal.
2. Aplikasi web berhasil diintegrasikan langsung dengan Supabase Auth dan Supabase SDK untuk mengelola sesi, mengambil data, dan menjalankan operasi CRUD sesuai RLS rancangan Database Schema Designer. Layanan aplikasi juga mencatat riwayat operasi CRUD agar perubahan dapat ditinjau melalui Admin Panel.
3. Integrasi React dan Unity berhasil menghubungkan pencarian lokasi dengan navigasi 3D. React mengirim tujuan yang dipilih pengguna kepada Unity, sedangkan Unity mengirim pemberitahuan setelah pengguna tiba. React memeriksa kesesuaian tujuan sebelum menampilkan notifikasi, sehingga pembatalan navigasi atau data yang tidak valid tidak dianggap sebagai kondisi tiba.
4. React SPA, Vercel Serverless Functions, dan artefak Unity WebGL v0.8.6.1 berhasil dipublikasikan melalui Vercel. Konfigurasi mencakup variabel lingkungan, header dan cache aset, endpoint pemeriksaan layanan, serta pencatatan analitik melalui Supabase. Express dan Umami tetap tersedia sebagai pilihan operasional. Konfigurasi hosting dapat disesuaikan apabila integrasi dengan infrastruktur kampus dilakukan pada tahap lanjutan.
5. Pengujian aplikasi web mencatat 129 pengujian lulus pada 13 berkas, termasuk 11 pengujian untuk notifikasi kedatangan. Pemeriksaan ESLint, TypeScript, dan build produksi juga berhasil. Empat pemeriksaan manual API menunjukkan bahwa endpoint pemeriksaan layanan, data Unity, dan daftar kode objek dapat diakses, sedangkan perubahan data tanpa otorisasi ditolak. Audit Lighthouse pada 21 Juli 2026 menghasilkan skor Performance 86 pada mobile dan 99 pada desktop. Accessibility, Best Practices, dan SEO memperoleh skor 100 pada kedua mode. Hasil Lighthouse merupakan pengujian laboratorium lokal; waktu tampil konten utama pada mobile masih menjadi fokus optimasi berikutnya.
6. Pada pengujian Black Box awal, 23 dari 24 skenario lulus atau setara dengan 95,83 persen. Setelah BB-20 diperbaiki dan diuji ulang, label tujuan menggunakan nama yang mudah dibaca, garis rute tetap tampil sebelum pengguna tiba, lalu menghilang ketika notifikasi kedatangan muncul. Hasil akhir menjadi 24 dari 24 skenario lulus. UAT tertutup menghasilkan nilai 77,78 persen untuk Dashboard Publik, 84,55 persen untuk Dashboard Admin, dan 81,50 persen dari seluruh jawaban. UAT diikuti lima peserta, yaitu dua dosen penguji, dua dosen pembimbing, dan satu perwakilan Humas. Tindak lanjut UAT-R01 sampai UAT-R10 telah diterapkan dan diperiksa melalui kode sumber, pengujian otomatis, sumber resmi, dan tangkapan layar aplikasi. Pemeriksaan setelah perbaikan tersebut bukan pengulangan kuesioner UAT dan tidak melibatkan sampel pengguna publik baru.

## 4.2 Saran

Beberapa saran yang direkomendasikan untuk pengembangan sistem lebih lanjut di masa mendatang adalah:

1. Menyiapkan adapter identitas, domain, secret management, dan API institusional apabila sistem memperoleh persetujuan untuk diintegrasikan dengan infrastruktur kampus. Integrasi tersebut perlu dilakukan melalui kontrak resmi tanpa menanamkan ketergantungan pada satu platform hosting.
2. Meningkatkan skor Performance mobile hingga sekurang-kurangnya 90 tanpa menurunkan skor Accessibility, Best Practices, dan SEO. Prioritas optimasi mencakup pengurangan waktu tunda tampilan gambar hero, sekitar 75 KiB JavaScript yang tidak terpakai, penyediaan ukuran gambar yang lebih sesuai dengan perangkat, dan pengurangan stylesheet yang menghambat tampilan awal. Setiap perubahan perlu diperiksa kembali melalui audit mobile dan desktop dengan konfigurasi yang sama.
3. Menambahkan rangkaian pengujian browser dan WebGL dari awal sampai akhir untuk login, akses halaman admin, CRUD, pemilih denah, pencarian 2D/3D, pemuatan WebGL, notifikasi kedatangan, dan endpoint pada deployment. Pengujian pengguna berikutnya juga perlu melibatkan mahasiswa baru, orang tua atau wali, dan pengunjung eksternal agar kemudahan penggunaan dapat dinilai langsung pada kelompok pengguna yang dituju.
4. Menetapkan satu jalur analitik utama antara Supabase dan Umami agar definisi metrik, retensi data, privasi, serta operasional layanan tidak mengalami drift.
5. Berkoordinasi dengan Database Schema Designer untuk menerapkan otorisasi admin yang lebih granular dan memastikan pencatatan audit tetap berlaku pada mutasi yang tidak berasal dari frontend.

---

# DAFTAR PUSTAKA

Aliyah, A., Hartono, N., dan Muin, A. A. (2025). Penggunaan User Acceptance Testing (UAT) pada pengujian sistem informasi pengelolaan keuangan dan inventaris barang. *Switch: Jurnal Sains dan Teknologi Informasi*, 3(2), 42–58. https://doi.org/10.62951/switch.v3i1.330

Jamaludin, J., dan Saepuloh, L. (2024). Tren riset twin digital smart campus. *Sang Pencerah: Jurnal Ilmiah Universitas Muhammadiyah Buton*, 10(2), 408–425. https://doi.org/10.35326/pencerah.v10i2.5317

Kurniawan, T. A. (2018). Pemodelan Use Case (UML): Evaluasi terhadap beberapa kesalahan dalam praktik. *Jurnal Teknologi Informasi dan Ilmu Komputer (JTIIK)*, 5(1), 77–86. https://doi.org/10.25126/jtiik.201851610

Maulida, M., Zahro, F., Hakim, R., dan Akbar, M. S. (2025). Pengujian black box testing pada sistem website pemesanan online Toko Ayam Krispy. *Jurnal Media Akademik (JMA)*, 3(5). https://doi.org/10.62281/v3i5.1908

Muharam, Y., Anggara, M. B., dan Hanafi, T. J. (2023). Implementasi peta 3 dimensi menggunakan metode IMSDD (Interactive Multimedia System Design and Development) dan WebGL API berbasis web (Studi kasus di SMP Karya Pembangunan 2 Majalaya). *Jurnal Informatika-COMPUTING*, 10, 20–30. https://doi.org/10.55222/computing.v10i01.1155

Pricillia, T., dan Zulfachmi (2021). Perbandingan metode pengembangan perangkat lunak (Waterfall, Prototype, RAD). *Jurnal Bangkit Indonesia*, 10(1), 6–12. https://doi.org/10.52771/bangkitindonesia.v10i1.153

Putra, I. G. W. W., Dharma, E. M., dan Permana, P. T. H. (2026). Implementasi relational database dengan Row-Level Security (RLS) pada sistem inventory menggunakan Supabase dan React Native Expo (Studi kasus Bengkel Sari Merta). *JATI (Jurnal Mahasiswa Teknik Informatika)*, 10(2), 2443–2448. https://doi.org/10.36040/jati.v10i2.17551

Syarif, S., dan Risdiansyah, D. (2024). Pemanfaatan metode prototype dalam perancangan sistem informasi penjualan berbasis website. *Jurnal Ekonomi Manajemen dan Bisnis (JEMB)*, 2(1), 12–25. https://doi.org/10.54895/jemb.v2i1.2312

Taurusta, C., Asiddiq, A. M., Suprianto, S., dan Setiawan, H. (2024). Visualisasi gedung kampus 1 Universitas Muhammadiyah Sidoarjo menggunakan augmented reality sebagai media informasi. *Journal of Technology and System Information*, 1(1), 55–70. https://doi.org/10.47134/jtsi.v1i1.2146

UPNVJ. (2022). Lokasi kampus. https://www.upnvj.ac.id/id/tentang-upn/lokasi-kampus.html

UPNVJ. (2025a). Kantin. https://www.upnvj.ac.id/id/fasilitas-layanan/kantin.html

UPNVJ. (2025b). Sejarah. https://www.upnvj.ac.id/id/tentang-upn/sejarah.html

UPNVJ. (2026). Rapat koordinasi Humas UPNVJ 2026: Fokus strategi komunikasi digital dan media sosial perguruan tinggi. https://www.upnvj.ac.id/id/berita/2026/02/rapat-koordinasi-humas-upnvj-2026-fokus-strategi-komunikasi-digital-dan-media-sosial-perguruan-tinggi.html

---

# LAMPIRAN 1. Surat Pernyataan Keaslian

Yang bertanda tangan di bawah ini:

Nama : Muhammad Iman Nugraha
NIM : 2210511129
Program Studi : Informatika
Fakultas : Ilmu Komputer
Universitas : Universitas Pembangunan Nasional Veteran Jakarta

Menyatakan dengan sesungguhnya bahwa laporan Tugas Akhir Proyek yang berjudul "Pengembangan Dashboard Web, Integrasi Unity WebGL, dan Deployment Sistem Denah Virtual UPNVJ Kampus Pondok Labu" adalah benar-benar hasil karya saya sendiri, bebas dari plagiat, dan tidak memuat bagian karya ilmiah orang lain kecuali yang secara formal disitasi dan dicantumkan dalam daftar pustaka sesuai dengan ketentuan akademik yang berlaku.

Apabila di kemudian hari terbukti terdapat plagiarisme, manipulasi data, atau pelanggaran etika akademik lainnya dalam laporan ini, saya bersedia menerima sanksi sesuai ketentuan akademik yang berlaku di Universitas Pembangunan Nasional Veteran Jakarta.

Jakarta, ____ __________ 20__
Yang menyatakan,

(Meterai Rp10.000)

Muhammad Iman Nugraha
NIM 2210511129

---

# LAMPIRAN 2. Dokumentasi Penyerahan Pakta Integritas kepada UPA TIK

Salinan pakta integritas yang telah diserahkan tidak berada dalam arsip penulis. Bukti yang tersedia berupa foto dokumentasi penyerahan dokumen kepada staf UPA TIK; lampiran ini tidak dimaksudkan sebagai pengganti scan dokumen bertanda tangan atau surat keterangan resmi dari institusi.

Proses penyerahan yang terekam pada [FIGREF:foto_penyerahan_pakta_upa_tik] menunjukkan tim membawa dokumen pakta integritas dalam kegiatan koordinasi dengan UPA TIK. Caption dan narasi tidak menetapkan identitas staf, nomor surat, tanggal pengesahan, atau status persetujuan yang tidak dapat diverifikasi dari artefak.

[FIGURE:foto_penyerahan_pakta_upa_tik]
[FIGCAPTION:Dokumentasi Penyerahan Pakta Integritas kepada UPA TIK]

---

# LAMPIRAN 3. Kode Sumber Utama

Lampiran ini hanya memuat cuplikan yang berada dalam batas kontribusi Full Stack Web Developer, System Integrator, dan DevOps Engineer. Kode internal Unity, termasuk `DatabaseSyncChecker`, tidak dicantumkan karena dikembangkan oleh Engine Developer. Cuplikan dipilih untuk membuktikan autentikasi, CRUD, integrasi React–Unity, REST API, analitik, dan deployment tanpa memuat repository secara penuh atau menampilkan kredensial.

Pemetaan pada [TABREF:lampiran_artefak_kode] menunjukkan delapan kelompok artefak yang menjadi dasar pemilihan cuplikan kode.

[TABLE-ID:lampiran_artefak_kode]
[TABLECAPTION:Pemetaan Cuplikan Kode terhadap Kontribusi Penulis]

[TABLE]
No. | Artefak | Lokasi Sumber | Kontribusi yang Dibuktikan
1 | Supabase Auth dan perlindungan halaman admin | `src/lib/supabase.ts`, `src/contexts/AuthContext.tsx`, `src/components/common/ProtectedRoute.tsx` | Sesi browser, autentikasi, dan pembatasan akses Admin Panel
2 | CRUD Admin Panel | `src/services/api/supabaseDataService.ts` | Validasi input, operasi data melalui Supabase SDK, cache, dan audit aplikasi
3 | Preload adaptif | `src/utils/unityPreloader.ts` | Penghematan bandwidth sebelum pengguna memilih mode 3D
4 | Loader dan perintah navigasi | `UnityCampusMap.tsx`, `SearchOverlay.tsx` | Pemuatan artefak WebGL dan bridge React ke Unity
5 | Notifikasi penyelesaian navigasi | `SearchOverlay.tsx` | Pemeriksaan tujuan aktif sebelum notifikasi kedatangan ditampilkan
6 | REST API Unity | `api/unity/data.js`, `api/unity/names.js` | Penyediaan data untuk aplikasi Unity dan alat bantu editor
7 | Analitik aplikasi | `src/services/analytics/trackingService.ts` | Pencatatan page view pada Supabase
8 | Pemeriksaan layanan dan deployment | `api/health.js`, `vercel.json` | Status layanan, header, kompresi, dan cache aset
[/TABLE]

1. Supabase Client dan Perlindungan Halaman Admin (`src/lib/supabase.ts` dan `src/components/common/ProtectedRoute.tsx`):

```typescript
import { createClient } from "@supabase/supabase-js";
import { env } from "../utils/env";

export const supabase = createClient(
  env.VITE_SUPABASE_URL,
  env.VITE_SUPABASE_ANON_KEY,
  {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true,
    },
  },
);

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-[#2C5F2D] mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) return <Navigate to="/admin/login" replace />;
  return <>{children}</>;
};
```

2. Operasi CRUD Fasilitas melalui Supabase SDK (`src/services/api/supabaseDataService.ts`):

```typescript
export const createFacility = async (
  facility: Omit<Fasilitas, "id">,
): Promise<Fasilitas> => {
  if (!facility.nama_fasilitas) throw new Error("Nama fasilitas wajib diisi.");
  if (!facility.id_gedung) throw new Error("ID gedung wajib diisi.");
  clearCache();

  const { data, error } = await supabase
    .from("fasilitas")
    .insert({
      nama_fasilitas: facility.nama_fasilitas,
      deskripsi_fasilitas: facility.deskripsi_fasilitas,
      tipe_fasilitas: facility.tipe_fasilitas,
      id_gedung: facility.id_gedung,
      color: facility.color || "gray",
      lantai: facility.lantai ?? null,
      foto_url: facility.foto_url ?? null,
      unity_object_name: facility.unity_object_name ?? null,
    })
    .select()
    .single();

  if (error) throw new Error("Gagal membuat fasilitas.");
  await logCreate("fasilitas", data.id.toString(), data);
  return data as Fasilitas;
};
```

3. Keputusan Preload Adaptif Aset Unity (`src/utils/unityPreloader.ts`):

```typescript
function shouldSkipPreload(): { skip: boolean; reason?: string } {
  const isMobile =
    /Android|iPhone|iPad|iPod|webOS|BlackBerry|IEMobile|Opera Mini/i.test(
      navigator.userAgent
    ) || window.innerWidth < 768;
  if (isMobile) {
    return { skip: true, reason: "Mobile device detected — Unity WebGL skipped" };
  }

  const connection = (navigator as any).connection;
  if (connection?.saveData) {
    return { skip: true, reason: "Save-Data mode enabled" };
  }
  if (connection?.effectiveType === "slow-2g" || connection?.effectiveType === "2g") {
    return { skip: true, reason: `Slow connection: ${connection.effectiveType}` };
  }
  return { skip: false };
}
```

Nilai `skip` pada cuplikan tersebut hanya melewati pengunduhan awal di latar belakang. Pengguna mobile atau pengguna dengan koneksi terbatas tetap dapat memilih Denah 3D secara sadar melalui pemilih mode; file WebGL baru dimuat ketika mode tersebut dibuka.

4. Native Unity Loader dan Bridge Perintah Navigasi (`UnityCampusMap.tsx` dan `SearchOverlay.tsx`):

```typescript
const unityConfig = {
  dataUrl: `${basePath}unity-builds/v0.8.6.1/Build/v0.8.6.1.data.unityweb`,
  frameworkUrl: `${basePath}unity-builds/v0.8.6.1/Build/v0.8.6.1.framework.js.unityweb`,
  codeUrl: `${basePath}unity-builds/v0.8.6.1/Build/v0.8.6.1.wasm.unityweb`,
  streamingAssetsUrl: "StreamingAssets",
  productVersion: "v0.8.6.1",
  matchWebGLToCanvasSize: true,
  devicePixelRatio: Math.min(window.devicePixelRatio || 1, 2),
};

const configWithProgress = {
  ...unityConfig,
  onProgress: (progress: number) => {
    const pct = Math.round(progress * 100);
    setLoadingProgress((previous) => Math.max(previous, pct));
  },
};

const instance = await window.createUnityInstance(
  canvas,
  configWithProgress,
  configWithProgress.onProgress,
);
window.unityInstance = instance;

window.unityInstance.SendMessage(
  "NavigationReceiver",
  "NavigateTo",
  item.unityObjectName,
);
```

5. Validasi Callback Penyelesaian Navigasi (`SearchOverlay.tsx`):

```typescript
type NavigationCompletedPayload = {
  unity_object_name: string;
};

const handleNavigationCompleted = (event: Event) => {
  const detail = (event as CustomEvent<unknown>).detail;
  if (typeof detail !== "string" || !detail.trim()) return;

  let payload: NavigationCompletedPayload;
  try {
    payload = JSON.parse(detail) as NavigationCompletedPayload;
  } catch {
    console.warn("[SearchOverlay] Payload OnNavigationCompleted tidak valid.");
    return;
  }

  const completedKey =
    typeof payload?.unity_object_name === "string"
      ? payload.unity_object_name.trim().toLowerCase()
      : "";
  const activeItem = activeNavigationRef.current;
  const selectedKey = activeItem?.unityObjectName.trim().toLowerCase() ?? "";

  if (!activeItem || !completedKey || completedKey !== selectedKey) return;
  setSelectedItem(activeItem);
  setIsNavigating(true);
  setHasReachedDestination(true);
};

window.addEventListener(
  "OnNavigationCompleted",
  handleNavigationCompleted as EventListener,
);
```

6. Vercel Serverless Functions untuk Kontrak Runtime dan Editor (`api/unity/data.js` dan `api/unity/names.js`):

Endpoint runtime mengambil data gedung dan fasilitas melalui query paralel sebagai berikut:

```javascript
const [gedungResult, fasilitasResult] = await Promise.all([
  supabase
    .from("gedung")
    .select("id, nama_gedung, deskripsi_gedung, lokasi, jumlah_lantai, unity_object_name")
    .order("id", { ascending: true }),
  supabase
    .from("fasilitas")
    .select("id, nama_fasilitas, deskripsi_fasilitas, tipe_fasilitas, id_gedung, lantai, foto_url, unity_object_name")
    .order("id_gedung", { ascending: true })
    .order("lantai", { ascending: true }),
]);

if (gedungResult.error) throw gedungResult.error;
if (fasilitasResult.error) throw fasilitasResult.error;

return res.status(200).json(result);
```

Endpoint tooling editor mengekstrak identifier tidak kosong dan mengembalikannya sebagai daftar terurut:

```javascript
const extractNames = (rows) =>
  rows
    ?.map((item) => item.unity_object_name)
    .filter((name) => typeof name === "string" && name.trim().length > 0)
    .sort((a, b) => a.localeCompare(b)) ?? [];

const gedungNames = extractNames(gedungData);
const fasilitasNames = extractNames(fasilitasData);
let resultNames;
const { type } = req.query;
if (type === "gedung") {
  resultNames = gedungNames;
} else if (type === "fasilitas") {
  resultNames = fasilitasNames;
} else {
  resultNames = [...gedungNames, ...fasilitasNames].sort((a, b) =>
    a.localeCompare(b),
  );
}

return res.status(200).json({ unityObjectNames: resultNames });
```

7. Pencatatan Analitik Aktif melalui Supabase (`src/services/analytics/trackingService.ts`):

```typescript
export const trackPageView = async (pagePath?: string): Promise<void> => {
  const page = pagePath || window.location.pathname;
  const { error } = await supabase.from("web_analytics_log").insert({
    visitor_hash: getVisitorHash(),
    page_path: page,
    device_type: getDeviceType(),
  });

  if (error && import.meta.env.DEV) {
    console.warn("Analytics tracking error:", error.message);
  }
};
```

8. Health Check serta Header dan Cache Deployment (`api/health.js` dan `vercel.json`):

```javascript
export default async function handler(req, res) {
  setCors(res);
  if (req.method === "OPTIONS") return res.status(200).end();
  return res.status(200).json(
    createResponse({ status: "OK", message: "Server is running" }),
  );
}
```

```json
{
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Access-Control-Allow-Methods", "value": "GET, OPTIONS" },
        { "key": "Cache-Control", "value": "s-maxage=60, stale-while-revalidate=300" }
      ]
    },
    {
      "source": "/unity-builds/v0.8.6.1/Build/(.*)\\.wasm\\.unityweb",
      "headers": [
        { "key": "Content-Type", "value": "application/wasm" },
        { "key": "Content-Encoding", "value": "br" },
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
      ]
    }
  ]
}
```

---

# LAMPIRAN 4. Panduan Pengguna dan Kontrak Operasional

Panduan ini menjelaskan langkah operasional yang sesuai dengan antarmuka terkini. Informasi kredensial, anon key, service role key, dan nilai environment variables tidak dicantumkan. Panduan internal Unity dibatasi pada tindakan yang terlihat oleh pengguna karena implementasi scene dan engine merupakan kontribusi Simulator dan Engine Developer.

## A. Panduan Administrator

Admin Panel digunakan untuk mengelola data yang dikonsumsi Public Dashboard, Denah 2D, dan kontrak integrasi Unity.

1. Masuk dan Keluar dari Admin Panel:
   a. Buka `/admin/login` atau `/login` pada domain aplikasi.
   b. Masukkan username dan kata sandi akun administrator yang sah, lalu pilih tombol "Masuk".
   c. Supabase Auth membentuk sesi dan `ProtectedRoute` membuka `/admin` setelah autentikasi berhasil.
   d. Gunakan tombol logout setelah pekerjaan selesai, terutama ketika menggunakan perangkat bersama. Kredensial pengujian tidak ditulis pada laporan atau repository.
2. Memilih Modul Pengelolaan:
   a. Admin Panel menyediakan tab Gedung, Fasilitas, Program Studi, Denah 2D, Analytics, dan Audit Log.
   b. Gunakan pencarian, filter, dan paginasi pada tabel untuk mempersempit data sebelum melakukan perubahan.
3. Mengelola Data Gedung dan Fasilitas:
   a. Pilih tab Gedung atau Fasilitas, kemudian gunakan tombol "Tambah Gedung" atau "Tambah Fasilitas" untuk membuka formulir.
   b. Isi field wajib dan field informasi yang tersedia, termasuk nama tampilan, deskripsi, lokasi atau lantai, gedung induk, tipe, serta foto apabila tersedia.
   c. Gunakan aksi Edit untuk memperbarui data dan aksi Hapus untuk membuka konfirmasi sebelum penghapusan dilakukan.
   d. `unity_object_name` merupakan identifier teknis, bukan nama yang ditampilkan kepada pengguna. Field ini diperlukan apabila data menjadi target navigasi 3D langsung dan harus sesuai dengan kontrak GameObject. Fasilitas yang tidak memiliki target langsung dapat dipetakan ke gedung induk sesuai aturan pencarian.
   e. Setelah penyimpanan, periksa toast, data tabel, dan tampilan publik yang terkait. Jumlah data pada deployment tidak boleh disamakan secara otomatis dengan seed lokal sebelum proses sinkronisasi live diverifikasi.
4. Mengelola Program Studi:
   a. Pilih tab Program Studi untuk menambah, mengubah, mencari, atau menghapus data program studi.
   b. Pilih fakultas naungan dan isi field akademik yang tersedia pada formulir. Admin Panel tidak menyediakan tab Fakultas terpisah pada antarmuka yang ditinjau.
5. Mengelola Konfigurasi Denah 2D:
   a. Pilih tab Denah 2D untuk mengelola peta aktif, marker gedung, entrance, node, dan edge graph.
   b. Pastikan setiap gedung yang dapat menjadi titik awal atau tujuan mempunyai marker dan entrance yang terhubung ke graph.
   c. Simpan perubahan secara bertahap dan periksa rute melalui mode 2D pada Public Dashboard. Perubahan graph yang tidak terhubung dapat menyebabkan garis rute tidak terbentuk.
6. Meninjau Analytics dan Audit Log:
   a. Tab Analytics menampilkan agregasi page view yang dibaca dari `web_analytics_log` pada Supabase.
   b. Tab Audit Log menampilkan operasi yang dicatat layanan aplikasi setelah proses CRUD melalui Admin Panel.
   c. Pencatatan dari aplikasi tidak digunakan untuk mengklaim bahwa seluruh mutasi di luar aplikasi otomatis dicatat oleh trigger database.

## B. Panduan Pengguna Publik

Public Dashboard dapat digunakan oleh mahasiswa baru, orang tua atau wali, sivitas akademika, dan pengunjung eksternal untuk memperoleh informasi serta memilih pengalaman navigasi 2D atau 3D.

1. Membuka Dashboard dan Panduan Awal:
   a. Buka root domain `/` melalui browser.
   b. Gunakan pilihan bahasa Indonesia atau Inggris sesuai kebutuhan.
   c. Baca bagian Tutorial dan FAQ Denah Kampus. Tutorial dapat dipilih berdasarkan mode 2D atau 3D dan perangkat desktop atau mobile.
   d. Gunakan kartu serta bagian informasi yang tersedia untuk meninjau gedung, fasilitas, statistik kunjungan, dan informasi utama kampus sebelum membuka denah.
2. Memilih Jenis Denah:
   a. Pilih tombol "Buka Denah Kampus" untuk membuka pemilih mode.
   b. Pilih Denah 2D untuk pencarian rute yang lebih ringan atau Denah 3D untuk pengalaman Unity WebGL.
   c. Tombol "Ganti mode" dapat digunakan untuk kembali ke pemilih tanpa memuat ulang seluruh halaman.
3. Menggunakan Denah 2D:
   a. Pada dialog awal, pilih gedung tempat pengguna berada dan tekan "Gunakan sebagai titik awal".
   b. Ketik nama gedung, ruangan, fasilitas, atau istilah yang familiar pada kolom pencarian, lalu pilih hasil yang sesuai.
   c. Frontend memetakan hasil ke entrance gedung dan menampilkan garis rute hasil perhitungan A* pada denah.
   d. Gunakan pilihan "Mulai dari gedung" untuk mengganti titik awal. Denah 2D mengarahkan pengguna ke entrance gedung tujuan dan tidak mensimulasikan pergerakan di dalam ruangan.
4. Menggunakan Denah 3D:
   a. Pilih Denah 3D dan tunggu progres pemuatan build Unity WebGL v0.8.6.1 selesai. Pada perangkat atau koneksi tertentu, aplikasi tidak melakukan preload otomatis agar halaman utama tetap ringan.
   b. Pilih lokasi awal yang sesuai pada tampilan pemilihan titik awal.
   c. Pada desktop, klik area permainan lalu gunakan `W`, `A`, `S`, dan `D` untuk bergerak, `Shift` untuk berlari, `Space` untuk melompat, mouse untuk mengarahkan kamera, serta `Esc` untuk melepaskan kursor.
   d. Pada mobile, gunakan posisi landscape, joystick kiri untuk bergerak, gestur pada area kanan untuk mengarahkan kamera, serta tombol sprint dan lompat yang tersedia.
5. Mencari Tujuan dan Menyelesaikan Navigasi:
   a. Gunakan Search Overlay di bagian atas denah dan pilih hasil tujuan.
   b. Pada mode 3D, React mengirim `unity_object_name` melalui `SendMessage`, kemudian runtime menampilkan petunjuk rute dan label tujuan.
   c. Setelah pengguna tiba, Unity mengirim `OnNavigationCompleted` beserta `unity_object_name`. React hanya menampilkan notifikasi "Tiba di Tujuan" apabila kode lokasi tersebut sama dengan tujuan yang sedang aktif.
   d. Pengguna dapat membatalkan navigasi atau memilih tujuan baru. Pembatalan tidak diperlakukan sebagai kondisi tiba.
6. Memperoleh Bantuan:
   a. Gunakan tombol bantuan pada canvas 3D untuk membuka panduan navigasi dan kontak layanan kampus.
   b. Jika mode 3D gagal dimuat atau sulit digunakan, muat ulang halaman, periksa koneksi, atau beralih ke Denah 2D.
   c. Nomor layanan yang ditampilkan aplikasi adalah 021-7699431 dan 021-7656971. Kedua nomor tersebut diambil dari [halaman Hubungi Kami pada situs Penmaru UPNVJ](https://penmaru.upnvj.ac.id/id/contact.html).

## C. Kontrak Handoff Data, Artefak Unity, dan Deployment

Bagian ini menjadi daftar pemeriksaan operasional lintas komponen. Penulis mengelola antarmuka React, kontrak API, penghubung React–Unity, dan deployment. Engine Developer mengelola scene, NavMesh, alat bantu editor, optimasi, dan proses build Unity.

1. Pembaruan Data dan Kode Objek:
   a. Perubahan data dilakukan melalui Admin Panel sesuai sesi dan kebijakan akses yang tersedia.
   b. Nama tampilan disimpan terpisah dari `unity_object_name`. Perubahan kode objek harus disepakati bersama karena digunakan oleh API, React, dan GameObject Unity.
   c. `/api/unity/data` menyediakan data untuk aplikasi Unity saat dijalankan, sedangkan `/api/unity/names` digunakan oleh alat bantu editor untuk memeriksa daftar kode objek.
2. Penyerahan Artefak Unity WebGL:
   a. Engine Developer menyerahkan loader, framework, WebAssembly, data, dan StreamingAssets dari satu build yang sama.
   b. Penyerahan mencantumkan nomor versi dan catatan perubahan. Build aktif yang dikonfigurasi pada source saat peninjauan lampiran adalah v0.8.6.1.
   c. Pemberitahuan penyelesaian navigasi menggunakan event `OnNavigationCompleted`. Data yang dikirim harus memuat `unity_object_name` dalam format JSON yang telah disepakati.
3. Deployment oleh Penulis:
   a. Artefak ditempatkan pada path versi di `public/unity-builds/`, kemudian URL loader, preloader, dan `vercel.json` diselaraskan ke versi yang sama.
   b. Vercel menetapkan content type, Brotli content encoding, cache immutable, header keamanan, dan fallback route SPA.
   c. Pemeriksaan dasar mencakup `/api/health`, `/api/unity/data`, `/api/unity/names`, status aset build, progres pemuatan, pengiriman perintah melalui `SendMessage`, dan notifikasi kedatangan.
4. Batas Perubahan:
   a. Masalah kontrak React, API, header, cache, atau deployment diperbaiki oleh penulis.
   b. Masalah scene, spawn, NavMesh, label runtime, minimap, `BuildingDatabase`, `NavigationReceiver`, atau kompilasi dikembalikan kepada Engine Developer untuk diperbaiki dan dibangun ulang.
   c. Hasil pengamatan jaringan pada v0.8.0 dan audit Lighthouse tanggal 21 Juli 2026 merupakan bukti dari versi sebelumnya. Nilainya tidak digunakan untuk menilai build v0.8.6.1 tanpa pengukuran ulang.

---

# LAMPIRAN 5. Instrumen UAT Tertutup dan Indeks Bukti Pengujian

<!-- PIPELINE:INCLUDE content/shared/testing/appendix-instruments.md -->

---

# LAMPIRAN 6. Matriks Artefak dan Reproduksi Pengujian

Lampiran ini memetakan klaim kontribusi Full Stack Web Developer, System Integrator, dan DevOps Engineer kepada artefak yang dapat diperiksa. Matriks tidak menggantikan pembahasan hasil pada BAB III dan tidak memperluas klaim ke implementasi database atau Unity yang dimiliki anggota tim lain.

Hubungan antara area kontribusi, bukti, versi yang diperiksa, dan batas interpretasi ditunjukkan pada [TABREF:lampiran_matriks_artefak_iman].

[TABLE-ID:lampiran_matriks_artefak_iman]
[TABLECAPTION:Matriks Artefak dan Bukti Kontribusi Penulis]

[TABLE]
Area | Artefak atau Lokasi | Versi Bukti | Hasil yang Dibuktikan | Batas Interpretasi
Frontend publik dan admin | Empat gambar UI utama pada BAB III; `src/components/dashboard/`, `src/components/admin/` | Tangkapan layar deployment 21 Juli 2026 | Public Dashboard, pencarian, canvas 3D, dan Admin Panel tersedia | Tangkapan layar tidak membuktikan seluruh kondisi antarmuka atau penerapan seed ke database aktif
Autentikasi dan CRUD | `AuthContext.tsx`, `ProtectedRoute.tsx`, `supabaseDataService.ts` | Kode sumber web `08ebc06` | Sesi, jalur admin terproteksi, validasi formulir, dan CRUD melalui Supabase SDK | Rancangan RLS dan skema database bukan kontribusi penulis
Pengujian React | `SearchOverlay.test.tsx` dan suite Vitest | Kode sumber `08ebc06`; pengujian awal `b572a48`; pengujian lanjutan `d2e8fdb` | 13 berkas dan 129 pengujian lulus, termasuk 11 pengujian notifikasi kedatangan | Angka berlaku untuk versi kode sumber yang dicantumkan
REST API dan kontrol akses | `api/health.js`, `api/unity/data.js`, `api/unity/names.js`; empat gambar TEST API | Pemeriksaan 21 Juli 2026 | Tiga endpoint GET memperoleh HTTP 200 dan perubahan data tanpa otorisasi ditolak RLS | Pemeriksaan manual belum menggantikan pengujian otomatis dari browser sampai layanan akhir
Integrasi React–Unity | `SearchOverlay.tsx`, event `OnNavigationCompleted`, tangkapan layar notifikasi tiba | React `08ebc06`; Unity `1845c65` | Notifikasi hanya muncul apabila tujuan yang dilaporkan Unity sesuai dengan tujuan aktif di React | Proses navigasi dan build Unity dimiliki Engine Developer
Deployment WebGL | `UnityCampusMap.tsx`, `unityPreloader.ts`, `vercel.json`, `api/health.js` | Build v0.8.6.1 dari `d30f7d1`; kode web `08ebc06` | Loader, lokasi aset versi, pemeriksaan layanan, kompresi Brotli, tipe konten, dan cache telah dikonfigurasi | Belum terdapat pengukuran jaringan baru yang menggantikan pengamatan v0.8.0
Lighthouse | `reports/lighthouse/latest-summary.md` | `bdeb5bc` | Performance mobile 86 dan desktop 99; tiga kategori lain 100 | Hasil merupakan pengujian laboratorium lokal, bukan data pengguna nyata atau pengukuran build v0.8.6.1
Tindak lanjut pengujian pengguna | Subbab 3.5, `content/shared/testing/results.json`, dan folder dokumentasi revisi | Verifikasi 21 Juli 2026 | Basis visual, audit kode sumber, pengujian otomatis, dan sumber resmi terdokumentasi | Tangkapan layar revisi bukan kuesioner UAT kedua
[/TABLE]

Perintah reproduksi untuk repository web adalah sebagai berikut:

1. `npm test` menjalankan suite Vitest satu kali.
2. `npm run lint` menjalankan pemeriksaan ESLint.
3. `npm run build` menjalankan TypeScript build dan production build Vite.
4. `npm run lighthouse` membangun aplikasi, menjalankan preview lokal, dan memperbarui audit mobile serta desktop.
5. Pemeriksaan deployment dilakukan melalui `GET /api/health`, `GET /api/unity/data`, dan `GET /api/unity/names`, lalu dilengkapi skenario negatif mutasi Supabase tanpa sesi yang sah.

Reproduksi memerlukan environment variables yang valid pada lingkungan pemeriksa. Nilai rahasia, kata sandi administrator, service role key, dan kredensial layanan tidak disertakan dalam lampiran atau perintah reproduksi.
