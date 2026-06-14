import pdfplumber
import os

def analyze_pdf_properties(pdf_path, name):
    if not os.path.exists(pdf_path):
        return None
        
    results = {}
    with pdfplumber.open(pdf_path) as pdf:
        results['pages_count'] = len(pdf.pages)
        if len(pdf.pages) == 0:
            return results
            
        # We sample a few typical pages in the middle of the chapter
        # For BAB 3.pdf, let's use page 2 (index 1)
        # For the final document, let's use page 25 (index 24) or page 30 (index 29) to be in Section 2 (the main body)
        sample_page_idx = 1 if name == "Reference (BAB 3.pdf)" else 29
        
        if sample_page_idx >= len(pdf.pages):
            sample_page_idx = 0
            
        page = pdf.pages[sample_page_idx]
        results['width_pt'] = float(page.width)
        results['height_pt'] = float(page.height)
        results['width_cm'] = float(page.width) / 28.346
        results['height_cm'] = float(page.height) / 28.346
        
        chars = page.chars
        if not chars:
            return results
            
        # Extract fonts and sizes
        fonts = set()
        font_sizes = set()
        for c in chars:
            fonts.add(c.get('fontname', ''))
            font_sizes.add(round(c.get('size', 0), 2))
        results['fonts'] = list(fonts)
        results['font_sizes'] = sorted(list(font_sizes))
        
        # Detect lines
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
                'text': l_text, 'x0': l_x0, 'x1': l_x1, 'top': l_top, 'bottom': l_bottom, 'font': l_font, 'size': l_size
            })
            
        # Spacing
        spacings = []
        for i in range(len(line_details) - 1):
            ld1 = line_details[i]
            ld2 = line_details[i+1]
            if abs(ld1['size'] - 12.0) < 1.0 and abs(ld2['size'] - 12.0) < 1.0:
                dist = ld2['top'] - ld1['top']
                if 12.0 < dist < 40.0:
                    spacings.append(dist)
        results['avg_spacing_pt'] = sum(spacings) / len(spacings) if spacings else 0.0
        results['avg_spacing_ratio'] = results['avg_spacing_pt'] / 12.0
        
        # Margins
        body_lines_x0 = [ld['x0'] for ld in line_details if abs(ld['size'] - 12.0) < 1.0 and 'Bold' not in ld['font']]
        if body_lines_x0:
            results['left_margin_pt'] = min(body_lines_x0)
            results['left_margin_cm'] = results['left_margin_pt'] / 28.346
            
            indented_x0s = [x for x in body_lines_x0 if x > results['left_margin_pt'] + 15.0]
            if indented_x0s:
                results['first_line_indent_pt'] = min(indented_x0s) - results['left_margin_pt']
                results['first_line_indent_cm'] = results['first_line_indent_pt'] / 28.346
            else:
                results['first_line_indent_pt'] = 0.0
                results['first_line_indent_cm'] = 0.0
                
        body_lines_x1 = [ld['x1'] for ld in line_details if abs(ld['size'] - 12.0) < 1.0 and 'Bold' not in ld['font']]
        if body_lines_x1:
            max_x1 = max(body_lines_x1)
            results['right_margin_pt'] = results['width_pt'] - max_x1
            results['right_margin_cm'] = results['right_margin_pt'] / 28.346
            
        body_tops = [ld['top'] for ld in line_details if ld['top'] > 80.0]
        if body_tops:
            results['top_margin_pt'] = min(body_tops)
            results['top_margin_cm'] = results['top_margin_pt'] / 28.346
            
        body_bottoms = [ld['bottom'] for ld in line_details if ld['bottom'] < results['height_pt'] - 50.0]
        if body_bottoms:
            results['bottom_margin_pt'] = results['height_pt'] - max(body_bottoms)
            results['bottom_margin_cm'] = results['bottom_margin_pt'] / 28.346
            
    return results

def main():
    pdf_ref = "BAB 3.pdf"
    pdf_formatted = "Tugas_Akhir_Formatted.pdf"
    
    print("=== FORMATTING COMPARISON ===")
    ref_res = analyze_pdf_properties(pdf_ref, "Reference (BAB 3.pdf)")
    fmt_res = analyze_pdf_properties(pdf_formatted, "Formatted (Tugas_Akhir_Formatted.pdf)")
    
    if not ref_res:
        print(f"Error: Could not load reference {pdf_ref}")
        return
    if not fmt_res:
        print(f"Error: Could not load formatted {pdf_formatted}")
        return
        
    print(f"{'Property':<30} | {'Reference (BAB 3.pdf)':<25} | {'Formatted (Tugas Akhir)':<25}")
    print("-" * 88)
    
    print(f"{'Page Size':<30} | {ref_res['width_cm']:.1f} x {ref_res['height_cm']:.1f} cm (A4) | {fmt_res['width_cm']:.1f} x {fmt_res['height_cm']:.1f} cm (A4)")
    print(f"{'Left Margin':<30} | {ref_res['left_margin_cm']:.2f} cm ({ref_res['left_margin_pt']:.1f} pt) | {fmt_res['left_margin_cm']:.2f} cm ({fmt_res['left_margin_pt']:.1f} pt)")
    print(f"{'Right Margin (approx)':<30} | {ref_res['right_margin_cm']:.2f} cm ({ref_res['right_margin_pt']:.1f} pt) | {fmt_res['right_margin_cm']:.2f} cm ({fmt_res['right_margin_pt']:.1f} pt)")
    print(f"{'Top Margin (approx)':<30} | {ref_res['top_margin_cm']:.2f} cm ({ref_res['top_margin_pt']:.1f} pt) | {fmt_res['top_margin_cm']:.2f} cm ({fmt_res['top_margin_pt']:.1f} pt)")
    print(f"{'Bottom Margin (approx)':<30} | {ref_res['bottom_margin_cm']:.2f} cm ({ref_res['bottom_margin_pt']:.1f} pt) | {fmt_res['bottom_margin_cm']:.2f} cm ({fmt_res['bottom_margin_pt']:.1f} pt)")
    print(f"{'Line Spacing (Ratio)':<30} | {ref_res['avg_spacing_pt']:.2f} pt ({ref_res['avg_spacing_ratio']:.2f}x) | {fmt_res['avg_spacing_pt']:.2f} pt ({fmt_res['avg_spacing_ratio']:.2f}x)")
    print(f"{'First Line Indent':<30} | {ref_res['first_line_indent_cm']:.2f} cm ({ref_res['first_line_indent_pt']:.1f} pt) | {fmt_res['first_line_indent_cm']:.2f} cm ({fmt_res['first_line_indent_pt']:.1f} pt)")
    
    print("\nReference Fonts:", ref_res.get('fonts', []))
    print("Formatted Fonts:", fmt_res.get('fonts', []))
    print("Reference Font Sizes:", ref_res.get('font_sizes', []))
    print("Formatted Font Sizes:", fmt_res.get('font_sizes', []))

if __name__ == '__main__':
    main()
