import os
import sys

def main():
    pdf_path = "BAB 3.pdf"
    if not os.path.exists(pdf_path):
        print(f"File {pdf_path} not found.")
        sys.exit(1)
        
    print("PDF File exists. Checking pypdf and pdfplumber...")
    
    try:
        import pypdf
        print("pypdf version:", pypdf.__version__)
    except ImportError:
        print("pypdf not installed.")
        
    try:
        import pdfplumber
        print("pdfplumber installed.")
    except ImportError:
        print("pdfplumber not installed.")
        
    # Let's write code to extract properties
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            print("Total pages:", len(pdf.pages))
            if len(pdf.pages) > 0:
                page = pdf.pages[0]
                print("Page width:", page.width)
                print("Page height:", page.height)
                
                # Check margins by looking at bbox of characters
                chars = page.chars
                if chars:
                    x0s = [c['x0'] for c in chars]
                    x1s = [c['x1'] for c in chars]
                    top_coords = [c['top'] for c in chars]
                    bottom_coords = [c['bottom'] for c in chars]
                    
                    min_x = min(x0s)
                    max_x = max(x1s)
                    min_t = min(top_coords)
                    max_b = max(bottom_coords)
                    
                    # Page margins in points (1 inch = 72 points, 1 cm = 28.346 points)
                    margin_left = min_x
                    margin_right = float(page.width) - max_x
                    margin_top = min_t
                    margin_bottom = float(page.height) - max_b
                    
                    print(f"Leftmost char x0: {min_x:.2f}pt ({min_x/28.346:.2f} cm)")
                    print(f"Rightmost char x1: {max_x:.2f}pt (Margin Right: {margin_right:.2f}pt / {margin_right/28.346:.2f} cm)")
                    print(f"Topmost char top: {min_t:.2f}pt ({min_t/28.346:.2f} cm)")
                    print(f"Bottommost char bottom: {max_b:.2f}pt (Margin Bottom: {margin_bottom:.2f}pt / {margin_bottom/28.346:.2f} cm)")
                    
                    # Fonts
                    fonts = set()
                    font_sizes = set()
                    for c in chars[:200]: # Sample first 200 chars
                        fonts.add(c.get('fontname', ''))
                        font_sizes.add(round(c.get('size', 0), 2))
                    print("Sample fonts:", fonts)
                    print("Sample font sizes:", font_sizes)
    except Exception as e:
        print("Error during inspection:", e)

if __name__ == "__main__":
    main()
