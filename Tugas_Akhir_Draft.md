# PENGEMBANGAN SISTEM NAVIGASI SPASIAL DAN OPTIMASI ENGINE UNITY WEBGL PADA DENAH VIRTUAL UPNVJ KAMPUS PONDOK LABU

Muammar Faiz Khairul Anam

2210511138

INFORMATIKA

FAKULTAS ILMU KOMPUTER

UNIVERSITAS PEMBANGUNAN NASIONAL VETERAN JAKARTA

2026

# DAFTAR GAMBAR

[Dibentuk otomatis oleh Microsoft Word melalui pipeline dokumen.]

# DAFTAR TABEL

[Dibentuk otomatis oleh Microsoft Word melalui pipeline dokumen.]

# DAFTAR LAMPIRAN

[Dibentuk otomatis oleh Microsoft Word melalui pipeline dokumen.]

---

# BAB I PENDAHULUAN

## 1.1 Latar Belakang

<!-- PIPELINE:INCLUDE content/shared/bab1/latar-belakang-umum.md -->

Visualisasi lingkungan kampus dalam bentuk tiga dimensi dapat membantu pengguna memahami hubungan spasial antarlokasi melalui representasi yang lebih interaktif daripada denah statis. Penelitian mengenai visualisasi kampus berbasis WebGL dan media kampus digital menunjukkan bahwa teknologi tiga dimensi dapat digunakan sebagai sarana penyajian informasi serta orientasi ruang berbasis web (Muharam et al. 2023; Taurusta et al. 2024). Dalam konteks Smart Campus, denah virtual tidak cukup hanya menampilkan bentuk bangunan, tetapi juga perlu menyediakan mekanisme navigasi yang dapat mengarahkan pengguna menuju gedung atau fasilitas yang dipilih.

Sistem integrasi denah virtual UPNVJ menggabungkan dashboard publik berbasis React, layanan API berbasis Vercel Serverless Functions, database Supabase, dan modul Unity WebGL. Dashboard berfungsi sebagai titik interaksi pencarian, sedangkan Unity menampilkan lingkungan kampus dan menjalankan navigasi spasial. Integrasi membentuk dua alur: React mengirim perintah ke Unity melalui `SendMessage`, sedangkan Unity mengirim callback `OnNavigationCompleted` hanya setelah navigasi selesai secara normal. Unity juga mengambil data gedung dan fasilitas secara mandiri melalui `HTTP GET /api/unity/data`. Field `unity_object_name` menjadi penghubung antara data pada database, GameObject sasaran, dan callback tujuan di React.

Keberadaan model tiga dimensi belum secara langsung menjamin pengalaman navigasi yang baik. Engine perlu menghitung jalur pada area yang dapat dilalui, menampilkan rute yang mengikuti kontur lantai dan tangga, menyajikan nama tujuan yang mudah dipahami, serta menghentikan navigasi ketika pengguna telah mencapai sasaran. Pada sisi interaksi, pengguna desktop membutuhkan kendali pandangan yang tidak terhambat batas layar, sedangkan pengguna perangkat bergerak membutuhkan kontrol sentuh yang sesuai. Pada sisi distribusi, build Unity harus dikonfigurasi agar dapat dijalankan melalui peramban dengan ukuran dan perilaku pemuatan yang dapat dievaluasi.

Berdasarkan kebutuhan tersebut, laporan ini berfokus pada kontribusi penulis sebagai 3D Simulator dan Engine Developer. Kontribusi tersebut mencakup pengembangan modul `BuildingDatabase`, `NavigationReceiver`, dan `NavigationGuide`; pembentukan rute melalui subdivisi linear, raycast vertikal, dan *moving average*; optimasi *renderer* melalui `BuildingCulling`; konfigurasi *build* melalui `WebGLOptimizer`; kontrol *Pointer Lock* dan *joystick* virtual; pemilihan titik awal, minimap, penanda tujuan, tutorial adaptif; serta alat editor `DatabaseSyncChecker`. Pembuatan aset tiga dimensi merupakan lingkup 3D Asset Designer dan Database Schema Designer, sedangkan pengembangan dashboard, API, dan jembatan integrasi web merupakan lingkup Full Stack Web Developer, System Integrator, dan DevOps Engineer.

Dengan fokus tersebut, penelitian ini diarahkan untuk menghasilkan modul simulator yang dapat mengubah data tujuan dari sistem web menjadi panduan navigasi di dalam lingkungan tiga dimensi. Laporan tidak hanya membahas hasil akhir visual, tetapi juga menelusuri rancangan alur data, logika pencarian dan rendering rute, pengendalian pengguna lintas perangkat, optimasi build WebGL, serta mekanisme pemeriksaan konsistensi antara database dan scene Unity.

## 1.2 Identifikasi Masalah

Berdasarkan latar belakang yang telah diuraikan, masalah yang menjadi fokus laporan ini diidentifikasi sebagai berikut:

1. Belum tersedia mekanisme pada engine tiga dimensi yang mengubah pilihan lokasi dari dashboard web menjadi rute navigasi spasial yang dapat diikuti pengguna di lingkungan kampus virtual.
2. Titik sudut hasil perhitungan jalur NavMesh perlu diolah menjadi rute visual yang lebih halus dan tetap mengikuti perubahan elevasi permukaan, termasuk lantai dan tangga.
3. Scene kampus yang memuat banyak objek memerlukan mekanisme optimasi renderer dan konfigurasi build WebGL agar penggunaan sumber daya serta proses pemuatan dapat dikendalikan dan diuji.
4. Perbedaan karakteristik perangkat desktop dan perangkat bergerak memerlukan pola kontrol yang berbeda tanpa memisahkan implementasi utama simulator.
5. Ketergantungan navigasi pada `unity_object_name` menimbulkan risiko ketidaksesuaian antara data pada database dan nama GameObject di dalam scene Unity.

## 1.3 Batasan Masalah

Untuk menjaga pembahasan tetap sesuai dengan kontribusi penulis, batasan masalah ditetapkan sebagai berikut:

1. Area yang direpresentasikan dibatasi pada lingkungan UPNVJ Kampus Pondok Labu yang tersedia di dalam scene Unity proyek.
2. Target distribusi simulator adalah WebGL yang dijalankan melalui peramban modern, bukan aplikasi native Android, iOS, atau desktop.
3. Navigasi hanya berlaku pada area yang telah tercakup oleh NavMesh hasil bake dan tidak mencakup pathfinding di luar area tersebut.
4. Sistem menggunakan karakter dan kamera sudut pandang orang ketiga untuk satu pengguna dan tidak mencakup *multiplayer*, berbagi lokasi waktu nyata, atau navigasi berbasis GPS.
5. React memanggil metode Unity melalui `SendMessage`, sedangkan *runtime* Unity menyediakan event browser `OnNavigationCompleted`. Implementasi antarmuka dan listener React merupakan lingkup Full Stack Web Developer, System Integrator, dan DevOps Engineer.
6. Unity mengambil data runtime melalui endpoint `/api/unity/data`, tetapi implementasi endpoint, autentikasi admin, serta dashboard web tidak dibahas sebagai kontribusi penulis.
7. Pembuatan model gedung, tekstur, dan tata letak aset tiga dimensi merupakan lingkup 3D Asset Designer dan Database Schema Designer; laporan ini membahas pemanfaatan aset tersebut oleh *engine*.
8. Optimasi yang dibahas meliputi Building Culling serta konfigurasi build WebGL berupa Brotli, decompression fallback, IL2CPP, dan managed stripping. Klaim peningkatan performa kuantitatif hanya dinyatakan apabila bukti pengukuran tersedia.
9. Evaluasi khusus terhadap waktu komputasi rute, *frame rate*, ukuran *build*, dan waktu muat hanya dinyatakan berhasil apabila didukung artefak pengujian yang dapat diverifikasi.

Pembagian peran dan tanggung jawab pada proyek sistem dijelaskan lebih detail dalam [TABREF:peran_tanggung_jawab].

[TABLE-ID:peran_tanggung_jawab]
[TABLECAPTION:Peran dan Tanggung Jawab]

[TABLE]
Role | Tugas dan Tanggung Jawab
3D Asset Designer dan Database Schema Designer | Merancang aset visual 3D dan hierarki prefab beserta `Pointer`, serta merancang skema database Supabase PostgreSQL, ERD, kebijakan RLS, dan rancangan trigger basis data.
3D Simulator dan Engine Developer | Mengembangkan *runtime* Unity WebGL, termasuk `BuildingDatabase`, `NavigationReceiver`, `DatabaseSyncChecker`, navigasi NavMesh, interaksi pengguna, optimasi performa, dan proses *build* WebGL.
Full Stack Web Developer, System Integrator, dan DevOps Engineer | Mengembangkan Public Dashboard dan Admin Panel React, REST API pada Vercel Serverless Functions, integrasi Supabase Auth dan CRUD, *bridge* React ke Unity, pencatatan analitik aplikasi, pengujian web, serta deployment dan operasional layanan web; Express dan Umami dikelola sebagai jalur opsional.
[/TABLE]

## 1.4 Tujuan dan Manfaat

### 1.4.1 Tujuan

Tujuan pengembangan yang dibahas dalam laporan ini adalah sebagai berikut:

1. Merancang dan mengimplementasikan alur navigasi Unity yang menerima `unity_object_name`, menemukan GameObject tujuan, menghitung jalur NavMesh, serta menampilkan panduan rute di dalam scene tiga dimensi.
2. Menerapkan subdivisi linear, raycast vertikal, dan moving average untuk menghasilkan rute visual yang lebih rapat serta mengikuti kontur permukaan yang dapat dilalui.
3. Mengembangkan mekanisme optimasi renderer dan konfigurasi build untuk mendukung distribusi simulator melalui platform WebGL.
4. Menyediakan kontrol karakter dan kamera third-person yang sesuai bagi pengguna desktop melalui Pointer Lock dan bagi pengguna perangkat bergerak melalui joystick virtual.
5. Mengembangkan mekanisme pemeriksaan sinkronisasi `unity_object_name` antara database dan hierarki GameObject melalui `DatabaseSyncChecker`.
6. Menyediakan pemilihan titik awal yang tervalidasi terhadap NavMesh, minimap, penanda tujuan, dan tutorial yang menyesuaikan jenis perangkat.
7. Mengevaluasi fungsi modul simulator melalui skenario pengujian yang dapat ditelusuri dan tidak bergantung pada klaim performa tanpa bukti.

### 1.4.2 Manfaat

Manfaat yang diharapkan dari pengembangan ini adalah sebagai berikut:

1. Bagi mahasiswa dan pengunjung, simulator menyediakan media orientasi ruang yang dapat menampilkan tujuan dan rute secara interaktif melalui peramban.
2. Bagi pengelola sistem, penggunaan `unity_object_name` dan alat pemeriksaan sinkronisasi membantu mengurangi risiko terputusnya hubungan antara data fasilitas dan objek pada scene Unity.
3. Bagi tim pengembang, pemisahan tanggung jawab antarmodul memudahkan pemeliharaan logika pengambilan data, penerimaan perintah, perhitungan rute, rendering, kontrol, dan konfigurasi build.
4. Bagi pengembangan akademik selanjutnya, laporan ini dapat menjadi rujukan implementasi navigasi NavMesh, penyesuaian rute berbasis raycast dan moving average, serta optimasi aplikasi Unity yang didistribusikan melalui WebGL.

## 1.5 Jadwal Kegiatan

Pelaksanaan proyek berlangsung selama enam bulan dan dirangkum pada [TABREF:jadwal_kegiatan]. Tanda `X` menunjukkan bulan pelaksanaan utama setiap kegiatan. Tabel ini menggambarkan tahapan proyek yang telah dilaksanakan oleh tim, bukan rencana pekerjaan mendatang.

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

Jadwal pada [TABREF:jadwal_kegiatan] merupakan jadwal tim. Kontribusi Faiz pada setiap fase tetap dibatasi pada pengembangan *runtime* Unity dan tidak mencakup implementasi *backend*, *frontend*, basis data, atau pembuatan aset tiga dimensi. Pelaksanaannya dijabarkan sebagai berikut:

1. Pada fase desain arsitektur dan antarmuka, Faiz merancang posisi Unity dalam arsitektur sistem, kontrak `unity_object_name`, alur `SendMessage`, hierarki *scene*, NavMesh, dan penyajian rute.
2. Pada fase pengembangan *backend*, Faiz menyiapkan `BuildingDatabase` sebagai konsumen kontrak `/api/unity/data`. Endpoint dan pengelolaan basis data tetap menjadi tanggung jawab anggota tim terkait.
3. Pada fase pengembangan *frontend*, Faiz menyiapkan metode publik Unity, yaitu `NavigateTo`, `StopNavigation`, `SetSpawn`, dan `SetDevice`, agar dapat dipanggil melalui jembatan web tanpa mengklaim implementasi React.
4. Pada fase integrasi dan pengujian, Faiz mengembangkan navigasi NavMesh, rute visual, kontrol lintas perangkat, pemilihan titik awal, minimap, tutorial, *completion event*, optimasi, dan *build* WebGL, kemudian menguji perilaku modul tersebut bersama alur sistem.
5. Pada fase revisi dan penulisan, Faiz memperbaiki temuan yang berkaitan dengan *runtime* Unity, melakukan pengujian ulang pada versi yang sama, serta menyusun bukti dan pembahasan teknis.
6. Dokumentasi dilakukan selama enam bulan untuk menjaga keterlacakan rancangan, konfigurasi, kode sumber, hasil pengujian, dan bukti visual.

## 1.6 Sistematika Penulisan

Laporan ini disusun dalam empat bab dengan sistematika sebagai berikut:

1. BAB I PENDAHULUAN menjelaskan konteks proyek, fokus masalah simulator, batasan kontribusi, tujuan, manfaat, jadwal kegiatan, dan susunan laporan.
2. BAB II RANCANGAN PROYEK menguraikan hasil observasi, kebutuhan simulator, arsitektur sistem, rancangan alur data, rancangan navigasi dan rendering rute, rancangan optimasi, rancangan kontrol, serta rencana pengujian.
3. BAB III IMPLEMENTASI PROYEK membahas profil mitra, implementasi modul Unity, konfigurasi scene dan build WebGL, bukti kontribusi, hasil pengujian bersama, hasil pengujian khusus simulator, serta analisis tindak lanjut UAT yang berkaitan dengan engine.
4. BAB IV PENUTUP menyajikan kesimpulan berdasarkan hasil yang telah memiliki bukti dan saran pengembangan lebih lanjut.

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

Solusi yang diusulkan untuk lingkup penulis adalah modul simulator Unity WebGL yang menerima identitas tujuan dari dashboard, mengambil data nama tampilan dari API, menemukan Transform yang sesuai, menghitung rute pada NavMesh, dan menampilkan panduan visual hingga pengguna mencapai tujuan. Solusi dilengkapi dengan optimasi renderer, konfigurasi build, pola kontrol lintas perangkat, dan alat pemeriksaan sinkronisasi data.

### 2.2.1 Identifikasi Kebutuhan Fungsional

Kebutuhan fungsional modul simulator dirumuskan sebagai berikut:

1. Sistem harus dapat memuat scene tiga dimensi kampus melalui peramban tanpa instalasi aplikasi native.
2. Sistem harus mengambil data gedung dan fasilitas dari endpoint `/api/unity/data` ketika runtime dimulai.
3. Sistem harus menerima perintah `NavigateTo(unity_object_name)` dari React melalui `NavigationReceiver`.
4. Sistem harus mencari GameObject tujuan secara case-insensitive serta menyediakan fallback apabila cache belum terbentuk atau objek tidak aktif.
5. Sistem harus menghitung rute dari posisi pengguna menuju Transform tujuan pada area NavMesh yang tersedia.
6. Sistem harus menampilkan garis rute yang mengikuti kontur lantai dan tangga.
7. Sistem harus menampilkan nama tujuan yang mudah dibaca dan informasi jarak tersisa.
8. Sistem harus menghentikan navigasi serta membersihkan garis dan label ketika pengguna telah berada di dalam batas `stopDistance`.
9. Sistem harus menyediakan perintah untuk menghentikan navigasi secara manual.
10. Sistem harus menyediakan Pointer Lock untuk kontrol kamera desktop dan joystick virtual untuk perangkat bergerak.
11. Sistem harus menonaktifkan renderer bangunan yang berada di luar jarak relevan melalui mekanisme Building Culling.
12. Sistem harus menyediakan menu editor untuk menerapkan konfigurasi build WebGL yang ditetapkan proyek.
13. Sistem harus menyediakan alat editor untuk membandingkan `unity_object_name` dari API dengan GameObject di dalam scene.
14. Sistem harus memungkinkan pengguna memilih titik awal yang diproyeksikan ke area NavMesh sebelum kontrol karakter diaktifkan.
15. Sistem harus menampilkan minimap yang mengikuti posisi pemain dan menunjukkan tujuan navigasi aktif.
16. Sistem harus memberikan penanda visual pada tujuan serta mengirim event `OnNavigationCompleted` ketika pemain mencapai `stopDistance`; penghentian manual tidak memicu event kedatangan.
17. Sistem harus menyediakan tutorial kontrol yang menyesuaikan mode desktop atau mobile berdasarkan pesan `SetDevice`.

### 2.2.2 Identifikasi Kebutuhan Teknis

NavMesh merupakan representasi area yang dapat dilalui dan digunakan oleh komponen navigasi untuk mendukung pencarian jalur pada *scene*. Paket AI Navigation Unity menyediakan komponen untuk membangun dan menggunakan NavMesh pada waktu edit maupun *runtime* (Unity Technologies 2026a). Proyek menggunakan Unity 6 dengan Universal Render Pipeline, AI Navigation, New Input System, TextMeshPro, dan target *build* WebGL.

Titik sudut hasil `NavMeshPath` digunakan sebagai dasar pembentukan garis navigasi. Implementasi final membagi setiap segmen secara linear berdasarkan jarak sampling, memproyeksikan setiap titik ke permukaan melalui raycast vertikal, lalu menerapkan moving average agar perubahan posisi antartitik tidak bergerigi. Pendekatan ini mengikuti kode aktif pada scene final dan menggantikan rancangan interpolasi kurva yang tidak lagi dipanggil oleh alur runtime.

Pointer Lock API menyediakan perubahan posisi relatif tetikus, mempertahankan input meskipun pergerakan melewati batas layar, dan menyembunyikan kursor selama penguncian. Karakteristik tersebut digunakan untuk mengendalikan kamera sudut pandang orang ketiga di peramban (MDN Web Docs 2025). Untuk perangkat sentuh, New Input System menyediakan konsep *on-screen control* yang dapat memetakan widget antarmuka ke kontrol perangkat virtual (Unity Technologies 2026c).

