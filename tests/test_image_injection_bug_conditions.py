"""Bug-condition exploration tests for the image-injection pipeline (defects C1-C4).

Spec: .kiro/specs/image-injection-pipeline-fix

These tests encode the EXPECTED post-fix behavior described by the design's
``isBugCondition(run)`` specification and Correctness Properties 1-4: for any
run whose document exhibits a content-level figure defect, the canonical
validator (``skills/scripts/validate_docx_structure.py``) MUST reject it
(exit non-zero) and name the defect.

CRITICAL (exploration phase): On the UNFIXED code the validator performs NO
content-level checks, so it ACCEPTS every bug-condition document. Therefore
EVERY test in this module is EXPECTED TO FAIL right now -- the failure is the
proof that each defect exists and is undetected. Do NOT "fix" the tests or the
code at this stage. The very same tests are re-run after the fix (task 3.3),
at which point they must PASS.

Defect map (observed on the captured artifact ``Tugas_Akhir_Formatted.docx``):
  * C1 Duplicate media content   - no natural instance in the captured doc;
                                    demonstrated by making two distinct
                                    drawing-referenced media share one MD5.
  * C2 Ambiguous/zero resolution - NATURAL counterexample: 7 ``post_com``
                                    entries (survey_01..survey_07) resolve to
                                    ZERO caption paragraphs and are silently
                                    skipped. Plus synthetic zero-match and
                                    multi-match mutations.
  * C3 Packed-vs-injected drift   - no natural instance (python packing is
                                    lossless); demonstrated by corrupting a
                                    packed ``word/media/imageNN`` so it no
                                    longer matches its injected ``images/<file>``.
  * C4 Image/caption page split   - no natural instance (all tall figures
                                    already carry ``pageBreakBefore``);
                                    demonstrated with an image taller than the
                                    printable page height that lacks
                                    ``pageBreakBefore``.

Validates: Requirements 1.1, 1.2, 1.3, 1.4 (and Correctness Properties 1-4).
"""
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import lxml.etree as LET
import pytest
from hypothesis import HealthCheck, Phase, given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Paths / namespaces
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
CAPTURED_DOCX = ROOT / "Tugas_Akhir_Formatted.docx"
VALIDATOR = ROOT / "skills" / "scripts" / "validate_docx_structure.py"
MANIFEST = ROOT / "images" / "manifest.json"
IMAGES_DIR = ROOT / "images"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
REL_PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"w": W, "r": R, "a": A, "wp": WP}

DOC = "word/document.xml"
RELS = "word/_rels/document.xml.rels"


# --------------------------------------------------------------------------- #
# Low-level docx helpers
# --------------------------------------------------------------------------- #
def _md5_bytes(b: bytes) -> str:
    return hashlib.md5(b).hexdigest()


def read_all(path: Path) -> dict:
    with zipfile.ZipFile(path) as z:
        return {n: z.read(n) for n in z.namelist()}


def write_all(entries: dict, out_path: Path) -> None:
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name, data in entries.items():
            z.writestr(name, data)


def parse_doc(entries: dict):
    return LET.fromstring(entries[DOC])


def serialize_doc(root) -> bytes:
    return LET.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def run_validator(docx_path: Path) -> subprocess.CompletedProcess:
    """Run the canonical validator against ``docx_path`` from the repo root."""
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(docx_path)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )


def rels_target_map(entries: dict) -> dict:
    root = LET.fromstring(entries[RELS])
    return {rel.get("Id"): rel.get("Target") for rel in root}


def referenced_media(entries: dict) -> list:
    """Ordered list of ``word/media/...`` files referenced by a w:drawing blip."""
    doc = parse_doc(entries)
    tmap = rels_target_map(entries)
    out = []
    for blip in doc.findall(".//a:blip", NS):
        embed = blip.get(f"{{{R}}}embed")
        target = tmap.get(embed)
        if target:
            out.append("word/" + target)
    return out


def caption_paragraphs(doc):
    body = doc.find("w:body", NS)
    return body.findall("w:p", NS)


def para_text(p) -> str:
    return "".join(t.text for t in p.iter(f"{{{W}}}t") if t.text).strip()


def para_style(p) -> str:
    pPr = p.find("w:pPr", NS)
    if pPr is None:
        return ""
    pStyle = pPr.find("w:pStyle", NS)
    return pStyle.get(f"{{{W}}}val") if pStyle is not None else ""


def caption_match_count(doc, caption_match: str) -> int:
    """Replicates the injector/validator resolution rule for an entry."""
    count = 0
    for p in caption_paragraphs(doc):
        if para_style(p) != "Caption":
            continue
        text = para_text(p)
        if caption_match in text:
            remainder = text.replace(caption_match, "").strip()
            if re.match(r"^(Gambar|Tabel)\s+[0-9\.]+$", remainder, re.IGNORECASE):
                count += 1
    return count


