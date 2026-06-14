import os
import sys

def inspect_bibliography(text_path):
    if not os.path.exists(text_path):
        print("document_text.txt not found")
        return
        
    with open(text_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    bib_start = -1
    for idx, line in enumerate(lines):
        if 'DAFTAR PUSTAKA' in line and '[Heading1]' in line:
            if idx > 50:
                bib_start = idx
                break
                
    if bib_start == -1:
        print("DAFTAR PUSTAKA section header not found.")
        return
        
    print(f"DAFTAR PUSTAKA found at line {bib_start+1}")
    print("--- DAFTAR PUSTAKA CONTENT ---")
    for idx in range(bib_start, min(len(lines), bib_start + 100)):
        line = lines[idx]
        # Replace non-ascii characters for console print safety
        safe_line = "".join([c if ord(c) < 128 else f"\\u{ord(c):04x}" for c in line])
        print(f"{idx+1}: {safe_line}", end='')

if __name__ == '__main__':
    inspect_bibliography('scratch/document_text.txt')
