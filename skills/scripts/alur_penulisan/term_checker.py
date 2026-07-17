"""TermConsistencyChecker — enforce and report term consistency (Istilah).

This module implements section "7. TermConsistencyChecker" of the design
document (``.kiro/specs/automated-writing-workflow/design.md``). It is a
**pure** component: it reads a :class:`~alur_penulisan.draft_model.DraftModel`
and a :class:`~alur_penulisan.models.TermRegistry` and returns findings /
resolved forms, without touching disk and **without mutating the draft**.

Responsibilities (Requirements 6.1–6.4):

* **canonical_form** — for a term that has a registered canonical form, return
  that single canonical form; the lookup ignores letter case and surrounding /
  collapsing whitespace (Requirements 6.1, 6.2). Returns ``None`` for a term
  without a registered canonical form.
* **scan_terms** — scan the *entire* draft (case-insensitively, Requirement 6.2)
  for every registered concept. When two or more differing surface forms of the
  **same** concept (same registered canonical form) appear, produce an
  :class:`~alur_penulisan.models.InconsistencyReport` listing every form found
  together with its occurrence location, **without changing the draft
  automatically** (Requirement 6.3). Concepts that appear in a single consistent
  form produce no report.
* **resolve_form** — the writer-side normalization rule. A registered term is
  normalized to its single canonical form (Requirement 6.1); a term *without* a
  registered canonical form keeps the surface form of its first occurrence, and
  that same form is reused for every later occurrence (Requirement 6.4).

Modeling conventions:

* The registry maps a *normalized* variant key (lower-cased, whitespace
  collapsed) to the canonical surface form, e.g.
  ``{"navmesh": "NavMesh", "nav mesh": "NavMesh"}``. Every variant key that maps
  to the same canonical form belongs to the same *concept*; the concept is keyed
  by that canonical form.
* A "different form" is a distinct exact surface string. Because Requirement 6.1
  demands one *identical* canonical form throughout the draft, forms that differ
  only in letter case (e.g. ``NavMesh`` vs ``navmesh``) count as different forms
  and, when two or more co-occur, are reported.
"""

from __future__ import annotations

import re

from .draft_model import DraftModel
from .models import InconsistencyReport, TermOccurrence, TermRegistry


# --------------------------------------------------------------------------- #
# Normalization helpers
# --------------------------------------------------------------------------- #
def _normalize_key(term: str) -> str:
    """Return the case-insensitive, whitespace-collapsed lookup key for a term.

    Collapsing internal runs of whitespace and lower-casing makes the lookup
    ignore letter case and incidental spacing (Requirement 6.2).
    """
    return " ".join(term.lower().split())


def _build_lookup(registry: TermRegistry) -> "dict[str, str]":
    """Build a normalized ``{variant_key: canonical_form}`` lookup.

    Registry keys are normalized defensively so callers may register variants
    using any case / spacing. When two raw keys normalize to the same value the
    later one wins, mirroring plain ``dict`` construction semantics.
    """
    lookup: dict[str, str] = {}
    for raw_key, canonical in registry.canonical.items():
        lookup[_normalize_key(raw_key)] = canonical
    return lookup


def _variant_pattern(norm_key: str) -> "re.Pattern[str]":
    """Compile a case-insensitive, whitespace-flexible matcher for a variant.

    Word tokens of the normalized key are joined by ``\\s+`` so a registered
    ``"nav mesh"`` also matches ``"Nav   Mesh"``. Non-word boundaries guard both
    ends so ``"mesh"`` does not match inside ``"meshing"``.
    """
    tokens = norm_key.split(" ")
    escaped = r"\s+".join(re.escape(token) for token in tokens if token)
    return re.compile(rf"(?<!\w){escaped}(?!\w)", re.IGNORECASE)


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def canonical_form(term: str, registry: TermRegistry) -> "str | None":
    """Return the registered canonical form of ``term`` or ``None``.

    The lookup ignores letter case and collapses whitespace (Requirements 6.1,
    6.2). A term with no registered canonical form yields ``None`` so callers can
    fall back to the first-occurrence rule (Requirement 6.4, see
    :func:`resolve_form`).

    Args:
        term: the term whose canonical form is requested.
        registry: the project term registry.

    Returns:
        The canonical surface form, or ``None`` when the term is unregistered.
    """
    return _build_lookup(registry).get(_normalize_key(term))


def scan_terms(
    draft: DraftModel, registry: TermRegistry
) -> "list[InconsistencyReport]":
    """Scan the whole draft for inconsistent use of registered terms.

    For every registered concept the entire draft is scanned case-insensitively
    (Requirement 6.2). When two or more distinct surface forms of the same
    concept appear, an :class:`InconsistencyReport` is produced listing each form
    with its 1-based line location (Requirement 6.3). The draft is **never**
    modified — this function only reports (Requirements 6.3).

    Args:
        draft: the source draft model (read only, not mutated).
        registry: the project term registry.

    Returns:
        A list of :class:`InconsistencyReport`, one per concept that appears in
        two or more differing forms. Concepts used consistently (or absent) yield
        no report; the list is empty when the draft is fully consistent.
    """
    lookup = _build_lookup(registry)

    # Group registered variant keys by the concept (canonical form) they map to,
    # preserving discovery order for stable, deterministic output.
    concept_variants: dict[str, list[str]] = {}
    for variant_key, canonical in lookup.items():
        concept_variants.setdefault(canonical, []).append(variant_key)

    # Pre-compile one matcher per variant key.
    patterns = {key: _variant_pattern(key) for key in lookup}

    lines = draft.to_markdown().split("\n")

    reports: list[InconsistencyReport] = []
    for canonical, variant_keys in concept_variants.items():
        occurrences: list[TermOccurrence] = []
        distinct_forms: set[str] = set()

        for line_no, line in enumerate(lines, start=1):
            # Collect matches keyed by start offset so overlapping variant keys
            # (e.g. "mesh" inside "nav mesh") do not double-count one position.
            matches: dict[int, str] = {}
            for variant_key in variant_keys:
                for match in patterns[variant_key].finditer(line):
                    matches.setdefault(match.start(), match.group(0))
            for _start in sorted(matches):
                surface = matches[_start]
                occurrences.append(TermOccurrence(form=surface, line=line_no))
                distinct_forms.add(surface)

        # Requirement 6.3: only two-or-more differing forms are an inconsistency.
        if len(distinct_forms) >= 2:
            reports.append(
                InconsistencyReport(concept_key=canonical, forms=occurrences)
            )

    return reports


def resolve_form(
    term: str, registry: TermRegistry, first_seen: "dict[str, str]"
) -> str:
    """Return the form to use for ``term`` under the consistency rules.

    This is the writer-side normalization used while emitting content:

    * A registered term is normalized to its single canonical form so every
      occurrence is identical throughout the draft (Requirement 6.1).
    * A term **without** a registered canonical form keeps the surface form of
      its first occurrence; that same form is returned for every subsequent
      occurrence (Requirement 6.4).

    Args:
        term: the term being written.
        registry: the project term registry.
        first_seen: a mutable ``{normalized_key: first_surface_form}`` map that
            accumulates first-occurrence forms of unregistered terms across
            calls. Callers create it once (empty) per draft run.

    Returns:
        The canonical form (registered) or the first-occurrence form
        (unregistered).
    """
    canonical = canonical_form(term, registry)
    if canonical is not None:
        return canonical

    key = _normalize_key(term)
    if key in first_seen:
        return first_seen[key]
    first_seen[key] = term
    return term
