# Requirements Document

## Introduction

Tahap GENERASI pada pipeline penyusunan dokumen Tugas Akhir (`skills/scripts/build_pipeline.py`)
saat ini masih memuat sejumlah pengkodean nilai tetap (hardcoding) yang terikat pada isi spesifik
draf sumber saat ini (`Tugas_Akhir_Draft.md`). Akibatnya, setiap kali draf diubah (penambahan,
penghapusan, atau pengurutan ulang gambar/tabel/subbab), skrip generasi berpotensi menghasilkan
penomoran kapsi, deskripsi, atau referensi silang yang salah tanpa adanya perubahan kode manual.

Fitur ini menjadikan tahap generasi sepenuhnya dinamis sehingga tangguh terhadap versi baru atau
versi yang disunting dari draf, tanpa memerlukan perubahan kode per-dokumen. Lingkup pekerjaan
difokuskan pada dua skrip generasi yang masih memuat hardcoding, yaitu
`skills/scripts/format_ta_proyek.py` dan `scratch/merge_draft_to_docx.py`. Guard validasi
(`scratch/validate_docx_structure.py`) sudah dinamis dan tidak diubah semantiknya.

Hardcoding yang harus dihilangkan (terverifikasi pada kode saat ini):

1. `format_ta_proyek.py` `ref_repl()` — tabel pemetaan tetap untuk renumbering referensi
   "Gambar 2.x" yang terikat pada urutan gambar BAB II saat ini.
2. `format_ta_proyek.py` — daftar literal `survey_captions` (7 teks kapsi "Hasil Kuesioner ...")
   serta pemicu judul-seksi literal seperti "Analisis Sistem yang Sedang Berjalan" dan
   "Integrasi Backend dengan Unity" untuk menyuntikkan kapsi tertentu (mis. "Gambar 2.15" yang
   dipaksakan).
3. `format_ta_proyek.py` — penomoran gambar BAB II memakai satu penghitung sekuensial yang
   memaksa bab "2."; kasus bab III sudah dibuat sadar-bab dan perlu digeneralisasi untuk SEMUA bab.
4. `format_ta_proyek.py` — indeks fallback tetap seperti `bab1_idx_orig = 60` dan
   `section1_last_p_idx = 60`.
5. `merge_draft_to_docx.py` `is_match()` — fallback kasus khusus manual (mis. image20 →
   "modaltambahdatagedung", trik "Dosen" → "Gedung") dan path absolut dalam `main()`.
6. Setiap kopling literal lain terhadap gambar, tabel, nama seksi, atau jumlah spesifik draf saat ini.

## Glossary

- **Pipeline_Generasi**: Tahap generasi dokumen pada `build_pipeline.py` yang mencakup
  `merge_draft_to_docx.py`, `patch_template.py`, `add_numbering_preset.py`, dan
  `format_ta_proyek.py`, sampai sebelum tahap validasi.
- **Mesin_Format**: Skrip `skills/scripts/format_ta_proyek.py`.
- **Mesin_Merge**: Skrip `scratch/merge_draft_to_docx.py`.
- **Validator_Struktur**: Skrip `scratch/validate_docx_structure.py`.
- **Draf**: Berkas markdown sumber `Tugas_Akhir_Draft.md`.
- **BAB**: Heading tingkat 1 (paragraf bergaya `Heading1`) yang menandai awal sebuah bab,
  mis. "BAB II RANCANGAN PROYEK".
- **Nomor_Bab**: Bilangan bulat bab (1, 2, 3, ...) yang diturunkan dari teks BAB pembungkus.
- **Kapsi**: Paragraf bergaya `Caption` yang memuat label "Gambar" atau "Tabel" beserta nomor
  dan deskripsi, mis. "Gambar 2.5 Use Case Diagram".
- **Deskripsi_Kapsi**: Bagian teks kapsi setelah label dan nomor, mis. "Use Case Diagram".
- **Field_SEQ**: Field Word `SEQ` yang menghitung nomor gambar/tabel secara otomatis; opsi
  `\r 1` me-restart hitungan.
- **Referensi_Silang**: Penyebutan "Gambar X.Y" atau "Tabel X.Y" dalam paragraf narasi yang
  merujuk ke sebuah kapsi.
- **Gambar_Template**: Elemen drawing yang sudah tertanam pada template `.docx` dan
  dipasang-ulang oleh Mesin_Merge melalui asosiasi teks.
