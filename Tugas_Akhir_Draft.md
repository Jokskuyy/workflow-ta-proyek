Integrasi Denah Virtual Universitas Pembangunan Nasional Veteran Jakarta Kampus Pondok Labu

(Dashboard Profil)






Muhammad Iman Nugraha

2210511129



INFORMATIKA

FAKULTAS ILMU KOMPUTER

UNIVERSITAS PEMBANGUNAN NASIONAL VETERAN JAKARTA

2025







# DAFTAR GAMBAR


Gambar 2.1 Diagram Arsitektur Sistem	10

Gambar 2.2 Tahap Pengembangan	13

Gambar 2.3 Entity-Relationship Diagram	15

Gambar 2.4 Legenda Use Case Diagram	17

Gambar 2.5 Use Case Diagram	18

Gambar 2.6 Activity Diagram: Pengelolaan Data oleh Admin	19

Gambar 2.7 Activity Diagram: Integrasi Data Denah	20

Gambar 2.8 Halaman Login Admin	23

Gambar 2.9 Halaman Dashboard Admin	24

Gambar 2.10 Modal Tambah Dosen	25

Gambar 2.11 Modal Update Dosen	25

Gambar 2.12 Modal Konfirmasi Hapus Dosen	26

Gambar 2.13 Traffic Website Admin	27

Gambar 2.14 Hero Section	28

Gambar 2.15 Public Traffic Statistics Website	29

Gambar 2.16 Bagian Fasilitas dan Aset	30

Gambar 2.17 Modal List Fasilitas dan Aset	31

Gambar 2.18 Modal  Fasilitas dan Aset	32

Gambar 2.19 Bagian Statistik	33

Gambar 2.20 Detail Data Dosen	34

Gambar 2.21 Detail Data Mahasiswa	34

Gambar 2.22 Bagian Footer	35





# DAFTAR TABEL

Tabel 1.1 Peran dan Tanggung Jawab	3

Tabel 2.1 Jadwal Kegiatan	21

Tabel 2.2 Skenario Black Box Testing	37


# 










# BAB I PENDAHULUAN



## 1.1  Latar Belakang

Perkembangan transformasi digital telah mendorong institusi pendidikan tinggi untuk mengadopsi teknologi informasi secara menyeluruh dalam mendukung layanan akademik, manajemen fasilitas, dan pengalaman pengguna (Ghai, 2025). Perguruan tinggi tidak lagi dipandang semata sebagai ruang fisik pembelajaran, melainkan sebagai ekosistem digital yang menuntut penyajian informasi yang terintegrasi, mudah diakses, dan intuitif (Jamaludin & Saepuloh, 2024). Salah satu konsep yang berkembang dalam konteks ini adalah Smart Campus, yang menekankan integrasi teknologi digital untuk meningkatkan efisiensi operasional, kualitas layanan, serta pengalaman sivitas akademika dan pengunjung (Taurusta et al., 2024).

Salah satu tantangan utama dalam implementasi Smart Campus adalah penyediaan informasi spasial dan profil institusi, khususnya pada kampus dengan area yang luas dan struktur bangunan yang kompleks. Media navigasi konvensional seperti papan penunjuk arah dan denah statis berbasis gambar bersifat pasif, sulit diperbarui, serta tidak mampu menyajikan informasi secara dinamis dan terintegrasi (Siv, 2025). Kondisi ini sering menyebabkan mahasiswa baru maupun pengunjung mengalami kesulitan dalam menemukan lokasi gedung atau fasilitas tertentu, serta kesenjangan informasi terkait profil akademik dan fasilitas kampus (Taurusta et al., 2024).

Berdasarkan hasil pengumpulan data melalui kuesioner yang disebarkan kepada mahasiswa Universitas Pembangunan Nasional “Veteran” Jakarta, ditemukan bahwa 95% dari total responden pernah mengalami kesulitan dalam menemukan lokasi tertentu di lingkungan kampus. Permasalahan ini umumnya terjadi pada mahasiswa baru maupun pengunjung yang belum familiar dengan tata letak kampus. Selain itu, responden juga menunjukkan kebutuhan terhadap sistem navigasi yang lebih interaktif dan mudah diakses dibandingkan dengan media konvensional seperti papan penunjuk arah atau denah statis. Hasil survei ini memperkuat indikasi bahwa sistem informasi navigasi yang saat ini tersedia belum sepenuhnya mampu memenuhi kebutuhan pengguna secara efektif dan efisien.

Kondisi tersebut relevan dengan permasalahan yang dihadapi oleh Universitas Pembangunan Nasional “Veteran” Jakarta (UPNVJ) Kampus Pondok Labu. Kampus ini memiliki area yang luas dengan banyak fakultas dan fasilitas, sementara media informasi dan navigasi yang tersedia saat ini masih bersifat konvensional dan terfragmentasi. Berdasarkan observasi awal, belum tersedia sistem digital terintegrasi yang mampu menggabungkan navigasi spasial berbasis visualisasi 3D dengan penyajian informasi profil kampus secara terpusat dan interaktif. Oleh karena itu, penelitian ini mengusulkan pengembangan Sistem Integrasi Denah Virtual Kampus dan Dashboard Profil UPNVJ sebagai solusi digital terpadu. Sistem ini mengombinasikan visualisasi 3D interaktif lingkungan kampus, pengelolaan aset dan data spasial, serta dashboard profil kampus berbasis web yang didukung oleh arsitektur backend dan API (Muharam et al., 2023). Sistem dikembangkan sebagai proyek kolaboratif dengan pembagian peran yang jelas, sehingga setiap komponen saling mendukung dalam mewujudkan konsep Smart Campus yang efisien, informatif, dan mudah diakses (Jamaludin & Saepuloh, 2024).

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

Untuk menjaga fokus, ruang lingkup, serta kelayakan penelitian, maka batasan masalah dalam pengembangan sistem integrasi denah virtual kampus dan dashboard profil Universitas Pembangunan Nasional “Veteran” Jakarta ditetapkan sebagai berikut:

1. Pengembangan sistem difokuskan pada integrasi antara backend, dashboard berbasis web, dan visualisasi denah virtual berbasis 3D, tanpa mencakup pengembangan sistem akademik utama seperti sistem perkuliahan atau keuangan.
2. Cakupan area visualisasi dan data dibatasi pada lingkungan Kampus Universitas Pembangunan Nasional “Veteran” Jakarta Kampus Pondok Labu.
3. Data profil kampus seperti statistik mahasiswa, dosen, dan akreditasi tidak dikelola secara langsung dalam sistem backend, melainkan diperoleh melalui mekanisme integrasi atau embed dari sistem yang telah dikembangkan oleh unit terkait (UPA TIK).
4. Pengembangan pada sisi backend difokuskan pada perancangan dan implementasi REST API, pengelolaan database, serta penyediaan data secara dinamis untuk mendukung kebutuhan dashboard dan integrasi dengan engine visualisasi.
5. Sistem API yang dikembangkan mendukung penyediaan data publik serta manipulasi data (Create, Read, Update, Delete) yang dibatasi hanya untuk administrator melalui mekanisme autentikasi berbasis Supabase Auth, sehingga tidak semua endpoint dapat diakses secara terbuka oleh pengguna umum.
6. Pengembangan visualisasi 3D dibatasi pada pembuatan aset dan lingkungan virtual oleh 3D Designer, tanpa membahas secara mendalam proses teknis pemodelan dalam laporan ini.
7. Pengembangan pada sisi Unity atau simulator difokuskan pada integrasi dengan backend melalui pemanggilan API serta implementasi interaksi dasar, tanpa membahas secara mendalam pengembangan engine atau optimasi grafis tingkat lanjut.
8. Sistem yang dikembangkan tidak mencakup integrasi real-time dengan seluruh sistem internal universitas, sehingga pembaruan data bergantung pada ketersediaan sumber data eksternal atau hasil pengelolaan internal sistem.

Pembagian Peran dan Tanggung Jawab Tim

Pembagian peran dan tanggung jawab pada proyek sistem dijelaskan lebih detail dalam Tabel 1.1.

Tabel 1.1 Peran dan Tanggung Jawab


[TABLE]
Role | Tugas dan Tanggung Jawab
3D Designer | Merancang dan memproduksi aset visual tiga dimensi lingkungan kampus, termasuk pemodelan gedung dan elemen pendukung, serta melakukan optimasi aset agar sesuai untuk digunakan pada lingkungan visualisasi 3D interaktif.
3D Simulator / Engine Developer | Mengembangkan engine visualisasi 3D interaktif sebagai modul navigasi spasial, termasuk pengelolaan scene, interaksi pengguna, optimasi performa, serta integrasi data satu arah dari API ke dalam lingkungan visualisasi 3D.
Full Stack Developer (Dashboard Profile) | Merancang dan mengimplementasikan arsitektur backend dan frontend sistem, meliputi pengembangan database, RESTful API, dashboard publik, dan dashboard administrator untuk pengelolaan serta penyajian data profil kampus.
[/TABLE]



## 1.4 Tujuan dan Manfaat

Berdasarkan rumusan masalah pada Subbab 1.2 yang berkaitan dengan inefisiensi navigasi spasial, kesenjangan kebutuhan informasi pengguna, fragmentasi informasi kampus, serta belum tersedianya sistem digital terintegrasi, maka tujuan dari penelitian ini adalah sebagai berikut:

1. Mengembangkan sistem navigasi spasial kampus berbasis visualisasi 3D interaktif yang mampu meningkatkan efisiensi proses orientasi dan pencarian lokasi di lingkungan Kampus UPNVJ Pondok Labu.
2. Menyediakan media informasi kampus yang intuitif, mudah diakses, dan interaktif untuk menjawab kebutuhan pengguna akan penyajian informasi yang cepat dan mudah dipahami.
3. Mengintegrasikan informasi profil akademik, fasilitas, dan lingkungan kampus ke dalam satu sistem terpusat guna mengatasi fragmentasi sumber informasi yang selama ini terjadi.
4. Merancang dan mengimplementasikan sistem digital terintegrasi yang menggabungkan denah virtual kampus berbasis 3D dengan dashboard profil kampus sebagai solusi Smart Campus yang saling terhubung dan berkelanjutan.
Penelitian ini diharapkan dapat dirasakan oleh berbagai pihak. Bagi sivitas akademika dan pengunjung, sistem integrasi denah virtual kampus dan dashboard profil diharapkan mampu meningkatkan efisiensi navigasi dan mempermudah akses terhadap informasi kampus secara terpadu dan interaktif, sehingga mengurangi pemborosan waktu serta membantu pengguna, khususnya mahasiswa baru dan tamu, dalam beradaptasi dengan lingkungan Kampus UPNVJ Pondok Labu. Bagi pihak manajemen dan pengelola fakultas, sistem ini menyediakan media informasi digital yang terpusat, mudah dikelola, dan mudah diperbarui untuk menyajikan profil akademik, fasilitas, dan data pendukung lainnya secara akurat, sehingga dapat mendukung proses diseminasi informasi dan pengambilan keputusan manajerial. Selain itu, bagi institusi UPNVJ secara keseluruhan, penelitian ini berkontribusi dalam meningkatkan citra dan daya saing universitas sebagai institusi pendidikan yang modern dan adaptif terhadap transformasi digital, sekaligus mendukung implementasi konsep Smart Campus secara berkelanjutan.


## 1.5 Sistematika Penulisan

Sistematika penulisan ini disusun untuk memudahkan pembaca dalam memperoleh informasi serta memberikan gambaran umum mengenai “Denah Virtual Universitas Pembangunan Nasional Veteran Jakarta Kampus Pondok Labu”. Adapun sistematika penulisannya adalah sebagai berikut:

BAB I PENDAHULUAN

Bab ini memaparkan secara ringkas dan jelas mengenai latar belakang permasalahan, perumusan masalah, batasan penelitian, tujuan serta manfaat penelitian, dan juga sistematika penulisan.

BAB II RANCANGAN PROYEK

Bab ini menjelaskan tahapan-tahapan penelitian, disertai dengan uraian mengenai alat dan bahan yang digunakan, serta jadwal pelaksanaan penelitian.


# BAB II RANCANGAN PROYEK


## 2.1 Observasi

Tahap observasi awal merupakan fondasi penting dalam memahami permasalahan serta merumuskan kebutuhan sistem yang akan dikembangkan. Proses observasi dalam penelitian ini dilakukan melalui kombinasi beberapa metode, yaitu observasi lapangan, penyebaran kuesioner kepada mahasiswa, serta wawancara dengan stakeholder terkait. Pendekatan ini digunakan untuk memperoleh gambaran yang komprehensif, baik dari sisi pengguna maupun dari sisi institusi.

Berdasarkan hasil kuesioner yang telah disebarkan kepada mahasiswa, ditemukan bahwa mayoritas responden pernah mengalami kesulitan dalam menemukan lokasi tertentu di lingkungan kampus. Hal ini menunjukkan adanya permasalahan nyata pada aspek navigasi yang dirasakan langsung oleh pengguna, terutama mahasiswa baru dan pengunjung yang belum familiar dengan lingkungan kampus.

Selanjutnya, hasil observasi lapangan menunjukkan bahwa sistem navigasi yang tersedia saat ini masih mengandalkan media konvensional seperti papan penunjuk arah dan denah statis, yang bersifat pasif, tidak interaktif, serta sulit diperbarui. Kondisi ini menyebabkan keterbatasan dalam memberikan pengalaman navigasi yang efektif dan intuitif bagi pengguna.

Untuk melengkapi analisis dari sisi institusi, dilakukan wawancara dengan Wakil Rektor Bidang Kemahasiswaan, Kerja Sama, dan Sistem Informasi (Wakil Rektor 3). Berdasarkan hasil wawancara tersebut, tidak ditemukan adanya laporan formal yang secara spesifik membahas permasalahan navigasi kampus sebagai isu strategis. Namun demikian, pihak pimpinan universitas memberikan dukungan terhadap pengembangan solusi berbasis teknologi yang dapat meningkatkan kualitas layanan informasi kampus.

Selain itu, koordinasi juga dilakukan dengan unit pengelola teknologi informasi (UPA TIK) untuk memahami kondisi sistem yang sedang dikembangkan di lingkungan kampus. Hasil koordinasi menunjukkan bahwa beberapa data profil kampus, seperti statistik mahasiswa, dosen, dan akreditasi, telah dikelola dalam sistem terpisah, sehingga pendekatan integrasi melalui mekanisme embed menjadi solusi yang lebih relevan dibandingkan dengan pengelolaan data secara langsung dalam sistem yang dikembangkan.

Dengan menggabungkan hasil kuesioner, observasi lapangan, wawancara stakeholder, serta koordinasi teknis, dapat disimpulkan bahwa permasalahan utama terletak pada keterbatasan sistem navigasi yang belum interaktif serta belum terintegrasinya data dan visualisasi dalam satu platform yang terpadu. Temuan ini menjadi dasar dalam perumusan solusi sistem yang diusulkan pada penelitian ini.


### 2.1.1 Observasi Lapangan Kegiatan

Berdasarkan hasil observasi lapangan (Subbab 2.1.1), data kuesioner mahasiswa, serta analisis terhadap sistem digital yang saat ini digunakan di Universitas Pembangunan Nasional “Veteran” Jakarta, diperoleh beberapa temuan terkait kondisi sistem yang sedang berjalan sebagai berikut:

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

Berdasarkan hasil kuesioner yang telah disebarkan kepada 21 responden, diperoleh beberapa temuan penting terkait pengalaman pengguna dalam melakukan navigasi di lingkungan Kampus Universitas Pembangunan Nasional “Veteran” Jakarta.


Mayoritas responden merupakan sivitas akademika UPNVJ, yaitu sebesar 95,2%, sedangkan sisanya merupakan pengunjung eksternal. Hal ini menunjukkan bahwa data yang diperoleh cukup merepresentasikan pengalaman pengguna utama yang beraktivitas di lingkungan kampus secara rutin.


Dari aspek efektivitas media navigasi yang tersedia, diperoleh bahwa persepsi responden terhadap papan penunjuk arah dan denah statis cenderung berada pada kategori cukup hingga kurang informatif. Hal ini terlihat dari distribusi jawaban yang menunjukkan bahwa hanya sebagian kecil responden yang menilai sistem navigasi saat ini sangat membantu, sementara sebagian lainnya masih merasakan keterbatasan dalam memahami informasi yang disajikan.


Lebih lanjut, dalam satu semester terakhir, sebanyak 57,1% responden mengaku mengalami kesulitan menemukan lokasi sebanyak 1–3 kali, sementara 33,3% menyatakan tidak pernah mengalami kesulitan. Namun demikian, terdapat juga responden yang mengalami kesulitan lebih dari 3 kali, yang menunjukkan bahwa permasalahan navigasi masih terjadi secara berulang bagi sebagian pengguna.


Dari sisi perilaku pengguna dalam mencari informasi lokasi, sebanyak 90,5% responden menyatakan bahwa mereka lebih mengandalkan bantuan orang lain, seperti bertanya kepada mahasiswa lain atau petugas kampus, dibandingkan menggunakan media navigasi yang tersedia. Hal ini mengindikasikan bahwa sistem navigasi yang ada belum mampu menjadi sumber informasi utama yang efektif.


Terkait kebutuhan akan sistem yang lebih baik, mayoritas responden menyatakan bahwa keberadaan sistem peta virtual 3D interaktif yang terintegrasi dengan informasi fasilitas merupakan hal yang penting. Sebanyak 76,2% responden memberikan penilaian tinggi (skala 4 dan 5) terhadap pentingnya sistem tersebut, yang menunjukkan adanya kebutuhan yang signifikan terhadap solusi berbasis teknologi yang lebih interaktif.


Selain itu, dalam hal potensi penggunaan, sebanyak 61,9% responden menyatakan akan menggunakan sistem denah virtual 3D ketika membutuhkan pencarian lokasi tertentu, sementara sebagian lainnya menyatakan akan menggunakan dalam kondisi tertentu atau jarang. Hal ini menunjukkan bahwa sistem yang diusulkan memiliki potensi adopsi yang baik, terutama dalam situasi yang membutuhkan orientasi lokasi.


Dari aspek kebutuhan informasi, responden juga menunjukkan bahwa informasi yang paling penting untuk ditampilkan dalam sistem adalah nama gedung (95,2%), diikuti oleh fasilitas dalam ruangan (52,4%) dan kapasitas ruangan (38,1%). Temuan ini menjadi dasar dalam menentukan jenis data yang perlu disediakan oleh backend dan ditampilkan dalam sistem visualisasi.

Berdasarkan keseluruhan hasil kuesioner tersebut, dapat disimpulkan bahwa terdapat kebutuhan nyata terhadap sistem navigasi kampus yang lebih interaktif, terintegrasi, dan berbasis data dinamis. Temuan ini memperkuat urgensi pengembangan sistem integrasi denah virtual berbasis 3D yang didukung oleh backend sebagai pusat distribusi data.


### 2.1.2 Analisis Sistem yang Sedang Berjalan

Berdasarkan hasil observasi lapangan (2.1.1) dan tinjauan pada aset digital kampus (situs web upnvj.ac.id), dilakukan analisis terhadap sistem yang sedang berjalan untuk penyediaan informasi navigasi dan profil. Analisis ini krusial untuk mengidentifikasi kesenjangan (gap) yang akan diisi oleh sistem baru yang diusulkan.

Identifikasi kelemahan pada sistem yang sedang berjalan adalah sebagai berikut:

1. Aspek Navigasi Spasial:
  a. Sistem yang ada saat ini mengandalkan media konvensional, yaitu papan penunjuk arah fisik dan denah statis (berbasis gambar/PDF) yang terdapat di beberapa titik atau di situs web.
  b. Kelemahan: Media ini bersifat pasif (tidak interaktif), dan sulit diperbarui. Hal ini secara langsung menyebabkan inefisiensi navigasi seperti yang diidentifikasi pada Bab 1.2.
