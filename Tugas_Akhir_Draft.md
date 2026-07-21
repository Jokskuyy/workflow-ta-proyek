# PENGEMBANGAN SISTEM NAVIGASI SPASIAL DAN OPTIMASI ENGINE UNITY WEBGL PADA DENAH VIRTUAL UPNVJ KAMPUS PONDOK LABU

Muammar Faiz Khairul Anam

2210511138

INFORMATIKA

FAKULTAS ILMU KOMPUTER

UNIVERSITAS PEMBANGUNAN NASIONAL VETERAN JAKARTA

2025/2026

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

Sistem integrasi denah virtual UPNVJ menggabungkan dashboard publik berbasis React, layanan API berbasis Vercel Serverless Functions, database Supabase, dan modul Unity WebGL. Dashboard berfungsi sebagai titik interaksi pencarian, sedangkan Unity menampilkan lingkungan kampus dan menjalankan navigasi spasial. Komunikasi dari React menuju Unity berlangsung satu arah melalui `SendMessage`, sementara Unity mengambil data gedung dan fasilitas secara mandiri melalui `HTTP GET /api/unity/data`. Field `unity_object_name` menjadi penghubung antara data pada database dan GameObject sasaran di dalam scene Unity.

Keberadaan model tiga dimensi belum secara langsung menjamin pengalaman navigasi yang baik. Engine perlu menghitung jalur pada area yang dapat dilalui, menampilkan rute yang mengikuti kontur lantai dan tangga, menyajikan nama tujuan yang mudah dipahami, serta menghentikan navigasi ketika pengguna telah mencapai sasaran. Pada sisi interaksi, pengguna desktop membutuhkan kendali pandangan yang tidak terhambat batas layar, sedangkan pengguna perangkat bergerak membutuhkan kontrol sentuh yang sesuai. Pada sisi distribusi, build Unity harus dikonfigurasi agar dapat dijalankan melalui peramban dengan ukuran dan perilaku pemuatan yang dapat dievaluasi.

Berdasarkan kebutuhan tersebut, laporan ini berfokus pada kontribusi penulis sebagai **3D Simulator & Engine Developer**. Kontribusi tersebut mencakup pengembangan modul `BuildingDatabase`, `NavigationReceiver`, dan `NavigationGuide`; pembentukan rute melalui subdivisi linear, raycast vertikal, dan moving average; optimasi renderer melalui `BuildingCulling`; konfigurasi build melalui `WebGLOptimizer`; kontrol Pointer Lock dan joystick virtual; pemilihan titik awal, minimap, penanda tujuan, tutorial adaptif; serta alat editor `DatabaseSyncChecker`. Pembuatan aset tiga dimensi merupakan lingkup 3D Asset Designer, sedangkan pengembangan dashboard, API, dan jembatan integrasi web merupakan lingkup Full Stack Developer & System Integrator.

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
4. Sistem menggunakan karakter dan kamera third-person untuk satu pengguna dan tidak mencakup multiplayer, berbagi lokasi real-time, atau navigasi berbasis GPS.
5. React memanggil method Unity melalui `SendMessage`, sedangkan runtime Unity menyediakan event browser `OnNavigationCompleted`. Implementasi antarmuka dan listener React merupakan lingkup Full Stack Developer & System Integrator.
6. Unity mengambil data runtime melalui endpoint `/api/unity/data`, tetapi implementasi endpoint, autentikasi admin, serta dashboard web tidak dibahas sebagai kontribusi penulis.
7. Pembuatan model gedung, tekstur, dan tata letak aset tiga dimensi merupakan lingkup 3D Asset Designer; laporan ini membahas pemanfaatan aset tersebut oleh engine.
8. Optimasi yang dibahas meliputi Building Culling serta konfigurasi build WebGL berupa Brotli, decompression fallback, IL2CPP, dan managed stripping. Klaim peningkatan performa kuantitatif hanya dinyatakan apabila bukti pengukuran tersedia.
9. Evaluasi dedicated terhadap waktu komputasi rute, frame rate, ukuran build, dan waktu muat tetap ditandai `[TBD: ...]` apabila artefak pengujiannya belum tersedia pada repository laporan.

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

Usulan jadwal kegiatan untuk penyelesaian proyek ini dirinci dalam bentuk Gantt Chart yang menyajikan alokasi waktu pengerjaan secara bertahap, sebagaimana disajikan pada [TABREF:jadwal_kegiatan]. Keseluruhan proyek direncanakan selesai dalam kurun waktu enam bulan atau 24 minggu. Setiap bulan terdiri atas empat minggu; tanda `X` menunjukkan periode pelaksanaan utama, sedangkan tanda `–` menunjukkan tidak ada kegiatan utama pada periode tersebut. Waktu aktual tiap kegiatan perlu disesuaikan dengan logbook dan bukti pelaksanaan yang telah disahkan.

[TABLE-ID:jadwal_kegiatan]
[TABLECAPTION:Jadwal Kegiatan]
[TABLE gantt]
Aktivitas | Bulan 1 | Bulan 2 | Bulan 3 | Bulan 4 | Bulan 5 | Bulan 6
Minggu | 1  2  3  4 | 1  2  3  4 | 1  2  3  4 | 1  2  3  4 | 1  2  3  4 | 1  2  3  4
Analisis kebutuhan dan desain arsitektur engine | X  X  X  X | –  –  –  – | –  –  –  – | –  –  –  – | –  –  –  – | –  –  –  –
Pengembangan modul inti engine Unity | –  –  –  – | X  X  X  X | X  X  –  – | –  –  –  – | –  –  –  – | –  –  –  –
Pengembangan fitur orientasi, kontrol, dan optimasi | –  –  –  – | –  –  –  – | X  X  X  X | X  X  X  X | –  –  –  – | –  –  –  –
Integrasi Unity WebGL dan pengujian sistem | –  –  –  – | –  –  –  – | –  –  –  – | X  X  X  X | X  X  X  X | –  –  –  –
Revisi, retest, dan penulisan laporan | –  –  –  – | –  –  –  – | –  –  –  – | –  –  –  – | X  X  X  X | X  X  X  X
Dokumentasi | X  X  X  X | X  X  X  X | X  X  X  X | X  X  X  X | X  X  X  X | X  X  X  X
[/TABLE]

Alur pengerjaan dirancang secara sekuensial dan bertahap, dengan beberapa aktivitas yang berjalan tumpang tindih untuk menjaga kesinambungan integrasi. Tahapan-tahapan tersebut adalah:

1. **Analisis Kebutuhan dan Desain Arsitektur Engine (Bulan 1):** tahap fondasi yang berfokus pada posisi Unity dalam arsitektur sistem, kontrak `unity_object_name`, alur `SendMessage`, kebutuhan navigasi, rancangan scene, Use Case Diagram, serta rancangan NavMesh dan rendering rute. Perancangan dashboard, API, dan skema database tetap menjadi tanggung jawab anggota tim terkait.
2. **Pengembangan Modul Inti Engine Unity (Bulan 2 sampai pertengahan Bulan 3):** tahap implementasi `BuildingDatabase`, `NavigationReceiver`, `NavigationGuide`, perhitungan jalur NavMesh, serta rendering rute berbasis subdivisi linear, raycast, dan moving average. Endpoint dan data diperlakukan sebagai kontrak integrasi, bukan implementasi backend oleh penulis.
3. **Pengembangan Fitur Orientasi, Kontrol, dan Optimasi (Bulan 3–4):** tahap implementasi kontrol desktop dan mobile, pemilihan spawn, minimap, penanda tujuan, tutorial adaptif, Building Culling, Occlusion Culling, WebGL optimizer, serta `DatabaseSyncChecker`.
4. **Integrasi Unity WebGL dan Pengujian Sistem (Bulan 4–5):** tahap penyatuan build Unity dengan dashboard melalui method `NavigateTo`, `StopNavigation`, `SetSpawn`, dan `SetDevice`, dilanjutkan pengujian konsumsi data, navigasi, kontrol lintas perangkat, sinkronisasi nama, build WebGL, Black Box, dan modul khusus engine. Implementasi React dan listener browser tetap dikelola anggota integrasi.
5. **Revisi, Retest, dan Penulisan Laporan (Bulan 5–6):** alokasi waktu untuk perbaikan bug berdasarkan hasil pengujian, retest pada build yang sama, pemutakhiran screenshot atau log, pengukuran performa dengan kondisi sebanding, dan penyusunan laporan final.
6. **Dokumentasi (Bulan 1–6):** aktivitas paralel sepanjang proyek untuk memastikan rancangan, konfigurasi, script, commit, hasil pengujian, dan bukti visual terdokumentasi secara konsisten.

## 1.6 Sistematika Penulisan

Laporan ini disusun dalam empat bab dengan sistematika sebagai berikut:

1. BAB I PENDAHULUAN menjelaskan konteks proyek, fokus masalah simulator, batasan kontribusi, tujuan, manfaat, jadwal kegiatan, dan susunan laporan.
2. BAB II RANCANGAN PROYEK menguraikan hasil observasi, kebutuhan simulator, arsitektur sistem, rancangan alur data, rancangan navigasi dan rendering rute, rancangan optimasi, rancangan kontrol, serta rencana pengujian.
3. BAB III IMPLEMENTASI PROYEK membahas profil mitra, implementasi modul Unity, konfigurasi scene dan build WebGL, bukti kontribusi, hasil pengujian bersama, hasil pengujian khusus simulator, serta analisis tindak lanjut UAT yang berkaitan dengan engine.
4. BAB IV PENUTUP menyajikan kesimpulan berdasarkan hasil yang telah memiliki bukti dan saran pengembangan lebih lanjut.

---

# BAB II RANCANGAN PROYEK

## 2.1 Observasi

Observasi proyek dilakukan untuk memahami kondisi navigasi kampus, kebutuhan pengguna, batas kebijakan data, dan pembagian tanggung jawab teknis di dalam tim. Bagian ini menggunakan temuan bersama sebagai konteks, kemudian mengarahkannya pada kebutuhan simulator dan engine yang menjadi lingkup penulis.

### 2.1.1 Observasi Lapangan

Observasi lapangan berfokus pada hubungan spasial antargedung, jalur pejalan kaki, pintu masuk, koridor, lantai, tangga, dan hambatan yang perlu direpresentasikan di dalam scene. Informasi tersebut menjadi dasar untuk menentukan area yang dapat dilalui oleh agen NavMesh serta lokasi target navigasi. Karena repository laporan belum memuat catatan pengukuran spasial terperinci, ukuran agen, kemiringan, tinggi langkah, dan konfigurasi bake perlu dicocokkan kembali dengan scene Unity aktual sebelum dinyatakan sebagai nilai final. [TBD: lampirkan catatan observasi dan konfigurasi NavMesh hasil verifikasi]

Observasi juga mempertimbangkan perangkat yang digunakan oleh pengguna. Simulator ditargetkan berjalan di peramban, dengan perangkat bergerak sebagai kebutuhan penting proyek. Oleh karena itu, rancangan engine tidak dapat hanya mengandalkan input tetikus dan papan ketik, tetapi perlu menyediakan kontrol sentuh serta tata letak antarmuka yang tidak menutupi area navigasi utama.

### 2.1.2 Analisis Kebutuhan Pengguna

Kuesioner awal digunakan oleh tim untuk mengenali profil responden, pengalaman menggunakan media navigasi, frekuensi kesulitan mencari lokasi, perilaku ketika tersesat, urgensi denah virtual, potensi penggunaan, dan prioritas informasi. Profil responden disajikan pada [FIGREF:survey_01_profil], sedangkan persepsi efektivitas informasi navigasi ditampilkan pada [FIGREF:survey_02_efektivitas].

[FIGURE:survey_01_profil]
[FIGCAPTION:Hasil Kuesioner: Profil Status Akademik]

[FIGURE:survey_02_efektivitas]
[FIGCAPTION:Hasil Kuesioner: Efektivitas Informasi]

Frekuensi pengalaman pengguna saat mengakses atau membutuhkan denah dirangkum pada [FIGREF:survey_03_frekuensi], sementara perilaku pencarian lokasi ketika informasi belum mencukupi diperlihatkan pada [FIGREF:survey_04_perilaku]. Pembacaan angka rinci pada kedua gambar perlu mengikuti data kuesioner sumber dan tidak disalin dari laporan anggota lain tanpa pemeriksaan ulang.

[FIGURE:survey_03_frekuensi]
[FIGCAPTION:Hasil Kuesioner: Frekuensi Akses Denah]

[FIGURE:survey_04_perilaku]
[FIGCAPTION:Hasil Kuesioner: Perilaku Pencarian Lokasi]

Kebutuhan terhadap denah virtual ditunjukkan pada [FIGREF:survey_05_urgensi], potensi adopsinya disajikan pada [FIGREF:survey_06_adopsi], dan prioritas informasi fasilitas dirangkum pada [FIGREF:survey_07_prioritas]. Bagi peran penulis, rangkaian temuan tersebut diterjemahkan menjadi kebutuhan navigasi terpandu, label tujuan yang mudah dibaca, kontrol yang dapat dipahami, serta performa pemuatan yang perlu diukur pada build WebGL.

[FIGURE:survey_05_urgensi]
[FIGCAPTION:Hasil Kuesioner: Urgensi Kebutuhan Denah]

[FIGURE:survey_06_adopsi]
[FIGCAPTION:Hasil Kuesioner: Tingkat Adopsi Potensial]

[FIGURE:survey_07_prioritas]
[FIGCAPTION:Hasil Kuesioner: Prioritas Fitur]

### 2.1.3 Analisis Sistem yang Sedang Berjalan

Media navigasi yang tersedia sebelum pengembangan proyek terutama berupa papan penunjuk arah dan denah statis. Media tersebut tetap berguna sebagai informasi dasar, tetapi tidak menghitung rute dari posisi pengguna, tidak menyesuaikan tampilan berdasarkan tujuan, dan tidak menghubungkan informasi fasilitas dengan representasi ruang tiga dimensi. Studi mengenai peta tiga dimensi berbasis WebGL menunjukkan bahwa penyajian lingkungan secara interaktif dapat menjadi pendekatan untuk memperluas fungsi media informasi konvensional (Muharam et al. 2023).

Pada sisi digital, data profil dan fasilitas berada pada komponen yang berbeda dari scene Unity. Tanpa kontrak identitas yang sama, perubahan nama pada database dapat menyebabkan target navigasi tidak ditemukan di dalam scene. Permasalahan ini mendasari penggunaan `unity_object_name` sebagai identitas teknis dan kebutuhan terhadap pemeriksaan sinkronisasi sebelum build dipublikasikan.

### 2.1.4 Wawancara dengan Stakeholder

Wawancara dengan Kepala UPA TIK UPNVJ membahas pembagian peran tim dan kebutuhan fungsional maupun non-fungsional sistem. Wawancara dengan Wakil Rektor Bidang Kemahasiswaan, Kerja Sama, dan Sistem Informasi membahas ketersediaan serta kebijakan pembagian data sarana prasarana. Dokumentasi kegiatan tersebut diperlihatkan pada [FIGREF:foto_wawancara_warek] sebagai bukti konteks koordinasi institusional proyek.

