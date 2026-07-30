# Handoff Manual Sinkronisasi Tipografi, Bahasa, dan Bibliografi

> Untuk AI yang menangani laporan Dwikhi atau Faiz.
>
> Dokumen ini menjelaskan perubahan fundamental yang telah diterapkan pada pipeline dan draf laporan Iman. Terapkan aturan bersama secara selektif pada branch penerima. Jangan menyalin seluruh draf, fakta proyek, manifest gambar, front matter, atau bukti teknis Iman.

## 1. Tujuan

Sinkronisasi ini bertujuan agar ketiga laporan:

1. menggunakan bahasa Indonesia akademik yang tetap mudah dipahami;
2. memakai istilah yang konsisten dan tidak mencampurkan padanan Indonesia dengan istilah Inggris yang artinya sama;
3. menghasilkan DOCX dengan tipografi yang seragam setelah field Word diperbarui;
4. mempunyai caption, rujukan gambar/tabel, kode, dan bibliografi yang stabil;
5. tetap mempertahankan judul, identitas, fokus pembahasan, bukti, serta kontribusi teknis masing-masing anggota.

Dokumen ini tidak mengubah pembagian ownership:

| Anggota | Fokus yang Tetap Dilindungi |
| --- | --- |
| Iman | React, REST API, integrasi Supabase, penghubung sisi React, deployment, dan pengujian web/API |
| Dwikhi | ERD, skema, RLS, data dan mapping, aset 3D, prefab, serta hierarchy `Pointer` |
| Faiz | Unity saat dijalankan, konsumsi API, NavMesh, navigasi, spawn, minimap, tooling editor, callback, optimasi, dan build WebGL |

## 2. Gerbang Keselamatan Sebelum Sinkronisasi

AI penerima wajib melakukan langkah berikut sebelum menyunting:

1. Pastikan branch aktif adalah branch pemilik laporan.
2. Periksa `git status --short` dan seluruh diff lokal.
3. Jangan menambahkan `.env`, kredensial, token, hasil build sementara, atau data sensitif.
4. Commit seluruh pekerjaan lokal sebagai checkpoint.
5. Push checkpoint ke branch pemilik laporan.
6. Berhenti apabila commit atau push gagal.
7. Baru setelah checkpoint aman, terapkan perubahan dalam handoff ini.
8. Buat commit sinkronisasi terpisah setelah seluruh validasi lulus.
9. Perlakukan penulis laporan pada branch aktif sebagai pemilik dokumen dan sumber keputusan untuk gaya personal yang belum diatur pedoman kampus atau dokumen ini.

Jangan memakai checkout, merge, cherry-pick, restore, atau penyalinan seluruh file dari branch Iman. Gunakan diff manual dan pertahankan perubahan lokal yang tidak terkait.

## 3. Sumber Aturan yang Perlu Dibandingkan

AI penerima perlu membandingkan file lokalnya dengan sumber berikut secara selektif:

| Sumber | Fungsi |
| --- | --- |
| `.kiro/steering/aturan-penulisan.md` | Aturan bahasa, istilah, daftar, caption, kode, dan larangan bold manual |
| `.kiro/steering/aturan-sitasi.md` | Format sitasi dan bibliografi |
| `skills/references/format-spec-upnvj.md` | Ukuran halaman, margin, font, spasi, caption, dan penomoran halaman |
| `term_registry.json` | Bentuk istilah kanonik dan istilah asing yang dicetak miring |
| `skills/scripts/merge_draft_to_docx.py` | Parsing Markdown, inline code, istilah miring, dan fenced code block |
| `skills/scripts/format_ta_proyek.py` | Style Word, caption, field `SEQ`/`REF`, tabel, font, dan bibliografi |
| `skills/scripts/inject_all_images.py` | Pemulihan tipografi setelah Word COM dan batas ukuran gambar |
| `tests/test_technical_typography.py` | Regression test tipografi umum |
| `tests/test_report_terminology_contract.py` | Regression test konsistensi bahasa laporan |
| `tests/test_wpi_bibliography.py` | Regression test format bibliografi |

File pipeline boleh berbeda antarbranch. Jangan mengganti script penerima secara utuh. Port fungsi atau perilaku yang belum tersedia, lalu jalankan test branch tersebut.

## 4. Kesepakatan Bahasa dan Istilah

### 4.1 Bentuk yang Dipertahankan

Gunakan bentuk berikut secara konsisten dalam narasi Indonesia:

