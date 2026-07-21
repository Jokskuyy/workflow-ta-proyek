# Handoff Manual Sinkronisasi Laporan Tugas Akhir Tim Denah Virtual UPNVJ

> **Untuk AI yang menangani branch `laporan/dwikhi` atau `laporan/faiz`.**
>
> Dokumen ini hanya menjadi panduan sinkronisasi manual. Jangan melakukan merge, cherry-pick, checkout, restore, atau rebase dari branch `laporan/iman`. Jangan mengganti draf, fakta proyek, atau manifest gambar branch penerima secara utuh.

## 1. Tujuan dan Sumber Kebenaran

Tujuan pekerjaan adalah menyamakan fakta dan materi proyek bersama pada tiga laporan tanpa mengubah kontribusi teknis personal. Laporan tetap merupakan tiga karya yang berbeda berdasarkan ownership masing-masing.

Snapshot konten final yang menjadi rujukan handoff ini adalah commit:

```text
bbc9ee2  docs: perbarui draf TA dan bukti pengujian
```

Jika repository penerima memiliki akses ke remote yang sama, isi sumber dapat dibaca tanpa mengubah working tree dengan pola berikut:

```powershell
git fetch origin laporan/iman
git show bbc9ee2:content/shared/bab1/latar-belakang-umum.md
git show bbc9ee2:content/shared/testing/blackbox.md
git show bbc9ee2:content/shared/testing/uat.md
git show bbc9ee2:content/shared/testing/uat-revisions.md
git show bbc9ee2:content/shared/testing/appendix-instruments.md
git show bbc9ee2:Tugas_Akhir_Draft.md
```

Perintah `git show` hanya dipakai untuk membaca. Dilarang mengganti file lokal dengan seluruh file dari commit Iman. Jika commit tersebut tidak tersedia, gunakan fakta kanonik dalam dokumen ini dan minta salinan fragment terkait kepada Iman. Jangan mengisi kekosongan dengan tebakan.

## 2. Gerbang Keselamatan: Commit dan Push Sebelum Menyunting

Jangan melakukan sinkronisasi sebelum seluruh langkah berikut berhasil.

1. Pastikan branch aktif benar:

   ```powershell
   git branch --show-current
   ```

   Hasil yang diizinkan hanya `laporan/dwikhi` atau `laporan/faiz`. Jika hasilnya berbeda, berhenti.

2. Periksa seluruh perubahan lokal:

   ```powershell
   git status --short
   git diff --check
   ```

3. Tinjau setiap file yang akan masuk checkpoint. Jangan commit `.env`, service role key, kata sandi, token, output DOCX, folder runtime sementara, atau kredensial apa pun. Jangan memakai `git add -A` sebelum daftar file ditinjau.
4. Stage hanya pekerjaan laporan milik pemilik branch, lalu periksa staged diff:

   ```powershell
   git add -- <daftar-file-yang-sudah-ditinjau>
   git diff --cached --stat
   git diff --cached
   ```

5. Buat checkpoint:

   ```powershell
   git commit -m "chore(laporan): checkpoint sebelum sinkronisasi konten bersama"
   git push origin HEAD
   git rev-parse HEAD
   ```

6. Simpan hash hasil `git rev-parse HEAD` sebagai `CHECKPOINT_SEBELUM_SYNC`. Jika commit atau push gagal, berhenti dan jangan mengubah materi laporan.
7. Setelah checkpoint aman, lakukan sinkronisasi manual dan buat commit kedua yang terpisah. Jangan menggabungkan checkpoint dengan commit sinkronisasi.

## 3. Branch dan Ownership yang Tidak Boleh Berubah

