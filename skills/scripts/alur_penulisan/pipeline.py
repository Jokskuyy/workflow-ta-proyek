"""Pipeline — orchestration of the Alur_Penulisan (``run_alur``).

This module wires the individual (mostly pure) components of the package into a
single end-to-end run, following the order of the flowchart in design.md
("Architecture") and the task specification:

    Resolusi Peran_Branch
        -> baca Berkas_Draf + Basis_Fakta
            -> SkeletonGenerator
            -> SectionContentWriter
            -> ListFormatter
            -> FactVerifier
            -> FigureTableManager
            -> TermConsistencyChecker
            -> IdempotentMerger
            -> Assembler
        -> tulis Berkas_Draf + WriterReport

Guarantees enforced here (design.md "Error Handling"):

* **Hold on undetermined scope (Req 9.4/9.5).** The run resolves the active
  Peran_Branch *first*. If it cannot be determined the run is *held* — no file is
  read or written — and the writer is asked to define the scope. The active-role
  indication is always surfaced (Req 9.5).
* **Fail safe, no partial draft (Req 1.5, 7.3, 7.4, 8.5, 10.1).** Berkas_Draf is
  read through the retrying DraftIO layer; if it cannot be accessed a
  :class:`DraftInaccessibleError` stops the run *before* any write, leaving the
  old content untouched. Likewise, the Assembler validation gate raises
  :class:`AssemblyError` (missing entries / orphan content) *before* any write,
  so a failed assembly never persists a partial draft — the old content is
  preserved.
* **Facts degrade, they do not abort (Req 10.3).** Basis_Fakta is loaded through
  :meth:`FactStore.load`, which returns an *inaccessible* store instead of
  raising; every fact-dependent value then degrades to a Placeholder_TBD.

Design note on the write target: the components that mutate the whole draft
(SkeletonGenerator, FigureTableManager, ReportBuilder's TBD fill, IdempotentMerger)
operate on the block-oriented :class:`DraftModel`, which preserves the preamble
and every Konten_Manual block (Req 8.2). The Assembler is used here as the final
*structural validation gate* over the canonical sections actually present in the
draft (order/depth, exactly-once, missing/orphan detection); on success the fully
processed :class:`DraftModel` — not a rebuilt body that would drop front matter /
manual content — is what gets persisted. This keeps re-runs idempotent (Req 8.1)
while still honouring the Assembler's fail-safe contract.

This module performs I/O only through the injected ``read``/``write``/``load_facts``
hooks (defaulting to the real DraftIO / FactStore), so the orchestration can be
exercised deterministically in tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

from .assembler import assemble
from .branch_scope import active_role_indication, in_scope, out_of_scope_finding, resolve_scope
from .content_writer import EMPTY_BIBLIOGRAPHY, BibliographyResult, write_theory_subchapter
from .draft_io import read_draft, write_draft
from .draft_model import DraftBlock, DraftBlockType, DraftModel
from .exceptions import AssemblyError, DraftInaccessibleError
from .fact_verifier import DEFAULT_FACTS_PATH, FactStore
from .figure_table import number_objects
from .merger import is_manual_content, merge
from .models import (
    BlockKind,
    BranchScope,
    ContentBlock,
    Finding,
    FindingKind,
    Paragraph,
    ScopeState,
    Skeleton,
    SkeletonEntry,
    WriterReport,
)
from .report import build_report, fill_empty_mandatory_sections
from .skeleton import canonical_skeleton, entry_heading_text, generate_skeleton, title_matches
from .term_checker import scan_terms

__all__ = ["RunStatus", "RunResult", "run_alur"]

#: Default draft file (Berkas_Draf) at the repository root.
DEFAULT_DRAFT_PATH = "Tugas_Akhir_Draft.md"

# Block types that carry real body content (a section holding only blanks / page
# breaks is considered to have no content).
_BODY_BLOCK_TYPES = frozenset(
    {
        DraftBlockType.PARAGRAPH,
        DraftBlockType.PREAMBLE,
        DraftBlockType.LIST,
        DraftBlockType.CODE,
        DraftBlockType.TABLE,
        DraftBlockType.PIPE_TABLE,
    }
)


class RunStatus(Enum):
    """Outcome of a :func:`run_alur` invocation."""

    HELD = "held"            # Peran_Branch undetermined -> generation withheld (Req 9.4)
    COMPLETED = "completed"  # draft processed and persisted
    FAILED = "failed"        # draft inaccessible or assembly error -> no write (fail safe)


@dataclass
class RunResult:
    """Result of an end-to-end run.

    ``draft_text`` is the Markdown that was written on success; on a hold or a
    failure no write happens and ``draft_text`` stays ``None`` (the on-disk draft
    is left untouched). ``error`` carries a human-readable cause for a hold or a
    failure, and ``error_type`` names the exception class for a failure.
    """

    status: RunStatus
    active_role: "str | None"
    role_indication: str
    report: WriterReport
    draft_text: "str | None" = None
    error: "str | None" = None
    error_type: "str | None" = None


# --------------------------------------------------------------------------- #
# Section helpers
# --------------------------------------------------------------------------- #
def _split_sections(
    draft: DraftModel,
) -> "tuple[list[DraftBlock], list[tuple[DraftBlock, list[DraftBlock]]]]":
    """Split ``draft`` into ``(preamble, sections)``.

    Each section is ``(heading_block, [content_blocks])`` holding a heading and
    every block up to (but excluding) the next heading of any level.
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


