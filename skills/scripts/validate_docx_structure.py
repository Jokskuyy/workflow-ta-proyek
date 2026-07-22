import sys
import os
import zipfile
import re
import json
import hashlib
import posixpath
import xml.etree.ElementTree as ET

# Namespaces / constants shared by the content-level checks (C1-C4).
W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'
WP_NS = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
PACKAGE_REL_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'
CONTENT_TYPES_NS = 'http://schemas.openxmlformats.org/package/2006/content-types'
MAX_WIDTH_EMU = 5400000
EMU_PER_TWIP = 635  # printable page-height threshold uses twips * 635 (matches injector)
FIGURE_CAPTION_RESERVE_EMU = 1080000  # 3 cm; must match inject_all_images.py

# Canonical UPNVJ FIK page geometry (OOXML twips): A4 portrait with a 4 cm
# binding margin on the left and 3 cm on the top, right, and bottom.
EXPECTED_PAGE_SIZE_DXA = {'w': 11906, 'h': 16838}
EXPECTED_MARGINS_DXA = {
    'top': 1701,
    'right': 1701,
    'bottom': 1701,
    'left': 2268,
}

# w:spacing@line uses 240ths of a line when lineRule="auto". The corrected
# campus rule is 1.15 lines for body, headings, lists, and automatic lists.
EXPECTED_MAIN_LINE_SPACING_AUTO = '276'
LEGACY_CITATION_COMMA_RE = re.compile(
    r'\([^()]*,\s*(?:19|20)\d{2}[a-z]?[^()]*\)',
    re.IGNORECASE,
)
REQUIRED_MAIN_LINE_SPACING_STYLES = (
    'Normal',
    'ListParagraph',
    'Heading1',
    'Heading2',
    'Heading3',
    'TOC1',
    'TOC2',
    'TOC3',
    'TOC9',
    'TableofFigures',
)
UNRESOLVED_SOURCE_TOKEN_RE = re.compile(
    r'\[(?:FIGREF|TABREF|FIGCAPTION|TABLECAPTION|TABLE-ID):[^\]]*\]'
)
SEMANTIC_BOOKMARK_RE = re.compile(r'^(?:fig|tbl)_[a-z0-9_]+$')
REF_FIELD_RE = re.compile(r'\bREF\s+([A-Za-z][A-Za-z0-9_]*)\b', re.IGNORECASE)


def validate_times_new_roman_fonts(xml_parts):
    """Return findings for authored OOXML text that names another font."""
    findings = set()
    allowed = {'times new roman', 'symbol', 'wingdings'}

    def is_allowed(value):
        normalized = (value or '').strip().lower()
        return (
            not normalized
            or normalized in allowed
            or normalized.startswith('wingdings ')
        )

    for part_name, raw_xml in xml_parts.items():
        try:
            root = ET.fromstring(raw_xml)
        except ET.ParseError:
            continue
        for fonts in root.iter(f'{{{W_NS}}}rFonts'):
            for attr in ('ascii', 'hAnsi', 'eastAsia', 'cs'):
                value = fonts.get(f'{{{W_NS}}}{attr}')
                if value and not is_allowed(value):
                    findings.add(
                        f"[font] {part_name} uses {attr}={value!r}; "
                        "expected Times New Roman."
                    )
            for attr in ('asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme'):
                if fonts.get(f'{{{W_NS}}}{attr}') is not None:
                    findings.add(
                        f"[font] {part_name} retains w:{attr}; "
                        "theme fonts are not allowed in report text."
                    )
        for local_name in ('latin', 'ea', 'cs'):
            for font in root.iter(f'{{{A_NS}}}{local_name}'):
                value = font.get('typeface')
                if value and not is_allowed(value):
                    findings.add(
                        f"[font] {part_name} uses DrawingML typeface={value!r}; "
                        "expected Times New Roman."
                    )
    return sorted(findings)


def validate_body_bold_usage(doc_root):
    """Reject direct bold in report body outside approved structural roles."""
    body = doc_root.find(f'{{{W_NS}}}body')
    if body is None:
        return []

    parent = {child: node for node in body.iter() for child in node}
    findings = []
    in_report_body = False

    def style_id(paragraph):
        p_pr = paragraph.find(f'{{{W_NS}}}pPr')
        style = p_pr.find(f'{{{W_NS}}}pStyle') if p_pr is not None else None
        return style.get(f'{{{W_NS}}}val', '') if style is not None else ''

    def in_first_table_row(paragraph):
        node = paragraph
        row = None
        while node in parent:
            node = parent[node]
            if node.tag == f'{{{W_NS}}}tr':
                row = node
                break
        if row is None or row not in parent:
            return False
        table = parent[row]
        rows = [child for child in table if child.tag == f'{{{W_NS}}}tr']
        return bool(rows and rows[0] is row)

    def bold_enabled(run):
        r_pr = run.find(f'{{{W_NS}}}rPr')
        if r_pr is None:
            return False
        bold = r_pr.find(f'{{{W_NS}}}b')
        if bold is None:
            return False
        return (bold.get(f'{{{W_NS}}}val') or '1').lower() not in {
            '0', 'false', 'off', 'none'
        }

    for paragraph_index, paragraph in enumerate(body.iter(f'{{{W_NS}}}p')):
        text = ''.join(
            node.text or '' for node in paragraph.iter(f'{{{W_NS}}}t')
        ).strip()
        style = style_id(paragraph)
        if style == 'Heading1' and re.match(r'^BAB\s+(?:I|1)\b', text, re.IGNORECASE):
            in_report_body = True
        if not in_report_body:
            continue
        if style.startswith('Heading') or style == 'taappendixheading':
            continue
        if in_first_table_row(paragraph):
            continue

        if style in {'Caption', 'Keterangan'}:
            label_match = re.match(r'^(?:Gambar|Tabel)\s+\d+(?:\.\d+)+', text)
            label = label_match.group(0) if label_match else ''
            for run in paragraph.findall(f'{{{W_NS}}}r'):
                run_text = ''.join(
                    node.text or '' for node in run.iter(f'{{{W_NS}}}t')
                )
                if bold_enabled(run) and run_text and run_text not in label:
                    findings.append(
                        f"[bold] caption paragraph {paragraph_index} has bold "
                        f"description text {run_text!r}."
                    )
            continue

        for run in paragraph.findall(f'{{{W_NS}}}r'):
            run_text = ''.join(
                node.text or '' for node in run.iter(f'{{{W_NS}}}t')
            ).strip()
            if run_text and bold_enabled(run):
                findings.append(
                    f"[bold] body paragraph {paragraph_index} has disallowed "
                    f"bold text {run_text!r}."
                )
    return findings


def validate_page_layout(doc_root):
    """Return fatal findings for any section that violates campus geometry."""
    body = doc_root.find(f'{{{W_NS}}}body')
    if body is None:
        return ["[layout] document body is missing; page layout cannot be validated."]

    sections = list(body.iter(f'{{{W_NS}}}sectPr'))
    if not sections:
        return ["[layout] no w:sectPr found; A4 size and margins are undefined."]

    findings = []
    for section_number, sect_pr in enumerate(sections, start=1):
        pg_sz = sect_pr.find(f'{{{W_NS}}}pgSz')
        pg_mar = sect_pr.find(f'{{{W_NS}}}pgMar')
        if pg_sz is None:
            findings.append(f"[layout] section {section_number} is missing w:pgSz.")
        else:
            for name, expected in EXPECTED_PAGE_SIZE_DXA.items():
                raw = pg_sz.get(f'{{{W_NS}}}{name}')
                if raw != str(expected):
                    findings.append(
                        f"[layout] section {section_number} pgSz@{name}={raw!r}; "
                        f"expected {expected} twips (A4 portrait)."
                    )
            orientation = pg_sz.get(f'{{{W_NS}}}orient')
            if orientation not in (None, 'portrait'):
                findings.append(
                    f"[layout] section {section_number} orientation={orientation!r}; "
                    "expected portrait."
                )

        if pg_mar is None:
            findings.append(f"[layout] section {section_number} is missing w:pgMar.")
        else:
            for name, expected in EXPECTED_MARGINS_DXA.items():
                raw = pg_mar.get(f'{{{W_NS}}}{name}')
                if raw != str(expected):
                    cm = 4 if name == 'left' else 3
                    findings.append(
                        f"[layout] section {section_number} margin {name}={raw!r}; "
                        f"expected {expected} twips ({cm} cm)."
                    )
    return findings


