# PERANCANGAN ASSET 3D DAN PENGELOLAAN DATABASE
# PADA SISTEM DENAH VIRTUAL UPNVJ KAMPUS PONDOK LABU

Dwikhi Deandra Purnianto
2210511131

INFORMATIKA
FAKULTAS ILMU KOMPUTER
UNIVERSITAS PEMBANGUNAN NASIONAL VETERAN JAKARTA
2026

# SURAT PERNYATAAN KEASLIAN

Yang bertanda tangan di bawah ini:

Nama: Dwikhi Deandra Purnianto

NIM: 2210511131

Program Studi: S-1 Informatika

Judul Proyek: “Perancangan *Asset* 3D dan Pengelolaan *Database* pada Sistem Denah Virtual UPNVJ Kampus Pondok Labu”

Menyatakan bahwa laporan tugas akhir proyek ini disusun oleh penulis berdasarkan hasil pekerjaan, pemikiran, dan pengembangan dalam lingkup kontribusi penulis sebagaimana dijelaskan di dalam laporan. Bagian yang merupakan hasil kolaborasi tim, kutipan, data, gambar, atau informasi dari pihak lain telah dinyatakan dan dirujuk dengan benar.

Demikian surat pernyataan ini dibuat dengan sebenar-benarnya. Apabila kemudian ditemukan penyimpangan atau ketidaksesuaian dalam pernyataan ini, penulis bersedia menerima konsekuensi dan diproses sesuai dengan aturan serta ketentuan yang berlaku.

Jakarta, [tanggal, bulan, tahun]

Yang menyatakan,

[Meterai dan tanda tangan]

Dwikhi Deandra Purnianto

# PERNYATAAN MENGENAI SKRIPSI DAN SUMBER INFORMASI SERTA PELIMPAHAN HAK CIPTA

Dengan ini saya menyatakan bahwa skripsi dengan judul “Perancangan *Asset* 3D dan Pengelolaan *Database* pada Sistem Denah Virtual UPNVJ Kampus Pondok Labu” adalah karya saya dengan arahan dari dosen pembimbing dan belum diajukan dalam bentuk apa pun kepada perguruan tinggi mana pun. Sumber informasi yang berasal atau dikutip dari karya yang diterbitkan maupun tidak diterbitkan dari penulis lain telah disebutkan dalam teks dan dicantumkan dalam Daftar Pustaka di bagian akhir skripsi ini.

Dengan ini saya melimpahkan hak cipta dari karya tulis saya kepada Universitas Pembangunan Nasional “Veteran” Jakarta.

Jakarta, 23 Juli 2026

Dwikhi Deandra Purnianto 2210511131

# ABSTRAK

Kuesioner awal menunjukkan bahwa 14 dari 21 responden pernah mengalami kesulitan menemukan lokasi di Kampus UPNVJ Pondok Labu. Tugas akhir ini bertujuan merancang hubungan data melalui *Entity Relationship Diagram* (ERD), mengelola data awal, membuat serta menata *asset* 3D gedung dan fasilitas, dan menerapkan kode lokasi yang sama pada *database* serta objek tujuan di *Unity*. Pengerjaan menggunakan metode *prototyping* melalui pengumpulan kebutuhan, pembuatan rancangan awal, pemeriksaan, dan perbaikan berulang. Proses dimulai dengan merancang ERD dan kebutuhan kebijakan akses data, kemudian menerjemahkannya menjadi struktur *database* serta data awal. Gedung Dewi Sartika digunakan sebagai contoh untuk memperlihatkan urutan pengisian data, pembuatan visual dari foto referensi, penyusunan *prefab*, pembuatan `Pointer`, dan penyamaan kode lokasi. Referensi visual diperoleh dengan mendatangi gedung dan mengambil foto tanpa pengukuran dimensi menggunakan alat ukur. Bentuk bangunan dibuat pada *Unity Editor*, sedangkan sebagian objek pendukung dibuat pada *Blender*. Hasilnya meliputi 19 *asset* gedung dan satu *asset* fasilitas Masjid, ERD untuk data gedung, fasilitas, fakultas, dan program studi, serta data awal berisi 19 entitas gedung dan 311 fasilitas. Kode lokasi `unity_object_name` diterapkan pada data dan objek tujuan, sedangkan alat milik pengembang *engine* digunakan untuk menelusuri nama yang perlu diperiksa. Pada tingkat produk bersama, pengujian fungsional akhir menghasilkan 24 dari 24 skenario lulus dan UAT memperoleh nilai gabungan 81,50 persen. Hasil tersebut menunjukkan bahwa kontribusi penulis menyediakan dasar visual dan data bagi denah virtual, dengan pembaruan informasi lapangan serta pemeriksaan pemetaan tetap diperlukan ketika data berubah.

Kata kunci: *asset* 3D, *database*, ERD, *Unity*, denah virtual.

# ABSTRACT

The questionnaire showed that 14 of 21 respondents had difficulty finding locations on the UPNVJ Pondok Labu Campus. This project aimed to design data relationships through an Entity Relationship Diagram (ERD), manage initial data, create and arrange 3D assets for buildings and facilities, and apply the same location code to database records and destination objects in Unity. The work used a prototyping method involving requirements collection, initial design, inspection, and iterative improvement. The process began with the ERD and data-access policy requirements, followed by the database structure and initial data. Dewi Sartika Building was used as an example to show the sequence of entering data, creating a visual model from a reference photograph, arranging the prefab, creating the `Pointer`, and matching the location code. Visual references were collected by visiting buildings and taking photographs without instrument-based dimension measurements. Building forms were created in the Unity Editor, while several supporting objects were created in Blender. The results comprised 19 building assets and one Masjid facility asset, an ERD for buildings, facilities, faculties, and study programs, and initial data containing 19 building entities and 311 facilities. The `unity_object_name` location code was applied to the data and destination objects, while a tool developed by the engine developer was used to identify names requiring review. At the shared-product level, the functional test passed 24 of 24 scenarios, and the combined UAT score was 81.50 percent. These results show that the author's contribution provides the visual and data foundation for the virtual map, while field updates and mapping checks remain necessary whenever the data change.

Keywords: 3D asset, database, ERD, Unity, virtual map.

# KATA PENGANTAR

Puji syukur kehadirat Tuhan Yang Maha Esa atas rahmat dan karunia-Nya sehingga penulis dapat menyelesaikan laporan tugas akhir yang berjudul “Perancangan *Asset* 3D dan Pengelolaan *Database* pada Sistem Denah Virtual UPNVJ Kampus Pondok Labu”.

Penyusunan proyek dan laporan ini tidak lepas dari doa, dukungan, arahan, serta bantuan dari berbagai pihak sejak tahap perencanaan hingga penyelesaian. Oleh karena itu, penulis menyampaikan rasa terima kasih dan penghargaan yang setinggi-tingginya kepada:

1. Keluarga penulis, yang selalu memberikan doa, dukungan moril, semangat, dan perhatian penuh selama pelaksanaan tugas akhir.

2. Erly Krisnanik, S.Kom., M.M., yang senantiasa memberikan dukungan dan dorongan moral kepada penulis selama proses pengerjaan tugas akhir.

3. Dr. Ridwan Raafi’udin, S.Kom., M.Kom. dan Novi Trisman Hadi, S.Pd., M.Kom., selaku Dosen Pembimbing yang telah meluangkan waktu, memberikan arahan, masukan, serta bimbingan yang sangat berharga dalam pengerjaan proyek dan penyusunan laporan ini.

4. Mochamad Fariz Satyawan, S.Kom., selaku Staf Program Studi yang telah membantu dan memfasilitasi kelancaran proses hingga pelaksanaan sidang.

5. Reyhan Mahendra, S.I.Kom., selaku Pengelola Majalah & Desain Humas Biro AKK UPN Veteran Jakarta, yang telah memberikan kemudahan serta bantuan teknis selama pengerjaan proyek ini.

6. Muamar Faiz Khairul Anam Setiawan dan Muhammad Iman Nugraha, selaku rekan satu tim yang telah bekerja sama dengan baik melalui diskusi, pembagian tugas, dan pengembangan setiap komponen pada sistem denah virtual.

7. Rekan-rekan *Discord* NYPD dan Dimari Aje Cuyy, khususnya mtgim, Semua Baik, whychucksaysnah, serta marqui de natra666, yang telah memberikan hiburan dan dukungan semangat selama proses pengerjaan.

8. *Podcast Seminggu*, Bang Awwe, dan Abah Pican yang menjadi sumber hiburan dan menemani penulis selama penyusunan proyek dan laporan ini.

9. Diri sendiri, yang telah berjuang, bertahan, dan konsisten belajar hingga mampu menyelesaikan tugas akhir ini dengan baik.

Penulis menyadari bahwa laporan ini masih memiliki kekurangan. Oleh karena itu, kritik dan saran yang membangun sangat diharapkan demi penyempurnaan karya ini. Semoga proyek dan laporan tugas akhir ini dapat memberikan manfaat serta panduan berguna bagi pengembangan sistem denah virtual kampus di masa mendatang.

Jakarta, 23 Juli 2026

Dwikhi Deandra Purnianto

2210511131

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

---

# BAB I PENDAHULUAN

## 1.1 Latar Belakang

<!-- PIPELINE:INCLUDE content/shared/bab1/latar-belakang-umum.md -->

Visualisasi lingkungan kampus dalam bentuk tiga dimensi dapat membantu penyajian hubungan spasial secara lebih interaktif dibandingkan denah statis. Penelitian terdahulu menunjukkan bahwa visualisasi gedung berbasis teknologi tiga dimensi dan WebGL dapat digunakan sebagai media informasi lokasi, sedangkan kajian mengenai *digital twin smart campus* menempatkan representasi digital lingkungan kampus sebagai bagian dari transformasi layanan pendidikan tinggi (Jamaludin et al. 2024; Muharam et al. 2023; Taurusta et al. 2024). Dalam proyek ini, manfaat visualisasi tersebut bergantung pada dua fondasi yang saling terkait, yaitu asset 3D yang merepresentasikan lingkungan fisik kampus dan struktur data yang menyimpan identitas gedung serta fasilitas secara konsisten.

Dalam *Unity*, *scene* merupakan ruang kerja yang memuat lingkungan aplikasi, sedangkan *GameObject* merupakan unit objek yang dapat diberi komponen dan disusun dalam hubungan induk-anak. *Prefab* adalah templat *GameObject* beserta komponen dan susunan *child*-nya yang dapat digunakan kembali, sehingga hierarki dan konvensi penamaan menjadi bagian penting dalam pemeliharaan objek (Unity Technologies 2026a). *Asset* 3D yang tidak mengikuti struktur seragam akan menyulitkan proses integrasi dengan logika navigasi. Pada sisi lain, data gedung dan fasilitas yang tidak memiliki relasi, identitas integrasi, serta aturan akses yang jelas berisiko menimbulkan ketidaksesuaian antara informasi pada *dashboard* dan objek pada *scene* *Unity*. Oleh karena itu, perancangan *asset* 3D perlu dilakukan bersama perancangan skema *database*, khususnya melalui atribut `unity_object_name` sebagai penghubung antara baris data dan *GameObject* di *Unity*.

Pengelolaan data proyek juga membutuhkan pembatasan akses pada tingkat *database*. *Row Level Security* (RLS) adalah mekanisme yang membatasi baris data yang boleh dibaca atau diubah berdasarkan peran pengguna. Pada tingkat rancangan, penulis menetapkan kebijakan RLS untuk membedakan akses baca publik dan perubahan terautentikasi. *Audit log* adalah catatan berurutan mengenai tindakan perubahan data agar pelaku, jenis perubahan, dan waktu kejadian dapat ditelusuri (Putra et al. 2026). Penulis merancang skema akhir 11 tabel, termasuk tabel `audit_logs`, sedangkan autentikasi dan penulisan catatan melalui layanan aplikasi berada pada kontribusi *Full Stack Web Developer*, *System Integrator*, dan *DevOps Engineer*. Berkas SQL tidak memuat definisi *trigger* audit sehingga laporan tidak mengklaim *trigger* tersebut aktif. Laporan ini berfokus pada pembuatan dan penataan seluruh *asset* 3D gedung dan fasilitas yang memiliki *GameObject* pada *scene* *Unity*, penyusunan *prefab* serta *child* `Pointer`, perancangan skema melalui *Entity Relationship Diagram* (ERD), yaitu diagram yang menggambarkan entitas dan hubungannya, pengelolaan data gedung atau fasilitas, serta penjagaan konsistensi `unity_object_name` pada *asset* dan data.

Kuesioner proyek memberi sumber langsung bagi kebutuhan tersebut. Sebanyak 14 dari 21 responden pernah mengalami kesulitan menemukan lokasi sedikitnya satu kali dalam satu semester, 76,2 persen menilai peta virtual 3D yang terhubung dengan informasi fasilitas sebagai kebutuhan penting, dan nama gedung menjadi informasi yang paling banyak dipilih. Hasil ini tidak mewakili seluruh sivitas akademika, tetapi menunjukkan bahwa sampel pengguna membutuhkan bantuan pencarian lokasi yang menghubungkan bentuk bangunan dengan informasi tujuannya.

Observasi visual dan inventarisasi data dilakukan penulis secara mandiri dengan mendatangi gedung satu per satu. Foto dapat menunjukkan bentuk bangunan, tetapi informasi nama dan fungsi ruang bergantung pada keterangan yang tersedia ketika pengamatan dilakukan. Kondisi tersebut menimbulkan kebutuhan untuk memisahkan nama yang dibaca pengguna dari kode lokasi yang dipakai sistem, menyusun hubungan data agar dapat diperbarui, serta memeriksa apakah setiap informasi tujuan menunjuk ke objek tiga dimensi yang benar. Berdasarkan sumber pada Latar Belakang ini, fokus masalah penulis dikelompokkan menjadi ketersediaan representasi 3D, keteraturan data lokasi, dan hubungan antara data dengan objek pada denah virtual.

## 1.2 Identifikasi Masalah

Berdasarkan kuesioner, observasi lapangan, dan kebutuhan integrasi yang telah dijelaskan pada Latar Belakang, masalah dalam lingkup penulis diidentifikasi sebagai berikut:

1. Sampel pengguna masih mengalami kesulitan menemukan lokasi, sedangkan denah virtual memerlukan representasi 3D gedung dan fasilitas yang dapat dikenali berdasarkan kondisi Kampus UPNVJ Pondok Labu.
2. Informasi gedung dan fasilitas dikumpulkan dari sumber yang tersedia ketika observasi, sehingga data lokasi memerlukan susunan hubungan yang jelas dan dapat diperbarui melalui alur CRUD administrator yang tetap mengikuti aturan akses serta pencatatan perubahan.
3. Data lokasi dan objek tiga dimensi dikelola pada bagian yang berbeda. Tanpa kode lokasi yang sama dan proses pemeriksaan, informasi yang dipilih pengguna dapat menunjuk ke objek tujuan yang salah atau tidak ditemukan.

## 1.3 Batasan Masalah

Ruang lingkup laporan ini dibatasi agar pembahasan tetap sesuai dengan kontribusi Desainer Asset 3D dan Desainer Skema Database, yaitu sebagai berikut:

1. Objek yang direpresentasikan dibatasi pada asset 3D gedung dan fasilitas yang benar-benar memiliki GameObject pada scene Unity dan dikerjakan dalam lingkup kontribusi penulis.
2. *Unity Editor* digunakan sebagai alat utama untuk membuat dan menata *asset*. Bukti proses *Blender* memperlihatkan pembuatan objek teks 3D, tetapi laporan tidak mengaitkan objek tersebut dengan *asset* tertentu.
3. Pembahasan *asset* mencakup geometri, material, tekstur, *prefab*, hierarki, *child* `Pointer`, *GameObject* tujuan, dan konvensi penamaan. Material mengatur tampilan permukaan objek, sedangkan tekstur merupakan gambar atau pola yang diterapkan pada material; definisi teknisnya dijelaskan pada Subbab 2.3.2.
4. Pembahasan database mencakup perancangan skema akhir 11 tabel dan 10 *foreign key* melalui ERD, *constraint*, serta pengelolaan record `gedung` dan `fasilitas` yang terhubung dengan asset.
5. Penulis merancang kebijakan RLS pada 11 tabel dan struktur tabel `audit_logs`. Supabase Auth serta penulisan catatan audit melalui aplikasi dibahas sebagai konteks implementasi *Full Stack Web Developer*, *System Integrator*, dan *DevOps Engineer*; status penerapan setiap kebijakan pada database aktif tidak diklaim tanpa bukti.
6. `unity_object_name` digunakan sebagai identifier integrasi yang ditetapkan dan diperbaiki penulis pada record database serta GameObject tujuan.
7. `DatabaseSyncChecker` adalah alat pada *Unity Editor* yang membandingkan nama tujuan pada *database* dengan nama *GameObject* pada *scene*. Penulis menggunakan alat tersebut untuk memeriksa nama yang perlu ditelusuri, sedangkan kode alat merupakan kontribusi *3D Simulator* dan *Engine Developer*.
8. Logika *NavMesh*, navigasi, kontrol pemain, optimasi *engine*, *API* utama, *dashboard* *React*, autentikasi, komunikasi `SendMessage`, penerapan SQL pada database produksi, dan penulisan audit melalui aplikasi berada di luar implementasi utama penulis. Perancangan skema, *constraint*, kebijakan RLS, dan struktur tabel `audit_logs` tetap termasuk kontribusi penulis. *API* pada batasan ini berarti antarmuka pertukaran data antarkomponen perangkat lunak.
9. *Asset* disusun berdasarkan observasi visual, yaitu pengamatan bentuk dan kondisi melalui lokasi serta foto tanpa pengukuran dimensi menggunakan alat ukur. Hasilnya merupakan representasi visual, bukan model *as-built* dengan ketelitian dimensi arsitektural.

