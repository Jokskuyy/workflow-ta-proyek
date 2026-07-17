# Requirements Document

## Introduction

Fitur ini mendefinisikan sebuah **alur/algoritma penulisan otomatis** yang menghasilkan dan menyusun draf laporan Tugas Akhir "Integrasi Denah Virtual UPNVJ" secara sistematis di berkas `Tugas_Akhir_Draft.md`. Fokus fitur adalah **orkestrasi konten per-bab dan per-sub-bab**: menyusun kerangka bab, mengisi tiap sub-bab sesuai kaidah akademik, menempatkan rujukan Gambar/Tabel, serta merakit urutan bagian menjadi satu draf yang koheren.

Alur ini **bukan** pengganti pipeline format `.docx` yang sudah ada (`skills/scripts/build_pipeline.py`) dan **bukan** pengganti skill `docx-ta-proyek`; keluaran alur ini adalah konten Markdown pada `Tugas_Akhir_Draft.md` yang menjadi masukan bagi pipeline format tersebut.

Alur ini **wajib menghormati** aturan yang sudah ditetapkan:
1. Aturan penulisan pada `.kiro/steering/aturan-penulisan.md` (larangan bullet, hierarki penomoran, penyebutan Gambar/Tabel, definisi + sitasi pada sub-bab teori, konsistensi istilah, lampiran, penomoran gambar).
2. Aturan sitasi pada `.kiro/steering/aturan-sitasi.md` (APA in-text, klaim faktual wajib bersitasi, penanda `[BUTUH SITASI]`).
3. Aturan anti-mengarang: verifikasi fakta/angka ke `project_facts.json` dan gunakan placeholder `[TBD: ...]` bila fakta belum tersedia.

## Glossary

- **Alur_Penulisan**: Sistem/algoritma orkestrasi yang menghasilkan dan menyusun konten draf laporan Tugas Akhir pada berkas draf. Merupakan subjek utama seluruh requirement di dokumen ini.
- **Berkas_Draf**: Berkas Markdown tunggal `Tugas_Akhir_Draft.md` di root repositori yang menjadi keluaran Alur_Penulisan.
- **Kerangka_Bab**: Struktur berjenjang bab dan sub-bab laporan (BAB I–BAB IV beserta sub-babnya) yang menjadi rangka penulisan.
- **Sub_Bab_Teori**: Sub-bab yang menjelaskan konsep/teori (mis. UAT, Black Box, ERD, NavMesh) yang wajib diawali paragraf definisi.
- **Aturan_Penulisan**: Ketentuan pada `.kiro/steering/aturan-penulisan.md`.
- **Aturan_Sitasi**: Ketentuan pada `.kiro/steering/aturan-sitasi.md`.
- **Basis_Fakta**: Berkas `project_facts.json` yang menjadi sumber kebenaran fakta dan angka proyek.
- **Placeholder_TBD**: Penanda teks berbentuk `[TBD: ...]` untuk fakta/angka yang belum tersedia di Basis_Fakta.
- **Penanda_Sitasi_Kurang**: Penanda teks `[BUTUH SITASI]` untuk klaim faktual yang belum memiliki rujukan.
- **Sitasi_APA**: Sitasi dalam-teks bergaya APA berbentuk `(Nama, Tahun)` atau `(Nama et al., Tahun)`.
- **Rujukan_Objek**: Kalimat yang merujuk "Gambar x.y" atau "Tabel x.y" di dalam Berkas_Draf.
- **Daftar_Berjenjang**: Daftar bernomor dengan hierarki `1.` → `a.` → `1)` → `a)`.
- **Peran_Branch**: Lingkup penulisan yang terkait branch aktif (`laporan/iman`, `laporan/dwikhi`, `laporan/faiz`).
- **Konten_Manual**: Bagian teks pada Berkas_Draf yang ditulis atau disunting langsung oleh penulis manusia.

## Requirements

### Requirement 1: Pembuatan Kerangka Bab

**User Story:** Sebagai penulis Tugas Akhir, saya ingin alur menghasilkan kerangka bab dan sub-bab secara otomatis, agar penulisan draf memiliki struktur yang konsisten sejak awal.

#### Acceptance Criteria

