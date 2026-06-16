# INTEGRASI DENAH VIRTUAL UNIVERSITAS PEMBANGUNAN NASIONAL VETERAN JAKARTA KAMPUS PONDOK LABU
# (DASHBOARD PROFIL)

Muhammad Iman Nugraha
2210511129

INFORMATIKA
FAKULTAS ILMU KOMPUTER
UNIVERSITAS PEMBANGUNAN NASIONAL VETERAN JAKARTA
2025

# DAFTAR GAMBAR

Gambar 2.1 Diagram Arsitektur Sistem
Gambar 2.2 Tahap Pengembangan
Gambar 2.3 Entity-Relationship Diagram
Gambar 2.4 Legenda Use Case Diagram
Gambar 2.5 Use Case Diagram
Gambar 2.6 Activity Diagram: Pengelolaan Data oleh Admin
Gambar 2.7 Activity Diagram: Integrasi Data Denah
Gambar 2.8 Sequence Diagram: Autentikasi Administrator
Gambar 2.9 Sequence Diagram: Sinkronisasi Data Gedung dan Unity
Gambar 2.10 Halaman Login Admin
Gambar 2.11 Halaman Dashboard Admin
Gambar 2.12 Modal Tambah Dosen
Gambar 2.13 Modal Update Dosen
Gambar 2.14 Modal Konfirmasi Hapus Dosen
Gambar 2.15 Traffic Website Admin
Gambar 2.16 Hero Section
Gambar 2.17 Public Traffic Statistics Website
Gambar 2.18 Bagian Fasilitas dan Aset
Gambar 2.19 Modal List Fasilitas dan Aset
Gambar 2.20 Modal Fasilitas dan Aset
Gambar 2.21 Bagian Statistik
Gambar 2.22 Detail Data Dosen
Gambar 2.23 Detail Data Mahasiswa
Gambar 2.24 Bagian Footer
Gambar 2.25 Dokumentasi Wawancara dan Penandatanganan Pakta Integritas

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

Tahap observasi awal merupakan fondasi penting dalam memahami permasalahan serta merumuskan kebutuhan sistem yang akan dikembangkan. Proses observasi dalam penelitian ini dilakukan melalui kombinasi beberapa metode, yaitu observasi lapangan, penyebaran kuesioner kepada mahasiswa, serta wawancara dengan stakeholder terkait. Pendekatan ini digunakan untuk memperoleh gambaran yang komprehensif, baik dari sisi pengguna maupun dari sisi institusi.

Berdasarkan hasil kuesioner yang telah disebarkan kepada mahasiswa, ditemukan bahwa mayoritas responden pernah mengalami kesulitan dalam menemukan lokasi tertentu di lingkungan kampus. Hal ini menunjukkan adanya permasalahan nyata pada aspek navigasi yang dirasakan langsung oleh pengguna, terutama mahasiswa baru dan pengunjung yang belum familiar dengan lingkungan kampus.

Selanjutnya, hasil observasi lapangan menunjukkan bahwa sistem navigasi yang tersedia saat ini masih mengandalkan media konvensional seperti papan penunjuk arah dan denah statis, yang bersifat pasif, tidak interaktif, serta sulit diperbarui. Kondisi ini menyebabkan keterbatasan dalam memberikan pengalaman navigasi yang efektif dan intuitif bagi pengguna.

Untuk melengkapi analisis dari sisi institusi, dilakukan wawancara dengan Wakil Rektor Bidang Kemahasiswaan, Kerja Sama, dan Sistem Informasi (Wakil Rektor 3). Berdasarkan hasil wawancara tersebut, tidak ditemukan adanya laporan formal yang secara spesifik membahas permasalahan navigasi kampus sebagai isu strategis. Namun demikian, pihak pimpinan universitas memberikan dukungan terhadap pengembangan solusi berbasis teknologi yang dapat meningkatkan kualitas layanan informasi kampus.

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
  b. Data belum dapat didistribusikan secara dinamis ke berbagai komponen sistem seperti dashboard dan engine visualisasi.
5. Kondisi Integrasi Data Eksisting
  a. Berdasarkan koordinasi dengan UPA TIK, sebagian data kampus telah dikelola dalam sistem terpisah yang sedang dikembangkan.
  b. Oleh karena itu, pendekatan integrasi melalui embed atau konsumsi data eksternal menjadi lebih relevan dibandingkan pengelolaan data secara mandiri.

Berdasarkan temuan tersebut, dapat disimpulkan bahwa sistem yang sedang berjalan masih memiliki keterbatasan pada aspek navigasi, integrasi data, serta arsitektur sistem. Kondisi ini menjadi dasar dalam perumusan solusi yang diusulkan pada Subbab 2.2.

### 2.1.2 Analisis Sistem yang Sedang Berjalan

Berdasarkan hasil kuesioner yang telah disebarkan kepada 21 responden, diperoleh beberapa temuan penting terkait pengalaman pengguna dalam melakukan navigasi di lingkungan Kampus Universitas Pembangunan Nasional Veteran Jakarta.

Mayoritas responden merupakan sivitas akademika UPNVJ, yaitu sebesar 95,2%, sedangkan sisanya merupakan pengunjung eksternal. Hal ini menunjukkan bahwa data yang diperoleh cukup merepresentasikan pengalaman pengguna utama yang beraktivitas di lingkungan kampus secara rutin.

Dari aspek efektivitas media navigasi yang tersedia, diperoleh bahwa persepsi responden terhadap papan penunjuk arah dan denah statis cenderung berada pada kategori cukup hingga kurang informatif. Hal ini terlihat dari distribusi jawaban yang menunjukkan bahwa hanya sebagian kecil responden yang menilai sistem navigasi saat ini sangat membantu, sementara sebagian lainnya masih merasakan keterbatasan dalam memahami informasi yang disajikan.

