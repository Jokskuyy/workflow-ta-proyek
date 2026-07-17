"""Property-based test for FactVerifier degradation when Basis_Fakta is inaccessible.

Spec: .kiro/specs/automated-writing-workflow

Covers task 7.3 (Property 13) against the PURE fact-resolution helpers exposed by
``skills/scripts/alur_penulisan/fact_verifier.py``:

  FactStore.inaccessible, resolve_fact, emit_value.

When Basis_Fakta cannot be accessed (after 3 attempts within 30 seconds), the
FactStore becomes *inaccessible* rather than raising. Every fact-dependent value
must then degrade to a Placeholder_TBD (``[TBD: ...]``) so the workflow never
emits a value from any other source (Requirement 10.3). This is a brand-new
file; nothing here touches disk (the store is built via ``inaccessible``).
"""
import string
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Import the FactVerifier from the alur_penulisan package.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from alur_penulisan.fact_verifier import (  # noqa: E402
    FactStore,
    emit_value,
    resolve_fact,
)

# --------------------------------------------------------------------------- #
# Strategies: arbitrary lists of fact keys, plus an optional access-failure cause.
# --------------------------------------------------------------------------- #
# Keys mirror real fact addressing: flat identifiers and dot-separated nested
# paths are both exercised so no key shape escapes the degradation guarantee.
_SEGMENT = st.text(alphabet=string.ascii_letters + string.digits + "_", min_size=1, max_size=8)
_KEYS = st.one_of(
    _SEGMENT,
    st.lists(_SEGMENT, min_size=2, max_size=4).map(".".join),
)
_KEY_LISTS = st.lists(_KEYS, min_size=1, max_size=8)
_CAUSES = st.one_of(st.none(), st.text(max_size=30))


# --------------------------------------------------------------------------- #
# Property 13
# --------------------------------------------------------------------------- #
# Feature: automated-writing-workflow, Property 13: Basis_Fakta tak terakses memaksa Placeholder_TBD
@settings(max_examples=200)
@given(keys=_KEY_LISTS, cause=_CAUSES, candidate=st.one_of(st.none(), st.text(max_size=25)))
def test_property_13_inaccessible_facts_force_placeholder_tbd(keys, cause, candidate) -> None:
    """Property 13: Basis_Fakta tak terakses memaksa Placeholder_TBD.

    Untuk setiap barisan permintaan fakta ketika Basis_Fakta tidak dapat diakses
    (setelah 3 percobaan dalam 30 detik), setiap nilai yang bergantung pada
    Basis_Fakta ditulis sebagai Placeholder_TBD.

    Validates: Requirements 10.3
    """
    store = FactStore.inaccessible(cause=cause)

    # Precondition: the store models a persistent access failure.
    assert store.accessible is False

    for key in keys:
        # Look-up-before-writing never claims a fact is present on an
        # inaccessible store, regardless of any candidate value offered.
        fact = resolve_fact(key, store, candidate=candidate)
        assert fact.present is False
        assert fact.value is None
        assert fact.tbd_reason is not None

        # Every dependent value is emitted as a Placeholder_TBD (``[TBD: ...]``).
        emitted = emit_value(key, store, candidate=candidate)
        assert emitted.startswith("[TBD:")
        assert emitted.endswith("]")

        # The candidate from another source is never written verbatim.
        if candidate is not None:
            assert emitted != candidate


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