1. WHEN penulis memulai Alur_Penulisan pada Berkas_Draf yang belum memuat Kerangka_Bab, THE Alur_Penulisan SHALL menghasilkan Kerangka_Bab yang memuat BAB I sampai BAB IV secara berurutan (BAB I, BAB II, BAB III, BAB IV) beserta seluruh sub-bab baku yang ditetapkan pada Aturan_Penulisan untuk masing-masing bab.
2. WHEN Alur_Penulisan menuliskan setiap judul bab dan sub-bab, THE Alur_Penulisan SHALL menerapkan penomoran hierarkis yang sesuai dengan Aturan_Penulisan (nomor bab pada tingkat bab dan nomor bertingkat pada tingkat sub-bab).
3. IF Berkas_Draf sudah memuat sebuah judul bab atau sub-bab yang identik dengan judul baku (perbandingan mengabaikan perbedaan huruf besar/kecil dan spasi berlebih di awal/akhir), THEN THE Alur_Penulisan SHALL mempertahankan judul yang sudah ada dan SHALL TIDAK menambahkan judul duplikat untuk entri tersebut.
4. IF Berkas_Draf sudah memuat Kerangka_Bab lengkap (seluruh BAB I sampai BAB IV beserta sub-bab bakunya), THEN THE Alur_Penulisan SHALL mempertahankan Kerangka_Bab yang ada tanpa menghasilkan ulang struktur.
5. IF Berkas_Draf tidak dapat dibaca atau ditulis saat Alur_Penulisan berjalan, THEN THE Alur_Penulisan SHALL menghentikan pembuatan Kerangka_Bab, mempertahankan seluruh isi Berkas_Draf yang ada tanpa perubahan, dan menampilkan indikasi kesalahan yang menyatakan Berkas_Draf tidak dapat diakses.

### Requirement 2: Penyusunan Konten Sub-Bab Teori

**User Story:** Sebagai penulis Tugas Akhir, saya ingin setiap sub-bab teori disusun dengan paragraf definisi dan sitasi, agar draf memenuhi kaidah akademik.

#### Acceptance Criteria

1. WHEN Alur_Penulisan menyusun konten sebuah Sub_Bab_Teori, THE Alur_Penulisan SHALL menempatkan tepat satu paragraf definisi yang memuat pernyataan definisi konsep utama Sub_Bab_Teori tersebut sebagai paragraf ke-1 (paragraf pertama) sub-bab.
2. WHEN Alur_Penulisan menuliskan paragraf definisi sebuah Sub_Bab_Teori, THE Alur_Penulisan SHALL menyertakan paling sedikit satu Sitasi_APA berformat in-text `(Nama, Tahun)` atau `(Nama et al., Tahun)` yang menempel langsung pada pernyataan definisi tersebut.
3. IF Alur_Penulisan menuliskan klaim faktual yang bukan pengetahuan umum dan bukan hasil observasi penulis sendiri serta belum memiliki Sitasi_APA, THEN THE Alur_Penulisan SHALL menandai klaim tersebut dengan Penanda_Sitasi_Kurang tepat pada posisi klaim dan SHALL mempertahankan teks klaim tanpa menghapusnya.
4. IF Alur_Penulisan menyelesaikan konten sebuah Sub_Bab_Teori tanpa paragraf definisi bersitasi pada paragraf ke-1, THEN THE Alur_Penulisan SHALL menandai paragraf pertama Sub_Bab_Teori tersebut dengan Penanda_Sitasi_Kurang tanpa menghapus konten yang sudah ditulis.
5. IF sebuah Sitasi_APA pada Sub_Bab_Teori tidak memiliki entri padanan pada Daftar Pustaka, THEN THE Alur_Penulisan SHALL menandai sitasi tersebut dengan Penanda_Sitasi_Kurang dan tidak memperlakukan klaim terkait sebagai klaim yang sudah tervalidasi.

### Requirement 3: Format Daftar Berjenjang

**User Story:** Sebagai penulis Tugas Akhir, saya ingin daftar ditulis dengan penomoran berjenjang tanpa bullet, agar format draf konsisten dengan aturan penulisan.

#### Acceptance Criteria

