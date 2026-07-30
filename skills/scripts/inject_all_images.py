import os
import sys
import copy
import json
import zipfile
import lxml.etree
import shutil
import struct
import hashlib
import re

# ------------------------------------------------------------------ #
# Shared BODY-figure bounding box (tunable). Every BODY figure is scaled to
# fit INSIDE this box while preserving aspect ratio (never upscaled, never
# cropped). 1 cm = 360000 EMU.
#   BODY_MAX_W_EMU = 14 cm, BODY_MAX_H_EMU = 16 cm.
# These MUST match format_ta_proyek.center_and_scale_drawings().
# ------------------------------------------------------------------ #
BODY_MAX_W_EMU = 5040000   # 14 cm; A4 width minus 4 cm left and 3 cm right
BODY_MAX_H_EMU = 5760000   # 16 cm
# Reserve enough printable height for a multi-line 12 pt caption plus its
# paragraph spacing.  C4 requires the drawing and caption to fit on one page.
# This value must match validate_docx_structure.py.
FIGURE_CAPTION_RESERVE_EMU = 1080000  # 3 cm

# Legacy alias kept only as the printable-height fallback below.
MAX_WIDTH = BODY_MAX_W_EMU
# 1 twip = 635 EMU (used to derive the printable page height threshold for C4).
EMU_PER_TWIP = 635

WORD_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
REL_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'
CONTENT_TYPES_NS = 'http://schemas.openxmlformats.org/package/2006/content-types'
FIGURE_MARKER_PREFIX = '[FIGURE:'

# Default reconciliation file (shared with the validator). Lists are empty by
# default so every duplicate-content (C1) and unresolved-caption (C2) defect
# remains detectable; only legitimate reuse/omission is allow-listed here.
RECONCILE_PATH = os.path.join("images", "manifest_reconcile.json")


def md5_file(filepath):
    """Return the hex MD5 of a file's bytes."""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def load_reconcile(path=RECONCILE_PATH):
    """Load the reconciliation allow-lists. Missing file => empty allow-lists."""
    duplicate_allow_groups = []
    unresolved_allow = set()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        duplicate_allow_groups = [set(group) for group in data.get("duplicate_content_allow", [])]
        unresolved_allow = set(data.get("unresolved_allow", []))
    return duplicate_allow_groups, unresolved_allow


def load_italic_terms(path="term_registry.json"):
    """Load technical terms that must remain italic after Word COM updates."""
    if not os.path.exists(path):
        return ()
    try:
        with open(path, "r", encoding="utf-8-sig") as handle:
            payload = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return ()
    terms = payload.get("italic_terms", [])
    if not isinstance(terms, list):
        return ()
    cleaned = {
        term.strip()
        for term in terms
        if isinstance(term, str) and term.strip()
    }
    return tuple(sorted(cleaned, key=lambda term: (-len(term), term.casefold())))


def _set_direct_run_typography(
        run, *, bold=None, italic=None, size=None, color=None):
    """Set deterministic Times New Roman properties on one OOXML run."""
    r_pr = run.find(f'{{{WORD_NS}}}rPr')
    if r_pr is None:
        r_pr = lxml.etree.Element(f'{{{WORD_NS}}}rPr')
        run.insert(0, r_pr)

    fonts = r_pr.find(f'{{{WORD_NS}}}rFonts')
    if fonts is None:
        fonts = lxml.etree.SubElement(r_pr, f'{{{WORD_NS}}}rFonts')
    for attr in ('ascii', 'hAnsi', 'eastAsia', 'cs'):
        fonts.set(f'{{{WORD_NS}}}{attr}', 'Times New Roman')
    for attr in ('asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme'):
        fonts.attrib.pop(f'{{{WORD_NS}}}{attr}', None)

    if size is not None:
        for local_name in ('sz', 'szCs'):
            element = r_pr.find(f'{{{WORD_NS}}}{local_name}')
            if element is None:
                element = lxml.etree.SubElement(r_pr, f'{{{WORD_NS}}}{local_name}')
            element.set(f'{{{WORD_NS}}}val', str(size))
    if color is not None:
        color_element = r_pr.find(f'{{{WORD_NS}}}color')
        if color_element is None:
            color_element = lxml.etree.SubElement(
                r_pr, f'{{{WORD_NS}}}color'
            )
        color_element.set(f'{{{WORD_NS}}}val', color)

    for local_name, enabled in (
            ('b', bold), ('bCs', bold), ('i', italic), ('iCs', italic)):
        if enabled is None:
            continue
        element = r_pr.find(f'{{{WORD_NS}}}{local_name}')
        if enabled:
            if element is None:
                lxml.etree.SubElement(r_pr, f'{{{WORD_NS}}}{local_name}')
            else:
                element.attrib.pop(f'{{{WORD_NS}}}val', None)
        else:
            if element is None:
                element = lxml.etree.SubElement(
                    r_pr, f'{{{WORD_NS}}}{local_name}'
                )
            element.set(f'{{{WORD_NS}}}val', '0')
    return r_pr


def _ensure_word_child(parent, local_name, attributes=None):
    """Return one direct Word child and deterministically replace its attrs."""
    child = parent.find(f'{{{WORD_NS}}}{local_name}')
    if child is None:
        child = lxml.etree.SubElement(parent, f'{{{WORD_NS}}}{local_name}')
    if attributes is not None:
        child.attrib.clear()
        for name, value in attributes.items():
            child.set(f'{{{WORD_NS}}}{name}', str(value))
    return child


def _set_paragraph_indent(paragraph, *, left, first_line):
    """Reassert a direct paragraph indent in schema-valid child order."""
    q = lambda local_name: f'{{{WORD_NS}}}{local_name}'
    paragraph_properties = paragraph.find(q('pPr'))
    if paragraph_properties is None:
        paragraph_properties = lxml.etree.Element(q('pPr'))
        paragraph.insert(0, paragraph_properties)

    indent = paragraph_properties.find(q('ind'))
    if indent is None:
        indent = lxml.etree.Element(q('ind'))
        later_property_tags = {
            q('contextualSpacing'), q('mirrorIndents'), q('suppressOverlap'),
            q('jc'), q('textDirection'), q('textAlignment'),
            q('textboxTightWrap'), q('outlineLvl'), q('divId'), q('cnfStyle'),
            q('rPr'), q('sectPr'),
        }
        insertion_index = next((
            index for index, child in enumerate(paragraph_properties)
            if child.tag in later_property_tags
        ), len(paragraph_properties))
        paragraph_properties.insert(insertion_index, indent)

    indent.attrib.clear()
    indent.set(q('left'), str(left))
    indent.set(q('firstLine'), str(first_line))


