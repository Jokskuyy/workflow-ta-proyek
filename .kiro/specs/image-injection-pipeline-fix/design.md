# Image Injection Pipeline Fix Bugfix Design

## Overview

The thesis automation pipeline (`skills/scripts/build_pipeline.py`) builds a formatted Word document from a Markdown draft, then injects every figure with a single manifest-driven, post-COM step (`skills/scripts/inject_all_images.py`) that reads `images/manifest.json` (32 `post_com` entries, each keyed by `caption_match` + `file` + `source`). Structural correctness is then checked by `scratch/validate_docx_structure.py`.

Four related defects affect the figures in the generated document:

1. **Duplicate media content** — distinct figures end up referencing byte-identical media (e.g., `image18 == image35 == seq_auth`), and nothing detects it.
2. **Ambiguous caption resolution** — a manifest entry's `caption_match` can resolve to zero or multiple caption paragraphs, causing wrong-location injection or a silent skip that validation never flags.
3. **Content drift** — the media bytes that end up in the packed `word/media/imageNN` can differ from the `images/<file>` that was injected (e.g., Word/packing lossy recompression), and validation never compares content.
4. **Image/caption page splits** — a very tall image can split from its caption (or split itself) across a page boundary because `keepNext`/`keepLines` alone is ignored for oversized images.

The fix is twofold and deliberately minimal: harden `inject_all_images.py` so each manifest entry resolves to exactly one caption and one media file, the bytes that land in the packed document match the `images/<file>` that was injected, no media content is duplicated, and oversized figures get a page break; and extend `validate_docx_structure.py` with content-level checks (MD5 uniqueness, exactly-one resolution, injected-content integrity, page-split safety) so any violation fails the build. Behavior for non-figure content and figures that are already correct must remain unchanged.

> **Canonical script locations.** Both `inject_all_images.py` and `validate_docx_structure.py` exist under `skills/scripts/` (the canonical, pipeline-invoked copies) and under `scratch/` (working copies). This design targets the `skills/scripts/` copies; the `scratch/` copies are out of scope and, if kept, should be re-synced from `skills/scripts/` after the fix.

> **Content-identity convention (resolved).** The manifest's `file` is the curated image actually injected (under `images/`); its `source` is provenance metadata and is frequently a *different* file (e.g., `dokumentasi/login-page.png`) or a path that no longer exists (`unpacked_ta/word/media/...`). Therefore "content match" (Defect 3 / Req 2.3) is defined as: the bytes that end up in the packed `word/media/imageNN` MUST MD5-match the `images/<file>` that was injected (post-pack integrity, i.e. no recompression/alteration during packing). The `source` field is cross-checked on a best-effort basis only when the file exists on disk; a missing or byte-different `source` is reported as a non-fatal note, never a build failure.

## Glossary

- **Bug_Condition (C)**: A pipeline run whose generated document or manifest exhibits at least one of: duplicate media content, ambiguous/unresolved caption resolution, injected-vs-source content mismatch, or a splittable image+caption pair.
- **Property (P)**: The desired post-fix behavior — every figure resolves to exactly one caption and one media file, the packed media bytes match the `images/<file>` that was injected by MD5, no media content (by MD5) is duplicated across distinct figures, and no image+caption pair can split across a page.
- **Preservation**: Existing behavior that must remain unchanged — non-manifest caption paragraphs, `SEQ Gambar`/`SEQ Tabel` numbering, aspect-ratio rendering for within-width images, and front-matter/TOC/appendix structure.
- **inject_all_images(docx_path)**: The injector in `skills/scripts/inject_all_images.py` that resolves each manifest caption, copies the media into `word/media/`, adds a relationship, and inserts a centered `w:drawing` paragraph before the caption.
- **validate_docx_structure.py**: The validator in `skills/scripts/validate_docx_structure.py` that opens the packed `.docx` and asserts structural/field invariants, exiting non-zero on any error.
- **manifest entry**: A record in `images/manifest.json` with `id`, `file` (the bytes actually injected, under `images/`), `caption_match` (substring of the target caption), `source` (declared provenance, often a different or now-absent file), and `inject_method: post_com`.
- **injected file**: `images/<file>` — the curated image whose bytes the injector copies into `word/media/`. This is the authoritative content reference for the integrity check.
- **media MD5**: The MD5 hash of a file in `word/media/`, used as the content identity of an injected figure.
- **EMU**: English Metric Units (9525 EMU per pixel at 96 DPI); the max content width is 5400000 EMU (~15 cm).

