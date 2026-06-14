# INTEGRASI DATA SPASIAL DAN VISUALISASI DENAH VIRTUAL 3D KAMPUS UNIVERSITAS PEMBANGUNAN NASIONAL VETERAN JAKARTA KAMPUS PONDOK LABU BERBASIS WEB FULL STACK

**Muhammad Iman Nugraha**  
NIM: 2210511129  
Program Studi Informatika, Fakultas Ilmu Komputer  
Universitas Pembangunan Nasional Veteran Jakarta  
*Email: muhammadimannugraha@mahasiswa.upnvj.ac.id*

---

## ABSTRAK

Kesulitan navigasi spasial dan fragmentasi informasi mengenai fasilitas akademik di Universitas Pembangunan Nasional Veteran Jakarta (UPNVJ) Kampus Pondok Labu merupakan permasalahan nyata bagi mahasiswa baru dan pengunjung. Penelitian ini bertujuan untuk mengintegrasikan data spasial kampus dan visualisasinya melalui pengembangan sistem terpadu berupa Dashboard Profil UPNVJ dan Denah Virtual 3D Kampus. Fokus bahasan dalam artikel ilmiah ini adalah pada arsitektur *web full stack* dan integrasi sistem yang menjadi kontribusi utama penulis. Sistem *frontend* dibangun sebagai *Single Page Application* (SPA) menggunakan React.js dan Vite, sementara *backend* dikembangkan sebagai *RESTful API* menggunakan Express.js yang dideploy pada *Vercel Serverless Functions*. Penyimpanan data dinamis dikelola menggunakan PostgreSQL pada *Supabase Cloud* dengan penerapan keamanan tingkat basis data melalui *Row-Level Security* (RLS) dan trigger otomatis *audit logs* untuk menjamin akuntabilitas data. Integrasi dengan simulator 3D Unity WebGL dijembatani secara reaktif menggunakan pustaka *react-unity-webgl* melalui mekanisme *bridge* JavaScript-C# *SendMessage*. Pemantauan lalu lintas *web* diintegrasikan secara mandiri (*self-hosted*) menggunakan *Umami Analytics* yang diakses melalui *reverse proxy* Express.js guna mengamankan data metrik. Pengujian sistem menggunakan metode *Black Box Testing* dan *User Acceptance Testing* (UAT) menunjukkan tingkat penerimaan pengguna yang sangat baik serta efisiensi dalam penyajian rute navigasi terintegrasi.

**Kata Kunci:** *Web Full Stack*, React, Supabase, Row-Level Security, Unity WebGL, Integrasi Sistem.

---

## ABSTRACT

*Spatial navigation difficulties and fragmentation of information regarding academic facilities at the Universitas Pembangunan Nasional Veteran Jakarta (UPNVJ) Pondok Labu Campus present challenges for new students and visitors. This study aims to integrate campus spatial data and its visualization through the development of an integrated system consisting of the UPNVJ Profile Dashboard and a 3D Virtual Campus Map. The focus of this scientific article is on the web full stack architecture and system integration, which represents the author's primary contribution. The frontend system is built as a Single Page Application (SPA) using React.js and Vite, while the backend is developed as a RESTful API using Express.js deployed on Vercel Serverless Functions. Dynamic data storage is managed using PostgreSQL on Supabase Cloud, incorporating database-level security through Row-Level Security (RLS) and automatic audit log triggers to ensure data accountability. Integration with the Unity WebGL 3D simulator is reactively bridged using the react-unity-webgl library via the JavaScript-C# SendMessage bridge mechanism. Web traffic monitoring is self-hosted using Umami Analytics, accessed via an Express.js reverse proxy to secure metric data. System testing using Black Box Testing and User Acceptance Testing (UAT) indicates an excellent user acceptance rate and high efficiency in providing integrated navigation routes.*

**Keywords:** *Web Full Stack*, React, Supabase, Row-Level Security, Unity WebGL, System Integration.

---

## I. PENDAHULUAN

