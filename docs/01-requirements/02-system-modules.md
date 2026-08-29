# IntelliGrade — Functional System Modules & Architecture Catalog

**Document Version:** 3.5.0 (Enterprise Academic Edition)  
**Last Updated:** August 29, 2026  
**Auditor:** Principal Enterprise Systems Architect  

---

## 1. Modular Architecture Overview

IntelliGrade is constructed around a clean, modular service-oriented architecture implemented within Django applications (`core`), specialized AI subpackages (`core/ai_engine`), and backend services (`core/services`).

```mermaid
graph TD
    subgraph Administration & Portals
        M1[MOD-01: Authentication & RBAC]
        M2[MOD-02: Chief Exam Controller Portal]
        M3[MOD-03: Department Head Dashboard]
        M4[MOD-04: Teacher / Examiner Portal]
        M5[MOD-05: Student Transparency Portal]
    end

    subgraph Academic Ingestion & Authoring
        M6[MOD-06: Academic Structure Management]
        M7[MOD-07: AI Exam Routine Parser]
        M8[MOD-08: Question Paper & 23-Taxonomy Studio]
        M9[MOD-09: Master Benchmark Solution Service]
    end

    subgraph Vision, Preprocessing & OCR
        M10[MOD-10: Script Ingestion & 300 DPI Preprocessor]
        M11[MOD-11: Hybrid Multi-Engine OCR]
        M12[MOD-12: Question Boundary & Mapping Engine]
    end

    subgraph AI Evaluation Core
        M13[MOD-13: AI Provider Failover Orchestrator]
        M14[MOD-14: TaskRouter & Cooldown Health Tracker]
        M15[MOD-15: AI Script Evaluator v3.0]
        M16[MOD-16: LaTeX Matrix & JSON Sanitize Engine]
    end

    subgraph Review, Tabulation & Dissemination
        M17[MOD-17: Split-Screen Teacher Grading Workbench]
        M18[MOD-18: Certified PDF Script Generator]
        M19[MOD-19: Course OBE Tabulation Engine]
        M20[MOD-20: 8-Sheet Excel Export & Bi-directional Sync]
        M21[MOD-21: Asynchronous Institutional Email Service]
    end
```

---

## 2. Granular Module Specifications

### MOD-01: Authentication & Role-Based Access Control (RBAC)
- **Files**: `core/views.py`, `core/models.py` (`Profile.Role`)
- **Key Functions**:
  - Unified session-based authentication with role redirection (`ADMIN`, `DEPT_HEAD`, `TEACHER`, `STUDENT`).
  - Security decorators enforcing strict role boundaries (`@admin_required`, `@teacher_required`, `@student_required`, `@dept_head_required`).
  - Self-registration for students with mandatory Exam Controller approval workflow.
  - 6-digit security OTP password reset dispatch and verification pipeline.

### MOD-02: Chief Exam Controller Portal (`/dashboard/exam-controller/`)
- **Key Functions**:
  - Full CRUD operations on institutional entities: Colleges, Schools, Departments, Courses, Faculty, and Department Heads.
  - Active/Blocked toggle switches for all institutional user accounts.
  - Pending student admissions review with approval/rejection email triggers.
  - AI Configuration Management (`/controller/ai-config/`): Configure API keys, primary providers, and OCR thresholds.

### MOD-03: Department Head Portal (`/dashboard/dept-head/`)
- **Key Functions**:
  - Real-time departmental metrics: Active courses, enrolled students, assigned faculty, scheduled exams.
  - Live semester pass rate calculation derived from routine and tabulation records.
  - Tabulation review and approval workflow for department-level OBE verification.

### MOD-04: Teacher / Examiner Workspace (`/dashboard/teacher/`)
- **Key Functions**:
  - Course-wise examination assignment overview.
  - Direct entry points to Question Paper Builder, Batch Script Upload, Evaluation Wizard, and OBE Tabulation.
  - Live progress indicators for pending vs evaluated answer scripts.

