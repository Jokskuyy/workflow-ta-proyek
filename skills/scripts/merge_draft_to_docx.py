import os
import re
import sys
import json
import argparse
from dataclasses import dataclass
from enum import Enum
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

# --------------------------------------------------------------------------- #
# List nesting by indentation (R3)
# --------------------------------------------------------------------------- #
# Spaces of leading indentation that correspond to one nesting level.
# The current Draf indents nested lists in steps of 3 spaces (top-level markers
# at column 0, second level at 3 spaces, third level at 6 spaces), which aligns
# 1:1 with the baseline marker nesting (1. -> a. -> 1)). A unit of 3 therefore
# reproduces the captured baseline level partition exactly (see
# tests/test_wpi_lists.py backward-compat test).
LIST_INDENT_UNIT = 3


def compute_list_level(indent_spaces, marker):
    """Return the nesting level of a list item from its leading indentation.

    Level depends ONLY on indentation; ``marker`` is cosmetic (R3.2) and never
    changes the level. Indentation 0 yields the outermost level 1 (R3.5), and
    the mapping is monotonic non-decreasing in indentation (R3.3): for
    ``a <= b`` we have ``compute_list_level(a, _) <= compute_list_level(b, _)``.

    Rule: ``level = 1 + (indent_spaces // LIST_INDENT_UNIT)``.

    Backward compatibility (R3.4): the current Draf uses real leading
    indentation (0/3/6 spaces) that mirrors its marker nesting, so this pure
    indentation rule reproduces the baseline list levels exactly without any
    marker-based fallback. The ``marker`` parameter is accepted for interface
    completeness only.
    """
    if indent_spaces < 0:
        indent_spaces = 0
    return 1 + (indent_spaces // LIST_INDENT_UNIT)


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
    
    skip_until = -1
    for idx, line in enumerate(lines):
        # Skip lines already consumed by a detected pipe table (R5).
        if idx <= skip_until:
            continue
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
            
        # Handle standard pipe tables (R5, Opt_In_By_Content). Only triggers
        # when a real pipe table (line with '|' + valid separator) is present,
        # and only outside code blocks / [TABLE] blocks (handled by the
        # continues above). The existing [TABLE] path is untouched.
        if not in_code_block and not in_table and '|' in stripped:
            detected = detect_pipe_table(lines, idx)
            if detected is not None:
                end_idx, table_item = detected
                items.append(table_item)
                skip_until = end_idx - 1
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

            # Level is computed from leading indentation; marker is cosmetic (R3).
            list_level = compute_list_level(indent_spaces, marker)

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

# --------------------------------------------------------------------------- #
# Inline tokenizer (R2) — pure token model + left->right scanner.
# --------------------------------------------------------------------------- #
class TokenKind(Enum):
    """Kind of an inline token produced by ``tokenize_inline``."""
    TEXT = "text"   # plain text, carries bold/italic flags
    CODE = "code"   # inline code -> monospace run
    LINK = "link"   # hyperlink -> w:hyperlink run


@dataclass(frozen=True)
class InlineToken:
    """A flat inline token (immutable). ``url`` is only set for LINK tokens."""
    kind: TokenKind
    text: str
    bold: bool = False
    italic: bool = False
    url: "str | None" = None


# Hyperlink pattern: [text](url). Greedy-free inner classes per design §1.
_LINK_RE = re.compile(r'\[([^\]]*)\]\(([^)]*)\)')


def tokenize_inline(text):
    """Turn inline-markup ``text`` into a flat list of :class:`InlineToken`.

    Supports (design Components §1):
      - ``\\*``        -> literal asterisk (no state change)
      - ```` `code` `` -> CODE token (literal backtick if unclosed)
      - ``[text](url)``-> LINK token (literal ``[`` if the pattern does not match)
      - ``***``        -> toggle bold+italic
      - ``**``         -> toggle bold
      - ``*``          -> toggle italic
      - otherwise      -> accumulate as literal text

    Unbalanced emphasis markers are reconciled (R2.7): an unpaired opener is
    treated as a literal ``*``/``**``/``***`` at its position and never leaks
    its format to following text. Pure and deterministic (no lxml).
    """
    if text is None:
        return []

    # ----- Pass 1: scan into a flat element list -------------------------- #
    # Each element is a dict with a 'kind'. Markers carry a mutable 'literal'
    # flag set during reconciliation.
    elements = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        # Escaped asterisk -> literal '*', no state change.
        if c == '\\' and i + 1 < n and text[i + 1] == '*':
            elements.append({'kind': 'text', 'text': '*'})
            i += 2
            continue
        # Inline code.
        if c == '`':
            close = text.find('`', i + 1)
            if close != -1:
                elements.append({'kind': 'code', 'text': text[i + 1:close]})
                i = close + 1
            else:
                elements.append({'kind': 'text', 'text': '`'})
                i += 1
            continue
        # Hyperlink.
        if c == '[':
            m = _LINK_RE.match(text, i)
            if m:
                elements.append({'kind': 'link', 'text': m.group(1), 'url': m.group(2)})
                i = m.end()
            else:
                elements.append({'kind': 'text', 'text': '['})
                i += 1
            continue
        # Emphasis markers (longest first).
        if text.startswith('***', i):
            elements.append({'kind': 'bitoggle', 'literal': False})
            i += 3
            continue
        if text.startswith('**', i):
            elements.append({'kind': 'btoggle', 'literal': False})
            i += 2
            continue
        if c == '*':
            elements.append({'kind': 'itoggle', 'literal': False})
            i += 1
            continue
        # Plain character.
        elements.append({'kind': 'text', 'text': c})
        i += 1

    # ----- Reconcile unbalanced markers (R2.7) ---------------------------- #
    # A '***' participates in BOTH the bold and italic toggle streams.
    bold_markers = [e for e in elements if e['kind'] in ('btoggle', 'bitoggle')]
    italic_markers = [e for e in elements if e['kind'] in ('itoggle', 'bitoggle')]
    if len(bold_markers) % 2 == 1:
        bold_markers[-1]['literal'] = True
    if len(italic_markers) % 2 == 1:
        italic_markers[-1]['literal'] = True

    _literal_form = {'btoggle': '**', 'itoggle': '*', 'bitoggle': '***'}

    # ----- Pass 2: build final tokens ------------------------------------- #
    tokens = []
    buf = []
    bold = False
    italic = False

    def flush():
        if buf:
            tokens.append(InlineToken(TokenKind.TEXT, ''.join(buf), bold, italic))
            buf.clear()

    for e in elements:
        kind = e['kind']
        if kind == 'text':
            buf.append(e['text'])
        elif kind == 'code':
            flush()
            tokens.append(InlineToken(TokenKind.CODE, e['text']))
        elif kind == 'link':
            flush()
            tokens.append(InlineToken(TokenKind.LINK, e['text'], url=e['url']))
        else:  # marker
            if e['literal']:
                buf.append(_literal_form[kind])
            else:
                flush()
                if kind == 'btoggle':
                    bold = not bold
                elif kind == 'itoggle':
                    italic = not italic
                else:  # bitoggle
                    bold = not bold
                    italic = not italic
    flush()
    return tokens


# --------------------------------------------------------------------------- #
# Relationship manager for external hyperlinks (R2) -> document.xml.rels.
# --------------------------------------------------------------------------- #
class RelManager:
    """Allocate and persist external (hyperlink) relationships additively.

    ``add_external`` returns a relationship id (deduped per identical URL).
    ``write`` appends the new relationships to ``document.xml.rels`` while
    preserving every relationship already present. When no external
    relationships were allocated, ``write`` leaves the file untouched.
    """
    _PKG_REL_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'
    _HYPERLINK_TYPE = ('http://schemas.openxmlformats.org/officeDocument/'
                       '2006/relationships/hyperlink')

    def __init__(self, existing_ids=None):
        self._url_to_id = {}          # url -> rId (dedup)
        self._new = []                # [(rId, url)] in allocation order
        self._existing_ids = set(existing_ids or ())
        self._counter = 0

    def _next_id(self):
        while True:
            self._counter += 1
            rid = f'rId{self._counter}'
            if rid not in self._existing_ids and rid not in self._url_to_id.values():
                return rid

    def add_external(self, url):
        """Return an rId for ``url`` (reusing the same rId for identical URLs)."""
        if url in self._url_to_id:
            return self._url_to_id[url]
        rid = self._next_id()
        self._url_to_id[url] = rid
        self._new.append((rid, url))
        return rid

    @property
    def has_new(self):
        return bool(self._new)

    def write(self, rels_path):
        """Append new hyperlink relationships to ``rels_path`` (additive)."""
        if not self._new:
            return  # nothing allocated -> leave rels file unchanged
        parser = lxml.etree.XMLParser(remove_blank_text=False)
        if os.path.exists(rels_path):
            tree = lxml.etree.parse(rels_path, parser)
            root = tree.getroot()
        else:
            root = lxml.etree.Element(f'{{{self._PKG_REL_NS}}}Relationships')
            tree = lxml.etree.ElementTree(root)
        existing = {rel.get('Id') for rel in root}
        for rid, url in self._new:
            if rid in existing:
                continue
            rel = lxml.etree.SubElement(root, f'{{{self._PKG_REL_NS}}}Relationship')
            rel.set('Id', rid)
            rel.set('Type', self._HYPERLINK_TYPE)
            rel.set('Target', url)
            rel.set('TargetMode', 'External')
        tree.write(rels_path, encoding='UTF-8', xml_declaration=True, standalone=True)


# --------------------------------------------------------------------------- #
# Bibliography entry parser (R1) — pure helpers consumed by the bibliography
# writer (clean_bibliography_sdt in skills/scripts/format_ta_proyek.py) and the
# citation cross-check (R1.5/1.6). Draft '# DAFTAR PUSTAKA' is the source of
# truth (Option B); no references are hardcoded.
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class ReferenceEntry:
    """One APA reference entry parsed from the draft '# DAFTAR PUSTAKA' section.

    - ``raw``    : the verbatim entry line (no trailing newline, stripped).
    - ``spans``  : tuple of (text, is_italic) segments (render-ready). Joining
                   the segment texts reproduces ``raw`` with the ``*`` italic
                   markers removed (R1.2 fidelity).
    - ``authors``: tuple of author surname(s) used for matching/cross-check.
    - ``year``   : publication year ('YYYY') or None.
    """
    raw: str
    spans: tuple
    authors: tuple
    year: "str | None"


class BibliographyResult(list):
    """A ``list[ReferenceEntry]`` that also carries ``section_found`` (R1.8).

    Behaves exactly like a list (count/order/indexing) so callers and property
    tests can treat it as ``list[ReferenceEntry]``; the extra attribute lets
    the bibliography writer distinguish "section missing" from "section empty".
    """
    def __init__(self, entries=(), section_found=False):
        super().__init__(entries)
        self.section_found = section_found


_DAFTAR_PUSTAKA_RE = re.compile(r'^\s*#\s+DAFTAR\s+PUSTAKA\s*$', re.IGNORECASE)
_YEAR_RE = re.compile(r'\((\d{4})[a-z]?\)')


def _load_draft_text(draft_path_or_text):
    """Accept either a draft path or raw draft text and return the text.

    A value containing a newline, or starting with '#', or that is not an
    existing file, is treated as literal text; otherwise it is read as a file.
    """
    s = draft_path_or_text
    if not isinstance(s, str):
        return ""
    if '\n' in s or s.lstrip().startswith('#'):
        return s
    try:
        if os.path.exists(s):
            with open(s, encoding='utf-8') as f:
                return f.read()
    except (OSError, ValueError):
        pass
    return s


def parse_italic_spans(raw):
    """Split a reference entry into (text, is_italic) segments via the italic
    path of :func:`tokenize_inline` (reuse keeps R1.2 consistent with R2).

    Adjacent segments sharing the same italic flag are merged so the result is
    canonical. Joining the segment texts reproduces ``raw`` minus the ``*``
    markers. CODE/LINK tokens (not expected inside bibliography entries) are
    emitted as plain, non-italic text.
    """
    spans = []
    for tok in tokenize_inline(raw or ""):
        text = tok.text
        if not text:
            continue
        is_italic = bool(tok.italic) and tok.kind == TokenKind.TEXT
        if spans and spans[-1][1] == is_italic:
            spans[-1] = (spans[-1][0] + text, is_italic)
        else:
            spans.append((text, is_italic))
    return [(t, i) for t, i in spans]


def _parse_authors(raw):
    """Best-effort extraction of author surname(s) from an APA entry.

    The author block is the text before the first '(YYYY)'. The first surname
    (text up to the first comma) is always returned; a second surname after an
    '&' is included when easily separable.
    """
    m = _YEAR_RE.search(raw)
    head = (raw[:m.start()] if m else raw).strip()
    if not head:
        return ()
    first = head.split(',', 1)[0].strip()
    surnames = [first] if first else []
    if '&' in head:
        tail = head.rsplit('&', 1)[1].strip()
        tail_surname = tail.split(',', 1)[0].strip().rstrip('.').strip()
        if tail_surname and tail_surname not in surnames:
            surnames.append(tail_surname)
    return tuple(surnames)


def reference_key(entry):
    """Matching key for an entry: (first-author surname lowercased, year)."""
    surname = entry.authors[0].lower() if entry.authors else ""
    return (surname, entry.year or "")


def parse_bibliography_entries(draft_path_or_text):
    """Read the '# DAFTAR PUSTAKA' section -> :class:`BibliographyResult`.

    Each non-empty line under the heading (until the next '#' heading or a
    '---' horizontal rule) is one entry, in order of appearance (R1.1, R1.4).
    If the heading is absent, an empty result with ``section_found=False`` is
    returned (R1.8).
    """
    text = _load_draft_text(draft_path_or_text)
    lines = text.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if _DAFTAR_PUSTAKA_RE.match(line):
            start = idx + 1
            break
    if start is None:
        return BibliographyResult((), section_found=False)

    entries = []
    for line in lines[start:]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('#') or stripped == '---':
            break
        ym = _YEAR_RE.search(stripped)
        entries.append(ReferenceEntry(
            raw=stripped,
            spans=tuple(parse_italic_spans(stripped)),
            authors=_parse_authors(stripped),
            year=(ym.group(1) if ym else None),
        ))
    return BibliographyResult(entries, section_found=True)


# --------------------------------------------------------------------------- #
# Writing guards (R6 + citation cross-check R1.5/1.6/6.3) — PURE collectors.
# --------------------------------------------------------------------------- #
# These functions are pure, deterministic, and never touch lxml. They are
# consumed by ``validate_docx_structure.py`` (both copies) which prints the
# returned strings as non-fatal ``[WARN]`` lines (additive, R6.6). Each
# collector returns a list of warning strings, except the citation cross-check
# which returns ``(warnings, has_fatal)``.
# --------------------------------------------------------------------------- #
_BAB_RE = re.compile(r'^BAB\s+([IVXLCDM]+|\d+)\b', re.IGNORECASE)
_ROMAN_MAP = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
# In-text citation: a parenthesised group that contains at least one 4-digit year.
_CITATION_PAREN_RE = re.compile(r'\(([^)]*\d{4}[a-z]?[^)]*)\)')
_INNER_YEAR_RE = re.compile(r'(\d{4})[a-z]?')
_ET_AL_RE = re.compile(r'\bet\s+al\.?', re.IGNORECASE)


def _roman_to_int(s):
    """Convert a Roman numeral to int; return None if any char is invalid."""
    total = 0
    prev = 0
    for ch in reversed(s.upper()):
        v = _ROMAN_MAP.get(ch)
        if v is None:
            return None
        if v < prev:
            total -= v
        else:
            total += v
            prev = v
    return total


def _bab_number(text):
    """Return the BAB ordinal as int for a heading text like 'BAB II ...'.

    Supports Roman (I, II, III, ...) and Arabic (1, 2, ...). Returns None when
    the text is not a BAB heading or the numeral is unparseable.
    """
    if not text:
        return None
    m = _BAB_RE.match(text.strip())
    if not m:
        return None
    token = m.group(1)
    if token.isdigit():
        return int(token)
    return _roman_to_int(token)


def collect_heading_level_warnings(items):
    """R6.1 — warn on heading level jumps that ascend by more than one level.

    Returns exactly one warning per transition between two consecutive headings
    whose level increases by more than one (e.g. ``#`` directly to ``###``),
    naming the location and the skipped level(s). Transitions that ascend by at
    most one level (or descend) produce no warning. (Property 12)
    """
    warnings = []
    headings = [it for it in (items or []) if it.get('type') == 'heading']
    prev_level = None
    for h in headings:
        level = h.get('level')
        text = h.get('text', '')
        if prev_level is not None and level - prev_level > 1:
            skipped = ", ".join(f"H{lv}" for lv in range(prev_level + 1, level))
            warnings.append(
                f"[WARN][heading] Lompatan level heading pada '{text}': "
                f"dari H{prev_level} ke H{level} (melewati {skipped})."
            )
        prev_level = level
    return warnings


def collect_bab_order_warnings(items):
    """R6.2 — warn when a BAB heading does not ascend sequentially.

    For each BAB heading compared to the previous BAB heading, emit one warning
    when the ordinal is not exactly ``prev + 1`` (i.e. out of order, repeated,
    or skipped). Sequentially ascending BABs produce no warning. (Property 13)
    """
    warnings = []
    prev_num = None
    prev_text = None
    for it in (items or []):
        if it.get('type') != 'heading':
            continue
        num = _bab_number(it.get('text', ''))
        if num is None:
            continue
        if prev_num is not None and num != prev_num + 1:
            warnings.append(
                f"[WARN][bab] Urutan BAB tidak berurutan: '{it.get('text', '')}' "
                f"(BAB {num}) mengikuti '{prev_text}' (BAB {prev_num}); "
                f"diharapkan BAB {prev_num + 1}."
            )
        prev_num = num
        prev_text = it.get('text', '')
    return warnings


def collect_unclosed_table_warnings(lines):
    """R6.4 — warn when a ``[TABLE]`` block is opened without a ``[/TABLE]``.

    Mirrors the ``parse_markdown`` open/close semantics: a line whose stripped
    form starts with ``[TABLE]`` opens a block; a line whose stripped form ends
    with ``[/TABLE]`` closes it. Emits exactly one warning when a block remains
    open at end of input, and none when every block is closed. (Property 14)
    """
    warnings = []
    in_table = False
    open_line = None
    for idx, line in enumerate(lines or []):
        stripped = line.strip()
        if stripped.startswith('[TABLE]'):
            in_table = True
            open_line = idx + 1
            continue
        if stripped.endswith('[/TABLE]'):
            in_table = False
            continue
    if in_table:
        warnings.append(
            f"[WARN][tabel] Blok [TABLE] dibuka pada baris {open_line} "
            f"tanpa penutup [/TABLE]."
        )
    return warnings


def _emphasis_balanced(line):
    """True if a line's emphasis markers are balanced (ignoring escaped ``\\*``).

    Counts backticks (code spans), ``**``/``***`` (bold stream) and
    ``*``/``***`` (italic stream) exactly as the inline tokenizer does. Inside a
    code span (between backticks) asterisks are literal and not counted. The
    line is balanced iff backticks are even AND the bold stream is even AND the
    italic stream is even.
    """
    i = 0
    n = len(line)
    bold = 0
    italic = 0
    backticks = 0
    in_code = False
    while i < n:
        c = line[i]
        if c == '\\' and i + 1 < n and line[i + 1] == '*':
            i += 2
            continue
        if c == '`':
            backticks += 1
            in_code = not in_code
            i += 1
            continue
        if in_code:
            i += 1
            continue
        if line.startswith('***', i):
            bold += 1
            italic += 1
            i += 3
            continue
        if line.startswith('**', i):
            bold += 1
            i += 2
            continue
        if c == '*':
            italic += 1
            i += 1
            continue
        i += 1
    return (backticks % 2 == 0) and (bold % 2 == 0) and (italic % 2 == 0)


def collect_unbalanced_emphasis_warnings(lines):
    """R6.5 — warn for each line whose emphasis markers are unbalanced.

    Emits one warning naming the line exactly when its emphasis markers
    (``*``/``**``/`` ` ``) are unbalanced, ignoring escaped ``\\*``; balanced
    lines produce no warning. (Property 15)
    """
    warnings = []
    for idx, line in enumerate(lines or []):
        content = line.rstrip('\r\n')
        if not _emphasis_balanced(content):
            warnings.append(
                f"[WARN][emphasis] Penanda emphasis tak seimbang pada baris "
                f"{idx + 1}: '{content}'."
            )
    return warnings


def _extract_citation_keys(body_text):
    """Extract in-text APA citation keys from ``body_text``.

    Returns a list of ``(surname_lower, year, display_name)`` tuples. Handles
    ``(Nama, Tahun)``, ``(Nama et al., Tahun)``, ``(Nama & Lain, Tahun)`` and
    multiple sources in one parenthesis separated by ';'.
    """
    keys = []
    for m in _CITATION_PAREN_RE.finditer(body_text or ""):
        inner = m.group(1)
        for part in inner.split(';'):
            part = part.strip()
            ym = _INNER_YEAR_RE.search(part)
            if not ym:
                continue
            year = ym.group(1)
            name_part = part.split(',', 1)[0].strip()
            name_part = _ET_AL_RE.sub('', name_part).strip()
            name_part = name_part.split('&', 1)[0].strip()
            if not name_part:
                continue
            keys.append((name_part.lower(), year, name_part))
    return keys


def collect_citation_crosscheck_warnings(body_text, entries, *, fatal=False):
    """R1.5/1.6/6.3 — two-way cross-check between citations and references.

    Forward (R1.5, Property 4): each in-text citation whose key (name, year) has
    no matching :class:`ReferenceEntry` yields exactly one warning naming the
    citation's name and year.
    Backward (R1.6, Property 5): each reference entry never referenced by any
    citation yields exactly one warning naming the entry.

    Returns ``(warnings, has_fatal)``. ``has_fatal`` is always ``False`` when
    ``fatal=False`` (default, non-fatal); when ``fatal=True`` any mismatch sets
    ``has_fatal=True`` (R1.7).
    """
    warnings = []
    citations = _extract_citation_keys(body_text)
    entry_keys = {reference_key(e) for e in (entries or [])}
    cited_keys = {(surname, year) for surname, year, _ in citations}

    # Forward: citation -> Daftar_Pustaka (R1.5). Dedup per unique (name, year).
    seen_missing = set()
    for surname, year, display in citations:
        key = (surname, year)
        if key not in entry_keys and key not in seen_missing:
            seen_missing.add(key)
            warnings.append(
                f"[WARN][sitasi] Sitasi ({display}, {year}) tidak memiliki "
                f"Entri_Referensi padanan pada Daftar_Pustaka."
            )

    # Backward: Daftar_Pustaka -> citation (R1.6).
    for e in (entries or []):
        if reference_key(e) not in cited_keys:
            warnings.append(
                f"[WARN][sitasi] Entri_Referensi '{e.raw}' tidak pernah "
                f"dirujuk oleh Sitasi_In_Text mana pun."
            )

    has_fatal = bool(fatal and warnings)
    return warnings, has_fatal


# --------------------------------------------------------------------------- #
def _baseline_text_rPr(ns_uri, bold, italic, default_rPr=None):
    """Build the baseline rPr for a TEXT run, byte-identical to the oracle."""
    rPr = lxml.etree.Element(f'{{{ns_uri}}}rPr')

    # Inherit default fonts and sizes.
    if default_rPr is not None:
        for child in default_rPr:
            rPr.append(lxml.etree.fromstring(lxml.etree.tostring(child)))

    # Set fonts explicitly to Times New Roman.
    rFonts = rPr.find(f'{{{ns_uri}}}rFonts')
    if rFonts is None:
        rFonts = lxml.etree.Element(f'{{{ns_uri}}}rFonts')
        rPr.append(rFonts)
    rFonts.set(f'{{{ns_uri}}}ascii', 'Times New Roman')
    rFonts.set(f'{{{ns_uri}}}hAnsi', 'Times New Roman')

    # Set size explicitly if not set (sz val 24 = 12pt).
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

    if bold:
        rPr.append(lxml.etree.Element(f'{{{ns_uri}}}b'))
        rPr.append(lxml.etree.Element(f'{{{ns_uri}}}bCs'))

    if italic:
        rPr.append(lxml.etree.Element(f'{{{ns_uri}}}i'))
        rPr.append(lxml.etree.Element(f'{{{ns_uri}}}iCs'))

    return rPr


def emit_runs(p_elem, tokens, default_rPr=None, rel_manager=None):
    """Append ``w:r`` (and ``w:hyperlink`` for LINK tokens) to ``p_elem``.

    TEXT tokens replicate the baseline rPr byte-for-byte (Times New Roman,
    sz/szCs 24, optional w:b/bCs and w:i/iCs) so balanced/plain text is
    identical to the frozen oracle. CODE tokens use Consolas. LINK tokens wrap a
    run inside a ``w:hyperlink`` carrying an r:id allocated by ``rel_manager``
    (falls back to a plain run when no rel_manager is supplied).
    """
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    r_ns = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'

    for tok in tokens:
        if tok.kind == TokenKind.TEXT:
            if not tok.text:
                continue
            r = lxml.etree.Element(f'{{{ns_uri}}}r')
            r.append(_baseline_text_rPr(ns_uri, tok.bold, tok.italic, default_rPr))
            t = lxml.etree.Element(f'{{{ns_uri}}}t')
            t.text = tok.text
            if tok.text.startswith(' ') or tok.text.endswith(' '):
                t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            r.append(t)
            p_elem.append(r)

        elif tok.kind == TokenKind.CODE:
            r = lxml.etree.Element(f'{{{ns_uri}}}r')
            rPr = lxml.etree.SubElement(r, f'{{{ns_uri}}}rPr')
            lxml.etree.SubElement(rPr, f'{{{ns_uri}}}rFonts', {
                f'{{{ns_uri}}}ascii': 'Consolas',
                f'{{{ns_uri}}}hAnsi': 'Consolas'
            })
            lxml.etree.SubElement(rPr, f'{{{ns_uri}}}sz', {f'{{{ns_uri}}}val': '18'})
            lxml.etree.SubElement(rPr, f'{{{ns_uri}}}szCs', {f'{{{ns_uri}}}val': '18'})
            t = lxml.etree.SubElement(r, f'{{{ns_uri}}}t')
            t.text = tok.text
            if tok.text.startswith(' ') or tok.text.endswith(' '):
                t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            p_elem.append(r)

        elif tok.kind == TokenKind.LINK:
            if rel_manager is not None:
                rid = rel_manager.add_external(tok.url)
                hyperlink = lxml.etree.SubElement(p_elem, f'{{{ns_uri}}}hyperlink')
                hyperlink.set(f'{{{r_ns}}}id', rid)
                hyperlink.set(f'{{{ns_uri}}}history', '1')
                r = lxml.etree.SubElement(hyperlink, f'{{{ns_uri}}}r')
                rPr = lxml.etree.SubElement(r, f'{{{ns_uri}}}rPr')
                lxml.etree.SubElement(rPr, f'{{{ns_uri}}}rStyle', {f'{{{ns_uri}}}val': 'Hyperlink'})
                lxml.etree.SubElement(rPr, f'{{{ns_uri}}}rFonts', {
                    f'{{{ns_uri}}}ascii': 'Times New Roman',
                    f'{{{ns_uri}}}hAnsi': 'Times New Roman'
                })
                lxml.etree.SubElement(rPr, f'{{{ns_uri}}}sz', {f'{{{ns_uri}}}val': '24'})
                lxml.etree.SubElement(rPr, f'{{{ns_uri}}}szCs', {f'{{{ns_uri}}}val': '24'})
                t = lxml.etree.SubElement(r, f'{{{ns_uri}}}t')
                t.text = tok.text
                if tok.text.startswith(' ') or tok.text.endswith(' '):
                    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            else:
                # No rel manager -> degrade gracefully to a plain baseline run.
                r = lxml.etree.Element(f'{{{ns_uri}}}r')
                r.append(_baseline_text_rPr(ns_uri, False, False, default_rPr))
                t = lxml.etree.Element(f'{{{ns_uri}}}t')
                t.text = tok.text
                if tok.text.startswith(' ') or tok.text.endswith(' '):
                    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                r.append(t)
                p_elem.append(r)


def add_formatted_text(p_elem, text, default_rPr=None, rel_manager=None):
    """Backwards-compatible wrapper: emit_runs(p_elem, tokenize_inline(text), ...).

    The legacy signature is preserved (``rel_manager`` is optional) so existing
    callers keep working. For text without new constructs (plain text plus
    balanced ``**``/``*``) the emitted runs are byte-identical to the frozen
    oracle ``add_formatted_text``.
    """
    emit_runs(p_elem, tokenize_inline(text), default_rPr, rel_manager)

def build_p_element(item, rel_manager=None):
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
        
        add_formatted_text(p, item['text'], default_rPr, rel_manager)
        
    elif item['type'] == 'page_break':
        r = lxml.etree.SubElement(p, f'{{{ns_uri}}}r')
        lxml.etree.SubElement(r, f'{{{ns_uri}}}br', {f'{{{ns_uri}}}type': 'page'})
        
    elif item['type'] == 'list_item':
        # R4: opt-in Word numbering (numPr). The branch only activates when the
        # list_item explicitly requests it via 'use_numpr' (Opt_In_By_Content).
        # Without the trigger the rendering is byte-identical to Output_Baseline:
        # a literal textual marker run.
        use_numpr = bool(item.get('use_numpr', False))

        lxml.etree.SubElement(pPr, f'{{{ns_uri}}}pStyle', {f'{{{ns_uri}}}val': 'ListParagraph'})

        if use_numpr:
            # R4.1: render the ordered-list item through Word's numbering engine
            # (numId/ilvl) instead of a literal textual marker. numPr must sit
            # right after pStyle per the CT_PPr child ordering.
            numPr = lxml.etree.SubElement(pPr, f'{{{ns_uri}}}numPr')
            ilvl_val = str(max(0, item['level'] - 1))
            num_id_val = str(item.get('num_id', 1))
            lxml.etree.SubElement(numPr, f'{{{ns_uri}}}ilvl', {f'{{{ns_uri}}}val': ilvl_val})
            lxml.etree.SubElement(numPr, f'{{{ns_uri}}}numId', {f'{{{ns_uri}}}val': num_id_val})

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
        
        if not use_numpr:
            # R4.2/R4.3 (default, baseline): literal textual marker + tab run.
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
        
        add_formatted_text(p, item['text'], rel_manager=rel_manager)
        
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
                
                add_formatted_text(p, suffix, rel_manager=rel_manager)
            else:
                add_formatted_text(p, item['text'], rel_manager=rel_manager)
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
            
            add_formatted_text(p, item['text'], rel_manager=rel_manager)
            
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

# --------------------------------------------------------------------------- #
# Pipe table parsing (R5) — pure functions, Opt_In_By_Content.
# --------------------------------------------------------------------------- #
class Alignment(Enum):
    """Per-column alignment of a pipe table, mapped directly to w:jc/@w:val.

    NOTE: DEFAULT and LEFT share the value "left"; per Python Enum semantics
    LEFT becomes an alias of DEFAULT. Both render to ``w:jc w:val="left"``.
    """
    DEFAULT = "left"   # no ':' -> default (left, identical to baseline cell)
    LEFT = "left"      # :---
    CENTER = "center"  # :---:
    RIGHT = "right"    # ---:


_SEPARATOR_CELL_RE = re.compile(r'^:?-+:?$')


def _split_pipe_cells(line):
    """Split a pipe-table line into trimmed cells, dropping outer-pipe empties."""
    cells = [c.strip() for c in line.split('|')]
    if cells and cells[0] == '':
        cells = cells[1:]
    if cells and cells[-1] == '':
        cells = cells[:-1]
    return cells


def is_pipe_table_separator(line):
    """True if ``line`` is a Baris_Pemisah: every cell matches ``^:?-+:?$``
    after splitting on '|' (e.g. '---', ':---', ':---:', '---:')."""
    cells = _split_pipe_cells(line)
    if not cells:
        return False
    return all(_SEPARATOR_CELL_RE.match(c) for c in cells)


def parse_alignment_row(line):
    """Map each separator cell to an :class:`Alignment`
    (LEFT ':---', CENTER ':---:', RIGHT '---:', DEFAULT '---')."""
    alignments = []
    for cell in _split_pipe_cells(line):
        left = cell.startswith(':')
        right = cell.endswith(':')
        if left and right:
            alignments.append(Alignment.CENTER)
        elif right:
            alignments.append(Alignment.RIGHT)
        elif left:
            alignments.append(Alignment.LEFT)
        else:
            alignments.append(Alignment.DEFAULT)
    return alignments


def detect_pipe_table(lines, start_idx):
    """Detect a standard pipe table starting at ``lines[start_idx]``.

    Requires that ``lines[start_idx]`` contains '|' AND ``lines[start_idx + 1]``
    is a Baris_Pemisah with a matching column count. Collects following lines
    that contain '|' until a blank line (or a non-pipe line / end of input).

    Returns ``(end_idx, item)`` where ``end_idx`` is the index of the first line
    after the table and ``item`` is
    ``{'type':'table','lines':[header + data rows, WITHOUT separator],
       'alignments':[...], 'is_pipe':True}``. Returns ``None`` when no pipe
    table is present (so the caller falls through to existing behavior)."""
    n = len(lines)
    if start_idx + 1 >= n:
        return None
    header = lines[start_idx].strip()
    sep = lines[start_idx + 1].strip()
    if '|' not in header:
        return None
    if not is_pipe_table_separator(sep):
        return None
    if len(_split_pipe_cells(header)) != len(_split_pipe_cells(sep)):
        return None

    alignments = parse_alignment_row(sep)
    data_lines = [header]
    idx = start_idx + 2
    while idx < n:
        cur = lines[idx].strip()
        if cur == '' or '|' not in cur:
            break
        data_lines.append(cur)
        idx += 1

    item = {
        'type': 'table',
        'lines': data_lines,
        'alignments': alignments,
        'is_pipe': True,
    }
    return (idx, item)


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
        
    # Pipe-table per-column alignment metadata (R5). Absent for [TABLE] data,
    # so that path stays byte-identical to the frozen baseline oracle.
    alignments = item.get('alignments')

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
            
        for j, cell_text in enumerate(row_cells):
            tc = lxml.etree.SubElement(tr, f'{{{ns_uri}}}tc')
            tcPr = lxml.etree.SubElement(tc, f'{{{ns_uri}}}tcPr')
            lxml.etree.SubElement(tcPr, f'{{{ns_uri}}}tcW', {f'{{{ns_uri}}}w': '0', f'{{{ns_uri}}}type': 'auto'})
            
            p = lxml.etree.SubElement(tc, f'{{{ns_uri}}}p')
            pPr = lxml.etree.SubElement(p, f'{{{ns_uri}}}pPr')
            lxml.etree.SubElement(pPr, f'{{{ns_uri}}}pStyle', {f'{{{ns_uri}}}val': 'Normal'})
            # Without alignments (the [TABLE] path) this is always 'left',
            # byte-identical to the oracle. With alignments, apply per-column jc.
            if alignments and j < len(alignments):
                jc_val = alignments[j].value
            else:
                jc_val = 'left'
            lxml.etree.SubElement(pPr, f'{{{ns_uri}}}jc', {f'{{{ns_uri}}}val': jc_val})
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
    
    # Allocate a RelManager seeded with the existing relationship ids so any
    # hyperlink rIds we hand out never collide with what is already present.
    rels_path = os.path.join(os.path.dirname(xml_path), "_rels", "document.xml.rels")
    existing_rel_ids = set()
    if os.path.exists(rels_path):
        try:
            rels_tree = lxml.etree.parse(rels_path, parser)
            for rel in rels_tree.getroot():
                rid = rel.get('Id')
                if rid:
                    existing_rel_ids.add(rid)
        except lxml.etree.XMLSyntaxError as e:
            print(f"Warning: could not read existing rels {rels_path}: {e}")
    rel_manager = RelManager(existing_ids=existing_rel_ids)
    
    # Build and insert new XML elements
    new_elements = []
    for item in parsed_items:
        if item['type'] in ['heading', 'page_break', 'list_item', 'paragraph']:
            p_elem = build_p_element(item, rel_manager)
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
    
    # Persist any external hyperlink relationships additively. When no links
    # were emitted, this is a no-op and document.xml.rels stays untouched.
    if rel_manager.has_new:
        rel_manager.write(rels_path)
        print(f"Wrote {len(rel_manager._new)} hyperlink relationship(s) to {rels_path}.")

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
