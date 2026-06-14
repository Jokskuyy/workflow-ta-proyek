import xml.etree.ElementTree as ET
import os

def find():
    doc_xml_path = 'unpacked_ta/word/document.xml'
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    tree = ET.parse(doc_xml_path)
    root = tree.getroot()
    body = root.find('w:body', namespaces)
    paragraphs = body.findall('w:p', namespaces)
    
    for i, p in enumerate(paragraphs):
        text = "".join([t.text for t in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if t.text])
        if 'DAFTAR' in text.upper():
            print(f"Paragraph #{i}: '{text[:100]}'")

if __name__ == '__main__':
    find()
