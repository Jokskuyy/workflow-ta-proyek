import xml.etree.ElementTree as ET
import os

def set_pPr_element(pPr, tag_name, attribs):
    """
    Sets an element inside w:pPr in the correct schema-compliant order:
    w:pStyle, w:numPr, w:spacing, w:ind, w:jc, w:rPr
    tag_name: string without namespace (e.g. 'spacing', 'ind', 'jc')
    attribs: dict of attributes (without namespace)
    """
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    ns_tag = f'{{{ns_uri}}}{tag_name}'
    
    # Create or update the element
    elem = pPr.find(ns_tag)
    if elem is None:
        elem = ET.Element(ns_tag)
        # Find correct position to insert
        # Elements order:
        order = ['pStyle', 'numPr', 'spacing', 'ind', 'jc', 'rPr']
        target_idx = order.index(tag_name)
        
        inserted = False
        for idx, child in enumerate(pPr):
            child_local = child.tag.split('}')[-1]
            if child_local in order:
                child_idx = order.index(child_local)
                if child_idx > target_idx:
                    pPr.insert(idx, elem)
                    inserted = True
                    break
        if not inserted:
            pPr.append(elem)
            
    # Set attributes
    for k, v in attribs.items():
        if v is None:
            # remove attribute if exists
            ns_k = f'{{{ns_uri}}}{k}'
            if ns_k in elem.attrib:
                del elem.attrib[ns_k]
        else:
            elem.set(f'{{{ns_uri}}}{k}', str(v))
            
    return elem

def remove_pPr_element(pPr, tag_name):
    """
    Removes an element inside w:pPr if it exists.
    """
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    ns_tag = f'{{{ns_uri}}}{tag_name}'
    elem = pPr.find(ns_tag)
    if elem is not None:
        pPr.remove(elem)

