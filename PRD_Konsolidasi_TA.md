# Product Requirements Document (PRD) Konsolidasi
# Platform Web UPNVJ — Dashboard Profil Kampus & Sistem Navigasi Denah Virtual 3D

> **Versi:** 1.0 (Konsolidasi untuk Laporan Tugas Akhir)
> **Tanggal:** 22 Juni 2026
> **Penyusun:** Muhammad Iman Nugraha (2210511129)
> **Lingkup Sistem:** Aplikasi Web (Frontend + Backend) + Aplikasi Denah Virtual 3D (Unity WebGL)
> **Repositori Web:** `dashboard-profile-upnvj`
> **Repositori Unity:** `T_A---Copy`

---

## Catatan Penggunaan Dokumen (untuk Penyusunan Laporan TA)

Dokumen PRD ini disusun sebagai **rujukan tunggal** yang menggabungkan dua subsistem (Web/Backend dan Unity 3D) menjadi satu kesatuan produk. Setiap bagian sengaja dipetakan ke bab-bab laporan tugas akhir agar mudah dikutip:

| Bagian PRD | Dipakai untuk Bab Laporan TA |
|---|---|
| 1. Latar Belakang & Rumusan Masalah | BAB I — Pendahuluan |
| 2. Tujuan, Manfaat, dan Batasan | BAB I — Pendahuluan |
| 3. Landasan & Teknologi yang Digunakan | BAB II — Tinjauan Pustaka / Landasan Teori |
| 4. Analisis Kebutuhan (Fungsional & Non-Fungsional) | BAB III — Analisis & Perancangan |
| 5. Perancangan Sistem (Arsitektur, Data, Antarmuka) | BAB III — Analisis & Perancangan |
| 6. Spesifikasi Fitur & User Stories | BAB III / BAB IV |
| 7. Implementasi | BAB IV — Implementasi |
| 8. Pengujian | BAB V — Pengujian |
| 9. Batasan, Asumsi, dan Pekerjaan Lanjutan | BAB VI — Penutup |

---

## 1. Latar Belakang & Rumusan Masalah

### 1.1 Latar Belakang

Universitas Pembangunan Nasional Veteran Jakarta (UPNVJ) merupakan kampus dengan banyak gedung bertingkat yang tersebar di area yang cukup luas. Mahasiswa baru, calon mahasiswa, tamu, dan civitas akademika sering mengalami kesulitan dalam dua hal: (1) memperoleh informasi profil dan data institusional kampus secara terpadu, dan (2) menemukan lokasi fisik gedung, ruangan, serta fasilitas di lingkungan kampus.

Berdasarkan hasil *Survei Evaluasi Pengalaman Navigasi dan Kebutuhan Peta Virtual UPNVJ*, kebutuhan akan sarana navigasi digital yang dapat diakses langsung dari peramban — terutama melalui perangkat *mobile* yang menjadi perangkat utama mahasiswa — menjadi salah satu kebutuhan nyata yang belum terpenuhi oleh denah 2D statis maupun papan petunjuk fisik.

### 1.2 Rumusan Masalah

Sistem yang dibangun menjawab tiga permasalahan utama yang saling berkaitan:

1. **Akses Informasi Kampus yang Terfragmentasi.** Data profil (fakultas, program studi, fasilitas, akreditasi) tersebar dan disajikan secara statis tanpa keterhubungan dengan representasi fisik kampus.

2. **Navigasi Fisik Kampus yang Sulit.** Belum tersedia sistem navigasi digital interaktif yang dapat diakses langsung dari peramban — khususnya pada perangkat *mobile* — untuk memandu pengguna menuju gedung, ruangan, dan fasilitas, termasuk pada kampus multi-gedung bertingkat dengan koridor dan tangga antar lantai.

3. **Tidak Ada Sumber Data Terpadu (*Single Source of Truth*) untuk Admin.** Admin kampus tidak memiliki pusat data terpadu untuk memperbarui data secara dinamis, sehingga konsistensi antara data web dan model 3D Unity sulit dijaga.