[FIGURE:foto_wawancara_warek]
[FIGCAPTION:Dokumentasi Wawancara dan Penandatanganan Pakta Integritas]

Pembagian peran yang digunakan dalam laporan ini adalah sebagai berikut:

1. Muammar Faiz Khairul Anam berperan sebagai 3D Simulator & Engine Developer dengan tanggung jawab pada logika runtime Unity, navigasi, rendering rute, optimasi WebGL, kontrol pengguna, konsumsi data engine, dan editor tool.
2. Muhammad Dwikhi Deandra Purnianto berperan sebagai 3D Asset Designer & Database/Asset Manager dengan tanggung jawab pada pembuatan aset, penataan scene, skema database, RLS, audit log, dan integritas pemetaan data.
3. Muhammad Iman Nugraha berperan sebagai Full Stack Developer & System Integrator dengan tanggung jawab pada dashboard React, Vercel Serverless Functions, integrasi Supabase Auth, proxy Umami, jembatan React–Unity, dan pengujian web.

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

NavMesh merupakan representasi area yang dapat dilalui dan digunakan oleh komponen navigasi untuk mendukung pencarian jalur pada scene. Paket AI Navigation Unity menyediakan komponen untuk membangun dan menggunakan NavMesh pada waktu edit maupun runtime (Unity Technologies 2026). Proyek menggunakan Unity 6 dengan Universal Render Pipeline, AI Navigation, New Input System, TextMeshPro, dan target build WebGL.

Titik sudut hasil `NavMeshPath` digunakan sebagai dasar pembentukan garis navigasi. Implementasi final membagi setiap segmen secara linear berdasarkan jarak sampling, memproyeksikan setiap titik ke permukaan melalui raycast vertikal, lalu menerapkan moving average agar perubahan posisi antartitik tidak bergerigi. Pendekatan ini mengikuti kode aktif pada scene final dan menggantikan rancangan interpolasi kurva yang tidak lagi dipanggil oleh alur runtime.

Pointer Lock API menyediakan perubahan posisi relatif tetikus, mempertahankan input meskipun pergerakan melewati batas layar, dan menyembunyikan kursor selama penguncian. Karakteristik tersebut digunakan untuk mengendalikan pandangan kamera third-person di peramban (MDN Web Docs 2025). Untuk perangkat sentuh, New Input System menyediakan konsep on-screen control yang dapat memetakan widget antarmuka ke kontrol perangkat virtual (Unity Technologies 2026).

Distribusi WebGL menggunakan build Unity yang dikompresi. Dokumentasi Unity menjelaskan bahwa Brotli menghasilkan berkas yang lebih kecil daripada gzip dengan konsekuensi waktu kompresi build yang lebih panjang, dan server perlu mengirim header yang sesuai agar peramban memproses berkas terkompresi dengan benar (Unity Technologies 2026). Konfigurasi teknis proyek mencakup Brotli, decompression fallback, IL2CPP, dan managed stripping, dengan validasi runtime diperlukan untuk memastikan kode yang digunakan tidak ikut terhapus oleh proses stripping.

### 2.2.3 Identifikasi Kebutuhan Non-Fungsional

Kebutuhan non-fungsional modul simulator dirumuskan sebagai berikut:

1. Performa: halaman yang memuat model tiga dimensi ditargetkan dapat digunakan dalam waktu kurang dari 10 detik sesuai requirement proyek; pencapaian target harus dibuktikan melalui pengukuran pada perangkat, jaringan, dan build yang terdokumentasi.
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
[FIGCAPTION:Tahap Pengembangan]

Iterasi pengembangan modul Unity dirancang melalui tahapan berikut:

1. Menentukan kebutuhan navigasi dan kontrak data bersama pengembang dashboard, API, database, dan aset tiga dimensi.
2. Menetapkan hierarki scene, target `Pointer`, area NavMesh, serta komponen runtime yang diperlukan.
3. Membuat prototipe penerimaan tujuan dan perhitungan jalur dasar menggunakan NavMesh.
4. Menambahkan penghalusan rute, raycast kontur, label tujuan, jarak, dan penghentian otomatis.
5. Menambahkan kontrol desktop dan perangkat bergerak.
6. Menambahkan Building Culling, WebGL optimizer, dan Database Sync Checker.
7. Mengintegrasikan build Unity pada alur sistem melalui kontrak `NavigateTo`, `StopNavigation`, `SetSpawn`, `SetDevice`, dan event `OnNavigationCompleted`; implementasi dashboard React dan endpoint serverless tetap dikerjakan anggota integrasi.
8. Menjalankan pengujian fungsional, pengujian modul, pengukuran performa, perbaikan, dan retest.

### 2.3.2 Perancangan Arsitektur Sistem

Arsitektur sistem menjelaskan pembagian tanggung jawab antara dashboard, engine, API, database, dan layanan analitik. Hubungan antarkomponen diperlihatkan pada [FIGREF:diagram_arsitektur], dengan Unity WebGL ditempatkan sebagai modul visualisasi yang berjalan di dalam peramban.

[FIGURE:diagram_arsitektur]
[FIGCAPTION:Diagram Arsitektur Sistem]

Alur utama yang berkaitan dengan peran penulis dirancang sebagai berikut:

1. React menampilkan daftar hasil pencarian gedung dan fasilitas kepada pengguna.
2. Ketika pengguna memilih tujuan, React memanggil `SendMessage("NavigationReceiver", "NavigateTo", unity_object_name)`.
3. `NavigationReceiver` mencari Transform sasaran yang sesuai di dalam scene.
4. `NavigationGuide` menghitung jalur pada NavMesh dan menampilkan garis rute, nama tujuan, serta jarak tersisa.
5. Secara terpisah, `BuildingDatabase` menarik data dari `/api/unity/data` untuk membentuk cache `unityObjectNames` dan `realNames`.
6. Ketika pengguna mencapai `stopDistance` atau memilih berhenti, garis dan label navigasi dibersihkan.

Pemetaan komponen arsitektur pada [TABREF:pemetaan_arsitektur_engine] digunakan untuk membedakan bagian yang menjadi kontribusi penulis dan bagian yang hanya menjadi kontrak integrasi bersama.

[TABLE-ID:pemetaan_arsitektur_engine]
[TABLECAPTION:Pemetaan Komponen Arsitektur terhadap Peran Engine]
[TABLE]
Komponen | Fungsi pada Sistem | Hubungan dengan Modul Faiz | Batas Klaim
Dashboard React | Menampilkan pencarian, pemilihan tujuan, dan canvas Unity | Mengirim `NavigateTo`, `StopNavigation`, `SetSpawn`, serta `SetDevice` | Implementasi antarmuka dan listener bukan kontribusi penulis
Vercel Serverless Functions | Menyediakan endpoint data Unity dan endpoint daftar nama | Dikonsumsi oleh `BuildingDatabase` dan `DatabaseSyncChecker` | Pembuatan endpoint bukan kontribusi penulis
Supabase Database | Menyimpan data gedung, fasilitas, dan kunci `unity_object_name` | Menjadi sumber identitas teknis target scene | Skema, RLS, dan audit log bukan kontribusi penulis
Unity WebGL | Menjalankan scene, kontrol, navigasi, rendering rute, dan tool editor | Menjadi ruang kontribusi utama penulis | Klaim dibatasi pada script, konfigurasi, dan bukti Unity
Browser dan Hosting | Menjalankan build WebGL serta menyajikan `.data` dan `.wasm` | Menjadi tempat validasi build, MIME, encoding, dan event browser | Infrastruktur hosting dijelaskan sebagai konteks integrasi
[/TABLE]

### 2.3.3 Perancangan Aktor dan Batas Interaksi

Use case merupakan model yang menjelaskan interaksi aktor dengan fungsi sistem dari sudut pandang kebutuhan pengguna (Kurniawan 2018). Legenda simbol yang digunakan ditampilkan pada [FIGREF:diagram_use_case_legenda], sedangkan hubungan pengguna publik, administrator, developer, dashboard, dan denah virtual disajikan pada [FIGREF:diagram_use_case].

[FIGURE:diagram_use_case_legenda]
[FIGCAPTION:Legenda Use Case Diagram]

[FIGURE:diagram_use_case]
[FIGCAPTION:Use Case Diagram]

Pada lingkup engine, pengguna publik berinteraksi dengan kontrol eksplorasi, pemilihan tujuan yang diteruskan oleh dashboard, garis rute, label tujuan, dan penghentian navigasi. Developer menggunakan WebGL optimizer dan Database Sync Checker. Administrator tidak berinteraksi langsung dengan kode engine; perubahan data dilakukan melalui dashboard dan diteruskan melalui database serta API yang dikelola anggota tim lain.

### 2.3.4 Perancangan Alur Data dan Sinkronisasi

Proses pengambilan dan penggunaan data oleh Unity diperlihatkan pada [FIGREF:diagram_activity_integrasi]. Alur tersebut menegaskan batas bahwa engine merupakan konsumen data dan tidak melakukan operasi CRUD terhadap database.

[FIGURE:diagram_activity_integrasi]
[FIGCAPTION:Activity Diagram: Integrasi Data Denah]

Urutan sinkronisasi data hingga pencocokan GameObject ditunjukkan pada [FIGREF:diagram_sequence_sinkronisasi]. Peran penulis dimulai ketika Unity meminta data, membentuk cache, mencocokkan nama, dan menyiapkan objek untuk navigasi.

[FIGURE:diagram_sequence_sinkronisasi]
[FIGCAPTION:Sequence Diagram: Sinkronisasi Data Gedung dan Unity]

Rangkuman penggunaan diagram rancangan pada [TABREF:pemetaan_diagram_rancangan] menjaga agar diagram UML dan arsitektur dibaca sesuai batas kontribusi penulis. Diagram perancangan skema database tidak digunakan dalam laporan ini karena berada pada lingkup Database Developer; penulis hanya mendokumentasikan kontrak data yang dikonsumsi Unity.

[TABLE-ID:pemetaan_diagram_rancangan]
[TABLECAPTION:Pemetaan Diagram Rancangan terhadap Kebutuhan Laporan Faiz]
[TABLE]
Artefak Rancangan | Informasi yang Dipakai | Relevansi untuk Role Faiz | Catatan Batas Kontribusi
Diagram arsitektur | Alur dashboard, API, database, Unity, dan browser | Menentukan posisi Unity sebagai runtime visualisasi | Komponen web dan API hanya konteks integrasi
Use Case Diagram | Aktor pengguna, administrator, dan developer | Menentukan interaksi eksplorasi, navigasi, dan tool developer | Fitur admin tidak diklaim sebagai implementasi Faiz
Activity Diagram Integrasi | Urutan data dari dashboard hingga Unity | Menjadi dasar lifecycle `BuildingDatabase` dan pencarian target | Operasi CRUD tetap berada di luar engine
Sequence Diagram Sinkronisasi | Urutan API, cache, dan pencocokan GameObject | Menjadi dasar rancangan `NavigationReceiver` dan `DatabaseSyncChecker` | Listener React hanya disebut sebagai kontrak
[/TABLE]

### 2.3.5 Perancangan Konsumsi Data dan Lifecycle Engine

`BuildingDatabase` dirancang sebagai sumber data runtime bagi modul engine. Ketika scene dimulai, komponen memasuki kondisi pemuatan, mengirim `HTTP GET` ke `/api/unity/data`, memeriksa keberhasilan respons, lalu memproses koleksi `gedung` dan `fasilitas`. Pada Editor, method `Awake()` menetapkan endpoint produksi `https://dashboard-profile-upnvj.vercel.app/api/unity/data`; pada build WebGL, URL diganti menjadi `/api/unity/data` agar mengikuti origin hosting. Nilai lama `/api/unity/names` yang masih tersimpan pada Inspector scene bukan endpoint runtime `BuildingDatabase` dan tidak digunakan sebagai bukti hasil akhir. Engine tidak membuat atau mengubah data pada database karena operasi tersebut berada di luar lingkup penulis.

Struktur minimum setiap entitas yang digunakan engine terdiri atas nama tampilan dan `unity_object_name`. Data gedung serta fasilitas diproses melalui alur yang sama agar target dari kedua koleksi dapat dicari tanpa membedakan sumbernya pada tahap navigasi. Cache `unityObjectNames` menyimpan identitas teknis yang tersedia, sedangkan dictionary `realNames` memetakan identitas tersebut ke nama yang ditampilkan pada label tujuan. Kunci cache dinormalisasi secara case-insensitive, tetapi bentuk sumber tetap mengikuti konvensi huruf kecil dan underscore.

Lifecycle data engine dirancang melalui kondisi berikut:

1. **Belum dimuat:** scene baru aktif dan belum menerima respons API; modul lain tidak boleh mengasumsikan cache telah tersedia.
2. **Sedang dimuat:** permintaan API sedang berlangsung dan status pemuatan dipertahankan sampai respons selesai diproses.
3. **Berhasil:** respons valid menghasilkan cache `unityObjectNames`, dictionary `realNames`, dan status `isLoaded` yang dapat dibaca modul lain.
4. **Respons dengan koleksi kosong:** JSON valid dengan `gedung` dan `fasilitas` kosong tetap menyelesaikan parsing, mengaktifkan `isLoaded`, dan menghasilkan cache kosong; perilaku aktual ini perlu dibedakan dari respons null atau JSON tidak valid.
5. **Permintaan atau parsing gagal:** pesan kesalahan dicatat untuk penelusuran tanpa menghentikan aplikasi secara tidak terkendali.
6. **Nama tidak ditemukan:** `GetRealName()` mengembalikan input asli sebagai fallback agar label tidak kosong.

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

Rancangan ketahanan jalur mempertahankan path lengkap terakhir ketika rekalkulasi gagal sesaat di batas polygon, tangga, atau NavMesh link. Path parsial atau invalid tidak menggantikan rute aktif dan tidak dianggap sebagai kedatangan. Sistem menjadwalkan percobaan ulang dengan interval 1 detik sampai path lengkap tersedia atau navigasi dibatalkan.

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

Titik `corners` dari hasil NavMesh dapat memiliki jarak antartitik yang besar dan perubahan arah yang tajam. Implementasi final tidak memanggil helper Catmull–Rom yang masih tersisa pada script. Setiap segmen aktif dibagi secara linear dengan `pointSpacing` 0,4 m, kemudian raycast diarahkan ke bawah agar posisi vertikal garis mengikuti permukaan lantai atau tangga. Moving average dengan `smoothingWindow` 4 diterapkan pada koordinat akhir, sedangkan titik awal dan akhir dipertahankan.

Alur rendering dirancang sebagai berikut:

