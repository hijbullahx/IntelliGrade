# IntelliGrade — Detailed User Stories & Acceptance Criteria

**Document Version:** 3.5.0 (Enterprise Academic Edition)  
**Last Updated:** August 29, 2026  
**Auditor:** Principal Enterprise Systems Architect  

---

## 1. Persona-Driven User Stories

### US-01: Chief Exam Controller — Routine Ingestion
- **As a** Chief Exam Controller,
- **I want to** upload multi-page university exam routines in PDF or image format,
- **So that** the AI automatically extracts course codes, dates, times, and examiners, and bulk-creates scheduled exams without manual data entry.
- **Acceptance Criteria**:
  - *Given* an official semester routine document,
  - *When* I click "Scan Routine with AI",
  - *Then* the system renders pages at 300 DPI, runs OCR, parses schedule rows via LLM, matches course codes with 0ms local DB lookups, and presents a confirmation modal before batch creation.

### US-02: Chief Exam Controller — Student Approval & Onboarding
- **As a** Chief Exam Controller,
- **I want to** review and approve self-registered student accounts,
- **So that** only legitimately enrolled university students access examination portals.
- **Acceptance Criteria**:
  - *Given* a list of pending student registrations,
  - *When* I click "Approve",
  - *Then* the student's `Profile.is_approved` flag is set to `True`, and an automated institutional welcome email is dispatched to their email address.

### US-03: Department Head — Real-Time Departmental Pass Rates
- **As a** Department Head,
- **I want to** monitor live pass rates, active courses, and faculty evaluation workloads,
- **So that** I have instant visibility into departmental academic performance and accreditation readiness.
- **Acceptance Criteria**:
  - *Given* I am logged into `/dashboard/dept-head/`,
  - *When* the dashboard loads,
  - *Then* it calculates the live departmental pass rate across all course tabulations and routines, and lists all active faculty members and assigned exams.

### US-04: Faculty Member — 23-Section OBE Question Paper Authoring
- **As a** Faculty Examiner,
- **I want to** define question papers with complete IUBAT OBE metadata (Bloom's level, CO1–CO5, PO1–PO12, KP, CEP, CEA),
- **So that** my examination adheres strictly to BAETE accreditation standards.
- **Acceptance Criteria**:
  - *Given* the Question & Rubric Studio (`/teacher/questions-rubric/`),
  - *When* I author or AI-scan a question paper,
  - *Then* the system records question prompts, maximum marks, Bloom taxonomy classifications, Course Outcome mappings, and criterion rubrics in the database.

### US-05: Faculty Member — Multimodal Script Ingestion & 300 DPI Preprocessing
- **As a** Faculty Examiner,
- **I want to** drag and drop batch PDF or image student scripts,
- **So that** the system automatically generates high-resolution 300 DPI working copies and runs hybrid OCR.
- **Acceptance Criteria**:
  - *Given* multiple student answer scripts in PDF/image format,
  - *When* I upload them via `/scripts/upload/` or the evaluation wizard,
  - *Then* the system generates versioned 300 DPI images in `submission_working/`, runs PyTesseract/EasyOCR fallback, and detects question boundaries.

### US-06: Faculty Member — Interactive Question Boundary Confirmation
- **As a** Faculty Examiner,
- **I want to** inspect detected question boundaries and adjust visual bounding boxes before AI evaluation,
- **So that** the AI evaluator evaluates the exact handwritten region corresponding to each question.
- **Acceptance Criteria**:
  - *Given* an uploaded script with detected question regions,
  - *When* the interactive mapping modal opens,
  - *Then* I can verify page associations, adjust crop coordinates visually, and click "Confirm Mapping & Run Evaluation".

### US-07: Faculty Member — Split-Screen Grading Workbench & Override
- **As a** Faculty Examiner,
- **I want to** review AI-evaluated answers side-by-side with original script images and override marks,
- **So that** I retain full authority over student grades and can provide custom feedback.
- **Acceptance Criteria**:
  - *Given* an AI-evaluated student submission,
  - *When* I open `/teacher/submission/<id>/workspace/`,
  - *Then* I see the original script on the left and AI scores/rubrics on the right; adjusting a mark updates the database and logs a `TeacherReview` audit trail entry.

### US-08: Faculty Member — Real-Time OBE Course Tabulation & Excel Export
- **As a** Faculty Examiner,
- **I want to** manage a course-wide OBE tabulation sheet (CT 10%, Mid 25%, Final 50%, Assign 10%, Att 5%),
- **So that** I can edit marks live in the web table and export an official 8-sheet Excel workbook.
- **Acceptance Criteria**:
  - *Given* the Course Tabulation page (`/course/<id>/tabulation/`),
  - *When* I edit a student's marks and click "Save & Sync Tabulation",
  - *Then* the system updates `StudentGradeRecord`, recalculates overall percentages and letter grades, synchronizes the student portal, and exports an 8-sheet Excel file (`HOME`, `ASSIGNMENT`, `CO_ATTAINMENT`, `PO_ATTAINMENT`, `CO_CLASS_ATTAINED`, `PO_CLASS_ATTAINED`, `CQI`).

### US-09: Student — Real-Time Grade & Script Transparency
- **As a** University Student,
- **I want to** view my official course tabulation grades, GPA, question-by-question marks, and feedback,
- **So that** I have full academic transparency and can download certified PDF answer scripts.
- **Acceptance Criteria**:
  - *Given* I am logged into `/dashboard/student/`,
  - *When* results are finalized,
  - *Then* I see my overall course grade (e.g. `91.75% / A+`), component breakdowns, criterion feedback, and a button to download the watermarked certified PDF script.