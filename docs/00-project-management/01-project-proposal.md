# IntelliGrade: An End-to-End Outcome-Based Examination Management and Intelligent Script Evaluation Ecosystem for Higher Education Institutions

**Official Project Title:** IntelliGrade: An End-to-End Outcome-Based Examination Management and Intelligent Script Evaluation Ecosystem for Higher Education Institutions  
**Document Version:** 4.0.0 (Enterprise Academic Release)  
**Lead Architect & Developer:** Md. Taher Bin Omar Hijbullah  
**Target Institutional Standard:** International University of Business Agriculture and Technology (IUBAT) & BAETE OBE Accreditation Standards  
**Last Updated:** August 30, 2026  

---

## 1. Executive Summary & Vision

**IntelliGrade** is an enterprise academic SaaS platform and comprehensive evaluation ecosystem engineered to unify and automate the complete university examination lifecycle. Higher education institutions face significant challenges across the examination spectrum: manual routine scheduling, disconnected question paper and rubric authoring, laborious handwriting deciphering, grading fatigue, complex Course Outcome (CO) and Program Outcome (PO) weighted mathematics, and delayed student feedback.

IntelliGrade resolves these institutional challenges through a **Human-in-the-Loop, AI-Augmented Evaluation Pipeline**. The platform provides centralized administrative governance, AI exam routine parsing, 23-section IUBAT OBE taxonomy mapping, 300 DPI high-resolution script preprocessing, optical character recognition (OCR), question boundary segmentation, dual evaluation workbenches (Multi-Provider AI & Fast-Track Manual), split-screen teacher verification, and real-time OBE tabulation with 8-sheet Excel workbook export.

---

## 2. Problem Statement & Institutional Justification

| Traditional Examination Bottleneck | Impact on Academic Operations | IntelliGrade Enterprise Solution |
| :--- | :--- | :--- |
| **Manual Script Reading & Fatigue** | Inconsistent grading across examiners; grading drift between first and last graded scripts; delayed publication. | Standardized AI evaluation using structured rubrics, criterion-level scoring, and instant confidence validation. |
| **Complex OBE CO/PO Calculations** | Manual calculation of CO and PO percentages per student and class takes weeks and is prone to human error. | Automated real-time CO/PO attainment matrix calculation, live aggregation, and 8-sheet Excel generation. |
| **Subjective Feedback** | Students receive only a raw numeric mark with zero actionable feedback on strengths or conceptual mistakes. | Question-wise detailed feedback, highlighting strengths, identified mistakes, and missing key points. |
| **Paper-Based Record Management** | Vulnerable to physical loss, damage, and lack of historical traceability for accreditation audits. | Centralized digital archive with 300 DPI working copies, full audit trails, and certified watermarked PDF scripts. |
| **Disconnected Academic Hierarchy** | Exam controllers, department heads, teachers, and students operate in silos with delayed communication. | Role-Based Access Control (RBAC) portals with real-time dashboards and automated institutional email triggers. |

---

## 3. System Architecture & High-Level Components

