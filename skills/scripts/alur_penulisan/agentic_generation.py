"""Guarded, provider-agnostic content generation for the TA Markdown draft.

The deterministic :func:`alur_penulisan.pipeline.run_alur` workflow remains the
quality/assembly pipeline.  This module adds an *optional* agentic stage in
front of it:

``provider -> structured candidate -> validation -> diff -> optional apply``

The default mode is suggestion-only.  The draft is written only when callers
pass ``apply=True``.  Even then, the candidate is appended only to the direct
body of one explicitly selected subchapter; existing lines are never removed or
replaced.  A second read immediately before the atomic write prevents a provider
call from overwriting edits made concurrently by a human.

The semantic boundary is intentionally explicit.  A provider must declare the
project facts, citations, and unresolved claims used by its prose.  The
validator can prove those declarations against ``project_facts.json`` and the
existing bibliography, while final semantic review remains a human decision in
suggestion mode.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence

from .branch_scope import active_role_indication, resolve_scope
from .content_writer import BibliographyResult, find_citations
from .draft_io import read_draft, write_draft
from .draft_model import DraftModel
from .exceptions import DraftInaccessibleError
from .fact_verifier import DEFAULT_FACTS_PATH, FactStore, emit_value
from .figure_table import is_valid_reference_position
from .models import ScopeState, TermRegistry
from .term_checker import scan_terms

__all__ = [
    "CandidateFactClaim",
    "ContentGenerationProvider",
    "GenerationCandidate",
    "GenerationIssue",
    "GenerationRequest",
    "GenerationResult",
    "GenerationSeverity",
    "GenerationStatus",
    "build_generation_request",
    "extract_bibliography_entries",
    "load_term_registry",
    "prepare_generation_request",
    "propose_section_append",
    "run_agentic_generation",
    "validate_candidate",
]


_SECTION_ID_RE = re.compile(r"^\d+(?:\.\d+)+$")
_HEADING_RE = re.compile(r"^\s{0,3}(?P<marks>#{1,6})\s+(?P<title>.+?)\s*$")
_NUMBERED_HEADING_RE = re.compile(r"^(?P<section>\d+(?:\.\d+)*)\b")
_BULLET_RE = re.compile(r"^(?P<indent>[ \t]*)[-*+]\s+")
_LIST_RE = re.compile(r"^(?P<indent>[ \t]*)(?P<marker>\d+[.)]|[A-Za-z][.)])\s+")
_OBJECT_RE = re.compile(r"\b(?P<kind>Gambar|Tabel)\s+(?P<number>\d+(?:\.\d+)*)\b", re.IGNORECASE)
_CAPTION_RE = re.compile(r"^\s*(?P<kind>Gambar|Tabel)\s+(?P<number>\d+(?:\.\d+)*)\b", re.IGNORECASE)
_SEMANTIC_OBJECT_RE = re.compile(
    r"\[(?P<kind>FIGREF|TABREF):(?P<id>[a-z0-9][a-z0-9_-]*)\]"
)
_SEMANTIC_SOURCE_LINE_RE = re.compile(
    r"^\s*\[(?:FIGURE|FIGCAPTION|TABLE-ID|TABLECAPTION):[^\]]+\]\s*$"
)
_FIGURE_MARKER_RE = re.compile(
    r"^\s*\[FIGURE:(?P<id>[a-z0-9][a-z0-9_-]*)\]\s*$"
)
_TABLE_MARKER_RE = re.compile(
    r"^\s*\[TABLE-ID:(?P<id>[a-z0-9][a-z0-9_-]*)\]\s*$"
)
_BAB_HEADING_RE = re.compile(
    r"^\s*#\s+BAB\s+(?P<number>[IVX]+|\d+)\b", re.IGNORECASE
)
_TBD_RE = re.compile(r"\[TBD:\s*[^\]]+\]", re.IGNORECASE)
_MISSING_CITATION_MARKER = "[BUTUH SITASI]"
_GENERATION_BRANCH_RE = re.compile(
    r"^(?:refs/heads/)?laporan/(?P<role>iman|dwikhi|faiz)$", re.IGNORECASE
)


class GenerationStatus(Enum):
    """Outcome of a guarded generation run."""

    PREPARED = "prepared"
    SUGGESTED = "suggested"
    APPLIED = "applied"
    UNCHANGED = "unchanged"
    HELD = "held"
    REJECTED = "rejected"
    FAILED = "failed"


class GenerationSeverity(Enum):
    """Whether an issue blocks ``--apply`` or only requires review."""

    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class CandidateFactClaim:
    """One project-fact value declared by a provider response."""

    key: str
    value: str


@dataclass(frozen=True)
class GenerationCandidate:
    """Structured provider response; prose alone is not accepted."""

    section_id: str
    markdown: str
    fact_claims: tuple[CandidateFactClaim, ...] = ()
    citations_used: tuple[str, ...] = ()
    unverified_claims: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "GenerationCandidate":
        """Parse and strictly type-check a provider response mapping."""

        section_id = raw.get("section_id")
        markdown = raw.get("markdown")
        if not isinstance(section_id, str) or not isinstance(markdown, str):
            raise ValueError("candidate requires string fields 'section_id' and 'markdown'")

        raw_facts = raw.get("fact_claims", [])
        if not isinstance(raw_facts, list):
            raise ValueError("candidate 'fact_claims' must be a list")
        facts: list[CandidateFactClaim] = []
        for index, item in enumerate(raw_facts):
            if not isinstance(item, Mapping):
                raise ValueError(f"fact_claims[{index}] must be an object")
            key = item.get("key")
            value = item.get("value")
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValueError(f"fact_claims[{index}] requires string key/value")
            facts.append(CandidateFactClaim(key=key, value=value))

        def _string_tuple(name: str) -> tuple[str, ...]:
            value = raw.get(name, [])
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                raise ValueError(f"candidate '{name}' must be a list of strings")
            return tuple(value)

        return cls(
            section_id=section_id.strip(),
            markdown=markdown.strip(),
            fact_claims=tuple(facts),
            citations_used=_string_tuple("citations_used"),
            unverified_claims=_string_tuple("unverified_claims"),
            notes=_string_tuple("notes"),
        )

    def to_mapping(self) -> dict[str, Any]:
        return {
            "section_id": self.section_id,
            "markdown": self.markdown,
            "fact_claims": [
                {"key": claim.key, "value": claim.value} for claim in self.fact_claims
            ],
            "citations_used": list(self.citations_used),
            "unverified_claims": list(self.unverified_claims),
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class GenerationIssue:
    """One validation or safety finding."""

    code: str
    severity: GenerationSeverity
    detail: str
    location: str = "candidate"

    def to_mapping(self) -> dict[str, str]:
        return {
            "code": self.code,
            "severity": self.severity.value,
            "location": self.location,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class GenerationRequest:
    """Minimal, auditable context sent to a generation provider."""

    version: int
    section_id: str
    section_heading: str
    existing_markdown: str
    instruction: str
    active_branch: str
    active_role: str
    role_context: str
    allowed_facts: Mapping[str, str]
    bibliography_entries: tuple[str, ...]
    canonical_terms: Mapping[str, str]
    constraints: tuple[str, ...]
    source_hash: str

    def to_mapping(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "task": "generate_ta_subchapter_content",
            "section": {
                "id": self.section_id,
                "heading": self.section_heading,
                "existing_markdown": self.existing_markdown,
            },
            "instruction": self.instruction,
            "branch_scope": {
                "branch": self.active_branch,
                "role": self.active_role,
                "role_context": self.role_context,
            },
            "allowed_facts": dict(self.allowed_facts),
            "bibliography_entries": list(self.bibliography_entries),
            "canonical_terms": dict(self.canonical_terms),
            "constraints": list(self.constraints),
            "source_hash": self.source_hash,
            "response_schema": {
                "section_id": self.section_id,
                "markdown": "body Markdown only; no heading",
                "fact_claims": [{"key": "dot.path", "value": "exact value used"}],
                "citations_used": ["(Nama Tahun) exactly as written"],
                "unverified_claims": ["claim marked [BUTUH SITASI] in markdown"],
                "notes": ["optional reviewer note"],
            },
        }


class ContentGenerationProvider(Protocol):
    """Provider boundary used by :func:`run_agentic_generation`."""

    def generate(self, request: GenerationRequest) -> GenerationCandidate:
        """Return one structured candidate for ``request``."""


@dataclass
class GenerationResult:
    """Result returned by prepare/suggest/apply workflows."""

    status: GenerationStatus
    section_id: str
    active_role: str | None
    message: str
    wrote_draft: bool = False
    diff: str = ""
    issues: list[GenerationIssue] = field(default_factory=list)
    request: GenerationRequest | None = None
    candidate: GenerationCandidate | None = None
    proposed_text: str | None = None

    def to_mapping(self, *, include_request: bool = False) -> dict[str, Any]:
        data: dict[str, Any] = {
            "status": self.status.value,
            "section_id": self.section_id,
            "active_role": self.active_role,
            "message": self.message,
            "wrote_draft": self.wrote_draft,
            "issues": [issue.to_mapping() for issue in self.issues],
        }
        if self.candidate is not None:
            data["candidate"] = self.candidate.to_mapping()
        if include_request and self.request is not None:
            data["request"] = self.request.to_mapping()
        return data


@dataclass(frozen=True)
class _SectionSpan:
    heading_index: int
    body_start: int
    body_end: int
    heading: str
    body: str


def _split_lines(text: str) -> tuple[list[str], bool]:
    trailing_newline = text.endswith("\n")
    lines = text.split("\n")
    if trailing_newline:
        lines = lines[:-1]
    return lines, trailing_newline


def _generation_scope(active_branch: str | None):
    """Resolve only real team report branches, never a matching last segment."""

    if active_branch is None:
        return resolve_scope(None)
    normalized = active_branch.strip().replace("\\", "/")
    if not _GENERATION_BRANCH_RE.fullmatch(normalized):
        return resolve_scope(None)
    return resolve_scope(normalized)


def _section_span(draft_text: str, section_id: str) -> _SectionSpan:
    """Locate the direct body of one numbered subchapter."""

    if not _SECTION_ID_RE.fullmatch(section_id.strip()):
        raise ValueError("section_id must be a numbered subchapter such as '2.3.4'")

    lines, _ = _split_lines(draft_text)
    target_index: int | None = None
    target_heading = ""
    for index, line in enumerate(lines):
        heading = _HEADING_RE.match(line)
        if not heading:
            continue
        numbered = _NUMBERED_HEADING_RE.match(heading.group("title"))
        if numbered and numbered.group("section") == section_id:
            if target_index is not None:
                raise ValueError(f"section '{section_id}' occurs more than once in the draft")
            target_index = index
            target_heading = heading.group("title")

    if target_index is None:
        raise ValueError(f"section '{section_id}' was not found in the draft")

    body_start = target_index + 1
    body_end = len(lines)
    for index in range(body_start, len(lines)):
        if _HEADING_RE.match(lines[index]):
            body_end = index
            break
    body = "\n".join(lines[body_start:body_end]).strip()
    return _SectionSpan(target_index, body_start, body_end, target_heading, body)


def extract_bibliography_entries(draft_text: str) -> tuple[str, ...]:
    """Return paragraph-like entries under ``# DAFTAR PUSTAKA``."""

    lines, _ = _split_lines(draft_text)
    start: int | None = None
    for index, line in enumerate(lines):
        heading = _HEADING_RE.match(line)
        if heading and heading.group("title").strip().casefold() == "daftar pustaka":
            start = index + 1
            break
    if start is None:
        return ()

    entries: list[str] = []
    paragraph: list[str] = []
    for line in lines[start:]:
        heading = _HEADING_RE.match(line)
        if heading and len(heading.group("marks")) == 1:
            break
        if line.strip() == "---":
            break
        if line.strip() == "":
            if paragraph:
                entries.append(" ".join(part.strip() for part in paragraph).lstrip("'\""))
                paragraph = []
            continue
        paragraph.append(line)
    if paragraph:
        entries.append(" ".join(part.strip() for part in paragraph).lstrip("'\""))
    return tuple(entries)


