-- =============================================================================
-- SEEDING DATA UPNVJ PONDOK LABU
-- =============================================================================
-- Jalankan SETELAH 001_full_setup.sql
-- Aman untuk di-run ulang (akan TRUNCATE dulu)
-- =============================================================================

-- =============================================================================
-- CLEAN EXISTING DATA (safe re-run)
-- =============================================================================
TRUNCATE public.fasilitas, public.program_studi, public.fakultas, public.gedung RESTART IDENTITY CASCADE;

-- =============================================================================
-- INSERT GEDUNG
-- =============================================================================

INSERT INTO public.gedung (nama_gedung, deskripsi_gedung, lokasi, jumlah_lantai, foto_url, unity_object_name) VALUES
('Gedung Rektorat (jenderal soedirman)', 'Gedung rektorat dan pusat administrasi universitas', 'Area depan kampus utama Pondok Labu', 4, 'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/gedung/gedung_gedung_rektorat.webp', 'soedirman'),
('Gedung DR. Soepomo', 'Gedung perpustakaan pusat dan laboratorium terpadu universitas', 'Zona pelayanan akademik', 4, 'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/gedung/gedung_gedung_dr_soepomo.webp', 'soepomo'),
('Gedung Dr. Wahidin Sudiro Husodo', 'Gedung utama Fakultas Kedokteran', 'Klaster Fakultas Kedokteran', 4, 'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/gedung/gedung_gedung_dr_wahidin_sudiro_husodo.webp', 'wahidin_sudiro_husodo'),
('Gedung Dr. Cipto Mangunkusumo', 'Gedung penunjang laboratorium dan skills lab Fakultas Kedokteran', 'Klaster Fakultas Kedokteran', 4, 'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/gedung/gedung_gedung_dr_cipto_mangunkusumo.webp', 'cipto_mangunkusumo'),
('Gedung Abdul Rahman Saleh', 'Gedung fasilitas pendukung Fakultas Kedokteran dan laboratorium klinis', 'Perbatasan FK dan FISIP', 4, 'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/gedung/gedung_gedung_abdul_rahman_saleh.webp', 'abdul_rahman_saleh'),
('Gedung Ki Hadjar Dewantara', 'Gedung Fakultas Ilmu Komputer dan laboratorium komputer', 'Klaster Fakultas Ilmu Komputer', 4, NULL, 'ki_hadjar_dewantara'),
('Gedung Muh. Husni Thamrin', 'Gedung Fakultas Ekonomi dan Bisnis', 'Klaster Fakultas Ekonomi dan Bisnis', 4, 'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/gedung/gedung_gedung_moh_husni_thamrin.webp', 'thamrin'),
('Gedung Muhammad Yamin', 'Gedung Fakultas Ilmu Sosial dan Ilmu Politik', 'Klaster FISIP', 4, 'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/gedung/gedung_gedung_muhammad_yamin.webp', 'yamin'),
('Gedung Yos Sudarso', 'Gedung Fakultas Hukum Program Sarjana', 'Klaster Fakultas Hukum', 4, 'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/gedung/gedung_gedung_yos_sudarso.webp', 'yos_sudarso'),
('Gedung RA Kartini', 'Gedung Fakultas Hukum Pascasarjana', 'Klaster Fakultas Hukum', 4, 'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/gedung/gedung_gedung_ra_kartini.webp', 'kartini'),
('Parkir Depan UPNVJ', 'Gedung parkir bertingkat untuk kendaraan mahasiswa dan staf', 'Sisi depan kampus', 4, 'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/gedung/gedung_gedung_parkir_depan_upnvj.jpg', 'parkir_depan'),
('Parkir Belakang UPNVJ', 'Gedung parkir bertingkat untuk kendaraan mahasiswa dan staf', 'Sisi belakang kampus', 4, 'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/gedung/gedung_gedung_parkir_belakang_upnvj.jpg', 'parkir_belakang'),
('Gedung Dewi Sartika', 'Gedung Fakultas Ilmu Komputer', 'Klaster Fakultas Ilmu Komputer', 4, 'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/gedung/gedung_gedung_dewi_sartika.webp', 'dewi_sartika'),
('Lapangan Upacara', 'Tempat upacara dan parkir mobil apabila sedang tidak dipakai', 'Area tengah kampus', 1, 'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/gedung/gedung_lapangan_upacara.jpg', 'lapangan_upacara'),
('Gedung Kuliah dan Kegiatan Mahasiswa', 'Gedung ruang kuliah dan sekretariat UKM', 'Area belakang kampus', 8, NULL, 'ukm'),
('Gedung Soetomo', 'Gedung perpustakaan utama kampus, ruang organisasi mahasiswa, dan Unit Kegiatan Mahasiswa UPN Veteran Jakarta', 'Kampus Pondok Labu', 4, NULL, 'soetomo'),
('Lapangan Basket', 'Lapangan basket outdoor untuk kegiatan olahraga mahasiswa dan staf', 'Area belakang kampus', 1, NULL, 'lapangan_basket'),
('Parkir Hukum', 'Parkir untuk kendaraan mahasiswa dan staf Fakultas Hukum', 'Sisi belakang kampus', 4, NULL, 'parkir_hukum'),
('Kantin', 'Kantin dan tempat makan mahasiswa, staf, dan dosen', 'Area samping kampus', 1, NULL, 'kantin');
-- =============================================================================
-- INSERT FAKULTAS
-- =============================================================================

INSERT INTO public.fakultas (nama_fakultas, deskripsi_fakultas, email, website, id_gedung_utama) VALUES
(
    'Fakultas Kedokteran',
    'Fakultas pendidikan kedokteran dan kesehatan',
    'tatausahafkupn@upnvj.ac.id',
    'https://fk.upnvj.ac.id',
    3
),

(
    'Fakultas Ekonomi dan Bisnis',
    'Fakultas bidang ekonomi, akuntansi, dan manajemen',
    'feb@upnvj.ac.id',
    'https://feb.upnvj.ac.id',
    7
),

(
    'Fakultas Ilmu Komputer',
    'Fakultas bidang teknologi informasi dan komputer',
    'fik@upnvj.ac.id',
    'https://new-fik.upnvj.ac.id',
    6
),

(
    'Fakultas Hukum',
    'Fakultas bidang ilmu hukum dan peradilan',
    'fh@upnvj.ac.id',
    'https://hukum.upnvj.ac.id',
    9
),

(
    'Fakultas Ilmu Sosial dan Ilmu Politik',
    'Fakultas bidang komunikasi, hubungan internasional, dan politik',
    'fisip@upnvj.ac.id',
    'https://fisip.upnvj.ac.id',
    8
),

(
    'Fakultas Teknik',
    'Fakultas bidang teknik industri, mesin, dan perkapalan',
    'ft@upnvj.ac.id',
    'https://ft.upnvj.ac.id',
    NULL
),

(
    'Fakultas Ilmu Kesehatan',
    'Fakultas bidang keperawatan dan kesehatan masyarakat',
    'fikes@upnvj.ac.id',
    'https://fikes.upnvj.ac.id',
    NULL
);

-- =============================================================================
-- INSERT PROGRAM STUDI
-- =============================================================================

INSERT INTO public.program_studi (nama_prodi, jenjang, id_fakultas, akreditasi) VALUES
('Perbankan dan Keuangan', 'Vokasi', 2, 'Unggul'),
('Akuntansi', 'Vokasi', 2, 'Unggul'),
('Manajemen', 'Sarjana', 2, 'Unggul'),
('Akuntansi', 'Sarjana', 2, 'Unggul'),
('Ekonomi Pembangunan', 'Sarjana', 2, 'Baik Sekali'),
('Ekonomi Syariah', 'Sarjana', 2, 'Unggul'),
('Manajemen', 'Magister', 2, 'B'),
('Akuntansi', 'Magister', 2, 'Baik Sekali'),
('Kedokteran', 'Sarjana', 1, 'Unggul'),
('Farmasi', 'Sarjana', 1, 'Baik Sekali'),
('Biologi', 'Sarjana', 1, 'Izin Operasional'),
('Pendidikan Profesi Dokter', 'Profesi', 1, 'Unggul'),
('Apoteker', 'Profesi', 1, 'Izin Operasional'),
('Sains Biomedis', 'Magister', 1, 'Izin Operasional'),
('Radiologi', 'Spesialis', 1, 'Izin Operasional'),
('Sistem Informasi', 'Vokasi', 3, 'B'),
('Informatika', 'Sarjana', 3, 'Unggul'),
('Sistem Informasi', 'Sarjana', 3, 'Baik Sekali'),
('Sains Data', 'Sarjana', 3, 'Ijin Operasional'),
('Hukum', 'Sarjana', 4, 'Unggul'),
('Hukum Bisnis', 'Sarjana', 4, 'Ijin Operasional'),
('Hukum', 'Magister', 4, 'Baik Sekali'),
('Hukum', 'Doktor', 4, 'Ijin Operasional'),
('Ilmu Komunikasi', 'Sarjana', 5, 'Unggul'),
('Hubungan Internasional', 'Sarjana', 5, 'B'),
('Ilmu Politik', 'Sarjana', 5, 'Baik Sekali'),
('Sains Informasi', 'Sarjana', 5, 'Baik'),
('Kajian Film, Televisi dan Media', 'Sarjana', 5, 'Izin Operasional'),
('Hubungan Internasional', 'Magister', 5, 'Baik'),
('Ilmu Politik', 'Magister', 5, 'Baik'),
('Ilmu Komunikasi', 'Magister', 5, 'Baik Sekali'),
('Teknik Mesin', 'Sarjana', 6, 'Unggul'),
('Teknik Industri', 'Sarjana', 6, 'Unggul'),
('Teknik Perkapalan', 'Sarjana', 6, 'Unggul'),
('Teknik Elektro', 'Sarjana', 6, 'Unggul'),
('Keperawatan', 'Vokasi', 7, 'Unggul'),
('Fisioterapi', 'Vokasi', 7, 'Unggul'),
('Kesehatan Masyarakat', 'Sarjana', 7, 'Unggul'),
('Gizi', 'Sarjana', 7, 'Unggul'),
('Keperawatan', 'Sarjana', 7, 'Baik Sekali'),
('Fisioterapi', 'Sarjana', 7, 'Unggul'),
('Pendidikan Profesi Ners', 'Profesi', 7, 'Baik Sekali'),
('Kesehatan Masyarakat', 'Magister', 7, 'Baik'),
('Keperawatan', 'Magister', 7, 'Ijin Operasional');

-- =============================================================================
-- INSERT FASILITAS
-- =============================================================================

