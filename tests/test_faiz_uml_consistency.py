"""Guards for the active UML/architecture diagrams in the Faiz report."""

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
DIAGRAMS = ROOT / "diagrams"
IMAGES = ROOT / "images"

ACTIVE = {
    "diagram_tahap_pengembangan": "gambar-2.10-tahap-pengembangan",
    "diagram_arsitektur": "gambar-2.09-arsitektur-sistem",
    "diagram_use_case": "gambar-2.12-use-case-diagram",
    "diagram_activity_integrasi": "gambar-2.14-activity-integrasi-data-denah",
    "diagram_sequence_sinkronisasi": "gambar-2.16-sequence-sinkronisasi-data-unity",
    "diagram_alur_navmesh_rendering": "gambar-2.18-alur-navmesh-rendering",
}

FORBIDDEN = (
    "api sik",
    "data dosen",
    "data mahasiswa",
    "akreditasi publik",
    "crud fakultas",
    "login melalui backend",
    "satu arah",
    "segoe ui",
)


def _manifest_by_id():
    payload = json.loads((IMAGES / "manifest.json").read_text(encoding="utf-8"))
    return {entry["id"]: entry for entry in payload["images"]}


def test_active_uml_sources_use_tnr_and_current_contract():
    combined = []
    for stem in ACTIVE.values():
        source = (DIAGRAMS / f"{stem}.puml").read_text(encoding="utf-8")
        lower = source.lower()
        assert 'defaultfontname "times new roman"' in lower
        assert not re.search(r"^\s*title\b", source, re.MULTILINE | re.IGNORECASE)
        assert "gambar 2." not in lower
        assert not re.search(r"\b[0-9a-f]{7,40}\b", source, re.IGNORECASE)
        assert not re.search(r"[a-z]:\\|/users/|/home/", source, re.IGNORECASE)
        for forbidden in FORBIDDEN:
            assert forbidden not in lower
        combined.append(source)

    contract = "\n".join(combined)
    for required in (
        "/api/unity/data",
        "/api/unity/names",
        "NavigateTo",
        "StopNavigation",
        "SetSpawn",
        "SetDevice",
        "OnNavigationCompleted",
        "CompleteNavigation",
        "A*",
    ):
        assert required in contract


def test_active_pngs_match_manifest_sources_and_have_svg_counterparts():
    manifest = _manifest_by_id()
    assert "diagram_use_case_legenda" not in manifest
    for diagram_id, stem in ACTIVE.items():
        entry = manifest[diagram_id]
        report_image = IMAGES / entry["file"]
        rendered_png = DIAGRAMS / f"{stem}.png"
        rendered_svg = DIAGRAMS / f"{stem}.svg"
        assert report_image.read_bytes() == rendered_png.read_bytes()
        assert rendered_svg.exists()
        svg = rendered_svg.read_text(encoding="utf-8")
        assert "Times New Roman" in svg
        assert not re.search(r"<title>\s*Gambar\b", svg, re.IGNORECASE)


def test_active_markdown_uses_exactly_six_uml_markers_without_manual_bold():
    draft = (ROOT / "Tugas_Akhir_Draft.md").read_text(encoding="utf-8")
    for diagram_id in ACTIVE:
        assert draft.count(f"[FIGURE:{diagram_id}]") == 1
        assert draft.count(f"[FIGREF:{diagram_id}]") >= 1
    assert "diagram_use_case_legenda" not in draft
    assert "**" not in draft
    assert "[TBD:" not in draft
    assert not re.search(r"`[0-9a-f]{7,40}`", draft, re.IGNORECASE)
    assert not re.search(r"[A-Z]:\\|/Users/|/home/|Assets/", draft, re.IGNORECASE)
    assert "hash commit" not in draft.lower()
    assert "path lokal" not in draft.lower()
    assert "satu arah" not in draft.lower()