def load_term_registry(path: str = "term_registry.json") -> TermRegistry:
    """Load the repository's ``istilah_teknis`` registry."""

    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except (OSError, ValueError):
        return TermRegistry()
    mapping = raw.get("istilah_teknis", {}) if isinstance(raw, Mapping) else {}
    if not isinstance(mapping, Mapping):
        return TermRegistry()
    return TermRegistry(
        canonical={str(key): str(value) for key, value in mapping.items()}
    )


def build_generation_request(
    draft_text: str,
    *,
    section_id: str,
    instruction: str,
    active_branch: str,
    active_role: str,
    facts: FactStore,
    fact_keys: Sequence[str] = (),
    registry: TermRegistry | None = None,
    role_context: str = "",
) -> GenerationRequest:
    """Build the data-minimised request sent to an external provider.

    Only fact keys explicitly selected by the caller are included.  This avoids
    sending unrelated personal metadata from ``project_facts.json`` to a remote
    provider.
    """

    span = _section_span(draft_text, section_id)
    if registry is None:
        registry = TermRegistry()

    allowed_facts: dict[str, str] = {}
    for key in fact_keys:
        cleaned = key.strip()
        if cleaned and cleaned not in allowed_facts:
            allowed_facts[cleaned] = emit_value(cleaned, facts)

    semantic_objects = _existing_semantic_objects(draft_text)
    semantic_id_summary = ", ".join(
        f"{kind.upper()}:{object_id}"
        for kind, object_id in sorted(semantic_objects)
    ) or "(tidak ada)"
    constraints = (
        "Tulis hanya body subbab target; jangan keluarkan heading Markdown.",
        "Jangan menghapus, mengganti, atau mengulang isi manual yang sudah ada.",
        "Dilarang memakai bullet -, *, atau +; daftar harus 1. -> a. -> 1) -> a) dengan indentasi 3 spasi.",
        "Fakta/angka proyek hanya boleh berasal dari allowed_facts; jika tidak tersedia gunakan [TBD: ...].",
        "Deklarasikan setiap fakta proyek yang dipakai pada fact_claims dengan nilai persis yang tertulis.",
        "Jangan mengarang sitasi. Sitasi hanya boleh berasal dari bibliography_entries dan harus dideklarasikan pada citations_used.",
        "Klaim yang belum terverifikasi wajib diberi [BUTUH SITASI] dan dicatat pada unverified_claims.",
        "Rujukan objek wajib memakai [FIGREF:<id>] atau [TABREF:<id>] yang sudah ada pada draf, serta berada di tengah kalimat. Sintaks lama Gambar/Tabel X.Y hanya untuk draf legacy.",
        f"ID objek stabil yang tersedia pada draf: {semantic_id_summary}.",
        "Jangan membuat caption atau aset Gambar/Tabel baru melalui generator teks.",
        "Gunakan canonical_terms secara konsisten.",
        "Kembalikan satu objek JSON sesuai response_schema, tanpa code fence atau teks tambahan.",
    )
    return GenerationRequest(
        version=1,
        section_id=section_id,
        section_heading=span.heading,
        existing_markdown=span.body,
        instruction=instruction.strip(),
        active_branch=active_branch,
        active_role=active_role,
        role_context=role_context.strip(),
        allowed_facts=allowed_facts,
        bibliography_entries=extract_bibliography_entries(draft_text),
        canonical_terms=dict(registry.canonical),
        constraints=constraints,
        source_hash=hashlib.sha256(draft_text.encode("utf-8")).hexdigest(),
    )


