# IntelliGrade - Functional System Modules & Architecture Catalog

**Document Version:** 4.0.0 (Enterprise Academic Release)  
**Last Updated:** August 30, 2026  
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

    subgraph Dual Evaluation Pipelines
        M13[MOD-13: AI Evaluation Wizard v3.0]
        M14[MOD-14: Manual Script Grading Wizard]
        M15[MOD-15: AI Provider Failover Orchestrator]
        M16[MOD-16: TaskRouter & Cooldown Health Tracker]
    end

    subgraph Review, Tabulation & Dissemination
        M17[MOD-17: Split-Screen Teacher Grading Workbench]
        M18[MOD-18: Certified PDF Script Generator & Cleanup]
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
  - Department Head login supporting both Username and Email authentication.
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
  - Direct entry points to Question Paper Builder, Batch Script Upload, Dual Evaluation Wizards, and OBE Tabulation.
  - Live progress indicators for pending vs evaluated answer scripts.

### MOD-05: Student Transparency Portal (`/dashboard/student/`)
- **Key Functions**:
  - Top summary cards displaying overall course grade, cumulative GPA (4.00 scale), and completion stats.
  - Course-wise OBE Tabulation table showing individual marks for CT, Mid, Final, Assignment, Attendance (5%), and CO/PO attainments.
  - Script-level transparency view with question-wise score breakdowns, feedback, strengths, and mistakes.
  - One-click certified watermarked PDF script download.

### MOD-06: Academic Structure Management
- **Models**: `College`, `School`, `Department`, `Course`
- **Key Functions**:
  - Multi-tier hierarchy matching university governance (College -> School -> Department -> Course).
  - Assigns multiple faculty instructors to specific course codes.

### MOD-07: AI Exam Routine Parser
- **Files**: `core/ai_engine/routine_parser/`, `core/views.py` (`scan_routine_ai`)
- **Key Functions**:
  - Ingests multi-page official examination routine schedules in PDF or image format.
  - Automatically identifies course codes, course titles, examination dates, start/end times, and departments.
  - Bulk provisions scheduled `Examination` records in the database.

### MOD-08: Question Paper & 23-Taxonomy Studio
- **Models**: `Question`, `Rubric`, `QuestionFigure`, `QuestionTable`, `QuestionFormula`
- **Key Functions**:
  - Authoring and AI scanning of question papers with complete 23-section IUBAT taxonomy: Bloom's level, CO1-CO6, PO1-PO12, KP1-KP8, CEP1-CEP7, CEA1-CEA5.
  - Multi-modal extraction of visual diagrams, tabular data/matrices, and LaTeX mathematical equations with bounding boxes.

### MOD-09: Master Benchmark Solution Service
- **Models**: `Examination.master_solution_file`, `Examination.master_solution_parsed`
- **Key Functions**:
  - Ingests golden benchmark solution scripts uploaded by the course instructor.
  - Extracts step-by-step model solutions and maps partial mark distributions per question.

### MOD-10: Script Ingestion & 300 DPI Preprocessor
- **Files**: `core/ai_engine/services/submission_processor.py`, `core/ai_engine/preprocessing/working_copy_manager.py`
- **Key Functions**:
  - Ingests multi-page PDFs, high-res photos, and ZIP archives.
  - Converts PDF pages into 300 DPI rasterized images (`zoom = 4.166`) with Hough Line deskewing and adaptive contrast enhancement.

### MOD-11: Hybrid Multi-Engine OCR
- **Files**: `core/ai_engine/ocr/`
- **Key Functions**:
  - Primary font map glyph extraction for digital PDFs via PyMuPDF.
  - High-speed PyTesseract optical character recognition for printed script components.
  - Deep learning EasyOCR fallback on PyTorch CPU for handwritten text.

### MOD-12: Question Boundary & Mapping Engine
- **Files**: `core/ai_engine/mapping/`
- **Key Functions**:
  - Multi-pattern heading detection (`"Answer to the Question No."`, `"Ans to Q."`, `"Q1"`).
  - State-machine page propagation assigning consecutive pages to active questions until new headers appear.
  - Teacher confirmation interactive matrix supporting page re-assignments.