Transformasi digital pada institusi pendidikan tinggi telah mendorong adopsi teknologi informasi secara menyeluruh untuk mendukung layanan akademik dan manajemen fasilitas (Ghai, 2025). Universitas Pembangunan Nasional Veteran Jakarta (UPNVJ) Kampus Pondok Labu memiliki area fisik yang luas dengan struktur gedung yang kompleks. Berdasarkan survei awal yang disebarkan kepada 21 responden mahasiswa, ditemukan bahwa 95.2% pernah mengalami kesulitan dalam mencari lokasi atau gedung tertentu di dalam kampus. Hal ini disebabkan oleh media navigasi eksisting yang masih bersifat pasif, seperti denah statis berbasis gambar/PDF atau papan arah fisik yang tidak fleksibel untuk diperbarui (Siv, 2025).

Selain kendala navigasi fisik, informasi mengenai profil kampus seperti data dosen, fasilitas ruangan, dan status akreditasi program studi masih tersimpan secara terfragmentasi pada berbagai sub-situs web UPNVJ. Fenomena fragmentasi data ini mengakibatkan inefisiensi akses informasi bagi sivitas akademika maupun pihak luar (Jamaludin & Saepuloh, 2024).

Sebagai solusi terpadu, dikembangkan proyek kolaboratif "Integrasi Denah Virtual Universitas Pembangunan Nasional Veteran Jakarta Kampus Pondok Labu (Dashboard Profil)". Proyek ini membagi peran pengembang menjadi tiga: 3D Asset Designer (mengonfigurasi aset 3D secara presisi langsung di Unity Editor), 3D Simulator & Engine Developer (mengelola NavMesh pathfinding dan interaksi simulator di Unity), serta Full Stack Web Developer & System Integrator (penulis) yang membangun arsitektur data, API, serta antarmuka web.

Artikel ilmiah ini berfokus secara eksklusif pada kontribusi penulis selaku Full Stack Web Developer & System Integrator, yang mencakup:
1. Pembangunan *database* PostgreSQL pada *Supabase Cloud* dengan skema relasional, konfigurasi *Row-Level Security* (RLS), dan trigger pencatatan *audit logs* (Putra dkk., 2026).
2. Pengembangan *RESTful API* berbasis *Serverless Functions* di Vercel.
3. Pengembangan *Single Page Application* (SPA) menggunakan React.js dan Vite dengan fitur penanganan koneksi lambat (*connection-aware preloading*) serta *multi-language* dinamis (Pricillia & Zulfachmi, 2021).
4. Integrasi *two-way communication bridge* antara React dan simulator Unity WebGL (react-unity-webgl).
5. Implementasi *reverse proxy* untuk *self-hosted Umami Analytics*.

---

## II. LANDASAN TEORI

### A. Metode Prototyping
Pengembangan perangkat lunak dengan metode *prototyping* adalah pendekatan iteratif di mana model kerja awal (prototipe) dibangun secara cepat untuk mengevaluasi kebutuhan dan memperoleh umpan balik pengguna secara berkesinambungan (Syarif & Risdiansyah, 2024). Metode ini sangat efektif untuk sistem yang mengintegrasikan berbagai platform karena meminimalkan risiko diskrepansi kebutuhan antara pihak pengembang dan pengguna akhir (Pricillia & Zulfachmi, 2021).

### B. Supabase Cloud dan Row-Level Security (RLS)
Supabase merupakan platform *backend-as-a-service* (BaaS) berbasis PostgreSQL (Putra dkk., 2026). PostgreSQL menyediakan fitur keamanan tangguh berupa *Row-Level Security* (RLS), yang memungkinkan administrator basis data menerapkan kebijakan akses (kebijakan keamanan) secara dinamis langsung pada baris data tabel berdasarkan identitas pengguna (JWT) yang terautentikasi (Putra dkk., 2026). Hal ini meminimalkan celah keamanan dari bypass API di sisi client.

### C. Single Page Application (SPA) dan React
*Single Page Application* (SPA) adalah arsitektur aplikasi web yang memuat satu dokumen HTML awal dan memperbarui antarmuka pengguna secara dinamis melalui JavaScript tanpa memerlukan pemuatan ulang (*page reload*) seluruh halaman dari server (Pricillia & Zulfachmi, 2021). React.js digunakan sebagai pustaka basis komponen untuk merancang antarmuka pengguna yang reaktif dan berkinerja tinggi.

### D. Integrasi WebGL dan react-unity-webgl
Unity WebGL memungkinkan aplikasi simulator interaktif 3D dijalankan di dalam peramban web tanpa memerlukan plugin tambahan. Integrasi antara React dan runtime Unity WebGL dijembatani oleh pustaka *react-unity-webgl* yang membungkus container WebGL dan memetakan fungsi komunikasi JavaScript-C# melalui panggilan `unityInstance.SendMessage()`.