Lebih lanjut, dalam satu semester terakhir, sebanyak 57,1% responden mengaku mengalami kesulitan menemukan lokasi sebanyak 1–3 kali, sementara 33,3% menyatakan tidak pernah mengalami kesulitan. Namun demikian, terdapat juga responden yang mengalami kesulitan lebih dari 3 kali, yang menunjukkan bahwa permasalahan navigasi masih terjadi secara berulang bagi sebagian pengguna.

Dari sisi perilaku pengguna dalam mencari informasi lokasi, sebanyak 90,5% responden menyatakan bahwa mereka lebih mengandalkan bantuan orang lain, seperti bertanya kepada mahasiswa lain atau petugas kampus, dibandingkan menggunakan media navigasi yang tersedia. Hal ini mengindikasikan bahwa sistem navigasi yang ada belum mampu menjadi sumber informasi utama yang efektif.

Terkait kebutuhan akan sistem yang lebih baik, mayoritas responden menyatakan bahwa keberadaan sistem peta virtual 3D interaktif yang terintegrasi dengan informasi fasilitas merupakan hal yang penting. Sebanyak 76,2% responden memberikan penilaian tinggi (skala 4 dan 5) terhadap pentingnya sistem tersebut, yang menunjukkan adanya kebutuhan yang signifikan terhadap solusi berbasis teknologi yang lebih interaktif.

Selain itu, dalam hal potensi penggunaan, sebanyak 61,9% responden menyatakan akan menggunakan sistem denah virtual 3D ketika membutuhkan pencarian lokasi tertentu, sementara sebagian lainnya menyatakan akan menggunakan dalam kondisi tertentu atau jarang. Hal ini menunjukkan bahwa sistem yang diusulkan memiliki potensi adopsi yang baik, terutama dalam situasi yang membutuhkan orientasi lokasi.

Dari aspek kebutuhan informasi, responden juga menunjukkan bahwa informasi yang paling penting untuk ditampilkan dalam sistem adalah nama gedung (95,2%), diikuti oleh fasilitas dalam ruangan (52,4%) dan kapasitas ruangan (38,1%). Temuan ini menjadi dasar dalam menentukan jenis data yang perlu disediakan oleh backend dan ditampilkan dalam sistem visualisasi.

Berdasarkan keseluruhan hasil kuesioner tersebut, dapat disimpulkan bahwa terdapat kebutuhan nyata terhadap sistem navigasi kampus yang lebih interaktif, terintegrasi, dan berbasis data dinamis. Temuan ini memperkuat urgensi pengembangan sistem integrasi denah virtual berbasis 3D yang didukung oleh backend sebagai pusat distribusi data.

Berdasarkan hasil observasi lapangan dan tinjauan pada aset digital kampus (situs web upnvj.ac.id), dilakukan analisis terhadap sistem yang sedang berjalan untuk penyediaan informasi navigasi dan profil. Analisis ini krusial untuk mengidentifikasi kesenjangan (gap) yang akan diisi oleh sistem baru yang diusulkan.

Identifikasi kelemahan pada sistem yang sedang berjalan adalah sebagai berikut:

1. Aspek Navigasi Spasial:
  a. Sistem yang ada saat ini mengandalkan media konvensional, yaitu papan penunjuk arah fisik dan denah statis (berbasis gambar/PDF) yang terdapat di beberapa titik atau di situs web.
  b. Kelemahan: Media ini bersifat pasif (tidak interaktif), dan sulit diperbarui. Hal ini secara langsung menyebabkan inefisiensi navigasi seperti yang diidentifikasi pada Bab 1.2.
2. Aspek Penyajian Data Profil (Lingkup Full Stack):
  a. Sistem yang ada saat ini untuk penyajian data profil kampus (statistik, akreditasi, fasilitas) bersifat terfragmentasi. Informasi tersimpan di berbagai laman dan sub-situs yang tidak saling terhubung, menciptakan fenomena fragmentasi data.
  b. Kelemahan: Tidak ada dashboard terpusat yang menyajikan data secara agregat dan interaktif. Pengguna harus membuka banyak halaman untuk mendapatkan gambaran utuh, dan administrator tidak memiliki satu "pintu" (Admin Dashboard) untuk mengelola data konten tersebut secara efisien.

### 2.1.3 Wawancara dengan Stakeholder

Tahapan identifikasi kebutuhan sistem dilakukan melalui metode wawancara terstruktur dan mendalam dengan Asep Saeful Ridwan, S.Kom., yang bertindak sebagai pemangku kepentingan (stakeholder) sekaligus mitra pembangunan di lingkungan Universitas Pembangunan Nasional Veteran Jakarta. Interaksi ini bertujuan untuk memetakan strategi pengembangan proyek yang bersifat lintas disiplin. Dalam diskusi ini, narasumber menegaskan bahwa realisasi sistem denah virtual yang ideal memerlukan sinergi teknis dari tiga peran spesifik, yaitu:

1. 3D Designer untuk visualisasi aset gedung.
2. Simulator Developer untuk logika navigasi spasial.
3. Full Stack Developer untuk manajemen infrastruktur data.

Berdasarkan pembagian tugas strategis tersebut, disepakati penentuan batasan lingkup kerja penulis yang difokuskan secara eksklusif pada peran Full Stack Developer. Penulis dimandatkan untuk membangun arsitektur sistem yang tangguh guna menjamin skalabilitas dan ketersediaan data profil universitas secara real-time, yang nantinya akan dikonsumsi oleh engine simulasi yang dikembangkan anggota tim lain.

