import os
import re
import sys
import json
import argparse
from pathlib import Path

import lxml.etree

# Register all standard Office Open XML namespaces to preserve original prefixes
for prefix, uri in {
    'wpc': 'http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas',
    'cx': 'http://schemas.microsoft.com/office/drawing/2014/chartex',
    'cx1': 'http://schemas.microsoft.com/office/drawing/2015/9/8/chartex',
    'cx2': 'http://schemas.microsoft.com/office/drawing/2015/10/21/chartex',
    'cx3': 'http://schemas.microsoft.com/office/drawing/2016/5/9/chartex',
    'cx4': 'http://schemas.microsoft.com/office/drawing/2016/5/10/chartex',
    'cx5': 'http://schemas.microsoft.com/office/drawing/2016/5/11/chartex',
    'cx6': 'http://schemas.microsoft.com/office/drawing/2016/5/12/chartex',
    'cx7': 'http://schemas.microsoft.com/office/drawing/2016/5/13/chartex',
    'cx8': 'http://schemas.microsoft.com/office/drawing/2016/5/14/chartex',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
    'aink': 'http://schemas.microsoft.com/office/drawing/2016/ink',
    'am3d': 'http://schemas.microsoft.com/office/drawing/2017/model3d',
    'o': 'urn:schemas-microsoft-com:office:office',
    'oel': 'http://schemas.microsoft.com/office/2019/extlst',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
    'v': 'urn:schemas-microsoft-com:vml',
    'wp14': 'http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'w10': 'urn:schemas-microsoft-com:office:word',
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
    'w15': 'http://schemas.microsoft.com/office/word/2012/wordml',
    'w16cex': 'http://schemas.microsoft.com/office/word/2018/wordml/cex',
    'w16cid': 'http://schemas.microsoft.com/office/word/2016/wordml/cid',
    'w16': 'http://schemas.microsoft.com/office/word/2018/wordml',
    'w16du': 'http://schemas.microsoft.com/office/word/2023/wordml/word16du',
    'w16sdtdh': 'http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash',
    'w16sdtfl': 'http://schemas.microsoft.com/office/word/2024/wordml/sdtformatlock',
    'w16se': 'http://schemas.microsoft.com/office/word/2015/wordml/symex',
    'wpg': 'http://schemas.microsoft.com/office/word/2010/wordprocessingGroup',
    'wpi': 'http://schemas.microsoft.com/office/word/2010/wordprocessingInk',
    'wne': 'http://schemas.microsoft.com/office/word/2006/wordml',
    'wps': 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape'
}.items():
    lxml.etree.register_namespace(prefix, uri)

def parse_markdown(md_path):
    items = []
    
    if not os.path.exists(md_path):
        print(f"Error: {md_path} not found.")
        return items
        
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    in_chapter_or_later = False
    in_code_block = False
    code_lines = []
    code_lang = ""
    in_table = False
    table_lines = []
    
    # List item regex
    # Matches: 1. , a. , 1) , a)
    list_item_pattern = re.compile(r'^(\s*)([0-9a-zA-Z]+[\.\)])\s+(.*)$')
    
    for line in lines:
        stripped = line.strip()
        
        # Detect Chapter I start
        if not in_chapter_or_later:
            if stripped.startswith('# BAB I') or stripped.startswith('# BAB 1'):
                in_chapter_or_later = True
            else:
                continue
                
        # Handle code blocks
        if stripped.startswith('```'):
            if in_code_block:
                items.append({
                    'type': 'code_block',
                    'lang': code_lang,
                    'lines': code_lines
                })
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
                code_lang = stripped[3:].strip()
            continue
            
        if in_code_block:
            # Keep line as-is, just strip newline at the end
            code_lines.append(line.rstrip('\r\n'))
            continue
            
        # Handle tables
        if stripped.startswith('[TABLE]'):
            in_table = True
            table_lines = []
            continue
            
        if stripped.endswith('[/TABLE]'):
            in_table = False
            items.append({
                'type': 'table',
                'lines': table_lines
            })
            table_lines = []
            continue
            
        if in_table:
            if stripped:
                table_lines.append(stripped)
            continue
            
        # Handle page breaks
        if stripped == '---':
            items.append({'type': 'page_break'})
            continue
            
        # Handle headings
        if stripped.startswith('#'):
            # Count the # characters
            level = 0
            while level < len(stripped) and stripped[level] == '#':
                level += 1
            text = stripped[level:].strip()
            items.append({
                'type': 'heading',
                'level': level, # 1 for #, 2 for ##, etc.
                'text': text
            })
            continue
            
        # Handle list items
        list_match = list_item_pattern.match(line)
        if list_match:
            indent_spaces = len(list_match.group(1))
            marker = list_match.group(2)
            text_content = list_match.group(3)
            
            # Determine level based on marker and indent
            list_level = 1
            if marker.endswith('.'):
                if marker[:-1].isdigit():
                    list_level = 1
                else:
                    list_level = 2
            elif marker.endswith(')'):
                if marker[:-1].isdigit():
                    list_level = 3
                else:
                    list_level = 4
                    
            items.append({
                'type': 'list_item',
                'level': list_level,
                'marker': marker,
                'text': text_content
            })
            continue
            
        # Handle plain paragraphs
        if stripped:
            items.append({
                'type': 'paragraph',
                'text': stripped
            })
            
    return items

