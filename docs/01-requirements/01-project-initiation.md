# IntelliGrade — Project Initiation Document (PID)

**Document Version:** 4.0.0 (Enterprise Academic Release)  
**Project Name:** IntelliGrade — AI-Assisted Outcome-Based Education (OBE) Examination Evaluation & Management System  
**Prepared By:** Md. Taher Bin Omar Hijbullah (Lead Technical Architect)  
**Target Institutional Standard:** International University of Business Agriculture and Technology (IUBAT) & BAETE OBE Accreditation  
**Date:** August 30, 2026  
**Status:** Operational / Fully Implemented  

---

## 1. Project Vision & Purpose

**IntelliGrade** is an institutional academic evaluation platform designed to empower university educators, department heads, and exam controllers. The system augments traditional examination workflows with state-of-the-art AI evaluation, automated OCR, 23-section OBE taxonomy mapping, and real-time tabulation while ensuring **absolute instructor authority and oversight**.

Unlike generic AI grading tools, IntelliGrade is custom-tailored to the institutional standards of IUBAT and OBE accreditation boards (such as BAETE). It seamlessly connects academic structure creation, routine scanning, question paper authoring, rubric criteria formulation, script preprocessing, question boundary detection, AI evaluation, teacher review, and official 8-sheet OBE Excel tabulation.

---

## 2. Problem Statement & Operational Challenges

1. **Labor-Intensive Script Evaluation**: Manually evaluating hundreds of multi-page handwritten scripts per semester leads to examiner fatigue, grading drift, and long turnaround times before results are released.
2. **Complex Outcome-Based Education (OBE) Accounting**: Calculating student-level and class-wide Course Outcome (CO1–CO6) and Program Outcome (PO1–PO12) attainments requires complex multi-step weighted math that is error-prone when done manually in spreadsheets.
3. **Lack of Detailed Student Feedback**: Students traditionally receive only a single overall mark, leaving them with no visibility into which concepts they mastered or where they made errors.
4. **Vulnerability of Physical Paper Records**: Physical paper answer scripts can be misplaced or damaged, and retrieving historical scripts during academic accreditation reviews is cumbersome.
5. **Multi-Role Coordination Barriers**: Exam controllers, department heads, faculty examiners, and students lack a synchronized digital ecosystem for examination schedules, approvals, and score verification.

---

## 3. Project Objectives

- **Primary Objective**: Build a robust, scalable, and secure AI-assisted academic examination evaluation platform that slashes grading turnaround time while maintaining total instructor grading authority and full OBE compliance.
- **Specific Objectives**:
  1. Reduce answer script grading time by up to 70% through automated OCR and AI-suggested marks.
  2. Implement complete 23-section IUBAT OBE taxonomy metadata across all examination questions.
  3. Provide dual evaluation workflows: Automated AI Evaluation Wizard (v3.0) and 100% Direct Manual Grading Wizard.
  4. Provide a split-screen teacher grading workbench with 1-click override and approval mechanisms.
  5. Implement real-time Course OBE Tabulation with bi-directional 8-sheet Excel workbook export (`openpyxl`).
  6. Provide role-based access control (RBAC) portals for Chief Exam Controller, Department Head, Teacher, and Student.
  7. Support resilient, zero-downtime AI evaluation via a multi-provider failover orchestrator (Local Vision Moondream, Groq, OpenRouter, Gemini, OpenAI).
  8. Deliver institutional email notifications for account creation, password reset OTPs, exam assignments, published results (with watermarked PDF), and tabulation summaries.

---

## 4. Scope Matrix

```text
========================================================================================
SYSTEM AREA               IN-SCOPE CAPABILITY                                  OUT-OF-SCOPE
========================================================================================
Academic Governance       Colleges, Schools, Departments, Courses, User RBAC   Financial Billing
Exam Administration       AI Exam Routine Parsing, Batch Exam Scheduling       Live Video Proctoring
Question Paper Studio     23-Taxonomy Builder, Figures, Tables, LaTeX Matrices Online Quiz Authoring
Answer Script Ingestion   300 DPI Preprocessing, Hybrid PyTesseract/EasyOCR    Automated Essay Writing
Boundary Detection        State machine regex, multi-page answer propagation   Plagiarism Web Crawling
AI Evaluation Core        Multi-provider failover (Local Moondream/Groq/etc.)  Unsupervised Auto-Pass
Teacher Review            Split-screen workbench, score override, audit log    Student Re-grading
OBE Tabulation            5% Attendance, 8-sheet Excel export, live sync       External LMS Sync (Phase 2)
Dissemination             Certified watermarked PDF script, Student Dashboard  Physical Postal Mailing
========================================================================================
```

---

## 5. Key Stakeholders & Personas

- **Chief Exam Controller (ADMIN)**: Oversees institutional structure, approves student accounts, configures AI API credentials, and scans university exam routines.
- **Department Head (DEPT_HEAD)**: Monitors department pass rates, audits course tabulation reports, and tracks faculty evaluation progress.
- **Faculty / Examiner (TEACHER)**: Prepares question papers and rubrics, uploads answer scripts, reviews AI grades on the split-screen workbench, and finalizes course tabulations.
- **Student (STUDENT)**: Registers for portal access, tracks exam schedules, reviews question-by-question graded feedback, and downloads certified PDF scripts.