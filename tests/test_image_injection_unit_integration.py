"""Unit + integration tests for the image-injection pipeline fix (task 4).

Spec: .kiro/specs/image-injection-pipeline-fix

These SUPPORTING tests complement the property suites
(``test_image_injection_bug_conditions.py`` and
``test_image_injection_preservation.py``) by exercising the fix at two levels:

  * UNIT - the injector helpers exposed by
    ``skills/scripts/inject_all_images.py`` (``resolve_caption_indices``,
    ``md5_file``, ``load_reconcile``, ``_duplicate_pair_allowed``,
    ``scaled_dimensions``, ``printable_height_emu``, ``generate_drawing_xml``)
    and the injector's pre-pass guards run on tiny, purpose-built ``.docx``
    packages.
  * INTEGRATION - the full ``inject -> validate`` pipeline run end-to-end, a
    negative run that seeds all four defects (C1-C4) at once, and a regression
    run confirming the validator's structural Sections A-J still pass unchanged.

Conventions (docx build/mutate helpers, namespaces) follow
``test_image_injection_bug_conditions.py``. Per the task, the existing
exploration/preservation test files are NOT modified; this is a brand-new file.
All artifacts are created under ``tmp_path`` (or a copy of the captured doc /
manifest / reconcile file) so no real repo file is mutated.

Validates: Requirements 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import lxml.etree as LET
import pytest
from PIL import Image

# --------------------------------------------------------------------------- #
# Paths / import of the canonical injector module
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
CAPTURED_DOCX = ROOT / "Tugas_Akhir_Formatted.docx"
VALIDATOR = SCRIPTS / "validate_docx_structure.py"
MANIFEST = ROOT / "images" / "manifest.json"

# Import the canonical injector (skills/scripts, not the scratch copy).
sys.path.insert(0, str(SCRIPTS))
import inject_all_images as inj  # noqa: E402

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
REL_PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"w": W, "r": R, "a": A, "wp": WP}
WNS = {"w": W}

DOC = "word/document.xml"
RELS = "word/_rels/document.xml.rels"


# --------------------------------------------------------------------------- #
# Low-level docx helpers (replicated locally; existing test files untouched)
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


def rels_target_map(entries: dict) -> dict:
    root = LET.fromstring(entries[RELS])
    return {rel.get("Id"): rel.get("Target") for rel in root}


def referenced_media(entries: dict) -> list:
    """Ordered list of word/media/... files referenced by a w:drawing blip."""
    doc = parse_doc(entries)
    tmap = rels_target_map(entries)
    out = []
    for blip in doc.findall(".//a:blip", NS):
        target = tmap.get(blip.get(f"{{{R}}}embed"))
        if target:
            out.append("word/" + target)
    return out


def body_of(doc):
    return doc.find("w:body", NS)


def para_text(p) -> str:
    return "".join(t.text for t in p.iter(f"{{{W}}}t") if t.text).strip()


def para_style(p) -> str:
    pPr = p.find("w:pPr", NS)
    if pPr is None:
        return ""
    s = pPr.find("w:pStyle", NS)
    return s.get(f"{{{W}}}val") if s is not None else ""


def caption_match_count(doc, caption_match: str) -> int:
    """Replicate the injector/validator resolution rule for an entry."""
    count = 0
    for p in body_of(doc).findall("w:p", NS):
        if para_style(p) != "Caption":
            continue
        text = para_text(p)
        if caption_match in text:
            remainder = text.replace(caption_match, "").strip()
            if re.match(r"^(Gambar|Tabel)\s+[0-9\.]+$", remainder, re.IGNORECASE):
                count += 1
    return count


def survey_ids() -> list:
    """Manifest ids whose captions are absent from the captured doc (the C2 gap)."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return [it["id"] for it in manifest["images"] if it["id"].startswith("survey_")]


def run_validator(docx_path: Path, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(docx_path)],
        capture_output=True, text=True, cwd=str(cwd),
    )


# --------------------------------------------------------------------------- #
# Builders for tiny, injector-ready docx packages (no Sections A-J needed; the
# injector itself does not run the validator)
# --------------------------------------------------------------------------- #
def _make_png(path: Path, w: int = 24, h: int = 24, color=(200, 30, 30)) -> None:
    Image.new("RGB", (int(w), int(h)), color).save(str(path), "PNG")


