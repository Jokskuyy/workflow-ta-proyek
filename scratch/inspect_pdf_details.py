import pdfplumber
import os

def analyze_pdf():
    pdf_path = "BAB 3.pdf"
    if not os.path.exists(pdf_path):
        print("PDF not found")
        return

    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        
        # Analyze pages 2-5 (avoiding cover/title/table-of-contents if any, although this is BAB III)
        # Wait, since this is "BAB 3.pdf", it's probably Chapter 3.
        # Let's inspect pages 2, 3, 4, 5.
        pages_to_check = [1, 2, 3, 4] # 0-indexed: pages 2, 3, 4, 5
        
        for idx in pages_to_check:
            if idx >= len(pdf.pages):
                break
            page = pdf.pages[idx]
            print(f"\n--- Page {idx + 1} Analysis ---")
            
            # Group characters by line to determine line spacing
            chars = page.chars
            if not chars:
                print("No text characters found on page")
                continue
                
            # Filter out very small characters (like page numbers or headers)
            # Typically page number is at top right or bottom center
            # Let's see all font sizes and fonts
            font_sizes = {}
            for c in chars:
                sz = round(c['size'], 2)
                font_sizes[sz] = font_sizes.get(sz, 0) + 1
            print("Font sizes and character counts:", font_sizes)
            
            # Let's group characters into lines by matching their top coordinates (approximate within 1pt)
            lines = []
            # Sort chars by top coordinate
            sorted_chars = sorted(chars, key=lambda c: (c['top'], c['x0']))
            
            current_line = []
            current_top = None
            for c in sorted_chars:
                if current_top is None:
                    current_top = c['top']
                    current_line.append(c)
                elif abs(c['top'] - current_top) < 3.0: # threshold for same line
                    current_line.append(c)
                else:
                    lines.append(current_line)
                    current_line = [c]
                    current_top = c['top']
            if current_line:
                lines.append(current_line)
                
            print(f"Detected {len(lines)} lines on page.")
            
            # Let's extract line details: top, bottom, height, x0, x1, text
            line_details = []
            for line in lines:
                l_text = "".join([c['text'] for c in line])
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
            
            # Print first 5 lines and last 5 lines details
            print("First 5 lines:")
            for ld in line_details[:10]:
                print(f"  x0={ld['x0']:.2f}, x1={ld['x1']:.2f}, top={ld['top']:.2f}, bottom={ld['bottom']:.2f}, sz={ld['size']:.1f}, txt='{ld['text'][:60]}'")
                
            # Let's calculate standard line-to-line spacing (distance between tops of consecutive lines of same size)
            spacings = []
            for i in range(len(line_details) - 1):
                ld1 = line_details[i]
                ld2 = line_details[i+1]
                # check if both are standard body lines (size around 12)
                if abs(ld1['size'] - 12.0) < 0.5 and abs(ld2['size'] - 12.0) < 0.5:
                    dist = ld2['top'] - ld1['top']
                    # normal line spacing for 12pt is 12-30pt
                    if 12.0 < dist < 40.0:
                        spacings.append(dist)
            
            if spacings:
                avg_spacing = sum(spacings) / len(spacings)
                # in Word, double spacing is 2 * size, 1.5 spacing is 1.5 * size
                # 12pt font with 1.5 line spacing: 12 * 1.5 = 18pt line height (usually slightly more, e.g. 1.15x is normal multiplier, 
                # actually in Word, 1.5 line spacing is 1.5 * font_size = 18pt or is it relative to font's line space?)
                # Let's print average spacing in points and ratio to font size
                print(f"Average spacing between consecutive 12pt lines: {avg_spacing:.2f} pt (Ratio: {avg_spacing/12.0:.2f}x)")
            
            # Let's detect margins from typical body lines.
            # A body line is a 12pt line that is not a heading (not bold, or doesn't have large size)
            # Standard left margin: we look at x0 of lines that don't look like indented paragraphs or headings
            x0_values = [ld['x0'] for ld in line_details if abs(ld['size'] - 12.0) < 0.5 and 'Bold' not in ld['font']]
            if x0_values:
                # Standard left margin is the minimum x0 (excluding first-line indents or list bullets if any, 
                # but wait, first-line indent would have a larger x0, so the base margin is the minimum or the mode)
                # Let's sort and find the most common base x0
                # In standard pages, the main body left margin is the leftmost aligned text.
                print("x0 distribution (sorted):", sorted([round(x, 1) for x in x0_values]))
                base_x0 = min(x0_values)
                print(f"Inferred base Left Margin: {base_x0:.2f} pt ({base_x0/28.346:.2f} cm)")
                
                # Check for first-line indent: lines that are shifted to the right compared to base_x0
                indented_x0s = [x for x in x0_values if x > base_x0 + 10.0]
                if indented_x0s:
                    min_indented = min(indented_x0s)
                    indent_val = min_indented - base_x0
                    print(f"Potential first-line indent: {indent_val:.2f} pt ({indent_val/28.346:.2f} cm)")
            
            x1_values = [ld['x1'] for ld in line_details if abs(ld['size'] - 12.0) < 0.5 and 'Bold' not in ld['font']]
            if x1_values:
                # Right margin is page.width - max(x1)
                max_x1 = max(x1_values)
                base_right_margin = float(page.width) - max_x1
                print(f"Inferred base Right Margin: {base_right_margin:.2f} pt ({base_right_margin/28.346:.2f} cm)")
                
            # Top margin: find the topmost line (excluding header if any)
            # Typically, header has a separate style or position (e.g. top < 80pt)
            body_tops = [ld['top'] for ld in line_details if ld['top'] > 80.0] # assume header is above 80
            if body_tops:
                print(f"Inferred base Top Margin: {min(body_tops):.2f} pt ({min(body_tops)/28.346:.2f} cm)")
            
            # Bottom margin: find the bottommost line (excluding footer/page number if any)
            body_bottoms = [ld['bottom'] for ld in line_details if ld['bottom'] < float(page.height) - 50.0]
            if body_bottoms:
                inferred_bottom_margin = float(page.height) - max(body_bottoms)
                print(f"Inferred base Bottom Margin: {inferred_bottom_margin:.2f} pt ({inferred_bottom_margin/28.346:.2f} cm)")

if __name__ == '__main__':
    analyze_pdf()
