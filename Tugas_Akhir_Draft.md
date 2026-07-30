# Pengembangan Dashboard Web, Integrasi Unity WebGL, dan Deployment Sistem Denah Virtual UPNVJ Kampus Pondok Labu

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

LAMPIRAN 1. Dokumentasi Penyerahan Pakta Integritas kepada UPA TIK
LAMPIRAN 2. Kode Sumber Utama
LAMPIRAN 3. Panduan Pengguna dan Prosedur Operasional
LAMPIRAN 4. Instrumen UAT Tertutup dan Indeks Bukti Pengujian
LAMPIRAN 5. Matriks Bukti dan Prosedur Pengujian Ulang
LAMPIRAN 6. Dokumen Administratif Penelitian dan Pelaksanaan UAT

# BAB I PENDAHULUAN

## 1.1 Latar Belakang

<!-- PIPELINE:INCLUDE content/shared/bab1/latar-belakang-umum.md -->

## 1.2 Identifikasi Masalah

Berdasarkan penjabaran latar belakang serta pengumpulan data awal yang telah diuraikan, identifikasi masalah dalam penelitian ini dirumuskan sebagai berikut:

1. Pengguna sasaran, yaitu sivitas akademika seperti mahasiswa, dosen, dan tenaga kependidikan serta pengunjung eksternal seperti calon mahasiswa, orang tua atau wali mahasiswa, dan tamu kampus, masih dapat mengalami kesulitan menemukan gedung atau fasilitas. Pada sampel kebutuhan awal, 14 dari 21 responden pernah mengalami kesulitan setidaknya satu kali dalam satu semester dan 90,5 persen responden paling sering meminta bantuan orang lain ketika mencari lokasi.
2. Informasi gedung atau fasilitas, pencarian tujuan, dan panduan spasial belum terhubung dalam satu alur web pada ruang lingkup produk yang dikembangkan. Pengguna memerlukan pilihan panduan Denah 2D atau Denah 3D agar dapat memilih cara navigasi sesuai tingkat pengenalan kampus dan pengalaman menggunakan navigasi digital.
3. Pengelola sistem memerlukan cara yang terkendali untuk memperbarui informasi gedung, fasilitas, dan tujuan navigasi. Informasi yang diperbarui perlu digunakan secara konsisten oleh Dashboard Publik, pencarian lokasi, Denah 2D, dan Denah 3D agar pengguna tidak menerima tujuan atau keterangan yang berbeda antarkomponen.

## 1.3 Batasan Masalah

Untuk menjaga fokus, ruang lingkup, serta kelayakan penelitian, batasan masalah dalam pengembangan sistem integrasi denah virtual kampus dan dashboard web Universitas Pembangunan Nasional Veteran Jakarta ditetapkan sebagai berikut:

1. Pengguna sasaran mencakup sivitas akademika dan pengunjung eksternal Kampus Pondok Labu. Kuesioner kebutuhan awal didominasi pengguna internal, sedangkan UAT tertutup tidak melibatkan sampel calon mahasiswa, orang tua atau wali mahasiswa, maupun pengunjung eksternal. Hasil evaluasi karena itu tidak digeneralisasi sebagai penilaian seluruh kelompok pengguna sasaran.
2. Cakupan area informasi, pencarian, dan visualisasi dibatasi pada lingkungan UPNVJ Kampus Pondok Labu.
3. Fungsi bagi pengguna dibatasi pada penyajian informasi kampus terpilih, pencarian gedung atau fasilitas, Tutorial dan FAQ, pilihan Denah 2D atau Denah 3D, serta panduan menuju tujuan. Denah 2D mengarahkan pengguna sampai pintu masuk gedung dan tidak memetakan rute di dalam ruangan.
4. Fungsi administratif dibatasi pada autentikasi serta pengelolaan data gedung, fasilitas, program studi, dan konfigurasi Denah 2D. Sistem tidak mengelola data akademik utama seperti data mahasiswa, dosen, perkuliahan, keuangan, atau akreditasi.
5. Lingkup penulis mencakup Dashboard Publik, Panel Admin, Denah 2D berbasis React, REST API, integrasi Supabase Auth dan operasi CRUD, penghubung perintah React ke Unity, penerimaan notifikasi kedatangan, deployment file hasil build WebGL, serta pengoperasian layanan web.
6. Skema database, RLS, rancangan trigger database, aset 3D, dan hierarki `Pointer` merupakan kontribusi 3D Asset Designer dan Database Schema Designer. Aplikasi Unity, navigasi, alat bantu editor, optimasi, serta proses build Unity WebGL merupakan kontribusi 3D Simulator dan Engine Developer.
7. Sistem yang dikembangkan menggunakan layanan proyek yang tersedia pada saat penelitian dan belum terhubung secara waktu nyata dengan seluruh sistem internal universitas. Integrasi institusional pada tahap berikutnya harus mengikuti ketentuan, izin, identitas, dan infrastruktur yang disetujui unit terkait.

Pembagian peran dan tanggung jawab pada proyek sistem dijelaskan lebih detail dalam [TABREF:peran_tanggung_jawab].

[TABLE-ID:peran_tanggung_jawab]
[TABLECAPTION:Peran dan Tanggung Jawab]

[TABLE]
Peran | Tugas dan Tanggung Jawab
3D Asset Designer dan Database Schema Designer | Merancang aset visual 3D dan hierarki prefab beserta objek `Pointer`, serta merancang skema database Supabase PostgreSQL, ERD, kebijakan RLS, dan rancangan trigger database.
3D Simulator dan Engine Developer | Mengembangkan aplikasi Unity WebGL, penerimaan data dan perintah, navigasi NavMesh, interaksi pengguna, optimasi kinerja, alat bantu editor, serta proses build WebGL.
Full Stack Web Developer, System Integrator, dan DevOps Engineer | Mengembangkan Dashboard Publik dan Panel Admin React, REST API pada Vercel Serverless Functions, integrasi autentikasi dan pengelolaan data melalui Supabase, penghubung React–Unity, pencatatan analitik aplikasi, pengujian web, deployment, dan pengoperasian layanan web; Express dan Umami dikelola sebagai jalur opsional.
[/TABLE]

## 1.4 Tujuan dan Manfaat

### 1.4.1 Tujuan

Berdasarkan identifikasi masalah pada Subbab 1.2, tujuan penelitian ini dirumuskan sebagai berikut:

1. Mengembangkan Dashboard Publik berbasis web yang membantu sivitas akademika dan pengunjung eksternal memperoleh informasi serta menemukan gedung atau fasilitas di Kampus Pondok Labu.
2. Menghubungkan pencarian tujuan dengan panduan spasial melalui perhitungan rute pada Denah 2D dan pengiriman tujuan ke Denah 3D, sehingga pengguna dapat memilih cara navigasi yang sesuai dan memperoleh umpan balik ketika tujuan tercapai.
3. Mengembangkan Panel Admin dan mekanisme integrasi data yang memungkinkan administrator memperbarui informasi melalui akses terkendali serta menjaga konsistensi data pada Dashboard Publik, pencarian, Denah 2D, dan Denah 3D.

### 1.4.2 Manfaat

Penelitian ini diharapkan dapat memberikan manfaat bagi berbagai pihak, antara lain:

1. Bagi sivitas akademika dan pengunjung eksternal, aplikasi menyediakan satu tempat untuk menelusuri informasi kampus, mencari gedung atau fasilitas, dan membuka denah virtual melalui browser.
2. Bagi staf pengelola, Panel Admin menyediakan antarmuka untuk memperbarui konten sesuai hak akses tanpa mengubah kode aplikasi maupun file hasil build Unity selama kode lokasi tetap konsisten.
3. Bagi Humas UPNVJ sebagai mitra pengguna, sistem yang dikembangkan dapat dievaluasi sebagai media informasi dan navigasi untuk membantu mahasiswa baru, orang tua atau wali, sivitas akademika, dan pengunjung eksternal.
4. Bagi UPA TIK dan tim pengembang, REST API, penghubung React–Unity, serta konfigurasi deployment menyediakan spesifikasi teknis yang terdokumentasi dan dapat disesuaikan apabila sistem memperoleh persetujuan untuk dipindahkan ke infrastruktur institusi.

## 1.5 Jadwal Kegiatan

Jadwal pelaksanaan proyek dirinci dalam tabel enam bulan yang menyajikan alokasi waktu pengerjaan secara bertahap, sebagaimana ditunjukkan pada [TABREF:jadwal_kegiatan]. Keseluruhan rangkaian kegiatan dilaksanakan dalam enam bulan.

[TABLE-ID:jadwal_kegiatan]
[TABLECAPTION:Jadwal Kegiatan]

[TABLE gantt]
Aktivitas | Bulan 1 | Bulan 2 | Bulan 3 | Bulan 4 | Bulan 5 | Bulan 6
Desain Arsitektur dan Antarmuka | X | | | | |
Pengembangan Layanan Server | | X | X | | |
Pengembangan Antarmuka Web | | | X | X | |
Integrasi dan Pengujian Sistem | | | | X | X |
Revisi Final dan Penulisan Laporan | | | | | X | X
Dokumentasi | X | X | X | X | X | X
[/TABLE]

Alur pengerjaan dilaksanakan secara bertahap dengan beberapa kegiatan yang saling tumpang tindih. Tahapan-tahapan tersebut adalah:

1. Desain Arsitektur dan Antarmuka (Bulan 1): Tahap awal yang berfokus pada rancangan arsitektur sistem, mekanisme integrasi, Use Case Diagram, ERD yang dirancang Database Schema Designer, dan rancangan awal antarmuka.
2. Pengembangan Layanan Server (Bulan 2-3): Tahap implementasi kode sisi server, mencakup REST API Node.js dan integrasi layanan Supabase berdasarkan skema database yang dirancang Database Schema Designer.
3. Pengembangan Antarmuka Web (Bulan 3-4): Tahap implementasi React yang berfokus pada pembangunan Panel Admin dan Dashboard Publik. Tahap ini berjalan bersamaan dengan sebagian pekerjaan backend.
4. Integrasi, Deployment, dan Pengujian Sistem (Bulan 4-5): Tahap penyatuan frontend, backend, dan Unity WebGL, konfigurasi deployment layanan, serta pemeriksaan menggunakan skenario pengujian Black Box.
5. Revisi Final dan Penulisan Laporan (Bulan 5-6): Alokasi waktu khusus untuk perbaikan berdasarkan hasil pengujian, verifikasi ulang, dan penyusunan draf final laporan.
6. Dokumentasi (Bulan 1-6): Aktivitas ini dilakukan secara paralel sepanjang proyek untuk memastikan proses, desain, dan kode terdokumentasi dengan baik.

## 1.6 Sistematika Penulisan

Sistematika penulisan laporan Tugas Akhir Proyek ini disusun secara terperinci ke dalam empat bab utama guna memberikan alur pembahasan yang runtut dan sistematis:

1. BAB I PENDAHULUAN: Memaparkan latar belakang masalah navigasi spasial, identifikasi masalah, batasan penelitian, tujuan dan manfaat, jadwal kegiatan, serta sistematika penulisan.
2. BAB II RANCANGAN PROYEK: Menguraikan hasil observasi sistem berjalan, usulan solusi teknis berupa arsitektur terintegrasi, identifikasi kebutuhan fungsional dan teknis, rencana pengembangan prototyping, desain UML, pemetaan data integrasi, rancangan antarmuka pengguna, serta rencana pengujian sistem.
3. BAB III IMPLEMENTASI PROYEK: Mendokumentasikan profil institusi mitra, metode pengembangan prototyping, implementasi antarmuka web dan layanan server, integrasi Unity WebGL, catatan kegiatan proyek, konfigurasi sistem, serta hasil evaluasi Black Box dan UAT.
4. BAB IV PENUTUP: Menyajikan kesimpulan akhir dari hasil pengembangan dan evaluasi sistem serta saran untuk pengembangan selanjutnya.

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

Berdasarkan analisis pada Subbab 2.1, proyek mengusulkan aplikasi web yang menggabungkan penyajian informasi kampus, pengelolaan konten, dan akses denah virtual dalam satu pengalaman pengguna. Solusi ini tidak dimaksudkan untuk menggantikan seluruh sistem institusional UPNVJ. Kontribusi penulis difokuskan pada antarmuka React, REST API, penghubung React–Unity, deployment, dan pengoperasian layanan web.

Secara umum, solusi yang diusulkan memiliki karakteristik sebagai berikut:

1. Antarmuka Aplikasi Web
   a. Dashboard Publik menyajikan informasi kampus, pemilih denah 2D atau tur 3D, pencarian lokasi, petunjuk interaksi, dan bantuan pemuatan.
   b. Panel Admin menyediakan autentikasi, pengelolaan data, konfigurasi denah 2D, catatan perubahan, dan analitik melalui halaman yang hanya dapat diakses setelah pengguna masuk.
2. Integrasi Berbasis Spesifikasi
   a. React menggunakan Supabase Auth dan Supabase SDK secara langsung untuk autentikasi, sesi, permintaan data, dan CRUD sesuai kebijakan akses yang tersedia.
   b. Vercel Serverless Functions menyediakan REST API bagi komponen yang memerlukan respons JSON, termasuk aplikasi Unity dan alat bantu Unity Editor.
3. Pemisahan Data dan Perintah Unity
   a. Unity menarik data secara mandiri saat dijalankan melalui `GET /api/unity/data`.
   b. React hanya mengirim kode tujuan melalui mekanisme `SendMessage`; data gedung dan fasilitas tidak dikirim dari React ke Unity.
4. Deployment dan Pengoperasian Layanan
   a. Implementasi saat ini menggunakan Vercel untuk React SPA, layanan API, dan penyajian file hasil build WebGL. Analitik utama menggunakan data Supabase, sedangkan Express dan Umami yang dihosting mandiri dipertahankan sebagai jalur opsional.
   b. Konfigurasi domain, variabel lingkungan, kunci rahasia, kredensial, dan konektivitas layanan dapat disesuaikan apabila sistem kelak diintegrasikan dengan infrastruktur kampus.
5. Batas Kolaborasi
   a. Penulis mengembangkan antarmuka web, API, penghubung pada sisi React, dan pengoperasian layanan web.
   b. Skema dan kontrol database disediakan Database Schema Designer, sedangkan aplikasi Unity saat dijalankan serta proses build-nya disediakan 3D Simulator dan Engine Developer.

Karakteristik tersebut menempatkan aplikasi sebagai lapisan integrasi yang menghubungkan beberapa komponen tanpa mengaburkan batas kontribusi implementasinya. Struktur arsitektur sistem secara umum disajikan pada [FIGREF:diagram_arsitektur].

[FIGURE:diagram_arsitektur]
[FIGCAPTION:Arsitektur Integrasi Dashboard Web, Supabase, dan Unity WebGL]

Sebagaimana diilustrasikan pada [FIGREF:diagram_arsitektur], interaksi antarmuka web, layanan server, dan Unity WebGL berlangsung melalui tujuh alur berikut:

1. Pemuatan Aplikasi dan Aset: Browser memuat React SPA beserta file hasil build Unity WebGL dari Vercel. Penulis mengelola konfigurasi deployment, variabel lingkungan, header, dan cache aset pada bagian tersebut.
2. Autentikasi dan Pengelolaan Data: React berinteraksi langsung dengan Supabase Auth melalui SDK untuk mengautentikasi administrator dan memperoleh sesi JWT. Dashboard Publik dan Panel Admin membaca atau mengubah data melalui Supabase SDK sesuai kebijakan RLS yang dirancang Database Schema Designer.
3. Penyediaan REST API: Vercel Serverless Functions menyediakan layanan `/api/buildings`, `/api/rooms`, `/api/unity/data`, `/api/unity/names`, dan `/api/health`. Setiap fungsi mengambil data dari Supabase dan mengembalikan respons JSON sesuai kebutuhan konsumennya.
4. Penarikan Data oleh Unity WebGL: Ketika Unity dijalankan, modul `BuildingDatabase` milik Unity memanggil `GET /api/unity/data` secara mandiri untuk memperoleh data gedung dan fasilitas. React tidak mengirimkan data JSON ke Unity. Layanan `/api/unity/names` digunakan oleh alat pemeriksaan sinkronisasi pada Unity Editor (`DatabaseSyncChecker`), bukan sebagai jalur data saat Unity dijalankan.
5. Perintah dan Penyelesaian Navigasi: Ketika pengguna memilih lokasi pada mode 3D, antarmuka web mengirim kode lokasi Unity (`unity_object_name`) melalui mekanisme pengiriman perintah React–Unity (`SendMessage`). Setelah pengguna tiba, Unity mengirim notifikasi kedatangan (`OnNavigationCompleted`) beserta kode lokasi. React membandingkan kode tersebut dengan tujuan aktif sebelum menampilkan notifikasi kepada pengguna. Data yang kosong, tidak valid, berbeda, atau diterima setelah pembatalan diabaikan.
6. Integrasi Analitik: Analitik utama mencatat dan menggabungkan data `web_analytics_log` melalui Supabase. Express.js pada port 3001 menyediakan pembatasan jumlah permintaan dan perantara menuju Umami sebagai jalur opsional yang dapat dijalankan melalui Docker.
7. Batas Tanggung Jawab Integrasi: Penulis menangani antarmuka web, REST API, penghubung pada sisi React, pencatatan riwayat perubahan oleh layanan aplikasi, dan pengoperasian layanan web. Database Schema Designer menangani ERD, skema database, RLS, serta rancangan trigger database. 3D Asset Designer menangani aset 3D dan hierarki `Pointer`. 3D Simulator dan Engine Developer menangani aplikasi Unity, pemetaan objek tujuan, navigasi, optimasi, dan proses build WebGL.

