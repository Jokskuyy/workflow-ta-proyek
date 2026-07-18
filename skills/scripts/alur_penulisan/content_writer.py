"""SectionContentWriter — compose Sub_Bab_Teori content with cited definitions.

This is a **pure** transformation component (design.md §3 "SectionContentWriter").
It composes the content of a theory sub-chapter (Sub_Bab_Teori) so that it obeys
the project's citation rules (``.kiro/steering/aturan-sitasi.md``):

* Exactly **one** definition paragraph is placed as the *first* paragraph of the
  sub-chapter, stating the definition of the main concept (Requirement 2.1).
* The definition paragraph must carry at least one attached author-year citation
  ``(Nama Tahun)`` / ``(Nama et al. Tahun)`` (Requirement 2.2). Because this
  workflow must never fabricate sources, a generated definition scaffold has no
  citation and is therefore flagged.
* A factual claim that is neither common knowledge nor the author's own
  observation and that lacks an APA citation is marked with the
  Penanda_Sitasi_Kurang ``[BUTUH SITASI]`` **at the claim**, without deleting any
  text (Requirement 2.3).
* When the sub-chapter ends up without a cited definition on paragraph 1, the
  first paragraph is marked with ``[BUTUH SITASI]`` (Requirement 2.4).
* An APA citation with no matching entry in the Daftar Pustaka is marked with
  ``[BUTUH SITASI]`` and its claim is *not* treated as validated
  (Requirement 2.5).

All marking is **idempotent**: re-running over already-marked text does not add
duplicate markers, which keeps the surrounding pipeline safe to re-run
(Requirement 8 spirit). The component performs no I/O and can be exercised freely
by property-based tests.

The Daftar Pustaka is modelled here as :class:`BibliographyResult`: a small
collection of bibliography keys with a membership check that answers "does this
citation have a matching entry?" (design.md §3 ``bib: BibliographyResult``).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .fact_verifier import FactStore
from .models import ContentBlock, Finding, FindingKind, Paragraph, SkeletonEntry

# --------------------------------------------------------------------------- #
# Markers
# --------------------------------------------------------------------------- #
#: Penanda_Sitasi_Kurang written next to claims/citations that lack a source.
MISSING_CITATION_MARKER = "[BUTUH SITASI]"

# --------------------------------------------------------------------------- #
# APA in-text citation grammar
# --------------------------------------------------------------------------- #
# A parenthetical group, e.g. ``(Muharam et al. 2023; Taurusta et al. 2024)``.
_PAREN_RE = re.compile(r"\(([^()]*)\)")

# A single source inside a group: ``Nama Tahun`` / ``Nama et al. Tahun`` where
# Tahun is a 4-digit year with an optional disambiguation letter (``2023a``).
# A comma is intentionally rejected by the campus-specific citation rule.
_SOURCE_RE = re.compile(
    r"^\s*(?P<name>[^,;]+?)\s+(?P<year>\d{4}[a-z]?)\s*$"
)

# A 4-digit year (with optional letter), used when normalizing bibliography keys.
_YEAR_RE = re.compile(r"\b(\d{4}[a-z]?)\b")

# Author self-observation cues (steering: "berdasarkan hasil kuesioner
# (Lampiran 1)") — such statements are backed by the author's own data/appendix
# rather than external literature, so they do not require an external citation.
_OBSERVATION_RE = re.compile(
    r"\b(lampiran|hasil\s+kuesioner|hasil\s+pengujian|observasi\s+penulis|"
    r"data\s+penulis|hasil\s+uat|hasil\s+wawancara)\b",
    re.IGNORECASE,
)


# --------------------------------------------------------------------------- #
# Citation model & parsing
# --------------------------------------------------------------------------- #
def _normalize_name(name: str) -> str:
    """Normalize an author name to its leading surname for key comparison.

    Drops an ``et al.`` suffix and keeps only the first author (the part before
    ``&``, ``dan`` or a comma), then casefolds and trims. This mirrors APA
    in-text usage where the first surname identifies the reference.
    """
    cleaned = re.sub(r"\bet\s+al\.?", "", name, flags=re.IGNORECASE)
    first = re.split(r"\s*(?:&|,|\bdan\b)\s*", cleaned)[0]
    return first.strip().casefold()


def _citation_key(name: str, year: str) -> str:
    """Build the comparison key ``surname|year`` for a single source."""
    return f"{_normalize_name(name)}|{year.strip().lower()}"


@dataclass(frozen=True)
class Citation:
    """One parsed APA in-text citation group (``(...)``) within a paragraph.

    ``sources`` holds the ``(name, year)`` pairs contained in the group; a group
    may cite several sources separated by ``;``. ``start``/``end`` are the string
    offsets of the whole ``(...)`` span so markers can be inserted right after it.
    """

    raw: str
    start: int
    end: int
    sources: "tuple[tuple[str, str], ...]"

    @property
    def keys(self) -> "tuple[str, ...]":
        """Comparison keys for every source in this citation group."""
        return tuple(_citation_key(name, year) for name, year in self.sources)


def find_citations(text: str) -> "list[Citation]":
    """Return every APA in-text citation group found in ``text``.

    Only parenthetical groups that contain at least one ``Nama Tahun`` source
    are returned; parentheses used for other purposes are ignored.
    """
    citations: list[Citation] = []
    for match in _PAREN_RE.finditer(text):
        inner = match.group(1)
        sources: list[tuple[str, str]] = []
        for part in inner.split(";"):
            source_match = _SOURCE_RE.match(part)
            if source_match:
                sources.append(
                    (source_match.group("name"), source_match.group("year"))
                )
        if sources:
            citations.append(
                Citation(
                    raw=match.group(0),
                    start=match.start(),
                    end=match.end(),
                    sources=tuple(sources),
                )
            )
    return citations


def has_apa_citation(text: str) -> bool:
    """True when ``text`` contains at least one APA in-text citation."""
    return bool(find_citations(text))


# --------------------------------------------------------------------------- #
# BibliographyResult (Daftar Pustaka membership)
# --------------------------------------------------------------------------- #
def _normalize_bib_key(raw: str) -> str:
    """Normalize a raw Daftar Pustaka key to the ``surname|year`` form.

    Accepts flexible inputs — ``"Muharam et al., 2023"``, ``"Muharam, 2023"`` or a
    fuller reference string — by extracting the first surname (text before the
    year) and the first 4-digit year found. When no year is present, the raw text
    is casefolded so exact-string matching still works.
    """
    year_match = _YEAR_RE.search(raw)
    if not year_match:
        return raw.strip().casefold()
    year = year_match.group(1)
    name = raw[: year_match.start()].strip().rstrip(",;.").strip()
    return _citation_key(name, year)


@dataclass(frozen=True)
class BibliographyResult:
    """A collection of Daftar Pustaka keys with a citation membership check.

    Construct with :meth:`from_keys` (which normalizes arbitrary bibliography
    entry strings) or directly with an already-normalized key set. ``covers``
    reports whether every source of a citation has a matching entry — a citation
    is only treated as validated when all its sources are present (Requirement
    2.5).
    """

    keys: frozenset[str] = frozenset()

    @classmethod
    def from_keys(cls, keys: "list[str] | tuple[str, ...] | frozenset[str]") -> "BibliographyResult":
        """Build a bibliography by normalizing every raw entry key."""
        return cls(frozenset(_normalize_bib_key(k) for k in keys))

    def covers(self, citation: Citation) -> bool:
        """True when *every* source in ``citation`` has a matching entry."""
        return all(key in self.keys for key in citation.keys)

    def missing_sources(self, citation: Citation) -> "list[tuple[str, str]]":
        """Return the ``(name, year)`` sources of ``citation`` with no entry."""
        return [
            (name, year)
            for (name, year), key in zip(citation.sources, citation.keys)
            if key not in self.keys
        ]


#: An empty bibliography — every citation is treated as unvalidated.
EMPTY_BIBLIOGRAPHY = BibliographyResult()


# --------------------------------------------------------------------------- #
# has_cited_definition
# --------------------------------------------------------------------------- #
def has_cited_definition(paragraph: Paragraph) -> bool:
    """True when ``paragraph`` is a definition that carries an APA citation.

    Implements the check behind Requirement 2.2/2.4: a *cited definition* is a
    paragraph flagged as the definition (``is_definition``) whose text contains
    at least one attached APA in-text citation. Bibliography coverage is checked
    separately (Requirement 2.5); this predicate only reports citation presence.
    """
    return paragraph.is_definition and has_apa_citation(paragraph.text)


# --------------------------------------------------------------------------- #
# Marking helpers (idempotent)
# --------------------------------------------------------------------------- #
def _marker_follows(text: str, pos: int) -> bool:
    """True when the Penanda_Sitasi_Kurang already follows position ``pos``."""
    return text[pos:].lstrip().startswith(MISSING_CITATION_MARKER)


def _insert_marker_after(text: str, pos: int) -> str:
    """Insert the marker right after ``pos`` unless it is already there."""
    if _marker_follows(text, pos):
        return text
    return f"{text[:pos]} {MISSING_CITATION_MARKER}{text[pos:]}"


def _append_marker(text: str) -> str:
    """Append the marker at the end of ``text`` unless already present."""
    if MISSING_CITATION_MARKER in text:
        return text
    return f"{text.rstrip()} {MISSING_CITATION_MARKER}"


def _is_author_observation(text: str) -> bool:
    """True when the paragraph is the author's own observation/appendix data."""
    return bool(_OBSERVATION_RE.search(text))