```mermaid
graph TD
    subgraph Governance & Ingestion
        A[Chief Exam Controller / Dept Head] -->|Administers| B[Colleges / Schools / Departments / Courses / Faculty]
        A -->|Uploads| C[Exam Routine PDF/Image]
        C -->|AI Routine Parser| D[Automated Scheduled Examinations]
    end

    subgraph Question & Rubric Studio
        E[Faculty / Examiner] -->|Uploads / Builds| F[23-Section Question Paper & Golden Rubric]
        F -->|Extracts| G[CO, PO, Bloom, KP, CEP, CEA, Figures, Tables, Formulas]
    end

    subgraph Script Ingestion & Boundary Engine
        H[Student Answer Scripts] -->|Batch Upload / PDF / Images| I[300 DPI Image Normalization & Preprocessing]
        I -->|Hybrid OCR| J[PyMuPDF Font Map + PyTesseract + EasyOCR]
        J -->|Boundary State Machine| K[Question Number Detector & Page Mapping]
        K -->|Teacher Confirmation Modal| L[Confirmed Answer Regions]
    end

    subgraph AI Evaluation & Failover Core
        L -->|TaskRouter| M{Failover AI Provider}
        M -->|1. Local Offline Vision| N1[Moondream2 / Ollama (800px LANCZOS)]
        M -->|2. Fast Cloud LLM| N2[Groq Llama-3.3 70B]
        M -->|3. Cloud Aggregator| N3[OpenRouter API]
        M -->|4. Vision & Reasoning| N4[Gemini 2.5 Flash / OpenAI GPT-4o]
        M -->|JSON Schema Validator| O[Structured Evaluation Result & Confidence Score]
    end

    subgraph Grading Workbench & Verification
        O --> P[Split-Screen Teacher Grading Workbench]
        E -->|Review / Override / Approve| P
        P -->|Finalize & Certify| Q[Certified Stamped PDF Script]
        Q -->|Automatic Cleanup| Q2[Purge Obsolete Working Images]
    end

    subgraph OBE Tabulation & Dissemination
        P -->|Live Sync| R[Course OBE Tabulation Engine]
        R -->|Calculates| S[CT 10% + Mid 25% + Final 50% + Assign 10% + Att 5%]
        R -->|Bi-directional Sync| T[8-Sheet OBE Excel Workbook & Student Dashboard]
        R -->|EmailService| U[Automated Institutional Result Notification]
    end
```

---

## 4. Key Actor Roles & Portal Capabilities

### 4.1 Chief Exam Controller (`/dashboard/exam-controller/`)
- **Institutional Structure**: Add and manage Colleges, Schools, Departments, Courses, Faculty, and Department Heads.
- **Student Admissions & Security**: Review, approve, or reject student registration requests with automated welcome emails.
- **AI Infrastructure Configuration**: Configure system-wide AI provider keys (Gemini, Groq, OpenAI, OpenRouter, Ollama) and monitor API health.
- **AI Exam Routine Scanner**: Multi-page PDF/Image exam schedule OCR parser with auto-department detection and bulk exam creation.

### 4.2 Department Head (`/dashboard/dept-head/`)
- **Departmental Oversight**: Real-time pass rate analytics, active faculty counts, enrolled student tallies, and scheduled examination tracking.
- **Course Tabulation Approval**: Review and audit course-level OBE grade records, CO/PO attainment graphs, and Continuous Quality Improvement (CQI) reports.
- **Faculty Workload Management**: Monitor script evaluation progress across assigned department examiners.

### 4.3 Faculty Member / Examiner (`/dashboard/teacher/`)
- **Question Paper & Rubric Studio**: Build or scan exam papers with 23-section taxonomy (CO/PO, Bloom levels, figures, data tables, LaTeX matrices).
- **Master Benchmark Solution Studio**: Upload teacher solution scripts and extract step-by-step mark distribution.
- **Dual Evaluation Wizards**:
  - *AI Wizard (v3.0)*: Multi-image/PDF upload, automatic OCR boundary detection, confidence review, and AI grading.
  - *Manual Wizard*: Fast PDF page slicing, pure manual question-to-page assignment, and split-screen teacher grading without AI interference.
- **Split-Screen Grading Workbench**: Side-by-side verification of scanned scripts, OCR text, rubric benchmarks, AI scores, and feedback.
- **OBE Course Tabulation**: Manage course grade sheets (CT, Mid, Final, Assignment, Attendance 5%) with live bi-directional Excel export and student sync.

### 4.4 Student (`/dashboard/student/`)
- **Self-Service Portal**: Secure registration, login, and password reset via 6-digit OTP email.
- **Real-Time Grade Dashboard**: View official course tabulation grades, GPA (4.00 scale), component breakdowns, and download certified evaluated PDF scripts.
