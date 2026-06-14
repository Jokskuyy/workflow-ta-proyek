import sys
import os
from pathlib import Path

# Add the docx skill validation module to path
sys.path.append(r'C:\Users\imann\.gemini\config\skills\docx\ooxml\scripts')

from validation.docx import DOCXSchemaValidator

validator = DOCXSchemaValidator('unpacked_ta', 'Tugas Akhir(1)_backup.docx', verbose=True)
print("xml_files:", [str(f) for f in validator.xml_files])
print("unpacked paragraph count:", validator.count_paragraphs_in_unpacked())
print("original paragraph count:", validator.count_paragraphs_in_original())
