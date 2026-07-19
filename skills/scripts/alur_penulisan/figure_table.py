"""FigureTableManager — numbering and reference placement for Gambar/Tabel.

This module implements section "5. FigureTableManager" of the design document
(``.kiro/specs/automated-writing-workflow/design.md``). It is a **pure**
component: it takes a :class:`~alur_penulisan.draft_model.DraftModel` and returns
a new ``DraftModel`` plus a list of :class:`~alur_penulisan.models.Finding`,
without touching disk.

Responsibilities (Requirements 4.1–4.4):

* **Number objects** (``number_objects``) — assign every Gambar/Tabel a number
  ``x.y`` where ``x`` is the chapter number the object lives in and ``y`` is the
  1-based order of appearance (reading order) inside that chapter. The ``y``
  counter is reset to 1 at every new chapter and is tracked **separately** for
  Gambar and for Tabel (Requirements 4.2, 4.3).
* **Validate reference position** (``is_valid_reference_position``) — a
  Rujukan_Objek ("Gambar x.y" / "Tabel x.y") must not sit at the start of a
  paragraph nor immediately after a sentence terminator (``.`` ``?`` ``!``)
  (Requirement 4.1).
* **Dangling references** — a reference pointing to an object that is not (yet)
  numbered / does not exist produces ``Finding(DANGLING_REFERENCE)`` while the
  surrounding narrative is preserved verbatim (Requirement 4.4).

Modeling convention (consistent with ``merge_draft_to_docx.py``):

* A **caption** is a paragraph whose text starts with the keyword
  ``Gambar``/``Tabel`` (case-insensitive). Captions are the *numbered objects*;
  ``number_objects`` (re)assigns their ``x.y`` following reading order.
* A **reference** is a ``Gambar x.y``/``Tabel x.y`` mention that appears
  *within* narrative text (not at the very start of a paragraph). Because a
  keyword at the start of a paragraph is treated as a caption, every genuine
  reference is naturally mid-paragraph — matching Requirement 4.1.
"""

from __future__ import annotations

import re
from dataclasses import replace

from .draft_model import DraftBlock, DraftBlockType, DraftModel
from .models import Finding, FindingKind, ObjectKind

# --------------------------------------------------------------------------- #
# Regex grammar
# --------------------------------------------------------------------------- #
# A caption starts (after optional indentation) with the object keyword,
# optionally followed by an existing "x.y" number, then the description.
_CAPTION_RE = re.compile(
    r"^(?P<ws>\s*)(?P<kw>gambar|tabel)\b[ \t]*"
    r"(?P<num>\d+(?:\.\d+)*)?[ \t]*(?P<rest>.*)$",
    re.IGNORECASE,
)

# Any "Gambar <num>" / "Tabel <num>" token (used to locate references).
_OBJECT_TOKEN_RE = re.compile(
    r"(?P<kw>gambar|tabel)\s+(?P<num>\d+(?:\.\d+)*)",
    re.IGNORECASE,
)

_SEMANTIC_MARKER_RE = re.compile(
    r"^\s*\[(?P<kind>FIGURE|TABLE-ID):"
    r"(?P<id>[a-z0-9][a-z0-9_-]*)\]\s*$"
)
_SEMANTIC_REFERENCE_RE = re.compile(
    r"\[(?P<kind>FIGREF|TABREF):(?P<id>[a-z0-9][a-z0-9_-]*)\]"
)

# A chapter heading: "BAB <roman-or-arabic> ...".
_BAB_RE = re.compile(r"^\s*BAB\s+(?P<num>[IVXLCDM]+|\d+)\b", re.IGNORECASE)

_SENTENCE_TERMINATORS = frozenset(".?!")

_ROMAN_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _roman_to_int(text: str) -> "int | None":
    """Convert a Roman numeral to an int, or ``None`` if it is not valid."""
    total = 0
    prev = 0
    for ch in reversed(text.upper()):
        val = _ROMAN_VALUES.get(ch)
        if val is None:
            return None
        if val < prev:
            total -= val
        else:
            total += val
            prev = val
    return total if total > 0 else None


def _chapter_number(heading_text: str) -> "int | None":
    """Extract the chapter number from a heading like "BAB II ..." (or None)."""
    match = _BAB_RE.match(heading_text)
    if not match:
        return None
    token = match.group("num")
    if token.isdigit():
        return int(token)
    return _roman_to_int(token)


def _kind_word(keyword: str) -> str:
    """Normalize a matched keyword to its canonical ``ObjectKind`` value."""
    return ObjectKind.GAMBAR.value if keyword.lower() == "gambar" else ObjectKind.TABEL.value


def _is_caption_paragraph(block: DraftBlock) -> bool:
    """True when a paragraph block's first non-empty line is a caption."""
    if block.block_type not in (DraftBlockType.PARAGRAPH, DraftBlockType.PREAMBLE):
        return False
    for line in block.lines:
        stripped = line.strip()
        if stripped == "":
            continue
        low = stripped.lower()
        return low.startswith("gambar") or low.startswith("tabel")
    return False


def is_valid_reference_position(sentence: str, index: int) -> bool:
    """Return whether a Rujukan_Objek at ``index`` sits at a valid position.

    A reference is valid when it is neither at the beginning of the paragraph /
    sentence nor immediately after a sentence terminator (``.`` ``?`` ``!``),
    ignoring intervening whitespace (Requirement 4.1).

    Args:
        sentence: the surrounding text (paragraph or sentence).
        index: character offset at which the "Gambar"/"Tabel" phrase starts.

    Returns:
        ``True`` if the position is allowed, ``False`` otherwise.
    """
    if index <= 0:
        return False
    j = index - 1
    while j >= 0 and sentence[j].isspace():
        j -= 1
    if j < 0:
        # Only whitespace precedes the reference -> start of paragraph.
        return False
    return sentence[j] not in _SENTENCE_TERMINATORS


