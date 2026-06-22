import sys
import os
import zipfile
import re
import json
import hashlib
import xml.etree.ElementTree as ET

# Namespaces / constants shared by the content-level checks (C1-C4).
W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'
WP_NS = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
MAX_WIDTH_EMU = 5400000
EMU_PER_TWIP = 635  # printable page-height threshold uses twips * 635 (matches injector)


def _md5_bytes(b):
    """Hex MD5 of a byte string."""
    return hashlib.md5(b).hexdigest()


def _md5_file(path):
    """Hex MD5 of a file's bytes."""
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def _content_text(p):
    """Concatenated, stripped text of every w:t descendant of a paragraph."""
    return "".join(t.text for t in p.iter(f'{{{W_NS}}}t') if t.text).strip()


def _content_style(p):
    """pStyle val of a paragraph ('' if none)."""
    pPr = p.find(f'{{{W_NS}}}pPr')
    if pPr is None:
        return ""
    pStyle = pPr.find(f'{{{W_NS}}}pStyle')
    if pStyle is None:
        return ""
    return pStyle.get(f'{{{W_NS}}}val') or ""


def _resolve_caption_indices_content(body, caption_match):
    """Replicate the injector's resolution rule: collect the indices (within the
    body's direct children) of ALL paragraphs where pStyle == 'Caption', the text
    contains caption_match, and the remainder matches ^(Gambar|Tabel)\\s+[0-9\\.]+$.
    Returns (children_list, matched_indices)."""
    children = list(body)
    matches = []
    for idx, child in enumerate(children):
        if child.tag != f'{{{W_NS}}}p':
            continue
        if _content_style(child) != 'Caption':
            continue
        text = _content_text(child)
        if caption_match in text:
            remainder = text.replace(caption_match, "").strip()
            if re.match(r'^(Gambar|Tabel)\s+[0-9\.]+$', remainder, re.IGNORECASE):
                matches.append(idx)
    return children, matches


def _preceding_drawing_media(children, caption_idx, rel_target):
    """Walk backwards from a caption to the nearest preceding drawing paragraph
    (skipping empty paragraphs) and resolve its blip -> rels Target -> packed
    media name ('word/media/imageNN'). Returns (media_name, drawing_p) or
    (None, None)."""
    j = caption_idx - 1
    while j >= 0:
        prev = children[j]
        if prev.tag != f'{{{W_NS}}}p':
            break
        if prev.find(f'.//{{{W_NS}}}drawing') is not None:
            blip = prev.find(f'.//{{{A_NS}}}blip')
            if blip is None:
                return None, None
            embed = blip.get(f'{{{R_NS}}}embed')
            target = rel_target.get(embed)
            if not target:
                return None, None
            return 'word/' + target, prev
        if _content_text(prev):
            break
        j -= 1
    return None, None


def _printable_height_emu_content(doc_root):
    """Printable page height in EMU from the body sectPr:
    (pgSz.h - pgMar.top - pgMar.bottom) twips * 635. Must match the injector's
    threshold. Falls back to MAX_WIDTH_EMU if the geometry is unavailable."""
    sect = doc_root.find(f'{{{W_NS}}}body/{{{W_NS}}}sectPr')
    if sect is None:
        return MAX_WIDTH_EMU
    pgSz = sect.find(f'{{{W_NS}}}pgSz')
    pgMar = sect.find(f'{{{W_NS}}}pgMar')
    if pgSz is None or pgMar is None:
        return MAX_WIDTH_EMU
    try:
        h = int(pgSz.get(f'{{{W_NS}}}h'))
        top = int(pgMar.get(f'{{{W_NS}}}top'))
        bottom = int(pgMar.get(f'{{{W_NS}}}bottom'))
    except (TypeError, ValueError):
        return MAX_WIDTH_EMU
    return (h - top - bottom) * EMU_PER_TWIP