Fokus utama usulan solusi dalam laporan ini adalah pengembangan aplikasi web secara menyeluruh, integrasi antarsistem, serta deployment dan pengoperasian layanan web.

### 2.2.1 Identifikasi Kebutuhan Fungsional

Kebutuhan fungsional diturunkan dari kebutuhan pengguna, batas akses data, dan arsitektur integrasi pada Subbab 2.1 dan 2.2. Kebutuhan berikut difokuskan pada komponen yang dikembangkan atau diintegrasikan oleh penulis.

1. Kebutuhan Fungsional Pengguna Publik
   a. Sistem harus menyajikan informasi utama kampus, statistik kunjungan, kartu gedung atau fasilitas, serta akses pencarian lokasi yang tersedia untuk publik.
   b. Sistem harus menyediakan pemilih mode denah 2D atau tur 3D sesuai dukungan hosting dan perangkat pengguna.
   c. Mode 2D harus menggunakan konfigurasi titik jalur, ruas penghubung, dan pintu masuk untuk menghitung serta menggambar rute menuju gedung yang dipilih.
   d. Mode 3D harus menyediakan kanvas Unity WebGL beserta indikator pemuatan, pesan kesalahan, dan petunjuk interaksi.
   e. Sistem harus menyediakan pencarian gedung atau fasilitas pada antarmuka React dan menerjemahkan pilihan pengguna menjadi identitas gedung untuk Denah 2D atau kode lokasi Unity untuk Denah 3D.
   f. Sistem harus menyediakan tombol bantuan atau petunjuk yang relevan pada area denah.
   g. Sistem harus mendukung Bahasa Indonesia dan Inggris serta menyimpan preferensi bahasa pada browser.
2. Kebutuhan Fungsional Administrator
   a. Sistem harus mengautentikasi administrator melalui Supabase Auth dan mempertahankan sesi pada halaman admin yang dilindungi.
   b. Sistem harus menyediakan CRUD data gedung, fasilitas, program studi, dan konfigurasi jalur denah 2D melalui Supabase SDK sesuai kebijakan RLS. Data fakultas digunakan sebagai referensi pilihan pada formulir program studi dan tidak dikelola melalui tab CRUD terpisah.
   c. Sistem harus meminta konfirmasi sebelum penghapusan dan menampilkan status berhasil atau gagal dari setiap operasi.
   d. Sistem harus menampilkan riwayat perubahan yang hanya dapat dilihat dan menyajikan analitik bagi administrator.
3. Kebutuhan Fungsional API dan Penghubung Unity
   a. Sistem harus menyediakan endpoint API `GET /api/unity/data` yang menyajikan data gedung dan fasilitas beserta `unity_object_name` dalam satu respons JSON terstruktur.
   b. Sistem harus menyediakan endpoint API `GET /api/unity/names` yang menyajikan larik nama unik objek terdaftar untuk pemeriksaan sinkronisasi di Unity Editor.
   c. Sistem harus menyediakan endpoint `/api/buildings`, `/api/rooms`, dan `/api/health` untuk akses data serta pemeriksaan status setiap layanan.
   d. Antarmuka web harus mengirim kode lokasi ke penerima perintah navigasi ketika pengguna memilih tujuan dan mengirim perintah berhenti ketika navigasi dibatalkan.
   e. Penghubung React–Unity tidak mengirim data gedung. Setelah navigasi selesai, React harus mencocokkan kode lokasi pada notifikasi kedatangan dengan tujuan aktif sebelum menampilkannya kepada pengguna.
4. Kebutuhan Fungsional Deployment dan Pengoperasian Layanan
   a. Sistem harus memisahkan konfigurasi layanan melalui variabel lingkungan dan tidak menanamkan kunci rahasia atau kredensial ke dalam kode sumber.
   b. Layanan hosting harus menyajikan React SPA, API, serta file hasil build WebGL dengan header tipe konten dan cache yang sesuai.
   c. Pengoperasian layanan harus menyediakan endpoint status layanan serta pembatasan jumlah permintaan pada layanan pendukung Express untuk analitik.

### 2.2.2 Identifikasi Kebutuhan Teknis

RESTful API menyediakan antarmuka pertukaran data melalui permintaan HTTP, sedangkan JSON Web Token (JWT) dapat digunakan untuk membawa informasi sesi yang divalidasi oleh layanan. Penerapan JWT pada RESTful API telah digunakan untuk mendukung pengelolaan sesi dan pembatasan akses (Dalimunthe et al. 2023). Dalam proyek ini, sesi JWT diperoleh melalui Supabase Auth; laporan tidak menetapkan atau mengklaim algoritma penandatanganan token yang tidak diverifikasi.

Arsitektur *serverless* menjalankan fungsi aplikasi melalui layanan komputasi terkelola dan dapat menghubungkan fungsi dengan layanan backend melalui API atau SDK. Pemisahan tersebut mendukung penempatan fungsi sesuai kebutuhan tanpa menjadikan pengembang bertanggung jawab atas seluruh pengelolaan server fisik, meskipun konfigurasi, keamanan, dan ketergantungan layanan tetap harus dikendalikan (Li et al. 2022).

Kebutuhan teknis dipetakan berdasarkan fungsi setiap komponen dalam implementasi sebagai berikut:

1. Antarmuka Web
   a. React, TypeScript, dan Vite digunakan untuk membangun SPA, mengatur perpindahan halaman dan kondisi antarmuka, serta memisahkan Dashboard Publik dari Panel Admin.
   b. Tailwind CSS dan Lucide React digunakan untuk penyusunan tampilan, sedangkan Recharts digunakan untuk grafik dan Fuse.js untuk pencarian toleran terhadap variasi kata.
   c. Loader Unity WebGL digunakan untuk memuat file hasil build ke elemen kanvas, memantau kemajuan, dan menyediakan mekanisme pengiriman perintah React–Unity.
2. Autentikasi dan Akses Data Aplikasi
   a. Supabase Auth menyediakan autentikasi dan sesi administrator.
   b. Supabase SDK digunakan React untuk membaca dan mengubah data sesuai skema serta kebijakan RLS yang disediakan Database Schema Designer.
3. Layanan Server dan Spesifikasi API
   a. Vercel Serverless Functions berbasis Node.js digunakan sebagai REST API utama.
   b. Setiap fungsi memvalidasi metode HTTP, mengambil data melalui klien Supabase, membentuk respons JSON, dan menangani kondisi kesalahan.
4. Analitik dan Layanan Pendukung
   a. Analitik utama menggunakan pencatatan dan penggabungan data `web_analytics_log` melalui Supabase.
   b. Express pada port 3001 menyediakan perantara Umami dan pembatasan jumlah permintaan sebagai pilihan pengoperasian; Umami dapat dijalankan secara mandiri melalui Docker. Express bukan API utama yang tersedia melalui Vercel.
5. Hosting
   a. Vercel digunakan untuk menyajikan React SPA, Vercel Serverless Functions, dan file hasil build Unity WebGL.
   b. Variabel lingkungan, header respons, tipe konten, cache aset, dan jalur cadangan SPA dikelola pada konfigurasi deployment.

### 2.2.3 Identifikasi Kebutuhan Non-Fungsional

Web Content Accessibility Guidelines (WCAG) 2.2 mengelompokkan aksesibilitas konten web ke dalam prinsip dapat dipersepsi, dapat dioperasikan, dapat dipahami, dan tangguh. Pada proyek ini, WCAG 2.2 digunakan sebagai acuan untuk akses papan ketik, pelabelan komponen, penyampaian status, dan penanganan kesalahan, tetapi tidak digunakan untuk mengklaim kepatuhan penuh tanpa pemeriksaan seluruh kriteria yang berlaku (W3C 2024).

Kebutuhan nonfungsional digunakan sebagai acuan kualitas aplikasi web dan pengoperasian layanan. Pemenuhannya dievaluasi melalui pengujian web, pemeriksaan lingkungan produksi, Lighthouse, pengujian fungsional, dan UAT.

1. Kinerja
   a. React SPA harus tetap dapat digunakan sebelum pengguna mengaktifkan atau menunggu inisialisasi Unity WebGL.
   b. Pemuatan aset WebGL harus menampilkan kemajuan dan pesan kondisi, menggunakan cache, serta menyesuaikan pemuatan awal berdasarkan perangkat, preferensi penghematan data, dan kualitas koneksi yang dapat dideteksi browser.
   c. Kinerja halaman harus diukur secara berulang dengan Lighthouse pada smartphone dan komputer desktop sebagai dasar optimasi, bukan dinyatakan berhasil berdasarkan batas waktu yang tidak memiliki bukti pengukuran.
2. Kompatibilitas dan Aksesibilitas
   a. Antarmuka harus responsif dan mengutamakan penggunaan melalui browser pada smartphone, serta tetap optimal pada komputer desktop.
   b. Antarmuka mendukung bahasa Indonesia dan Inggris serta menyimpan pilihan bahasa pengguna.
3. Keamanan
   a. Seluruh operasi perubahan data pada Panel Admin wajib menggunakan sesi Supabase Auth yang valid.
   b. Antarmuka web dan API harus mengikuti kebijakan RLS yang disediakan Database Schema Designer. Kunci dengan hak akses tinggi dan kredensial tidak boleh dimasukkan ke dalam kode yang dikirim ke browser.
   c. Layanan pendukung Express harus membatasi jumlah permintaan sesuai konfigurasi yang ditetapkan.
4. Privasi
   a. Konfigurasi analitik harus membatasi data yang dikirim sesuai kebutuhan statistik penggunaan dan kebijakan layanan yang berlaku.
5. Kemudahan Penggunaan dan Aksesibilitas
   a. Sistem harus menampilkan layar pemuatan, kemajuan proses, pesan kesalahan, dan opsi mencoba kembali ketika denah 3D gagal dimuat.
   b. Lapisan pencarian dan jendela konfirmasi harus dapat dioperasikan menggunakan papan ketik serta menyediakan label yang dapat dikenali teknologi bantu.
6. Keterpeliharaan
   a. Perubahan data gedung atau fasilitas melalui Panel Admin dapat digunakan pada pemuatan berikutnya tanpa proses build ulang Unity selama kode lokasi tetap sesuai dengan objek tujuan yang tersedia.
   b. Domain, kredensial layanan, versi file hasil build WebGL, dan konfigurasi hosting harus dapat disesuaikan tanpa mengubah struktur pertukaran data antarkomponen.

## 2.3 Rancangan Proyek

### 2.3.1 Rencana Pengembangan

Metodologi penelitian dan pengembangan yang digunakan pada proyek ini adalah Prototyping. Metode prototyping bersifat iteratif dan berorientasi pada umpan balik pengguna, sehingga sesuai ketika kebutuhan sistem perlu diperjelas melalui purwarupa yang dapat diperiksa dan diperbaiki (Syarif dan Risdiansyah 2024). Penerapannya dilakukan melalui lima tahap yang dikerjakan sesuai peran masing-masing tetapi dipertemukan pada kontrak data, kode lokasi, antarmuka web, dan file hasil build Unity WebGL.

1. Pengumpulan Kebutuhan
   a. Tim menggunakan kuesioner, tinjauan jalur informasi, wawancara, dan koordinasi pemangku kepentingan untuk memetakan masalah navigasi, batas data, serta kebutuhan pengguna dan pengelola.
   b. Full Stack Web Developer, System Integrator, dan DevOps Engineer merumuskan kebutuhan Dashboard Publik, Panel Admin, pencarian, Denah 2D, REST API, penghubung React–Unity, deployment, dan pengoperasian layanan.
   c. 3D Asset Designer dan Database Schema Designer merumuskan kebutuhan aset, struktur data, relasi, kebijakan akses, serta kode lokasi yang digunakan bersama.
   d. 3D Simulator dan Engine Developer merumuskan kebutuhan visualisasi 3D, navigasi, titik awal, alat pemeriksaan pada Unity Editor, dan proses build WebGL.
   e. Hasil tahap ini disatukan menjadi kebutuhan fungsional, batas kontribusi, dan kontrak integrasi antarkomponen.
2. Perancangan Cepat
   a. Penulis merancang arsitektur web, alur pengguna, antarmuka Dashboard Publik dan Panel Admin, Denah 2D, bentuk respons API, serta mekanisme pertukaran pesan dengan Unity.
   b. Database Schema Designer menyiapkan ERD dan struktur data, sedangkan 3D Asset Designer menyiapkan aset dan pemetaan objek. Engine Developer merancang alur Unity, navigasi, dan kebutuhan file hasil build.
   c. Rancangan ketiga peran dihubungkan melalui identitas gedung atau fasilitas, kode lokasi Unity, endpoint data, dan batas tanggung jawab deployment.
3. Pembangunan Prototipe
   a. Penulis membangun React SPA, Denah 2D berbasis A\*, Panel Admin, layanan API, autentikasi dan layanan data, pemuat Unity WebGL, penghubung navigasi, serta konfigurasi deployment.
   b. Database Schema Designer dan 3D Asset Designer membangun struktur data serta aset yang digunakan pada versi sistem, sedangkan Engine Developer membangun aplikasi Unity, NavMesh, mekanisme navigasi, alat pemeriksaan, dan file hasil build WebGL.
   c. Setiap keluaran peran digabungkan secara bertahap. React menggunakan data dan kode lokasi yang sama, Unity mengambil data melalui API, dan file hasil build ditempatkan pada aplikasi web untuk menghasilkan versi sistem yang terintegrasi.
4. Evaluasi Prototipe
   a. Setiap anggota memeriksa komponen sesuai kepemilikannya sebelum pengujian integrasi.
   b. Penulis memeriksa komponen React, layanan API, autentikasi, pencarian, Denah 2D, penghubung React–Unity, konfigurasi deployment, dan kondisi pemuatan.
   c. Tim kemudian menjalankan Black Box Testing dan UAT terhadap produk terintegrasi agar masalah antarkomponen tidak dinilai sebagai keluaran satu peran saja.
5. Perbaikan Berulang
   a. Penulis menindaklanjuti masukan yang berkaitan dengan antarmuka web, Tutorial dan FAQ, pemilih mode, Denah 2D, pencarian, bantuan, dan validasi notifikasi kedatangan.
   b. Database Schema Designer dan 3D Asset Designer menindaklanjuti konsistensi data serta aset, sedangkan Engine Developer menindaklanjuti navigasi, label lingkungan 3D, minimap, titik awal, dan pengiriman status kedatangan.
   c. Perubahan tersebut diintegrasikan kembali, diperiksa melalui pengujian sesuai peran, dan diulang apabila kriteria fungsi atau integrasi belum terpenuhi.

Tahapan pengembangan ini secara visual digambarkan pada [FIGREF:diagram_tahap_pengembangan].

[FIGURE:diagram_tahap_pengembangan]
[FIGCAPTION:Tahapan Metode Prototyping pada Pengembangan Sistem]

### 2.3.2 Perancangan Arsitektur Informasi

Arsitektur informasi mengatur aliran dan penyajian informasi agar pengguna dapat menavigasi serta menemukan konten yang dibutuhkan. Kajian pada situs perpustakaan universitas menempatkan arsitektur informasi, navigasi, pencarian, dan kemudahan penggunaan sebagai aspek yang saling berkaitan (Chandralekha dan Raghunandana 2023). Pada proyek ini, prinsip tersebut diterapkan dengan membagi aplikasi web ke dalam dua bagian akses utama:

1. Jalur Halaman Publik
   a. Dashboard Publik (`/`): Menampilkan informasi utama kampus, statistik kunjungan, kartu gedung dan fasilitas, pemilih Denah 2D atau Denah 3D, pencarian lokasi, serta Tutorial dan FAQ.
   b. Pengaturan Bahasa: Tombol pemilih bahasa menerapkan kamus bahasa Indonesia atau Inggris pada komponen antarmuka React.
2. Halaman Administratif Terlindungi
   a. Halaman Masuk (`/login`): Formulir autentikasi administrator yang dilindungi oleh sesi pengguna.
   b. Panel Admin (`/admin`): Mengelola data gedung, fasilitas, program studi, dan konfigurasi denah 2D, serta menampilkan analitik dan riwayat perubahan melalui tab `Analytics` dan `Audit Log`.

### 2.3.3 Perancangan UML

Interaksi sistem dan alur pertukaran data dirancang menggunakan *Unified Modeling Language* (UML). Use Case Diagram digunakan untuk memodelkan interaksi aktor dengan fungsi sistem, Activity Diagram untuk menggambarkan alur aktivitas, dan Sequence Diagram untuk menunjukkan urutan interaksi secara lebih terperinci (Wayahdi dan Ruziq 2023).

