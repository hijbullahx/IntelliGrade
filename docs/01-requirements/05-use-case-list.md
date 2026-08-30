# IntelliGrade - Exhaustive Use Case Inventory

**Document Version:** 3.5.0 (Enterprise Academic Edition)  
**Last Updated:** August 30, 2026  
**Auditor:** Principal Enterprise Systems Architect  

---

## 1. Actor Catalog

- **ACT-01: Chief Exam Controller (ADMIN)** - Master administrator managing academic hierarchy, student approvals, AI configs, and semester routine parsing.
- **ACT-02: Department Head (DEPT_HEAD)** - Oversees departmental pass rates, faculty evaluation progress, and course OBE tabulations. Supports login with both Username and Email.
- **ACT-03: Faculty Member / Examiner (TEACHER)** - Authors questions/rubrics, uploads scripts, reviews AI evaluations, overrides marks, and exports tabulations.
- **ACT-04: Student (STUDENT)** - Views published course grades, question-wise feedback, and downloads certified PDF scripts.
- **ACT-05: AI Evaluation Engine (SYSTEM)** - Automated background sub-agent performing OCR, boundary detection, rubric evaluation, and email dispatch.

---

## 2. Complete Use Case Inventory

```text
====================================================================================================
USE CASE ID   USE CASE TITLE                          PRIMARY ACTOR     DESCRIPTION & TRIGGER
====================================================================================================
UC-01         User Login & Role-Based Dispatch        All Users         User authenticates with username/password;
                                                                        system redirects to specific role dashboard.
UC-02         Student Self-Registration               Student           Student signs up; status set to pending
                                                                        until approved by Exam Controller.
UC-03         Password Reset via 6-Digit OTP Email    All Users         User requests reset; receives 6-digit OTP
                                                                        via SMTP; verifies OTP and resets password.
UC-04         Academic Structure Management           Controller        Add, edit, delete, or toggle Colleges,
                                                                        Schools, Departments, and Courses.
UC-05         Faculty & Dept Head Provisioning        Controller        Create faculty and department head accounts
                                                                        with automated credential welcome emails.
UC-06         Student Registration Approval Workflow  Controller        Review pending student accounts; approve or
                                                                        reject with automated email notification.
UC-07         AI Infrastructure Configuration         Controller        Configure API keys for Gemini, Groq, OpenAI,
                                                                        OpenRouter, Ollama, and set OCR thresholds.
UC-08         AI Examination Routine Scanning         Controller        Upload multi-page exam routine PDF/Image;
                                                                        AI extracts schedules and bulk-creates exams.
UC-09         Department Head Performance Overview    Dept Head         View departmental pass rates, active faculty,
                                                                        enrolled students, and exam schedules.
UC-10         Department Course Tabulation Audit      Dept Head         Audit course-level OBE grade records, CO/PO
                                                                        attainments, and download Excel reports.
UC-11         23-Section Question Paper Authoring     Teacher           Define exam questions with Bloom's Taxonomy,
                                                                        CO/PO/KP/CEP/CEA tags, figures, and formulas.
UC-12         AI Question Paper Scanning              Teacher           Upload official exam paper PDF; AI extracts
                                                                        all questions, marks, and rubric criteria.
UC-13         Master Solution Script Ingestion        Teacher           Upload golden benchmark solution script; system
                                                                        segments and links steps to questions.
UC-14         Batch Answer Script Upload              Teacher           Upload multi-page student PDF/image scripts;
                                                                        system generates 300 DPI working copies.
UC-15         Hybrid Multi-Engine Script OCR          System / Teacher  System runs PyMuPDF -> PyTesseract ->
                                                                        EasyOCR (PyTorch CPU fallback) with BBoxes.
UC-16         Question Boundary & Mapping Discovery   System / Teacher  State machine detects question numbers; teacher
                                                                        verifies or visually adjusts answer bounds.
UC-17         Multi-Provider AI Script Evaluation     System / Teacher  Failover AI orchestrator evaluates answers
                                                                        against rubrics with 429 rate limit backoff.
UC-18         Split-Screen Grading Workbench Review   Teacher           Side-by-side verification of scanned script,
                                                                        OCR text, AI score, criteria, and feedback.
UC-19         Manual Mark Override & Audit Logging    Teacher           Teacher overrides AI mark or edits comments;
                                                                        system logs modification audit trail.
UC-20         Finalize Evaluation & PDF Certification Teacher           Teacher locks submission; system stamps and
                                                                        generates certified evaluated PDF script.
UC-21         Real-Time OBE Course Tabulation         Teacher           Tabulation aggregates CT (10%), Mid (25%),
                                                                        Final (50%), Assign (10%), Attendance (5%).
UC-22         Live Tabulation Grade Record Editing    Teacher           Edit student marks directly in web table modal;
                                                                        instantly syncs to DB, Excel, and Student.
UC-23         8-Sheet OBE Excel Workbook Export       Teacher / Head    Export official 8-sheet Excel spreadsheet with
                                                                        HOME, ASSIGNMENT, CO/PO, and CQI formulas.
UC-24         Institutional Email Result Dispatch     System            System emails student with final grade summary
                                                                        and attached certified PDF answer script.
UC-25         Student Grade Dashboard & Transparency  Student           Student views official OBE course grades, GPA,
                                                                        question breakdowns, and downloads PDF scripts.
====================================================================================================
```