def prepare_generation_request(
    *,
    draft_path: str = "Tugas_Akhir_Draft.md",
    section_id: str,
    instruction: str,
    active_branch: str | None,
    facts_path: str = DEFAULT_FACTS_PATH,
    fact_keys: Sequence[str] = (),
    term_registry_path: str = "term_registry.json",
    role_context: str = "",
    read: Callable[[str], str] = read_draft,
    load_facts: Callable[..., FactStore] = FactStore.load,
) -> GenerationRequest:
    """Read source files and prepare a request without invoking a provider."""

    scope = _generation_scope(active_branch)
    if scope.state is not ScopeState.RESOLVED or scope.role is None:
        raise ValueError(active_role_indication(scope))
    draft_text = read(draft_path)
    facts = load_facts(facts_path)
    registry = load_term_registry(term_registry_path)
    return build_generation_request(
        draft_text,
        section_id=section_id,
        instruction=instruction,
        active_branch=active_branch or "",
        active_role=scope.role,
        facts=facts,
        fact_keys=fact_keys,
        registry=registry,
        role_context=role_context,
    )


def propose_section_append(
    draft_text: str, section_id: str, candidate_markdown: str
) -> tuple[str, bool]:
    """Append body Markdown to one section without deleting existing content.

    Returns ``(proposed_text, already_present)``.  An exact candidate already in
    the direct section body is a no-op, making repeated apply calls idempotent.
    """

    span = _section_span(draft_text, section_id)
    candidate = candidate_markdown.strip()
    if not candidate:
        return draft_text, True
    if candidate in span.body:
        return draft_text, True

    lines, trailing_newline = _split_lines(draft_text)
    insert_at = span.body_end
    while insert_at > span.body_start and lines[insert_at - 1].strip() == "":
        insert_at -= 1

    inserted: list[str] = []
    if insert_at > span.body_start and lines[insert_at - 1].strip() != "":
        inserted.append("")
    inserted.extend(candidate.split("\n"))
    if insert_at == span.body_end or not lines[insert_at:span.body_end]:
        inserted.append("")

    new_lines = lines[:insert_at] + inserted + lines[insert_at:]
    proposed = "\n".join(new_lines)
    if trailing_newline:
        proposed += "\n"
    return proposed, False


