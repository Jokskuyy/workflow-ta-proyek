#!/usr/bin/env python3
"""CLI for safe, optional AI-assisted Markdown generation.

Default behaviour is ``suggest``: validate a structured candidate and print its
diff without changing ``Tugas_Akhir_Draft.md``.  ``--apply`` is the only switch
that authorises an atomic append to the selected subchapter.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from alur_penulisan.agentic_generation import (  # noqa: E402
    GenerationStatus,
    prepare_generation_request,
    run_agentic_generation,
)
from alur_penulisan.generation_providers import (  # noqa: E402
    HttpJsonProvider,
    ResponseFileProvider,
)


ROLE_GUIDES = {
    "iman": "laporan-tim/iman-fullstack-integrator/README.md",
    "dwikhi": "laporan-tim/dwikhi-3d-asset-database/README.md",
    "faiz": "laporan-tim/faiz-engine-developer/README.md",
}


def _detect_branch(cwd: Path) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    value = completed.stdout.strip()
    return value or None


def _role_from_branch(branch: str | None) -> str | None:
    if not branch:
        return None
    token = branch.replace("\\", "/").rsplit("/", 1)[-1].casefold()
    return token if token in ROLE_GUIDES else None


def _read_role_context(root: Path, branch: str | None) -> str:
    role = _role_from_branch(branch)
    relative = ROLE_GUIDES.get(role or "")
    if not relative:
        return ""
    try:
        return (root / relative).read_text(encoding="utf-8")
    except OSError:
        return ""


def _write_json(path: str, payload: object) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_text(path: str, text: str) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a validated TA subchapter proposal. Default: suggest-only; "
            "Tugas_Akhir_Draft.md changes only with --apply."
        )
    )
    parser.add_argument("--section", required=True, help="Target subchapter, e.g. 3.2.1")
    parser.add_argument(
        "--instruction",
        default="Berikan usulan pengembangan konten yang relevan dan tidak mengulang isi yang sudah ada.",
        help="Natural-language generation instruction",
    )
    parser.add_argument("--draft", default="Tugas_Akhir_Draft.md")
    parser.add_argument("--facts", default="project_facts.json")
    parser.add_argument("--term-registry", default="term_registry.json")
    parser.add_argument(
        "--branch",
        help="Override active branch detection; only laporan/iman|dwikhi|faiz are accepted",
    )
    parser.add_argument(
        "--fact",
        action="append",
        default=[],
        metavar="DOT.KEY",
        help=(
            "Explicit project_facts.json key to expose to the provider; repeatable. "
            "No facts are sent by default."
        ),
    )

    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "--response-file",
        help="Structured candidate JSON produced by any AI agent",
    )
    source.add_argument(
        "--endpoint",
        nargs="?",
        const=os.environ.get("TA_GENERATOR_ENDPOINT"),
        help=(
            "Provider-neutral HTTP JSON adapter. Pass a URL, or pass --endpoint "
            "without a value to read TA_GENERATOR_ENDPOINT."
        ),
    )
    parser.add_argument(
        "--token-env",
        default="TA_GENERATOR_TOKEN",
        help="Environment variable containing the optional HTTP bearer token",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("TA_GENERATOR_MODEL"),
        help="Optional model hint forwarded to the HTTP adapter",
    )
    parser.add_argument("--timeout", type=float, default=120.0)

    parser.add_argument(
        "--prepare-out",
        help=(
            "Write the provider-neutral request JSON. If no provider is selected, "
            "stop after preparation."
        ),
    )
    parser.add_argument(
        "--result-out",
        help="Optional path for the validated result/candidate JSON",
    )
    parser.add_argument("--diff-out", help="Optional path for the unified diff")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="After validation, atomically append the candidate to the target Markdown section",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    branch = args.branch or _detect_branch(REPO_ROOT)
    role_context = _read_role_context(REPO_ROOT, branch)

    if args.prepare_out:
        try:
            request = prepare_generation_request(
                draft_path=args.draft,
                section_id=args.section,
                instruction=args.instruction,
                active_branch=branch,
                facts_path=args.facts,
                fact_keys=args.fact,
                term_registry_path=args.term_registry,
                role_context=role_context,
            )
        except Exception as exc:
            print(json.dumps({"status": "failed", "message": str(exc)}, ensure_ascii=False))
            return 1
        _write_json(args.prepare_out, request.to_mapping())
        if not args.response_file and not args.endpoint:
            summary = {
                "status": GenerationStatus.PREPARED.value,
                "section_id": args.section,
                "active_role": request.active_role,
                "message": (
                    "Request JSON dibuat; Markdown belum diubah. Berikan request ini ke AI "
                    "agent, lalu validasi responsnya dengan --response-file."
                ),
                "request_out": args.prepare_out,
                "wrote_draft": False,
            }
            print(json.dumps(summary, ensure_ascii=False, indent=2))
            return 0

    if not args.response_file and not args.endpoint:
        if "--endpoint" in (argv or sys.argv[1:]):
            parser.error("--endpoint needs a URL or a non-empty TA_GENERATOR_ENDPOINT")
        parser.error("select --response-file or --endpoint, or use --prepare-out")

    if args.response_file:
        provider = ResponseFileProvider(args.response_file)
    else:
        token = os.environ.get(args.token_env) if args.token_env else None
        provider = HttpJsonProvider(
            endpoint=args.endpoint,
            bearer_token=token,
            timeout_seconds=args.timeout,
            model=args.model,
        )

    result = run_agentic_generation(
        provider,
        draft_path=args.draft,
        section_id=args.section,
        instruction=args.instruction,
        active_branch=branch,
        apply=args.apply,
        facts_path=args.facts,
        fact_keys=args.fact,
        term_registry_path=args.term_registry,
        role_context=role_context,
    )
    summary = result.to_mapping()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if result.diff:
        print("\n--- unified diff ---")
        print(result.diff, end="" if result.diff.endswith("\n") else "\n")
    if args.result_out:
        _write_json(args.result_out, summary)
    if args.diff_out:
        _write_text(args.diff_out, result.diff)

    if result.status in {
        GenerationStatus.SUGGESTED,
        GenerationStatus.APPLIED,
        GenerationStatus.UNCHANGED,
    }:
        return 0
    if result.status in {GenerationStatus.HELD, GenerationStatus.REJECTED}:
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
