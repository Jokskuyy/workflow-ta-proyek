# Diagram-as-Code Laporan Dwikhi

PlantUML menjadi sumber kanonik diagram laporan. Nomor dan judul gambar tidak ditulis di dalam kanvas karena dibentuk oleh caption Word.

## Diagram Aktif BAB II

| Berkas | Jenis | Isi |
| --- | --- | --- |
| `gambar-2.09-arsitektur-sistem.puml` | Arsitektur | Integrasi aset, data, React, API, dan Unity beserta ownership |
| `gambar-2.10-tahap-pengembangan.puml` | Activity | Alur perancangan aset dan data Dwikhi |
| `gambar-2.11-hierarki-prefab.puml` | Hierarki | Prefab, geometri, child `Pointer`, dan objek tujuan |
| `gambar-2.17-erd.puml` | ERD | Empat tabel inti rancangan Dwikhi |
| `gambar-2.16-sequence-sinkronisasi-data-unity.puml` | Sequence | Validasi identifier melalui alat pemeriksa, API, data, dan scene |

`gambar-3.1-hierarki-prefab-unity.puml` mendukung penjelasan implementasi BAB III.

## Kontrak Isi

1. React mengakses Supabase Auth dan CRUD secara langsung.
2. Unity runtime mengambil data melalui `/api/unity/data`.
3. `DatabaseSyncChecker` mengambil nama melalui `/api/unity/names`.
4. React mengirim perintah melalui `SendMessage` dan Unity mengirim callback penyelesaian normal.
5. ERD aktif hanya memuat `gedung`, `fasilitas`, `fakultas`, dan `program_studi`.
6. Diagram tidak memuat Use Case seluruh aplikasi, alur login melalui backend, data akademik eksternal, trigger audit, atau CRUD fakultas.

## Rendering

Render PNG dan SVG dari root folder diagram:

```powershell
java -Dfile.encoding=UTF-8 -jar plantuml.jar -tpng gambar-2.09-arsitektur-sistem.puml gambar-2.10-tahap-pengembangan.puml gambar-2.11-hierarki-prefab.puml gambar-2.16-sequence-sinkronisasi-data-unity.puml gambar-2.17-erd.puml gambar-3.1-hierarki-prefab-unity.puml
java -Dfile.encoding=UTF-8 -jar plantuml.jar -tsvg gambar-2.09-arsitektur-sistem.puml gambar-2.10-tahap-pengembangan.puml gambar-2.11-hierarki-prefab.puml gambar-2.16-sequence-sinkronisasi-data-unity.puml gambar-2.17-erd.puml gambar-3.1-hierarki-prefab-unity.puml
```

Semua diagram menggunakan Times New Roman dan UTF-8.
