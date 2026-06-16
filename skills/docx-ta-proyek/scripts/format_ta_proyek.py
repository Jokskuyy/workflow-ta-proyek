import lxml.etree
import os
import re
import sys

# Official element order from OOXML schemas
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
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    def key_func(child):
        tag = child.tag
        local_name = tag[len(f'{{{ns_uri}}}'):] if tag.startswith(f'{{{ns_uri}}}') else tag.split('}')[-1]
        return order_list.index(local_name) if local_name in order_list else len(order_list)
        
    children = list(parent)
    for child in children: parent.remove(child)
    children.sort(key=key_func)
    for child in children: parent.append(child)

def set_child_element(parent, tag_name, attribs=None):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    ns_tag = f'{{{ns_uri}}}{tag_name}'
    elem = parent.find(ns_tag)
    if elem is None:
        elem = lxml.etree.Element(ns_tag)
        parent.append(elem)
    if attribs is not None:
        for k, v in attribs.items():
            if k == 'space': elem.set('{http://www.w3.org/XML/1998/namespace}space', v)
            elif k.startswith('{'): elem.set(k, str(v))
            else: elem.set(f'{{{ns_uri}}}{k}', str(v))
    return elem

def fix_whitespace_preservation(root):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    xml_ns = 'http://www.w3.org/XML/1998/namespace'
    for t_elem in root.iter(f'{{{ns_uri}}}t'):
        text = t_elem.text
        if text and (text.startswith(' ') or text.endswith(' ') or '\xa0' in text):
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
        set_child_element(rPr, 'sz', {'val': '28'})
        set_child_element(rPr, 'szCs', {'val': '28'})
        style.append(rPr)
        sort_element_children(style, STYLE_ORDER)
        styles_root.append(style)

def ensure_appendix_heading_style(styles_root):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    style = styles_root.find("w:style[@w:styleId='taappendixheading']", namespaces)
    if style is None:
        style = lxml.etree.Element(f'{{{ns_uri}}}style')
        style.set(f'{{{ns_uri}}}type', 'paragraph')
        style.set(f'{{{ns_uri}}}styleId', 'taappendixheading')
        set_child_element(style, 'name', {'val': 'taappendixheading'})
        set_child_element(style, 'basedOn', {'val': 'Normal'})
        set_child_element(style, 'next', {'val': 'Normal'})
        set_child_element(style, 'qFormat', {})
        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
        set_child_element(pPr, 'keepNext', {})
        set_child_element(pPr, 'keepLines', {})
        set_child_element(pPr, 'pageBreakBefore', {})
        set_child_element(pPr, 'spacing', {'before': '240', 'after': '120'})
        set_child_element(pPr, 'jc', {'val': 'center'})
        set_child_element(pPr, 'outlineLvl', {'val': '8'})
        sort_element_children(pPr, PPR_ORDER)
        style.append(pPr)
        rPr = lxml.etree.Element(f'{{{ns_uri}}}rPr')
        set_child_element(rPr, 'rFonts', {'ascii': 'Times New Roman', 'hAnsi': 'Times New Roman'})
        set_child_element(rPr, 'b', {})
        set_child_element(rPr, 'bCs', {})
        set_child_element(rPr, 'sz', {'val': '28'})
        set_child_element(rPr, 'szCs', {'val': '28'})
        style.append(rPr)
        sort_element_children(style, STYLE_ORDER)
        styles_root.append(style)
        print("Successfully defined taappendixheading style in styles.xml")

def ensure_toc9_style(styles_root):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    style = styles_root.find("w:style[@w:styleId='TOC9']", namespaces)
    if style is None:
        style = lxml.etree.Element(f'{{{ns_uri}}}style')
        style.set(f'{{{ns_uri}}}type', 'paragraph')
        style.set(f'{{{ns_uri}}}styleId', 'TOC9')
        set_child_element(style, 'name', {'val': 'toc 9'})
        set_child_element(style, 'basedOn', {'val': 'Normal'})
        set_child_element(style, 'next', {'val': 'Normal'})
        set_child_element(style, 'qFormat', {})
        styles_root.append(style)
        
    pPr = style.find('w:pPr', namespaces)
    if pPr is None:
        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
        style.append(pPr)
    
    set_child_element(pPr, 'spacing', {'before': '0', 'after': '0', 'line': '360', 'lineRule': 'auto'})
    set_child_element(pPr, 'ind', {'left': '1'})
    set_child_element(pPr, 'jc', {'val': 'left'})
    sort_element_children(pPr, PPR_ORDER)
    
    rPr = style.find('w:rPr', namespaces)
    if rPr is None:
        rPr = lxml.etree.Element(f'{{{ns_uri}}}rPr')
        style.append(rPr)
        
    set_child_element(rPr, 'rFonts', {'ascii': 'Times New Roman', 'hAnsi': 'Times New Roman'})
    set_child_element(rPr, 'sz', {'val': '24'})
    set_child_element(rPr, 'szCs', {'val': '24'})
    
    # Remove any bold/italic elements to keep the text plain
    for tag in ['b', 'bCs', 'i', 'iCs']:
        elem = rPr.find(f'w:{tag}', namespaces)
        if elem is not None:
            rPr.remove(elem)
            
    sort_element_children(style, STYLE_ORDER)
    print("Successfully defined or updated TOC9 style in styles.xml")

def ensure_hyperlink_style(styles_root):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    STYLE_ORDER = [
        'name', 'aliases', 'basedOn', 'next', 'link', 'autoRedefine', 'hidden', 
        'uiPriority', 'semiHidden', 'unhideWhenUsed', 'qFormat', 'locked', 
        'personal', 'personalCompose', 'personalReply', 'rsid', 'pPr', 'rPr', 
        'tblPr', 'trPr', 'tcPr', 'tblStylePr'
    ]
    style = styles_root.find("w:style[@w:styleId='Hyperlink']", namespaces)
    if style is None:
        style = lxml.etree.Element(f'{{{ns_uri}}}style')
        style.set(f'{{{ns_uri}}}type', 'character')
        style.set(f'{{{ns_uri}}}styleId', 'Hyperlink')
        set_child_element(style, 'name', {'val': 'Hyperlink'})
        set_child_element(style, 'basedOn', {'val': 'DefaultParagraphFont'})
        set_child_element(style, 'uiPriority', {'val': '99'})
        set_child_element(style, 'unhideWhenUsed', {})
        
        rPr = lxml.etree.Element(f'{{{ns_uri}}}rPr')
        set_child_element(rPr, 'color', {'val': '000000', 'themeColor': 'text1'})
        set_child_element(rPr, 'u', {'val': 'none'})
        style.append(rPr)
        
        sort_element_children(style, STYLE_ORDER)
        styles_root.append(style)
    else:
        rPr = style.find('w:rPr', namespaces)
        if rPr is None:
            rPr = lxml.etree.Element(f'{{{ns_uri}}}rPr')
            style.append(rPr)
        set_child_element(rPr, 'color', {'val': '000000', 'themeColor': 'text1'})
        set_child_element(rPr, 'u', {'val': 'none'})


def clean_heading_text_and_add_num(p, level, num_id):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    text = "".join([t.text for t in p.iter(f'{{{ns_uri}}}t') if t.text])
    
    # Strip manual numbering pattern
    pattern = None
    if level == 0: pattern = r'^BAB\s+[IVX0-9]+(?:\.|\s+)?\s*'
    elif level == 1: pattern = r'^[0-9]+\.[0-9]+(?:\.|\s+)?\s*'
    elif level == 2: pattern = r'^[0-9]+\.[0-9]+\.[0-9]+(?:\.|\s+)?\s*'
    elif level == 3: pattern = r'^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(?:\.|\s+)?\s*'
    
    cleaned_text = text
    if pattern:
        cleaned_text = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
        print(f"  Stripped heading level {level}: '{text}' -> '{cleaned_text}'")
        
    for r in p.findall(f'{{{ns_uri}}}r', namespaces):
        p.remove(r)
        
    new_r = lxml.etree.Element(f'{{{ns_uri}}}r')
    new_t = lxml.etree.Element(f'{{{ns_uri}}}t')
    new_t.text = cleaned_text
    if cleaned_text.startswith(' ') or cleaned_text.endswith(' '):
        new_t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    new_r.append(new_t)
    p.append(new_r)
    
    pPr = p.find(f'{{{ns_uri}}}pPr', namespaces)
    if pPr is None:
        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
        p.insert(0, pPr)
        
    numPr = set_child_element(pPr, 'numPr')
    set_child_element(numPr, 'ilvl', {'val': str(level)})
    set_child_element(numPr, 'numId', {'val': str(num_id)})
    
    # Direct formatting override to ensure headings are left-aligned with no indent
    set_child_element(pPr, 'ind', {'left': '0', 'firstLine': '0'})
    if level == 0:
        set_child_element(pPr, 'pageBreakBefore', {})
        
    sort_element_children(pPr, PPR_ORDER)

