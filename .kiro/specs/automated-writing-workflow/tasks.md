# Implementation Plan: Alur Penulisan Otomatis

## Overview

Rencana implementasi ini menerjemahkan desain **Alur_Penulisan** menjadi langkah-langkah pengkodean bertahap dalam Python (selaras dengan `skills/scripts/`), memakai **Hypothesis** untuk property-based testing (repositori sudah memakai `.hypothesis/`). Pendekatannya mengikuti prinsip **inti murni, tepi bersisi-efek**: seluruh komponen transformasi Markdown dibangun sebagai fungsi murni yang mudah diuji secara property-based, sedangkan akses berkas/git diisolasi pada lapisan I/O tipis.

Kode inti ditempatkan pada paket baru `skills/scripts/alur_penulisan/`, dan seluruh pengujian pada `tests/`. Keluaran akhir adalah konten Markdown pada `Tugas_Akhir_Draft.md` yang **tetap kompatibel** dengan pipeline format `.docx` yang sudah ada (`skills/scripts/merge_draft_to_docx.py`, `build_pipeline.py`) — tahap format **tidak boleh dimodifikasi**.

Konvensi pengujian:
- Setiap property test dijalankan minimal **100 iterasi** (`@settings(max_examples=100)`).
- Setiap property test diberi komentar penanda berformat:
  `# Feature: automated-writing-workflow, Property {number}: {property_text}`
- Setiap correctness property (Property 1–27) diimplementasikan oleh **satu** property test.

## Tasks

- [x] 1. Siapkan struktur paket dan data models inti
  - [x] 1.1 Buat paket dan definisikan data models serta DraftModel
    - Buat paket `skills/scripts/alur_penulisan/` dengan `__init__.py`
    - Definisikan seluruh data models pada `models.py`: `Level`, `SkeletonEntry`, `Skeleton`, `BlockKind`, `ContentBlock`, `Paragraph`, `ListNode`, `ObjectKind`, `NumberedObject`, `ObjectReference`, `FactValue`, `TermRegistry`, `TermOccurrence`, `InconsistencyReport`, `ScopeState`, `BranchScope`, `FindingKind`, `Finding`, `WriterReport`
    - Definisikan `DraftModel` (representasi in-memory berorientasi blok) beserta fungsi round-trip ke/dari teks Markdown yang kompatibel dengan `merge_draft_to_docx.py` (heading `#`, daftar berindentasi 3 spasi, blok `[TABLE]`, pipe table, page break `---`, seksi `# DAFTAR PUSTAKA`)
    - Definisikan kelas exception `DraftInaccessibleError` dan `AssemblyError`
    - _Requirements: 1.1, 7.2, 8.2_

  - [x]* 1.2 Tulis unit test untuk data models dan round-trip DraftModel
    - Uji `DraftModel` mem-parse lalu men-serialize kembali teks Markdown tanpa kehilangan struktur (round-trip)
    - Uji penandaan blok `BlockKind.MANUAL` dipertahankan pada model
    - _Requirements: 7.2, 8.2_

- [x] 2. Implementasikan lapisan I/O berkas (DraftIO)
  - [x] 2.1 Implementasikan `draft_io.py` dengan `read_draft` dan `write_draft`
    - Tangani retry akses hingga 3 kali dalam jendela 30 detik
    - Lempar `DraftInaccessibleError` (memuat nama berkas dan penyebab) sebelum ada penulisan apa pun bila akses tetap gagal
    - Pastikan `write_draft` tidak menghasilkan berkas sebagian saat gagal
    - _Requirements: 1.5, 8.5, 10.1, 10.2_

  - [x]* 2.2 Tulis unit test untuk DraftIO
    - Uji berkas terkunci/tak terbaca → `DraftInaccessibleError` dengan nama berkas dan tanpa penulisan
    - Uji perilaku retry (3x / 30 detik) dengan waktu/percobaan yang di-mock
    - _Requirements: 1.5, 8.5, 10.1, 10.2_