Distribusi WebGL menggunakan *build* Unity yang dikompresi. Dokumentasi Unity menjelaskan bahwa Brotli menghasilkan berkas yang lebih kecil daripada gzip dengan konsekuensi waktu kompresi *build* yang lebih panjang, dan server perlu mengirim header yang sesuai agar peramban memproses berkas terkompresi dengan benar (Unity Technologies 2026b). Konfigurasi teknis proyek mencakup Brotli, *decompression fallback*, IL2CPP, dan *managed stripping*, dengan validasi *runtime* untuk memastikan kode yang digunakan tidak ikut terhapus oleh proses *stripping*.

### 2.2.3 Identifikasi Kebutuhan Non-Fungsional

Kebutuhan non-fungsional modul simulator dirumuskan sebagai berikut:

1. Performa: pemuatan model tiga dimensi harus memberikan umpan balik yang jelas, memanfaatkan kompresi dan *cache*, serta dievaluasi melalui pengukuran pada perangkat, jaringan, dan *build* yang terdokumentasi. Laporan tidak menetapkan target waktu muat tanpa dasar pengukuran.
2. Efisiensi: perhitungan ulang rute dilakukan ketika perpindahan pengguna melewati ambang `pathUpdateDistance`, bukan pada setiap frame.
3. Kompatibilitas: simulator mendukung peramban desktop modern dan memprioritaskan Chrome Android sebagai kebutuhan perangkat bergerak.
4. Usabilitas: sistem menampilkan status pemuatan, nama tujuan, jarak tersisa, serta kontrol yang sesuai dengan jenis perangkat.
5. Keandalan: target yang tidak ditemukan atau respons API yang gagal harus menghasilkan pesan kesalahan yang dapat ditelusuri tanpa menyebabkan aplikasi berhenti secara tidak terkendali.
6. Keterpeliharaan: tanggung jawab pengambilan data, penerimaan perintah, perhitungan rute, rendering, culling, dan validasi editor dipisahkan ke dalam modul yang berbeda.
7. Konsistensi data: nilai `unity_object_name` diperlakukan case-insensitive saat lookup, tetapi konvensi penulisan sumber tetap menggunakan huruf kecil dan underscore.

## 2.3 Rancangan Proyek

### 2.3.1 Rencana Pengembangan

Metode prototyping merupakan pendekatan pengembangan yang membentuk versi awal sistem untuk dievaluasi, diperbaiki, dan dikembangkan secara iteratif berdasarkan umpan balik (Pricillia 2021). Pendekatan ini digunakan karena perilaku navigasi, bentuk rute, kontrol pengguna, dan performa WebGL memerlukan evaluasi langsung pada scene serta peramban.

Tahap pengembangan dirangkum pada [FIGREF:diagram_tahap_pengembangan] yang menggambarkan hubungan antara analisis kebutuhan, perancangan, pembuatan prototipe, evaluasi, perbaikan, integrasi, dan pengujian.

[FIGURE:diagram_tahap_pengembangan]
[FIGCAPTION:Tahap Pengembangan Modul Simulator dan Engine]

Iterasi pengembangan modul Unity dirancang melalui tahapan berikut:

1. Menentukan kebutuhan navigasi dan kontrak data bersama pengembang dashboard, API, database, dan aset tiga dimensi.
2. Menetapkan hierarki scene, target `Pointer`, area NavMesh, serta komponen runtime yang diperlukan.
3. Membuat prototipe penerimaan tujuan dan perhitungan jalur dasar menggunakan NavMesh.
4. Menambahkan penghalusan rute, raycast kontur, label tujuan, jarak, dan penghentian otomatis.
5. Menambahkan kontrol desktop dan perangkat bergerak.
6. Menambahkan Building Culling, WebGL optimizer, dan Database Sync Checker.
7. Mengintegrasikan build Unity pada alur sistem melalui kontrak `NavigateTo`, `StopNavigation`, `SetSpawn`, `SetDevice`, dan event `OnNavigationCompleted`; implementasi dashboard React dan endpoint serverless tetap dikerjakan anggota integrasi.
8. Menjalankan pengujian fungsional, pengujian modul, pengukuran performa, perbaikan, dan pengujian ulang.

### 2.3.2 Perancangan Arsitektur Sistem

Arsitektur sistem menjelaskan pembagian tanggung jawab antara dashboard, denah dua dimensi, Unity WebGL, API, database, dan layanan analitik. Hubungan antarkomponen diperlihatkan pada [FIGREF:diagram_arsitektur], dengan Unity WebGL ditempatkan sebagai modul visualisasi tiga dimensi yang berjalan di dalam peramban.

[FIGURE:diagram_arsitektur]
[FIGCAPTION:Arsitektur Integrasi Sistem dan Unity WebGL]

Alur utama yang berkaitan dengan peran penulis dirancang sebagai berikut:

1. React menampilkan daftar hasil pencarian gedung dan fasilitas kepada pengguna.
2. Ketika pengguna memilih tujuan, React memanggil `SendMessage("NavigationReceiver", "NavigateTo", unity_object_name)`.
3. `NavigationReceiver` mencari Transform sasaran yang sesuai di dalam scene.
4. `NavigationGuide` menghitung jalur pada NavMesh dan menampilkan garis rute, nama tujuan, serta jarak tersisa.
5. Secara terpisah, `BuildingDatabase` menarik data dari `/api/unity/data` untuk membentuk cache `unityObjectNames` dan `realNames`.
6. Ketika pengguna tiba secara normal, `CompleteNavigation()` membersihkan garis dan label, kemudian Unity mengirim `OnNavigationCompleted` dengan `unity_object_name` tujuan.
7. Ketika pengguna membatalkan navigasi melalui `StopNavigation()` atau target tidak ditemukan, rute dibersihkan tanpa mengirim callback kedatangan.

Pemetaan komponen arsitektur pada [TABREF:pemetaan_arsitektur_engine] digunakan untuk membedakan bagian yang menjadi kontribusi penulis dan bagian yang hanya menjadi kontrak integrasi bersama.

[TABLE-ID:pemetaan_arsitektur_engine]
[TABLECAPTION:Pemetaan Komponen Arsitektur terhadap Peran Engine]
[TABLE]
Komponen | Fungsi pada Sistem | Hubungan dengan Modul Faiz | Batas Klaim
Dashboard React | Menampilkan pencarian, pemilihan tujuan, dan canvas Unity | Mengirim `NavigateTo`, `StopNavigation`, `SetSpawn`, serta `SetDevice` | Implementasi antarmuka dan listener bukan kontribusi penulis
Vercel Serverless Functions | Menyediakan endpoint data Unity dan endpoint daftar nama | Dikonsumsi oleh `BuildingDatabase` dan `DatabaseSyncChecker` | Pembuatan endpoint bukan kontribusi penulis
Supabase Database | Menyimpan data gedung, fasilitas, dan kunci `unity_object_name` | Menjadi sumber identitas teknis target scene | Skema, RLS, dan audit log bukan kontribusi penulis
Unity WebGL | Menjalankan scene, kontrol, navigasi, rendering rute, dan tool editor | Menjadi ruang kontribusi utama penulis | Klaim dibatasi pada skrip, konfigurasi, dan bukti Unity
Browser dan Hosting | Menjalankan build WebGL serta menyajikan `.data` dan `.wasm` | Meneruskan callback `OnNavigationCompleted` dari Unity ke listener React | Infrastruktur hosting dan listener React dijelaskan sebagai konteks integrasi
[/TABLE]

### 2.3.3 Perancangan Aktor dan Batas Interaksi

Use case merupakan model yang menjelaskan interaksi aktor dengan fungsi sistem dari sudut pandang kebutuhan pengguna (Kurniawan 2018). Hubungan pengguna, dashboard React, Vercel API, dan pengembang Unity dengan fungsi modul Unity WebGL disajikan pada [FIGREF:diagram_use_case].

[FIGURE:diagram_use_case]
[FIGCAPTION:Use Case Modul Unity WebGL]

Pada lingkup engine, pengguna berinteraksi dengan pemilihan titik awal, kontrol eksplorasi, rute, minimap, tutorial, dan penghentian navigasi. Dashboard React mengirim perintah ke Unity, sedangkan Vercel API menyediakan data runtime. Pengembang Unity mengonfigurasi scene, memeriksa kesesuaian identifier melalui `DatabaseSyncChecker`, dan membuat build WebGL. Administrator tidak berinteraksi langsung dengan kode engine; perubahan data dilakukan melalui dashboard yang dikelola anggota tim lain.

### 2.3.4 Perancangan Alur Data dan Sinkronisasi

Pemilihan pengalaman Denah 2D atau 3D diperlihatkan pada [FIGREF:diagram_activity_integrasi]. Denah 2D menghitung rute pada jaringan graf dengan algoritma A-star, sedangkan Unity mengambil data runtime, menerima perintah React, dan mengirim callback hanya setelah navigasi tiga dimensi selesai secara normal. Alur tersebut menegaskan bahwa engine merupakan konsumen data dan tidak melakukan operasi CRUD terhadap database.

[FIGURE:diagram_activity_integrasi]
[FIGCAPTION:Activity Diagram Integrasi Denah 2D dan 3D]

Urutan integrasi data, penerimaan tujuan, dan penyelesaian navigasi ditunjukkan pada [FIGREF:diagram_sequence_sinkronisasi]. Peran penulis dimulai ketika Unity meminta data, membentuk cache, mencocokkan nama, menghitung rute, dan memancarkan callback penyelesaian normal. Validasi callback dan notifikasi pada dashboard tetap menjadi implementasi anggota integrasi.

[FIGURE:diagram_sequence_sinkronisasi]
[FIGCAPTION:Sequence Diagram Integrasi Data dan Penyelesaian Navigasi]

Rangkuman penggunaan diagram rancangan pada [TABREF:pemetaan_diagram_rancangan] menjaga agar diagram UML dan arsitektur dibaca sesuai batas kontribusi penulis. Diagram perancangan skema database tidak digunakan dalam laporan ini karena berada pada lingkup Database Developer; penulis hanya mendokumentasikan kontrak data yang dikonsumsi Unity.

[TABLE-ID:pemetaan_diagram_rancangan]
[TABLECAPTION:Pemetaan Diagram Rancangan terhadap Kebutuhan Laporan Faiz]
[TABLE]
Artefak Rancangan | Informasi yang Dipakai | Relevansi untuk Role Faiz | Catatan Batas Kontribusi
Diagram arsitektur | Jalur React, Denah 2D, Unity, API, Supabase, dan analitik opsional | Menentukan posisi Unity sebagai runtime visualisasi | Komponen web dan API hanya konteks integrasi
Use Case Modul Unity WebGL | Interaksi pengguna, React, API, dan pengembang dengan modul Unity | Menentukan fungsi eksplorasi, navigasi, tooling, dan build | Fitur dashboard tidak diklaim sebagai implementasi Faiz
Activity Diagram Integrasi | Pemilihan Denah 2D atau 3D sampai keluaran navigasi | Membedakan graf A-star dan runtime Unity NavMesh | Operasi CRUD dan Denah 2D tetap berada di luar engine
Sequence Diagram Integrasi | Urutan pemuatan data, perintah navigasi, penyelesaian normal, dan pembatalan | Menjadi dasar `BuildingDatabase`, `NavigationReceiver`, `NavigationGuide`, serta callback runtime | Listener React hanya disebut sebagai kontrak
Activity Diagram NavMesh | Validasi target, pembentukan path, rendering, pembaruan, kedatangan, dan pembatalan | Menjadi dasar algoritme navigasi serta rendering rute | Struktur data dan aset tiga dimensi mengikuti ownership anggota lain
[/TABLE]

### 2.3.5 Perancangan Konsumsi Data dan Lifecycle Engine

`BuildingDatabase` dirancang sebagai sumber data runtime bagi modul engine. Ketika scene dimulai, komponen memasuki kondisi pemuatan, mengirim `HTTP GET` ke `/api/unity/data`, memeriksa keberhasilan respons, lalu memproses koleksi `gedung` dan `fasilitas`. Pada Editor, method `Awake()` menetapkan endpoint produksi `https://dashboard-profile-upnvj.vercel.app/api/unity/data`; pada build WebGL, URL diganti menjadi `/api/unity/data` agar mengikuti origin hosting. Nilai lama `/api/unity/names` yang masih tersimpan pada Inspector scene bukan endpoint runtime `BuildingDatabase` dan tidak digunakan sebagai bukti hasil akhir. Engine tidak membuat atau mengubah data pada database karena operasi tersebut berada di luar lingkup penulis.

Struktur minimum setiap entitas yang digunakan engine terdiri atas nama tampilan dan `unity_object_name`. Data gedung serta fasilitas diproses melalui alur yang sama agar target dari kedua koleksi dapat dicari tanpa membedakan sumbernya pada tahap navigasi. Cache `unityObjectNames` menyimpan identitas teknis yang tersedia, sedangkan dictionary `realNames` memetakan identitas tersebut ke nama yang ditampilkan pada label tujuan. Kunci cache dinormalisasi secara case-insensitive, tetapi bentuk sumber tetap mengikuti konvensi huruf kecil dan underscore.

Lifecycle data engine dirancang melalui kondisi berikut:

1. Belum dimuat: scene baru aktif dan belum menerima respons API; modul lain tidak boleh mengasumsikan cache telah tersedia.
2. Sedang dimuat: permintaan API sedang berlangsung dan status pemuatan dipertahankan sampai respons selesai diproses.
3. Berhasil: respons valid menghasilkan cache `unityObjectNames`, dictionary `realNames`, dan status `isLoaded` yang dapat dibaca modul lain.
4. Respons dengan koleksi kosong: JSON valid dengan `gedung` dan `fasilitas` kosong tetap menyelesaikan parsing, mengaktifkan `isLoaded`, dan menghasilkan cache kosong; perilaku aktual ini perlu dibedakan dari respons null atau JSON tidak valid.
5. Permintaan atau parsing gagal: pesan kesalahan dicatat untuk penelusuran tanpa menghentikan aplikasi secara tidak terkendali.
6. Nama tidak ditemukan: `GetRealName()` mengembalikan input asli sebagai fallback agar label tidak kosong.

Hubungan data dengan scene dimulai ketika `unity_object_name` dari hasil pencarian React diterima oleh `NavigationReceiver`. Identitas tersebut dicocokkan dengan cache dan nama GameObject pada child `Pointer`. Transform hasil pencocokan menjadi tujuan `NavigationGuide`, sedangkan `realNames` digunakan hanya sebagai teks tampilan. Pemisahan ini menjaga agar perubahan label tidak mengubah identitas teknis navigasi.

### 2.3.6 Perancangan Sistem Navigasi NavMesh

NavMesh digunakan untuk merepresentasikan area yang dapat dilalui oleh pengguna virtual. Perancangan dimulai dengan menentukan sumber geometri, area walkable, hambatan, dan karakteristik agen sebelum proses bake. Area indoor, outdoor, jalur antargedung, dan tangga perlu terhubung secara fisik melalui collision mesh agar rute lintas lantai atau lintas gedung dapat dihitung.

Alur pencarian tujuan dirancang dengan tahapan berikut:

1. `NavigationReceiver` menerima `unity_object_name` dari React.
2. Sistem mencari Transform pada cache dengan perbandingan case-insensitive.
3. Apabila cache belum tersedia atau target tidak ditemukan, sistem membangun ulang cache dan melakukan pencarian fallback termasuk pada objek tidak aktif.
4. Transform yang ditemukan diteruskan ke `NavigationGuide`.
5. `NavigationGuide` memproyeksikan posisi pengguna ke NavMesh dengan radius maksimum 2 m. Tujuan dicoba dengan radius dekat maksimum 2 m, kemudian menggunakan fallback 5 m apabila diperlukan; hasil sampling ditolak apabila selisih vertikalnya melebihi 2 m agar tidak berpindah lantai secara keliru.
6. Sistem memeriksa status jalur sebelum menampilkan rute.
7. Jalur dihitung ulang ketika pergerakan pengguna melewati `pathUpdateDistance` sebesar 1 m.
8. Scene menyimpan `stopDistance` 5 m, tetapi kode runtime membatasi ambang kedatangan ke rentang 0,5–2 m. Navigasi hanya selesai ketika path berstatus lengkap, jarak jalur tersisa tidak melebihi 2 m, dan jarak pemain terhadap endpoint NavMesh juga tidak melebihi 2 m.

Rancangan ketahanan jalur mempertahankan path lengkap terakhir ketika rekalkulasi gagal sesaat di batas polygon, tangga, atau NavMesh link. Path parsial atau invalid tidak menggantikan rute aktif dan tidak dianggap sebagai kedatangan. Sistem menjadwalkan percobaan ulang dengan interval 1 detik sampai path lengkap tersedia atau navigasi dibatalkan. Keseluruhan validasi target, pembentukan path, pembaruan rute, kedatangan, dan pembatalan dirangkum pada [FIGREF:diagram_alur_navmesh_rendering].

[FIGURE:diagram_alur_navmesh_rendering]
[FIGCAPTION:Activity Diagram Navigasi NavMesh dan Rendering Rute]

Urutan tersebut diringkas pada [TABREF:alur_navigasi_engine] agar hubungan input, pemrosesan, dan keluaran setiap modul dapat ditelusuri tanpa mengklaim proses pencarian atau API sebagai implementasi Faiz.

[TABLE-ID:alur_navigasi_engine]
[TABLECAPTION:Alur Algoritme Penerimaan Tujuan dan Navigasi]
[TABLE]
Tahap | Komponen | Input | Keluaran
1 | `NavigationReceiver` | `unity_object_name` dari kontrak `SendMessage` | Nama target yang dinormalisasi dan permintaan pencarian Transform
2 | Cache target | Cache `unityObjectNames`, hierarki scene, dan child `Pointer` | Transform tujuan yang cocok secara case-insensitive
3 | `NavigationGuide` | Posisi pemain dan Transform tujuan | Posisi awal serta akhir yang diproyeksikan ke NavMesh
4 | Unity NavMesh | Dua posisi hasil `NavMesh.SamplePosition` | `NavMeshPath` dari `NavMesh.CalculatePath`
5 | State navigasi | Status path, perpindahan pemain, `stopDistance` | Rute aktif, pembaruan jalur, atau event selesai navigasi
[/TABLE]

### 2.3.7 Perancangan Rendering Rute

Titik `corners` dari hasil NavMesh dapat memiliki jarak antartitik yang besar dan perubahan arah yang tajam. Implementasi final tidak memanggil helper Catmull–Rom yang masih tersisa pada skrip. Setiap segmen aktif dibagi secara linear dengan `pointSpacing` 0,4 m, kemudian raycast diarahkan ke bawah agar posisi vertikal garis mengikuti permukaan lantai atau tangga. Moving average dengan `smoothingWindow` 4 diterapkan pada koordinat akhir, sedangkan titik awal dan akhir dipertahankan.