### 1.3 Pertanyaan Penelitian (opsional untuk laporan)

- Bagaimana merancang platform web yang menyatukan informasi profil kampus dengan representasi spasial 3D dalam satu antarmuka?
- Bagaimana mengintegrasikan aplikasi web (React) dengan engine 3D (Unity WebGL) agar pencarian lokasi di web dapat memandu navigasi di dunia 3D?
- Bagaimana menjaga konsistensi data antara basis data web dan objek pada *scene* Unity melalui satu mekanisme jembatan data?

---

## 2. Tujuan, Manfaat, dan Batasan

### 2.1 Tujuan

Membangun **Platform Web UPNVJ** yang menyatukan empat komponen terintegrasi:

1. **Dashboard Publik Interaktif** — menyajikan statistik kunjungan web, indikator (KPI) aset kampus (gedung & fasilitas), serta daftar program studi beserta status akreditasinya, dengan dukungan dwibahasa (Indonesia & Inggris).
2. **Denah Virtual 3D (Unity WebGL)** — peta interaktif 3D kampus dengan mode eksplorasi bebas dan navigasi terpandu (*pathfinding* first-person), berjalan penuh di peramban tanpa instalasi.
3. **Admin Panel Terpusat** — dashboard CRUD berbasis Supabase dengan *Row Level Security* (RLS), *audit logs*, dan sinkronisasi data web↔Unity melalui field `unity_object_name`.
4. **Analytics Terintegrasi** — pemantauan lalu lintas kunjungan via Umami Analytics yang menjaga privasi pengunjung.

### 2.2 Manfaat

- **Bagi pengguna publik:** kemudahan memperoleh informasi akademis sekaligus menemukan lokasi fisik kampus dari satu platform.
- **Bagi admin kampus:** kemudahan mengelola data kampus secara terpusat tanpa menyentuh kode aplikasi 3D.
- **Bagi institusi:** penyajian profil kampus modern dan terukur melalui data analitik kunjungan.

### 2.3 Batasan Masalah (Ringkas)

Lihat **Bagian 9** untuk daftar *Out of Scope* lengkap. Secara ringkas: sistem berupa simulasi 3D di peramban (bukan AR), target platform WebGL (bukan aplikasi native), komunikasi bersifat satu arah React→Unity, dan navigasi hanya berlaku pada area NavMesh yang telah di-*bake*.

---

## 3. Landasan & Teknologi yang Digunakan

Tabel berikut merangkum keseluruhan *technology stack* untuk dijadikan dasar BAB II (Tinjauan Pustaka/Landasan Teori).

| Komponen | Teknologi | Versi/Catatan | Penempatan Deploy |
|---|---|---|---|
| Frontend (Web) | React + TypeScript + Vite | React 19.1.1, TS 5.8.3, Vite 7.1.5 | Vercel (Static) |
| UI Styling | TailwindCSS | 4.1.13 | — |
| Routing | React Router | 7.x (client-side) | — |
| Visualisasi Data | Recharts | 3.x | — |
| Pencarian | Fuse.js | 7.x (fuzzy search) | — |
| Backend-as-a-Service | Supabase (PostgreSQL + Auth + RLS) | Cloud | Supabase Cloud |
| Serverless API | Vercel Functions (Node.js) | — | Vercel |
| Server Helper | Express.js | 4.21.2 | Server kampus (port 3001) |
| Keamanan Password | bcryptjs | — | — |
| Engine 3D | Unity + Universal Render Pipeline (URP) | Unity 6 (6000.x) | WebGL → Vercel Static |
| Input Unity | New Input System | (bukan legacy Input) | — |
| Integrasi Web-Unity | react-unity-webgl | — | — |
| Web Analytics | Umami (Docker) | self-hosted | Server kampus (port 3000) |
| Pengujian Web | Vitest + React Testing Library | — | — |
| Pengujian E2E | Playwright | — | — |
| Audit Performa | Lighthouse | — | — |