| Konteks | Bentuk yang Dipakai | Bentuk yang Dihindari |
| --- | --- | --- |
| Halaman publik | Dashboard Publik | Dasbor Publik, Public Dashboard |
| Halaman pengelola | Panel Admin | Admin Panel, dashboard admin jika merujuk nama komponen |
| Tampilan untuk pengguna | antarmuka | user interface, UI pada narasi umum |
| Lapisan React | frontend | front-end, sisi klien jika tidak diperlukan |
| Layanan aplikasi | backend | back-end |
| Penyimpanan data | database | basis data jika digunakan bergantian dalam laporan yang sama |
| Pihak yang berkepentingan | pemangku kepentingan | stakeholder |
| Perangkat telepon | smartphone | perangkat bergerak, mobile device |
| Aplikasi penjelajah web | browser | peramban, web browser |
| Proses publikasi | deployment | penyebaran aplikasi jika dipakai bergantian |
| Tempat layanan berjalan | hosting | penginangan |
| Penyimpanan sementara aset | cache aset | asset cache, penyimpanan sementara aset |
| Keluaran kompilasi | file hasil build | build artifact, artefak build |
| Bukti tampilan | tangkapan layar | screenshot |
| Program yang dilampirkan | kode sumber | source code |
| Pemeriksaan dengan script | pengujian otomatis | automated test |
| Hasil permintaan API | respons | response, respon |
| Data akses | kredensial | credential |
| Pemberitahuan saat tiba | notifikasi kedatangan | pemberitahuan penyelesaian navigasi pada narasi umum |
| Identifier tujuan Unity | kode lokasi Unity | kode objek, nama internal, `unity_object_name` berulang-ulang |

Gunakan `frontend` untuk lapisan implementasi React dan `antarmuka` untuk tampilan yang digunakan pengguna. Gunakan `backend` untuk implementasi layanan dan `server` untuk lingkungan yang menjalankannya.

### 4.2 Identifier Teknis

Identifier persis diperkenalkan satu kali ketika diperlukan, kemudian gunakan padanan yang lebih mudah dipahami:

| Identifier | Penyebutan Setelah Diperkenalkan |
| --- | --- |
| `unity_object_name` | kode lokasi Unity |
| `OnNavigationCompleted` | notifikasi kedatangan atau pemberitahuan selesai dari Unity |
| `SendMessage` | mekanisme pengiriman perintah React-Unity |
| `DatabaseSyncChecker` | alat pemeriksaan sinkronisasi pada Unity Editor |
| payload | data yang dikirim |
| runtime Unity | Unity saat dijalankan |

Identifier asli tetap dipertahankan di cuplikan kode, tabel endpoint/format data, skenario pengujian, dan lampiran teknis. Jangan menghilangkannya dari tempat yang memang membutuhkan ketepatan implementasi.

### 4.3 Singkatan dan Istilah Asing

Kepanjangan asing ketika pertama kali memperkenalkan singkatan ditulis miring, sedangkan singkatannya tetap regular:

```md
*Unified Modeling Language* (UML)
*Entity Relationship Diagram* (ERD)
*Row Level Security* (RLS)
*User Acceptance Test* (UAT)
```

Penyebutan berikutnya cukup menggunakan UML, ERD, RLS, atau UAT. Jangan menulis terjemahan Inggris dalam kurung apabila istilah Indonesia sudah jelas. Contoh yang harus dihapus adalah `Aksesibilitas (Accessibility)` dan `pemangku kepentingan (stakeholder)`.

Nama diagram yang digunakan:

1. Use Case Diagram;
2. Activity Diagram;
3. Sequence Diagram;
4. Entity Relationship Diagram ketika pertama diperkenalkan, lalu ERD.

Jangan memakai bentuk campuran seperti Diagram Aktivitas, Diagram Urutan, dan Sequence Diagram dalam laporan yang sama.

### 4.4 Kalimat Akademik yang Tetap Wajar

1. Utamakan subjek, tindakan, dan hasil yang jelas.
2. Hindari menyebut nama variabel, fungsi, hash commit, atau path lokal apabila tidak dibutuhkan untuk memahami hasil.
3. Hash dan path boleh berada pada fakta internal atau indeks keterlacakan, tetapi tidak pada narasi yang dibaca penguji.
4. Hindari kalimat yang menjelaskan proses dengan istilah kode secara berturut-turut. Jelaskan tujuan dan perilakunya terlebih dahulu.
5. Hindari istilah `kontrak` jika yang dimaksud hanya hubungan data atau aturan integrasi. Pilih istilah sesuai konteks:
   a. ketentuan integrasi;
   b. format data;
   c. pemetaan data;
   d. spesifikasi endpoint;
   e. hubungan antarkomponen.
