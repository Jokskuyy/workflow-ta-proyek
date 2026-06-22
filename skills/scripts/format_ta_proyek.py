import lxml.etree
import os
import re
import sys

# Tabel angka Romawi untuk Nomor_Bab (I=1 .. X=10).
ROMAN = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5,
    "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10,
}

# Pola heading BAB: 'BAB' diikuti angka Romawi atau Arab, dengan batas kata.
_BAB_PATTERN = re.compile(r"^BAB\s+([IVX]+|[0-9]+)\b", re.IGNORECASE)


def parse_chapter_number(heading_text):
    """Ambil Nomor_Bab dari teks heading BAB sebagai fungsi murni.

    Mendukung 'BAB II', 'BAB 2', 'BAB II RANCANGAN PROYEK', case-insensitive,
    dengan spasi ternormalisasi (mis. '  bab   iii  '). Mengembalikan int bila
    teks merupakan heading BAB, atau None bila bukan.

    Aturan: cocokkan ^BAB\\s+([IVX]+|[0-9]+)\\b; angka Romawi dipetakan via
    tabel ROMAN, angka Arab via int().
    """
    if not heading_text:
        return None
    # Normalisasi spasi: ringkas whitespace berturut menjadi satu spasi, trim.
    normalized = re.sub(r"\s+", " ", str(heading_text)).strip()
    if not normalized:
        return None
    m = _BAB_PATTERN.match(normalized)
    if not m:
        return None
    token = m.group(1)
    if token.isdigit():
        return int(token)
    roman = token.upper()
    return ROMAN.get(roman)


class _Ambiguous:
    """Penanda (sentinel) untuk nomor lama yang memetakan ke >1 nomor baru.

    Konvensi nilai remap (dipakai oleh task 5.1 `rewrite_references`):
      - Kunci peta (`fig_remap`/`tbl_remap`) selalu berupa string nomor lama
        "C.Y" (mis. "2.5") yang terbaca dari teks kapsi sumber draf.
      - Bila satu nomor lama hanya pernah memetakan ke SATU nomor baru, nilainya
        berupa string nomor baru "C.k" (mis. "2.7"). `rewrite_references` boleh
        mengganti referensi secara langsung.
      - Bila satu nomor lama memetakan ke LEBIH DARI SATU nomor baru yang
        berbeda (mis. dua kapsi "Gambar 2.5" akibat penyuntingan), nilainya
        diganti dengan instance `_Ambiguous` yang menyimpan `frozenset` seluruh
        nomor baru kandidat pada atribut `candidates`. `rewrite_references`
        WAJIB mendeteksi ini (via `is_ambiguous(value)`), mempertahankan teks
        asli, dan mencatat peringatan berisi daftar kandidat.
    """

    __slots__ = ("candidates",)

    def __init__(self, candidates):
        # Simpan sebagai frozenset agar nilai bersifat hashable & immutable.
        self.candidates = frozenset(candidates)

    def __repr__(self):
        return "AMBIGUOUS(%s)" % sorted(self.candidates)

    def __eq__(self, other):
        return isinstance(other, _Ambiguous) and self.candidates == other.candidates

    def __hash__(self):
        return hash(("_Ambiguous", self.candidates))


def is_ambiguous(value):
    """True bila nilai remap menandakan nomor lama yang ambigu (>1 nomor baru)."""
    return isinstance(value, _Ambiguous)


# Sentinel marker tingkat-modul. Nilai remap yang merupakan instance `_Ambiguous`
# menandai nomor lama yang memetakan ke lebih dari satu nomor baru (R6.5).
AMBIGUOUS = _Ambiguous


class CaptionRegistry:
    """Menomori kapsi gambar & tabel per-bab dan merekam pemetaan nomor lama->baru.

    Registri ini adalah sumber kebenaran tunggal untuk penomoran kapsi (R1, R2)
    sekaligus menyediakan peta renumbering referensi silang (R6.3). Logika murni
    tanpa efek samping XML sehingga dapat diuji langsung (property-based testing).

    Atribut:
      _fig_seq / _tbl_seq: dict[int,int] penghitung gambar/tabel berjalan per-bab.
      fig_remap / tbl_remap: dict[str, str | _Ambiguous] pemetaan nomor lama "C.Y"
        -> nomor baru "C.k"; bernilai instance `_Ambiguous` bila satu nomor lama
        memetakan ke >1 nomor baru (lihat konvensi pada docstring `_Ambiguous`).
      fig_numbers / tbl_numbers: set[str] himpunan nomor final ("C.k") untuk
        pengecekan "punya padanan?" (R6.4).
    """

    def __init__(self):
        self._fig_seq = {}      # bab -> seq gambar berjalan
        self._tbl_seq = {}      # bab -> seq tabel berjalan
        self.fig_remap = {}     # "2.5" -> "2.7" | _Ambiguous
        self.tbl_remap = {}
        self.fig_numbers = set()
        self.tbl_numbers = set()

    @staticmethod
    def _record_remap(remap, old_number, new_number):
        """Catat old_number -> new_number, tandai AMBIGUOUS bila berbeda padanan."""
        if old_number is None:
            return
        existing = remap.get(old_number)
        if existing is None:
            remap[old_number] = new_number
            return
        if is_ambiguous(existing):
            # Sudah ambigu: tambahkan kandidat baru ke himpunan.
            remap[old_number] = _Ambiguous(existing.candidates | {new_number})
            return
        if existing == new_number:
            # Padanan identik berulang: tetap unik, tidak ada perubahan.
            return
        # Dua padanan berbeda untuk satu nomor lama -> tandai ambigu.
        remap[old_number] = _Ambiguous({existing, new_number})

    def _next(self, seq, remap, numbers, chapter, old_number):
        k = seq.get(chapter, 0) + 1
        seq[chapter] = k
        new_number = "%d.%d" % (chapter, k)
        is_first_in_chapter = (k == 1)
        self._record_remap(remap, old_number, new_number)
        numbers.add(new_number)
        return new_number, k, is_first_in_chapter

    def next_figure(self, chapter, old_number):
        """Kembalikan (nomor_baru 'C.k', default_val=k, is_first_in_chapter).

        Menaikkan penghitung gambar per-bab (`_fig_seq[chapter]`); k dimulai dari
        1 di tiap bab dan bertambah tepat 1. `is_first_in_chapter` True bila k==1
        (memicu opsi restart SEQ `\\r 1`, R1.4/R1.5). `default_val` sama dengan k.
        Mencatat `old_number -> nomor_baru` ke `fig_remap` (menandai AMBIGUOUS
        bila perlu) dan menambah nomor baru ke `fig_numbers`.
        """
        return self._next(
            self._fig_seq, self.fig_remap, self.fig_numbers, chapter, old_number
        )

    def next_table(self, chapter, old_number):
        """Analog `next_figure` untuk tabel (R2.2-R2.5) memakai `_tbl_seq`,
        `tbl_remap`, dan `tbl_numbers`."""
        return self._next(
            self._tbl_seq, self.tbl_remap, self.tbl_numbers, chapter, old_number
        )


# ---------------------------------------------------------------------------
# Helper murni: ekstraksi teks/gaya paragraf lxml (dipakai task 3.1, 4.1).
# ---------------------------------------------------------------------------

def _paragraph_text(p, ns):
    """Gabungkan seluruh teks (`w:t`) di dalam paragraf lxml `p` menjadi satu
    string (urutan baca). `ns` adalah dict namespace konsisten dengan kode
    eksisting, mis. {'w': ns_uri}."""
    ns_uri = ns['w']
    return "".join(t.text for t in p.iter('{%s}t' % ns_uri) if t.text)


def _paragraph_style(p, ns):
    """Kembalikan nilai `w:pStyle/@w:val` paragraf `p`, atau None bila tak ada."""
    ns_uri = ns['w']
    pPr = p.find('w:pPr', ns)
    if pPr is None:
        return None
    pStyle = pPr.find('w:pStyle', ns)
    if pStyle is None:
        return None
    return pStyle.get('{%s}val' % ns_uri)


# ---------------------------------------------------------------------------
# Task 3.1 (R3.1-3.5): parse teks kapsi draf -> (label, old_number, desc).
# ---------------------------------------------------------------------------

# Pola kapsi: 'Gambar'/'Tabel' diikuti nomor 'C' atau 'C.Y[.Z...]' lalu deskripsi.
# Titik opsional setelah nomor (mis. 'Gambar 3.1.' atau 'Gambar 3.1'), lalu
# deskripsi VERBATIM sebagai trailing text.
_CAPTION_TEXT_PATTERN = re.compile(
    r"^(Gambar|Tabel)\s+([0-9]+(?:\.[0-9]+)*)\.?\s*(.*)$", re.IGNORECASE
)


def parse_caption_text(text):
    """Parse satu paragraf kapsi draf menjadi `(label, old_number, desc)`.

    Mengembalikan tuple `("Gambar"|"Tabel", "C.Y", deskripsi_verbatim)` bila
    `text` adalah kapsi, atau `None` bila bukan kapsi (R3.1, R3.5). `desc`
    diambil verbatim dari trailing description draf (tanpa label & nomor),
    sehingga mengubah deskripsi di draf mengubah keluaran tanpa perubahan kode.

    Contoh:
        parse_caption_text("Gambar 3.1 Hierarki Prefab")
            -> ("Gambar", "3.1", "Hierarki Prefab")
        parse_caption_text("Paragraf narasi biasa") -> None

    Helper ini adalah basis untuk menyumber deskripsi kapsi dari draf dan
    Aturan_Umum gambar tanpa kapsi; penghapusan `survey_captions`/pemicu
    judul-seksi bernama dilakukan pada task integrasi 7.2.
    """
    if not text:
        return None
    s = str(text).strip()
    if not s:
        return None
    m = _CAPTION_TEXT_PATTERN.match(s)
    if not m:
        return None
    label = "Gambar" if m.group(1).lower() == "gambar" else "Tabel"
    old_number = m.group(2)
    desc = m.group(3)
    return (label, old_number, desc)


# ---------------------------------------------------------------------------
# Task 4.1 (R5.1-5.5): deteksi seksi & heading dinamis (tanpa indeks tetap).
# ---------------------------------------------------------------------------

# Petunjuk teks heading front matter, dipakai HANYA untuk fallback struktural
# batas front matter bila heading 'BAB I'/'PENDAHULUAN' tidak ditemukan (R5.5).
_FRONT_MATTER_HEADING_HINTS = (
    "DAFTAR", "KATA PENGANTAR", "ABSTRAK", "ABSTRACT", "LEMBAR", "HALAMAN",
    "PERNYATAAN", "MOTTO", "PERSEMBAHAN", "RINGKASAN",
)


def find_front_matter_boundary(children, ns):
    """Kembalikan indeks paragraf Heading1 BAB I pertama.

    BAB I dikenali bila teks heading (gaya 'Heading1') memuat 'PENDAHULUAN'
    atau `parse_chapter_number(text) == 1` (mencakup 'BAB I'/'BAB 1'), R5.1/R5.2.

    Fallback (R5.3/R5.5): bila tidak ditemukan, kembalikan akhir front matter
    terdeteksi secara struktural (indeks tepat setelah heading front-matter
    terakhir; bila tak ada heading front-matter, `len(children)`), dan catat
    tepat satu peringatan. Tidak memakai indeks numerik tetap.
    """
    last_front_matter_idx = -1
    for idx, p in enumerate(children):
        if _paragraph_style(p, ns) != 'Heading1':
            continue
        text_norm = re.sub(r"\s+", " ", _paragraph_text(p, ns)).strip()
        upper = text_norm.upper()
        if 'PENDAHULUAN' in upper or parse_chapter_number(text_norm) == 1:
            return idx
        if any(hint in upper for hint in _FRONT_MATTER_HEADING_HINTS):
            last_front_matter_idx = idx
    boundary = last_front_matter_idx + 1 if last_front_matter_idx != -1 else len(children)
    print(
        "  [WARNING] find_front_matter_boundary: heading 'BAB I'/'PENDAHULUAN' "
        "tidak ditemukan; memakai fallback struktural index %d" % boundary
    )
    return boundary


