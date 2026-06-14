import lxml.etree
import os
import re

# Official element order from schemas
PPR_ORDER = [
    'pStyle', 'keepNext', 'keepLines', 'pageBreakBefore', 'framePr', 
    'widowControl', 'numPr', 'suppressLineNumbers', 'pBdr', 'shd', 
    'tabs', 'suppressAutoHyphens', 'kinsoku', 'wordWrap', 'overflowPunct', 
    'topLinePunct', 'autoSpaceDE', 'autoSpaceDN', 'bidi', 'adjustRightInd', 
    'snapToGrid', 'spacing', 'ind', 'contextualSpacing', 'mirrorIndents', 
    'suppressOverlap', 'jc', 'textDirection', 'textAlignment', 'textboxTightWrap', 
    'outlineLvl', 'divId', 'cnfStyle', 'rPr', 'sectPr', 'pPrChange'
]

STYLE_ORDER = [
    'name', 'aliases', 'basedOn', 'next', 'link', 'autoRedefine', 'hidden', 
    'uiPriority', 'semiHidden', 'unhideWhenUsed', 'qFormat', 'locked', 
    'personal', 'personalCompose', 'personalReply', 'rsid', 'pPr', 'rPr', 
    'tblPr', 'trPr', 'tcPr', 'tblStylePr'
]

SECTPR_ORDER = [
    'headerReference', 'footerReference', 'footnotePr', 'endnotePr', 'type',
    'pgSz', 'pgMar', 'paperSrc', 'pgBorders', 'lnNumType', 'pgNumType',
    'cols', 'formProt', 'vAlign', 'noEndnote', 'titlePg', 'textDirection',
    'bidi', 'rtlGutter', 'docGrid', 'printerSettings', 'sectPrChange'
]

def sort_element_children(parent, order_list):
    """
    Sorts the child elements of 'parent' in place according to 'order_list'.
    Elements not in 'order_list' are kept at the end.
    """
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    
    def key_func(child):
        tag = child.tag
        if tag.startswith(f'{{{ns_uri}}}'):
            local_name = tag[len(f'{{{ns_uri}}}'):]
        else:
            local_name = tag.split('}')[-1]
            
        if local_name in order_list:
            return order_list.index(local_name)
        else:
            return len(order_list)
            
    children = list(parent)
    children.sort(key=key_func)
    
    for child in children:
        parent.remove(child)
    for child in children:
        parent.append(child)

def set_child_element(parent, tag_name, attribs=None):
    """
    Finds or creates a child element with the given tag_name under parent,
    and sets the specified attributes (with proper namespace prefixes).
    """
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    ns_tag = f'{{{ns_uri}}}{tag_name}'
    
    elem = parent.find(ns_tag)
    if elem is None:
        elem = lxml.etree.Element(ns_tag)
        parent.append(elem)
        
    if attribs is not None:
        for k, v in attribs.items():
            if k == 'space':
                elem.set('{http://www.w3.org/XML/1998/namespace}space', v)
            elif k.startswith('{'):
                elem.set(k, str(v))
            else:
                elem.set(f'{{{ns_uri}}}{k}', str(v))
                
    return elem

def fix_whitespace_preservation(root):
    """
    Ensures that any w:t element with leading/trailing spaces or non-breaking spaces (\xa0)
    has the xml:space="preserve" attribute.
    """
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    xml_ns = 'http://www.w3.org/XML/1998/namespace'
    
    for t_elem in root.iter(f'{{{ns_uri}}}t'):
        text = t_elem.text
        if text:
            if text.startswith(' ') or text.endswith(' ') or '\xa0' in text or text.startswith('\xa0') or text.endswith('\xa0'):
                t_elem.set(f'{{{xml_ns}}}space', 'preserve')