Alur rendering dirancang sebagai berikut:

1. Mengambil titik sudut dari `NavMeshPath` yang valid.
2. Membagi setiap segmen secara linear dengan jarak sampling 0,4 m.
3. Melakukan `Physics.RaycastNonAlloc()` dari 1,5 m di atas titik sampling sejauh 3 m ke bawah menggunakan `groundMask` dan mengabaikan trigger.
4. Mengabaikan collider pemain dan target dari kandidat hasil raycast, lalu menerima permukaan terdekat apabila selisih vertikalnya tidak melebihi toleransi 0,75 m.
5. Menambahkan `lineHeightOffset` 0,6 m agar garis tidak berimpit dengan permukaan.
6. Menghaluskan kumpulan titik dengan moving average berjendela 4 tanpa menggeser titik awal dan akhir.
7. Mengirim kumpulan titik akhir ke `LineRenderer` dengan lebar 0,2 m dan material putus-putus yang dibentuk saat runtime.
8. Memperbarui label nama tujuan dan jarak jalur tersisa.

Transformasi titik mentah menjadi garis yang dirender dirangkum pada [TABREF:alur_rendering_rute_rancangan]. Bukti visual hasil akhirnya diberikan melalui tangkapan layar rute aktif dan perubahan elevasi pada BAB III; perbandingan titik internal sebelum dan sesudah pemrosesan tidak diklaim apabila log debug belum tersedia.

[TABLE-ID:alur_rendering_rute_rancangan]
[TABLECAPTION:Alur Pemrosesan Titik Rute sebelum Rendering]
[TABLE]
Tahap | Operasi | Parameter final | Hasil
1 | Mengambil `corners` | `NavMeshPath` valid | Segmen rute mentah
2 | Subdivisi linear | `pointSpacing` 0,4 m | Titik sampling lebih rapat
3 | Raycast vertikal | `surfaceProbeHeight` 1,5 m, jarak total 3 m, `groundMask` | Kandidat permukaan tanpa alokasi baru per titik
4 | Seleksi permukaan | Toleransi vertikal 0,75 m; collider pemain dan target diabaikan | Titik mengikuti lantai atau tangga terdekat tanpa meloncat ke permukaan lain
5 | Offset ketinggian | `lineHeightOffset` 0,6 m | Garis tidak berimpit dengan permukaan
6 | Moving average | `smoothingWindow` 4, titik awal dan akhir dipertahankan | Rute lebih halus tanpa mengubah endpoint
7 | `LineRenderer` | `lineWidth` 0,2 m, material putus-putus | Rute visual dan label tujuan pada Game View
[/TABLE]

### 2.3.8 Perancangan Optimasi Performa

Building Culling dirancang untuk mengurangi jumlah renderer aktif ketika bangunan berada di luar jarak atau pandangan kamera yang relevan terhadap pengguna. Sistem memindai objek bertag `Cullable`, menyimpan status awal seluruh renderer, menggunakan child `CullingPoint` atau pivot root sebagai titik acuan, lalu memeriksa jarak kuadrat pada interval 1 detik. Lapis camera-frustum culling menggunakan kamera gameplay dengan pemeriksaan setiap 0,1 detik, padding bounds 10 m, dan grace period 0,35 detik untuk mengurangi flicker. Pemeriksaan frustum dihentikan saat selector spawn/overview terbuka, renderer yang terlihat oleh minimap dipertahankan, dan target navigasi selalu dikecualikan dari penonaktifan. Scene final menyimpan `minRenderDistance` dan `maxRenderDistance` sama-sama 200 m sehingga `startingRenderDistance` 500 m dikunci menjadi 200 m. Walaupun `adaptationMode` bernilai `Combined`, jarak efektif tidak dapat berubah sebelum kedua batas tersebut dibedakan; oleh karena itu laporan tidak mengklaim adaptasi jarak dinamis atau hysteresis yang tidak terdapat pada konfigurasi aktif.

WebGL optimizer dirancang sebagai menu editor satu klik yang menerapkan konfigurasi build proyek. Konfigurasi meliputi target WebGL, kompresi Brotli, decompression fallback, backend IL2CPP, tingkat managed stripping, dan opsi produksi terkait. Setiap pengaturan perlu diverifikasi pada build final karena konfigurasi agresif dapat mengurangi ukuran berkas tetapi juga berisiko menghapus jalur kode yang hanya dipanggil melalui reflection.

Rencana pembandingan Building Culling menggunakan posisi kamera, scene, lintasan, durasi, dan perangkat yang sama. Capture NVIDIA Statistics Overlay digunakan sebagai bukti runtime pendahuluan, bukan hasil benchmark, karena tidak menyediakan draw call, renderer aktif, frame time Unity, durasi sampling, dan indikator state yang cukup. Hasil sebelum–sesudah baru disimpulkan setelah capture Unity Profiler memenuhi kondisi uji tersebut.

### 2.3.9 Perancangan Kontrol Pengguna

Kontrol desktop menggunakan Pointer Lock setelah tindakan klik pengguna pada canvas. Pergerakan relatif tetikus digunakan untuk rotasi pandangan, sedangkan tombol ESC melepaskan kunci kursor. Rancangan harus tetap mengikuti kebijakan keamanan peramban yang mensyaratkan aktivasi melalui interaksi pengguna.

Kontrol perangkat bergerak menggunakan prefab `UI_Virtual_Joystick` yang memetakan gerakan sentuh ke New Input System. `WebPlatformSync.SetDevice(string)` menerima nilai `mobile` atau `desktop`, mengubah visibilitas joystick, dan meneruskan mode perangkat kepada antarmuka spawn serta tutorial. Tangkapan layar desktop, mobile, dan tutorial adaptif telah tersedia; respons Pointer Lock, joystick, serta perubahan mode tetap memerlukan rekaman pada build final.

### 2.3.10 Perancangan DatabaseSyncChecker

`DatabaseSyncChecker` dirancang sebagai alat editor yang memeriksa konsistensi `unity_object_name` sebelum build WebGL dibuat. Tool menerima daftar identitas dari `/api/unity/names`, memindai hierarki scene secara rekursif termasuk child `Pointer`, menormalisasi perbandingan secara case-insensitive, lalu membandingkan himpunan nama dari API dengan himpunan nama pada scene. Pada implementasi aktif, kategori nama API yang cocok atau hilang menggunakan seluruh hierarki, sedangkan kategori objek scene yang belum terdaftar di database hanya memeriksa root object scene.

Hasil pemeriksaan dirancang dalam tiga kategori:

1. Synchronized: nama tersedia pada API dan memiliki GameObject padanan di dalam scene.
2. Missing in Scene: nama tersedia pada API, tetapi tidak ditemukan pada hierarki scene.
3. Not Registered in Database: root GameObject tersedia pada scene, tetapi namanya tidak terdapat pada data API.

Tool perlu menyediakan ringkasan jumlah setiap kategori, daftar nama yang dapat ditelusuri, dan tindakan untuk menyalin daftar ketidaksesuaian. Respons API kosong dibedakan dari kondisi seluruh data tersinkronisasi agar hasil tidak menyesatkan. Apabila permintaan gagal, format respons tidak sesuai, atau scene belum tersedia, tool menampilkan pesan kesalahan yang dapat ditindaklanjuti dan tidak mengubah hierarki scene secara otomatis.

### 2.3.11 Perancangan Pemilihan Titik Awal dan Minimap

Pemilihan titik awal dirancang agar pengguna tidak langsung ditempatkan pada pivot model gedung yang mungkin berada di luar area berjalan. `SpawnPointRegistry` menyimpan pasangan `unityObjectName`, nama tampilan fallback, Transform spawn aman, anchor peta, serta radius sampling khusus bila diperlukan. `SpawnReceiver.SetSpawn(string)` mencari entri secara case-insensitive, memproyeksikan posisi ke NavMesh, menghentikan navigasi lama, menonaktifkan kontrol selama teleportasi, memindahkan karakter, lalu mengaktifkan kontrol kembali setelah spawn berhasil.

Scene final memuat 16 titik spawn, radius sampling umum 5 m, `groundOffset` 0,05 m, dan kewajiban pemilihan awal. Override 120 m digunakan untuk `cipto_mangunkusumo`, sedangkan dua titik gerbang belakang memakai 40 m. Nilai override merupakan toleransi pencarian NavMesh dan bukan jarak perpindahan yang diklaim sebagai hasil ukur.

`SpawnSelectionUI` dirancang untuk menampilkan overview ketika titik awal belum dipilih dan berubah menjadi minimap setelah spawn berhasil. Kamera minimap ditempatkan pada ketinggian 120 m, menggunakan ukuran ortografis 28 ketika mengikuti pemain, dan menampilkan marker pemain serta tujuan aktif. Render texture minimap berukuran 512 piksel, overview 1280 × 720 piksel, ukuran panel desktop 230 × 230 piksel, dan panel mobile 170 × 170 piksel. Bukti tampilan overview dan minimap ditempatkan pada Subbab 3.4.7, sedangkan bukti konfigurasi registry ditempatkan pada Subbab 3.3.5.

Transisi mode overview dan gameplay menggunakan `DayNightCycle` agar selector spawn memiliki kondisi visual yang lebih jelas. Saat overview dibuka, waktu dapat diatur ke `overviewStartTime` 9 dan fog menggunakan `overviewFogDensity` 0; setelah spawn berhasil, mode gameplay mengembalikan fog ke `gameplayFogDensity` 0,01. Nilai tersebut merupakan konfigurasi scene dan bukan pengukuran performa atau klaim kepemilikan aset lingkungan.

### 2.3.12 Perancangan Visual Tujuan dan Tutorial Adaptif

`DestinationHighlighter` dirancang sebagai penanda visual tambahan di luar garis rute. `NavigationGuide` membuat komponen tersebut secara otomatis apabila referensi Inspector kosong, memanggil `Show()` ketika tujuan ditetapkan, dan memanggil `Hide()` ketika navigasi berhenti atau komponen dinonaktifkan. Material pulse serta fallback bingkai portal digunakan untuk membantu pengguna mengenali gedung atau pintu tujuan tanpa mengubah mesh sumber.

Tutorial dirancang sebagai alur runtime yang dibentuk otomatis setelah scene dimuat. `GameTutorialController` menunggu sinkronisasi perangkat dan penyelesaian spawn, lalu menyediakan langkah bergerak, melihat sekeliling, berlari, melompat, serta pencarian tujuan. Instruksi dan sorotan kontrol dibedakan antara desktop dan mobile. Penyelesaian tutorial disimpan melalui `PlayerPrefs` per jenis perangkat, sementara tombol F8 dan F9 hanya menjadi fasilitas simulasi pada Editor.

Ketika pemain mencapai `stopDistance`, plugin `ReactBridge.jslib` memungkinkan Unity mengirim event browser `OnNavigationCompleted` satu kali dengan payload `unity_object_name`. `StopNavigation()` manual dan pergantian tujuan hanya membersihkan status tanpa mengirim event kedatangan. Listener serta tampilan pemberitahuan pada React merupakan kontribusi Full Stack Web Developer, System Integrator, dan DevOps Engineer dan tidak dijadikan gambar bukti Faiz. Kontribusi penulis dibatasi pada pengiriman event dari *runtime* Unity; bukti yang relevan untuk bagian ini adalah log pengiriman Unity atau Console browser dan pengujian ulang yang memastikan penghentian manual tidak mengirim event selesai.

### 2.3.13 Perancangan Occlusion Culling dan Transisi Overview–Gameplay

`CampusOcclusionInstaller` dirancang sebagai editor tool tambahan untuk menandai renderer gedung yang memenuhi syarat sebagai occluder atau occludee, mengecualikan renderer dinamis dan material transparan, mengatur `OcclusionArea`, serta menghasilkan `OcclusionCullingData.asset`. Rancangan memakai ukuran minimum occluder 5 m, padding area `(20, 10, 20)` m, `smallestOccluder` 5 m, `smallestHole` 0,5 m, dan `backfaceThreshold` 100. Kamera gameplay `MainCamera` menggunakan hasil bake, sedangkan `MinimapCamera` tidak menggunakannya agar seluruh area peta tetap tersedia.

Transisi state dirancang agar `SpawnSelectionUI` menyimpan lalu menonaktifkan occlusion kamera gameplay ketika overview dibuka, kemudian memulihkannya setelah spawn berhasil atau selector ditutup. Perubahan tersebut berjalan bersama transisi waktu dan fog yang dirancang pada Subbab 2.3.11. Pemetaan state pada [TABREF:state_transisi_occlusion] menjadi acuan pengujian agar mode overview dan gameplay tidak dinilai hanya dari tangkapan layar diam.

[TABLE-ID:state_transisi_occlusion]
[TABLECAPTION:Rancangan State Occlusion dan Fog pada Overview–Gameplay]
[TABLE]
State Runtime | Kamera Gameplay | Kamera Minimap | Fog | Kondisi yang Diverifikasi
Selector spawn terbuka | Occlusion disimpan lalu dinonaktifkan | Occlusion tetap nonaktif | 0 | Seluruh area dan marker pemilihan dapat dilihat
Spawn berhasil atau selector ditutup | Occlusion dipulihkan ke status scene final | Occlusion tetap nonaktif | 0,01 | Kamera gameplay kembali menggunakan data bake tanpa menghilangkan area minimap
[/TABLE]

Keberadaan data *bake* dan perubahan status telah didokumentasikan sebagai implementasi *engine*. Dampaknya terhadap jumlah *renderer*, *draw call*, dan *frame time* berstatus Belum diverifikasi sampai diukur pada skenario yang sama.

## 2.4 Rencana Pengujian Proyek

Pengujian dirancang untuk memeriksa perilaku eksternal modul, bukan hanya memastikan bahwa metode dapat dipanggil. Cakupan skenario pada [TABREF:rencana_pengujian_unity] meliputi kondisi berhasil, gagal, dan tepi yang relevan dengan data, navigasi, interaksi, optimasi, serta distribusi WebGL.

### 2.4.1 Data dan Integrasi Runtime

Pengujian `BuildingDatabase` menggunakan respons API valid, koleksi kosong, format tidak valid, kegagalan jaringan, dan pencarian nama yang tidak dikenal. Kondisi awal mencatat endpoint, *fixture* respons, dan status *cache*. Hasil yang diperiksa meliputi perubahan `isLoaded`, isi `unityObjectNames`, isi `realNames`, *fallback* `GetRealName()`, dan pesan log.

Pengujian `DatabaseSyncChecker` menggunakan *fixture* yang memuat nama cocok, nama yang hanya ada pada API, dan objek yang hanya ada pada *scene*. Skenario tambahan mencakup *child* `Pointer`, variasi kapitalisasi, respons kosong, format tidak valid, dan kegagalan jaringan. Alat editor harus memberikan diagnosis yang jelas tanpa mengubah *scene* secara otomatis.

### 2.4.2 Navigasi, Rute, dan Penyelesaian Navigasi

Pengujian navigasi mencakup target yang tersedia pada *cache*, perbedaan kapitalisasi, target tidak ditemukan, tujuan pada dan di luar NavMesh, pergantian tujuan, penghentian manual, serta penghentian otomatis pada `stopDistance`. Pengujian rute mencakup jalur lurus, tikungan, perubahan elevasi, dan tangga. Highlighter juga diperiksa ketika tujuan dipilih, diganti, atau dibersihkan.

Event `OnNavigationCompleted` diuji pada *build* WebGL bersama listener React. Skenario mencapai `stopDistance` harus menghasilkan payload `unity_object_name` tepat satu kali, sedangkan `StopNavigation()` manual atau pergantian tujuan tidak boleh dianggap sebagai kedatangan. Implementasi listener dan notifikasi pada React tetap menjadi kontribusi Iman.

### 2.4.3 Interaksi, Spawn, Minimap, dan Tutorial

Pengujian desktop memeriksa aktivasi *Pointer Lock* setelah tindakan pengguna, gerak kamera, pelepasan kursor melalui ESC, dan kondisi kegagalan penguncian. Pengujian perangkat bergerak memeriksa visibilitas dan respons *joystick* tanpa mengganggu tampilan desktop. Perangkat, sistem operasi, peramban, resolusi, dan metode input dicatat pada setiap hasil.

Pengujian spawn mencakup identitas terdaftar, identitas tidak dikenal, proyeksi NavMesh, radius *sampling*, dan pemulihan kontrol. Minimap diperiksa saat beralih dari tampilan awal ke mode mengikuti pemain, termasuk pembaruan penanda pemain dan tujuan. Tutorial diuji pada mode desktop dan perangkat bergerak untuk memeriksa langkah, progres, *skip*, penyimpanan status, dan sinkronisasi melalui `SetDevice`.

### 2.4.4 Optimasi, Occlusion Culling, dan Build WebGL

Pengujian `BuildingCulling` menggunakan *scene*, posisi pemain, rute kamera, durasi, dan perangkat yang sama. Pemeriksaan mencakup ambang jarak 200 m, *frustum* `MainCamera`, *grace period*, pengecualian target navigasi, dan pemeliharaan *renderer* minimap. `CampusOcclusionInstaller` diperiksa melalui konfigurasi *static occluder*, *static occludee*, `OcclusionArea`, data bake, serta perbedaan status occlusion pada kamera utama dan minimap. Transisi tampilan awal ke permainan juga memeriksa pemulihan occlusion dan nilai fog.

Pengujian *build* mencatat versi Unity, Player Settings, ukuran berkas, waktu muat, perangkat, peramban, kondisi jaringan, serta header `Content-Encoding` dan `Content-Type`. Kebutuhan pemuatan dinilai secara adaptif melalui umpan balik pemuatan, konfigurasi kompresi, dan pengukuran aktual. Laporan tidak menetapkan target kurang dari 10 detik tanpa dasar pengukuran.

