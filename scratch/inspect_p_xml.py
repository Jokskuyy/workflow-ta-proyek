import xml.etree.ElementTree as ET
import os

def inspect_p_xml(unpacked_dir):
    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    }
    
    doc_xml_path = os.path.join(unpacked_dir, 'word/document.xml')
    tree = ET.parse(doc_xml_path)
    root = tree.getroot()
    
    print("--- Heading1 Paragraphs XML ---")
    heading_count = 0
    for p in root.findall('.//w:p', namespaces):
        pPr = p.find('w:pPr', namespaces)
        if pPr is not None:
            pStyle = pPr.find('w:pStyle', namespaces)
            if pStyle is not None and pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') == 'Heading1':
                heading_count += 1
                # print XML string of pPr and the first few text runs
                pPr_str = ET.tostring(pPr, encoding='utf-8').decode('utf-8')
                
                # Extract text
                text_parts = [t.text for t in p.findall('.//w:t', namespaces) if t.text]
                text = "".join(text_parts)
                print(f"Heading1 #{heading_count}: '{text}'")
                print(f"  pPr: {pPr_str}\n")
                if heading_count >= 5:
                    break
                    
    print("--- Normal Paragraphs XML (first 5 with left jc) ---")
    normal_count = 0
    for p in root.findall('.//w:p', namespaces):
        pPr = p.find('w:pPr', namespaces)
        if pPr is not None:
            pStyle = pPr.find('w:pStyle', namespaces)
            is_normal = pStyle is not None and pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') == 'Normal'
            # if no pStyle is present, it's also Normal by default
            if is_normal or pStyle is None:
                jc = pPr.find('w:jc', namespaces)
                if jc is not None and jc.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') == 'left':
                    normal_count += 1
                    pPr_str = ET.tostring(pPr, encoding='utf-8').decode('utf-8')
                    text_parts = [t.text for t in p.findall('.//w:t', namespaces) if t.text]
                    text = "".join(text_parts)[:100]
                    print(f"Normal #{normal_count}: '{text}...'")
                    print(f"  pPr: {pPr_str}\n")
                    if normal_count >= 5:
                        break

if __name__ == '__main__':
    inspect_p_xml('unpacked_ta')
