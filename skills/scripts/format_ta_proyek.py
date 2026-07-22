import lxml.etree
import copy
import hashlib
import os
import re
import sys

# Canonical UPNVJ FIK page geometry. OOXML stores these values in twips
# (1 cm ~= 567 twips): A4 portrait, 4 cm left, and 3 cm on the other sides.
# Keep layout writes and width calculations tied to these constants so a future
# formatting change cannot silently make tables use different page geometry.
A4_PAGE_WIDTH_DXA = 11906
A4_PAGE_HEIGHT_DXA = 16838
MARGIN_LEFT_DXA = 2268
MARGIN_TOP_DXA = 1701
MARGIN_RIGHT_DXA = 1701
MARGIN_BOTTOM_DXA = 1701
HEADER_DISTANCE_DXA = 720
FOOTER_DISTANCE_DXA = 720

OFFICE_REL_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PACKAGE_REL_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'
CONTENT_TYPES_NS = 'http://schemas.openxmlformats.org/package/2006/content-types'
HEADER_REL_TYPE = OFFICE_REL_NS + '/header'
FOOTER_REL_TYPE = OFFICE_REL_NS + '/footer'
HEADER_CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml'
FOOTER_CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml'

# For w:spacing with lineRule="auto", Word stores line height in 240ths of a
# line. The corrected campus requirement is 1.15 lines: 1.15 * 240 = 276.
MAIN_LINE_SPACING_AUTO = '276'


def main_line_spacing_attrs(before='0', after='0'):
    """Return canonical OOXML spacing attributes for body/heading paragraphs."""
    return {
        'before': str(before),
        'after': str(after),
        'line': MAIN_LINE_SPACING_AUTO,
        'lineRule': 'auto',
    }


def make_explicit_page_break_paragraph(namespaces):
    """Create a standalone page break that survives Word field regeneration."""
    ns_uri = namespaces['w']
    paragraph = lxml.etree.Element(f'{{{ns_uri}}}p')
    p_pr = lxml.etree.SubElement(paragraph, f'{{{ns_uri}}}pPr')
    set_child_element(p_pr, 'pStyle', {'val': 'Normal'})
    set_child_element(p_pr, 'spacing', main_line_spacing_attrs())
    sort_element_children(p_pr, PPR_ORDER)
    run = lxml.etree.SubElement(paragraph, f'{{{ns_uri}}}r')
    lxml.etree.SubElement(
        run, f'{{{ns_uri}}}br', {f'{{{ns_uri}}}type': 'page'}
    )
    return paragraph

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
_SEMANTIC_CAPTION_PATTERN = re.compile(
    r"^\[(FIGCAPTION|TABLECAPTION):"
    r"(?:([a-z0-9][a-z0-9_-]*)\|)?(.+)\]$"
)
_SEMANTIC_REFERENCE_PATTERN = re.compile(
    r"\[(FIGREF|TABREF):([a-z0-9][a-z0-9_-]*)\]"
)


def parse_semantic_caption(text):
    """Return ``(label, semantic_id, description)`` for a caption token.

    The merge parser binds the source-only marker to its adjacent caption and
    emits ``[FIGCAPTION:id|Description]`` or
    ``[TABLECAPTION:id|Description]`` in intermediate OOXML.  Accepting the
    public unbound form as well keeps this helper useful for focused tests,
    while the merge validator is responsible for rejecting missing IDs in a
    real build.
    """
    if not text:
        return None
    match = _SEMANTIC_CAPTION_PATTERN.fullmatch(str(text).strip())
    if not match:
        return None
    label = "Gambar" if match.group(1) == "FIGCAPTION" else "Tabel"
    return label, match.group(2), match.group(3).strip()


def make_crossref_bookmark(label, semantic_id):
    """Build a deterministic, Word-safe bookmark name (maximum 40 chars)."""
    prefix = "fig" if str(label).lower() == "gambar" else "tbl"
    raw_id = str(semantic_id).lower()
    safe_id = re.sub(r"[^a-z0-9_]", "_", raw_id)
    base = f"{prefix}_{safe_id}"
    if len(base) <= 40 and safe_id == raw_id:
        return base
    digest = hashlib.sha1(f"{prefix}_{raw_id}".encode("utf-8")).hexdigest()[:8]
    return f"{base[:31]}_{digest}"


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
    semantic = parse_semantic_caption(s)
    if semantic is not None:
        label, _semantic_id, desc = semantic
        return (label, None, desc)
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

# Official CT_TblPr child order from the OOXML schema.
TBLPR_ORDER = [
    'tblStyle', 'tblpPr', 'tblOverlap', 'bidiVisual',
    'tblStyleRowBandSize', 'tblStyleColBandSize', 'tblW', 'jc',
    'tblCellSpacing', 'tblInd', 'tblBorders', 'shd', 'tblLayout',
    'tblCellMar', 'tblLook', 'tblCaption', 'tblDescription', 'tblPrChange'
]

