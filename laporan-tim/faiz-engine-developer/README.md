# Laporan TA — Muammar Faiz Khairul Anam (3D Simulator & Engine Developer)

**Branch:** `laporan/faiz` — tulis laporan di `Tugas_Akhir_Draft.md` (root repo) saat berada di branch ini.

## Fokus / Lingkup Laporan
Berdasarkan pembagian peran (BAB II — Wawancara Stakeholder), kontribusi:
1. **Sistem Navigasi Spasial** — NavMesh pathfinding lintas gedung & multi-lantai (`NavigationGuide`, `NavigationReceiver`).
2. **Rendering Rute Visual** — interpolasi **Catmull-Rom Centripetal** + raycast subdivisi; label nama tujuan & jarak.
3. **Optimasi Performa** — **Building Culling** & **WebGL Settings Optimizer** (Brotli, IL2CPP, stripping).
4. **Kontrol & Interaksi** — **Pointer Lock** & **joystick virtual** mobile.
5. **Konsumsi Data Engine** — `BuildingDatabase` menarik data via `HTTP GET /api/unity/data`.
6. **Editor Tool** — **DatabaseSyncChecker** (validasi `unity_object_name` DB vs scene).

> Ruang lingkup: logika engine 3D & runtime. Pembuatan aset = Dwikhi; API/integrasi web = Iman.

## Diagram Relevan
- **2.14 Activity: Integrasi Data Denah**
- **2.16 Sequence: Sinkronisasi Data & Unity**
- **3.1 Hierarki Prefab Gedung (Pointer)**
- **3.2 UI Database Sync Checker**
- **2.9 Arsitektur Sistem** *(konteks bersama)*
- Sumber diagram: `../../diagrams/`.

## Yang Perlu Ditambahkan Sendiri
- Diagram alur algoritma pathfinding (NavMesh → CalculatePath → Catmull-Rom → raycast → render).
- Ilustrasi sebelum/sesudah Building Culling (performa).
- Screenshot joystick mobile & Pointer Lock.
- Diagram konfigurasi build WebGL.

## Acuan
- PRD (bagian "Modul Unity (C#)", "Build & Performa WebGL", "Testing Decisions"): `../../PRD_Konsolidasi_TA.md`
- Kerangka laporan: `outline-laporan.md`
- Kode Unity: repo eksternal (lihat `../../PANDUAN-TIM.md`).
