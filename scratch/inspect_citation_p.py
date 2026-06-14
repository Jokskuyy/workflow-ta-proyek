import xml.etree.ElementTree as ET
import os

def inspect():
    doc_xml_path = 'unpacked_ta/word/document.xml'
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    tree = ET.parse(doc_xml_path)
    root = tree.getroot()
    body = root.find('w:body', namespaces)
    paragraphs = body.findall('.//w:p', namespaces)
    
    for i, p in enumerate(paragraphs):
        text = "".join([t.text for t in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if t.text])
        if 'Aliyah Aliyah' in text:
            print(f"Paragraph #{i} - Text: '{text}'")
            print("Runs:")
            for r_idx, r in enumerate(p.findall('.//w:r', namespaces)):
                r_text = "".join([t.text for t in r.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if t.text])
                print(f"  Run #{r_idx}: '{r_text}'")

if __name__ == '__main__':
    inspect()