def printable_height_emu(doc) -> int:
    """Printable page height (EMU) from the body sectPr: (h - top - bottom) twips * 635."""
    sect = doc.find("w:body/w:sectPr", NS)
    pgSz = sect.find("w:pgSz", NS)
    pgMar = sect.find("w:pgMar", NS)
    h = int(pgSz.get(f"{{{W}}}h"))
    top = int(pgMar.get(f"{{{W}}}top"))
    bottom = int(pgMar.get(f"{{{W}}}bottom"))
    return (h - top - bottom) * 635


def injected_file_md5s() -> set:
    """MD5 set of every existing ``images/<file>`` for post_com manifest entries."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    md5s = set()
    for item in manifest["images"]:
        if item.get("inject_method") != "post_com":
            continue
        p = IMAGES_DIR / item["file"]
        if p.exists():
            md5s.add(_md5_bytes(p.read_bytes()))
    return md5s


# --------------------------------------------------------------------------- #
# Defect-specific keyword expectations (the fixed validator should mention these)
# --------------------------------------------------------------------------- #
C1_KEYWORDS = re.compile(r"duplicate|identical|same\s+md5|shared\s+md5|uniqu", re.I)
C2_KEYWORDS = re.compile(r"resolv|caption.*count|exactly\s+one|zero\s+match|multiple|ambiguou|not\s+exactly", re.I)
C3_KEYWORDS = re.compile(r"content|integrity|mismatch|recompress|does not match|md5", re.I)
C4_KEYWORDS = re.compile(r"page\s*break|pagebreakbefore|split|too\s+tall|height|oversiz", re.I)


def assert_rejected(result, keyword_re, defect, detail):
    combined = (result.stdout or "") + "\n" + (result.stderr or "")
    assert result.returncode != 0, (
        f"[{defect}] EXPECTED the validator to REJECT the bug-condition document "
        f"(exit != 0) but it returned exit 0.\n"
        f"This is the bug: the current pipeline does not detect {defect}.\n"
        f"Counterexample: {detail}\n"
        f"--- validator output (tail) ---\n{combined[-1500:]}"
    )
    assert keyword_re.search(combined), (
        f"[{defect}] validator failed but did not report the {defect} defect.\n"
        f"Counterexample: {detail}\n"
        f"--- validator output (tail) ---\n{combined[-1500:]}"
    )


# --------------------------------------------------------------------------- #
# Sanity: captured artifact + harness are present and the base round-trips clean
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="module")
def base_entries():
    assert CAPTURED_DOCX.exists(), f"missing captured docx: {CAPTURED_DOCX}"
    assert VALIDATOR.exists(), f"missing validator: {VALIDATOR}"
    return read_all(CAPTURED_DOCX)


# Cached base entries for property-based tests (kept out of the @given signature
# so Hypothesis does not build an enormous repr of the whole docx on failure).
_BASE_CACHE = {}


def _base():
    if "entries" not in _BASE_CACHE:
        _BASE_CACHE["entries"] = read_all(CAPTURED_DOCX)
    return _BASE_CACHE["entries"]


# Exploration PBT: these are EXPECTED to fail on unfixed code, so skip the
# (wasteful) shrinking phase and keep the example count small for speed.
EXPLORE_PBT = settings(
    max_examples=4,
    deadline=None,
    phases=[Phase.explicit, Phase.reuse, Phase.generate],
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)


# =========================================================================== #
# C1 - Duplicate media content (Property 1 / Requirement 1.1, 2.1)
# =========================================================================== #
def _make_duplicate_media(entries: dict, idx_a: int, idx_b: int):
    """Force the media referenced by drawing idx_b to share idx_a's bytes."""
    refs = referenced_media(entries)
    distinct = []
    seen = set()
    for m in refs:
        if m not in seen:
            seen.add(m)
            distinct.append(m)
    ia, ib = idx_a % len(distinct), idx_b % len(distinct)
    if ia == ib:
        ib = (ib + 1) % len(distinct)
    src, dst = distinct[ia], distinct[ib]
    mutated = dict(entries)
    mutated[dst] = mutated[src]  # byte-identical -> duplicate MD5 across two figures
    detail = (
        f"media '{dst}' overwritten with '{src}' -> both share MD5 "
        f"{_md5_bytes(mutated[src])} (two distinct figures, identical content)"
    )
    return mutated, detail