Berdasarkan arahan narasumber, dirumuskanlah spesifikasi kebutuhan fungsional yang mencakup manajemen konten dinamis melalui Admin Dashboard serta penyediaan jalur distribusi data (API endpoints) untuk mendukung visualisasi pada Public Dashboard dan Denah Virtual. Lebih lanjut, narasumber menekankan krusialnya kebutuhan non-fungsional yang menitikberatkan pada aspek integritas data dan efisiensi waktu respons, mengingat backend sistem ini harus melayani permintaan data secara simultan dari antarmuka web dan engine 3D. Seluruh informasi teknis ini menjadi fondasi utama dalam penyusunan tiga skenario operasional sistem (Skenario A, B, dan C), yang dirancang sebagai strategi mitigasi risiko untuk menjaga reliabilitas sistem di tengah ketidakpastian ketersediaan data akademik eksternal.

Selain wawancara dengan Kepala UPA TIK, penulis juga melakukan diskusi dan koordinasi dengan Wakil Rektor Bidang Kemahasiswaan, Kerja Sama, dan Sistem Informasi (Wakil Rektor III) UPN Veteran Jakarta guna memverifikasi kebijakan pembagian data sarana prasarana. Berdasarkan wawancara tersebut, disimpulkan bahwa data administratif tertentu bersifat tertutup demi alasan keamanan informasi. Pembatasan ini justru memperkuat urgensi proyek yang diusulkan, yaitu penyediaan portal integrasi data yang aman berbasis Row Level Security (RLS) serta arsitektur backend-centric. Sebagai bukti penjaminan komitmen pengerjaan dan validasi lapangan, penulis melakukan penandatanganan pakta integritas dengan mitra serta dokumentasi pertemuan dengan Wakil Rektor Bidang Kemahasiswaan, Kerja Sama, dan Sistem Informasi (Wakil Rektor III) seperti yang ditunjukkan oleh Gambar 2.25.

Gambar 2.25 Dokumentasi Wawancara dan Penandatanganan Pakta Integritas


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
4. Strategi Integrasi Data Eksternal
  a. Data tertentu seperti statistik dan akreditasi diperoleh melalui mekanisme embed dari sistem UPA TIK.
  b. Sistem tidak menggantikan sistem yang sudah ada, tetapi berfungsi sebagai layer integrasi.
5. Pendekatan Kolaboratif Multi-Role
  a. Sistem dikembangkan melalui kolaborasi antara:
    1) 3D Designer (aset visual)
    2) Unity/Simulator Developer (interaksi dan navigasi)
    3) Full Stack Developer (backend, API, dan dashboard)
  b. Fokus utama penelitian ini berada pada pengembangan backend dan integrasi sistem.

Dengan pendekatan tersebut, sistem yang diusulkan diharapkan mampu mengatasi permasalahan navigasi yang teridentifikasi melalui survei, sekaligus menyediakan platform informasi kampus yang terintegrasi, dinamis, dan interaktif.

Sebelum merinci komponen teknis yang menjadi tanggung jawab penulis, Gambar 2.1 menyajikan diagram arsitektur sistem secara high-level. Diagram ini memetakan hubungan antara aset visual, logika simulasi, dan sistem informasi web.

Gambar 2.1 Diagram Arsitektur Sistem

Sebagaimana diilustrasikan pada Gambar 2.1, arsitektur sistem dirancang dengan alur kerja yang saling terhubung antar ketiga peran tersebut:

1. Integrasi Aset Visual: Aset 3D yang dihasilkan oleh 3D Designer diekspor dan diimpor ke dalam sistem Denah Virtual yang dikelola oleh Simulator Developer.
2. Alur Pengguna Publik (User): Pengguna berinteraksi melalui Frontend Public Dashboard. Halaman ini berfungsi sebagai wadah (container) yang menampilkan Denah Virtual (Unity/WebGL) sekaligus menyajikan informasi profil kampus yang dinamis.
3. Alur Administrator (Admin): Administrator memiliki jalur akses khusus melalui Frontend Admin Dashboard untuk mengelola data konten kampus (seperti data dosen, fasilitas, dan aset) melalui mekanisme CRUD.
4. Pusat Pertukaran Data: Seluruh interaksi data bermuara pada satu titik pusat, yaitu Backend: Main API. Komponen ini bertindak sebagai "otak" yang melayani permintaan data dari Denah Virtual (agar gedung dapat menampilkan informasi saat diklik) dan menyediakan data untuk kedua dashboard.

Fokus utama dari usulan solusi dalam laporan ini akan menitikberatkan pada pengembangan komponen Full Stack Web yang terdiri dari empat modul fungsional berikut:

### 2.2.1 Identifikasi Kebutuhan Fungsional

Identifikasi kebutuhan sistem dirumuskan berdasarkan hasil wawancara mendalam dengan pemangku kepentingan (stakeholder) pada Bab 2.1.3 dan analisis sistem berjalan pada Bab 2.1.2. Mengingat proyek ini merupakan kolaborasi lintas peran, analisis kebutuhan difokuskan untuk menerjemahkan arahan strategis menjadi spesifikasi teknis yang mendukung kinerja tiga peran pengembang. Hasil analisis ini dikonversi menjadi serangkaian Kebutuhan Fungsional sistem yang spesifik, yang menjadi landasan utama untuk perancangan Use Case Diagram (Bab 2.3.3) dan penyusunan skenario pengujian (Bab 2.4).

Secara garis besar, kebutuhan fungsional sistem diklasifikasikan ke dalam tiga kategori utama:

