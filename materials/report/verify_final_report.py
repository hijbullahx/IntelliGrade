import fitz
import os

pdf_path = r'D:\Projects\IntelliGrade\Materials\report\Practicum_Soft_Report_Template_DAS(v3).pdf'
doc = fitz.open(pdf_path)

print(f"=== FINAL PDF VERIFICATION REPORT ===")
print(f"File: {pdf_path}")
print(f"Total Pages: {len(doc)}\n")

# 1. Front matter pages (Pages 1 to 18)
print("--- 1. Front Matter Page Numbers (Bottom Center) ---")
for pno in range(18):
    p = doc[pno]
    footers = [b[4].strip() for b in p.get_text('blocks') if b[1] > 720 and b[4].strip()]
    headers = [b[4].strip() for b in p.get_text('blocks') if b[1] < 60 and b[4].strip()]
    first_title = [b[4].strip() for b in p.get_text('blocks') if 60 <= b[1] <= 180 and b[4].strip()]
    title_str = first_title[0].replace('\n', ' ')[:45] if first_title else "N/A"
    print(f"  Page {pno+1:2d}: Footer={repr(footers):10s} Header={repr(headers):8s} Title='{title_str}'")

# 2. Main body sample pages (Page 18 onwards)
print("\n--- 2. Main Body Sample Pages ---")
for pno in [17, 18, 19, 20, 50, 80, 100, len(doc)-1]:
    p = doc[pno]
    footers = [b[4].strip() for b in p.get_text('blocks') if b[1] > 720 and b[4].strip()]
    headers = [b[4].strip() for b in p.get_text('blocks') if b[1] < 60 and b[4].strip()]
    first_title = [b[4].strip() for b in p.get_text('blocks') if 60 <= b[1] <= 180 and b[4].strip()]
    title_str = first_title[0].replace('\n', ' ')[:45] if first_title else "N/A"
    print(f"  Page {pno+1:3d}: Footer={repr(footers):8s} Header={repr(headers):8s} Title='{title_str}'")

# 3. Check Google Drive sync
print("\n--- 3. Google Drive Sync Status ---")
q_docx = r'Q:\My Drive\Practicum\IntelliGrade\Presentation and Report\Report\Practicum_Soft_Report_Template_DAS(v3).docx'
q_pdf = r'Q:\My Drive\Practicum\IntelliGrade\Presentation and Report\Report\Practicum_Soft_Report_Template_DAS(v3).pdf'
print(f"Q: docx exists: {os.path.exists(q_docx)} (Size: {os.path.getsize(q_docx) if os.path.exists(q_docx) else 0} bytes)")
print(f"Q: pdf exists:  {os.path.exists(q_pdf)} (Size: {os.path.getsize(q_pdf) if os.path.exists(q_pdf) else 0} bytes)")