2. Aspek Penyajian Data Profil (Lingkup Full Stack):
  a. Sistem yang ada saat ini untuk penyajian data profil kampus (statistik, akreditasi, fasilitas) bersifat terfragmentasi. Informasi tersimpan di berbagai laman dan sub-situs yang tidak saling terhubung, menciptakan fenomena fragmentasi data.
  b. Kelemahan: Tidak ada dashboard terpusat yang menyajikan data secara agregat dan interaktif. Pengguna harus membuka banyak halaman untuk mendapatkan gambaran utuh, dan administrator tidak memiliki satu "pintu" (Admin Dashboard) untuk mengelola data konten tersebut secara efisien.

### 2.1.3 Wawancara dengan Stakeholder

Tahapan identifikasi kebutuhan sistem dilakukan melalui metode wawancara terstruktur dan mendalam dengan Erly Krisnanik, S.Kom., M.M., yang bertindak sebagai pemangku kepentingan (stakeholder) sekaligus pakar domain di lingkungan Universitas Pembangunan Nasional Veteran Jakarta. Interaksi ini bertujuan untuk memetakan strategi pengembangan proyek yang bersifat lintas disiplin. Dalam diskusi ini, narasumber menegaskan bahwa realisasi sistem denah virtual yang ideal memerlukan sinergi teknis dari tiga peran spesifik, yaitu:

1. 3D Designer untuk visualisasi aset gedung.
2. Simulator Developer untuk logika navigasi spasial.
3. Full Stack Developer untuk manajemen infrastruktur data.
Berdasarkan pembagian tugas strategis tersebut, disepakati penentuan batasan lingkup kerja penulis yang difokuskan secara eksklusif pada peran Full Stack Developer. Penulis dimandatkan untuk membangun arsitektur sistem yang tangguh guna menjamin skalabilitas dan ketersediaan data profil universitas secara real-time, yang nantinya akan dikonsumsi oleh engine simulasi yang dikembangkan anggota tim lain.

Berdasarkan arahan narasumber, dirumuskanlah spesifikasi kebutuhan fungsional yang mencakup manajemen konten dinamis melalui Admin Dashboard serta penyediaan jalur distribusi data (API endpoints) untuk mendukung visualisasi pada Public Dashboard dan Denah Virtual. Lebih lanjut, narasumber menekankan krusialnya kebutuhan non-fungsional yang menitikberatkan pada aspek integritas data dan efisiensi waktu respons, mengingat backend sistem ini harus melayani permintaan data secara simultan dari antarmuka web dan engine 3D. Seluruh informasi teknis ini menjadi fondasi utama dalam penyusunan tiga skenario operasional sistem (Skenario A, B, dan C), yang dirancang sebagai strategi mitigasi risiko untuk menjaga reliabilitas sistem di tengah ketidakpastian ketersediaan data akademik eksternal.


### 2.1.4 Analisis Kebutuhan Pengguna dan Fungsional

Identifikasi kebutuhan sistem dirumuskan berdasarkan hasil wawancara mendalam dengan pemangku kepentingan (stakeholder) pada Bab 2.1.3 dan analisis sistem berjalan pada Bab 2.1.2. Mengingat proyek ini merupakan kolaborasi lintas peran, analisis kebutuhan difokuskan untuk menerjemahkan arahan strategis menjadi spesifikasi teknis yang mendukung kinerja tiga peran pengembang: Full Stack Web Developer, 3D Designer, dan 3D Simulator Developer.

Hasil analisis ini dikonversi menjadi serangkaian Kebutuhan Fungsional sistem yang spesifik, yang menjadi landasan utama untuk perancangan Use Case Diagram (Bab 2.3.4) dan penyusunan skenario pengujian (Bab 2.4).

Secara garis besar, kebutuhan fungsional sistem diklasifikasikan ke dalam tiga kategori utama:

1. Kebutuhan Fungsional Pengguna Publik (User):
2. Sistem harus dapat menyajikan data statistik kampus (dosen, mahasiswa).
3. Sistem harus dapat menyajikan data profil (akreditasi, fasilitas, aset).
4. Sistem harus dapat menyajikan data terperinci saat chart atau item fasilitas diklik.
5. Sistem harus dapat menampilkan viewport Denah Virtual (yang diintegrasikan oleh Simulator Developer menggunakan aset dari 3D Designer).
6. Kebutuhan Fungsional Administrator (Admin):
7. Sistem harus menyediakan halaman login yang aman (autentikasi) untuk Admin.
8. Sistem harus dapat menampilkan widget analitik dasar (kunjungan, page views).
9. Sistem harus menyediakan fungsionalitas CRUD (Create, Read, Update, Delete) untuk mengelola semua data konten dinamis (Dosen, Mahasiswa, Fakultas, Aset, Fasilitas, Akreditasi, dll.). Fungsionalitas ini juga krusial untuk implementasi Rencana B (Mitigasi Risiko).
10. Kebutuhan Fungsional Integrasi (API untuk 3D Engine): Selain kebutuhan interaksi manusia, backend API (lingkup Full Stack penulis) harus memenuhi kebutuhan teknis bagi 3D/VR Simulator Developer agar Denah Virtual dapat menampilkan informasi secara dinamis:
11. Sistem harus menyediakan endpoint API (misal: GET /api/gedung) yang menyajikan data spasial (nama gedung, deskripsi gedung).
12. Sistem harus menyediakan endpoint API (misal: GET /api/fasilitas) yang menyajikan data fasilitas (nama fasilitas, deskripsi, lokasi/gedung terkait).
13. Sistem harus menyediakan endpoint API (misal: GET /api/fakultas) yang menyajikan data profil fakultas dan program studi terkait.
14. API harus menyediakan data dalam format JSON yang terstruktur agar mudah di-parse oleh engine Unity/WebGL yang dikelola 3D Simulator Developer.

### 2.1.5 Pengumpulan Data Konten dan Lokasi

Tahap pengumpulan data awal bertujuan untuk menginventarisasi seluruh konten yang akan diintegrasikan ke dalam sistem. Data yang dikumpulkan dikategorikan menjadi dua jenis, selaras dengan batasan scope Full Stack penulis, yaitu:

1. Data Konten (untuk Database): Mencakup pengumpulan data tekstual dan tabular seperti nama fakultas, daftar program studi, data akreditasi, dan daftar fasilitas. Data ini akan menjadi input utama bagi Admin Dashboard dan selanjutnya didistribusikan melalui API.
2. Data Lokasi (untuk Integrasi): Mencakup pengumpulan data identitas lokasi gedung (misalnya: "Gedung Rektorat", "Fakultas Hukum"). Data ini berfungsi sebagai "kunci penghubung" (foreign key) yang menjembatani data pada database PostgreSQL dengan objek visual terkait pada engine 3D/VR.

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

  1. 3D Designer: Bertanggung jawab atas pemodelan visual (3D modeling), tekstur, dan estetika seluruh aset gedung serta lingkungan kampus secara presisi menggunakan perangkat lunak Blender.
  2. 3D/VR Simulator Developer: Bertanggung jawab menyusun logika interaksi spasial, mekanisme navigasi, dan merakit aset 3D ke dalam engine Unity berbasis WebGL agar dapat dijalankan di peramban web.
  3. Full Stack Web Developer (Penulis): Bertanggung jawab membangun "tulang punggung" sistem yang mencakup manajemen basis data, pengembangan API (Application Programming Interface), serta antarmuka informasi (dashboard) berbasis web.
Sebelum merinci komponen teknis yang menjadi tanggung jawab penulis, Gambar 2.1 menyajikan diagram arsitektur sistem secara high-level. Diagram ini memetakan hubungan antara aset visual, logika simulasi, dan sistem informasi web.


Gambar 2.1 Diagram Arsitektur Sistem

Sebagaimana diilustrasikan pada Gambar 2.1, arsitektur sistem dirancang dengan alur kerja yang saling terhubung antar ketiga peran tersebut:

  1. Integrasi Aset Visual: Aset 3D yang dihasilkan oleh 3D Designer diekspor dan diimpor ke dalam sistem Denah Virtual yang dikelola oleh Simulator Developer.
  2. Alur Pengguna Publik (User): Pengguna berinteraksi melalui Frontend Public Dashboard (lingkup penulis). Halaman ini berfungsi sebagai wadah (container) yang menampilkan Denah Virtual (Unity/WebGL) sekaligus menyajikan informasi profil kampus yang dinamis.
  3. Alur Administrator (Admin): Administrator memiliki jalur akses khusus melalui Frontend Admin Dashboard  untuk mengelola data konten kampus (seperti data dosen, fasilitas, dan aset) melalui mekanisme CRUD.
  4. Pusat Pertukaran Data: Seluruh interaksi data bermuara pada satu titik pusat, yaitu Backend: Main API. Komponen ini bertindak sebagai "otak" yang melayani permintaan data dari Denah Virtual (agar gedung dapat menampilkan informasi saat diklik) dan menyediakan data untuk kedua dashboard.
Fokus utama dari usulan solusi dalam laporan ini akan menitikberatkan pada pengembangan komponen Full Stack Web yang terdiri dari empat modul fungsional berikut:


### 2.2.1 Pengembangan Backend (API dan Database)

Pengembangan backend dalam sistem ini berperan sebagai komponen inti yang berfungsi sebagai pusat pengelolaan dan distribusi data. Backend dirancang menggunakan pendekatan RESTful API yang memungkinkan sistem untuk menyediakan data secara terstruktur dan dapat diakses oleh berbagai komponen, termasuk dashboard berbasis web dan engine visualisasi 3D berbasis Unity WebGL.

Secara umum, pengembangan backend dalam penelitian ini mencakup beberapa aspek utama sebagai berikut:

1. Perancangan RESTful API sebagai Data Hub
  a. Backend dikembangkan untuk menyediakan endpoint API yang berfungsi sebagai jalur komunikasi utama antara database dan client.
  b. Endpoint API dirancang untuk melayani kebutuhan data baik untuk dashboard maupun Unity, seperti data gedung, fasilitas, dan profil kampus.
  c. Contoh endpoint yang digunakan antara lain:
  d. GET /api/gedung
  e. GET /api/fasilitas
  f. GET /api/search?q=kata_kunci
  g. Data yang dikirimkan menggunakan format JSON agar mudah diproses oleh frontend dan Unity.
2. Pengelolaan Database Relasional (PostgreSQL)
  a. Sistem menggunakan database PostgreSQL untuk menyimpan data terstruktur seperti fakultas, program studi, dosen, mahasiswa, fasilitas, dan gedung.
  b. Struktur database dirancang menggunakan pendekatan relasional untuk menjaga konsistensi dan integritas data.
  c. Relasi antar tabel memungkinkan pengambilan data yang kompleks secara efisien, seperti keterkaitan antara fasilitas dan gedung.
3. Penyediaan Data untuk Multi-Client (Dashboard dan Unity)
  a. Backend dirancang untuk melayani lebih dari satu jenis client, yaitu:
  b. Dashboard berbasis web (React)
  c. Engine visualisasi (Unity WebGL)
  d. Untuk kebutuhan Unity, disediakan endpoint khusus yang menyajikan data dalam format yang lebih sederhana dan langsung dapat digunakan dalam proses rendering objek 3D.
4. Implementasi Fitur Pencarian (Search Feature)
  a. Backend menyediakan fitur pencarian berbasis query parameter untuk mempermudah pengguna dalam menemukan data tertentu.
  b. Mekanisme pencarian dilakukan dengan memanfaatkan query database menggunakan keyword tertentu, sehingga hasil yang ditampilkan bersifat dinamis dan relevan.
5. Pengelolaan Akses Data dan Keamanan
  a. Backend mendukung dua jenis akses data, yaitu akses publik dan akses administratif.
  b. Endpoint publik digunakan untuk menyediakan data yang dapat diakses oleh pengguna umum dan engine Unity, seperti data gedung, fasilitas, dan profil kampus.
  c. Selain itu, sistem juga menyediakan endpoint untuk manipulasi data (Create, Read, Update, Delete) yang hanya dapat diakses oleh administrator.
  d. Mekanisme keamanan pada endpoint administratif diimplementasikan menggunakan sistem autentikasi berbasis Supabase Auth, sehingga hanya pengguna yang memiliki hak akses yang dapat melakukan perubahan data.
  e. Dengan pendekatan ini, sistem tetap terbuka untuk konsumsi data publik, namun tetap menjaga keamanan dan integritas data melalui pembatasan akses pada fungsi tertentu.
6. Arsitektur Backend Berbasis Modular
  a. Backend dikembangkan dengan struktur modular yang memisahkan komponen seperti routing, controller, dan database access.
  b. Pendekatan ini mempermudah pengembangan, pemeliharaan, serta pengujian sistem di masa mendatang.
Dengan perancangan tersebut, backend tidak hanya berfungsi sebagai penyimpan data, tetapi juga sebagai lapisan integrasi yang menghubungkan berbagai komponen sistem secara efisien. Peran ini menjadi krusial dalam memastikan bahwa data dapat disajikan secara konsisten, dinamis, dan dapat diakses oleh berbagai platform yang terlibat dalam sistem.


### 2.2.2 Integrasi Backend dengan Unity

Integrasi antara backend dan engine visualisasi berbasis Unity WebGL merupakan salah satu komponen utama dalam sistem yang dikembangkan. Integrasi ini bertujuan untuk memungkinkan penyajian informasi kampus secara dinamis dalam bentuk visualisasi spasial interaktif, sehingga pengguna tidak hanya melihat data dalam bentuk teks, tetapi juga dalam representasi lingkungan virtual.

Dalam arsitektur sistem ini, Unity berperan sebagai client yang melakukan request data ke backend melalui RESTful API. Backend kemudian merespons dengan mengirimkan data dalam format JSON yang berisi informasi terkait objek yang ditampilkan, seperti gedung, fasilitas, dan deskripsi lokasi. Data tersebut selanjutnya diproses oleh Unity untuk ditampilkan pada objek 3D yang sesuai.

Secara umum, alur integrasi sistem dapat dijelaskan sebagai berikut:

1. Pengguna melakukan interaksi pada objek dalam lingkungan 3D (misalnya klik pada gedung).
2. Unity mengirimkan request ke endpoint API backend untuk mengambil data terkait objek tersebut.
3. Backend memproses permintaan dan mengembalikan data dalam format JSON.
4. Unity menerima data dan menampilkan informasi dalam bentuk panel atau elemen antarmuka pada lingkungan 3D.
Untuk mendukung integrasi ini, backend menyediakan endpoint khusus yang dirancang agar mudah digunakan oleh Unity, dengan struktur data yang sederhana dan terfokus pada kebutuhan visualisasi. Pendekatan ini memastikan bahwa proses komunikasi antara backend dan Unity berjalan secara efisien dan tidak membebani performa sistem.

Integrasi ini juga memungkinkan sistem untuk menampilkan data secara dinamis, sehingga perubahan data pada backend dapat langsung tercermin pada visualisasi tanpa perlu melakukan perubahan pada sisi Unity. Dengan demikian, backend berperan sebagai sumber data utama yang mendukung fleksibilitas dan skalabilitas sistem visualisasi.

Melalui pendekatan ini, sistem yang dikembangkan tidak hanya berfungsi sebagai media informasi statis, tetapi juga sebagai platform interaktif yang menggabungkan data dan visualisasi dalam satu kesatuan sistem yang terintegrasi.


Diagram pada Gambar 2.1 menggambarkan arsitektur integrasi sistem yang dikembangkan dalam penelitian ini. Sistem terdiri dari tiga komponen utama, yaitu database, backend API, serta client yang terdiri dari dashboard berbasis web dan engine visualisasi Unity WebGL.

Database berfungsi sebagai penyimpan data utama yang mencakup informasi terkait gedung, fasilitas, serta data profil kampus lainnya. Data tersebut kemudian dikelola dan diakses melalui backend yang dikembangkan menggunakan pendekatan RESTful API. Backend bertindak sebagai perantara yang menghubungkan data dengan berbagai client yang membutuhkan.

Pada lapisan client, terdapat dua komponen utama, yaitu dashboard berbasis web yang dikembangkan menggunakan React, serta engine visualisasi berbasis Unity WebGL. Keduanya mengakses data yang sama melalui endpoint API yang disediakan oleh backend, sehingga menjamin konsistensi informasi yang ditampilkan.

Dashboard digunakan untuk menyajikan informasi dalam bentuk teks, grafik, dan elemen antarmuka interaktif, sedangkan Unity digunakan untuk menyajikan representasi spasial dalam bentuk visualisasi 3D. Melalui pendekatan ini, pengguna dapat memperoleh informasi kampus baik secara informatif maupun secara visual dalam satu sistem yang terintegrasi.

Arsitektur ini menunjukkan bahwa backend berperan sebagai pusat distribusi data (data hub), yang memungkinkan berbagai client untuk mengakses data secara terpusat dan dinamis. Dengan demikian, sistem menjadi lebih fleksibel, mudah dikembangkan, serta mampu mendukung integrasi lintas platform.


### 2.2.3 Pengembangan Frontend (Dashboard Interaktif)

Ini adalah "antarmuka" utama bagi pengguna untuk mengakses informasi non-spasial. Sebuah Single Page Application (SPA) akan dikembangkan menggunakan library React.js. Antarmuka ini akan menyajikan data yang diterima dari API (poin 1) secara bersih dan responsif. Frontend ini akan ditampilkan bersanding dengan viewer 3D/VR, di mana keduanya saling berinteraksi.


### 2.2.4 Implementasi Admin Dashboard (Sistem Manajemen Konten)

Ini adalah "ruang kontrol" proyek. Sebuah dashboard administratif terpisah akan dikembangkan (menggunakan React.js dan dilayani oleh API Node.js) yang memungkinkan administrator untuk melakukan fungsionalitas Create, Read, Update, Delete (CRUD) pada data di database PostgreSQL. Komponen ini sangat krusial karena juga berfungsi sebagai implementasi Skenario Alternatif (Rencana B) untuk mengelola data akademik jika akses API kampus tidak diperoleh, sebagaimana dijelaskan pada batasan masalah (1.3).


### 2.2.5 Implementasi Modul Analitik Dasar

Untuk memberikan data awal mengenai penggunaan sistem, sebuah modul analitik custom yang dasar akan diimplementasikan. Modul ini akan melacak metrik-metrik esensial seperti jumlah pengunjung unik (page visitors), total kunjungan (page views), dan tipe perangkat yang terdeteksi yang digunakan pengguna untuk mengakses sistem.


## 2.3 Rancangan Proyek

Bab ini secara khusus membahas rancangan dan implementasi komponen Full Stack yang menjadi tanggung jawab penulis dalam proyek integrasi denah virtual kampus. Fokus kontribusi penulis mencakup perancangan basis data, pengembangan RESTful API, serta pengembangan antarmuka Admin Dashboard dan Public Dashbpoard berbasis web. Sementara itu, komponen visualisasi denah virtual disajikan sebatas konteks integrasi sistem dan tidak termasuk dalam ruang lingkup pengembangan teknis penulis.


### 2.3.1 Komponen Proyek

Rancangan proyek Full Stack ini terdiri dari empat komponen fungsional utama yang akan dikembangkan oleh penulis:

1. Sistem Backend dan API: Komponen inti yang berfungsi sebagai "otak" sistem. Mencakup:
2. RESTful API (Node.js) untuk melayani data ke frontend dan engine 3D/VR.
3. Database (PostgreSQL) sebagai penyimpan data terstruktur.
4. Antarmuka Pengguna (Frontend Dashboard): Komponen client-side yang berinteraksi langsung dengan pengguna. Mencakup:
5. Dashboard Profil dan Panel Informasi (React.js).
6. Sistem Administrasi (Admin Dashboard): Komponen backend internal untuk manajemen konten. Mencakup:
7. Antarmuka Create, Read, Update, Delete (CRUD) untuk mengelola data kampus (fasilitas, profil, dll.).
8. Fungsionalitas ini juga berfungsi sebagai Rencana B (Mitigasi Risiko) untuk data akademik.
9. Modul Analitik Dasar: Komponen untuk melacak penggunaan aplikasi, mencakup:
10. Pencatatan metrik dasar (kunjungan, page views, tipe perangkat).

