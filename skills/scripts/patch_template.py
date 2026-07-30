import os
import re
import shutil
import json
import lxml.etree

# Register all namespaces
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
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
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
    'w16se': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'wpg': 'http://schemas.microsoft.com/office/word/2010/wordprocessingGroup',
    'wpi': 'http://schemas.microsoft.com/office/word/2010/wordprocessingInk',
    'wne': 'http://schemas.microsoft.com/office/word/2006/wordml',
    'wps': 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape'
}.items():
    lxml.etree.register_namespace(prefix, uri)

import sys
sys.path.append('scratch')
from merge_draft_to_docx import build_p_element

W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PACKAGE_REL_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'
CONTENT_TYPES_NS = 'http://schemas.openxmlformats.org/package/2006/content-types'
A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'
PIC_NS = 'http://schemas.openxmlformats.org/drawingml/2006/picture'
WP_NS = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
XML_NS = 'http://www.w3.org/XML/1998/namespace'
IMAGE_REL_TYPE = (
    'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'
)


def _front_run(text, *, bold=False, size=24):
    run = lxml.etree.Element(f'{{{W_NS}}}r')
    run_pr = lxml.etree.SubElement(run, f'{{{W_NS}}}rPr')
    lxml.etree.SubElement(run_pr, f'{{{W_NS}}}rFonts', {
        f'{{{W_NS}}}ascii': 'Times New Roman',
        f'{{{W_NS}}}hAnsi': 'Times New Roman',
        f'{{{W_NS}}}eastAsia': 'Times New Roman',
        f'{{{W_NS}}}cs': 'Times New Roman',
    })
    if bold:
        lxml.etree.SubElement(run_pr, f'{{{W_NS}}}b')
        lxml.etree.SubElement(run_pr, f'{{{W_NS}}}bCs')
    lxml.etree.SubElement(run_pr, f'{{{W_NS}}}sz', {f'{{{W_NS}}}val': str(size)})
    lxml.etree.SubElement(run_pr, f'{{{W_NS}}}szCs', {f'{{{W_NS}}}val': str(size)})
    text_el = lxml.etree.SubElement(run, f'{{{W_NS}}}t')
    text_el.text = text
    if text.startswith(' ') or text.endswith(' '):
        text_el.set(f'{{{XML_NS}}}space', 'preserve')
    return run


def _front_paragraph(
    text='', *, style=None, bold=False, align='both', line=276,
    first_line=567, page_break_before=False, before=0, after=120,
    left=None, hanging=None, keep_next=False, size=24,
):
    paragraph = lxml.etree.Element(f'{{{W_NS}}}p')
    p_pr = lxml.etree.SubElement(paragraph, f'{{{W_NS}}}pPr')
    if style:
        lxml.etree.SubElement(p_pr, f'{{{W_NS}}}pStyle', {f'{{{W_NS}}}val': style})
    if keep_next:
        lxml.etree.SubElement(p_pr, f'{{{W_NS}}}keepNext')
        lxml.etree.SubElement(p_pr, f'{{{W_NS}}}keepLines')
    if page_break_before:
        lxml.etree.SubElement(p_pr, f'{{{W_NS}}}pageBreakBefore')
    lxml.etree.SubElement(p_pr, f'{{{W_NS}}}spacing', {
        f'{{{W_NS}}}before': str(before),
        f'{{{W_NS}}}after': str(after),
        f'{{{W_NS}}}line': str(line),
        f'{{{W_NS}}}lineRule': 'auto',
    })
    ind_attrs = {f'{{{W_NS}}}firstLine': str(first_line)}
    if left is not None:
        ind_attrs[f'{{{W_NS}}}left'] = str(left)
    if hanging is not None:
        ind_attrs.pop(f'{{{W_NS}}}firstLine', None)
        ind_attrs[f'{{{W_NS}}}hanging'] = str(hanging)
    lxml.etree.SubElement(p_pr, f'{{{W_NS}}}ind', ind_attrs)
    lxml.etree.SubElement(p_pr, f'{{{W_NS}}}jc', {f'{{{W_NS}}}val': align})
    if text:
        paragraph.append(_front_run(text, bold=bold, size=size))
    return paragraph


def _front_heading(text, *, toc=False, page_break_before=True):
    return _front_paragraph(
        text,
        style='FrontMatterHeading' if toc else None,
        bold=True,
        align='center',
        line=276,
        first_line=0,
        page_break_before=page_break_before,
        before=0,
        after=240,
        keep_next=True,
    )


def _front_keywords(label, values):
    paragraph = _front_paragraph(
        align='left', line=240, first_line=0, before=120, after=0,
    )
    paragraph.append(_front_run(label, bold=True))
    paragraph.append(_front_run(' ' + ', '.join(values), bold=False))
    return paragraph


def _front_centered_pair(left_text, right_text, *, before=0, after=0):
    """Create two centered text blocks without introducing a layout table."""
    paragraph = _front_paragraph(
        align='left', line=240, first_line=0, before=before, after=after,
    )
    p_pr = paragraph.find(f'{{{W_NS}}}pPr')
    tabs = lxml.etree.SubElement(p_pr, f'{{{W_NS}}}tabs')
    for position in (1984, 5953):
        lxml.etree.SubElement(tabs, f'{{{W_NS}}}tab', {
            f'{{{W_NS}}}val': 'center',
            f'{{{W_NS}}}pos': str(position),
        })
    for text in (left_text, right_text):
        tab_run = lxml.etree.Element(f'{{{W_NS}}}r')
        tab_run.append(lxml.etree.Element(f'{{{W_NS}}}tab'))
        paragraph.append(tab_run)
        paragraph.append(_front_run(text))
    return paragraph


def _front_dotted_field(label='', *, end_position=7938, before=0, after=0):
    """Create a form line whose empty value is represented by a dot leader."""
    paragraph = _front_paragraph(
        align='left', line=240, first_line=0, before=before, after=after,
    )
    p_pr = paragraph.find(f'{{{W_NS}}}pPr')
    tabs = lxml.etree.SubElement(p_pr, f'{{{W_NS}}}tabs')
    if label:
        lxml.etree.SubElement(tabs, f'{{{W_NS}}}tab', {
            f'{{{W_NS}}}val': 'left',
            f'{{{W_NS}}}pos': '1700',
        })
    lxml.etree.SubElement(tabs, f'{{{W_NS}}}tab', {
        f'{{{W_NS}}}val': 'right',
        f'{{{W_NS}}}leader': 'dot',
        f'{{{W_NS}}}pos': str(end_position),
    })
    if label:
        paragraph.append(_front_run(label))
        label_tab = lxml.etree.Element(f'{{{W_NS}}}r')
        label_tab.append(lxml.etree.Element(f'{{{W_NS}}}tab'))
        paragraph.append(label_tab)
        paragraph.append(_front_run(':'))
    leader_tab = lxml.etree.Element(f'{{{W_NS}}}r')
    leader_tab.append(lxml.etree.Element(f'{{{W_NS}}}tab'))
    paragraph.append(leader_tab)
    return paragraph


def _front_labeled_value(label, value, *, before=0, after=0):
    """Create a label and value separated by a stable tab stop."""
    paragraph = _front_paragraph(
        align='left', line=240, first_line=0, before=before, after=after,
    )
    p_pr = paragraph.find(f'{{{W_NS}}}pPr')
    tabs = lxml.etree.SubElement(p_pr, f'{{{W_NS}}}tabs')
    lxml.etree.SubElement(tabs, f'{{{W_NS}}}tab', {
        f'{{{W_NS}}}val': 'left',
        f'{{{W_NS}}}pos': '1700',
    })
    paragraph.append(_front_run(label))
    label_tab = lxml.etree.Element(f'{{{W_NS}}}r')
    label_tab.append(lxml.etree.Element(f'{{{W_NS}}}tab'))
    paragraph.append(label_tab)
    paragraph.append(_front_run(': ' + value))
    return paragraph


def _front_table_cell(
        lines, *, width, grid_span=1, align='left', bold_first=False,
        signature_space=False):
    cell = lxml.etree.Element(f'{{{W_NS}}}tc')
    cell_pr = lxml.etree.SubElement(cell, f'{{{W_NS}}}tcPr')
    lxml.etree.SubElement(cell_pr, f'{{{W_NS}}}tcW', {
        f'{{{W_NS}}}w': str(width),
        f'{{{W_NS}}}type': 'dxa',
    })
    if grid_span > 1:
        lxml.etree.SubElement(cell_pr, f'{{{W_NS}}}gridSpan', {
            f'{{{W_NS}}}val': str(grid_span),
        })
    borders = lxml.etree.SubElement(cell_pr, f'{{{W_NS}}}tcBorders')
    for side in ('top', 'left', 'bottom', 'right'):
        lxml.etree.SubElement(borders, f'{{{W_NS}}}{side}', {
            f'{{{W_NS}}}val': 'nil',
        })
    vertical_alignment = 'center' if signature_space else 'top'
    lxml.etree.SubElement(cell_pr, f'{{{W_NS}}}vAlign', {
        f'{{{W_NS}}}val': vertical_alignment,
    })

    rendered_lines = list(lines) or ['']
    if signature_space:
        rendered_lines = ['', ''] + rendered_lines
    for index, line in enumerate(rendered_lines):
        cell.append(_front_paragraph(
            line,
            bold=bool(bold_first and index == 0 and line),
            align=align,
            line=240,
            first_line=0,
            before=0,
            after=0,
        ))
    return cell


