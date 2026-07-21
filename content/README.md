# Kontrak Konten Bersama dan Konten Peran

Direktori ini adalah sumber konten yang dapat dikomposisikan ke `Tugas_Akhir_Draft.md` tanpa menyalin paragraf secara manual antarcabang. AI agent harus membaca dokumen ini sebelum mengubah bagian laporan yang ditandai dengan `PIPELINE:INCLUDE`.

## Lapisan konten

| Lokasi | Ownership | Kontrak |
|---|---|---|
| `content/shared/` | Tim | Fakta, narasi, tabel, dan hasil pengujian yang harus identik pada seluruh laporan |
| `content/roles/<role>/` | Pemilik branch | Analisis, implementasi, bukti, dan kontribusi yang khusus terhadap satu peran |
| `Tugas_Akhir_Draft.md` | Pemilik branch | Struktur heading, urutan komposisi, identitas, judul, dan narasi personal |

Konten bersama tidak boleh memuat nama, NIM, tanda tangan, judul personal, atau klaim kontribusi satu anggota. Dokumen bukti mentah yang memuat identitas responden tidak otomatis menjadi konten bersama. Ringkasan anonim yang telah diverifikasi dapat ditempatkan di `content/shared/`.

## Sintaks include

Directive harus berada pada satu baris tersendiri dan path selalu relatif terhadap root repository.

```md
<!-- PIPELINE:INCLUDE content/shared/bab1/latar-belakang-umum.md -->
```

Pipeline memperluas directive di memori. `Tugas_Akhir_Draft.md` dan fragment sumber tidak ditulis ulang saat build. Include yang hilang, absolut, keluar dari repository, bukan Markdown, digunakan dua kali, atau rekursif merupakan kegagalan fatal sebelum `document.xml` diubah.

Fragment yang ditempatkan setelah heading sebaiknya tidak mengulang heading tersebut. Sebagai contoh, file yang dimasukkan setelah `## 1.1 Latar Belakang` hanya berisi paragraf isi. Directive di dalam fenced code block dianggap contoh literal dan tidak dieksekusi.

## Aturan konsistensi tiga laporan

1. Angka Black Box, UAT, fakta proyek, istilah, dan status produk hanya memiliki satu sumber bersama.
2. File peran tidak boleh menyalin ulang angka hasil pengujian. File peran hanya menjelaskan kontribusi terhadap temuan atau perbaikannya.
3. Latar belakang menggunakan konteks proyek bersama, kemudian dilanjutkan narasi fokus peran pada draf atau `content/roles/<role>/`.
4. Solusi aktual boleh berbeda dari redaksi saran UAT jika memecahkan masalah pengguna yang sama. Hubungan tersebut wajib dicatat sebagai masalah, solusi aktual, bukti, status, dan hasil retest.
5. Judul laporan, identitas, rumusan masalah khusus, batasan peran, implementasi, dan kesimpulan kontribusi tidak boleh dipindahkan ke `content/shared/`.
6. Perubahan shared content didistribusikan bersama pipeline dan dokumentasi. Perubahan draf atau role content tetap berada pada branch pemiliknya.

## Validasi tanpa membuat DOCX

Jalankan dari root repository:

```powershell
C:\Python312\python.exe skills/scripts/merge_draft_to_docx.py --check-includes
```

Perintah tersebut hanya memperluas include, mem-parse Markdown, dan memeriksa marker gambar. Perintah tidak mengubah `document.xml` atau menghasilkan DOCX.

## Sumber konten bersama aktif

| Bagian laporan | Fragment kanonik |
|---|---|
| 1.1 konteks umum Latar Belakang | `content/shared/bab1/latar-belakang-umum.md` |
| 2.1 Observasi dan Analisis Kebutuhan Awal | `content/shared/bab2/observasi-dan-analisis-kebutuhan.md` |
| 2.1.1 Sumber Data dan Batas Observasi | `content/shared/bab2/sumber-data-dan-batas-observasi.md` |
| 2.1.2 Analisis Kebutuhan Pengguna dan Sistem yang Berjalan | `content/shared/bab2/analisis-kebutuhan-dan-sistem-berjalan.md` |
| 2.1.3 Hasil Wawancara dan Implikasi Kebutuhan | `content/shared/bab2/wawancara-dan-implikasi-kebutuhan.md` |
| 3.5.1 Black Box Testing | `content/shared/testing/blackbox.md` |
| 3.5.3 User Acceptance Test | `content/shared/testing/uat.md` |
| 3.5.4 Implementasi Hasil UAT | `content/shared/testing/uat-revisions.md` |
| Lampiran instrumen UAT tertutup | `content/shared/testing/appendix-instruments.md` |

Angka dan status terstruktur yang mendasari fragment pengujian berada di `content/shared/testing/results.json`. `project_facts.json` pada setiap branch boleh memuat salinan yang diperlukan generator per-role, tetapi tidak boleh bertentangan dengan hasil bersama tersebut.

File di `Hasil UAT/` adalah bukti atau hasil ekstraksi kerja. Isi laporan yang digunakan semua branch berasal dari fragment kanonik pada tabel di atas.