### 2.3.2 Teknologi yang Digunakan

Untuk membangun keempat komponen proyek Full Stack yang telah dirinci dalam Bab 2.3.1, proyek ini akan mengandalkan tumpukan teknologi (tech stack) spesifik berikut:

1. Pengembangan Antarmuka (Frontend):
Antarmuka Dashboard Profil Pengguna dan Admin Dashboard akan dikembangkan menggunakan library React.js. Teknologi ini dipilih karena kapabilitasnya dalam membangun Single Page Application (SPA) yang reaktif, cepat, dan modular, yang esensial untuk pengalaman pengguna yang modern.

1. Pengembangan Backend & API
Sisi server (logika bisnis) dan RESTful API akan dikembangkan menggunakan runtime environment Node.js (kemungkinan besar dengan framework seperti Express.js). Node.js dipilih karena arsitekturnya yang event-driven dan non-blocking I/O, yang sangat efisien untuk menangani permintaan API.

1. Manajemen Database
Untuk penyimpanan data terstruktur, proyek ini akan menggunakan PostgreSQL, sebuah sistem manajemen database relasional (Object-Relational DBMS) yang open-source dan kuat. PostgreSQL dipilih karena keandalannya (reliability), kemampuannya menangani query yang kompleks, dan skalabilitasnya yang teruji.

1. Konteks Teknologi Tim (Di Luar Lingkup Penulis)
Untuk memberikan konteks integrasi, teknologi di luar lingkup penulis (seperti engine visualisasi 3D/VR, misal: Unity/WebGL, dan software pemodelan aset, misal: Blender) akan ditangani oleh anggota yang lain. Sistem Full Stack ini akan berinteraksi dengan engine tersebut melalui endpoint API yang telah disediakan (poin 2).


### 2.3.3 Proses Pengembangan


Gambar 2.2 Tahap Pengembangan

Proses pengembangan proyek ini akan mengikuti alur kerja yang terstruktur dan sekuensial untuk memastikan setiap tahapan diselesaikan dengan matang sebelum melanjutkan ke tahap berikutnya. Alur proses ini, seperti yang diilustrasikan pada Gambar 2.2, dibagi menjadi beberapa tahapan utama:

1. Tahap Perencanaan: Tahap inisiasi ini berfokus pada pendefinisian ruang lingkup proyek. Kegiatan utamanya mencakup analisis kebutuhan fungsional (fitur-fitur sistem) dan non-fungsional (teknologi Full Stack), serta penyusunan Rencana Pengembangan (penjadwalan) dan Rencana Pengujian (perumusan skenario tes).
2. Tahap Desain: Pada tahap ini, semua "cetak biru" (blueprint) teknis sistem dirancang secara detail sebelum proses implementasi kode. Sesuai dengan scope Full Stack, tahap ini menghasilkan tiga artefak desain utama:
3. Perancangan Database (ERD): Merancang skema dan relasi database PostgreSQL.
4. Perancangan Fungsional (Use Case Diagram): Memetakan interaksi Aktor (Admin, User) dengan fungsionalitas sistem.
5. Perancangan User Interface (Mockup): Merancang mockup visual untuk Admin Dashboard dan Public Dashboard.
6. Tahap Pengodean: Tahap ini adalah implementasi dari semua artefak desain (dari Tahap 2) ke dalam kode program fungsional. Berdasarkan batasan masalah, tahap ini berfokus pada:
7. Implementasi Back-end: Membangun RESTful API (Node.js) dan database (PostgreSQL).
8. Implementasi Front-end: Membangun antarmuka Admin Dashboard dan Public Dashboard (React.js).
9. Integrasi API dengan Engine Denah Virtual: Menghubungkan endpoint API (dari Back-end) ke Front-end dan ke engine Denah Virtual (yang dikembangkan anggota yang lain).
10. Tahap Pengujian: Setelah prototipe fungsional selesai dikodekan, sistem akan diuji secara menyeluruh untuk memvalidasi fungsionalitasnya. Seperti yang diuraikan dalam diagram, metode pengujian utama yang digunakan adalah Black Box Testing, yang berfokus pada validasi skenario pengguna tanpa melihat kode internal. (Rincian skenario pengujian akan dijelaskan pada Bab 2.4).
11. Tahap Evaluasi/Iterasi Perbaikan: Hasil dari Tahap Pengujian akan dievaluasi. Jika "Pengujian Berhasil?" (semua skenario lulus), proyek dianggap selesai. Jika "Tidak" (ditemukan bug atau ketidaksesuaian fungsional), alur akan kembali ke Tahap "Pengodean" untuk perbaikan bug. Siklus Pengodean-Pengujian ini akan berulang hingga sistem dinyatakan stabil.

### 2.3.4 Rancangan Sistem dan Database


#### 2.3.4.1 Rancangan Database

Tahap perancangan basis data dimulai dengan pemodelan struktur data menggunakan Entity Relationship Diagram (ERD). ERD merupakan teknik pemodelan yang digunakan untuk menggambarkan entitas, atribut, dan hubungan antar entitas dalam suatu sistem, yang bertujuan untuk memastikan basis data yang dirancang terstruktur dengan baik, efisien, dan minim redundansi data (Afiifah, Azzahra, & Anggoro, 2022).


Rancangan skema database PostgreSQL yang diusulkan untuk proyek ini divisualisasikan secara detail pada Gambar 2.3.


Gambar 2.3 Entity-Relationship Diagram

Rancangan basis data pada sistem ini terdiri dari sembilan tabel utama yang dirancang untuk mendukung pengelolaan data akademik, spasial, serta aktivitas pengguna secara terstruktur. Beberapa tabel bersifat independen dan tidak memiliki ketergantungan hierarkis langsung, yaitu admin_users, web_analytics_log, gedung, dan akreditasi. Tabel admin_users digunakan untuk menyimpan data autentikasi dan otorisasi administrator sistem, sementara tabel web_analytics_log berfungsi untuk mencatat aktivitas kunjungan pengguna, termasuk halaman yang diakses, jenis perangkat (device_type), serta waktu kunjungan (visited_at).

Struktur data akademik dibangun secara hierarkis, dimulai dari tabel fakultas yang memiliki relasi one-to-many dengan tabel program_studi. Selanjutnya, tabel program_studi menjadi entitas penghubung utama yang memiliki relasi one-to-many dengan tabel dosen dan mahasiswa, sehingga setiap data dosen dan mahasiswa terasosiasi secara langsung dengan satu program studi tertentu. Relasi antara program_studi dan akreditasi bersifat many-to-one, yang memungkinkan satu status akreditasi digunakan oleh lebih dari satu program studi sesuai dengan kondisi aktual institusi pendidikan.

Pada aspek spasial, tabel gedung berperan sebagai entitas lokasi utama yang memiliki relasi one-to-many dengan tabel fasilitas melalui atribut id_gedung. Selain itu, tabel fakultas juga memiliki relasi opsional dengan tabel gedung melalui atribut id_gedung_utama untuk merepresentasikan gedung utama masing-masing fakultas. Pemisahan struktur data akademik dan data spasial ini dirancang untuk mendukung fleksibilitas integrasi dengan sistem visualisasi denah virtual berbasis 3D/VR serta penyajian data pada dashboard web.


#### 2.3.4.2 Rancangan Fungsional Use Case Diagram

Untuk memodelkan aspek fungsionalitas sistem, digunakan Use Case Diagram. Use Case Diagram adalah bagian dari Unified Modeling Language (UML) yang berfungsi menjelaskan aspek fungsionalitas sebuah sistem (Kurniawan, 2018). Secara spesifik, diagram ini adalah sebuah visualisasi interaksi yang terjadi antara pengguna (disebut 'Aktor') dengan sistem, yang bertujuan untuk memberikan gambaran yang jelas mengenai konteks dan batasan-batasan sistem tersebut.

Untuk membantu memahami notasi yang digunakan dalam diagram rancangan, Gambar 2.4 menyajikan legenda dari simbol-simbol Use Case Diagram yang akan digunakan.



Gambar 2.4 Legenda Use Case Diagram

Berdasarkan legenda tersebut, fungsionalitas sistem yang dirancang dari perspektif pengguna kemudian dipetakan secara visual pada Gambar 2.5.


Gambar 2.5 Use Case Diagram

Seperti yang diilustrasikan pada Gambar 2.5, diagram ini memetakan fungsionalitas dari perspektif dua aktor utama: 'User' (Pengguna Publik) dan 'Admin'. Diagram ini secara visual memvalidasi Batasan Masalah Full Stack yang telah ditetapkan:

1. Aktor 'User' memiliki akses read-only untuk melihat berbagai data (Dosen, Mahasiswa, Akreditasi, Fasilitas) dan 'Lihat Denah Virtual'. Ini adalah fungsionalitas yang akan dilayani oleh API dan ditampilkan di Public Dashboard.
2. Aktor 'Admin' memiliki fungsionalitas eksklusif untuk 'Manipulasi Data', yang merepresentasikan fungsionalitas CRUD (Create, Read, Update, Delete). Hubungan <<extend>> menunjukkan bahwa manipulasi data adalah fungsionalitas opsional yang memperluas kasus penggunaan 'Lihat Data', yang hanya dapat diakses oleh 'Admin'.

#### 2.3.4.3 Rancangan Alur Sistem (Activity Diagram)

1. Activity Diagram: Pengelolaan Data oleh Admin (CRUD)

Gambar 2.6 Activity Diagram: Pengelolaan Data oleh Admin