def test_c1_duplicate_media_is_detected(base_entries, tmp_path):
    """C1: two distinct drawing-referenced media sharing one MD5 must be rejected."""
    mutated, detail = _make_duplicate_media(base_entries, 5, 12)
    out = tmp_path / "c1_duplicate.docx"
    write_all(mutated, out)
    assert_rejected(run_validator(out), C1_KEYWORDS, "C1 (duplicate media)", detail)


@settings(EXPLORE_PBT)
@given(pair=st.tuples(st.integers(0, 26), st.integers(0, 26)))
def test_c1_duplicate_media_is_detected_scoped(tmp_path, pair):
    """Scoped PBT: for any chosen pair of referenced media made identical,
    the validator must reject the resulting duplicate-content document."""
    mutated, detail = _make_duplicate_media(_base(), pair[0], pair[1])
    out = tmp_path / "c1_duplicate_pbt.docx"
    write_all(mutated, out)
    assert_rejected(run_validator(out), C1_KEYWORDS, "C1 (duplicate media)", detail)


# =========================================================================== #
# C2 - Ambiguous / unresolved caption resolution (Property 2 / Req 1.2, 2.2)
# =========================================================================== #
def test_c2_natural_zero_match_entries_are_detected(base_entries, tmp_path):
    """C2 (zero-match): a manifest entry that resolves to ZERO caption
    paragraphs must be rejected.

    Re-baselined to the now-correct captured document: the previously-natural
    counterexample (7 ``survey_*`` ``post_com`` entries resolving to zero
    captions) NO LONGER EXISTS -- the regenerated ``Tugas_Akhir_Formatted.docx``
    carries proper ``Gambar 2.x Hasil Kuesioner...`` captions, so every survey
    entry now resolves and the validator legitimately ACCEPTS the captured doc
    (exit 0). The C2 detection property is therefore demonstrated the same way
    the sibling synthetic tests do: craft a document where a known, currently
    resolvable manifest entry is broken so it resolves to 0 captions, then
    assert the validator REJECTS it (exit != 0) and names the C2 defect.

    Uses a DISTINCT entry (``diagram_arsitektur``) from the sibling
    ``test_c2_synthetic_zero_match_is_detected`` (``diagram_erd``)."""
    entries = dict(base_entries)
    doc = parse_doc(entries)
    target = "Diagram Arsitektur Sistem"  # manifest entry: diagram_arsitektur
    assert caption_match_count(doc, target) == 1, (
        "precondition: entry diagram_arsitektur must resolve to exactly 1 caption "
        "in the captured baseline document"
    )
    _edit_caption_descriptor(doc, target, "Bagan Yang Sudah Tidak Cocok")
    assert caption_match_count(doc, target) == 0
    entries[DOC] = serialize_doc(doc)
    out = tmp_path / "c2_natural_zero.docx"
    write_all(entries, out)
    detail = (
        f"entry diagram_arsitektur caption_match '{target}' now resolves to "
        f"0 captions (a manifest entry silently skipped)"
    )
    assert_rejected(run_validator(out), C2_KEYWORDS, "C2 (zero-match)", detail)


def _edit_caption_descriptor(doc, find_text: str, new_descriptor: str):
    """Replace the trailing descriptive w:t run of the caption containing find_text."""
    for p in caption_paragraphs(doc):
        if para_style(p) == "Caption" and find_text in para_text(p):
            t_runs = [t for t in p.iter(f"{{{W}}}t") if t.text and find_text in t.text]
            if t_runs:
                t_runs[-1].text = t_runs[-1].text.replace(find_text, new_descriptor)
                return p
    raise AssertionError(f"caption containing '{find_text}' not found")


def test_c2_synthetic_zero_match_is_detected(base_entries, tmp_path):
    """C2 (synthetic zero-match): break a resolvable caption so its manifest
    entry resolves to 0; the validator must reject the document."""
    entries = dict(base_entries)
    doc = parse_doc(entries)
    target = "Entity-Relationship Diagram"  # manifest entry: diagram_erd
    assert caption_match_count(doc, target) == 1
    _edit_caption_descriptor(doc, target, "Bagan Yang Sudah Tidak Cocok")
    assert caption_match_count(doc, target) == 0
    entries[DOC] = serialize_doc(doc)
    out = tmp_path / "c2_zero.docx"
    write_all(entries, out)
    detail = f"entry diagram_erd caption_match '{target}' now resolves to 0 captions"
    assert_rejected(run_validator(out), C2_KEYWORDS, "C2 (synthetic zero-match)", detail)


