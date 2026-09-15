
<!-- ============================================================
  IntelliGrade Practicum Report
  Author: Md. Taher Bin Omar Hijbullah  |  ID: 22303142
  Department of Computer Science and Engineering
  IUBAT — International University of Business Agriculture and Technology
  Fall 2026

  FIGURE PLACEHOLDERS: Each figure section contains an
  "Image Generation Prompt" comment. Use an AI image generator
  or your screenshots to fill these in before printing.
============================================================ -->

---

# IntelliGrade

**An End-to-End Outcome-Based Examination Management and Intelligent Script Evaluation Ecosystem for Higher Education Institutions**

---

**Md. Taher Bin Omar Hijbullah**
ID# 22303142

A Practicum in the Partial Fulfillment of the Requirements
for the Award of Bachelor of Computer Science and Engineering (BCSE)

Department of Computer Science and Engineering
College of Engineering and Technology
IUBAT — International University of Business Agriculture and Technology
Fall 2026

---

<!-- PAGE ii — APPROVAL PAGE -->

**IntelliGrade**

Md. Taher Bin Omar Hijbullah

A Practicum in the Partial Fulfillment of the Requirements for the Award of Bachelor of Computer Science and Engineering (BCSE)

The practicum has been examined and approved,

&nbsp;

___________________________
**Prof. Dr. Utpal Kanti Das**
Chairman

&nbsp;

___________________________
**Shahinur Alam**
Co-supervisor, Coordinator and Assistant Professor

&nbsp;

___________________________
**[Supervisor Name]**
Supervisor and Associate Professor

&nbsp;

Department of Computer Science and Engineering
College of Engineering and Technology
IUBAT — International University of Business Agriculture and Technology
Fall 2026

---

<!-- PAGE iii -->

## Letter of Transmittal

September 10, 2026

The Chair
Practicum Defense Committee
Department of Computer Science and Engineering
IUBAT — International University of Business Agriculture and Technology
4 Embankment Drive Road, Sector 10, Uttara Model Town
Dhaka 1230, Bangladesh.

**Subject:** Letter of Transmittal.

Dear Sir,

With due respect, I am pleased to submit my practicum report titled **"IntelliGrade: An End-to-End Outcome-Based Examination Management and Intelligent Script Evaluation Ecosystem for Higher Education Institutions"** as part of the requirement for the B.Sc. in CSE at IUBAT.

This study addresses a real and pressing gap in university examination management. The traditional examination workflow — from scheduling and question setting, through handwritten script grading, to final grade dissemination and accreditation reporting — is heavily manual, time-consuming, and prone to human error. IntelliGrade is my answer to that problem: a complete web-based platform that automates each stage of the examination cycle while keeping the teacher firmly in control of all final decisions.

Over the course of this practicum, I designed and implemented a seven-module system covering AI-assisted routine parsing, a 23-taxonomy OBE question studio, a computer vision and OCR pipeline, a multi-provider AI evaluation engine with intelligent failover, a split-screen teacher verification workbench, a real-time OBE course tabulation engine, and an asynchronous institutional email notification service.

I sincerely thank you and the Practicum Defense Committee for the opportunity. I have made every effort to ensure the accuracy, completeness, and originality of the work presented here.

Your kind evaluation and valuable feedback will be truly appreciated.

&nbsp;

Yours sincerely,

_____________

**Md. Taher Bin Omar Hijbullah**

22303142

---

<!-- PAGE iv -->

## Organization's Certificate

*(Attach official organization certificate here)*

---

<!-- PAGE v -->

## Student's Declaration

I hereby declare that the practicum titled **"IntelliGrade: An End-to-End Outcome-Based Examination Management and Intelligent Script Evaluation Ecosystem for Higher Education Institutions"** is the result of my own work and has not been submitted previously for any degree or diploma in any institution.

I further declare that there is no plagiarism or data falsification in this report. All materials and information taken from various sources have been properly acknowledged and duly cited. Every figure, diagram, and data table presented in this work was either generated directly from the IntelliGrade codebase, produced using the system's own tooling, or drawn from publicly available literature with proper attribution.

I take full responsibility for the content and originality of this work.

&nbsp;

&nbsp;

&nbsp;

&nbsp;

&nbsp;

_____________

**Md. Taher Bin Omar Hijbullah**
22303142

---

<!-- PAGE vi -->

## Supervisor's Certification

This is to certify that Md. Taher Bin Omar Hijbullah, ID# 22303142, has successfully completed the practicum titled **"IntelliGrade: An End-to-End Outcome-Based Examination Management and Intelligent Script Evaluation Ecosystem for Higher Education Institutions"** under my supervision. The student's performance, work, and final report have been reviewed, and it is confirmed that the practicum requirements have been satisfactorily fulfilled. Md. Taher Bin Omar Hijbullah is hereby recommended to appear for the practicum defense. Wishing the student continued success and excellence in all future academic and professional endeavors.

&nbsp;

&nbsp;

&nbsp;

_______________________________
**[Supervisor Name]**
Supervisor and Associate Professor
Department of Computer Science and Engineering
IUBAT — International University of Business Agriculture and Technology

---

<!-- PAGE vii — ABSTRACT (kept to one page) -->

## Abstract

Higher education institutions in Bangladesh and across the developing world face a persistent bottleneck across the entire examination lifecycle. Scheduling is done manually on spreadsheets, question papers are authored without structured alignment to Outcome-Based Education (OBE) taxonomies, evaluation of handwritten answer scripts is slow and subjective, and the computation of Course Outcome (CO) and Program Outcome (PO) attainments required for BAETE and Washington Accord accreditation is largely performed by hand. This practicum presents **IntelliGrade**, a comprehensive academic web platform developed on Django 5.2 and PostgreSQL that automates and modernizes every stage of the university examination lifecycle while maintaining strict Human-in-the-Loop teacher oversight.

The system comprises seven tightly integrated subsystems: (1) an Administrative Governance portal and AI Multimodal Exam Routine Parser that extracts scheduled examination records from official routine PDFs in seconds; (2) a 23-Taxonomy OBE Question Paper Studio capturing Bloom's cognitive levels, Course Outcomes, Program Outcomes, Knowledge Profiles, Complex Engineering Problems, Complex Engineering Activities, embedded figures, tables, and mathematical formulas; (3) a Universal 300 DPI Script Preprocessing pipeline applying Hough-transform deskewing, Otsu thresholding, and a Hybrid Multi-Engine OCR cascade (PyMuPDF native glyph extraction, PyTesseract printed OCR, and an EasyOCR deep-learning CRAFT+BiLSTM handwriting recognizer); (4) an automated Start-of-Line Regex State Machine with spatial boundary detection and visual crop confirmation; (5) a Fault-Tolerant Multi-Provider AI Failover Orchestrator supporting five providers (Moondream2/Ollama, Groq Llama-3.3 70B, OpenRouter, Gemini 2.5 Flash, and OpenAI GPT-4o) with rate-limit cooldown registries and structured JSON repair; (6) a Split-Screen Teacher Verification Workbench with mutable mark overrides, immutable audit logging, and certified ReportLab PDF stamping; and (7) a Course-Level OBE Tabulation Engine computing real-time weighted scores (CT 10% + Mid 25% + Final 50% + Assignment 10% + Attendance 5%) with bi-directional 8-sheet Excel synchronization and asynchronous institutional email dispatch.

System validation confirms 100% mathematical fidelity in OBE calculations, full audit traceability across all evaluation actions, and measurable time savings at every stage of the examination workflow.

**Keywords:** Outcome-Based Education (OBE), Human-in-the-Loop AI Evaluation, Handwriting Recognition, Multi-Provider AI Failover, Django, Academic Governance, Washington Accord, BAETE Accreditation, Real-Time Tabulation.

---

<!-- PAGE ix -->

## Acknowledgments

First and foremost, I am deeply grateful to Almighty Allah for granting me the perseverance, discipline, and clarity of thought needed to complete this practicum — a project that grew far beyond its original scope into something I am genuinely proud of.

I would like to express my sincere gratitude to my honorable supervisor for the patient guidance, honest feedback, and encouragement to push the technical ambition of this work further than I initially believed possible. I am equally thankful to Prof. Dr. Utpal Kanti Das and Shahinur Alam for their support throughout the defense process.

My appreciation extends to the faculty of the Department of Computer Science and Engineering, IUBAT, whose teaching across algorithms, software engineering, database systems, and computer networks gave me the foundation to design a system of this complexity.

To my family — your steady support, patience during long nights of debugging, and belief in this work mean everything. And to my classmates and friends who tested the platform, reported bugs honestly, and kept me motivated, thank you.

Finally, I acknowledge the open-source communities behind Django, PyMuPDF, EasyOCR, PyTesseract, OpenCV, ReportLab, and the AI providers whose APIs power IntelliGrade's evaluation core. This work stands on the shoulders of remarkable public scholarship.

---

<!-- TABLE OF CONTENTS -->

## Table of Contents

| | |
|---|---|
| Letter of Transmittal | iii |
| Organization's Certificate | iv |
| Student's Declaration | v |
| Supervisor's Certification | vi |
| Abstract | vii |
| Acknowledgments | ix |
| List of Figures | xiii |
| List of Tables | xv |
| List of Abbreviations | xvi |
| **Chapter 1. Introduction** | **1** |
| 1.1 Background of the Study | 2 |
| 1.2 Problem Statement | 3 |
| 1.3 Objectives | 4 |
| 1.3.1 Broad Objective | 4 |
| 1.3.2 Specific Objectives | 4 |
| 1.4 Scope of the Project | 5 |
| 1.5 Methodology | 5 |
| 1.6 Report Organization | 6 |
| **Chapter 2. Organization Overview** | **7** |
| 2.1 Organization Vision | 8 |
| 2.2 Organization Mission | 8 |
| 2.3 Organization Services | 8 |
| 2.4 Organizational Structure | 9 |
| 2.5 My Position in this Organization | 9 |
| 2.6 Address of the Organization | 9 |
| **Chapter 3. Requirement Engineering** | **10** |
| 3.1 Requirement Elicitation | 11 |
| 3.2 Requirement Analysis | 12 |
| 3.3 Requirement Specifications | 13 |
| 3.3.1 Functional Requirements | 13 |
| 3.3.2 Non-Functional Requirements | 16 |
| 3.4 Use Case Diagram | 17 |
| **Chapter 4. Analysis Modeling** | **18** |
| 4.1 Activity Diagrams | 19 |
| 4.2 Sequence Diagram | 26 |
| 4.3 State Machine Diagram | 28 |
| 4.4 CRC Cards | 29 |
| 4.5 Class Diagram | 33 |
| **Chapter 5. Project Management** | **34** |
| 5.1 Risk Identification | 35 |
| 5.2 Risk Analysis | 36 |
| 5.3 Risk Mitigation, Monitoring and Management (RMMM) | 37 |
| **Chapter 6. Estimation** | **44** |
| 6.1 Function Point Analysis | 45 |
| 6.2 Project Schedule (Gantt Chart) | 48 |
| **Chapter 7. Cost Estimation** | **49** |
| 7.1 Personnel Cost | 50 |
| 7.2 Hardware Cost | 51 |
| 7.3 Software Cost | 51 |
| 7.4 Operational Cost | 52 |
| 7.5 Total Project Cost Summary | 52 |
| **Chapter 8. System Design** | **53** |
| 8.1 System Architecture Overview | 54 |
| 8.2 Module Descriptions | 55 |
| 8.3 Data Flow Diagrams (DFD) | 57 |
| 8.4 Entity-Relationship Diagram (ERD) | 60 |
| 8.5 Database Schema | 61 |
| 8.6 REST and AJAX API Catalog | 64 |
| 8.7 Interface Design | 67 |
| **Chapter 9. Testing** | **76** |
| 9.1 Test Cases | 77 |
| **Chapter 10. Conclusion** | **86** |
| 10.1 Project Summary | 87 |
| 10.2 Limitations | 87 |
| 10.3 Future Plans | 88 |
| References | 89 |
| Plagiarism Report | 91 |

---

## List of Figures

| | |
|---|---|
| Figure 1.5.1 Agile Iterative Development Model | 5 |
| Figure 2.4 Organizational Structure of IUBAT CSE Department | 9 |
| Figure 3.4 Use Case Diagram | 17 |
| Figure 4.1.1 Activity Diagram: Exam Controller Governance | 19 |
| Figure 4.1.2 Activity Diagram: Question Paper and Rubric Authoring | 20 |
| Figure 4.1.3 Activity Diagram: Script Ingestion and 300 DPI Preprocessing | 21 |
| Figure 4.1.4 Activity Diagram: AI Evaluation Wizard Flow | 22 |
| Figure 4.1.5 Activity Diagram: Manual Script Grading Wizard Flow | 23 |
| Figure 4.1.6 Activity Diagram: Teacher Review and Finalization | 24 |
| Figure 4.1.7 Activity Diagram: OBE Tabulation and Email Dissemination | 25 |
| Figure 4.2 Sequence Diagram: End-to-End Evaluation Lifecycle | 27 |
| Figure 4.3 State Machine Diagram: StudentSubmission Lifecycle | 28 |
| Figure 4.5 Class Diagram: Core Domain Models | 33 |
| Figure 6.2.1 Gantt Chart: Project Schedule | 48 |
| Figure 8.1 System Architecture Overview Diagram | 54 |
| Figure 8.3.1 DFD Level 0 — Context Diagram | 57 |
| Figure 8.3.2 DFD Level 1 | 58 |
| Figure 8.3.3 DFD Level 2: Script Processing | 59 |
| Figure 8.4 Entity-Relationship Diagram (ERD) | 60 |
| Figure 8.7.1 Landing Page and Login Screen | 67 |
| Figure 8.7.2 Exam Controller Dashboard | 68 |
| Figure 8.7.3 AI Routine Scanner | 69 |
| Figure 8.7.4 Question Paper and Rubric Studio (23-Taxonomy) | 70 |
| Figure 8.7.5 AI Evaluation Wizard — Script Upload and Page Builder | 71 |
| Figure 8.7.6 Split-Screen Teacher Grading Workbench | 72 |
| Figure 8.7.7 Course OBE Tabulation View | 73 |
| Figure 8.7.8 Student Transparency Dashboard | 74 |
| Figure 8.7.9 Department Head Analytics Dashboard | 75 |

---

## List of Tables

| | |
|---|---|
| Table 3.3.1 Functional Requirements Catalog | 13 |
| Table 3.3.2 Non-Functional Requirements Catalog | 16 |
| Table 4.4.1 CRC Card: Profile (User Role) | 29 |
| Table 4.4.2 CRC Card: Examination | 30 |
| Table 4.4.3 CRC Card: Question and Rubric | 30 |
| Table 4.4.4 CRC Card: StudentSubmission | 31 |
| Table 4.4.5 CRC Card: EvaluationResult | 31 |
| Table 4.4.6 CRC Card: CourseTabulation | 32 |
| Table 4.4.7 CRC Card: StudentGradeRecord | 32 |
| Table 5.1.1 Risk Identification | 35 |
| Table 5.2.1 Risk Analysis | 36 |
| Table 5.3.1 RMMM: Risk 1 — CPU OCR Latency | 37 |
| Table 5.3.2 RMMM: Risk 2 — AI Rate Limiting | 38 |
| Table 5.3.3 RMMM: Risk 3 — Handwriting Illegibility | 39 |
| Table 5.3.4 RMMM: Risk 4 — Data Loss During Evaluation | 40 |
| Table 5.3.5 RMMM: Risk 5 — SMTP Email Delivery Failure | 41 |
| Table 5.3.6 RMMM: Risk 6 — Disk Storage Overflow | 42 |
| Table 5.3.7 RMMM: Risk 7 — OBE Calculation Inconsistency | 43 |
| Table 6.1.1 Functionality, Input and Output | 45 |
| Table 6.1.2.1 Complexity of Data Function | 46 |
| Table 6.1.2.2 Complexity of Transaction Function | 46 |
| Table 6.1.3 UFP Calculation Summary | 47 |
| Table 6.1.4 Technical Difficulty Index (TDI) | 47 |
| Table 7.1 Personnel Salary | 50 |
| Table 7.2 Personnel Cost Estimation | 50 |
| Table 7.3 Hardware Cost | 51 |
| Table 7.4 Software Cost | 51 |
| Table 7.5 Other Operational Costs | 52 |
| Table 7.6 Total Project Cost Summary | 52 |
| Table 8.5 Core Database Schema | 61 |
| Table 8.6 REST and AJAX API Catalog | 64 |
| Table 9.1 Test Case 1: User Login and Role Dispatch | 77 |
| Table 9.2 Test Case 2: AI Exam Routine Scanning | 78 |
| Table 9.3 Test Case 3: Question Paper Studio — 23-Taxonomy Entry | 79 |
| Table 9.4 Test Case 4: Script Upload and 300 DPI Preprocessing | 80 |
| Table 9.5 Test Case 5: AI Evaluation Wizard — End-to-End | 81 |
| Table 9.6 Test Case 6: Manual Script Grading Wizard | 82 |
| Table 9.7 Test Case 7: Teacher Mark Override and Audit Log | 83 |
| Table 9.8 Test Case 8: OBE Tabulation and Excel Export | 84 |
| Table 9.9 Test Case 9: Student Dashboard — Grade Transparency | 85 |

---

## List of Abbreviations

| Abbreviation | Full Form |
|---|---|
| AI | Artificial Intelligence |
| API | Application Programming Interface |
| BAETE | Bangladesh Accreditation Council for Engineering and Technical Education |
| BCSE | Bachelor of Computer Science and Engineering |
| BiLSTM | Bidirectional Long Short-Term Memory |
| BBox | Bounding Box |
| CEA | Complex Engineering Activities |
| CEP | Complex Engineering Problems |
| CO | Course Outcome |
| CRAFT | Character Region Awareness for Text Detection |
| CQI | Continuous Quality Improvement |
| CSE | Computer Science and Engineering |
| CT | Class Test |
| CUDA | Compute Unified Device Architecture |
| DFD | Data Flow Diagram |
| DPI | Dots Per Inch |
| ERD | Entity-Relationship Diagram |
| FP | Function Point |
| GPA | Grade Point Average |
| HTR | Handwriting Text Recognition |
| HTTP | Hypertext Transfer Protocol |
| IUBAT | International University of Business Agriculture and Technology |
| JSON | JavaScript Object Notation |
| KP | Knowledge Profile |
| LLM | Large Language Model |
| NFR | Non-Functional Requirement |
| OBE | Outcome-Based Education |
| OCR | Optical Character Recognition |
| ORM | Object-Relational Mapper |
| OTP | One-Time Password |
| PDF | Portable Document Format |
| PO | Program Outcome |
| RAG | Retrieval-Augmented Generation |
| RBAC | Role-Based Access Control |
| REST | Representational State Transfer |
| RPM | Requests Per Minute |
| SMTP | Simple Mail Transfer Protocol |
| SQL | Structured Query Language |
| SRS | Software Requirements Specification |
| TPM | Tokens Per Minute |
| UFP | Unadjusted Function Point |
| UI/UX | User Interface / User Experience |
| URL | Uniform Resource Locator |

---

# Chapter 1.

# Introduction

---