def format_document(unpacked_dir):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    
    # Register namespaces
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)
        
    styles_path = os.path.join(unpacked_dir, 'word/styles.xml')
    doc_path = os.path.join(unpacked_dir, 'word/document.xml')
    
    # ------------------- 1. MODIFY STYLES.XML -------------------
    if os.path.exists(styles_path):
        print("Modifying styles.xml...")
        styles_tree = ET.parse(styles_path)
        styles_root = styles_tree.getroot()
        
        for style in styles_root.findall('w:style', namespaces):
            style_id = style.get(f'{{{ns_uri}}}styleId')
            style_type = style.get(f'{{{ns_uri}}}type')
            
            if style_type == 'paragraph':
                pPr = style.find('w:pPr', namespaces)
                if pPr is None:
                    pPr = ET.Element(f'{{{ns_uri}}}pPr')
                    style.append(pPr)
                
                # Check style ID
                if style_id == 'Normal':
                    # Normal style: 1.5 line spacing, 0 before/after, justified alignment
                    set_pPr_element(pPr, 'spacing', {'before': '0', 'after': '0', 'line': '360', 'lineRule': 'auto'})
                    set_pPr_element(pPr, 'jc', {'val': 'both'})
                    # default indent is 0
                    set_pPr_element(pPr, 'ind', {'firstLine': '0', 'left': '0'})
                    
                elif style_id == 'ListParagraph':
                    # List style: 1.5 line spacing, 0 before/after
                    set_pPr_element(pPr, 'spacing', {'before': '0', 'after': '0', 'line': '360', 'lineRule': 'auto'})
                    
                elif style_id == 'Caption':
                    # Caption style: 1.0 line spacing, 6pt before/after, centered
                    set_pPr_element(pPr, 'spacing', {'before': '120', 'after': '120', 'line': '240', 'lineRule': 'auto'})
                    set_pPr_element(pPr, 'jc', {'val': 'center'})
                    set_pPr_element(pPr, 'ind', {'firstLine': '0', 'left': '0'})
                    
                elif style_id.startswith('Heading'):
                    # Heading style: 1.5 line spacing, 12pt before, 6pt after
                    set_pPr_element(pPr, 'spacing', {'before': '240', 'after': '120', 'line': '360', 'lineRule': 'auto'})
                    # Headings must explicitly set firstLine=0 to override inherited indent from Normal style
                    set_pPr_element(pPr, 'ind', {'firstLine': '0'})
                    
                    if style_id == 'Heading1':
                        set_pPr_element(pPr, 'jc', {'val': 'center'})
                    else:
                        set_pPr_element(pPr, 'jc', {'val': 'left'})
                        
        # Save styles.xml
        styles_tree.write(styles_path, encoding='utf-8', xml_declaration=True)
        print("styles.xml updated successfully.")
        
    # ------------------- 2. MODIFY DOCUMENT.XML -------------------
    if os.path.exists(doc_path):
        print("Modifying document.xml...")
        doc_tree = ET.parse(doc_path)
        doc_root = doc_tree.getroot()
        body = doc_root.find('w:body', namespaces)
        
        if body is None:
            print("Error: Body element not found in document.xml")
            return
            
        paragraphs = body.findall('w:p', namespaces)
        print(f"Total paragraphs to process: {len(paragraphs)}")
        
        for idx, p in enumerate(paragraphs):
            # Check if this paragraph is inside a table cell (w:tc)
            # Find the path from root to p to see if there is any 'w:tc' ancestor
            # Since ElementTree doesn't easily track parents, we can do a traversal or check if the paragraph
            # is a direct child of body. Actually, a direct child of body has body as parent.
            # In ElementTree, we can construct a parent map:
            pass
            
        # Create parent map
        parent_map = {c: p for p in doc_root.iter() for c in p}
        
        def is_inside_table(p):
            curr = p
            while curr in parent_map:
                parent = parent_map[curr]
                if parent.tag.endswith('tc'):
                    return True
                curr = parent
            return False
            
        for idx, p in enumerate(paragraphs):
            # Skip paragraphs inside table cells
            if is_inside_table(p):
                continue
                
            pPr = p.find('w:pPr', namespaces)
            pStyle_val = "Normal"
            if pPr is not None:
                pStyle = pPr.find('w:pStyle', namespaces)
                if pStyle is not None:
                    pStyle_val = pStyle.get(f'{{{ns_uri}}}val')
            
            # Determine Section: Section 1 is front matter (up to index 58), Section 2 is body (index 59 onwards)
            is_section2 = (idx >= 59)
            
            if is_section2:
                # Main body paragraph formatting
                if pStyle_val == 'Normal':
                    if pPr is None:
                        pPr = ET.Element(f'{{{ns_uri}}}pPr')
                        p.insert(0, pPr)
                        
                    # Check current left indentation. If it has explicit left indent > 0, do not add firstLine indent
                    left_indent = '0'
                    ind_elem = pPr.find('w:ind', namespaces)
                    if ind_elem is not None:
                        left_indent = ind_elem.get(f'{{{ns_uri}}}left', '0')
                        
                    try:
                        left_val = int(left_indent)
                    except ValueError:
                        left_val = 0
                        
                    if left_val > 0:
                        # blockquote or list indent: keep left, no first-line
                        set_pPr_element(pPr, 'ind', {'firstLine': '0'})
                    else:
                        # standard body paragraph: 1.0 cm first-line indent (567 dxa)
                        set_pPr_element(pPr, 'ind', {'firstLine': '567', 'left': '0'})
                        
                    # Enforce alignment: justified (both) unless it has explicit 'center' or 'right'
                    jc_elem = pPr.find('w:jc', namespaces)
                    jc_val = jc_elem.get(f'{{{ns_uri}}}val', 'both') if jc_elem is not None else 'both'
                    if jc_val not in ['center', 'right']:
                        set_pPr_element(pPr, 'jc', {'val': 'both'})
                        
                    # Enforce spacing: 1.5 lines, 0 before/after
                    set_pPr_element(pPr, 'spacing', {'before': '0', 'after': '0', 'line': '360', 'lineRule': 'auto'})
                    
                elif pStyle_val == 'ListParagraph':
                    if pPr is None:
                        pPr = ET.Element(f'{{{ns_uri}}}pPr')
                        p.insert(0, pPr)
                    # Enforce spacing: 1.5 lines, 0 before/after
                    set_pPr_element(pPr, 'spacing', {'before': '0', 'after': '0', 'line': '360', 'lineRule': 'auto'})
                    # Keep its existing w:ind (which holds list indents)
                    
                elif pStyle_val == 'Caption':
                    if pPr is None:
                        pPr = ET.Element(f'{{{ns_uri}}}pPr')
                        p.insert(0, pPr)
                    set_pPr_element(pPr, 'spacing', {'before': '120', 'after': '120', 'line': '240', 'lineRule': 'auto'})
                    set_pPr_element(pPr, 'jc', {'val': 'center'})
                    set_pPr_element(pPr, 'ind', {'firstLine': '0', 'left': '0'})
                    
                elif pStyle_val.startswith('Heading'):
                    if pPr is None:
                        pPr = ET.Element(f'{{{ns_uri}}}pPr')
                        p.insert(0, pPr)
                    # Spacing: 240 dxa before, 120 dxa after, 1.5 line spacing
                    set_pPr_element(pPr, 'spacing', {'before': '240', 'after': '120', 'line': '360', 'lineRule': 'auto'})
                    # Headings must override firstLine to 0
                    set_pPr_element(pPr, 'ind', {'firstLine': '0'})
                    
                    if pStyle_val == 'Heading1':
                        set_pPr_element(pPr, 'jc', {'val': 'center'})
                    else:
                        set_pPr_element(pPr, 'jc', {'val': 'left'})
                        
            else:
                # Section 1 (front matter) paragraph formatting
                if pStyle_val == 'Normal':
                    if pPr is None:
                        pPr = ET.Element(f'{{{ns_uri}}}pPr')
                        p.insert(0, pPr)
                    # Ensure no first-line indent
                    set_pPr_element(pPr, 'ind', {'firstLine': '0'})
                    # Keep alignment if it is center, otherwise default spacing
                    jc_elem = pPr.find('w:jc', namespaces)
                    jc_val = jc_elem.get(f'{{{ns_uri}}}val', 'left') if jc_elem is not None else 'left'
                    if jc_val != 'center':
                        # Default left aligned or both for front matter is fine, keep as is
                        pass
                        
            # Section Break Page Setup
            # Paragraph 58 contains Section 1 properties
            if idx == 58:
                if pPr is not None:
                    sectPr = pPr.find('w:sectPr', namespaces)
                    if sectPr is not None:
                        # Page size to A4
                        set_pPr_element(sectPr, 'pgSz', {'w': '11906', 'h': '16838'})
                        # Margins: Left=2268 (4cm), Right=1701 (3cm), Top=1701 (3cm), Bottom=1701 (3cm)
                        set_pPr_element(sectPr, 'pgMar', {
                            'top': '1701', 'right': '1701', 'bottom': '1701', 'left': '2268',
                            'header': '720', 'footer': '720', 'gutter': '0'
                        })
                        print("Section 1 (front matter) page properties updated.")
                        
        # Modify final section properties directly under w:body
        final_sectPr = body.find('w:sectPr', namespaces)
        if final_sectPr is not None:
            # Page size to A4
            set_pPr_element(final_sectPr, 'pgSz', {'w': '11906', 'h': '16838'})
            # Margins: Left=2268 (4cm), Right=1701 (3cm), Top=1701 (3cm), Bottom=1701 (3cm)
            set_pPr_element(final_sectPr, 'pgMar', {
                'top': '1701', 'right': '1701', 'bottom': '1701', 'left': '2268',
                'header': '720', 'footer': '720', 'gutter': '0'
            })
            print("Section 2 (main body) page properties updated.")
            
        # Save document.xml
        doc_tree.write(doc_path, encoding='utf-8', xml_declaration=True)
        print("document.xml updated successfully.")
        
    # ------------------- 3. REPLACE ARIAL FONT WITH TIMES NEW ROMAN -------------------
    # We will do a direct file text replacement for Arial font references in both XML files
    # to catch any runs, sdt properties, field characters, etc.
    for path in [styles_path, doc_path]:
        if os.path.exists(path):
            print(f"Normalizing font names in {os.path.basename(path)}...")
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Replace Arial font attributes
            new_content = content.replace('w:ascii="Arial"', 'w:ascii="Times New Roman"')
            new_content = new_content.replace('w:hAnsi="Arial"', 'w:hAnsi="Times New Roman"')
            new_content = new_content.replace('w:eastAsia="Arial"', 'w:eastAsia="Times New Roman"')
            new_content = new_content.replace('w:cs="Arial"', 'w:cs="Times New Roman"')
            # Also catch any raw value representation if any
            new_content = new_content.replace('val="Arial"', 'val="Times New Roman"')
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"{os.path.basename(path)} font normalization done.")

if __name__ == '__main__':
    format_document('unpacked_ta')