def test_c2_synthetic_multi_match_is_detected(base_entries, tmp_path):
    """C2 (synthetic multi-match): make a second caption also match an entry's
    caption_match so it resolves to 2; the validator must reject the document."""
    entries = dict(base_entries)
    doc = parse_doc(entries)
    target = "Entity-Relationship Diagram"  # manifest entry: diagram_erd
    assert caption_match_count(doc, target) == 1
    # Repurpose a different existing Gambar caption to also read as the target.
    _edit_caption_descriptor(doc, "Tampilan UI Database Sync Checker di Unity Editor", target)
    assert caption_match_count(doc, target) == 2
    entries[DOC] = serialize_doc(doc)
    out = tmp_path / "c2_multi.docx"
    write_all(entries, out)
    detail = f"entry diagram_erd caption_match '{target}' now resolves to 2 captions"
    assert_rejected(run_validator(out), C2_KEYWORDS, "C2 (synthetic multi-match)", detail)


# =========================================================================== #
# C3 - Packed media bytes differ from injected images/<file> (Property 3 / Req 1.3, 2.3)
# =========================================================================== #
def test_c3_content_drift_is_detected(base_entries, tmp_path):
    """C3: a packed ``word/media/imageNN`` whose bytes no longer match the
    injected ``images/<file>`` (simulated recompression) must be rejected."""
    refs = referenced_media(base_entries)
    inj_md5 = injected_file_md5s()
    # Pick a referenced media that corresponds to a real injected figure.
    figure_media = [m for m in refs if _md5_bytes(base_entries[m]) in inj_md5]
    assert figure_media, "expected at least one packed figure matching an injected file"
    victim = figure_media[0]
    mutated = dict(base_entries)
    original_md5 = _md5_bytes(mutated[victim])
    mutated[victim] = mutated[victim] + b"\x00recompressed"  # alter the packed bytes
    out = tmp_path / "c3_drift.docx"
    write_all(mutated, out)
    detail = (
        f"packed '{victim}' md5 changed {original_md5} -> {_md5_bytes(mutated[victim])}; "
        f"no longer matches its injected images/<file>"
    )
    assert_rejected(run_validator(out), C3_KEYWORDS, "C3 (content drift)", detail)


# =========================================================================== #
# C4 - Image/caption page-split safety (Property 4 / Req 1.4, 2.4)
# =========================================================================== #
def _make_tall_image_without_pagebreak(entries: dict, target_cy: int):
    """Set the first drawing's height above the page and strip pageBreakBefore."""
    doc = parse_doc(entries)
    drawing_p = None
    for p in caption_paragraphs(doc):
        if p.find(".//w:drawing", NS) is not None:
            drawing_p = p
            break
    assert drawing_p is not None, "no drawing paragraph found"

    for ext in drawing_p.findall(".//wp:extent", NS):
        ext.set("cy", str(target_cy))
    for ext in drawing_p.findall(".//a:ext", NS):
        ext.set("cy", str(target_cy))

    pPr = drawing_p.find("w:pPr", NS)
    if pPr is not None:
        for pbb in pPr.findall("w:pageBreakBefore", NS):
            pPr.remove(pbb)
    has_pbb = pPr is not None and pPr.find("w:pageBreakBefore", NS) is not None
    assert not has_pbb

    mutated = dict(entries)
    mutated[DOC] = serialize_doc(doc)
    return mutated, printable_height_emu(doc)


def test_c4_tall_image_without_pagebreak_is_detected(base_entries, tmp_path):
    """C4: an image taller than the printable page height that lacks
    ``pageBreakBefore`` must be rejected (it can split across a page)."""
    doc = parse_doc(base_entries)
    threshold = printable_height_emu(doc)
    target_cy = threshold + 1_500_000
    mutated, _ = _make_tall_image_without_pagebreak(base_entries, target_cy)
    out = tmp_path / "c4_split.docx"
    write_all(mutated, out)
    detail = (
        f"drawing height cy={target_cy} EMU exceeds printable page height "
        f"{threshold} EMU but has no pageBreakBefore"
    )
    assert_rejected(run_validator(out), C4_KEYWORDS, "C4 (page split)", detail)


@settings(EXPLORE_PBT)
@given(over=st.integers(min_value=200_000, max_value=6_000_000))
def test_c4_tall_image_without_pagebreak_is_detected_scoped(tmp_path, over):
    """Scoped PBT: for any height above the printable page threshold and no
    pageBreakBefore, the validator must reject the splittable figure."""
    entries = _base()
    doc = parse_doc(entries)
    threshold = printable_height_emu(doc)
    target_cy = threshold + over
    mutated, _ = _make_tall_image_without_pagebreak(entries, target_cy)
    out = tmp_path / "c4_split_pbt.docx"
    write_all(mutated, out)
    detail = f"drawing height cy={target_cy} EMU > printable {threshold} EMU, no pageBreakBefore"
    assert_rejected(run_validator(out), C4_KEYWORDS, "C4 (page split)", detail)
