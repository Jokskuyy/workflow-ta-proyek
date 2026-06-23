# Panduan Fitur Repo `workflow-ta-proyek`

Repo ini adalah **toolkit penulisan + otomatisasi format** laporan Tugas Akhir Proyek (UPNVJ FIK 2025). Panduan ini merangkum **seluruh fitur** dan cara memakainya. Berlaku di semua branch (`master`, `laporan/iman`, `laporan/dwikhi`, `laporan/faiz`).

Dokumen terkait:
- `PANDUAN-TIM.md` — alur kerja branch per anggota.
- `README.md` — ringkasan dua skill & pipeline.
- `laporan-tim/<peran>/` — lingkup & kerangka per anggota.
- `PRD_Konsolidasi_TA.md` — acuan kebutuhan produk.

---

## 1. Prasyarat Lingkungan

| Kebutuhan | Keterangan |
|---|---|
| **Python 3.12** | Pipeline meng-hardcode `C:\Python312\python.exe` (lihat `skills/scripts/build_pipeline.py`). Sesuaikan bila path Python berbeda. |
| **Microsoft Word** | Tahap `pack` & update field memakai **Word COM automation** (`win32com`). Wajib ada di Windows. |
| **pywin32** | `pip install pywin32` (untuk `win32com.client`). |
| **Java (JRE/JDK)** | Untuk render diagram PlantUML (`diagrams/plantuml.jar`). |
| **Git** | Kolaborasi multi-branch. |

> Platform: **Windows** (karena dependensi Word COM).

---

## 2. Dua Skill Inti

Definisi lengkap ada di `skills/`:
1. **`write-ta-proyek`** (`skills/write-ta-proyek/SKILL.md`) — memandu penulisan konten: audit konsistensi, sitasi, terminologi, kerangka 4 bab, aturan penulisan akademik.
2. **`docx-ta-proyek`** (`skills/docx-ta-proyek/SKILL.md`) — otomatisasi format `.docx` (margin, font, page break, caption, penomoran halaman).

---

## 3. Menulis Laporan (`Tugas_Akhir_Draft.md`)

Sumber kebenaran tunggal tiap branch adalah **`Tugas_Akhir_Draft.md`** di root. Markdown dipakai karena aman diedit (tidak merusak XML `.docx`).

### Aturan penulisan wajib (dari `write-ta-proyek`)
1. **Tanpa bullet** (`-`, `*`, `+`). Gunakan hierarki: `1.` → `a.` → `1)` → `a)`.
2. **Setiap sub-bab teori diawali definisi + minimal satu sitasi.**
3. **Jangan menyebut gambar/tabel di awal kalimat** ("Gambar 2.1 menunjukkan..." ❌). Sebut di tengah kalimat ("...seperti pada Gambar 2.1.").
4. **Konsistensi istilah** (mis. pakai "database" terus, jangan ganti "basis data").
5. **Jangan mengarang fakta/angka.** Verifikasi ke `project_facts.json`. Bila `completed: false`/`null`, tulis placeholder `[TBD: ...]`.
6. **Lampiran**: format `LAMPIRAN 1.`, tiap lampiran pisah halaman (`---`), tidak muncul di Daftar Isi.

### Aturan sitasi
Detail di `.kiro/steering/aturan-sitasi.md`. Inti: gaya **APA in-text** `(Nama, Tahun)` / `(Nama et al., Tahun)`; setiap sitasi wajib punya entri di `# DAFTAR PUSTAKA` dan sebaliknya; jangan mengarang sumber (tandai `[BUTUH SITASI]`).

### File pendukung penulisan
| File | Fungsi |
|---|---|
| `Tugas_Akhir_Draft.md` | Draf utama (sumber kebenaran). |
| `project_facts.json` | Fakta proyek terverifikasi (status pengujian, angka). Acuan anti-mengarang. |
| `term_registry.json` | Registry istilah teknis untuk konsistensi *(bila ada)*. |
| `citations_to_download.md` | Daftar referensi hasil pencarian yang perlu diunduh PDF-nya *(bila ada)*. |
| `journal/` | PDF jurnal referensi + `references/REFERENCES_GUIDE.md` (link unduh manual). |