**Konsep teori pendukung yang relevan untuk dibahas di BAB II:**
- *Single Page Application* (SPA) dan *client-side routing*.
- *Backend-as-a-Service* dan *Row Level Security* pada PostgreSQL.
- *NavMesh* dan algoritma *pathfinding* pada Unity.
- Interpolasi kurva **Catmull-Rom Centripetal** untuk penghalusan jalur navigasi.
- Kompresi **Brotli** dan optimasi *build* WebGL (IL2CPP, *stripping*).
- *Pointer Lock API* pada peramban.

---

## 4. Analisis Kebutuhan

### 4.1 Aktor Sistem

| Aktor | Deskripsi |
|---|---|
| **Pengguna Publik** | Pengguna anonim (tanpa login): mahasiswa, calon mahasiswa, tamu. Mengakses dashboard & denah virtual. |
| **Admin Kampus** | Pengguna terautentikasi yang mengelola data profil, gedung, fasilitas, dosen, dan aset. |
| **Developer / Tim Teknis** | Pengembang yang memelihara sinkronisasi data web↔Unity dan konfigurasi build. |
| **Sistem Eksternal** | Supabase (data & auth), Umami (analytics), Unity WebGL (engine 3D). |

### 4.2 Kebutuhan Fungsional (Functional Requirements)

**FR-Publik:**
- FR-01 Sistem menampilkan statistik lalu lintas kunjungan web (tren harian, tampilan halaman).
- FR-02 Sistem menampilkan KPI aset kampus (gedung & fasilitas) serta daftar program studi beserta akreditasi.
- FR-03 Sistem menyediakan pergantian bahasa (ID↔EN) secara *real-time* tanpa *reload*.
- FR-04 Sistem menyimpan preferensi bahasa pengguna secara persisten (localStorage).
- FR-05 Sistem memuat Denah Virtual 3D langsung di peramban tanpa instalasi tambahan.
- FR-06 Sistem menyediakan pencarian lokasi (gedung + fasilitas dalam satu daftar, dibedakan ikon).
- FR-07 Sistem memandu pengguna secara otomatis dari posisi saat ini menuju tujuan (termasuk rute lintas gedung & multi-lantai).
- FR-08 Sistem menampilkan rute visual berupa garis pada lantai 3D yang mengikuti kontur tangga.
- FR-09 Sistem menampilkan nama tampilan tujuan dan informasi jarak tersisa.
- FR-10 Sistem menghentikan navigasi secara otomatis saat pengguna mendekati tujuan.
- FR-11 Sistem mendukung kontrol kamera 360° (Pointer Lock) dan pelepasan kursor via ESC.
- FR-12 Sistem menyediakan joystick virtual untuk kontrol di perangkat mobile.

**FR-Admin:**
- FR-13 Sistem menyediakan autentikasi admin yang aman via Supabase Auth (JWT).
- FR-14 Sistem menyediakan CRUD data gedung (termasuk field `unity_object_name`).
- FR-15 Sistem menyediakan CRUD data fasilitas yang terkait gedung beserta info lantai.
- FR-16 Sistem menyediakan CRUD data program studi & fakultas (jenjang, akreditasi).
- FR-17 Sistem memisahkan `nama_gedung` (tampilan) dari `unity_object_name` (internal Unity).
- FR-18 Sistem menampilkan modal konfirmasi sebelum penghapusan data.
- FR-19 Sistem mencatat riwayat perubahan data (*audit logs*: aktor, waktu, tabel, data).
- FR-20 Sistem menampilkan statistik kunjungan web (Umami) di panel admin.

**FR-Developer:**
- FR-21 Sistem menyediakan Unity Editor Tool untuk memeriksa kecocokan `unity_object_name` antara database dan scene.
- FR-22 Sistem menyediakan Unity Editor Tool untuk menerapkan konfigurasi build WebGL optimal dengan satu klik.

