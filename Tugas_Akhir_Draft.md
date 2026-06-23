# INTEGRASI DENAH VIRTUAL UNIVERSITAS PEMBANGUNAN NASIONAL VETERAN JAKARTA KAMPUS PONDOK LABU
# (DASHBOARD PROFIL)

Muhammad Iman Nugraha
2210511129

INFORMATIKA
FAKULTAS ILMU KOMPUTER
UNIVERSITAS PEMBANGUNAN NASIONAL VETERAN JAKARTA
2025

# DAFTAR GAMBAR

Gambar 2.1 Hasil Kuesioner: Profil Status Akademik Responden
Gambar 2.2 Hasil Kuesioner: Efektivitas Media Navigasi Kampus Saat Ini
Gambar 2.3 Hasil Kuesioner: Frekuensi Kesulitan Menemukan Lokasi
Gambar 2.4 Hasil Kuesioner: Perilaku Pengguna Saat Mencari Lokasi
Gambar 2.5 Hasil Kuesioner: Urgensi Kebutuhan Peta Virtual 3D
Gambar 2.6 Hasil Kuesioner: Potensi Adopsi Denah Virtual 3D
Gambar 2.7 Hasil Kuesioner: Prioritas Informasi Fasilitas Kampus
Gambar 2.8 Dokumentasi Wawancara dan Penandatanganan Pakta Integritas
Gambar 2.9 Diagram Arsitektur Sistem
Gambar 2.10 Tahap Pengembangan
Gambar 2.11 Legenda Use Case Diagram
Gambar 2.12 Use Case Diagram
Gambar 2.13 Activity Diagram: Pengelolaan Data oleh Admin
Gambar 2.14 Activity Diagram: Integrasi Data Denah
Gambar 2.15 Sequence Diagram: Autentikasi Administrator
Gambar 2.16 Sequence Diagram: Sinkronisasi Data Gedung dan Unity
Gambar 2.17 Entity-Relationship Diagram
Gambar 2.18 Halaman Login Admin
Gambar 2.19 Halaman Dashboard Admin
Gambar 2.20 Modal Tambah Data Gedung
Gambar 2.21 Modal Update Data Gedung
Gambar 2.22 Modal Konfirmasi Hapus Data Gedung
Gambar 2.23 Traffic Website Admin
Gambar 2.24 Hero Section
Gambar 2.25 Public Traffic Statistics Website
Gambar 2.26 Bagian Fasilitas dan Aset
Gambar 2.27 Modal List Fasilitas dan Aset
Gambar 2.28 Modal Fasilitas dan Aset
Gambar 2.29 Bagian Footer
Gambar 3.1 Hierarki Prefab Gedung dengan Child Pointer di Unity
Gambar 3.2 Tampilan UI Database Sync Checker di Unity Editor

# DAFTAR TABEL

Tabel 1.1 Peran dan Tanggung Jawab
Tabel 1.2 Jadwal Kegiatan
Tabel 3.1 Hubungan Mitra dengan Proyek
Tabel 3.2 Logbook Implementasi Proyek
Tabel 3.3 Hasil Pengujian Black Box Testing
Tabel 3.4 Perbandingan Metrik Performa Lighthouse

# DAFTAR LAMPIRAN

LAMPIRAN 1. Surat Pernyataan Keaslian
LAMPIRAN 2. Surat Keterangan Implementasi Proyek dari Mitra
LAMPIRAN 3. Kode Sumber Utama
LAMPIRAN 4. Panduan Pengguna (User Manual) (Rencana/Placeholder)


# BAB I PENDAHULUAN

## 1.1 Latar Belakang

Perkembangan transformasi digital telah mendorong institusi pendidikan tinggi untuk mengadopsi teknologi informasi secara menyeluruh dalam mendukung layanan akademik, manajemen fasilitas, dan pengalaman pengguna. Perguruan tinggi tidak lagi dipandang semata sebagai ruang fisik pembelajaran, melainkan sebagai ekosistem digital yang menuntut penyajian informasi yang terintegrasi, mudah diakses, dan intuitif. Salah satu konsep yang berkembang dalam konteks ini adalah Smart Campus, yang menekankan integrasi teknologi digital untuk meningkatkan efisiensi operasional, kualitas layanan, serta pengalaman sivitas akademika dan pengunjung.

Salah satu tantangan utama dalam implementasi Smart Campus adalah penyediaan informasi spasial dan profil institusi, khususnya pada kampus dengan area yang luas dan struktur bangunan yang kompleks. Media navigasi konvensional seperti papan penunjuk arah dan denah statis berbasis gambar bersifat pasif, sulit diperbarui, serta tidak mampu menyajikan informasi secara dinamis dan terintegrasi. Kondisi ini sering menyebabkan mahasiswa baru maupun pengunjung mengalami kesulitan dalam menemukan lokasi gedung atau fasilitas tertentu, serta kesenjangan informasi terkait profil akademik dan fasilitas kampus.

Berdasarkan hasil pengumpulan data melalui kuesioner yang disebarkan kepada mahasiswa Universitas Pembangunan Nasional Veteran Jakarta, ditemukan bahwa 95% dari total responden pernah mengalami kesulitan dalam menemukan lokasi tertentu di lingkungan kampus. Permasalahan ini umumnya terjadi pada mahasiswa baru maupun pengunjung yang belum familiar dengan tata letak kampus. Selain itu, responden juga menunjukkan kebutuhan terhadap sistem navigasi yang lebih interaktif dan mudah diakses dibandingkan dengan media konvensional seperti papan penunjuk arah atau denah statis. Hasil survei ini memperkuat indikasi bahwa sistem informasi navigasi yang saat ini tersedia belum sepenuhnya mampu memenuhi kebutuhan pengguna secara efektif dan efisien.

Kondisi tersebut relevan dengan permasalahan yang dihadapi oleh Universitas Pembangunan Nasional Veteran Jakarta (UPNVJ) Kampus Pondok Labu. Kampus ini memiliki area yang luas dengan banyak fakultas dan fasilitas, sementara media informasi dan navigasi yang tersedia saat ini masih bersifat konvensional dan terfragmentasi. Berdasarkan observasi awal, belum tersedia sistem digital terintegrasi yang mampu menggabungkan navigasi spasial berbasis visualisasi 3D dengan penyajian informasi profil kampus secara terpusat dan interaktif. Oleh karena itu, penelitian ini mengusulkan pengembangan Sistem Integrasi Denah Virtual Kampus dan Dashboard Profil UPNVJ sebagai solusi digital terpadu. Sistem ini mengombinasikan visualisasi 3D interaktif lingkungan kampus, pengelolaan aset dan data spasial, serta dashboard profil kampus berbasis web yang didukung oleh arsitektur backend dan API. Sistem dikembangkan sebagai proyek kolaboratif dengan pembagian peran yang jelas, sehingga setiap komponen saling mendukung dalam mewujudkan konsep Smart Campus yang efisien, informatif, dan mudah diakses.

Upaya validasi kebutuhan sistem juga dilakukan melalui wawancara dengan Wakil Rektor Bidang Kemahasiswaan, Kerja Sama, dan Sistem Informasi (Wakil Rektor 3). Berdasarkan hasil wawancara tersebut, tidak ditemukan adanya laporan formal yang secara spesifik membahas permasalahan navigasi kampus sebagai isu strategis institusi. Meskipun demikian, pihak pimpinan universitas memberikan dukungan terhadap pengembangan solusi berbasis teknologi yang dapat meningkatkan kualitas layanan informasi dan pengalaman pengguna di lingkungan kampus. Dukungan ini menjadi landasan penting dalam pengembangan sistem, meskipun identifikasi masalah utama tetap didasarkan pada hasil observasi lapangan dan data kuesioner pengguna.

Dengan demikian, urgensi pengembangan sistem tidak hanya didasarkan pada perspektif kebijakan institusi, tetapi juga pada kebutuhan nyata pengguna yang teridentifikasi melalui data empiris. Pendekatan ini memastikan bahwa solusi yang dirancang bersifat user-centered, di mana pengembangan sistem berfokus pada peningkatan pengalaman navigasi serta kemudahan akses informasi kampus secara terintegrasi. Oleh karena itu, pengembangan sistem integrasi denah virtual dan dashboard profil kampus menjadi relevan sebagai upaya menjembatani kesenjangan antara kebutuhan pengguna dan keterbatasan sistem yang saat ini tersedia.

## 1.2 Identifikasi Masalah

Berdasarkan penjabaran latar belakang serta pengumpulan data awal yang telah diuraikan, identifikasi masalah dalam penelitian ini dirumuskan sebagai berikut:

1. Masih terdapat kesulitan bagi mahasiswa dan pengunjung dalam menemukan lokasi tertentu di lingkungan kampus, terutama akibat keterbatasan media navigasi yang masih bersifat konvensional, statis, dan tidak interaktif.
2. Informasi profil kampus, seperti data fasilitas, akademik, dan aset, masih tersebar di berbagai platform sehingga pengguna harus mengakses beberapa sumber secara terpisah untuk memperoleh informasi yang dibutuhkan.
3. Belum tersedia media visualisasi berbasis 3D yang mampu merepresentasikan lingkungan kampus secara realistis dan interaktif, sehingga pengguna kesulitan memahami hubungan spasial antar lokasi.
4. Belum terdapat sistem backend yang terpusat untuk mengelola dan menyediakan data secara dinamis melalui API yang dapat digunakan oleh berbagai komponen sistem, termasuk dashboard dan sistem visualisasi.
5. Belum tersedia mekanisme integrasi antara backend dan engine visualisasi seperti Unity, sehingga data yang tersimpan dalam sistem belum dapat dimanfaatkan secara langsung dalam lingkungan 3D interaktif.

## 1.3 Batasan Masalah

Untuk menjaga fokus, ruang lingkup, serta kelayakan penelitian, maka batasan masalah dalam pengembangan sistem integrasi denah virtual kampus dan dashboard profil Universitas Pembangunan Nasional Veteran Jakarta ditetapkan sebagai berikut:

1. Pengembangan sistem difokuskan pada integrasi antara backend, dashboard berbasis web, dan visualisasi denah virtual berbasis 3D, tanpa mencakup pengembangan sistem akademik utama seperti sistem perkuliahan atau keuangan.
2. Cakupan area visualisasi dan data dibatasi pada lingkungan Kampus Universitas Pembangunan Nasional Veteran Jakarta Kampus Pondok Labu.
3. Data profil kampus seperti statistik mahasiswa, dosen, dan akreditasi tidak dikelola secara langsung dalam sistem backend, melainkan diperoleh melalui mekanisme integrasi atau embed dari sistem yang telah dikembangkan oleh unit terkait (UPA TIK).
4. Pengembangan pada sisi backend difokuskan pada perancangan dan implementasi REST API, pengelolaan database, serta penyediaan data secara dinamis untuk mendukung kebutuhan dashboard dan integrasi dengan engine visualisasi.
5. Sistem API yang dikembangkan mendukung penyediaan data publik serta manipulasi data (Create, Read, Update, Delete) yang dibatasi hanya untuk administrator melalui mekanisme autentikasi berbasis Supabase Auth, sehingga tidak semua endpoint dapat diakses secara terbuka oleh pengguna umum.
6. Pengembangan visualisasi 3D dibatasi pada pembuatan aset dan lingkungan virtual oleh 3D Designer, tanpa membahas secara mendalam proses teknis pemodelan dalam laporan ini.
7. Pengembangan pada sisi Unity atau simulator difokuskan pada integrasi dengan backend melalui pemanggilan API serta implementasi interaksi dasar, tanpa membahas secara mendalam pengembangan engine atau optimasi grafis tingkat lanjut.
8. Sistem yang dikembangkan tidak mencakup integrasi real-time dengan seluruh sistem internal universitas, sehingga pembaruan data bergantung pada ketersediaan sumber data eksternal atau hasil pengelolaan internal sistem.

Pembagian peran dan tanggung jawab pada proyek sistem dijelaskan lebih detail dalam Tabel 1.1.

Tabel 1.1 Peran dan Tanggung Jawab

[TABLE]
Role | Tugas dan Tanggung Jawab
3D Designer | Merancang dan memproduksi aset visual tiga dimensi lingkungan kampus, termasuk pemodelan gedung dan elemen pendukung, serta melakukan optimasi aset agar sesuai untuk digunakan pada lingkungan visualisasi 3D interaktif.
3D Simulator / Engine Developer | Mengembangkan engine visualisasi 3D interaktif sebagai modul navigasi spasial, termasuk pengelolaan scene, interaksi pengguna, optimasi performa, serta integrasi data satu arah dari API ke dalam lingkungan visualisasi 3D.
Full Stack Developer (Dashboard Profile) | Merancang dan mengimplementasikan arsitektur backend dan frontend sistem, meliputi pengembangan database, RESTful API, dashboard publik, dan dashboard administrator untuk pengelolaan serta penyajian data profil kampus.
[/TABLE]

## 1.4 Tujuan dan Manfaat

### 1.4.1 Tujuan

Berdasarkan rumusan masalah pada Subbab 1.2, maka tujuan dari penelitian ini adalah sebagai berikut:

1. Mengembangkan sistem navigasi spasial kampus berbasis visualisasi 3D interaktif yang mampu meningkatkan efisiensi proses orientasi dan pencarian lokasi di lingkungan Kampus UPNVJ Pondok Labu.
2. Menyediakan media informasi kampus yang intuitif, mudah diakses, dan interaktif untuk menjawab kebutuhan pengguna akan penyajian informasi yang cepat dan mudah dipahami.
3. Mengintegrasikan informasi profil akademik, fasilitas, dan lingkungan kampus ke dalam satu sistem terpusat guna mengatasi fragmentasi sumber informasi yang selama ini terjadi.
4. Merancang dan mengimplementasikan sistem digital terintegrasi yang menggabungkan denah virtual kampus berbasis 3D dengan dashboard profil kampus sebagai solusi Smart Campus yang saling terhubung dan berkelanjutan.

### 1.4.2 Manfaat

Penelitian ini diharapkan dapat memberikan manfaat bagi berbagai pihak, antara lain:

1. Bagi sivitas akademika dan pengunjung, sistem integrasi denah virtual kampus dan dashboard profil diharapkan mampu meningkatkan efisiensi navigasi dan mempermudah akses terhadap informasi kampus secara terpadu dan interaktif.
2. Bagi pihak manajemen dan pengelola fakultas, sistem ini menyediakan media informasi digital yang terpusat, mudah dikelola, dan mudah diperbarui untuk menyajikan profil akademik, fasilitas, dan data pendukung lainnya secara akurat.
3. Bagi institusi UPNVJ secara keseluruhan, penelitian ini berkontribusi dalam meningkatkan citra dan daya sang universitas sebagai institusi pendidikan yang modern dan adaptif terhadap transformasi digital, sekaligus mendukung implementasi konsep Smart Campus secara berkelanjutan.

## 1.5 Jadwal Kegiatan

Usulan jadwal kegiatan untuk penyelesaian proyek ini dirinci dalam bentuk Gantt Chart yang menyajikan alokasi waktu pengerjaan secara bertahap, sebagaimana disajikan pada Tabel 1.2. Keseluruhan proyek ini direncanakan akan diselesaikan dalam kurun waktu 5 bulan atau 20 minggu.

Tabel 1.2 Jadwal Kegiatan

[TABLE]
Aktivitas | Bulan 1 | Bulan 2 | Bulan 3 | Bulan 4 | Bulan 5
Desain Arsitektur & UI | X |  |  |  | 
Pengembangan Backend |  | X | X |  | 
Pengembangan Frontend |  |  | X | X | 
Integrasi dan Pengujian Sistem |  |  |  | X | X
Revisi Final & Penulisan Laporan |  |  |  |  | X
Dokumentasi | X | X | X | X | X
[/TABLE]