def add_formatted_text(p_elem, text, default_rPr=None):
    """
    Parses **bold** and *italic* markdown tags and adds runs to the paragraph.
    """
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    
    # Split text into tokens based on markdown formatting
    tokens = re.split(r'(\*\*|\*)', text)
    
    current_bold = False
    current_italic = False
    
    for token in tokens:
        if token == '**':
            current_bold = not current_bold
            continue
        elif token == '*':
            current_italic = not current_italic
            continue
            
        if not token:
            continue
            
        r = lxml.etree.Element(f'{{{ns_uri}}}r')
        rPr = lxml.etree.Element(f'{{{ns_uri}}}rPr')
        
        # Inherit default fonts and sizes
        if default_rPr is not None:
            for child in default_rPr:
                # Use deep copy for lxml elements
                rPr.append(lxml.etree.fromstring(lxml.etree.tostring(child)))
                
        # Set fonts explicitly to Times New Roman
        rFonts = rPr.find(f'{{{ns_uri}}}rFonts')
        if rFonts is None:
            rFonts = lxml.etree.Element(f'{{{ns_uri}}}rFonts')
            rPr.append(rFonts)
        rFonts.set(f'{{{ns_uri}}}ascii', 'Times New Roman')
        rFonts.set(f'{{{ns_uri}}}hAnsi', 'Times New Roman')
        
        # Set size explicitly if not set (sz val 24 = 12pt)
        sz = rPr.find(f'{{{ns_uri}}}sz')
        if sz is None:
            sz = lxml.etree.Element(f'{{{ns_uri}}}sz')
            sz.set(f'{{{ns_uri}}}val', '24')
            rPr.append(sz)
            
        szCs = rPr.find(f'{{{ns_uri}}}szCs')
        if szCs is None:
            szCs = lxml.etree.Element(f'{{{ns_uri}}}szCs')
            szCs.set(f'{{{ns_uri}}}val', '24')
            rPr.append(szCs)
            
        if current_bold:
            b = lxml.etree.Element(f'{{{ns_uri}}}b')
            bCs = lxml.etree.Element(f'{{{ns_uri}}}bCs')
            rPr.append(b)
            rPr.append(bCs)
            
        if current_italic:
            i = lxml.etree.Element(f'{{{ns_uri}}}i')
            iCs = lxml.etree.Element(f'{{{ns_uri}}}iCs')
            rPr.append(i)
            rPr.append(iCs)
            
        r.append(rPr)
        
        t = lxml.etree.Element(f'{{{ns_uri}}}t')
        t.text = token
        if token.startswith(' ') or token.endswith(' '):
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            
        r.append(t)
        p_elem.append(r)

