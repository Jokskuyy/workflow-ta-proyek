# AI Agent Operating Guide

Scope: seluruh repository ini.

Dokumen ini adalah entry point untuk AI agent. Tujuannya agar agent dapat memahami sistem dan menentukan file yang perlu dibaca tanpa memindai seluruh codebase. Untuk penjelasan manusia yang lebih lengkap, baca `DOKUMENTASI-PIPELINE.md`.

## 1. Tujuan repository

Repository ini menghasilkan laporan Tugas Akhir Proyek UPNVJ FIK 2025.

Ada tiga tahap yang tetap terpisah:

1. `skills/scripts/generate_content.py` dapat meminta proposal konten dari AI/provider secara opsional. Default-nya hanya suggest + diff; draf baru ditulis dengan `--apply` eksplisit.
2. `skills/scripts/alur_penulisan/` memproses dan menjaga kualitas Markdown secara deterministik. Workflow ini hanya berjalan jika `run_alur()` dipanggil secara eksplisit.
3. `skills/scripts/build_pipeline.py` mengomposisikan `Tugas_Akhir_Draft.md` dengan fragment `content/shared/`, mengubah hasilnya bersama template menjadi `Tugas_Akhir_Formatted.docx`, lalu memvalidasinya. Komposisi berlangsung di memori dan build tidak pernah memanggil provider AI.

Alur DOCX:

```text
archive/Tugas Akhir.docx
        +
Tugas_Akhir_Draft.md -- include --> content/shared/*.md
        |
        v
unpack -> merge -> project patch -> numbering -> formatting
       -> pack/Word COM -> image injection -> validation
        |
        v
Tugas_Akhir_Formatted.docx
```

## 2. Protokol awal agent

Sebelum mengubah apa pun:

1. Baca `git status --short`. Worktree sering berisi perubahan pengguna; jangan menghapus, me-reset, atau menimpa perubahan yang tidak terkait.
2. Tentukan jenis tugas melalui tabel routing di bawah.
3. Baca hanya sumber kanonik dan implementation files yang disebut untuk jenis tugas tersebut.
4. Jangan mengedit salinan runtime di `scratch/` sebagai perubahan utama. Empat script runtime ditimpa dari `skills/scripts/` pada setiap build.
5. Jika aturan baru tidak jelas fatal atau warning, jangan menebak. Periksa pedoman kampus/sumber kanonik atau minta keputusan pengguna.
6. Setelah perubahan, jalankan test terfokus, full suite resmi, dan validator/generate DOCX jika perubahan memengaruhi output.

## 3. Routing: file yang perlu dibaca berdasarkan tugas