- **Manifest_Gambar**: Berkas `images/manifest.json` yang menggerakkan injeksi gambar pasca-COM.
- **Aturan_Umum**: Aturan berbasis pola/struktur dokumen yang berlaku untuk seluruh masukan,
  bukan kasus khusus bernama (named special-case).
- **Dokumen_Referensi**: Dokumen keluaran dari Draf saat ini yang dihasilkan sebelum perubahan
  dinamis diterapkan, dipakai sebagai pembanding kompatibilitas mundur.

## Requirements

### Requirement 1: Penomoran Kapsi Gambar Dinamis per Bab

**User Story:** Sebagai pengguna pipeline, saya ingin nomor kapsi gambar diturunkan secara dinamis
per bab dari struktur dokumen, sehingga draf dengan jumlah bab atau gambar berapa pun dinomori
dengan benar tanpa perubahan kode.

#### Acceptance Criteria

1. WHEN Mesin_Format memproses sebuah Kapsi gambar, THE Mesin_Format SHALL menentukan Nomor_Bab
   dari BAB yang posisinya terakhir muncul sebelum Kapsi tersebut dalam urutan baca dokumen.
2. WHEN Mesin_Format menomori gambar dalam sebuah bab, THE Mesin_Format SHALL memberi nomor urut
   per-bab berbentuk "Gambar {Nomor_Bab}.{urutan}", dengan urutan berupa bilangan bulat yang
   dimulai dari 1 pada gambar pertama bab tersebut dan bertambah tepat 1 untuk setiap gambar
   berikutnya dalam bab yang sama.
3. WHEN Mesin_Format berpindah ke bab baru, THE Mesin_Format SHALL me-reset urutan gambar kembali
   ke 1 untuk gambar pertama bab baru tersebut.
4. WHEN Mesin_Format membuat Kapsi gambar pertama dalam sebuah bab, THE Mesin_Format SHALL
   menyisipkan Field_SEQ dengan opsi restart `\r 1`.
5. WHEN Mesin_Format membuat Kapsi gambar selain yang pertama dalam sebuah bab, THE Mesin_Format
   SHALL menyisipkan Field_SEQ tanpa opsi restart.
6. THE Mesin_Format SHALL menerapkan aturan penomoran per-bab yang sama untuk SEMUA bab (1..N) yang
   ada pada dokumen tanpa mengasumsikan nomor bab tertentu.
7. IF BAB pembungkus tidak dapat ditentukan untuk sebuah Kapsi gambar, THEN THE Mesin_Format SHALL
   memakai Nomor_Bab terakhir yang berhasil ditentukan (atau 1 bila belum ada), melanjutkan proses
   tanpa berhenti, dan mencatat peringatan yang menyebutkan Kapsi terkait.

### Requirement 2: Penomoran Kapsi Tabel Dinamis per Bab

**User Story:** Sebagai pengguna pipeline, saya ingin nomor kapsi tabel diturunkan secara dinamis
per bab, sehingga penambahan atau pengurutan ulang tabel tidak memerlukan perubahan kode.

#### Acceptance Criteria

1. WHEN Mesin_Format memproses sebuah Kapsi tabel, THE Mesin_Format SHALL menentukan Nomor_Bab
   dari BAB yang posisinya terakhir muncul sebelum Kapsi tersebut dalam urutan baca dokumen.
2. WHEN Mesin_Format menomori tabel dalam sebuah bab, THE Mesin_Format SHALL memberi nomor urut
   per-bab berbentuk "Tabel {Nomor_Bab}.{urutan}", dengan urutan berupa bilangan bulat yang
   dimulai dari 1 pada tabel pertama bab tersebut dan bertambah tepat 1 untuk setiap tabel
   berikutnya dalam bab yang sama.
3. WHEN Mesin_Format membuat Kapsi tabel pertama dalam sebuah bab, THE Mesin_Format SHALL
   menyisipkan Field_SEQ dengan opsi restart `\r 1`.
4. WHEN Mesin_Format membuat Kapsi tabel selain yang pertama dalam sebuah bab, THE Mesin_Format
   SHALL menyisipkan Field_SEQ tanpa opsi restart sehingga penomoran berlanjut dalam bab yang sama.