def _caption_p_xml(text: str) -> str:
    return (
        '<w:p><w:pPr><w:pStyle w:val="Caption"/></w:pPr>'
        f'<w:r><w:t xml:space="preserve">{text}</w:t></w:r></w:p>'
    )


def _minimal_docx(path: Path, caption_texts, pg_h: int = 15840,
                  top: int = 1440, bottom: int = 1440) -> None:
    """Write a tiny injector-ready .docx with the given Caption paragraphs and a
    body sectPr (so printable_height_emu has real geometry to read)."""
    paras = "".join(_caption_p_xml(c) for c in caption_texts)
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W}"><w:body>{paras}'
        f'<w:sectPr><w:pgSz w:w="12240" w:h="{pg_h}"/>'
        f'<w:pgMar w:top="{top}" w:bottom="{bottom}" w:left="1440" w:right="1440"/>'
        '</w:sectPr></w:body></w:document>'
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<Relationships xmlns="{REL_PKG}">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
        'Target="styles.xml"/></Relationships>'
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="png" ContentType="image/png"/>'
        '<Default Extension="jpg" ContentType="image/jpeg"/>'
        '<Default Extension="rels" '
        'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.'
        'wordprocessingml.document.main+xml"/></Types>'
    )
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("word/document.xml", document)
        z.writestr(RELS, rels)
        # Ensure word/media/ exists after extractall (injector copies into it).
        z.writestr("word/media/placeholder.txt", b"placeholder")


def _setup_inject_project(tmp_path: Path, items, caption_texts, image_specs,
                          reconcile=None, pg_h: int = 15840):
    """Create an isolated injector project under tmp_path:
      tmp_path/images/manifest.json (+ optional manifest_reconcile.json)
      tmp_path/images/<file> for each requested image
      tmp_path/test.docx (minimal, with the given caption paragraphs)
    image_specs: dict filename -> (w, h, color) OR ("copyof", other_filename).
    Returns the docx Path.
    """
    images_dir = tmp_path / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    (images_dir / "manifest.json").write_text(
        json.dumps({"images": items}), encoding="utf-8")
    if reconcile is not None:
        (images_dir / "manifest_reconcile.json").write_text(
            json.dumps(reconcile), encoding="utf-8")
    for fname, spec in image_specs.items():
        dest = images_dir / fname
        if isinstance(spec, tuple) and spec and spec[0] == "copyof":
            shutil.copy2(images_dir / spec[1], dest)
        else:
            w, h, color = spec
            _make_png(dest, w, h, color)
    docx = tmp_path / "test.docx"
    _minimal_docx(docx, caption_texts, pg_h=pg_h)
    return docx


def _run_injector(tmp_path: Path, docx: Path, monkeypatch):
    """Run the real injector in-process with cwd set to the project root."""
    monkeypatch.chdir(tmp_path)
    inj.inject_all_images(str(docx))


# --------------------------------------------------------------------------- #
# Additional helpers for mutating the captured artifact + reconciled projects.
# (Built on the module-level helpers above; the exploration/preservation test
# files are NOT touched.)
# --------------------------------------------------------------------------- #
def _distinct_referenced_media(entries: dict) -> list:
    """Ordered, de-duplicated list of word/media/... referenced by a drawing."""
    out, seen = [], set()
    for m in referenced_media(entries):
        if m not in seen:
            seen.add(m)
            out.append(m)
    return out


def _make_duplicate_media(entries: dict, idx_a: int, idx_b: int):
    """Overwrite the media at idx_b with idx_a's bytes so two distinct
    drawing-referenced figures share one MD5 (the C1 defect)."""
    distinct = _distinct_referenced_media(entries)
    ia, ib = idx_a % len(distinct), idx_b % len(distinct)
    if ia == ib:
        ib = (ib + 1) % len(distinct)
    src, dst = distinct[ia], distinct[ib]
    mutated = dict(entries)
    mutated[dst] = mutated[src]
    return mutated, (src, dst)