- [x] 3. Implementasikan SkeletonGenerator
  - [x] 3.1 Implementasikan `skeleton.py` dengan `generate_skeleton` dan `title_matches`
    - Hasilkan Kerangka_Bab BAB I–IV berurutan beserta sub-bab baku dari `skills/references/outline-4bab.md` dengan penomoran hierarkis sesuai level entri
    - `title_matches` membandingkan judul mengabaikan perbedaan huruf besar/kecil dan spasi tepi
    - Pertahankan judul yang sudah ada (cocok) tanpa menambah duplikat; bila kerangka sudah lengkap jangan hasilkan ulang
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [x]* 3.2 Tulis property test untuk kelengkapan dan urutan Kerangka_Bab
    - **Property 1: Kelengkapan dan urutan Kerangka_Bab**
    - **Validates: Requirements 1.1, 1.2**

  - [x]* 3.3 Tulis property test untuk pencegahan duplikasi judul kerangka
    - **Property 2: Tidak ada duplikasi judul kerangka**
    - **Validates: Requirements 1.3**

- [x] 4. Implementasikan ListFormatter
  - [x] 4.1 Implementasikan `list_formatter.py` dengan `render_list`, `marker_for_level`, `clamp_level`
    - Penanda level 1–4: `1.`, `a.`, `1)`, `a)`; penomoran bersaudara berurutan +1 mulai dari `1`/`a`
    - Reset sub-level baru ke penanda awal; kedalaman >4 dipatok ke penanda level 4 (`a)`) via `clamp_level`
    - Jangan pernah memakai penanda bullet `-`, `*`, `+`; keluaran berindentasi 3 spasi per level (selaras `LIST_INDENT_UNIT = 3`)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x]* 4.2 Tulis property test untuk kebenaran penomoran Daftar_Berjenjang
    - **Property 7: Kebenaran penomoran Daftar_Berjenjang**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4**

  - [x]* 4.3 Tulis property test untuk larangan penanda bullet
    - **Property 8: Tidak ada penanda bullet**
    - **Validates: Requirements 3.5**

- [x] 5. Checkpoint - Pastikan seluruh test lulus
  - Pastikan seluruh test lulus, tanyakan kepada penulis bila muncul pertanyaan.

- [x] 6. Implementasikan SectionContentWriter
  - [x] 6.1 Implementasikan `content_writer.py` dengan `write_theory_subchapter` dan `has_cited_definition`
    - Tempatkan tepat satu paragraf definisi sebagai paragraf pertama Sub_Bab_Teori dengan minimal satu Sitasi_APA menempel
    - Tandai klaim faktual tanpa sitasi dengan `[BUTUH SITASI]` tanpa menghapus teks; bila paragraf pertama tak bersitasi, tandai paragraf pertama dengan `[BUTUH SITASI]`
    - Sitasi tanpa entri padanan di Daftar Pustaka ditandai `[BUTUH SITASI]` dan klaim tidak dianggap tervalidasi
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x]* 6.2 Tulis property test untuk paragraf definisi bersitasi
    - **Property 4: Paragraf definisi bersitasi pada Sub_Bab_Teori**
    - **Validates: Requirements 2.1, 2.2, 2.4**

  - [x]* 6.3 Tulis property test untuk penandaan klaim tanpa sitasi
    - **Property 5: Penandaan klaim tanpa sitasi tanpa penghapusan teks**
    - **Validates: Requirements 2.3, 2.4**

  - [x]* 6.4 Tulis property test untuk sitasi tanpa entri Daftar Pustaka
    - **Property 6: Sitasi tanpa entri Daftar Pustaka ditandai**
    - **Validates: Requirements 2.5**

- [x] 7. Implementasikan FactVerifier dan FactStore
  - [x] 7.1 Implementasikan `fact_verifier.py` dengan `FactStore`, `resolve_fact`, `emit_value`
    - Cari nilai pada `project_facts.json` sebelum menulis; tulis nilai persis tanpa pembulatan/penambahan
    - Tulis `[TBD: ...]` bila nilai tidak tersedia; bila kandidat berbeda dari Basis_Fakta, pakai nilai Basis_Fakta dan tolak lainnya
    - Bila Basis_Fakta tidak dapat diakses setelah retry (3x/30 dtk), turunkan seluruh nilai bergantung fakta menjadi `[TBD: ...]` dengan penyebab
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 10.3_

  - [x]* 7.2 Tulis property test untuk sumber nilai fakta terbatas
    - **Property 12: Sumber nilai fakta terbatas pada Basis_Fakta atau Placeholder_TBD**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**

  - [x]* 7.3 Tulis property test untuk Basis_Fakta tak terakses
    - **Property 13: Basis_Fakta tak terakses memaksa Placeholder_TBD**
    - **Validates: Requirements 10.3**

  - [x]* 7.4 Tulis unit test untuk perilaku "cari sebelum tulis"
    - Verifikasi via mock/spy bahwa `FactStore` dikonsultasi sebelum nilai apa pun ditulis
    - _Requirements: 5.1_

