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
- Jangan menaruh "Gambar x.y"/"Tabel x.y" di **awal** kalimat/paragraf.
- Sebut di tengah kalimat, mis. "...seperti pada Gambar 2.9." / "Peran tim dirinci pada Tabel 1.1.".

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
- Ikuti urutan kemunculan (reading order), konsisten dengan DAFTAR GAMBAR (saat ini Gambar 2.1–2.29 untuk BAB II, 3.1–3.2 untuk BAB III).