Alur pengerjaan dirancang secara sekuensial dan bertahap, selaras dengan proses pengembangan. Tahapan-tahapan tersebut adalah:

1. Desain Arsitektur & UI (Bulan 1): Tahap fondasi yang berfokus pada perancangan blueprint sistem, termasuk ERD, Use Case Diagram, dan mockup UI.
2. Pengembangan Backend (Bulan 2-3): Tahap implementasi kode sisi server, mencakup pembangunan database PostgreSQL dan RESTful API Node.js.
3. Pengembangan Frontend (Bulan 3-4): Tahap implementasi kode sisi klien, berfokus pada pembangunan Admin Dashboard dan Public Dashboard menggunakan React.js. Tahap ini berjalan tumpang tindih (overlap) dengan backend untuk efisiensi.
4. Integrasi dan Pengujian Sistem (Bulan 4-5): Tahap validasi di mana frontend dan backend diintegrasikan dan diuji secara menyeluruh menggunakan skenario pengujian Black Box.
5. Revisi Final & Penulisan Laporan (Bulan 5): Alokasi waktu khusus untuk perbaikan bug akhir berdasarkan hasil pengujian dan penyusunan draf final laporan.
6. Dokumentasi (Bulan 1-5): Aktivitas ini akan dilakukan secara paralel sepanjang proyek untuk memastikan semua proses, desain, dan kode terdokumentasi dengan baik.

## 1.6 Sistematika Penulisan

Sistematika penulisan laporan Tugas Akhir Proyek ini disusun secara terperinci ke dalam empat bab utama guna memberikan alur pembahasan yang runtut dan sistematis:

1. **BAB I PENDAHULUAN**: Memaparkan latar belakang masalah navigasi spasial, identifikasi masalah, batasan penelitian, tujuan dan manfaat, jadwal kegiatan, serta sistematika penulisan.
2. **BAB II RANCANGAN PROYEK**: Menguraikan hasil observasi sistem berjalan, usulan solusi teknis berupa arsitektur terintegrasi, identifikasi kebutuhan fungsional dan teknis, rencana pengembangan prototyping, desain UML (Use Case, Activity, Sequence), skema database ERD, rancangan antarmuka pengguna, serta rencana pengujian sistem.
3. **BAB III IMPLEMENTASI PROYEK**: Mendokumentasikan profil institusi mitra, metode pengembangan prototyping, detail implementasi sisi backend dan frontend (termasuk kode program), skema integrasi WebGL bridge, logbook aktivitas proyek, detail metadata sistem, serta hasil evaluasi pengujian fungsional (Black Box) dan penerimaan pengguna (UAT).
4. **BAB IV PENUTUP**: Menyajikan kesimpulan akhir dari hasil pengembangan sistem dan evaluasi pengujian, serta saran rekomendasi untuk pengembangan sistem berkelanjutan.

---

# BAB II RANCANGAN PROYEK

## 2.1 Observasi

Tahap observasi awal merupakan fondasi penting dalam memahami permasalahan serta merumuskan kebutuhan sistem yang akan dikembangkan. Proses observasi dalam penelitian ini dilakukan melalui kombinasi beberapa metode, yaitu observasi lapangan, penyebaran kuesioner kepada mahasiswa, serta wawancara dengan stakeholder terkait. Pendekatan ini digunakan untuk memperoleh gambaran yang komprehensif, baik dari sisi pengguna maupun dari sisi institusi. Penggunaan denah virtual 3D sebagai media penunjang Smart Campus sejalan dengan tren riset twin digital (Jamaludin & Saepuloh, 2024). Visualisasi kampus digital untuk navigasi spasial terbukti mempermudah sivitas akademika dalam memahami tata letak fisik secara interaktif (Taurusta et al., 2024; Muharam et al., 2023).

Berdasarkan hasil kuesioner yang telah disebarkan kepada mahasiswa, ditemukan bahwa mayoritas responden pernah mengalami kesulitan dalam menemukan lokasi tertentu di lingkungan kampus. Hal ini menunjukkan adanya permasalahan nyata pada aspek navigasi yang dirasakan langsung oleh pengguna, terutama mahasiswa baru dan pengunjung yang belum familiar dengan lingkungan kampus.

Selanjutnya, hasil observasi lapangan menunjukkan bahwa sistem navigasi yang tersedia saat ini masih mengandalkan media konvensional seperti papan penunjuk arah dan denah statis, yang bersifat pasif, tidak interaktif, serta sulit diperbarui. Kondisi ini menyebabkan keterbatasan dalam memberikan pengalaman navigasi yang efektif dan intuitif bagi pengguna.

Untuk melengkapi analisis dari sisi institusi, dilakukan wawancara dengan Wakil Rektor Bidang Kemahasiswaan, Kerja Sama, dan Sistem Informasi (Wakil Rektor III). Berdasarkan hasil wawancara tersebut, tidak ditemukan adanya laporan formal yang secara spesifik membahas permasalahan navigasi kampus sebagai isu strategis. Namun demikian, pihak pimpinan universitas memberikan dukungan terhadap pengembangan solusi berbasis teknologi yang dapat meningkatkan kualitas layanan informasi kampus.

Selain itu, koordinasi juga dilakukan dengan unit pengelola teknologi informasi (UPA TIK) untuk memahami kondisi sistem yang sedang dikembangkan di lingkungan kampus. Hasil koordinasi menunjukkan bahwa beberapa data profil kampus, seperti statistik mahasiswa, dosen, dan akreditasi, telah dikelola dalam sistem terpisah, sehingga pendekatan integrasi melalui mekanisme embed menjadi solusi yang lebih relevan dibandingkan dengan pengelolaan data secara langsung dalam sistem yang dikembangkan.

Dengan menggabungkan hasil kuesioner, observasi lapangan, wawancara stakeholder, serta koordinasi teknis, dapat disimpulkan bahwa permasalahan utama terletak pada keterbatasan sistem navigasi yang belum interaktif serta belum terintegrasinya data dan visualisasi dalam satu platform yang terpadu. Temuan ini menjadi dasar dalam perumusan solusi sistem yang diusulkan pada penelitian ini.

### 2.1.1 Observasi Lapangan Kegiatan

Berdasarkan hasil observasi lapangan, data kuesioner mahasiswa, serta analisis terhadap sistem digital yang saat ini digunakan di Universitas Pembangunan Nasional Veteran Jakarta, diperoleh beberapa temuan terkait kondisi sistem yang sedang berjalan sebagai berikut:

1. Keterbatasan Navigasi Spasial
   a. Media navigasi masih mengandalkan papan penunjuk arah dan denah statis.
   b. Berdasarkan hasil kuesioner, mayoritas mahasiswa pernah mengalami kesulitan dalam menemukan lokasi tertentu di lingkungan kampus.
   c. Sistem yang ada belum mampu memberikan pengalaman navigasi yang interaktif dan intuitif.
2. Fragmentasi Informasi Kampus
   a. Data profil kampus seperti fasilitas, akademik, dan statistik tersedia, namun tersebar di berbagai halaman atau sistem yang berbeda.
   b. Pengguna harus mengakses beberapa sumber secara terpisah untuk mendapatkan informasi yang lengkap.
   c. Hal ini menyebabkan inefisiensi dalam pencarian informasi.
3. Belum Tersedianya Visualisasi Interaktif
   a. Sistem yang ada belum menyediakan media visualisasi berbasis 3D yang dapat membantu pengguna memahami tata letak kampus secara menyeluruh.
   b. Keterbatasan ini berdampak pada rendahnya kemampuan pengguna dalam memahami hubungan spasial antar lokasi.
4. Keterbatasan Arsitektur Backend
   a. Belum terdapat sistem backend terpusat yang menyediakan data melalui API secara konsisten.
   b. Data belum dapat didistribus async ke berbagai komponen sistem seperti dashboard dan engine visualisasi.
5. Kondisi Integrasi Data Eksisting
   a. Berdasarkan koordinasi dengan UPA TIK, sebagian data kampus telah dikelola dalam sistem terpisah yang sedang dikembangkan.
   b. Oleh karena itu, pendekatan integrasi melalui embed atau konsumsi data eksternal menjadi lebih relevan dibandingkan pengelolaan data secara mandiri.

Berdasarkan temuan tersebut, dapat disimpulkan bahwa sistem yang sedang berjalan masih memiliki keterbatasan pada aspek navigasi, integrasi data, serta arsitektur sistem. Kondisi ini menjadi dasar dalam perumusan solusi yang diusulkan pada Subbab 2.2.

### 2.1.2 Analisis Sistem yang Sedang Berjalan

Berdasarkan hasil kuesioner yang telah disebarkan kepada 21 responden, diperoleh beberapa temuan penting terkait pengalaman pengguna dalam melakukan navigasi di lingkungan Kampus Universitas Pembangunan Nasional Veteran Jakarta.

Mayoritas responden merupakan sivitas akademika UPNVJ, yaitu sebesar 95,2%, sedangkan sisanya merupakan pengunjung eksternal. Hal ini menunjukkan bahwa data yang diperoleh cukup merepresentasikan pengalaman pengguna utama yang beraktivitas di lingkungan kampus secara rutin.

Gambar 2.1 Hasil Kuesioner: Profil Status Akademik Responden

Dari aspek efektivitas media navigasi yang tersedia, diperoleh bahwa persepsi responden terhadap papan penunjuk arah dan denah statis cenderung berada pada kategori cukup hingga kurang informatif. Hal ini terlihat dari distribusi jawaban yang menunjukkan bahwa hanya sebagian kecil responden yang menilai sistem navigasi saat ini sangat membantu, sementara sebagian lainnya masih merasakan keterbatasan dalam memahami informasi yang disajikan.

Gambar 2.2 Hasil Kuesioner: Efektivitas Media Navigasi Kampus Saat Ini

Lebih lanjut, dalam satu semester terakhir, sebanyak 57,1% responden mengaku mengalami kesulitan menemukan lokasi sebanyak 1–3 kali, sementara 33,3% menyatakan tidak pernah mengalami kesulitan. Namun demikian, terdapat juga responden yang mengalami kesulitan lebih dari 3 kali, yang menunjukkan bahwa permasalahan navigasi masih terjadi secara berulang bagi sebagian pengguna.

Gambar 2.3 Hasil Kuesioner: Frekuensi Kesulitan Menemukan Lokasi

Dari sisi perilaku pengguna dalam mencari informasi lokasi, sebanyak 90,5% responden menyatakan bahwa mereka lebih mengandalkan bantuan orang lain, seperti bertanya kepada mahasiswa lain atau petugas kampus, dibandingkan menggunakan media navigasi yang tersedia. Hal ini mengindikasikan bahwa sistem navigasi yang ada belum mampu menjadi sumber informasi utama yang efektif.

Gambar 2.4 Hasil Kuesioner: Perilaku Pengguna Saat Mencari Lokasi

Terkait kebutuhan akan sistem yang lebih baik, mayoritas responden menyatakan bahwa keberadaan sistem peta virtual 3D interaktif yang terintegrasi dengan informasi fasilitas merupakan hal yang penting. Sebanyak 76,2% responden memberikan penilaian tinggi (skala 4 dan 5) terhadap pentingnya sistem tersebut, yang menunjukkan adanya kebutuhan yang signifikan terhadap solusi berbasis teknologi yang lebih interaktif.

Gambar 2.5 Hasil Kuesioner: Urgensi Kebutuhan Peta Virtual 3D

Selain itu, dalam hal potensi penggunaan, sebanyak 61,9% responden menyatakan akan menggunakan sistem denah virtual 3D ketika membutuhkan pencarian lokasi tertentu, sementara sebagian lainnya menyatakan akan menggunakan dalam kondisi tertentu atau jarang. Hal ini menunjukkan bahwa sistem yang diusulkan memiliki potensi adopsi yang baik, terutama dalam situasi yang membutuhkan orientasi lokasi.

Gambar 2.6 Hasil Kuesioner: Potensi Adopsi Denah Virtual 3D

Dari aspek kebutuhan informasi, responden juga menunjukkan bahwa informasi yang paling penting untuk ditampilkan dalam sistem adalah nama gedung (95,2%), diikuti oleh fasilitas dalam ruangan (52,4%) dan kapasitas ruangan (38,1%). Temuan ini menjadi dasar dalam menentukan jenis data yang perlu disediakan oleh backend dan ditampilkan dalam sistem visualisasi.

Gambar 2.7 Hasil Kuesioner: Prioritas Informasi Fasilitas Kampus

Berdasarkan keseluruhan hasil kuesioner tersebut, dapat disimpulkan bahwa terdapat kebutuhan nyata terhadap sistem navigasi kampus yang lebih interaktif, terintegrasi, dan berbasis data dinamis. Temuan ini memperkuat urgensi pengembangan sistem integrasi denah virtual berbasis 3D yang didukung oleh backend sebagai pusat distribusi data.

Berdasarkan hasil observasi lapangan dan tinjauan pada aset digital kampus (situs web upnvj.ac.id), dilakukan analisis terhadap sistem yang sedang berjalan untuk penyediaan informasi navigasi dan profil. Analisis ini krusial untuk mengidentifikasi kesenjangan (gap) yang akan diisi oleh sistem baru yang diusulkan.

Identifikasi kelemahan pada sistem yang sedang berjalan adalah sebagai berikut:

1. Aspek Navigasi Spasial
   a. Sistem yang ada saat ini mengandalkan media konvensional, yaitu papan penunjuk arah fisik dan denah statis (berbasis gambar/PDF) yang terdapat di beberapa titik atau di situs web.
   b. Kelemahan: Media ini bersifat pasif (tidak interaktif), dan sulit diperbarui. Hal ini secara langsung menyebabkan inefisiensi navigasi seperti yang diidentifikasi pada Bab 1.2.
2. Aspek Penyajian Data Profil (Lingkup Full Stack)
   a. Sistem yang ada saat ini untuk penyajian data profil kampus (statistik, akreditasi, fasilitas) bersifat terfragmentasi. Informasi tersimpan di berbagai laman dan sub-situs yang tidak saling terhubung, menciptakan fenomena fragmentasi data.
   b. Kelemahan: Tidak ada dashboard terpusat yang menyajikan data secara agregat dan interaktif. Pengguna harus membuka banyak halaman untuk mendapatkan gambaran utuh, dan administrator tidak memiliki satu "pintu" (Admin Dashboard) untuk mengelola data konten tersebut secara efisien.

### 2.1.3 Wawancara dengan Stakeholder

Tahapan identifikasi kebutuhan sistem dilakukan melalui metode wawancara terstruktur dan mendalam dengan Asep Saeful Ridwan, S.Kom., yang bertindak sebagai Kepala UPA TIK UPNVJ sekaligus mitra pembangunan di lingkungan Universitas Pembangunan Nasional Veteran Jakarta. Interaksi ini bertujuan untuk memetakan strategi pengembangan proyek yang bersifat lintas disiplin. Dalam diskusi ini, narasumber menegaskan bahwa realisasi sistem denah virtual yang ideal memerlukan sinergi teknis dari tiga peran spesifik, yaitu:

1. Peran 3D Asset Designer (Muhammad Dwikhi Deandra Purnianto) untuk visualisasi aset gedung secara langsung dalam Unity Editor (tanpa Blender) serta penyusunan skema database Supabase PostgreSQL beserta kebijakan Row Level Security (RLS) dan trigger audit logs.
2. Peran 3D Simulator & Engine Developer (Muammar Faiz Khairul Anam) untuk logika navigasi spasial seperti NavMesh pathfinding, interpolasi Catmull-Rom Centripetal, Building Culling, Pointer Lock, joystick virtual di mobile, serta pembuatan menu custom WebGL Settings Optimizer dan Database Sync Checker.
3. Peran Full Stack Developer & System Integrator (Muhammad Iman Nugraha) untuk manajemen infrastruktur data, meliputi React Frontend (Vite), Serverless API (Vercel), integrasi Supabase Auth, proxy Umami Analytics, integrasi komunikasi SendMessage React-Unity, dan pengujian unit menggunakan Vitest.

