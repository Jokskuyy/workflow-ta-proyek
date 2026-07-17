"""SkeletonGenerator — build the Kerangka_Bab (chapter skeleton).

This is a **pure** transformation component (design.md §2 "SkeletonGenerator").
Given the in-memory :class:`~alur_penulisan.draft_model.DraftModel` of
``Tugas_Akhir_Draft.md`` and the canonical outline, it ensures the draft
contains the full BAB I–IV structure with all baseline sub-chapters, in
canonical reading order, with hierarchical numbering (Requirements 1.1, 1.2).

Behaviour:

* Titles that already exist in the draft — matched while ignoring case and
  leading/trailing whitespace via :func:`title_matches` — are preserved together
  with their following content and are never duplicated (Requirement 1.3).
* When the draft already contains the complete skeleton (every canonical entry
  present), the draft is returned unchanged, i.e. the structure is not
  regenerated (Requirement 1.4).

The canonical outline mirrors ``skills/references/outline-4bab.md`` (the single
source of truth). It is embedded here as data so this component stays pure (no
file I/O), which keeps it easy to exercise with property-based tests.

Branch-role scoping (Requirement 9) is intentionally *not* applied here; that is
the job of the BranchScopeResolver. The ``scope`` parameter is accepted for
signature compatibility with the design and is currently informational only.
"""

from __future__ import annotations

from .draft_model import DraftBlock, DraftBlockType, DraftModel
from .models import BranchScope, Finding, Level, Skeleton, SkeletonEntry

# --------------------------------------------------------------------------- #
# Canonical outline (mirrors skills/references/outline-4bab.md)
# --------------------------------------------------------------------------- #
# Structure per BAB: (roman_numeral, bab_title, [sub-chapters]).
# Each sub-chapter: (numbering, title, [sub-sub-chapters]).
# Each sub-sub-chapter: (numbering, title).
_CANONICAL_SPEC: tuple = (
    ("I", "PENDAHULUAN", [
        ("1.1", "Latar Belakang", []),
        ("1.2", "Identifikasi Masalah", []),
        ("1.3", "Batasan Masalah", []),
        ("1.4", "Tujuan dan Manfaat", [
            ("1.4.1", "Tujuan"),
            ("1.4.2", "Manfaat"),
        ]),
        ("1.5", "Jadwal Kegiatan", []),
        ("1.6", "Sistematika Penulisan", []),
    ]),
    ("II", "RANCANGAN PROYEK", [
        ("2.1", "Observasi", [
            ("2.1.1", "Observasi Lapangan"),
            ("2.1.2", "Analisis Sistem Berjalan"),
            ("2.1.3", "Wawancara Stakeholder"),
        ]),
        ("2.2", "Usulan Solusi", [
            ("2.2.1", "Identifikasi Kebutuhan Fungsional"),
            ("2.2.2", "Identifikasi Kebutuhan Teknis"),
            ("2.2.3", "Identifikasi Kebutuhan Non-Fungsional"),
        ]),
        ("2.3", "Rancangan Proyek", [
            ("2.3.1", "Rencana Pengembangan"),
            ("2.3.2", "Perancangan Information Architecture (IA)"),
            ("2.3.3", "Perancangan UML"),
            ("2.3.4", "Perancangan Modul Keamanan & Analitik"),
            ("2.3.5", "Perancangan Entity Relationship Diagram (ERD)"),
            ("2.3.6", "Perancangan Antarmuka"),
        ]),
        ("2.4", "Rencana Pengujian Proyek", []),
    ]),
    ("III", "IMPLEMENTASI PROYEK", [
        ("3.1", "Profil Mitra", [
            ("3.1.1", "Nama"),
            ("3.1.2", "Deskripsi"),
            ("3.1.3", "Hubungan"),
        ]),
        ("3.2", "Metode Implementasi", [
            ("3.2.1", "Implementasi Back-end"),
            ("3.2.2", "Implementasi Front-end"),
            ("3.2.3", "Implementasi Integrasi (WebGL Bridge React-Unity)"),
        ]),
        ("3.3", "Konfigurasi & Metadata Sistem", [
            ("3.3.1", "Basis Data"),
            ("3.3.2", "Proxy Analytics (Umami)"),
            ("3.3.3", "Web Manifest / Web Assets"),
        ]),
        ("3.4", "Laporan Implementasi Proyek", [
            ("3.4.1", "Logbook Implementasi Proyek"),
            ("3.4.2", "Hasil & Bukti Implementasi Back-end"),
            ("3.4.3", "Hasil & Bukti Implementasi Front-end"),
        ]),
        ("3.5", "Hasil Pengujian Proyek", [
            ("3.5.1", "Black Box Testing"),
            ("3.5.2", "Lighthouse Testing / Performance"),
            ("3.5.3", "User Acceptance Test (UAT)"),
            ("3.5.4", "Implementasi Hasil UAT"),
        ]),
    ]),
    ("IV", "PENUTUP", [
        ("4.1", "Kesimpulan", []),
        ("4.2", "Saran", []),
    ]),
)


