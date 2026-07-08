# Rencana Pengujian (Black Box & UAT)
## Integrasi Denah Virtual UPNVJ Kampus Pondok Labu (Dashboard Profil)

Dokumen ini berisi skenario pengujian fungsional (Black Box) dan panduan User Acceptance Testing (UAT) untuk disalin ke dokumen Laporan Tugas Akhir (.docx).

---

## 1. Pengujian Black Box (Validasi Fungsional Utama)
**Fokus**: Memastikan autentikasi & keamanan (RLS/audit), fungsi CRUD, mapping kategori fasilitas, serta integrasi API dan navigasi denah berjalan sesuai harapan, baik pada alur normal maupun alur gagal.

**Kesimpulan**: P = Pass (sesuai ekspektasi), F = Fail (tidak sesuai). Kolom **Hasil Aktual** diisi saat eksekusi.

### Prasyarat Pengujian
1. Basis data uji telah di-*seed* dengan data gedung/fasilitas yang jumlah dan kategorinya diketahui (dijadikan acuan verifikasi agregat pada BB-10).
2. Tersedia satu akun admin valid (authenticated) dan satu kondisi pengunjung publik (anon, tanpa sesi login).
3. Build Unity WebGL sudah termuat pada halaman denah dan endpoint API serverless (`/api/unity/data`, dll.) dapat diakses.
4. Nama objek acuan (`unity_object_name`) pada basis data konsisten dengan GameObject di scene (lowercase + underscore, *case-insensitive*).

### A. Skenario Autentikasi & Keamanan (Auth, RLS, Audit)
| ID | Skenario | Langkah Pengujian | Ekspektasi Hasil | Hasil Aktual | Kesimpulan |
|---|---|---|---|---|---|
| BB-01 | Login Admin Valid | Masuk ke panel admin dengan kredensial yang benar. | Autentikasi berhasil, pengguna diarahkan ke dashboard admin, sesi aktif. |  | [ ] |
| BB-02 | Login Admin Invalid | Masuk dengan password salah / akun tidak terdaftar. | Login ditolak dengan pesan error; tidak ada sesi yang terbentuk. |  | [ ] |
| BB-03 | Proteksi RLS pada Anon | Sebagai pengunjung publik (anon), coba operasi tulis (create/update/delete) ke tabel gedung/fasilitas via API/klien. | Operasi tulis ditolak oleh RLS; anon hanya dapat membaca (SELECT). Data tidak berubah. |  | [ ] |
| BB-04 | Pencatatan Audit Log | Sebagai admin authenticated, lakukan satu aksi CRUD, lalu periksa tabel audit log. | Baris audit log baru tercatat berisi aksi, tabel target, identitas user, dan timestamp. |  | [ ] |

### B. Skenario Manajemen Data (Admin Panel)
| ID | Skenario | Langkah Pengujian | Ekspektasi Hasil | Hasil Aktual | Kesimpulan |
|---|---|---|---|---|---|
| BB-05 | Validasi Dropdown Tipe Fasilitas | Buka form edit/tambah fasilitas, cek opsi dropdown tipe. | Dropdown menampilkan tepat 9 opsi (Laboratorium, Ruang Kuliah, Administrasi & Layanan, Lainnya, Ruang Kegiatan Mahasiswa, Auditorium & Aula, Perpustakaan & Ruang Baca, Fasilitas Ibadah, Fasilitas Olahraga). |  | [ ] |
| BB-06 | Integrasi Update Data | Ubah fasilitas bertipe lama ke salah satu dari 9 tipe baru, lalu simpan. | Data tersimpan di basis data tanpa *override* kosong/blank; nilai tipe terbarui. |  | [ ] |
| BB-07 | Validasi Input Tidak Lengkap (*negative*) | Simpan form fasilitas dengan field wajib dikosongkan atau nilai tidak valid. | Sistem menolak penyimpanan dengan pesan validasi; data lama tidak berubah. |  | [ ] |

### C. Skenario Public Dashboard
| ID | Skenario | Langkah Pengujian | Ekspektasi Hasil | Hasil Aktual | Kesimpulan |
|---|---|---|---|---|---|
| BB-08 | Hitungan Card Kategori | Bandingkan angka pada Card "Laboratorium" dan "Ruang Kuliah" dengan agregat data *seed*. | Angka sesuai agregat basis data (Lab termasuk Studio; Ruang Kuliah termasuk Ujian & Diskusi). |  | [ ] |
| BB-09 | Filter Modal Kategori | Klik card "Administrasi & Layanan". | Modal menampilkan ruang dosen, ruang rapat, fasilitas umum, dan ruang kegiatan mahasiswa tanpa ruangan *orphan* yang hilang. |  | [ ] |
| BB-10 | Pencarian Positif & Render Ikon | Ketik "BEM" atau "Senat" di search bar. | Muncul dropdown hasil dengan ikon sesuai kategori (mis. ikon "groups" untuk Ruang Kegiatan Mahasiswa). |  | [ ] |
| BB-11 | Pencarian Tanpa Hasil (*negative*) | Ketik kata acak/karakter khusus yang tidak cocok data mana pun. | Muncul *empty state* yang informatif; aplikasi tidak *crash* atau menampilkan hasil keliru. |  | [ ] |
| BB-12 | Peralihan Bahasa ID/EN | Ganti bahasa antarmuka dari Indonesia ke Inggris dan sebaliknya. | Label/teks UI berganti bahasa secara konsisten; data fasilitas tetap utuh. |  | [ ] |