def _renumber_caption_line(line: str, number: str) -> str:
    """Rewrite the leading caption token of ``line`` to carry ``number``."""
    match = _CAPTION_RE.match(line)
    if not match:
        return line
    ws = match.group("ws")
    kind = _kind_word(match.group("kw"))
    rest = match.group("rest")
    rebuilt = f"{ws}{kind} {number}"
    if rest:
        rebuilt = f"{rebuilt} {rest}"
    return rebuilt.rstrip()


def _number_caption_block(block: DraftBlock, number: str) -> DraftBlock:
    """Return a copy of ``block`` with its caption line renumbered to ``number``."""
    new_lines = list(block.lines)
    for i, line in enumerate(new_lines):
        if line.strip() == "":
            continue
        new_lines[i] = _renumber_caption_line(line, number)
        break
    return replace(block, lines=new_lines, meta=dict(block.meta))


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def number_objects(draft: DraftModel) -> "tuple[DraftModel, list[Finding]]":
    """Number every Gambar/Tabel and report dangling references.

    Walks ``draft`` in reading order, assigning each caption a ``x.y`` number
    (chapter number + per-chapter, per-kind sequence starting at 1). References
    to objects that were never numbered are reported as
    ``Finding(DANGLING_REFERENCE)`` while their narrative is preserved
    (Requirements 4.2, 4.3, 4.4).

    Args:
        draft: the source draft model (not mutated).

    Returns:
        A tuple ``(new_draft, findings)`` where ``new_draft`` carries the
        renumbered captions and ``findings`` lists any dangling references.
    """
    current_chapter = 0
    # Per-chapter, per-kind running counters: {(chapter, kind_word): y}.
    counters: dict[tuple[int, str], int] = {}
    # Numbers actually assigned to captions, per kind: {kind_word: {"x.y", ...}}.
    assigned: dict[str, set[str]] = {
        ObjectKind.GAMBAR.value: set(),
        ObjectKind.TABEL.value: set(),
    }
    assigned_ids: set[tuple[str, str]] = set()

    new_blocks: list[DraftBlock] = []

    # Pass 1 — assign numbers to captions in reading order.
    for block in draft.blocks:
        if block.block_type == DraftBlockType.HEADING:
            chapter = _chapter_number(block.meta.get("text", ""))
            if chapter is not None:
                current_chapter = chapter
            new_blocks.append(block)
            continue

        semantic_markers = []
        for line in block.lines:
            semantic_match = _SEMANTIC_MARKER_RE.fullmatch(line)
            if semantic_match:
                kind = (
                    ObjectKind.GAMBAR.value
                    if semantic_match.group("kind") == "FIGURE"
                    else ObjectKind.TABEL.value
                )
                assigned_ids.add((kind, semantic_match.group("id")))
                semantic_markers.append(semantic_match.group(0))
        if semantic_markers:
            # ID-based objects are numbered later by the DOCX formatter through
            # SEQ fields.  Preserve their source text byte-for-byte here.
            new_blocks.append(block)
            continue

        if _is_caption_paragraph(block):
            # Determine kind from the caption keyword.
            first = next(l for l in block.lines if l.strip() != "")
            match = _CAPTION_RE.match(first)
            kind = _kind_word(match.group("kw"))
            key = (current_chapter, kind)
            seq_y = counters.get(key, 0) + 1
            counters[key] = seq_y
            number = f"{current_chapter}.{seq_y}"
            assigned[kind].add(number)
            new_blocks.append(_number_caption_block(block, number))
            continue

        new_blocks.append(block)

    numbered = DraftModel(blocks=new_blocks, trailing_newline=draft.trailing_newline)

    # Pass 2 — validate references against the numbers assigned above.
    findings: list[Finding] = []
    for position, block in enumerate(numbered.blocks):
        if block.block_type not in (DraftBlockType.PARAGRAPH, DraftBlockType.PREAMBLE):
            continue

        text = "\n".join(block.lines)
        is_caption = _is_caption_paragraph(block)

        for token in _OBJECT_TOKEN_RE.finditer(text):
            # The caption's own leading token is the object itself, not a
            # reference — skip the match anchored at the paragraph start.
            if is_caption and text[: token.start()].strip() == "":
                continue

            kind = _kind_word(token.group("kw"))
            number = token.group("num")
            if number not in assigned[kind]:
                findings.append(
                    Finding(
                        kind=FindingKind.DANGLING_REFERENCE,
                        location=f"blok#{position}",
                        detail=(
                            f"Rujukan_Objek '{kind} {number}' menunjuk objek yang "
                            f"belum bernomor atau tidak ada; narasi dipertahankan."
                        ),
                    )
                )

        for token in _SEMANTIC_REFERENCE_RE.finditer(text):
            kind = (
                ObjectKind.GAMBAR.value
                if token.group("kind") == "FIGREF"
                else ObjectKind.TABEL.value
            )
            object_id = token.group("id")
            if (kind, object_id) not in assigned_ids:
                findings.append(
                    Finding(
                        kind=FindingKind.DANGLING_REFERENCE,
                        location=f"blok#{position}",
                        detail=(
                            f"Rujukan_Objek '[{token.group('kind')}:{object_id}]' "
                            "menunjuk ID objek yang tidak ada; narasi dipertahankan."
                        ),
                    )
                )

    return numbered, findings