1. Mengambil titik sudut dari `NavMeshPath` yang valid.
2. Membagi setiap segmen secara linear dengan jarak sampling 0,4 m.
3. Melakukan `Physics.RaycastNonAlloc()` dari 1,5 m di atas titik sampling sejauh 3 m ke bawah menggunakan `groundMask` dan mengabaikan trigger.
4. Mengabaikan collider pemain dan target dari kandidat hasil raycast, lalu menerima permukaan terdekat apabila selisih vertikalnya tidak melebihi toleransi 0,75 m.
5. Menambahkan `lineHeightOffset` 0,6 m agar garis tidak berimpit dengan permukaan.
6. Menghaluskan kumpulan titik dengan moving average berjendela 4 tanpa menggeser titik awal dan akhir.
7. Mengirim kumpulan titik akhir ke `LineRenderer` dengan lebar 0,2 m dan material putus-putus yang dibentuk saat runtime.
8. Memperbarui label nama tujuan dan jarak jalur tersisa.

Transformasi titik mentah menjadi garis yang dirender dirangkum pada [TABREF:alur_rendering_rute_rancangan]. Bukti visual hasil akhirnya diberikan melalui screenshot rute aktif dan perubahan elevasi pada BAB III; perbandingan titik internal sebelum dan sesudah pemrosesan tidak diklaim apabila log debug belum tersedia.

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

Kontrol perangkat bergerak menggunakan prefab `UI_Virtual_Joystick` yang memetakan gerakan sentuh ke New Input System. `WebPlatformSync.SetDevice(string)` menerima nilai `mobile` atau `desktop`, mengubah visibilitas joystick, dan meneruskan mode perangkat kepada antarmuka spawn serta tutorial. Screenshot desktop, mobile, dan tutorial adaptif telah tersedia; respons Pointer Lock, joystick, serta perubahan mode tetap memerlukan rekaman pada build final.

### 2.3.10 Perancangan DatabaseSyncChecker

`DatabaseSyncChecker` dirancang sebagai alat editor yang memeriksa konsistensi `unity_object_name` sebelum build WebGL dibuat. Tool menerima daftar identitas dari `/api/unity/names`, memindai hierarki scene secara rekursif termasuk child `Pointer`, menormalisasi perbandingan secara case-insensitive, lalu membandingkan himpunan nama dari API dengan himpunan nama pada scene. Pada implementasi aktif, kategori nama API yang cocok atau hilang menggunakan seluruh hierarki, sedangkan kategori objek scene yang belum terdaftar di database hanya memeriksa root object scene.

Hasil pemeriksaan dirancang dalam tiga kategori:

1. **Synchronized:** nama tersedia pada API dan memiliki GameObject padanan di dalam scene.
2. **Missing in Scene:** nama tersedia pada API, tetapi tidak ditemukan pada hierarki scene.
3. **Not Registered in Database:** root GameObject tersedia pada scene, tetapi namanya tidak terdapat pada data API.

Tool perlu menyediakan ringkasan jumlah setiap kategori, daftar nama yang dapat ditelusuri, dan tindakan untuk menyalin daftar ketidaksesuaian. Respons API kosong dibedakan dari kondisi seluruh data tersinkronisasi agar hasil tidak menyesatkan. Apabila permintaan gagal, format respons tidak sesuai, atau scene belum tersedia, tool menampilkan pesan kesalahan yang dapat ditindaklanjuti dan tidak mengubah hierarki scene secara otomatis.

### 2.3.11 Perancangan Pemilihan Titik Awal dan Minimap

Pemilihan titik awal dirancang agar pengguna tidak langsung ditempatkan pada pivot model gedung yang mungkin berada di luar area berjalan. `SpawnPointRegistry` menyimpan pasangan `unityObjectName`, nama tampilan fallback, Transform spawn aman, anchor peta, serta radius sampling khusus bila diperlukan. `SpawnReceiver.SetSpawn(string)` mencari entri secara case-insensitive, memproyeksikan posisi ke NavMesh, menghentikan navigasi lama, menonaktifkan kontrol selama teleportasi, memindahkan karakter, lalu mengaktifkan kontrol kembali setelah spawn berhasil.

Scene final memuat 16 titik spawn, radius sampling umum 5 m, `groundOffset` 0,05 m, dan kewajiban pemilihan awal. Override 120 m digunakan untuk `cipto_mangunkusumo`, sedangkan dua titik gerbang belakang memakai 40 m. Nilai override merupakan toleransi pencarian NavMesh dan bukan jarak perpindahan yang diklaim sebagai hasil ukur.

`SpawnSelectionUI` dirancang untuk menampilkan overview ketika titik awal belum dipilih dan berubah menjadi minimap setelah spawn berhasil. Kamera minimap ditempatkan pada ketinggian 120 m, menggunakan ukuran ortografis 28 ketika mengikuti pemain, dan menampilkan marker pemain serta tujuan aktif. Render texture minimap berukuran 512 piksel, overview 1280 × 720 piksel, ukuran panel desktop 230 × 230 piksel, dan panel mobile 170 × 170 piksel. Bukti tampilan overview dan minimap ditempatkan pada Subbab 3.4.7, sedangkan bukti konfigurasi registry ditempatkan pada Subbab 3.3.5.

Transisi mode overview dan gameplay menggunakan `DayNightCycle` agar selector spawn memiliki kondisi visual yang lebih jelas. Saat overview dibuka, waktu dapat diatur ke `overviewStartTime` 9 dan fog menggunakan `overviewFogDensity` 0; setelah spawn berhasil, mode gameplay mengembalikan fog ke `gameplayFogDensity` 0,01. Nilai tersebut merupakan konfigurasi scene dan bukan pengukuran performa atau klaim kepemilikan aset lingkungan.

### 2.3.12 Perancangan Visual Tujuan dan Tutorial Adaptif

`DestinationHighlighter` dirancang sebagai penanda visual tambahan di luar garis rute. `NavigationGuide` membuat komponen tersebut secara otomatis apabila referensi Inspector kosong, memanggil `Show()` ketika tujuan ditetapkan, dan memanggil `Hide()` ketika navigasi berhenti atau komponen dinonaktifkan. Material pulse serta fallback bingkai portal digunakan untuk membantu pengguna mengenali gedung atau pintu tujuan tanpa mengubah mesh sumber.

Tutorial dirancang sebagai alur runtime yang dibentuk otomatis setelah scene dimuat. `GameTutorialController` menunggu sinkronisasi perangkat dan penyelesaian spawn, lalu menyediakan langkah bergerak, melihat sekeliling, berlari, melompat, serta pencarian tujuan. Instruksi dan sorotan kontrol dibedakan antara desktop dan mobile. Penyelesaian tutorial disimpan melalui `PlayerPrefs` per jenis perangkat, sementara tombol F8 dan F9 hanya menjadi fasilitas simulasi pada Editor.

Ketika pemain mencapai `stopDistance`, plugin `ReactBridge.jslib` memungkinkan Unity mengirim event browser `OnNavigationCompleted` satu kali dengan payload `unity_object_name`. `StopNavigation()` manual dan pergantian tujuan hanya membersihkan state tanpa mengirim event kedatangan. Listener serta tampilan pemberitahuan pada React merupakan kontribusi Full Stack Developer & System Integrator dan tidak dijadikan gambar bukti Faiz. Kontribusi penulis dibatasi pada pengiriman event dari runtime Unity; bukti yang relevan untuk bagian ini adalah log dispatch Unity atau Console browser dan retest yang memastikan penghentian manual tidak mengirim event selesai.

### 2.3.13 Perancangan Occlusion Culling dan Transisi Overview–Gameplay

`CampusOcclusionInstaller` dirancang sebagai editor tool tambahan untuk menandai renderer gedung yang memenuhi syarat sebagai occluder atau occludee, mengecualikan renderer dinamis dan material transparan, mengatur `OcclusionArea`, serta menghasilkan `OcclusionCullingData.asset`. Rancangan memakai ukuran minimum occluder 5 m, padding area `(20, 10, 20)` m, `smallestOccluder` 5 m, `smallestHole` 0,5 m, dan `backfaceThreshold` 100. Kamera gameplay `MainCamera` menggunakan hasil bake, sedangkan `MinimapCamera` tidak menggunakannya agar seluruh area peta tetap tersedia.

Transisi state dirancang agar `SpawnSelectionUI` menyimpan lalu menonaktifkan occlusion kamera gameplay ketika overview dibuka, kemudian memulihkannya setelah spawn berhasil atau selector ditutup. Perubahan tersebut berjalan bersama transisi waktu dan fog yang dirancang pada Subbab 2.3.11. Pemetaan state pada [TABREF:state_transisi_occlusion] menjadi acuan pengujian agar mode overview dan gameplay tidak dinilai hanya dari screenshot diam.

[TABLE-ID:state_transisi_occlusion]
[TABLECAPTION:Rancangan State Occlusion dan Fog pada Overview–Gameplay]
[TABLE]
State Runtime | Kamera Gameplay | Kamera Minimap | Fog | Kondisi yang Diverifikasi
Selector spawn terbuka | Occlusion disimpan lalu dinonaktifkan | Occlusion tetap nonaktif | 0 | Seluruh area dan marker pemilihan dapat dilihat
Spawn berhasil atau selector ditutup | Occlusion dipulihkan ke status scene final | Occlusion tetap nonaktif | 0,01 | Kamera gameplay kembali menggunakan data bake tanpa menghilangkan area minimap
[/TABLE]

Keberadaan data bake dan perubahan state dicatat sebagai implementasi engine, tetapi pengurangan renderer, draw call, atau frame time tetap `[TBD]` sampai diukur pada skenario yang sama.

## 2.4 Rencana Pengujian Proyek

Pengujian dirancang untuk memeriksa perilaku eksternal modul, bukan hanya memastikan bahwa metode dapat dipanggil. Cakupan skenario pada [TABREF:rencana_pengujian_unity] meliputi kondisi berhasil, kondisi gagal, dan kondisi tepi yang relevan dengan navigasi, data, kontrol, optimasi, serta editor tool.

### 2.4.1 Rencana Pengujian BuildingDatabase

Pengujian `BuildingDatabase` menggunakan respons API valid, respons dengan koleksi kosong, respons tidak valid, kegagalan jaringan, dan pencarian nama yang tidak dikenal. Kondisi awal mencatat URL endpoint, fixture respons, serta status cache. Hasil yang diperiksa meliputi perubahan `isLoaded`, isi `unityObjectNames`, isi `realNames`, fallback `GetRealName()`, dan pesan log. Bukti minimum berupa fixture JSON, log Play Mode, dan screenshot Inspector atau test runner.

### 2.4.2 Rencana Pengujian Navigasi dan Rendering Rute

Pengujian navigasi mencakup target yang tersedia pada cache, perbedaan kapitalisasi, target tidak ditemukan, tujuan pada area NavMesh, tujuan di luar area NavMesh, pemilihan tujuan baru ketika navigasi aktif, penghentian manual, dan penghentian otomatis pada `stopDistance`. Pengujian rendering mencakup jalur lurus, tikungan, perubahan elevasi, serta tangga. Bukti minimum berupa setup scene, rekaman Play Mode, log status jalur, dan screenshot garis serta label tujuan.

### 2.4.3 Rencana Pengujian Kontrol Desktop dan Mobile

Pengujian desktop memeriksa aktivasi Pointer Lock setelah tindakan pengguna, pergerakan kamera menggunakan delta tetikus, pelepasan kursor melalui ESC, dan penanganan ketika penguncian gagal. Pengujian perangkat bergerak memeriksa visibilitas joystick, respons sumbu pergerakan, tata letak terhadap canvas, serta ketiadaan joystick pada desktop. Perangkat, sistem operasi, browser, resolusi, dan metode input dicatat pada setiap hasil.

### 2.4.4 Rencana Pengujian Building Culling dan Build WebGL

Pengujian Building Culling membandingkan scene, posisi pemain, rute kamera, dan status selector yang sama sebelum serta sesudah optimasi. Pengujian mencakup ambang jarak 200 m, frustum `MainCamera`, grace period, pengecualian target navigasi, pemeliharaan renderer untuk minimap, occlusion aktif pada `MainCamera`, dan occlusion nonaktif pada `MinimapCamera`. Metrik yang dicatat meliputi renderer aktif, draw call, frame time, frame rate, dan penggunaan memori. Pengujian build mencatat versi Unity, konfigurasi Player Settings, ukuran berkas, waktu muat, perangkat, browser, jaringan, serta header `Content-Encoding` dan `Content-Type`. Target kurang dari 10 detik diperlakukan sebagai requirement sampai bukti pengukuran menunjukkan hasil aktual.

### 2.4.5 Rencana Pengujian DatabaseSyncChecker

Pengujian `DatabaseSyncChecker` menggunakan fixture yang sengaja memuat nama cocok, nama yang hanya ada pada API, dan root object yang hanya ada pada scene. Skenario tambahan mencakup child `Pointer`, variasi kapitalisasi, respons kosong, respons tidak valid, serta kegagalan jaringan. Hasil yang diharapkan adalah pengelompokan sesuai batas implementasi, daftar yang dapat disalin, pesan kesalahan yang jelas, dan tidak adanya perubahan otomatis pada scene.

### 2.4.6 Rencana Pengujian Spawn dan Minimap

Pengujian spawn mencakup identitas yang terdaftar, identitas yang tidak dikenal, titik di dekat NavMesh, titik di luar radius sampling, penggunaan radius override, penghentian navigasi lama, serta pemulihan kontrol karakter. Pengujian minimap memeriksa transisi overview ke mode mengikuti pemain, orientasi marker, marker tujuan, ukuran desktop dan mobile, serta pembaruan ketika resolusi layar berubah. Screenshot harus disertai log dan rekaman karena gambar diam tidak membuktikan perpindahan posisi.

### 2.4.7 Rencana Pengujian Highlighter, Tutorial, Sinkronisasi Perangkat, dan Event Selesai Navigasi

Pengujian highlighter memeriksa tampilan ketika tujuan dipilih, fallback portal, perubahan tujuan, dan pembersihan visual. Tutorial diuji pada mode desktop dan mobile untuk setiap langkah, penyimpanan progres, skip, serta restart Editor. `SetDevice` diuji dengan kedua nilai yang didukung dan nilai selain `mobile`. Event `OnNavigationCompleted` diuji pada build WebGL bersama listener React untuk membedakan pengiriman event Unity dari tampilan notifikasi pada dashboard. Skenario mencapai `stopDistance` harus menghasilkan payload tujuan tepat satu kali, sedangkan `StopNavigation()` manual atau pergantian tujuan tidak boleh dianggap sebagai kedatangan.

### 2.4.8 Rencana Pengujian Occlusion dan Transisi Overview–Gameplay

