# Naskah Presentasi Dwikhi Deandra Purnianto

Naskah ini mengikuti bagian Dwikhi pada halaman 9–13 berkas presentasi *standarisasi pada format nama (1).pdf*. Kalimatnya dibuat agar mudah disampaikan secara lisan dan tetap sesuai dengan batas kontribusi penulis.

## Transisi dari Bagian Full Stack

“Terima kasih. Selanjutnya, saya akan menjelaskan bagian yang menjadi tanggung jawab saya dalam proyek ini, yaitu perancangan *asset* 3D kampus dan skema *database*.

Fokus pekerjaan saya dibagi menjadi tiga bagian. Pertama, membuat dan menata *asset* 3D gedung serta fasilitas. Kedua, merancang hubungan data gedung, fasilitas, fakultas, dan program studi. Ketiga, menjaga agar nama objek di *Unity* dapat dipetakan dengan data yang sesuai pada *database*.”

## Slide 1 — Perancangan Asset 3D Kampus dan Skema Database Supabase

“Perkenalkan, saya Dwikhi Deandra Purnianto. Dalam proyek ini, saya berperan sebagai Desainer *Asset* 3D dan Desainer Skema *Database*.

Pada sisi visual, saya membuat dan menata objek gedung serta fasilitas yang digunakan pada denah tiga dimensi. Pekerjaan tersebut mencakup bentuk objek, material, tekstur, susunan *prefab*, dan objek tujuan navigasi.

Pada sisi data, saya merancang struktur tabel utama dan hubungan antartabel melalui ERD. Saya juga mengelola data gedung dan fasilitas serta menetapkan kode lokasi *Unity* yang menghubungkan data dengan objek tiga dimensi.

Jadi, bagian saya menjadi penghubung antara bentuk lokasi yang dilihat pengguna dan data lokasi yang digunakan oleh sistem.”

## Slide 2 — Agenda Pembahasan

“Pada bagian ini, saya akan menjelaskan tiga hal.

Pertama adalah proses pembuatan dan penataan *asset* 3D. Kedua adalah perancangan ERD dan skema *database*. Ketiga adalah pemetaan identitas antara data dan objek pada *Unity*.

Ketiga bagian ini saling berhubungan. *Asset* menyediakan bentuk visual lokasinya, *database* menyimpan informasinya, sedangkan kode lokasi *Unity* memastikan bahwa data tersebut mengarah ke objek yang tepat.”

## Slide 3 — Pemodelan Asset 3D dan Hierarki Prefab

“Dalam proyek ini, saya mengerjakan 19 *asset* gedung dan satu *asset* fasilitas Masjid. Masjid disebut sebagai fasilitas karena pada data proyek Masjid berada di bawah Gedung Ki Hadjar Dewantara, walaupun pada lingkungan tiga dimensi Masjid memiliki objek tersendiri.

Pembuatan *asset* dimulai dengan mendatangi lokasi kampus dan mengambil foto gedung sebagai referensi visual. Saya tidak melakukan pengukuran dimensi menggunakan alat ukur. Karena itu, model yang dibuat merupakan representasi visual berdasarkan bentuk utama bangunan, jumlah lantai, susunan pintu dan jendela, warna, material, serta perbandingan antarbagian yang terlihat.

Tiga contoh yang digunakan sebagai perwakilan dalam laporan adalah Gedung Rektorat atau Jenderal Soedirman, Gedung Dewi Sartika, dan Gedung Ki Hadjar Dewantara.

*Unity Editor* menjadi alat utama untuk membuat dan menata objek. Beberapa objek pendukung juga dibuat menggunakan *Blender*. Setelah bentuk selesai, saya menerapkan material dan tekstur agar objek lebih mudah dikenali berdasarkan kondisi bangunan aslinya.

Setiap gedung kemudian disusun sebagai *prefab*. Secara sederhana, *prefab* adalah objek yang sudah memiliki bentuk, komponen, dan susunan bagian yang dapat digunakan kembali di dalam *Unity*.

Di dalam hierarki *prefab*, saya memisahkan bagian visual gedung dari objek tujuan. Bagian visual memuat objek yang terlihat, sedangkan objek tujuan ditempatkan di bawah *child* bernama `Pointer`. *Pointer* berisi *GameObject* kosong yang digunakan sebagai penanda lokasi tujuan.

Saya juga mencatat jumlah *GameObject*, *mesh*, *vertex*, *triangle*, material, *collider*, dan ukuran berkas *prefab*. Data tersebut digunakan untuk mendokumentasikan struktur teknis *asset*, bukan untuk menyatakan hasil pengujian atau optimasi performa.”

## Slide 4 — Perancangan ERD dan Skema Database

“Setelah objek tiga dimensi disusun, saya merancang struktur data menggunakan ERD atau *Entity Relationship Diagram*. ERD adalah diagram yang menunjukkan tabel yang digunakan serta hubungan di antara tabel-tabel tersebut.

Empat tabel inti yang saya rancang adalah `gedung`, `fasilitas`, `fakultas`, dan `program_studi`.

Tabel `gedung` menyimpan informasi utama bangunan. Satu gedung dapat mempunyai banyak fasilitas. Gedung juga dapat menjadi lokasi utama bagi fakultas, dan satu fakultas dapat mempunyai beberapa program studi.

