import xml.etree.ElementTree as ET
import os

def inspect():
    doc_xml_path = 'unpacked_ta/word/document.xml'
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    tree = ET.parse(doc_xml_path)
    root = tree.getroot()
    body = root.find('w:body', namespaces)
    children = list(body)
    
    sdt = children[17]
    print(f"SDT tag: {sdt.tag}")
    
    # Let's inspect paragraphs inside sdtContent
    sdtContent = sdt.find('w:sdtContent', namespaces)
    if sdtContent is None:
        print("No sdtContent found")
        return
        
    sdt_children = list(sdtContent)
    print(f"Total children inside sdtContent: {len(sdt_children)}")
    for idx, c in enumerate(sdt_children):
        tag = c.tag.split('}')[-1]
        text = "".join([t.text for t in c.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if t.text])
        pPr = c.find('w:pPr', namespaces)
        pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
        pStyle_val = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if pStyle is not None else "None"
        print(f"  Child #{idx} ({tag}) - Style: {pStyle_val} - text: '{text[:80]}'")

if __name__ == '__main__':
    inspect()
