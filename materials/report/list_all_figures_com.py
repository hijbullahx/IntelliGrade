import win32com.client as win32
import pythoncom
import os

pythoncom.CoInitialize()
word = win32.Dispatch('Word.Application')
word.Visible = False
word.DisplayAlerts = False

try:
    doc_path = os.path.abspath(r'D:\Projects\IntelliGrade\Materials\report\test_clean_fixed_first.docx')
    doc = word.Documents.Open(doc_path)
    
    sec3 = doc.Sections(3)
    figures = []
    for p in sec3.Range.Paragraphs:
        t = p.Range.Text.strip()
        if t.startswith("Figure ") and len(t) > 10:
            pg = p.Range.Information(1)
            figures.append((t, pg))
            
    print(f"Total figures: {len(figures)}")
    for i, f in enumerate(figures):
        print(f"  {i+1}: {f[0]} -> Page {f[1]}")
        
    doc.Close(False)
finally:
    word.Quit()