[TABLE-ID:rencana_pengujian_unity]
[TABLECAPTION:Rencana Pengujian Modul Simulator dan Engine]
[TABLE]
ID | Modul | Skenario | Hasil yang Diharapkan | Bukti
UT-01 | BuildingDatabase | API mengembalikan data gedung dan fasilitas valid | Cache terbentuk, `isLoaded` aktif, dan nama tampilan dapat diambil | Log Play Mode dan respons API
UT-02 | BuildingDatabase | Nama tidak dikenal diminta melalui `GetRealName()` | Sistem mengembalikan input asli dan tidak menghasilkan nilai null | Log Play Mode
UT-03 | NavigationReceiver | Nama tersedia pada cache | Transform yang tepat diteruskan ke `NavigationGuide` | Play Mode Test
UT-04 | NavigationReceiver | Nama tidak tersedia atau berbeda kapitalisasi | Fallback dijalankan, pesan warning muncul, dan aplikasi tidak berhenti | Play Mode Test
UT-05 | NavigationGuide | Target berada pada area NavMesh | Jalur valid terbentuk dan `LineRenderer` aktif | Rekaman Play Mode
UT-06 | NavigationGuide | Pengguna mencapai `stopDistance` | Rute dan label dibersihkan secara otomatis | Rekaman Play Mode
UT-07 | NavigationGuide | Navigasi sedang aktif lalu pengguna menghentikan atau mengganti tujuan | Rute lama dibersihkan dan state baru tidak menghasilkan garis ganda | Rekaman Play Mode
UT-08 | Route Rendering | Jalur melewati tikungan dan perubahan elevasi | Subdivisi linear, raycast, moving average, dan `LineRenderer` menghasilkan garis yang mengikuti permukaan | Tangkapan layar dan rekaman
UT-09 | Pointer Lock | Pengguna mengaktifkan dan melepas kontrol desktop | Kursor terkunci setelah klik dan terlepas melalui ESC | Uji peramban desktop
UT-10 | Joystick Virtual | Build dibuka pada perangkat bergerak dan desktop | Joystick berfungsi pada mobile dan tidak mengganggu desktop | Uji lintas perangkat
UT-11 | Building Culling | Pengguna bergerak melintasi ambang tetap 200 m | Renderer berubah sesuai aturan, target navigasi tetap aktif, dan metrik sebelum-sesudah dapat dibandingkan | Unity Profiler, konfigurasi scene, dan rekaman
UT-12 | WebGLOptimizer | Menu konfigurasi dijalankan pada project final | Player Settings WebGL sesuai konfigurasi final yang terdokumentasi | Tangkapan layar Player Settings dan log Console
UT-13 | WebGL Build | Build produksi dimuat melalui hosting yang ditetapkan | Berkas termuat tanpa kesalahan MIME atau compression header | DevTools Network dan log browser
UT-14 | DatabaseSyncChecker | Data API dan scene memiliki nama cocok, hilang, dan berlebih | Kategori cocok dan hilang memakai hierarki rekursif, kategori scene belum terdaftar memakai root object, dan daftar dapat disalin | Tangkapan layar editor dan fixture uji
UT-15 | DatabaseSyncChecker | Endpoint kosong, tidak valid, atau gagal | Tool menampilkan pesan yang jelas dan tidak mengubah scene | Log dan tangkapan layar error
UT-16 | SpawnPointRegistry | Pengguna memilih titik spawn terdaftar yang berada dalam radius NavMesh | Karakter dipindahkan ke posisi valid dan kontrol dipulihkan | Log, tangkapan layar, dan rekaman
UT-17 | SpawnPointRegistry | Nama tidak terdaftar atau posisi berada di luar radius sampling | Spawn ditolak dengan pesan diagnosis tanpa memindahkan karakter | Log Play Mode
UT-18 | SpawnSelectionUI dan MinimapFollow | Spawn selesai dan navigasi menuju tujuan aktif | Overview berubah menjadi minimap serta marker pemain dan tujuan diperbarui | Tangkapan layar dan rekaman desktop/mobile
UT-19 | DestinationHighlighter | Tujuan dipilih, diganti, lalu navigasi dihentikan | Highlighter mengikuti tujuan aktif dan dibersihkan ketika selesai | Tangkapan layar dan rekaman
UT-20 | GameTutorialController | Tutorial dijalankan pada mode desktop dan mobile | Instruksi, progres, dan sorotan kontrol sesuai perangkat | Tangkapan layar dan rekaman dua mode
UT-21 | WebPlatformSync | React mengirim `SetDevice("mobile")` dan `SetDevice("desktop")` | Joystick, spawn UI, dan tutorial mengikuti mode perangkat | Log browser, tangkapan layar, dan rekaman
UT-22 | OnNavigationCompleted | Pengguna mencapai `stopDistance`, lalu diulangi dengan penghentian manual atau pergantian tujuan | Unity mengirim payload `unity_object_name` tepat satu kali hanya saat tiba; pembatalan manual tidak mengirim event kedatangan | Console browser, tangkapan layar, dan rekaman pengujian ulang
UT-23 | Camera Frustum dan Occlusion Culling | Jalankan scene gameplay, putar kamera, buka selector spawn, lalu kembali ke gameplay | Renderer di luar jarak/frustum ditangani sesuai grace period, target navigasi tetap aktif, minimap tidak kehilangan area, dan status occlusion kamera berubah sesuai mode | Profiler, log runtime, Inspector, dan rekaman
UT-24 | Transisi Overview–Gameplay | Buka selector sebelum spawn, pilih spawn valid, lalu buka selector ulang | Fog overview bernilai 0, occlusion gameplay nonaktif saat selector, fog gameplay bernilai 0,01, dan occlusion gameplay pulih setelah spawn | Log runtime, Inspector, dan rekaman
[/TABLE]

Hasil hanya dinyatakan lulus apabila bukti yang diperlukan tersedia. Skenario tanpa artefak pendukung diberi status Belum diverifikasi pada BAB III dan disertai keterangan bukti yang masih diperlukan.

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
Pengguna layanan | Mahasiswa baru, orang tua atau wali, sivitas akademika, dan pengunjung eksternal menjadi kelompok penerima manfaat navigasi | Tidak seluruh kelompok tersebut menjadi peserta UAT tertutup
UPA TIK UPNVJ | Memberikan konteks koordinasi teknis, kebijakan data, kemungkinan integrasi, wawancara, dan penyerahan pakta integritas | Bukan mitra pengguna dan tidak dinyatakan telah menerima implementasi sistem
Tim pengembang | Mengembangkan sistem sesuai pembagian tanggung jawab setiap anggota | Faiz hanya mengklaim implementasi *runtime* Unity, tooling editor, optimasi, dan *build* WebGL
[/TABLE]

## 3.2 Metode Implementasi

Implementasi dibangun menggunakan Unity 6000.4.1f1 pada `SceneUtama`. Seluruh nilai konfigurasi dan bukti hasil pada subbab berikut berasal dari versi proyek final yang sama. Identitas versi kode sumber dipusatkan pada logbook dan indeks bukti lampiran agar pembahasan utama tetap berfokus pada cara kerja sistem.

### 3.2.1 Implementasi BuildingDatabase

`BuildingDatabase` diimplementasikan sebagai modul pengambilan data runtime di dalam Unity. Method `Awake()` mengganti nilai Inspector menjadi endpoint produksi `/api/unity/data`, sedangkan conditional compilation menggunakan URL relatif `/api/unity/data` pada build WebGL. Modul memproses koleksi `gedung` dan `fasilitas`, lalu mengganti cache secara atomik setelah parsing berhasil. Cache `unityObjectNames` digunakan untuk mengetahui identitas yang tersedia, dictionary `realNames` digunakan oleh label navigasi, dan cache tambahan menghubungkan ID gedung dengan target gedung maupun fasilitas.

Modul menyediakan `GetRealName()` dengan fallback ke nilai input ketika nama tidak ditemukan. Respons JSON valid dengan dua koleksi kosong tetap menghasilkan `isLoaded = true` dan cache kosong, sedangkan respons null, parsing gagal, atau kegagalan request tidak mengaktifkan status tersebut. Setelah pemuatan berhasil, modul memanggil `NavigationReceiver.RebuildCache()` agar daftar Transform dibentuk dari data terbaru. Bukti log runtime ditempatkan pada Subbab 3.4.2 agar pembacaan hasil tetap berada pada bagian implementasi.

Hierarki prefab yang menjadi tujuan pemetaan data diperlihatkan pada [FIGREF:impl_pointer_hierarchy]. Child `Pointer` menampung GameObject yang namanya mengikuti `unity_object_name`, sehingga titik target dapat dipisahkan dari mesh visual bangunan. Hierarki tersebut didokumentasikan sebagai kontrak scene; kontribusi penulis dimulai pada proses pencarian dan penggunaan Transform, bukan pada pembuatan model atau struktur aset sumber.

[FIGURE:impl_pointer_hierarchy]
[FIGCAPTION:Hierarki Prefab Gedung dengan Child Pointer di Unity]

### 3.2.2 Implementasi NavigationReceiver dan NavigationGuide

`NavigationReceiver` menjadi titik masuk perintah dari JavaScript. Metode publik `NavigateTo(string unityObjectName)` dipanggil melalui `SendMessage` dan bertanggung jawab menemukan Transform tujuan. Input kosong ditolak dengan peringatan. Pencarian awal menggunakan *cache* agar permintaan berulang tidak memindai seluruh *scene*. Apabila target belum tersedia, sistem membangun ulang *cache* dan melakukan pencarian tambahan, termasuk pada objek tidak aktif. Perbandingan nama dilakukan dengan `ToLowerInvariant()`, sedangkan kegagalan dicatat sebagai peringatan tanpa melempar pengecualian yang menghentikan aplikasi.

Transform yang ditemukan diteruskan ke `NavigationGuide` bersama `destinationKey` teknis. Modul ini mengelola status tujuan aktif, menjalankan `NavMesh.CalculatePath()`, mengirim titik jalur ke renderer, serta memperbarui label nama dan jarak. `CompleteNavigation()` hanya dipanggil ketika path berstatus lengkap, jarak jalur tersisa dan jarak pemain ke endpoint sama-sama berada dalam ambang efektif maksimal 2 m. Method `StopNavigation()` membersihkan state ketika pengguna membatalkan rute atau memilih tujuan baru tanpa mengirim event kedatangan.

Implementasi final mempertahankan rute lengkap terakhir apabila rekalkulasi baru gagal sesaat, menolak `PathPartial` atau `PathInvalid`, dan mengulangi pencarian setiap 1 detik. Posisi pemain menggunakan radius sampling maksimum 2 m, sedangkan tujuan dapat menggunakan fallback 5 m setelah pencarian dekat gagal. Setiap hasil sampling juga diperiksa terhadap selisih vertikal maksimum 2 m untuk mengurangi risiko snap ke lantai lain.

### 3.2.3 Implementasi Rendering Rute

Implementasi rendering menggunakan titik sudut dari `NavMeshPath` sebagai input. Setiap segmen dibagi secara linear dengan interval 0,4 m. `Physics.RaycastNonAlloc()` ditembakkan dari 1,5 m di atas setiap titik sejauh 3 m ke bawah. Sistem mengabaikan trigger serta collider pemain dan target, lalu memilih permukaan terdekat dalam toleransi vertikal 0,75 m. Koordinat permukaan diberi offset 0,6 m dan dihaluskan dengan moving average berjendela 4 sebelum dikirim ke `LineRenderer`. Fungsi helper Catmull–Rom yang masih terdapat pada skrip tidak dipanggil oleh alur tersebut dan tidak dianggap sebagai implementasi final.

Label tiga dimensi berbasis TextMeshPro menampilkan nama tujuan yang diperoleh melalui `BuildingDatabase` dan jarak tersisa yang dihitung dari posisi pengguna. Insiden awal pada skenario BB-20 menunjukkan bahwa label pernah menampilkan `unity_object_name` akibat skrip testing yang ikut terkompilasi. Tindakan korektif memisahkan skrip testing dari build produksi dan memulihkan nama tampilan fasilitas; hasil pengujian ulang dicatat pada fragment Black Box bersama.

Bukti konfigurasi `LineRenderer`, hasil rute, dan elevasi ditempatkan pada Subbab 3.3.4, 3.4.2, dan 3.4.3 agar setiap gambar memiliki narasi serta rujukan yang jelas.

### 3.2.4 Implementasi Building Culling dan WebGL Settings Optimizer

`BuildingCulling` diimplementasikan untuk mengubah status *renderer* bangunan berdasarkan jarak dan pandangan kamera terhadap pengguna. Modul memindai objek bertag `Cullable`, menyimpan status awal *renderer*, menggunakan `CullingPoint` bila tersedia, memeriksa jarak setiap 1 detik, menjalankan pemeriksaan *frustum* setiap 0,1 detik dengan *padding* 10 m dan *grace period* 0,35 detik, serta mempertahankan *renderer* target navigasi dan area yang diperlukan minimap. *Frustum culling* dijeda saat pemilih spawn terbuka. *Scene* final memakai batas minimum serta maksimum 200 m; akibatnya nilai awal 500 m dikunci menjadi 200 m dan mode `Combined` belum menghasilkan perubahan jarak adaptif. Konfigurasi editor dan data *bake* telah didokumentasikan, tetapi jumlah *renderer* aktif sebelum–sesudah, perubahan status occlusion saat *runtime*, dan hasil Unity Profiler berstatus Belum diverifikasi.

`CampusOcclusionInstaller` ditambahkan sebagai editor tool melalui menu `Tools > UPNVJ > Occlusion`. Tool mengonfigurasi static flags pada renderer gedung, membuat atau memperbarui `OcclusionArea`, mengaktifkan occlusion pada `MainCamera`, menonaktifkannya pada `MinimapCamera`, lalu menjalankan bake `OcclusionCullingData.asset`. Implementasi ini merupakan bagian dari optimasi engine; tidak ada klaim pengurangan draw call atau frame time sebelum profiler tersedia.

`WebGLOptimizer` diimplementasikan melalui menu `Tools > UPNVJ > WebGL > Apply Safe Release Settings` serta alias lama `Tools > UPNVJ > Apply Optimal WebGL Settings`. Menu menerapkan release build, `runInBackground`, Brotli, decompression fallback, data caching, managed stripping High, IL2CPP Master dengan Optimize Size, engine code stripping, WebAssembly 2023, exception support `Explicitly Thrown Exceptions Only`, dan optimasi Wasm Disk Size tanpa LTO. Tool juga menyediakan audit texture tanpa perubahan serta optimasi kandidat texture 3D maksimum 1024 piksel. Konfigurasi editor dan Network ditempatkan pada Subbab 3.3.1 serta 3.4.4.

### 3.2.5 Implementasi Pointer Lock dan Joystick Virtual

Pointer Lock diintegrasikan pada alur kontrol desktop agar rotasi pandangan menggunakan delta pergerakan tetikus dan tidak berhenti ketika kursor mencapai tepi layar. Penguncian dimulai setelah klik pengguna pada canvas dan dilepas melalui ESC. Implementasi perlu menangani perubahan status serta kegagalan penguncian agar pengguna tidak kehilangan kendali atas antarmuka peramban.

Kontrol perangkat bergerak menggunakan prefab `UI_Virtual_Joystick` dan New Input System. `WebPlatformSync.SetDevice(string)` mengubah mode menjadi `mobile` hanya ketika nilai yang diterima cocok secara case-insensitive; nilai lain diperlakukan sebagai `desktop`. Mode tersebut mengatur visibilitas joystick dan diteruskan ke spawn UI serta tutorial. Tangkapan layar desktop dan mobile telah mendokumentasikan perbedaan tampilan, sedangkan respons input serta perpindahan karakter masih memerlukan rekaman dua perangkat dan pengujian ulang build yang sama.

### 3.2.6 Implementasi DatabaseSyncChecker

`DatabaseSyncChecker` diimplementasikan sebagai EditorWindow melalui menu `Tools > UPNVJ > Check Database Sync`. Tool mengirim permintaan ke `/api/unity/names`, mengumpulkan nama GameObject pada hierarki scene secara rekursif, lalu membandingkan kedua himpunan secara case-insensitive. Kategori cocok dan hilang di scene menggunakan seluruh nama hierarki, tetapi kategori yang belum terdaftar di database hanya membandingkan nama root object. Batas tersebut dicatat agar hasil tool tidak ditafsirkan sebagai audit seluruh child scene dari arah sebaliknya.

Antarmuka tool diperlihatkan pada [FIGREF:impl_sync_db_checker] yang menyediakan ringkasan hasil dan tindakan untuk menyalin daftar missing ke clipboard. Pemeriksaan ini digunakan sebelum build agar kesalahan penamaan dapat diperbaiki tanpa menunggu kegagalan navigasi pada runtime.

[FIGURE:impl_sync_db_checker]
[FIGCAPTION:Tampilan UI Database Sync Checker di Unity Editor]

### 3.2.7 Implementasi SpawnPointRegistry, SpawnSelectionUI, dan MinimapFollow

`SpawnPointRegistry` mengelola 16 titik awal dan menyediakan receiver WebGL `SpawnReceiver.SetSpawn(string)`. Sebelum memindahkan karakter, sistem mencari entri secara case-insensitive dan memanggil `NavMesh.SamplePosition()` dengan radius umum 5 m atau override per titik. Navigasi lama dihentikan, input serta `CharacterController` dinonaktifkan sementara, posisi dan rotasi karakter diperbarui, kemudian kontrol dipulihkan dan event `SpawnCompleted` dikirim.

`SpawnSelectionUI` membentuk *canvas*, tampilan awal, tombol penanda, dan panel minimap secara *runtime*. Ketika pemilihan terbuka, kontrol karakter dan *Pointer Lock* dilepas. Setelah spawn berhasil, tampilan awal ditutup dan `MinimapFollow` memindahkan kamera ortografis agar mengikuti pemain. Penanda tujuan hanya ditampilkan ketika navigasi aktif. Bukti tampilan spawn dan minimap ditempatkan pada Subbab 3.4.7, sedangkan konfigurasi `SpawnReceiver` ditempatkan pada Subbab 3.3.5. Log spawn dan rekaman perpindahan belum tersedia.

### 3.2.8 Implementasi DestinationHighlighter dan Event OnNavigationCompleted

`NavigationGuide` mencari `DestinationHighlighter` pada GameObject yang sama dan membuatnya secara otomatis apabila belum tersedia. Ketika `StartNavigation()` dipanggil, highlighter memproses renderer tujuan atau fallback portal. Saat pengguna mencapai `stopDistance`, `CompleteNavigation()` membersihkan visual, memicu event C# `NavigationCompleted`, dan pada build WebGL mengirim `DispatchReactEvent("OnNavigationCompleted", payload)` melalui `ReactBridge.jslib`; payload JSON membawa kunci `unity_object_name`. Sebaliknya, `StopNavigation()` hanya membersihkan state dan mencatat pembatalan tanpa mengirim event selesai. Pemisahan ini mencegah event kedatangan terkirim ketika pengguna membatalkan rute atau mengganti tujuan. Bukti highlight ditempatkan pada Subbab 3.4.7, sedangkan pengiriman event masih memerlukan log dispatch dan pengujian ulang terintegrasi. Tampilan notifikasi React tidak digunakan sebagai bukti kontribusi penulis.

### 3.2.9 Implementasi GameTutorialController, GameTutorialUI, dan WebPlatformSync

`GameTutorialController` dibentuk melalui `RuntimeInitializeOnLoadMethod` apabila scene belum memiliki instance. Controller melakukan auto-wiring terhadap spawn, input, kontrol karakter, sinkronisasi perangkat, dan navigasi. Alur desktop maupun mobile terdiri atas bergerak, melihat sekeliling, berlari, melompat, serta pencarian tujuan apabila receiver tersedia. Progres disimpan terpisah untuk setiap jenis perangkat melalui `PlayerPrefs`, sedangkan `GameTutorialUI` membangun tampilan dan sorotan kontrol secara runtime.