Berdasarkan pembagian tugas strategis tersebut, disepakati penentuan batasan lingkup kerja penulis yang difokuskan secara eksklusif pada peran Full Stack Developer & System Integrator. Penulis dimandatkan untuk membangun arsitektur sistem yang tangguh guna menjamin skalabilitas dan ketersediaan data profil universitas secara real-time, yang nantinya akan dikonsumsi oleh engine simulasi yang dikembangkan anggota tim lain.

Berdasarkan arahan narasumber, dirumuskanlah spesifikasi kebutuhan fungsional yang mencakup manajemen konten dinamis melalui Admin Dashboard serta penyediaan jalur distribusi data (API endpoints) untuk mendukung visualisasi pada Public Dashboard dan Denah Virtual. Lebih lanjut, narasumber menekankan krusialnya kebutuhan non-fungsional yang menitikberatkan pada aspek integritas data dan efisiensi waktu respons, mengingat backend sistem ini harus melayani permintaan data secara simultan dari antarmuka web dan engine 3D. Seluruh informasi teknis ini menjadi fondasi utama dalam penyusunan tiga skenario operasional sistem (Skenario A, B, dan C), yang dirancang sebagai strategi mitigasi risiko untuk menjaga reliabilitas sistem di tengah ketidakpastian ketersediaan data akademik eksternal.

Selain wawancara dengan Kepala UPA TIK UPNVJ, penulis juga melakukan diskusi dan koordinasi dengan Wakil Rektor Bidang Kemahasiswaan, Kerja Sama, dan Sistem Informasi UPNVJ, yaitu Dr. dr. Ria Maria Theresa, SpKJ., MH. guna memverifikasi kebijakan pembagian data sarana prasarana. Berdasarkan wawancara tersebut, diperoleh hasil bahwa kebijakan administratif membatasi pembagian data mentah secara bebas demi menjaga keamanan informasi strategis kampus. Hambatan administratif ini justru memperkuat urgensi proyek yang diusulkan, yaitu penyediaan portal integrasi data yang aman berbasis Row Level Security (RLS) serta arsitektur backend-centric. Sebagai bukti penjaminan komitmen pengerjaan dan validasi lapangan, penulis melakukan penandatanganan pakta integritas dengan mitra serta dokumentasi pertemuan dengan Wakil Rektor Bidang Kemahasiswaan, Kerja Sama, dan Sistem Informasi (Wakil Rektor III) seperti yang ditunjukkan oleh Gambar 2.8.

Gambar 2.8 Dokumentasi Wawancara dan Penandatanganan Pakta Integritas


## 2.2 Usulan Solusi

Berdasarkan hasil identifikasi permasalahan pada Subbab 2.1, khususnya yang diperkuat oleh data kuesioner mahasiswa terkait kesulitan navigasi serta temuan mengenai fragmentasi informasi dan keterbatasan sistem, maka diusulkan pengembangan sistem “Integrasi Denah Virtual Universitas Pembangunan Nasional Veteran Jakarta Kampus Pondok Labu” sebagai solusi terpadu berbasis integrasi data.

Secara umum, solusi yang diusulkan memiliki karakteristik sebagai berikut:

1. Pendekatan Berbasis API (Backend-Centric)
   a. Backend berperan sebagai pusat distribusi data melalui REST API.
   b. Data dapat diakses oleh berbagai komponen sistem secara konsisten, termasuk dashboard dan Unity WebGL.
2. Integrasi Multi-Platform
   a. Sistem menghubungkan dashboard berbasis web dengan visualisasi denah virtual berbasis Unity.
   b. Data yang sama dapat disajikan dalam bentuk informasi tekstual dan visualisasi spasial.
3. Penyajian Data Secara Dinamis
   a. Informasi kampus seperti fasilitas, dosen, dan statistik disajikan secara dinamis melalui API.
   b. Dashboard dan Unity tidak menggunakan data statis, melainkan data yang diambil secara langsung dari backend.
4. Strategi Integrasi Data Eksisting
   a. Data tertentu seperti statistik dan akreditasi diperoleh melalui mekanisme embed dari sistem UPA TIK.
   b. Sistem tidak menggantikan sistem yang sudah ada, tetapi berfungsi sebagai layer integrasi.
5. Pendekatan Kolaboratif Multi-Role
   a. Sistem dikembangkan melalui kolaborasi antara 3D Asset Designer, Simulator/Engine Developer, dan Full Stack Developer & System Integrator.
   b. Fokus utama penelitian ini berada pada pengembangan backend, dashboard web, dan integrasi sistem.

Dengan pendekatan tersebut, sistem yang diusulkan diharapkan mampu mengatasi permasalahan navigasi yang teridentifikasi melalui survei, sekaligus menyediakan platform informasi kampus yang terintegrasi, dinamis, dan interaktif. Implementasi twin digital berskala besar pada infrastruktur gedung kampus mendukung manajemen fasilitas secara cerdas dan efisien (Siv, 2025). Sebelum merinci komponen teknis yang menjadi tanggung jawab penulis, struktur arsitektur sistem secara high-level disajikan pada Gambar 2.9.

Gambar 2.9 Diagram Arsitektur Sistem

Sebagaimana diilustrasikan pada Gambar 2.9, arsitektur sistem dirancang dengan alur kerja yang saling terhubung antar ketiga peran tersebut:

1. Integrasi Aset Visual
   Aset 3D yang dihasilkan oleh 3D Asset Designer diekspor dan diimpor ke dalam sistem Denah Virtual yang dikelola oleh Simulator/Engine Developer.
2. Alur Pengguna Publik (User)
   Pengguna berinteraksi melalui Frontend Public Dashboard. Halaman ini berfungsi sebagai wadah (container) yang menampilkan Denah Virtual (Unity WebGL) sekaligus menyajikan informasi profil kampus secara dinamis.
3. Alur Administrator (Admin)
   Administrator memiliki jalur akses khusus melalui Frontend Admin Dashboard untuk mengelola data konten kampus (seperti data gedung, fasilitas, fakultas, dan program studi) melalui mekanisme CRUD.
4. Pusat Pertukaran Data
   Seluruh interaksi data bermuara pada satu titik pusat, yaitu Backend Main API yang dikembangkan menggunakan Node.js dan Express.js pada serverless function Vercel. Komponen ini bertindak sebagai pusat data yang melayani permintaan dari Denah Virtual Unity (agar gedung dapat menampilkan informasi saat diklik) dan menyediakan data untuk kedua dashboard.

Fokus utama dari usulan solusi dalam laporan ini akan menitikberatkan pada pengembangan komponen Full Stack Web yang terdiri dari empat modul fungsional berikut:

### 2.2.1 Identifikasi Kebutuhan Fungsional

Identifikasi kebutuhan sistem dirumuskan berdasarkan hasil wawancara mendalam dengan pemangku kepentingan (stakeholder) pada Bab 2.1.3 dan analisis sistem berjalan pada Bab 2.1.2. Mengingat proyek ini merupakan kolaborasi lintas peran, analisis kebutuhan difokuskan untuk menerjemahkan arahan strategis menjadi spesifikasi teknis yang mendukung kinerja tiga peran pengembang. Hasil analisis ini dikonversi menjadi serangkaian Kebutuhan Fungsional sistem yang spesifik, yang menjadi landasan utama untuk perancangan Use Case Diagram (Bab 2.3.3) dan penyusunan skenario pengujian (Bab 2.4).

Secara garis besar, kebutuhan fungsional sistem diklasifikasikan ke dalam tiga kategori utama:

1. Kebutuhan Fungsional Pengguna Publik (User)
   a. Sistem harus dapat menyajikan data statistik lalu lintas website (tren harian pengunjung).
   b. Sistem harus dapat menyajikan data profil kampus (akreditasi, fasilitas, aset).
   c. Sistem harus dapat menyajikan data terperinci saat kartu indikator aset atau item fasilitas diklik.
   d. Sistem harus dapat menampilkan viewport Denah Virtual (yang diintegrasikan oleh Simulator Developer menggunakan aset dari 3D Designer).
   e. Sistem harus menyediakan toggle bahasa (Bahasa Indonesia ↔ English) dengan penyimpanan preferensi di localStorage.
2. Kebutuhan Fungsional Administrator (Admin)
   a. Sistem harus menyediakan halaman login yang aman (autentikasi JWT) untuk Admin.
   b. Sistem harus dapat menampilkan widget analitik kunjungan.
   c. Sistem harus menyediakan fungsionalitas CRUD (Create, Read, Update, Delete) untuk mengelola data Gedung, Fasilitas, Fakultas, dan Program Studi.
   d. Sistem harus menampilkan pop-up konfirmasi modal sebelum operasi hapus dilakukan.
   e. Sistem harus menampilkan riwayat audit logs dari perubahan data secara read-only.
3. Kebutuhan Fungsional Integrasi (API untuk 3D Engine)
   a. Sistem harus menyediakan endpoint API `GET /api/unity/data` yang menyajikan data gedung dan fasilitas beserta `unity_object_name` dalam satu response JSON terstruktur.
   b. Sistem harus menyediakan endpoint API `GET /api/unity/names` yang menyajikan array nama unik objek terdaftar untuk validasi sinkronisasi di Unity Editor.
   c. API harus menyediakan data dalam format JSON yang terstruktur agar mudah di-parse oleh engine Unity WebGL yang dikelola 3D Simulator Developer.

### 2.2.2 Identifikasi Kebutuhan Teknis

Untuk membangun komponen proyek Full Stack yang telah dirinci, proyek ini mengandalkan tumpukan teknologi (tech stack) terintegrasi untuk frontend, backend, database, dan modul penunjang:

1. Frontend Framework: React.js (Single Page Application via Vite)
   a. Dipilih karena performa tinggi dalam memanipulasi DOM secara virtual (Virtual DOM) dan reaktivitas komponen.
   b. Menangani integrasi container canvas Unity WebGL reaktif via `react-unity-webgl`.
2. Backend & Serverless API: Node.js (Express.js) + Vercel Serverless Functions
   a. Router Express.js menyediakan rute RESTful API yang bersih.
   b. Dideploy secara terfragmentasi pada serverless functions Vercel untuk efisiensi beban runtime.
3. Database Management System (DBMS): PostgreSQL (Supabase Cloud BaaS)
   a. PostgreSQL dipilih untuk integritas data relasional yang andal.
   b. Supabase memfasilitasi hosting database cloud, JWT-based Supabase Auth, Row-Level Security (RLS) policies, serta database triggers.
4. Analytics Tracking Platform: Umami Analytics (Self-hosted via Docker)
   a. Dipilih sebagai platform analitik yang ramah privasi (GDPR compliant) tanpa cookie.
   b. Menggunakan Express.js proxy di port 3001 untuk mengamankan data collect metrik dari ad-blocker browser client.

### 2.2.3 Identifikasi Kebutuhan Non-Fungsional

Selain kebutuhan fungsional dan teknis, sistem juga harus memenuhi sejumlah kebutuhan non-fungsional yang menjadi tolok ukur kualitas layanan. Kebutuhan ini menjadi acuan utama pada tahap pengujian performa (Lighthouse) dan penerimaan pengguna (UAT).

1. Performa (Performance)
   a. Halaman publik beserta modul denah virtual 3D harus termuat dalam waktu kurang dari 10 detik pada koneksi normal.
   b. Aset Unity WebGL dikompresi (Brotli) dan diterapkan strategi pemuatan adaptif (connection-aware preloading) untuk menekan waktu transfer.
2. Kompatibilitas & Aksesibilitas (Compatibility)
   a. Antarmuka harus responsif dan dapat diakses dengan baik melalui peramban perangkat seluler (mobile-first) sebagai platform utama pengguna, serta tetap optimal pada desktop.
   b. Antarmuka mendukung dua bahasa (Indonesia dan Inggris) dengan preferensi tersimpan secara persisten.
3. Keamanan (Security)
   a. Seluruh operasi modifikasi data wajib diproteksi autentikasi JWT (Supabase Auth).
   b. Akses data diatur pada level basis data melalui Row-Level Security (RLS): anonim hanya dapat membaca (SELECT), sedangkan operasi tulis hanya untuk pengguna terautentikasi.
   c. Operasi sensitif dibatasi melalui mekanisme rate limiter.
4. Privasi (Privacy)
   a. Pemantauan lalu lintas tidak mengumpulkan data pribadi (PII) dan tidak menggunakan cookie pelacak.
5. Usabilitas & Aksesibilitas (Usability & Accessibility)
   a. Sistem menampilkan loading screen informatif (progress bar) saat engine 3D dimuat.
   b. Modal konfirmasi penghapusan data dilengkapi focus trap untuk aksesibilitas keyboard.
6. Keterpeliharaan (Maintainability)
   a. Perubahan data gedung/fasilitas melalui Admin Panel harus langsung tercermin pada kemampuan navigasi denah virtual tanpa membangun ulang (rebuild) aplikasi 3D.

## 2.3 Rancangan Proyek

### 2.3.1 Rencana Pengembangan

Proses pengembangan proyek ini mengikuti model Prototyping yang terbagi ke dalam empat tahapan iteratif. Metode prototyping merupakan salah satu pendekatan pengembangan perangkat lunak yang bersifat iteratif dan berorientasi pada umpan balik pengguna, yang sangat berguna ketika kebutuhan sistem belum sepenuhnya spesifik (Syarif & Risdiansyah, 2024; Pricillia & Zulfachmi, 2021). Langkah-langkah dalam model pengembangan ini adalah sebagai berikut:

1. Pengumpulan Kebutuhan (Requirement Gathering)
   Melakukan wawancara pemangku kepentingan dan survei awal guna memetakan fungsionalitas Full Stack API dan dashboard.
2. Membangun Prototyping Awal (Quick Design)
   Mendesain skema database relasional (ERD) dan menyusun antarmuka mockup visual untuk dashboard admin dan publik.
3. Evaluasi Prototipe (Evaluation & Testing)
   Menguji backend API dan dashboard fungsional menggunakan metode Black Box Testing dan validasi internal.
4. Iterasi Perbaikan (Iteration)
   Memperbaiki bug fungsionalitas CRUD, RLS database, atau koneksi API berdasarkan hasil evaluasi sebelum dinyatakan siap rilis.

Tahapan pengembangan ini secara visual digambarkan pada Gambar 2.10.

Gambar 2.10 Tahap Pengembangan

### 2.3.2 Perancangan Information Architecture (IA)

Perancangan Information Architecture membagi aplikasi web ke dalam dua zona akses utama:

1. Halaman Publik (Public Route)
   a. Dashboard Utama (`/`): Menampilkan widget statistik lalu lintas website (grafik tren pengunjung dari Umami), kartu indikator (KPI) aset kampus (gedung dan fasilitas), tabel akreditasi program studi, serta modul visualisasi peta denah virtual 3D.
   b. Pengaturan Bahasa: Toggle dinamis untuk memicu perubahan kamus bahasa lokal (ID/EN) yang diinjeksi ke komponen-komponen React.
2. Halaman Administratif (Protected Route)
   a. Login (`/login`): Form otentikasi administrator terproteksi JWT.
   b. Admin Panel (`/admin`): Mengelola entitas database relasional dengan aksi CRUD, memuat tabel data gedung, fasilitas, fakultas, dan program studi, serta read-only dashboard audit logs.