def find_heading(children, ns, *, style=None, text_contains=None):
    """Pemindaian awal->akhir; kembalikan indeks heading pertama yang cocok.

    - `style`: bila diberikan, paragraf wajib ber-`pStyle` sama (case-insensitive).
    - `text_contains`: bila diberikan, teks paragraf (ternormalisasi spasi, trim,
      case-insensitive) wajib memuat substring ini.
    Mengembalikan -1 bila tak ada yang cocok, atau bila tidak ada kriteria yang
    diberikan (`style` dan `text_contains` keduanya None).
    """
    if style is None and text_contains is None:
        return -1
    target = re.sub(r"\s+", " ", text_contains).strip().lower() if text_contains else None
    for idx, p in enumerate(children):
        if style is not None:
            p_style = _paragraph_style(p, ns)
            if p_style is None or p_style.lower() != style.lower():
                continue
        if target is not None:
            txt = re.sub(r"\s+", " ", _paragraph_text(p, ns)).strip().lower()
            if target not in txt:
                continue
        return idx
    return -1


# ---------------------------------------------------------------------------
# Task 5.1 (R6.1-6.5): reference rewriter dari registri kapsi.
# ---------------------------------------------------------------------------

# Penyebutan referensi silang 'Gambar X.Y' / 'Tabel X.Y' pada narasi.
_REFERENCE_PATTERN = re.compile(
    r"\b(Gambar|Tabel)\s+([0-9]+(?:\.[0-9]+)*)\b", re.IGNORECASE
)


def rewrite_references(text, fig_remap, tbl_remap):
    """Tulis ulang semua 'Gambar X.Y' / 'Tabel X.Y' pada `text` memakai peta
    yang DITURUNKAN dari `CaptionRegistry` (`fig_remap`/`tbl_remap`), R6.1-R6.3.

    Per kemunculan:
      - padanan unik (nilai berupa string 'C.k') -> ganti ke nomor baru pada
        SEMUA kemunculan, termasuk yang berulang (R6.1, R6.3).
      - tanpa padanan di peta -> pertahankan teks asli + tambahkan peringatan
        yang menyebut teks referensi & nomornya (R6.4).
      - ambigu (`is_ambiguous(value)` True; nilai instance AMBIGUOUS dengan
        atribut `.candidates`) -> pertahankan teks asli + peringatan berisi
        daftar nomor kandidat (R6.5).

    Mengembalikan `(new_text, warnings)`; `warnings` adalah list[str].
    """
    warnings = []
    if not text:
        return text, warnings

    def _repl(m):
        label_raw = m.group(1)
        old_number = m.group(2)
        is_fig = label_raw.lower() == "gambar"
        label = "Gambar" if is_fig else "Tabel"
        remap = fig_remap if is_fig else tbl_remap
        original = m.group(0)
        if not remap or old_number not in remap:
            warnings.append(
                "Referensi '%s %s' tidak memiliki padanan kapsi; teks dipertahankan."
                % (label, old_number)
            )
            return original
        target = remap[old_number]
        if is_ambiguous(target):
            candidates = ", ".join(sorted(target.candidates))
            warnings.append(
                "Referensi '%s %s' ambigu (kandidat: %s); teks dipertahankan."
                % (label, old_number, candidates)
            )
            return original
        return "%s %s" % (label, target)

    new_text = _REFERENCE_PATTERN.sub(_repl, text)
    return new_text, warnings


# Official element order from OOXML schemas
PPR_ORDER = [
    'pStyle', 'keepNext', 'keepLines', 'pageBreakBefore', 'framePr', 
    'widowControl', 'numPr', 'suppressLineNumbers', 'pBdr', 'shd', 
    'tabs', 'suppressAutoHyphens', 'kinsoku', 'wordWrap', 'overflowPunct', 
    'topLinePunct', 'autoSpaceDE', 'autoSpaceDN', 'bidi', 'adjustRightInd', 
    'snapToGrid', 'spacing', 'ind', 'contextualSpacing', 'mirrorIndents', 
    'suppressOverlap', 'jc', 'textDirection', 'textAlignment', 'textboxTightWrap', 
    'outlineLvl', 'divId', 'cnfStyle', 'rPr', 'sectPr', 'pPrChange'
]

STYLE_ORDER = [
    'name', 'aliases', 'basedOn', 'next', 'link', 'autoRedefine', 'hidden', 
    'uiPriority', 'semiHidden', 'unhideWhenUsed', 'qFormat', 'locked', 
    'personal', 'personalCompose', 'personalReply', 'rsid', 'pPr', 'rPr', 
    'tblPr', 'trPr', 'tcPr', 'tblStylePr'
]

SECTPR_ORDER = [
    'headerReference', 'footerReference', 'footnotePr', 'endnotePr', 'type',
    'pgSz', 'pgMar', 'paperSrc', 'pgBorders', 'lnNumType', 'pgNumType',
    'cols', 'formProt', 'vAlign', 'noEndnote', 'titlePg', 'textDirection',
    'bidi', 'rtlGutter', 'docGrid', 'printerSettings', 'sectPrChange'
]

def sort_element_children(parent, order_list):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    def key_func(child):
        tag = child.tag
        local_name = tag[len(f'{{{ns_uri}}}'):] if tag.startswith(f'{{{ns_uri}}}') else tag.split('}')[-1]
        return order_list.index(local_name) if local_name in order_list else len(order_list)
        
    children = list(parent)
    for child in children: parent.remove(child)
    children.sort(key=key_func)
    for child in children: parent.append(child)

def set_child_element(parent, tag_name, attribs=None):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    ns_tag = f'{{{ns_uri}}}{tag_name}'
    elem = parent.find(ns_tag)
    if elem is None:
        elem = lxml.etree.Element(ns_tag)
        parent.append(elem)
    if attribs is not None:
        for k, v in attribs.items():
            if k == 'space': elem.set('{http://www.w3.org/XML/1998/namespace}space', v)
            elif k.startswith('{'): elem.set(k, str(v))
            else: elem.set(f'{{{ns_uri}}}{k}', str(v))
    return elem

def fix_whitespace_preservation(root):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    xml_ns = 'http://www.w3.org/XML/1998/namespace'
    for t_elem in root.iter(f'{{{ns_uri}}}t'):
        text = t_elem.text
        if text and (text.startswith(' ') or text.endswith(' ') or '\xa0' in text):
            t_elem.set(f'{{{xml_ns}}}space', 'preserve')

def ensure_front_matter_heading_style(styles_root):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    style = styles_root.find("w:style[@w:styleId='FrontMatterHeading']", namespaces)
    if style is None:
        style = lxml.etree.Element(f'{{{ns_uri}}}style')
        style.set(f'{{{ns_uri}}}type', 'paragraph')
        style.set(f'{{{ns_uri}}}styleId', 'FrontMatterHeading')
        set_child_element(style, 'name', {'val': 'front matter heading'})
        set_child_element(style, 'basedOn', {'val': 'Normal'})
        set_child_element(style, 'next', {'val': 'Normal'})
        set_child_element(style, 'qFormat', {})
        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
        set_child_element(pPr, 'keepNext', {})
        set_child_element(pPr, 'keepLines', {})
        set_child_element(pPr, 'spacing', {'before': '480', 'after': '240'})
        set_child_element(pPr, 'jc', {'val': 'center'})
        set_child_element(pPr, 'outlineLvl', {'val': '0'})
        sort_element_children(pPr, PPR_ORDER)
        style.append(pPr)
        rPr = lxml.etree.Element(f'{{{ns_uri}}}rPr')
        set_child_element(rPr, 'rFonts', {'ascii': 'Times New Roman', 'hAnsi': 'Times New Roman'})
        set_child_element(rPr, 'b', {})
        set_child_element(rPr, 'bCs', {})
        set_child_element(rPr, 'sz', {'val': '28'})
        set_child_element(rPr, 'szCs', {'val': '28'})
        style.append(rPr)
        sort_element_children(style, STYLE_ORDER)
        styles_root.append(style)

def ensure_appendix_heading_style(styles_root):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    style = styles_root.find("w:style[@w:styleId='taappendixheading']", namespaces)
    if style is None:
        style = lxml.etree.Element(f'{{{ns_uri}}}style')
        style.set(f'{{{ns_uri}}}type', 'paragraph')
        style.set(f'{{{ns_uri}}}styleId', 'taappendixheading')
        set_child_element(style, 'name', {'val': 'taappendixheading'})
        set_child_element(style, 'basedOn', {'val': 'Normal'})
        set_child_element(style, 'next', {'val': 'Normal'})
        set_child_element(style, 'qFormat', {})
        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
        set_child_element(pPr, 'keepNext', {})
        set_child_element(pPr, 'keepLines', {})
        set_child_element(pPr, 'pageBreakBefore', {})
        set_child_element(pPr, 'spacing', {'before': '240', 'after': '120'})
        set_child_element(pPr, 'jc', {'val': 'center'})
        set_child_element(pPr, 'outlineLvl', {'val': '8'})
        sort_element_children(pPr, PPR_ORDER)
        style.append(pPr)
        rPr = lxml.etree.Element(f'{{{ns_uri}}}rPr')
        set_child_element(rPr, 'rFonts', {'ascii': 'Times New Roman', 'hAnsi': 'Times New Roman'})
        set_child_element(rPr, 'b', {})
        set_child_element(rPr, 'bCs', {})
        set_child_element(rPr, 'sz', {'val': '28'})
        set_child_element(rPr, 'szCs', {'val': '28'})
        style.append(rPr)
        sort_element_children(style, STYLE_ORDER)
        styles_root.append(style)
        print("Successfully defined taappendixheading style in styles.xml")

def ensure_toc9_style(styles_root):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    style = styles_root.find("w:style[@w:styleId='TOC9']", namespaces)
    if style is None:
        style = lxml.etree.Element(f'{{{ns_uri}}}style')
        style.set(f'{{{ns_uri}}}type', 'paragraph')
        style.set(f'{{{ns_uri}}}styleId', 'TOC9')
        set_child_element(style, 'name', {'val': 'toc 9'})
        set_child_element(style, 'basedOn', {'val': 'Normal'})
        set_child_element(style, 'next', {'val': 'Normal'})
        set_child_element(style, 'qFormat', {})
        styles_root.append(style)
        
    pPr = style.find('w:pPr', namespaces)
    if pPr is None:
        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
        style.append(pPr)
    
    set_child_element(pPr, 'spacing', {'before': '0', 'after': '0', 'line': '360', 'lineRule': 'auto'})
    set_child_element(pPr, 'ind', {'left': '1'})
    set_child_element(pPr, 'jc', {'val': 'left'})
    sort_element_children(pPr, PPR_ORDER)
    
    rPr = style.find('w:rPr', namespaces)
    if rPr is None:
        rPr = lxml.etree.Element(f'{{{ns_uri}}}rPr')
        style.append(rPr)
        
    set_child_element(rPr, 'rFonts', {'ascii': 'Times New Roman', 'hAnsi': 'Times New Roman'})
    set_child_element(rPr, 'sz', {'val': '24'})
    set_child_element(rPr, 'szCs', {'val': '24'})
    
    # Remove any bold/italic elements to keep the text plain
    for tag in ['b', 'bCs', 'i', 'iCs']:
        elem = rPr.find(f'w:{tag}', namespaces)
        if elem is not None:
            rPr.remove(elem)
            
    sort_element_children(style, STYLE_ORDER)
    print("Successfully defined or updated TOC9 style in styles.xml")

def ensure_hyperlink_style(styles_root):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    STYLE_ORDER = [
        'name', 'aliases', 'basedOn', 'next', 'link', 'autoRedefine', 'hidden', 
        'uiPriority', 'semiHidden', 'unhideWhenUsed', 'qFormat', 'locked', 
        'personal', 'personalCompose', 'personalReply', 'rsid', 'pPr', 'rPr', 
        'tblPr', 'trPr', 'tcPr', 'tblStylePr'
    ]
    style = styles_root.find("w:style[@w:styleId='Hyperlink']", namespaces)
    if style is None:
        style = lxml.etree.Element(f'{{{ns_uri}}}style')
        style.set(f'{{{ns_uri}}}type', 'character')
        style.set(f'{{{ns_uri}}}styleId', 'Hyperlink')
        set_child_element(style, 'name', {'val': 'Hyperlink'})
        set_child_element(style, 'basedOn', {'val': 'DefaultParagraphFont'})
        set_child_element(style, 'uiPriority', {'val': '99'})
        set_child_element(style, 'unhideWhenUsed', {})
        
        rPr = lxml.etree.Element(f'{{{ns_uri}}}rPr')
        set_child_element(rPr, 'color', {'val': '000000', 'themeColor': 'text1'})
        set_child_element(rPr, 'u', {'val': 'none'})
        style.append(rPr)
        
        sort_element_children(style, STYLE_ORDER)
        styles_root.append(style)
    else:
        rPr = style.find('w:rPr', namespaces)
        if rPr is None:
            rPr = lxml.etree.Element(f'{{{ns_uri}}}rPr')
            style.append(rPr)
        set_child_element(rPr, 'color', {'val': '000000', 'themeColor': 'text1'})
        set_child_element(rPr, 'u', {'val': 'none'})


