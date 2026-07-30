Sebanyak 20 dari 21 responden atau 95,2 persen merupakan sivitas akademika UPNVJ, sedangkan satu responden merupakan pengunjung eksternal. Komposisi pada [FIGREF:survey_01_profil] menunjukkan bahwa temuan terutama menggambarkan pengalaman pengguna internal dalam sampel yang diteliti.

[FIGURE:survey_01_profil]
[FIGCAPTION:Distribusi Status Akademik Responden]

Penilaian terhadap papan penunjuk arah dan peta statis tidak menunjukkan penolakan yang dominan. Sebanyak 33,3 persen responden memberi nilai 1 atau 2, 23,8 persen memberi nilai 3, dan 42,9 persen memberi nilai 4 atau 5. Distribusi pada [FIGREF:survey_02_efektivitas] menunjukkan persepsi yang terbagi dengan nilai rata-rata sekitar 3,05 dari 5, sehingga kebutuhan sistem baru tidak dapat didasarkan pada klaim bahwa seluruh media yang tersedia tidak informatif.

[FIGURE:survey_02_efektivitas]
[FIGCAPTION:Penilaian Responden terhadap Efektivitas Media Navigasi Kampus]

Dalam satu semester terakhir, sebanyak 57,1 persen responden mengalami kesulitan mencari lokasi sebanyak 1–3 kali, 9,5 persen mengalaminya lebih dari tiga kali, dan 33,3 persen tidak pernah mengalaminya. Dengan demikian, 14 dari 21 responden atau 66,7 persen pernah mengalami kesulitan setidaknya satu kali, sebagaimana disajikan pada [FIGREF:survey_03_frekuensi].

[FIGURE:survey_03_frekuensi]
[FIGCAPTION:Frekuensi Kesulitan Responden dalam Menemukan Lokasi]

Ketika mencari lokasi, sebanyak 90,5 persen responden paling sering bertanya kepada orang di sekitar, petugas keamanan, atau layanan mahasiswa. Pola pada [FIGREF:survey_04_perilaku] menunjukkan bahwa bantuan interpersonal masih menjadi jalur utama dalam sampel, sedangkan papan penunjuk dan situs kampus digunakan oleh sebagian kecil responden.

[FIGURE:survey_04_perilaku]
[FIGCAPTION:Sumber Informasi yang Digunakan Responden Saat Mencari Lokasi]

Sebanyak 76,2 persen responden memberi nilai 4 atau 5 terhadap pentingnya peta virtual 3D yang terintegrasi dengan informasi fasilitas. Penilaian pada [FIGREF:survey_05_urgensi] mendukung kebutuhan akan alternatif digital, tetapi tetap diperlakukan sebagai kebutuhan pengguna pada sampel, bukan bukti keberhasilan solusi yang belum diuji pada tahap observasi.

[FIGURE:survey_05_urgensi]
[FIGCAPTION:Penilaian Responden terhadap Kebutuhan Denah Virtual 3D]

Dalam rencana penggunaan, 9,5 persen responden menyatakan akan menggunakan denah setiap kali berada di kampus, 61,9 persen ketika mencari lokasi tertentu, 23,8 persen hanya sesekali, dan 4,8 persen tidak akan menggunakannya. Distribusi pada [FIGREF:survey_06_adopsi] menunjukkan bahwa fungsi pencarian lokasi merupakan konteks penggunaan yang paling relevan.

[FIGURE:survey_06_adopsi]
[FIGCAPTION:Minat Responden Menggunakan Denah Virtual 3D]

Informasi yang paling banyak dipilih untuk ditampilkan adalah nama gedung sebesar 95,2 persen, fasilitas dalam ruangan sebesar 52,4 persen, dan kapasitas ruangan sebesar 38,1 persen. Prioritas pada [FIGREF:survey_07_prioritas] menjadi dasar pemilihan informasi yang disajikan melalui dashboard dan lingkungan denah virtual.

[FIGURE:survey_07_prioritas]
[FIGCAPTION:Prioritas Informasi Fasilitas Menurut Responden]

Hasil kuesioner dan tinjauan sistem berjalan diringkas pada [TABREF:analisis_sistem_berjalan]. Matriks ini memisahkan kondisi yang teramati, kesenjangan dalam ruang lingkup proyek, dan implikasinya terhadap kebutuhan sistem.

[TABLE-ID:analisis_sistem_berjalan]
[TABLECAPTION:Analisis Sistem yang Berjalan dan Implikasi Kebutuhan]

[TABLE]
Aspek | Kondisi yang Diamati atau Telah Diperiksa | Kesenjangan dalam Ruang Lingkup Proyek | Implikasi terhadap Kebutuhan Sistem
Pencarian lokasi | Responden masih dominan meminta bantuan orang lain dan 66,7 persen pernah mengalami kesulitan setidaknya satu kali dalam satu semester | Produk memerlukan hubungan antara pencarian tujuan dan panduan spasial | Menyediakan pencarian lokasi serta panduan melalui Denah 2D dan Denah 3D
Informasi tujuan | Nama gedung dan fasilitas menjadi prioritas informasi responden | Informasi lokasi dan fasilitas perlu disajikan secara terhubung dengan tujuan navigasi | Menampilkan nama tujuan, informasi fasilitas, jarak, rute, dan petunjuk orientasi yang relevan
Konsistensi identitas | Data fasilitas dan objek Unity digunakan oleh beberapa komponen dengan kebutuhan yang berbeda | Setiap tujuan memerlukan kode yang konsisten pada database, API, Dashboard Publik, dan Unity | Menggunakan kode lokasi Unity sebagai acuan identitas lintas komponen
Distribusi data | Dashboard Publik, aplikasi Unity, dan alat bantu Unity Editor memiliki kebutuhan data yang berbeda | Proses autentikasi, pengelolaan konten, pengambilan data Unity, dan pemeriksaan melalui editor perlu dibedakan | Memisahkan autentikasi dan pengelolaan data melalui Supabase, `/api/unity/data`, serta `/api/unity/names` berdasarkan komponen yang menggunakannya
Distribusi aplikasi | Denah virtual dijalankan melalui dashboard web pada perangkat dan kondisi jaringan yang beragam | Proses pemuatan, pilihan mode denah, serta pengoperasian layanan perlu memberikan informasi yang jelas kepada pengguna | Menyesuaikan pemuatan dengan perangkat dan koneksi, menggunakan cache aset, menyediakan pilihan 2D/3D, serta memeriksa status layanan
[/TABLE]

Analisis tersebut tidak menyimpulkan bahwa UPNVJ secara institusional tidak memiliki sistem terpusat. Kesenjangan yang dimaksud adalah kebutuhan integrasi pada produk yang dikembangkan dalam proyek ini.