Pengujian `CampusOcclusionInstaller` memeriksa konfigurasi static occluder, static occludee, `OcclusionArea`, keberadaan `OcclusionCullingData.asset`, occlusion aktif pada `MainCamera`, dan occlusion nonaktif pada `MinimapCamera`. Pengujian transisi memeriksa bahwa selector spawn menonaktifkan occlusion gameplay dan mengatur fog overview menjadi 0, kemudian mengembalikan occlusion gameplay serta fog 0,01 setelah spawn berhasil. Hasil performa tetap `[TBD]` sampai profiler dilakukan pada scene, posisi, perangkat, dan durasi yang sama.

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
UT-08 | Route Rendering | Jalur melewati tikungan dan perubahan elevasi | Subdivisi linear, raycast, moving average, dan `LineRenderer` menghasilkan garis yang mengikuti permukaan | Screenshot dan rekaman
UT-09 | Pointer Lock | Pengguna mengaktifkan dan melepas kontrol desktop | Kursor terkunci setelah klik dan terlepas melalui ESC | Uji peramban desktop
UT-10 | Joystick Virtual | Build dibuka pada perangkat bergerak dan desktop | Joystick berfungsi pada mobile dan tidak mengganggu desktop | Uji lintas perangkat
UT-11 | Building Culling | Pengguna bergerak melintasi ambang tetap 200 m | Renderer berubah sesuai aturan, target navigasi tetap aktif, dan metrik sebelum-sesudah dapat dibandingkan | Unity Profiler, konfigurasi scene, dan rekaman
UT-12 | WebGLOptimizer | Menu konfigurasi dijalankan pada project final | Player Settings WebGL sesuai konfigurasi final yang terdokumentasi | Screenshot Player Settings dan log Console
UT-13 | WebGL Build | Build produksi dimuat melalui hosting yang ditetapkan | Berkas termuat tanpa kesalahan MIME atau compression header | DevTools Network dan log browser
UT-14 | DatabaseSyncChecker | Data API dan scene memiliki nama cocok, hilang, dan berlebih | Kategori cocok dan hilang memakai hierarki rekursif, kategori scene belum terdaftar memakai root object, dan daftar dapat disalin | Screenshot editor dan fixture uji
UT-15 | DatabaseSyncChecker | Endpoint kosong, tidak valid, atau gagal | Tool menampilkan pesan yang jelas dan tidak mengubah scene | Log dan screenshot error
UT-16 | SpawnPointRegistry | Pengguna memilih titik spawn terdaftar yang berada dalam radius NavMesh | Karakter dipindahkan ke posisi valid dan kontrol dipulihkan | Log, screenshot, dan rekaman
UT-17 | SpawnPointRegistry | Nama tidak terdaftar atau posisi berada di luar radius sampling | Spawn ditolak dengan pesan diagnosis tanpa memindahkan karakter | Log Play Mode
UT-18 | SpawnSelectionUI dan MinimapFollow | Spawn selesai dan navigasi menuju tujuan aktif | Overview berubah menjadi minimap serta marker pemain dan tujuan diperbarui | Screenshot dan rekaman desktop/mobile
UT-19 | DestinationHighlighter | Tujuan dipilih, diganti, lalu navigasi dihentikan | Highlighter mengikuti tujuan aktif dan dibersihkan ketika selesai | Screenshot dan rekaman
UT-20 | GameTutorialController | Tutorial dijalankan pada mode desktop dan mobile | Instruksi, progres, dan sorotan kontrol sesuai perangkat | Screenshot dan rekaman dua mode
UT-21 | WebPlatformSync | React mengirim `SetDevice("mobile")` dan `SetDevice("desktop")` | Joystick, spawn UI, dan tutorial mengikuti mode perangkat | Log browser, screenshot, dan rekaman
UT-22 | OnNavigationCompleted | Pengguna mencapai `stopDistance`, lalu diulangi dengan penghentian manual atau pergantian tujuan | Unity mengirim payload `unity_object_name` tepat satu kali hanya saat tiba; pembatalan manual tidak mengirim event kedatangan | Console browser, screenshot, dan rekaman retest
UT-23 | Camera Frustum dan Occlusion Culling | Jalankan scene gameplay, putar kamera, buka selector spawn, lalu kembali ke gameplay | Renderer di luar jarak/frustum ditangani sesuai grace period, target navigasi tetap aktif, minimap tidak kehilangan area, dan status occlusion kamera berubah sesuai mode | Profiler, log runtime, Inspector, dan rekaman
UT-24 | Transisi Overview–Gameplay | Buka selector sebelum spawn, pilih spawn valid, lalu buka selector ulang | Fog overview bernilai 0, occlusion gameplay nonaktif saat selector, fog gameplay bernilai 0,01, dan occlusion gameplay pulih setelah spawn | Log runtime, Inspector, dan rekaman
[/TABLE]

Hasil pengujian baru dapat dinyatakan lulus setelah setiap bukti pada tabel tersedia. Skenario yang belum memiliki artefak akan tetap diberi status `[TBD: hasil pengujian dan bukti]` pada BAB III.

---

# BAB III IMPLEMENTASI PROYEK

## 3.1 Profil Mitra

### 3.1.1 Nama Organisasi atau Lembaga Mitra

Mitra proyek adalah Unit Penunjang Akademik Teknologi Informasi dan Komunikasi Universitas Pembangunan Nasional Veteran Jakarta atau UPA TIK UPNVJ. Perwakilan mitra yang tercatat pada fakta proyek adalah Asep Saeful Ridwan, S.Kom. selaku Kepala UPA TIK UPNVJ.

### 3.1.2 Deskripsi Mitra

UPA TIK UPNVJ merupakan unit yang berkaitan dengan penyelenggaraan serta dukungan teknologi informasi dan komunikasi di lingkungan universitas. Dalam proyek ini, mitra memberikan konteks kebutuhan layanan informasi kampus, masukan terhadap ruang lingkup, dan koordinasi mengenai integrasi sistem. Deskripsi kewenangan organisasi yang lebih rinci perlu diselaraskan dengan profil resmi universitas apabila akan ditambahkan ke laporan. [BUTUH SITASI]

### 3.1.3 Hubungan Mitra dengan Proyek

Mitra berhubungan dengan proyek sebagai pihak yang memberikan konteks kebutuhan dan validasi terhadap pengembangan sistem integrasi denah virtual. Pembagian tanggung jawab tim serta kebutuhan umum sistem dibahas melalui koordinasi dengan mitra, sedangkan implementasi teknis dilakukan oleh tiga anggota tim sesuai perannya masing-masing.

## 3.2 Metode Implementasi

Repository `C:\Users\Faiz\Proposal` dengan Unity 6000.2.6f1 digunakan sebagai baseline historis, sedangkan implementasi final diverifikasi pada `C:\Users\Faiz\Proposal\T_A---Copy` dengan Unity 6000.4.1f1, scene `Assets/Scene/SceneUtama.unity`, dan commit acuan `5f575c0`. Seluruh nilai konfigurasi serta bukti hasil pada subbab berikut harus berasal dari project final; baseline tidak digunakan sebagai bukti keberhasilan fitur.

### 3.2.1 Implementasi BuildingDatabase

`BuildingDatabase` diimplementasikan sebagai modul pengambilan data runtime di dalam Unity. Method `Awake()` mengganti nilai Inspector menjadi endpoint produksi `/api/unity/data`, sedangkan conditional compilation menggunakan URL relatif `/api/unity/data` pada build WebGL. Modul memproses koleksi `gedung` dan `fasilitas`, lalu mengganti cache secara atomik setelah parsing berhasil. Cache `unityObjectNames` digunakan untuk mengetahui identitas yang tersedia, dictionary `realNames` digunakan oleh label navigasi, dan cache tambahan menghubungkan ID gedung dengan target gedung maupun fasilitas.

Modul menyediakan `GetRealName()` dengan fallback ke nilai input ketika nama tidak ditemukan. Respons JSON valid dengan dua koleksi kosong tetap menghasilkan `isLoaded = true` dan cache kosong, sedangkan respons null, parsing gagal, atau kegagalan request tidak mengaktifkan status tersebut. Setelah pemuatan berhasil, modul memanggil `NavigationReceiver.RebuildCache()` agar daftar Transform dibentuk dari data terbaru. Bukti log runtime ditempatkan pada Subbab 3.4.2 agar pembacaan hasil tetap berada pada bagian implementasi.

Hierarki prefab yang menjadi tujuan pemetaan data diperlihatkan pada [FIGREF:impl_pointer_hierarchy]. Child `Pointer` menampung GameObject yang namanya mengikuti `unity_object_name`, sehingga titik target dapat dipisahkan dari mesh visual bangunan. Hierarki tersebut didokumentasikan sebagai kontrak scene; kontribusi penulis dimulai pada proses pencarian dan penggunaan Transform, bukan pada pembuatan model atau struktur aset sumber.

[FIGURE:impl_pointer_hierarchy]
[FIGCAPTION:Hierarki Prefab Gedung dengan Child Pointer di Unity]

### 3.2.2 Implementasi NavigationReceiver dan NavigationGuide

`NavigationReceiver` menjadi titik masuk perintah dari JavaScript. Method publik `NavigateTo(string unityObjectName)` dipanggil melalui `SendMessage` dan bertanggung jawab menemukan Transform tujuan. Input kosong ditolak dengan warning. Lookup awal menggunakan cache agar pencarian berulang tidak memindai seluruh scene. Apabila target belum tersedia, fallback membangun ulang cache dan melakukan pencarian tambahan termasuk pada objek tidak aktif. Perbandingan nama dilakukan dengan `ToLowerInvariant()`, sedangkan kegagalan dicatat sebagai warning tanpa melempar exception yang menghentikan aplikasi.

Transform yang ditemukan diteruskan ke `NavigationGuide` bersama `destinationKey` teknis. Modul ini mengelola status tujuan aktif, menjalankan `NavMesh.CalculatePath()`, mengirim titik jalur ke renderer, serta memperbarui label nama dan jarak. `CompleteNavigation()` hanya dipanggil ketika path berstatus lengkap, jarak jalur tersisa dan jarak pemain ke endpoint sama-sama berada dalam ambang efektif maksimal 2 m. Method `StopNavigation()` membersihkan state ketika pengguna membatalkan rute atau memilih tujuan baru tanpa mengirim event kedatangan.

Implementasi final mempertahankan rute lengkap terakhir apabila rekalkulasi baru gagal sesaat, menolak `PathPartial` atau `PathInvalid`, dan mengulangi pencarian setiap 1 detik. Posisi pemain menggunakan radius sampling maksimum 2 m, sedangkan tujuan dapat menggunakan fallback 5 m setelah pencarian dekat gagal. Setiap hasil sampling juga diperiksa terhadap selisih vertikal maksimum 2 m untuk mengurangi risiko snap ke lantai lain.

### 3.2.3 Implementasi Rendering Rute

Implementasi rendering menggunakan titik sudut dari `NavMeshPath` sebagai input. Setiap segmen dibagi secara linear dengan interval 0,4 m. `Physics.RaycastNonAlloc()` ditembakkan dari 1,5 m di atas setiap titik sejauh 3 m ke bawah. Sistem mengabaikan trigger serta collider pemain dan target, lalu memilih permukaan terdekat dalam toleransi vertikal 0,75 m. Koordinat permukaan diberi offset 0,6 m dan dihaluskan dengan moving average berjendela 4 sebelum dikirim ke `LineRenderer`. Fungsi helper Catmull–Rom yang masih terdapat pada script tidak dipanggil oleh alur tersebut dan tidak dianggap sebagai implementasi final.

Label tiga dimensi berbasis TextMeshPro menampilkan nama tujuan yang diperoleh melalui `BuildingDatabase` dan jarak tersisa yang dihitung dari posisi pengguna. Insiden awal pada skenario BB-20 menunjukkan bahwa label pernah menampilkan `unity_object_name` akibat script testing yang ikut terkompilasi. Tindakan korektif memisahkan script testing dari build produksi dan memulihkan nama tampilan fasilitas; hasil retest dicatat pada fragment Black Box bersama.

Bukti konfigurasi `LineRenderer`, hasil rute, dan elevasi ditempatkan pada Subbab 3.3.4, 3.4.2, dan 3.4.3 agar setiap gambar memiliki narasi serta rujukan yang jelas.

### 3.2.4 Implementasi Building Culling dan WebGL Settings Optimizer

`BuildingCulling` diimplementasikan untuk mengubah status renderer bangunan berdasarkan jarak dan pandangan kamera terhadap pengguna. Modul memindai objek bertag `Cullable`, menyimpan status awal renderer, menggunakan `CullingPoint` bila tersedia, memeriksa jarak setiap 1 detik, menjalankan frustum check setiap 0,1 detik dengan padding 10 m dan grace period 0,35 detik, serta mempertahankan renderer target navigasi dan area yang diperlukan minimap. Frustum culling dijeda saat selector spawn terbuka. Scene final memakai batas minimum serta maksimum 200 m; akibatnya nilai awal 500 m dikunci menjadi 200 m dan mode `Combined` belum menghasilkan perubahan jarak adaptif. Konfigurasi editor dan data bake telah didokumentasikan, tetapi jumlah renderer aktif sebelum–sesudah, perubahan status occlusion saat runtime, dan hasil Unity Profiler masih `[TBD]`.

`CampusOcclusionInstaller` ditambahkan sebagai editor tool melalui menu `Tools > UPNVJ > Occlusion`. Tool mengonfigurasi static flags pada renderer gedung, membuat atau memperbarui `OcclusionArea`, mengaktifkan occlusion pada `MainCamera`, menonaktifkannya pada `MinimapCamera`, lalu menjalankan bake `OcclusionCullingData.asset`. Implementasi ini merupakan bagian dari optimasi engine; tidak ada klaim pengurangan draw call atau frame time sebelum profiler tersedia.

`WebGLOptimizer` diimplementasikan melalui menu `Tools > UPNVJ > WebGL > Apply Safe Release Settings` serta alias lama `Tools > UPNVJ > Apply Optimal WebGL Settings`. Menu menerapkan release build, `runInBackground`, Brotli, decompression fallback, data caching, managed stripping High, IL2CPP Master dengan Optimize Size, engine code stripping, WebAssembly 2023, exception support `Explicitly Thrown Exceptions Only`, dan optimasi Wasm Disk Size tanpa LTO. Tool juga menyediakan audit texture tanpa perubahan serta optimasi kandidat texture 3D maksimum 1024 piksel. Konfigurasi editor dan Network ditempatkan pada Subbab 3.3.1 serta 3.4.4.

### 3.2.5 Implementasi Pointer Lock dan Joystick Virtual

Pointer Lock diintegrasikan pada alur kontrol desktop agar rotasi pandangan menggunakan delta pergerakan tetikus dan tidak berhenti ketika kursor mencapai tepi layar. Penguncian dimulai setelah klik pengguna pada canvas dan dilepas melalui ESC. Implementasi perlu menangani perubahan status serta kegagalan penguncian agar pengguna tidak kehilangan kendali atas antarmuka peramban.