def _edit_caption_descriptor(doc, find_text: str, new_descriptor: str):
    """Replace the trailing descriptive run of the caption containing find_text."""
    body = body_of(doc)
    for p in body.findall("w:p", NS):
        if para_style(p) == "Caption" and find_text in para_text(p):
            t_runs = [t for t in p.iter(f"{{{W}}}t") if t.text and find_text in t.text]
            if t_runs:
                t_runs[-1].text = t_runs[-1].text.replace(find_text, new_descriptor)
                return p
    raise AssertionError(f"caption containing {find_text!r} not found")


def _media_before_caption(entries: dict, caption_text: str):
    """Resolve the packed 'word/media/imageNN' referenced by the drawing
    immediately preceding the caption containing caption_text."""
    doc = parse_doc(entries)
    children = list(body_of(doc))
    tmap = rels_target_map(entries)
    for i, p in enumerate(children):
        if p.tag != f"{{{W}}}p" or para_style(p) != "Caption":
            continue
        if caption_text not in para_text(p):
            continue
        j = i - 1
        while j >= 0:
            prev = children[j]
            if prev.tag != f"{{{W}}}p":
                break
            if prev.find(".//w:drawing", NS) is not None:
                blip = prev.find(".//a:blip", NS)
                tgt = tmap.get(blip.get(f"{{{R}}}embed"))
                return "word/" + tgt if tgt else None
            if para_text(prev):
                break
            j -= 1
    return None


def _drawing_p_before_caption(doc, caption_text: str):
    """Return the drawing paragraph immediately preceding a caption (or None)."""
    children = list(body_of(doc))
    for i, p in enumerate(children):
        if p.tag != f"{{{W}}}p" or para_style(p) != "Caption":
            continue
        if caption_text not in para_text(p):
            continue
        j = i - 1
        while j >= 0:
            prev = children[j]
            if prev.tag != f"{{{W}}}p":
                break
            if prev.find(".//w:drawing", NS) is not None:
                return prev
            if para_text(prev):
                break
            j -= 1
    return None


def _make_tall_strip_pbb(p, target_cy: int):
    """Set a drawing paragraph's extents above the threshold and drop pageBreakBefore."""
    for ext in p.findall(".//wp:extent", NS):
        ext.set("cy", str(target_cy))
    for ext in p.findall(".//a:ext", NS):
        ext.set("cy", str(target_cy))
    pPr = p.find("w:pPr", NS)
    if pPr is not None:
        for pbb in pPr.findall("w:pageBreakBefore", NS):
            pPr.remove(pbb)


def _printable_height(doc) -> int:
    """Printable page height (EMU) from the body sectPr: (h - top - bottom)*635."""
    sect = doc.find("w:body/w:sectPr", NS)
    pgSz = sect.find("w:pgSz", NS)
    pgMar = sect.find("w:pgMar", NS)
    h = int(pgSz.get(f"{{{W}}}h"))
    top = int(pgMar.get(f"{{{W}}}top"))
    bottom = int(pgMar.get(f"{{{W}}}bottom"))
    return (h - top - bottom) * 635


def _pbb_before_caption(entries: dict, caption_text: str) -> bool:
    """True iff the drawing paragraph immediately preceding the caption carries
    w:pageBreakBefore (used to assert the C4 page-break decision after inject)."""
    doc = parse_doc(entries)
    children = list(body_of(doc))
    for i, p in enumerate(children):
        if p.tag == f"{{{W}}}p" and para_style(p) == "Caption" and caption_text in para_text(p):
            prev = children[i - 1]
            pPr = prev.find("w:pPr", NS)
            return pPr is not None and pPr.find("w:pageBreakBefore", NS) is not None
    raise AssertionError(f"caption containing {caption_text!r} not found")


def _body_from_captions(caption_texts):
    """Build an in-memory w:body element holding the given Caption paragraphs."""
    paras = "".join(_caption_p_xml(c) for c in caption_texts)
    doc = LET.fromstring(
        f'<w:document xmlns:w="{W}"><w:body>{paras}</w:body></w:document>'.encode("utf-8"))
    return doc.find("w:body", NS)


def _reconcile_with_surveys() -> dict:
    """Reconciliation allow-lists with the 7 survey_* ids in unresolved_allow so
    they do not add C2 noise to validator runs on the captured doc."""
    return {"duplicate_content_allow": [], "unresolved_allow": survey_ids()}