def build_p_element(item):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    p = lxml.etree.Element(f'{{{ns_uri}}}p')
    pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
    p.append(pPr)
    
    if item['type'] == 'heading':
        style_val = f"Heading{item['level']}"
        lxml.etree.SubElement(pPr, f'{{{ns_uri}}}pStyle', {f'{{{ns_uri}}}val': style_val})
        
        # Heading 1 is centered
        if item['level'] == 1:
            lxml.etree.SubElement(pPr, f'{{{ns_uri}}}jc', {f'{{{ns_uri}}}val': 'center'})
        else:
            lxml.etree.SubElement(pPr, f'{{{ns_uri}}}jc', {f'{{{ns_uri}}}val': 'left'})
            
        # Add heading text with bold runs
        default_rPr = lxml.etree.Element(f'{{{ns_uri}}}rPr')
        sz_val = '28' if item['level'] == 1 else '24'
        lxml.etree.SubElement(default_rPr, f'{{{ns_uri}}}sz', {f'{{{ns_uri}}}val': sz_val})
        lxml.etree.SubElement(default_rPr, f'{{{ns_uri}}}szCs', {f'{{{ns_uri}}}val': sz_val})
        lxml.etree.SubElement(default_rPr, f'{{{ns_uri}}}b')
        lxml.etree.SubElement(default_rPr, f'{{{ns_uri}}}bCs')
        
        add_formatted_text(p, item['text'], default_rPr)
        
    elif item['type'] == 'page_break':
        r = lxml.etree.SubElement(p, f'{{{ns_uri}}}r')
        lxml.etree.SubElement(r, f'{{{ns_uri}}}br', {f'{{{ns_uri}}}type': 'page'})
        
    elif item['type'] == 'list_item':
        lxml.etree.SubElement(pPr, f'{{{ns_uri}}}pStyle', {f'{{{ns_uri}}}val': 'ListParagraph'})
        
        left_dxa = str(item['level'] * 360)
        lxml.etree.SubElement(pPr, f'{{{ns_uri}}}ind', {
            f'{{{ns_uri}}}left': left_dxa,
            f'{{{ns_uri}}}hanging': '360'
        })
        
        lxml.etree.SubElement(pPr, f'{{{ns_uri}}}spacing', {
            f'{{{ns_uri}}}before': '0',
            f'{{{ns_uri}}}after': '0',
            f'{{{ns_uri}}}line': '360',
            f'{{{ns_uri}}}lineRule': 'auto'
        })
        
        lxml.etree.SubElement(pPr, f'{{{ns_uri}}}jc', {f'{{{ns_uri}}}val': 'both'})
        
        marker_run = lxml.etree.SubElement(p, f'{{{ns_uri}}}r')
        marker_rPr = lxml.etree.SubElement(marker_run, f'{{{ns_uri}}}rPr')
        lxml.etree.SubElement(marker_rPr, f'{{{ns_uri}}}rFonts', {
            f'{{{ns_uri}}}ascii': 'Times New Roman',
            f'{{{ns_uri}}}hAnsi': 'Times New Roman'
        })
        lxml.etree.SubElement(marker_rPr, f'{{{ns_uri}}}sz', {f'{{{ns_uri}}}val': '24'})
        lxml.etree.SubElement(marker_rPr, f'{{{ns_uri}}}szCs', {f'{{{ns_uri}}}val': '24'})
        
        marker_t = lxml.etree.SubElement(marker_run, f'{{{ns_uri}}}t')
        marker_t.text = item['marker'] + "\t"
        marker_t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        
        add_formatted_text(p, item['text'])
        
    elif item['type'] == 'paragraph':
        is_caption = item['text'].startswith('Gambar ') or item['text'].startswith('Tabel ') or item['text'].startswith('LAMPIRAN ')
        
        if is_caption:
            lxml.etree.SubElement(pPr, f'{{{ns_uri}}}pStyle', {f'{{{ns_uri}}}val': 'Caption'})
            lxml.etree.SubElement(pPr, f'{{{ns_uri}}}jc', {f'{{{ns_uri}}}val': 'center'})
            lxml.etree.SubElement(pPr, f'{{{ns_uri}}}ind', {f'{{{ns_uri}}}firstLine': '0', f'{{{ns_uri}}}left': '0'})
            
            lxml.etree.SubElement(pPr, f'{{{ns_uri}}}spacing', {
                f'{{{ns_uri}}}before': '120',
                f'{{{ns_uri}}}after': '120',
                f'{{{ns_uri}}}line': '240',
                f'{{{ns_uri}}}lineRule': 'auto'
            })
            
            match = re.match(r'^(Gambar\s+[0-9\.]+|Tabel\s+[0-9\.]+|LAMPIRAN\s+[0-9\.]+)(.*)$', item['text'], re.IGNORECASE)
            if match:
                prefix = match.group(1)
                suffix = match.group(2)
                
                r_pref = lxml.etree.SubElement(p, f'{{{ns_uri}}}r')
                rPr_pref = lxml.etree.SubElement(r_pref, f'{{{ns_uri}}}rPr')
                lxml.etree.SubElement(rPr_pref, f'{{{ns_uri}}}rFonts', {
                    f'{{{ns_uri}}}ascii': 'Times New Roman',
                    f'{{{ns_uri}}}hAnsi': 'Times New Roman'
                })
                lxml.etree.SubElement(rPr_pref, f'{{{ns_uri}}}sz', {f'{{{ns_uri}}}val': '24'})
                lxml.etree.SubElement(rPr_pref, f'{{{ns_uri}}}szCs', {f'{{{ns_uri}}}val': '24'})
                lxml.etree.SubElement(rPr_pref, f'{{{ns_uri}}}b')
                lxml.etree.SubElement(rPr_pref, f'{{{ns_uri}}}bCs')
                
                t_pref = lxml.etree.SubElement(r_pref, f'{{{ns_uri}}}t')
                t_pref.text = prefix
                t_pref.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                
                add_formatted_text(p, suffix)
            else:
                add_formatted_text(p, item['text'])
        else:
            lxml.etree.SubElement(pPr, f'{{{ns_uri}}}pStyle', {f'{{{ns_uri}}}val': 'Normal'})
            lxml.etree.SubElement(pPr, f'{{{ns_uri}}}jc', {f'{{{ns_uri}}}val': 'both'})
            
            lxml.etree.SubElement(pPr, f'{{{ns_uri}}}spacing', {
                f'{{{ns_uri}}}before': '0',
                f'{{{ns_uri}}}after': '0',
                f'{{{ns_uri}}}line': '360',
                f'{{{ns_uri}}}lineRule': 'auto'
            })
            
            lxml.etree.SubElement(pPr, f'{{{ns_uri}}}ind', {
                f'{{{ns_uri}}}firstLine': '567',
                f'{{{ns_uri}}}left': '0'
            })
            
            add_formatted_text(p, item['text'])
            
    return p

