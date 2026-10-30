import win32com.client as win32
import pythoncom
import os
import docx
from docx import Document
from docx.shared import Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import fitz
import shutil

base_dir = r'D:\Projects\IntelliGrade\Materials\report'
dst_v3 = os.path.join(base_dir, 'Practicum_Soft_Report_Template_DAS(v3).docx')
dst_pdf = os.path.join(base_dir, 'Practicum_Soft_Report_Template_DAS(v3).pdf')
remote_dir = r'Q:\My Drive\Practicum\IntelliGrade\Presentation and Report\Report'
remote_v3 = os.path.join(remote_dir, 'Practicum_Soft_Report_Template_DAS(v3).docx')
remote_pdf = os.path.join(remote_dir, 'Practicum_Soft_Report_Template_DAS(v3).pdf')

# 1. Open current v3 in Word COM to get exact current page numbers of all figures & tables
pythoncom.CoInitialize()
word = win32.Dispatch('Word.Application')
word.Visible = False
word.DisplayAlerts = False

fig_pages = {}
tbl_pages = {}

try:
    wdoc = word.Documents.Open(os.path.abspath(dst_v3))
    sec3 = wdoc.Sections(3)
    for p in sec3.Range.Paragraphs:
        t = p.Range.Text.strip()
        if t.startswith("Figure "):
            parts = t.split()
            if len(parts) >= 2:
                key = f"{parts[0]} {parts[1]}"
                pg = p.Range.Information(1)
                if key not in fig_pages:
                    fig_pages[key] = pg
        elif t.startswith("Table "):
            parts = t.split()
            if len(parts) >= 2:
                key = f"{parts[0]} {parts[1]}"
                pg = p.Range.Information(1)
                if key not in tbl_pages:
                    tbl_pages[key] = pg
    wdoc.Close(False)
finally:
    word.Quit()

print(f"Read current exact page numbers: {len(fig_pages)} figures, {len(tbl_pages)} tables.")

# 2. Update List of Figures and List of Tables in docx
doc = Document(dst_v3)
lof_idx = None
lot_idx = None
ch1_idx = None
for i, p in enumerate(doc.paragraphs):
    t = p.text.strip()
    if t == "List of Figures" and lof_idx is None:
        lof_idx = i
    elif t == "List of Tables" and lot_idx is None:
        lot_idx = i
    elif "Chapter 1." in t and ch1_idx is None:
        ch1_idx = i

def format_dot_leader_paragraph(p, title, page_num):
    p.text = ''
    pPr = p._p.get_or_add_pPr()
    for tabs_el in pPr.xpath('./w:tabs'):
        pPr.remove(tabs_el)
    tabs_el = OxmlElement('w:tabs')
    tab_el = OxmlElement('w:tab')
    tab_el.set(qn('w:val'), 'right')
    tab_el.set(qn('w:leader'), 'dot')
    tab_el.set(qn('w:pos'), '9000')
    tabs_el.append(tab_el)
    pPr.append(tabs_el)

    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15

    r1 = p.add_run(title)
    r1.font.name = 'Times New Roman'
    r1.font.size = Pt(12)
    r2 = p.add_run('\t')
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(12)
    r3 = p.add_run(str(page_num))
    r3.font.name = 'Times New Roman'
    r3.font.size = Pt(12)