def clean_bibliography_sdt(sdt_elem):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    sdtContent = sdt_elem.find('w:sdtContent', namespaces)
    if sdtContent is None: return
    for child in list(sdtContent): sdtContent.remove(child)
    
    # Standard APA 7th edition entries (with single line spacing 240 dxa)
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
        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
        set_child_element(pPr, 'pStyle', {'val': 'Normal'})
        set_child_element(pPr, 'ind', {'left': '567', 'hanging': '567'})
        set_child_element(pPr, 'spacing', {'before': '0', 'after': '120', 'line': '240', 'lineRule': 'auto'})
        set_child_element(pPr, 'jc', {'val': 'both'})
        sort_element_children(pPr, PPR_ORDER)
        p.append(pPr)
        
        r1 = lxml.etree.Element(f'{{{ns_uri}}}r')
        t1 = lxml.etree.Element(f'{{{ns_uri}}}t')
        t1.text = entry['plain1']
        t1.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        r1.append(t1)
        p.append(r1)
        
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
        
        r3 = lxml.etree.Element(f'{{{ns_uri}}}r')
        t3 = lxml.etree.Element(f'{{{ns_uri}}}t')
        t3.text = entry['plain2']
        t3.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        r3.append(t3)
        p.append(r3)
        
        sdtContent.append(p)
    print("Replaced bibliography entries inside SDT.")

def load_rels_map(unpacked_dir):
    rels_path = os.path.join(unpacked_dir, 'word', '_rels', 'document.xml.rels')
    rel_map = {}
    if os.path.exists(rels_path):
        try:
            tree = lxml.etree.parse(rels_path)
            root = tree.getroot()
            for rel in root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
                rel_id = rel.get('Id')
                target = rel.get('Target')
                if rel_id and target:
                    rel_map[rel_id] = target
        except Exception as e:
            print(f"Error loading relationships from {rels_path}: {e}")
    return rel_map

