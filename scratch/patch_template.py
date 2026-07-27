import os
import re
import shutil
import copy
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


def load_draft_front_matter():
    """Read identity/title metadata from the active draft for template front matter.

    The archive DOCX is a reusable layout template and may contain another
    author's cover page.  The draft is the source of truth for branch-specific
    identity metadata, so the patcher updates the cover without hard-coding a
    particular branch or NIM.
    """
    draft_path = os.environ.get('TA_DRAFT_PATH', 'Tugas_Akhir_Draft.md')
    if not os.path.isfile(draft_path):
        return {}

    with open(draft_path, 'r', encoding='utf-8') as handle:
        lines = handle.read().splitlines()

    headings = []
    second_heading_index = None
    heading_end = 0
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('# BAB '):
            heading_end = index
            break
        if stripped.startswith('# '):
            headings.append(stripped[2:].strip())
            if len(headings) == 2:
                second_heading_index = index
    if len(headings) < 2:
        return {}

    # The draft contract places name and NIM immediately after the two title
    # lines. Keep TBD markers intact when the student has not supplied a NIM.
    metadata_lines = [
        line.strip()
        for line in lines[second_heading_index + 1:heading_end]
        if line.strip()
    ]
    if len(metadata_lines) < 2:
        return {}

    year = next(
        (line for line in metadata_lines[2:] if re.fullmatch(r'(?:19|20)\d{2}', line)),
        None,
    )

    def extract_section(heading, keyword_label):
        marker = f'# {heading}'
        try:
            start = next(
                index for index, line in enumerate(lines[:heading_end])
                if line.strip() == marker
            )
        except StopIteration:
            return None, None
        section_lines = []
        for line in lines[start + 1:heading_end]:
            stripped = line.strip()
            if stripped.startswith('# '):
                break
            if stripped:
                section_lines.append(stripped)
        keyword_prefix = f'{keyword_label}:'
        keyword_line = next(
            (line for line in section_lines if line.lower().startswith(keyword_prefix.lower())),
            None,
        )
        abstract_lines = [line for line in section_lines if line != keyword_line]
        keyword_text = keyword_line[len(keyword_prefix):].strip() if keyword_line else None
        return ' '.join(abstract_lines).strip() or None, keyword_text

    abstract_id, keywords_id = extract_section('ABSTRAK', 'Kata kunci')
    abstract_en, keywords_en = extract_section('ABSTRACT', 'Keywords')

    def extract_paragraph_section(heading):
        marker = f'# {heading}'
        try:
            start = next(
                index for index, line in enumerate(lines[:heading_end])
                if line.strip() == marker
            )
        except StopIteration:
            return []
        paragraphs = []
        current = []
        for line in lines[start + 1:heading_end]:
            stripped = line.strip()
            if stripped.startswith('# '):
                break
            if stripped:
                current.append(stripped)
            elif current:
                paragraphs.append(' '.join(current))
                current = []
        if current:
            paragraphs.append(' '.join(current))
        return paragraphs

    return {
        'title': headings[0],
        'subtitle': headings[1],
        'name': metadata_lines[0],
        'nim': metadata_lines[1],
        'year': year,
        'abstract_id': abstract_id,
        'keywords_id': keywords_id,
        'abstract_en': abstract_en,
        'keywords_en': keywords_en,
        'originality_statement': extract_paragraph_section(
            'SURAT PERNYATAAN KEASLIAN'
        ),
        'copyright_statement': extract_paragraph_section(
            'PERNYATAAN MENGENAI SKRIPSI DAN SUMBER INFORMASI SERTA PELIMPAHAN HAK CIPTA'
        ),
        'preface': extract_paragraph_section('KATA PENGANTAR'),
    }