5. THE Mesin_Format SHALL menerapkan aturan penomoran tabel per-bab yang sama untuk SEMUA bab tanpa
   mengasumsikan nomor bab tertentu.
6. IF BAB pembungkus tidak dapat ditentukan untuk sebuah Kapsi tabel, THEN THE Mesin_Format SHALL
   memakai Nomor_Bab terakhir yang berhasil ditentukan (atau 1 bila belum ada), melanjutkan proses
   tanpa berhenti, dan mencatat peringatan yang menyebutkan Kapsi terkait.

### Requirement 3: Deskripsi Kapsi Bersumber dari Draf

**User Story:** Sebagai pengguna pipeline, saya ingin teks deskripsi kapsi diambil dari draf,
sehingga tidak ada daftar kapsi literal yang tertanam dalam kode.

#### Acceptance Criteria

1. WHEN Mesin_Format menyusun teks sebuah Kapsi, THE Mesin_Format SHALL menggunakan Deskripsi_Kapsi
   yang diturunkan dari teks kapsi gambar atau tabel terkait pada Draf dan menyalin isi
   Deskripsi_Kapsi tersebut secara verbatim ke dalam teks Kapsi tanpa mengubah karakternya selain
   penambahan label dan nomor.
2. THE Mesin_Format SHALL menyusun teks setiap Kapsi tanpa membaca atau merujuk daftar deskripsi
   kapsi literal apa pun yang ditulis di dalam kode, sehingga tidak ada teks Deskripsi_Kapsi yang
   muncul pada keluaran kecuali teks tersebut terdapat pada Draf.
3. IF sebuah gambar pada Draf tidak memiliki Kapsi, THEN THE Mesin_Format SHALL menangani gambar
   tersebut hanya melalui Aturan_Umum yang sama untuk seluruh gambar tanpa kapsi dan SHALL tidak
   membuat Kapsi maupun menetapkan nomor Kapsi untuk gambar tersebut.
4. THE Mesin_Format SHALL menyusun teks Kapsi tanpa memicu penyisipan atau penggantian
   Deskripsi_Kapsi berdasarkan kecocokan terhadap judul-seksi literal bernama tertentu yang
   ditulis di dalam kode.
5. WHEN Deskripsi_Kapsi sebuah gambar atau tabel pada Draf berubah, THE Mesin_Format SHALL
   menghasilkan teks Kapsi yang sesuai dengan Deskripsi_Kapsi terbaru pada Draf tanpa memerlukan
   perubahan kode.

### Requirement 4: Asosiasi Gambar Template ke Narasi Berbasis Aturan Umum

**User Story:** Sebagai pengguna pipeline, saya ingin Mesin_Merge memasang-ulang Gambar_Template ke
paragraf yang tepat menggunakan aturan pencocokan umum, sehingga tidak ada trik per-gambar.

#### Acceptance Criteria

1. WHEN Mesin_Merge mencocokkan sebuah Gambar_Template dengan paragraf pada hasil merge,
   THE Mesin_Merge SHALL menggunakan Aturan_Umum berbasis teks asosiasi, yaitu kecocokan ketika
   teks paragraf memuat teks asosiasi setelah normalisasi spasi dan huruf besar/kecil.
2. THE Mesin_Merge SHALL melakukan pencocokan Gambar_Template tanpa kasus khusus yang menyebut nama
   berkas gambar tertentu atau pemetaan istilah tertentu yang ditulis dalam kode.
3. IF sebuah Gambar_Template tidak menemukan paragraf yang cocok, THEN THE Mesin_Merge SHALL
   melanjutkan proses tanpa berhenti dan mencatat Gambar_Template yang tidak terpasang beserta
   teks asosiasinya.
4. IF lebih dari satu paragraf cocok untuk sebuah Gambar_Template, THEN THE Mesin_Merge SHALL
   memilih paragraf pertama menurut urutan dokumen dan mencatat peringatan adanya kecocokan ganda.
5. THE Mesin_Merge SHALL mencocokkan Gambar_Template hanya ke paragraf yang sejenis (kapsi ke
   kapsi, narasi ke narasi) dan SHALL tidak mencocokkan lintas-jenis.

### Requirement 5: Deteksi Seksi dan Heading Secara Dinamis

**User Story:** Sebagai pengguna pipeline, saya ingin semua deteksi seksi dan heading dilakukan
dengan memindai gaya dan teks dokumen, sehingga tidak ada indeks paragraf tetap.

