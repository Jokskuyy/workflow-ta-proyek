# Spesifikasi Format Laporan TA Proyek (UPNVJ FIK 2025)

> Sumber kanonik tunggal. Dirujuk oleh `write-ta-proyek` dan `docx-ta-proyek`
> agar tidak terjadi duplikasi/drift. Jangan menyalin ulang tabel ini ke SKILL.md;
> cukup tautkan ke berkas ini.

| Element | Specification |
|---------|---------------|
| **Paper Size** | A4 |
| **Margins** | Top = 3cm, Bottom = 3cm, **Left = 4cm**, Right = 3cm |
| **Font Name** | Times New Roman untuk seluruh teks laporan dan kode inline; pengecualian hanya fenced code block yang memakai Courier New |
| **Font Size** | Body (12pt), Headings (12pt Bold), Chapter Titles (14pt Bold Centered), Abstracts (12pt) |
| **Line Spacing** | Body & Headings (1.15), Captions & Bibliography (1.0) |
| **Technical Terms** | Hanya istilah asing yang diperlukan pada `term_registry.json` dan identifier di dalam backtick yang dirender italic. Pemrosesan istilah tidak boleh memiringkan seluruh run atau seluruh deskripsi caption. |
| **Indentations** | Body (1.0cm first-line indent), Bibliography (1.0cm hanging indent dan rata kiri agar jarak antarkata tetap wajar) |
| **Table Captions** | **Di atas** tabel, center, `Tabel 1.1 Deskripsi` (tanpa titik setelah nomor); label dan nomor 12 pt tebal, deskripsi regular |
| **Figure Captions** | **Di bawah** gambar, center, `Gambar 2.3 Deskripsi` (tanpa titik setelah nomor); label dan nomor 12 pt tebal, deskripsi regular |
| **Code Blocks** | Courier New 12 pt miring, rata kiri, spasi tunggal, tanpa warna sintaks, latar, bingkai, atau nomor baris |
| **Figure Narration** | Setiap gambar wajib dirujuk secara eksplisit sebagai "Gambar X.Y" dalam paragraf narasi biasa pada bab yang sama. Rujukan ditempatkan di tengah kalimat, bukan sebagai kata pertama paragraf/kalimat. Pelanggaran bersifat fatal dan menggagalkan build. |
| **Front Matter Pages** | Romawi (`i, ii, iii...`) di kanan bawah; halaman sampul tidak menampilkan nomor |
| **Body Pages** | Arab (`1, 2, 3...`), restart dari `1` pada BAB I; halaman pembuka setiap BAB di tengah bawah, halaman lanjutan di kanan atas |
| **Identity Footer** | Berlaku mulai BAB I sampai Daftar Pustaka dan berhenti sebelum Lampiran. Baris pertama berisi `Nama Penulis, Tahun` dalam Times New Roman 8 pt tebal. Baris kedua berisi judul utama huruf kapital dalam Times New Roman 8 pt tebal-miring. Dua baris berikutnya berisi identitas `UPN Veteran Jakarta, Fakultas Ilmu Komputer, S1 Informatika` dan `[www.upnvj.ac.id-www.library.upnvj.ac.id-www.repository.upnvj.ac.id]` dalam Times New Roman 8 pt regular. Footer tetap berdampingan dengan aturan nomor halaman body. |
| **In-text Citations** | Author-year tanpa koma sebelum tahun: `(Nama Tahun)`, `(Nama et al. Tahun)`, dan `(Nama 2023; Nama Lain 2024)` |
| **TOC & Bibliography** | Judul center, Heading1 tanpa nomor, font dipaksa Times New Roman |
| **Page Splits** | Daftar Isi, Daftar Gambar, Daftar Tabel di halaman terpisah |
| **Cover Page** | Cover di halaman sendiri, terpisah dari isi |
| **Table of Appendices** | Daftar Lampiran di halaman sendiri setelah Daftar Tabel. Seluruh heading lampiran dikecualikan dari Daftar Isi (gaya paragraf kustom tanpa outline level). |
| **Images & Figures** | Pertahankan rasio aspek asli (tidak distorsi); ukuran menyesuaikan dimensi gambar secara dinamis. Drawing wajib tepat sebelum caption dan keduanya harus berada pada halaman yang sama. Jika ruang halaman tersisa tidak cukup, pasangan gambar-caption dipindahkan bersama ke halaman berikutnya. |