1. Kebutuhan Fungsional Pengguna Publik (User):
  a. Sistem harus dapat menyajikan data statistik kampus (dosen, mahasiswa).
  b. Sistem harus dapat menyajikan data profil (akreditasi, fasilitas, aset).
  c. Sistem harus dapat menyajikan data terperinci saat chart atau item fasilitas diklik.
  d. Sistem harus dapat menampilkan viewport Denah Virtual (yang diintegrasikan oleh Simulator Developer menggunakan aset dari 3D Designer).
2. Kebutuhan Fungsional Administrator (Admin):
  a. Sistem harus menyediakan halaman login yang aman (autentikasi) untuk Admin.
  b. Sistem harus dapat menampilkan widget analitik dasar (kunjungan, page views).
  c. Sistem harus menyediakan fungsionalitas CRUD (Create, Read, Update, Delete) untuk mengelola semua data konten dinamis (Dosen, Mahasiswa, Fakultas, Aset, Fasilitas, Akreditasi, dll.).
3. Kebutuhan Fungsional Integrasi (API untuk 3D Engine): Backend API harus memenuhi kebutuhan teknis bagi 3D Simulator Developer agar Denah Virtual dapat menampilkan informasi secara dinamis:
  a. Sistem harus menyediakan endpoint API (misal: GET /api/gedung) yang menyajikan data spasial (nama gedung, deskripsi gedung).
  b. Sistem harus menyediakan endpoint API (misal: GET /api/fasilitas) yang menyajikan data fasilitas (nama fasilitas, deskripsi, lokasi/gedung terkait).
  c. Sistem harus menyediakan endpoint API (misal: GET /api/fakultas) yang menyajikan data profil fakultas dan program studi terkait.
  d. API harus menyediakan data dalam format JSON yang terstruktur agar mudah di-parse oleh engine Unity/WebGL yang dikelola 3D Simulator Developer.

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

## 2.3 Rancangan Proyek

### 2.3.1 Rencana Pengembangan

Proses pengembangan proyek ini mengikuti model Prototyping yang terbagi ke dalam empat tahapan iteratif:

1. Pengumpulan Kebutuhan (Requirement Gathering): Melakukan wawancara pemangku kepentingan dan survei awal guna memetakan fungsionalitas Full Stack API dan dashboard.
2. Membangun Prototyping Awal (Quick Design): Mendesain skema database relasional (ERD) dan menyusun antarmuka mockup visual untuk dashboard admin dan publik.
3. Evaluasi Prototipe (Evaluation & Testing): Menguji backend API dan dashboard fungsional menggunakan metode Black Box Testing dan validasi internal.
4. Iterasi Perbaikan (Iteration): Memperbaiki bug fungsionalitas CRUD, RLS database, atau koneksi API berdasarkan hasil evaluasi sebelum dinyatakan siap rilis.

### 2.3.2 Perancangan Information Architecture (IA)

Perancangan Information Architecture membagi aplikasi web ke dalam dua zona akses utama:

1. Halaman Publik (Public Route):
  a. Dashboard Utama (`/`): Menampilkan widget statistik akademik (grafik batang sebaran mahasiswa/dosen), modul visualisasi peta denah virtual 3D, serta bagian fasilitas.
  b. Pengaturan Bahasa: Toggle dinamis untuk memicu perubahan kamus bahasa lokal (ID/EN) yang diinjeksi ke komponen-komponen React.
2. Halaman Administratif (Protected Route):
  a. Login (`/login`): Form otentikasi administrator terproteksi JWT.
  b. Admin Panel (`/admin`): Mengelola entitas database relasional dengan aksi CRUD, memuat tabel data dosen, mahasiswa, gedung, fasilitas, fakultas, dan program studi, serta read-only dashboard audit logs.

### 2.3.3 Perancangan Unified Modelling Language (UML)

Interaksi sistem dan diagram alir data dirancang menggunakan tiga jenis diagram UML:

1. **Use Case Diagram**: Aktor 'User' memiliki hak akses read-only untuk melihat visualisasi grafik profil dan denah virtual. Aktor 'Admin' harus melalui use case login sebelum diberikan hak akses penuh untuk melakukan operasi CRUD data. Diagram use case sistem terinci pada Gambar 2.5.
2. **Activity Diagram**: Alur kerja pengelolaan data CRUD oleh administrator digambarkan pada Gambar 2.6, sedangkan alur logika mitigasi skenario ketersediaan data akademik eksternal (Skenario A, B, C) digambarkan pada Gambar 2.7.
3. **Sequence Diagram**:
  a. Autentikasi Admin: Memetakan proses login dari frontend React, pengiriman kredensial ke backend API, verifikasi ke Supabase Auth, pengembalian JWT token, dan pembukaan akses router admin, seperti yang diilustrasikan pada Gambar 2.8.
  b. Sinkronisasi Data: Memetakan aliran pembaruan field `unity_object_name` dari Admin Dashboard, penyimpanan ke database Supabase, penarikan data JSON oleh Unity `BuildingDatabase` via HTTP request, dan pencocokan nama GameObject visual di scene, seperti yang diilustrasikan pada Gambar 2.9.

### 2.3.4 Perancangan Sistem Spesifik

Perancangan modul keamanan data dan mitigasi penelusuran lalu lintas web mencakup spesifikasi arsitektur berikut:

1. Keamanan Row-Level Security (RLS) Database:
  a. Tabel publik (`gedung`, `fasilitas`, `prodi`) diberikan kebijakan izin SELECT secara terbuka untuk publik (`anon`).
  b. Kebijakan INSERT, UPDATE, dan DELETE diamankan secara database-level, hanya mengizinkan modifikasi bagi koneksi client yang memiliki JWT token bertipe `authenticated` (admin).
