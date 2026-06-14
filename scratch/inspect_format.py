import xml.etree.ElementTree as ET
import os

def inspect_docx_formatting(unpacked_dir):
    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    }
    
    doc_xml_path = os.path.join(unpacked_dir, 'word/document.xml')
    styles_xml_path = os.path.join(unpacked_dir, 'word/styles.xml')
    
    if not os.path.exists(doc_xml_path):
        print("document.xml not found")
        return
        
    doc_tree = ET.parse(doc_xml_path)
    doc_root = doc_tree.getroot()
    
    print("--- PAGE MARGINS & LAYOUT ---")
    # Find sectPr at the end of body
    body = doc_root.find('w:body', namespaces)
    if body is not None:
        sectPr = body.find('w:sectPr', namespaces)
        if sectPr is not None:
            pgMar = sectPr.find('w:pgMar', namespaces)
            if pgMar is not None:
                # margins are in twentieths of a point (dxa)
                # 1 inch = 1440 dxa, 1 cm = 566.9 dxa
                top = int(pgMar.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}top', 0)) / 566.9
                bottom = int(pgMar.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}bottom', 0)) / 566.9
                left = int(pgMar.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}left', 0)) / 566.9
                right = int(pgMar.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}right', 0)) / 566.9
                print(f"Margins (cm): Top={top:.2f}, Bottom={bottom:.2f}, Left={left:.2f}, Right={right:.2f}")
            else:
                print("pgMar not found in sectPr")
        else:
            print("sectPr not found in body")
            
    print("\n--- STYLES USED & PARAGRAPH PROPERTIES ---")
    style_counts = {}
    fonts_used = set()
    font_sizes = set()
    paragraph_alignments = {}
    line_spacings = {}
    
    for p in doc_root.findall('.//w:p', namespaces):
        # Style
        pStyle_val = "Normal"
        pPr = p.find('w:pPr', namespaces)
        alignment = "left" # default
        line_spacing = "default"
        
        if pPr is not None:
            pStyle = pPr.find('w:pStyle', namespaces)
            if pStyle is not None:
                pStyle_val = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
            
            jc = pPr.find('w:jc', namespaces)
            if jc is not None:
                alignment = jc.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
                
            spacing = pPr.find('w:spacing', namespaces)
            if spacing is not None:
                line_val = spacing.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}line')
                line_rule = spacing.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}lineRule')
                if line_val:
                    line_spacings[pStyle_val] = (line_val, line_rule)
        
        style_counts[pStyle_val] = style_counts.get(pStyle_val, 0) + 1
        
        # Check alignment for normal paragraphs
        if pStyle_val not in paragraph_alignments:
            paragraph_alignments[pStyle_val] = {}
        paragraph_alignments[pStyle_val][alignment] = paragraph_alignments[pStyle_val].get(alignment, 0) + 1
        
        # Runs fonts and sizes
        for r in p.findall('.//w:r', namespaces):
            rPr = r.find('w:rPr', namespaces)
            if rPr is not None:
                rFonts = rPr.find('w:rFonts', namespaces)
                if rFonts is not None:
                    ascii_font = rFonts.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii')
                    if ascii_font:
                        fonts_used.add(ascii_font)
                sz = rPr.find('w:sz', namespaces)
                if sz is not None:
                    sz_val = sz.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
                    if sz_val:
                        font_sizes.add(sz_val)
                        
    print("Paragraph Styles Count:")
    for style, count in sorted(style_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {style}: {count}")
        
    print("\nParagraph Alignments per Style:")
    for style, aligns in paragraph_alignments.items():
        print(f"  - {style}: {aligns}")
        
    print("\nLine Spacing samples per style:")
    for style, spacing in line_spacings.items():
        print(f"  - {style}: line={spacing[0]}, rule={spacing[1]}")
        
    print(f"\nFonts used in runs: {fonts_used}")
    print(f"Font sizes used in runs (half-points, e.g. 24 = 12pt): {sorted(list(font_sizes))}")

if __name__ == '__main__':
    inspect_docx_formatting('unpacked_ta')
