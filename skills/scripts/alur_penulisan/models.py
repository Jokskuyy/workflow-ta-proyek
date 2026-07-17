"""Data models for the Alur_Penulisan (automated writing workflow).

These dataclasses and enums mirror the "Data Models" section of the design
document (``.kiro/specs/automated-writing-workflow/design.md``). They are pure
data carriers with no I/O, so they can be exercised freely by property-based
tests.

The block-oriented draft representation (:class:`DraftModel`) lives in
``draft_model.py`` and re-exports :class:`BlockKind` from here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# --------------------------------------------------------------------------- #
# Kerangka_Bab (chapter skeleton)
# --------------------------------------------------------------------------- #
class Level(Enum):
    """Hierarchical level of a skeleton entry."""

    BAB = 1
    SUBBAB = 2
    SUBSUBBAB = 3


@dataclass(frozen=True)
class SkeletonEntry:
    """One chapter / sub-chapter entry in the Kerangka_Bab."""

    entry_id: str          # e.g. "2.3.5"
    numbering: str         # displayed hierarchical numbering ("2.3.5")
    title: str             # canonical title
    level: Level
    owner_role: str        # branch role responsible for this entry


@dataclass(frozen=True)
class Skeleton:
    """Ordered collection of skeleton entries (order == canonical reading order)."""

    entries: tuple[SkeletonEntry, ...] = ()


# --------------------------------------------------------------------------- #
# Content blocks
# --------------------------------------------------------------------------- #
class BlockKind(Enum):
    """Origin of a content block, used to protect Konten_Manual."""

    GENERATED = "generated"
    MANUAL = "manual"


@dataclass
class Paragraph:
    """A single paragraph of body text."""

    text: str
    is_definition: bool = False


@dataclass
class ContentBlock:
    """The content associated with a single skeleton entry."""

    entry_id: str
    paragraphs: list[Paragraph] = field(default_factory=list)
    kind: BlockKind = BlockKind.GENERATED


# --------------------------------------------------------------------------- #
# Daftar_Berjenjang (nested numbered list)
# --------------------------------------------------------------------------- #
@dataclass
class ListNode:
    """A node in a nested list tree.

    Marker per level: ``{1: "1.", 2: "a.", 3: "1)", 4: "a)"}``; levels deeper
    than 4 are clamped to level 4 by the ListFormatter.
    """

    text: str
    children: list["ListNode"] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Gambar / Tabel numbering & references
# --------------------------------------------------------------------------- #
class ObjectKind(Enum):
    """Kind of a numbered object (figure or table)."""

    GAMBAR = "Gambar"
    TABEL = "Tabel"


@dataclass(frozen=True)
class NumberedObject:
    """A figure or table with an assigned ``x.y`` number."""

    kind: ObjectKind
    bab: int
    seq_y: int             # sequence within the chapter (starts at 1)
    number: str            # "x.y"


@dataclass(frozen=True)
class ObjectReference:
    """An in-narrative reference ("Gambar x.y" / "Tabel x.y")."""

    kind: ObjectKind
    number: str            # referenced "x.y"
    para_offset: int       # position within the paragraph (placement rule 4.1)


# --------------------------------------------------------------------------- #
# Basis_Fakta & Placeholder_TBD
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class FactValue:
    """Result of resolving a fact against Basis_Fakta."""

    key: str
    present: bool
    value: "str | None" = None       # exact value from Basis_Fakta when present
    tbd_reason: "str | None" = None   # description when it becomes a Placeholder_TBD


# --------------------------------------------------------------------------- #
# Term consistency
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class TermRegistry:
    """Registered canonical forms of project terms."""

    canonical: dict[str, str] = field(default_factory=dict)   # lower form -> canonical form


@dataclass(frozen=True)
class TermOccurrence:
    """A single occurrence of a term in the draft."""

    form: str
    line: int


@dataclass
class InconsistencyReport:
    """Report of two or more differing forms for one concept."""

    concept_key: str
    forms: list[TermOccurrence] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Peran_Branch (branch role scope)
# --------------------------------------------------------------------------- #
class ScopeState(Enum):
    """Whether the active branch role could be resolved."""

    RESOLVED = "resolved"
    UNDETERMINED = "undetermined"


@dataclass(frozen=True)
class BranchScope:
    """The resolved (or undetermined) scope of the active branch role."""

    state: ScopeState
    role: "str | None" = None            # "iman" | "dwikhi" | "faiz" | None
    owned_entries: frozenset[str] = frozenset()


# --------------------------------------------------------------------------- #
# Findings & report
# --------------------------------------------------------------------------- #
class FindingKind(Enum):
    """Kind of a finding collected during the workflow."""

    TBD = "tbd"
    MISSING_CITATION = "missing_citation"
    TERM_INCONSISTENCY = "term_inconsistency"
    DANGLING_REFERENCE = "dangling_reference"
    MISSING_ENTRY = "missing_entry"
    ORPHAN_CONTENT = "orphan_content"
    OUT_OF_SCOPE = "out_of_scope"


@dataclass(frozen=True)
class Finding:
    """A single non-fatal (or fatal-precursor) finding."""

    kind: FindingKind
    location: str
    detail: str


@dataclass
class WriterReport:
    """Aggregated findings surfaced to the writer at the end of a run."""

    findings: list[Finding] = field(default_factory=list)
    active_role: "str | None" = None