1. Use Case Diagram
   Diagram hanya menggunakan dua aktor manusia, yaitu 'Pengguna Publik' dan 'Administrator'. Pengguna Publik mewakili sivitas akademika serta pengunjung eksternal yang melihat informasi kampus, mencari dan menavigasi lokasi, serta mengakses Tutorial, FAQ, dan bantuan. Administrator masuk ke Panel Admin untuk mengelola data kampus dan konfigurasi Denah 2D serta meninjau analitik dan riwayat perubahan. Kedua aktor berasosiasi dengan use case bersama Mengakses Data Gedung dan Fasilitas karena menggunakan sumber informasi yang sama dengan hak akses berbeda. Use case Mengelola Data Gedung, Fasilitas, Program Studi, dan Konfigurasi Denah 2D memiliki relasi `<<include>>` menuju use case bersama tersebut karena proses pengelolaan selalu memerlukan pembacaan data yang sedang dikelola. Unity WebGL dan alat pemeriksaan pada Unity Editor diperlakukan sebagai komponen internal, bukan aktor. Legenda simbol use case ditunjukkan oleh [FIGREF:diagram_use_case_legenda], sedangkan diagram use case sistem terinci pada [FIGREF:diagram_use_case].

   [FIGURE:diagram_use_case_legenda]
   [FIGCAPTION:Legenda Simbol pada Use Case Diagram]

   [FIGURE:diagram_use_case]
   [FIGCAPTION:Use Case Diagram Sistem Denah Virtual UPNVJ]

2. Activity Diagram
   Activity Diagram digunakan untuk memperlihatkan urutan aktivitas, keputusan, dan hasil pada proses pengelolaan data serta pemilihan mode denah.

   [FIGURE:diagram_activity_kelola_data]
   [FIGCAPTION:Activity Diagram Pengelolaan Data oleh Administrator]

   Proses pada [FIGREF:diagram_activity_kelola_data] menunjukkan bahwa administrator harus memiliki sesi yang valid sebelum menambah, membaca, mengubah, atau menghapus data melalui Supabase. Setiap permintaan diperiksa oleh kebijakan akses database, sedangkan riwayat perubahan dicatat oleh layanan aplikasi setelah operasi berhasil.

   [FIGURE:diagram_activity_integrasi]
   [FIGCAPTION:Activity Diagram Integrasi Denah 2D dan 3D]

   Alur pada [FIGREF:diagram_activity_integrasi] membedakan penggunaan Denah 2D dan Denah 3D. Mode 2D menghitung rute dengan algoritma A\*, sedangkan mode 3D memuat data melalui API, menerima perintah tujuan dari React, dan mengirim notifikasi kedatangan setelah navigasi selesai secara normal.

3. Sequence Diagram
   Sequence Diagram digunakan untuk menunjukkan urutan pesan antarkomponen pada proses autentikasi administrator dan sinkronisasi data dengan Unity.

   [FIGURE:diagram_sequence_autentikasi]
   [FIGCAPTION:Sequence Diagram Autentikasi Administrator]

   Urutan pada [FIGREF:diagram_sequence_autentikasi] memperlihatkan bahwa antarmuka React mengirim kredensial langsung ke Supabase Auth. Panel Admin hanya dapat dibuka setelah Supabase mengembalikan sesi yang valid; layanan API Vercel tidak menjadi perantara autentikasi tersebut.

   [FIGURE:diagram_sequence_sinkronisasi]
   [FIGCAPTION:Sequence Diagram Sinkronisasi Data Gedung dan Fasilitas dengan Unity]

   Pertukaran pesan pada [FIGREF:diagram_sequence_sinkronisasi] dimulai ketika kode lokasi diperbarui melalui Panel Admin dan disimpan ke Supabase. Unity kemudian mengambil data melalui API dan mencocokkan kode tersebut dengan objek tujuan di lingkungan 3D, sehingga React tidak perlu mengirim seluruh data gedung atau fasilitas ke Unity.

### 2.3.4 Perancangan Integrasi Keamanan dan Analitik

Perancangan pada subbab ini membahas cara aplikasi menggunakan kontrol keamanan dan layanan analitik, bukan perancangan kebijakan database oleh penulis.

1. Autentikasi dan Sesi Aplikasi
   a. Halaman login React memanggil Supabase Auth melalui adapter aplikasi dan menyimpan status sesi pada `AuthContext`.
   b. Komponen pelindung halaman (`ProtectedRoute`) hanya menampilkan Panel Admin setelah sesi tervalidasi, sedangkan proses keluar menghapus sesi melalui Supabase Auth. Penggunaan JWT pada RESTful API dapat mendukung pengelolaan sesi dan pembatasan akses (Dalimunthe et al. 2023); dalam implementasi ini, JWT diperoleh melalui Supabase Auth tanpa menetapkan algoritma penandatanganan yang tidak diverifikasi.
2. Konsumsi Kontrol Akses Database dan Audit Aplikasi
   a. React membaca dan mengubah data melalui Supabase SDK menggunakan konteks sesi pengguna.
   b. Pembatasan hak akses `anon` dan `authenticated` dilaksanakan melalui *Row Level Security* (RLS) yang dirancang Database Schema Designer (Putra et al. 2026). Pada implementasi yang diperiksa, layanan aplikasi mencatat riwayat setelah operasi tambah, baca, ubah, dan hapus (CRUD). Laporan tidak menyatakan bahwa trigger database telah aktif karena bukti tersebut tidak ditemukan pada skema yang diperiksa.
3. Integrasi Analitik dan Pembatasan Permintaan
   a. Analitik utama mencatat dan menggabungkan data `web_analytics_log` melalui Supabase, sedangkan Umami dan layanan pendukung Express tersedia sebagai jalur opsional.
   b. Layanan Express membatasi jumlah permintaan per alamat klien dalam rentang waktu yang dikonfigurasi ketika jalur opsional tersebut dijalankan.

### 2.3.5 Perancangan Pemetaan Data Integrasi

*Entity Relationship Diagram* (ERD), relasi antartabel, kebijakan RLS, dan rancangan trigger database merupakan kontribusi Database Schema Designer. Dalam lingkup System Integrator, penulis memetakan informasi yang dibutuhkan oleh antarmuka, API, dan penghubung React–Unity tanpa mengambil alih kepemilikan struktur database. Pemetaan pada subbab ini berisi informasi yang digunakan setiap komponen, bukan perancangan ulang skema database. Ringkasannya disajikan pada [TABREF:kontrak_data_integrasi].

[TABLE-ID:kontrak_data_integrasi]
[TABLECAPTION:Pemetaan Data yang Digunakan Aplikasi dan API]

[TABLE]
Sumber Data | Informasi yang Digunakan | Penggunaan dalam Lingkup Penulis
Gedung | Identitas, nama, deskripsi, lokasi, jumlah lantai, foto, dan kode lokasi Unity | Kartu informasi, pencarian, pengelolaan melalui Panel Admin, layanan data gedung, dan data yang dibaca Unity
Fasilitas | Identitas, nama, deskripsi, jenis, warna, lantai, foto, gedung induk, dan kode lokasi Unity | Daftar fasilitas, pencarian, pengelolaan melalui Panel Admin, layanan data fasilitas, dan data yang dibaca Unity
Fakultas | Identitas dan nama fakultas | Referensi pilihan fakultas pada formulir program studi; tidak tersedia sebagai tab pengelolaan terpisah
Program studi | Identitas, nama, jenjang, fakultas, dan akreditasi | Pengelolaan program studi pada Panel Admin; tidak disajikan sebagai tabel pada halaman publik
Profil administrator | Nama pengguna, nama lengkap, dan peran | Metadata profil tambahan setelah autentikasi Supabase; bukan sumber kata sandi utama
Analitik kunjungan | Kode anonim pengunjung, jalur halaman, perangkat, dan waktu kunjungan | Pencatatan kunjungan halaman dan penggabungan statistik pada analitik utama
Riwayat perubahan | Aktor, tindakan, sumber data, waktu, nilai lama, dan nilai baru | Riwayat perubahan yang hanya dapat dibaca pada Panel Admin
Konfigurasi Denah 2D | Metadata peta, simpul, jalur, penanda gedung, dan pintu masuk | Pemuatan Denah 2D, perhitungan rute A\*, dan penyuntingan konfigurasi denah pada Panel Admin
Supabase Auth | Identitas pengguna dan sesi | Proses masuk, pemeriksaan akses Panel Admin, proses keluar, dan sesi autentikasi untuk pengelolaan data
[/TABLE]

Kolom kode lokasi Unity (`unity_object_name`) menjadi penghubung data antarkomponen. Antarmuka web menggunakannya sebagai kode lokasi, API mengirimkannya kepada Unity, dan Unity memetakannya ke objek tujuan yang sesuai. Penulis menjaga konsistensi kode tersebut pada aplikasi dan API. Penataan serta pemeriksaan objek di Unity tetap menjadi kontribusi anggota terkait.

### 2.3.6 Perancangan Antarmuka

Rancangan antarmuka tidak mendokumentasikan seluruh halaman secara terpisah, melainkan memilih bukti visual yang langsung mendukung kontribusi penulis pada antarmuka web dan integrasi sistem. Pilihan ini menjaga pembahasan tetap berfokus pada alur akses denah, pencarian React, penghubung menuju Unity, dan pengelolaan konten oleh administrator.

1. Titik Masuk Denah Kampus
   Panel pada [FIGREF:ui_section_denah_kampus] menjadi titik masuk dari Dashboard Publik menuju fitur navigasi. Navigasi utama di bagian atas menyediakan akses ke Beranda, Fasilitas, Denah Kampus, pergantian bahasa, dan halaman administrator. Tiga kartu informasi menjelaskan bahwa pengguna dapat menentukan lokasi awal, mencari ruangan atau fasilitas berdasarkan gedung, serta memilih Denah 2D atau 3D. Tombol “Buka Denah Kampus” membuka pemilih mode, sedangkan informasi cache memberi tahu bahwa file 3D telah tersedia pada browser sehingga pengguna memahami kondisi pemuatan sebelum masuk ke mode Unity.

   [FIGURE:ui_section_denah_kampus]
   [FIGCAPTION:Panel Akses Denah 2D dan 3D]

2. Antarmuka Denah 3D
   Tampilan pada [FIGREF:ui_webgl_canvas] menggunakan susunan berlapis antara kanvas Unity dan komponen React. Unity menampilkan lingkungan kampus, avatar, serta minimap, sedangkan React menyediakan tombol pergantian mode, bilah pencarian lokasi, dan tombol bantuan. Bilah pencarian digunakan untuk memilih gedung atau fasilitas tanpa mengharuskan pengguna menghafal posisi objek dalam lingkungan 3D. Tombol bantuan membuka petunjuk navigasi dan informasi kontak kampus, sedangkan tombol pergantian mode mengembalikan pengguna ke pemilih Denah 2D atau 3D. Setelah tujuan dipilih, React meneruskan kode lokasi kepada Unity; pergerakan karakter, pembentukan rute, dan minimap tetap dijalankan oleh aplikasi Unity milik Engine Developer.

   [FIGURE:ui_webgl_canvas]
   [FIGCAPTION:Antarmuka Denah 3D dengan Pencarian, Minimap, dan Tombol Bantuan]

3. Pencarian dan Penentuan Rute pada Denah 2D
   Algoritma A\* merupakan metode pencarian heuristik pada graf yang memilih jalur dari simpul awal ke tujuan berdasarkan gabungan biaya perjalanan yang telah ditempuh dan perkiraan biaya menuju tujuan (Wang et al. 2022). Antarmuka pada [FIGREF:ui_search_overlay] memperlihatkan kolom pencarian, daftar hasil, label gedung, penanda lokasi, pilihan titik awal, tombol pergantian mode, dan kontrol pembesaran tampilan. Setiap hasil fasilitas disertai nama gedung induk agar pengguna dapat membedakan lokasi yang memiliki nama serupa. Pilihan “Mulai dari gedung” menetapkan posisi awal, kemudian pilihan tujuan dipetakan ke pintu masuk gedung yang terhubung dengan jaringan jalur. React menghitung rute menggunakan algoritma A\* berdasarkan simpul dan jalur yang tersimpan di Supabase, lalu menggambar hasilnya di atas denah. Dengan alur tersebut, pengguna dapat memperoleh arahan tanpa harus mengoperasikan karakter pada lingkungan 3D.

   [FIGURE:ui_search_overlay]
   [FIGCAPTION:Hasil Pencarian Lokasi pada Denah 2D]

4. Pengelolaan Fasilitas pada Panel Admin
   Tampilan pada [FIGREF:mockup_dashboard_admin] memperlihatkan halaman administrator yang telah melewati autentikasi. Navigasi modul menyediakan Gedung, Fasilitas, Program Studi, Denah 2D, Analytics, dan Audit Log. Pada modul Fasilitas, administrator dapat menambah data, mencari berdasarkan nama fasilitas atau gedung, serta menyaring data menurut tipe, gedung, dan lantai. Tabel menampilkan nama dan deskripsi ringkas, kode lokasi Unity, tipe fasilitas, gedung induk, lantai, serta tindakan ubah dan hapus. Operasi tersebut dijalankan oleh layanan React melalui Supabase SDK, sedangkan hasil setiap operasi ditampilkan kembali melalui notifikasi dan pemuatan ulang data.

   Tangkapan layar pada [FIGREF:mockup_dashboard_admin] memperlihatkan 331 fasilitas pada database Supabase aktif saat gambar diambil. Angka tersebut tidak disamakan dengan 311 data pada seed final karena penerapan ulang seed ke Supabase belum diverifikasi. Rincian autentikasi, pemanggilan Supabase SDK, dan pembatasan operasi berdasarkan RLS dijelaskan pada Subbab 3.2 sehingga tidak diperlukan tangkapan layar terpisah untuk setiap formulir CRUD.

   [FIGURE:mockup_dashboard_admin]
[FIGCAPTION:Halaman Pengelolaan Fasilitas pada Panel Admin]

## 2.4 Rencana Pengujian Proyek

### 2.4.1 Pengujian API dan Integrasi Data

Pengujian API dirancang untuk memeriksa fungsi Vercel Serverless Functions dan kesesuaian responsnya dengan data Supabase sebagai berikut:

1. Memastikan endpoint `/api/buildings`, `/api/rooms`, `/api/unity/data`, dan `/api/unity/names` mengembalikan status serta struktur JSON sesuai spesifikasi ketika data tersedia.
2. Memastikan `/api/unity/data` memisahkan larik `gedung` dan `fasilitas`, sedangkan `/api/unity/names` hanya mengembalikan daftar kode lokasi (`unityObjectNames`) yang valid.
3. Memastikan metode selain `GET` atau `OPTIONS` ditolak pada API yang hanya menyediakan data dan kegagalan akses menghasilkan respons kesalahan tanpa memaparkan kredensial.
4. Memastikan `/api/health` mengembalikan status layanan yang dapat digunakan untuk pemeriksaan operasional.
5. Menguji permintaan data dan CRUD React melalui Supabase SDK menggunakan sesi terautentikasi serta memastikan kegagalan RLS ditampilkan sebagai kesalahan aplikasi. Pengujian ini tidak menggunakan layanan POST, PUT, atau DELETE pada REST API.

### 2.4.2 Pengujian Web dan Operasional

Lighthouse merupakan alat audit otomatis yang mengevaluasi Kinerja, Aksesibilitas, Praktik Terbaik, dan SEO untuk membantu mengidentifikasi area perbaikan, tetapi hasilnya tidak menggantikan pemeriksaan manual maupun evaluasi pengalaman pengguna (McGill et al. 2023). Pemeriksaan aksesibilitas pada proyek ini juga mengacu pada WCAG 2.2 tanpa menganggap skor otomatis sebagai bukti kepatuhan penuh (W3C 2024).

Pengujian yang langsung berkaitan dengan kontribusi penulis direncanakan sebagai berikut:

1. Vitest dan React Testing Library digunakan untuk menguji fungsi pendukung, penghubung autentikasi, komponen dialog, penerjemahan antarmuka, perlindungan data, serta pemuatan awal WebGL.
2. Pengujian integrasi digunakan untuk memeriksa layanan kesehatan sistem, data gedung atau fasilitas, struktur data Unity, dan kondisi kegagalan akses Supabase.
3. Alur pada browser diperiksa melalui *Black Box Testing* dan UAT. Playwright ditempatkan sebagai rencana pengujian lanjutan karena belum tersedia rangkaian pengujian menyeluruh yang dapat dilaporkan.
4. Lighthouse digunakan pada hasil build produksi melalui server pratinjau lokal untuk mengukur Kinerja, Aksesibilitas, Praktik Terbaik, dan SEO pada simulasi smartphone serta komputer desktop. Laporan JSON Lighthouse menjadi sumber angka, sedangkan hasil otomatis dibedakan dari pemeriksaan manual dan data pengguna nyata.
5. Pemeriksaan lingkungan produksi memastikan React SPA, layanan API, pengalihan halaman, header keamanan, tipe konten, cache aset WebGL, dan endpoint status layanan tersedia sesuai konfigurasi.

### 2.4.3 Pengujian Fungsional (Black Box Testing)

Pengujian fungsional sistem menggunakan metode *Black Box Testing* untuk menguji 24 skenario pada Panel Admin, Dashboard Publik, API, dan integrasi navigasi Unity. Pengujian ini berfokus pada persyaratan fungsional perangkat lunak tanpa meninjau struktur kode internal program (Maulida et al. 2025). Cakupan skenario meliputi:

1. Autentikasi administrator, perlindungan RLS, dan pencatatan riwayat perubahan.
2. Operasi tambah, baca, ubah, dan hapus data, pemeriksaan formulir, serta fitur tabel pada Panel Admin.
3. Penggabungan kategori, pencarian, pergantian bahasa, penanganan kondisi pemuatan atau kesalahan, dan responsivitas Dashboard Publik.
4. Endpoint data denah, jembatan komunikasi React ke Unity, navigasi NavMesh, ketahanan `unity_object_name`, interupsi rute, dan pemuatan awal Unity WebGL.

### 2.4.4 User Acceptance Test

*User Acceptance Test* (UAT) dirancang untuk mengukur tingkat penerimaan dan penilaian peserta terhadap sistem yang dikembangkan. UAT dilaksanakan secara tertutup dengan peserta yang dipilih berdasarkan keterlibatan dan kemampuannya dalam mengevaluasi proyek, yaitu dua dosen penguji, dua dosen pembimbing, dan satu perwakilan Humas UPNVJ. Pengujian ini tidak melibatkan sampel mahasiswa baru, orang tua atau wali, maupun pengunjung eksternal. Humas ditempatkan sebagai mitra pengguna, tetapi penilaian satu perwakilan tidak digunakan untuk mengklaim persetujuan formal atau mewakili seluruh pengguna UPNVJ (Aliyah et al. 2025).

Pengukuran dilakukan menggunakan skala Likert 1 sampai 5 melalui dua kuesioner terstruktur. Instrumen evaluasi Dashboard Publik memuat sembilan pernyataan dan instrumen evaluasi Panel Admin memuat sebelas pernyataan. Setiap instrumen diisi oleh empat peserta, dengan total lima peserta unik karena sebagian peserta mengevaluasi kedua instrumen. Istilah Dashboard Publik merujuk pada bagian aplikasi yang dinilai, bukan asal peserta pengujian. Persentase penerimaan dihitung dari perbandingan skor aktual terhadap skor maksimum, sedangkan masukan terbuka digunakan sebagai dasar penyusunan tindak lanjut setelah pengujian.

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
Pengguna Publik | Memberikan data kebutuhan awal melalui kuesioner dan menggunakan Dashboard Publik serta Denah 2D atau 3D | Antarmuka informasi, pencarian lokasi, petunjuk penggunaan, dan alternatif navigasi berbasis web
UPA TIK UPNVJ | Menjadi pihak koordinasi teknis untuk batas akses data, kemungkinan integrasi institusional, wawancara, dan penyerahan pakta integritas | Spesifikasi teknis dan batas penggunaan data tanpa mengklaim UPA TIK sebagai mitra pengguna atau penerima sistem
Tim Pengembang | Menyediakan komponen database, aset, aplikasi Unity, aplikasi web, dan deployment sesuai pembagian peran | Hasil kerja lintas komponen yang terhubung melalui mekanisme integrasi dan deployment yang terdokumentasi
[/TABLE]

## 3.2 Metode Implementasi

Implementasi sistem dalam proyek ini merupakan pelaksanaan metodologi Prototyping yang dijelaskan pada Subbab 2.3.1 (Syarif dan Risdiansyah 2024). Tahap pengumpulan kebutuhan menghasilkan sasaran pengguna, fungsi web, batas data, dan kontrak integrasi. Tahap perancangan cepat menghasilkan rancangan antarmuka, API, Denah 2D, serta hubungan React–Unity. Tahap pembangunan menghasilkan komponen dari setiap peran yang kemudian diintegrasikan. Versi sistem yang telah terintegrasi dievaluasi melalui pemeriksaan komponen, Black Box Testing, dan UAT, lalu diperbaiki berdasarkan temuan.

Dalam lingkup penulis, siklus tersebut menghasilkan Dashboard Publik, Panel Admin, Denah 2D, REST API, integrasi Supabase, pemuat Unity WebGL, penghubung navigasi, serta konfigurasi deployment. Komponen data dan aset dari Database Schema Designer serta file hasil build dari Engine Developer menjadi masukan integrasi, sedangkan hasil evaluasi dikembalikan kepada pemilik komponen untuk diperbaiki sesuai tanggung jawabnya. Subbab ini menguraikan cara komponen dalam lingkup penulis dibangun dan dihubungkan, sedangkan bukti keluaran serta hasil akhirnya disajikan pada Subbab 3.4.

### 3.2.1 Implementasi Layanan Server

Layanan server yang menjadi tanggung jawab penulis adalah REST API berbasis Node.js pada folder `api/` dan dijalankan sebagai Vercel Serverless Functions. API ini hanya menerima permintaan pengambilan data. React tidak memakai layanan tersebut untuk masuk atau melakukan operasi CRUD utama karena kedua proses itu dilakukan langsung melalui Supabase SDK. API digunakan oleh aplikasi Unity, alat bantu Unity Editor, endpoint status layanan, dan integrator eksternal yang memerlukan akses data melalui HTTP.

Setiap fungsi API menerapkan CORS, menerima metode `GET` dan `OPTIONS`, serta menolak metode lain dengan status 405. Fungsi tersebut membuat klien Supabase dari variabel lingkungan, lalu mengembalikan data JSON atau status 500 apabila permintaan data gagal. Potongan implementasi `/api/unity/data` berikut menunjukkan pengambilan data gedung dan fasilitas secara bersamaan tanpa memuat kredensial:

```javascript
const [gedungResult, fasilitasResult] = await Promise.all([
  supabase
    .from("gedung")
    .select(
      "id, nama_gedung, deskripsi_gedung, lokasi, " +
        "jumlah_lantai, unity_object_name",
    )
    .order("id", { ascending: true }),
  supabase
    .from("fasilitas")
    .select(
      "id, nama_fasilitas, deskripsi_fasilitas, tipe_fasilitas, " +
        "id_gedung, lantai, foto_url, unity_object_name",
    )
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

Spesifikasi endpoint pada implementasi yang diperiksa diringkas pada [TABREF:kontrak_endpoint_api].

[TABLE-ID:kontrak_endpoint_api]
[TABLECAPTION:Spesifikasi Endpoint API pada Vercel Serverless Functions]

[TABLE]
Endpoint | Respons Utama | Konsumen atau Tujuan
`GET /api/health` | objek yang memuat status, pesan, dan waktu pemeriksaan | Pemantauan status layanan
`GET /api/buildings` | daftar gedung beserta fasilitas terkait | Integrator eksternal dan kesesuaian spesifikasi API
`GET /api/rooms` | daftar fasilitas beserta data gedung | Integrator eksternal dan kesesuaian spesifikasi API
`GET /api/unity/data` | objek dengan larik `gedung` dan `fasilitas` | Komponen data Unity (`BuildingDatabase`) ketika Unity dijalankan
`GET /api/unity/names?type=gedung` atau `GET /api/unity/names?type=fasilitas` | larik kode lokasi (`unityObjectNames`) | Alat pemeriksaan sinkronisasi (`DatabaseSyncChecker`) pada Unity Editor
[/TABLE]

Klien Supabase pada fungsi Vercel menggunakan URL proyek dan kunci publik dari variabel lingkungan. Kunci dengan hak akses tinggi tidak digunakan pada browser maupun fungsi yang menyediakan data. Skema, relasi, dan RLS tetap menjadi tanggung jawab Database Schema Designer. Kontribusi penulis berada pada pemilihan kolom data, konsistensi bentuk respons, pembatasan metode HTTP, CORS, dan penanganan kesalahan.

### 3.2.2 Implementasi Antarmuka Web

Antarmuka web diimplementasikan sebagai SPA menggunakan React 19, TypeScript, dan Vite 7. Komponen konteks aplikasi mengatur bahasa, autentikasi, notifikasi, dan perpindahan halaman. Halaman utama memuat Dashboard Publik, sedangkan halaman admin hanya dapat dibuka setelah sesi pengguna dinyatakan valid. Komponen berukuran besar dimuat ketika diperlukan agar tampilan awal tidak menunggu seluruh modul.

1. Dashboard Publik
   Dashboard Publik mengambil data melalui Supabase SDK dan menyajikan informasi kampus, statistik kunjungan, kartu gedung atau fasilitas, tutorial dan FAQ, pencarian lokasi, serta pemilih Denah 2D atau 3D. Konteks dashboard mengatur kondisi pemuatan, kesalahan, cache, dan pemuatan ulang data.
2. Pencarian Lokasi
   Fitur pencarian mengambil data gedung beserta fasilitas terkait secara langsung dari Supabase. Pencocokan dilakukan terhadap nama gedung, nama fasilitas, deskripsi, lokasi, dan nama gedung induk. Fuse.js digunakan agar pencarian tetap dapat menemukan hasil ketika kata yang dimasukkan tidak sama persis. Istilah singkat yang umum, seperti FIK, FEB, perpus, dan rektorat, juga dihubungkan dengan bentuk lengkapnya. Karena deskripsi fasilitas ikut diperiksa, istilah alternatif yang dicantumkan pada deskripsi dapat membantu pengguna menemukan nama ruang yang kurang dikenal.

   Setiap hasil menampilkan nama lokasi dan, untuk fasilitas, nama gedung induknya. Data hasil pencarian menyimpan dua tujuan yang berbeda: identitas gedung untuk perhitungan rute pada Denah 2D dan kode lokasi Unity untuk navigasi pada Denah 3D. Jika fasilitas belum memiliki kode lokasi tersendiri, sistem menggunakan kode gedung induknya sebagai tujuan 3D. Antarmuka dapat dioperasikan melalui papan ketik menggunakan tombol panah, Enter, dan Escape. Tampilan hasil pencarian pada [FIGREF:ui_search_overlay] memperlihatkan bahwa satu pilihan lokasi dapat digunakan tanpa mengubah istilah yang dilihat pengguna, meskipun mekanisme navigasi 2D dan 3D berbeda.
3. Panel Admin
   Konteks autentikasi mempertahankan sesi dan mengarahkan pengguna yang valid ke Panel Admin. Operasi CRUD gedung, fasilitas, program studi, dan konfigurasi Denah 2D dilakukan melalui layanan aplikasi yang berkomunikasi langsung dengan Supabase. Validasi formulir, konfirmasi penghapusan, notifikasi, dan pembaruan data memberikan umpan balik kepada administrator.
4. Denah 2D
   Mode 2D memuat konfigurasi peta aktif, simpul, jalur, penanda gedung, dan pintu masuk dari Supabase. Setelah pengguna menentukan titik awal dan tujuan, antarmuka mencari pintu masuk gedung, menjalankan algoritma A\*, dan menggambar jalur sebagai SVG di atas gambar denah. Penyunting pada Panel Admin digunakan untuk mengatur seluruh unsur tersebut.
5. Pemuatan Unity WebGL
   File hasil build Unity v0.8.6.1 dimuat menggunakan loader bawaan Unity tanpa pustaka `react-unity-webgl`. React menyiapkan kanvas dan lokasi file data, kerangka kerja, serta WebAssembly, kemudian menyimpan objek Unity yang telah dimuat untuk keperluan komunikasi. Potongan berikut berasal dari implementasi aktif:

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

6. Pemuatan Awal dan Penanganan Kondisi
   Pemuatan awal menjadwalkan pengunduhan file Unity secara berurutan dengan prioritas rendah setelah halaman stabil. Proses ini dilewati pada smartphone, mode penghematan data, koneksi lambat, dan GitHub Pages. Ketika pengguna memulai mode 3D, antarmuka memeriksa dukungan WebGL, menampilkan kemajuan dan pesan kesalahan, serta menghentikan objek Unity ketika pengguna meninggalkan halaman. Penanganan pada sisi web merupakan kontribusi penulis; joystick, NavMesh, dan kontrol di dalam Unity tetap menjadi kontribusi 3D Simulator dan Engine Developer.

### 3.2.3 Implementasi Integrasi Antarmuka Web, Layanan Server, dan Unity WebGL

Sebagai System Integrator, penulis menghubungkan React, Supabase, Vercel Serverless Functions, dan file hasil build Unity WebGL melalui mekanisme yang berbeda untuk autentikasi, pertukaran data, serta perintah navigasi. Pemisahan ini mencegah antarmuka web, API, dan Unity menggunakan jalur data yang keliru.

1. Autentikasi dan Pengelolaan Data
   Halaman login React berkomunikasi langsung dengan Supabase Auth dan menerima sesi pengguna. Setelah sesi dinyatakan valid, pengguna dapat membuka Panel Admin. Operasi CRUD, konfigurasi Denah 2D, dan pencatatan riwayat perubahan dilakukan oleh layanan aplikasi melalui Supabase SDK sesuai RLS. Kontribusi penulis mencakup pengelolaan sesi, formulir, layanan data, penanganan respons, cache, dan umpan balik antarmuka.
2. Penyediaan Data melalui REST API
   Vercel Serverless Functions menyediakan respons JSON melalui metode GET. Layanan `/api/unity/data` menyajikan data gedung dan fasilitas ketika Unity dijalankan, sedangkan `/api/unity/names` menyajikan daftar kode lokasi untuk alat pemeriksaan sinkronisasi pada Unity Editor. Antarmuka React tidak bergantung pada `/api/buildings` atau `/api/rooms` untuk alur utamanya karena mengambil data langsung melalui Supabase SDK.
3. Penarikan Data Mandiri oleh Unity
   Ketika Unity WebGL dimulai, komponen data yang dikembangkan 3D Simulator dan Engine Developer memanggil `GET /api/unity/data`. Nama tampilan dan kode lokasi disimpan selama aplikasi berjalan untuk mendukung navigasi. React tidak mengirim data gedung atau fasilitas melalui mekanisme pengiriman perintah. Alur ini dipetakan pada [FIGREF:diagram_sequence_sinkronisasi].
4. Pengiriman Perintah Navigasi dari React
   Komponen pencarian memisahkan nama yang dilihat pengguna, identitas gedung untuk Denah 2D, dan kode lokasi untuk Denah 3D. Identitas gedung digunakan untuk menghitung rute A\*, sedangkan kode lokasi dikirim kepada Unity untuk memulai navigasi. Perintah berhenti dikirim apabila pengguna membatalkan rute.
5. Validasi Penyelesaian Navigasi
   Unity hanya mengirim notifikasi kedatangan setelah pengguna benar-benar mencapai tujuan. Pembatalan navigasi, pergantian titik awal, atau tujuan yang tidak ditemukan tidak dianggap sebagai kondisi tiba. React membandingkan kode lokasi yang diterima dengan tujuan yang sedang aktif. Notifikasi hanya ditampilkan apabila keduanya sesuai; data kosong, tidak valid, atau berbeda diabaikan.
6. Deployment dan Batas Tanggung Jawab
   Penulis mengelola deployment React SPA, Vercel Serverless Functions, variabel lingkungan, header, cache aset, serta file hasil build Unity WebGL yang diberikan oleh 3D Simulator dan Engine Developer. Database Schema Designer tetap bertanggung jawab atas ERD, skema database, RLS, dan rancangan trigger database, sedangkan 3D Asset Designer bertanggung jawab atas aset 3D dan hierarki `Pointer`. 3D Simulator dan Engine Developer bertanggung jawab atas pengambilan data di Unity, penerimaan perintah navigasi, alat pemeriksaan sinkronisasi, navigasi, optimasi, dan proses build Unity WebGL. Implementasi web yang diperiksa mencatat riwayat perubahan melalui layanan aplikasi dan tidak membuktikan bahwa trigger database telah aktif.

### 3.2.4 Implementasi Deployment, Pengoperasian Layanan, dan Kesiapan Integrasi Institusional

Pada tahap implementasi saat ini, deployment React SPA, Vercel Serverless Functions, dan file hasil build Unity WebGL v0.8.6.1 dilakukan melalui Vercel. Supabase menyediakan data dan autentikasi. Analitik utama juga menggunakan Supabase, sedangkan Express dan Umami tersedia sebagai pilihan pengoperasian.

1. Deployment dan Konfigurasi Layanan
   Penulis mengelola variabel lingkungan, konfigurasi domain, jalur cadangan SPA, header keamanan, cache, serta tipe konten file hasil build Unity WebGL. Versi v0.8.6.1 yang telah dibangun oleh 3D Simulator dan Engine Developer ditempatkan pada folder versi di layanan web; proses build dan optimasi Unity tidak termasuk dalam kontribusi penulis.
2. Pengoperasian dan Pemantauan
   Pengoperasian layanan mencakup `/api/health`, pemeriksaan respons aset WebGL, pengaturan cache, serta pembatasan jumlah permintaan pada layanan Express. Docker Compose Umami dan perantara Express dipertahankan sebagai analitik opsional, tetapi bukan bagian wajib dari analitik utama.
3. Kesiapan Integrasi Institusional
   Penggunaan Vercel pada tahap ini merupakan pilihan hosting proyek, bukan ketetapan arsitektur permanen. Apabila sistem kelak diintegrasikan dengan infrastruktur kampus, penyesuaian dapat dilakukan pada domain, variabel lingkungan, pengelolaan kunci rahasia dan kredensial, konektivitas API, serta mekanisme identitas yang disetujui institusi. Spesifikasi REST API, struktur respons JSON, dan penghubung React–Unity dipertahankan agar perubahan platform hosting tidak mengubah perilaku antarkomponen. Integrasi institusional tersebut belum diimplementasikan dan menjadi rencana pengembangan lanjutan.

## 3.3 Konfigurasi dan Ketentuan Operasional Sistem

### 3.3.1 Variabel Lingkungan dan Konsistensi Kode Lokasi

Konfigurasi dipisahkan antara nilai yang boleh digunakan browser dan rahasia khusus server. Pemetaan pada [TABREF:konfigurasi_environment] mencegah kunci dengan hak akses tinggi atau kredensial Umami masuk ke berkas antarmuka web.

[TABLE-ID:konfigurasi_environment]
[TABLECAPTION:Konfigurasi Variabel Lingkungan]

[TABLE]
Lingkungan | Variabel Utama | Penggunaan
Antarmuka React di browser dan fungsi API Vercel | `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` | Membuat klien Supabase dengan hak yang dibatasi kebijakan akses data
Layanan Express | `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `PORT`, `FRONTEND_URL` | Koneksi server, pemilihan port, dan domain asal yang diizinkan; kunci khusus server tidak boleh dimasukkan ke browser
Umami opsional | `UMAMI_API_URL`, `UMAMI_WEBSITE_ID`, `UMAMI_API_USER`, `UMAMI_API_PASSWORD`, `UMAMI_APP_SECRET` | Autentikasi layanan Express ke Umami yang dihosting mandiri
Vite dan hosting | `BASE_URL` serta jalur versi file hasil build | Penentuan lokasi aset statis, denah, dan loader Unity WebGL
[/TABLE]

