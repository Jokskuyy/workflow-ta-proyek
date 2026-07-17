"""Alur_Penulisan — automated writing workflow for the Tugas Akhir draft.

This package orchestrates the generation and assembly of Markdown content for
``Tugas_Akhir_Draft.md`` following the project's writing and citation rules. It
only produces/edits Markdown; it is NOT a replacement for the ``.docx`` format
pipeline (``skills/scripts/build_pipeline.py``). Its output stays compatible
with ``skills/scripts/merge_draft_to_docx.py``.

The public surface here is the core data model layer (task 1.1); subsequent
tasks add the I/O layer and the pure transformation components.
"""

from __future__ import annotations

from .exceptions import AssemblyError, DraftInaccessibleError
from .models import (
    BlockKind,
    BranchScope,
    ContentBlock,
    FactValue,
    Finding,
    FindingKind,
    InconsistencyReport,
    Level,
    ListNode,
    NumberedObject,
    ObjectKind,
    ObjectReference,
    Paragraph,
    ScopeState,
    Skeleton,
    SkeletonEntry,
    TermOccurrence,
    TermRegistry,
    WriterReport,
)
from .draft_model import (
    LIST_INDENT_UNIT,
    DraftBlock,
    DraftBlockType,
    DraftModel,
)
from .figure_table import (
    is_valid_reference_position,
    number_objects,
)
from .content_writer import (
    EMPTY_BIBLIOGRAPHY,
    MISSING_CITATION_MARKER,
    BibliographyResult,
    Citation,
    find_citations,
    has_apa_citation,
    has_cited_definition,
    mark_paragraph_citations,
    write_theory_subchapter,
)
from .fact_verifier import (
    DEFAULT_FACTS_PATH,
    FactStore,
    emit_value,
    fact_finding,
    resolve_fact,
)
from .list_formatter import (
    MAX_LIST_LEVEL,
    clamp_level,
    marker_for_level,
    render_list,
)
from .branch_scope import (
    BRANCH_PREFIX,
    ROLE_DESCRIPTIONS,
    active_role_indication,
    in_scope,
    out_of_scope_finding,
    resolve_scope,
    role_description,
)
from .skeleton import (
    canonical_skeleton,
    entry_heading_markdown,
    entry_heading_text,
    generate_skeleton,
    title_matches,
)
from .draft_io import read_draft, write_draft
from .merger import is_manual_content, merge
from .term_checker import (
    canonical_form,
    resolve_form,
    scan_terms,
)
from .assembler import assemble
from .pipeline import (
    DEFAULT_DRAFT_PATH,
    RunResult,
    RunStatus,
    run_alur,
)
from .report import (
    TBD_MARKER_RE,
    build_report,
    collect_tbd_findings,
    fill_empty_mandatory_sections,
    find_empty_mandatory_sections,
    make_tbd_marker,
    mandatory_sections,
)

__all__ = [
    # exceptions
    "AssemblyError",
    "DraftInaccessibleError",
    # enums
    "Level",
    "BlockKind",
    "ObjectKind",
    "ScopeState",
    "FindingKind",
    "DraftBlockType",
    # skeleton
    "SkeletonEntry",
    "Skeleton",
    # content
    "ContentBlock",
    "Paragraph",
    "ListNode",
    # objects
    "NumberedObject",
    "ObjectReference",
    # facts
    "FactValue",
    # terms
    "TermRegistry",
    "TermOccurrence",
    "InconsistencyReport",
    # scope
    "BranchScope",
    # findings / report
    "Finding",
    "WriterReport",
    # draft model
    "DraftModel",
    "DraftBlock",
    "LIST_INDENT_UNIT",
    # figure & table manager
    "number_objects",
    "is_valid_reference_position",
    # section content writer
    "write_theory_subchapter",
    "has_cited_definition",
    "mark_paragraph_citations",
    "find_citations",
    "has_apa_citation",
    "BibliographyResult",
    "Citation",
    "EMPTY_BIBLIOGRAPHY",
    "MISSING_CITATION_MARKER",
    # fact verifier
    "FactStore",
    "resolve_fact",
    "emit_value",
    "fact_finding",
    "DEFAULT_FACTS_PATH",
    # draft I/O
    "read_draft",
    "write_draft",
    # idempotent merger
    "merge",
    "is_manual_content",
    # assembler
    "assemble",
    # report builder
    "build_report",
    "collect_tbd_findings",
    "fill_empty_mandatory_sections",
    "find_empty_mandatory_sections",
    "mandatory_sections",
    "make_tbd_marker",
    "TBD_MARKER_RE",
    # list formatter
    "render_list",
    "marker_for_level",
    "clamp_level",
    "MAX_LIST_LEVEL",
    # branch scope resolver
    "resolve_scope",
    "in_scope",
    "out_of_scope_finding",
    "active_role_indication",
    "role_description",
    "BRANCH_PREFIX",
    "ROLE_DESCRIPTIONS",
    # term consistency checker
    "scan_terms",
    "canonical_form",
    "resolve_form",
    # skeleton generator
    "generate_skeleton",
    "title_matches",
    "canonical_skeleton",
    "entry_heading_text",
    "entry_heading_markdown",
    # pipeline orchestration
    "run_alur",
    "RunResult",
    "RunStatus",
    "DEFAULT_DRAFT_PATH",
]
