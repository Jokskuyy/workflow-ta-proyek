import subprocess
import os
import shutil
import sys
import win32com.client

def run_command(args, label):
    print(f"\n>>> Running: {label}...")
    # Use C:\Python312\python.exe to match user environment
    python_exe = "C:\\Python312\\python.exe"
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
    template_docx = "archive/Tugas Akhir.docx"
    unpacked_dir = "unpacked_ta"
    output_docx = "Tugas_Akhir_Formatted.docx"
    
    # Kill any running Word processes to release file locks
    print("Terminating background Word processes to release file locks...")
    subprocess.run(["taskkill", "/f", "/im", "winword.exe"], capture_output=True)
    
    # Check if target docx is locked (open in Word)
    if os.path.exists(output_docx):
        try:
            with open(output_docx, "a+b") as f:
                pass
        except IOError:
            print(f"\n=======================================================")
            print(f"ERROR: '{output_docx}' is locked (likely open in Microsoft Word).")
            print(f"Please close Microsoft Word and re-run the pipeline.")
            print(f"=======================================================")
            sys.exit(1)
    
    # 0. Clean previous unpacked directory if it exists
    if os.path.exists(unpacked_dir):
        print(f"Cleaning existing {unpacked_dir} directory...")
        shutil.rmtree(unpacked_dir)
        
    # 1. Unpack fresh template
    run_command(
        ["skills/scripts/unpack.py", template_docx, unpacked_dir],
        "Unpack template docx"
    )
    
    # 2. Merge draft Markdown to XML
    run_command(
        ["scratch/merge_draft_to_docx.py"],
        "Merge draft markdown to docx XML"
    )
    
    # 2.5. Patch template Chapter II database & CRUD discrepancies
    run_command(
        ["scratch/patch_template.py"],
        "Patch template Chapter II database & CRUD discrepancies"
    )
    
    # 3. Inject interview text and caption
    run_command(
        ["scratch/inject_warek2_xml.py"],
        "Inject interview paragraph and caption"
    )
    
    # 4. Inject drawing elements (images)
    run_command(
        ["scratch/inject_images.py"],
        "Inject integrity pact and interview images"
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
    
    # 8. Post-COM image injection (sequence diagrams stripped by Word COM)
    run_command(
        ["scratch/post_com_inject_images.py", output_docx],
        "Post-COM inject sequence diagram images"
    )
    
    # 9. Verify generated document structure and fields
    run_command(
        ["scratch/validate_docx_structure.py", output_docx],
        "Verify generated document structure and fields"
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