### 4.3 Kebutuhan Non-Fungsional (Non-Functional Requirements)

| Kode | Kategori | Kebutuhan |
|---|---|---|
| NFR-01 | Performa | Halaman web termuat < 10 detik meski memuat model 3D kampus lengkap. |
| NFR-02 | Performa | Rute dihitung ulang hanya saat player berpindah melebihi ambang jarak (`pathUpdateDistance`), bukan tiap frame. |
| NFR-03 | Performa | Build WebGL dikompres Brotli + *decompression fallback* untuk memperkecil unduhan. |
| NFR-04 | Kompatibilitas | **Mobile browser (Chrome Android) merupakan hard requirement**; desktop didukung namun bukan prioritas. |
| NFR-05 | Keamanan | Operasi admin diproteksi JWT; akses data diatur RLS (anon = SELECT, authenticated = penuh). |
| NFR-06 | Keamanan | Operasi sensitif dibatasi *rate limiter*. |
| NFR-07 | Privasi | Analytics tanpa PII dan tanpa cookie tracking. |
| NFR-08 | Usabilitas | Loading screen informatif (progress bar) saat engine dimuat. |
| NFR-09 | Aksesibilitas | Modal konfirmasi memiliki *focus trap*. |
| NFR-10 | Keterpeliharaan | Perubahan data gedung melalui Admin Panel langsung tercermin pada navigasi Denah Virtual 3D. |


---

## 5. Perancangan Sistem

### 5.1 Arsitektur Sistem

```
┌──────────────────────────────────────────────────────────────────┐
│                       Browser (Pengguna)                          │
│  ┌────────────────────────────┐  ┌────────────────────────────┐   │
│  │    Vite + React SPA        │  │     Unity WebGL Canvas     │   │
│  │  - Dashboard akademik      │──┤  - Scene 3D kampus         │   │
│  │  - Panel pencarian         │  │  - NavMesh pathfinding     │   │
│  │  - Multi-language toggle   │  │  - First-person control    │   │
│  │  - Admin Panel (Auth)      │  │  - Visual route line       │   │
│  │  - Loading overlay         │  │  - Joystick virtual (mobile)│  │
│  └────────────┬───────────────┘  └────────────────────────────┘   │
│               │ SendMessage("NavigationReceiver","NavigateTo")     │
│               └────────────────────────────────────────────────►  │
└──────────────────────────────────────────────────────────────────┘
                    │
     ┌──────────────┼──────────────────────┐
     ▼                                      ▼
┌─────────────────────────┐    ┌────────────────────────────┐
│   VERCEL                │    │   SERVER KAMPUS             │
│  Static Hosting:        │    │  Express.js (port 3001):   │
│   dist/ (Vite build)    │    │   - Umami API proxy        │
│   unity-builds/ (WebGL) │    │   - Analytics endpoints    │
│  Serverless Functions:  │    │   - Rate limiter           │
│   api/unity/names.js    │    │  Umami (Docker, port 3000):│
│   api/unity/data.js     │    │   - Web analytics          │
│   api/buildings/*       │    │                            │
│   api/rooms/*           │    │                            │
│   api/health.js         │    │                            │
└────────────┬────────────┘    └────────────────────────────┘
             │ HTTPS
             ▼
   ┌────────────────────┐
   │  Supabase Cloud    │
   │  - PostgreSQL      │
   │  - Auth (JWT)      │
   │  - RLS             │
   └────────────────────┘
```

**Prinsip kunci arsitektur:** field `unity_object_name` adalah **jembatan tunggal** yang menghubungkan data pada basis data (tabel `gedung`/`fasilitas`) dengan GameObject pada *scene* Unity. Setiap perubahan data gedung melalui Admin Panel langsung tercermin pada kemampuan navigasi Denah Virtual 3D.

### 5.2 Perancangan Basis Data (Supabase — PostgreSQL)

