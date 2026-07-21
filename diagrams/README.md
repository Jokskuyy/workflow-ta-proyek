# Diagram PlantUML Laporan Faiz

PlantUML pada folder ini merupakan sumber kanonik diagram laporan. Judul dan nomor gambar tidak ditulis di dalam kanvas karena keduanya dibentuk oleh caption Word.

## Enam diagram aktif

| Sumber | Jenis | Caption laporan |
|---|---|---|
| `gambar-2.10-tahap-pengembangan.puml` | Activity | Tahap Pengembangan Modul Simulator dan Engine |
| `gambar-2.09-arsitektur-sistem.puml` | Arsitektur | Arsitektur Integrasi Sistem dan Unity WebGL |
| `gambar-2.12-use-case-diagram.puml` | Use Case | Use Case Modul Unity WebGL |
| `gambar-2.14-activity-integrasi-data-denah.puml` | Activity | Activity Diagram Integrasi Denah 2D dan 3D |
| `gambar-2.16-sequence-sinkronisasi-data-unity.puml` | Sequence | Sequence Diagram Integrasi Data dan Penyelesaian Navigasi |
| `gambar-2.18-alur-navmesh-rendering.puml` | Activity | Activity Diagram Navigasi NavMesh dan Rendering Rute |

Diagram lain pada folder ini merupakan sumber historis atau digunakan oleh laporan anggota tim lain. Diagram legenda use case telah dihapus karena tidak menambah bukti rancangan modul Faiz.

## Kontrak sistem aktif

1. React mengakses Supabase Auth dan CRUD secara langsung.
2. Denah 2D menggunakan jaringan graf dan algoritma A*.
3. Unity runtime mengambil data melalui `GET /api/unity/data`.
4. `DatabaseSyncChecker` pada Unity Editor menggunakan `GET /api/unity/names`.
5. React mengirim `NavigateTo`, `StopNavigation`, `SetSpawn`, dan `SetDevice` melalui `SendMessage`.
6. Unity mengirim `OnNavigationCompleted` hanya setelah navigasi selesai secara normal. Pembatalan dan target yang tidak ditemukan tidak menghasilkan callback kedatangan.
7. Express dan Umami hanya membentuk jalur analitik opsional.

## Aturan visual

Semua teks diagram menggunakan Times New Roman. Kanvas tidak boleh memuat nomor gambar, hash commit, path lokal, API SIK, data dosen/mahasiswa, akreditasi publik, CRUD fakultas, atau alur login React melalui backend.

## Render

Jalankan dari folder `diagrams/`:

```powershell
java -jar plantuml.jar -charset UTF-8 -tpng *.puml
java -jar plantuml.jar -charset UTF-8 -tsvg *.puml
```

Setelah render, salin PNG enam diagram aktif ke nama aset yang ditentukan oleh `images/manifest.json`. SVG tetap disimpan bersama sumber PlantUML untuk pemeriksaan kualitas vektor.
