# Laporan TA — Muhammad Iman Nugraha (Full Stack Developer & System Integrator)

**Branch:** `laporan/iman` — draf lengkap ada di `Tugas_Akhir_Draft.md` (root repo) saat berada di branch ini.

## Fokus / Lingkup Laporan
Peran **Full Stack Developer & System Integrator**:
1. **Backend** — RESTful API (Node.js/Express) di Vercel Serverless Functions; endpoint `/api/unity/data`, `/api/unity/names`, `/api/buildings`, `/api/rooms`, `/api/health`.
2. **Database & Auth (sisi integrasi)** — integrasi Supabase Auth (JWT) dan konsumsi RLS (skema & policy dirancang Dwikhi).
3. **Frontend** — React SPA (Vite): Public Dashboard, Admin Panel (CRUD), multi-bahasa, panel pencarian.
4. **Integrasi React–Unity** — jembatan satu arah `SendMessage("NavigationReceiver","NavigateTo", unity_object_name)`, loading overlay, preloading.
5. **Analitik** — proxy Umami via Express.js (port 3001).
6. **Pengujian** — unit test (Vitest), integration test endpoint, audit Lighthouse.

## Diagram Relevan
2.9, 2.11, 2.12, 2.13, 2.14, 2.15, 2.16, 2.17 (lihat `../../diagrams/`).

## Acuan
- PRD: `../../PRD_Konsolidasi_TA.md`
- Panduan branch tim: `../../PANDUAN-TIM.md`
