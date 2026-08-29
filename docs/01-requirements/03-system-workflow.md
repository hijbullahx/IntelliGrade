# IntelliGrade — End-to-End System Workflows & State Machines

**Document Version:** 3.5.0 (Enterprise Academic Edition)  
**Last Updated:** August 29, 2026  
**Auditor:** Principal Enterprise Systems Architect  

---

## 1. High-Level University Examination Lifecycle Workflow

```mermaid
sequenceDiagram
    autonumber
    actor C as Chief Exam Controller
    actor T as Faculty Member / Examiner
    actor S as Student
    participant Sys as IntelliGrade Core System
    participant OCR as OCR & Boundary Engine
    participant AI as Multi-Provider AI Failover
    participant Tab as OBE Tabulation Engine

    Note over C,Sys: Stage 1: Academic Structure & Routine Setup
    C->>Sys: Manage Colleges, Schools, Departments, Courses & Faculty
    C->>Sys: Upload Examination Routine PDF/Image
    Sys->>AI: Parse Routine Schedule & Detect Courses
    AI-->>Sys: Return Structured Exam Schedule
    Sys-->>C: Display Batch Scheduled Exams & Publish

    Note over T,Sys: Stage 2: Question Paper & Rubric Studio
    T->>Sys: Open Question Paper Studio (/teacher/questions-rubric/)
    T->>Sys: Upload Official Question Paper & Syllabus Outline
    Sys->>AI: Extract 23-Taxonomy Metadata (CO/PO, Bloom's, Tables, Formulas)
    AI-->>Sys: Return Questions & Criterion Rubrics
    T->>Sys: (Optional) Upload Master Benchmark Solution Script
    T->>Sys: Verify & Save Golden Exam Configuration

    Note over S,T: Stage 3: Examination Conduct
    S->>T: Students complete handwritten examination scripts

    Note over T,OCR: Stage 4: Script Ingestion, 300 DPI Preprocess & OCR
    T->>Sys: Batch Upload Student Answer Scripts (PDF / Images)
    Sys->>OCR: Preprocess Images, Deskew & Render at 300 DPI
    OCR->>OCR: Run Hybrid OCR (PyMuPDF -> PyTesseract -> EasyOCR)
    OCR->>OCR: Detect Question Numbers & Segment Boundaries
    OCR-->>Sys: Generated Mapped Question Regions
    Sys-->>T: Present Interactive Visual Mapping Modal for Verification

    Note over T,AI: Stage 5: Multi-Provider AI Script Evaluation
    T->>Sys: Confirm Mapping & Start Evaluation
    Sys->>AI: Evaluate Mapped Answers against Rubric Criteria (Failover: Local -> Groq -> Gemini -> OpenAI)
    AI-->>Sys: Return Scores, Strengths, Mistakes & Missing Points
    Sys->>Sys: Flag Low Confidence Submissions for Mandatory Review

    Note over T,Sys: Stage 6: Teacher Grading Review & Certification
    T->>Sys: Open Split-Screen Grading Workbench
    T->>Sys: Verify Scores, Override Marks, Edit Comments & Click 'Finalize'
    Sys->>Sys: Stamp & Generate Certified Evaluated PDF Script

    Note over Tab,S: Stage 7: Real-Time Tabulation, Excel Export & Results
    Sys->>Tab: Sync Evaluation Marks to StudentGradeRecord
    Tab->>Tab: Calculate CT (10%) + Mid (25%) + Final (50%) + Assign (10%) + Att (5%)
    Tab->>Tab: Calculate Individual & Class CO/PO Attainments
    Tab->>Sys: Generate 8-Sheet OBE Excel Workbook (.xlsx)
    Sys->>S: Dispatch Institutional Result Email with PDF Attachment
    S->>Sys: View Live Tabulation Breakdown & Download Stamped Script (/dashboard/student/)
```

---

## 2. Granular State Machine Specifications

### 2.1 StudentSubmission Lifecycle State Machine

```mermaid
stateDiagram-v2
    [*] --> UPLOADED: Script PDF/Images Uploaded
    UPLOADED --> PREVIEW_READY: Thumbnail & Metadata Generated
    PREVIEW_READY --> WORKING_COPY_CREATED: 300 DPI Normalization in submission_working/
    WORKING_COPY_CREATED --> PDF_GENERATED: Unified Preview PDF Compiled
    PDF_GENERATED --> OCR_COMPLETE: PyTesseract / EasyOCR Text Extracted
    OCR_COMPLETE --> SEGMENTED: Answer Boundaries Detected
    SEGMENTED --> MAPPING_COMPLETE: Auto-Mapping Generated
    MAPPING_COMPLETE --> WAITING_TEACHER_CONFIRMATION: Ambiguous Mappings Detected
    WAITING_TEACHER_CONFIRMATION --> AI_EVALUATED: Teacher Confirms Mapping / Starts AI Eval
    MAPPING_COMPLETE --> AI_EVALUATED: High-Confidence Auto Match Proceeded
    AI_EVALUATED --> UNDER_REVIEW: Teacher Opens Split-Screen Workbench
    UNDER_REVIEW --> REVIEWED: Teacher Modifies / Approves Question Marks
    REVIEWED --> FINALIZED: Teacher Clicks 'Finalize Evaluation'
    FINALIZED --> ARCHIVED: Temp Files Cleaned, Certified PDF Stamped
    AI_EVALUATED --> FAILED: Provider Timeout / All Chains Exhausted
    FAILED --> AI_EVALUATED: Retry / Fallback Triggered
```

### 2.2 Question Mapping State Machine
- **AUTO_HIGH**: Full regex match found at line beginning (e.g. `Question 1: Explain...`, `Ans to Q.1`), confidence $\ge 85\%$.
- **AMBIGUOUS**: Substring match or overlapping page boundaries detected, confidence $< 85\%$. Triggers teacher confirmation modal before AI grading.
- **MANUAL_OVERRIDE**: Teacher visually modifies bounding boxes or page numbers via the interactive crop tool.

### 2.3 EvaluationResult Review State Machine
- **PENDING**: AI evaluation completed, awaiting instructor inspection.
- **APPROVED**: Instructor verified and accepted AI-awarded scores without alteration.
- **OVERRIDDEN**: Instructor adjusted numerical marks or modified criteria feedback. Logs entry in `TeacherReview` and `EvaluationHistory`.
- **REJECTED**: Instructor marked evaluation invalid and requested targeted AI re-evaluation.

---

## 3. Real-Time OBE Tabulation Synchronization Flow

```mermaid
graph TD
    A[Teacher Edits Grade in Tabulation Modal] -->|AJAX POST /api/tabulation/grade-record/id/update/| B[views.api_update_student_grade_record]
    B --> C[Validate & Parse Float Scores with Attendance 5%]
    C --> D[Update StudentGradeRecord DB Model & Set is_manually_edited=True]
    D --> E[Sync Matching StudentSubmission.total_obtained_marks & status]
    D --> F[Recompute Weighted Overall Percentage & Letter Grade]
    D --> G[Generate 8-Sheet Excel Workbook with openpyxl]
    G --> H[Export Downloadable .xlsx File]
    D --> I[Student Dashboard /dashboard/student/ Instantly Displays 91.75% / A+]
    D --> J[Dept Head Dashboard /dashboard/dept-head/ Updates Pass Rate]
```