| Anggota | Branch | Role Formal | Ownership Utama |
| --- | --- | --- | --- |
| Muhammad Iman Nugraha | `laporan/iman` | Full Stack Web Developer, System Integrator, dan DevOps Engineer | React Public Dashboard dan Admin Panel, REST API Vercel, integrasi Supabase Auth/CRUD, bridge sisi React, deployment, operasional web, serta pengujian web/API |
| Muhammad Dwikhi Deandra Purnianto | `laporan/dwikhi` | 3D Asset Designer dan Database Schema Designer | ERD, skema dan relasi database, RLS, rancangan trigger audit, data/mapping, aset 3D, prefab, dan hierarchy `Pointer` |
| Muammar Faiz Khairul Anam | `laporan/faiz` | 3D Simulator dan Engine Developer | Runtime Unity, `BuildingDatabase`, `NavigationReceiver`, navigasi, label tujuan, minimap, spawn, tooling editor, optimasi, completion event, dan build WebGL |

Ketergantungan antarkomponen tidak memindahkan ownership. Contoh: Iman menyediakan `/api/unity/data`, tetapi Faiz memiliki consumer runtime Unity. Iman mendeploy artefak WebGL, tetapi Faiz memiliki source, optimasi, dan proses build Unity. Dwikhi merancang skema/RLS, sedangkan Iman mengintegrasikan Supabase SDK dari aplikasi web.

## 4. Bagian yang Dilindungi

Jangan mengubah substansi bagian berikut kecuali pemilik branch secara eksplisit memintanya:

1. Judul personal, nama, NIM, dan identitas cover.
2. Identifikasi/rumusan masalah, batasan masalah, tujuan, serta manfaat khusus role.
3. Rancangan teknis khusus role pada BAB II setelah konteks observasi bersama.
4. Implementasi, konfigurasi, kode sumber, logbook, gambar, dan bukti teknis role pada BAB III.
5. Pengujian teknis khusus role. Hasil pengujian bersama ditambahkan setelahnya, bukan menggantikannya.
6. Kesimpulan dan saran kontribusi personal pada BAB IV.
7. Lampiran kode dan bukti teknis personal.
8. `content/roles/<role>/` dan aset dokumentasi milik role.

Dilarang menyalin utuh dari Iman:

- `Tugas_Akhir_Draft.md`;
- `project_facts.json`;
- `images/manifest.json`;
- screenshot frontend, Admin Panel, API, Lighthouse, atau lampiran kode Iman;
- hasil 129 pengujian React sebagai hasil pengujian teknis Dwikhi/Faiz;
- kesimpulan Full Stack, System Integrator, atau DevOps.

## 5. Materi yang Harus Sama

Nomor subbab boleh berbeda jika struktur role memerlukannya, tetapi fakta, angka, status, dan batas interpretasinya harus sama.

| Materi | Lokasi yang Disarankan | Aturan Sinkronisasi |
| --- | --- | --- |
| Konteks Latar Belakang | 1.1 | Gunakan konteks Smart Campus, visualisasi 3D, informasi resmi UPNVJ, kuesioner, dan batas klaim yang sama. Tambahkan fokus role setelah konteks bersama. |
| Jadwal proyek | 1.5 | Enam bulan dan ditulis retrospektif sebagai kegiatan yang telah dilaksanakan. Jangan memakai “Usulan Jadwal”. |
| Observasi dan sistem berjalan | 2.1 | Gunakan angka kuesioner dan batas interpretasi yang sama. Implikasi terakhir boleh diarahkan ke role masing-masing. |
| Profil mitra/pemangku kepentingan | 3.1 | Humas adalah mitra pengguna. UPA TIK adalah koordinasi teknis/institusional, bukan mitra pengguna. |
| Black Box | Setelah pengujian teknis role | Pertahankan hasil awal 23/24 dan retest final 24/24. |
| UAT | Setelah Black Box | Pertahankan peserta, instrumen, nilai, dan batas generalisasi yang sama. |
| Tindak lanjut UAT | Setelah UAT | Pertahankan R01–R10 dan status final. Jelaskan kontribusi revisi sesuai role. |
| Instrumen UAT anonim | Lampiran berikutnya yang tersedia | Jelaskan UAT tertutup; gunakan 9 pernyataan evaluasi Dashboard Publik, 11 pernyataan evaluasi Dashboard Admin, dan 5 kode peserta anonim. |
| Daftar pustaka | Daftar Pustaka tiap branch | Masukkan referensi yang dipakai materi bersama, lalu pertahankan referensi teknis khusus role. |