def replace_paragraph_text(paragraph, text, ns_uri):
    """Replace a paragraph's visible text while retaining its paragraph/run style."""
    ppr = paragraph.find(f'{{{ns_uri}}}pPr')
    source_run = paragraph.find(f'{{{ns_uri}}}r')
    source_rpr = source_run.find(f'{{{ns_uri}}}rPr') if source_run is not None else None
    for child in list(paragraph):
        if child is not ppr:
            paragraph.remove(child)
    run = lxml.etree.SubElement(paragraph, f'{{{ns_uri}}}r')
    if source_rpr is not None:
        run.append(copy.deepcopy(source_rpr))
    for index, line in enumerate(text.split('\n')):
        if index:
            lxml.etree.SubElement(run, f'{{{ns_uri}}}br')
        if line:
            text_node = lxml.etree.SubElement(run, f'{{{ns_uri}}}t')
            text_node.text = line
            text_node.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')


APPROVAL_IMAGE_SOURCE = os.path.join(
    'images', 'lembar_persetujuan.jpeg'
)


def _next_relationship_id(rels_root):
    ids = []
    for relationship in rels_root:
        value = relationship.get('Id', '')
        if value.startswith('rId') and value[3:].isdigit():
            ids.append(int(value[3:]))
    return f'rId{max(ids, default=0) + 1}'


def _next_media_name(media_dir, extension='png'):
    numbers = []
    for filename in os.listdir(media_dir):
        match = re.fullmatch(r'image(\d+)\.[^.]+', filename, re.IGNORECASE)
        if match:
            numbers.append(int(match.group(1)))
    return f'image{max(numbers, default=0) + 1}.{extension.lstrip(".").lower()}'


def _next_docpr_id(root):
    values = []
    wp_uri = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
    for node in root.iter(f'{{{wp_uri}}}docPr'):
        value = node.get('id')
        if value and value.isdigit():
            values.append(int(value))
    return max(values, default=0) + 1


def inject_approval_image(paragraph, root, unpacked_dir, ns_uri):
    """Replace the approval placeholder with the latest supplied image.

    The latest approval image is embedded byte-for-byte as JPEG. It remains a
    front-matter element rather than a report figure, so no caption, marker, or
    manifest entry is created.
    """
    image_source = os.path.join(os.getcwd(), APPROVAL_IMAGE_SOURCE)
    if not os.path.exists(image_source):
        raise FileNotFoundError(
            'Approval image is missing: ' + image_source
        )

    media_dir = os.path.join(unpacked_dir, 'word', 'media')
    rels_path = os.path.join(unpacked_dir, 'word', '_rels', 'document.xml.rels')
    content_types_path = os.path.join(unpacked_dir, '[Content_Types].xml')
    os.makedirs(media_dir, exist_ok=True)

    rel_ns = 'http://schemas.openxmlformats.org/package/2006/relationships'
    rel_tree = lxml.etree.parse(rels_path)
    rels_root = rel_tree.getroot()
    r_id = _next_relationship_id(rels_root)
    source_extension = os.path.splitext(image_source)[1].lstrip('.').lower() or 'png'
    media_name = _next_media_name(media_dir, source_extension)
    shutil.copy2(image_source, os.path.join(media_dir, media_name))
    lxml.etree.SubElement(
        rels_root,
        f'{{{rel_ns}}}Relationship',
        {
            'Id': r_id,
            'Type': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image',
            'Target': f'media/{media_name}',
        },
    )
    rel_tree.write(rels_path, encoding='utf-8', xml_declaration=True)

    content_types_ns = 'http://schemas.openxmlformats.org/package/2006/content-types'
    content_tree = lxml.etree.parse(content_types_path)
    content_root = content_tree.getroot()
    content_type_by_extension = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'webp': 'image/webp',
    }
    media_content_type = content_type_by_extension.get(
        source_extension, 'application/octet-stream'
    )
    has_source_extension = any(
        (node.get('Extension') or '').lower() == source_extension
        for node in content_root.findall(f'{{{content_types_ns}}}Default')
    )
    if not has_source_extension:
        lxml.etree.SubElement(
            content_root,
            f'{{{content_types_ns}}}Default',
            {'Extension': source_extension, 'ContentType': media_content_type},
        )
        content_tree.write(content_types_path, encoding='utf-8', xml_declaration=True)

    try:
        from inject_all_images import generate_drawing_xml, get_image_dimensions
    except ImportError:
        from skills.scripts.inject_all_images import generate_drawing_xml, get_image_dimensions

    width, height = get_image_dimensions(image_source)
    drawing_paragraph = generate_drawing_xml(
        r_id,
        width * 9525,
        height * 9525,
        'approval-sheet',
        _next_docpr_id(root),
        max_height_emu=8532000,
    )
    ppr = paragraph.find(f'{{{ns_uri}}}pPr')
    for child in list(paragraph):
        if child is not ppr:
            paragraph.remove(child)
    if ppr is None:
        ppr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
        paragraph.insert(0, ppr)
    if ppr.find(f'{{{ns_uri}}}pageBreakBefore') is None:
        lxml.etree.SubElement(ppr, f'{{{ns_uri}}}pageBreakBefore')
    jc = ppr.find(f'{{{ns_uri}}}jc')
    if jc is None:
        jc = lxml.etree.SubElement(ppr, f'{{{ns_uri}}}jc')
    jc.set(f'{{{ns_uri}}}val', 'center')
    for property_name in ('keepNext', 'keepLines'):
        if ppr.find(f'{{{ns_uri}}}{property_name}') is None:
            lxml.etree.SubElement(ppr, f'{{{ns_uri}}}{property_name}')
    drawing_run = drawing_paragraph.find(f'{{{ns_uri}}}r')
    paragraph.append(copy.deepcopy(drawing_run))
    return media_name


