import pdfplumber
import os

def check_paragraphs():
    pdf_path = "BAB 3.pdf"
    with pdfplumber.open(pdf_path) as pdf:
        for idx in range(1, 6): # pages 2 to 6
            page = pdf.pages[idx]
            print(f"\n=== Page {idx+1} ===")
            
            # Extract characters
            chars = page.chars
            if not chars:
                continue
                
            # Group into lines
            sorted_chars = sorted(chars, key=lambda c: (c['top'], c['x0']))
            lines = []
            current_line = []
            current_top = None
            for c in sorted_chars:
                if current_top is None:
                    current_top = c['top']
                    current_line.append(c)
                elif abs(c['top'] - current_top) < 3.0:
                    current_line.append(c)
                else:
                    lines.append(current_line)
                    current_line = [c]
                    current_top = c['top']
            if current_line:
                lines.append(current_line)
                
            # Print lines and analyze their starts
            for i, line in enumerate(lines[:15]):
                txt = "".join([c['text'] for c in line])
                x0 = min([c['x0'] for c in line])
                first_char = txt[0] if txt else ''
                # check if first char is space
                has_leading_space = txt.startswith(' ')
                print(f"Line {i+1:2d}: x0={x0:.2f}, lead_space={has_leading_space}, txt='{txt[:75]}'")

if __name__ == '__main__':
    check_paragraphs()