## Bug Details

### Bug Condition

The bug manifests when a pipeline run produces a generated document in which one or more figures are wrong at the content level rather than the structural level. Concretely, the injector resolves a `caption_match` to the wrong number of caption paragraphs (zero or many), the bytes that land in the packed document do not match the `images/<file>` that was injected, leaves two distinct figures sharing identical media bytes, or places a tall image such that it can split from its caption — and none of these conditions is detected by the current validator.

**Formal Specification:**
```
FUNCTION isBugCondition(run)
  INPUT: run with { document (packed .docx), manifest, mediaFiles }
  OUTPUT: boolean

  // C1: Duplicate media content across distinct figures
  duplicateContent := EXISTS m1, m2 IN injectedMediaOf(run.document)
                        WHERE m1 != m2 AND md5(m1) == md5(m2)

  // C2: Ambiguous or unresolved caption resolution
  ambiguousResolution := EXISTS entry IN run.manifest WHERE
                           entry.inject_method == "post_com" AND
                           captionMatchCount(entry.caption_match, run.document) != 1

  // C3: Packed media bytes differ from the injected images/<file>
  contentDrift := EXISTS entry IN run.manifest WHERE
                    entry.inject_method == "post_com" AND
                    md5(injectedMediaFor(entry, run.document)) != md5(injectedFile(entry))

  // C4: An image+caption pair can split across a page boundary
  pageSplitRisk := EXISTS fig IN figuresOf(run.document) WHERE
                     NOT (drawingHasKeepNextKeepLines(fig)
                          AND captionHasKeepNextKeepLines(fig)
                          AND (imageHeightEmu(fig) <= MAX_HEIGHT
                               OR drawingHasPageBreakBefore(fig)))

  RETURN duplicateContent OR ambiguousResolution OR contentDrift OR pageSplitRisk
END FUNCTION
```

### Examples

- **C1 — Duplicate media**: After the COM step renumbers/strips custom images, `image18`, `image35`, and the source `seq_auth` resolve to identical MD5 bytes. Expected: each sequence-diagram figure references its own distinct media; validation fails on any duplicate MD5.
- **C2 — Zero matches**: An entry whose `caption_match` no longer appears (caption text changed) is silently skipped (`"Error: Could not find caption..."` printed, build continues). Expected: the run fails because the entry resolved to 0 captions.
- **C2 — Multiple matches**: A `caption_match` substring that appears in two `Caption` paragraphs injects against the first one found. Expected: the run fails because the entry resolved to 2 captions.
- **C3 — Content drift**: `mockup_dashboard_admin.png` is injected at full fidelity, but the corresponding `imageNN` packed into the output is smaller due to recompression during packing. Expected: validation fails because the packed media MD5 ≠ the injected `images/<file>` MD5. (The `source` field, e.g. `dokumentasi/header+gedung-view.png`, is provenance only and is not required to match byte-for-byte.)
- **C4 — Page split**: A figure taller than the page splits from its caption across pages even though both carry `keepNext`/`keepLines`. Expected: an oversized image gets `pageBreakBefore` so the image and caption stay together; validation fails if any figure can split.

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Caption paragraphs not referenced by any manifest entry, and their surrounding content, remain untouched (Req 3.1).
- `SEQ Gambar` / `SEQ Tabel` caption fields and figure/table numbering (including the first-caption `\r 1` restart switch) are preserved after injection (Req 3.2).
- Images within or scaled to the maximum width (≤ 5400000 EMU) continue to render with aspect ratio preserved (Req 3.3).
- Front-matter, table-of-contents, and appendix structures (`taappendixheading` outline level 8, `TOC9` `left='1'` indentation, the Daftar Lampiran `TOC \n 9-9` field) continue to pass existing structural validation unchanged (Req 3.4).

**Scope:**
All inputs that do NOT involve the bug condition must be completely unaffected by this fix. This includes:
- Body text, headings, code blocks, tables, and any non-figure paragraph.
- Caption paragraphs that no manifest entry targets.
- Figures that already resolve uniquely, already match their source bytes, are already non-duplicated, and already fit within page bounds — these must produce the same document as before.
- All checks the current validator already performs (Sections A–J): they must continue to pass exactly as today on a correct document.

**Note:** The expected correct behavior for buggy inputs is defined in the Correctness Properties section (Properties 1–4). This section focuses on what must NOT change.

## Hypothesized Root Cause

