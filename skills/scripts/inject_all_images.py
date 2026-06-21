import os
import sys
import json
import zipfile
import lxml.etree
import shutil
import struct
import hashlib
import re

# Standard Word max content width is around 15cm (5400000 EMU).
MAX_WIDTH = 5400000
# 1 twip = 635 EMU (used to derive the printable page height threshold for C4).
EMU_PER_TWIP = 635

WORD_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
REL_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'

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


def scaled_dimensions(cx, cy):
    """Replicate generate_drawing_xml width-scaling so callers can reason about
    the *rendered* height (used for the C4 page-break decision)."""
    if cx > MAX_WIDTH:
        scale = MAX_WIDTH / cx
        return MAX_WIDTH, int(cy * scale)
    return cx, cy


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


def generate_drawing_xml(r_id, cx, cy, name, docpr_id):
    """Generate w:drawing XML element with specified properties."""
    cx, cy = scaled_dimensions(cx, cy)

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

        match_count = len(resolve_caption_indices(body, caption_match, namespaces))

        # C2: exactly-one caption resolution (no silent skip).
        if match_count != 1:
            if item_id in unresolved_allow and match_count == 0:
                print(f"RECONCILED (unresolved_allow): '{item_id}' resolves to 0 captions; "
                      f"intentionally skipped.")
                continue
            errors.append(
                f"[C2] entry '{item_id}' caption_match '{caption_match}' resolved to "
                f"{match_count} caption paragraph(s); expected exactly 1."
            )
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
        matches = resolve_caption_indices(body, caption_match, namespaces)
        if len(matches) != 1:
            # Reconciled, intentionally-omitted entry: skip when it is
            # allow-listed AND resolves to 0 captions. This mirrors the pre-pass
            # reconciliation rule (which keys on caption count, not file
            # existence) so an allow-listed entry whose image happens to exist on
            # disk is skipped consistently rather than tripping the guard below.
            if item_id in unresolved_allow and len(matches) == 0:
                continue
            # Defensive: should never happen after the pre-pass.
            print(f"Error: entry '{item_id}' no longer resolves to exactly one caption.")
            shutil.rmtree(temp_dir)
            sys.exit(1)
        caption_idx = matches[0]

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

        # Compute drawing dimensions.
        w, h = get_image_dimensions(src_path)
        cx = w * 9525
        cy = h * 9525
        if "cx" in item:
            cx = item["cx"]
        if "cy" in item:
            cy = item["cy"]

        docpr_id += 1
        p_drawing = generate_drawing_xml(r_id, cx, cy, new_img_name, docpr_id)

        # C4: page-break-before for oversized images. Preserve the original
        # width-derived check (cy > MAX_WIDTH) AND add the explicit printable
        # page-height threshold check on the rendered (scaled) height.
        _, rendered_cy = scaled_dimensions(cx, cy)
        if cy > MAX_WIDTH or rendered_cy > page_height_threshold:
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
        print(f"Injected {img_file} before '{caption_match}' (rId={r_id}, size={w}x{h})")

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

    # Write changes
    rels_tree.write(rels_path, encoding='utf-8', xml_declaration=True)
    doc_tree.write(doc_path, encoding='utf-8', xml_declaration=True)

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