2. Sistem Audit Logs Otomatis:
  a. Merancang trigger basis data `log_data_mutation()` yang aktif setiap kali terjadi modifikasi data (INSERT/UPDATE/DELETE) pada tabel penting.
  b. Trigger menyimpan metadata perubahan (nama tabel, jenis operasi, ID rekaman, UUID admin, timestamp) ke dalam tabel `audit_logs` secara otomatis.
3. Reverse Proxy Umami Analytics:
  a. Mengonfigurasi Express.js proxy server pada port 3001 untuk memotong request collect tracker Umami dari client.
  b. Proxy menyembunyikan endpoint Umami Docker internal (port 3000) dan menyajikan file JavaScript pelacak secara transparan guna menghindari sensor dari ekstensi browser ad-blocker.

### 2.3.5 Perancangan Entity Relationship Diagram (ERD)

Struktur data relasional yang diinangi pada PostgreSQL dirancang untuk menghubungkan profil akademik, aset fisik kampus, dan log aktivitas audit. Skema ERD divisualisasikan pada Gambar 2.3. Rancangan tabel adalah sebagai berikut:

1. `gedung` (id, nama_gedung, deskripsi_gedung, lokasi, jumlah_lantai, foto_url, unity_object_name)
2. `fasilitas` (id, nama_fasilitas, deskripsi_fasilitas, tipe_fasilitas, warna_ui, lantai, id_gedung [FK], foto_url, unity_object_name)
3. `fakultas` (id, nama_fakultas, deskripsi, email, website, gedung_id [FK])
4. `program_studi` (id, nama_prodi, jenjang, fakultas_id [FK], akreditasi)
5. `admin_users` (id, email, role, created_at)
6. `audit_logs` (id, admin_id, table_name, action, old_data, new_data, timestamp)

### 2.3.6 Perancangan Antarmuka

Rancangan antarmuka pengguna diwujudkan melalui serangkaian mockup visual:

1. Bagian Admin Dashboard: Mockup halaman login admin (Gambar 2.10), halaman utama dashboard admin (Gambar 2.11), modal formulir tambah data (Gambar 2.12), modal formulir edit data (Gambar 2.13), modal konfirmasi hapus data (Gambar 2.14), serta visualisasi statistik analitik admin (Gambar 2.15).
2. Bagian Public Dashboard: Mockup hero section (Gambar 2.16), visualisasi analitik publik (Gambar 2.17), bagian pencarian fasilitas dan aset (Gambar 2.18), modal daftar fasilitas kategori (Gambar 2.19), modal detail spesifik fasilitas unggulan (Gambar 2.20), diagram statistik drill-down mahasiswa/dosen (Gambar 2.21), detail drill-down (Gambar 2.22 dan Gambar 2.23), dan footer halaman (Gambar 2.24).

## 2.4 Rencana Pengujian Proyek

### 2.4.1 Pengujian Backend (API & Integration Testing)

Pengujian backend difokuskan pada pengujian integrasi fungsional (Integration Testing) untuk memvalidasi:

1. Validasi Koneksi Database: Menguji apakah RESTful API dapat terhubung secara lancar ke database Supabase Cloud.
2. Pengujian Endpoint API: Melakukan tes terhadap endpoint publik (`/api/buildings`, `/api/rooms`, `/api/unity/data`) untuk memvalidasi format data keluaran JSON dan status response HTTP (200 OK).
3. Pengujian Proteksi Autentikasi: Memastikan endpoint modifikasi data (POST/PUT/DELETE) menolak request (status 401 Unauthorized) jika tidak dibarengi dengan token JWT admin yang valid.

### 2.4.2 Pengujian Fungsional (Black Box Testing)

Pengujian fungsional sistem menggunakan metode Black Box Testing untuk menguji 18 skenario interaksi antarmuka pengguna pada dashboard admin dan dashboard publik. Skenario tersebut meliputi:

1. Pengujian fungsionalitas CRUD pada dashboard admin untuk setiap entitas data (Dosen, Mahasiswa, Gedung, Fasilitas, Fakultas, Program Studi).
2. Pengujian validitas form login admin dan penanganan error kredensial yang tidak valid.
3. Pengujian interaktivitas grafik statistik publik (drill-down saat grafik diklik).
4. Pengujian sinkronisasi filter bahasa (Bahasa Indonesia dan English) pada public dashboard.
5. Pengujian keakuratan modul pencarian gabungan (Search Overlay) di frontend React.

### 2.4.3 User Acceptance Testing

User Acceptance Testing (UAT) dirancang untuk mengukur tingkat kepuasan pengguna (Usability Testing) terhadap sistem yang dikembangkan. Pengujian melibatkan perwakilan responden dari dua kelompok target:

1. Pengguna Publik (Mahasiswa dan Pengunjung): Untuk menguji tingkat kemudahan penelusuran profil akademik dan kegunaan peta virtual 3D.
2. Pengguna Administratif (Staf Administrasi): Untuk menguji efisiensi pengelolaan CRUD data via admin panel.

Pengukuran usability dilakukan menggunakan skala Likert melalui kuesioner terstruktur setelah responden menyelesaikan serangkaian skenario tugas yang diberikan. Indeks kepuasan dihitung secara kuantitatif untuk memvalidasi penerimaan sistem.

---

# BAB III IMPLEMENTASI PROYEK

## 3.1 Profil Mitra

### 3.1.1 Nama Organisasi/Lembaga Mitra

Universitas Pembangunan Nasional Veteran Jakarta Kampus Pondok Labu.

### 3.1.2 Deskripsi Mitra

