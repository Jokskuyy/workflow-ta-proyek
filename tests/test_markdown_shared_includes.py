"""Regression tests for deterministic shared Markdown composition."""

import importlib.util
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MERGE_SCRIPT = ROOT / "skills" / "scripts" / "merge_draft_to_docx.py"


def _load_merge_module():
    spec = importlib.util.spec_from_file_location("merge_with_shared_includes", MERGE_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


mrg = _load_merge_module()


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_include_is_expanded_in_memory_and_parsed(tmp_path):
    fragment = _write(
        tmp_path / "content" / "shared" / "testing" / "result.md",
        "Paragraf hasil bersama.\n\n[TABLE]\nA | B\n1 | 2\n[/TABLE]\n",
    )
    source_text = (
        "# BAB I PENDAHULUAN\n\n"
        "## 1.1 Latar Belakang\n\n"
        "<!-- PIPELINE:INCLUDE content/shared/testing/result.md -->\n"
    )
    draft = _write(tmp_path / "Tugas_Akhir_Draft.md", source_text)

    expanded, included = mrg.expand_markdown_includes(draft, tmp_path)
    items = mrg.parse_markdown(draft, workspace_root=tmp_path)

    assert "Paragraf hasil bersama." in expanded
    assert "PIPELINE:INCLUDE" not in expanded
    assert included == [fragment.resolve()]
    assert draft.read_text(encoding="utf-8") == source_text
    assert any(i["type"] == "paragraph" and i["text"] == "Paragraf hasil bersama."
               for i in items)
    assert [i["type"] for i in items].count("table") == 1


def test_nested_includes_are_deterministic(tmp_path):
    second = _write(tmp_path / "content" / "shared" / "second.md", "Isi kedua.\n")
    first = _write(
        tmp_path / "content" / "shared" / "first.md",
        "Isi pertama.\n<!-- PIPELINE:INCLUDE content/shared/second.md -->\n",
    )
    draft = _write(
        tmp_path / "Tugas_Akhir_Draft.md",
        "# BAB I\n<!-- PIPELINE:INCLUDE content/shared/first.md -->\n",
    )

    expanded, included = mrg.expand_markdown_includes(draft, tmp_path)

    assert expanded.index("Isi pertama.") < expanded.index("Isi kedua.")
    assert included == [first.resolve(), second.resolve()]


@pytest.mark.parametrize(
    "directive, expected",
    [
        ("<!-- PIPELINE:INCLUDE content/shared/missing.md -->", "tidak ditemukan"),
        ("<!-- PIPELINE:INCLUDE ../outside.md -->", "keluar dari root"),
        ("<!-- PIPELINE:INCLUDE content/shared/data.json -->", "file Markdown"),
        ("<!-- PIPELINE:INCLUDE -->", "directive include tidak valid"),
    ],
)
def test_invalid_include_fails_before_merge(tmp_path, directive, expected):
    draft = _write(tmp_path / "Tugas_Akhir_Draft.md", f"# BAB I\n{directive}\n")

    with pytest.raises(mrg.MarkdownIncludeError, match=expected):
        mrg.expand_markdown_includes(draft, tmp_path)


def test_duplicate_include_is_fatal(tmp_path):
    _write(tmp_path / "content" / "shared" / "same.md", "Isi.\n")
    marker = "<!-- PIPELINE:INCLUDE content/shared/same.md -->"
    draft = _write(tmp_path / "Tugas_Akhir_Draft.md", f"# BAB I\n{marker}\n{marker}\n")

    with pytest.raises(mrg.MarkdownIncludeError, match="lebih dari satu kali"):
        mrg.expand_markdown_includes(draft, tmp_path)


def test_recursive_include_is_fatal(tmp_path):
    _write(
        tmp_path / "content" / "shared" / "a.md",
        "<!-- PIPELINE:INCLUDE content/shared/b.md -->\n",
    )
    _write(
        tmp_path / "content" / "shared" / "b.md",
        "<!-- PIPELINE:INCLUDE content/shared/a.md -->\n",
    )
    draft = _write(
        tmp_path / "Tugas_Akhir_Draft.md",
        "# BAB I\n<!-- PIPELINE:INCLUDE content/shared/a.md -->\n",
    )

    with pytest.raises(mrg.MarkdownIncludeError, match="rekursif"):
        mrg.expand_markdown_includes(draft, tmp_path)


def test_directive_inside_code_block_remains_literal(tmp_path):
    source = (
        "# BAB I\n\n```md\n"
        "<!-- PIPELINE:INCLUDE content/shared/not-executed.md -->\n"
        "```\n"
    )
    draft = _write(tmp_path / "Tugas_Akhir_Draft.md", source)

    expanded, included = mrg.expand_markdown_includes(draft, tmp_path)

    assert expanded == source
    assert included == []


def test_bibliography_reader_uses_expanded_draft(tmp_path):
    _write(
        tmp_path / "content" / "shared" / "bibliography.md",
        "# DAFTAR PUSTAKA\n\nContoh, A. (2026). *Sumber bersama*.\n",
    )
    draft = _write(
        tmp_path / "Tugas_Akhir_Draft.md",
        "# BAB I\n\n<!-- PIPELINE:INCLUDE content/shared/bibliography.md -->\n",
    )

    result = mrg.parse_bibliography_entries(str(draft))

    assert result.section_found is True
    assert len(result) == 1
    assert result[0].year == "2026"


def test_check_include_mode_does_not_require_document_xml(tmp_path, monkeypatch, capsys):
    _write(tmp_path / "content" / "shared" / "body.md", "Isi bersama.\n")
    draft = _write(
        tmp_path / "Tugas_Akhir_Draft.md",
        "# BAB I\n<!-- PIPELINE:INCLUDE content/shared/body.md -->\n",
    )
    monkeypatch.setattr(mrg, "find_workspace_root", lambda: tmp_path)

    mrg.main([str(draft), "--check-includes"])

    assert "document.xml was not modified" in capsys.readouterr().out


def test_wrapper_in_repository_subdirectory_infers_root(tmp_path):
    _write(tmp_path / "AGENTS.md", "# Test repository\n")
    fragment = _write(
        tmp_path / "content" / "shared" / "body.md",
        "Isi bersama dari root.\n",
    )
    wrapper = _write(
        tmp_path / "notes" / "wrapper.md",
        "# BAB I\n<!-- PIPELINE:INCLUDE content/shared/body.md -->\n",
    )

    expanded, included = mrg.expand_markdown_includes(wrapper)

    assert included == [fragment.resolve()]
    assert "Isi bersama dari root." in expanded