def _front_table_row(cells):
    row = lxml.etree.Element(f'{{{W_NS}}}tr')
    row_pr = lxml.etree.SubElement(row, f'{{{W_NS}}}trPr')
    lxml.etree.SubElement(row_pr, f'{{{W_NS}}}cantSplit')
    for cell in cells:
        row.append(cell)
    return row


def _build_approval_table(config):
    """Build the editable four-column approval table from the latest Iman DOCX."""
    table = lxml.etree.Element(f'{{{W_NS}}}tbl')
    table_pr = lxml.etree.SubElement(table, f'{{{W_NS}}}tblPr')
    lxml.etree.SubElement(table_pr, f'{{{W_NS}}}tblStyle', {
        f'{{{W_NS}}}val': 'TableGrid',
    })
    lxml.etree.SubElement(table_pr, f'{{{W_NS}}}tblW', {
        f'{{{W_NS}}}w': '7927',
        f'{{{W_NS}}}type': 'dxa',
    })
    lxml.etree.SubElement(table_pr, f'{{{W_NS}}}jc', {
        f'{{{W_NS}}}val': 'center',
    })
    # A structural marker lets the general body-table formatter preserve the
    # borderless approval-page layout.
    lxml.etree.SubElement(table_pr, f'{{{W_NS}}}tblCaption', {
        f'{{{W_NS}}}val': 'FRONT_MATTER_APPROVAL',
    })
    table_grid = lxml.etree.SubElement(table, f'{{{W_NS}}}tblGrid')
    for width in (1980, 283, 3402, 2262):
        lxml.etree.SubElement(table_grid, f'{{{W_NS}}}gridCol', {
            f'{{{W_NS}}}w': str(width),
        })

    for label, value in config['identity'].items():
        table.append(_front_table_row([
            _front_table_cell([label], width=1980),
            _front_table_cell([':'], width=283),
            _front_table_cell([value], width=5664, grid_span=2),
        ]))

    table.append(_front_table_row([
        _front_table_cell(
            ['Disetujui oleh:'],
            width=7927,
            grid_span=4,
            align='center',
            bold_first=True,
        ),
    ]))
    for item in config['approved_by']:
        table.append(_front_table_row([
            _front_table_cell(
                [f"{item['role']}:", item['name'], ''],
                width=5665,
                grid_span=3,
            ),
            _front_table_cell(
                [config['signature_line']],
                width=2262,
                align='center',
                signature_space=True,
            ),
        ]))

    table.append(_front_table_row([
        _front_table_cell(
            ['Diketahui oleh:'],
            width=7927,
            grid_span=4,
            align='center',
            bold_first=True,
        ),
    ]))
    for item in config['known_by']:
        table.append(_front_table_row([
            _front_table_cell(
                [f"{item['role']}:", item['name'], item['employee_id'], ''],
                width=5665,
                grid_span=3,
            ),
            _front_table_cell(
                [config['signature_line']],
                width=2262,
                align='center',
                signature_space=True,
            ),
        ]))

    table.append(_front_table_row([
        _front_table_cell(
            [
                '',
                f"{config['exam_date_label']}:",
                config['exam_date'],
            ],
            width=5665,
            grid_span=3,
        ),
        _front_table_cell([''], width=2262),
    ]))
    return table


def _replace_paragraph_text(paragraph, text, *, bold=False, size=28):
    p_pr = paragraph.find(f'{{{W_NS}}}pPr')
    for child in list(paragraph):
        if child is not p_pr:
            paragraph.remove(child)
    if text:
        paragraph.append(_front_run(text, bold=bold, size=size))


def _paragraph_text(element):
    return ''.join(element.itertext()).strip()


def _append_hidden_scan_heading(paragraph, heading):
    """Return a 1 pt white TOC anchor followed by its full-page scan."""
    anchor = _front_paragraph(
        heading,
        style='FrontMatterHeading',
        align='center',
        line=2,
        first_line=0,
        before=0,
        after=0,
        keep_next=True,
        size=2,
    )
    anchor_properties = anchor.find(f'{{{W_NS}}}r/{{{W_NS}}}rPr')
    lxml.etree.SubElement(
        anchor_properties,
        f'{{{W_NS}}}color',
        {f'{{{W_NS}}}val': 'FFFFFF'},
    )
    lxml.etree.SubElement(anchor_properties, f'{{{W_NS}}}noProof')
    return anchor, paragraph


def _build_front_matter(
        config, *, declaration_signature=None, approval_scan=None,
        front_matter_scans=None):
    title_page = config['report_title_page']
    authenticity = config['authenticity_statement']
    abstract_id = config['abstract_id']
    abstract_en = config['abstract_en']
    preface = config['preface']
    uses_latest_iman_front_matter = (
        'approval_page' in config and 'publication_permission' in config
    )
    approval = config.get('approval_page')
    publication = config.get('publication_permission')
    declaration = config.get('declaration')
    front_matter_scans = front_matter_scans or {}
    elements = []

    elements.append(_front_paragraph(
        title_page['heading'],
        style='FrontMatterHeading' if uses_latest_iman_front_matter else None,
        bold=True, align='center', line=276,
        first_line=0, page_break_before=True, after=720, size=28,
    ))
    elements.append(_front_paragraph(
        title_page['title'], bold=True, align='center', line=276,
        first_line=0, after=1440, size=28,
    ))
    elements.append(_front_paragraph(
        title_page['author'], bold=True, align='center', line=276,
        first_line=0, after=120, size=28,
    ))
    elements.append(_front_paragraph(
        title_page['nim'], bold=True, align='center', line=276,
        first_line=0, after=1440, size=28,
    ))
    for index, key in enumerate((
        'program_study', 'faculty', 'university', 'city', 'year',
    )):
        elements.append(_front_paragraph(
            title_page[key], bold=True, align='center', line=276,
            first_line=0, after=0 if index == 4 else 120, size=28,
        ))

    if uses_latest_iman_front_matter:
        signed_scan = front_matter_scans.get('approval')
        if signed_scan is not None:
            elements.extend(_append_hidden_scan_heading(
                signed_scan, approval['heading'],
            ))
        else:
            elements.append(_front_heading(approval['heading'], toc=True))
            elements.append(_build_approval_table(approval))

    authenticity_scan = front_matter_scans.get('authenticity')
    if authenticity_scan is not None:
        elements.extend(_append_hidden_scan_heading(
            authenticity_scan, authenticity['heading'],
        ))
    else:
        elements.append(_front_heading(
            authenticity['heading'], toc=uses_latest_iman_front_matter,
        ))
        elements.append(_front_paragraph(
            authenticity['intro'], align='left', line=240, first_line=0,
            before=120, after=60,
        ))
        for label, value in authenticity['identity'].items():
            elements.append(_front_labeled_value(label, value, after=60))
        for paragraph in authenticity['paragraphs']:
            elements.append(_front_paragraph(
                paragraph, line=276, first_line=567, before=120, after=120,
            ))
        elements.append(_front_paragraph(
            authenticity['date'], align='right', line=240, first_line=0,
            before=240, after=0, keep_next=True,
        ))
        elements.append(_front_paragraph(
            authenticity['declarant_label'], align='right', line=240,
            first_line=0, before=0,
            after=int(authenticity.get('signature_space_lines', 0)) * 240,
            keep_next=True,
        ))
        elements.append(_front_paragraph(
            authenticity['author'], align='right', line=240, first_line=0,
            before=0, after=0,
        ))

    if uses_latest_iman_front_matter:
        publication_scan = front_matter_scans.get('publication')
        if publication_scan is not None:
            elements.extend(_append_hidden_scan_heading(
                publication_scan, publication['heading'],
            ))
        else:
            elements.append(_front_heading(publication['heading'], toc=True))
            elements.append(_front_paragraph(
                publication['intro'], align='left', line=240, first_line=0,
                before=120, after=60,
            ))
            for label in publication['blank_identity_labels']:
                elements.append(_front_dotted_field(label, after=60))
            elements.append(_front_paragraph(
                publication['paragraphs'][0],
                line=276,
                first_line=567,
                before=120,
                after=120,
            ))
            for _ in range(int(publication.get('title_blank_lines', 3))):
                elements.append(_front_dotted_field(after=60))
            elements.append(_front_paragraph(
                publication['paragraphs'][1],
                line=276,
                first_line=567,
                before=120,
                after=120,
            ))
            elements.append(_front_paragraph(
                publication['date'], align='right', first_line=0,
                before=240, after=0, keep_next=True,
            ))
            elements.append(_front_paragraph(
                publication['author'], align='right', first_line=0,
                before=int(publication.get('signature_space_lines', 0)) * 240,
                after=0,
                keep_next=True,
            ))
            elements.append(_front_paragraph(
                publication['nim'], align='right', first_line=0, after=0,
            ))
    else:
        elements.append(_front_heading(declaration['heading'], toc=False))
        for paragraph in declaration['paragraphs']:
            elements.append(_front_paragraph(paragraph))
        elements.append(_front_paragraph(
            declaration['date'], align='right', first_line=0,
            before=360, after=0, keep_next=True,
        ))
        if declaration_signature is not None:
            elements.append(declaration_signature)
        elements.append(_front_paragraph(
            declaration['author'], align='right', first_line=0,
            before=(
                0 if declaration_signature is not None
                else int(declaration.get('signature_space_lines', 0)) * 240
            ),
            after=0,
            keep_next=True,
        ))
        elements.append(_front_paragraph(
            declaration['nim'], align='right', first_line=0, after=0,
        ))
        if approval_scan is not None:
            elements.append(approval_scan)

    elements.append(_front_heading(abstract_id['heading'], toc=True))
    elements.append(_front_paragraph(
        abstract_id['body'], line=240, first_line=0, after=120,
    ))
    elements.append(_front_keywords(
        abstract_id['keywords_label'], abstract_id['keywords'],
    ))

    elements.append(_front_heading(abstract_en['heading'], toc=True))
    elements.append(_front_paragraph(
        abstract_en['body'], line=240, first_line=0, after=120,
    ))
    elements.append(_front_keywords(
        abstract_en['keywords_label'], abstract_en['keywords'],
    ))

    elements.append(_front_heading(preface['heading'], toc=True))
    for paragraph in preface['opening']:
        elements.append(_front_paragraph(
            paragraph, first_line=567, left=0,
        ))
    for index, acknowledgement in enumerate(preface['acknowledgements'], start=1):
        elements.append(_front_paragraph(
            f'{index}. {acknowledgement}', first_line=0, left=0, after=60,
        ))
    for paragraph in preface['closing']:
        elements.append(_front_paragraph(
            paragraph, first_line=567, left=0, before=120,
        ))
    elements.append(_front_paragraph(
        preface['date'], align='right', first_line=0, left=0,
        before=240, after=0, keep_next=True,
    ))
    elements.append(_front_paragraph(
        preface['author'], align='right', first_line=0, left=0,
        after=0, keep_next=True,
    ))
    elements.append(_front_paragraph(
        preface['nim'], align='right', first_line=0, left=0, after=0,
    ))

    return elements