def _bibliography(draft_text: str) -> BibliographyResult:
    return BibliographyResult.from_keys(extract_bibliography_entries(draft_text))


def _validate_lists(markdown: str) -> list[GenerationIssue]:
    issues: list[GenerationIssue] = []
    expected = {
        1: re.compile(r"^\d+\.$"),
        2: re.compile(r"^[A-Za-z]\.$"),
        3: re.compile(r"^\d+\)$"),
        4: re.compile(r"^[A-Za-z]\)$"),
    }
    for line_no, line in enumerate(markdown.splitlines(), start=1):
        if _BULLET_RE.match(line):
            issues.append(
                GenerationIssue(
                    "bullet_forbidden",
                    GenerationSeverity.ERROR,
                    "Bullet -, *, dan + dilarang; gunakan daftar bernomor berjenjang.",
                    f"candidate:{line_no}",
                )
            )
            continue
        match = _LIST_RE.match(line)
        if not match:
            continue
        indent = match.group("indent")
        if "\t" in indent or len(indent) % 3 != 0:
            issues.append(
                GenerationIssue(
                    "invalid_list_indent",
                    GenerationSeverity.ERROR,
                    "Indentasi daftar harus berupa kelipatan tepat 3 spasi tanpa tab.",
                    f"candidate:{line_no}",
                )
            )
            continue
        level = len(indent) // 3 + 1
        marker = match.group("marker")
        if level > 4 or not expected[level].fullmatch(marker):
            issues.append(
                GenerationIssue(
                    "invalid_list_marker",
                    GenerationSeverity.ERROR,
                    f"Marker '{marker}' tidak sesuai level {level}; gunakan 1. -> a. -> 1) -> a).",
                    f"candidate:{line_no}",
                )
            )
    return issues


