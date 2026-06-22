# Requirements Document

## Introduction

Dokumen ini mendefinisikan kebutuhan untuk peningkatan **tahap penulisan (writing
stage)** pada pipeline penyusunan laporan Tugas Akhir, yaitu proses konversi draf
Markdown (`Tugas_Akhir_Draft.md`) menjadi XML Word (`document.xml`). Tahap penulisan
berada pada dua berkas skrip:

- `scratch/merge_draft_to_docx.py` (fungsi `parse_markdown`, `add_formatted_text`,
  `build_p_element`, `build_code_block_elements`, `build_table_element`,
  `merge_draft_to_xml`).
- `clean_bibliography_sdt()` pada `skills/scripts/format_ta_proyek.py`.

Tujuan utama fitur ini adalah **memperbaiki tahap penulisan tanpa merusak apa pun
yang sudah berfungsi**. Karena itu, **non-destruktivitas (preservasi /
kompatibilitas mundur)** dijadikan kelas kebutuhan utama: setiap perubahan WAJIB
mempertahankan perilaku konstruk yang saat ini sudah dirender dengan benar.
Setiap area peningkatan memiliki kriteria preservasinya sendiri, dan terdapat satu
kelompok kebutuhan preservasi lintas-area (cross-cutting) yang eksplisit dan dapat
diuji.

Enam area peningkatan yang dicakup:

1. Daftar Pustaka dinamis + pemeriksaan silang sitasi (prioritas tertinggi).
2. Ketangguhan dan cakupan tokenizer Markdown inline.
3. Penjenjangan (nesting) daftar berdasarkan indentasi.
4. Penomoran daftar terurut (opsional/prioritas lebih rendah).
5. Parsing tabel pipa Markdown standar + perataan kolom.
6. Penjaga penulisan (writing guards) berupa peringatan non-fatal pada validator.

**Di luar lingkup (OUT OF SCOPE), kecuali sebagai batasan preservasi:** penomoran
kapsi dinamis, penulisan ulang referensi silang, injeksi gambar, dan logika
validasi yang sudah selesai (spec `dynamic-generation-pipeline` dan
`image-injection-pipeline-fix`). Konstruk-konstruk tersebut TIDAK boleh berubah
perilakunya dan WAJIB tetap lulus.

### Temuan Awal (Open Issue) — RESOLVED

Analisis kode dan draf sebelumnya menemukan ketidakcocokan faktual yang relevan
dengan kebutuhan R1:

- `clean_bibliography_sdt()` menulis **9 entri** APA secara hardcoded
  (Afiifah 2022, Aliyah 2024, Ghai 2025, Jamaludin 2024, Kurniawan 2018,
  Maulida 2025, Muharam 2023, Siv 2025, Taurusta 2024).
- Bagian `# DAFTAR PUSTAKA` pada `Tugas_Akhir_Draft.md` saat ini memuat **8 entri
  yang berbeda** (Aliyah 2024, Ghai 2025, Jamaludin 2024, Kurniawan 2018,
  Pricillia 2021, Putra 2026, Siv 2025, Taurusta 2024) — memuat Pricillia & Putra,
  serta TIDAK memuat Afiifah, Maulida, dan Muharam.

**Keputusan pengguna (Option B):** Draf (`# DAFTAR PUSTAKA` pada
`Tugas_Akhir_Draft.md`) ditetapkan sebagai **sumber kebenaran (source of truth)**
untuk Daftar_Pustaka. Dengan demikian:

- Preservasi R1 berlaku pada **format, gaya, dan struktur rendering** (gaya
  paragraf APA, Rentang_Miring, indentasi gantung, spasi, urutan = urutan Draf),
  **bukan** pada himpunan entri yang identik byte-per-byte dengan 9 entri hardcoded
  lama.
- Himpunan entri yang dirender mengikuti isi `# DAFTAR PUSTAKA` Draf (saat ini 8
  entri), bukan ke-9 entri hardcoded lama.
