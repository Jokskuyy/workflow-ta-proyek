# Panduan Tim — Workflow Branch Laporan TA

Repo ini (`workflow-ta-proyek`) dipakai bersama oleh **3 anggota**, namun **setiap anggota menulis laporan TA-nya sendiri**. Karena pipeline format `.docx` dirancang untuk **satu draf tunggal** `Tugas_Akhir_Draft.md` di root, pemisahan antaranggota dilakukan lewat **branch git**, bukan subfolder. Dengan begitu pipeline tetap berjalan tanpa perubahan pada setiap branch.

## Struktur Branch

| Branch | Isi `Tugas_Akhir_Draft.md` | Pemilik |
|---|---|---|
| `master` | Template/kerangka kosong + seluruh toolkit & aset bersama | Bersama |
| `laporan/iman` | Draf lengkap peran Full Stack & Integrator | Iman |
| `laporan/dwikhi` | Kerangka peran 3D Asset & Database | Dwikhi |
| `laporan/faiz` | Kerangka peran Simulator & Engine | Faiz |

Yang **bersama di semua branch**: `skills/`, `scratch/`, `tests/`, `diagrams/`, `dokumentasi/`, `PRD_Konsolidasi_TA.md`, `diagram_alur_sistem.md`, `laporan-tim/` (README & outline tiap peran).

## Cara Mulai (tiap anggota)

```bash
# 1. Clone repo
git clone https://github.com/Jokskuyy/workflow-ta-proyek.git
cd workflow-ta-proyek

# 2. Pindah ke branch milikmu (contoh: Dwikhi)
git checkout laporan/dwikhi

# 3. Tulis laporan di Tugas_Akhir_Draft.md (lihat panduan peran di laporan-tim/<peran>/)

# 4. Commit & push perubahan ke branch sendiri
git add Tugas_Akhir_Draft.md
git commit -m "tulis bab ..."
git push origin laporan/dwikhi
```

## Aturan Kolaborasi
- **Jangan menulis draf langsung di `master`.** `master` hanya untuk template + pembaruan toolkit/aset bersama.
- Setiap anggota hanya menyunting `Tugas_Akhir_Draft.md` di **branch sendiri** untuk menghindari konflik.
- Perbaikan toolkit/aset bersama (skills, diagrams, dll.) dilakukan di `master`, lalu tiap anggota `git merge master` ke branch-nya agar sinkron.
- Output `.docx` (`Tugas_Akhir_Formatted.docx`) di-*ignore* git dan dibuat lokal oleh masing-masing.

## Menjalankan Pipeline Format
Sama untuk semua branch (lihat `README.md`). Pipeline membaca `Tugas_Akhir_Draft.md` di root, jadi pastikan kamu berada di branch yang benar sebelum membangun `.docx`.

## Catatan Aset Eksternal (di luar repo ini)
- **Kode sumber** ada di repo terpisah:
  - Web + Backend: `https://github.com/Jokskuyy/dashboard-profile-upnvj`
  - Unity (engine 3D): repo `T_A---Copy`
- **Data survei kuesioner** (`.xlsx`) disimpan di penyimpanan tim (bukan di repo ini).
