# IntelliGrade: An End-to-End Outcome-Based Examination Management and Intelligent Script Evaluation Ecosystem for Higher Education Institutions

**Document Reference:** `DOCS-UPDATE-4.0.0`  
**Official System Title:** IntelliGrade: An End-to-End Outcome-Based Examination Management and Intelligent Script Evaluation Ecosystem for Higher Education Institutions  
**Lead Architect & Auditor:** Md. Taher Bin Omar Hijbullah  
**Audit Timestamp:** August 30, 2026  
**System Health:** Production Ready — Zero System Check Errors (Django 5.2.x, SQLite/PostgreSQL, Multi-Provider AI Core)

---

## 1. Executive Summary & Core Milestones

**IntelliGrade** is an end-to-end outcome-based examination management and intelligent script evaluation ecosystem engineered specifically for higher education institutions aligned with IUBAT and BAETE accreditation standards. The platform eliminates manual examination management and grading friction by uniting central administrative governance, AI routine scheduling, 23-taxonomy OBE question blueprints, computer vision (PyMuPDF, PyTesseract, EasyOCR), structured rubric engines, multi-provider AI evaluation failovers (Local Ollama Moondream, Groq Llama-3.3 70B, Google Gemini, OpenRouter, OpenAI GPT-4o), interactive split-screen workbenches, and real-time OBE course tabulation with 8-sheet Excel reporting.

### Core Architectural Capabilities Implemented:
1. **Academic Hierarchy & Multi-Tier Governance**: Complete RBAC governance covering Chief Exam Controller (`ADMIN`), Department Head (`DEPT_HEAD`), Faculty Member / Examiner (`TEACHER`), and Student (`STUDENT`) with profile approval workflows.
2. **AI Exam Routine Scanner**: Multi-page PDF/image ingestion with OCR parsing that auto-detects departments, course codes, exam dates, times, and batch-creates scheduled examinations.
3. **23-Section Question Paper & Rubric Studio**: Full taxonomy ingestion capturing Bloom's Taxonomy, Course Outcomes (CO1-CO6), Program Outcomes (PO1-PO12), Knowledge Profiles (KP1-KP8), Complex Engineering Problems (CEP1-CEP7), Complex Engineering Activities (CEA1-CEA5), Figures, Tables, and LaTeX mathematical formulas.
4. **Master Benchmark Solution Extraction**: OCR extraction and step-by-step mark distribution ingestion from teacher's golden benchmark solutions.
5. **Universal Answer Script Processing**: Ingestion of multi-page PDFs, high-res photos, and nested ZIP archives with automatic 300 DPI image rendering, rotation management, and cached text normalization.
6. **Dual Evaluation Pipelines**:
   - **AI Answer Script Evaluation Wizard (v3.0)**: Automatic question heading detection, spatial region segmentation, multi-signal confidence matching, and automated AI scoring.
   - **Manual Script Evaluation & Mapping Wizard**: 100% direct teacher marking with zero AI/OCR interference, fast PDF page slicing, manual question-to-page assignment, and split-screen teacher grading.
7. **Multi-Provider AI Evaluation & Failover Core**: Resilient orchestrator with task routing, cooldown registries (429 handling), Local Ollama Moondream vision (800px LANCZOS downsampling, JPEG quality 75), Groq, OpenRouter, and Gemini providers.
8. **Interactive Split-Screen Workbenches**: High-resolution script viewer, OCR overlay, bounding box visualizer, rubric criteria checklist, marks override, AI feedback editor, and live re-evaluation triggers.
9. **OBE Course Tabulation & 8-Sheet Workbook Engine**: Real-time aggregation (CT 10%, Midterm 25%, Final 50%, Assignment 10%, Attendance 5%), CO/PO attainment matrices, Continuous Quality Improvement (CQI) triggers, and automated openpyxl Excel exports.
10. **Institutional Email & Notification Service**: Asynchronous non-blocking multi-threaded email dispatch for account provisioning, OTP password resets, exam assignments, student result publication (with PDF attachments), and department tabulation summaries.

---

## 2. Recent Technical Enhancements & Surgical Optimizations