def build_code_block_elements(item):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    elements = []
    
    for line in item['lines']:
        p = lxml.etree.Element(f'{{{ns_uri}}}p')
        pPr = lxml.etree.SubElement(p, f'{{{ns_uri}}}pPr')
        lxml.etree.SubElement(pPr, f'{{{ns_uri}}}pStyle', {f'{{{ns_uri}}}val': 'Normal'})
        lxml.etree.SubElement(pPr, f'{{{ns_uri}}}jc', {f'{{{ns_uri}}}val': 'left'})
        
        lxml.etree.SubElement(pPr, f'{{{ns_uri}}}ind', {
            f'{{{ns_uri}}}left': '720',
            f'{{{ns_uri}}}firstLine': '0'
        })
        
        lxml.etree.SubElement(pPr, f'{{{ns_uri}}}spacing', {
            f'{{{ns_uri}}}before': '0',
            f'{{{ns_uri}}}after': '0',
            f'{{{ns_uri}}}line': '240',
            f'{{{ns_uri}}}lineRule': 'auto'
        })
        
        r = lxml.etree.SubElement(p, f'{{{ns_uri}}}r')
        rPr = lxml.etree.SubElement(r, f'{{{ns_uri}}}rPr')
        
        lxml.etree.SubElement(rPr, f'{{{ns_uri}}}rFonts', {
            f'{{{ns_uri}}}ascii': 'Consolas',
            f'{{{ns_uri}}}hAnsi': 'Consolas'
        })
        lxml.etree.SubElement(rPr, f'{{{ns_uri}}}sz', {f'{{{ns_uri}}}val': '18'})
        lxml.etree.SubElement(rPr, f'{{{ns_uri}}}szCs', {f'{{{ns_uri}}}val': '18'})
        
        t = lxml.etree.SubElement(r, f'{{{ns_uri}}}t')
        t.text = line
        t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        
        elements.append(p)
        
    return elements