#### Acceptance Criteria

1. WHEN Pipeline_Generasi perlu menemukan sebuah seksi atau heading, THE Pipeline_Generasi SHALL
   memindai seluruh paragraf dari awal ke akhir dan mencocokkan gaya paragraf serta teks secara
   case-insensitive dengan pemangkasan spasi.
2. THE Pipeline_Generasi SHALL menentukan batas antara halaman depan (front matter) dan isi
   menggunakan paragraf heading BAB I pertama yang ditemukan (bergaya `Heading1` dengan teks memuat
   "PENDAHULUAN"/"BAB I"), bukan indeks paragraf tetap.
3. IF sebuah seksi atau heading yang dicari tidak ditemukan, THEN THE Pipeline_Generasi SHALL
   menggunakan fallback yang diturunkan dari struktur dokumen (heading terdeteksi terdekat
   sebelumnya, atau akhir front matter), melanjutkan proses tanpa berhenti, dan mencatat satu
   peringatan yang menyebutkan target pencarian.
4. THE Pipeline_Generasi SHALL menentukan posisi seksi dan heading tanpa menggunakan nilai indeks
   paragraf numerik tetap yang ditulis dalam kode.
5. IF tidak ada heading BAB I di seluruh dokumen, THEN THE Pipeline_Generasi SHALL memakai fallback
   batas front matter yang diturunkan dari struktur dokumen dan mencatat peringatan.

### Requirement 6: Konsistensi Renumbering Referensi Silang

**User Story:** Sebagai pengguna pipeline, saya ingin penyebutan "Gambar X.Y" dan "Tabel X.Y" pada
narasi tetap konsisten dengan nomor kapsi yang ditetapkan secara dinamis, sehingga referensi tidak
salah arah.

#### Acceptance Criteria

1. WHEN Mesin_Format menetapkan nomor Kapsi secara dinamis, THE Mesin_Format SHALL memutakhirkan
   setiap kemunculan Referensi_Silang berbentuk "Gambar X.Y" dan "Tabel X.Y" pada paragraf narasi,
   termasuk kemunculan berulang yang merujuk nomor lama yang sama, agar seluruhnya (100%) sesuai
   dengan nomor Kapsi yang ditetapkan.
2. THE Mesin_Format SHALL melakukan renumbering Referensi_Silang tanpa tabel pemetaan tetap yang
   ditulis dalam kode.
3. THE Mesin_Format SHALL menurunkan pemetaan nomor lama ke nomor baru dari hasil penomoran Kapsi
   pada dokumen yang sedang diproses.
4. IF sebuah Referensi_Silang merujuk nomor yang tidak memiliki Kapsi padanan pada dokumen yang
   sedang diproses, THEN THE Mesin_Format SHALL mempertahankan teks asli Referensi_Silang tanpa
   perubahan dan mencatat peringatan yang menyebutkan teks Referensi_Silang terkait beserta nomor
   yang tidak memiliki padanan.
5. IF nomor lama sebuah Referensi_Silang dapat dipetakan ke lebih dari satu nomor Kapsi baru
   (pemetaan ambigu), THEN THE Mesin_Format SHALL mempertahankan teks asli Referensi_Silang tanpa
   perubahan dan mencatat peringatan yang menyebutkan teks Referensi_Silang terkait beserta seluruh
   nomor baru kandidat.

### Requirement 7: Konfigurasi Path Tanpa Nilai Absolut Tetap

**User Story:** Sebagai pengguna pipeline, saya ingin path masukan dan keluaran dapat dikonfigurasi,
sehingga skrip tidak terikat pada lokasi absolut tertentu.

#### Acceptance Criteria

1. WHEN Mesin_Merge dijalankan, THE Mesin_Merge SHALL memperoleh path Draf dan path `document.xml`
   dari argumen baris perintah bila tersedia, dan bila argumen tidak tersedia dari berkas
   konfigurasi, serta SHALL tidak pernah menggunakan path absolut yang ditulis dalam kode.
2. THE Pipeline_Generasi SHALL menentukan setiap path masukan dan keluaran sebagai path relatif
   terhadap akar ruang kerja (direktori akar repositori tempat Pipeline_Generasi dijalankan) atau
   dari parameter yang disediakan, tanpa menggunakan path absolut yang ditulis dalam kode.