def _restore_preface_indentation(
        paragraphs, texts, expected_acknowledgements=8):
    """Restore Kata Pengantar indentation removed by Microsoft Word COM."""
    try:
        heading_index = texts.index('KATA PENGANTAR')
        boundary_index = texts.index('DAFTAR ISI', heading_index + 1)
    except ValueError:
        return {
            'opening': 0, 'acknowledgements': 0,
            'closing': 0, 'signoff': 0,
        }

    content = [
        (index, paragraphs[index], texts[index])
        for index in range(heading_index + 1, boundary_index)
        if texts[index]
    ]
    acknowledgement_positions = [
        position for position, (_, _, text) in enumerate(content)
        if re.match(r'^\d+\.\s+', text)
    ]
    expected_labels = [
        int(re.match(r'^(\d+)\.', content[position][2]).group(1))
        for position in acknowledgement_positions
    ]
    if (
        expected_labels != list(range(1, expected_acknowledgements + 1))
        or acknowledgement_positions != list(range(
            acknowledgement_positions[0],
            acknowledgement_positions[0] + expected_acknowledgements,
        ))
    ):
        return {
            'opening': 0, 'acknowledgements': 0,
            'closing': 0, 'signoff': 0,
        }

    first_acknowledgement = acknowledgement_positions[0]
    last_acknowledgement = acknowledgement_positions[-1]
    opening = content[:first_acknowledgement]
    acknowledgements = [content[position] for position in acknowledgement_positions]
    trailing = content[last_acknowledgement + 1:]
    if len(opening) != 2 or len(trailing) != 4:
        return {
            'opening': 0, 'acknowledgements': 0,
            'closing': 0, 'signoff': 0,
        }

    closing = trailing[:1]
    signoff = trailing[1:]
    for _, paragraph, _ in opening + closing:
        _set_paragraph_indent(paragraph, left=0, first_line=567)
    for _, paragraph, _ in acknowledgements + signoff:
        _set_paragraph_indent(paragraph, left=0, first_line=0)
    for _, paragraph, _ in signoff:
        paragraph_properties = paragraph.find(f'{{{WORD_NS}}}pPr')
        _ensure_word_child(paragraph_properties, 'jc', {'val': 'right'})

    return {
        'opening': len(opening),
        'acknowledgements': len(acknowledgements),
        'closing': len(closing),
        'signoff': len(signoff),
    }


def restore_front_matter_after_com(
        doc_root, styles_root, expected_acknowledgements=8):
    """Restore front-matter style IDs and direct abstract typography.

    Microsoft Word lowercases the custom ``FrontMatterHeading`` style ID and
    removes direct font/size properties that match the surrounding defaults
    when it updates fields.  The report validator intentionally requires the
    canonical style ID and explicit 12 pt Times New Roman runs so the output is
    deterministic across Word installations.  Re-assert those properties in
    the post-COM pass, after every field has already been refreshed.
    """
    q = lambda local_name: f'{{{WORD_NS}}}{local_name}'
    canonical_style_id = 'FrontMatterHeading'

    style = None
    for candidate in styles_root.findall(q('style')):
        style_id = candidate.get(q('styleId'), '')
        if style_id.casefold() == canonical_style_id.casefold():
            style = candidate
            break
    if style is None:
        style = lxml.etree.SubElement(styles_root, q('style'))
    style.set(q('type'), 'paragraph')
    style.set(q('styleId'), canonical_style_id)
    _ensure_word_child(style, 'name', {'val': 'front matter heading'})
    _ensure_word_child(style, 'basedOn', {'val': 'Normal'})
    _ensure_word_child(style, 'next', {'val': 'Normal'})
    _ensure_word_child(style, 'qFormat', {})

    paragraph_properties = _ensure_word_child(style, 'pPr')
    _ensure_word_child(paragraph_properties, 'keepNext', {})
    _ensure_word_child(paragraph_properties, 'keepLines', {})
    _ensure_word_child(paragraph_properties, 'spacing', {
        'before': '0', 'after': '240', 'line': '276', 'lineRule': 'auto',
    })
    _ensure_word_child(paragraph_properties, 'jc', {'val': 'center'})
    _ensure_word_child(paragraph_properties, 'outlineLvl', {'val': '0'})

    run_properties = _ensure_word_child(style, 'rPr')
    _ensure_word_child(run_properties, 'rFonts', {
        'ascii': 'Times New Roman', 'hAnsi': 'Times New Roman',
        'eastAsia': 'Times New Roman', 'cs': 'Times New Roman',
    })
    _ensure_word_child(run_properties, 'b', {})
    _ensure_word_child(run_properties, 'bCs', {})
    _ensure_word_child(run_properties, 'sz', {'val': '24'})
    _ensure_word_child(run_properties, 'szCs', {'val': '24'})
    _ensure_word_child(run_properties, 'color', {'val': '000000'})

    paragraph_style_updates = 0
    paragraphs = list(doc_root.iter(q('p')))
    texts = [
        ''.join(node.text or '' for node in paragraph.iter(q('t'))).strip()
        for paragraph in paragraphs
    ]
    for paragraph in paragraphs:
        paragraph_style = paragraph.find(f"{q('pPr')}/{q('pStyle')}")
        if paragraph_style is None:
            continue
        value = paragraph_style.get(q('val'), '')
        if value.casefold() != canonical_style_id.casefold():
            continue
        if value != canonical_style_id:
            paragraph_style.set(q('val'), canonical_style_id)
            paragraph_style_updates += 1

    normalized_runs = 0
    for heading, keyword_label in (
            ('ABSTRAK', 'Kata kunci:'), ('ABSTRACT', 'Keywords:')):
        try:
            heading_index = texts.index(heading)
        except ValueError:
            continue
        content_indices = [
            index for index in range(heading_index + 1, len(paragraphs))
            if texts[index]
        ]
        if len(content_indices) < 2:
            continue
        body_paragraph = paragraphs[content_indices[0]]
        keyword_paragraph = paragraphs[content_indices[1]]

        for run in body_paragraph.findall(q('r')):
            if not ''.join(node.text or '' for node in run.iter(q('t'))):
                continue
            _set_direct_run_typography(run, bold=False, size=24, color='000000')
            normalized_runs += 1

        keyword_runs = [
            run for run in keyword_paragraph.findall(q('r'))
            if ''.join(node.text or '' for node in run.iter(q('t')))
        ]
        for index, run in enumerate(keyword_runs):
            run_text = ''.join(node.text or '' for node in run.iter(q('t')))
            is_label = index == 0 and keyword_label in run_text
            _set_direct_run_typography(
                run, bold=is_label, size=24, color='000000'
            )
            normalized_runs += 1

    preface = _restore_preface_indentation(
        paragraphs, texts, expected_acknowledgements
    )

    return {
        'paragraph_styles': paragraph_style_updates,
        'runs': normalized_runs,
        'preface': preface,
    }