def validate_main_line_spacing(styles_root):
    """Return fatal findings when main paragraph styles do not resolve to 1.15.

    Word may normalize a DOCX during COM field updates by moving the common
    line value into ``docDefaults`` and removing redundant values from each
    style. Resolve the ``basedOn`` chain plus paragraph defaults so validation
    checks effective formatting instead of requiring one exact XML layout.
    """
    style_tag = f'{{{W_NS}}}style'
    style_id_attr = f'{{{W_NS}}}styleId'
    type_attr = f'{{{W_NS}}}type'
    p_pr_tag = f'{{{W_NS}}}pPr'
    spacing_tag = f'{{{W_NS}}}spacing'
    based_on_tag = f'{{{W_NS}}}basedOn'
    val_attr = f'{{{W_NS}}}val'
    line_attr = f'{{{W_NS}}}line'
    line_rule_attr = f'{{{W_NS}}}lineRule'

    styles = {
        style.get(style_id_attr): style
        for style in styles_root.findall(style_tag)
        if style.get(type_attr) == 'paragraph'
    }
    findings = []
    style_ids = list(REQUIRED_MAIN_LINE_SPACING_STYLES)
    style_ids.extend(
        style_id for style_id in styles
        if style_id and style_id.startswith('Heading') and style_id not in style_ids
    )

    default_spacing = styles_root.find(
        f'{{{W_NS}}}docDefaults/'
        f'{{{W_NS}}}pPrDefault/'
        f'{{{W_NS}}}pPr/'
        f'{{{W_NS}}}spacing'
    )
    default_line = default_spacing.get(line_attr) if default_spacing is not None else None
    default_line_rule = (
        default_spacing.get(line_rule_attr) if default_spacing is not None else None
    )

    def effective_spacing(style_id, seen=None):
        seen = set() if seen is None else set(seen)
        if style_id in seen:
            return default_line, default_line_rule
        seen.add(style_id)
        style = styles.get(style_id)
        if style is None:
            return default_line, default_line_rule

        p_pr = style.find(p_pr_tag)
        spacing = p_pr.find(spacing_tag) if p_pr is not None else None
        own_line = spacing.get(line_attr) if spacing is not None else None
        own_line_rule = spacing.get(line_rule_attr) if spacing is not None else None

        based_on = style.find(based_on_tag)
        parent_id = based_on.get(val_attr) if based_on is not None else None
        parent_line, parent_rule = (
            effective_spacing(parent_id, seen)
            if parent_id
            else (default_line, default_line_rule)
        )
        return own_line or parent_line, own_line_rule or parent_rule

    for style_id in style_ids:
        style = styles.get(style_id)
        if style is None:
            if style_id in REQUIRED_MAIN_LINE_SPACING_STYLES:
                findings.append(
                    f"[spacing] required paragraph style '{style_id}' is missing."
                )
            continue
        line, line_rule = effective_spacing(style_id)
        if line != EXPECTED_MAIN_LINE_SPACING_AUTO or line_rule != 'auto':
            findings.append(
                f"[spacing] style '{style_id}' resolves to line={line!r}, "
                f"lineRule={line_rule!r}; expected line='276', lineRule='auto' "
                "(1.15 lines)."
            )
    return findings


def validate_semantic_cross_references(doc_root):
    """Validate source-token removal and Word bookmark/REF integrity."""
    body = doc_root.find(f'{{{W_NS}}}body')
    if body is None:
        return ['[crossref] document body is missing.']

    findings = []
    bookmark_rows = {}
    referenced_names = []
    for paragraph_index, paragraph in enumerate(body.iter(f'{{{W_NS}}}p')):
        visible_text = ''.join(
            node.text or '' for node in paragraph.iter(f'{{{W_NS}}}t')
        )
        for token in UNRESOLVED_SOURCE_TOKEN_RE.findall(visible_text):
            findings.append(
                f"[crossref] paragraph {paragraph_index} contains unresolved "
                f"source token {token!r}."
            )

        paragraph_instructions = ' '.join(
            node.text or '' for node in paragraph.iter(f'{{{W_NS}}}instrText')
        )
        for match in REF_FIELD_RE.finditer(paragraph_instructions):
            referenced_names.append(match.group(1))

        end_ids = {
            node.get(f'{{{W_NS}}}id')
            for node in paragraph.iter(f'{{{W_NS}}}bookmarkEnd')
        }
        for start in paragraph.iter(f'{{{W_NS}}}bookmarkStart'):
            name = start.get(f'{{{W_NS}}}name', '')
            if not SEMANTIC_BOOKMARK_RE.fullmatch(name):
                continue
            bookmark_id = start.get(f'{{{W_NS}}}id')
            bookmark_rows.setdefault(name, []).append(paragraph_index)
            expected_label = 'Gambar' if name.startswith('fig_') else 'Tabel'
            if bookmark_id not in end_ids:
                findings.append(
                    f"[crossref] semantic bookmark {name!r} at paragraph "
                    f"{paragraph_index} has no matching bookmarkEnd."
                )
            if not visible_text.startswith(expected_label + ' '):
                findings.append(
                    f"[crossref] semantic bookmark {name!r} is not attached "
                    f"to a visible {expected_label} caption."
                )
            if f'SEQ {expected_label}' not in paragraph_instructions:
                findings.append(
                    f"[crossref] semantic bookmark {name!r} caption is missing "
                    f"the SEQ {expected_label} field."
                )

    for name, positions in sorted(bookmark_rows.items()):
        if len(positions) != 1:
            findings.append(
                f"[crossref] semantic bookmark {name!r} occurs "
                f"{len(positions)} times at paragraphs {positions}; expected once."
            )
        if name not in referenced_names:
            findings.append(
                f"[crossref] semantic bookmark {name!r} has no REF field."
            )
    for name in sorted(set(referenced_names)):
        if SEMANTIC_BOOKMARK_RE.fullmatch(name) and name not in bookmark_rows:
            findings.append(
                f"[crossref] REF field targets missing semantic bookmark {name!r}."
            )
    return findings


def _page_field_alignment(part_root):
    """Return PAGE-field paragraph alignment, or None when no PAGE field exists."""
    if part_root is None:
        return None
    for paragraph in part_root.iter(f'{{{W_NS}}}p'):
        instructions = [
            node.text or '' for node in paragraph.iter(f'{{{W_NS}}}instrText')
        ]
        instructions.extend(
            node.get(f'{{{W_NS}}}instr', '')
            for node in paragraph.iter(f'{{{W_NS}}}fldSimple')
        )
        if not re.search(r'\bPAGE\b', ' '.join(instructions), re.IGNORECASE):
            continue
        p_pr = paragraph.find(f'{{{W_NS}}}pPr')
        jc = p_pr.find(f'{{{W_NS}}}jc') if p_pr is not None else None
        return jc.get(f'{{{W_NS}}}val') if jc is not None else ''
    return None