Apabila draf memakai `PIPELINE:INCLUDE`, isi fragment di `content/shared/` tidak boleh diedit untuk menyesuaikan satu role. Narasi kontribusi role ditulis sebelum atau sesudah include pada draf branch.

## 6. Fakta Final Proyek Bersama

### 6.1 Tahun, Produk, dan Pengguna

1. Tahun cover adalah **2026**.
2. Judul laporan harus unik per anggota. Jangan menyalin judul Iman ke branch lain.
3. Produk merupakan prototipe denah virtual UPNVJ Kampus Pondok Labu dengan Public Dashboard, Admin Panel, Denah 2D, dan Unity WebGL 3D.
4. Pengguna layanan mencakup mahasiswa baru, orang tua/wali, sivitas akademika, dan pengunjung eksternal.
5. Produk belum diklaim sebagai layanan resmi institusi, belum diserahterimakan secara formal, dan belum terintegrasi aktif dengan seluruh sistem internal kampus.
6. Vercel digunakan untuk hosting saat ini. Integrasi dengan infrastruktur kampus merupakan kemungkinan pengembangan mendatang yang memerlukan izin dan penyesuaian kontrak.

### 6.2 Mitra dan Pemangku Kepentingan

1. **Humas UPNVJ** adalah mitra pengguna dan peserta UAT.
2. Satu perwakilan Humas mengikuti UAT. Keterlibatan satu peserta tidak mewakili seluruh Humas, seluruh sivitas akademika, atau persetujuan formal UPNVJ.
3. **UPA TIK UPNVJ bukan mitra pengguna.** Perannya terbatas pada koordinasi teknis, batas akses/kebijakan data, kemungkinan integrasi institusional, wawancara, dan penyerahan pakta integritas.
4. Wawancara Kepala UPA TIK dan Wakil Rektor digunakan untuk memahami batas akses data dan kemungkinan integrasi teknis. Wawancara tidak membuktikan ketiadaan sistem UPNVJ dan tidak menetapkan navigasi sebagai prioritas strategis institusi.
5. Lampiran pakta integritas hanya didukung foto penyerahan dokumen kepada staf UPA TIK. Jangan mengklaim nomor surat, tanggal pengesahan, identitas penandatangan, salinan scan bertanda tangan, atau persetujuan sistem.

Hubungan yang dipakai dalam ketiga laporan:

| Entitas | Hubungan dengan Proyek | Batas Klaim |
| --- | --- | --- |
| Humas UPNVJ | Mitra pengguna; satu perwakilan mengikuti UAT | Tidak diklaim sebagai persetujuan atau penerimaan institusional |
| Pengguna publik | Sumber kebutuhan awal melalui kuesioner 21 responden dan penerima manfaat navigasi | Tidak menjadi sampel UAT tertutup |
| UPA TIK UPNVJ | Koordinasi teknis, kebijakan data, integrasi mendatang, dan penyerahan pakta | Bukan mitra pengguna atau penerima sistem |
| Tim pengembang | Mengimplementasikan komponen sesuai ownership | Tidak boleh saling mengambil klaim kontribusi |

### 6.3 Observasi dan Data Kuesioner Awal

