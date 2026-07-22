Instrumen UAT tertutup menggunakan skala Likert 1 sampai 5. UAT hanya melibatkan dua dosen penguji, dua dosen pembimbing, dan satu perwakilan Humas UPNVJ; tidak terdapat sampel mahasiswa baru, orang tua atau wali, maupun pengunjung eksternal. Kode peserta pada lampiran ini dianonimkan dan tidak dipetakan kepada nama. Redaksi pernyataan disalin dari instrumen kerja dengan normalisasi ejaan tanpa mengubah makna pertanyaan. Hasil agregat dan batas interpretasinya tetap dibahas pada Subbab 3.5 agar lampiran ini berfungsi sebagai bukti instrumen, bukan analisis kedua.

Instrumen evaluasi Dashboard Publik yang diperlihatkan pada [TABREF:lampiran_instrumen_uat_dashboard_publik] terdiri atas sembilan pernyataan mengenai kegunaan, kemudahan, desain, dan kinerja sistem. Nama instrumen merujuk pada antarmuka yang dinilai, bukan pada asal peserta pengujian.

[TABLE-ID:lampiran_instrumen_uat_dashboard_publik]
[TABLECAPTION:Instrumen Evaluasi UAT Dashboard Publik]

[TABLE]
Kode | Dimensi | Pernyataan
PUB-01 | Fungsionalitas dan Kegunaan | Aplikasi Denah Virtual UPNVJ membantu saya menemukan lokasi gedung atau ruangan dengan lebih mudah.
PUB-02 | Fungsionalitas dan Kegunaan | Informasi gedung dan fasilitas yang ditampilkan pada denah sudah akurat dan informatif.
PUB-03 | Kemudahan Penggunaan | Navigasi untuk menjelajahi denah virtual WebGL sangat mudah dikendalikan.
PUB-04 | Kemudahan Penggunaan | Saya tidak memerlukan panduan khusus atau waktu lama untuk memahami cara kerja aplikasi ini.
PUB-05 | Desain dan Interaksi | Tampilan visual 3D atau denah terlihat menarik dan merepresentasikan kondisi kampus dengan baik.
PUB-06 | Desain dan Interaksi | Tata letak tombol, menu, pencarian, dan filter pada layar mudah ditemukan dan enak dilihat.
PUB-07 | Desain dan Interaksi | Warna dan teks yang digunakan pada dashboard publik mudah dibaca.
PUB-08 | Kinerja Sistem | Aplikasi berjalan dengan lancar saat memuat denah virtual.
PUB-09 | Kinerja Sistem | Interaksi pada denah terasa responsif dan tidak mengalami keterlambatan yang mengganggu.
[/TABLE]

Instrumen administrator pada [TABREF:lampiran_instrumen_uat_admin] memuat sebelas pernyataan yang menilai pengelolaan data, autentikasi, kemudahan penggunaan, desain, dan kinerja Admin Panel.

[TABLE-ID:lampiran_instrumen_uat_admin]
[TABLECAPTION:Instrumen UAT Dashboard Admin]

[TABLE]
Kode | Dimensi | Pernyataan
ADM-01 | Manajemen dan Fungsionalitas Data | Fitur untuk menambah, membaca, mengubah, dan menghapus data gedung berfungsi dengan sangat baik.
ADM-02 | Manajemen dan Fungsionalitas Data | Formulir pengisian data, seperti nama gedung, deskripsi, atau foto, mudah diisi dan dipahami.
ADM-03 | Manajemen dan Fungsionalitas Data | Sistem memberikan notifikasi atau pesan yang jelas ketika data berhasil disimpan, diubah, atau gagal diproses.
ADM-04 | Manajemen dan Fungsionalitas Data | Perubahan data pada Dashboard Admin tersinkronisasi dan tampil dengan benar pada sisi pengguna akhir.
ADM-05 | Keamanan dan Autentikasi | Proses login dan logout berjalan lancar dan aman.
ADM-06 | Keamanan dan Autentikasi | Pengguna yang tidak memiliki hak akses tidak dapat masuk ke Admin Panel.
ADM-07 | Kemudahan Penggunaan | Susunan menu pada sidebar atau navigasi dashboard terstruktur dan memudahkan pencarian halaman yang dibutuhkan.
ADM-08 | Kemudahan Penggunaan | Saya dapat mengelola data tanpa memerlukan waktu lama untuk mempelajari cara kerja sistem.
ADM-09 | Kemudahan Penggunaan | Tabel atau daftar data mudah dibaca, diurutkan, atau dicari menggunakan fitur pencarian.
ADM-10 | Desain dan Kinerja | Tampilan visual Dashboard Admin terlihat profesional, bersih, dan tidak membingungkan.
ADM-11 | Desain dan Kinerja | Transisi antarhalaman dan pemrosesan data ke database terasa cepat dan responsif.
[/TABLE]

Rekap anonim pada [TABREF:lampiran_rekap_responden_uat] menunjukkan kelengkapan instrumen dan jumlah skor setiap peserta. Tanda em dash berarti peserta tidak mengisi instrumen tersebut; kondisi ini menjelaskan mengapa terdapat lima peserta unik, tetapi masing-masing instrumen memperoleh empat respons.

[TABLE-ID:lampiran_rekap_responden_uat]
[TABLECAPTION:Rekap Anonim Respons UAT]

[TABLE]
Kode | Skor Publik | Skor Admin | Kelengkapan
R-01 | 39 dari 45 | 52 dari 55 | Mengisi kedua instrumen
R-02 | 39 dari 45 | 48 dari 55 | Mengisi kedua instrumen
R-03 | 31 dari 45 | 37 dari 55 | Mengisi kedua instrumen
R-04 | 31 dari 45 | — | Mengisi instrumen Dashboard Publik
R-05 | — | 49 dari 55 | Mengisi instrumen Dashboard Admin
[/TABLE]

Sumber bukti pengujian dipertahankan terpisah dari narasi laporan. Rekap respons UAT berada pada `Hasil UAT/Hasil_UAT.xlsx`, sedangkan formulir individual tersimpan sebagai arsip PDF dan tidak direproduksi bersama identitas peserta pada tabel lampiran.

Hasil awal 24 skenario Black Box berada pada `Hasil UAT/Hasil_BlackBox.docx`. Pengujian ulang BB-20 didukung oleh dua tangkapan layar berurutan, yaitu `BB20_1.png` dan `BB20_2.png`, yang menunjukkan kondisi sebelum dan sesudah navigasi selesai.

Bukti visual tindak lanjut UAT disimpan pada `Hasil UAT/dokumentasi revisi/` dan digunakan secara selektif pada BAB III. Seluruh tangkapan layar aplikasi tidak dimasukkan kembali ke lampiran.

Dokumen mentah tetap diperlakukan sebagai arsip bukti. Status lulus, persentase, dan batas klaim yang digunakan laporan mengikuti sumber kanonik pada Subbab 3.5 serta `content/shared/testing/results.json`.