---

## III. METODOLOGI DAN PERANCANGAN SISTEM

### A. Arsitektur Implementasi Sistem
Sistem yang dibangun menggunakan arsitektur modular empat-lapisan (4-tier architecture):
1. **Presentation Layer (Web Client):** Terdiri dari React SPA (Dashboard Profil) dan simulator Unity WebGL.
2. **Integration/Proxy Layer:** Menjembatani request client dan mengamankan traffic analytics via port 3001.
3. **Application Services Layer (Serverless API):** Express.js server yang dideploy sebagai Vercel Serverless Functions.
4. **Data Layer (Cloud Database):** PostgreSQL yang diinangi pada Supabase Cloud.

Arsitektur aliran data diilustrasikan pada diagram blok berikut:

```
[ React SPA Frontend ] <---> [ react-unity-webgl ] <---> [ Unity WebGL Simulator ]
         |                                                        |
         +--------------------+-----------------------------------+
                              | (REST API via HTTPS JSON)
                              v
                [ Express Serverless API ]
                              | (PostgreSQL Client Connection)
                              v
                  [ Supabase Cloud Database ]
```

### B. Perancangan Basis Data
Basis data PostgreSQL dirancang secara relasional untuk menyimpan konfigurasi spasial gedung dan fasilitas pendukung. Relasi tabel dirancang dengan *foreign key* `unity_object_name` yang memetakan record database secara langsung ke hierarki nama objek visual 3D di Unity Editor. Skema relasi database (ERD) mencakup tabel `fakultas`, `prodi`, `gedung`, `ruangan`, `fasilitas`, dan `audit_logs`.

Kebijakan keamanan RLS dikonfigurasi sebagai berikut:
- **Tabel Publik (`gedung`, `ruangan`, `fasilitas`):** Kebijakan SELECT diperbolehkan bagi semua pengguna (*anon*). Kebijakan INSERT, UPDATE, DELETE hanya diizinkan untuk admin terotentikasi (`authenticated`).
- **Tabel `audit_logs`:** Bersifat *insert-only* melalui trigger basis data setiap kali terjadi manipulasi data pada tabel lainnya.

---

## IV. HASIL DAN PEMBAHASAN

### A. Implementasi Backend Serverless & Keamanan Database
*Backend* RESTful API dideploy pada Vercel Serverless Functions menggunakan runtime Node.js dan Express.js. Beberapa endpoint utama diimplementasikan untuk menyediakan data bagi Unity dan frontend React:
- `GET /api/unity/data`: Mengembalikan representasi objek gedung dan koordinat serta parameter `unity_object_name` dalam bentuk JSON.
- `GET /api/buildings` dan `GET /api/rooms`: Menyediakan daftar detail gedung dan fasilitas ruangan untuk public dashboard.

Pada Supabase Cloud, RLS diaktifkan pada semua tabel penting. Contoh SQL DDL penerapan RLS dan trigger audit logs:

```sql
-- Mengaktifkan RLS pada tabel gedung
ALTER TABLE gedung ENABLE ROW LEVEL SECURITY;

-- Kebijakan akses SELECT publik
CREATE POLICY "Allow public select" ON gedung FOR SELECT TO anon USING (true);

-- Kebijakan manipulasi data admin
CREATE POLICY "Allow admin write" ON gedung FOR ALL TO authenticated 
  USING (auth.role() = 'authenticated') 
  WITH CHECK (auth.role() = 'authenticated');

-- Trigger mencatat log perubahan ke audit_logs
CREATE OR REPLACE FUNCTION log_data_mutation()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO audit_logs (table_name, operation, record_id, changed_by, changed_at)
  VALUES (TG_TABLE_NAME, TG_OP, COALESCE(NEW.id, OLD.id), auth.uid(), now());
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
```

### B. Implementasi Frontend & Optimasi Connection-Aware
Frontend dibangun menggunakan React.js dan Vite. Untuk mengatasi kendala performa peramban web saat memuat file build Unity WebGL yang besar pada perangkat dengan jaringan internet lambat, diimplementasikan mekanisme *connection-aware preloading*. Mekanisme ini mengevaluasi status koneksi client melalui API peramban `navigator.connection`:

```javascript
const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
const isConnectionSlow = connection && (connection.saveData || ['slow-2g', '2g', '3g'].includes(connection.effectiveType));

if (isConnectionSlow) {
  // Lewati preload otomatis WebGL, tampilkan tombol aktivasi manual
  setShowManualActivationButton(true);
} else {
  // Lakukan preload aset WebGL secara otomatis di latar belakang
  triggerWebGLPreload();
}
```

Fitur pencarian terpadu diimplementasikan pada komponen `SearchOverlay.tsx`. Komponen ini menggabungkan hasil query teks untuk data gedung dan fasilitas dalam satu hasil pencarian terpadu dengan penyajian ikon dinamis (`Building2` untuk gedung dan `LayoutGrid` untuk fasilitas).

### C. Integrasi React dengan Unity WebGL via SendMessage
System integration dijembatani oleh pembungkus `react-unity-webgl`. Ketika pengguna mencari dan memilih rute fasilitas tertentu pada antarmuka web, React mengirimkan instruksi navigasi ke Unity WebGL secara asinkron dengan memicu nama objek visual target (`unity_object_name`) lewat API bridge:

```typescript
import { useUnityContext } from "react-unity-webgl";

const { sendMessage, isLoaded } = useUnityContext({
  loaderUrl: "build/UnityWebGL.loader.js",
  dataUrl: "build/UnityWebGL.data",
  frameworkUrl: "build/UnityWebGL.framework.js",
  codeUrl: "build/UnityWebGL.wasm",
});

const handleNavigate = (targetObjectName: string) => {
  if (isLoaded) {
    // Mengirim nama objek visual ke Unity receiver script secara case-insensitive
    sendMessage("NavigationReceiver", "FindFacilityRoute", targetObjectName);
  }
};
```

Di sisi Unity, script C# `NavigationReceiver.cs` menerima instruksi, mencocokkan `unity_object_name` dengan dictionary data, memicu NavMesh pathfinding, dan melukis visualisasi kurva rute navigasi terdekat yang telah dihaluskan secara dinamis menggunakan interpolasi kurva Catmull-Rom Centripetal.

### D. Reverse Proxy Umami Analytics
Untuk memantau penggunaan sistem secara mandiri (*self-hosted*), Umami Analytics dipasang menggunakan kontainer Docker di port 3000. Untuk meminimalkan kegagalan pemuatan skrip pelacakan akibat pemblokiran oleh perangkat lunak *ad-blocker* pada peramban web client, server Express.js di port 3001 dikonfigurasi sebagai *reverse proxy*. Request metrik dari peramban client diarahkan ke endpoint internal proxy `/api/collect` yang kemudian meneruskannya ke kontainer Umami di port 3000 secara transparan.

### E. Evaluasi Sistem dan Hasil Pengujian
Sistem diuji menggunakan dua metode evaluasi:
1. **Black Box Testing:** Menguji 18 skenario fungsionalitas backend API, dashboard admin (Protected routes JWT), formulir CRUD, connection-aware preloading, dan fungsionalitas SendMessage bridge. Hasil pengujian menunjukkan seluruh skenario berjalan 100% sukses sesuai kriteria.
2. **User Acceptance Testing (UAT):** Dilakukan terhadap 16 responden menggunakan model kuesioner skala Likert untuk menilai kegunaan (*usability*), kemudahan pemahaman navigasi, dan performa antarmuka web. Hasil UAT memperoleh skor rata-rata indeks kepuasan sebesar **89.5% (Sangat Baik)**, membuktikan bahwa integrasi visualisasi denah 3D dengan dashboard web profil sangat membantu pengguna dalam orientasi spasial di lingkungan kampus.

---

## V. KESIMPULAN DAN SARAN

### A. Kesimpulan
Penelitian ini berhasil merancang dan mengimplementasikan sistem integrasi data denah virtual 3D dan web dashboard profil UPNVJ Kampus Pondok Labu secara Full Stack. Penerimaan sistem oleh pengguna sangat tinggi dibuktikan dengan nilai indeks kepuasan UAT sebesar 89.5%. Kontribusi arsitektur Full Stack (Vercel Serverless, Supabase PostgreSQL, RLS, react-unity-webgl bridge, dan proxy Umami) mampu menjamin kecepatan akses data dinamis, kemudahan pemeliharaan data spasial oleh administrator secara terpusat, serta keamanan tingkat basis data yang andal dari risiko kebocoran data.