INSERT INTO public.fasilitas (nama_fasilitas, deskripsi_fasilitas, tipe_fasilitas, lantai, foto_url, id_gedung, unity_object_name) VALUES
-- Gedung 3: Gedung Dr. Wahidin Sudiro Husodo
(
    'Ilmu Kesehatan Matra/UPNVERI',
    $$Ruang Ilmu Kesehatan Matra/UPNVERI di lantai 1 Gedung Dr. Wahidin Sudiro Husodo untuk kegiatan akademik dan operasional Fakultas Kedokteran UPNVJ.$$,
    'Lainnya',
    1,
    NULL,
    3,
    'wsh_upn_veri'
),
(
    'Medical Quality Assurance (MQA)',
    $$Unit Medical Quality Assurance (MQA) untuk penjaminan mutu pendidikan medis Fakultas Kedokteran UPNVJ di lantai 1 Gedung Dr. Wahidin Sudiro Husodo.$$,
    'Lainnya',
    1,
    NULL,
    3,
    'wsh_mqa'
),
(
    'Pusat Stem Cell dan Tissue Engineering Research Centre',
    $$Pusat penelitian sel punca (stem cell) dan rekayasa jaringan (tissue engineering) di Fakultas Kedokteran UPNVJ.$$,
    'Lainnya',
    1,
    NULL,
    3,
    'wsh_stem_cell'
),
(
    'Ruang BEM FK UPNVJ',
    $$Ruang organisasi Badan Eksekutif Mahasiswa (BEM) Fakultas Kedokteran UPNVJ di lantai 1 Gedung Dr. Wahidin Sudiro Husodo.$$,
    'Ruang Kegiatan Mahasiswa',
    1,
    NULL,
    3,
    'wsh_bem'
),
(
    'Ruang Dosen FK UPNVJ',
    $$Ruang kerja dan aktivitas dosen Fakultas Kedokteran UPNVJ.$$,
    'Administrasi & Layanan',
    1,
    NULL,
    3,
    'wsh_ruang_dosen_fk'
),
(
    'Ruang Program Studi Spesialis',
    $$Ruang pengelolaan akademik Program Studi Spesialis Fakultas Kedokteran UPNVJ di lantai 1 Gedung Dr. Wahidin Sudiro Husodo.$$,
    'Lainnya',
    1,
    NULL,
    3,
    'wsh_program_studi_spesialis'
),
(
    'Musala FK UPNVJ',
    $$Fasilitas ibadah Fakultas Kedokteran UPNVJ di lantai 2 Gedung Dr. Wahidin Sudiro Husodo.$$,
    'Fasilitas Ibadah',
    2,
    NULL,
    3,
    'wsh_musholla'
),
(
    'Ruang Dekan FK UPNVJ',
    $$Ruang kerja Dekan Fakultas Kedokteran.$$,
    'Lainnya',
    2,
    NULL,
    3,
    'wsh_dekan'
),
(
    'Ruang Podcast, MITEK, dan Rapat FK UPNVJ',
    $$Ruang bersama untuk kegiatan podcast, MITEK, dan rapat Fakultas Kedokteran UPNVJ di lantai 2 Gedung Dr. Wahidin Sudiro Husodo.$$,
    'Laboratorium',
    2,
    NULL,
    3,
    'wsh_podcast_meeting'
),
(
    'Ruang Program Studi Profesi',
    $$Ruang pengelolaan akademik Program Studi Profesi Fakultas Kedokteran UPNVJ di lantai 2 Gedung Dr. Wahidin Sudiro Husodo.$$,
    'Lainnya',
    2,
    NULL,
    3,
    'wsh_prodi_profesi'
),
(
    'Ruang PSKPP',
    $$Ruang PSKPP Fakultas Kedokteran UPNVJ di lantai 2 Gedung Dr. Wahidin Sudiro Husodo untuk kegiatan unit tersebut.$$,
    'Lainnya',
    2,
    NULL,
    3,
    'wsh_pskpp'
),
(
    'Ruang Rapat Dekan dan Fakultas Kedokteran',
    $$Ruang rapat untuk kegiatan pimpinan dan fakultas.$$,
    'Lainnya',
    2,
    NULL,
    3,
    'wsh_rapat_fk'
),
(
    'Ruang Sekretariat Tata Usaha FK UPNVJ',
    $$Ruang Sekretariat Tata Usaha (TU) Fakultas Kedokteran UPNVJ untuk layanan administrasi fakultas di lantai 2 Gedung Dr. Wahidin Sudiro Husodo.$$,
    'Administrasi & Layanan',
    2,
    NULL,
    3,
    'wsh_tata_usaha'
),
(
    'Ruang Server FK UPNVJ',
    $$Ruang server Fakultas Kedokteran UPNVJ untuk infrastruktur teknologi informasi di lantai 2 Gedung Dr. Wahidin Sudiro Husodo.$$,
    'Administrasi & Layanan',
    2,
    NULL,
    3,
    'wsh_server'
),
(
    'Ruang Wakil Dekan Bidang Akademik',
    $$Ruang kerja Wakil Dekan Bidang Akademik Fakultas Kedokteran UPNVJ. Jabatan Wakil Dekan juga dikenal sebagai Wadek.$$,
    'Ruang Kuliah',
    2,
    NULL,
    3,
    'wsh_wadek_akademik'
),
(
    'Ruang Wakil Dekan Bidang Kemahasiswaan dan Kerja Sama',
    $$Ruang kerja Wakil Dekan Bidang Kemahasiswaan dan Kerja Sama Fakultas Kedokteran UPNVJ. Jabatan Wakil Dekan juga dikenal sebagai Wadek.$$,
    'Lainnya',
    2,
    NULL,
    3,
    'wsh_wadek_kemahasiswaan'
),
(
    'Auditorium Fakultas Kedokteran',
    $$Auditorium dengan kapasitas sekitar 200 orang.$$,
    'Auditorium & Aula',
    3,
    NULL,
    3,
    'wsh_auditorium'
),
(
    'Laboratorium Biologi Molekuler',
    $$Laboratorium untuk praktikum dan penelitian biologi molekuler.$$,
    'Laboratorium',
    3,
    NULL,
    3,
    'wsh_lab_biologi_molekuler'
),
(
    'Laboratorium Patologi Klinik',
    $$Laboratorium untuk kegiatan patologi klinik.$$,
    'Laboratorium',
    3,
    NULL,
    3,
    'wsh_lab_patologi_klinik'
),
(
    'Ruang Dosen Patologi Klinik',
    $$Ruang kerja dan transit untuk Dosen Patologi Klinik$$,
    'Administrasi & Layanan',
    3,
    NULL,
    3,
    'wsh_ruang_dosen_patologi_klinik'
),
(
    'Ruang Kelas Farmasi',
    $$Ruang kuliah Farmasi untuk kegiatan pembelajaran di lantai 3 Gedung Dr. Wahidin Sudiro Husodo.$$,
    'Ruang Kuliah',
    3,
    NULL,
    3,
    'wsh_kelas_farmasi'
),
(
    'Ruang Kepala Laboratorium Biokimia',
    $$Ruang kerja Kepala Laboratorium Biokimia di lantai 3 Gedung Dr. Wahidin Sudiro Husodo. Kepala Laboratorium sering disebut Kalab.$$,
    'Laboratorium',
    3,
    NULL,
    3,
    'wsh_ruang_kalab_biokimia'
),
(
    'Ruang Kepala Laboratorium Biologi',
    $$Ruang kerja Kepala Laboratorium Biologi di lantai 3 Gedung Dr. Wahidin Sudiro Husodo. Kepala Laboratorium sering disebut Kalab.$$,
    'Laboratorium',
    3,
    NULL,
    3,
    'wsh_ruang_kalab_biologi'
),
(
    'Ruang Kepala Laboratorium Patologi Klinik',
    $$Ruang kerja Kepala Laboratorium Patologi Klinik di lantai 3 Gedung Dr. Wahidin Sudiro Husodo. Kepala Laboratorium sering disebut Kalab.$$,
    'Laboratorium',
    3,
    NULL,
    3,
    'wsh_ruang_kalab_patologi_klinik'
),
(
    'Ruang Laboratorium Biokimia',
    $$Ruang laboratorium biokimia.$$,
    'Laboratorium',
    3,
    NULL,
    3,
    'wsh_ruang_lab_biokimia'
),
(
    'Ruang Multimedia',
    $$Ruang multimedia Fakultas Kedokteran UPNVJ di lantai 3 Gedung Dr. Wahidin Sudiro Husodo untuk kegiatan akademik berbasis media.$$,
    'Lainnya',
    3,
    NULL,
    3,
    'wsh_multimedia'
),
(
    'Ruang Reagen Biokimia',
    $$Ruang penyimpanan reagen biokimia.$$,
    'Lainnya',
    3,
    NULL,
    3,
    'wsh_reagent_biokimia'
),
(
    'Bimbingan dan Konseling Farmasi UPNVJ',
    $$Bimbingan dan konseling farmasi di Universitas Pembangunan Nasional Veteran Jakarta.$$,
    'Lainnya',
    4,
    NULL,
    3,
    'wsh_bimbingan_dan_konseling_farmasi'
),
(
    'Kandang Hewan FK UPNVJ',
    $$Fasilitas kandang hewan untuk penelitian dan praktikum mahasiswa Fakultas Kedokteran.$$,
    'Lainnya',
    4,
    NULL,
    3,
    'wsh_kandang_hewan'
),
(
    'Laboratorium Mikrobiologi',
    $$Laboratorium Mikrobiologi untuk kegiatan praktikum dan penelitian mahasiswa Fakultas Kedokteran di lantai 4 Gedung Dr. Wahidin Sudiro Husodo. Sering disebut Lab Mikrobiologi.$$,
    'Laboratorium',
    4,
    NULL,
    3,
    'wsh_lab_mikrobiologi'
),
(
    'Laboratorium Parasitologi',
    $$Laboratorium Parasitologi untuk kegiatan praktikum dan penelitian mahasiswa Fakultas Kedokteran di lantai 4 Gedung Dr. Wahidin Sudiro Husodo. Sering disebut Lab Parasitologi.$$,
    'Laboratorium',
    4,
    NULL,
    3,
    'wsh_lab_parasitologi'
),
(
    'Laboratorium Farmakologi dan Farmasi Klinik',
    $$Laboratorium untuk kegiatan praktikum dan penelitian farmakologi dan farmasi klinik.$$,
    'Laboratorium',
    4,
    NULL,
    3,
    'wsh_lab_farmakologi_dan_farmasi_klinik'
),
(
    'Laboratorium Farmasi UPNVJ',
    $$Laboratorium farmasi di Universitas Pembangunan Nasional Veteran Jakarta.$$,
    'Laboratorium',
    4,
    NULL,
    3,
    'wsh_lab_farmasi'
),
(
    'Laboratorium Instrumentasi Farmasi',
    $$Laboratorium untuk kegiatan praktikum dan penelitian instrumentasi farmasi.$$,
    'Laboratorium',
    4,
    NULL,
    3,
    'wsh_lab_instrumentasi_farmasi'
),
(
    'Program Studi Farmasi UPNVJ',
    $$Program studi farmasi di Universitas Pembangunan Nasional Veteran Jakarta.$$,
    'Lainnya',
    4,
    NULL,
    3,
    'wsh_prodi_farmasi'
),
(
    'Ruang Kepala Laboratorium Mikrobiologi dan Parasitologi',
    $$Ruang kerja Kepala Laboratorium Mikrobiologi dan Parasitologi di lantai 4 Gedung Dr. Wahidin Sudiro Husodo. Kepala Laboratorium sering disebut Kalab.$$,
    'Laboratorium',
    4,
    NULL,
    3,
    'wsh_kalab_mikrobiologi_dan_parasitologi'
),
(
    'Ruang Kepala Laboratorium Farmakologi',
    $$Ruang kerja Kepala Laboratorium Farmakologi di lantai 4 Gedung Dr. Wahidin Sudiro Husodo. Kepala Laboratorium sering disebut Kalab.$$,
    'Lainnya',
    4,
    NULL,
    3,
    'wsh_kalab_farmakologi'
),
(
    'Ruang Laporan dan MITEK Program Studi Farmasi',
    $$Ruang kegiatan laporan dan MITEK Program Studi Farmasi di lantai 4 Gedung Dr. Wahidin Sudiro Husodo.$$,
    'Lainnya',
    4,
    NULL,
    3,
    'wsh_laporan_dan_mitek_prodi_farmasi'
),


-- Gedung 5: Gedung Abdul Rahman Saleh
(
    'Laboratorium Anatomi A.101',
    $$Fasilitas laboratorium anatomi Fakultas Kedokteran.$$,
    'Laboratorium',
    1,
    NULL,
    5,
    'ars_lab_anatomi_101'
),
(
    'Laboratorium Anatomi A.102',
    $$Fasilitas laboratorium anatomi Fakultas Kedokteran.$$,
    'Laboratorium',
    1,
    NULL,
    5,
    'ars_lab_anatomi_102'
),
(
    'Laboratorium Fisiologi',
    $$Laboratorium fisiologi Fakultas Kedokteran.$$,
    'Laboratorium',
    1,
    NULL,
    5,
    'ars_lab_fisiologi'
),
(
    'Pusat Bimbingan Ujian dan Administrasi Terpadu (PBU)',
    $$Layanan Pusat Bimbingan Ujian dan Administrasi Terpadu (PBU) di lantai 1 Gedung Abdul Rahman Saleh.$$,
    'Lainnya',
    1,
    NULL,
    5,
    'ars_pbu'
),
(
    'Musala',
    $$Fasilitas tempat ibadah bagi mahasiswa, staf, dan dosen.$$,
    'Fasilitas Ibadah',
    2,
    NULL,
    5,
    'ars_musholla'
),
(
    'Pantry',
    $$Fasilitas dapur kecil untuk kebutuhan konsumsi staf dan dosen.$$,
    'Administrasi & Layanan',
    2,
    NULL,
    5,
    'ars_pantry'
),
(
    'Ruang BEM FISIP',
    $$Ruang sekretariat Badan Eksekutif Mahasiswa (BEM) Fakultas Ilmu Sosial dan Ilmu Politik.$$,
    'Ruang Kegiatan Mahasiswa',
    2,
    NULL,
    5,
    'ars_ruang_bem_fisip'
),
(
    'Ruang Dosen',
    $$Fasilitas ruang istirahat dan kerja bagi tenaga pendidik atau dosen.$$,
    'Administrasi & Layanan',
    2,
    NULL,
    5,
    'ars_ruang_dosen'
),
(
    'Ruang EOS',
    $$Ruang sekretariat Unit Kegiatan Mahasiswa (UKM) EOS di lantai 2 Gedung Abdul Rahman Saleh.$$,
    'Lainnya',
    2,
    NULL,
    5,
    'ars_ruang_eos'
),
(
    'Ruang Gugus Kendali Mutu',
    $$Ruang operasional Gugus Kendali Mutu untuk penjaminan standar mutu akademik dan pelayanan.$$,
    'Lainnya',
    2,
    NULL,
    5,
    'ars_gugus_kendali_mutu'
),
(
    'Ruang HIMASIFO',
    $$Ruang sekretariat operasional Himpunan Mahasiswa Sistem Informasi (HIMASIFO).$$,
    'Ruang Kegiatan Mahasiswa',
    2,
    NULL,
    5,
    'ars_ruang_himasifo'
),
(
    'Ruang Kelas F.201',
    $$Ruang perkuliahan teori F.201 untuk kegiatan belajar mengajar, dilengkapi kursi kuliah, papan tulis, dan proyektor.$$,
    'Ruang Kuliah',
    2,
    NULL,
    5,
    'ars_ruang_kelas_f201'
),
(
    'Ruang Konseling dan Bimbingan Karir',
    $$Ruang layanan bimbingan, konseling, dan pengembangan karier mahasiswa di lantai 2 Gedung Abdul Rahman Saleh.$$,
    'Lainnya',
    2,
    NULL,
    5,
    'ars_ruang_konseling_dan_bimbingan_karir'
),
(
    'Ruang Server Wi-Fi',
    $$Pusat kontrol dan server jaringan WiFi untuk menjamin konektivitas internet di area gedung.$$,
    'Administrasi & Layanan',
    2,
    NULL,
    5,
    'ars_ruang_server_wifi'
),
(
    'Ruang Kelas F.301',
    $$Ruang perkuliahan teori F.301 untuk kegiatan belajar mengajar, dilengkapi kursi kuliah, papan tulis, dan proyektor.$$,
    'Ruang Kuliah',
    3,
    NULL,
    5,
    'ars_ruang_kelas_f301'
),
(
    'Ruang Kelas F.302',
    $$Ruang perkuliahan teori F.302 untuk kegiatan belajar mengajar, dilengkapi kursi kuliah, papan tulis, dan proyektor.$$,
    'Ruang Kuliah',
    3,
    NULL,
    5,
    'ars_ruang_kelas_f302'
),
(
    'Ruang Kelas F.303',
    $$Ruang perkuliahan teori F.303 untuk kegiatan belajar mengajar, dilengkapi kursi kuliah, papan tulis, dan proyektor.$$,
    'Ruang Kuliah',
    3,
    NULL,
    5,
    'ars_ruang_kelas_f303'
),
(
    'Ruang Kelas F.304',
    $$Ruang perkuliahan teori F.304 untuk kegiatan belajar mengajar, dilengkapi kursi kuliah, papan tulis, dan proyektor.$$,
    'Ruang Kuliah',
    3,
    NULL,
    5,
    'ars_ruang_kelas_f304'
),
(
    'Ruang Kelas F.305',
    $$Ruang perkuliahan teori F.305 untuk kegiatan belajar mengajar, dilengkapi kursi kuliah, papan tulis, dan proyektor.$$,
    'Ruang Kuliah',
    3,
    NULL,
    5,
    'ars_ruang_kelas_f305'
),
(
    'Ruang Kelas F.306',
    $$Ruang perkuliahan teori F.306 untuk kegiatan belajar mengajar, dilengkapi kursi kuliah, papan tulis, dan proyektor.$$,
    'Ruang Kuliah',
    3,
    NULL,
    5,
    'ars_ruang_kelas_f306'
),
(
    'Ruang Kelas F.307',
    $$Ruang perkuliahan teori F.307 untuk kegiatan belajar mengajar, dilengkapi kursi kuliah, papan tulis, dan proyektor.$$,
    'Ruang Kuliah',
    3,
    NULL,
    5,
    'ars_ruang_kelas_f307'
),
(
    'Ruang Kelas F.401',
    $$Ruang perkuliahan teori F.401 untuk kegiatan belajar mengajar, dilengkapi kursi kuliah, papan tulis, dan proyektor.$$,
    'Ruang Kuliah',
    4,
    NULL,
    5,
    'ars_ruang_kelas_f401'
),
(
    'Ruang Kelas F.402',
    $$Ruang perkuliahan teori F.402 untuk kegiatan belajar mengajar, dilengkapi kursi kuliah, papan tulis, dan proyektor.$$,
    'Ruang Kuliah',
    4,
    NULL,
    5,
    'ars_ruang_kelas_f402'
),
(
    'Ruang Kelas F.403',
    $$Ruang perkuliahan teori F.403 untuk kegiatan belajar mengajar, dilengkapi kursi kuliah, papan tulis, dan proyektor.$$,
    'Ruang Kuliah',
    4,
    NULL,
    5,
    'ars_ruang_kelas_f403'
),
(
    'Ruang Kelas F.404',
    $$Ruang perkuliahan teori F.404 untuk kegiatan belajar mengajar, dilengkapi kursi kuliah, papan tulis, dan proyektor.$$,
    'Ruang Kuliah',
    4,
    NULL,
    5,
    'ars_ruang_kelas_f404'
),


