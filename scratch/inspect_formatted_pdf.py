import pdfplumber
import os

def analyze_formatted_pdf():
    pdf_path = "Tugas_Akhir_Formatted.pdf"
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found")
        return

    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        
        # Check a few pages:
        # Page 1, 2, 3 (front matter)
        # Page 10, 15, 20 (body pages)
        pages_to_check = [0, 2, 4, 10, 20, 30]
        
        for idx in pages_to_check:
            if idx >= len(pdf.pages):
                break
            page = pdf.pages[idx]
            print(f"\n--- Page {idx + 1} Analysis ---")
            
            chars = page.chars
            if not chars:
                print("No text characters found on page")
                continue
                
            # Filter and gather font information
            fonts = {}
            sizes = {}
            for c in chars:
                f_name = c.get('fontname', 'Unknown')
                sz = round(c.get('size', 0), 2)
                fonts[f_name] = fonts.get(f_name, 0) + 1
                sizes[sz] = sizes.get(sz, 0) + 1
                
            print("Fonts found:", fonts)
            print("Font sizes found (top 5):", sorted(sizes.items(), key=lambda x: x[1], reverse=True)[:5])
            
            # Let's group characters into lines by matching their top coordinates (within 3pt)
            lines = []
            sorted_chars = sorted(chars, key=lambda c: (c['top'], c['x0']))
            
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
                
            print(f"Detected {len(lines)} text lines on page.")
            
            line_details = []
            for line in lines:
                l_text = "".join([c['text'] for c in line]).strip()
                if not l_text:
                    continue
                l_x0 = min([c['x0'] for c in line])
                l_x1 = max([c['x1'] for c in line])
                l_top = min([c['top'] for c in line])
                l_bottom = max([c['bottom'] for c in line])
                l_font = line[0].get('fontname', '')
                l_size = line[0].get('size', 0)
                line_details.append({
                    'text': l_text,
                    'x0': l_x0,
                    'x1': l_x1,
                    'top': l_top,
                    'bottom': l_bottom,
                    'font': l_font,
                    'size': l_size
                })
            
            # Print sample lines
            print("Sample lines:")
            for ld in line_details[:5]:
                print(f"  x0={ld['x0']:.1f}, x1={ld['x1']:.1f}, top={ld['top']:.1f}, bottom={ld['bottom']:.1f}, sz={ld['size']:.1f}, txt='{ld['text'][:50]}'")
                
            # Line spacing calculation for standard body text (size ~ 12)
            spacings = []
            for i in range(len(line_details) - 1):
                ld1 = line_details[i]
                ld2 = line_details[i+1]
                if abs(ld1['size'] - 12.0) < 0.5 and abs(ld2['size'] - 12.0) < 0.5:
                    dist = ld2['top'] - ld1['top']
                    if 12.0 < dist < 40.0:
                        spacings.append(dist)
            if spacings:
                avg_spacing = sum(spacings) / len(spacings)
                print(f"Average line spacing for 12pt text: {avg_spacing:.2f} pt (Ratio: {avg_spacing/12.0:.2f}x)")
            
            # Check margins based on 12pt body text
            body_x0s = [ld['x0'] for ld in line_details if abs(ld['size'] - 12.0) < 0.5 and 'Bold' not in ld['font']]
            if body_x0s:
                base_x0 = min(body_x0s)
                print(f"Inferred base Left Margin: {base_x0:.2f} pt ({base_x0/28.346:.2f} cm)")
                
                # Check for first-line indent: lines that are shifted to the right compared to base_x0
                indented_x0s = [x for x in body_x0s if x > base_x0 + 10.0]
                if indented_x0s:
                    min_indented = min(indented_x0s)
                    indent_val = min_indented - base_x0
                    print(f"Potential first-line indent: {indent_val:.2f} pt ({indent_val/28.346:.2f} cm)")
            
            body_x1s = [ld['x1'] for ld in line_details if abs(ld['size'] - 12.0) < 0.5 and 'Bold' not in ld['font']]
            if body_x1s:
                max_x1 = max(body_x1s)
                right_mar = float(page.width) - max_x1
                print(f"Inferred base Right Margin: {right_mar:.2f} pt ({right_mar/28.346:.2f} cm)")
                
            body_tops = [ld['top'] for ld in line_details if ld['top'] > 80.0]
            if body_tops:
                min_top = min(body_tops)
                print(f"Inferred base Top Margin: {min_top:.2f} pt ({min_top/28.346:.2f} cm)")
                
            body_bottoms = [ld['bottom'] for ld in line_details if ld['bottom'] < float(page.height) - 50.0]
            if body_bottoms:
                max_bottom = max(body_bottoms)
                bottom_mar = float(page.height) - max_bottom
                print(f"Inferred base Bottom Margin: {bottom_mar:.2f} pt ({bottom_mar/28.346:.2f} cm)")

if __name__ == '__main__':
    analyze_formatted_pdf()
