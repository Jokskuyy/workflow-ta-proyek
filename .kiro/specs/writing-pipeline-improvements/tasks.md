# Implementation Plan: Peningkatan Tahap Penulisan (Writing Pipeline Improvements)

## Overview

Rencana ini menerjemahkan desain Tahap_Penulisan menjadi langkah-langkah koding
inkremental dalam **Python** (selaras dengan suite Hypothesis yang ada). Prinsip
tertinggi adalah **non-destruktivitas**: tugas pertama menangkap **Output_Baseline**
dan menyimpan **oracle** fungsi lama sebagai jaring pengaman sebelum refaktor apa
pun. Setiap kemampuan baru bersifat **Opt_In_By_Content**.

Urutan: tangkap baseline → fungsi murni (tiap fungsi disertai uji propertinya) →
integrasi ke `add_formatted_text`/`build_table_element`/`parse_markdown`/
`build_p_element` → refaktor bibliografi (`clean_bibliography_sdt` bersumber Draf)
→ penjaga validator (kedua salinan disinkronkan) → tabel pipa opt-in → numPr opsional
→ build end-to-end + verifikasi kompatibilitas mundur + pytest penuh.

Lokasi perubahan inti:
- **Mesin_Merge**: `scratch/merge_draft_to_docx.py` (pipeline menjalankan salinan `scratch/`).
- **Penulis_Bibliografi**: `clean_bibliography_sdt()` pada `skills/scripts/format_ta_proyek.py`.
- **Validator**: `validate_docx_structure.py` — terdapat DUA salinan (`scratch/` dan
  `skills/scripts/`) yang WAJIB dijaga sinkron.

## Tasks

- [x] 1. Tangkap Output_Baseline dan oracle preservasi (jaring pengaman, WAJIB pertama)
  - [x] 1.1 Tangkap Output_Baseline dari Draf saat ini ke `tests/fixtures/`
    - Jalankan Tahap_Penulisan pada `Tugas_Akhir_Draft.md` saat ini dan simpan `word/document.xml` sebagai `tests/fixtures/baseline_document.xml`
    - Simpan nomor kapsi `Tugas_Akhir_Formatted.docx` saat ini ke `tests/fixtures/baseline_caption_numbers.json`
    - Simpan rendering 8 entri `# DAFTAR PUSTAKA` Draf saat ini ke `tests/fixtures/baseline_bibliography.xml`
    - Simpan `w:tbl` Tabel_Kurung saat ini (Tabel 1.1, 1.2, 3.1–3.4) ke `tests/fixtures/baseline_tables.xml`
    - Simpan tingkat (`level`/`left`/`hanging` dxa) tiap `list_item` Draf saat ini ke `tests/fixtures/baseline_list_levels.json`
    - _Requirements: 1.9, 2.8, 2.9, 3.4, 5.5, 7.2, 7.3_

  - [x] 1.2 Bekukan salinan oracle fungsi lama untuk perbandingan byte-per-byte
    - Salin implementasi `add_formatted_text` lama ke modul oracle uji (mis. `tests/fixtures/oracle_add_formatted_text.py`) tanpa mengubah perilakunya
    - Salin implementasi `build_table_element` lama ke `tests/fixtures/oracle_build_table_element.py`
    - Sediakan helper pembanding `lxml.etree.tostring` untuk uji preservasi (Properti 8, 11, 16)
    - _Requirements: 2.8, 2.9, 5.5, 7.7_

