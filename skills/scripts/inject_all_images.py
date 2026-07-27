import os
import sys
import json
import zipfile
import lxml.etree
import shutil
import struct
import hashlib
import re

# ------------------------------------------------------------------ #
# Shared BODY-figure bounding box (tunable). Every BODY figure is scaled to
# fit INSIDE this box while preserving aspect ratio (never upscaled, never
# cropped). 1 cm = 360000 EMU.
#   BODY_MAX_W_EMU = 15 cm, BODY_MAX_H_EMU = 16 cm.
# These MUST match format_ta_proyek.center_and_scale_drawings().
# ------------------------------------------------------------------ #
BODY_MAX_W_EMU = 5400000   # 15 cm
BODY_MAX_H_EMU = 5760000   # 16 cm
# Reserve enough printable height for a multi-line 12 pt caption plus its
# paragraph spacing.  C4 requires the drawing and caption to fit on one page.
# This value must match validate_docx_structure.py.
FIGURE_CAPTION_RESERVE_EMU = 1080000  # 3 cm

# Legacy alias kept only as the printable-height fallback below.
MAX_WIDTH = 5400000
# 1 twip = 635 EMU (used to derive the printable page height threshold for C4).
EMU_PER_TWIP = 635
EMU_PER_CM = 360000

WORD_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
REL_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'
CONTENT_TYPES_NS = 'http://schemas.openxmlformats.org/package/2006/content-types'
FIGURE_MARKER_PREFIX = '[FIGURE:'

# Default reconciliation file (shared with the validator). Lists are empty by
# default so every duplicate-content (C1) and unresolved-caption (C2) defect
# remains detectable; only legitimate reuse/omission is allow-listed here.
RECONCILE_PATH = os.path.join("images", "manifest_reconcile.json")


def md5_file(filepath):
    """Return the hex MD5 of a file's bytes."""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def load_reconcile(path=RECONCILE_PATH):
    """Load the reconciliation allow-lists. Missing file => empty allow-lists."""
    duplicate_allow_groups = []
    unresolved_allow = set()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        duplicate_allow_groups = [set(group) for group in data.get("duplicate_content_allow", [])]
        unresolved_allow = set(data.get("unresolved_allow", []))
    return duplicate_allow_groups, unresolved_allow


def _duplicate_pair_allowed(id_a, id_b, duplicate_allow_groups):
    """True if both figure ids appear together in any allow-list group."""
    for group in duplicate_allow_groups:
        if id_a in group and id_b in group:
            return True
    return False


def get_image_dimensions(filepath):
    """Return (width, height) in pixels for PNG/JPEG."""
    with open(filepath, 'rb') as f:
        head = f.read(24)
        if len(head) != 24:
            return 800, 600
        if head.startswith(b'\x89PNG\r\n\x1a\n'):
            check = struct.unpack('>I', head[8:12])[0]
            if check == 0x0d0a1a0a:
                pass
            w, h = struct.unpack('>LL', head[16:24])
            return w, h
        elif head.startswith(b'\xff\xd8'):
            f.seek(0)
            size = 2
            ftype = 0
            while not 0xc0 <= ftype <= 0xcf or ftype in (0xc4, 0xc8, 0xcc):
                f.seek(size, 1)
                byte = f.read(1)
                while ord(byte) == 0xff:
                    byte = f.read(1)
                ftype = ord(byte)
                size = struct.unpack('>H', f.read(2))[0] - 2
            f.seek(1, 1)
            h, w = struct.unpack('>HH', f.read(4))
            return w, h
    return 800, 600


def scaled_dimensions(cx, cy, max_height_emu=None):
    """Aspect-preserving bounding-box scale applied to every BODY figure.

    Scales the native (cx, cy) to fit INSIDE the shared box
    (BODY_MAX_W_EMU x BODY_MAX_H_EMU) and an optional page-aware height cap
    using a SINGLE factor on both axes, so the aspect ratio is preserved (no
    stretch). Never upscales (scale capped at 1.0). Callers use the returned
    values for BOTH wp:extent and a:ext (so wp == ae) and to enforce the C4
    same-page drawing/caption contract."""
    if cx <= 0 or cy <= 0:
        return cx, cy
    height_cap = BODY_MAX_H_EMU
    if max_height_emu is not None:
        height_cap = min(height_cap, max(1, int(max_height_emu)))
    scale = min(BODY_MAX_W_EMU / cx, height_cap / cy, 1.0)
    return int(cx * scale), int(cy * scale)


def printable_height_emu(doc_root, namespaces):
    """Printable page height in EMU from the body sectPr:
    (pgSz.h - pgMar.top - pgMar.bottom) twips * 635. Falls back to MAX_WIDTH if
    the section geometry is unavailable. Must match the validator's threshold."""
    sect = doc_root.find('w:body/w:sectPr', namespaces)
    if sect is None:
        return MAX_WIDTH
    pgSz = sect.find('w:pgSz', namespaces)
    pgMar = sect.find('w:pgMar', namespaces)
    if pgSz is None or pgMar is None:
        return MAX_WIDTH
    try:
        h = int(pgSz.get(f'{{{WORD_NS}}}h'))
        top = int(pgMar.get(f'{{{WORD_NS}}}top'))
        bottom = int(pgMar.get(f'{{{WORD_NS}}}bottom'))
    except (TypeError, ValueError):
        return MAX_WIDTH
    return (h - top - bottom) * EMU_PER_TWIP


def _para_text(p):
    return "".join([t.text for t in p.iter(f'{{{WORD_NS}}}t') if t.text]).strip()


