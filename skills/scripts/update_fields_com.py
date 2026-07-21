#!/usr/bin/env python3
"""
COM Automation script to update all document fields (TOC, Daftar Gambar, Daftar Tabel, PageRefs)
using Microsoft Word in headless mode.
"""

import os
import re
import sys
import win32com.client


CAPTION_LABEL_PATTERN = re.compile(r"^(?:Gambar|Tabel)\s+\d+(?:\.\d+)+")
SEMANTIC_REF_PATTERN = re.compile(r"^\s*REF\s+(?:fig_|tbl_)", re.IGNORECASE)


def caption_label_span(text):
    """Return the visible label span for a numbered figure/table caption."""
    match = CAPTION_LABEL_PATTERN.match(text or "")
    return match.span() if match else None


def format_caption_ranges(doc):
    """Reapply caption typography after Word refreshes SEQ field results."""
    formatted = 0
    for paragraph in doc.Paragraphs:
        text = paragraph.Range.Text.rstrip("\r\x07")
        span = caption_label_span(text)
        if span is None:
            continue

        try:
            style_name = str(paragraph.Style.NameLocal)
        except Exception:
            style_name = str(paragraph.Style)
        if style_name.lower() not in {"caption", "keterangan"}:
            continue

        caption_range = doc.Range(
            Start=paragraph.Range.Start,
            End=paragraph.Range.Start + len(text),
        )
        caption_range.Font.Name = "Times New Roman"
        caption_range.Font.NameAscii = "Times New Roman"
        caption_range.Font.NameFarEast = "Times New Roman"
        caption_range.Font.NameBi = "Times New Roman"
        caption_range.Font.Size = 12
        caption_range.Font.SizeBi = 12
        caption_range.Font.Bold = 0
        caption_range.Font.BoldBi = 0
        caption_range.Font.Italic = 0
        caption_range.Font.ItalicBi = 0
        caption_range.Font.Superscript = 0
        caption_range.Font.Subscript = 0
        caption_range.Font.Position = 0
        caption_range.Font.Color = 0  # wdColorBlack

        label_range = doc.Range(
            Start=paragraph.Range.Start + span[0],
            End=paragraph.Range.Start + span[1],
        )
        label_range.Font.Bold = -1
        label_range.Font.BoldBi = -1
        formatted += 1

    return formatted


def format_semantic_reference_fields(doc):
    """Keep figure/table REF results Times New Roman 12 pt and regular."""
    formatted = 0
    for field in doc.Fields:
        try:
            instruction = str(field.Code.Text)
        except Exception:
            continue
        if not SEMANTIC_REF_PATTERN.match(instruction):
            continue

        result = field.Result
        result.Font.Name = "Times New Roman"
        result.Font.NameAscii = "Times New Roman"
        result.Font.NameFarEast = "Times New Roman"
        result.Font.NameBi = "Times New Roman"
        result.Font.Size = 12
        result.Font.SizeBi = 12
        result.Font.Bold = 0
        result.Font.BoldBi = 0
        result.Font.Italic = 0
        result.Font.ItalicBi = 0
        result.Font.Superscript = 0
        result.Font.Subscript = 0
        result.Font.Position = 0
        result.Font.Color = 0
        formatted += 1

    return formatted

def update_fields(docx_path):
    abs_path = os.path.abspath(docx_path)
    if not os.path.exists(abs_path):
        print(f"Error: File not found at {abs_path}")
        sys.exit(1)

    print(f"Opening Word COM object to update fields in: {docx_path}")
    word = None
    doc = None
    try:
        # Launch Microsoft Word headlessly
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0  # Disable all popup alerts/dialogs (wdAlertsNone)

        print("Opening document...")
        doc = word.Documents.Open(abs_path)

        # Update all field codes
        print("Updating all general fields...")
        doc.Fields.Update()

        # Specifically update all Tables of Contents (Daftar Isi)
        print("Updating Tables of Contents...")
        for toc in doc.TablesOfContents:
            toc.Update()

        # Specifically update all Tables of Figures (Daftar Gambar/Tabel)
        print("Updating Tables of Figures...")
        for tof in doc.TablesOfFigures:
            tof.Update()

        print("Reapplying semantic reference typography after field updates...")
        formatted_references = format_semantic_reference_fields(doc)
        print(f"Formatted {formatted_references} figure/table references.")

        print("Reapplying caption typography after field updates...")
        formatted_captions = format_caption_ranges(doc)
        print(f"Formatted {formatted_captions} figure/table captions.")

        print("Saving document...")
        doc.Save()
        print("Fields updated and saved successfully.")

    except Exception as e:
        print(f"Error updating fields via COM: {e}")
        # Return failure exit code
        sys.exit(1)
    finally:
        if doc is not None:
            try:
                doc.Close(SaveChanges=-1)  # wdSaveChanges
            except Exception as e:
                print(f"Error closing document: {e}")
        if word is not None:
            try:
                word.Quit()
            except Exception as e:
                print(f"Error quitting Word: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python update_fields_com.py <docx_file>")
        sys.exit(1)
        
    update_fields(sys.argv[1])