@pytest.fixture(scope="module")
def reconciled_project(tmp_path_factory):
    """An isolated project dir holding a copy of images/ (manifest + curated
    files), a reconcile file with the survey_* ids allow-listed, and a copy of
    the captured doc. No real repo file is mutated."""
    proj = tmp_path_factory.mktemp("reconciled_proj")
    shutil.copytree(ROOT / "images", proj / "images")
    (proj / "images" / "manifest_reconcile.json").write_text(
        json.dumps(_reconcile_with_surveys()), encoding="utf-8")
    shutil.copy2(CAPTURED_DOCX, proj / "captured.docx")
    return proj


# =========================================================================== #
# UNIT - caption resolution (Requirement 2.2)
# =========================================================================== #
def test_unit_resolve_caption_indices_zero_one_multiple():
    """inj.resolve_caption_indices returns ALL matching body indices: 0, 1, or
    many, per the pStyle=='Caption' + contains + remainder rule."""
    ns = {"w": W}
    match = "Diagram Arsitektur Sistem"

    # Zero matches: no caption mentions the target descriptor.
    body0 = _body_from_captions(["Gambar 2.1 Sesuatu Yang Lain",
                                 "Tabel 2.1 Bukan Gambar Itu"])
    assert inj.resolve_caption_indices(body0, match, ns) == []

    # Exactly one match.
    body1 = _body_from_captions(["Gambar 2.1 Pendahuluan",
                                 f"Gambar 2.2 {match}",
                                 "Tabel 2.1 Lain Lagi"])
    assert inj.resolve_caption_indices(body1, match, ns) == [1]

    # Multiple matches (two captions whose remainder is a valid Gambar number).
    body2 = _body_from_captions([f"Gambar 2.2 {match}",
                                 "Gambar 2.3 Tidak Cocok",
                                 f"Gambar 2.4 {match}"])
    assert inj.resolve_caption_indices(body2, match, ns) == [0, 2]


def test_unit_injector_caption_resolution_zero_one_multiple(tmp_path, monkeypatch):
    """The real injector aborts (SystemExit) on 0 and on 2 matches, and succeeds
    on exactly 1 match for the same entry."""
    match = "My Arsitektur Figure"
    items = [{"id": "fig_a", "file": "fig_a.png",
              "caption_match": match, "inject_method": "post_com"}]
    specs = {"fig_a.png": (40, 40, (10, 120, 200))}

    # Zero matches -> abort.
    p0 = tmp_path / "zero"
    docx0 = _setup_inject_project(p0, items, ["Gambar 2.1 Tidak Ada Yang Cocok"], specs)
    with pytest.raises(SystemExit):
        _run_injector(p0, docx0, monkeypatch)

    # Two matches -> abort.
    p2 = tmp_path / "multi"
    docx2 = _setup_inject_project(
        p2, items, [f"Gambar 2.1 {match}", f"Gambar 2.2 {match}"], specs)
    with pytest.raises(SystemExit):
        _run_injector(p2, docx2, monkeypatch)

    # Exactly one match -> succeeds (no SystemExit) and injects a drawing.
    p1 = tmp_path / "one"
    docx1 = _setup_inject_project(p1, items, [f"Gambar 2.1 {match}"], specs)
    _run_injector(p1, docx1, monkeypatch)
    out = read_all(docx1)
    assert len(referenced_media(out)) == 1, "exactly-one match should inject one drawing"


# =========================================================================== #
# UNIT - MD5 content integrity (Requirement 2.3)
# =========================================================================== #
def test_unit_md5_file_identical_and_altered(tmp_path):
    """inj.md5_file: identical bytes -> equal digest; altered bytes -> different."""
    a = tmp_path / "a.bin"
    b = tmp_path / "b.bin"
    payload = b"the-quick-brown-fox" * 32
    a.write_bytes(payload)
    b.write_bytes(payload)
    assert inj.md5_file(str(a)) == inj.md5_file(str(b))

    b.write_bytes(payload + b"\x00recompressed")
    assert inj.md5_file(str(a)) != inj.md5_file(str(b))


# =========================================================================== #
# UNIT - duplicate-media guard (Requirement 2.1)
# =========================================================================== #
def test_unit_duplicate_pair_allowed():
    """inj._duplicate_pair_allowed is true only when both ids share an allow group."""
    groups = [{"x", "y"}, {"p", "q", "r"}]
    assert inj._duplicate_pair_allowed("x", "y", groups)
    assert inj._duplicate_pair_allowed("p", "r", groups)
    assert not inj._duplicate_pair_allowed("x", "p", groups)
    assert not inj._duplicate_pair_allowed("x", "z", groups)