def _next_numeric_relationship_id(rels_root):
    numeric_ids = []
    for relationship in rels_root:
        rel_id = relationship.get('Id', '')
        if rel_id.startswith('rId') and rel_id[3:].isdigit():
            numeric_ids.append(int(rel_id[3:]))
    return f"rId{max(numeric_ids, default=0) + 1}"


def _signature_geometry(image_path, width_cm):
    """Return drawing size and transparent-edge crop for a signature image."""
    from PIL import Image

    with Image.open(image_path) as image:
        width_px, height_px = image.size
        if width_px <= 0 or height_px <= 0:
            raise ValueError(f'Invalid signature dimensions: {image.size!r}')
        if 'A' in image.getbands():
            bbox = image.getchannel('A').getbbox()
        else:
            bbox = (0, 0, width_px, height_px)

    if bbox is None:
        raise ValueError('Preface signature image is fully transparent.')

    padding = max(4, round(min(width_px, height_px) * 0.01))
    left = max(0, bbox[0] - padding)
    top = max(0, bbox[1] - padding)
    right = min(width_px, bbox[2] + padding)
    bottom = min(height_px, bbox[3] + padding)
    cropped_width = right - left
    cropped_height = bottom - top

    cx = round(float(width_cm) * 360000)
    cy = round(cx * cropped_height / cropped_width)
    crop = {
        'l': str(round(left * 100000 / width_px)),
        't': str(round(top * 100000 / height_px)),
        'r': str(round((width_px - right) * 100000 / width_px)),
        'b': str(round((height_px - bottom) * 100000 / height_px)),
    }
    return cx, cy, crop


def _image_geometry(image_path, width_cm):
    """Return an uncropped drawing size that preserves the source aspect ratio."""
    from PIL import Image

    with Image.open(image_path) as image:
        width_px, height_px = image.size
    if width_px <= 0 or height_px <= 0:
        raise ValueError(f'Invalid image dimensions: {(width_px, height_px)!r}')
    cx = round(float(width_cm) * 360000)
    cy = round(cx * height_px / width_px)
    return cx, cy, {'l': '0', 't': '0', 'r': '0', 'b': '0'}


def _front_image_drawing_paragraph(
        r_id, docpr_id, cx, cy, crop, alt_text, drawing_name, *,
        align='right', page_break_before=False, keep_next=True):
    paragraph = _front_paragraph(
        align=align, line=240, first_line=0, before=0, after=0,
        page_break_before=page_break_before, keep_next=keep_next,
    )
    run = lxml.etree.SubElement(paragraph, f'{{{W_NS}}}r')
    drawing = lxml.etree.SubElement(run, f'{{{W_NS}}}drawing')
    inline = lxml.etree.SubElement(
        drawing, f'{{{WP_NS}}}inline',
        distT='0', distB='0', distL='0', distR='0',
    )
    lxml.etree.SubElement(
        inline, f'{{{WP_NS}}}extent', cx=str(cx), cy=str(cy),
    )
    lxml.etree.SubElement(
        inline, f'{{{WP_NS}}}effectExtent', l='0', t='0', r='0', b='0',
    )
    lxml.etree.SubElement(
        inline, f'{{{WP_NS}}}docPr',
        id=str(docpr_id),
        name=drawing_name,
        descr=alt_text,
    )
    frame_properties = lxml.etree.SubElement(
        inline, f'{{{WP_NS}}}cNvGraphicFramePr',
    )
    lxml.etree.SubElement(
        frame_properties, f'{{{A_NS}}}graphicFrameLocks',
        noChangeAspect='1',
    )
    graphic = lxml.etree.SubElement(inline, f'{{{A_NS}}}graphic')
    graphic_data = lxml.etree.SubElement(
        graphic, f'{{{A_NS}}}graphicData',
        uri='http://schemas.openxmlformats.org/drawingml/2006/picture',
    )
    picture = lxml.etree.SubElement(graphic_data, f'{{{PIC_NS}}}pic')
    non_visual = lxml.etree.SubElement(picture, f'{{{PIC_NS}}}nvPicPr')
    lxml.etree.SubElement(
        non_visual, f'{{{PIC_NS}}}cNvPr',
        id=str(docpr_id),
        name=drawing_name,
        descr=alt_text,
    )
    lxml.etree.SubElement(non_visual, f'{{{PIC_NS}}}cNvPicPr')
    blip_fill = lxml.etree.SubElement(picture, f'{{{PIC_NS}}}blipFill')
    lxml.etree.SubElement(
        blip_fill, f'{{{A_NS}}}blip', {f'{{{R_NS}}}embed': r_id},
    )
    lxml.etree.SubElement(blip_fill, f'{{{A_NS}}}srcRect', **crop)
    stretch = lxml.etree.SubElement(blip_fill, f'{{{A_NS}}}stretch')
    lxml.etree.SubElement(stretch, f'{{{A_NS}}}fillRect')
    shape_properties = lxml.etree.SubElement(
        picture, f'{{{PIC_NS}}}spPr',
    )
    transform = lxml.etree.SubElement(
        shape_properties, f'{{{A_NS}}}xfrm',
    )
    lxml.etree.SubElement(transform, f'{{{A_NS}}}off', x='0', y='0')
    lxml.etree.SubElement(
        transform, f'{{{A_NS}}}ext', cx=str(cx), cy=str(cy),
    )
    geometry = lxml.etree.SubElement(
        shape_properties, f'{{{A_NS}}}prstGeom', prst='rect',
    )
    lxml.etree.SubElement(geometry, f'{{{A_NS}}}avLst')
    return paragraph


