# Diagram-as-Code — Laporan Tugas Akhir

Folder ini berisi diagram dalam format **PlantUML** (`.puml`). Penomoran mengikuti **DAFTAR GAMBAR pada DOCX final**.

| Berkas | Nomor (DOCX) | Jenis | Judul |
|---|---|---|---|
| `gambar-2.09-arsitektur-sistem.puml` | Gambar 2.9 | Component | Arsitektur Integrasi Dashboard Web, Supabase, dan Unity WebGL |
| `gambar-2.10-tahap-pengembangan.puml` | Gambar 2.10 | Activity | Tahapan Metode Prototyping pada Pengembangan Sistem |
| `../images/diagram_use_case_legenda.png` | Gambar 2.11 | Legenda | Legenda Simbol pada Use Case Diagram |
| `gambar-2.12-use-case-diagram.puml` | Gambar 2.12 | Use Case | Use Case Diagram Sistem Denah Virtual UPNVJ |
| `gambar-2.13-activity-pengelolaan-data-admin.puml` | Gambar 2.13 | Activity | Pengelolaan Data oleh Admin |
| `gambar-2.14-activity-integrasi-data-denah.puml` | Gambar 2.14 | Activity | Integrasi Data Denah 2D dan 3D |
| `gambar-2.15-sequence-autentikasi-admin.puml` | Gambar 2.15 | Sequence | Autentikasi Administrator |
| `gambar-2.16-sequence-sinkronisasi-data-unity.puml` | Gambar 2.16 | Sequence | Sinkronisasi Data Gedung dan Fasilitas dengan Unity |
| `gambar-2.17-erd.puml` | Gambar 2.17 | ERD | Entity-Relationship Diagram (sesuai PRD) |
| `gambar-3.1-hierarki-prefab-unity.puml` | Gambar 3.1 | WBS | Hierarki Prefab Gedung dengan Child Pointer |

> Semua diagram memakai **palet netral** (abu-abu muda + garis abu gelap), tanpa warna brand.

Judul dan nomor `Gambar X.X` tidak ditanamkan ke dalam kanvas diagram. Penomoran serta deskripsi gambar dibuat oleh caption Word agar nomor tetap mengikuti urutan otomatis laporan.

Gambar legenda Use Case merupakan aset kurasi manual yang disimpan pada `images/diagram_use_case_legenda.png`. Aset tersebut tidak boleh dirender ulang atau ditimpa dari `gambar-2.11-legenda-use-case.puml`; berkas PlantUML lama hanya dipertahankan sebagai arsip dan bukan sumber gambar aktif laporan.

## Diagram yang Diregenerasi karena Deprecated
Mengacu PRD terkini, beberapa diagram lama tidak lagi sesuai sistem sekarang dan telah diperbarui:
- **Arsitektur Sistem (2.9):** versi lama memakai alur kirim JSON data gedung melalui `SendMessage` dan callback klik objek. Versi aktif: Unity menarik data sendiri melalui `GET /api/unity/data`; React mengirim `NavigateTo`, sedangkan Unity mengembalikan completion JSON `unity_object_name` setelah tiba normal. Express hanya mengarah ke Umami sebagai jalur analitik opsional dan tidak menjadi perantara Supabase.
- **Use Case (2.12):** versi aktif hanya memuat fitur antarmuka yang terverifikasi. Tabel akreditasi publik dan CRUD fakultas telah dihapus; runtime dan tooling editor dipisahkan menurut endpoint masing-masing.
- **Activity Admin (2.13):** autentikasi serta CRUD mengalir langsung dari React ke Supabase. Audit dicatat oleh service aplikasi, bukan diklaim berasal dari trigger basis data.
- **Activity Integrasi (2.14):** skenario data akademik eksternal telah diganti dengan alur Denah 2D A*, pemuatan Unity WebGL, pengiriman perintah navigasi, dan notifikasi kedatangan.
- **File `../diagram_alur_sistem.md` (Mermaid) DEPRECATED:** masih memuat modul lama `BuildingDataReceiver`, `BuildingClickHandler`, dan `ReceiveBuildingsData`. Gunakan diagram pada folder ini sebagai gantinya.

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
Semua diagram memakai Times New Roman serta palet netral dengan latar putih, bidang abu-abu muda, dan garis abu-abu gelap agar konsisten saat disisipkan ke laporan.

## Hal yang Perlu Diverifikasi
- Gambar 2.12 membedakan Unity Runtime sebagai konsumen `/api/unity/data` dan tooling Unity Editor sebagai konsumen `/api/unity/names`.
- Gambar 2.14 harus tetap selaras dengan alur notifikasi kedatangan dan pemeriksaan tujuan aktif pada kode sumber React.
- Nama endpoint, partisipan, dan field disesuaikan dengan fakta proyek serta draf BAB II.