def test_unit_load_reconcile_bom_tolerant(tmp_path):
    """inj.load_reconcile reads a BOM-prefixed (utf-8-sig) reconcile file."""
    path = tmp_path / "manifest_reconcile.json"
    payload = {"duplicate_content_allow": [["a", "b"]], "unresolved_allow": ["c"]}
    path.write_text(json.dumps(payload), encoding="utf-8-sig")  # leading BOM
    groups, unresolved = inj.load_reconcile(str(path))
    assert {"a", "b"} in groups
    assert unresolved == {"c"}
    # Missing file -> empty allow-lists.
    groups2, unresolved2 = inj.load_reconcile(str(tmp_path / "nope.json"))
    assert groups2 == [] and unresolved2 == set()


def test_unit_duplicate_media_guard_blocks_then_reconciles(tmp_path, monkeypatch):
    """Two entries pointing to byte-identical images abort the run (C1); the same
    scenario reconciled via duplicate_content_allow succeeds."""
    items = [
        {"id": "dup_a", "file": "dup_a.png", "caption_match": "Alpha Figure",
         "inject_method": "post_com"},
        {"id": "dup_b", "file": "dup_b.png", "caption_match": "Beta Figure",
         "inject_method": "post_com"},
    ]
    captions = ["Gambar 4.1 Alpha Figure", "Gambar 4.2 Beta Figure"]
    specs = {"dup_a.png": (32, 32, (5, 60, 90)), "dup_b.png": ("copyof", "dup_a.png")}

    # No reconciliation -> the duplicate-content guard aborts.
    pblock = tmp_path / "blocked"
    docx_b = _setup_inject_project(pblock, items, captions, specs)
    with pytest.raises(SystemExit):
        _run_injector(pblock, docx_b, monkeypatch)

    # Reconciled via duplicate_content_allow -> succeeds.
    pok = tmp_path / "reconciled"
    reconcile = {"duplicate_content_allow": [["dup_a", "dup_b"]], "unresolved_allow": []}
    docx_ok = _setup_inject_project(pok, items, captions, specs, reconcile=reconcile)
    _run_injector(pok, docx_ok, monkeypatch)
    out = read_all(docx_ok)
    assert len(referenced_media(out)) == 2, "reconciled reuse should inject both figures"


# =========================================================================== #
# UNIT - page break (Requirement 2.4)
# =========================================================================== #
def test_unit_page_break_threshold(tmp_path, monkeypatch):
    """A tall image (rendered cy above the printable page-height threshold) gets
    w:pageBreakBefore on the drawing paragraph; a short image does not."""
    # Geometry chosen so the threshold (~2.99M EMU) is below MAX_WIDTH, isolating
    # the explicit page-height check from the width-derived cy > MAX_WIDTH branch.
    pg_h = 7604  # (7604 - 2880) * 635 = 2_999_740 EMU
    items = [
        {"id": "tall_fig", "file": "tall.png", "caption_match": "Tall Figure",
         "inject_method": "post_com", "cx": 2_000_000, "cy": 4_000_000},
        {"id": "short_fig", "file": "short.png", "caption_match": "Short Figure",
         "inject_method": "post_com", "cx": 2_000_000, "cy": 2_000_000},
    ]
    captions = ["Gambar 5.1 Tall Figure", "Gambar 5.2 Short Figure"]
    specs = {"tall.png": (30, 30, (200, 10, 10)), "short.png": (30, 30, (10, 200, 10))}

    proj = tmp_path / "pb"
    docx = _setup_inject_project(proj, items, captions, specs, pg_h=pg_h)
    _run_injector(proj, docx, monkeypatch)

    out = read_all(docx)
    threshold = _printable_height(parse_doc(out))
    assert threshold < inj.MAX_WIDTH  # sanity: page-height check is the deciding factor
    assert _pbb_before_caption(out, "Tall Figure"), (
        f"tall image (cy 4,000,000 > threshold {threshold}) should get pageBreakBefore")
    assert not _pbb_before_caption(out, "Short Figure"), (
        f"short image (cy 2,000,000 <= threshold {threshold}) should NOT get pageBreakBefore")