| Jenis tugas | Baca terlebih dahulu | Implementation/test berikutnya |
|---|---|---|
| Menulis atau merevisi isi laporan | `Tugas_Akhir_Draft.md`, `.kiro/steering/aturan-penulisan.md`, `.kiro/steering/aturan-sitasi.md`, `skills/references/outline-4bab.md` | `project_facts.json`, `term_registry.json`, lalu panduan peran pada pemetaan di bawah |
| Mengubah format kampus/layout | `skills/references/format-spec-upnvj.md`, `skills/scripts/format_ta_proyek.py` | `skills/scripts/validate_docx_structure.py`, `tests/test_page_layout_formatting.py`, `tests/test_dynamic_format_helpers_properties.py` |
| Mengubah parser Markdown/merge | `skills/scripts/merge_draft_to_docx.py` | `tests/test_wpi_tokenizer.py`, `tests/test_wpi_lists.py`, `tests/test_wpi_tables.py`, `tests/test_dynamic_merge_properties.py` |
| Mengubah gambar/caption/narasi | `images/manifest.json`, `images/manifest_reconcile.json`, `skills/scripts/inject_all_images.py` | `skills/scripts/format_ta_proyek.py`, `skills/scripts/validate_docx_structure.py`, `tests/test_figure_narration_validation.py`, seluruh `tests/test_image_*` |
| Mengubah tabel | `skills/scripts/merge_draft_to_docx.py`, `skills/scripts/format_ta_proyek.py` | seluruh `tests/test_table_*`, `tests/test_gantt_table.py`, `tests/test_wpi_tables.py` |
| Mengubah sitasi/writing guard | `.kiro/steering/aturan-sitasi.md`, `skills/scripts/merge_draft_to_docx.py`, `skills/scripts/validate_docx_structure.py` | `tests/test_wpi_guards.py`, `tests/test_wpi_validator_guards.py`, `tests/test_wpi_bibliography.py` |
| Mengubah workflow penulisan otomatis | `.kiro/specs/automated-writing-workflow/`, `skills/scripts/alur_penulisan/pipeline.py`, `skills/scripts/alur_penulisan/__init__.py` | `tests/test_alur_*`, `tests/test_awf_*`, `tests/test_draft_io.py` |
| Mengubah generator konten AI | `.kiro/specs/agentic-content-generation/`, `skills/scripts/alur_penulisan/agentic_generation.py`, `skills/scripts/alur_penulisan/generation_providers.py` | `skills/scripts/generate_content.py`, `tests/test_agentic_content_generation.py` |
| Mengubah build/packaging | `skills/scripts/build_pipeline.py`, `skills/scripts/unpack.py`, `skills/scripts/pack.py`, `skills/scripts/update_fields_com.py` | validator final dan build end-to-end |
| Menambah patch konten proyek | `skills/scripts/patch_template.py` | Draf, hasil build, dan test/regression baru yang spesifik |
| Dokumentasi/troubleshooting | `DOKUMENTASI-PIPELINE.md`, `README.md` | Script yang perilakunya sedang didokumentasikan |
| Mengubah konten bersama tiga laporan | `content/README.md`, fragment terkait di `content/shared/`, `project_facts.json`, `term_registry.json` | `Tugas_Akhir_Draft.md`, `tests/test_markdown_shared_includes.py`, panduan peran yang relevan |

Jangan membaca semua file `.kiro/specs/` secara default. Baca spec yang sesuai dengan fitur yang sedang diubah. Spec menjelaskan riwayat requirement/desain; code dan test aktif menentukan perilaku implementasi saat ini.

Pemetaan panduan branch/peran:

| Branch | Panduan peran | Outline tambahan |
|---|---|---|
| `laporan/iman` | `laporan-tim/iman-fullstack-integrator/README.md` | Belum ada file khusus; gunakan `skills/references/outline-4bab.md` |
| `laporan/dwikhi` | `laporan-tim/dwikhi-3d-asset-database/README.md` | `laporan-tim/dwikhi-3d-asset-database/outline-laporan.md` |
| `laporan/faiz` | `laporan-tim/faiz-engine-developer/README.md` | `laporan-tim/faiz-engine-developer/outline-laporan.md` |

## 4. Urutan otoritas

Jika informasi bertentangan, gunakan urutan berikut:

1. Pedoman resmi kampus dan instruksi pengguna saat ini.
2. `skills/references/format-spec-upnvj.md`.
3. `skills/references/outline-4bab.md`.
4. `.kiro/steering/aturan-penulisan.md` dan `.kiro/steering/aturan-sitasi.md`.
5. `.kiro/steering/konteks-proyek.md`.
6. `project_facts.json` dan `term_registry.json`.
7. Fragment laporan aktif di `content/shared/` dan konten branch di `Tugas_Akhir_Draft.md`/`content/roles/`.
8. Code aktif di `skills/scripts/` beserta test di `tests/`.
9. Dokumentasi ringkasan seperti `DOKUMENTASI-PIPELINE.md`, `PANDUAN-FITUR.md`, atau README.

Jika implementasi menyimpang dari sumber dengan prioritas lebih tinggi, laporkan drift dan perbaiki code/test/dokumentasi secara konsisten sesuai scope tugas.

## 5. Invariant yang tidak boleh dilanggar

### 5.1 Format halaman