### MOD-05: Student Transparency Portal (`/dashboard/student/`)
- **Key Functions**:
  - Top summary cards displaying overall course grade, cumulative GPA ($4.00$ scale), and completion stats.
  - Course-wise OBE Tabulation table showing individual marks for CT, Mid, Final, Assignment, Attendance (5%), and CO/PO attainments.
  - Script-level transparency view with question-wise score breakdowns, feedback, strengths, and mistakes.
  - One-click certified watermarked PDF script download.

### MOD-06: Academic Structure Management
- **Models**: `College`, `School`, `Department`, `Course`
- **Key Functions**:
  - Multi-tier hierarchy matching university governance (College $\rightarrow$ School $\rightarrow$ Department $\rightarrow$ Course).
  - Assigns multiple faculty instructors to specific course codes.

### MOD-07: AI Exam Routine Parser
- **Files**: `core/ai_engine/routine_parser/`, `core/views.py` (`scan_routine_ai`)
- **Key Functions**:
  - Ingests multi-page official examination routine schedules in PDF or image format.
  - Employs PyMuPDF and regex LLM prompt routing to extract exam dates, times, course codes, course titles, total marks, and assigned examiners.
  - 0ms local re-matching against existing database courses with 1-click batch exam creation.

### MOD-08: Question Paper & 23-Taxonomy Studio
- **Models**: `Question`, `Rubric`, `QuestionFigure`, `QuestionTable`, `QuestionFormula`, `DocumentDOM`
- **Key Functions**:
  - Full IUBAT OBE taxonomy builder: Course Outcomes (CO1–CO5), Program Outcomes (PO1–PO12), Bloom's Taxonomy, Knowledge Profiles (KP1–KP8), Complex Engineering Problems (CEP1–CEP7), Complex Engineering Activities (CEA1–CEA5), command verbs, difficulty levels, and estimated time.
  - AI Question Paper Scanner: Upload official question paper PDF $\rightarrow$ automatically extracts all questions, marks, Bloom levels, and rubrics.
  - Bounding box visual coordinate extraction for attached diagrams, data tables, and LaTeX mathematical formulas.

### MOD-09: Master Benchmark Solution Service
- **Models**: `Examination.master_solution_file`, `Question.master_solution_text`, `Question.master_solution_steps`
- **Key Functions**:
  - Allows teachers to upload a golden handwritten/typed master solution script.
  - Automatically segments and pairs master benchmark solution steps to corresponding questions to guide AI grading.

### MOD-10: Script Ingestion & 300 DPI Preprocessor
- **Files**: `core/ai_engine/preprocessing/image_processor.py`, `core/models.py` (`SubmissionImage`, `SubmissionPage`)
- **Key Functions**:
  - Batch upload support for multi-page PDF files and high-res image sets.
  - Renders all PDF pages at 300 DPI (`zoom = 4.166`) for maximum OCR fidelity.
  - OpenCV-based deskewing, noise reduction, and adaptive thresholding with versioned working copy generation (`submission_working/`).

### MOD-11: Hybrid Multi-Engine OCR
- **Files**: `core/ai_engine/ocr/`, `core/models.py` (`OCRResult`)
- **Key Functions**:
  - Multi-tier OCR strategy: PyMuPDF font extraction $\rightarrow$ PyTesseract (printed text) $\rightarrow$ EasyOCR (handwritten text on PyTorch CPU).
  - Stores word-level and line-level bounding box coordinates (`word_boxes_json`, `line_boxes_json`) and overall page confidence ratings.

### MOD-12: Question Boundary & Mapping Engine
- **Files**: `core/ai_engine/mapping/`, `core/models.py` (`QuestionDetection`, `QuestionMapping`, `MappingHistory`)
- **Key Functions**:
  - State-machine question number detector recognizing variations (`Question 1`, `Ans to Q.1`, `১ নং প্রশ্নের উত্তর`).
  - Strict header validation preventing false positives from question prompts within student answers.
  - Interactive visual mapping modal enabling teachers to adjust and confirm page-to-question associations before AI evaluation.