Kode lokasi Unity merupakan bagian integrasi lintas repositori yang paling sensitif. Nilai ini disimpan pada data gedung atau fasilitas, dikirim melalui `/api/unity/data`, dan digunakan komponen pencarian untuk menentukan tujuan navigasi. Fasilitas yang tidak memiliki kode sendiri dapat menggunakan target gedung induknya. Perubahan kode harus dikoordinasikan dengan objek tujuan pada proyek Unity dan diperiksa sebelum file hasil build WebGL baru di-deploy.

Versi folder hasil build juga menjadi acuan deployment. Pada kode sumber yang ditinjau 21 Juli 2026, versi aktif adalah v0.8.6.1 sehingga loader React, pemuatan awal, dan `vercel.json` harus menunjuk ke folder versi yang sama.

### 3.3.2 Analitik dan Layanan Pendukung Express

Implementasi analitik berada dalam masa transisi dan didokumentasikan berdasarkan bagian yang benar-benar aktif. Layanan pencatatan menyimpan kunjungan halaman ke `web_analytics_log`, sedangkan layanan React membaca tabel yang sama untuk membentuk statistik. Dengan demikian, Dashboard Publik dan Panel Admin dapat menampilkan analitik tanpa menjalankan Express atau Umami.

Express pada port 3001 tetap tersedia sebagai layanan opsional. Layanan ini membatasi asal dan jumlah permintaan menjadi paling banyak 100 permintaan per alamat klien per menit, serta menyediakan `/api/analytics/*` untuk berkomunikasi dengan API Umami. Docker Compose menjalankan Umami dan database internalnya. Jalur tersebut dipertahankan sebagai alternatif yang dihosting mandiri dan bukan jalur wajib antarmuka web saat ini.

Pemisahan ini juga memperjelas batas kontribusi DevOps. Penulis mengelola konfigurasi dan kesiapan operasional Express/Umami, tetapi data analitik yang tampil pada antarmuka aktif berasal dari Supabase. Pada pengembangan berikutnya, kedua jalur perlu disatukan agar definisi dan pengelolaan data analitik tidak berbeda.

### 3.3.3 Konfigurasi Hosting Vercel dan Aset WebGL

File hasil build Unity WebGL v0.8.6.1 dibuat oleh 3D Simulator dan Engine Developer lalu diserahkan kepada penulis untuk ditempatkan pada folder versi layanan web. Pemanfaatan fungsi *serverless* pada lapisan hosting memisahkan eksekusi fungsi dari pengelolaan server fisik, tetapi konfigurasi layanan, keamanan, dan integrasi backend tetap harus dikendalikan (Li et al. 2022). Vercel digunakan karena mendukung Vercel Serverless Functions, pengalihan jalur SPA, serta header tipe konten, kompresi, dan cache yang diperlukan aset Unity. Potongan konfigurasi berikut menunjukkan pola header untuk versi aktif:

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

GitHub Pages tetap dapat menyajikan aplikasi React, tetapi pilihan tur 3D dinonaktifkan pada domain `github.io` karena layanan tersebut tidak menyediakan konfigurasi header WebGL yang digunakan proyek. Denah 2D tetap tersedia sebagai pilihan cadangan. Jika sistem dipindahkan ke infrastruktur kampus, server tujuan harus menyediakan pengalihan SPA, layanan API, HTTPS, header aset, cache, variabel lingkungan, serta pengelolaan kunci rahasia dan kredensial sebelum domain dialihkan.

## 3.4 Laporan Implementasi Proyek

Subbab ini menyajikan bukti dan hasil implementasi yang metodenya telah diuraikan pada Subbab 3.2, mencakup catatan kegiatan serta hasil pada antarmuka web, layanan server, integrasi sistem, dan DevOps.

### 3.4.1 Catatan Pelaksanaan Proyek

Ringkasan aktivitas pada [TABREF:logbook_implementasi] disusun berdasarkan bukti yang dapat ditelusuri pada repositori aplikasi, konfigurasi deployment, dan hasil pengujian. Kolom terakhir tidak menggunakan klaim persetujuan pemangku kepentingan yang tidak dilengkapi bukti formal.

[TABLE-ID:logbook_implementasi]
[TABLECAPTION:Catatan Pelaksanaan Proyek]

[TABLE]
Rentang Kegiatan | Aktivitas | Kontribusi Penulis | Bukti
Tahap kebutuhan dan desain | Analisis pengguna, arsitektur informasi, UML, dan antarmuka | Merumuskan kebutuhan aplikasi, API, penghubung integrasi, deployment, serta rancangan Dashboard Publik dan Panel Admin | Draf kebutuhan, diagram arsitektur, diagram alur, dan rancangan antarmuka
Tahap layanan server dan data aplikasi | Implementasi fungsi Vercel, autentikasi, layanan data, dan pengelolaan data | Membuat layanan pengambilan data, mengintegrasikan autentikasi dan pengelolaan data Supabase, serta menangani respons dan cache | Folder `api/`, modul autentikasi, layanan Supabase, dan spesifikasi API
Tahap antarmuka web | Implementasi React SPA, Denah 2D, loader Unity, pencarian, dan Panel Admin | Membuat halaman, komponen antarmuka, perhitungan A\*, loader Unity, dan penyunting konfigurasi peta | Komponen React, pemuatan awal, layanan peta, dan empat bukti antarmuka terpilih
Tahap integrasi dan DevOps | Sinkronisasi data dan deployment file hasil build | Menghubungkan identitas gedung dan kode lokasi Unity, memasang file versi v0.8.6.1, serta mengatur variabel lingkungan, header, cache, dan pemantauan layanan | `vercel.json`, folder versi, fungsi API, dan hasil pemeriksaan jaringan browser
Tahap evaluasi | Pengujian web, Black Box, Lighthouse, dan UAT | Mengumpulkan bukti pengujian sesuai batas kontribusi serta mencatat keterbatasan hasil | Catatan hasil pemeriksaan web, dokumen Black Box, laporan Lighthouse, dan file UAT
[/TABLE]

### 3.4.2 Hasil dan Bukti Implementasi Layanan Server

Layanan API diimplementasikan pada Vercel Serverless Functions. Struktur respons `/api/unity/data` yang dibentuk fungsi dan digunakan Unity saat dijalankan adalah sebagai berikut. Nilai data disamarkan karena bagian ini menjelaskan struktur respons, bukan menyalin data produksi.

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

Respons pada lingkungan produksi dalam [FIGREF:api_test_unity_data] menunjukkan bahwa `GET /api/unity/data` memperoleh status `200 OK` dan mengembalikan objek JSON dengan larik `gedung`. Data yang terlihat memuat identitas, nama, deskripsi, lokasi, jumlah lantai, dan kode lokasi Unity, sehingga bentuk respons sesuai dengan struktur yang digunakan aplikasi Unity. Waktu 2,86 detik dan ukuran 12,24 kB merupakan hasil satu pemeriksaan manual, bukan tolok ukur kinerja untuk seluruh kondisi jaringan.

[FIGURE:api_test_unity_data]
[FIGCAPTION:Respons Endpoint Data untuk Unity pada Lingkungan Produksi]

### 3.4.3 Hasil dan Bukti Implementasi Antarmuka Web

Antarmuka React SPA berhasil melalui proses build dan diperiksa pada 21 Juli 2026. Empat bukti antarmuka inti pada Subbab 2.3.6 diambil ulang dari aplikasi setelah revisi agar tidak mencampurkan tampilan lama dengan implementasi aktif. Gambar dipilih secara selektif agar pembahasan tetap berfokus pada fitur utama.

1. Dashboard Publik menyediakan informasi kampus, tutorial dan FAQ, pemilih Denah 2D atau 3D, serta pencarian lokasi. Mode 2D menghitung rute A\*, sedangkan mode 3D mengirim kode lokasi kepada Unity.
2. Loader React menampilkan kemajuan dan pilihan pemulihan, menyesuaikan ketajaman tampilan, meneruskan tipe perangkat, serta menghentikan Unity ketika pengguna meninggalkan halaman.
3. Panel Admin menyediakan halaman terlindungi untuk CRUD gedung, fasilitas, program studi, dan konfigurasi Denah 2D, serta tab analitik dan audit.
4. Integrasi menggunakan loader bawaan Unity dan objek Unity yang telah dimuat pada React, tanpa pustaka `react-unity-webgl`.
5. Tangkapan layar Panel Admin mencatat 331 fasilitas pada database Supabase aktif, sedangkan pembersihan berkas data awal menghasilkan 311 data. Perbedaan tersebut menunjukkan bahwa berkas akhir belum terbukti diterapkan kembali ke database aktif. Oleh karena itu, tangkapan layar pencarian tidak digunakan untuk menyatakan bahwa penambahan kata pencarian pada R01 sudah tersedia pada aplikasi aktif.

### 3.4.4 Hasil dan Bukti Deployment serta Pengoperasian Layanan

Layanan web menggunakan Vercel untuk React SPA, file hasil build Unity WebGL, dan Vercel Serverless Functions. Konfigurasi pada Subbab 3.3.3 menunjukkan pemetaan tipe konten, kompresi Brotli, cache jangka panjang, header keamanan, dan pengalihan SPA. Endpoint `/api/health` tersedia untuk memeriksa status layanan, sedangkan Express dan Umami tetap merupakan jalur opsional.

Pemeriksaan operasional pada [FIGREF:api_test_health] menunjukkan bahwa `GET /api/health` memperoleh status `200 OK` dan mengembalikan `success: true`, status `OK`, pesan `Server is running`, serta waktu respons. Bukti tersebut merupakan pemeriksaan manual pada lingkungan yang dipilih melalui aplikasi penguji API dan tidak diperlakukan sebagai pemantauan ketersediaan berkelanjutan.

[FIGURE:api_test_health]
[FIGCAPTION:Hasil Pemeriksaan Endpoint Kesehatan Layanan pada Lingkungan Produksi]

Pemeriksaan jaringan browser terhadap tiga file utama hasil build v0.8.0 menunjukkan bahwa seluruh permintaan memperoleh status 200. Hasil satu kali pengamatan tersebut ditranskripsikan pada [TABREF:webgl_network_loading] dan tidak digunakan sebagai tolok ukur untuk semua perangkat atau kondisi jaringan. Pengamatan dilakukan sebelum versi diperbarui ke v0.8.6.1 sehingga ukuran dan waktu pada tabel tidak diterapkan pada build terbaru.

[TABLE-ID:webgl_network_loading]
[TABLECAPTION:Observasi Pemuatan Aset Utama Unity WebGL v0.8.0]

[TABLE]
Aset | Status | Ukuran Transfer yang Ditampilkan | Waktu yang Ditampilkan
`v0.8.0.framework.js.unityweb` | 200 | 72,5 kB | 351 ms
`v0.8.0.wasm.unityweb` | 200 | 6.528 kB | 1,95 detik
`v0.8.0.data.unityweb` | 200 | 76.864 kB | 15,92 detik
[/TABLE]

Data tersebut menunjukkan bahwa file data merupakan komponen transfer terbesar pada pengamatan yang dilakukan. Karena hasil hanya berasal dari satu kondisi browser, evaluasi kinerja perlu membedakan ukuran transfer, waktu unduh, dekompresi, inisialisasi Unity, dan kondisi cache. Apabila sistem dipindahkan ke infrastruktur UPNVJ, penyesuaian dapat dipusatkan pada domain, kunci rahasia dan kredensial, konektivitas layanan, header aset, serta kebijakan identitas tanpa mengubah spesifikasi REST API atau komunikasi React–Unity.

## 3.5 Hasil Pengujian Proyek

### 3.5.1 Pengujian Web dan API

Pemeriksaan teknis pada 21 Juli 2026 menunjukkan bahwa ESLint, pengujian unit dan komponen, serta build produksi aplikasi web berhasil dijalankan. Hasilnya dirangkum pada [TABREF:hasil_pengujian_web].

[TABLE-ID:hasil_pengujian_web]
[TABLECAPTION:Hasil Verifikasi Teknis Aplikasi Web]

[TABLE]
Pemeriksaan | Hasil Terverifikasi | Batas Interpretasi
ESLint | Lulus | Tidak ditemukan kesalahan berdasarkan aturan pemeriksaan kode yang digunakan
Vitest dan React Testing Library | 13 file pengujian dan 129 pengujian lulus | Mencakup fungsi pendukung, modul penghubung autentikasi, dialog, alih bahasa, perlindungan data, komponen, serta 11 pengujian notifikasi kedatangan; bukan pengujian internal Unity
Build produksi | `tsc -b` dan Vite build lulus | Pemeriksaan tipe dan penyusunan berkas aplikasi berhasil; peringatan data browser tidak termasuk kesalahan proyek
Playwright | Belum tersedia sebagai rangkaian hasil | Alur browser masih dibuktikan melalui Black Box dan UAT; tidak ada jumlah pengujian menyeluruh dari antarmuka hingga layanan yang diklaim
[/TABLE]

Selain pengujian otomatis, empat pemeriksaan manual dijalankan melalui aplikasi penguji API terhadap lingkungan produksi dan Supabase. Hasilnya dirangkum pada [TABREF:hasil_pengujian_api_deployment]. Status lulus ditentukan berdasarkan kesesuaian hasil aktual dengan hasil yang diharapkan. Oleh karena itu, respons `401 Unauthorized` ketika perubahan data dilakukan tanpa autentikasi menunjukkan bahwa kontrol akses bekerja, bukan bahwa layanan gagal.

[TABLE-ID:hasil_pengujian_api_deployment]
[TABLECAPTION:Hasil Pengujian Manual API dan Integrasi Supabase]

[TABLE]
Skenario | Hasil yang Diharapkan | Hasil Aktual | Status
`GET /api/health` | HTTP 200 dan status layanan dapat dibaca | HTTP 200; `success: true`, status `OK`, pesan layanan, dan waktu pemeriksaan tersedia | Lulus
`GET /api/unity/data` | HTTP 200 dengan objek `gedung` dan `fasilitas` sesuai kebutuhan Unity saat dijalankan | HTTP 200; respons JSON memuat data gedung beserta kode lokasi dan struktur respons yang ditetapkan | Lulus
`GET /api/unity/names` | HTTP 200 dengan daftar kode lokasi (`unityObjectNames`) untuk Unity Editor | HTTP 200; daftar kode lokasi Unity diterima | Lulus
`POST /rest/v1/fasilitas` tanpa autentikasi | Perubahan data ditolak oleh kebijakan akses | HTTP 401; kode PostgreSQL `42501` menyatakan data melanggar kebijakan keamanan tingkat baris | Lulus
[/TABLE]

Respons pada [FIGREF:api_test_unity_names] menunjukkan bahwa `GET /api/unity/names` memperoleh status `200 OK` dan mengembalikan daftar kode lokasi Unity. Layanan tersebut digunakan oleh alat bantu Unity Editor, sedangkan aplikasi Unity saat dijalankan tetap menggunakan `/api/unity/data`.

[FIGURE:api_test_unity_names]
[FIGCAPTION:Respons Endpoint Daftar Kode Lokasi untuk Unity Editor]

Skenario negatif pada [FIGREF:api_test_rls_unauthorized] mengirim data uji ke REST API Supabase tanpa kredensial yang memenuhi policy. Respons `401 Unauthorized` dengan kode `42501` membuktikan bahwa mutasi tersebut ditolak oleh RLS. Penulis menggunakan hasil ini untuk memverifikasi bahwa integrasi web tunduk pada kontrol akses yang tersedia; rancangan policy RLS tetap merupakan kontribusi Database Schema Designer.

[FIGURE:api_test_rls_unauthorized]
[FIGCAPTION:Penolakan Perubahan Data Tanpa Autentikasi oleh Supabase RLS]

Keempat pemeriksaan tersebut merupakan pemeriksaan dasar secara manual dan belum menggantikan pengujian lingkungan produksi secara otomatis. Playwright belum digunakan untuk menguji autentikasi, CRUD terotorisasi, header produksi, dan integrasi Unity dari awal sampai akhir. Keterbatasan ini dipisahkan dari hasil 129 pengujian otomatis agar cakupan pengujian tidak dilebihkan.