6. Jangan menambahkan teks tebal hanya untuk penekanan dalam paragraf biasa.

### 4.5 Keputusan Istilah yang Belum Disepakati

Untuk kata, frasa, singkatan, atau gaya penyebutan yang belum tercantum dalam kesepakatan bahasa dan istilah, AI wajib berkomunikasi dengan pemilik dokumen sebelum melakukan penggantian massal.

Aturan pengambilan keputusannya:

1. Pemilik dokumen adalah penulis laporan pada branch yang sedang dikerjakan: Dwikhi untuk laporan Dwikhi dan Faiz untuk laporan Faiz.
2. Pedoman resmi kampus tetap menjadi otoritas tertinggi. Pilihan pemilik dokumen berlaku untuk hal yang tidak diatur secara eksplisit oleh pedoman.
3. AI harus menunjukkan istilah yang ditemukan, konteks kalimatnya, serta dua atau tiga alternatif yang wajar. Jangan hanya menanyakan “mau diganti apa?” tanpa konteks.
4. Jangan menganggap pilihan bahasa Iman otomatis berlaku untuk kalimat khusus kontribusi Dwikhi atau Faiz.
5. Setelah pemilik memilih, terapkan bentuk tersebut secara konsisten pada laporan miliknya dan, bila relevan, catat dalam `term_registry.json` branch tersebut.
6. Jika pemilik belum menjawab, jangan melakukan penggantian massal dan jangan mengarang keputusan. Pertahankan teks asal yang tidak menyesatkan, catat temuannya dalam laporan kerja AI, lalu lanjutkan bagian lain yang tidak bergantung pada keputusan tersebut.
7. Jangan memasukkan placeholder diskusi internal ke DOCX final.

Aturan bersama menentukan konsistensi format dan fakta. Gaya kalimat personal tetap boleh disesuaikan dengan penulis selama tetap akademik, jelas, tidak berlebihan, dan tidak mengubah fakta atau ownership.

## 5. Aturan Tipografi DOCX

### 5.1 Format Umum

1. Kertas A4 portrait.
2. Margin kiri 4 cm; atas, kanan, dan bawah 3 cm.
3. Teks laporan memakai Times New Roman 12 pt.
4. Judul BAB memakai Times New Roman 14 pt tebal dan rata tengah.
5. Heading lain memakai Times New Roman 12 pt tebal sesuai template.
6. Paragraf isi rata kiri-kanan, spasi 1,15, dan inden baris pertama 1 cm.
7. Screenshot aplikasi tidak diubah font-nya karena merupakan bukti antarmuka asli.
8. Daftar Isi, Daftar Gambar, Daftar Tabel, Daftar Lampiran, dan hyperlink internal harus tampil hitam dengan Times New Roman, bukan biru atau bergaris bawah.

### 5.2 Batas Penebalan

Bold hanya digunakan pada:

1. bagian cover yang diwajibkan template;
2. heading dan judul lampiran;
3. header tabel;
4. label dan nomor caption, misalnya `Gambar 2.1` atau `Tabel 3.2`;
5. label front matter yang memang diwajibkan, seperti `Kata kunci:` dan `Keywords:`.

Kalimat penjelasan, status pengujian, nama fitur di tengah paragraf, hyperlink, inline code, dan rujukan `Gambar X.Y`/`Tabel X.Y` harus regular.

### 5.3 Cuplikan Kode

1. Fenced code block memakai Courier New 12 pt miring.
2. Kode rata kiri, spasi tunggal, tanpa warna sintaks, latar, bingkai, atau nomor baris.
3. Inline code tetap memakai Times New Roman 12 pt miring agar menyatu dengan paragraf.
4. Courier New hanya boleh muncul pada paragraf style `CodeBlock`. Font monospace yang muncul di bagian lain harus dinormalisasi menjadi Times New Roman.
5. Cuplikan BAB III hanya menampilkan alur penting. Impor, konfigurasi berulang, dan baris yang tidak dibahas dipindahkan atau diringkas.
6. Jangan memakai add-in Easy Code Formatter. Format kode dibuat oleh pipeline agar tidak bergantung pada langkah manual, tidak berubah pada build berikutnya, dan tidak mengirim isi dokumen ke layanan eksternal.

## 6. Caption, Rujukan, Gambar, dan Tabel

### 6.1 Caption