def _para_style(p, namespaces):
    pPr = p.find('w:pPr', namespaces)
    if pPr is None:
        return ""
    pStyle = pPr.find('w:pStyle', namespaces)
    return pStyle.get(f'{{{WORD_NS}}}val') if pStyle is not None else ""


def _ensure_paragraph_property(paragraph, property_name, namespaces):
    ppr = paragraph.find('w:pPr', namespaces)
    if ppr is None:
        ppr = lxml.etree.Element(f'{{{WORD_NS}}}pPr')
        paragraph.insert(0, ppr)
    prop = ppr.find(f'w:{property_name}', namespaces)
    if prop is None:
        prop = lxml.etree.SubElement(ppr, f'{{{WORD_NS}}}{property_name}')
    return ppr, prop


def enforce_manifest_page_groups(body, manifest_items, namespaces):
    """Keep selected narrative/figure pairs together on one report page.

    A group is declared entirely through manifest metadata. Its expected direct
    body sequence is narrative, drawing 1, caption 1, drawing 2, caption 2.
    ``keepNext`` links the sequence and ``pageBreakBefore`` starts the group on
    a fresh page. The final caption keeps the required property in the XML but
    explicitly disables it so the chain ends without pulling the next section.
    """
    groups = {}
    for item in manifest_items:
        group_id = item.get('page_group')
        if group_id:
            groups.setdefault(group_id, []).append(item)

    grouped = 0
    wp_ns = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
    for group_id, items in groups.items():
        ordered = sorted(items, key=lambda item: item.get('page_group_order', 0))
        if len(ordered) != 2 or [item.get('page_group_order') for item in ordered] != [1, 2]:
            raise ValueError(
                f"Page group '{group_id}' must contain exactly two items ordered 1 and 2."
            )

        children = list(body)
        drawing_indices = []
        for item in ordered:
            identity = f"FIGURE:{item['id']}"
            matches = [
                index for index, child in enumerate(children)
                if child.tag == f'{{{WORD_NS}}}p'
                and identity in child.xpath(
                    './/wp:docPr/@name', namespaces={'wp': wp_ns}
                )
            ]
            if len(matches) != 1:
                raise ValueError(
                    f"Page group '{group_id}' item '{item['id']}' resolved to "
                    f"{len(matches)} drawing paragraphs; expected exactly 1."
                )
            drawing_indices.append(matches[0])

        first_drawing, second_drawing = drawing_indices
        if first_drawing < 1 or second_drawing != first_drawing + 2:
            raise ValueError(
                f"Page group '{group_id}' does not have adjacent drawing/caption pairs."
            )
        narrative_index = first_drawing - 1
        first_caption = first_drawing + 1
        second_caption = second_drawing + 1
        if second_caption >= len(children):
            raise ValueError(f"Page group '{group_id}' is missing its second caption.")

        narrative = children[narrative_index]
        chain = [
            narrative,
            children[first_drawing],
            children[first_caption],
            children[second_drawing],
            children[second_caption],
        ]
        if narrative.tag != f'{{{WORD_NS}}}p' or not _para_text(narrative):
            raise ValueError(f"Page group '{group_id}' is missing its narrative paragraph.")
        if any(_para_style(paragraph, namespaces) != 'Caption' for paragraph in chain[2::2]):
            raise ValueError(f"Page group '{group_id}' has an invalid caption paragraph.")

        _ensure_paragraph_property(narrative, 'pageBreakBefore', namespaces)
        for paragraph in chain:
            _ensure_paragraph_property(paragraph, 'keepNext', namespaces)
            _ensure_paragraph_property(paragraph, 'keepLines', namespaces)
        for paragraph in chain[1:]:
            ppr = paragraph.find('w:pPr', namespaces)
            page_break = ppr.find('w:pageBreakBefore', namespaces) if ppr is not None else None
            if page_break is not None:
                ppr.remove(page_break)

        last_ppr, last_keep_next = _ensure_paragraph_property(
            chain[-1], 'keepNext', namespaces
        )
        last_keep_next.set(f'{{{WORD_NS}}}val', '0')
        grouped += 1
        print(
            f"Page group '{group_id}': kept narrative and two figure/caption pairs together."
        )
    return grouped


def resolve_caption_indices(body, caption_match, namespaces):
    """Collect the body indices of ALL paragraphs that match a manifest entry:
    pStyle == 'Caption', text contains caption_match, and the remainder matches
    ^(Gambar|Tabel)\\s+[0-9\\.]+$. Returns the full list (no break-on-first)."""
    matches = []
    for idx, child in enumerate(list(body)):
        if child.tag != f'{{{WORD_NS}}}p':
            continue
        if _para_style(child, namespaces) != 'Caption':
            continue
        text = _para_text(child)
        if caption_match in text:
            remainder = text.replace(caption_match, "").strip()
            if re.match(r'^(Gambar|Tabel)\s+[0-9\.]+$', remainder, re.IGNORECASE):
                matches.append(idx)
    return matches


def resolve_figure_marker_indices(body, figure_id):
    """Return direct-body paragraph indices for one exact stable marker."""
    expected = f"[FIGURE:{figure_id}]"
    return [
        idx for idx, child in enumerate(list(body))
        if child.tag == f'{{{WORD_NS}}}p' and _para_text(child) == expected
    ]