1. Kuesioner awal diisi oleh **21 responden**.
2. Sebanyak 20 dari 21 responden atau **95,2 persen** merupakan sivitas akademika; satu merupakan pengunjung eksternal.
3. Efektivitas papan penunjuk/peta statis memperoleh rata-rata sekitar **3,05 dari 5**. Data ini tidak membuktikan seluruh media kampus tidak informatif.
4. Sebanyak 14 dari 21 responden atau **66,7 persen** pernah mengalami kesulitan menemukan lokasi setidaknya satu kali dalam satu semester.
5. Sebanyak **90,5 persen** responden paling sering bertanya kepada orang lain ketika mencari lokasi.
6. Sebanyak **76,2 persen** memberi nilai 4 atau 5 terhadap pentingnya peta virtual 3D terintegrasi informasi fasilitas.
7. Rencana penggunaan terbesar adalah ketika mencari lokasi tertentu, yaitu **61,9 persen**.
8. Informasi yang paling diprioritaskan adalah nama gedung **95,2 persen**, fasilitas dalam ruangan **52,4 persen**, dan kapasitas ruangan **38,1 persen**.
9. Seluruh angka diperlakukan sebagai temuan sampel, bukan generalisasi bagi seluruh pengguna UPNVJ.
10. Situs resmi UPNVJ telah memiliki halaman lokasi dan fasilitas. Jangan menyatakan UPNVJ sama sekali tidak mempunyai sistem, backend, atau informasi digital.

### 6.4 Jadwal Bersama

Jadwal proyek berlangsung enam bulan:

| Aktivitas | Waktu |
| --- | --- |
| Desain Arsitektur dan UI | Bulan 1 |
| Pengembangan Backend | Bulan 2–3 |
| Pengembangan Frontend | Bulan 3–4 |
| Integrasi dan Pengujian Sistem | Bulan 4–5 |
| Revisi Final dan Penulisan Laporan | Bulan 5–6 |
| Dokumentasi | Bulan 1–6 |

Jadwal menjelaskan pelaksanaan tim. Penjabaran setelah tabel boleh menyoroti pekerjaan role masing-masing, tetapi tidak mengubah urutan proyek bersama.

### 6.5 Kontrak Arsitektur dan Integrasi

Gunakan kontrak aktual berikut:

1. Browser memuat React SPA dan artefak Unity WebGL dari Vercel.
2. React mengakses Supabase Auth dan Supabase SDK secara langsung untuk autentikasi, sesi JWT, query, dan CRUD yang dibatasi RLS.
3. Login tidak melalui REST API buatan Iman.
4. Vercel Serverless Functions menyediakan REST API, termasuk `/api/unity/data`, `/api/unity/names`, dan `/api/health`.
5. Unity runtime melalui `BuildingDatabase` mengambil data sendiri dari `GET /api/unity/data`.
6. `/api/unity/names` digunakan tooling Unity Editor, bukan jalur runtime.
7. React tidak mengirim JSON data gedung/fasilitas ke Unity. React hanya mengirim `unity_object_name` melalui `SendMessage("NavigationReceiver", "NavigateTo", ...)`.
8. Setelah tiba normal, Unity mengirim event `OnNavigationCompleted` dengan JSON `unity_object_name`.
9. React mencocokkan callback dengan tujuan aktif sebelum menampilkan notifikasi tiba. Payload kosong, rusak, berbeda, atau setelah pembatalan diabaikan.
10. Express hanya merupakan jalur opsional proxy/rate limiter Umami. Express bukan backend API utama.
11. Jalur analitik antarmuka yang aktif menggunakan Supabase; Umami Docker dipertahankan sebagai jalur operasional opsional.
12. Build Unity aktif adalah **v0.8.6.1**. Observasi Network v0.8.0 dan Lighthouse `bdeb5bc` merupakan snapshot historis dan tidak boleh dijadikan benchmark build aktif tanpa pengukuran ulang.
13. Screenshot deployment yang ditinjau masih memperlihatkan petunjuk kontrol ringkas pada footer canvas. Jangan mengklaim panel/footer tersebut telah hilang jika bukti branch tidak menunjukkan demikian.

### 6.6 Fitur Aktual

Fitur publik yang boleh dinyatakan:

- informasi utama kampus;
- statistik kunjungan;
- kartu gedung dan fasilitas;
- pencarian lokasi;
- Tutorial dan FAQ;
- Denah 2D dan Denah 3D;
- bantuan dan pergantian mode;
- pemilihan titik awal serta notifikasi tiba pada alur 3D.

Fitur Admin Panel yang boleh dinyatakan:

- Gedung;
- Fasilitas;
- Program Studi;
- konfigurasi Denah 2D;
- Analytics;
- Audit Log.