def restore_identity_footer_after_com(temp_dir, identity_footer):
    """Restore explicit footer typography stripped by the Word COM save."""
    if not identity_footer:
        return 0
    expected = {
        identity_footer['author_year']: (True, False),
        identity_footer['title']: (True, True),
        identity_footer['institution']: (False, False),
        identity_footer['links']: (False, False),
    }
    normalized = 0
    word_dir = os.path.join(temp_dir, 'word')
    for filename in os.listdir(word_dir):
        if not re.fullmatch(r'footer\d+\.xml', filename, re.IGNORECASE):
            continue
        path = os.path.join(word_dir, filename)
        tree = lxml.etree.parse(path)
        root = tree.getroot()
        changed = False
        for run in root.iter(f'{{{WORD_NS}}}r'):
            text = ''.join(
                node.text or ''
                for node in run.findall(f'{{{WORD_NS}}}t')
            )
            if text not in expected:
                continue
            _set_direct_run_typography(
                run,
                bold=expected[text][0],
                italic=expected[text][1],
                size=round(float(identity_footer.get('size_pt', 8)) * 2),
                color='000000',
            )
            normalized += 1
            changed = True
        if changed:
            tree.write(path, encoding='utf-8', xml_declaration=True)
    return normalized


def normalize_caption_typography(doc_root):
    """Keep caption labels/numbers bold and descriptions selectively regular."""
    namespaces = {'w': WORD_NS}
    normalized = 0
    for paragraph in doc_root.iter(f'{{{WORD_NS}}}p'):
        style = paragraph.find('w:pPr/w:pStyle', namespaces)
        if style is None or style.get(f'{{{WORD_NS}}}val') != 'Caption':
            continue
        paragraph_text = ''.join(
            node.text or '' for node in paragraph.iter(f'{{{WORD_NS}}}t')
        ).strip()
        if not re.match(r'^(Gambar|Tabel)\s', paragraph_text, re.IGNORECASE):
            continue

        runs = paragraph.findall('w:r', namespaces)
        instruction_index = next((
            index for index, run in enumerate(runs)
            if 'SEQ Gambar' in ''.join(run.itertext())
            or 'SEQ Tabel' in ''.join(run.itertext())
        ), None)
        if instruction_index is None:
            continue

        begin_index = instruction_index
        for index in range(instruction_index, -1, -1):
            field = runs[index].find('w:fldChar', namespaces)
            if field is not None and field.get(f'{{{WORD_NS}}}fldCharType') == 'begin':
                begin_index = index
                break

        end_index = instruction_index
        for index in range(instruction_index, len(runs)):
            field = runs[index].find('w:fldChar', namespaces)
            if field is not None and field.get(f'{{{WORD_NS}}}fldCharType') == 'end':
                end_index = index
                break

        for run in runs[:begin_index]:
            if ''.join(node.text or '' for node in run.findall('w:t', namespaces)):
                _set_direct_run_typography(
                    run, bold=True, italic=False, size='24', color='000000'
                )
        for run in runs[begin_index:end_index + 1]:
            _set_direct_run_typography(
                run, bold=True, italic=False, size='24', color='000000'
            )
        for run in runs[end_index + 1:]:
            if ''.join(node.text or '' for node in run.findall('w:t', namespaces)):
                _set_direct_run_typography(
                    run, bold=False, italic=False, size='24', color='000000'
                )
        normalized += 1
    return normalized


def normalize_reference_field_typography(doc_root):
    """Keep Word ``REF`` fields regular after Word refreshes their results.

    Word may copy the bold formatting stored inside a caption bookmark into
    the visible result of a ``REF`` field.  The caption itself must retain a
    bold label and number, but an in-sentence reference must remain regular.
    """
    namespaces = {'w': WORD_NS}
    normalized = 0
    for paragraph in doc_root.iter(f'{{{WORD_NS}}}p'):
        runs = paragraph.findall('.//w:r', namespaces)
        for instruction_index, run in enumerate(runs):
            instruction = ''.join(
                node.text or ''
                for node in run.findall('w:instrText', namespaces)
            )
            if not re.search(r'(^|\s)REF\s+[A-Za-z]', instruction):
                continue

            begin_index = None
            for index in range(instruction_index, -1, -1):
                field = runs[index].find('w:fldChar', namespaces)
                if field is None:
                    continue
                field_type = field.get(f'{{{WORD_NS}}}fldCharType')
                if field_type == 'begin':
                    begin_index = index
                    break
                if field_type == 'end':
                    break
            if begin_index is None:
                continue

            end_index = None
            for index in range(instruction_index, len(runs)):
                field = runs[index].find('w:fldChar', namespaces)
                if field is not None and field.get(
                        f'{{{WORD_NS}}}fldCharType') == 'end':
                    end_index = index
                    break
            if end_index is None:
                continue

            for field_run in runs[begin_index:end_index + 1]:
                _set_direct_run_typography(
                    field_run,
                    bold=False,
                    italic=False,
                    size='24',
                    color='000000',
                )
            normalized += 1
    return normalized


def cover_report_title(doc_root):
    """Return the first visible cover paragraph before front matter begins."""
    paragraphs = list(doc_root.iter(f'{{{WORD_NS}}}p'))
    first_page_break = next(
        (
            index for index, paragraph in enumerate(paragraphs)
            if paragraph.find(
                f'{{{WORD_NS}}}pPr/{{{WORD_NS}}}pageBreakBefore'
            ) is not None
        ),
        None,
    )
    if first_page_break is None:
        return ''
    for paragraph in paragraphs[:first_page_break]:
        text = ''.join(
            node.text or ''
            for node in paragraph.iter(f'{{{WORD_NS}}}t')
        ).strip()
        if text:
            return text
    return ''


