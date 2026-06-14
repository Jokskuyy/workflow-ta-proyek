import xml.etree.ElementTree as ET
import os

def inspect():
    doc_xml_path = 'unpacked_ta/word/document.xml'
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    tree = ET.parse(doc_xml_path)
    root = tree.getroot()
    body = root.find('w:body', namespaces)
    children = list(body)
    
    for i in range(45, 62):
        c = children[i]
        tag = c.tag.split('}')[-1]
        text = "".join([t.text for t in c.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if t.text])
        print(f"Child #{i} ({tag}) - text: '{text}'")

if __name__ == '__main__':
    inspect()