### MOD-13: AI Evaluation Wizard (v3.0)
- **Files**: `core/templates/core/evaluation_wizard.html`, `core/views.py` (`api_run_evaluation_v3`)
- **Key Functions**:
  - Multi-step automated pipeline: Image/PDF upload -> Page Builder -> Computer Vision Preprocessing -> Live OCR Scanner Terminal -> Question Mapping Review -> Automated AI Evaluation.

### MOD-14: Manual Script Grading Wizard
- **Files**: `core/templates/core/manual_evaluation_wizard.html`, `core/views.py` (`manual_evaluation_wizard`, `api_wizard_upload_pdf`)
- **Key Functions**:
  - Fast PDF page slicing without triggering OCR/AI scoring.
  - Direct teacher assignment of question-to-page numbers.
  - Immediate launch into Manual Grading Workbench.

### MOD-15: Multi-Provider AI Evaluation Core & Failover
- **Files**: `core/ai_engine/evaluation/`, `core/ai_engine/providers/`
- **Key Functions**:
  - Multi-tier provider failover: Local Offline Moondream (800px LANCZOS JPEG quality 75) -> Groq Llama-3.3 70B -> OpenRouter -> Gemini 2.5 Flash -> OpenAI GPT-4o.
  - Enforces partial credit rubric scoring, confidence estimation, strengths, mistakes, and missing points.

### MOD-16: TaskRouter & Cooldown Health Tracker
- **Files**: `core/ai_engine/routing/task_router.py`, `core/models.py` (`AIProviderHealth`)
- **Key Functions**:
  - Evaluates provider health, response latency, and rate-limit errors (HTTP 429).
  - Applies dynamic cooldown windows to temporarily bypass failing providers.

### MOD-17: Split-Screen Teacher Grading Workbench
- **Files**: `core/templates/core/evaluation_workspace.html`, `core/views.py` (`evaluation_workspace`)
- **Key Functions**:
  - Side-by-side verification view: Left pane displays high-res script page image with zoom/rotate; right pane displays question statement, master solution, rubric criteria, AI score, and feedback.
  - Eager-loaded queries eliminating N+1 database bottlenecks.
  - 1-click teacher override, custom marks adjustment, and real-time re-evaluation.

### MOD-18: Certified PDF Script Generator & Lifecycle Cleanup
- **Files**: `core/ai_engine/evaluation/evaluated_pdf_service.py`, `core/ai_engine/services/finalization_service.py`
- **Key Functions**:
  - Generates official evaluated PDF script with ReportLab grading overlay, summary banner, score breakdown, and security watermarks.
  - Automatically purges obsolete temporary working images from `media/submission_working/`.

### MOD-19: Course OBE Tabulation Engine
- **Files**: `core/services/tabulation_service.py`, `core/models.py` (`CourseTabulation`, `StudentGradeRecord`)
- **Key Functions**:
  - Aggregates multi-assessment components: Class Tests (10%), Midterm (25%), Final (50%), Assignment (10%), Attendance (5%).
  - Computes weighted overall score, letter grade (A+ to F), grade point (0.00 to 4.00), and CO/PO attainment distributions.

### MOD-20: 8-Sheet Excel Export & Bi-directional Sync
- **Files**: `core/views.py` (`export_course_tabulation`)
- **Key Functions**:
  - Generates comprehensive 8-sheet Excel workbook (`openpyxl`):
    1. Overall Course Summary
    2. Continuous Assessment (CT & Assignments)
    3. Midterm Examination
    4. Final Examination
    5. CO Attainment Summary Matrix
    6. PO Attainment Breakdown
    7. Grade Distribution & CQI Analysis
    8. Student-wise Detailed Audit Log

### MOD-21: Asynchronous Institutional Email Service
- **Files**: `core/services/email_service.py`
- **Key Functions**:
  - Non-blocking multi-threaded background email delivery via `dsr.iubat.ac.bd` SMTP.
  - Dispatches account credentials, OTP password resets, exam assignments, published student results (with PDF attachment), and faculty tabulation spreadsheets.