def apply_post_com_technical_italics(
        doc_root, terms, *, protected_phrases=()):
    """Italicize only matching technical-term spans after Word COM updates."""
    if not terms:
        return 0
    protected = tuple(
        phrase.strip().casefold()
        for phrase in protected_phrases
        if isinstance(phrase, str) and phrase.strip()
    )
    protected_paragraphs = set()
    if protected:
        for paragraph in doc_root.iter(f'{{{WORD_NS}}}p'):
            paragraph_text = ''.join(
                node.text or ''
                for node in paragraph.iter(f'{{{WORD_NS}}}t')
            ).casefold()
            if any(phrase in paragraph_text for phrase in protected):
                protected_paragraphs.add(paragraph)
    pattern = re.compile(
        r'(?<!\w)(?:' + '|'.join(re.escape(term) for term in terms) + r')(?!\w)',
        re.IGNORECASE,
    )
    changed = 0
    xml_space = '{http://www.w3.org/XML/1998/namespace}space'
    for run in list(doc_root.iter(f'{{{WORD_NS}}}r')):
        paragraph = run.getparent()
        while (
            paragraph is not None
            and paragraph.tag != f'{{{WORD_NS}}}p'
        ):
            paragraph = paragraph.getparent()
        paragraph_style = (
            paragraph.find(
                f'{{{WORD_NS}}}pPr/{{{WORD_NS}}}pStyle'
            )
            if paragraph is not None else None
        )
        if (
            paragraph_style is not None
            and paragraph_style.get(f'{{{WORD_NS}}}val') == 'CodeBlock'
        ):
            continue
        if paragraph in protected_paragraphs:
            _set_direct_run_typography(run, italic=False)
            continue
        text_nodes = run.findall(f'{{{WORD_NS}}}t')
        text = ''.join(node.text or '' for node in text_nodes)
        matches = list(pattern.finditer(text)) if text else []
        if not matches:
            continue

        if any(child.tag not in {
                f'{{{WORD_NS}}}rPr', f'{{{WORD_NS}}}t'} for child in run):
            if len(matches) == 1 and matches[0].span() == (0, len(text)):
                _set_direct_run_typography(run, italic=True)
                changed += 1
            continue

        segments = []
        cursor = 0
        for match in matches:
            if match.start() > cursor:
                segments.append((text[cursor:match.start()], False))
            segments.append((match.group(0), True))
            cursor = match.end()
        if cursor < len(text):
            segments.append((text[cursor:], False))

        if len(segments) == 1:
            _set_direct_run_typography(run, italic=True)
            changed += 1
            continue

        parent = run.getparent()
        if parent is None:
            continue
        insert_at = parent.index(run)
        for offset, (segment_text, is_term) in enumerate(segments):
            replacement = copy.deepcopy(run)
            for child in list(replacement):
                if child.tag != f'{{{WORD_NS}}}rPr':
                    replacement.remove(child)
            text_element = lxml.etree.SubElement(
                replacement, f'{{{WORD_NS}}}t'
            )
            text_element.text = segment_text
            if segment_text.startswith(' ') or segment_text.endswith(' '):
                text_element.set(xml_space, 'preserve')
            if is_term:
                _set_direct_run_typography(replacement, italic=True)
                changed += 1
            parent.insert(insert_at + offset, replacement)
        parent.remove(run)
    return changed


def _duplicate_pair_allowed(id_a, id_b, duplicate_allow_groups):
    """True if both figure ids appear together in any allow-list group."""
    for group in duplicate_allow_groups:
        if id_a in group and id_b in group:
            return True
    return False


def get_image_dimensions(filepath):
    """Return (width, height) in pixels for PNG/JPEG."""
    with open(filepath, 'rb') as f:
        head = f.read(24)
        if len(head) != 24:
            return 800, 600
        if head.startswith(b'\x89PNG\r\n\x1a\n'):
            check = struct.unpack('>I', head[8:12])[0]
            if check == 0x0d0a1a0a:
                pass
            w, h = struct.unpack('>LL', head[16:24])
            return w, h
        elif head.startswith(b'\xff\xd8'):
            f.seek(0)
            size = 2
            ftype = 0
            while not 0xc0 <= ftype <= 0xcf or ftype in (0xc4, 0xc8, 0xcc):
                f.seek(size, 1)
                byte = f.read(1)
                while ord(byte) == 0xff:
                    byte = f.read(1)
                ftype = ord(byte)
                size = struct.unpack('>H', f.read(2))[0] - 2
            f.seek(1, 1)
            h, w = struct.unpack('>HH', f.read(4))
            return w, h
    return 800, 600


def scaled_dimensions(cx, cy, max_height_emu=None):
    """Aspect-preserving bounding-box scale applied to every BODY figure.

    Scales the native (cx, cy) to fit INSIDE the shared box
    (BODY_MAX_W_EMU x BODY_MAX_H_EMU) and an optional page-aware height cap
    using a SINGLE factor on both axes, so the aspect ratio is preserved (no
    stretch). Never upscales (scale capped at 1.0). Callers use the returned
    values for BOTH wp:extent and a:ext (so wp == ae) and to enforce the C4
    same-page drawing/caption contract."""
    if cx <= 0 or cy <= 0:
        return cx, cy
    height_cap = BODY_MAX_H_EMU
    if max_height_emu is not None:
        height_cap = min(height_cap, max(1, int(max_height_emu)))
    scale = min(BODY_MAX_W_EMU / cx, height_cap / cy, 1.0)
    return int(cx * scale), int(cy * scale)


def printable_height_emu(doc_root, namespaces):
    """Printable page height in EMU from the body sectPr:
    (pgSz.h - pgMar.top - pgMar.bottom) twips * 635. Falls back to MAX_WIDTH if
    the section geometry is unavailable. Must match the validator's threshold."""
    sect = doc_root.find('w:body/w:sectPr', namespaces)
    if sect is None:
        return MAX_WIDTH
    pgSz = sect.find('w:pgSz', namespaces)
    pgMar = sect.find('w:pgMar', namespaces)
    if pgSz is None or pgMar is None:
        return MAX_WIDTH
    try:
        h = int(pgSz.get(f'{{{WORD_NS}}}h'))
        top = int(pgMar.get(f'{{{WORD_NS}}}top'))
        bottom = int(pgMar.get(f'{{{WORD_NS}}}bottom'))
    except (TypeError, ValueError):
        return MAX_WIDTH
    return (h - top - bottom) * EMU_PER_TWIP


def _para_text(p):
    return "".join([t.text for t in p.iter(f'{{{WORD_NS}}}t') if t.text]).strip()