Hubungan tersebut dijaga menggunakan *foreign key*. Istilah ini berarti kolom yang menghubungkan satu tabel dengan baris pada tabel lain. Sebagai contoh, `id_gedung` pada tabel `fasilitas` menunjukkan gedung tempat fasilitas tersebut berada.

Saya juga menggunakan batasan unik atau `UNIQUE` pada kolom tertentu. Aturan ini mencegah dua baris menggunakan kode lokasi *Unity* yang sama.

Pada kolom `unity_object_name`, setiap data gedung atau fasilitas mempunyai kode yang digunakan untuk mencari *GameObject* tujuan pada *Unity*. Dengan demikian, nama yang ditampilkan kepada pengguna boleh berubah tanpa harus mengubah kode teknis yang digunakan oleh sistem.

Data awal yang dimasukkan melalui berkas *seed* memuat 19 entitas gedung dan 311 fasilitas. *Seed* adalah kumpulan perintah untuk mengisi data awal ke dalam *database*.

Selain empat tabel inti tersebut, pada tingkat rancangan saya menetapkan kebutuhan kebijakan RLS dan struktur tabel `audit_logs`. RLS merupakan aturan untuk membatasi data berdasarkan hak akses pengguna, sedangkan `audit_logs` dirancang untuk menyimpan catatan perubahan data. Penerapan layanan audit pada Dashboard merupakan bagian dari *Full Stack Web Developer*, *System Integrator*, dan *DevOps Engineer*. Saya tidak mengklaim penerapan SQL produksi maupun *trigger* audit yang tidak memiliki bukti.”

## Slide 5 — Pemetaan dan Sinkronisasi Identitas

“Bagian terakhir adalah pemetaan identitas antara *database* dan *Unity*.

Kolom `unity_object_name` dapat dipahami sebagai kode lokasi *Unity*. Kode yang sama disimpan pada data dan digunakan sebagai nama *GameObject* tujuan di bawah `Pointer`.

Format nama dibuat seragam menggunakan huruf kecil dan tanda garis bawah sebagai pengganti spasi. Contohnya adalah `cipto_mangunkusumo` dan `lab_komp_1`. Penamaan yang seragam memudahkan sistem membandingkan data tanpa bergantung pada nama resmi yang ditampilkan kepada pengguna.

Sebagai contoh, nama tampilan sebuah ruangan dapat diperbaiki agar lebih mudah dibaca, tetapi kode teknisnya tetap dipertahankan. Pemisahan ini mengurangi risiko rute navigasi terganggu hanya karena terjadi perubahan tulisan pada nama gedung atau fasilitas.

Untuk membantu pemeriksaan, saya menggunakan `DatabaseSyncChecker`, yaitu alat pada *Unity Editor* yang membandingkan daftar kode dari *database* dengan nama *GameObject* pada *scene*.

Alat tersebut dikembangkan oleh *3D Simulator* dan *Engine Developer*. Kontribusi saya adalah menetapkan serta memperbaiki nama pada *asset* dan data, kemudian menggunakan alat tersebut untuk melihat nama yang perlu diperiksa. Tampilan pada slide merupakan dokumentasi proses pemeriksaan, bukan pernyataan bahwa seluruh data sudah cocok.

Melalui proses ini, hubungan antara data lokasi dan objek tiga dimensi dapat ditelusuri dengan lebih jelas.”

## Transisi ke Bagian Engine

“Demikian penjelasan bagian saya. Hasil pekerjaan ini menyediakan *asset* tiga dimensi, objek tujuan, struktur data, dan kode lokasi yang digunakan oleh komponen lain dalam sistem.

Selanjutnya, bagian navigasi, perhitungan rute *NavMesh*, kontrol pengguna, serta optimasi *engine* akan dijelaskan oleh *3D Simulator* dan *Engine Developer*. Terima kasih.”

## Catatan Penting saat Menjawab Pertanyaan

1. Jangan menyebut 20 gedung. Gunakan “19 *asset* gedung dan satu *asset* fasilitas Masjid”.
2. Jangan menyatakan model dibuat berdasarkan pengukuran dimensi. Metode yang digunakan adalah observasi visual dan dokumentasi foto.
3. Jangan menyatakan data *mesh*, *vertex*, atau ukuran *prefab* sebagai bukti optimasi performa. Data tersebut merupakan dokumentasi teknis.
4. Jangan mengklaim kode `DatabaseSyncChecker`. Alat tersebut dibuat oleh *3D Simulator* dan *Engine Developer* serta digunakan oleh penulis.
5. Jangan menyatakan tampilan `DatabaseSyncChecker` sebagai hasil akhir bahwa seluruh data sudah cocok.
6. Jangan mengklaim penerapan SQL produksi RLS atau *trigger* audit. Kontribusi penulis berada pada rancangan kebutuhan kebijakan RLS dan skema tabel `audit_logs`.
7. Jika ditanya mengapa nama tampilan dipisahkan dari `unity_object_name`, jawab bahwa nama tampilan dapat berubah mengikuti kebutuhan informasi, sedangkan kode teknis perlu stabil agar pemetaan ke objek *Unity* tidak rusak.