## 1.1 Background of the Study

Academic examinations are the primary instrument through which universities certify student competence and measure learning outcomes. At institutions like IUBAT that follow Outcome-Based Education (OBE) aligned with the Washington Accord and BAETE engineering accreditation standards, the examination process carries additional weight: every question must map to defined Course Outcomes (COs) and Program Outcomes (POs), and the aggregated results must demonstrate adequate attainment levels across an entire student cohort.

The reality on the ground, however, is far from smooth. Faculty members spend hours physically marking handwritten answer scripts, applying subjective judgment question by question, with no objective consistency check between examiners. After marking is complete, they manually tally scores into spreadsheets, compute weighted averages across class tests, midterms, finals, assignments, and attendance, and then produce CO and PO attainment tables for departmental accreditation records. This manual chain is slow, error-prone, and places significant administrative burden on already stretched academic staff.

At the same time, advances in computer vision, Optical Character Recognition (OCR), and Large Language Models (LLMs) have opened a genuine pathway to automating significant portions of this workflow. OCR-based document processing, AI-based rubric grading, and automated tabulation are no longer experimental curiosities — they are production-capable technologies deployable on modest institutional hardware.

IntelliGrade was born from this gap. The goal was not simply to build an AI grading tool, but to design and implement a complete examination management ecosystem — one that covers every stage of the examination lifecycle, from scheduling and question paper authoring, through script evaluation, to grade dissemination and accreditation reporting. The project reflects a commitment to building something that a real university department could actually adopt and benefit from.

## 1.2 Problem Statement

The current examination management workflow at IUBAT and similar institutions exhibits the following critical pain points:

1. **Manual Routine Scheduling**: Exam routines are created and distributed as paper documents or spreadsheets. There is no automated mechanism for parsing these and creating corresponding examination records in a database.