---

## 4. Membangun `.docx` (Pipeline Otomatis)

### Cara cepat (satu perintah, end-to-end)
Dari root repo, di branch yang benar:
```bash
C:\Python312\python.exe skills/scripts/build_pipeline.py
```
Output: **`Tugas_Akhir_Formatted.docx`** (di-*ignore* git; tiap anggota generate sendiri).

Tahapan yang dijalankan otomatis:
1. **unpack** template `archive/Tugas Akhir.docx` → `unpacked_ta/`
2. **merge** `Tugas_Akhir_Draft.md` → XML (`scratch/merge_draft_to_docx.py`)
3. **patch** diskrepansi Bab II (`scratch/patch_template.py`)
4. **add numbering preset** (`skills/scripts/add_numbering_preset.py`)
5. **format** margin/font/page break (`skills/scripts/format_ta_proyek.py`)
6. **pack** → `.docx` via **Word COM** (`skills/scripts/pack.py`)
7. **inject gambar** dari `images/manifest.json` (`scratch/inject_all_images.py`)
8. **validasi** struktur & field (`scratch/validate_docx_structure.py`)

> Pastikan **Microsoft Word tertutup** sebelum build (pipeline otomatis `taskkill winword.exe` untuk melepas lock; bila file terkunci, build berhenti dengan pesan jelas).

### Cara manual (langkah per langkah)
```bash
python skills/scripts/unpack.py "archive/Tugas Akhir.docx" unpacked_ta
python skills/scripts/add_numbering_preset.py unpacked_ta
python skills/scripts/format_ta_proyek.py unpacked_ta
python skills/scripts/pack.py unpacked_ta Tugas_Akhir_Formatted.docx
```

### Setelah build — update DAFTAR ISI
Karena pergeseran halaman, buka `.docx` di Word → klik kanan tabel **DAFTAR ISI** → **Update Field → Update entire table**. Bisa juga via `skills/scripts/update_fields_com.py` (otomatis via COM).

---

## 5. Spesifikasi Format (UPNVJ FIK 2025)

| Elemen | Nilai |
|---|---|
| Kertas / Margin | A4 / Atas 3cm, Bawah 3cm, **Kiri 4cm**, Kanan 3cm |
| Font | Times New Roman — Body 12pt (1.5), Judul Bab 14pt Bold Center, Caption 12pt (1.0) |
| Caption Tabel | **di atas** tabel, center, "Tabel 1.1 ..." (tanpa titik setelah nomor) |
| Caption Gambar | **di bawah** gambar, center, "Gambar 2.3 ..." |
| Nomor halaman | Romawi (i, ii, ...) untuk front matter; Arab (1, 2, ...) mulai BAB I |
| Page split | Daftar Isi/Gambar/Tabel/Lampiran di halaman terpisah; cover sendiri |
| Gambar | Pertahankan rasio aspek (tidak distorsi) |

---

## 6. Diagram (Diagram-as-Code)

Folder `diagrams/` berisi 10 diagram **PlantUML** (`.puml`) + hasil render `.png`/`.svg`, semua sesuai PRD & berwarna netral. Lihat `diagrams/README.md`.

Render ulang (mis. setelah mengedit `.puml`):
```bash
# dari folder diagrams/ (plantuml.jar sudah ada di sana)
java -jar plantuml.jar -tpng *.puml
java -jar plantuml.jar -tsvg *.puml
```
Alternatif tanpa instalasi: tempel isi `.puml` ke https://www.plantuml.com/plantuml/uml. Diagram alur tambahan (Mermaid) ada di `diagram_alur_sistem.md` (render di https://mermaid.live).

---

## 7. Gambar & Manifest

- `images/manifest.json` memetakan berkas gambar ke caption "Gambar x.y" untuk injeksi otomatis ke `.docx` (tahap 7 pipeline / `scratch/inject_all_images.py`).
- Screenshot antarmuka & dokumentasi ada di `dokumentasi/`.
- Saat menambah gambar baru: simpan filenya, daftarkan di `manifest.json` dengan nomor caption yang sesuai, lalu rebuild.

