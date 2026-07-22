### 4.2.1 Pengujian Fungsional (Black Box Testing)

Pengujian fungsional dilakukan menggunakan metode *Black Box Testing* dengan pendekatan *Equivalence Partitioning* dan *Boundary Value Analysis*. Pengujian ini bertujuan memastikan seluruh alur fungsional, baik dari sisi Administrator (Dashboard) maupun Pengguna Publik (Integrasi WebGL), berjalan sesuai dengan spesifikasi kebutuhan sistem tanpa melihat struktur kode internal. 

Tabel 4.x menampilkan 18 skenario pengujian utama yang dilakukan oleh tim pengembang terhadap purwarupa akhir sistem.

**Tabel 4.x Skenario dan Hasil Pengujian Fungsional (Black Box Testing)**

| No | Modul / Fitur | Skenario Pengujian | Hasil yang Diharapkan | Hasil Sebenarnya | Status |
|----|---------------|-------------------|----------------------|------------------|--------|
| 1 | Autentikasi | Login menggunakan username dan password admin yang valid. | Sistem mengarahkan pengguna ke halaman Dashboard Admin utama dan memberikan sesi token. | [Sesuai Harapan] | **Valid** |
| 2 | Autentikasi | Login menggunakan password yang salah atau kosong. | Sistem menolak akses dan menampilkan pesan error peringatan kredensial tidak valid. | [Sesuai Harapan] | **Valid** |
| 3 | Autentikasi | Logout dari sistem melalui dashboard admin. | Sesi token dihapus, dan pengguna dikembalikan ke halaman publik/login tanpa bisa mengakses dashboard admin lagi. | [Sesuai Harapan] | **Valid** |
| 4 | CRUD Gedung | Menambahkan data Gedung baru dengan mengisi form secara lengkap (termasuk *unity_object_name*). | Data gedung berhasil disimpan ke tabel `gedung` Supabase dan muncul di tabel dashboard admin. | [Sesuai Harapan] | **Valid** |
| 5 | CRUD Gedung | Mengosongkan form nama gedung saat proses tambah data. | Sistem menolak *submit* dan menampilkan validasi error pada form (wajib diisi). | [Sesuai Harapan] | **Valid** |
| 6 | CRUD Gedung | Melakukan proses Update (Edit) deskripsi dan foto gedung yang sudah ada. | Perubahan langsung tersimpan di *database* dan tabel dashboard ter-refresh dengan data baru. | [Sesuai Harapan] | **Valid** |
| 7 | CRUD Gedung | Melakukan proses Delete (Hapus) gedung yang memiliki relasi dengan tabel fasilitas. | Menampilkan modal konfirmasi. Jika dihapus, data terhapus secara *cascade* atau memberikan peringatan relasi data. | [Sesuai Harapan] | **Valid** |
| 8 | CRUD Fasilitas | Menambahkan ruangan fasilitas baru di dalam spesifik gedung (misal: Ruang Dosen). | Fasilitas tersimpan, terikat dengan `id_gedung` yang tepat, dan memiliki properti lantai yang sesuai. | [Sesuai Harapan] | **Valid** |
| 9 | Audit Log | Admin melakukan aksi hapus fasilitas, lalu memeriksa tabel Audit Logs. | Sistem mencatat rekam jejak (*trigger database*) berupa waktu hapus, aktor, dan data lama yang dihapus. | [Sesuai Harapan] | **Valid** |
| 10 | Dashboard Publik | Mengakses halaman utama publik (`/`). | Sistem berhasil memuat komponen antarmuka React secara utuh tanpa error CORS. | [Sesuai Harapan] | **Valid** |
| 11 | Pencarian Data | Pengguna publik mengetikkan nama fasilitas pada *search bar*. | Muncul *dropdown/modal* saran pencarian yang sesuai dengan *keyword* fasilitas. | [Sesuai Harapan] | **Valid** |
| 12 | Integrasi 3D | Memuat modul Denah Virtual Unity WebGL di halaman utama. | Loading bar berjalan progresif hingga kanvas Unity WebGL tampil interaktif di *browser*. | [Sesuai Harapan] | **Valid** |
| 13 | Sinkronisasi Data 3D | Unity melakukan HTTP GET Request otomatis ke API `/api/unity/data` saat runtime di awal muat. | Sistem backend mengembalikan response JSON lengkap yang berisi pemetaan gedung dan `unity_object_name`. | [Sesuai Harapan] | **Valid** |
| 14 | Navigasi 3D | Mengklik tombol "Tunjukkan Lokasi" atau icon map pada daftar pencarian fasilitas di panel web React. | React mengirim fungsi *SendMessage* ke Unity, kamera Unity bergerak (*pathfinding*) menuju *pointer* objek tujuan. | [Sesuai Harapan] | **Valid** |
| 15 | Responsivitas UI | Membuka *dashboard* panel pada resolusi *mobile* (contoh: ukuran *smartphone*). | Panel *overlay* web menyesuaikan *layout* (menjadi panel geser di bawah atau *hamburger menu*). | [Sesuai Harapan] | **Valid** |
| 16 | Kontrol Mobile 3D | Melakukan interaksi sentuh *Virtual Joystick* pada modul Unity WebGL lewat peramban ponsel. | Kamera Unity merespons *joystick* secara akurat (gerak rotasi dan maju-mundur). | [Sesuai Harapan] | **Valid** |
| 17 | Sinkronisasi Tools | Menjalankan "Check Database Sync" dari Unity Editor. | *Database Sync Checker* berhasil menarik API `/api/unity/names` dan memvalidasi `unity_object_name` di *Hierarchy*. | [Sesuai Harapan] | **Valid** |
| 18 | Analytics Proxy | Membuka halaman dan melakukan navigasi antar halaman (*routing*). | Skrip pelacakan mengirim data secara diam-diam ke Vercel Serverless `/api/umami`, yang diteruskan secara *proxy* ke Umami Backend tanpa memblokir peramban pengguna. | [Sesuai Harapan] | **Valid** |

**Kesimpulan Pengujian Fungsional:**
Berdasarkan pengujian *Black Box* dengan 18 skenario komprehensif pada tabel di atas, seluruh fitur kunci mulai dari keamanan autentikasi, manajemen CRUD *database*, hingga interaksi *cross-platform* (React-Unity) merespons sesuai dengan desain kebutuhan spesifikasi. Modul berhasil mencapai persentase keberhasilan 100% (*Pass Rate*), menandakan sistem siap untuk tahap pengujian tingkat lanjut, yakni *User Acceptance Test* (UAT).
