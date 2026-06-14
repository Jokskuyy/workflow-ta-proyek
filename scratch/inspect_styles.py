import xml.etree.ElementTree as ET
import os

def inspect_styles(unpacked_dir):
    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    }
    
    styles_xml_path = os.path.join(unpacked_dir, 'word/styles.xml')
    if not os.path.exists(styles_xml_path):
        print("styles.xml not found")
        return
        
    tree = ET.parse(styles_xml_path)
    root = tree.getroot()
    
    for style in root.findall('w:style', namespaces):
        style_id = style.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}styleId')
        style_type = style.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}type')
        name_elem = style.find('w:name', namespaces)
        name = name_elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if name_elem is not None else style_id
        
        print(f"Style: {name} (ID: {style_id}, Type: {style_type})")
        
        # Check paragraph properties
        pPr = style.find('w:pPr', namespaces)
        if pPr is not None:
            jc = pPr.find('w:jc', namespaces)
            if jc is not None:
                print(f"  Paragraph Alignment: {jc.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')}")
            spacing = pPr.find('w:spacing', namespaces)
            if spacing is not None:
                before = spacing.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}before')
                after = spacing.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}after')
                line = spacing.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}line')
                line_rule = spacing.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}lineRule')
                print(f"  Spacing: Before={before}, After={after}, Line={line}, LineRule={line_rule}")
                
        # Check run properties
        rPr = style.find('w:rPr', namespaces)
        if rPr is not None:
            rFonts = rPr.find('w:rFonts', namespaces)
            if rFonts is not None:
                ascii_f = rFonts.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii')
                hAnsi = rFonts.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hAnsi')
                print(f"  Font: ascii={ascii_f}, hAnsi={hAnsi}")
            sz = rPr.find('w:sz', namespaces)
            if sz is not None:
                print(f"  Font Size (half-points): {sz.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')}")
            b = rPr.find('w:b', namespaces)
            if b is not None:
                print("  Bold: Yes")
            i = rPr.find('w:i', namespaces)
            if i is not None:
                print("  Italic: Yes")

if __name__ == '__main__':
    inspect_styles('unpacked_ta')