def set_paragraph_font_size(paragraph, half_points, ns_uri):
    """Set direct run size for a cover identity paragraph."""
    for run in paragraph.findall('.//w:r', {'w': ns_uri}):
        rpr = run.find('w:rPr', {'w': ns_uri})
        if rpr is None:
            rpr = lxml.etree.Element(f'{{{ns_uri}}}rPr')
            run.insert(0, rpr)
        for tag in ('sz', 'szCs'):
            node = rpr.find(f'w:{tag}', {'w': ns_uri})
            if node is None:
                node = lxml.etree.SubElement(rpr, f'{{{ns_uri}}}{tag}')
            node.set(f'{{{ns_uri}}}val', str(half_points))


def _plain_front_matter_text(text):
    """Remove Markdown-only delimiters before inserting front-matter prose."""
    if not text:
        return ''
    return re.sub(r'(?<!\\)[*_`]', '', text).replace('\\*', '*')


def _build_front_matter_paragraph(
        text, ns_uri, *, style='Normal', half_points=22,
        page_break_before=False, alignment='both', first_line_twips=None,
        left_twips=None, hanging_twips=None, bold=False,
        after_twips='0', line_twips='240'):
    paragraph = lxml.etree.Element(f'{{{ns_uri}}}p')
    ppr = lxml.etree.SubElement(paragraph, f'{{{ns_uri}}}pPr')
    lxml.etree.SubElement(
        ppr, f'{{{ns_uri}}}pStyle', {f'{{{ns_uri}}}val': style}
    )
    if page_break_before:
        lxml.etree.SubElement(ppr, f'{{{ns_uri}}}pageBreakBefore')
    lxml.etree.SubElement(
        ppr, f'{{{ns_uri}}}jc', {f'{{{ns_uri}}}val': alignment}
    )
    spacing = {
        f'{{{ns_uri}}}before': '0',
        f'{{{ns_uri}}}after': str(after_twips),
    }
    if line_twips is not None:
        spacing[f'{{{ns_uri}}}line'] = str(line_twips)
        spacing[f'{{{ns_uri}}}lineRule'] = 'auto'
    lxml.etree.SubElement(ppr, f'{{{ns_uri}}}spacing', spacing)
    if any(
        value is not None
        for value in (first_line_twips, left_twips, hanging_twips)
    ):
        indent = {}
        if first_line_twips is not None:
            indent[f'{{{ns_uri}}}firstLine'] = str(first_line_twips)
        if left_twips is not None:
            indent[f'{{{ns_uri}}}left'] = str(left_twips)
        if hanging_twips is not None:
            indent[f'{{{ns_uri}}}hanging'] = str(hanging_twips)
        lxml.etree.SubElement(
            ppr,
            f'{{{ns_uri}}}ind',
            indent,
        )
    run = lxml.etree.SubElement(paragraph, f'{{{ns_uri}}}r')
    rpr = lxml.etree.SubElement(run, f'{{{ns_uri}}}rPr')
    lxml.etree.SubElement(
        rpr,
        f'{{{ns_uri}}}rFonts',
        {
            f'{{{ns_uri}}}ascii': 'Times New Roman',
            f'{{{ns_uri}}}hAnsi': 'Times New Roman',
            f'{{{ns_uri}}}eastAsia': 'Times New Roman',
            f'{{{ns_uri}}}cs': 'Times New Roman',
        },
    )
    lxml.etree.SubElement(
        rpr, f'{{{ns_uri}}}sz', {f'{{{ns_uri}}}val': str(half_points)}
    )
    lxml.etree.SubElement(
        rpr, f'{{{ns_uri}}}szCs', {f'{{{ns_uri}}}val': str(half_points)}
    )
    if bold:
        lxml.etree.SubElement(rpr, f'{{{ns_uri}}}b')
        lxml.etree.SubElement(rpr, f'{{{ns_uri}}}bCs')
    text_node = lxml.etree.SubElement(run, f'{{{ns_uri}}}t')
    text_node.text = _plain_front_matter_text(text)
    text_node.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    return paragraph