- [x] 2. Tokenizer inline tangguh (R2)
  - [x] 2.1 Implementasi `tokenize_inline` murni dan model token
    - Tambah `TokenKind` (TEXT/CODE/LINK) dan dataclass `InlineToken` di `scratch/merge_draft_to_docx.py`
    - Implementasi pemindaian kiri→kanan untuk `**`, `*`, `***`, `\*`, `` `code` ``, `[teks](url)` dengan rekonsiliasi penanda tak seimbang (pass dua: penanda yatim → literal, tanpa kebocoran state)
    - Fungsi murni & deterministik (tidak menyentuh lxml)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

  - [x]* 2.2 Uji properti kebenaran format token inline
    - **Feature: writing-pipeline-improvements, Property 6: Kebenaran format token inline**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.5, 2.6**
    - Hypothesis ≥100 iterasi

  - [x]* 2.3 Uji properti escape literal dan tanpa kebocoran state
    - **Feature: writing-pipeline-improvements, Property 7: Escape literal dan tanpa kebocoran state**
    - **Validates: Requirements 2.4, 2.7**
    - Hypothesis ≥100 iterasi

  - [x] 2.4 Implementasi `emit_runs` dan `RelManager`
    - `emit_runs` menempel `w:r` baseline (rFonts Times New Roman, sz/szCs 24, `w:b/bCs`, `w:i/iCs`) untuk TEXT; Consolas untuk CODE; `w:hyperlink` untuk LINK
    - `RelManager.add_external(url)` mengalokasikan `rId` (dedup URL identik) dan `write()` mempertahankan relationship lama secara aditif
    - _Requirements: 2.5, 2.6_

  - [x]* 2.5 Uji properti preservasi tokenizer terhadap oracle baseline
    - **Feature: writing-pipeline-improvements, Property 8: Preservasi tokenizer terhadap baseline**
    - **Validates: Requirements 2.8, 2.9**
    - Bandingkan `emit_runs(tokenize_inline(text))` byte-per-byte dengan oracle `add_formatted_text` lama (Task 1.2) untuk teks tanpa Konstruk_Inline baru; Hypothesis ≥100 iterasi

  - [x] 2.6 Integrasi wrapper `add_formatted_text` dan rels hyperlink di `merge_draft_to_xml`
    - `add_formatted_text(p_elem, text, default_rPr=None, rel_manager=None)` = `emit_runs(p_elem, tokenize_inline(text), ...)`, tanda tangan lama dipertahankan
    - Sambungkan `RelManager.write()` ke `word/_rels/document.xml.rels` dalam `merge_draft_to_xml`
    - _Requirements: 2.6, 7.4_

- [x] 3. Checkpoint
  - Pastikan seluruh uji lulus, tanyakan pengguna bila ada pertanyaan.

- [x] 4. Daftar Pustaka dinamis bersumber Draf (R1)
  - [x] 4.1 Implementasi parser entri referensi murni
    - Tambah dataclass `ReferenceEntry` dan fungsi `parse_bibliography_entries`, `parse_italic_spans` (reuse jalur italic `tokenize_inline`), `reference_key` di `scratch/merge_draft_to_docx.py`
    - `parse_bibliography_entries` mengembalikan `[]` + `section_found=False` bila `# DAFTAR PUSTAKA` tidak ada
    - _Requirements: 1.1, 1.2, 1.4, 1.8_

  - [x]* 4.2 Uji properti jumlah dan urutan entri referensi
    - **Feature: writing-pipeline-improvements, Property 1: Parsing entri referensi mempertahankan jumlah dan urutan**
    - **Validates: Requirements 1.1, 1.4**
    - Hypothesis ≥100 iterasi

  - [x]* 4.3 Uji properti fidelity Rentang_Miring (round-trip span)
    - **Feature: writing-pipeline-improvements, Property 2: Fidelity Rentang_Miring (round-trip span)**
    - **Validates: Requirements 1.2**
    - Hypothesis ≥100 iterasi

  - [x] 4.4 Refaktor `clean_bibliography_sdt` menjadi bersumber Draf (Option B)
    - Ubah `clean_bibliography_sdt(sdt_elem, entries=None, draft_path="Tugas_Akhir_Draft.md")` agar membaca Entri_Referensi dari Draf via `parse_bibliography_entries` alih-alih `refs_data` hardcoded
    - Render pPr IDENTIK baseline (pStyle Normal; ind left=567 hanging=567; spacing before=0 after=120 line=240 lineRule=auto; jc=both); runs dari `parse_italic_spans` (miring → `w:i/iCs`); urutan = urutan Draf
    - Bila tak ada entri: cetak satu `[WARN]` "sumber Daftar_Pustaka tidak ditemukan" dan jangan tulis entri palsu
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.8, 1.9, 7.3, 7.4_

  - [x]* 4.5 Uji properti invarian gaya paragraf bibliografi
    - **Feature: writing-pipeline-improvements, Property 3: Invarian gaya paragraf bibliografi**
    - **Validates: Requirements 1.3, 1.9**
    - Hypothesis ≥100 iterasi

  - [x]* 4.6 Uji unit kasus batas bibliografi
    - Uji R1.8 (bagian referensi hilang → warning, tanpa entri palsu) dan R1.9 (snapshot 8 entri Draf vs `tests/fixtures/baseline_bibliography.xml`)
    - _Requirements: 1.8, 1.9_

