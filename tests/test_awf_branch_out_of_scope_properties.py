"""Property test for BranchScopeResolver out-of-scope rejection (R9.3) of the
automated-writing-workflow spec.

Spec: .kiro/specs/automated-writing-workflow

Covers design **Property 25: Permintaan di luar lingkup ditolak dengan indikasi
peran** — for any content request whose SkeletonEntry is owned by a role
*different* from the active Peran_Branch, the workflow refuses to generate the
content (``in_scope`` is ``False``) and produces a ``Finding(OUT_OF_SCOPE)``
whose detail names the Peran_Branch that should own the content.

``in_scope`` and ``out_of_scope_finding`` are pure transforms, so 100+
Hypothesis iterations are cheap.
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

from alur_penulisan.branch_scope import (  # noqa: E402
    ROLE_DESCRIPTIONS,
    in_scope,
    out_of_scope_finding,
    resolve_scope,
)
from alur_penulisan.models import (  # noqa: E402
    FindingKind,
    Level,
    SkeletonEntry,
)

_ROLES = sorted(ROLE_DESCRIPTIONS.keys())  # ["dwikhi", "faiz", "iman"]


@st.composite
def _active_and_foreign_entry(draw):
    """Pick an active role and build an entry owned by a *different* role.

    Returns a tuple ``(active_role, owner_role, entry)`` where
    ``owner_role != active_role`` so the entry is guaranteed out of scope.
    """
    active_role = draw(st.sampled_from(_ROLES))
    owner_role = draw(st.sampled_from([r for r in _ROLES if r != active_role]))

    bab = draw(st.integers(min_value=1, max_value=9))
    sub = draw(st.integers(min_value=1, max_value=9))
    numbering = f"{bab}.{sub}"
    title = draw(
        st.text(
            alphabet=st.characters(
                whitelist_categories=("Lu", "Ll", "Nd", "Zs"),
            ),
            min_size=1,
            max_size=30,
        ).map(lambda s: s.strip() or "Judul")
    )

    entry = SkeletonEntry(
        entry_id=numbering,
        numbering=numbering,
        title=title,
        level=Level.SUBBAB,
        owner_role=owner_role,
    )
    return active_role, owner_role, entry


# =========================================================================== #
# Property 25: Permintaan di luar lingkup ditolak dengan indikasi peran
# =========================================================================== #
# Feature: automated-writing-workflow, Property 25: Permintaan di luar lingkup ditolak dengan indikasi peran
# Validates: Requirements 9.3
@settings(max_examples=100, deadline=None)
@given(data=_active_and_foreign_entry())
def test_out_of_scope_rejected_with_role_indication(data):
    active_role, owner_role, entry = data

    scope = resolve_scope(f"laporan/{active_role}")

    # The workflow refuses to generate content outside the active scope.
    assert in_scope(entry, scope) is False, (
        f"entry owned by {owner_role!r} must be out of scope for active "
        f"role {active_role!r}"
    )

    finding = out_of_scope_finding(entry, scope)

    # An out-of-scope finding is produced ...
    assert finding is not None, (
        "out_of_scope_finding must return a Finding for an out-of-scope entry"
    )
    # ... of kind OUT_OF_SCOPE ...
    assert finding.kind is FindingKind.OUT_OF_SCOPE, (
        f"expected OUT_OF_SCOPE finding, got {finding.kind!r}"
    )
    # ... that names the Peran_Branch that should handle the content.
    assert owner_role in finding.detail, (
        f"finding detail must name the owner role {owner_role!r}; "
        f"detail={finding.detail!r}"
    )