- A4 portrait.
- Margin kiri 4 cm = 2268 twips.
- Margin atas, kanan, dan bawah 3 cm = 1701 twips.
- Semua section harus memakai ukuran dan margin yang sama.
- Font utama Times New Roman.
- Body 12 pt, justify, spasi 1,15, first-line indent 1 cm.
- Caption spasi 1,0 dan center.
- Bibliografi spasi 1,0 dengan hanging indent 1 cm.
- Front matter memakai nomor Romawi di kanan bawah (sampul tanpa nomor).
- Body restart nomor Arab dari `1` pada BAB I; pembuka setiap BAB di tengah bawah dan halaman lanjutannya di kanan atas.

### 5.2 Gambar dan narasi

- Caption gambar berada di bawah gambar dan menggunakan style `Caption`.
- Format final caption: `Gambar X.Y Deskripsi`, tanpa titik setelah nomor. Nomor `X.Y` dibuat oleh field Word `SEQ`, bukan ditulis di Markdown.
- Sumber gambar ID-based wajib memakai dua baris bersebelahan: `[FIGURE:<id-manifest>]` lalu `[FIGCAPTION:Deskripsi]`. ID adalah pencarian aset dan bookmark utama; `caption_match` hanya menjadi assertion deskripsi. Draf branch lama dengan caption bernomor masih didukung sementara.
- Counter gambar restart per bab dan mengikuti urutan baca.
- Narasi sumber merujuk gambar dengan `[FIGREF:<id-manifest>]`; formatter mengubah token itu menjadi field Word `REF` yang terlihat sebagai `Gambar X.Y`.
- Setiap caption gambar wajib memiliki minimal satu paragraf narasi biasa dengan `[FIGREF:<id>]` dalam bab yang sama. Rujukan tambahan dari bab lain diperbolehkan.
- Rujukan harus berada di tengah kalimat. Rujukan pada awal paragraf atau tepat setelah `.`, `!`, atau `?` adalah pelanggaran fatal.
- Caption, heading, Daftar Gambar, atau paragraf drawing tidak dihitung sebagai narasi.
- Struktur final harus menjaga drawing tepat sebelum caption. Pola `[drawing][narasi][caption]` diubah menjadi `[drawing][caption][narasi]`.
- Drawing dan caption harus memiliki `keepNext` serta `keepLines`.
- Drawing dan caption wajib berada pada halaman yang sama. Ukuran drawing harus menyisakan ruang caption; bila ruang halaman tersisa tidak cukup, Word harus memindahkan pasangan tersebut bersama ke halaman berikutnya.
- Gambar mempertahankan rasio aspek, tidak di-upscale, tidak dicrop, dan dibatasi sekitar 15 × 16 cm.

### 5.3 Integritas gambar C1–C4

- C1: byte gambar duplikat berdasarkan MD5 ditolak kecuali direkonsiliasi secara sah.
- C2: entry manifest `post_com` harus menghasilkan tepat satu drawing bernama `FIGURE:<id>`, tepat satu caption target, dan keduanya harus bersebelahan. Jika sebuah draf memakai marker, draf tersebut wajib memuat seluruh ID manifest branch itu tepat satu kali.
- C3: byte media di DOCX harus sama dengan file `images/<file>`.
- C4: setiap pasangan `[drawing][caption]` wajib berada pada satu halaman. Validator memeriksa adjacency, `keepNext`/`keepLines`, dan bahwa tinggi drawing ditambah cadangan caption masih muat dalam printable height.
- `source` pada manifest adalah provenance; perbedaan path source saja bukan kegagalan jika byte final benar.
- Jangan menambah allow-list hanya agar test lulus. Gunakan hanya untuk exception yang dapat dijelaskan.

### 5.4 Tabel dan caption

- Caption tabel berada di atas tabel.
- Format final caption: `Tabel X.Y Deskripsi`; nomor dibuat oleh field Word `SEQ`.
- Sumber tabel ID-based memakai `[TABLE-ID:<id>]`, `[TABLECAPTION:Deskripsi]`, lalu blok `[TABLE]...[/TABLE]`. Narasi memakai `[TABREF:<id>]`, yang menjadi field Word `REF` terlihat sebagai `Tabel X.Y`.
- Counter tabel terpisah dari gambar dan restart per bab.
- Tabel harus muat dalam printable width.
- Header row diulang pada halaman lanjutan.
- Isi sel tidak menggunakan first-line indent body.
- Formatter tabel harus struktural. Jangan menambah cabang berdasarkan teks tabel tertentu.