- [x] 8. Implementasikan FigureTableManager
  - [x] 8.1 Implementasikan `figure_table.py` dengan `number_objects` dan `is_valid_reference_position`
    - Nomori Gambar/Tabel `x.y`: x = nomor bab, y = urutan kemunculan (reading order) mulai 1; reset y per bab, terpisah Gambar dan Tabel
    - Validasi posisi Rujukan_Objek: tidak di awal paragraf dan tidak tepat setelah tanda akhir kalimat (`.`, `?`, `!`)
    - Rujukan ke objek yang belum bernomor/tidak ada → hasilkan `Finding(DANGLING_REFERENCE)` dan pertahankan narasi tanpa menghapus
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [x]* 8.2 Tulis property test untuk posisi valid Rujukan_Objek
    - **Property 9: Posisi valid Rujukan_Objek**
    - **Validates: Requirements 4.1**

  - [x]* 8.3 Tulis property test untuk penomoran Gambar/Tabel per bab
    - **Property 10: Penomoran Gambar dan Tabel mengikuti reading order per bab**
    - **Validates: Requirements 4.2, 4.3**

  - [x]* 8.4 Tulis property test untuk rujukan objek menggantung
    - **Property 11: Rujukan objek menggantung dilaporkan tanpa menghapus narasi**
    - **Validates: Requirements 4.4**

- [x] 9. Checkpoint - Pastikan seluruh test lulus
  - Pastikan seluruh test lulus, tanyakan kepada penulis bila muncul pertanyaan.

- [x] 10. Implementasikan TermConsistencyChecker
  - [x] 10.1 Implementasikan `term_checker.py` dengan `scan_terms` dan `canonical_form`
    - Untuk istilah berpadanan baku: normalkan seluruh kemunculan ke satu bentuk baku identik, pemindaian seluruh draf mengabaikan case
    - Dua+ bentuk berbeda untuk satu konsep sama → hasilkan `InconsistencyReport` memuat setiap bentuk beserta lokasi kemunculan, tanpa mengubah draf otomatis
    - Istilah tanpa padanan baku: bentuk kemunculan pertama menjadi acuan dan dipertahankan pada kemunculan berikutnya
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [x]* 10.2 Tulis property test untuk konsistensi istilah berpadanan baku
    - **Property 14: Konsistensi istilah berpadanan baku**
    - **Validates: Requirements 6.1, 6.2**

  - [x]* 10.3 Tulis property test untuk laporan inkonsistensi tanpa mutasi
    - **Property 15: Laporan inkonsistensi istilah tanpa mutasi otomatis**
    - **Validates: Requirements 6.3**

  - [x]* 10.4 Tulis property test untuk istilah tanpa padanan baku
    - **Property 16: Istilah tanpa padanan baku memakai bentuk kemunculan pertama**
    - **Validates: Requirements 6.4**

- [x] 11. Implementasikan IdempotentMerger
  - [x] 11.1 Implementasikan `merger.py` dengan `merge` dan `is_manual_content`
    - Pertahankan seluruh Konten_Manual (`BlockKind.MANUAL`) tanpa menimpa/menghapus/mengubah
    - Perbarui bab/sub-bab yang sudah ada di lokasi yang sama sehingga muncul tepat satu kali (tanpa salinan baru)
    - Gabungkan kerangka berbeda secara union: tambahkan hanya entri baru, pertahankan bab lama beserta Konten_Manual
    - _Requirements: 8.2, 8.3, 8.4_

  - [x]* 11.2 Tulis property test untuk pelestarian Konten_Manual
    - **Property 21: Konten_Manual dipertahankan utuh**
    - **Validates: Requirements 8.2**

  - [x]* 11.3 Tulis property test untuk pembaruan bab tanpa duplikasi lokasi
    - **Property 22: Pembaruan bab yang ada tanpa duplikasi lokasi**
    - **Validates: Requirements 8.3**

  - [x]* 11.4 Tulis property test untuk penggabungan kerangka berbeda
    - **Property 23: Penggabungan kerangka berbeda bersifat union yang mempertahankan konten lama**
    - **Validates: Requirements 8.4**