- [x] 5. Penjenjangan daftar oleh indentasi (R3)
  - [x] 5.1 Implementasi `compute_list_level` dan integrasi ke `parse_markdown`
    - Tambah `LIST_INDENT_UNIT` dan `compute_list_level(indent_spaces, marker)` (level dari indentasi; marker kosmetik; indent 0 → level terluar) dengan mode kompatibilitas baseline
    - `parse_markdown` menetapkan `level` `list_item` dari indentasi awal baris
    - _Requirements: 3.1, 3.2, 3.3, 3.5_

  - [x]* 5.2 Uji properti level daftar monoton dan invarian terhadap penanda
    - **Feature: writing-pipeline-improvements, Property 9: Level daftar monoton dan invarian terhadap penanda**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.5**
    - Hypothesis ≥100 iterasi

  - [x]* 5.3 Uji unit kompatibilitas mundur level daftar
    - Tegaskan `left`/`hanging` dxa untuk tiap `list_item` Draf saat ini sama dengan `tests/fixtures/baseline_list_levels.json`
    - _Requirements: 3.4, 3.5_

- [x] 6. Checkpoint
  - Pastikan seluruh uji lulus, tanyakan pengguna bila ada pertanyaan.

- [x] 7. Tabel pipa standar + perataan kolom, opt-in (R5)
  - [x] 7.1 Implementasi parser Tabel_Pipa murni
    - Tambah enum `Alignment` dan fungsi `is_pipe_table_separator`, `parse_alignment_row`, `detect_pipe_table` di `scratch/merge_draft_to_docx.py`
    - `detect_pipe_table` mengembalikan `(end_idx, item)` dengan `lines` data (tanpa separator), `alignments`, `is_pipe=True`
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 7.2 Perluas `build_table_element` untuk perataan kolom
    - Bila `item.get('alignments')` ada, terapkan `w:jc` per sel sesuai kolom; baris pertama tetap `tblHeader` + bold; tanpa `alignments` (jalur `[TABLE]`) perilaku identik baseline
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [x]* 7.3 Uji properti struktur dan perataan Tabel_Pipa
    - **Feature: writing-pipeline-improvements, Property 10: Struktur dan perataan Tabel_Pipa**
    - **Validates: Requirements 5.1, 5.2, 5.3**
    - Hypothesis ≥100 iterasi

  - [x]* 7.4 Uji properti ekuivalensi Tabel_Kurung terhadap oracle baseline
    - **Feature: writing-pipeline-improvements, Property 11: Ekuivalensi Tabel_Kurung terhadap baseline**
    - **Validates: Requirements 5.4, 5.5**
    - Bandingkan `build_table_element` (tanpa `alignments`) byte-per-byte dengan oracle lama (Task 1.2); Hypothesis ≥100 iterasi

  - [x] 7.5 Integrasi `detect_pipe_table` ke `parse_markdown` (Opt_In_By_Content)
    - Deteksi Tabel_Pipa hanya bila Draf memuat baris `|` + Baris_Pemisah valid; pertahankan jalur `[TABLE]` tanpa perubahan
    - _Requirements: 5.1, 5.3, 5.4, 5.6, 7.7_