def _build_canonical_skeleton() -> Skeleton:
    """Construct the canonical :class:`Skeleton` from :data:`_CANONICAL_SPEC`."""
    entries: list[SkeletonEntry] = []
    for bab_index, (roman, bab_title, children) in enumerate(_CANONICAL_SPEC, start=1):
        entries.append(
            SkeletonEntry(
                entry_id=str(bab_index),
                numbering=roman,
                title=bab_title,
                level=Level.BAB,
                owner_role="",
            )
        )
        for sub_numbering, sub_title, sub_children in children:
            entries.append(
                SkeletonEntry(
                    entry_id=sub_numbering,
                    numbering=sub_numbering,
                    title=sub_title,
                    level=Level.SUBBAB,
                    owner_role="",
                )
            )
            for ss_numbering, ss_title in sub_children:
                entries.append(
                    SkeletonEntry(
                        entry_id=ss_numbering,
                        numbering=ss_numbering,
                        title=ss_title,
                        level=Level.SUBSUBBAB,
                        owner_role="",
                    )
                )
    return Skeleton(entries=tuple(entries))


# The canonical skeleton is immutable, so build it once at import time.
_CANONICAL_SKELETON: Skeleton = _build_canonical_skeleton()


def canonical_skeleton() -> Skeleton:
    """Return the canonical Kerangka_Bab (BAB I–IV with baseline sub-chapters)."""
    return _CANONICAL_SKELETON


# --------------------------------------------------------------------------- #
# Title comparison & heading rendering
# --------------------------------------------------------------------------- #
def _normalize_title(title: str) -> str:
    """Normalize a title for comparison: drop edge whitespace, ignore case."""
    return title.strip().casefold()


def title_matches(existing: str, canonical: str) -> bool:
    """True when two titles are equal ignoring case and leading/trailing spaces.

    Implements the comparison rule of Requirement 1.3: differences in letter
    case and edge whitespace are ignored; internal spacing is significant.
    """
    return _normalize_title(existing) == _normalize_title(canonical)


def entry_heading_text(entry: SkeletonEntry) -> str:
    """Return the canonical heading text for a skeleton entry.

    ``BAB`` entries render as ``"BAB {roman} {TITLE}"`` (e.g.
    ``"BAB I PENDAHULUAN"``); sub-chapters render as ``"{numbering} {title}"``
    (e.g. ``"1.1 Latar Belakang"``), applying hierarchical numbering per level
    (Requirement 1.2).
    """
    if entry.level is Level.BAB:
        return f"BAB {entry.numbering} {entry.title}"
    return f"{entry.numbering} {entry.title}"


def entry_heading_markdown(entry: SkeletonEntry) -> str:
    """Return the Markdown heading line for a skeleton entry.

    The number of ``#`` markers follows the entry level (BAB -> ``#``,
    SUBBAB -> ``##``, SUBSUBBAB -> ``###``), matching the grammar understood by
    ``merge_draft_to_docx.parse_markdown``.
    """
    prefix = "#" * entry.level.value
    return f"{prefix} {entry_heading_text(entry)}"