Fakultas hanya menjadi referensi pada formulir Program Studi dan bukan tab CRUD terpisah. Jangan mengklaim tabel akreditasi publik, CRUD fakultas, atau embed data mahasiswa/dosen sebagai fitur aktif.

## 7. Hasil Pengujian Bersama

### 7.1 Black Box

1. Jumlah skenario: **24**.
2. Hasil awal: **23 lulus, 1 tidak lulus**, atau **95,83 persen**.
3. Skenario awal yang tidak lulus: **BB-20**, karena label tujuan menampilkan identifier internal `unity_object_name`.
4. Tindakan korektif: memisahkan script testing dari build produksi, memulihkan nama tampilan, membangun ulang, dan melakukan retest.
5. Bukti retest:
   - `BB20_1.png`: garis rute aktif, label `Gedung Dewi Sartika`, dan jarak 16 meter sebelum completion;
   - `BB20_2.png`: garis rute hilang dan notifikasi tiba tampil setelah completion.
6. Hasil akhir: **24 dari 24 terverifikasi lulus** atau **100 persen**.
7. Tetap jelaskan hasil awal dan tindakan korektif. Jangan mengubah sejarah pengujian menjadi “langsung 24/24”.

### 7.2 User Acceptance Testing

1. UAT dilaksanakan secara tertutup dan tidak melibatkan sampel mahasiswa baru, orang tua atau wali, maupun pengunjung eksternal.
2. Lima peserta unik: dua dosen penguji, dua dosen pembimbing, dan satu perwakilan Humas UPNVJ.
3. Instrumen evaluasi Dashboard Publik: 9 pernyataan, 4 pengisi, skor **140/180**, rata-rata **3,89**, hasil **77,78 persen**. Nama instrumen menunjukkan komponen yang dinilai, bukan asal peserta.
4. Instrumen evaluasi Dashboard Admin: 11 pernyataan, 4 pengisi, skor **186/220**, rata-rata **4,23**, hasil **84,55 persen**.
5. Gabungan seluruh jawaban: **326/400** atau **81,50 persen**.
6. Sebagian peserta mengisi dua instrumen; jangan menjumlahkannya menjadi delapan peserta unik.
7. Tangkapan layar revisi merupakan verifikasi pascaimplementasi, bukan UAT kuesioner kedua.
8. Hasil tidak boleh digeneralisasi sebagai penilaian pengguna publik, seluruh sivitas akademika, atau penerimaan institusional.

### 7.3 Tindak Lanjut UAT R01–R10

UAT-R11 tidak ada. Perubahan judul diperiksa melalui cover dan bukan bagian pengujian produk.

| ID | Tindak Lanjut Final | Ownership yang Boleh Dijelaskan | Batas Klaim |
| --- | --- | --- | --- |
| R01 | 119 nama distandarkan dan 189 deskripsi diperbaiki; alias pencarian ditambahkan | Dwikhi: data/seed; Iman: indeks pencarian deskripsi | Reseed Supabase live belum diklaim |
| R02 | Tutorial dan FAQ 2D/3D serta tutorial Unity desktop/mobile | Iman: Tutorial/FAQ web; Faiz: tutorial runtime | Bukan retest UAT baru |
| R03 | Pemilih mode dan Denah 2D dengan graph A* | Iman | Jangan diklaim sebagai implementasi engine Unity |
| R04 | Label tujuan dinamis menampilkan nama dan jarak; object tulisan tersedia pada sejumlah area | Faiz: runtime/label; Dwikhi: aset/object scene sesuai bukti | Jangan klaim seluruh 311 fasilitas memiliki label statis |
| R05 | Adaptasi kontekstual melalui bahasa, perangkat, mode, tutorial, pencarian, dan spawn | Iman: web; Faiz: runtime/spawn | Tidak ada profil persona tersimpan |
| R06 | Minimap north-up menampilkan posisi dan konteks kampus | Faiz | Verifikasi visual tidak menggantikan retest pengguna |
| R07 | Pilihan 2D/3D; titik awal 2D; 16 spawn 3D dengan validasi NavMesh | Iman: chooser/2D; Faiz: spawn/NavMesh | Screenshot tidak menampilkan seluruh spawn satu per satu |
| R08 | Tombol bantuan dan kontak resmi Penmaru UPNVJ | Iman | Kontak berasal dari sumber resmi; bukan hotline darurat |
| R09 | Dari 339 record, 27 dikeluarkan dari scope dan satu duplikasi diselesaikan; seed akhir 311 fasilitas unik | Dwikhi | Sinkronisasi live dan seluruh GameObject tidak dilebihkan |
| R10 | Unity mengirim completion JSON; React memvalidasi target dan menampilkan popup | Faiz: completion runtime; Iman: listener/validasi React | Kondisi negatif diverifikasi pengujian React, bukan screenshot saja |