### B. Saran
Bagi pengembangan selanjutnya, disarankan untuk mengintegrasikan basis data sistem denah ini dengan API akademik utama (SIK UPNVJ) secara langsung untuk menyinkronkan jadwal pemakaian ruang kuliah dan profil dosen secara otomatis. Selain itu, optimalisasi ukuran aset build WebGL perlu ditingkatkan lebih lanjut agar waktu pemuatan awal visualisasi 3D pada jaringan seluler mobile dapat dipangkas seminimal mungkin.

---

## DAFTAR PUSTAKA

'Afiifah, K., Azzahra, Z. F., & Anggoro, A. D. (2022). Analisis teknik Entity-Relationship Diagram dalam perancangan database: Sebuah literature review. *INTECH (Informatika dan Teknologi)*, 3(1), 8–14. https://doi.org/10.54895/intech.v3i1.1261

Aliyah, A., Hartono, N., & Muin, A. A. (2024). Penggunaan User Acceptance Testing (UAT) pada pengujian sistem informasi pengelolaan keuangan dan inventaris barang. *Switch: Jurnal Sains dan Teknologi Informasi*, 3(1), 84–100. https://doi.org/10.62951/switch.v3i1.330

Ghai, V. (2025). Exploring the future career potential of Blender 3D as a professional tool. *International Journal of Advance Research*. https://www.ijariit.com/manuscript/exploring-the-future-career-potential-of-blender-3d-as-a-professional-tool/

Jamaludin, J., & Saepuloh, L. (2024). Tren riset twin digital smart campus. *Sang Pencerah: Jurnal Ilmiah Universitas Muhammadiyah Buton*, 10(2), 408–425. https://doi.org/10.35326/pencerah.v10i2.5317

Kurniawan, T. A. (2018). Pemodelan Use Case (UML): Evaluasi terhadap beberapa kesalahan dalam praktik. *Jurnal Teknologi Informasi dan Ilmu Komputer (JTIIK)*, 5(1), 77–86. https://doi.org/10.25126/jtiik.201851610

Maulida, M., Zahro, F., Hakim, R., & Akbar, M. S. (2025). Pengujian black box testing pada sistem website pemesanan online Toko Ayam Krispy. *Jurnal Media Akademik (JMA)*, 3(5). https://mediaakademik.com/index.php/jma/article/view/392

Muharam, Y., Anggara, M. B., & Hanafi, T. J. (2023). Implementasi peta 3 dimensi menggunakan metode IMSDD (Interactive Multimedia System Design and Development) dan WebGL API berbasis web (Studi kasus di SMP Karya Pembangunan 2 Majalaya). *Jurnal Informatika-COMPUTING*, 10, 20–30. https://doi.org/10.55222/computing.v10i01.1155

Pricillia, T., & Zulfachmi (2021). Perbandingan metode pengembangan perangkat lunak (Waterfall, Prototype, RAD). *Jurnal Bangkit Indonesia*, 10(1), 6–12. https://doi.org/10.32722/jbi.v10i1.124

Putra, I. G. W. W., Dharma, E. M., & Permana, P. T. H. (2026). Implementasi relational database dengan Row-Level Security (RLS) pada sistem inventory menggunakan Supabase dan React Native Expo (Studi kasus Bengkel Sari Merta). *JATI (Jurnal Mahasiswa Teknik Informatika)*, 10(2), 2443–2448. https://ejournal.itn.ac.id/index.php/jati/article/view/8282

Siv, T. (2025). A framework for scalable digital twin deployment in smart campus building facility management. *arXiv*. https://doi.org/10.48550/arXiv.2512.12149

Syarif, S., & Risdiansyah, D. (2024). Pemanfaatan metode prototype dalam perancangan sistem informasi penjualan berbasis website. *Jurnal Ekonomi Manajemen dan Bisnis (JEMB)*, 2(1), 12–25. https://doi.org/10.54895/jemb.v2i1.2312

Taurusta, C., Asiddiq, A. M., Suprianto, S., & Setiawan, H. (2024). Visualisasi gedung kampus 1 Universitas Muhammadiyah Sidoarjo menggunakan augmented reality sebagai media informasi. *Journal of Technology and System Information*, 1(1), 55–70. https://doi.org/10.47134/jtsi.v1i1.2146
