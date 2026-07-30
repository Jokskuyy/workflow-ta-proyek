import argparse
import json
import subprocess
import os
import shutil
import sys
import time

PROFILE_CONFIG_PATH = os.path.join("content", "report-profiles.json")


def _kill_word():
    """Terminate any running Word instances to release file locks."""
    subprocess.run(["taskkill", "/f", "/im", "winword.exe"], capture_output=True)


def _is_locked(path):
    """True if the file exists and cannot be opened for writing."""
    if not os.path.exists(path):
        return False
    try:
        with open(path, "a+b"):
            return False
    except (IOError, OSError):
        return True


def ensure_unlocked(path, attempts=5, wait_seconds=2):
    """Kill Word and wait until ``path`` is writable, retrying a few times.

    Word (including instances spawned by this pipeline's own COM field-update
    step) can linger and hold a lock on the output docx. Rather than failing
    immediately, kill Word and retry with a short backoff before giving up.
    """
    for attempt in range(1, attempts + 1):
        _kill_word()
        time.sleep(wait_seconds)
        if not _is_locked(path):
            return True
        print(f"  '{path}' still locked (attempt {attempt}/{attempts}); retrying...")
    return not _is_locked(path)

def run_command(args, label, *, env=None):
    print(f"\n>>> Running: {label}...")
    # Use C:\Python312\python.exe to match user environment
    python_exe = "C:\\Python312\\python.exe"
    cmd = [python_exe] + args
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"ERROR: {label} failed with exit code {result.returncode}")
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
        sys.exit(1)
    else:
        print(f"SUCCESS: {label} completed.")
        if result.stdout.strip():
            print(result.stdout.strip())

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Build and validate the formatted Tugas Akhir DOCX."
    )
    parser.add_argument(
        "--profile",
        default="iman",
        help=(
            "Report build profile from content/report-profiles.json "
            "(default: iman)."
        ),
    )
    parser.add_argument(
        "--output",
        default=None,
        help=(
            "Output DOCX path. When omitted, the selected profile's output "
            "name is used."
        ),
    )
    return parser.parse_args(argv)


def load_profile(profile_name, config_path=PROFILE_CONFIG_PATH):
    if not os.path.isfile(config_path):
        raise FileNotFoundError(
            f"Report profile configuration not found: {config_path}"
        )
    with open(config_path, "r", encoding="utf-8") as profile_file:
        profiles = json.load(profile_file)
    if profile_name not in profiles:
        available = ", ".join(sorted(profiles))
        raise ValueError(
            f"Unknown report profile '{profile_name}'. Available: {available}"
        )
    profile = profiles[profile_name]
    required = {
        "draft",
        "front_matter",
        "image_root",
        "manifest",
        "reconcile",
        "output",
    }
    missing = sorted(required - set(profile))
    if missing:
        raise ValueError(
            f"Profile '{profile_name}' is missing keys: {', '.join(missing)}"
        )
    for key in required - {"output"}:
        if not os.path.exists(profile[key]):
            raise FileNotFoundError(
                f"Profile '{profile_name}' path for {key} not found: "
                f"{profile[key]}"
            )
    return profile