Pembagian tanggung jawab tim dirangkum pada [TABREF:peran_tanggung_jawab].

[TABLE-ID:peran_tanggung_jawab]
[TABLECAPTION:Peran dan Tanggung Jawab]

[TABLE]
Peran | Tanggung Jawab Utama
Desainer *Asset* 3D dan Desainer Skema *Database* | Merancang *asset* visual 3D dan hierarki *prefab* beserta `Pointer`, merancang skema akhir 11 tabel, ERD, 10 *foreign key*, *constraint*, dan kebijakan RLS, mengelola data serta pemetaan *asset*, dan menjaga konsistensi `unity_object_name`.
*3D Simulator* dan *Engine Developer* | Mengembangkan *runtime* *Unity* *WebGL*, termasuk `BuildingDatabase`, `NavigationReceiver`, `DatabaseSyncChecker`, navigasi *NavMesh*, interaksi pengguna, optimasi performa, dan proses *build* *WebGL*.
*Full Stack Web Developer*, *System Integrator*, dan *DevOps Engineer* | Mengembangkan Dashboard Publik dan Panel Admin *React*, *REST API* pada *Vercel Serverless Functions*, integrasi *Supabase Auth* dan *CRUD*, *bridge* sisi *React*, pencatatan analitik aplikasi, pengujian *web*, serta *deployment* dan operasional layanan *web*; *Express* dan *Umami* dikelola sebagai jalur opsional.
[/TABLE]

## 1.4 Tujuan dan Manfaat

### 1.4.1 Tujuan

Tujuan penyusunan dan pelaksanaan proyek dalam lingkup laporan ini adalah sebagai berikut:

1. Membuat dan menata representasi 3D gedung serta fasilitas berdasarkan observasi visual, kemudian menyusunnya sebagai templat *asset* yang memiliki kelompok titik tujuan.
2. Merancang skema akhir 11 tabel, ERD, 10 *foreign key*, *constraint*, dan kebijakan RLS untuk data kampus, Denah 2D, administrasi, audit, serta analitik, memodelkan alur CRUD administrator melalui Panel Admin, sekaligus mengelola data awal gedung dan fasilitas.
3. Menerapkan kode lokasi yang sama pada data dan objek tujuan di *Unity*, kemudian menggunakan alat pemeriksa milik pengembang *engine* untuk menelusuri nama yang perlu diperbaiki.

Keterkaitan satu per satu antara identifikasi masalah dan tujuan dirangkum pada [TABREF:keterkaitan_masalah_tujuan]. Urutan tiga rantai ini dipertahankan kembali pada Kesimpulan agar setiap masalah memiliki jawaban yang dapat ditelusuri.

[TABLE-ID:keterkaitan_masalah_tujuan]
[TABLECAPTION:Keterkaitan Identifikasi Masalah dan Tujuan]

[TABLE]
Rantai | Identifikasi Masalah | Arah Tujuan dan Indikator Jawaban
1 | Kebutuhan representasi 3D gedung dan fasilitas yang dapat dikenali | Pembuatan asset, prefab, dan kelompok titik tujuan berdasarkan observasi visual
2 | Kebutuhan hubungan data yang jelas serta alur CRUD administrator yang terkontrol | Skema relasional, aturan integritas dan akses, UML pengelolaan data, serta data awal yang dapat diperiksa
3 | Risiko perbedaan antara kode lokasi pada data dan objek tujuan Unity | Penerapan kode lokasi yang sama dan penggunaan alat pemeriksa untuk menelusuri ketidaksesuaian
[/TABLE]

### 1.4.2 Manfaat

Manfaat yang diharapkan dari kontribusi tersebut adalah sebagai berikut:

1. Bagi pengguna, asset 3D yang terstruktur dan data yang konsisten mendukung penyajian denah virtual serta informasi gedung dan fasilitas secara lebih mudah dipahami.
2. Bagi administrator, skema relasional dan record yang tertata memberikan dasar pengelolaan data gedung serta fasilitas secara terpusat.
3. Bagi tim pengembang, konvensi `unity_object_name` mengurangi ambiguitas ketika menghubungkan data pada dashboard, API, dan objek pada *scene* Unity.
4. Bagi institusi, rancangan tersebut dapat menjadi fondasi pengembangan layanan informasi spasial kampus yang lebih terpelihara dan berkelanjutan.

## 1.5 Jadwal Kegiatan

Kegiatan aktual penulis berlangsung selama enam bulan dan dirangkum pada [TABREF:jadwal_kegiatan]. Struktur tabel menggunakan periode enam bulan, sedangkan aktivitasnya dibatasi pada pekerjaan asset 3D, skema database, pengelolaan data, pemetaan identifier, dan dokumentasi penulis.

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
4. BAB IV PENUTUP memuat kesimpulan berdasarkan hasil yang telah didokumentasikan dan saran pengembangan lebih lanjut.

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

Solusi dalam lingkup penulis terdiri atas dua bagian yang dihubungkan oleh satu kode lokasi. Bagian pertama adalah *asset* 3D yang merepresentasikan gedung dan fasilitas. Bagian kedua adalah *database* yang menyimpan data kampus, struktur Denah 2D, profil administrator, audit, dan analitik. Kode lokasi disimpan pada kolom teknis `unity_object_name` dan dipakai juga sebagai nama objek tujuan di *Unity*. Hubungan antarkomponen tersebut ditunjukkan pada [FIGREF:diagram_arsitektur].

[FIGURE:diagram_arsitektur]
[FIGCAPTION:Arsitektur Keseluruhan Sistem Denah Virtual UPNVJ Kampus Pondok Labu]

Arsitektur tersebut membedakan kontribusi setiap anggota. Penulis merancang skema akhir 11 tabel beserta relasi, *constraint*, dan kebijakan RLS, mengelola informasi gedung atau fasilitas, membuat *asset* 3D, dan menata objek tujuan. *Full Stack Web Developer*, *System Integrator*, dan *DevOps Engineer* mengintegrasikan rancangan data ke repositori *web*, membuat antarmuka *React*, menyediakan API, mengelola autentikasi, dan menulis catatan audit melalui aplikasi. API dapat dipahami sebagai jalur pertukaran data, sedangkan *endpoint* adalah alamat layanan yang menyediakan data tertentu (Vercel 2026). *Supabase* menyediakan penyimpanan *PostgreSQL* dan layanan data berdasarkan struktur tabel yang telah dibuat (PostgreSQL Global Development Group 2026b; Supabase 2026). *React* menggunakan komponen yang dapat dipakai kembali untuk menyusun antarmuka (React 2026). *3D Simulator* dan *Engine Developer* mengembangkan *Unity* saat dijalankan dan alat pemeriksa kesesuaian data. Dalam alur ini, *Unity* menerima data lokasi melalui layanan data, sedangkan alat pemeriksa menerima daftar kode lokasi. Rincian pembuatan API dan navigasi tidak dibahas sebagai implementasi penulis.

### 2.2.1 Identifikasi Kebutuhan Fungsional

Kebutuhan fungsional dalam lingkup asset 3D dan database dirumuskan sebagai berikut:

1. *Asset* gedung dan fasilitas perlu menampilkan bentuk utama, pembagian lantai, pintu, jendela, warna, dan ciri visual yang dapat dikenali dari observasi.
2. *Asset* perlu disimpan sebagai templat yang memisahkan bentuk gedung dari objek penanda tujuan.
3. *Database* perlu menyimpan data gedung, fasilitas, fakultas, dan program studi beserta hubungan di antaranya.
4. Data awal gedung dan fasilitas perlu disusun dalam urutan yang dapat diperiksa kembali.
5. Setiap tujuan perlu menggunakan kode lokasi yang unik dan sama pada data serta objek *Unity*.
6. Perbedaan kode pada data dan objek tujuan perlu dapat ditemukan sebelum aplikasi dibangun ulang.

### 2.2.2 Identifikasi Kebutuhan Teknis

Kebutuhan teknis yang mendukung lingkup laporan ini adalah sebagai berikut:

1. *Unity* 6 dan *Unity Editor* digunakan untuk membuat serta menata bentuk 3D, material, tekstur, templat *asset*, dan susunan objek (Unity Technologies 2026a).
2. *ProBuilder*, yaitu alat pembentuk objek di dalam *Unity*, digunakan untuk membuat dan mengubah bentuk secara langsung (Unity Technologies 2026b).
3. *Supabase PostgreSQL* digunakan untuk menyimpan struktur dan data yang telah dirancang (Supabase 2026).
4. Berkas perintah *SQL* dan data awal digunakan untuk memeriksa tabel, hubungan, aturan data, dan isi data (PostgreSQL Global Development Group 2026a; PostgreSQL Global Development Group 2026b).
5. Alamat layanan */api/unity/names* menyediakan daftar kode lokasi untuk kebutuhan pemeriksaan pada *Unity Editor*.
6. Alat `DatabaseSyncChecker` yang dikembangkan *3D Simulator* dan *Engine Developer* digunakan penulis untuk membandingkan kode pada *database* dengan nama objek tujuan.
7. Autentikasi, penerapan aturan akses pada sistem produksi, pembuatan API, layanan pencatatan aktivitas, dan penyebaran aplikasi berada di luar implementasi penulis.

### 2.2.3 Identifikasi Kebutuhan Non-Fungsional

Kebutuhan nonfungsional ditetapkan sebagai berikut:

1. Setiap baris memiliki nomor pengenal, hubungan antartabel memakai kolom penghubung, nilai tertentu tidak boleh ganda, dan kolom penting wajib diisi. Istilah teknis untuk aturan tersebut dijelaskan pada awal Subbab 2.3 (PostgreSQL Global Development Group 2026a).
2. Kode lokasi harus unik, stabil, dan sama dengan nama objek tujuan.
3. Bentuk gedung, templat *asset*, titik tujuan, nama tampilan, dan kode lokasi dipisahkan agar perubahan pada satu bagian tidak merusak bagian lain.
4. Sumber rancangan, data awal, inventaris *asset*, dan hasil pemeriksaan disimpan agar perubahan dapat ditelusuri.
5. Bentuk utama dan identitas gedung harus dapat dikenali tanpa mengklaim ketelitian ukuran arsitektural.

## 2.3 Rancangan Proyek

Istilah teknis utama yang digunakan dalam rancangan dijelaskan terlebih dahulu pada [TABREF:istilah_teknis_utama] agar pembaca dapat memahami konteks pembahasan berikutnya.

[TABLE-ID:istilah_teknis_utama]
[TABLECAPTION:Istilah Teknis Utama dalam Rancangan Proyek]

[TABLE]
Istilah | Arti Sederhana | Penggunaan dalam Proyek
*Asset* 3D | Bentuk tiga dimensi yang mewakili gedung atau fasilitas | Menampilkan lingkungan kampus pada denah virtual
*Unity Editor* | Lingkungan kerja untuk membuat dan menata objek Unity | Membuat geometri, material, hierarki, dan prefab
*Scene* | Ruang kerja yang memuat lingkungan dan objek aplikasi | Menempatkan asset gedung, fasilitas, dan titik tujuan
*GameObject* | Unit objek yang dapat diberi komponen | Menjadi bagian penyusun asset dan titik tujuan
*Prefab* dan *child* | Templat objek beserta susunan turunannya | Menyimpan struktur asset agar dapat digunakan kembali
`Pointer` | Induk objek untuk menyimpan titik tujuan | Mengelompokkan GameObject tujuan
*Mesh*, *vertex*, dan *triangle* | Bentuk permukaan, titik pembentuk, dan segitiga penyusunnya | Menjelaskan ukuran teknis asset
Material, tekstur, dan *shader* | Pengaturan tampilan permukaan, gambar/pola, dan cara permukaan ditampilkan | Menyusun tampilan gedung dan fasilitas
*Collider* | Batas tak terlihat untuk mendeteksi sentuhan atau benturan | Mendokumentasikan komponen teknis asset
*Database*, tabel, dan record | Tempat penyimpanan, kelompok data, dan satu baris data | Menyimpan gedung, fasilitas, serta relasinya
ERD | Diagram yang memperlihatkan tabel dan hubungan antartabel | Merancang struktur data inti
SQL dan DDL | Bahasa perintah database dan bagian SQL untuk membuat struktur | Mendokumentasikan tabel, kolom, dan batasan
*Seed* | Data awal yang dipakai untuk mengisi database | Menyediakan data gedung dan fasilitas secara terstruktur
*Primary key* | Identitas unik untuk setiap baris | Membedakan record dalam satu tabel
*Foreign key* | Kolom penghubung antar tabel | Menghubungkan fasilitas dengan gedung
*Unique constraint* dan `NOT NULL` | Aturan pencegah nilai ganda dan penanda kolom wajib | Menjaga kualitas data
RLS | Aturan pembatasan baris data berdasarkan peran pengguna | Menjadi kebutuhan rancangan akses database
*Audit log* dan `audit_logs` | Catatan perubahan data dan tabel penyimpannya | Menjadi bagian rancangan keterlacakan perubahan
API dan *endpoint* | Jalur pertukaran data dan alamat layanan | Menyediakan data untuk komponen sistem
Kode lokasi Unity (`unity_object_name`) | Nama penghubung antara record database dan GameObject | Menyamakan nama asset dengan data
`DatabaseSyncChecker` | Alat untuk membandingkan nama pada database dan scene | Digunakan sebagai dokumentasi pemeriksaan nama
*Mismatch* dan *snapshot* | Ketidaksesuaian dan salinan kondisi pada satu waktu | Menjelaskan keluaran pemeriksaan tanpa membandingkan dua waktu yang berbeda
*Build* dan WebGL | Hasil paket aplikasi dan teknologi untuk menjalankan Unity di web | Menjadi konteks penggunaan asset pada aplikasi
[/TABLE]

### 2.3.1 Alur Perancangan Asset dan Data

Pengembangan mengikuti metode *prototyping*, yaitu pembuatan rancangan awal yang diperiksa dan diperbaiki secara berulang sampai kebutuhan proyek dapat diterapkan dengan lebih jelas (Pricillia dan Zulfachmi 2021). Dalam laporan ini, purwarupa bukan hanya tampilan aplikasi. Purwarupa dalam lingkup penulis dimulai dari rancangan hubungan data dan kebutuhan akses, dilanjutkan dengan struktur *database* serta data awal, visual gedung, titik tujuan, dan kode lokasi yang menghubungkan data dengan objek di *Unity*. Alur kerja berurutan tersebut divisualisasikan pada [FIGREF:diagram_tahap_pengembangan].

[FIGURE:diagram_tahap_pengembangan]
[FIGCAPTION:Alur Perancangan Asset 3D dan Data]

Penerapan metode tersebut pada kontribusi penulis dirinci pada [TABREF:tahapan_prototipe_dwikhi]. Setiap tahap menghasilkan bahan yang dapat diperiksa sebelum pekerjaan dilanjutkan.

[TABLE-ID:tahapan_prototipe_dwikhi]
[TABLECAPTION:Tahapan Metode Prototipe pada Lingkup Penulis]

[TABLE]
Tahap | Kegiatan dalam Lingkup Penulis | Hasil Tahap
Memahami kebutuhan | Mencatat informasi gedung, fasilitas, fakultas, program studi, kebutuhan visual, serta kebutuhan pembatasan akses | Daftar kebutuhan data dan visual
Merancang hubungan dan akses data | Mengelompokkan informasi menjadi tabel dan kolom, menentukan hubungan, menggambar ERD, serta menetapkan kebutuhan kebijakan RLS | ERD dan kebutuhan akses data
Membuat struktur dan data awal | Menerjemahkan rancangan menjadi struktur tabel, menentukan kolom wajib atau unik, lalu memasukkan data induk sebelum data turunannya | Struktur database dan data awal
Membuat visual gedung | Memilih foto referensi, membentuk model, membagi bagian per lantai, menambahkan material atau tekstur, dan menyimpan susunan sebagai prefab | Purwarupa asset 3D
Menambahkan titik tujuan | Membuat kelompok `Pointer`, menempatkan objek tujuan, dan memakai kode yang sudah dicatat pada database | Pasangan kode lokasi pada data dan objek tujuan
Memeriksa dan memperbaiki | Memeriksa hubungan data, kode yang sama, bentuk visual, susunan objek, dan titik tujuan; bagian yang tidak sesuai diperbaiki lalu diperiksa kembali | Versi perbaikan dan catatan pemeriksaan
Mendokumentasikan hasil | Menyimpan ERD, cuplikan SQL, gambar proses, tampilan asset, hierarki, dan tampilan alat pemeriksa | Bukti proses dan hasil implementasi
[/TABLE]