-- Gedung 6: Gedung Ki Hadjar Dewantara
(
    'Ruang Koordinator Program Studi D3 Sistem Informasi',
    $$Ruang kerja Koordinator Program Studi D3 Sistem Informasi untuk pengelolaan akademik program studi. Koordinator Program Studi dikenal juga sebagai Korprodi atau Koorprodi.$$,
    'Pelayanan & Administrasi',
    1,
    ' ',
    6,
    'khd_kaprodi_d3_si'
),
(
    'Ruang Koordinator Program Studi S1 Informatika',
    $$Ruang kerja Koordinator Program Studi S1 Informatika untuk pengelolaan akademik program studi. Koordinator Program Studi dikenal juga sebagai Korprodi atau Koorprodi.$$,
    'Pelayanan & Administrasi',
    1,
    ' ',
    6,
    'khd_kaprodi_s1_informatika'
),
(
    'Ruang Koordinator Program Studi S1 Sistem Informasi',
    $$Ruang kerja Koordinator Program Studi S1 Sistem Informasi untuk pengelolaan akademik program studi. Koordinator Program Studi dikenal juga sebagai Korprodi atau Koorprodi.$$,
    'Pelayanan & Administrasi',
    1,
    ' ',
    6,
    'khd_kaprodi_s1_si'
),
(
    'Ruang Kepala Jurusan FIK',
    $$Ruang kerja Kepala Jurusan Fakultas Ilmu Komputer untuk pengelolaan akademik jurusan. Kepala Jurusan dikenal juga sebagai Kajur.$$,
    'Pelayanan & Administrasi',
    1,
    ' ',
    6,
    'khd_kajur_fik'
),
(
    'Ruang Koordinator Program Studi S1 Sains Data',
    $$Ruang kerja Koordinator Program Studi S1 Sains Data untuk pengelolaan akademik program studi. Program ini juga dicari sebagai Data Science, sedangkan Koordinator Program Studi dikenal sebagai Korprodi atau Koorprodi.$$,
    'Pelayanan & Administrasi',
    1,
    ' ',
    6,
    'khd_kaprodi_s1_data_science'
),
(
    'Digital Library',
    $$Perpustakaan digital Fakultas Ilmu Komputer yang menyimpan koleksi buku, jurnal, artikel, dan sumber informasi lainnya dalam bentuk digital.$$,
    'Perpustakaan & Ruang Baca',
    1,
    'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/fasilitas/kihadjar/digital_library.jpg',
    6,
    'khd_digital_library'
),
(
    'Pelayanan Mahasiswa FIK',
    $$Loket pelayanan akademik dan administrasi mahasiswa Fakultas Ilmu Komputer. Fasilitas ini umum dikenal atau dicari mahasiswa sebagai Tata Usaha (TU) FIK.$$,
    'Lainnya',
    1,
    'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/fasilitas/kihadjar/selasar_lantai_1.jpg',
    6,
    'khd_pelayanan_mahasiswa'
),
(
    'Ruang Dekan FIK',
    $$Ruang kerja Dekan Fakultas Ilmu Komputer untuk kegiatan administrasi, koordinasi, dan pengambilan keputusan tingkat fakultas.$$,
    'Administrasi & Layanan',
    1,
    NULL,
    6,
    'khd_ruang_dekan'
),
(
    'Ruang Kepala Program Studi FIK',
    $$Ruang kerja Kepala Program Studi Fakultas Ilmu Komputer untuk pengelolaan akademik dan kemahasiswaan program studi. Kepala Program Studi dikenal juga sebagai Kaprodi.$$,
    'Lainnya',
    1,
    NULL,
    6,
    'khd_kaprodi'
),
(
    'Ruang Podcast FIK',
    $$Ruang podcast Fakultas Ilmu Komputer yang dilengkapi dengan peralatan rekaman audio dan video profesional, digunakan untuk produksi konten digital, wawancara, dan kegiatan penyiaran mahasiswa.$$,
    'Laboratorium',
    1,
    'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/fasilitas/kihadjar/digital_library.jpg',
    6,
    'khd_podcast'
),
(
    'Selasar Gedung Ki Hadjar Dewantara',
    $$Area selasar pada lantai 1 Gedung Ki Hadjar Dewantara.$$,
    'Lainnya',
    1,
    'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/fasilitas/kihadjar/selasar_lantai_1.jpg',
    6,
    'khd_selasar'
),
(
    'Laboratorium Software Engineering (Ruang 201)',
    $$Laboratorium rekayasa perangkat lunak (software engineering) untuk kegiatan praktikum dan penelitian Fakultas Ilmu Komputer di ruang 201. Sering disebut Lab Software Engineering.$$,
    'Laboratorium',
    2,
    'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/fasilitas/kihadjar/lab_software_engineering_201.jpg',
    6,
    'khd_201_lab'
),
(
    'Ruang Dosen FIK',
    $$Ruang kerja dan transit dosen Fakultas Ilmu Komputer untuk persiapan mengajar, bimbingan mahasiswa, dan kegiatan akademik.$$,
    'Administrasi & Layanan',
    2,
    'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/fasilitas/kihadjar/lab_software_engineering_201.jpg',
    6,
    'khd_ruang_dosen'
),
(
    'Ruang Kuliah 202',
    $$Ruang perkuliahan di lantai 2 Gedung Ki Hadjar Dewantara untuk kegiatan belajar mengajar mahasiswa Fakultas Ilmu Komputer, dilengkapi proyektor dan papan tulis.$$,
    'Ruang Kuliah',
    2,
    NULL,
    6,
    'khd_202'
),
(
    'Ruang Kuliah 203',
    $$Ruang perkuliahan di lantai 2 Gedung Ki Hadjar Dewantara untuk kegiatan belajar mengajar mahasiswa Fakultas Ilmu Komputer, dilengkapi proyektor dan papan tulis.$$,
    'Ruang Kuliah',
    2,
    NULL,
    6,
    'khd_203'
),
(
    'Sekretariat Laboratorium',
    $$Ruang sekretariat laboratorium yang berfungsi sebagai pusat administrasi dan koordinasi kegiatan laboratorium.$$,
    'Laboratorium',
    2,
    'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/fasilitas/kihadjar/sekretariat_laboratorium.jpg',
    6,
    'khd_sekretariat_ikatik'
),
(
    'Laboratorium Artificial Intelligence dan Robotics (Ruang 302)',
    $$Laboratorium kecerdasan buatan dan robotika (artificial intelligence and robotics) untuk kegiatan praktikum dan penelitian di ruang 302. Sering disebut Lab AI dan Robotics.$$,
    'Laboratorium',
    3,
    'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/fasilitas/kihadjar/lab_artificial_intelligence_dan_robotics_302.jpg',
    6,
    'khd_302_lab'
),
(
    'Laboratorium Big Data dan Data Science (Ruang 303)',
    $$Laboratorium data besar dan sains data (big data and data science) untuk kegiatan praktikum dan penelitian di ruang 303. Sering disebut Lab Big Data dan Data Science.$$,
    'Laboratorium',
    3,
    'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/fasilitas/kihadjar/lab_big_data_dan_data_science_303.jpg',
    6,
    'khd_303_lab'
),
(
    'Laboratorium Cybersecurity dan Networking (Ruang 304)',
    $$Laboratorium keamanan siber dan jaringan (cybersecurity and networking) untuk kegiatan praktikum dan penelitian di ruang 304. Sering disebut Lab Cybersecurity dan Networking.$$,
    'Laboratorium',
    3,
    'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/fasilitas/kihadjar/lab_cybersecurity_dan_networking_304.jpg',
    6,
    'khd_304_lab'
),
(
    'Laboratorium Immersive dan Multimedia/Programming',
    $$Laboratorium teknologi imersif, multimedia, dan pemrograman untuk kegiatan praktikum dan penelitian Fakultas Ilmu Komputer. Sering disebut Lab Immersive dan Multimedia/Programming.$$,
    'Laboratorium',
    3,
    'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/fasilitas/kihadjar/lab_immersive_dan_multimedia.jpg',
    6,
    'khd_301_lab'
),
(
    'Sekretariat Laboratorium',
    $$Ruang sekretariat laboratorium yang berfungsi sebagai pusat administrasi dan koordinasi kegiatan laboratorium.$$,
    'Laboratorium',
    3,
    'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/fasilitas/kihadjar/sekretariat_laboratorium.jpg',
    6,
    'khd_sekretariat_lab'
),
(
    'Laboratorium E-Governance/Database',
    $$Laboratorium tata kelola elektronik dan basis data (e-governance/database) untuk kegiatan praktikum dan penelitian Fakultas Ilmu Komputer. Sering disebut Lab E-Governance/Database.$$,
    'Laboratorium',
    4,
    'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/fasilitas/kihadjar/lab_e_governance.jpg',
    6,
    'khd_403_lab'
),
(
    'Laboratorium Enterprise System/Business Intelligence',
    $$Laboratorium sistem perusahaan dan intelijen bisnis (enterprise system/business intelligence) untuk kegiatan praktikum dan penelitian. Sering disebut Lab Enterprise System/Business Intelligence.$$,
    'Laboratorium',
    4,
    'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/fasilitas/kihadjar/lab_enterprise_system.jpg',
    6,
    'khd_402_lab'
),
(
    'Laboratorium Internet of Things (Ruang 401)',
    $$Laboratorium Internet of Things (IoT) untuk kegiatan praktikum dan penelitian Fakultas Ilmu Komputer di ruang 401. Sering disebut Lab IoT.$$,
    'Laboratorium',
    4,
    'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/fasilitas/kihadjar/lab_internet_of_things_401.jpg',
    6,
    'khd_401_lab'
),
(
    'Masjid',
    $$Masjid di lingkungan kampus UPNVJ, berlokasi di area Gedung Ki Hadjar Dewantara.$$,
    'Fasilitas Ibadah',
    NULL,
    'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/fasilitas/kihadjar/masjid.jpg',
    6,
    'masjid'
),