def insert_cover_two_and_statement(body, approval_paragraph, front_matter, ns_uri):
    """Insert a second cover that follows the first cover's layout.

    The archive template's first cover contains a fixed sequence of
    paragraphs around the logo and identity block.  Reusing that sequence
    keeps the second cover's title, identity, and bottom alignment in the
    same positions.  The thesis title replaces the logo paragraph; no logo
    or image is added to the second cover.
    """
    insertion_index = list(body).index(approval_paragraph)
    title = front_matter['title']
    subtitle = front_matter['subtitle']
    preceding_paragraphs = [
        paragraph for paragraph in list(body)[:insertion_index]
        if paragraph.tag == f'{{{ns_uri}}}p'
    ]

    # The archive cover consists of 15 paragraphs (title, logo slot, and
    # identity block).  Clone those paragraphs when available so all spacing,
    # alignment, and font properties track the first cover automatically.
    if len(preceding_paragraphs) >= 15:
        cover_paragraphs = [
            copy.deepcopy(paragraph)
            for paragraph in preceding_paragraphs[:15]
        ]
        replace_paragraph_text(cover_paragraphs[0], 'LAPORAN PROYEK', ns_uri)
        replace_paragraph_text(cover_paragraphs[1], '', ns_uri)
        # Replace the logo paragraph with the two-line thesis title while
        # retaining the first cover's logo-slot position and paragraph style.
        title_slot = copy.deepcopy(cover_paragraphs[0])
        replace_paragraph_text(
            title_slot, title + '\n' + subtitle, ns_uri
        )
        cover_paragraphs[4] = title_slot
        replace_paragraph_text(
            cover_paragraphs[7], front_matter['name'], ns_uri
        )
        replace_paragraph_text(
            cover_paragraphs[8], front_matter['nim'], ns_uri
        )
        replace_paragraph_text(cover_paragraphs[11], 'INFORMATIKA', ns_uri)
        replace_paragraph_text(
            cover_paragraphs[12], 'FAKULTAS ILMU KOMPUTER', ns_uri
        )
        replace_paragraph_text(
            cover_paragraphs[13],
            'UNIVERSITAS PEMBANGUNAN NASIONAL VETERAN JAKARTA',
            ns_uri,
        )
        replace_paragraph_text(
            cover_paragraphs[14], front_matter['year'], ns_uri
        )
        first_ppr = cover_paragraphs[0].find(f'{{{ns_uri}}}pPr')
        if first_ppr is None:
            first_ppr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
            cover_paragraphs[0].insert(0, first_ppr)
        if first_ppr.find(f'{{{ns_uri}}}pageBreakBefore') is None:
            lxml.etree.SubElement(
                first_ppr, f'{{{ns_uri}}}pageBreakBefore'
            )
    else:
        # Keep the helper useful in isolation and in unit tests that provide
        # only a small synthetic body rather than the full archive cover.
        text_kwargs = {
            'half_points': 28,
            'alignment': 'center',
            'bold': True,
            'after_twips': '120',
            'line_twips': None,
        }
        blank_kwargs = {
            'alignment': 'center',
            'after_twips': '0',
            'line_twips': '240',
        }
        cover_paragraphs = [
            _build_front_matter_paragraph(
                'LAPORAN PROYEK', ns_uri, page_break_before=True,
                **text_kwargs,
            ),
            _build_front_matter_paragraph('', ns_uri, **blank_kwargs),
            _build_front_matter_paragraph('', ns_uri, **blank_kwargs),
            _build_front_matter_paragraph('', ns_uri, **blank_kwargs),
            _build_front_matter_paragraph(
                title + '\n' + subtitle, ns_uri, **text_kwargs
            ),
            _build_front_matter_paragraph('', ns_uri, **blank_kwargs),
            _build_front_matter_paragraph('', ns_uri, **blank_kwargs),
            _build_front_matter_paragraph(
                front_matter['name'], ns_uri, **text_kwargs
            ),
            _build_front_matter_paragraph(
                front_matter['nim'], ns_uri, **text_kwargs
            ),
            _build_front_matter_paragraph('', ns_uri, **blank_kwargs),
            _build_front_matter_paragraph('', ns_uri, **blank_kwargs),
            _build_front_matter_paragraph(
                'INFORMATIKA', ns_uri, **text_kwargs
            ),
            _build_front_matter_paragraph(
                'FAKULTAS ILMU KOMPUTER', ns_uri, **text_kwargs
            ),
            _build_front_matter_paragraph(
                'UNIVERSITAS PEMBANGUNAN NASIONAL VETERAN JAKARTA',
                ns_uri, **text_kwargs,
            ),
            _build_front_matter_paragraph(
                front_matter['year'], ns_uri, **text_kwargs
            ),
        ]
    statement_source = front_matter.get('originality_statement') or []
    if statement_source:
        statement_paragraphs = [
            _build_front_matter_paragraph(
                'SURAT PERNYATAAN KEASLIAN',
                ns_uri, style='Normal', half_points=24,
                page_break_before=True, alignment='center', bold=True,
                after_twips='240',
            ),
        ]
        field_prefixes = ('Nama:', 'NIM:', 'Program Studi:', 'Judul Proyek:')
        signature_prefixes = (
            'Jakarta,', 'Yang menyatakan,', '[Meterai dan tanda tangan]'
        )
        for text in statement_source:
            is_field = text.startswith(field_prefixes)
            is_signature = (
                text.startswith(signature_prefixes)
                or text == front_matter.get('name')
            )
            if is_signature:
                alignment = 'right'
                first_line_twips = None
            elif is_field or text == 'Yang bertanda tangan di bawah ini:':
                alignment = 'left'
                first_line_twips = None
            else:
                alignment = 'both'
                first_line_twips = 567
            after_twips = (
                '720' if text == '[Meterai dan tanda tangan]' else
                '240' if text.startswith('Demikian surat pernyataan') else
                '0'
            )
            statement_paragraphs.append(
                _build_front_matter_paragraph(
                    text, ns_uri, half_points=24, alignment=alignment,
                    first_line_twips=first_line_twips,
                    after_twips=after_twips, line_twips='276',
                )
            )
    else:
        statement_paragraphs = [
            _build_front_matter_paragraph(
                'PERNYATAAN MENGENAI SKRIPSI DAN SUMBER INFORMASI',
                ns_uri, style='Normal', half_points=24,
                page_break_before=True, alignment='center', bold=True,
            ),
            _build_front_matter_paragraph('', ns_uri, alignment='center'),
        ]

    copyright_source = front_matter.get('copyright_statement') or []
    if copyright_source:
        copyright_paragraphs = [
            _build_front_matter_paragraph(
                'PERNYATAAN MENGENAI SKRIPSI DAN SUMBER INFORMASI SERTA PELIMPAHAN HAK CIPTA',
                ns_uri, style='Normal', half_points=24,
                page_break_before=True, alignment='center', bold=True,
                after_twips='240',
            ),
        ]
        signature_values = {
            front_matter.get('name'),
            front_matter.get('nim'),
            f"{front_matter.get('name')} {front_matter.get('nim')}",
        }
        for text in copyright_source:
            is_signature = (
                text.startswith('Jakarta,')
                or text in signature_values
            )
            copyright_paragraphs.append(
                _build_front_matter_paragraph(
                    text, ns_uri, half_points=24,
                    alignment='right' if is_signature else 'both',
                    first_line_twips=None if is_signature else 567,
                    after_twips='240' if text.startswith('Dengan ini saya melimpahkan') else '0',
                    line_twips='276',
                )
            )
        statement_paragraphs.extend(copyright_paragraphs)
    cover_paragraphs.extend(statement_paragraphs)
    for offset, paragraph in enumerate(cover_paragraphs):
        body.insert(insertion_index + offset, paragraph)
    return len(cover_paragraphs)