1. WHEN Alur_Penulisan menuliskan sebuah daftar pada Berkas_Draf, THE Alur_Penulisan SHALL menggunakan Daftar_Berjenjang dengan penanda level yang berurutan dari level 1 hingga level 4: `1.` untuk level 1, `a.` untuk level 2, `1)` untuk level 3, dan `a)` untuk level 4.
2. WHEN Alur_Penulisan menuliskan dua atau lebih item pada level yang sama dalam Daftar_Berjenjang, THE Alur_Penulisan SHALL memberi penomoran berurutan yang bertambah satu langkah (misalnya `1.`, `2.`, `3.` atau `a.`, `b.`, `c.`) dimulai dari penanda awal `1` atau `a` pada item pertama level tersebut.
3. WHEN Alur_Penulisan memulai sebuah sub-level baru di bawah suatu item dalam Daftar_Berjenjang, THE Alur_Penulisan SHALL mengatur ulang penomoran sub-level tersebut ke penanda awal (`1` atau `a`) sesuai jenis penanda yang berlaku untuk level itu.
4. IF sebuah daftar pada Berkas_Draf memerlukan kedalaman lebih dari 4 level, THEN THE Alur_Penulisan SHALL membatasi penomoran berjenjang maksimum pada 4 level dan mempertahankan penanda level 4 (`a)`) untuk setiap item yang berada lebih dalam dari level 4.
5. WHEN Alur_Penulisan menuliskan seluruh daftar pada Berkas_Draf, THE Alur_Penulisan SHALL tidak menggunakan penanda bullet `-`, `*`, atau `+` pada item level mana pun.

### Requirement 4: Penempatan Rujukan Gambar dan Tabel

**User Story:** Sebagai penulis Tugas Akhir, saya ingin rujukan Gambar dan Tabel ditempatkan sesuai aturan, agar narasi draf enak dibaca dan penomoran benar.

#### Acceptance Criteria

1. WHEN Alur_Penulisan menuliskan sebuah Rujukan_Objek, THE Alur_Penulisan SHALL menempatkan frasa "Gambar x.y" atau "Tabel x.y" pada posisi yang bukan awal paragraf dan bukan tepat setelah tanda akhir kalimat (titik, tanda tanya, atau tanda seru).
2. WHEN Alur_Penulisan memberi nomor pada sebuah Gambar atau Tabel, THE Alur_Penulisan SHALL menetapkan nomor berformat "x.y" dengan x adalah nomor bab tempat objek berada dan y adalah urutan kemunculan objek pada bab tersebut yang dimulai dari 1 dan bertambah 1 mengikuti urutan kemunculan (reading order) pada Berkas_Draf.
3. WHEN Alur_Penulisan berpindah ke bab baru, THE Alur_Penulisan SHALL mengatur ulang penghitung urutan (y) ke 1 secara terpisah untuk Gambar dan untuk Tabel.
4. IF Alur_Penulisan menuliskan Rujukan_Objek ke Gambar atau Tabel yang belum bernomor atau tidak ada pada Berkas_Draf, THEN THE Alur_Penulisan SHALL menghasilkan indikasi kesalahan yang menyebutkan rujukan tersebut dan mempertahankan narasi tanpa menghapusnya.

### Requirement 5: Anti-Mengarang Fakta dan Angka

**User Story:** Sebagai penulis Tugas Akhir, saya ingin alur tidak pernah mengarang fakta atau angka, agar isi laporan dapat dipertanggungjawabkan.

#### Acceptance Criteria

1. WHEN Alur_Penulisan hendak menuliskan sebuah nilai fakta atau angka proyek, THE Alur_Penulisan SHALL mencari nilai tersebut pada Basis_Fakta sebelum menuliskan nilai apa pun pada posisi tersebut.
2. WHEN sebuah nilai fakta atau angka proyek tersedia pada Basis_Fakta, THE Alur_Penulisan SHALL menuliskan nilai tersebut persis sama dengan yang tercatat pada Basis_Fakta tanpa perubahan, pembulatan, atau penambahan.
3. IF sebuah fakta atau angka proyek tidak tersedia pada Basis_Fakta, THEN THE Alur_Penulisan SHALL menuliskan Placeholder_TBD yang memuat deskripsi fakta atau angka yang belum tersedia pada posisi nilai tersebut.
4. IF nilai fakta atau angka proyek yang hendak dituliskan berbeda dari nilai yang tercatat pada Basis_Fakta, THEN THE Alur_Penulisan SHALL menuliskan nilai dari Basis_Fakta dan menolak nilai lain.
5. THE Alur_Penulisan SHALL menuliskan setiap nilai fakta dan angka proyek hanya bersumber dari Basis_Fakta atau sebagai Placeholder_TBD, dan tidak menuliskan nilai yang berasal dari sumber lain.