Urutan tersebut tidak berarti setiap tahap hanya dikerjakan satu kali. Ketika hubungan data atau kode lokasi belum sesuai, penulis kembali ke rancangan atau isi data. Ketika bentuk gedung belum cukup mudah dikenali, penulis kembali meninjau foto dan memperbaiki bentuk atau material. Siklus pemeriksaan dan perbaikan ini menjelaskan hubungan metode pada BAB II dengan langkah implementasi pada BAB III tanpa menyatakan bahwa seluruh pemetaan telah mencapai kondisi akhir.

### 2.3.2 Perancangan Asset 3D Gedung dan Fasilitas

Permukaan objek 3D dibentuk oleh titik dan bidang penyusun yang dalam *Unity* disebut *vertex* dan *mesh* (Unity Technologies 2026b). Material dan tekstur mengatur warna serta pola permukaan, sedangkan *collider* merupakan batas tidak terlihat yang digunakan sistem untuk mengenali benturan (Unity Technologies 2026c; Unity Technologies 2026d). Setelah istilah ini diperkenalkan, pembahasan berikutnya menggunakan sebutan bentuk 3D, tampilan permukaan, dan batas benturan agar prosesnya lebih mudah dipahami.

Rancangan *asset* dimulai dari foto kondisi aktual. Penulis mengamati bentuk utama bangunan, jumlah lantai, susunan pintu dan jendela, warna, serta perbandingan antarbagian yang terlihat. Informasi tersebut dipakai untuk membuat bentuk awal, bukan untuk menghasilkan model arsitektur dengan ukuran presisi.

Urutan rancangan visual terdiri atas:

1. Menentukan bagian bangunan yang menjadi ciri utama dan perlu terlihat pada denah virtual.
2. Membagi bentuk menjadi bagian utama, lantai, pintu, jendela, atap, dan objek pendukung.
3. Menentukan material atau tekstur yang mendekati warna serta pola permukaan pada foto.
4. Mengelompokkan bagian objek agar mudah ditemukan dan diperbaiki.
5. Menyimpan susunan tersebut sebagai templat *asset* yang dapat ditempatkan pada lingkungan utama *Unity*.
6. Menambahkan kelompok titik tujuan tanpa mencampurkannya dengan bentuk bangunan yang terlihat.
7. Membandingkan hasil sementara dengan foto, lalu memperbaiki bagian yang belum cukup mudah dikenali.

Alat pembentuk objek bawaan *Unity* digunakan untuk membuat dan menyunting bentuk secara langsung pada *Unity Editor* (Unity Technologies 2026b). Rancangan tersebut kemudian dibandingkan dengan referensi visual dan bukti implementasi pada Subbab 3.2.3.

Lingkup asset mencakup asset 3D gedung dan fasilitas yang memiliki GameObject pada scene Unity dan dikerjakan penulis. Jumlah record pada database tidak otomatis sama dengan jumlah asset karena sebagian fasilitas direpresentasikan sebagai titik tujuan atau informasi, bukan model terpisah. Dokumentasi visual dan struktur prefab digunakan untuk menunjukkan keterlacakan asset yang tersedia.

### 2.3.3 Perancangan Hierarki Prefab dan Konvensi Penamaan

Susunan templat *asset* dirancang untuk memisahkan bentuk gedung yang terlihat dari objek yang menandai tujuan navigasi. Dalam *Unity*, templat tersebut disebut *prefab* dan dapat menyimpan susunan objek agar digunakan kembali (Unity Technologies 2026a). Kelompok `Pointer` berisi objek kosong yang hanya menandai posisi tujuan. Pemisahan ini menjaga agar perubahan bentuk atau material gedung tidak langsung mengubah kode yang menghubungkan *asset* dengan data.

Susunan konseptual prefab dan target navigasi ditunjukkan pada [FIGREF:diagram_hierarki_prefab].

[FIGURE:diagram_hierarki_prefab]
[FIGCAPTION:Rancangan Hierarki Prefab dan Target Navigasi]

Aturan penamaan yang digunakan adalah sebagai berikut:

1. Kode lokasi Unity, yang disimpan pada kolom `unity_object_name`, menggunakan huruf kecil dan garis bawah, misalnya `gedung_rektorat` atau `mht_201`.
2. Kode harus unik pada *database* dan tidak digunakan oleh dua objek tujuan yang berbeda.
3. Titik tujuan ditempatkan pada posisi yang aman dan dapat dijangkau sistem navigasi, bukan di dalam geometri penghalang.
4. Bentuk gedung yang terlihat dipisahkan dari objek tujuan agar perubahan material atau bentuk tidak mengubah kode lokasi.
5. Templat gedung harus mempertahankan kelompok `Pointer` ketika digunakan kembali pada lingkungan utama *Unity*.

Templat dan susunan *asset* gedung serta fasilitas dalam lingkup penulis memisahkan bentuk visual dari kelompok titik tujuan. Rincian objek per lantai serta variasi susunan *asset* dijelaskan menggunakan tangkapan hierarki pada BAB III. Inventaris terbaru mencatat 19 *asset* gedung dan satu *asset* fasilitas Masjid; setiap *asset* tersebut memiliki pasangan gambar hasil dan tangkapan susunan objek.

### 2.3.4 Perancangan Interaksi Administrator dengan Database

Interaksi aktor dan alur pengelolaan data dimodelkan menggunakan *Unified Modeling Language* (UML). *Use case* digunakan untuk menunjukkan fungsi yang dapat dijalankan aktor, sedangkan *activity diagram* digunakan untuk memperlihatkan urutan aktivitas dan keputusan pada suatu proses (Wayahdi dan Ruziq 2023). Dalam lingkup laporan ini, kedua diagram menjelaskan bagaimana administrator menggunakan Panel Admin untuk melakukan operasi CRUD terhadap data yang strukturnya dirancang penulis. Implementasi antarmuka, autentikasi, dan layanan aplikasi tetap diatribusikan kepada *Full Stack Web Developer*, *System Integrator*, dan *DevOps Engineer*.

Hubungan antara Administrator dan fungsi pengelolaan data ditunjukkan pada [FIGREF:diagram_use_case_database]. Diagram memisahkan masuk ke Panel Admin, pemilihan modul data, operasi melihat, menambah, mengubah, dan menghapus data, validasi isian dan relasi, pemeriksaan sesi serta RLS, penyimpanan perubahan, dan pencatatan riwayat melalui layanan aplikasi. Modul data yang dikelola mencakup `gedung`, `fasilitas`, `program_studi`, dan konfigurasi Denah 2D. Relasi `<<include>>` mempertahankan kata *include* untuk menunjukkan langkah yang selalu menjadi bagian dari fungsi induknya.

[FIGURE:diagram_use_case_database]
[FIGCAPTION:Use Case Pengelolaan Database melalui Panel Admin]

Urutan proses CRUD diperinci pada [FIGREF:diagram_activity_crud_admin]. Setelah kredensial diverifikasi, administrator memilih modul dan operasi data, mengisi formulir atau mengonfirmasi penghapusan, lalu antarmuka memeriksa isian. Database memeriksa sesi dan kebijakan RLS sebelum menjalankan operasi. Jika operasi berhasil, layanan aplikasi mencatat perubahan dan antarmuka memuat ulang tabel. Diagram ini tidak menyatakan adanya *trigger* audit pada database karena artefak SQL tidak mendefinisikannya.

[FIGURE:diagram_activity_crud_admin]
[FIGCAPTION:Activity Diagram CRUD Data melalui Panel Admin]

Hubungan administrator dengan tabel pada kedua diagram tersebut merupakan hubungan perilaku atau kewenangan akses, bukan *foreign key*. Relasi fisik antartabel tetap ditentukan pada ERD dan DDL pada subbab berikutnya.

### 2.3.5 Perancangan ERD dan Struktur Data

*Entity Relationship Diagram* (ERD) merupakan diagram yang memperlihatkan kelompok data, isi setiap kelompok, dan hubungan di antaranya sebagai dasar perancangan *database* (Afiifah et al. 2022). Dalam proyek ini, ERD membantu penulis menentukan struktur sebelum data gedung serta fasilitas dimasukkan.

Proses pembuatan ERD dilakukan melalui langkah berikut:

1. Menginventarisasi informasi yang tersedia dari observasi dan data proyek, seperti nama gedung, lokasi, jumlah lantai, nama fasilitas, fakultas, dan program studi.
2. Mengelompokkan kebutuhan data awal menjadi empat kelompok utama, yaitu `gedung`, `fasilitas`, `fakultas`, dan `program_studi`.
3. Menentukan kolom yang diperlukan pada setiap kelompok dan membedakan kolom wajib dari kolom tambahan.
4. Menetapkan nomor pengenal utama agar setiap baris data dapat dibedakan.
5. Menentukan hubungan satu gedung dengan banyak fasilitas, satu gedung dengan fakultas yang menempatinya, serta satu fakultas dengan banyak program studi.
6. Menambahkan empat tabel `campus_map_*` ke skema akhir setelah pengembangan dan tindak lanjut UAT menghadirkan kebutuhan Denah 2D, bukan sebagai kebutuhan awal.
7. Menambahkan tabel `admin_users`, `audit_logs`, dan `web_analytics_log` untuk kebutuhan administrasi, audit, dan analitik, lalu membedakan hubungan akses logis administrator dari relasi fisik yang didefinisikan oleh *foreign key*.
8. Menetapkan aturan hubungan agar penghapusan atau perubahan satu data tidak meninggalkan hubungan yang tidak jelas.
9. Menambahkan kode lokasi Unity pada data gedung dan fasilitas agar keduanya dapat dipetakan ke objek tujuan.
10. Menggambar skema akhir sebagai dua ERD, memeriksanya menggunakan contoh data dan DDL, lalu memperbaiki kolom atau hubungan yang belum sesuai.

Hasil proses tersebut membentuk skema lengkap 11 tabel. Delapan tabel data kampus dan Denah 2D yang memiliki 10 *foreign key* fisik ditunjukkan pada [FIGREF:diagram_erd_data_navigasi].

[FIGURE:diagram_erd_data_navigasi]
[FIGCAPTION:ERD Data Kampus dan Denah 2D]

Tiga tabel pendukung ditampilkan pada [FIGREF:diagram_erd_pendukung]. Garis putus-putus dari `admin_users` ke kelompok tabel data menunjukkan kewenangan CRUD melalui Panel Admin, bukan *foreign key*. Hubungan menuju `audit_logs` menunjukkan bahwa aktivitas perubahan dicatat melalui layanan aplikasi, sedangkan hubungan menuju `web_analytics_log` menunjukkan fungsi peninjauan analitik. Pemodelan ini menghubungkan peran administrator dengan tabel yang dikelolanya tanpa menggambarkan `audit_logs.actor_id` secara keliru sebagai *foreign key* ke `admin_users` atau `auth.users`.

[FIGURE:diagram_erd_pendukung]
[FIGCAPTION:ERD Tabel Pendukung dan Hubungan Akses Logis Administrator]

Fungsi seluruh tabel pada skema akhir disajikan pada [TABREF:struktur_basis_data].

[TABLE-ID:struktur_basis_data]
[TABLECAPTION:Struktur Entitas Database]

[TABLE]
Tabel | Fungsi | Relasi atau Batasan Utama
`gedung` | Menyimpan identitas dan informasi fisik gedung | Primary key `id`; `nama_gedung` dan `unity_object_name` unik; menjadi induk `fasilitas`
`fasilitas` | Menyimpan ruangan atau fasilitas di dalam gedung | Foreign key `id_gedung` ke `gedung`; `unity_object_name` unik
`fakultas` | Menyimpan profil fakultas | Foreign key `id_gedung_utama` ke `gedung`
`program_studi` | Menyimpan program studi dan akreditasi | Foreign key `id_fakultas` ke `fakultas`; kombinasi nama, jenjang, dan fakultas unik
`campus_maps` | Menyimpan metadata gambar Denah 2D | `slug` unik; menjadi induk node, edge, dan titik gedung
`campus_map_nodes` | Menyimpan simpul jalur pada Denah 2D | Foreign key `map_id` ke `campus_maps`; koordinat berada pada rentang 0 sampai 1
`campus_map_edges` | Menyimpan hubungan antarsimpul untuk perhitungan rute | Foreign key ke peta serta simpul asal dan tujuan; kombinasi arah edge unik
`campus_map_building_points` | Menyimpan posisi gedung dan simpul masuk pada Denah 2D | Foreign key ke peta, gedung, dan simpul masuk; kombinasi peta dan gedung unik
`admin_users` | Menyimpan profil administrator lokal | `username` unik; tidak memiliki foreign key pada SQL; secara logis menjadi aktor CRUD melalui Panel Admin
`audit_logs` | Menyimpan data pelaku, tindakan, tabel, dan perubahan record | `actor_id` berupa UUID biasa; SQL tidak mendefinisikan foreign key atau trigger audit; penulisan riwayat dilakukan layanan aplikasi
`web_analytics_log` | Menyimpan ringkasan kunjungan halaman | Tidak memiliki foreign key pada SQL
[/TABLE]

Penulis merancang entitas, atribut, 10 *foreign key*, *constraint*, aksi penghapusan, serta kebijakan RLS pada skema akhir. Berkas `dokumentasi/sql/001_full_setup.sql` menjadi artefak dokumentasi struktur dan tidak dijalankan saat penyusunan laporan karena memuat perintah `DROP TABLE`. Berkas tersebut tidak memuat definisi *trigger* sehingga laporan tidak mengklaim *trigger* audit aktif. Integrasi SQL ke repositori *web*, implementasi Supabase Auth, dan penulisan catatan audit melalui aplikasi tetap diatribusikan kepada *Full Stack Web Developer*, *System Integrator*, dan *DevOps Engineer*.

### 2.3.6 Perancangan Pengelolaan Data Awal dan Kualitas Data

Data awal, yang pada berkas teknis disebut *seed*, merupakan kumpulan data untuk mengisi *database* secara terstruktur dan dapat diulang. Dalam proyek ini, data awal menjadi sumber data gedung, fakultas, program studi, dan fasilitas yang dikelola penulis. Pengelolaannya dilakukan dengan memasukkan data induk sebelum data turunannya, memeriksa hubungan antardata, melengkapi kolom wajib, mencegah kode ganda, dan menyamakan penulisan nama.

Kualitas data dijaga dengan memisahkan nama tampilan dari kode lokasi. Nama tampilan dapat diperbaiki agar mudah dicari tanpa mengubah kode yang telah dipakai pada lingkungan *Unity*. Data yang belum mempunyai pasangan objek perlu diperiksa dan tidak boleh langsung dianggap sebagai *asset* yang tersedia.

### 2.3.7 Perancangan Pemetaan dan Pemeriksaan Kode Lokasi Unity

Alur pemeriksaan kode lokasi ditunjukkan pada [FIGREF:diagram_sequence_validasi]. Nama teknis alat yang digunakan adalah `DatabaseSyncChecker`. Setelah diperkenalkan pada bagian ini, alat tersebut disebut sebagai alat pemeriksa kesesuaian data. Kode alat dibuat oleh *3D Simulator* dan *Engine Developer*, sedangkan penulis menggunakannya untuk menelusuri nama yang perlu diperiksa.

[FIGURE:diagram_sequence_validasi]
[FIGCAPTION:Sequence Diagram Validasi Identifier Asset dan Data]

Ketentuan pemetaan dirancang sebagai berikut:

1. Data gedung dan fasilitas menyimpan kode lokasi pada kolom `unity_object_name` dan setiap kode harus unik.
2. Layanan data menyediakan kode tersebut untuk komponen *Unity* dan alat pemeriksa.
3. Objek tujuan ditempatkan di dalam kelompok `Pointer` dan menggunakan kode yang sama.
4. Penulisan kode menggunakan huruf kecil dan garis bawah agar mudah dibandingkan.
5. Nama gedung atau fasilitas yang dibaca pengguna dipisahkan dari kode lokasi sehingga perubahan tulisan tidak merusak pemetaan.
6. Perbedaan nama perlu ditelusuri pada data atau objek tujuan sesuai sumber masalahnya.

## 2.4 Rencana Pengujian Proyek

Rencana pengujian disusun agar setiap bagian rancangan memiliki hasil pengujian yang dapat ditelusuri pada Subbab 3.5. Setiap skenario perlu mencantumkan input, prasyarat, hasil yang diharapkan, hasil aktual, status, dan lokasi bukti.

### 2.4.1 Pemeriksaan Visual dan Struktur Asset

Pemeriksaan asset dilakukan terhadap bukti representatif dengan membandingkan bentuk utama, jumlah lantai yang terlihat, susunan objek, material atau tekstur, struktur prefab, child `Pointer`, dan GameObject tujuan. Pemeriksaan ini mendokumentasikan kesesuaian struktur dan keterbacaan visual, bukan mengukur performa, frame rate, atau dampak asset terhadap ukuran build.