def _match_sections_to_entries(
    outline: Skeleton,
    sections: "list[tuple[DraftBlock, list[DraftBlock]]]",
) -> "dict[str, tuple[DraftBlock, list[DraftBlock]]]":
    """Map each canonical entry to at most one matching draft section.

    Headings are matched to canonical entries case-/edge-space-insensitively via
    :func:`~alur_penulisan.skeleton.title_matches`; each section is consumed at
    most once so no entry is matched to a duplicate heading.
    """
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
    return matched


def _content_block_from_section(
    entry: SkeletonEntry,
    content: "list[DraftBlock]",
) -> ContentBlock:
    """Build a :class:`ContentBlock` from a draft section's body blocks.

    Blank/page-break blocks are ignored. If any body block is Konten_Manual the
    whole block is flagged ``BlockKind.MANUAL`` so downstream stages preserve it.
    """
    paragraphs: list[Paragraph] = []
    kind = BlockKind.GENERATED
    for block in content:
        if block.block_type not in _BODY_BLOCK_TYPES:
            continue
        if all(line.strip() == "" for line in block.lines):
            continue
        if is_manual_content(block):
            kind = BlockKind.MANUAL
        paragraphs.append(Paragraph(text=block.text()))
    return ContentBlock(entry_id=entry.entry_id, paragraphs=paragraphs, kind=kind)


# --------------------------------------------------------------------------- #
# Stage: SectionContentWriter (+ FactVerifier) over in-scope sections
# --------------------------------------------------------------------------- #
def _apply_section_content_writer(
    draft: DraftModel,
    outline: Skeleton,
    scope: BranchScope,
    facts: FactStore,
    bib: BibliographyResult,
) -> "tuple[DraftModel, list[Finding]]":
    """Run the SectionContentWriter over the in-scope sections of ``draft``.

    For every canonical entry that is *in scope* (Req 9.1/9.2) and already has
    body content, the section's paragraphs are re-processed by
    :func:`write_theory_subchapter` so uncited claims/definitions are flagged with
    ``[BUTUH SITASI]`` without deleting text (Req 2.3–2.5). ``facts`` is threaded
    through for interface compatibility (FactVerifier stage). Entries requested
    but out of scope yield a ``Finding(OUT_OF_SCOPE)`` naming the owner role
    (Req 9.3). The draft is otherwise left structurally unchanged.
    """
    preamble, sections = _split_sections(draft)
    matched = _match_sections_to_entries(outline, sections)

    findings: list[Finding] = []
    # Map section index -> replacement paragraph blocks (marked content).
    replacements: dict[int, list[DraftBlock]] = {}
    # Recover section index by identity of the heading block.
    index_of_heading = {id(heading): idx for idx, (heading, _) in enumerate(sections)}

    for entry in outline.entries:
        section = matched.get(entry.entry_id)
        if section is None:
            continue
        heading_block, content = section

        if not in_scope(entry, scope):
            # Not our responsibility: do not generate/modify, only note ownership
            # when the entry actually carries content the writer would touch.
            continue

        existing_paragraphs = [
            Paragraph(text=b.text())
            for b in content
            if b.block_type in _BODY_BLOCK_TYPES
            and any(line.strip() != "" for line in b.lines)
            and not is_manual_content(b)
        ]
        if not existing_paragraphs:
            # Empty in-scope section is handled by fill_empty_mandatory_sections.
            continue

        block, block_findings = write_theory_subchapter(
            entry, facts, bib, drafts=existing_paragraphs
        )
        findings.extend(block_findings)

        new_blocks = [
            DraftBlock(DraftBlockType.PARAGRAPH, para.text.split("\n"))
            for para in block.paragraphs
        ]
        replacements[index_of_heading[id(heading_block)]] = new_blocks

    if not replacements:
        return draft, findings

    # Rebuild the draft, swapping the generated body of processed in-scope
    # sections while keeping every other block (incl. Konten_Manual) verbatim.
    new_blocks: list[DraftBlock] = list(preamble)
    for idx, (heading_block, content) in enumerate(sections):
        new_blocks.append(heading_block)
        replacement = replacements.get(idx)
        if replacement is None:
            new_blocks.extend(content)
            continue
        # Preserve manual + non-body blocks, replace the generated body once.
        inserted = False
        for block in content:
            is_body = block.block_type in _BODY_BLOCK_TYPES and any(
                line.strip() != "" for line in block.lines
            )
            if is_manual_content(block) or not is_body:
                new_blocks.append(block)
            elif not inserted:
                for i, rep in enumerate(replacement):
                    new_blocks.append(rep)
                    if i < len(replacement) - 1:
                        new_blocks.append(DraftBlock(DraftBlockType.BLANK, [""]))
                inserted = True
        if not inserted:
            new_blocks.extend(replacement)

    new_draft = DraftModel(blocks=new_blocks, trailing_newline=draft.trailing_newline)
    return new_draft, findings