Status seluruh R01–R10 adalah **Diterapkan**, dengan basis verifikasi visual, audit kode sumber, pengujian otomatis, atau sumber resmi sesuai barisnya.

## 8. Angka Pengujian Khusus Iman yang Tidak Boleh Diambil Alih

Informasi berikut boleh disebut sebagai konteks verifikasi aplikasi web bersama, tetapi harus diatribusikan kepada implementasi/pengujian Iman dan tidak boleh dijadikan hasil pengujian teknis Dwikhi atau Faiz:

1. Kode sumber web aktif `08ebc06`.
2. Vitest/React Testing Library: **13 file dan 129 pengujian lulus**.
3. Sebanyak **11 pengujian** memeriksa kontrak `OnNavigationCompleted`.
4. ESLint, TypeScript build, dan production build lulus.
5. Empat smoke test manual API: health, data runtime Unity, identifier editor, dan penolakan mutasi anonim.
6. Lighthouse historis `bdeb5bc`: Performance mobile 86 dan desktop 99; Accessibility, Best Practices, dan SEO 100 pada kedua mode.
7. Belum ada hasil Playwright/browser end-to-end yang boleh diklaim.

Faiz harus menggunakan pengujian Unity/runtime miliknya untuk membuktikan engine. Dwikhi harus menggunakan pengujian integritas data, RLS, mapping, dan aset miliknya untuk membuktikan kontribusi database/aset.

## 9. Diskrepansi yang Wajib Dihapus

Cari dan koreksi apabila masih ditemukan:

1. UPA TIK disebut sebagai mitra pengguna.
2. Humas disebut memberi persetujuan formal, menerima serah terima, atau mewakili seluruh pengguna.
3. UAT-R11 atau status R01–R10 masih `needs_verification`.
4. BB-20 hanya disebut tidak lulus tanpa hasil retest.
5. Black Box masih berjumlah 18 skenario atau hasil akhir bukan 24/24.
6. Target pemuatan WebGL kurang dari 10 detik tanpa pengukuran yang relevan.
7. React digambarkan melakukan login melalui backend API sebelum Supabase.
8. React digambarkan mengirim seluruh JSON data gedung/fasilitas ke Unity.
9. `/api/unity/names` disebut sebagai endpoint runtime.
10. Callback `OnNavigationCompleted` disebut belum tersedia atau alurnya masih satu arah.
11. Express disebut backend utama.
12. Umami disebut sebagai jalur analitik aktif tanpa membedakannya dari implementasi Supabase saat ini.
13. Public Dashboard diklaim menampilkan akreditasi atau tabel Program Studi.
14. Admin Panel diklaim memiliki CRUD Fakultas terpisah.
15. Sistem diklaim mengelola atau embed data mahasiswa/dosen.
16. Iman mengklaim ERD, RLS, trigger database, hierarchy `Pointer`, scene, NavMesh, atau build Unity.
17. Dwikhi/Faiz mengklaim frontend React, REST API, bridge sisi React, atau deployment Vercel sebagai implementasi mereka.
18. Dwikhi mengklaim runtime Unity/tooling milik Faiz, atau Faiz mengklaim skema/aset milik Dwikhi.
19. Audit trigger disebut aktif pada snapshot web tanpa bukti; snapshot web mencatat audit melalui service aplikasi, sementara rancangan trigger tetap ownership Dwikhi.
20. Observasi Network v0.8.0 atau Lighthouse historis diperlakukan sebagai benchmark v0.8.6.1.