Based on the defect descriptions and the current code, the most likely causes are:

1. **No content-identity verification anywhere in the pipeline**: Neither `inject_all_images.py` nor `validate_docx_structure.py` computes or compares MD5 hashes. Duplicate media (C1) and content drift (C3) are therefore structurally invisible — the validator only checks paragraph styles, fields, and keep flags, never media bytes.

2. **First-match caption resolution with silent failure**: In `inject_all_images.py`, the caption loop breaks on the first `Caption` paragraph whose text contains `caption_match` and whose remainder matches `^(Gambar|Tabel)\s+[0-9\.]+$`. It never counts total matches, so a substring that matches multiple captions injects against the wrong one, and a zero-match entry only prints a warning and continues (C2).

3. **No post-pack integrity check on injected bytes**: The injector copies bytes from `images/<file>` into `word/media/imageNN`, but nothing re-reads the packed output to confirm those exact bytes survived the re-zip/packing step. The manifest also declares a separate `source` path that is frequently a *different* file (e.g., `dokumentasi/login-page.png` vs `images/mockup_login_admin.png`) or a path that no longer exists (`unpacked_ta/word/media/...`), so `source` cannot serve as the integrity reference. Without comparing the packed media MD5 against the injected `images/<file>` MD5, any recompression or alteration during packing goes undetected (C3).

4. **Height threshold not enforced for page-keeping**: `generate_drawing_xml` adds `keepNext`/`keepLines` and the injector adds `pageBreakBefore` only when `cy > 5400000` after width-scaling. Word ignores `keepLines` for an image that is itself taller than the printable page area, and the validator (Sections F, I/J) checks only for the presence of `keepNext`/`keepLines`, never whether an oversized image actually needs `pageBreakBefore` (C4).

## Correctness Properties

Property 1: Bug Condition — Unique Media Content

_For any_ pipeline run where the bug condition holds via duplicate media content, the fixed pipeline SHALL produce a document in which every injected figure's media content (by MD5) appears exactly once, with no two distinct figures referencing duplicate image content, and validation SHALL fail when any duplicate MD5 is present.

**Validates: Requirements 2.1**

Property 2: Bug Condition — Exactly-One Caption and Media Resolution

_For any_ pipeline run where the bug condition holds via ambiguous or unresolved resolution, the fixed pipeline SHALL resolve each `post_com` manifest entry to exactly one caption paragraph and exactly one injected media file, and validation SHALL fail when any entry resolves to zero or multiple captions or media files.

**Validates: Requirements 2.2**

Property 3: Bug Condition — Packed Content Matches the Injected File

_For any_ pipeline run where the bug condition holds via content drift, the fixed pipeline SHALL ensure each figure's packed media bytes (`word/media/imageNN`) match the `images/<file>` that was injected by MD5, and validation SHALL fail on any content mismatch. The declared `source` is cross-checked best-effort (only when present on disk) and never fails the build on its own.

**Validates: Requirements 2.3**

Property 4: Bug Condition — Image and Caption Stay Together

_For any_ pipeline run where the bug condition holds via page-split risk, the fixed pipeline SHALL keep each image and its caption on the same page — via `keepNext`/`keepLines` on the drawing paragraph, `keepNext`/`keepLines` on the caption paragraph, and `pageBreakBefore` for images exceeding the height threshold — and validation SHALL fail if any figure can split across a page boundary.

**Validates: Requirements 2.4**

Property 5: Preservation — Non-Manifest Captions Unchanged

_For any_ input where the bug condition does NOT hold (a caption paragraph not referenced by any manifest entry), the fixed pipeline SHALL produce the same result as the original pipeline, preserving that paragraph and its surrounding content unchanged.

**Validates: Requirements 3.1**

Property 6: Preservation — SEQ Numbering Fields Unchanged

_For any_ input where the bug condition does NOT hold, the fixed pipeline SHALL produce the same result as the original, preserving `SEQ Gambar`/`SEQ Tabel` caption fields and figure/table numbering (including the first-caption `\r 1` restart switch).

**Validates: Requirements 3.2**

Property 7: Preservation — Aspect-Ratio Rendering Unchanged

_For any_ image within or scaled to the maximum width (≤ 5400000 EMU), where the page-split bug condition does NOT hold, the fixed pipeline SHALL produce the same result as the original, preserving aspect-ratio rendering.

**Validates: Requirements 3.3**

Property 8: Preservation — Front-Matter/TOC/Appendix Structure Unchanged