### D. Skenario Integrasi Unity (API & Navigasi)
| ID | Skenario | Langkah Pengujian | Ekspektasi Hasil | Hasil Aktual | Kesimpulan |
|---|---|---|---|---|---|
| BB-13 | Endpoint Data Denah | Akses endpoint `/api/unity/data`. | Response JSON berhasil di-*fetch* dan memuat atribut `unity_object_name` yang sinkron (mis. `ds_201`, `ds_ukm_1`). |  | [ ] |
| BB-14 | Terima Perintah Navigasi (React→Unity) | Pilih sebuah ruangan (mis. Lab) di search bar React, amati denah 3D. | Unity menerima `unity_object_name` via `SendMessage` (satu arah) dan navigasi ke tujuan dimulai. |  | [ ] |
| BB-15 | Rute Terpendek & Label | Amati denah 3D setelah perintah navigasi. | Player dipandu via jalur terpendek (NavMesh); garis rute tergambar di lantai; label menampilkan **nama tampilan** (bukan kode internal) + jarak tersisa. |  | [ ] |
| BB-16 | Navigasi Berhenti Otomatis | Gerakkan/ikuti player mendekati tujuan hingga di bawah `stopDistance`. | Navigasi berhenti otomatis; garis rute & label dibersihkan tanpa aksi manual. |  | [ ] |
| BB-17 | Robustesitas `unity_object_name` (*edge*) | (a) Kirim nama dengan kapitalisasi berbeda; (b) pilih ruangan yang belum punya GameObject padanan. | (a) Tetap cocok karena *case-insensitive*; (b) ditangani aman (tanpa navigasi keliru / *crash*), idealnya dengan penanda "lokasi belum tersedia". |  | [ ] |

> **Catatan arsitektur:** Objek 3D di WebGL **tidak bisa diklik** untuk memunculkan info (tidak ada callback Unity→React — *out of scope* di PRD). Informasi detail gedung/ruangan ditampilkan di sisi **dashboard publik / hasil pencarian React**, bukan di dalam kanvas Unity. `unity_object_name` adalah jembatan tunggal antara baris basis data dan GameObject di scene.

---

## 2. User Acceptance Testing (UAT)
**Fokus**: Memastikan sistem teruji dan disetujui oleh end-user serta validator akademik.
*Catatan: Format di bawah dipindahkan ke tabel Microsoft Word (.docx) untuk lembar persetujuan/kuesioner fisik.*

### Daftar Partisipan UAT
1. **Dosen Penguji**: Dr. Widya Cholil, Kharisma Wiati Gusti
2. **Dosen Pembimbing**: Dr. Ridwan Raafi'udin, Novi Trisman Hadi
3. **Representatif End-User**: Humas UPNVJ
4. **Representatif Administrator**: Admin Prodi

### Identitas Responden
| Field | Isian |
|---|---|
| Nama | |
| Peran (Penguji/Pembimbing/End-User/Administrator) | |
| Instansi/Unit | |
| Tanggal Pengujian | |
| Tanda Tangan | |

### Form Evaluasi UAT (Draft Kuesioner)
*Skala Penilaian: 1 (Sangat Kurang) – 5 (Sangat Baik). Setiap butir memetakan satu dimensi kualitas sistem.*

| No | Dimensi | Pernyataan | Nilai (1–5) |
|---|---|---|---|
| 1 | Kemudahan Administrasi | Antarmuka panel admin mudah dipahami untuk manajemen data gedung dan ruangan. | |
| 2 | Kesesuaian Informasi | Klasifikasi kategori ruangan pada dashboard publik merepresentasikan tata ruang nyata kampus secara akurat. | |
| 3 | Navigasi Spasial | Pencarian ruangan dari dashboard berhasil memandu navigasi denah 3D (jalur terpendek) ke lokasi yang benar. | |
| 4 | Kejelasan Visualisasi 3D | Visualisasi denah 3D (rute, label, orientasi) jelas dan mudah diikuti. | |
| 5 | Kecepatan Respon | Antarmuka dan denah 3D merespons dengan cepat tanpa jeda yang mengganggu. | |
| 6 | Konsistensi Data | Informasi detail gedung/ruangan pada dashboard sesuai dengan data yang diinput via panel admin. | |
| 7 | UX Keseluruhan | Secara keseluruhan aplikasi memudahkan navigasi informasi fasilitas dan ruang fisik bagi sivitas akademika UPNVJ. | |

**Saran / Masukan Terbuka:**

_(isian bebas untuk catatan kualitatif, temuan bug, atau usulan perbaikan)_

### Pengolahan Hasil
Skor kepuasan dihitung menggunakan rumus persentase indeks kepuasan atas total nilai seluruh responden, lalu dipetakan ke rentang interpretasi (mis. Sangat Baik/Baik/Cukup/Kurang). Jumlah responden, tanggal pelaksanaan, dan skor akhir diisi setelah pengujian selesai [TBD: Jumlah Responden] [TBD: Tanggal Pengujian] [TBD: Skor Kepuasan UAT].