`WebPlatformSync` menerima `SetDevice(string)` dari React, mengatur joystick, meneruskan mode ke `SpawnSelectionUI`, dan mengirim event `DeviceChanged` kepada tutorial. Controller menunggu handshake tersebut sampai 1,75 detik sebelum menggunakan `Application.isMobilePlatform` sebagai fallback. Bukti visual tutorial desktop dan mobile ditempatkan pada Subbab 3.4.7, sedangkan log mode perangkat serta rekaman interaksi masih diperlukan untuk membuktikan perubahan state secara dinamis.

### 3.2.10 Implementasi CampusOcclusionInstaller dan Transisi Overview–Gameplay

`CampusOcclusionInstaller` dijalankan dari menu editor untuk memindai root bertag `Cullable`, mengelompokkan renderer statis sebagai occluder atau occludee, mengabaikan renderer dinamis serta material transparan, mengatur area pandang kampus, dan menghasilkan data bake occlusion untuk `SceneUtama`. `MainCamera` diaktifkan untuk occlusion, sedangkan `MinimapCamera` tidak menggunakannya agar peta tidak kehilangan area.

`SpawnSelectionUI` menyimpan status occlusion kamera gameplay ketika selector dibuka, menonaktifkannya selama overview, lalu mengembalikan status semula setelah spawn atau selector ditutup. `DayNightCycle` mengatur waktu overview ke 09.00 ketika pemilihan awal dibuka, memakai fog 0 pada overview, dan mengubah fog menjadi 0,01 pada mode gameplay. Konfigurasi occlusion editor telah didokumentasikan pada Subbab 3.3.6. Dampak performa serta transisi overview–gameplay tetap menunggu log runtime, rekaman, dan hasil Unity Profiler yang sebanding.

## 3.3 Konfigurasi dan Metadata Sistem

### 3.3.1 Konfigurasi Build WebGL

Konfigurasi *build* final pada proyek Unity 6000.4.1f1 adalah sebagai berikut:

1. Platform target menggunakan WebGL dan hanya `SceneUtama` yang aktif pada konfigurasi build.
2. Skriping backend menggunakan IL2CPP Master dengan mode Optimize Size.
3. Compression Format menggunakan Brotli.
4. Decompression Fallback, Data Caching, `runInBackground`, dan WebAssembly 2023 diaktifkan.
5. Managed Stripping Level menggunakan High dan engine code stripping diaktifkan. `Enable Exceptions` menggunakan `Explicitly Thrown Exceptions Only`, sesuai konfigurasi aman pada `WebGLOptimizer` ketika WebAssembly 2023 aktif.
6. Optimasi Wasm menggunakan Disk Size tanpa LTO, sedangkan development build dan diagnostics dinonaktifkan.
7. Berkas build ditempatkan pada jalur statis yang dikonsumsi dashboard React.
8. Server perlu menyajikan berkas `.br` dan WebAssembly dengan header yang sesuai; pemeriksaan dilakukan melalui panel Network pada DevTools.

Versi Unity Editor yang digunakan diperlihatkan pada [FIGREF:unity_version_editor]. Gambar tersebut mengonfirmasi versi 6000.4.1f1. Target Web aktif dan penggunaan `SceneUtama` ditunjukkan pada [FIGREF:webgl_build_profile], sedangkan identitas revisi kode sumber dicatat pada logbook dan indeks bukti lampiran.

[FIGURE:unity_version_editor]
[FIGCAPTION:Versi Unity Editor 6000.4.1f1]

[FIGURE:webgl_build_profile]
[FIGCAPTION:Build Profile Web Aktif dan SceneUtama]

Konfigurasi Brotli, Data Caching, Decompression Fallback, WebAssembly 2023, dan `Explicitly Thrown Exceptions Only` diperlihatkan pada [FIGREF:webgl_player_settings_publishing]. Konfigurasi kompilasi IL2CPP Master, Optimize for Code Size and Build Time, serta Managed Stripping Level High ditunjukkan pada [FIGREF:webgl_player_settings_other].

[FIGURE:webgl_player_settings_publishing]
[FIGCAPTION:Publishing Settings WebGL]

[FIGURE:webgl_player_settings_other]
[FIGCAPTION:Konfigurasi Kompilasi dan Stripping WebGL]

### 3.3.2 Konvensi Scene dan NavMesh Bake

Scene menempatkan komponen infrastruktur seperti kamera, pemain, `NavigationGuide`, `NavigationReceiver`, `BuildingDatabase`, `BuildingCulling`, sumber NavMesh, dan `PathLine` terpisah dari hierarki objek bangunan. Setiap bangunan dapat memiliki child `Pointer` yang menampung target gedung maupun fasilitas.

NavMesh dibake melalui GameObject `NavMesh_Bake` dengan `NavMeshSurface` Agent Type 0, collect objects seluruh scene, layer mask seluruh layer, render mesh sebagai sumber geometri, voxel 0,1667 m, tile size 256, dan minimum region area 2 m². Agent Type 0 pada `NavMeshAreas.asset` menggunakan radius 0,5 m, tinggi 2 m, maximum slope 45 derajat, dan climb 0,75 m. Tangga memerlukan geometri yang tersambung agar rute lintas lantai dapat dihitung tanpa mengandalkan asumsi visual. Area bake pada [FIGREF:navmesh_bake_config] memperlihatkan konfigurasi Inspector, permukaan walkable, target Web aktif, scene tersimpan, serta Console tanpa error.

[FIGURE:navmesh_bake_config]
[FIGCAPTION:Konfigurasi NavMeshSurface dan Hasil Bake]

### 3.3.3 Konvensi Identitas dan Metadata Tujuan

`unity_object_name` menggunakan huruf kecil dan underscore, misalnya `gedung_rektorat` atau `mht_201`. Nilai ini harus sama dengan nama target pada hierarki `Pointer`, tetapi lookup runtime tetap case-insensitive sebagai toleransi terhadap variasi kapitalisasi. Nama tersebut tidak digunakan sebagai label pengguna; `BuildingDatabase` memetakan identitas teknis ke `nama_gedung` atau `nama_fasilitas`.

### 3.3.4 Konfigurasi Komponen Engine

Konfigurasi komponen *engine* dicatat dari `SceneUtama` pada versi kode sumber yang sama agar implementasi dapat direproduksi. Tampilan editor pada [FIGREF:unity_scene_hierarchy] memperlihatkan lingkungan kampus serta kelompok kamera, pemain, UI, *receiver*, spawn, dan minimap pada hierarki *scene* dengan target Web aktif dan *scene* tersimpan.

[FIGURE:unity_scene_hierarchy]
[FIGCAPTION:SceneUtama dan Hierarki Komponen Engine]

1. NavMeshSurface dan agen: GameObject `NavMesh_Bake`, Agent Type 0, radius 0,5 m, tinggi 2 m, climb 0,75 m, maximum slope 45 derajat, layer mask seluruh layer, serta data bake `SceneUtama`.
2. Layer dan LayerMask raycast: `groundMask` menggunakan seluruh layer; `surfaceProbeHeight` 1,5 m menghasilkan raycast total 3 m ke bawah, sedangkan `surfaceProjectionTolerance` 0,75 m mencegah garis memilih permukaan yang terlalu jauh dari titik NavMesh. Nilai Y titik dipertahankan ketika tidak ada permukaan valid.
3. LineRenderer: lebar awal dan akhir 0,2 m, alignment `TransformZ`, texture mode Tile, tekstur putus-putus 50 persen transparan dibentuk saat runtime, dan offset vertikal 0,6 m.
4. Parameter navigasi: posisi pemain memakai radius sampling maksimum 2 m, tujuan memakai radius dekat maksimum 2 m dengan fallback 5 m, dan selisih vertikal sampling dibatasi 2 m. Scene menyimpan `stopDistance` 5 m, tetapi kode membatasi ambang kedatangan efektif maksimum 2 m. `pathUpdateDistance` bernilai 1 m, interval retry 1 detik, `pointSpacing` 0,4 m, dan `smoothingWindow` 4.
5. Input Actions dan Pointer Lock: *action map*, *binding* desktop dan sentuh, tindakan aktivasi *Pointer Lock*, tombol pelepas, serta *handler* perubahan atau kegagalan status perlu dilengkapi dengan file `.inputactions`, kode sumber, dan tangkapan layar.
6. Joystick virtual: *scene* menyediakan *joystick* gerak dan pandang, tombol sprint, serta tombol lompat; visibilitas induk ditentukan oleh `WebPlatformSync`. Konfigurasi *prefab* dan bukti perangkat belum tersedia.
7. Building Culling: tag `Cullable`, batas minimum 200 m, batas maksimum 200 m, nilai awal 500 m yang dikunci menjadi 200 m, step maksimum 50 m, target 60 fps, interval jarak 1 detik, mode `Combined`, frustum check 0,1 detik, padding bounds 10 m, grace period 0,35 detik, jeda saat selector map terbuka, dan pemeliharaan renderer yang terlihat minimap. Tidak terdapat hysteresis terpisah pada kode aktif.

Nilai serialized `NavigationGuide` yang mengatur jarak berhenti, interval pembaruan, subdivisi titik, smoothing, dan offset garis ditunjukkan pada [FIGREF:navigation_guide_config]. Komponen `PathLine` yang menjadi penerima hasil rute divisualkan pada [FIGREF:path_line_config], sehingga konfigurasi renderer tidak hanya dijelaskan dari skrip.

[FIGURE:navigation_guide_config]
[FIGCAPTION:Konfigurasi NavigationGuide pada Scene Final]

[FIGURE:path_line_config]
[FIGCAPTION:Konfigurasi PathLine untuk Rendering Rute]

Konfigurasi jarak, interval, kamera gameplay, kamera minimap, dan camera-frustum culling pada [FIGREF:building_culling_config] membuktikan nilai Inspector yang digunakan scene. Gambar tersebut merupakan bukti konfigurasi, bukan bukti peningkatan performa.

[FIGURE:building_culling_config]
[FIGCAPTION:Konfigurasi Building Culling Berbasis Jarak dan Frustum]

### 3.3.5 Konfigurasi Spawn, Minimap, dan Tutorial Lintas Perangkat

Konfigurasi orientasi pengguna pada scene final adalah sebagai berikut:

1. `SpawnReceiver` menyimpan 16 titik, memakai `navMeshSampleRadius` 5 m, `groundOffset` 0,05 m, dan `requireInitialSelection` aktif.
2. `cipto_mangunkusumo` memakai override 120 m, sedangkan `gerbang_belakang` dan `gerbang_belakang2` memakai override 40 m.
3. `SpawnSelectionUI` memakai render texture 512 piksel, overview 1280 × 720 piksel, minimap desktop 230 × 230 piksel, dan minimap mobile 170 × 170 piksel.
4. `MinimapFollow` memakai tinggi kamera 120 m, ukuran ortografis mengikuti pemain 28, overview padding 30, dan orientasi utara 0 derajat.
5. `GameTutorialController` memakai target bergerak 4 m, sprint 3 m, rotasi pandang 65 derajat, jeda sukses 0,65 detik, durasi selesai 3 detik, dan timeout sinkronisasi perangkat 1,75 detik.
6. Kontrak lintas perangkat menggunakan `WebPlatformSync.SetDevice("mobile"|"desktop")`, sedangkan spawn memakai `SpawnReceiver.SetSpawn(unity_object_name)`.

Inspector `SpawnReceiver` pada [FIGREF:spawn_registry_config] memperlihatkan 16 entri, radius sampling 5 m, `groundOffset` 0,05 m, `requireInitialSelection`, serta referensi modul terkait. Detail elemen daftar pada [FIGREF:spawn_registry_override] menunjukkan `cipto_mangunkusumo` dengan radius override 120 m serta `gerbang_belakang` dan `gerbang_belakang2` dengan radius override 40 m. Gambar detail tersebut menguatkan nilai yang sebelumnya telah diverifikasi melalui serialisasi `SceneUtama.unity`.

[FIGURE:spawn_registry_config]
[FIGCAPTION:Konfigurasi Umum SpawnPointRegistry]

[FIGURE:spawn_registry_override]
[FIGCAPTION:Konfigurasi Radius Override pada SpawnPointRegistry]

### 3.3.6 Konfigurasi Occlusion Culling dan Transisi Overview–Gameplay

Scene final menyertakan `OcclusionCullingData.asset` hasil konfigurasi `CampusOcclusionInstaller`. Tool menggunakan ukuran minimum occluder 5 m, menambahkan padding area `(20, 10, 20)` m terhadap bounds kampus, serta menetapkan parameter bake `smallestOccluder` 5 m, `smallestHole` 0,5 m, dan `backfaceThreshold` 100. `MainCamera` menggunakan occlusion culling, sedangkan `MinimapCamera` tidak menggunakannya agar peta tidak kehilangan area. Saat selector spawn dibuka, `SpawnSelectionUI` menyimpan lalu menonaktifkan status occlusion kamera gameplay; setelah spawn atau selector ditutup, status tersebut dipulihkan. `DayNightCycle` menggunakan `overviewStartTime` 9, `overviewFogDensity` 0, dan `gameplayFogDensity` 0,01.

Ukuran `OcclusionArea` diperlihatkan pada [FIGREF:occlusion_area_config], sedangkan [FIGREF:occlusion_data_asset] membuktikan keberadaan data bake untuk satu scene dengan 14.315 static renderer. Status checkbox kamera pada [FIGREF:occlusion_main_camera] dan [FIGREF:occlusion_minimap_camera] memperlihatkan bahwa occlusion aktif pada kamera gameplay dan nonaktif pada kamera minimap.

[FIGURE:occlusion_area_config]
[FIGCAPTION:Konfigurasi Campus Gameplay Occlusion Area]

[FIGURE:occlusion_data_asset]
[FIGCAPTION:Data Bake Occlusion Culling SceneUtama]

[FIGURE:occlusion_main_camera]
[FIGCAPTION:Occlusion Culling Aktif pada MainCamera]

[FIGURE:occlusion_minimap_camera]
[FIGCAPTION:Occlusion Culling Nonaktif pada MinimapCamera]

Keempat gambar tersebut mendokumentasikan konfigurasi editor, bukan hasil *benchmark* performa. Perubahan status kamera selama transisi tampilan awal ke permainan berstatus Belum diverifikasi karena log atau rekaman *runtime* belum tersedia.

## 3.4 Laporan Implementasi Proyek

### 3.4.1 Logbook Implementasi Proyek

Ringkasan logbook pada [TABREF:logbook_faiz] disusun berdasarkan fase kerja. Informasi versi kode sumber dipertahankan pada catatan internal, sedangkan laporan menampilkan keluaran dan bukti yang dapat dipahami secara langsung.

[TABLE-ID:logbook_faiz]
[TABLECAPTION:Logbook Implementasi Modul Simulator dan Engine]
[TABLE]
Fase | Kegiatan | Keluaran | Bukti dan Tanggal
Analisis | Menetapkan kontrak `unity_object_name`, alur `SendMessage`, callback, dan kebutuhan navigasi | Spesifikasi integrasi engine | Kontrak tercermin pada diagram arsitektur dan sequence; tanggal analisis belum diverifikasi
Perancangan | Menyusun hierarki scene, NavMesh, alur pathfinding, rute, dan kontrol | Rancangan modul Unity | Enam diagram rancangan dan tabel pemetaan tersedia; tanggal penyusunan belum diverifikasi
Implementasi Data | Mengembangkan `BuildingDatabase` dan cache nama | Modul konsumsi `/api/unity/data` | Kode sumber dan log runtime tersedia; pengujian fixture terkontrol belum diverifikasi
Implementasi Navigasi | Mengembangkan `NavigationReceiver` dan `NavigationGuide` | Navigasi tujuan berbasis NavMesh | Kode sumber, rute aktif, dan pengujian Black Box tersedia; rekaman skenario negatif belum diverifikasi
Implementasi Rute | Menerapkan subdivisi linear, raycast, moving average, label, dan jarak | Rute visual mengikuti kontur | Tangkapan layar rute aktif dan perubahan elevasi tersedia
Implementasi Optimasi | Mengembangkan `BuildingCulling`, frustum culling, occlusion installer, dan `WebGLOptimizer` | Culling dan baseline build | Konfigurasi editor dan tangkapan layar tersedia; Unity Profiler belum diverifikasi
Implementasi Kontrol | Mengintegrasikan Pointer Lock, joystick virtual, dan sinkronisasi perangkat | Kontrol desktop dan mobile | Tangkapan layar kedua mode tersedia; rekaman respons input belum diverifikasi
Implementasi Tool | Mengembangkan `DatabaseSyncChecker` dan `CampusOcclusionInstaller` | Pemeriksaan sinkronisasi dan konfigurasi occlusion | Tangkapan layar hasil pemeriksaan dan konfigurasi tersedia
Implementasi Orientasi | Menambahkan spawn, minimap, highlighter, tutorial adaptif, dan transisi overview | Orientasi dan onboarding pengguna | Tangkapan layar tersedia; rekaman interaksi dan pengujian ulang khusus Unity belum diverifikasi
Integrasi | Menghasilkan build WebGL dan menghubungkannya dengan dashboard | Build WebGL terintegrasi | Versi build aktif tercatat pada sumber fakta internal; bukti reproduksi build belum diverifikasi
Pengujian | Menjalankan skenario, memperbaiki BB-20, dan melakukan pengujian ulang | Hasil uji dan catatan koreksi | Black Box bersama dan bukti pengujian ulang tersedia; test runner khusus Unity belum diverifikasi
[/TABLE]

### 3.4.2 Hasil dan Bukti Implementasi Navigasi

Implementasi menghasilkan alur yang menerima `unity_object_name`, menemukan Transform tujuan, memproyeksikan pemain dan target ke NavMesh, menghitung jalur, menampilkan rute, memperbarui nama serta jarak, dan membedakan penyelesaian otomatis dari pembatalan manual. Hasil Black Box bersama mencatat bahwa pemilihan tujuan, rute terpendek, penghentian otomatis, ketahanan terhadap variasi nama, dan interupsi navigasi telah diuji. Log runtime pada [FIGREF:building_database_runtime_log] menunjukkan snapshot lama sebelum pembersihan seed: `BuildingDatabase` mengambil `/api/unity/data`, memuat 19 gedung dan 331 fasilitas, lalu membentuk 323 `unityObjectNames` sebelum `NavigationReceiver` membangun cache scene. Angka tersebut membuktikan perilaku pemuatan pada saat tangkapan layar dibuat dan tidak dinyatakan sebagai kondisi seed final, yang memuat 311 fasilitas.

[FIGURE:building_database_runtime_log]
[FIGCAPTION:Log Runtime BuildingDatabase dan Cache NavigationReceiver]

