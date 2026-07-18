"""Regression tests for exact Markdown-to-manifest figure references."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MERGE_SCRIPT = ROOT / "skills" / "scripts" / "merge_draft_to_docx.py"


def _load_merge_module():
    spec = importlib.util.spec_from_file_location("merge_with_figure_markers", MERGE_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


mrg = _load_merge_module()


def _paragraph(text):
    return {"type": "paragraph", "text": text}


def _manifest(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(
        json.dumps(
            {
                "images": [
                    {
                        "id": "fig_alpha",
                        "file": "alpha.png",
                        "caption_match": "Diagram Alpha",
                        "inject_method": "post_com",
                    },
                    {
                        "id": "fig_beta",
                        "file": "beta.png",
                        "caption_match": "Diagram Beta",
                        "inject_method": "post_com",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    return path


def test_complete_exact_marker_set_is_valid(tmp_path):
    items = [
        _paragraph("[FIGURE:fig_alpha]"),
        _paragraph("Gambar 2.1 Diagram Alpha"),
        _paragraph("[FIGURE:fig_beta]"),
        _paragraph("Gambar 2.2 Diagram Beta"),
    ]
    assert mrg.validate_figure_markers(items, _manifest(tmp_path)) == []


def test_marker_validation_reports_unknown_duplicate_missing_and_bad_adjacency(tmp_path):
    items = [
        _paragraph("[FIGURE:fig_alpha]"),
        _paragraph("Gambar 2.1 Diagram Yang Salah"),
        _paragraph("[FIGURE:fig_alpha]"),
        _paragraph("Gambar 2.2 Diagram Alpha"),
        _paragraph("[FIGURE:fig_unknown]"),
        _paragraph("Gambar 2.3 Diagram Unknown"),
    ]
    errors = "\n".join(mrg.validate_figure_markers(items, _manifest(tmp_path)))
    assert "caption does not contain expected text" in errors
    assert "occurs 2 times" in errors
    assert "unknown figure marker" in errors
    assert "[FIGURE:fig_beta]" in errors


def test_malformed_marker_is_rejected(tmp_path):
    errors = mrg.validate_figure_markers(
        [_paragraph("[FIGURE:Fig Alpha]")], _manifest(tmp_path)
    )
    assert errors and "malformed figure marker" in errors[0]


def test_repository_draft_names_every_manifest_figure_once():
    items = mrg.parse_markdown(str(ROOT / "Tugas_Akhir_Draft.md"))
    markers = [mrg.figure_marker_id(item) for item in items if mrg.figure_marker_id(item)]
    if not markers:
        pytest.skip("branch draft still uses the supported legacy caption fallback")
    manifest = json.loads((ROOT / "images" / "manifest.json").read_text(encoding="utf-8-sig"))
    expected = {
        item["id"]
        for item in manifest.get("images", [])
        if item.get("inject_method") == "post_com"
    }
    assert len(markers) == len(set(markers)) == len(expected)
    assert set(markers) == expected
    assert mrg.validate_figure_markers(items, ROOT / "images" / "manifest.json") == []