def _install_front_image(
        root, unpacked_dir, image_config, *, media_stem, drawing_name,
        crop_transparent=False, align='right', page_break_before=False,
        keep_next=True, docpr_id_offset=0):
    relative_image = image_config['image']
    repository_root = os.path.realpath(os.getcwd())
    source_path = os.path.realpath(os.path.join(repository_root, relative_image))
    if not source_path.startswith(repository_root + os.sep):
        raise ValueError('Front-matter image must stay inside the repository.')
    if not os.path.isfile(source_path):
        raise FileNotFoundError(f'Front-matter image not found: {relative_image}')

    extension = os.path.splitext(source_path)[1].lower()
    mime_by_extension = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
    }
    if extension not in mime_by_extension:
        raise ValueError(f'Unsupported front-matter image extension: {extension}')

    media_dir = os.path.join(unpacked_dir, 'word', 'media')
    os.makedirs(media_dir, exist_ok=True)
    media_name = f'{media_stem}{extension}'
    shutil.copy2(source_path, os.path.join(media_dir, media_name))

    parser = lxml.etree.XMLParser(remove_blank_text=False)
    rels_path = os.path.join(
        unpacked_dir, 'word', '_rels', 'document.xml.rels',
    )
    rels_tree = lxml.etree.parse(rels_path, parser)
    rels_root = rels_tree.getroot()
    relationship = next(
        (
            item for item in rels_root
            if item.get('Type') == IMAGE_REL_TYPE
            and item.get('Target') == f'media/{media_name}'
        ),
        None,
    )
    if relationship is None:
        relationship = lxml.etree.SubElement(
            rels_root, f'{{{PACKAGE_REL_NS}}}Relationship',
            Id=_next_numeric_relationship_id(rels_root),
            Type=IMAGE_REL_TYPE,
            Target=f'media/{media_name}',
        )
    rels_tree.write(
        rels_path, encoding='utf-8', xml_declaration=True, standalone=True,
    )

    content_types_path = os.path.join(unpacked_dir, '[Content_Types].xml')
    content_types_tree = lxml.etree.parse(content_types_path, parser)
    content_types_root = content_types_tree.getroot()
    existing_extensions = {
        (item.get('Extension') or '').lower()
        for item in content_types_root.findall(
            f'{{{CONTENT_TYPES_NS}}}Default'
        )
    }
    normalized_extension = extension.lstrip('.')
    if normalized_extension not in existing_extensions:
        lxml.etree.SubElement(
            content_types_root,
            f'{{{CONTENT_TYPES_NS}}}Default',
            Extension=normalized_extension,
            ContentType=mime_by_extension[extension],
        )
        content_types_tree.write(
            content_types_path,
            encoding='utf-8',
            xml_declaration=True,
            standalone=True,
        )

    docpr_ids = []
    for element in root.findall(f'.//{{{WP_NS}}}docPr'):
        try:
            docpr_ids.append(int(element.get('id', '0')))
        except ValueError:
            continue
    width_cm = float(image_config.get('width_cm', 4.0))
    if not 1.5 <= width_cm <= 15.0:
        raise ValueError('Front-matter image width_cm must be between 1.5 and 15.0.')
    if crop_transparent:
        cx, cy, crop = _signature_geometry(source_path, width_cm)
    else:
        cx, cy, crop = _image_geometry(source_path, width_cm)
    return _front_image_drawing_paragraph(
        relationship.get('Id'),
        max(docpr_ids, default=0) + 1 + int(docpr_id_offset),
        cx,
        cy,
        crop,
        image_config.get('alt_text', 'Gambar front matter'),
        drawing_name,
        align=align,
        page_break_before=page_break_before,
        keep_next=keep_next,
    )


def _cleanup_removed_media(unpacked_dir, removed_relationship_ids, root):
    if not removed_relationship_ids:
        return
    live_ids = set(root.xpath('//a:blip/@r:embed', namespaces={
        'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
        'r': R_NS,
    }))
    orphan_ids = set(removed_relationship_ids) - live_ids
    if not orphan_ids:
        return
    rels_path = os.path.join(unpacked_dir, 'word', '_rels', 'document.xml.rels')
    if not os.path.exists(rels_path):
        return
    rels_tree = lxml.etree.parse(rels_path)
    rels_root = rels_tree.getroot()
    removed_targets = []
    for rel in list(rels_root):
        rel_id = rel.get('Id')
        if rel_id in orphan_ids:
            target = rel.get('Target', '')
            if target.startswith('media/'):
                removed_targets.append(target)
            rels_root.remove(rel)
    rels_tree.write(
        rels_path, encoding='utf-8', xml_declaration=True, standalone=True,
    )
    for target in removed_targets:
        media_path = os.path.join(unpacked_dir, 'word', *target.split('/'))
        if os.path.exists(media_path):
            os.remove(media_path)
            print(f'  Removed obsolete front-matter media: {target}')


def inject_front_matter(
        tree, config, unpacked_dir='unpacked_ta', *, profile='iman'):
    root = tree.getroot()
    body = root.find(f'{{{W_NS}}}body')
    if body is None:
        raise ValueError('document.xml does not contain w:body')
    children = list(body)
    toc_idx = -1
    for index, child in enumerate(children):
        if child.tag == f'{{{W_NS}}}sdt' and 'DAFTAR ISI' in _paragraph_text(child).upper():
            toc_idx = index
            break
    if toc_idx < 0:
        raise ValueError('Could not locate the Daftar Isi content control')

    insertion_idx = toc_idx
    while insertion_idx > 0 and children[insertion_idx - 1].tag in {
        f'{{{W_NS}}}bookmarkStart', f'{{{W_NS}}}bookmarkEnd',
    }:
        insertion_idx -= 1

    cover_year_idx = -1
    for index, child in enumerate(children[:insertion_idx]):
        if child.tag == f'{{{W_NS}}}p' and re.fullmatch(r'20\d{2}', _paragraph_text(child)):
            cover_year_idx = index
    if cover_year_idx < 0:
        raise ValueError('Could not locate the cover year paragraph')

    nonempty_cover = [
        child for child in children[:cover_year_idx]
        if child.tag == f'{{{W_NS}}}p' and _paragraph_text(child)
    ]
    if len(nonempty_cover) < 2:
        raise ValueError('Could not locate the cover title paragraphs')
    _replace_paragraph_text(
        nonempty_cover[0], config['cover']['title'], bold=True, size=28,
    )
    _replace_paragraph_text(nonempty_cover[1], '', bold=True, size=28)

    cover_nim_paragraphs = [
        child for child in children[:cover_year_idx]
        if child.tag == f'{{{W_NS}}}p'
        and re.fullmatch(r'\d{8,12}', _paragraph_text(child))
    ]
    if not cover_nim_paragraphs:
        raise ValueError('Could not locate the cover NIM paragraph')
    cover_nim_paragraph = cover_nim_paragraphs[-1]
    cover_nim_idx = children.index(cover_nim_paragraph)
    cover_author_paragraph = next(
        (
            child for child in reversed(children[:cover_nim_idx])
            if child.tag == f'{{{W_NS}}}p' and _paragraph_text(child)
        ),
        None,
    )
    if cover_author_paragraph is None:
        raise ValueError('Could not locate the cover author paragraph')
    _replace_paragraph_text(
        cover_author_paragraph, config['cover']['author'], bold=True, size=24,
    )
    _replace_paragraph_text(
        cover_nim_paragraph, config['cover']['nim'], bold=True, size=24,
    )
    _replace_paragraph_text(
        children[cover_year_idx], config['cover']['year'], bold=True, size=28,
    )

    removed_relationship_ids = []
    for child in children[cover_year_idx + 1:insertion_idx]:
        removed_relationship_ids.extend(child.xpath(
            './/a:blip/@r:embed', namespaces={
                'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                'r': R_NS,
            },
        ))
        body.remove(child)

    children = list(body)
    toc_idx = next(
        index for index, child in enumerate(children)
        if child.tag == f'{{{W_NS}}}sdt' and 'DAFTAR ISI' in _paragraph_text(child).upper()
    )
    insertion_idx = toc_idx
    while insertion_idx > 0 and children[insertion_idx - 1].tag in {
        f'{{{W_NS}}}bookmarkStart', f'{{{W_NS}}}bookmarkEnd',
    }:
        insertion_idx -= 1
    declaration_signature = None
    approval_scan = None
    front_matter_scans = {}
    if 'approval_page' in config:
        scan_blocks = (
            ('approval', config['approval_page'], 0),
            ('authenticity', config['authenticity_statement'], 1),
            ('publication', config['publication_permission'], 2),
        )
        for key, block, docpr_offset in scan_blocks:
            scan_config = block.get('scan')
            if not scan_config:
                continue
            front_matter_scans[key] = _install_front_image(
                root,
                unpacked_dir,
                scan_config,
                media_stem=f'front-matter-{key}-{profile}',
                drawing_name=f'FRONT_MATTER_SCAN:{profile}:{key}',
                align='center',
                page_break_before=False,
                keep_next=False,
                docpr_id_offset=docpr_offset,
            )
        if front_matter_scans:
            expected_scans = {'approval', 'authenticity', 'publication'}
            if set(front_matter_scans) != expected_scans:
                missing = sorted(expected_scans - set(front_matter_scans))
                raise ValueError(
                    f'Incomplete signed front-matter scan set: {missing!r}'
                )
    else:
        signature_config = config.get('declaration', {}).get('signature')
        if signature_config:
            declaration_signature = _install_front_image(
                root,
                unpacked_dir,
                signature_config,
                media_stem=f'declaration-signature-{profile}',
                drawing_name=f'DECLARATION_SIGNATURE:{profile}',
                crop_transparent=True,
            )
        approval_config = config.get('approval_scan')
        if approval_config:
            approval_scan = _install_front_image(
                root,
                unpacked_dir,
                approval_config,
                media_stem=f'approval-scan-{profile}',
                drawing_name=f'APPROVAL_SCAN:{profile}',
                align='center',
                page_break_before=True,
                keep_next=False,
                docpr_id_offset=1,
            )
    for offset, element in enumerate(_build_front_matter(
            config,
            declaration_signature=declaration_signature,
            approval_scan=approval_scan,
            front_matter_scans=front_matter_scans,
    )):
        body.insert(insertion_idx + offset, element)

    _cleanup_removed_media(unpacked_dir, removed_relationship_ids, root)
    if front_matter_scans:
        print(
            'Inserted project title page, signed approval/authenticity/'
            'publication scans, abstracts, and preface.'
        )
    elif 'approval_page' in config:
        print(
            'Inserted project title page, editable approval page, authenticity '
            'statement, publication permission, abstracts, and preface.'
        )
    else:
        print(
            'Inserted project title page, authenticity statement, declaration, '
            'approval page, abstracts, and preface.'
        )