Kontrol perangkat bergerak menggunakan prefab `UI_Virtual_Joystick` dan New Input System. `WebPlatformSync.SetDevice(string)` mengubah mode menjadi `mobile` hanya ketika nilai yang diterima cocok secara case-insensitive; nilai lain diperlakukan sebagai `desktop`. Mode tersebut mengatur visibilitas joystick dan diteruskan ke spawn UI serta tutorial. Screenshot desktop dan mobile telah mendokumentasikan perbedaan tampilan, sedangkan respons input serta perpindahan karakter masih memerlukan rekaman dua perangkat dan retest build yang sama.

### 3.2.6 Implementasi DatabaseSyncChecker

`DatabaseSyncChecker` diimplementasikan sebagai EditorWindow melalui menu `Tools > UPNVJ > Check Database Sync`. Tool mengirim permintaan ke `/api/unity/names`, mengumpulkan nama GameObject pada hierarki scene secara rekursif, lalu membandingkan kedua himpunan secara case-insensitive. Kategori cocok dan hilang di scene menggunakan seluruh nama hierarki, tetapi kategori yang belum terdaftar di database hanya membandingkan nama root object. Batas tersebut dicatat agar hasil tool tidak ditafsirkan sebagai audit seluruh child scene dari arah sebaliknya.

Antarmuka tool diperlihatkan pada [FIGREF:impl_sync_db_checker] yang menyediakan ringkasan hasil dan tindakan untuk menyalin daftar missing ke clipboard. Pemeriksaan ini digunakan sebelum build agar kesalahan penamaan dapat diperbaiki tanpa menunggu kegagalan navigasi pada runtime.

[FIGURE:impl_sync_db_checker]
[FIGCAPTION:Tampilan UI Database Sync Checker di Unity Editor]

### 3.2.7 Implementasi SpawnPointRegistry, SpawnSelectionUI, dan MinimapFollow

`SpawnPointRegistry` mengelola 16 titik awal dan menyediakan receiver WebGL `SpawnReceiver.SetSpawn(string)`. Sebelum memindahkan karakter, sistem mencari entri secara case-insensitive dan memanggil `NavMesh.SamplePosition()` dengan radius umum 5 m atau override per titik. Navigasi lama dihentikan, input serta `CharacterController` dinonaktifkan sementara, posisi dan rotasi karakter diperbarui, kemudian kontrol dipulihkan dan event `SpawnCompleted` dikirim.

`SpawnSelectionUI` membentuk canvas, overview, tombol marker, dan panel minimap secara runtime. Ketika pemilihan terbuka, kontrol karakter dan Pointer Lock dilepas. Setelah spawn berhasil, overview ditutup dan `MinimapFollow` memindahkan kamera ortografis agar mengikuti pemain. Marker tujuan hanya ditampilkan ketika navigasi aktif. Bukti tampilan spawn dan minimap ditempatkan pada Subbab 3.4.7, sedangkan konfigurasi `SpawnReceiver` ditempatkan pada Subbab 3.3.5. [TBD: log spawn dan rekaman perpindahan]

### 3.2.8 Implementasi DestinationHighlighter dan Event OnNavigationCompleted

`NavigationGuide` mencari `DestinationHighlighter` pada GameObject yang sama dan membuatnya secara otomatis apabila belum tersedia. Ketika `StartNavigation()` dipanggil, highlighter memproses renderer tujuan atau fallback portal. Saat pengguna mencapai `stopDistance`, `CompleteNavigation()` membersihkan visual, memicu event C# `NavigationCompleted`, dan pada build WebGL mengirim `DispatchReactEvent("OnNavigationCompleted", payload)` melalui `ReactBridge.jslib`; payload JSON membawa kunci `unity_object_name`. Sebaliknya, `StopNavigation()` hanya membersihkan state dan mencatat pembatalan tanpa mengirim event selesai. Pemisahan ini mencegah event kedatangan terkirim ketika pengguna membatalkan rute atau mengganti tujuan. Bukti highlight ditempatkan pada Subbab 3.4.7, sedangkan pengiriman event masih memerlukan log dispatch dan retest terintegrasi. Tampilan notifikasi React tidak digunakan sebagai bukti kontribusi penulis.

### 3.2.9 Implementasi GameTutorialController, GameTutorialUI, dan WebPlatformSync

`GameTutorialController` dibentuk melalui `RuntimeInitializeOnLoadMethod` apabila scene belum memiliki instance. Controller melakukan auto-wiring terhadap spawn, input, kontrol karakter, sinkronisasi perangkat, dan navigasi. Alur desktop maupun mobile terdiri atas bergerak, melihat sekeliling, berlari, melompat, serta pencarian tujuan apabila receiver tersedia. Progres disimpan terpisah untuk setiap jenis perangkat melalui `PlayerPrefs`, sedangkan `GameTutorialUI` membangun tampilan dan sorotan kontrol secara runtime.

`WebPlatformSync` menerima `SetDevice(string)` dari React, mengatur joystick, meneruskan mode ke `SpawnSelectionUI`, dan mengirim event `DeviceChanged` kepada tutorial. Controller menunggu handshake tersebut sampai 1,75 detik sebelum menggunakan `Application.isMobilePlatform` sebagai fallback. Bukti visual tutorial desktop dan mobile ditempatkan pada Subbab 3.4.7, sedangkan log mode perangkat serta rekaman interaksi masih diperlukan untuk membuktikan perubahan state secara dinamis.

### 3.2.10 Implementasi CampusOcclusionInstaller dan Transisi Overview–Gameplay

`CampusOcclusionInstaller` dijalankan dari menu editor untuk memindai root bertag `Cullable`, mengelompokkan renderer statis sebagai occluder atau occludee, mengabaikan renderer dinamis serta material transparan, mengatur area pandang kampus, dan menghasilkan data bake pada `Assets/Scene/SceneUtama/OcclusionCullingData.asset`. `MainCamera` diaktifkan untuk occlusion, sedangkan `MinimapCamera` tidak menggunakannya agar peta tidak kehilangan area.

`SpawnSelectionUI` menyimpan status occlusion kamera gameplay ketika selector dibuka, menonaktifkannya selama overview, lalu mengembalikan status semula setelah spawn atau selector ditutup. `DayNightCycle` mengatur waktu overview ke 09.00 ketika pemilihan awal dibuka, memakai fog 0 pada overview, dan mengubah fog menjadi 0,01 pada mode gameplay. Konfigurasi occlusion editor telah didokumentasikan pada Subbab 3.3.6. Dampak performa serta transisi overview–gameplay tetap menunggu log runtime, rekaman, dan hasil Unity Profiler yang sebanding.

## 3.3 Konfigurasi dan Metadata Sistem

### 3.3.1 Konfigurasi Build WebGL

Konfigurasi build final pada project Unity 6000.4.1f1 dengan revision `336a400b9ea2` dan commit Unity `5f575c0` adalah sebagai berikut:

1. Platform target menggunakan WebGL dan hanya `Assets/Scene/SceneUtama.unity` yang aktif pada `EditorBuildSettings`.
2. Scripting backend menggunakan IL2CPP Master dengan mode Optimize Size.
3. Compression Format menggunakan Brotli.
4. Decompression Fallback, Data Caching, `runInBackground`, dan WebAssembly 2023 diaktifkan.
5. Managed Stripping Level menggunakan High dan engine code stripping diaktifkan. `Enable Exceptions` menggunakan `Explicitly Thrown Exceptions Only`, sesuai konfigurasi aman pada `WebGLOptimizer` ketika WebAssembly 2023 aktif.
6. Optimasi Wasm menggunakan Disk Size tanpa LTO, sedangkan development build dan diagnostics dinonaktifkan.
7. Berkas build ditempatkan pada jalur statis yang dikonsumsi dashboard React.
8. Server perlu menyajikan berkas `.br` dan WebAssembly dengan header yang sesuai; pemeriksaan dilakukan melalui panel Network pada DevTools.

Versi executable Unity Editor yang digunakan diperlihatkan pada [FIGREF:unity_version_editor]. Gambar tersebut mengonfirmasi versi 6000.4.1f1, sedangkan revision project `336a400b9ea2` bersumber dari `ProjectVersion.txt`. Target Web aktif dan penggunaan `SceneUtama` ditunjukkan pada [FIGREF:webgl_build_profile].

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

Konfigurasi komponen engine dicatat dari scene `SceneUtama` pada commit acuan terbaru `5f575c0` agar implementasi dapat direproduksi. Tampilan editor pada [FIGREF:unity_scene_hierarchy] memperlihatkan environment kampus serta kelompok kamera, pemain, UI, receiver, spawn, dan minimap pada hierarki scene dengan target Web aktif dan scene tersimpan.

[FIGURE:unity_scene_hierarchy]
[FIGCAPTION:SceneUtama dan Hierarki Komponen Engine]

1. **NavMeshSurface dan agen:** GameObject `NavMesh_Bake`, Agent Type 0, radius 0,5 m, tinggi 2 m, climb 0,75 m, maximum slope 45 derajat, layer mask seluruh layer, serta data bake `SceneUtama`.
2. **Layer dan LayerMask raycast:** `groundMask` menggunakan seluruh layer; `surfaceProbeHeight` 1,5 m menghasilkan raycast total 3 m ke bawah, sedangkan `surfaceProjectionTolerance` 0,75 m mencegah garis memilih permukaan yang terlalu jauh dari titik NavMesh. Nilai Y titik dipertahankan ketika tidak ada permukaan valid.
3. **LineRenderer:** lebar awal dan akhir 0,2 m, alignment `TransformZ`, texture mode Tile, tekstur putus-putus 50 persen transparan dibentuk saat runtime, dan offset vertikal 0,6 m.
4. **Parameter navigasi:** posisi pemain memakai radius sampling maksimum 2 m, tujuan memakai radius dekat maksimum 2 m dengan fallback 5 m, dan selisih vertikal sampling dibatasi 2 m. Scene menyimpan `stopDistance` 5 m, tetapi kode membatasi ambang kedatangan efektif maksimum 2 m. `pathUpdateDistance` bernilai 1 m, interval retry 1 detik, `pointSpacing` 0,4 m, dan `smoothingWindow` 4.
5. **Input Actions dan Pointer Lock:** catat action map, binding desktop, binding sentuh, tindakan aktivasi Pointer Lock, tombol pelepas, serta handler perubahan atau kegagalan status. [TBD: file `.inputactions`, script, dan screenshot]
6. **Joystick virtual:** scene menyediakan joystick gerak dan pandang, tombol sprint, serta tombol lompat; visibilitas induk ditentukan oleh `WebPlatformSync`. [TBD: konfigurasi prefab dan bukti perangkat]
7. **Building Culling:** tag `Cullable`, batas minimum 200 m, batas maksimum 200 m, nilai awal 500 m yang dikunci menjadi 200 m, step maksimum 50 m, target 60 fps, interval jarak 1 detik, mode `Combined`, frustum check 0,1 detik, padding bounds 10 m, grace period 0,35 detik, jeda saat selector map terbuka, dan pemeliharaan renderer yang terlihat minimap. Tidak terdapat hysteresis terpisah pada kode aktif.

Nilai serialized `NavigationGuide` yang mengatur jarak berhenti, interval pembaruan, subdivisi titik, smoothing, dan offset garis ditunjukkan pada [FIGREF:navigation_guide_config]. Komponen `PathLine` yang menjadi penerima hasil rute divisualkan pada [FIGREF:path_line_config], sehingga konfigurasi renderer tidak hanya dijelaskan dari script.

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

Keempat gambar tersebut mendokumentasikan konfigurasi editor, bukan hasil benchmark performa. Perubahan status kamera selama transisi overview masih memerlukan log atau rekaman runtime. [TBD: log atau rekaman transisi overview–gameplay]

## 3.4 Laporan Implementasi Proyek

### 3.4.1 Logbook Implementasi Proyek

Ringkasan logbook pada [TABREF:logbook_faiz] disusun berdasarkan fase kerja. Tanggal, tautan commit, screenshot, dan status perlu dilengkapi dari bukti aktual sebelum laporan dinyatakan final.

[TABLE-ID:logbook_faiz]
[TABLECAPTION:Logbook Implementasi Modul Simulator dan Engine]
[TABLE]
Fase | Kegiatan | Keluaran | Bukti dan Tanggal
Analisis | Menetapkan kontrak `unity_object_name`, alur `SendMessage`, dan kebutuhan navigasi | Spesifikasi integrasi engine | [TBD: tautan dokumen, commit, dan tanggal]
Perancangan | Menyusun hierarki scene, NavMesh, alur pathfinding, rute, dan kontrol | Rancangan modul Unity | [TBD: diagram, commit, dan tanggal]
Implementasi Data | Mengembangkan `BuildingDatabase` dan cache nama | Modul konsumsi `/api/unity/data` | Commit final file `6378864`, 20 Juli 2026; [TBD: hasil uji]
Implementasi Navigasi | Mengembangkan `NavigationReceiver` dan `NavigationGuide` | Navigasi tujuan berbasis NavMesh | Dasar implementasi `007d207`, pemisahan event `1845c65`, hardening routing `968d067`, dan perbaikan final `5f575c0`; [TBD: rekaman]
Implementasi Rute | Menerapkan subdivisi linear, raycast, moving average, label, dan jarak | Rute visual mengikuti kontur | Commit `3af9d9f`; [TBD: screenshot]
Implementasi Optimasi | Mengembangkan `BuildingCulling`, frustum culling, occlusion installer, dan `WebGLOptimizer` | Culling dan baseline build | Commit `0d90ecb`, `7c630f0`, dan `9fdf0fa`; [TBD: profiler]
Implementasi Kontrol | Mengintegrasikan Pointer Lock, joystick virtual, dan sinkronisasi perangkat | Kontrol desktop dan mobile | Commit `f82f465` dan final `5f575c0`; [TBD: uji perangkat]
Implementasi Tool | Mengembangkan `DatabaseSyncChecker` dan `CampusOcclusionInstaller` | Pemeriksaan sinkronisasi dan konfigurasi occlusion | Commit `4540686` dan `7c630f0`; [TBD: screenshot]
Implementasi Orientasi | Menambahkan spawn, minimap, highlighter, tutorial adaptif, dan transisi overview | Orientasi dan onboarding pengguna | Commit `007d207`, `26643f6`, `7c630f0`, `968d067`, dan `f82f465`; screenshot tersedia, [TBD: rekaman dan retest]
Integrasi | Menghasilkan build WebGL dan menghubungkannya dengan dashboard | Build terintegrasi | [TBD: URL build, commit, dan tanggal]
Pengujian | Menjalankan skenario, memperbaiki BB-20, dan melakukan retest | Hasil uji dan catatan koreksi | [TBD: dokumen uji dan bukti retest]
[/TABLE]

### 3.4.2 Hasil dan Bukti Implementasi Navigasi

