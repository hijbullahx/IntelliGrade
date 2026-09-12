import os
import sys
import copy
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

def build_presentation():
    base_ppt_path = r'D:\Projects\IntelliGrade\Materials\Presentation\FINAL_ppt.pptx [mine].pptx'
    output_path = r'D:\Projects\IntelliGrade\Materials\Presentation\IntelliGrade_Practicum_Presentation_Final.pptx'
    
    diagrams_dir = r'D:\Projects\IntelliGrade\Materials\Diagrams'
    ss_dir = r'D:\Projects\IntelliGrade\Materials\SS'
    
    src_prs = Presentation(base_ppt_path)
    out_prs = Presentation(base_ppt_path)
    # Clear out all slides in out_prs so we can add in exact chronological order
    # In python-pptx, to clear slides, we can remove slide elements from sldIdLst
    rId_list = [s.rId for s in out_prs.slides._sldIdLst]
    for rId in rId_list:
        out_prs.part.drop_rel(rId)
    out_prs.slides._sldIdLst.clear()

    blank_layout = out_prs.slide_layouts[6]
    
    # Template shapes from existing slide 12 in src_prs (for logos and title styling)
    template_slide = src_prs.slides[11]
    
    def copy_slide_from_src(src_slide_idx):
        src_slide = src_prs.slides[src_slide_idx]
        new_slide = out_prs.slides.add_slide(blank_layout)
        for shape in src_slide.shapes:
            new_slide.shapes._spTree.append(copy.deepcopy(shape.element))
        return new_slide

    def add_header_and_logos(slide, title_text):
        for sh in template_slide.shapes:
            if sh.name in ['Picture 4', 'Picture 2']:
                slide.shapes._spTree.append(copy.deepcopy(sh.element))
        
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.2), Inches(8.5), Inches(0.8))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.bold = True
        p.font.size = Pt(20)
        p.font.color.rgb = RGBColor(15, 34, 64) # Navy
        return title_box

    def add_diagram_slide(title, img_filename):
        img_path = os.path.join(diagrams_dir, img_filename)
        if not os.path.exists(img_path):
            print(f"Warning: image {img_filename} not found!")
            return None
        slide = out_prs.slides.add_slide(blank_layout)
        add_header_and_logos(slide, title)
        slide.shapes.add_picture(img_path, Inches(0.6), Inches(1.15), width=Inches(8.8))
        return slide

    def add_screenshot_slide(title, img_filename, subtitle=""):
        img_path = os.path.join(ss_dir, img_filename)
        if not os.path.exists(img_path):
            alt_path = os.path.join(diagrams_dir, img_filename)
            if os.path.exists(alt_path):
                img_path = alt_path
            else:
                print(f"Warning: screenshot {img_filename} not found!")
                return None
        slide = out_prs.slides.add_slide(blank_layout)
        add_header_and_logos(slide, title)
        
        if subtitle:
            cap_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.85), Inches(8.8), Inches(0.35))
            tf = cap_box.text_frame
            p = tf.paragraphs[0]
            p.text = subtitle
            p.font.size = Pt(11)
            p.font.color.rgb = RGBColor(80, 95, 115)
            
        slide.shapes.add_picture(img_path, Inches(0.6), Inches(1.2), width=Inches(8.8))
        return slide

    def add_cards_slide(title, cards):
        slide = out_prs.slides.add_slide(blank_layout)
        add_header_and_logos(slide, title)
        
        n = len(cards)
        if n == 3:
            card_h = Inches(1.5)
            spacing = Inches(1.65)
        elif n == 4:
            card_h = Inches(1.15)
            spacing = Inches(1.3)
        else:
            card_h = Inches(0.95)
            spacing = Inches(1.05)
            
        for i, (head, body) in enumerate(cards):
            top_pos = Inches(1.15 + i * spacing)
            shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top_pos, Inches(8.4), card_h)
            shape.fill.solid()
            shape.fill.fore_color.rgb = RGBColor(246, 249, 254)
            shape.line.color.rgb = RGBColor(56, 128, 255)
            shape.line.width = Pt(1.5)
            
            tf = shape.text_frame
            tf.word_wrap = True
            p1 = tf.paragraphs[0]
            p1.text = head
            p1.font.bold = True
            p1.font.size = Pt(14 if n > 4 else 15)
            p1.font.color.rgb = RGBColor(15, 34, 64)
            
            p2 = tf.add_paragraph()
            p2.text = body
            p2.font.size = Pt(11 if n > 4 else 12)
            p2.font.color.rgb = RGBColor(70, 80, 95)
        return slide

    def add_table_slide(title, headers, rows_data):
        slide = out_prs.slides.add_slide(blank_layout)
        add_header_and_logos(slide, title)
        
        num_rows = len(rows_data) + 1
        num_cols = len(headers)
        
        top_pos = Inches(1.2)
        table_w = Inches(8.4)
        table_h = Inches(0.4 * num_rows)
        
        table_shape = slide.shapes.add_table(num_rows, num_cols, Inches(0.8), top_pos, table_w, table_h)
        table = table_shape.table
        
        for c_idx, h_text in enumerate(headers):
            cell = table.cell(0, c_idx)
            cell.text = h_text
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(15, 34, 64)
            for p in cell.text_frame.paragraphs:
                p.font.bold = True
                p.font.size = Pt(12)
                p.font.color.rgb = RGBColor(255, 255, 255)
                p.alignment = PP_ALIGN.CENTER
                
        for r_idx, row in enumerate(rows_data):
            for c_idx, val in enumerate(row):
                cell = table.cell(r_idx + 1, c_idx)
                cell.text = str(val)
                cell.fill.solid()
                if r_idx % 2 == 0:
                    cell.fill.fore_color.rgb = RGBColor(255, 255, 255)
                else:
                    cell.fill.fore_color.rgb = RGBColor(245, 248, 253)
                for p in cell.text_frame.paragraphs:
                    p.font.size = Pt(11)
                    p.font.color.rgb = RGBColor(30, 40, 55)
        return slide

    print("Assembling slides in logical defense order...")
    
    # -------------------------------------------------------------
    # SECTION 1: COVER & INTRODUCTION (Slides 1 to 6)
    # -------------------------------------------------------------
    copy_slide_from_src(0) # 1: Cover Slide
    copy_slide_from_src(1) # 2: Table of Contents
    copy_slide_from_src(2) # 3: Internship Organization
    copy_slide_from_src(3) # 4: My Portfolio
    
    # 5: Org Structure
    add_cards_slide("Organization Structure & Deployment Hierarchy", [
        ("College of Engineering and Technology (CEAT)", "Governing academic body at IUBAT establishing accreditation requirements, OBE mandates, and overarching faculty standards."),
        ("Department of Computer Science and Engineering (CSE)", "Host academic department executing the practicum initiative and serving as the primary deployment testbed for IntelliGrade."),
        ("Office of the Chief Examination Controller", "Institutional authority responsible for schedule provisioning, centralized routine scanning, and official student record approvals."),
        ("Host Organization: Al-Hadi Enterprise", "Providing industrial software engineering internship supervision, infrastructure mentorship, and quality assurance oversight.")
    ])
    
    copy_slide_from_src(4) # 6: Problem Statement (Slide 5 in src)
    copy_slide_from_src(5) # 7: Innovative Solutions (Slide 6 in src)
    copy_slide_from_src(6) # 8: Specific Objectives (Slide 7 in src)
    copy_slide_from_src(7) # 9: Key Stakeholders (Slide 8 in src)

    # -------------------------------------------------------------
    # SECTION 2: ACTOR WORKFLOWS & SYSTEM BENEFITS
    # -------------------------------------------------------------
    add_cards_slide("Actor Workflow: Chief Exam Controller", [
        ("AI Exam Routine Ingestion", "Uploads complex university examination routine PDFs; system automatically extracts dates, courses, and exam slots via AI/regex hybrid parser."),
        ("Course & Faculty Allocation", "Dispatches automated welcome emails with OTPs, registers department heads, and binds teachers to designated courses."),
        ("Governance & Approval Queue", "Audits pending student registrations, activates semester exams, and locks finalized tabulations into immutable archives.")
    ])
    
    add_cards_slide("Actor Workflow: Department Head & Faculty", [
        ("Department Head Governance", "Monitors department-wide grading progress, tracks faculty evaluation bottlenecks, and reviews class OBE attainment heatmaps."),
        ("Faculty Exam Authoring", "Builds multi-part exam question papers with 23-field taxonomy mappings (Bloom's, CO, PO, KP, CEP, CEA) and detailed rubrics."),
        ("Interactive Evaluation Workbench", "Conducts side-by-side verification of scanned scripts against AI scores, overrides criteria marks with audit notes, and finalizes grades.")
    ])
    
    add_cards_slide("Actor Workflow: Student Transparency Portal", [
        ("Secure Self-Registration & OTP", "Students self-register with their roll numbers, receive email confirmation, and log in securely via two-factor OTP verification."),
        ("Live Academic Dashboard", "Views published semester grades, weighted GPAs (4.00 scale), and exact question-by-question marks breakdown."),
        ("Certified PDF Download", "Downloads digitally watermarked, officially certified evaluation scripts containing examiner comments and rubric breakdowns.")
    ])

    add_cards_slide("System Benefits: Operational Efficiency & Accuracy", [
        ("70% Grading Turnaround Reduction", "Automated 300 DPI script slicing, multi-engine OCR, and parallel AI rubric grading cut per-script turnaround from 25 minutes to under 7 minutes."),
        ("Zero Spreadsheet Arithmetic Errors", "Real-time automated weighted calculation (CT 10% + Mid 25% + Final 50% + Assign 10% + Att 5%) eliminates human floating-point mistakes."),
        ("Human-in-the-Loop Authority", "AI provides calibrated suggestions and highlight cues, but teachers retain 100% final grading authority via explicit review modals."),
        ("100% Paperless Script Lifecycle", "Digital rasterization and certified PDF stamping eliminate script misplacement, physical transport logistics, and paper degradation.")
    ])
    
    add_cards_slide("System Benefits: OBE Compliance & Accreditation", [
        ("Automated BAETE CO/PO Attainment", "Translates raw question marks directly into Course Outcome (CO1-CO6) and Program Outcome (PO1-PO12) attainment percentages."),
        ("One-Click 8-Sheet Excel Tabulation", "Generates complete institutional Excel workbooks ready for immediate submission to the Academic Council and accreditation teams."),
        ("Tamper-Proof Audit Trails", "Every mark override, teacher review, and finalization action is permanently recorded with actor ID, timestamp, and rationale."),
        ("Democratized Student Transparency", "Eliminates student grading anxiety by offering full visibility into marking criteria, deduction reasons, and performance feedback.")
    ])

    # -------------------------------------------------------------
    # SECTION 3: SDLC & REQUIREMENTS
    # -------------------------------------------------------------
    add_cards_slide("Software Development Methodology: Agile Scrum", [
        ("Sprint 1: Foundation & RBAC", "Role-based authentication, user profile schema, OTP email verification, and baseline portal layouts."),
        ("Sprint 2: Academic Governance & Routine Parser", "Exam schedule PDF parser, course allocations, and 23-taxonomy question and rubric authoring studio."),
        ("Sprint 3: Document Ingestion & Hybrid OCR", "300 DPI rasterization, OpenCV deskewing, PyMuPDF native vector text, and EasyOCR handwriting recognition."),
        ("Sprint 4: Multi-Provider AI Failover Engine", "Orchestrator integration with Moondream2 (local), Groq Llama-3.3 70B, Gemini 2.5 Flash, and OpenAI GPT-4o."),
        ("Sprint 5: Evaluation Workbench & Finalization", "Split-screen grading UI, manual fallback wizard, ReportLab certified PDF stamping, and storage artifact purging."),
        ("Sprint 6: OBE Tabulation & Final Audits", "Live CO/PO attainment matrix, 8-sheet openpyxl Excel exporter, async SMTP notifications, and E2E system testing.")
    ])
    
    add_cards_slide("User Requirements: Functional Needs by Actor", [
        ("Chief Exam Controller Requirements", "Must schedule exams from raw PDFs, manage academic roles, audit system-wide grading health, and approve student rosters."),
        ("Department Head Requirements", "Must track department faculty evaluation deadlines, inspect course pass rates, and verify OBE attainment standards."),
        ("Course Examiner Requirements", "Must upload answer scripts in bulk, map answers to questions, review AI mark distributions, override grades, and export tabulations."),
        ("Student Requirements", "Must access personal grades in real-time, view question-level feedback, and download signed, watermarked answer scripts.")
    ])

    copy_slide_from_src(22) # FR-01 to FR-20
    copy_slide_from_src(23) # FR-21 to FR-37
    copy_slide_from_src(24) # NFRs

    # -------------------------------------------------------------
    # SECTION 4: ARCHITECTURE, MODULES & USE CASE
    # -------------------------------------------------------------
    copy_slide_from_src(8)  # System Architecture Overview 1
    copy_slide_from_src(9)  # System Architecture Overview 2
    copy_slide_from_src(10) # 21-Module Catalog
    copy_slide_from_src(11) # Use Case Diagram

    # -------------------------------------------------------------
    # SECTION 5: ACTIVITY DIAGRAMS (Full Suite)
    # -------------------------------------------------------------
    add_diagram_slide("Activity Diagram: Routine Scanning & Ingestion", "activity diagram exam controller.png")
    add_diagram_slide("Activity Diagram: Question Paper & Rubric Authoring", "Activity Diagram Question Paper and Rubric Authoring.png")
    add_diagram_slide("Activity Diagram: Script Ingestion & 300 DPI Preprocessing", "Activity Diagram Script Ingestion and 300 DPI Preprocessing.png")
    copy_slide_from_src(12) # Activity Diagram: AI Evaluation Wizard Pipeline
    copy_slide_from_src(13) # Activity Diagram: Manual Grading Wizard
    add_diagram_slide("Activity Diagram: Teacher Review & Finalization", "Activity Diagram Teacher Review and Finalization.png")
    add_diagram_slide("Activity Diagram: OBE Tabulation & Email Dissemination", "Activity Diagram OBE Tabulation and Email Dissemination.png")

    # -------------------------------------------------------------
    # SECTION 6: SWIMLANE & SEQUENCE DIAGRAMS
    # -------------------------------------------------------------
    add_diagram_slide("Swim-lane Diagram: End-to-End Evaluation Ecosystem", "Swim-lane Diagram.png")
    copy_slide_from_src(14) # Sequence Diagram: AI Evaluation Wizard
    copy_slide_from_src(15) # Sequence Diagram: Student Portal

    # -------------------------------------------------------------
    # SECTION 7: CLASS DIAGRAMS & ERD & DFD
    # -------------------------------------------------------------
    copy_slide_from_src(16) # Class Diagram: Core Domain Model
    copy_slide_from_src(17) # Class Diagram: AI Engine & Services
    copy_slide_from_src(18) # ERD
    copy_slide_from_src(19) # DFD Level 0
    copy_slide_from_src(20) # DFD Level 1

    # -------------------------------------------------------------
    # SECTION 8: RISK MANAGEMENT
    # -------------------------------------------------------------
    add_cards_slide("Risk Management: Identification (RMMM Framework)", [
        ("Technical: AI API Rate Limits & Network Outages", "Groq / Gemini HTTP 429 throttling or campus internet dropouts stalling the script grading pipeline."),
        ("Computational: Floating-Point Rounding Inconsistencies", "Python standard float math drifting by +-0.01 between web UI display and exported Excel workbooks."),
        ("Accuracy: Handwriting OCR Recognition Variance", "Messy, cursive, or low-contrast handwritten answer scripts yielding low OCR confidence scores."),
        ("Operational: Server Storage Exhaustion", "Uncompressed high-resolution 300 DPI raw page images rapidly filling local server disk partitions."),
        ("Governance: Unauthorized Grade Modifications", "Compromised faculty sessions or malicious POST requests attempting to alter finalized examination marks.")
    ])
    
    add_cards_slide("Risk Management: Mitigation Strategies & Safeguards", [
        ("Dynamic Multi-Provider AI Failover", "TaskRouter cascades from Groq -> OpenRouter -> Gemini -> OpenAI -> Local Moondream2 (Ollama) with 45s timeout budgets."),
        ("Strict Decimal Wrapping & Excel Formula Verification", "All intermediate scores wrapped in round(val, 2). openpyxl formulas validate Python-computed totals on export."),
        ("Adaptive Contrast & Human Review Queue", "OpenCV CLAHE enhancement + thresholding. Any question confidence < 0.75 is flagged for mandatory teacher review."),
        ("Automated Working Copy Artifact Purging", "Post-finalization cleanup script deletes interim draft images while keeping certified PDFs and compressed records."),
        ("Immutable Audit Logs & Session Expiry", "EvaluationAuditLog stores every mark change with actor ID, IP, and reason. Automatic session timeouts protect active portals.")
    ])

    # -------------------------------------------------------------
    # SECTION 9: ESTIMATION & COSTING
    # -------------------------------------------------------------
    copy_slide_from_src(21) # Function Point (FP) Calculation Summary
    add_cards_slide("Function Point Analysis: Complexity Breakdown", [
        ("External Inputs (EI) — 6 Transactions", "Routine Scanning, Script Preprocessing, Question Authoring, Mark Override, Student Self-Registration, Attendance Edit."),
        ("External Outputs (EO) — 7 Transactions", "Certified PDF Generation, 8-Sheet Excel Export, Student Dashboard, Grade Cards, OCR Visualizer, Email Alert Dispatch."),
        ("External Interface Files (EIF) — 3 Interfaces", "Multi-Provider AI Orchestration (Groq/Gemini/OpenAI), SMTP Gateway, Local Ollama Moondream2 Service."),
        ("Internal Logical Files (ILF) — 5 Data Groups", "Core Profiles/Auth, Exam & Question Hierarchy, Student Submissions & Pages, Evaluation Results, Tabulation & Grade Records."),
        ("Technical Difficulty Index (TDI) & VAF", "14 General System Characteristics evaluated -> TDI = 40 -> Value Adjustment Factor (VAF) = 1.05. AFP = 130 * 1.05 = 136.5 AFP.")
    ])
    add_diagram_slide("Project Scheduling: 12-Week Gantt Chart", "Gantt Chart Project Schedule.png")
    add_table_slide("Total Project Cost Estimation Summary (BDT)", 
        ["Cost Component", "Particulars & Resource Allocation", "Amount (BDT)"],
        [
            ["Personnel Salary", "System Architect / Full-Stack Developer (8 Months @ 80,000)", "640,000"],
            ["Personnel Salary", "AI / Machine Learning Engineer (6 Months @ 75,000)", "450,000"],
            ["Personnel Salary", "Database Engineer (4 Months @ 60,000)", "240,000"],
            ["Personnel Salary", "UI/UX Front-End Designer (4 Months @ 50,000)", "200,000"],
            ["Personnel Salary", "QA / Test Engineer (3 Months @ 45,000)", "135,000"],
            ["Subtotal Personnel", "5 Software Engineering Specialists (Total 25 Person-Months)", "1,665,000"],
            ["Hardware Costs", "Dev Workstation (Core i7, 32GB RAM, 1TB SSD) + RTX 4060 GPU", "185,000"],
            ["Hardware Costs", "Network Switches, High-Speed Router, UPS Backup Equipment", "25,000"],
            ["Subtotal Hardware", "Dedicated Development & On-Premises Inference Hardware", "210,000"],
            ["Software & Cloud", "Django, PostgreSQL, PyMuPDF, EasyOCR (Open Source)", "0"],
            ["Software & Cloud", "Production Cloud Server Hosting & Custom Domain Name", "8,220"],
            ["Operational Expenses", "Electricity, High-Speed Internet, Testing Stationery & Supplies", "80,000"],
            ["GRAND TOTAL", "Comprehensive End-to-End System Development Cost", "1,963,220 BDT"]
        ]
    )

    # -------------------------------------------------------------
    # SECTION 10: ARCHITECTURE DETAILS & SYSTEM DESIGN
    # -------------------------------------------------------------
    add_diagram_slide("System Architecture Overview Diagram (4 Tiers)", "System Architecture Overview Diagram.png")
    copy_slide_from_src(25) # Technology Stack & Infrastructure
    copy_slide_from_src(26) # DB Schema & Composite Indexes
    copy_slide_from_src(27) # Technical Changes Roadmap
    copy_slide_from_src(28) # Multi-Provider AI Failover Engine

    # -------------------------------------------------------------
    # SECTION 11: TESTING & VERIFICATION
    # -------------------------------------------------------------
    copy_slide_from_src(29) # Testing Strategy
    copy_slide_from_src(30) # Unit Testing Results
    copy_slide_from_src(31) # Integration Testing Results
    copy_slide_from_src(32) # UAT Testing Results

    # -------------------------------------------------------------
    # SECTION 12: SYSTEM DEMONSTRATION (SCREENSHOTS)
    # -------------------------------------------------------------
    copy_slide_from_src(33) # Landing Page Hero
    copy_slide_from_src(34) # System Entry Portal
    copy_slide_from_src(35) # Exam Controller Dashboard
    add_screenshot_slide("UI Demo: AI Exam Routine Scanning Modal", "exam routine scan.png", "Exam Controller interface for uploading institutional schedule PDFs for automatic parsing")
    add_screenshot_slide("UI Demo: Parsed Examination Schedule & Courses", "after scanned routine.png", "Extracted exam timetable, course codes, exam dates, and slot allocations ready for approval")
    add_screenshot_slide("UI Demo: Department Head Governance Dashboard", "dep_had dash.png", "Executive dashboard tracking faculty grading velocity, submission volumes, and course metrics")
    add_screenshot_slide("UI Demo: Question & Rubric Authoring Studio", "AI qs mapping.png", "23-field taxonomy authoring interface linking Bloom's taxonomy, COs, and evaluation rubrics")
    add_screenshot_slide("UI Demo: Answer Script Ingestion & Slicing Modal", "AI Script upload.png", "Batch upload modal rasterizing multi-page student scripts into 300 DPI working copies")
    add_screenshot_slide("UI Demo: OCR Question Boundary Mapping View", "answer script scanning.png", "OpenCV & OCR pipeline matching student handwritten answer regions to exam questions")
    add_screenshot_slide("UI Demo: Multi-Provider AI Evaluation Progress", "AI evaluation progress.png", "Live task runner tracking AI evaluation queue and provider health fallback status")
    copy_slide_from_src(36) # Split-Screen Workbench
    copy_slide_from_src(37) # OBE Tabulation & Excel Export
    add_screenshot_slide("UI Demo: Fast Manual Script Grading Wizard", "Manual Script grading.png", "Alternative streamlined grading workflow enabling rapid manual score entry and annotation")
    add_screenshot_slide("UI Demo: Generated 8-Sheet Official Excel Export", "OBE xl sheet.png", "Official openpyxl Excel workbook formatted strictly according to BAETE accreditation guidelines")
    add_screenshot_slide("UI Demo: Watermarked Evaluated Certified PDF", "Manual Script evaluated pdf ss.png", "Digitally stamped student answer script containing official seals and question-by-question marks")
    add_screenshot_slide("UI Demo: Automated Email Notification Dispatch", "exam_aasigned email.png", "System-generated HTML email alerts notifying faculty of grading assignments and deadlines")
    copy_slide_from_src(38) # Student Portal

    # -------------------------------------------------------------
    # SECTION 13: CONCLUSION, ROADMAP & REFERENCES
    # -------------------------------------------------------------
    add_cards_slide("System Limitations & Operational Boundaries", [
        ("Cloud AI API Throttling & Latency", "Reliance on external free-tier AI APIs (Groq, Gemini) can encounter sudden rate limits under concurrent exam surges."),
        ("High-DPI Server Storage Consumption", "Uncompressed 300 DPI rasterized scripts demand considerable local storage before finalization purge triggers."),
        ("Cursive Handwriting OCR Ambiguity", "Extremely degraded, low-contrast, or unreadable student handwriting requires human examiner intervention."),
        ("Browser Memory Utilization", "Rendering dozens of high-resolution canvas overlays in split-screen mode requires modern client browser hardware.")
    ])

    add_cards_slide("Future Roadmap & Engineering Directions", [
        ("Asynchronous Distributed Task Workers", "Migrating heavy OCR and AI evaluation tasks to Celery workers backed by Redis message queues."),
        ("Dedicated Edge GPU Inference", "Deploying on-premises NVIDIA RTX GPUs to accelerate EasyOCR and Moondream2 evaluation by over 100x."),
        ("RAG-Powered Marking Consistency", "Integrating pgvector vector databases to calibrate AI scoring against historical teacher marking styles."),
        ("Native Mobile Examination Portal", "Developing cross-platform Flutter mobile applications for instant student grade alerts and offline script review.")
    ])

    copy_slide_from_src(39) # Conclusion & Achievements
    copy_slide_from_src(40) # References
    copy_slide_from_src(41) # Any Questions?
    copy_slide_from_src(42) # Thank You

    out_prs.save(output_path)
    print(f"\n=======================================================")
    print(f"SUCCESS: Master Defense Presentation created!")
    print(f"File Path: {output_path}")
    print(f"Total Slides: {len(out_prs.slides)}")
    print(f"=======================================================")

if __name__ == '__main__':
    build_presentation()