# =========================================================================== #
# VALIDATOR unit tests - each new content check rejects a crafted bad doc and a
# good doc passes (Requirements 2.1-2.4). Run in a reconciled project so the 7
# survey_* entries do not add C2 noise.
# =========================================================================== #
def _combined(result) -> str:
    return (result.stdout or "") + "\n" + (result.stderr or "")


def test_validator_good_doc_passes(reconciled_project):
    """The reconciled captured doc passes the validator (exit 0) and the four new
    content-level check headers/notes are emitted."""
    res = run_validator(reconciled_project / "captured.docx", reconciled_project)
    out = _combined(res)
    assert res.returncode == 0, f"good doc should pass:\n{out[-1500:]}"
    assert "C1 uniqueness, C2 resolution, C3 integrity, C4 page-split" in out
    assert "media MD5 uniqueness" in out
    assert "page-split safety" in out


def test_validator_c1_duplicate_media_rejected(reconciled_project):
    """C1: two distinct drawing-referenced media sharing one MD5 are rejected."""
    entries = read_all(reconciled_project / "captured.docx")
    mutated, (src, dst) = _make_duplicate_media(entries, 5, 12)
    out_docx = reconciled_project / "c1.docx"
    write_all(mutated, out_docx)
    res = run_validator(out_docx, reconciled_project)
    combined = _combined(res)
    assert res.returncode != 0, f"C1 duplicate ({src}->{dst}) should fail:\n{combined[-1200:]}"
    assert "[C1]" in combined, f"expected [C1] defect reported:\n{combined[-1200:]}"


def test_validator_c2_wrong_resolution_count_rejected(reconciled_project):
    """C2: an entry that no longer resolves to exactly one caption is rejected."""
    entries = read_all(reconciled_project / "captured.docx")
    doc = parse_doc(entries)
    target = "Entity-Relationship Diagram"  # manifest entry diagram_erd
    assert caption_match_count(doc, target) == 1
    _edit_caption_descriptor(doc, target, "Bagan Yang Sudah Tidak Cocok")
    assert caption_match_count(doc, target) == 0
    entries[DOC] = serialize_doc(doc)
    out_docx = reconciled_project / "c2.docx"
    write_all(entries, out_docx)
    res = run_validator(out_docx, reconciled_project)
    combined = _combined(res)
    assert res.returncode != 0, f"C2 zero-match should fail:\n{combined[-1200:]}"
    assert "[C2]" in combined, f"expected [C2] defect reported:\n{combined[-1200:]}"


def test_validator_c3_content_mismatch_rejected(reconciled_project):
    """C3: a packed media whose bytes no longer match its injected images/<file>
    (simulated recompression) is rejected."""
    entries = read_all(reconciled_project / "captured.docx")
    victim = _media_before_caption(entries, "Entity-Relationship Diagram")
    assert victim is not None, "expected a packed media preceding the ERD caption"
    original = _md5_bytes(entries[victim])
    entries[victim] = entries[victim] + b"\x00recompressed-drift"
    assert _md5_bytes(entries[victim]) != original
    out_docx = reconciled_project / "c3.docx"
    write_all(entries, out_docx)
    res = run_validator(out_docx, reconciled_project)
    combined = _combined(res)
    assert res.returncode != 0, f"C3 content drift should fail:\n{combined[-1200:]}"
    assert "[C3]" in combined, f"expected [C3] defect reported:\n{combined[-1200:]}"


def test_validator_c4_oversized_without_pagebreak_rejected(reconciled_project):
    """C4: an image taller than the printable page height that lacks
    pageBreakBefore is rejected."""
    entries = read_all(reconciled_project / "captured.docx")
    doc = parse_doc(entries)
    threshold = _printable_height(doc)
    p = _drawing_p_before_caption(doc, "Sequence Diagram: Autentikasi Administrator")
    assert p is not None, "expected a drawing before the autentikasi sequence caption"
    _make_tall_strip_pbb(p, threshold + 2_000_000)
    entries[DOC] = serialize_doc(doc)
    out_docx = reconciled_project / "c4.docx"
    write_all(entries, out_docx)
    res = run_validator(out_docx, reconciled_project)
    combined = _combined(res)
    assert res.returncode != 0, f"C4 oversized-without-pageBreak should fail:\n{combined[-1200:]}"
    assert "[C4]" in combined, f"expected [C4] defect reported:\n{combined[-1200:]}"