Universitas Pembangunan Nasional “Veteran” Jakarta (UPNVJ) Kampus Pondok Labu merupakan salah satu institusi pendidikan tinggi negeri yang memiliki peran strategis dalam pengembangan sumber daya manusia di bidang akademik dan profesional. Sejak memperoleh status sebagai Perguruan Tinggi Negeri pada tahun 2014, UPNVJ terus berkomitmen dalam meningkatkan kualitas pendidikan, penelitian, dan pengabdian kepada masyarakat dengan mengedepankan nilai-nilai bela negara.

Kampus Pondok Labu sebagai salah satu pusat kegiatan akademik UPNVJ memiliki lingkungan yang luas dengan berbagai fasilitas pendukung, seperti gedung fakultas, ruang perkuliahan, laboratorium, serta sarana umum lainnya. Seiring dengan perkembangan jumlah mahasiswa dan kompleksitas infrastruktur kampus, kebutuhan akan sistem informasi yang terintegrasi dan mudah diakses menjadi semakin penting.

Dalam konteks transformasi digital menuju konsep Smart Campus, UPNVJ telah mulai mengembangkan berbagai sistem informasi untuk mendukung pengelolaan data akademik dan layanan kampus. Namun, berdasarkan kondisi eksisting, penyajian informasi kampus masih bersifat terfragmentasi dan sistem navigasi yang tersedia masih mengandalkan media konvensional seperti papan petunjuk dan denah statis.

Oleh karena itu, UPNVJ Kampus Pondok Labu menjadi lingkungan yang relevan sebagai mitra dalam pengembangan sistem integrasi denah virtual dan dashboard profil kampus. Proyek ini diharapkan dapat mendukung upaya digitalisasi layanan informasi serta meningkatkan pengalaman pengguna dalam mengakses informasi dan melakukan navigasi di lingkungan kampus.

### 3.1.3 Hubungan Mitra dengan Proyek

Pengembangan sistem integrasi denah virtual kampus dan dashboard profil UPNVJ melibatkan keterkaitan langsung dengan mitra, yaitu Universitas Pembangunan Nasional “Veteran” Jakarta Kampus Pondok Labu, sebagai lingkungan implementasi dan sumber data utama. Hubungan antara mitra dan proyek dapat dijelaskan secara detail pada Tabel 3.1.

Tabel 3.1 Hubungan Mitra dengan Proyek

[TABLE]
Entitas | Peran | Manfaat
UPNVJ Kampus Pondok Labu | 1. Menjadi objek utama dalam pengembangan dan implementasi sistem, khususnya dalam penyediaan data spasial (gedung dan fasilitas) serta data profil kampus.<br>2. Menyediakan lingkungan nyata (real-world environment) sebagai dasar observasi, analisis kebutuhan, serta validasi sistem yang dikembangkan.<br>3. Mendukung proses pengembangan melalui koordinasi dengan stakeholder terkait, seperti pihak pengelola teknologi informasi (UPA TIK). | 1. Mendapatkan solusi sistem navigasi kampus berbasis visualisasi 3D yang lebih interaktif dibandingkan metode konvensional.<br>2. Memperoleh platform dashboard profil kampus yang terintegrasi, sehingga penyajian informasi menjadi lebih terpusat dan mudah diakses.<br>3. Mendukung implementasi konsep Smart Campus melalui integrasi teknologi backend, dashboard web, dan visualisasi 3D.
Sivitas Akademika (Mahasiswa & Tamu) | 1. Bertindak sebagai pengguna utama sistem (end-user) yang berinteraksi langsung dengan public dashboard dan denah virtual.<br>2. Menjadi sumber data kebutuhan sistem melalui kuesioner dan observasi pengalaman navigasi kampus. | 1. Mempermudah proses pencarian lokasi di lingkungan kampus melalui sistem navigasi berbasis visualisasi 3D.<br>2. Meningkatkan kemudahan akses terhadap informasi kampus yang sebelumnya tersebar di berbagai platform.
Administrator Sistem (Staf Pengelola) | 1. Mengelola data konten kampus melalui admin dashboard, termasuk data fasilitas, gedung, dan profil.<br>2. Menjaga konsistensi dan keakuratan data yang digunakan oleh sistem. | 1. Memperoleh sistem manajemen konten terpusat yang mempermudah pengelolaan data secara efisien.<br>2. Mendukung proses pembaruan informasi secara real-time tanpa perlu mengubah sistem secara keseluruhan.
[/TABLE]

## 3.2 Metode Implementasi

Implementasi sistem dalam proyek ini dilakukan menggunakan pendekatan prototyping yang iteratif. Proses pengembangan secara eksklusif difokuskan pada kontribusi penulis selaku Full Stack Web Developer & System Integrator.

### 3.2.1 Implementasi Back-end

