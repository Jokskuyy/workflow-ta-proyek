import xml.etree.ElementTree as ET
import os

def inspect_fonts_xml(xml_path):
    if not os.path.exists(xml_path):
        print(f"{xml_path} not found")
        return
        
    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    }
    
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    rFonts_elems = root.findall('.//w:rFonts', namespaces)
    print(f"\nAnalyzing fonts in {os.path.basename(xml_path)}...")
    print(f"Total <w:rFonts> elements: {len(rFonts_elems)}")
    
    font_attrs = ['ascii', 'hAnsi', 'eastAsia', 'cs', 'asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme']
    unique_fonts = {attr: set() for attr in font_attrs}
    
    for rFonts in rFonts_elems:
        for attr in font_attrs:
            val = rFonts.get(f'{{http://schemas.openxmlformats.org/wordprocessingml/2006/main}}{attr}')
            if val:
                unique_fonts[attr].add(val)
                
    for attr in font_attrs:
        if unique_fonts[attr]:
            print(f"  {attr}: {sorted(list(unique_fonts[attr]))}")

if __name__ == '__main__':
    inspect_fonts_xml('unpacked_ta/word/document.xml')
    inspect_fonts_xml('unpacked_ta/word/styles.xml')