def resolve_figure_target(body, item, namespaces):
    """Resolve one manifest item to its caption, preferring its exact marker.

    Returns ``(mode, locator_idx, caption_idx, error)``.  ``mode`` is
    ``marker`` for the stable Markdown reference or ``legacy_caption`` for
    backward-compatible documents that contain no marker for the item.
    """
    item_id = item.get('id', item.get('file', '<unknown>'))
    caption_match = item.get('caption_match', '')
    marker_matches = resolve_figure_marker_indices(body, item_id)
    if marker_matches:
        if len(marker_matches) != 1:
            return 'marker', None, None, (
                f"[C2] entry '{item_id}' marker [FIGURE:{item_id}] resolved to "
                f"{len(marker_matches)} paragraphs; expected exactly 1."
            )
        marker_idx = marker_matches[0]
        children = list(body)
        caption_idx = marker_idx + 1
        if caption_idx >= len(children):
            return 'marker', marker_idx, None, (
                f"[C2] entry '{item_id}' marker is not immediately followed by its caption."
            )
        caption_p = children[caption_idx]
        caption_matches = (
            caption_p.tag == f'{{{WORD_NS}}}p'
            and _para_style(caption_p, namespaces) == 'Caption'
            and caption_match in _para_text(caption_p)
        )
        if not caption_matches:
            return 'marker', marker_idx, caption_idx, (
                f"[C2] entry '{item_id}' marker must be immediately followed by a Caption "
                f"paragraph containing {caption_match!r}."
            )
        return 'marker', marker_idx, caption_idx, None

    caption_matches = resolve_caption_indices(body, caption_match, namespaces)
    if len(caption_matches) != 1:
        return 'legacy_caption', None, None, (
            f"[C2] entry '{item_id}' caption_match '{caption_match}' resolved to "
            f"{len(caption_matches)} caption paragraph(s); expected exactly 1."
        )
    return 'legacy_caption', caption_matches[0], caption_matches[0], None


def ensure_media_content_types(content_types_root, image_files):
    """Ensure every injected media extension has an OPC content type.

    Word may remove the PNG default while saving the pre-injection package if
    no PNG drawing remains at that stage.  Adding PNG parts without restoring
    this declaration produces a ZIP/XML package that our structural parser can
    read but Microsoft Word correctly rejects as corrupt.
    """
    mime_by_extension = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
    }
    existing = {
        (node.get('Extension') or '').lower()
        for node in content_types_root.findall(f'{{{CONTENT_TYPES_NS}}}Default')
    }
    added = []
    for image_file in image_files:
        extension = os.path.splitext(image_file)[1].lstrip('.').lower()
        if extension in existing:
            continue
        content_type = mime_by_extension.get(extension)
        if content_type is None:
            raise ValueError(
                f"Unsupported image extension '.{extension}' for '{image_file}'; "
                "add an explicit OPC content type before injection."
            )
        lxml.etree.SubElement(
            content_types_root,
            f'{{{CONTENT_TYPES_NS}}}Default',
            Extension=extension,
            ContentType=content_type,
        )
        existing.add(extension)
        added.append(extension)
    return added


def generate_drawing_xml(r_id, cx, cy, name, docpr_id, max_height_emu=None):
    """Generate w:drawing XML element with specified properties."""
    cx, cy = scaled_dimensions(cx, cy, max_height_emu=max_height_emu)

    xml = f'''<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" 
             xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" 
             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" 
             xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" 
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
        <w:pPr>
            <w:keepNext/>
            <w:keepLines/>
            <w:jc w:val="center"/>
        </w:pPr>
        <w:r>
            <w:drawing>
                <wp:inline distT="0" distB="0" distL="0" distR="0">
                    <wp:extent cx="{cx}" cy="{cy}"/>
                    <wp:effectExtent l="0" t="0" r="0" b="0"/>
                    <wp:docPr id="{docpr_id}" name="{name}"/>
                    <wp:cNvGraphicFramePr>
                        <a:graphicFrameLocks noChangeAspect="1"/>
                    </wp:cNvGraphicFramePr>
                    <a:graphic>
                        <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
                            <pic:pic>
                                <pic:nvPicPr>
                                    <pic:cNvPr id="{docpr_id}" name="{name}"/>
                                    <pic:cNvPicPr/>
                                </pic:nvPicPr>
                                <pic:blipFill>
                                    <a:blip r:embed="{r_id}" cstate="print"/>
                                    <a:stretch>
                                        <a:fillRect/>
                                    </a:stretch>
                                </pic:blipFill>
                                <pic:spPr>
                                    <a:xfrm>
                                        <a:off x="0" y="0"/>
                                        <a:ext cx="{cx}" cy="{cy}"/>
                                    </a:xfrm>
                                    <a:prstGeom prst="rect">
                                        <a:avLst/>
                                    </a:prstGeom>
                                    <a:ln>
                                        <a:noFill/>
                                    </a:ln>
                                </pic:spPr>
                            </pic:pic>
                        </a:graphicData>
                    </a:graphic>
                </wp:inline>
            </w:drawing>
        </w:r>
    </w:p>'''
    return lxml.etree.fromstring(xml)


