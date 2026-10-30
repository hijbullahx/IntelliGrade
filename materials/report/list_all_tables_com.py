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
    tables = []
    for p in sec3.Range.Paragraphs:
        t = p.Range.Text.strip()
        if t.startswith("Table ") and len(t) > 5:
            pg = p.Range.Information(1)
            tables.append((t, pg))
            
    print(f"Total tables: {len(tables)}")
    for i, t in enumerate(tables):
        print(f"  {i+1}: {t[0]} -> Page {t[1]}")
        
    doc.Close(False)
finally:
    word.Quit()