Keamanan dan integritas data profil pada sistem navigasi kampus sangat bergantung pada mekanisme kontrol yang ketat oleh pihak pengelola. Alur interaksi sistematis antara administrator dan perangkat lunak untuk memastikan pembaruan data yang valid dapat dianalisis melalui Activity Diagram yang disajikan pada Gambar 2.6.

Proses ini mengintegrasikan fungsi autentikasi pada Frontend dengan validasi Backend melalui RESTful API guna mencegah akses yang tidak sah. Penggunaan modal form dalam alur ini bertujuan untuk menyederhanakan prosedur CRUD (Create, Read, Update, Delete), di mana setiap masukan data akan diproses secara asinkron dan disimpan ke dalam database PostgreSQL. Metodologi pengelolaan data terpusat ini menjamin bahwa informasi yang disajikan kepada pengguna akhir selalu akurat dan konsisten dengan kondisi fisik kampus.

1. Activity Diagram: Integrasi Data Denah (Mitigasi Skenario A/B/C)

Gambar 2.7 Activity Diagram: Integrasi Data Denah

Kontinuitas penyajian informasi spasial dan akademik yang responsif memerlukan arsitektur sistem yang adaptif terhadap fluktuasi ketersediaan data eksternal. Strategi mitigasi risiko untuk menangani kendala akses pada API SIK Kampus dirancang melalui alur logika cerdas sebagaimana digambarkan pada Activity Diagram Gambar 2.7.

Logika pemrosesan di sisi Backend secara dinamis memprioritaskan Skenario A, yaitu penarikan data secara real-time untuk menjamin aktualitas informasi. Namun, sistem secara otomatis akan beralih ke Skenario B atau C (penggunaan database lokal/hibrida) jika terdeteksi adanya kegagalan konektivitas pada server universitas. Pendekatan metodologis ini krusial untuk mencapai tujuan penelitian dalam menciptakan Akses Informasi Kampus yang Mulus, di mana Dashboard tetap fungsional dan informatif bagi pengguna dalam berbagai kondisi infrastruktur jaringan.


### 2.3.5 Jadwal Kegiatan

Tabel 2.1 Jadwal Kegiatan


[TABLE]
Aktivitas | Bulan 1 | Bulan 2 | Bulan 3 | Bulan 4 | Bulan 5
 | 1 | 2 | 3 | 4 | 1 | 2 | 3 | 4 | 1 | 2 | 3 | 4 | 1 | 2 | 3 | 4 | 1 | 2 | 3 | 4
Desain Arsitektur & UI |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
Pengembangan Backend |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
Pengembangan Frontend |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
Integrasi dan Pengujian Sistem |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
Revisi Final & Penulisan Laporan |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
Dokumentasi |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
[/TABLE]


Usulan jadwal kegiatan untuk penyelesaian proyek ini dirinci dalam bentuk Gantt Chart yang menyajikan alokasi waktu pengerjaan secara bertahap, sebagaimana disajikan pada Tabel 1.1. Keseluruhan proyek ini direncanakan akan diselesaikan dalam kurun waktu 5 bulan atau 20 minggu.

Alur pengerjaan dirancang secara sekuensial dan bertahap, selaras dengan proses pengembangan yang telah diuraikan pada Bab 2.3.3 . Tahapan-tahapan tersebut adalah:

1. Desain Arsitektur & UI (Bulan 1): Tahap fondasi yang berfokus pada perancangan blueprint sistem, termasuk ERD , Use Case Diagram , dan mockup UI.
2. Pengembangan Backend (Bulan 2-3): Tahap implementasi kode sisi server, mencakup pembangunan database PostgreSQL dan RESTful API Node.js.
3. Pengembangan Frontend (Bulan 3-4): Tahap implementasi kode sisi klien, berfokus pada pembangunan Admin Dashboard dan Public Dashboard menggunakan React.js. Tahap ini berjalan tumpang tindih (overlap) dengan backend untuk efisiensi.
4. Integrasi dan Pengujian Sistem (Bulan 4-5): Tahap validasi di mana frontend dan backend diintegrasikan dan diuji secara menyeluruh menggunakan skenario pengujian Black Box .
5. Revisi Final & Penulisan Laporan (Bulan 5): Alokasi waktu khusus untuk perbaikan bug akhir berdasarkan hasil pengujian dan penyusunan draf final laporan.
6. Dokumentasi (Bulan 1-5): Aktivitas ini akan dilakukan secara paralel sepanjang proyek untuk memastikan semua proses, desain, dan kode terdokumentasi dengan baik.


### 2.3.6 User Interface

Berikut adalah rancangan antarmuka pengguna (User Interface) dalam bentuk mockup untuk komponen frontend utama yang akan dikembangkan, sesuai dengan tahapan desain yang telah dijelaskan.


#### 2.3.6.1 Antarmuka Dashboard Admin

Proses awal interaksi administrator dengan sistem diawali melalui mekanisme autentikasi yang bertujuan untuk menjaga keamanan dan integritas data yang dikelola. Halaman ini menyediakan form input berupa username dan password yang wajib diisi oleh administrator sebelum dapat mengakses sistem manajemen konten, sebagaimana ditunjukkan pada Gambar 2.8. Implementasi autentikasi ini memastikan bahwa hanya pengguna yang memiliki hak akses yang dapat melakukan manipulasi data melalui dashboard administratif.


Gambar 2.8 Halaman Login Admin

Setelah autentikasi berhasil dilakukan, administrator diarahkan menuju halaman utama dashboard yang berfungsi sebagai pusat pengelolaan data kampus. Halaman ini menampilkan ringkasan data dalam bentuk widget statistik serta tabel data terperinci yang mendukung aktivitas pemantauan dan manajemen informasi, sebagaimana divisualisasikan pada Gambar 2.9. Keberadaan tombol aksi seperti Tambah, Edit, dan Hapus pada setiap entitas data memungkinkan administrator menjalankan fungsi CRUD secara efisien dan terstruktur.



Gambar 2.9 Halaman Dashboard Admin

Interaksi pengelolaan data pada sistem ini dirancang menggunakan pendekatan modal-based form untuk menjaga fokus pengguna tanpa harus berpindah halaman. Ketika administrator menambahkan atau memperbarui data, sistem akan menampilkan formulir input dalam bentuk modal yang memuat field sesuai dengan atribut entitas terkait, seperti yang ditampilkan pada Gambar 2.10 dan Gambar 2.11. Pendekatan ini meningkatkan efisiensi alur kerja sekaligus meminimalkan kesalahan input data.




Gambar 2.10 Modal Tambah Dosen


Gambar 2.11 Modal Update Dosen


Untuk mencegah terjadinya penghapusan data secara tidak disengaja, sistem menerapkan mekanisme konfirmasi sebelum eksekusi aksi hapus dilakukan. Mekanisme ini direalisasikan melalui modal konfirmasi yang meminta persetujuan eksplisit dari administrator, sebagaimana diperlihatkan pada Gambar 2.12. Dengan adanya lapisan validasi ini, integritas data kampus dapat tetap terjaga.



Gambar 2.12 Modal Konfirmasi Hapus Dosen

Pemantauan lalu lintas penggunaan sistem pada sisi administratif dirancang tidak hanya untuk menghitung jumlah kunjungan, tetapi juga untuk menganalisis karakteristik akses pengguna secara lebih mendalam. Modul traffic website pada Dashboard Admin menyajikan informasi agregat mengenai aktivitas pengguna internal, termasuk jumlah kunjungan, frekuensi akses, serta detail perangkat (device) yang digunakan untuk mengakses sistem, sebagaimana ditampilkan pada Gambar 2.13.

Sedikit berbeda dengan modul public traffic yang berfokus pada volume kunjungan dan metrik umum pengguna eksternal, modul ini juga menampilkan klasifikasi perangkat seperti desktop, tablet, dan mobile sebagai indikator pola kerja administrator. Informasi jenis perangkat ini menjadi pembeda utama karena akses administratif umumnya dilakukan melalui perangkat kerja tertentu (misalnya desktop atau laptop), sehingga dapat digunakan untuk mengidentifikasi anomali akses maupun kecenderungan penggunaan sistem.

Keberadaan detail perangkat pada admin traffic juga memiliki implikasi terhadap evaluasi non-fungsional sistem, khususnya pada aspek usability dan security awareness. Dengan memahami perangkat yang dominan digunakan oleh administrator, pengelola sistem dapat melakukan optimalisasi antarmuka, penyesuaian kebijakan keamanan, serta perencanaan pengembangan lanjutan yang lebih tepat sasaran.


Gambar 2.13 Traffic Website Admin


#### 2.3.6.2 Antarmuka Public Dashboard

Bagian awal antarmuka public dashboard dirancang sebagai hero section yang berfungsi sebagai titik orientasi utama pengguna saat pertama kali mengakses sistem. Area ini menampilkan identitas sistem, navigasi utama, serta fitur pengaturan bahasa yang mendukung aksesibilitas bagi pengguna dengan latar belakang berbeda, sebagaimana terlihat pada Gambar 2.14. Desain ini bertujuan untuk memberikan kesan awal yang informatif dan profesional.


Gambar 2.14 Hero Section

Pemantauan aktivitas pengguna pada public dashboard dirancang untuk memberikan gambaran umum mengenai tingkat keterlibatan pengunjung terhadap sistem. Modul ini menyajikan visualisasi line chart yang merepresentasikan tren kunjungan dari waktu ke waktu, serta indikator kinerja utama (Key Performance Indicator/KPI) berupa total pengunjung, total page views, rata-rata pengunjung harian, dan rata-rata jumlah tampilan halaman, sebagaimana ditampilkan pada Gambar 2.15. Penyajian data ini bertujuan untuk membantu pengelola sistem dalam mengevaluasi efektivitas penyampaian informasi kepada publik.


Gambar 2.15 Public Traffic Statistics Website

