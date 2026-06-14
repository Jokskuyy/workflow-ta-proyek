import xml.etree.ElementTree as ET
import os

def inspect_sections(unpacked_dir):
    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    }
    
    doc_xml_path = os.path.join(unpacked_dir, 'word/document.xml')
    tree = ET.parse(doc_xml_path)
    root = tree.getroot()
    
    body = root.find('w:body', namespaces)
    if body is None:
        print("Body not found")
        return
        
    print("--- Section properties in body ---")
    
    # 1. Check for sectPr inside paragraphs (section breaks)
    sectPr_in_p = []
    for idx, p in enumerate(body.findall('w:p', namespaces)):
        pPr = p.find('w:pPr', namespaces)
        if pPr is not None:
            sectPr = pPr.find('w:sectPr', namespaces)
            if sectPr is not None:
                sectPr_in_p.append((idx, sectPr))
                
    print(f"Number of paragraph-level section breaks: {len(sectPr_in_p)}")
    for idx, (p_idx, sectPr) in enumerate(sectPr_in_p):
        pgMar = sectPr.find('w:pgMar', namespaces)
        margin_str = "No pgMar"
        if pgMar is not None:
            top = int(pgMar.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}top', 0)) / 566.9
            bottom = int(pgMar.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}bottom', 0)) / 566.9
            left = int(pgMar.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}left', 0)) / 566.9
            right = int(pgMar.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}right', 0)) / 566.9
            margin_str = f"Top={top:.2f}, Bottom={bottom:.2f}, Left={left:.2f}, Right={right:.2f} cm"
        print(f"  Break #{idx+1} at paragraph #{p_idx}: {margin_str}")
        
    # 2. Check for body-level sectPr (final section)
    final_sectPr = body.find('w:sectPr', namespaces)
    if final_sectPr is not None:
        pgMar = final_sectPr.find('w:pgMar', namespaces)
        margin_str = "No pgMar"
        if pgMar is not None:
            top = int(pgMar.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}top', 0)) / 566.9
            bottom = int(pgMar.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}bottom', 0)) / 566.9
            left = int(pgMar.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}left', 0)) / 566.9
            right = int(pgMar.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}right', 0)) / 566.9
            margin_str = f"Top={top:.2f}, Bottom={bottom:.2f}, Left={left:.2f}, Right={right:.2f} cm"
        print(f"  Final section properties: {margin_str}")

if __name__ == '__main__':
    inspect_sections('unpacked_ta')