def _existing_objects(draft_text: str) -> set[tuple[str, str]]:
    objects: set[tuple[str, str]] = set()
    for line in draft_text.splitlines():
        match = _CAPTION_RE.match(line)
        if match:
            objects.add((match.group("kind").casefold(), match.group("number")))
    return objects


def _roman_chapter(token: str) -> int | None:
    values = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5,
              "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10}
    return int(token) if token.isdigit() else values.get(token.upper())


def _existing_semantic_objects(draft_text: str) -> dict[tuple[str, str], int | None]:
    """Return stable object IDs and the BAB in which their marker appears."""
    objects: dict[tuple[str, str], int | None] = {}
    current_chapter = None
    for line in draft_text.splitlines():
        chapter_match = _BAB_HEADING_RE.match(line)
        if chapter_match:
            current_chapter = _roman_chapter(chapter_match.group("number"))
            continue
        figure_match = _FIGURE_MARKER_RE.match(line)
        if figure_match:
            objects[("figref", figure_match.group("id"))] = current_chapter
            continue
        table_match = _TABLE_MARKER_RE.match(line)
        if table_match:
            objects[("tabref", table_match.group("id"))] = current_chapter
    return objects


def _validate_object_references(
    markdown: str, draft_text: str, section_id: str
) -> list[GenerationIssue]:
    issues: list[GenerationIssue] = []
    objects = _existing_objects(draft_text)
    semantic_objects = _existing_semantic_objects(draft_text)
    chapter = section_id.split(".", 1)[0]
    for line_no, line in enumerate(markdown.splitlines(), start=1):
        for match in _OBJECT_RE.finditer(line):
            kind = match.group("kind")
            number = match.group("number")
            location = f"candidate:{line_no}"
            if not is_valid_reference_position(line, match.start()):
                issues.append(
                    GenerationIssue(
                        "invalid_object_reference_position",
                        GenerationSeverity.ERROR,
                        f"Rujukan {kind} {number} harus berada di tengah kalimat.",
                        location,
                    )
                )
            if number.split(".", 1)[0] != chapter:
                issues.append(
                    GenerationIssue(
                        "cross_chapter_object_reference",
                        GenerationSeverity.ERROR,
                        f"Rujukan {kind} {number} tidak berada pada BAB {chapter}.",
                        location,
                    )
                )
            if (kind.casefold(), number) not in objects:
                issues.append(
                    GenerationIssue(
                        "dangling_object_reference",
                        GenerationSeverity.ERROR,
                        f"Rujukan {kind} {number} tidak memiliki caption/objek pada draf saat ini.",
                        location,
                    )
                )
        for match in _SEMANTIC_OBJECT_RE.finditer(line):
            kind = match.group("kind")
            object_id = match.group("id")
            location = f"candidate:{line_no}"
            if not is_valid_reference_position(line, match.start()):
                issues.append(
                    GenerationIssue(
                        "invalid_object_reference_position",
                        GenerationSeverity.ERROR,
                        f"Rujukan [{kind}:{object_id}] harus berada di tengah kalimat.",
                        location,
                    )
                )
            key = (kind.casefold(), object_id)
            if key not in semantic_objects:
                issues.append(
                    GenerationIssue(
                        "dangling_object_reference",
                        GenerationSeverity.ERROR,
                        f"Rujukan [{kind}:{object_id}] tidak memiliki marker objek pada draf saat ini.",
                        location,
                    )
                )
    return issues


