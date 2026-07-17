"""Unit tests for undetermined branch scope and active-role indication.

Spec: .kiro/specs/automated-writing-workflow

Covers the BranchScopeResolver behaviours for:

* **Requirement 9.4** — when the active branch cannot be recognised (``None`` or
  an unknown branch), scope resolution yields ``ScopeState.UNDETERMINED`` with
  no role and no in-scope entries, so the workflow withholds content generation
  and asks the writer to define the scope.
* **Requirement 9.5** — an active-role indication is produced when generation
  starts: it names the resolved Peran_Branch, and for an undetermined scope it
  instead requests that the scope be defined.

These are plain pytest example-based unit tests complementing the property
tests for the same component.
"""
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# Import the alur_penulisan package (pure core under skills/scripts).
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from alur_penulisan.branch_scope import (  # noqa: E402
    ROLE_DESCRIPTIONS,
    active_role_indication,
    in_scope,
    resolve_scope,
)
from alur_penulisan.models import (  # noqa: E402
    BranchScope,
    Level,
    ScopeState,
    SkeletonEntry,
)


def _entry(entry_id: str = "2.1", owner_role: str = "iman") -> SkeletonEntry:
    """Build a simple skeleton entry for scope checks."""
    return SkeletonEntry(
        entry_id=entry_id,
        numbering=entry_id,
        title="Contoh Sub-bab",
        level=Level.SUBBAB,
        owner_role=owner_role,
    )


# --------------------------------------------------------------------------- #
# Requirement 9.4 — UNDETERMINED role withholds content and asks for scope
# --------------------------------------------------------------------------- #
def test_resolve_scope_none_is_undetermined():
    """``None`` active branch resolves to UNDETERMINED with no role/entries."""
    scope = resolve_scope(None)

    assert scope.state is ScopeState.UNDETERMINED
    assert scope.role is None
    assert scope.owned_entries == frozenset()


def test_resolve_scope_unknown_branch_is_undetermined():
    """An unrecognised branch resolves to UNDETERMINED with no role/entries."""
    scope = resolve_scope("laporan/orang-asing")

    assert scope.state is ScopeState.UNDETERMINED
    assert scope.role is None
    assert scope.owned_entries == frozenset()


def test_undetermined_scope_has_no_in_scope_entries():
    """No entry is in scope while the role is undetermined (content withheld)."""
    scope = resolve_scope(None)

    # Even an entry owned by a real role is not writable without a resolved role.
    for role in ROLE_DESCRIPTIONS:
        assert in_scope(_entry(owner_role=role), scope) is False


# --------------------------------------------------------------------------- #
# Requirement 9.5 — active-role indication at start of generation
# --------------------------------------------------------------------------- #
def test_active_role_indication_names_resolved_role():
    """A resolved scope produces a banner naming the active role + description."""
    scope = resolve_scope("laporan/iman")
    message = active_role_indication(scope)

    assert scope.state is ScopeState.RESOLVED
    assert scope.role == "iman"
    assert "iman" in message
    assert ROLE_DESCRIPTIONS["iman"] in message


def test_active_role_indication_names_each_known_role():
    """Every known Peran_Branch is named in its own active-role indication."""
    for role, desc in ROLE_DESCRIPTIONS.items():
        scope = resolve_scope(f"laporan/{role}")
        message = active_role_indication(scope)

        assert role in message
        assert desc in message


def test_active_role_indication_requests_scope_when_undetermined():
    """An undetermined scope yields a request to define the role scope."""
    message = active_role_indication(resolve_scope(None))

    lowered = message.lower()
    assert "tidak dapat ditentukan" in lowered
    # It points the writer at the concrete role branches to choose from.
    assert "laporan/iman" in lowered
    assert "laporan/dwikhi" in lowered
    assert "laporan/faiz" in lowered


def test_active_role_indication_undetermined_from_explicit_scope():
    """A directly-constructed UNDETERMINED scope also requests a scope."""
    message = active_role_indication(BranchScope(state=ScopeState.UNDETERMINED))

    assert "tidak dapat ditentukan" in message.lower()