### 5.5 Lampiran dan daftar otomatis

- Lampiran memakai `LAMPIRAN N.` dan style `taappendixheading`.
- `taappendixheading` memakai outline level 8 dan tidak boleh memiliki numbering Word.
- Daftar Lampiran memakai TOC level 9–9 dan style `TOC9` dengan left indent internal `1`.
- Lampiran tidak boleh masuk Daftar Isi utama.
- Field Daftar Isi, Daftar Gambar, Daftar Tabel, dan Daftar Lampiran diperbarui melalui Word COM.

### 5.6 Penulisan akademik

- Jangan gunakan bullet untuk daftar laporan. Hirarki: `1.` -> `a.` -> `1)` -> `a)` dengan tiga spasi per level di Markdown.
- Subbab teori dimulai dengan definisi dan minimal satu sitasi formal.
- Klaim eksternal harus memiliki sumber.
- Latar Belakang tanpa sitasi substantif adalah warning, bukan fatal.
- Cross-check sitasi dua arah adalah warning secara default; hanya fatal ketika dikonfigurasi.
- Sitasi in-text memakai author-year tanpa koma sebelum tahun: `(Nama Tahun)` atau `(Nama et al. Tahun)`.
- Jangan mengarang fakta atau hasil pengujian. Gunakan `project_facts.json`; jika belum tersedia gunakan `[TBD: ...]`.
- Jangan membuat sumber fiktif. Gunakan `[BUTUH SITASI]` jika sumber belum tersedia.

### 5.7 Konten bersama tiga laporan

- `content/shared/` adalah sumber kanonik untuk fakta dan narasi yang harus identik pada tiga laporan.
- `Tugas_Akhir_Draft.md` mengomposisikan fragment dengan directive satu baris `<!-- PIPELINE:INCLUDE path/relatif.md -->`.
- Fragment shared tidak boleh memuat nama, NIM, tanda tangan, judul personal, atau klaim kontribusi satu anggota.
- Angka Black Box/UAT dan status produk tidak boleh disalin ulang ke file role. File role hanya menjelaskan kontribusi dan buktinya.
- Latar Belakang memakai konteks proyek bersama lalu dilanjutkan fokus masalah per role. Rumusan masalah, batasan, tujuan khusus, implementasi, judul, dan kesimpulan kontribusi tetap branch-specific.
- Temuan UAT, kebutuhan produk, dan status build final sama untuk semua laporan. Bentuk solusi boleh berbeda dari saran awal jika matriks menjelaskan ekuivalensi masalah, solusi, bukti, dan retest.
- Raw XLSX/PDF atau bukti bertanda tangan bukan shared content. Gunakan ringkasan anonim yang telah diverifikasi.

## 6. Sumber data dan konfigurasi

| Sumber | Kontrak |
|---|---|
| `Tugas_Akhir_Draft.md` | Merge membaca mulai `# BAB I`/`# BAB 1`; front matter berasal dari template |
| `content/README.md` | Kontrak ownership dan komposisi shared content versus role content |
| `content/shared/` | Fragment fakta/narasi/tabel bersama yang diperluas di memori sebelum parser berjalan; hasil pengujian terstruktur berada di `content/shared/testing/results.json` |
| `archive/Tugas Akhir.docx` | Template sumber build |
| `project_facts.json` | Fakta yang boleh dinyatakan; data tidak tersedia menjadi TBD |
| `term_registry.json` | Bentuk istilah kanonik; ketidakkonsistenan dilaporkan, tidak diam-diam diganti |
| `images/manifest.json` | Sumber ID stabil, aset gambar, assertion caption, provenance, dan metode injeksi |
| `images/manifest_reconcile.json` | Exception C1/C2 yang memang sah |
| `merge_config.json` | Config opsional path `draft` dan `xml`; prioritas CLI > config > default |
| `TA_DRAFT_PATH` | Override lokasi draf untuk writing guard validator |
| `TA_CITATION_FATAL` | `1`, `true`, `yes`, atau `on` membuat cross-check sitasi fatal |