- [x] 12. Implementasikan Assembler
  - [x] 12.1 Implementasikan `assembler.py` dengan `assemble` dan `AssemblyError`
    - Susun bab/sub-bab persis mengikuti urutan dan kedalaman Kerangka_Bab; setiap entri muncul tepat satu kali saat sukses
    - Entri tanpa konten → `AssemblyError` menyebut daftar entri hilang, tanpa draf sebagian
    - Konten yatim (tanpa entri padanan) → `AssemblyError` menyebut konten yatim, tanpa draf sebagian
    - _Requirements: 7.1, 7.3, 7.4, 7.5_

  - [x]* 12.2 Tulis property test untuk urutan dan kedalaman perakitan
    - **Property 17: Perakitan mempertahankan urutan dan kedalaman Kerangka_Bab**
    - **Validates: Requirements 7.1**

  - [x]* 12.3 Tulis property test untuk kemunculan entri tepat satu kali
    - **Property 18: Perakitan sukses memunculkan setiap entri tepat satu kali**
    - **Validates: Requirements 7.5**

  - [x]* 12.4 Tulis property test untuk entri tanpa konten
    - **Property 19: Entri tanpa konten menghentikan perakitan tanpa draf sebagian**
    - **Validates: Requirements 7.3**

  - [x]* 12.5 Tulis property test untuk konten yatim
    - **Property 20: Konten yatim menghentikan perakitan tanpa draf sebagian**
    - **Validates: Requirements 7.4**

- [x] 13. Implementasikan BranchScopeResolver
  - [x] 13.1 Implementasikan `branch_scope.py` dengan `resolve_scope` dan `in_scope`
    - Petakan branch aktif `laporan/iman|dwikhi|faiz` ke `BranchScope` (state `RESOLVED`, role, `owned_entries`); branch tak dikenal/None → `UNDETERMINED`
    - `in_scope` menentukan apakah sebuah entri berada dalam lingkup peran aktif
    - Sediakan indikasi peran aktif dan penolakan permintaan di luar lingkup (`Finding(OUT_OF_SCOPE)` menyebut peran pemilik)
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [x]* 13.2 Tulis property test untuk cakupan sesuai Peran_Branch
    - **Property 24: Cakupan penulisan sesuai Peran_Branch aktif**
    - **Validates: Requirements 9.1, 9.2**

  - [x]* 13.3 Tulis property test untuk penolakan permintaan di luar lingkup
    - **Property 25: Permintaan di luar lingkup ditolak dengan indikasi peran**
    - **Validates: Requirements 9.3**

  - [x]* 13.4 Tulis unit test untuk peran tak tentu dan indikasi peran aktif
    - Peran `UNDETERMINED` → alur menahan pembuatan konten dan meminta lingkup
    - Indikasi peran aktif muncul pada laporan saat mulai
    - _Requirements: 9.4, 9.5_

- [x] 14. Implementasikan ReportBuilder
  - [x] 14.1 Implementasikan `report.py` dengan `build_report` dan penanganan bagian wajib kosong
    - Kumpulkan seluruh temuan menjadi `WriterReport`: `[TBD: ...]`, `[BUTUH SITASI]`, inkonsistensi istilah, rujukan objek menggantung
    - Bagian wajib yang kosong pada Berkas_Draf yang dapat diakses ditulis `[TBD: ...]`
    - Setiap `[TBD: ...]` dilaporkan beserta penyebabnya (jumlah entri laporan TBD = jumlah `[TBD: ...]` pada draf)
    - _Requirements: 10.4, 10.5_

  - [x]* 14.2 Tulis property test untuk bagian wajib kosong diberi Placeholder_TBD
    - **Property 26: Bagian wajib kosong diberi Placeholder_TBD**
    - **Validates: Requirements 10.4**

  - [x]* 14.3 Tulis property test untuk pelaporan setiap Placeholder_TBD
    - **Property 27: Setiap Placeholder_TBD dilaporkan beserta penyebabnya**
    - **Validates: Requirements 10.5**