Implementasi menghasilkan alur yang menerima `unity_object_name`, menemukan Transform tujuan, memproyeksikan pemain dan target ke NavMesh, menghitung jalur, menampilkan rute, memperbarui nama serta jarak, dan membedakan penyelesaian otomatis dari pembatalan manual. Hasil Black Box bersama mencatat bahwa pemilihan tujuan, rute terpendek, penghentian otomatis, ketahanan terhadap variasi nama, dan interupsi navigasi telah diuji. Log runtime pada [FIGREF:building_database_runtime_log] menunjukkan bahwa `BuildingDatabase` mengambil `/api/unity/data`, memuat 19 gedung, 331 fasilitas, dan membentuk 323 `unityObjectNames` sebelum `NavigationReceiver` membangun cache scene.

[FIGURE:building_database_runtime_log]
[FIGCAPTION:Log Runtime BuildingDatabase dan Cache NavigationReceiver]

Hasil navigasi aktif pada [FIGREF:active_navigation_route] memperlihatkan karakter third-person, garis rute putus-putus, label nama tujuan, jarak tersisa, minimap, dan kontrol mobile dalam satu skenario. Bukti ini mendukung klaim visual rute, tetapi rekaman Play Mode masih diperlukan untuk membuktikan perubahan state ketika pengguna bergerak atau menghentikan navigasi.

[FIGURE:active_navigation_route]
[FIGCAPTION:Rute Navigasi Aktif pada Game View]

[TBD: rekaman Play Mode untuk perpindahan karakter, penghentian otomatis, dan interupsi navigasi]

### 3.4.3 Hasil dan Bukti Rendering Rute

Bagian ini membuktikan perubahan titik sudut `NavMeshPath` menjadi garis rute yang dapat diikuti pengguna. Bukti perlu memperlihatkan corners mentah, hasil subdivisi linear, penyesuaian raycast, hasil moving average, label nama tujuan, dan jarak tersisa. Scene, tujuan, posisi awal, layer permukaan, serta konfigurasi `LineRenderer` harus sama ketika hasil dibandingkan. Rute pada [FIGREF:route_elevation] digunakan sebagai bukti awal bahwa garis mengikuti permukaan pada area yang memiliki perubahan elevasi, bukan sekadar garis lurus pada bidang datar.

[FIGURE:route_elevation]
[FIGCAPTION:Rute pada Perubahan Elevasi Scene]

Alur rendering rute diringkas pada [TABREF:alur_rendering_rute] agar hubungan antara perhitungan NavMesh dan hasil visual dapat dibaca tanpa bergantung hanya pada screenshot.

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

[TBD: rekaman rute pada tikungan atau tangga dan pembandingan corners mentah dengan titik akhir]

### 3.4.4 Hasil dan Bukti Implementasi Optimasi WebGL

Implementasi optimasi mencakup pengendalian renderer melalui batas jarak, camera-frustum culling, occlusion culling berbasis `OcclusionCullingData.asset`, serta konfigurasi produksi melalui WebGL optimizer. Konfigurasi jarak scene final efektif tetap 200 m, sehingga kemampuan adaptasi jarak belum dapat dinilai sebagai hasil. Project facts mencatat skor Lighthouse baseline untuk dashboard secara keseluruhan, tetapi skor tersebut tidak dapat diklaim sebagai hasil optimasi engine saja. Ukuran build prototipe lama juga tidak digunakan sebagai hasil final. Ukuran berkas, waktu muat, frame rate, renderer aktif, draw call, dan memori harus diukur pada skenario yang sama sebelum dan sesudah perubahan.

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

Kedua gambar belum menjadi benchmark sebelum–sesudah yang konklusif karena menggunakan NVIDIA Statistics Overlay, bukan Unity Profiler; durasi sampling, identitas perangkat, draw call, renderer aktif, frame time Unity, dan indikator status aktif/nonaktif komponen juga belum tercatat di dalam capture. Angka sesaat pada overlay tidak digunakan untuk menyimpulkan peningkatan performa. Hasil kuantitatif tetap `[TBD: Unity Profiler dan tabel benchmark pada kondisi yang terdokumentasi]`.

### 3.4.5 Hasil dan Bukti Kontrol Lintas Perangkat

Bagian ini membuktikan bahwa kontrol third-person desktop dan perangkat bergerak menggunakan jalur input yang sesuai. Tampilan desktop pada [FIGREF:desktop_control] menunjukkan build WebGL dengan navigasi aktif, minimap, dan tanpa joystick mobile. Tampilan mobile pada [FIGREF:mobile_control] menunjukkan joystick gerak, tombol sprint, tombol lompat, minimap, dan tata letak antarmuka perangkat bergerak.

[FIGURE:desktop_control]
[FIGCAPTION:Tampilan Kontrol Desktop pada Build WebGL]

[FIGURE:mobile_control]
[FIGCAPTION:Tampilan Kontrol Mobile pada Build WebGL]

Kedua screenshot membuktikan perbedaan tampilan menurut mode perangkat, tetapi belum membuktikan respons input, Pointer Lock, atau perpindahan karakter. Bukti interaksi tetap memerlukan file `.inputactions`, identitas perangkat dan browser, serta rekaman 15–30 detik. [TBD: rekaman Pointer Lock dan kontrol mobile]

### 3.4.6 Hasil dan Bukti DatabaseSyncChecker

Bagian ini membuktikan bahwa tool editor membandingkan data `/api/unity/names` dengan hierarki scene dan menampilkan kategori hasil sesuai batas implementasi. Hasil aktual pada [FIGREF:database_sync_checker_result] menampilkan 320 nama ditemukan, 3 nama dari API belum tersedia di scene, dan 14 root object scene belum terdaftar di database. Daftar contoh dan tombol penyalinan juga terlihat pada window hasil.

[FIGURE:database_sync_checker_result]
[FIGCAPTION:Hasil Pemeriksaan DatabaseSyncChecker]

Angka tersebut mendokumentasikan satu pemeriksaan terhadap scene dan endpoint aktif, bukan hasil fixture terkendali. Status pengujian UT-14 dan UT-15 tetap `[TBD]` sampai respons acuan, commit, kondisi API kosong/gagal, serta retest dicatat. Screenshot lama `impl_sync_db_checker` tetap diperlakukan sebagai ilustrasi antarmuka, sedangkan gambar baru menjadi bukti hasil pemeriksaan aktual.

### 3.4.7 Hasil Spawn, Minimap, Highlighter, dan Tutorial

Implementasi final memuat pemilihan spawn yang tervalidasi terhadap NavMesh, minimap yang mengikuti pemain, marker tujuan, destination highlighter, tutorial adaptif, serta pengiriman event selesai navigasi. Keberadaan script, konfigurasi scene, dan screenshot tutorial membuktikan implementasi visual fitur, tetapi status tindak lanjut UAT tetap `[TBD]` sampai interaksi diuji ulang pada build terintegrasi yang sama.

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

Screenshot tersebut membuktikan penyesuaian visual berdasarkan mode perangkat, tetapi belum membuktikan handshake `SetDevice`, respons input, atau penyimpanan progres. Bukti dinamis masih memerlukan log mode perangkat, log spawn, dan rekaman interaksi pada build yang sama. Tampilan notifikasi kedatangan pada React tidak disertakan karena berada di luar kontribusi penulis.

### 3.4.8 Hasil dan Bukti Occlusion Culling serta Transisi Overview–Gameplay

Implementasi final menyertakan `OcclusionArea`, data bake, occlusion aktif pada `MainCamera`, dan occlusion nonaktif pada `MinimapCamera` sebagaimana dibuktikan pada Subbab 3.3.6. Saat overview aktif, kamera gameplay dirancang menonaktifkan occlusion sementara; setelah spawn berhasil, statusnya dipulihkan. `DayNightCycle` mengatur fog overview 0 dan fog gameplay 0,01.

Bukti yang diterima membuktikan konfigurasi statis editor, tetapi belum membuktikan perubahan status selama transisi atau dampaknya terhadap renderer, draw call, dan frame time. Hasil performa serta transisi runtime tetap `[TBD: log CampusOcclusion, rekaman buka/tutup selector, Unity Profiler, dan benchmark sebanding]`.

### 3.4.9 Batas Kontribusi Penulis

Batas kontribusi pada [TABREF:batas_kontribusi_faiz] digunakan agar implementasi bersama tidak diklaim sebagai pekerjaan individual penulis.

[TABLE-ID:batas_kontribusi_faiz]
[TABLECAPTION:Batas Kontribusi Penulis dalam Sistem Terintegrasi]
[TABLE]
Komponen | Pemilik Utama | Keterlibatan Penulis
Model dan aset tiga dimensi | 3D Asset Designer & Database/Asset Manager | Menggunakan aset yang tersedia di dalam scene serta menyampaikan kebutuhan collision, target navigasi, dan optimasi runtime
Skema database, RLS, dan audit log | 3D Asset Designer & Database/Asset Manager | Menggunakan kontrak `unity_object_name` sebagai konsumen data
Dashboard React dan pencarian | Full Stack Developer & System Integrator | Menetapkan format perintah tujuan yang diterima Unity
Vercel Serverless Functions | Full Stack Developer & System Integrator | Mengonsumsi `/api/unity/data` dan `/api/unity/names`
Jembatan React–Unity | Full Stack Developer & System Integrator | Menyepakati kontrak method dan event; receiver Unity serta dispatch event pada runtime dikerjakan penulis, sedangkan bridge, pemanggil, dan listener React berada di luar kontribusi penulis
Navigasi, rendering rute, dan kontrol Unity | 3D Simulator & Engine Developer | Merancang, mengimplementasikan, dan menguji modul engine
Building Culling dan WebGL optimizer | 3D Simulator & Engine Developer | Merancang, mengimplementasikan, dan mengevaluasi optimasi
DatabaseSyncChecker | 3D Simulator & Engine Developer | Merancang, mengimplementasikan, dan menguji editor tool
Spawn, minimap, highlighter, dan tutorial Unity | 3D Simulator & Engine Developer | Merancang, mengimplementasikan, dan menyiapkan pengujian fitur orientasi
[/TABLE]

## 3.5 Hasil Pengujian Proyek

### 3.5.1 Black Box Testing

<!-- PIPELINE:INCLUDE content/shared/testing/blackbox.md -->

### 3.5.2 Pengujian Khusus Modul Unity

Pengujian khusus memisahkan perilaku modul engine dari alur sistem melalui dashboard. Hasil Black Box pada [TABREF:hasil_black_box] tetap menjadi bukti integrasi bersama, sedangkan format hasil setiap skenario khusus dirangkum pada [TABREF:hasil_pengujian_modul_unity]. Semua nilai aktual, status, dan bukti dipertahankan sebagai `[TBD: ...]` sampai artefak yang dapat diverifikasi tersedia.