- Pemeriksaan silang sitasi (Kriteria 5, 6, 7, 8) tetap berlaku. Ketidakcocokan
  saat ini seperti `(Muharam et al., 2023)` yang tidak memiliki Entri_Referensi
  padanan pada Draf akan **muncul sebagai peringatan non-fatal** (default non-fatal
  per `.kiro/steering/aturan-sitasi.md`) hingga penulis memperbaiki isi Draf, bukan
  sebagai kegagalan.

## Glossary

- **Tahap_Penulisan**: Proses konversi draf Markdown menjadi `document.xml`, terdiri
  atas Mesin_Merge dan Penulis_Bibliografi.
- **Mesin_Merge**: Komponen pada `scratch/merge_draft_to_docx.py` yang mem-parse draf
  dan menyisipkan elemen XML ke `document.xml`.
- **Parser_Markdown**: Fungsi `parse_markdown` pada Mesin_Merge yang mengubah baris draf
  menjadi daftar item terstruktur (`heading`, `paragraph`, `list_item`, `table`,
  `code_block`, `page_break`).
- **Tokenizer_Inline**: Fungsi `add_formatted_text` pada Mesin_Merge yang mengubah teks
  ber-markup inline menjadi satu atau lebih `w:r` (run) Word.
- **Pembangun_Tabel**: Fungsi `build_table_element` pada Mesin_Merge yang membangun elemen
  `w:tbl`.
- **Penulis_Bibliografi**: Fungsi `clean_bibliography_sdt()` pada
  `skills/scripts/format_ta_proyek.py` yang menulis entri Daftar Pustaka ke dalam SDT.
- **Validator**: Skrip `validate_docx_structure.py` yang memeriksa struktur `.docx`
  dan melaporkan temuan fatal dan non-fatal.
- **Draf**: Berkas `Tugas_Akhir_Draft.md`, sumber kebenaran konten laporan.
- **Daftar_Pustaka**: Bagian referensi APA pada laporan; pada Draf ditandai heading
  `# DAFTAR PUSTAKA`.
- **Entri_Referensi**: Satu butir Daftar_Pustaka bergaya APA, yang dapat memuat
  rentang teks miring (mis. nama jurnal).
- **Sitasi_In_Text**: Penyebutan sumber di dalam narasi bergaya APA, berpola
  `(Nama, Tahun)` atau `(Nama et al., Tahun)`, sesuai `.kiro/steering/aturan-sitasi.md`.
- **Rentang_Miring**: Bagian Entri_Referensi yang dirender dengan `w:i`/`w:iCs`
  (mis. nama jurnal/sumber), pada Markdown ditulis dengan `*...*`.
- **Konstruk_Inline**: Markup teks dalam baris: tebal `**...**`, miring `*...*`,
  tebal+miring `***...***`, kode inline `` `...` ``, dan tautan `[teks](url)`.
- **Tabel_Pipa**: Tabel Markdown standar yang menggunakan karakter `|` sebagai
  pemisah kolom dan baris pemisah `---|:--:` untuk menetapkan perataan.
- **Tabel_Kurung**: Tabel format eksisting yang dibatasi penanda `[TABLE]` dan
  `[/TABLE]`.
- **Baris_Pemisah**: Baris kedua Tabel_Pipa berisi tanda hubung dan titik dua
  (mis. `---`, `:---`, `:---:`, `---:`) yang menyatakan perataan per kolom.
- **Output_Baseline**: Keluaran `document.xml` yang dihasilkan Tahap_Penulisan dari
  Draf saat ini SEBELUM perubahan fitur ini diterapkan; menjadi acuan preservasi.
- **Konstruk_Baru**: Setiap kemampuan yang diperkenalkan fitur ini (mis. kode inline,
  tautan, Tabel_Pipa, perataan kolom, sumber bibliografi dinamis).