-- Gedung 10: Gedung RA Kartini
('Ruang BMN', $$Ruang BMN (Barang Milik Negara) pada lantai 1 Gedung RA Kartini untuk penyimpanan dan pengelolaan aset milik negara di lingkungan kampus.$$,
    'Administrasi & Layanan',
    1,
    NULL,
    10,
    'rak_bmn'
),
(
    'Ruang Dosen dan Staf Administrasi Doktor (S3) Hukum',
    $$Ruang dosen dan staf administrasi Program Doktor (S3) Hukum pada lantai 1 Gedung RA Kartini.$$,
    'Administrasi & Layanan',
    1,
    NULL,
    10,
    'rak_dosen_staff_doktor_hukum'
),
(
    'Ruang Kelas 101',
    $$Ruang perkuliahan 101 di lantai 1 Gedung RA Kartini untuk kegiatan belajar mengajar, dilengkapi kursi, papan tulis, dan proyektor.$$,
    'Ruang Kuliah',
    1,
    NULL,
    10,
    'rak_kelas_101'
),
(
    'Ruang Kelas 102',
    $$Ruang perkuliahan 102 di lantai 1 Gedung RA Kartini untuk kegiatan belajar mengajar, dilengkapi kursi, papan tulis, dan proyektor.$$,
    'Ruang Kuliah',
    1,
    NULL,
    10,
    'rak_kelas_102'
),
(
    'Laboratorium Farmasi Fakultas Kedokteran',
    $$Laboratorium Farmasi Fakultas Kedokteran pada lantai 1 Gedung RA Kartini.$$,
    'Laboratorium',
    1,
    NULL,
    10,
    'rak_lab_farmasi_fk'
),
(
    'Ruang UPT Pengembangan Karir dan Kewirausahaan',
    $$Ruang UPT Pengembangan Karir dan Kewirausahaan pada lantai 1 Gedung RA Kartini.$$,
    'Administrasi & Layanan',
    1,
    NULL,
    10,
    'rak_upt_pengembangan_karir'
),
(
    'Ruang Ujian UPA Bahasa dan Ruang Sidang S3',
    $$Satu ruang yang difungsikan sebagai ruang ujian UPA Bahasa sekaligus ruang sidang Program Doktor (S3) pada lantai 2 Gedung RA Kartini. Dikenal juga sebagai Ruang Sidang Doktor atau Ruang Sidang S3.$$,
    'Ruang Kuliah',
    2,
    NULL,
    10,
    'rak_ujian_upa_sidang_s3'
),
(
    'Ruang Diskusi dan Ruang Instruktur UPA Bahasa',
    $$Satu ruang yang difungsikan sebagai ruang diskusi sekaligus ruang instruktur UPA Bahasa pada lantai 2 Gedung RA Kartini.$$,
    'Ruang Kuliah',
    2,
    NULL,
    10,
    'rak_diskusi_instruktur_upa_bahasa'
),
(
    'Laboratorium Bahasa dan Ruang Ujian UPA Bahasa',
    $$Laboratorium bahasa yang juga digunakan sebagai ruang ujian UPA Bahasa pada lantai 2 Gedung RA Kartini. Dikenal juga sebagai Lab Bahasa atau Ruang Ujian UPA Bahasa.$$,
    'Laboratorium',
    2,
    NULL,
    10,
    'rak_lab_bahasa_ujian_upa'
),
(
    'Ruang Kelas 201',
    $$Ruang perkuliahan 201 di lantai 2 Gedung RA Kartini untuk kegiatan belajar mengajar, dilengkapi kursi, papan tulis, dan proyektor.$$,
    'Ruang Kuliah',
    2,
    NULL,
    10,
    'rak_kelas_201'
),
(
    'Ruang Guru Besar dan Pengelola Jurnal',
    $$Ruang Guru Besar dan Pengelola Jurnal pada lantai 2 Gedung RA Kartini.$$,
    'Administrasi & Layanan',
    2,
    NULL,
    10,
    'rak_guru_besar_pengelola_jurnal'
),
(
    'UPA Bahasa',
    $$Ruang layanan Unit Pelaksana Akademik (UPA) Bahasa pada lantai 2 Gedung RA Kartini.$$,
    'Administrasi & Layanan',
    2,
    NULL,
    10,
    'rak_upa_bahasa'
),
(
    'Ruang Ujian UPA Bahasa 301',
    $$Ruang ujian UPA Bahasa nomor 301 di lantai 3 Gedung RA Kartini untuk pelaksanaan tes kemampuan bahasa bagi mahasiswa.$$,
    'Ruang Kuliah',
    3,
    NULL,
    10,
    'rak_ujian_upa_bahasa_301'
),
(
    'Ruang Ujian UPA Bahasa 302',
    $$Ruang ujian UPA Bahasa nomor 302 di lantai 3 Gedung RA Kartini untuk pelaksanaan tes kemampuan bahasa bagi mahasiswa.$$,
    'Ruang Kuliah',
    3,
    NULL,
    10,
    'rak_ujian_upa_bahasa_302'
),
(
    'Ruang Ujian UPA Bahasa 303',
    $$Ruang ujian UPA Bahasa nomor 303 di lantai 3 Gedung RA Kartini untuk pelaksanaan tes kemampuan bahasa bagi mahasiswa.$$,
    'Ruang Kuliah',
    3,
    NULL,
    10,
    'rak_ujian_upa_bahasa_303'
),
(
    'Ruang Ujian UPA Bahasa 304',
    $$Ruang ujian UPA Bahasa nomor 304 di lantai 3 Gedung RA Kartini untuk pelaksanaan tes kemampuan bahasa bagi mahasiswa.$$,
    'Ruang Kuliah',
    3,
    NULL,
    10,
    'rak_ujian_upa_bahasa_304'
),
(
    'Ruang Ujian UPA Bahasa 305',
    $$Ruang ujian UPA Bahasa nomor 305 di lantai 3 Gedung RA Kartini untuk pelaksanaan tes kemampuan bahasa bagi mahasiswa.$$,
    'Ruang Kuliah',
    3,
    NULL,
    10,
    'rak_ujian_upa_bahasa_305'
),
(
    'Ruang Ujian UPA Bahasa 306',
    $$Ruang ujian UPA Bahasa nomor 306 di lantai 3 Gedung RA Kartini untuk pelaksanaan tes kemampuan bahasa bagi mahasiswa.$$,
    'Ruang Kuliah',
    3,
    NULL,
    10,
    'rak_ujian_upa_bahasa_306'
),
-- Fasilitas RA Kartini Lantai 4 (Kelas 401-406)
(
    'Ruang Kelas 401',
    $$Ruang perkuliahan 401 di lantai 4 Gedung RA Kartini untuk kegiatan belajar mengajar, dilengkapi kursi, papan tulis, dan proyektor.$$,
    'Ruang Kuliah',
    4,
    NULL,
    10,
    'rak_ujian_upa_bahasa_401'
),
(
    'Ruang Kelas 402',
    $$Ruang perkuliahan 402 di lantai 4 Gedung RA Kartini untuk kegiatan belajar mengajar, dilengkapi kursi, papan tulis, dan proyektor.$$,
    'Ruang Kuliah',
    4,
    NULL,
    10,
    'rak_ujian_upa_bahasa_402'
),
(
    'Ruang Kelas 403',
    $$Ruang perkuliahan 403 di lantai 4 Gedung RA Kartini untuk kegiatan belajar mengajar, dilengkapi kursi, papan tulis, dan proyektor.$$,
    'Ruang Kuliah',
    4,
    NULL,
    10,
    'rak_ujian_upa_bahasa_403'
),
(
    'Ruang Kelas 404',
    $$Ruang perkuliahan 404 di lantai 4 Gedung RA Kartini untuk kegiatan belajar mengajar, dilengkapi kursi, papan tulis, dan proyektor.$$,
    'Ruang Kuliah',
    4,
    NULL,
    10,
    'rak_ujian_upa_bahasa_404'
),
(
    'Ruang Kelas 405',
    $$Ruang perkuliahan 405 di lantai 4 Gedung RA Kartini untuk kegiatan belajar mengajar, dilengkapi kursi, papan tulis, dan proyektor.$$,
    'Ruang Kuliah',
    4,
    NULL,
    10,
    'rak_ujian_upa_bahasa_405'
),
(
    'Ruang Kelas 406',
    $$Ruang perkuliahan 406 di lantai 4 Gedung RA Kartini untuk kegiatan belajar mengajar, dilengkapi kursi, papan tulis, dan proyektor.$$,
    'Ruang Kuliah',
    4,
    NULL,
    10,
    'rak_ujian_upa_bahasa_406'
),

-- Gedung 13: Gedung Dewi Sartika
(
    'Ruang BEM FIK',
    $$Ruang sekretariat Badan Eksekutif Mahasiswa (BEM) FIK di Gedung Dewi Sartika, sebagai pusat koordinasi program kerja dan kegiatan kemahasiswaan.$$,
    'Ruang Kegiatan Mahasiswa',
    1,
    NULL,
    13,
    'ds_bem'
),
(
    'Ruang Senat Mahasiswa FIK',
    $$Ruang sekretariat Senat Mahasiswa Fakultas Ilmu Komputer (FIK) di lantai 1 Gedung Dewi Sartika.$$,
    'Ruang Kegiatan Mahasiswa',
    1,
    NULL,
    13,
    'ds_senat'
),
(
    'Ruang UKM Basket',
    $$Ruang sekretariat dan kegiatan Unit Kegiatan Mahasiswa (UKM) Basket di lantai 1 Gedung Dewi Sartika.$$,
    'Ruang Kegiatan Mahasiswa',
    1,
    NULL,
    13,
    'ds_ukm_basket'
),
(
    'Ruang UKM Boxer',
    $$Ruang sekretariat dan kegiatan Unit Kegiatan Mahasiswa (UKM) Boxer di lantai 1 Gedung Dewi Sartika.$$,
    'Ruang Kegiatan Mahasiswa',
    1,
    NULL,
    13,
    'ds_ukm_boxer'
),
(
    'Ruang UKM Bulu Tangkis',
    $$Ruang sekretariat dan kegiatan Unit Kegiatan Mahasiswa (UKM) Bulu Tangkis di lantai 1 Gedung Dewi Sartika.$$,
    'Ruang Kegiatan Mahasiswa',
    1,
    NULL,
    13,
    'ds_ukm_bulu_tangkis'
),
(
    'Ruang UKM Catur',
    $$Ruang sekretariat dan kegiatan Unit Kegiatan Mahasiswa (UKM) Catur di lantai 1 Gedung Dewi Sartika.$$,
    'Ruang Kegiatan Mahasiswa',
    1,
    NULL,
    13,
    'ds_ukm_catur'
),
(
    'Ruang UKM Futsal',
    $$Ruang sekretariat dan kegiatan Unit Kegiatan Mahasiswa (UKM) Futsal di lantai 1 Gedung Dewi Sartika.$$,
    'Ruang Kegiatan Mahasiswa',
    1,
    NULL,
    13,
    'ds_ukm_futsal'
),
(
    'Ruang UKM Jujitsu',
    $$Ruang sekretariat dan kegiatan Unit Kegiatan Mahasiswa (UKM) Jujitsu di lantai 1 Gedung Dewi Sartika.$$,
    'Ruang Kegiatan Mahasiswa',
    1,
    NULL,
    13,
    'ds_ukm_jujitsu'
),
(
    'Ruang UKM Katolik',
    $$Ruang sekretariat dan kegiatan Unit Kegiatan Mahasiswa (UKM) Katolik di lantai 1 Gedung Dewi Sartika.$$,
    'Ruang Kegiatan Mahasiswa',
    1,
    NULL,
    13,
    'ds_ukm_katolik'
),
(
    'Ruang UKM MC',
    $$Ruang sekretariat dan kegiatan Unit Kegiatan Mahasiswa (UKM) MC di lantai 1 Gedung Dewi Sartika.$$,
    'Ruang Kegiatan Mahasiswa',
    1,
    NULL,
    13,
    'ds_ukm_mc'
),
-- Restored dari commit 024ba7a (fasilitas Dewi Sartika yang sebelumnya terpotong)
(
    'Ruang UKM UBV',
    $$Ruang sekretariat dan kegiatan Unit Kegiatan Mahasiswa (UKM) UBV di lantai 1 Gedung Dewi Sartika.$$,
    'Ruang Kegiatan Mahasiswa',
    1,
    NULL,
    13,
    'ds_ukm_ubv'
),
(
    'Ruang UKM UFO',
    $$Ruang sekretariat dan kegiatan Unit Kegiatan Mahasiswa (UKM) UFO di lantai 1 Gedung Dewi Sartika.$$,
    'Ruang Kegiatan Mahasiswa',
    1,
    NULL,
    13,
    'ds_ukm_ufo'
),
(
    'Ruang UKM Seni Tari',
    $$Ruang sekretariat dan kegiatan Unit Kegiatan Mahasiswa (UKM) Seni Tari di lantai 1 Gedung Dewi Sartika.$$,
    'Ruang Kegiatan Mahasiswa',
    1,
    NULL,
    13,
    'ds_ukm_seni_tari'
),
(
    'Ruang UKM Voli',
    $$Ruang sekretariat dan kegiatan Unit Kegiatan Mahasiswa (UKM) Voli di lantai 1 Gedung Dewi Sartika.$$,
    'Ruang Kegiatan Mahasiswa',
    1,
    NULL,
    13,
    'ds_ukm_voli'
),
(
    'Ruang UKM Pencak Silat',
    $$Ruang sekretariat dan kegiatan Unit Kegiatan Mahasiswa (UKM) Pencak Silat di lantai 1 Gedung Dewi Sartika.$$,
    'Ruang Kegiatan Mahasiswa',
    1,
    NULL,
    13,
    'ds_ukm_pencak_silat'
),
(
    'Ruang UKM Paduan Suara',
    $$Ruang sekretariat dan kegiatan Unit Kegiatan Mahasiswa (UKM) Paduan Suara di lantai 1 Gedung Dewi Sartika.$$,
    'Ruang Kegiatan Mahasiswa',
    1,
    NULL,
    13,
    'ds_ukm_paduan_suara'
),
(
    'Ruang UKM Protestan',
    $$Ruang sekretariat dan kegiatan Unit Kegiatan Mahasiswa (UKM) Protestan di lantai 1 Gedung Dewi Sartika.$$,
    'Ruang Kegiatan Mahasiswa',
    1,
    NULL,
    13,
    'ds_ukm_protestan'
),
(
    'Ruang Kuliah 201',
    $$Ruang perkuliahan di lantai 2 Gedung Dewi Sartika untuk kegiatan belajar mengajar mahasiswa Fakultas Ilmu Komputer, dilengkapi proyektor dan papan tulis.$$,
    'Ruang Kuliah',
    2,
    NULL,
    13,
    'ds_201'
),
(
    'Ruang Kuliah 202',
    $$Ruang perkuliahan di lantai 2 Gedung Dewi Sartika untuk kegiatan belajar mengajar mahasiswa Fakultas Ilmu Komputer, dilengkapi proyektor dan papan tulis.$$,
    'Ruang Kuliah',
    2,
    NULL,
    13,
    'ds_202'
),
(
    'Ruang Kuliah 203',
    $$Ruang perkuliahan di lantai 2 Gedung Dewi Sartika untuk kegiatan belajar mengajar mahasiswa Fakultas Ilmu Komputer, dilengkapi proyektor dan papan tulis.$$,
    'Ruang Kuliah',
    2,
    NULL,
    13,
    'ds_203'
),
(
    'Ruang Kuliah 301',
    $$Ruang perkuliahan di lantai 3 Gedung Dewi Sartika untuk kegiatan belajar mengajar mahasiswa Fakultas Ilmu Komputer, dilengkapi proyektor dan papan tulis.$$,
    'Ruang Kuliah',
    3,
    NULL,
    13,
    'ds_301'
),
(
    'Ruang Kuliah 302',
    $$Ruang perkuliahan di lantai 3 Gedung Dewi Sartika untuk kegiatan belajar mengajar mahasiswa Fakultas Ilmu Komputer, dilengkapi proyektor dan papan tulis.$$,
    'Ruang Kuliah',
    3,
    NULL,
    13,
    'ds_302'
),
(
    'Ruang Kuliah 303',
    $$Ruang perkuliahan di lantai 3 Gedung Dewi Sartika untuk kegiatan belajar mengajar mahasiswa Fakultas Ilmu Komputer, dilengkapi proyektor dan papan tulis.$$,
    'Ruang Kuliah',
    3,
    NULL,
    13,
    'ds_303'
),
(
    'Ruang Kuliah 401',
    $$Ruang perkuliahan di lantai 4 Gedung Dewi Sartika untuk kegiatan belajar mengajar mahasiswa Fakultas Ilmu Komputer, dilengkapi proyektor dan papan tulis.$$,
    'Ruang Kuliah',
    4,
    NULL,
    13,
    'ds_401'
),
(
    'Ruang Kuliah 402',
    $$Ruang perkuliahan di lantai 4 Gedung Dewi Sartika untuk kegiatan belajar mengajar mahasiswa Fakultas Ilmu Komputer, dilengkapi proyektor dan papan tulis.$$,
    'Ruang Kuliah',
    4,
    NULL,
    13,
    'ds_402'
),
(
    'Ruang Kuliah 403',
    $$Ruang perkuliahan di lantai 4 Gedung Dewi Sartika untuk kegiatan belajar mengajar mahasiswa Fakultas Ilmu Komputer, dilengkapi proyektor dan papan tulis.$$,
    'Ruang Kuliah',
    4,
    NULL,
    13,
    'ds_403_mesh'
)
;


