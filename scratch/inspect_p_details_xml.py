import xml.etree.ElementTree as ET
import os

def inspect():
    doc_xml_path = 'unpacked_ta/word/document.xml'
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    tree = ET.parse(doc_xml_path)
    root = tree.getroot()
    body = root.find('w:body', namespaces)
    paragraphs = body.findall('w:p', namespaces)
    
    for idx in range(58, 66):
        p = paragraphs[idx]
        pPr = p.find('w:pPr', namespaces)
        pPr_str = ET.tostring(pPr, encoding='utf-8').decode('utf-8') if pPr is not None else "No pPr"
        text = "".join([t.text for t in p.findall('.//w:t', namespaces) if t.text])
        print(f"Paragraph #{idx} (Text: '{text[:50]}...'):")
        print(f"  pPr: {pPr_str}\n")

if __name__ == '__main__':
    inspect()
