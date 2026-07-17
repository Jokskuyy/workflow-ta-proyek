"""BranchScopeResolver — role-aware scoping for the active Git branch.

This module implements section "10. BranchScopeResolver" of the design
document (``.kiro/specs/automated-writing-workflow/design.md``). It is a
**pure** component: it maps an already-known branch name to a
:class:`~alur_penulisan.models.BranchScope` and answers scope questions about
:class:`~alur_penulisan.models.SkeletonEntry` objects. Reading the active
branch from Git is an effectful edge handled elsewhere (the pipeline);
everything here is deterministic and side-effect free.

Responsibilities (Requirements 9.1–9.5):

* **Resolve scope** (``resolve_scope``) — map an active branch
  ``laporan/iman|dwikhi|faiz`` to a ``BranchScope`` with ``state RESOLVED``,
  the branch ``role`` and (optionally) the ``owned_entries`` derived from a
  Kerangka_Bab. An unknown branch or ``None`` yields ``state UNDETERMINED``
  (Requirements 9.1, 9.4).
* **Scope test** (``in_scope``) — decide whether a skeleton entry falls within
  the active role's scope so in-scope content can be written (Requirement 9.2)
  and out-of-scope content withheld (Requirement 9.3).
* **Out-of-scope indication** (``out_of_scope_finding``) — when a requested
  entry is outside the active scope, produce a ``Finding(OUT_OF_SCOPE)`` that
  names the Peran_Branch that *should* own the content (Requirement 9.3).
* **Active-role indication** (``active_role_indication``) — a human-readable
  banner shown when generation starts (Requirement 9.5), or a request to define
  the scope when the role is undetermined (Requirement 9.4).

Role definitions (source of truth: ``PANDUAN-TIM.md`` and
``.kiro/steering/konteks-proyek.md``):

* ``iman``   — Full Stack & System Integrator
* ``dwikhi`` — 3D Asset & Database Schema
* ``faiz``   — Simulator & Engine
"""

from __future__ import annotations

from .models import (
    BranchScope,
    Finding,
    FindingKind,
    ScopeState,
    Skeleton,
    SkeletonEntry,
)

# --------------------------------------------------------------------------- #
# Role catalogue
# --------------------------------------------------------------------------- #
#: Prefix of the team's role branches (see ``PANDUAN-TIM.md``).
BRANCH_PREFIX = "laporan/"

#: Known Peran_Branch roles mapped to their human-readable descriptions.
ROLE_DESCRIPTIONS: dict[str, str] = {
    "iman": "Full Stack & System Integrator",
    "dwikhi": "3D Asset & Database Schema",
    "faiz": "Simulator & Engine",
}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _normalize_role(value: "str | None") -> "str | None":
    """Extract a canonical role key from a branch name / owner-role string.

    Accepts full branch refs (``refs/heads/laporan/iman``), the conventional
    ``laporan/<role>`` form, or a bare role (``iman``). Matching is
    case-insensitive and tolerant of surrounding whitespace. Returns the
    lower-cased role key when it is one of the known roles, otherwise ``None``.

    Args:
        value: a branch name, branch ref, or owner-role string (may be ``None``).

    Returns:
        The canonical role key (``"iman" | "dwikhi" | "faiz"``) or ``None`` when
        it cannot be recognised.
    """
    if value is None:
        return None
    token = value.strip().lower()
    if token == "":
        return None
    # Reduce any path-like ref to its final segment: refs/heads/laporan/iman.
    token = token.replace("\\", "/")
    if "/" in token:
        token = token.rsplit("/", 1)[-1]
    return token if token in ROLE_DESCRIPTIONS else None