[TABLE-ID:hasil_pengujian_modul_unity]
[TABLECAPTION:Hasil Pengujian Khusus Modul Unity]
[TABLE]
ID | Kondisi Awal | Langkah Pengujian | Hasil yang Diharapkan | Hasil Aktual | Status | Bukti
UT-01 | Scene uji aktif dan endpoint mengembalikan koleksi gedung serta fasilitas valid | Jalankan Play Mode dan tunggu proses pemuatan `BuildingDatabase` selesai | `isLoaded` aktif, cache terisi, dan nama tampilan dapat diambil | [TBD: hasil aktual] | [TBD: Lulus atau Gagal] | [TBD: fixture, log, dan screenshot]
UT-02 | Scene uji aktif dan sebuah nama tidak tersedia pada cache | Panggil `GetRealName()` menggunakan nama yang tidak dikenal | Method mengembalikan input asli dan tidak menghasilkan null | [TBD: hasil aktual] | [TBD: Lulus atau Gagal] | [TBD: log atau test runner]
UT-03 | Cache Transform memuat target yang valid | Panggil `NavigateTo()` menggunakan `unity_object_name` target | `NavigationReceiver` meneruskan Transform yang tepat ke `NavigationGuide` | [TBD: hasil aktual] | [TBD: Lulus atau Gagal] | [TBD: log dan rekaman Play Mode]
UT-04 | Target memiliki variasi kapitalisasi atau tidak tersedia pada cache awal | Panggil `NavigateTo()` dan amati fallback pencarian | Variasi kapitalisasi dikenali; target yang benar-benar hilang menghasilkan warning tanpa exception | [TBD: hasil aktual] | [TBD: Lulus atau Gagal] | [TBD: log dan fixture scene]
UT-05 | Pemain dan target valid berada pada area NavMesh | Mulai navigasi dan amati status jalur serta `LineRenderer` | Jalur valid dihitung, garis aktif, nama tujuan tampil, dan jarak diperbarui | [TBD: hasil aktual] | [TBD: Lulus atau Gagal] | [TBD: screenshot dan rekaman]
UT-06 | Navigasi aktif dan pemain berada di luar `stopDistance` | Gerakkan pemain hingga memasuki `stopDistance` | Navigasi berhenti serta garis dan label dibersihkan | [TBD: hasil aktual] | [TBD: Lulus atau Gagal] | [TBD: rekaman dan log]
UT-07 | Navigasi aktif menuju tujuan pertama | Panggil `StopNavigation()` atau pilih tujuan kedua | Rute lama dibersihkan dan state baru tidak menghasilkan garis ganda | [TBD: hasil aktual] | [TBD: Lulus atau Gagal] | [TBD: rekaman Play Mode]
UT-08 | Jalur uji memuat tikungan dan perubahan elevasi | Jalankan navigasi lalu bandingkan corners mentah dengan hasil renderer | Subdivisi linear memperapat titik, raycast menjaga garis mengikuti permukaan, dan moving average mengurangi perubahan titik yang tajam | [TBD: hasil aktual] | [TBD: Lulus atau Gagal] | [TBD: screenshot sebelum-sesudah]
UT-09 | Build dibuka pada browser desktop yang mendukung Pointer Lock | Klik canvas, gerakkan tetikus, lalu tekan ESC | Kursor terkunci setelah tindakan pengguna, kamera merespons delta, dan ESC melepaskan kursor | Tampilan desktop tanpa joystick dan navigasi aktif telah tersedia; respons Pointer Lock belum dibuktikan oleh screenshot diam | [TBD: menunggu rekaman] | `kontrol_desktop.png`; [TBD: perangkat, browser, dan rekaman]
UT-10 | Build yang sama dibuka pada perangkat mobile dan desktop | Gunakan joystick pada mobile lalu periksa tampilan desktop | Joystick mengendalikan pemain pada mobile dan tidak mengganggu tampilan desktop | UI desktop dan mobile tampil berbeda sesuai mode; respons gerak, sprint, dan lompat belum dibuktikan | [TBD: menunggu rekaman] | `kontrol_desktop.png`, `kontrol_mobile.png`; [TBD: identitas perangkat]
UT-11 | Scene, kamera, dan lintasan benchmark telah ditetapkan | Jalankan skenario yang sama sebelum dan sesudah Building Culling | Pada konfigurasi 200 m, renderer di luar ambang/frustum ditangani sesuai grace period, target navigasi tetap aktif, area minimap dipertahankan, dan metrik sebelum–sesudah dapat dibandingkan | Dua capture NVIDIA Statistics Overlay pada sudut gameplay yang hampir sama telah tersedia, tetapi tidak memuat Unity Profiler, draw call, renderer aktif, durasi sampling, identitas perangkat, atau indikator state aktif/nonaktif yang dapat diverifikasi | [TBD: belum dapat dinilai sebagai benchmark] | `statistik_runtime_culling_aktif.png` dan `statistik_runtime_culling_nonaktif.png`; [TBD: Unity Profiler]
UT-12 | Project menggunakan konfigurasi sebelum optimizer | Jalankan menu WebGL optimizer lalu periksa Player Settings | Brotli, decompression fallback, IL2CPP, stripping, WebAssembly 2023, dan exception support sesuai baseline proyek | Target Web aktif, SceneUtama terpilih, Brotli, fallback, caching, IL2CPP Master, optimasi ukuran, stripping High, WebAssembly 2023, dan `Explicitly Thrown Exceptions Only` terlihat | Lulus | Build Profile, Player Settings, dan log optimizer
UT-13 | Build produksi tersedia pada hosting yang ditetapkan | Muat build dan periksa Network serta Console browser | Build termuat tanpa error dan header kompresi serta MIME sesuai konfigurasi | [TBD: hasil aktual, ukuran, dan waktu muat] | [TBD: Lulus atau Gagal] | [TBD: DevTools, perangkat, browser, dan jaringan]
UT-14 | Fixture API dan scene memuat nama cocok, hilang, dan berlebih | Jalankan `DatabaseSyncChecker` lalu salin daftar ketidaksesuaian | Pencocokan dan nama yang hilang di scene memakai seluruh hierarki, kategori scene yang belum terdaftar memakai root object, dan daftar dapat disalin | Pemeriksaan aktual menampilkan 320 cocok, 3 tidak ada di scene, 14 root tidak ada di database, contoh nama, dan tombol salin | [TBD: fixture belum dicatat] | `hasil_database_sync_checker.png`; [TBD: fixture]
UT-15 | Endpoint mengembalikan data kosong, tidak valid, atau gagal | Jalankan pemeriksaan untuk setiap kondisi kegagalan | Tool menampilkan pesan yang jelas, tidak menganggap data tersinkronisasi, dan tidak mengubah scene | [TBD: hasil aktual] | [TBD: Lulus atau Gagal] | [TBD: log dan screenshot error]
UT-16 | Registry memuat titik spawn valid dan pemain berada pada scene utama | Panggil `SetSpawn()` menggunakan nama yang terdaftar | Pemain berpindah ke NavMesh di sekitar titik spawn sesuai radius dan override yang aktif | [TBD: hasil aktual] | [TBD: Lulus atau Gagal] | [TBD: log, screenshot posisi, dan rekaman]
UT-17 | Registry aktif dan nama spawn tidak terdaftar atau tidak memiliki posisi NavMesh valid | Panggil `SetSpawn()` menggunakan nama tidak valid lalu menggunakan titik yang gagal diproyeksikan | Sistem menampilkan warning, tidak menghasilkan exception, dan tidak memindahkan pemain ke posisi yang tidak valid | [TBD: hasil aktual] | [TBD: Lulus atau Gagal] | [TBD: log dan rekaman]
UT-18 | Minimap, marker pemain, marker tujuan, dan navigasi aktif telah dikonfigurasi | Gerakkan pemain dan ubah tujuan navigasi | Minimap mengikuti pemain, marker pemain bergerak, dan marker tujuan mengarah ke tujuan aktif | [TBD: hasil aktual] | [TBD: Lulus atau Gagal] | [TBD: screenshot dan rekaman]
UT-19 | Tujuan navigasi memiliki renderer yang dapat disorot | Mulai navigasi, ganti tujuan, lalu selesaikan atau hentikan navigasi | Highlighter aktif hanya pada tujuan saat ini dan dibersihkan ketika tujuan berubah atau navigasi berakhir | [TBD: hasil aktual] | [TBD: Lulus atau Gagal] | [TBD: screenshot dan rekaman]
UT-20 | Tutorial pertama kali aktif dan build dapat menerima mode perangkat | Panggil `SetDevice()` untuk desktop dan mobile lalu jalankan langkah tutorial yang setara | Instruksi dan visual kontrol mengikuti mode perangkat tanpa menampilkan kontrol yang tidak relevan | Pada langkah 2 dari 5, mode desktop menampilkan instruksi mouse dan mode mobile menampilkan instruksi geser area kamera beserta kontrol sentuh | Lulus dengan catatan | Screenshot tutorial desktop dan mobile; [TBD: log `SetDevice` dan rekaman]
UT-21 | Build WebGL telah dimuat dan bridge JavaScript dapat diamati | Panggil `WebPlatformSync.SetDevice()` dengan nilai valid serta nilai tak dikenal | Nilai valid menerapkan mode yang tepat; nilai tak dikenal ditangani tanpa exception dan menghasilkan fallback atau warning yang tercatat | [TBD: hasil aktual] | [TBD: Lulus atau Gagal] | [TBD: Console browser dan rekaman]
UT-22 | Navigasi aktif dan listener browser `OnNavigationCompleted` terpasang | Masuki `stopDistance`, lalu ulangi skenario penghentian manual atau pergantian tujuan | Unity mengirim event dengan payload tujuan tepat satu kali hanya saat tiba, sedangkan pembatalan manual tidak mengirim event selesai; state navigasi tetap dibersihkan | [TBD: hasil aktual dispatch event] | [TBD: Lulus atau Gagal] | [TBD: log Unity, Console browser, dan rekaman pembatalan]; tampilan notifikasi React di luar bukti kontribusi Faiz
UT-23 | Camera Frustum dan Occlusion Culling | Jalankan scene gameplay, putar kamera, buka selector spawn, lalu kembali ke gameplay | Renderer di luar jarak/frustum ditangani sesuai grace period, target navigasi tetap aktif, minimap tidak kehilangan area, dan status occlusion kamera berubah sesuai mode | Konfigurasi jarak/frustum, `OcclusionArea`, data bake, MainCamera aktif, dan MinimapCamera nonaktif telah terbukti; perubahan renderer saat runtime belum terbukti | [TBD: menunggu rekaman dan profiler] | Screenshot konfigurasi Building Culling dan occlusion; [TBD: log runtime]
UT-24 | Transisi Overview–Gameplay | Buka selector sebelum spawn, pilih spawn valid, lalu buka selector ulang | Fog overview bernilai 0, occlusion gameplay nonaktif saat selector, fog gameplay bernilai 0,01, dan occlusion gameplay pulih setelah spawn | [TBD: hasil aktual] | [TBD: Lulus atau Gagal] | [TBD: log runtime, Inspector, dan rekaman]
[/TABLE]

#### 3.5.2.1 Pengujian BuildingDatabase

Pengujian mencatat URL atau fixture tanpa membuka kredensial, kondisi awal cache, waktu mulai pemuatan, status `isLoaded`, jumlah entitas yang berhasil diproses, hasil `GetRealName()`, dan pesan ketika respons kosong atau tidak valid. Script, fixture, versi Unity, dan screenshot log menjadi bukti minimum untuk UT-01 dan UT-02.

#### 3.5.2.2 Pengujian NavigationReceiver

Pengujian menggunakan target pada cache, target yang hanya ditemukan setelah cache dibangun ulang, variasi kapitalisasi, objek tidak aktif, dan nama yang benar-benar tidak tersedia. Bukti UT-03 dan UT-04 harus menunjukkan nilai input, Transform hasil, jalur fallback yang terjadi, dan ketiadaan exception.

#### 3.5.2.3 Pengujian NavigationGuide dan Rendering Rute

Pengujian menggunakan posisi awal serta tujuan yang dicatat, NavMesh yang sama, dan konfigurasi renderer yang sama. UT-05 sampai UT-08 memeriksa status jalur, jumlah titik, label, jarak, penghentian otomatis, penghentian manual, pergantian tujuan, tikungan, serta perubahan elevasi. Screenshot sebelum-sesudah dan rekaman Play Mode digunakan untuk menunjukkan perbedaan corners mentah dengan rute akhir.

#### 3.5.2.4 Pengujian Pointer Lock dan Joystick

Pengujian UT-09 dan UT-10 mencatat perangkat, sistem operasi, browser, resolusi, dan metode input. Pointer Lock diuji setelah klik pengguna dan dilepas dengan ESC, sedangkan joystick diuji pada perangkat sentuh serta dibandingkan dengan tampilan desktop. Screenshot tunggal tidak cukup untuk membuktikan respons input sehingga rekaman singkat atau log aksi turut dilampirkan.

#### 3.5.2.5 Pengujian Building Culling

Pengujian UT-11 menggunakan build, scene, posisi awal, jalur kamera, durasi, dan perangkat yang sama. Metrik minimum adalah renderer aktif, draw call, frame time, frame rate, dan memori. Nilai sebelum dan sesudah disajikan bersama konfigurasi jarak serta interval culling. Karena batas minimum dan maksimum pada scene final sama-sama 200 m, pengujian ini hanya membuktikan perilaku ambang tetap 200 m dan tidak digunakan untuk mengklaim adaptasi jarak dinamis. Pengujian juga memverifikasi camera-frustum culling dengan pemeriksaan setiap 0,1 detik, padding 10 m, grace period 0,35 detik, pengecualian target navigasi, serta pemeliharaan renderer yang diperlukan oleh minimap.

#### 3.5.2.6 Pengujian Konfigurasi dan Deployment WebGL

Pengujian UT-12 memeriksa perubahan Player Settings yang diterapkan optimizer. Pengujian UT-13 mencatat versi Unity, ukuran berkas, waktu sampai aplikasi dapat digunakan, perangkat, browser, koneksi, `Content-Encoding`, `Content-Type`, dan pesan Console. Requirement kurang dari 10 detik tidak dinyatakan tercapai sebelum hasil aktual tersedia.

#### 3.5.2.7 Pengujian DatabaseSyncChecker

Pengujian UT-14 dan UT-15 menggunakan fixture terkendali agar hasil tiga kategori dapat dibandingkan dengan data acuan. Verifikasi kategori cocok dan hilang di scene mencakup seluruh hierarki secara rekursif, sedangkan kategori objek scene yang belum terdaftar hanya dibandingkan terhadap root object sesuai batas implementasi. Skenario kegagalan membedakan respons kosong, format tidak valid, dan kegagalan jaringan. Bukti harus menunjukkan bahwa tool memberikan diagnosis tanpa mengubah scene atau menampilkan kondisi kosong sebagai sinkronisasi berhasil.

#### 3.5.2.8 Pengujian Spawn dan Minimap

Pengujian UT-16 sampai UT-18 mencatat nama spawn, posisi sebelum dan sesudah perpindahan, radius pencarian NavMesh, override lokasi, serta perubahan marker selama pemain bergerak. Skenario positif dan negatif dijalankan pada scene serta commit yang sama. Rekaman digunakan untuk membuktikan perpindahan pemain dan pergerakan marker, sedangkan screenshot Inspector mendokumentasikan konfigurasi registry yang diuji.

#### 3.5.2.9 Pengujian Highlighter, Tutorial, Device Sync, dan Penyelesaian Navigasi

Pengujian UT-19 sampai UT-22 mencatat tujuan aktif, perubahan material atau renderer yang disorot, mode perangkat, langkah tutorial, serta event browser yang diterima. Tutorial desktop dan mobile diuji pada langkah yang setara. Penyelesaian otomatis dan penghentian manual diuji terpisah agar payload tujuan, jumlah pengiriman, pembersihan state, serta respons listener dapat diverifikasi tanpa mengklaim implementasi listener React sebagai kontribusi penulis.

#### 3.5.2.10 Pengujian Camera Frustum dan Occlusion Culling

Pengujian UT-23 mencatat status renderer sebelum dan sesudah kamera diputar, status target navigasi, visibilitas area minimap, interval pemeriksaan 0,1 detik, padding 10 m, grace period 0,35 detik, dan perubahan status occlusion kamera. Hasil profiler dan jumlah renderer aktif tetap `[TBD]` sampai kondisi benchmark disamakan.

#### 3.5.2.11 Pengujian Transisi Overview–Gameplay

Pengujian UT-24 memeriksa selector sebelum spawn, pemilihan spawn valid, pembukaan selector ulang, status `useOcclusionCulling`, nilai fog, dan pemulihan kontrol. Bukti wajib berupa log runtime atau assertion Play Mode serta rekaman transisi; screenshot konfigurasi saja tidak cukup untuk membuktikan perubahan state.

### 3.5.3 User Acceptance Test

<!-- PIPELINE:INCLUDE content/shared/testing/uat.md -->

### 3.5.4 Implementasi Hasil User Acceptance Test

<!-- PIPELINE:INCLUDE content/shared/testing/uat-revisions.md -->

### 3.5.5 Analisis Kontribusi Faiz terhadap Tindak Lanjut UAT

Temuan UAT merupakan backlog produk bersama, sedangkan penjelasan kontribusi pada [TABREF:kontribusi_faiz_uat] dibatasi pada komponen engine. Tabel ini tidak mengubah status verifikasi bersama dan tidak menyatakan suatu perbaikan selesai sebelum bukti serta retest tersedia.

[TABLE-ID:kontribusi_faiz_uat]
[TABLECAPTION:Pemetaan Kontribusi Engine terhadap Tindak Lanjut UAT]
[TABLE]
ID Temuan | Kaitan dengan Engine | Kandidat Kontribusi Penulis | Bukti Peran
UAT-R02 | Pengguna memerlukan petunjuk penggunaan yang mudah ditemukan | Menyediakan tutorial runtime yang menyesuaikan instruksi desktop atau mobile sebagai pelengkap bantuan pada dashboard | Screenshot tutorial desktop dan mobile tersedia; [TBD: build terintegrasi dan retest]
UAT-R04 | Pengguna perlu mengenali nama ruang atau fasilitas di lingkungan 3D | Menggunakan `realNames` untuk label tujuan, menjaga fallback nama tampilan, dan menyorot tujuan aktif | [TBD: screenshot label dan highlighter, audit cakupan, dan retest]
UAT-R05 | Pengguna memerlukan onboarding yang mudah dipahami | Menyediakan urutan tutorial dan visual kontrol yang mengikuti mode perangkat dari `SetDevice()` | Langkah `Lihat Sekeliling` telah dibuktikan pada dua mode; [TBD: skenario pengguna, log `SetDevice`, dan retest]
UAT-R06 | Pengguna perlu mengetahui posisi saat ini | Menyediakan minimap yang mengikuti pemain serta marker pemain dan tujuan aktif | [TBD: screenshot runtime, rekaman pergerakan marker, dan retest]
UAT-R07 | Pengguna memerlukan pilihan mode dan titik awal | Mendukung pemilihan serta validasi spawn pada NavMesh dan kontrak `SpawnReceiver.SetSpawn()` | [TBD: screenshot pemilihan spawn, log validasi, dan retest]
UAT-R10 | Pengguna memerlukan konfirmasi ketika mencapai tujuan | Mengirim event browser `OnNavigationCompleted` setelah state navigasi selesai; implementasi dan screenshot notifikasi React tidak menjadi bukti kontribusi Faiz | [TBD: log dispatch event Unity, build yang sama, dan retest pembatalan manual]
[/TABLE]