### Phase 1 Optimization (Database Composite Indexes & Performance)
- **Database Composite Indexes (`core/models.py`)**:
  - `StudentSubmission`: Added `models.Index(fields=['examination', 'status'])`, `models.Index(fields=['student_roll_no'])`, `models.Index(fields=['is_finalized'])`.
  - `EvaluationResult`: Added `models.Index(fields=['status', 'requires_manual_review'])`.
  - `QuestionMapping`: Added `models.Index(fields=['submission', 'mapping_status'])`, `models.Index(fields=['submission', 'is_confirmed'])`.
  - `StudentGradeRecord`: Added `models.Index(fields=['tabulation', 'student_id'])`, `models.Index(fields=['tabulation', 'overall_score'])`, `models.Index(fields=['is_manually_edited'])`.
  - Applied cleanly via migration `0028_evaluationresult_core_evalua_status_1f634b_idx_and_more.py`.
- **Elimination of N+1 Query Leaks**:
  - `evaluation_workspace` view: Eager-loaded relations with `.select_related('question__rubric', 'page', 'evaluation_result').prefetch_related('question__figures_rel', 'question__tables_rel', 'question__formulas_rel')`.
  - `course_tabulation_view`: Attached `.select_related('examination')` to `evaluated_subs` queryset.
  - `sync_submission_to_tabulation`: Updated answer query to `.select_related('question__rubric', 'evaluation_result')`.
- **Storage Lifecycle & Finalization Cleanup**:
  - `FinalizationService._purge_temporary_artifacts`: Automatically purges obsolete working images (`media/submission_working/`), preview PDFs (`media/submission_preview/`), and OCR trace directories upon final certificate PDF creation.
- **Local Ollama Vision Optimization**:
  - `LocalOfflineVisionProvider`: Enforced 800px LANCZOS downsampling and JPEG `quality=75` compression pipeline prior to local inference dispatch (`/api/generate`).
- **Wizard Endpoint & JavaScript Sanitization**:
  - Resolved `SyntaxError: Invalid Unicode escape sequence` in `evaluation_wizard.html` by ordering filters as `truncatechars:80|escapejs`.
  - Fixed PDF upload endpoint in `manual_evaluation_wizard.html` to use `api_wizard_upload_pdf`, ensuring pure page slicing without triggering unwanted AI evaluation in manual grading mode.

---

## 3. Ground Truth Verification Summary

| Component | Status | Verification Detail |
| :--- | :--- | :--- |
| **Django Framework** | Active (5.2.x) | Zero configuration or linting errors via `python manage.py check`. |
| **Database Migrations** | 28 Migrations Applied | Full schema synchronization across all 28 core migrations. |
| **Multi-Provider AI** | Active & Resilient | Local Moondream, Groq, OpenRouter, Gemini, OpenAI with dynamic failover. |
| **OBE Calculation** | Verified | Automatic calculation of CT, Mid, Final, Assignment, Attendance, CO/PO attainment. |
| **Security & RBAC** | Enforced | Strict role-based route protection and OTP password recovery. |

---

## 4. Master Technical Specifications & Capacity Blueprints

1. [`docs/HARDWARE_API_BENCHMARK_SPEC.md`](file:///f:/Hijbullah/IntelliGrade/docs/HARDWARE_API_BENCHMARK_SPEC.md): Comprehensive deep-dive diagnostic on OCR and AI evaluation latencies, hardware specifications (RTX 4090/L4 GPU, EPYC CPUs), Cloud Tier 1 RPM/TPM benchmarks, cost matrices, and hybrid deployment blueprints.
2. [`docs/MASTER_SYSTEM_REPORT.md`](file:///f:/Hijbullah/IntelliGrade/docs/MASTER_SYSTEM_REPORT.md): Complete architectural blueprint, end-to-end actor manuals, full relational database schema with composite indexes, and complete REST/AJAX API catalog.
3. [`docs/SYSTEM_IMPROVEMENT_ROADMAP.md`](file:///f:/Hijbullah/IntelliGrade/docs/SYSTEM_IMPROVEMENT_ROADMAP.md): Architectural roadmap detailing Celery/Redis distributed workers, INT8 quantization, token bucket rate limiters, and pgvector RAG for historical teacher mark calibration.