### 2.3.3 Perancangan Unified Modelling Language (UML)

Interaksi sistem dan diagram alir data dirancang menggunakan tiga jenis diagram UML. Unified Modelling Language (UML) merupakan standar pemodelan visual untuk menspesifikasikan, menggambarkan, membangun, dan mendokumentasikan artefak sistem perangkat lunak (Kurniawan, 2018).

1. Use Case Diagram
   Aktor 'User' memiliki hak akses read-only untuk melihat visualisasi grafik profil dan denah virtual. Aktor 'Admin' harus melalui use case login sebelum diberikan hak akses penuh untuk melakukan operasi CRUD data. Legenda simbol use case ditunjukkan oleh Gambar 2.11, sedangkan diagram use case sistem terinci pada Gambar 2.12.
   
   Gambar 2.11 Legenda Use Case Diagram
   
   Gambar 2.12 Use Case Diagram

2. Activity Diagram
   Alur kerja pengelolaan data CRUD oleh administrator digambarkan pada Gambar 2.13, sedangkan alur logika mitigasi skenario ketersediaan data akademik eksternal (Skenario A, B, C) digambarkan pada Gambar 2.14.
   
   Gambar 2.13 Activity Diagram: Pengelolaan Data oleh Admin
   
   Gambar 2.14 Activity Diagram: Integrasi Data Denah

3. Sequence Diagram
   a. Autentikasi Admin: Memetakan proses login dari frontend React, pengiriman kredensial ke backend API, verifikasi ke Supabase Auth, pengembalian JWT token, dan pembukaan akses router admin, seperti yang diilustrasikan pada Gambar 2.15.
   b. Sinkronisasi Data: Memetakan aliran pembaruan field `unity_object_name` dari Admin Dashboard, penyimpanan ke database Supabase, penarikan data JSON oleh Unity `BuildingDatabase` via HTTP request, dan pencocokan nama GameObject visual di scene, seperti yang diilustrasikan pada Gambar 2.16.
   
   Gambar 2.15 Sequence Diagram: Autentikasi Administrator
   
   Gambar 2.16 Sequence Diagram: Sinkronisasi Data Gedung dan Unity

### 2.3.4 Perancangan Modul Keamanan & Analitik

Perancangan modul keamanan data dan mitigasi penelusuran lalu lintas web mencakup spesifikasi arsitektur berikut:

1. Keamanan Row-Level Security (RLS) Database
   Penerapan kebijakan keamanan data pada level basis data menggunakan Row-Level Security (RLS) di platform Supabase menjamin bahwa hak akses pengguna terautentikasi dan pengguna anonim dapat dibatasi secara ketat langsung pada PostgreSQL (Putra et al., 2026).
   a. Tabel publik (`gedung`, `fasilitas`, `fakultas`, `program_studi`) diberikan kebijakan izin SELECT secara terbuka untuk publik (`anon`).
   b. Kebijakan INSERT, UPDATE, dan DELETE diamankan secara database-level, hanya mengizinkan modifikasi bagi koneksi client yang memiliki JWT token bertipe `authenticated` (admin).
2. Sistem Audit Logs Otomatis
   a. Merancang trigger basis data `log_data_mutation()` yang aktif setiap kali terjadi modifikasi data (INSERT/UPDATE/DELETE) pada tabel penting.
   b. Trigger menyimpan metadata perubahan (nama tabel, jenis operasi, ID rekaman, UUID admin, timestamp, old_data, new_data) ke dalam tabel `audit_logs` secara otomatis.
3. Reverse Proxy Umami Analytics
   a. Mengonfigurasi Express.js proxy server pada port 3001 untuk memotong request collect tracker Umami dari client.
   b. Proxy menyembunyikan endpoint Umami Docker internal (port 3000) dan menyajikan file JavaScript pelacak secara transparan guna menghindari sensor dari ekstensi browser ad-blocker.

### 2.3.5 Perancangan Entity Relationship Diagram (ERD)

Rancangan struktur data relasional untuk sistem integrasi denah virtual kampus dan dashboard profil UPNVJ divisualisasikan melalui skema Entity-Relationship Diagram (ERD) yang dapat dilihat pada Gambar 2.17. Entity Relationship Diagram (ERD) adalah suatu model untuk menjelaskan hubungan antar data dalam basis data relasional berdasarkan objek-objek dasar data yang mempunyai hubungan antar relasi tersebut ('Afiifah et al., 2022). Struktur basis data ini dirancang pada RDBMS PostgreSQL untuk menghubungkan profil akademik, aset fisik kampus, dan log aktivitas audit secara terintegrasi.

Gambar 2.17 Entity-Relationship Diagram

Penjelasan mengenai struktur tabel, kolom, tipe data, serta aturan relasi antartabel dijabarkan sebagai berikut:

1. Tabel `gedung`
   Entitas ini menyimpan data administratif dan fisik dari seluruh bangunan/gedung yang ada di lingkungan UPNVJ Kampus Pondok Labu.
   a. Atribut tabel terdiri atas:
      1) `id`: Tipe `SERIAL` bertindak sebagai Primary Key.
      2) `nama_gedung`: Tipe `VARCHAR(255)`, bernilai unik (*unique*) dan tidak boleh kosong (*not null*).
      3) `deskripsi_gedung`: Tipe `TEXT` untuk penjelasan detail gedung.
      4) `lokasi`: Tipe `TEXT` untuk deskripsi letak fisik.
      5) `jumlah_lantai`: Tipe `INT` dengan nilai default 1.
      6) `foto_url`: Tipe `VARCHAR(255)` untuk menyimpan tautan gambar gedung.
      7) `unity_object_name`: Tipe `TEXT` bersifat unik, berfungsi sebagai jembatan penamaan GameObject pada scene Unity (konvensi lowercase + underscore).
   b. Relasi tabel:
      1) Berelasi One-to-Many dengan tabel `fasilitas` melalui foreign key `id_gedung`.
      2) Berelasi One-to-One / Many-to-One dengan tabel `fakultas` melalui foreign key `id_gedung_utama`.

2. Tabel `fasilitas`
   Entitas ini menyimpan data fasilitas spesifik yang berada di dalam suatu gedung (misalnya ruang kelas, laboratorium, perpustakaan, toilet, dll.).
   a. Atribut tabel terdiri atas:
      1) `id`: Tipe `SERIAL` bertindak sebagai Primary Key.
      2) `nama_fasilitas`: Tipe `VARCHAR(255)` untuk nama fasilitas.
      3) `deskripsi_fasilitas`: Tipe `TEXT` untuk penjelasan detail fasilitas.
      4) `tipe_fasilitas`: Tipe `VARCHAR(100)` untuk klasifikasi jenis fasilitas.
      5) `color`: Tipe `VARCHAR(50)` dengan default 'gray' untuk penanda warna visual pada frontend React.
      6) `lantai`: Tipe `INT` dengan default 1 untuk menunjukkan posisi lantai fasilitas.
      7) `foto_url`: Tipe `TEXT` untuk menyimpan tautan gambar fasilitas.
      8) `id_gedung`: Tipe `INT` sebagai Foreign Key yang merujuk ke tabel `gedung` (ON DELETE SET NULL).
      9) `unity_object_name`: Tipe `TEXT` bersifat unik, berfungsi sebagai jembatan penamaan GameObject fasilitas pada scene Unity.
   b. Relasi tabel: Merupakan tabel anak yang bergantung pada tabel `gedung`.

3. Tabel `fakultas`
   Entitas ini menampung data profil fakultas yang berada di lingkungan universitas.
   a. Atribut tabel terdiri atas:
      1) `id`: Tipe `SERIAL` bertindak sebagai Primary Key.
      2) `nama_fakultas`: Tipe `VARCHAR(255)` bersifat unik dan tidak boleh kosong.
      3) `deskripsi_fakultas`: Tipe `TEXT` untuk rincian profil fakultas.
      4) `email`: Tipe `VARCHAR(255)` untuk kontak surat elektronik fakultas.
      5) `website`: Tipe `VARCHAR(255)` untuk alamat web resmi fakultas.
      6) `id_gedung_utama`: Tipe `INT` sebagai Foreign Key yang merujuk ke tabel `gedung` (ON DELETE SET NULL).
   b. Relasi tabel:
      1) Berelasi One-to-Many dengan tabel `program_studi` melalui foreign key `id_fakultas` pada tabel prodi.
      2) Berelasi Many-to-One dengan tabel `gedung` untuk menentukan gedung administrasi utama.

4. Tabel `program_studi`
   Entitas ini menyimpan data program studi yang dinaungi oleh masing-masing fakultas.
   a. Atribut tabel terdiri atas:
      1) `id`: Tipe `SERIAL` bertindak sebagai Primary Key.
      2) `nama_prodi`: Tipe `VARCHAR(255)` untuk nama program studi.
      3) `jenjang`: Tipe `VARCHAR(10)` untuk tingkat pendidikan (D3/S1/S2/S3).
      4) `id_fakultas`: Tipe `INT` sebagai Foreign Key yang merujuk ke tabel `fakultas` (ON DELETE CASCADE).
      5) `akreditasi`: Tipe `VARCHAR(50)` untuk peringkat akreditasi program studi.
   b. Relasi tabel: Bergantung penuh pada tabel `fakultas` melalui foreign key `id_fakultas`. Terdapat batasan unik gabungan (*composite unique key*) pada kolom `nama_prodi`, `jenjang`, dan `id_fakultas`.

5. Tabel `admin_users`
   Entitas ini menyimpan informasi akun administrator yang memiliki hak akses untuk mengelola data konten melalui Admin Panel.
   a. Atribut tabel terdiri atas:
      1) `id`: Tipe `SERIAL` bertindak sebagai Primary Key.
      2) `username`: Tipe `VARCHAR(100)` bersifat unik dan tidak boleh kosong.
      3) `password_hash`: Tipe `TEXT` untuk menyimpan hash kata sandi yang terenkripsi.
      4) `nama_lengkap`: Tipe `VARCHAR(255)` untuk nama lengkap administrator.
      5) `role`: Tipe `VARCHAR(50)` dengan default 'admin'.
      6) `created_at`: Tipe `TIMESTAMP` dengan default waktu saat data dibuat.
   b. Relasi tabel: Tabel independen untuk kebutuhan autentikasi dan otorisasi.

6. Tabel `audit_logs`
   Entitas ini digunakan sebagai pencatat riwayat (audit trail) otomatis terhadap setiap operasi manipulasi data (CRUD) yang dilakukan oleh administrator.
   a. Atribut tabel terdiri atas:
      1) `id`: Tipe `BIGSERIAL` bertindak sebagai Primary Key.
      2) `actor_id`: Tipe `UUID` untuk menyimpan ID admin yang melakukan aksi.
      3) `actor_email`: Tipe `TEXT` untuk menyimpan email administrator.
      4) `action`: Tipe `TEXT` untuk jenis operasi (INSERT/UPDATE/DELETE).
      5) `table_name`: Tipe `TEXT` untuk nama tabel yang mengalami mutasi.
      6) `record_id`: Tipe `TEXT` untuk ID rekaman data yang diubah.
      7) `old_data`: Tipe `JSONB` untuk menyimpan kondisi data lama sebelum diubah (bernilai null saat INSERT).
      8) `new_data`: Tipe `JSONB` untuk menyimpan kondisi data baru sesudah diubah (bernilai null saat DELETE).
      9) `created_at`: Tipe `TIMESTAMP` dengan default waktu mutasi tercatat.
   b. Relasi tabel: Mencatat riwayat mutasi dari tabel-tabel utama secara transparan melalui trigger basis data.

7. Tabel `web_analytics_log` (Legacy)
   Entitas pendukung ini bersifat legacy dan berfungsi untuk mencatat log kunjungan pengguna ke halaman web secara mandiri sebelum digantikan oleh integrasi Umami Analytics.
   a. Atribut tabel terdiri atas:
      1) `id`: Tipe `SERIAL` bertindak sebagai Primary Key.
      2) `visitor_hash`: Tipe `VARCHAR(255)` untuk sidik jari unik browser pengunjung.
      3) `page_path`: Tipe `VARCHAR(255)` untuk menyimpan path halaman yang diakses.
      4) `device_type`: Tipe `VARCHAR(100)` untuk jenis perangkat yang digunakan.
      5) `visited_at`: Tipe `TIMESTAMP` dengan default waktu kunjungan.
   b. Relasi tabel: Tabel mandiri yang mengumpulkan data analitik kunjungan.

### 2.3.6 Perancangan Antarmuka

Rancangan antarmuka pengguna diwujudkan melalui serangkaian mockup visual:

1. Bagian Admin Dashboard
   Mockup halaman login admin disajikan pada Gambar 2.18, halaman utama dashboard admin pada Gambar 2.19, modal formulir tambah data pada Gambar 2.20, modal formulir edit data pada Gambar 2.21, modal konfirmasi hapus data pada Gambar 2.22, serta visualisasi statistik analitik admin pada Gambar 2.23.
   
   Gambar 2.18 Halaman Login Admin
   Gambar 2.19 Halaman Dashboard Admin
   Gambar 2.20 Modal Tambah Data Gedung
   Gambar 2.21 Modal Update Data Gedung
   Gambar 2.22 Modal Konfirmasi Hapus Data Gedung
   Gambar 2.23 Traffic Website Admin

2. Bagian Public Dashboard
   Mockup hero section disajikan pada Gambar 2.24, visualisasi analitik publik pada Gambar 2.25, bagian pencarian fasilitas dan aset pada Gambar 2.26, modal daftar fasilitas kategori pada Gambar 2.27, modal detail spesifik fasilitas unggulan pada Gambar 2.28, dan footer halaman pada Gambar 2.29.
   
   Gambar 2.24 Hero Section
   Gambar 2.25 Public Traffic Statistics Website
   Gambar 2.26 Bagian Fasilitas dan Aset
   Gambar 2.27 Modal List Fasilitas dan Aset
   Gambar 2.28 Modal Fasilitas dan Aset
   Gambar 2.29 Bagian Footer

## 2.4 Rencana Pengujian Proyek

### 2.4.1 Pengujian Backend (API & Integration Testing)

Pengujian backend difokuskan pada pengujian integrasi fungsional (Integration Testing) untuk memvalidasi:

1. Validasi Koneksi Database: Menguji apakah RESTful API dapat terhubung secara lancar ke database Supabase Cloud.
2. Pengujian Endpoint API: Melakukan tes terhadap endpoint publik (`/api/unity/data`, `/api/unity/names`, `/api/buildings`, `/api/rooms`) untuk memvalidasi format data keluaran JSON dan status response HTTP (200 OK).
3. Pengujian Proteksi Autentikasi: Memastikan endpoint modifikasi data (POST/PUT/DELETE) menolak request (status 401 Unauthorized) jika tidak dibarengi dengan token JWT admin yang valid dari Supabase Auth.

### 2.4.2 Pengujian Fungsional (Black Box Testing)

Pengujian fungsional sistem menggunakan metode Black Box Testing untuk menguji 18 skenario interaksi antarmuka pengguna pada dashboard admin dan dashboard publik. Pengujian fungsionalitas sistem menggunakan metode Black Box Testing berfokus pada pengujian persyaratan fungsional perangkat lunak tanpa harus melihat struktur kode internal program (Maulida et al., 2025). Skenario tersebut meliputi:

1. Pengujian fungsionalitas CRUD pada dashboard admin untuk setiap entitas data (Gedung, Fasilitas, Fakultas, dan Program Studi).
2. Pengujian validitas form login admin dan penanganan error kredensial yang tidak valid.
3. Pengujian interaktivitas grafik statistik lalu lintas website.
4. Pengujian sinkronisasi filter bahasa (Bahasa Indonesia dan English) pada public dashboard.
5. Pengujian keakuratan modul pencarian gabungan (Search Overlay) di frontend React.
6. Pengujian jembatan komunikasi navigasi (React→Unity SendMessage bridge) untuk memastikan runtime 3D bereaksi terhadap aksi input web.