### 3.5.2 Pengujian Black Box

<!-- PIPELINE:INCLUDE content/shared/testing/blackbox.md -->

Pengujian ulang BB-20 didokumentasikan melalui dua tangkapan layar berurutan karena perubahan terjadi ketika pengguna mendekati tujuan. Kondisi sebelum pengguna tiba terlihat pada [FIGREF:blackbox_bb20_rute_aktif], yang memperlihatkan garis rute masih aktif, jarak tersisa 16 meter, dan nama Gedung Dewi Sartika, bukan kode lokasi internal.

[FIGURE:blackbox_bb20_rute_aktif]
[FIGCAPTION:Pengujian Ulang BB-20 Saat Navigasi Masih Aktif]

Kondisi setelah pengguna mencapai tujuan terlihat pada [FIGREF:blackbox_bb20_navigasi_selesai], yang memperlihatkan bahwa garis rute telah hilang dan notifikasi kedatangan menampilkan nama tujuan yang sama. Kedua tangkapan layar tersebut menjadi bukti visual pengujian ulang BB-20 sehingga status akhirnya dinyatakan lulus.

[FIGURE:blackbox_bb20_navigasi_selesai]
[FIGCAPTION:Pengujian Ulang BB-20 Setelah Navigasi Selesai]

### 3.5.3 Pengujian Lighthouse

Lighthouse digunakan sebagai alat audit otomatis untuk menilai kualitas halaman web melalui kategori kinerja, aksesibilitas, praktik terbaik, dan SEO, dengan keterbatasan bahwa pemeriksaan otomatis belum mencakup seluruh hambatan aksesibilitas (McGill et al. 2023).

Audit Lighthouse dijalankan pada 21 Juli 2026 sekitar pukul 08.15 WIB terhadap hasil build produksi melalui server pratinjau Vite pada `http://127.0.0.1:4173/`. Perintah `npm run lighthouse` membangun aplikasi, menjalankan server pratinjau, serta menghasilkan laporan untuk simulasi smartphone dan komputer desktop. Pengujian menggunakan Lighthouse 12.8.2, HeadlessChrome 150, simulasi pembatasan jaringan dan CPU, serta pembersihan data browser terpilih. Skor dari laporan JSON Lighthouse dirangkum pada [TABREF:performa_lighthouse].

[TABLE-ID:performa_lighthouse]
[TABLECAPTION:Hasil Audit Lighthouse pada Smartphone dan Komputer Desktop]

[TABLE]
Perangkat | Kinerja | Aksesibilitas | Praktik Terbaik | SEO
Smartphone | 86/100 | 100/100 | 100/100 | 100/100
Komputer Desktop | 99/100 | 100/100 | 100/100 | 100/100
[/TABLE]

Metrik utama yang membentuk skor tersebut disajikan pada [TABREF:metrik_lighthouse]. Nilai dibulatkan untuk keterbacaan, sedangkan data mentah tetap tersedia pada `reports/lighthouse/latest-mobile.json` dan `reports/lighthouse/latest-desktop.json`.

[TABLE-ID:metrik_lighthouse]
[TABLECAPTION:Metrik Utama Lighthouse pada Smartphone dan Komputer Desktop]

[TABLE]
Metrik | Smartphone | Komputer Desktop | Interpretasi
*First Contentful Paint* (FCP) | 2.444 ms | 541 ms | Waktu tampil konten awal pada smartphone masih menjadi bagian yang perlu dioptimalkan
*Largest Contentful Paint* (LCP) | 3.681 ms | 775 ms | Waktu tampil elemen utama pada smartphone merupakan hambatan utama; hasil komputer desktop sangat baik
*Speed Index* | 2.444 ms | 589 ms | Kecepatan tampilan komputer desktop sangat baik dan smartphone masih dapat ditingkatkan
*Total Blocking Time* (TBT) | 89 ms | 6 ms | Keduanya berada di bawah 200 ms
*Cumulative Layout Shift* (CLS) | 0 | 0 | Tidak terdeteksi pergeseran tata letak pada audit
*Time to Interactive* (TTI) | 3.913 ms | 781 ms | Interaktivitas pada smartphone masih dapat dipercepat
*Total Byte Weight* | 419.577 byte | 566.763 byte | Ukuran pada komputer desktop lebih besar karena menggunakan gambar utama versi komputer
[/TABLE]

Elemen LCP pada kedua mode adalah gambar utama pertama dengan teks alternatif "UPNVJ Campus 1". Pada simulasi smartphone, file `hero1-mobile.webp` berukuran sekitar 32,2 KiB dan telah diminta sejak awal dengan prioritas tinggi. Hasil audit menunjukkan bahwa sekitar 88 persen waktu LCP terjadi setelah file tersedia, ketika browser menunggu gambar ditampilkan. Oleh karena itu, optimasi berikutnya lebih diarahkan pada proses tampilan, sekitar 75 KiB JavaScript yang tidak terpakai, kompresi dan ukuran responsif gambar utama, serta satu stylesheet sekitar 16 KiB yang masih menghambat tampilan awal.

Hasil tersebut berasal dari pengujian lokal dengan kondisi yang disimulasikan, bukan dari data penggunaan nyata. Seluruh 19 pemeriksaan otomatis Aksesibilitas yang berlaku dinyatakan lulus, tetapi 10 pemeriksaan manual masih perlu dilakukan. Sembilan pemeriksaan otomatis SEO juga lulus dengan satu pemeriksaan manual tersisa, sedangkan kategori *Progressive Web App* (PWA) tidak diuji. Audit halaman awal ini tidak mengukur seluruh proses pemuatan Unity WebGL setelah pengguna memilih Denah 3D.

### 3.5.4 UAT

<!-- PIPELINE:INCLUDE content/shared/testing/uat.md -->

### 3.5.5 Tindak Lanjut Hasil UAT

<!-- PIPELINE:INCLUDE content/roles/iman/uat-revisions.md -->

### 3.5.6 Dokumentasi Implementasi Revisi UAT

Dokumentasi pada subbab ini hanya menampilkan realisasi tindak lanjut UAT yang berada dalam batas kontribusi penulis. Pemeriksaan dilakukan melalui kode sumber, hasil pengujian otomatis, sumber resmi, serta tangkapan layar aplikasi pada 21 Juli 2026. Tangkapan layar digunakan untuk memeriksa hasil setelah perbaikan dan tidak diperlakukan sebagai kuesioner UAT kedua.

1. Tutorial, FAQ, dan Pemilih Mode
   Tindak lanjut UAT-R02 diwujudkan melalui bagian Tutorial dan FAQ yang membedakan panduan Denah 2D dan Denah 3D pada komputer desktop maupun smartphone. Tutorial 2D menjelaskan cara menentukan lokasi awal, mencari tujuan, membaca garis rute, dan mengganti titik awal. Panduan 3D pada lapisan web menjelaskan proses pemuatan, kontrol dasar, pencarian, pergantian mode, dan langkah pemulihan. Tampilan pada [FIGREF:uat_revisi_tutorial_faq] memperlihatkan bahwa bantuan tersedia sebelum pengguna membuka denah.

[FIGURE:uat_revisi_tutorial_faq]
[FIGCAPTION:Tutorial dan FAQ Denah Kampus Setelah Revisi]

   Tindak lanjut UAT-R03 dan UAT-R05 tidak meminta pengguna membuat profil khusus. Sebagai gantinya, antarmuka web menyediakan pilihan bahasa, perangkat, mode denah, tutorial, pencarian tujuan, dan lokasi awal. Pemilih pada [FIGREF:uat_revisi_mode_selector] memberi pengguna opsi Denah 2D untuk navigasi yang lebih sederhana atau Denah 3D untuk menjelajahi lingkungan kampus. Dengan pilihan ini, pengguna yang tidak terbiasa dengan kontrol permainan tetap dapat memakai Denah 2D tanpa harus memuat simulasi 3D.

[FIGURE:uat_revisi_mode_selector]
[FIGCAPTION:Pemilihan Mode Denah 2D atau 3D]

2. Denah 2D sebagai Alternatif Navigasi
   Pada tindak lanjut UAT-R03 dan bagian web UAT-R07, pengguna memilih gedung awal lalu mencari gedung atau fasilitas tujuan. Antarmuka React memuat jaringan jalur dan pintu masuk gedung, menghitung rute menggunakan algoritma A\*, kemudian menggambar garis rute di atas denah. Fasilitas diarahkan ke pintu masuk gedung induknya karena Denah 2D belum menampilkan rute di dalam ruangan; batasan ini juga dijelaskan pada FAQ. Verifikasi visual pada [FIGREF:uat_revisi_map_2d] menunjukkan nama lokasi, penanda titik awal, kolom pencarian, garis rute, dan tombol untuk mengganti titik awal dalam satu tampilan.

[FIGURE:uat_revisi_map_2d]
[FIGCAPTION:Denah 2D dengan Titik Awal dan Label Lokasi]

3. Pencarian dan Bantuan pada Antarmuka Web
   Pada sisi React untuk UAT-R01, pencarian memeriksa nama fasilitas, deskripsi fasilitas, nama gedung, deskripsi gedung, lokasi, dan istilah alternatif. Antarmuka memanfaatkan data yang disiapkan Database Schema Designer tanpa mengklaim pekerjaan pembersihan data sebagai kontribusi penulis. UAT-R08 ditindaklanjuti melalui tombol bantuan yang memuat petunjuk pencarian, pembatalan navigasi, pergantian mode, langkah ketika denah gagal dimuat, dan nomor layanan resmi kampus.

4. Validasi Notifikasi Kedatangan pada React
   Pada tindak lanjut UAT-R10, React mengirim kode lokasi tujuan kepada Unity untuk memulai navigasi. Ketika Unity mengirim pesan `OnNavigationCompleted`, React memeriksa apakah kode lokasi pada pesan sama dengan tujuan yang sedang aktif. Notifikasi "Tiba di Tujuan" hanya ditampilkan jika keduanya sesuai; pesan kosong, tidak valid, tujuan berbeda, atau pesan setelah pembatalan diabaikan. Mekanisme pengiriman pesan dari Unity tetap menjadi kontribusi Engine Developer, sedangkan validasi dan tampilan notifikasi pada React merupakan kontribusi penulis.

   Hasil penerapan fitur tersebut terlihat pada [FIGREF:uat_revisi_notifikasi_tiba], yang menunjukkan notifikasi "Tiba di Tujuan" dengan nama Gedung Dewi Sartika setelah navigasi selesai. Perilaku ini juga diperiksa melalui sebelas pengujian otomatis untuk memastikan notifikasi hanya muncul pada kondisi kedatangan yang benar.

[FIGURE:uat_revisi_notifikasi_tiba]
[FIGCAPTION:Notifikasi Tiba di Tujuan Setelah Navigasi Selesai]

   Bukti pada subbab ini menunjukkan tindak lanjut UAT dalam lingkup Denah 2D, antarmuka web, dan penghubung React–Unity. Perbaikan data, aset 3D, minimap, titik awal di dalam Unity, label lingkungan 3D, serta proses build Unity tidak diklaim sebagai kontribusi penulis. Nilai UAT awal tetap dipertahankan, dan pemeriksaan setelah perbaikan tidak dihitung sebagai pengulangan kuesioner terhadap lima peserta.

---

# BAB IV PENUTUP

## 4.1 Kesimpulan

Berdasarkan hasil pengembangan, implementasi, dan pengujian, kesimpulan disusun untuk menjawab identifikasi masalah dan tujuan penelitian sebagai berikut:

1. Menjawab kesulitan pengguna dalam memperoleh informasi dan menemukan lokasi, Dashboard Publik telah menyediakan informasi kampus terpilih, pencarian gedung atau fasilitas, Tutorial dan FAQ, serta pilihan Denah 2D atau Denah 3D melalui browser. Denah 2D memberi alternatif bagi pengguna yang tidak terbiasa dengan kontrol permainan. UAT tertutup pada Dashboard Publik memperoleh 77,78 persen dari empat peserta, tetapi hasil tersebut belum mewakili calon mahasiswa, orang tua atau wali mahasiswa, maupun pengunjung eksternal karena kelompok tersebut tidak menjadi peserta UAT.
2. Menjawab kebutuhan akan alur yang menghubungkan pencarian dengan panduan spasial, pilihan tujuan pada React telah digunakan untuk menghitung rute A\* pada Denah 2D atau dikirim sebagai kode lokasi kepada Unity untuk navigasi 3D. React juga memvalidasi pesan kedatangan terhadap tujuan aktif sebelum menampilkan notifikasi. Pengujian Black Box akhir mencatat 24 dari 24 skenario lulus, sedangkan sebelas pengujian otomatis React memeriksa kondisi notifikasi kedatangan.
3. Menjawab kebutuhan pengelolaan informasi yang terkendali dan konsisten, Panel Admin telah menggunakan Supabase Auth dan RLS untuk membatasi akses serta menyediakan pengelolaan gedung, fasilitas, program studi, dan konfigurasi Denah 2D. REST API menyediakan data bagi Unity dan pemeriksaan kode lokasi, sedangkan konfigurasi deployment menempatkan aplikasi web, layanan API, dan file hasil build Unity WebGL pada layanan yang sama. UAT tertutup pada Panel Admin memperoleh 84,55 persen dari empat peserta, dan pemeriksaan API menunjukkan bahwa perubahan data tanpa autentikasi ditolak. Integrasi dengan sistem internal universitas tetap menjadi pekerjaan lanjutan yang memerlukan persetujuan institusional.
4. Sebagai hasil tindak lanjut UAT dalam lingkup kontribusi penulis, perbaikan telah diterapkan pada pencarian React, Tutorial dan FAQ Denah 2D serta Denah 3D, pemilih mode dan Denah 2D, bantuan pada antarmuka web, serta validasi notifikasi kedatangan dari Unity ke React. Perbaikan tersebut diperiksa melalui kode sumber, sebelas pengujian otomatis React, sumber resmi, dan tangkapan layar aplikasi. Pemeriksaan pascaperbaikan ini bukan UAT ulang sehingga tidak mengubah nilai UAT awal sebesar 81,50 persen.

## 4.2 Saran

Beberapa saran yang direkomendasikan untuk pengembangan sistem lebih lanjut di masa mendatang adalah:

1. Menyiapkan penghubung identitas, domain, pengelolaan kunci rahasia dan kredensial, serta API institusional apabila sistem memperoleh persetujuan untuk diintegrasikan dengan infrastruktur kampus. Integrasi tersebut perlu mengikuti prosedur dan persetujuan resmi tanpa menanamkan ketergantungan pada satu platform hosting.
2. Meningkatkan skor Kinerja pada simulasi smartphone hingga sekurang-kurangnya 90 tanpa menurunkan skor Aksesibilitas, Praktik Terbaik, dan SEO. Prioritas optimasi mencakup pengurangan waktu tunda tampilan gambar utama, sekitar 75 KiB JavaScript yang tidak terpakai, penyediaan ukuran gambar yang sesuai dengan perangkat, dan pengurangan stylesheet yang menghambat tampilan awal. Setiap perubahan perlu diperiksa kembali melalui audit smartphone dan komputer desktop dengan konfigurasi yang sama.
3. Menambahkan rangkaian pengujian browser dan WebGL secara menyeluruh untuk proses masuk, akses halaman admin, CRUD, pemilih denah, pencarian 2D/3D, pemuatan WebGL, notifikasi kedatangan, dan layanan API pada lingkungan produksi. Pengujian pengguna berikutnya juga perlu melibatkan mahasiswa baru, orang tua atau wali, dan pengunjung eksternal agar kemudahan penggunaan dapat dinilai langsung pada kelompok pengguna yang dituju.
4. Menetapkan satu analitik utama antara Supabase dan Umami agar definisi metrik, retensi data, privasi, serta pengoperasian layanan tetap konsisten.
5. Berkoordinasi dengan Database Schema Designer untuk menerapkan otorisasi admin yang lebih terperinci dan memastikan pencatatan audit tetap berlaku pada perubahan yang tidak berasal dari antarmuka web.

---

# DAFTAR PUSTAKA

Aliyah, A., Hartono, N., dan Muin, A. A. (2025). Penggunaan User Acceptance Testing (UAT) pada pengujian sistem informasi pengelolaan keuangan dan inventaris barang. *Switch: Jurnal Sains dan Teknologi Informasi*, 3(2), 42–58. https://doi.org/10.62951/switch.v3i1.330

Chandralekha, C. S., dan Raghunandana, M. (2023). Analysis of information architecture for university library websites: An Indian perspective. *International Journal of Information Dissemination and Technology*, 13(3), 111–115. https://doi.org/10.5958/2249-5576.2023.00021.3

Dalimunthe, S., Hasri Putra, E., dan Fadhly Ridha, M. A. (2023). Restful API security using JSON Web Token (JWT) with HMAC-SHA512 algorithm in session management. *IT Journal Research and Development*, 8(1), 81–94. https://doi.org/10.25299/itjrd.2023.12029

Jamaludin, J., dan Saepuloh, L. (2024). Tren riset twin digital smart campus. *Sang Pencerah: Jurnal Ilmiah Universitas Muhammadiyah Buton*, 10(2), 408–425. https://doi.org/10.35326/pencerah.v10i2.5317