Informasi mengenai fasilitas dan aset kampus disajikan dengan tata letak berbasis kartu yang mengelompokkan data berdasarkan kategori utama, seperti gedung kampus, laboratorium, perpustakaan, ruang kuliah, dan fasilitas pendukung lainnya. Setiap kartu menampilkan jumlah entitas yang tersedia serta menyediakan aksi lihat semua untuk eksplorasi lebih lanjut, sebagaimana diperlihatkan pada Gambar 2.16. Pendekatan visual ini dirancang untuk memberikan ringkasan cepat sekaligus kemudahan navigasi bagi pengguna.


Gambar 2.16 Bagian Fasilitas dan Aset

Ketika pengguna memilih salah satu kartu pada bagian fasilitas dan aset (selain kategori unggulan), sistem akan menampilkan modal yang berisi daftar fasilitas sesuai kategori yang dipilih. Modal ini menyajikan informasi dasar setiap fasilitas dalam bentuk daftar terstruktur, sehingga pengguna dapat melakukan penelusuran tanpa harus berpindah halaman, sebagaimana ditunjukkan pada Gambar 2.17. Desain ini mendukung prinsip efisiensi interaksi dan pengalaman pengguna yang lebih fokus.


Gambar 2.17 Modal List Fasilitas dan Aset

Untuk fasilitas yang dikategorikan sebagai unggulan, sistem menyediakan tampilan detail yang lebih informatif. Modal detail ini tidak hanya ditampilkan ketika pengguna memilih kategori fasilitas unggulan, tetapi juga akan muncul apabila pengguna menekan salah satu item pada daftar fasilitas yang tersedia. Dalam kondisi tersebut, sistem menampilkan informasi spesifik yang mencakup deskripsi lengkap fasilitas yang dipilih, sebagaimana terlihat pada Gambar 2.18. Mekanisme ini memastikan konsistensi perilaku antarmuka sekaligus memberikan konteks yang lebih mendalam mengenai fasilitas strategis kampus.



Gambar 2.18 Modal  Fasilitas dan Aset

Distribusi sumber daya akademik divisualisasikan melalui grafik batang yang menampilkan jumlah mahasiswa dan dosen pada setiap fakultas, yaitu FEB, FH, FIK, FISIP, dan FK. Visualisasi ini memungkinkan pengguna untuk membandingkan skala akademik antar fakultas secara cepat dan intuitif, sebagaimana disajikan pada Gambar 2.19. Data ini berperan penting dalam memberikan gambaran profil institusi secara kuantitatif.



Gambar 2.19 Bagian Statistik

Sistem mendukung interaksi lanjutan melalui mekanisme drill-down, di mana pengguna dapat memperoleh informasi rinci dengan mengklik salah satu batang pada grafik dosen. Aksi tersebut akan memicu penampilan detail data dosen berdasarkan fakultas yang dipilih, sebagaimana ditampilkan pada Gambar 2.20. Fitur ini menunjukkan penerapan antarmuka dinamis yang responsif terhadap interaksi pengguna.



Gambar 2.20 Detail Data Dosen

Pola interaksi yang serupa diterapkan pada data mahasiswa. Ketika pengguna memilih salah satu batang pada grafik mahasiswa, sistem akan menampilkan detail data mahasiswa sesuai fakultas terkait, sebagaimana diperlihatkan pada Gambar 2.21. Konsistensi pola interaksi ini menunjukkan penerapan prinsip reusability pada komponen antarmuka frontend.



Gambar 2.21 Detail Data Mahasiswa

Sebagai penutup halaman, sistem menyediakan bagian footer yang berfungsi sebagai pusat informasi tambahan dan navigasi cepat. Footer ini memuat tautan ke media sosial resmi UPNVJ, informasi kontak institusi, serta tautan cepat menuju situs-situs penting universitas, sebagaimana ditunjukkan pada Gambar 2.22. Keberadaan footer ini mendukung aksesibilitas informasi dan memperkuat identitas institusi secara digital.



Gambar 2.22 Bagian Footer

Perancangan antarmuka pengguna pada Admin Dashboard dan Public Dashboard tidak hanya berfokus pada aspek visual, tetapi juga mempertimbangkan kemudahan penggunaan (usability) dan konsistensi pola interaksi (user experience). Pendekatan antarmuka berbasis komponen dan interaksi dinamis diharapkan dapat membantu pengguna, khususnya mahasiswa baru dan pengunjung kampus, dalam memahami informasi secara intuitif. Rancangan antarmuka ini selanjutnya menjadi dasar dalam penyusunan skenario pengujian fungsional dan pengujian penerimaan pengguna pada tahap evaluasi sistem.



## 2.4 Rencana Pengujian Proyek

Metodologi pengujian yang digunakan dalam proyek ini dipilih berdasarkan karakteristik sistem yang berorientasi pada layanan pengguna. Pengujian Black Box digunakan karena fokus evaluasi berada pada kesesuaian fungsional sistem terhadap kebutuhan pengguna tanpa mempertimbangkan struktur kode internal.

Sementara itu, User Acceptance Testing (UAT) diterapkan untuk memastikan bahwa sistem yang dikembangkan benar-benar dapat diterima dan digunakan secara efektif oleh pengguna akhir, khususnya mahasiswa dan staf administrasi. Pendekatan ini dinilai relevan untuk menilai aspek kegunaan (usability) dan pengalaman pengguna (user experience) dari sistem dashboard yang dikembangkan.


### 2.4.1 Pengujian Backend (API & Integration Testing)

Tahap ini berfokus untuk memvalidasi "otak" sistem, yaitu RESTful API (Node.js) dan konektivitasnya ke database PostgreSQL.

1. Metode: Pengujian Integrasi API (sering disebut sebagai Grey Box Testing atau pengujian endpoint).
2. Alat: Software seperti Postman atau framework pengujian backend (misal: Jest).
3. Skenario Pengujian:
4. Validasi Koneksi: Memastikan backend dapat terhubung dengan benar ke database PostgreSQL.
5. Pengujian Endpoint API: Mengirimkan berbagai request HTTP ke endpoint API yang telah dibuat (misal: GET /api/fakultas, POST /api/dosen) untuk memvalidasi:
6. Apakah request yang valid mengembalikan status 200 OK (untuk GET) atau 201 Created (untuk POST) beserta data JSON yang benar?
7. Apakah request yang tidak valid (misal: data tidak lengkap) mengembalikan status error yang sesuai (misal: 400 Bad Request)?
8. Apakah request ke endpoint yang diamankan (misal: CRUD Admin) gagal jika tidak menyertakan token autentikasi?
Pengujian backend difokuskan pada endpoint RESTful API yang melayani data akademik, spasial, dan analitik. Endpoint publik diuji untuk memastikan data dapat diakses tanpa autentikasi, sedangkan endpoint administratif diuji dengan validasi token autentikasi untuk memastikan kontrol akses berjalan dengan baik. Pendekatan ini bertujuan untuk menjamin keandalan layanan API dalam mendukung public dashboard maupun admin dashboard.


### 2.4.2 Pengujian Fungsional (Black Box Testing)

Black Box Testing, yang juga dikenal sebagai pengujian fungsional, merupakan metode evaluasi perangkat lunak yang menitikberatkan pada validasi fungsionalitas tanpa meninjau struktur kode internalnya. Dalam pendekatan ini, perangkat lunak diperlakukan layaknya 'kotak hitam', di mana pengujian dilakukan semata-mata berdasarkan kesesuaian antara input yang diberikan dan output yang dihasilkan(Maulida et al., 2025).

Implementasi Black Box Testing pada tahap ini berfokus untuk memvalidasi fungsionalitas antarmuka pengguna (frontend) dari perspektif pengguna, tanpa melihat kode internal. Pengujian ini memastikan bahwa semua alur kerja pada Admin Dashboard dan Public Dashboard berjalan sesuai mockup dan kebutuhan fungsional.

1. Metode: Black Box Testing.
2. Skenario Pengujian :
Tabel 2.2 Skenario Black Box Testing


[TABLE]
ID Test | Komponen | Skenario Pengujian | Langkah-Langkah | Hasil yang Diharapkan
BB-01 | Admin Dashboard | Fungsionalitas Login Admin | 1. Buka halaman Login Admin.2. Masukkan username dan password yang valid.3. Klik tombol "Masuk". | Sistem berhasil mengautentikasi dan mengarahkan admin ke halaman utama dashboard.
BB-02 | Admin Dashboard | Fungsionalitas CRUD (Create) | 1. Di halaman utama admin, klik tombol "Tambah Dosen".2. Isi form pada modal "Tambah Dosen".3. Klik "Simpan". | Modal tertutup, tabel data dosen di halaman utama otomatis diperbarui (refresh) dan menampilkan data dosen yang baru saja ditambahkan.
BB-03 | Admin Dashboard | Fungsionalitas CRUD (Update) | 1. Di tabel data dosen, klik ikon "Edit" pada salah satu baris.2. Modal "Edit Dosen" muncul dengan data yang sudah terisi.3. Ubah salah satu data (misal: email).4. Klik "Simpan". | Modal tertutup, data email pada tabel dosen tersebut berhasil diperbarui.
BB-04 | Admin Dashboard | Fungsionalitas CRUD (Delete) | 1. Di tabel data dosen, klik ikon "Hapus" pada salah satu baris.2. Modal "Konfirmasi Hapus" muncul.3. Klik "Hapus". | Modal tertutup, baris data dosen tersebut hilang dari tabel.
BB-05 | Public Dashboard | Interaksi Chart dan Panel Info | 1. Buka halaman public dashboard.2. Klik pada salah satu bar chart (misal: bar "Fakultas Teknik" di chart Dosen). | Panel informasi di sisi kanan atau area lain berubah (me-render ulang state) untuk menampilkan detail data "Fakultas Teknik".
BB-06 | Modul Analitik | Pelacakan Kunjungan | 1. Buka public dashboard  dari browser baru.2. Navigasi ke beberapa halaman.3. Cek Dashboard bagian "Analytics". | Widget 'Page Visitors' dan 'Page Views' di Admin Dashboard (Gambar 2.7) bertambah nilainya sesuai dengan aktivitas pengguna.
BB-07 | Dashboard Publik |  | Dashboard Publik | Interaksi Kartu Fasilitas | Klik salah satu card fasilitas (non-unggulan) | Modal daftar fasilitas tampil sesuai kategori