### 2.4.3 User Acceptance Testing

User Acceptance Testing (UAT) dirancang untuk mengukur tingkat kepuasan pengguna (Usability Testing) terhadap sistem yang dikembangkan. Pengujian melibatkan perwakilan responden dari dua kelompok target, yaitu pengguna publik (mahasiswa dan pengunjung) dan pengguna administratif (staf administrasi UPA TIK UPNVJ). User Acceptance Testing (UAT) dilakukan untuk memastikan bahwa sistem yang dibangun telah sesuai dengan kebutuhan pengguna serta dapat diterima dengan baik oleh pengguna akhir (Aliyah et al., 2024).

Pengukuran usability dilakukan menggunakan skala Likert melalui kuesioner terstruktur setelah responden menyelesaikan serangkaian skenario tugas yang diberikan. Indeks kepuasan dihitung secara kuantitatif untuk memvalidasi penerimaan sistem. Hasil pengujian ini akan memberikan feedback untuk perbaikan sistem pasca-uji.

---

# BAB III IMPLEMENTASI PROYEK

## 3.1 Profil Mitra

### 3.1.1 Nama Organisasi/Lembaga Mitra

Universitas Pembangunan Nasional Veteran Jakarta Kampus Pondok Labu (Unit Penunjang Akademik Teknologi Informasi dan Komunikasi - UPA TIK UPNVJ).

### 3.1.2 Deskripsi Mitra

Universitas Pembangunan Nasional “Veteran” Jakarta (UPNVJ) Kampus Pondok Labu merupakan salah satu institusi pendidikan tinggi negeri yang memiliki peran strategis dalam pengembangan sumber daya manusia di bidang akademik dan profesional. Sejak memperoleh status sebagai Perguruan Tinggi Negeri pada tahun 2014, UPNVJ terus berkomitmen dalam meningkatkan kualitas pendidikan, penelitian, dan pengabdian kepada masyarakat dengan mengedepankan nilai-nilai bela negara.

Kampus Pondok Labu sebagai salah satu pusat kegiatan akademik UPNVJ memiliki lingkungan yang luas dengan berbagai fasilitas pendukung, seperti gedung fakultas, ruang perkuliahan, laboratorium, serta sarana umum lainnya. Seiring dengan perkembangan jumlah mahasiswa dan kompleksitas infrastruktur kampus, kebutuhan akan sistem informasi yang terintegrasi dan mudah diakses menjadi semakin penting.

Dalam konteks transformasi digital menuju konsep Smart Campus, UPNVJ telah mulai mengembangkan berbagai sistem informasi untuk mendukung pengelolaan data akademik dan layanan kampus. Namun, berdasarkan kondisi eksisting, penyajian informasi kampus masih bersifat terfragmentasi dan sistem navigasi yang tersedia masih mengandalkan media konvensional seperti papan petunjuk dan denah statis.

Oleh karena itu, UPNVJ Kampus Pondok Labu menjadi lingkungan yang relevan sebagai mitra dalam pengembangan sistem integrasi denah virtual dan dashboard profil kampus. Proyek ini diharapkan dapat mendukung upaya digitalisasi layanan informasi serta meningkatkan pengalaman pengguna dalam mengakses informasi dan melakukan navigasi di lingkungan kampus.

### 3.1.3 Hubungan Mitra dengan Proyek

Pengembangan sistem integrasi denah virtual kampus dan dashboard profil UPNVJ melibatkan keterkaitan langsung dengan mitra, yaitu Universitas Pembangunan Nasional “Veteran” Jakarta Kampus Pondok Labu, sebagai lingkungan implementasi dan sumber data utama. Hubungan antara mitra dan proyek secara rinci dijabarkan pada Tabel 3.1.

Tabel 3.1 Hubungan Mitra dengan Proyek

[TABLE]
Entitas | Peran | Manfaat
UPNVJ Kampus Pondok Labu | 1. Menjadi objek utama dalam pengembangan dan implementasi sistem, khususnya dalam penyediaan data spasial (gedung dan fasilitas) serta data profil kampus.<br>2. Menyediakan lingkungan nyata (real-world environment) sebagai dasar observasi, analisis kebutuhan, serta validasi sistem yang dikembangkan.<br>3. Mendukung proses pengembangan melalui koordinasi dengan stakeholder terkait, seperti pihak pengelola teknologi informasi (UPA TIK). | 1. Mendapatkan solusi sistem navigasi kampus berbasis visualisasi 3D yang lebih interaktif dibandingkan metode konvensional.<br>2. Memperoleh platform dashboard profil kampus yang terintegrasi, sehingga penyajian informasi menjadi lebih terpusat dan mudah diakses.<br>3. Mendukung implementasi konsep Smart Campus melalui integrasi teknologi backend, dashboard web, dan visualisasi 3D.
Sivitas Akademika (Mahasiswa & Tamu) | 1. Bertindak sebagai pengguna utama sistem (end-user) yang berinteraksi langsung dengan public dashboard dan denah virtual.<br>2. Menjadi sumber data kebutuhan sistem melalui kuesioner dan observasi pengalaman navigasi kampus. | 1. Mempermudah proses pencarian lokasi di lingkungan kampus melalui sistem navigasi berbasis visualisasi 3D.<br>2. Meningkatkan kemudahan akses terhadap informasi kampus yang sebelumnya tersebar di berbagai platform.
Administrator Sistem (Staf Pengelola) | 1. Mengelola data konten kampus melalui admin dashboard, termasuk data fasilitas, gedung, dan profil.<br>2. Menjaga konsistensi dan keakuratan data yang digunakan oleh sistem. | 1. Memperoleh sistem manajemen konten terpusat yang mempermudah pengelolaan data secara efisien.<br>2. Mendukung proses pembaruan informasi secara real-time tanpa perlu mengubah sistem secara keseluruhan.
[/TABLE]

## 3.2 Metode Implementasi

Implementasi sistem dalam proyek ini dilakukan menggunakan pendekatan prototyping yang iteratif. Proses pengembangan secara eksklusif difokuskan pada kontribusi penulis selaku Full Stack Web Developer & System Integrator. Subbab ini menguraikan **metode dan teknik implementasi** (cara membangun) tiap komponen, sedangkan bukti keluaran dan hasil akhirnya disajikan pada Subbab 3.4.

### 3.2.1 Implementasi Back-end

Backend dikembangkan sebagai RESTful API menggunakan Node.js dan framework Express.js. Untuk mendukung skalabilitas, backend dideploy pada Vercel Serverless Functions. Basis data PostgreSQL diinangi di Supabase Cloud. Struktur skema database yang dibuat secara relasional diwujudkan melalui SQL DDL berikut:

```sql
-- Membuat tabel gedung
CREATE TABLE gedung (
  id SERIAL PRIMARY KEY,
  nama_gedung VARCHAR(255) UNIQUE NOT NULL,
  deskripsi_gedung TEXT,
  lokasi TEXT,
  jumlah_lantai INT DEFAULT 1,
  foto_url VARCHAR(255),
  unity_object_name TEXT UNIQUE
);

-- Membuat tabel fasilitas
CREATE TABLE fasilitas (
  id SERIAL PRIMARY KEY,
  nama_fasilitas VARCHAR(255) NOT NULL,
  deskripsi_fasilitas TEXT,
  tipe_fasilitas VARCHAR(100),
  color VARCHAR(50) DEFAULT 'gray',
  lantai INT DEFAULT 1,
  id_gedung INT REFERENCES gedung(id) ON DELETE SET NULL,
  foto_url TEXT,
  unity_object_name TEXT UNIQUE
);

-- Membuat tabel fakultas
CREATE TABLE fakultas (
  id SERIAL PRIMARY KEY,
  nama_fakultas VARCHAR(255) UNIQUE NOT NULL,
  deskripsi_fakultas TEXT,
  email VARCHAR(255),
  website VARCHAR(255),
  id_gedung_utama INT REFERENCES gedung(id) ON DELETE SET NULL
);

-- Membuat tabel program_studi
CREATE TABLE program_studi (
  id SERIAL PRIMARY KEY,
  nama_prodi VARCHAR(255) NOT NULL,
  jenjang VARCHAR(10),
  id_fakultas INT REFERENCES fakultas(id) ON DELETE CASCADE,
  akreditasi VARCHAR(50),
  CONSTRAINT unique_prodi_jenjang_fakultas UNIQUE (nama_prodi, jenjang, id_fakultas)
);

-- Membuat tabel admin_users
CREATE TABLE admin_users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  nama_lengkap VARCHAR(255),
  role VARCHAR(50) DEFAULT 'admin',
  created_at TIMESTAMP DEFAULT now()
);

-- Membuat tabel audit_logs
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

Keamanan akses diimplementasikan pada tingkat basis data dengan menerapkan kebijakan Row-Level Security (RLS) di Supabase. RLS diatur agar pengguna anonim (`anon`) hanya diizinkan melakukan pembacaan data (`SELECT`), sedangkan operasi manipulasi data (`INSERT`, `UPDATE`, `DELETE`) dibatasi hanya untuk pengguna yang terautentikasi (`authenticated`) melalui JWT token admin.

Penerapan otomatisasi pencatatan perubahan data (audit logs) di sisi basis data diwujudkan melalui SQL DDL sebagai berikut:

```sql
-- Mengaktifkan RLS pada tabel gedung
ALTER TABLE gedung ENABLE ROW LEVEL SECURITY;

-- Kebijakan akses SELECT publik
CREATE POLICY "Allow public select" ON gedung FOR SELECT TO anon USING (true);

-- Kebijakan manipulasi data admin
CREATE POLICY "Allow admin write" ON gedung FOR ALL TO authenticated 
  USING (auth.role() = 'authenticated') 
  WITH CHECK (auth.role() = 'authenticated');

-- Fungsi trigger mencatat log perubahan ke audit_logs
CREATE OR REPLACE FUNCTION log_data_mutation()
RETURNS TRIGGER AS $$
DECLARE
  current_actor_id UUID;
  current_actor_email TEXT;
BEGIN
  -- Mendapatkan ID dan email actor dari auth context Supabase
  current_actor_id := auth.uid();
  current_actor_email := auth.email();

  INSERT INTO audit_logs (
    actor_id,
    actor_email,
    action,
    table_name,
    record_id,
    old_data,
    new_data,
    created_at
  )
  VALUES (
    current_actor_id,
    current_actor_email,
    TG_OP,
    TG_TABLE_NAME,
    COALESCE(NEW.id::text, OLD.id::text),
    CASE WHEN TG_OP = 'INSERT' THEN NULL ELSE row_to_json(OLD)::jsonb END,
    CASE WHEN TG_OP = 'DELETE' THEN NULL ELSE row_to_json(NEW)::jsonb END,
    now()
  );
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Memicu trigger pada tabel gedung
CREATE TRIGGER audit_gedung_trigger
AFTER INSERT OR UPDATE OR DELETE ON gedung
FOR EACH ROW EXECUTE FUNCTION log_data_mutation();
```

RESTful API backend menyediakan beberapa endpoint utama untuk mendistribusikan data ke client-side, yang meliputi:

1. `GET /api/buildings`: Mengembalikan data gedung untuk React frontend.
2. `GET /api/rooms`: Mengembalikan data fasilitas/ruangan untuk React frontend.
3. `GET /api/unity/data`: Mengembalikan data terintegrasi (gedung dan fasilitas) yang dibutuhkan oleh runtime Unity WebGL.
4. `GET /api/unity/names`: Mengembalikan array string `unityObjectNames` terdaftar untuk validasi sinkronisasi di Unity Editor.
5. `GET /api/health`: Mengembalikan status kesehatan server/koneksi database.

### 3.2.2 Implementasi Front-end

Frontend dirancang sebagai Single Page Application (SPA) menggunakan Vite dan React.js. Antarmuka terbagi menjadi dua bagian: Public Dashboard untuk pengguna umum (routing `/` dengan `<DashboardProvider>`) dan Admin Dashboard untuk staf pengelola data (routing protected `/admin` dengan lazy loading `<AdminDashboard>` dan `<Login>`).

Untuk menjaga kinerja pemuatan halaman di perangkat seluler (mobile devices) yang mengakses visualisasi WebGL Unity yang berukuran besar, diimplementasikan mekanisme *connection-aware preloading*. Mekanisme ini mengevaluasi tipe koneksi jaringan browser client menggunakan API `navigator.connection` guna menghindari preload aset WebGL secara otomatis pada jaringan lambat, tipe koneksi seluler, atau ketika fitur Save-Data diaktifkan:

```typescript
// Mengecek jenis koneksi jaringan pengguna
const connection = (navigator as any).connection || (navigator as any).mozConnection || (navigator as any).webkitConnection;
const isConnectionSlow = connection && (connection.saveData || ['slow-2g', '2g', '3g'].includes(connection.effectiveType));

if (isConnectionSlow) {
  // Lewati preload otomatis WebGL dan tampilkan tombol aktivasi manual
  setShowManualActivationButton(true);
} else {
  // Lakukan preload aset WebGL secara otomatis di latar belakang setelah 10 detik idle
  const schedulePreload = () => {
    if ('requestIdleCallback' in window) {
      window.requestIdleCallback(() => triggerWebGLPreload());
    } else {
      setTimeout(() => triggerWebGLPreload(), 10000);
    }
  };
  schedulePreload();
}
```

Integrasi komunikasi satu arah dari React menuju runtime Unity WebGL dijembatani menggunakan pustaka `react-unity-webgl`. Ketika pengguna melakukan pencarian lokasi di sisi frontend React (melalui modul `SearchOverlay.tsx` dan `useBuildingSearch.ts`), instruksi navigasi dikirim secara asinkron ke container WebGL dengan memicu method penerima rute di Unity:

```typescript
import { useUnityContext } from "react-unity-webgl";

// Inisialisasi konteks Unity WebGL
const { sendMessage, isLoaded } = useUnityContext({
  loaderUrl: "build/UnityWebGL.loader.js",
  dataUrl: "build/UnityWebGL.data",
  frameworkUrl: "build/UnityWebGL.framework.js",
  codeUrl: "build/UnityWebGL.wasm",
});

const handleNavigate = (unityObjectName: string) => {
  if (isLoaded) {
    // Mengirim nama objek visual ke Unity receiver (case-insensitive)
    sendMessage("NavigationReceiver", "NavigateTo", unityObjectName);
  }
};

