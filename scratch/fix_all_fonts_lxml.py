import lxml.etree
import os

W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'

def process_xml_file(filepath):
    parser = lxml.etree.XMLParser(remove_blank_text=False)
    try:
        tree = lxml.etree.parse(filepath, parser)
        root = tree.getroot()
    except Exception as e:
        print(f"Skipping {filepath} due to parsing error: {e}")
        return
        
    modified = False
    
    # Iterate through all elements
    for elem in root.iter():
        tag_local = elem.tag.split('}')[-1]
        
        # 1. Process w:rFonts
        if tag_local == 'rFonts':
            for attr in ['ascii', 'hAnsi', 'eastAsia', 'cs']:
                full_attr = f'{{{W_NS}}}{attr}'
                val = elem.get(full_attr)
                if val and val not in ['Symbol', 'Wingdings', 'Courier New', 'Times New Roman']:
                    elem.set(full_attr, 'Times New Roman')
                    modified = True
                    
            # Remove theme attributes
            theme_attrs = ['asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme']
            has_theme = False
            for attr in theme_attrs:
                full_attr = f'{{{W_NS}}}{attr}'
                if elem.get(full_attr) is not None:
                    elem.attrib.pop(full_attr)
                    has_theme = True
                    modified = True
                    
            if has_theme:
                # Ensure explicit attributes are set to Times New Roman
                for attr in ['ascii', 'hAnsi', 'eastAsia', 'cs']:
                    full_attr = f'{{{W_NS}}}{attr}'
                    val = elem.get(full_attr)
                    if not val or val not in ['Symbol', 'Wingdings', 'Courier New']:
                        elem.set(full_attr, 'Times New Roman')
                        modified = True
                        
        # 2. Process drawingml latin / ea / cs font elements
        elif tag_local in ['latin', 'ea', 'cs'] and elem.tag.startswith(f'{{{A_NS}}}'):
            val = elem.get('typeface')
            if val and val not in ['Symbol', 'Wingdings', 'Courier New', 'Times New Roman']:
                elem.set('typeface', 'Times New Roman')
                modified = True
                
        # 3. Process generic typeface attributes in theme or drawing elements
        elif 'typeface' in elem.attrib:
            val = elem.attrib['typeface']
            if val and val not in ['Symbol', 'Wingdings', 'Courier New', 'Times New Roman']:
                elem.attrib['typeface'] = 'Times New Roman'
                modified = True
                
    if modified:
        try:
            tree.write(filepath, encoding='utf-8', xml_declaration=True)
            print(f"Updated fonts in {filepath}")
        except Exception as e:
            print(f"Error writing {filepath}: {e}")

def walk_and_fix(directory):
    print(f"Recursively fixing fonts in: {directory} using lxml...")
    for root_dir, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.xml') or file.endswith('.rels'):
                process_xml_file(os.path.join(root_dir, file))

if __name__ == '__main__':
    walk_and_fix('unpacked_ta')