def format_document(unpacked_dir):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    
    styles_path = os.path.join(unpacked_dir, 'word/styles.xml')
    doc_path = os.path.join(unpacked_dir, 'word/document.xml')
    
    # ------------------- 1. MODIFY STYLES.XML -------------------
    if os.path.exists(styles_path):
        print("Modifying styles.xml...")
        parser = lxml.etree.XMLParser(remove_blank_text=False)
        styles_tree = lxml.etree.parse(styles_path, parser)
        styles_root = styles_tree.getroot()
        
        for style in styles_root.findall('w:style', namespaces):
            style_id = style.get(f'{{{ns_uri}}}styleId')
            style_type = style.get(f'{{{ns_uri}}}type')
            
            if style_type == 'paragraph':
                pPr = style.find('w:pPr', namespaces)
                if pPr is None:
                    pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                    style.append(pPr)
                
                # Check style ID
                if style_id == 'Normal':
                    set_child_element(pPr, 'spacing', {'before': '0', 'after': '0', 'line': '360', 'lineRule': 'auto'})
                    set_child_element(pPr, 'jc', {'val': 'both'})
                    set_child_element(pPr, 'ind', {'firstLine': '0', 'left': '0'})
                    
                elif style_id == 'ListParagraph':
                    set_child_element(pPr, 'spacing', {'before': '0', 'after': '0', 'line': '360', 'lineRule': 'auto'})
                    
                elif style_id == 'Caption':
                    set_child_element(pPr, 'spacing', {'before': '120', 'after': '120', 'line': '240', 'lineRule': 'auto'})
                    set_child_element(pPr, 'jc', {'val': 'center'})
                    set_child_element(pPr, 'ind', {'firstLine': '0', 'left': '0'})
                    
                elif style_id.startswith('Heading'):
                    set_child_element(pPr, 'spacing', {'before': '240', 'after': '120', 'line': '360', 'lineRule': 'auto'})
                    set_child_element(pPr, 'ind', {'firstLine': '0'})
                    
                    if style_id == 'Heading1':
                        set_child_element(pPr, 'jc', {'val': 'center'})
                    else:
                        set_child_element(pPr, 'jc', {'val': 'left'})
                
                # Sort elements inside w:pPr
                sort_element_children(pPr, PPR_ORDER)
            
            # Sort elements inside w:style
            sort_element_children(style, STYLE_ORDER)
            
        # Save styles.xml
        styles_tree.write(styles_path, encoding='utf-8', xml_declaration=True)
        print("styles.xml updated successfully.")
        
    # ------------------- 2. MODIFY DOCUMENT.XML -------------------
    if os.path.exists(doc_path):
        print("Modifying document.xml...")
        parser = lxml.etree.XMLParser(remove_blank_text=False)
        doc_tree = lxml.etree.parse(doc_path, parser)
        doc_root = doc_tree.getroot()
        body = doc_root.find('w:body', namespaces)
        
        if body is None:
            print("Error: Body element not found in document.xml")
            return
            
        paragraphs = body.findall('w:p', namespaces)
        print(f"Total paragraphs to process: {len(paragraphs)}")
        
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
            if is_inside_table(p):
                continue
                
            pPr = p.find('w:pPr', namespaces)
            pStyle_val = "Normal"
            if pPr is not None:
                pStyle = pPr.find('w:pStyle', namespaces)
                if pStyle is not None:
                    pStyle_val = pStyle.get(f'{{{ns_uri}}}val')
            
            is_section2 = (idx >= 59)
            
            if is_section2:
                if pStyle_val == 'Normal':
                    if pPr is None:
                        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                        p.insert(0, pPr)
                        
                    left_indent = '0'
                    ind_elem = pPr.find('w:ind', namespaces)
                    if ind_elem is not None:
                        left_indent = ind_elem.get(f'{{{ns_uri}}}left', '0')
                        
                    try:
                        left_val = int(left_indent)
                    except ValueError:
                        left_val = 0
                        
                    if left_val > 0:
                        set_child_element(pPr, 'ind', {'firstLine': '0'})
                    else:
                        set_child_element(pPr, 'ind', {'firstLine': '567', 'left': '0'})
                        
                    jc_elem = pPr.find('w:jc', namespaces)
                    jc_val = jc_elem.get(f'{{{ns_uri}}}val', 'both') if jc_elem is not None else 'both'
                    if jc_val not in ['center', 'right']:
                        set_child_element(pPr, 'jc', {'val': 'both'})
                        
                    set_child_element(pPr, 'spacing', {'before': '0', 'after': '0', 'line': '360', 'lineRule': 'auto'})
                    
                elif pStyle_val == 'ListParagraph':
                    if pPr is None:
                        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                        p.insert(0, pPr)
                    set_child_element(pPr, 'spacing', {'before': '0', 'after': '0', 'line': '360', 'lineRule': 'auto'})
                    
                elif pStyle_val == 'Caption':
                    if pPr is None:
                        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                        p.insert(0, pPr)
                    set_child_element(pPr, 'spacing', {'before': '120', 'after': '120', 'line': '240', 'lineRule': 'auto'})
                    set_child_element(pPr, 'jc', {'val': 'center'})
                    set_child_element(pPr, 'ind', {'firstLine': '0', 'left': '0'})
                    
                elif pStyle_val.startswith('Heading'):
                    if pPr is None:
                        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                        p.insert(0, pPr)
                    set_child_element(pPr, 'spacing', {'before': '240', 'after': '120', 'line': '360', 'lineRule': 'auto'})
                    set_child_element(pPr, 'ind', {'firstLine': '0'})
                    
                    if pStyle_val == 'Heading1':
                        set_child_element(pPr, 'jc', {'val': 'center'})
                    else:
                        set_child_element(pPr, 'jc', {'val': 'left'})
                        
            else:
                if pStyle_val == 'Normal':
                    if pPr is None:
                        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                        p.insert(0, pPr)
                    set_child_element(pPr, 'ind', {'firstLine': '0'})
            
            # Sort elements inside w:pPr
            if pPr is not None:
                sort_element_children(pPr, PPR_ORDER)
                
            # Paragraph 58 section break page setup
            if idx == 58:
                if pPr is not None:
                    sectPr = pPr.find('w:sectPr', namespaces)
                    if sectPr is not None:
                        set_child_element(sectPr, 'pgSz', {'w': '11906', 'h': '16838'})
                        set_child_element(sectPr, 'pgMar', {
                            'top': '1701', 'right': '1701', 'bottom': '1701', 'left': '2268',
                            'header': '720', 'footer': '720', 'gutter': '0'
                        })
                        # Sort elements inside sectPr
                        sort_element_children(sectPr, SECTPR_ORDER)
                        print("Section 1 (front matter) page properties updated and sorted.")
                        
        # Final section properties directly under w:body
        final_sectPr = body.find('w:sectPr', namespaces)
        if final_sectPr is not None:
            set_child_element(final_sectPr, 'pgSz', {'w': '11906', 'h': '16838'})
            set_child_element(final_sectPr, 'pgMar', {
                'top': '1701', 'right': '1701', 'bottom': '1701', 'left': '2268',
                'header': '720', 'footer': '720', 'gutter': '0'
            })
            sort_element_children(final_sectPr, SECTPR_ORDER)
            print("Section 2 (main body) page properties updated and sorted.")
            
        # Fix whitespace preservation
        fix_whitespace_preservation(doc_root)
        
        # Save document.xml
        doc_tree.write(doc_path, encoding='utf-8', xml_declaration=True)
        print("document.xml updated successfully.")
        
    # ------------------- 3. REPLACE ARIAL FONT WITH TIMES NEW ROMAN -------------------
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
            new_content = new_content.replace('val="Arial"', 'val="Times New Roman"')
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"{os.path.basename(path)} font normalization done.")

if __name__ == '__main__':
    format_document('unpacked_fresh')