```sql
gedung          → id, nama_gedung, deskripsi_gedung, lokasi, jumlah_lantai,
                  foto_url, unity_object_name
fasilitas       → id, nama_fasilitas, deskripsi_fasilitas, tipe_fasilitas, color,
                  lantai, id_gedung (FK→gedung), foto_url, unity_object_name
fakultas        → id, nama_fakultas, deskripsi_fakultas, email, website,
                  id_gedung_utama (FK→gedung)
program_studi   → id, nama_prodi, jenjang (D3/S1/S2/S3), id_fakultas (FK→fakultas),
                  akreditasi
admin_users     → id, username, password_hash, nama_lengkap, role, created_at
audit_logs      → id, actor_id, actor_email, action (INSERT/UPDATE/DELETE),
                  table_name, record_id, old_data, new_data, created_at
```

**Kebijakan RLS:**
- `anon`: hanya `SELECT`.
- `authenticated`: `SELECT`, `INSERT`, `UPDATE`, `DELETE`.

**Audit Logging:** *trigger* basis data otomatis menulis ke `audit_logs` setiap mutasi data oleh pengguna terautentikasi.

### 5.3 Kontrak API

**Vercel Serverless Functions (repo `dashboard-profile-upnvj/api/`):**

| Endpoint | Method | Format Respons | Konsumen |
|---|---|---|---|
| `/api/unity/names` | GET | `{ "unityObjectNames": string[] }` | DatabaseSyncChecker (Editor) |
| `/api/unity/data` | GET | `{ "gedung": [...], "fasilitas": [...] }` | BuildingDatabase.cs (runtime) |
| `/api/buildings/*` | GET | Data gedung | React SPA |
| `/api/rooms/*` | GET | Data fasilitas | React SPA |
| `/api/health` | GET | `{ "status": "ok" }` | Monitoring |

**Express.js Server (server kampus, port 3001):** proxy Umami API, endpoint analytics teragregasi, rate limiter.

**Jembatan React→Unity:**

```js
// Mulai navigasi (mengirim unity_object_name, bukan nama tampilan)
unityInstance.SendMessage("NavigationReceiver", "NavigateTo", unity_object_name)

// Hentikan navigasi
unityInstance.SendMessage("NavigationReceiver", "StopNavigation", "")
```

### 5.4 Perancangan Antarmuka Web (Frontend)

- **Routing (client-side):** `/` (dashboard publik), `/admin` (protected route, lazy-loaded), `/login` & `/admin/login` (lazy-loaded).
- **Integrasi React-Unity:** komponen `CampusMapViewer.tsx` via `react-unity-webgl`, dengan *loading overlay* (callback `onProgress`) dan strategi *preloading* file WebGL di latar belakang.
- **Multi-bahasa:** `LanguageProvider` (React Context) + kamus JSON (id/en) dengan *token replacement*, preferensi disimpan di localStorage.
- **Admin Panel:** form CRUD untuk `gedung`, `fasilitas`, `program_studi`, `fakultas`; modal konfirmasi hapus dengan *focus trap*; tampilan audit logs (read-only); dashboard Umami; *code splitting* agar tidak membebani halaman publik.

### 5.5 Perancangan Scene Unity

```
SceneUtama
├── [Infrastruktur]
│   ├── MainCamera, PlayerArmature, PlayerFollowCamera
│   ├── NavigationGuide, NavigationReceiver
│   ├── BuildingDatabase, BuildingCulling
│   ├── NavMesh_Bake, PathLine
├── BuildingObjek
│   └── [NamaGedung]
│       ├── Pointer                    ← Parent semua unity_object_name
│       │   ├── [unity_object_name_1]  ← Target navigasi (match dengan DB)
│       │   └── [unity_object_name_2]  ← Bisa gedung ATAU fasilitas
│       ├── Lantai 1 ... Lantai N
└── Environment
```

---

## 6. Spesifikasi Fitur & User Stories