def restore_post_com_typography(doc_root):
    """Restore typography that Word COM may flatten while updating fields.

    This pass is deliberately structural: it does not touch hyperlinks,
    drawings, or field instructions. CodeBlock paragraphs and inline code are
    restored first, then the shared technical-term formatter is reused when
    available so paragraph and table terminology follows the same registry.
    """
    namespaces = {'w': WORD_NS}
    ns = WORD_NS
    def set_font(rpr, name, size='24', italic=False):
        fonts = rpr.find('w:rFonts', namespaces)
        if fonts is None:
            fonts = lxml.etree.Element(f'{{{ns}}}rFonts')
            rpr.insert(0, fonts)
        for attr in ('ascii', 'hAnsi', 'cs'):
            fonts.set(f'{{{ns}}}{attr}', name)
        for tag in ('sz', 'szCs'):
            elem = rpr.find(f'w:{tag}', namespaces)
            if elem is None:
                elem = lxml.etree.SubElement(rpr, f'{{{ns}}}{tag}')
            elem.set(f'{{{ns}}}val', str(size))
        for tag in ('i', 'iCs'):
            elem = rpr.find(f'w:{tag}', namespaces)
            if italic and elem is None:
                lxml.etree.SubElement(rpr, f'{{{ns}}}{tag}')
            elif not italic and elem is not None:
                rpr.remove(elem)

    def restore_abstract_layout():
        abstract_active = False
        for paragraph in doc_root.findall('.//w:p', namespaces):
            paragraph_text = _para_text(paragraph).strip()
            style = _para_style(paragraph, namespaces)
            if style == 'Heading1' and paragraph_text.upper() in {'ABSTRAK', 'ABSTRACT'}:
                ppr = paragraph.find('w:pPr', namespaces)
                if ppr is None:
                    ppr = lxml.etree.Element(f'{{{ns}}}pPr')
                    paragraph.insert(0, ppr)
                if ppr.find('w:pageBreakBefore', namespaces) is None:
                    lxml.etree.SubElement(ppr, f'{{{ns}}}pageBreakBefore')
                abstract_active = True
                continue
            if abstract_active and style == 'Heading1':
                abstract_active = False
            if not abstract_active or style not in {'Normal', ''}:
                continue
            for run in paragraph.findall('.//w:r', namespaces):
                rpr = run.find('w:rPr', namespaces)
                if rpr is None:
                    rpr = lxml.etree.Element(f'{{{ns}}}rPr')
                    run.insert(0, rpr)
                italic = rpr.find('w:i', namespaces) is not None
                set_font(rpr, 'Times New Roman', '22', italic=italic)

    front_matter = True
    for paragraph in doc_root.findall('.//w:p', namespaces):
        style = _para_style(paragraph, namespaces)
        is_caption = style == 'Caption'
        is_codeblock = style == 'CodeBlock'
        paragraph_text = _para_text(paragraph)
        if re.match(r'^BAB\s+(?:[IVXLCDM]+|\d+)', paragraph_text, re.IGNORECASE):
            front_matter = False
        if paragraph.find('.//w:drawing', namespaces) is not None or is_caption:
            ppr = paragraph.find('w:pPr', namespaces)
            if ppr is None:
                ppr = lxml.etree.Element(f'{{{ns}}}pPr')
                paragraph.insert(0, ppr)
            for tag in ('keepNext', 'keepLines'):
                if ppr.find(f'w:{tag}', namespaces) is None:
                    lxml.etree.SubElement(ppr, f'{{{ns}}}{tag}')
        for run in paragraph.findall('.//w:r', namespaces):
            if any(a.tag == f'{{{ns}}}hyperlink' for a in run.iterancestors()):
                continue
            if run.find('w:instrText', namespaces) is not None or run.find('w:fldChar', namespaces) is not None:
                rpr = run.find('w:rPr', namespaces)
                if rpr is not None:
                    for tag in ('i', 'iCs'):
                        elem = rpr.find(f'w:{tag}', namespaces)
                        if elem is not None:
                            rpr.remove(elem)
                continue
            rpr = run.find('w:rPr', namespaces)
            if rpr is None:
                rpr = lxml.etree.Element(f'{{{ns}}}rPr')
                run.insert(0, rpr)
            if is_codeblock:
                set_font(rpr, 'Courier New', '24', italic=True)
            else:
                if front_matter and not is_caption:
                    # Word COM occasionally changes front-matter runs to the
                    # template's fallback font or 9 pt. Preserve intentional
                    # larger headings, but restore the report body baseline.
                    set_font(rpr, 'Times New Roman', '24' if style != 'Heading1' else '28', italic=False)
                fonts = rpr.find('w:rFonts', namespaces)
                font_text = '' if fonts is None else ' '.join(
                    fonts.get(f'{{{ns}}}{attr}', '') for attr in ('ascii', 'hAnsi', 'cs')
                )
                if 'Consolas' in font_text or 'Courier New' in font_text:
                    set_font(rpr, 'Times New Roman', '24', italic=True)
                if is_caption:
                    for tag in ('i', 'iCs'):
                        elem = rpr.find(f'w:{tag}', namespaces)
                        if elem is not None:
                            rpr.remove(elem)

    try:
        from format_ta_proyek import (
            apply_required_inline_term_formatting,
            normalize_regular_technical_terms,
        )
        apply_required_inline_term_formatting(doc_root, namespaces)
        normalize_regular_technical_terms(doc_root, namespaces)
    except Exception:
        # The build invokes a synchronized copy from ``scratch/``. Resolve the
        # canonical formatter explicitly so post-COM typography restoration is
        # not dependent on the process working directory's import path.
        canonical_scripts = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'skills', 'scripts')
        )
        if not os.path.isdir(canonical_scripts):
            canonical_scripts = os.path.abspath(
                os.path.join(os.getcwd(), 'skills', 'scripts')
            )
        if canonical_scripts not in sys.path:
            sys.path.insert(0, canonical_scripts)
        try:
            from format_ta_proyek import (
                apply_required_inline_term_formatting,
                normalize_regular_technical_terms,
            )
            apply_required_inline_term_formatting(doc_root, namespaces)
            normalize_regular_technical_terms(doc_root, namespaces)
            print('Post-COM technical term restoration loaded canonical formatter.')
        except Exception as exc:
            print(f"[WARN] post-COM technical term restoration skipped: {exc}")
    restore_abstract_layout()


