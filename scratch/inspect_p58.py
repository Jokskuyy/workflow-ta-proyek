import xml.etree.ElementTree as ET
import os

def inspect_p58(unpacked_dir):
    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    }
    
    doc_xml_path = os.path.join(unpacked_dir, 'word/document.xml')
    tree = ET.parse(doc_xml_path)
    root = tree.getroot()
    
    body = root.find('w:body', namespaces)
    paragraphs = body.findall('w:p', namespaces)
    
    for idx in range(max(0, 55), min(len(paragraphs), 65)):
        p = paragraphs[idx]
        text_parts = [t.text for t in p.findall('.//w:t', namespaces) if t.text]
        text = "".join(text_parts)
        pPr = p.find('w:pPr', namespaces)
        sectPr_present = (pPr is not None and pPr.find('w:sectPr', namespaces) is not None)
        print(f"Paragraph #{idx}: sectPr={sectPr_present}, Text='{text}'")

if __name__ == '__main__':
    inspect_p58('unpacked_ta')