def scale_cover_drawings(p, namespaces, unpacked_dir=None, rel_map=None):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    drawings = p.findall('.//w:drawing', namespaces)
    if not drawings:
        return
        
    pPr = p.find('w:pPr', namespaces)
    if pPr is None:
        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
        p.insert(0, pPr)
    set_child_element(pPr, 'jc', {'val': 'center'})
    set_child_element(pPr, 'ind', {'left': '0', 'firstLine': '0'})
    sort_element_children(pPr, PPR_ORDER)
    
    max_width_emu = 1800000   # 5.0 cm
    max_height_emu = 1800000  # 5.0 cm
    
    for drawing in drawings:
        aspect_ratio = None
        if unpacked_dir and rel_map:
            blip = drawing.find('.//a:blip', {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'})
            if blip is not None:
                embed_id = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                if embed_id and embed_id in rel_map:
                    rel_target = rel_map[embed_id]
                    img_path = os.path.join(unpacked_dir, 'word', rel_target)
                    if os.path.exists(img_path):
                        try:
                            from PIL import Image
                            with Image.open(img_path) as img:
                                img_w, img_h = img.size
                                if img_h > 0:
                                    aspect_ratio = img_w / img_h
                        except Exception as e:
                            print(f"  Error reading cover image aspect ratio: {e}")

        for elem in drawing.iter():
            tag_local = elem.tag.split('}')[-1]
            if tag_local in ['extent', 'ext']:
                cx_str = elem.get('cx')
                cy_str = elem.get('cy')
                if cx_str and cy_str:
                    try:
                        cx = int(cx_str)
                        cy = int(cy_str)
                        if aspect_ratio is not None:
                            cy = int(cx / aspect_ratio)
                            elem.set('cy', str(cy))
                            
                        scale_x = max_width_emu / cx
                        scale_y = max_height_emu / cy
                        scale = min(scale_x, scale_y, 1.0)
                        if scale < 1.0:
                            elem.set('cx', str(int(cx * scale)))
                            elem.set('cy', str(int(cy * scale)))
                            print(f"  Scaled cover drawing to {scale * 100:.2f}% of original size")
                    except ValueError:
                        pass

def center_and_scale_drawings(p, namespaces, unpacked_dir=None, rel_map=None):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    drawings = p.findall('.//w:drawing', namespaces)
    if not drawings:
        return
        
    # Set paragraph alignment to center and clear indents on the figure paragraph
    pPr = p.find('w:pPr', namespaces)
    if pPr is None:
        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
        p.insert(0, pPr)
    set_child_element(pPr, 'jc', {'val': 'center'})
    set_child_element(pPr, 'ind', {'left': '0', 'firstLine': '0'})
    sort_element_children(pPr, PPR_ORDER)
    
    max_width_emu = 5040000  # 14.0cm in EMUs
    
    for drawing in drawings:
        aspect_ratio = None
        if unpacked_dir and rel_map:
            blip = drawing.find('.//a:blip', {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'})
            if blip is not None:
                embed_id = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                if embed_id and embed_id in rel_map:
                    rel_target = rel_map[embed_id]
                    img_path = os.path.join(unpacked_dir, 'word', rel_target)
                    if os.path.exists(img_path):
                        try:
                            from PIL import Image
                            with Image.open(img_path) as img:
                                img_w, img_h = img.size
                                if img_h > 0:
                                    aspect_ratio = img_w / img_h
                        except Exception as e:
                            print(f"  Error reading image aspect ratio: {e}")

        if aspect_ratio is not None:
            for elem in drawing.iter():
                tag_local = elem.tag.split('}')[-1]
                if tag_local in ['extent', 'ext']:
                    cx_str = elem.get('cx')
                    if cx_str:
                        try:
                            cx = int(cx_str)
                            cy = int(cx / aspect_ratio)
                            elem.set('cy', str(cy))
                        except ValueError:
                            pass
                elif tag_local == 'srcRect':
                    for attr in list(elem.attrib.keys()):
                        elem.attrib.pop(attr)

        max_cx = 0
        for elem in drawing.iter():
            tag_local = elem.tag.split('}')[-1]
            if tag_local in ['extent', 'ext']:
                cx_str = elem.get('cx')
                if cx_str:
                    try:
                        max_cx = max(max_cx, int(cx_str))
                    except ValueError:
                        pass
                        
        if max_cx > max_width_emu:
            scale_factor = max_width_emu / max_cx
            print(f"  Scaling drawing in paragraph to {scale_factor * 100:.2f}% of original size")
            for elem in drawing.iter():
                tag_local = elem.tag.split('}')[-1]
                if tag_local in ['extent', 'ext']:
                    cx_str = elem.get('cx')
                    cy_str = elem.get('cy')
                    if cx_str and cy_str:
                        try:
                            new_cx = int(int(cx_str) * scale_factor)
                            new_cy = int(int(cy_str) * scale_factor)
                            elem.set('cx', str(new_cx))
                            elem.set('cy', str(new_cy))
                        except ValueError:
                            pass

def build_toc_entry(caption_text, page_num, bookmark_name):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    
    def set_child_element(parent, tag_name, attrs=None):
        el = lxml.etree.SubElement(parent, f'{{{ns_uri}}}{tag_name}')
        if attrs:
            for k, v in attrs.items():
                el.set(f'{{{ns_uri}}}{k}', v)
        return el

    PPR_ORDER = [
        'pStyle', 'keepNext', 'keepLines', 'pageBreakBefore', 'framePr',
        'widowControl', 'numPr', 'suppressLineNumbers', 'pBdr', 'shd',
        'tabs', 'suppressAutoHyphens', 'kinsoku', 'wordWrap', 'overflowPunct',
        'topLinePunct', 'autoSpaceDE', 'autoSpaceDN', 'bidi', 'adjustRightInd',
        'snapToGrid', 'spacing', 'ind', 'contextualSpacing', 'mirrorIndents',
        'suppressOverlap', 'jc', 'textDirection', 'textAlignment', 'textboxTightWrap',
        'outlineLvl', 'divId', 'cnfStyle', 'rPr', 'sectPr', 'pPrChange'
    ]

    def sort_element_children(parent, order_list):
        def key_func(child):
            tag = child.tag
            local_name = tag[len(f'{{{ns_uri}}}'):] if tag.startswith(f'{{{ns_uri}}}') else tag.split('}')[-1]
            return order_list.index(local_name) if local_name in order_list else len(order_list)
        children = list(parent)
        for child in children: parent.remove(child)
        children.sort(key=key_func)
        for child in children: parent.append(child)

    p = lxml.etree.Element(f'{{{ns_uri}}}p')
    pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
    
    set_child_element(pPr, 'pStyle', {'val': 'TableofFigures'})
    
    rPr_ppr = lxml.etree.Element(f'{{{ns_uri}}}rPr')
    set_child_element(rPr_ppr, 'noProof', {})
    pPr.append(rPr_ppr)
    
    tabs = lxml.etree.Element(f'{{{ns_uri}}}tabs')
    set_child_element(tabs, 'tab', {'val': 'right', 'leader': 'dot', 'pos': '7927'})
    pPr.append(tabs)
    
    sort_element_children(pPr, PPR_ORDER)
    p.append(pPr)
    
    # Hyperlink element
    hyperlink = lxml.etree.SubElement(p, f'{{{ns_uri}}}hyperlink', {'{'+ns_uri+'}anchor': bookmark_name, '{'+ns_uri+'}history': '1'})
    
    # Caption text run
    r = lxml.etree.SubElement(hyperlink, f'{{{ns_uri}}}r')
    rPr = lxml.etree.SubElement(r, f'{{{ns_uri}}}rPr')
    set_child_element(rPr, 'noProof', {})
    t = lxml.etree.SubElement(r, f'{{{ns_uri}}}t')
    t.text = caption_text
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    
    # Tab run (for dot leader)
    tab_r = lxml.etree.SubElement(hyperlink, f'{{{ns_uri}}}r')
    tab_rPr = lxml.etree.SubElement(tab_r, f'{{{ns_uri}}}rPr')
    set_child_element(tab_rPr, 'noProof', {})
    set_child_element(tab_rPr, 'webHidden', {})
    lxml.etree.SubElement(tab_r, f'{{{ns_uri}}}tab')
    
    # Page number run
    page_r = lxml.etree.SubElement(hyperlink, f'{{{ns_uri}}}r')
    page_rPr = lxml.etree.SubElement(page_r, f'{{{ns_uri}}}rPr')
    set_child_element(page_rPr, 'noProof', {})
    set_child_element(page_rPr, 'webHidden', {})
    page_t = lxml.etree.SubElement(page_r, f'{{{ns_uri}}}t')
    page_t.text = str(page_num)
    
    return p

def replace_mentions_in_paragraph(text):
    # Rule 1: Wawancara / Mitra (Gambar 2.25 -> Gambar 2.8)
    if "Wakil Rektor" in text and "pakta integritas" in text and "Gambar 2.25" in text:
        text = text.replace("Gambar 2.25", "Gambar 2.8")
        
    # Rule 2: Diagram Arsitektur (Gambar 2.1 -> Gambar 2.9)
    if "arsitektur sistem secara high-level" in text and "Gambar 2.1" in text:
        text = text.replace("Gambar 2.1", "Gambar 2.9")
    if "diilustrasikan pada Gambar 2.1" in text:
        text = text.replace("Gambar 2.1", "Gambar 2.9")
        
    # Rule 3: Arsitektur Integrasi (Gambar 2.15 -> Gambar 2.10)
    if "Arsitektur Integrasi" in text and "Gambar 2.15" in text:
        text = text.replace("Gambar 2.15", "Gambar 2.10")
    if "unity_object_name" in text and "Gambar 2.15" in text:
        text = text.replace("Gambar 2.15", "Gambar 2.10")
        
    # Rule 4: Tahap Pengembangan (Gambar 2.9 -> Gambar 2.11)
    if "telah ditetapkan" in text and "Gambar 2.9" in text:
        text = text.replace("Gambar 2.9", "Gambar 2.11")
    if "Alur waktu pelaksanaan" in text and "Gambar 2.9" in text:
        text = text.replace("Gambar 2.9", "Gambar 2.11")
        
    # Rule 5: ERD (Gambar 2.10 -> Gambar 2.12)
    if "skema database PostgreSQL" in text and "Gambar 2.10" in text:
        text = text.replace("Gambar 2.10", "Gambar 2.12")
    if "Skema ERD divisualisasikan" in text and "Gambar 2.10" in text:
        text = text.replace("Gambar 2.10", "Gambar 2.12")
        
    # Rule 6: Legenda Use Case (Gambar 2.11 -> Gambar 2.13)
    if "legenda" in text and "Gambar 2.11" in text:
        text = text.replace("Gambar 2.11", "Gambar 2.13")
        
    # Rule 7: Use Case (Gambar 2.12 -> Gambar 2.14)
    if "Use Case Diagram" in text and "Gambar 2.12" in text:
        text = text.replace("Gambar 2.12", "Gambar 2.14")
    if "hak akses read-only" in text and "Gambar 2.12" in text:
        text = text.replace("Gambar 2.12", "Gambar 2.14")
        
    # Rule 8: Activity Admin (Gambar 2.13 -> Gambar 2.15)
    if "Activity Diagram" in text and "Gambar 2.13" in text:
        text = text.replace("Gambar 2.13", "Gambar 2.15")
    if "pengelolaan data oleh administrator" in text and "Gambar 2.13" in text:
        text = text.replace("Gambar 2.13", "Gambar 2.15")
        
    # Rule 9: Activity Denah (Gambar 2.14 -> Gambar 2.16)
    if "Activity Diagram" in text and "Gambar 2.14" in text:
        text = text.replace("Gambar 2.14", "Gambar 2.16")
    if "mitigasi" in text and "Gambar 2.14" in text:
        text = text.replace("Gambar 2.14", "Gambar 2.16")
        
    # Rule 10: Halaman Login (Gambar 2.16 -> Gambar 2.17)
    if "autentikasi" in text and "Gambar 2.16" in text:
        text = text.replace("Gambar 2.16", "Gambar 2.17")
    if "halaman login admin" in text and "Gambar 2.16" in text:
        text = text.replace("Gambar 2.16", "Gambar 2.17")
        
    # Rule 11: Dashboard Admin (Gambar 2.17 -> Gambar 2.18)
    if "pusat pengelolaan data" in text and "Gambar 2.17" in text:
        text = text.replace("Gambar 2.17", "Gambar 2.18")
    if "halaman utama dashboard admin" in text and "Gambar 2.17" in text:
        text = text.replace("Gambar 2.17", "Gambar 2.18")
        
    # Rule 12: Modal Tambah (Gambar 2.18 -> Gambar 2.19)
    if "tambah data" in text and "Gambar 2.18" in text:
        text = text.replace("Gambar 2.18", "Gambar 2.19")
        
    # Rule 13: Modal Update (Gambar 2.19 -> Gambar 2.20)
    if "edit data" in text and "Gambar 2.19" in text:
        text = text.replace("Gambar 2.19", "Gambar 2.20")
    if "modal update dosen" in text and "Gambar 2.19" in text:
        text = text.replace("Gambar 2.19", "Gambar 2.20")
        
    # Rule 14: Modal Konfirmasi Hapus (Gambar 2.20 -> Gambar 2.21)
    if "hapus data" in text and "Gambar 2.20" in text:
        text = text.replace("Gambar 2.20", "Gambar 2.21")
    if "modal konfirmasi hapus" in text and "Gambar 2.20" in text:
        text = text.replace("Gambar 2.20", "Gambar 2.21")
        
    # Rule 15: Traffic Admin (Gambar 2.21 -> Gambar 2.22)
    if "traffic website" in text and "Gambar 2.21" in text:
        text = text.replace("Gambar 2.21", "Gambar 2.22")
    if "lalu lintas penggunaan" in text and "Gambar 2.21" in text:
        text = text.replace("Gambar 2.21", "Gambar 2.22")
        
    # Rule 16: Hero Section (Gambar 2.22 -> Gambar 2.23)
    if "hero section" in text and "Gambar 2.22" in text:
        text = text.replace("Gambar 2.22", "Gambar 2.23")
    if "titik orientasi utama" in text and "Gambar 2.22" in text:
        text = text.replace("Gambar 2.22", "Gambar 2.23")
        
    # Rule 17: Traffic Public (Gambar 2.23 -> Gambar 2.24)
    if "Public Traffic" in text and "Gambar 2.23" in text:
        text = text.replace("Gambar 2.23", "Gambar 2.24")
    if "aktivitas pengguna pada public dashboard" in text and "Gambar 2.23" in text:
        text = text.replace("Gambar 2.23", "Gambar 2.24")
        
    # Rule 18: Fasilitas dan Aset (Gambar 2.24 -> Gambar 2.25)
    if "fasilitas dan aset" in text and "Gambar 2.24" in text:
        text = text.replace("Gambar 2.24", "Gambar 2.25")
        
    # Rule 19: Modal List Fasilitas (Gambar 2.25 -> Gambar 2.26)
    if "modal yang berisi daftar fasilitas" in text and "Gambar 2.25" in text:
        text = text.replace("Gambar 2.25", "Gambar 2.26")
    if "modal daftar fasilitas kategori" in text and "Gambar 2.25" in text:
        text = text.replace("Gambar 2.25", "Gambar 2.26")
        
    # Rule 20: Modal Detail Fasilitas (Gambar 2.26 -> Gambar 2.27)
    if "kategori unggulan" in text and "Gambar 2.26" in text:
        text = text.replace("Gambar 2.26", "Gambar 2.27")
    if "informasi spesifik" in text and "Gambar 2.26" in text:
        text = text.replace("Gambar 2.26", "Gambar 2.27")
        
    # Rule 21: Bagian Statistik (Gambar 2.27 -> Gambar 2.28)
    if "grafik batang" in text and "Gambar 2.27" in text:
        text = text.replace("Gambar 2.27", "Gambar 2.28")
    if "distribusi sumber daya akademik" in text and "Gambar 2.27" in text:
        text = text.replace("Gambar 2.27", "Gambar 2.28")
        
    # Rule 22: Detail Dosen (Gambar 2.28 -> Gambar 2.29)
    if "detail data dosen" in text and "Gambar 2.28" in text:
        text = text.replace("Gambar 2.28", "Gambar 2.29")
    if "grafik dosen" in text and "Gambar 2.28" in text:
        text = text.replace("Gambar 2.28", "Gambar 2.29")
        
    # Rule 23: Detail Mahasiswa (Gambar 2.29 -> Gambar 2.30)
    if "detail data mahasiswa" in text and "Gambar 2.29" in text:
        text = text.replace("Gambar 2.29", "Gambar 2.30")
    if "grafik mahasiswa" in text and "Gambar 2.29" in text:
        text = text.replace("Gambar 2.29", "Gambar 2.30")
        
    # Rule 24: Bagian Footer (Gambar 2.30 / Gambar 2.22 -> Gambar 2.28)
    if "footer" in text and ("Gambar 2.30" in text or "Gambar 2.22" in text or "Gambar 2.31" in text):
        text = text.replace("Gambar 2.30", "Gambar 2.28").replace("Gambar 2.22", "Gambar 2.28").replace("Gambar 2.31", "Gambar 2.28")
        
    # Rule 25: Unity Prefab (Gambar 3.1 -> Gambar 2.29)
    if "Gambar 3.1" in text:
        text = text.replace("Gambar 3.1", "Gambar 2.29")
        
    # Rule 26: Unity Editor Sync Checker (Gambar 3.2 -> Gambar 2.30)
    if "Gambar 3.2" in text:
        text = text.replace("Gambar 3.2", "Gambar 2.30")
        
    return text

def format_caption_paragraph_clean(p, label, prefix, seq_name, default_val, desc, namespaces):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    
    pPr = p.find('w:pPr', namespaces)
    if pPr is None:
        pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
        p.insert(0, pPr)
        
    set_child_element(pPr, 'pStyle', {'val': 'Caption'})
    set_child_element(pPr, 'spacing', {'before': '120', 'after': '120', 'line': '240', 'lineRule': 'auto'})
    set_child_element(pPr, 'jc', {'val': 'center'})
    set_child_element(pPr, 'ind', {'firstLine': '0', 'left': '0'})
    sort_element_children(pPr, PPR_ORDER)
    
    # Extract bookmarks (resilient to namespaces)
    bookmarks = []
    for elem in list(p):
        if elem.tag.endswith('bookmarkStart'):
            bm_id = elem.get(f'{{{ns_uri}}}id') or elem.get('id')
            bm_name = elem.get(f'{{{ns_uri}}}name') or elem.get('name')
            if bm_id is not None:
                bookmarks.append(('start', bm_id, bm_name or ""))
        elif elem.tag.endswith('bookmarkEnd'):
            bm_id = elem.get(f'{{{ns_uri}}}id') or elem.get('id')
            if bm_id is not None:
                bookmarks.append(('end', bm_id, None))
            
    # Clear all child elements except pPr
    for elem in list(p):
        if elem != pPr:
            p.remove(elem)
            
    # Add bookmarkStarts
    for bm_type, bm_id, bm_name in bookmarks:
        if bm_type == 'start':
            bms = lxml.etree.Element(f'{{{ns_uri}}}bookmarkStart')
            bms.set(f'{{{ns_uri}}}id', str(bm_id))
            bms.set(f'{{{ns_uri}}}name', str(bm_name))
            p.append(bms)
            
    # Label prefix, e.g. "Gambar 2."
    r1 = lxml.etree.Element(f'{{{ns_uri}}}r')
    rPr1 = lxml.etree.Element(f'{{{ns_uri}}}rPr')
    set_child_element(rPr1, 'rFonts', {'ascii': 'Times New Roman', 'hAnsi': 'Times New Roman'})
    set_child_element(rPr1, 'b', {})
    set_child_element(rPr1, 'bCs', {})
    set_child_element(rPr1, 'sz', {'val': '24'})
    set_child_element(rPr1, 'szCs', {'val': '24'})
    r1.append(rPr1)
    
    t1 = lxml.etree.Element(f'{{{ns_uri}}}t')
    t1.text = f"{label} {prefix}"
    if t1.text.startswith(' ') or t1.text.endswith(' '):
        t1.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    r1.append(t1)
    p.append(r1)
    
    # SEQ field
    r2 = lxml.etree.Element(f'{{{ns_uri}}}r')
    fld2 = lxml.etree.Element(f'{{{ns_uri}}}fldChar', **{f'{{{ns_uri}}}fldCharType': "begin"})
    r2.append(fld2)
    p.append(r2)
    
    r3 = lxml.etree.Element(f'{{{ns_uri}}}r')
    ins3 = lxml.etree.Element(f'{{{ns_uri}}}instrText')
    if default_val == 1:
        ins3.text = f" SEQ {seq_name} \\r 1 \\* ARABIC "
    else:
        ins3.text = f" SEQ {seq_name} \\* ARABIC "
    ins3.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    r3.append(ins3)
    p.append(r3)
    
    r4 = lxml.etree.Element(f'{{{ns_uri}}}r')
    fld4 = lxml.etree.Element(f'{{{ns_uri}}}fldChar', **{f'{{{ns_uri}}}fldCharType': "separate"})
    r4.append(fld4)
    p.append(r4)
    
    r5 = lxml.etree.Element(f'{{{ns_uri}}}r')
    t5 = lxml.etree.Element(f'{{{ns_uri}}}t')
    t5.text = str(default_val)
    r5.append(t5)
    p.append(r5)
    
    r6 = lxml.etree.Element(f'{{{ns_uri}}}r')
    fld6 = lxml.etree.Element(f'{{{ns_uri}}}fldChar', **{f'{{{ns_uri}}}fldCharType': "end"})
    r6.append(fld6)
    p.append(r6)
    
    # Description
    r7 = lxml.etree.Element(f'{{{ns_uri}}}r')
    rPr7 = lxml.etree.Element(f'{{{ns_uri}}}rPr')
    set_child_element(rPr7, 'rFonts', {'ascii': 'Times New Roman', 'hAnsi': 'Times New Roman'})
    set_child_element(rPr7, 'sz', {'val': '24'})
    set_child_element(rPr7, 'szCs', {'val': '24'})
    r7.append(rPr7)
    
    t7 = lxml.etree.Element(f'{{{ns_uri}}}t')
    t7.text = f" {desc.strip()}"
    t7.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    r7.append(t7)
    p.append(r7)
    
    # Add bookmarkEnds
    for bm_type, bm_id, _ in bookmarks:
        if bm_type == 'end':
            bme = lxml.etree.Element(f'{{{ns_uri}}}bookmarkEnd')
            bme.set(f'{{{ns_uri}}}id', str(bm_id))
            p.append(bme)

def insert_dynamic_toc_field(body, insertion_idx, field_instruction, namespaces):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    
    p = lxml.etree.Element(f'{{{ns_uri}}}p')
    pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
    set_child_element(pPr, 'pStyle', {'val': 'TableofFigures'})
    tabs = lxml.etree.Element(f'{{{ns_uri}}}tabs')
    set_child_element(tabs, 'tab', {'val': 'right', 'leader': 'dot', 'pos': '7927'})
    pPr.append(tabs)
    
    # Sort pPr
    children_list = list(pPr)
    for c in children_list: pPr.remove(c)
    for tag in PPR_ORDER:
        for c in children_list:
            if c.tag.split('}')[-1] == tag:
                pPr.append(c)
                break
    p.append(pPr)
    
    r_begin = lxml.etree.Element(f'{{{ns_uri}}}r')
    set_child_element(r_begin, 'fldChar', {'fldCharType': 'begin'})
    p.append(r_begin)
    
    r_instr = lxml.etree.Element(f'{{{ns_uri}}}r')
    instr = lxml.etree.Element(f'{{{ns_uri}}}instrText')
    instr.text = field_instruction
    instr.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    r_instr.append(instr)
    p.append(r_instr)
    
    r_sep = lxml.etree.Element(f'{{{ns_uri}}}r')
    set_child_element(r_sep, 'fldChar', {'fldCharType': 'separate'})
    p.append(r_sep)
    
    r_end = lxml.etree.Element(f'{{{ns_uri}}}r')
    set_child_element(r_end, 'fldChar', {'fldCharType': 'end'})
    p.append(r_end)
    
    body.insert(insertion_idx, p)
    return p

def format_document_xmls(unpacked_dir):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    styles_path = os.path.join(unpacked_dir, 'word/styles.xml')
    doc_path = os.path.join(unpacked_dir, 'word/document.xml')
    rel_map = load_rels_map(unpacked_dir)
    
    # 1. Modify Styles
    if os.path.exists(styles_path):
        parser = lxml.etree.XMLParser(remove_blank_text=False)
        tree = lxml.etree.parse(styles_path, parser)
        root = tree.getroot()
        ensure_front_matter_heading_style(root)
        ensure_appendix_heading_style(root)
        ensure_toc9_style(root)
        # ensure_hyperlink_style(root)
        for style in root.findall('w:style', namespaces):
            style_id = style.get(f'{{{ns_uri}}}styleId')
            style_type = style.get(f'{{{ns_uri}}}type')
            if style_type == 'paragraph':
                pPr = style.find('w:pPr', namespaces)
                if pPr is None:
                    pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                    style.append(pPr)
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
                elif style_id in ['TOC1', 'TOC2', 'TOC3', 'TableofFigures']:
                    set_child_element(pPr, 'spacing', {'before': '0', 'after': '0', 'line': '360', 'lineRule': 'auto'})
                    tabs = set_child_element(pPr, 'tabs')
                    for child in list(tabs):
                        tabs.remove(child)
                    set_child_element(tabs, 'tab', {'val': 'right', 'leader': 'dot', 'pos': '7927'})
                elif style_id.startswith('Heading'):
                    if style_id in ['Heading1', 'Heading2']:
                        set_child_element(pPr, 'spacing', {'before': '240', 'after': '120', 'line': '360', 'lineRule': 'auto'})
                    else:
                        set_child_element(pPr, 'spacing', {'before': '120', 'after': '60', 'line': '360', 'lineRule': 'auto'})
                    set_child_element(pPr, 'ind', {'firstLine': '0', 'left': '0'})
                    if style_id == 'Heading1':
                        set_child_element(pPr, 'jc', {'val': 'center'})
                        set_child_element(pPr, 'pageBreakBefore', {})
                    else:
                        set_child_element(pPr, 'jc', {'val': 'left'})
                sort_element_children(pPr, PPR_ORDER)
            sort_element_children(style, STYLE_ORDER)
        tree.write(styles_path, encoding='utf-8', xml_declaration=True)
        print("Updated styles.xml.")
        
    # 2. Modify Document
    if os.path.exists(doc_path):
        parser = lxml.etree.XMLParser(remove_blank_text=False)
        tree = lxml.etree.parse(doc_path, parser)
        root = tree.getroot()
        body = root.find('w:body', namespaces)
        if body is None: return
        
        # Reorder table and figure captions
        children = list(body)
        
        # 1. Move table captions above tables
        i = 0
        while i < len(children):
            child = children[i]
            if child.tag.endswith('tbl'):
                if i + 1 < len(children) and children[i+1].tag.endswith('p'):
                    p_after = children[i+1]
                    txt_after = "".join([t.text for t in p_after.iter(f'{{{ns_uri}}}t') if t.text]).strip()
                    if txt_after.startswith('Tabel'):
                        body.remove(p_after)
                        body.insert(i, p_after)
                        children = list(body)
                        print(f"  Moved table caption '{txt_after}' above the table.")
            i += 1
            
        # 2. Move figure captions below figures (Disabled: causing reordering issues; all figures are already placed correctly above captions)
        # i = 0
        # while i < len(children):
        #     child = children[i]
        #     if child.tag.endswith('p'):
        #         if child.find('.//w:drawing', namespaces) is not None:
        #             if i - 1 >= 0 and children[i-1].tag.endswith('p'):
        #                 p_before = children[i-1]
        #                 txt_before = "".join([t.text for t in p_before.iter(f'{{{ns_uri}}}t') if t.text]).strip()
        #                 if txt_before.startswith('Gambar'):
        #                     body.remove(p_before)
        #                     body.insert(i, p_before)
        #                     children = list(body)
        #                     print(f"  Moved figure caption '{txt_before}' below the figure.")
        #     i += 1

            
        # Remove manual page breaks that are immediately before Heading 1 (to prevent double page breaks)
        children = list(body)
        i = 0
        while i < len(children):
            p = children[i]
            if p.tag.endswith('p'):
                has_page_break = False
                br_elems = []
                for elem in p.iter():
                    tag_local = elem.tag.split('}')[-1]
                    if tag_local == 'br' and elem.get(f'{{{ns_uri}}}type') == 'page':
                        has_page_break = True
                        br_elems.append(elem)
                        
                if has_page_break:
                    is_before_heading1 = False
                    for j in range(i + 1, len(children)):
                        next_child = children[j]
                        next_p = next_child
                        if next_child.tag.endswith('sdt'):
                            sdtContent = next_child.find('w:sdtContent', namespaces)
                            if sdtContent is not None:
                                next_p = sdtContent.find('w:p', namespaces)
                        
                        if next_p is None or not next_p.tag.endswith('p'):
                            break
                        next_text = "".join(next_p.itertext()).strip()
                        next_pPr = next_p.find('w:pPr', namespaces)
                        next_pStyle = next_pPr.find('w:pStyle', namespaces) if next_pPr is not None else None
                        next_pStyle_val = next_pStyle.get(f'{{{ns_uri}}}val') if next_pStyle is not None else ""
                        
                        if next_pStyle_val == 'Heading1':
                            is_before_heading1 = True
                            break
                        if next_text:
                            break
                            
                    if is_before_heading1:
                        print(f"  Removing manual page break before Heading 1 at index {i}")
                        for br in br_elems:
                            parent = br.getparent()
                            if parent is not None:
                                parent.remove(br)
                                if len(parent) == 0 and not parent.text:
                                    gp = parent.getparent()
                                    if gp is not None: gp.remove(parent)
                        p_text = "".join(p.itertext()).strip()
                        runs = p.findall('.//w:r', namespaces)
                        if not p_text and len(runs) == 0:
                            body.remove(p)
                            children = list(body)
                            continue
            i += 1
            
        # 3. Update existing figure references and captions to their new numbers (to avoid double-matching new captions)
        def ref_repl(match):
            val = match.group(1)
            if val == 'x':
                return 'Gambar 2.15'
            try:
                num = int(val)
                if 1 <= num <= 7:
                    return f'Gambar 2.{num + 7}'
                elif 8 <= num <= 22:
                    return f'Gambar 2.{num + 8}'
            except ValueError:
                pass
            return match.group(0)
            
        for t_elem in root.iter(f'{{{ns_uri}}}t'):
            if t_elem.text:
                new_text = re.sub(r'Gambar\s+2\.([0-9]+|x)\b', ref_repl, t_elem.text)
                if new_text != t_elem.text:
                    t_elem.text = new_text
                    
        # 4. Generate new captions for uncaptioned drawings and reconstruct body
        reconstructed_children = []
        fig_counter = 0
        survey_captions = [
            "Hasil Kuesioner: Profil Status Akademik Responden",
            "Hasil Kuesioner: Efektivitas Media Navigasi Kampus Saat Ini",
            "Hasil Kuesioner: Frekuensi Kesulitan Menemukan Lokasi",
            "Hasil Kuesioner: Perilaku Pengguna Saat Mencari Lokasi",
            "Hasil Kuesioner: Urgensi Kebutuhan Peta Virtual 3D",
            "Hasil Kuesioner: Potensi Adopsi Denah Virtual 3D",
            "Hasil Kuesioner: Prioritas Informasi Fasilitas Kampus"
        ]
        survey_idx = 0
        current_section_title = ""
        
        bab1_idx_orig = -1
        for idx, child in enumerate(children):
            if child.tag.endswith('p'):
                pPr = child.find('w:pPr', namespaces)
                pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                pStyle_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                text = "".join([t.text for t in child.iter(f'{{{ns_uri}}}t') if t.text])
                if pStyle_val == 'Heading1' and 'PENDAHULUAN' in text.upper():
                    bab1_idx_orig = idx
                    break
        if bab1_idx_orig == -1:
            bab1_idx_orig = 60
            
        def create_caption_paragraph_local(label, prefix, seq_name, default_val, desc, bookmark_id, bookmark_name):
            p = lxml.etree.Element(f'{{{ns_uri}}}p')
            pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
            set_child_element(pPr, 'pStyle', {'val': 'Caption'})
            set_child_element(pPr, 'spacing', {'before': '120', 'after': '120', 'line': '240', 'lineRule': 'auto'})
            set_child_element(pPr, 'jc', {'val': 'center'})
            set_child_element(pPr, 'ind', {'firstLine': '0', 'left': '0'})
            sort_element_children(pPr, PPR_ORDER)
            p.append(pPr)
            
            bms = lxml.etree.Element(f'{{{ns_uri}}}bookmarkStart', id=str(bookmark_id), name=bookmark_name)
            p.append(bms)

            # Label and prefix, e.g. "Gambar 2."
            r1 = lxml.etree.Element(f'{{{ns_uri}}}r')
            t1 = lxml.etree.Element(f'{{{ns_uri}}}t')
            t1.text = f"{label} {prefix}"
            if t1.text.startswith(' ') or t1.text.endswith(' '):
                t1.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            r1.append(t1)
            p.append(r1)
            
            # fldChar begin
            r2 = lxml.etree.Element(f'{{{ns_uri}}}r')
            fld2 = lxml.etree.Element(f'{{{ns_uri}}}fldChar', **{f'{{{ns_uri}}}fldCharType': "begin"})
            r2.append(fld2)
            p.append(r2)
            
            # instrText
            r3 = lxml.etree.Element(f'{{{ns_uri}}}r')
            ins3 = lxml.etree.Element(f'{{{ns_uri}}}instrText')
            if default_val == 1:
                ins3.text = f" SEQ {seq_name} \\r 1 \\* ARABIC "
            else:
                ins3.text = f" SEQ {seq_name} \\* ARABIC "
            ins3.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            r3.append(ins3)
            p.append(r3)
            
            # fldChar separate
            r4 = lxml.etree.Element(f'{{{ns_uri}}}r')
            fld4 = lxml.etree.Element(f'{{{ns_uri}}}fldChar', **{f'{{{ns_uri}}}fldCharType': "separate"})
            r4.append(fld4)
            p.append(r4)
            
            # default value run
            r5 = lxml.etree.Element(f'{{{ns_uri}}}r')
            t5 = lxml.etree.Element(f'{{{ns_uri}}}t')
            t5.text = str(default_val)
            r5.append(t5)
            p.append(r5)
            
            # fldChar end
            r6 = lxml.etree.Element(f'{{{ns_uri}}}r')
            fld6 = lxml.etree.Element(f'{{{ns_uri}}}fldChar', **{f'{{{ns_uri}}}fldCharType': "end"})
            r6.append(fld6)
            p.append(r6)
            
            # description run
            r7 = lxml.etree.Element(f'{{{ns_uri}}}r')
            t7 = lxml.etree.Element(f'{{{ns_uri}}}t')
            t7.text = f" {desc}"
            t7.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            r7.append(t7)
            p.append(r7)
            
            bme = lxml.etree.Element(f'{{{ns_uri}}}bookmarkEnd', id=str(bookmark_id))
            p.append(bme)
            
            return p

        # Find cover page end index (last paragraph before the SECOND drawing, which is Lembar Pengesahan)
        collected_captions = []
        estimated_page = 1
        para_count = 0
        cover_end_idx = 0
        drawing_count = 0
        for idx, child in enumerate(children):
            if idx < bab1_idx_orig and child.tag.endswith('p'):
                if child.find('.//w:drawing', namespaces) is not None:
                    drawing_count += 1
                    if drawing_count == 2:
                        break
                cover_end_idx = idx

        lembar_pengesahan_processed = False
        for idx, child in enumerate(children):
            para_count += 1
            if para_count > 25:
                estimated_page += 1
                para_count = 0
                
            if idx < bab1_idx_orig:
                if idx <= cover_end_idx:
                    if child.tag.endswith('p'):
                        scale_cover_drawings(child, namespaces, unpacked_dir, rel_map)
                        text = "".join(child.itertext()).strip()
                        if not text:
                            pPr = child.find('w:pPr', namespaces)
                            if pPr is None:
                                pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                                child.insert(0, pPr)
                            set_child_element(pPr, 'spacing', {'before': '0', 'after': '0', 'line': '240', 'lineRule': 'auto'})
                            sort_element_children(pPr, PPR_ORDER)
                    reconstructed_children.append(child)
                else:
                    # Transition zone: skip empty paragraphs to prevent blank pages
                    if child.tag.endswith('p'):
                        text = "".join(child.itertext()).strip()
                        has_drawing = child.find('.//w:drawing', namespaces) is not None
                        has_sectPr = child.find('.//w:sectPr', namespaces) is not None
                        has_fldChar = child.find('.//w:fldChar', namespaces) is not None
                        has_instr = child.find('.//w:instrText', namespaces) is not None
                        if text or has_drawing or has_sectPr or has_fldChar or has_instr:
                            if has_drawing and not lembar_pengesahan_processed:
                                pPr = child.find('w:pPr', namespaces)
                                if pPr is None:
                                    pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                                    child.insert(0, pPr)
                                set_child_element(pPr, 'pageBreakBefore', {})
                                set_child_element(pPr, 'jc', {'val': 'center'})
                                sort_element_children(pPr, PPR_ORDER)
                                lembar_pengesahan_processed = True
                                print(f"  Applied page break and centering to Lembar Pengesahan at index {idx}")
                            reconstructed_children.append(child)
                        else:
                            print(f"  Removing redundant empty paragraph in front-matter transition at index {idx}")
                    else:
                        reconstructed_children.append(child)
                continue
                
            if child.tag.endswith('p'):
                pPr = child.find('w:pPr', namespaces)
                pStyle_val = ""
                if pPr is not None:
                    pStyle = pPr.find('w:pStyle', namespaces)
                    if pStyle is not None:
                        pStyle_val = pStyle.get(f'{{{ns_uri}}}val')
                
                if pStyle_val and pStyle_val.startswith('Heading'):
                    current_section_title = "".join(child.itertext()).strip()
                    
                has_drawing = child.find('.//w:drawing', namespaces) is not None
                
                if has_drawing:
                    already_captioned = False
                    if idx + 1 < len(children):
                        next_child = children[idx + 1]
                        if next_child.tag.endswith('p'):
                            next_pPr = next_child.find('w:pPr', namespaces)
                            next_pStyle = next_pPr.find('w:pStyle', namespaces) if next_pPr is not None else None
                            next_pStyle_val = next_pStyle.get(f'{{{ns_uri}}}val') if next_pStyle is not None else ""
                            next_text = "".join(next_child.itertext()).strip()
                            if next_pStyle_val == 'Caption' or re.match(r'^Gambar\s+2\b', next_text, re.IGNORECASE):
                                already_captioned = True
                                
                    if "Analisis Sistem yang Sedang Berjalan" in current_section_title and survey_idx < 7:
                        reconstructed_children.append(child)
                        if not already_captioned:
                            bmid = 9000 + len(collected_captions) + survey_idx
                            bmname = f"_TocGemini{bmid}"
                            caption_p = create_caption_paragraph_local("Gambar", "2.", "Gambar_2.", survey_idx + 1, survey_captions[survey_idx], bmid, bmname)
                            reconstructed_children.append(caption_p)
                            print(f"  Generated survey caption Gambar 2.{survey_idx + 1}")
                        else:
                            print(f"  Survey caption for Gambar 2.{survey_idx + 1} already exists, skipping generation.")
                        survey_idx += 1
                    elif "Integrasi Backend dengan Unity" in current_section_title:
                        reconstructed_children.append(child)
                        if not already_captioned:
                            bmid = 9000 + 100
                            bmname = f"_TocGemini{bmid}"
                            caption_p = create_caption_paragraph_local("Gambar", "2.", "Gambar_2.", 15, "Arsitektur Integrasi Sistem", bmid, bmname)
                            reconstructed_children.append(caption_p)
                            print("  Generated integration caption Gambar 2.15")
                        else:
                            print("  Integration caption Gambar 2.15 already exists, skipping generation.")
                    else:
                        reconstructed_children.append(child)
                else:
                    reconstructed_children.append(child)
            else:
                reconstructed_children.append(child)
                
        for child in list(body):
            body.remove(child)
        for child in reconstructed_children:
            body.append(child)
            
        # 3. Create DAFTAR LAMPIRAN section (run before boundaries are checked so it's in Section 1)
        daftar_tabel_idx = -1
        children_temp = list(body)
        for idx, child in enumerate(children_temp):
            if child.tag.endswith('p'):
                text = "".join(child.itertext()).strip()
                pPr = child.find('w:pPr', namespaces)
                pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                style_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                if text == "DAFTAR TABEL" and style_val == "Heading1":
                    daftar_tabel_idx = idx
                    break
                    
        insertion_idx = -1
        for idx in range(daftar_tabel_idx + 1, len(children_temp)):
            child = children_temp[idx]
            if child.tag.endswith('p'):
                pPr = child.find('w:pPr', namespaces)
                pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                style_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                if style_val == "Heading1":
                    text = "".join(child.itertext()).strip()
                    if "DAFTAR LAMPIRAN" in text.upper():
                        insertion_idx = -1
                        break
                    if "PENDAHULUAN" in text.upper() or "BAB I" in text.upper():
                        insertion_idx = idx
                        break
                        
        if insertion_idx != -1:
            print(f"Inserting DAFTAR LAMPIRAN at index {insertion_idx}...")
            p_head = lxml.etree.Element(f'{{{ns_uri}}}p')
            pPr_head = lxml.etree.Element(f'{{{ns_uri}}}pPr')
            set_child_element(pPr_head, 'pStyle', {'val': 'Heading1'})
            set_child_element(pPr_head, 'pageBreakBefore', {})
            set_child_element(pPr_head, 'jc', {'val': 'center'})
            sort_element_children(pPr_head, PPR_ORDER)
            p_head.append(pPr_head)
            
            r_head = lxml.etree.Element(f'{{{ns_uri}}}r')
            rPr_head = lxml.etree.Element(f'{{{ns_uri}}}rPr')
            set_child_element(rPr_head, 'rFonts', {'ascii': 'Times New Roman', 'hAnsi': 'Times New Roman'})
            set_child_element(rPr_head, 'b', {})
            set_child_element(rPr_head, 'bCs', {})
            set_child_element(rPr_head, 'sz', {'val': '28'})
            set_child_element(rPr_head, 'szCs', {'val': '28'})
            r_head.append(rPr_head)
            t_head = lxml.etree.Element(f'{{{ns_uri}}}t')
            t_head.text = "DAFTAR LAMPIRAN"
            r_head.append(t_head)
            p_head.append(r_head)
            
            body.insert(insertion_idx, p_head)
            insert_dynamic_toc_field(body, insertion_idx + 1, ' TOC \\o "9-9" \\n 9-9 \\h \\z ', namespaces)
            print("Successfully inserted DAFTAR LAMPIRAN heading and TOF field.")
            
        children = list(body)
        parent_map = {c: p for p in root.iter() for c in p}
        
        def is_inside_table(elem):
            curr = elem
            while curr in parent_map:
                parent = parent_map[curr]
                if parent.tag.endswith('tc'): return True
                curr = parent
            return False
            
        # Find boundaries
        bab1_idx = -1
        for idx, child in enumerate(children):
            if child.tag.endswith('p'):
                pPr = child.find('w:pPr', namespaces)
                pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                pStyle_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                text = "".join([t.text for t in child.iter(f'{{{ns_uri}}}t') if t.text])
                if pStyle_val == 'Heading1' and 'PENDAHULUAN' in text.upper():
                    bab1_idx = idx
                    break
        section1_last_p_idx = bab1_idx - 1 if bab1_idx != -1 else 60
        
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
                        
        gambar_idx = 1
        for idx, child in enumerate(children):
            if child.tag.endswith('tbl'): continue
            if child.tag.endswith('sdt'):
                if daftar_pustaka_heading_idx != -1 and idx > daftar_pustaka_heading_idx:
                    clean_bibliography_sdt(child)
                # Formats DAFTAR ISI paragraph inside the TOC sdt
                sdtContent = child.find('w:sdtContent', namespaces)
                if sdtContent is not None:
                    sdtPr = child.find('w:sdtPr', namespaces)
                    tag_elem = sdtPr.find('w:tag', namespaces) if sdtPr is not None else None
                    tag_val = tag_elem.get(f'{{{ns_uri}}}val') if tag_elem is not None else ""
                    if tag_val != 'MENDELEY_BIBLIOGRAPHY':
                        toc_p = sdtContent.find('w:p', namespaces)
                        if toc_p is not None:
                            toc_text = "".join(toc_p.itertext()).strip()
                            if 'DAFTAR ISI' in toc_text.upper():
                                toc_pPr = toc_p.find('w:pPr', namespaces)
                                if toc_pPr is None:
                                    toc_pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                                    toc_p.insert(0, toc_pPr)
                                set_child_element(toc_pPr, 'pStyle', {'val': 'Heading1'})
                                set_child_element(toc_pPr, 'pageBreakBefore', {})
                                sort_element_children(toc_pPr, PPR_ORDER)
                continue
                
            if child.tag.endswith('p'):
                p = child
                if is_inside_table(p): continue
                pPr = p.find('w:pPr', namespaces)
                pStyle_val = "Normal"
                if pPr is not None:
                    pStyle = pPr.find('w:pStyle', namespaces)
                    if pStyle is not None: pStyle_val = pStyle.get(f'{{{ns_uri}}}val')
                    
                is_section2 = (idx > section1_last_p_idx)
                
                # Correct in-text citations
                text = "".join([t.text for t in p.iter(f'{{{ns_uri}}}t') if t.text])
                if 'Aliyah Aliyah' in text:
                    cleaned_text = text.replace('Aliyah Aliyah et al., 2024', 'Aliyah et al., 2024')
                    for r in p.findall(f'{{{ns_uri}}}r', namespaces): p.remove(r)
                    new_r = lxml.etree.Element(f'{{{ns_uri}}}r')
                    new_t = lxml.etree.Element(f'{{{ns_uri}}}t')
                    new_t.text = cleaned_text
                    new_r.append(new_t)
                    p.append(new_r)
                    text = cleaned_text
                    
                # Auto-detect captions and format them (only in body Section 2)
                if is_section2:
                    text_clean = text.strip()
                    is_gambar_caption = (pStyle_val == 'Caption' and text_clean.lower().startswith('gambar')) or re.match(r'^Gambar\s+[0-9]+', text_clean, re.IGNORECASE)
                    is_tabel_caption = (pStyle_val == 'Caption' and text_clean.lower().startswith('tabel')) or re.match(r'^Tabel\s+[0-9]+', text_clean, re.IGNORECASE)
                    
                    if is_gambar_caption:
                        m = re.match(r'^Gambar\s+[0-9]+(?:\.[0-9]+)*\.?\s*(.*)$', text_clean, re.IGNORECASE)
                        desc = m.group(1) if m else text_clean
                        format_caption_paragraph_clean(p, "Gambar", "2.", "Gambar", gambar_idx, desc, namespaces)
                        
                        new_caption_text = f"Gambar 2.{gambar_idx} {desc}"
                        collected_captions.append({
                            "type": "Gambar",
                            "text": new_caption_text,
                            "page": estimated_page
                        })
                        text = new_caption_text
                        gambar_idx += 1
                        
                    elif is_tabel_caption:
                        m = re.match(r'^Tabel\s+([0-9]+(?:\.[0-9]+)*)\.?\s*(.*)$', text_clean, re.IGNORECASE)
                        if m:
                            num_part = m.group(1)
                            desc = m.group(2)
                            parts = num_part.split('.')
                            if len(parts) >= 2:
                                chap_num = parts[0]
                                seq_val = int(parts[1])
                            else:
                                chap_num = "2"
                                seq_val = int(parts[0])
                            
                            format_caption_paragraph_clean(p, "Tabel", f"{chap_num}.", "Tabel", seq_val, desc, namespaces)
                            cleaned_caption = f"Tabel {chap_num}.{seq_val} {desc}"
                            text = cleaned_caption
                            
                        collected_captions.append({
                            "type": "Tabel",
                            "text": text,
                            "page": estimated_page
                        })
                        
                    elif "Gambar 2." in text or "Gambar 3." in text:
                        new_text = replace_mentions_in_paragraph(text)
                        if new_text != text:
                            t_elems = p.findall('.//w:t', namespaces)
                            if t_elems:
                                t_elems[0].text = new_text
                                t_elems[0].set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                                for t in t_elems[1:]:
                                    t.text = ""
                            text = new_text
                    
                # Format Headings
                if pStyle_val == 'Heading1':
                    text = "".join([t.text for t in p.iter(f'{{{ns_uri}}}t') if t.text]).strip()
                    if text.upper().startswith('LAMPIRAN'):
                        pStyle.set(f'{{{ns_uri}}}val', 'taappendixheading')
                        pStyle_val = 'taappendixheading'
                        
                if pStyle_val.startswith('Heading') or pStyle_val == 'taappendixheading':
                    text = "".join([t.text for t in p.iter(f'{{{ns_uri}}}t') if t.text]).strip()
                    if not text:
                        if pPr is not None:
                            set_child_element(pPr, 'pStyle', {'val': 'Normal'})
                            numPr = pPr.find(f'{{{ns_uri}}}numPr', namespaces)
                            if numPr is not None: pPr.remove(numPr)
                        continue
                    if pStyle_val == 'taappendixheading':
                        if pPr is None:
                            pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                            p.insert(0, pPr)
                        set_child_element(pPr, 'pStyle', {'val': 'taappendixheading'})
                        set_child_element(pPr, 'pageBreakBefore', {})
                        numPr = pPr.find(f'{{{ns_uri}}}numPr', namespaces)
                        if numPr is not None:
                            pPr.remove(numPr)
                    elif pStyle_val == 'Heading1':
                        if pPr is None:
                            pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                            p.insert(0, pPr)
                        set_child_element(pPr, 'pageBreakBefore', {})
                        if 'DAFTAR' in text.upper() or 'KATA PENGANTAR' in text.upper() or 'ABSTRAK' in text.upper():
                            set_child_element(pPr, 'pStyle', {'val': 'Heading1'})
                            numPr = pPr.find(f'{{{ns_uri}}}numPr', namespaces)
                            if numPr is not None: pPr.remove(numPr)
                        else:
                            clean_heading_text_and_add_num(p, 0, 76)
                    elif pStyle_val == 'Heading2': clean_heading_text_and_add_num(p, 1, 76)
                    elif pStyle_val == 'Heading3': clean_heading_text_and_add_num(p, 2, 76)
                    elif pStyle_val == 'Heading4': clean_heading_text_and_add_num(p, 3, 76)
                    elif pStyle_val == 'Heading5': clean_heading_text_and_add_num(p, 4, 76)
                else:
                    # Body text
                    if is_section2:
                        if pStyle_val == 'Normal':
                            if pPr is None:
                                pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                                p.insert(0, pPr)
                            left_indent = '0'
                            ind_elem = pPr.find('w:ind', namespaces)
                            if ind_elem is not None:
                                left_indent = ind_elem.get(f'{{{ns_uri}}}left', '0')
                            try: left_val = int(left_indent)
                            except: left_val = 0
                            
                            if left_val > 0: set_child_element(pPr, 'ind', {'firstLine': '0'})
                            else: set_child_element(pPr, 'ind', {'firstLine': '567', 'left': '0'})
                            
                            jc_elem = pPr.find('w:jc', namespaces)
                            jc_val = jc_elem.get(f'{{{ns_uri}}}val', 'both') if jc_elem is not None else 'both'
                            if jc_val not in ['center', 'right']: set_child_element(pPr, 'jc', {'val': 'both'})
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
                        if pStyle_val == 'Normal':
                            if pPr is None:
                                pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                                p.insert(0, pPr)
                            set_child_element(pPr, 'ind', {'firstLine': '0'})
                
                # Center and scale drawings if present in paragraph
                if p.find('.//w:drawing', namespaces) is not None:
                    center_and_scale_drawings(p, namespaces, unpacked_dir, rel_map)
                    pPr = p.find('w:pPr', namespaces)
                
                if pPr is not None: sort_element_children(pPr, PPR_ORDER)
                
            # Layout Break Section 1
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
                    
        # Final section break (body section)
        final_sectPr = body.find('w:sectPr', namespaces)
        if final_sectPr is not None:
            pg_num_type = set_child_element(final_sectPr, 'pgNumType', {'fmt': 'decimal'})
            start_attr = f'{{{ns_uri}}}start'
            if start_attr in pg_num_type.attrib:
                del pg_num_type.attrib[start_attr]
            set_child_element(final_sectPr, 'pgSz', {'w': '11906', 'h': '16838'})
            set_child_element(final_sectPr, 'pgMar', {
                'top': '1701', 'right': '1701', 'bottom': '1701', 'left': '2268',
                'header': '720', 'footer': '720', 'gutter': '0'
            })
            sort_element_children(final_sectPr, SECTPR_ORDER)
            
        # Strip all dirty flags from fldChar elements to prevent Word 
        # from showing "update fields" dialog on open.
        for fldChar in body.iter(f'{{{ns_uri}}}fldChar'):
            if fldChar.get(f'{{{ns_uri}}}dirty'):
                del fldChar.attrib[f'{{{ns_uri}}}dirty']

        # Split and format nested TOC fields to remove the gap/jeda between Tabel 1.1 and Tabel 2.1
        idx_t = 0
        while idx_t < len(body):
            child = body[idx_t]
            if child.tag.endswith('p'):
                instrs = child.findall('.//w:instrText', namespaces)
                has_t1 = any('Tabel 1.' in instr.text for instr in instrs)
                has_t2 = any('Tabel 2.' in instr.text for instr in instrs)
                if has_t1 and has_t2:
                    children_elems = list(child)
                    p1_elems = []
                    p2_elems = []
                    found_second_begin = False
                    
                    for elem in children_elems:
                        if elem.tag.endswith('pPr'):
                            continue
                        
                        is_second_begin = False
                        if elem.tag.endswith('r'):
                            fldChar = elem.find('w:fldChar', namespaces)
                            if fldChar is not None and fldChar.get(f'{{{ns_uri}}}fldCharType') == 'begin':
                                if len(p1_elems) > 0:
                                    is_second_begin = True
                                    
                        if is_second_begin:
                            found_second_begin = True
                            
                        if not found_second_begin:
                            p1_elems.append(elem)
                        else:
                            p2_elems.append(elem)
                            
                    if found_second_begin and len(p2_elems) > 0:
                        for elem in list(child):
                            if not elem.tag.endswith('pPr'):
                                child.remove(elem)
                        for elem in p1_elems:
                            child.append(elem)
                            
                        # Build P2 (1pt spacing and font size)
                        p2 = lxml.etree.Element(f'{{{ns_uri}}}p')
                        pPr2 = lxml.etree.Element(f'{{{ns_uri}}}pPr')
                        set_child_element(pPr2, 'pStyle', {'val': 'TableofFigures'})
                        set_child_element(pPr2, 'spacing', {'before': '0', 'after': '0', 'line': '20', 'lineRule': 'auto'})
                        
                        rPr2 = lxml.etree.Element(f'{{{ns_uri}}}rPr')
                        set_child_element(rPr2, 'sz', {'val': '2'})
                        set_child_element(rPr2, 'szCs', {'val': '2'})
                        pPr2.append(rPr2)
                        p2.append(pPr2)
                        
                        for elem in p2_elems:
                            if elem.tag.endswith('r'):
                                run_rPr = elem.find('w:rPr', namespaces)
                                if run_rPr is None:
                                    run_rPr = lxml.etree.Element(f'{{{ns_uri}}}rPr')
                                    elem.insert(0, run_rPr)
                                set_child_element(run_rPr, 'sz', {'val': '2'})
                                set_child_element(run_rPr, 'szCs', {'val': '2'})
                            p2.append(elem)
                            
                        body.insert(idx_t + 1, p2)
                        print("  Split nested Table of Figures fields (Tabel 1. and Tabel 2.) and formatted second field as 1pt.")
            idx_t += 1

        # Clean static lists and replace with dynamic fields
        children = list(body)
        daftar_gambar_idx = -1
        daftar_tabel_idx = -1
        
        for idx, child in enumerate(children):
            if child.tag.endswith('p'):
                text = "".join(child.itertext()).strip()
                pPr = child.find('w:pPr', namespaces)
                pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                style_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                if text == "DAFTAR GAMBAR" and style_val == "Heading1":
                    daftar_gambar_idx = idx
                elif text == "DAFTAR TABEL" and style_val == "Heading1":
                    daftar_tabel_idx = idx
                    
        # 1. Clean and insert dynamic Table of Figures
        if daftar_gambar_idx != -1 and daftar_tabel_idx != -1:
            print(f"Cleaning static DAFTAR GAMBAR list between {daftar_gambar_idx} and {daftar_tabel_idx}...")
            to_delete = []
            for idx in range(daftar_gambar_idx + 1, daftar_tabel_idx):
                child = children[idx]
                if child.tag.endswith('p'):
                    pPr = child.find('w:pPr', namespaces)
                    pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                    style_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                    text = "".join(child.itertext()).strip()
                    if style_val == 'TableofFigures' or not text:
                        to_delete.append(child)
            for child in to_delete:
                body.remove(child)
            print(f"Removed {len(to_delete)} elements from DAFTAR GAMBAR.")
            
            children = list(body)
            for idx, child in enumerate(children):
                if child.tag.endswith('p'):
                    text = "".join(child.itertext()).strip()
                    pPr = child.find('w:pPr', namespaces)
                    pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                    style_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                    if text == "DAFTAR GAMBAR" and style_val == "Heading1":
                        daftar_gambar_idx = idx
                        break
            for idx, child in enumerate(children):
                if child.tag.endswith('p'):
                    text = "".join(child.itertext()).strip()
                    pPr = child.find('w:pPr', namespaces)
                    pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                    style_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                    if text == "DAFTAR TABEL" and style_val == "Heading1":
                        daftar_tabel_idx = idx
                        break
                        
            insert_dynamic_toc_field(body, daftar_gambar_idx + 1, ' TOC \\h \\z \\c "Gambar" ', namespaces)
            
        # 2. Clean and insert Table of Tables
        children = list(body)
        for idx, child in enumerate(children):
            if child.tag.endswith('p'):
                text = "".join(child.itertext()).strip()
                pPr = child.find('w:pPr', namespaces)
                pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                style_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                if text == "DAFTAR TABEL" and style_val == "Heading1":
                    daftar_tabel_idx = idx
                    break
                    
        insertion_idx = -1
        if daftar_tabel_idx != -1:
            for idx in range(daftar_tabel_idx + 1, len(children)):
                child = children[idx]
                if child.tag.endswith('p'):
                    pPr = child.find('w:pPr', namespaces)
                    pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                    style_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                    if style_val == "Heading1":
                        insertion_idx = idx
                        break
                        
        if daftar_tabel_idx != -1 and insertion_idx != -1:
            print(f"Cleaning static DAFTAR TABEL list between {daftar_tabel_idx} and {insertion_idx}...")
            to_delete = []
            for idx in range(daftar_tabel_idx + 1, insertion_idx):
                child = children[idx]
                if child.tag.endswith('p'):
                    pPr = child.find('w:pPr', namespaces)
                    pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                    style_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                    text = "".join(child.itertext()).strip()
                    if style_val == 'TableofFigures' or not text:
                        to_delete.append(child)
            for child in to_delete:
                body.remove(child)
            print(f"Removed {len(to_delete)} elements from DAFTAR TABEL.")
            
            children = list(body)
            for idx, child in enumerate(children):
                if child.tag.endswith('p'):
                    text = "".join(child.itertext()).strip()
                    pPr = child.find('w:pPr', namespaces)
                    pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                    style_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                    if text == "DAFTAR TABEL" and style_val == "Heading1":
                        daftar_tabel_idx = idx
                        break
            for idx in range(daftar_tabel_idx + 1, len(children)):
                child = children[idx]
                if child.tag.endswith('p'):
                    pPr = child.find('w:pPr', namespaces)
                    pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                    style_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
                    if style_val == "Heading1":
                        insertion_idx = idx
                        break
                        
            insert_dynamic_toc_field(body, daftar_tabel_idx + 1, ' TOC \\h \\z \\c "Tabel" ', namespaces)
            


        fix_whitespace_preservation(root)
        tree.write(doc_path, encoding='utf-8', xml_declaration=True)
        print("Updated document.xml.")

def fix_all_fonts_lxml(directory):
    W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'
    parser = lxml.etree.XMLParser(remove_blank_text=False)
    
    print(f"Normalizing fonts in {directory} recursively...")
    for root_dir, dirs, files in os.walk(directory):
        for file in files:
            if not (file.endswith('.xml') or file.endswith('.rels')): continue
            filepath = os.path.join(root_dir, file)
            try:
                tree = lxml.etree.parse(filepath, parser)
                root = tree.getroot()
            except:
                continue
                
            modified = False
            for elem in root.iter():
                tag_local = elem.tag.split('}')[-1]
                if tag_local == 'rFonts':
                    for attr in ['ascii', 'hAnsi', 'eastAsia', 'cs']:
                        full_attr = f'{{{W_NS}}}{attr}'
                        val = elem.get(full_attr)
                        if val and val not in ['Symbol', 'Wingdings', 'Courier New', 'Times New Roman']:
                            elem.set(full_attr, 'Times New Roman')
                            modified = True
                    theme_attrs = ['asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme']
                    has_theme = False
                    for attr in theme_attrs:
                        full_attr = f'{{{W_NS}}}{attr}'
                        if elem.get(full_attr) is not None:
                            elem.attrib.pop(full_attr)
                            has_theme = True
                            modified = True
                    if has_theme:
                        for attr in ['ascii', 'hAnsi', 'eastAsia', 'cs']:
                            full_attr = f'{{{W_NS}}}{attr}'
                            val = elem.get(full_attr)
                            if not val or val not in ['Symbol', 'Wingdings', 'Courier New']:
                                elem.set(full_attr, 'Times New Roman')
                                modified = True
                elif tag_local in ['latin', 'ea', 'cs'] and elem.tag.startswith(f'{{{A_NS}}}'):
                    val = elem.get('typeface')
                    if val and val not in ['Symbol', 'Wingdings', 'Courier New', 'Times New Roman']:
                        elem.set('typeface', 'Times New Roman')
                        modified = True
                elif 'typeface' in elem.attrib:
                    val = elem.attrib['typeface']
                    if val and val not in ['Symbol', 'Wingdings', 'Courier New', 'Times New Roman']:
                        elem.attrib['typeface'] = 'Times New Roman'
                        modified = True
                        
            if modified:
                try:
                    tree.write(filepath, encoding='utf-8', xml_declaration=True)
                    print(f"  Fixed fonts in {os.path.relpath(filepath, directory)}")
                except Exception as e:
                    print(f"  Error writing {file}: {e}")

def force_field_update(unpacked_dir):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    settings_path = os.path.join(unpacked_dir, 'word', 'settings.xml')
    if os.path.exists(settings_path):
        tree = lxml.etree.parse(settings_path)
        root = tree.getroot()
        update_fields = root.find('w:updateFields', namespaces)
        if update_fields is not None:
            root.remove(update_fields)
            tree.write(settings_path, encoding='utf-8', xml_declaration=True, standalone=True)
            print("Removed updateFields from settings.xml to prevent popup.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python format_ta_proyek.py <unpacked_dir>")
        sys.exit(1)
    unpacked_dir = sys.argv[1]
    format_document_xmls(unpacked_dir)
    force_field_update(unpacked_dir)
    fix_all_fonts_lxml(unpacked_dir)