def validate_page_numbering(doc_root, rels_root, page_parts):
    """Validate Roman/Arabic numbering, reset, and header/footer placement."""
    body = doc_root.find(f'{{{W_NS}}}body')
    if body is None:
        return ['[page-number] document body is missing.']

    numbered_chapters = 0
    for paragraph in body.findall(f'{{{W_NS}}}p'):
        p_pr = paragraph.find(f'{{{W_NS}}}pPr')
        if p_pr is None:
            continue
        p_style = p_pr.find(f'{{{W_NS}}}pStyle')
        num_pr = p_pr.find(f'{{{W_NS}}}numPr')
        if (
            p_style is not None
            and p_style.get(f'{{{W_NS}}}val', '').lower() == 'heading1'
            and num_pr is not None
        ):
            numbered_chapters += 1

    # Unit-test fixtures and partial documents do not necessarily model a full
    # report. Enforce this contract only when numbered BAB headings are present.
    if numbered_chapters == 0:
        return []

    sections = list(body.iter(f'{{{W_NS}}}sectPr'))
    if len(sections) < 2:
        return [
            '[page-number] expected front matter plus at least one BAB section; '
            f'found {len(sections)} section(s).'
        ]

    rel_targets = {}
    if rels_root is not None:
        for relationship in rels_root:
            rid = relationship.get('Id')
            target = relationship.get('Target')
            if rid and target:
                rel_targets[rid] = posixpath.normpath(
                    posixpath.join('word', target)
                )

    findings = []

    def page_part(section, tag_name, ref_type, label):
        ref = next(
            (
                item for item in section.findall(f'{{{W_NS}}}{tag_name}')
                if item.get(f'{{{W_NS}}}type') == ref_type
            ),
            None,
        )
        if ref is None:
            findings.append(
                f"[page-number] {label} is missing {ref_type} {tag_name}."
            )
            return None
        rid = ref.get(f'{{{R_NS}}}id')
        target = rel_targets.get(rid)
        if target is None or target not in page_parts:
            findings.append(
                f"[page-number] {label} {ref_type} {tag_name} cannot be resolved "
                f"from relationship {rid!r}."
            )
            return None
        return page_parts[target]

    def require_page(part, alignment, label):
        actual = _page_field_alignment(part)
        accepted = {'right', 'end'} if alignment == 'right' else {alignment}
        if actual not in accepted:
            findings.append(
                f"[page-number] {label} PAGE field alignment={actual!r}; "
                f"expected {alignment!r}."
            )

    def require_blank(part, label):
        actual = _page_field_alignment(part)
        if actual is not None:
            findings.append(
                f"[page-number] {label} must not contain a PAGE field."
            )

    if len(sections) != numbered_chapters + 1:
        findings.append(
            f'[page-number] found {numbered_chapters} numbered BAB heading(s) but '
            f'{len(sections)} section(s); expected one front section plus one per BAB.'
        )

    front = sections[0]
    front_num = front.find(f'{{{W_NS}}}pgNumType')
    front_fmt = front_num.get(f'{{{W_NS}}}fmt') if front_num is not None else None
    front_start = front_num.get(f'{{{W_NS}}}start') if front_num is not None else None
    if front_fmt != 'lowerRoman' or front_start != '1':
        findings.append(
            f"[page-number] front matter has fmt={front_fmt!r}, start={front_start!r}; "
            "expected lowerRoman starting at 1."
        )
    if front.find(f'{{{W_NS}}}titlePg') is None:
        findings.append('[page-number] front matter is missing w:titlePg for the cover page.')

    front_default_header = page_part(front, 'headerReference', 'default', 'front matter')
    front_first_header = page_part(front, 'headerReference', 'first', 'front matter')
    front_default_footer = page_part(front, 'footerReference', 'default', 'front matter')
    front_first_footer = page_part(front, 'footerReference', 'first', 'front matter')
    require_blank(front_default_header, 'front-matter default header')
    require_blank(front_first_header, 'front-matter first-page header')
    require_page(front_default_footer, 'right', 'front-matter default footer')
    require_blank(front_first_footer, 'front-matter first-page footer')

    for body_index, section in enumerate(sections[1:], start=1):
        label = f'BAB section {body_index}'
        pg_num = section.find(f'{{{W_NS}}}pgNumType')
        fmt = pg_num.get(f'{{{W_NS}}}fmt') if pg_num is not None else None
        start = pg_num.get(f'{{{W_NS}}}start') if pg_num is not None else None
        if fmt not in (None, 'decimal'):
            findings.append(
                f"[page-number] {label} has fmt={fmt!r}; expected decimal."
            )
        if body_index == 1 and start != '1':
            findings.append(
                f"[page-number] BAB I must restart Arabic numbering at 1; start={start!r}."
            )
        if body_index > 1 and start is not None:
            findings.append(
                f"[page-number] {label} unexpectedly restarts at {start!r}; "
                "numbering must continue from the previous BAB."
            )
        if section.find(f'{{{W_NS}}}titlePg') is None:
            findings.append(
                f'[page-number] {label} is missing w:titlePg for its opening page.'
            )

        default_header = page_part(section, 'headerReference', 'default', label)
        first_header = page_part(section, 'headerReference', 'first', label)
        default_footer = page_part(section, 'footerReference', 'default', label)
        first_footer = page_part(section, 'footerReference', 'first', label)
        require_page(default_header, 'right', f'{label} continuation header')
        require_blank(first_header, f'{label} opening-page header')
        require_blank(default_footer, f'{label} continuation footer')
        require_page(first_footer, 'center', f'{label} opening-page footer')

    return findings


def _md5_bytes(b):
    """Hex MD5 of a byte string."""
    return hashlib.md5(b).hexdigest()


def _md5_file(path):
    """Hex MD5 of a file's bytes."""
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def _content_text(p):
    """Concatenated, stripped text of every w:t descendant of a paragraph."""
    return "".join(t.text for t in p.iter(f'{{{W_NS}}}t') if t.text).strip()


def _content_style(p):
    """pStyle val of a paragraph ('' if none)."""
    pPr = p.find(f'{{{W_NS}}}pPr')
    if pPr is None:
        return ""
    pStyle = pPr.find(f'{{{W_NS}}}pStyle')
    if pStyle is None:
        return ""
    return pStyle.get(f'{{{W_NS}}}val') or ""


def collect_figure_narration_errors(p_list, bab1_idx=-1):
    """Return fatal findings for figures without an explicit narrative mention.

    Every ``Gambar X.Y`` caption in the report body must be referenced by an
    ordinary paragraph in the same chapter.  The reference must occur in the
    middle of a sentence, rather than starting a paragraph/sentence with the
    figure label.  This mirrors the canonical UPNVJ writing rule and keeps the
    check independent from visual placement of the drawing/caption pair.
    """

    heading1_idxs = [
        i for i, paragraph in enumerate(p_list)
        if _content_style(paragraph).lower() == 'heading1'
    ]

    def chapter_range(caption_idx):
        start = 0
        for heading_idx in heading1_idxs:
            if heading_idx <= caption_idx:
                start = heading_idx
            else:
                break
        end = len(p_list)
        for heading_idx in heading1_idxs:
            if heading_idx > caption_idx:
                end = heading_idx
                break
        return start, end

    findings = []
    for caption_idx, paragraph in enumerate(p_list):
        if bab1_idx != -1 and caption_idx < bab1_idx:
            continue

        style = _content_style(paragraph)
        text = _content_text(paragraph)
        is_figure_caption = (
            style.lower() == 'caption'
            and re.match(r'^Gambar\s+[0-9]', text, re.IGNORECASE)
        )
        if not is_figure_caption:
            continue

        caption_match = re.match(r'^Gambar\s+([0-9]+\.[0-9]+)', text, re.IGNORECASE)
        if not caption_match:
            continue

        figure_number = caption_match.group(1)
        reference_re = re.compile(
            r'\bGambar\s+' + re.escape(figure_number) + r'\b',
            re.IGNORECASE,
        )
        chapter_start, chapter_end = chapter_range(caption_idx)
        has_reference = False
        has_valid_reference = False

        for narrative_idx in range(chapter_start, chapter_end):
            if narrative_idx == caption_idx:
                continue
            narrative = p_list[narrative_idx]
            narrative_style = _content_style(narrative)
            if narrative_style == 'Caption':
                continue
            if narrative_style.lower().startswith('heading'):
                continue
            if narrative_style.lower() in ('tableoffigures', 'table of figures'):
                continue
            if narrative.find(f'.//{{{W_NS}}}drawing') is not None:
                continue

            narrative_text = _content_text(narrative)
            if not narrative_text:
                continue
            for reference_match in reference_re.finditer(narrative_text):
                has_reference = True
                # Empty prefix means the label starts the paragraph.  A terminal
                # punctuation mark means it starts a later sentence.
                prefix = narrative_text[:reference_match.start()].rstrip()
                if prefix and not re.search(r'[.!?]\s*$', prefix):
                    has_valid_reference = True
                    break
            if has_valid_reference:
                break

        if not has_reference:
            findings.append(
                f'[narration] Gambar {figure_number} tidak memiliki paragraf '
                f'narasi yang menyebut "Gambar {figure_number}" dalam bab yang sama.'
            )
        elif not has_valid_reference:
            findings.append(
                f'[narration] Rujukan Gambar {figure_number} mengawali kalimat; '
                'rujukan harus ditempatkan di tengah kalimat narasi.'
            )

    return findings


def collect_citation_punctuation_errors(p_list, bab1_idx=-1):
    """Reject legacy ``(Author, Year)`` commas in report-body citations."""
    findings = []
    for paragraph_index, paragraph in enumerate(p_list):
        if bab1_idx != -1 and paragraph_index < bab1_idx:
            continue
        text = _content_text(paragraph)
        style = _content_style(paragraph).lower()
        if style == 'heading1' and 'DAFTAR PUSTAKA' in text.upper():
            break
        if not text or style == 'caption' or paragraph.find(f'.//{{{W_NS}}}drawing') is not None:
            continue
        for match in LEGACY_CITATION_COMMA_RE.finditer(text):
            findings.append(
                f"[citation-format] Paragraph {paragraph_index} uses legacy citation "
                f"{match.group(0)!r}; remove the comma before the year."
            )
    return findings


def _resolve_caption_indices_content(body, caption_match):
    """Replicate the injector's resolution rule: collect the indices (within the
    body's direct children) of ALL paragraphs where pStyle == 'Caption', the text
    contains caption_match, and the remainder matches ^(Gambar|Tabel)\\s+[0-9\\.]+$.
    Returns (children_list, matched_indices)."""
    children = list(body)
    matches = []
    for idx, child in enumerate(children):
        if child.tag != f'{{{W_NS}}}p':
            continue
        if _content_style(child) != 'Caption':
            continue
        text = _content_text(child)
        if caption_match in text:
            remainder = text.replace(caption_match, "").strip()
            if re.match(r'^(Gambar|Tabel)\s+[0-9\.]+$', remainder, re.IGNORECASE):
                matches.append(idx)
    return children, matches


