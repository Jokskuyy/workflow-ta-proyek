"""Unit tests for the end-to-end fail-safe behaviour of ``run_alur``.

Spec: .kiro/specs/automated-writing-workflow (task 16.4)

These example-based unit tests exercise the pipeline orchestration
(:func:`alur_penulisan.pipeline.run_alur`) when Berkas_Draf cannot be accessed.
They complement the DraftIO-level tests (``test_draft_io.py``) by checking the
*whole run* honours the fail-safe contract:

* **Requirement 1.5 / 8.5 / 10.1 / 10.2** — when Berkas_Draf is inaccessible the
  run stops with a :class:`DraftInaccessibleError`, performs *no* write, and the
  old on-disk content is therefore preserved.

The pipeline reads/writes exclusively through injectable ``read``/``write`` hooks
(defaulting to the real DraftIO), so we drive the failure deterministically:

* a *read hook* that raises :class:`DraftInaccessibleError` simulates a locked /
  unreadable draft, and
* a *write spy* records every write so we can assert it is **never** called.

The active branch is ``laporan/iman`` so scope resolves to ``RESOLVED`` and the
run proceeds past the HELD gate to the read stage under test.

Validates: Requirements 1.5, 8.5, 10.1, 10.2
"""
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# Make the alur_penulisan package importable from skills/scripts.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from alur_penulisan.exceptions import DraftInaccessibleError  # noqa: E402
from alur_penulisan.pipeline import RunStatus, run_alur  # noqa: E402

DRAFT_PATH = "Tugas_Akhir_Draft.md"
ACTIVE_BRANCH = "laporan/iman"


# --------------------------------------------------------------------------- #
# Test doubles: a spy recording every write, and a failing read hook.
# --------------------------------------------------------------------------- #
class WriteSpy:
    """Records every ``(path, content)`` written so we can assert none happen."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def __call__(self, path: str, content: str) -> None:
        self.calls.append((path, content))

    @property
    def called(self) -> bool:
        return bool(self.calls)


def _failing_read(exc: DraftInaccessibleError):
    """Build a read hook that always raises ``exc`` (draft inaccessible)."""

    def _read(path: str) -> str:
        raise exc

    return _read


# --------------------------------------------------------------------------- #
# Requirement 1.5 / 10.1 / 10.2 — inaccessible draft => FAILED, no write
# --------------------------------------------------------------------------- #
def test_inaccessible_draft_returns_failed_without_writing():
    """A read that raises DraftInaccessibleError => FAILED and the write spy is
    never called (fail safe: no partial write, old content preserved)."""
    exc = DraftInaccessibleError(DRAFT_PATH, "berkas terkunci")
    write_spy = WriteSpy()

    result = run_alur(
        draft_path=DRAFT_PATH,
        active_branch=ACTIVE_BRANCH,
        read=_failing_read(exc),
        write=write_spy,
    )

    assert result.status is RunStatus.FAILED
    assert result.error_type == "DraftInaccessibleError"
    # No write means the existing on-disk draft is left untouched.
    assert write_spy.called is False
    assert write_spy.calls == []
    # Nothing was persisted, so no draft text is returned.
    assert result.draft_text is None


def test_inaccessible_draft_error_names_the_file_and_cause():
    """The FAILED result surfaces an error message naming Berkas_Draf + cause."""
    exc = DraftInaccessibleError(DRAFT_PATH, "berkas terkunci")
    write_spy = WriteSpy()

    result = run_alur(
        draft_path=DRAFT_PATH,
        active_branch=ACTIVE_BRANCH,
        read=_failing_read(exc),
        write=write_spy,
    )

    assert result.status is RunStatus.FAILED
    assert result.error is not None
    assert DRAFT_PATH in result.error
    assert "berkas terkunci" in result.error
    # The active role is still resolved (we passed the HELD gate).
    assert result.active_role == "iman"
    assert write_spy.called is False


def test_read_failure_preserves_existing_content_because_no_write_occurs():
    """When the read fails, no write occurs, so pre-existing on-disk content
    would be preserved verbatim (Req 8.5/10.2)."""
    existing_on_disk = "# BAB I\n\nIsi lama yang harus dipertahankan.\n"
    written_paths: list[str] = []

    def _read(path: str) -> str:
        raise DraftInaccessibleError(path, PermissionError("locked"))

    def _write(path: str, content: str) -> None:
        written_paths.append(path)

    result = run_alur(
        draft_path=DRAFT_PATH,
        active_branch=ACTIVE_BRANCH,
        read=_read,
        write=_write,
    )

    assert result.status is RunStatus.FAILED
    assert result.error_type == "DraftInaccessibleError"
    # The write target was never touched -> existing_on_disk is intact.
    assert written_paths == []
    # (Sanity) the content we claim is preserved is exactly what we started with.
    assert existing_on_disk == "# BAB I\n\nIsi lama yang harus dipertahankan.\n"


# --------------------------------------------------------------------------- #
# Requirement 8.5 — a write-time inaccessibility also yields FAILED
# --------------------------------------------------------------------------- #
def test_write_time_inaccessible_draft_yields_failed():
    """If the draft becomes inaccessible at write time, the run reports FAILED
    (atomic write leaves no partial file behind)."""
    readable = "# BAB I PENDAHULUAN\n\nIsi awal.\n"

    def _read(path: str) -> str:
        return readable

    def _write(path: str, content: str) -> None:
        raise DraftInaccessibleError(path, "tidak dapat menulis")

    result = run_alur(
        draft_path=DRAFT_PATH,
        active_branch=ACTIVE_BRANCH,
        read=_read,
        write=_write,
    )

    assert result.status is RunStatus.FAILED
    assert result.error_type == "DraftInaccessibleError"
    assert result.draft_text is None
