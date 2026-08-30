# IntelliGrade - Functional System Modules & Architecture Catalog

**Document Version:** 3.5.0 (Enterprise Academic Edition)  
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
  - Direct entry points to Question Paper Builder, Batch Script Upload, Evaluation Wizard, and OBE Tabulation.
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
  - Employs PyMuPDF and regex LLM prompt routing to extract exam dates, times, course codes, course titles, total marks, and assigned examiners.
  - 0ms local database lookup matching existing course and faculty records without overwriting.

### MOD-08: Question Paper & 23-Taxonomy Studio
- **Files**: `core/models.py` (`Question`, `Rubric`, `QuestionFigure`, `QuestionTable`, `QuestionFormula`), `core/views.py` (`question_rubric_manage`)
- **Key Functions**:
  - 23-section IUBAT question metadata builder (Bloom levels, CO1-CO5, PO1-PO12, KP1-KP8, CEP1-CEP7, CEA1-CEA5).
  - Supports LaTeX mathematical matrices with automated backslash regex sanitization.
  - Extracts and displays bounding box coordinates for diagrams, data tables, and equations.

### MOD-09: Master Benchmark Solution Service
- **Files**: `core/ai_engine/solution_parser/`, `core/views.py` (`api_upload_master_solution`)
- **Key Functions**:
  - Ingests instructor's golden benchmark solution document.
  - Aligns step-by-step marking rubrics against official questions.

### MOD-10: Script Ingestion & 300 DPI Preprocessor
- **Files**: `core/models.py` (`StudentSubmission`, `SubmissionImage`, `SubmissionPage`)
- **Key Functions**:
  - Drag-and-drop batch upload supporting multi-page PDF or JPEG/PNG scripts.
  - PyMuPDF 300 DPI high-resolution rendering with OpenCV deskewing and adaptive thresholding.

### MOD-11: Hybrid Multi-Engine OCR
- **Files**: `core/ai_engine/ocr/engine.py`
- **Key Functions**:
  - Multi-tier optical character recognition:
    1. PyMuPDF embedded font glyph extraction.
    2. PyTesseract high-speed printed text OCR.
    3. EasyOCR deep learning handwriting fallback powered by PyTorch CPU.

### MOD-12: Question Boundary & Mapping Engine
- **Files**: `core/ai_engine/mapping/orchestrator.py`
- **Key Functions**:
  - Regex state machine for question boundary detection.
  - Interactive visual crop confirmation modal for teacher overrides.

### MOD-13: AI Provider Failover Orchestrator
- **Files**: `core/ai_engine/providers/failover.py`
- **Key Functions**:
  - Dynamic fallback chain: Local Moondream2/Ollama -> Groq Llama-3.3 70B -> OpenRouter -> Google Gemini -> OpenAI GPT-4o.
  - Rate-limit (HTTP 429) backoff with 120-second cooldown registry.

### MOD-14: TaskRouter & Cooldown Health Tracker
- **Files**: `core/ai_engine/routing/task_router.py`, `core/models.py` (`AIProviderHealth`)
- **Key Functions**:
  - Task-aware routing for vision vs text vs routine tasks.
  - DB persistence of latency, error counts, and operational health events.

### MOD-15: AI Script Evaluator (v3.0)
- **Files**: `core/ai_engine/evaluation/script_evaluator.py`
- **Key Functions**:
  - Sequentially evaluates student answers against 23-taxonomy rubrics with 0.5s inter-call sleep.
  - Human-in-the-loop flagging: marks `requires_manual_review = True` if confidence < 0.75.
  - Fast-path MCQ evaluation for objective exams (< 3s).

### MOD-16: LaTeX Matrix & JSON Sanitize Engine
- **Files**: `core/ai_engine/providers/base.py`
- **Key Functions**:
  - Regular expression sanitization repairing unescaped backslashes in mathematical matrices.

### MOD-17: Split-Screen Teacher Grading Workbench
- **Files**: `core/views.py` (`evaluation_workspace`)
- **Key Functions**:
  - Synchronized side-by-side view of original script, extracted text, rubric criteria, and AI scores.
  - Per-criteria mark overrides with audit log persistence.

### MOD-18: Certified PDF Script Generator
- **Files**: `core/views.py` (`api_download_evaluated_pdf`)
- **Key Functions**:
  - ReportLab PDF generator stamping institutional header, score badge, criteria breakdown, and official certificate watermark.

### MOD-19: Course OBE Tabulation Engine
- **Files**: `core/services/tabulation_service.py`
- **Key Functions**:
  - Aggregates Class Tests (10%), Midterm (25%), Final Exam (50%), Assignments (10%), and Attendance (5%).
  - Honors teacher lock overrides (`is_manually_edited == True`).

### MOD-20: 8-Sheet Excel Export & Bi-directional Sync
- **Files**: `core/services/tabulation_service.py`, `core/views.py` (`export_course_tabulation`)
- **Key Functions**:
  - openpyxl compiler generating `HOME`, `ASSIGNMENT`, `CO_ATTAINMENT`, `PO_ATTAINMENT`, `CO_CLASS_ATTAINED`, `PO_CLASS_ATTAINED`, and `CQI` sheets.

### MOD-21: Asynchronous Institutional Email Service
- **Files**: `core/services/email_service.py`
- **Key Functions**:
  - Background daemon threads dispatching welcome emails, exam assignments, and published grade notifications via Port 465 SSL.
