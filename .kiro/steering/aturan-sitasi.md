---
inclusion: fileMatch
fileMatchPattern: 'Tugas_Akhir_Draft.md'
---

# Aturan Sitasi & Penulisan Ilmiah (Tugas Akhir)

Aturan ini berlaku saat menulis atau menyunting isi laporan Tugas Akhir
(`Tugas_Akhir_Draft.md`). Tujuannya menjaga klaim tetap dapat
dipertanggungjawabkan secara akademik dan konsisten dengan Daftar Pustaka.

## Prinsip utama

- Setiap **klaim faktual yang bukan pengetahuan umum** wajib didukung sitasi.
- Gaya sitasi: **APA in-text** — `(Nama, Tahun)`, `(Nama et al., Tahun)`.
  Beberapa sumber dalam satu kurung dipisah titik koma dan diurutkan alfabetis:
  `(Muharam et al., 2023; Taurusta et al., 2024)`.
- Setiap sitasi in-text **harus ada** entri padanannya di Daftar Pustaka, dan
  sebaliknya tidak boleh ada entri Daftar Pustaka yang tidak pernah dirujuk.

## Latar Belakang WAJIB bersitasi

Pendapat dan aturan: **Latar Belakang justru bagian yang paling padat sitasi.**
Bagian ini membangun argumen "mengapa penelitian ini perlu", sehingga setiap
fondasi argumennya harus berbasis sumber, bukan opini.

Yang **wajib** disitasi di Latar Belakang (dan di seluruh bab teori):

- **Data & statistik** (angka, persentase, tren) — sebutkan sumbernya.
- **Pernyataan tentang penelitian/sistem terdahulu** dan state of the art.
- **Definisi konsep/teori** dan metode yang diadopsi.
- **Klaim tren/urgensi** ("semakin meningkat", "terbukti mempermudah", dll.).
- **Research gap** — celah yang diklaim harus dirujuk ke literatur yang ada.

Yang **tidak perlu** sitasi eksternal:

- Pengetahuan umum yang tak terbantahkan.
- **Hasil/observasi penulis sendiri** (mis. data kuesioner, hasil pengujian) —
  ini dirujuk ke data/lampiran milik sendiri, bukan ke pustaka eksternal,
  mis. "berdasarkan hasil kuesioner (Lampiran 1)".

## Panduan praktis

- Idealnya **setiap paragraf yang memuat klaim faktual punya minimal satu
  sitasi**. Paragraf pembuka Latar Belakang yang menyatakan kondisi/masalah
  tanpa satu pun sitasi adalah tanda bahaya — tambahkan sumber.
- Letakkan sitasi **menempel pada klaimnya**, bukan ditumpuk di akhir paragraf
  atau akhir bab tanpa konteks.
- Jangan menambah sitasi "asal tempel": sumber harus benar-benar mendukung
  klaim yang ditulis.
- Jangan mengarang sumber. Jika sebuah klaim belum punya rujukan, tandai
  dengan `[BUTUH SITASI]` agar mudah ditelusuri, jangan dibiarkan seolah sudah
  tervalidasi.

## Catatan integrasi pipeline (opsional)

Pola yang sama seperti guard "wajib narasi gambar" bisa diterapkan: validator
dapat memberi **peringatan non-fatal** bila ada paragraf di Latar Belakang yang
memuat klaim namun tidak memuat pola sitasi `(... , Tahun)`. Aktifkan hanya
bila diminta.