Li, Z., Guo, L., Cheng, J., Chen, Q., He, B., dan Guo, M. (2022). The serverless computing survey: A technical primer for design architecture. *ACM Computing Surveys*, 54(10s), Article 220, 1–34. https://doi.org/10.1145/3508360

Maulida, M., Zahro, F., Hakim, R., dan Akbar, M. S. (2025). Pengujian black box testing pada sistem website pemesanan online Toko Ayam Krispy. *Jurnal Media Akademik (JMA)*, 3(5). https://doi.org/10.62281/v3i5.1908

McGill, T., Bamgboye, O., Liu, X., dan Kalutharage, C. S. (2023). Towards improving accessibility of web auditing with Google Lighthouse. In *2023 IEEE 47th Annual Computers, Software, and Applications Conference (COMPSAC)* (pp. 1594–1599). IEEE Computer Society. https://doi.org/10.1109/COMPSAC57700.2023.00246

Muharam, Y., Anggara, M. B., dan Hanafi, T. J. (2023). Implementasi peta 3 dimensi menggunakan metode IMSDD (Interactive Multimedia System Design and Development) dan WebGL API berbasis web (Studi kasus di SMP Karya Pembangunan 2 Majalaya). *Jurnal Informatika-COMPUTING*, 10, 20–30. https://doi.org/10.55222/computing.v10i01.1155

Putra, I. G. W. W., Dharma, E. M., dan Permana, P. T. H. (2026). Implementasi relational database dengan Row-Level Security (RLS) pada sistem inventory menggunakan Supabase dan React Native Expo (Studi kasus Bengkel Sari Merta). *JATI (Jurnal Mahasiswa Teknik Informatika)*, 10(2), 2443–2448. https://doi.org/10.36040/jati.v10i2.17551

Syarif, S., dan Risdiansyah, D. (2024). Pemanfaatan metode prototype dalam perancangan sistem informasi penjualan berbasis website. *Jurnal Ekonomi Manajemen dan Bisnis (JEMB)*, 2(1), 12–25. https://doi.org/10.54895/jemb.v2i1.2312

Taurusta, C., Asiddiq, A. M., Suprianto, S., dan Setiawan, H. (2024). Visualisasi gedung kampus 1 Universitas Muhammadiyah Sidoarjo menggunakan augmented reality sebagai media informasi. *Journal of Technology and System Information*, 1(1), 55–70. https://doi.org/10.47134/jtsi.v1i1.2146

UPNVJ. (2022). Lokasi kampus. https://www.upnvj.ac.id/id/tentang-upn/lokasi-kampus.html

UPNVJ. (2025a). Kantin. https://www.upnvj.ac.id/id/fasilitas-layanan/kantin.html

UPNVJ. (2025b). Sejarah. https://www.upnvj.ac.id/id/tentang-upn/sejarah.html

UPNVJ. (2026). Rapat koordinasi Humas UPNVJ 2026: Fokus strategi komunikasi digital dan media sosial perguruan tinggi. https://www.upnvj.ac.id/id/berita/2026/02/rapat-koordinasi-humas-upnvj-2026-fokus-strategi-komunikasi-digital-dan-media-sosial-perguruan-tinggi.html

W3C. (2024). Web Content Accessibility Guidelines (WCAG) 2.2. https://www.w3.org/TR/WCAG22/

Wang, H., Lou, S., Jing, J., Wang, Y., Liu, W., dan Liu, T. (2022). The EBS-A\* algorithm: An improved A\* algorithm for path planning. *PLOS ONE*, 17(2), e0263841. https://doi.org/10.1371/journal.pone.0263841

Wayahdi, M. R., dan Ruziq, F. (2023). Pemodelan sistem penerimaan anggota baru dengan Unified Modeling Language (UML) (Studi kasus: Programmer Association of Battuta). *Jurnal Minfo Polgan*, 12(1), 1514–1521. https://doi.org/10.33395/jmp.v12i1.12870

---

# LAMPIRAN 1. Dokumentasi Penyerahan Pakta Integritas kepada UPA TIK

Salinan pakta integritas atas nama penulis tidak berada dalam arsip yang tersedia. Bukti utama yang dimiliki penulis berupa foto dokumentasi penyerahan dokumen kepada staf UPA TIK; lampiran ini tidak dimaksudkan sebagai pengganti pakta atas nama penulis atau surat keterangan resmi dari institusi.

Proses penyerahan yang terekam pada [FIGREF:foto_penyerahan_pakta_upa_tik] menunjukkan tim membawa dokumen pakta integritas dalam kegiatan koordinasi dengan UPA TIK. Caption dan narasi tidak menetapkan identitas staf, nomor surat, tanggal pengesahan, atau status persetujuan yang tidak dapat diverifikasi dari bukti tersebut.

[FIGURE:foto_penyerahan_pakta_upa_tik]
[FIGCAPTION:Dokumentasi Penyerahan Pakta Integritas kepada UPA TIK]

Sebagai konteks bentuk dokumen yang diserahkan, [FIGREF:contoh_pakta_integritas_anggota_tim] menampilkan contoh pakta integritas yang telah diisi oleh salah satu anggota tim dan dicantumkan dengan izin pemilik dokumen. Identitas, tanda tangan, dan meterai pada contoh tersebut bukan milik penulis, sehingga gambar tidak digunakan sebagai bukti bahwa penulis telah menandatangani pakta, memperoleh persetujuan institusional, atau menyerahkan dokumen secara individual.

[FIGURE:contoh_pakta_integritas_anggota_tim]
[FIGCAPTION:Contoh Pakta Integritas Penelitian Anggota Tim]

---

# LAMPIRAN 2. Kode Sumber Utama

Lampiran ini hanya memuat cuplikan yang berada dalam batas kontribusi Full Stack Web Developer, System Integrator, dan DevOps Engineer. Kode internal Unity, termasuk alat pemeriksaan sinkronisasi, tidak dicantumkan karena dikembangkan oleh 3D Simulator dan Engine Developer. Cuplikan dipilih untuk membuktikan autentikasi, CRUD, integrasi React–Unity, REST API, analitik, dan deployment tanpa memuat repositori secara penuh atau menampilkan kredensial.

Pemetaan pada [TABREF:lampiran_artefak_kode] menunjukkan delapan kelompok bukti yang menjadi dasar pemilihan cuplikan kode.

[TABLE-ID:lampiran_artefak_kode]
[TABLECAPTION:Pemetaan Cuplikan Kode terhadap Kontribusi Penulis]

[TABLE]
No. | Bukti | Lokasi Sumber | Kontribusi yang Dibuktikan
1 | Supabase Auth dan perlindungan halaman admin | `src/lib/supabase.ts`, `src/contexts/AuthContext.tsx`, `src/components/common/ProtectedRoute.tsx` | Sesi browser, autentikasi, dan pembatasan akses Panel Admin
2 | Pengelolaan Data Panel Admin | `src/services/api/supabaseDataService.ts` | Pemeriksaan isian, operasi data melalui Supabase, cache, dan pencatatan riwayat perubahan
3 | Pemuatan awal adaptif | `src/utils/unityPreloader.ts` | Penghematan bandwidth sebelum pengguna memilih mode 3D
4 | Loader dan perintah navigasi | `UnityCampusMap.tsx`, `SearchOverlay.tsx` | Pemuatan file hasil build WebGL dan penghubung React ke Unity
5 | Notifikasi penyelesaian navigasi | `SearchOverlay.tsx` | Pemeriksaan tujuan aktif sebelum notifikasi kedatangan ditampilkan
6 | REST API Unity | `api/unity/data.js`, `api/unity/names.js` | Penyediaan data untuk aplikasi Unity dan alat bantu editor
7 | Analitik aplikasi | `src/services/analytics/trackingService.ts` | Pencatatan kunjungan halaman pada Supabase
8 | Pemantauan layanan dan deployment | `api/health.js`, `vercel.json` | Status layanan, header, kompresi, dan cache aset
[/TABLE]

1. Klien Supabase dan Perlindungan Halaman Admin (`src/lib/supabase.ts` dan `src/components/common/ProtectedRoute.tsx`):

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
          <div
            className={
              "animate-spin rounded-full h-16 w-16 " +
              "border-b-4 border-[rgb(44_95_45)] mx-auto mb-4"
            }
          ></div>
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

3. Keputusan Pemuatan Awal Adaptif Aset Unity (`src/utils/unityPreloader.ts`):

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

Nilai `skip` pada cuplikan tersebut hanya melewati pengunduhan awal di latar belakang. Pengguna smartphone atau pengguna dengan koneksi terbatas tetap dapat memilih Denah 3D melalui pemilih mode; file WebGL baru dimuat ketika mode tersebut dibuka.

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

5. Validasi Notifikasi Kedatangan (`SearchOverlay.tsx`):

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

6. Vercel Serverless Functions untuk Data Unity dan Alat Editor (`api/unity/data.js` dan `api/unity/names.js`):

Layanan untuk Unity mengambil data gedung dan fasilitas melalui permintaan paralel sebagai berikut:

```javascript
const [gedungResult, fasilitasResult] = await Promise.all([
  supabase
    .from("gedung")
    .select(
      "id, nama_gedung, deskripsi_gedung, lokasi, " +
        "jumlah_lantai, unity_object_name",
    )
    .order("id", { ascending: true }),
  supabase
    .from("fasilitas")
    .select(
      "id, nama_fasilitas, deskripsi_fasilitas, tipe_fasilitas, " +
        "id_gedung, lantai, foto_url, unity_object_name",
    )
    .order("id_gedung", { ascending: true })
    .order("lantai", { ascending: true }),
]);

if (gedungResult.error) throw gedungResult.error;
if (fasilitasResult.error) throw fasilitasResult.error;

return res.status(200).json(result);
```

Layanan untuk alat bantu editor mengambil kode lokasi yang tidak kosong dan mengembalikannya sebagai daftar terurut:

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

8. Pemantauan Status Layanan serta Konfigurasi Header dan Cache (`api/health.js` dan `vercel.json`):

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

# LAMPIRAN 3. Panduan Pengguna dan Prosedur Operasional

Panduan ini menjelaskan langkah pengoperasian yang sesuai dengan antarmuka terkini. Informasi kredensial, kunci akses, dan nilai variabel lingkungan tidak dicantumkan. Panduan Unity dibatasi pada tindakan yang terlihat oleh pengguna karena implementasi aplikasi 3D merupakan kontribusi 3D Simulator dan Engine Developer.

## A. Panduan Administrator

Panel Admin digunakan untuk mengelola data yang digunakan Dashboard Publik, Denah 2D, dan integrasi Unity.

1. Masuk dan Keluar dari Panel Admin:
   a. Buka `/login` pada domain aplikasi.
   b. Masukkan nama pengguna dan kata sandi akun administrator yang sah, lalu pilih tombol "Masuk".
   c. Supabase Auth membentuk sesi dan membuka halaman `/admin` setelah autentikasi berhasil.
   d. Gunakan tombol keluar setelah pekerjaan selesai, terutama ketika menggunakan perangkat bersama. Kredensial pengujian tidak ditulis pada laporan atau repositori.
2. Memilih Modul Pengelolaan:
   a. Panel Admin menyediakan tab Gedung, Fasilitas, Program Studi, Denah 2D, Analytics, dan Audit Log.
   b. Gunakan pencarian, penyaring, dan pembagian halaman tabel untuk mempersempit data sebelum melakukan perubahan.
3. Mengelola Data Gedung dan Fasilitas:
   a. Pilih tab Gedung atau Fasilitas, kemudian gunakan tombol "Tambah Gedung" atau "Tambah Fasilitas" untuk membuka formulir.
   b. Isi kolom wajib dan informasi yang tersedia, termasuk nama tampilan, deskripsi, lokasi atau lantai, gedung induk, tipe, serta foto apabila tersedia.
   c. Gunakan aksi Edit untuk memperbarui data dan aksi Hapus untuk membuka konfirmasi sebelum penghapusan dilakukan.
   d. Kode lokasi Unity merupakan kode teknis, bukan nama yang ditampilkan kepada pengguna. Kolom ini diperlukan apabila data menjadi tujuan navigasi 3D langsung dan harus sesuai dengan objek tujuan pada Unity. Fasilitas yang tidak memiliki tujuan langsung dapat dipetakan ke gedung induk sesuai aturan pencarian.
   e. Setelah penyimpanan, periksa notifikasi, data tabel, dan tampilan publik yang terkait. Jumlah data pada aplikasi aktif tidak boleh disamakan dengan berkas data awal sebelum proses sinkronisasi diverifikasi.
4. Mengelola Program Studi:
   a. Pilih tab Program Studi untuk menambah, mengubah, mencari, atau menghapus data program studi.
   b. Pilih fakultas naungan dan isi kolom akademik yang tersedia pada formulir. Panel Admin tidak menyediakan tab Fakultas terpisah pada antarmuka yang ditinjau.
5. Mengelola Konfigurasi Denah 2D:
   a. Pilih tab Denah 2D untuk mengelola peta aktif, penanda gedung, pintu masuk, simpul, dan jalur pada jaringan rute.
   b. Pastikan setiap gedung yang dapat menjadi titik awal atau tujuan mempunyai penanda dan pintu masuk yang terhubung ke jaringan rute.
   c. Simpan perubahan secara bertahap dan periksa rute melalui mode 2D pada Dashboard Publik. Jalur yang tidak terhubung dapat menyebabkan garis rute tidak terbentuk.
6. Meninjau Analitik dan Catatan Perubahan:
   a. Tab `Analytics` menampilkan ringkasan kunjungan halaman yang dibaca dari `web_analytics_log` pada Supabase.
   b. Tab Audit Log menampilkan operasi yang dicatat layanan aplikasi setelah proses CRUD melalui Panel Admin.
   c. Pencatatan dari aplikasi tidak digunakan untuk mengklaim bahwa seluruh mutasi di luar aplikasi otomatis dicatat oleh trigger database.

## B. Panduan Pengguna Publik

Dashboard Publik dapat digunakan oleh mahasiswa baru, orang tua atau wali, sivitas akademika, dan pengunjung eksternal untuk memperoleh informasi serta memilih pengalaman navigasi 2D atau 3D.

1. Membuka Dashboard Publik dan Panduan Awal:
   a. Buka root domain `/` melalui browser.
   b. Gunakan pilihan bahasa Indonesia atau Inggris sesuai kebutuhan.
   c. Baca bagian Tutorial dan FAQ Denah Kampus. Tutorial dapat dipilih berdasarkan mode 2D atau 3D dan jenis perangkat yang digunakan.
   d. Gunakan kartu serta bagian informasi yang tersedia untuk meninjau gedung, fasilitas, statistik kunjungan, dan informasi utama kampus sebelum membuka denah.
2. Memilih Jenis Denah:
   a. Pilih tombol "Buka Denah Kampus" untuk membuka pemilih mode.
   b. Pilih Denah 2D untuk pencarian rute yang lebih ringan atau Denah 3D untuk pengalaman Unity WebGL.
   c. Tombol "Ganti mode" dapat digunakan untuk kembali ke pemilih tanpa memuat ulang seluruh halaman.
3. Menggunakan Denah 2D:
   a. Pada dialog awal, pilih gedung tempat pengguna berada dan tekan "Gunakan sebagai titik awal".
   b. Ketik nama gedung, ruangan, fasilitas, atau istilah yang familiar pada kolom pencarian, lalu pilih hasil yang sesuai.
   c. Antarmuka memetakan hasil ke pintu masuk gedung dan menampilkan garis rute hasil perhitungan A\* pada denah.
   d. Gunakan pilihan "Mulai dari gedung" untuk mengganti titik awal. Denah 2D mengarahkan pengguna ke pintu masuk gedung tujuan dan tidak mensimulasikan pergerakan di dalam ruangan.
4. Menggunakan Denah 3D:
   a. Pilih Denah 3D dan tunggu proses pemuatan Unity WebGL v0.8.6.1 selesai. Pada perangkat atau koneksi tertentu, aplikasi tidak melakukan pemuatan awal otomatis agar halaman utama tetap ringan.
   b. Pilih lokasi awal yang sesuai pada tampilan pemilihan titik awal.
   c. Pada komputer, klik area denah lalu gunakan `W`, `A`, `S`, dan `D` untuk bergerak, `Shift` untuk berlari, `Space` untuk melompat, tetikus untuk mengarahkan kamera, serta `Esc` untuk melepaskan kursor.
   d. Pada smartphone, gunakan posisi mendatar, joystick kiri untuk bergerak, gestur pada area kanan untuk mengarahkan kamera, serta tombol berlari dan melompat yang tersedia.
5. Mencari Tujuan dan Menyelesaikan Navigasi:
   a. Gunakan kolom pencarian di bagian atas denah dan pilih tujuan.
   b. Pada mode 3D, React mengirim kode lokasi kepada Unity, kemudian Unity menampilkan petunjuk rute dan label tujuan.
   c. Setelah pengguna tiba, Unity mengirim pemberitahuan penyelesaian. React hanya menampilkan notifikasi "Tiba di Tujuan" apabila kode lokasi yang diterima sama dengan tujuan aktif.
   d. Pengguna dapat membatalkan navigasi atau memilih tujuan baru. Pembatalan tidak diperlakukan sebagai kondisi tiba.
