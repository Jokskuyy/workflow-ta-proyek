import lxml.etree
import os
import re
import sys

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
    for child in children:
        parent.remove(child)
    children.sort(key=key_func)
    for child in children:
        parent.append(child)

def set_child_element(parent, tag_name, attribs=None):
    """
    Finds or creates a child element with the given tag_name under parent,
    and sets the specified attributes.
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

def ensure_front_matter_heading_style(styles_root):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    style = styles_root.find("w:style[@w:styleId='FrontMatterHeading']", namespaces)
    if style is None:
        style = lxml.etree.Element(f'{{{ns_uri}}}style')
        style.set(f'{{{ns_uri}}}type', 'paragraph')
        style.set(f'{{{ns_uri}}}styleId', 'FrontMatterHeading')
        
        set_child_element(style, 'name', {'val': 'front matter heading'})
        set_child_element(style, 'basedOn', {'val': 'Normal'})
        set_child_element(style, 'next', {'val': 'Normal'})
        set_child_element(style, 'qFormat', {})
        
        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
        set_child_element(pPr, 'keepNext', {})
        set_child_element(pPr, 'keepLines', {})
        set_child_element(pPr, 'spacing', {'before': '480', 'after': '240'})
        set_child_element(pPr, 'jc', {'val': 'center'})
        set_child_element(pPr, 'outlineLvl', {'val': '0'})
        sort_element_children(pPr, PPR_ORDER)
        style.append(pPr)
        
        rPr = lxml.etree.Element(f'{{{ns_uri}}}rPr')
        set_child_element(rPr, 'rFonts', {'ascii': 'Times New Roman', 'hAnsi': 'Times New Roman'})
        set_child_element(rPr, 'b', {})
        set_child_element(rPr, 'bCs', {})
        set_child_element(rPr, 'sz', {'val': '28'}) # 14pt
        set_child_element(rPr, 'szCs', {'val': '28'})
        style.append(rPr)
        
        sort_element_children(style, STYLE_ORDER)
        styles_root.append(style)
        print("Created FrontMatterHeading style.")

def clean_heading_text_and_add_num(p, level, num_id):
    """
    Cleans manual numbers from heading text and links to native auto-numbering.
    """
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    
    # 1. Join all text inside the paragraph
    text = "".join([t.text for t in p.iter(f'{{{ns_uri}}}t') if t.text])
    
    # 2. Match manual numbering patterns to strip
    pattern = None
    if level == 0:
        # BAB I, BAB II, BAB 3, etc.
        pattern = r'^BAB\s+[IVX0-9]+(?:\.|\s+)?\s*'
    elif level == 1:
        # 1.1, 2.1, etc.
        pattern = r'^[0-9]+\.[0-9]+(?:\.|\s+)?\s*'
    elif level == 2:
        # 2.1.1, etc.
        pattern = r'^[0-9]+\.[0-9]+\.[0-9]+(?:\.|\s+)?\s*'
    elif level == 3:
        # 2.1.1.1, etc.
        pattern = r'^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(?:\.|\s+)?\s*'
        
    cleaned_text = text
    if pattern:
        cleaned_text = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
        print(f"  Stripped heading level {level}: '{text}' -> '{cleaned_text}'")
        
    # 3. Remove all runs (w:r)
    runs = p.findall(f'{{{ns_uri}}}r', namespaces)
    for r in runs:
        p.remove(r)
        
    # 4. Insert a single clean run
    new_r = lxml.etree.Element(f'{{{ns_uri}}}r')
    new_t = lxml.etree.Element(f'{{{ns_uri}}}t')
    new_t.text = cleaned_text
    # Preserve whitespace if necessary
    if cleaned_text.startswith(' ') or cleaned_text.endswith(' '):
        new_t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    new_r.append(new_t)
    p.append(new_r)
    
    # 5. Set numPr inside pPr
    pPr = p.find(f'{{{ns_uri}}}pPr', namespaces)
    if pPr is None:
        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
        p.insert(0, pPr)
        
    numPr = set_child_element(pPr, 'numPr')
    set_child_element(numPr, 'ilvl', {'val': str(level)})
    set_child_element(numPr, 'numId', {'val': str(num_id)})
    
    sort_element_children(pPr, PPR_ORDER)

def clean_bibliography_sdt(sdt_elem):
    """
    Replaces the contents of the bibliography SDT with our clean, APA 7th sorted list of references.
    """
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    
    sdtContent = sdt_elem.find('w:sdtContent', namespaces)
    if sdtContent is None:
        print("Warning: sdtContent not found inside bibliography SDT")
        return
        
    # Remove all children inside sdtContent
    for child in list(sdtContent):
        sdtContent.remove(child)
        
    # Standard APA 7th edition entries (with italic journal/book details)
    refs_data = [
        {
            'plain1': "'Afiifah, K., Azzahra, Z. F., & Anggoro, A. D. (2022). Analisis teknik Entity-Relationship Diagram dalam perancangan database: Sebuah literature review. ",
            'italic': "INTECH (Informatika dan Teknologi)",
            'plain2': ", 3(1), 8\u201314. https://doi.org/10.54895/intech.v3i1.1278"
        },
        {
            'plain1': "Aliyah, A., Hartono, N., & Muin, A. A. (2024). Penggunaan User Acceptance Testing (UAT) pada pengujian sistem informasi pengelolaan keuangan dan inventaris barang. ",
            'italic': "Switch: Jurnal Sains dan Teknologi Informasi",
            'plain2': ", 3(1), 84\u2013100. https://doi.org/10.62951/switch.v3i1.330"
        },
        {
            'plain1': "Ghai, V. (2025). Exploring the future career potential of Blender 3D as a professional tool. ",
            'italic': "International Journal of Advance Research",
            'plain2': ". https://www.ijariit.com/manuscript/exploring-the-future-career-potential-of-blender-3d-as-a-professional-tool/"
        },
        {
            'plain1': "Jamaludin, J., & Saepuloh, L. (2024). Tren riset twin digital smart campus. ",
            'italic': "Sang Pencerah: Jurnal Ilmiah Universitas Muhammadiyah Buton",
            'plain2': ", 10(2), 408\u2013425. https://doi.org/10.35326/pencerah.v10i2.5317"
        },
        {
            'plain1': "Kurniawan, T. A. (2018). Pemodelan Use Case (UML): Evaluasi terhadap beberapa kesalahan dalam praktik. ",
            'italic': "Jurnal Teknologi Informasi dan Ilmu Komputer (JTIIK)",
            'plain2': ", 5(1), 77\u201386. https://doi.org/10.25126/jtiik.201851610"
        },
        {
            'plain1': "Maulida, M., Zahro, F., Hakim, R., & Akbar, M. S. (2025). Pengujian black box testing pada sistem website pemesanan online Toko Ayam Krispy. ",
            'italic': "Jurnal Media Akademik (JMA)",
            'plain2': ", 3(5). https://mediaakademik.com/index.php/jma/article/view/392"
        },
        {
            'plain1': "Muharam, Y., Anggara, M. B., & Hanafi, T. J. (2023). Implementasi peta 3 dimensi menggunakan metode IMSDD (Interactive Multimedia System Design and Development) dan WebGL API berbasis web (Studi kasus di SMP Karya Pembangunan 2 Majalaya). ",
            'italic': "Jurnal Informatika-COMPUTING",
            'plain2': ", 10, 20\u201330. https://doi.org/10.55222/computing.v10i01.1155"
        },
        {
            'plain1': "Siv, T. (2025). A framework for scalable digital twin deployment in smart campus building facility management. ",
            'italic': "arXiv",
            'plain2': ". https://doi.org/10.48550/arXiv.2512.12149"
        },
        {
            'plain1': "Taurusta, C., Asiddiq, A. M., Suprianto, S., & Setiawan, H. (2024). Visualisasi gedung kampus 1 Universitas Muhammadiyah Sidoarjo menggunakan augmented reality sebagai media informasi. ",
            'italic': "Journal of Technology and System Information",
            'plain2': ", 1(1), 55\u201370. https://doi.org/10.47134/jtsi.v1i1.2146"
        }
    ]
    
    for entry in refs_data:
        p = lxml.etree.Element(f'{{{ns_uri}}}p')
        
        # 1. pPr
        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
        set_child_element(pPr, 'pStyle', {'val': 'Normal'})
        set_child_element(pPr, 'ind', {'left': '567', 'hanging': '567'})
        set_child_element(pPr, 'spacing', {'before': '0', 'after': '120', 'line': '240', 'lineRule': 'auto'})
        set_child_element(pPr, 'jc', {'val': 'both'})
        sort_element_children(pPr, PPR_ORDER)
        p.append(pPr)
        
        # 2. Plain run 1
        r1 = lxml.etree.Element(f'{{{ns_uri}}}r')
        t1 = lxml.etree.Element(f'{{{ns_uri}}}t')
        t1.text = entry['plain1']
        t1.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        r1.append(t1)
        p.append(r1)
        
        # 3. Italic run
        r2 = lxml.etree.Element(f'{{{ns_uri}}}r')
        rPr2 = lxml.etree.Element(f'{{{ns_uri}}}rPr')
        set_child_element(rPr2, 'i', {})
        set_child_element(rPr2, 'iCs', {})
        r2.append(rPr2)
        t2 = lxml.etree.Element(f'{{{ns_uri}}}t')
        t2.text = entry['italic']
        t2.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        r2.append(t2)
        p.append(r2)
        
        # 4. Plain run 2
        r3 = lxml.etree.Element(f'{{{ns_uri}}}r')
        t3 = lxml.etree.Element(f'{{{ns_uri}}}t')
        t3.text = entry['plain2']
        t3.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        r3.append(t3)
        p.append(r3)
        
        sdtContent.append(p)
    print("Replaced bibliography entries inside SDT Content.")

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
        
        ensure_front_matter_heading_style(styles_root)
        
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
                    if style_id in ['Heading1', 'Heading2']:
                        set_child_element(pPr, 'spacing', {'before': '240', 'after': '120', 'line': '360', 'lineRule': 'auto'})
                    else:
                        set_child_element(pPr, 'spacing', {'before': '120', 'after': '60', 'line': '360', 'lineRule': 'auto'})
                    set_child_element(pPr, 'ind', {'firstLine': '0'})
                    
                    if style_id == 'Heading1':
                        set_child_element(pPr, 'jc', {'val': 'center'})
                    else:
                        set_child_element(pPr, 'jc', {'val': 'left'})
                
                sort_element_children(pPr, PPR_ORDER)
            sort_element_children(style, STYLE_ORDER)
            
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
            
        children = list(body)
        print(f"Total children in body: {len(children)}")
        
        # We need a parent map to check if elements are inside a table cell (tc)
        parent_map = {c: p for p in doc_root.iter() for c in p}
        
        def is_inside_table(elem):
            curr = elem
            while curr in parent_map:
                parent = parent_map[curr]
                if parent.tag.endswith('tc'):
                    return True
                curr = parent
            return False
            
        # Find index of BAB I PENDAHULUAN
        bab1_idx = -1
        for idx, child in enumerate(children):
            if child.tag.endswith('p'):
                text = "".join([t.text for t in child.iter(f'{{{ns_uri}}}t') if t.text])
                if 'BAB I PENDAHULUAN' in text:
                    bab1_idx = idx
                    break
        
        if bab1_idx == -1:
            print("Warning: BAB I PENDAHULUAN not found. Section 1 will end at index 60 by default.")
            section1_last_p_idx = 60
        else:
            section1_last_p_idx = bab1_idx - 1
            print(f"BAB I PENDAHULUAN found at index {bab1_idx}. Section 1 ends at index {section1_last_p_idx}.")
            
        # Find index of DAFTAR PUSTAKA heading
        daftar_pustaka_heading_idx = -1
        for idx, child in enumerate(children):
            if child.tag.endswith('p'):
                text = "".join([t.text for t in child.iter(f'{{{ns_uri}}}t') if t.text])
                if 'DAFTAR PUSTAKA' in text:
                    pPr = child.find('w:pPr', namespaces)
                    pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                    if pStyle is not None and pStyle.get(f'{{{ns_uri}}}val') == 'Heading1':
                        daftar_pustaka_heading_idx = idx
                        break
                        
        print(f"DAFTAR PUSTAKA Heading1 found at index {daftar_pustaka_heading_idx}.")
        
        # Process children
        for idx, child in enumerate(children):
            # Skip tables themselves
            if child.tag.endswith('tbl'):
                continue
                
            # If child is an sdt (Structured Document Tag)
            if child.tag.endswith('sdt'):
                # We only replace the bibliography SDT if it is located after the DAFTAR PUSTAKA heading!
                if daftar_pustaka_heading_idx != -1 and idx > daftar_pustaka_heading_idx:
                    print(f"Found bibliography SDT at index {idx} (after DAFTAR PUSTAKA heading at {daftar_pustaka_heading_idx}).")
                    clean_bibliography_sdt(child)
                else:
                    print(f"Skipping SDT at index {idx} (either before DAFTAR PUSTAKA heading or heading not found).")
                continue
                
            if child.tag.endswith('p'):
                # Process paragraph
                p = child
                if is_inside_table(p):
                    continue
                    
                pPr = p.find('w:pPr', namespaces)
                pStyle_val = "Normal"
                if pPr is not None:
                    pStyle = pPr.find('w:pStyle', namespaces)
                    if pStyle is not None:
                        pStyle_val = pStyle.get(f'{{{ns_uri}}}val')
                        
                is_section2 = (idx > section1_last_p_idx)
                
                # Check for in-text citation correction: Aliyah Aliyah et al., 2024 -> Aliyah et al., 2024
                # We do this by checking the full joined paragraph text first
                text = "".join([t.text for t in p.iter(f'{{{ns_uri}}}t') if t.text])
                if 'Aliyah Aliyah' in text:
                    print(f"Fixing in-text citation in paragraph #{idx}: '{text[:60]}...'")
                    cleaned_text = text.replace('Aliyah Aliyah et al., 2024', 'Aliyah et al., 2024')
                    # Remove all runs
                    for r in p.findall(f'{{{ns_uri}}}r', namespaces):
                        p.remove(r)
                    # Add a single clean run
                    new_r = lxml.etree.Element(f'{{{ns_uri}}}r')
                    new_t = lxml.etree.Element(f'{{{ns_uri}}}t')
                    new_t.text = cleaned_text
                    new_r.append(new_t)
                    p.append(new_r)
                
                # Format headings and apply auto-numbering
                if pStyle_val.startswith('Heading'):
                    # Check if heading is empty
                    text = "".join([t.text for t in p.iter(f'{{{ns_uri}}}t') if t.text]).strip()
                    if not text:
                        print(f"Empty heading style {pStyle_val} found at index {idx}, changing to Normal style.")
                        if pPr is not None:
                            set_child_element(pPr, 'pStyle', {'val': 'Normal'})
                            # Remove numPr if any
                            numPr = pPr.find(f'{{{ns_uri}}}numPr', namespaces)
                            if numPr is not None:
                                pPr.remove(numPr)
                        continue
                        
                    if pStyle_val == 'Heading1':
                        # If front matter titles like DAFTAR ISI, DAFTAR GAMBAR, DAFTAR TABEL, DAFTAR PUSTAKA
                        if 'DAFTAR' in text.upper():
                            print(f"Front matter title found: '{text}' (using Heading1 but unnumbered)")
                            # Change style to Heading1 (keeps centered & unnumbered)
                            if pPr is None:
                                pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                                p.insert(0, pPr)
                            set_child_element(pPr, 'pStyle', {'val': 'Heading1'})
                            # Remove numPr if any
                            numPr = pPr.find(f'{{{ns_uri}}}numPr', namespaces)
                            if numPr is not None:
                                pPr.remove(numPr)
                        else:
                            # Chapter titles (BAB 1., BAB 2.)
                            clean_heading_text_and_add_num(p, 0, 76)
                            
                    elif pStyle_val == 'Heading2':
                        clean_heading_text_and_add_num(p, 1, 76)
                        
                    elif pStyle_val == 'Heading3':
                        clean_heading_text_and_add_num(p, 2, 76)
                        
                    elif pStyle_val == 'Heading4':
                        clean_heading_text_and_add_num(p, 3, 76)
                        
                    elif pStyle_val == 'Heading5':
                        clean_heading_text_and_add_num(p, 4, 76)
                        
                else:
                    # Regular body paragraph formatting
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
                                # Keep left indent, no firstLine indent
                                set_child_element(pPr, 'ind', {'firstLine': '0'})
                            else:
                                # Normal body indent: 1.0cm (567 dxa)
                                set_child_element(pPr, 'ind', {'firstLine': '567', 'left': '0'})
                                
                            # Enforce justified alignment
                            jc_elem = pPr.find('w:jc', namespaces)
                            jc_val = jc_elem.get(f'{{{ns_uri}}}val', 'both') if jc_elem is not None else 'both'
                            if jc_val not in ['center', 'right']:
                                set_child_element(pPr, 'jc', {'val': 'both'})
                                
                            # Spacing: 1.5 line spacing, 0 before/after
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
                            
                    else:
                        # Section 1 (front matter) Normal paragraph formatting
                        if pStyle_val == 'Normal':
                            if pPr is None:
                                pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                                p.insert(0, pPr)
                            set_child_element(pPr, 'ind', {'firstLine': '0'})
                            
                # Sort elements inside w:pPr
                if pPr is not None:
                    sort_element_children(pPr, PPR_ORDER)
                    
            # Section Break Page Setup for Section 1 (front matter)
            if idx == section1_last_p_idx:
                if p.tag.endswith('p'):
                    pPr = p.find('w:pPr', namespaces)
                    if pPr is None:
                        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                        p.insert(0, pPr)
                    
                    sectPr = set_child_element(pPr, 'sectPr')
                    set_child_element(sectPr, 'type', {'val': 'nextPage'})
                    set_child_element(sectPr, 'pgNumType', {'fmt': 'lowerRoman', 'start': '1'})
                    set_child_element(sectPr, 'pgSz', {'w': '11906', 'h': '16838'})
                    set_child_element(sectPr, 'pgMar', {
                        'top': '1701', 'right': '1701', 'bottom': '1701', 'left': '2268',
                        'header': '720', 'footer': '720', 'gutter': '0'
                    })
                    sort_element_children(sectPr, SECTPR_ORDER)
                    sort_element_children(pPr, PPR_ORDER)
                    print(f"Section 1 (front matter) page properties updated and sorted at paragraph #{idx}.")
                    
        # Final section properties directly under w:body for Section 2 (body)
        final_sectPr = body.find('w:sectPr', namespaces)
        if final_sectPr is not None:
            set_child_element(final_sectPr, 'pgNumType', {'fmt': 'decimal', 'start': '1'})
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
    format_document('unpacked_ta')
