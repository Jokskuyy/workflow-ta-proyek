# Implementation Plan: Dynamic Generation Pipeline

## Overview

Rencana ini merombak tahap GENERASI yang sudah berjalan menjadi sepenuhnya dinamis terhadap
isi `Tugas_Akhir_Draft.md`, dengan menghapus seluruh hardcoding pada dua skrip generasi:
`skills/scripts/format_ta_proyek.py` (Mesin_Format) dan `scratch/merge_draft_to_docx.py`
(Mesin_Merge). Karena ini adalah refactor pipeline yang sudah benar, langkah pertama
menangkap baseline Dokumen_Referensi agar kompatibilitas mundur (R8, Property 17) dapat
diperiksa setelah perubahan.

Pendekatan: ekstrak logika inti menjadi fungsi murni yang dapat diuji (parse bab, registri
kapsi, normalisasi/pencocokan asosiasi, deteksi seksi, rewriter referensi, resolve path),
uji setiap fungsi dengan property-based test (Hypothesis, ≥100 iterasi), lalu integrasikan
ke `format_document_xmls` (3 fase) dan `merge_draft_to_xml`, sinkronkan salinan scratch/skills,
dan tutup dengan build penuh + `pytest`.

Catatan operasional: pipeline menjalankan salinan **scratch** untuk merge/validate dan salinan
**skills/scripts** untuk format. Setiap perubahan pada skrip sumber harus disinkronkan ke
salinan yang relevan (lihat tugas 11). Bahasa implementasi: **Python**. Semua test baru
ditempatkan di bawah `tests/`.

## Tasks

- [x] 1. Tangkap baseline & siapkan guard kompatibilitas mundur
  - [x] 1.1 Buat skrip penangkap baseline Dokumen_Referensi
    - Buat `scratch/capture_reference_baseline.py` yang menjalankan pipeline atas draf saat ini
      (kondisi sebelum refactor), lalu menyimpan: (a) himpunan nomor kapsi Gambar/Tabel ke
      `tests/fixtures/reference_caption_numbers.json`, (b) ringkasan keluaran `validate_docx_structure.py`
      ke `tests/fixtures/reference_validator_summary.json`, dan (c) salinan docx hasil ke
      `tests/fixtures/Dokumen_Referensi.docx`
    - Fungsi pengumpul nomor kapsi harus murni (menerima daftar paragraf/teks, mengembalikan
      `set[str]`) agar dapat dipakai ulang oleh test Property 17
    - Semua path relatif terhadap akar ruang kerja; tidak ada path absolut
    - _Requirements: 8.1, 8.2, 8.4_

- [x] 2. Helper deteksi bab & registri penomoran kapsi (Mesin_Format)
  - [x] 2.1 Implementasi `parse_chapter_number`
    - Tambahkan fungsi murni `parse_chapter_number(heading_text) -> int | None` di
      `skills/scripts/format_ta_proyek.py`
    - Cocokkan pola `^BAB\s+([IVX]+|[0-9]+)\b` case-insensitive dengan spasi ternormalisasi;
      angka romawi via tabel `ROMAN`, angka arab via `int()`; kembalikan `None` bila bukan heading BAB
    - _Requirements: 1.1, 2.1, 5.1_

  - [x]* 2.2 Tulis property test untuk penetapan Nomor_Bab dari BAB pembungkus
    - **Property 1: Penetapan Nomor_Bab dari BAB pembungkus**
    - **Validates: Requirements 1.1, 2.1**
    - Tag: `# Feature: dynamic-generation-pipeline, Property 1: ...`; ≥100 iterasi; dokumen
      sintetis dengan urutan heading BAB & kapsi arbitrer di `tests/test_caption_registry_properties.py`

  - [x] 2.3 Implementasi `CaptionRegistry`
    - Tambahkan kelas `CaptionRegistry` dengan `next_figure(chapter, old_number)` dan
      `next_table(chapter, old_number)` mengembalikan `(nomor_baru "C.k", default_val=k, is_first_in_chapter)`
    - Pelihara penghitung per-bab (`_fig_seq`, `_tbl_seq`), peta `fig_remap`/`tbl_remap`
      (rekam `old_number -> nomor_baru`, tandai AMBIGUOUS bila satu old_number → >1 baru),
      dan himpunan final `fig_numbers`/`tbl_numbers`
    - Reset urutan ke 1 pada bab baru; berlaku seragam untuk SEMUA bab tanpa asumsi nomor bab
    - _Requirements: 1.2, 1.3, 1.6, 2.2, 2.5, 6.3_

  - [x]* 2.4 Tulis property test penomoran per-bab berurutan
    - **Property 2: Penomoran per-bab berurutan untuk gambar dan tabel**
    - **Validates: Requirements 1.2, 1.3, 1.6, 2.2, 2.5**
    - Tag Property 2; ≥100 iterasi; sertakan himpunan bab yang melompat (mis. {1, 2, 5})

  - [x]* 2.5 Tulis property test opsi restart SEQ pada kapsi pertama bab
    - **Property 3: Opsi restart SEQ muncul tepat pada kapsi pertama tiap bab**
    - **Validates: Requirements 1.4, 1.5, 2.3, 2.4**
    - Tag Property 3; ≥100 iterasi; verifikasi `is_first_in_chapter`/`default_val==1` iff kapsi pertama

  - [x]* 2.6 Tulis property test fallback Nomor_Bab tanpa berhenti
    - **Property 4: Fallback Nomor_Bab tanpa berhenti**
    - **Validates: Requirements 1.7, 2.6**
    - Tag Property 4; ≥100 iterasi; kapsi sebelum BAB pertama → pakai Nomor_Bab terakhir/1, tepat satu peringatan

