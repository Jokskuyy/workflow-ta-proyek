---
inclusion: fileMatch
fileMatchPattern: 'Tugas_Akhir_Draft.md'
---

# Aturan Penulisan Draf Laporan TA

Berlaku saat menulis/menyunting `Tugas_Akhir_Draft.md`. Diekstrak dari skill
`write-ta-proyek` agar selalu ditegakkan otomatis. Untuk sitasi, lihat
`aturan-sitasi.md`.

## Format daftar (WAJIB)
- **Dilarang memakai bullet** (`-`, `*`, `+`).
- Hierarki penomoran: Level 1 `1.` → Level 2 `a.` → Level 3 `1)` → Level 4 `a)`.

## Penyebutan Gambar & Tabel
- Jangan menulis nomor `Gambar x.y`/`Tabel x.y` secara statis pada draf baru.
- Rujuk di tengah kalimat dengan `[FIGREF:<id>]` atau `[TABREF:<id>]`, misalnya `...seperti pada [FIGREF:diagram_arsitektur].`.
- Caption sumber memakai `[FIGCAPTION:Deskripsi]` setelah `[FIGURE:<id>]`, atau `[TABLECAPTION:Deskripsi]` setelah `[TABLE-ID:<id>]`. Nomor final dibuat pipeline.
- Pada DOCX final, drawing wajib tepat sebelum caption dan pasangan gambar-caption harus berada pada halaman yang sama. Pipeline memindahkan pasangan tersebut bersama ke halaman berikutnya bila ruang tersisa tidak cukup.

## Sub-bab Teori
- Setiap sub-bab teori (UAT, Black Box, ERD, NavMesh, dll.) diawali **paragraf definisi** dengan **minimal satu sitasi** formal.

## Konsistensi Istilah
- Pertahankan satu istilah konsisten (mis. "database", bukan berganti "basis data"; "antarmuka" vs "user interface" — pilih satu).

## Fakta & Angka (anti-mengarang)
- Verifikasi ke `project_facts.json`. Bila status pengujian `completed: false`/`null`, tulis placeholder `[TBD: ...]` — **jangan** menyalin angka dari laporan/skripsi lain.

## Lampiran
- Penomoran `LAMPIRAN 1.`, `LAMPIRAN 2.`, dst.
- Tiap lampiran diawali halaman baru (pemisah `---` di Markdown).
- Lampiran tidak muncul di Daftar Isi; Daftar Lampiran diletakkan setelah Daftar Tabel.

## Penomoran Gambar
- Penulis tidak menentukan nomor. Pipeline mengikuti urutan kemunculan (reading order), memakai counter terpisah untuk gambar/tabel, dan me-reset counter pada setiap BAB melalui field Word `SEQ`.
- Setiap gambar wajib memiliki minimal satu `[FIGREF:<id>]` pada paragraf narasi biasa di BAB yang sama; token tidak boleh mengawali kalimat.
