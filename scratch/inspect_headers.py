import xml.etree.ElementTree as ET
import os

def inspect_headers_footers(unpacked_dir):
    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    }
    
    print("--- HEADERS AND FOOTERS ---")
    files = os.listdir(os.path.join(unpacked_dir, 'word'))
    for file in sorted(files):
        if file.startswith('header') or file.startswith('footer'):
            file_path = os.path.join(unpacked_dir, 'word', file)
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extract text
            text_parts = [t.text for t in root.findall('.//w:t', namespaces) if t.text]
            text = "".join(text_parts).strip()
            print(f"File: {file} - Text: '{text}'")

if __name__ == '__main__':
    inspect_headers_footers('unpacked_ta')
