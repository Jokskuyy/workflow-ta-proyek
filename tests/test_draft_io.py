"""Unit tests for DraftIO (skills/scripts/alur_penulisan/draft_io.py).

Covers Requirements 1.5, 8.5, 10.1, 10.2:

* A locked / unreadable Berkas_Draf raises ``DraftInaccessibleError`` that
  carries the file name and the underlying cause, and no write happens.
* ``write_draft`` never leaves a partial file behind when it fails.
* The bounded retry behaviour (up to 3 attempts within a 30 s window) is
  exercised deterministically with injected ``sleep`` / ``monotonic`` hooks.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# --------------------------------------------------------------------------- #
# Import the DraftIO module as part of the alur_penulisan package. The package
# uses relative imports, so skills/scripts must be on sys.path and the module
# imported via its package.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from alur_penulisan import draft_io  # noqa: E402
from alur_penulisan.exceptions import DraftInaccessibleError  # noqa: E402


# --------------------------------------------------------------------------- #
# Deterministic clock: sleep advances a virtual monotonic clock so retry timing
# can be asserted without any real waiting.
# --------------------------------------------------------------------------- #
class FakeClock:
    def __init__(self, jump: float | None = None):
        # `jump`, when set, is added to `now` on every sleep call in ADDITION to
        # the requested delay, letting a test force the retry window to elapse.
        self.now = 0.0
        self.jump = jump
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds
        if self.jump is not None:
            self.now += self.jump


# --------------------------------------------------------------------------- #
# read_draft — happy path
# --------------------------------------------------------------------------- #
def test_read_draft_returns_file_content(tmp_path: Path):
    draft = tmp_path / "Tugas_Akhir_Draft.md"
    draft.write_text("# BAB I\nisi draf", encoding="utf-8")

    clock = FakeClock()
    result = draft_io.read_draft(
        str(draft), sleep=clock.sleep, monotonic=clock.monotonic
    )

    assert result == "# BAB I\nisi draf"
    # A readable file must not trigger any retry delays.
    assert clock.sleeps == []


# --------------------------------------------------------------------------- #
# read_draft — unreadable file raises DraftInaccessibleError with name + cause
# --------------------------------------------------------------------------- #
def test_read_draft_missing_file_raises_with_filename_and_cause(tmp_path: Path):
    missing = tmp_path / "tidak_ada.md"
    clock = FakeClock()

    with pytest.raises(DraftInaccessibleError) as excinfo:
        draft_io.read_draft(
            str(missing), sleep=clock.sleep, monotonic=clock.monotonic
        )

    err = excinfo.value
    assert err.filename == str(missing)
    assert err.cause is not None
    assert isinstance(err.cause, OSError)
    # Filename must be surfaced in the message.
    assert str(missing) in str(err)
    # Reading never creates the file.
    assert not missing.exists()


def test_read_draft_retries_default_three_attempts(tmp_path: Path):
    """A persistently unreadable file is retried 3 times → 2 delays."""
    missing = tmp_path / "tidak_ada.md"
    clock = FakeClock()

    with pytest.raises(DraftInaccessibleError):
        draft_io.read_draft(
            str(missing),
            attempts=3,
            window_seconds=30.0,
            sleep=clock.sleep,
            monotonic=clock.monotonic,
        )

    # 3 attempts means 2 inter-attempt sleeps.
    assert len(clock.sleeps) == 2
    # Delays are spread as window / attempts = 10 s each.
    assert clock.sleeps == [pytest.approx(10.0), pytest.approx(10.0)]
    # Total simulated wait stays within the 30 s window.
    assert sum(clock.sleeps) <= 30.0


# --------------------------------------------------------------------------- #
# write_draft — happy path (atomic write)
# --------------------------------------------------------------------------- #
def test_write_draft_writes_content_atomically(tmp_path: Path):
    draft = tmp_path / "Tugas_Akhir_Draft.md"
    clock = FakeClock()

    draft_io.write_draft(
        str(draft),
        "# BAB I\nkonten baru",
        sleep=clock.sleep,
        monotonic=clock.monotonic,
    )

    assert draft.read_text(encoding="utf-8") == "# BAB I\nkonten baru"
    assert clock.sleeps == []
    # No stray temp files left behind.
    leftovers = [p.name for p in tmp_path.iterdir() if p.name.startswith(".draft-")]
    assert leftovers == []


# --------------------------------------------------------------------------- #
# write_draft — failure leaves no partial file and preserves the original
# --------------------------------------------------------------------------- #
def test_write_draft_failure_preserves_original_and_no_partial(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    draft = tmp_path / "Tugas_Akhir_Draft.md"
    draft.write_text("ISI LAMA", encoding="utf-8")

    # Simulate the destination being locked: the atomic move fails every time.
    def boom(src, dst):
        raise OSError("berkas terkunci")

    monkeypatch.setattr(draft_io.os, "replace", boom)

    clock = FakeClock()
    with pytest.raises(DraftInaccessibleError) as excinfo:
        draft_io.write_draft(
            str(draft),
            "ISI BARU",
            sleep=clock.sleep,
            monotonic=clock.monotonic,
        )

    err = excinfo.value
    assert err.filename == str(draft)
    assert isinstance(err.cause, OSError)
    # Original content is untouched — no partial write.
    assert draft.read_text(encoding="utf-8") == "ISI LAMA"
    # No temporary file is left behind.
    leftovers = [p.name for p in tmp_path.iterdir() if p.name.startswith(".draft-")]
    assert leftovers == []


def test_write_draft_retries_default_three_attempts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    draft = tmp_path / "Tugas_Akhir_Draft.md"

    def boom(src, dst):
        raise OSError("berkas terkunci")

    monkeypatch.setattr(draft_io.os, "replace", boom)

    clock = FakeClock()
    with pytest.raises(DraftInaccessibleError):
        draft_io.write_draft(
            str(draft),
            "ISI BARU",
            attempts=3,
            window_seconds=30.0,
            sleep=clock.sleep,
            monotonic=clock.monotonic,
        )

    assert len(clock.sleeps) == 2
    assert sum(clock.sleeps) <= 30.0


# --------------------------------------------------------------------------- #
# _retry_access — retry mechanics with mocked attempts / timing
# --------------------------------------------------------------------------- #
def test_retry_access_stops_after_all_attempts_fail():
    calls = {"n": 0}

    def failing():
        calls["n"] += 1
        raise OSError("gagal")

    clock = FakeClock()
    with pytest.raises(DraftInaccessibleError) as excinfo:
        draft_io._retry_access(
            failing,
            filename="berkas.md",
            attempts=3,
            window_seconds=30.0,
            sleep=clock.sleep,
            monotonic=clock.monotonic,
        )

    assert calls["n"] == 3  # exactly `attempts` tries
    assert len(clock.sleeps) == 2  # one sleep between each attempt
    assert excinfo.value.filename == "berkas.md"
    assert isinstance(excinfo.value.cause, OSError)


def test_retry_access_succeeds_on_second_attempt():
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 2:
            raise OSError("transient")
        return "ok"

    clock = FakeClock()
    result = draft_io._retry_access(
        flaky,
        filename="berkas.md",
        attempts=3,
        window_seconds=30.0,
        sleep=clock.sleep,
        monotonic=clock.monotonic,
    )

    assert result == "ok"
    assert calls["n"] == 2
    assert len(clock.sleeps) == 1  # only one retry delay was needed


def test_retry_access_stops_when_window_elapsed():
    """If the 30 s window is exhausted, retries stop before all attempts."""
    calls = {"n": 0}

    def failing():
        calls["n"] += 1
        raise OSError("gagal")

    # Each sleep jumps the clock far past the window, forcing an early stop.
    clock = FakeClock(jump=1000.0)
    with pytest.raises(DraftInaccessibleError):
        draft_io._retry_access(
            failing,
            filename="berkas.md",
            attempts=5,
            window_seconds=30.0,
            sleep=clock.sleep,
            monotonic=clock.monotonic,
        )

    # After the first sleep the window is already exceeded, so we stop early
    # instead of using all 5 attempts.
    assert calls["n"] < 5


def test_retry_access_returns_immediately_on_success():
    clock = FakeClock()
    result = draft_io._retry_access(
        lambda: 42,
        filename="berkas.md",
        attempts=3,
        window_seconds=30.0,
        sleep=clock.sleep,
        monotonic=clock.monotonic,
    )

    assert result == 42
    assert clock.sleeps == []


def test_retry_access_rejects_invalid_attempts():
    clock = FakeClock()
    with pytest.raises(ValueError):
        draft_io._retry_access(
            lambda: None,
            filename="berkas.md",
            attempts=0,
            window_seconds=30.0,
            sleep=clock.sleep,
            monotonic=clock.monotonic,
        )
