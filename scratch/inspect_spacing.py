import xml.etree.ElementTree as ET
import os

def inspect_spacing(unpacked_dir):
    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    }
    
    doc_xml_path = os.path.join(unpacked_dir, 'word/document.xml')
    tree = ET.parse(doc_xml_path)
    root = tree.getroot()
    
    spacing_counts = {}
    ind_counts = {}
    
    for p in root.findall('.//w:p', namespaces):
        pStyle_val = "Normal"
        pPr = p.find('w:pPr', namespaces)
        if pPr is not None:
            pStyle = pPr.find('w:pStyle', namespaces)
            if pStyle is not None:
                pStyle_val = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
            
            spacing = pPr.find('w:spacing', namespaces)
            if spacing is not None:
                before = spacing.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}before', '0')
                after = spacing.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}after', '0')
                line = spacing.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}line', 'default')
                key = (before, after, line)
                spacing_counts[pStyle_val] = spacing_counts.get(pStyle_val, {})
                spacing_counts[pStyle_val][key] = spacing_counts[pStyle_val].get(key, 0) + 1
                
            ind = pPr.find('w:ind', namespaces)
            if ind is not None:
                left = ind.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}left', '0')
                firstLine = ind.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}firstLine', '0')
                hanging = ind.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hanging', '0')
                key = (left, firstLine, hanging)
                ind_counts[pStyle_val] = ind_counts.get(pStyle_val, {})
                ind_counts[pStyle_val][key] = ind_counts[pStyle_val].get(key, 0) + 1
                
    print("Spacing counts per style (before, after, line):")
    for style, counts in spacing_counts.items():
        print(f"  Style: {style}")
        for key, count in counts.items():
            print(f"    - {key}: {count}")
            
    print("\nIndentation counts per style (left, firstLine, hanging):")
    for style, counts in ind_counts.items():
        print(f"  Style: {style}")
        for key, count in counts.items():
            print(f"    - {key}: {count}")

if __name__ == '__main__':
    inspect_spacing('unpacked_ta')