3. WHEN Pipeline_Generasi menerima path relatif melalui argumen atau konfigurasi, THE
   Pipeline_Generasi SHALL menyelesaikan (resolve) path tersebut terhadap akar ruang kerja menjadi
   lokasi konkret sebelum membaca atau menulis berkas.
4. IF sebuah path masukan wajib tidak tersedia atau menunjuk berkas yang tidak dapat dibaca, THEN
   THE Pipeline_Generasi SHALL menghentikan proses sebelum menghasilkan keluaran apa pun,
   menampilkan pesan kesalahan yang menyebutkan path yang hilang atau tidak terbaca, dan SHALL
   tidak membuat atau menimpa berkas keluaran.
5. IF direktori dari path keluaran yang ditentukan tidak tersedia, THEN THE Pipeline_Generasi SHALL
   menghentikan proses dan menampilkan pesan kesalahan yang menyebutkan path keluaran yang tidak
   tersedia, tanpa membuat atau menimpa berkas lain.

### Requirement 8: Kompatibilitas Mundur dengan Draf Saat Ini

**User Story:** Sebagai pengguna pipeline, saya ingin draf saat ini tetap menghasilkan dokumen yang
lolos validasi dan pengujian, sehingga perubahan dinamis tidak merusak hasil yang sudah benar.

#### Acceptance Criteria

1. WHEN Pipeline_Generasi memproses Draf saat ini, THE Pipeline_Generasi SHALL menghasilkan dokumen
   dengan jumlah kegagalan fatal Validator_Struktur sama dengan 0.
2. WHEN Validator_Struktur memeriksa dokumen hasil dari Draf saat ini, THE Validator_Struktur SHALL
   menyelesaikan pemeriksaan tanpa kegagalan baru dibandingkan Dokumen_Referensi selain peringatan
   non-fatal.
3. WHEN suite pengujian pada direktori `tests/` dijalankan terhadap hasil perubahan,
   THE suite_pengujian SHALL berakhir dengan exit code 0, jumlah pengujian gagal 0, dan jumlah error 0.
4. THE Pipeline_Generasi SHALL menghasilkan nomor Kapsi untuk Draf saat ini yang identik dengan
   nomor Kapsi pada Dokumen_Referensi.
5. IF dokumen hasil dari Draf saat ini menghasilkan kegagalan fatal Validator_Struktur, THEN THE
   Pipeline_Generasi SHALL menghentikan promosi hasil, mencatat kegagalan tersebut, dan SHALL tidak
   menimpa Dokumen_Referensi.
6. IF nomor Kapsi hasil berbeda dari Dokumen_Referensi, THEN THE Pipeline_Generasi SHALL mencatat
   peringatan yang menyebutkan nomor lama dan nomor baru yang berbeda.

### Requirement 9: Batasan Lingkup (Non-Goals)

**User Story:** Sebagai pengguna pipeline, saya ingin lingkup perubahan dibatasi pada skrip
generasi, sehingga komponen lain yang sudah benar tidak terdampak.

#### Acceptance Criteria

1. WHEN Validator_Struktur memvalidasi dokumen masukan yang sama sebelum dan sesudah perubahan,
   THE Validator_Struktur SHALL menghasilkan himpunan pemeriksaan dan hasil pass/fail yang identik.
2. WHEN Pipeline_Generasi menjalankan injeksi gambar pasca-COM dengan Manifest_Gambar yang sama
   sebelum dan sesudah perubahan, THE Pipeline_Generasi SHALL menghasilkan kumpulan gambar
   terinjeksi yang identik dalam jumlah gambar, lokasi kapsi penambatan, dan konten media.
3. WHEN Pipeline_Generasi menghasilkan halaman depan setelah perubahan, THE Pipeline_Generasi SHALL
   menghasilkan struktur dan konten halaman depan yang identik dengan keluaran sebelum perubahan,
   kecuali bagian yang diubah semata-mata untuk menggantikan kopling literal atau kasus khusus
   bernama dengan Aturan_Umum guna mendukung deteksi dinamis.
4. WHILE perubahan diterapkan, THE perubahan SHALL terbatas pada skrip generasi di dalam
   Pipeline_Generasi dan SHALL TIDAK memodifikasi berkas maupun perilaku keluaran komponen di luar
   Pipeline_Generasi.
