# Implementation Plan

## Overview

This plan follows the exploratory bugfix workflow for the image-injection pipeline. It first surfaces counterexamples for the four content-level defects (C1 duplicate media, C2 ambiguous caption resolution, C3 packed-vs-injected content drift, C4 image/caption page splits) on the UNFIXED code, captures preservation baselines for non-buggy behavior, then applies a minimal two-file fix (`skills/scripts/inject_all_images.py` and `skills/scripts/validate_docx_structure.py`) and verifies both the fix and preservation hold. Exploration and preservation tests are written and run BEFORE the implementation.

## Task Dependency Graph

```json
{
  "waves": [
    {
      "wave": 1,
      "tasks": ["1", "2"],
      "description": "Write exploration tests (must FAIL) and preservation tests (must PASS) on the UNFIXED code. No dependencies."
    },
    {
      "wave": 2,
      "tasks": ["3.1", "3.2"],
      "description": "Implement the fix in the injector and the validator. Depends on understanding gained from wave 1."
    },
    {
      "wave": 3,
      "tasks": ["3.3", "3.4"],
      "description": "Re-run the same exploration tests (now PASS) and preservation tests (still PASS). Depends on wave 2."
    },
    {
      "wave": 4,
      "tasks": ["4"],
      "description": "Add supporting unit and integration tests. Depends on wave 2/3."
    },
    {
      "wave": 5,
      "tasks": ["5"],
      "description": "Checkpoint: ensure the entire test suite passes. Depends on all prior tasks."
    }
  ]
}
```

- Tasks 1 and 2 have no dependencies and should be done first (in either order).
- Tasks 3.1 and 3.2 depend on the understanding gained from tasks 1 and 2.
- Tasks 3.3 and 3.4 depend on 3.1 and 3.2.
- Task 4 depends on 3.x. Task 5 depends on all prior tasks.

## Tasks

### Exploration: Bug Condition Tests (write BEFORE the fix)

- [x] 1. Write bug-condition exploration tests for all four defects (C1–C4)
  - **Property 1: Bug Condition** - Unique Media Content (C1), Exactly-One Resolution (C2), Packed-vs-Injected Content Integrity (C3), and Image/Caption Page-Split Safety (C4)
  - **CRITICAL**: These tests MUST FAIL on the unfixed code - failure confirms each defect exists
  - **DO NOT attempt to fix the test or the code when it fails** at this stage
  - **NOTE**: These tests encode the expected behavior - they will validate the fix once they pass after implementation
  - **GOAL**: Surface concrete counterexamples that demonstrate each defect from `isBugCondition(run)` in design
  - **Scoped PBT Approach**: For deterministic defects, scope each property to the concrete failing case(s) observed in the built document for reproducibility, then generalize where a property holds across inputs
  - Build the document with the current pipeline (or use a captured `.docx` output) and probe `word/media/*`, `word/document.xml`, and `word/_rels/document.xml.rels`
  - **C1 — Duplicate-media probe**: Compute MD5 of every injected media file referenced by a `w:drawing`; assert all distinct figures are unique. Expected counterexample: `image18 == image35 == seq_auth` share one MD5
  - **C2 — Resolution-count probe**: For each `post_com` manifest entry assert exactly one matching `Caption` paragraph (text contains `caption_match` and remainder matches `^(Gambar|Tabel)\s+[0-9\.]+$`); include a synthetic zero-match entry and a synthetic multi-match entry. Expected counterexample: an entry resolving to 0 or ≥2 captions (currently silently skipped)
  - **C3 — Content-integrity probe**: Assert `md5(packed word/media/imageNN) == md5(injected images/<file>)` for each `post_com` entry. Expected counterexample: a figure whose packed bytes differ from the injected `images/<file>` due to packing recompression
  - **C4 — Page-split probe**: Inject (or locate) a deliberately tall image and assert it carries `pageBreakBefore` and that the image+caption pair cannot split. Expected counterexample: a tall image lacking `pageBreakBefore`
  - Run all probes on the UNFIXED code
  - **EXPECTED OUTCOME**: Tests FAIL (this is correct - it proves the bugs exist)
  - Document the counterexamples found (shared MD5 set, the 0/≥2 caption entries, mismatched `imageNN`, the tall image without `pageBreakBefore`) to confirm or refute the root-cause hypotheses; if refuted, re-hypothesize before proceeding
  - Mark this task complete when the tests are written, run, and the failures are documented
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