_For any_ input where the bug condition does NOT hold, the fixed pipeline SHALL produce the same result as the original, preserving the `taappendixheading` outline level, `TOC9` indentation, and Daftar Lampiran TOC field so existing structural validation continues to pass unchanged.

**Validates: Requirements 3.4**

## Fix Implementation

### Changes Required

Assuming the root cause analysis is correct, the fix touches two files. No change is made to the COM/pack steps, the manifest schema (beyond reading existing fields), or any non-figure handling.

**File**: `skills/scripts/inject_all_images.py`

**Function**: `inject_all_images(docx_path)` (and a small helper for hashing/height)

**Specific Changes**:
1. **Exactly-one caption resolution (C2)**: Replace the break-on-first-match loop with a pass that collects ALL paragraphs matching `pStyle == 'Caption'`, containing `caption_match`, and whose remainder matches `^(Gambar|Tabel)\s+[0-9\.]+$`. If the count is `!= 1`, raise an error and exit non-zero (no silent skip). Inject only when exactly one caption is found.
2. **Post-pack content integrity (C3)**: Record the MD5 of each `images/<file>` at injection time (keyed by the allocated `imageNN` name). The injector itself copies bytes verbatim; the authoritative integrity assertion is performed after the document is re-zipped (see validator), confirming `word/media/imageNN` still MD5-matches the injected `images/<file>`. If a `source` path is present and exists on disk, optionally log whether it matches, but never fail the run on a `source` mismatch or a missing `source`.
3. **Duplicate-content guard (C1)**: Track the MD5 of every media file injected during the run. If a new injection would introduce an MD5 already present for a different figure, fail the run (entries that legitimately reuse the same source, e.g. the two `modal-fasilitas-aset.png` mockups, are reconciled in the manifest/validator allow-list rather than silently producing duplicate media).
4. **Oversized-image page break (C4)**: Define an explicit page-height threshold (printable height in EMU). Apply `pageBreakBefore` when the scaled image height exceeds the threshold (not only the existing `cy > 5400000` width-derived check), while keeping `keepNext`/`keepLines` on both the drawing and caption paragraphs.
5. **No behavior change for correct entries**: Leave drawing XML generation, centering, width scaling (≤ 5400000 EMU with `noChangeAspect`), relationship/`rId` allocation, and the removal of a pre-existing preceding drawing exactly as today for entries that already satisfy the properties.

**File**: `skills/scripts/validate_docx_structure.py`

**Function**: `main()` (new check sections appended to the existing error-collection flow)

**Specific Changes**:
1. **Media MD5 uniqueness check (C1)**: Compute MD5 for every `word/media/*` referenced by an injected `w:drawing`; append an error for any MD5 shared by two distinct figures.
2. **Exactly-one resolution check (C2)**: For each `post_com` manifest entry, count matching caption paragraphs in `document.xml`; append an error when the count is not exactly 1.
3. **Content-integrity check (C3)**: For each `post_com` entry, compare the packed `word/media/imageNN` MD5 against the MD5 of the `images/<file>` that should have been injected; append an error on mismatch. When the declared `source` exists on disk, emit an informational note if it differs, but do not append an error for `source` mismatch or absence.
4. **Page-split safety check (C4)**: For each figure, append an error when an image taller than the threshold lacks `pageBreakBefore`, in addition to the existing `keepNext`/`keepLines` presence checks (Sections F and I/J).
5. **Preserve all existing checks**: Sections A–J remain unchanged and continue to run first; the new checks only add failures, never relax existing ones.

## Testing Strategy

### Validation Approach

The strategy follows two phases: first surface counterexamples that demonstrate each defect on the UNFIXED code, then verify the fix resolves them and preserves existing behavior. Because the artifacts are generated `.docx` packages, tests operate on a built document and its `word/media`, `word/document.xml`, and `word/_rels/document.xml.rels` entries.

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix, and confirm or refute the root-cause analysis. If refuted, re-hypothesize.

**Test Plan**: Build the document with the current pipeline (or use a captured output), then run probes that compute media MD5s, count caption matches per manifest entry, compare packed media bytes to the injected `images/<file>`, and inspect keep/`pageBreakBefore` flags on tall figures. Run these on the UNFIXED code to observe failures.