def insert_blank_front_heading(body, heading, ns_uri):
    """Insert one blank front-matter page immediately before Daftar Isi."""
    target = None
    fallback = None
    for child in body:
        visible = ''.join(
            node.text for node in child.iter(f'{{{ns_uri}}}t') if node.text
        ).strip()
        if visible.upper() == 'DAFTAR GAMBAR' and fallback is None:
            fallback = child
        if 'DAFTAR ISI' in visible.upper():
            target = child
            break
    if target is None:
        target = fallback
    if target is None:
        return 0
    target_ppr = target.find(f'{{{ns_uri}}}pPr')
    if target_ppr is None:
        target_ppr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
        target.insert(0, target_ppr)
    if target_ppr.find(f'{{{ns_uri}}}pageBreakBefore') is None:
        lxml.etree.SubElement(target_ppr, f'{{{ns_uri}}}pageBreakBefore')
    insertion_index = list(body).index(target)
    paragraphs = [
        _build_front_matter_paragraph(
            heading, ns_uri, style='Normal', half_points=24,
            page_break_before=True, alignment='center', bold=True,
        ),
        _build_front_matter_paragraph('', ns_uri, alignment='center'),
    ]
    for offset, paragraph in enumerate(paragraphs):
        body.insert(insertion_index + offset, paragraph)
    return len(paragraphs)


