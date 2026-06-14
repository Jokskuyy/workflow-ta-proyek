import xml.etree.ElementTree as ET
import os

def inspect():
    styles_xml_path = 'unpacked_ta/word/styles.xml'
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    tree = ET.parse(styles_xml_path)
    root = tree.getroot()
    
    for style in root.findall('w:style', namespaces):
        style_id = style.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}styleId')
        if style_id in ['Normal', 'Heading1']:
            print(f"Style ID: {style_id}")
            print(ET.tostring(style, encoding='utf-8').decode('utf-8'))
            print("-" * 50)

if __name__ == '__main__':
    inspect()
