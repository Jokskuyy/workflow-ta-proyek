"""DraftIO — thin, effectful file I/O layer for the Alur_Penulisan.

This module isolates all disk access for Berkas_Draf (``Tugas_Akhir_Draft.md``)
so that the pure transformation core stays testable without touching the
filesystem. Two operations are exposed:

* :func:`read_draft`  — read the draft content, retrying transient failures.
* :func:`write_draft` — write the draft content atomically.

Access behaviour (Requirements 1.5, 8.5, 10.1, 10.2):

* Each operation retries access up to ``attempts`` times (default 3) spread
  across a ``window_seconds`` window (default 30 s).
* If access keeps failing, a :class:`DraftInaccessibleError` is raised that
  carries both the file name and the underlying cause.
* :func:`write_draft` never leaves a partial file behind: content is written to
  a temporary file in the same directory and then atomically moved into place.
  If any step fails, the temporary file is removed and the original file (if
  any) is left untouched, and the error is raised *before* the destination is
  replaced.

The core logic is effectful, but the timing hooks (``sleep``/``monotonic``) are
injectable so the retry behaviour can be exercised deterministically in tests.
"""

from __future__ import annotations

import os
import tempfile
import time
from typing import Callable, TypeVar

from .exceptions import DraftInaccessibleError

__all__ = ["read_draft", "write_draft"]

# Default encoding used across the draft pipeline (matches merge_draft_to_docx).
_ENCODING = "utf-8"

_T = TypeVar("_T")

# Filesystem-level failures we treat as (potentially transient) access errors.
_ACCESS_ERRORS = (OSError,)


def _retry_access(
    operation: Callable[[], _T],
    *,
    filename: str,
    attempts: int,
    window_seconds: float,
    sleep: Callable[[float], None],
    monotonic: Callable[[], float],
) -> _T:
    """Run ``operation`` retrying access errors within a bounded time window.

    The operation is attempted up to ``attempts`` times. Retries are spread
    across ``window_seconds`` (default one delay slice per remaining attempt)
    and never extend past the window. If every attempt fails with an access
    error, a :class:`DraftInaccessibleError` naming ``filename`` and the last
    cause is raised.
    """
    if attempts < 1:
        raise ValueError("attempts must be at least 1")

    # Spread the retry delays evenly across the window between attempts.
    delay = window_seconds / attempts if attempts > 0 else 0.0
    start = monotonic()
    last_error: BaseException | None = None

    for attempt in range(1, attempts + 1):
        try:
            return operation()
        except _ACCESS_ERRORS as exc:  # transient / access failure
            last_error = exc
            if attempt >= attempts:
                break
            # Do not sleep past the retry window.
            elapsed = monotonic() - start
            remaining = window_seconds - elapsed
            if remaining <= 0:
                break
            sleep(min(delay, remaining))

    raise DraftInaccessibleError(filename, last_error)


def read_draft(
    path: str,
    attempts: int = 3,
    window_seconds: float = 30.0,
    *,
    sleep: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
) -> str:
    """Read Berkas_Draf, retrying transient access failures.

    Retries reading ``path`` up to ``attempts`` times within ``window_seconds``.
    Raises :class:`DraftInaccessibleError` (naming the file and cause) if the
    file cannot be read after all attempts.
    """

    def _do_read() -> str:
        with open(path, "r", encoding=_ENCODING) as handle:
            return handle.read()

    return _retry_access(
        _do_read,
        filename=path,
        attempts=attempts,
        window_seconds=window_seconds,
        sleep=sleep,
        monotonic=monotonic,
    )


def write_draft(
    path: str,
    content: str,
    attempts: int = 3,
    window_seconds: float = 30.0,
    *,
    sleep: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
) -> None:
    """Write ``content`` to Berkas_Draf atomically, retrying access failures.

    The content is first written to a temporary file in the same directory as
    ``path`` and flushed to disk, then atomically moved into place with
    :func:`os.replace`. This guarantees that a failure never leaves a partial
    draft: either the destination is fully replaced or it is left untouched.

    Retries the whole atomic write up to ``attempts`` times within
    ``window_seconds``. Raises :class:`DraftInaccessibleError` (naming the file
    and cause) if the write cannot complete after all attempts. The error is
    raised *before* the destination file is replaced.
    """

    directory = os.path.dirname(os.path.abspath(path))

    def _do_write() -> None:
        # Create the temp file in the same directory so os.replace is atomic
        # (a cross-device rename would not be).
        fd, tmp_path = tempfile.mkstemp(
            prefix=".draft-", suffix=".tmp", dir=directory
        )
        try:
            with os.fdopen(fd, "w", encoding=_ENCODING) as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            # Atomic move into place — either fully succeeds or leaves original.
            os.replace(tmp_path, path)
        except BaseException:
            # Never leave a partial file behind on failure.
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except OSError:
                pass
            raise

    _retry_access(
        _do_write,
        filename=path,
        attempts=attempts,
        window_seconds=window_seconds,
        sleep=sleep,
        monotonic=monotonic,
    )
