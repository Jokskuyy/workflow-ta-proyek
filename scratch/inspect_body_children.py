import xml.etree.ElementTree as ET
import os
import sys

# Ensure UTF-8 output
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def inspect():
    doc_xml_path = 'unpacked_ta/word/document.xml'
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    tree = ET.parse(doc_xml_path)
    root = tree.getroot()
    body = root.find('w:body', namespaces)
    children = list(body)
    
    print(f"Total children of body: {len(children)}")
    for i in range(max(0, len(children) - 20), len(children)):
        c = children[i]
        tag = c.tag.split('}')[-1]
        text = "".join([t.text for t in c.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if t.text])
        # strip or represent non-ascii characters safely
        safe_text = "".join([char if ord(char) < 128 else f"\\u{ord(char):04x}" for char in text])
        print(f"Child #{i} ({tag}) - text length: {len(safe_text)}, text: '{safe_text[:80]}...'")

if __name__ == '__main__':
    inspect()