# --------------------------------------------------------------------------- #
# Skeleton generation
# --------------------------------------------------------------------------- #
def _split_sections(
    draft: DraftModel,
) -> "tuple[list[DraftBlock], list[tuple[DraftBlock, list[DraftBlock]]]]":
    """Split a draft into a preamble and heading-led sections.

    Returns ``(preamble, sections)`` where ``preamble`` is the run of blocks that
    precede the first heading, and each section is ``(heading_block, [content])``
    holding a heading and every block up to (but excluding) the next heading.
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


def _new_heading_block(entry: SkeletonEntry) -> DraftBlock:
    """Create a fresh heading block for a canonical entry (Requirements 1.1, 1.2)."""
    return DraftBlock(
        block_type=DraftBlockType.HEADING,
        lines=[entry_heading_markdown(entry)],
        meta={
            "level": entry.level.value,
            "text": entry_heading_text(entry),
            "is_bibliography": False,
        },
    )


def _blank_block() -> DraftBlock:
    """A single blank line, used to space out newly generated headings."""
    return DraftBlock(block_type=DraftBlockType.BLANK, lines=[""])


def generate_skeleton(
    draft: DraftModel,
    outline: "Skeleton | None" = None,
    scope: "BranchScope | None" = None,
) -> "tuple[DraftModel, list[Finding]]":
    """Ensure ``draft`` contains the full canonical Kerangka_Bab.

    * Produces BAB I–IV in canonical order with all baseline sub-chapters and
      hierarchical numbering (Requirements 1.1, 1.2).
    * Preserves headings that already exist — matched case-/edge-space-insensitively
      — together with their content, without adding duplicates (Requirement 1.3).
    * Returns the draft unchanged when the skeleton is already complete, i.e.
      every canonical entry is present, so the structure is not regenerated
      (Requirement 1.4).

    ``outline`` defaults to :func:`canonical_skeleton`. ``scope`` is accepted for
    design-signature compatibility but is not applied here (see module docstring).

    Returns a tuple of the (possibly new) :class:`DraftModel` and a list of
    :class:`Finding` (empty for the skeleton stage).
    """
    if outline is None:
        outline = canonical_skeleton()

    findings: list[Finding] = []

    preamble, sections = _split_sections(draft)

    # Match each canonical entry to at most one existing heading section.
    used = [False] * len(sections)
    matched: dict[str, tuple[DraftBlock, list[DraftBlock]]] = {}
    for entry in outline.entries:
        target = entry_heading_text(entry)
        for idx, (heading_block, content) in enumerate(sections):
            if used[idx]:
                continue
            if title_matches(heading_block.meta.get("text", ""), target):
                matched[entry.entry_id] = (heading_block, content)
                used[idx] = True
                break

    # Requirement 1.4: skeleton already complete -> do not regenerate.
    if len(matched) == len(outline.entries):
        return draft, findings

    # Rebuild the block list in canonical order, preserving matched sections and
    # inserting fresh headings for the missing entries.
    new_blocks: list[DraftBlock] = list(preamble)
    for entry in outline.entries:
        section = matched.get(entry.entry_id)
        if section is not None:
            heading_block, content = section
            new_blocks.append(heading_block)
            new_blocks.extend(content)
        else:
            new_blocks.append(_new_heading_block(entry))
            new_blocks.append(_blank_block())

    # Preserve any existing sections that did not match a canonical entry
    # (e.g. manual chapters) rather than discarding their content.
    for idx, (heading_block, content) in enumerate(sections):
        if not used[idx]:
            new_blocks.append(heading_block)
            new_blocks.extend(content)

    new_draft = DraftModel(blocks=new_blocks, trailing_newline=draft.trailing_newline)
    return new_draft, findings