def insert_preface_page(body, preface_paragraphs, ns_uri, signature_values=None):
    """Insert the authored Kata Pengantar immediately before Daftar Isi."""
    if not preface_paragraphs:
        return 0
    target = None
    fallback = None
    for child in body:
        visible = ''.join(
            node.text for node in child.iter(f'{{{ns_uri}}}t') if node.text
        ).strip()
        field_code = ''.join(
            node.text for node in child.iter(f'{{{ns_uri}}}instrText') if node.text
        ).upper()
        if visible.upper() == 'DAFTAR GAMBAR' and fallback is None:
            fallback = child
        if 'DAFTAR ISI' in visible.upper() or ' TOC ' in f' {field_code} ':
            target = child
            break
    if target is None:
        target = fallback
    if target is None:
        return 0

    target_ppr = target.find(f'{{{ns_uri}}}pPr')
    if target_ppr is None:
        target_ppr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
        target.insert(0, target_ppr)
    if target_ppr.find(f'{{{ns_uri}}}pageBreakBefore') is None:
        lxml.etree.SubElement(target_ppr, f'{{{ns_uri}}}pageBreakBefore')

    insertion_index = list(body).index(target)
    paragraphs = [
        _build_front_matter_paragraph(
            'KATA PENGANTAR', ns_uri, style='Normal', half_points=24,
            page_break_before=True, alignment='center', bold=True,
        ),
    ]
    signature_values = {
        value for value in (signature_values or ()) if value
    }
    for text in preface_paragraphs:
        numbered = re.match(r'^\d+\.\s+', text) is not None
        is_signature = (
            text.startswith('Jakarta,')
            or text in signature_values
            or bool(re.fullmatch(r'\d{10}', text))
        )
        paragraphs.append(
            _build_front_matter_paragraph(
                text, ns_uri, half_points=24,
                alignment='right' if is_signature else 'both',
                first_line_twips=(
                    None if numbered or is_signature else 567
                ),
                left_twips=567 if numbered and not is_signature else None,
                hanging_twips=360 if numbered and not is_signature else None,
                after_twips='0', line_twips='276',
            )
        )
    for offset, paragraph in enumerate(paragraphs):
        body.insert(insertion_index + offset, paragraph)
    return len(paragraphs)