figures_list = [
    ("Figure 1.1 Agile Iterative Development Model", fig_pages.get("Figure 1.1", 9)),
    ("Figure 2.1 Organizational Structure of Al Hadi Enterprise and Software Development Team", fig_pages.get("Figure 2.1", 15)),
    ("Figure 3.1 Use Case Diagram of IntelliGrade", fig_pages.get("Figure 3.1", 39)),
    ("Figure 4.1 Activity Diagram: Exam Controller Governance Workflow", fig_pages.get("Figure 4.1", 41)),
    ("Figure 4.2 Activity Diagram: Examination Scheduling and Provisioning (AI Routine Scan vs. Manual Entry)", fig_pages.get("Figure 4.2", 42)),
    ("Figure 4.3 Activity Diagram: Faculty/Examiner Workflow", fig_pages.get("Figure 4.3", 43)),
    ("Figure 4.4 Activity Diagram: Question Paper and Rubric Authoring (AI Document Scan vs. Manual Builder)", fig_pages.get("Figure 4.4", 44)),
    ("Figure 4.5 Activity Diagram: AI Evaluation Wizard Flow", fig_pages.get("Figure 4.5", 46)),
    ("Figure 4.6 Activity Diagram: OBE Tabulation & Calculation", fig_pages.get("Figure 4.6", 47)),
    ("Figure 4.7 Activity Diagram: Department Head Governance", fig_pages.get("Figure 4.7", 48)),
    ("Figure 4.8 Activity Diagram: Student Academic Transparency Portal", fig_pages.get("Figure 4.8", 48)),
    ("Figure 4.9 Swim-lane Diagram for User Authentication & Role-Based Access Control", fig_pages.get("Figure 4.9", 49)),
    ("Figure 4.10 Swim-lane Diagram for Examination Scheduling & Faculty Allocation", fig_pages.get("Figure 4.10", 49)),
    ("Figure 4.11 Swim-lane Diagram for Answer Script Evaluation & Teacher Finalization", fig_pages.get("Figure 4.11", 50)),
    ("Figure 4.12 Swim-lane Diagram for OBE Tabulation, Excel Export & Student Result Dissemination", fig_pages.get("Figure 4.12", 50)),
    ("Figure 4.13 Class Diagram: Core Domain Models", fig_pages.get("Figure 4.13", 56)),
    ("Figure 6.1 Gantt Chart: Project Schedule", fig_pages.get("Figure 6.1", 69)),
    ("Figure 8.1 System Architecture Overview Diagram (4-Tier)", fig_pages.get("Figure 8.1", 74)),
    ("Figure 8.2 Data Flow Diagram \u2013 Level 0 (Context Diagram)", fig_pages.get("Figure 8.2", 77)),
    ("Figure 8.3 Data Flow Diagram \u2013 Level 1 (System Level)", fig_pages.get("Figure 8.3", 77)),
    ("Figure 8.4 Entity-Relationship Diagram (ERD)", fig_pages.get("Figure 8.4", 78)),
    ("Figure 8.5 UI Mockup: Landing Page & Portal Selector", fig_pages.get("Figure 8.5", 82)),
    ("Figure 8.6 UI Mockup: Exam Controller Governance Dashboard", fig_pages.get("Figure 8.6", 83)),
    ("Figure 8.7 UI Mockup: AI Routine Scanner & Scheduler", fig_pages.get("Figure 8.7", 83)),
    ("Figure 8.8 UI Mockup: AI Evaluation Wizard & Script Upload", fig_pages.get("Figure 8.8", 84)),
    ("Figure 8.9 UI Mockup: Split-Screen Teacher Grading Workbench", fig_pages.get("Figure 8.9", 85)),
    ("Figure 8.10 UI Mockup: Course OBE Tabulation View", fig_pages.get("Figure 8.10", 86)),
    ("Figure 8.11 UI Mockup: Student Transparency Dashboard", fig_pages.get("Figure 8.11", 86)),
    ("Figure 8.12 UI Mockup: Department Head Analytics Dashboard", fig_pages.get("Figure 8.12", 87)),
]

for idx, (title, page) in enumerate(figures_list):
    p_idx = lof_idx + 1 + idx
    format_dot_leader_paragraph(doc.paragraphs[p_idx], title, page)

for extra_p in range(lof_idx + 1 + len(figures_list), lot_idx):
    doc.paragraphs[extra_p].text = ''

