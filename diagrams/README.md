# Diagram-as-Code — Laporan Tugas Akhir

Folder ini berisi 6 diagram dalam format **PlantUML** (`.puml`). Penomoran mengikuti **DAFTAR GAMBAR pada DOCX final**.

| Berkas | Nomor (DOCX) | Jenis | Judul |
|---|---|---|---|
| `gambar-2.09-arsitektur-sistem.puml` | Gambar 2.9 | Component | Diagram Arsitektur Sistem (regenerasi, sesuai PRD) |
| `gambar-2.10-tahap-pengembangan.puml` | Gambar 2.10 | Activity | Tahap Pengembangan (Model Prototyping) |
| `gambar-2.11-legenda-use-case.puml` | Gambar 2.11 | Legenda | Legenda Use Case Diagram |
| `gambar-2.12-use-case-diagram.puml` | Gambar 2.12 | Use Case | Use Case Diagram |
| `gambar-2.13-activity-pengelolaan-data-admin.puml` | Gambar 2.13 | Activity | Pengelolaan Data oleh Admin |
| `gambar-2.14-activity-integrasi-data-denah.puml` | Gambar 2.14 | Activity | Integrasi Data Denah (Skenario A/B/C) |
| `gambar-2.15-sequence-autentikasi-admin.puml` | Gambar 2.15 | Sequence | Autentikasi Administrator |
| `gambar-2.16-sequence-sinkronisasi-data-unity.puml` | Gambar 2.16 | Sequence | Sinkronisasi Data Gedung dan Unity |
| `gambar-2.17-erd.puml` | Gambar 2.17 | ERD | Entity-Relationship Diagram (sesuai PRD) |
| `gambar-3.1-hierarki-prefab-unity.puml` | Gambar 3.1 | WBS | Hierarki Prefab Gedung dengan Child Pointer |

> Semua diagram memakai **palet netral** (abu-abu muda + garis abu gelap), tanpa warna brand.

## Diagram yang Diregenerasi karena Deprecated
Mengacu PRD terkini, beberapa diagram lama tidak lagi sesuai sistem sekarang dan telah diperbarui:
- **Arsitektur Sistem (2.9):** versi lama memakai alur kirim JSON `SendMessage` ke Unity dan interaksi klik Unity→React. Versi baru: Unity menarik data sendiri via `GET /api/unity/data`, komunikasi **satu arah** React→Unity (`NavigateTo`).
- **File `../diagram_alur_sistem.md` (Mermaid) DEPRECATED:** masih memuat modul lama `BuildingDataReceiver`, `BuildingClickHandler`, `ReceiveBuildingsData`, dan callback Unity→React (kini *out of scope*). Gunakan diagram pada folder ini sebagai gantinya.

## Cara Render ke PNG/SVG

### Opsi 1 — Tanpa instalasi (paling cepat)
1. Buka https://www.plantuml.com/plantuml/uml
2. Salin isi salah satu berkas `.puml`, tempel, lalu unduh PNG/SVG.

### Opsi 2 — VS Code (rekomendasi, sekalian preview)
1. Install extension **"PlantUML"** (jebbs.plantuml).
2. Buka berkas `.puml`, tekan `Alt + D` untuk preview.
3. `Ctrl + Shift + P` → **PlantUML: Export Current Diagram** → pilih PNG/SVG.
4. Memerlukan **Java** terpasang (atau set server render di setting extension).

### Opsi 3 — Command line (batch, semua sekaligus)
`plantuml.jar` **sudah tersedia di folder ini** dan PNG/SVG hasil render juga sudah dibuat. Untuk render ulang setelah mengedit, di folder ini jalankan:

```cmd
java -jar plantuml.jar -tpng *.puml
```

Untuk SVG (kualitas vektor, terbaik untuk dicetak di laporan):

```cmd
java -jar plantuml.jar -tsvg *.puml
```

## Konsistensi Visual
Semua diagram memakai palet warna seragam (navy `#0B2A4A` + aksen emas `#F4B400`) agar selaras saat disisipkan ke laporan. Ubah blok `skinparam` di tiap berkas bila ingin menyesuaikan warna/brand.

## Hal yang Perlu Diverifikasi
- **Gambar 2.14 (Integrasi Data Denah):** label cabang **Skenario A/B/C** disusun berdasarkan konteks "mitigasi ketersediaan data akademik eksternal". Sesuaikan teks tiap cabang dengan narasi A/B/C persis di laporan kamu.
- **Gambar 2.12 (Use Case):** aktor "Engine Unity" ditambahkan sebagai konsumen API (`/api/unity/data`, `/api/unity/names`). Hapus bila ingin fokus hanya pada User & Admin.
- Nama endpoint, partisipan, dan field disesuaikan dengan PRD & draf BAB II.
