# Requirements — Agentic Content Generation

## Tujuan

Menambahkan generator konten bebas berbasis AI sebagai tahap opsional sebelum
pipeline Markdown/DOCX, tanpa memberi AI wewenang untuk mengarang fakta,
sitasi, struktur, atau menimpa tulisan manusia.

## Requirements

1. Generator harus terpisah dari `build_pipeline.py` dan `run_alur()` sehingga
   build dokumen tetap deterministik dan tidak pernah memanggil provider AI.
2. Mode default harus menghasilkan proposal dan unified diff tanpa menulis
   `Tugas_Akhir_Draft.md`. Penulisan hanya boleh terjadi dengan otorisasi
   eksplisit `--apply`.
3. Generator hanya boleh berjalan pada branch anggota yang dikenal:
   `laporan/iman`, `laporan/dwikhi`, atau `laporan/faiz`. Branch lain harus
   menghasilkan status `HELD` sebelum draf dibaca atau provider dipanggil.
4. Provider harus mengembalikan objek terstruktur berisi `section_id`, body
   Markdown, fakta yang dipakai, sitasi yang dipakai, klaim belum terverifikasi,
   dan catatan reviewer.
5. Nilai fakta yang dideklarasikan harus sama persis dengan
   `project_facts.json`; fakta yang tidak tersedia hanya boleh ditulis sebagai
   `[TBD: ...]`.
6. Sitasi kandidat harus benar-benar muncul pada body, dideklarasikan dalam
   metadata kandidat, dan memiliki entri pada Daftar Pustaka draf. Sumber baru
   tidak boleh dibuat otomatis.
7. Klaim belum terverifikasi harus dideklarasikan dan ditandai
   `[BUTUH SITASI]` pada body.
8. Kandidat tidak boleh membuat heading, page break, bullet, caption/aset
   Gambar/Tabel baru, rujukan objek menggantung/lintas bab, atau istilah baru
   yang membuat draf tidak konsisten.
9. Apply hanya boleh menambahkan body ke subbab target. Baris lama dan konten
   manual tidak boleh dihapus atau diganti. Kandidat identik yang sudah ada
   harus menjadi no-op.
10. Tepat sebelum apply, sistem harus membaca ulang draf dan membatalkan
    penulisan bila hash berubah sejak request dibuat.
11. Konteks yang dikirim ke provider harus diminimalkan. Fakta proyek hanya
    dikirim untuk key yang dipilih eksplisit melalui `--fact`; token provider
    tidak boleh disimpan pada repository.
12. Sistem harus mendukung respons JSON lokal dari AI agent mana pun dan
    adaptor HTTP JSON yang tidak terikat vendor.