tables_list = [
    ("Table 4.1 CRC Card: Profile (User Role)", tbl_pages.get("Table 4.1", 51)),
    ("Table 4.2 CRC Card: Examination", tbl_pages.get("Table 4.2", 51)),
    ("Table 4.3 CRC Card: Question", tbl_pages.get("Table 4.3", 52)),
    ("Table 4.4 CRC Card: StudentSubmission", tbl_pages.get("Table 4.4", 52)),
    ("Table 4.5 CRC Card: EvaluationResult", tbl_pages.get("Table 4.5", 53)),
    ("Table 4.6 CRC Card: CourseTabulation", tbl_pages.get("Table 4.6", 54)),
    ("Table 4.7 CRC Card: StudentGradeRecord", tbl_pages.get("Table 4.7", 54)),
    ("Table 5.1 Risk Identification", tbl_pages.get("Table 5.1", 57)),
    ("Table 5.2 Risk Analysis", tbl_pages.get("Table 5.2", 58)),
    ("Table 5.3 RMMM: Risk 1 \u2013 CPU OCR Latency", tbl_pages.get("Table 5.3", 59)),
    ("Table 5.4 RMMM: Risk 2 \u2013 AI Rate Limiting", tbl_pages.get("Table 5.4", 60)),
    ("Table 5.5 RMMM: Risk 3 \u2013 Handwriting Illegibility", tbl_pages.get("Table 5.5", 61)),
    ("Table 5.6 RMMM: Risk 4 \u2013 Data Loss During Evaluation", tbl_pages.get("Table 5.6", 61)),
    ("Table 5.7 RMMM: Risk 5 \u2013 SMTP Email Delivery Failure", tbl_pages.get("Table 5.7", 62)),
    ("Table 5.8 RMMM: Risk 6 \u2013 Disk Storage Overflow", tbl_pages.get("Table 5.8", 63)),
    ("Table 5.9 Risk 7 \u2013 OBE Calculation Inconsistency", tbl_pages.get("Table 5.9", 63)),
    ("Table 6.1 Functionality, Input and Output", tbl_pages.get("Table 6.1", 65)),
    ("Table 6.2 Complexity of Data Function", tbl_pages.get("Table 6.2", 66)),
    ("Table 6.3 Complexity of Transaction Function", tbl_pages.get("Table 6.3", 67)),
    ("Table 6.4 UFP Calculation Summary", tbl_pages.get("Table 6.4", 67)),
    ("Table 6.5 Technical Difficulty Index (TDI)", tbl_pages.get("Table 6.5", 68)),
    ("Table 7.1 Personnel Salary", tbl_pages.get("Table 7.1", 70)),
    ("Table 7.2 Personnel Cost Estimation", tbl_pages.get("Table 7.2", 70)),
    ("Table 7.3 Hardware Cost", tbl_pages.get("Table 7.3", 71)),
    ("Table 7.4 Software Cost", tbl_pages.get("Table 7.4", 71)),
    ("Table 7.5 Other Operational Costs", tbl_pages.get("Table 7.5", 71)),
    ("Table 7.6 Total Project Cost Summary", tbl_pages.get("Table 7.6", 72)),
    ("Table 8.1 Technology Stack Details", tbl_pages.get("Table 8.1", 74)),
    ("Table 8.2 Core Database Schema", tbl_pages.get("Table 8.2", 79)),
    ("Table 8.3 REST and AJAX API Catalog", tbl_pages.get("Table 8.3", 80)),
    ("Table 9.1 Test Case 1: User Login and Role-Based Dispatch", tbl_pages.get("Table 9.1", 88)),
    ("Table 9.2 Test Case 2: AI Exam Routine Scanning", tbl_pages.get("Table 9.2", 89)),
    ("Table 9.3 Test Case 3: Question Paper Studio \u2013 23-Taxonomy Entry", tbl_pages.get("Table 9.3", 90)),
    ("Table 9.4 Test Case 4: Script Upload and 300 DPI Preprocessing", tbl_pages.get("Table 9.4", 91)),
    ("Table 9.5 Test Case 5: AI Evaluation Wizard \u2013 End-to-End", tbl_pages.get("Table 9.5", 92)),
    ("Table 9.6 Test Case 6: Manual Script Grading Wizard", tbl_pages.get("Table 9.6", 93)),
    ("Table 9.7 Test Case 7: Teacher Mark Override and Audit Log", tbl_pages.get("Table 9.7", 94)),
    ("Table 9.8 Test Case 8: OBE Tabulation and Excel Export", tbl_pages.get("Table 9.8", 95)),
    ("Table 9.9 Test Case 9: Student Dashboard \u2013 Grade Transparency", tbl_pages.get("Table 9.9", 96)),
]

for idx, (title, page) in enumerate(tables_list):
    p_idx = lot_idx + 1 + idx
    format_dot_leader_paragraph(doc.paragraphs[p_idx], title, page)

for extra_p in range(lot_idx + 1 + len(tables_list), ch1_idx - 2):
    doc.paragraphs[extra_p].text = ''

doc.save(dst_v3)
print("Updated LOF & LOT in v3 docx.")

# 3. Final TOC update and PDF export
word = win32.Dispatch('Word.Application')
word.Visible = False
word.DisplayAlerts = False
try:
    wdoc = word.Documents.Open(os.path.abspath(dst_v3))
    wdoc.Fields.Update()
    if wdoc.TablesOfContents.Count > 0:
        wdoc.TablesOfContents(1).Update()
    wdoc.Save()
    wdoc.ExportAsFixedFormat(os.path.abspath(dst_pdf), 17)
    wdoc.Close(False)
finally:
    word.Quit()
print("Final TOC update and PDF export complete.")

# 4. Copy to Q drive
if os.path.exists(remote_dir):
    shutil.copyfile(dst_v3, remote_v3)
    shutil.copyfile(dst_pdf, remote_pdf)
    print("Copied finalized v3 docx and pdf to Google Drive!")