Temuan UAT-R03 dan UAT-R08 melibatkan komponen di luar engine, sedangkan UAT-R01 serta UAT-R09 terutama berkaitan dengan konsistensi database, API, pencarian, dan aset. Penulis tidak mengklaim implementasi bagian tersebut sebagai kontribusi personal. Status produk tetap mengikuti fragment bersama pada Subbab 3.5.4 berdasarkan audit kode, pengujian, sumber resmi, dan bukti deployment yang dicantumkan di sana. Sementara itu, penanda `[TBD]` pada [TABREF:kontribusi_faiz_uat] hanya menunjukkan bukti reproduksi khusus modul Unity yang masih perlu dilengkapi dan tidak membatalkan status hasil integrasi tim.

---

# BAB IV PENUTUP

## 4.1 Kesimpulan

Berdasarkan perancangan, implementasi, dan pengujian yang terdokumentasi, kesimpulan laporan ini adalah sebagai berikut:

1. Kontribusi penulis sebagai 3D Simulator & Engine Developer menghasilkan susunan modul yang memisahkan konsumsi data, penerimaan perintah tujuan, pencarian Transform, perhitungan NavMesh, rendering rute, kontrol pengguna, optimasi renderer, konfigurasi build, pemeriksaan sinkronisasi, pemilihan spawn, minimap, penanda tujuan, dan tutorial adaptif.
2. Alur integrasi menggunakan `unity_object_name` sebagai penghubung teknis antara data gedung atau fasilitas dan GameObject di dalam scene. Unity mengonsumsi `GET /api/unity/data` untuk data runtime dan `GET /api/unity/names` untuk editor tool, menerima `NavigateTo()`, `StopNavigation()`, `SetSpawn()`, serta `SetDevice()`, kemudian mengekspos event browser `OnNavigationCompleted` hanya ketika path lengkap dan ambang kedatangan efektif maksimal 2 m terpenuhi, dengan payload tujuan. Pembatalan manual tidak mengirim event kedatangan; implementasi pemanggil dan listener React berada di luar kontribusi penulis.
3. Navigasi final menggunakan `NavMesh.SamplePosition`, validasi perpindahan lantai, `NavMesh.CalculatePath`, subdivisi linear dengan jarak titik 0,4 m, `RaycastNonAlloc`, moving average berjendela empat titik, dan `LineRenderer` berlebar 0,2 m dengan offset 0,6 m. Jalur diperbarui setelah perpindahan 1 m. Walaupun Inspector menyimpan `stopDistance` 5 m, ambang kedatangan runtime dibatasi maksimal 2 m serta mensyaratkan path lengkap dan kedekatan terhadap endpoint NavMesh. Hasil aktual dedicated tetap mengikuti matriks pengujian dan bukti yang tersedia.
4. Kontrol karakter dan kamera third-person menggunakan Pointer Lock pada desktop serta joystick virtual pada perangkat bergerak. Tutorial langkah `Lihat Sekeliling` telah menunjukkan instruksi mouse pada desktop dan gestur area kamera pada mobile. Bukti dinamis `WebPlatformSync.SetDevice()`, respons input, dan penerimaan pengguna tetap `[TBD]` sampai log, rekaman, serta retest build terintegrasi tersedia.
5. Building Culling, camera-frustum culling, occlusion culling, dan WebGL optimizer telah menjadi bagian dari implementasi engine. Batas minimum dan maksimum culling jarak pada scene final sama-sama 200 m sehingga mode `Combined` bekerja dengan jarak efektif tetap, bukan adaptif. Capture NVIDIA Statistics Overlay telah tersedia sebagai bukti runtime pendahuluan, tetapi dampak kuantitatif belum boleh disimpulkan sebelum Unity Profiler, ukuran build, waktu muat, frame time, draw call, renderer aktif, durasi, dan identitas perangkat dilengkapi pada kondisi uji yang terkendali.
6. `DatabaseSyncChecker` menyediakan mekanisme pencegahan untuk menemukan ketidaksesuaian `unity_object_name` sebelum build. Pencarian padanan API menjangkau hierarki secara rekursif, tetapi kategori objek scene yang belum terdaftar hanya memeriksa root object. Pemeriksaan aktual yang terdokumentasi menampilkan 320 nama cocok, 3 nama yang tidak ditemukan di scene, dan 14 objek root yang belum terdaftar; fixture terkendali dan pengujian kondisi API kosong atau gagal masih `[TBD]`.
7. Spawn tervalidasi NavMesh, radius override, minimap, destination highlighter, serta tutorial desktop/mobile telah memiliki bukti visual pada implementasi final. Transisi overview–gameplay dan event selesai navigasi tersedia pada kode, tetapi keterkaitannya dengan UAT-R02, UAT-R05, UAT-R06, UAT-R07, dan UAT-R10 belum dinyatakan selesai sampai log event, rekaman interaksi, build yang sama, serta retest tersedia. Tampilan notifikasi React dikecualikan dari bukti karena berada di luar kontribusi penulis.

## 4.2 Saran

Saran pengembangan lebih lanjut adalah sebagai berikut:

1. Melengkapi automated Play Mode Test dan Edit Mode Test untuk `BuildingDatabase`, `NavigationReceiver`, `NavigationGuide`, Building Culling, `DatabaseSyncChecker`, spawn, minimap, highlighter, tutorial, sinkronisasi perangkat, dan event selesai navigasi agar regresi dapat dideteksi sebelum build WebGL dibuat.
2. Menetapkan prosedur benchmark yang merekam perangkat, versi peramban, jenis koneksi, ukuran build, waktu muat, frame time, draw call, penggunaan memori, dan jumlah renderer aktif agar dampak optimasi dapat dibandingkan secara adil.
3. Melakukan retest minimap dan marker tujuan untuk menilai keterbacaan, skala, orientasi, dan kegunaannya sebagai tindak lanjut UAT-R06 sebelum menentukan penyempurnaan visual berikutnya.
4. Membedakan penyelesaian karena mencapai `stopDistance` dari penghentian manual pada payload atau state event, lalu memverifikasi melalui log bahwa `OnNavigationCompleted` hanya dikirim pada kondisi kedatangan. Tampilan notifikasi pada React tetap menjadi tanggung jawab integrator web.
5. Menyempurnakan deteksi kapabilitas perangkat agar joystick virtual hanya muncul ketika relevan dan Pointer Lock memiliki fallback yang jelas pada peramban yang tidak mendukungnya secara penuh.
6. Menjaga sinkronisasi `unity_object_name` melalui pemeriksaan otomatis pada pipeline build serta memperluas pemeriksaan objek scene yang belum terdaftar dari root object ke hierarki yang relevan, sehingga build dapat ditahan ketika terdapat target database yang tidak memiliki padanan di scene.
7. Mengembangkan strategi pemuatan aset secara bertahap apabila hasil profiler menunjukkan bahwa ukuran atau inisialisasi aset menjadi hambatan utama sambil mempertahankan kontrak endpoint, method penerima Unity, dan event browser yang telah didokumentasikan.

---

# DAFTAR PUSTAKA


Aliyah, A., Hartono, N., dan Muin, A. A. (2025). Penggunaan User Acceptance Testing (UAT) pada pengujian sistem informasi pengelolaan keuangan dan inventaris barang. *Switch: Jurnal Sains dan Teknologi Informasi*, 3(2), 42–58. https://doi.org/10.62951/switch.v3i1.330

Jamaludin, J., dan Saepuloh, L. (2024). Tren riset twin digital smart campus. *Sang Pencerah: Jurnal Ilmiah Universitas Muhammadiyah Buton*, 10(2), 408–425. https://doi.org/10.35326/pencerah.v10i2.5317

Kurniawan, T. A. (2018). Pemodelan Use Case (UML): Evaluasi terhadap beberapa kesalahan dalam praktik. *Jurnal Teknologi Informasi dan Ilmu Komputer*, 5(1), 77–86. https://doi.org/10.25126/jtiik.201851610

Maulida, M., Zahro, F., Hakim, R., & Akbar, M. S. (2025). Pengujian black box testing pada sistem website pemesanan online Toko Ayam Krispy. *Jurnal Media Akademik*, 3(5). https://doi.org/10.62281/v3i5.1908

MDN Web Docs, M. (2025). *Pointer Lock API*. https://developer.mozilla.org/en-US/docs/Web/API/Pointer_Lock_API

Muharam, Y., Anggara, M. B., & Hanafi, T. J. (2023). Implementasi peta 3 dimensi menggunakan metode IMSDD (Interactive Multimedia System Design and Development) dan WebGL API berbasis web (Studi kasus di SMP Karya Pembangunan 2 Majalaya). *Jurnal Informatika-COMPUTING*, 10, 20–30. https://doi.org/10.55222/computing.v10i01.1155

Pricillia, T., & Zulfachmi. (2021). Perbandingan metode pengembangan perangkat lunak (Waterfall, Prototype, RAD). *Jurnal Bangkit Indonesia*, 10(1), 6–12. https://doi.org/10.52771/bangkitindonesia.v10i1.153

Taurusta, C., Asiddiq, A. M., Suprianto, S., & Setiawan, H. (2024). Visualisasi gedung kampus 1 Universitas Muhammadiyah Sidoarjo menggunakan augmented reality sebagai media informasi. *Journal of Technology and System Information*, 1(1), 55–70. https://doi.org/10.47134/jtsi.v1i1.2146

UPNVJ. (2022). Lokasi kampus. https://www.upnvj.ac.id/id/tentang-upn/lokasi-kampus.html

UPNVJ. (2025a). Kantin. https://www.upnvj.ac.id/id/fasilitas-layanan/kantin.html

UPNVJ. (2026a). Hubungi kami. *Penerimaan Mahasiswa Baru UPN Veteran Jakarta*. https://penmaru.upnvj.ac.id/id/contact.html

Unity Technologies, U. (2026). *AI Navigation: Unity 6.0 Manual*. https://docs.unity3d.com/6000.0/Documentation/Manual/com.unity.ai.navigation.html

Unity Technologies, U. (2026). *Deploy a web application: Unity 6.0 Manual*. https://docs.unity3d.com/6000.0/Documentation/Manual/webgl-deploying.html

Unity Technologies, U. (2026). *Input System: Unity 6.0 Manual*. https://docs.unity3d.com/6000.0/Documentation/Manual/com.unity.inputsystem.html

---

# LAMPIRAN 1. Identitas dan Pernyataan Keaslian

Nama: Muammar Faiz Khairul Anam

NIM: 2210511138

Judul: Pengembangan Sistem Navigasi Spasial dan Optimasi Engine Unity WebGL pada Denah Virtual UPNVJ Kampus Pondok Labu

[TBD: masukkan naskah pernyataan keaslian dan halaman tanda tangan sesuai template resmi kampus]

---

# LAMPIRAN 2. Bukti Implementasi Modul Unity

Bukti implementasi pada bagian ini menggunakan project final `C:\Users\Faiz\Proposal\T_A---Copy` pada commit `5f575c0`, Unity 6000.4.1f1, dan scene `Assets/Scene/SceneUtama.unity`. Project `C:\Users\Faiz\Proposal` hanya menjadi baseline historis Unity 6000.2.6f1 dan tidak digunakan untuk membuktikan konfigurasi atau hasil final. Apabila project Unity berubah setelah commit tersebut, commit acuan dan seluruh bukti yang terdampak harus diperbarui agar kode, scene, build, dan laporan berasal dari versi yang sama.

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
Belum tersedia | Unity Profiler, log dispatch `OnNavigationCompleted`, dan rekaman interaksi | Tetap `[TBD]` | Notifikasi React sengaja tidak dimasukkan karena bukan kontribusi Faiz
[/TABLE]

Aturan pengambilan bukti adalah sebagai berikut:

1. Gunakan project final, scene, commit, build, dan data yang sama untuk bukti hasil. Satu gambar baseline bersifat opsional dan hanya ditempatkan pada lampiran sebagai penjelas perkembangan.
2. Sertakan rekaman 15–30 detik untuk Pointer Lock, joystick, perpindahan marker, Building Culling, dan event selesai karena screenshot diam tidak membuktikan interaksi.
3. Catat perangkat, sistem operasi, browser, resolusi, commit, scene, durasi, dan metode ukur pada bukti performa. Angka sebelum dan sesudah hanya dibandingkan apabila seluruh kondisi tersebut sama.
4. Sembunyikan token, cookie, kredensial, dan data sensitif lain sebelum mengambil DevTools Network atau Console.
5. Gunakan screenshot top-down lama di `Assets/Screenshots` hanya sebagai sumber tambahan minimap, bukan pengganti tampilan minimap saat runtime.
6. Simpan Console log, Profiler capture, dan HAR atau Network log bersama screenshot agar hasil aktual dapat ditelusuri.

Script kontribusi yang diarsipkan sebagai bukti adalah `BuildingDatabase.cs`, `NavigationReceiver.cs`, `NavigationGuide.cs`, `BuildingCulling.cs`, `WebGLOptimizer.cs`, `DatabaseSyncChecker.cs`, `CampusOcclusionInstaller.cs`, `SpawnPointRegistry.cs`, `SpawnSelectionUI.cs`, `SpawnMinimapSceneInstaller.cs`, `MinimapFollow.cs`, `DayNightCycle.cs`, `DestinationHighlighter.cs`, `NavigationDestinationVisual.cs`, `GameTutorialController.cs`, `GameTutorialUI.cs`, `WebPlatformSync.cs`, `TestNavigation.cs`, dan `ReactBridge.jslib`. Artefak konfigurasi yang menyertai bukti adalah `SceneUtama.unity`, `ProjectVersion.txt`, `NavMeshAreas.asset`, `OcclusionCullingData.asset`, `EditorBuildSettings.asset`, `Packages/manifest.json`, output build final, Console log, Profiler capture, serta HAR atau Network log. [TBD: arsip script, artefak konfigurasi, rekaman interaksi, log dispatch event, dan log final]

---

# LAMPIRAN 3. Bukti Pengujian dan Benchmark

Bukti pengujian pada bagian ini perlu memuat konfigurasi perangkat, versi Unity, versi peramban, kondisi jaringan, fixture data, hasil Play Mode Test, hasil Edit Mode Test, Unity Profiler, DevTools Network, perbandingan build, dan bukti retest. [TBD: artefak pengujian final]

---

# LAMPIRAN 4. Instrumen UAT dan Indeks Bukti Pengujian

Instrumen pada lampiran ini merupakan bukti pengujian produk bersama. Pencantumannya tidak mengubah batas kontribusi penulis pada runtime dan tooling Unity.

<!-- PIPELINE:INCLUDE content/shared/testing/appendix-instruments.md -->
