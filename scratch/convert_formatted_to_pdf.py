import win32com.client
import os
import sys

def main():
    doc_path = r"d:\Iman\Semester 7\Tugas Akhir\Tugas Akhir\document\Tugas_Akhir_Formatted.docx"
    pdf_path = r"d:\Iman\Semester 7\Tugas Akhir\Tugas Akhir\document\Tugas_Akhir_Formatted.pdf"
    
    # Ensure absolute paths
    doc_path = os.path.abspath(doc_path)
    pdf_path = os.path.abspath(pdf_path)
    
    print(f"Opening Word to convert {doc_path} -> {pdf_path}")
    
    if not os.path.exists(doc_path):
        print(f"Error: {doc_path} does not exist!")
        sys.exit(1)
        
    # Open word application
    word = None
    doc = None
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        
        print("Word application dispatched. Opening document...")
        doc = word.Documents.Open(doc_path)
        
        print("Document opened. Saving as PDF...")
        # 17 represents wdFormatPDF
        doc.SaveAs(pdf_path, FileFormat=17)
        print("Document saved successfully.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if doc:
            try:
                doc.Close(SaveChanges=0) # wdDoNotSaveChanges = 0
            except:
                pass
        if word:
            try:
                word.Quit()
            except:
                pass
                
    if os.path.exists(pdf_path):
        print(f"Success! PDF created. Size: {os.path.getsize(pdf_path)} bytes")
    else:
        print("Error: PDF was not found at the destination path even after execution.")
        sys.exit(1)

if __name__ == '__main__':
    main()
