"""FactVerifier & FactStore — anti-fabrication of project facts and numbers.

This module implements component 6 ("FactVerifier") of the design document
(``.kiro/specs/automated-writing-workflow/design.md``). Its single
responsibility is to guarantee that every project fact / number written into
Berkas_Draf comes from exactly one of two sources (Requirement 5.5):

1. **Basis_Fakta** (``project_facts.json``) — written *exactly* as recorded,
   with no rounding or additions (Requirement 5.2); or
2. A **Placeholder_TBD** of the form ``[TBD: ...]`` when the value is not
   available (Requirement 5.3) or when Basis_Fakta cannot be accessed at all
   (Requirement 10.3).

No code path here ever emits a numeric/factual value that originated from any
other source. When a *candidate* value is offered that differs from the value
recorded in Basis_Fakta, the Basis_Fakta value wins and the candidate is
rejected (Requirement 5.4).

Design split (inti murni, tepi bersisi-efek):

* :class:`FactStore` is the thin effectful edge. It loads ``project_facts.json``
  from disk with a bounded retry policy (3 attempts within a 30-second window)
  and, on persistent failure, becomes an *inaccessible* store rather than
  raising — so the workflow degrades every dependent value to a Placeholder_TBD
  instead of aborting (Requirement 10.3).
* :func:`resolve_fact` and :func:`emit_value` are pure with respect to a given
  :class:`FactStore`; they perform the "look up before writing" contract
  (Requirement 5.1) and can be exercised freely by property-based tests.

Nested facts are addressed with dot-separated key paths, e.g.
``"testing_status.lighthouse_testing.metrics.performance"``.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Callable, Mapping

from .models import FactValue, Finding, FindingKind

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
#: Default location of Basis_Fakta relative to the repository root.
DEFAULT_FACTS_PATH = "project_facts.json"

#: Retry budget for reading Basis_Fakta (Requirement 10.3 / 10.1 window).
DEFAULT_ATTEMPTS = 3
DEFAULT_WINDOW_SECONDS = 30

#: Sentinel string values inside Basis_Fakta that mean "not yet available".
#: A literal ``"TBD"`` recorded in the JSON is treated as an absent value so a
#: proper Placeholder_TBD is emitted rather than the bare sentinel text.
_TBD_SENTINELS = frozenset({"tbd"})

#: Reason text used when Basis_Fakta itself cannot be accessed (Requirement 10.3).
FACTS_INACCESSIBLE_REASON = "Basis_Fakta tidak dapat diakses"


# --------------------------------------------------------------------------- #
# FactStore (effectful edge)
# --------------------------------------------------------------------------- #
@dataclass
class FactStore:
    """In-memory view over Basis_Fakta (``project_facts.json``).

    Construct directly from a mapping (handy for tests) or via
    :meth:`load` to read from disk with the bounded retry policy. When the
    store is *inaccessible* (``accessible is False``) every lookup reports the
    fact as absent with a cause that names the access failure, so callers emit
    Placeholder_TBD for all fact-dependent values (Requirement 10.3).
    """

    data: Mapping[str, Any]
    accessible: bool = True
    error: "str | None" = None

    # ------------------------------------------------------------------ #
    # Construction
    # ------------------------------------------------------------------ #
    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "FactStore":
        """Build an accessible store from an already-parsed mapping."""
        return cls(data=dict(data), accessible=True, error=None)

    @classmethod
    def inaccessible(cls, cause: "str | None" = None) -> "FactStore":
        """Build a store that reports every fact as unavailable.

        ``cause`` describes why Basis_Fakta could not be accessed and is folded
        into the Placeholder_TBD reason for every dependent value.
        """
        reason = FACTS_INACCESSIBLE_REASON
        if cause:
            reason += f" ({cause})"
        return cls(data={}, accessible=False, error=reason)

    @classmethod
    def load(
        cls,
        path: str = DEFAULT_FACTS_PATH,
        attempts: int = DEFAULT_ATTEMPTS,
        window_seconds: int = DEFAULT_WINDOW_SECONDS,
        *,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> "FactStore":
        """Read and parse Basis_Fakta from ``path`` with bounded retries.

        Retries up to ``attempts`` times within a ``window_seconds`` window
        (Requirement 10.1/10.3). On persistent failure this does **not** raise;
        it returns an *inaccessible* store so the workflow can degrade every
        dependent value to a Placeholder_TBD rather than abort (Requirement
        10.3). ``sleep`` and ``clock`` are injectable for deterministic tests.
        """
        start = clock()
        last_cause: "str | None" = None

        for attempt in range(attempts):
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    parsed = json.load(handle)
            except (OSError, ValueError) as exc:  # missing/locked file or bad JSON
                last_cause = str(exc)
            else:
                if isinstance(parsed, Mapping):
                    return cls.from_mapping(parsed)
                last_cause = "isi Basis_Fakta bukan objek JSON"

            # Do not sleep after the final attempt, and never exceed the window.
            is_last = attempt == attempts - 1
            if not is_last and (clock() - start) < window_seconds:
                remaining = window_seconds - (clock() - start)
                if remaining > 0:
                    # Spread remaining attempts across the remaining window.
                    delay = remaining / max(1, attempts - attempt - 1)
                    sleep(min(delay, remaining))

        return cls.inaccessible(cause=last_cause)

    # ------------------------------------------------------------------ #
    # Lookup (pure)
    # ------------------------------------------------------------------ #
    def lookup(self, key: str) -> "tuple[bool, str | None]":
        """Resolve ``key`` to ``(present, exact_value_string)``.

        Supports dot-separated nested paths. A value is considered *present*
        only when it is a scalar (``str``/``int``/``float``/``bool``) that is
        neither ``None`` nor a TBD sentinel. Non-scalar containers (dict/list)
        and missing paths are reported as absent. When present, the returned
        string is the value rendered *exactly* (no rounding/formatting beyond a
        faithful string conversion) per Requirement 5.2.
        """
        if not self.accessible:
            return (False, None)

        node: Any = self.data
        for segment in key.split("."):
            if isinstance(node, Mapping) and segment in node:
                node = node[segment]
            else:
                return (False, None)

        return self._as_scalar(node)

    @staticmethod
    def _as_scalar(value: Any) -> "tuple[bool, str | None]":
        """Classify a resolved node as a present scalar or an absent value."""
        if value is None:
            return (False, None)
        if isinstance(value, bool):
            # Handle bool before int (bool is a subclass of int).
            return (True, "true" if value else "false")
        if isinstance(value, (int, float)):
            return (True, repr(value) if isinstance(value, float) else str(value))
        if isinstance(value, str):
            if value.strip().lower() in _TBD_SENTINELS:
                return (False, None)
            return (True, value)
        # Containers (dict/list) are not writable scalar facts.
        return (False, None)


# --------------------------------------------------------------------------- #
# resolve_fact / emit_value (pure w.r.t. a FactStore)
# --------------------------------------------------------------------------- #
def _placeholder(description: str) -> str:
    """Render a Placeholder_TBD (``[TBD: ...]``) for ``description``."""
    return f"[TBD: {description}]"


def resolve_fact(
    key: str,
    facts: FactStore,
    candidate: "str | None" = None,
    description: "str | None" = None,
) -> FactValue:
    """Resolve ``key`` against Basis_Fakta before any value is written.

    This is the "look up before writing" step (Requirement 5.1). The result is
    the single source of truth for what :func:`emit_value` will write:

    * Value present in Basis_Fakta → :class:`FactValue` with ``present=True`` and
      the exact recorded value (Requirement 5.2). Any differing ``candidate`` is
      ignored/rejected — the Basis_Fakta value always wins (Requirement 5.4).
    * Value absent → ``present=False`` with a ``tbd_reason`` describing the
      missing fact (Requirement 5.3).
    * Basis_Fakta inaccessible → ``present=False`` with a ``tbd_reason`` naming
      the access failure (Requirement 10.3).

    ``candidate`` is the value the caller *would* have written; it is accepted
    only to be explicitly rejected when it disagrees with Basis_Fakta, ensuring
    no value from another source is ever emitted (Requirement 5.5).
    ``description`` overrides the default human-readable fact description used in
    the Placeholder_TBD text.
    """
    present, value = facts.lookup(key)
    desc = description or key

    if present:
        return FactValue(key=key, present=True, value=value, tbd_reason=None)

    if not facts.accessible:
        reason = facts.error or FACTS_INACCESSIBLE_REASON
        tbd_reason = f"{desc} — {reason}"
    else:
        tbd_reason = f"{desc} tidak tersedia pada Basis_Fakta"

    return FactValue(key=key, present=False, value=None, tbd_reason=tbd_reason)


def emit_value(
    key: str,
    facts: FactStore,
    candidate: "str | None" = None,
    description: "str | None" = None,
) -> str:
    """Return the text to write for ``key`` — never a value from another source.

    Delegates to :func:`resolve_fact` and renders either the exact Basis_Fakta
    value (Requirement 5.2) or a Placeholder_TBD (Requirement 5.3/10.3). A
    ``candidate`` that differs from Basis_Fakta is never emitted; when the fact
    is absent, the candidate is *not* used either — a Placeholder_TBD is written
    instead (Requirement 5.5).
    """
    fact = resolve_fact(key, facts, candidate=candidate, description=description)
    if fact.present:
        # ``value`` is guaranteed non-None when present.
        return fact.value if fact.value is not None else _placeholder(description or key)
    return _placeholder(fact.tbd_reason or (description or key))


def fact_finding(fact: FactValue) -> "Finding | None":
    """Produce a ``Finding(TBD)`` for an unresolved fact, else ``None``.

    Supports later aggregation by the ReportBuilder so every Placeholder_TBD is
    reported with its cause (Requirement 10.5 / 5.3 / 10.3). Present facts yield
    no finding.
    """
    if fact.present:
        return None
    return Finding(
        kind=FindingKind.TBD,
        location=fact.key,
        detail=fact.tbd_reason or f"{fact.key} tidak tersedia pada Basis_Fakta",
    )