## 7. Kontrak parser Markdown

Parser mendukung:

- heading `#` sampai `######`;
- paragraf biasa;
- daftar `1.`, `a.`, `1)`, `a)` dengan tiga spasi indent per level;
- fenced code block;
- inline bold, italic, bold+italic, inline code, escape `\*`, dan hyperlink;
- `[TABLE]...[/TABLE]`, termasuk mode seperti `[TABLE gantt]`;
- marker/caption/ref ID-based: `[FIGURE:id]`, `[FIGCAPTION:...]`, `[FIGREF:id]`, `[TABLE-ID:id]`, `[TABLECAPTION:...]`, dan `[TABREF:id]`;
- pipe table dengan alignment Markdown;
- `---` sebagai page break;
- `# DAFTAR PUSTAKA` sebagai bibliografi dinamis.
- `<!-- PIPELINE:INCLUDE content/shared/...md -->` sebagai include deterministik relatif terhadap root repository.

Include yang hilang, absolut, keluar dari repository, bukan `.md`, digunakan lebih dari sekali, malformed, atau rekursif merupakan fatal sebelum `document.xml` ditulis. Directive di dalam fenced code block tetap literal. Fragment yang dimasukkan setelah sebuah heading tidak boleh mengulang heading tersebut.

Writing guard murni mengumpulkan warning untuk heading jump, urutan BAB, tabel tidak tertutup, emphasis tidak seimbang, dan cross-check sitasi. Jangan menjadikan warning tersebut fatal tanpa requirement eksplisit.

## 8. Aturan edit dan ownership file

- Ubah script ter-track di `skills/scripts/`.
- Ubah fakta bersama pada fragment kanonik di `content/shared/`, bukan dengan menyalinnya ke tiga draf.
- Baca `content/README.md` sebelum mengubah bagian yang memakai `PIPELINE:INCLUDE`. Jangan edit isi shared secara tidak langsung melalui generator konten per-role.
- Jangan mengandalkan edit langsung di `scratch/merge_draft_to_docx.py`, `scratch/patch_template.py`, `scratch/inject_all_images.py`, atau `scratch/validate_docx_structure.py`; build akan menimpanya.
- `patch_template.py` adalah satu-satunya lokasi yang memang boleh berisi transformasi content-specific. Formatter umum harus tetap berbasis struktur.
- `Tugas_Akhir_Formatted.docx`, `unpacked_ta/`, dan media package adalah hasil build, bukan source of truth.
- Jangan menghapus `unpacked_ta/` atau output pengguna di luar alur build tanpa memastikan target dan izin.
- Jangan menormalkan atau memformat ulang seluruh draf untuk perubahan kecil.
- Pertahankan konten manual dan perubahan pengguna yang tidak terkait.
- Jika mengubah aturan, sinkronkan minimal: sumber kanonik, implementation, regression test, dan dokumentasi agent/manusia yang relevan.

## 9. Perintah resmi

Jalankan dari root repository.

### Build final

```powershell
C:\Python312\python.exe skills/scripts/build_pipeline.py
```

Build melakukan hal berikut yang harus diketahui agent:

- Python executable masih hard-coded ke `C:\Python312\python.exe`.
- Seluruh proses `winword.exe` dihentikan paksa sebelum build. Peringatkan pengguna untuk menyimpan dokumen Word.
- Script runtime disalin dari `skills/scripts/` ke `scratch/`.
- Build fail-fast pada setiap exit code nonzero.
- Output sukses: `Tugas_Akhir_Formatted.docx`.

### Full test suite resmi

```powershell
C:\Python312\python.exe -m pytest -q tests
```

Jangan memakai `pytest -q` tanpa target. Itu juga mengoleksi script diagnostik legacy `test_*.py` di `scratch/` yang bukan bagian suite resmi.