def role_description(role: "str | None") -> "str | None":
    """Return the human-readable description of a role, or ``None`` if unknown."""
    if role is None:
        return None
    return ROLE_DESCRIPTIONS.get(role)


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def resolve_scope(
    active_branch: "str | None",
    skeleton: "Skeleton | None" = None,
) -> BranchScope:
    """Map the active branch to a :class:`BranchScope`.

    A branch of ``laporan/iman``, ``laporan/dwikhi`` or ``laporan/faiz`` (in any
    ref form, case-insensitive) resolves to ``state RESOLVED`` with the matching
    ``role``. Any other branch — or ``None`` — resolves to ``state
    UNDETERMINED`` so the workflow can withhold generation and ask the writer to
    define the scope (Requirements 9.1, 9.4).

    When a ``skeleton`` is supplied, ``owned_entries`` is populated with the
    ``entry_id`` of every entry whose ``owner_role`` matches the resolved role,
    giving downstream stages a ready set of in-scope entries.

    Args:
        active_branch: the active Git branch name/ref, or ``None`` if unknown.
        skeleton: optional Kerangka_Bab used to derive ``owned_entries``.

    Returns:
        A resolved or undetermined :class:`BranchScope`.
    """
    role = _normalize_role(active_branch)
    if role is None:
        return BranchScope(state=ScopeState.UNDETERMINED, role=None)

    owned: frozenset[str] = frozenset()
    if skeleton is not None:
        owned = frozenset(
            entry.entry_id
            for entry in skeleton.entries
            if _normalize_role(entry.owner_role) == role
        )
    return BranchScope(state=ScopeState.RESOLVED, role=role, owned_entries=owned)


def in_scope(entry: SkeletonEntry, scope: BranchScope) -> bool:
    """Return whether ``entry`` falls within the active role's scope.

    An entry is in scope only when the scope is ``RESOLVED`` and either the
    entry's ``owner_role`` matches the active role, or the entry's ``entry_id``
    appears in the scope's ``owned_entries``. An ``UNDETERMINED`` scope has no
    in-scope entries, so generation is withheld until a role is chosen
    (Requirements 9.1, 9.2, 9.4).

    Args:
        entry: the skeleton entry being considered.
        scope: the resolved (or undetermined) branch scope.

    Returns:
        ``True`` if the entry is within scope, ``False`` otherwise.
    """
    if scope.state is not ScopeState.RESOLVED or scope.role is None:
        return False
    if entry.entry_id in scope.owned_entries:
        return True
    return _normalize_role(entry.owner_role) == scope.role


def out_of_scope_finding(
    entry: SkeletonEntry,
    scope: BranchScope,
) -> "Finding | None":
    """Produce an out-of-scope finding for ``entry`` if it is not in scope.

    When ``entry`` is outside the active scope, the returned
    ``Finding(OUT_OF_SCOPE)`` names the Peran_Branch that should own the content
    so the writer knows who is responsible (Requirement 9.3). If the entry is in
    scope, ``None`` is returned.

    Args:
        entry: the requested skeleton entry.
        scope: the active branch scope.

    Returns:
        A :class:`Finding` of kind ``OUT_OF_SCOPE`` or ``None`` when in scope.
    """
    if in_scope(entry, scope):
        return None

    owner_role = _normalize_role(entry.owner_role)
    owner_desc = role_description(owner_role)
    if owner_role is not None:
        owner_label = f"'{owner_role}'"
        if owner_desc is not None:
            owner_label += f" ({owner_desc})"
    else:
        owner_label = f"'{entry.owner_role}'"

    active_label = scope.role if scope.role is not None else "tidak tentu"
    detail = (
        f"Entri '{entry.numbering} {entry.title}' berada di luar lingkup peran "
        f"aktif ({active_label}); seharusnya ditangani oleh Peran_Branch "
        f"{owner_label}."
    )
    return Finding(
        kind=FindingKind.OUT_OF_SCOPE,
        location=entry.entry_id,
        detail=detail,
    )


def active_role_indication(scope: BranchScope) -> str:
    """Return a human-readable indication of the active Peran_Branch.

    Shown when generation starts (Requirement 9.5). If the scope is
    ``UNDETERMINED``, the message instead asks the writer to define the scope
    before any content is produced (Requirement 9.4).

    Args:
        scope: the active branch scope.

    Returns:
        A one-line status message describing the active role or requesting one.
    """
    if scope.state is ScopeState.RESOLVED and scope.role is not None:
        desc = role_description(scope.role)
        suffix = f" — {desc}" if desc is not None else ""
        return f"Peran_Branch aktif: {scope.role}{suffix}."
    return (
        "Peran_Branch tidak dapat ditentukan; tentukan lingkup peran "
        "(laporan/iman | laporan/dwikhi | laporan/faiz) sebelum menghasilkan konten."
    )
