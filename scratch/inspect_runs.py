import xml.etree.ElementTree as ET
import os

def inspect_runs(unpacked_dir):
    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    }
    
    doc_xml_path = os.path.join(unpacked_dir, 'word/document.xml')
    tree = ET.parse(doc_xml_path)
    root = tree.getroot()
    
    arial_runs = []
    sz22_runs = []
    
    for p_idx, p in enumerate(root.findall('.//w:p', namespaces)):
        p_text_parts = []
        pStyle = p.find('.//w:pStyle', namespaces)
        style_val = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if pStyle is not None else "Normal"
        
        for r in p.findall('.//w:r', namespaces):
            t_text = "".join([t.text for t in r.findall('.//w:t', namespaces) if t.text])
            if not t_text.strip():
                continue
                
            rPr = r.find('w:rPr', namespaces)
            if rPr is not None:
                rFonts = rPr.find('w:rFonts', namespaces)
                if rFonts is not None:
                    ascii_font = rFonts.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii')
                    if ascii_font == 'Arial':
                        arial_runs.append((p_idx, style_val, t_text))
                sz = rPr.find('w:sz', namespaces)
                if sz is not None:
                    sz_val = sz.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
                    if sz_val == '22':
                        sz22_runs.append((p_idx, style_val, t_text))
                        
    print(f"Total Arial runs: {len(arial_runs)}")
    print("Arial runs sample (first 10):")
    for idx, (p_idx, style, text) in enumerate(arial_runs[:10]):
        print(f"  [{idx}] Paragraph #{p_idx} (Style: {style}): '{text[:60]}...'")
        
    print(f"\nTotal size 22 (11pt) runs: {len(sz22_runs)}")
    print("Size 22 runs sample (first 10):")
    for idx, (p_idx, style, text) in enumerate(sz22_runs[:10]):
        print(f"  [{idx}] Paragraph #{p_idx} (Style: {style}): '{text[:60]}...'")

if __name__ == '__main__':
    inspect_runs('unpacked_ta')