6. Memperoleh Bantuan:
   a. Gunakan tombol bantuan pada Denah 3D untuk membuka panduan navigasi dan kontak layanan kampus.
   b. Jika mode 3D gagal dimuat atau sulit digunakan, muat ulang halaman, periksa koneksi, atau beralih ke Denah 2D.
   c. Nomor layanan yang ditampilkan aplikasi adalah 021-7699431 dan 021-7656971. Kedua nomor tersebut diambil dari [halaman Hubungi Kami pada situs Penmaru UPNVJ](https://penmaru.upnvj.ac.id/id/contact.html).

## C. Prosedur Serah Terima Data, File Hasil Build Unity, dan Deployment

Bagian ini menjadi daftar pemeriksaan pengoperasian lintas komponen. Penulis mengelola antarmuka React, spesifikasi API, penghubung React–Unity, dan deployment layanan. 3D Simulator dan Engine Developer mengelola aplikasi Unity, NavMesh, alat bantu editor, optimasi, dan proses build Unity.

1. Pembaruan Data dan Kode Lokasi:
   a. Perubahan data dilakukan melalui Panel Admin sesuai sesi dan kebijakan akses yang tersedia.
   b. Nama tampilan disimpan terpisah dari kode lokasi Unity. Perubahan kode lokasi harus disepakati bersama karena digunakan oleh API, React, dan objek tujuan pada Unity.
   c. `/api/unity/data` menyediakan data untuk aplikasi Unity saat dijalankan, sedangkan `/api/unity/names` digunakan oleh alat bantu editor untuk memeriksa daftar kode lokasi.
2. Penyerahan File Hasil Build Unity WebGL:
   a. 3D Simulator dan Engine Developer menyerahkan loader, kerangka kerja, WebAssembly, data, dan StreamingAssets dari satu hasil build yang sama.
   b. Penyerahan mencantumkan nomor versi dan catatan perubahan. Versi aktif yang dikonfigurasi saat peninjauan lampiran adalah v0.8.6.1.
   c. Notifikasi kedatangan menggunakan format yang telah disepakati dan mengirim kode lokasi dalam bentuk JSON.
3. Deployment oleh Penulis:
   a. File hasil build ditempatkan pada folder versi, kemudian lokasi loader, pemuatan awal, dan `vercel.json` diselaraskan ke versi yang sama.
   b. Vercel menetapkan tipe konten, kompresi Brotli, cache jangka panjang, header keamanan, dan pengalihan jalur SPA.
   c. Pemeriksaan dasar mencakup `/api/health`, `/api/unity/data`, `/api/unity/names`, status aset, kemajuan pemuatan, pengiriman perintah, dan notifikasi kedatangan.
4. Batas Perubahan:
   a. Masalah integrasi React, spesifikasi API, header, cache, atau deployment diperbaiki oleh penulis.
   b. Masalah aplikasi Unity, titik awal, NavMesh, label tujuan, minimap, pengambilan data, penerimaan perintah, atau proses build dikembalikan kepada 3D Simulator dan Engine Developer untuk diperbaiki dan dibangun ulang.
   c. Hasil pengamatan jaringan pada v0.8.0 dan audit Lighthouse tanggal 21 Juli 2026 merupakan bukti dari versi sebelumnya. Nilainya tidak digunakan untuk menilai v0.8.6.1 tanpa pengukuran ulang.

---

# LAMPIRAN 4. Instrumen UAT Tertutup dan Indeks Bukti Pengujian

<!-- PIPELINE:INCLUDE content/shared/testing/appendix-instruments.md -->

## A. Hasil Pindai Form UAT Tertutup

Bagian ini menyajikan hasil pindai formulir yang diisi pada UAT tertutup tanggal 15 Juli 2026. Penyebutan peserta pada caption dibatasi pada perannya berdasarkan daftar undangan resmi. Judul yang tercetak pada formulir merupakan judul proyek bersama yang digunakan saat pengujian dan tidak menggantikan judul individual laporan ini. Hasil pindai tidak digunakan untuk membuka pemetaan kode peserta R-01 sampai R-05 pada rekap anonim dan tidak dihitung ulang sebagai hasil pengujian baru. Apabila satu berkas memuat lebih dari satu pasangan lembar penilaian, seluruh halaman dipertahankan sesuai urutan arsip sumber tanpa menganggapnya sebagai peserta tambahan.

Form Dosen Penguji II disajikan secara berurutan pada [FIGREF:uat_closed_penguji_2_p1] dan [FIGREF:uat_closed_penguji_2_p2]. Kedua lembar tersebut mempertahankan pilihan skala dan masukan tulisan tangan sebagaimana terdapat pada arsip PDF.

[FIGURE:uat_closed_penguji_2_p1]
[FIGCAPTION:Form UAT Tertutup Dosen Penguji II, Lembar 1]

[FIGURE:uat_closed_penguji_2_p2]
[FIGCAPTION:Form UAT Tertutup Dosen Penguji II, Lembar 2]

Form Dosen Pembimbing II disajikan pada [FIGREF:uat_closed_pembimbing_2_p1], [FIGREF:uat_closed_pembimbing_2_p2], [FIGREF:uat_closed_pembimbing_2_p3], dan [FIGREF:uat_closed_pembimbing_2_p4]. Empat halaman tersebut memuat penilaian terhadap Panel Admin dan Dashboard Publik dalam satu arsip PDF.

[FIGURE:uat_closed_pembimbing_2_p1]
[FIGCAPTION:Form UAT Tertutup Dosen Pembimbing II, Lembar 1]

[FIGURE:uat_closed_pembimbing_2_p2]
[FIGCAPTION:Form UAT Tertutup Dosen Pembimbing II, Lembar 2]

[FIGURE:uat_closed_pembimbing_2_p3]
[FIGCAPTION:Form UAT Tertutup Dosen Pembimbing II, Lembar 3]

[FIGURE:uat_closed_pembimbing_2_p4]
[FIGCAPTION:Form UAT Tertutup Dosen Pembimbing II, Lembar 4]

Form UAT Dosen Pembimbing I ditampilkan pada [FIGREF:uat_closed_pembimbing_1_p1], [FIGREF:uat_closed_pembimbing_1_p2], [FIGREF:uat_closed_pembimbing_1_p3], dan [FIGREF:uat_closed_pembimbing_1_p4]. Berkas sumber memuat dua pasangan lembar dengan pilihan nilai dan masukan yang berbeda; seluruhnya disajikan sesuai urutan arsip, sedangkan angka agregat laporan tetap mengikuti rekap hasil UAT yang telah diverifikasi.

[FIGURE:uat_closed_pembimbing_1_p1]
[FIGCAPTION:Form UAT Tertutup Dosen Pembimbing I, Lembar 1]

[FIGURE:uat_closed_pembimbing_1_p2]
[FIGCAPTION:Form UAT Tertutup Dosen Pembimbing I, Lembar 2]

[FIGURE:uat_closed_pembimbing_1_p3]
[FIGCAPTION:Form UAT Tertutup Dosen Pembimbing I, Lembar 3]

[FIGURE:uat_closed_pembimbing_1_p4]
[FIGCAPTION:Form UAT Tertutup Dosen Pembimbing I, Lembar 4]

Form perwakilan Humas UPNVJ disajikan pada [FIGREF:uat_closed_humas_p1], [FIGREF:uat_closed_humas_p2], [FIGREF:uat_closed_humas_p3], dan [FIGREF:uat_closed_humas_p4]. Dokumen ini membuktikan keterlibatan Humas sebagai peserta evaluasi pengguna, tetapi tidak digunakan untuk mengklaim persetujuan atau penerimaan resmi sistem oleh institusi.

[FIGURE:uat_closed_humas_p1]
[FIGCAPTION:Form UAT Tertutup Perwakilan Humas UPNVJ, Lembar 1]

[FIGURE:uat_closed_humas_p2]
[FIGCAPTION:Form UAT Tertutup Perwakilan Humas UPNVJ, Lembar 2]

[FIGURE:uat_closed_humas_p3]
[FIGCAPTION:Form UAT Tertutup Perwakilan Humas UPNVJ, Lembar 3]

[FIGURE:uat_closed_humas_p4]
[FIGCAPTION:Form UAT Tertutup Perwakilan Humas UPNVJ, Lembar 4]

Form Dosen Penguji I disajikan pada [FIGREF:uat_closed_penguji_1_p1], [FIGREF:uat_closed_penguji_1_p2], [FIGREF:uat_closed_penguji_1_p3], dan [FIGREF:uat_closed_penguji_1_p4]. Empat halaman tersebut mempertahankan urutan hasil pindai serta masukan terbuka tanpa menambahkan interpretasi baru pada lampiran.

[FIGURE:uat_closed_penguji_1_p1]
[FIGCAPTION:Form UAT Tertutup Dosen Penguji I, Lembar 1]

[FIGURE:uat_closed_penguji_1_p2]
[FIGCAPTION:Form UAT Tertutup Dosen Penguji I, Lembar 2]

[FIGURE:uat_closed_penguji_1_p3]
[FIGCAPTION:Form UAT Tertutup Dosen Penguji I, Lembar 3]

[FIGURE:uat_closed_penguji_1_p4]
[FIGCAPTION:Form UAT Tertutup Dosen Penguji I, Lembar 4]

---

# LAMPIRAN 5. Matriks Bukti dan Prosedur Pengujian Ulang

Lampiran ini memetakan klaim kontribusi Full Stack Web Developer, System Integrator, dan DevOps Engineer kepada bukti yang dapat diperiksa. Matriks tidak menggantikan pembahasan hasil pada BAB III dan tidak memperluas klaim ke implementasi database atau Unity yang dimiliki anggota tim lain.

Hubungan antara area kontribusi, bukti, versi yang diperiksa, dan batas interpretasi ditunjukkan pada [TABREF:lampiran_matriks_artefak_iman].

[TABLE-ID:lampiran_matriks_artefak_iman]
[TABLECAPTION:Matriks Bukti Kontribusi Penulis]

[TABLE]
Area | Bukti atau Lokasi | Versi Bukti | Hasil yang Dibuktikan | Batas Interpretasi
Antarmuka publik dan admin | Empat gambar antarmuka utama pada BAB III; `src/components/dashboard/`, `src/components/admin/` | Tangkapan layar lingkungan produksi 21 Juli 2026 | Dashboard Publik, pencarian, tampilan 3D, dan Panel Admin tersedia | Tangkapan layar tidak membuktikan seluruh kondisi antarmuka atau penerapan file data awal ke database aktif
Autentikasi dan pengelolaan data | `AuthContext.tsx`, `ProtectedRoute.tsx`, `supabaseDataService.ts` | Kode sumber web yang diperiksa pada 21 Juli 2026 | Sesi, halaman admin yang dilindungi, pemeriksaan formulir, serta operasi data melalui Supabase | Rancangan RLS dan skema database bukan kontribusi penulis
Pengujian React | `SearchOverlay.test.tsx` dan rangkaian Vitest | Hasil pengujian kode sumber pada 21 Juli 2026 | 13 berkas dan 129 pengujian lulus, termasuk 11 pengujian notifikasi kedatangan | Angka berlaku untuk versi kode sumber yang diperiksa
REST API dan kontrol akses | `api/health.js`, `api/unity/data.js`, `api/unity/names.js`; empat gambar pengujian API | Pemeriksaan 21 Juli 2026 | Tiga endpoint GET memperoleh HTTP 200 dan perubahan data tanpa otorisasi ditolak RLS | Pemeriksaan manual belum menggantikan pengujian otomatis dari antarmuka hingga layanan akhir
Integrasi React–Unity | `SearchOverlay.tsx`, notifikasi kedatangan, tangkapan layar notifikasi tiba | Implementasi React dan Unity yang diperiksa pada 21 Juli 2026 | Notifikasi hanya muncul apabila tujuan yang dilaporkan Unity sesuai dengan tujuan aktif di React | Proses navigasi dan build Unity dimiliki 3D Simulator dan Engine Developer
Deployment WebGL | `UnityCampusMap.tsx`, `unityPreloader.ts`, `vercel.json`, `api/health.js` | Unity WebGL v0.8.6.1 dan kode web yang diperiksa pada 21 Juli 2026 | Loader, lokasi file versi, status layanan, kompresi Brotli, tipe konten, dan cache telah dikonfigurasi | Belum terdapat pengukuran jaringan baru yang menggantikan pengamatan v0.8.0
Lighthouse | `reports/lighthouse/latest-summary.md` | Audit 21 Juli 2026 | Kinerja smartphone 86 dan komputer desktop 99; tiga kategori lain 100 | Hasil merupakan pengujian laboratorium lokal, bukan data pengguna nyata atau pengukuran versi v0.8.6.1
Tindak lanjut pengujian pengguna | Subbab 3.5, `content/shared/testing/results.json`, dan folder dokumentasi revisi | Pemeriksaan 21 Juli 2026 | Bukti visual, pemeriksaan kode sumber, pengujian otomatis, dan sumber resmi terdokumentasi | Tangkapan layar revisi bukan kuesioner UAT kedua
[/TABLE]

Perintah reproduksi untuk repositori web adalah sebagai berikut:

1. `npm test` menjalankan suite Vitest satu kali.
2. `npm run lint` menjalankan pemeriksaan ESLint.
3. `npm run build` menjalankan TypeScript build dan production build Vite.
4. `npm run lighthouse` membangun aplikasi, menjalankan pratinjau lokal, dan memperbarui audit smartphone serta komputer desktop.
5. Pemeriksaan deployment dilakukan melalui `GET /api/health`, `GET /api/unity/data`, dan `GET /api/unity/names`, lalu dilengkapi skenario negatif perubahan data Supabase tanpa sesi yang sah.

Pengujian ulang memerlukan variabel lingkungan yang valid. Kunci rahasia, kata sandi administrator, kunci dengan hak akses tinggi, dan kredensial layanan tidak disertakan dalam lampiran atau perintah pengujian.

---

# LAMPIRAN 6. Dokumen Administratif Penelitian dan Pelaksanaan UAT

Lampiran ini memuat dokumen administratif yang mendukung pelaksanaan riset dan UAT tim. Dokumen ditampilkan sebagai bukti korespondensi dan koordinasi; keberadaannya tidak digunakan untuk mengubah Humas menjadi pihak pemberi persetujuan formal, menyatakan UPA TIK sebagai mitra pengguna, atau mengklaim serah terima sistem kepada institusi.

## A. Administrasi Riset

Rangkaian awal administrasi riset ditunjukkan melalui surat permohonan tanggal 22 Januari 2026 pada [FIGREF:admin_research_request_jan_2026] dan lembar disposisi tanggal 4 Februari 2026 pada [FIGREF:admin_research_disposition_feb_2026]. Kedua dokumen tersebut menunjukkan proses permohonan dan penerusan koordinasi internal, bukan surat penerimaan atau pengesahan hasil sistem.

[FIGURE:admin_research_request_jan_2026]
[FIGCAPTION:Surat Permohonan Riset Tim, 22 Januari 2026]

[FIGURE:admin_research_disposition_feb_2026]
[FIGCAPTION:Lembar Disposisi Permohonan Riset, 4 Februari 2026]

Dokumen lanjutan bulan Juli terdiri atas surat permohonan pada [FIGREF:admin_research_request_jul_2026] dan lembar disposisi pada [FIGREF:admin_research_disposition_jul_2026]. Versi digital surat digunakan karena lebih terbaca daripada foto duplikat dokumen yang sama, sedangkan lembar disposisi dipertahankan sebagai bukti proses koordinasi.

[FIGURE:admin_research_request_jul_2026]
[FIGCAPTION:Surat Permohonan Riset Lanjutan, 16 Juli 2026]

[FIGURE:admin_research_disposition_jul_2026]
[FIGCAPTION:Lembar Disposisi Permohonan Riset Lanjutan, 16 Juli 2026]

## B. Administrasi UAT Tertutup

Pelaksanaan UAT diawali dengan surat permohonan tanggal 9 Juli 2026 yang ditampilkan pada [FIGREF:admin_uat_request_jul_2026]. Dokumen tersebut mencatat kelompok calon evaluator yang diajukan, termasuk dosen, perwakilan Humas, dan calon pengelola. Komposisi peserta yang digunakan dalam laporan mengikuti daftar undangan akhir dan formulir yang terisi, bukan seluruh pihak yang disebut pada tahap permohonan.

[FIGURE:admin_uat_request_jul_2026]
[FIGCAPTION:Surat Permohonan Pelaksanaan UAT, 9 Juli 2026]

Tindak lanjut resmi ditunjukkan melalui surat undangan pada [FIGREF:admin_uat_invitation_jul_2026_p1] dan daftar undangan pada [FIGREF:admin_uat_invitation_jul_2026_p2]. Dokumen mencatat pelaksanaan pada 15 Juli 2026 serta komposisi peserta; dokumen tersebut tidak menunjukkan adanya UAT bersama sampel pengguna publik.

[FIGURE:admin_uat_invitation_jul_2026_p1]
[FIGCAPTION:Surat Undangan Pelaksanaan UAT, 13 Juli 2026]

[FIGURE:admin_uat_invitation_jul_2026_p2]
[FIGCAPTION:Daftar Undangan UAT Tertutup, 15 Juli 2026]