- **Opt_In_By_Content**: Sifat bahwa Konstruk_Baru hanya aktif bila konten Draf
  benar-benar memuat sintaks pemicunya; dokumen tanpa sintaks tersebut tidak berubah.

## Requirements

### Requirement 1: Daftar Pustaka Dinamis dan Pemeriksaan Silang Sitasi

**User Story:** Sebagai penulis Tugas Akhir, saya ingin Daftar Pustaka bersumber dari
Draf secara dinamis dan diperiksa silang terhadap sitasi in-text, sehingga referensi
tidak perlu di-hardcode di Python dan inkonsistensi sitasi terdeteksi otomatis.

#### Acceptance Criteria

1. THE Penulis_Bibliografi SHALL membaca Entri_Referensi dari bagian `# DAFTAR PUSTAKA`
   pada Draf sebagai sumber data, bukan dari daftar yang ditulis tetap (hardcoded) di
   kode Python.
2. WHEN sebuah Entri_Referensi pada Draf memuat teks dengan penanda `*...*`, THE
   Penulis_Bibliografi SHALL merender bagian tersebut sebagai Rentang_Miring
   (`w:i`/`w:iCs`) dan sisanya sebagai teks biasa.
3. THE Penulis_Bibliografi SHALL merender setiap Entri_Referensi dengan gaya paragraf
   yang sama seperti Output_Baseline: `pStyle` Normal, indentasi `left=567` dan
   `hanging=567`, spasi `before=0`/`after=120`/`line=240`/`lineRule=auto`, dan
   perataan `jc=both`.
4. THE Penulis_Bibliografi SHALL mempertahankan urutan Entri_Referensi sesuai urutan
   kemunculannya pada bagian `# DAFTAR PUSTAKA` di Draf.
5. WHEN sebuah Sitasi_In_Text berpola `(Nama, Tahun)` atau `(Nama et al., Tahun)` tidak
   memiliki Entri_Referensi padanan pada Daftar_Pustaka, THE Validator SHALL menghasilkan
   satu peringatan non-fatal yang menyebut nama dan tahun sitasi tersebut.
6. WHEN sebuah Entri_Referensi pada Daftar_Pustaka tidak pernah dirujuk oleh
   Sitasi_In_Text mana pun, THE Validator SHALL menghasilkan satu peringatan non-fatal
   yang menyebut Entri_Referensi tersebut.
7. WHERE mode pemeriksaan silang dikonfigurasi sebagai fatal, THE Validator SHALL
   memperlakukan ketidakcocokan sitasi-Daftar_Pustaka sebagai temuan fatal; jika tidak
   dikonfigurasi demikian, THE Validator SHALL memperlakukannya sebagai peringatan
   non-fatal secara default.
8. IF bagian `# DAFTAR PUSTAKA` tidak ditemukan pada Draf, THEN THE Penulis_Bibliografi
   SHALL menghasilkan satu peringatan non-fatal yang menyatakan sumber Daftar_Pustaka
   tidak ditemukan dan mempertahankan perilaku terdefinisi (tidak menulis Entri_Referensi
   palsu).

#### Preservation Criteria

9. WHEN Penulis_Bibliografi memproses bagian `# DAFTAR PUSTAKA` Draf saat ini, THE
   Penulis_Bibliografi SHALL menghasilkan struktur paragraf, Rentang_Miring, urutan,
   indentasi, dan spasi yang identik dengan Output_Baseline untuk setiap Entri_Referensi
   yang dirender (preservasi format dan gaya).
10. THE Tahap_Penulisan SHALL TIDAK menerapkan baseline himpunan 9 entri hardcoded
    lama; opsi tersebut tidak dipilih karena pengguna menetapkan Draf sebagai sumber
    kebenaran (Option B). Himpunan Entri_Referensi yang dirender mengikuti isi
    `# DAFTAR PUSTAKA` Draf, dan baseline preservasi yang aktif adalah Kriteria 9
    (preservasi format/gaya).

