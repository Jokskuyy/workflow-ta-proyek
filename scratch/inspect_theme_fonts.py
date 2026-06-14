import xml.etree.ElementTree as ET
import os

def inspect_theme_fonts(xml_path):
    if not os.path.exists(xml_path):
        print(f"{xml_path} not found")
        return
        
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # We want to search for any tags that specify fonts
    # Common theme font elements are: a:fontScheme, a:majorFont, a:minorFont
    print(f"\nAnalyzing fonts in theme XML: {xml_path}")
    
    namespaces = {
        'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'
    }
    
    for tag in ['.//a:fontScheme', './/a:majorFont', './/a:minorFont', './/a:latin', './/a:ea', './/a:cs']:
        elems = root.findall(tag, namespaces)
        print(f"Elements matching '{tag}': {len(elems)}")
        for e in elems[:5]:
            print(f"  Tag: {e.tag}, Attribs: {e.attrib}")

if __name__ == '__main__':
    inspect_theme_fonts('unpacked_ta/word/theme/theme1.xml')