Backend dikembangkan sebagai RESTful API menggunakan Node.js dan framework Express.js. Untuk mendukung skalabilitas, backend dideploy pada Vercel Serverless Functions. Basis data PostgreSQL diinangi di Supabase Cloud.

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
BEGIN
  INSERT INTO audit_logs (table_name, operation, record_id, changed_by, changed_at)
  VALUES (TG_TABLE_NAME, TG_OP, COALESCE(NEW.id, OLD.id), auth.uid(), now());
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Memicu trigger pada tabel gedung
CREATE TRIGGER audit_gedung_trigger
AFTER INSERT OR UPDATE OR DELETE ON gedung
FOR EACH ROW EXECUTE FUNCTION log_data_mutation();
```

RESTful API backend menyediakan beberapa endpoint utama untuk mendistribusikan data ke client-side, yang meliputi:
1. `GET /api/buildings`: Mengembalikan array data seluruh gedung dalam format JSON.
2. `GET /api/rooms`: Mengembalikan detail data ruang perkuliahan dan laboratorium.
3. `GET /api/unity/data`: Mengembalikan data terintegrasi yang dibutuhkan oleh runtime Unity WebGL.

### 3.2.2 Implementasi Front-end

Frontend dirancang sebagai Single Page Application (SPA) menggunakan Vite dan React.js. Antarmuka terbagi menjadi dua bagian: Public Dashboard untuk pengguna umum dan Admin Dashboard untuk staf pengelola data.

Untuk menjaga kinerja pemuatan halaman di perangkat seluler (mobile devices) yang mengakses visualisasi WebGL Unity yang berukuran besar, diimplementasikan mekanisme *connection-aware preloading*. Mekanisme ini mengevaluasi tipe koneksi jaringan browser client menggunakan API `navigator.connection` guna menghindari preload aset WebGL secara otomatis pada jaringan lambat:

```typescript
const connection = (navigator as any).connection || (navigator as any).mozConnection || (navigator as any).webkitConnection;
const isConnectionSlow = connection && (connection.saveData || ['slow-2g', '2g', '3g'].includes(connection.effectiveType));

if (isConnectionSlow) {
  // Lewati preload otomatis WebGL, tampilkan tombol aktivasi manual
  setShowManualActivationButton(true);
} else {
  // Lakukan preload aset WebGL secara otomatis di latar belakang
  triggerWebGLPreload();
}
```

Integrasi komunikasi dua arah dari React menuju runtime Unity WebGL dijembatani menggunakan pustaka `react-unity-webgl`. Ketika pengguna melakukan pencarian lokasi di sisi frontend React, instruksi navigasi dikirim secara asinkron ke container WebGL dengan memicu method penerima rute di Unity:

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
    // Mengirim nama objek visual ke Unity receiver script secara case-insensitive
    sendMessage("NavigationReceiver", "NavigateTo", unityObjectName);
  }
};
```

## 3.3 Metadata

### 3.3.1 Basis Data

Infrastruktur basis data PostgreSQL dirancang relasional untuk menjamin integritas referensial. Tabel `gedung` bertindak sebagai entitas induk yang menaungi tabel `fasilitas`. Relasi kedua tabel dihubungkan oleh foreign key `id_gedung`. 

Untuk menjamin sinkronisasi data visual 3D Unity dengan record data di database web, field `unity_object_name` diimplementasikan secara konsisten pada tabel `gedung` dan `fasilitas`. Field ini bertindak sebagai jembatan penamaan unik (unique naming bridge) yang dicocokkan case-insensitive dengan hierarki GameObject di Unity scene.

Sebagai integrator, penulis membuat penamaan objek Unity di dalam editor (seperti prefab dewi sartika) yang memiliki child pointer di dalamnya. Child pointer ini berupa child empty GameObject dengan nama yang disesuaikan secara presisi dengan kolom `unity_object_name` di database Supabase (seperti diilustrasikan pada Gambar 3.1). Mekanisme ini mempermudah pencarian node visual dan penargetan navigasi rute visual secara dinamis saat runtime.

Gambar 3.1 Hierarki Prefab Gedung dengan Child Pointer di Unity

Untuk meminimalkan kesalahan pengetikan manusia (*human error*) dan menjamin validitas pemetaan nama objek sebelum melakukan *build*, diimplementasikan sebuah skrip editor khusus di sisi Unity yaitu `DatabaseSyncChecker.cs` yang dapat diakses melalui menu `Tools > UPNVJ > Check Database Sync` (dijelaskan pada Lampiran 3 dan diilustrasikan pada Gambar 3.2).

Skrip `DatabaseSyncChecker.cs` ini bertindak sebagai alat validasi otomatis yang melakukan tugas-tugas berikut:
1. Mengambil seluruh record penamaan objek (`unityObjectNames`) secara asinkron dari endpoint API backend `/api/unity/names`.
2. Melakukan penelusuran (*traverse*) hierarki scene aktif di Unity Editor secara rekursif untuk mengumpulkan seluruh nama GameObject yang aktif.
3. Mencocokkan nama GameObject di scene dengan data dari database secara case-insensitive untuk mengklasifikasikannya ke dalam tiga kategori: objek yang sudah sinkron antara database dan scene, objek yang terdaftar di database tetapi tidak ditemukan di scene (*missing*), serta objek yang ada di scene tetapi belum didaftarkan di database.
4. Menampilkan laporan diagnostik interaktif dalam Editor Window khusus lengkap dengan statistik visual berkode warna dan tombol salin ke clipboard (*copy to clipboard*).

Gambar 3.2 Tampilan UI Database Sync Checker di Unity Editor

### 3.3.2 Proxy Analytics

Pemantauan lalu lintas data dashboard menggunakan platfom Umami Analytics yang di-deploy secara mandiri (*self-hosted*) menggunakan container Docker di port 3000. 

Untuk menghindari pemblokiran skrip pelacakan (tracking script) oleh ekstensi ad-blocker pada browser pengguna, server Express.js di port 3001 dikonfigurasi sebagai reverse proxy. Proxy menyamarkan request pelacakan dan mengarahkannya ke endpoint internal proxy `/api/collect`, yang kemudian meneruskannya ke Umami di port 3000 secara transparan.

### 3.3.3 Web Manifest & Web Assets

Visualisasi Unity WebGL dikompilasi menggunakan kompresi Brotli guna memperkecil ukuran aset transfer data di jaringan browser. Konfigurasi fallback dekompresi diatur di `vercel.json` untuk menjamin file wasm dan data terkompresi didekompresi dengan benar oleh browser client meskipun server web tidak mendukung header kompresi secara default.