> Catatan (Open Issue — RESOLVED): Pengguna memilih Draf sebagai sumber kebenaran
> Daftar_Pustaka (Option B, lihat bagian Temuan Awal). Preservasi R1 berlaku pada
> format/gaya (Kriteria 9) dan himpunan entri mengikuti Draf saat ini (8 entri),
> bukan 9 entri hardcoded lama. Sitasi `(Muharam et al., 2023)` yang ada di narasi
> saat ini tidak memiliki padanan pada `# DAFTAR PUSTAKA` Draf, sehingga akan
> memicu peringatan non-fatal Kriteria 5 hingga penulis memperbaiki isi Draf.

### Requirement 2: Ketangguhan dan Cakupan Tokenizer Markdown Inline

**User Story:** Sebagai penulis Tugas Akhir, saya ingin penanganan markup inline yang
tangguh dan lebih lengkap, sehingga tebal, miring, kode inline, dan tautan dirender benar
tanpa kebocoran state pada markup tak seimbang.

#### Acceptance Criteria

1. WHEN teks memuat `**teks**`, THE Tokenizer_Inline SHALL merender `teks` sebagai run tebal
   (`w:b`/`w:bCs`).
2. WHEN teks memuat `*teks*`, THE Tokenizer_Inline SHALL merender `teks` sebagai run miring
   (`w:i`/`w:iCs`).
3. WHEN teks memuat `***teks***`, THE Tokenizer_Inline SHALL merender `teks` sebagai run
   tebal sekaligus miring.
4. WHEN teks memuat karakter asterisk yang di-escape `\*`, THE Tokenizer_Inline SHALL
   merender satu karakter asterisk literal tanpa mengubah state tebal atau miring.
5. WHEN teks memuat `` `kode` ``, THE Tokenizer_Inline SHALL merender `kode` sebagai run
   kode inline dengan font monospace (mis. Consolas).
6. WHEN teks memuat tautan `[teks](url)`, THE Tokenizer_Inline SHALL merender hyperlink Word
   yang menampilkan `teks` dan menargetkan `url`.
7. IF penanda emphasis pada sebuah teks tidak seimbang (mis. `a*b` atau `**c` tanpa
   penutup), THEN THE Tokenizer_Inline SHALL memperlakukan penanda yang tidak berpasangan
   sebagai karakter literal dan TIDAK membawa state format ke teks setelahnya.

#### Preservation Criteria

8. WHEN sebuah teks tidak memuat Konstruk_Inline baru (kode inline, tautan, `***`, atau
   `\*`), THE Tokenizer_Inline SHALL menghasilkan run yang identik byte-per-byte dengan
   Output_Baseline untuk teks tersebut.
9. WHEN sebuah teks memuat hanya `**...**` atau `*...*` yang seimbang seperti pada Draf
   saat ini, THE Tokenizer_Inline SHALL menghasilkan rentang tebal/miring yang identik
   dengan Output_Baseline.

### Requirement 3: Penjenjangan Daftar Berdasarkan Indentasi

**User Story:** Sebagai penulis Tugas Akhir, saya ingin tingkat penjenjangan daftar
ditentukan oleh indentasi sesuai Markdown standar, sehingga struktur daftar bersarang
mencerminkan indentasi nyata, bukan jenis penanda.

#### Acceptance Criteria

1. THE Parser_Markdown SHALL menentukan tingkat penjenjangan (nesting level) sebuah
   `list_item` dari jumlah spasi indentasi di awal baris sesuai konvensi Markdown standar.
2. THE Parser_Markdown SHALL memperlakukan gaya penanda daftar (`1.`, `a.`, `1)`, `a)`)
   sebagai kosmetik dan TIDAK menjadikannya penentu tingkat penjenjangan.
3. WHEN dua baris daftar memiliki indentasi yang berbeda, THE Parser_Markdown SHALL
   menetapkan tingkat penjenjangan yang lebih dalam pada baris dengan indentasi lebih besar.

