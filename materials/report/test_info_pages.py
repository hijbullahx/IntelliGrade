import win32com.client as win32
import pythoncom
import os

pythoncom.CoInitialize()
word = win32.Dispatch('Word.Application')
word.Visible = False
word.DisplayAlerts = False

try:
    doc_path = os.path.abspath(r'D:\Projects\IntelliGrade\Materials\report\Practicum_Soft_Report_Template_DAS(v3).docx')
    doc = word.Documents.Open(doc_path)
    print("Opened v3 docx.")
    print("Total pages in doc:", doc.ComputeStatistics(2)) # 2 = wdStatisticPages
    
    # Check Information constants on Chapter 1 and a few captions
    found = 0
    for i in range(1, doc.Paragraphs.Count + 1):
        p = doc.Paragraphs(i)
        t = p.Range.Text.strip()
        if t.startswith("Chapter 1.") or t.startswith("Figure 1.1") or t.startswith("Table 4.1") or t.startswith("Figure 8.1"):
            p1 = p.Range.Information(1) # wdActiveEndAdjustedPageNumber
            p3 = p.Range.Information(3) # wdActiveEndPageNumber
            print(f"P[{i}]: '{t[:40]}' -> Info(1)={p1}, Info(3)={p3}")
            found += 1
            if found >= 6:
                break
    doc.Close(False)
finally:
    word.Quit()