- [x] 3. Helper deskripsi kapsi dari draf & Aturan_Umum gambar tanpa kapsi (Mesin_Format)
  - [x] 3.1 Implementasi ekstraksi Deskripsi_Kapsi verbatim + aturan gambar tanpa kapsi
    - Tambahkan helper yang mem-parse teks kapsi draf dengan regex
      `^(Gambar|Tabel)\s+([0-9]+(?:\.[0-9]+)*)\.?\s*(.*)$`, mengembalikan `(old_number, desc)`
      dengan `desc` verbatim
    - Hapus daftar literal `survey_captions` serta pemicu judul-seksi bernama
      ("Analisis Sistem yang Sedang Berjalan", "Integrasi Backend dengan Unity")
    - Tetapkan satu Aturan_Umum: gambar tanpa baris kapsi di draf TIDAK dibuatkan kapsi maupun nomor
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x]* 3.2 Tulis property test deskripsi kapsi verbatim
    - **Property 5: Deskripsi kapsi verbatim dari draf**
    - **Validates: Requirements 3.1, 3.5**
    - Tag Property 5; ≥100 iterasi; teks deskripsi unicode/tanda baca arbitrer muncul verbatim di keluaran

  - [x]* 3.3 Tulis property test gambar tanpa kapsi tidak diberi kapsi/nomor
    - **Property 6: Gambar tanpa kapsi tidak memperoleh kapsi maupun nomor**
    - **Validates: Requirements 3.3**
    - Tag Property 6; ≥100 iterasi; campuran gambar berkapsi/tanpa kapsi → jumlah kapsi keluaran = jumlah baris kapsi draf

  - [x]* 3.4 Tulis property test tidak ada teks kapsi non-draf
    - **Property 7: Tidak ada teks kapsi yang tidak bersumber dari draf**
    - **Validates: Requirements 3.2, 3.4**
    - Tag Property 7; ≥100 iterasi; teks yang tak ada di draf tak pernah muncul di keluaran

- [x] 4. Helper deteksi seksi & heading dinamis (Mesin_Format)
  - [x] 4.1 Implementasi `find_front_matter_boundary` dan `find_heading`
    - Tambahkan `find_front_matter_boundary(children, ns)` (indeks Heading1 BAB I pertama,
      teks memuat "PENDAHULUAN"/"BAB I"; fallback struktural + 1 peringatan bila tak ada) dan
      `find_heading(children, ns, *, style=None, text_contains=None)` (pemindaian awal→akhir,
      cocokkan pStyle + teks case-insensitive/trim, kembalikan -1 bila tak ada)
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x]* 4.2 Tulis property test deteksi heading/seksi invarian
    - **Property 11: Deteksi heading/seksi invarian terhadap kapitalisasi dan spasi**
    - **Validates: Requirements 5.1, 5.2, 5.4**
    - Tag Property 11; ≥100 iterasi; heading di indeks arbitrer, transformasi kapitalisasi/spasi tak mengubah hasil

  - [x]* 4.3 Tulis property test fallback deteksi seksi terstruktur
    - **Property 12: Fallback deteksi seksi terstruktur**
    - **Validates: Requirements 5.3, 5.5**
    - Tag Property 12; ≥100 iterasi; dokumen tanpa target/BAB I → fallback terstruktur + tepat satu peringatan