def _validate_terms(
    draft_text: str, proposed_text: str, registry: TermRegistry
) -> list[GenerationIssue]:
    existing = {
        report.concept_key: {occ.form for occ in report.forms}
        for report in scan_terms(DraftModel.from_markdown(draft_text), registry)
    }
    issues: list[GenerationIssue] = []
    for report in scan_terms(DraftModel.from_markdown(proposed_text), registry):
        forms = {occ.form for occ in report.forms}
        if forms.issubset(existing.get(report.concept_key, set())):
            continue
        issues.append(
            GenerationIssue(
                "new_term_inconsistency",
                GenerationSeverity.ERROR,
                f"Kandidat memperkenalkan bentuk istilah tidak konsisten untuk '{report.concept_key}': {', '.join(sorted(forms))}.",
                "candidate",
            )
        )
    return issues


def validate_candidate(
    candidate: GenerationCandidate,
    request: GenerationRequest,
    *,
    draft_text: str,
    facts: FactStore,
    registry: TermRegistry | None = None,
) -> list[GenerationIssue]:
    """Validate declared provenance and mechanical writing rules."""

    issues: list[GenerationIssue] = []
    markdown = candidate.markdown

    if candidate.section_id != request.section_id:
        issues.append(
            GenerationIssue(
                "section_mismatch",
                GenerationSeverity.ERROR,
                f"Kandidat menargetkan '{candidate.section_id}', bukan '{request.section_id}'.",
            )
        )
    if not markdown.strip():
        issues.append(
            GenerationIssue("empty_candidate", GenerationSeverity.ERROR, "Kandidat tidak berisi body Markdown.")
        )
    for line_no, line in enumerate(markdown.splitlines(), start=1):
        if _HEADING_RE.match(line):
            issues.append(
                GenerationIssue(
                    "heading_forbidden",
                    GenerationSeverity.ERROR,
                    "Kandidat tidak boleh membuat heading; section target dikendalikan pipeline.",
                    f"candidate:{line_no}",
                )
            )
        if line.strip() == "---":
            issues.append(
                GenerationIssue(
                    "page_break_forbidden",
                    GenerationSeverity.ERROR,
                    "Generator subbab tidak boleh membuat page break.",
                    f"candidate:{line_no}",
                )
            )
        if _CAPTION_RE.match(line) or _SEMANTIC_SOURCE_LINE_RE.match(line):
            issues.append(
                GenerationIssue(
                    "caption_insertion_forbidden",
                    GenerationSeverity.ERROR,
                    "Caption/aset Gambar atau Tabel baru harus ditambahkan melalui pipeline objek, bukan generator teks.",
                    f"candidate:{line_no}",
                )
            )
    issues.extend(_validate_lists(markdown))
    issues.extend(_validate_object_references(markdown, draft_text, request.section_id))

    seen_fact_keys: set[str] = set()
    for claim in candidate.fact_claims:
        if claim.key in seen_fact_keys:
            issues.append(
                GenerationIssue(
                    "duplicate_fact_claim",
                    GenerationSeverity.ERROR,
                    f"Fact claim '{claim.key}' dideklarasikan lebih dari sekali.",
                )
            )
            continue
        seen_fact_keys.add(claim.key)
        present, exact = facts.lookup(claim.key)
        if present:
            if claim.key not in request.allowed_facts:
                issues.append(
                    GenerationIssue(
                        "fact_not_authorized_for_request",
                        GenerationSeverity.ERROR,
                        f"Fakta '{claim.key}' tidak dipilih melalui --fact untuk request ini.",
                    )
                )
            if claim.value != exact:
                issues.append(
                    GenerationIssue(
                        "fact_value_mismatch",
                        GenerationSeverity.ERROR,
                        f"Nilai '{claim.key}' harus persis '{exact}', bukan '{claim.value}'.",
                    )
                )
        elif not _TBD_RE.fullmatch(claim.value.strip()):
            issues.append(
                GenerationIssue(
                    "unknown_fact_without_tbd",
                    GenerationSeverity.ERROR,
                    f"Fakta '{claim.key}' tidak tersedia; gunakan [TBD: ...].",
                )
            )
        if claim.value not in markdown:
            issues.append(
                GenerationIssue(
                    "declared_fact_not_in_markdown",
                    GenerationSeverity.ERROR,
                    f"Nilai fact claim '{claim.key}' tidak ditemukan pada body kandidat.",
                )
            )

    bibliography = _bibliography(draft_text)
    actual_citations = find_citations(markdown)
    actual_raw = {citation.raw.strip() for citation in actual_citations}
    declared_raw = {citation.strip() for citation in candidate.citations_used}
    for citation in actual_citations:
        if not bibliography.covers(citation):
            missing = "; ".join(
                f"{name} {year}" for name, year in bibliography.missing_sources(citation)
            )
            issues.append(
                GenerationIssue(
                    "citation_not_in_bibliography",
                    GenerationSeverity.ERROR,
                    f"Sitasi {citation.raw} tidak memiliki entri Daftar Pustaka: {missing}.",
                )
            )
    if actual_raw != declared_raw:
        issues.append(
            GenerationIssue(
                "citation_declaration_mismatch",
                GenerationSeverity.ERROR,
                "citations_used harus sama persis dengan sitasi APA yang tertulis pada body kandidat.",
            )
        )

    marker_count = markdown.count(_MISSING_CITATION_MARKER)
    if candidate.unverified_claims and marker_count < len(candidate.unverified_claims):
        issues.append(
            GenerationIssue(
                "unverified_claim_missing_marker",
                GenerationSeverity.ERROR,
                "Setiap unverified_claim harus memiliki penanda [BUTUH SITASI] pada body kandidat.",
            )
        )
    if marker_count and not candidate.unverified_claims:
        issues.append(
            GenerationIssue(
                "marker_without_declaration",
                GenerationSeverity.ERROR,
                "Body memuat [BUTUH SITASI], tetapi unverified_claims kosong.",
            )
        )
    for claim in candidate.unverified_claims:
        issues.append(
            GenerationIssue(
                "unverified_claim",
                GenerationSeverity.WARNING,
                claim,
            )
        )

    proposed_text, _ = propose_section_append(draft_text, request.section_id, markdown)
    if registry is not None:
        issues.extend(_validate_terms(draft_text, proposed_text, registry))
    return issues


