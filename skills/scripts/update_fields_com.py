#!/usr/bin/env python3
"""
COM Automation script to update all document fields (TOC, Daftar Gambar, Daftar Tabel, PageRefs)
using Microsoft Word in headless mode.
"""

import os
import sys
import win32com.client

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