- [x] 5. Helper reference rewriter dari registri (Mesin_Format)
  - [x] 5.1 Implementasi derivasi remap + `rewrite_references`
    - Tambahkan `rewrite_references(text, fig_remap, tbl_remap) -> (text, warnings)` yang
      memetakan semua "Gambar X.Y"/"Tabel X.Y" memakai peta yang DITURUNKAN dari `CaptionRegistry`
    - Aturan per kemunculan: padanan unik → ganti (semua kemunculan, termasuk berulang);
      tanpa padanan → pertahankan + peringatan; ambigu (AMBIGUOUS) → pertahankan + peringatan kandidat
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x]* 5.2 Tulis property test renumbering konsisten dengan kapsi
    - **Property 13: Renumbering referensi konsisten dengan kapsi yang ada**
    - **Validates: Requirements 6.1, 6.3**
    - Tag Property 13; ≥100 iterasi; mention berulang nomor lama yang sama semuanya terganti & menunjuk nomor yang ada

  - [x]* 5.3 Tulis property test referensi tak berpadanan dipertahankan
    - **Property 14: Referensi tak berpadanan dipertahankan dengan peringatan**
    - **Validates: Requirements 6.4**
    - Tag Property 14; ≥100 iterasi; nomor tanpa kapsi padanan → teks asli utuh + peringatan menyebut teks & nomor

  - [x]* 5.4 Tulis property test referensi ambigu dipertahankan
    - **Property 15: Referensi ambigu dipertahankan dengan peringatan kandidat**
    - **Validates: Requirements 6.5**
    - Tag Property 15; ≥100 iterasi; old_number → >1 kandidat → teks asli utuh + peringatan daftar kandidat

- [x] 6. Checkpoint - Pastikan helper Mesin_Format lulus uji
  - Pastikan semua test lulus, tanyakan ke pengguna bila ada pertanyaan.

- [x] 7. Integrasikan tiga fase ke `format_document_xmls`
  - [x] 7.1 Fase 0 — deteksi struktur dinamis
    - Ganti `bab1_idx_orig = 60` dan `section1_last_p_idx = 60` dengan
      `find_front_matter_boundary(...)` dan `section1_last_p_idx = bab1_idx - 1`, dengan fallback
      struktural; tidak ada indeks numerik tetap
    - _Requirements: 5.2, 5.3, 5.4, 5.5_

  - [x] 7.2 Fase 1 — chapter-aware caption pass tunggal
    - Telusuri body urutan baca sekali: lacak `current_chapter` via `parse_chapter_number`,
      panggil `CaptionRegistry.next_figure/next_table`, dan panggil `format_caption_paragraph_clean`
      apa adanya dengan `prefix=f"{chapter}."` dan `default_val=k`
    - Hapus penghitung `gambar_idx` paksa "2.", `gambar_seq_by_chap` parsial, dan cabang
      `if src_chap >= 3 ... else`; pakai deskripsi verbatim dari draf (tugas 3.1) dan bangun
      registri nomor lama→baru
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 2.2, 2.3, 2.4, 2.5, 2.6, 3.1, 3.3_

  - [x] 7.3 Fase 2 — terapkan reference rewriter
    - Ganti `ref_repl()` dan stub `replace_mentions_in_paragraph()` dengan `rewrite_references`
      memakai `fig_remap`/`tbl_remap` dari registri Fase 1; teruskan peringatan ke stdout/stderr
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x]* 7.4 Tulis unit/integration test untuk `format_document_xmls`
    - Uji integrasi tiga fase atas document.xml sintetis kecil: penomoran per-bab, restart SEQ,
      deskripsi verbatim, dan referensi terupdate
    - Edge case: tidak ada BAB I (fallback front matter), seksi bernama lama tidak memicu kapsi (R3.4)
    - _Requirements: 1.6, 2.5, 3.4, 5.5, 6.1_