### 6.1 Pengguna Publik — Dashboard Informasi Akademik
1. Melihat statistik traffic website (tren pengunjung & tampilan halaman).
2. Melihat & menjelajahi sebaran aset kampus via KPI dan daftar program studi beserta akreditasi.
3. Beralih bahasa antarmuka (ID↔EN) dengan toggle beranimasi.
4. Preferensi bahasa tersimpan otomatis (localStorage).

### 6.2 Pengguna Publik — Denah Virtual 3D & Navigasi
5. Denah Virtual 3D termuat langsung di web tanpa instalasi.
6. Mencari ruang/fasilitas via kotak pencarian (gedung + fasilitas dalam satu daftar, dibedakan ikon).
7. Dipandu otomatis dari posisi saat ini ke tujuan, termasuk rute lintas gedung via jalan outdoor.
8. Melihat rute visual berupa garis di lantai 3D.
9. Rute menyesuaikan kontur tangga antar lantai (navigasi gedung bertingkat).
10. Melihat nama tampilan tujuan (bukan kode internal Unity) pada label.
11. Melihat informasi jarak tersisa ke tujuan.
12. Navigasi berhenti otomatis saat dekat tujuan.
13. Memutar kamera 360° tanpa kursor mentok (Pointer Lock).
14. Menekan ESC untuk melepaskan kursor.
15. (**Hard requirement**) Kontrol via joystick virtual yang hanya tampil di mobile.
16. Menemukan gedung utama (Rektorat, Masjid, Aula) hanya dengan mengetik nama.
17. Halaman web termuat < 10 detik meski memuat model 3D lengkap.
18. Loading screen informatif (progress bar) saat engine dimuat.

### 6.3 Admin Kampus
19. Login aman via Supabase Auth.
20. CRUD data gedung (termasuk `unity_object_name`).
21. Mengelola fasilitas terkait gedung beserta info lantai.
22. Mengelola program studi tiap fakultas (jenjang, akreditasi).
23. Menambah gedung/fasilitas baru tanpa menyentuh kode Unity.
24–25. Memisahkan `nama_gedung` (tampilan) dari `unity_object_name` (internal).
26. Modal konfirmasi sebelum menghapus.
27. Melihat audit logs (akuntabilitas perubahan data).
28. Memantau statistik traffic via Umami.

### 6.4 Developer / Tim Teknis
29–31. Unity Editor Tool `Check Database Sync` — mendeteksi kecocokan/ketidakcocokan `unity_object_name` (3 kategori: cocok / ada di DB tapi tidak di scene / ada di scene tapi tidak di DB) + salin daftar *missing* ke clipboard.
32. Rute dihitung ulang hanya saat player berpindah > ambang jarak.
33–34. Build WebGL terkompres Brotli + konfigurasi build optimal satu klik (`Apply Optimal WebGL Settings`).

---

## 7. Implementasi

### 7.1 Modul Unity (C#)

| Modul | Tanggung Jawab |
|---|---|
| **BuildingDatabase** | Fetch data dari `/api/unity/data` saat game start; cache `unityObjectNames` (list) & `realNames` (dict); `GetRealName()` sebagai sumber nama tampilan dengan fallback ke input asli. |
| **NavigationReceiver** | Menerima `NavigateTo(unity_object_name)` dari JavaScript; lookup Transform via cache O(1) dengan fallback bertingkat (cache → rebuild → pencarian langsung termasuk objek inactive). |
| **NavigationGuide** | Mengelola siklus navigasi; `NavMesh.CalculatePath()`; interpolasi **Catmull-Rom Centripetal** (alpha=0.5); *raycast* subdivisi tiap 10cm untuk mengikuti kontur lantai/tangga; label 3D (TMP) nama tujuan + jarak; stop otomatis pada `stopDistance`; integrasi Pointer Lock. |
| **BuildingCulling** | Optimasi performa: nonaktifkan renderer gedung yang jauh dari player. |
| **WebGLOptimizer** (Editor) | `Tools → UPNVJ → Apply Optimal WebGL Settings`: Brotli, decompression fallback, stripping, IL2CPP Master. |
| **DatabaseSyncChecker** (Editor) | `Tools → UPNVJ → Check Database Sync`: bandingkan `/api/unity/names` dengan hierarki scene secara rekursif; tampilkan 3 kategori + copy clipboard. |
| **Joystick Virtual** | Prefab `UI_Virtual_Joystick` untuk kontrol mobile. |