def _preceding_drawing_media(children, caption_idx, rel_target):
    """Walk backwards from a caption to the nearest preceding drawing paragraph
    (skipping empty paragraphs) and resolve its blip -> rels Target -> packed
    media name ('word/media/imageNN'). Returns (media_name, drawing_p) or
    (None, None)."""
    j = caption_idx - 1
    while j >= 0:
        prev = children[j]
        if prev.tag != f'{{{W_NS}}}p':
            break
        if prev.find(f'.//{{{W_NS}}}drawing') is not None:
            blip = prev.find(f'.//{{{A_NS}}}blip')
            if blip is None:
                return None, None
            embed = blip.get(f'{{{R_NS}}}embed')
            target = rel_target.get(embed)
            if not target:
                return None, None
            return 'word/' + target, prev
        if _content_text(prev):
            break
        j -= 1
    return None, None


def _resolve_figure_identity_content(body, figure_id):
    """Find direct-body drawing paragraphs carrying the exact manifest id."""
    children = list(body)
    expected = f"FIGURE:{figure_id}"
    matches = []
    for idx, child in enumerate(children):
        if child.tag != f'{{{W_NS}}}p':
            continue
        doc_pr = child.find(f'.//{{{WP_NS}}}docPr')
        if doc_pr is not None and doc_pr.get('name') == expected:
            matches.append(idx)
    return children, matches


def _drawing_media(drawing_p, rel_target):
    """Resolve one drawing paragraph to its packed ``word/media`` part."""
    blip = drawing_p.find(f'.//{{{A_NS}}}blip')
    if blip is None:
        return None
    target = rel_target.get(blip.get(f'{{{R_NS}}}embed'))
    return 'word/' + target if target else None


def _printable_height_emu_content(doc_root):
    """Printable page height in EMU from the body sectPr:
    (pgSz.h - pgMar.top - pgMar.bottom) twips * 635. Must match the injector's
    threshold. Falls back to MAX_WIDTH_EMU if the geometry is unavailable."""
    sect = doc_root.find(f'{{{W_NS}}}body/{{{W_NS}}}sectPr')
    if sect is None:
        return MAX_WIDTH_EMU
    pgSz = sect.find(f'{{{W_NS}}}pgSz')
    pgMar = sect.find(f'{{{W_NS}}}pgMar')
    if pgSz is None or pgMar is None:
        return MAX_WIDTH_EMU
    try:
        h = int(pgSz.get(f'{{{W_NS}}}h'))
        top = int(pgMar.get(f'{{{W_NS}}}top'))
        bottom = int(pgMar.get(f'{{{W_NS}}}bottom'))
    except (TypeError, ValueError):
        return MAX_WIDTH_EMU
    return (h - top - bottom) * EMU_PER_TWIP


def collect_figure_same_page_errors(body, printable_height_emu):
    """Return fatal C4 findings for broken drawing/caption page contracts.

    Word keeps two adjacent paragraphs on one page when the drawing paragraph
    has ``keepNext`` and both paragraphs have ``keepLines``, provided the pair
    can fit in the printable height.  The injector reserves 3 cm for the
    caption when scaling; this validator checks the same structural contract.
    """
    findings = []
    children = list(body) if body is not None else []
    for idx, drawing_p in enumerate(children):
        if drawing_p.tag != f'{{{W_NS}}}p':
            continue
        drawing = drawing_p.find(f'.//{{{W_NS}}}drawing')
        if drawing is None:
            continue

        ext = drawing.find(f'.//{{{WP_NS}}}extent')
        try:
            rendered_height = int(ext.get('cy')) if ext is not None else None
        except (TypeError, ValueError):
            rendered_height = None
        drawing_p_pr = drawing_p.find(f'{{{W_NS}}}pPr')
        has_page_break_before = bool(
            drawing_p_pr is not None
            and drawing_p_pr.find(f'{{{W_NS}}}pageBreakBefore') is not None
        )
        if (rendered_height is not None
                and rendered_height > printable_height_emu
                and not has_page_break_before):
            findings.append(
                f"[C4] drawing paragraph {idx} is too tall (image height "
                f"{rendered_height} EMU > printable page height "
                f"{printable_height_emu} EMU) but lacks w:pageBreakBefore."
            )

        doc_pr = drawing.find(f'.//{{{WP_NS}}}docPr')
        identity = doc_pr.get('name', '') if doc_pr is not None else ''
        next_p = children[idx + 1] if idx + 1 < len(children) else None
        next_text = (
            _content_text(next_p)
            if next_p is not None and next_p.tag == f'{{{W_NS}}}p'
            else ''
        )
        next_is_caption = bool(
            next_p is not None
            and next_p.tag == f'{{{W_NS}}}p'
            and _content_style(next_p) == 'Caption'
            and re.match(r'^Gambar\s+[0-9]+\.[0-9]+\b', next_text, re.IGNORECASE)
        )
        is_report_figure = identity.startswith('FIGURE:') or next_is_caption
        if not is_report_figure:
            continue

        figure_name = identity or next_text or f'paragraph {idx}'
        if not next_is_caption:
            findings.append(
                f"[C4] {figure_name!r} is not immediately followed by its Gambar "
                "caption; the pair cannot be guaranteed on one page."
            )
            continue

        caption_p_pr = next_p.find(f'{{{W_NS}}}pPr')
        for prop in ('keepNext', 'keepLines'):
            if (drawing_p_pr is None
                    or drawing_p_pr.find(f'{{{W_NS}}}{prop}') is None):
                findings.append(
                    f"[C4] {figure_name!r} drawing is missing w:{prop}; "
                    "drawing and caption may be split across pages."
                )
        for prop in ('keepNext', 'keepLines'):
            if (caption_p_pr is None
                    or caption_p_pr.find(f'{{{W_NS}}}{prop}') is None):
                findings.append(
                    f"[C4] caption {next_text!r} is missing w:{prop}; the "
                    "drawing/caption same-page chain is incomplete."
                )

        if rendered_height is None:
            findings.append(
                f"[C4] {figure_name!r} has no valid rendered height; same-page "
                "fit with its caption cannot be validated."
            )
        elif rendered_height + FIGURE_CAPTION_RESERVE_EMU > printable_height_emu:
            findings.append(
                f"[C4] {figure_name!r} plus the 3 cm caption reserve requires "
                f"{rendered_height + FIGURE_CAPTION_RESERVE_EMU} EMU, exceeding "
                f"the printable page height {printable_height_emu} EMU."
            )
    return findings


# ============================================================ #
# Writing guards (R6) + citation cross-check (R1.5/1.6/6.3/1.7).
#
# These wire the PURE collectors defined in the Mesin_Merge
# (scratch/merge_draft_to_docx.py) into the validator and print their results
# as NON-FATAL "[WARN]" lines, ADDITIVELY (R6.6): existing checks A-J and C1-C4
# are untouched and none of the structural guards append to errors_found.
#
# The ONLY path that can become fatal is the citation cross-check, and only
# when explicitly configured via env "TA_CITATION_FATAL=1" (or the
# "--citation-fatal" flag) -- R1.7. Default remains non-fatal.
#
# Everything here is defensively guarded: if the Mesin_Merge module or the draft
# cannot be located/read, the guards are skipped with a note and the legacy
# validation semantics are preserved exactly.
# ============================================================ #
def _locate_merge_module():
    """Locate and import scratch/merge_draft_to_docx.py (the Mesin_Merge that
    hosts the pure guard collectors). Walks up from this file and the cwd,
    checking both "<root>" and "<root>/scratch". Returns the module or None."""
    search_roots = []

    def _add_ancestors(start):
        d = start
        for _ in range(8):
            if d and d not in search_roots:
                search_roots.append(d)
            nd = os.path.dirname(d)
            if not nd or nd == d:
                break
            d = nd

    _add_ancestors(os.path.dirname(os.path.abspath(__file__)))
    _add_ancestors(os.getcwd())

    for root in search_roots:
        for sub in (".", "scratch"):
            cand = os.path.join(root, sub, "merge_draft_to_docx.py")
            if os.path.exists(cand):
                moddir = os.path.dirname(os.path.abspath(cand))
                if moddir not in sys.path:
                    sys.path.insert(0, moddir)
                try:
                    import merge_draft_to_docx as _m
                    return _m
                except Exception:
                    return None
    return None