### Validasi shared content tanpa membuat DOCX

```powershell
C:\Python312\python.exe skills/scripts/merge_draft_to_docx.py --check-includes
```

Perintah ini tidak menulis draf, XML, atau DOCX. Jalankan sebelum build setelah mengubah directive atau fragment bersama.

### Generator konten AI opsional

Siapkan request untuk AI agent lain tanpa mengubah draf:

```powershell
C:\Python312\python.exe skills/scripts/generate_content.py --section 3.2.1 --prepare-out scratch/generation-request.json
```

Validasi respons dalam mode suggest (default, tidak menulis draf):

```powershell
C:\Python312\python.exe skills/scripts/generate_content.py --section 3.2.1 --response-file scratch/generation-candidate.json
```

Penulisan hanya diizinkan setelah diff ditinjau:

```powershell
C:\Python312\python.exe skills/scripts/generate_content.py --section 3.2.1 --response-file scratch/generation-candidate.json --apply
```

Agent harus mengingat batas berikut:

- branch selain `laporan/iman|dwikhi|faiz` menghasilkan `HELD` sebelum I/O/provider;
- `--fact` bersifat opt-in; jangan mengirim seluruh `project_facts.json` ke provider eksternal;
- response wajib JSON terstruktur dengan provenance fakta/sitasi/klaim belum terverifikasi;
- jangan membuat sitasi atau caption/aset gambar baru dari generator; rujukan kandidat hanya boleh memakai `[FIGREF:<id>]`/`[TABREF:<id>]` yang sudah ada;
- jangan pernah menambahkan `--apply` tanpa meninjau issues dan diff;
- request/result pada `scratch/` adalah artefak lokal dan tidak boleh dianggap source of truth.

### Validator final

```powershell
C:\Python312\python.exe skills/scripts/validate_docx_structure.py Tugas_Akhir_Formatted.docx
```

Mode cross-check sitasi fatal:

```powershell
C:\Python312\python.exe skills/scripts/validate_docx_structure.py Tugas_Akhir_Formatted.docx --citation-fatal
```

Argumen `--citation-fatal` harus berada setelah path DOCX.

### Test terfokus umum

```powershell
C:\Python312\python.exe -m pytest -q tests/test_figure_narration_validation.py
C:\Python312\python.exe -m pytest -q tests/test_page_layout_formatting.py
C:\Python312\python.exe -m pytest -q tests/test_image_injection_bug_conditions.py
C:\Python312\python.exe -m pytest -q tests/test_table_formatting_integration.py
```

## 10. Fatal versus warning

### Fatal

- DOCX/XML inti tidak valid.
- Section bukan A4/margin 4-3-3-3.
- Style/field appendix dan TOC9 salah.
- Caption/SEQ numbering rusak.
- Drawing-caption adjacency atau keep properties rusak.
- Integritas gambar C1–C4 gagal.
- Gambar tidak memiliki rujukan naratif mid-sentence dalam bab yang sama.
- Teks kode orphan di luar code style.
- Cross-check sitasi hanya fatal jika mode fatal aktif.

### Warning default

- Latar Belakang substantif tanpa sitasi.
- Heading jump, urutan BAB, tabel tidak tertutup, atau emphasis tidak seimbang.
- Cross-check sitasi dua arah.
- Mapping caption/reference lama ambigu atau tidak ditemukan.
- Perbedaan provenance `source` manifest ketika byte media final benar.

Validator harus mengumpulkan semua fatal findings sebelum gagal agar pengguna mendapat laporan lengkap.

## 11. Definition of done

### Perubahan isi saja

- Isi sesuai outline dan scope peran.
- Fakta diverifikasi atau ditandai TBD.
- Istilah konsisten.
- Semua gambar memiliki narasi mid-sentence pada bab yang sama.
- Build dan validator final lulus jika pengguna meminta dokumen terbaru.

### Perubahan formatter/parser/validator