### 2.4.2 Pemeriksaan Struktur Skema dan Seed

*Constraint* adalah aturan pada *database* yang mencegah data disimpan dalam bentuk yang tidak sesuai. Aturan ini diterapkan melalui `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, dan `NOT NULL` yang telah dijelaskan pada kebutuhan nonfungsional (PostgreSQL Global Development Group 2026a). Penulis membaca definisi *SQL* dan struktur *seed* untuk mendokumentasikan jumlah kolom, relasi ID, nilai wajib, dan keunikan `unity_object_name`. Berkas *SQL setup* tidak dijalankan karena memuat operasi penghapusan tabel, sehingga uraian ini tidak menyatakan kondisi *PostgreSQL* *live*.

### 2.4.3 Pemeriksaan Konsistensi Asset dan Data

Pemeriksaan konsistensi membandingkan `unity_object_name` pada *database* dengan nama *GameObject* pada *scene* *Unity*. Perbedaan antara dua daftar tersebut disebut *mismatch* atau ketidaksesuaian. Penulis menggunakan `DatabaseSyncChecker` yang dikembangkan *3D Simulator* dan *Engine Developer* sebagai alat bantu untuk menelusuri nama yang perlu diperiksa.

### 2.4.4 Black Box dan UAT Produk Bersama

*Black Box Testing* adalah metode yang memeriksa fungsi sistem melalui masukan dan keluaran tanpa meninjau rincian kode internal (Maulida et al. 2025). *User Acceptance Testing* (UAT) adalah pengujian oleh pihak yang berkepentingan untuk menilai kesesuaian sistem dengan kebutuhan penggunaan yang telah ditentukan (Aliyah et al. 2025). Dalam laporan ini, hasil pengujian bersama digunakan sebagai konteks produk, bukan sebagai klaim kepemilikan seluruh implementasi sistem.

---

# BAB III IMPLEMENTASI PROYEK
## 3.1 Profil Mitra dan Pemangku Kepentingan

### 3.1.1 Nama Organisasi atau Lembaga Mitra

Humas Universitas Pembangunan Nasional “Veteran” Jakarta atau Humas UPNVJ.

### 3.1.2 Deskripsi Mitra

UPNVJ berakar dari Akademi Pembangunan Nasional "Veteran" yang didirikan pada 15 Desember 1958. Perkembangan UPNVJ Jakarta dimulai melalui penggabungan tiga akademi di bawah Lembaga Pembinaan Kader Pembangunan pada 7 Januari 1963, kemudian berkembang menjadi UPN "Veteran" Cabang Jakarta pada 1977. Pada 6 Oktober 2014, UPNVJ berubah status dari perguruan tinggi swasta menjadi perguruan tinggi negeri berdasarkan Peraturan Presiden Nomor 120 Tahun 2014 (UPNVJ 2025b).

Kampus utama yang menjadi konteks proyek berada di Jalan R.S. Fatmawati Nomor 1, Cilandak, Jakarta Selatan 12450. Halaman lokasi resmi UPNVJ mencatat Kampus Pondok Labu menempati lahan 2,4 ha, memiliki luas lantai bangunan keseluruhan 28.887 m², dan menyediakan 71 ruang kuliah (UPNVJ 2022). Data tersebut digunakan sebagai profil institusi dan konteks lokasi, bukan sebagai ukuran geometri asset Unity.

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

Implementasi menerapkan tahapan metode *prototyping* pada Subbab 2.3.1. Penulis tidak langsung menghasilkan bentuk dan data akhir, tetapi membuat rancangan awal, memeriksanya dengan contoh data atau foto, memperbaiki bagian yang belum sesuai, kemudian mendokumentasikan versi yang tersedia. Urutan aktual dimulai dari ERD dan kebutuhan akses data, dilanjutkan dengan struktur *database* serta data awal, pembuatan visual gedung, pembuatan titik tujuan berdasarkan kode pada data, dan pemeriksaan hubungan keduanya.

Pembuatan API tidak termasuk implementasi penulis. Penulis menyiapkan struktur data dan kode lokasi yang perlu tersedia bagi komponen lain, sedangkan alamat layanan dan kode API dibuat oleh *Full Stack Web Developer*, *System Integrator*, dan *DevOps Engineer*. Demikian pula, perhitungan rute dan alat pemeriksa kesesuaian data dibuat oleh *3D Simulator* dan *Engine Developer*. Batas ini dipertahankan agar urutan kerja dapat dijelaskan secara lengkap tanpa mengambil klaim kontribusi anggota lain.

### 3.2.1 Implementasi Perancangan ERD dan Kebijakan Akses Data

Implementasi dimulai dengan menyusun hubungan data sebelum model gedung diberi kode tujuan. Penulis menginventarisasi informasi gedung, fasilitas, fakultas, dan program studi; mengelompokkannya menjadi empat tabel data kampus; menentukan kolom; lalu menetapkan hubungan antartabel. Nomor pengenal utama membedakan setiap baris, sedangkan kolom penghubung mengaitkan fasilitas dengan gedung, fakultas dengan gedung utama, dan program studi dengan fakultas. Skema kemudian berkembang menjadi 11 tabel: tiga tabel pendukung ditambahkan untuk administrasi, audit, dan analitik, sedangkan empat tabel Denah 2D masuk setelah pengembangan dan tindak lanjut UAT. Kode lokasi tetap digunakan pada data gedung dan fasilitas agar tahap pembuatan titik tujuan mempunyai acuan yang jelas.

Proses tersebut dilakukan melalui urutan berikut:

1. Mencatat informasi yang perlu disimpan dari inventaris lapangan dan kebutuhan produk.
2. Memisahkan informasi menjadi tabel `gedung`, `fasilitas`, `fakultas`, dan `program_studi`.
3. Menentukan kolom wajib, kolom tambahan, nomor pengenal utama, serta nilai yang tidak boleh ganda.
4. Menentukan arah hubungan dan tindakan ketika data induk dihapus.
5. Menambahkan tabel `admin_users`, `audit_logs`, dan `web_analytics_log` sesuai kebutuhan pendukung sistem.
6. Menambahkan empat tabel `campus_map_*` setelah tindak lanjut UAT membutuhkan Denah 2D.
7. Menambahkan kolom kode lokasi pada data gedung dan fasilitas.
8. Menggambar dua ERD, membaca kembali seluruh 10 *foreign key* dengan contoh data dan DDL, lalu memperbaiki kolom atau hubungan yang belum tepat.

Penulis merancang kebijakan RLS pada seluruh 11 tabel agar data publik dapat dibaca sesuai kebutuhan, sedangkan perubahan data dibatasi pada pengguna terautentikasi. Tabel `audit_logs` menampung informasi pelaku, tindakan, tabel yang diubah, nilai lama, nilai baru, dan waktu perubahan. Cuplikan berikut memperlihatkan bentuk salah satu kebijakan pada berkas dokumentasi sistem.

```sql
ALTER TABLE public.gedung ENABLE ROW LEVEL SECURITY;

CREATE POLICY gedung_anon_select ON public.gedung
    FOR SELECT TO anon USING (true);

CREATE POLICY gedung_auth_update ON public.gedung
    FOR UPDATE TO authenticated USING (true) WITH CHECK (true);
```

Berkas yang diperiksa juga memuat kebijakan baca, tambah, ubah, dan hapus untuk pengguna terautentikasi. Cuplikan tersebut menunjukkan bahwa bentuk perintah sesuai dengan akses yang dirancang, tetapi tidak digunakan untuk menyatakan bahwa penulis menjalankan atau menerapkan setiap kebijakan pada *database* produksi. Definisi tabel `audit_logs` tersedia pada berkas *setup*, sedangkan perintah *trigger* audit tidak terdapat pada artefak SQL yang diberikan. Oleh karena itu, laporan tidak mengklaim adanya *trigger* audit *database*.

### 3.2.2 Implementasi Struktur Database dan Data Gedung Dewi Sartika

Rancangan ERD diterjemahkan menjadi perintah pembentuk 11 tabel dan 10 *foreign key* pada `dokumentasi/sql/001_full_setup.sql`, sedangkan data awal berada pada `dokumentasi/sql/002_seed_data.sql`. Kedua berkas merupakan salinan persis dari sumber yang diberikan pengguna dan hanya dibaca sebagai dokumentasi. Berkas pertama memuat `DROP TABLE`, sedangkan berkas kedua memuat `TRUNCATE ... RESTART IDENTITY CASCADE`; karena itu, keduanya tidak dijalankan dalam proses penyusunan laporan.

Struktur tabel `gedung` pada berkas *setup* ditunjukkan melalui cuplikan berikut.

```sql
CREATE TABLE public.gedung (
    id SERIAL PRIMARY KEY,
    nama_gedung VARCHAR(255) NOT NULL UNIQUE,
    deskripsi_gedung TEXT,
    lokasi TEXT,
    jumlah_lantai INT DEFAULT 1,
    foto_url VARCHAR(255),
    unity_object_name TEXT UNIQUE
);
```

Kolom `id` menjadi nomor pengenal utama, `nama_gedung` harus terisi dan tidak boleh ganda, sedangkan `unity_object_name` menyimpan kode lokasi yang juga tidak boleh ganda. Setelah struktur ditentukan, data induk dimasukkan sebelum data fasilitas yang merujuknya.

Gedung Dewi Sartika digunakan sebagai contoh untuk menunjukkan hubungan antara urutan data dan kode lokasi. Bagian awal *seed* mengosongkan tabel serta mengulang nomor otomatis sebelum 19 data gedung dimasukkan. Baris Dewi Sartika berada pada posisi ke-13 dalam satu perintah `INSERT`.

```sql
TRUNCATE public.fasilitas, public.program_studi, public.fakultas, public.gedung
RESTART IDENTITY CASCADE;

('Gedung Dewi Sartika', 'Gedung Fakultas Ilmu Komputer',
 'Klaster Fakultas Ilmu Komputer', 4,
 'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/gedung/gedung_gedung_dewi_sartika.webp',
 'dewi_sartika'),
