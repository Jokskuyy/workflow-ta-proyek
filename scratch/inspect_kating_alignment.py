import pdfplumber

def check_alignment():
    pdf_path = "Tugas_Akhir_Formatted.pdf"
    with pdfplumber.open(pdf_path) as pdf:
        # Check pages 18, 19, 20
        for page_idx in [17, 18, 19]:
            page = pdf.pages[page_idx]
            print(f"\n=== Page {page_idx+1} (Width: {page.width:.2f}, Height: {page.height:.2f}) ===")
            chars = page.chars
            if not chars:
                print("No characters found")
                continue
                
            # Group characters into lines
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
                
            for idx, line in enumerate(lines):
                txt = "".join([c['text'] for c in line]).strip()
                if not txt:
                    continue
                x0 = min([c['x0'] for c in line])
                x1 = max([c['x1'] for c in line])
                font = line[0].get('fontname', '')
                size = line[0].get('size', 0)
                print(f"Line {idx+1:02d}: x0={x0:.2f}, x1={x1:.2f}, sz={size:.1f}, font={font}, txt='{txt}'")

if __name__ == '__main__':
    check_alignment()
