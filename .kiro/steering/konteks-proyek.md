---
inclusion: always
---

# Konteks Proyek — Integrasi Denah Virtual UPNVJ (untuk Asisten AI)

Steering ini selalu aktif. Tujuannya menjaga asisten AI tetap selaras dengan
sistem **terkini** dan tidak memunculkan kembali pola yang sudah usang.

## Ringkasan Sistem (sumber kebenaran: `PRD_Konsolidasi_TA.md`)

Platform Web UPNVJ menyatukan empat komponen:
1. **Dashboard publik** (React SPA + Vite): informasi utama, statistik kunjungan, kartu aset, pencarian, Tutorial/FAQ, serta Denah 2D dan 3D.
2. **Denah Virtual 3D** (Unity 6 WebGL): navigasi sudut pandang orang ketiga berbasis NavMesh, pemilihan titik awal, minimap, tutorial, dan pemberitahuan kedatangan.
3. **Admin Panel** (Supabase Auth + RLS, audit log, dan CRUD): Gedung, Fasilitas, Program Studi, Denah 2D, Analytics, dan Audit Log.
4. **Analitik**: pencatatan Supabase digunakan pada implementasi aktif; Express/Umami merupakan jalur self-hosted opsional.

### Arsitektur kunci (JANGAN ditulis keliru)
- **API utama = Vercel Serverless Functions (Node.js)** (`/api/unity/data`, `/api/unity/names`, `/api/buildings`, `/api/rooms`, `/api/health`).
- **Express.js (port 3001)** hanya **proxy Umami Analytics + rate limiter**, BUKAN API utama.
- **Database = Supabase Cloud (PostgreSQL)** dengan **RLS** (anon=SELECT, authenticated=CRUD) + **trigger audit logs**.
- **React mengirim perintah ke Unity** melalui `SendMessage("NavigationReceiver","NavigateTo", unity_object_name)`.
- **Unity menarik datanya sendiri** via `HTTP GET /api/unity/data` saat runtime (modul `BuildingDatabase`).
- **Unity mengirim penyelesaian navigasi ke React** melalui event `OnNavigationCompleted` dengan payload JSON `unity_object_name`; React hanya menampilkan notifikasi apabila target cocok dengan navigasi aktif.
- **`unity_object_name`** = jembatan tunggal antara baris DB (`gedung`/`fasilitas`) dan GameObject di scene (lowercase + underscore, case-insensitive).

### Pola DEPRECATED — JANGAN dipakai lagi
- ❌ Interaksi klik objek 3D untuk mengirim informasi fasilitas ke React. Callback Unity→React yang aktif hanya melaporkan penyelesaian navigasi dengan payload tujuan.
- ❌ Payload kosong pada `OnNavigationCompleted`; kontrak aktif menggunakan JSON `unity_object_name`.
- ❌ Modul lama: `BuildingDataReceiver`, `BuildingClickHandler`, `DatabaseFetcher`, `ReceiveBuildingsData`, `ShowFloorPanel`, `UIManager`.
- ❌ Mengirim data gedung sebagai JSON via `SendMessage` dari React ke Unity. (Unity fetch sendiri via HTTP.)
- ❌ Menyebut Express sebagai "backend/API utama".

## Struktur Tim & Branch
Repo dipakai 3 anggota; tiap anggota menulis di branch sendiri (lihat `PANDUAN-TIM.md`):
- `laporan/iman` — Full Stack Web Developer, System Integrator, dan DevOps Engineer
- `laporan/dwikhi` — 3D Asset Designer dan Database Schema Designer (ERD, skema, RLS, trigger, data/pemetaan, dan aset)
- `laporan/faiz` — 3D Simulator dan Engine Developer (runtime Unity, NavMesh, rendering rute, kontrol, spawn, minimap, tutorial, optimasi, completion event, dan build WebGL)

Saat membantu, **cek peran branch aktif** di `laporan-tim/<peran>/` dan fokuskan pembahasan pada lingkup peran itu.

## Aturan Mutlak
- **Jangan mengarang fakta/angka** (UAT, jumlah responden, skor Lighthouse, dll.). Verifikasi ke `project_facts.json`; bila belum ada, tulis `[TBD: ...]`.
- **Jangan mengarang sumber sitasi.** Ikuti `.kiro/steering/aturan-sitasi.md`.
- Saat menulis draf, ikuti `.kiro/steering/aturan-penulisan.md`.
- Panduan fitur lengkap untuk manusia: `PANDUAN-FITUR.md`.