### Requirement 6: Konsistensi Istilah

**User Story:** Sebagai penulis Tugas Akhir, saya ingin istilah digunakan secara konsisten di seluruh draf, agar tidak membingungkan pembaca.

#### Acceptance Criteria

1. WHEN Alur_Penulisan menuliskan sebuah istilah yang memiliki padanan baku terdaftar pada daftar istilah proyek, THE Alur_Penulisan SHALL menggunakan satu bentuk baku yang identik untuk istilah tersebut di seluruh Berkas_Draf, tanpa kecuali.
2. WHEN Alur_Penulisan melakukan pemeriksaan konsistensi istilah, THE Alur_Penulisan SHALL memindai seluruh isi Berkas_Draf terhadap setiap istilah yang memiliki padanan baku terdaftar dengan pencocokan yang mengabaikan perbedaan huruf besar/kecil.
3. IF Alur_Penulisan mendeteksi dua atau lebih bentuk istilah berbeda yang merujuk pada satu konsep yang sama (yaitu memiliki padanan baku terdaftar yang sama) di dalam Berkas_Draf, THEN THE Alur_Penulisan SHALL melaporkan ketidakkonsistenan tersebut kepada penulis dengan menyertakan setiap bentuk istilah yang ditemukan beserta lokasi kemunculannya di dalam Berkas_Draf, dan SHALL tidak mengubah isi Berkas_Draf secara otomatis.
4. IF Alur_Penulisan menuliskan sebuah istilah yang tidak memiliki padanan baku terdaftar pada daftar istilah proyek, THEN THE Alur_Penulisan SHALL menggunakan bentuk istilah kemunculan pertama sebagai acuan dan mempertahankan bentuk yang sama tersebut pada seluruh kemunculan berikutnya di dalam Berkas_Draf.

### Requirement 7: Perakitan dan Urutan Bagian

**User Story:** Sebagai penulis Tugas Akhir, saya ingin bagian-bagian draf dirakit dalam urutan yang benar, agar draf akhir koheren dan siap diformat.

#### Acceptance Criteria

1. WHEN Alur_Penulisan merakit konten ke Berkas_Draf, THE Alur_Penulisan SHALL menyusun seluruh bab dan sub-bab dengan urutan yang sama persis seperti urutan entri pada Kerangka_Bab, termasuk tingkat kedalaman (bab dan sub-bab) sesuai hierarki Kerangka_Bab.
2. THE Alur_Penulisan SHALL menghasilkan Berkas_Draf yang tetap dapat diproses oleh pipeline format `.docx` yang sudah ada tanpa memodifikasi tahap format tersebut.
3. IF terdapat satu atau lebih entri pada Kerangka_Bab yang tidak memiliki konten terkait saat perakitan, THEN THE Alur_Penulisan SHALL menghentikan perakitan Berkas_Draf dan menghasilkan indikasi kesalahan yang menyebutkan setiap entri Kerangka_Bab yang kontennya hilang, tanpa menghasilkan Berkas_Draf sebagian.
4. IF terdapat konten yang tidak memiliki entri padanan pada Kerangka_Bab, THEN THE Alur_Penulisan SHALL menghentikan perakitan Berkas_Draf dan menghasilkan indikasi kesalahan yang menyebutkan konten yatim tersebut, tanpa menghasilkan Berkas_Draf sebagian.
5. WHEN Alur_Penulisan selesai merakit Berkas_Draf tanpa kesalahan, THE Alur_Penulisan SHALL memastikan setiap entri Kerangka_Bab muncul tepat satu kali di dalam Berkas_Draf.

### Requirement 8: Idempotensi Penulisan Ulang

**User Story:** Sebagai penulis Tugas Akhir, saya ingin dapat menjalankan alur berulang kali dengan aman, agar draf tidak terduplikasi atau rusak.

#### Acceptance Criteria

