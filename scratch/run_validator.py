import sys
import os

# Add the docx skill validation module to path
sys.path.append(r'C:\Users\imann\.gemini\config\skills\docx\ooxml\scripts')

from validation.docx import DOCXSchemaValidator

try:
    validator = DOCXSchemaValidator('unpacked_ta_proyek', 'Tugas Akhir.docx', verbose=True)
    # Perform validation
    is_valid = validator.validate()
    print("Is document valid?", is_valid)
except Exception as e:
    print("Validation failed with error:")
    import traceback
    traceback.print_exc()