### 7.2 Alur Data Integrasi (`unity_object_name` sebagai Bridge)

```
Admin Panel (web) → Supabase Cloud → Vercel Serverless (/api/unity/data)
    → BuildingDatabase.cs (cache realNames + unityObjectNames)
    → NavigationReceiver.cs (cache Transform lookup)
    → NavigationGuide.cs (render path + display name)
```
**Konvensi wajib `unity_object_name`:** huruf kecil + underscore (contoh: `mht_201`, `gedung_rektorat`); lookup *case-insensitive*; harus sama persis dengan nama GameObject di folder `Pointer`.

### 7.3 Konfigurasi Build & Deployment WebGL

| Setting | Nilai | Alasan |
|---|---|---|
| Kompresi | Brotli + decompression fallback | Ukuran file kecil; tetap jalan meski server tak serve `Content-Encoding: br`. |
| IL2CPP | Master + LTO | Ukuran binary minimal untuk produksi. |
| NavMesh | Di-bake seluruh area kampus (indoor + outdoor + jalan antar gedung) | Rute multi-lantai & lintas gedung tanpa NavMeshLink manual. |
| Pointer Lock | Kunci saat klik kiri, lepas saat ESC | Aturan keamanan peramban. |
| Path Recalculation | Berbasis ambang jarak player | Hemat performa. |

**Deployment:** file `.br` dilayani dengan header `Content-Encoding: br` per-path di `vercel.json`; seluruh `unity-builds` di-cache `public, max-age=31536000, immutable`. Build WebGL disimpan di `/unity-builds/`.

### 7.4 Catatan Keamanan

- **Supabase Anon Key** aman diekspos di klien karena proteksi data sepenuhnya bergantung pada RLS di PostgreSQL.
- **JWT Auth** untuk seluruh operasi admin.

---

## 8. Pengujian

### 8.1 Prinsip Pengujian
Pengujian berfokus pada **perilaku eksternal** tiap modul, bukan detail implementasi internal (tidak bergantung pada nama variabel privat atau struktur cache konkret).

### 8.2 Pengujian Unity (C#)

| Modul | Skenario Uji |
|---|---|
| DatabaseSyncChecker (Editor) | API 3 nama vs scene 2 objek → lapor 1 *missing*; API kosong → pesan error jelas (bukan crash); nama di child `Pointer` → terdeteksi "ditemukan". |
| NavigationGuide (Play Mode) | Target valid → `pathLine` aktif & > 0 posisi; player dalam `stopDistance` → stop otomatis; `StopNavigation` → pathLine nonaktif + label dihapus. |
| NavigationReceiver (Play Mode) | Nama ada di cache → panggil `StartNavigation` dengan Transform benar; nama tidak ada → fallback + warning, tidak throw exception. |
| BuildingDatabase (Play Mode) | API sukses → `isLoaded=true` & list tidak kosong; `GetRealName()` → nama terbaca; nama tak dikenal → fallback ke input asli (bukan null). |

### 8.3 Pengujian Web (Vite + React)

- **Unit Test (Vitest + RTL):** `retry.ts` (exponential backoff), `sanitizeData` (masking email/telepon), `rateLimiter`, `translationEngine.ts` (dot-notation key + token), `DeleteConfirmModal.tsx` (aksi confirm/batal, focus trap).
- **Integration Test:** endpoint Vercel serverless (health, data gedung/fasilitas, fallback error DB).
- **Audit Performa & SEO (Lighthouse):** LCP, TBT, CLS; validasi code splitting & caching aset statis.
- **E2E (Playwright):** alur pengguna ujung-ke-ujung (tersedia laporan di `playwright-report/`).