#### Preservation Criteria

4. WHEN Parser_Markdown memproses daftar pada Draf saat ini, THE Parser_Markdown SHALL
   menghasilkan tingkat penjenjangan dan penanda yang setara dengan Output_Baseline untuk
   setiap `list_item`.
5. WHEN sebuah `list_item` pada Draf tidak memiliki indentasi awal, THE Parser_Markdown
   SHALL menetapkannya pada tingkat penjenjangan terluar sebagaimana Output_Baseline.

### Requirement 4: Penomoran Daftar Terurut (Opsional)

**User Story:** Sebagai penulis Tugas Akhir, saya ingin opsi penomoran daftar terurut
melalui mekanisme penomoran Word, sehingga penomoran dapat konsisten secara otomatis bila
diinginkan, tanpa memaksakan perubahan yang berisiko.

#### Acceptance Criteria

1. WHERE penomoran Word (`numPr`) untuk daftar terurut diaktifkan, THE Mesin_Merge SHALL
   merender item daftar terurut menggunakan properti penomoran Word alih-alih penanda
   tekstual literal.
2. WHERE penomoran Word untuk daftar terurut tidak diaktifkan, THE Mesin_Merge SHALL
   mempertahankan penanda tekstual literal seperti Output_Baseline.

#### Preservation Criteria

3. WHEN opsi penomoran Word tidak diaktifkan, THE Mesin_Merge SHALL merender seluruh daftar
   pada Draf saat ini secara identik dengan Output_Baseline.

### Requirement 5: Parsing Tabel Pipa Standar dan Perataan Kolom

**User Story:** Sebagai penulis Tugas Akhir, saya ingin Mesin_Merge mendukung Tabel_Pipa
Markdown standar beserta perataan kolom, sehingga tabel dapat ditulis dengan sintaks
Markdown umum, sambil tetap mendukung Tabel_Kurung yang sudah ada.

#### Acceptance Criteria

1. WHEN Draf memuat Tabel_Pipa dengan Baris_Pemisah `---|:--:` setelah baris pertama, THE
   Pembangun_Tabel SHALL mem-parse tabel tersebut menjadi elemen `w:tbl`.
2. WHEN Baris_Pemisah menetapkan perataan kolom (`:---` kiri, `:---:` tengah, `---:` kanan),
   THE Pembangun_Tabel SHALL menerapkan perataan tersebut pada sel-sel kolom terkait.
3. WHEN sebuah Tabel_Pipa memiliki Baris_Pemisah, THE Pembangun_Tabel SHALL memperlakukan
   baris di atas Baris_Pemisah sebagai baris header (`tblHeader`) dan tidak merender
   Baris_Pemisah sebagai baris data.
4. THE Pembangun_Tabel SHALL tetap mendukung Tabel_Kurung yang dibatasi `[TABLE]` dan
   `[/TABLE]` seperti perilaku saat ini.

#### Preservation Criteria

5. WHEN Pembangun_Tabel memproses Tabel_Kurung pada Draf saat ini (Tabel 1.1, Tabel 1.2,
   Tabel 3.1, Tabel 3.2, Tabel 3.3, Tabel 3.4), THE Pembangun_Tabel SHALL menghasilkan
   elemen `w:tbl` yang identik dengan Output_Baseline, termasuk baris pertama sebagai
   header dan lebar kolom yang sama.
6. WHERE Draf tidak memuat Tabel_Pipa, THE Pembangun_Tabel SHALL berperilaku identik dengan
   Output_Baseline (Opt_In_By_Content).

### Requirement 6: Penjaga Penulisan (Writing Guards) Non-Fatal

**User Story:** Sebagai penulis Tugas Akhir, saya ingin peringatan non-fatal atas masalah
struktur penulisan, sehingga kesalahan seperti lompatan level heading, sitasi yang tidak
sinkron, dan konstruk cacat tidak lagi diabaikan secara diam-diam.

