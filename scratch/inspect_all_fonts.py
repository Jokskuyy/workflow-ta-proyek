import re
import os

def find_font_and_sz_in_xml(xml_path):
    if not os.path.exists(xml_path):
        print(f"File {xml_path} does not exist.")
        return
        
    with open(xml_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Find all occurrences of w:ascii="Arial"
    arial_matches = re.findall(r'<w:rFonts[^>]*w:ascii="Arial"', content)
    print(f"Occurrences of w:ascii=\"Arial\": {len(arial_matches)}")
    
    # Find all occurrences of w:sz w:val="..."
    sz_vals = re.findall(r'<w:sz w:val="([^"]+)"', content)
    sz_counts = {}
    for val in sz_vals:
        sz_counts[val] = sz_counts.get(val, 0) + 1
    print("\nw:sz values and counts in document.xml:")
    for val, count in sorted(sz_counts.items(), key=lambda x: int(x[0])):
        print(f"  - {val} (size {int(val)/2}pt): {count}")

if __name__ == '__main__':
    find_font_and_sz_in_xml('unpacked_ta/word/document.xml')
