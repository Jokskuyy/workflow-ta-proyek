import pdfplumber

def main():
    pdf_path = "Tugas_Akhir_Formatted.pdf"
    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
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
                
            for line in lines:
                txt = "".join([c['text'] for c in line]).strip()
                # If the line starts with standard headings like "1.1", "2.1", "3.1"
                # (since we stripped the manual numbering, they are formatted by Word list numbering,
                # which in PDF shows up as "1.1 Latar Belakang" or similar)
                import re
                if re.match(r'^[0-9]+\.[0-9]+', txt) or txt.startswith("BAB ") or txt.startswith("PENDAHULUAN") or txt.startswith("RANCANGAN PROYEK") or txt.startswith("IMPLEMENTASI PROYEK"):
                    x0 = min([c['x0'] for c in line])
                    print(f"Page {page_idx+1:02d}: x0={x0:.2f}, txt='{txt}'")

if __name__ == '__main__':
    main()