Hasil navigasi aktif pada [FIGREF:active_navigation_route] memperlihatkan karakter third-person, garis rute putus-putus, label nama tujuan, jarak tersisa, minimap, dan kontrol mobile dalam satu skenario. Bukti ini mendukung klaim visual rute, tetapi rekaman Play Mode masih diperlukan untuk membuktikan perubahan state ketika pengguna bergerak atau menghentikan navigasi.

[FIGURE:active_navigation_route]
[FIGCAPTION:Rute Navigasi Aktif pada Game View]

Bukti dinamis berupa rekaman Play Mode untuk perpindahan karakter, penghentian otomatis, dan interupsi navigasi belum tersedia.

### 3.4.3 Hasil dan Bukti Rendering Rute

Bagian ini membuktikan perubahan titik sudut `NavMeshPath` menjadi garis rute yang dapat diikuti pengguna. Bukti perlu memperlihatkan corners mentah, hasil subdivisi linear, penyesuaian raycast, hasil moving average, label nama tujuan, dan jarak tersisa. Scene, tujuan, posisi awal, layer permukaan, serta konfigurasi `LineRenderer` harus sama ketika hasil dibandingkan. Rute pada [FIGREF:route_elevation] digunakan sebagai bukti awal bahwa garis mengikuti permukaan pada area yang memiliki perubahan elevasi, bukan sekadar garis lurus pada bidang datar.

[FIGURE:route_elevation]
[FIGCAPTION:Rute pada Perubahan Elevasi Scene]

Alur rendering rute diringkas pada [TABREF:alur_rendering_rute] agar hubungan antara perhitungan NavMesh dan hasil visual dapat dibaca tanpa bergantung hanya pada tangkapan layar.

[TABLE-ID:alur_rendering_rute]
[TABLECAPTION:Alur Rendering Rute pada NavigationGuide]
[TABLE]
Tahap | Input | Proses | Output yang Diverifikasi
Sampling posisi | Posisi pemain dan target | Radius pemain maksimum 2 m; tujuan maksimum 2 m dengan fallback 5 m; selisih vertikal maksimum 2 m | Titik awal dan target berada pada NavMesh tanpa berpindah lantai secara keliru
Perhitungan jalur | Posisi hasil sampling | `NavMesh.CalculatePath()` | `NavMeshPath.corners`
Subdivisi linear | Pasangan titik corner | Pembagian segmen dengan `pointSpacing` 0,4 m | Titik antara yang lebih rapat
Raycast vertikal | Titik hasil subdivisi | `RaycastNonAlloc` dari 1,5 m di atas titik sejauh 3 m; toleransi vertikal 0,75 m | Titik mengikuti permukaan terdekat tanpa menerima collider pemain atau target
Smoothing | Titik hasil raycast | Moving average berjendela 4 | Perubahan arah garis lebih halus
Rendering | Titik akhir dan offset 0,6 m | Pengiriman posisi ke `LineRenderer` | Garis putus-putus tampil pada Game View
[/TABLE]

Bukti berupa rekaman rute pada tikungan atau tangga serta perbandingan titik sudut mentah dengan titik akhir belum tersedia.

### 3.4.4 Hasil dan Bukti Implementasi Optimasi WebGL

Implementasi optimasi mencakup pengendalian *renderer* melalui batas jarak, *camera-frustum culling*, *occlusion culling* berbasis `OcclusionCullingData.asset`, serta konfigurasi produksi melalui WebGL optimizer. Konfigurasi jarak *scene* final efektif tetap 200 m sehingga kemampuan adaptasi jarak belum dapat dinilai. Audit Lighthouse mengukur dashboard secara keseluruhan dan tidak digunakan sebagai bukti optimasi *engine* Faiz. Ukuran *build* prototipe lama juga tidak dipakai sebagai hasil final. Ukuran berkas, waktu muat, *frame rate*, *renderer* aktif, *draw call*, dan memori harus diukur pada skenario yang sama sebelum dan sesudah perubahan.

Validasi Network pada [FIGREF:webgl_network_data] dan [FIGREF:webgl_network_wasm] memperlihatkan pemuatan berkas build WebGL dari browser. Detail header pada [FIGREF:webgl_wasm_mime_headers] menunjukkan `Content-Encoding: br` dan `Content-Type: application/wasm` untuk berkas Wasm, sehingga bukti ini mendukung klaim konfigurasi penyajian file, bukan klaim peningkatan performa.

[FIGURE:webgl_network_data]
[FIGCAPTION:Network Build WebGL untuk Berkas Data]

[FIGURE:webgl_network_wasm]
[FIGCAPTION:Network Build WebGL untuk Berkas Wasm]

[FIGURE:webgl_wasm_mime_headers]
[FIGCAPTION:Header MIME dan Encoding Berkas Wasm]

Log editor pada [FIGREF:webgl_optimizer_console] menunjukkan bahwa menu optimizer berhasil menerapkan WebGL release settings. Bukti ini melengkapi Build Profile dan Player Settings pada Subbab 3.3.1, tetapi tidak membuktikan perubahan waktu muat atau frame rate.

[FIGURE:webgl_optimizer_console]
[FIGCAPTION:Log Penerapan WebGL Release Settings]

Dua capture statistik runtime ditempatkan pada [FIGREF:runtime_stats_culling_enabled] dan [FIGREF:runtime_stats_culling_disabled]. Keduanya memperlihatkan sudut gameplay yang hampir sama, overlay metrik GPU/CPU, serta konfigurasi `BuildingCulling` pada Inspector.

[FIGURE:runtime_stats_culling_enabled]
[FIGCAPTION:Statistik Runtime pada Capture Building Culling Aktif]

[FIGURE:runtime_stats_culling_disabled]
[FIGCAPTION:Statistik Runtime pada Capture Building Culling Nonaktif]

Kedua gambar belum menjadi *benchmark* sebelum–sesudah yang konklusif karena menggunakan NVIDIA Statistics Overlay, bukan Unity Profiler. Durasi *sampling*, identitas perangkat, *draw call*, *renderer* aktif, *frame time* Unity, dan indikator status komponen juga belum tercatat. Angka sesaat pada tampilan tersebut tidak digunakan untuk menyimpulkan peningkatan performa. Hasil kuantitatif berstatus Belum diverifikasi sampai tersedia Unity Profiler dan tabel *benchmark* pada kondisi yang terdokumentasi.

### 3.4.5 Hasil dan Bukti Kontrol Lintas Perangkat

Bagian ini membuktikan bahwa kontrol third-person desktop dan perangkat bergerak menggunakan jalur input yang sesuai. Tampilan desktop pada [FIGREF:desktop_control] menunjukkan build WebGL dengan navigasi aktif, minimap, dan tanpa joystick mobile. Tampilan mobile pada [FIGREF:mobile_control] menunjukkan joystick gerak, tombol sprint, tombol lompat, minimap, dan tata letak antarmuka perangkat bergerak.

[FIGURE:desktop_control]
[FIGCAPTION:Tampilan Kontrol Desktop pada Build WebGL]

[FIGURE:mobile_control]
[FIGCAPTION:Tampilan Kontrol Mobile pada Build WebGL]

Kedua tangkapan layar membuktikan perbedaan tampilan menurut mode perangkat, tetapi belum membuktikan respons input, *Pointer Lock*, atau perpindahan karakter. Verifikasi interaksi masih memerlukan file `.inputactions`, identitas perangkat dan peramban, serta rekaman 15–30 detik.

### 3.4.6 Hasil dan Bukti DatabaseSyncChecker

Bagian ini membuktikan bahwa tool editor membandingkan data `/api/unity/names` dengan hierarki scene dan menampilkan kategori hasil sesuai batas implementasi. Snapshot pemeriksaan pada [FIGREF:database_sync_checker_result] menampilkan 320 nama ditemukan, 3 nama dari API belum tersedia di scene, dan 14 root object scene belum terdaftar di database. Daftar contoh dan tombol penyalinan juga terlihat pada window hasil.

[FIGURE:database_sync_checker_result]
[FIGCAPTION:Hasil Pemeriksaan DatabaseSyncChecker]

Angka tersebut merupakan snapshot lama yang mendokumentasikan satu pemeriksaan terhadap *scene* dan endpoint aktif sebelum seed dirapikan menjadi 311 fasilitas. Angka itu tidak dinyatakan sebagai kondisi sinkronisasi seed final. UT-14 dan UT-15 berstatus Belum diverifikasi sampai respons acuan, versi kode sumber, kondisi API kosong atau gagal, serta pengujian ulang dicatat. Tangkapan layar lama `impl_sync_db_checker` diperlakukan sebagai ilustrasi antarmuka, sedangkan gambar baru menjadi bukti hasil pemeriksaan pada saat snapshot dibuat.

### 3.4.7 Hasil Spawn, Minimap, Highlighter, dan Tutorial

Implementasi final memuat pemilihan spawn yang tervalidasi terhadap NavMesh, minimap yang mengikuti pemain, penanda tujuan, *destination highlighter*, tutorial adaptif, serta pengiriman event selesai navigasi. Kode sumber, konfigurasi *scene*, dan tangkapan layar membuktikan keberadaan visual fitur. Pengujian dinamis khusus modul Unity berstatus Belum diverifikasi sampai interaksi diuji ulang pada *build* terintegrasi yang sama.

Tampilan pemilihan titik awal pada [FIGREF:spawn_selection_overview] memperlihatkan overview kampus dengan marker spawn dan nama lokasi. Setelah spawn dan navigasi aktif, minimap pada [FIGREF:minimap_destination] memperlihatkan marker pemain, marker tujuan, dan garis arah sehingga pengguna tetap memiliki orientasi ketika kamera utama berada pada sudut third-person.

[FIGURE:spawn_selection_overview]
[FIGCAPTION:Tampilan Pemilihan Titik Awal]

[FIGURE:minimap_destination]
[FIGCAPTION:Minimap dengan Marker Pemain dan Tujuan]

Visual tujuan pada [FIGREF:destination_highlight] menjadi bukti awal bahwa tujuan aktif dapat diberi penanda tambahan selain garis rute. Bukti ini perlu dilengkapi rekaman perubahan tujuan dan pembersihan highlight saat navigasi selesai.

[FIGURE:destination_highlight]
[FIGCAPTION:Highlight Visual pada Tujuan Navigasi]

Perbedaan tutorial adaptif terlihat pada [FIGREF:tutorial_desktop_lookaround] dan [FIGREF:tutorial_mobile_lookaround]. Kedua gambar menggunakan langkah 2 dari 5 dengan judul `Lihat Sekeliling`; mode desktop menampilkan instruksi menggerakkan mouse, sedangkan mode mobile menampilkan instruksi menggeser area kamera dan kontrol sentuh.

[FIGURE:tutorial_desktop_lookaround]
[FIGCAPTION:Tutorial Lihat Sekeliling pada Mode Desktop]

[FIGURE:tutorial_mobile_lookaround]
[FIGCAPTION:Tutorial Lihat Sekeliling pada Mode Mobile]

Tangkapan layar tersebut membuktikan penyesuaian visual berdasarkan mode perangkat, tetapi belum membuktikan handshake `SetDevice`, respons input, atau penyimpanan progres. Bukti dinamis masih memerlukan log mode perangkat, log spawn, dan rekaman interaksi pada build yang sama. Tampilan notifikasi kedatangan pada React tidak disertakan karena berada di luar kontribusi penulis.

### 3.4.8 Hasil dan Bukti Occlusion Culling serta Transisi Overview–Gameplay

Implementasi final menyertakan `OcclusionArea`, data bake, occlusion aktif pada `MainCamera`, dan occlusion nonaktif pada `MinimapCamera` sebagaimana dibuktikan pada Subbab 3.3.6. Saat overview aktif, kamera gameplay dirancang menonaktifkan occlusion sementara; setelah spawn berhasil, statusnya dipulihkan. `DayNightCycle` mengatur fog overview 0 dan fog gameplay 0,01.

Bukti yang tersedia menunjukkan konfigurasi statis editor, tetapi belum membuktikan perubahan status selama transisi atau dampaknya terhadap *renderer*, *draw call*, dan *frame time*. Hasil performa serta transisi *runtime* berstatus Belum diverifikasi sampai tersedia log `CampusOcclusion`, rekaman pemilih spawn, Unity Profiler, dan *benchmark* sebanding.

### 3.4.9 Batas Kontribusi Penulis

Batas kontribusi pada [TABREF:batas_kontribusi_faiz] digunakan agar implementasi bersama tidak diklaim sebagai pekerjaan individual penulis.

[TABLE-ID:batas_kontribusi_faiz]
[TABLECAPTION:Batas Kontribusi Penulis dalam Sistem Terintegrasi]
[TABLE]
Komponen | Pemilik Utama | Keterlibatan Penulis
Model dan aset tiga dimensi | 3D Asset Designer dan Database Schema Designer | Menggunakan aset yang tersedia di dalam *scene* serta menyampaikan kebutuhan *collision*, target navigasi, dan optimasi *runtime*
Skema database, RLS, trigger, dan pemetaan data | 3D Asset Designer dan Database Schema Designer | Menggunakan kontrak `unity_object_name` sebagai konsumen data
Dashboard React dan pencarian | Full Stack Web Developer, System Integrator, dan DevOps Engineer | Menetapkan format perintah tujuan yang diterima Unity
Vercel Serverless Functions | Full Stack Web Developer, System Integrator, dan DevOps Engineer | Menyediakan `/api/unity/data` dan `/api/unity/names` yang dikonsumsi komponen Unity
Jembatan React–Unity | Full Stack Web Developer, System Integrator, dan DevOps Engineer | Menyepakati kontrak metode dan event; *receiver* serta pengiriman event pada *runtime* Unity dikerjakan Faiz, sedangkan *bridge*, pemanggil, dan listener React dikerjakan Iman
Navigasi, rendering rute, dan kontrol Unity | 3D Simulator dan Engine Developer | Merancang, mengimplementasikan, dan menguji modul *engine*
Building Culling dan WebGL optimizer | 3D Simulator dan Engine Developer | Merancang, mengimplementasikan, dan mengevaluasi optimasi
DatabaseSyncChecker | 3D Simulator dan Engine Developer | Merancang, mengimplementasikan, dan menguji alat editor
Spawn, minimap, highlighter, dan tutorial Unity | 3D Simulator dan Engine Developer | Merancang, mengimplementasikan, dan menyiapkan pengujian fitur orientasi
[/TABLE]

## 3.5 Hasil Pengujian Proyek

### 3.5.1 Black Box Testing

<!-- PIPELINE:INCLUDE content/shared/testing/blackbox.md -->

### 3.5.2 Pengujian Khusus Modul Unity

Pengujian khusus memisahkan perilaku modul *engine* dari alur sistem melalui dashboard. Hasil Black Box pada [TABREF:hasil_black_box] menjadi bukti integrasi bersama, sedangkan [TABREF:hasil_pengujian_modul_unity] memuat 24 skenario khusus Unity. Status Belum diverifikasi digunakan apabila artefak yang tersedia belum cukup untuk menilai hasil; kolom bukti menyebutkan artefak yang masih diperlukan.

