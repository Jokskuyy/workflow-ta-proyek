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
- Pada keluaran akhir, label dan nomor caption lengkap (`Gambar X.Y` atau `Tabel X.Y`) memakai Times New Roman 12 pt tebal. Deskripsi caption tetap regular; hanya istilah asing yang terdaftar dan benar-benar diperlukan yang dicetak miring.
- Field `REF` pada narasi harus regular meskipun merujuk caption yang label dan nomornya tebal.
- Pada DOCX final, drawing wajib tepat sebelum caption dan pasangan gambar-caption harus berada pada halaman yang sama. Pipeline memindahkan pasangan tersebut bersama ke halaman berikutnya bila ruang tersisa tidak cukup.

## Sub-bab Teori
- Setiap sub-bab teori (UAT, Black Box, ERD, NavMesh, dll.) diawali **paragraf definisi** dengan **minimal satu sitasi** formal.

## Konsistensi Istilah
- Pertahankan satu istilah konsisten (mis. "database", bukan berganti "basis data"; "antarmuka" vs "user interface" — pilih satu).
- Istilah teknis asing yang tercantum pada `term_registry.json` dirender *italic*. Identifier atau perintah teknis ditulis dengan backtick; pipeline tetap merendernya *italic* memakai Times New Roman.
- Untuk memperkenalkan singkatan dari istilah asing, tulis kepanjangannya dalam huruf miring dan singkatannya dalam huruf regular, misalnya *User Acceptance Test* (UAT). Penyebutan berikutnya cukup menggunakan singkatan UAT.
- Narasi bahasa Indonesia menggunakan `Dashboard Publik`, `Panel Admin`, `pemangku kepentingan`, `database`, `smartphone`, `browser`, `deployment`, `hosting`, `cache aset`, `file hasil build`, `kode lokasi Unity`, dan `notifikasi kedatangan`. Jangan mencampurkannya dengan Dasbor Publik, Public Dashboard, Admin Panel, stakeholder, basis data, perangkat bergerak, peramban, publikasi aplikasi, penyimpanan sementara aset, artefak build, kode objek, atau pemberitahuan penyelesaian navigasi.
- Parenthetical tidak digunakan hanya untuk mengulang terjemahan, misalnya `Aksesibilitas (Accessibility)` atau `Dashboard Publik (Public Dashboard)`. Parenthetical tetap digunakan untuk singkatan dan identifier teknis yang perlu diperkenalkan.
- Gunakan `frontend` untuk lapisan implementasi React dan `antarmuka` untuk tampilan yang digunakan pengguna. Gunakan `backend` untuk implementasi layanan dan `server` untuk lingkungan yang menjalankannya.
- Gunakan `sistem`, `sistem denah virtual`, atau `sistem yang dikembangkan` untuk menyebut produk yang dihasilkan. `Prototyping` digunakan sebagai nama metode, sedangkan `prototipe` atau `purwarupa` hanya digunakan ketika menjelaskan definisi dan tahapan iteratif metode tersebut, bukan sebagai sebutan produk akhir.

## Fakta & Angka (anti-mengarang)
- Verifikasi ke `project_facts.json`. Bila status pengujian `completed: false`/`null`, tulis placeholder `[TBD: ...]` — **jangan** menyalin angka dari laporan/skripsi lain.

## Lampiran
- Penomoran `LAMPIRAN 1.`, `LAMPIRAN 2.`, dst.
- Tiap lampiran diawali halaman baru (pemisah `---` di Markdown).
- Lampiran tidak muncul di Daftar Isi; Daftar Lampiran diletakkan setelah Daftar Tabel.

## Penomoran Gambar
- Penulis tidak menentukan nomor. Pipeline mengikuti urutan kemunculan (reading order), memakai counter terpisah untuk gambar/tabel, dan me-reset counter pada setiap BAB melalui field Word `SEQ`.
- Setiap gambar wajib memiliki minimal satu `[FIGREF:<id>]` pada paragraf narasi biasa di BAB yang sama; token tidak boleh mengawali kalimat.
- Kalimat penjelasan biasa tidak memakai bold manual. Penebalan dibatasi pada heading, header tabel, label dan nomor caption, serta bagian lain yang diwajibkan template.
- Blok kode memakai Courier New 12 pt miring, rata kiri, spasi tunggal, tanpa warna sintaks, latar, bingkai, atau nomor baris. Font isi laporan lainnya tetap Times New Roman.
