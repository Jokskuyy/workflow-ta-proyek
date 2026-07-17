"""Unit test for the "look up before writing" behaviour of the FactVerifier.

Spec: .kiro/specs/automated-writing-workflow (task 7.4)

Requirement 5.1:

    WHEN Alur_Penulisan hendak menuliskan sebuah nilai fakta atau angka
    proyek, THE Alur_Penulisan SHALL mencari nilai tersebut pada Basis_Fakta
    SEBELUM menuliskan nilai apa pun pada posisi tersebut.

These tests verify — via a spy/wrapper around ``FactStore.lookup`` — that the
Basis_Fakta is *consulted* before ``emit_value`` (which produces the text that
would be written to the draft) yields any value. The emitted string is the
"write"; if ``lookup`` were not invoked before that string existed, the
requirement would be violated.

Validates: Requirements 5.1
"""
import sys
from pathlib import Path
from unittest import mock

# --------------------------------------------------------------------------- #
# Make the alur_penulisan package importable from skills/scripts.
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
# Helpers: a FactStore whose ``lookup`` records the order of operations.
# --------------------------------------------------------------------------- #
def _spy_store(store: FactStore, events: list):
    """Wrap ``store.lookup`` so every consultation is appended to ``events``.

    The real lookup is still executed (no mocking of behaviour), so the emitted
    value reflects genuine Basis_Fakta resolution. Returns the ``MagicMock``
    used as the spy so callers can make ``assert_called`` style assertions.
    """
    real_lookup = store.lookup

    def _recording_lookup(key):
        events.append(("lookup", key))
        return real_lookup(key)

    spy = mock.MagicMock(side_effect=_recording_lookup, wraps=None)
    # Bind the spy onto this instance only (dataclass instances allow this).
    object.__setattr__(store, "lookup", spy)
    return spy


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def test_emit_value_consults_factstore_before_writing_present_value():
    """A present fact: lookup must fire before emit_value returns the value."""
    store = FactStore.from_mapping({"responden": "42"})
    events: list = []
    spy = _spy_store(store, events)

    value = emit_value("responden", store)
    events.append(("write", value))

    # Basis_Fakta was consulted at all ...
    spy.assert_called_once_with("responden")
    # ... and the consultation happened strictly before the write.
    kinds = [kind for kind, _ in events]
    assert kinds.index("lookup") < kinds.index("write")
    # The written value came from Basis_Fakta (exact value), not fabricated.
    assert value == "42"


def test_emit_value_consults_factstore_before_writing_placeholder():
    """An absent fact: lookup must still precede the Placeholder_TBD write."""
    store = FactStore.from_mapping({"responden": "42"})
    events: list = []
    spy = _spy_store(store, events)

    value = emit_value("skor_lighthouse", store, description="skor Lighthouse")
    events.append(("write", value))

    spy.assert_called_once_with("skor_lighthouse")
    kinds = [kind for kind, _ in events]
    assert kinds.index("lookup") < kinds.index("write")
    # Missing fact => Placeholder_TBD, never a made-up value.
    assert value.startswith("[TBD:")


def test_emit_value_consults_factstore_before_rejecting_candidate():
    """A differing candidate is never emitted without consulting Basis_Fakta."""
    store = FactStore.from_mapping({"responden": "42"})
    events: list = []
    spy = _spy_store(store, events)

    # Caller "would have" written 99, but Basis_Fakta must be checked first.
    value = emit_value("responden", store, candidate="99")
    events.append(("write", value))

    spy.assert_called_once_with("responden")
    kinds = [kind for kind, _ in events]
    assert kinds.index("lookup") < kinds.index("write")
    # Basis_Fakta wins; the candidate is rejected.
    assert value == "42"
    assert value != "99"


def test_resolve_fact_consults_factstore_before_producing_factvalue():
    """resolve_fact (the look-up-before-write step) must invoke lookup."""
    store = FactStore.from_mapping({"responden": "42"})
    events: list = []
    spy = _spy_store(store, events)

    fact = resolve_fact("responden", store)
    events.append(("resolved", fact))

    spy.assert_called_once_with("responden")
    kinds = [kind for kind, _ in events]
    assert kinds.index("lookup") < kinds.index("resolved")
    assert fact.present is True
    assert fact.value == "42"


def test_no_value_is_produced_without_a_lookup():
    """If Basis_Fakta is never consulted, emit_value cannot yield a value.

    A store whose ``lookup`` raises simulates "writing without consulting":
    emit_value must propagate the failure rather than fabricate a value,
    proving the consultation is a prerequisite of producing any output.
    """
    store = FactStore.from_mapping({"responden": "42"})
    boom = mock.MagicMock(side_effect=AssertionError("lookup skipped"))
    object.__setattr__(store, "lookup", boom)

    try:
        emit_value("responden", store)
    except AssertionError as exc:
        assert "lookup skipped" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("emit_value produced a value without consulting FactStore")

    boom.assert_called_once_with("responden")
