import os
import re
import shutil
import lxml.etree

# Register all namespaces
for prefix, uri in {
    'wpc': 'http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas',
    'cx': 'http://schemas.microsoft.com/office/drawing/2014/chartex',
    'cx1': 'http://schemas.microsoft.com/office/drawing/2015/9/8/chartex',
    'cx2': 'http://schemas.microsoft.com/office/drawing/2015/10/21/chartex',
    'cx3': 'http://schemas.microsoft.com/office/drawing/2016/5/9/chartex',
    'cx4': 'http://schemas.microsoft.com/office/drawing/2016/5/10/chartex',
    'cx5': 'http://schemas.microsoft.com/office/drawing/2016/5/11/chartex',
    'cx6': 'http://schemas.microsoft.com/office/drawing/2016/5/12/chartex',
    'cx7': 'http://schemas.microsoft.com/office/drawing/2016/5/13/chartex',
    'cx8': 'http://schemas.microsoft.com/office/drawing/2016/5/14/chartex',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
    'aink': 'http://schemas.microsoft.com/office/drawing/2016/ink',
    'am3d': 'http://schemas.microsoft.com/office/drawing/2017/model3d',
    'o': 'urn:schemas-microsoft-com:office:office',
    'oel': 'http://schemas.microsoft.com/office/2019/extlst',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
    'v': 'urn:schemas-microsoft-com:vml',
    'wp14': 'http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'w10': 'urn:schemas-microsoft-com:office:word',
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
    'w15': 'http://schemas.microsoft.com/office/word/2012/wordml',
    'w16cex': 'http://schemas.microsoft.com/office/word/2018/wordml/cex',
    'w16cid': 'http://schemas.microsoft.com/office/word/2016/wordml/cid',
    'w16': 'http://schemas.microsoft.com/office/word/2018/wordml',
    'w16du': 'http://schemas.microsoft.com/office/word/2023/wordml/word16du',
    'w16sdtdh': 'http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash',
    'w16sdtfl': 'http://schemas.microsoft.com/office/word/2024/wordml/sdtformatlock',
    'w16se': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'wpg': 'http://schemas.microsoft.com/office/word/2010/wordprocessingGroup',
    'wpi': 'http://schemas.microsoft.com/office/word/2010/wordprocessingInk',
    'wne': 'http://schemas.microsoft.com/office/word/2006/wordml',
    'wps': 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape'
}.items():
    lxml.etree.register_namespace(prefix, uri)

import sys
sys.path.append('scratch')
from merge_draft_to_docx import build_p_element

