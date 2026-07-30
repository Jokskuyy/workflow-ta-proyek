# Artefak SQL Laporan Dwikhi

Direktori ini menyimpan salinan byte-identik dari dua berkas dokumentasi database
yang diberikan pengguna. Berkas hanya digunakan sebagai sumber pembahasan dan
tidak dijalankan oleh pipeline laporan.

| Berkas repository | Sumber salinan | SHA-256 |
|---|---|---|
| `001_full_setup.sql` | `C:\dashboard-profile-upnvj\database\001_full_setup.sql` | `B440C517FC0289CBD6F546B4A3ED12D2ADC8E7B9F6CB8181F4FFF5A96681E61B` |
| `002_seed_data.sql` | `C:\dashboard-profile-upnvj\database\002_seed_data.sql` | `2A2BF7A97A566B75546C29D8FE3025EB0D9C4F682BF49BE2E323D603E1D57B2F` |

Peringatan: `001_full_setup.sql` memuat `DROP TABLE`, sedangkan
`002_seed_data.sql` memuat `TRUNCATE ... RESTART IDENTITY CASCADE`. Jangan
menjalankan kedua berkas hanya untuk membangun atau memvalidasi laporan.