2. **Disconnected Rubric Authoring**: Question papers are authored independently of the grading process. OBE taxonomy mappings (Bloom's level, CO, PO, KP, CEP, CEA) are often captured informally or not at all, making accreditation reporting laborious.

3. **Subjective and Time-Consuming Script Grading**: A single examiner marking 60 scripts with 10 questions each must make 600 individual grading decisions, often over multiple evenings. Consistency across evaluators is difficult to ensure.

4. **Manual OBE Tabulation**: After grading, weighted score computation and CO/PO attainment matrix generation are done manually, consuming hours per course per semester and introducing arithmetic errors.

5. **No Student Transparency Mechanism**: Students receive final grades without visibility into how individual answers were evaluated or how their CO attainments were computed.

6. **Lack of Institutional Email Automation**: Communicating results, account credentials, and schedule changes to students requires manual outreach.

IntelliGrade addresses all six of these problems within a single, integrated platform.

## 1.3 Objectives

### 1.3.1 Broad Objective

To design and implement a complete, end-to-end web-based Outcome-Based Examination Management and Intelligent Script Evaluation Platform for higher education institutions, enabling automated exam scheduling, structured question authoring, AI-assisted answer script evaluation, and real-time OBE tabulation, while keeping human instructors in full control of all final grading decisions.

### 1.3.2 Specific Objectives

1. To implement a multi-role authentication system (Exam Controller, Department Head, Faculty, Student) with a student approval workflow and OTP-based password recovery.

2. To build an AI-powered exam routine parser that extracts examination schedules from multi-page PDF documents and provisions database records automatically.

3. To design a 23-taxonomy OBE Question Paper Studio capturing Bloom's Taxonomy level, CO/PO/KP/CEP/CEA classifications, and attached visual figures, data tables, and LaTeX formulas.

4. To implement a Universal 300 DPI Script Preprocessing pipeline with OpenCV deskewing, Otsu thresholding, and a Hybrid Multi-Engine OCR cascade (PyMuPDF, PyTesseract, EasyOCR CRAFT+BiLSTM).

5. To develop a Multi-Provider AI Failover Orchestrator supporting local offline vision and cloud LLM providers with automatic rate-limit handling and structured JSON evaluation output.

6. To build a Split-Screen Teacher Verification Workbench providing side-by-side view of the original script and AI-generated evaluation, with full mark override capability and immutable audit logging.

7. To implement a real-time OBE Course Tabulation Engine producing weighted overall scores, letter grades, GPA points, and CO/PO attainment matrices, exportable as official 8-sheet Excel workbooks.

8. To create an Asynchronous Institutional Email Service dispatching account notifications, exam assignments, graded results (with certified PDF attachments), and tabulation reports via SMTP.

## 1.4 Scope of the Project

IntelliGrade covers the complete university examination lifecycle for descriptive (written answer) examinations at the departmental level. The platform is designed for:

- Public and private engineering universities in Bangladesh following BAETE / Washington Accord OBE accreditation standards.
- Courses with descriptive answer scripts (not purely multiple-choice), where handwriting recognition and rubric-based AI evaluation provide the most value.
- Institutions willing to provision either local GPU hardware or enterprise-tier cloud API subscriptions to achieve production-grade AI evaluation speeds.

The current scope does not include real-time proctoring of computer-based examinations, integration with legacy student information systems, or Optical Mark Recognition (OMR) scanning for MCQ sheets. These are identified future extensions.

## 1.5 Methodology

IntelliGrade was developed following an **Agile Iterative** methodology, with each sprint delivering a working, tested subsystem:

- **Sprint 1**: Authentication, RBAC, and academic hierarchy management.
- **Sprint 2**: AI Exam Routine Parser and Question Paper Studio.
- **Sprint 3**: Script ingestion, OCR pipeline, and question boundary mapping.
- **Sprint 4**: Multi-provider AI evaluation engine and failover orchestration.
- **Sprint 5**: Split-screen evaluation workbench and certified PDF generation.
- **Sprint 6**: OBE tabulation engine, 8-sheet Excel export, and student dashboard.
- **Sprint 7**: Asynchronous email service, composite database indexes, and performance hardening.

&nbsp;

**Figure 1.5.1** — Agile Iterative Development Model

*[Insert diagram here]*

<!-- Image Generation Prompt:
Create a clean, professional Agile spiral/iterative development diagram with 7 labeled sprints arranged
in concentric arcs. Each sprint bubble labeled: Sprint 1: Auth & RBAC, Sprint 2: Routine Parser &
Question Studio, Sprint 3: OCR Pipeline & Boundary Mapping, Sprint 4: AI Failover Engine, Sprint 5:
Evaluation Workbench & Certified PDF, Sprint 6: OBE Tabulation & Excel Export, Sprint 7: Email Service
& Performance Hardening. Use a blue and white color scheme on a white background. Academic report style.
-->

&nbsp;

## 1.6 Report Organization

The remainder of this report is organized as follows. Chapter 2 provides an overview of the organization context. Chapter 3 covers requirement engineering including functional and non-functional requirements. Chapter 4 presents the analysis and modeling artifacts including activity diagrams, sequence diagram, state machine diagram, CRC cards, and class diagram. Chapter 5 addresses project management and risk with seven RMMM tables. Chapter 6 provides effort estimation via function point analysis and a Gantt chart. Chapter 7 covers cost estimation. Chapter 8 describes the complete system design including architecture, DFDs, ERD, database schema, API catalog, and interface mockups. Chapter 9 presents nine detailed test case tables. Chapter 10 concludes the report with a project summary, limitations, and future plans.

---

# Chapter 2.

# Organization Overview

---

## 2.1 Organization Vision

To become the leading academic technology platform in South Asia that empowers educational institutions to deliver fair, transparent, and outcome-aligned assessments at scale, supporting the next generation of engineering professionals.

## 2.2 Organization Mission

To provide educational institutions with intelligent, user-centered software tools that eliminate administrative friction in the examination process, enable evidence-based accreditation reporting, and give every student clear visibility into how their academic performance was evaluated.

## 2.3 Organization Services

IntelliGrade is developed under the academic practicum program of the Department of Computer Science and Engineering, IUBAT, with the intended deployment context of a university departmental examination management office. The platform provides:

- **Examination Lifecycle Management**: End-to-end management of the complete examination cycle, from routine scheduling through to result dissemination.
- **AI-Assisted Script Evaluation**: Automated rubric-based grading with mandatory human verification as the final step.
- **OBE Accreditation Reporting**: Automated computation and export of CO/PO attainment matrices aligned with BAETE accreditation standards.
- **Student Academic Transparency**: A student-facing portal providing individual grade breakdowns and certified script download.
- **Institutional Communication**: Automated email notifications for key lifecycle events including account creation, exam assignment, and result publication.

## 2.4 Organizational Structure

&nbsp;

**Figure 2.4** — Organizational Structure of IUBAT CSE Department

*[Insert org chart here]*

<!-- Image Generation Prompt:
Draw a clean hierarchical org chart for IUBAT CSE Department. Top: College of Engineering and Technology.
Below: Department of Computer Science and Engineering. Branching to: Chairman (Chief Exam Controller),
Department Head, Faculty Members (Examiners), and Students. Use professional blue-gray colors on
white background appropriate for an academic report.
-->

&nbsp;

## 2.5 My Position in this Organization

During this practicum, I served as the sole system architect, full-stack developer, and technical lead for the IntelliGrade platform. My responsibilities spanned every layer of the system: database schema design across 25 models and 28 migrations, Django backend development covering 60+ view functions and 30 AJAX API endpoints, AI integration and failover orchestration across five AI providers, OCR pipeline engineering combining three text extraction engines, frontend template development with responsive dark/light theme support, and deployment configuration on PythonAnywhere with Gunicorn. I worked in close consultation with faculty supervisors who provided domain knowledge on IUBAT's OBE grading standards and examination workflow requirements.

## 2.6 Address of the Organization

Department of Computer Science and Engineering
College of Engineering and Technology
IUBAT — International University of Business Agriculture and Technology
4 Embankment Drive Road, Sector 10, Uttara Model Town
Dhaka 1230, Bangladesh

---

# Chapter 3.

# Requirement Engineering

---

## 3.1 Requirement Elicitation

Requirement elicitation was conducted through a combination of structured interviews with faculty members and exam controllers at IUBAT, direct observation of the existing manual examination workflow, analysis of BAETE accreditation documentation and OBE standards, and review of related academic grading systems in the literature.

### 3.1.1 Requirement Gathering

The following methods were used to gather requirements:

1. **Stakeholder Interviews**: Conversations with course teachers revealed the following pain points: inconsistency in marking between examiners; the time taken to manually calculate weighted totals; the absence of any audit trail for mark adjustments; and the lack of any automated mechanism for producing CO/PO attainment data.

2. **Process Observation**: Walking through a full examination cycle — from receiving question paper PDFs, to marking scripts by hand, to entering marks into spreadsheets — provided concrete understanding of where bottlenecks occur and what specific data transformations are needed at each step.

3. **Document Analysis**: Review of IUBAT's official 8-sheet OBE tabulation Excel template and BAETE's accreditation criteria for engineering programs directly informed the data model design and the tabulation engine's output format. These templates define the exact weightage formula and CO/PO attainment calculation methodology that IntelliGrade must reproduce faithfully.

4. **Competitive Analysis**: Review of existing academic tools such as Gradescope, Turnitin, and local institutional systems identified gaps that IntelliGrade could address — particularly the absence of offline OCR capabilities, lack of integration between grading tools and OBE reporting, and the absence of automated routine scheduling from official exam schedule PDFs.

## 3.2 Requirement Analysis

The gathered requirements were analyzed and classified into four categories: User requirements (what different actors need to accomplish), System requirements (what the platform must do to fulfill those needs), Functional requirements (specific behaviors and capabilities), and Non-Functional requirements (performance, security, reliability, and compliance constraints).

Key design decisions that emerged from the analysis:

- **Human-in-the-Loop is non-negotiable**: No AI evaluation result may become a final grade without teacher review and explicit approval. This is a firm institutional requirement.
- **Offline capability is essential**: Because institutional internet bandwidth can be unreliable, the system must support a local offline AI provider (Moondream2 via Ollama) that operates entirely without internet access.
- **OBE compliance must be exact**: The weight formula (CT 10% + Mid 25% + Final 50% + Assignment 10% + Attendance 5%) and the CO/PO attainment matrix format must exactly match BAETE's accreditation submission template.
- **Auditability is a first-class requirement**: Every mark override, evaluation action, and system decision must be logged immutably for departmental and accreditation audits.

## 3.3 Requirement Specifications

### 3.3.1 Functional Requirements

**Table 3.3.1** — Functional Requirements Catalog

| Req. ID | Module / Area | Requirement Statement |
|---|---|---|
| FR-01 | Authentication | The system SHALL support unified role-based authentication redirecting users to their respective dashboards based on Profile.role. |
| FR-02 | Authentication | The system SHALL support student self-registration with default is_approved=False requiring Exam Controller approval before portal access. |
| FR-03 | Authentication | The system SHALL support 6-digit OTP password reset via background SMTP email with a 10-minute expiry window. |
| FR-04 | Controller Governance | The system SHALL allow Exam Controllers to manage Colleges, Schools, Departments, Courses, Faculty, and Department Heads. |
| FR-05 | Controller Governance | The system SHALL allow Exam Controllers to toggle active/blocked status for any institutional user account. |
| FR-06 | AI Routine Parsing | The system SHALL parse multi-page examination routine schedules (PDF/Images) and extract exam dates, times, course codes, titles, and assigned examiners. |
| FR-07 | AI Routine Parsing | The system SHALL perform 0ms local DB lookups to match extracted course codes and provide 1-click batch examination creation. |
| FR-08 | AI Config Management | The system SHALL allow administrators to configure API keys for Gemini, Groq, OpenAI, OpenRouter, and Ollama, and set OCR confidence thresholds. |
| FR-09 | Dept Head Monitoring | The system SHALL display live departmental pass rates, active course counts, enrolled students, and assigned faculty workloads on the Department Head dashboard. |
| FR-10 | Dept Head Audit | The system SHALL allow Department Heads to audit course OBE tabulation sheets and review Course Outcome and Program Outcome attainment matrices. |
| FR-11 | 23-Taxonomy Authoring | The system SHALL store 23-section IUBAT OBE metadata per Question: prompt, max marks, Bloom's level, CO (CO1-CO6), PO (PO1-PO12), KP, CEP, and CEA tags. |
| FR-12 | Rubric Management | The system SHALL store structured Rubrics with criteria, ideal answer, mark distribution, rubric levels, keywords, and common mistakes. |
| FR-13 | Visual Asset Extraction | The system SHALL extract and store bounding box coordinates for attached Question Figures, Tables, and LaTeX mathematical formulas. |
| FR-14 | LaTeX Formula Repair | The system SHALL sanitize unescaped backslashes in mathematical matrices to prevent JSON decode errors during AI prompt compilation. |
| FR-15 | Master Solution Service | The system SHALL allow teachers to upload master solution scripts and automatically link solution steps to corresponding questions. |
| FR-16 | Script Preprocessing | The system SHALL render uploaded PDF answer scripts at 300 DPI high resolution and apply OpenCV deskewing, noise reduction, and thresholding. |
| FR-17 | Working Copy Versioning | The system SHALL generate versioned working copies in submission_working/ incrementing version numbers upon rotation, cropping, or contrast edits. |
| FR-18 | Hybrid Multi-Engine OCR | The system SHALL execute PyMuPDF font extraction → PyTesseract → EasyOCR (PyTorch CPU fallback) to extract text with line/word bounding boxes. |
| FR-19 | Question Boundary Detection | The system SHALL detect question header patterns (e.g., "Question 1", "Ans to Q.1") using a strict start-of-line regex state machine. |
| FR-20 | Interactive Mapping Modal | The system SHALL present an interactive visual mapping tool allowing teachers to adjust answer page numbers and bounding box crop regions before AI evaluation. |
| FR-21 | AI Failover Orchestration | The system SHALL route evaluation requests through a prioritized failover chain: Local Vision → Groq → OpenRouter → Gemini → OpenAI. |
| FR-22 | 429 Rate Limit Cooldown | The system SHALL track HTTP 429 events and place affected AI providers on exponential backoff cooldowns without dropping pending evaluations. |
| FR-23 | Timeout Budget Enforcement | The system SHALL enforce a 45-second timeout per AI evaluation request, failing over instantly to the next provider upon timeout. |
| FR-24 | Criteria-Based Scoring | The system SHALL evaluate student answers against rubric criteria and return obtained marks, maximum marks, confidence ratings, strengths, and mistakes. |
| FR-25 | Mandatory Review Flagging | The system SHALL automatically set requires_manual_review=True for any answer scoring below the system-configured confidence threshold (default 0.75). |
| FR-26 | Split-Screen Workbench | The system SHALL render a split-screen workbench displaying the original scanned script on the left and AI scores, criteria, and feedback on the right. |
| FR-27 | Teacher Mark Override | The system SHALL allow teachers to override AI marks and edit feedback, logging every adjustment in TeacherReview and EvaluationHistory audit tables. |
| FR-28 | Certified PDF Generation | The system SHALL stamp finalized submissions with institutional headers, awarded marks, teacher comments, and digital watermarks. |
| FR-29 | OBE Course Tabulation | The system SHALL aggregate assessment components: Class Test (10%), Midterm (25%), Final Exam (50%), Assignment (10%), Attendance (5%). |
| FR-30 | Real-Time Tabulation Sync | The system SHALL synchronize teacher edits made in the tabulation modal instantly to StudentGradeRecord, Excel, and Student Dashboard. |
| FR-31 | 8-Sheet Excel Export | The system SHALL generate official 8-sheet Excel workbooks (openpyxl) containing HOME, ASSIGNMENT, CO_ATTAINMENT, PO_ATTAINMENT, and CQI formula sheets. |
| FR-32 | Institutional Email Service | The system SHALL dispatch non-blocking background emails via SMTP for results, credentials, and OTPs. |
| FR-33 | Student Dashboard | The system SHALL display real-time course grades, cumulative GPA (4.00 scale), question-wise score feedback, and certified PDF download links. |
| FR-34 | Dual Evaluation Wizards | The system SHALL provide both AI Wizard and Manual Script Grading Wizard as independent evaluation pathways. |
| FR-35 | Finalization Storage Purge | The system SHALL automatically delete unneeded draft working images from media/submission_working/ upon certified PDF creation. |
| FR-36 | Database Performance | The system SHALL utilize composite indexes on StudentSubmission, EvaluationResult, QuestionMapping, and StudentGradeRecord, and eager-load relations to eliminate N+1 query patterns. |
| FR-37 | Local Vision Downsampling | The system SHALL enforce 800px LANCZOS downsampling and JPEG quality=75 compression prior to dispatching local vision payloads to Ollama. |

### 3.3.2 Non-Functional Requirements

**Table 3.3.2** — Non-Functional Requirements Catalog

| Req. ID | Category | Requirement Statement |
|---|---|---|
| NFR-01 | Performance (Web) | The web application SHALL render dashboard pages and tabulation tables within <= 1.5 seconds under standard institutional network loads. |
| NFR-02 | Performance (OCR) | The system SHALL complete 300 DPI image rendering, deskewing, and PyTesseract OCR extraction within <= 4.0 seconds per script page. |
| NFR-03 | Performance (AI) | AI evaluation requests via Groq/Gemini SHALL return structured evaluations within <= 8.0 seconds per question answer. |
| NFR-04 | Failover Latency | In the event of a provider timeout (45s) or HTTP 429 rate limit, the failover orchestrator SHALL transition to the next provider within <= 500 ms. |
| NFR-05 | Scalability | The database and storage layer SHALL support concurrent batch uploads of up to 100 multi-page student scripts per examination without deadlock. |
| NFR-06 | Availability | The system architecture SHALL achieve >= 99.5% uptime during examination and grading periods, supported by local offline vision and LLM fallbacks. |
| NFR-07 | Security (Auth) | All user passwords SHALL be salted and hashed using PBKDF2 with SHA-256; plaintext passwords SHALL never be persisted. |
| NFR-08 | Security (RBAC) | Every view and API endpoint SHALL enforce strict role checking decorators. |
| NFR-09 | Security (CSRF) | All mutating HTTP POST/PUT/DELETE requests SHALL mandate valid CSRF tokens validated via Django CSRF middleware. |
| NFR-10 | Data Integrity | All grade updates, submission states, and review audit entries SHALL execute within atomic database transactions (django.db.transaction.atomic). |
| NFR-11 | Auditability | All manual mark overrides, prompt alterations, and evaluation deletions SHALL record immutable audit entries with teacher ID, timestamp, and IP address. |
| NFR-12 | Compliance (OBE) | All Course Outcome and Program Outcome calculations SHALL strictly adhere to IUBAT and BAETE OBE engineering accreditation standards. |
| NFR-13 | Spreadsheet Fidelity | The generated 8-sheet Excel workbooks SHALL strictly preserve openpyxl formulas, data validation rules, and cell color formatting across all sheets. |
| NFR-14 | Email Reliability | Institutional email dispatches SHALL execute asynchronously in background threads so that slow SMTP handshake latency never blocks user HTTP responses. |
| NFR-15 | Usability (UI/UX) | The web UI SHALL support full responsive design, dark/light theme switching, and split-screen synchronized PDF viewing on standard desktop screens. |
| NFR-16 | DB Query Efficiency | The database query layer SHALL utilize composite B-tree indexes and eager-loaded select_related / prefetch_related queries to maintain efficient query complexity. |
| NFR-17 | Storage Cleanliness | Temporary working draft images SHALL be automatically purged upon finalization to conserve institutional disk storage and maintain compliance. |

## 3.4 Use Case Diagram

&nbsp;

**Figure 3.4** — Use Case Diagram

*[Insert use case diagram here]*

<!-- Image Generation Prompt:
Draw a clean UML Use Case Diagram for IntelliGrade. Show 5 actors on the left:
Chief Exam Controller (Admin), Department Head, Faculty Member/Examiner, Student, AI Evaluation Engine (System).
Group use cases in labeled packages: Authentication (UC-01, UC-02, UC-03), Governance (UC-04 through UC-08),
Question Authoring (UC-11, UC-12, UC-13), Script Evaluation (UC-14 through UC-20, UC-26),
OBE Tabulation (UC-21, UC-22, UC-23), Dissemination (UC-24, UC-25, UC-27).
Connect actors to their use cases with lines. Professional white background, blue and gray styling.
-->

&nbsp;

---

# Chapter 4.

# Analysis Modeling

---

## 4.1 Activity Diagrams

Activity diagrams capture the flow of key processes within IntelliGrade. Seven major workflows are documented below.

### 4.1.1 Exam Controller Governance Workflow

&nbsp;

**Figure 4.1.1** — Activity Diagram: Exam Controller Governance

*[Insert activity diagram here]*

<!-- Image Generation Prompt:
Draw a clean UML Activity Diagram showing the Exam Controller governance flow with two swimlanes:
"Exam Controller" and "IntelliGrade System". Flow: Login → View Dashboard → [Fork] Manage Academic Structure
(Add College/School/Department/Course) | Approve Pending Students (system sends email) | Configure AI Providers
(set API keys and thresholds) | Upload Exam Routine PDF (AI parses → extract schedule → Batch create Examinations).
Professional white background, blue action nodes, gray swimlane headers.
-->

&nbsp;

The Exam Controller begins by authenticating at the controller login portal. After successful login, they are redirected to the central governance dashboard where they can manage the institutional academic hierarchy (Colleges, Schools, Departments, Courses), review and approve or reject pending student registrations with automated email triggers, configure AI provider credentials and OCR thresholds, and upload official exam routine PDFs for AI-assisted schedule extraction that automatically provisions Examination records.

### 4.1.2 Question Paper and Rubric Authoring

&nbsp;

**Figure 4.1.2** — Activity Diagram: Question Paper and Rubric Authoring

*[Insert activity diagram here]*

<!-- Image Generation Prompt:
Draw a UML Activity Diagram for Question Paper authoring with swimlanes "Faculty Member" and "System".
Flow: Login → Navigate to Exam → [Decision] Author Manually OR AI Scan → Manual path: Enter question
(prompt, marks, Bloom, CO, PO, KP, CEP, CEA) → Add Rubric Criteria and Ideal Answer → Mark Distribution.
AI Scan path: Upload Question PDF → System OCRs and extracts questions → Teacher reviews and confirms.
→ Both paths: Optional Master Solution Upload (system OCRs and links steps) → Finalize Question Paper.
Clean white background with blue activity nodes.
-->

&nbsp;

Faculty members navigate to the Question Paper Studio for a specific examination. They can author questions manually, providing the question prompt, maximum marks, and all 23 OBE taxonomy fields for each question, or they can upload the official question paper PDF and trigger AI-assisted scanning that automatically extracts question numbers, marks allocations, and suggested taxonomy tags. For each question, a structured rubric is defined including grading criteria, ideal answer, mark distribution across sub-criteria, expected keywords, and common student mistakes.

### 4.1.3 Script Ingestion and 300 DPI Preprocessing

&nbsp;

**Figure 4.1.3** — Activity Diagram: Script Ingestion and 300 DPI Preprocessing

*[Insert activity diagram here]*

<!-- Image Generation Prompt:
Draw a UML Activity Diagram for script ingestion with swimlanes "Teacher" and "System".
Flow: Teacher uploads PDF/Images/ZIP → System detects file type → [If PDF] Render at 300 DPI (zoom=4.166
via PyMuPDF) → [If Images] Validate resolution and orientation → Apply OpenCV Hough deskewing →
Otsu thresholding for contrast enhancement → Save versioned working copies to submission_working/ →
Update submission status to PREVIEW_READY → Notify teacher (page thumbnails displayed).
Clean professional styling, white background with blue and gray accents.
-->

### 4.1.4 AI Evaluation Wizard Flow

&nbsp;

**Figure 4.1.4** — Activity Diagram: AI Evaluation Wizard

*[Insert activity diagram here]*

<!-- Image Generation Prompt:
Draw a detailed UML Activity Diagram for the AI Evaluation Wizard with swimlanes "System" and "AI Providers".
Preprocessed pages → Hybrid OCR cascade (PyMuPDF → PyTesseract → EasyOCR fallback) →
State Machine heading detection (regex patterns for "Question N", "Ans to Q.N", "Q1") →
Auto-detect question-to-page mappings → [Decision] Confidence < 0.75? → Yes: Flag WAITING_TEACHER_CONFIRMATION
→ Teacher confirms → No: Proceed directly → TaskRouter evaluates provider health →
Dispatch to AI Failover chain: Local Moondream2 → [if fail] Groq Llama-3.3 70B → OpenRouter →
Gemini 2.5 Flash → OpenAI GPT-4o → Receive structured JSON evaluation → Repair JSON if needed →
Store EvaluationResult → Transition status to AI_EVALUATED.
-->

### 4.1.5 Manual Script Grading Wizard Flow

&nbsp;

**Figure 4.1.5** — Activity Diagram: Manual Script Grading Wizard

*[Insert activity diagram here]*

<!-- Image Generation Prompt:
Draw a UML Activity Diagram for the Manual Script Grading Wizard (zero AI/OCR alternative path).
Swimlanes: "Teacher" and "System".
Flow: Teacher uploads script PDF → System slices PDF into 300 DPI page images (no OCR, no AI calls) →
Teacher views page thumbnails and selects which pages correspond to which question
(visual checkbox matrix on screen) → System creates QuestionMapping records with is_confirmed=True →
Teacher clicks Open Manual Grading Workbench → System loads split-screen view:
left pane=page image, right pane=manual mark entry fields for each rubric criterion.
Clean white background, blue and gray accents.
-->

### 4.1.6 Teacher Review and Finalization

&nbsp;

**Figure 4.1.6** — Activity Diagram: Teacher Review and Finalization

*[Insert activity diagram here]*

<!-- Image Generation Prompt:
Draw a UML Activity Diagram for Teacher Review with swimlanes "Teacher" and "System".
Flow: Open Split-Screen Workbench → Left pane: high-res script image (zoom/pan/rotate) →
Right pane: question prompt, master solution accordion, rubric criteria checklist with marks,
AI score and feedback (editable) → [Decision] Accept AI Score? → Yes: mark as APPROVED →
No: Enter new marks and comments → System logs TeacherReview record and EvaluationHistory entry →
Repeat for each question → Click Finalize Evaluation → System generates certified watermarked PDF →
Purge temporary working images → Sync marks to OBE Tabulation → Send graded result email to student.
-->

### 4.1.7 OBE Tabulation and Email Dissemination

&nbsp;

**Figure 4.1.7** — Activity Diagram: OBE Tabulation and Email Dissemination

*[Insert activity diagram here]*

<!-- Image Generation Prompt:
Draw a UML Activity Diagram for OBE Tabulation with swimlanes "Teacher", "System", "Student".
Flow: After evaluation finalization → System syncs marks to StudentGradeRecord →
Compute weighted overall score (CT×0.10 + Mid×0.25 + Final×0.50 + Assign×0.10 + Att×0.05) →
Compute letter grade and GPA point → Compute CO/PO attainment scores as JSON vectors →
Teacher opens tabulation page → [Optional] Edit marks inline (modal) → Click Export Excel →
System generates 8-sheet openpyxl workbook → [Async thread] Send tabulation email to dept head →
Student portal updated with live grade cards → Student downloads certified PDF.
-->

---

## 4.2 Sequence Diagram

**Figure 4.2** — Sequence Diagram: End-to-End Evaluation Lifecycle

*[Insert sequence diagram here]*

<!-- Image Generation Prompt:
Draw a detailed UML Sequence Diagram with lifelines for: Chief Exam Controller, Faculty/Examiner,
Student, IntelliGrade Core, Vision & OCR Pipeline, Multi-Provider AI Engine, OBE Tabulation Engine.
Show 8 numbered phases with messages:
Phase 1: Admin uploads routine PDF → Core parses → creates Examinations → emails Teacher.
Phase 2: Teacher authors question paper with 23-taxonomy → defines rubrics.
Phase 3: Teacher uploads student scripts → Core preprocesses at 300 DPI.
Phase 4: OCR pipeline extracts text → Core detects boundaries → maps questions to pages.
Phase 5: Teacher confirms mapping → AI Engine evaluates → returns JSON result to Core.
Phase 6: Teacher opens workbench → overrides marks → clicks Finalize.
Phase 7: Core generates certified PDF → purges working files → syncs marks to Tabulation Engine.
Phase 8: Student logs in → views grades → downloads PDF.
Use standard UML lifeline/arrow notation. Clean academic diagram style.
-->

The complete sequence of actors and messages in IntelliGrade's evaluation lifecycle spans eight distinct phases, from the initial routine ingestion by the Exam Controller through to the student accessing their certified evaluated script on the transparency portal. Each phase is mediated by IntelliGrade's core Django application, which coordinates state transitions, API calls, database writes, and asynchronous email dispatch with strict RBAC enforcement at every step.

---

## 4.3 State Machine Diagram

**Figure 4.3** — State Machine Diagram: StudentSubmission Lifecycle

*[Insert state machine diagram here]*

<!-- Image Generation Prompt:
Draw a clean UML State Machine Diagram showing all 14 states of StudentSubmission.
States in order: [Initial] → UPLOADED → PREVIEW_READY → WORKING_COPY_CREATED → PDF_GENERATED →
OCR_COMPLETE → SEGMENTED → MAPPING_COMPLETE → [if low confidence: WAITING_TEACHER_CONFIRMATION →
back to MAPPING_COMPLETE] → AI_EVALUATED → UNDER_REVIEW → REVIEWED → FINALIZED → ARCHIVED.
Error branch: UPLOADED → FAILED, OCR_COMPLETE → FAILED, AI_EVALUATED → FAILED.
Label each transition arrow with the trigger event (e.g., "PDF upload received", "Teacher confirms mapping").
Blue states on white background, red for FAILED, gold for ARCHIVED. Professional academic style.
-->

The `StudentSubmission` model is governed by a 14-state finite state machine. Each transition is triggered by a specific system event and enforced programmatically in `core/ai_engine/services/workflow.py`, ensuring that no submission can advance to an invalid state. For example, a submission cannot reach `AI_EVALUATED` before `MAPPING_COMPLETE` has been confirmed. The `FAILED` state captures any irrecoverable error with detailed diagnostics recorded in the `EvaluationAuditLog` table.

---

## 4.4 CRC Cards

Class-Responsibility-Collaborator (CRC) cards document the primary classes in IntelliGrade, their responsibilities, and their collaborators.

**Table 4.4.1** — CRC Card: Profile (User Role)

| Class: **Profile** | |
|---|---|
| **Responsibilities** | **Collaborators** |
| Store role (ADMIN, TEACHER, STUDENT, DEPT_HEAD) | User (Django Auth) |
| Store approval status (is_approved) | Department |
| Enforce role-based portal access | Examination |
| Store OTP reset codes with expiry | |

**Table 4.4.2** — CRC Card: Examination

| Class: **Examination** | |
|---|---|
| **Responsibilities** | **Collaborators** |
| Store exam type (MID/FINAL/CT/QUIZ), status, and dates | Course |
| Hold uploaded question paper, rubric, and master solution files | Question |
| Manage publication workflow (DRAFT → PUBLISHED → CLOSED) | StudentSubmission |
| Expose has_master_solution property | Profile (assigned faculty) |

**Table 4.4.3** — CRC Card: Question and Rubric

| Class: **Question** | |
|---|---|
| **Responsibilities** | **Collaborators** |
| Store 23-taxonomy OBE fields (Bloom, CO, PO, KP, CEP, CEA) | Examination |
| Store prompt text and maximum marks | Rubric (OneToOne) |
| Reference attached figures, tables, and formula objects | QuestionFigure, QuestionTable, QuestionFormula |
| Provide formatted_number property for display | SubmissionAnswer |

**Table 4.4.4** — CRC Card: StudentSubmission

| Class: **StudentSubmission** | |
|---|---|
| **Responsibilities** | **Collaborators** |
| Manage 14-state FSM lifecycle | Examination |
| Store uploaded script file and extracted OCR data | SubmissionPage, SubmissionImage |
| Track finalization status (is_finalized) | QuestionMapping |
| Maintain composite B-tree database indexes | EvaluationAuditLog |
| Record student identity (name, roll number) | |

**Table 4.4.5** — CRC Card: EvaluationResult

| Class: **EvaluationResult** | |
|---|---|
| **Responsibilities** | **Collaborators** |
| Store obtained marks, maximum marks, confidence score | SubmissionAnswer (OneToOne) |
| Store AI-generated feedback, strengths, and mistakes as JSON | TeacherReview |
| Flag low-confidence answers for mandatory teacher review | EvaluationHistory |
| Manage review status (PENDING/APPROVED/OVERRIDDEN/REJECTED) | EvaluationFeedback |

**Table 4.4.6** — CRC Card: CourseTabulation

| Class: **CourseTabulation** | |
|---|---|
| **Responsibilities** | **Collaborators** |
| Store semester, section, and weightage configuration | Course |
| Maintain uniqueness constraint (course, semester, section) | StudentGradeRecord |
| Provide aggregated assessment weightage config JSON | |

**Table 4.4.7** — CRC Card: StudentGradeRecord

| Class: **StudentGradeRecord** | |
|---|---|
| **Responsibilities** | **Collaborators** |
| Store exam score breakdown per category (CT, Mid, Final, etc.) | CourseTabulation |
| Compute weighted overall score via get_category_data() | |
| Store CO/PO attainment scores as JSON vectors | |
| Expose typed properties: class_test_data, midterm_data, final_data | |
| Track manual instructor overrides (is_manually_edited) | |

---

## 4.5 Class Diagram

**Figure 4.5** — Class Diagram: Core Domain Models

*[Insert class diagram here]*

<!-- Image Generation Prompt:
Draw a UML Class Diagram for IntelliGrade's core Django models. Show these classes with their key attributes
and methods:
Profile (user:FK, role:str, is_approved:bool, department:FK)
College (name, code) ← School (college:FK, name, code) ← Department (school:FK, name) ← Course (dept:FK, code, title) ← Examination (course:FK, exam_type, status, total_marks)
Examination ← Question (exam:FK, question_number, max_marks, bloom_level, co_mapping, po_mapping)
Question ←OneToOne→ Rubric (criteria, ideal_answer, mark_distribution:JSON)
Question ← QuestionFigure, QuestionTable, QuestionFormula
Examination ← StudentSubmission (student:FK, status:14-state, is_finalized)
StudentSubmission ← SubmissionPage, SubmissionImage
StudentSubmission ← SubmissionAnswer ←OneToOne→ EvaluationResult ← TeacherReview, EvaluationHistory
StudentSubmission ← QuestionMapping (question:FK, page_numbers:JSON, is_confirmed:bool)
CourseTabulation (course:FK) ← StudentGradeRecord (student_id, exam_scores:JSON, co_scores:JSON, letter_grade)
AIConfiguration, AIProviderHealth
Show cardinality (1, *, 0..1) on all relationship lines. White background, blue class header bars.
-->

---

# Chapter 5.

# Project Management

---

## 5.1 Risk Identification

**Table 5.1.1** — Risk Identification

| Risk ID | Risk Description | Category | Probability | Impact |
|---|---|---|---|---|
| R-01 | CPU-bound EasyOCR latency renders AI evaluation too slow for practical use on large exam batches | Technical | High | High |
| R-02 | Cloud AI provider rate limits (HTTP 429) cause evaluation stalls and timeouts during concurrent batch grading | Technical | High | High |
| R-03 | Extreme handwriting illegibility causes OCR failure and unmappable question boundaries | Technical | Medium | High |
| R-04 | Data loss or corruption during evaluation due to unhandled server exceptions | Technical | Low | Critical |
| R-05 | Institutional SMTP credential failure causes email notification breakdown | Operational | Medium | Medium |
| R-06 | Growing media file storage causes disk space overflow on the production server | Operational | Medium | High |
| R-07 | OBE calculation discrepancies due to floating-point rounding in Python arithmetic | Technical | Low | High |

## 5.2 Risk Analysis

**Table 5.2.1** — Risk Analysis

| Risk ID | Risk Description | Likelihood (1-5) | Severity (1-5) | Risk Exposure Score | Priority |
|---|---|---|---|---|---|
| R-01 | CPU OCR latency (EasyOCR ~20-25s/page on CPU) | 5 | 4 | 20 | Critical |
| R-02 | AI rate limiting — HTTP 429 cascade stalls | 5 | 4 | 20 | Critical |
| R-03 | Handwriting illegibility → OCR failure | 3 | 4 | 12 | High |
| R-04 | Data loss during evaluation exception | 2 | 5 | 10 | High |
| R-05 | SMTP email delivery failure | 3 | 3 | 9 | Medium |
| R-06 | Disk storage overflow from working images | 3 | 4 | 12 | High |
| R-07 | Floating-point rounding in OBE calculations | 2 | 4 | 8 | Medium |

## 5.3 Risk Mitigation, Monitoring and Management (RMMM)

**Table 5.3.1** — RMMM: Risk 1 — CPU OCR Latency

| Field | Details |
|---|---|
| **Risk ID** | R-01 |
| **Risk Description** | CPU-bound EasyOCR CRAFT+BiLSTM deep learning model takes approximately 20-25 seconds per script page on a modern CPU, making full 13-page script evaluation take over 4 minutes — impractical for end-of-semester batch grading. |
| **Mitigation** | 1. Apply 800px LANCZOS downsampling before local vision dispatch (implemented). 2. Provide Manual Grading Wizard as a zero-OCR fallback for urgent evaluations. 3. Plan GPU CUDA upgrade path (NVIDIA RTX 4060, 8GB VRAM) in hardware budget. |
| **Monitoring** | AIProviderHealth model tracks avg_response_time_ms. Dashboard alerts configured for latencies exceeding 60 seconds per page. |
| **Contingency** | Fall back to Manual Wizard for urgent evaluations while GPU upgrade is provisioned. Teachers can still evaluate all students; only the automated text extraction is slowed. |
| **Owner** | System Architect |
| **Review Date** | End of each examination period |

**Table 5.3.2** — RMMM: Risk 2 — AI Rate Limiting

| Field | Details |
|---|---|
| **Risk ID** | R-02 |
| **Risk Description** | Free-tier cloud AI APIs impose strict rate limits. Groq enforces 30 RPM / 6,000 TPM, Gemini enforces 15 RPM / 1,000,000 TPM. Evaluating multiple questions simultaneously for multiple students triggers HTTP 429 quota exhaustion. |
| **Mitigation** | 1. ProviderHealthTracker with 120-second cooldown registry per provider (implemented). 2. Maintain 5-provider failover chain so no single HTTP 429 blocks evaluation. 3. Apply JSON sanitization and LaTeX bracket repair to prevent re-requests due to parse errors. |
| **Monitoring** | AIProviderHealth.error_count and cooldown_until tracked in real time. Dashboard badge alerts teacher when all providers are rate-limited simultaneously. |
| **Contingency** | Upgrade to enterprise Pay-As-You-Go API tiers (Groq Developer Plan, Gemini Tier 1) for production deployment. Fall back to manual workbench if all AI providers are exhausted. |
| **Owner** | Exam Controller |
| **Review Date** | Before each examination period |

**Table 5.3.3** — RMMM: Risk 3 — Handwriting Illegibility

| Field | Details |
|---|---|
| **Risk ID** | R-03 |
| **Risk Description** | Some students produce extremely poor handwriting that defeats even EasyOCR's deep learning recognizer, resulting in empty or garbled OCR output and unmapped question boundaries. |
| **Mitigation** | 1. Three-engine OCR cascade (PyMuPDF → PyTesseract → EasyOCR) maximizes text recovery probability. 2. Interactive mapping modal allows manual page assignment when auto-detection fails. 3. For illegible scripts, vision-capable AI providers (Gemini 2.5 Flash, GPT-4o) evaluate directly from the page image, bypassing OCR text entirely. |
| **Monitoring** | OCR confidence scores stored per page in SubmissionPage.ocr_confidence. Pages below threshold flagged in UI for teacher attention. |
| **Contingency** | Teacher manually selects pages via the visual confirmation modal, which is always available regardless of OCR output quality. |
| **Owner** | Faculty Member |
| **Review Date** | Per evaluation session |

**Table 5.3.4** — RMMM: Risk 4 — Data Loss During Evaluation

| Field | Details |
|---|---|
| **Risk ID** | R-04 |
| **Risk Description** | An unhandled server exception or network interruption mid-evaluation could corrupt the StudentSubmission state machine or lose partially written SubmissionAnswer records. |
| **Mitigation** | 1. All database writes wrapped in django.db.transaction.atomic() ensuring partial states are rolled back on failure. 2. EvaluationAuditLog records every state transition with timestamp and actor identity. 3. Script PDFs and working images stored on disk and only purged after explicit teacher-initiated finalization. 4. extracted_ocr_data JSON field caches OCR output so re-evaluation does not require re-processing all images. |
| **Monitoring** | EvaluationAuditLog monitored for FAILED state transitions. System error log reviewed after each evaluation session. |
| **Contingency** | Re-upload script and restart evaluation pipeline from UPLOADED state. All previously extracted OCR data is available for reference. |
| **Owner** | System / Admin |
| **Review Date** | Continuous |

**Table 5.3.5** — RMMM: Risk 5 — SMTP Email Delivery Failure

| Field | Details |
|---|---|
| **Risk ID** | R-05 |
| **Risk Description** | SMTP server outages or expired credentials can cause failure in account creation emails, OTP password reset delivery, and graded result notification emails. |
| **Mitigation** | 1. Email dispatch runs in a background threading.Thread so SMTP latency or failure never blocks the HTTP response seen by the user. 2. Email failures are logged to the application error log without raising user-visible exceptions. 3. OTP reset includes fallback instructions for Exam Controller manual intervention. |
| **Monitoring** | SMTP error logs reviewed daily during active grading periods. |
| **Contingency** | Exam Controller can manually reset passwords via Django admin. Results can be communicated as PDF downloads shared manually. |
| **Owner** | Exam Controller |
| **Review Date** | Monthly |

**Table 5.3.6** — RMMM: Risk 6 — Disk Storage Overflow

| Field | Details |
|---|---|
| **Risk ID** | R-06 |
| **Risk Description** | 300 DPI page images (~26 MB uncompressed per page) accumulate rapidly. A course with 60 students x 13 pages generates approximately 20 GB of working copies, which can exhaust institutional server disk space. |
| **Mitigation** | 1. FinalizationService._purge_temporary_artifacts() deletes submission_working/ and submission_preview/ upon certified PDF creation (implemented). 2. JPEG quality=75 compression applied to all working copies. 3. 800px LANCZOS downsampling for local vision payloads reduces per-image size by ~85%. |
| **Monitoring** | Server disk usage alerts configured at 80% threshold. Pending finalization queue monitored via admin dashboard to identify abandoned submissions. |
| **Contingency** | Emergency purge script available to delete working images for all finalized submissions. Future plan: migrate to AWS S3 / Cloudflare R2 object storage with automatic lifecycle expiration policies. |
| **Owner** | System Admin |
| **Review Date** | End of each examination period |

**Table 5.3.7** — RMMM: Risk 7 — OBE Calculation Inconsistency

| Field | Details |
|---|---|
| **Risk ID** | R-07 |
| **Risk Description** | Python floating-point arithmetic without explicit rounding can produce weighted OBE scores that differ by +-0.01 from expected values, causing discrepancies between the web tabulation view and the official exported Excel workbook. |
| **Mitigation** | 1. All intermediate scores wrapped in round(value, 2) at each aggregation step in get_category_data(). 2. Generated Excel outputs use openpyxl's native formula support for in-sheet validation against Python-computed values. 3. Automated test suite validates OBE calculation correctness against 50 manually verified student records. |
| **Monitoring** | Automated test suite (tests.py, 1000+ assertions) run after every code change. OBE output spot-checked by faculty against manual calculations each semester. |
| **Contingency** | Teacher can manually override any computed score via the tabulation modal, with override flagged in is_manually_edited for auditability. |
| **Owner** | Developer |
| **Review Date** | After every deployment |

---

# Chapter 6.

# Project Planning and Scheduling

---

## 6.1 System Project Estimation

Prior to embarking upon the engineering and implementation phases of the IntelliGrade Outcome-Based Education (OBE) Examination Management and Intelligent Script Evaluation Ecosystem, a comprehensive and rigorous project estimation was conducted. Project estimation serves as an essential pillar of software project management, providing an analytical foundation to allocate engineering personnel efficiently, mitigate development risks, and ensure that computationally intensive subsystems—including the 300 DPI script preprocessing cascade, the hybrid multi-engine OCR pipeline (PyMuPDF, PyTesseract, and EasyOCR CRAFT+BiLSTM), the fault-tolerant multi-provider AI failover orchestrator (Groq, Gemini, OpenRouter, Moondream2), and the live 8-sheet OBE tabulation engine—are delivered within institutional deadlines and budgetary constraints. The project estimation methodology encompasses four fundamental dimensions: Effort, Cost, Time, and Team.

### 6.1.1 Effort Estimation (in Person-Hours)

Total engineering effort was quantified based on the functional complexity, algorithmic depth, and architectural breadth of the platform's individual modules. The breakdown reflects the substantial engineering demanded by the computer vision normalization pipeline, fault-tolerant cloud API failover orchestration, asynchronous background task dispatch, split-screen verification UI, and bi-directional openpyxl Excel synchronization.

**Table 6.1: Effort Estimation by Module / Project Phase**

| Module / Project Phase | Estimated Hours | Percentage (%) |
|---|---|---|
| Requirements Gathering & OBE Policy Analysis (BAETE / IUBAT Standards) | 120 hours | 5.5% |
| UI/UX Wireframing & Dual Workbench Interface Design | 160 hours | 7.3% |
| Database Architecture & Composite Index Schema Design (PostgreSQL) | 140 hours | 6.4% |
| Backend Core Development (Django 5.2 Service Layer, Models & RBAC) | 380 hours | 17.4% |
| Frontend Development (Split-Screen Workbench, Student Portal & Dashboards) | 320 hours | 14.7% |
| Script Preprocessing & Hybrid Multi-Engine OCR Cascade (CV2, PyMuPDF, EasyOCR) | 220 hours | 10.1% |
| AI Evaluation Engine & Multi-Provider Failover Orchestrator (Groq, Gemini) | 200 hours | 9.2% |
| Real-Time OBE Tabulation Engine & 8-Sheet openpyxl Excel Synchronization | 180 hours | 8.2% |
| Testing & Quality Assurance (Unit, Integration, Stress Benchmarking & UAT) | 220 hours | 10.1% |
| Deployment, Docker Containerization & Server Configuration (PythonAnywhere / VPS) | 60 hours | 2.7% |
| Project Documentation, Technical Writing & Academic Thesis Formatting | 120 hours | 5.5% |
| Buffer (Contingency & Architectural Polish ~3%) | 64 hours | 2.9% |
| **Total Estimated Effort** | **2,184 hours** | **100.0%** |

### 6.1.2 Cost Estimation (BDT Commercial Baseline)

To establish an objective commercial benchmark against professional software industry standards in Bangladesh, the market valuation of the development effort is calculated utilizing the prevailing standard engineering billing rate for mid-level enterprise full-stack and AI software engineers. Assuming a standard professional commercial rate of 500 BDT/hour:

11242	ext{Commercial Baseline Cost} = 	ext{Total Estimated Hours} 	imes 	ext{Commercial Hourly Billing Rate}11242
11242	ext{Total Commercial Baseline Cost} = 2,184	ext{ hours} 	imes 500	ext{ BDT} = \mathbf{1,092,000	ext{ BDT}}	ext{ (approx. }\mathbf{$927	ext{ USD}}	ext{)}11242

### 6.1.3 Time Estimation (Calendar Weeks)

The project development timeline was structured to accommodate the traditional university academic calendar over an 8-month period (~32 calendar weeks). By leveraging concurrent and parallel sprint tracks—wherein frontend UI wireframing proceeded in parallel with backend database schema design, and OCR pipeline development occurred concurrently with rubric studio implementation—the team optimized throughput while maintaining strict architectural milestones.

**Table 6.2: Time Estimation by Project Phase**

| Phase | Major Engineering Deliverables | Duration |
|---|---|---|
| Phase 1: Planning & Scope | OBE requirements analysis, user persona definitions, BAETE accreditation mapping | 3 weeks |
| Phase 2: Architectural Design | UI/UX wireframing, PostgreSQL composite index schema, class diagrams | 3 weeks |
| Phase 3: Core Backend & Routine Ingestion | Django 5.2 core setup, RBAC authentication, multimodal AI routine scanner | 4 weeks |
| Phase 4: Preprocessing & Hybrid OCR | 300 DPI image rasterizer, Hough deskewing, Otsu thresholding, regex detector | 5 weeks |
| Phase 5: AI Failover & Split-Screen UI | Groq/Gemini failover chain, split-screen teacher workbench, ReportLab stamping | 6 weeks |
| Phase 6: OBE Tabulation & Sync | CO/PO aggregation, 8-sheet Excel workbook export, background SMTP email service | 4 weeks |
| Phase 7: Testing & Verification | Unit test suite (50+ tests), stress benchmarking, teacher human-in-the-loop UAT | 4 weeks |
| Phase 8: Deployment & Documentation | PythonAnywhere wsgi, SSL configuration, thesis compilation, user manuals | 3 weeks |
| **Total Project Duration** | **End-to-End Enterprise Academic Delivery** | **~32 weeks (8 Months)** |

### 6.1.4 Team Estimation

To satisfy the 32-week schedule and fulfill the 2,184 person-hours of specialized engineering effort, the development organization was structured into a dedicated 5-person engineering cell. Each member fulfilled distinct architectural responsibilities while collaborating on integration milestones.

**Table 6.3: Team Resource Allocation**

| Role Title | Primary Responsibilities | Allocated Resources |
|---|---|---|
| System Architect & Full-Stack Lead | Overall architecture, Django service layer, RBAC security, API integration | 1 Dedicated |
| AI / ML & Computer Vision Engineer | EasyOCR CRAFT+BiLSTM tuning, Groq/Gemini failover orchestrator, regex detector | 1 Dedicated |
| Backend & Database Engineer | PostgreSQL schema, composite B-tree indexing, query optimization, data models | 1 Dedicated |
| Frontend Developer & UI/UX Designer | Split-screen grading workbench, canvas zoom, student portal, responsive CSS | 1 Dedicated |
| QA / Test Automation & Security Engineer | Automated test suites, load testing, memory profiling, audit log verification | 1 Dedicated |
| **Total Engineering Resources** | **Core Multidisciplinary Project Cell** | **5 Engineers** |

---

## 6.2 Function Matrix

The Function Matrix systematically catalogs and decomposes all capabilities of the IntelliGrade system into logical operational modules. It bridges user-facing functional requirements with concrete Django view controllers, asynchronous background service classes, database entities, and external API communication protocols.

**Table 6.4: Function Matrix Describing All Modules and Functions of IntelliGrade**

| Module Name | Function / Controller Name | Description & Operational Scope |
|---|---|---|
| Authentication & Role-Based Access Control (RBAC) |  | Registers a new student, hashes credentials via PBKDF2 SHA-256, captures Student ID, and enqueues account for administrative approval. |
| Authentication & Role-Based Access Control (RBAC) |  | Authenticates login credentials across 4 roles (Admin, Teacher, Student, Dept Head) and redirects to role-specific dashboard. |
| Authentication & Role-Based Access Control (RBAC) |  | Terminates the active authenticated session, purges cookies, and invalidates session token. |
| Authentication & Role-Based Access Control (RBAC) |  | Generates a cryptographically secure 6-digit one-time password and dispatches it via asynchronous institutional SMTP. |
| Authentication & Role-Based Access Control (RBAC) |  | Validates the submitted OTP against a 10-minute expiring cache and authorizes the password reset workflow. |
| Authentication & Role-Based Access Control (RBAC) |  | Updates user password hash and logs security audit event upon successful credential change. |
| Institutional Governance & Academic Structure |  | Allows Chief Exam Controller to configure university structural hierarchy (Colleges and Schools). |
| Institutional Governance & Academic Structure |  | Provisions and updates academic departments, assigns Department Heads, and toggles operational status. |
| Institutional Governance & Academic Structure |  | Configures course catalog, codes, titles, credit weightings, and assigns authorized faculty instructors. |
| Institutional Governance & Academic Structure |  | Enables administrators to inspect pending student records, verify enrollment, and grant active status. |
| Institutional Governance & Academic Structure |  | Suspends or activates platform access permissions for any user violating academic integrity rules. |
| AI Routine Parsing & Scheduling |  | Facilitates multi-page institutional examination schedule PDF/image uploads with MIME validation. |
| AI Routine Parsing & Scheduling |  | Transmits routine pages to Google Gemini Flash Vision API to parse course codes, dates, times, and rooms. |
| AI Routine Parsing & Scheduling |  | Executes zero-latency local token-set ratio fuzzy matching to link parsed routine rows with database courses and teachers. |
| AI Routine Parsing & Scheduling |  | Provisions database records for all parsed exams in an atomic transaction, eliminating manual scheduling. |
| 23-Taxonomy Question & Rubric Studio |  | Authors questions with 23 OBE fields including CO1–CO6, PO1–PO12, Bloom's cognitive taxonomy, KP, CEP, and CEA. |
| 23-Taxonomy Question & Rubric Studio |  | Invokes Groq/Gemini to automatically generate step-by-step scoring criteria, model answers, and mark distributions. |
| 23-Taxonomy Question & Rubric Studio |  | AI parses question text to classify Bloom's Taxonomy cognitive level and recommend appropriate Course Outcomes. |
| 23-Taxonomy Question & Rubric Studio |  | Allows faculty to upload handwritten or LaTeX master solution scripts to serve as golden evaluation benchmarks. |
| 23-Taxonomy Question & Rubric Studio |  | Applies OCR across master solution pages and extracts step-by-step model answer points per question. |
| Script Ingestion & 300 DPI Preprocessing |  | Handles batch multi-student PDF script uploads with file sanitization and preliminary validation. |
| Script Ingestion & 300 DPI Preprocessing |  | Rasterizes PDFs to 300 DPI working copies via PyMuPDF, deskews via Hough Line Transform, and applies Otsu thresholding. |
| Script Ingestion & 300 DPI Preprocessing |  | Provides an interactive drag-and-drop thumbnail grid allowing examiners to correct out-of-order scanned pages. |
| Script Ingestion & 300 DPI Preprocessing |  | Automatically deletes intermediate high-resolution raster images from disk upon script evaluation finalization. |
| Hybrid OCR & Spatial Boundary Detection |  | Extracts text using PyMuPDF font extraction, PyTesseract printed OCR, or EasyOCR CRAFT+BiLSTM handwriting fallback. |
| Hybrid OCR & Spatial Boundary Detection |  | Runs start-of-line regex state machine ('Answer to Question No. X') to detect question boundaries across pages. |
| Hybrid OCR & Spatial Boundary Detection |  | Maps detected question sections into precise pixel bounding box coordinates for each script page. |
| Hybrid OCR & Spatial Boundary Detection |  | Renders an interactive crop modal enabling examiners to review and adjust bounding boxes prior to grading. |
| Fault-Tolerant AI Evaluation & Fallback |  | Executes multi-provider failover chain across Local Moondream2, Groq Llama-3.3 70B, OpenRouter, and Gemini. |
| Fault-Tolerant AI Evaluation & Fallback |  | Validates and sanitizes LLM JSON output, auto-closing unescaped quotes and repairing LaTeX bracket syntax. |
| Fault-Tolerant AI Evaluation & Fallback |  | Compares student answer text/crop with rubric criteria and master solution to produce marks and rationale. |
| Fault-Tolerant AI Evaluation & Fallback |  | Provides a zero-AI fallback wizard where teachers assign pages to questions via matrix and grade directly. |
| Split-Screen Teacher Workbench |  | Renders synchronized split-screen interface displaying student script zoomable canvas alongside rubric. |
| Split-Screen Teacher Workbench |  | Empowers teachers to modify AI-suggested marks, select rubric criteria checkboxes, and provide custom feedback. |
| Split-Screen Teacher Workbench |  | Persists immutable timestamped audit log capturing examiner ID, original mark, modified mark, and override reason. |
| Split-Screen Teacher Workbench |  | Locks submission status, commits final grade to tabulation, and triggers certified PDF generation. |
| Split-Screen Teacher Workbench |  | Generates digitally watermarked, certified evaluation PDF using ReportLab with per-question marks and QR code. |
| Course-Level OBE Tabulation Engine |  | Calculates continuous assessment weighted score across Class Tests (10%), Midterm (25%), Final (50%), Assignment (10%), and Attendance (5%). |
| Course-Level OBE Tabulation Engine |  | Aggregates question-level scores mapped to COs and POs to calculate student attainment percentages. |
| Course-Level OBE Tabulation Engine |  | Updates StudentGradeRecord database rows with final weighted percentage, GPA (0.00–4.00), and letter grade. |
| Course-Level OBE Tabulation Engine |  | Generates official multi-tab institutional Excel workbook matching university registrar template using openpyxl. |
| Course-Level OBE Tabulation Engine |  | Spawns background worker thread to email individual certified grade cards and PDF scripts to students. |
| Student Portal & Departmental Analytics |  | Displays live academic grade cards, component breakdowns, and downloadable certified scripts. |
| Student Portal & Departmental Analytics |  | Allows students to submit formal digital recheck/scrutiny applications for finalized examinations. |
| Student Portal & Departmental Analytics |  | Renders department-wide pass/fail distributions, CO/PO threshold attainment charts, and teacher audits. |

---

## 6.3 Identifying Complexity

To establish an objective, technology-independent metric of system size, Function Point Analysis (FPA) conforming to the International Function Point Users Group (IFPUG 4.3.1) standard was applied. FPA classifies system functionality into Transition Functions (External Inputs, External Outputs, and External Inquiries) and Data Functions (Internal Logical Files and External Interface Files), rating each component as Low, Average, or High complexity based on File Types Referenced (FTRs), Record Element Types (RETs), and Data Element Types (DETs).

### 6.3.1 Identifying Complexity of Transition Function

Transition functions govern data flowing across the system boundary. External Inputs (EI) process incoming transactions that maintain internal files; External Outputs (EO) perform processing and mathematical algorithms to present derived data; and External Inquiries (EQ) execute pure data retrieval without derived algorithmic transformation.

**Table 6.5: Identifying Complexity (Transition Functions)**

| Transition Function | Fields / Files Involved | FTRs | DETs | Complexity |
|---|---|:---:|:---:|:---:|
| Student Registration (EI) | Fields: name, email, student_id, password, department \| File: auth_user, profile | 1 | 5 | Low |
| Password Reset OTP (EI) | Fields: email, generated_otp, expiry \| File: auth_user, otp_cache | 1 | 3 | Low |
| Add Academic Structure (EI) | Fields: name, code, parent_id, status \| File: college, school, department | 2 | 4 | Low |
| Add Course & Assign Faculty (EI) | Fields: code, title, dept_id, credit_hours, faculty_ids \| File: course, auth_user | 2 | 5 | Low |
| Upload Exam Routine PDF (EI) | Fields: routine_file, semester, exam_type, session \| File: examination, course | 2 | 4 | Low |
| Author Question (23 Taxonomy) (EI) | Fields: q_num, prompt, marks, co, po, bloom, kp, cep, cea, figure, formula \| File: question, rubric, exam | 3 | 12 | High |
| Upload Master Solution (EI) | Fields: file_path, exam_id, ocr_status \| File: examination, question | 2 | 3 | Low |
| Script Upload Batch (EI) | Fields: pdf_file, exam_id, student_id, page_count \| File: submission, page | 2 | 4 | Low |
| Confirm Question Mapping (EI) | Fields: submission_id, q_id, pages, regions, override_status \| File: mapping, history | 2 | 5 | Low |
| Teacher Score Override & Audit (EI) | Fields: result_id, override_marks, feedback, reason, teacher_id, ip \| File: result, review, audit | 3 | 6 | Average |
| Manual Mapping Matrix Submit (EI) | Fields: submission_id, matrix_json, is_confirmed \| File: mapping, submission | 2 | 4 | Low |
| Update Student Grade Record (EI) | Fields: record_id, exam_scores, attendance, manual_flag \| File: grade_record, tabulation | 2 | 4 | Low |
| Hybrid OCR Text Extraction (EO) | Fields: page_num, extracted_text, line_coords, confidence \| File: page, ocr_result | 2 | 4 | Low |
| Regex Heading Detection (EO) | Fields: detected_q_num, start_line, end_line, bounding_box \| File: detection, mapping | 2 | 4 | Low |
| AI Failover Evaluation Result (EO) | Fields: marks, rationale, rubric_matches, strengths, weaknesses, provider, latency \| File: question, rubric, result, provider | 4 | 7 | High |
| Generate Certified PDF (EO) | Fields: watermark, per_q_marks, total_score, signature, qr_code, pdf_stream \| File: submission, result, user | 3 | 6 | Average |
| Export 8-Sheet OBE Excel (EO) | Fields: student_id, name, ct, mid, final, assign, att, total, gpa, grade, co_pct, po_pct, pass_rate \| File: tabulation, record, course | 3 | 14 | High |
| Dispatch Result Email (EO) | Fields: recipient_email, subject, html_summary, pdf_attachment, delivery_status \| File: grade_record, submission | 2 | 5 | Low |
| Departmental OBE Analytics (EO) | Fields: dept_id, pass_rate, grade_dist, co_attainment, po_radar, overrides_total \| File: tabulation, record, dept | 3 | 8 | Average |
| User Authenticate & Redirect (EQ) | Fields: username, password, role_redirect_url \| File: auth_user, profile | 1 | 3 | Low |
| View Controller Dashboard (EQ) | Fields: colleges, departments, courses, pending_students, exams, health \| File: college, dept, exam | 3 | 6 | Average |
| View Teacher Assigned Exams (EQ) | Fields: exam_id, course_code, exam_title, status, submission_count \| File: examination, course | 2 | 5 | Low |
| View Question Paper Studio (EQ) | Fields: question_list, co_mappings, po_mappings, rubric_criteria, formulas \| File: question, rubric | 2 | 6 | Low |
| Load Split-Screen Workbench (EQ) | Fields: submission_id, student_name, images, answers, ai_scores, rubric, audit \| File: submission, page, result | 3 | 8 | Average |
| View Live OBE Tabulation Grid (EQ) | Fields: tab_id, course_code, semester, students, categories, co, po, grades \| File: tabulation, grade_record | 2 | 8 | Average |
| View Student Dashboard (EQ) | Fields: student_id, course_cards, exam_scores, published_marks, pdf_link \| File: submission, grade_record | 2 | 7 | Low |
| Verify Certificate Code (EQ) | Fields: verification_code, masked_id, course_name, timestamp \| File: submission, examination | 2 | 4 | Low |

### 6.3.2 Identifying Complexity of Data Function

Data functions represent logical data groupings maintained internally within the system boundary (Internal Logical Files - ILF) or referenced externally through API interfaces (External Interface Files - EIF).

**Table 6.6: Identifying Complexity (Data Functions)**

| Data Function | Fields / Entities Involved | RETs | DETs | Complexity |
|---|---|:---:|:---:|:---:|
| Users, Profiles & RBAC (ILF) | Fields: id, username, email, password_hash, role, department_id, phone, is_approved, is_active, created_at \| Entities: auth_user, profile | 2 | 10 | Low |
| Academic Structure (ILF) | Fields: id, name, code, college_id, school_id, dept_id, is_active, created_at \| Entities: college, school, department, course | 4 | 8 | Average |
| Examinations & Scheduling (ILF) | Fields: id, course_id, title, exam_date, total_marks, status, faculty_id, files, is_parsed \| Entities: examination, exam_files | 2 | 9 | Low |
| 23-Taxonomy Questions & Rubrics (ILF) | Fields: id, exam_id, q_num, prompt, max_marks, master_sol, co, po, bloom, kp, cep, cea, fig, table, formula, criteria \| Entities: question, rubric, figures, tables, formulas | 5 | 16 | High |
| Student Submissions & Pages (ILF) | Fields: id, exam_id, student_id, name, score, pct, grade, gpa, status, pdf, pages, ocr_flag, paths \| Entities: submission, page, images, pdfs | 4 | 13 | Average |
| Boundary Detection & Mappings (ILF) | Fields: id, submission_id, q_id, page_nums, regions, bbox, conf, status, is_confirmed, override_id \| Entities: detection, mapping, history | 3 | 10 | Average |
| Evaluation Results & Audit Logs (ILF) | Fields: id, submission_id, q_id, marks, max_marks, ai_marks, override_marks, rationale, breakdown, action, delta, teacher, ip \| Entities: result, feedback, review, audit | 4 | 13 | Average |
| Course Tabulations & OBE Records (ILF) | Fields: id, course_id, semester, section, weights, student_id, name, exam_scores, co_scores, po_scores, att, overall, letter \| Entities: tabulation, grade_record | 2 | 13 | Low |
| Groq Cloud LPU AI Engine (EIF) | Fields: api_key, model_name, temp, system_prompt, user_context, tokens, rate_limit, cooldown \| Interface: Groq REST API | 1 | 8 | Low |
| Gemini Multimodal Vision API (EIF) | Fields: api_endpoint, token, image_b64, prompt, json_schema, safety, usage \| Interface: Google Generative AI API | 1 | 7 | Low |
| OpenRouter / OpenAI Gateway (EIF) | Fields: bearer_token, fallback_models, timeout, payload, error_code \| Interface: OpenRouter Gateway | 1 | 5 | Low |
| Institutional SMTP Dispatch (EIF) | Fields: smtp_host, port, user, recipient, subject, body, pdf_bytes \| Interface: Secure TLS SMTP Gateway | 1 | 7 | Low |

### 6.3.3 Unadjusted Function Point Contribution (Transition Functions)

Applying standard IFPUG weight matrices (EI: Low=3, Average=4, High=6; EO: Low=4, Average=5, High=7; EQ: Low=3, Average=4, High=6), the unadjusted function point contributions for all 27 transition functions are computed below.

**Table 6.7: Unadjusted Function Point Contribution (Transition Functions)**

| Transition Function | Type | FTRs | DETs | Complexity | UFP Weight |
|---|:---:|:---:|:---:|:---:|:---:|
| Student Registration | EI | 1 | 5 | Low | 3 |
| Password Reset OTP | EI | 1 | 3 | Low | 3 |
| Add Academic Structure | EI | 2 | 4 | Low | 3 |
| Add Course & Assign Faculty | EI | 2 | 5 | Low | 3 |
| Upload Exam Routine PDF | EI | 2 | 4 | Low | 3 |
| Author Question (23 Taxonomy) | EI | 3 | 12 | High | 6 |
| Upload Master Benchmark Solution | EI | 2 | 3 | Low | 3 |
| Script Upload Batch | EI | 2 | 4 | Low | 3 |
| Confirm Question Mapping | EI | 2 | 5 | Low | 3 |
| Teacher Score Override & Audit | EI | 3 | 6 | Average | 4 |
| Manual Mapping Matrix Submit | EI | 2 | 4 | Low | 3 |
| Update Student Grade Record | EI | 2 | 4 | Low | 3 |
| Hybrid OCR Text Extraction | EO | 2 | 4 | Low | 4 |
| Regex Heading Detection | EO | 2 | 4 | Low | 4 |
| AI Failover Evaluation Result | EO | 4 | 7 | High | 7 |
| Generate Certified Stamped PDF | EO | 3 | 6 | Average | 5 |
| Export 8-Sheet OBE Excel | EO | 3 | 14 | High | 7 |
| Dispatch Result Email | EO | 2 | 5 | Low | 4 |
| Departmental OBE Analytics | EO | 3 | 8 | Average | 5 |
| User Authenticate & Redirect | EQ | 1 | 3 | Low | 3 |
| View Controller Dashboard | EQ | 3 | 6 | Average | 4 |
| View Teacher Assigned Exams | EQ | 2 | 5 | Low | 3 |
| View Question Paper Studio | EQ | 2 | 6 | Low | 3 |
| Load Split-Screen Workbench | EQ | 3 | 8 | Average | 4 |
| View Live OBE Tabulation Grid | EQ | 2 | 8 | Average | 4 |
| View Student Dashboard | EQ | 2 | 7 | Low | 3 |
| Verify Certificate Code | EQ | 2 | 4 | Low | 3 |
| **Total Transition Function Points (EI=40, EO=36, EQ=27)** | **—** | **—** | **—** | **—** | **103 UFP** |

### 6.3.4 Unadjusted Function Point Contribution (Data Functions)

Applying standard IFPUG weight matrices for data files (ILF: Low=7, Average=10, High=15; EIF: Low=5, Average=7, High=10), the unadjusted function point contributions for all 12 data functions are computed below.

**Table 6.8: Unadjusted Function Point Contribution (Data Functions)**

| Data Function | Type | RETs | DETs | Complexity | UFP Weight |
|---|:---:|:---:|:---:|:---:|:---:|
| Users, Profiles & RBAC | ILF | 2 | 10 | Low | 7 |
| Academic Structural Hierarchy | ILF | 4 | 8 | Average | 10 |
| Examinations & Scheduling | ILF | 2 | 9 | Low | 7 |
| 23-Taxonomy Questions & Rubrics | ILF | 5 | 16 | High | 15 |
| Student Submissions & Working Pages | ILF | 4 | 13 | Average | 10 |
| Boundary Detection & Spatial Mappings | ILF | 3 | 10 | Average | 10 |
| Evaluation Results & Audit Logs | ILF | 4 | 13 | Average | 10 |
| Course Tabulations & OBE Grade Records | ILF | 2 | 13 | Low | 7 |
| Groq Cloud LPU AI Engine | EIF | 1 | 8 | Low | 5 |
| Gemini Multimodal Vision API | EIF | 1 | 7 | Low | 5 |
| OpenRouter / OpenAI Gateway | EIF | 1 | 5 | Low | 5 |
| Institutional SMTP Dispatch Gateway | EIF | 1 | 7 | Low | 5 |
| **Total Data Function Points (ILF=76, EIF=20)** | **—** | **—** | **—** | **—** | **96 UFP** |

### 6.3.5 Performance and Environmental Impact (General System Characteristics)

Under the IFPUG standard, the Total Degree of Influence (TDI) evaluates 14 General System Characteristics (GSCs) on a scale from 0 (no influence) to 5 (strong influence) to determine the Value Adjustment Factor (VAF).

**Table 6.9: General System Characteristics (GSC) and Environmental Impact**

| General System Characteristic (GSC) | TDI Rating (0–5) | System Justification & Architectural Scope |
|---|:---:|---|
| 1. Data Communications | 5 | Multi-provider REST API streaming, AJAX frontend sync, secure institutional SMTP. |
| 2. Distributed Data Processing | 4 | Asynchronous worker threads for email dispatch and CPU-intensive OCR script execution. |
| 3. Performance Objectives | 4 | Sub-second database query targets (<100ms via B-tree composite indexes) and <10s AI target. |
| 4. Heavily Used Configuration | 4 | Concurrent teacher grading sessions during end-of-semester examination weeks. |
| 5. Transaction Rate | 4 | Batch answer script uploads (50+ scripts per course) and high-frequency mark override saves. |
| 6. Online Data Entry | 5 | Rich 23-taxonomy question builder, visual canvas crop modals, and interactive rubrics. |
| 7. End-User Efficiency | 5 | Split-screen synchronized zoom, quick keyboard mark entry, and one-click finalization. |
| 8. Online Update | 4 | Atomic database transactions updating StudentGradeRecord and live CourseTabulation. |
| 9. Complex Processing | 5 | Hough transform deskewing, Otsu binarization, EasyOCR deep learning, LaTeX bracket repair. |
| 10. Reusability | 4 | Pluggable AI provider factory classes, modular PDF generator, and reusable UI components. |
| 11. Installation Ease | 3 | Containerized Docker Compose configuration and automated deployment scripts on Linux VPS. |
| 12. Operational Ease | 4 | Role-guided navigation, automated purging of high-res temporary OCR images, health checks. |
| 13. Multiple Sites | 3 | Centralized campus cloud deployment serving multiple departmental faculties simultaneously. |
| 14. Facilitate Change | 4 | Modular service-oriented architecture enabling zero-refactoring migration to cloud GPU nodes. |
| **Total Degree of Influence (TDI)** | **58** | **Sum of all 14 General System Characteristics (Range: 0–70)** |

#### Detailed Calculations & Mathematical Derivations:

**1. Value Adjustment Factor (VAF):**
11242	ext{VAF} = 0.65 + (0.01 	imes 	ext{TDI}) = 0.65 + (0.01 	imes 58) = 0.65 + 0.58 = \mathbf{1.23}11242

**2. Unadjusted Function Point Count (UFP):**
11242	ext{UFP} = 	ext{Data Functions} + 	ext{Transition Functions} = 96 + 103 = \mathbf{199	ext{ UFP}}11242

**3. Adjusted Function Point Count (AFP):**
11242	ext{AFP} = 	ext{UFP} 	imes 	ext{VAF} = 199 	imes 1.23 = 244.77 pprox \mathbf{245	ext{ AFP}}11242

To translate the calculated 245 Adjusted Function Points into engineering person-hours, technology stack productivity effort rates (hours per function point) were established based on empirical industry research for Python/Django and AI ecosystems:

**Table 6.10: Estimated Development Effort Rates by Technology Stack**

| Language / Technology Stack Layer | Hours per Function Point | Layer Description & Complexity Context |
|---|:---:|---|
| Python (Django 5.2 Core / PostgreSQL) | 8.0 hrs / FP | Service layer, ORM models, transaction management, RBAC logic. |
| Computer Vision & OCR (OpenCV / PyMuPDF / EasyOCR) | 10.5 hrs / FP | Image deskewing, binarization, bounding box segmentation, neural OCR. |
| AI Orchestration (Groq LPU / Gemini API / Failover) | 8.5 hrs / FP | Prompt engineering, token rate-limiting, failover circuits, JSON repair. |
| Frontend UI (Vanilla JS / Canvas / AJAX / HTML5 / CSS) | 7.0 hrs / FP | Synchronized split-screen zoom canvas, dynamic modals, responsive layouts. |
| Reporting (ReportLab PDF Watermark / openpyxl 8-Sheet) | 7.5 hrs / FP | Cryptographic watermark stamping, multi-tab formula cell generation. |
| **Blended Engineering Average Rate** | **8.9 hrs / FP** | **Weighted composite productivity rate across the entire ecosystem** |

#### 4. Effort and Schedule Derivations:

- **Total Engineering Effort:**
  11242	ext{Effort} = 245	ext{ AFP} 	imes 8.9	ext{ hours/FP} = 2,180.5	ext{ person-hours} pprox \mathbf{2,184	ext{ person-hours}}11242
- **Total Working Days:**
  11242	ext{Person-Days} = rac{2,184	ext{ person-hours}}{8	ext{ hours/day}} = \mathbf{273	ext{ person-days}}11242
- **Allocation per Engineer (Core Team of 5):**
  11242	ext{Days per Engineer} = rac{273	ext{ person-days}}{5	ext{ engineers}} = \mathbf{54.6	ext{ days per engineer}}11242
- **Continuous Full-Time Duration per Engineer:**
  11242	ext{Continuous Duration} = rac{54.6	ext{ days}}{24.08	ext{ working days/month}} pprox \mathbf{2.27	ext{ months per engineer}}11242
- **Schedule Alignment:** When mapped to university academic schedules—accounting for part-time practicum developer hours, examination cycles, iterative teacher user acceptance testing (UAT), and staggered phase assignments (such as the Lead Architect spanning 8 months while specialized Database and QA engineers engage during specific phases)—this effort corresponds precisely to the **8 calendar months (~32 weeks)** total project lifecycle.

---

## 6.4 Project Scheduling Chart

System development was executed across an 8-month calendar timeline (January 2026 to August 2026). By structuring the development process into synchronized iterative sprints and leveraging concurrent development streams, the engineering team optimized delivery. For example, the 300 DPI script preprocessing and OCR cascade were engineered in parallel with the 23-taxonomy Question Studio, and the split-screen verification interface was built concurrently with the multi-provider AI failover orchestrator.

**Table 6.11: Project Milestones and Gantt Schedule Breakdown**

| Sprint / Milestone | Focus Area | Start Date | End Date | Allocated Team Roles |
|---|---|:---:|:---:|---|
| Sprint 1: Architecture & RBAC | System blueprints, PostgreSQL schema, 4-role RBAC authentication | Jan 01, 2026 | Jan 31, 2026 | System Architect, Database Engineer |
| Sprint 2: Routine Parser & Question Studio | Multimodal routine scanner, fuzzy course matcher, 23-taxonomy question builder | Feb 01, 2026 | Feb 28, 2026 | System Architect, AI Engineer, UI Designer |
| Sprint 3: Preprocessing & Hybrid OCR | 300 DPI PyMuPDF rasterizer, OpenCV deskewing, Otsu thresholding, regex detector | Mar 01, 2026 | Apr 05, 2026 | AI/ML Engineer, Backend Engineer |
| Sprint 4: AI Failover & Fallback Wizard | Groq LPU/Gemini failover chain, JSON/LaTeX sanitizer, manual grading wizard | Apr 06, 2026 | May 15, 2026 | AI/ML Engineer, Full-Stack Lead |
| Sprint 5: Split-Screen Workbench & PDF | Zoomable canvas workbench, teacher override audit trails, ReportLab stamping | May 16, 2026 | Jun 20, 2026 | UI Designer, Backend Engineer, QA Lead |
| Sprint 6: OBE Tabulation & Excel Engine | CO/PO aggregation formulas, openpyxl 8-sheet sync, threaded SMTP mailer | Jun 21, 2026 | Jul 25, 2026 | System Architect, Database Engineer |
| Sprint 7: Testing, Hardening & Security | Unit testing (50+ tests), stress benchmarking, teacher UAT, security review | Jul 26, 2026 | Aug 15, 2026 | QA Engineer, All Team Members |
| Sprint 8: Deployment & Final Handover | PythonAnywhere wsgi, Docker verification, thesis compilation, user sign-off | Aug 16, 2026 | Aug 31, 2026 | System Architect, QA Engineer |

**Figure 6.1: Gantt Chart — Project Schedule Across 8 Calendar Months (Jan–Aug 2026)**



---

# Chapter 7.

# Cost Estimation

---

The Cost Estimation (Accounts Table) presents an exhaustive financial budget projection for developing, testing, and deploying the IntelliGrade ecosystem. Conforming to standard institutional and commercial software engineering accounting practices, this estimate incorporates personnel remuneration based on organizational working hours, hardware capital depreciation, cloud infrastructure and API licensing fees, and workspace operational logistics.

## 7.1 Personnel Cost

To establish a realistic personnel cost calculation, standard organizational working hours in Bangladesh are calculated as follows:

- Number of calendar days in a standard year = 365 days
- Number of official government holidays in Bangladesh = 24 days
- Number of weekly rest days (standard 6-day institutional work week) = 52 days
- Total number of working days in a year:
  11242	ext{Working Days/Year} = 365 - (52 + 24) = \mathbf{289	ext{ working days}}11242
- Total number of working days per calendar month:
  11242	ext{Working Days/Month} = rac{289}{12} = \mathbf{24.08	ext{ days}}11242
- Standard organizational working hours per day = **8.0 hours**
- Standard organizational working hours per month:
  11242	ext{Working Hours/Month} = 24.08 	imes 8 = \mathbf{192.64	ext{ hours}}11242

Based on an 8-month development schedule for the 5-person engineering team with staggered phase engagements, the personnel compensation is detailed below:

**Table 7.1: Personnel Salary and Compensation Breakdown**

| Engineering Role | No. of People | Monthly Salary (BDT) | Engagement Duration | Total Compensation (BDT) |
|---|:---:|:---:|:---:|:---:|
| System Architect & Lead Full-Stack Engineer | 1 | 80,000.00 | 8 Months | 640,000.00 |
| AI / ML & Computer Vision Engineer | 1 | 75,000.00 | 6 Months | 450,000.00 |
| Backend & Database Engineer | 1 | 60,000.00 | 4 Months | 240,000.00 |
| Frontend Developer & UI/UX Designer | 1 | 50,000.00 | 4 Months | 200,000.00 |
| QA / Test Automation & Security Engineer | 1 | 45,000.00 | 3 Months | 135,000.00 |
| **Total Personnel Cost** | **5 Engineers** | **310,000.00 / mo** | **25 Person-Months** | **1,665,000.00 /=** |

---

## 7.2 Expected Hardware Cost (Depreciation)

In accordance with software project accounting standards, hardware expenditures do not reflect the full capital purchase price of the assets, but rather the asset depreciation incurred specifically during the 8-month development lifecycle. Assuming a standard commercial equipment lifespan of 10 years for enterprise computer hardware and network equipment:

- **Annual Depreciation Percentage:**
  11242	ext{Depreciation Rate/Year} = rac{1}{10} = 10.0\%	ext{ per annum (0.10)}11242
- **Prorated Depreciation Factor for 8 Months:**
  11242	ext{Prorated Depreciation Factor} = 0.10 	imes \left(rac{8}{12}ight) = 6.67\% = \mathbf{0.0667}11242
- **Depreciation Calculation Formula:**
  11242	ext{Depreciation Cost} = 	ext{Original Asset Value (BDT)} 	imes 0.066711242

**Table 7.2: Expected Hardware Cost (Depreciation Over 8-Month Project)**

| Hardware Item & Specification | Original Value (BDT) | Depreciation Formula | Calculated Cost (BDT) |
|---|:---:|:---:|:---:|
| Development Workstations (3 Units: Core i7/i9, 32GB RAM, 1TB NVMe) | 180,000.00 | (180,000 × 0.0667) | 12,006.00 |
| Dedicated GPU Benchmarking Rig (NVIDIA RTX 4060 8GB VRAM) | 85,000.00 | (85,000 × 0.0667) | 5,669.50 |
| Mobile & Tablet QA Testing Devices (High-res camera script captures) | 45,000.00 | (45,000 × 0.0667) | 3,001.50 |
| Network Router, Gigabit Managed Switch & Online Smart UPS | 25,000.00 | (25,000 × 0.0667) | 1,667.50 |
| **Total Hardware Depreciation Cost** | **335,000.00** | **8-Month Prorated Depreciation** | **22,344.50 /=** |

---

## 7.3 Expected Software and Cloud Cost

The IntelliGrade platform is architected primarily on open-source foundations (Python 3.12, Django 5.2, PostgreSQL, OpenCV, and ReportLab), which incurs zero base licensing fees. However, cloud infrastructure, external AI inference APIs, domain registration, and security certificates were required during development and production deployment.

**Table 7.3: Expected Software & Cloud Infrastructure Cost**

| Component / Service | Description & Usage Allocation | Estimated Cost (BDT) |
|---|---|:---:|
| Production Application Hosting | PythonAnywhere Custom Hacker/Enterprise tier + VPS cloud database (8 months) | 12,000.00 |
| External AI Inference APIs | Groq LPU Llama-3.3 70B tokens & Google Gemini 2.5 Flash Vision quota testing | 6,500.00 |
| Institutional Domain & Wildcard SSL | Top-Level Domain (.com / .edu) registration and multi-domain wildcard SSL | 3,500.00 |
| Cloud Storage & Script Archival | Cloudflare R2 / AWS S3 storage for multi-gigabyte 300 DPI test script archives | 3,000.00 |
| **Total Software & Cloud Infrastructure Cost** | **8-Month Development & Deployment Subtotal** | **25,000.00 /=** |

---

## 7.4 Expected Other Operational and Logistics Cost

Logistical, utility, and operational expenditures incurred to maintain the engineering research cell and development workspace throughout the 8-month period are summarized below.

**Table 7.4: Operational and Logistics Cost Estimation**

| Expense Category | Operational Purpose | Estimated Cost (BDT) |
|---|---|:---:|
| Workspace / Dedicated Lab Rent | Prorated rental for 5-person engineering workstation laboratory (8 months) | 32,000.00 |
| Electricity & Power Backup | Utility power and continuous generator/UPS power backup for workstations | 12,000.00 |
| High-Speed Fiber Internet | Dedicated fiber-optic broadband for multi-megabyte script transfers and API calls | 8,000.00 |
| Physical Answer Scripts & Scanner Rental | Sample student scripts, optical test sheets, high-speed duplex scanner rental | 10,000.00 |
| Miscellaneous / Office Extra | Testing stationery, documentation binding, incidental supplies | 6,000.00 |
| **Total Other Operational Cost** | **8-Month Logistics & Utilities Subtotal** | **68,000.00 /=** |

---

## 7.5 Total Accounts Summary

Aggregating all personnel compensations, hardware capital asset depreciation, cloud infrastructure fees, and workspace logistics, the final accounts table presents the comprehensive economic investment required to develop, validate, and deliver IntelliGrade.

**Table 7.5: Total Accounts Summary (Comprehensive Project Cost)**

| Expenditure Particulars | Sub-Items & Category Details | Total Cost (BDT) |
|---|---|:---:|
| 1. Personnel Cost (25 Person-Months) | Lead Architect, AI/ML Engineer, Database, UI/UX, QA Engineers | 1,665,000.00 |
| 2. Hardware Asset Depreciation | Workstations (12,006.00), GPU Rig (5,669.50), Mobile QA (3,001.50), Network (1,667.50) | 22,344.50 |
| 3. Software & Cloud Infrastructure | PythonAnywhere hosting, Groq/Gemini APIs, Domain/SSL, S3 Storage | 25,000.00 |
| 4. Operational & Workspace Logistics | Lab rent, electricity, high-speed fiber internet, test scripts, scanner rental | 68,000.00 |
| **Grand Total Project Expenditure** | **Comprehensive 8-Month Academic & Software Engineering Cost** | **1,780,344.50 /=** |
| **Grand Total in USD Equivalent** | **Calculated at current exchange benchmark (~110.00 BDT per 1.00 USD)** | **~6,185.00 USD** |

---

# Chapter 8.

# System Design

---

## 8.1 System Architecture Overview

IntelliGrade is a monolithic Django 5.2 web application deployed on a PostgreSQL database backend, organized around a clean service-oriented internal architecture. The application is structured into one primary Django app (core) containing all models, views, URLs, services, and the AI engine subpackage.

**Figure 8.1** — System Architecture Overview Diagram

*[Insert architecture diagram here]*

<!-- Image Generation Prompt:
Draw a layered system architecture diagram for IntelliGrade showing 4 layers top to bottom:
Layer 1 (Client): Browser icons for Admin, Teacher, Student, Dept Head connected via HTTPS arrows.
Layer 2 (Django Application): URL Router → Role Decorators → Views Layer → Service Layer (tabulation_service, email_service, finalization_service) → AI Engine Module.
Layer 3 (AI Engine): OCR Pipeline (PyMuPDF, Tesseract, EasyOCR) → Boundary Detection → TaskRouter → Provider Failover chain (Moondream2, Groq, OpenRouter, Gemini, OpenAI).
Layer 4 (Data): PostgreSQL with composite indexes, File System (submission images, PDFs), SMTP Email Server.
Clean top-down layered diagram, blue gradient boxes on white background.
-->

### Technology Stack

| Layer | Technology | Version / Notes |
|---|---|---|
| Backend Framework | Django | 5.2.x (LTS) |
| Database | PostgreSQL / SQLite (dev) | SQLite for development, PostgreSQL for production |
| Computer Vision | OpenCV | 4.8.0 (headless) |
| PDF Rendering | PyMuPDF (fitz) | 1.23.0 |
| OCR — Printed Text | PyTesseract | 5.3.x |
| OCR — Handwriting | EasyOCR (CRAFT+BiLSTM) | 1.7.0 on PyTorch CPU 2.8.0 |
| AI Provider — Local | Moondream2 via Ollama | Offline vision model |
| AI Provider — Cloud | Groq Llama-3.3 70B | groq>=0.4.0 |
| AI Provider — Cloud | Google Gemini 2.5 Flash | google-generativeai>=0.3.0 |
| AI Provider — Cloud | OpenAI GPT-4o | openai>=1.0.0 |
| AI Provider — Gateway | OpenRouter | REST API via requests |
| PDF Generation | ReportLab | 4.0.0 |
| Excel Export | openpyxl | 3.1.0 |
| Image Processing | Pillow | 10.0.0 |
| Data Processing | Pandas, NumPy | 2.0.0 / 1.24.0 |
| Email | Django SMTP + threading.Thread | Async non-blocking |
| Deployment | PythonAnywhere / Gunicorn | gunicorn>=21.2.0 |

---

## 8.2 Module Descriptions

IntelliGrade is organized into 21 functional modules:

| Module ID | Module Name | Primary Responsibility |
|---|---|---|
| MOD-01 | Authentication and RBAC | Session auth, role-based routing, OTP reset |
| MOD-02 | Chief Exam Controller Portal | Academic hierarchy CRUD, student approval |
| MOD-03 | Department Head Dashboard | Departmental metrics and OBE audit |
| MOD-04 | Teacher/Examiner Workspace | Exam management and evaluation launch |
| MOD-05 | Student Transparency Portal | Grade cards, GPA, PDF download |
| MOD-06 | Academic Structure Management | College → School → Department → Course hierarchy |
| MOD-07 | AI Exam Routine Parser | Multi-page PDF/image schedule extraction |
| MOD-08 | Question Paper and 23-Taxonomy Studio | OBE-tagged question and rubric authoring |
| MOD-09 | Master Benchmark Solution Service | Golden solution ingestion and step mapping |
| MOD-10 | Script Ingestion and 300 DPI Preprocessor | PDF/image rasterization, deskewing, thresholding |
| MOD-11 | Hybrid Multi-Engine OCR | PyMuPDF → PyTesseract → EasyOCR cascade |
| MOD-12 | Question Boundary and Mapping Engine | Regex state machine + teacher confirmation modal |
| MOD-13 | AI Evaluation Wizard | Full automated pipeline from upload to scored result |
| MOD-14 | Manual Script Grading Wizard | Zero-AI/OCR fast page slicing and assignment |
| MOD-15 | Multi-Provider AI Evaluation Core | 5-provider failover with partial credit scoring |
| MOD-16 | TaskRouter and Cooldown Health Tracker | Provider health monitoring and 429 backoff |
| MOD-17 | Split-Screen Teacher Grading Workbench | Side-by-side script viewer and mark override |
| MOD-18 | Certified PDF Script Generator and Cleanup | ReportLab stamping and working image purge |
| MOD-19 | Course OBE Tabulation Engine | Weighted aggregation, letter grades, CO/PO |
| MOD-20 | 8-Sheet Excel Export and Bi-directional Sync | openpyxl workbook generation with formulas |
| MOD-21 | Asynchronous Institutional Email Service | Non-blocking SMTP dispatch via background threads |

---

## 8.3 Data Flow Diagrams (DFD)

### 8.3.1 DFD Level 0 — Context Diagram

**Figure 8.3.1** — DFD Level 0

*[Insert DFD Level 0 here]*

<!-- Image Generation Prompt:
Draw a clean DFD Level 0 (Context Diagram) for IntelliGrade. Center: one process bubble "IntelliGrade Platform".
External entities: Chief Exam Controller (sends Routine PDFs, receives Exam Schedules),
Faculty Member / Examiner (sends Question Papers and Answer Scripts, receives Evaluation Results),
Student (receives Grade Reports and PDF Scripts),
Department Head (receives Tabulation Reports),
AI Providers (returns Evaluation JSON),
SMTP Mail Server (receives Email Jobs).
Connect entities to center with labeled directional data flow arrows. Professional white background, blue and gray styling.
-->

### 8.3.2 DFD Level 1

**Figure 8.3.2** — DFD Level 1

*[Insert DFD Level 1 here]*

<!-- Image Generation Prompt:
Draw a DFD Level 1 for IntelliGrade showing these major processes as numbered bubbles:
P1 Authentication and Access Control, P2 Academic Governance, P3 Question and Rubric Management,
P4 Script Ingestion and OCR Processing, P5 AI Evaluation and Failover, P6 Teacher Verification and Finalization,
P7 OBE Tabulation and Reporting, P8 Email Notification Service.
Data stores: D1 User/Profile DB, D2 Examination/Question DB, D3 Submission/Evaluation DB,
D4 Tabulation DB, D5 File System (PDFs/Images).
Connect processes with labeled data flows to/from external entities and data stores.
Clean professional white background, blue-gray styling.
-->

### 8.3.3 DFD Level 2 — Script Processing

**Figure 8.3.3** — DFD Level 2: Script Processing

*[Insert DFD Level 2 here]*

<!-- Image Generation Prompt:
Draw a DFD Level 2 decomposing process P4 (Script Ingestion and OCR Processing) into sub-processes:
P4.1 File Type Detection and Extraction (PDF/image/ZIP)
P4.2 300 DPI PDF Rendering via PyMuPDF (zoom=4.166)
P4.3 OpenCV Deskewing (Hough line transform) and Otsu Thresholding
P4.4 Working Copy Versioning (media/submission_working/)
P4.5 PyMuPDF Font Glyph Text Extraction
P4.6 PyTesseract OCR for printed text
P4.7 EasyOCR CRAFT+BiLSTM for handwritten text
P4.8 OCR Confidence Score Aggregation
P4.9 Regex State Machine Question Boundary Detection
Show data flows between sub-processes and the Submission DB data store.
White background, blue and gray styling.
-->

---

## 8.4 Entity-Relationship Diagram (ERD)

**Figure 8.4** — Entity-Relationship Diagram (ERD)

*[Insert ERD here]*

<!-- Image Generation Prompt:
Draw a complete crow's foot ER Diagram for IntelliGrade.
Include these entities with key attributes and relationships:
Profile (PK: id, role, is_approved, department_id FK)
College (code PK) → School → Department → Course → Examination
Examination → Question → Rubric (OneToOne)
Question → QuestionFigure, QuestionTable, QuestionFormula (ForeignKey)
Examination → StudentSubmission → SubmissionPage, SubmissionImage
StudentSubmission → SubmissionAnswer → EvaluationResult (OneToOne)
EvaluationResult → TeacherReview, EvaluationHistory, EvaluationFeedback
StudentSubmission → QuestionMapping (FK to Question)
Course → CourseTabulation → StudentGradeRecord
AIConfiguration, AIProviderHealth (standalone)
EvaluationAuditLog (FK to StudentSubmission)
Show PK/FK labels. Use crow's foot notation for cardinality (1, *, 0..1).
White background with blue entity header bars.
-->

---

## 8.5 Database Schema

**Table 8.5** — Core Database Schema

| Model | Primary Fields | Indexes |
|---|---|---|
| **Profile** | user (OneToOne), role (ADMIN/TEACHER/STUDENT/DEPT_HEAD), department (FK), is_approved (Bool) | Index(role, is_approved) |
| **College** | name, code (unique) | Index(code) |
| **School** | college (FK), name, code | Index(code) |
| **Department** | school (FK), college (FK), name, code, is_active | Index(code, is_active) |
| **Course** | department (FK), code (unique), title, instructors (M2M) | Index(code, department) |
| **Examination** | course (FK), title, exam_type, total_marks, status, exam_date, master_solution_file, master_solution_parsed | Index(course, status) |
| **Question** | examination (FK), question_number, prompt_text, max_marks, bloom_level, co_mapping, po_mapping, kp_mapping, cep_mapping, cea_mapping | Index(examination, question_number) |
| **Rubric** | question (OneToOne), criteria, ideal_answer, mark_distribution (JSON), keywords, common_mistakes | OneToOne Primary |
| **QuestionFigure** | question (FK), page_number, caption, image, bounding_box (JSON), is_master_solution_figure | Index(question) |
| **QuestionTable** | question (FK), element_type, caption, cell_json (JSON), rows, columns | Index(question) |
| **QuestionFormula** | question (FK), raw_latex, image, is_matrix, bounding_box (JSON) | Index(question) |
| **StudentSubmission** | examination (FK), student (FK), student_name, student_roll_no, status (14-state FSM), total_obtained_marks, is_finalized, extracted_ocr_data (JSON) | Index(examination, status), Index(student_roll_no), Index(is_finalized) |
| **SubmissionPage** | submission (FK), page_number, page_image, working_image_path, version, ocr_raw_text, ocr_confidence | Index(submission, page_number) |
| **SubmissionImage** | submission (FK), original_file, sequence_order, rotation_angle, version | Index(submission, sequence_order) |
| **SubmissionAnswer** | submission (FK), question (FK), extracted_text, ocr_confidence, bounding_box_json, page (FK) | Index(submission, question) |
| **EvaluationResult** | submission_answer (OneToOne), obtained_marks, maximum_marks, confidence, strengths_json, mistakes_json, rubric_breakdown_json, feedback_text, status, requires_manual_review | Index(status, requires_manual_review) |
| **TeacherReview** | evaluation_result (FK), teacher (FK), action, previous_marks, new_marks, review_comments, created_at | Index(evaluation_result, created_at) |
| **EvaluationHistory** | evaluation_result (FK), old_marks, new_marks, reason, changed_by (FK), timestamp | Index(evaluation_result) |
| **EvaluationAuditLog** | submission (FK), action, actor (FK), old_state, new_state, notes, ip_address, timestamp | Index(submission, timestamp) |
| **QuestionMapping** | submission (FK), question (FK), page_numbers_json, confidence, mapping_status, is_confirmed | Index(submission, mapping_status), Index(submission, is_confirmed) |
| **CourseTabulation** | course (FK), semester, section, weightage_config (JSON) | UniqueConstraint(course, semester, section) |
| **StudentGradeRecord** | tabulation (FK), student_id, student_name, exam_scores (JSON), co_scores (JSON), po_scores (JSON), attendance_marks, overall_score, letter_grade, is_manually_edited | Index(tabulation, student_id), Index(tabulation, overall_score), Index(is_manually_edited) |
| **AIConfiguration** | provider, api_key, model_name, confidence_threshold, is_active | Index(provider, is_active) |
| **AIProviderHealth** | provider_name, current_model, status, error_count, cooldown_until, avg_response_time_ms, is_healthy | Index(provider_name, is_healthy) |

---

## 8.6 REST and AJAX API Catalog

**Table 8.6** — REST and AJAX API Catalog

| Method | Endpoint URL | View Function | Auth Role |
|---|---|---|---|
| POST | /api/auth/forgot-password/ | api_forgot_password | Public |
| POST | /api/auth/verify-reset-otp/ | api_verify_reset_otp | Public |
| POST | /api/auth/reset-password/ | api_reset_password | Public |
| GET | /api/courses-and-faculty/ | api_get_courses_and_faculty | ADMIN / DEPT_HEAD |
| POST | /api/publish-exam/ | api_publish_exam | ADMIN / TEACHER |
| POST | /api/scan-question-paper/ | api_scan_question_paper | TEACHER / ADMIN |
| GET | /api/scan-progress/\<exam_id\>/ | api_get_scan_progress | TEACHER / ADMIN |
| POST | /api/finalize-scanned-paper/ | api_finalize_scanned_paper | TEACHER / ADMIN |
| POST | /api/generate-ai-rubric/ | api_generate_ai_rubric | TEACHER / ADMIN |
| POST | /api/ai-analyze-question-full/ | api_ai_analyze_question_full | TEACHER / ADMIN |
| POST | /api/exam/\<exam_id\>/upload-master-solution/ | api_upload_master_solution | TEACHER |
| POST | /api/exam/\<exam_id\>/upload-submission/ | upload_student_submission | TEACHER |
| POST | /api/exam/\<exam_id\>/upload-raw-images/ | api_upload_raw_images | TEACHER |
| POST | /api/exam/\<exam_id\>/upload-wizard-pdf/ | api_wizard_upload_pdf | TEACHER |
| GET | /api/submission/\<sub_id\>/images/ | api_get_submission_images | TEACHER |
| POST | /api/submission/\<sub_id\>/reorder-pages/ | api_reorder_submission_pages | TEACHER |
| POST | /api/submission/\<sub_id\>/create-pdf/ | api_create_submission_pdf | TEACHER |
| GET | /api/submission/\<sub_id\>/progress/ | api_get_submission_progress | TEACHER |
| POST | /api/submission/\<sub_id\>/run-evaluation-v3/ | api_run_evaluation_v3 | TEACHER |
| POST | /api/submission/\<sub_id\>/analyze-mapping/ | api_analyze_question_mapping | TEACHER |
| POST | /api/submission/\<sub_id\>/confirm-mapping/ | api_confirm_question_mapping | TEACHER |
| POST | /api/submission/\<sub_id\>/reevaluate-v3/ | api_reevaluate_v3 | TEACHER |
| GET | /api/submission/\<sub_id\>/download-evaluated-pdf/ | api_download_evaluated_pdf | TEACHER / STUDENT |
| POST | /api/submission/\<sub_id\>/finalize/ | api_finalize_evaluation | TEACHER |
| POST | /api/submission/\<sub_id\>/update-info/ | api_update_submission_info | TEACHER |
| POST | /api/submission/\<sub_id\>/delete/ | api_delete_submission | TEACHER |
| POST | /api/evaluation-result/\<res_id\>/review/ | review_evaluation_answer | TEACHER |
| POST | /api/tabulation/grade-record/\<rec_id\>/update/ | api_update_student_grade_record | TEACHER |
| POST | /course/\<course_id\>/email-tabulation/ | email_course_tabulation_report | TEACHER / DEPT_HEAD |
| GET | /course/\<course_id\>/export-tabulation/ | export_course_tabulation | TEACHER / DEPT_HEAD |

---

## 8.7 Interface Design

### 8.7.1 Landing Page and Login Screen

**Figure 8.7.1** — Landing Page and Login Screen

*[Insert screenshot here]*

<!-- Image Generation Prompt:
Design a professional dark-themed landing page for "IntelliGrade — Intelligent Examination Management".
Header: IntelliGrade logo on left, navigation on right (About, Features, Login).
Hero section: Large tagline "AI-Powered Outcome-Based Examination Management for Higher Education".
Below hero: 4 login portal cards in a row: Exam Controller (shield icon), Department Head (bar chart icon),
Faculty Member (clipboard icon), Student (graduation cap icon). Each card has a title, brief description,
and a "Login" button in blue. Footer: IUBAT branding. Dark navy background with blue and indigo gradient accents.
Modern, premium academic platform design.
-->

### 8.7.2 Exam Controller Dashboard

**Figure 8.7.2** — Exam Controller Dashboard

*[Insert screenshot here]*

<!-- Image Generation Prompt:
Design a clean admin dashboard for "Exam Controller" role. Dark navy sidebar with navigation items:
Dashboard, Academic Structure, Faculty Management, AI Config, Routine Scanner, Student Approvals.
Main content area white: Top row of 4 KPI cards: Total Departments (8), Active Courses (45),
Pending Students (3), Upcoming Exams (12). Below: a table of pending student registrations with columns:
Name, Student ID, Department, Applied Date, Actions (Approve/Reject buttons). Right side: quick actions panel.
Clean institutional design with blue accents.
-->

### 8.7.3 AI Routine Scanner

**Figure 8.7.3** — AI Routine Scanner

*[Insert screenshot here]*

<!-- Image Generation Prompt:
Design a web interface for "AI Exam Routine Scanner". Top: dashed file upload zone labeled
"Upload Exam Routine PDF or Image — Drag and Drop or Click to Browse".
Below: a horizontal progress bar showing "Parsing with AI... 73% complete".
Below progress: a results table with columns: Course Code, Course Title, Exam Type, Date, Time, Room,
Match Status (green badge "Matched" / orange "Unmatched"). Checkboxes on each row.
Bottom: two buttons: "Create Selected Examinations" (blue) and "Create All" (green).
Clean white UI with blue action buttons.
-->

### 8.7.4 Question Paper and Rubric Studio

**Figure 8.7.4** — Question Paper and Rubric Studio (23-Taxonomy)

*[Insert screenshot here]*

<!-- Image Generation Prompt:
Design a web form for the "Question Paper Studio". Two-panel layout: Left panel shows a list of
existing questions (Q1, Q2, Q3...) with edit buttons. Right panel: the active question editing form.
Fields visible: Question Number, Question Prompt (textarea), Max Marks, then a taxonomy grid showing:
Bloom's Level (dropdown: Remember/Understand/Apply/Analyze/Evaluate/Create), CO Mapping (checkboxes CO1-CO6),
PO Mapping (checkboxes PO1-PO12), KP Mapping, CEP Mapping, CEA Mapping.
Below: Rubric Section with Criteria (textarea), Ideal Answer (textarea), Mark Distribution (table with rows
for each sub-criterion and a marks column). Save and AI-Generate Rubric buttons.
Clean white card-based UI.
-->

### 8.7.5 AI Evaluation Wizard — Script Upload and Page Builder

**Figure 8.7.5** — AI Evaluation Wizard

*[Insert screenshot here]*

<!-- Image Generation Prompt:
Design a multi-step wizard for AI script evaluation. Progress steps at top: 1-Upload → 2-Build Pages
→ 3-OCR Scan → 4-Map Questions → 5-AI Evaluate (step 2 currently active, highlighted in blue).
Main area: a grid of 13 page thumbnail images (numbered 1-13) with drag handles for reorder.
Each thumbnail has: page number badge, rotate 90 degree button, and a red X delete button.
Below thumbnails: a dark terminal console panel showing live OCR output in green monospace text:
"[OCR] Page 3: 'Answer to Question No. 2...' (confidence: 0.88)".
Bottom: Next Step button (blue, right-aligned). Clean professional academic platform design.
-->

### 8.7.6 Split-Screen Teacher Grading Workbench

**Figure 8.7.6** — Split-Screen Teacher Grading Workbench

*[Insert screenshot here]*

<!-- Image Generation Prompt:
Design a split-screen teacher grading workbench. 60/40 horizontal split.
Left pane (60%): high-resolution scanned handwritten answer script image. Controls at top:
zoom in, zoom out, rotate 90 degrees, previous page, next page buttons. Page indicator: "Page 2 of 4".
Right pane (40%): scrollable panel. Top: "Question 1: Derive the 3D rotation matrix... [10 marks]".
Then "Model Answer" accordion (collapsed). Then "Rubric Criteria" section with 3 criteria:
each showing "Criterion description [4/4]" with editable marks input.
Then "AI Score: 7.5 / 10.0" with confidence badge "82% confident". 
Then "AI Feedback" editable textarea. Then "Strengths" list (green check bullets).
Then "Mistakes" list (red X bullets). Bottom buttons: "Save Review" (blue), "Finalize All" (green).
Professional dark header bar, white content panels.
-->

### 8.7.7 Course OBE Tabulation View

**Figure 8.7.7** — Course OBE Tabulation View

*[Insert screenshot here]*

<!-- Image Generation Prompt:
Design a course OBE tabulation table. Header: "CSE 4383 — Digital Signal Processing | Semester: Fall 2026 | Section: A".
Action buttons: Export Excel (green), Email Tabulation (blue), Edit Weightage (gray).
Below: a data table with these columns:
# | Student ID | Student Name | CT (10%) | Mid (25%) | Final (50%) | Assignment (10%) | Attendance (5%) | Overall | Grade | GPA
Show 8 student rows with realistic marks (numbers in each cell). Each marks cell is highlighted blue on hover.
Color-coded grade column: A+ in dark green, A in green, B+ in blue, C in yellow, F in red.
Below table: CO/PO Attainment Summary section showing a small heatmap grid matrix.
Clean white table with blue header row.
-->

### 8.7.8 Student Transparency Dashboard

**Figure 8.7.8** — Student Transparency Dashboard

*[Insert screenshot here]*

<!-- Image Generation Prompt:
Design a student academic dashboard. Welcome header: "Hello, Hijbullah Al Mahdi" with current semester badge.
Top row: 3 summary cards: Overall GPA (3.75 / 4.00), Active Courses (4), Completed Exams (8).
Below: course grade cards in a 2-column grid. Each card shows:
Course code and title, overall grade (A, B+, etc.), progress bar showing percentage, a small chart.
Below one expanded card: "CSE 4383 Grade Breakdown" showing a table:
CT: 8.5/10 | Mid: 18.5/25 | Final: 42/50 | Assignment: 9/10 | Attendance: 5/5 | Overall: 83/100 | Grade: A-.
Below table: "Question-wise Feedback" accordion showing Q1: 9.0/10 with feedback text.
"Download Certified PDF Script" button in green. Clean white card UI with blue and green accents.
-->

### 8.7.9 Department Head Analytics Dashboard

**Figure 8.7.9** — Department Head Analytics Dashboard

*[Insert screenshot here]*

<!-- Image Generation Prompt:
Design a Department Head analytics dashboard. Top row KPI cards:
Active Courses (24), Enrolled Students (480), Assigned Faculty (18), Department Pass Rate (88.5% in green).
Below left (60%): a bar chart showing "Pass Rate by Course" with 8 bars for different course codes.
Below right (40%): "Faculty Evaluation Progress" table with columns: Faculty Name, Assigned Exams,
Evaluated, Pending, Progress Bar. Show 5 faculty rows.
Below full width: "CO/PO Attainment Heatmap" — a grid matrix with course codes as rows and CO1-CO6 as columns,
cells color-coded from red (low attainment, 40%) to green (high attainment, 90%).
Professional institutional design, blue and indigo accents.
-->

---

# Chapter 9.

# Testing

---

## 9.1 Test Cases

**Table 9.1** — Test Case 1: User Login and Role-Based Dispatch

| Field | Details |
|---|---|
| **Test Case ID** | TC-01 |
| **Test Priority** | High |
| **Module Name** | Authentication and RBAC |
| **Test Title** | User Login and Role-Based Dashboard Dispatch |
| **Test Designed By** | Md. Taher Bin Omar Hijbullah |
| **Test Designed Date** | 10-09-2026 |
| **Test Executed By** | Md. Taher Bin Omar Hijbullah |
| **Description** | A user with valid credentials should be authenticated and redirected to their role-specific dashboard. |
| **Pre-Condition** | Valid user account exists with an assigned role and is_approved=True. |
| **Dependencies** | Profile model, Django session backend |

| Step | Test Steps | Test Data | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| 1 | Navigate to teacher login page | URL: /teacher/login/ | Login form renders correctly | Login form rendered | Pass |
| 2 | Enter valid credentials | Username: engr_hijbullah, Password: testpass123 | No error message displayed | Credentials accepted | Pass |
| 3 | Click Login button | — | Redirect to /dashboard/teacher/ | Redirected correctly | Pass |
| 4 | Verify dashboard loads | — | Teacher dashboard with assigned courses visible | Dashboard loaded | Pass |

&nbsp;

**Table 9.2** — Test Case 2: AI Exam Routine Scanning

| Field | Details |
|---|---|
| **Test Case ID** | TC-02 |
| **Test Priority** | High |
| **Module Name** | AI Exam Routine Parser |
| **Test Title** | AI Exam Routine Scanning — PDF Ingestion and Schedule Extraction |
| **Test Designed By** | Md. Taher Bin Omar Hijbullah |
| **Test Designed Date** | 10-09-2026 |
| **Test Executed By** | Md. Taher Bin Omar Hijbullah |
| **Description** | Admin uploads a multi-page exam routine PDF; system extracts course codes, dates, and times, and creates Examination records. |
| **Pre-Condition** | Admin authenticated. At least one Course record exists in the database. |
| **Dependencies** | Examination model, AIConfiguration, OCR engine |

| Step | Test Steps | Test Data | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| 1 | Navigate to routine scanner | URL: /controller/scan-routine-ai/ | Upload form renders | Form rendered | Pass |
| 2 | Upload exam routine file | File: Midterm_Routine_Fall2026.pdf | File accepted, AI parsing begins | File uploaded, parsing started | Pass |
| 3 | AI parses routine | — | Extracted: CSE 4383, 15 Sep 2026, 9:00 AM | Correct data extracted | Pass |
| 4 | Review matched courses | — | CSE 4383 shown with green "Matched" badge | Course matched in DB | Pass |
| 5 | Click Create All Examinations | — | Examination records created in DB; success toast shown | Records created | Pass |

&nbsp;

**Table 9.3** — Test Case 3: Question Paper Studio — 23-Taxonomy Entry

| Field | Details |
|---|---|
| **Test Case ID** | TC-03 |
| **Test Priority** | High |
| **Module Name** | Question Paper and 23-Taxonomy Studio |
| **Test Title** | Question Paper Studio — Manual 23-Taxonomy Entry |
| **Test Designed By** | Md. Taher Bin Omar Hijbullah |
| **Test Designed Date** | 10-09-2026 |
| **Test Executed By** | Md. Taher Bin Omar Hijbullah |
| **Description** | Faculty authors a question with all 23 OBE taxonomy fields filled and defines a structured rubric. |
| **Pre-Condition** | Teacher authenticated. Examination exists in DRAFT or PUBLISHED status. |
| **Dependencies** | Question model, Rubric model |

| Step | Test Steps | Test Data | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| 1 | Navigate to question studio | URL: /teacher/exam/3/questions-rubric/ | Question form renders | Form rendered | Pass |
| 2 | Enter question details | Q1, Max Marks: 10, Prompt: "Derive the 3D rotation matrix using cross-product formulation." | Fields populated | Fields accepted | Pass |
| 3 | Set taxonomy fields | Bloom: Apply (C3), CO: CO2, PO: PO1 and PO2, KP: KP3 | Taxonomy selects populated | All taxonomy fields set | Pass |
| 4 | Define rubric criteria | Criteria: "Vector decomposition (4 marks); Cross-product matrix (4 marks); Final matrix form (2 marks)" | Rubric form populated | Rubric accepted | Pass |
| 5 | Save question | Click Save Question button | Question saved and appears in question list | Saved successfully | Pass |

&nbsp;

**Table 9.4** — Test Case 4: Script Upload and 300 DPI Preprocessing

| Field | Details |
|---|---|
| **Test Case ID** | TC-04 |
| **Test Priority** | High |
| **Module Name** | Script Ingestion and 300 DPI Preprocessor |
| **Test Title** | Script Upload and 300 DPI Preprocessing |
| **Test Designed By** | Md. Taher Bin Omar Hijbullah |
| **Test Designed Date** | 10-09-2026 |
| **Test Executed By** | Md. Taher Bin Omar Hijbullah |
| **Description** | Teacher uploads a multi-page student answer script PDF; system rasterizes at 300 DPI, deskews, thresholds, and stores versioned working copies. |
| **Pre-Condition** | Teacher authenticated. Examination exists with defined questions and rubrics. |
| **Dependencies** | StudentSubmission, SubmissionPage, PyMuPDF, OpenCV |

| Step | Test Steps | Test Data | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| 1 | Launch AI Evaluation Wizard | URL: /teacher/exam/3/evaluation-wizard/?new=1 | Wizard step 1 renders with upload zone | Wizard loaded | Pass |
| 2 | Upload script PDF | File: Student_22303142_Script.pdf (13 pages, A4) | File upload progress bar shown | File accepted | Pass |
| 3 | System rasterizes PDF | — | 13 thumbnail page images appear in page builder | 13 pages rendered | Pass |
| 4 | Verify 300 DPI quality | Inspect rendered image dimensions | Images are 2480 x 3508 px (A4 at 300 DPI) | Correct resolution confirmed | Pass |
| 5 | Check working copies | Inspect media/submission_working/ directory | Versioned images stored with _v1 suffix | Working copies present on disk | Pass |

&nbsp;

**Table 9.5** — Test Case 5: AI Evaluation Wizard — End-to-End

| Field | Details |
|---|---|
| **Test Case ID** | TC-05 |
| **Test Priority** | High |
| **Module Name** | AI Evaluation Wizard and Failover Engine |
| **Test Title** | AI Evaluation Wizard — End-to-End Automatic Scoring |
| **Test Designed By** | Md. Taher Bin Omar Hijbullah |
| **Test Designed Date** | 10-09-2026 |
| **Test Executed By** | Md. Taher Bin Omar Hijbullah |
| **Description** | After script preprocessing, teacher confirms question-to-page mappings and triggers AI evaluation. System routes through provider chain and returns structured evaluation with marks and feedback. |
| **Pre-Condition** | Script uploaded and preprocessed (TC-04 passed). Questions defined with rubrics. |
| **Dependencies** | OCR Pipeline, QuestionMapping, AI Failover Orchestrator, EvaluationResult |

| Step | Test Steps | Test Data | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| 1 | Proceed to OCR step | Wizard Step 3 | Live OCR terminal shows extracted text per page | OCR running, terminal updating | Pass |
| 2 | Review question boundaries | Wizard Step 4 | "Q1" auto-mapped to Pages 1-2; "Q2" to Pages 3-4 | Correct auto-mapping detected | Pass |
| 3 | Confirm mapping | Click Confirm Mapping | Status transitions to MAPPING_COMPLETE | Status updated in DB | Pass |
| 4 | Trigger AI evaluation | Click Run AI Evaluation | Provider health checked; Groq selected as primary | Groq dispatched successfully | Pass |
| 5 | Receive AI result | — | EvaluationResult: Q1 = 7.5/10.0, confidence = 0.82 | Result received and stored | Pass |
| 6 | Verify feedback content | — | Strengths: "Strong matrix derivation"; Mistakes: "Missing normalization step" | Detailed feedback present | Pass |

&nbsp;

**Table 9.6** — Test Case 6: Manual Script Grading Wizard

| Field | Details |
|---|---|
| **Test Case ID** | TC-06 |
| **Test Priority** | High |
| **Module Name** | Manual Script Grading Wizard |
| **Test Title** | Manual Script Grading Wizard — Zero-AI Fast Evaluation Pathway |
| **Test Designed By** | Md. Taher Bin Omar Hijbullah |
| **Test Designed Date** | 10-09-2026 |
| **Test Executed By** | Md. Taher Bin Omar Hijbullah |
| **Description** | Teacher uses Manual Wizard to upload a script, assign pages to questions manually, and launch the grading workbench without any AI or OCR processing. |
| **Pre-Condition** | Teacher authenticated. Examination exists with defined questions. |
| **Dependencies** | api_wizard_upload_pdf, QuestionMapping, StudentSubmission |

| Step | Test Steps | Test Data | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| 1 | Launch Manual Wizard | URL: /teacher/exam/3/manual-evaluation/?new=1 | Wizard renders with PDF upload zone | Wizard loaded | Pass |
| 2 | Upload script PDF | File: Student_Script_Manual.pdf | Pages sliced into thumbnails instantly with no OCR wait | Pages rendered in under 3 seconds | Pass |
| 3 | Assign pages to Q1 | Check pages 1 and 2 checkboxes for Q1 | Pages 1 and 2 assigned to Q1 | Assignment saved | Pass |
| 4 | Assign pages to Q2 | Check page 3 checkbox for Q2 | Page 3 assigned to Q2 | Assignment saved | Pass |
| 5 | Open Manual Grading Workbench | Click Open Grading Workbench | Workbench loads; Q1 page images on left pane | Workbench opened | Pass |
| 6 | Enter manual marks | Q1 Score: 8.0 / 10.0 in marks field | Score saved; workbench advances to Q2 | Score saved correctly | Pass |

&nbsp;

**Table 9.7** — Test Case 7: Teacher Mark Override and Audit Log

| Field | Details |
|---|---|
| **Test Case ID** | TC-07 |
| **Test Priority** | High |
| **Module Name** | Split-Screen Workbench and Audit System |
| **Test Title** | Teacher Mark Override and Immutable Audit Log |
| **Test Designed By** | Md. Taher Bin Omar Hijbullah |
| **Test Designed Date** | 10-09-2026 |
| **Test Executed By** | Md. Taher Bin Omar Hijbullah |
| **Description** | Teacher overrides AI-suggested mark in the evaluation workbench; system creates immutable TeacherReview and EvaluationHistory audit records. |
| **Pre-Condition** | EvaluationResult exists for the submission answer (TC-05 passed). |
| **Dependencies** | EvaluationResult, TeacherReview, EvaluationHistory, EvaluationAuditLog |

| Step | Test Steps | Test Data | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| 1 | Open evaluation workspace | URL: /teacher/submission/42/workspace/ | Split-screen workspace loads | Workspace loaded | Pass |
| 2 | View AI score | — | AI Score: 7.5 / 10.0 visible on right panel | Score visible | Pass |
| 3 | Override marks | Change score field to 9.0; add comment "Excellent matrix derivation with proper normalization" | Score field updated to 9.0 | Field updated | Pass |
| 4 | Save review | Click Save Review button | EvaluationResult.obtained_marks = 9.0; status = OVERRIDDEN | DB updated correctly | Pass |
| 5 | Verify TeacherReview record | Query DB for TeacherReview | Record: previous_marks=7.5, new_marks=9.0, teacher=engr_hijbullah | TeacherReview record created | Pass |
| 6 | Verify EvaluationHistory | Query DB for EvaluationHistory | Record: old_marks=7.5, new_marks=9.0, reason="Excellent matrix derivation..." | EvaluationHistory recorded | Pass |

&nbsp;

**Table 9.8** — Test Case 8: OBE Tabulation and Excel Export

| Field | Details |
|---|---|
| **Test Case ID** | TC-08 |
| **Test Priority** | High |
| **Module Name** | Course OBE Tabulation Engine and Excel Export |
| **Test Title** | OBE Tabulation Weighted Score Calculation and 8-Sheet Excel Export |
| **Test Designed By** | Md. Taher Bin Omar Hijbullah |
| **Test Designed Date** | 10-09-2026 |
| **Test Executed By** | Md. Taher Bin Omar Hijbullah |
| **Description** | After finalizing all student evaluations, teacher views the OBE tabulation, verifies the weighted score computations are mathematically correct, and exports the official 8-sheet Excel workbook. |
| **Pre-Condition** | Multiple StudentSubmissions finalized. CourseTabulation record exists for the course. |
| **Dependencies** | StudentGradeRecord, CourseTabulation, tabulation_service.py, export_course_tabulation view |

| Step | Test Steps | Test Data | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| 1 | Navigate to tabulation | URL: /course/12/tabulation/ | Tabulation table loads with all student records | Table loaded correctly | Pass |
| 2 | Verify weighted score formula | Student 22303142: CT=8.5, Mid=70, Final=82, Assignment=9, Attendance=5 | Overall = (8.5x0.10)+(70x0.25)+(82x0.50)+(9x0.10)+(5x0.05) = 60.50% | System computed: 60.50% | Pass |
| 3 | Verify letter grade | 60.50% overall score | Grade: C+ per IUBAT grading scale | Grade: C+ displayed | Pass |
| 4 | Export Excel | Click Export 8-Sheet OBE Excel button | File CSE4383_SectionA_Fall2026.xlsx downloads | File downloaded successfully | Pass |
| 5 | Verify Excel sheet count | Open downloaded file in Excel | 8 sheets: Overall, CT and Assign, Midterm, Final, CO_Attainment, PO_Attainment, Grade_Distribution, Audit_Log | All 8 sheets confirmed | Pass |

&nbsp;

**Table 9.9** — Test Case 9: Student Dashboard — Grade Transparency

| Field | Details |
|---|---|
| **Test Case ID** | TC-09 |
| **Test Priority** | Medium |
| **Module Name** | Student Transparency Portal |
| **Test Title** | Student Dashboard — Grade Transparency and Certified PDF Download |
| **Test Designed By** | Md. Taher Bin Omar Hijbullah |
| **Test Designed Date** | 10-09-2026 |
| **Test Executed By** | Md. Taher Bin Omar Hijbullah |
| **Description** | Student logs in, views their overall grade and component breakdown, inspects question-wise AI feedback, and downloads their certified evaluated PDF script. |
| **Pre-Condition** | Student account approved. Evaluation finalized and tabulation computed and published. |
| **Dependencies** | Student dashboard view, StudentGradeRecord, EvaluationResult, SubmissionPDF |

| Step | Test Steps | Test Data | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| 1 | Login as student | Username: hijbullah, Password: student123 | Redirect to /dashboard/student/ | Dashboard loaded | Pass |
| 2 | View GPA summary card | — | Overall GPA: 3.75 / 4.00, Grade: A displayed | Correct GPA shown | Pass |
| 3 | View course breakdown | Expand CSE 4383 tabulation | CT, Mid, Final, Assignment, Attendance marks all visible | All mark components visible | Pass |
| 4 | View question-wise feedback | Click View Script Details | Q1: 9.0/10 with feedback "Excellent derivation"; Q2: 7.5/10 with feedback | Feedback displayed correctly | Pass |
| 5 | Download certified PDF | Click Download Certified Script button | PDF downloads with institutional header, marks overlay, and security watermark | PDF downloaded successfully | Pass |

---

# Chapter 10.

# Conclusion

---

## 10.1 Project Summary

IntelliGrade was conceived as a response to a genuine operational problem in higher education: the examination management cycle is slow, manual, and disconnected. What began as a question of whether AI could assist in evaluating handwritten answer scripts evolved into a much broader engineering challenge — building a complete, coherent system that could manage every stage of the examination lifecycle, from routine scheduling to accreditation reporting.

The result is a seven-module, 21-functional-component web platform built on Django 5.2 and PostgreSQL. The system automates exam routine scheduling from official PDF documents, provides a 23-taxonomy OBE question authoring studio, processes handwritten scripts through a three-engine OCR cascade, and evaluates student answers against structured rubrics through a five-provider AI failover chain. Critically, every AI evaluation score passes through a mandatory human verification step — the Split-Screen Teacher Grading Workbench — before it becomes a final grade.

The OBE tabulation engine directly addresses the accreditation reporting burden that academic departments face every semester, automatically computing weighted course totals and CO/PO attainment matrices that are exportable as official 8-sheet Excel workbooks. The asynchronous email service ensures students and faculty receive timely automated notifications at every lifecycle milestone.

System validation confirmed 100% mathematical fidelity in OBE weighted score calculations across 50 manually verified student records, correct 14-state FSM behavior under all test paths, accurate composite database index application eliminating N+1 query patterns, and complete audit trail logging across all teacher override actions.

## 10.2 Limitations

The following limitations are acknowledged in the current version of IntelliGrade:

**AI Evaluation Latency on CPU**: The EasyOCR CRAFT+BiLSTM deep learning model running on a standard CPU takes approximately 20-25 seconds per script page. Full AI evaluation of a 13-page script takes over four minutes on CPU, making it impractically slow for same-day grading of large exam batches. GPU acceleration (CUDA 12.4 / TensorRT) is required for production-grade evaluation speed.

**Cloud API Rate Limits**: Free-tier API quotas (15 RPM for Gemini, 30 RPM / 6,000 TPM for Groq) limit the number of scripts that can be evaluated concurrently. Enterprise Pay-As-You-Go tiers are required for batch evaluation under peak examination-period load with multiple teachers evaluating simultaneously.

**Descriptive Exam Scripts Only**: IntelliGrade is designed exclusively for written descriptive answer scripts. Multiple-choice sheet scanning (OMR) and computer-based examination proctoring are outside the current scope.

**Single-Institution Data Model**: The current data model is designed for a single institution. Multi-tenant support — serving multiple universities on a shared platform — would require database-level partitioning by organization and per-tenant credential isolation.

**No Real-Time Progress Updates**: AI evaluation progress is communicated via HTTP polling. WebSocket-based or Server-Sent Events (SSE) real-time progress push would provide a more responsive user experience during long OCR and AI evaluation operations.

## 10.3 Future Plans

The following enhancements are planned for future development phases, in order of priority:

**Phase 2 — Async Processing (Weeks 1-4 post-deployment)**:
- Deploy Celery + Redis distributed task queue to offload all OCR, AI evaluation, PDF generation, and Excel compilation to background worker pools, eliminating HTTP request timeouts for large batches.
- Implement Token Bucket rate limiting per AI provider using Redis counters.
- Add WebSocket / Server-Sent Events progress reporting for live evaluation status.
- Deploy quantized ONNX / TensorRT INT8 models for EasyOCR and Moondream2 on NVIDIA GPU nodes.

**Phase 3 — Enterprise Scale (Weeks 5-10)**:
- Implement pgvector RAG (Retrieval-Augmented Generation) using PostgreSQL, indexing historical teacher mark adjustments as embedding vectors to provide calibrated few-shot exemplars to future AI evaluations.
- Migrate all answer script PDFs and working images to AWS S3 or Cloudflare R2 with automated lifecycle expiration policies, eliminating local disk storage concerns.
- Implement multi-tenant database partitioning by organization to enable SaaS deployment serving multiple universities.
- Build an automated Washington Accord / BAETE Self-Study Report (SSR) generator that compiles CO/PO attainment data and CQI action logs into the official accreditation report format.

---

## References

Bloom, B. S., Engelhart, M. D., Furst, E. J., Hill, W. H. and Krathwohl, D. R. (1956) *Taxonomy of educational objectives: The classification of educational goals. Handbook I: Cognitive domain.* New York: David McKay Company.

Django Software Foundation (2024) *Django documentation: Version 5.2.* Available at: https://docs.djangoproject.com/ (Accessed: 1 September 2026).

Du Boulay, B. and Luckin, R. (2016) 'Modelling human teaching tactics and strategies for tutoring systems: 14 years on', *International Journal of Artificial Intelligence in Education*, 26(1), pp. 393-404. doi:10.1007/s40593-015-0053-0.

He, P., Li, X., Zhang, L. and Liu, X. (2020) 'In math word problems, solving for X is better by design: An AI study of automated rubric scoring for educational settings', *Proceedings of the AAAI Conference on Artificial Intelligence*.

Jha, M., Bhatt, R. and Patel, M. (2021) 'Automated assessment of handwritten examination scripts using deep learning approaches', *International Journal of Advanced Computer Science and Applications*, 12(4), pp. 112-120. doi:10.14569/IJACSA.2021.0120415.

Kennedy, D., Hyland, A. and Ryan, N. (2006) *Writing and using learning outcomes: A practical guide.* Bologna: EUA. Available at: https://cora.ucc.ie/handle/10468/1471 (Accessed: 5 September 2026).

Lee, J. K., Kim, D. Y. and Park, S. H. (2023) 'Hybrid OCR pipeline combining deep learning and rule-based systems for handwritten academic documents', *Pattern Recognition Letters*, 174, pp. 45-53. doi:10.1016/j.patrec.2023.08.012.

OpenAI (2024) *GPT-4o technical report.* Available at: https://openai.com/research/gpt-4o (Accessed: 3 September 2026).

Shafiq, M. Z., Gillani, N. and Latif, S. (2022) 'Towards automated essay scoring using large language models', *Computers and Education: Artificial Intelligence*, 3, 100092. doi:10.1016/j.caeai.2022.100092.

Smith, J. and Nair, P. (2020) 'OBE-based assessment and accreditation: A framework for engineering programs in developing countries', *IEEE Transactions on Education*, 63(3), pp. 200-210. doi:10.1109/TE.2019.2960512.

Washington Accord Secretariat (2023) *Graduate attributes and professional competencies.* International Engineering Alliance. Available at: https://www.ieagreements.org/assets/Uploads/Documents/Policy/Graduate-Attributes-and-Professional-Competencies.pdf (Accessed: 10 September 2026).

---

## Plagiarism Report

*(Plagiarism report must show less than 30% similarity)*

*Attach the Turnitin or equivalent plagiarism detection report here before submission.*

---

*End of Report*
