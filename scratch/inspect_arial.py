import xml.etree.ElementTree as ET
import os

def find_arial():
    doc_xml_path = 'unpacked_ta/word/document.xml'
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    tree = ET.parse(doc_xml_path)
    root = tree.getroot()
    
    arial_runs = []
    for p_idx, p in enumerate(root.findall('.//w:p', namespaces)):
        for r_idx, r in enumerate(p.findall('.//w:r', namespaces)):
            rFonts = r.find('.//w:rFonts', namespaces)
            if rFonts is not None:
                ascii_f = rFonts.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii')
                hAnsi_f = rFonts.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hAnsi')
                cs_f = rFonts.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}cs')
                if 'Arial' in [ascii_f, hAnsi_f, cs_f]:
                    text = "".join([t.text for t in r.findall('.//w:t', namespaces) if t.text])
                    arial_runs.append((p_idx, r_idx, ascii_f, hAnsi_f, cs_f, text))
                    
    print(f"Total Arial occurrences: {len(arial_runs)}")
    for p_idx, r_idx, ascii_f, hAnsi_f, cs_f, text in arial_runs:
        print(f"  P #{p_idx}, R #{r_idx}: ascii={ascii_f}, hAnsi={hAnsi_f}, cs={cs_f}, Text='{text}'")

if __name__ == '__main__':
    find_arial()
