"""Unit tests for the validator-side wiring of the writing guards
(writing-pipeline-improvements, Task 8.8/8.9).

Spec: .kiro/specs/writing-pipeline-improvements

Focus (R1.7): the citation cross-check is NON-FATAL by default and becomes a
fatal finding (appended to ``errors_found``) only when explicitly configured via
env ``TA_CITATION_FATAL=1``. The structural guards (R6.1/6.2/6.4/6.5) stay
non-fatal and additive in all cases.

Also asserts the two validator copies (scratch/ and skills/scripts/) are kept
byte-identical (Task 8.8 sync requirement).
"""
import importlib
import sys
from pathlib import Path

import pytest

# --------------------------------------------------------------------------- #
# Import the canonical validator (scratch copy) as a module.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / "scratch"
if str(SCRATCH) not in sys.path:
    sys.path.insert(0, str(SCRATCH))

vds = importlib.import_module("validate_docx_structure")


# A draft with a guaranteed two-way citation mismatch:
#   - in-text "(Nonexistent, 2099)" has no matching reference entry (R1.5)
#   - the only entry "Smith (2010)" is never cited (R1.6)
_DRAFT_WITH_MISMATCH = """# BAB I PENDAHULUAN

## Latar Belakang

Menurut penelitian terbaru (Nonexistent, 2099), topik ini penting untuk dikaji.

# DAFTAR PUSTAKA

Smith, J. (2010). A real reference that nobody cites. Jurnal Contoh.
"""


@pytest.fixture()
def draft_file(tmp_path):
    p = tmp_path / "Tugas_Akhir_Draft.md"
    p.write_text(_DRAFT_WITH_MISMATCH, encoding="utf-8")
    return p


def test_default_citation_crosscheck_is_non_fatal(draft_file, monkeypatch, capsys):
    """R1.7 default: without TA_CITATION_FATAL the mismatch is reported as a
    non-fatal [WARN] line and is NOT added to errors_found."""
    monkeypatch.setenv("TA_DRAFT_PATH", str(draft_file))
    monkeypatch.delenv("TA_CITATION_FATAL", raising=False)
    # Ensure the flag is not present in argv either.
    monkeypatch.setattr(sys, "argv", ["validate_docx_structure.py"])

    errors_found = []
    vds._run_writing_guards(errors_found)

    out = capsys.readouterr().out
    assert "[WARN][sitasi]" in out, "expected a non-fatal citation warning to be printed"
    assert "non-fatal" in out
    assert errors_found == [], "default mode must NOT push citation mismatches into errors_found"


def test_fatal_env_promotes_citation_mismatch_to_error(draft_file, monkeypatch, capsys):
    """R1.7 fatal: TA_CITATION_FATAL=1 turns citation mismatches into fatal
    findings appended to errors_found."""
    monkeypatch.setenv("TA_DRAFT_PATH", str(draft_file))
    monkeypatch.setenv("TA_CITATION_FATAL", "1")
    monkeypatch.setattr(sys, "argv", ["validate_docx_structure.py"])

    errors_found = []
    vds._run_writing_guards(errors_found)

    out = capsys.readouterr().out
    assert "FATAL" in out
    assert errors_found, "fatal mode must push citation mismatches into errors_found"
    # Every appended finding is a citation warning (structural guards stay non-fatal).
    assert all("[WARN][sitasi]" in e for e in errors_found)
    # Both directions detected: forward (in-text -> entry) and backward (entry -> in-text).
    assert any("Nonexistent" in e for e in errors_found), "forward mismatch (R1.5) missing"
    assert any("Smith" in e for e in errors_found), "backward mismatch (R1.6) missing"


def test_fatal_disabled_values_remain_non_fatal(draft_file, monkeypatch, capsys):
    """Only truthy toggles enable fatal mode; e.g. '0' stays non-fatal."""
    monkeypatch.setenv("TA_DRAFT_PATH", str(draft_file))
    monkeypatch.setenv("TA_CITATION_FATAL", "0")
    monkeypatch.setattr(sys, "argv", ["validate_docx_structure.py"])

    errors_found = []
    vds._run_writing_guards(errors_found)

    assert errors_found == [], "'0' must not enable fatal mode"


def test_missing_draft_skips_guards_without_error(monkeypatch, tmp_path, capsys):
    """Defensive: an unreadable/missing draft degrades to a skip note and never
    adds to errors_found (preserves legacy validation semantics, R6.6)."""
    monkeypatch.setenv("TA_DRAFT_PATH", str(tmp_path / "does_not_exist.md"))
    monkeypatch.setenv("TA_CITATION_FATAL", "1")
    monkeypatch.setattr(sys, "argv", ["validate_docx_structure.py"])

    errors_found = []
    vds._run_writing_guards(errors_found)

    assert errors_found == []


def test_both_validator_copies_are_byte_identical():
    """Task 8.8: the scratch/ and skills/scripts/ validator copies must stay in
    sync (kept byte-identical so the guard wiring cannot diverge)."""
    scratch_bytes = (ROOT / "scratch" / "validate_docx_structure.py").read_bytes()
    skills_bytes = (ROOT / "skills" / "scripts" / "validate_docx_structure.py").read_bytes()
    assert scratch_bytes == skills_bytes, (
        "validate_docx_structure.py copies diverged; re-sync scratch/ and skills/scripts/"
    )
