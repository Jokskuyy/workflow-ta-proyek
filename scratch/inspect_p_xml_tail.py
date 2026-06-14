import xml.etree.ElementTree as ET
import os

def inspect_tail():
    doc_xml_path = 'unpacked_ta/word/document.xml'
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    tree = ET.parse(doc_xml_path)
    root = tree.getroot()
    body = root.find('w:body', namespaces)
    paragraphs = body.findall('w:p', namespaces)
    
    dp_idx = -1
    for idx, p in enumerate(paragraphs):
        text = "".join([t.text for t in p.findall('.//w:t', namespaces) if t.text])
        if 'DAFTAR PUSTAKA' in text:
            dp_idx = idx
            break
            
    if dp_idx == -1:
        print("DAFTAR PUSTAKA not found")
        return
        
    print(f"DAFTAR PUSTAKA found at paragraph index {dp_idx}")
    for idx in range(dp_idx, len(paragraphs)):
        p = paragraphs[idx]
        pPr = p.find('w:pPr', namespaces)
        pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
        pStyle_val = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if pStyle is not None else "Normal"
        text = "".join([t.text for t in p.findall('.//w:t', namespaces) if t.text])
        print(f"Paragraph #{idx} (Style: {pStyle_val}): '{text[:100]}...'")

if __name__ == '__main__':
    inspect_tail()