## 10. Referensi Bersama yang Harus Konsisten

Masukkan hanya referensi yang benar-benar disitasi pada draf branch. Pertahankan urutan alfabetis dan jangan menghapus sumber khusus role.

```text
Aliyah, A., Hartono, N., dan Muin, A. A. (2025). Penggunaan User Acceptance Testing (UAT) pada pengujian sistem informasi pengelolaan keuangan dan inventaris barang. Switch: Jurnal Sains dan Teknologi Informasi, 3(2), 42–58. https://doi.org/10.62951/switch.v3i1.330

Jamaludin, J., dan Saepuloh, L. (2024). Tren riset twin digital smart campus. Sang Pencerah: Jurnal Ilmiah Universitas Muhammadiyah Buton, 10(2), 408–425. https://doi.org/10.35326/pencerah.v10i2.5317

Maulida, M., Zahro, F., Hakim, R., dan Akbar, M. S. (2025). Pengujian black box testing pada sistem website pemesanan online Toko Ayam Krispy. Jurnal Media Akademik (JMA), 3(5). https://doi.org/10.62281/v3i5.1908

Muharam, Y., Anggara, M. B., dan Hanafi, T. J. (2023). Implementasi peta 3 dimensi menggunakan metode IMSDD (Interactive Multimedia System Design and Development) dan WebGL API berbasis web (Studi kasus di SMP Karya Pembangunan 2 Majalaya). Jurnal Informatika-COMPUTING, 10, 20–30. https://doi.org/10.55222/computing.v10i01.1155

Taurusta, C., Asiddiq, A. M., Suprianto, S., dan Setiawan, H. (2024). Visualisasi gedung kampus 1 Universitas Muhammadiyah Sidoarjo menggunakan augmented reality sebagai media informasi. Journal of Technology and System Information, 1(1), 55–70. https://doi.org/10.47134/jtsi.v1i1.2146

UPNVJ. (2022). Lokasi kampus. https://www.upnvj.ac.id/id/tentang-upn/lokasi-kampus.html

UPNVJ. (2025a). Kantin. https://www.upnvj.ac.id/id/fasilitas-layanan/kantin.html

UPNVJ. (2025b). Sejarah. https://www.upnvj.ac.id/id/tentang-upn/sejarah.html

Nomor bantuan 021-7699431 dan 021-7656971 disebutkan secara natural sebagai nomor yang diambil dari halaman Hubungi Kami pada situs Penmaru UPNVJ: https://penmaru.upnvj.ac.id/id/contact.html. Tidak perlu memberi label sitasi terpisah `UPNVJ 2026a` pada kalimat nomor telepon.

UPNVJ. (2026). Rapat koordinasi Humas UPNVJ 2026: Fokus strategi komunikasi digital dan media sosial perguruan tinggi. https://www.upnvj.ac.id/id/berita/2026/02/rapat-koordinasi-humas-upnvj-2026-fokus-strategi-komunikasi-digital-dan-media-sosial-perguruan-tinggi.html
```

Untuk laporan Dwikhi, referensi database/RLS seperti Putra dapat dipertahankan dengan DOI `https://doi.org/10.36040/jati.v10i2.17551` jika memang disitasi. Untuk laporan Faiz, pertahankan referensi Unity, NavMesh, pathfinding, kontrol, dan optimasi yang benar-benar digunakan pada narasi engine.

## 11. Prosedur Integrasi Manual per Branch

### 11.1 Branch Dwikhi

