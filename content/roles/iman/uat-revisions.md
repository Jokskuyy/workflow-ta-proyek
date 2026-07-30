Hasil UAT pada Subbab 3.5.4 merupakan hasil evaluasi produk bersama. Pembahasan tindak lanjut pada laporan ini dibatasi pada kontribusi penulis sebagai Full Stack Web Developer, System Integrator, dan DevOps Engineer. Kontribusi tersebut berfokus pada Denah 2D berbasis React, Tutorial dan FAQ, pemilih mode, pencarian dan bantuan pada antarmuka web, serta penghubung notifikasi kedatangan dari Unity ke React. Perubahan data dan aset 3D, minimap, titik awal di dalam Unity, label lingkungan 3D, dan proses build Unity dibahas pada laporan anggota sesuai kepemilikannya.

Pemetaan tindak lanjut UAT dalam lingkup penulis dirangkum pada [TABREF:uat_revisi_peran_iman].

[TABLE-ID:uat_revisi_peran_iman]
[TABLECAPTION:Tindak Lanjut UAT dalam Lingkup Kontribusi Penulis]

[TABLE]
ID Temuan | Kontribusi Penulis | Keterhubungan Antarperan | Bukti dan Batas Pemeriksaan
UAT-R01 | Memperluas pencarian React agar membaca nama, deskripsi, lokasi, istilah alternatif, dan nama gedung induk. | Antarmuka menggunakan data yang disiapkan dan dibersihkan oleh Database Schema Designer. | Pemeriksaan kode sumber pencarian; penerapan ulang data hasil pembersihan pada database aktif belum diverifikasi.
UAT-R02 | Menyediakan Tutorial dan FAQ Denah 2D serta Denah 3D sebelum pengguna membuka denah. | Isi panduan 3D mengikuti kontrol dan alur yang disediakan Engine Developer. | Pemeriksaan kode sumber dan tampilan Tutorial/FAQ pada aplikasi.
UAT-R03, UAT-R05, dan UAT-R07 | Menyediakan pemilih mode serta Denah 2D berbasis A\* dengan pilihan gedung awal, pencarian tujuan, dan garis rute. | Denah 2D menjadi alternatif terhadap mode 3D; pemilihan titik awal dan navigasi di dalam Unity tetap menjadi kontribusi Engine Developer. | Pemeriksaan kode sumber serta tampilan pemilih mode dan Denah 2D.
UAT-R08 | Menyediakan tombol bantuan pada lapisan web, petunjuk pemulihan, pergantian mode, dan kontak resmi kampus. | Petunjuk yang berkaitan dengan kontrol Unity diselaraskan dengan perilaku aplikasi 3D. | Pemeriksaan kode sumber dan sumber resmi nomor layanan kampus.
UAT-R10 | Memvalidasi pesan `OnNavigationCompleted` terhadap tujuan aktif sebelum React menampilkan notifikasi kedatangan. | Unity mengirim pesan setelah navigasi selesai; React memeriksa muatan dan mengendalikan notifikasi pada antarmuka web. | Sebelas pengujian otomatis React dan tangkapan layar notifikasi kedatangan.
[/TABLE]

Pemetaan tersebut tidak mengubah nilai UAT awal dan bukan pengujian ulang kepada peserta. Status produk secara keseluruhan tetap bersumber dari data pengujian bersama, sedangkan subbab berikutnya hanya menampilkan bukti yang relevan dengan kontribusi penulis.