1. WHEN Alur_Penulisan dijalankan ulang pada Berkas_Draf yang sudah memuat Kerangka_Bab yang sama, THE Alur_Penulisan SHALL menghasilkan struktur bab dan sub-bab dengan judul, urutan, dan penomoran yang identik dengan hasil jalannya sebelumnya, tanpa menambahkan bab atau sub-bab duplikat.
2. WHILE Alur_Penulisan memproses Berkas_Draf, THE Alur_Penulisan SHALL mempertahankan seluruh Konten_Manual yang sudah ada tanpa menimpa, menghapus, atau mengubah isinya.
3. IF sebuah bab atau sub-bab pada Kerangka_Bab sudah ada di Berkas_Draf, THEN THE Alur_Penulisan SHALL memperbarui isi bab tersebut di lokasi yang sama tanpa membuat salinan bab baru.
4. IF Kerangka_Bab pada jalannya saat ini berbeda dari struktur yang sudah ada di Berkas_Draf, THEN THE Alur_Penulisan SHALL menambahkan hanya bab atau sub-bab yang belum ada dan mempertahankan bab yang sudah ada beserta Konten_Manual-nya.
5. IF Berkas_Draf tidak dapat diakses atau dibaca saat Alur_Penulisan dijalankan ulang, THEN THE Alur_Penulisan SHALL menghentikan proses tanpa mengubah Berkas_Draf dan menampilkan pesan kesalahan yang menunjukkan bahwa berkas tidak dapat diakses.

### Requirement 9: Penulisan Sadar Peran Branch

**User Story:** Sebagai anggota tim dengan lingkup peran tertentu, saya ingin alur menyesuaikan cakupan penulisan dengan peran branch aktif, agar setiap anggota menulis pada lingkupnya.

#### Acceptance Criteria

1. WHERE branch aktif adalah salah satu dari `laporan/iman`, `laporan/dwikhi`, atau `laporan/faiz`, THE Alur_Penulisan SHALL membatasi cakupan konten yang dihasilkan hanya pada lingkup Peran_Branch yang bersangkutan.
2. WHEN Alur_Penulisan menghasilkan konten yang berada dalam lingkup Peran_Branch aktif, THE Alur_Penulisan SHALL menuliskan konten tersebut ke Berkas_Draf.
3. IF penulis meminta konten yang berada di luar lingkup Peran_Branch aktif, THEN THE Alur_Penulisan SHALL menolak menghasilkan konten tersebut dan menghasilkan indikasi yang menyebutkan Peran_Branch yang seharusnya menangani konten itu.
4. WHERE Peran_Branch tidak dapat ditentukan, THE Alur_Penulisan SHALL menahan pembuatan konten dan meminta penulis menentukan lingkup Peran_Branch terlebih dahulu.
5. WHEN Alur_Penulisan mulai menghasilkan konten, THE Alur_Penulisan SHALL menampilkan indikasi Peran_Branch aktif yang sedang menjadi acuan cakupan.

### Requirement 10: Penanganan Masukan Tidak Lengkap

**User Story:** Sebagai penulis Tugas Akhir, saya ingin alur menangani masukan yang belum lengkap secara jelas, agar saya tahu bagian mana yang perlu dilengkapi.

#### Acceptance Criteria

1. IF Berkas_Draf tidak dapat diakses setelah 3 kali percobaan dalam rentang waktu 30 detik saat Alur_Penulisan dijalankan, THEN THE Alur_Penulisan SHALL menghentikan proses tanpa mengubah isi Berkas_Draf yang sudah ada.
2. WHEN Alur_Penulisan menghentikan proses akibat Berkas_Draf tidak dapat diakses, THE Alur_Penulisan SHALL menampilkan pesan galat yang menyebutkan penyebab kegagalan akses beserta nama Berkas_Draf yang terpengaruh.
3. IF Basis_Fakta tidak dapat diakses setelah 3 kali percobaan dalam rentang waktu 30 detik saat Alur_Penulisan memerlukan verifikasi fakta, THEN THE Alur_Penulisan SHALL menuliskan Placeholder_TBD pada setiap nilai fakta yang bergantung pada Basis_Fakta.
4. IF Berkas_Draf dapat diakses tetapi memiliki bagian wajib yang kosong saat Alur_Penulisan dijalankan, THEN THE Alur_Penulisan SHALL menuliskan Placeholder_TBD pada setiap bagian wajib yang kosong.
5. WHEN Alur_Penulisan menuliskan Placeholder_TBD, THE Alur_Penulisan SHALL melaporkan kepada penulis daftar setiap bagian yang diberi Placeholder_TBD beserta penyebabnya.