---

## 8. Validasi & Quality Guard

`scratch/validate_docx_structure.py` dijalankan otomatis di akhir build dan memeriksa:
1. **Struktur** (style heading, TOC field, page numbering, lampiran) — *fatal bila regресi*.
2. **Writing guards (non-fatal)**: keseimbangan heading/BAB/tabel/emphasis.
3. **Citation cross-check (non-fatal)**: setiap sitasi in-text punya entri Daftar Pustaka & sebaliknya.

> **Catatan false-positive sitasi:** pola seperti `(port 3000, 3000)` atau `('Proxy server running on port 3001', 3001)` berasal dari contoh kode/log, **bukan** sitasi. Aman diabaikan — jangan dibuatkan entri pustaka.

---

## 9. Referensi Jurnal

- PDF tersimpan di `journal/` dan `journal/references/`.
- `journal/references/REFERENCES_GUIDE.md` = tabel link unduh manual tiap referensi (OJS Indonesia sering memblok bot) + catatan koreksi DOI.
- `journal/Jurnal_Iman.md` memuat daftar entri referensi lengkap (format APA) sebagai acuan `# DAFTAR PUSTAKA`.

---

## 10. Konversi PDF (opsional)

Tersedia script konversi di `scratch/` (mis. `convert_formatted_to_pdf.py`, `convert_docx_to_pdf.py`) yang memakai Word COM untuk mengekspor `.docx` → `.pdf`. Pastikan Word tertutup sebelum menjalankan.

---

## 11. Daftar Script Penting

| Script | Fungsi |
|---|---|
| `skills/scripts/build_pipeline.py` | Orchestrator build end-to-end (rekomendasi). |
| `skills/scripts/unpack.py` / `pack.py` | Bongkar/rakit `.docx` ↔ folder XML (pack via Word COM). |
| `skills/scripts/add_numbering_preset.py` | Suntik preset penomoran bab/heading. |
| `skills/scripts/format_ta_proyek.py` | Terapkan aturan format (margin, font, page break, caption). |
| `scratch/merge_draft_to_docx.py` | Konversi `Tugas_Akhir_Draft.md` → `document.xml`. |
| `scratch/patch_template.py` | Patch konten template Bab II. |
| `scratch/inject_all_images.py` | Injeksi gambar dari `images/manifest.json`. |
| `scratch/validate_docx_structure.py` | Validasi struktur & guard non-fatal. |
| `skills/scripts/update_fields_com.py` | Update field (DAFTAR ISI dll.) via COM. |

> Sebagian script `scratch/*` di-*ignore* git (lihat `.gitignore`). Bila clone tidak memilikinya, minta dari pemilik repo atau gunakan jalur manual `skills/scripts/`.

---

## 12. Troubleshooting

| Masalah | Solusi |
|---|---|
| `'Tugas_Akhir_Formatted.docx' is locked` | Tutup Microsoft Word, ulangi build. |
| `ModuleNotFoundError: win32com` | `pip install pywin32` di Python 3.12. |
| Python path salah | Edit `python_exe` di `build_pipeline.py` agar sesuai instalasi. |
| Diagram tak ter-render | Pastikan Java terpasang; jalankan `java -jar plantuml.jar ...` dari folder `diagrams/`. |
| Nomor halaman DAFTAR ISI tidak update | Update Field di Word atau jalankan `update_fields_com.py`. |
| `.docx` tidak ada setelah clone | Memang sengaja (di-*ignore*); generate sendiri dengan `build_pipeline.py`. |

---

## 13. Alur Kerja Singkat per Anggota

```bash
git clone https://github.com/Jokskuyy/workflow-ta-proyek.git
cd workflow-ta-proyek
git checkout laporan/<nama>            # iman | dwikhi | faiz
# tulis di Tugas_Akhir_Draft.md (ikuti aturan Bagian 3)
C:\Python312\python.exe skills/scripts/build_pipeline.py   # build .docx
git add Tugas_Akhir_Draft.md && git commit -m "..." && git push
```