1. Style `Caption` harus berbasis `Normal`, bukan Heading.
2. Caption memakai Times New Roman 12 pt, hitam, rata tengah, dan spasi 1,0.
3. Label dan nomor lengkap dicetak tebal.
4. Deskripsi caption regular; hanya istilah asing yang benar-benar diperlukan yang miring.
5. Nomor dibuat oleh field Word `SEQ`, bukan angka statis dari Markdown.
6. Field angka hasil `SEQ` harus diberi format 12 pt tebal secara langsung agar digit terakhir tidak berbeda ukuran.
7. Pemrosesan istilah teknis tidak boleh memiringkan seluruh deskripsi caption.

Sumber Markdown yang digunakan:

```md
[FIGURE:id_gambar]
[FIGCAPTION:Deskripsi gambar]

[TABLE-ID:id_tabel]
[TABLECAPTION:Deskripsi tabel]
[TABLE]
...
[/TABLE]
```

### 6.2 Rujukan Gambar dan Tabel

1. Gunakan `[FIGREF:id]` atau `[TABREF:id]` di tengah kalimat.
2. Jangan mengawali kalimat dengan token referensi.
3. Pipeline mengubah token menjadi field Word `REF`.
4. Hasil field `REF` harus regular walaupun caption sumbernya tebal.
5. Setiap gambar wajib mempunyai minimal satu narasi penjelasan dalam BAB yang sama.

### 6.3 Gambar dan Diagram

1. Gambar tidak boleh dipotong, didistorsi, atau diperbesar melampaui resolusi sumber.
2. Ukuran maksimum gambar isi sekitar 14 cm lebar dan 16 cm tinggi.
3. Drawing harus tepat sebelum caption dan keduanya harus berada pada halaman yang sama.
4. Nomor dan teks `Gambar X.Y` tidak boleh ditulis di dalam kanvas UML; caption Word menjadi satu-satunya judul/nomor.
5. Seluruh teks diagram buatan tim memakai Times New Roman.
6. Jangan mengganti aset legenda Use Case yang sudah dipilih manual tanpa permintaan eksplisit pemilik laporan.

### 6.4 Tabel

1. Caption tabel berada di atas tabel.
2. Header tabel tebal; isi tabel regular.
3. Isi tabel tidak boleh seluruhnya miring hanya karena memuat istilah teknis atau rujukan tabel.
4. Miring hanya diterapkan pada istilah asing yang diperlukan dan identifier yang memang perlu dibedakan.
5. Tabel harus muat dalam printable width dan header diulang pada halaman lanjutan.
6. Gunakan nama yang mudah dipahami, misalnya `Pemetaan Data yang Digunakan Komponen`, bukan `Kontrak Data` apabila pembaca tidak memerlukan istilah tersebut.

## 7. Perbaikan Bibliografi

### 7.1 Format Entri

Daftar Pustaka berasal dari bagian `# DAFTAR PUSTAKA` pada Markdown. Aturannya:

1. satu sumber ditulis sebagai satu paragraf;
2. entri diurutkan alfabetis menurut penulis atau organisasi;
3. Times New Roman 12 pt;
4. spasi 1,0;
5. rata kiri, bukan rata kiri-kanan;
6. inden gantung 1 cm;
7. jarak setelah paragraf 6 pt;
8. judul jurnal dicetak miring;
9. nama penulis, tahun, judul artikel, volume, nomor, halaman, DOI, dan URL regular;
10. DOI ditulis satu kali sebagai `https://doi.org/...`.

Rata kiri wajib dipertahankan karena rata kiri-kanan membuat Word melebarkan jarak antarkata pada baris yang pendek. Awalan ganda seperti berikut harus ditolak:

```text
https://doi.org/https://doi.org/...
```

### 7.2 Jalur Pipeline yang Harus Ditangani

Bibliografi dapat muncul melalui dua jalur:

1. Mendeley bibliography SDT pada template lama;
2. paragraf Markdown biasa setelah heading `DAFTAR PUSTAKA`.

Keduanya harus menggunakan formatter yang sama. Pada implementasi terbaru, `format_bibliography_paragraph()`:

1. menghapus numbering/list style yang tidak semestinya;
2. menetapkan style Normal;
3. menerapkan rata kiri, inden gantung 1 cm, dan spasi tunggal;
4. membangun ulang run regular/miring dari sumber Markdown;
5. mencegah `UPNVJ.` terbaca sebagai penanda daftar dan berubah menjadi `UPNVJ.(2026)` tanpa spasi.

