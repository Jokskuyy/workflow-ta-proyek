# Kerangka 4 Bab Laporan TA Proyek (UPNVJ FIK 2025)

> Sumber kanonik tunggal, **selaras dengan sistem terkini** (lihat `PRD_Konsolidasi_TA.md`).
> Dirujuk oleh `write-ta-proyek` dan `docx-ta-proyek`. Jangan menyalin ulang ke SKILL.md.
>
> Catatan: penekanan tiap sub-bab dapat berbeda per peran/branch
> (lihat `laporan-tim/<peran>/outline-laporan.md`). Struktur dasar tetap sama.

## BAB I PENDAHULUAN
1. 1.1 Latar Belakang — konteks Smart Campus, kesulitan navigasi spasial, peran kolaboratif.
2. 1.2 Identifikasi Masalah — daftar bernomor.
3. 1.3 Batasan Masalah — ruang lingkup Kampus Pondok Labu, batas kontribusi setiap peran, jalur autentikasi/data yang digunakan, dan batas integrasi WebGL.
4. 1.4 Tujuan dan Manfaat — 1.4.1 Tujuan, 1.4.2 Manfaat.
5. 1.5 Jadwal Kegiatan — Gantt/tabel.
6. 1.6 Sistematika Penulisan.

## BAB II RANCANGAN PROYEK
1. 2.1 Observasi — 2.1.1 Observasi Lapangan, 2.1.2 Analisis Sistem Berjalan, 2.1.3 Wawancara Stakeholder.
2. 2.2 Usulan Solusi
   a. 2.2.1 Identifikasi Kebutuhan Fungsional (Public Dashboard, Admin Panel, API/bridge, deployment dan operasional).
   b. 2.2.2 Identifikasi Kebutuhan Teknis — React SPA, **Vercel Serverless API (Node.js)**, Supabase, Unity WebGL, serta jalur analitik aktif yang terverifikasi. Express.js dan Umami hanya disebut aktif apabila ada bukti; pada laporan Iman keduanya merupakan jalur operasional opsional, bukan API atau analitik UI utama.
   c. 2.2.3 Identifikasi Kebutuhan Non-Fungsional — pemuatan adaptif, loading feedback, cache, evaluasi Lighthouse, mobile-first, keamanan (JWT/RLS/rate limiter), privasi, usabilitas/aksesibilitas, dan keterpeliharaan. Jangan memakai target waktu muat tetap tanpa artefak pengukuran.
3. 2.3 Rancangan Proyek
   a. 2.3.1 Rencana Pengembangan (Prototyping).
   b. 2.3.2 Perancangan Information Architecture (IA).
   c. 2.3.3 Perancangan UML (Use Case, Activity, Sequence).
   d. 2.3.4 Perancangan Integrasi Keamanan dan Analitik. Jelaskan batas antara rancangan skema/RLS/trigger dan integrasi yang mengonsumsinya; nyatakan jalur analitik aktif serta jalur opsional berdasarkan artefak.
   e. 2.3.5 Perancangan data sesuai fokus peran. Laporan perancang database dapat memuat ERD lengkap; laporan integrator memakai Kontrak Data Integrasi dan mengatribusikan ERD, relasi, RLS, serta trigger kepada pemiliknya.
   f. 2.3.6 Perancangan Antarmuka (mockup Public Dashboard & Admin Panel).
4. 2.4 Rencana Pengujian Proyek — API/integration test, pengujian web, Black Box, UAT, Lighthouse, dan pemeriksaan deployment sesuai ownership.

## BAB III IMPLEMENTASI PROYEK
1. 3.1 Profil Mitra — 3.1.1 Nama, 3.1.2 Deskripsi, 3.1.3 Hubungan.
2. 3.2 Metode Implementasi
   a. 3.2.1 Implementasi Back-end — Vercel Serverless Functions (Node.js), Supabase client, kontrak endpoint, serta respons/error. Skema, SQL, RLS, dan trigger hanya dibahas oleh peran pemiliknya.
   b. 3.2.2 Implementasi Front-end — React SPA, Public Dashboard, Admin Panel, autentikasi/protected route, CRUD, pencarian/bantuan/tutorial, serta pemuatan WebGL adaptif.
   c. 3.2.3 Implementasi Integrasi Front-end, Back-end, dan Unity WebGL — React memakai Supabase Auth/SDK langsung, Unity menarik `/api/unity/data`, `/api/unity/names` melayani tooling editor, React mengirim `unity_object_name` melalui `SendMessage`, dan completion JSON dari Unity divalidasi terhadap tujuan aktif sebelum popup ditampilkan.
   d. 3.2.4 Implementasi deployment dan operasional — hosting, environment variables, aset WebGL, header/cache, health monitoring, dan kesiapan integrasi institusional.
3. 3.3 Konfigurasi dan Kontrak Operasional Sistem
   a. 3.3.1 Environment variables dan kontrak identifier `unity_object_name`.
   b. 3.3.2 Konfigurasi analitik dan layanan operasional sesuai jalur aktif; Express/Umami dapat didokumentasikan sebagai alternatif apabila tidak menjadi dependensi UI aktif.
   c. 3.3.3 Hosting, header/cache, aset WebGL, endpoint health, dan batas ownership proses build Unity.
4. 3.4 Laporan Implementasi Proyek
   a. 3.4.1 Logbook Implementasi Proyek.
   b. 3.4.2 Hasil dan bukti implementasi sesuai kontrak API/integrasi.
   c. 3.4.3 Hasil dan bukti antarmuka terpilih; hindari tangkapan layar berulang untuk setiap modal atau state yang serupa.
5. 3.5 Hasil Pengujian Proyek
   a. 3.5.1 Pengujian otomatis web dan API sesuai artefak yang tersedia.
   b. 3.5.2 Black Box Testing.
   c. 3.5.3 Lighthouse Testing / Performance sebagai data lab, bukan data pengguna nyata.
   d. 3.5.4 User Acceptance Test (UAT).
   e. 3.5.5 Tindak lanjut UAT dengan status bukti dan retest yang eksplisit.

## BAB IV PENUTUP
1. 4.1 Kesimpulan.
2. 4.2 Saran (prospek keberlanjutan).