def build_table_element(item):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    tbl = lxml.etree.Element(f'{{{ns_uri}}}tbl')
    
    tblPr = lxml.etree.SubElement(tbl, f'{{{ns_uri}}}tblPr')
    lxml.etree.SubElement(tblPr, f'{{{ns_uri}}}tblStyle', {f'{{{ns_uri}}}val': 'TableGrid'})
    lxml.etree.SubElement(tblPr, f'{{{ns_uri}}}tblW', {f'{{{ns_uri}}}w': '0', f'{{{ns_uri}}}type': 'auto'})
    lxml.etree.SubElement(tblPr, f'{{{ns_uri}}}jc', {f'{{{ns_uri}}}val': 'center'})
    
    borders = lxml.etree.SubElement(tblPr, f'{{{ns_uri}}}tblBorders')
    for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        lxml.etree.SubElement(borders, f'{{{ns_uri}}}{border_name}', {
            f'{{{ns_uri}}}val': 'single',
            f'{{{ns_uri}}}sz': '4',
            f'{{{ns_uri}}}space': '0',
            f'{{{ns_uri}}}color': 'auto'
        })
        
    rows_data = []
    for line in item['lines']:
        cells = [c.strip() for c in line.split('|')]
        if line.startswith('|'):
            cells = cells[1:]
        if line.endswith('|'):
            cells = cells[:-1]
        rows_data.append(cells)
        
    if not rows_data:
        return tbl
        
    num_cols = max(len(r) for r in rows_data)
    tblGrid = lxml.etree.SubElement(tbl, f'{{{ns_uri}}}tblGrid')
    for _ in range(num_cols):
        lxml.etree.SubElement(tblGrid, f'{{{ns_uri}}}gridCol', {f'{{{ns_uri}}}w': '2000'})
        
    is_first_row = True
    for row_cells in rows_data:
        tr = lxml.etree.SubElement(tbl, f'{{{ns_uri}}}tr')
        
        trPr = lxml.etree.SubElement(tr, f'{{{ns_uri}}}trPr')
        lxml.etree.SubElement(trPr, f'{{{ns_uri}}}cantSplit')
        if is_first_row:
            lxml.etree.SubElement(trPr, f'{{{ns_uri}}}tblHeader')
            
        for cell_text in row_cells:
            tc = lxml.etree.SubElement(tr, f'{{{ns_uri}}}tc')
            tcPr = lxml.etree.SubElement(tc, f'{{{ns_uri}}}tcPr')
            lxml.etree.SubElement(tcPr, f'{{{ns_uri}}}tcW', {f'{{{ns_uri}}}w': '0', f'{{{ns_uri}}}type': 'auto'})
            
            p = lxml.etree.SubElement(tc, f'{{{ns_uri}}}p')
            pPr = lxml.etree.SubElement(p, f'{{{ns_uri}}}pPr')
            lxml.etree.SubElement(pPr, f'{{{ns_uri}}}pStyle', {f'{{{ns_uri}}}val': 'Normal'})
            lxml.etree.SubElement(pPr, f'{{{ns_uri}}}jc', {f'{{{ns_uri}}}val': 'left'})
            lxml.etree.SubElement(pPr, f'{{{ns_uri}}}ind', {f'{{{ns_uri}}}firstLine': '0', f'{{{ns_uri}}}left': '0'})
            
            lxml.etree.SubElement(pPr, f'{{{ns_uri}}}spacing', {
                f'{{{ns_uri}}}before': '60',
                f'{{{ns_uri}}}after': '60',
                f'{{{ns_uri}}}line': '240',
                f'{{{ns_uri}}}lineRule': 'auto'
            })
            
            default_rPr = None
            if is_first_row:
                default_rPr = lxml.etree.Element(f'{{{ns_uri}}}rPr')
                lxml.etree.SubElement(default_rPr, f'{{{ns_uri}}}b')
                lxml.etree.SubElement(default_rPr, f'{{{ns_uri}}}bCs')
                
            add_formatted_text(p, cell_text, default_rPr)
            
        is_first_row = False
        
    return tbl

# --- Aturan_Umum association matching helpers (pure, importable) — Task 8.1, R4.1/R4.2/R4.5 ---

# Code-like text patterns reused as a general structural guard (never match drawings to code).
_CODE_PATTERNS = ['$$', 'LANGUAGE plpgsql', 'CREATE TRIGGER', 'CREATE OR REPLACE',
                  'EXECUTE FUNCTION', 'RETURNS TRIGGER', 'BEGIN', 'END;',
                  'INSERT INTO', 'SELECT ', 'FROM ', 'WHERE ', 'VALUES (',
                  'function()', '=>', 'import ', 'export ', 'const ', 'let ', 'var ']


def normalize_assoc_text(t):
    """Normalize text for association matching (R4.1).

    Steps: lowercase, strip a leading caption prefix ``gambar|tabel|lampiran <num>``,
    collapse whitespace, and remove non-alphanumeric characters. Returns a compact
    lowercase alphanumeric string so that matching is invariant to capitalization,
    whitespace, and punctuation.
    """
    if not t:
        return ""
    t = t.lower()
    # Strip a leading caption prefix like "gambar 2.10 ", "tabel 1.1 ", "lampiran 3 "
    t = re.sub(r'^\s*(gambar|tabel|lampiran)\s+[0-9]+(?:\.[0-9]+)*\.?\s*', '', t)
    # Collapse whitespace
    t = re.sub(r'\s+', ' ', t).strip()
    # Remove non-alphanumeric chars
    t = re.sub(r'[^a-z0-9]', '', t)
    return t