def _para_style(p, namespaces):
    pPr = p.find('w:pPr', namespaces)
    if pPr is None:
        return ""
    pStyle = pPr.find('w:pStyle', namespaces)
    return pStyle.get(f'{{{WORD_NS}}}val') if pStyle is not None else ""


def resolve_caption_indices(body, caption_match, namespaces):
    """Collect the body indices of ALL paragraphs that match a manifest entry:
    pStyle == 'Caption', text contains caption_match, and the remainder matches
    ^(Gambar|Tabel)\\s+[0-9\\.]+$. Returns the full list (no break-on-first)."""
    matches = []
    for idx, child in enumerate(list(body)):
        if child.tag != f'{{{WORD_NS}}}p':
            continue
        if _para_style(child, namespaces) != 'Caption':
            continue
        text = _para_text(child)
        if caption_match in text:
            remainder = text.replace(caption_match, "").strip()
            if re.match(r'^(Gambar|Tabel)\s+[0-9\.]+$', remainder, re.IGNORECASE):
                matches.append(idx)
    return matches


def resolve_figure_marker_indices(body, figure_id):
    """Return direct-body paragraph indices for one exact stable marker."""
    expected = f"[FIGURE:{figure_id}]"
    return [
        idx for idx, child in enumerate(list(body))
        if child.tag == f'{{{WORD_NS}}}p' and _para_text(child) == expected
    ]


def resolve_figure_target(body, item, namespaces):
    """Resolve one manifest item to its caption, preferring its exact marker.

    Returns ``(mode, locator_idx, caption_idx, error)``.  ``mode`` is
    ``marker`` for the stable Markdown reference or ``legacy_caption`` for
    backward-compatible documents that contain no marker for the item.
    """
    item_id = item.get('id', item.get('file', '<unknown>'))
    caption_match = item.get('caption_match', '')
    marker_matches = resolve_figure_marker_indices(body, item_id)
    if marker_matches:
        if len(marker_matches) != 1:
            return 'marker', None, None, (
                f"[C2] entry '{item_id}' marker [FIGURE:{item_id}] resolved to "
                f"{len(marker_matches)} paragraphs; expected exactly 1."
            )
        marker_idx = marker_matches[0]
        children = list(body)
        caption_idx = marker_idx + 1
        if caption_idx >= len(children):
            return 'marker', marker_idx, None, (
                f"[C2] entry '{item_id}' marker is not immediately followed by its caption."
            )
        caption_p = children[caption_idx]
        caption_matches = (
            caption_p.tag == f'{{{WORD_NS}}}p'
            and _para_style(caption_p, namespaces) == 'Caption'
            and caption_match in _para_text(caption_p)
        )
        if not caption_matches:
            return 'marker', marker_idx, caption_idx, (
                f"[C2] entry '{item_id}' marker must be immediately followed by a Caption "
                f"paragraph containing {caption_match!r}."
            )
        return 'marker', marker_idx, caption_idx, None

    caption_matches = resolve_caption_indices(body, caption_match, namespaces)
    if len(caption_matches) != 1:
        return 'legacy_caption', None, None, (
            f"[C2] entry '{item_id}' caption_match '{caption_match}' resolved to "
            f"{len(caption_matches)} caption paragraph(s); expected exactly 1."
        )
    return 'legacy_caption', caption_matches[0], caption_matches[0], None


def ensure_media_content_types(content_types_root, image_files):
    """Ensure every injected media extension has an OPC content type.

    Word may remove the PNG default while saving the pre-injection package if
    no PNG drawing remains at that stage.  Adding PNG parts without restoring
    this declaration produces a ZIP/XML package that our structural parser can
    read but Microsoft Word correctly rejects as corrupt.
    """
    mime_by_extension = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
    }
    existing = {
        (node.get('Extension') or '').lower()
        for node in content_types_root.findall(f'{{{CONTENT_TYPES_NS}}}Default')
    }
    added = []
    for image_file in image_files:
        extension = os.path.splitext(image_file)[1].lstrip('.').lower()
        if extension in existing:
            continue
        content_type = mime_by_extension.get(extension)
        if content_type is None:
            raise ValueError(
                f"Unsupported image extension '.{extension}' for '{image_file}'; "
                "add an explicit OPC content type before injection."
            )
        lxml.etree.SubElement(
            content_types_root,
            f'{{{CONTENT_TYPES_NS}}}Default',
            Extension=extension,
            ContentType=content_type,
        )
        existing.add(extension)
        added.append(extension)
    return added


def generate_drawing_xml(r_id, cx, cy, name, docpr_id, max_height_emu=None):
    """Generate w:drawing XML element with specified properties."""
    cx, cy = scaled_dimensions(cx, cy, max_height_emu=max_height_emu)

    xml = f'''<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" 
             xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" 
             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" 
             xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" 
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
        <w:pPr>
            <w:keepNext/>
            <w:keepLines/>
            <w:jc w:val="center"/>
        </w:pPr>
        <w:r>
            <w:drawing>
                <wp:inline distT="0" distB="0" distL="0" distR="0">
                    <wp:extent cx="{cx}" cy="{cy}"/>
                    <wp:effectExtent l="0" t="0" r="0" b="0"/>
                    <wp:docPr id="{docpr_id}" name="{name}"/>
                    <wp:cNvGraphicFramePr>
                        <a:graphicFrameLocks noChangeAspect="1"/>
                    </wp:cNvGraphicFramePr>
                    <a:graphic>
                        <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
                            <pic:pic>
                                <pic:nvPicPr>
                                    <pic:cNvPr id="{docpr_id}" name="{name}"/>
                                    <pic:cNvPicPr/>
                                </pic:nvPicPr>
                                <pic:blipFill>
                                    <a:blip r:embed="{r_id}" cstate="print"/>
                                    <a:stretch>
                                        <a:fillRect/>
                                    </a:stretch>
                                </pic:blipFill>
                                <pic:spPr>
                                    <a:xfrm>
                                        <a:off x="0" y="0"/>
                                        <a:ext cx="{cx}" cy="{cy}"/>
                                    </a:xfrm>
                                    <a:prstGeom prst="rect">
                                        <a:avLst/>
                                    </a:prstGeom>
                                    <a:ln>
                                        <a:noFill/>
                                    </a:ln>
                                </pic:spPr>
                            </pic:pic>
                        </a:graphicData>
                    </a:graphic>
                </wp:inline>
            </w:drawing>
        </w:r>
    </w:p>'''
    return lxml.etree.fromstring(xml)