**Test Cases**:
1. **Duplicate-media probe (C1)**: Compute MD5 of every injected media file and assert all distinct figures are unique (will fail on unfixed code where `image18 == image35 == seq_auth`).
2. **Resolution-count probe (C2)**: For each `post_com` entry, assert exactly one matching caption paragraph; include a synthetic zero-match and a synthetic multi-match entry (will fail / silently skip on unfixed code).
3. **Content-integrity probe (C3)**: Assert `md5(packed word/media/imageNN) == md5(injected images/<file>)` for each entry (will fail for any figure recompressed/altered during packing).
4. **Page-split probe (C4)**: Inject a deliberately tall image and assert it carries `pageBreakBefore`; assert the image+caption pair cannot split (may fail on unfixed code for oversized images).

**Expected Counterexamples**:
- Two or more distinct figures sharing one MD5.
- A manifest entry resolving to 0 or ≥2 captions.
- Injected media MD5 ≠ the injected `images/<file>` MD5 (recompression/alteration during packing).
- A tall image lacking `pageBreakBefore`.
- Possible causes: no MD5 verification, first-match-with-silent-skip resolution, missing post-pack integrity check, height threshold not enforced.

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed pipeline produces the expected behavior (Properties 1–4).

**Pseudocode:**
```
FOR ALL run WHERE isBugCondition(run) DO
  result := buildPipeline_fixed(run)
  ASSERT allInjectedMediaUniqueByMd5(result)              // Property 1
  ASSERT forEachEntry_exactlyOneCaptionAndMedia(result)    // Property 2
  ASSERT forEachEntry_packedMediaMd5EqualsInjectedFileMd5(result)  // Property 3
  ASSERT noFigureCanSplitAcrossPage(result)                // Property 4
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed pipeline produces the same result as the original pipeline (Properties 5–8).

**Pseudocode:**
```
FOR ALL run WHERE NOT isBugCondition(run) DO
  ASSERT buildPipeline_original(run) == buildPipeline_fixed(run)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many caption/figure/document configurations automatically across the input domain.
- It catches edge cases that hand-written unit tests would miss.
- It provides strong guarantees that non-buggy inputs are byte-for-byte unchanged.

**Test Plan**: Observe behavior on UNFIXED code first for non-manifest captions, SEQ numbering, within-width images, and front-matter/TOC/appendix structure, then write property-based tests that capture that behavior and assert it is unchanged after the fix.

**Test Cases**:
1. **Non-manifest caption preservation (Property 5)**: Observe that a caption with no manifest entry is untouched on unfixed code, then assert it stays unchanged after the fix.
2. **SEQ numbering preservation (Property 6)**: Observe `SEQ Gambar`/`SEQ Tabel` fields and the first-caption `\r 1` restart on unfixed code, then assert they are preserved.
3. **Aspect-ratio preservation (Property 7)**: Observe that a within-width image keeps `noChangeAspect` and its scaled extent on unfixed code, then assert it is preserved.
4. **Structure preservation (Property 8)**: Observe `taappendixheading` outline level 8, `TOC9` `left='1'`, and the Daftar Lampiran `TOC \n 9-9` field pass on unfixed code, then assert they still pass.

### Unit Tests

- Caption resolution: exactly-one match injects; zero matches fails; multiple matches fails.
- MD5 content integrity: packed media matching the injected `images/<file>` passes; recompressed/altered bytes fail.
- Duplicate-media guard: a new injection with an already-seen MD5 fails (except reconciled reuse).
- Page break: image height above threshold receives `pageBreakBefore`; below threshold does not.
- Validator: each new check (uniqueness, resolution count, source match, page-split) raises on a crafted bad document and passes on a good one.

### Property-Based Tests

- Generate random sets of caption paragraphs and manifest entries; assert each entry resolves to exactly one caption or the run fails (Property 2).
- Generate random media byte sets; assert packed-vs-injected-file MD5 equality and global MD5 uniqueness hold or the run fails (Properties 1, 3).
- Generate random image heights around the threshold; assert `pageBreakBefore` presence iff height exceeds the threshold (Property 4).
- Generate documents containing non-manifest captions, SEQ fields, within-width images, and front-matter/TOC/appendix structures; assert the fixed output equals the original output (Properties 5–8).

### Integration Tests

- Full pipeline run end-to-end: build the document, then assert all four new validator checks pass and exit code is 0.
- Negative integration: seed a duplicate media file, a zero-match caption, a recompressed image, and an oversized image; assert the pipeline fails with a clear per-defect error message.
- Regression integration: run the existing validator Sections A–J on the fixed output and confirm they still pass unchanged.