def inject_all_images(docx_path):
    print(f"Injecting all images into {docx_path}...")
    temp_dir = "temp_inject_dir"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    # 1. Unzip
    with zipfile.ZipFile(docx_path, 'r') as z:
        z.extractall(temp_dir)

    # 2. Read manifest + reconciliation allow-lists
    with open("images/manifest.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)
    duplicate_allow_groups, unresolved_allow = load_reconcile()

    ns_uri = WORD_NS
    namespaces = {'w': ns_uri}
    parser = lxml.etree.XMLParser(remove_blank_text=False)

    # 3. Parse rels
    rels_path = os.path.join(temp_dir, "word", "_rels", "document.xml.rels")
    rels_tree = lxml.etree.parse(rels_path, parser)
    rels_root = rels_tree.getroot()
    rel_ns = REL_NS

    max_rid = 0
    max_img = 0
    for rel in rels_root:
        rid_str = rel.get('Id')
        if rid_str.startswith('rId'):
            try:
                rid_val = int(rid_str[3:])
                if rid_val > max_rid:
                    max_rid = rid_val
            except:
                pass
        target = rel.get('Target')
        if target and target.startswith('media/image'):
            try:
                img_num = int(target.replace('media/image', '').split('.')[0])
                if img_num > max_img:
                    max_img = img_num
            except:
                pass

    # 4. Parse document XML
    doc_path = os.path.join(temp_dir, "word", "document.xml")
    doc_tree = lxml.etree.parse(doc_path, parser)
    doc_root = doc_tree.getroot()
    body = doc_root.find('w:body', namespaces)

    page_height_threshold = printable_height_emu(doc_root, namespaces)
    print(f"Printable page-height threshold: {page_height_threshold} EMU")

    post_com_items = [it for it in manifest["images"] if it.get("inject_method") == "post_com"]

    # Word COM can drop the PNG declaration when the intermediate document has
    # no remaining PNG drawings. Restore every media content type before any
    # new part is added so the final package opens without Word repair.
    content_types_path = os.path.join(temp_dir, "[Content_Types].xml")
    content_types_tree = lxml.etree.parse(content_types_path, parser)
    added_content_types = ensure_media_content_types(
        content_types_tree.getroot(), [item["file"] for item in post_com_items]
    )
    if added_content_types:
        print("Added OPC media content type(s): " + ", ".join(added_content_types))

    # ----------------------------------------------------------------- #
    # PRE-PASS: validate exactly-one resolution (C2), file presence, and
    # global content uniqueness (C1) BEFORE mutating the document, so the run
    # fails cleanly (non-zero, no partial write) instead of silently skipping.
    # ----------------------------------------------------------------- #
    errors = []
    md5_to_figure = {}  # media MD5 -> figure id (first injector to claim it)
    for item in post_com_items:
        item_id = item.get("id", item.get("file", "<unknown>"))
        caption_match = item["caption_match"]
        img_file = item["file"]
        src_path = os.path.join("images", img_file)

        mode, _locator_idx, _caption_idx, resolution_error = resolve_figure_target(
            body, item, namespaces
        )

        # C2: exactly-one marker/caption resolution (no silent skip).
        if resolution_error:
            legacy_match_count = len(resolve_caption_indices(body, caption_match, namespaces))
            if (mode == 'legacy_caption' and item_id in unresolved_allow
                    and legacy_match_count == 0):
                print(f"RECONCILED (unresolved_allow): '{item_id}' resolves to 0 captions; "
                      f"intentionally skipped.")
                continue
            errors.append(resolution_error)
            continue

        # Injectable entry must have its curated image on disk.
        if not os.path.exists(src_path):
            errors.append(
                f"[C2/file] entry '{item_id}' resolves to a caption but its injected "
                f"file '{src_path}' is missing on disk."
            )
            continue

        # C1: duplicate-content guard (honoring the reconciled reuse allow-list).
        digest = md5_file(src_path)
        if digest in md5_to_figure and md5_to_figure[digest] != item_id:
            other = md5_to_figure[digest]
            if not _duplicate_pair_allowed(item_id, other, duplicate_allow_groups):
                errors.append(
                    f"[C1] entry '{item_id}' would inject media with MD5 {digest}, "
                    f"already used by a different figure '{other}' (duplicate content). "
                    f"Reconcile legitimate reuse via duplicate_content_allow."
                )
                continue
        md5_to_figure.setdefault(digest, item_id)

    if errors:
        print("\n=== INJECTION ABORTED: content-level defects detected ===")
        for err in errors:
            print(f"- {err}")
        shutil.rmtree(temp_dir)
        sys.exit(1)

    # ----------------------------------------------------------------- #
    # INJECTION PASS: every remaining entry resolves to exactly one caption.
    # ----------------------------------------------------------------- #
    docpr_id = 1000
    injected_md5_by_image = {}  # imageNN -> injected images/<file> MD5 (C3 record)

    for item in post_com_items:
        item_id = item.get("id", item.get("file", "<unknown>"))
        caption_match = item["caption_match"]
        img_file = item["file"]
        src_path = os.path.join("images", img_file)

        # Re-resolve against the (possibly mutated) body.
        mode, locator_idx, caption_idx, resolution_error = resolve_figure_target(
            body, item, namespaces
        )
        if resolution_error:
            # Reconciled, intentionally-omitted entry: skip when it is
            # allow-listed AND resolves to 0 captions. This mirrors the pre-pass
            # reconciliation rule (which keys on caption count, not file
            # existence) so an allow-listed entry whose image happens to exist on
            # disk is skipped consistently rather than tripping the guard below.
            matches = resolve_caption_indices(body, caption_match, namespaces)
            if mode == 'legacy_caption' and item_id in unresolved_allow and len(matches) == 0:
                continue
            # Defensive: should never happen after the pre-pass.
            print(f"Error: {resolution_error}")
            shutil.rmtree(temp_dir)
            sys.exit(1)

        # Replace the explicit Markdown marker itself.  In the legacy fallback
        # there is no marker, so the caption remains the insertion locator.
        if mode == 'marker':
            marker_p = list(body)[locator_idx]
            body.remove(marker_p)
            caption_idx -= 1

        # Remove any existing drawing immediately preceding the caption.
        children = list(body)
        removed_existing = False
        if caption_idx >= 1:
            prev_p = children[caption_idx - 1]
            if prev_p.find('.//w:drawing', namespaces) is not None:
                body.remove(prev_p)
                caption_idx -= 1
                removed_existing = True

        # Copy image file verbatim into word/media (C3: bytes copied as-is).
        max_img += 1
        ext = img_file.split('.')[-1]
        new_img_name = f"image{max_img}.{ext}"
        dest_path = os.path.join(temp_dir, "word", "media", new_img_name)
        shutil.copy2(src_path, dest_path)
        # Record the injected file's MD5 keyed by the allocated imageNN. The
        # authoritative packed-vs-injected assertion runs in the validator.
        injected_md5_by_image[new_img_name] = md5_file(src_path)

        # Best-effort, non-fatal provenance note for the declared source.
        source = item.get("source")
        if source and os.path.exists(source):
            if md5_file(source) == injected_md5_by_image[new_img_name]:
                print(f"  note: source '{source}' matches injected '{img_file}' (MD5).")
            else:
                print(f"  note: source '{source}' differs from injected '{img_file}' "
                      f"(provenance only, not a failure).")

        # Add relationship.
        max_rid += 1
        r_id = f"rId{max_rid}"
        elem = lxml.etree.Element(f'{{{rel_ns}}}Relationship', {
            'Id': r_id,
            'Type': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image',
            'Target': f'media/{new_img_name}'
        })
        rels_root.append(elem)

        # Compute drawing dimensions. Read the ACTUAL image pixels (PIL) to get
        # the true native aspect ratio; fall back to the lightweight header
        # reader if PIL cannot open the file.
        w = h = None
        try:
            from PIL import Image
            with Image.open(src_path) as im:
                w, h = im.size
        except Exception as e:
            print(f"  note: PIL could not read '{src_path}' ({e}); using header reader.")
        if not w or not h:
            w, h = get_image_dimensions(src_path)
        cx = w * 9525
        cy = h * 9525
        if "cx" in item:
            cx = item["cx"]
        if "cy" in item:
            cy = item["cy"]

        docpr_id += 1
        drawing_identity = f"FIGURE:{item_id}"
        pair_figure_height = max(
            1, page_height_threshold - FIGURE_CAPTION_RESERVE_EMU
        )
        if item.get('max_height_cm') is not None:
            requested_height = int(float(item['max_height_cm']) * EMU_PER_CM)
            if requested_height <= 0:
                raise ValueError(
                    f"Manifest item '{item_id}' has invalid max_height_cm="
                    f"{item['max_height_cm']!r}."
                )
            pair_figure_height = min(pair_figure_height, requested_height)
        p_drawing = generate_drawing_xml(
            r_id,
            cx,
            cy,
            drawing_identity,
            docpr_id,
            max_height_emu=pair_figure_height,
        )

        # C4: reserve printable height for the caption, then scale the drawing
        # so the complete [drawing][caption] pair can fit on one page.  The
        # keepNext/keepLines chain below makes Word move the pair together when
        # the remaining space on the current page is insufficient.
        _, baseline_rendered_cy = scaled_dimensions(cx, cy)
        if baseline_rendered_cy > page_height_threshold:
            pPr = p_drawing.find('w:pPr', namespaces)
            if pPr is not None and pPr.find('w:pageBreakBefore', namespaces) is None:
                lxml.etree.SubElement(pPr, f'{{{ns_uri}}}pageBreakBefore')

        # Ensure caption keeps with the following text (keepNext/keepLines).
        caption_p = body[caption_idx]
        pPr_cap = caption_p.find('w:pPr', namespaces)
        if pPr_cap is None:
            pPr_cap = lxml.etree.Element(f'{{{ns_uri}}}pPr')
            caption_p.insert(0, pPr_cap)
        if pPr_cap.find('w:keepNext', namespaces) is None:
            lxml.etree.SubElement(pPr_cap, f'{{{ns_uri}}}keepNext')
        if pPr_cap.find('w:keepLines', namespaces) is None:
            lxml.etree.SubElement(pPr_cap, f'{{{ns_uri}}}keepLines')

        body.insert(caption_idx, p_drawing)
        print(
            f"Injected [FIGURE:{item_id}] from {img_file} before '{caption_match}' "
            f"(mode={mode}, rId={r_id}, size={w}x{h})"
        )

    # ----------------------------------------------------------------- #
    # POST-COM keep-props pass: the Word COM field-update step normalizes
    # Caption-styled paragraphs down to bare <w:pStyle w:val="Caption"/>,
    # discarding the keepNext/keepLines that the formatter applied pre-COM.
    # Re-assert them here (post-COM) on EVERY Gambar/Tabel caption so the
    # caption never splits from its image or across a page. Injected captions
    # already received these above; non-injected captions (e.g. the inline
    # survey charts) are fixed by this pass.
    # ----------------------------------------------------------------- #
    cap_fixed = 0
    for p in doc_root.iter(f'{{{ns_uri}}}p'):
        pPr = p.find('w:pPr', namespaces)
        pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
        style_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
        text = _para_text(p)
        is_caption = (style_val == 'Caption') or bool(re.match(r'^(Gambar|Tabel)\s+[0-9]', text, re.IGNORECASE))
        if not is_caption:
            continue
        if pPr is None:
            pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
            p.insert(0, pPr)
        changed = False
        if pPr.find('w:keepNext', namespaces) is None:
            lxml.etree.SubElement(pPr, f'{{{ns_uri}}}keepNext')
            changed = True
        if pPr.find('w:keepLines', namespaces) is None:
            lxml.etree.SubElement(pPr, f'{{{ns_uri}}}keepLines')
            changed = True
        if changed:
            cap_fixed += 1
    print(f"Post-COM keep-props pass: ensured keepNext/keepLines on {cap_fixed} caption paragraph(s).")

    page_groups = enforce_manifest_page_groups(body, post_com_items, namespaces)
    if page_groups:
        print(f"Post-COM page-group pass: enforced {page_groups} grouped page(s).")

    # Keep the visible Daftar Isi heading outside the TOC content control in
    # the final package.  Word/LibreOffice can otherwise split the heading
    # across the approval-page boundary while regenerating the SDT field.
    for child in list(body):
        if child.tag != f'{{{ns_uri}}}sdt':
            continue
        sdt_content = child.find(f'{{{ns_uri}}}sdtContent')
        toc_heading = sdt_content.find(f'{{{ns_uri}}}p') if sdt_content is not None else None
        if toc_heading is None:
            continue
        toc_text = ''.join(toc_heading.itertext()).strip().upper()
        if not toc_text.startswith('DAFTAR ISI'):
            continue
        p_pr = toc_heading.find(f'{{{ns_uri}}}pPr')
        if p_pr is None:
            p_pr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
            toc_heading.insert(0, p_pr)
        if p_pr.find(f'{{{ns_uri}}}pageBreakBefore') is None:
            lxml.etree.SubElement(p_pr, f'{{{ns_uri}}}pageBreakBefore')

        # The archive template stores the TOC heading's bookmark end, but
        # Word's field refresh can drop the corresponding bookmark start when
        # the heading is regenerated inside the content control.  The first
        # TOC hyperlink points at that heading; restore the missing start so
        # the cached TOC does not render ``Error! Bookmark not defined.``.
        toc_hyperlinks = sdt_content.xpath('.//w:hyperlink', namespaces=namespaces)
        toc_anchor = (
            toc_hyperlinks[0].get(f'{{{ns_uri}}}anchor')
            if toc_hyperlinks else None
        )
        if toc_anchor:
            existing_names = {
                node.get(f'{{{ns_uri}}}name')
                for node in doc_root.iter(f'{{{ns_uri}}}bookmarkStart')
            }
            if toc_anchor not in existing_names:
                bookmark_end = toc_heading.find(f'{{{ns_uri}}}bookmarkEnd')
                bookmark_id = (
                    bookmark_end.get(f'{{{ns_uri}}}id')
                    if bookmark_end is not None else None
                )
                if bookmark_id is None:
                    ids = [
                        int(node.get(f'{{{ns_uri}}}id'))
                        for node in doc_root.iter(f'{{{ns_uri}}}bookmarkStart')
                        if (node.get(f'{{{ns_uri}}}id') or '').isdigit()
                    ]
                    ids.extend(
                        int(node.get(f'{{{ns_uri}}}id'))
                        for node in doc_root.iter(f'{{{ns_uri}}}bookmarkEnd')
                        if (node.get(f'{{{ns_uri}}}id') or '').isdigit()
                    )
                    bookmark_id = str(max(ids, default=-1) + 1)
                bookmark_start = lxml.etree.Element(
                    f'{{{ns_uri}}}bookmarkStart',
                    {
                        f'{{{ns_uri}}}id': bookmark_id,
                        f'{{{ns_uri}}}name': toc_anchor,
                    },
                )
                first_run = toc_heading.find(f'{{{ns_uri}}}r')
                insert_at = (
                    list(toc_heading).index(first_run)
                    if first_run is not None else len(toc_heading)
                )
                toc_heading.insert(insert_at, bookmark_start)
                print(
                    f'Post-COM TOC pass: restored bookmark {toc_anchor} '
                    'for the Daftar Isi heading.'
                )
        sdt_content.remove(toc_heading)
        body.insert(body.index(child), toc_heading)
        print('Post-COM TOC pass: moved Daftar Isi heading outside the TOC SDT.')

    # ``pack.py`` may already have moved the heading before this script runs.
    # In that case, repeat the bookmark repair against the visible paragraph
    # and the cached TOC hyperlinks that remain inside the SDT.
    else:
        direct_toc_heading = None
        for child in list(body):
            if child.tag != f'{{{ns_uri}}}p':
                continue
            if ''.join(child.itertext()).strip().upper().startswith('DAFTAR ISI'):
                direct_toc_heading = child
                break
        toc_hyperlinks = []
        for candidate in body.findall(f'{{{ns_uri}}}p'):
            candidate_text = ''.join(candidate.itertext()).strip().upper()
            if candidate is direct_toc_heading or not candidate_text.startswith('DAFTAR ISI'):
                continue
            toc_hyperlinks = candidate.xpath('./w:hyperlink', namespaces=namespaces)
            if toc_hyperlinks:
                break
        if not toc_hyperlinks:
            toc_hyperlinks = doc_root.xpath(
                '//w:sdtContent//w:hyperlink', namespaces=namespaces
            )
        if direct_toc_heading is not None and toc_hyperlinks:
            toc_anchor = toc_hyperlinks[0].get(f'{{{ns_uri}}}anchor')
            existing_names = {
                node.get(f'{{{ns_uri}}}name')
                for node in doc_root.iter(f'{{{ns_uri}}}bookmarkStart')
            }
            if toc_anchor and toc_anchor not in existing_names:
                bookmark_end = direct_toc_heading.find(f'{{{ns_uri}}}bookmarkEnd')
                bookmark_id = (
                    bookmark_end.get(f'{{{ns_uri}}}id')
                    if bookmark_end is not None else None
                )
                if bookmark_id is None:
                    ids = [
                        int(node.get(f'{{{ns_uri}}}id'))
                        for node in doc_root.iter(f'{{{ns_uri}}}bookmarkStart')
                        if (node.get(f'{{{ns_uri}}}id') or '').isdigit()
                    ]
                    ids.extend(
                        int(node.get(f'{{{ns_uri}}}id'))
                        for node in doc_root.iter(f'{{{ns_uri}}}bookmarkEnd')
                        if (node.get(f'{{{ns_uri}}}id') or '').isdigit()
                    )
                    bookmark_id = str(max(ids, default=-1) + 1)
                bookmark_start = lxml.etree.Element(
                    f'{{{ns_uri}}}bookmarkStart',
                    {
                        f'{{{ns_uri}}}id': bookmark_id,
                        f'{{{ns_uri}}}name': toc_anchor,
                    },
                )
                first_run = direct_toc_heading.find(f'{{{ns_uri}}}r')
                insert_at = (
                    list(direct_toc_heading).index(first_run)
                    if first_run is not None else len(direct_toc_heading)
                )
                direct_toc_heading.insert(insert_at, bookmark_start)
                print(
                    f'Post-COM TOC pass: restored bookmark {toc_anchor} '
                    'for the existing Daftar Isi heading.'
                )

    # Final defensive pass: depending on Word's field-update order, the first
    # TOC result paragraph can live either directly in the body or inside a
    # different SDT. Locate it structurally rather than assuming one layout.
    visible_heading = next(
        (
            child for child in body.findall(f'{{{ns_uri}}}p')
            if ''.join(child.xpath('.//w:t/text()', namespaces=namespaces)).strip().upper()
            == 'DAFTAR ISI'
        ),
        None,
    )
    if visible_heading is not None and not visible_heading.xpath(
        './w:bookmarkStart', namespaces=namespaces
    ):
        toc_entry = next(
            (
                paragraph for paragraph in doc_root.xpath(
                    '//w:p[.//w:hyperlink]', namespaces=namespaces
                )
                if paragraph is not visible_heading
                and ''.join(
                    paragraph.xpath('.//w:t/text()', namespaces=namespaces)
                ).strip().upper().startswith('DAFTAR ISI')
            ),
            None,
        )
        if toc_entry is not None:
            toc_entry_ppr = toc_entry.find(f'{{{ns_uri}}}pPr')
            if toc_entry_ppr is not None:
                toc_entry_break = toc_entry_ppr.find(f'{{{ns_uri}}}pageBreakBefore')
                if toc_entry_break is not None:
                    toc_entry_ppr.remove(toc_entry_break)
        toc_hyperlink = (
            toc_entry.find('w:hyperlink', namespaces)
            if toc_entry is not None else None
        )
        toc_anchor = (
            toc_hyperlink.get(f'{{{ns_uri}}}anchor')
            if toc_hyperlink is not None else None
        )
        if toc_anchor:
            existing_start = next(
                (
                    node for node in doc_root.iter(f'{{{ns_uri}}}bookmarkStart')
                    if node.get(f'{{{ns_uri}}}name') == toc_anchor
                ),
                None,
            )
            bookmark_end = visible_heading.find(f'{{{ns_uri}}}bookmarkEnd')
            bookmark_id = (
                existing_start.get(f'{{{ns_uri}}}id')
                if existing_start is not None else (
                    bookmark_end.get(f'{{{ns_uri}}}id')
                    if bookmark_end is not None else None
                )
            )
            if existing_start is not None:
                existing_start.getparent().remove(existing_start)
            if bookmark_id is None:
                ids = [
                    int(node.get(f'{{{ns_uri}}}id'))
                    for node in doc_root.iter(f'{{{ns_uri}}}bookmarkStart')
                    if (node.get(f'{{{ns_uri}}}id') or '').isdigit()
                ]
                ids.extend(
                    int(node.get(f'{{{ns_uri}}}id'))
                    for node in doc_root.iter(f'{{{ns_uri}}}bookmarkEnd')
                    if (node.get(f'{{{ns_uri}}}id') or '').isdigit()
                )
                bookmark_id = str(max(ids, default=-1) + 1)
            bookmark_start = lxml.etree.Element(
                f'{{{ns_uri}}}bookmarkStart',
                {
                    f'{{{ns_uri}}}id': bookmark_id,
                    f'{{{ns_uri}}}name': toc_anchor,
                },
            )
            first_run = visible_heading.find(f'{{{ns_uri}}}r')
            insert_at = (
                list(visible_heading).index(first_run)
                if first_run is not None else len(visible_heading)
            )
            visible_heading.insert(insert_at, bookmark_start)
            print(
                f'Post-COM TOC pass: restored bookmark {toc_anchor} '
                'in the final defensive pass.'
            )

    # Restore typography and keep properties after Word COM has updated fields.
    restore_post_com_typography(doc_root)

    # Write changes
    rels_tree.write(rels_path, encoding='utf-8', xml_declaration=True)
    doc_tree.write(doc_path, encoding='utf-8', xml_declaration=True)
    content_types_tree.write(content_types_path, encoding='utf-8', xml_declaration=True)

    # Re-zip
    output_docx = docx_path
    if os.path.exists(output_docx):
        os.remove(output_docx)

    with zipfile.ZipFile(output_docx, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, temp_dir)
                z.write(filepath, arcname)

    shutil.rmtree(temp_dir)
    print(f"SUCCESS: Saved all post-COM images to {docx_path}")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        inject_all_images(sys.argv[1])
    else:
        inject_all_images("Tugas_Akhir_Formatted.docx")