```

Perintah `RESTART IDENTITY` berarti nomor otomatis dimulai kembali ketika *seed* tersebut dijalankan sesuai urutannya. Karena Dewi Sartika merupakan data gedung ke-13, contoh fasilitasnya merujuk `id_gedung = 13`. Hubungan tersebut terlihat pada cuplikan satu data fasilitas berikut.

```sql
-- Gedung 13: Gedung Dewi Sartika
(
    'Ruang BEM FIK',
    $$Ruang sekretariat Badan Eksekutif Mahasiswa (BEM) FIK di Gedung Dewi Sartika, sebagai pusat koordinasi program kerja dan kegiatan kemahasiswaan.$$,
    'Ruang Kegiatan Mahasiswa',
    1,
    NULL,
    13,
    'ds_bem'
),
```

Contoh tersebut menunjukkan dua tingkat kode lokasi. Nilai `dewi_sartika` digunakan untuk tujuan gedung, sedangkan `ds_bem` digunakan untuk salah satu fasilitas di dalamnya. Penjelasan ini membaca hubungan yang tertulis pada artefak *seed* dan tidak digunakan sebagai bukti bahwa perintah telah dieksekusi pada *database* produksi.

### 3.2.3 Implementasi Pembuatan Visual Gedung Dewi Sartika

Setelah data dan kode gedung tersedia, penulis membuat visual Gedung Dewi Sartika sebagai studi proses lengkap. *Unity Editor* menjadi alat utama untuk membentuk dan menata objek. Dimensi presisi tidak dinyatakan karena observasi dilakukan melalui pengamatan langsung dan foto tanpa alat ukur.

Foto pada [FIGREF:process_dewi_reference] memperlihatkan bangunan empat lantai berwarna hijau, susunan koridor dan jendela, atap memanjang, tulisan nama gedung, lapangan, serta objek olahraga di bagian depan. Unsur yang terlihat dipakai sebagai referensi bentuk dan warna, bukan sebagai data ukuran bangunan.

[FIGURE:process_dewi_reference]
[FIGCAPTION:Referensi Visual Gedung Dewi Sartika]

Bentuk awal pada [FIGREF:process_dewi_base] memperlihatkan susunan geometri sederhana yang menjadi dasar bangunan. Karena gambar hanya menampilkan area model dan tidak memperlihatkan seluruh antarmuka *Unity*, gambar ini digunakan sebatas untuk menjelaskan bentuk awal.

[FIGURE:process_dewi_base]
[FIGCAPTION:Bentuk Dasar Gedung Dewi Sartika]

Perkembangan lantai dasar pada [FIGREF:process_dewi_ground_floor] memperlihatkan penambahan dinding, tiang, bidang lantai, dan bagian yang membentuk ruang dasar. Susunan objek pada sisi kiri membantu penulis menemukan bagian yang sedang dikerjakan.

[FIGURE:process_dewi_ground_floor]
[FIGCAPTION:Pembentukan Struktur Lantai Dasar Gedung Dewi Sartika]

Tahap pembuatan material pada [FIGREF:process_dewi_material_create] memperlihatkan perintah untuk membuat material baru di dalam proyek *Unity*. Material tersebut menjadi tempat pengaturan warna atau gambar permukaan sebelum diterapkan pada model.

[FIGURE:process_dewi_material_create]
[FIGCAPTION:Pembuatan Material Baru pada Unity]

Penambahan tekstur pada [FIGREF:process_dewi_material_texture] memperlihatkan berkas gambar yang disiapkan pada kumpulan berkas proyek dan slot permukaan material pada *Inspector*. Gambar ini digunakan untuk menjelaskan pemasukan tekstur, tanpa menambahkan klaim pengaturan lain yang tidak terlihat.

[FIGURE:process_dewi_material_texture]
[FIGCAPTION:Penambahan Tekstur pada Material di Unity]

Tampilan model pada [FIGREF:process_dewi_material_apply] memperlihatkan permukaan gedung yang sudah mempunyai beberapa warna dan material. Karena objek beserta slot materialnya tidak terlihat bersamaan pada *Inspector*, gambar ini hanya digunakan untuk menunjukkan perubahan tampilan model pada tahap penggunaan material.

[FIGURE:process_dewi_material_apply]
[FIGCAPTION:Tampilan Model Gedung Dewi Sartika pada Tahap Penggunaan Material]

Objek pendukung pada [FIGREF:process_dewi_environment] memperlihatkan tambahan pintu, tanaman, dan bagian lingkungan di sekitar lantai dasar. Tahap ini membantu mendekatkan tampilan model pada unsur yang terlihat di lingkungan aktual.

[FIGURE:process_dewi_environment]
[FIGCAPTION:Penambahan Objek Pendukung pada Gedung Dewi Sartika]

Pengelompokan pada [FIGREF:process_dewi_floor_groups] memperlihatkan bagian Gedung Dewi Sartika yang dipisahkan menjadi kelompok Lantai 1 sampai Lantai 4. Pemisahan tersebut memudahkan penulis menemukan dan memperbaiki bagian per lantai tanpa menelusuri seluruh objek satu per satu.

[FIGURE:process_dewi_floor_groups]
[FIGCAPTION:Pengelompokan Gedung Dewi Sartika Berdasarkan Lantai]

Langkah tersebut diulang pada *asset* lain dengan bentuk dan referensi masing-masing. Sebagian objek pendukung dibuat menggunakan *Blender*; bukti yang tersedia memperlihatkan pembuatan objek teks 3D, tetapi tidak digunakan untuk menyatakan Gedung Dewi Sartika atau gedung tertentu sebagai hasil *Blender*.

Folder bukti terbaru memuat 30 berkas referensi visual. Berkas tersebut menjadi rujukan bentuk dan kondisi visual untuk sebagian *asset* dan entitas *database* terkait. Cakupan foto tidak digunakan untuk menyimpulkan jumlah seluruh *GameObject* yang dikerjakan.

Daftar berkas referensi visual dirangkum pada [TABREF:inventaris_foto_referensi].

[TABLE-ID:inventaris_foto_referensi]
[TABLECAPTION:Inventaris Berkas Referensi Visual Kondisi Aktual]

[TABLE]
No. | Objek yang Terdokumentasi | Berkas Bukti
1 | Bagian depan Gedung Muhammad Yamin | `Foto_depan_M.Yamin.jpg`
2 | Gedung Cipto Mangunkusumo | `Foto_gedung_Cipto.jpg`
3 | Gedung Muhammad Yamin | `Foto_gedung_M.Yamin.jpg`
4 | Gedung Muh. Husni Thamrin | `Foto_gedung_Muh_Tamrin.jpg`
5 | Gedung Soetomo | `Foto_gedung_Soetomo.jpg`
6 | Gedung Wahidin Sudiro Husodo | `Foto_gedung_wahidin.jpg`
7 | Gerbang depan kampus | `Foto_gerbang_depan.jpg`
8 | Ruang Rektorat | `Foto_ruangan_rektorat.jpg`
9 | Ruang Wi-Fi Gedung Abdul Rahman Saleh | `Foto_ruangan_Wifi_gedung_Abdul_Rachman.jpg`
10 | Gedung Yos Sudarso | `gambar_Gedung_Yos_Sudarso.png`
11 | Masjid | `gambar_masjid.png`
12 | Gedung Wahidin Sudiro Husodo | `refrensi__gedung_Wahidin.jpeg`
13 | Gedung Abdul Rahman Saleh | `refrensi_gedung_abdul_rachman.jpeg`
14 | Gedung Dewi Sartika | `refrensi_gedung_dewi_sartika.jpeg`
15 | Gedung Cipto Mangunkusumo | `refrensi_gedung_dr.cipto.jpeg`
16 | Gedung Jenderal Soedirman | `refrensi_Gedung_jenderal_soedirman.png`
17 | Gedung Ki Hadjar Dewantara | `refrensi_gedung_ki_hadjar_dewantara.jpeg`
18 | Gedung Muhammad Yamin | `refrensi_gedung_m.yamin.jpeg`
19 | Gedung Muh. Husni Thamrin | `refrensi_gedung_muh husni tamrin.jpeg`
20 | Gedung RA Kartini | `refrensi_gedung_ra_kartini.jpeg`
21 | Gedung Soepomo | `refrensi_gedung_soepomo.jpeg`
22 | Gedung Soetomo | `refrensi_gedung_soetomo.jpeg`
23 | Gedung Kuliah dan Kegiatan Mahasiswa | `refrensi_Gedung_ukm.jpeg`
24 | Gedung Yos Sudarso | `refrensi_gedung_Yos_Sudarso.jpeg`
25 | Kantin | `Refrensi_kantin.jpeg`
26 | Lapangan Basket | `refrensi_lapangan_basket.png`
27 | Lapangan Upacara | `refrensi_lapangan_upacara.png`
28 | Parkir Hukum | `refrensi_parkir_hukum.jpeg`
29 | Parkir Depan UPNVJ | `Refrensi_parkiran_depan.webp`
30 | Parkir Belakang UPNVJ | `Refrensi_parkiran_belakang.webp`
[/TABLE]

Referensi visual Gedung Jenderal Soedirman ditampilkan pada [FIGREF:evidence_photo_jenderal_soedirman]. Foto memperlihatkan bentuk utama gedung, susunan lantai, pintu, jendela, dan warna yang digunakan sebagai acuan visual.

[FIGURE:evidence_photo_jenderal_soedirman]
[FIGCAPTION:Referensi Visual Gedung Jenderal Soedirman]

Foto dan pengamatan langsung digunakan sebagai pembanding pada setiap perbaikan bentuk. Oleh karena itu, hasil implementasi merupakan representasi visual untuk denah virtual dan tidak dimaksudkan sebagai gambar bangunan dengan ukuran arsitektural.

Selain rangkaian Gedung Dewi Sartika, bukti proses umum pada [FIGREF:evidence_process_asset] memperlihatkan kegiatan penyusunan objek gedung di *Unity Editor*. Gambar ini digunakan sebagai bukti tambahan bahwa pembuatan bentuk dan pengelompokan objek dilakukan pada lingkungan kerja proyek.

[FIGURE:evidence_process_asset]
[FIGCAPTION:Proses Pengerjaan Asset Gedung di Unity Editor]

Proses pembuatan objek pendukung menggunakan *Blender* ditunjukkan pada [FIGREF:evidence_process_blender]. Tangkapan tersebut memperlihatkan pembuatan objek teks 3D dan pengaturan ketebalannya, tetapi tidak digunakan untuk menyatakan objek tersebut sebagai bagian dari gedung tertentu.

[FIGURE:evidence_process_blender]
[FIGCAPTION:Proses Pembuatan Objek Teks 3D pada Blender]

Versi *editor* dan inventaris *asset* dicatat pada Subbab 3.3.3. Bukti proses digunakan untuk menjelaskan tahapan pengerjaan yang terlihat.

### 3.2.4 Implementasi Prefab, Pointer, dan Penempatan pada Scene

Setelah bagian visual dikelompokkan, penulis menambahkan objek tujuan berdasarkan kode yang telah dicatat pada *database*. Bentuk gedung dipisahkan dari kelompok `Pointer` agar perubahan tampilan gedung tidak mengubah nama objek yang dibaca sistem.

Implementasi mengikuti urutan berikut:

1. Membuka susunan Gedung Dewi Sartika dan memeriksa kelompok objek per lantai.
2. Membuat kelompok `Pointer` sebagai tempat objek tujuan.
3. Membuat objek kosong untuk tujuan gedung dan memberinya nama `dewi_sartika`.
4. Menempatkan objek tujuan pada bagian depan gedung sebagai penanda lokasi tujuan.
5. Menempatkan gedung pada *scene* utama.
6. Menyimpan susunan gedung, kelompok lantai, dan titik tujuan sebagai *prefab*.

Pembuatan kelompok pada [FIGREF:process_dewi_pointer_create] memperlihatkan objek `Pointer` yang dipilih dan perintah untuk membuat objek kosong di bawahnya. Objek kosong tersebut tidak menambah bentuk yang terlihat; fungsinya adalah menyimpan posisi tujuan.

[FIGURE:process_dewi_pointer_create]
[FIGCAPTION:Pembuatan Kelompok Pointer pada Gedung Dewi Sartika]

Objek tujuan pada [FIGREF:process_dewi_pointer_target] diberi nama `dewi_sartika` dan ditempatkan di bagian depan gedung. Nama tersebut sama dengan kode gedung pada cuplikan *seed* di Subbab 3.2.2, sehingga hubungan data dan objek tujuan dapat dibaca tanpa menggunakan nama panjang gedung.

[FIGURE:process_dewi_pointer_target]
[FIGCAPTION:Penamaan dan Penempatan Objek Tujuan dewi_sartika]

Penempatan pada [FIGREF:process_dewi_scene_placement] memperlihatkan Gedung Dewi Sartika di lingkungan utama bersama susunan objek dan nilai posisi pada *Inspector*. Komponen *NavMesh Modifier* terlihat pada gambar sebagai bagian dari komponen sistem, tetapi pengaturan *NavMesh* dan perhitungan jalur merupakan kontribusi *3D Simulator* dan *Engine Developer*, bukan pekerjaan penulis.

[FIGURE:process_dewi_scene_placement]
[FIGCAPTION:Penempatan Gedung Dewi Sartika pada Scene Utama]

Penyimpanan pada [FIGREF:process_dewi_prefab_save] memperlihatkan Dewi Sartika sebagai berkas *prefab* di dalam kumpulan berkas proyek. Penyimpanan ini mempertahankan susunan visual dan objek tujuan agar dapat digunakan pada *scene* utama.

[FIGURE:process_dewi_prefab_save]
[FIGCAPTION:Penyimpanan Gedung Dewi Sartika sebagai Prefab]

Folder bukti memuat pasangan hasil visual dan hierarki akhir untuk *asset* gedung. Hierarki akhir Dewi Sartika pada Subbab 3.4.2 digunakan untuk menunjukkan bahwa kelompok `Pointer` tetap tersimpan bersama susunan gedung.

### 3.2.5 Implementasi Pemetaan Kode Lokasi dan Batas Integrasi

Pemetaan dilakukan dengan menerapkan kode yang sama pada kolom `unity_object_name` di data `gedung` atau `fasilitas` dan pada objek tujuan di dalam kelompok `Pointer`. Setelah istilah teknis tersebut diperkenalkan, bagian ini menggunakan sebutan kode lokasi. Pada contoh Dewi Sartika, data gedung memakai `dewi_sartika`, objek tujuan gedung memakai nama yang sama, sedangkan fasilitas BEM memakai kode `ds_bem`.

Tahap pemeriksaan dilakukan sebagai berikut:

1. Mengumpulkan daftar kode lokasi dari data gedung dan fasilitas.
2. Mengumpulkan nama objek tujuan dari kelompok `Pointer`.
3. Membandingkan kedua daftar menggunakan alat pemeriksa kesesuaian data.
4. Menelusuri perbedaan pada data atau nama objek sesuai sumber masalahnya.
5. Memperbarui kode atau nama yang tidak sesuai, kemudian mengulangi pemeriksaan bila diperlukan.

Kolom dan contoh kode lokasi pada data `gedung` dapat dilihat pada [FIGREF:evidence_unity_names_gedung]. Gambar tersebut memperlihatkan bahwa kode ditulis dengan huruf kecil dan garis bawah serta disimpan terpisah dari nama gedung yang dibaca pengguna. Gambar digunakan untuk menjelaskan bentuk kolom dan pola penulisannya, bukan untuk menyatakan bahwa seluruh nama telah cocok.

[FIGURE:evidence_unity_names_gedung]
[FIGCAPTION:Contoh Nilai unity_object_name pada Tabel Gedung]

Penerapan kode lokasi pada data fasilitas terlihat pada [FIGREF:evidence_unity_names_fasilitas]. Tangkapan tersebut juga menampilkan hubungan fasilitas dengan gedung, lantai, alamat foto, dan kode lokasi. Gambar digunakan untuk menunjukkan bahwa kode disimpan bersama informasi fasilitas yang akan ditampilkan.

[FIGURE:evidence_unity_names_fasilitas]
[FIGCAPTION:Contoh Nilai unity_object_name pada Tabel Fasilitas]

Kesamaan kode Dewi Sartika pada data dan objek tujuan dapat dibaca dengan membandingkan cuplikan *seed* pada Subbab 3.2.2 dengan gambar penamaan objek tujuan pada Subbab 3.2.4. Tampilan alat pada Subbab 3.5.5 digunakan untuk menjelaskan cara membandingkan kode pada *database* dengan nama objek di lingkungan *Unity*, bukan untuk menyatakan bahwa seluruh pemetaan telah cocok.

Penulis merancang skema akhir 11 tabel, dua ERD, 10 *foreign key*, *constraint*, kebijakan RLS, data awal, serta pemetaan kode lokasi. Integrasi SQL ke repositori *web*, API, antarmuka Denah 2D, Supabase Auth, dan penulisan catatan audit melalui aplikasi ditangani *Full Stack Web Developer*, *System Integrator*, dan *DevOps Engineer*. Kode alat pemeriksa, *NavMesh*, algoritma pencarian rute, dan *Unity* saat dijalankan ditangani *3D Simulator* dan *Engine Developer*.

## 3.3 Konfigurasi dan Metadata

### 3.3.1 Struktur Database dan Relasi

Konfigurasi database menggunakan 10 *foreign key* untuk menjaga hubungan entitas dan batasan unik untuk menjaga identitas. Tiga relasi data kampus menghubungkan `fakultas.id_gedung_utama` serta `fasilitas.id_gedung` ke `gedung.id` dan `program_studi.id_fakultas` ke `fakultas.id`. Tujuh relasi Denah 2D menghubungkan node, edge, dan titik gedung ke `campus_maps`, `campus_map_nodes`, serta `gedung`. Aturan penghapusan menggunakan `ON DELETE CASCADE` atau `ON DELETE SET NULL` sesuai ketergantungan masing-masing. Field `unity_object_name` pada `gedung` serta `fasilitas` menjadi metadata integrasi ke Unity.

Struktur constraint yang terlihat pada [FIGREF:evidence_constraint_inventory] menampilkan baris hasil kueri katalog PostgreSQL. Bagian yang terlihat memuat contoh primary key, batasan unik, foreign key, dan aturan `ON DELETE`. Gambar ini hanya mendokumentasikan struktur yang tampak, bukan hasil percobaan memasukkan atau menghapus data yang melanggar aturan.

[FIGURE:evidence_constraint_inventory]
[FIGCAPTION:Inventaris Constraint Tabel Utama pada Supabase]

Berkas *setup* tidak dijalankan ulang karena memuat perintah penghapusan tabel. Oleh karena itu, DDL digunakan untuk menjelaskan rancangan seluruh struktur dan relasi, sedangkan gambar kueri katalog hanya menunjukkan sebagian *constraint* pada *database* aktif dan tidak dipakai untuk mengklaim bahwa setiap struktur telah diterapkan.

### 3.3.2 Konvensi Struktur Prefab dan Penamaan

Contoh struktur prefab dengan child `Pointer` dapat dilihat pada [FIGREF:impl_pointer_hierarchy].

[FIGURE:impl_pointer_hierarchy]
[FIGCAPTION:Hierarki Prefab Gedung dengan Child Pointer di Unity]

Validasi kecocokan nama dibantu oleh `DatabaseSyncChecker`, dengan antarmuka yang ditunjukkan pada [FIGREF:impl_sync_db_checker]. Alat ini mengambil daftar nama dari */api/unity/names*, menelusuri hierarki *scene*, dan mengelompokkan hasil yang cocok atau tidak cocok.

[FIGURE:impl_sync_db_checker]
[FIGCAPTION:Tampilan UI Database Sync Checker di Unity Editor]

Antarmuka pada [FIGREF:impl_sync_db_checker] menampilkan daftar nama yang sedang dibandingkan. Tangkapan ini digunakan untuk menjelaskan cara kerja alat, bukan untuk menyatakan perubahan atau kelulusan pemeriksaan.

### 3.3.3 Inventaris dan Metadata Asset 3D

Inventaris asset digunakan untuk menelusuri nama prefab, struktur objek, material atau tekstur, serta keterkaitannya dengan target navigasi. Pencatatan ini berfungsi sebagai dokumentasi keadaan asset dan tidak digunakan untuk menyatakan optimasi performa. Evaluasi performa runtime, occlusion culling, dan build WebGL menjadi bagian pekerjaan pengembang engine.

Versi editor yang terlihat pada [FIGREF:evidence_unity_version] adalah Unity 6.4 dengan identifier `6000.4.1f1_8535861f39e1`. Bukti ini menetapkan lingkungan yang terlihat ketika data dikumpulkan dan digunakan sebagai konteks untuk membaca metrik asset.

[FIGURE:evidence_unity_version]
[FIGCAPTION:Versi Unity yang Digunakan pada Pengukuran Asset]

Perangkat yang digunakan saat inventarisasi ditunjukkan pada [FIGREF:evidence_test_device]. Tangkapan tersebut memperlihatkan prosesor 13th Gen Intel(R) Core(TM) i7-13620H, RAM terpasang 32 GB, GPU NVIDIA GeForce RTX 4060 Laptop GPU 8 GB, dan sistem operasi 64-bit. Informasi ini hanya mencatat lingkungan pengambilan bukti dan bukan hasil pengujian performa asset.

[FIGURE:evidence_test_device]
[FIGCAPTION:Spesifikasi Perangkat Pengujian Asset]

Inventaris pada [FIGREF:evidence_prefab_sizes] menampilkan ukuran berkas prefab gedung beserta berkas `.meta` yang berukuran jauh lebih kecil. Nilai yang terbaca pada tiga berkas lama adalah 24,3 MB pada Ki Hajar Dewantara, 11,2 MB pada Dewi Sartika, dan 11,2 MB pada Jenderal Soedirman. Beberapa nama memiliki lebih dari satu versi berkas, sehingga ukuran tersebut digunakan sebagai nilai yang terlihat pada inventaris, bukan sebagai klaim bahwa seluruh prefab telah memiliki versi final yang sama.

[FIGURE:evidence_prefab_sizes]
[FIGCAPTION:Ukuran Berkas Prefab Gedung pada Inventaris Asset]

Inventaris berkas lingkungan terbaru pada [FIGREF:evidence_prefab_sizes_latest] melengkapi daftar ukuran prefab untuk Kantin, Lapangan Basket, Lapangan Upacara, Parkir Belakang, dan Parkir Depan. Berkas ini digunakan sebagai bukti ukuran file yang terlihat, bukan sebagai ukuran geometri atau klaim bahwa seluruh prefab berada pada versi final yang sama.

[FIGURE:evidence_prefab_sizes_latest]
[FIGCAPTION:Ukuran Berkas Prefab Lingkungan Terbaru]

Data inventaris yang terbaca dari 20 tangkapan Unity dirangkum pada [TABREF:metrik_tiga_aset]. Angka hanya menggambarkan objek yang dipilih ketika tangkapan dibuat dan tidak digunakan sebagai kriteria kelulusan atau perbandingan performa.

[TABLE-ID:metrik_tiga_aset]
[TABLECAPTION:Inventaris Teknis 20 Asset]

[TABLE]
Asset | GameObject | Mesh (instance/unik) | Vertex | Triangle | Material (slot/unik) | Collider | Ukuran prefab
Abdul Rahman Saleh | 1.890 | 1.293/397 | 971.455 | 1.126.321 | 2.440/34 | 1.131 | 7,26 MB
Cipto Mangunkusumo | 2.364 | 1.291/317 | 1.012.862 | 1.221.448 | 2.251/38 | 723 | 7,58 MB
Dewi Sartika | 477 | 371/279 | 124.973 | 60.980 | 433/15 | 352 | 11,2 MB
Jenderal Soedirman | 2.809 | 2.108/885 | 1.308.941 | 1.461.065 | 2.812/580 | 660 | 11,2 MB
Ki Hadjar Dewantara | 864 | 583/318 | 703.694 | 619.511 | 855/55 | 360 | 24,3 MB
Gedung Muhammad Yamin | 1.946 | 1.546/195 | 580.470 | 661.170 | 1.837/29 | 387 | 6,21 MB
Muh. Husni Thamrin | 1.973 | 1.329/363 | 9.472.541 | 16.101.941 | 2.379/51 | 915 | 10,5 MB
Gedung RA Kartini | 646 | 441/295 | 337.103 | 166.484 | 536/17 | 380 | 19,1 MB
Soepomo | 816 | 519/116 | 461.934 | 559.201 | 911/26 | 355 | 3,06 MB
Soetomo | 327 | 183/142 | 83.218 | 91.846 | 245/36 | 156 | 2,16 MB
Gedung Kuliah dan Kegiatan Mahasiswa | 66 | 42/32 | 11.711 | 5.128 | 48/9 | 42 | 3,20 MB
Wahidin Sudiro Husodo | 2.822 | 2.051/683 | 8.805.239 | 5.338.400 | 3.345/47 | 1.212 | 14,7 MB
Yos Sudarso | 2.071 | 1.375/473 | 1.177.433 | 1.467.504 | 2.739/54 | 1.039 | 7,93 MB
Kantin | 336 | 294/271 | 83.914 | 41.108 | 634/17 | 294 | 21.160 KB
Lapangan Upacara | 212 | 201/14 | 816.232 | 408.116 | 214/2 | 13 | 468 KB
Lapangan Basket | 162 | 156/24 | 503.853 | 252.428 | 185/9 | 42 | 1.451 KB
Masjid | 301 | 258/176 | 258.703 | 141.170 | 297/16 | 180 | 4,15 MB
Parkir Belakang UPNVJ | 42 | 39/29 | 20.375 | 9.372 | 65/10 | 39 | 5.592 KB
Parkir Depan UPNVJ | 556 | 444/350 | 744.482 | 376.388 | 455/14 | 348 | 89.222 KB
Parkir Hukum | 69 | 61/61 | 21.680 | 11.072 | 71/8 | 61 | 9.400 KB
[/TABLE]

Tiga gambar pengukuran dipilih sebagai contoh perwakilan pada BAB III, yaitu [FIGREF:evidence_metrics_dewi] untuk Gedung Dewi Sartika, [FIGREF:evidence_metrics_ki_hadjar] untuk Gedung Ki Hadjar Dewantara, dan [FIGREF:evidence_metrics_jenderal] untuk Gedung Jenderal Soedirman. Ketiga gambar tersebut menunjukkan cara membaca jumlah *GameObject*, *mesh*, *vertex*, *triangle*, material, *collider*, dan ukuran *prefab*. Tujuh belas gambar pengukuran lainnya dipindahkan ke Lampiran 3 agar BAB III tetap berfokus pada contoh utama, sedangkan 19 *asset* gedung dan satu *asset* fasilitas Masjid tetap tercatat pada tabel inventaris.

Jumlah objek dan vertex pada setiap asset berbeda karena cakupan geometri, material, dan fasilitas yang dipilih tidak sama. Perbedaan tersebut diperlakukan sebagai inventaris keadaan asset, bukan sebagai peringkat kualitas atau hasil pengujian performa.

[FIGURE:evidence_metrics_dewi]
[FIGCAPTION:Hasil Pengukuran GameObject, Mesh, dan Vertex Dewi Sartika]
[FIGURE:evidence_metrics_ki_hadjar]
[FIGCAPTION:Hasil Pengukuran GameObject, Mesh, dan Vertex Ki Hajar Dewantara]
[FIGURE:evidence_metrics_jenderal]
[FIGCAPTION:Hasil Pengukuran GameObject, Mesh, dan Vertex Jenderal Soedirman]

Inventaris awal memuat 37 berkas gambar material dan tekstur. Pemeriksaan otomatis menunjukkan seluruh 37 berkas tersebut memiliki byte yang sama dengan berkas bernama sama pada proyek *Unity* sumber. Folder bukti kemudian memperoleh 32 berkas tambahan yang terdiri atas dua referensi tekstur permukaan, 21 referensi warna polos, satu berkas logo Mandiri, lima berkas model atau tekstur alat olahraga, satu berkas warna patung, `kaca.jpg`, dan `material_warna_besi.png`. Berdasarkan konfirmasi penulis, ke-21 referensi warna digunakan pada material *Unity* dan dua referensi tekstur permukaan diterapkan pada Gedung Utama/Jenderal Soedirman. Logo Mandiri digunakan pada *asset* gedung bank yang ditempatkan sebagai pelengkap visual lingkungan aktual dan tidak memiliki record pada *database*. Lima berkas `model1_alat_olahraga.png` sampai `model5_alat_olahraga.png` digunakan pada objek alat olahraga di depan Gedung Dewi Sartika, sedangkan `warna_patung.png` digunakan pada *asset* patung. Material kaca jendela interior dan material tulisan nama gedung dibuat langsung di *Unity* sehingga tidak tersedia sebagai berkas PNG. Oleh karena itu, `kaca.jpg` yang diperoleh dari internet digunakan hanya sebagai interpretasi visual material kaca jendela interior, sedangkan `material_warna_besi.png` yang diperoleh dari internet digunakan hanya sebagai interpretasi visual material tulisan nama gedung. Keduanya tidak ditampilkan secara eksplisit pada gambar implementasi dan tidak diperlakukan sebagai berkas tekstur yang diterapkan langsung pada proyek. Dengan demikian, jumlah seluruh berkas pada folder menjadi 69, sedangkan klaim kecocokan byte dengan proyek sumber tetap dibatasi pada 37 berkas awal. Pengelompokan bukti dirangkum pada [TABREF:inventaris_material_tekstur].

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
Referensi interpretasi material Unity | 2 | `kaca.jpg` untuk kaca jendela interior dan `material_warna_besi.png` untuk tulisan nama gedung; tidak ditampilkan secara eksplisit
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

Ketiga gambar tersebut dipilih sebagai contoh perwakilan penggunaan tekstur pada dinding, atap, dan lingkungan. Bukti tekstur jendela serta dua tekstur Gedung Utama/Jenderal Soedirman ditempatkan pada Lampiran 3 agar pembahasan utama tetap berfokus pada proses dan contoh penerapan material.

Dokumentasi *render* dan hierarki tersedia untuk 19 *asset* gedung dan satu *asset* fasilitas Masjid. BAB III menggunakan Gedung Jenderal Soedirman, Gedung Dewi Sartika, dan Gedung Ki Hadjar Dewantara sebagai contoh utama, sedangkan bukti *asset* lainnya ditempatkan pada Lampiran 3. Ukuran piksel tangkapan layar tidak digunakan untuk menilai kualitas atau tingkat detail *asset*.

Keberadaan berkas gambar belum memberikan informasi lengkap mengenai konfigurasi *Unity Material*, *shader*, nilai *tiling*, resolusi impor, dan pemetaan material terhadap setiap *asset*. Laporan mencatat bahwa 21 referensi warna digunakan pada material *Unity* dan dua referensi tekstur diterapkan pada Gedung Utama/Jenderal Soedirman. Logo Mandiri digunakan pada *asset* gedung bank pelengkap lingkungan, lima berkas alat olahraga digunakan pada objek di depan Gedung Dewi Sartika, dan warna patung digunakan pada *asset* patung. Berkas `kaca.jpg` dan `material_warna_besi.png` membantu menginterpretasikan tampilan material yang dibuat langsung di *Unity*. Pemetaan konfigurasi teknis hanya dicatat sebagai informasi material.

## 3.4 Laporan Implementasi Proyek

### 3.4.1 Logbook Implementasi Proyek

Logbook implementasi disusun sebagai rekap bulanan berdasarkan kegiatan dan artefak dokumentasi yang tersedia.

Rekap kegiatan dan bukti pada setiap periode disajikan pada [TABREF:logbook_implementasi].

[TABLE-ID:logbook_implementasi]
[TABLECAPTION:Logbook Implementasi Asset 3D dan Pengelolaan Data]

[TABLE]
Periode | Kegiatan | Hasil | Artefak yang Tersedia
Bulan 1 | Observasi, wawancara, pengambilan foto, dan identifikasi kebutuhan | Kebutuhan asset dan struktur data dirangkum | Notulensi wawancara, dokumen riset, dan foto referensi
Bulan 2 | Perancangan ERD, skema, dan pemodelan awal | Struktur database dan bentuk awal asset dirangkum | ERD, SQL setup, dan gambar proses Unity
Bulan 3 | Pemodelan, material, tekstur, prefab, dan pengisian seed | Asset serta data gedung atau fasilitas mulai disusun | Render asset, hierarki, inventaris material, dan seed SQL
Bulan 4 | Penyelesaian hierarki, `Pointer`, serta pemetaan nama | GameObject tujuan dan `unity_object_name` disusun | Hierarki prefab dan gambar nama objek Unity
Bulan 5 | Pemeriksaan constraint, asset, dan konsistensi nama | Catatan pemeriksaan disusun | Gambar constraint, metrik asset, dan `DatabaseSyncChecker`
Bulan 6 | Koreksi, pengujian akhir, dan penyusunan laporan | Bukti implementasi dan hasil pengujian dirangkum | Hasil Black Box, UAT, survei, dan dokumentasi final
[/TABLE]

Rekap ini menunjukkan hubungan antara kegiatan bulanan dan artefak dokumentasi yang digunakan dalam laporan.

### 3.4.2 Hasil dan Bukti Implementasi Asset 3D Gedung dan Fasilitas

Bukti implementasi terdiri atas *render* dan tangkapan hierarki untuk 19 *asset* gedung serta satu *asset* fasilitas Masjid. Tiga pasangan gambar pada BAB III digunakan untuk menjelaskan pola pembuatan dan penataan objek, sedangkan bukti untuk *asset* lainnya disajikan pada Lampiran 3.

Representasi Gedung Jenderal Soedirman ditampilkan pada [FIGREF:evidence_asset_jenderal], sedangkan susunan objeknya ditampilkan pada [FIGREF:evidence_hierarchy_jenderal]. Render memperlihatkan bentuk utama gedung, susunan jendela, dan bagian masuk. Hierarki memperlihatkan pemisahan objek gedung dan titik tujuan tanpa digunakan untuk menyatakan ketelitian ukuran arsitektural.

[FIGURE:evidence_asset_jenderal]
[FIGCAPTION:Asset 3D Gedung Jenderal Soedirman]

[FIGURE:evidence_hierarchy_jenderal]
[FIGCAPTION:Hierarki Asset Gedung Jenderal Soedirman]

Representasi Gedung Ki Hadjar Dewantara ditampilkan pada [FIGREF:evidence_asset_ki_hadjar], sedangkan susunan objeknya ditampilkan pada [FIGREF:evidence_hierarchy_ki_hadjar]. Render memperlihatkan susunan lantai dan bentuk luar gedung. Hierarki menunjukkan pengelompokan objek yang digunakan untuk menyusun asset.

[FIGURE:evidence_asset_ki_hadjar]
[FIGCAPTION:Asset 3D Gedung Ki Hadjar Dewantara]

[FIGURE:evidence_hierarchy_ki_hadjar]
[FIGCAPTION:Hierarki Asset Gedung Ki Hadjar Dewantara]

Contoh representasi Gedung Dewi Sartika ditampilkan pada [FIGREF:evidence_asset_dewi]. Hierarki pada [FIGREF:evidence_hierarchy_dewi] memperlihatkan objek `CullingPoint`, child `Pointer`, dan objek tujuan `dewi_sartika`. Ketiga contoh ini digunakan untuk menjelaskan pola umum penataan asset; bukti aset lain disajikan pada Lampiran 3.

[FIGURE:evidence_asset_dewi]
[FIGCAPTION:Asset 3D Gedung Dewi Sartika]

[FIGURE:evidence_hierarchy_dewi]
[FIGCAPTION:Hierarki Asset Gedung Dewi Sartika]

Ketiga pasangan gambar tersebut memperlihatkan bentuk luar bangunan, pembagian objek, dan penempatan titik tujuan sebagai pola umum penataan *asset*. Bukti rinci untuk *asset* lain ditempatkan pada Lampiran 3 agar pembahasan BAB III tetap berfokus pada proses dan hasil utama.

### 3.4.3 Hasil dan Bukti Rancangan Skema serta Pengelolaan Data

Bukti database yang terdapat dalam repository laporan dirangkum pada [TABREF:status_bukti_basis_data]. Ringkasan ini difokuskan pada skema dan ERD yang dirancang penulis, pengelolaan record gedung atau fasilitas, serta pemetaan `unity_object_name`.

[TABLE-ID:status_bukti_basis_data]
[TABLECAPTION:Status Bukti Rancangan Skema dan Pengelolaan Data]

[TABLE]
Komponen | Bukti Tersedia | Informasi yang Ditampilkan | Cakupan Uraian
ERD lengkap | Dua gambar ERD pada Subbab 2.3.5 dan dua sumber PlantUML | Seluruh 11 tabel, 10 *foreign key*, *constraint* utama, *nullability*, aksi penghapusan, serta hubungan akses logis administrator | Garis akses logis dibedakan dari *foreign key*; `audit_logs.actor_id` tetap berupa UUID biasa
Struktur data, *constraint*, dan RLS | Berkas *setup*, representasi DDL pada Subbab 3.2.2, serta inventaris *constraint* pada Subbab 3.3.1 | *Primary key*, *unique constraint*, 10 *foreign key*, aturan penghapusan, dan kebijakan RLS pada 11 tabel | Berkas *setup* tidak dijalankan saat penyusunan laporan sehingga tidak membuktikan kondisi produksi terkini
Pengelolaan *record* | Contoh nilai `unity_object_name` gedung dan fasilitas serta inventaris *seed* 311 *record* | Kolom, contoh *identifier*, dan jumlah fasilitas per induk | Isi *seed* yang dikelola dalam proyek
Pemetaan *asset*–data | Hierarki *prefab* serta tampilan `DatabaseSyncChecker` pada Subbab 3.3.2 dan 3.5.5 | Cara *identifier* dibandingkan dengan nama *GameObject* tujuan | Proses pemeriksaan nama tanpa klaim kecocokan akhir
[/TABLE]

*Seed* final memuat 19 *record* pada tabel `gedung` dan 311 *record* pada tabel `fasilitas`. Sebelas kelompok induk yang mempunyai *record* fasilitas diringkas pada [TABREF:inventaris_seed_fasilitas]. Kolom cakupan pada tabel hanya menampilkan rentang lantai gedung, sedangkan narasi kualitas data memisahkan Masjid sebagai fasilitas dengan `id_gedung = 6` dan kode `masjid`.

[TABLE-ID:inventaris_seed_fasilitas]
[TABLECAPTION:Ringkasan Inventaris Fasilitas pada Seed Data]

[TABLE]
Referensi Seed | Induk Fasilitas | Jumlah Record | Cakupan Lantai
1 | Gedung Rektorat (jenderal soedirman) | 36 | Lantai 1–4
2 | Gedung DR. Soepomo | 24 | Lantai 1–4
3 | Gedung Dr. Wahidin Sudiro Husodo | 38 | Lantai 1–4
4 | Gedung Dr. Cipto Mangunkusumo | 38 | Lantai 1–4
5 | Gedung Abdul Rahman Saleh | 25 | Lantai 1–4
6 | Gedung Ki Hadjar Dewantara | 25 | Lantai 1–4
7 | Gedung Muh. Husni Thamrin | 37 | Lantai 1–4
8 | Gedung Muhammad Yamin | 20 | Lantai 1–4
10 | Gedung RA Kartini | 24 | Lantai 1–4
13 | Gedung Dewi Sartika | 26 | Lantai 1–4
17 | Gedung Soetomo | 18 | Lantai 1–4
Total | Kelompok induk yang tercantum dalam seed | 311 | —
[/TABLE]

Pemeriksaan terhadap daftar tersebut menghasilkan catatan kualitas data yang dirangkum pada [TABREF:temuan_kualitas_seed_fasilitas]. Catatan tersebut membedakan fakta pada seed terbaru dari informasi yang belum menjadi bagian laporan.

[TABLE-ID:temuan_kualitas_seed_fasilitas]
[TABLECAPTION:Temuan Awal Kualitas Data pada Inventaris Fasilitas]

[TABLE]
Temuan | Bukti pada Inventaris | Dampak | Tindak Lanjut
Pemetaan Masjid | Masjid merupakan asset visual terpisah, sedangkan record fasilitasnya menggunakan `id_gedung = 6` | Nama asset visual dan induk database dapat berbeda bila tidak dicatat secara eksplisit | Pertahankan catatan pemetaan asset visual–record pada inventaris dan pengujian
Pemisahan entitas gedung | Gedung Soepomo, Gedung Soetomo, Yos Sudarso, RA Kartini, Lapangan Basket, parkir, lapangan, dan entitas lain dicatat sebagai record gedung yang berbeda; `id_gedung = 17` adalah Gedung Soetomo pada seed terbaru | Penyamaan nama atau fungsi dapat menghasilkan pemetaan yang salah | Cocokkan nama record gedung dengan GameObject dan data fasilitas pada saat sinkronisasi
Kemutakhiran nama | Pengumpulan lapangan dilakukan mandiri dengan informasi ruangan yang terbatas | Nama atau fungsi ruang dapat berbeda dari kondisi terbaru | Catat perubahan apabila informasi terbaru tersedia
[/TABLE]

Kontribusi penulis pada bagian database adalah perancangan skema 11 tabel, dua ERD, 10 *foreign key*, *constraint*, kebijakan RLS, pengelolaan record gedung atau fasilitas, serta pemetaan `unity_object_name`. Supabase Auth, penulisan catatan audit melalui layanan aplikasi, API, serta Dashboard diatribusikan sebagai implementasi *Full Stack Web Developer*, *System Integrator*, dan *DevOps Engineer*. Uraian ini berfokus pada rancangan struktur, relasi, dan kualitas *seed*, bukan penerapan SQL pada database produksi atau *trigger* audit.

## 3.5 Hasil Pengujian Proyek

### 3.5.1 Pengujian Fungsional Bersama

<!-- PIPELINE:INCLUDE content/shared/testing/blackbox.md -->

### 3.5.2 Pengujian Integritas dan Relasi Database

Pemeriksaan integritas menjelaskan 10 *foreign key*, kolom wajib, batasan unik, aksi penghapusan, dan hubungan antar-*record*. *Constraint* seperti `NOT NULL`, `UNIQUE`, dan `FOREIGN KEY` membantu mencegah penyimpanan data yang tidak sesuai (PostgreSQL Global Development Group 2026a). Dalam laporan ini, artefak SQL lengkap digunakan untuk memeriksa struktur seluruh relasi, sedangkan gambar kueri katalog dan berkas *seed* menunjukkan sebagian struktur serta isi data yang tersedia.

Pembuktian isi dan hubungan data dilakukan dengan perintah `SELECT` yang hanya membaca data tanpa mengubah *record*. Kueri pertama menggabungkan `gedung.id` dengan `fasilitas.id_gedung` dan membatasi hasil pada Gedung Dewi Sartika.

```sql
SELECT
    g.id AS id_gedung,
    g.nama_gedung,
    g.unity_object_name AS kode_gedung,
    f.id AS id_fasilitas,
    f.nama_fasilitas,
    f.lantai,
    f.unity_object_name AS kode_fasilitas