# =========================================================================== #
# INTEGRATION - happy path: inject -> validate, both exit 0 (Req 2.1-2.4)
# =========================================================================== #
def test_integration_happy_path(reconciled_project, monkeypatch):
    """End-to-end: run the real injector then the validator on a reconciled
    project; both succeed and the four new validator checks are exercised."""
    target = reconciled_project / "happy.docx"
    shutil.copy2(reconciled_project / "captured.docx", target)

    monkeypatch.chdir(reconciled_project)
    inj.inject_all_images(str(target))  # exits non-zero on any content defect

    res = run_validator(target, reconciled_project)
    out = _combined(res)
    assert res.returncode == 0, f"validate after inject should pass:\n{out[-1500:]}"
    # The four new content-level checks ran (headers/notes present).
    assert "C1 uniqueness, C2 resolution, C3 integrity, C4 page-split" in out
    assert "media MD5 uniqueness" in out
    assert "page-split safety" in out
    assert "VALIDATION SUCCESSFUL" in out


# =========================================================================== #
# INTEGRATION - negative: seed all four defects -> [C1][C2][C3][C4] reported
# =========================================================================== #
def test_integration_negative_all_four_defects(reconciled_project):
    """Seed a duplicate media (C1), a zero-match caption (C2), a recompressed
    image (C3) and an oversized image (C4) at once; the pipeline fails and every
    defect is reported."""
    entries = read_all(reconciled_project / "captured.docx")

    # Document-level defects: C2 (zero match) + C4 (tall, no pageBreakBefore).
    doc = parse_doc(entries)
    _edit_caption_descriptor(doc, "Entity-Relationship Diagram", "Bagan Rusak Tak Cocok")
    threshold = _printable_height(doc)
    tall_p = _drawing_p_before_caption(doc, "Sequence Diagram: Autentikasi Administrator")
    assert tall_p is not None
    _make_tall_strip_pbb(tall_p, threshold + 2_500_000)
    entries[DOC] = serialize_doc(doc)

    # Media-level defects: C1 (duplicate) + C3 (content drift on a third figure).
    entries, (src, dst) = _make_duplicate_media(entries, 5, 12)
    victim = _media_before_caption(entries, "Sequence Diagram: Sinkronisasi Data Gedung dan Unity")
    assert victim is not None and victim not in (src, dst)
    entries[victim] = entries[victim] + b"\x00drift-bytes"

    out_docx = reconciled_project / "negative.docx"
    write_all(entries, out_docx)
    res = run_validator(out_docx, reconciled_project)
    combined = _combined(res)
    assert res.returncode != 0, f"pipeline should fail with seeded defects:\n{combined[-1800:]}"
    for tag in ("[C1]", "[C2]", "[C3]", "[C4]"):
        assert tag in combined, f"expected {tag} reported:\n{combined[-1800:]}"


# =========================================================================== #
# INTEGRATION - regression: structural Sections A-J still pass (Req 3.1-3.4)
# =========================================================================== #
def test_integration_regression_structural_sections_preserved(reconciled_project, monkeypatch):
    """On a reconciled copy of the fixed captured doc output, the validator's
    structural Sections A-J still pass unchanged (exit 0, success markers present)."""
    target = reconciled_project / "regression.docx"
    shutil.copy2(reconciled_project / "captured.docx", target)

    monkeypatch.chdir(reconciled_project)
    inj.inject_all_images(str(target))

    res = run_validator(target, reconciled_project)
    out = _combined(res)
    assert res.returncode == 0, f"fixed output should pass structural checks:\n{out[-1500:]}"
    assert "taappendixheading style is correctly defined with outline level 8" in out
    assert "TOC9 style is correctly defined" in out
    assert "Found Daftar Lampiran TOC field" in out
    # No structural/Section A-J error lines (the reconciled doc has none).
    error_lines = [ln.strip() for ln in out.splitlines() if ln.strip().startswith("- ")]
    assert not error_lines, "structural Sections A-J regressed:\n" + "\n".join(error_lines)