[TABLE-ID:hasil_pengujian_modul_unity]
[TABLECAPTION:Hasil Pengujian Khusus Modul Unity]
[TABLE]
ID | Kondisi Awal | Langkah Pengujian | Hasil yang Diharapkan | Hasil Aktual | Status | Bukti
UT-01 | Scene uji aktif dan endpoint mengembalikan koleksi gedung serta fasilitas valid | Jalankan Play Mode dan tunggu proses pemuatan `BuildingDatabase` selesai | `isLoaded` aktif, cache terisi, dan nama tampilan dapat diambil | Belum diverifikasi | Belum diverifikasi | Masih memerlukan fixture, log, dan tangkapan layar
UT-02 | Scene uji aktif dan sebuah nama tidak tersedia pada cache | Panggil `GetRealName()` menggunakan nama yang tidak dikenal | Method mengembalikan input asli dan tidak menghasilkan null | Belum diverifikasi | Belum diverifikasi | Masih memerlukan log atau hasil test runner
UT-03 | Cache Transform memuat target yang valid | Panggil `NavigateTo()` menggunakan `unity_object_name` target | `NavigationReceiver` meneruskan Transform yang tepat ke `NavigationGuide` | Belum diverifikasi | Belum diverifikasi | Masih memerlukan log dan rekaman Play Mode
UT-04 | Target memiliki variasi kapitalisasi atau tidak tersedia pada cache awal | Panggil `NavigateTo()` dan amati fallback pencarian | Variasi kapitalisasi dikenali; target yang benar-benar hilang menghasilkan warning tanpa exception | Belum diverifikasi | Belum diverifikasi | Masih memerlukan log dan fixture scene
UT-05 | Pemain dan target valid berada pada area NavMesh | Mulai navigasi dan amati status jalur serta `LineRenderer` | Jalur valid dihitung, garis aktif, nama tujuan tampil, dan jarak diperbarui | Belum diverifikasi | Belum diverifikasi | Masih memerlukan tangkapan layar dan rekaman
UT-06 | Navigasi aktif dan pemain berada di luar `stopDistance` | Gerakkan pemain hingga memasuki `stopDistance` | Navigasi berhenti serta garis dan label dibersihkan | Belum diverifikasi | Belum diverifikasi | Masih memerlukan rekaman dan log
UT-07 | Navigasi aktif menuju tujuan pertama | Panggil `StopNavigation()` atau pilih tujuan kedua | Rute lama dibersihkan dan state baru tidak menghasilkan garis ganda | Belum diverifikasi | Belum diverifikasi | Masih memerlukan rekaman Play Mode
UT-08 | Jalur uji memuat tikungan dan perubahan elevasi | Jalankan navigasi lalu bandingkan corners mentah dengan hasil renderer | Subdivisi linear memperapat titik, raycast menjaga garis mengikuti permukaan, dan moving average mengurangi perubahan titik yang tajam | Belum diverifikasi | Belum diverifikasi | Masih memerlukan tangkapan layar sebelum dan sesudah
UT-09 | Build dibuka pada browser desktop yang mendukung Pointer Lock | Klik canvas, gerakkan tetikus, lalu tekan ESC | Kursor terkunci setelah tindakan pengguna, kamera merespons delta, dan ESC melepaskan kursor | Tampilan desktop tanpa joystick dan navigasi aktif telah tersedia; respons Pointer Lock belum dibuktikan oleh tangkapan layar diam | Belum diverifikasi | `kontrol_desktop.png`; masih memerlukan identitas perangkat, browser, dan rekaman
UT-10 | Build yang sama dibuka pada perangkat mobile dan desktop | Gunakan joystick pada mobile lalu periksa tampilan desktop | Joystick mengendalikan pemain pada mobile dan tidak mengganggu tampilan desktop | UI desktop dan mobile tampil berbeda sesuai mode; respons gerak, sprint, dan lompat belum dibuktikan | Belum diverifikasi | `kontrol_desktop.png` dan `kontrol_mobile.png`; masih memerlukan identitas perangkat
UT-11 | Scene, kamera, dan lintasan benchmark telah ditetapkan | Jalankan skenario yang sama sebelum dan sesudah Building Culling | Pada konfigurasi 200 m, renderer di luar ambang/frustum ditangani sesuai grace period, target navigasi tetap aktif, area minimap dipertahankan, dan metrik sebelum–sesudah dapat dibandingkan | Dua capture NVIDIA Statistics Overlay pada sudut gameplay yang hampir sama telah tersedia, tetapi tidak memuat Unity Profiler, draw call, renderer aktif, durasi sampling, identitas perangkat, atau indikator state aktif/nonaktif yang dapat diverifikasi | Belum diverifikasi | `statistik_runtime_culling_aktif.png` dan `statistik_runtime_culling_nonaktif.png`; masih memerlukan Unity Profiler
UT-12 | Project menggunakan konfigurasi sebelum optimizer | Jalankan menu WebGL optimizer lalu periksa Player Settings | Brotli, decompression fallback, IL2CPP, stripping, WebAssembly 2023, dan exception support sesuai baseline proyek | Target Web aktif, SceneUtama terpilih, Brotli, fallback, caching, IL2CPP Master, optimasi ukuran, stripping High, WebAssembly 2023, dan `Explicitly Thrown Exceptions Only` terlihat | Lulus | Build Profile, Player Settings, dan log optimizer
UT-13 | Build produksi tersedia pada hosting yang ditetapkan | Muat build dan periksa Network serta Console browser | Build termuat tanpa error dan header kompresi serta MIME sesuai konfigurasi | Belum diverifikasi | Belum diverifikasi | Masih memerlukan DevTools, identitas perangkat, browser, dan kondisi jaringan
UT-14 | Fixture API dan scene memuat nama cocok, hilang, dan berlebih | Jalankan `DatabaseSyncChecker` lalu salin daftar ketidaksesuaian | Pencocokan dan nama yang hilang di scene memakai seluruh hierarki, kategori scene yang belum terdaftar memakai root object, dan daftar dapat disalin | Snapshot pemeriksaan lama menampilkan 320 cocok, 3 tidak ada di scene, 14 root tidak ada di database, contoh nama, dan tombol salin | Belum diverifikasi | `hasil_database_sync_checker.png`; masih memerlukan fixture yang sesuai seed final
UT-15 | Endpoint mengembalikan data kosong, tidak valid, atau gagal | Jalankan pemeriksaan untuk setiap kondisi kegagalan | Tool menampilkan pesan yang jelas, tidak menganggap data tersinkronisasi, dan tidak mengubah scene | Belum diverifikasi | Belum diverifikasi | Masih memerlukan log dan tangkapan layar kondisi gagal
UT-16 | Registry memuat titik spawn valid dan pemain berada pada scene utama | Panggil `SetSpawn()` menggunakan nama yang terdaftar | Pemain berpindah ke NavMesh di sekitar titik spawn sesuai radius dan override yang aktif | Belum diverifikasi | Belum diverifikasi | Masih memerlukan log, tangkapan layar posisi, dan rekaman
UT-17 | Registry aktif dan nama spawn tidak terdaftar atau tidak memiliki posisi NavMesh valid | Panggil `SetSpawn()` menggunakan nama tidak valid lalu menggunakan titik yang gagal diproyeksikan | Sistem menampilkan warning, tidak menghasilkan exception, dan tidak memindahkan pemain ke posisi yang tidak valid | Belum diverifikasi | Belum diverifikasi | Masih memerlukan log dan rekaman
UT-18 | Minimap, marker pemain, marker tujuan, dan navigasi aktif telah dikonfigurasi | Gerakkan pemain dan ubah tujuan navigasi | Minimap mengikuti pemain, marker pemain bergerak, dan marker tujuan mengarah ke tujuan aktif | Belum diverifikasi | Belum diverifikasi | Masih memerlukan tangkapan layar dan rekaman
UT-19 | Tujuan navigasi memiliki renderer yang dapat disorot | Mulai navigasi, ganti tujuan, lalu selesaikan atau hentikan navigasi | Highlighter aktif hanya pada tujuan saat ini dan dibersihkan ketika tujuan berubah atau navigasi berakhir | Belum diverifikasi | Belum diverifikasi | Masih memerlukan tangkapan layar dan rekaman
UT-20 | Tutorial pertama kali aktif dan build dapat menerima mode perangkat | Panggil `SetDevice()` untuk desktop dan mobile lalu jalankan langkah tutorial yang setara | Instruksi dan visual kontrol mengikuti mode perangkat tanpa menampilkan kontrol yang tidak relevan | Pada langkah 2 dari 5, mode desktop menampilkan instruksi mouse dan mode mobile menampilkan instruksi geser area kamera beserta kontrol sentuh | Lulus dengan catatan | Tangkapan layar tutorial desktop dan mobile; masih memerlukan log `SetDevice` dan rekaman
UT-21 | Build WebGL telah dimuat dan jembatan JavaScript dapat diamati | Panggil `WebPlatformSync.SetDevice()` dengan nilai valid serta nilai tak dikenal | Nilai valid menerapkan mode yang tepat; nilai tak dikenal ditangani tanpa pengecualian dan menghasilkan *fallback* atau peringatan yang tercatat | Belum diverifikasi | Belum diverifikasi | Masih memerlukan Console browser dan rekaman
UT-22 | Navigasi aktif dan listener browser `OnNavigationCompleted` terpasang | Masuki `stopDistance`, lalu ulangi skenario penghentian manual atau pergantian tujuan | Unity mengirim event dengan payload tujuan tepat satu kali hanya saat tiba, sedangkan pembatalan manual tidak mengirim event selesai; state navigasi tetap dibersihkan | Belum diverifikasi | Belum diverifikasi | Masih memerlukan log Unity, Console browser, dan rekaman pembatalan; tampilan notifikasi React di luar bukti kontribusi Faiz
UT-23 | Camera Frustum dan Occlusion Culling | Jalankan scene gameplay, putar kamera, buka selector spawn, lalu kembali ke gameplay | Renderer di luar jarak/frustum ditangani sesuai grace period, target navigasi tetap aktif, minimap tidak kehilangan area, dan status occlusion kamera berubah sesuai mode | Konfigurasi jarak/frustum, `OcclusionArea`, data bake, MainCamera aktif, dan MinimapCamera nonaktif telah terbukti; perubahan renderer saat runtime belum terbukti | Belum diverifikasi | Tangkapan layar konfigurasi Building Culling dan occlusion; masih memerlukan log runtime
UT-24 | Transisi Overview–Gameplay | Buka selector sebelum spawn, pilih spawn valid, lalu buka selector ulang | Fog overview bernilai 0, occlusion gameplay nonaktif saat selector, fog gameplay bernilai 0,01, dan occlusion gameplay pulih setelah spawn | Belum diverifikasi | Belum diverifikasi | Masih memerlukan log runtime, Inspector, dan rekaman
[/TABLE]

#### 3.5.2.1 Data dan Integrasi Runtime

Pengujian UT-01 dan UT-02 mencatat endpoint atau *fixture* tanpa membuka kredensial, kondisi awal *cache*, status `isLoaded`, jumlah entitas yang diproses, hasil `GetRealName()`, dan pesan ketika respons kosong atau tidak valid. Kode sumber, *fixture*, versi Unity, dan tangkapan layar log menjadi bukti minimum.

Pengujian UT-14 dan UT-15 memakai *fixture* terkendali agar kategori nama cocok, hilang dari *scene*, dan belum terdaftar dapat dibandingkan dengan data acuan. Pencarian dua kategori pertama mencakup seluruh hierarki, sedangkan objek *scene* yang belum terdaftar diperiksa pada *root object* sesuai batas implementasi. Kondisi respons kosong, format tidak valid, dan kegagalan jaringan diuji tanpa mengubah *scene*.

#### 3.5.2.2 Navigasi, Rute, dan Penyelesaian Navigasi

Pengujian UT-03 sampai UT-08 memakai posisi awal, tujuan, NavMesh, dan konfigurasi *renderer* yang sama. Pemeriksaan mencakup pencarian target, variasi kapitalisasi, target hilang, status jalur, jumlah titik, label, jarak, penghentian otomatis, penghentian manual, pergantian tujuan, tikungan, dan perubahan elevasi. Tangkapan layar serta rekaman Play Mode digunakan untuk membandingkan sudut jalur mentah dengan rute akhir.

Pengujian UT-19 dan UT-22 memeriksa highlighter serta penyelesaian navigasi. Kedatangan normal dan pembatalan diuji terpisah agar tujuan aktif, pembersihan visual, payload `unity_object_name`, jumlah pengiriman event, dan pembersihan status dapat diverifikasi. Listener serta notifikasi React hanya dipakai sebagai konteks integrasi dan tidak diklaim sebagai implementasi Faiz.

#### 3.5.2.3 Interaksi, Spawn, Minimap, dan Tutorial

Pengujian UT-09 dan UT-10 mencatat perangkat, sistem operasi, peramban, resolusi, dan metode input. *Pointer Lock* diuji setelah klik pengguna dan dilepas dengan ESC, sedangkan *joystick* diuji pada perangkat sentuh serta dibandingkan dengan tampilan desktop. Tangkapan layar diam hanya membuktikan tampilan sehingga respons input tetap memerlukan rekaman atau log aksi.

Pengujian UT-16 sampai UT-18 mencatat nama spawn, posisi sebelum dan sesudah perpindahan, radius pencarian NavMesh, *override* lokasi, dan perubahan penanda ketika pemain bergerak. UT-20 dan UT-21 memeriksa langkah tutorial yang setara pada desktop dan perangkat bergerak, perubahan mode melalui `SetDevice()`, *fallback* nilai tidak dikenal, serta visibilitas kontrol yang sesuai.

#### 3.5.2.4 Optimasi, Occlusion Culling, dan Build WebGL

Pengujian UT-11 menggunakan *build*, *scene*, posisi awal, jalur kamera, durasi, dan perangkat yang sama. Metrik minimumnya meliputi *renderer* aktif, *draw call*, *frame time*, *frame rate*, dan memori. Karena batas minimum dan maksimum pada *scene* final sama-sama 200 m, hasil hanya digunakan untuk menilai ambang tetap dan tidak untuk mengklaim jarak adaptif.

UT-12 dan UT-13 memeriksa Player Settings, ukuran berkas, waktu sampai aplikasi dapat digunakan, perangkat, peramban, jaringan, `Content-Encoding`, `Content-Type`, dan pesan Console. UT-23 dan UT-24 memeriksa *frustum*, *grace period*, pengecualian target, area minimap, status occlusion kamera, nilai fog, dan pemulihan kontrol ketika berpindah antara tampilan awal dan permainan. Kesimpulan performa hanya diberikan setelah tersedia hasil profiler serta kondisi pembanding yang setara.

### 3.5.3 User Acceptance Test

<!-- PIPELINE:INCLUDE content/shared/testing/uat.md -->

### 3.5.4 Implementasi Hasil User Acceptance Test

<!-- PIPELINE:INCLUDE content/shared/testing/uat-revisions.md -->

### 3.5.5 Analisis Kontribusi Faiz terhadap Tindak Lanjut UAT

Temuan UAT merupakan tindak lanjut produk bersama, sedangkan [TABREF:kontribusi_faiz_uat] hanya memetakan bagian yang berkaitan dengan *engine*. Status produk mengikuti matriks bersama pada Subbab 3.5.4. Kolom bukti pada tabel ini menunjukkan artefak khusus Unity yang masih diperlukan untuk reproduksi teknis dan tidak mengubah status implementasi produk.

[TABLE-ID:kontribusi_faiz_uat]
[TABLECAPTION:Pemetaan Kontribusi Engine terhadap Tindak Lanjut UAT]
[TABLE]
ID Temuan | Kaitan dengan Engine | Kandidat Kontribusi Penulis | Bukti Peran
UAT-R02 | Pengguna memerlukan petunjuk penggunaan yang mudah ditemukan | Menyediakan tutorial runtime yang menyesuaikan instruksi desktop atau mobile sebagai pelengkap bantuan pada dashboard | Tangkapan layar tutorial desktop dan mobile tersedia; build terintegrasi dan pengujian ulang khusus Unity belum diverifikasi
UAT-R04 | Pengguna perlu mengenali nama ruang atau fasilitas di lingkungan 3D | Menggunakan `realNames` untuk label tujuan, menjaga fallback nama tampilan, dan menyorot tujuan aktif | Tangkapan layar label dan highlighter, audit cakupan, serta pengujian ulang belum diverifikasi
UAT-R05 | Pengguna memerlukan onboarding yang mudah dipahami | Menyediakan urutan tutorial dan visual kontrol yang mengikuti mode perangkat dari `SetDevice()` | Langkah `Lihat Sekeliling` telah dibuktikan pada dua mode; skenario pengguna, log `SetDevice`, dan pengujian ulang belum diverifikasi
UAT-R06 | Pengguna perlu mengetahui posisi saat ini | Menyediakan minimap yang mengikuti pemain serta marker pemain dan tujuan aktif | Tangkapan layar runtime, rekaman pergerakan marker, dan pengujian ulang belum diverifikasi
UAT-R07 | Pengguna memerlukan pilihan mode dan titik awal | Mendukung pemilihan serta validasi spawn pada NavMesh dan kontrak `SpawnReceiver.SetSpawn()` | Tangkapan layar pemilihan spawn, log validasi, dan pengujian ulang belum diverifikasi
UAT-R10 | Pengguna memerlukan konfirmasi ketika mencapai tujuan | Mengirim event browser `OnNavigationCompleted` hanya setelah navigasi selesai secara normal; implementasi dan tangkapan layar notifikasi React tidak menjadi bukti kontribusi Faiz | Log pengiriman event Unity, build yang sama, dan pengujian ulang pembatalan manual belum diverifikasi
[/TABLE]

Temuan UAT-R03 dan UAT-R08 melibatkan komponen di luar *engine*, sedangkan UAT-R01 dan UAT-R09 terutama berkaitan dengan konsistensi basis data, API, pencarian, serta aset. Faiz tidak mengklaim implementasi bagian tersebut sebagai kontribusi personal. Status produk tetap mengikuti fragment bersama pada Subbab 3.5.4 berdasarkan audit kode sumber, pengujian, sumber resmi, dan bukti deployment. Status Belum diverifikasi pada tabel hanya menunjukkan artefak reproduksi khusus Unity yang masih perlu dilengkapi.

---

# BAB IV PENUTUP

## 4.1 Kesimpulan

Berdasarkan perancangan, implementasi, dan pengujian yang terdokumentasi, kesimpulan laporan ini adalah sebagai berikut:

1. Kontribusi penulis sebagai 3D Simulator dan Engine Developer menghasilkan susunan modul yang memisahkan konsumsi data, penerimaan perintah tujuan, pencarian Transform, perhitungan NavMesh, rendering rute, kontrol pengguna, optimasi *renderer*, konfigurasi *build*, pemeriksaan sinkronisasi, pemilihan spawn, minimap, penanda tujuan, dan tutorial adaptif.
2. Alur integrasi menggunakan `unity_object_name` sebagai penghubung teknis antara data gedung atau fasilitas dan GameObject di dalam scene. Unity mengonsumsi `GET /api/unity/data` untuk data runtime dan `GET /api/unity/names` untuk editor tool, menerima `NavigateTo()`, `StopNavigation()`, `SetSpawn()`, serta `SetDevice()`, kemudian mengekspos event browser `OnNavigationCompleted` hanya ketika path lengkap dan ambang kedatangan efektif maksimal 2 m terpenuhi, dengan payload tujuan. Pembatalan manual tidak mengirim event kedatangan; implementasi pemanggil dan listener React berada di luar kontribusi penulis.
3. Navigasi final menggunakan `NavMesh.SamplePosition`, validasi perpindahan lantai, `NavMesh.CalculatePath`, subdivisi linear dengan jarak titik 0,4 m, `RaycastNonAlloc`, rata-rata bergerak berjendela empat titik, dan `LineRenderer` berlebar 0,2 m dengan *offset* 0,6 m. Jalur diperbarui setelah perpindahan 1 m. Walaupun Inspector menyimpan `stopDistance` 5 m, ambang kedatangan *runtime* dibatasi maksimal 2 m serta mensyaratkan jalur lengkap dan kedekatan terhadap endpoint NavMesh. Hasil setiap skenario tetap mengikuti matriks pengujian dan bukti yang tersedia.
4. Kontrol karakter dan kamera sudut pandang orang ketiga menggunakan *Pointer Lock* pada desktop serta *joystick* virtual pada perangkat bergerak. Tutorial langkah `Lihat Sekeliling` telah menunjukkan instruksi tetikus pada desktop dan gestur area kamera pada perangkat bergerak. Respons input dan perubahan mode dinamis melalui `WebPlatformSync.SetDevice()` berstatus Belum diverifikasi karena log serta rekaman pada *build* terintegrasi belum tersedia.
5. Building Culling, camera-frustum culling, occlusion culling, dan WebGL optimizer telah menjadi bagian dari implementasi engine. Batas minimum dan maksimum culling jarak pada scene final sama-sama 200 m sehingga mode `Combined` bekerja dengan jarak efektif tetap, bukan adaptif. Capture NVIDIA Statistics Overlay telah tersedia sebagai bukti runtime pendahuluan, tetapi dampak kuantitatif belum boleh disimpulkan sebelum Unity Profiler, ukuran build, waktu muat, frame time, draw call, renderer aktif, durasi, dan identitas perangkat dilengkapi pada kondisi uji yang terkendali.
6. `DatabaseSyncChecker` menyediakan mekanisme pencegahan untuk menemukan ketidaksesuaian `unity_object_name` sebelum *build*. Pencarian padanan API menjangkau hierarki secara rekursif, tetapi kategori objek *scene* yang belum terdaftar hanya memeriksa *root object*. Snapshot pemeriksaan lama menampilkan 320 nama cocok, 3 nama yang tidak ditemukan di *scene*, dan 14 objek *root* yang belum terdaftar. Angka itu tidak dianggap sebagai kondisi seed final. Pengujian menggunakan data uji terkendali serta kondisi API kosong atau gagal berstatus Belum diverifikasi.
7. Spawn tervalidasi NavMesh, radius *override*, minimap, *destination highlighter*, serta tutorial desktop dan perangkat bergerak telah memiliki bukti visual. Pada tingkat produk, tindak lanjut UAT-R01 sampai UAT-R10 telah diterapkan berdasarkan bukti bersama. Namun, rekaman interaksi dan log khusus modul Unity untuk R02, R05, R06, R07, dan R10 masih berstatus Belum diverifikasi. Tampilan notifikasi React tidak digunakan sebagai bukti kontribusi Faiz.
8. Pada tingkat produk bersama, pengujian Black Box awal menghasilkan 23 dari 24 skenario lulus. Setelah BB-20 diperbaiki dan diuji ulang, hasil akhir menjadi 24 dari 24 skenario lulus. UAT tertutup bersama dua dosen penguji, dua dosen pembimbing, dan satu perwakilan Humas menghasilkan nilai gabungan 81,50 persen. Hasil tersebut tidak diperlakukan sebagai penilaian pengguna publik. Angka pengujian web dan API tetap menjadi bukti teknis milik Iman dan tidak dihitung sebagai hasil pengujian khusus Unity oleh Faiz.