FROM public.gedung AS g
LEFT JOIN public.fasilitas AS f
    ON f.id_gedung = g.id
WHERE g.nama_gedung = 'Gedung Dewi Sartika'
ORDER BY f.lantai, f.nama_fasilitas;
```

Bagian hasil kueri yang terlihat pada [FIGREF:evidence_select_dewi_facilities] menampilkan `id_gedung = 13` secara konsisten pada delapan baris fasilitas yang tampak. Hasil tersebut juga memperlihatkan kode gedung `dewi_sartika` dan kode fasilitas yang berbeda, antara lain `ds_lapangan`, `ds_bem`, dan `ds_senat`. Bukti ini menunjukkan bahwa fasilitas dapat ditelusuri ke gedung induknya melalui kolom penghubung, tanpa digunakan untuk menyatakan bahwa tangkapan layar memuat seluruh fasilitas Dewi Sartika.

[FIGURE:evidence_select_dewi_facilities]
[FIGCAPTION:Hasil SELECT Relasi Gedung Dewi Sartika dengan Fasilitas]

Relasi fakultas, program studi, dan gedung utama dapat diperiksa dengan kueri baca berikut. Hasilnya memperlihatkan rantai `program_studi.id_fakultas` ke `fakultas.id` dan `fakultas.id_gedung_utama` ke `gedung.id`.

```sql
SELECT
    fa.id AS id_fakultas,
    fa.nama_fakultas,
    g.nama_gedung AS gedung_utama,
    ps.id AS id_program_studi,
    ps.nama_prodi,
    ps.jenjang