- [x] 8. Helper pencocokan asosiasi Gambar_Template (Mesin_Merge)
  - [x] 8.1 Implementasi `normalize_assoc_text`, `is_caption_text`, `find_template_matches`
    - Tambahkan di `scratch/merge_draft_to_docx.py`: `normalize_assoc_text(t)` (lowercase, buang
      prefix "gambar|tabel|lampiran <num>", buang non-alfanumerik, ringkas spasi),
      `is_caption_text(t)`, dan `find_template_matches(assoc_text, candidates)` yang mengembalikan
      daftar indeks cocok dengan aturan sejenis + substring ternormalisasi
    - Pertahankan penjagaan struktural umum (tolak paragraf < 15 char & teks mirip-kode);
      JANGAN tambahkan kasus khusus nama berkas/istilah
    - _Requirements: 4.1, 4.2, 4.5_

  - [x]* 8.2 Tulis property test invarian pencocokan asosiasi
    - **Property 8: Pencocokan asosiasi invarian terhadap kapitalisasi, spasi, dan nama berkas**
    - **Validates: Requirements 4.1, 4.2**
    - Tag Property 8; ≥100 iterasi; transformasi kapitalisasi/spasi & penggantian `target_img` tak mengubah keputusan
    - Tempatkan di `tests/test_merge_matching_properties.py`

  - [x]* 8.3 Tulis property test pencocokan hanya antar sejenis
    - **Property 9: Pencocokan hanya antar paragraf sejenis**
    - **Validates: Requirements 4.5**
    - Tag Property 9; ≥100 iterasi; pasangan beda jenis (kapsi vs narasi) tak pernah cocok

  - [x]* 8.4 Tulis property test tie-break kecocokan ganda
    - **Property 10: Tie-break kecocokan ganda memilih urutan dokumen pertama**
    - **Validates: Requirements 4.4**
    - Tag Property 10; ≥100 iterasi; >1 kandidat → indeks terkecil terpilih + satu peringatan

- [x] 9. Konfigurasi path Mesin_Merge tanpa nilai absolut
  - [x] 9.1 Implementasi `resolve_path` + pembacaan konfigurasi + `main(argv)`
    - Tambahkan `resolve_path(p, workspace_root)` dan susun `main()` dengan prioritas
      argv > konfigurasi > default relatif; `workspace_root = Path(__file__).resolve().parents[1]`
    - Hapus path absolut; validasi pra-tulis: draf wajib terbaca, direktori xml keluaran wajib ada
      (berhenti sebelum menulis bila gagal)
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [x]* 9.2 Tulis property test resolusi path
    - **Property 16: Resolusi path relatif terhadap akar ruang kerja**
    - **Validates: Requirements 7.2, 7.3**
    - Tag Property 16; ≥100 iterasi; path absolut dikembalikan apa adanya, path relatif → `workspace_root / path`

  - [x]* 9.3 Tulis unit test prioritas & guard path
    - Uji prioritas argv > konfigurasi (R7.1); berhenti tanpa menulis saat draf hilang/tak terbaca (R7.4);
      berhenti saat direktori keluaran tak ada (R7.5)
    - _Requirements: 7.1, 7.4, 7.5_

- [x] 10. Integrasikan kebijakan pencocokan ke `merge_draft_to_xml`
  - [x] 10.1 Terapkan Aturan_Umum + tie-break + logging pada alur merge
    - Ganti logika "pertama cocok lalu break" dengan "kumpulkan kandidat via `find_template_matches`
      lalu terapkan kebijakan": 0 cocok → log unmatched (assoc_text + target_img) & lanjut;
      >1 → pilih indeks terkecil + peringatan; 1 → inject
    - Hapus blok `target_img`/"image20"/"modaltambahdatagedung" dan trik "Dosen"→"Gedung";
      tambahkan field `is_caption` pada `drawings_map`
    - _Requirements: 4.2, 4.3, 4.4, 4.5_

  - [x]* 10.2 Tulis integration test asosiasi merge
    - Uji `merge_draft_to_xml` atas XML sintetis: unmatched dicatat & lanjut, kecocokan ganda → pertama,
      tanpa kasus khusus bernama
    - _Requirements: 4.3, 4.4_