- [x] 8. Penjaga penulisan non-fatal pada validator (R6 + cross-check R1)
  - [x] 8.1 Implementasi kolektor guard murni di Mesin_Merge
    - Tambah `collect_heading_level_warnings`, `collect_bab_order_warnings`, `collect_unclosed_table_warnings`, `collect_unbalanced_emphasis_warnings`, `collect_citation_crosscheck_warnings(body_text, entries, *, fatal=False)` di `scratch/merge_draft_to_docx.py`
    - Cross-check dua arah mengembalikan `(warnings, has_fatal)`
    - _Requirements: 6.1, 6.2, 6.4, 6.5, 1.5, 1.6, 6.3_

  - [x]* 8.2 Uji properti guard lompatan level heading
    - **Feature: writing-pipeline-improvements, Property 12: Guard lompatan level heading**
    - **Validates: Requirements 6.1**
    - Hypothesis ≥100 iterasi

  - [x]* 8.3 Uji properti guard urutan BAB
    - **Feature: writing-pipeline-improvements, Property 13: Guard urutan BAB**
    - **Validates: Requirements 6.2**
    - Hypothesis ≥100 iterasi

  - [x]* 8.4 Uji properti guard blok [TABLE] tak tertutup
    - **Feature: writing-pipeline-improvements, Property 14: Guard blok [TABLE] tak tertutup**
    - **Validates: Requirements 6.4**
    - Hypothesis ≥100 iterasi

  - [x]* 8.5 Uji properti guard emphasis tak seimbang
    - **Feature: writing-pipeline-improvements, Property 15: Guard emphasis tak seimbang**
    - **Validates: Requirements 6.5**
    - Hypothesis ≥100 iterasi

  - [x]* 8.6 Uji properti pemeriksaan silang sitasi → Daftar_Pustaka
    - **Feature: writing-pipeline-improvements, Property 4: Kelengkapan pemeriksaan silang sitasi → Daftar_Pustaka**
    - **Validates: Requirements 1.5, 6.3**
    - Hypothesis ≥100 iterasi

  - [x]* 8.7 Uji properti pemeriksaan silang Daftar_Pustaka → sitasi
    - **Feature: writing-pipeline-improvements, Property 5: Kelengkapan pemeriksaan silang Daftar_Pustaka → sitasi**
    - **Validates: Requirements 1.6, 6.3**
    - Hypothesis ≥100 iterasi

  - [x] 8.8 Sambungkan guard ke `validate_docx_structure.py` dan sinkronkan KEDUA salinan
    - Tambah pemanggilan kolektor + cetak `[WARN]` non-fatal secara aditif; mode fatal cross-check via `TA_CITATION_FATAL=1`/flag menambah ke `errors_found` (R1.7)
    - Terapkan perubahan IDENTIK pada `scratch/validate_docx_structure.py` dan `skills/scripts/validate_docx_structure.py` (atau faktor ke fungsi murni bersama) agar tidak divergen; semantik check lama tidak diubah
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 1.5, 1.6, 1.7, 7.4_

  - [x]* 8.9 Uji unit mode fatal cross-check
    - Tegaskan `TA_CITATION_FATAL=1` mengubah ketidakcocokan menjadi temuan fatal; default tetap non-fatal
    - _Requirements: 1.7_

- [x] 9. Checkpoint
  - Pastikan seluruh uji lulus, tanyakan pengguna bila ada pertanyaan.