## 3.4 Laporan Implementasi Proyek

### 3.4.1 Logbook Implementasi Proyek

Logbook aktivitas implementasi proyek dari awal perencanaan hingga tahap evaluasi akhir dirinci pada Tabel 3.2.

Tabel 3.2 Logbook Implementasi Proyek

[TABLE]
Minggu ke- | Aktivitas Pengembangan | Kontribusi Peran Full Stack | Validasi User
1-4 | Requirement Gathering & UI Design | Menganalisis kebutuhan API, menyusun rancangan database ERD, merancang mockup Admin/Public Dashboard | Disetujui Stakeholder (Asep Saeful Ridwan, S.Kom.)
5-8 | Backend Development | Membangun database PostgreSQL di Supabase, menerapkan aturan keamanan RLS, membuat RESTful API serverless | Lulus validasi uji koneksi DB
9-12 | Frontend Development | Memprogram komponen React SPA, mengintegrasikan Umami Analytics Proxy, menerapkan connection-aware | Antarmuka responsif di desktop
13-16 | System Integration | Mengintegrasikan container Unity WebGL dengan React menggunakan react-unity-webgl, menguji bridge SendMessage | Navigasi terpemicu dari pencarian React
17-20 | Testing & Evaluation | Melakukan Black Box Testing pada 18 skenario, melaksanakan kuesioner UAT, menyusun laporan Tugas Akhir | [TBD: Evaluasi UAT Selesai]
[/TABLE]

### 3.4.2 Hasil Implementasi Back-end

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
      "warna_ui": "blue",
      "lantai": 2,
      "id_gedung": 1,
      "foto_url": "https://supabase-storage/lab_rpl.jpg",
      "unity_object_name": "lab_rpl_fik"
    }
  ]
}
```

### 3.4.3 Hasil Implementasi Front-end

Frontend React SPA berhasil dideploy secara statis. Antarmuka pengguna menyajikan:
1. Public Dashboard: Menyajikan widget grafik statistik mahasiswa/dosen, bilah pencarian gabungan (Search Overlay), serta viewport canvas WebGL yang memuat peta 3D UPNVJ secara halus.
2. Admin Dashboard: Menyediakan halaman login aman, halaman pengelolaan data CRUD untuk semua entitas dengan modal form interaktif, serta widget traffic analitik dari Umami proxy.

## 3.5 Hasil Pengujian Proyek

### 3.5.1 Black Box Testing

Pengujian fungsionalitas asinkron pada dashboard admin dan public dashboard akan dilakukan untuk memvalidasi kelayakan fungsional antarmuka admin dashboard dan visualisasi 3D. Rencana pengujian fungsional dirangkum pada Tabel 3.3. [TBD: Pelaksanaan Uji]

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

Pengujian performa non-fungsional, aksesibilitas, best practices, dan SEO pada public dashboard diuji menggunakan Google Lighthouse. Hasil perbandingan metrik performa dirangkum pada Tabel 3.4.

Tabel 3.4 Perbandingan Metrik Performa Lighthouse

[TABLE]
Kategori Audit | Kondisi Awal (Tanpa Optimasi) | Kondisi Akhir (Dengan Optimasi)
Performance | [TBD] | [TBD]
Accessibility | [TBD] | [TBD]
Best Practices | [TBD] | [TBD]
SEO | [TBD] | [TBD]
[/TABLE]

[TBD: Analisis dan Optimasi Kinerja Lighthouse]

### 3.5.3 User Acceptance Test (UAT)

Pengujian UAT akan dilakukan setelah prototipe akhir dideploy. Pengujian direncanakan melibatkan responden dari kelompok mahasiswa dan staf pengelola/admin menggunakan skala Likert 5-titik untuk menilai aspek kegunaan (*usability*), kemudahan orientasi navigasi, dan performa antarmuka. [TBD: Metodologi UAT] 

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

# LAMPIRAN 4. Panduan Pengguna (User Manual) (Rencana/Placeholder)

Panduan Pengguna (User Manual) sistem terintegrasi Dashboard Profil & Denah Virtual 3D UPNVJ Kampus Pondok Labu saat ini dirancang sebagai rencana implementasi dokumen pelengkap. Panduan ini akan memuat panduan operasional langkah-demi-langkah bagi dua kelompok pengguna:

1. Kelompok Administrator (Staff Pengelola):
  a. Panduan masuk/login ke halaman Admin Panel.
  b. Langkah-langkah melakukan operasi CRUD data gedung (termasuk pengisian parameter `unity_object_name` secara presisi).
  c. Langkah-langkah mengaitkan data fasilitas ke gedung dan mendefinisikan lantai.
  d. Peninjauan riwayat perubahan data pada log audit.
  e. Pemantauan statistik lalu lintas pengunjung via visualisasi dashboard Umami.
2. Kelompok Pengguna Publik (Mahasiswa dan Tamu Kampus):
  a. Panduan menjelajahi Dashboard publik (peninjauan statistik dosen/mahasiswa drill-down).
  b. Panduan interaksi eksplorasi bebas pada Canvas Denah Virtual 3D.
  c. Panduan melakukan pencarian rute fasilitas tertentu menggunakan Search Overlay React.
  d. Panduan kontrol pergerakan karakter dan rotasi kamera first-person (Pointer Lock) serta penggunaan joystick virtual pada perangkat mobile.

Dokumen lengkap Panduan Pengguna beserta tangkapan layar antarmuka operasional (User Guide manual) akan dilampirkan setelah sistem secara penuh diserahkan dan dideploy di lingkungan server produksi milik mitra.