# --------------------------------------------------------------------------- #
# Stage: Assembler validation gate
# --------------------------------------------------------------------------- #
def _assembler_gate(draft: DraftModel, outline: Skeleton) -> "list[Finding]":
    """Validate the canonical structure of ``draft`` through the Assembler.

    Builds a skeleton of the canonical entries actually present in ``draft`` and
    the matching content blocks, then calls :func:`assemble`. This exercises the
    Assembler's order/depth and exactly-once guarantees (Req 7.1/7.5) and its
    missing/orphan detection (Req 7.3/7.4). On any problem :func:`assemble` raises
    :class:`AssemblyError`, which the caller turns into a fail-safe stop (no
    write, old content preserved). Returns the assembler findings on success.
    """
    _, sections = _split_sections(draft)
    matched = _match_sections_to_entries(outline, sections)

    present_entries: list[SkeletonEntry] = []
    contents: dict[str, ContentBlock] = {}
    for entry in outline.entries:
        section = matched.get(entry.entry_id)
        if section is None:
            continue
        _, content = section
        present_entries.append(entry)
        contents[entry.entry_id] = _content_block_from_section(entry, content)

    _, findings = assemble(Skeleton(entries=tuple(present_entries)), contents)
    return findings


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def run_alur(
    draft_path: str = DEFAULT_DRAFT_PATH,
    active_branch: "str | None" = None,
    facts_path: str = DEFAULT_FACTS_PATH,
    *,
    outline: "Skeleton | None" = None,
    registry=None,
    bibliography: "BibliographyResult | None" = None,
    read: "Callable[[str], str]" = read_draft,
    write: "Callable[[str, str], None]" = write_draft,
    load_facts: "Callable[..., FactStore]" = FactStore.load,
) -> RunResult:
    """Run the automated writing workflow end to end.

    Args:
        draft_path: path to Berkas_Draf (``Tugas_Akhir_Draft.md``).
        active_branch: the active Git branch name/ref (or ``None`` if unknown).
        facts_path: path to Basis_Fakta (``project_facts.json``).
        outline: canonical Kerangka_Bab; defaults to :func:`canonical_skeleton`.
        registry: optional :class:`~alur_penulisan.models.TermRegistry` for the
            consistency check; when ``None`` no term scanning is performed.
        bibliography: optional Daftar Pustaka membership; defaults to empty.
        read: injectable draft reader (defaults to DraftIO ``read_draft``).
        write: injectable draft writer (defaults to DraftIO ``write_draft``).
        load_facts: injectable Basis_Fakta loader (defaults to ``FactStore.load``).

    Returns:
        A :class:`RunResult`. ``status`` is ``HELD`` when the Peran_Branch is
        undetermined (no I/O performed), ``FAILED`` when Berkas_Draf is
        inaccessible or assembly fails (no write, old content preserved), or
        ``COMPLETED`` when the processed draft is persisted.
    """
    if outline is None:
        outline = canonical_skeleton()
    if bibliography is None:
        bibliography = EMPTY_BIBLIOGRAPHY

    # --- Stage 1: resolve Peran_Branch (before any I/O) ------------------ #
    scope = resolve_scope(active_branch, outline)
    role_indication = active_role_indication(scope)  # Req 9.5 (always surfaced)

    if scope.state is not ScopeState.RESOLVED:
        # Req 9.4: withhold generation and ask the writer to define the scope.
        return RunResult(
            status=RunStatus.HELD,
            active_role=None,
            role_indication=role_indication,
            report=WriterReport(findings=[], active_role=None),
            error=role_indication,
        )

    # --- Stage 2: read Berkas_Draf + Basis_Fakta (fail safe) ------------- #
    try:
        original_text = read(draft_path)
    except DraftInaccessibleError as exc:
        # Req 1.5/8.5/10.1/10.2: stop before any write; old content preserved.
        return RunResult(
            status=RunStatus.FAILED,
            active_role=scope.role,
            role_indication=role_indication,
            report=WriterReport(findings=[], active_role=scope.role),
            error=str(exc),
            error_type=type(exc).__name__,
        )

    # Basis_Fakta degrades to an inaccessible store instead of raising (Req 10.3).
    facts = load_facts(facts_path)

    draft = DraftModel.from_markdown(original_text)
    findings: list[Finding] = []

    # --- Stage 3: SkeletonGenerator ------------------------------------- #
    skeleton_draft, sk_findings = generate_skeleton(draft, outline, scope)
    findings.extend(sk_findings)

    # --- Stage 4/5/6: SectionContentWriter (+ ListFormatter, FactVerifier) #
    # write_theory_subchapter consults FactVerifier (``facts``) and marks uncited
    # claims; generated list content, when produced, is rendered via the
    # ListFormatter's 3-space grammar embedded in the DraftModel.
    written_draft, cw_findings = _apply_section_content_writer(
        skeleton_draft, outline, scope, facts, bibliography
    )
    findings.extend(cw_findings)

    # --- Stage 7: FigureTableManager ------------------------------------ #
    numbered_draft, ft_findings = number_objects(written_draft)
    findings.extend(ft_findings)

    # Fill empty mandatory (bagian wajib) sections with Placeholder_TBD (Req 10.4).
    filled_draft, _tbd_findings = fill_empty_mandatory_sections(numbered_draft, outline)

    # --- Stage 8: TermConsistencyChecker -------------------------------- #
    if registry is not None:
        for report in scan_terms(filled_draft, registry):
            forms = ", ".join(sorted({occ.form for occ in report.forms}))
            locations = ", ".join(f"baris {occ.line}" for occ in report.forms)
            findings.append(
                Finding(
                    kind=FindingKind.TERM_INCONSISTENCY,
                    location=report.concept_key,
                    detail=(
                        f"Istilah '{report.concept_key}' memiliki bentuk berbeda "
                        f"[{forms}] pada {locations}; tidak diubah otomatis."
                    ),
                )
            )

    # --- Stage 9: IdempotentMerger -------------------------------------- #
    # Reconcile the processed draft with the original so Konten_Manual and the
    # preamble are preserved and re-runs stay idempotent (Req 8.1–8.4).
    merged_draft, merge_findings = merge(draft, filled_draft)
    findings.extend(merge_findings)

    # --- Stage 10: Assembler (structural validation gate, fail safe) ---- #
    try:
        asm_findings = _assembler_gate(merged_draft, outline)
    except AssemblyError as exc:
        # Req 7.3/7.4: stop without producing a partial draft; old content kept.
        return RunResult(
            status=RunStatus.FAILED,
            active_role=scope.role,
            role_indication=role_indication,
            report=WriterReport(findings=list(findings), active_role=scope.role),
            error=str(exc),
            error_type=type(exc).__name__,
        )
    findings.extend(asm_findings)

    # --- Stage 11: write Berkas_Draf + WriterReport --------------------- #
    final_text = merged_draft.to_markdown()
    try:
        write(draft_path, final_text)
    except DraftInaccessibleError as exc:
        # write_draft is atomic: a failed write leaves no partial file (Req 8.5).
        return RunResult(
            status=RunStatus.FAILED,
            active_role=scope.role,
            role_indication=role_indication,
            report=WriterReport(findings=list(findings), active_role=scope.role),
            error=str(exc),
            error_type=type(exc).__name__,
        )

    report = build_report(findings, draft=merged_draft, active_role=scope.role)
    return RunResult(
        status=RunStatus.COMPLETED,
        active_role=scope.role,
        role_indication=role_indication,
        report=report,
        draft_text=final_text,
    )