def _locate_draft():
    """Locate the draft Markdown (source of truth for the writing guards).
    Honours env "TA_DRAFT_PATH" authoritatively: when set, that path is used
    exclusively (returned only if it exists, else None -- no silent fallback to
    a different draft). Otherwise looks for "Tugas_Akhir_Draft.md" in the cwd and
    the ancestors of this file. Returns a path or None."""
    env = os.environ.get("TA_DRAFT_PATH")
    if env:
        return env if os.path.exists(env) else None
    candidates = [os.path.join(os.getcwd(), "Tugas_Akhir_Draft.md")]
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(8):
        candidates.append(os.path.join(d, "Tugas_Akhir_Draft.md"))
        nd = os.path.dirname(d)
        if not nd or nd == d:
            break
        d = nd
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def _citation_fatal_enabled():
    """R1.7 — the citation cross-check is fatal only when explicitly configured
    via env "TA_CITATION_FATAL" (1/true/yes/on) or the "--citation-fatal" flag.
    Default (unset) is non-fatal."""
    val = os.environ.get("TA_CITATION_FATAL", "")
    if val.strip().lower() in ("1", "true", "yes", "on"):
        return True
    if "--citation-fatal" in sys.argv:
        return True
    return False


def _run_writing_guards(errors_found):
    """Run the pure writing-guard collectors against the draft and print their
    results as non-fatal "[WARN]" lines (R6.1/6.2/6.4/6.5). The citation
    cross-check (R1.5/1.6/6.3) is also printed non-fatal by default and only
    appended to errors_found when fatal mode is configured (R1.7).

    This NEVER raises: any lookup/parse failure degrades to a skip note so the
    legacy validation is preserved exactly (R6.6)."""
    print("Checking writing guards (heading/BAB/table/emphasis/citation, non-fatal additive)...")

    mrg = _locate_merge_module()
    if mrg is None:
        print("  note: Mesin_Merge (merge_draft_to_docx) not importable; writing guards skipped.")
        return
    draft_path = _locate_draft()
    if draft_path is None:
        print("  note: draft 'Tugas_Akhir_Draft.md' not found; writing guards skipped.")
        return
    try:
        if hasattr(mrg, "_load_draft_text"):
            draft_text = mrg._load_draft_text(draft_path)
        else:
            with open(draft_path, encoding="utf-8") as f:
                draft_text = f.read()
    except (OSError, ValueError) as e:
        print(f"  note: could not read draft '{draft_path}': {e}; writing guards skipped.")
        return
    draft_lines = draft_text.splitlines()

    # Parsed items feed the heading-level (R6.1) and BAB-order (R6.2) guards.
    items = []
    try:
        items = mrg.parse_markdown(draft_path)
    except Exception as e:
        print(f"  note: parse_markdown failed ({e}); heading/BAB guards skipped.")

    guard_warnings = []
    for fn, arg in (
        ("collect_heading_level_warnings", items),        # R6.1
        ("collect_bab_order_warnings", items),            # R6.2
        ("collect_unclosed_table_warnings", draft_lines), # R6.4
        ("collect_unbalanced_emphasis_warnings", draft_lines),  # R6.5
    ):
        try:
            guard_warnings.extend(getattr(mrg, fn)(arg))
        except Exception:
            pass

    for w in guard_warnings:
        print(w)

    # Citation cross-check (R1.5/1.6/6.3). Two-way: in-text citation -> entry and
    # entry -> citation. Default non-fatal; fatal only when configured (R1.7).
    fatal = _citation_fatal_enabled()
    cite_warnings = []
    try:
        bib = mrg.parse_bibliography_entries(draft_text)
        entries = list(getattr(bib, "entries", bib) or [])
        # Narrative body = draft up to the '# DAFTAR PUSTAKA' heading so the
        # bibliography's own '(YYYY)' tokens are not mistaken for citations.
        body_text = draft_text
        for i, line in enumerate(draft_lines):
            if re.match(r'^#{1,6}\s+DAFTAR\s+PUSTAKA\b', line.strip(), re.IGNORECASE):
                body_text = "\n".join(draft_lines[:i])
                break
        cite_warnings, has_fatal = mrg.collect_citation_crosscheck_warnings(
            body_text, entries, fatal=fatal)
        for w in cite_warnings:
            print(w)
        if has_fatal:
            # R1.7: configured fatal -> mismatches become fatal findings.
            for w in cite_warnings:
                errors_found.append(w)
    except Exception as e:
        print(f"  note: citation cross-check skipped ({e}).")

    mode = "FATAL" if fatal else "non-fatal"
    print(
        f"Writing guards: {len(guard_warnings)} structural warning(s) (non-fatal); "
        f"citation cross-check ({mode}): {len(cite_warnings)} mismatch(es)."
    )


