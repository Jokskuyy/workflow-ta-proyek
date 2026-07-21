#!/usr/bin/env python3
"""Set final DOCX metadata from project_facts.json after Word COM updates."""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[2]
def _replace_core_text(xml_text: str, tag: str, value: str) -> str:
    escaped = escape(value)
    pattern = rf"(<{re.escape(tag)}(?:\s[^>]*)?>).*?(</{re.escape(tag)}>)"
    updated, count = re.subn(pattern, rf"\g<1>{escaped}\g<2>", xml_text, count=1, flags=re.DOTALL)
    if count:
        return updated
    closing = "</cp:coreProperties>"
    return updated.replace(closing, f"<{tag}>{escaped}</{tag}>{closing}")


def set_metadata(source_path: Path, output_path: Path | None = None) -> Path:
    output_path = output_path or source_path
    facts = json.loads((ROOT / "project_facts.json").read_text(encoding="utf-8"))
    metadata = facts["project_metadata"]

    with zipfile.ZipFile(source_path, "r") as source:
        core_text = source.read("docProps/core.xml").decode("utf-8")
        core_text = _replace_core_text(core_text, "dc:title", metadata["title"])
        core_text = _replace_core_text(
            core_text,
            "dc:subject",
            "Tugas Akhir Proyek - 3D Simulator & Engine Developer",
        )
        core_text = _replace_core_text(core_text, "dc:creator", metadata["author"])
        core_text = _replace_core_text(core_text, "cp:lastModifiedBy", metadata["author"])
        core_text = _replace_core_text(
            core_text,
            "dc:description",
            "Laporan Tugas Akhir Muammar Faiz Khairul Anam tentang navigasi spasial dan optimasi Unity WebGL.",
        )
        updated_core = core_text.encode("utf-8")

        fd, temp_name = tempfile.mkstemp(suffix=".docx", dir=output_path.parent)
        os.close(fd)
        temp_path = Path(temp_name)
        try:
            with zipfile.ZipFile(temp_path, "w", zipfile.ZIP_DEFLATED) as target:
                for item in source.infolist():
                    payload = updated_core if item.filename == "docProps/core.xml" else source.read(item.filename)
                    target.writestr(item, payload)
            os.replace(temp_path, output_path)
        finally:
            if temp_path.exists():
                temp_path.unlink()
    return output_path


def main(argv: list[str] | None = None) -> None:
    argv = argv or sys.argv[1:]
    if len(argv) not in (1, 2):
        raise SystemExit("Usage: set_docx_metadata.py <source.docx> [output.docx]")
    source = Path(argv[0]).resolve()
    output = Path(argv[1]).resolve() if len(argv) == 2 else source
    created = set_metadata(source, output)
    print(f"Updated DOCX metadata for Faiz: {created}")


if __name__ == "__main__":
    main()