-- Gedung 17: Gedung Soetomo
INSERT INTO public.fasilitas (nama_fasilitas, deskripsi_fasilitas, tipe_fasilitas, lantai, id_gedung, unity_object_name) VALUES
('TechnoWater Water Station', 'Fasilitas penyediaan air minum gratis (water station) TechnoWater pada lantai 1 Gedung Soetomo.', 'Lainnya', 1, 17, 'stm_technowater'),
('Ruang Majelis Permusyawaratan Mahasiswa (MPM)', 'Ruang organisasi Majelis Permusyawaratan Mahasiswa (MPM) pada lantai 1 Gedung Soetomo. Dikenal juga sebagai MPM UPNVJ.', 'Ruang Kegiatan Mahasiswa', 1, 17, 'stm_mpm'),
('Ruang Badan Perwakilan Mahasiswa (BPM)', 'Ruang organisasi Badan Perwakilan Mahasiswa (BPM) pada lantai 1 Gedung Soetomo. Dikenal juga sebagai BPM UPNVJ.', 'Ruang Kegiatan Mahasiswa', 1, 17, 'stm_bpm'),
('Ruang Teater', 'Ruang teater pada lantai 1 Gedung Soetomo untuk kegiatan pertunjukan seni, latihan, dan aktivitas kemahasiswaan.', 'Auditorium & Aula', 1, 17, 'stm_ruang_teater'),
('Studio Latihan Tari', 'Studio latihan tari pada lantai 1 Gedung Soetomo untuk kegiatan seni tari dan latihan Unit Kegiatan Mahasiswa.', 'Laboratorium', 1, 17, 'stm_studio_latihan_tari'),
('Lobi Perpustakaan', 'Area lobi perpustakaan pada lantai 1 Gedung Soetomo sebagai area penerima dan akses utama menuju fasilitas perpustakaan.', 'Administrasi & Layanan', 1, 17, 'stm_lobby_perpustakaan'),
('Ruang Diskusi', 'Ruang diskusi pada lantai 1 Gedung Soetomo untuk kegiatan belajar kelompok dan diskusi mahasiswa.', 'Ruang Kuliah', 1, 17, 'stm_ruang_diskusi_l1'),
('Ruang UKM Girigahana', 'Ruang sekretariat Unit Kegiatan Mahasiswa (UKM) Girigahana pada lantai 1 area ekstensi Gedung Soetomo.', 'Ruang Kegiatan Mahasiswa', 1, 17, 'stm_ukm_girigahana'),
('Ruang Aspirasi', 'Ruang beridentitas Aspirasi pada lantai 1 area ekstensi Gedung Soetomo untuk kegiatan kemahasiswaan.', 'Ruang Kegiatan Mahasiswa', 1, 17, 'stm_aspirasi'),
('Ruang UKM Mapala', 'Ruang sekretariat Unit Kegiatan Mahasiswa (UKM) Mapala pada lantai 1 area ekstensi Gedung Soetomo.', 'Ruang Kegiatan Mahasiswa', 1, 17, 'stm_ukm_mapala'),
('Ruang Akses Digital', 'Ruang akses digital pada lantai 2 Gedung Soetomo untuk pemanfaatan layanan digital dan akses informasi akademik perpustakaan.', 'Administrasi & Layanan', 2, 17, 'stm_ruang_akses_digital'),
('Ruang Multimedia', 'Ruang multimedia pada lantai 2 Gedung Soetomo untuk kegiatan pembelajaran, presentasi, dan akses media digital.', 'Laboratorium', 2, 17, 'stm_ruang_multimedia'),
('Ruang UKM Pencak Silat Veteran Jakarta (PSVJ)', 'Ruang sekretariat Unit Kegiatan Mahasiswa (UKM) Pencak Silat Veteran Jakarta (PSVJ) pada lantai 2 area ekstensi Gedung Soetomo. Berbeda dari Ruang UKM Pencak Silat di Gedung Dewi Sartika.', 'Ruang Kegiatan Mahasiswa', 2, 17, 'stm_ukm_psvj'),
('Ruang UKM Taekwondo', 'Ruang sekretariat Unit Kegiatan Mahasiswa (UKM) Taekwondo pada lantai 2 area ekstensi Gedung Soetomo.', 'Ruang Kegiatan Mahasiswa', 2, 17, 'stm_ukm_taekwondo'),
('Ruang UKM KSR PMI', 'Ruang sekretariat Unit Kegiatan Mahasiswa (UKM) Korps Sukarela Palang Merah Indonesia (KSR PMI) pada lantai 2 area ekstensi Gedung Soetomo.', 'Ruang Kegiatan Mahasiswa', 2, 17, 'stm_ukm_ksr_pmi'),
('Ruang UKM Bulu Tangkis', 'Ruang sekretariat Unit Kegiatan Mahasiswa (UKM) Bulu Tangkis pada lantai 2 area ekstensi Gedung Soetomo. Berbeda dari Ruang UKM Bulu Tangkis di Gedung Dewi Sartika.', 'Ruang Kegiatan Mahasiswa', 2, 17, 'stm_ukm_bulutangkis'),
('Perpustakaan Utama Kampus', 'Perpustakaan utama kampus pada lantai 3 Gedung Soetomo. Mencakup area: Pojok Bela Negara, Kazakhstan Corner, German Corner, Ruang Selasar, Ruang Komputer, Komputer E-paper, Ruang Diskusi, dan Rak Koleksi. Seluruh area ini merupakan bagian integral dari satu fasilitas perpustakaan.', 'Perpustakaan & Ruang Baca', 3, 17, 'stm_perpustakaan_utama'),
('Ruang Ujian Doktor Hukum', 'Ruang ujian tugas akhir Program Doktor Hukum pada lantai 1 Gedung Soetomo.', 'Ruang Kegiatan Mahasiswa',1, 17, 'stm_ruang_ujian_doktor_hukum')
-- ,('Perpustakaan Lantai 4', 'Area perpustakaan yang menempati keseluruhan lantai 4 Gedung Soetomo.', 'Perpustakaan & Ruang Baca', 4, 17, 'stm_perpustakaan_l4')
;
-- =============================================================================
-- DATA FASILITAS GEDUNG REKTORAT (id_gedung = 1)
-- =============================================================================
-- DATA FASILITAS GEDUNG REKTORAT (id_gedung = 1)
-- =============================================================================
INSERT INTO public.fasilitas (nama_fasilitas, deskripsi_fasilitas, tipe_fasilitas, lantai, id_gedung, unity_object_name) VALUES
-- Lantai 1
('Ruang Senat Universitas dan Lembaga Konsultasi dan Bantuan Hukum', 'Ruang Senat Universitas dan Lembaga Konsultasi dan Bantuan Hukum pada lantai 1 Gedung Rektorat.', 'Administrasi & Layanan', 1, 1, 'rt_senat_univ'),
('Ruang Mata Kuliah Wajib Kurikulum (MKWK)', 'Ruang Mata Kuliah Wajib Kurikulum (MKWK) pada lantai 1 Gedung Rektorat.', 'Administrasi & Layanan', 1, 1, 'rt_mkwk'),
('Ruang Kantor Urusan Internasional (KUI)', 'Ruang Kantor Urusan Internasional (KUI) pada lantai 1 Gedung Rektorat untuk layanan kerja sama dan urusan internasional.', 'Administrasi & Layanan', 1, 1, 'rt_kui'),
('Ruang Kepala Pusat Pemeringkatan dan Kepala Pusat MKWU', 'Ruang Kepala Pusat Pemeringkatan dan Kepala Pusat MKWU pada lantai 1 Gedung Rektorat.', 'Administrasi & Layanan', 1, 1, 'rt_kep_pemeringkatan'),
('Ruang Tamu Bersama', 'Ruang Tamu Bersama pada lantai 1 Gedung Rektorat.', 'Administrasi & Layanan', 1, 1, 'rt_ruang_tamu_bersama'),
('Ruang Hubungan Masyarakat (Humas)', 'Ruang Hubungan Masyarakat (Humas) pada lantai 1 Gedung Rektorat.', 'Administrasi & Layanan', 1, 1, 'rt_humas'),
('Ruang Dewan Pengawas', 'Ruang Dewan Pengawas pada lantai 1 Gedung Rektorat.', 'Administrasi & Layanan', 1, 1, 'rt_dewas'),
('Ruang Pusat Kajian Bela Negara', 'Ruang Pusat Kajian Bela Negara pada lantai 1 Gedung Rektorat.', 'Administrasi & Layanan', 1, 1, 'rt_puska'),
('Ruang Unit Layanan Terpadu dan Informasi Publik', 'Ruang Unit Layanan Terpadu dan Informasi Publik pada lantai 1 Gedung Rektorat.', 'Administrasi & Layanan', 1, 1, 'rt_layanan_terpadu'),
('Bank BNI', 'Fasilitas perbankan BNI pada Lantai 1 Gedung Rektorat.', 'Administrasi & Layanan', 1, 1, 'rt_bni'),
('Plaza Penmaru Wardiman', 'Plaza Penmaru Wardiman pada Lantai 1 Gedung Rektorat.', 'Administrasi & Layanan', 1, 1, 'rt_wardiman'),

-- Lantai 2
('Ruang Rapat Nusantara 1', 'Ruang Rapat Nusantara 1 pada lantai 2 Gedung Rektorat.', 'Administrasi & Layanan', 2, 1, 'rt_rapat_nusantara_1'),
('Ruang Rapat Nusantara 2', 'Ruang Rapat Nusantara 2 pada lantai 2 Gedung Rektorat.', 'Administrasi & Layanan', 2, 1, 'rt_rapat_nusantara_2'),
('Ruang Wakil Rektor 1', 'Ruang kerja Wakil Rektor 1 pada lantai 2 Gedung Rektorat. Wakil Rektor dikenal juga sebagai Warek.', 'Administrasi & Layanan', 2, 1, 'rt_warek_1'),
('Ruang Wakil Rektor 3', 'Ruang kerja Wakil Rektor 3 pada lantai 2 Gedung Rektorat. Wakil Rektor dikenal juga sebagai Warek.', 'Administrasi & Layanan', 2, 1, 'rt_warek_3'),
('Ruang Rapat Nusantara dan Ruang Wakil Rektor 2', 'Ruang Rapat Nusantara dan ruang kerja Wakil Rektor 2 pada lantai 2 Gedung Rektorat. Wakil Rektor dikenal juga sebagai Warek.', 'Administrasi & Layanan', 2, 1, 'rt_warek_2'),
('Ruang Kepegawaian', 'Ruang Kepegawaian pada Lantai 2 Gedung Rektorat.', 'Administrasi & Layanan', 2, 1, 'rt_kepegawaian'),
('UPA TIK', 'Unit Penunjang Akademik Teknologi Informasi dan Komunikasi (UPA TIK) pada Lantai 2 Gedung Rektorat.', 'Administrasi & Layanan', 2, 1, 'rt_upa_tik'),
('Ruang Rektor', 'Ruang kerja Rektor pada lantai 2 Gedung Rektorat.', 'Administrasi & Layanan', 2, 1, 'rt_rektorat'),
('Bagian Hukum & Tata Laksana', 'Bagian Hukum & Tata Laksana pada Lantai 2 Gedung Rektorat.', 'Administrasi & Layanan', 2, 1, 'rt_hukum_tata_laksana'),
('Ruang Staf', 'Ruang kerja staf pada lantai 2 Gedung Rektorat.', 'Administrasi & Layanan', 2, 1, 'rt_staff'),

-- Lantai 3
('Ruang Biro Perencanaan Umum, Keuangan, dan Umum', 'Ruang Biro Perencanaan Umum, Keuangan, dan Umum pada lantai 3 Gedung Rektorat.', 'Administrasi & Layanan', 3, 1, 'rt_ruku'),
('Ruang Biro AKPK', 'Ruang Biro Akademik, Kemahasiswaan, Perencanaan, dan Kerja Sama (AKPK) pada lantai 3 Gedung Rektorat.', 'Administrasi & Layanan', 3, 1, 'rt_akpk'),
('Pusat Pelayanan Keuangan Mahasiswa', 'Pusat Pelayanan Keuangan Mahasiswa pada Lantai 3 Gedung Rektorat.', 'Administrasi & Layanan', 3, 1, 'rt_pusat_keuangan'),
('Bagian Keuangan Biro Umum & Keuangan', 'Bagian Keuangan Biro Umum & Keuangan pada Lantai 3 Gedung Rektorat.', 'Administrasi & Layanan', 3, 1, 'rt_biro_umum_keuangan'),
('Ruang Rapat Nusantara 4', 'Ruang Rapat Nusantara 4 pada lantai 3 Gedung Rektorat.', 'Administrasi & Layanan', 3, 1, 'rt_rapat_nusantara_4'),
('Ruang Tax Center', 'Ruang Tax Center pada Lantai 3 Gedung Rektorat.', 'Administrasi & Layanan', 3, 1, 'rt_tax_center'),
('Ruang Pusat Kajian Bela Negara', 'Ruang Pusat Kajian Bela Negara pada lantai 3 Gedung Rektorat.', 'Administrasi & Layanan', 3, 1, 'rt_pkbn'),
('Ruang Bidang Kemahasiswaan', 'Ruang Bidang Kemahasiswaan pada lantai 3 Gedung Rektorat.', 'Administrasi & Layanan', 3, 1, 'rt_kemahasiswaan'),
('Ruang Kelas Bank Mini 302', 'Ruang Kelas Bank Mini 302 pada Lantai 3 Gedung Rektorat.', 'Ruang Kuliah', 3, 1, 'rt_302'),

