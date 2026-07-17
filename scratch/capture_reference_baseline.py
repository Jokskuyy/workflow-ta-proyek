"""Capture the CURRENT (pre-refactor) generation output as a backward-compatibility
baseline (Dokumen_Referensi) for the dynamic-generation-pipeline refactor.

Task 1.1 (.kiro/specs/dynamic-generation-pipeline). Captures three artifacts under
``tests/fixtures/`` so Task 12.1 (Property 17) and Task 12.2 can verify backward
compatibility after the refactor:

  (a) the set of figure/table caption numbers -> reference_caption_numbers.json
  (b) a summary of ``validate_docx_structure.py`` output (exit code + the
      WARN/ERROR lines / success marker) -> reference_validator_summary.json
  (c) a copy of the generated docx -> Dokumen_Referensi.docx

The caption-number collector ``collect_caption_numbers`` is a PURE function
(takes an iterable of texts, returns ``set[str]``) so Task 12.1's Property 17
test can import and reuse it. All paths are resolved relative to the workspace
root; no absolute paths are used.

This is BASELINE CAPTURE ONLY: it does NOT refactor or rebuild generation code.
It reads caption numbers from the existing ``Tugas_Akhir_Formatted.docx`` and runs
``scratch/validate_docx_structure.py`` against it. (Only rebuild manually if the
docx is missing.)
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable

# WordprocessingML namespace.
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

# A caption number is "C.Y" (chapter.sequence), e.g. "2.1", "3.12".
# The leading label decides whether it is a figure (Gambar) or a table (Tabel).
CAPTION_NUMBER_RE = re.compile(r"^(Gambar|Tabel)\s+([0-9]+\.[0-9]+)", re.IGNORECASE)


# --------------------------------------------------------------------------- #
# PURE function (reused by Task 12.1 / Property 17).
# --------------------------------------------------------------------------- #
def collect_caption_numbers(texts: Iterable[str]) -> set[str]:
    """Collect the set of caption numbers ("C.Y") from caption texts.

    PURE: no I/O, no globals; deterministic for a given input. Accepts an
    iterable of caption paragraph texts and returns the set of "C.Y" numbers
    found, matching ``^(Gambar|Tabel)\\s+([0-9]+\\.[0-9]+)`` on each text.
    Non-matching texts are ignored.

    This is the single source of truth for the backward-compatibility number set
    so the same logic is reused by the Property 17 test.
    """
    numbers: set[str] = set()
    for text in texts:
        if text is None:
            continue
        m = CAPTION_NUMBER_RE.match(text.strip())
        if m:
            numbers.add(m.group(2))
    return numbers


def classify_caption_numbers(texts: Iterable[str]) -> dict[str, set[str]]:
    """Split caption numbers by kind ('Gambar' vs 'Tabel'). Also PURE.

    Helper for richer reporting in the fixture; the canonical set used by
    Property 17 is the union, produced by :func:`collect_caption_numbers`.
    """
    figures: set[str] = set()
    tables: set[str] = set()
    for text in texts:
        if text is None:
            continue
        m = CAPTION_NUMBER_RE.match(text.strip())
        if not m:
            continue
        if m.group(1).lower() == "gambar":
            figures.add(m.group(2))
        else:
            tables.add(m.group(2))
    return {"figures": figures, "tables": tables}


def diff_caption_numbers(baseline: Iterable[str], current: Iterable[str]) -> dict:
    """Compare two caption-number sets. PURE: no I/O, deterministic.

    Returns a dict describing the difference between a ``baseline`` set (the
    reference / "old" numbers) and a ``current`` set ("new" numbers):

      ``equal``   - True iff both sets are identical.
      ``missing`` - sorted numbers present in baseline but NOT in current
                    (i.e. caption numbers that disappeared).
      ``extra``   - sorted numbers present in current but NOT in baseline
                    (i.e. caption numbers that newly appeared).

    Used by the ``compare`` mode to build the R8.6 "old vs new" warning.
    Numbers are sorted naturally (chapter, then sequence) for stable output.
    """
    base_set = {n for n in baseline if n}
    cur_set = {n for n in current if n}

    def _key(num: str) -> tuple[int, int, str]:
        parts = num.split(".")
        try:
            return (int(parts[0]), int(parts[1]), num)
        except (ValueError, IndexError):
            return (1 << 30, 1 << 30, num)

    return {
        "equal": base_set == cur_set,
        "missing": sorted(base_set - cur_set, key=_key),
        "extra": sorted(cur_set - base_set, key=_key),
    }


def is_fatal_validator_result(exit_code: int, stdout: str) -> bool:
    """Decide whether a validator run is a FATAL failure (R8.5). PURE.

    Fatal iff the validator exited non-zero OR the explicit FAILED marker is
    present. Non-fatal [WARN] lines do not count as fatal.
    """
    return exit_code != 0 or FAILED_MARKER in stdout


# --------------------------------------------------------------------------- #
# DOCX reading helpers (impure: read the package).
# --------------------------------------------------------------------------- #
def _paragraph_style(p: ET.Element) -> str:
    pPr = p.find(f"{{{W_NS}}}pPr")
    if pPr is None:
        return ""
    pStyle = pPr.find(f"{{{W_NS}}}pStyle")
    if pStyle is None:
        return ""
    return pStyle.get(f"{{{W_NS}}}val") or ""


def _paragraph_text(p: ET.Element) -> str:
    return "".join(t.text for t in p.iter(f"{{{W_NS}}}t") if t.text).strip()


def extract_caption_texts(docx_path: Path) -> list[str]:
    """Return the text of every paragraph styled 'Caption' in the docx body.

    The pure :func:`collect_caption_numbers` is then applied to these texts.
    """
    with zipfile.ZipFile(docx_path) as z:
        doc_xml = z.read("word/document.xml")
    root = ET.fromstring(doc_xml)
    body = root.find(f"{{{W_NS}}}body")
    if body is None:
        return []
    texts: list[str] = []
    for p in body.iter(f"{{{W_NS}}}p"):
        if _paragraph_style(p) == "Caption":
            texts.append(_paragraph_text(p))
    return texts


# --------------------------------------------------------------------------- #
# Validator summary helpers (impure: run the validator).
# --------------------------------------------------------------------------- #
SUCCESS_MARKER = "=== VALIDATION SUCCESSFUL: No regressions found! ==="
FAILED_MARKER = "=== VALIDATION FAILED ==="


def summarize_validator_output(exit_code: int, stdout: str) -> dict:
    """Extract a compact summary of validate_docx_structure.py output.

    Keeps the exit code, whether the success/failed markers appeared, and the
    ERROR / [WARN] lines so Task 12.2 can diff against a post-refactor run
    without storing the full noisy log.
    """
    lines = stdout.splitlines()
    error_lines = [ln.strip() for ln in lines if ln.lstrip().startswith("- ")]
    warn_lines = [ln.strip() for ln in lines if "[WARN]" in ln]
    return {
        "exit_code": exit_code,
        "success": exit_code == 0 and SUCCESS_MARKER in stdout,
        "success_marker_present": SUCCESS_MARKER in stdout,
        "failed_marker_present": FAILED_MARKER in stdout,
        "error_count": len(error_lines),
        "error_lines": error_lines,
        "warn_count": len(warn_lines),
        "warn_lines": warn_lines,
    }


def run_validator(workspace_root: Path, validator: Path, docx_path: Path) -> tuple[int, str]:
    """Run the validator against the docx from the workspace root.

    The validator resolves auxiliary paths (images/manifest.json, etc.) relative
    to its CWD, so we run it from the workspace root.
    """
    proc = subprocess.run(
        [sys.executable, str(validator), str(docx_path)],
        cwd=str(workspace_root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


# --------------------------------------------------------------------------- #
# Capture routine (Task 1.1 behavior, unchanged semantics).
# --------------------------------------------------------------------------- #
def run_capture(workspace_root: Path) -> int:
    # All paths relative to workspace root; no absolute paths.
    docx_rel = "Tugas_Akhir_Formatted.docx"
    docx_path = workspace_root / docx_rel
    validator = workspace_root / "scratch" / "validate_docx_structure.py"
    fixtures_dir = workspace_root / "tests" / "fixtures"

    if not docx_path.exists():
        print(f"ERROR: generated docx not found at '{docx_rel}'. Build the "
              f"pipeline first (this script does not rebuild).")
        return 1

    fixtures_dir.mkdir(parents=True, exist_ok=True)

    # (a) Caption numbers (figure/table) via the PURE collector.
    caption_texts = extract_caption_texts(docx_path)
    numbers = collect_caption_numbers(caption_texts)
    by_kind = classify_caption_numbers(caption_texts)

    caption_payload = {
        "source": docx_rel,
        "caption_numbers": sorted(numbers),
        "figure_numbers": sorted(by_kind["figures"]),
        "table_numbers": sorted(by_kind["tables"]),
        "caption_count": len(caption_texts),
        "figure_count": len(by_kind["figures"]),
        "table_count": len(by_kind["tables"]),
    }
    caption_file = fixtures_dir / "reference_caption_numbers.json"
    caption_file.write_text(
        json.dumps(caption_payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # (b) Validator summary.
    exit_code, stdout = run_validator(workspace_root, validator, docx_path)
    validator_summary = summarize_validator_output(exit_code, stdout)
    validator_summary["source"] = docx_rel
    validator_file = fixtures_dir / "reference_validator_summary.json"
    validator_file.write_text(
        json.dumps(validator_summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # (c) Copy of the generated docx as Dokumen_Referensi.
    reference_docx = fixtures_dir / "Dokumen_Referensi.docx"
    shutil.copyfile(docx_path, reference_docx)

    # Report (paths shown relative to workspace root).
    def rel(p: Path) -> str:
        return p.relative_to(workspace_root).as_posix()

    print("=== Baseline capture complete ===")
    print(f"(a) caption numbers  -> {rel(caption_file)}")
    print(f"      total={len(numbers)} "
          f"figures={len(by_kind['figures'])} tables={len(by_kind['tables'])}")
    print(f"      numbers={sorted(numbers)}")
    print(f"(b) validator summary-> {rel(validator_file)}")
    print(f"      exit_code={exit_code} success={validator_summary['success']} "
          f"errors={validator_summary['error_count']} warns={validator_summary['warn_count']}")
    print(f"(c) reference docx   -> {rel(reference_docx)} "
          f"({reference_docx.stat().st_size} bytes)")
    return 0


# --------------------------------------------------------------------------- #
# Compare / promotion routine (Task 12.4, R8.5 + R8.6).
# --------------------------------------------------------------------------- #
def run_compare(workspace_root: Path, *, promote: bool = False) -> int:
    """Compare the CURRENT generated docx against the captured baseline.

    R8.5: if the current document produces ANY fatal validator failure, HALT
          promotion (never overwrite Dokumen_Referensi.docx), log clearly, and
          return non-zero.
    R8.6: if the current caption-number set differs from the baseline set, log a
          clear WARNING listing baseline (old) vs current (new) numbers -- the
          missing and extra numbers. This is a WARNING, not fatal on its own.

    Promotion (``--promote``) overwrites the reference fixtures, but is GATED on
    there being NO fatal validator failure.
    """
    docx_rel = "Tugas_Akhir_Formatted.docx"
    docx_path = workspace_root / docx_rel
    validator = workspace_root / "scratch" / "validate_docx_structure.py"
    fixtures_dir = workspace_root / "tests" / "fixtures"
    caption_file = fixtures_dir / "reference_caption_numbers.json"
    validator_baseline_file = fixtures_dir / "reference_validator_summary.json"
    reference_docx = fixtures_dir / "Dokumen_Referensi.docx"

    def rel(p: Path) -> str:
        try:
            return p.relative_to(workspace_root).as_posix()
        except ValueError:
            return str(p)

    print("=== Compare current document against baseline (Task 12.4) ===")

    if not docx_path.exists():
        print(f"ERROR: generated docx not found at '{docx_rel}'. Build the "
              f"pipeline first (this script does not rebuild).")
        return 1
    if not caption_file.exists():
        print(f"ERROR: baseline '{rel(caption_file)}' missing. Run "
              f"`capture` first to record the baseline.")
        return 1

    # --- Current caption numbers (via the PURE collector). -------------------
    current_texts = extract_caption_texts(docx_path)
    current_numbers = collect_caption_numbers(current_texts)

    # --- Baseline caption numbers. -------------------------------------------
    baseline_payload = json.loads(caption_file.read_text(encoding="utf-8"))
    baseline_numbers = set(baseline_payload.get("caption_numbers", []))

    # --- Run validator on the CURRENT document. ------------------------------
    exit_code, stdout = run_validator(workspace_root, validator, docx_path)
    current_summary = summarize_validator_output(exit_code, stdout)
    fatal = is_fatal_validator_result(exit_code, stdout)

    print(f"validator: exit_code={exit_code} success={current_summary['success']} "
          f"errors={current_summary['error_count']} warns={current_summary['warn_count']}")

    # --- R8.6: caption-number difference WARNING (non-fatal). ----------------
    diff = diff_caption_numbers(baseline_numbers, current_numbers)
    if diff["equal"]:
        print(f"caption numbers: MATCH baseline "
              f"({len(current_numbers)} numbers, sets equal)")
    else:
        print("[WARN][R8.6] Caption-number set DIFFERS from baseline (Dokumen_Referensi):")
        print(f"    baseline (old) count={len(baseline_numbers)} "
              f"current (new) count={len(current_numbers)}")
        print(f"    missing (in baseline, not in current): {diff['missing']}")
        print(f"    extra   (in current, not in baseline): {diff['extra']}")
        print("    NOTE: caption-number difference is a WARNING, not fatal by itself.")

    # --- R8.5: fatal validator failure HALTS promotion. ----------------------
    if fatal:
        print("[FATAL][R8.5] Current document produced a FATAL validator failure.")
        if current_summary["failed_marker_present"]:
            print("    VALIDATION FAILED marker present.")
        if exit_code != 0:
            print(f"    Validator exit_code={exit_code} (non-zero).")
        for ln in current_summary["error_lines"]:
            print(f"    ERROR: {ln}")
        print(f"    HALTING promotion: '{rel(reference_docx)}' was NOT overwritten.")
        return 1

    # --- Promotion (gated on no fatal failure). ------------------------------
    if promote:
        fixtures_dir.mkdir(parents=True, exist_ok=True)
        by_kind = classify_caption_numbers(current_texts)
        caption_payload = {
            "source": docx_rel,
            "caption_numbers": sorted(current_numbers),
            "figure_numbers": sorted(by_kind["figures"]),
            "table_numbers": sorted(by_kind["tables"]),
            "caption_count": len(current_texts),
            "figure_count": len(by_kind["figures"]),
            "table_count": len(by_kind["tables"]),
        }
        caption_file.write_text(
            json.dumps(caption_payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        current_summary["source"] = docx_rel
        validator_baseline_file.write_text(
            json.dumps(current_summary, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        shutil.copyfile(docx_path, reference_docx)
        print(f"PROMOTED: reference updated -> {rel(reference_docx)} "
              f"(no fatal validator failure).")
        if not diff["equal"]:
            print("    (Promoted despite caption-number WARNING above.)")
    else:
        print("No fatal validator failure. (Run with --promote to update the "
              "reference fixtures.)")

    print("=== Compare complete ===")
    return 0


# --------------------------------------------------------------------------- #
# CLI dispatch: `capture` (Task 1.1) vs `compare` (Task 12.4).
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    # workspace_root = repo root (this script lives in scratch/).
    workspace_root = Path(__file__).resolve().parents[1]

    parser = argparse.ArgumentParser(
        description="Capture or compare the generation backward-compatibility "
                    "baseline (Dokumen_Referensi)."
    )
    sub = parser.add_subparsers(dest="mode")
    sub.add_parser(
        "capture",
        help="Capture the current generated docx as the baseline "
             "(Task 1.1 behavior; default when no subcommand is given).",
    )
    p_compare = sub.add_parser(
        "compare",
        help="Compare the current generated docx against the baseline "
             "(R8.5 promotion control + R8.6 caption-number-difference warning).",
    )
    p_compare.add_argument(
        "--promote",
        action="store_true",
        help="Overwrite the reference fixtures with the current document. "
             "Gated on NO fatal validator failure (R8.5).",
    )

    args = parser.parse_args(argv)

    # Default (no subcommand) preserves Task 1.1's capture path.
    if args.mode in (None, "capture"):
        return run_capture(workspace_root)
    if args.mode == "compare":
        return run_compare(workspace_root, promote=args.promote)
    parser.error(f"unknown mode: {args.mode!r}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