## 4.2 Saran

Saran pengembangan lebih lanjut adalah sebagai berikut:

1. Melengkapi automated Play Mode Test dan Edit Mode Test untuk `BuildingDatabase`, `NavigationReceiver`, `NavigationGuide`, Building Culling, `DatabaseSyncChecker`, spawn, minimap, highlighter, tutorial, sinkronisasi perangkat, dan event selesai navigasi agar regresi dapat dideteksi sebelum build WebGL dibuat.
2. Menetapkan prosedur benchmark yang merekam perangkat, versi peramban, jenis koneksi, ukuran build, waktu muat, frame time, draw call, penggunaan memori, dan jumlah renderer aktif agar dampak optimasi dapat dibandingkan secara adil.
3. Melakukan pengujian ulang minimap dan marker tujuan untuk menilai keterbacaan, skala, orientasi, dan kegunaannya sebagai tindak lanjut UAT-R06 sebelum menentukan penyempurnaan visual berikutnya.
4. Menambahkan pengujian otomatis lintas Unity dan peramban untuk memastikan `OnNavigationCompleted` tetap hanya dikirim ketika pengguna mencapai tujuan dan tidak terkirim saat navigasi dibatalkan. Tampilan notifikasi pada React tetap menjadi tanggung jawab integrator web.
5. Menyempurnakan deteksi kapabilitas perangkat agar joystick virtual hanya muncul ketika relevan dan Pointer Lock memiliki fallback yang jelas pada peramban yang tidak mendukungnya secara penuh.
6. Menjaga sinkronisasi `unity_object_name` melalui pemeriksaan otomatis pada pipeline build serta memperluas pemeriksaan objek scene yang belum terdaftar dari root object ke hierarki yang relevan, sehingga build dapat ditahan ketika terdapat target database yang tidak memiliki padanan di scene.
7. Mengembangkan strategi pemuatan aset secara bertahap apabila hasil profiler menunjukkan bahwa ukuran atau inisialisasi aset menjadi hambatan utama sambil mempertahankan kontrak endpoint, method penerima Unity, dan event browser yang telah didokumentasikan.

---

# DAFTAR PUSTAKA


Aliyah, A., Hartono, N., dan Muin, A. A. (2025). Penggunaan User Acceptance Testing (UAT) pada pengujian sistem informasi pengelolaan keuangan dan inventaris barang. *Switch: Jurnal Sains dan Teknologi Informasi*, 3(2), 42–58. https://doi.org/10.62951/switch.v3i1.330

Jamaludin, J., dan Saepuloh, L. (2024). Tren riset twin digital smart campus. *Sang Pencerah: Jurnal Ilmiah Universitas Muhammadiyah Buton*, 10(2), 408–425. https://doi.org/10.35326/pencerah.v10i2.5317

Kurniawan, T. A. (2018). Pemodelan Use Case (UML): Evaluasi terhadap beberapa kesalahan dalam praktik. *Jurnal Teknologi Informasi dan Ilmu Komputer*, 5(1), 77–86. https://doi.org/10.25126/jtiik.201851610

Maulida, M., Zahro, F., Hakim, R., dan Akbar, M. S. (2025). Pengujian black box testing pada sistem website pemesanan online Toko Ayam Krispy. *Jurnal Media Akademik*, 3(5). https://doi.org/10.62281/v3i5.1908

MDN Web Docs, M. (2025). *Pointer Lock API*. https://developer.mozilla.org/en-US/docs/Web/API/Pointer_Lock_API

Muharam, Y., Anggara, M. B., dan Hanafi, T. J. (2023). Implementasi peta 3 dimensi menggunakan metode IMSDD (Interactive Multimedia System Design and Development) dan WebGL API berbasis web (Studi kasus di SMP Karya Pembangunan 2 Majalaya). *Jurnal Informatika-COMPUTING*, 10, 20–30. https://doi.org/10.55222/computing.v10i01.1155

Pricillia, T., dan Zulfachmi. (2021). Perbandingan metode pengembangan perangkat lunak (Waterfall, Prototype, RAD). *Jurnal Bangkit Indonesia*, 10(1), 6–12. https://doi.org/10.52771/bangkitindonesia.v10i1.153

Taurusta, C., Asiddiq, A. M., Suprianto, S., dan Setiawan, H. (2024). Visualisasi gedung kampus 1 Universitas Muhammadiyah Sidoarjo menggunakan augmented reality sebagai media informasi. *Journal of Technology and System Information*, 1(1), 55–70. https://doi.org/10.47134/jtsi.v1i1.2146

UPNVJ. (2022). Lokasi kampus. https://www.upnvj.ac.id/id/tentang-upn/lokasi-kampus.html

UPNVJ. (2025a). Kantin. https://www.upnvj.ac.id/id/fasilitas-layanan/kantin.html

UPNVJ. (2026). Rapat koordinasi Humas UPNVJ 2026: Fokus strategi komunikasi digital dan media sosial perguruan tinggi. https://www.upnvj.ac.id/id/berita/2026/02/rapat-koordinasi-humas-upnvj-2026-fokus-strategi-komunikasi-digital-dan-media-sosial-perguruan-tinggi.html

Unity Technologies. (2026a). *AI Navigation: Unity 6.0 Manual*. https://docs.unity3d.com/6000.0/Documentation/Manual/com.unity.ai.navigation.html

Unity Technologies. (2026b). *Deploy a web application: Unity 6.0 Manual*. https://docs.unity3d.com/6000.0/Documentation/Manual/webgl-deploying.html

Unity Technologies. (2026c). *Input System: Unity 6.0 Manual*. https://docs.unity3d.com/6000.0/Documentation/Manual/com.unity.inputsystem.html

---

# LAMPIRAN 1. Identitas dan Pernyataan Keaslian

Nama: Muammar Faiz Khairul Anam

NIM: 2210511138

Judul: Pengembangan Sistem Navigasi Spasial dan Optimasi Engine Unity WebGL pada Denah Virtual UPNVJ Kampus Pondok Labu

Naskah pernyataan keaslian dan halaman tanda tangan belum tersedia. Bukti yang masih diperlukan adalah halaman sesuai template resmi kampus yang telah ditandatangani.

---

# LAMPIRAN 2. Bukti Implementasi Modul Unity

Bukti implementasi pada bagian ini menggunakan kode sumber final, Unity 6000.4.1f1, dan `SceneUtama`. Apabila proyek Unity berubah, indeks bukti harus diperbarui agar kode sumber, *scene*, *build*, dan laporan tetap berasal dari versi yang sama. Rincian versi pengembangan disimpan pada catatan internal dan tidak ditampilkan dalam naskah laporan.

Panduan pengambilan bukti pada [TABREF:panduan_bukti_unity] menggunakan Game View 1920 × 1080. Nama file dipertahankan stabil agar dapat dimasukkan ke `images/manifest.json` setelah aset diterima. Setiap gambar kemudian digunakan tepat sekali melalui marker gambar, diberi caption gambar, dan dirujuk di tengah kalimat melalui referensi gambar ID-based. Marker tersebut belum ditambahkan untuk file yang belum tersedia.

[TABLE-ID:panduan_bukti_unity]
[TABLECAPTION:Panduan Pengambilan dan Penempatan Bukti Unity]
[TABLE]
ID dan Nama File | Yang Harus Terlihat | Penempatan
`unity_version_editor` — `versi_unity_editor.png` | Jendela About Unity yang menunjukkan versi editor 6000.4.1f1; target WebGL dibuktikan terpisah | 3.3.1
`unity_scene_hierarchy` — `scene_utama_hierarki_engine.png` | `SceneUtama` tersimpan, target Web aktif, dan Hierarchy komponen engine | 3.3.4
`navmesh_bake_config` — `konfigurasi_dan_bake_navmesh.png` | `NavMesh_Bake`, Inspector `NavMeshSurface`, area biru hasil bake, dan Console tanpa error | 3.3.2
`navigation_guide_config` — `konfigurasi_navigation_guide.png` | Inspector `NavigationGuide` dengan nilai final | 3.3.4
`path_line_config` — `konfigurasi_path_line.png` | Inspector `PathLine` dan konfigurasi `LineRenderer` | 3.3.4
`building_database_runtime_log` — `log_runtime_building_database.png` | Console Play Mode yang membuktikan fetch `/api/unity/data`, jumlah data, dan cache rebuild | 3.4.2
`active_navigation_route` — `rute_navigasi_aktif.png` | Karakter, garis putus-putus, nama tujuan, jarak, dan tujuan aktif | 3.4.2
`route_elevation` — `rute_perubahan_elevasi.png` | Rute pada tangga atau perubahan elevasi tanpa menembus permukaan | 3.4.3
`spawn_selection_overview` — `pemilihan_titik_awal.png` | Overview pemilihan spawn beserta marker dan nama lokasi | 3.4.7
`spawn_registry_config` — `konfigurasi_spawn_registry_umum.png` | Inspector `SpawnReceiver`, jumlah 16 titik, radius 5 m, ground offset 0,05 m, dan pemilihan awal aktif | 3.3.5
`spawn_registry_override` — `konfigurasi_spawn_registry_override.png` | Tiga elemen spawn dengan radius override 120 m, 40 m, dan 40 m | 3.3.5
`building_culling_config` — `konfigurasi_building_culling.png` | Batas jarak, mode Combined, interval, camera-frustum culling, padding, grace period, dan preservasi minimap | 3.3.4
`minimap_destination` — `minimap_pemain_dan_tujuan.png` | Minimap mengikuti pemain serta marker pemain dan tujuan | 3.4.7
`destination_highlight` — `highlight_tujuan_navigasi.png` | Gedung atau pintu tujuan yang sedang memperoleh efek highlight | 3.4.7
`desktop_control` — `kontrol_desktop.png` | Tampilan desktop tanpa joystick dan kondisi navigasi aktif | 3.4.5
`mobile_control` — `kontrol_mobile.png` | Perangkat mobile dengan joystick gerak atau pandang, sprint, dan lompat | 3.4.5
`tutorial_desktop_lookaround` — `tutorial_desktop_lihat_sekeliling.png` | Tutorial PC langkah 2 dari 5 dengan instruksi menggerakkan mouse | 3.4.7
`tutorial_mobile_lookaround` — `tutorial_mobile_lihat_sekeliling.jpg` | Tutorial mobile langkah 2 dari 5 dengan instruksi menggeser area kamera | 3.4.7
`runtime_stats_culling_enabled` — `statistik_runtime_culling_aktif.png` | NVIDIA Statistics Overlay dan Inspector pada capture yang diberi label culling aktif | 3.4.4
`runtime_stats_culling_disabled` — `statistik_runtime_culling_nonaktif.png` | NVIDIA Statistics Overlay dan Inspector pada capture yang diberi label culling nonaktif | 3.4.4
`webgl_build_profile` — `webgl_build_profile.png` | Target Web aktif, `SceneUtama`, Development Build nonaktif, dan optimasi Disk Size | 3.3.1
`webgl_player_settings_publishing` — `webgl_player_settings_publishing.png` | Brotli, Data Caching, Decompression Fallback, WebAssembly 2023, dan `Explicitly Thrown Exceptions Only` | 3.3.1
`webgl_player_settings_other` — `webgl_player_settings_other.png` | IL2CPP code generation, compiler Master, engine stripping, dan managed stripping High | 3.3.1
`webgl_optimizer_console` — `webgl_optimizer_console.png` | Log berhasil menerapkan WebGL release settings | 3.4.4
`webgl_network_data` — `jaringan_webgl_data.png` | DevTools Network untuk berkas `.data` | 3.4.4
`webgl_network_wasm` — `jaringan_webgl_wasm.png` | DevTools Network untuk berkas `.wasm` | 3.4.4
`webgl_wasm_mime_headers` — `header_mime_webgl_wasm.png` | Header MIME, encoding, ukuran, dan waktu | 3.4.4
`database_sync_checker_result` — `hasil_database_sync_checker.png` | Tiga kategori `DatabaseSyncChecker`, jumlah, serta nama contoh | 3.4.6
`occlusion_area_config` — `occlusion_area.png` | `Campus Gameplay Occlusion Area`, ukuran area, dan status View Volume | 3.3.6
`occlusion_data_asset` — `occlusion_data_asset.png` | `OcclusionCullingData.asset`, satu scene, dan jumlah static renderer | 3.3.6
`occlusion_main_camera` — `occlusion_main_camera.png` | Occlusion Culling aktif pada `MainCamera` | 3.3.6
`occlusion_minimap_camera` — `occlusion_minimap_camera.png` | Occlusion Culling nonaktif pada `MinimapCamera` | 3.3.6
[/TABLE]

Status bukti yang sudah diterima pada [TABREF:status_bukti_faiz] dipakai sebagai kontrol agar gambar yang sudah masuk tidak tertukar dengan bukti yang masih harus dilengkapi.

[TABLE-ID:status_bukti_faiz]
[TABLECAPTION:Status Bukti Unity yang Sudah Diterima]
[TABLE]
Kelompok Bukti | File yang Sudah Masuk | Status di Laporan | Catatan Lanjutan
Konfigurasi project dan scene | `unity_version_editor`, `unity_scene_hierarchy`, `navmesh_bake_config`, `navigation_guide_config`, `path_line_config`, `spawn_registry_config`, `spawn_registry_override`, `building_culling_config` | Sudah ditempatkan pada BAB III | Radius umum dan ketiga nilai override telah memiliki bukti Inspector
Konsumsi data dan navigasi | `building_database_runtime_log`, `active_navigation_route`, `route_elevation` | Sudah ditempatkan pada BAB III | Tambahkan rekaman Play Mode untuk pembuktian interaksi
Spawn, minimap, highlighter, kontrol, dan tutorial | `spawn_selection_overview`, `minimap_destination`, `destination_highlight`, `desktop_control`, `mobile_control`, `tutorial_desktop_lookaround`, `tutorial_mobile_lookaround` | Sudah ditempatkan pada BAB III | Lengkapi log mode perangkat, event selesai, dan rekaman interaksi
WebGL dan occlusion | `webgl_build_profile`, `webgl_player_settings_publishing`, `webgl_player_settings_other`, `webgl_optimizer_console`, `webgl_network_data`, `webgl_network_wasm`, `webgl_wasm_mime_headers`, `occlusion_area_config`, `occlusion_data_asset`, `occlusion_main_camera`, `occlusion_minimap_camera` | Sudah ditempatkan pada BAB III | Exception support telah diperbaiki; bukti konfigurasi tidak menjadi klaim performa
Sinkronisasi database–scene | `database_sync_checker_result` | Sudah ditempatkan pada BAB III | Lengkapi fixture gagal/kosong untuk UT-15
Bukti performa awal | `runtime_stats_culling_enabled`, `runtime_stats_culling_disabled` | Ditempatkan sebagai capture statistik runtime pendahuluan | Belum memenuhi benchmark Unity Profiler dan tidak digunakan untuk menyimpulkan peningkatan
Belum tersedia | Unity Profiler, log pengiriman `OnNavigationCompleted`, dan rekaman interaksi | Belum diverifikasi | Notifikasi React sengaja tidak dimasukkan karena bukan kontribusi Faiz
[/TABLE]

Aturan pengambilan bukti adalah sebagai berikut:

1. Gunakan project final, scene, build, dan data yang sama untuk bukti hasil. Satu gambar baseline bersifat opsional dan hanya ditempatkan pada lampiran sebagai penjelas perkembangan.
2. Sertakan rekaman 15–30 detik untuk Pointer Lock, joystick, perpindahan marker, Building Culling, dan event selesai karena tangkapan layar diam tidak membuktikan interaksi.
3. Catat perangkat, sistem operasi, browser, resolusi, versi kode sumber, scene, durasi, dan metode ukur pada bukti performa. Angka sebelum dan sesudah hanya dibandingkan apabila seluruh kondisi tersebut sama.
4. Sembunyikan token, cookie, kredensial, dan data sensitif lain sebelum mengambil DevTools Network atau Console.
5. Gunakan tangkapan layar top-down lama hanya sebagai sumber tambahan minimap, bukan pengganti tampilan minimap saat runtime.
6. Simpan Console log, Profiler capture, dan HAR atau Network log bersama tangkapan layar agar hasil aktual dapat ditelusuri.

Skrip kontribusi yang diarsipkan sebagai bukti adalah `BuildingDatabase.cs`, `NavigationReceiver.cs`, `NavigationGuide.cs`, `BuildingCulling.cs`, `WebGLOptimizer.cs`, `DatabaseSyncChecker.cs`, `CampusOcclusionInstaller.cs`, `SpawnPointRegistry.cs`, `SpawnSelectionUI.cs`, `SpawnMinimapSceneInstaller.cs`, `MinimapFollow.cs`, `DayNightCycle.cs`, `DestinationHighlighter.cs`, `NavigationDestinationVisual.cs`, `GameTutorialController.cs`, `GameTutorialUI.cs`, `WebPlatformSync.cs`, `TestNavigation.cs`, dan `ReactBridge.jslib`. Artefak konfigurasi yang menyertai bukti adalah `SceneUtama`, informasi versi Unity, konfigurasi NavMesh, data occlusion, konfigurasi build, output build final, Console log, Profiler capture, serta HAR atau Network log. Arsip skrip, artefak konfigurasi, rekaman interaksi, log pengiriman event, dan log final belum diverifikasi kelengkapannya.

---

# LAMPIRAN 3. Bukti Pengujian dan Benchmark

Bukti pengujian pada bagian ini perlu memuat konfigurasi perangkat, versi Unity, versi peramban, kondisi jaringan, fixture data, hasil Play Mode Test, hasil Edit Mode Test, Unity Profiler, DevTools Network, perbandingan build, dan bukti pengujian ulang. Artefak pengujian final tersebut belum diverifikasi kelengkapannya.

---

# LAMPIRAN 4. Instrumen UAT dan Indeks Bukti Pengujian

Instrumen pada lampiran ini merupakan bukti pengujian produk bersama. Pencantumannya tidak mengubah batas kontribusi penulis pada runtime dan tooling Unity.

<!-- PIPELINE:INCLUDE content/shared/testing/appendix-instruments.md -->