### Preservation Tests (write BEFORE the fix)

- [x] 2. Write preservation property tests for unchanged behavior (Properties 5–8)
  - **Property 2: Preservation** - Non-Manifest Captions, SEQ Numbering Fields, Aspect-Ratio Rendering, and Front-Matter/TOC/Appendix Structure Unchanged
  - **IMPORTANT**: Follow the observation-first methodology - record actual outputs from the UNFIXED code, then assert them
  - **Why property-based**: Preservation is a universal property ("for all non-buggy inputs"); generate many caption/figure/document configurations to catch edge cases and give strong byte-for-byte guarantees
  - **Property 5 — Non-manifest caption preservation**: Observe on unfixed code that a `Caption` paragraph not referenced by any manifest entry (and its surrounding content) is untouched; assert it stays unchanged after the fix
  - **Property 6 — SEQ numbering preservation**: Observe `SEQ Gambar`/`SEQ Tabel` caption fields and figure/table numbering (including the first-caption `\r 1` restart switch) on unfixed code; assert they are preserved
  - **Property 7 — Aspect-ratio preservation**: Observe that a within-width image (≤ 5400000 EMU) keeps `noChangeAspect` and its scaled extent on unfixed code; assert it is preserved (page-split condition not holding)
  - **Property 8 — Structure preservation**: Observe `taappendixheading` outline level 8, `TOC9` `left='1'` indentation, and the Daftar Lampiran `TOC \n 9-9` field pass on unfixed code; assert existing structural validation (Sections A–J) still passes
  - Run all preservation tests on the UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms the baseline behavior to preserve)
  - Mark this task complete when the tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

### Implementation

- [x] 3. Fix content-level figure defects in the injector and validator

  - [x] 3.1 Harden caption resolution and content/page guards in `skills/scripts/inject_all_images.py`
    - Target the canonical `skills/scripts/inject_all_images.py` copy (the `scratch/` copy is out of scope; re-sync it from `skills/scripts/` afterward if kept)
    - **Exactly-one caption resolution (C2)**: Replace the break-on-first-match loop with a pass that collects ALL paragraphs where `pStyle == 'Caption'`, the text contains `caption_match`, and the remainder matches `^(Gambar|Tabel)\s+[0-9\.]+$`; if the count is `!= 1`, raise an error and exit non-zero (no silent skip); inject only when exactly one caption is found
    - **Post-pack content integrity (C3)**: Record the MD5 of each `images/<file>` at injection time keyed by the allocated `imageNN` name; copy bytes verbatim (the authoritative post-pack assertion runs in the validator); if a `source` path exists on disk, optionally log whether it matches but never fail on a `source` mismatch or missing `source`
    - **Duplicate-content guard (C1)**: Track the MD5 of every media file injected during the run; if a new injection would introduce an MD5 already present for a different figure, fail the run (legitimate reuse, e.g. the two `modal-fasilitas-aset.png` mockups, is reconciled via a manifest/validator allow-list, not silently duplicated)
    - **Oversized-image page break (C4)**: Define an explicit printable page-height threshold in EMU; apply `pageBreakBefore` when the scaled image height exceeds the threshold (not only the existing `cy > 5400000` width-derived check), while keeping `keepNext`/`keepLines` on both the drawing and caption paragraphs
    - **No behavior change for correct entries**: Leave drawing XML generation, centering, width scaling (≤ 5400000 EMU with `noChangeAspect`), relationship/`rId` allocation, and removal of a pre-existing preceding drawing exactly as today for entries that already satisfy the properties
    - _Bug_Condition: isBugCondition(run) — duplicateContent (C1), ambiguousResolution (C2), contentDrift (C3), pageSplitRisk (C4) from design_
    - _Expected_Behavior: Property P — exactly-one caption+media resolution, packed media MD5 == injected images/<file> MD5, globally unique media MD5, image+caption kept on one page (Properties 1–4)_
    - _Preservation: Non-manifest captions, SEQ numbering, aspect-ratio rendering, front-matter/TOC/appendix structure unchanged (Properties 5–8)_
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 3.2 Add content-level validation checks to `skills/scripts/validate_docx_structure.py`
    - Append new check sections to the existing `main()` error-collection flow; target the canonical `skills/scripts/validate_docx_structure.py` copy
    - **Media MD5 uniqueness (C1)**: Compute MD5 for every `word/media/*` referenced by an injected `w:drawing`; append an error for any MD5 shared by two distinct figures (honoring the reconciled-reuse allow-list)
    - **Exactly-one resolution (C2)**: For each `post_com` manifest entry, count matching caption paragraphs in `document.xml`; append an error when the count is not exactly 1
    - **Content integrity (C3)**: For each `post_com` entry, compare the packed `word/media/imageNN` MD5 against the MD5 of the `images/<file>` that should have been injected; append an error on mismatch; when the declared `source` exists on disk, emit an informational note if it differs but do not append an error for a `source` mismatch or absence
    - **Page-split safety (C4)**: For each figure, append an error when an image taller than the threshold lacks `pageBreakBefore`, in addition to the existing `keepNext`/`keepLines` presence checks (Sections F and I/J)
    - **Preserve existing checks**: Sections A–J remain unchanged and run first; new checks only add failures, never relax existing ones; exit non-zero on any error
    - _Bug_Condition: isBugCondition(run) — detection of duplicateContent, ambiguousResolution, contentDrift, pageSplitRisk from design_
    - _Expected_Behavior: validation SHALL fail on any duplicate MD5, non-exactly-one resolution, packed-vs-injected mismatch, or splittable figure (Properties 1–4)_
    - _Preservation: Existing Sections A–J continue to pass unchanged on a correct document (Properties 5–8)_
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 3.3 Verify the bug-condition exploration tests now pass
    - **Property 1: Expected Behavior** - Unique Media Content (C1), Exactly-One Resolution (C2), Packed-vs-Injected Content Integrity (C3), and Image/Caption Page-Split Safety (C4)
    - **IMPORTANT**: Re-run the SAME tests from task 1 - do NOT write new tests
    - The tests from task 1 encode the expected behavior; when they pass, they confirm each defect is resolved
    - **EXPECTED OUTCOME**: Tests PASS (confirms C1–C4 are fixed and validation fails on crafted bad inputs)
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 3.4 Verify the preservation tests still pass
    - **Property 2: Preservation** - Non-Manifest Captions, SEQ Numbering Fields, Aspect-Ratio Rendering, and Front-Matter/TOC/Appendix Structure Unchanged
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions for non-buggy inputs)
    - Confirm all preservation tests still pass after the fix (Properties 5–8)
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