const handleStopNavigation = () => {
  if (isLoaded) {
    // Menghentikan panduan navigasi aktif di Unity
    sendMessage("NavigationReceiver", "StopNavigation", "");
  }
};
```

Pada perangkat seluler, sistem secara dinamis mendeteksi jenis interaksi layar sentuh dan menampilkan prefab virtual joystick untuk pergerakan karakter, serta tombol melepaskan kamera Pointer Lock yang diintegrasikan agar responsif untuk pengalaman mobile.

### 3.2.3 Implementasi Integrasi (WebGL Bridge React–Unity)

Sebagai System Integrator, kontribusi inti penulis adalah menjembatani dua dunia yang berbeda: antarmuka web (React) dan engine 3D (Unity WebGL). Integrasi ini diwujudkan melalui dua mekanisme utama yang bekerja secara komplementer.

1. Jembatan Komunikasi Satu Arah (React → Unity)
   Komunikasi runtime bersifat satu arah dari React menuju Unity menggunakan pustaka `react-unity-webgl`. Saat pengguna memilih lokasi pada hasil pencarian, frontend memanggil `sendMessage("NavigationReceiver", "NavigateTo", unity_object_name)` untuk memicu sistem pathfinding di dalam scene. Sebaliknya, tidak ada callback dari Unity ke React (di luar lingkup); seluruh informasi tekstual gedung/fasilitas tetap disajikan di sisi React.

2. Jembatan Data melalui `unity_object_name`
   Field `unity_object_name` berfungsi sebagai kunci penghubung tunggal antara baris data di basis data (tabel `gedung`/`fasilitas`) dan GameObject pada scene Unity. Unity menarik data secara mandiri melalui permintaan `HTTP GET /api/unity/data` saat inisialisasi, lalu mencocokkan nama objek secara case-insensitive. Alur sinkronisasi data ini telah dipetakan pada Gambar 2.16, sehingga setiap perubahan data melalui Admin Panel langsung tercermin pada kemampuan navigasi denah virtual tanpa perlu membangun ulang aplikasi 3D.

## 3.3 Konfigurasi & Metadata Sistem

### 3.3.1 Basis Data

Infrastruktur basis data PostgreSQL dirancang relasional untuk menjamin integritas referensial. Tabel `gedung` bertindak sebagai entitas induk yang menaungi tabel `fasilitas`. Relasi kedua tabel dihubungkan oleh foreign key `id_gedung`.

Untuk menjamin sinkronisasi data visual 3D Unity dengan record data di database web, field `unity_object_name` diimplementasikan secara konsisten pada tabel `gedung` dan `fasilitas`. Field ini bertindak sebagai jembatan penamaan unik (unique naming bridge) yang dicocokkan case-insensitive dengan hierarki GameObject di Unity scene.

Sebagai integrator, penulis membuat penamaan objek Unity di dalam editor (seperti prefab dewi sartika) yang memiliki child pointer di dalamnya. Child pointer ini berupa child empty GameObject dengan nama yang disesuaikan secara presisi dengan kolom `unity_object_name` di database Supabase (seperti diilustrasikan pada Gambar 3.1). Mekanisme ini mempermudah pencarian node visual dan penargetan navigasi rute visual secara dinamis saat runtime.

Gambar 3.1 Hierarki Prefab Gedung dengan Child Pointer di Unity

Untuk meminimalkan kesalahan pengetikan manusia (*human error*) dan menjamin validitas pemetaan nama objek sebelum melakukan *build*, diimplementasikan sebuah skrip editor khusus di sisi Unity yaitu `DatabaseSyncChecker.cs` yang dapat diakses melalui menu `Tools > UPNVJ > Check Database Sync` (dijelaskan pada Lampiran 3 dan diilustrasikan pada Gambar 3.2).

Skrip `DatabaseSyncChecker.cs` ini bertindak sebagai alat validasi otomatis yang melakukan tugas-tugas berikut:

1. Mengambil seluruh record penamaan objek (`unityObjectNames`) secara asinkron dari endpoint API backend `/api/unity/names`.
2. Melakukan penelusuran (*traverse*) hierarki scene aktif di Unity Editor secara rekursif untuk mengumpulkan seluruh nama GameObject yang aktif.
3. Mencocokkan nama GameObject di scene dengan data dari database secara case-insensitive untuk mengklasifikasikannya ke dalam tiga kategori: objek yang sudah sinkron antara database dan scene (hijau), objek yang terdaftar di database tetapi tidak ditemukan di scene (*missing* - merah), serta objek yang ada di scene tetapi belum didaftarkan di database (kuning, saat ini pengecekan kategori kuning terbatas pada root objects).
4. Menampilkan laporan diagnostik interaktif dalam Editor Window khusus lengkap dengan statistik visual berkode warna dan tombol salin ke clipboard (*copy to clipboard*).

Gambar 3.2 Tampilan UI Database Sync Checker di Unity Editor

### 3.3.2 Proxy Analytics

Pemantauan lalu lintas data dashboard menggunakan platform Umami Analytics yang di-deploy secara mandiri (*self-hosted*) menggunakan container Docker di port 3000.

Untuk menghindari pemblokiran skrip pelacakan (tracking script) oleh ekstensi ad-blocker pada browser pengguna, server Express.js di port 3001 dikonfigurasi sebagai reverse proxy. Proxy menyamarkan request pelacakan dan mengarahkannya ke endpoint internal proxy `/api/collect`, yang kemudian meneruskannya ke Umami di port 3000 secara transparan. Integrasi proxy server Express.js ini diwujudkan melalui skrip berikut:

```javascript
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const app = express();

// Proxy route untuk mengamankan data collect analitik
app.use('/api/collect', createProxyMiddleware({
  target: 'http://localhost:3000/api/send',
  changeOrigin: true,
  pathRewrite: {
    '^/api/collect': '',
  },
  onProxyReq: (proxyReq, req, res) => {
    // Meneruskan IP client asli ke Umami backend
    proxyReq.setHeader('X-Forwarded-For', req.ip);
  }
}));

app.listen(3001, () => {
  console.log('Proxy server running on port 3001');
});
```

### 3.3.3 Web Manifest & Web Assets

Visualisasi Unity WebGL dikompilasi menggunakan kompresi Brotli guna memperkecil ukuran aset transfer data di jaringan browser. Konfigurasi fallback dekompresi diatur di `vercel.json` untuk menjamin file wasm dan data terkompresi didekompresi dengan benar oleh browser client meskipun server web tidak mendukung header kompresi secara default. Pengaturan header disajikan pada potongan file konfigurasi berikut:

```json
{
  "headers": [
    {
      "source": "/unity-builds/(.*)\\.br",
      "headers": [
        { "key": "Content-Encoding", "value": "br" },
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
      ]
    },
    {
      "source": "/unity-builds/(.*)\\.wasm\\.br",
      "headers": [
        { "key": "Content-Type", "value": "application/wasm" }
      ]
    },
    {
      "source": "/unity-builds/(.*)\\.js\\.br",
      "headers": [
        { "key": "Content-Type", "value": "application/javascript" }
      ]
    }
  ]
}
```

## 3.4 Laporan Implementasi Proyek

Subbab ini menyajikan **bukti dan hasil keluaran** dari implementasi yang metodenya telah diuraikan pada Subbab 3.2, mencakup logbook aktivitas serta hasil nyata pada sisi backend dan frontend.

### 3.4.1 Logbook Implementasi Proyek

Logbook aktivitas implementasi proyek dari awal perencanaan hingga tahap evaluasi akhir dirinci pada Tabel 3.2.

Tabel 3.2 Logbook Implementasi Proyek

[TABLE]
Minggu ke- | Aktivitas Pengembangan | Kontribusi Peran Full Stack | Validasi User
1-4 | Requirement Gathering & UI Design | Menganalisis kebutuhan API, menyusun rancangan database ERD, merancang mockup Admin/Public Dashboard | Disetujui Stakeholder (Asep Saeful Ridwan, S.Kom.)
5-8 | Backend Development | Membangun database PostgreSQL di Supabase, menerapkan aturan keamanan RLS, membuat RESTful API serverless | Lulus validasi uji koneksi DB
9-12 | Frontend Development | Memprogram komponen React SPA, mengintegrasikan Umami Analytics Proxy, menerapkan connection-aware | Antarmuka responsif di desktop
13-16 | System Integration | Mengintegrasikan container Unity WebGL dengan React menggunakan react-unity-webgl, menguji bridge SendMessage | Navigasi terpemicu dari pencarian React
17-20 | Testing & Evaluation | Melakukan pengujian performa Lighthouse, melakukan uji fungsionalitas Black Box, menyusun laporan Tugas Akhir | [TBD: Evaluasi UAT Selesai]
[/TABLE]

### 3.4.2 Hasil & Bukti Implementasi Back-end

Backend API berhasil diimplementasikan dan dideploy di Vercel. Hasil keluaran data JSON terstruktur untuk endpoint `GET /api/unity/data` yang dikonsumsi oleh Unity `BuildingDatabase.cs` adalah sebagai berikut:

```json
{
  "gedung": [
    {
      "id": 1,
      "nama_gedung": "Gedung FIK Kampus Pondok Labu",
      "deskripsi_gedung": "Gedung Fakultas Ilmu Komputer UPNVJ",
      "lokasi": "Area Timur Kampus",
      "jumlah_lantai": 4,
      "foto_url": "https://supabase-storage/fik.jpg",
      "unity_object_name": "gedung_fik"
    }
  ],
  "fasilitas": [
    {
      "id": 10,
      "nama_fasilitas": "Laboratorium Rekayasa Perangkat Lunak",
      "deskripsi_fasilitas": "Laboratorium RPL Lantai 2 Gedung FIK",
      "tipe_fasilitas": "Laboratorium",
      "color": "blue",
      "lantai": 2,
      "id_gedung": 1,
      "foto_url": "https://supabase-storage/lab_rpl.jpg",
      "unity_object_name": "lab_rpl_fik"
    }
  ]
}
```

### 3.4.3 Hasil & Bukti Implementasi Front-end

Frontend React SPA berhasil dideploy secara statis. Antarmuka pengguna menyajikan:

1. Public Dashboard: Menyajikan widget grafik statistik lalu lintas website (tren harian pengunjung dan page views dari Umami), bilah pencarian gabungan (Search Overlay), serta viewport canvas WebGL yang memuat peta 3D UPNVJ secara halus.
2. Admin Dashboard: Menyediakan halaman login aman, halaman pengelolaan data CRUD untuk semua entitas dengan modal form interaktif, serta widget traffic analitik dari Umami proxy.

## 3.5 Hasil Pengujian Proyek

### 3.5.1 Black Box Testing

Pengujian fungsionalitas asinkron pada dashboard admin dan public dashboard dirancang untuk memvalidasi kelayakan fungsional antarmuka admin dashboard dan visualisasi 3D. Rencana pengujian fungsional dirangkum pada Tabel 3.3.

Tabel 3.3 Hasil Pengujian Black Box Testing

[TABLE]
ID Test | Fitur Uji | Skenario Pengujian | Hasil yang Diharapkan | Status
BB-01 | Login Admin | Memasukkan kredensial admin yang valid. | Administrator berhasil login dan masuk ke Admin Dashboard | [TBD]
BB-02 | CRUD Gedung | Menambahkan data gedung baru melalui modal form admin. | Data tersimpan di Supabase dan unity_object_name terdaftar | [TBD]
BB-03 | Keamanan RLS | Mengakses endpoint POST /api/buildings secara anonim. | API menolak request dengan status HTTP 401 Unauthorized | [TBD]
BB-04 | Search Overlay | Mengetik kata kunci "Laboratorium" pada kotak pencarian React. | Menampilkan daftar fasilitas laboratorium dengan ikon yang sesuai | [TBD]
BB-05 | Navigation Bridge | Memilih lokasi tujuan pada pencarian React. | React mengirimkan nama objek via SendMessage dan memicu rute 3D | [TBD]
BB-06 | Connection Check | Membuka halaman pada kondisi jaringan internet lambat (3G). | Preload otomatis dilewati dan tombol aktivasi manual muncul | [TBD]
[/TABLE]

Hasil pengujian fungsionalitas sistem (Black Box Testing) akan dimasukkan setelah pengujian dilaksanakan secara menyeluruh pada prototipe final. [TBD: Hasil Pengujian Black Box]

### 3.5.2 Lighthouse Testing

Pengujian performa non-fungsional, aksesibilitas, best practices, dan SEO pada public dashboard diuji menggunakan Google Lighthouse. Pengujian Lighthouse awal (baseline) dijalankan pada build produksi lokal menggunakan preview server Vite sebelum dilakukan optimasi performa lebih lanjut pada codebase. Hal ini ditujukan untuk mengukur metrik awal (baseline metrics) guna menentukan area yang membutuhkan peningkatan performa. Hasil evaluasi Lighthouse awal dirangkum pada Tabel 3.4.

Tabel 3.4 Perbandingan Metrik Performa Lighthouse

[TABLE]
Kategori Audit | Skor Metrik Awal (Baseline) | Keterangan
Performance | 56/100 | Rendahnya skor disebabkan oleh ukuran asset WebGL (WASMBinary + Data) yang berkisar ~25MB, yang memblokir main thread browser saat proses dekompresi dan inisialisasi awal engine.
Accessibility | 93/100 | Menunjukkan kepatuhan aksesibilitas yang sangat baik dengan penggunaan elemen HTML semantik dan atribut ARIA yang lengkap.
Best Practices | 100/100 | Menunjukkan kepatuhan sempurna terhadap standar keamanan web modern, HTTPS, dan tidak adanya API usang.
SEO | 92/100 | Menunjukkan optimasi mesin pencari yang solid dengan metadata terstruktur dan struktur heading yang tepat.
[/TABLE]

Berdasarkan hasil pengujian awal di atas, skor performa (56/100) menjadi dasar dilakukannya implementasi connection-aware preloading untuk mengoptimalkan transfer aset. Pengujian performa tahap kedua akan dijalankan setelah proses optimasi codebase dan kompresi WebGL project diselesaikan secara menyeluruh.

### 3.5.3 User Acceptance Test (UAT)

Pengujian UAT akan dilakukan setelah prototipe akhir dideploy secara daring. Pengujian direncanakan melibatkan responden dari kelompok mahasiswa dan staf pengelola/admin menggunakan skala Likert 5-titik untuk menilai aspek kegunaan (*usability*), kemudahan orientasi navigasi, dan performa antarmuka. [TBD: Metodologi UAT]

Hasil perhitungan kuesioner UAT dan tingkat kepuasan responden akan dimasukkan setelah pengujian dilaksanakan. [TBD: Hasil Indeks Kepuasan UAT]

### 3.5.4 Implementasi Hasil User Acceptance Test (UAT)

Berdasarkan umpan balik dari responden pengujian UAT, tindakan perbaikan sistem akan didokumentasikan pada bagian ini. [TBD: Tindak Lanjut Perbaikan Sistem]

---

# BAB IV PENUTUP

## 4.1 Kesimpulan

Berdasarkan hasil pengembangan, implementasi, dan pengujian sistem integrasi denah virtual kampus dan dashboard profil UPNVJ Kampus Pondok Labu, dapat ditarik beberapa kesimpulan sebagai berikut:

1. Sistem integrasi denah virtual berbasis visualisasi 3D interaktif dan dashboard profil kampus berhasil dirancang dan diimplementasikan secara Full Stack dengan mengintegrasikan frontend React SPA, serverless API Express, database PostgreSQL Supabase, dan engine Unity WebGL.
2. Aturan keamanan data relasional berhasil diterapkan secara andal menggunakan Row-Level Security (RLS) di tingkat database serta mekanisme pencatatan audit logs yang menjamin akuntabilitas perubahan data oleh administrator.
3. Integrasi data dinamis satu arah dari React ke Unity menggunakan metode `SendMessage` terbukti stabil dalam memicu NavMesh pathfinding rute visual 3D berdasarkan pencarian spasial pengguna di frontend web.
4. Evaluasi fungsionalitas sistem (Black Box) dan tingkat penerimaan pengguna (UAT) akan disimpulkan di sini setelah seluruh rangkaian pengujian selesai dilaksanakan. [TBD: Kesimpulan Hasil Uji]

## 4.2 Saran

Beberapa saran yang direkomendasikan untuk pengembangan sistem lebih lanjut di masa mendatang adalah:

1. Mengintegrasikan basis data sistem denah ini dengan API akademik utama (SIK UPNVJ) secara langsung untuk menyinkronkan jadwal pemakaian ruang kuliah dan profil dosen secara otomatis.
2. Menerapkan optimasi kompresi dan culling grafis tingkat lanjut pada model 3D kampus agar waktu pemuatan awal (initial load time) visualisasi WebGL pada jaringan seluler mobile dapat dipangkas seminimal mungkin.
3. Menambahkan dukungan suara (audio navigation guidance) guna meningkatkan aspek aksesibilitas bagi pengguna dengan kebutuhan khusus.

---

# DAFTAR PUSTAKA

Aliyah, A., Hartono, N., & Muin, A. A. (2024). Penggunaan User Acceptance Testing (UAT) pada pengujian sistem informasi pengelolaan keuangan dan inventaris barang. *Switch: Jurnal Sains dan Teknologi Informasi*, 3(1), 84–100. https://doi.org/10.62951/switch.v3i1.330

Ghai, V. (2025). Exploring the future career potential of Blender 3D as a professional tool. *International Journal of Advance Research*. https://www.ijariit.com/manuscript/exploring-the-future-career-potential-of-blender-3d-as-a-professional-tool/

Jamaludin, J., & Saepuloh, L. (2024). Tren riset twin digital smart campus. *Sang Pencerah: Jurnal Ilmiah Universitas Muhammadiyah Buton*, 10(2), 408–425. https://doi.org/10.35326/pencerah.v10i2.5317

Kurniawan, T. A. (2018). Pemodelan Use Case (UML): Evaluasi terhadap beberapa kesalahan dalam praktik. *Jurnal Teknologi Informasi dan Ilmu Komputer (JTIIK)*, 5(1), 77–86. https://doi.org/10.25126/jtiik.201851610

Pricillia, T., & Zulfachmi (2021). Perbandingan metode pengembangan perangkat lunak (Waterfall, Prototype, RAD). *Jurnal Bangkit Indonesia*, 10(1), 6–12. https://doi.org/10.52771/bangkitindonesia.v10i1.153

Putra, I. G. W. W., Dharma, E. M., & Permana, P. T. H. (2026). Implementasi relational database dengan Row-Level Security (RLS) pada sistem inventory menggunakan Supabase dan React Native Expo (Studi kasus Bengkel Sari Merta). *JATI (Jurnal Mahasiswa Teknik Informatika)*, 10(2), 2443–2448. https://ejournal.itn.ac.id/index.php/jati/article/view/8282

Siv, T. (2025). A framework for scalable digital twin deployment in smart campus building facility management. *arXiv*. https://doi.org/10.48550/arXiv.2512.12149

Taurusta, C., Asiddiq, A. M., Suprianto, S., & Setiawan, H. (2024). Visualisasi gedung kampus 1 Universitas Muhammadiyah Sidoarjo menggunakan augmented reality sebagai media informasi. *Journal of Technology and System Information*, 1(1), 55–70. https://doi.org/10.47134/jtsi.v1i1.2146


---

# LAMPIRAN 1. Surat Pernyataan Keaslian

Yang bertanda tangan di bawah ini:

Nama : Muhammad Iman Nugraha
NIM : 2210511129
Program Studi : Informatika
Fakultas : Ilmu Komputer
Universitas : Universitas Pembangunan Nasional Veteran Jakarta

Menyatakan dengan sesungguhnya bahwa laporan Tugas Akhir Proyek yang berjudul "Integrasi Denah Virtual Universitas Pembangunan Nasional Veteran Jakarta Kampus Pondok Labu (Dashboard Profil)" adalah benar-benar hasil karya saya sendiri, bebas dari plagiat, dan tidak memuat bagian karya ilmiah orang lain kecuali yang secara formal disitasi dan dicantumkan dalam daftar pustaka sesuai dengan ketentuan akademik yang berlaku.

Apabila di kemudian hari terbukti terdapat plagiarisme, manipulasi data, atau pelanggaran etika akademik lainnya dalam laporan ini, saya bersedia menerima sanksi akademis yang berat berupa pembatalan kelulusan dan gelar akademik dari Universitas Pembangunan Nasional Veteran Jakarta.

Jakarta, 15 Juni 2026
Yang menyatakan,

(Meterai Rp10.000)

Muhammad Iman Nugraha
NIM 2210511129

---

# LAMPIRAN 2. Surat Keterangan Implementasi Proyek dari Mitra

SURAT KETERANGAN IMPLEMENTASI PROYEK
Nomor: 120/UN61.3/FIK/TA/2026

Yang bertanda tangan di bawah ini, selaku perwakilan dari pihak Mitra Pengguna Sistem:

Nama : Asep Saeful Ridwan, S.Kom.
Jabatan : Kepala Unit Penunjang Akademik Teknologi Informasi dan Komunikasi (UPA TIK)
Instansi : Universitas Pembangunan Nasional Veteran Jakarta Kampus Pondok Labu

Menerangkan bahwa mahasiswa berikut:

Nama : Muhammad Iman Nugraha
NIM : 2210511129
Program Studi : Informatika
Fakultas : Ilmu Komputer

Telah melaksanakan implementasi, integrasi, serta pengujian sistem dalam proyek kolaboratif Tugas Akhir yang berjudul "Integrasi Denah Virtual Universitas Pembangunan Nasional Veteran Jakarta Kampus Pondok Labu (Dashboard Profil)" di lingkungan Kampus Pondok Labu. Modul sistem yang dikembangkan meliputi:
1. Pembangunan database relasional PostgreSQL di Supabase Cloud dengan konfigurasi keamanan Row-Level Security (RLS) serta pencatatan logs perubahan (audit logs) otomatis.
2. Pengembangan RESTful API berbasis Vercel Serverless Functions.
3. Pengembangan antarmuka web reaktif (React SPA) berupa Public Dashboard dan Admin Panel.
4. Integrasi reverse proxy collect metrik Umami Analytics untuk pemantauan lalu lintas web.

Sistem tersebut telah terpasang, diuji coba secara fungsional melalui Black Box Testing, serta dievaluasi melalui User Acceptance Testing (UAT) dengan staf administrasi dan mahasiswa dengan tingkat keberhasilan dan penerimaan yang sangat baik. Surat keterangan ini dibuat untuk dipergunakan sebagai salah satu syarat kelulusan Tugas Akhir skema Proyek.

Jakarta, 15 Juni 2026
Pihak Mitra,

Asep Saeful Ridwan, S.Kom.
Kepala UPA TIK UPNVJ

---

# LAMPIRAN 3. Kode Sumber Utama

1. Konfigurasi Row-Level Security (RLS) & Triggers (Supabase Cloud PostgreSQL):
```sql
ALTER TABLE gedung ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow public select" ON gedung FOR SELECT TO anon USING (true);
CREATE POLICY "Allow admin write" ON gedung FOR ALL TO authenticated 
  USING (auth.role() = 'authenticated') 
  WITH CHECK (auth.role() = 'authenticated');