def main(argv=None):
    args = parse_args(argv)
    try:
        profile = load_profile(args.profile)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    build_env = os.environ.copy()
    build_env.update({
        "TA_REPORT_PROFILE": args.profile,
        "TA_DRAFT_PATH": profile["draft"],
        "TA_FRONT_MATTER_PATH": profile["front_matter"],
        "TA_IMAGE_ROOT": profile["image_root"],
        "TA_IMAGE_MANIFEST_PATH": profile["manifest"],
        "TA_IMAGE_RECONCILE_PATH": profile["reconcile"],
    })

    # Setup paths
    template_docx = "archive/Tugas Akhir.docx"
    unpacked_dir = "unpacked_ta"
    output_docx = args.output or profile["output"]

    print(
        f"Selected report profile '{args.profile}' "
        f"(draft: {profile['draft']}, output: {output_docx})."
    )
    
    # Kill any running Word processes and wait for the output to be writable,
    # retrying with a short backoff (a lingering Word/COM instance from a prior
    # run can keep the file locked briefly).
    print("Terminating background Word processes to release file locks...")
    if not ensure_unlocked(output_docx):
        print(f"\n=======================================================")
        print(f"ERROR: '{output_docx}' is locked (likely open in Microsoft Word).")
        print(f"Please close Microsoft Word and re-run the pipeline.")
        print(f"=======================================================")
        sys.exit(1)
    
    # 0. Bootstrap: regenerate the scratch/ runtime copies from the tracked
    # skills/scripts/ sources (single source of truth). Some of these scripts
    # are gitignored under scratch/, so this guarantees a fresh clone has them
    # and that scratch never drifts from the version-controlled skills copies.
    # (The scripts resolve the repo root as parents[1], so they must run from
    # scratch/ -- one level under the repo root -- not skills/scripts/.)
    print("Syncing runtime scripts from skills/scripts/ into scratch/...")
    for _name in ("merge_draft_to_docx.py", "patch_template.py",
                  "inject_all_images.py", "validate_docx_structure.py"):
        _src = os.path.join("skills", "scripts", _name)
        _dst = os.path.join("scratch", _name)
        if os.path.exists(_src):
            shutil.copyfile(_src, _dst)

    # 0.1. Clean previous unpacked directory if it exists
    if os.path.exists(unpacked_dir):
        print(f"Cleaning existing {unpacked_dir} directory...")
        shutil.rmtree(unpacked_dir)
        
    # 1. Unpack fresh template
    run_command(
        ["skills/scripts/unpack.py", template_docx, unpacked_dir],
        "Unpack template docx",
        env=build_env,
    )
    
    # 2. Merge draft Markdown to XML
    run_command(
        ["scratch/merge_draft_to_docx.py", profile["draft"]],
        "Merge draft markdown to docx XML",
        env=build_env,
    )
    
    # 2.5. Patch template Chapter II database & CRUD discrepancies
    run_command(
        ["scratch/patch_template.py"],
        "Patch template Chapter II database & CRUD discrepancies",
        env=build_env,
    )
    
    # 5. Add numbering preset
    run_command(
        ["skills/scripts/add_numbering_preset.py", unpacked_dir],
        "Add numbering presets to unpacked docx",
        env=build_env,
    )
    
    # 6. Apply formatting rules
    run_command(
        ["skills/scripts/format_ta_proyek.py", unpacked_dir],
        "Format document layout and style XML files",
        env=build_env,
    )
    
    # 7. Pack unpacked directory to docx
    run_command(
        ["skills/scripts/pack.py", unpacked_dir, output_docx],
        "Pack XML files back to DOCX",
        env=build_env,
    )
    
    # 8. Post-COM image injection (all images based on manifest)
    run_command(
        ["scratch/inject_all_images.py", output_docx],
        "Post-COM inject all images",
        env=build_env,
    )

    # Image injection can change pagination after Word has populated the TOC,
    # lists of figures/tables, and PAGEREF caches. Refresh the fields once the
    # final drawings exist, then restore the direct formatting Word normalizes
    # without inserting or replacing any image a second time.
    run_command(
        ["skills/scripts/update_fields_com.py", output_docx],
        "Refresh fields after final image pagination",
        env=build_env,
    )
    run_command(
        ["scratch/inject_all_images.py", output_docx, "--repair-only"],
        "Restore post-COM formatting without reinjecting images",
        env=build_env,
    )
    
    # 9. Verify generated document structure and fields
    run_command(
        ["scratch/validate_docx_structure.py", output_docx],
        "Verify generated document structure and fields",
        env=build_env,
    )
    
    # Clean up unpacked directory
    if os.path.exists(unpacked_dir):
        print(f"\nCleaning up {unpacked_dir}...")
        shutil.rmtree(unpacked_dir)
        
    print("\n=======================================================")
    print(f"SUCCESS: Generated formatted document: {output_docx}")
    print("=======================================================")


if __name__ == '__main__':
    main()