def is_caption_text(t):
    """True if the stripped, lowercased text starts with "gambar" or "tabel" (R4.5)."""
    if not t:
        return False
    s = t.strip().lower()
    return s.startswith("gambar") or s.startswith("tabel")


def find_template_matches(assoc_text, candidates):
    """Find paragraphs matching a template drawing's associated text (Aturan_Umum).

    Args:
        assoc_text: text associated with the template drawing (caption or body).
        candidates: list of ``(doc_order_idx, paragraph_text)`` tuples in document order.

    Returns:
        list[int]: the ``doc_order_idx`` values whose paragraph text matches, in
        document order. Matching rules:
          - same-type only: ``is_caption_text(assoc_text) == is_caption_text(p_text)`` (R4.5)
          - match when ``normalize_assoc_text(assoc_text)`` is contained in
            ``normalize_assoc_text(p_text)`` as a substring (R4.1)
          - structural guards (general, not named special cases): reject paragraph text
            shorter than 15 chars and reject code-like text (``_CODE_PATTERNS``)
          - NO special-cases by image filename or term mapping (R4.2)
    """
    matches = []
    if not assoc_text:
        return matches

    assoc_is_caption = is_caption_text(assoc_text)
    norm_assoc = normalize_assoc_text(assoc_text)
    if not norm_assoc:
        return matches

    for idx, p_text in candidates:
        if not p_text:
            continue
        # Reject very short paragraph text — too ambiguous for matching
        if len(p_text.strip()) < 15:
            continue
        # Captions must only match captions, and body text must only match body text
        if is_caption_text(p_text) != assoc_is_caption:
            continue
        # Reject code-like text — never match drawings to code fragments
        p_stripped = p_text.strip()
        if any(p_stripped.startswith(pat) or p_stripped.endswith(pat) for pat in _CODE_PATTERNS):
            continue
        norm_p = normalize_assoc_text(p_text)
        if not norm_p:
            continue
        if norm_assoc in norm_p:
            matches.append(idx)

    return matches