- Ada regression test untuk perilaku baru atau bug yang diperbaiki.
- Test terfokus lulus.
- `C:\Python312\python.exe -m pytest -q tests` lulus.
- DOCX terbaru berhasil dibangun.
- Validator final lulus.
- Layout diperiksa manual di Microsoft Word jika perubahan visual.

### Perubahan gambar

- File aset dan manifest sinkron.
- `caption_match` tepat satu target atau exception direkonsiliasi dengan alasan sah.
- Narasi gambar tersedia.
- C1–C4 lulus.
- Hasil visual diperiksa tanpa distorsi/crop.

### Perubahan dokumentasi

- Perilaku diverifikasi terhadap code/test, bukan hanya spec lama.
- Path dan command dapat dijalankan dari root repository.
- `DOKUMENTASI-PIPELINE.md`, README, dan `AGENTS.md` tidak saling bertentangan.

### Perubahan shared content

- Sumber kanonik hanya ada satu di `content/shared/`; tidak ada salinan isi pada draf atau role content.
- `--check-includes` dan `tests/test_markdown_shared_includes.py` lulus.
- Shared fragment anonim dan bebas identitas/judul personal.
- Angka/fakta konsisten dengan `project_facts.json`, istilah konsisten dengan `term_registry.json`, dan status UAT memiliki bukti atau TBD.
- Perubahan pipeline/dokumentasi dapat disebarkan ke semua branch tanpa menimpa `Tugas_Akhir_Draft.md` atau konten role masing-masing.

### Perubahan generator konten AI

- Mode tanpa `--apply` terbukti tidak memanggil write.
- Branch tidak dikenal berhenti sebelum read/provider.
- Kandidat invalid tidak mengubah draf.
- Apply mempertahankan seluruh baris lama, idempoten, dan membatalkan write bila hash sumber berubah.
- Fakta, sitasi, TBD, daftar, heading, istilah, serta rujukan Gambar/Tabel memiliki regression test.

## 12. Known traps

- Worktree sering kotor. Jangan menganggap semua perubahan adalah milik agent.
- Include tidak membuat salinan fisik. AI yang hanya membaca `Tugas_Akhir_Draft.md` wajib mengikuti marker ke `content/shared/` sebelum menyimpulkan isi subbab.
- `build_pipeline.py` mematikan semua proses Word; jangan menjalankannya tanpa memperingatkan pengguna jika mungkin ada dokumen belum disimpan.
- LibreOffice bukan jalur utama. Instalasi lokal dapat rusak dengan error `bootstrap.ini`; gunakan Word COM. `pack.py --force` hanya workaround dan wajib diikuti injector serta validator.
- Update field COM dapat gagal sebagai warning pada `pack.py`; periksa daftar otomatis secara manual jika itu terjadi.
- Manifest memiliki exception yang disengaja untuk foto lampiran/grafik survei. Jangan menghapus atau memperluas reconciliation tanpa memahami mekanisme penempatannya.
- Generated DOCX dapat lulus struktur tetapi tetap memiliki masalah visual. Untuk perubahan layout, inspeksi Word tetap wajib.
- Jangan menyimpulkan PDF adalah output resmi build; output utama pipeline adalah DOCX.

## 13. Konteks proyek singkat

Sistem yang didokumentasikan adalah platform Smart Campus dengan komponen:

- Public Dashboard: React SPA/Vite.
- Visualisasi 3D: Unity 6 WebGL.
- Admin/data: Supabase Auth, database, RLS, audit, dan CRUD.
- Analytics: Umami self-hosted.
- API utama: Vercel Serverless Functions berbasis Node.js.
- Express hanya untuk reverse proxy Umami dan rate limiter, bukan API utama.
- React mengirim pesan satu arah ke Unity melalui `SendMessage`.
- Unity mengambil data melalui `/api/unity/data` dan memetakan objek menggunakan `unity_object_name`.

Untuk detail arsitektur atau fakta implementasi, baca `.kiro/steering/konteks-proyek.md`, `PRD_Konsolidasi_TA.md`, dan `project_facts.json`; jangan menebak dari ringkasan ini.
