---
inclusion: always
---

# Konteks Proyek — Integrasi Denah Virtual UPNVJ (untuk Asisten AI)

Steering ini selalu aktif. Tujuannya menjaga asisten AI tetap selaras dengan
sistem **terkini** dan tidak memunculkan kembali pola yang sudah usang.

## Ringkasan Sistem (sumber kebenaran: `PRD_Konsolidasi_TA.md`)

Platform Web UPNVJ menyatukan empat komponen:
1. **Dashboard publik** (React SPA + Vite): informasi utama kampus, statistik kunjungan, kartu aset gedung/fasilitas, pencarian, multi-bahasa ID/EN, tutorial/FAQ, serta pemilih denah 2D atau 3D. Snapshot aktif tidak menampilkan tabel akreditasi atau program studi publik.
2. **Denah kampus**: denah 2D berbasis graph Supabase dan A* pada frontend, serta Unity 6 WebGL v0.8.6.1 untuk tur 3D dan navigasi NavMesh.
3. **Admin Panel** (Supabase Auth + RLS): CRUD data kampus, konfigurasi denah 2D, analitik, dan audit log.
4. **Analitik**: jalur UI aktif memakai `web_analytics_log` di Supabase; Express/Umami self-hosted tersedia sebagai jalur opsional.

### Arsitektur kunci (JANGAN ditulis keliru)
- **API utama = Vercel Serverless Functions read-only (Node.js)** (`/api/unity/data`, `/api/unity/names`, `/api/buildings`, `/api/rooms`, `/api/health`). React UI melakukan Auth, query, dan CRUD langsung melalui Supabase SDK.
- **Express.js (port 3001)** adalah server opsional untuk proxy API Umami, rate limiter, dan API lokal/mandiri; bukan jalur data frontend utama pada deployment Vercel.
- **Database = Supabase Cloud (PostgreSQL)** dengan **RLS** (anon=SELECT sesuai policy, authenticated=CRUD). Pada snapshot 21 Juli 2026, audit dicatat oleh service aplikasi; trigger audit tidak terverifikasi pada schema aktif.
- **React memuat Unity WebGL v0.8.6.1 melalui loader native**, bukan `react-unity-webgl`. Observasi Network v0.8.0 tetap merupakan bukti historis dan tidak dipakai sebagai pengukuran build aktif.
- **Kontrak navigasi React→Unity** menggunakan `SendMessage("NavigationReceiver","NavigateTo", unity_object_name)`. Setelah tiba normal, Unity commit `1845c65` memancarkan `OnNavigationCompleted` dengan JSON `unity_object_name`; sembilan pengujian awal diperkenalkan pada React `b572a48` dan dua pengujian lanjutan pada `d2e8fdb`. Kode sumber aktif `08ebc06` memvalidasi payload terhadap `activeNavigationRef`. Pembatalan dan pergantian spawn tidak mengirim completion.
- **Unity menarik datanya sendiri** via `HTTP GET /api/unity/data` saat runtime (modul `BuildingDatabase`).
- **`unity_object_name`** = jembatan tunggal antara baris DB (`gedung`/`fasilitas`) dan GameObject di scene (lowercase + underscore, case-insensitive).
- **Verifikasi web aktif 21 Juli 2026** pada `08ebc06`: 13 file dan 129 pengujian lulus, termasuk 11 pengujian kontrak completion; lint dan production build lulus. **Snapshot audit Lighthouse** pada `bdeb5bc` menghasilkan Performance mobile 86 dan desktop 99; Accessibility, Best Practices, dan SEO bernilai 100 pada kedua mode. Angka Lighthouse merupakan data laboratorium lokal, bukan data pengguna nyata; PWA dan pemeriksaan manual tidak dinyatakan lulus.

### Mitra dan pihak koordinasi
- **Humas UPNVJ** adalah mitra pengguna. Satu perwakilan mengikuti UAT, tetapi hasilnya tidak digunakan untuk mengklaim persetujuan formal atau representasi seluruh pengguna UPNVJ.
- **UPA TIK UPNVJ** bukan mitra pengguna. Perannya terbatas pada koordinasi teknis, batas akses data, kemungkinan integrasi institusional, wawancara, serta penyerahan pakta integritas.

### Pola DEPRECATED — JANGAN dipakai lagi
- ❌ Mendeskripsikan `OnNavigationCompleted` sebagai payload kosong atau memicu popup pada pembatalan. Kontrak aktif menggunakan JSON `unity_object_name` dan validasi tujuan pada React.
- ❌ Menyebut UPA TIK sebagai mitra pengguna atau Humas sebagai pemberi persetujuan formal institusional.
- ❌ Menyebut akreditasi, program studi publik, atau CRUD fakultas sebagai fitur antarmuka aktif.
- ❌ Modul lama: `BuildingDataReceiver`, `BuildingClickHandler`, `DatabaseFetcher`, `ReceiveBuildingsData`, `ShowFloorPanel`, `UIManager`.
- ❌ Mengirim data gedung sebagai JSON via `SendMessage` dari React ke Unity. (Unity fetch sendiri via HTTP.)
- ❌ Menyebut Express sebagai "backend/API utama".
- ❌ Menyebut `react-unity-webgl` sebagai dependency implementasi aktif.
- ❌ Menyebut Umami sebagai satu-satunya jalur analitik aktif; UI snapshot menggunakan `web_analytics_log` Supabase.

## Struktur Tim & Branch
Repo dipakai 3 anggota; tiap anggota menulis di branch sendiri (lihat `PANDUAN-TIM.md`):
- `laporan/iman` — Full Stack Web Developer, System Integrator, dan DevOps Engineer
- `laporan/dwikhi` — 3D Asset & Database Schema (RLS, audit, ERD)
- `laporan/faiz` — Simulator & Engine (NavMesh, Catmull-Rom, Building Culling, WebGL Optimizer, Database Sync Checker)

Saat membantu, **cek peran branch aktif** di `laporan-tim/<peran>/` dan fokuskan pembahasan pada lingkup peran itu.

## Aturan Mutlak
- **Jangan mengarang fakta/angka** (UAT, jumlah responden, skor Lighthouse, dll.). Verifikasi ke `project_facts.json`; bila belum ada, tulis `[TBD: ...]`.
- **Jangan mengarang sumber sitasi.** Ikuti `.kiro/steering/aturan-sitasi.md`.
- Saat menulis draf, ikuti `.kiro/steering/aturan-penulisan.md`.
- Panduan fitur lengkap untuk manusia: `PANDUAN-FITUR.md`.
