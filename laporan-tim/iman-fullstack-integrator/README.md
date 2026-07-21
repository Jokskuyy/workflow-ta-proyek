# Laporan TA — Muhammad Iman Nugraha (Full Stack Web Developer, System Integrator, dan DevOps Engineer)

**Branch:** `laporan/iman` — draf lengkap ada di `Tugas_Akhir_Draft.md` (root repo) saat berada di branch ini.

## Fokus / Lingkup Laporan
Peran **Full Stack Web Developer, System Integrator, dan DevOps Engineer**:
1. **Backend** — REST API berbasis Node.js pada Vercel Serverless Functions; endpoint `/api/unity/data`, `/api/unity/names`, `/api/buildings`, `/api/rooms`, `/api/health`. Express.js bukan API utama.
2. **Database & Auth (sisi integrasi)** — integrasi Supabase Auth (JWT) dan konsumsi RLS (skema & policy dirancang Dwikhi).
3. **Frontend** — React SPA (Vite): Public Dashboard, Admin Panel (CRUD), denah 2D berbasis A*, multi-bahasa, tutorial/FAQ, dan pencarian.
4. **Integrasi React–Unity** — loader native Unity WebGL v0.8.6.1, `SendMessage("NavigationReceiver","NavigateTo", unity_object_name)`, loading overlay, preload adaptif, serta listener `OnNavigationCompleted` yang memvalidasi JSON `unity_object_name` sebelum menampilkan popup tiba. Observasi Network v0.8.0 dipertahankan sebagai bukti historis, bukan sebagai pengukuran build aktif.
5. **DevOps** — deployment Vercel untuk React SPA, serverless API, dan artefak Unity WebGL; pengelolaan environment variables, header/cache aset, health monitoring, serta jalur opsional Umami Docker dan Express proxy/rate limiter.
6. **Analitik** — jalur UI aktif melalui `web_analytics_log` Supabase; Express/Umami dipertahankan sebagai alternatif operasional.
7. **Pengujian** — kode sumber aktif `08ebc06` mencatat 13 file dengan 129 pengujian Vitest/React Testing Library lulus, termasuk 11 pengujian kontrak completion; lint dan production build lulus. Sembilan pengujian awal diperkenalkan pada `b572a48` dan dua pengujian lanjutan pada `d2e8fdb`. Snapshot Lighthouse `bdeb5bc` menghasilkan Performance mobile 86 dan desktop 99; Accessibility, Best Practices, dan SEO bernilai 100 pada kedua mode. Black Box/UAT digunakan untuk alur browser dan snapshot belum memiliki hasil Playwright.

## Mitra dan Pemangku Kepentingan
1. Humas UPNVJ merupakan mitra pengguna; satu perwakilan mengikuti UAT tanpa digunakan untuk mengklaim persetujuan formal atau mewakili seluruh pengguna UPNVJ.
2. UPA TIK UPNVJ merupakan pihak koordinasi teknis, batas akses data, kemungkinan integrasi institusional, wawancara, dan penyerahan pakta integritas; bukan mitra pengguna.

## Batas Ownership
1. Skema database/ERD, RLS, serta rancangan trigger basis data merupakan kontribusi Dwikhi; trigger audit tidak diklaim aktif pada snapshot web 21 Juli 2026. Aset 3D dan hierarchy `Pointer` juga berada di luar ownership Iman.
2. Unity runtime, `BuildingDatabase`, `NavigationReceiver`, `DatabaseSyncChecker`, navigasi, optimasi, dan proses build WebGL merupakan kontribusi Faiz.
3. Iman menyediakan kontrak API, bridge sisi React, integrasi aplikasi, serta deployment artefak WebGL yang dihasilkan oleh Faiz; Iman tidak mengklaim implementasi engine Unity.

## Diagram Relevan
2.9, 2.11, 2.12, 2.13, 2.14, 2.15, 2.16, 2.17 (lihat `../../diagrams/`).

## Acuan
- Kontrak konten bersama dan include: `../../content/README.md`
- PRD: `../../PRD_Konsolidasi_TA.md`
- Panduan branch tim: `../../PANDUAN-TIM.md`
