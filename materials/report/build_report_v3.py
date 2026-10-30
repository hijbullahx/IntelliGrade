# -*- coding: utf-8 -*-
"""
build_report_v3.py
Transforms Practicum_Soft_Report_Template_DAS(v2).docx into (v3).docx
with perfect formatting matching the sample PDF:
1. 3 clean sections (Cover/Approval: no nums; Front matter: iii..; Main body: 1..)
2. Normalizes all Figure captions and Table captions
3. Sets up TOC, List of Figures, List of Tables with dot leaders
4. Formats References with 0.5 in hanging indent
"""

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import os

def create_report_v3():
    src_path = r'D:\Projects\IntelliGrade\Materials\report\Practicum_Soft_Report_Template_DAS(v2).docx'
    dst_path = r'D:\Projects\IntelliGrade\Materials\report\Practicum_Soft_Report_Template_DAS(v3).docx'

    doc = Document(src_path)
    print(f"Loaded v2 docx with {len(doc.paragraphs)} paragraphs and {len(doc.sections)} sections.")

    # -------------------------------------------------------------
    # 1. SECTION RESTRUCTURING
    # -------------------------------------------------------------
    # In v2, sectPr exists at P[67], P[95], P[181], and body.
    # We want:
    # Break 1 at P[43] (end of Cover/Approval, before Letter of Transmittal P[44])
    # Break 2 at P[181] (end of Front matter, before Chapter 1 P[183])
    # Body sectPr (end of Main body)

    # First, find Letter of Transmittal and Chapter 1
    transmittal_idx = None
    ch1_idx = None
    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if t == "Letter of Transmittal" and transmittal_idx is None:
            transmittal_idx = i
        if "Chapter 1." in t and ch1_idx is None:
            ch1_idx = i

    print(f"Transmittal at P[{transmittal_idx}], Chapter 1 at P[{ch1_idx}]")

    # Remove all existing paragraph-level sectPr
    for i, p in enumerate(doc.paragraphs):
        pPr = p._p.get_or_add_pPr()
        sectPr_list = pPr.xpath('./w:sectPr')
        for s in sectPr_list:
            pPr.remove(s)

    # Now add sectPr at transmittal_idx - 1 (P[43])
    # and at ch1_idx - 2 (P[181])
    break1_p = doc.paragraphs[transmittal_idx - 1]
    break2_p = doc.paragraphs[ch1_idx - 2]

    # Create sectPr for Break 1 (end of Section 0 / Cover & Approval)
    sectPr1 = OxmlElement('w:sectPr')
    # type newPage
    type_elem = OxmlElement('w:type')
    type_elem.set(qn('w:val'), 'nextPage')
    sectPr1.append(type_elem)
    # page size & margins matching standard
    pgSz = OxmlElement('w:pgSz')
    pgSz.set(qn('w:w'), '12240') # 8.5 in
    pgSz.set(qn('w:h'), '15840') # 11 in
    sectPr1.append(pgSz)
    pgMar = OxmlElement('w:pgMar')
    pgMar.set(qn('w:top'), '1440') # 1 in
    pgMar.set(qn('w:right'), '1440') # 1 in
    pgMar.set(qn('w:bottom'), '1440') # 1 in
    pgMar.set(qn('w:left'), '1800') # 1.25 in
    pgMar.set(qn('w:header'), '720')
    pgMar.set(qn('w:footer'), '720')
    sectPr1.append(pgMar)
    break1_p._p.get_or_add_pPr().append(sectPr1)

    # Create sectPr for Break 2 (end of Section 1 / Front matter)
    sectPr2 = OxmlElement('w:sectPr')
    type_elem2 = OxmlElement('w:type')
    type_elem2.set(qn('w:val'), 'nextPage')
    sectPr2.append(type_elem2)
    # pgNumType: lowerRoman starting at 3
    pgNumType2 = OxmlElement('w:pgNumType')
    pgNumType2.set(qn('w:fmt'), 'lowerRoman')
    pgNumType2.set(qn('w:start'), '3')
    sectPr2.append(pgNumType2)
    sectPr2.append(pgSz)
    sectPr2.append(pgMar)
    break2_p._p.get_or_add_pPr().append(sectPr2)

    # Configure Section 2 (Main body) in body sectPr
    body_sectPr = doc._body._element.xpath('./w:sectPr')[0]
    # Remove existing pgNumType if any in body_sectPr
    for pnt in body_sectPr.xpath('./w:pgNumType'):
        body_sectPr.remove(pnt)
    pgNumType3 = OxmlElement('w:pgNumType')
    pgNumType3.set(qn('w:fmt'), 'decimal')
    pgNumType3.set(qn('w:start'), '1')
    # Insert before cols or at beginning of sectPr
    cols = body_sectPr.xpath('./w:cols')
    if cols:
        cols[0].addprevious(pgNumType3)
    else:
        body_sectPr.insert(0, pgNumType3)

    # Save and reload doc to let python-docx parse the 3 sections properly
    doc.save(dst_path)
    doc = Document(dst_path)
    print(f"Restructured into {len(doc.sections)} sections successfully!")

    # Now configure Headers and Footers for each of the 3 sections:
    # Section 0: Cover & Approval
    sec0 = doc.sections[0]
    sec0.header.is_linked_to_previous = False
    sec0.footer.is_linked_to_previous = False
    for p in sec0.header.paragraphs:
        p.text = ''
    for p in sec0.footer.paragraphs:
        p.text = ''

    # Section 1: Front Matter
    sec1 = doc.sections[1]
    sec1.header.is_linked_to_previous = False
    sec1.footer.is_linked_to_previous = False
    for p in sec1.header.paragraphs:
        p.text = ''
    f_p1 = sec1.footer.paragraphs[0]
    f_p1.text = ''
    f_p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # Add page field to footer
    f_p1._p.append(parse_xml('<w:fldSimple ' + nsdecls('w') + ' w:instr="PAGE"/>'))
    # Clean any additional footer paragraphs
    for p in sec1.footer.paragraphs[1:]:
        p.text = ''

    # Section 2: Main Body
    sec2 = doc.sections[2]
    sec2.header.is_linked_to_previous = False
    sec2.footer.is_linked_to_previous = False
    for p in sec2.header.paragraphs:
        p.text = ''
    f_p2 = sec2.footer.paragraphs[0]
    f_p2.text = ''
    f_p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # Add page field to footer
    f_p2._p.append(parse_xml('<w:fldSimple ' + nsdecls('w') + ' w:instr="PAGE"/>'))
    for p in sec2.footer.paragraphs[1:]:
        p.text = ''

    print("Configured clean headers and dynamic page numbers in footers.")

    # -------------------------------------------------------------
    # 2. FRONT MATTER HEADINGS STYLE
    # -------------------------------------------------------------
    front_matter_headings = [
        "Letter of Transmittal",
        "Organization’s Certificate",
        "Organization's Certificate",
        "Student’s Declaration",
        "Student's Declaration",
        "Supervisor’s Certification",
        "Supervisor's Certification",
        "Abstract",
        "Acknowledgments"
    ]
    for p in doc.paragraphs:
        txt = p.text.strip()
        for fmh in front_matter_headings:
            if txt == fmh:
                try:
                    p.style = doc.styles['Heading 2']
                except Exception:
                    pass
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                for r in p.runs:
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(14)
                    r.font.bold = True
                    r.font.color.rgb = RGBColor(0, 0, 0)
                break

    # -------------------------------------------------------------
    # 3. NORMALIZE BODY FIGURE CAPTIONS
    # -------------------------------------------------------------
    figure_map = {
        "Figure 1.0.1": "Figure 1.1 Agile Iterative Development Model",
        "Figure 2.0.1": "Figure 2.1 Organizational Structure of Al Hadi Enterprise and Software Development Team",
        "Figure 3.0.1": "Figure 3.1 Use Case Diagram of IntelliGrade",
        "Figure 4.0.1": "Figure 4.1 Activity Diagram: Exam Controller Governance Workflow",
        "Figure 4.0.2": "Figure 4.2 Activity Diagram: Examination Scheduling and Provisioning (AI Routine Scan vs. Manual Entry)",
        "Figure 4.0.3": "Figure 4.3 Activity Diagram: Faculty/Examiner Workflow",
        "Figure 4.0.4": "Figure 4.4 Activity Diagram: Question Paper and Rubric Authoring (AI Document Scan vs. Manual Builder)",
        "Figure 4.0.5": "Figure 4.5 Activity Diagram: AI Evaluation Wizard Flow",
        "Figure 4.0.6": "Figure 4.6 Activity Diagram: OBE Tabulation & Calculation",
        "Figure 4.0.7": "Figure 4.7 Activity Diagram: Department Head Governance",
        "Figure 4.0.8": "Figure 4.8 Activity Diagram: Student Academic Transparency Portal",
        "Figure 4.0.9": "Figure 4.9 Swim-lane Diagram for User Authentication & Role-Based Access Control",
        "Figure 4.10": "Figure 4.10 Swim-lane Diagram for Examination Scheduling & Faculty Allocation",
        "Figure 4.12": "Figure 4.11 Swim-lane Diagram for Answer Script Evaluation & Teacher Finalization",
        "Figure 4.13": "Figure 4.12 Swim-lane Diagram for OBE Tabulation, Excel Export & Student Result Dissemination",
        "Figure 4.14": "Figure 4.13 Class Diagram: Core Domain Models",
        "Figure 6.1": "Figure 6.1 Gantt Chart: Project Schedule",
        "Figure 8.1": "Figure 8.1 System Architecture Overview Diagram (4-Tier)",
        "Figure 8.2": "Figure 8.2 Data Flow Diagram – Level 0 (Context Diagram)",
        "Figure 8.3": "Figure 8.3 Data Flow Diagram – Level 1 (System Level)",
        "Figure 8.4": "Figure 8.4 Entity-Relationship Diagram (ERD)",
        "Figure 8.5": "Figure 8.5 UI Mockup: Landing Page & Portal Selector",
        "Figure 8.6": "Figure 8.6 UI Mockup: Exam Controller Governance Dashboard",
        "Figure 8.7": "Figure 8.7 UI Mockup: AI Routine Scanner & Scheduler",
        "Figure 8.8": "Figure 8.8 UI Mockup: AI Evaluation Wizard & Script Upload",
        "Figure 8.9": "Figure 8.9 UI Mockup: Split-Screen Teacher Grading Workbench",
        "Figure 8.10": "Figure 8.10 UI Mockup: Course OBE Tabulation View",
        "Figure 8.11": "Figure 8.11 UI Mockup: Student Transparency Dashboard",
        "Figure 8.12": "Figure 8.12 UI Mockup: Department Head Analytics Dashboard",
    }

    fig_count = 0
    for i, p in enumerate(doc.paragraphs):
        if i < 182: # front matter
            continue
        txt = p.text.strip()
        for prefix, target_caption in figure_map.items():
            if txt.startswith(prefix):
                p.text = target_caption
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(6)
                p.paragraph_format.space_after = Pt(12)
                for r in p.runs:
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(12)
                    r.font.bold = True
                    r.font.color.rgb = RGBColor(0, 0, 0)
                fig_count += 1
                break
    print(f"Normalized {fig_count} figure captions in body.")

    # -------------------------------------------------------------
    # 4. NORMALIZE BODY TABLE CAPTIONS
    # -------------------------------------------------------------
    table_map = {
        "Table 4.1": "Table 4.1 CRC Card: Profile (User Role)",
        "Table 4.2": "Table 4.2 CRC Card: Examination",
        "Table 4.3": "Table 4.3 CRC Card: Question",
        "Table 4.4": "Table 4.4 CRC Card: StudentSubmission",
        "Table 4.5": "Table 4.5 CRC Card: EvaluationResult",
        "Table 4.6": "Table 4.6 CRC Card: CourseTabulation",
        "Table 4.7": "Table 4.7 CRC Card: StudentGradeRecord",
        "Table 5.1": "Table 5.1 Risk Identification",
        "Table 5.2": "Table 5.2 Risk Analysis",
        "Table 5.3": "Table 5.3 RMMM: Risk 1 – CPU OCR Latency",
        "Table 5.4": "Table 5.4 RMMM: Risk 2 – AI Rate Limiting",
        "Table 5.5": "Table 5.5 RMMM: Risk 3 – Handwriting Illegibility",
        "Table 5.6": "Table 5.6 RMMM: Risk 4 – Data Loss During Evaluation",
        "Table 5.7": "Table 5.7 RMMM: Risk 5 – SMTP Email Delivery Failure",
        "Table 5.8": "Table 5.8 RMMM: Risk 6 – Disk Storage Overflow",
        "Table 5.9": "Table 5.9 Risk 7 – OBE Calculation Inconsistency",
        "Table 6.1": "Table 6.1 Functionality, Input and Output",
        "Table 6.2": "Table 6.2 Complexity of Data Function",
        "Table 6.3": "Table 6.3 Complexity of Transaction Function",
        "Table 6.4": "Table 6.4 UFP Calculation Summary",
        "Table 6.5": "Table 6.5 Technical Difficulty Index (TDI)",
        "Table 7.1": "Table 7.1 Personnel Salary",
        "Table 7.2": "Table 7.2 Personnel Cost Estimation",
        "Table 7.3": "Table 7.3 Hardware Cost",
        "Table 7.4": "Table 7.4 Software Cost",
        "Table 7.5": "Table 7.5 Other Operational Costs",
        "Table 7.6": "Table 7.6 Total Project Cost Summary",
        "Table 8.1": "Table 8.1 Technology Stack Details",
        "Table 8.2": "Table 8.2 Core Database Schema",
        "Table 8.3": "Table 8.3 REST and AJAX API Catalog",
        "Table 9.1": "Table 9.1 Test Case 1: User Login and Role-Based Dispatch",
        "Table 9.2": "Table 9.2 Test Case 2: AI Exam Routine Scanning",
        "Table 9.3": "Table 9.3 Test Case 3: Question Paper Studio – 23-Taxonomy Entry",
        "Table 9.4": "Table 9.4 Test Case 4: Script Upload and 300 DPI Preprocessing",
        "Table 9.5": "Table 9.5 Test Case 5: AI Evaluation Wizard – End-to-End",
        "Table 9.6": "Table 9.6 Test Case 6: Manual Script Grading Wizard",
        "Table 9.7": "Table 9.7 Test Case 7: Teacher Mark Override and Audit Log",
        "Table 9.8": "Table 9.8 Test Case 8: OBE Tabulation and Excel Export",
        "Table 9.9": "Table 9.9 Test Case 9: Student Dashboard – Grade Transparency",
    }

    tbl_count = 0
    for i, p in enumerate(doc.paragraphs):
        if i < 182:
            continue
        txt = p.text.strip()
        for prefix, target_caption in table_map.items():
            if txt.startswith(prefix):
                p.text = target_caption
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(12)
                p.paragraph_format.space_after = Pt(6)
                for r in p.runs:
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(12)
                    r.font.bold = True
                    r.font.color.rgb = RGBColor(0, 0, 0)
                tbl_count += 1
                break
    print(f"Normalized {tbl_count} table captions in body.")

    # -------------------------------------------------------------
    # 5. FORMAT REFERENCES WITH HANGING INDENT
    # -------------------------------------------------------------
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
        # Paragraphs from ref_idx+1 until next heading ("Plagiarism Report")
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
        print("Formatted References with 0.5-inch hanging indent.")

    # -------------------------------------------------------------
    # 6. ENSURE TOC FIELD AT P[105]
    # -------------------------------------------------------------
    toc_heading_idx = None
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip() == "Table of Contents":
            toc_heading_idx = i
            break

    if toc_heading_idx is not None:
        # Check paragraph after Table of Contents
        next_p = doc.paragraphs[toc_heading_idx + 1]
        # Insert a TOC field paragraph if not already present
        toc_fld_p = next_p.insert_paragraph_before()
        toc_fld_p._p.append(parse_xml(
            '<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
            '<w:r><w:instrText xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
            '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
            '</w:p>'
        ))
        print("Ensured native TOC field in Table of Contents.")

    doc.save(dst_path)
    print(f"Saved intermediate formatted report to: {dst_path}")

if __name__ == '__main__':
    create_report_v3()