# Official CT_TcPr child order from the OOXML schema.
TCPR_ORDER = [
    'cnfStyle', 'tcW', 'gridSpan', 'hMerge', 'vMerge', 'tcBorders', 'shd',
    'noWrap', 'tcMar', 'textDirection', 'tcFitText', 'vAlign', 'hideMark',
    'headers', 'cellIns', 'cellDel', 'cellMerge', 'tcPrChange'
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


def build_page_number_part(kind, alignment, include_page):
    """Build a deterministic header/footer part for one page-number role."""
    if kind not in ('header', 'footer'):
        raise ValueError("kind must be 'header' or 'footer'")
    if alignment not in ('left', 'center', 'right'):
        raise ValueError("alignment must be left, center, or right")

    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    root_tag = 'hdr' if kind == 'header' else 'ftr'
    style_id = 'Header' if kind == 'header' else 'Footer'
    root = lxml.etree.Element(f'{{{ns_uri}}}{root_tag}', nsmap={'w': ns_uri})
    p = lxml.etree.SubElement(root, f'{{{ns_uri}}}p')
    p_pr = lxml.etree.SubElement(p, f'{{{ns_uri}}}pPr')
    set_child_element(p_pr, 'pStyle', {'val': style_id})
    set_child_element(p_pr, 'jc', {'val': alignment})
    sort_element_children(p_pr, PPR_ORDER)

    if include_page:
        for field_type in ('begin',):
            run = lxml.etree.SubElement(p, f'{{{ns_uri}}}r')
            set_child_element(run, 'fldChar', {'fldCharType': field_type})

        instr_run = lxml.etree.SubElement(p, f'{{{ns_uri}}}r')
        instr = set_child_element(instr_run, 'instrText', {'space': 'preserve'})
        instr.text = ' PAGE '

        separate_run = lxml.etree.SubElement(p, f'{{{ns_uri}}}r')
        set_child_element(separate_run, 'fldChar', {'fldCharType': 'separate'})

        value_run = lxml.etree.SubElement(p, f'{{{ns_uri}}}r')
        value_r_pr = lxml.etree.SubElement(value_run, f'{{{ns_uri}}}rPr')
        set_child_element(
            value_r_pr,
            'rFonts',
            {'ascii': 'Times New Roman', 'hAnsi': 'Times New Roman'},
        )
        set_child_element(value_r_pr, 'sz', {'val': '24'})
        set_child_element(value_r_pr, 'szCs', {'val': '24'})
        value_text = lxml.etree.SubElement(value_run, f'{{{ns_uri}}}t')
        value_text.text = '1'

        end_run = lxml.etree.SubElement(p, f'{{{ns_uri}}}r')
        set_child_element(end_run, 'fldChar', {'fldCharType': 'end'})

    return root


def ensure_page_number_parts(unpacked_dir):
    """Create/reuse page-number parts and return their document rIds.

    Fixed role-based part names make this helper idempotent. The parts are
    intentionally explicit so Word cannot inherit the Roman footer into an
    Arabic body section through an implicit "Link to Previous" relationship.
    """
    specs = {
        'body_default_header': (
            'ta-header-body-default.xml', 'header', 'right', True,
            HEADER_REL_TYPE, HEADER_CONTENT_TYPE,
        ),
        'blank_header': (
            'ta-header-blank.xml', 'header', 'right', False,
            HEADER_REL_TYPE, HEADER_CONTENT_TYPE,
        ),
        'front_default_footer': (
            'ta-footer-front-default.xml', 'footer', 'right', True,
            FOOTER_REL_TYPE, FOOTER_CONTENT_TYPE,
        ),
        'body_first_footer': (
            'ta-footer-body-first.xml', 'footer', 'center', True,
            FOOTER_REL_TYPE, FOOTER_CONTENT_TYPE,
        ),
        'blank_footer': (
            'ta-footer-blank.xml', 'footer', 'center', False,
            FOOTER_REL_TYPE, FOOTER_CONTENT_TYPE,
        ),
    }
    rels_path = os.path.join(unpacked_dir, 'word', '_rels', 'document.xml.rels')
    content_types_path = os.path.join(unpacked_dir, '[Content_Types].xml')
    parser = lxml.etree.XMLParser(remove_blank_text=False)
    rels_tree = lxml.etree.parse(rels_path, parser)
    rels_root = rels_tree.getroot()
    content_types_tree = lxml.etree.parse(content_types_path, parser)
    content_types_root = content_types_tree.getroot()

    numeric_ids = []
    for relationship in rels_root:
        rid = relationship.get('Id', '')
        if rid.startswith('rId') and rid[3:].isdigit():
            numeric_ids.append(int(rid[3:]))
    next_rid = max(numeric_ids, default=0) + 1

    reference_ids = {}
    for role, (target, kind, alignment, include_page, rel_type, content_type) in specs.items():
        part_path = os.path.join(unpacked_dir, 'word', target)
        part_root = build_page_number_part(kind, alignment, include_page)
        lxml.etree.ElementTree(part_root).write(
            part_path,
            encoding='utf-8',
            xml_declaration=True,
            standalone=True,
        )

        relationship = next(
            (
                item for item in rels_root
                if item.get('Type') == rel_type and item.get('Target') == target
            ),
            None,
        )
        if relationship is None:
            rid = f'rId{next_rid}'
            next_rid += 1
            relationship = lxml.etree.SubElement(
                rels_root,
                f'{{{PACKAGE_REL_NS}}}Relationship',
                Id=rid,
                Type=rel_type,
                Target=target,
            )
        reference_ids[role] = relationship.get('Id')

        part_name = f'/word/{target}'
        override = next(
            (
                item for item in content_types_root
                if item.tag == f'{{{CONTENT_TYPES_NS}}}Override'
                and item.get('PartName') == part_name
            ),
            None,
        )
        if override is None:
            override = lxml.etree.SubElement(
                content_types_root,
                f'{{{CONTENT_TYPES_NS}}}Override',
            )
            override.set('PartName', part_name)
        override.set('ContentType', content_type)

    rels_tree.write(rels_path, encoding='utf-8', xml_declaration=True, standalone=True)
    content_types_tree.write(
        content_types_path,
        encoding='utf-8',
        xml_declaration=True,
        standalone=True,
    )
    return reference_ids


def _is_numbered_chapter_heading(paragraph, namespaces):
    """True for a numbered Heading1 chapter, excluding front-matter headings."""
    ns_uri = namespaces['w']
    p_pr = paragraph.find('w:pPr', namespaces)
    if p_pr is None:
        return False
    p_style = p_pr.find('w:pStyle', namespaces)
    if p_style is None or p_style.get(f'{{{ns_uri}}}val') != 'Heading1':
        return False
    num_pr = p_pr.find('w:numPr', namespaces)
    if num_pr is None:
        return False
    ilvl = num_pr.find('w:ilvl', namespaces)
    return ilvl is None or ilvl.get(f'{{{ns_uri}}}val', '0') == '0'


def _apply_page_number_section(sect_pr, reference_ids, *, front, start, next_page):
    """Apply header/footer roles and numbering rules to one section."""
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    for tag_name in ('headerReference', 'footerReference'):
        for existing in list(sect_pr.findall(f'{{{ns_uri}}}{tag_name}')):
            sect_pr.remove(existing)

    if front:
        refs = (
            ('headerReference', 'default', reference_ids['blank_header']),
            ('headerReference', 'first', reference_ids['blank_header']),
            ('footerReference', 'default', reference_ids['front_default_footer']),
            ('footerReference', 'first', reference_ids['blank_footer']),
        )
        number_format = 'lowerRoman'
    else:
        refs = (
            ('headerReference', 'default', reference_ids['body_default_header']),
            ('headerReference', 'first', reference_ids['blank_header']),
            ('footerReference', 'default', reference_ids['blank_footer']),
            ('footerReference', 'first', reference_ids['body_first_footer']),
        )
        number_format = 'decimal'

    for tag_name, ref_type, rid in refs:
        ref = lxml.etree.Element(f'{{{ns_uri}}}{tag_name}')
        ref.set(f'{{{ns_uri}}}type', ref_type)
        ref.set(f'{{{OFFICE_REL_NS}}}id', rid)
        sect_pr.append(ref)

    if next_page:
        set_child_element(sect_pr, 'type', {'val': 'nextPage'})
    else:
        type_element = sect_pr.find(f'{{{ns_uri}}}type')
        if type_element is not None:
            sect_pr.remove(type_element)

    pg_num_type = set_child_element(sect_pr, 'pgNumType', {'fmt': number_format})
    start_attr = f'{{{ns_uri}}}start'
    if start is None:
        pg_num_type.attrib.pop(start_attr, None)
    else:
        pg_num_type.set(start_attr, str(start))
    set_child_element(sect_pr, 'titlePg', {})
    apply_upnvj_page_layout(sect_pr)
    sort_element_children(sect_pr, SECTPR_ORDER)


def configure_report_sections(
    body,
    namespaces,
    original_sect_pr,
    reference_ids,
    chapter_paragraphs=None,
):
    """Create one front-matter section and one section per numbered BAB.

    The first page of every BAB uses a centered footer page number, later pages
    use a right-aligned header, Roman front matter uses a right-aligned footer,
    and the first Arabic section explicitly restarts at page 1.
    """
    ns_uri = namespaces['w']
    body_final = body.find('w:sectPr', namespaces)
    source_sect_pr = (
        original_sect_pr if original_sect_pr is not None else body_final
    )
    template = copy.deepcopy(source_sect_pr)
    if template is None:
        template = lxml.etree.Element(f'{{{ns_uri}}}sectPr')

    for paragraph in body.findall('w:p', namespaces):
        p_pr = paragraph.find('w:pPr', namespaces)
        sect_pr = p_pr.find('w:sectPr', namespaces) if p_pr is not None else None
        if sect_pr is not None:
            p_pr.remove(sect_pr)
    if body_final is not None:
        body.remove(body_final)

    children = list(body)
    chapters = [
        paragraph for paragraph in (chapter_paragraphs or [])
        if paragraph in children
    ]
    if not chapters:
        chapters = [
            child for child in children
            if child.tag == f'{{{ns_uri}}}p'
            and _is_numbered_chapter_heading(child, namespaces)
        ]
    if not chapters:
        chapters = [
            child for child in children
            if child.tag == f'{{{ns_uri}}}p'
            and (_paragraph_style(child, namespaces) or '') == 'Heading1'
            and 'PENDAHULUAN' in _paragraph_text(child, namespaces).upper()
        ][:1]
    if not chapters:
        raise RuntimeError('Cannot configure page numbering: no BAB heading found.')

    chapter_set = set(chapters)
    for child in children:
        body.remove(child)

    started_chapters = 0
    for child in children:
        if child in chapter_set:
            break_paragraph = lxml.etree.Element(f'{{{ns_uri}}}p')
            break_p_pr = lxml.etree.SubElement(
                break_paragraph,
                f'{{{ns_uri}}}pPr',
            )
            section_properties = copy.deepcopy(template)
            if started_chapters == 0:
                _apply_page_number_section(
                    section_properties,
                    reference_ids,
                    front=True,
                    start=1,
                    next_page=True,
                )
            else:
                _apply_page_number_section(
                    section_properties,
                    reference_ids,
                    front=False,
                    start=1 if started_chapters == 1 else None,
                    next_page=True,
                )
            break_p_pr.append(section_properties)
            sort_element_children(break_p_pr, PPR_ORDER)
            body.append(break_paragraph)
            started_chapters += 1
        body.append(child)

    final_section = copy.deepcopy(template)
    _apply_page_number_section(
        final_section,
        reference_ids,
        front=False,
        start=1 if started_chapters == 1 else None,
        next_page=False,
    )
    body.append(final_section)
    return started_chapters + 1


def apply_upnvj_page_layout(sect_pr):
    """Apply the canonical A4 + 4/3/3/3 cm layout to one ``w:sectPr``.

    The helper is intentionally idempotent and preserves unrelated section
    properties such as header/footer references and page-numbering settings.
    """
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    pg_sz = set_child_element(sect_pr, 'pgSz', {
        'w': str(A4_PAGE_WIDTH_DXA),
        'h': str(A4_PAGE_HEIGHT_DXA),
    })
    # A stale landscape flag can override otherwise-correct portrait dimensions.
    orient_attr = f'{{{ns_uri}}}orient'
    if orient_attr in pg_sz.attrib:
        del pg_sz.attrib[orient_attr]

    set_child_element(sect_pr, 'pgMar', {
        'top': str(MARGIN_TOP_DXA),
        'right': str(MARGIN_RIGHT_DXA),
        'bottom': str(MARGIN_BOTTOM_DXA),
        'left': str(MARGIN_LEFT_DXA),
        'header': str(HEADER_DISTANCE_DXA),
        'footer': str(FOOTER_DISTANCE_DXA),
        'gutter': '0',
    })
    sort_element_children(sect_pr, SECTPR_ORDER)
    return sect_pr

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
    
    set_child_element(pPr, 'spacing', main_line_spacing_attrs())
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


REPORT_BLACK_STYLE_IDS = {
    'Heading1',
    'Heading2',
    'Heading3',
    'Caption',
    'FrontMatterHeading',
    'taappendixheading',
    'TOC1',
    'TOC2',
    'TOC3',
    'TOC9',
    'TableofFigures',
}


def ensure_report_style_colors(styles_root):
    """Paksa hierarki akademik dan caption menggunakan teks hitam.

    Style bawaan Word membawa warna tema biru pada Heading dan Caption.
    Atribut tema harus dihapus juga agar ``w:val=000000`` tidak dikalahkan
    oleh ``themeColor`` saat dokumen dibuka atau field diperbarui di Word.
    """
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    for style in styles_root.findall('w:style', namespaces):
        style_id = style.get(f'{{{ns_uri}}}styleId')
        if style_id not in REPORT_BLACK_STYLE_IDS:
            continue
        r_pr = style.find('w:rPr', namespaces)
        if r_pr is None:
            r_pr = lxml.etree.Element(f'{{{ns_uri}}}rPr')
            style.append(r_pr)
        color = set_child_element(r_pr, 'color', {'val': '000000'})
        for attribute in ('themeColor', 'themeTint', 'themeShade'):
            color.attrib.pop(f'{{{ns_uri}}}{attribute}', None)
        sort_element_children(style, STYLE_ORDER)


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

def clean_bibliography_sdt(sdt_elem, entries=None, draft_path="Tugas_Akhir_Draft.md"):
    """Fill the bibliography SDT from the draft '# DAFTAR PUSTAKA' (Option B, R1).

    The draft is the single source of truth: references are NO LONGER hardcoded
    (R1.1). ``entries`` may be a precomputed list of ReferenceEntry; when None
    they are parsed from ``draft_path`` via ``parse_bibliography_entries``.

    Each entry is rendered with the baseline paragraph style (R1.3): pStyle
    Normal; ind left=567 hanging=567; spacing before=0/after=120/line=240/
    lineRule=auto; jc=both. Italic spans (``*...*`` in the draft) become
    ``w:i``/``w:iCs`` runs (R1.2); entry order follows the draft (R1.4).

    If the section is missing or empty (R1.8) the function prints a non-fatal
    [WARN] and leaves the SDT untouched -- it never writes fake entries, so the
    body-paragraph references produced by the merge stay intact.
    """
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    sdtContent = sdt_elem.find('w:sdtContent', namespaces)
    if sdtContent is None:
        return

    section_found = True
    if entries is None:
        try:
            from merge_draft_to_docx import parse_bibliography_entries
        except ImportError:
            _here = os.path.dirname(os.path.abspath(__file__))
            if _here not in sys.path:
                sys.path.insert(0, _here)
            from merge_draft_to_docx import parse_bibliography_entries
        result = parse_bibliography_entries(draft_path)
        entries = list(result)
        section_found = getattr(result, 'section_found', bool(entries))

    if not entries:
        # R1.8: never write fake entries. Leave the SDT (and the body-paragraph
        # references produced by the merge) untouched.
        if not section_found:
            print("[WARN] sumber Daftar_Pustaka tidak ditemukan: bagian "
                  "'# DAFTAR PUSTAKA' tidak ada pada Draf.")
        else:
            print("[WARN] sumber Daftar_Pustaka kosong: bagian "
                  "'# DAFTAR PUSTAKA' tidak memuat entri.")
        return

    # Draft entries exist -> replace SDT content with draft-sourced references.
    for child in list(sdtContent):
        sdtContent.remove(child)

    for entry in entries:
        p = lxml.etree.Element(f'{{{ns_uri}}}p')
        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
        set_child_element(pPr, 'pStyle', {'val': 'Normal'})
        set_child_element(pPr, 'ind', {'left': '567', 'hanging': '567'})
        set_child_element(pPr, 'spacing', {'before': '0', 'after': '120', 'line': '240', 'lineRule': 'auto'})
        set_child_element(pPr, 'jc', {'val': 'both'})
        sort_element_children(pPr, PPR_ORDER)
        p.append(pPr)

        for text, is_italic in entry.spans:
            r = lxml.etree.Element(f'{{{ns_uri}}}r')
            if is_italic:
                rPr = lxml.etree.Element(f'{{{ns_uri}}}rPr')
                set_child_element(rPr, 'i', {})
                set_child_element(rPr, 'iCs', {})
                r.append(rPr)
            t = lxml.etree.Element(f'{{{ns_uri}}}t')
            t.text = text
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            r.append(t)
            p.append(r)

        sdtContent.append(p)
    print(f"Replaced bibliography entries inside SDT from draft ({len(entries)} entries).")

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

def compute_printable_width(root, namespaces):
    """Return the printable page width in dxa (twips) from the document's page setup.

    Reads ``pgSz@w`` minus ``pgMar@left`` and ``pgMar@right`` from the body
    ``sectPr`` (``w:body/w:sectPr``, falling back to the last ``sectPr`` in the
    body when no direct child ``sectPr`` exists). Each value falls back to a safe
    default matching the canonical UPNVJ page setup (``w=11906``,
    ``left=2268``, ``right=1701`` -> ``7937`` dxa) when it is missing or
    unparseable.

    This helper is strictly read-only: it never mutates ``sectPr`` (or any other
    element). It only inspects attributes to compute the printable width.
    """
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    DEFAULT_W = A4_PAGE_WIDTH_DXA
    DEFAULT_LEFT = MARGIN_LEFT_DXA
    DEFAULT_RIGHT = MARGIN_RIGHT_DXA

    # Locate the section properties: prefer the body's direct-child sectPr,
    # otherwise fall back to the last sectPr found anywhere in the body.
    sectPr = None
    body = root.find('w:body', namespaces)
    search_scope = body if body is not None else root
    if search_scope is not None:
        sectPr = search_scope.find('w:sectPr', namespaces)
        if sectPr is None:
            sect_list = search_scope.findall('.//w:sectPr', namespaces)
            if sect_list:
                sectPr = sect_list[-1]

    def _parse_attr(elem, attr, default):
        if elem is None:
            return default
        raw = elem.get(f'{{{ns_uri}}}{attr}')
        if raw is None:
            return default
        try:
            return int(raw)
        except (TypeError, ValueError):
            return default

    pgSz = sectPr.find('w:pgSz', namespaces) if sectPr is not None else None
    pgMar = sectPr.find('w:pgMar', namespaces) if sectPr is not None else None

    width = _parse_attr(pgSz, 'w', DEFAULT_W)
    left = _parse_attr(pgMar, 'left', DEFAULT_LEFT)
    right = _parse_attr(pgMar, 'right', DEFAULT_RIGHT)

    printable = width - left - right
    if printable <= 0:
        # Degenerate/unusable geometry -> fall back to the known-good default.
        return DEFAULT_W - DEFAULT_LEFT - DEFAULT_RIGHT
    return printable


def count_table_columns(tbl, namespaces):
    """Return the structural column count of a ``w:tbl``.

    The count is derived purely from structure (never from cell text):

      * when a ``w:tblGrid`` with ``w:gridCol`` children exists, the count is
        ``len(tblGrid/gridCol)``;
      * otherwise it is the maximum number of grid columns spanned by any row,
        i.e. ``max`` over rows of ``sum(w:tc/w:tcPr/w:gridSpan@val)`` (a cell
        without ``gridSpan`` counts as one column).

    Returns ``0`` for a table with no grid and no rows/cells.
    """
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

    tblGrid = tbl.find('w:tblGrid', namespaces)
    if tblGrid is not None:
        cols = tblGrid.findall('w:gridCol', namespaces)
        if cols:
            return len(cols)

    max_cols = 0
    for row in tbl.findall('w:tr', namespaces):
        span_total = 0
        for tc in row.findall('w:tc', namespaces):
            span = 1
            tcPr = tc.find('w:tcPr', namespaces)
            if tcPr is not None:
                gridSpan = tcPr.find('w:gridSpan', namespaces)
                if gridSpan is not None:
                    raw = gridSpan.get(f'{{{ns_uri}}}val')
                    try:
                        parsed = int(raw)
                        if parsed > 0:
                            span = parsed
                    except (TypeError, ValueError):
                        span = 1
            span_total += span
        if span_total > max_cols:
            max_cols = span_total
    return max_cols


def column_ratios_from_grid(tbl, namespaces, n_cols):
    """Return a list of ``n_cols`` column proportions (summing to 1.0).

    When the table's existing ``w:tblGrid`` has exactly ``n_cols`` ``w:gridCol``
    entries whose widths are parseable and sum to a positive value, those widths
    are used as proportions (each divided by their total). Otherwise the width
    is split evenly (``1/n_cols`` per column).

    This helper is read-only and structure-driven: it never inspects cell text
    and never hardcodes a width by column count. Returns ``[]`` when
    ``n_cols <= 0``.
    """
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

    if n_cols <= 0:
        return []

    even = [1.0 / n_cols] * n_cols

    tblGrid = tbl.find('w:tblGrid', namespaces)
    if tblGrid is None:
        return even

    cols = tblGrid.findall('w:gridCol', namespaces)
    if len(cols) != n_cols:
        return even

    widths = []
    for gc in cols:
        raw = gc.get(f'{{{ns_uri}}}w')
        try:
            value = float(raw)
        except (TypeError, ValueError):
            return even
        if value < 0:
            return even
        widths.append(value)

    total = sum(widths)
    if total <= 0:
        return even
    return [w / total for w in widths]


def distribute_width(printable, ratios, overrides=None):
    """Distribute ``printable`` dxa across columns, summing exactly to ``printable``.

    ``ratios`` is a per-column proportion list (e.g. from
    :func:`column_ratios_from_grid`). An optional ``overrides`` proportion list
    replaces ``ratios`` when it is supplied, has the same length, and sums to a
    positive value -- letting callers pass non-hardcoded per-column ratios
    without keying anything to cell text or a specific column count.

    Each column width is ``floor(printable * ratio / sum(ratios))``; the leftover
    remainder (so the total is exact) is added to the last column. Handles
    ``n_cols == 1`` (the single column receives the full ``printable``). Returns
    ``[]`` for an empty ratio list.
    """
    effective = list(ratios)

    if overrides is not None:
        overrides = list(overrides)
        if len(overrides) == len(effective) and sum(overrides) > 0 \
                and all(o >= 0 for o in overrides):
            effective = overrides

    n = len(effective)
    if n == 0:
        return []

    total = sum(effective)
    if total <= 0:
        # Degenerate ratios -> fall back to an even split.
        effective = [1.0 / n] * n
        total = 1.0

    widths = [int(printable * r / total) for r in effective]
    widths[-1] += printable - sum(widths)
    return widths


def format_all_tables(root, namespaces):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

    def qn(tag):
        return f'{{{ns_uri}}}{tag}'

    # Compute the printable width once from the document's own page setup.
    printable = compute_printable_width(root, namespaces)

    # Consistent, content-agnostic borders and cell padding for every table.
    BORDER_SIDES = ('top', 'left', 'bottom', 'right', 'insideH', 'insideV')
    BORDER_ATTRS = {'val': 'single', 'sz': '4', 'color': '000000'}
    CELL_MARGIN_DXA = {'top': '0', 'left': '108', 'bottom': '0', 'right': '108'}

    tbl_count = 0
    for tbl in root.findall('.//w:tbl', namespaces):
        tbl_count += 1
        tblPr = tbl.find('w:tblPr', namespaces)
        if tblPr is None:
            tblPr = lxml.etree.Element(qn('tblPr'))
            tbl.insert(0, tblPr)

        # Center table horizontally (preserved behavior).
        set_child_element(tblPr, 'jc', {'val': 'center'})

        rows = tbl.findall('w:tr', namespaces)
        if not rows:
            # Nothing structural to size; keep any tblPr children schema-valid.
            sort_element_children(tblPr, TBLPR_ORDER)
            continue

        # --- Structure-driven width fitting (no content probing) --------------
        n_cols = count_table_columns(tbl, namespaces)
        if n_cols <= 0:
            n_cols = 1
        ratios = column_ratios_from_grid(tbl, namespaces, n_cols)
        col_widths = distribute_width(printable, ratios)

        # Total preferred width + fixed layout so the table fits the page.
        set_child_element(tblPr, 'tblW', {'w': str(printable), 'type': 'dxa'})
        set_child_element(tblPr, 'tblLayout', {'type': 'fixed'})

        # Consistent borders (all sides + insideH/insideV) and cell padding.
        tblBorders = set_child_element(tblPr, 'tblBorders')
        for side in BORDER_SIDES:
            set_child_element(tblBorders, side, BORDER_ATTRS)
        tblCellMar = set_child_element(tblPr, 'tblCellMar')
        for side in ('top', 'left', 'bottom', 'right'):
            set_child_element(tblCellMar, side, {'w': CELL_MARGIN_DXA[side], 'type': 'dxa'})

        # Keep tblPr children in valid OOXML schema order.
        sort_element_children(tblPr, TBLPR_ORDER)

        # Rewrite tblGrid so gridCol widths equal the distributed widths.
        tblGrid = tbl.find('w:tblGrid', namespaces)
        if tblGrid is None:
            tblGrid = lxml.etree.Element(qn('tblGrid'))
            tbl.insert(list(tbl).index(tblPr) + 1, tblGrid)
        for gc in list(tblGrid):
            tblGrid.remove(gc)
        for w in col_widths:
            gc = lxml.etree.SubElement(tblGrid, qn('gridCol'))
            gc.set(qn('w'), str(w))

        # --- Per-row / per-cell formatting ------------------------------------
        for row_idx, row in enumerate(rows):
            is_header = (row_idx == 0)

            # Mark the first row as a repeating header row.
            if is_header:
                trPr = row.find('w:trPr', namespaces)
                if trPr is None:
                    trPr = lxml.etree.Element(qn('trPr'))
                    row.insert(0, trPr)
                set_child_element(trPr, 'tblHeader', {'val': 'true'})

            col_cursor = 0
            for cell in row.findall('w:tc', namespaces):
                tcPr = cell.find('w:tcPr', namespaces)
                if tcPr is None:
                    tcPr = lxml.etree.Element(qn('tcPr'))
                    cell.insert(0, tcPr)

                # Determine how many grid columns this cell spans.
                span = 1
                gridSpan = tcPr.find('w:gridSpan', namespaces)
                if gridSpan is not None:
                    raw = gridSpan.get(qn('val'))
                    try:
                        parsed = int(raw)
                        if parsed > 0:
                            span = parsed
                    except (TypeError, ValueError):
                        span = 1

                # Cell width = sum of the widths of the columns it spans.
                start = min(col_cursor, len(col_widths))
                end = min(col_cursor + span, len(col_widths))
                cell_width = sum(col_widths[start:end])
                if cell_width <= 0 and col_widths:
                    cell_width = col_widths[min(col_cursor, len(col_widths) - 1)]
                col_cursor += span
                set_child_element(tcPr, 'tcW', {'w': str(cell_width), 'type': 'dxa'})

                # Vertical alignment.
                if is_header:
                    set_child_element(tcPr, 'vAlign', {'val': 'center'})
                else:
                    set_child_element(tcPr, 'vAlign', {'val': 'top'})

                # Keep tcPr children in valid OOXML schema order.
                sort_element_children(tcPr, TCPR_ORDER)

                # Process cell paragraphs.
                for p in cell.findall('w:p', namespaces):
                    pPr = p.find('w:pPr', namespaces)
                    if pPr is None:
                        pPr = lxml.etree.Element(qn('pPr'))
                        p.insert(0, pPr)

                    # Horizontal alignment: header centered, body left.
                    if is_header:
                        set_child_element(pPr, 'jc', {'val': 'center'})
                    else:
                        set_child_element(pPr, 'jc', {'val': 'left'})

                    # Clear indentation and keep pPr children ordered.
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


def caption_run_properties(ns_uri, *, bold=False):
    """Return deterministic Times New Roman 12 pt properties for a caption run."""
    r_pr = lxml.etree.Element(f'{{{ns_uri}}}rPr')
    set_child_element(r_pr, 'rFonts', {
        'ascii': 'Times New Roman',
        'hAnsi': 'Times New Roman',
        'eastAsia': 'Times New Roman',
        'cs': 'Times New Roman',
    })
    set_child_element(r_pr, 'b', {} if bold else {'val': '0'})
    set_child_element(r_pr, 'bCs', {} if bold else {'val': '0'})
    set_child_element(r_pr, 'i', {'val': '0'})
    set_child_element(r_pr, 'iCs', {'val': '0'})
    set_child_element(r_pr, 'color', {'val': '000000'})
    set_child_element(r_pr, 'sz', {'val': '24'})
    set_child_element(r_pr, 'szCs', {'val': '24'})
    return r_pr


def format_caption_paragraph_clean(
        p, label, prefix, seq_name, default_val, desc, namespaces,
        semantic_bookmark=None, semantic_bookmark_id=None):
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
    
    # Extract pre-existing bookmarks (resilient to namespaces).  When this
    # function is re-run, do not preserve the semantic bookmark that is about
    # to be rebuilt around the visible caption number.
    bookmarks = []
    replaced_bookmark_ids = set()
    for elem in list(p):
        if elem.tag.endswith('bookmarkStart'):
            bm_id = elem.get(f'{{{ns_uri}}}id') or elem.get('id')
            bm_name = elem.get(f'{{{ns_uri}}}name') or elem.get('name')
            if bm_id is not None:
                if bm_name == semantic_bookmark:
                    replaced_bookmark_ids.add(str(bm_id))
                else:
                    bookmarks.append(('start', bm_id, bm_name or ""))
        elif elem.tag.endswith('bookmarkEnd'):
            bm_id = elem.get(f'{{{ns_uri}}}id') or elem.get('id')
            if bm_id is not None:
                bookmarks.append(('end', bm_id, None))
    bookmarks = [
        row for row in bookmarks
        if not (row[0] == 'end' and str(row[1]) in replaced_bookmark_ids)
    ]
            
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

    if semantic_bookmark and semantic_bookmark_id is not None:
        semantic_start = lxml.etree.Element(f'{{{ns_uri}}}bookmarkStart')
        semantic_start.set(f'{{{ns_uri}}}id', str(semantic_bookmark_id))
        semantic_start.set(f'{{{ns_uri}}}name', semantic_bookmark)
        p.append(semantic_start)
            
    # Label prefix, e.g. "Gambar 2."
    r1 = lxml.etree.Element(f'{{{ns_uri}}}r')
    r1.append(caption_run_properties(ns_uri, bold=True))
    
    t1 = lxml.etree.Element(f'{{{ns_uri}}}t')
    t1.text = f"{label} {prefix}"
    if t1.text.startswith(' ') or t1.text.endswith(' '):
        t1.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    r1.append(t1)
    p.append(r1)
    
    # SEQ field
    r2 = lxml.etree.Element(f'{{{ns_uri}}}r')
    r2.append(caption_run_properties(ns_uri, bold=True))
    fld2 = lxml.etree.Element(f'{{{ns_uri}}}fldChar', **{f'{{{ns_uri}}}fldCharType': "begin"})
    r2.append(fld2)
    p.append(r2)
    
    r3 = lxml.etree.Element(f'{{{ns_uri}}}r')
    r3.append(caption_run_properties(ns_uri, bold=True))
    ins3 = lxml.etree.Element(f'{{{ns_uri}}}instrText')
    if default_val == 1:
        ins3.text = f" SEQ {seq_name} \\r 1 \\* ARABIC "
    else:
        ins3.text = f" SEQ {seq_name} \\* ARABIC "
    ins3.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    r3.append(ins3)
    p.append(r3)
    
    r4 = lxml.etree.Element(f'{{{ns_uri}}}r')
    r4.append(caption_run_properties(ns_uri, bold=True))
    fld4 = lxml.etree.Element(f'{{{ns_uri}}}fldChar', **{f'{{{ns_uri}}}fldCharType': "separate"})
    r4.append(fld4)
    p.append(r4)
    
    r5 = lxml.etree.Element(f'{{{ns_uri}}}r')
    r5.append(caption_run_properties(ns_uri, bold=True))
    t5 = lxml.etree.Element(f'{{{ns_uri}}}t')
    t5.text = str(default_val)
    r5.append(t5)
    p.append(r5)
    
    r6 = lxml.etree.Element(f'{{{ns_uri}}}r')
    r6.append(caption_run_properties(ns_uri, bold=True))
    fld6 = lxml.etree.Element(f'{{{ns_uri}}}fldChar', **{f'{{{ns_uri}}}fldCharType': "end"})
    r6.append(fld6)
    p.append(r6)

    # The stable bookmark deliberately spans only ``Gambar/Tabel C.k`` and
    # not the description.  A Word REF field therefore renders a compact,
    # automatically updated narrative reference such as ``Gambar 2.9``.
    if semantic_bookmark and semantic_bookmark_id is not None:
        semantic_end = lxml.etree.Element(f'{{{ns_uri}}}bookmarkEnd')
        semantic_end.set(f'{{{ns_uri}}}id', str(semantic_bookmark_id))
        p.append(semantic_end)
    
    # Description
    r7 = lxml.etree.Element(f'{{{ns_uri}}}r')
    r7.append(caption_run_properties(ns_uri, bold=False))
    
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


def next_bookmark_numeric_id(root, namespaces):
    """Return an unused numeric bookmark id for the current document tree."""
    ns_uri = namespaces['w']
    values = []
    for element in root.iter(f'{{{ns_uri}}}bookmarkStart'):
        raw = element.get(f'{{{ns_uri}}}id') or element.get('id')
        try:
            values.append(int(raw))
        except (TypeError, ValueError):
            continue
    return max(values, default=0) + 1


def replace_semantic_references_in_paragraph(p, targets, namespaces):
    """Replace semantic Markdown references with cached Word ``REF`` fields.

    ``targets`` is keyed by ``("FIGREF"|"TABREF", id)`` and contains a
    bookmark name plus the cached visible value.  Caching keeps the document
    readable in headless renderers, while Word can refresh the same field when
    caption numbering changes.

    Returns ``(replacement_count, unresolved_tokens)``.  Only text-bearing
    runs are rewritten; surrounding run properties are preserved.
    """
    ns_uri = namespaces['w']
    xml_space = '{http://www.w3.org/XML/1998/namespace}space'
    replacement_count = 0

    def _append_rpr(run, source_rpr):
        if source_rpr is not None:
            run.append(copy.deepcopy(source_rpr))

    def _append_reference_rpr(run):
        """Force semantic REF fields to remain regular after Word updates."""
        r_pr = lxml.etree.Element(f'{{{ns_uri}}}rPr')
        set_child_element(r_pr, 'rFonts', {
            'ascii': 'Times New Roman',
            'hAnsi': 'Times New Roman',
            'eastAsia': 'Times New Roman',
            'cs': 'Times New Roman',
        })
        set_child_element(r_pr, 'b', {'val': '0'})
        set_child_element(r_pr, 'bCs', {'val': '0'})
        set_child_element(r_pr, 'i', {'val': '0'})
        set_child_element(r_pr, 'iCs', {'val': '0'})
        set_child_element(r_pr, 'sz', {'val': '24'})
        set_child_element(r_pr, 'szCs', {'val': '24'})
        run.append(r_pr)

    def _text_run(value, source_rpr):
        run = lxml.etree.Element(f'{{{ns_uri}}}r')
        _append_rpr(run, source_rpr)
        text_element = lxml.etree.SubElement(run, f'{{{ns_uri}}}t')
        text_element.text = value
        if value.startswith(' ') or value.endswith(' '):
            text_element.set(xml_space, 'preserve')
        return run

    def _field_runs(bookmark, visible, source_rpr):
        begin_run = lxml.etree.Element(f'{{{ns_uri}}}r')
        _append_reference_rpr(begin_run)
        lxml.etree.SubElement(
            begin_run, f'{{{ns_uri}}}fldChar',
            {f'{{{ns_uri}}}fldCharType': 'begin'},
        )

        instruction_run = lxml.etree.Element(f'{{{ns_uri}}}r')
        _append_reference_rpr(instruction_run)
        instruction = lxml.etree.SubElement(
            instruction_run, f'{{{ns_uri}}}instrText'
        )
        instruction.text = f' REF {bookmark} \\h \\* CHARFORMAT '
        instruction.set(xml_space, 'preserve')

        separate_run = lxml.etree.Element(f'{{{ns_uri}}}r')
        _append_reference_rpr(separate_run)
        lxml.etree.SubElement(
            separate_run, f'{{{ns_uri}}}fldChar',
            {f'{{{ns_uri}}}fldCharType': 'separate'},
        )

        result_run = lxml.etree.Element(f'{{{ns_uri}}}r')
        _append_reference_rpr(result_run)
        result_text = lxml.etree.SubElement(result_run, f'{{{ns_uri}}}t')
        result_text.text = visible
        if visible.startswith(' ') or visible.endswith(' '):
            result_text.set(xml_space, 'preserve')

        end_run = lxml.etree.Element(f'{{{ns_uri}}}r')
        _append_reference_rpr(end_run)
        lxml.etree.SubElement(
            end_run, f'{{{ns_uri}}}fldChar',
            {f'{{{ns_uri}}}fldCharType': 'end'},
        )
        return [begin_run, instruction_run, separate_run, result_run, end_run]

    # Work on a snapshot because matching runs are removed during traversal.
    for run in list(p.findall('.//w:r', namespaces)):
        text_elements = run.findall('w:t', namespaces)
        if not text_elements:
            continue
        run_text = ''.join(element.text or '' for element in text_elements)
        matches = list(_SEMANTIC_REFERENCE_PATTERN.finditer(run_text))
        if not matches:
            continue
        # A mixed-content run is rare and unsafe to split mechanically because
        # tabs/drawings would lose their exact position.  Leave it unresolved
        # so the caller/validator can report the source token.
        if any(child.tag not in {
                f'{{{ns_uri}}}rPr', f'{{{ns_uri}}}t'} for child in run):
            continue

        parent = run.getparent()
        if parent is None:
            continue
        insert_at = parent.index(run)
        source_rpr = run.find('w:rPr', namespaces)
        generated = []
        cursor = 0
        if any(targets.get((match.group(1), match.group(2))) is None
               for match in matches):
            continue
        for match in matches:
            key = (match.group(1), match.group(2))
            target = targets.get(key)
            if match.start() > cursor:
                generated.append(_text_run(run_text[cursor:match.start()], source_rpr))
            generated.extend(_field_runs(
                target['bookmark'], target['display'], source_rpr
            ))
            replacement_count += 1
            cursor = match.end()
        if cursor < len(run_text):
            generated.append(_text_run(run_text[cursor:], source_rpr))
        parent.remove(run)
        for offset, element in enumerate(generated):
            parent.insert(insert_at + offset, element)

    unresolved = [match.group(0) for match in _SEMANTIC_REFERENCE_PATTERN.finditer(
        _paragraph_text(p, namespaces)
    )]
    return replacement_count, unresolved


def replace_semantic_references_in_table_cells(body, targets, namespaces):
    """Replace stable figure/table references in every non-caption table cell."""
    replacement_count = 0
    unresolved_tokens = []
    for table_p in body.xpath('.//w:tbl//w:p', namespaces=namespaces):
        if (_paragraph_style(table_p, namespaces) or "Normal") == 'Caption':
            continue
        count, unresolved = replace_semantic_references_in_paragraph(
            table_p, targets, namespaces
        )
        replacement_count += count
        unresolved_tokens.extend(unresolved)
    return replacement_count, unresolved_tokens

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
        ensure_report_style_colors(root)
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
                    set_child_element(pPr, 'spacing', main_line_spacing_attrs())
                    set_child_element(pPr, 'jc', {'val': 'both'})
                    set_child_element(pPr, 'ind', {'firstLine': '0', 'left': '0'})
                elif style_id == 'ListParagraph':
                    set_child_element(pPr, 'spacing', main_line_spacing_attrs())
                elif style_id == 'Caption':
                    set_child_element(pPr, 'spacing', {'before': '120', 'after': '120', 'line': '240', 'lineRule': 'auto'})
                    set_child_element(pPr, 'jc', {'val': 'center'})
                    set_child_element(pPr, 'ind', {'firstLine': '0', 'left': '0'})
                elif style_id in ['TOC1', 'TOC2', 'TOC3', 'TableofFigures']:
                    set_child_element(pPr, 'spacing', main_line_spacing_attrs())
                    tabs = set_child_element(pPr, 'tabs')
                    for child in list(tabs):
                        tabs.remove(child)
                    set_child_element(tabs, 'tab', {'val': 'right', 'leader': 'dot', 'pos': '7927'})
                elif style_id.startswith('Heading'):
                    if style_id in ['Heading1', 'Heading2']:
                        set_child_element(pPr, 'spacing', main_line_spacing_attrs('240', '120'))
                    else:
                        set_child_element(pPr, 'spacing', main_line_spacing_attrs('120', '60'))
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
        
        # Capture BAB paragraph identities before heading text is normalized. This
        # prevents another level-1 heading with numbering from becoming a false
        # chapter section merely because it shares the same Word style/numId.
        chapter_paragraphs = []
        for paragraph in body.findall('w:p', namespaces):
            p_pr = paragraph.find('w:pPr', namespaces)
            p_style = p_pr.find('w:pStyle', namespaces) if p_pr is not None else None
            style_id = p_style.get(f'{{{ns_uri}}}val') if p_style is not None else ''
            text = _paragraph_text(paragraph, namespaces)
            if style_id == 'Heading1' and parse_chapter_number(text) is not None:
                chapter_paragraphs.append(paragraph)

        # Find the original paragraph-level sectPr from the template to preserve header/footer references
        original_sectPr = None
        for p_elem in body.findall('w:p', namespaces):
            pPr_elem = p_elem.find('w:pPr', namespaces)
            if pPr_elem is not None:
                sectPr_elem = pPr_elem.find('w:sectPr', namespaces)
                if sectPr_elem is not None:
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
            format_caption_paragraph_clean(
                p,
                label,
                prefix,
                seq_name,
                default_val,
                desc,
                namespaces,
                semantic_bookmark=bookmark_name,
                semantic_bookmark_id=bookmark_id,
            )
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
                        if (child.tag.endswith('sdt') and lembar_pengesahan_processed
                                and need_page_break_after_lp):
                            # Word regenerates TOC SDT paragraphs during COM
                            # field update and may discard pageBreakBefore from
                            # the heading itself. A standalone break before the
                            # SDT prevents "DAFTAR ISI" leaking onto the approval
                            # page and survives that regeneration.
                            reconstructed_children.append(
                                make_explicit_page_break_paragraph(namespaces)
                            )
                            need_page_break_after_lp = False
                            print(
                                "  Inserted durable page break before Daftar Isi "
                                f"SDT at index {idx}"
                            )
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
        semantic_targets = {}
        bookmark_numeric_id = next_bookmark_numeric_id(root, namespaces)
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
            semantic = parse_semantic_caption(text_clean)
            semantic_id = semantic[1] if semantic is not None else None
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
            bookmark_name = None
            assigned_bookmark_id = None
            if semantic_id:
                bookmark_name = make_crossref_bookmark(label, semantic_id)
                assigned_bookmark_id = bookmark_numeric_id
                bookmark_numeric_id += 1
                ref_kind = 'FIGREF' if label == 'Gambar' else 'TABREF'
                semantic_targets[(ref_kind, semantic_id)] = {
                    'bookmark': bookmark_name,
                    'display': f"{label} {new_number}",
                }
            format_caption_paragraph_clean(
                p, label, f"{chapter}.", label, k, desc, namespaces,
                semantic_bookmark=bookmark_name,
                semantic_bookmark_id=assigned_bookmark_id,
            )
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

        # Convert stable source tokens to real Word REF fields.  Their cached
        # values keep headless/PDF output correct before Word refreshes fields.
        semantic_ref_count = 0
        unresolved_semantic_refs = []
        for idx, child in enumerate(children):
            if not child.tag.endswith('p') or idx <= section1_last_p_idx:
                continue
            if is_inside_table(child):
                continue
            if (_paragraph_style(child, namespaces) or "Normal") == 'Caption':
                continue
            count, unresolved = replace_semantic_references_in_paragraph(
                child, semantic_targets, namespaces
            )
            semantic_ref_count += count
            unresolved_semantic_refs.extend(unresolved)
        # Table-cell evidence often contains the same stable [FIGREF:id] tokens
        # as body prose.  Process those paragraphs separately so the generated
        # REF fields remain clickable even when the reference is inside a cell.
        count, unresolved = replace_semantic_references_in_table_cells(
            body, semantic_targets, namespaces
        )
        semantic_ref_count += count
        unresolved_semantic_refs.extend(unresolved)
        if semantic_ref_count:
            print(
                "  Inserted %d semantic figure/table REF field(s)."
                % semantic_ref_count
            )
        for token in sorted(set(unresolved_semantic_refs)):
            print("  [WARNING] Semantic reference was not resolved: %s" % token)

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
                    cleaned_text = text.replace(
                        'Aliyah Aliyah et al., 2024',
                        'Aliyah et al. 2024',
                    ).replace(
                        'Aliyah Aliyah et al. 2024',
                        'Aliyah et al. 2024',
                    )
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
                            set_child_element(pPr, 'spacing', main_line_spacing_attrs())
                        elif pStyle_val == 'ListParagraph':
                            if pPr is None:
                                pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                                p.insert(0, pPr)
                            set_child_element(pPr, 'spacing', main_line_spacing_attrs())
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
                

        if chapter_paragraphs:
            page_number_reference_ids = ensure_page_number_parts(unpacked_dir)
            section_count = configure_report_sections(
                body,
                namespaces,
                original_sectPr,
                page_number_reference_ids,
                chapter_paragraphs,
            )
            print(
                "Configured %d report section(s): Roman front matter at bottom-right; "
                "BAB first pages at bottom-center; continuation pages at top-right; "
                "Arabic numbering restarts at 1 on BAB I." % section_count
            )
        else:
            # Partial DOCX fixtures and reusable fragments may contain tables or
            # styles without any report chapters. Preserve their sections while
            # still enforcing the canonical page geometry.
            all_sect_pr = list(body.iter(f'{{{ns_uri}}}sectPr'))
            for section_properties in all_sect_pr:
                apply_upnvj_page_layout(section_properties)
            print(
                "Skipped report page-number sectioning: no explicit BAB heading "
                "was present; canonical geometry was retained."
            )
            
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
                        if val and val not in ['Symbol', 'Wingdings', 'Times New Roman']:
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
                            if not val or val not in ['Symbol', 'Wingdings']:
                                elem.set(full_attr, 'Times New Roman')
                                modified = True
                elif tag_local in ['latin', 'ea', 'cs'] and elem.tag.startswith(f'{{{A_NS}}}'):
                    val = elem.get('typeface')
                    if val and val not in ['Symbol', 'Wingdings', 'Times New Roman']:
                        elem.set('typeface', 'Times New Roman')
                        modified = True
                elif 'typeface' in elem.attrib:
                    val = elem.attrib['typeface']
                    if val and val not in ['Symbol', 'Wingdings', 'Times New Roman']:
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