def insert_bilingual_abstracts(body, front_matter, ns_uri):
    """Insert one separate page per abstract immediately before DAFTAR ISI."""
    required = ('abstract_id', 'keywords_id', 'abstract_en', 'keywords_en')
    if not front_matter or not all(front_matter.get(key) for key in required):
        return 0
    target = None
    fallback = None
    for child in body:
        visible = ''.join(
            node.text for node in child.iter(f'{{{ns_uri}}}t') if node.text
        ).strip()
        field_code = ''.join(
            node.text for node in child.iter(f'{{{ns_uri}}}instrText') if node.text
        ).upper()
        if visible == 'DAFTAR GAMBAR' and fallback is None:
            fallback = child
        if 'DAFTAR ISI' in visible.upper() or ' TOC ' in f' {field_code} ':
            target = child
            break
    if target is None:
        target = fallback
    if target is None:
        return 0
    insertion_index = list(body).index(target)
    paragraphs = [
        _build_front_matter_paragraph(
            'ABSTRAK', ns_uri, style='Heading1', half_points=24,
            page_break_before=True, alignment='center', bold=True,
        ),
        _build_front_matter_paragraph(
            front_matter['abstract_id'], ns_uri, half_points=22,
            alignment='both', first_line_twips=567,
        ),
        _build_front_matter_paragraph(
            f"Kata kunci: {front_matter['keywords_id']}", ns_uri,
            half_points=22, alignment='left',
        ),
        _build_front_matter_paragraph(
            'ABSTRACT', ns_uri, style='Heading1', half_points=24,
            page_break_before=True, alignment='center', bold=True,
        ),
        _build_front_matter_paragraph(
            front_matter['abstract_en'], ns_uri, half_points=22,
            alignment='both', first_line_twips=567,
        ),
        _build_front_matter_paragraph(
            f"Keywords: {front_matter['keywords_en']}", ns_uri,
            half_points=22, alignment='left',
        ),
    ]
    for offset, paragraph in enumerate(paragraphs):
        body.insert(insertion_index + offset, paragraph)
    return len(paragraphs)

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
    front_matter = load_draft_front_matter()
    front_matter_replacements = {}
    if front_matter:
        front_matter_replacements = {
            'Integrasi Denah Virtual Universitas Pembangunan Nasional Veteran Jakarta Kampus Pondok Labu': front_matter['title'],
            '(Dashboard Profil)': front_matter['subtitle'],
            'Muhammad Iman Nugraha': front_matter['name'],
            '2210511129': front_matter['nim'],
        }
        if front_matter.get('year'):
            front_matter_replacements['2025'] = front_matter['year']
        print(
            'Loaded front matter from %s: %s / %s / %s / %s'
            % (
                os.environ.get('TA_DRAFT_PATH', 'Tugas_Akhir_Draft.md'),
                front_matter['title'],
                front_matter['subtitle'],
                front_matter['name'],
                front_matter['nim'],
            )
        )

        paragraph_replacements = {
            'Integrasi Denah Virtual Universitas Pembangunan Nasional Veteran Jakarta Kampus Pondok Labu': front_matter['title'],
            '(Dashboard Profil)': front_matter['subtitle'],
        }
        replaced_front_paragraphs = 0
        for paragraph in body.findall('w:p', namespaces):
            paragraph_text = ''.join(
                node.text for node in paragraph.iter(f'{{{ns_uri}}}t') if node.text
            )
            replacement = paragraph_replacements.get(paragraph_text)
            if replacement is not None:
                replace_paragraph_text(paragraph, replacement, ns_uri)
                replaced_front_paragraphs += 1
        print(f'Replaced {replaced_front_paragraphs} split front-matter paragraph(s).')

        # The retained template contains Iman's signed approval scan. It must
        # not be carried into another student's report. Dwikhi's supplied PDF
        # is embedded exactly as rendered; other reports retain the existing
        # non-fabricated placeholder behavior.
        if front_matter['name'] != 'Muhammad Iman Nugraha':
            front_drawings = [
                paragraph
                for paragraph in body.findall('w:p', namespaces)
                if paragraph.find('.//w:drawing', namespaces) is not None
            ]
            if len(front_drawings) >= 2:
                approval_paragraph = front_drawings[1]
                if front_matter['name'] == 'Dwikhi Deandra Purnianto':
                    media_name = inject_approval_image(
                        approval_paragraph, root, 'unpacked_ta', ns_uri
                    )
                    print(
                        'Replaced template approval scan with the latest approval image '
                        f'({media_name}).'
                    )
                    inserted_front = insert_cover_two_and_statement(
                        body, approval_paragraph, front_matter, ns_uri
                    )
                    print(
                        'Inserted second cover and originality statement page '
                        f'({inserted_front} paragraph(s)).'
                    )
                else:
                    replace_paragraph_text(
                        approval_paragraph,
                        'LEMBAR PERSETUJUAN\n\n'
                        + front_matter['name']
                        + '\nNIM '
                        + front_matter['nim']
                        + '\n\n[TBD: lampirkan lembar persetujuan resmi yang telah ditandatangani]',
                        ns_uri,
                    )
                    print('Replaced mismatched template approval scan with a TBD placeholder.')

    wt_replaced = 0
    for wt in root.xpath('//w:t', namespaces=namespaces):
        text = wt.text
        if not text:
            continue
            
        new_text = front_matter_replacements.get(text, text)
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
        
    if front_matter:
        inserted_abstract_paragraphs = insert_bilingual_abstracts(
            body, front_matter, ns_uri
        )
        if inserted_abstract_paragraphs:
            print(
                'Inserted %d bilingual abstract paragraph(s).'
                % inserted_abstract_paragraphs
            )
        else:
            print('Warning: bilingual abstract metadata was incomplete or target was missing.')

        if front_matter.get('name') == 'Dwikhi Deandra Purnianto':
            inserted_preface = insert_preface_page(
                body,
                front_matter.get('preface'),
                ns_uri,
                signature_values=(
                    front_matter.get('name'),
                    front_matter.get('nim'),
                ),
            )
            if not inserted_preface:
                inserted_preface = insert_blank_front_heading(
                    body, 'KATA PENGANTAR', ns_uri
                )
            if inserted_preface:
                print(
                    'Inserted Kata Pengantar page '
                    f'({inserted_preface} paragraph(s)).'
                )

        identity_values = {front_matter.get('name'), front_matter.get('nim')}
        for paragraph in body.findall('.//w:p', namespaces):
            paragraph_text = ''.join(
                node.text for node in paragraph.iter(f'{{{ns_uri}}}t') if node.text
            ).strip()
            if paragraph_text in identity_values:
                set_paragraph_font_size(paragraph, 28, ns_uri)
    tree.write(xml_path, encoding='utf-8', xml_declaration=True)
    print("SUCCESS: document.xml patched and saved.")
    


if __name__ == '__main__':
    main()