AI penerima harus memastikan loop formatter umum tidak mengubah kembali paragraf bibliografi menjadi rata kiri-kanan atau inden baris pertama.

### 7.3 Sitasi

1. Sitasi memakai author-year tanpa koma sebelum tahun: `(Nama 2024)` atau `(Nama et al. 2024)`.
2. Dua penulis dapat memakai bentuk `(Syarif dan Risdiansyah 2024)`.
3. Tahun bersufiks seperti `2025a` dan `2025b` harus dikenali.
4. Semua sitasi harus memiliki entri bibliografi dan semua entri harus digunakan.
5. Jalankan cross-check dengan target nol mismatch.

## 8. Front Matter

Urutan umum yang telah dipakai:

1. cover;
2. Pernyataan Mengenai Skripsi dan Sumber Informasi serta Pelimpahan Hak Cipta;
3. lembar persetujuan placeholder;
4. abstrak Bahasa Indonesia dan kata kunci;
5. abstract Bahasa Inggris dan keywords;
6. kata pengantar;
7. Daftar Isi, Daftar Gambar, Daftar Tabel, dan Daftar Lampiran.

Judul `ABSTRAK` dan `ABSTRACT` rata tengah, Times New Roman 12 pt tebal. Isi regular 12 pt. Hanya label `Kata kunci:` dan `Keywords:` yang tebal. Front matter merupakan konten personal; nama, NIM, judul, tanggal, isi abstrak, ucapan terima kasih, dan tanda tangan tidak boleh disalin dari Iman.

Word COM dapat mengubah style atau run front matter saat memperbarui field. Oleh karena itu, tahap pasca-COM harus mengembalikan style front matter dan tipografi eksplisit yang diwajibkan.

## 9. Fungsi Pipeline yang Perlu Tersedia

Periksa apakah branch penerima sudah mempunyai perilaku berikut:

### 9.1 `merge_draft_to_docx.py`

1. inline code menjadi Times New Roman 12 pt miring;
2. istilah dalam `italic_terms` dimiringkan secara selektif;
3. fenced code block menjadi Courier New 12 pt miring;
4. marker caption dan referensi ID-based dipertahankan;
5. bold manual Markdown tidak dipakai pada narasi laporan.

### 9.2 `format_ta_proyek.py`

1. `ensure_caption_style()` menetapkan Caption berbasis Normal;
2. `set_run_typography()` memberi font, ukuran, bold, dan italic secara eksplisit;
3. `format_caption_paragraph_clean()` memformat label/nomor tebal dan deskripsi regular;
4. `replace_semantic_references_in_paragraph()` membuat field `REF` regular;
5. `format_bibliography_paragraph()` menangani bibliografi SDT dan paragraf Markdown;
6. `fix_all_fonts_lxml()` mempertahankan Courier New hanya pada CodeBlock dan menormalkan font lainnya;
7. tabel dan heading tetap mengikuti format kampus.

### 9.3 `inject_all_images.py`

Tahap setelah Word COM harus menjalankan:

1. normalisasi caption;
2. normalisasi field `REF`;
3. pemulihan front matter;
4. penerapan ulang italic teknis secara selektif;
5. pembatasan gambar isi 14 x 16 cm;
6. penjagaan drawing-caption dan integritas gambar.

Tanpa tahap pasca-COM, Word dapat mengembalikan nomor caption yang tidak tebal, membuat rujukan narasi ikut tebal, menghapus italic tertentu, atau mengubah style front matter.

## 10. Bagian yang Dilarang Ditimpa

AI penerima tidak boleh mengganti secara utuh:

1. `Tugas_Akhir_Draft.md`;
2. `project_facts.json`;
3. `images/manifest.json`;
4. `content/roles/<role>/`;
5. judul, nama, NIM, abstrak, kata pengantar, dan identitas personal;
6. BAB II dan BAB III teknis khusus role;
7. gambar, logbook, pengujian, kesimpulan, dan lampiran kode personal;
8. DOCX yang sedang diedit manual oleh pemilik laporan.

Aturan tipografi dan bahasa boleh sama, tetapi isi kontribusi tetap berbeda. Jangan menjadikan angka pengujian React, Lighthouse, atau API Iman sebagai hasil pengujian teknis Dwikhi atau Faiz.

## 11. Urutan Implementasi yang Disarankan