-- Lantai 4
('Ruang UPA LUK/LSP', 'Ruang UPA LUK/LSP (Lembaga Sertifikasi Profesi) pada Lantai 4 Gedung Rektorat.', 'Administrasi & Layanan', 4, 1, 'rt_upa_luk'),
('Ruang Subbagian Pendanaan Barang dan Jasa', 'Ruang Subbagian Pendanaan Barang dan Jasa pada lantai 4 Gedung Rektorat.', 'Administrasi & Layanan', 4, 1, 'rt_pendanaan'),
('Ruang Simulasi Bank Mini', 'Ruang Simulasi Bank Mini pada lantai 4 Gedung Rektorat.', 'Laboratorium', 4, 1, 'rt_simulasi_bank_mini'),
('Ruang Lembaga Penelitian dan Pengabdian kepada Masyarakat (LPPM)', 'Ruang Lembaga Penelitian dan Pengabdian kepada Masyarakat (LPPM) pada lantai 4 Gedung Rektorat.', 'Administrasi & Layanan', 4, 1, 'rt_lppm'),
('Lembaga Penjaminan Mutu dan Pengembangan Pembelajaran (LPMPP)', 'Ruang Lembaga Penjaminan Mutu dan Pengembangan Pembelajaran (LPMPP) pada lantai 4 Gedung Rektorat.', 'Administrasi & Layanan', 4, 1, 'rt_lpmpp'),
('Auditorium Bhineka Tunggal Ika', 'Auditorium Bhineka Tunggal Ika pada Lantai 4 Gedung Rektorat.', 'Auditorium & Aula', 4, 1, 'rt_auditorium_bki');
-- =============================================================================
-- DATA FASILITAS GEDUNG REKTORAT (id_gedung = 1)
-- =============================================================================
-- =============================================================================
-- DATA FASILITAS GEDUNG MOH. HUSNI THAMRIN (id_gedung = 7)
-- =============================================================================
INSERT INTO public.fasilitas (nama_fasilitas, deskripsi_fasilitas, tipe_fasilitas, lantai, id_gedung, unity_object_name) VALUES
-- Lantai 1
('Ruang Baca dan BI Corner', 'Ruang baca dan BI Corner pada lantai 1 Gedung Moh. Husni Thamrin (FEB).', 'Administrasi & Layanan', 1, 7, 'mt_bi_corner'),
('Ruang Jurusan Ilmu Ekonomi S1 dan Akuntansi', 'Ruang jurusan Ilmu Ekonomi S1 dan Akuntansi pada lantai 1 Gedung Moh. Husni Thamrin.', 'Administrasi & Layanan', 1, 7, 'mt_ekonomi_akutansi'),
('Ruang Himpunan Mahasiswa Jurusan (HMJ) S1 Manajemen', 'Ruang Himpunan Mahasiswa Jurusan (HMJ) S1 Manajemen pada lantai 1 Gedung Moh. Husni Thamrin.', 'Ruang Kegiatan Mahasiswa', 1, 7, 'mt_hmj_manajemen'),
('Ruang Himpunan Mahasiswa Jurusan (HMJ) S1 Akuntansi', 'Ruang Himpunan Mahasiswa Jurusan (HMJ) S1 Akuntansi pada lantai 1 Gedung Moh. Husni Thamrin.', 'Ruang Kegiatan Mahasiswa', 1, 7, 'mt_hmj_akutansi'),
('Ruang Tunggu Dosen FEB', 'Ruang tunggu dosen Fakultas Ekonomi dan Bisnis (FEB) pada lantai 1 Gedung Moh. Husni Thamrin.', 'Administrasi & Layanan', 1, 7, 'mt_ruang_dosen_feb'),
('Ruang LKEB dan Guru Besar', 'Ruang LKEB dan Guru Besar pada lantai 1 Gedung Moh. Husni Thamrin.', 'Administrasi & Layanan', 1, 7, 'mt_lkeb_guru_besar'),
('Ruang Layanan Akademik dan Kemahasiswaan FEB', 'Ruang layanan akademik dan kemahasiswaan Fakultas Ekonomi dan Bisnis pada lantai 1 Gedung Moh. Husni Thamrin. Fasilitas ini umum dikenal atau dicari mahasiswa sebagai Tata Usaha (TU) FEB.', 'Administrasi & Layanan', 1, 7, 'mt_layanan_mahasiswa'),
('Selasar FEB', 'Selasar Fakultas Ekonomi dan Bisnis pada lantai 1 Gedung Moh. Husni Thamrin.', 'Administrasi & Layanan', 1, 7, 'mt_selasar'),
('Ruang Himpunan Mahasiswa (HIMA) Akuntansi, Manajemen, dan Perbankan', 'Ruang Himpunan Mahasiswa (HIMA) Akuntansi S1 dan D3, Manajemen S1, serta Perbankan dan Keuangan D3 pada lantai 1 Gedung Moh. Husni Thamrin.', 'Ruang Kegiatan Mahasiswa', 1, 7, 'mt_hima'),