### Supporting Tests

- [x] 4. Add unit and integration tests for the fix
  - **Unit — caption resolution**: exactly-one match injects; zero matches fails; multiple matches fails
  - **Unit — MD5 content integrity**: packed media matching the injected `images/<file>` passes; recompressed/altered bytes fail
  - **Unit — duplicate-media guard**: a new injection with an already-seen MD5 fails (except reconciled reuse)
  - **Unit — page break**: image height above threshold receives `pageBreakBefore`; below threshold does not
  - **Unit — validator**: each new check (uniqueness, resolution count, content integrity, page-split) raises on a crafted bad document and passes on a good one
  - **Integration — happy path**: full pipeline run end-to-end; assert all four new validator checks pass and exit code is 0
  - **Integration — negative**: seed a duplicate media file, a zero-match caption, a recompressed image, and an oversized image; assert the pipeline fails with a clear per-defect error message
  - **Integration — regression**: run existing validator Sections A–J on the fixed output and confirm they still pass unchanged
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4_

### Checkpoint

- [x] 5. Checkpoint - Ensure all tests pass
  - Run the full test suite (exploration, preservation, unit, property-based, integration) and confirm everything passes
  - Confirm the bug-condition exploration tests (task 1) now pass and the preservation tests (task 2) still pass
  - If the `scratch/` copies of the scripts are retained, re-sync them from the canonical `skills/scripts/` copies
  - Ensure all tests pass; ask the user if questions arise

## Notes

- The fix is deliberately minimal and touches only two files: `skills/scripts/inject_all_images.py` and `skills/scripts/validate_docx_structure.py`. No change to the COM/pack steps, the manifest schema, or any non-figure handling.
- "Content match" (C3) is defined as the packed `word/media/imageNN` bytes MD5-matching the injected `images/<file>` (post-pack integrity). The manifest `source` field is provenance only and is cross-checked best-effort, never a build failure on its own.
- Exploration tests (task 1) must FAIL on unfixed code; preservation tests (task 2) must PASS on unfixed code. Do not implement the fix until both are written and run.
- Legitimate media reuse across distinct figures is handled via a reconciled allow-list in the manifest/validator rather than by silently producing duplicate media.