1. Buat checkpoint commit dan push.
2. Sinkronkan aturan istilah dan format terlebih dahulu.
3. Perbarui `term_registry.json` secara selektif.
4. Inventarisasi istilah yang belum tercakup dan minta keputusan pemilik dokumen sebelum penggantian massal.
5. Perbaiki Markdown agar memakai istilah yang telah disepakati dan menghapus bold manual.
6. Port formatter caption, field `REF`, fenced code block, dan normalisasi font.
7. Port formatter bibliografi untuk jalur SDT dan Markdown.
8. Port tahap pasca-COM.
9. Tambahkan atau sesuaikan regression test.
10. Tinjau Markdown bersama pemilik dokumen sebelum membuat DOCX.
11. Setelah disetujui pemilik laporan, simpan dan tutup seluruh Word lalu jalankan build.

## 12. Validasi Wajib

Jalankan dari root repository penerima.

### 12.1 Pemeriksaan Markdown dan Include

```powershell
C:\Python312\python.exe skills/scripts/merge_draft_to_docx.py --check-includes
git diff --check
```

Pastikan tidak ada:

1. campuran `Dasbor`, `Public Dashboard`, dan `Dashboard Publik`;
2. campuran `stakeholder` dan `pemangku kepentingan`;
3. `perangkat bergerak` ketika yang dimaksud smartphone;
4. terjemahan ganda seperti `Aksesibilitas (Accessibility)`;
5. hash commit dan path lokal pada laporan;
6. bold manual pada kalimat penjelasan;
7. DOI ganda;
8. placeholder `[TBD: ...]` yang seharusnya telah diselesaikan berdasarkan bukti.

### 12.2 Test Terfokus

```powershell
C:\Python312\python.exe -m pytest -q tests/test_technical_typography.py
C:\Python312\python.exe -m pytest -q tests/test_report_terminology_contract.py
C:\Python312\python.exe -m pytest -q tests/test_wpi_bibliography.py
C:\Python312\python.exe -m pytest -q tests/test_page_layout_formatting.py
C:\Python312\python.exe -m pytest -q tests/test_figure_narration_validation.py
```

Jika nama test berbeda pada branch penerima, jalankan padanan yang menguji perilaku sama. Jangan menyalin test Iman lalu menghapus test khusus role penerima.

### 12.3 Full Suite dan Build

```powershell
C:\Python312\python.exe -m pytest -q tests
C:\Python312\python.exe skills/scripts/build_pipeline.py
C:\Python312\python.exe skills/scripts/validate_docx_structure.py Tugas_Akhir_Formatted.docx --citation-fatal
```

Sebelum build, pengguna harus menyimpan dan menutup seluruh Microsoft Word karena pipeline menghentikan proses Word. Jangan membangun DOCX sebelum Markdown ditinjau pemilik laporan.

### 12.4 Pemeriksaan Visual Word

Periksa minimal bagian awal, tengah, dan akhir dokumen:

1. heading dan daftar otomatis berwarna hitam serta memakai Times New Roman;
2. nomor caption sejajar dan ukurannya sama;
3. deskripsi caption tidak seluruhnya miring;
4. rujukan Gambar/Tabel di kalimat tidak tebal;
5. fenced code block memakai Courier New 12 pt miring;
6. tabel tidak melewati margin dan isi tabel tidak seluruhnya miring;
7. gambar tidak melewati margin kanan;
8. bibliografi rata kiri dengan inden gantung dan tidak memiliki jarak kata yang melebar;
9. entri organisasi seperti `UPNVJ. (2026)` mempertahankan spasi yang benar;
10. tidak ada PDF baru apabila pemilik hanya meminta DOCX.

## 13. Laporan Hasil yang Harus Diberikan AI

Setelah selesai, AI penerima harus melaporkan:

1. branch aktif dan checkpoint sebelum sinkronisasi;
2. file yang diubah;
3. aturan bahasa yang diterapkan;
4. daftar istilah baru yang dikonfirmasi pemilik dokumen beserta keputusan yang dipakai;
5. perubahan pipeline tipografi dan bibliografi;
6. bukti bahwa konten role tidak ditimpa dan gaya personal penulis dipertahankan;
7. hasil include check, test terfokus, full suite, validator, dan `git diff --check`;
8. hasil pemeriksaan visual DOCX;
9. keterbatasan atau istilah yang masih menunggu keputusan;
10. commit sinkronisasi terpisah dan status push.

Jika aturan dalam dokumen ini bertentangan dengan pedoman kampus atau instruksi terbaru pemilik laporan, hentikan bagian yang bertentangan dan minta keputusan. Jangan memilih secara diam-diam.