def _is_blank(text: str) -> bool:
    """True when the paragraph has no meaningful text."""
    return text.strip() == ""


def _requires_citation(paragraph: Paragraph) -> bool:
    """True when ``paragraph`` makes a factual claim that needs a citation.

    Definitions always require a citation (Requirement 2.2). Otherwise a
    non-empty paragraph is treated as a factual claim requiring a source unless
    it is the author's own observation/appendix reference (Requirement 2.3
    exemption per ``aturan-sitasi.md``). This is deliberately conservative:
    flagging an uncited claim is safer than silently letting it pass.
    """
    if paragraph.is_definition:
        return True
    if _is_blank(paragraph.text):
        return False
    return not _is_author_observation(paragraph.text)


# --------------------------------------------------------------------------- #
# Per-paragraph citation processing
# --------------------------------------------------------------------------- #
def mark_paragraph_citations(
    paragraph: Paragraph,
    bib: BibliographyResult,
    location: str,
) -> "tuple[Paragraph, list[Finding]]":
    """Validate/mark the citations of a single paragraph without deleting text.

    * Every citation whose sources are not all present in ``bib`` is marked with
      ``[BUTUH SITASI]`` and reported; the citation is not treated as validated
      (Requirement 2.5).
    * A claim that requires a citation but has no *validated* citation is marked
      with ``[BUTUH SITASI]`` at the claim, preserving the text (Requirement 2.3;
      and Requirement 2.4 for the definition paragraph).

    Marking is idempotent, so re-processing already-marked text is a no-op.
    Returns the (possibly rewritten) paragraph and any findings raised.
    """
    text = paragraph.text
    findings: list[Finding] = []

    citations = find_citations(text)
    has_validated_citation = any(bib.covers(c) for c in citations)

    # Mark citations lacking a matching Daftar Pustaka entry (Requirement 2.5).
    # Process right-to-left so earlier offsets stay valid after insertion.
    for citation in sorted(citations, key=lambda c: c.start, reverse=True):
        missing = bib.missing_sources(citation)
        if missing:
            text = _insert_marker_after(text, citation.end)
            missing_desc = "; ".join(f"{name} {year}" for name, year in missing)
            findings.append(
                Finding(
                    kind=FindingKind.MISSING_CITATION,
                    location=location,
                    detail=(
                        f"Sitasi {citation.raw} tanpa entri padanan di Daftar "
                        f"Pustaka: {missing_desc}"
                    ),
                )
            )

    # Claim requires a source but has no validated citation (Requirements 2.3/2.4).
    if _requires_citation(paragraph) and not has_validated_citation:
        already_marked = MISSING_CITATION_MARKER in text
        text = _append_marker(text)
        if not already_marked:
            reason = (
                "Paragraf definisi tanpa Sitasi_APA tervalidasi"
                if paragraph.is_definition
                else "Klaim faktual tanpa Sitasi_APA"
            )
            findings.append(
                Finding(
                    kind=FindingKind.MISSING_CITATION,
                    location=location,
                    detail=reason,
                )
            )

    return Paragraph(text=text, is_definition=paragraph.is_definition), findings