def main():
    # Force UTF-8 encoding for stdout
    sys.stdout.reconfigure(encoding='utf-8')
    
    docx_path = "Tugas_Akhir_Formatted.docx"
    if len(sys.argv) > 1:
        docx_path = sys.argv[1]
        
    print(f"=== Starting automated validation on: {docx_path} ===")
    if not os.path.exists(docx_path):
        print(f"Error: {docx_path} does not exist.")
        sys.exit(1)
        
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    
    try:
        with zipfile.ZipFile(docx_path) as z:
            doc_xml = z.read("word/document.xml")
            styles_xml = z.read("word/styles.xml")
    except Exception as e:
        print(f"Error: Failed to open zip or read XML from {docx_path}: {e}")
        sys.exit(1)
        
    doc_root = ET.fromstring(doc_xml)
    styles_root = ET.fromstring(styles_xml)
    
    # 1. Validate taappendixheading style in styles.xml
    print("Checking styles.xml for taappendixheading...")
    appendix_style = styles_root.find("w:style[@w:styleId='taappendixheading']", namespaces)
    if appendix_style is None:
        appendix_style = styles_root.find("w:style[@w:styleId='taappendixheading']", namespaces)
        
    if appendix_style is None:
        print("ERROR: taappendixheading style not found in styles.xml")
        sys.exit(1)
        
    style_pPr = appendix_style.find("w:pPr", namespaces)
    if style_pPr is not None:
        outlineLvl = style_pPr.find("w:outlineLvl", namespaces)
        if outlineLvl is None:
            print("ERROR: taappendixheading style is missing w:outlineLvl. It needs to have outline level 8 to map to TOC level 9.")
            sys.exit(1)
        val = outlineLvl.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') or outlineLvl.get('val')
        if val != '8':
            print(f"ERROR: taappendixheading style outlineLvl value is '{val}' (should be '8' to map to level 9 and isolate from main TOC).")
            sys.exit(1)
            
    print("SUCCESS: taappendixheading style is correctly defined with outline level 8.")
    
    # 1.1 Validate TOC9 style in styles.xml
    print("Checking styles.xml for TOC9 style...")
    toc9_style = styles_root.find("w:style[@w:styleId='TOC9']", namespaces)
    if toc9_style is None:
        print("ERROR: TOC9 style not found in styles.xml")
        sys.exit(1)
        
    toc9_pPr = toc9_style.find("w:pPr", namespaces)
    if toc9_pPr is not None:
        toc9_ind = toc9_pPr.find("w:ind", namespaces)
        if toc9_ind is None:
            print("ERROR: TOC9 style is missing indentation definition (w:ind).")
            sys.exit(1)
        left_val = toc9_ind.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}left') or toc9_ind.get('left')
        if left_val != '1':
            print(f"ERROR: TOC9 indentation has left='{left_val}' (should be '1' to prevent Word from stripping it).")
            sys.exit(1)
            
    print("SUCCESS: TOC9 style is correctly defined with left='1' (visually zero) indentation.")
    
    # 2. Iterate paragraphs and perform checks
    body = doc_root.find('w:body', namespaces)
    if body is None:
        print("ERROR: body element not found in document.xml")
        sys.exit(1)
        
    # Find Section 2 start index (PENDAHULUAN Heading1) to isolate front matter
    p_list = list(body.findall('.//w:p', namespaces))
    bab1_idx = -1
    for idx, p in enumerate(p_list):
        pPr = p.find('w:pPr', namespaces)
        pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
        pStyle_val = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if pStyle is not None else ""
        text = "".join([t.text for t in p.findall('.//w:t', namespaces) if t.text]).strip()
        if pStyle_val in ['Heading1', 'heading1'] and 'PENDAHULUAN' in text.upper():
            bab1_idx = idx
            break
            
    print(f"Section 2 (PENDAHULUAN) starts at paragraph index {bab1_idx}")
    
    print("Iterating paragraphs for structure validation...")
    
    errors_found = []
    first_gambar_checked = False
    gambar_count = 0
    tabel_count = 0
    
    for idx, p in enumerate(p_list):
        pPr = p.find('w:pPr', namespaces)
        pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
        pStyle_val = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if pStyle is not None else ""
        
        # Get text of the paragraph
        text = "".join([t.text for t in p.findall('.//w:t', namespaces) if t.text]).strip()
        
        # A. Check for Word field error text (on all paragraphs)
        for err_str in [
            "Error! Hyperlink reference not valid",
            "No table of figures entries found",
            "No table of contents entries found",
            "Error! Bookmark not defined",
            "Error! Reference source not found"
        ]:
            if err_str.lower() in text.lower():
                errors_found.append(f"Paragraph {idx} contains Word field error '{err_str}': '{text}'")
                
        # B. Check Appendix paragraphs (only in body/appendix section)
        is_in_body = (bab1_idx == -1 or idx >= bab1_idx)
        
        if is_in_body and text.upper().startswith("LAMPIRAN"):
            # Ensure style is taappendixheading
            if pStyle_val not in ["taappendixheading"]:
                errors_found.append(f"Appendix paragraph {idx} '{text}' has incorrect style '{pStyle_val}' (should be taappendixheading)")
            # Ensure no w:numPr
            if pPr is not None:
                numPr = pPr.find('w:numPr', namespaces)
                if numPr is not None:
                    errors_found.append(f"Appendix paragraph {idx} '{text}' has w:numPr auto-numbering, which should be stripped.")
                    
        # C. Check Captions (Gambar / Tabel) - only check actual captions in body section
        is_caption = (pStyle_val == 'Caption')
        is_gambar_prefix = re.match(r'^Gambar\s+[0-9]', text, re.IGNORECASE)
        is_tabel_prefix = re.match(r'^Tabel\s+[0-9]', text, re.IGNORECASE)
        
        if is_in_body and (is_caption or is_gambar_prefix or is_tabel_prefix):
            instrs = [t.text.strip() for t in p.findall('.//w:instrText', namespaces) if t.text]
            instr_str = " ".join(instrs)
            
            if is_gambar_prefix or (is_caption and text.lower().startswith("gambar")):
                gambar_count += 1
                # Must contain SEQ Gambar
                if "SEQ Gambar" not in instr_str:
                    errors_found.append(f"Gambar caption {idx} '{text}' is missing 'SEQ Gambar' field. Instrs: '{instr_str}'")
                # First Gambar (Gambar 2.1) must have restart switch \r 1
                is_first_gambar = re.match(r'^Gambar\s+2\.1\b', text, re.IGNORECASE)
                if is_first_gambar or not first_gambar_checked:
                    if is_first_gambar and "\\r 1" not in instr_str:
                        errors_found.append(f"First Gambar caption {idx} '{text}' is missing restart switch '\\r 1'. Instrs: '{instr_str}'")
                    if is_first_gambar:
                        first_gambar_checked = True
                        
            elif is_tabel_prefix or (is_caption and text.lower().startswith("tabel")):
                tabel_count += 1
                # Must contain SEQ Tabel
                if "SEQ Tabel" not in instr_str:
                    errors_found.append(f"Tabel caption {idx} '{text}' is missing 'SEQ Tabel' field. Instrs: '{instr_str}'")
                # First table of each chapter (e.g. 1.1, 2.1, 3.1) must have restart switch \r 1
                m = re.match(r'^Tabel\s+[0-9]+\.1\b', text, re.IGNORECASE)
                if m and "\\r 1" not in instr_str:
                    errors_found.append(f"First Table of chapter {idx} '{text}' is missing restart switch '\\r 1'. Instrs: '{instr_str}'")
                    
        # D. Check Daftar Lampiran TOC (only in front matter or body)
        if "DAFTAR LAMPIRAN" in text.upper() and pStyle_val in ["Heading1", "heading1"] and not text.endswith("7"):
            found_lampiran_toc_field = False
            for j in range(idx + 1, min(idx + 6, len(p_list))):
                next_p = p_list[j]
                next_p_instrs = [t.text.strip() for t in next_p.findall('.//w:instrText', namespaces) if t.text]
                next_p_instr_str = " ".join(next_p_instrs)
                if "TOC" in next_p_instr_str and ("9-9" in next_p_instr_str) and ("\\n 9-9" in next_p_instr_str):
                    found_lampiran_toc_field = True
                    print(f"SUCCESS: Found Daftar Lampiran TOC field at paragraph {j}: '{next_p_instr_str}'")
                    break
            if not found_lampiran_toc_field:
                errors_found.append(f"DAFTAR LAMPIRAN heading at paragraph {idx} is not followed by a TOC field targeting level 9-9.")
                
        # E. Check for consecutive figure captions without intervening drawings or descriptions
        if is_in_body and is_gambar_prefix:
            found_consecutive_caption = False
            for j in range(idx - 1, -1, -1):
                prev_p = p_list[j]
                prev_pPr = prev_p.find('w:pPr', namespaces)
                prev_pStyle = prev_pPr.find('w:pStyle', namespaces) if prev_pPr is not None else None
                prev_pStyle_val = prev_pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if prev_pStyle is not None else ""
                prev_text = "".join([t.text for t in prev_p.findall('.//w:t', namespaces) if t.text]).strip()
                
                if not prev_text and prev_p.find('.//w:drawing', namespaces) is None:
                    continue
                    
                if prev_p.find('.//w:drawing', namespaces) is not None:
                    break
                    
                prev_is_gambar_prefix = re.match(r'^Gambar\s+[0-9]', prev_text, re.IGNORECASE)
                if prev_pStyle_val == 'Caption' or prev_is_gambar_prefix:
                    if "sequence diagram" in text.lower() or "sequence diagram" in prev_text.lower():
                        pass
                    else:
                        found_consecutive_caption = True
                        break
                    
                break
                
            if found_consecutive_caption:
                errors_found.append(f"Consecutive figure captions found: Paragraph {idx} '{text}' is preceded by another caption without an intervening drawing.")

    print(f"Processed {gambar_count} Gambar captions and {tabel_count} Tabel captions.")
    
    # F. Verify keepNext+keepLines chain on ALL drawing paragraphs in body
    print("Checking keepNext/keepLines chain on drawing paragraphs...")
    for idx, p in enumerate(p_list):
        is_in_body = (bab1_idx == -1 or idx >= bab1_idx)
        if not is_in_body:
            continue
        has_drawing = p.find('.//w:drawing', namespaces) is not None
        if has_drawing:
            pPr = p.find('w:pPr', namespaces)
            has_keepNext = pPr is not None and pPr.find('w:keepNext', namespaces) is not None
            has_keepLines = pPr is not None and pPr.find('w:keepLines', namespaces) is not None
            if not has_keepNext:
                errors_found.append(f"Drawing paragraph {idx} is missing w:keepNext (image may split from caption)")
            if not has_keepLines:
                errors_found.append(f"Drawing paragraph {idx} is missing w:keepLines (image may split across pages)")
    
    # G. Verify every Gambar caption is immediately preceded by a drawing paragraph
    print("Checking drawing-before-caption adjacency...")
    for idx, p in enumerate(p_list):
        is_in_body = (bab1_idx == -1 or idx >= bab1_idx)
        if not is_in_body:
            continue
        pPr = p.find('w:pPr', namespaces)
        pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
        pStyle_val = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if pStyle is not None else ""
        text = "".join([t.text for t in p.findall('.//w:t', namespaces) if t.text]).strip()
        
        is_gambar_prefix = re.match(r'^Gambar\s+[0-9]', text, re.IGNORECASE)
        if is_gambar_prefix or (pStyle_val == 'Caption' and text.lower().startswith('gambar')):
            # Look backwards for the nearest drawing paragraph, skipping empty paragraphs
            found_drawing = False
            for j in range(idx - 1, max(idx - 3, -1), -1):
                prev_p = p_list[j]
                prev_text = "".join([t.text for t in prev_p.findall('.//w:t', namespaces) if t.text]).strip()
                if prev_p.find('.//w:drawing', namespaces) is not None:
                    found_drawing = True
                    break
                if prev_text:
                    # Non-empty non-drawing paragraph between drawing and caption = error
                    break
            if not found_drawing:
                # Exception: sequence diagram captions can be consecutive without intervening drawings
                if "sequence diagram" not in text.lower():
                    errors_found.append(f"Gambar caption at paragraph {idx} '{text}' is NOT immediately preceded by a drawing paragraph")
                    
    # I/J. Verify every Gambar caption paragraph has keepNext and keepLines
    print("Checking keepNext/keepLines on Gambar captions...")
    for idx, p in enumerate(p_list):
        is_in_body = (bab1_idx == -1 or idx >= bab1_idx)
        if not is_in_body:
            continue
        pPr = p.find('w:pPr', namespaces)
        pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
        pStyle_val = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if pStyle is not None else ""
        text = "".join([t.text for t in p.findall('.//w:t', namespaces) if t.text]).strip()
        
        is_gambar_prefix = re.match(r'^Gambar\s+[0-9]', text, re.IGNORECASE)
        if is_gambar_prefix or (pStyle_val == 'Caption' and text.lower().startswith('gambar')):
            has_keepNext = pPr is not None and pPr.find('w:keepNext', namespaces) is not None
            has_keepLines = pPr is not None and pPr.find('w:keepLines', namespaces) is not None
            if not has_keepNext:
                errors_found.append(f"Gambar caption {idx} '{text}' is missing w:keepNext (may split from following paragraph)")
            if not has_keepLines:
                errors_found.append(f"Gambar caption {idx} '{text}' is missing w:keepLines (caption may split across pages)")
    
    # H. Check for orphan code text outside code-styled paragraphs
    # After font normalization, code blocks have: sz=18 (9pt) + ind left=720, no Consolas
    print("Checking for orphan code text outside code blocks...")
    code_markers = ['$$ LANGUAGE plpgsql', 'CREATE TRIGGER', 'CREATE OR REPLACE FUNCTION',
                    'EXECUTE FUNCTION', 'RETURNS TRIGGER AS $$']
    ns_w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    for idx, p in enumerate(p_list):
        is_in_body = (bab1_idx == -1 or idx >= bab1_idx)
        if not is_in_body:
            continue
        pPr = p.find('w:pPr', namespaces)
        pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
        pStyle_val = pStyle.get(f'{{{ns_w}}}val') if pStyle is not None else ""
        if 'code' in pStyle_val.lower():
            continue
        # Detect code block by sz=18 (9pt) + ind left=720
        is_code_block = False
        ind_elem = pPr.find('w:ind', namespaces) if pPr is not None else None
        left_val = ind_elem.get(f'{{{ns_w}}}left', '0') if ind_elem is not None else '0'
        if left_val == '720':
            for sz_el in p.findall('.//w:sz', namespaces):
                if sz_el.get(f'{{{ns_w}}}val') == '18':
                    is_code_block = True
                    break
        # Also check for Consolas font (pre-normalization)
        if not is_code_block:
            for rFonts in p.findall('.//w:rFonts', namespaces):
                av = rFonts.get(f'{{{ns_w}}}ascii', '')
                if av.lower() in ['consolas', 'courier new', 'courier']:
                    is_code_block = True
                    break
        if is_code_block:
            continue
        text = "".join([t.text for t in p.findall('.//w:t', namespaces) if t.text]).strip()
        for marker in code_markers:
            if marker in text:
                errors_found.append(f"Paragraph {idx} contains code text '{marker}' outside code block (style='{pStyle_val}')")
    
    # ============================================================ #
    # Content-level figure checks (C1-C4).
    #
    # These ADD failures only; Sections A-J above remain unchanged and run
    # first. None of the checks below short-circuits the build via sys.exit:
    # every defect is appended to errors_found so the final report lists all
    # of them and the process exits non-zero at the end.
    # ============================================================ #
    print("Checking content-level figure invariants (C1 uniqueness, C2 resolution, C3 integrity, C4 page-split)...")

    # Load the manifest + reconciliation allow-lists (BOM tolerant, utf-8-sig).
    manifest_path = os.path.join("images", "manifest.json")
    reconcile_path = os.path.join("images", "manifest_reconcile.json")
    post_com_items = []
    duplicate_allow_groups = []
    unresolved_allow = set()
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8-sig") as f:
            manifest = json.load(f)
        post_com_items = [it for it in manifest.get("images", [])
                          if it.get("inject_method") == "post_com"]
    else:
        errors_found.append(
            f"[content] manifest not found at '{manifest_path}'; cannot run content-level checks.")
    if os.path.exists(reconcile_path):
        with open(reconcile_path, "r", encoding="utf-8-sig") as f:
            rec = json.load(f)
        duplicate_allow_groups = [set(g) for g in rec.get("duplicate_content_allow", [])]
        unresolved_allow = set(rec.get("unresolved_allow", []))

    # Read packed media bytes + the document relationship targets.
    media_bytes = {}
    rel_target = {}
    rels_xml = None
    try:
        with zipfile.ZipFile(docx_path) as z:
            for n in z.namelist():
                if n.startswith("word/media/"):
                    media_bytes[n] = z.read(n)
            try:
                rels_xml = z.read("word/_rels/document.xml.rels")
            except KeyError:
                rels_xml = None
    except Exception as e:
        errors_found.append(f"[content] failed to read media/rels from package: {e}")
    if rels_xml is not None:
        rels_root = ET.fromstring(rels_xml)
        for rel in rels_root:
            rid = rel.get("Id")
            tgt = rel.get("Target")
            if rid and tgt:
                rel_target[rid] = tgt

    body_el = doc_root.find(f'{{{W_NS}}}body')

    # Per-entry resolution feeds C2 (count) and C3 (packed-vs-injected), and
    # records the figure<->media mapping consumed by the C1 allow-list logic.
    target_to_figure = {}  # packed media name -> figure id (for allow-list mapping)
    for item in post_com_items:
        item_id = item.get("id", item.get("file", "<unknown>"))
        caption_match = item.get("caption_match", "")
        img_file = item.get("file", "")
        src_path = os.path.join("images", img_file)

        children, matches = _resolve_caption_indices_content(body_el, caption_match)
        count = len(matches)

        # --- C2: exactly-one caption resolution --------------------------- #
        if count != 1:
            if item_id in unresolved_allow and count == 0:
                print(f"  note: [C2] entry '{item_id}' resolves to 0 captions but is "
                      f"reconciled (unresolved_allow); intentionally skipped.")
                continue
            errors_found.append(
                f"[C2] entry '{item_id}' caption_match '{caption_match}' resolved to {count} "
                f"caption paragraph(s); expected exactly 1 (ambiguous/unresolved caption "
                f"resolution; not exactly one match)."
            )
            continue

        # Map the resolved caption to its preceding drawing's packed media.
        media_name, _drawing_p = _preceding_drawing_media(children, matches[0], rel_target)
        if media_name is None:
            errors_found.append(
                f"[C3] entry '{item_id}' resolves to a caption but no preceding drawing/media "
                f"could be located for content integrity verification."
            )
            continue
        target_to_figure[media_name] = item_id

        packed = media_bytes.get(media_name)
        if packed is None:
            errors_found.append(
                f"[C3] entry '{item_id}' references packed media '{media_name}' which is "
                f"absent from the package; cannot verify content integrity."
            )
            continue
        packed_md5 = _md5_bytes(packed)

        # --- C3: packed media MD5 == injected images/<file> MD5 ----------- #
        if os.path.exists(src_path):
            injected_md5 = _md5_file(src_path)
            if packed_md5 != injected_md5:
                errors_found.append(
                    f"[C3] entry '{item_id}' content integrity mismatch: packed '{media_name}' "
                    f"md5 {packed_md5} does not match injected '{src_path}' md5 {injected_md5} "
                    f"(content drift / recompression)."
                )
        else:
            errors_found.append(
                f"[C3] entry '{item_id}' injected file '{src_path}' is missing on disk; cannot "
                f"verify packed-vs-injected content integrity (md5)."
            )

        # Best-effort, NON-FATAL provenance note for the declared source.
        source = item.get("source")
        if source and os.path.exists(source):
            if _md5_file(source) != packed_md5:
                print(f"  note: [C3] entry '{item_id}' declared source '{source}' differs from "
                      f"the packed media (provenance only, not a failure).")

    # --- C1: media MD5 uniqueness across distinct drawing-referenced media - #
    print("Checking media MD5 uniqueness across injected drawings...")
    md5_to_targets = {}
    if body_el is not None:
        for p in body_el.findall(f'{{{W_NS}}}p'):
            if p.find(f'.//{{{W_NS}}}drawing') is None:
                continue
            blip = p.find(f'.//{{{A_NS}}}blip')
            if blip is None:
                continue
            target = rel_target.get(blip.get(f'{{{R_NS}}}embed'))
            if not target:
                continue
            media_name = 'word/' + target
            packed = media_bytes.get(media_name)
            if packed is None:
                continue
            md5_to_targets.setdefault(_md5_bytes(packed), set()).add(media_name)

    for md5val, targets in md5_to_targets.items():
        if len(targets) < 2:
            continue
        fig_ids = sorted(target_to_figure.get(t, t) for t in targets)
        # Allowed only if every involved figure appears together in one allow group.
        allowed = any(set(fig_ids).issubset(group) for group in duplicate_allow_groups)
        if not allowed:
            errors_found.append(
                f"[C1] duplicate media content: {sorted(targets)} (figures {fig_ids}) share "
                f"identical MD5 {md5val}; distinct figures must reference unique image content. "
                f"Reconcile legitimate reuse via duplicate_content_allow."
            )

    # --- C4: oversized image lacking pageBreakBefore (page-split safety) --- #
    page_height_threshold = _printable_height_emu_content(doc_root)
    print(f"Checking page-split safety (printable page-height threshold {page_height_threshold} EMU)...")
    if body_el is not None:
        for fig_idx, p in enumerate(body_el.findall(f'{{{W_NS}}}p')):
            drawing = p.find(f'.//{{{W_NS}}}drawing')
            if drawing is None:
                continue
            ext = drawing.find(f'.//{{{WP_NS}}}extent')
            if ext is None or ext.get('cy') is None:
                continue
            try:
                cy = int(ext.get('cy'))
            except ValueError:
                continue
            if cy > page_height_threshold:
                pPr = p.find(f'{{{W_NS}}}pPr')
                has_pbb = pPr is not None and pPr.find(f'{{{W_NS}}}pageBreakBefore') is not None
                if not has_pbb:
                    errors_found.append(
                        f"[C4] drawing paragraph {fig_idx} is too tall (image height {cy} EMU > "
                        f"printable page height {page_height_threshold} EMU) but lacks "
                        f"w:pageBreakBefore; the image and its caption can split across a page break."
                    )

    # ============================================================ #
    # Narration guard (WARNING ONLY -- never fatal).
    #
    # For every figure caption ("Gambar X.Y ...") confirm that, within the SAME
    # chapter (Heading1 .. next Heading1), at least one ordinary body paragraph
    # (Normal style, NOT a Caption, NOT a drawing paragraph) references the
    # figure via \bGambar\s+X\.Y\b. If none does, print a clearly-labelled
    # [WARN][narration] line. This DOES NOT append to errors_found and DOES NOT
    # change the exit code.
    # ============================================================ #
    print("Checking figure narration references (non-fatal warnings)...")

    def _h1_val(pp):
        ppr = pp.find('w:pPr', namespaces)
        ps = ppr.find('w:pStyle', namespaces) if ppr is not None else None
        return ps.get(f'{{{W_NS}}}val') if ps is not None else ""

    # Heading1 boundaries (chapter starts) within the document body.
    heading1_idxs = [i for i, pp in enumerate(p_list)
                     if _h1_val(pp) in ('Heading1', 'heading1')]

    def _chapter_range(cap_idx):
        start = 0
        for hi in heading1_idxs:
            if hi <= cap_idx:
                start = hi
            else:
                break
        end = len(p_list)
        for hi in heading1_idxs:
            if hi > cap_idx:
                end = hi
                break
        return start, end

    narration_warnings = []
    for idx, p in enumerate(p_list):
        is_in_body = (bab1_idx == -1 or idx >= bab1_idx)
        if not is_in_body:
            continue
        pStyle_val = _content_style(p)
        text = _content_text(p)
        is_gambar_caption = (re.match(r'^Gambar\s+[0-9]', text, re.IGNORECASE)
                             or (pStyle_val == 'Caption' and text.lower().startswith('gambar')))
        if not is_gambar_caption:
            continue
        m = re.match(r'^Gambar\s+([0-9]+\.[0-9]+)', text, re.IGNORECASE)
        if not m:
            continue
        fig_num = m.group(1)
        ref_re = re.compile(r'\bGambar\s+' + re.escape(fig_num) + r'\b', re.IGNORECASE)
        c_start, c_end = _chapter_range(idx)
        found_ref = False
        for j in range(c_start, c_end):
            if j == idx:
                continue
            q = p_list[j]
            q_style = _content_style(q)
            if q_style == 'Caption':
                continue
            if q.find(f'.//{{{W_NS}}}drawing') is not None:
                continue
            # Treat empty/un-styled body text as Normal narrative; exclude only
            # explicit Caption/drawing paragraphs above.
            q_text = _content_text(q)
            if not q_text:
                continue
            if ref_re.search(q_text):
                found_ref = True
                break
        if not found_ref:
            narration_warnings.append(f"[WARN][narration] Gambar {fig_num} has no referencing narrative paragraph")

    for w in narration_warnings:
        print(w)
    print(f"Narration check: {len(narration_warnings)} figure(s) without a narrative reference (non-fatal).")

    # ============================================================ #
    # Citation guard for Latar Belakang (WARNING ONLY -- never fatal).
    #
    # Academic rule (.kiro/steering/aturan-sitasi.md): the Latar Belakang is the
    # most citation-dense section -- every substantial factual-claim paragraph
    # should carry an APA in-text citation "(... Tahun)". Here we flag any
    # sizeable body paragraph inside the "Latar Belakang" subsection that has no
    # citation, unless it explicitly refers to the author's own data (kuesioner /
    # responden / Lampiran), which is cited to the author's own material instead.
    # This DOES NOT append to errors_found and DOES NOT change the exit code.
    # ============================================================ #
    print("Checking Latar Belakang citations (non-fatal warnings)...")
    CITATION_RE = re.compile(r'\([^()]*(?:19|20)\d{2}[a-z]?\)')
    SELF_DATA_RE = re.compile(r'kuesioner|responden|lampiran|gambar|tabel', re.I)

    def _is_heading(pp):
        return _content_style(pp).lower().startswith('heading')

    # Locate the "Latar Belakang" heading and the extent of its subsection
    # (until the next heading of any level).
    lb_start = -1
    for idx, p in enumerate(p_list):
        if _is_heading(p) and 'latar belakang' in _content_text(p).lower():
            lb_start = idx
            break
    citation_warnings = []
    if lb_start != -1:
        lb_end = len(p_list)
        for j in range(lb_start + 1, len(p_list)):
            if _is_heading(p_list[j]):
                lb_end = j
                break
        for j in range(lb_start + 1, lb_end):
            q = p_list[j]
            if _is_heading(q):
                continue
            style_val = _content_style(q)
            if style_val in ('Caption',) or style_val.startswith('TableofFigures'):
                continue
            if q.find(f'.//{{{W_NS}}}drawing') is not None:
                continue
            q_text = _content_text(q)
            # Only sizeable claim paragraphs (skip short transitions/list lines).
            if len(q_text) < 200:
                continue
            if CITATION_RE.search(q_text):
                continue
            if SELF_DATA_RE.search(q_text):
                continue
            citation_warnings.append(
                f"[WARN][sitasi] Paragraf Latar Belakang tanpa sitasi: '{q_text[:70]}...'")
    else:
        print("  note: 'Latar Belakang' heading not found; citation check skipped.")

    for w in citation_warnings:
        print(w)
    print(f"Citation check: {len(citation_warnings)} Latar Belakang paragraph(s) without a citation (non-fatal).")

    # 3. Report results
    if errors_found:
        print("\n=== VALIDATION FAILED ===")
        for err in errors_found:
            print(f"- {err}")
        sys.exit(1)
    else:
        print("\n=== VALIDATION SUCCESSFUL: No regressions found! ===")
        sys.exit(0)

if __name__ == '__main__':
    main()