new_erd_markdown = """Penjelasan mengenai struktur tabel, kolom, tipe data, serta aturan relasi antartabel dijabarkan sebagai berikut:

1. Tabel `gedung`
   Entitas ini menyimpan data administratif dan fisik dari seluruh bangunan/gedung yang ada di lingkungan UPNVJ Kampus Pondok Labu.
   a. Atribut tabel terdiri atas:
      1) `id`: Tipe `SERIAL` bertindak sebagai Primary Key.
      2) `nama_gedung`: Tipe `VARCHAR(255)`, bernilai unik (*unique*) dan tidak boleh kosong (*not null*).
      3) `deskripsi_gedung`: Tipe `TEXT` untuk penjelasan detail gedung.
      4) `lokasi`: Tipe `TEXT` untuk deskripsi alamat atau letak koordinat fisik.
      5) `jumlah_lantai`: Tipe `INT` dengan nilai default 1.
      6) `foto_url`: Tipe `VARCHAR(255)` untuk menyimpan tautan gambar gedung.
      7) `unity_object_name`: Tipe `TEXT` bersifat unik, berfungsi sebagai jembatan penamaan GameObject pada scene Unity.
   b. Relasi tabel:
      1) Berelasi One-to-Many dengan tabel `fasilitas` melalui foreign key `id_gedung`.
      2) Berelasi One-to-One / Many-to-One dengan tabel `fakultas` melalui foreign key `id_gedung_utama`.

2. Tabel `fasilitas`
   Entitas ini menyimpan data fasilitas spesifik yang berada di dalam suatu gedung (misalnya ruang kelas, laboratorium, perpustakaan, toilet, dll.).
   a. Atribut tabel terdiri atas:
      1) `id`: Tipe `SERIAL` bertindak sebagai Primary Key.
      2) `nama_fasilitas`: Tipe `VARCHAR(255)` untuk nama fasilitas.
      3) `deskripsi_fasilitas`: Tipe `TEXT` untuk penjelasan detail fasilitas.
      4) `tipe_fasilitas`: Tipe `VARCHAR(100)` untuk klasifikasi jenis fasilitas.
      5) `color`: Tipe `VARCHAR(50)` dengan default 'gray' untuk penanda warna visual pada frontend React.
      6) `lantai`: Tipe `INT` dengan default 1 untuk menunjukkan posisi lantai fasilitas.
      7) `foto_url`: Tipe `TEXT` untuk menyimpan tautan gambar fasilitas.
      8) `id_gedung`: Tipe `INT` sebagai Foreign Key yang merujuk ke tabel `gedung` (ON DELETE SET NULL).
      9) `unity_object_name`: Tipe `TEXT` bersifat unik, berfungsi sebagai jembatan penamaan GameObject fasilitas pada scene Unity.
   b. Relasi tabel: Merupakan tabel anak yang bergantung pada tabel `gedung`.

3. Tabel `fakultas`
   Entitas ini menampung data profil fakultas yang berada di lingkungan universitas.
   a. Atribut tabel terdiri atas:
      1) `id`: Tipe `SERIAL` bertindak sebagai Primary Key.
      2) `nama_fakultas`: Tipe `VARCHAR(255)` bersifat unik dan tidak boleh kosong.
      3) `deskripsi_fakultas`: Tipe `TEXT` untuk rincian profil fakultas.
      4) `email`: Tipe `VARCHAR(255)` untuk kontak surat elektronik fakultas.
      5) `website`: Tipe `VARCHAR(255)` untuk alamat web resmi fakultas.
      6) `id_gedung_utama`: Tipe `INT` sebagai Foreign Key yang merujuk ke tabel `gedung` (ON DELETE SET NULL).
   b. Relasi tabel:
      1) Berelasi One-to-Many dengan tabel `program_studi` melalui foreign key `id_fakultas` pada tabel prodi.
      2) Berelasi Many-to-One dengan tabel `gedung` untuk menentukan gedung administrasi utama.

4. Tabel `program_studi`
   Entitas ini menyimpan data program studi yang dinaungi oleh masing-masing fakultas.
   a. Atribut tabel terdiri atas:
      1) `id`: Tipe `SERIAL` bertindak sebagai Primary Key.
      2) `nama_prodi`: Tipe `VARCHAR(255)` untuk nama program studi.
      3) `jenjang`: Tipe `VARCHAR(10)` untuk tingkat pendidikan (D3/S1/S2/S3).
      4) `id_fakultas`: Tipe `INT` sebagai Foreign Key yang merujuk ke tabel `fakultas` (ON DELETE CASCADE).
      5) `akreditasi`: Tipe `VARCHAR(50)` untuk peringkat akreditasi program studi.
   b. Relasi tabel: Bergantung penuh pada tabel `fakultas` melalui foreign key `id_fakultas`. Terdapat batasan unik gabungan (*composite unique key*) pada kolom `nama_prodi`, `jenjang`, dan `id_fakultas`.

5. Tabel `admin_users`
   Entitas ini menyimpan informasi akun administrator yang memiliki hak akses untuk mengelola data konten melalui Admin Panel.
   a. Atribut tabel terdiri atas:
      1) `id`: Tipe `SERIAL` bertindak sebagai Primary Key.
      2) `username`: Tipe `VARCHAR(100)` bersifat unik dan tidak boleh kosong.
      3) `password_hash`: Tipe `TEXT` untuk menyimpan hash kata sandi yang terenkripsi.
      4) `nama_lengkap`: Tipe `VARCHAR(255)` untuk nama lengkap administrator.
      5) `role`: Tipe `VARCHAR(50)` dengan default 'admin'.
      6) `created_at`: Tipe `TIMESTAMP` dengan default waktu saat data dibuat.
   b. Relasi tabel: Tabel independen untuk kebutuhan autentikasi dan otorisasi.

6. Tabel `audit_logs`
   Entitas ini digunakan sebagai pencatat riwayat (audit trail) otomatis terhadap setiap operasi manipulasi data (CRUD) yang dilakukan oleh administrator.
   a. Atribut tabel terdiri atas:
      1) `id`: Tipe `BIGSERIAL` bertindak sebagai Primary Key.
      2) `actor_id`: Tipe `UUID` untuk menyimpan ID admin yang melakukan aksi.
      3) `actor_email`: Tipe `TEXT` untuk menyimpan email administrator.
      4) `action`: Tipe `TEXT` untuk jenis operasi (INSERT/UPDATE/DELETE).
      5) `table_name`: Tipe `TEXT` untuk nama tabel yang mengalami mutasi.
      6) `record_id`: Tipe `TEXT` untuk ID rekaman data yang diubah.
      7) `old_data`: Tipe `JSONB` untuk menyimpan kondisi data lama sebelum diubah (bernilai null saat INSERT).
      8) `new_data`: Tipe `JSONB` untuk menyimpan kondisi data baru sesudah diubah (bernilai null saat DELETE).
      9) `created_at`: Tipe `TIMESTAMP` dengan default waktu mutasi tercatat.
   b. Relasi tabel: Mencatat riwayat mutasi dari tabel-tabel utama secara transparan melalui trigger basis data.

7. Tabel `web_analytics_log`
   Entitas pendukung ini bersifat legacy dan berfungsi untuk mencatat log kunjungan pengguna ke halaman web secara mandiri sebelum digantikan oleh integrasi Umami Analytics.
   a. Atribut tabel terdiri atas:
      1) `id`: Tipe `SERIAL` bertindak sebagai Primary Key.
      2) `visitor_hash`: Tipe `VARCHAR(255)` untuk sidik jari unik browser pengunjung.
      3) `page_path`: Tipe `VARCHAR(255)` untuk menyimpan path halaman yang diakses.
      4) `device_type`: Tipe `VARCHAR(100)` untuk jenis perangkat yang digunakan.
      5) `visited_at`: Tipe `TIMESTAMP` dengan default waktu kunjungan.
   b. Relasi tabel: Tabel mandiri yang mengumpulkan data analitik kunjungan."""

