"""Property test for the BranchScopeResolver's role-aware scoping (R9.1, R9.2) of
the automated-writing-workflow spec.

Spec: .kiro/specs/automated-writing-workflow

Covers design **Property 24: Cakupan penulisan sesuai Peran_Branch aktif** — for
each active team branch (``laporan/iman``, ``laporan/dwikhi``, ``laporan/faiz``),
after ``resolve_scope`` every skeleton entry that is *in scope* belongs to the
active role. In other words, ``in_scope`` returns ``True`` only for entries owned
by the active role, so all generated/written content stays within the active
Peran_Branch (Requirements 9.1, 9.2).

``resolve_scope`` / ``in_scope`` are pure transforms, so 100+ Hypothesis
iterations are cheap.
"""
import sys
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Import the alur_penulisan package (pure core under skills/scripts).
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from alur_penulisan.branch_scope import resolve_scope, in_scope  # noqa: E402
from alur_penulisan.models import (  # noqa: E402
    Level,
    ScopeState,
    Skeleton,
    SkeletonEntry,
)

# The three team branches and their canonical role keys.
_BRANCHES = {
    "laporan/iman": "iman",
    "laporan/dwikhi": "dwikhi",
    "laporan/faiz": "faiz",
}
_ROLES = tuple(_BRANCHES.values())
_LEVELS = tuple(Level)


@st.composite
def _skeleton_with_roles(draw):
    """Build a skeleton whose entries are owned by a random mix of the roles.

    Each entry gets a unique ``entry_id`` and an ``owner_role`` drawn from the
    three known team roles, so the property can check scope membership against
    the active role. Sometimes an owner is given in ``laporan/<role>`` or
    mixed-case form to exercise the resolver's normalization.
    """
    n = draw(st.integers(min_value=0, max_value=12))
    entries = []
    for i in range(n):
        role = draw(st.sampled_from(_ROLES))
        # Vary the surface form of the owner_role to exercise normalization.
        owner_form = draw(
            st.sampled_from(
                [role, role.upper(), f"laporan/{role}", f"refs/heads/laporan/{role}"]
            )
        )
        level = draw(st.sampled_from(_LEVELS))
        entries.append(
            SkeletonEntry(
                entry_id=f"{i}",
                numbering=f"{i}",
                title=f"Entri {i}",
                level=level,
                owner_role=owner_form,
            )
        )
    return Skeleton(entries=tuple(entries))


# =========================================================================== #
# Property 24: Cakupan penulisan sesuai Peran_Branch aktif
# =========================================================================== #
# Feature: automated-writing-workflow, Property 24: Cakupan penulisan sesuai Peran_Branch aktif
# Validates: Requirements 9.1, 9.2
@settings(max_examples=150, deadline=None)
@given(
    active_branch=st.sampled_from(sorted(_BRANCHES.keys())),
    skeleton=_skeleton_with_roles(),
    pass_skeleton=st.booleans(),
)
def test_in_scope_only_for_active_role(active_branch, skeleton, pass_skeleton):
    active_role = _BRANCHES[active_branch]

    # Resolve the scope for the active branch. Optionally pass the skeleton so
    # owned_entries is derived; either way the in_scope contract must hold.
    scope = resolve_scope(active_branch, skeleton if pass_skeleton else None)

    # A known team branch always resolves to its role.
    assert scope.state is ScopeState.RESOLVED
    assert scope.role == active_role

    # Core property: every in-scope entry belongs to the active role, and every
    # entry owned by the active role is in scope. Equivalently, in_scope is True
    # exactly for the active role's entries.
    for entry in skeleton.entries:
        owner_is_active = _BRANCHES.get(
            f"laporan/{entry.owner_role.strip().lower().rsplit('/', 1)[-1]}"
        ) == active_role
        expected = owner_is_active
        assert in_scope(entry, scope) is expected, (
            f"entry {entry.entry_id!r} owned by {entry.owner_role!r}: "
            f"in_scope={in_scope(entry, scope)} but expected {expected} "
            f"for active role {active_role!r}"
        )

    # Restated as the requirement guarantee: all in-scope content is within the
    # active Peran_Branch (no entry from another role is ever in scope).
    for entry in skeleton.entries:
        if in_scope(entry, scope):
            normalized = entry.owner_role.strip().lower().rsplit("/", 1)[-1]
            assert normalized == active_role, (
                f"in-scope entry {entry.entry_id!r} is owned by "
                f"{normalized!r}, outside active role {active_role!r}"
            )
