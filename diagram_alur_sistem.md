# Diagram Mermaid Lama (Tidak Digunakan)

Berkas ini dipertahankan hanya sebagai penanda migrasi. Diagram Mermaid yang pernah berada di sini tidak lagi menjadi sumber laporan karena memuat kontrak integrasi lama.

Sumber diagram kanonik berada di folder `diagrams/` dalam format PlantUML. Enam diagram aktif untuk laporan Faiz adalah:

1. `gambar-2.10-tahap-pengembangan.puml`;
2. `gambar-2.09-arsitektur-sistem.puml`;
3. `gambar-2.12-use-case-diagram.puml`;
4. `gambar-2.14-activity-integrasi-data-denah.puml`;
5. `gambar-2.16-sequence-sinkronisasi-data-unity.puml`; dan
6. `gambar-2.18-alur-navmesh-rendering.puml`.

Kontrak aktif memisahkan perintah React ke Unity melalui `SendMessage` dan callback penyelesaian normal dari Unity ke React melalui `OnNavigationCompleted`. Pembatalan dan target yang tidak ditemukan tidak menghasilkan callback kedatangan.