def _make_diff(original: str, proposed: str, draft_path: str) -> str:
    return "".join(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            proposed.splitlines(keepends=True),
            fromfile=f"a/{Path(draft_path).name}",
            tofile=f"b/{Path(draft_path).name}",
        )
    )


def run_agentic_generation(
    provider: ContentGenerationProvider,
    *,
    draft_path: str = "Tugas_Akhir_Draft.md",
    section_id: str,
    instruction: str,
    active_branch: str | None,
    apply: bool = False,
    facts_path: str = DEFAULT_FACTS_PATH,
    fact_keys: Sequence[str] = (),
    term_registry_path: str = "term_registry.json",
    role_context: str = "",
    read: Callable[[str], str] = read_draft,
    write: Callable[[str, str], None] = write_draft,
    load_facts: Callable[..., FactStore] = FactStore.load,
) -> GenerationResult:
    """Generate, validate, diff, and optionally append one candidate.

    ``apply=False`` is the default and never calls ``write``.  ``apply=True``
    writes only after all error-severity findings are clear and after a
    concurrent-change check.
    """

    scope = _generation_scope(active_branch)
    indication = active_role_indication(scope)
    if scope.state is not ScopeState.RESOLVED or scope.role is None:
        return GenerationResult(
            status=GenerationStatus.HELD,
            section_id=section_id,
            active_role=None,
            message=indication,
        )

    try:
        original_text = read(draft_path)
    except (DraftInaccessibleError, OSError) as exc:
        return GenerationResult(
            status=GenerationStatus.FAILED,
            section_id=section_id,
            active_role=scope.role,
            message=str(exc),
        )

    facts = load_facts(facts_path)
    registry = load_term_registry(term_registry_path)
    try:
        request = build_generation_request(
            original_text,
            section_id=section_id,
            instruction=instruction,
            active_branch=active_branch or "",
            active_role=scope.role,
            facts=facts,
            fact_keys=fact_keys,
            registry=registry,
            role_context=role_context,
        )
    except ValueError as exc:
        return GenerationResult(
            status=GenerationStatus.REJECTED,
            section_id=section_id,
            active_role=scope.role,
            message=str(exc),
        )

    try:
        candidate = provider.generate(request)
    except Exception as exc:  # provider boundary: surface a stable FAILED result
        return GenerationResult(
            status=GenerationStatus.FAILED,
            section_id=section_id,
            active_role=scope.role,
            message=f"Provider generation failed: {exc}",
            request=request,
        )

    try:
        issues = validate_candidate(
            candidate,
            request,
            draft_text=original_text,
            facts=facts,
            registry=registry,
        )
        proposed_text, already_present = propose_section_append(
            original_text, section_id, candidate.markdown
        )
    except ValueError as exc:
        issues = [
            GenerationIssue("invalid_candidate", GenerationSeverity.ERROR, str(exc))
        ]
        proposed_text = original_text
        already_present = False

    diff = _make_diff(original_text, proposed_text, draft_path)
    if any(issue.severity is GenerationSeverity.ERROR for issue in issues):
        return GenerationResult(
            status=GenerationStatus.REJECTED,
            section_id=section_id,
            active_role=scope.role,
            message="Kandidat ditolak oleh guard; draf tidak diubah.",
            issues=issues,
            request=request,
            candidate=candidate,
            proposed_text=proposed_text,
            diff=diff,
        )

    if not apply:
        return GenerationResult(
            status=GenerationStatus.SUGGESTED,
            section_id=section_id,
            active_role=scope.role,
            message="Proposal valid. Mode suggest tidak menulis ke Markdown; gunakan --apply setelah meninjau diff.",
            issues=issues,
            request=request,
            candidate=candidate,
            proposed_text=proposed_text,
            diff=diff,
        )

    if already_present:
        return GenerationResult(
            status=GenerationStatus.UNCHANGED,
            section_id=section_id,
            active_role=scope.role,
            message="Kandidat yang sama sudah ada pada subbab; tidak ada penulisan ulang.",
            issues=issues,
            request=request,
            candidate=candidate,
            proposed_text=original_text,
            diff="",
        )

    try:
        current_text = read(draft_path)
    except (DraftInaccessibleError, OSError) as exc:
        return GenerationResult(
            status=GenerationStatus.FAILED,
            section_id=section_id,
            active_role=scope.role,
            message=f"Gagal memeriksa perubahan bersamaan: {exc}",
            issues=issues,
            request=request,
            candidate=candidate,
            diff=diff,
        )
    current_hash = hashlib.sha256(current_text.encode("utf-8")).hexdigest()
    if current_hash != request.source_hash:
        concurrent = GenerationIssue(
            "draft_changed_during_generation",
            GenerationSeverity.ERROR,
            "Draf berubah setelah request dibuat; jalankan ulang agar perubahan manual tidak tertimpa.",
            draft_path,
        )
        return GenerationResult(
            status=GenerationStatus.REJECTED,
            section_id=section_id,
            active_role=scope.role,
            message="Apply dibatalkan karena draf berubah secara bersamaan.",
            issues=issues + [concurrent],
            request=request,
            candidate=candidate,
            diff=diff,
        )

    try:
        write(draft_path, proposed_text)
    except (DraftInaccessibleError, OSError) as exc:
        return GenerationResult(
            status=GenerationStatus.FAILED,
            section_id=section_id,
            active_role=scope.role,
            message=f"Atomic write failed: {exc}",
            issues=issues,
            request=request,
            candidate=candidate,
            diff=diff,
        )
    return GenerationResult(
        status=GenerationStatus.APPLIED,
        section_id=section_id,
        active_role=scope.role,
        message="Kandidat valid ditambahkan ke subbab target; konten lama dipertahankan.",
        wrote_draft=True,
        issues=issues,
        request=request,
        candidate=candidate,
        proposed_text=proposed_text,
        diff=diff,
    )