new_erd_markdown = """Penjelasan mengenai struktur tabel, kolom, tipe data, serta aturan relasi antartabel dijabarkan sebagai berikut:

1. Tabel `gedung`
   Entitas ini menyimpan data administratif dan fisik dari seluruh bangunan/gedung yang ada di lingkungan UPNVJ Kampus Pondok Labu.
   a. Atribut tabel terdiri atas:
      1) `id`: Tipe `SERIAL` bertindak sebagai Primary Key.
      2) `nama_gedung`: Tipe `VARCHAR(255)`, bernilai unik (*unique*) dan tidak boleh kosong (*not null*).
      3) `deskripsi_gedung`: Tipe `TEXT` untuk penjelasan detail gedung.
      4) `lokasi`: Tipe `TEXT` untuk deskripsi alamat atau letak koordinat fisik.
      5) `jumlah_lantai`: Tipe `INT` dengan nilai default 1.
      6) `foto_url`: Tipe `VARCHAR(255)` untuk menyimpan tautan gambar gedung.
      7) `unity_object_name`: Tipe `TEXT` bersifat unik, berfungsi sebagai jembatan penamaan GameObject pada scene Unity.
   b. Relasi tabel:
      1) Berelasi One-to-Many dengan tabel `fasilitas` melalui foreign key `id_gedung`.
      2) Berelasi One-to-One / Many-to-One dengan tabel `fakultas` melalui foreign key `id_gedung_utama`.

2. Tabel `fasilitas`
   Entitas ini menyimpan data fasilitas spesifik yang berada di dalam suatu gedung (misalnya ruang kelas, laboratorium, perpustakaan, toilet, dll.).
   a. Atribut tabel terdiri atas:
      1) `id`: Tipe `SERIAL` bertindak sebagai Primary Key.
      2) `nama_fasilitas`: Tipe `VARCHAR(255)` untuk nama fasilitas.
      3) `deskripsi_fasilitas`: Tipe `TEXT` untuk penjelasan detail fasilitas.
      4) `tipe_fasilitas`: Tipe `VARCHAR(100)` untuk klasifikasi jenis fasilitas.
      5) `color`: Tipe `VARCHAR(50)` dengan default 'gray' untuk penanda warna visual pada frontend React.
      6) `lantai`: Tipe `INT` dengan default 1 untuk menunjukkan posisi lantai fasilitas.
      7) `foto_url`: Tipe `TEXT` untuk menyimpan tautan gambar fasilitas.
      8) `id_gedung`: Tipe `INT` sebagai Foreign Key yang merujuk ke tabel `gedung` (ON DELETE SET NULL).
      9) `unity_object_name`: Tipe `TEXT` bersifat unik, berfungsi sebagai jembatan penamaan GameObject fasilitas pada scene Unity.
   b. Relasi tabel: Merupakan tabel anak yang bergantung pada tabel `gedung`.

3. Tabel `fakultas`
   Entitas ini menampung data profil fakultas yang berada di lingkungan universitas.
   a. Atribut tabel terdiri atas:
      1) `id`: Tipe `SERIAL` bertindak sebagai Primary Key.
      2) `nama_fakultas`: Tipe `VARCHAR(255)` bersifat unik dan tidak boleh kosong.
      3) `deskripsi_fakultas`: Tipe `TEXT` untuk rincian profil fakultas.
      4) `email`: Tipe `VARCHAR(255)` untuk kontak surat elektronik fakultas.
      5) `website`: Tipe `VARCHAR(255)` untuk alamat web resmi fakultas.
      6) `id_gedung_utama`: Tipe `INT` sebagai Foreign Key yang merujuk ke tabel `gedung` (ON DELETE SET NULL).
   b. Relasi tabel:
      1) Berelasi One-to-Many dengan tabel `program_studi` melalui foreign key `id_fakultas` pada tabel prodi.
      2) Berelasi Many-to-One dengan tabel `gedung` untuk menentukan gedung administrasi utama.

4. Tabel `program_studi`
   Entitas ini menyimpan data program studi yang dinaungi oleh masing-masing fakultas.
   a. Atribut tabel terdiri atas:
      1) `id`: Tipe `SERIAL` bertindak sebagai Primary Key.
      2) `nama_prodi`: Tipe `VARCHAR(255)` untuk nama program studi.
      3) `jenjang`: Tipe `VARCHAR(10)` untuk tingkat pendidikan (D3/S1/S2/S3).
      4) `id_fakultas`: Tipe `INT` sebagai Foreign Key yang merujuk ke tabel `fakultas` (ON DELETE CASCADE).
      5) `akreditasi`: Tipe `VARCHAR(50)` untuk peringkat akreditasi program studi.
   b. Relasi tabel: Bergantung penuh pada tabel `fakultas` melalui foreign key `id_fakultas`. Terdapat batasan unik gabungan (*composite unique key*) pada kolom `nama_prodi`, `jenjang`, dan `id_fakultas`.

5. Tabel `admin_users`
   Entitas ini menyimpan informasi akun administrator yang memiliki hak akses untuk mengelola data konten melalui Admin Panel.
   a. Atribut tabel terdiri atas:
      1) `id`: Tipe `SERIAL` bertindak sebagai Primary Key.
      2) `username`: Tipe `VARCHAR(100)` bersifat unik dan tidak boleh kosong.
      3) `password_hash`: Tipe `TEXT` untuk menyimpan hash kata sandi yang terenkripsi.
      4) `nama_lengkap`: Tipe `VARCHAR(255)` untuk nama lengkap administrator.
      5) `role`: Tipe `VARCHAR(50)` dengan default 'admin'.
      6) `created_at`: Tipe `TIMESTAMP` dengan default waktu saat data dibuat.
   b. Relasi tabel: Tabel independen untuk kebutuhan autentikasi dan otorisasi.

6. Tabel `audit_logs`
   Entitas ini digunakan sebagai pencatat riwayat (audit trail) otomatis terhadap setiap operasi manipulasi data (CRUD) yang dilakukan oleh administrator.
   a. Atribut tabel terdiri atas:
      1) `id`: Tipe `BIGSERIAL` bertindak sebagai Primary Key.
      2) `actor_id`: Tipe `UUID` untuk menyimpan ID admin yang melakukan aksi.
      3) `actor_email`: Tipe `TEXT` untuk menyimpan email administrator.
      4) `action`: Tipe `TEXT` untuk jenis operasi (INSERT/UPDATE/DELETE).
      5) `table_name`: Tipe `TEXT` untuk nama tabel yang mengalami mutasi.
      6) `record_id`: Tipe `TEXT` untuk ID rekaman data yang diubah.
      7) `old_data`: Tipe `JSONB` untuk menyimpan kondisi data lama sebelum diubah (bernilai null saat INSERT).
      8) `new_data`: Tipe `JSONB` untuk menyimpan kondisi data baru sesudah diubah (bernilai null saat DELETE).
      9) `created_at`: Tipe `TIMESTAMP` dengan default waktu mutasi tercatat.
   b. Relasi tabel: Mencatat riwayat mutasi dari tabel-tabel utama secara transparan melalui trigger basis data.

7. Tabel `web_analytics_log`
   Entitas pendukung ini bersifat legacy dan berfungsi untuk mencatat log kunjungan pengguna ke halaman web secara mandiri sebelum digantikan oleh integrasi Umami Analytics.
   a. Atribut tabel terdiri atas:
      1) `id`: Tipe `SERIAL` bertindak sebagai Primary Key.
      2) `visitor_hash`: Tipe `VARCHAR(255)` untuk sidik jari unik browser pengunjung.
      3) `page_path`: Tipe `VARCHAR(255)` untuk menyimpan path halaman yang diakses.
      4) `device_type`: Tipe `VARCHAR(100)` untuk jenis perangkat yang digunakan.
      5) `visited_at`: Tipe `TIMESTAMP` dengan default waktu kunjungan.
   b. Relasi tabel: Tabel mandiri yang mengumpulkan data analitik kunjungan."""

