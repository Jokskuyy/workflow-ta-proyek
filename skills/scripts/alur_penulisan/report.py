"""ReportBuilder — aggregate findings into a WriterReport and handle empty
mandatory sections (design.md §11 "ReportBuilder").

This is a **pure** transformation component: it operates on the in-memory
:class:`~alur_penulisan.draft_model.DraftModel` and on lists of
:class:`~alur_penulisan.models.Finding`, and never touches disk.

Responsibilities (Requirements 10.4, 10.5):

* **Aggregate findings** (:func:`build_report`) — collect every finding surfaced
  during a run into a single :class:`~alur_penulisan.models.WriterReport`:
  Placeholder_TBD (``[TBD: ...]``) together with their cause (Requirement 10.5),
  Penanda_Sitasi_Kurang (``[BUTUH SITASI]``), term inconsistencies, and dangling
  object references. The active branch role is echoed on the report.
* **Fill empty mandatory sections** (:func:`fill_empty_mandatory_sections`) — for
  every *bagian wajib* (mandatory leaf section of the canonical Kerangka_Bab)
  that exists as a heading in an accessible Berkas_Draf but has an empty body,
  write a Placeholder_TBD into that section (Requirement 10.4, Property 26).
* **Report every Placeholder_TBD** (:func:`collect_tbd_findings`) — scan the draft
  for ``[TBD: ...]`` markers and emit exactly one ``Finding(TBD)`` per marker,
  carrying its cause. This guarantees the number of TBD report entries equals the
  number of Placeholder_TBD in the draft (Requirement 10.5, Property 27).

"Bagian wajib" (mandatory sections) are the **leaf** entries of the canonical
outline — the sections that must carry prose. Parent entries (a BAB or a
sub-chapter that only groups deeper sub-sections) are not themselves expected to
hold body text, so an empty parent is not flagged; its leaf descendants are.
"""

from __future__ import annotations

import re

from .draft_model import DraftBlock, DraftBlockType, DraftModel
from .models import Finding, FindingKind, Skeleton, SkeletonEntry, WriterReport
from .skeleton import canonical_skeleton, entry_heading_text, title_matches

# --------------------------------------------------------------------------- #
# Placeholder_TBD grammar
# --------------------------------------------------------------------------- #
# A Placeholder_TBD marker: "[TBD: <reason>]". The reason may be empty and must
# not contain a closing bracket. Matching is done on the rendered Markdown so it
# covers markers written anywhere in the draft (headings, paragraphs, lists,
# captions, ...).
TBD_MARKER_RE = re.compile(r"\[TBD:\s*(?P<reason>[^\]]*?)\s*\]")

# Content block types that count as real body content (a section holding only
# blanks / page breaks is considered empty).
_CONTENT_BLOCK_TYPES = frozenset(
    {
        DraftBlockType.PARAGRAPH,
        DraftBlockType.PREAMBLE,
        DraftBlockType.LIST,
        DraftBlockType.CODE,
        DraftBlockType.TABLE,
        DraftBlockType.PIPE_TABLE,
    }
)


def make_tbd_marker(reason: str) -> str:
    """Return a Placeholder_TBD marker string ``[TBD: <reason>]``."""
    return f"[TBD: {reason}]"


# --------------------------------------------------------------------------- #
# Mandatory sections (bagian wajib)
# --------------------------------------------------------------------------- #
def _is_leaf_entry(entry: SkeletonEntry, outline: Skeleton) -> bool:
    """True when ``entry`` has no deeper sub-section in ``outline``.

    Leaf entries are the sections expected to carry prose; a parent entry (whose
    ``entry_id`` is a dotted prefix of another entry's id) merely groups deeper
    sections and is not itself a mandatory prose section.
    """
    prefix = entry.entry_id + "."
    return not any(other.entry_id.startswith(prefix) for other in outline.entries)


