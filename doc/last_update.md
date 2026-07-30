# IntelliGrade — Project Overview & Full Update Report

**Last Updated:** July 30, 2026  
**Platform Version:** 2.5.0  
**Target Institution Standard:** IUBAT (International University of Business Agriculture and Technology)

---

## 1. Executive Summary

**IntelliGrade** is an enterprise-grade, AI-powered academic evaluation and examination management SaaS platform built with Django and Python. The platform automates the end-to-end lifecycle of university examinations — from AI-driven exam routine parsing, question paper extraction, and academic rubric generation to automated multimodal OCR scanning, AI answer script evaluation, and split-screen teacher grading workbenches.

---

## 2. Core Architecture & Technology Stack

- **Backend Framework**: Django 5.2.16 (Python 3.11)
- **Database Layer**: SQLite (Development) / PostgreSQL (Production)
- **Multimodal OCR & Document Engine**:
  - **PyMuPDF (`fitz`)**: Native PDF font glyph map decoding and 300 DPI high-resolution page rendering.
  - **OpenCV & PIL**: Grayscale conversion, adaptive thresholding, noise reduction, and deskewing.
  - **Skia/PDF Glyph Noise Filter**: Regex filtering (`node\d{6,}`) to clean PostScript font glyph artifacts (`node00000265`, `Skia/PDF`).
- **AI Engine Architecture**:
  - **Provider Factory (`AIProviderFactory`)**: Dynamic instantiation of AI LLM providers.
  - **Failover Provider (`FailoverAIProvider`)**: Automated failover chain (`Gemini` $\rightarrow$ `Groq` $\rightarrow$ `OpenAI` $\rightarrow$ `Ollama`).
  - **Model Quota Failover**: Instant failover on HTTP 429 Rate Limits / Quota Exhaustion (`gemini-2.0-flash` $\rightarrow$ `gemini-2.5-flash` $\rightarrow$ `gemini-1.5-flash` $\rightarrow$ `Groq Llama-3.3 70B` $\rightarrow$ `OpenAI GPT-4o`).
  - **LaTeX Syntax Repair**: Regex backslash repair (`re.sub(r'\\(?![/"\\bfnrtu])', r'\\\\', cleaned)`) to parse complex mathematical matrices and formulas safely without JSON syntax errors.

---

## 3. Major Features & Systems

### 3.1 Chief Exam Controller Portal (`/dashboard/exam-controller/`)
- Unified administrator dashboard to manage colleges, schools, departments, courses, faculty, and department heads.
- Dynamic user status toggling (Active / Blocked / Approved).
- Pending student registration approval workflow with simulated email notifications.
- System-wide AI Provider configuration interface (`/controller/ai-config/`).

### 3.2 Faculty & Examiner Workspace (`/dashboard/teacher/`)
- Assigned examination management with strict security controls.
- **AI Exam Routine Scanner** (`/exams/create/`):
  - Upload multi-page official exam routine documents (PDF or images).
  - Extract course codes, exam dates, times, total marks, and faculty examiners.
  - 0ms local re-matching and instant exam publishing.
