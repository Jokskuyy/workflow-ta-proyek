---
inclusion: always
---

# Konteks Proyek — Integrasi Denah Virtual UPNVJ (untuk Asisten AI)

Steering ini selalu aktif. Tujuannya menjaga asisten AI tetap selaras dengan
sistem **terkini** dan tidak memunculkan kembali pola yang sudah usang.

## Ringkasan Sistem (sumber kebenaran: `PRD_Konsolidasi_TA.md`)

Platform Web UPNVJ menyatukan empat komponen:
1. **Dashboard publik** (React SPA + Vite): statistik traffic, KPI aset kampus, akreditasi prodi, multi-bahasa ID/EN.
2. **Denah Virtual 3D** (Unity 6 WebGL): navigasi first-person NavMesh, dua mode (eksplorasi & terpandu).
3. **Admin Panel** (Supabase Auth + RLS, audit logs, CRUD).
4. **Analitik** (Umami self-hosted).

### Arsitektur kunci (JANGAN ditulis keliru)
- **API utama = Vercel Serverless Functions (Node.js)** (`/api/unity/data`, `/api/unity/names`, `/api/buildings`, `/api/rooms`, `/api/health`).
- **Express.js (port 3001)** hanya **proxy Umami Analytics + rate limiter**, BUKAN API utama.
- **Database = Supabase Cloud (PostgreSQL)** dengan **RLS** (anon=SELECT, authenticated=CRUD) + **trigger audit logs**.
- **Komunikasi React→Unity bersifat SATU ARAH** via `SendMessage("NavigationReceiver","NavigateTo", unity_object_name)`.
- **Unity menarik datanya sendiri** via `HTTP GET /api/unity/data` saat runtime (modul `BuildingDatabase`).
- **`unity_object_name`** = jembatan tunggal antara baris DB (`gedung`/`fasilitas`) dan GameObject di scene (lowercase + underscore, case-insensitive).

### Pola DEPRECATED — JANGAN dipakai lagi
- ❌ Interaksi klik objek 3D di Unity yang menampilkan info (Unity→React callback). Komunikasi Unity→React **di luar lingkup**; info hanya di sisi React (hasil pencarian).
- ❌ Modul lama: `BuildingDataReceiver`, `BuildingClickHandler`, `DatabaseFetcher`, `ReceiveBuildingsData`, `ShowFloorPanel`, `UIManager`.
- ❌ Mengirim data gedung sebagai JSON via `SendMessage` dari React ke Unity. (Unity fetch sendiri via HTTP.)
- ❌ Menyebut Express sebagai "backend/API utama".

## Struktur Tim & Branch
Repo dipakai 3 anggota; tiap anggota menulis di branch sendiri (lihat `PANDUAN-TIM.md`):
- `laporan/iman` — Full Stack & System Integrator
- `laporan/dwikhi` — 3D Asset & Database Schema (RLS, audit, ERD)
- `laporan/faiz` — Simulator & Engine (NavMesh, Catmull-Rom, Building Culling, WebGL Optimizer, Database Sync Checker)

Saat membantu, **cek peran branch aktif** di `laporan-tim/<peran>/` dan fokuskan pembahasan pada lingkup peran itu.

## Aturan Mutlak
- **Jangan mengarang fakta/angka** (UAT, jumlah responden, skor Lighthouse, dll.). Verifikasi ke `project_facts.json`; bila belum ada, tulis `[TBD: ...]`.
- **Jangan mengarang sumber sitasi.** Ikuti `.kiro/steering/aturan-sitasi.md`.
- Saat menulis draf, ikuti `.kiro/steering/aturan-penulisan.md`.
- Panduan fitur lengkap untuk manusia: `PANDUAN-FITUR.md`.