- [x] 10. Penomoran daftar terurut Word, opsional (R4)
  - [x] 10.1 Tambah cabang `numPr` opt-in di `build_p_element`
    - Bila penomoran Word diaktifkan, render item daftar terurut via `numPr`; default tetap penanda tekstual literal identik baseline
    - _Requirements: 4.1, 4.2, 4.3_

  - [x]* 10.2 Uji unit jalur numPr opt-in
    - Uji R4.1 (numPr aktif), R4.2/R4.3 (nonaktif → identik baseline)
    - _Requirements: 4.1, 4.2, 4.3_

- [x] 11. Build end-to-end + verifikasi kompatibilitas mundur
  - [x]* 11.1 Uji properti preservasi lintas-area Opt_In_By_Content (tingkat dokumen)
    - **Feature: writing-pipeline-improvements, Property 16: Preservasi lintas-area Opt_In_By_Content (tingkat dokumen)**
    - **Validates: Requirements 5.6, 7.7**
    - Generate Draf sintetis hanya konstruk lama, bandingkan keluaran pipeline baru byte-per-byte dengan jalur baseline; Hypothesis ≥100 iterasi

  - [x]* 11.2 Uji integrasi build Draf saat ini → nol fatal
    - Bangun docx dari `Tugas_Akhir_Draft.md` saat ini, jalankan `validate_docx_structure.py`, tegaskan nol temuan fatal dan nomor kapsi sama dengan `baseline_caption_numbers.json`
    - _Requirements: 6.7, 7.1, 7.2_

  - [x]* 11.3 Uji integrasi regresi spec lain tetap hijau
    - Jalankan ulang suite `dynamic-generation-pipeline` dan `image-injection-pipeline-fix` di `tests/`, tegaskan tetap lulus
    - _Requirements: 7.5, 7.6_

  - [x]* 11.4 Jalankan pytest penuh sebagai gerbang regresi akhir
    - Pastikan seluruh `tests/` hijau setelah seluruh perubahan
    - _Requirements: 7.5_

- [x] 12. Checkpoint akhir
  - Pastikan seluruh uji lulus, tanyakan pengguna bila ada pertanyaan.

## Notes

- Tugas berpostfiks `*` bersifat opsional (uji unit/properti/integrasi) dan dapat dilewati untuk MVP lebih cepat.
- Tugas 1.1/1.2 adalah jaring pengaman preservasi dan WAJIB dikerjakan lebih dulu sebelum refaktor apa pun.
- Validator memiliki DUA salinan (`scratch/` + `skills/scripts/`); Task 8.8 menjaga keduanya sinkron.
- Setiap uji properti diberi tag komentar `# Feature: writing-pipeline-improvements, Property {n}: ...` dan dijalankan ≥100 iterasi Hypothesis.
- Properti 8, 11, dan 16 adalah uji preservasi berbasis oracle/baseline byte-per-byte.
- Semua kemampuan baru bersifat Opt_In_By_Content; dokumen tanpa sintaks pemicu tidak berubah.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] },
    { "id": 1, "tasks": ["2.1"] },
    { "id": 2, "tasks": ["2.4", "2.2", "2.3"] },
    { "id": 3, "tasks": ["2.6", "2.5"] },
    { "id": 4, "tasks": ["4.1"] },
    { "id": 5, "tasks": ["5.1", "4.2", "4.3"] },
    { "id": 6, "tasks": ["7.1", "4.4", "5.2", "5.3"] },
    { "id": 7, "tasks": ["7.2", "4.5", "4.6"] },
    { "id": 8, "tasks": ["7.5", "7.3", "7.4"] },
    { "id": 9, "tasks": ["8.1"] },
    { "id": 10, "tasks": ["10.1", "8.2", "8.3", "8.4", "8.5", "8.6", "8.7"] },
    { "id": 11, "tasks": ["8.8"] },
    { "id": 12, "tasks": ["10.2", "8.9"] },
    { "id": 13, "tasks": ["11.1", "11.2", "11.3", "11.4"] }
  ]
}
```