def extract_drawings_from_xml(xml_path, bab1_idx=-1):
    """
    Extracts all drawings in BAB I and II from the template XML, mapping them
    to semantic keys (like following caption text, following paragraph text, or target image name).
    """
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    
    parser = lxml.etree.XMLParser(remove_blank_text=False)
    if not os.path.exists(xml_path):
        return {}
    tree = lxml.etree.parse(xml_path, parser)
    root = tree.getroot()
    body = root.find('w:body', namespaces)
    if body is None:
        return {}
        
    drawings_map = {}
    children = list(body)
    
    # We need to read relations to know the target image name
    rels_path = os.path.join(os.path.dirname(xml_path), "_rels", "document.xml.rels")
    rel_map = {}
    if os.path.exists(rels_path):
        rels_tree = lxml.etree.parse(rels_path, parser)
        rels_root = rels_tree.getroot()
        for rel in rels_root:
            r_id = rel.get('Id')
            target = rel.get('Target')
            rel_map[r_id] = target
            
    for idx, child in enumerate(children):
        if bab1_idx != -1 and idx < bab1_idx:
            continue
        if child.tag == f'{{{ns_uri}}}p':
            drawings = child.findall('.//w:drawing', namespaces)
            if drawings:
                # Find the associated text (following paragraph or caption)
                assoc_text = ""
                # Check next 3 paragraphs for non-empty text
                for offset in range(1, 4):
                    ni = idx + offset
                    if ni < len(children):
                        nc = children[ni]
                        if nc.tag == f'{{{ns_uri}}}p':
                            t_text = "".join([t.text for t in nc.iter(f'{{{ns_uri}}}t') if t.text]).strip()
                            if t_text:
                                assoc_text = t_text
                                break
                
                # Also find target image name for key matching
                target_img = ""
                for drawing in drawings:
                    blip = drawing.find('.//a:blip', {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'})
                    if blip is not None:
                        embed_id = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                        target_img = rel_map.get(embed_id, "")
                        break
                
                # Deep copy paragraph element
                p_copy = lxml.etree.fromstring(lxml.etree.tostring(child))
                
                drawings_map[idx] = {
                    'p_elem': p_copy,
                    'assoc_text': assoc_text,
                    'target_img': target_img,
                    'is_caption': is_caption_text(assoc_text)
                }
                print(f"Extracted template drawing: idx={idx}, target_img={target_img}, assoc_text='{assoc_text[:60]}'")
                
    return drawings_map

def merge_draft_to_xml(xml_path, parsed_items):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    
    # Register namespaces globally to avoid prefix changes in writing
    lxml.etree.register_namespace('w', ns_uri)
    
    # Use lxml parser to preserve namespaces and format
    parser = lxml.etree.XMLParser(remove_blank_text=False)
    tree = lxml.etree.parse(xml_path, parser)
    root = tree.getroot()
    
    body = root.find('w:body', namespaces)
    if body is None:
        print("Error: w:body not found in document.xml")
        return
        
    # Find the paragraph corresponding to BAB 1
    bab1_idx = -1
    children = list(body)
    
    for idx, child in enumerate(children):
        if child.tag == f'{{{ns_uri}}}p':
            pPr = child.find('w:pPr', namespaces)
            if pPr is not None:
                pStyle = pPr.find('w:pStyle', namespaces)
                if pStyle is not None:
                    style_val = pStyle.get(f'{{{ns_uri}}}val')
                    if style_val == 'Heading1':
                        text = "".join([t.text for t in child.iter(f'{{{ns_uri}}}t') if t.text])
                        if 'BAB 1' in text.upper() or 'BAB I' in text.upper():
                            bab1_idx = idx
                            break
                            
    if bab1_idx == -1:
        print("Error: Could not find BAB 1 / BAB I Heading1 paragraph in document.xml")
        return
        
    print(f"Found BAB 1 heading paragraph at index {bab1_idx}. Preserving cover page.")
    
    # Extract drawings (restricted to index >= bab1_idx)
    drawings_map = extract_drawings_from_xml(xml_path, bab1_idx)
    
    # Preserve the last sectPr element
    sectPr = body.find('w:sectPr', namespaces)
    if sectPr is not None:
        body.remove(sectPr)
        
    # Remove elements starting from bab1_idx to the end
    elements_to_remove = children[bab1_idx:]
    for child in reversed(elements_to_remove):
        if child in body:
            body.remove(child)
            
    print(f"Removed {len(elements_to_remove)} placeholder elements.")
    
    # Build and insert new XML elements
    new_elements = []
    for item in parsed_items:
        if item['type'] in ['heading', 'page_break', 'list_item', 'paragraph']:
            p_elem = build_p_element(item)
            new_elements.append(p_elem)
        elif item['type'] == 'code_block':
            new_elements.extend(build_code_block_elements(item))
        elif item['type'] == 'table':
            tbl_elem = build_table_element(item)
            new_elements.append(tbl_elem)
            
    # Inject matched template drawings back using the Aturan_Umum matching policy
    # (find_template_matches + tie-break + logging). R4.2/R4.3/R4.4/R4.5.
    #
    # Build the candidate list of (doc_order_idx, paragraph_text) for the new body
    # paragraphs in document order. doc_order_idx is the index into new_elements.
    candidates = []
    for i, elem in enumerate(new_elements):
        if elem.tag == f'{{{ns_uri}}}p':
            p_text = "".join([t.text for t in elem.iter(f'{{{ns_uri}}}t') if t.text]).strip()
            if p_text:
                candidates.append((i, p_text))

    # For each template drawing (in document order of the template), compute matches
    # over the not-yet-consumed candidate paragraphs and apply the selection policy.
    consumed = set()                    # doc_order_idx values already claimed by a drawing
    inject_before = {}                  # doc_order_idx -> [drawing entries] to inject before it
    injected_count = 0

    for key in sorted(drawings_map.keys()):
        dr = drawings_map[key]
        available = [(idx, txt) for (idx, txt) in candidates if idx not in consumed]
        matches = find_template_matches(dr['assoc_text'], available)

        if not matches:
            # 0 matches (R4.3): log and continue, do not stop.
            print(f"  Gambar_Template tidak terpasang: target_img={dr['target_img']} "
                  f"assoc_text='{dr['assoc_text'][:80]}'")
            continue

        if len(matches) > 1:
            # >1 matches (R4.4): pick the smallest index (first in document order) and warn.
            cand_preview = [(idx, dict(candidates).get(idx, '')[:40]) for idx in matches]
            print(f"  WARNING kecocokan ganda: target_img={dr['target_img']} "
                  f"assoc_text='{dr['assoc_text'][:60]}' kandidat={cand_preview}; "
                  f"memilih indeks {min(matches)} (pertama urutan dokumen)")

        target_idx = min(matches)       # 1 match -> inject; >1 -> first in document order
        consumed.add(target_idx)
        inject_before.setdefault(target_idx, []).append(dr)
        injected_count += 1

    # Assemble final elements, injecting each drawing paragraph before its matched paragraph.
    final_elements = []
    for i, elem in enumerate(new_elements):
        for dr in inject_before.get(i, []):
            final_elements.append(dr['p_elem'])
            p_text = "".join([t.text for t in elem.iter(f'{{{ns_uri}}}t') if t.text]).strip()
            print(f"  Injected template drawing {dr['target_img']} before paragraph: '{p_text[:80]}'")
        final_elements.append(elem)

    unmatched_count = len(drawings_map) - injected_count
    print(f"Total drawings injected: {injected_count} (out of {len(drawings_map)} extracted, "
          f"{unmatched_count} unmatched)")
    
    for elem in final_elements:
        body.append(elem)
        
    print(f"Appended {len(final_elements)} new elements.")
    
    if sectPr is not None:
        body.append(sectPr)
        print("Re-appended document section properties (sectPr).")
        
    # Write back to XML
    tree.write(xml_path, encoding='utf-8', xml_declaration=True)
    print("document.xml updated successfully.")

def resolve_path(p, workspace_root):
    """Resolve a path against the workspace root (R7.2, R7.3).

    Returns ``Path(p)`` unchanged when ``p`` is absolute; otherwise returns
    ``workspace_root / p``. No fixed absolute paths are used; every relative path
    is anchored to the workspace root.
    """
    path = Path(p)
    if path.is_absolute():
        return path
    return Path(workspace_root) / path


def read_path_config(workspace_root):
    """Read optional path configuration (R7.1).

    Looks for an optional JSON config file ``merge_config.json`` at the workspace
    root. If present, returns a dict with optional ``draft`` and ``xml`` keys
    (relative or absolute paths as written). If absent or unreadable, returns an
    empty dict so callers fall back to defaults.
    """
    cfg_path = Path(workspace_root) / "merge_config.json"
    if not cfg_path.exists():
        return {}
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
        print(f"Warning: config file {cfg_path} is not a JSON object; ignoring.")
        return {}
    except (OSError, json.JSONDecodeError) as e:
        print(f"Warning: could not read config file {cfg_path}: {e}; ignoring.")
        return {}


def main(argv=None):
    # workspace_root = repo root. This script lives in scratch/, so parents[1]
    # is the repository root directory (e.g. .../document).
    workspace_root = Path(__file__).resolve().parents[1]

    # Path resolution priority: argv > config file (optional) > relative defaults.
    parser = argparse.ArgumentParser(
        description="Merge Tugas_Akhir_Draft.md into the unpacked document.xml."
    )
    parser.add_argument("draft_md", nargs="?", default=None,
                        help="Path to the draft Markdown file (default: Tugas_Akhir_Draft.md)")
    parser.add_argument("document_xml", nargs="?", default=None,
                        help="Path to the output document.xml "
                             "(default: unpacked_ta/word/document.xml)")
    args = parser.parse_args(argv)

    cfg = read_path_config(workspace_root)

    draft_arg = args.draft_md or cfg.get("draft") or "Tugas_Akhir_Draft.md"
    xml_arg = args.document_xml or cfg.get("xml") or "unpacked_ta/word/document.xml"

    md_path = resolve_path(draft_arg, workspace_root)
    xml_path = resolve_path(xml_arg, workspace_root)

    # Pre-write validation (R7.4/R7.5): stop BEFORE writing anything if inputs are invalid.
    # The draft file must exist and be readable.
    if not md_path.exists():
        print(f"Error: draft file not found: {md_path}")
        sys.exit(1)
    if not os.access(md_path, os.R_OK):
        print(f"Error: draft file is not readable: {md_path}")
        sys.exit(1)
    # The output document.xml's parent directory must exist.
    if not xml_path.parent.is_dir():
        print(f"Error: output directory does not exist: {xml_path.parent}")
        sys.exit(1)

    print("Parsing draft Markdown file...")
    items = parse_markdown(str(md_path))
    print(f"Parsed {len(items)} items from Markdown.")

    print("Merging into document.xml using lxml...")
    merge_draft_to_xml(str(xml_path), items)


if __name__ == "__main__":
    main()
