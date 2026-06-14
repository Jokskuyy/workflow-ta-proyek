import xml.etree.ElementTree as ET
import os

def inspect():
    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    }
    
    doc_xml_path = 'unpacked_ta/word/document.xml'
    if not os.path.exists(doc_xml_path):
        print(f"{doc_xml_path} not found.")
        return
        
    tree = ET.parse(doc_xml_path)
    root = tree.getroot()
    body = root.find('w:body', namespaces)
    if body is None:
        print("Body not found.")
        return
        
    children = list(body)
    print(f"Total children: {len(children)}")
    
    # We will traverse all paragraphs, including looking inside sdt blocks.
    # To keep tracking clean, we'll list paragraphs in order.
    paras = []
    
    def process_element(elem):
        tag_local = elem.tag.split('}')[-1]
        if tag_local == 'p':
            paras.append(elem)
        elif tag_local == 'sdt':
            sdtContent = elem.find('w:sdtContent', namespaces)
            if sdtContent is not None:
                for child in sdtContent:
                    process_element(child)
                    
    for child in children:
        process_element(child)
        
    print(f"Total paragraphs found: {len(paras)}")
    
    for i, p in enumerate(paras):
        text = "".join([t.text for t in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if t.text]).strip()
        
        # Check style
        pPr = p.find('w:pPr', namespaces)
        pStyle_val = "Normal"
        has_page_break_before = False
        has_sect_pr = False
        
        if pPr is not None:
            pStyle = pPr.find('w:pStyle', namespaces)
            if pStyle is not None:
                pStyle_val = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
            if pPr.find('w:pageBreakBefore', namespaces) is not None:
                has_page_break_before = True
            if pPr.find('w:sectPr', namespaces) is not None:
                has_sect_pr = True
                
        # Check manual page break
        has_manual_break = False
        for br in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}br'):
            if br.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}type') == 'page':
                has_manual_break = True
                
        # We print paragraph if it is a heading, has any kind of page break/section break, or starts with DAFTAR / BAB
        is_interesting = (
            has_page_break_before or 
            has_sect_pr or 
            has_manual_break or 
            'DAFTAR' in text.upper() or 
            'BAB' in text.upper() or 
            pStyle_val.startswith('Heading') or
            i in [0, 1, 2, 7, 8, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        )
        
        if is_interesting:
            breaks_str = []
            if has_page_break_before: breaks_str.append("pageBreakBefore")
            if has_sect_pr: breaks_str.append("sectionBreak")
            if has_manual_break: breaks_str.append("manualPageBreak")
            breaks_desc = ", ".join(breaks_str) if breaks_str else "None"
            print(f"P #{i:03d} - Style: {pStyle_val:<15} - Breaks: {breaks_desc:<30} - Text: '{text[:80]}'")

if __name__ == '__main__':
    inspect()
