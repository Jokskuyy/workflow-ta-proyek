"""Exception types for the Alur_Penulisan (automated writing workflow).

These exceptions are raised at the effectful edges (DraftIO) and by the pure
assembly stage (Assembler). They are defined here so every module in the
package can import them without creating circular dependencies.
"""

from __future__ import annotations


class DraftInaccessibleError(Exception):
    """Raised when Berkas_Draf cannot be read or written.

    Carries the offending file name and the underlying cause so the workflow
    can surface an error message that names both (Requirements 1.5, 8.5, 10.1,
    10.2). It MUST be raised *before* any write occurs so no partial draft is
    produced.
    """

    def __init__(self, filename: str, cause: "str | BaseException | None" = None):
        self.filename = filename
        self.cause = cause
        detail = f"Berkas_Draf tidak dapat diakses: '{filename}'"
        if cause is not None:
            detail += f" (penyebab: {cause})"
        super().__init__(detail)


class AssemblyError(Exception):
    """Raised when the Assembler cannot produce a complete, valid draft.

    Two failure modes are represented (Requirements 7.3, 7.4):

    * ``missing_entries`` — Kerangka_Bab entries that have no associated content.
    * ``orphan_contents`` — content blocks that have no matching skeleton entry.

    In both cases assembly stops and NO partial Berkas_Draf is written; the old
    state is preserved.
    """

    def __init__(
        self,
        message: str,
        missing_entries: "tuple[str, ...]" = (),
        orphan_contents: "tuple[str, ...]" = (),
    ):
        self.missing_entries = tuple(missing_entries)
        self.orphan_contents = tuple(orphan_contents)
        super().__init__(message)