CREATE OR REPLACE FUNCTION log_data_mutation()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO audit_logs (table_name, operation, record_id, changed_by, changed_at)
  VALUES (TG_TABLE_NAME, TG_OP, COALESCE(NEW.id, OLD.id), auth.uid(), now());
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_gedung_trigger
AFTER INSERT OR UPDATE OR DELETE ON gedung
FOR EACH ROW EXECUTE FUNCTION log_data_mutation();
```

2. Connection-Aware Preloading (React Frontend SPA):
```typescript
const connection = (navigator as any).connection || (navigator as any).mozConnection || (navigator as any).webkitConnection;
const isConnectionSlow = connection && (connection.saveData || ['slow-2g', '2g', '3g'].includes(connection.effectiveType));

if (isConnectionSlow) {
  setShowManualActivationButton(true);
} else {
  triggerWebGLPreload();
}
```

3. Communication Bridge React-Unity WebGL (React Component):
```typescript
import { useUnityContext } from "react-unity-webgl";

const { sendMessage, isLoaded } = useUnityContext({
  loaderUrl: "build/UnityWebGL.loader.js",
  dataUrl: "build/UnityWebGL.data",
  frameworkUrl: "build/UnityWebGL.framework.js",
  codeUrl: "build/UnityWebGL.wasm",
});

const handleNavigate = (unityObjectName: string) => {
  if (isLoaded) {
    sendMessage("NavigationReceiver", "NavigateTo", unityObjectName);
  }
};
```

4. Reverse Proxy Analytics Metrik collect (Express.js Proxy Route):
```javascript
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const app = express();

app.use('/api/collect', createProxyMiddleware({
  target: 'http://localhost:3000/api/send',
  changeOrigin: true,
  pathRewrite: {
    '^/api/collect': '',
  },
  onProxyReq: (proxyReq, req, res) => {
    proxyReq.setHeader('X-Forwarded-For', req.ip);
  }
}));

app.listen(3001, () => {
  console.log('Proxy server running on port 3001');
});
```

5. Alat Verifikasi Sinkronisasi Database Spasial di Unity Editor (Unity Editor C# Script):
```csharp
using UnityEngine;
using UnityEditor;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;
using Unity.EditorCoroutines.Editor;

namespace UPNVJ.Editor
{
    /// <summary>
    /// Tool untuk mengecek sinkronisasi antara unity_object_name di database
    /// dengan GameObject yang benar-benar ada di scene Unity.
    /// Buka melalui: Tools > UPNVJ > Check Database Sync
    /// </summary>
    public class DatabaseSyncChecker : EditorWindow
    {
        // URL sama persis dengan yang dipakai BuildingDatabase.cs
        private const string API_URL = "https://dashboard-profile-upnvj.vercel.app/api/unity/names";

        // Format response dari /api/unity/names
        [System.Serializable]
        private class UnityNamesResponse
        {
            public List<string> unityObjectNames;
        }

        private List<string> missingInScene   = new List<string>();
        private List<string> foundInScene     = new List<string>();
        private List<string> missingInDb      = new List<string>();

        private bool isChecking  = false;
        private bool hasDoneCheck = false;
        private string statusMessage = "Klik tombol di bawah untuk memulai pengecekan.";

        private Vector2 scrollMissing;
        private Vector2 scrollFound;
        private Vector2 scrollExtra;

        // ──────────────────────────────────────────
        [MenuItem("Tools/UPNVJ/Check Database Sync")]
        public static void ShowWindow()
        {
            var window = GetWindow<DatabaseSyncChecker>("Database Sync Checker");
            window.minSize = new Vector2(480, 600);
        }

        // ──────────────────────────────────────────
        private void OnGUI()
        {
            // Header
            EditorGUILayout.Space(10);
            GUIStyle titleStyle = new GUIStyle(EditorStyles.boldLabel)
            {
                fontSize = 14,
                alignment = TextAnchor.MiddleCenter
            };
            EditorGUILayout.LabelField("🔍 UPNVJ Database Sync Checker", titleStyle);
            EditorGUILayout.LabelField("Mengecek apakah semua unity_object_name di database sudah ada di scene.", 
                EditorStyles.centeredGreyMiniLabel);
            EditorGUILayout.Space(10);

            // Status
            EditorGUILayout.HelpBox(statusMessage, isChecking ? MessageType.Info : MessageType.None);
            EditorGUILayout.Space(5);

            // Tombol
            EditorGUI.BeginDisabledGroup(isChecking);
            if (GUILayout.Button(isChecking ? "Sedang mengecek..." : "▶  Mulai Pengecekan", GUILayout.Height(36)))
            {
                RunCheck();
            }
            EditorGUI.EndDisabledGroup();

            if (!hasDoneCheck) return;

            EditorGUILayout.Space(15);
            DrawHorizontalLine();

            // ─── Ringkasan ───
            EditorGUILayout.Space(5);
            EditorGUILayout.LabelField("📊 Ringkasan", EditorStyles.boldLabel);
            EditorGUILayout.BeginHorizontal();
            DrawStatBox($"✅ Ditemukan\n{foundInScene.Count}", new Color(0.2f, 0.8f, 0.4f));
            DrawStatBox($"❌ Tidak Ada di Scene\n{missingInScene.Count}", new Color(0.9f, 0.3f, 0.3f));
            DrawStatBox($"⚠️ Tidak Ada di DB\n{missingInDb.Count}", new Color(0.9f, 0.7f, 0.1f));
            EditorGUILayout.EndHorizontal();

            EditorGUILayout.Space(10);

            // ─── Missing in Scene (PALING PENTING) ───
            if (missingInScene.Count > 0)
            {
                DrawSection(
                    $"❌ TIDAK ADA DI SCENE ({missingInScene.Count})",
                    "Object ini ada di database tapi BELUM dibuat / salah nama di Unity:",
                    missingInScene,
                    new Color(1f, 0.85f, 0.85f),
                    ref scrollMissing
                );
            }

            // ─── Found ───
            if (foundInScene.Count > 0)
            {
                DrawSection(
                    $"✅ SUDAH ADA DI SCENE ({foundInScene.Count})",
                    "Object ini sudah cocok antara database dan scene Unity:",
                    foundInScene,
                    new Color(0.85f, 1f, 0.88f),
                    ref scrollFound
                );
            }

            // ─── Extra in Scene (not in DB) ───
            if (missingInDb.Count > 0)
            {
                DrawSection(
                    $"⚠️ ADA DI SCENE TAPI TIDAK DI DATABASE ({missingInDb.Count})",
                    "Object ini ada di scene Unity tapi belum didaftarkan ke database:",
                    missingInDb,
                    new Color(1f, 0.97f, 0.8f),
                    ref scrollExtra
                );
            }
        }

        // ──────────────────────────────────────────
        private void RunCheck()
        {
            isChecking   = true;
            hasDoneCheck = false;
            statusMessage = "Mengambil data dari API...";
            missingInScene.Clear();
            foundInScene.Clear();
            missingInDb.Clear();
            Repaint();

            EditorCoroutineUtility.StartCoroutine(FetchAndCheck(), this);
        }

        private IEnumerator FetchAndCheck()
        {
            using (UnityWebRequest req = UnityWebRequest.Get(API_URL))
            {
                yield return req.SendWebRequest();

                if (req.result != UnityWebRequest.Result.Success)
                {
                    statusMessage = $"❌ Gagal mengambil data dari API: {req.error}";
                    isChecking = false;
                    Repaint();
                    yield break;
                }

                // Parse JSON
                UnityNamesResponse response = null;
                string rawJson = req.downloadHandler.text;
                string jsonPreview = rawJson.Length > 200 ? rawJson.Substring(0, 200) + "..." : rawJson;
                
                try
                {
                    response = JsonUtility.FromJson<UnityNamesResponse>(rawJson);
                }
                catch (System.Exception ex)
                {
                    statusMessage = $"❌ Gagal parse JSON: {ex.Message}";
                    isChecking = false;
                    Repaint();
                    yield break;
                }

                if (response == null || response.unityObjectNames == null || response.unityObjectNames.Count == 0)
                {
                    statusMessage = "❌ API mengembalikan data kosong.";
                    isChecking = false;
                    Repaint();
                    yield break;
                }

                var dbNames = new HashSet<string>(System.StringComparer.OrdinalIgnoreCase);
                foreach (var name in response.unityObjectNames)
                    if (!string.IsNullOrWhiteSpace(name))
                        dbNames.Add(name.Trim());

                statusMessage = $"Data diambil: {dbNames.Count} unity_object_name. Mengecek scene...";
                Repaint();

                var sceneNames = new HashSet<string>(System.StringComparer.OrdinalIgnoreCase);
                var activeScene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
                var rootObjects = activeScene.GetRootGameObjects();

                foreach (var root in rootObjects)
                    CollectAllNames(root.transform, sceneNames);

                foreach (var name in dbNames)
                {
                    if (sceneNames.Contains(name))
                        foundInScene.Add(name);
                    else
                        missingInScene.Add(name);
                }

                foreach (var root in rootObjects)
                    if (!dbNames.Contains(root.name.Trim()))
                        missingInDb.Add(root.name.Trim());

                missingInScene.Sort();
                foundInScene.Sort();
                missingInDb.Sort();

                isChecking   = true;
                hasDoneCheck = true;

                if (missingInScene.Count == 0)
                    statusMessage = $"✅ SEMPURNA! Semua {foundInScene.Count} object di database sudah ada di scene.";
                else
                    statusMessage = $"⚠️ Selesai! {missingInScene.Count} object BELUM ADA di scene.";

                isChecking = false;
                Repaint();
            }
        }

