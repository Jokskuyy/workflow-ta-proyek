"""Frozen oracle copies of the CURRENT (pre-refactor) pure writing functions.

WPI Task 1.2 (preservation safety net). These are VERBATIM snapshots of
``add_formatted_text`` and ``build_table_element`` from
``scratch/merge_draft_to_docx.py`` as they exist BEFORE the writing-pipeline
refactor. They are frozen here so later byte-equivalence tests (design
Properties 8, 11, and 16) can compare the new implementations against the old
behavior.

DO NOT EDIT the oracle function bodies to track refactors - that would defeat
the purpose. Only the public names are prefixed with ``oracle_`` and
``build_table_element`` calls the oracle ``add_formatted_text`` so the module is
self-contained and runnable in isolation.

Dependencies: only ``re`` and ``lxml.etree`` (no import of the production
module), so the frozen behavior cannot drift when production code changes.
"""
from __future__ import annotations

import re

import lxml.etree


# --------------------------------------------------------------------------- #
# VERBATIM snapshot of add_formatted_text (renamed oracle_add_formatted_text).
# --------------------------------------------------------------------------- #
def oracle_add_formatted_text(p_elem, text, default_rPr=None):
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


# --------------------------------------------------------------------------- #
# VERBATIM snapshot of build_table_element (renamed oracle_build_table_element).
# Internal add_formatted_text call routed to the oracle copy above so this
# module is self-contained and frozen.
# --------------------------------------------------------------------------- #
def oracle_build_table_element(item):
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

            oracle_add_formatted_text(p, cell_text, default_rPr)

        is_first_row = False

    return tbl


# --------------------------------------------------------------------------- #
# Comparison helper for byte-per-byte preservation tests (Properties 8/11/16).
# --------------------------------------------------------------------------- #
def serialize(el) -> bytes:
    """Serialize an lxml element to canonical bytes for byte-equivalence checks."""
    return lxml.etree.tostring(el)