def inject_all_images(docx_path, *, repair_only=False):
    print(f"Injecting all images into {docx_path}...")
    if repair_only:
        print(
            "Repair-only mode: preserving existing drawings while restoring "
            "post-COM formatting."
        )
    image_root = os.environ.get("TA_IMAGE_ROOT", "images")
    manifest_path = os.environ.get(
        "TA_IMAGE_MANIFEST_PATH",
        os.path.join(image_root, "manifest.json"),
    )
    reconcile_path = os.environ.get(
        "TA_IMAGE_RECONCILE_PATH",
        os.path.join(image_root, "manifest_reconcile.json"),
    )
    front_matter_path = os.environ.get(
        "TA_FRONT_MATTER_PATH",
        os.path.join("content", "roles", "iman", "front-matter.json"),
    )
    expected_acknowledgements = 8
    front_matter_config = {}
    if os.path.isfile(front_matter_path):
        with open(front_matter_path, "r", encoding="utf-8") as config_file:
            front_matter_config = json.load(config_file)
        expected_acknowledgements = len(
            front_matter_config.get("preface", {}).get(
                "acknowledgements", []
            )
        ) or expected_acknowledgements
    temp_dir = "temp_inject_dir"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    # 1. Unzip
    with zipfile.ZipFile(docx_path, 'r') as z:
        z.extractall(temp_dir)

    # 2. Read manifest + reconciliation allow-lists
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    duplicate_allow_groups, unresolved_allow = load_reconcile(reconcile_path)

    ns_uri = WORD_NS
    namespaces = {'w': ns_uri}
    parser = lxml.etree.XMLParser(remove_blank_text=False)

    # 3. Parse rels
    rels_path = os.path.join(temp_dir, "word", "_rels", "document.xml.rels")
    rels_tree = lxml.etree.parse(rels_path, parser)
    rels_root = rels_tree.getroot()
    rel_ns = REL_NS

    max_rid = 0
    max_img = 0
    for rel in rels_root:
        rid_str = rel.get('Id')
        if rid_str.startswith('rId'):
            try:
                rid_val = int(rid_str[3:])
                if rid_val > max_rid:
                    max_rid = rid_val
            except:
                pass
        target = rel.get('Target')
        if target and target.startswith('media/image'):
            try:
                img_num = int(target.replace('media/image', '').split('.')[0])
                if img_num > max_img:
                    max_img = img_num
            except:
                pass

    # 4. Parse document XML
    doc_path = os.path.join(temp_dir, "word", "document.xml")
    doc_tree = lxml.etree.parse(doc_path, parser)
    doc_root = doc_tree.getroot()
    body = doc_root.find('w:body', namespaces)

    styles_path = os.path.join(temp_dir, "word", "styles.xml")
    if os.path.exists(styles_path):
        styles_tree = lxml.etree.parse(styles_path, parser)
        styles_root = styles_tree.getroot()
    else:
        # Some unit fixtures intentionally contain only the minimum package
        # parts required for image injection.  Keep that compatibility while
        # still allowing the post-COM front-matter repair to create its style.
        styles_root = lxml.etree.Element(f'{{{ns_uri}}}styles')
        styles_tree = lxml.etree.ElementTree(styles_root)

    page_height_threshold = printable_height_emu(doc_root, namespaces)
    print(f"Printable page-height threshold: {page_height_threshold} EMU")

    post_com_items = [
        it for it in manifest["images"]
        if it.get("inject_method") == "post_com"
    ]
    if repair_only:
        post_com_items = []

    # Word COM can drop the PNG declaration when the intermediate document has
    # no remaining PNG drawings. Restore every media content type before any
    # new part is added so the final package opens without Word repair.
    content_types_path = os.path.join(temp_dir, "[Content_Types].xml")
    content_types_tree = lxml.etree.parse(content_types_path, parser)
    added_content_types = ensure_media_content_types(
        content_types_tree.getroot(), [item["file"] for item in post_com_items]
    )
    if added_content_types:
        print("Added OPC media content type(s): " + ", ".join(added_content_types))

    # ----------------------------------------------------------------- #
    # PRE-PASS: validate exactly-one resolution (C2), file presence, and
    # global content uniqueness (C1) BEFORE mutating the document, so the run
    # fails cleanly (non-zero, no partial write) instead of silently skipping.
    # ----------------------------------------------------------------- #
    errors = []
    md5_to_figure = {}  # media MD5 -> figure id (first injector to claim it)
    for item in post_com_items:
        item_id = item.get("id", item.get("file", "<unknown>"))
        caption_match = item["caption_match"]
        img_file = item["file"]
        src_path = os.path.join(image_root, img_file)

        mode, _locator_idx, _caption_idx, resolution_error = resolve_figure_target(
            body, item, namespaces
        )

        # C2: exactly-one marker/caption resolution (no silent skip).
        if resolution_error:
            legacy_match_count = len(resolve_caption_indices(body, caption_match, namespaces))
            if (mode == 'legacy_caption' and item_id in unresolved_allow
                    and legacy_match_count == 0):
                print(f"RECONCILED (unresolved_allow): '{item_id}' resolves to 0 captions; "
                      f"intentionally skipped.")
                continue
            errors.append(resolution_error)
            continue

        # Injectable entry must have its curated image on disk.
        if not os.path.exists(src_path):
            errors.append(
                f"[C2/file] entry '{item_id}' resolves to a caption but its injected "
                f"file '{src_path}' is missing on disk."
            )
            continue

        # C1: duplicate-content guard (honoring the reconciled reuse allow-list).
        digest = md5_file(src_path)
        if digest in md5_to_figure and md5_to_figure[digest] != item_id:
            other = md5_to_figure[digest]
            if not _duplicate_pair_allowed(item_id, other, duplicate_allow_groups):
                errors.append(
                    f"[C1] entry '{item_id}' would inject media with MD5 {digest}, "
                    f"already used by a different figure '{other}' (duplicate content). "
                    f"Reconcile legitimate reuse via duplicate_content_allow."
                )
                continue
        md5_to_figure.setdefault(digest, item_id)

    if errors:
        print("\n=== INJECTION ABORTED: content-level defects detected ===")
        for err in errors:
            print(f"- {err}")
        shutil.rmtree(temp_dir)
        sys.exit(1)

    # ----------------------------------------------------------------- #
    # INJECTION PASS: every remaining entry resolves to exactly one caption.
    # ----------------------------------------------------------------- #
    docpr_id = 1000
    injected_md5_by_image = {}  # imageNN -> injected images/<file> MD5 (C3 record)

    for item in post_com_items:
        item_id = item.get("id", item.get("file", "<unknown>"))
        caption_match = item["caption_match"]
        img_file = item["file"]
        src_path = os.path.join(image_root, img_file)

        # Re-resolve against the (possibly mutated) body.
        mode, locator_idx, caption_idx, resolution_error = resolve_figure_target(
            body, item, namespaces
        )
        if resolution_error:
            # Reconciled, intentionally-omitted entry: skip when it is
            # allow-listed AND resolves to 0 captions. This mirrors the pre-pass
            # reconciliation rule (which keys on caption count, not file
            # existence) so an allow-listed entry whose image happens to exist on
            # disk is skipped consistently rather than tripping the guard below.
            matches = resolve_caption_indices(body, caption_match, namespaces)
            if mode == 'legacy_caption' and item_id in unresolved_allow and len(matches) == 0:
                continue
            # Defensive: should never happen after the pre-pass.
            print(f"Error: {resolution_error}")
            shutil.rmtree(temp_dir)
            sys.exit(1)

        # Replace the explicit Markdown marker itself.  In the legacy fallback
        # there is no marker, so the caption remains the insertion locator.
        if mode == 'marker':
            marker_p = list(body)[locator_idx]
            body.remove(marker_p)
            caption_idx -= 1

        # Remove any existing drawing immediately preceding the caption.
        children = list(body)
        removed_existing = False
        if caption_idx >= 1:
            prev_p = children[caption_idx - 1]
            if prev_p.find('.//w:drawing', namespaces) is not None:
                body.remove(prev_p)
                caption_idx -= 1
                removed_existing = True

        # Copy image file verbatim into word/media (C3: bytes copied as-is).
        max_img += 1
        ext = img_file.split('.')[-1]
        new_img_name = f"image{max_img}.{ext}"
        dest_path = os.path.join(temp_dir, "word", "media", new_img_name)
        shutil.copy2(src_path, dest_path)
        # Record the injected file's MD5 keyed by the allocated imageNN. The
        # authoritative packed-vs-injected assertion runs in the validator.
        injected_md5_by_image[new_img_name] = md5_file(src_path)

        # Best-effort, non-fatal provenance note for the declared source.
        source = item.get("source")
        if source and os.path.exists(source):
            if md5_file(source) == injected_md5_by_image[new_img_name]:
                print(f"  note: source '{source}' matches injected '{img_file}' (MD5).")
            else:
                print(f"  note: source '{source}' differs from injected '{img_file}' "
                      f"(provenance only, not a failure).")

        # Add relationship.
        max_rid += 1
        r_id = f"rId{max_rid}"
        elem = lxml.etree.Element(f'{{{rel_ns}}}Relationship', {
            'Id': r_id,
            'Type': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image',
            'Target': f'media/{new_img_name}'
        })
        rels_root.append(elem)

        # Compute drawing dimensions. Read the ACTUAL image pixels (PIL) to get
        # the true native aspect ratio; fall back to the lightweight header
        # reader if PIL cannot open the file.
        w = h = None
        try:
            from PIL import Image
            with Image.open(src_path) as im:
                w, h = im.size
        except Exception as e:
            print(f"  note: PIL could not read '{src_path}' ({e}); using header reader.")
        if not w or not h:
            w, h = get_image_dimensions(src_path)
        cx = w * 9525
        cy = h * 9525
        if "cx" in item:
            cx = item["cx"]
        if "cy" in item:
            cy = item["cy"]

        docpr_id += 1
        drawing_identity = f"FIGURE:{item_id}"
        pair_figure_height = max(
            1, page_height_threshold - FIGURE_CAPTION_RESERVE_EMU
        )
        p_drawing = generate_drawing_xml(
            r_id,
            cx,
            cy,
            drawing_identity,
            docpr_id,
            max_height_emu=pair_figure_height,
        )

        # C4: reserve printable height for the caption, then scale the drawing
        # so the complete [drawing][caption] pair can fit on one page.  The
        # keepNext/keepLines chain below makes Word move the pair together when
        # the remaining space on the current page is insufficient.
        _, baseline_rendered_cy = scaled_dimensions(cx, cy)
        if baseline_rendered_cy > page_height_threshold:
            pPr = p_drawing.find('w:pPr', namespaces)
            if pPr is not None and pPr.find('w:pageBreakBefore', namespaces) is None:
                lxml.etree.SubElement(pPr, f'{{{ns_uri}}}pageBreakBefore')

        # Ensure caption keeps with the following text (keepNext/keepLines).
        caption_p = body[caption_idx]
        pPr_cap = caption_p.find('w:pPr', namespaces)
        if pPr_cap is None:
            pPr_cap = lxml.etree.Element(f'{{{ns_uri}}}pPr')
            caption_p.insert(0, pPr_cap)
        if pPr_cap.find('w:keepNext', namespaces) is None:
            lxml.etree.SubElement(pPr_cap, f'{{{ns_uri}}}keepNext')
        if pPr_cap.find('w:keepLines', namespaces) is None:
            lxml.etree.SubElement(pPr_cap, f'{{{ns_uri}}}keepLines')

        body.insert(caption_idx, p_drawing)
        print(
            f"Injected [FIGURE:{item_id}] from {img_file} before '{caption_match}' "
            f"(mode={mode}, rId={r_id}, size={w}x{h})"
        )

    # ----------------------------------------------------------------- #
    # POST-COM keep-props pass: the Word COM field-update step normalizes
    # Caption-styled paragraphs down to bare <w:pStyle w:val="Caption"/>,
    # discarding the keepNext/keepLines that the formatter applied pre-COM.
    # Re-assert them here (post-COM) on EVERY Gambar/Tabel caption so the
    # caption never splits from its image or across a page. Injected captions
    # already received these above; non-injected captions (e.g. the inline
    # survey charts) are fixed by this pass.
    # ----------------------------------------------------------------- #
    cap_fixed = 0
    for p in doc_root.iter(f'{{{ns_uri}}}p'):
        pPr = p.find('w:pPr', namespaces)
        pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
        style_val = pStyle.get(f'{{{ns_uri}}}val') if pStyle is not None else ""
        text = _para_text(p)
        is_caption = (style_val == 'Caption') or bool(re.match(r'^(Gambar|Tabel)\s+[0-9]', text, re.IGNORECASE))
        if not is_caption:
            continue
        if pPr is None:
            pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
            p.insert(0, pPr)
        changed = False
        if pPr.find('w:keepNext', namespaces) is None:
            lxml.etree.SubElement(pPr, f'{{{ns_uri}}}keepNext')
            changed = True
        if pPr.find('w:keepLines', namespaces) is None:
            lxml.etree.SubElement(pPr, f'{{{ns_uri}}}keepLines')
            changed = True
        if changed:
            cap_fixed += 1
    print(f"Post-COM keep-props pass: ensured keepNext/keepLines on {cap_fixed} caption paragraph(s).")

    # Keep the visible Daftar Isi heading outside the TOC content control in
    # the final package.  Word/LibreOffice can otherwise split the heading
    # across the approval-page boundary while regenerating the SDT field.
    for child in list(body):
        if child.tag != f'{{{ns_uri}}}sdt':
            continue
        sdt_content = child.find(f'{{{ns_uri}}}sdtContent')
        toc_heading = sdt_content.find(f'{{{ns_uri}}}p') if sdt_content is not None else None
        if toc_heading is None:
            continue
        toc_text = ''.join(toc_heading.itertext()).strip().upper()
        if not toc_text.startswith('DAFTAR ISI'):
            continue
        p_pr = toc_heading.find(f'{{{ns_uri}}}pPr')
        if p_pr is None:
            p_pr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
            toc_heading.insert(0, p_pr)
        if p_pr.find(f'{{{ns_uri}}}pageBreakBefore') is None:
            lxml.etree.SubElement(p_pr, f'{{{ns_uri}}}pageBreakBefore')
        sdt_content.remove(toc_heading)
        body.insert(body.index(child), toc_heading)
        bookmark_name = '_TocDaftarIsi'
        bookmark_ids = []
        for bookmark in doc_root.iter(f'{{{ns_uri}}}bookmarkStart'):
            try:
                bookmark_ids.append(int(bookmark.get(f'{{{ns_uri}}}id', '0')))
            except ValueError:
                continue
        bookmark_id = str(max(bookmark_ids, default=0) + 1)
        heading_children = list(toc_heading)
        heading_start = lxml.etree.Element(
            f'{{{ns_uri}}}bookmarkStart',
            {
                f'{{{ns_uri}}}id': bookmark_id,
                f'{{{ns_uri}}}name': bookmark_name,
            },
        )
        heading_end = lxml.etree.Element(
            f'{{{ns_uri}}}bookmarkEnd',
            {f'{{{ns_uri}}}id': bookmark_id},
        )
        first_content_index = 1 if heading_children and heading_children[0] is p_pr else 0
        toc_heading.insert(first_content_index, heading_start)
        field_index = next(
            (
                index for index, element in enumerate(list(toc_heading))
                if element.find(f'.//{{{ns_uri}}}fldChar') is not None
            ),
            len(toc_heading),
        )
        toc_heading.insert(field_index, heading_end)

        toc_entry_patched = False
        for paragraph in doc_root.iter(f'{{{ns_uri}}}p'):
            if paragraph is toc_heading:
                continue
            paragraph_text = ''.join(paragraph.itertext()).strip()
            if not paragraph_text.startswith('DAFTAR ISI'):
                continue
            instruction_nodes = paragraph.findall(
                f'.//{{{ns_uri}}}instrText'
            )
            pageref_nodes = [
                node for node in instruction_nodes
                if re.search(r'\bPAGEREF\s+\S+', node.text or '')
            ]
            if not pageref_nodes:
                continue
            for instruction in pageref_nodes:
                instruction.text = re.sub(
                    r'(\bPAGEREF\s+)\S+',
                    rf'\g<1>{bookmark_name}',
                    instruction.text,
                    count=1,
                )
            for hyperlink in paragraph.findall(f'.//{{{ns_uri}}}hyperlink'):
                hyperlink.set(f'{{{ns_uri}}}anchor', bookmark_name)
            toc_entry_patched = True
            break
        if not toc_entry_patched:
            raise RuntimeError(
                'Could not patch the Daftar Isi TOC entry to its stable bookmark.'
            )
        print('Post-COM TOC pass: moved Daftar Isi heading outside the TOC SDT.')
        break

    captions_normalized = normalize_caption_typography(doc_root)
    print(
        "Post-COM caption pass: normalized typography on "
        f"{captions_normalized} caption(s)."
    )
    references_normalized = normalize_reference_field_typography(doc_root)
    print(
        "Post-COM reference pass: normalized typography on "
        f"{references_normalized} REF field(s)."
    )
    front_matter_restored = restore_front_matter_after_com(
        doc_root, styles_root, expected_acknowledgements
    )
    print(
        "Post-COM front-matter pass: restored "
        f"{front_matter_restored['paragraph_styles']} style reference(s) and "
        f"{front_matter_restored['runs']} explicit text run(s); preface "
        f"indentation groups={front_matter_restored['preface']}."
    )
    footer_runs_restored = restore_identity_footer_after_com(
        temp_dir,
        front_matter_config.get('identity_footer'),
    )
    if footer_runs_restored:
        print(
            'Post-COM identity-footer pass: restored explicit typography on '
            f'{footer_runs_restored} run(s).'
        )
    report_title = cover_report_title(doc_root)
    italic_fixed = apply_post_com_technical_italics(
        doc_root,
        load_italic_terms(),
        protected_phrases=(report_title,),
    )
    print(f"Post-COM typography pass: ensured italic formatting on {italic_fixed} technical run(s).")

    # Write changes
    rels_tree.write(rels_path, encoding='utf-8', xml_declaration=True)
    doc_tree.write(doc_path, encoding='utf-8', xml_declaration=True)
    styles_tree.write(styles_path, encoding='utf-8', xml_declaration=True)
    content_types_tree.write(content_types_path, encoding='utf-8', xml_declaration=True)

    # Re-zip
    output_docx = docx_path
    if os.path.exists(output_docx):
        os.remove(output_docx)

    with zipfile.ZipFile(output_docx, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, temp_dir)
                z.write(filepath, arcname)

    shutil.rmtree(temp_dir)
    print(f"SUCCESS: Saved all post-COM images to {docx_path}")


if __name__ == '__main__':
    arguments = sys.argv[1:]
    repair_only = '--repair-only' in arguments
    paths = [argument for argument in arguments if argument != '--repair-only']
    inject_all_images(
        paths[0] if paths else "Tugas_Akhir_Formatted.docx",
        repair_only=repair_only,
    )