1. Pertahankan seluruh pembahasan aset 3D, prefab/`Pointer`, ERD, skema, relasi, RLS, rancangan trigger, seed, dan mapping.
2. Tambahkan materi bersama tanpa mengganti pengujian integritas data, pengujian RLS, atau validasi aset–database.
3. Pada tindak lanjut UAT, fokuskan kontribusi Dwikhi pada R01, bagian aset R04, serta R09. Untuk R02/R03/R05/R06/R07/R08/R10, jelaskan sebagai hasil produk bersama atau dependensi anggota lain.
4. Jangan menyalin kode React/API Iman atau internal runtime Unity Faiz ke lampiran kode Dwikhi.
5. `project_facts.json` branch Dwikhi harus mempertahankan identitas/judul Dwikhi. Hanya merge fakta bersama secara selektif; jangan menggantinya dengan file Iman.

### 11.2 Branch Faiz

1. Pertahankan seluruh pembahasan runtime Unity, konsumsi API, NavMesh, rendering rute, label tujuan, minimap, spawn, kontrol, tooling editor, optimasi, dan build WebGL.
2. Tambahkan materi bersama tanpa mengganti pengujian Play Mode, performa WebGL, atau pengujian tooling editor.
3. Pada tindak lanjut UAT, fokuskan kontribusi Faiz pada tutorial runtime R02, R04, bagian runtime R05, R06, spawn R07, dan completion runtime R10.
4. Jangan menyalin kode React/API/deployment Iman atau DDL/RLS/aset milik Dwikhi ke lampiran kode Faiz.
5. `project_facts.json` branch Faiz harus mempertahankan identitas/judul Faiz. Hanya merge fakta bersama secara selektif; jangan menggantinya dengan file Iman.

## 12. Validasi Wajib Setelah Integrasi

1. Bandingkan perubahan terhadap checkpoint:

   ```powershell
   git diff CHECKPOINT_SEBELUM_SYNC -- Tugas_Akhir_Draft.md project_facts.json content images diagrams laporan-tim
   ```

2. Pastikan perubahan hanya terjadi pada materi bersama, sitasi pendukung, dan marker/aset yang memang diperlukan. Jika implementasi atau kesimpulan role berubah tanpa kebutuhan sinkronisasi, pulihkan secara manual dari checkpoint.
3. Validasi JSON yang berubah.
4. Periksa include tanpa membuat DOCX:

   ```powershell
   C:\Python312\python.exe skills/scripts/merge_draft_to_docx.py --check-includes
   ```

5. Jalankan test shared content dan sitasi:

   ```powershell
   C:\Python312\python.exe -m pytest -q tests/test_markdown_shared_includes.py tests/test_shared_content_contract.py tests/test_wpi_guards.py tests/test_wpi_bibliography.py
   ```

6. Jalankan full suite resmi:

   ```powershell
   C:\Python312\python.exe -m pytest -q tests
   ```

7. Periksa whitespace dan konflik:

   ```powershell
   git diff --check
   git status --short
   ```

8. Jangan membuat DOCX. Tinjau Markdown dan aset terlebih dahulu.
9. Setelah semua lulus, commit dan push sinkronisasi secara terpisah:

   ```powershell
   git add -- <file-sinkronisasi-yang-sudah-ditinjau>
   git commit -m "docs(laporan): sinkronkan fakta dan hasil pengujian bersama"
   git push origin HEAD
   ```

## 13. Format Laporan Hasil AI

Setelah selesai, AI harus melaporkan:

1. branch dan hash checkpoint sebelum sinkronisasi;
2. hash commit sinkronisasi;
3. daftar file yang berubah;
4. bagian bersama yang ditambahkan atau diperbarui;
5. bukti bahwa bagian implementasi, kesimpulan, dan lampiran kode role tidak ditimpa;
6. hasil include check, cross-check sitasi, test terfokus, full suite, dan `git diff --check`;
7. keterbatasan atau bukti yang masih belum tersedia;
8. konfirmasi bahwa DOCX tidak dibuat.

Jika terdapat fakta yang bertentangan dengan dokumen ini, jangan memilih salah satu secara diam-diam. Pertahankan checkpoint, hentikan sinkronisasi pada bagian tersebut, dan minta konfirmasi kepada pemilik laporan.