def parse_markdown_string(md_text):
    items = []
    lines = md_text.split('\n')
    list_item_pattern = re.compile(r'^(\s*)([0-9a-zA-Z]+[\.\)])\s+(.*)$')
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        list_match = list_item_pattern.match(line)
        if list_match:
            indent_spaces = len(list_match.group(1))
            marker = list_match.group(2)
            text_content = list_match.group(3)
            list_level = 1
            if marker.endswith('.'):
                if marker[:-1].isdigit():
                    list_level = 1
                else:
                    list_level = 2
            elif marker.endswith(')'):
                if marker[:-1].isdigit():
                    list_level = 3
                else:
                    list_level = 4
            items.append({
                'type': 'list_item',
                'level': list_level,
                'marker': marker,
                'text': text_content
            })
        else:
            items.append({
                'type': 'paragraph',
                'text': stripped
            })
    return items

def main():
    xml_path = "unpacked_ta/word/document.xml"
    if not os.path.exists(xml_path):
        print(f"Error: {xml_path} does not exist.")
        return
        
    print(f"Patching {xml_path}...")
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    
    parser = lxml.etree.XMLParser(remove_blank_text=False)
    tree = lxml.etree.parse(xml_path, parser)
    root = tree.getroot()
    body = root.find('w:body', namespaces)
    
    # 1. Search and replace simple strings in w:t nodes
    wt_replaced = 0
    for wt in root.xpath('//w:t', namespaces=namespaces):
        text = wt.text
        if not text:
            continue
            
        new_text = text
        # Replace outdated figure titles
        if "Modal Tambah Dosen" in new_text:
            new_text = new_text.replace("Modal Tambah Dosen", "Modal Tambah Data Gedung")
        if "Modal Update Dosen" in new_text:
            new_text = new_text.replace("Modal Update Dosen", "Modal Update Data Gedung")
        if "Modal Konfirmasi Hapus Dosen" in new_text:
            new_text = new_text.replace("Modal Konfirmasi Hapus Dosen", "Modal Konfirmasi Hapus Data Gedung")
            
        # Replace CRUD text
        if "seperti data dosen, fasilitas, dan aset" in new_text:
            new_text = new_text.replace("seperti data dosen, fasilitas, dan aset", "seperti data gedung, fasilitas, fakultas, dan program studi")
        if "dosen, mahasiswa, fasilitas, dan gedung" in new_text:
            new_text = new_text.replace("dosen, mahasiswa, fasilitas, dan gedung", "fasilitas, gedung, fakultas, dan program studi")
            
        # General replacements for database and schema descriptions
        if "Sistem harus dapat menyajikan data statistik kampus (dosen, mahasiswa)." in new_text:
            new_text = new_text.replace("Sistem harus dapat menyajikan data statistik kampus (dosen, mahasiswa).", "Sistem harus dapat menyajikan data statistik lalu lintas website.")
            
        if "Sistem harus menyediakan fungsionalitas CRUD (Create, Read, Update, Delete) untuk mengelola semua data konten dinamis (Dosen, Mahasiswa, Fakultas, Aset, Fasilitas, Akreditasi, dll.)." in new_text:
            new_text = new_text.replace("Sistem harus menyediakan fungsionalitas CRUD (Create, Read, Update, Delete) untuk mengelola semua data konten dinamis (Dosen, Mahasiswa, Fakultas, Aset, Fasilitas, Akreditasi, dll.).", "Sistem harus menyediakan fungsionalitas CRUD (Create, Read, Update, Delete) untuk mengelola semua data konten dinamis (Gedung, Fasilitas, Fakultas, dan Program Studi).")
            
        if "Informasi kampus seperti fasilitas, dosen, dan statistik disajikan secara dinamis melalui API." in new_text:
            new_text = new_text.replace("Informasi kampus seperti fasilitas, dosen, dan statistik disajikan secara dinamis melalui API.", "Informasi kampus seperti fasilitas, gedung, dan statistik disajikan secara dinamis melalui API.")
            
        if "Sistem menggunakan database PostgreSQL untuk menyimpan data terstruktur seperti fakultas, program studi, dosen, mahasiswa, fasilitas, dan gedung." in new_text:
            new_text = new_text.replace("Sistem menggunakan database PostgreSQL untuk menyimpan data terstruktur seperti fakultas, program studi, dosen, mahasiswa, fasilitas, dan gedung.", "Sistem menggunakan database PostgreSQL untuk menyimpan data terstruktur seperti fakultas, program studi, fasilitas, gedung, dan audit logs.")
            
        if "Struktur data akademik dibangun secara hierarkis, dimulai dari tabel fakultas yang memiliki relasi one-to-many dengan tabel program_studi. Selanjutnya, tabel program_studi menjadi entitas penghubung utama yang memiliki relasi one-to-many dengan tabel dosen dan mahasiswa, sehingga setiap data dosen dan mahasiswa terasosiasi secara langsung dengan satu program studi tertentu. Relasi antara program_studi dan akreditasi bersifat many-to-one, yang memungkinkan satu status akreditasi digunakan oleh lebih dari satu program studi sesuai dengan kondisi aktual institusi pendidikan." in new_text:
            new_text = new_text.replace("Struktur data akademik dibangun secara hierarkis, dimulai dari tabel fakultas yang memiliki relasi one-to-many dengan tabel program_studi. Selanjutnya, tabel program_studi menjadi entitas penghubung utama yang memiliki relasi one-to-many dengan tabel dosen dan mahasiswa, sehingga setiap data dosen and mahasiswa terasosiasi secara langsung dengan satu program studi tertentu. Relasi antara program_studi dan akreditasi bersifat many-to-one, yang memungkinkan satu status akreditasi digunakan oleh lebih dari satu program studi sesuai dengan kondisi aktual institusi pendidikan.", "Struktur data akademik dibangun secara hierarkis, dimulai dari tabel gedung yang memiliki relasi one-to-many dengan tabel fasilitas. Selanjutnya, tabel gedung berelasi dengan tabel fakultas, dan tabel fakultas memiliki relasi one-to-many dengan tabel program_studi (akreditasi). Hal ini menghubungkan data program studi dan fakultas dengan representasi fisik gedung secara langsung.")
            
        if "Aktor 'User' memiliki akses read-only untuk melihat berbagai data (Dosen, Mahasiswa, Akreditasi, Fasilitas) dan 'Lihat Denah Virtual'." in new_text:
            new_text = new_text.replace("Aktor 'User' memiliki akses read-only untuk melihat berbagai data (Dosen, Mahasiswa, Akreditasi, Fasilitas) dan 'Lihat Denah Virtual'.", "Aktor 'User' memiliki akses read-only untuk melihat berbagai data (Akreditasi, Fasilitas, Gedung, Statistik lalu lintas) dan 'Lihat Denah Virtual'.")

        # Replace Dosen test steps with Gedung test steps
        if "Di halaman utama admin, klik tombol \"Tambah Dosen\"." in new_text:
            new_text = new_text.replace("Di halaman utama admin, klik tombol \"Tambah Dosen\".", "Di halaman utama admin, klik tombol \"Tambah Data Gedung\".")
        if "Isi form pada modal \"Tambah Dosen\"." in new_text:
            new_text = new_text.replace("Isi form pada modal \"Tambah Dosen\".", "Isi form pada modal \"Tambah Data Gedung\".")
        if "tabel data dosen di halaman utama otomatis diperbarui" in new_text:
            new_text = new_text.replace("tabel data dosen di halaman utama otomatis diperbarui", "tabel data gedung di halaman utama otomatis diperbarui")
        if "menampilkan data dosen yang baru saja ditambahkan" in new_text:
            new_text = new_text.replace("menampilkan data dosen yang baru saja ditambahkan", "menampilkan data gedung yang baru saja ditambahkan")
        if "Di tabel data dosen, klik ikon \"Edit\"" in new_text:
            new_text = new_text.replace("Di tabel data dosen, klik ikon \"Edit\"", "Di tabel data gedung, klik ikon \"Edit\"")
        if "Modal \"Edit Dosen\" muncul" in new_text:
            new_text = new_text.replace("Modal \"Edit Dosen\" muncul", "Modal \"Edit Gedung\" muncul")
        if "data email pada tabel dosen tersebut" in new_text:
            new_text = new_text.replace("data email pada tabel dosen tersebut", "data lokasi pada tabel gedung tersebut")
        if "Di tabel data dosen, klik ikon \"Hapus\"" in new_text:
            new_text = new_text.replace("Di tabel data dosen, klik ikon \"Hapus\"", "Di tabel data gedung, klik ikon \"Hapus\"")
        if "baris data dosen tersebut hilang dari tabel" in new_text:
            new_text = new_text.replace("baris data dosen tersebut hilang dari tabel", "baris data gedung tersebut hilang dari tabel")

        # Replace Chart interaction with Asset Card interaction
        if "Klik pada salah satu bar chart (misal: bar \"Fakultas Teknik\" di chart Dosen)." in new_text:
            new_text = new_text.replace("Klik pada salah satu bar chart (misal: bar \"Fakultas Teknik\" di chart Dosen).", "Klik pada salah satu kartu aset (misal: kartu \"Laboratorium\").")
        if "Panel informasi di sisi kanan atau area lain berubah (me-render ulang state) untuk menampilkan detail data \"Fakultas Teknik\"." in new_text:
            new_text = new_text.replace("Panel informasi di sisi kanan atau area lain berubah (me-render ulang state) untuk menampilkan detail data \"Fakultas Teknik\".", "Modal daftar fasilitas terbuka untuk menampilkan daftar laboratorium.")

        # Replace drill-down tests (BB-09 and BB-10)
        if "Klik salah satu bar grafik dosen" in new_text:
            new_text = new_text.replace("Klik salah satu bar grafik dosen", "Buka halaman utama public dashboard")
        if "Detail data dosen fakultas tampil" in new_text:
            new_text = new_text.replace("Detail data dosen fakultas tampil", "Grafik tren traffic harian dan KPI total pengunjung tampil")
        if "Klik salah satu bar grafik mahasiswa" in new_text:
            new_text = new_text.replace("Klik salah satu bar grafik mahasiswa", "Klik tombol toggle bahasa (ID/EN)")
        if "Detail data mahasiswa fakultas tampil" in new_text:
            new_text = new_text.replace("Detail data mahasiswa fakultas tampil", "Seluruh teks konten berubah ke bahasa yang dipilih")
        
        # Replace SUS procedures & UAT descriptions
        if "Tolong tambahkan data dosen baru bernama X" in new_text:
            new_text = new_text.replace("Tolong tambahkan data dosen baru bernama X", "Tolong tambahkan data gedung baru bernama X")
        if "menampilkan detail dosen berdasarkan fakultas" in new_text:
            new_text = new_text.replace("menampilkan detail dosen berdasarkan fakultas", "menampilkan detail fasilitas berdasarkan kategori")
        if "POST /api/dosen" in new_text:
            new_text = new_text.replace("POST /api/dosen", "POST /api/buildings")
            
        if new_text != text:
            wt.text = new_text
            wt_replaced += 1
            
    print(f"Replaced text in {wt_replaced} w:t nodes.")
    
    # 1.5. Remove the three outdated mockup paragraphs (dosen/mahasiswa charts) from the template's XML
    mockup_start_p = None
    mockup_end_p = None
    
    for p in body.findall('w:p', namespaces):
        p_text = "".join([t.text for t in p.iter(f'{{{ns_uri}}}t') if t.text])
        if "Distribusi sumber daya akademik divisualisasikan melalui grafik batang" in p_text:
            mockup_start_p = p
        elif "Gambar 2.21 Detail Data Mahasiswa" in p_text:
            mockup_end_p = p
            
    if mockup_start_p is not None and mockup_end_p is not None:
        children_list = list(body)
        start_idx_mockup = children_list.index(mockup_start_p)
        end_idx_mockup = children_list.index(mockup_end_p)
        
        print(f"Removing mockups from index {start_idx_mockup} to {end_idx_mockup}")
        # Remove paragraphs from start_idx_mockup to end_idx_mockup inclusive
        for idx in range(end_idx_mockup, start_idx_mockup - 1, -1):
            body.remove(children_list[idx])
        print("Outdated mockup paragraphs removed.")
    else:
        print("Warning: Could not locate outdated mockup paragraphs for removal.")

    # 1.6. Replace the User Interface section narrative paragraphs directly in XML
    ui_replacements = {
        "Berikut adalah rancangan antarmuka pengguna": 
            "Berikut adalah rancangan antarmuka pengguna (user interface) dalam bentuk mockup untuk komponen frontend utama yang akan dikembangkan. Halaman antarmuka dalam sistem ini dibagi menjadi dua bagian utama, yaitu Antarmuka Dashboard Admin untuk kebutuhan manajemen data oleh administrator dan Antarmuka Public Dashboard untuk akses informasi sarana prasarana oleh pengguna umum.",
        
        "Proses awal interaksi administrator dengan sistem diawali melalui mekanisme autentikasi": 
            "Proses awal interaksi administrator dengan sistem manajemen diawali melalui mekanisme autentikasi pada Halaman Login Admin. Halaman ini menyediakan formulir input kredensial berupa nama pengguna (username) dan kata sandi (password) yang wajib diisi oleh administrator sebelum dapat mengakses dashboard administratif, sebagaimana ditunjukkan pada Gambar 2.17. Mekanisme autentikasi ini berfungsi untuk membatasi akses administratif hanya kepada pengguna yang berwenang, sehingga integritas data operasional tetap terjaga.",
        
        "Setelah autentikasi berhasil dilakukan, administrator diarahkan menuju halaman utama dashboard": 
            "Setelah proses autentikasi berhasil, administrator akan diarahkan menuju Halaman Dashboard Admin yang bertindak sebagai pusat kendali manajemen data kampus. Halaman ini menampilkan ringkasan data statistik operasional dalam bentuk widget analitik serta tabel data terperinci yang mendukung aktivitas pemantauan dan pengelolaan sarana prasarana, sebagaimana divisualisasikan pada Gambar 2.18. Tombol aksi yang tersedia pada tabel ini memungkinkan administrator untuk mengelola data secara dinamis.",
        
        "Interaksi pengelolaan data pada sistem ini dirancang menggunakan pendekatan modal-based form": 
            "Interaksi pengelolaan data pada sistem ini dirancang menggunakan pendekatan formulir berbasis modal (modal-based form) untuk menjaga fokus administrator tanpa harus berpindah halaman. Ketika administrator menambahkan data gedung baru, sistem menampilkan modal popup formulir input sebagaimana ditunjukkan pada Gambar 2.19. Pola interaksi serupa diterapkan ketika administrator memperbarui data gedung, di mana data lama akan otomatis dimuat ke dalam kolom input modal, sebagaimana divisualisasikan pada Gambar 2.20.",
        
        "Untuk mencegah terjadinya penghapusan data secara tidak disengaja": 
            "Untuk mencegah terjadinya penghapusan data secara tidak sengaja, sistem menerapkan mekanisme konfirmasi sebelum eksekusi aksi hapus dilakukan. Mekanisme ini direalisasikan melalui modal konfirmasi yang meminta persetujuan eksplisit dari administrator, sebagaimana diperlihatkan pada Gambar 2.21. Aksi penghapusan data pada database hanya akan dijalankan apabila administrator menekan tombol konfirmasi hapus secara sadar.",
        
        "Pemantauan lalu lintas penggunaan sistem pada sisi administratif dirancang": 
            "Pemantauan lalu lintas penggunaan sistem pada sisi administratif dirancang untuk menyajikan analisis kunjungan secara mendalam. Modul traffic website pada Dashboard Admin menyajikan informasi agregat mengenai aktivitas penggunaan internal, mencakup total kunjungan, frekuensi akses halaman, serta detail sistem operasi dan peramban yang digunakan untuk mengakses sistem, sebagaimana ditunjukkan pada Gambar 2.22.",
        
        "Sedikit berbeda dengan modul public traffic": 
            "Metrik pemantauan lalu lintas pada Dashboard Admin ini memiliki cakupan yang lebih lengkap dibandingkan dengan Dashboard Publik. Klasifikasi tipe perangkat yang digunakan oleh pengguna (seperti desktop, tablet, dan mobile) ditampilkan secara detail untuk memberikan gambaran komprehensif mengenai pola kerja administrator dalam mengelola konten sistem.",
        
        "Keberadaan detail perangkat pada admin traffic": 
            "Analisis perangkat pada halaman admin traffic ini memiliki peran penting untuk mengevaluasi aspek keamanan dan kegunaan (usability) sistem. Dengan mengetahui peramban dan sistem operasi yang digunakan oleh administrator, pengelola sistem dapat mengoptimalkan tata letak antarmuka serta mengidentifikasi jika terjadi akses tidak wajar dari perangkat yang tidak dikenal.",
        
        "Bagian awal antarmuka public dashboard dirancang sebagai hero section": 
            "Bagian awal antarmuka public dashboard dirancang sebagai Hero Section yang menjadi titik orientasi visual utama bagi pengunjung. Area ini memuat identitas sistem, navigasi utama, tombol akses ke login admin, serta tombol toggle bahasa (Bahasa Indonesia dan English) untuk memfasilitasi aksesibilitas bagi pengguna internasional, sebagaimana diperlihatkan pada Gambar 2.23. Penyediaan fitur multi-bahasa ini bertujuan untuk mempermudah pengguna asing dalam memahami konten navigasi.",
        
        "Pemantauan aktivitas pengguna pada public dashboard dirancang": 
            "Metrik pemantauan lalu lintas pada halaman publik dirancang untuk menyajikan statistik kunjungan dasar secara transparan. Modul ini menampilkan visualisasi grafik garis tren kunjungan harian selama 14 hari terakhir serta empat kartu indikator kinerja utama (Key Performance Indicator/KPI) yang mencakup total pengunjung, total tampilan halaman, rata-rata pengunjung harian, dan rata-rata tampilan halaman, sebagaimana ditunjukkan pada Gambar 2.24.",
        
        "Informasi mengenai fasilitas dan aset kampus disajikan dengan tata letak berbasis kartu": 
            "Informasi mengenai sarana prasarana kampus disajikan dengan tata letak berbasis kartu (card-based layout) yang mengelompokkan data ke dalam 8 kategori utama aset dan fasilitas. Sistem juga dilengkapi dengan fitur pencarian gabungan (Search Overlay) di bagian atas untuk memudahkan penemuan nama gedung atau fasilitas secara langsung dari seluruh kategori yang tersedia, sebagaimana diperlihatkan pada Gambar 2.25.",
        
        "Ketika pengguna mengeklik salah satu kartu kategori": 
            "Ketika pengguna memilih salah satu kartu kategori sarana prasarana, sistem akan memicu jendela popup dinamis. Modal popup ini menyajikan daftar item terstruktur yang sesuai dengan kategori yang dipilih oleh pengguna tanpa memuat ulang halaman utama, sebagaimana ditunjukkan pada Gambar 2.26. Pola interaksi ini mendukung penelusuran informasi yang lebih terfokus.",
        
        "Ketika pengguna memilih salah satu kartu pada bagian fasilitas": 
            "Ketika pengguna memilih salah satu kartu kategori sarana prasarana, sistem akan memicu jendela popup dinamis. Modal popup ini menyajikan daftar item terstruktur yang sesuai dengan kategori yang dipilih oleh pengguna tanpa memuat ulang halaman utama, sebagaimana ditunjukkan pada Gambar 2.26. Pola interaksi ini mendukung penelusuran informasi yang lebih terfokus.",
        
        "Untuk fasilitas yang dikategorikan sebagai unggulan": 
            "Sistem menyediakan modal detail dengan struktur informasi berbeda yang disesuaikan secara otomatis berdasarkan jenis entitas yang dipilih oleh pengguna. Ketika pengguna mengeklik item bertipe gedung, modal detail menampilkan deskripsi gedung, foto fisik, lokasi kampus, serta daftar lengkap fasilitas yang ada di dalam gedung tersebut. Sementara itu, untuk item bertipe fasilitas, modal detail hanya menampilkan deskripsi spesifik dan lokasinya saja, sebagaimana ditunjukkan pada Gambar 2.27.",
        
        "Sebagai penutup halaman, sistem menyediakan bagian footer": 
            "Sebagai penutup halaman dan pusat navigasi pelengkap, sistem menyediakan Bagian Footer di area paling bawah halaman. Footer ini memuat tautan navigasi cepat, jam operasional layanan, informasi kontak institusi, serta widget peta interaktif Google Maps yang memvisualisasikan lokasi fisik Kampus Pondok Labu UPNVJ secara langsung, sebagaimana diperlihatkan pada Gambar 2.28. Keberadaan footer ini mempermudah pengguna dalam mengakses informasi kontak resmi serta menemukan rute lokasi fisik kampus.",
        
        "Perancangan antarmuka pengguna pada Admin Dashboard dan Public Dashboard tidak hanya berfokus pada aspek visual": 
            "Perancangan antarmuka pengguna pada Admin Dashboard dan Public Dashboard dirancang dengan mengutamakan aspek konsistensi elemen visual dan kemudahan penggunaan (usability). Desain antarmuka yang dinamis ini diharapkan dapat mempermudah pengguna dalam memperoleh informasi spasial secara mandiri. Rancangan antarmuka ini selanjutnya menjadi acuan dalam penyusunan skenario pengujian fungsional dan pengujian penerimaan pengguna pada tahap evaluasi sistem."
    }

    replaced_ui_count = 0
    for p in body.findall('w:p', namespaces):
        p_text = "".join([t.text for t in p.iter(f'{{{ns_uri}}}t') if t.text])
        for match_key, new_val in ui_replacements.items():
            if match_key in p_text:
                # Clear runs and insert new one
                pPr = p.find('w:pPr', namespaces)
                for child in list(p):
                    if child != pPr:
                        p.remove(child)
                r = lxml.etree.SubElement(p, f'{{{ns_uri}}}r')
                rPr = lxml.etree.SubElement(r, f'{{{ns_uri}}}rPr')
                lxml.etree.SubElement(rPr, f'{{{ns_uri}}}rFonts', {
                    f'{{{ns_uri}}}ascii': 'Times New Roman',
                    f'{{{ns_uri}}}hAnsi': 'Times New Roman'
                })
                lxml.etree.SubElement(rPr, f'{{{ns_uri}}}sz', {f'{{{ns_uri}}}val': '24'})
                lxml.etree.SubElement(rPr, f'{{{ns_uri}}}szCs', {f'{{{ns_uri}}}val': '24'})
                t = lxml.etree.SubElement(r, f'{{{ns_uri}}}t')
                t.text = new_val
                t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                replaced_ui_count += 1
                break

    print(f"Replaced {replaced_ui_count} UI narrative paragraphs directly in XML.")
    
    # 2. Replace the ERD section description paragraphs
    # Find start and end paragraph indices
    children = list(body)
    start_idx = -1
    end_idx = -1
    
    for idx, p in enumerate(children):
        if p.tag == f'{{{ns_uri}}}p':
            p_text = "".join([t.text for t in p.iter(f'{{{ns_uri}}}t') if t.text])
            if "Rancangan basis data pada sistem ini terdiri dari sembilan tabel utama" in p_text:
                start_idx = idx
            elif "2.3.4.2 Rancangan Fungsional Use Case Diagram" in p_text:
                end_idx = idx
                break
                
    if start_idx != -1 and end_idx != -1:
        print(f"Found ERD section to replace: from index {start_idx} to {end_idx}.")
        
        # Remove old paragraphs
        for idx in range(end_idx - 1, start_idx - 1, -1):
            body.remove(children[idx])
            print(f"Removed old paragraph at index {idx}.")
            
        # Parse new ERD markdown and build elements
        parsed_items = parse_markdown_string(new_erd_markdown)
        new_elements = []
        for item in parsed_items:
            p_elem = build_p_element(item)
            new_elements.append(p_elem)
            
        # Insert new elements at start_idx
        for elem in reversed(new_elements):
            body.insert(start_idx, elem)
            
        print(f"Inserted {len(new_elements)} new detailed ERD paragraphs.")
    else:
        print("Warning: Could not locate ERD section paragraphs in document.xml.")
        
    tree.write(xml_path, encoding='utf-8', xml_declaration=True)
    print("SUCCESS: document.xml patched and saved.")
    
    # Copy new screenshots over the old mockup images in word/media
    media_dir = "unpacked_ta/word/media"
    replacements = {
        "login-page.png": "image20.png",
        "header+gedung-view.png": "image21.png",
        "modal-create-gedung.png": "image22.png",
        "modal-edit-gedung.png": "image23.png",
        "modal-konfirmasi-delete-gedung.png": "image24.png",
        "section-admin-traffic-view.png": "image25.png",
        "section-header+hero.png": "image26.png",
        "traffic-web-public.png": "image27.png",
        "section fasilitas-asset(dan gedung).png": "image28.png",
        "modal-fasilitas-aset.png": "image29.png",
        "modal-detail-gedung.png": "image30.png",
        "section-footer.png": "image31.png",
        "erd_schema.png": "image15.png",
        "ttd pakta integritas UPA TIK.jpeg": "image10.jpg",
        "wawancara warek 2.jpeg": "image11.jpg",
        "contoh_pointer.png": "image32.png",
        "contoh_sync_db.png": "image33.png"
    }
    
    print("Replacing mockup image files with real screenshots...")
    for src_name, dest_name in replacements.items():
        src_path = os.path.join("dokumentasi", src_name)
        dest_path = os.path.join(media_dir, dest_name)
        if os.path.exists(src_path):
            shutil.copy2(src_path, dest_path)
            print(f"  Replaced {dest_name} with {src_name}")
        else:
            print(f"  Warning: Screenshot not found: {src_path}")

if __name__ == '__main__':
    main()
