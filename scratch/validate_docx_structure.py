import sys
import os
import zipfile
import re
import xml.etree.ElementTree as ET

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
                if "TOC" in next_p_instr_str and ("9-9" in next_p_instr_str):
                    found_lampiran_toc_field = True
                    print(f"SUCCESS: Found Daftar Lampiran TOC field at paragraph {j}: '{next_p_instr_str}'")
                    break
            if not found_lampiran_toc_field:
                errors_found.append(f"DAFTAR LAMPIRAN heading at paragraph {idx} is not followed by a TOC field targeting level 9-9.")

    print(f"Processed {gambar_count} Gambar captions and {tabel_count} Tabel captions.")
    
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