def mandatory_sections(outline: "Skeleton | None" = None) -> "tuple[SkeletonEntry, ...]":
    """Return the mandatory (leaf) sections of the canonical Kerangka_Bab.

    These are the *bagian wajib* that must contain content; an accessible draft
    whose heading for one of these sections has an empty body triggers a
    Placeholder_TBD (Requirement 10.4).
    """
    if outline is None:
        outline = canonical_skeleton()
    return tuple(e for e in outline.entries if _is_leaf_entry(e, outline))


# --------------------------------------------------------------------------- #
# Section splitting
# --------------------------------------------------------------------------- #
def _split_sections(
    draft: DraftModel,
) -> "tuple[list[DraftBlock], list[tuple[DraftBlock, list[DraftBlock]]]]":
    """Split ``draft`` into a preamble and heading-led sections.

    Returns ``(preamble, sections)`` where each section is
    ``(heading_block, [content_blocks])`` holding a heading and every block up to
    (but excluding) the next heading of any level.
    """
    preamble: list[DraftBlock] = []
    sections: list[tuple[DraftBlock, list[DraftBlock]]] = []
    current_content: "list[DraftBlock] | None" = None

    for block in draft.blocks:
        if block.block_type == DraftBlockType.HEADING:
            current_content = []
            sections.append((block, current_content))
        elif current_content is None:
            preamble.append(block)
        else:
            current_content.append(block)

    return preamble, sections


def _has_body_content(content: list[DraftBlock]) -> bool:
    """True when ``content`` contains at least one non-blank body block."""
    for block in content:
        if block.block_type not in _CONTENT_BLOCK_TYPES:
            continue
        if any(line.strip() != "" for line in block.lines):
            return True
    return False


def _blank_block() -> DraftBlock:
    """A single blank line used to space generated content."""
    return DraftBlock(block_type=DraftBlockType.BLANK, lines=[""])


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def find_empty_mandatory_sections(
    draft: DraftModel,
    outline: "Skeleton | None" = None,
) -> "list[tuple[int, SkeletonEntry]]":
    """Return mandatory sections present in ``draft`` but with an empty body.

    A section is *empty* when its heading matches a mandatory (leaf) canonical
    entry — compared case-/edge-space-insensitively via
    :func:`~alur_penulisan.skeleton.title_matches` — and there is no non-blank
    body block between that heading and the next heading (Requirement 10.4).

    Args:
        draft: the source draft model (not mutated).
        outline: the canonical outline; defaults to :func:`canonical_skeleton`.

    Returns:
        A list of ``(section_index, entry)`` pairs in draft order, where
        ``section_index`` is the index of the section within the heading-led
        sections of the draft.
    """
    if outline is None:
        outline = canonical_skeleton()

    mandatory = mandatory_sections(outline)
    _, sections = _split_sections(draft)

    empty: list[tuple[int, SkeletonEntry]] = []
    for idx, (heading_block, content) in enumerate(sections):
        heading_text = heading_block.meta.get("text", "")
        entry = next(
            (e for e in mandatory if title_matches(heading_text, entry_heading_text(e))),
            None,
        )
        if entry is None:
            continue
        if not _has_body_content(content):
            empty.append((idx, entry))
    return empty