def clean_heading_text_and_add_num(p, level, num_id):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    text = "".join([t.text for t in p.iter(f'{{{ns_uri}}}t') if t.text])
    
    # Strip manual numbering pattern
    pattern = None
    if level == 0: pattern = r'^BAB\s+[IVX0-9]+(?:\.|\s+)?\s*'
    elif level == 1: pattern = r'^[0-9]+\.[0-9]+(?:\.|\s+)?\s*'
    elif level == 2: pattern = r'^[0-9]+\.[0-9]+\.[0-9]+(?:\.|\s+)?\s*'
    elif level == 3: pattern = r'^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(?:\.|\s+)?\s*'
    
    cleaned_text = text
    if pattern:
        cleaned_text = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
        print(f"  Stripped heading level {level}: '{text}' -> '{cleaned_text}'")
        
    for r in p.findall(f'{{{ns_uri}}}r', namespaces):
        p.remove(r)
        
    new_r = lxml.etree.Element(f'{{{ns_uri}}}r')
    new_t = lxml.etree.Element(f'{{{ns_uri}}}t')
    new_t.text = cleaned_text
    if cleaned_text.startswith(' ') or cleaned_text.endswith(' '):
        new_t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    new_r.append(new_t)
    p.append(new_r)
    
    pPr = p.find(f'{{{ns_uri}}}pPr', namespaces)
    if pPr is None:
        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
        p.insert(0, pPr)
        
    numPr = set_child_element(pPr, 'numPr')
    set_child_element(numPr, 'ilvl', {'val': str(level)})
    set_child_element(numPr, 'numId', {'val': str(num_id)})
    
    # Direct formatting override to ensure headings are left-aligned with no indent
    set_child_element(pPr, 'ind', {'left': '0', 'firstLine': '0'})
    if level == 0:
        set_child_element(pPr, 'pageBreakBefore', {})
        
    sort_element_children(pPr, PPR_ORDER)

def clean_bibliography_sdt(sdt_elem):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    sdtContent = sdt_elem.find('w:sdtContent', namespaces)
    if sdtContent is None: return
    for child in list(sdtContent): sdtContent.remove(child)
    
    # Standard APA 7th edition entries (with single line spacing 240 dxa)
    refs_data = [
        {
            'plain1': "'Afiifah, K., Azzahra, Z. F., & Anggoro, A. D. (2022). Analisis teknik Entity-Relationship Diagram dalam perancangan database: Sebuah literature review. ",
            'italic': "INTECH (Informatika dan Teknologi)",
            'plain2': ", 3(1), 8\u201314. https://doi.org/10.54895/intech.v3i1.1278"
        },
        {
            'plain1': "Aliyah, A., Hartono, N., & Muin, A. A. (2024). Penggunaan User Acceptance Testing (UAT) pada pengujian sistem informasi pengelolaan keuangan dan inventaris barang. ",
            'italic': "Switch: Jurnal Sains dan Teknologi Informasi",
            'plain2': ", 3(1), 84\u2013100. https://doi.org/10.62951/switch.v3i1.330"
        },
        {
            'plain1': "Ghai, V. (2025). Exploring the future career potential of Blender 3D as a professional tool. ",
            'italic': "International Journal of Advance Research",
            'plain2': ". https://www.ijariit.com/manuscript/exploring-the-future-career-potential-of-blender-3d-as-a-professional-tool/"
        },
        {
            'plain1': "Jamaludin, J., & Saepuloh, L. (2024). Tren riset twin digital smart campus. ",
            'italic': "Sang Pencerah: Jurnal Ilmiah Universitas Muhammadiyah Buton",
            'plain2': ", 10(2), 408\u2013425. https://doi.org/10.35326/pencerah.v10i2.5317"
        },
        {
            'plain1': "Kurniawan, T. A. (2018). Pemodelan Use Case (UML): Evaluasi terhadap beberapa kesalahan dalam praktik. ",
            'italic': "Jurnal Teknologi Informasi dan Ilmu Komputer (JTIIK)",
            'plain2': ", 5(1), 77\u201386. https://doi.org/10.25126/jtiik.201851610"
        },
        {
            'plain1': "Maulida, M., Zahro, F., Hakim, R., & Akbar, M. S. (2025). Pengujian black box testing pada sistem website pemesanan online Toko Ayam Krispy. ",
            'italic': "Jurnal Media Akademik (JMA)",
            'plain2': ", 3(5). https://mediaakademik.com/index.php/jma/article/view/392"
        },
        {
            'plain1': "Muharam, Y., Anggara, M. B., & Hanafi, T. J. (2023). Implementasi peta 3 dimensi menggunakan metode IMSDD (Interactive Multimedia System Design and Development) dan WebGL API berbasis web (Studi kasus di SMP Karya Pembangunan 2 Majalaya). ",
            'italic': "Jurnal Informatika-COMPUTING",
            'plain2': ", 10, 20\u201330. https://doi.org/10.55222/computing.v10i01.1155"
        },
        {
            'plain1': "Siv, T. (2025). A framework for scalable digital twin deployment in smart campus building facility management. ",
            'italic': "arXiv",
            'plain2': ". https://doi.org/10.48550/arXiv.2512.12149"
        },
        {
            'plain1': "Taurusta, C., Asiddiq, A. M., Suprianto, S., & Setiawan, H. (2024). Visualisasi gedung kampus 1 Universitas Muhammadiyah Sidoarjo menggunakan augmented reality sebagai media informasi. ",
            'italic': "Journal of Technology and System Information",
            'plain2': ", 1(1), 55\u201370. https://doi.org/10.47134/jtsi.v1i1.2146"
        }
    ]
    
    for entry in refs_data:
        p = lxml.etree.Element(f'{{{ns_uri}}}p')
        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
        set_child_element(pPr, 'pStyle', {'val': 'Normal'})
        set_child_element(pPr, 'ind', {'left': '567', 'hanging': '567'})
        set_child_element(pPr, 'spacing', {'before': '0', 'after': '120', 'line': '240', 'lineRule': 'auto'})
        set_child_element(pPr, 'jc', {'val': 'both'})
        sort_element_children(pPr, PPR_ORDER)
        p.append(pPr)
        
        r1 = lxml.etree.Element(f'{{{ns_uri}}}r')
        t1 = lxml.etree.Element(f'{{{ns_uri}}}t')
        t1.text = entry['plain1']
        t1.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        r1.append(t1)
        p.append(r1)
        
        r2 = lxml.etree.Element(f'{{{ns_uri}}}r')
        rPr2 = lxml.etree.Element(f'{{{ns_uri}}}rPr')
        set_child_element(rPr2, 'i', {})
        set_child_element(rPr2, 'iCs', {})
        r2.append(rPr2)
        t2 = lxml.etree.Element(f'{{{ns_uri}}}t')
        t2.text = entry['italic']
        t2.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        r2.append(t2)
        p.append(r2)
        
        r3 = lxml.etree.Element(f'{{{ns_uri}}}r')
        t3 = lxml.etree.Element(f'{{{ns_uri}}}t')
        t3.text = entry['plain2']
        t3.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        r3.append(t3)
        p.append(r3)
        
        sdtContent.append(p)
    print("Replaced bibliography entries inside SDT.")

def load_rels_map(unpacked_dir):
    rels_path = os.path.join(unpacked_dir, 'word', '_rels', 'document.xml.rels')
    rel_map = {}
    if os.path.exists(rels_path):
        try:
            tree = lxml.etree.parse(rels_path)
            root = tree.getroot()
            for rel in root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
                rel_id = rel.get('Id')
                target = rel.get('Target')
                if rel_id and target:
                    rel_map[rel_id] = target
        except Exception as e:
            print(f"Error loading relationships from {rels_path}: {e}")
    return rel_map