Dashboard Publik
BB-08 | Dashboard Publik |  | Dashboard Publik | Detail Fasilitas Unggulan | Klik fasilitas unggulan atau item pada list | Modal detail fasilitas tampil sesuai data

Dashboard Publik
BB-09 | Dashboard Publik | Interaksi Grafik Statistik | Klik salah satu bar grafik dosen | Detail data dosen fakultas tampil
BB-10 | Dashboard Publik | Interaksi Grafik Statistik | Klik salah satu bar grafik mahasiswa | Detail data mahasiswa fakultas tampil
BB-11 | Modul Analitik | Deteksi Perangkat | Akses website via perangkat berbeda | Device type tercatat pada admin traffic
[/TABLE]


### 2.4.3 User Acceptance Testing

User Acceptance Testing (UAT) berfungsi sebagai tahapan validasi krusial dalam siklus pengembangan sistem. Proses ini bertujuan untuk mengonfirmasi bahwa perangkat lunak yang dibangun telah selaras dengan ekspektasi serta kebutuhan operasional pengguna akhir sebelum dirilis secara resmi ke lingkungan produksi (Aliyah Aliyah et al., 2024). Tujuan utama UAT adalah untuk mendapatkan konfirmasi (penerimaan) dari pengguna bahwa sistem siap digunakan di lingkungan produksi sesungguhnya.

Pada proyek ini, tahap pengujian akhir ini akan melibatkan pengguna asli untuk memvalidasi kegunaan (usability) dan penerimaan sistem.

1. Metode: Metode yang digunakan dalam tahap UAT ini adalah Usability Testing (Pengujian Ketergunaan).
2. Target Responden:
3. Admin Dashboard: Perwakilan staf administrasi atau pengelola data kampus.
4. Public Dashboard: Perwakilan mahasiswa (terutama mahasiswa baru) dan pengunjung.
5. Prosedur: Responden akan diberikan serangkaian skenario tugas (misal: "Tolong tambahkan data dosen baru bernama X" atau "Coba temukan informasi akreditasi Fakultas Hukum").
6. Metrik Evaluasi: Keberhasilan penyelesaian tugas dan umpan balik kualitatif akan dikumpulkan. Untuk mengukur usability secara kuantitatif, kuesioner standar seperti SUS (System Usability Scale) akan digunakan untuk mendapatkan skor ketergunaan sistem.
Skenario tugas pada tahap User Acceptance Testing dirancang berdasarkan fitur utama sistem, seperti menemukan lokasi fasilitas tertentu melalui public dashboard, menampilkan detail dosen berdasarkan fakultas, serta mengelola data fasilitas melalui dashboard admin. Penyusunan skenario ini bertujuan untuk memastikan bahwa sistem dapat digunakan secara intuitif oleh pengguna dengan latar belakang teknis yang berbeda.


## 



# BAB 3 IMPLEMENTASI PROYEK


## 3.1 Profil Mitra


### 3.1.1 Nama Organisasi/Lembaga Mitra

Universitas Pembangunan Nasional Veteran Jakarta Kampus Pondok Labu


### 3.1.2 Deskripsi Mitra

Universitas Pembangunan Nasional “Veteran” Jakarta (UPNVJ) Kampus Pondok Labu merupakan salah satu institusi pendidikan tinggi negeri yang memiliki peran strategis dalam pengembangan sumber daya manusia di bidang akademik dan profesional. Sejak memperoleh status sebagai Perguruan Tinggi Negeri pada tahun 2014, UPNVJ terus berkomitmen dalam meningkatkan kualitas pendidikan, penelitian, dan pengabdian kepada masyarakat dengan mengedepankan nilai-nilai bela negara.

Kampus Pondok Labu sebagai salah satu pusat kegiatan akademik UPNVJ memiliki lingkungan yang luas dengan berbagai fasilitas pendukung, seperti gedung fakultas, ruang perkuliahan, laboratorium, serta sarana umum lainnya. Seiring dengan perkembangan jumlah mahasiswa dan kompleksitas infrastruktur kampus, kebutuhan akan sistem informasi yang terintegrasi dan mudah diakses menjadi semakin penting.

Dalam konteks transformasi digital menuju konsep Smart Campus, UPNVJ telah mulai mengembangkan berbagai sistem informasi untuk mendukung pengelolaan data akademik dan layanan kampus. Namun, berdasarkan kondisi eksisting, penyajian informasi kampus masih bersifat terfragmentasi dan sistem navigasi yang tersedia masih mengandalkan media konvensional seperti papan petunjuk dan denah statis.

Oleh karena itu, UPNVJ Kampus Pondok Labu menjadi lingkungan yang relevan sebagai mitra dalam pengembangan sistem integrasi denah virtual dan dashboard profil kampus. Proyek ini diharapkan dapat mendukung upaya digitalisasi layanan informasi serta meningkatkan pengalaman pengguna dalam mengakses informasi dan melakukan navigasi di lingkungan kampus.



### 3.1.3 Hubungan Mitra dengan Proyek

Pengembangan sistem integrasi denah virtual kampus dan dashboard profil UPNVJ melibatkan keterkaitan langsung dengan mitra, yaitu Universitas Pembangunan Nasional “Veteran” Jakarta Kampus Pondok Labu, sebagai lingkungan implementasi dan sumber data utama. Hubungan antara mitra dan proyek dapat dijelaskan sebagai berikut:

1. Universitas Pembangunan Nasional “Veteran” Jakarta Kampus Pondok Labu
  a. Peran:
    1) Menjadi objek utama dalam pengembangan dan implementasi sistem, khususnya dalam penyediaan data spasial (gedung dan fasilitas) serta data profil kampus.
    2) Menyediakan lingkungan nyata (real-world environment) sebagai dasar observasi, analisis kebutuhan, serta validasi sistem yang dikembangkan.
    3) Mendukung proses pengembangan melalui koordinasi dengan stakeholder terkait, seperti pihak pengelola teknologi informasi (UPA TIK).


  b. Manfaat:
    1) Mendapatkan solusi sistem navigasi kampus berbasis visualisasi 3D yang lebih interaktif dibandingkan metode konvensional.
    2) Memperoleh platform dashboard profil kampus yang terintegrasi, sehingga penyajian informasi menjadi lebih terpusat dan mudah diakses.
    3) Mendukung implementasi konsep Smart Campus melalui integrasi teknologi backend, dashboard web, dan visualisasi 3D.


2. Sivitas Akademika dan Pengguna (Mahasiswa dan Pengunjung)
  a. Peran:
    1) Bertindak sebagai pengguna utama sistem (end-user) yang berinteraksi langsung dengan public dashboard dan denah virtual.
    2) Menjadi sumber data kebutuhan sistem melalui kuesioner dan observasi pengalaman navigasi kampus.


  b. Manfaat:
    1) Mempermudah proses pencarian lokasi di lingkungan kampus melalui sistem navigasi berbasis visualisasi 3D.
    2) Meningkatkan kemudahan akses terhadap informasi kampus yang sebelumnya tersebar di berbagai platform.


3. Administrator Sistem (Pengelola Data Kampus)
  a. Peran:
    1) Mengelola data konten kampus melalui admin dashboard, termasuk data fasilitas, gedung, dan profil.
    2) Menjaga konsistensi dan keakuratan data yang digunakan oleh sistem.

  b. Manfaat:
    1) Memperoleh sistem manajemen konten terpusat yang mempermudah pengelolaan data secara efisien.
    2) Mendukung proses pembaruan informasi secara real-time tanpa perlu mengubah sistem secara keseluruhan.


## Metode Implementasi

Bagian ini menguraikan tahapan pengembangan dan implementasi proyek integrasi denah virtual yang dilakukan dengan menggunakan metode prototyping. Metode ini dipilih untuk memungkinkan proses pengembangan sistem yang iteratif dan adaptif terhadap kebutuhan pengguna.

Implementasi sistem dalam proyek ini dibagi menjadi tiga bagian utama, yaitu asset designing, engine development, dan full stack development. Adapun laporan ini berfokus pada aspek full stack development, yang menjadi tanggung jawab penulis dalam tim pengembang.

Pada sisi front-end, proses pengembangan mencakup perancangan serta implementasi antarmuka pengguna yang interaktif dan responsif. Sementara itu, pada sisi back-end, pengembangan difokuskan pada perancangan dan pengelolaan basis data, implementasi logika sistem, serta pengembangan Application Programming Interface (API) yang berfungsi sebagai


### Metode Pengembangan Sistem

  Penjelasan kenapa pakai prototyping

  Tahapan:

1. Requirement gathering
2. Prototype awal
3. Evaluasi
4. Iterasi


### Arsitektur Implementasi Sistem

  Jelaskan:

1. Backend sebagai data hub
2. Frontend sebagai interface
3. Unity sebagai visual layer
  Bisa tambahkan diagram (kalau ada)


### Implementasi Back-end

Isi:

1. Struktur backend (MVC / modular)
2. Teknologi (Express, MySQL/PostgreSQL, dll)
3. Endpoint utama
4. Autentikasi (kalau ada)
5. Flow request-response



### Implementasi Front-end


  Framework (React / HTML JS native)

  Struktur komponen

  Integrasi API

  State management (kalau ada)



### Implementasi Integrasi Back-end dengan Unity



  Cara Unity consume API

  Format data (JSON)

  Event interaksi (klik gedung → fetch API)

  Flow data end-to-end


### Implementasi Admin Dashboard


  Fitur CRUD

  Proteksi akses

  Alur pengelolaan data


### Alur Implementasi Modul Pendukung


  Analytics tracking

  Search feature

  Logging


### Alur Implementasi Sistem



  Flow lengkap:

1. Admin input data
2. Data masuk DB
3. API expose data
4. Frontend & Unity consume
  Bisa dalam bentuk narasi atau diagram







# DAFTAR PUSTAKA





