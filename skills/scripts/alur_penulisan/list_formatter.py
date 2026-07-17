"""ListFormatter — render Daftar_Berjenjang (nested numbered lists) as Markdown.

This is a **pure** transformation component (design.md §4 "ListFormatter"). It
takes a tree of :class:`~alur_penulisan.models.ListNode` and emits Markdown
lines that satisfy the project's list-formatting rules
(``.kiro/steering/aturan-penulisan.md``, Requirements 3.1–3.5):

* Level markers 1–4 are ``1.``, ``a.``, ``1)``, ``a)`` (Requirement 3.1).
* Siblings on the same level are numbered sequentially, incrementing by one and
  starting from ``1`` / ``a`` (Requirement 3.2).
* Each new sub-level resets to its initial marker (Requirement 3.3).
* Depth greater than 4 keeps the level-4 marker ``a)`` (Requirement 3.4) via
  :func:`clamp_level`, while indentation still tracks the true logical depth so
  ``merge_draft_to_docx.compute_list_level`` recovers the same level.
* Bullet markers (``-``, ``*``, ``+``) are never used (Requirement 3.5).

Output is indented 3 spaces per level, matching ``LIST_INDENT_UNIT = 3`` in
``merge_draft_to_docx.py`` so drafts stay compatible with the ``.docx`` format
pipeline (the format stage is never modified here).
"""

from __future__ import annotations

from collections.abc import Iterable

from .draft_model import LIST_INDENT_UNIT
from .models import ListNode

# Highest level that has a distinct marker; deeper items reuse this marker.
MAX_LIST_LEVEL = 4


def clamp_level(level: int) -> int:
    """Clamp a nesting level to the range ``[1, MAX_LIST_LEVEL]``.

    Levels below 1 are treated as level 1, and any depth greater than 4 is
    pinned to level 4 so the level-4 marker (``a)``) is reused for deeper items
    (Requirement 3.4).
    """
    if level < 1:
        return 1
    if level > MAX_LIST_LEVEL:
        return MAX_LIST_LEVEL
    return level


def _alpha_label(index: int) -> str:
    """Return a lowercase alphabetic label for a zero-based ``index``.

    ``0 -> 'a'``, ``25 -> 'z'``, ``26 -> 'aa'`` (spreadsheet-style), so lists
    longer than 26 siblings still get unique, ordered markers.
    """
    if index < 0:
        index = 0
    label = ""
    n = index
    while True:
        label = chr(ord("a") + (n % 26)) + label
        n = n // 26 - 1
        if n < 0:
            break
    return label


def marker_for_level(level: int, index: int = 0) -> str:
    """Return the list marker for ``level`` and zero-based sibling ``index``.

    The marker *style* is fixed per (clamped) level — numeric with ``.`` for
    level 1, alphabetic with ``.`` for level 2, numeric with ``)`` for level 3,
    alphabetic with ``)`` for level 4 (and any deeper level). ``index`` selects
    the sequential value within that level (Requirement 3.2): ``index=0`` yields
    the initial marker (``1.``, ``a.``, ``1)``, ``a)``).
    """
    clamped = clamp_level(level)
    if index < 0:
        index = 0
    # Levels 1 and 3 use numeric symbols; levels 2 and 4 use alphabetic symbols.
    if clamped in (1, 3):
        symbol = str(index + 1)
    else:
        symbol = _alpha_label(index)
    # Levels 1 and 2 use '.', levels 3 and 4 use ')'.
    suffix = "." if clamped in (1, 2) else ")"
    return f"{symbol}{suffix}"


def render_list(tree: "Iterable[ListNode] | ListNode") -> list[str]:
    """Render a nested list tree into Markdown lines.

    ``tree`` is the forest of top-level :class:`ListNode` items (a single
    ``ListNode`` is also accepted for convenience). Each returned line is
    ``<indent><marker> <text>`` where ``<indent>`` is ``LIST_INDENT_UNIT`` spaces
    per level of depth (starting at 0 for level 1). No bullet markers are ever
    emitted (Requirement 3.5).
    """
    if isinstance(tree, ListNode):
        nodes: list[ListNode] = [tree]
    else:
        nodes = list(tree)

    lines: list[str] = []
    _render_nodes(nodes, level=1, lines=lines)
    return lines


def _render_nodes(nodes: list[ListNode], level: int, lines: list[str]) -> None:
    """Append rendered lines for ``nodes`` at ``level`` (siblings reset to 1/a)."""
    indent = " " * (LIST_INDENT_UNIT * (level - 1))
    for index, node in enumerate(nodes):
        marker = marker_for_level(level, index)
        lines.append(f"{indent}{marker} {node.text}")
        if node.children:
            _render_nodes(node.children, level + 1, lines)