- **Question Paper & Academic Rubric Builder** (`/teacher/questions-rubric/`):
  - IUBAT 23-Section taxonomy builder (Bloom's Taxonomy, CO/PO mappings, KP/CEP/CEA engineering classifications, command verbs).
  - AI Question Paper Scanner (`/api/scan-question-paper/`): Extracts questions, allocated marks, Bloom taxonomy levels, CO/PO mappings, and model answers directly into the database.
  - Live document file selection status, preview URLs, and 1-click **Remove Document** functionality.
  - Interactive exam paper preview modal for printable formatting.
- **Batch Answer Script Upload & AI Pipeline** (`/scripts/upload/`):
  - Drag-and-drop batch upload for student answer scripts (PDFs, images).
  - Automated OCR text extraction and AI evaluation against rubric criteria.
- **Split-Screen AI Grading Review Workbench** (`/evaluation/<script_id>/review/`):
  - Side-by-side view of scanned student script, extracted OCR text, rubric criteria, AI suggested score, confidence rating, and feedback.
  - Manual teacher score override and 1-click final sign-off.

### 3.3 Student Portal (`/dashboard/student/`)
- Student self-registration and login portal.
- Examination schedule view and grade breakdown.
- Recheck and re-evaluation ticket management.

---

## 4. Key Improvements & Fixes Implemented

1. **Fixed Question Paper Scanning Engine & Failover Delegation**:
   - Added `analyze_academic_exam_paper` and `analyze_question_full` delegation methods to `FailoverAIProvider`.
   - Guaranteed seamless failover to Groq (`llama-3.3-70b-versatile`) or OpenAI (`gpt-4o`) when Gemini hit daily quota limits.
2. **Fixed LaTeX JSON Parsing in Math Equations**:
   - Implemented regex LaTeX backslash repair (`re.sub(r'\\(?![/"\\bfnrtu])', r'\\\\', cleaned)`) to prevent `JSONDecodeError` on mathematical matrices (`$$\begin{bmatrix}...$$`).
3. **Fixed Multi-Page Document OCR & Noise Filtering**:
   - Integrated PyMuPDF (`fitz`) for 300 DPI page rendering and font glyph noise filtering (`node\d{6,}`).
   - Removed arbitrary character truncation (`{doc_str[:4000]}`) to support full multi-page routines and question papers.
4. **Fixed Web Frontend Request Pipeline & CSRF**:
   - Appended `csrfmiddlewaretoken` directly into `FormData` payloads.
   - Enforced strict file input selection before scanning to eliminate silent re-scanning of old database files.
   - Added step-by-step terminal console logging (`sys.stdout`) for all API scan requests.
5. **Implemented Full AnswerScript Processing Pipeline**:
   - Updated `script_upload` view to create `AnswerScript`, `AnswerSegment`, and `Evaluation` records in the database.
   - Connected `/scripts/upload/` directly to the OCR and AI Evaluation engine, routing teachers to the Grading Workbench.

---

## 5. Directory & File Structure Summary

```text
mainproject/
├── core/
│   ├── ai_engine/
│   │   ├── ocr/
│   │   │   ├── engine.py           # OCREngineManager (PyMuPDF, Tesseract, OpenCV)
│   │   │   └── preprocessor.py     # Image preprocessing & deskewing
│   │   ├── providers/
│   │   │   ├── base.py             # BaseAIProvider & LaTeX repair
│   │   │   ├── failover.py         # FailoverAIProvider multi-model chain
│   │   │   ├── gemini.py           # GeminiProvider (2.0/2.5/1.5 Flash)
│   │   │   ├── groq.py             # GroqProvider (Llama 3.3 70B)
│   │   │   ├── openai.py           # OpenAIProvider (GPT-4o)
│   │   │   └── factory.py          # AIProviderFactory
│   │   ├── routine_parser/         # RoutineParser
│   │   └── course_outline_parser/  # CourseOutlineParser
│   ├── models.py                   # Examination, Question, Rubric, AnswerScript, Segment, Evaluation
│   ├── views.py                    # Core views, API endpoints, grading workbench
│   ├── urls.py                     # URL routing map
│   └── templates/core/             # HTML5 templates (question_rubric_manage, exam_create, etc.)
└── mainproject/                    # Django project settings & configuration
```

---

## 6. Verification Status

- **Automated AI Extraction Tests**: 100% Pass (All 4 questions from sample paper extracted with marks, Bloom level, CO/PO mapping).
- **Failover Chain & Rate Limit Fallback**: 100% Pass.
- **Batch Answer Script Upload & AI Grading Workbench**: 100% Pass.
- **System Integrity Check**: `python manage.py check` — **0 issues identified**.
