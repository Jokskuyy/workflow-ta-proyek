import xml.etree.ElementTree as ET
import os

def check():
    doc_xml_path = 'unpacked_ta/word/document.xml'
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    tree = ET.parse(doc_xml_path)
    root = tree.getroot()
    body = root.find('w:body', namespaces)
    
    jc_counts = {}
    total_p = 0
    p_with_jc = 0
    
    for idx, p in enumerate(body.findall('w:p', namespaces)):
        total_p += 1
        pPr = p.find('w:pPr', namespaces)
        pStyle_val = "Normal"
        if pPr is not None:
            pStyle = pPr.find('w:pStyle', namespaces)
            if pStyle is not None:
                pStyle_val = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
            
            jc = pPr.find('w:jc', namespaces)
            if jc is not None:
                val = jc.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
                key = (pStyle_val, val)
                jc_counts[key] = jc_counts.get(key, 0) + 1
                p_with_jc += 1
                
    print(f"Total paragraphs: {total_p}")
    print(f"Paragraphs with explicit w:jc: {p_with_jc}")
    print("Counts of explicit (Style, w:jc):")
    for key, count in sorted(jc_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {key}: {count}")

if __name__ == '__main__':
    check()