-- Lantai 2
('Ruang Sekretariat Program Magister Manajemen dan Akuntansi', 'Ruang sekretariat program Magister Manajemen dan Akuntansi pada lantai 2 Gedung Moh. Husni Thamrin.', 'Administrasi & Layanan', 2, 7, 'mt_sekretariat'),
('Ruang Kuliah Program Magister 1', 'Ruang kuliah Program Magister nomor 1 pada lantai 2 Gedung Moh. Husni Thamrin.', 'Ruang Kuliah', 2, 7, 'mt_kuliah_magister_1'),
('Ruang Jurusan Ilmu Ekonomi S1 dan Akuntansi', 'Ruang Jurusan Ilmu Ekonomi S1 dan Jurusan Akuntansi pada lantai 2 Gedung Moh. Husni Thamrin.', 'Administrasi & Layanan', 2, 7, 'mt_ekonomi_akuntansi'),
('Ruang Kuliah Program Magister 2', 'Ruang kuliah Program Magister nomor 2 pada lantai 2 Gedung Moh. Husni Thamrin.', 'Ruang Kuliah', 2, 7, 'mt_kuliah_magister_2'),
('Ruang Kelas 205', 'Ruang perkuliahan 205 di lantai 2 Gedung Moh. Husni Thamrin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 2, 7, 'mt_205'),
('Ruang Kelas 206', 'Ruang perkuliahan 206 di lantai 2 Gedung Moh. Husni Thamrin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 2, 7, 'mt_206'),
('Ruang Kelas 207', 'Ruang perkuliahan 207 di lantai 2 Gedung Moh. Husni Thamrin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 2, 7, 'mt_207'),
('Ruang Kelas 208', 'Ruang perkuliahan 208 di lantai 2 Gedung Moh. Husni Thamrin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 2, 7, 'mt_208'),
('Ruang Kelas 209', 'Ruang perkuliahan 209 di lantai 2 Gedung Moh. Husni Thamrin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 2, 7, 'mt_209'),
('Ruang Kelas 210', 'Ruang perkuliahan 210 di lantai 2 Gedung Moh. Husni Thamrin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 2, 7, 'mt_210'),

-- Lantai 3
('Ruang Mini Company 301', 'Ruang Mini Company atau perusahaan mini di ruang 301 lantai 3 Gedung Moh. Husni Thamrin.', 'Laboratorium', 3, 7, 'mt_mini_company'),
('Mesh Classroom (Ruang 302)', 'Ruang kelas Mesh Classroom di ruang 302 lantai 3 Gedung Moh. Husni Thamrin.', 'Ruang Kuliah', 3, 7, 'mt_mesh'),
('Ruang Kelas 303', 'Ruang perkuliahan 303 di lantai 3 Gedung Moh. Husni Thamrin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 3, 7, 'mt_303'),
('Ruang Kelas 304', 'Ruang perkuliahan 304 di lantai 3 Gedung Moh. Husni Thamrin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 3, 7, 'mt_304'),
('Ruang Kelas 305', 'Ruang perkuliahan 305 di lantai 3 Gedung Moh. Husni Thamrin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 3, 7, 'mt_305'),
('Ruang Kelas 306', 'Ruang perkuliahan 306 di lantai 3 Gedung Moh. Husni Thamrin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 3, 7, 'mt_306'),
('Ruang Kelas 307', 'Ruang perkuliahan 307 di lantai 3 Gedung Moh. Husni Thamrin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 3, 7, 'mt_307'),
('Ruang Kelas 308', 'Ruang perkuliahan 308 di lantai 3 Gedung Moh. Husni Thamrin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 3, 7, 'mt_308'),
('Ruang Kelas 309', 'Ruang perkuliahan 309 di lantai 3 Gedung Moh. Husni Thamrin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 3, 7, 'mt_309'),
('Ruang Kelas 310', 'Ruang perkuliahan 310 di lantai 3 Gedung Moh. Husni Thamrin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 3, 7, 'mt_310'),
('Ruang Kelas 311', 'Ruang perkuliahan 311 di lantai 3 Gedung Moh. Husni Thamrin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 3, 7, 'mt_311'),

-- Lantai 4
('Musala FEB', 'Fasilitas ibadah Fakultas Ekonomi dan Bisnis (FEB) pada lantai 4 Gedung Moh. Husni Thamrin.', 'Fasilitas Ibadah', 4, 7, 'mt_mushola'),
('Ruang Kelas 402', 'Ruang perkuliahan 402 di lantai 4 Gedung Moh. Husni Thamrin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 4, 7, 'mt_402'),
('Ruang Kelas 403', 'Ruang perkuliahan 403 di lantai 4 Gedung Moh. Husni Thamrin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 4, 7, 'mt_403'),
('Ruang Kelas 404', 'Ruang perkuliahan 404 di lantai 4 Gedung Moh. Husni Thamrin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 4, 7, 'mt_404'),
('Ruang Kelas 405', 'Ruang perkuliahan 405 di lantai 4 Gedung Moh. Husni Thamrin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 4, 7, 'mt_405'),
('Ruang Kelas 406', 'Ruang perkuliahan 406 di lantai 4 Gedung Moh. Husni Thamrin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 4, 7, 'mt_406'),
('Ruang Kelas 407', 'Ruang perkuliahan 407 di lantai 4 Gedung Moh. Husni Thamrin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 4, 7, 'mt_407');
-- =============================================================================
-- DATA FASILITAS GEDUNG MOH. HUSNI THAMRIN (id_gedung = 7)
-- =============================================================================
-- =============================================================================
-- DATA FASILITAS GEDUNG DR. SOEPOMO (id_gedung = 2)
-- =============================================================================
INSERT INTO public.fasilitas (nama_fasilitas, deskripsi_fasilitas, tipe_fasilitas, lantai, id_gedung, unity_object_name) VALUES
-- Lantai 1
('Ruang Badan Eksekutif Mahasiswa (BEM) FEB', 'Ruang organisasi Badan Eksekutif Mahasiswa (BEM) Fakultas Ekonomi dan Bisnis (FEB) pada lantai 1 Gedung Dr. Soepomo.', 'Ruang Kegiatan Mahasiswa', 1, 2, 'spm_bem'),
('Ruang Himpunan Mahasiswa (HIMA) Ekonomi Syariah', 'Ruang Himpunan Mahasiswa (HIMA) Ekonomi Syariah pada lantai 1 Gedung Dr. Soepomo.', 'Ruang Kegiatan Mahasiswa', 1, 2, 'spm_hima_ekonomi_syariah'),
('Ruang Himpunan Mahasiswa (HIMA) Perbankan Syariah', 'Ruang Himpunan Mahasiswa (HIMA) Perbankan Syariah pada lantai 1 Gedung Dr. Soepomo.', 'Ruang Kegiatan Mahasiswa', 1, 2, 'spm_hima_ekonomi_perbankan'),
('KSPM dan Galeri Investasi', 'Kelompok Studi Pasar Modal (KSPM) dan Galeri Investasi pada lantai 1 Gedung DR. Soepomo.', 'Administrasi & Layanan', 1, 2, 'spm_kspm'),
('Ruang Dekanat FEB', 'Ruang Dekanat Fakultas Ekonomi dan Bisnis (FEB) pada lantai 1 Gedung DR. Soepomo.', 'Administrasi & Layanan', 1, 2, 'spm_dekanat'),
('Ruang Tata Usaha (TU) FEB', 'Ruang Tata Usaha (TU) Fakultas Ekonomi dan Bisnis untuk layanan administrasi pada lantai 1 Gedung Dr. Soepomo.', 'Administrasi & Layanan', 1, 2, 'spm_tu'),
('Ruang Rapat', 'Ruang Rapat utama pada lantai 1 Gedung DR. Soepomo.', 'Administrasi & Layanan', 1, 2, 'spm_ruang_rapat'),

-- Lantai 2
('Ruang Dosen Manajemen Program Sarjana', 'Ruang Dosen Manajemen Program Sarjana pada lantai 2 Gedung DR. Soepomo.', 'Administrasi & Layanan', 2, 2, 'spm_dosen_manajemen'),
('Laboratorium Komputasi 1', 'Laboratorium Komputasi 1 pada lantai 2 Gedung Dr. Soepomo. Sering disebut Lab Komputasi 1.', 'Laboratorium', 2, 2, 'spm_komputasi_1'),
('Ruang Dosen FEB', 'Ruang dosen Fakultas Ekonomi dan Bisnis (FEB) pada lantai 2 Gedung Dr. Soepomo.', 'Administrasi & Layanan', 2, 2, 'spm_dosen'),
('Ruang Kelas D.201', 'Ruang kelas D.201 pada lantai 2 Gedung Dr. Soepomo.', 'Ruang Kuliah', 2, 2, 'spm_d_201'),
('Ruang Kelas D.202', 'Ruang kelas D.202 pada lantai 2 Gedung Dr. Soepomo.', 'Ruang Kuliah', 2, 2, 'spm_d_202'),


-- Lantai 3
('Laboratorium Komputasi 1 (Lantai 3)', 'Laboratorium Komputasi 1 pada lantai 3 Gedung Dr. Soepomo. Sering disebut Lab Komputasi 1 lantai 3.', 'Laboratorium', 3, 2, 'spm_komputasi_2'), -- di-suffix agar unik
('Laboratorium Komputasi 2 (Lantai 3)', 'Laboratorium Komputasi 2 pada lantai 3 Gedung Dr. Soepomo. Sering disebut Lab Komputasi 2 lantai 3.', 'Laboratorium', 3, 2, 'spm_komputasi_3'),
('Ruang Kelas D.301', 'Ruang kelas D.301 pada lantai 3 Gedung Dr. Soepomo.', 'Ruang Kuliah', 3, 2, 'spm_d_301'),
('Ruang Kelas D.302', 'Ruang kelas D.302 pada lantai 3 Gedung Dr. Soepomo.', 'Ruang Kuliah', 3, 2, 'spm_d_302'),
('Ruang Kelas D.303', 'Ruang kelas D.303 pada lantai 3 Gedung Dr. Soepomo.', 'Ruang Kuliah', 3, 2, 'spm_d_303'),
('Ruang Kelas D.304', 'Ruang kelas D.304 pada lantai 3 Gedung Dr. Soepomo.', 'Ruang Kuliah', 3, 2, 'spm_d_304'),


-- Lantai 4
('Ruang Kelas D.401', 'Ruang kelas D.401 pada lantai 4 Gedung Dr. Soepomo.', 'Ruang Kuliah', 4, 2, 'spm_d_401'),
('Ruang Kelas D.402', 'Ruang kelas D.402 pada lantai 4 Gedung Dr. Soepomo.', 'Ruang Kuliah', 4, 2, 'spm_d_402'),
('Ruang Kelas D.403', 'Ruang kelas D.403 pada lantai 4 Gedung Dr. Soepomo.', 'Ruang Kuliah', 4, 2, 'spm_d_403'),
('Ruang Kelas D.404', 'Ruang kelas D.404 pada lantai 4 Gedung Dr. Soepomo.', 'Ruang Kuliah', 4, 2, 'spm_d_404'),

('Laboratorium Bursa Efek Jakarta 1', 'Laboratorium Bursa Efek Jakarta 1 pada lantai 4 Gedung Dr. Soepomo. Sering disebut Lab Bursa Efek 1.', 'Laboratorium', 4, 2, 'spm_bursa_efek_1'),
('Laboratorium Bursa Efek Jakarta 2', 'Laboratorium Bursa Efek Jakarta 2 pada lantai 4 Gedung Dr. Soepomo. Sering disebut Lab Bursa Efek 2.', 'Laboratorium', 4, 2, 'spm_bursa_efek_2');
-- =============================================================================
-- DATA FASILITAS GEDUNG MUHAMMAD YAMIN (id_gedung = 8)
-- Gedung FISIP (Fakultas Ilmu Sosial dan Ilmu Politik)
-- jumlah_lantai: 4
-- =============================================================================
INSERT INTO public.fasilitas (nama_fasilitas, deskripsi_fasilitas, tipe_fasilitas, lantai, id_gedung, unity_object_name) VALUES
-- Lantai 1
('Lobi dan Pelayanan Mahasiswa FISIP', 'Lobi utama dan area pelayanan akademik serta administrasi mahasiswa Fakultas Ilmu Sosial dan Ilmu Politik pada lantai 1 Gedung Muhammad Yamin. Fasilitas ini umum dikenal atau dicari mahasiswa sebagai Tata Usaha (TU) FISIP.', 'Administrasi & Layanan', 1, 8, 'ymn_lobby'),
('Auditorium FISIP', 'Auditorium Fakultas Ilmu Sosial dan Ilmu Politik untuk seminar, kuliah umum, dan kegiatan akademik pada lantai 1 Gedung Muhammad Yamin.', 'Auditorium & Aula', 1, 8, 'ymn_auditorium'),

-- Lantai 2
('Ruang Staf Program Studi FISIP', 'Ruang staf program studi Fakultas Ilmu Sosial dan Ilmu Politik pada lantai 2 Gedung Muhammad Yamin.', 'Administrasi & Layanan', 2, 8, 'ymn_staff'),
('Ruang Dosen FISIP', 'Ruang dosen Fakultas Ilmu Sosial dan Ilmu Politik pada lantai 2 Gedung Muhammad Yamin.', 'Administrasi & Layanan', 2, 8, 'ymn_dosen'),
('Ruang Guru Besar', 'Ruang Guru Besar Fakultas Ilmu Sosial dan Ilmu Politik pada lantai 2 Gedung Muhammad Yamin.', 'Administrasi & Layanan', 2, 8, 'ymn_guru_besar'),

-- Lantai 3
('Ruang Kelas 301', 'Ruang perkuliahan 301 di lantai 3 Gedung Muhammad Yamin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 3, 8, 'ymn_301'),
('Laboratorium Politik (Ruang 302)', 'Laboratorium politik di ruang 302 untuk pembelajaran dan penelitian bidang ilmu politik pada lantai 3 Gedung Muhammad Yamin. Sering disebut Lab Politik.', 'Laboratorium', 3, 8, 'ymn_302'),
('Ruang Kelas 303', 'Ruang perkuliahan 303 di lantai 3 Gedung Muhammad Yamin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 3, 8, 'ymn_303'),
('Ruang Kelas 304', 'Ruang perkuliahan 304 di lantai 3 Gedung Muhammad Yamin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 3, 8, 'ymn_304'),
('Ruang Kelas 305', 'Ruang perkuliahan 305 di lantai 3 Gedung Muhammad Yamin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 3, 8, 'ymn_305'),
('Ruang Kelas 306', 'Ruang perkuliahan 306 di lantai 3 Gedung Muhammad Yamin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 3, 8, 'ymn_306'),
('Ruang Kelas 307', 'Ruang perkuliahan 307 di lantai 3 Gedung Muhammad Yamin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 3, 8, 'ymn_307'),
('Ruang Kelas 308', 'Ruang perkuliahan 308 di lantai 3 Gedung Muhammad Yamin, digunakan untuk kegiatan belajar mengajar dan dilengkapi proyektor, papan tulis, serta pendingin ruangan.', 'Ruang Kuliah', 3, 8, 'ymn_308'),

('Musala FISIP', 'Fasilitas ibadah Fakultas Ilmu Sosial dan Ilmu Politik (FISIP) pada lantai 3 Gedung Muhammad Yamin.', 'Fasilitas Ibadah', 3, 8, 'ymn_mushola'),
('Ruang Podcast FISIP', 'Ruang podcast FISIP untuk produksi konten audio digital dan penyiaran pada lantai 3 Gedung Muhammad Yamin.', 'Laboratorium', 3, 8, 'ymn_podcast'),

-- Lantai 4
('Laboratorium Fotografi', 'Laboratorium fotografi untuk praktikum dan pengembangan keterampilan fotografi mahasiswa pada lantai 4 Gedung Muhammad Yamin. Sering disebut Lab Fotografi.', 'Laboratorium', 4, 8, 'ymn_fotografi'),
('Laboratorium Sinematografi', 'Laboratorium sinematografi untuk produksi film dan konten visual pada lantai 4 Gedung Muhammad Yamin. Sering disebut Lab Sinematografi.', 'Laboratorium', 4, 8, 'ymn_sinematografi'),
('Laboratorium Televisi dan Radio', 'Laboratorium produksi televisi dan radio pada lantai 4 Gedung Muhammad Yamin. Sering disebut Lab Televisi dan Radio.', 'Laboratorium', 4, 8, 'ymn_televisi'),
('Laboratorium Multimedia FISIP', 'Laboratorium multimedia FISIP untuk praktikum dan pengembangan konten digital pada lantai 4 Gedung Muhammad Yamin. Sering disebut Lab Multimedia FISIP.', 'Laboratorium', 4, 8, 'ymn_multimedia'),
('Laboratorium Big Data FISIP', 'Laboratorium big data FISIP untuk praktikum dan penelitian analisis data pada lantai 4 Gedung Muhammad Yamin. Sering disebut Lab Big Data FISIP.', 'Laboratorium', 4, 8, 'ymn_big_data');
WITH cipto AS (
    SELECT id FROM public.gedung WHERE nama_gedung ILIKE '%Cipto%' LIMIT 1
)
INSERT INTO public.fasilitas (id_gedung, nama_fasilitas, lantai, unity_object_name, deskripsi_fasilitas)
SELECT cipto.id, data.nama, data.lt, data.unity, data.deskripsi
FROM cipto, (VALUES
    -- Lantai 1
    ('Perpustakaan', 1, 'cpt_perpustakaan', 'Perpustakaan di lantai 1 Gedung Dr. Cipto Mangunkusumo untuk layanan koleksi dan ruang baca Fakultas Kedokteran.'),
    ('Laboratorium Histologi dan Patologi', 1, 'cpt_histologi_patologi', 'Laboratorium Histologi dan Patologi di lantai 1 Gedung Dr. Cipto Mangunkusumo. Sering disebut Lab Histologi dan Patologi.'),
    ('Laboratorium Komputer', 1, 'cpt_komputer', 'Laboratorium Komputer untuk kegiatan akademik di lantai 1 Gedung Dr. Cipto Mangunkusumo. Sering disebut Lab Komputer.'),
    ('Ruang Medical Information and Technology Education and Communication (MITECH)', 1, 'cpt_mitech', 'Ruang Medical Information and Technology Education and Communication (MITECH) di lantai 1 Gedung Dr. Cipto Mangunkusumo untuk kegiatan unit tersebut.'),
    ('Ruang Kepala Laboratorium Histologi dan Patologi', 1, 'cpt_kalab_histologi_patologi', 'Ruang kerja Kepala Laboratorium Histologi dan Patologi di lantai 1 Gedung Dr. Cipto Mangunkusumo. Kepala Laboratorium sering disebut Kalab.'),
    ('Laboratorium Farmakologi dan Farmasi Klinik', 1, 'cpt_lab_farmakologi_farmasi_klinik', 'Laboratorium Farmakologi dan Farmasi Klinik di lantai 1 Gedung Dr. Cipto Mangunkusumo. Sering disebut Lab Farmakologi dan Farmasi Klinik.'),
    ('Student Lounge (Ruang Santai Mahasiswa)', 1, 'cpt_student_lounge', 'Student lounge atau ruang santai mahasiswa di lantai 1 Gedung Dr. Cipto Mangunkusumo.'),

    -- Lantai 2
    ('Ruang Medical Education Unit (MEU)', 2, 'cpt_medical_education_unit', 'Ruang Medical Education Unit (MEU) untuk pengembangan pendidikan kedokteran di lantai 2 Gedung Dr. Cipto Mangunkusumo.'),
    ('Ruang Pertemuan Tutor (Tutor Meeting)', 2, 'cpt_tutor', 'Ruang pertemuan tutor atau tutor meeting di lantai 2 Gedung Dr. Cipto Mangunkusumo.'),
('Ruang Tutorial A1', 2, 'cpt_tutorial_a_1', 'Ruang Tutorial A1 untuk kegiatan pembelajaran di lantai 2 Gedung Dr. Cipto Mangunkusumo.'),
    ('Ruang Tutorial A2', 2, 'cpt_tutorial_a_2', 'Ruang Tutorial A2 untuk kegiatan pembelajaran di lantai 2 Gedung Dr. Cipto Mangunkusumo.'),
    ('Ruang Tutorial A3', 2, 'cpt_tutorial_a_3', 'Ruang Tutorial A3 untuk kegiatan pembelajaran di lantai 2 Gedung Dr. Cipto Mangunkusumo.'),
    ('Ruang Tutorial A4', 2, 'cpt_tutorial_a_4', 'Ruang Tutorial A4 untuk kegiatan pembelajaran di lantai 2 Gedung Dr. Cipto Mangunkusumo.'),
('Ruang Tutorial B1', 2, 'cpt_tutorial_b_1', 'Ruang Tutorial B1 untuk kegiatan pembelajaran di lantai 2 Gedung Dr. Cipto Mangunkusumo.'),
    ('Ruang Tutorial B2', 2, 'cpt_tutorial_b_2', 'Ruang Tutorial B2 untuk kegiatan pembelajaran di lantai 2 Gedung Dr. Cipto Mangunkusumo.'),
    ('Ruang Tutorial B3', 2, 'cpt_tutorial_b_3', 'Ruang Tutorial B3 untuk kegiatan pembelajaran di lantai 2 Gedung Dr. Cipto Mangunkusumo.'),
    ('Ruang Tutorial B4', 2, 'cpt_tutorial_b_4', 'Ruang Tutorial B4 untuk kegiatan pembelajaran di lantai 2 Gedung Dr. Cipto Mangunkusumo.'),
('Ruang Tutorial C1', 2, 'cpt_tutorial_c_1', 'Ruang Tutorial C1 untuk kegiatan pembelajaran di lantai 2 Gedung Dr. Cipto Mangunkusumo.'),
    ('Ruang Tutorial C2', 2, 'cpt_tutorial_c_2', 'Ruang Tutorial C2 untuk kegiatan pembelajaran di lantai 2 Gedung Dr. Cipto Mangunkusumo.'),
    ('Ruang Tutorial C3', 2, 'cpt_tutorial_c_3', 'Ruang Tutorial C3 untuk kegiatan pembelajaran di lantai 2 Gedung Dr. Cipto Mangunkusumo.'),
    ('Ruang Tutorial C4', 2, 'cpt_tutorial_c_4', 'Ruang Tutorial C4 untuk kegiatan pembelajaran di lantai 2 Gedung Dr. Cipto Mangunkusumo.'),
('Ruang Tutorial D1', 2, 'cpt_tutorial_d_1', 'Ruang Tutorial D1 untuk kegiatan pembelajaran di lantai 2 Gedung Dr. Cipto Mangunkusumo.'),
    ('Ruang Tutorial D2', 2, 'cpt_tutorial_d_2', 'Ruang Tutorial D2 untuk kegiatan pembelajaran di lantai 2 Gedung Dr. Cipto Mangunkusumo.'),
    ('Ruang Tutorial D3', 2, 'cpt_tutorial_d_3', 'Ruang Tutorial D3 untuk kegiatan pembelajaran di lantai 2 Gedung Dr. Cipto Mangunkusumo.'),
    ('Ruang Tutorial D4', 2, 'cpt_tutorial_d_4', 'Ruang Tutorial D4 untuk kegiatan pembelajaran di lantai 2 Gedung Dr. Cipto Mangunkusumo.'),
    ('Ruang Program Studi Biologi dan Redaksi Jurnal Profesi Medika', 2, 'cpt_biologi_jurnal', 'Ruang Program Studi Biologi dan Redaksi Jurnal Profesi Medika di lantai 2 Gedung Dr. Cipto Mangunkusumo.'),

    -- Lantai 3
    ('Pusat Objective Structured Clinical Examination (OSCE)/Laboratorium Keterampilan Klinis B', 3, 'cpt_osce', 'Pusat Objective Structured Clinical Examination (OSCE) sekaligus Laboratorium Keterampilan Klinis B di lantai 3 Gedung Dr. Cipto Mangunkusumo. Laboratorium ini juga dicari sebagai Lab Keterampilan Klinis B.'),
    ('Ruang Penyimpanan Manekin 1', 3, 'cpt_penyimpanan_manekin_1', 'Ruang Penyimpanan Manekin 1 di lantai 3 Gedung Dr. Cipto Mangunkusumo untuk mendukung kegiatan keterampilan klinis.'),
    ('Ruang Penyimpanan Manekin 2', 3, 'cpt_penyimpanan_manekin_2', 'Ruang Penyimpanan Manekin 2 di lantai 3 Gedung Dr. Cipto Mangunkusumo untuk mendukung kegiatan keterampilan klinis.'),
    ('Ruang Instruktur Keterampilan Klinis', 3, 'cpt_instruktur_keterampilan', 'Ruang instruktur keterampilan klinis di lantai 3 Gedung Dr. Cipto Mangunkusumo.'),
    ('Ruang Manekin', 3, 'cpt_manekin', 'Ruang Manekin di lantai 3 Gedung Dr. Cipto Mangunkusumo untuk mendukung kegiatan keterampilan klinis.'),
    ('Laboratorium Keterampilan Klinis A (Skills Lab)', 3, 'cpt_skills', 'Laboratorium Keterampilan Klinis A di lantai 3 Gedung Dr. Cipto Mangunkusumo. Dikenal juga sebagai Skills Lab atau Lab Keterampilan Klinis A.'),

    -- Lantai 4
    ('Pusat Computer-Based Test (CBT)', 4, 'cpt_cbt', 'Pusat Computer-Based Test (CBT) untuk pelaksanaan ujian berbasis komputer di lantai 4 Gedung Dr. Cipto Mangunkusumo.'),
    ('Ruang Kuliah A (Lecture A)', 4, 'cpt_lecture_a', 'Ruang Kuliah A atau Lecture A di lantai 4 Gedung Dr. Cipto Mangunkusumo.'),
    ('Ruang Kuliah B (Lecture B)', 4, 'cpt_lecture_b', 'Ruang Kuliah B atau Lecture B di lantai 4 Gedung Dr. Cipto Mangunkusumo.'),
    ('Aula', 4, 'cpt_aula', 'Aula di lantai 4 Gedung Dr. Cipto Mangunkusumo yang juga digunakan untuk kegiatan sidang.'),
    ('Ruang Kuliah Mini 2 (Mini Lecture)', 4, 'cpt_mini_lecture_2', 'Ruang Kuliah Mini 2 atau Mini Lecture 2 di lantai 4 Gedung Dr. Cipto Mangunkusumo.'),
    ('Ruang Kuliah Mini 3 (Mini Lecture)', 4, 'cpt_mini_lecture_3', 'Ruang Kuliah Mini 3 atau Mini Lecture 3 di lantai 4 Gedung Dr. Cipto Mangunkusumo.')
) AS data(nama, lt, unity, deskripsi);

-- =============================================================================
-- STANDARDISASI TIPE FASILITAS GEDUNG DR. CIPTO MANGUNKUSUMO (id_gedung = 4)
-- Baris Cipto di atas di-insert tanpa tipe_fasilitas (NULL). Kita tetapkan
-- tipe yang dikenali dashboard berdasarkan nama fasilitas.
-- =============================================================================
UPDATE public.fasilitas
SET tipe_fasilitas = CASE
    WHEN nama_fasilitas ILIKE '%CBT%'                                   THEN 'Ruang Kuliah'
    WHEN nama_fasilitas ILIKE '%Lecture%'                               THEN 'Ruang Kuliah'
    WHEN nama_fasilitas ILIKE 'Aula%'                                   THEN 'Auditorium & Aula'
    WHEN nama_fasilitas ILIKE '%Tutorial%' OR nama_fasilitas ILIKE 'Tutor Meeting%' THEN 'Ruang Kuliah'
    WHEN nama_fasilitas ILIKE 'Student Lounge%'                         THEN 'Administrasi & Layanan'
    WHEN nama_fasilitas ILIKE 'Perpustakaan%'                           THEN 'Perpustakaan & Ruang Baca'
    WHEN nama_fasilitas ILIKE '%MITECH%'                                THEN 'Laboratorium'
    WHEN nama_fasilitas ILIKE '%Lab%'
      OR nama_fasilitas ILIKE 'Laboratorium%'
      OR nama_fasilitas ILIKE '%OSCE%'
      OR nama_fasilitas ILIKE '%Manekin%'
      OR nama_fasilitas ILIKE '%Skills%'
      OR nama_fasilitas ILIKE '%keterampilan klinis%'                   THEN 'Laboratorium'
    ELSE 'Lainnya'
END
WHERE id_gedung = (SELECT id FROM public.gedung WHERE nama_gedung ILIKE '%Cipto%' LIMIT 1)
  AND tipe_fasilitas IS NULL;

-- =============================================================================
-- RESTORE FASILITAS DENGAN UNITY OBJECT NAME DARI RIWAYAT SEED
-- =============================================================================
-- Baris berikut pernah ada di seed dan mempunyai target GameObject Unity, tetapi
-- terhapus saat pembersihan/penyusunan ulang data. Alias lama untuk fasilitas
-- yang masih ada dengan nama canonical baru sengaja tidak diduplikasi.
INSERT INTO public.fasilitas (
    nama_fasilitas,
    deskripsi_fasilitas,
    tipe_fasilitas,
    lantai,
    foto_url,
    id_gedung,
    unity_object_name
) VALUES
-- Gedung 6: Gedung Ki Hadjar Dewantara
(
    'Ruang Rapat Lantai 1 FIK',
    'Ruang rapat Fakultas Ilmu Komputer di lantai 1 Gedung Ki Hadjar Dewantara.',
    'Administrasi & Layanan',
    1,
    NULL,
    6,
    'khd_ruang_rapat'
),

-- Gedung 7: Gedung Muh. Husni Thamrin
(
    'Ruang Kelas 201',
    'Ruang perkuliahan untuk kegiatan belajar mengajar mahasiswa Fakultas Ekonomi dan Bisnis, dilengkapi kursi kuliah, papan tulis, proyektor, dan pendingin ruangan.',
    'Ruang Kuliah',
    2,
    NULL,
    7,
    'mht_201'
),
(
    'Ruang Kelas 202',
    'Ruang perkuliahan untuk kegiatan belajar mengajar mahasiswa Fakultas Ekonomi dan Bisnis, dilengkapi kursi kuliah, papan tulis, proyektor, dan pendingin ruangan.',
    'Ruang Kuliah',
    2,
    NULL,
    7,
    'mht_202'
),
(
    'Ruang Kelas 203',
    'Ruang perkuliahan untuk kegiatan belajar mengajar mahasiswa Fakultas Ekonomi dan Bisnis, dilengkapi kursi kuliah, papan tulis, proyektor, dan pendingin ruangan.',
    'Ruang Kuliah',
    2,
    NULL,
    7,
    'mht_203'
),
(
    'Ruang Kelas 204',
    'Ruang perkuliahan untuk kegiatan belajar mengajar mahasiswa Fakultas Ekonomi dan Bisnis, dilengkapi kursi kuliah, papan tulis, proyektor, dan pendingin ruangan.',
    'Ruang Kuliah',
    2,
    NULL,
    7,
    'mht_204'
),
(
    'Ruang Kelas 301',
    'Ruang perkuliahan untuk kegiatan belajar mengajar mahasiswa Fakultas Ekonomi dan Bisnis, dilengkapi kursi kuliah, papan tulis, proyektor, dan pendingin ruangan.',
    'Ruang Kuliah',
    3,
    NULL,
    7,
    'mht_301'
),

-- Gedung 9: Gedung Yos Sudarso
(
    'Ruang Pelayanan Mahasiswa FH',
    'Ruang pelayanan dan administrasi mahasiswa Fakultas Hukum di lantai 1 Gedung Yos Sudarso.',
    'Administrasi & Layanan',
    1,
    'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/fasilitas/yos%20sudarso/ruang_administrasi_yos_sudarso.png',
    9,
    'yos_ruang_pelayanan_mahasiswa_fh'
),
(
    'Ruang Transit Dosen FH',
    'Ruang tunggu dan transit bagi dosen Fakultas Hukum.',
    'Administrasi & Layanan',
    1,
    NULL,
    9,
    'yos_ruang_transit_dosen'
),
(
    'Lobby Yos Sudarso',
    'Area penerimaan tamu dan lobby utama Gedung Yos Sudarso.',
    'Lainnya',
    1,
    NULL,
    9,
    'yos_lobby'
),
(
    'Ruang BEM dan Senat FH',
    'Ruang sekretariat Badan Eksekutif Mahasiswa dan Senat Mahasiswa Fakultas Hukum.',
    'Ruang Kegiatan Mahasiswa',
    1,
    NULL,
    9,
    'yos_ruang_bem_dan_senat_fh'
),
(
    'Ruang Dosen Pidana',
    'Ruang kerja khusus dosen hukum pidana.',
    'Administrasi & Layanan',
    1,
    NULL,
    9,
    'yos_ruang_dosen_pidana'
),
(
    'Ruang Dosen FH (Pintu 1)',
    'Ruang dosen Fakultas Hukum dengan akses melalui pintu utama.',
    'Administrasi & Layanan',
    1,
    NULL,
    9,
    'yos_ruang_dosen_1'
),
(
    'Ruang Dosen FH (Pintu 2)',
    'Ruang dosen Fakultas Hukum dengan akses melalui pintu alternatif.',
    'Administrasi & Layanan',
    1,
    NULL,
    9,
    'yos_ruang_dosen_2'
),
(
    'Selasar Fakultas Hukum',
    'Area selasar dan lorong utama Fakultas Hukum.',
    'Lainnya',
    1,
    'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/fasilitas/yos%20sudarso/selasar_kanan_yos_sudarso.jpg',
    9,
    'yos_selasar'
),
(
    'Laboratorium Perancangan Kontrak',
    'Laboratorium Perancangan Kontrak pada lantai 2 Gedung Yos Sudarso.',
    'Laboratorium',
    2,
    'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/fasilitas/yos%20sudarso/lab_perancangan_kontrak.jpg',
    9,
    'yos_ruang_perancangan_kontrak'
),
(
    'Ruang Dosen Perdata dan Bisnis',
    'Ruang kerja khusus dosen hukum perdata dan hukum bisnis.',
    'Administrasi & Layanan',
    2,
    NULL,
    9,
    'yos_ruang_dosen_perdata_dan_bisnis'
),
(
    'Ruang Forum Riset & Debat Mahasiswa',
    'Ruangan untuk kegiatan riset dan latihan debat hukum mahasiswa.',
    'Ruang Kegiatan Mahasiswa',
    2,
    NULL,
    9,
    'yos_ruang_forum_riset_dan_debat_mahasiswa'
),
(
    'Ruang Kelas 201',
    'Ruang kelas teori 201 Gedung Yos Sudarso.',
    'Ruang Kuliah',
    2,
    NULL,
    9,
    'yos_kelas_201'
),
(
    'Ruang Kelas 202',
    'Ruang kelas teori 202 Gedung Yos Sudarso.',
    'Ruang Kuliah',
    2,
    NULL,
    9,
    'yos_kelas_202'
),
(
    'Ruang Kelas 203',
    'Ruang kelas teori 203 Gedung Yos Sudarso.',
    'Ruang Kuliah',
    2,
    NULL,
    9,
    'yos_kelas_203'
),
(
    'Ruang Kelas 204',
    'Ruang kelas teori 204 Gedung Yos Sudarso.',
    'Ruang Kuliah',
    2,
    NULL,
    9,
    'yos_kelas_204'
),
(
    'Ruang Kelas 205',
    'Ruang kelas teori 205 Gedung Yos Sudarso.',
    'Ruang Kuliah',
    2,
    NULL,
    9,
    'yos_kelas_205'
),
(
    'Perpustakaan Fakultas Hukum',
    'Fasilitas perpustakaan dan ruang baca Fakultas Hukum di lantai 3 Gedung Yos Sudarso.',
    'Perpustakaan & Ruang Baca',
    3,
    'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/fasilitas/yos%20sudarso/ruang_baca_yos_sudarso.jpg',
    9,
    'yos_perpustakaan_fh'
),
(
    'Ruang Asosiasi Mahasiswa Hukum Internasional',
    'Ruang sekretariat Asosiasi Mahasiswa Hukum Internasional.',
    'Ruang Kegiatan Mahasiswa',
    3,
    NULL,
    9,
    'yos_ruang_asosiasi_mahasiswa_hukum_internasional'
),
(
    'Ruang Kelas 301',
    'Ruang kelas teori 301 Gedung Yos Sudarso.',
    'Ruang Kuliah',
    3,
    NULL,
    9,
    'yos_kelas_301'
),
(
    'Ruang Kelas 302',
    'Ruang kelas teori 302 Gedung Yos Sudarso.',
    'Ruang Kuliah',
    3,
    NULL,
    9,
    'yos_kelas_302'
),
(
    'Ruang Kelas 303',
    'Ruang kelas teori 303 Gedung Yos Sudarso.',
    'Ruang Kuliah',
    3,
    NULL,
    9,
    'yos_kelas_303'
),
(
    'Ruang Kelas 304',
    'Ruang kelas teori 304 Gedung Yos Sudarso.',
    'Ruang Kuliah',
    3,
    NULL,
    9,
    'yos_kelas_304'
),
(
    'Ruang Kelas 305',
    'Ruang kelas teori 305 Gedung Yos Sudarso.',
    'Ruang Kuliah',
    3,
    NULL,
    9,
    'yos_kelas_305'
),
(
    'Ruang Kelas 306',
    'Ruang kelas teori 306 Gedung Yos Sudarso.',
    'Ruang Kuliah',
    3,
    NULL,
    9,
    'yos_kelas_306'
),
(
    'Ruang Kelas 307',
    'Ruang kelas teori 307 Gedung Yos Sudarso.',
    'Ruang Kuliah',
    3,
    NULL,
    9,
    'yos_kelas_307'
),
(
    'Ruang Podcast Yos Sudarso',
    'Ruang podcast Fakultas Hukum pada lantai 4 Gedung Yos Sudarso.',
    'Laboratorium',
    4,
    'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/fasilitas/yos%20sudarso/ruang_praktik_peradilan_semu.png',
    9,
    'yos_podcast'
),
(
    'Ruang Praktik Peradilan Semu 1',
    'Ruang sidang untuk praktik peradilan semu Fakultas Hukum.',
    'Lainnya',
    4,
    'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/fasilitas/yos%20sudarso/ruang_praktik_peradilan_semu.png',
    9,
    'yos_praktek_peradilan_semu_1'
),
(
    'Unit Peradilan Semu',
    'Ruangan administrasi dan persiapan Unit Peradilan Semu Fakultas Hukum.',
    'Administrasi & Layanan',
    4,
    NULL,
    9,
    'yos_unit_peradilan_semu'
),
(
    'Ruang Praktik Peradilan Semu 2',
    'Ruang sidang untuk praktik peradilan semu Fakultas Hukum.',
    'Lainnya',
    4,
    NULL,
    9,
    'yos_praktek_peradilan_semu_2'
),

-- Gedung 13: Gedung Dewi Sartika
(
    'Lapangan dan Alat Olahraga FIK',
    'Fasilitas olahraga yang terletak di depan Gedung Dewi Sartika.',
    'Fasilitas Olahraga',
    1,
    'https://aaysacqsibquiulpdzwz.supabase.co/storage/v1/object/public/Gambar%20Gedung%20dan%20Fasilitas/fasilitas/dewi%20sartika/lapangan_dan_alat_olahraga_fik.jpg',
    13,
    'ds_lapangan'
),
(
    'Ruang UKM Sepak Bola',
    'Ruang sekretariat dan kegiatan UKM Sepak Bola di Gedung Dewi Sartika.',
    'Ruang Kegiatan Mahasiswa',
    1,
    NULL,
    13,
    'ds_ukm_sepak_bola'
),
(
    'Ruang Kuliah 204',
    'Ruang perkuliahan di lantai 2 Gedung Dewi Sartika untuk kegiatan belajar mengajar mahasiswa Fakultas Ilmu Komputer.',
    'Ruang Kuliah',
    2,
    NULL,
    13,
    'ds_204'
),
(
    'Ruang Kuliah 304',
    'Ruang perkuliahan di lantai 3 Gedung Dewi Sartika untuk kegiatan belajar mengajar mahasiswa Fakultas Ilmu Komputer.',
    'Ruang Kuliah',
    3,
    NULL,
    13,
    'ds_304'
),
(
    'Ruang Kuliah 404',
    'Ruang perkuliahan di lantai 4 Gedung Dewi Sartika untuk kegiatan belajar mengajar mahasiswa Fakultas Ilmu Komputer.',
    'Ruang Kuliah',
    4,
    NULL,
    13,
    'ds_404'
);