# --------------------------------------------------------------------------- #
# Definition scaffolding
# --------------------------------------------------------------------------- #
def _definition_scaffold(title: str) -> str:
    """A neutral, non-fabricated definition placeholder for ``title``.

    The bracketed placeholder is intentionally distinct from ``[TBD: ...]`` (a
    fact/number placeholder) and from ``[BUTUH SITASI]`` so it is not counted by
    the ReportBuilder's TBD scan; it signals prose the writer must complete with
    a properly sourced definition.
    """
    return f"{title} adalah [definisi {title} yang perlu dilengkapi beserta sumber]."


# --------------------------------------------------------------------------- #
# write_theory_subchapter
# --------------------------------------------------------------------------- #
def write_theory_subchapter(
    entry: SkeletonEntry,
    facts: FactStore,
    bib: BibliographyResult,
    drafts: "list[Paragraph] | None" = None,
) -> "tuple[ContentBlock, list[Finding]]":
    """Compose (or normalize) the content of a Sub_Bab_Teori.

    Behaviour:

    * The first paragraph is guaranteed to be the sole definition paragraph of
      the main concept (Requirement 2.1): exactly one paragraph carries
      ``is_definition=True`` and it sits at index 0.
    * The definition paragraph must carry an attached, Daftar-Pustaka-backed APA
      citation (Requirement 2.2); when it does not, it is marked ``[BUTUH SITASI]``
      (Requirement 2.4). Generated scaffolds never fabricate a source, so they
      are always flagged.
    * Every other factual claim without a validated citation is marked
      ``[BUTUH SITASI]`` at the claim, without deleting text (Requirement 2.3),
      and citations without a matching Daftar Pustaka entry are flagged
      (Requirement 2.5).

    ``drafts`` is an optional list of already-written paragraphs to normalize; the
    first is treated as the definition. When omitted (or empty) a definition
    scaffold is generated for ``entry.title``. ``facts`` is accepted for interface
    compatibility with the design (a definition needs no project fact lookup).

    Returns the assembled :class:`ContentBlock` and the list of :class:`Finding`.
    """
    del facts  # No project fact/number is emitted while composing a definition.

    # Establish the working paragraph list with exactly one definition first.
    if drafts:
        paragraphs = [Paragraph(text=p.text, is_definition=False) for p in drafts]
    else:
        paragraphs = [Paragraph(text=_definition_scaffold(entry.title), is_definition=False)]

    # Requirement 2.1: exactly one definition paragraph, at paragraph 1.
    paragraphs[0] = Paragraph(text=paragraphs[0].text, is_definition=True)

    processed: list[Paragraph] = []
    findings: list[Finding] = []
    for index, paragraph in enumerate(paragraphs, start=1):
        location = f"{entry.entry_id} ¶{index}"
        new_paragraph, para_findings = mark_paragraph_citations(paragraph, bib, location)
        processed.append(new_paragraph)
        findings.extend(para_findings)

    block = ContentBlock(entry_id=entry.entry_id, paragraphs=processed)
    return block, findings
