#!/usr/bin/env python3
"""
Tool to pack a directory into a .docx, .pptx, or .xlsx file with XML formatting undone.

Example usage:
    python pack.py <input_directory> <office_file> [--force]
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
import defusedxml.minidom
import zipfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Pack a directory into an Office file")
    parser.add_argument("input_directory", help="Unpacked Office document directory")
    parser.add_argument("output_file", help="Output Office file (.docx/.pptx/.xlsx)")
    parser.add_argument("--force", action="store_true", help="Skip validation")
    args = parser.parse_args()

    try:
        success = pack_document(
            args.input_directory, args.output_file, validate=not args.force
        )

        # Show warning if validation was skipped
        if args.force:
            print("Warning: Skipped validation, file may be corrupt", file=sys.stderr)
        # Exit with error if validation failed
        elif not success:
            print("Contents would produce a corrupt file.", file=sys.stderr)
            print("Please validate XML before repacking.", file=sys.stderr)
            print("Use --force to skip validation and pack anyway.", file=sys.stderr)
            sys.exit(1)

    except ValueError as e:
        sys.exit(f"Error: {e}")


def pack_document(input_dir, output_file, validate=False):
    """Pack a directory into an Office file (.docx/.pptx/.xlsx).

    Args:
        input_dir: Path to unpacked Office document directory
        output_file: Path to output Office file
        validate: If True, validates with soffice (default: False)

    Returns:
        bool: True if successful, False if validation failed
    """
    input_dir = Path(input_dir)
    output_file = Path(output_file)

    if not input_dir.is_dir():
        raise ValueError(f"{input_dir} is not a directory")
    if output_file.suffix.lower() not in {".docx", ".pptx", ".xlsx"}:
        raise ValueError(f"{output_file} must be a .docx, .pptx, or .xlsx file")

    # Work in temporary directory to avoid modifying original
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_content_dir = Path(temp_dir) / "content"
        shutil.copytree(input_dir, temp_content_dir)

        # Process XML files to remove pretty-printing whitespace
        # Note: Bypassed to prevent minidom namespace and formatting corruption in MS Word
        # for pattern in ["*.xml", "*.rels"]:
        #     for xml_file in temp_content_dir.rglob(pattern):
        #         condense_xml(xml_file)

        # Create final Office file as zip archive
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in temp_content_dir.rglob("*"):
                if f.is_file():
                    zf.write(f, f.relative_to(temp_content_dir))

        # Validate if requested
        if validate:
            if not validate_document(output_file):
                output_file.unlink()  # Delete the corrupt file
                return False

        # Update fields via COM automation (Windows only)
        import platform
        if platform.system() == 'Windows':
            try:
                # Find update_fields_com.py relative to this script
                script_dir = Path(__file__).parent
                com_script = script_dir / 'update_fields_com.py'
                if com_script.exists():
                    print("Updating fields via COM automation...")
                    import subprocess
                    result = subprocess.run(
                        [sys.executable, str(com_script), str(output_file)],
                        capture_output=True, text=True
                    )
                    if result.returncode != 0:
                        print(f"Warning: COM field update failed:\n{result.stderr}\n{result.stdout}")
                    else:
                        print("COM field update completed successfully.")
                        cleanup_post_com_update(output_file)
                else:
                    print("Warning: update_fields_com.py not found, skipping field update.")
            except Exception as e:
                print(f"Warning: Failed to run COM field update: {e}")

    return True


def validate_document(doc_path):
    """Validate document by converting to HTML with soffice."""
    # Determine the correct filter based on file extension
    match doc_path.suffix.lower():
        case ".docx":
            filter_name = "html:HTML"
        case ".pptx":
            filter_name = "html:impress_html_Export"
        case ".xlsx":
            filter_name = "html:HTML (StarCalc)"

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            result = subprocess.run(
                [
                    "soffice",
                    "--headless",
                    "--convert-to",
                    filter_name,
                    "--outdir",
                    temp_dir,
                    str(doc_path),
                ],
                capture_output=True,
                timeout=10,
                text=True,
            )
            if not (Path(temp_dir) / f"{doc_path.stem}.html").exists():
                error_msg = result.stderr.strip() or "Document validation failed"
                print(f"Validation error: {error_msg}", file=sys.stderr)
                return False
            return True
        except FileNotFoundError:
            print("Warning: soffice not found. Skipping validation.", file=sys.stderr)
            return True
        except subprocess.TimeoutExpired:
            print("Validation error: Timeout during conversion", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Validation error: {e}", file=sys.stderr)
            return False


def condense_xml(xml_file):
    """Strip unnecessary whitespace and remove comments."""
    with open(xml_file, "r", encoding="utf-8") as f:
        dom = defusedxml.minidom.parse(f)

    # Process each element to remove whitespace and comments
    for element in dom.getElementsByTagName("*"):
        # Skip w:t elements and their processing
        if element.tagName.endswith(":t"):
            continue

        # Remove whitespace-only text nodes and comment nodes
        for child in list(element.childNodes):
            if (
                child.nodeType == child.TEXT_NODE
                and child.nodeValue
                and child.nodeValue.strip() == ""
            ) or child.nodeType == child.COMMENT_NODE:
                element.removeChild(child)

    # Write back the condensed XML
    with open(xml_file, "wb") as f:
        f.write(dom.toxml(encoding="UTF-8"))


def cleanup_post_com_update(docx_path):
    """Clean up empty TableofFigures paragraphs in document.xml after COM update."""
    import zipfile
    import tempfile
    import shutil
    import os
    try:
        import lxml.etree as ET
    except ImportError:
        import xml.etree.ElementTree as ET

    temp_dir = tempfile.mkdtemp()
    try:
        docx_path = str(docx_path)
        with zipfile.ZipFile(docx_path, 'r') as zin:
            zin.extract('word/document.xml', temp_dir)
            
        xml_path = os.path.join(temp_dir, 'word', 'document.xml')
        
        tree = ET.parse(xml_path)
        root = tree.getroot()
        namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        body = root.find('w:body', namespaces)
        if body is None:
            return
            
        children = list(body)
        paragraphs_to_remove = []
        
        for idx in range(1, len(children)):
            child = children[idx]
            if child.tag.endswith('p'):
                pPr = child.find('w:pPr', namespaces)
                pStyle = pPr.find('w:pStyle', namespaces) if pPr is not None else None
                pStyle_val = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if pStyle is not None else ""
                
                if pStyle_val == 'TableofFigures':
                    text = "".join(child.itertext()).strip()
                    if not text:
                        runs = child.findall('w:r', namespaces)
                        if runs:
                            prev_p = children[idx - 1]
                            if prev_p.tag.endswith('p'):
                                print(f"Cleanup: Moving {len(runs)} run(s) from empty TableofFigures paragraph at index {idx} to preceding paragraph.")
                                for run in runs:
                                    child.remove(run)
                                    prev_p.append(run)
                                paragraphs_to_remove.append(child)
                            else:
                                print(f"Cleanup: Preceding sibling is not a paragraph at index {idx}, skipping move.")
                        else:
                            paragraphs_to_remove.append(child)
                            print(f"Cleanup: Removing empty TableofFigures paragraph at index {idx}.")
                            
        if paragraphs_to_remove:
            for p in paragraphs_to_remove:
                body.remove(p)
            
            tree.write(xml_path, encoding='utf-8', xml_declaration=True)
            
            temp_zip_path = docx_path + '.temp'
            with zipfile.ZipFile(docx_path, 'r') as zin:
                with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zout:
                    for item in zin.infolist():
                        if item.filename == 'word/document.xml':
                            zout.write(xml_path, 'word/document.xml')
                        else:
                            zout.writestr(item, zin.read(item.filename))
            os.replace(temp_zip_path, docx_path)
            print("Cleanup: Successfully cleaned up empty TableofFigures paragraphs in final docx.")
            
    except Exception as e:
        print(f"Warning: Failed to cleanup empty TableofFigures paragraphs: {e}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