def main():
    # Force UTF-8 encoding for stdout
    sys.stdout.reconfigure(encoding='utf-8')
    
    docx_path = "Tugas_Akhir_Formatted.docx"
    if len(sys.argv) > 1:
        docx_path = sys.argv[1]
        
    print(f"=== Starting automated validation on: {docx_path} ===")
    if not os.path.exists(docx_path):
        print(f"Error: {docx_path} does not exist.")
        sys.exit(1)
        
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    
    try:
        with zipfile.ZipFile(docx_path) as z:
            doc_xml = z.read("word/document.xml")
            styles_xml = z.read("word/styles.xml")
            document_rels_xml = z.read("word/_rels/document.xml.rels")
            page_parts = {
                name: ET.fromstring(z.read(name))
                for name in z.namelist()
                if name.startswith((
                    'word/header',
                    'word/footer',
                    'word/ta-header',
                    'word/ta-footer',
                ))
            }
            font_xml_parts = {
                name: z.read(name)
                for name in z.namelist()
                if name.startswith('word/')
                and name.endswith('.xml')
                and name != 'word/fontTable.xml'
            }
    except Exception as e:
        print(f"Error: Failed to open zip or read XML from {docx_path}: {e}")
        sys.exit(1)
        
    doc_root = ET.fromstring(doc_xml)
    styles_root = ET.fromstring(styles_xml)
    document_rels_root = ET.fromstring(document_rels_xml)
    
    # 1. Validate taappendixheading style in styles.xml
    print("Checking styles.xml for taappendixheading...")
    appendix_style = styles_root.find("w:style[@w:styleId='taappendixheading']", namespaces)
    if appendix_style is None:
        appendix_style = styles_root.find("w:style[@w:styleId='taappendixheading']", namespaces)
        
    if appendix_style is None:
        print("ERROR: taappendixheading style not found in styles.xml")
        sys.exit(1)
        
    style_pPr = appendix_style.find("w:pPr", namespaces)
    if style_pPr is not None:
        outlineLvl = style_pPr.find("w:outlineLvl", namespaces)
        if outlineLvl is None:
            print("ERROR: taappendixheading style is missing w:outlineLvl. It needs to have outline level 8 to map to TOC level 9.")
            sys.exit(1)
        val = outlineLvl.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') or outlineLvl.get('val')
        if val != '8':
            print(f"ERROR: taappendixheading style outlineLvl value is '{val}' (should be '8' to map to level 9 and isolate from main TOC).")
            sys.exit(1)
            
    print("SUCCESS: taappendixheading style is correctly defined with outline level 8.")
    
    # 1.1 Validate TOC9 style in styles.xml
    print("Checking styles.xml for TOC9 style...")
    toc9_style = styles_root.find("w:style[@w:styleId='TOC9']", namespaces)
    if toc9_style is None:
        print("ERROR: TOC9 style not found in styles.xml")
        sys.exit(1)
        
    toc9_pPr = toc9_style.find("w:pPr", namespaces)
    if toc9_pPr is not None:
        toc9_ind = toc9_pPr.find("w:ind", namespaces)
        if toc9_ind is None:
            print("ERROR: TOC9 style is missing indentation definition (w:ind).")
            sys.exit(1)
        left_val = toc9_ind.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}left') or toc9_ind.get('left')
        if left_val != '1':
            print(f"ERROR: TOC9 indentation has left='{left_val}' (should be '1' to prevent Word from stripping it).")
            sys.exit(1)
            
    print("SUCCESS: TOC9 style is correctly defined with left='1' (visually zero) indentation.")
    
    # 2. Iterate paragraphs and perform checks
    body = doc_root.find('w:body', namespaces)
    if body is None:
        print("ERROR: body element not found in document.xml")
        sys.exit(1)
        
    # Find Section 2 start index (PENDAHULUAN Heading1) to isolate front matter
    p_list = list(body.findall('.//w:p', namespaces))
    bab1_idx = -1
    for idx, p in enumerate(p_list):
        pPr = p.find('w:pPr', namespaces)
        pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
        pStyle_val = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if pStyle is not None else ""
        text = "".join([t.text for t in p.findall('.//w:t', namespaces) if t.text]).strip()
        if pStyle_val in ['Heading1', 'heading1'] and 'PENDAHULUAN' in text.upper():
            bab1_idx = idx
            break
            
    print(f"Section 2 (PENDAHULUAN) starts at paragraph index {bab1_idx}")
    
    print("Iterating paragraphs for structure validation...")
    
    errors_found = []
    print("Checking Times New Roman usage and approved bold roles...")
    errors_found.extend(validate_times_new_roman_fonts(font_xml_parts))
    errors_found.extend(validate_body_bold_usage(doc_root))
    print("Checking A4 page size and campus margins on every section...")
    layout_errors = validate_page_layout(doc_root)
    errors_found.extend(layout_errors)
    if not layout_errors:
        print(
            "SUCCESS: All sections use A4 portrait with left=4 cm and "
            "top/right/bottom=3 cm."
        )
    print("Checking Roman/Arabic page numbering and first-page placement...")
    page_number_errors = validate_page_numbering(
        doc_root,
        document_rels_root,
        page_parts,
    )
    errors_found.extend(page_number_errors)
    if not page_number_errors:
        print(
            "SUCCESS: Roman pages are bottom-right; BAB opening pages are "
            "bottom-center; continuation pages are top-right; BAB I restarts at 1."
        )
    print("Checking main paragraph styles for 1.15 line spacing...")
    spacing_errors = validate_main_line_spacing(styles_root)
    errors_found.extend(spacing_errors)
    if not spacing_errors:
        print("SUCCESS: Body, heading, list, and automatic-list styles use 1.15 spacing.")
    print("Checking stable figure/table bookmarks and REF fields...")
    crossref_errors = validate_semantic_cross_references(doc_root)
    errors_found.extend(crossref_errors)
    if not crossref_errors:
        print("SUCCESS: Stable caption bookmarks and semantic REF fields are valid.")
    first_gambar_checked = False
    gambar_count = 0
    tabel_count = 0
    
    for idx, p in enumerate(p_list):
        pPr = p.find('w:pPr', namespaces)
        pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
        pStyle_val = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if pStyle is not None else ""
        
        # Get text of the paragraph
        text = "".join([t.text for t in p.findall('.//w:t', namespaces) if t.text]).strip()
        
        # A. Check for Word field error text (on all paragraphs)
        for err_str in [
            "Error! Hyperlink reference not valid",
            "No table of figures entries found",
            "No table of contents entries found",
            "Error! Bookmark not defined",
            "Error! Reference source not found"
        ]:
            if err_str.lower() in text.lower():
                errors_found.append(f"Paragraph {idx} contains Word field error '{err_str}': '{text}'")
                
        # B. Check Appendix paragraphs (only in body/appendix section)
        is_in_body = (bab1_idx == -1 or idx >= bab1_idx)
        
        if is_in_body and text.upper().startswith("LAMPIRAN"):
            # Ensure style is taappendixheading
            if pStyle_val not in ["taappendixheading"]:
                errors_found.append(f"Appendix paragraph {idx} '{text}' has incorrect style '{pStyle_val}' (should be taappendixheading)")
            # Ensure no w:numPr
            if pPr is not None:
                numPr = pPr.find('w:numPr', namespaces)
                if numPr is not None:
                    errors_found.append(f"Appendix paragraph {idx} '{text}' has w:numPr auto-numbering, which should be stripped.")
                    
        # C. Check Captions (Gambar / Tabel) - only check actual captions in body section
        is_caption = (pStyle_val == 'Caption')
        is_gambar_prefix = re.match(r'^Gambar\s+[0-9]', text, re.IGNORECASE)
        is_tabel_prefix = re.match(r'^Tabel\s+[0-9]', text, re.IGNORECASE)
        
        if is_in_body and (is_caption or is_gambar_prefix or is_tabel_prefix):
            instrs = [t.text.strip() for t in p.findall('.//w:instrText', namespaces) if t.text]
            instr_str = " ".join(instrs)
            
            if is_gambar_prefix or (is_caption and text.lower().startswith("gambar")):
                gambar_count += 1
                # Must contain SEQ Gambar
                if "SEQ Gambar" not in instr_str:
                    errors_found.append(f"Gambar caption {idx} '{text}' is missing 'SEQ Gambar' field. Instrs: '{instr_str}'")
                # First Gambar (Gambar 2.1) must have restart switch \r 1
                is_first_gambar = re.match(r'^Gambar\s+2\.1\b', text, re.IGNORECASE)
                if is_first_gambar or not first_gambar_checked:
                    if is_first_gambar and "\\r 1" not in instr_str:
                        errors_found.append(f"First Gambar caption {idx} '{text}' is missing restart switch '\\r 1'. Instrs: '{instr_str}'")
                    if is_first_gambar:
                        first_gambar_checked = True
                        
            elif is_tabel_prefix or (is_caption and text.lower().startswith("tabel")):
                tabel_count += 1
                # Must contain SEQ Tabel
                if "SEQ Tabel" not in instr_str:
                    errors_found.append(f"Tabel caption {idx} '{text}' is missing 'SEQ Tabel' field. Instrs: '{instr_str}'")
                # First table of each chapter (e.g. 1.1, 2.1, 3.1) must have restart switch \r 1
                m = re.match(r'^Tabel\s+[0-9]+\.1\b', text, re.IGNORECASE)
                if m and "\\r 1" not in instr_str:
                    errors_found.append(f"First Table of chapter {idx} '{text}' is missing restart switch '\\r 1'. Instrs: '{instr_str}'")
                    
        # D. Check Daftar Lampiran TOC (only in front matter or body)
        if "DAFTAR LAMPIRAN" in text.upper() and pStyle_val in ["Heading1", "heading1"] and not text.endswith("7"):
            found_lampiran_toc_field = False
            for j in range(idx + 1, min(idx + 6, len(p_list))):
                next_p = p_list[j]
                next_p_instrs = [t.text.strip() for t in next_p.findall('.//w:instrText', namespaces) if t.text]
                next_p_instr_str = " ".join(next_p_instrs)
                if "TOC" in next_p_instr_str and ("9-9" in next_p_instr_str) and ("\\n 9-9" in next_p_instr_str):
                    found_lampiran_toc_field = True
                    print(f"SUCCESS: Found Daftar Lampiran TOC field at paragraph {j}: '{next_p_instr_str}'")
                    break
            if not found_lampiran_toc_field:
                errors_found.append(f"DAFTAR LAMPIRAN heading at paragraph {idx} is not followed by a TOC field targeting level 9-9.")
                
        # E. Check for consecutive figure captions without intervening drawings or descriptions
        if is_in_body and is_gambar_prefix:
            found_consecutive_caption = False
            for j in range(idx - 1, -1, -1):
                prev_p = p_list[j]
                prev_pPr = prev_p.find('w:pPr', namespaces)
                prev_pStyle = prev_pPr.find('w:pStyle', namespaces) if prev_pPr is not None else None
                prev_pStyle_val = prev_pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if prev_pStyle is not None else ""
                prev_text = "".join([t.text for t in prev_p.findall('.//w:t', namespaces) if t.text]).strip()
                
                if not prev_text and prev_p.find('.//w:drawing', namespaces) is None:
                    continue
                    
                if prev_p.find('.//w:drawing', namespaces) is not None:
                    break
                    
                prev_is_gambar_prefix = re.match(r'^Gambar\s+[0-9]', prev_text, re.IGNORECASE)
                if prev_pStyle_val == 'Caption' or prev_is_gambar_prefix:
                    if "sequence diagram" in text.lower() or "sequence diagram" in prev_text.lower():
                        pass
                    else:
                        found_consecutive_caption = True
                        break
                    
                break
                
            if found_consecutive_caption:
                errors_found.append(f"Consecutive figure captions found: Paragraph {idx} '{text}' is preceded by another caption without an intervening drawing.")

    print(f"Processed {gambar_count} Gambar captions and {tabel_count} Tabel captions.")
    
    # F. Verify keepNext+keepLines chain on ALL drawing paragraphs in body
    print("Checking keepNext/keepLines chain on drawing paragraphs...")
    for idx, p in enumerate(p_list):
        is_in_body = (bab1_idx == -1 or idx >= bab1_idx)
        if not is_in_body:
            continue
        has_drawing = p.find('.//w:drawing', namespaces) is not None
        if has_drawing:
            pPr = p.find('w:pPr', namespaces)
            has_keepNext = pPr is not None and pPr.find('w:keepNext', namespaces) is not None
            has_keepLines = pPr is not None and pPr.find('w:keepLines', namespaces) is not None
            if not has_keepNext:
                errors_found.append(f"Drawing paragraph {idx} is missing w:keepNext (image may split from caption)")
            if not has_keepLines:
                errors_found.append(f"Drawing paragraph {idx} is missing w:keepLines (image may split across pages)")
    
    # G. Verify every Gambar caption is immediately preceded by a drawing paragraph
    print("Checking drawing-before-caption adjacency...")
    for idx, p in enumerate(p_list):
        is_in_body = (bab1_idx == -1 or idx >= bab1_idx)
        if not is_in_body:
            continue
        pPr = p.find('w:pPr', namespaces)
        pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
        pStyle_val = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if pStyle is not None else ""
        text = "".join([t.text for t in p.findall('.//w:t', namespaces) if t.text]).strip()
        
        is_gambar_prefix = re.match(r'^Gambar\s+[0-9]', text, re.IGNORECASE)
        if is_gambar_prefix or (pStyle_val == 'Caption' and text.lower().startswith('gambar')):
            # Look backwards for the nearest drawing paragraph, skipping empty paragraphs
            found_drawing = False
            for j in range(idx - 1, max(idx - 3, -1), -1):
                prev_p = p_list[j]
                prev_text = "".join([t.text for t in prev_p.findall('.//w:t', namespaces) if t.text]).strip()
                if prev_p.find('.//w:drawing', namespaces) is not None:
                    found_drawing = True
                    break
                if prev_text:
                    # Non-empty non-drawing paragraph between drawing and caption = error
                    break
            if not found_drawing:
                # Exception: sequence diagram captions can be consecutive without intervening drawings
                if "sequence diagram" not in text.lower():
                    errors_found.append(f"Gambar caption at paragraph {idx} '{text}' is NOT immediately preceded by a drawing paragraph")
                    
    # I/J. Verify every Gambar caption paragraph has keepNext and keepLines
    print("Checking keepNext/keepLines on Gambar captions...")
    for idx, p in enumerate(p_list):
        is_in_body = (bab1_idx == -1 or idx >= bab1_idx)
        if not is_in_body:
            continue
        pPr = p.find('w:pPr', namespaces)
        pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
        pStyle_val = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if pStyle is not None else ""
        text = "".join([t.text for t in p.findall('.//w:t', namespaces) if t.text]).strip()
        
        is_gambar_prefix = re.match(r'^Gambar\s+[0-9]', text, re.IGNORECASE)
        if is_gambar_prefix or (pStyle_val == 'Caption' and text.lower().startswith('gambar')):
            has_keepNext = pPr is not None and pPr.find('w:keepNext', namespaces) is not None
            has_keepLines = pPr is not None and pPr.find('w:keepLines', namespaces) is not None
            if not has_keepNext:
                errors_found.append(f"Gambar caption {idx} '{text}' is missing w:keepNext (may split from following paragraph)")
            if not has_keepLines:
                errors_found.append(f"Gambar caption {idx} '{text}' is missing w:keepLines (caption may split across pages)")
    
    # H. Check for orphan code text outside code-styled paragraphs
    # After font normalization, code blocks have: sz=24 (12pt) + ind left=720, no Consolas.
    # Keep sz=18 as a compatibility fallback for older fixture documents.
    print("Checking for orphan code text outside code blocks...")
    code_markers = ['$$ LANGUAGE plpgsql', 'CREATE TRIGGER', 'CREATE OR REPLACE FUNCTION',
                    'EXECUTE FUNCTION', 'RETURNS TRIGGER AS $$']
    ns_w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    for idx, p in enumerate(p_list):
        is_in_body = (bab1_idx == -1 or idx >= bab1_idx)
        if not is_in_body:
            continue
        pPr = p.find('w:pPr', namespaces)
        pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
        pStyle_val = pStyle.get(f'{{{ns_w}}}val') if pStyle is not None else ""
        if 'code' in pStyle_val.lower():
            continue
        # Detect code block by sz=24 (12pt) + ind left=720
        is_code_block = False
        ind_elem = pPr.find('w:ind', namespaces) if pPr is not None else None
        left_val = ind_elem.get(f'{{{ns_w}}}left', '0') if ind_elem is not None else '0'
        if left_val == '720':
            for sz_el in p.findall('.//w:sz', namespaces):
                if sz_el.get(f'{{{ns_w}}}val') in {'24', '18'}:
                    is_code_block = True
                    break
        # Also check for Consolas font (pre-normalization)
        if not is_code_block:
            for rFonts in p.findall('.//w:rFonts', namespaces):
                av = rFonts.get(f'{{{ns_w}}}ascii', '')
                if av.lower() in ['consolas', 'courier new', 'courier']:
                    is_code_block = True
                    break
        if is_code_block:
            continue
        text = "".join([t.text for t in p.findall('.//w:t', namespaces) if t.text]).strip()
        for marker in code_markers:
            if marker in text:
                errors_found.append(f"Paragraph {idx} contains code text '{marker}' outside code block (style='{pStyle_val}')")
    
    # ============================================================ #
    # Content-level figure checks (C1-C4).
    #
    # These ADD failures only; Sections A-J above remain unchanged and run
    # first. None of the checks below short-circuits the build via sys.exit:
    # every defect is appended to errors_found so the final report lists all
    # of them and the process exits non-zero at the end.
    # ============================================================ #
    print("Checking content-level figure invariants (C1 uniqueness, C2 resolution, C3 integrity, C4 page-split)...")

    # Load the manifest + reconciliation allow-lists (BOM tolerant, utf-8-sig).
    manifest_path = os.path.join("images", "manifest.json")
    reconcile_path = os.path.join("images", "manifest_reconcile.json")
    post_com_items = []
    duplicate_allow_groups = []
    unresolved_allow = set()
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8-sig") as f:
            manifest = json.load(f)
        post_com_items = [it for it in manifest.get("images", [])
                          if it.get("inject_method") == "post_com"]
    else:
        errors_found.append(
            f"[content] manifest not found at '{manifest_path}'; cannot run content-level checks.")
    if os.path.exists(reconcile_path):
        with open(reconcile_path, "r", encoding="utf-8-sig") as f:
            rec = json.load(f)
        duplicate_allow_groups = [set(g) for g in rec.get("duplicate_content_allow", [])]
        unresolved_allow = set(rec.get("unresolved_allow", []))

    # Read packed media bytes + the document relationship targets.
    media_bytes = {}
    rel_target = {}
    content_type_defaults = {}
    content_type_overrides = {}
    rels_xml = None
    try:
        with zipfile.ZipFile(docx_path) as z:
            for n in z.namelist():
                if n.startswith("word/media/"):
                    media_bytes[n] = z.read(n)
            try:
                rels_xml = z.read("word/_rels/document.xml.rels")
            except KeyError:
                rels_xml = None
            try:
                content_types_root = ET.fromstring(z.read("[Content_Types].xml"))
                for node in content_types_root:
                    if node.tag == f'{{{CONTENT_TYPES_NS}}}Default':
                        content_type_defaults[(node.get('Extension') or '').lower()] = (
                            node.get('ContentType') or ''
                        )
                    elif node.tag == f'{{{CONTENT_TYPES_NS}}}Override':
                        content_type_overrides[node.get('PartName') or ''] = (
                            node.get('ContentType') or ''
                        )
            except KeyError:
                errors_found.append(
                    "[C3/package] [Content_Types].xml is missing; Word cannot open the package."
                )
    except Exception as e:
        errors_found.append(f"[content] failed to read media/rels from package: {e}")
    if rels_xml is not None:
        rels_root = ET.fromstring(rels_xml)
        for rel in rels_root:
            rid = rel.get("Id")
            tgt = rel.get("Target")
            if rid and tgt:
                rel_target[rid] = tgt

    body_el = doc_root.find(f'{{{W_NS}}}body')

    # Per-entry exact-id resolution feeds C2 and C3, and
    # records the figure<->media mapping consumed by the C1 allow-list logic.
    target_to_figure = {}  # packed media name -> figure id (for allow-list mapping)
    for item in post_com_items:
        item_id = item.get("id", item.get("file", "<unknown>"))
        caption_match = item.get("caption_match", "")
        img_file = item.get("file", "")
        src_path = os.path.join("images", img_file)

        children, identity_matches = _resolve_figure_identity_content(body_el, item_id)
        _caption_children, caption_matches = _resolve_caption_indices_content(
            body_el, caption_match
        )
        count = len(identity_matches)

        # --- C2: one exact drawing id, one caption, and strict adjacency --- #
        if count != 1 or len(caption_matches) != 1:
            if (item_id in unresolved_allow and count == 0
                    and len(caption_matches) == 0):
                print(f"  note: [C2] entry '{item_id}' resolves to 0 figures/captions but is "
                      f"reconciled (unresolved_allow); intentionally skipped.")
                continue
            errors_found.append(
                f"[C2] entry '{item_id}' exact drawing identity 'FIGURE:{item_id}' resolved "
                f"to {count} drawing(s) and caption_match '{caption_match}' resolved to "
                f"{len(caption_matches)} caption(s); expected exactly one of each."
            )
            continue

        drawing_idx = identity_matches[0]
        caption_idx = caption_matches[0]
        if caption_idx != drawing_idx + 1:
            errors_found.append(
                f"[C2] entry '{item_id}' exact drawing 'FIGURE:{item_id}' is not "
                f"immediately followed by its caption '{caption_match}'."
            )
            continue

        # Map the exact-id drawing to its packed media.
        drawing_p = children[drawing_idx]
        media_name = _drawing_media(drawing_p, rel_target)
        if media_name is None:
            errors_found.append(
                f"[C3] entry '{item_id}' exact drawing resolves but its packed media "
                f"could not be located for content integrity verification."
            )
            continue
        target_to_figure[media_name] = item_id

        packed = media_bytes.get(media_name)
        if packed is None:
            errors_found.append(
                f"[C3] entry '{item_id}' references packed media '{media_name}' which is "
                f"absent from the package; cannot verify content integrity."
            )
            continue
        packed_md5 = _md5_bytes(packed)

        media_extension = posixpath.splitext(media_name)[1].lstrip('.').lower()
        media_part_name = '/' + media_name
        declared_media_type = (
            content_type_overrides.get(media_part_name)
            or content_type_defaults.get(media_extension)
        )
        if not declared_media_type or not declared_media_type.startswith('image/'):
            errors_found.append(
                f"[C3/package] entry '{item_id}' media '{media_name}' has no valid image "
                f"content type in [Content_Types].xml; Microsoft Word will reject the DOCX."
            )

        # --- C3: packed media MD5 == injected images/<file> MD5 ----------- #
        if os.path.exists(src_path):
            injected_md5 = _md5_file(src_path)
            if packed_md5 != injected_md5:
                errors_found.append(
                    f"[C3] entry '{item_id}' content integrity mismatch: packed '{media_name}' "
                    f"md5 {packed_md5} does not match injected '{src_path}' md5 {injected_md5} "
                    f"(content drift / recompression)."
                )
        else:
            errors_found.append(
                f"[C3] entry '{item_id}' injected file '{src_path}' is missing on disk; cannot "
                f"verify packed-vs-injected content integrity (md5)."
            )

        # Best-effort, NON-FATAL provenance note for the declared source.
        source = item.get("source")
        if source and os.path.exists(source):
            if _md5_file(source) != packed_md5:
                print(f"  note: [C3] entry '{item_id}' declared source '{source}' differs from "
                      f"the packed media (provenance only, not a failure).")

    # --- C1: media MD5 uniqueness across distinct drawing-referenced media - #
    print("Checking media MD5 uniqueness across injected drawings...")
    md5_to_targets = {}
    if body_el is not None:
        for p in body_el.findall(f'{{{W_NS}}}p'):
            if p.find(f'.//{{{W_NS}}}drawing') is None:
                continue
            blip = p.find(f'.//{{{A_NS}}}blip')
            if blip is None:
                continue
            target = rel_target.get(blip.get(f'{{{R_NS}}}embed'))
            if not target:
                continue
            media_name = 'word/' + target
            packed = media_bytes.get(media_name)
            if packed is None:
                continue
            md5_to_targets.setdefault(_md5_bytes(packed), set()).add(media_name)

    for md5val, targets in md5_to_targets.items():
        if len(targets) < 2:
            continue
        fig_ids = sorted(target_to_figure.get(t, t) for t in targets)
        # Allowed only if every involved figure appears together in one allow group.
        allowed = any(set(fig_ids).issubset(group) for group in duplicate_allow_groups)
        if not allowed:
            errors_found.append(
                f"[C1] duplicate media content: {sorted(targets)} (figures {fig_ids}) share "
                f"identical MD5 {md5val}; distinct figures must reference unique image content. "
                f"Reconcile legitimate reuse via duplicate_content_allow."
            )

    # --- C4: drawing and caption must remain on the same page. --- #
    page_height_threshold = _printable_height_emu_content(doc_root)
    print(
        "Checking page-split safety: drawing/caption same-page contract "
        f"(printable height {page_height_threshold} EMU, caption reserve "
        f"{FIGURE_CAPTION_RESERVE_EMU} EMU)..."
    )
    same_page_errors = collect_figure_same_page_errors(
        body_el, page_height_threshold
    )
    errors_found.extend(same_page_errors)
    if same_page_errors:
        for finding in same_page_errors:
            print(finding)
    else:
        print("SUCCESS: Every drawing and Gambar caption pair is constrained to one page.")

    # ============================================================ #
    # Figure narration guard (FATAL).
    #
    # Each figure must be explicitly mentioned by an ordinary narrative
    # paragraph in the same chapter, with the label placed mid-sentence.  A
    # missing/invalid mention is a campus-format violation and therefore blocks
    # the build instead of being silently tolerated as a warning.
    # ============================================================ #
    print("Checking figure narration references (fatal)...")
    narration_errors = collect_figure_narration_errors(p_list, bab1_idx)
    errors_found.extend(narration_errors)
    for finding in narration_errors:
        print(finding)
    if narration_errors:
        print(
            f"Narration check: {len(narration_errors)} figure(s) violate the "
            "mandatory narrative-reference rule."
        )
    else:
        print("SUCCESS: Every figure has an explicit mid-sentence narrative reference.")

    print("Checking citation punctuation (author and year without a comma)...")
    citation_format_errors = collect_citation_punctuation_errors(p_list, bab1_idx)
    errors_found.extend(citation_format_errors)
    for finding in citation_format_errors:
        print(finding)
    if not citation_format_errors:
        print("SUCCESS: In-text citations omit the comma before the year.")

    # ============================================================ #
    # Citation guard for Latar Belakang (WARNING ONLY -- never fatal).
    #
    # Academic rule (.kiro/steering/aturan-sitasi.md): the Latar Belakang is the
    # most citation-dense section -- every substantial factual-claim paragraph
    # should carry an APA in-text citation "(... Tahun)". Here we flag any
    # sizeable body paragraph inside the "Latar Belakang" subsection that has no
    # citation, unless it explicitly refers to the author's own data (kuesioner /
    # responden / Lampiran), which is cited to the author's own material instead.
    # This DOES NOT append to errors_found and DOES NOT change the exit code.
    # ============================================================ #
    print("Checking Latar Belakang citations (non-fatal warnings)...")
    CITATION_RE = re.compile(r'\([^()]*(?:19|20)\d{2}[a-z]?\)')
    SELF_DATA_RE = re.compile(r'kuesioner|responden|lampiran|gambar|tabel', re.I)

    def _is_heading(pp):
        return _content_style(pp).lower().startswith('heading')

    # Locate the "Latar Belakang" heading and the extent of its subsection
    # (until the next heading of any level).
    lb_start = -1
    for idx, p in enumerate(p_list):
        if _is_heading(p) and 'latar belakang' in _content_text(p).lower():
            lb_start = idx
            break
    citation_warnings = []
    if lb_start != -1:
        lb_end = len(p_list)
        for j in range(lb_start + 1, len(p_list)):
            if _is_heading(p_list[j]):
                lb_end = j
                break
        for j in range(lb_start + 1, lb_end):
            q = p_list[j]
            if _is_heading(q):
                continue
            style_val = _content_style(q)
            if style_val in ('Caption',) or style_val.startswith('TableofFigures'):
                continue
            if q.find(f'.//{{{W_NS}}}drawing') is not None:
                continue
            q_text = _content_text(q)
            # Only sizeable claim paragraphs (skip short transitions/list lines).
            if len(q_text) < 200:
                continue
            if CITATION_RE.search(q_text):
                continue
            if SELF_DATA_RE.search(q_text):
                continue
            citation_warnings.append(
                f"[WARN][sitasi] Paragraf Latar Belakang tanpa sitasi: '{q_text[:70]}...'")
    else:
        print("  note: 'Latar Belakang' heading not found; citation check skipped.")

    for w in citation_warnings:
        print(w)
    print(f"Citation check: {len(citation_warnings)} Latar Belakang paragraph(s) without a citation (non-fatal).")

    # ============================================================ #
    # Writing guards (R6) + citation cross-check (R1.5/1.6/6.3/1.7), additive.
    # Non-fatal by default; only the citation cross-check can turn fatal and
    # only when explicitly configured (TA_CITATION_FATAL=1 / --citation-fatal).
    # ============================================================ #
    _run_writing_guards(errors_found)

    # 3. Report results
    if errors_found:
        print("\n=== VALIDATION FAILED ===")
        for err in errors_found:
            print(f"- {err}")
        sys.exit(1)
    else:
        print("\n=== VALIDATION SUCCESSFUL: No regressions found! ===")
        sys.exit(0)

if __name__ == '__main__':
    main()
