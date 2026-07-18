"""Block-oriented in-memory representation of Berkas_Draf with Markdown round-trip.

``DraftModel`` parses the Markdown text of ``Tugas_Akhir_Draft.md`` into an
ordered list of typed blocks and can serialize them back to Markdown text. The
round-trip is *lossless*: ``DraftModel.from_markdown(text).to_markdown() == text``
for any input text.

The block classification deliberately mirrors the grammar understood by
``skills/scripts/merge_draft_to_docx.parse_markdown`` — headings (``#``), nested
numbered lists (3-space indentation), ``[TABLE]``/``[/TABLE]`` blocks, GitHub
pipe tables, page breaks (``---``) and the ``# DAFTAR PUSTAKA`` section — so any
draft produced from a ``DraftModel`` stays compatible with the existing ``.docx``
format pipeline (Requirements 7.2, 8.2). This module does NOT modify the format
stage; it only produces compatible Markdown.

Konten_Manual is tracked at the block level via :class:`~alur_penulisan.models.BlockKind`
so the IdempotentMerger can preserve manually written blocks untouched.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

from .models import BlockKind

# Indentation unit for nested lists — matches ``LIST_INDENT_UNIT`` in
# merge_draft_to_docx.py (3 spaces per nesting level).
LIST_INDENT_UNIT = 3

# List item marker grammar identical to merge_draft_to_docx.py.
_LIST_ITEM_RE = re.compile(r"^(\s*)([0-9a-zA-Z]+[\.\)])\s+(.*)$")

# A pipe-table separator cell: optional leading/trailing ':' around dashes.
_SEPARATOR_CELL_RE = re.compile(r"^:?-+:?$")

# The '# DAFTAR PUSTAKA' heading (case-insensitive).
_DAFTAR_PUSTAKA_RE = re.compile(r"^\s*#\s+DAFTAR\s+PUSTAKA\s*$", re.IGNORECASE)


class DraftBlockType(Enum):
    """Structural type of a draft block (mirrors parse_markdown item types)."""

    PREAMBLE = "preamble"        # content before the first '# BAB I' heading
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"                # a run of nested numbered list items
    CODE = "code"                # fenced ``` code block
    TABLE = "table"              # [TABLE] ... [/TABLE] block
    PIPE_TABLE = "pipe_table"    # GitHub pipe table
    PAGE_BREAK = "page_break"    # '---'
    BLANK = "blank"              # a run of blank lines


@dataclass
class DraftBlock:
    """A single structural block of the draft.

    ``lines`` holds the verbatim source lines (without trailing newlines) so the
    block can be re-emitted exactly. ``meta`` carries parsed attributes (e.g.
    heading level/text). ``kind`` marks whether the block is generated or
    Konten_Manual.
    """

    block_type: DraftBlockType
    lines: list[str] = field(default_factory=list)
    kind: BlockKind = BlockKind.GENERATED
    meta: dict = field(default_factory=dict)

    def text(self) -> str:
        """The block rendered as Markdown text (lines joined by newlines)."""
        return "\n".join(self.lines)


def _split_pipe_cells(line: str) -> list[str]:
    """Split a pipe-table line into trimmed cells, dropping outer-pipe empties."""
    cells = [c.strip() for c in line.split("|")]
    if cells and cells[0] == "":
        cells = cells[1:]
    if cells and cells[-1] == "":
        cells = cells[:-1]
    return cells


def _is_pipe_table_separator(line: str) -> bool:
    """True when every cell of ``line`` matches the separator pattern."""
    cells = _split_pipe_cells(line)
    if not cells:
        return False
    return all(_SEPARATOR_CELL_RE.match(c) for c in cells)


def _is_pipe_table_start(lines: list[str], idx: int) -> bool:
    """True when a pipe table begins at ``lines[idx]`` (header + separator)."""
    if idx + 1 >= len(lines):
        return False
    header = lines[idx].strip()
    sep = lines[idx + 1].strip()
    if "|" not in header:
        return False
    if not _is_pipe_table_separator(sep):
        return False
    return len(_split_pipe_cells(header)) == len(_split_pipe_cells(sep))


@dataclass
class DraftModel:
    """Ordered, block-oriented representation of a Markdown draft."""

    blocks: list[DraftBlock] = field(default_factory=list)
    trailing_newline: bool = False

    # ------------------------------------------------------------------ #
    # Round-trip
    # ------------------------------------------------------------------ #
    @classmethod
    def from_markdown(cls, text: str) -> "DraftModel":
        """Parse Markdown ``text`` into a :class:`DraftModel` (lossless)."""
        if text == "":
            return cls(blocks=[], trailing_newline=False)

        lines = text.split("\n")
        trailing_newline = False
        # A trailing '\n' produces a final empty element in ``split`` — record
        # it as ``trailing_newline`` instead of a spurious blank line.
        if lines and lines[-1] == "":
            trailing_newline = True
            lines = lines[:-1]

        blocks: list[DraftBlock] = []
        seen_bab = False
        i = 0
        n = len(lines)

        while i < n:
            line = lines[i]
            stripped = line.strip()

            # Preamble: everything before the first '# BAB I' heading is kept
            # verbatim so it round-trips (parse_markdown skips it, but the draft
            # file may carry a title page / front matter).
            is_bab_heading = stripped.startswith("# BAB I") or stripped.startswith("# BAB 1")
            if not seen_bab and stripped.startswith("#") and is_bab_heading:
                seen_bab = True

            # Fenced code block.
            if stripped.startswith("```"):
                start = i
                i += 1
                while i < n and not lines[i].strip().startswith("```"):
                    i += 1
                if i < n:  # include the closing fence
                    i += 1
                blocks.append(DraftBlock(DraftBlockType.CODE, lines[start:i]))
                continue

            # [TABLE] ... [/TABLE] block.
            if stripped.startswith("[TABLE") and not stripped.startswith("[/"):
                start = i
                inner = stripped[len("[TABLE"):].split("]", 1)[0].strip()
                i += 1
                while i < n and not lines[i].strip().endswith("[/TABLE]"):
                    i += 1
                if i < n:  # include the closing marker
                    i += 1
                blocks.append(
                    DraftBlock(
                        DraftBlockType.TABLE,
                        lines[start:i],
                        meta={"mode": inner or None},
                    )
                )
                continue

            # Blank line run.
            if stripped == "":
                start = i
                while i < n and lines[i].strip() == "":
                    i += 1
                blocks.append(DraftBlock(DraftBlockType.BLANK, lines[start:i]))
                continue

            # Page break.
            if stripped == "---":
                blocks.append(DraftBlock(DraftBlockType.PAGE_BREAK, [line]))
                i += 1
                continue

            # Heading.
            if stripped.startswith("#"):
                level = 0
                while level < len(stripped) and stripped[level] == "#":
                    level += 1
                heading_text = stripped[level:].strip()
                blocks.append(
                    DraftBlock(
                        DraftBlockType.HEADING,
                        [line],
                        meta={
                            "level": level,
                            "text": heading_text,
                            "is_bibliography": bool(_DAFTAR_PUSTAKA_RE.match(line)),
                        },
                    )
                )
                i += 1
                continue

            # Pipe table (header + separator + data rows).
            if "|" in stripped and _is_pipe_table_start(lines, i):
                start = i
                i += 2  # consume header + separator
                while i < n and lines[i].strip() != "" and "|" in lines[i].strip():
                    i += 1
                blocks.append(DraftBlock(DraftBlockType.PIPE_TABLE, lines[start:i]))
                continue

            # Nested numbered list run.
            if _LIST_ITEM_RE.match(line):
                start = i
                while i < n and _LIST_ITEM_RE.match(lines[i]):
                    i += 1
                blocks.append(DraftBlock(DraftBlockType.LIST, lines[start:i]))
                continue

            # Plain paragraph run (consecutive non-blank lines that do not open
            # any other block type).
            start = i
            while i < n:
                cur = lines[i]
                cur_stripped = cur.strip()
                if cur_stripped == "":
                    break
                if cur_stripped.startswith("#") or cur_stripped == "---":
                    break
                if cur_stripped.startswith("```"):
                    break
                if cur_stripped.startswith("[TABLE") and not cur_stripped.startswith("[/"):
                    break
                if "|" in cur_stripped and _is_pipe_table_start(lines, i):
                    break
                if _LIST_ITEM_RE.match(cur):
                    break
                i += 1
            block_type = DraftBlockType.PARAGRAPH if seen_bab else DraftBlockType.PREAMBLE
            blocks.append(DraftBlock(block_type, lines[start:i]))

        return cls(blocks=blocks, trailing_newline=trailing_newline)

    def to_markdown(self) -> str:
        """Serialize the model back to Markdown text (inverse of ``from_markdown``)."""
        parts: list[str] = []
        for block in self.blocks:
            parts.extend(block.lines)
        text = "\n".join(parts)
        if self.trailing_newline:
            text += "\n"
        return text

    # ------------------------------------------------------------------ #
    # Convenience accessors
    # ------------------------------------------------------------------ #
    def headings(self) -> list[DraftBlock]:
        """All heading blocks in document order."""
        return [b for b in self.blocks if b.block_type == DraftBlockType.HEADING]

    def manual_blocks(self) -> list[DraftBlock]:
        """All blocks marked as Konten_Manual (``BlockKind.MANUAL``)."""
        return [b for b in self.blocks if b.kind == BlockKind.MANUAL]
