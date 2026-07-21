import subprocess
import os
import shutil
import sys
import time
import win32com.client


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

def run_command(args, label):
    print(f"\n>>> Running: {label}...")
    # Use sys.executable to match the current running environment
    python_exe = sys.executable
    cmd = [python_exe] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
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

def main():
    # Setup paths
    template_docx = "scratch/Tugas_Akhir_Faiz_Base.docx"
    unpacked_dir = "unpacked_ta"
    output_docx = "Tugas_Akhir_Formatted.docx"
    faiz_output_docx = "Tugas_Akhir_Faiz_Formatted.docx"
    
    # Kill any running Word processes and wait for the output to be writable,
    # retrying with a short backoff (a lingering Word/COM instance from a prior
    # run can keep the file locked briefly).
    print("Terminating background Word processes to release file locks...")
    if not ensure_unlocked(output_docx) or not ensure_unlocked(faiz_output_docx):
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
        
    # 1. Create and unpack a clean branch-specific document skeleton. The
    # report body still comes exclusively from Tugas_Akhir_Draft.md.
    run_command(
        ["skills/scripts/create_faiz_base_docx.py", template_docx],
        "Create clean Faiz base DOCX"
    )

    # 2. Unpack fresh template
    run_command(
        ["skills/scripts/unpack.py", template_docx, unpacked_dir],
        "Unpack template docx"
    )
    
    # 2. Merge draft Markdown to XML
    run_command(
        ["scratch/merge_draft_to_docx.py"],
        "Merge draft markdown to docx XML"
    )
    
    # 5. Add numbering preset
    run_command(
        ["skills/scripts/add_numbering_preset.py", unpacked_dir],
        "Add numbering presets to unpacked docx"
    )
    
    # 6. Apply formatting rules
    run_command(
        ["skills/scripts/format_ta_proyek.py", unpacked_dir],
        "Format document layout and style XML files"
    )
    
    # 7. Pack unpacked directory to docx
    run_command(
        ["skills/scripts/pack.py", unpacked_dir, output_docx],
        "Pack XML files back to DOCX"
    )
    
    # 8. Post-COM image injection (all images based on manifest)
    run_command(
        ["scratch/inject_all_images.py", output_docx],
        "Post-COM inject all images"
    )

    # Word COM can replace core properties with the local Office account name.
    # Write the final Faiz deliverable to a separate path so a short-lived lock
    # on the COM-generated intermediate cannot block metadata correction.
    run_command(
        ["skills/scripts/set_docx_metadata.py", output_docx, faiz_output_docx],
        "Set final Faiz document metadata"
    )
    
    # 9. Verify generated document structure and fields
    run_command(
        ["scratch/validate_docx_structure.py", faiz_output_docx],
        "Verify generated document structure and fields"
    )

    # Clean up unpacked directory
    if os.path.exists(unpacked_dir):
        print(f"\nCleaning up {unpacked_dir}...")
        shutil.rmtree(unpacked_dir)
        
    print("\n=======================================================")
    print(f"SUCCESS: Generated formatted document: {faiz_output_docx}")
    print("=======================================================")


if __name__ == '__main__':
    main()