def parse_markdown_string(md_text):
    items = []
    lines = md_text.split('\n')
    list_item_pattern = re.compile(r'^(\s*)([0-9a-zA-Z]+[\.\)])\s+(.*)$')
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        list_match = list_item_pattern.match(line)
        if list_match:
            indent_spaces = len(list_match.group(1))
            marker = list_match.group(2)
            text_content = list_match.group(3)
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
        else:
            items.append({
                'type': 'paragraph',
                'text': stripped
            })
    return items

def main():
    xml_path = "unpacked_ta/word/document.xml"
    if not os.path.exists(xml_path):
        print(f"Error: {xml_path} does not exist.")
        return
        
    print(f"Patching {xml_path}...")
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    namespaces = {'w': ns_uri}
    
    parser = lxml.etree.XMLParser(remove_blank_text=False)
    tree = lxml.etree.parse(xml_path, parser)
    root = tree.getroot()
    body = root.find('w:body', namespaces)
    
    # 1. Search and replace simple strings in w:t nodes
    wt_replaced = 0
    for wt in root.xpath('//w:t', namespaces=namespaces):
        text = wt.text
        if not text:
            continue
            
        new_text = text
        # Replace outdated figure titles
        if "Modal Tambah Dosen" in new_text:
            new_text = new_text.replace("Modal Tambah Dosen", "Modal Tambah Data Gedung")
        if "Modal Update Dosen" in new_text:
            new_text = new_text.replace("Modal Update Dosen", "Modal Update Data Gedung")
        if "Modal Konfirmasi Hapus Dosen" in new_text:
            new_text = new_text.replace("Modal Konfirmasi Hapus Dosen", "Modal Konfirmasi Hapus Data Gedung")
            
        # Replace CRUD text
        if "seperti data dosen, fasilitas, dan aset" in new_text:
            new_text = new_text.replace("seperti data dosen, fasilitas, dan aset", "seperti data gedung, fasilitas, fakultas, dan program studi")
        if "dosen, mahasiswa, fasilitas, dan gedung" in new_text:
            new_text = new_text.replace("dosen, mahasiswa, fasilitas, dan gedung", "fasilitas, gedung, fakultas, dan program studi")
            
        # General replacements for database and schema descriptions
        if "Sistem harus dapat menyajikan data statistik kampus (dosen, mahasiswa)." in new_text:
            new_text = new_text.replace("Sistem harus dapat menyajikan data statistik kampus (dosen, mahasiswa).", "Sistem harus dapat menyajikan data statistik lalu lintas website.")
            
        if "Sistem harus menyediakan fungsionalitas CRUD (Create, Read, Update, Delete) untuk mengelola semua data konten dinamis (Dosen, Mahasiswa, Fakultas, Aset, Fasilitas, Akreditasi, dll.)." in new_text:
            new_text = new_text.replace("Sistem harus menyediakan fungsionalitas CRUD (Create, Read, Update, Delete) untuk mengelola semua data konten dinamis (Dosen, Mahasiswa, Fakultas, Aset, Fasilitas, Akreditasi, dll.).", "Sistem harus menyediakan fungsionalitas CRUD (Create, Read, Update, Delete) untuk mengelola semua data konten dinamis (Gedung, Fasilitas, Fakultas, dan Program Studi).")
            
        if "Informasi kampus seperti fasilitas, dosen, dan statistik disajikan secara dinamis melalui API." in new_text:
            new_text = new_text.replace("Informasi kampus seperti fasilitas, dosen, dan statistik disajikan secara dinamis melalui API.", "Informasi kampus seperti fasilitas, gedung, dan statistik disajikan secara dinamis melalui API.")
            
        if "Sistem menggunakan database PostgreSQL untuk menyimpan data terstruktur seperti fakultas, program studi, dosen, mahasiswa, fasilitas, dan gedung." in new_text:
            new_text = new_text.replace("Sistem menggunakan database PostgreSQL untuk menyimpan data terstruktur seperti fakultas, program studi, dosen, mahasiswa, fasilitas, dan gedung.", "Sistem menggunakan database PostgreSQL untuk menyimpan data terstruktur seperti fakultas, program studi, fasilitas, gedung, dan audit logs.")
            
        if "Struktur data akademik dibangun secara hierarkis, dimulai dari tabel fakultas yang memiliki relasi one-to-many dengan tabel program_studi. Selanjutnya, tabel program_studi menjadi entitas penghubung utama yang memiliki relasi one-to-many dengan tabel dosen dan mahasiswa, sehingga setiap data dosen dan mahasiswa terasosiasi secara langsung dengan satu program studi tertentu. Relasi antara program_studi dan akreditasi bersifat many-to-one, yang memungkinkan satu status akreditasi digunakan oleh lebih dari satu program studi sesuai dengan kondisi aktual institusi pendidikan." in new_text:
            new_text = new_text.replace("Struktur data akademik dibangun secara hierarkis, dimulai dari tabel fakultas yang memiliki relasi one-to-many dengan tabel program_studi. Selanjutnya, tabel program_studi menjadi entitas penghubung utama yang memiliki relasi one-to-many dengan tabel dosen dan mahasiswa, sehingga setiap data dosen and mahasiswa terasosiasi secara langsung dengan satu program studi tertentu. Relasi antara program_studi dan akreditasi bersifat many-to-one, yang memungkinkan satu status akreditasi digunakan oleh lebih dari satu program studi sesuai dengan kondisi aktual institusi pendidikan.", "Struktur data akademik dibangun secara hierarkis, dimulai dari tabel gedung yang memiliki relasi one-to-many dengan tabel fasilitas. Selanjutnya, tabel gedung berelasi dengan tabel fakultas, dan tabel fakultas memiliki relasi one-to-many dengan tabel program_studi (akreditasi). Hal ini menghubungkan data program studi dan fakultas dengan representasi fisik gedung secara langsung.")
            
        if "Aktor 'User' memiliki akses read-only untuk melihat berbagai data (Dosen, Mahasiswa, Akreditasi, Fasilitas) dan 'Lihat Denah Virtual'." in new_text:
            new_text = new_text.replace("Aktor 'User' memiliki akses read-only untuk melihat berbagai data (Dosen, Mahasiswa, Akreditasi, Fasilitas) dan 'Lihat Denah Virtual'.", "Aktor 'User' memiliki akses read-only untuk melihat berbagai data (Akreditasi, Fasilitas, Gedung, Statistik lalu lintas) dan 'Lihat Denah Virtual'.")

        # Replace Dosen test steps with Gedung test steps
        if "Di halaman utama admin, klik tombol \"Tambah Dosen\"." in new_text:
            new_text = new_text.replace("Di halaman utama admin, klik tombol \"Tambah Dosen\".", "Di halaman utama admin, klik tombol \"Tambah Data Gedung\".")
        if "Isi form pada modal \"Tambah Dosen\"." in new_text:
            new_text = new_text.replace("Isi form pada modal \"Tambah Dosen\".", "Isi form pada modal \"Tambah Data Gedung\".")
        if "tabel data dosen di halaman utama otomatis diperbarui" in new_text:
            new_text = new_text.replace("tabel data dosen di halaman utama otomatis diperbarui", "tabel data gedung di halaman utama otomatis diperbarui")
        if "menampilkan data dosen yang baru saja ditambahkan" in new_text:
            new_text = new_text.replace("menampilkan data dosen yang baru saja ditambahkan", "menampilkan data gedung yang baru saja ditambahkan")
        if "Di tabel data dosen, klik ikon \"Edit\"" in new_text:
            new_text = new_text.replace("Di tabel data dosen, klik ikon \"Edit\"", "Di tabel data gedung, klik ikon \"Edit\"")
        if "Modal \"Edit Dosen\" muncul" in new_text:
            new_text = new_text.replace("Modal \"Edit Dosen\" muncul", "Modal \"Edit Gedung\" muncul")
        if "data email pada tabel dosen tersebut" in new_text:
            new_text = new_text.replace("data email pada tabel dosen tersebut", "data lokasi pada tabel gedung tersebut")
        if "Di tabel data dosen, klik ikon \"Hapus\"" in new_text:
            new_text = new_text.replace("Di tabel data dosen, klik ikon \"Hapus\"", "Di tabel data gedung, klik ikon \"Hapus\"")
        if "baris data dosen tersebut hilang dari tabel" in new_text:
            new_text = new_text.replace("baris data dosen tersebut hilang dari tabel", "baris data gedung tersebut hilang dari tabel")

        # Replace Chart interaction with Asset Card interaction
        if "Klik pada salah satu bar chart (misal: bar \"Fakultas Teknik\" di chart Dosen)." in new_text:
            new_text = new_text.replace("Klik pada salah satu bar chart (misal: bar \"Fakultas Teknik\" di chart Dosen).", "Klik pada salah satu kartu aset (misal: kartu \"Laboratorium\").")
        if "Panel informasi di sisi kanan atau area lain berubah (me-render ulang state) untuk menampilkan detail data \"Fakultas Teknik\"." in new_text:
            new_text = new_text.replace("Panel informasi di sisi kanan atau area lain berubah (me-render ulang state) untuk menampilkan detail data \"Fakultas Teknik\".", "Modal daftar fasilitas terbuka untuk menampilkan daftar laboratorium.")

        # Replace drill-down tests (BB-09 and BB-10)
        if "Klik salah satu bar grafik dosen" in new_text:
            new_text = new_text.replace("Klik salah satu bar grafik dosen", "Buka halaman utama public dashboard")
        if "Detail data dosen fakultas tampil" in new_text:
            new_text = new_text.replace("Detail data dosen fakultas tampil", "Grafik tren traffic harian dan KPI total pengunjung tampil")
        if "Klik salah satu bar grafik mahasiswa" in new_text:
            new_text = new_text.replace("Klik salah satu bar grafik mahasiswa", "Klik tombol toggle bahasa (ID/EN)")
        if "Detail data mahasiswa fakultas tampil" in new_text:
            new_text = new_text.replace("Detail data mahasiswa fakultas tampil", "Seluruh teks konten berubah ke bahasa yang dipilih")
        
        # Replace SUS procedures & UAT descriptions
        if "Tolong tambahkan data dosen baru bernama X" in new_text:
            new_text = new_text.replace("Tolong tambahkan data dosen baru bernama X", "Tolong tambahkan data gedung baru bernama X")
        if "menampilkan detail dosen berdasarkan fakultas" in new_text:
            new_text = new_text.replace("menampilkan detail dosen berdasarkan fakultas", "menampilkan detail fasilitas berdasarkan kategori")
        if "POST /api/dosen" in new_text:
            new_text = new_text.replace("POST /api/dosen", "POST /api/buildings")
            
        if new_text != text:
            wt.text = new_text
            wt_replaced += 1
            
    print(f"Replaced text in {wt_replaced} w:t nodes.")
    
    # 1.5. Remove the three outdated mockup paragraphs (dosen/mahasiswa charts) from the template's XML
    mockup_start_p = None
    mockup_end_p = None
    
    for p in body.findall('w:p', namespaces):
        p_text = "".join([t.text for t in p.iter(f'{{{ns_uri}}}t') if t.text])
        if "Distribusi sumber daya akademik divisualisasikan melalui grafik batang" in p_text:
            mockup_start_p = p
        elif "Gambar 2.21 Detail Data Mahasiswa" in p_text:
            mockup_end_p = p
            
    if mockup_start_p is not None and mockup_end_p is not None:
        children_list = list(body)
        start_idx_mockup = children_list.index(mockup_start_p)
        end_idx_mockup = children_list.index(mockup_end_p)
        
        print(f"Removing mockups from index {start_idx_mockup} to {end_idx_mockup}")
        # Remove paragraphs from start_idx_mockup to end_idx_mockup inclusive
        for idx in range(end_idx_mockup, start_idx_mockup - 1, -1):
            body.remove(children_list[idx])
        print("Outdated mockup paragraphs removed.")
    else:
        print("Warning: Could not locate outdated mockup paragraphs for removal.")

    # 1.6. Replace the User Interface section narrative paragraphs directly in XML
    ui_replacements = {
        "Berikut adalah rancangan antarmuka pengguna": 
            "Berikut adalah rancangan antarmuka pengguna (user interface) dalam bentuk mockup untuk komponen frontend utama yang akan dikembangkan. Halaman antarmuka dalam sistem ini dibagi menjadi dua bagian utama, yaitu Antarmuka Dashboard Admin untuk kebutuhan manajemen data oleh administrator dan Antarmuka Public Dashboard untuk akses informasi sarana prasarana oleh pengguna umum.",
        
        "Proses awal interaksi administrator dengan sistem diawali melalui mekanisme autentikasi": 
            "Proses awal interaksi administrator dengan sistem manajemen diawali melalui mekanisme autentikasi pada Halaman Login Admin. Halaman ini menyediakan formulir input kredensial berupa nama pengguna (username) dan kata sandi (password) yang wajib diisi oleh administrator sebelum dapat mengakses dashboard administratif, sebagaimana ditunjukkan pada Gambar 2.17. Mekanisme autentikasi ini berfungsi untuk membatasi akses administratif hanya kepada pengguna yang berwenang, sehingga integritas data operasional tetap terjaga.",
        
        "Setelah autentikasi berhasil dilakukan, administrator diarahkan menuju halaman utama dashboard": 
            "Setelah proses autentikasi berhasil, administrator akan diarahkan menuju Halaman Dashboard Admin yang bertindak sebagai pusat kendali manajemen data kampus. Halaman ini menampilkan ringkasan data statistik operasional dalam bentuk widget analitik serta tabel data terperinci yang mendukung aktivitas pemantauan dan pengelolaan sarana prasarana, sebagaimana divisualisasikan pada Gambar 2.18. Tombol aksi yang tersedia pada tabel ini memungkinkan administrator untuk mengelola data secara dinamis.",
        
        "Interaksi pengelolaan data pada sistem ini dirancang menggunakan pendekatan modal-based form": 
            "Interaksi pengelolaan data pada sistem ini dirancang menggunakan pendekatan formulir berbasis modal (modal-based form) untuk menjaga fokus administrator tanpa harus berpindah halaman. Ketika administrator menambahkan data gedung baru, sistem menampilkan modal popup formulir input sebagaimana ditunjukkan pada Gambar 2.19. Pola interaksi serupa diterapkan ketika administrator memperbarui data gedung, di mana data lama akan otomatis dimuat ke dalam kolom input modal, sebagaimana divisualisasikan pada Gambar 2.20.",
        
        "Untuk mencegah terjadinya penghapusan data secara tidak disengaja": 
            "Untuk mencegah terjadinya penghapusan data secara tidak sengaja, sistem menerapkan mekanisme konfirmasi sebelum eksekusi aksi hapus dilakukan. Mekanisme ini direalisasikan melalui modal konfirmasi yang meminta persetujuan eksplisit dari administrator, sebagaimana diperlihatkan pada Gambar 2.21. Aksi penghapusan data pada database hanya akan dijalankan apabila administrator menekan tombol konfirmasi hapus secara sadar.",
        
        "Pemantauan lalu lintas penggunaan sistem pada sisi administratif dirancang": 
            "Pemantauan lalu lintas penggunaan sistem pada sisi administratif dirancang untuk menyajikan analisis kunjungan secara mendalam. Modul traffic website pada Dashboard Admin menyajikan informasi agregat mengenai aktivitas penggunaan internal, mencakup total kunjungan, frekuensi akses halaman, serta detail sistem operasi dan peramban yang digunakan untuk mengakses sistem, sebagaimana ditunjukkan pada Gambar 2.22.",
        
        "Sedikit berbeda dengan modul public traffic": 
            "Metrik pemantauan lalu lintas pada Dashboard Admin ini memiliki cakupan yang lebih lengkap dibandingkan dengan Dashboard Publik. Klasifikasi tipe perangkat yang digunakan oleh pengguna (seperti desktop, tablet, dan mobile) ditampilkan secara detail untuk memberikan gambaran komprehensif mengenai pola kerja administrator dalam mengelola konten sistem.",
        
        "Keberadaan detail perangkat pada admin traffic": 
            "Analisis perangkat pada halaman admin traffic ini memiliki peran penting untuk mengevaluasi aspek keamanan dan kegunaan (usability) sistem. Dengan mengetahui peramban dan sistem operasi yang digunakan oleh administrator, pengelola sistem dapat mengoptimalkan tata letak antarmuka serta mengidentifikasi jika terjadi akses tidak wajar dari perangkat yang tidak dikenal.",
        
        "Bagian awal antarmuka public dashboard dirancang sebagai hero section": 
            "Bagian awal antarmuka public dashboard dirancang sebagai Hero Section yang menjadi titik orientasi visual utama bagi pengunjung. Area ini memuat identitas sistem, navigasi utama, tombol akses ke login admin, serta tombol toggle bahasa (Bahasa Indonesia dan English) untuk memfasilitasi aksesibilitas bagi pengguna internasional, sebagaimana diperlihatkan pada Gambar 2.23. Penyediaan fitur multi-bahasa ini bertujuan untuk mempermudah pengguna asing dalam memahami konten navigasi.",
        
        "Pemantauan aktivitas pengguna pada public dashboard dirancang": 
            "Metrik pemantauan lalu lintas pada halaman publik dirancang untuk menyajikan statistik kunjungan dasar secara transparan. Modul ini menampilkan visualisasi grafik garis tren kunjungan harian selama 14 hari terakhir serta empat kartu indikator kinerja utama (Key Performance Indicator/KPI) yang mencakup total pengunjung, total tampilan halaman, rata-rata pengunjung harian, dan rata-rata tampilan halaman, sebagaimana ditunjukkan pada Gambar 2.24.",
        
        "Informasi mengenai fasilitas dan aset kampus disajikan dengan tata letak berbasis kartu": 
            "Informasi mengenai sarana prasarana kampus disajikan dengan tata letak berbasis kartu (card-based layout) yang mengelompokkan data ke dalam 8 kategori utama aset dan fasilitas. Sistem juga dilengkapi dengan fitur pencarian gabungan (Search Overlay) di bagian atas untuk memudahkan penemuan nama gedung atau fasilitas secara langsung dari seluruh kategori yang tersedia, sebagaimana diperlihatkan pada Gambar 2.25.",
        
        "Ketika pengguna mengeklik salah satu kartu kategori": 
            "Ketika pengguna memilih salah satu kartu kategori sarana prasarana, sistem akan memicu jendela popup dinamis. Modal popup ini menyajikan daftar item terstruktur yang sesuai dengan kategori yang dipilih oleh pengguna tanpa memuat ulang halaman utama, sebagaimana ditunjukkan pada Gambar 2.26. Pola interaksi ini mendukung penelusuran informasi yang lebih terfokus.",
        
        "Ketika pengguna memilih salah satu kartu pada bagian fasilitas": 
            "Ketika pengguna memilih salah satu kartu kategori sarana prasarana, sistem akan memicu jendela popup dinamis. Modal popup ini menyajikan daftar item terstruktur yang sesuai dengan kategori yang dipilih oleh pengguna tanpa memuat ulang halaman utama, sebagaimana ditunjukkan pada Gambar 2.26. Pola interaksi ini mendukung penelusuran informasi yang lebih terfokus.",
        
        "Untuk fasilitas yang dikategorikan sebagai unggulan": 
            "Sistem menyediakan modal detail dengan struktur informasi berbeda yang disesuaikan secara otomatis berdasarkan jenis entitas yang dipilih oleh pengguna. Ketika pengguna mengeklik item bertipe gedung, modal detail menampilkan deskripsi gedung, foto fisik, lokasi kampus, serta daftar lengkap fasilitas yang ada di dalam gedung tersebut. Sementara itu, untuk item bertipe fasilitas, modal detail hanya menampilkan deskripsi spesifik dan lokasinya saja, sebagaimana ditunjukkan pada Gambar 2.27.",
        
        "Sebagai penutup halaman, sistem menyediakan bagian footer": 
            "Sebagai penutup halaman dan pusat navigasi pelengkap, sistem menyediakan Bagian Footer di area paling bawah halaman. Footer ini memuat tautan navigasi cepat, jam operasional layanan, informasi kontak institusi, serta widget peta interaktif Google Maps yang memvisualisasikan lokasi fisik Kampus Pondok Labu UPNVJ secara langsung, sebagaimana diperlihatkan pada Gambar 2.28. Keberadaan footer ini mempermudah pengguna dalam mengakses informasi kontak resmi serta menemukan rute lokasi fisik kampus.",
        
        "Perancangan antarmuka pengguna pada Admin Dashboard dan Public Dashboard tidak hanya berfokus pada aspek visual": 
            "Perancangan antarmuka pengguna pada Admin Dashboard dan Public Dashboard dirancang dengan mengutamakan aspek konsistensi elemen visual dan kemudahan penggunaan (usability). Desain antarmuka yang dinamis ini diharapkan dapat mempermudah pengguna dalam memperoleh informasi spasial secara mandiri. Rancangan antarmuka ini selanjutnya menjadi acuan dalam penyusunan skenario pengujian fungsional dan pengujian penerimaan pengguna pada tahap evaluasi sistem."
    }

    replaced_ui_count = 0
    for p in body.findall('w:p', namespaces):
        p_text = "".join([t.text for t in p.iter(f'{{{ns_uri}}}t') if t.text])
        for match_key, new_val in ui_replacements.items():
            if match_key in p_text:
                # Clear runs and insert new one
                pPr = p.find('w:pPr', namespaces)
                for child in list(p):
                    if child != pPr:
                        p.remove(child)
                r = lxml.etree.SubElement(p, f'{{{ns_uri}}}r')
                rPr = lxml.etree.SubElement(r, f'{{{ns_uri}}}rPr')
                lxml.etree.SubElement(rPr, f'{{{ns_uri}}}rFonts', {
                    f'{{{ns_uri}}}ascii': 'Times New Roman',
                    f'{{{ns_uri}}}hAnsi': 'Times New Roman'
                })
                lxml.etree.SubElement(rPr, f'{{{ns_uri}}}sz', {f'{{{ns_uri}}}val': '24'})
                lxml.etree.SubElement(rPr, f'{{{ns_uri}}}szCs', {f'{{{ns_uri}}}val': '24'})
                t = lxml.etree.SubElement(r, f'{{{ns_uri}}}t')
                t.text = new_val
                t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                replaced_ui_count += 1
                break

    print(f"Replaced {replaced_ui_count} UI narrative paragraphs directly in XML.")
    
    # 2. Replace the ERD section description paragraphs
    # Find start and end paragraph indices
    children = list(body)
    start_idx = -1
    end_idx = -1
    
    for idx, p in enumerate(children):
        if p.tag == f'{{{ns_uri}}}p':
            p_text = "".join([t.text for t in p.iter(f'{{{ns_uri}}}t') if t.text])
            if "Rancangan basis data pada sistem ini terdiri dari sembilan tabel utama" in p_text:
                start_idx = idx
            elif "2.3.4.2 Rancangan Fungsional Use Case Diagram" in p_text:
                end_idx = idx
                break
                
    if start_idx != -1 and end_idx != -1:
        print(f"Found ERD section to replace: from index {start_idx} to {end_idx}.")
        
        # Remove old paragraphs
        for idx in range(end_idx - 1, start_idx - 1, -1):
            body.remove(children[idx])
            print(f"Removed old paragraph at index {idx}.")
            
        # Parse new ERD markdown and build elements
        parsed_items = parse_markdown_string(new_erd_markdown)
        new_elements = []
        for item in parsed_items:
            p_elem = build_p_element(item)
            new_elements.append(p_elem)
            
        # Insert new elements at start_idx
        for elem in reversed(new_elements):
            body.insert(start_idx, elem)
            
        print(f"Inserted {len(new_elements)} new detailed ERD paragraphs.")
    else:
        print("Warning: Could not locate ERD section paragraphs in document.xml.")
        
    report_profile = os.environ.get('TA_REPORT_PROFILE', 'iman')
    front_matter_path = os.environ.get(
        'TA_FRONT_MATTER_PATH',
        os.path.join('content', 'roles', 'iman', 'front-matter.json'),
    )
    with open(front_matter_path, 'r', encoding='utf-8') as front_matter_file:
        front_matter_config = json.load(front_matter_file)
    inject_front_matter(tree, front_matter_config, profile=report_profile)

    tree.write(xml_path, encoding='utf-8', xml_declaration=True)
    print("SUCCESS: document.xml patched and saved.")
    
    # Copy new screenshots over the old mockup images in word/media
    media_dir = "unpacked_ta/word/media"
    replacements = {
        "login-page.png": "image18.png",
        "header+gedung-view.png": "image19.png",
        "modal-create-gedung.png": "image20.png",
        "modal-edit-gedung.png": "image21.png",
        "modal-konfirmasi-delete-gedung.png": "image22.png",
        "section-admin-traffic-view.png": "image23.png",
        "section-header+hero.png": "image24.png",
        "traffic-web-public.png": "image25.png",
        "section fasilitas-asset(dan gedung).png": "image26.png",
        "modal-fasilitas-aset.png": "image27.png",
        "modal-detail-gedung.png": "image28.png",
        "section-footer.png": "image32.png",
        "erd_schema.png": "image13.png"
    }
    
    if report_profile == 'iman':
        print("Replacing mockup image files with real screenshots...")
        for src_name, dest_name in replacements.items():
            src_path = os.path.join("dokumentasi", src_name)
            dest_path = os.path.join(media_dir, dest_name)
            if os.path.exists(src_path):
                shutil.copy2(src_path, dest_path)
                print(f"  Replaced {dest_name} with {src_name}")
            else:
                print(f"  Warning: Screenshot not found: {src_path}")

if __name__ == '__main__':
    main()