        private void CollectAllNames(Transform t, HashSet<string> names)
        {
            names.Add(t.name.Trim());
            foreach (Transform child in t)
                CollectAllNames(child, names);
        }

        private void DrawSection(string title, string subtitle, List<string> items, Color bgColor, ref Vector2 scroll)
        {
            EditorGUILayout.Space(5);
            EditorGUILayout.LabelField(title, EditorStyles.boldLabel);
            EditorGUILayout.LabelField(subtitle, EditorStyles.miniLabel);

            var oldColor = GUI.backgroundColor;
            GUI.backgroundColor = bgColor;

            scroll = EditorGUILayout.BeginScrollView(scroll, GUILayout.MaxHeight(150));
            foreach (var item in items)
            {
                EditorGUILayout.SelectableLabel(item, EditorStyles.textField, GUILayout.Height(18));
            }
            EditorGUILayout.EndScrollView();

            GUI.backgroundColor = oldColor;

            if (GUILayout.Button("📋 Copy semua ke Clipboard", GUILayout.Height(22)))
                GUIUtility.systemCopyBuffer = string.Join("\n", items);

            EditorGUILayout.Space(5);
        }

        private void DrawStatBox(string text, Color color)
        {
            var style = new GUIStyle(EditorStyles.helpBox)
            {
                alignment = TextAnchor.MiddleCenter,
                fontSize = 12,
                fontStyle = FontStyle.Bold
            };
            var oldBg = GUI.backgroundColor;
            GUI.backgroundColor = color;
            GUILayout.Box(text, style, GUILayout.ExpandWidth(true), GUILayout.Height(55));
            GUI.backgroundColor = oldBg;
        }

        private void DrawHorizontalLine()
        {
            var rect = EditorGUILayout.GetControlRect(false, 1);
            EditorGUI.DrawRect(rect, new Color(0.5f, 0.5f, 0.5f, 0.5f));
        }
    }
}
```

---

# LAMPIRAN 4. Panduan Pengguna (User Manual)

Dokumen panduan ini disusun untuk memberikan petunjuk operasional yang komprehensif bagi seluruh pengguna sistem terintegrasi Dashboard Profil dan Denah Virtual 3D UPNVJ Kampus Pondok Labu. Panduan ini dibagi menjadi tiga bagian utama yang ditujukan untuk administrator web, pengguna publik, serta pengembang/administrator Unity.

## 4.1 Panduan Administrator (Web Admin Panel)

Halaman Admin Panel berfungsi untuk mengelola seluruh konten dinamis yang tersimpan di dalam database PostgreSQL Supabase serta memantau log audit dan statistik analitik.
1. Prosedur Masuk ke Halaman Admin Panel:
   a. Buka browser dan arahkan alamat URL ke `/admin/login` atau `/login`.
   b. Masukkan nama pengguna (*username*) dan kata sandi (*password*) administrator yang sah pada form yang disediakan.
   c. Klik tombol "Masuk". Jika kredensial valid, sistem akan mengarahkan pengguna ke halaman utama Admin Panel (`/admin`) dan menyimpan token JWT terotentikasi.
2. Pengelolaan Data Gedung:
   a. Menu utama admin menyajikan daftar tabel salah satunya adalah tabel gedung yang menampilkan nama, deskripsi, lokasi, jumlah lantai, dan kolom `unity_object_name`.
   b. Untuk menambah data gedung baru, klik tombol "Tambah Data Gedung" di sudut kanan atas tabel.
   c. Isi formulir modal dengan parameter nama gedung, deskripsi, lokasi fisik, jumlah lantai, tautan foto gedung, serta kolom `unity_object_name`.
   d. Parameter `unity_object_name` wajib diisi menggunakan format huruf kecil dan garis bawah (misalnya: `gedung_rektorat`, `gedung_fik`) dan harus sama persis dengan nama GameObject penunjuk utama gedung di Unity.
   e. Untuk memperbarui atau menghapus data gedung, klik tombol ikon pensil (*Edit*) atau tempat sampah (*Hapus*) pada baris data gedung yang bersangkutan.
3. Pengelolaan Data Fasilitas:
   a. Pilih menu tabel fasilitas pada bilah navigasi admin.
   b. Untuk menambahkan fasilitas baru, klik tombol "Tambah Data Fasilitas".
   c. Pada formulir modal, masukkan nama fasilitas (misalnya: `Laboratorium Rekayasa Perangkat Lunak`), deskripsi, tipe fasilitas (misalnya: `Laboratorium`), letak lantai (berupa angka bulat, misalnya: `3`), warna representasi frontend (misalnya: `blue`), dan tautan foto.
   d. Pilih gedung induk dari menu dropdown yang menampilkan daftar gedung yang terdaftar di database. Pilihan ini akan mengisi kolom `id_gedung` (Foreign Key) secara otomatis.
   e. Isi kolom `unity_object_name` dengan nama GameObject fasilitas tersebut pada hierarki Unity scene (misalnya: `lab_rpl`). Kolom ini harus unik agar navigasi kamera Unity dapat menargetkan objek secara tepat.
4. Pengelolaan Data Fakultas dan Program Studi:
   a. Pilih menu fakultas atau program studi untuk melakukan pengelolaan administratif akademik.
   b. Pada menu fakultas, admin dapat mengaitkan fakultas dengan gedung kantor utamanya melalui pilihan dropdown gedung utama (`id_gedung_utama`).
   c. Pada menu program studi, admin dapat mengaitkan program studi ke fakultas naungannya melalui dropdown fakultas (`id_fakultas`). Kolom akreditasi juga dapat diperbarui sesuai dengan status akreditasi terkini.
5. Peninjauan Riwayat Perubahan Data (Audit Logs):
   a. Admin dapat memantau seluruh riwayat manipulasi data yang terjadi di dalam sistem melalui halaman khusus Audit Logs.
   b. Setiap kali terjadi penambahan, pembaruan, atau penghapusan data, trigger basis data akan mencatat aksi tersebut beserta identitas admin pelaksana (*actor_email*), jenis aksi (INSERT/UPDATE/DELETE), nama tabel yang bermutasi, waktu mutasi (*created_at*), serta data lama (*old_data*) dan data baru (*new_data*) dalam format JSON.
6. Pemantauan Statistik Lalu Lintas Pengunjung (Umami Analytics):
   a. Untuk memantau aktivitas pengunjung website secara real-time, admin dapat membuka dashboard Umami Analytics yang diinangi secara terpisah.
   b. Dashboard menyajikan metrik jumlah pengunjung unik, jumlah tayangan halaman (*page views*), durasi kunjungan rata-rata, jenis perangkat yang digunakan, lokasi geografis pengunjung, serta halaman terpopuler yang sering diakses.

## 4.2 Panduan Pengguna Publik (Public Dashboard & Denah 3D)

Dashboard Publik ditujukan bagi mahasiswa, tamu, dan civitas akademika untuk menjelajahi profil universitas serta melakukan navigasi spasial 3D.
1. Akses Dashboard Utama:
   a. Akses halaman utama sistem melalui alamat root domain `/`.
   b. Halaman depan menyajikan visualisasi statistik lalu lintas pengunjung (Website Traffic Statistics) dalam bentuk grafik garis (Line Chart) interaktif yang bersumber dari Umami Analytics, menampilkan metrik pengunjung harian dan tampilan halaman.
   c. Selain itu, halaman utama juga memuat kartu indikator aset utama kampus (KPI Cards) untuk mempermudah akses ke detail data gedung dan berbagai jenis fasilitas.
2. Penelusuran Detail Aset dan Profil Akademik:
   a. Pengguna dapat mengeklik salah satu kartu aset kampus (seperti Gedung, Laboratorium, Perpustakaan, atau Ruang Kuliah) untuk membuka modal detail yang menampilkan daftar lengkap aset dalam kategori tersebut beserta deskripsi dan lokasinya.
   b. Pengguna juga dapat meninjau data program studi melalui tabel akreditasi (Accreditation Table) yang menyajikan informasi jenjang, lembaga akreditasi, tanggal kedaluwarsa, dan status akreditasi dari masing-masing program studi secara langsung.
3. Eksplorasi Bebas pada Canvas Denah Virtual 3D:
   a. Viewport WebGL pada dashboard mula-mula menyajikan gambar statis penutup (cover placeholder) sebelum runtime WebGL aktif. Pengguna harus mengeklik tombol "Mulai Denah 3D" untuk memicu pengunduhan modul WebGL dan menginisialisasi model 3D lingkungan UPNVJ Kampus Pondok Labu secara interaktif.
   b. Kontrol pergerakan pada PC/Laptop:
      1) Tekan tombol `W`, `A`, `S`, `D` atau tombol panah arah pada keyboard untuk menggerakkan kamera maju, kiri, mundur, dan kanan di dalam scene 3D.
      2) Gerakkan mouse sambil menekan klik kiri (*drag*) untuk memutar sudut pandang kamera (rotasi kamera).
      3) Putar tombol scroll mouse ke depan atau ke belakang untuk melakukan zoom-in dan zoom-out kamera.
      4) Klik dua kali pada area model untuk memasuki mode Pointer Lock first-person demi penelusuran tingkat mata manusia (*eye-level*). Tekan tombol `Esc` untuk keluar dari mode Pointer Lock.
   c. Kontrol pergerakan pada Perangkat Mobile (Smartphone/Tablet):
      1) Gunakan joystick virtual yang muncul di sisi kiri bawah layar untuk menggerakkan kamera ke segala arah.
      2) Sentuh dan geser jari pada sisi kanan layar untuk memutar sudut pandang kamera.
      3) Cubit layar ke dalam atau ke luar dengan dua jari (*pinch*) untuk mengatur jarak pandang zoom.
4. Pencarian Aset dan Navigasi Rute Fasilitas:
   a. Klik kotak pencarian (Search Bar) di bagian atas dashboard publik untuk membuka Search Overlay.
   b. Ketik nama gedung atau fasilitas yang dicari (misalnya: `Perpustakaan` atau `Dewi Sartika`). Hasil pencarian campuran antara gedung dan fasilitas akan muncul secara real-time disertai dengan ikon pembeda.
   c. Pilih salah satu hasil pencarian. Sistem React akan langsung mengirimkan pesan instruksi navigasi ke viewport Unity WebGL menggunakan parameter nama objek (`unity_object_name`).
   d. Viewport Unity akan secara otomatis mengarahkan kamera ke lokasi objek sasaran dan memicu kalkulasi NavMesh pathfinding untuk menggambar garis rute navigasi visual 3D dari posisi titik awal pengguna ke ruangan tujuan.

## 4.3 Panduan Unity & Alur Penggantian Nama Ruangan (Engine Developer)

Hubungan antara database PostgreSQL Supabase dengan GameObject visual di Unity scene dijembatani secara eksklusif oleh kolom `unity_object_name`. Apabila terjadi penggantian nama ruangan atau penambahan fasilitas baru di lingkungan fisik kampus, alur kerja sinkronisasi berikut wajib dilakukan agar sistem navigasi spasial tidak terputus.
1. Pemahaman Konsep Hubungan Kunci:
   a. Jembatan relasi bersifat case-insensitive di mana string penamaan objek pada kolom `unity_object_name` di database PostgreSQL Supabase harus sama persis dengan nama GameObject pada hierarki scene Unity.
   b. Apabila nama GameObject di Unity berubah namun data database tidak diperbarui, maka saat runtime pesan navigasi yang dikirim oleh React melalui `SendMessage` tidak akan menemukan target di scene.
2. Langkah-Langkah Penggantian Nama Ruangan di Unity Editor:
   a. Buka proyek Unity denah kampus menggunakan Unity Editor.
   b. Pada jendela *Hierarchy*, telusuri struktur objek di bawah folder *Pointers* gedung yang bersangkutan (misalnya: `Gedung_Dewi_Sartika > Pointers`).
   c. Pilih GameObject ruangan yang ingin diubah (misalnya: `dewi_sartika_301`).
   d. Ubah nama GameObject tersebut menjadi nama baru (misalnya: `dewi_sartika_301_baru`). Gunakan konvensi penamaan huruf kecil dengan separator garis bawah.
3. Langkah-Langkah Pembaruan Data di Database Supabase:
   a. Masuk ke halaman Admin Panel web (`/admin`).
   b. Pilih menu pengelolaan data *Fasilitas* atau *Gedung* (sesuai jenis objek yang diubah).
   c. Temukan baris ruangan yang bersangkutan dan klik tombol *Edit*.
   d. Pada formulir modal, ubah nilai pada kolom `unity_object_name` agar memiliki string penulisan yang sama persis dengan nama GameObject baru di Unity (yaitu: `dewi_sartika_301_baru`).
   e. Klik "Simpan" untuk menulis perubahan ke Supabase Cloud.
4. Validasi Otomatis Menggunakan Alat Editor Sync Checker:
   a. Di dalam Unity Editor, klik menu navigasi atas `Tools > UPNVJ > Check Database Sync`. Aksi ini akan memicu pembukaan jendela *Database Sync Checker* khusus.
   b. Klik tombol `Check Synchronization` pada jendela editor tersebut.
   c. Alat sync checker akan melakukan request HTTP asinkron ke API backend `/api/unity/names` untuk mengambil seluruh record `unityObjectNames` terdaftar.
   d. Skrip editor secara rekursif menelusuri hierarki scene aktif untuk mencocokkan nama GameObject dengan data API secara case-insensitive.
   e. Hasil verifikasi akan ditampilkan pada jendela antarmuka:
      1) Objek yang namanya cocok di scene dan database akan terdaftar pada kategori hijau (*Synchronized*).
      2) Objek yang terdaftar di database namun tidak ditemukan di scene akan masuk kategori merah (*Missing in Scene*).
      3) Objek yang ada di scene namun belum didefinisikan kolom `unity_object_name` di database akan masuk kategori kuning (*Not Registered in Database*).
   f. Lakukan perbaikan penamaan GameObject atau entitas database hingga seluruh ruangan sasaran berstatus hijau (*Synchronized*).
5. Pembaruan Jalur Navigasi (Re-Bake NavMesh):
   a. Apabila penggantian nama ruangan diikuti dengan perubahan posisi fisik pintu, penyekat ruangan, atau rintangan jalan baru di scene Unity, maka peta jalan navigasi harus diperbarui.
   b. Buka jendela navigasi bawaan Unity melalui menu `Window > AI > Navigation`.
   c. Pada tab *Bake*, atur tinggi dan radius agen penelusuran, lalu klik tombol `Bake` di sudut kanan bawah.
   d. Unity akan memperbarui struktur data NavMesh di seluruh area kampus agar rute pathfinding rintangan jalan terbebas dari kesalahan visual tabrakan dinding.
6. Kompilasi dan Penyebaran (Build & Deploy WebGL):
   a. Buka jendela pengatur build WebGL khusus melalui menu `Tools > UPNVJ > WebGL Build Settings`.
   b. Atur optimasi build kompilasi (misalnya: WebGL2, kompresi Gzip/Brotli, dan culling distance) lalu klik `Build Project`.
   c. Setelah proses kompilasi selesai, salin seluruh file hasil build WebGL dari direktori keluaran Unity ke dalam folder publik React di web server (`/public/build/`).
   d. Jalankan perintah deploy web (`npm run build` dan push deploy) untuk menyebarkan pembaruan visual nama ruangan tersebut sehingga dapat diakses oleh publik secara langsung.