FROM public.fakultas AS fa
LEFT JOIN public.gedung AS g
    ON g.id = fa.id_gedung_utama
LEFT JOIN public.program_studi AS ps
    ON ps.id_fakultas = fa.id
ORDER BY fa.nama_fakultas, ps.nama_prodi;
```

Data administrator diperiksa tanpa menampilkan `password_hash`. Pembatasan kolom tersebut menjaga agar bukti laporan hanya memuat metadata yang diperlukan.

```sql
SELECT
    id,
    username,
    nama_lengkap,
    role,
    created_at
FROM public.admin_users
ORDER BY id;
```

Matriks cakupan integritas dirangkum pada [TABREF:hasil_uji_integritas_db].

[TABLE-ID:hasil_uji_integritas_db]
[TABLECAPTION:Dokumentasi Integritas dan Relasi Database]

[TABLE]
Cakupan | Artefak yang Digunakan | Informasi yang Ditampilkan | Hubungan dengan Laporan
Struktur *constraint* | Artefak SQL lengkap dan gambar kueri katalog pada tabel utama | DDL mendefinisikan 10 *foreign key*; gambar katalog memperlihatkan contoh *primary key*, *unique constraint*, *foreign key*, dan aturan `ON DELETE SET NULL` | Memisahkan verifikasi struktur SQL dari bukti sebagian kondisi database aktif
Pemetaan Masjid | Berkas *seed* fasilitas | Masjid dicatat sebagai fasilitas dengan `id_gedung = 6` dan kode `masjid` | Memisahkan *asset* fasilitas dari 19 entitas gedung
Pemetaan Gedung Soetomo | Berkas *seed* gedung | `id_gedung = 17` digunakan untuk Gedung Soetomo dan terpisah dari Lapangan Basket | Menjaga nama gedung sesuai data yang digunakan
[/TABLE]

### 3.5.3 Konteks Akses Data dan Pencatatan Audit

Skenario database pada [TABREF:hasil_black_box] digunakan sebagai konteks penggunaan record yang dikelola penulis. Bagian ini mengatribusikan rancangan kebijakan RLS kepada penulis, tetapi membedakannya dari implementasi Supabase Auth dan penulisan catatan audit melalui aplikasi oleh *Full Stack Web Developer*, *System Integrator*, dan *DevOps Engineer*. Ringkasan konteks hasil bersama disajikan pada [TABREF:hasil_uji_rls_audit].

[TABLE-ID:hasil_uji_rls_audit]
[TABLECAPTION:Ringkasan Konteks Akses Data dan Pencatatan Audit]

[TABLE]
Skenario Sistem | Ringkasan Hasil Bersama | Sumber Ringkasan | Relevansi terhadap Pekerjaan Penulis
Pembacaan data publik | Akses baca data berjalan | Hasil *Black Box Testing* bersama | *Record* gedung atau fasilitas dapat digunakan sistem
Penolakan operasi anonim | Operasi tanpa autentikasi ditolak | Hasil *Black Box Testing* bersama | Perubahan *record* dilakukan melalui jalur terautentikasi
Pengelolaan data terautentikasi | Fungsi pengelolaan data berjalan | Hasil *Black Box Testing* bersama | Penulis mengelola data melalui komponen sistem yang tersedia
Pencatatan perubahan | Operasi pengelolaan data dicatat oleh layanan aplikasi | Hasil *Black Box Testing* bersama | Implementasi layanan audit bukan kontribusi penulis
[/TABLE]

### 3.5.4 Pemeriksaan Visual dan Struktur Asset 3D

Pemeriksaan asset mencakup keterbandingan bentuk dengan referensi visual, keterbacaan material atau tekstur, struktur prefab, child `Pointer`, dan lokasi objek tujuan. Pemeriksaan tidak digunakan untuk menilai optimasi atau performa build karena aspek tersebut berada dalam scope pengembang engine.

Foto kondisi aktual, *render asset*, tangkapan hierarki, inventaris tekstur, ukuran *prefab*, dan pengukuran 19 *asset* gedung serta satu *asset* fasilitas digunakan sebagai bahan pemeriksaan. Gedung Jenderal Soedirman, Gedung Dewi Sartika, dan Gedung Ki Hadjar Dewantara menjadi contoh utama untuk melihat keterkaitan bentuk, material, susunan objek, dan titik tujuan. Pemeriksaan ini tidak menghasilkan status kelulusan untuk setiap *asset* karena bukti yang tersedia digunakan sebagai dokumentasi proses dan keadaan objek, bukan sebagai pengujian performa atau ketelitian ukuran.

### 3.5.5 Validasi Konsistensi Asset dan Database

Bagian ini menjelaskan cara membaca alat pemeriksa nama, bukan menyatakan hasil pemeriksaan akhir. Tampilan alat pada [FIGREF:impl_sync_db_checker] memperlihatkan daftar nama yang dibandingkan antara *database* dan *scene*. Alat tersebut dikembangkan oleh *3D Simulator* dan *Engine Developer*, sedangkan penulis menggunakannya sebagai bantuan untuk menelusuri pemetaan `unity_object_name`.

### 3.5.6 User Acceptance Testing

<!-- PIPELINE:INCLUDE content/shared/testing/uat.md -->

### 3.5.7 Implementasi Hasil User Acceptance Testing

<!-- PIPELINE:INCLUDE content/shared/testing/uat-revisions.md -->

Denah 2D digunakan sebagai alternatif produk bersama pada UAT-R03 dan UAT-R07. Empat tabel `campus_map_*` masuk ke skema akhir setelah pengembangan dan tindak lanjut UAT, bukan sebagai kebutuhan awal. Perancangan tabel, *constraint*, relasi, dan kebijakan RLS diatribusikan kepada penulis, sedangkan pembuatan antarmuka, algoritma A\*, serta integrasi aplikasi ditangani anggota lain. Penulis tidak mengklaim pembuatan layanan Denah 2D atau algoritma pencarian rutenya.

Kontribusi yang relevan dengan peran *asset* dan pengelolaan data terutama berkaitan dengan nama dan deskripsi fasilitas, pemetaan objek, label ruang yang menggunakan nama tampilan, serta pemeriksaan kelengkapan data.

---

# BAB IV PENUTUP

## 4.1 Kesimpulan

Kesimpulan berikut menjawab tiga identifikasi masalah dan tujuan pada BAB I dalam urutan yang sama:

1. Masalah kebutuhan representasi lokasi dijawab sesuai tujuan pertama melalui pembuatan serta penataan 19 *asset* gedung dan satu *asset* fasilitas Masjid. Proses prototipe mencakup observasi visual dan foto, pembuatan bentuk awal, penerapan material atau tekstur, pengelompokan objek, pembuatan kelompok titik tujuan, dan penyimpanan *prefab*. Hasilnya menyediakan representasi yang dapat digunakan pada denah virtual, tetapi tidak dinyatakan sebagai model dengan ukuran arsitektural karena tidak dilakukan pengukuran menggunakan alat ukur.
2. Masalah keteraturan dan pembaruan data dijawab sesuai tujuan kedua melalui skema akhir 11 tabel yang didokumentasikan dalam dua ERD, dilengkapi 10 *foreign key*, kolom wajib, aturan nilai unik, aksi penghapusan, serta kebijakan RLS. Alur CRUD administrator dimodelkan melalui *use case* dan *activity diagram*, sedangkan hubungan akses logis dari `admin_users` ke tabel data dibedakan dari relasi fisik. Data awal yang dikelola memuat 19 entitas gedung dan 311 fasilitas, dan hasil `SELECT` pada Gedung Dewi Sartika memperlihatkan hubungan `gedung.id` dengan `fasilitas.id_gedung`. Supabase Auth, penerapan SQL pada database produksi, dan penulisan catatan audit melalui aplikasi tetap berada di luar implementasi penulis; berkas SQL tidak memuat definisi *trigger* audit.
3. Masalah hubungan antara data dan objek tiga dimensi dijawab dengan menerapkan kode lokasi yang sama pada data gedung atau fasilitas dan objek tujuan di *Unity*. Penulis menyusun kelompok titik tujuan, menetapkan kode, dan menggunakan alat pemeriksa milik pengembang *engine* untuk menelusuri nama yang perlu diperiksa. Proses tersebut membuat hubungan data dan objek lebih mudah diperiksa, tetapi bukti yang tersedia belum digunakan untuk menyatakan bahwa seluruh pemetaan telah cocok.

Pada tingkat produk bersama, pengujian fungsional akhir menghasilkan 24 dari 24 skenario lulus dan UAT memperoleh nilai gabungan 81,50 persen. Angka tersebut menilai sistem secara keseluruhan dan tidak digunakan sebagai hasil khusus pembuatan *asset* atau perancangan data oleh penulis.

## 4.2 Saran

Saran pengembangan awal adalah sebagai berikut:

1. Menyimpan ERD, kamus data, dan catatan perubahan skema dengan versi yang dapat ditelusuri agar keputusan perancangan dapat direplikasi.
2. Menambahkan validasi format dan keunikan `unity_object_name` pada form administrator serta pada pipeline integrasi sebelum build.
3. Menetapkan checklist asset yang mencakup keterbandingan bentuk, struktur prefab, child `Pointer`, material atau tekstur, serta posisi dan nama objek tujuan.
4. Menggunakan `DatabaseSyncChecker` buatan *3D Simulator* dan *Engine Developer* sebagai alat bantu ketika terdapat perubahan data gedung, fasilitas, atau hierarki *scene*.
5. Melengkapi dokumentasi perubahan data dan asset apabila bukti tersebut tersedia pada folder laporan.

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

Unity Technologies (2026c). _Unity 6 Manual: Materials_. https://docs.unity3d.com/6000.0/Documentation/Manual/Materials.html

Unity Technologies (2026d). _Unity 6 Manual: Collider 2D component reference_. https://docs.unity3d.com/6000.0/Documentation/Manual/Collider2D.html

UPNVJ. (2022). Lokasi Kampus UPN Veteran Jakarta. https://www.upnvj.ac.id/id/tentang-upn/lokasi-kampus.html

UPNVJ. (2025b). Sejarah UPN Veteran Jakarta. https://www.upnvj.ac.id/id/tentang-upn/sejarah.html

UPNVJ. (2025a). Kantin. https://www.upnvj.ac.id/id/fasilitas/kantin.html

UPNVJ. (2026). Rapat koordinasi Humas UPNVJ 2026: Fokus strategi komunikasi digital dan media sosial perguruan tinggi. https://www.upnvj.ac.id/id/berita/2026/02/rapat-koordinasi-humas-upnvj-2026-fokus-strategi-komunikasi-digital-dan-media-sosial-perguruan-tinggi.html

Vercel (2026). _Vercel Functions_. https://vercel.com/docs/functions

Wayahdi, M. R., dan Ruziq, F. (2023). Pemodelan sistem penerimaan anggota baru dengan Unified Modeling Language (UML) (Studi kasus: Programmer Association of Battuta). *Jurnal Minfo Polgan*, 12(1), 1514â€“1521. https://doi.org/10.33395/jmp.v12i1.12870

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

1. Tiga puluh berkas referensi visual tersedia pada folder bukti dan digunakan pada inventaris dokumentasi kondisi gedung serta fasilitas.
2. Tiga puluh tujuh berkas material dan tekstur cocok dengan berkas pada proyek *Unity* sumber, ditambah 32 berkas yang terdiri atas dua tekstur Gedung Utama/Jenderal Soedirman, 21 referensi warna material, logo Mandiri untuk *asset* gedung bank pelengkap lingkungan, lima berkas alat olahraga di depan Gedung Dewi Sartika, satu berkas warna *asset* patung, serta dua referensi interpretasi berupa `kaca.jpg` untuk kaca jendela interior dan `material_warna_besi.png` untuk tulisan nama gedung.
3. Dua puluh pasangan render–hierarki yang terdiri atas 19 aset gedung dan satu aset fasilitas Masjid. Tiga pasangan representatif berada di BAB III dan 17 pasangan lainnya dimuat pada lampiran ini.
4. Satu tangkapan versi Unity 6.4.
5. Satu tangkapan spesifikasi perangkat yang digunakan saat inventarisasi.
6. Satu inventaris ukuran prefab.
7. Dua puluh tangkapan pengukuran *GameObject*, *mesh*, *vertex*, *triangle*, material, *collider*, dan ukuran *prefab* untuk *asset* yang tercantum pada inventaris teknis.

Bukti foto digunakan untuk menunjukkan referensi visual. Berkas `kaca.jpg` serta `material_warna_besi.png` diperlakukan sebagai interpretasi tampilan material yang dibuat langsung di *Unity*, bukan sebagai tekstur yang diterapkan secara langsung. Parkir Belakang memiliki foto referensi, *render asset*, tangkapan hierarki, metrik, dan ukuran *prefab* pada folder bukti.

Bukti material tambahan yang tidak ditampilkan pada BAB III mencakup tekstur jendela dan dua tekstur Gedung Utama/Jenderal Soedirman. Tekstur jendela ditampilkan pada [FIGREF:evidence_material_window], sedangkan dua tekstur lobi ditampilkan pada [FIGREF:evidence_material_lobby_rektorat] dan [FIGREF:evidence_material_tembok_lobby]. Berdasarkan konfirmasi penulis, kedua tekstur lobi diterapkan pada Gedung Utama/Jenderal Soedirman, tetapi bukti yang tersedia tidak merinci pembagian penggunaannya pada setiap objek.

[FIGURE:evidence_material_window]
[FIGCAPTION:Contoh Tekstur Jendela]

[FIGURE:evidence_material_lobby_rektorat]
[FIGCAPTION:Berkas Referensi Tekstur Lobi Utama Gedung Rektorat]

[FIGURE:evidence_material_tembok_lobby]
[FIGCAPTION:Berkas Referensi Tekstur Tembok Lobi Gedung Utama]

Foto referensi Parkir Belakang yang baru tersedia digunakan untuk melengkapi inventaris kondisi aktual melalui [FIGREF:evidence_photo_parkir_belakang]. Foto ini hanya menunjukkan tampilan visual yang tersedia pada berkas, tanpa klaim tanggal pengambilan, identitas pengambil gambar, atau ketelitian ukuran.

[FIGURE:evidence_photo_parkir_belakang]
[FIGCAPTION:Referensi Aktual Parkir Belakang]

Referensi visual Gedung Cipto Mangunkusumo ditampilkan pada [FIGREF:evidence_photo_cipto]. Foto digunakan untuk mendokumentasikan bentuk luar dan susunan lantai yang terlihat.

[FIGURE:evidence_photo_cipto]
[FIGCAPTION:Referensi Aktual Gedung Cipto Mangunkusumo]

Referensi visual Gedung Muhammad Yamin ditampilkan pada [FIGREF:evidence_photo_myamin]. Foto memperlihatkan bidang kaca, kanopi, dan panel warna pada bagian luar gedung.

[FIGURE:evidence_photo_myamin]
[FIGCAPTION:Referensi Aktual Gedung M. Yamin]

Referensi visual Gedung Wahidin Sudiro Husodo ditampilkan pada [FIGREF:evidence_photo_wahidin]. Foto memperlihatkan susunan lantai, bagian dinding berwarna gelap, dan pintu atau jendela yang terlihat.

[FIGURE:evidence_photo_wahidin]
[FIGCAPTION:Referensi Aktual Gedung Wahidin Sudiro Husodo]

Dokumentasi Parkir Belakang memperlihatkan hasil *render* melalui [FIGREF:evidence_asset_parkir_belakang], sedangkan susunan objeknya ditunjukkan pada [FIGREF:evidence_hierarchy_parkir_belakang]. *Render* memperlihatkan bidang dinding memanjang, akses berpagar, dan pos kecil pada bagian depan. Tangkapan hierarki memperlihatkan objek induk Parkir Belakang yang memuat `parkir_belakang`, `CullingPoint`, serta objek penyusun berbentuk kubus, tiang, dan pintu. Bukti tersebut digunakan untuk menunjukkan keberadaan bentuk dan struktur objek, bukan untuk menyatakan ketelitian ukuran atau kelulusan optimasi.

[FIGURE:evidence_asset_parkir_belakang]
[FIGCAPTION:Asset 3D Parkir Belakang]

[FIGURE:evidence_hierarchy_parkir_belakang]
[FIGCAPTION:Hierarki Asset Parkir Belakang]

Dokumentasi Abdul Rahman Saleh memperlihatkan hasil render melalui [FIGREF:evidence_asset_abdul_rahman], sedangkan susunan objeknya ditunjukkan pada [FIGREF:evidence_hierarchy_abdul_rahman].

[FIGURE:evidence_asset_abdul_rahman]
[FIGCAPTION:Asset 3D Gedung Abdul Rahman Saleh]

[FIGURE:evidence_hierarchy_abdul_rahman]
[FIGCAPTION:Hierarki Asset Gedung Abdul Rahman Saleh]

Dokumentasi Masjid memperlihatkan hasil render melalui [FIGREF:evidence_asset_masjid], sedangkan susunan objeknya ditunjukkan pada [FIGREF:evidence_hierarchy_masjid].

[FIGURE:evidence_asset_masjid]
[FIGCAPTION:Asset 3D Masjid]

[FIGURE:evidence_hierarchy_masjid]
[FIGCAPTION:Hierarki Asset Masjid]

Dokumentasi Muh. Husni Thamrin memperlihatkan hasil render melalui [FIGREF:evidence_asset_thamrin], sedangkan susunan objeknya ditunjukkan pada [FIGREF:evidence_hierarchy_thamrin].

[FIGURE:evidence_asset_thamrin]
[FIGCAPTION:Asset 3D Gedung Muh. Husni Thamrin]

[FIGURE:evidence_hierarchy_thamrin]
[FIGCAPTION:Hierarki Asset Gedung Muh. Husni Thamrin]

Dokumentasi R.A. Kartini memperlihatkan hasil render melalui [FIGREF:evidence_asset_kartini], sedangkan susunan objeknya ditunjukkan pada [FIGREF:evidence_hierarchy_kartini].

[FIGURE:evidence_asset_kartini]
[FIGCAPTION:Asset 3D Gedung R.A. Kartini]

[FIGURE:evidence_hierarchy_kartini]
[FIGCAPTION:Hierarki Asset Gedung R.A. Kartini]

Dokumentasi Soepomo memperlihatkan hasil render melalui [FIGREF:evidence_asset_soepomo], sedangkan susunan objeknya ditunjukkan pada [FIGREF:evidence_hierarchy_soepomo].

[FIGURE:evidence_asset_soepomo]
[FIGCAPTION:Asset 3D Gedung Soepomo]

[FIGURE:evidence_hierarchy_soepomo]
[FIGCAPTION:Hierarki Asset Gedung Soepomo]

Dokumentasi Soetomo memperlihatkan hasil render melalui [FIGREF:evidence_asset_soetomo], sedangkan susunan objeknya ditunjukkan pada [FIGREF:evidence_hierarchy_soetomo].

[FIGURE:evidence_asset_soetomo]
[FIGCAPTION:Asset 3D Gedung Soetomo]

[FIGURE:evidence_hierarchy_soetomo]
[FIGCAPTION:Hierarki Asset Gedung Soetomo]

Dokumentasi Gedung UKM memperlihatkan hasil render melalui [FIGREF:evidence_asset_ukm], sedangkan susunan objeknya ditunjukkan pada [FIGREF:evidence_hierarchy_ukm].

[FIGURE:evidence_asset_ukm]
[FIGCAPTION:Asset 3D Gedung UKM]

[FIGURE:evidence_hierarchy_ukm]
[FIGCAPTION:Hierarki Asset Gedung UKM]

Dokumentasi Yos Sudarso memperlihatkan hasil render melalui [FIGREF:evidence_asset_yos], sedangkan susunan objeknya ditunjukkan pada [FIGREF:evidence_hierarchy_yos].

[FIGURE:evidence_asset_yos]
[FIGCAPTION:Asset 3D Gedung Yos Sudarso]

[FIGURE:evidence_hierarchy_yos]
[FIGCAPTION:Hierarki Asset Gedung Yos Sudarso]

Dokumentasi Kantin memperlihatkan hasil render melalui [FIGREF:evidence_asset_kantin], sedangkan susunan objeknya ditunjukkan pada [FIGREF:evidence_hierarchy_kantin].

[FIGURE:evidence_asset_kantin]
[FIGCAPTION:Asset 3D Kantin]

[FIGURE:evidence_hierarchy_kantin]
[FIGCAPTION:Hierarki Asset Kantin]

Dokumentasi Lapangan Basket memperlihatkan hasil render melalui [FIGREF:evidence_asset_lapangan_basket], sedangkan susunan objeknya ditunjukkan pada [FIGREF:evidence_hierarchy_lapangan_basket].

[FIGURE:evidence_asset_lapangan_basket]
[FIGCAPTION:Asset 3D Lapangan Basket]

[FIGURE:evidence_hierarchy_lapangan_basket]
[FIGCAPTION:Hierarki Asset Lapangan Basket]

Dokumentasi Lapangan Upacara memperlihatkan hasil render melalui [FIGREF:evidence_asset_lapangan_upacara], sedangkan susunan objeknya ditunjukkan pada [FIGREF:evidence_hierarchy_lapangan_upacara].

[FIGURE:evidence_asset_lapangan_upacara]
[FIGCAPTION:Asset 3D Lapangan Upacara]

[FIGURE:evidence_hierarchy_lapangan_upacara]
[FIGCAPTION:Hierarki Asset Lapangan Upacara]

Dokumentasi Parkir Depan memperlihatkan hasil render melalui [FIGREF:evidence_asset_parkir_depan], sedangkan susunan objeknya ditunjukkan pada [FIGREF:evidence_hierarchy_parkir_depan].

[FIGURE:evidence_asset_parkir_depan]
[FIGCAPTION:Asset 3D Parkir Depan]

[FIGURE:evidence_hierarchy_parkir_depan]
[FIGCAPTION:Hierarki Asset Parkir Depan]

Dokumentasi Parkir Hukum memperlihatkan hasil render melalui [FIGREF:evidence_asset_parkir_hukum], sedangkan susunan objeknya ditunjukkan pada [FIGREF:evidence_hierarchy_parkir_hukum].

[FIGURE:evidence_asset_parkir_hukum]
[FIGCAPTION:Asset 3D Parkir Hukum]

[FIGURE:evidence_hierarchy_parkir_hukum]
[FIGCAPTION:Hierarki Asset Parkir Hukum]

Dokumentasi Gedung Cipto Mangunkusumo ditampilkan melalui [FIGREF:evidence_asset_cipto] dan [FIGREF:evidence_hierarchy_cipto]. Kedua gambar menunjukkan render serta pengelompokan objek yang tersedia.

[FIGURE:evidence_asset_cipto]
[FIGCAPTION:Asset 3D Gedung Cipto Mangunkusumo]

[FIGURE:evidence_hierarchy_cipto]
[FIGCAPTION:Hierarki Asset Gedung Cipto Mangunkusumo]

Dokumentasi Gedung M. Yamin ditampilkan melalui [FIGREF:evidence_asset_myamin] dan [FIGREF:evidence_hierarchy_myamin]. Kedua gambar menunjukkan render serta susunan objek yang tersedia.

[FIGURE:evidence_asset_myamin]
[FIGCAPTION:Asset 3D Gedung M. Yamin]

[FIGURE:evidence_hierarchy_myamin]
[FIGCAPTION:Hierarki Asset Gedung M. Yamin]

Dokumentasi Gedung Wahidin Sudiro Husodo ditampilkan melalui [FIGREF:evidence_asset_wahidin] dan [FIGREF:evidence_hierarchy_wahidin]. Kedua gambar menunjukkan render serta susunan objek yang tersedia.

[FIGURE:evidence_asset_wahidin]
[FIGCAPTION:Asset 3D Gedung Wahidin Sudiro Husodo]

[FIGURE:evidence_hierarchy_wahidin]
[FIGCAPTION:Hierarki Asset Gedung Wahidin Sudiro Husodo]

Tujuh belas tangkapan pengukuran yang tidak ditampilkan pada BAB III disajikan berikut sebagai bukti rinci inventaris teknis. Urutan gambar mengikuti daftar asset pada tabel inventaris dan setiap tangkapan dibaca sebagai dokumentasi keadaan objek saat pengukuran, bukan sebagai peringkat kualitas atau hasil pengujian performa.

Rincian tersebut berturut-turut dapat ditelusuri melalui [FIGREF:evidence_metrics_abdul_rahman], [FIGREF:evidence_metrics_cipto], [FIGREF:evidence_metrics_myamin], [FIGREF:evidence_metrics_thamrin], [FIGREF:evidence_metrics_kartini], [FIGREF:evidence_metrics_soepomo], [FIGREF:evidence_metrics_soetomo], [FIGREF:evidence_metrics_ukm], [FIGREF:evidence_metrics_wahidin], [FIGREF:evidence_metrics_yos], [FIGREF:evidence_metrics_kantin], [FIGREF:evidence_metrics_lapangan_upacara], [FIGREF:evidence_metrics_lapangan_basket], [FIGREF:evidence_metrics_masjid], [FIGREF:evidence_metrics_parkir_belakang], [FIGREF:evidence_metrics_parkir_depan], dan [FIGREF:evidence_metrics_parkir_hukum].

[FIGURE:evidence_metrics_abdul_rahman]
[FIGCAPTION:Hasil Pengukuran Asset Abdul Rahman Saleh]

[FIGURE:evidence_metrics_cipto]
[FIGCAPTION:Hasil Pengukuran Asset Cipto Mangunkusumo]

[FIGURE:evidence_metrics_myamin]
[FIGCAPTION:Hasil Pengukuran Asset M. Yamin]

[FIGURE:evidence_metrics_thamrin]
[FIGCAPTION:Hasil Pengukuran Asset Muh. Husni Thamrin]

[FIGURE:evidence_metrics_kartini]
[FIGCAPTION:Hasil Pengukuran Asset R.A. Kartini]

[FIGURE:evidence_metrics_soepomo]
[FIGCAPTION:Hasil Pengukuran Asset Soepomo]

[FIGURE:evidence_metrics_soetomo]
[FIGCAPTION:Hasil Pengukuran Asset Soetomo]

[FIGURE:evidence_metrics_ukm]
[FIGCAPTION:Hasil Pengukuran Asset UKM]

[FIGURE:evidence_metrics_wahidin]
[FIGCAPTION:Hasil Pengukuran Asset Wahidin Sudiro Husodo]

[FIGURE:evidence_metrics_yos]
[FIGCAPTION:Hasil Pengukuran Asset Yos Sudarso]

[FIGURE:evidence_metrics_kantin]
[FIGCAPTION:Hasil Pengukuran Asset Kantin]

[FIGURE:evidence_metrics_lapangan_upacara]
[FIGCAPTION:Hasil Pengukuran Asset Lapangan Upacara]

[FIGURE:evidence_metrics_lapangan_basket]
[FIGCAPTION:Hasil Pengukuran Asset Lapangan Basket]

[FIGURE:evidence_metrics_masjid]
[FIGCAPTION:Hasil Pengukuran Asset Masjid]

[FIGURE:evidence_metrics_parkir_belakang]
[FIGCAPTION:Hasil Pengukuran Asset Parkir Belakang]

[FIGURE:evidence_metrics_parkir_depan]
[FIGCAPTION:Hasil Pengukuran Asset Parkir Depan]

[FIGURE:evidence_metrics_parkir_hukum]
[FIGCAPTION:Hasil Pengukuran Asset Parkir Hukum]

---

# LAMPIRAN 4. Skema Database dan Bukti Pengelolaan Data

Bukti yang tersedia adalah dua ERD yang mencakup 11 tabel dan 10 *foreign key*, rancangan kebijakan RLS, DDL dokumentasi, inventaris *constraint*, contoh nilai `unity_object_name`, serta inventaris *seed* berisi 311 fasilitas pada 19 gedung. Salinan sumber disimpan sebagai `dokumentasi/sql/001_full_setup.sql` dan `dokumentasi/sql/002_seed_data.sql`. Kedua berkas tidak dijalankan saat menyusun laporan karena berkas *setup* memuat `DROP TABLE` dan berkas *seed* memuat `TRUNCATE ... RESTART IDENTITY CASCADE`. Badan laporan hanya menggunakan cuplikan struktur tabel, kebijakan akses, data Gedung Dewi Sartika, dan contoh fasilitas yang relevan. Definisi *trigger* audit tidak ditemukan pada kedua artefak, sehingga *trigger* tidak diklaim. Daftar rinci fasilitas per gedung dan lantai dimuat setelah paragraf ini. Supabase Auth dan penulisan catatan audit melalui aplikasi tetap berada pada kontribusi *Full Stack Web Developer*, *System Integrator*, dan *DevOps Engineer*.

<!-- PIPELINE:INCLUDE content/roles/dwikhi/facility-seed-inventory.md -->

---

# LAMPIRAN 5. Logbook dan Bukti Pengujian

Subbab 3.4.1 memuat rekap kegiatan bulanan dan artefak yang tersedia. Hasil *Black Box Testing* dan UAT bersama, survei, inventaris *constraint*, gambar `DatabaseSyncChecker`, serta inventaris teknis *asset* disajikan sebagai dokumentasi proyek.

Tampilan lain alat pemeriksa nama pada saat digunakan didokumentasikan melalui [FIGREF:evidence_sync_checker_lanjutan].

[FIGURE:evidence_sync_checker_lanjutan]
[FIGCAPTION:Hasil Pemeriksaan Lanjutan Konsistensi Nama Asset dan Database]

Tangkapan tersebut hanya digunakan untuk menunjukkan antarmuka alat dan tidak digunakan untuk menyatakan perubahan atau kelulusan pemeriksaan.

Instrumen UAT tertutup dan indeks bukti pengujian bersama disajikan setelah uraian ini. Instrumen tersebut merupakan bukti produk bersama dan tidak digunakan sebagai hasil pengujian teknis khusus asset atau database penulis.

<!-- PIPELINE:INCLUDE content/shared/testing/appendix-instruments.md -->