def scale_cover_drawings(p, namespaces, unpacked_dir=None, rel_map=None):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    drawings = p.findall('.//w:drawing', namespaces)
    if not drawings:
        return
        
    pPr = p.find('w:pPr', namespaces)
    if pPr is None:
        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
        p.insert(0, pPr)
    set_child_element(pPr, 'jc', {'val': 'center'})
    set_child_element(pPr, 'ind', {'left': '0', 'firstLine': '0'})
    sort_element_children(pPr, PPR_ORDER)
    
    max_width_emu = 1800000   # 5.0 cm
    max_height_emu = 1800000  # 5.0 cm
    
    for drawing in drawings:
        aspect_ratio = None
        if unpacked_dir and rel_map:
            blip = drawing.find('.//a:blip', {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'})
            if blip is not None:
                embed_id = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                if embed_id and embed_id in rel_map:
                    rel_target = rel_map[embed_id]
                    img_path = os.path.join(unpacked_dir, 'word', rel_target)
                    if os.path.exists(img_path):
                        try:
                            from PIL import Image
                            with Image.open(img_path) as img:
                                img_w, img_h = img.size
                                if img_h > 0:
                                    aspect_ratio = img_w / img_h
                        except Exception as e:
                            print(f"  Error reading cover image aspect ratio: {e}")

        for elem in drawing.iter():
            tag_local = elem.tag.split('}')[-1]
            if tag_local in ['extent', 'ext']:
                cx_str = elem.get('cx')
                cy_str = elem.get('cy')
                if cx_str and cy_str:
                    try:
                        cx = int(cx_str)
                        cy = int(cy_str)
                        if aspect_ratio is not None:
                            cy = int(cx / aspect_ratio)
                            elem.set('cy', str(cy))
                            
                        scale_x = max_width_emu / cx
                        scale_y = max_height_emu / cy
                        scale = min(scale_x, scale_y, 1.0)
                        if scale < 1.0:
                            elem.set('cx', str(int(cx * scale)))
                            elem.set('cy', str(int(cy * scale)))
                            print(f"  Scaled cover drawing to {scale * 100:.2f}% of original size")
                    except ValueError:
                        pass


def scale_lembar_pengesahan(p, namespaces, unpacked_dir=None, rel_map=None):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    drawings = p.findall('.//w:drawing', namespaces)
    if not drawings:
        return
        
    pPr = p.find('w:pPr', namespaces)
    if pPr is None:
        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
        p.insert(0, pPr)
    set_child_element(pPr, 'jc', {'val': 'center'})
    set_child_element(pPr, 'ind', {'left': '0', 'firstLine': '0', 'right': '0'})
    sort_element_children(pPr, PPR_ORDER)
    
    max_width_emu = 5040000   # 14.0cm in EMUs
    max_height_emu = 8532000  # 23.7cm in EMUs
    
    for drawing in drawings:
        # Remove all srcRect elements to disable cropping entirely
        for src_rect in drawing.xpath('.//a:srcRect', namespaces={'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}):
            src_rect.getparent().remove(src_rect)
            
        aspect_ratio = None
        if unpacked_dir and rel_map:
            blip = drawing.find('.//a:blip', {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'})
            if blip is not None:
                embed_id = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                if embed_id and embed_id in rel_map:
                    rel_target = rel_map[embed_id]
                    img_path = os.path.join(unpacked_dir, 'word', rel_target)
                    if os.path.exists(img_path):
                        try:
                            from PIL import Image
                            with Image.open(img_path) as img:
                                img_w, img_h = img.size
                                if img_h > 0:
                                    aspect_ratio = img_w / img_h
                        except Exception as e:
                            print(f"  Error reading image aspect ratio for Lembar Pengesahan: {e}")
                            
        for elem in drawing.iter():
            tag_local = elem.tag.split('}')[-1]
            if tag_local in ['extent', 'ext']:
                cx_str = elem.get('cx')
                cy_str = elem.get('cy')
                if cx_str:
                    try:
                        cx = int(cx_str)
                        if aspect_ratio is not None:
                            cy = int(cx / aspect_ratio)
                        elif cy_str:
                            cy = int(cy_str)
                        else:
                            cy = cx
                            
                        # Scale to fit printable area exactly
                        scale_x = max_width_emu / cx
                        scale_y = max_height_emu / cy
                        scale = min(scale_x, scale_y)
                        
                        cx = int(cx * scale)
                        cy = int(cy * scale)
                        
                        elem.set('cx', str(cx))
                        elem.set('cy', str(cy))
                        print(f"  Scaled Lembar Pengesahan drawing to {cx}x{cy} EMUs (width 14.0cm)")
                    except ValueError:
                        pass

def format_all_tables(root, namespaces):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    tbl_count = 0
    for tbl in root.findall('.//w:tbl', namespaces):
        tbl_count += 1
        tblPr = tbl.find('w:tblPr', namespaces)
        if tblPr is None:
            tblPr = lxml.etree.Element(f'{{{ns_uri}}}tblPr')
            tbl.insert(0, tblPr)
        
        # Center table horizontally
        set_child_element(tblPr, 'jc', {'val': 'center'})
        
        # Format rows and cells
        rows = tbl.findall('w:tr', namespaces)
        if not rows:
            continue
            
        # Check if this is Tabel 1.2 (Jadwal Kegiatan)
        first_row_cells = rows[0].findall('w:tc', namespaces)
        is_tabel_1_2 = False
        if len(first_row_cells) == 6:
            first_cell_text = "".join(first_row_cells[0].itertext()).strip()
            if "Aktivitas" in first_cell_text:
                is_tabel_1_2 = True
                
        # Customize tblGrid for Tabel 1.2
        if is_tabel_1_2:
            tblGrid = tbl.find('w:tblGrid', namespaces)
            if tblGrid is not None:
                for gc in list(tblGrid):
                    tblGrid.remove(gc)
                lxml.etree.SubElement(tblGrid, f'{{{ns_uri}}}gridCol', {f'{{{ns_uri}}}w': '3500'})
                for _ in range(5):
                    lxml.etree.SubElement(tblGrid, f'{{{ns_uri}}}gridCol', {f'{{{ns_uri}}}w': '900'})
        
        for row_idx, row in enumerate(rows):
            is_header = (row_idx == 0)
            cells = row.findall('w:tc', namespaces)
            for cell_idx, cell in enumerate(cells):
                tcPr = cell.find('w:tcPr', namespaces)
                if tcPr is None:
                    tcPr = lxml.etree.Element(f'{{{ns_uri}}}tcPr')
                    cell.insert(0, tcPr)
                
                # Apply column width if it's Tabel 1.2
                if is_tabel_1_2:
                    col_width = '3500' if cell_idx == 0 else '900'
                    set_child_element(tcPr, 'tcW', {'w': col_width, 'type': 'dxa'})
                
                # Vertical alignment
                if is_header:
                    set_child_element(tcPr, 'vAlign', {'val': 'center'})
                else:
                    set_child_element(tcPr, 'vAlign', {'val': 'center'} if is_tabel_1_2 else {'val': 'top'})
                
                # Process cell paragraphs
                for p in cell.findall('w:p', namespaces):
                    pPr = p.find('w:pPr', namespaces)
                    if pPr is None:
                        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                        p.insert(0, pPr)
                    
                    # Horizontal alignment
                    if is_header:
                        set_child_element(pPr, 'jc', {'val': 'center'})
                    else:
                        if is_tabel_1_2 and cell_idx > 0:
                            set_child_element(pPr, 'jc', {'val': 'center'})
                        else:
                            set_child_element(pPr, 'jc', {'val': 'left'})
                        
                    # Clear indentation
                    set_child_element(pPr, 'ind', {'left': '0', 'firstLine': '0', 'right': '0'})
                    sort_element_children(pPr, PPR_ORDER)
    print(f"  Formatted {tbl_count} tables in document.xml.")

def center_and_scale_drawings(p, namespaces, unpacked_dir=None, rel_map=None):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    drawings = p.findall('.//w:drawing', namespaces)
    if not drawings:
        return
        
    # Set paragraph alignment to center and clear indents on the figure paragraph
    pPr = p.find('w:pPr', namespaces)
    if pPr is None:
        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
        p.insert(0, pPr)
    set_child_element(pPr, 'jc', {'val': 'center'})
    set_child_element(pPr, 'ind', {'left': '0', 'firstLine': '0'})
    sort_element_children(pPr, PPR_ORDER)
    
    # Shared BODY-figure bounding box (MUST match inject_all_images.py):
    #   BODY_MAX_W_EMU = 15 cm, BODY_MAX_H_EMU = 16 cm (1 cm = 360000 EMU).
    # Aspect ratio is preserved (cy recomputed from the PIL aspect), srcRect is
    # stripped (no crop), and a single min-scale fits the figure in the box.
    max_width_emu = 5400000   # 15.0 cm in EMUs (BODY_MAX_W_EMU)
    max_height_emu = 5760000  # 16.0 cm in EMUs (BODY_MAX_H_EMU)
    
    for drawing in drawings:
        # Remove all srcRect elements to disable cropping entirely
        for src_rect in drawing.xpath('.//a:srcRect', namespaces={'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}):
            src_rect.getparent().remove(src_rect)
            
        aspect_ratio = None
        if unpacked_dir and rel_map:
            blip = drawing.find('.//a:blip', {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'})
            if blip is not None:
                embed_id = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                if embed_id and embed_id in rel_map:
                    rel_target = rel_map[embed_id]
                    img_path = os.path.join(unpacked_dir, 'word', rel_target)
                    if os.path.exists(img_path):
                        try:
                            from PIL import Image
                            with Image.open(img_path) as img:
                                img_w, img_h = img.size
                                if img_h > 0:
                                    aspect_ratio = img_w / img_h
                        except Exception as e:
                            print(f"  Error reading image aspect ratio: {e}")

        # Scale based on aspect ratio and enforce limits
        for elem in drawing.iter():
            tag_local = elem.tag.split('}')[-1]
            if tag_local in ['extent', 'ext']:
                cx_str = elem.get('cx')
                cy_str = elem.get('cy')
                if cx_str:
                    try:
                        cx = int(cx_str)
                        if aspect_ratio is not None:
                            cy = int(cx / aspect_ratio)
                        elif cy_str:
                            cy = int(cy_str)
                        else:
                            cy = cx
                            
                        # Apply limits
                        scale_x = max_width_emu / cx
                        scale_y = max_height_emu / cy
                        scale = min(scale_x, scale_y, 1.0)
                        
                        if scale < 1.0:
                            cx = int(cx * scale)
                            cy = int(cy * scale)
                            
                        elem.set('cx', str(cx))
                        elem.set('cy', str(cy))
                    except ValueError:
                        pass

def build_toc_entry(caption_text, page_num, bookmark_name):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    
    def set_child_element(parent, tag_name, attrs=None):
        el = lxml.etree.SubElement(parent, f'{{{ns_uri}}}{tag_name}')
        if attrs:
            for k, v in attrs.items():
                el.set(f'{{{ns_uri}}}{k}', v)
        return el

    PPR_ORDER = [
        'pStyle', 'keepNext', 'keepLines', 'pageBreakBefore', 'framePr',
        'widowControl', 'numPr', 'suppressLineNumbers', 'pBdr', 'shd',
        'tabs', 'suppressAutoHyphens', 'kinsoku', 'wordWrap', 'overflowPunct',
        'topLinePunct', 'autoSpaceDE', 'autoSpaceDN', 'bidi', 'adjustRightInd',
        'snapToGrid', 'spacing', 'ind', 'contextualSpacing', 'mirrorIndents',
        'suppressOverlap', 'jc', 'textDirection', 'textAlignment', 'textboxTightWrap',
        'outlineLvl', 'divId', 'cnfStyle', 'rPr', 'sectPr', 'pPrChange'
    ]

    def sort_element_children(parent, order_list):
        def key_func(child):
            tag = child.tag
            local_name = tag[len(f'{{{ns_uri}}}'):] if tag.startswith(f'{{{ns_uri}}}') else tag.split('}')[-1]
            return order_list.index(local_name) if local_name in order_list else len(order_list)
        children = list(parent)
        for child in children: parent.remove(child)
        children.sort(key=key_func)
        for child in children: parent.append(child)

    p = lxml.etree.Element(f'{{{ns_uri}}}p')
    pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
    
    set_child_element(pPr, 'pStyle', {'val': 'TableofFigures'})
    
    rPr_ppr = lxml.etree.Element(f'{{{ns_uri}}}rPr')
    set_child_element(rPr_ppr, 'noProof', {})
    pPr.append(rPr_ppr)
    
    tabs = lxml.etree.Element(f'{{{ns_uri}}}tabs')
    set_child_element(tabs, 'tab', {'val': 'right', 'leader': 'dot', 'pos': '7927'})
    pPr.append(tabs)
    
    sort_element_children(pPr, PPR_ORDER)
    p.append(pPr)
    
    # Hyperlink element
    hyperlink = lxml.etree.SubElement(p, f'{{{ns_uri}}}hyperlink', {'{'+ns_uri+'}anchor': bookmark_name, '{'+ns_uri+'}history': '1'})
    
    # Caption text run
    r = lxml.etree.SubElement(hyperlink, f'{{{ns_uri}}}r')
    rPr = lxml.etree.SubElement(r, f'{{{ns_uri}}}rPr')
    set_child_element(rPr, 'noProof', {})
    t = lxml.etree.SubElement(r, f'{{{ns_uri}}}t')
    t.text = caption_text
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    
    # Tab run (for dot leader)
    tab_r = lxml.etree.SubElement(hyperlink, f'{{{ns_uri}}}r')
    tab_rPr = lxml.etree.SubElement(tab_r, f'{{{ns_uri}}}rPr')
    set_child_element(tab_rPr, 'noProof', {})
    set_child_element(tab_rPr, 'webHidden', {})
    lxml.etree.SubElement(tab_r, f'{{{ns_uri}}}tab')
    
    # Page number run
    page_r = lxml.etree.SubElement(hyperlink, f'{{{ns_uri}}}r')
    page_rPr = lxml.etree.SubElement(page_r, f'{{{ns_uri}}}rPr')
    set_child_element(page_rPr, 'noProof', {})
    set_child_element(page_rPr, 'webHidden', {})
    page_t = lxml.etree.SubElement(page_r, f'{{{ns_uri}}}t')
    page_t.text = str(page_num)
    
    return p

def replace_mentions_in_paragraph(text):
    return text

def format_caption_paragraph_clean(p, label, prefix, seq_name, default_val, desc, namespaces):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    
    pPr = p.find('w:pPr', namespaces)
    if pPr is None:
        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
        p.insert(0, pPr)
        
    set_child_element(pPr, 'pStyle', {'val': 'Caption'})
    # Keep the caption with its image and prevent it splitting across pages.
    set_child_element(pPr, 'keepNext', {})
    set_child_element(pPr, 'keepLines', {})
    set_child_element(pPr, 'spacing', {'before': '120', 'after': '120', 'line': '240', 'lineRule': 'auto'})
    set_child_element(pPr, 'jc', {'val': 'center'})
    set_child_element(pPr, 'ind', {'firstLine': '0', 'left': '0'})
    sort_element_children(pPr, PPR_ORDER)
    
    # Extract bookmarks (resilient to namespaces)
    bookmarks = []
    for elem in list(p):
        if elem.tag.endswith('bookmarkStart'):
            bm_id = elem.get(f'{{{ns_uri}}}id') or elem.get('id')
            bm_name = elem.get(f'{{{ns_uri}}}name') or elem.get('name')
            if bm_id is not None:
                bookmarks.append(('start', bm_id, bm_name or ""))
        elif elem.tag.endswith('bookmarkEnd'):
            bm_id = elem.get(f'{{{ns_uri}}}id') or elem.get('id')
            if bm_id is not None:
                bookmarks.append(('end', bm_id, None))
            
    # Clear all child elements except pPr
    for elem in list(p):
        if elem != pPr:
            p.remove(elem)
            
    # Add bookmarkStarts
    for bm_type, bm_id, bm_name in bookmarks:
        if bm_type == 'start':
            bms = lxml.etree.Element(f'{{{ns_uri}}}bookmarkStart')
            bms.set(f'{{{ns_uri}}}id', str(bm_id))
            bms.set(f'{{{ns_uri}}}name', str(bm_name))
            p.append(bms)
            
    # Label prefix, e.g. "Gambar 2."
    r1 = lxml.etree.Element(f'{{{ns_uri}}}r')
    rPr1 = lxml.etree.Element(f'{{{ns_uri}}}rPr')
    set_child_element(rPr1, 'rFonts', {'ascii': 'Times New Roman', 'hAnsi': 'Times New Roman'})
    set_child_element(rPr1, 'b', {})
    set_child_element(rPr1, 'bCs', {})
    set_child_element(rPr1, 'sz', {'val': '24'})
    set_child_element(rPr1, 'szCs', {'val': '24'})
    r1.append(rPr1)
    
    t1 = lxml.etree.Element(f'{{{ns_uri}}}t')
    t1.text = f"{label} {prefix}"
    if t1.text.startswith(' ') or t1.text.endswith(' '):
        t1.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    r1.append(t1)
    p.append(r1)
    
    # SEQ field
    r2 = lxml.etree.Element(f'{{{ns_uri}}}r')
    fld2 = lxml.etree.Element(f'{{{ns_uri}}}fldChar', **{f'{{{ns_uri}}}fldCharType': "begin"})
    r2.append(fld2)
    p.append(r2)
    
    r3 = lxml.etree.Element(f'{{{ns_uri}}}r')
    ins3 = lxml.etree.Element(f'{{{ns_uri}}}instrText')
    if default_val == 1:
        ins3.text = f" SEQ {seq_name} \\r 1 \\* ARABIC "
    else:
        ins3.text = f" SEQ {seq_name} \\* ARABIC "
    ins3.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    r3.append(ins3)
    p.append(r3)
    
    r4 = lxml.etree.Element(f'{{{ns_uri}}}r')
    fld4 = lxml.etree.Element(f'{{{ns_uri}}}fldChar', **{f'{{{ns_uri}}}fldCharType': "separate"})
    r4.append(fld4)
    p.append(r4)
    
    r5 = lxml.etree.Element(f'{{{ns_uri}}}r')
    t5 = lxml.etree.Element(f'{{{ns_uri}}}t')
    t5.text = str(default_val)
    r5.append(t5)
    p.append(r5)
    
    r6 = lxml.etree.Element(f'{{{ns_uri}}}r')
    fld6 = lxml.etree.Element(f'{{{ns_uri}}}fldChar', **{f'{{{ns_uri}}}fldCharType': "end"})
    r6.append(fld6)
    p.append(r6)
    
    # Description
    r7 = lxml.etree.Element(f'{{{ns_uri}}}r')
    rPr7 = lxml.etree.Element(f'{{{ns_uri}}}rPr')
    set_child_element(rPr7, 'rFonts', {'ascii': 'Times New Roman', 'hAnsi': 'Times New Roman'})
    set_child_element(rPr7, 'sz', {'val': '24'})
    set_child_element(rPr7, 'szCs', {'val': '24'})
    r7.append(rPr7)
    
    t7 = lxml.etree.Element(f'{{{ns_uri}}}t')
    t7.text = f" {desc.strip()}"
    t7.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    r7.append(t7)
    p.append(r7)
    
    # Add bookmarkEnds
    for bm_type, bm_id, _ in bookmarks:
        if bm_type == 'end':
            bme = lxml.etree.Element(f'{{{ns_uri}}}bookmarkEnd')
            bme.set(f'{{{ns_uri}}}id', str(bm_id))
            p.append(bme)

def insert_dynamic_toc_field(body, insertion_idx, field_instruction, namespaces):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    
    p = lxml.etree.Element(f'{{{ns_uri}}}p')
    pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
    set_child_element(pPr, 'pStyle', {'val': 'TableofFigures'})
    tabs = lxml.etree.Element(f'{{{ns_uri}}}tabs')
    set_child_element(tabs, 'tab', {'val': 'right', 'leader': 'dot', 'pos': '7927'})
    pPr.append(tabs)
    
    # Sort pPr
    children_list = list(pPr)
    for c in children_list: pPr.remove(c)
    for tag in PPR_ORDER:
        for c in children_list:
            if c.tag.split('}')[-1] == tag:
                pPr.append(c)
                break
    p.append(pPr)
    
    r_begin = lxml.etree.Element(f'{{{ns_uri}}}r')
    set_child_element(r_begin, 'fldChar', {'fldCharType': 'begin'})
    p.append(r_begin)
    
    r_instr = lxml.etree.Element(f'{{{ns_uri}}}r')
    instr = lxml.etree.Element(f'{{{ns_uri}}}instrText')
    instr.text = field_instruction
    instr.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    r_instr.append(instr)
    p.append(r_instr)
    
    r_sep = lxml.etree.Element(f'{{{ns_uri}}}r')
    set_child_element(r_sep, 'fldChar', {'fldCharType': 'separate'})
    p.append(r_sep)
    
    r_end = lxml.etree.Element(f'{{{ns_uri}}}r')
    set_child_element(r_end, 'fldChar', {'fldCharType': 'end'})
    p.append(r_end)
    
    body.insert(insertion_idx, p)
    return p

def format_document_xmls(unpacked_dir):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    styles_path = os.path.join(unpacked_dir, 'word/styles.xml')
    doc_path = os.path.join(unpacked_dir, 'word/document.xml')
    rel_map = load_rels_map(unpacked_dir)
    
    # 1. Modify Styles
    if os.path.exists(styles_path):
        parser = lxml.etree.XMLParser(remove_blank_text=False)
        tree = lxml.etree.parse(styles_path, parser)
        root = tree.getroot()
        ensure_front_matter_heading_style(root)
        ensure_appendix_heading_style(root)
        ensure_toc9_style(root)
        # ensure_hyperlink_style(root)
        for style in root.findall('w:style', namespaces):
            style_id = style.get(f'{{{ns_uri}}}styleId')
            style_type = style.get(f'{{{ns_uri}}}type')
            if style_type == 'paragraph':
                pPr = style.find('w:pPr', namespaces)
                if pPr is None:
                    pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                    style.append(pPr)
                if style_id == 'Normal':
                    set_child_element(pPr, 'spacing', {'before': '0', 'after': '0', 'line': '360', 'lineRule': 'auto'})
                    set_child_element(pPr, 'jc', {'val': 'both'})
                    set_child_element(pPr, 'ind', {'firstLine': '0', 'left': '0'})
                elif style_id == 'ListParagraph':
                    set_child_element(pPr, 'spacing', {'before': '0', 'after': '0', 'line': '360', 'lineRule': 'auto'})
                elif style_id == 'Caption':
                    set_child_element(pPr, 'spacing', {'before': '120', 'after': '120', 'line': '240', 'lineRule': 'auto'})
                    set_child_element(pPr, 'jc', {'val': 'center'})
                    set_child_element(pPr, 'ind', {'firstLine': '0', 'left': '0'})
                elif style_id in ['TOC1', 'TOC2', 'TOC3', 'TableofFigures']:
                    set_child_element(pPr, 'spacing', {'before': '0', 'after': '0', 'line': '360', 'lineRule': 'auto'})
                    tabs = set_child_element(pPr, 'tabs')
                    for child in list(tabs):
                        tabs.remove(child)
                    set_child_element(tabs, 'tab', {'val': 'right', 'leader': 'dot', 'pos': '7927'})
                elif style_id.startswith('Heading'):
                    if style_id in ['Heading1', 'Heading2']:
                        set_child_element(pPr, 'spacing', {'before': '240', 'after': '120', 'line': '360', 'lineRule': 'auto'})
                    else:
                        set_child_element(pPr, 'spacing', {'before': '120', 'after': '60', 'line': '360', 'lineRule': 'auto'})
                    set_child_element(pPr, 'ind', {'firstLine': '0', 'left': '0'})
                    if style_id == 'Heading1':
                        set_child_element(pPr, 'jc', {'val': 'center'})
                        set_child_element(pPr, 'pageBreakBefore', {})
                    else:
                        set_child_element(pPr, 'jc', {'val': 'left'})
                sort_element_children(pPr, PPR_ORDER)
            sort_element_children(style, STYLE_ORDER)
        tree.write(styles_path, encoding='utf-8', xml_declaration=True)
        print("Updated styles.xml.")
        
    # 2. Modify Document
    if os.path.exists(doc_path):
        parser = lxml.etree.XMLParser(remove_blank_text=False)
        tree = lxml.etree.parse(doc_path, parser)
        root = tree.getroot()
        body = root.find('w:body', namespaces)
        if body is None: return
        
        # Find the original paragraph-level sectPr from the template to preserve header/footer references
        original_sectPr = None
        for p_elem in body.findall('w:p', namespaces):
            pPr_elem = p_elem.find('w:pPr', namespaces)
            if pPr_elem is not None:
                sectPr_elem = pPr_elem.find('w:sectPr', namespaces)
                if sectPr_elem is not None:
                    import copy
                    original_sectPr = copy.deepcopy(sectPr_elem)
                    break
                    
        # Reorder table and figure captions
        children = list(body)
        
        # 1. Move table captions above tables
        i = 0
        while i < len(children):
            child = children[i]
            if child.tag.endswith('tbl'):
                if i + 1 < len(children) and children[i+1].tag.endswith('p'):
                    p_after = children[i+1]
                    txt_after = "".join([t.text for t in p_after.iter(f'{{{ns_uri}}}t') if t.text]).strip()
                    if txt_after.startswith('Tabel'):
                        body.remove(p_after)
                        body.insert(i, p_after)
                        children = list(body)
                        print(f"  Moved table caption '{txt_after}' above the table.")
            i += 1

        # 1b. Move figure captions to sit immediately after their figure when a
        # single narrative paragraph separates them: [drawing][narasi][kapsi] ->
        # [drawing][kapsi][narasi]. This is a GENERAL structural rule (analogous
        # to the table-caption move above) with no hardcoded caption text. It
        # restores figure/caption adjacency for figures whose drawing was anchored
        # to a narrative paragraph during the merge (e.g. survey charts), so the
        # caption is immediately preceded by its drawing.
        children = list(body)
        i = 2
        while i < len(children):
            cap = children[i]
            if cap.tag.endswith('p'):
                cap_text = "".join(t.text for t in cap.iter(f'{{{ns_uri}}}t') if t.text).strip()
                cap_style = _paragraph_style(cap, namespaces) or ""
                is_fig_caption = (cap_style == 'Caption' and cap_text.lower().startswith('gambar')) \
                    or re.match(r'^Gambar\s+[0-9]', cap_text, re.IGNORECASE)
                if is_fig_caption:
                    prev = children[i - 1]
                    prev2 = children[i - 2]
                    prev_is_p = prev.tag.endswith('p')
                    prev2_is_drawing = prev2.tag.endswith('p') and prev2.find('.//w:drawing', namespaces) is not None
                    prev_is_drawing = prev_is_p and prev.find('.//w:drawing', namespaces) is not None
                    prev_style = _paragraph_style(prev, namespaces) or "" if prev_is_p else ""
                    prev_text = "".join(t.text for t in prev.iter(f'{{{ns_uri}}}t') if t.text).strip() if prev_is_p else ""
                    prev_is_caption = bool(re.match(r'^(Gambar|Tabel)\s+[0-9]', prev_text, re.IGNORECASE)) or prev_style == 'Caption'
                    prev_is_heading = prev_style.startswith('Heading')
                    # Only reposition the specific [drawing][narrative][caption] pattern.
                    if (not prev_is_drawing) and prev2_is_drawing and prev_is_p \
                            and not prev_is_caption and not prev_is_heading:
                        body.remove(cap)
                        body.insert(i - 1, cap)
                        children = list(body)
                        print(f"  Moved figure caption '{cap_text[:50]}' to follow its figure.")
            i += 1

        # 2. Move figure captions below figures (Disabled: causing reordering issues; all figures are already placed correctly above captions)
        # i = 0
        # while i < len(children):
        #     child = children[i]
        #     if child.tag.endswith('p'):
        #         if child.find('.//w:drawing', namespaces) is not None:
        #             if i - 1 >= 0 and children[i-1].tag.endswith('p'):
        #                 p_before = children[i-1]
        #                 txt_before = "".join([t.text for t in p_before.iter(f'{{{ns_uri}}}t') if t.text]).strip()
        #                 if txt_before.startswith('Gambar'):
        #                     body.remove(p_before)
        #                     body.insert(i, p_before)
        #                     children = list(body)
        #                     print(f"  Moved figure caption '{txt_before}' below the figure.")
        #     i += 1

            
        # Remove manual page breaks that are immediately before Heading 1 (to prevent double page breaks)
        children = list(body)
        i = 0
        while i < len(children):
            p = children[i]
            if p.tag.endswith('p'):
                has_page_break = False
                br_elems = []
                for elem in p.iter():
                    tag_local = elem.tag.split('}')[-1]
                    if tag_local == 'br' and elem.get(f'{{{ns_uri}}}type') == 'page':
                        has_page_break = True
                        br_elems.append(elem)
                        
                if has_page_break:
                    is_before_heading1 = False
                    for j in range(i + 1, len(children)):
                        next_child = children[j]
                        next_p = next_child
                        if next_child.tag.endswith('sdt'):
                            sdtContent = next_child.find('w:sdtContent', namespaces)
                            if sdtContent is not None:
                                next_p = sdtContent.find('w:p', namespaces)
                        
                        if next_p is None or not next_p.tag.endswith('p'):
                            break
                        next_text = "".join(next_p.itertext()).strip()
                        next_pPr = next_p.find('w:pPr', namespaces)
                        next_pStyle = next_pPr.find('w:pStyle', namespaces) if next_pPr is not None else None
                        next_pStyle_val = next_pStyle.get(f'{{{ns_uri}}}val') if next_pStyle is not None else ""
                        
                        if next_pStyle_val == 'Heading1':
                            is_before_heading1 = True
                            break
                        if next_text:
                            break
                            
                    if is_before_heading1:
                        print(f"  Removing manual page break before Heading 1 at index {i}")
                        for br in br_elems:
                            parent = br.getparent()
                            if parent is not None:
                                parent.remove(br)
                                if len(parent) == 0 and not parent.text:
                                    gp = parent.getparent()
                                    if gp is not None: gp.remove(parent)
                        p_text = "".join(p.itertext()).strip()
                        runs = p.findall('.//w:r', namespaces)
                        if not p_text and len(runs) == 0:
                            body.remove(p)
                            children = list(body)
                            continue
            i += 1
            
        # 4. Reconstruct body (reference rewriting is deferred to Fase 2 after the
        #    chapter-aware caption pass has built the caption registry).
        reconstructed_children = []
        current_section_title = ""

        # Fase 0 (R5.2-5.5): batas front matter dinamis, mengganti konstanta 60.
        bab1_idx_orig = find_front_matter_boundary(children, namespaces)
            
        def create_caption_paragraph_local(label, prefix, seq_name, default_val, desc, bookmark_id, bookmark_name):
            p = lxml.etree.Element(f'{{{ns_uri}}}p')
            pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
            set_child_element(pPr, 'pStyle', {'val': 'Caption'})
            # Keep the caption with its image and prevent it splitting across pages.
            set_child_element(pPr, 'keepNext', {})
            set_child_element(pPr, 'keepLines', {})
            set_child_element(pPr, 'spacing', {'before': '120', 'after': '120', 'line': '240', 'lineRule': 'auto'})
            set_child_element(pPr, 'jc', {'val': 'center'})
            set_child_element(pPr, 'ind', {'firstLine': '0', 'left': '0'})
            sort_element_children(pPr, PPR_ORDER)
            p.append(pPr)
            
            bms = lxml.etree.Element(f'{{{ns_uri}}}bookmarkStart', id=str(bookmark_id), name=bookmark_name)
            p.append(bms)

            # Label and prefix, e.g. "Gambar 2."
            r1 = lxml.etree.Element(f'{{{ns_uri}}}r')
            t1 = lxml.etree.Element(f'{{{ns_uri}}}t')
            t1.text = f"{label} {prefix}"
            if t1.text.startswith(' ') or t1.text.endswith(' '):
                t1.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            r1.append(t1)
            p.append(r1)
            
            # fldChar begin
            r2 = lxml.etree.Element(f'{{{ns_uri}}}r')
            fld2 = lxml.etree.Element(f'{{{ns_uri}}}fldChar', **{f'{{{ns_uri}}}fldCharType': "begin"})
            r2.append(fld2)
            p.append(r2)
            
            # instrText
            r3 = lxml.etree.Element(f'{{{ns_uri}}}r')
            ins3 = lxml.etree.Element(f'{{{ns_uri}}}instrText')
            if default_val == 1:
                ins3.text = f" SEQ {seq_name} \\r 1 \\* ARABIC "
            else:
                ins3.text = f" SEQ {seq_name} \\* ARABIC "
            ins3.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            r3.append(ins3)
            p.append(r3)
            
            # fldChar separate
            r4 = lxml.etree.Element(f'{{{ns_uri}}}r')
            fld4 = lxml.etree.Element(f'{{{ns_uri}}}fldChar', **{f'{{{ns_uri}}}fldCharType': "separate"})
            r4.append(fld4)
            p.append(r4)
            
            # default value run
            r5 = lxml.etree.Element(f'{{{ns_uri}}}r')
            t5 = lxml.etree.Element(f'{{{ns_uri}}}t')
            t5.text = str(default_val)
            r5.append(t5)
            p.append(r5)
            
            # fldChar end
            r6 = lxml.etree.Element(f'{{{ns_uri}}}r')
            fld6 = lxml.etree.Element(f'{{{ns_uri}}}fldChar', **{f'{{{ns_uri}}}fldCharType': "end"})
            r6.append(fld6)
            p.append(r6)
            
            # description run
            r7 = lxml.etree.Element(f'{{{ns_uri}}}r')
            t7 = lxml.etree.Element(f'{{{ns_uri}}}t')
            t7.text = f" {desc}"
            t7.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            r7.append(t7)
            p.append(r7)
            
            bme = lxml.etree.Element(f'{{{ns_uri}}}bookmarkEnd', id=str(bookmark_id))
            p.append(bme)
            
            return p

        # Find cover page end index (last paragraph before the SECOND drawing, which is Lembar Pengesahan)
        collected_captions = []
        estimated_page = 1
        para_count = 0
        cover_end_idx = 0
        drawing_count = 0
        for idx, child in enumerate(children):
            if idx < bab1_idx_orig and child.tag.endswith('p'):
                if child.find('.//w:drawing', namespaces) is not None:
                    drawing_count += 1
                    if drawing_count == 2:
                        break
                cover_end_idx = idx

        lembar_pengesahan_processed = False
        need_page_break_after_lp = False
        for idx, child in enumerate(children):
            para_count += 1
            if para_count > 25:
                estimated_page += 1
                para_count = 0
                
            if idx < bab1_idx_orig:
                if idx <= cover_end_idx:
                    if child.tag.endswith('p'):
                        scale_cover_drawings(child, namespaces, unpacked_dir, rel_map)
                        text = "".join(child.itertext()).strip()
                        if not text:
                            pPr = child.find('w:pPr', namespaces)
                            if pPr is None:
                                pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                                child.insert(0, pPr)
                            set_child_element(pPr, 'spacing', {'before': '0', 'after': '0', 'line': '240', 'lineRule': 'auto'})
                            sort_element_children(pPr, PPR_ORDER)
                    reconstructed_children.append(child)
                else:
                    # Transition zone: skip empty paragraphs to prevent blank pages
                    if child.tag.endswith('p'):
                        text = "".join(child.itertext()).strip()
                        has_drawing = child.find('.//w:drawing', namespaces) is not None
                        has_sectPr = child.find('.//w:sectPr', namespaces) is not None
                        has_fldChar = child.find('.//w:fldChar', namespaces) is not None
                        has_instr = child.find('.//w:instrText', namespaces) is not None
                        if text or has_drawing or has_sectPr or has_fldChar or has_instr:
                            if has_drawing and not lembar_pengesahan_processed:
                                scale_lembar_pengesahan(child, namespaces, unpacked_dir, rel_map)
                                pPr = child.find('w:pPr', namespaces)
                                if pPr is None:
                                    pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                                    child.insert(0, pPr)
                                set_child_element(pPr, 'pageBreakBefore', {})
                                sort_element_children(pPr, PPR_ORDER)
                                lembar_pengesahan_processed = True
                                need_page_break_after_lp = True
                                print(f"  Applied page break, margin scaling, and centering to Lembar Pengesahan at index {idx}")
                            elif lembar_pengesahan_processed and need_page_break_after_lp:
                                pPr = child.find('w:pPr', namespaces)
                                if pPr is None:
                                    pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                                    child.insert(0, pPr)
                                set_child_element(pPr, 'pageBreakBefore', {})
                                sort_element_children(pPr, PPR_ORDER)
                                need_page_break_after_lp = False
                                print(f"  Applied page break after Lembar Pengesahan to paragraph at index {idx}")
                            reconstructed_children.append(child)
                        else:
                            print(f"  Removing redundant empty paragraph in front-matter transition at index {idx}")
                    else:
                        reconstructed_children.append(child)
                continue
                
            if child.tag.endswith('p'):
                # Aturan_Umum (R3.3): gambar tanpa baris kapsi di draf TIDAK dibuatkan
                # kapsi maupun nomor. Tidak ada lagi injeksi survey_captions atau pemicu
                # judul-seksi bernama; setiap paragraf dipertahankan apa adanya dan
                # penomoran kapsi ditangani satu kali oleh Fase 1 (chapter-aware pass).
                reconstructed_children.append(child)
            else:
                reconstructed_children.append(child)
                
        for child in list(body):
            body.remove(child)
        for child in reconstructed_children:
            body.append(child)
            
        # 3. Create DAFTAR LAMPIRAN section (run before boundaries are checked so it's in Section 1)
        daftar_tabel_idx = -1
        children_temp = list(body)
        for idx, child in enumerate(children_temp):
            if child.tag.endswith('p'):
                text = "".join(child.itertext()).strip()
                pPr = child.find('w:pPr', namespaces)
                pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                style_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                if text == "DAFTAR TABEL" and style_val == "Heading1":
                    daftar_tabel_idx = idx
                    break
                    
        insertion_idx = -1
        for idx in range(daftar_tabel_idx + 1, len(children_temp)):
            child = children_temp[idx]
            if child.tag.endswith('p'):
                pPr = child.find('w:pPr', namespaces)
                pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                style_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                if style_val == "Heading1":
                    text = "".join(child.itertext()).strip()
                    if "DAFTAR LAMPIRAN" in text.upper():
                        insertion_idx = -1
                        break
                    if "PENDAHULUAN" in text.upper() or "BAB I" in text.upper():
                        insertion_idx = idx
                        break
                        
        if insertion_idx != -1:
            print(f"Inserting DAFTAR LAMPIRAN at index {insertion_idx}...")
            p_head = lxml.etree.Element(f'{{{ns_uri}}}p')
            pPr_head = lxml.etree.Element(f'{{{ns_uri}}}pPr')
            set_child_element(pPr_head, 'pStyle', {'val': 'Heading1'})
            set_child_element(pPr_head, 'pageBreakBefore', {})
            set_child_element(pPr_head, 'jc', {'val': 'center'})
            sort_element_children(pPr_head, PPR_ORDER)
            p_head.append(pPr_head)
            
            r_head = lxml.etree.Element(f'{{{ns_uri}}}r')
            rPr_head = lxml.etree.Element(f'{{{ns_uri}}}rPr')
            set_child_element(rPr_head, 'rFonts', {'ascii': 'Times New Roman', 'hAnsi': 'Times New Roman'})
            set_child_element(rPr_head, 'b', {})
            set_child_element(rPr_head, 'bCs', {})
            set_child_element(rPr_head, 'sz', {'val': '28'})
            set_child_element(rPr_head, 'szCs', {'val': '28'})
            r_head.append(rPr_head)
            t_head = lxml.etree.Element(f'{{{ns_uri}}}t')
            t_head.text = "DAFTAR LAMPIRAN"
            r_head.append(t_head)
            p_head.append(r_head)
            
            body.insert(insertion_idx, p_head)
            insert_dynamic_toc_field(body, insertion_idx + 1, ' TOC \\o "9-9" \\n 9-9 \\h \\z ', namespaces)
            print("Successfully inserted DAFTAR LAMPIRAN heading and TOF field.")
            
        children = list(body)
        parent_map = {c: p for p in root.iter() for c in p}
        
        def is_inside_table(elem):
            curr = elem
            while curr in parent_map:
                parent = parent_map[curr]
                if parent.tag.endswith('tc'): return True
                curr = parent
            return False
            
        # Fase 0 (R5.2/R5.3): batas seksi dinamis tanpa indeks numerik tetap.
        bab1_idx = find_front_matter_boundary(children, namespaces)
        section1_last_p_idx = bab1_idx - 1
        
        daftar_pustaka_heading_idx = -1
        for idx, child in enumerate(children):
            if child.tag.endswith('p'):
                text = "".join([t.text for t in child.iter(f'{{{ns_uri}}}t') if t.text])
                if 'DAFTAR PUSTAKA' in text:
                    pPr = child.find('w:pPr', namespaces)
                    pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                    if pStyle is not None and pStyle.get(f'{{{ns_uri}}}val') == 'Heading1':
                        daftar_pustaka_heading_idx = idx
                        break
                        
        # ---- Fase 1 (R1, R2, R3.1, R3.3): chapter-aware caption pass tunggal ----
        # Telusuri body dalam urutan baca SEKALI: lacak Nomor_Bab dari heading BAB
        # (Heading1) via parse_chapter_number, lalu nomori tiap kapsi gambar/tabel
        # per-bab memakai CaptionRegistry. Deskripsi diambil VERBATIM dari draf.
        registry = CaptionRegistry()
        current_chapter = None
        for idx, child in enumerate(children):
            if not child.tag.endswith('p'):
                continue
            p = child
            if is_inside_table(p):
                continue
            pStyle_val = _paragraph_style(p, namespaces) or "Normal"
            text_clean = _paragraph_text(p, namespaces).strip()
            # Lacak Nomor_Bab dari heading BAB pembungkus (urutan baca).
            if pStyle_val == 'Heading1':
                chap = parse_chapter_number(text_clean)
                if chap is not None:
                    current_chapter = chap
            # Hanya kapsi pada body Section 2 yang dinomori.
            if idx <= section1_last_p_idx:
                continue
            parsed = parse_caption_text(text_clean)
            if parsed is None:
                continue
            is_caption_para = (pStyle_val == 'Caption') or re.match(
                r'^(Gambar|Tabel)\s+[0-9]+', text_clean, re.IGNORECASE)
            if not is_caption_para:
                continue
            label, old_number, desc = parsed
            chapter = current_chapter
            if chapter is None:
                # Fallback R1.7/R2.6: kapsi sebelum BAB pertama -> pakai 1 + peringatan.
                chapter = 1
                print("  [WARNING] Kapsi '%s' muncul sebelum heading BAB; memakai Nomor_Bab=1"
                      % text_clean[:60])
            if label == "Gambar":
                new_number, k, _ = registry.next_figure(chapter, old_number)
            else:
                new_number, k, _ = registry.next_table(chapter, old_number)
            # format_caption_paragraph_clean dipakai apa adanya: default_val=k -> kapsi
            # pertama bab (k==1) memancarkan opsi restart SEQ "\r 1" (R1.4/R2.3).
            format_caption_paragraph_clean(p, label, f"{chapter}.", label, k, desc, namespaces)
            collected_captions.append({
                "type": label,
                "text": f"{label} {new_number} {desc}".strip(),
                "page": estimated_page,
            })

        # ---- Fase 2 (R6): reference rewriter dari registri kapsi ----
        # Tulis ulang penyebutan "Gambar X.Y"/"Tabel X.Y" pada narasi memakai peta
        # yang DITURUNKAN dari registri Fase 1 (bukan tabel angka statis). Kapsi
        # (pStyle 'Caption') dilewati karena sudah dinomori oleh Fase 1.
        ref_warnings = []
        for idx, child in enumerate(children):
            if not child.tag.endswith('p'):
                continue
            p = child
            if is_inside_table(p):
                continue
            if idx <= section1_last_p_idx:
                continue
            if (_paragraph_style(p, namespaces) or "Normal") == 'Caption':
                continue
            for t_elem in p.findall('.//w:t', namespaces):
                if not t_elem.text:
                    continue
                new_text, warns = rewrite_references(
                    t_elem.text, registry.fig_remap, registry.tbl_remap)
                if new_text != t_elem.text:
                    t_elem.text = new_text
                if warns:
                    ref_warnings.extend(warns)
        for warn_msg in ref_warnings:
            print("  [REF] %s" % warn_msg)

        for idx, child in enumerate(children):
            if child.tag.endswith('tbl'): continue
            if child.tag.endswith('sdt'):
                if daftar_pustaka_heading_idx != -1 and idx > daftar_pustaka_heading_idx:
                    clean_bibliography_sdt(child)
                # Formats DAFTAR ISI paragraph inside the TOC sdt
                sdtContent = child.find('w:sdtContent', namespaces)
                if sdtContent is not None:
                    sdtPr = child.find('w:sdtPr', namespaces)
                    tag_elem = sdtPr.find('w:tag', namespaces) if sdtPr is not None else None
                    tag_val = tag_elem.get(f'{{{ns_uri}}}val') if tag_elem is not None else ""
                    if tag_val != 'MENDELEY_BIBLIOGRAPHY':
                        toc_p = sdtContent.find('w:p', namespaces)
                        if toc_p is not None:
                            toc_text = "".join(toc_p.itertext()).strip()
                            if 'DAFTAR ISI' in toc_text.upper():
                                toc_pPr = toc_p.find('w:pPr', namespaces)
                                if toc_pPr is None:
                                    toc_pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                                    toc_p.insert(0, toc_pPr)
                                set_child_element(toc_pPr, 'pStyle', {'val': 'Heading1'})
                                set_child_element(toc_pPr, 'pageBreakBefore', {})
                                sort_element_children(toc_pPr, PPR_ORDER)
                continue
                
            if child.tag.endswith('p'):
                p = child
                if is_inside_table(p): continue
                pPr = p.find('w:pPr', namespaces)
                pStyle_val = "Normal"
                if pPr is not None:
                    pStyle = pPr.find('w:pStyle', namespaces)
                    if pStyle is not None: pStyle_val = pStyle.get(f'{{{ns_uri}}}val')
                    
                is_section2 = (idx > section1_last_p_idx)
                
                # Correct in-text citations
                text = "".join([t.text for t in p.iter(f'{{{ns_uri}}}t') if t.text])
                if 'Aliyah Aliyah' in text:
                    cleaned_text = text.replace('Aliyah Aliyah et al., 2024', 'Aliyah et al., 2024')
                    for r in p.findall(f'{{{ns_uri}}}r', namespaces): p.remove(r)
                    new_r = lxml.etree.Element(f'{{{ns_uri}}}r')
                    new_t = lxml.etree.Element(f'{{{ns_uri}}}t')
                    new_t.text = cleaned_text
                    new_r.append(new_t)
                    p.append(new_r)
                    text = cleaned_text
                    
                # Caption renumbering & reference rewriting handled by Fase 1/Fase 2
                # above (chapter-aware pass + registry-derived reference rewriter).

                # Format Headings
                if pStyle_val == 'Heading1':
                    text = "".join([t.text for t in p.iter(f'{{{ns_uri}}}t') if t.text]).strip()
                    if text.upper().startswith('LAMPIRAN'):
                        pStyle.set(f'{{{ns_uri}}}val', 'taappendixheading')
                        pStyle_val = 'taappendixheading'
                        
                if pStyle_val.startswith('Heading') or pStyle_val == 'taappendixheading':
                    text = "".join([t.text for t in p.iter(f'{{{ns_uri}}}t') if t.text]).strip()
                    if not text:
                        if pPr is not None:
                            set_child_element(pPr, 'pStyle', {'val': 'Normal'})
                            numPr = pPr.find(f'{{{ns_uri}}}numPr', namespaces)
                            if numPr is not None: pPr.remove(numPr)
                        continue
                    if pStyle_val == 'taappendixheading':
                        if pPr is None:
                            pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                            p.insert(0, pPr)
                        set_child_element(pPr, 'pStyle', {'val': 'taappendixheading'})
                        set_child_element(pPr, 'pageBreakBefore', {})
                        numPr = pPr.find(f'{{{ns_uri}}}numPr', namespaces)
                        if numPr is not None:
                            pPr.remove(numPr)
                    elif pStyle_val == 'Heading1':
                        if pPr is None:
                            pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                            p.insert(0, pPr)
                        set_child_element(pPr, 'pageBreakBefore', {})
                        if 'DAFTAR' in text.upper() or 'KATA PENGANTAR' in text.upper() or 'ABSTRAK' in text.upper():
                            set_child_element(pPr, 'pStyle', {'val': 'Heading1'})
                            numPr = pPr.find(f'{{{ns_uri}}}numPr', namespaces)
                            if numPr is not None: pPr.remove(numPr)
                        else:
                            clean_heading_text_and_add_num(p, 0, 76)
                    elif pStyle_val == 'Heading2': clean_heading_text_and_add_num(p, 1, 76)
                    elif pStyle_val == 'Heading3': clean_heading_text_and_add_num(p, 2, 76)
                    elif pStyle_val == 'Heading4': clean_heading_text_and_add_num(p, 3, 76)
                    elif pStyle_val == 'Heading5': clean_heading_text_and_add_num(p, 4, 76)
                else:
                    # Body text
                    if is_section2:
                        if pStyle_val == 'Normal':
                            if pPr is None:
                                pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                                p.insert(0, pPr)
                            left_indent = '0'
                            ind_elem = pPr.find('w:ind', namespaces)
                            if ind_elem is not None:
                                left_indent = ind_elem.get(f'{{{ns_uri}}}left', '0')
                            try: left_val = int(left_indent)
                            except: left_val = 0
                            
                            if left_val > 0: set_child_element(pPr, 'ind', {'firstLine': '0'})
                            else: set_child_element(pPr, 'ind', {'firstLine': '567', 'left': '0'})
                            
                            jc_elem = pPr.find('w:jc', namespaces)
                            jc_val = jc_elem.get(f'{{{ns_uri}}}val', 'both') if jc_elem is not None else 'both'
                            if jc_val not in ['center', 'right']: set_child_element(pPr, 'jc', {'val': 'both'})
                            set_child_element(pPr, 'spacing', {'before': '0', 'after': '0', 'line': '360', 'lineRule': 'auto'})
                        elif pStyle_val == 'ListParagraph':
                            if pPr is None:
                                pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                                p.insert(0, pPr)
                            set_child_element(pPr, 'spacing', {'before': '0', 'after': '0', 'line': '360', 'lineRule': 'auto'})
                        elif pStyle_val == 'Caption':
                            if pPr is None:
                                pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                                p.insert(0, pPr)
                            set_child_element(pPr, 'spacing', {'before': '120', 'after': '120', 'line': '240', 'lineRule': 'auto'})
                            set_child_element(pPr, 'jc', {'val': 'center'})
                            set_child_element(pPr, 'ind', {'firstLine': '0', 'left': '0'})
                    else:
                        if pStyle_val == 'Normal':
                            if pPr is None:
                                pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                                p.insert(0, pPr)
                            set_child_element(pPr, 'ind', {'firstLine': '0'})
                
                # Center and scale drawings if present in paragraph
                if p.find('.//w:drawing', namespaces) is not None:
                    if is_section2:
                        center_and_scale_drawings(p, namespaces, unpacked_dir, rel_map)
                        pPr = p.find('w:pPr', namespaces)
                        if pPr is None:
                            pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                            p.insert(0, pPr)
                        set_child_element(pPr, 'keepNext', {})
                        set_child_element(pPr, 'keepLines', {})
                
                if pPr is not None: sort_element_children(pPr, PPR_ORDER)
                

        # Remove any existing paragraph-level section breaks to avoid duplicates
        for p_elem in body.findall('w:p', namespaces):
            pPr_elem = p_elem.find('w:pPr', namespaces)
            if pPr_elem is not None:
                sectPr_elem = pPr_elem.find('w:sectPr', namespaces)
                if sectPr_elem is not None:
                    pPr_elem.remove(sectPr_elem)

        # Insert dedicated section break paragraph before BAB I PENDAHULUAN
        bab1_idx_new = -1
        children_new = list(body)
        for idx, child in enumerate(children_new):
            if child.tag.endswith('p'):
                pPr = child.find('w:pPr', namespaces)
                pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                pStyle_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                text = "".join([t.text for t in child.iter(f'{{{ns_uri}}}t') if t.text])
                if pStyle_val == 'Heading1' and 'PENDAHULUAN' in text.upper():
                    bab1_idx_new = idx
                    break

        if bab1_idx_new != -1:
            p_sect = lxml.etree.Element(f'{{{ns_uri}}}p')
            pPr_sect = lxml.etree.Element(f'{{{ns_uri}}}pPr')
            
            if original_sectPr is not None:
                sectPr = original_sectPr
            else:
                sectPr = lxml.etree.Element(f'{{{ns_uri}}}sectPr')
            
            set_child_element(sectPr, 'type', {'val': 'nextPage'})
            set_child_element(sectPr, 'pgNumType', {'fmt': 'lowerRoman', 'start': '1'})
            set_child_element(sectPr, 'pgSz', {'w': '11906', 'h': '16838'})
            set_child_element(sectPr, 'pgMar', {
                'top': '1701', 'right': '1701', 'bottom': '1701', 'left': '2268',
                'header': '720', 'footer': '720', 'gutter': '0'
            })
            sort_element_children(sectPr, SECTPR_ORDER)
            
            pPr_sect.append(sectPr)
            sort_element_children(pPr_sect, PPR_ORDER)
            p_sect.append(pPr_sect)
            
            body.insert(bab1_idx_new, p_sect)
            print(f"Inserted dedicated section break paragraph before BAB I PENDAHULUAN at index {bab1_idx_new}")

        # Final section break (body section)
        final_sectPr = body.find('w:sectPr', namespaces)
        if final_sectPr is not None:
            pg_num_type = set_child_element(final_sectPr, 'pgNumType', {'fmt': 'decimal'})
            start_attr = f'{{{ns_uri}}}start'
            if start_attr in pg_num_type.attrib:
                del pg_num_type.attrib[start_attr]
            set_child_element(final_sectPr, 'pgSz', {'w': '11906', 'h': '16838'})
            set_child_element(final_sectPr, 'pgMar', {
                'top': '1701', 'right': '1701', 'bottom': '1701', 'left': '2268',
                'header': '720', 'footer': '720', 'gutter': '0'
            })
            sort_element_children(final_sectPr, SECTPR_ORDER)
            
        # Strip all dirty flags from fldChar elements to prevent Word 
        # from showing "update fields" dialog on open.
        for fldChar in body.iter(f'{{{ns_uri}}}fldChar'):
            if fldChar.get(f'{{{ns_uri}}}dirty'):
                del fldChar.attrib[f'{{{ns_uri}}}dirty']

        # Split and format nested TOC fields to remove the gap/jeda between Tabel 1.1 and Tabel 2.1
        idx_t = 0
        while idx_t < len(body):
            child = body[idx_t]
            if child.tag.endswith('p'):
                instrs = child.findall('.//w:instrText', namespaces)
                has_t1 = any('Tabel 1.' in instr.text for instr in instrs)
                has_t2 = any('Tabel 2.' in instr.text for instr in instrs)
                if has_t1 and has_t2:
                    children_elems = list(child)
                    p1_elems = []
                    p2_elems = []
                    found_second_begin = False
                    
                    for elem in children_elems:
                        if elem.tag.endswith('pPr'):
                            continue
                        
                        is_second_begin = False
                        if elem.tag.endswith('r'):
                            fldChar = elem.find('w:fldChar', namespaces)
                            if fldChar is not None and fldChar.get(f'{{{ns_uri}}}fldCharType') == 'begin':
                                if len(p1_elems) > 0:
                                    is_second_begin = True
                                    
                        if is_second_begin:
                            found_second_begin = True
                            
                        if not found_second_begin:
                            p1_elems.append(elem)
                        else:
                            p2_elems.append(elem)
                            
                    if found_second_begin and len(p2_elems) > 0:
                        for elem in list(child):
                            if not elem.tag.endswith('pPr'):
                                child.remove(elem)
                        for elem in p1_elems:
                            child.append(elem)
                            
                        # Build P2 (1pt spacing and font size)
                        p2 = lxml.etree.Element(f'{{{ns_uri}}}p')
                        pPr2 = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                        set_child_element(pPr2, 'pStyle', {'val': 'TableofFigures'})
                        set_child_element(pPr2, 'spacing', {'before': '0', 'after': '0', 'line': '20', 'lineRule': 'auto'})
                        
                        rPr2 = lxml.etree.Element(f'{{{ns_uri}}}rPr')
                        set_child_element(rPr2, 'sz', {'val': '2'})
                        set_child_element(rPr2, 'szCs', {'val': '2'})
                        pPr2.append(rPr2)
                        p2.append(pPr2)
                        
                        for elem in p2_elems:
                            if elem.tag.endswith('r'):
                                run_rPr = elem.find('w:rPr', namespaces)
                                if run_rPr is None:
                                    run_rPr = lxml.etree.Element(f'{{{ns_uri}}}rPr')
                                    elem.insert(0, run_rPr)
                                set_child_element(run_rPr, 'sz', {'val': '2'})
                                set_child_element(run_rPr, 'szCs', {'val': '2'})
                            p2.append(elem)
                            
                        body.insert(idx_t + 1, p2)
                        print("  Split nested Table of Figures fields (Tabel 1. and Tabel 2.) and formatted second field as 1pt.")
            idx_t += 1

        # Clean static lists and replace with dynamic fields
        children = list(body)
        daftar_gambar_idx = -1
        daftar_tabel_idx = -1
        
        for idx, child in enumerate(children):
            if child.tag.endswith('p'):
                text = "".join(child.itertext()).strip()
                pPr = child.find('w:pPr', namespaces)
                pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                style_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                if text == "DAFTAR GAMBAR" and style_val == "Heading1":
                    daftar_gambar_idx = idx
                elif text == "DAFTAR TABEL" and style_val == "Heading1":
                    daftar_tabel_idx = idx
                    
        # 1. Clean and insert dynamic Table of Figures
        if daftar_gambar_idx != -1 and daftar_tabel_idx != -1:
            print(f"Cleaning static DAFTAR GAMBAR list between {daftar_gambar_idx} and {daftar_tabel_idx}...")
            to_delete = []
            for idx in range(daftar_gambar_idx + 1, daftar_tabel_idx):
                child = children[idx]
                if child.tag.endswith('p'):
                    pPr = child.find('w:pPr', namespaces)
                    pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                    style_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                    text = "".join(child.itertext()).strip()
                    if style_val == 'TableofFigures' or not text:
                        to_delete.append(child)
            for child in to_delete:
                body.remove(child)
            print(f"Removed {len(to_delete)} elements from DAFTAR GAMBAR.")
            
            children = list(body)
            for idx, child in enumerate(children):
                if child.tag.endswith('p'):
                    text = "".join(child.itertext()).strip()
                    pPr = child.find('w:pPr', namespaces)
                    pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                    style_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                    if text == "DAFTAR GAMBAR" and style_val == "Heading1":
                        daftar_gambar_idx = idx
                        break
            for idx, child in enumerate(children):
                if child.tag.endswith('p'):
                    text = "".join(child.itertext()).strip()
                    pPr = child.find('w:pPr', namespaces)
                    pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                    style_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                    if text == "DAFTAR TABEL" and style_val == "Heading1":
                        daftar_tabel_idx = idx
                        break
                        
            insert_dynamic_toc_field(body, daftar_gambar_idx + 1, ' TOC \\h \\z \\c "Gambar" ', namespaces)
            
        # 2. Clean and insert Table of Tables
        children = list(body)
        for idx, child in enumerate(children):
            if child.tag.endswith('p'):
                text = "".join(child.itertext()).strip()
                pPr = child.find('w:pPr', namespaces)
                pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                style_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                if text == "DAFTAR TABEL" and style_val == "Heading1":
                    daftar_tabel_idx = idx
                    break
                    
        insertion_idx = -1
        if daftar_tabel_idx != -1:
            for idx in range(daftar_tabel_idx + 1, len(children)):
                child = children[idx]
                if child.tag.endswith('p'):
                    pPr = child.find('w:pPr', namespaces)
                    pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                    style_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                    if style_val == "Heading1":
                        insertion_idx = idx
                        break
                        
        if daftar_tabel_idx != -1 and insertion_idx != -1:
            print(f"Cleaning static DAFTAR TABEL list between {daftar_tabel_idx} and {insertion_idx}...")
            to_delete = []
            for idx in range(daftar_tabel_idx + 1, insertion_idx):
                child = children[idx]
                if child.tag.endswith('p'):
                    pPr = child.find('w:pPr', namespaces)
                    pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                    style_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                    text = "".join(child.itertext()).strip()
                    if style_val == 'TableofFigures' or not text:
                        to_delete.append(child)
            for child in to_delete:
                body.remove(child)
            print(f"Removed {len(to_delete)} elements from DAFTAR TABEL.")
            
            children = list(body)
            for idx, child in enumerate(children):
                if child.tag.endswith('p'):
                    text = "".join(child.itertext()).strip()
                    pPr = child.find('w:pPr', namespaces)
                    pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                    style_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                    if text == "DAFTAR TABEL" and style_val == "Heading1":
                        daftar_tabel_idx = idx
                        break
            for idx in range(daftar_tabel_idx + 1, len(children)):
                child = children[idx]
                if child.tag.endswith('p'):
                    pPr = child.find('w:pPr', namespaces)
                    pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                    style_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                    if style_val == "Heading1":
                        insertion_idx = idx
                        break
                        
            insert_dynamic_toc_field(body, daftar_tabel_idx + 1, ' TOC \\h \\z \\c "Tabel" ', namespaces)
            


        format_all_tables(root, namespaces)
        fix_whitespace_preservation(root)
        tree.write(doc_path, encoding='utf-8', xml_declaration=True)
        print("Updated document.xml.")

def fix_all_fonts_lxml(directory):
    W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'
    parser = lxml.etree.XMLParser(remove_blank_text=False)
    
    print(f"Normalizing fonts in {directory} recursively...")
    for root_dir, dirs, files in os.walk(directory):
        for file in files:
            if not (file.endswith('.xml') or file.endswith('.rels')): continue
            filepath = os.path.join(root_dir, file)
            try:
                tree = lxml.etree.parse(filepath, parser)
                root = tree.getroot()
            except:
                continue
                
            modified = False
            for elem in root.iter():
                tag_local = elem.tag.split('}')[-1]
                if tag_local == 'rFonts':
                    for attr in ['ascii', 'hAnsi', 'eastAsia', 'cs']:
                        full_attr = f'{{{W_NS}}}{attr}'
                        val = elem.get(full_attr)
                        if val and val not in ['Symbol', 'Wingdings', 'Courier New', 'Times New Roman']:
                            elem.set(full_attr, 'Times New Roman')
                            modified = True
                    theme_attrs = ['asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme']
                    has_theme = False
                    for attr in theme_attrs:
                        full_attr = f'{{{W_NS}}}{attr}'
                        if elem.get(full_attr) is not None:
                            elem.attrib.pop(full_attr)
                            has_theme = True
                            modified = True
                    if has_theme:
                        for attr in ['ascii', 'hAnsi', 'eastAsia', 'cs']:
                            full_attr = f'{{{W_NS}}}{attr}'
                            val = elem.get(full_attr)
                            if not val or val not in ['Symbol', 'Wingdings', 'Courier New']:
                                elem.set(full_attr, 'Times New Roman')
                                modified = True
                elif tag_local in ['latin', 'ea', 'cs'] and elem.tag.startswith(f'{{{A_NS}}}'):
                    val = elem.get('typeface')
                    if val and val not in ['Symbol', 'Wingdings', 'Courier New', 'Times New Roman']:
                        elem.set('typeface', 'Times New Roman')
                        modified = True
                elif 'typeface' in elem.attrib:
                    val = elem.attrib['typeface']
                    if val and val not in ['Symbol', 'Wingdings', 'Courier New', 'Times New Roman']:
                        elem.attrib['typeface'] = 'Times New Roman'
                        modified = True
                        
            if modified:
                try:
                    tree.write(filepath, encoding='utf-8', xml_declaration=True)
                    print(f"  Fixed fonts in {os.path.relpath(filepath, directory)}")
                except Exception as e:
                    print(f"  Error writing {file}: {e}")

def force_field_update(unpacked_dir):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    settings_path = os.path.join(unpacked_dir, 'word', 'settings.xml')
    if os.path.exists(settings_path):
        tree = lxml.etree.parse(settings_path)
        root = tree.getroot()
        update_fields = root.find('w:updateFields', namespaces)
        if update_fields is not None:
            root.remove(update_fields)
            tree.write(settings_path, encoding='utf-8', xml_declaration=True, standalone=True)
            print("Removed updateFields from settings.xml to prevent popup.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python format_ta_proyek.py <unpacked_dir>")
        sys.exit(1)
    unpacked_dir = sys.argv[1]
    format_document_xmls(unpacked_dir)
    force_field_update(unpacked_dir)
    fix_all_fonts_lxml(unpacked_dir)