def fill_empty_mandatory_sections(
    draft: DraftModel,
    outline: "Skeleton | None" = None,
) -> "tuple[DraftModel, list[Finding]]":
    """Write a Placeholder_TBD into every empty mandatory section.

    For each *bagian wajib* whose heading exists in the accessible ``draft`` but
    whose body is empty, a ``[TBD: ...]`` paragraph is inserted directly under the
    heading and a ``Finding(TBD)`` is emitted describing the cause
    (Requirement 10.4, Property 26). Sections that already carry content are left
    untouched.

    Args:
        draft: the source draft model (not mutated).
        outline: the canonical outline; defaults to :func:`canonical_skeleton`.

    Returns:
        A tuple ``(new_draft, findings)`` where ``new_draft`` carries the inserted
        placeholders and ``findings`` reports one ``Finding(TBD)`` per filled
        section.
    """
    if outline is None:
        outline = canonical_skeleton()

    empty = dict(find_empty_mandatory_sections(draft, outline))
    if not empty:
        return draft, []

    preamble, sections = _split_sections(draft)
    findings: list[Finding] = []

    new_blocks: list[DraftBlock] = list(preamble)
    for idx, (heading_block, content) in enumerate(sections):
        new_blocks.append(heading_block)
        entry = empty.get(idx)
        if entry is None:
            new_blocks.extend(content)
            continue

        reason = f'konten bagian wajib "{entry.title}" belum tersedia'
        tbd_paragraph = DraftBlock(
            block_type=DraftBlockType.PARAGRAPH,
            lines=[make_tbd_marker(reason)],
        )
        # Replace the (blank-only) body with: blank, [TBD ...], blank so the
        # placeholder is cleanly separated from the surrounding headings.
        new_blocks.append(_blank_block())
        new_blocks.append(tbd_paragraph)
        new_blocks.append(_blank_block())

        findings.append(
            Finding(
                kind=FindingKind.TBD,
                location=entry.numbering or entry.entry_id,
                detail=f"Bagian wajib kosong: {reason}.",
            )
        )

    new_draft = DraftModel(blocks=new_blocks, trailing_newline=draft.trailing_newline)
    return new_draft, findings


def collect_tbd_findings(draft: DraftModel) -> list[Finding]:
    """Emit one ``Finding(TBD)`` for every Placeholder_TBD marker in ``draft``.

    Scans each block for ``[TBD: <reason>]`` markers and reports each occurrence
    with its cause taken from the marker's ``reason`` text. The number of findings
    returned equals the number of ``[TBD: ...]`` markers in the draft
    (Requirement 10.5, Property 27).

    Args:
        draft: the draft model to scan (not mutated).

    Returns:
        A list of ``Finding(TBD)`` in reading order, one per marker.
    """
    findings: list[Finding] = []
    for position, block in enumerate(draft.blocks):
        text = "\n".join(block.lines)
        for match in TBD_MARKER_RE.finditer(text):
            reason = match.group("reason").strip()
            detail = (
                f"Placeholder_TBD: {reason}"
                if reason
                else "Placeholder_TBD tanpa deskripsi."
            )
            findings.append(
                Finding(
                    kind=FindingKind.TBD,
                    location=f"blok#{position}",
                    detail=detail,
                )
            )
    return findings


def build_report(
    findings: list[Finding],
    draft: "DraftModel | None" = None,
    active_role: "str | None" = None,
) -> WriterReport:
    """Aggregate findings into a :class:`WriterReport` (design.md §11).

    Collects every finding surfaced during a run — Placeholder_TBD with cause
    (Requirement 10.5), Penanda_Sitasi_Kurang, term inconsistencies, and dangling
    object references — into a single report.

    When ``draft`` is provided, the TBD findings are (re)derived directly from the
    draft's ``[TBD: ...]`` markers so the number of reported TBD entries matches
    the number of Placeholder_TBD in the draft exactly (Property 27); any TBD
    findings already present in ``findings`` are superseded by the draft-derived
    ones to avoid double counting. Non-TBD findings are preserved in their
    original order. When ``draft`` is ``None``, the findings are aggregated as
    given.

    Args:
        findings: findings collected from the pipeline components.
        draft: optional final draft used to reconcile TBD findings with markers.
        active_role: the active branch role to echo on the report.

    Returns:
        A :class:`WriterReport` carrying the aggregated findings and active role.
    """
    if draft is None:
        collected = list(findings)
    else:
        non_tbd = [f for f in findings if f.kind is not FindingKind.TBD]
        collected = non_tbd + collect_tbd_findings(draft)

    return WriterReport(findings=collected, active_role=active_role)