### 8.4 Skenario UAT
Skenario *User Acceptance Testing* terdokumentasi pada berkas `uat_scenarios.md`.

---

## 9. Batasan, Asumsi, dan Pekerjaan Lanjutan

### 9.1 Batasan Sistem (Out of Scope)
- **Augmented Reality (AR):** sistem berupa simulasi 3D di peramban, bukan AR kamera.
- **Multiplayer / location sharing real-time:** tidak ada sesi navigasi bersama.
- **Text-to-speech / panduan audio:** tidak termasuk.
- **Offline mode / Service Worker:** sistem memerlukan koneksi internet.
- **Analytics penggunaan rute:** tidak ada pelacakan rute terpopuler.
- **Build native iOS/Android:** target platform WebGL.
- **Pathfinding di luar area NavMesh ter-bake.**
- **Sistem pembayaran / fitur akademik internal (KRS, dll.).**
- **Pengeditan model 3D dari frontend.**
- **Komunikasi Unity→React:** detail gedung/fasilitas hanya ditampilkan di sisi React; tidak ada callback dari Unity ke React.

### 9.2 Asumsi
- Pengguna mengakses melalui peramban modern dengan dukungan WebGL.
- Tangga multi-lantai terhubung secara fisik (collision mesh) agar NavMesh dapat merute antar lantai.
- Supabase Cloud digunakan saat ini; Supabase self-hosted direncanakan saat server kampus tersedia.
- `docker-compose.yml` pada repo web khusus untuk Umami Analytics.

### 9.3 Isu yang Diketahui & Rencana Perbaikan (untuk pembahasan/keterbatasan)
- 🔴 **BuildingDatabase Endpoint/Parser Mismatch** — `Awake()` sempat mengakses `/api/unity/names` namun parser mengharapkan format `/api/unity/data`, sehingga cache nama tampilan kosong dan label menampilkan kode internal. *Rencana fix:* arahkan endpoint ke `/api/unity/data` + tambahkan `unity_object_name` pada select query.
- 🟡 **Joystick Virtual belum responsif** — masih tampil di desktop. *Rencana fix:* deteksi platform untuk menyembunyikan di desktop.
- 🟡 **Preloading belum mobile-aware** — file WebGL di-preload otomatis termasuk di mobile (boros kuota). *Rencana fix:* deteksi `navigator.connection.saveData`/`effectiveType` untuk melewati preload pada koneksi lambat/metered.

### 9.4 Pekerjaan Lanjutan (Future Work)
- Migrasi ke Supabase self-hosted di server kampus.
- Penyempurnaan responsivitas mobile (joystick & preloading).
- Penambahan analitik penggunaan rute navigasi.

---

## Lampiran — Referensi Berkas Pendukung

| Berkas | Lokasi | Kegunaan |
|---|---|---|
| Survei navigasi | `Survei Evaluasi Pengalaman Navigasi ... (Responses).xlsx` | Data latar belakang & rumusan masalah. |
| ERD | `ERD-Mermaid.png`, `dokumentasi/erd_schema.png` | Diagram perancangan basis data. |
| Diagram alur sistem | `diagram_alur_sistem.md`, `Alur Implementasi sistem.png` | Diagram BAB III/IV. |
| Diagram CRUD Admin | `Diagram Crud Admin.png` | Perancangan modul admin. |
| Diagram deployment | `Deployment.png` | Arsitektur deployment. |
| Skenario UAT | `uat_scenarios.md` | Pengujian penerimaan. |
| Implementasi backend | `implementasi_backend.md` | Detail implementasi BAB IV. |
| Dokumentasi tangkapan layar | folder `document/dokumentasi/` | Screenshot antarmuka untuk BAB IV. |
| Audit keamanan & WebGL | `dashboard-profile-upnvj/docs/` | Pendukung BAB IV/V. |
