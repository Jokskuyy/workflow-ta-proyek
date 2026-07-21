# Ruang Kerja Laporan per Anggota

Folder ini berisi **panduan & kerangka laporan** untuk tiap anggota tim. Penulisan draf sebenarnya dilakukan pada `Tugas_Akhir_Draft.md` di **branch masing-masing** (lihat `../PANDUAN-TIM.md`).

## Pembagian Peran

| Anggota | Peran | Branch |
|---|---|---|
| **Muhammad Iman Nugraha** (2210511129) | Full Stack Web Developer, System Integrator, dan DevOps Engineer | `laporan/iman` |
| **Muhammad Dwikhi Deandra Purnianto** | 3D Asset Designer & Database Schema Designer | `laporan/dwikhi` |
| **Muammar Faiz Khairul Anam** | 3D Simulator & Engine Developer | `laporan/faiz` |

## Isi Folder

- `iman-fullstack-integrator/` — panduan & lingkup peran Iman
- `dwikhi-3d-asset-database/` — panduan + `outline-laporan.md` peran Dwikhi
- `faiz-engine-developer/` — panduan + `outline-laporan.md` peran Faiz

## Sumber Daya Bersama (tersedia di repo ini)

- **Kontrak konten bersama untuk manusia/AI:** `../content/README.md`
- **Fragment laporan yang identik:** `../content/shared/`
- **PRD (acuan kebutuhan):** `../PRD_Konsolidasi_TA.md`
- **Diagram (PlantUML + PNG/SVG):** `../diagrams/`
- **Diagram alur (Mermaid):** `../diagram_alur_sistem.md`
- **Screenshot antarmuka:** `../dokumentasi/`
- **Toolkit penulisan & format:** `../skills/`, `../scratch/`, `../tests/`

## Aturan AI Agent dan Shared Content

AI agent pada branch mana pun harus mulai dari `../AGENTS.md`. Jika `Tugas_Akhir_Draft.md` memuat `PIPELINE:INCLUDE`, agent wajib membaca fragment target sebelum menyimpulkan atau mengubah isi subbab. Angka pengujian, temuan UAT, dan konteks proyek bersama diubah pada `../content/shared/`; fokus kontribusi dan identitas tetap berada pada branch masing-masing.

## Relevansi Diagram per Anggota

| Diagram (di `../diagrams/`) | Iman | Dwikhi | Faiz |
|---|:---:|:---:|:---:|
| 2.9 Arsitektur Sistem | ✅ | ✅ | ✅ |
| 2.11 Legenda Use Case | ✅ | ✅ | ✅ |
| 2.12 Use Case Diagram | ✅ | ✅ | ✅ |
| 2.13 Activity: Pengelolaan Data Admin | ✅ | ✅ | |
| 2.14 Activity: Integrasi Data Denah | ✅ | | ✅ |
| 2.15 Sequence: Autentikasi Admin | ✅ | | |
| 2.16 Sequence: Sinkronisasi Data & Unity | ✅ | ✅ | ✅ |
| 2.17 Entity-Relationship Diagram | ✅ | ✅ | |
| 3.1 Hierarki Prefab Gedung (Pointer) | | ✅ | ✅ |
| 3.2 UI Database Sync Checker | | | ✅ |
