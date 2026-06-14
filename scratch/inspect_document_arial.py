import xml.etree.ElementTree as ET
import os

def find_details():
    doc_path = 'unpacked_ta/word/document.xml'
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    
    # We will search using regular expressions or manual element scanning
    # Let's read the XML text and find segments around 'Arial'
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    pos = 0
    while True:
        pos = content.find('Arial', pos)
        if pos == -1:
            break
        start = max(0, pos - 150)
        end = min(len(content), pos + 150)
        print(f"Match at position {pos}:")
        print(f"  ... {content[start:end]} ...")
        print("-" * 50)
        pos += 5

if __name__ == '__main__':
    find_details()