- [x] 11. Sinkronkan salinan scratch/skills
  - [x] 11.1 Sinkronkan skrip yang diubah ke salinan yang dijalankan pipeline
    - Pastikan salinan format yang dipakai pipeline (`skills/scripts/format_ta_proyek.py`) dan salinan
      merge/validate yang dipakai pipeline (`scratch/merge_draft_to_docx.py`) konsisten dengan hasil
      tugas 7 & 10; sinkronkan setiap salinan duplikat yang relevan di scratch/skills
    - Verifikasi dengan diff bahwa fungsi/perilaku salinan identik (hanya path lokasi yang berbeda)
    - _Requirements: 9.4_

- [x] 12. Verifikasi kompatibilitas mundur & integrasi penuh
  - [x]* 12.1 Tulis property test nomor kapsi identik dengan Dokumen_Referensi
    - **Property 17: Nomor kapsi draf saat ini identik dengan Dokumen_Referensi**
    - **Validates: Requirements 8.4**
    - Tag Property 17; bandingkan himpunan nomor kapsi keluaran terhadap fixture baseline (tugas 1.1)

  - [x]* 12.2 Tulis integration test pipeline end-to-end + validator
    - Jalankan `build_pipeline.py` atas draf saat ini lalu `validate_docx_structure.py` → 0 kegagalan fatal;
      bandingkan ringkasan validator & gambar terinjeksi terhadap baseline (tanpa kegagalan baru)
    - _Requirements: 8.1, 8.2, 9.1, 9.2_

  - [x]* 12.3 Tulis scope-guard test
    - Pastikan diff perubahan terbatas pada `skills/scripts/format_ta_proyek.py` dan
      `scratch/merge_draft_to_docx.py` (beserta salinan tersinkron); tidak ada perubahan semantik
      pada validator atau skrip injeksi gambar
    - _Requirements: 9.3, 9.4_

  - [x] 12.4 Implementasi kontrol promosi & peringatan beda nomor
    - Lengkapi skrip baseline/compare (tugas 1.1) agar: bila ada kegagalan fatal validator → hentikan
      promosi, catat kegagalan, jangan timpa Dokumen_Referensi; bila nomor kapsi berbeda → catat
      peringatan lama vs baru
    - _Requirements: 8.5, 8.6_

- [x] 13. Checkpoint akhir - Build penuh + pytest
  - Jalankan build pipeline penuh atas draf saat ini lalu `pytest tests/` (gunakan eksekusi sekali jalan,
    bukan watch mode) → exit code 0, 0 gagal, 0 error. Pastikan semua test lulus, tanyakan ke pengguna
    bila ada pertanyaan.

## Notes

- Tugas bertanda `*` bersifat opsional (test) dan dapat dilewati untuk MVP cepat; tugas implementasi inti tidak ditandai opsional.
- Setiap tugas mereferensikan klausa requirement spesifik untuk ketertelusuran.
- Tugas 1.1 (baseline) WAJIB dijalankan sebelum refactor agar kompatibilitas mundur (R8, Property 17) dapat diverifikasi.
- Property test memakai Hypothesis ≥100 iterasi pada fungsi murni dengan dokumen XML sintetis; diberi tag `# Feature: dynamic-generation-pipeline, Property {n}: ...`.
- Checkpoint (tugas 6, 13) memastikan validasi inkremental.
- Tugas 11 menjaga salinan scratch/skills yang dijalankan pipeline tetap sinkron.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["2.1", "8.1"] },
    { "id": 2, "tasks": ["2.3", "9.1", "2.2", "8.2", "8.3", "8.4"] },
    { "id": 3, "tasks": ["3.1", "10.1", "2.4", "2.5", "2.6", "9.2", "9.3"] },
    { "id": 4, "tasks": ["4.1", "10.2", "3.2", "3.3", "3.4"] },
    { "id": 5, "tasks": ["5.1", "4.2", "4.3"] },
    { "id": 6, "tasks": ["7.1", "5.2", "5.3", "5.4"] },
    { "id": 7, "tasks": ["7.2"] },
    { "id": 8, "tasks": ["7.3"] },
    { "id": 9, "tasks": ["7.4", "11.1"] },
    { "id": 10, "tasks": ["12.1", "12.2", "12.3", "12.4"] }
  ]
}
```
