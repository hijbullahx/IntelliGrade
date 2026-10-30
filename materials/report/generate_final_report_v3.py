# -*- coding: utf-8 -*-
"""
generate_final_report_v3.py
Complete master automation script to finalize:
Practicum_Soft_Report_Template_DAS(v3).docx & .pdf
Matching the exact layout, page numbering, dot leaders, captions, and referencing
from the sample reference PDF (A_Practicum Report_Md Minhazul Islam.pdf(Sample).pdf).
"""

import os
import shutil
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import win32com.client as win32
import pythoncom
import fitz

def main():
    base_dir = r'D:\Projects\IntelliGrade\Materials\report'
    src_v2 = os.path.join(base_dir, 'Practicum_Soft_Report_Template_DAS(v2).docx')
    dst_v3 = os.path.join(base_dir, 'Practicum_Soft_Report_Template_DAS(v3).docx')
    dst_pdf = os.path.join(base_dir, 'Practicum_Soft_Report_Template_DAS(v3).pdf')

    remote_dir = r'Q:\My Drive\Practicum\IntelliGrade\Presentation and Report\Report'
    remote_v3 = os.path.join(remote_dir, 'Practicum_Soft_Report_Template_DAS(v3).docx')
    remote_pdf = os.path.join(remote_dir, 'Practicum_Soft_Report_Template_DAS(v3).pdf')

    print("Step 1: Loading v2 docx and structuring sections...")
    doc = Document(src_v2)

    # 1. Restructure sections
    transmittal_idx = None
    ch1_idx = None
    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if t == "Letter of Transmittal" and transmittal_idx is None:
            transmittal_idx = i
        if "Chapter 1." in t and ch1_idx is None:
            ch1_idx = i

    p43 = doc.paragraphs[transmittal_idx - 1]
    p67 = doc.paragraphs[67]
    p95 = doc.paragraphs[95]

    # Move sectPr from P[67] to P[43]
    sectPr_67_list = p67._p.xpath('./w:pPr/w:sectPr')
    if sectPr_67_list:
        p67._p.pPr.remove(sectPr_67_list[0])
        p43._p.get_or_add_pPr().append(sectPr_67_list[0])

    # Remove sectPr from P[95]
    sectPr_95_list = p95._p.xpath('./w:pPr/w:sectPr')
    if sectPr_95_list:
        p95._p.pPr.remove(sectPr_95_list[0])

    # Save to intermediate v3
    doc.save(dst_v3)
    doc = Document(dst_v3)
    print(f"Verified sections count: {len(doc.sections)}")

    # 2. Configure page numbering and headers/footers
    for i, s in enumerate(doc.sections):
        s.different_first_page_header_footer = False
        s.header.is_linked_to_previous = False
        s.footer.is_linked_to_previous = False
        for p in s.header.paragraphs:
            p.text = ''

        if i == 0: # Section 0: Cover & Approval
            for p in s.footer.paragraphs:
                p.text = ''
            for pnt in s._sectPr.xpath('./w:pgNumType'):
                s._sectPr.remove(pnt)
        elif i == 1: # Section 1: Front Matter (iii, iv, ...)
            f = s.footer.paragraphs[0]
            f.text = ''
            f.alignment = WD_ALIGN_PARAGRAPH.CENTER
            f._p.append(parse_xml('<w:fldSimple ' + nsdecls('w') + ' w:instr="PAGE"/>'))
            for p in s.footer.paragraphs[1:]:
                p.text = ''
            for pnt in s._sectPr.xpath('./w:pgNumType'):
                s._sectPr.remove(pnt)
            pgNumType1 = OxmlElement('w:pgNumType')
            pgNumType1.set(qn('w:fmt'), 'lowerRoman')
            pgNumType1.set(qn('w:start'), '3')
            cols1 = s._sectPr.xpath('./w:cols')
            if cols1:
                cols1[0].addprevious(pgNumType1)
            else:
                s._sectPr.append(pgNumType1)
        elif i == 2: # Section 2: Main Body (1, 2, ...)
            f = s.footer.paragraphs[0]
            f.text = ''
            f.alignment = WD_ALIGN_PARAGRAPH.CENTER
            f._p.append(parse_xml('<w:fldSimple ' + nsdecls('w') + ' w:instr="PAGE"/>'))
            for p in s.footer.paragraphs[1:]:
                p.text = ''
            for pnt in s._sectPr.xpath('./w:pgNumType'):
                s._sectPr.remove(pnt)
            pgNumType2 = OxmlElement('w:pgNumType')
            pgNumType2.set(qn('w:fmt'), 'decimal')
            pgNumType2.set(qn('w:start'), '1')
            cols2 = s._sectPr.xpath('./w:cols')
            if cols2:
                cols2[0].addprevious(pgNumType2)
            else:
                s._sectPr.append(pgNumType2)

    # 3. Format front matter headings and enforce page breaks
    fm_headings = [
        "Letter of Transmittal",
        "Supervisor’s Certification",
        "Supervisor's Certification",
        "Abstract"
    ]
    for p in doc.paragraphs:
        txt = p.text.strip()
        if txt in fm_headings:
            try:
                p.style = doc.styles['Heading 2']
            except Exception:
                pass
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(14)
                r.font.bold = True
                r.font.color.rgb = RGBColor(0, 0, 0)

    # Explicit page_break_before on major front matter & chapters
    page_break_headings = [
        "Organization’s Certificate",
        "Organization's Certificate",
        "Student’s Declaration",
        "Student's Declaration",
        "Supervisor’s Certification",
        "Supervisor's Certification",
        "Abstract",
        "Acknowledgments",
        "Table of Contents",
        "List of Figures",
        "List of Tables",
        "Chapter 1. Introduction",
        "Chapter 2. Organizational Overview",
        "Chapter 3. Requirement Engineering",
        "Chapter 4. System Analysis and Design",
        "Chapter 5. Software Risk Management",
        "Chapter 6. Project Planning and Scheduling",
        "Chapter 7. Cost Estimation",
        "Chapter 8. System Architecture and Implementation",
        "Chapter 9. Software Testing",
        "Chapter 10. Conclusions and Future Enhancements",
        "References",
        "Plagiarism Report"
    ]
    for p in doc.paragraphs:
        txt = p.text.strip()
        for pbh in page_break_headings:
            if txt == pbh or (pbh.startswith("Chapter ") and txt.startswith(pbh[:9])):
                p.paragraph_format.page_break_before = True
                break

    # 4. Normalize body figure captions (all 29 figures)
    figure_norm_map = [
        ("Figure 1.0.1", "Figure 1.1 Agile Iterative Development Model"),
        ("Figure 2.0.1", "Figure 2.1 Organizational Structure of Al Hadi Enterprise and Software Development Team"),
        ("Figure 3.0.1", "Figure 3.1 Use Case Diagram of IntelliGrade"),
        ("Figure 4.0.1", "Figure 4.1 Activity Diagram: Exam Controller Governance Workflow"),
        ("Figure 4.0.2", "Figure 4.2 Activity Diagram: Examination Scheduling and Provisioning (AI Routine Scan vs. Manual Entry)"),
        ("Figure 4.0.3", "Figure 4.3 Activity Diagram: Faculty/Examiner Workflow"),
        ("Figure 4.0.4", "Figure 4.4 Activity Diagram: Question Paper and Rubric Authoring (AI Document Scan vs. Manual Builder)"),
        ("Figure 4.0.5", "Figure 4.5 Activity Diagram: AI Evaluation Wizard Flow"),
        ("Figure 4.0.6", "Figure 4.6 Activity Diagram: OBE Tabulation & Calculation"),
        ("Figure 4.0.7", "Figure 4.7 Activity Diagram: Department Head Governance"),
        ("Figure 4.0.8", "Figure 4.8 Activity Diagram: Student Academic Transparency Portal"),
        ("Figure 4.0.9", "Figure 4.9 Swim-lane Diagram for User Authentication & Role-Based Access Control"),
        ("Figure 4.10", "Figure 4.10 Swim-lane Diagram for Examination Scheduling & Faculty Allocation"),
        ("Figure 4.12", "Figure 4.11 Swim-lane Diagram for Answer Script Evaluation & Teacher Finalization"),
        ("Figure 4.13", "Figure 4.12 Swim-lane Diagram for OBE Tabulation, Excel Export & Student Result Dissemination"),
        ("Figure 4.14", "Figure 4.13 Class Diagram: Core Domain Models"),
        ("Figure 6.1", "Figure 6.1 Gantt Chart: Project Schedule"),
        ("Figure 8.1", "Figure 8.1 System Architecture Overview Diagram (4-Tier)"),
        ("Figure 8.2", "Figure 8.2 Data Flow Diagram \u2013 Level 0 (Context Diagram)"),
        ("Figure 8.3", "Figure 8.3 Data Flow Diagram \u2013 Level 1 (System Level)"),
        ("Figure 8.4", "Figure 8.4 Entity-Relationship Diagram (ERD)"),
        ("Figure 8.5", "Figure 8.5 UI Mockup: Landing Page & Portal Selector"),
        ("Figure 8.6", "Figure 8.6 UI Mockup: Exam Controller Governance Dashboard"),
        ("Figure 8.7", "Figure 8.7 UI Mockup: AI Routine Scanner & Scheduler"),
        ("Figure 8.8", "Figure 8.8 UI Mockup: AI Evaluation Wizard & Script Upload"),
        ("Figure 8.9", "Figure 8.9 UI Mockup: Split-Screen Teacher Grading Workbench"),
        ("Figure 8.10", "Figure 8.10 UI Mockup: Course OBE Tabulation View"),
        ("Figure 8.11", "Figure 8.11 UI Mockup: Student Transparency Dashboard"),
        ("Figure 8.12", "Figure 8.12 UI Mockup: Department Head Analytics Dashboard"),
    ]

    for i in range(183, len(doc.paragraphs)):
        p = doc.paragraphs[i]
        txt = p.text.strip()
        for prefix, target_text in figure_norm_map:
            if txt.startswith(prefix):
                p.text = target_text
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(6)
                p.paragraph_format.space_after = Pt(12)
                for r in p.runs:
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(12)
                    r.font.bold = True
                    r.font.color.rgb = RGBColor(0, 0, 0)
                break

    # 5. Normalize body table captions (all 39 tables)
    table_norm_map = [
        ("Table 4.1", "Table 4.1 CRC Card: Profile (User Role)"),
        ("Table 4.2", "Table 4.2 CRC Card: Examination"),
        ("Table 4.3", "Table 4.3 CRC Card: Question"),
        ("Table 4.4", "Table 4.4 CRC Card: StudentSubmission"),
        ("Table 4.5", "Table 4.5 CRC Card: EvaluationResult"),
        ("Table 4.6", "Table 4.6 CRC Card: CourseTabulation"),
        ("Table 4.7", "Table 4.7 CRC Card: StudentGradeRecord"),
        ("Table 5.1", "Table 5.1 Risk Identification"),
        ("Table 5.2", "Table 5.2 Risk Analysis"),
        ("Table 5.3", "Table 5.3 RMMM: Risk 1 \u2013 CPU OCR Latency"),
        ("Table 5.4", "Table 5.4 RMMM: Risk 2 \u2013 AI Rate Limiting"),
        ("Table 5.5", "Table 5.5 RMMM: Risk 3 \u2013 Handwriting Illegibility"),
        ("Table 5.6", "Table 5.6 RMMM: Risk 4 \u2013 Data Loss During Evaluation"),
        ("Table 5.7", "Table 5.7 RMMM: Risk 5 \u2013 SMTP Email Delivery Failure"),
        ("Table 5.8", "Table 5.8 RMMM: Risk 6 \u2013 Disk Storage Overflow"),
        ("Table 5.9", "Table 5.9 Risk 7 \u2013 OBE Calculation Inconsistency"),
        ("Table 6.1", "Table 6.1 Functionality, Input and Output"),
        ("Table 6.2", "Table 6.2 Complexity of Data Function"),
        ("Table 6.3", "Table 6.3 Complexity of Transaction Function"),
        ("Table 6.4", "Table 6.4 UFP Calculation Summary"),
        ("Table 6.5", "Table 6.5 Technical Difficulty Index (TDI)"),
        ("Table 7.1", "Table 7.1 Personnel Salary"),
        ("Table 7.2", "Table 7.2 Personnel Cost Estimation"),
        ("Table 7.3", "Table 7.3 Hardware Cost"),
        ("Table 7.4", "Table 7.4 Software Cost"),
        ("Table 7.5", "Table 7.5 Other Operational Costs"),
        ("Table 7.6", "Table 7.6 Total Project Cost Summary"),
        ("Table 8.1", "Table 8.1 Technology Stack Details"),
        ("Table 8.2", "Table 8.2 Core Database Schema"),
        ("Table 8.3", "Table 8.3 REST and AJAX API Catalog"),
        ("Table 9.1", "Table 9.1 Test Case 1: User Login and Role-Based Dispatch"),
        ("Table 9.2", "Table 9.2 Test Case 2: AI Exam Routine Scanning"),
        ("Table 9.3", "Table 9.3 Test Case 3: Question Paper Studio \u2013 23-Taxonomy Entry"),
        ("Table 9.4", "Table 9.4 Test Case 4: Script Upload and 300 DPI Preprocessing"),
        ("Table 9.5", "Table 9.5 Test Case 5: AI Evaluation Wizard \u2013 End-to-End"),
        ("Table 9.6", "Table 9.6 Test Case 6: Manual Script Grading Wizard"),
        ("Table 9.7", "Table 9.7 Test Case 7: Teacher Mark Override and Audit Log"),
        ("Table 9.8", "Table 9.8 Test Case 8: OBE Tabulation and Excel Export"),
        ("Table 9.9", "Table 9.9 Test Case 9: Student Dashboard \u2013 Grade Transparency"),
    ]

    for i in range(183, len(doc.paragraphs)):
        p = doc.paragraphs[i]
        txt = p.text.strip()
        for prefix, target_text in table_norm_map:
            if txt.startswith(prefix):
                p.text = target_text
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(12)
                p.paragraph_format.space_after = Pt(6)
                for r in p.runs:
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(12)
                    r.font.bold = True
                    r.font.color.rgb = RGBColor(0, 0, 0)
                break

    # 6. Format References with 0.5-inch hanging indent
    ref_idx = None
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip().lower() == 'references':
            ref_idx = i
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            try:
                p.style = doc.styles['Heading 2']
            except Exception:
                pass
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(14)
                r.font.bold = True
            break

    if ref_idx is not None:
        for j in range(ref_idx + 1, len(doc.paragraphs)):
            p = doc.paragraphs[j]
            t = p.text.strip()
            if t == "Plagiarism Report" or p.style.name.startswith("Heading 1"):
                break
            if t:
                p.paragraph_format.left_indent = Inches(0.5)
                p.paragraph_format.first_line_indent = Inches(-0.5)
                p.paragraph_format.space_after = Pt(6)
                p.paragraph_format.line_spacing = 1.15
                for r in p.runs:
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(12)

    doc.save(dst_v3)
    print("Step 2: Saved v3 baseline with formatted captions and sections.")

    # Step 3: Run Word COM to get exact page numbers
    print("Step 3: Opening Word COM to paginate and read exact page numbers...")
    pythoncom.CoInitialize()
    word = win32.Dispatch('Word.Application')
    word.Visible = False
    word.DisplayAlerts = False

    fig_pages = {}
    tbl_pages = {}

    try:
        wdoc = word.Documents.Open(os.path.abspath(dst_v3))
        wdoc.Fields.Update()
        if wdoc.TablesOfContents.Count > 0:
            wdoc.TablesOfContents(1).Update()

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

        wdoc.Close(True)
    finally:
        word.Quit()

    print(f"Collected exact page numbers: {len(fig_pages)} figures, {len(tbl_pages)} tables.")

    # Step 4: Populate List of Figures and List of Tables with dot leaders
    print("Step 4: Populating List of Figures and List of Tables in v3 docx...")
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
    print("Step 4 complete: Saved docx with synchronized List of Figures and Tables.")

    # Step 5: Final Word COM TOC Update & Export to PDF
    print("Step 5: Updating TOC and Exporting to PDF via Word COM...")
    word = win32.Dispatch('Word.Application')
    word.Visible = False
    word.DisplayAlerts = False
    try:
        wdoc = word.Documents.Open(os.path.abspath(dst_v3))
        wdoc.Fields.Update()
        if wdoc.TablesOfContents.Count > 0:
            wdoc.TablesOfContents(1).Update()
        wdoc.Save()
        wdoc.ExportAsFixedFormat(os.path.abspath(dst_pdf), 17) # 17 = wdExportFormatPDF
        wdoc.Close(False)
    finally:
        word.Quit()
    print("Step 5 complete: PDF exported successfully.")

    # Step 6: Deploy to Google Drive
    print("Step 6: Copying finalized (v3) files to Google Drive...")
    if os.path.exists(remote_dir):
        shutil.copyfile(dst_v3, remote_v3)
        shutil.copyfile(dst_pdf, remote_pdf)
        print("Copied both v3 docx and pdf to Google Drive successfully!")
    else:
        print("Google Drive directory not accessible.")

    # Step 7: Verify final PDF with PyMuPDF
    print("Step 7: Verifying exported PDF with PyMuPDF...")
    pdf = fitz.open(dst_pdf)
    print(f"Total pages in finalized PDF: {len(pdf)}")
    print("Sample page footers:")
    for pno in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 13, 15, 17, len(pdf)-1]:
        if pno < len(pdf):
            p = pdf[pno]
            footers = [b[4].strip() for b in p.get_text('blocks') if b[1] > 720 and b[4].strip()]
            first_text = [b[4].strip() for b in p.get_text('blocks') if b[1] < 200 and b[4].strip()]
            header_str = first_text[0][:30] if first_text else "EMPTY"
            print(f"  Page {pno+1}: Footer={footers}, Top='{header_str}'")

    print("\nALL AUTOMATION TASKS COMPLETED SUCCESSFULLY!")

if __name__ == '__main__':
    main()