### MOD-13: AI Provider Failover Orchestrator
- **Files**: `core/ai_engine/providers/failover.py`, `registry.py`, `factory.py`
- **Key Functions**:
  - Seamless multi-provider fallback hierarchy: Local Vision (Moondream/Ollama) $\rightarrow$ Groq (Llama-3.3 70B) $\rightarrow$ OpenRouter $\rightarrow$ Gemini (2.5/2.0 Flash) $\rightarrow$ OpenAI (GPT-4o).
  - Handles HTTP 429 rate limit events, token exhaustion, and API timeouts without crashing.

### MOD-14: TaskRouter & Cooldown Health Tracker
- **Files**: `core/ai_engine/routing/task_router.py`, `core/ai_engine/routing/task_types.py`
- **Key Functions**:
  - Inspects task types (`ANSWER_VISUAL_READ`, `ANSWER_GRADING`, `ROUTINE_PARSE`, `OCR_TEXT`) to route requests to the most efficient provider.
  - Enforces exponential backoff cooldown timers for unhealthy or rate-limited API endpoints.

### MOD-15: AI Script Evaluator v3.0
- **Files**: `core/ai_engine/evaluation/script_evaluator.py`, `core/models.py` (`EvaluationResult`, `EvaluationFeedback`)
- **Key Functions**:
  - Evaluates student answers against question rubrics, criterion allocations, and master solutions.
  - Produces structured JSON output with obtained marks, maximum marks, confidence scores, strengths, mistakes, and missing points.
  - Automatically flags answers scoring below the confidence threshold for mandatory teacher review.

### MOD-16: LaTeX Matrix & JSON Sanitize Engine
- **Files**: `core/ai_engine/providers/base.py`
- **Key Functions**:
  - Employs regex sanitization to escape unescaped backslashes in mathematical formulas (`$$\begin{bmatrix}...$$`), preventing JSON syntax decode errors.

### MOD-17: Split-Screen Teacher Grading Workbench
- **Files**: `core/templates/core/grading_workbench.html`, `core/views.py` (`evaluation_workspace`, `review_evaluation_answer`)
- **Key Functions**:
  - Side-by-side synchronized user interface: Scanned student script on the left, AI score breakdown and rubric criteria on the right.
  - Allows instant manual mark overrides, teacher feedback editing, and re-evaluation requests.
  - Full audit logging of all teacher modifications in `TeacherReview`, `EvaluationHistory`, and `EvaluationAuditLog`.

### MOD-18: Certified PDF Script Generator
- **Files**: `core/ai_engine/evaluation/evaluated_pdf_service.py`
- **Key Functions**:
  - Stitches scanned student pages with official institutional header, awarded marks, teacher feedback, and digital certification watermark.
  - Generates downloadable, certifiable PDF answer scripts.

### MOD-19: Course OBE Tabulation Engine
- **Files**: `core/services/tabulation_service.py`, `core/models.py` (`CourseTabulation`, `StudentGradeRecord`)
- **Key Functions**:
  - Real-time aggregation of multi-component assessments: Class Test (10%), Midterm (25%), Final Exam (50%), Assignment (10%), Attendance (5%).
  - Automatically computes Course Outcome (CO1–CO5) and Program Outcome (PO1–PO12) percentage attainments.
  - Supports live teacher mark edits with instant database, Excel, and student portal synchronization.

### MOD-20: 8-Sheet Excel Export & Bi-directional Sync
- **Files**: `core/services/tabulation_exporter.py`
- **Key Functions**:
  - Generates official 8-sheet OBE Excel workbooks (`HOME`, `ASSIGNMENT`, `CO_ATTAINMENT`, `PO_ATTAINMENT`, `CO_CLASS_ATTAINED`, `PO_CLASS_ATTAINED`, `CQI`) using `openpyxl`.
  - Maps 100-mark question distributions into sheet formulas (`=(J*0.1)+(R*0.25)+(AN*0.5)+(AP*0.1)+Attendance`).

### MOD-21: Asynchronous Institutional Email Service
- **Files**: `core/services/email_service.py`
- **Key Functions**:
  - Dispatches non-blocking emails via Python background threads (`threading.Thread`) from `intelligrade@dsr.iubat.ac.bd`.
  - Notification triggers: Account creation, student approval, OTP password resets, exam assignments, published evaluation results (with PDF attachments), and faculty OBE summary spreadsheets.