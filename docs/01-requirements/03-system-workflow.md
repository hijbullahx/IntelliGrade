# IntelliGrade — End-to-End System Workflow & State Machine

**Document Version:** 4.0.0 (Enterprise Academic Release)  
**Last Updated:** August 30, 2026  
**Auditor:** Principal Enterprise Systems Architect  

---

## 1. Global End-to-End Process Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Chief Exam Controller
    actor Teacher as Faculty / Examiner
    actor Student as Student
    participant System as IntelliGrade Core & Router
    participant OCR as Vision & OCR Pipeline
    participant AI as Multi-Provider AI Engine
    participant Tab as OBE Tabulation Engine

    %% Phase 1: Governance & Routine
    Admin->>System: Upload University Exam Routine (PDF/Image)
    System->>OCR: Ingest & Parse Routine Table
    OCR-->>System: Extracted Exam Dates, Times, Courses, Rooms
    System->>Admin: Provision Scheduled Examinations
    System->>Teacher: Email Notification: Course & Exam Assigned

    %% Phase 2: Question & Rubric Studio
    Teacher->>System: Author/Scan Question Paper with 23-Section OBE Taxonomy
    Teacher->>System: Upload Master Benchmark Solution (Optional)
    System->>OCR: Extract Figures, Tables, LaTeX Formulas, Model Steps
    System->>Teacher: Confirmed Question Paper & Rubric Configuration

    %% Phase 3: Script Ingestion & Boundary Mapping
    alt Mode: AI Evaluation Wizard (v3.0)
        Teacher->>System: Batch Upload Student Answer Scripts (PDF/Images/ZIP)
        System->>OCR: Render 300 DPI Images + Hybrid OCR (Tesseract / EasyOCR)
        OCR-->>System: Word/Line Coordinates & Raw Text
        System->>System: State-Machine Heading Detection & Page Mapping
        System->>Teacher: Interactive Mapping Review Matrix
        Teacher->>System: Confirm Question-to-Page Mappings
        
        %% Phase 4: AI Evaluation
        System->>AI: TaskRouter Dispatch (Moondream/Groq/OpenRouter/Gemini)
        AI-->>System: Structured JSON Score, Feedback, Strengths, Mistakes
        System->>System: Transition State: AI_EVALUATED
    else Mode: Manual Grading Wizard
        Teacher->>System: Upload Script PDF (Fast Page Slicing)
        System->>System: Split Pages into 300 DPI Images (Zero AI/OCR)
        Teacher->>System: Direct Manual Question-to-Page Selection
        System->>System: Launch Direct Manual Grading Workbench
    end

    %% Phase 5: Teacher Review & Finalization
    Teacher->>System: Open Split-Screen Evaluation Workspace
    Teacher->>System: Verify Answer Crops, Rubric Criteria, Adjust Marks
    Teacher->>System: Click 'Finalize Evaluation'
    System->>System: Generate Certified PDF with Security Watermark
    System->>System: Purge Obsolete Temporary Working Images
    System->>Tab: Sync Marks to StudentGradeRecord (OBE Attainments)
    System->>Student: Email Notification: Graded Result Published (with PDF)

    %% Phase 6: OBE Tabulation & Dissemination
    Teacher->>Tab: Review Course Tabulation (CT 10%, Mid 25%, Final 50%, Assign 10%, Att 5%)
    Tab->>Teacher: Export Official 8-Sheet OBE Excel Workbook
    Student->>System: Login to Student Portal -> View Transparency Breakdown & Download PDF
```

---

## 2. Detailed State-Machine Lifecycle of `StudentSubmission`

The `StudentSubmission` entity progresses through a strictly validated state machine managed by `core/ai_engine/services/workflow.py`:

```mermaid
stateDiagram-v2
    [*] --> UPLOADED: Script Ingested (PDF / Image / ZIP)
    UPLOADED --> PREVIEW_READY: 300 DPI Working Copies Generated
    PREVIEW_READY --> WORKING_COPY_CREATED: Rotation & Ordering Applied
    WORKING_COPY_CREATED --> PDF_GENERATED: Clean Script PDF Compiled
    PDF_GENERATED --> OCR_COMPLETE: Hybrid Text & Word BBoxes Extracted
    OCR_COMPLETE --> SEGMENTED: Answer Regions Isolated
    SEGMENTED --> MAPPING_COMPLETE: Question Numbers Mapped to Pages
    MAPPING_COMPLETE --> WAITING_TEACHER_CONFIRMATION: Low-Confidence / Multi-Question Conflict
    WAITING_TEACHER_CONFIRMATION --> MAPPING_COMPLETE: Teacher Confirms Mapping
    MAPPING_COMPLETE --> AI_EVALUATED: Multi-Provider AI Scoring Complete
    AI_EVALUATED --> UNDER_REVIEW: Teacher Opens Evaluation Workspace
    UNDER_REVIEW --> REVIEWED: Teacher Adjusts / Approves Marks
    REVIEWED --> FINALIZED: Final Evaluated PDF Certified & Locked
    FINALIZED --> ARCHIVED: Course Closed & Tabulation Exported
    
    UPLOADED --> FAILED: Ingestion Error / Corrupt File
    OCR_COMPLETE --> FAILED: Unreadable Script
    AI_EVALUATED --> FAILED: Provider Timeout / All Fallbacks Exhausted
```

### State Definitions & Trigger Events:

1. **`UPLOADED`**: Script file received via API (`upload_student_submission`, `api_upload_raw_images`, `api_wizard_upload_pdf`).
2. **`PREVIEW_READY`**: Pages rendered to 300 DPI high-resolution working copies in `media/submission_working/`.
3. **`WORKING_COPY_CREATED`**: Page orientation angles (0°, 90°, 180°, 270°) and sequence orders normalized.
4. **`PDF_GENERATED`**: Clean composite answer script PDF generated in `media/submission_preview/`.
5. **`OCR_COMPLETE`**: Text extracted via PyMuPDF font parser, PyTesseract, or EasyOCR deep learning backend.
6. **`SEGMENTED`**: Visual bounding box coordinates (`[ymin, xmin, ymax, xmax]`) generated for distinct answer regions.
7. **`MAPPING_COMPLETE`**: Each exam question mapped to corresponding answer pages.
8. **`WAITING_TEACHER_CONFIRMATION`**: Flagged if question headers are missing, duplicated, or below 75% confidence.
9. **`AI_EVALUATED`**: Multi-provider AI completes partial-credit scoring, feedback generation, and rubric matching.
10. **`UNDER_REVIEW`**: Teacher actively inspecting script in split-screen Evaluation Workspace.
11. **`REVIEWED`**: Teacher completes manual score overrides and saves verified criteria marks.
12. **`FINALIZED`**: Final watermarked PDF generated in `media/submission_final/`, temporary working drafts purged, and marks synced to OBE Course Tabulation.
13. **`ARCHIVED`**: Grade records locked and exported for accreditation audits.
14. **`FAILED`**: Error state with detailed diagnostics recorded in `EvaluationAuditLog`.