- [x] 15. Checkpoint - Pastikan seluruh test lulus
  - Pastikan seluruh test lulus, tanyakan kepada penulis bila muncul pertanyaan.

- [x] 16. Rangkai orkestrasi pipeline dan integrasi
  - [x] 16.1 Implementasikan `pipeline.py` yang merangkai seluruh komponen menjadi `run_alur`
    - Urutkan: resolusi Peran_Branch → baca Berkas_Draf + Basis_Fakta → SkeletonGenerator → SectionContentWriter → ListFormatter → FactVerifier → FigureTableManager → TermConsistencyChecker → IdempotentMerger → Assembler → tulis Berkas_Draf + `WriterReport`
    - Tahan proses bila Peran_Branch `UNDETERMINED` (minta lingkup); tampilkan indikasi peran aktif
    - Gagal aman tanpa draf sebagian pada `DraftInaccessibleError` maupun `AssemblyError` (pertahankan isi lama)
    - _Requirements: 1.5, 7.2, 7.3, 7.4, 8.5, 9.4, 9.5, 10.1_

  - [x]* 16.2 Tulis property test untuk idempotensi menjalankan ulang alur
    - **Property 3: Idempotensi menjalankan ulang alur**
    - **Validates: Requirements 1.4, 8.1**

  - [x]* 16.3 Tulis integration test kompatibilitas pipeline (bukan PBT)
    - Jalankan `merge_draft_to_docx.parse_markdown` pada 1–3 draf hasil `run_alur` dan verifikasi parsing berhasil tanpa error serta struktur item terparse sesuai harapan
    - Verifikasi indentasi daftar keluaran = 3 spasi/level agar `compute_list_level` menghasilkan level yang sama dengan struktur logis
    - Tidak menjalankan `build_pipeline.py` penuh maupun memodifikasi tahap format
    - _Requirements: 7.2_

  - [x]* 16.4 Tulis unit test untuk gagal aman end-to-end
    - Berkas_Draf tak terakses → `DraftInaccessibleError`, tanpa penulisan, isi lama dipertahankan
    - _Requirements: 1.5, 8.5, 10.1, 10.2_

- [x] 17. Checkpoint akhir - Pastikan seluruh test lulus
  - Pastikan seluruh test lulus, tanyakan kepada penulis bila muncul pertanyaan.

## Notes

- Tugas bertanda `*` bersifat opsional (pengujian) dan dapat dilewati untuk MVP lebih cepat; tugas inti implementasi tidak boleh dilewati.
- Setiap tugas merujuk klausa requirement spesifik untuk keterlacakan.
- Checkpoint memastikan validasi bertahap.
- Property test memvalidasi properti kebenaran universal (Property 1–27), masing-masing minimal 100 iterasi dan diberi komentar penanda `# Feature: automated-writing-workflow, Property {number}: {property_text}`.
- Unit test dan integration test memvalidasi contoh spesifik, kondisi galat, serta kompatibilitas dengan `merge_draft_to_docx.py` — tahap format `.docx` tidak dimodifikasi.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["2.1", "3.1", "4.1", "7.1", "8.1", "10.1", "11.1", "12.1", "13.1", "14.1"] },
    { "id": 2, "tasks": ["1.2", "6.1", "2.2", "3.2", "3.3", "4.2", "4.3", "7.2", "7.3", "7.4", "8.2", "8.3", "8.4", "10.2", "10.3", "10.4", "11.2", "11.3", "11.4", "12.2", "12.3", "12.4", "12.5", "13.2", "13.3", "13.4", "14.2", "14.3"] },
    { "id": 3, "tasks": ["6.2", "6.3", "6.4", "16.1"] },
    { "id": 4, "tasks": ["16.2", "16.3", "16.4"] }
  ]
}
```