#### Acceptance Criteria

1. WHEN urutan level heading melompati satu tingkat atau lebih (mis. dari `#` langsung ke
   `###`), THE Validator SHALL menghasilkan satu peringatan non-fatal yang menyebut lokasi
   dan level yang terlewat.
2. WHEN urutan heading BAB tidak menaik secara berurutan, THE Validator SHALL menghasilkan
   satu peringatan non-fatal yang menyebut BAB yang tidak berurutan.
3. THE Validator SHALL melakukan pemeriksaan silang dua arah antara Sitasi_In_Text dan
   Daftar_Pustaka sebagaimana didefinisikan pada Requirement 1 (Kriteria 5 dan 6).
4. IF Parser_Markdown menemukan blok `[TABLE]` tanpa penutup `[/TABLE]`, THEN THE Validator
   SHALL menghasilkan satu peringatan non-fatal yang menyebut konstruk tabel yang tidak
   ditutup.
5. IF Parser_Markdown menemukan penanda emphasis yang tidak seimbang pada sebuah baris,
   THEN THE Validator SHALL menghasilkan satu peringatan non-fatal yang menyebut baris
   tersebut.

#### Preservation Criteria

6. THE Validator SHALL mempertahankan seluruh pemeriksaan dan semantik yang ada saat ini
   tanpa perubahan; pemeriksaan baru pada Requirement 6 SHALL bersifat aditif berupa
   peringatan non-fatal.
7. WHEN Validator memeriksa keluaran dari Draf saat ini, THE Validator SHALL melaporkan
   nol temuan fatal.

### Requirement 7: Preservasi Lintas-Area dan Non-Goal (Cross-Cutting)

**User Story:** Sebagai penulis Tugas Akhir, saya ingin jaminan bahwa seluruh perilaku yang
sudah berfungsi tetap utuh, sehingga peningkatan tahap penulisan tidak menimbulkan regresi
pada dokumen, validasi, kapsi, atau injeksi gambar.

#### Acceptance Criteria

1. WHEN Tahap_Penulisan memproses `Tugas_Akhir_Draft.md` saat ini, THE Tahap_Penulisan
   SHALL menghasilkan dokumen yang lulus `validate_docx_structure.py` dengan nol temuan
   fatal.
2. WHEN dokumen dihasilkan dari Draf saat ini, THE Tahap_Penulisan SHALL mempertahankan
   nomor kapsi yang sama dengan Output_Baseline (logika penomoran kapsi tidak diubah).
3. WHEN dokumen dihasilkan dari Draf saat ini, THE Tahap_Penulisan SHALL merender
   himpunan dan urutan Entri_Referensi yang konsisten dengan isi `# DAFTAR PUSTAKA`
   Draf (Draf sebagai sumber kebenaran, sesuai keputusan Option B pada Requirement 1),
   bukan dengan 9 entri hardcoded lama.
4. THE Tahap_Penulisan SHALL membatasi perubahan kode hanya pada skrip penulisan
   (`scratch/merge_draft_to_docx.py` dan `clean_bibliography_sdt()` pada
   `skills/scripts/format_ta_proyek.py`) dan TIDAK mengubah semantik validasi, injeksi
   gambar, atau penomoran kapsi.
5. WHEN suite pengujian pada direktori `tests/` dijalankan setelah perubahan, THE suite
   SHALL tetap lulus seluruhnya (tetap hijau).
6. THE Tahap_Penulisan SHALL menjaga perilaku pipeline pembangkitan dinamis
   (`dynamic-generation-pipeline`) dan injeksi gambar (`image-injection-pipeline-fix`)
   tidak terpengaruh oleh perubahan fitur ini.
7. WHERE sebuah dokumen tidak menggunakan suatu Konstruk_Baru, THE Tahap_Penulisan SHALL
   menghasilkan keluaran yang identik dengan Output_Baseline untuk dokumen tersebut
   (Opt_In_By_Content).
