# Bugfix Requirements Document

## Introduction

The document automation pipeline (`skills/scripts/build_pipeline.py`) generates a formatted Word thesis from a Markdown draft. After the Word COM field-update and packing step, all figures are injected by a single manifest-driven, post-COM injector (`skills/scripts/inject_all_images.py`) reading `images/manifest.json` (32 entries, each keyed by `caption_match` + `source` + `inject_method: post_com`). Structure is then validated by `scratch/validate_docx_structure.py`.

Three related defects affect the figures in the generated document:

1. **Image duplication** — Word COM renumbers/strips custom-injected images, causing distinct figures (notably sequence diagrams) to share identical media content under different names (e.g., `image18 == image35 == seq_auth`).
2. **Incorrect figure resolution / content drift** — A manifest entry can resolve to the wrong number of caption paragraphs (zero or many), and an injected image's bytes can differ from its declared source (e.g., Word lossy recompression: `header+gedung-view.png` 201KB vs `image22` 189KB in output). Neither condition is currently detected by validation.
3. **Image/caption page splits** — Very large or tall images can split from their caption (or split the image itself) across a page boundary because Word ignores `keepNext` for oversized images.

The fix focuses on verifying correctness and hardening the consolidated manifest-driven approach so that, for any pipeline run, every manifest entry resolves to exactly one caption and exactly one media file, each injected image's content matches its source, no media content is duplicated, and no image+caption pair can split across pages.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN the Word COM field-update step processes a document that contains custom-injected images THEN the system renumbers/strips those images so that distinct figures end up referencing duplicate media content (e.g., `image18`, `image35`, and `seq_auth` resolve to identical bytes).

1.2 WHEN a manifest entry's `caption_match` matches zero caption paragraphs or more than one caption paragraph in the generated document THEN the system injects the image at the wrong location or skips it, and validation does not flag the unresolved/ambiguous entry.

1.3 WHEN an injected image's media bytes differ from its declared `source` file (for example due to Word's lossy recompression) THEN the system emits a figure whose content does not match the intended source, and validation does not detect the mismatch.

1.4 WHEN an image and its caption are placed near a page boundary and the image is very large or tall THEN the system splits the image from its caption, or splits the image itself, across pages because `keepNext`/`keepLines` alone is ignored for oversized images.

### Expected Behavior (Correct)

2.1 WHEN image injection completes for a pipeline run THEN the system SHALL ensure each injected figure's media content (by MD5) appears exactly once, with no two distinct figures referencing duplicate image content.

2.2 WHEN each manifest entry is processed THEN the system SHALL resolve it to exactly one caption paragraph and exactly one injected media file, and validation SHALL fail when any entry resolves to zero or multiple captions or media files.

2.3 WHEN an image is injected THEN the system SHALL ensure the injected media bytes match the declared `source` file by MD5, and validation SHALL fail on any content mismatch.

2.4 WHEN an image and its caption are placed THEN the system SHALL keep the image and its caption together on the same page (via `keepNext`/`keepLines` on the drawing paragraph, `keepNext`/`keepLines` on the caption paragraph, and `pageBreakBefore` for images exceeding the height threshold), and validation SHALL fail if any figure can split across a page boundary.

### Unchanged Behavior (Regression Prevention)

3.1 WHEN a caption paragraph is not referenced by any manifest entry THEN the system SHALL CONTINUE TO leave that paragraph and its surrounding content unchanged.

3.2 WHEN the document contains `SEQ Gambar`/`SEQ Tabel` caption fields and figure numbering THEN the system SHALL CONTINUE TO preserve them after image injection.

3.3 WHEN an image is within or scaled to the maximum width (≤ 5400000 EMU) THEN the system SHALL CONTINUE TO render it with its aspect ratio preserved.

3.4 WHEN the front-matter, table-of-contents, and appendix structures (e.g., `taappendixheading` outline level, `TOC9` indentation, Daftar Lampiran TOC field) exist THEN the system SHALL CONTINUE TO pass the existing structural validation checks unchanged.
