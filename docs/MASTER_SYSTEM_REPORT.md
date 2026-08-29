# IntelliGrade — Master System Report & Architectural Blueprint

**Document Reference:** `DOCS-MSR-3.5.0`  
**System Name:** IntelliGrade — AI-Powered Outcome-Based Education (OBE) Academic Evaluation & Management Platform  
**Target Institutional Standard:** International University of Business Agriculture and Technology (IUBAT) & BAETE OBE Accreditation Standards  
**Release Version:** 3.5.0 (Enterprise Academic Edition)  
**Lead System Architect & Auditor:** Principal Enterprise Systems Architect & Technical Documentation Specialist  
**Audit & Release Date:** August 29, 2026  
**System Operational Status:** Verified / Operational (Django 5.2.x, Multi-Provider AI Failover, Bi-directional OBE Tabulation Sync)  

---

## 1. System Executive Blueprint & High-Level Architecture

IntelliGrade is an enterprise academic assessment and grading automation SaaS platform designed to modernize university examination lifecycles. Higher education institutions face severe bottlenecks during examination periods: faculty spend hundreds of hours deciphering handwriting, manually cross-referencing answers against multi-tiered criteria, and performing complex multi-component Course Outcome (CO) and Program Outcome (PO) weighted mathematics for accreditation compliance.

IntelliGrade resolves these bottlenecks through a **Human-in-the-Loop, AI-Augmented Evaluation Pipeline**. The system automates routine ingestion, question paper digitizing, 23-section IUBAT OBE taxonomy mapping, 300 DPI high-resolution script preprocessing, optical character recognition (OCR), question boundary segmentation, multi-provider AI evaluation, split-screen teacher verification workbenches, and real-time OBE tabulation with 8-sheet Excel workbook export.

```mermaid
graph TD
    subgraph Administrative Governance & Routine Ingestion
        A1[Chief Exam Controller] -->|Manages Structure & AI Config| B1[Academic Structure Management]
        A1 -->|Uploads Multi-page Routine PDF/Image| B2[AI Routine Parser]
        B2 -->|0ms Local Course Match| B3[Bulk Scheduled Examinations]
    end

    subgraph Question Paper & Academic Rubric Studio
        A2[Faculty / Examiner] -->|Authors / AI Scans Question Paper| C1[23-Taxonomy Question Paper Studio]
        C1 -->|Stores| C2[CO, PO, Bloom's, KP, CEP, CEA, Figures, Tables, Formulas]
        A2 -->|Uploads (Optional)| C3[Master Golden Solution Script]
    end

    subgraph Answer Script Processing & Hybrid OCR
        A2 -->|Batch Drag & Drop Upload| D1[300 DPI Preprocessing & Normalization]
        D1 -->|Versioned Working Copies in submission_working/| D2[Hybrid Multi-Engine OCR]
        D2 -->|PyMuPDF Font Map + PyTesseract + EasyOCR CPU| D3[Word & Line Bounding Boxes]
        D3 -->|Start-of-line Regex State Machine| D4[Question Number Detection & Page Mapping]
        D4 -->|Visual Crop Modal| D5[Teacher Mapping Confirmation]
    end

    subgraph AI Evaluation Core & Multi-Provider Failover
        D5 -->|TaskRouter| E1{Failover AI Orchestrator}
        E1 -->|1. Local Offline Vision| E2[Moondream2 / Ollama on CPU]
        E1 -->|2. High-Speed Cloud LLM| E3[Groq Llama-3.3 70B]
        E1 -->|3. Cloud Gateway| E4[OpenRouter API]
        E1 -->|4. Multimodal Reasoning| E5[Gemini 2.5 Flash / OpenAI GPT-4o]
        E1 -->|JSON Sanitize & LaTeX Repair| E6[Structured Evaluation Result & Confidence Score]
    end

    subgraph Split-Screen Teacher Workbench & Verification
        E6 --> F1[Split-Screen Teacher Grading Workbench]
        A2 -->|Inspects Scanned Script vs AI Score| F1
        A2 -->|Manual Score Override & Custom Feedback| F1
        F1 -->|Finalize Evaluation| F2[Certified Stamped PDF Answer Script]
    end

    subgraph Real-Time OBE Tabulation & Dissemination
        F1 -->|Live Event Sync| G1[Course OBE Tabulation Engine]
        G1 -->|Calculates CT 10% + Mid 25% + Final 50% + Assign 10% + Att 5%| G2[StudentGradeRecord Database Store]
        G2 -->|Bi-directional Sync| G3[8-Sheet OBE Excel Workbook .xlsx]
        G2 -->|Live Sync| G4[Student Dashboard & Progress Cards]
        G2 -->|Live Sync| G5[Dept Head Dashboard & Pass Rate Analytics]
        G2 -->|Asynchronous Threading SMTP| G6[Institutional Email Result Notification]
    end
```

---

## 2. End-to-End Actor User Manual & Walkthrough

### 2.1 Persona 1: Chief Exam Controller (`/dashboard/exam-controller/`)

The Chief Exam Controller possesses top-tier governance authority over university structural entities, student admissions, AI provider configurations, and exam routines.

```mermaid
journey
    title Chief Exam Controller Journey
    section Authentication & Setup
      Visit Landing Page: 5: Controller
      Login via /controller/login/: 5: Controller
      View Controller Dashboard: 5: Controller
    section Governance
      Manage Colleges & Departments: 4: Controller
      Add Courses & Assign Faculty: 4: Controller
      Approve Pending Students: 5: Controller
    section AI & Scheduling
      Configure AI API Keys (/controller/ai-config/): 4: Controller
      Upload & Scan Exam Routine PDF: 5: Controller
      Publish Scheduled Examinations: 5: Controller
```

#### Step-by-Step Workflow with Concrete Examples:
1. **Login & Role Verification**: Controller accesses `/controller/login/` with credentials (`controller` / `password123`). The system checks `Profile.Role.ADMIN` and redirects to `/dashboard/exam-controller/`.
2. **Academic Structure Setup**:
   - Controller clicks **"Add Department"** $\rightarrow$ Enters `Department of Computer Science and Engineering` (`CSE`), sets School to `School of Engineering and Technology` (`SET`), and saves.
   - Controller clicks **"Add Course"** $\rightarrow$ Enters Course Code `CSE 4383`, Title `Computer Graphics and Animation`, selects Department `CSE`, and assigns instructor `Engr. Hijbullah`.
3. **Student Admission Approval Workflow**:
   - Students registering via `/student/register/` are placed in `is_approved = False`.
   - Controller views the **Pending Students** badge $\rightarrow$ Inspects Student ID `22303142` (Name: `Hijbullah Al Mahdi`, Email: `hijbullah@dsr.iubat.ac.bd`) $\rightarrow$ Clicks **"Approve"**.
   - System updates `Profile.is_approved = True` and triggers `EmailService.send_account_creation_email()`, dispatching a welcome notification with direct login link.
4. **AI Exam Routine Scanning (`/controller/scan-routine-ai/`)**:
   - Controller uploads `Midterm_Routine_Spring_2026.pdf`.
   - The system executes PyMuPDF page rendering and invokes `RoutineParser` via the AI failover chain.
   - The AI extracts all routine rows (e.g. `Date: 2026-03-15 | Course: CSE 4383 | Time: 10:00 AM | Total Marks: 100 | Examiner: Hijbullah`).
   - The controller verifies extracted rows in the interactive preview table and clicks **"Publish Examinations"**, bulk-inserting `Examination` records.

---

### 2.2 Persona 2: Department Head (`/dashboard/dept-head/`)

The Department Head monitors department-level academic metrics, pass rates, and audits OBE course tabulations for accreditation compliance.

```mermaid
journey
    title Department Head Journey
    section Department Monitoring
      Login via /dept-head/login/: 5: Dept Head
      View Real-time Pass Rate & Active Courses: 5: Dept Head
      Track Faculty Evaluation Workload: 4: Dept Head
    section OBE Quality Audit
      Inspect Course Tabulation Reports: 5: Dept Head
      Audit Individual & Class CO/PO Attainments: 5: Dept Head
      Download Department 8-Sheet Excel Registers: 5: Dept Head
```

#### Step-by-Step Workflow with Concrete Examples:
1. **Login & Dashboard Ingestion**: Department Head logs in via `/dept-head/login/`.
2. **Live Pass Rate Analytics**:
   - Dashboard automatically queries all `CourseTabulation` and `StudentGradeRecord` instances belonging to the department.
   - Calculates the overall pass rate (percentage of students achieving $\ge 40\%$ / Grade $\text{D}$ or higher across active courses).
3. **Course Tabulation & OBE Attainment Audit**:
   - Department Head selects `CSE 4383 - Section C` $\rightarrow$ Clicks **"View Tabulation"**.
   - Inspects the live tabulation matrix: Class Test ($10\%$), Midterm ($25\%$), Final ($50\%$), Assignment ($10\%$), and Attendance ($5\%$).
   - Reviews class-wide Course Outcome attainment graphs (e.g. `CO1: 88.5% Attained`, `CO2: 74.2% Attained`, `CO3: 91.0% Attained`).
   - Clicks **"Export Tabulation (.xlsx)"** to download the official 8-sheet Excel file for internal accreditation audit records.

---

### 2.3 Persona 3: Faculty Member / Examiner (`/dashboard/teacher/`)

The Faculty Examiner is the primary operational user responsible for authoring question rubrics, uploading student scripts, conducting AI-assisted grading, and finalizing official course tabulations.

```mermaid
journey
    title Faculty Member / Examiner Journey
    section Question & Rubric Studio
      Login via /teacher/login/: 5: Teacher
      Open Question Paper Studio (/teacher/questions-rubric/): 5: Teacher
      AI Scan Question Paper & Define 23-Taxonomy: 5: Teacher
      Upload Master Golden Solution: 4: Teacher
    section Script Upload & Boundary Discovery
      Batch Upload Answer Scripts (/scripts/upload/): 5: Teacher
      Generate 300 DPI Copies & Run Hybrid OCR: 5: Teacher
      Confirm Question Mapping in Visual Modal: 4: Teacher
    section Grading & Tabulation
      Run AI Multi-Provider Evaluation: 5: Teacher
      Review on Split-Screen Workbench: 5: Teacher
      Override Marks & Finalize Evaluation: 5: Teacher
      Manage Live OBE Tabulation Table: 5: Teacher
      Download 8-Sheet Excel & Sync Student Portal: 5: Teacher
```

#### Step-by-Step Workflow with Concrete Examples:
1. **Question Paper & 23-Taxonomy Authoring (`/teacher/exam/1/questions-rubric/`)**:
   - Teacher selects `CSE 4383 - Midterm Examination`.
   - Clicks **"Scan Question Paper with AI"** and uploads `CSE4383_Midterm_Paper.pdf`.
   - The AI engine extracts:
     - `Question 1 (25 Marks)`: *"Explain matrix transformations in 2D viewing pipeline."* | Bloom: `Understand` | CO: `CO1` | PO: `PO1` | KP: `['KP1', 'KP3']`.
     - `Question 2 (25 Marks)`: *"Derive Bresenham line algorithm."* | Bloom: `Apply` | CO: `CO2` | PO: `PO2`.
     - `Question 3 (25 Marks)`: Attached Matrix Data Table $\begin{bmatrix} 50 & 56 \\ 52 & 72 \end{bmatrix}$ | Bloom: `Analyze` | CO: `CO3`.
     - `Question 4 (25 Marks)`: Numerical polygon clipping calculation | Bloom: `Apply` | CO: `CO1`.
   - System extracts rubric benchmarks, expected keywords, and criteria mark distributions.
2. **Master Solution Script Ingestion**:
   - Teacher clicks **"Upload Master Solution"** and selects `CSE4383_Master_Solution.pdf`.
   - The system extracts step-by-step benchmark solutions and links them to Questions 1–4.
3. **Batch Script Upload & Preprocessing (`/scripts/upload/`)**:
   - Teacher drags and drops 30 student answer scripts (PDFs and image sets).
   - System normalizes images, renders PDF pages at 300 DPI in `media/submission_working/`, and executes hybrid OCR (PyMuPDF $\rightarrow$ PyTesseract $\rightarrow$ EasyOCR fallback on PyTorch CPU).
4. **Interactive Question Boundary Confirmation**:
   - System detects question number headers (e.g. `Ans to Q.1`, `Question 2(a)`) via start-of-line regex state machine.
   - Teacher opens the visual mapping modal, verifies page-to-question associations, adjusts bounding crop rectangles, and clicks **"Confirm & Start AI Evaluation"**.
5. **AI Multi-Provider Evaluation**:
   - `TaskRouter` dispatches each answer to the failover orchestrator (Local Vision $\rightarrow$ Groq $\rightarrow$ OpenRouter $\rightarrow$ Gemini $\rightarrow$ OpenAI).
   - Evaluates answers against rubric criteria, awarding obtained marks, confidence ratings, and identifying specific strengths and mistakes.
6. **Split-Screen Grading Review Workbench (`/teacher/submission/1/workspace/`)**:
   - Teacher views student script on the left and AI evaluation cards on the right.
   - Teacher inspects Question 1: AI awarded `20.0 / 25.0` (Confidence: `0.92`).
   - Teacher modifies Question 2 score from `20.0` to `21.25`, adds a private note, and clicks **"Approve & Next"**.
   - Teacher clicks **"Finalize Evaluation"** $\rightarrow$ System generates a certified, watermarked PDF script.
7. **Live Course Tabulation Management (`/course/1/tabulation/`)**:
   - Teacher navigates to the Course Tabulation table.
   - For student `22303142` (`Hijbullah Al Mahdi`), teacher clicks **"Edit"**:
     - Class Test: `80.0%` ($8.0 / 10.0$)
     - Midterm: `85.0%` ($21.25 / 25.0$)
     - Final Exam: `95.0%` ($47.5 / 50.0$)
     - Assignment: `100.0%` ($10.0 / 10.0$)
     - Attendance: `5.0` ($100.0\% / 5\%$)
     - Weighted Total: `91.75%` | Letter Grade: `A+` | GPA: `4.00`
   - Teacher clicks **"Save & Sync Tabulation"**.
   - **Instant Tri-Directional Synchronization**:
     1. Database `StudentGradeRecord` and `StudentSubmission` updated.
     2. Downloadable 8-sheet Excel workbook (`HOME!AQ11`) formula updated to reflect normalized marks.
     3. Student portal instantly updates to display `91.75% / A+` and Attendance `5.0`.

---

### 2.4 Persona 4: Student (`/dashboard/student/`)

The Student portal delivers real-time grade transparency, component-level breakdowns, feedback reflections, and downloadable certified PDF scripts.

```mermaid
journey
    title Student Journey
    section Access & Dashboard
      Login via /student/login/: 5: Student
      View Overall Course Grade & GPA Cards: 5: Student
    section Tabulation & Script Transparency
      Inspect Official OBE Course Tabulation Table: 5: Student
      Review Question-by-Question Marks & Feedback: 5: Student
      Download Certified Stamped PDF Script: 5: Student
```

#### Step-by-Step Workflow with Concrete Examples:
1. **Login & Dashboard Overview**: Student `22303142` logs in via `/student/login/`.
2. **Top Performance Banner**:
   - Displays **Overall Course Grade**: `A+ (91.75%)`
   - **Cumulative GPA**: `4.00 / 4.00`
   - **Active Academic Department**: `Department of Computer Science and Engineering`
3. **Official Course OBE Tabulation Section**:
   - Displays interactive table for `CSE 4383`:
     - Class Test: `8.0` ($80.0\%$)
     - Midterm: `21.25` ($85.0\%$)
     - Final Exam: `47.5` ($95.0\%$)
     - Assignment: `10.0` ($100.0\%$)
     - Attendance: `5.0` ($100.0\%$)
     - Total: `91.75%` (Grade: `A+`)
     - Outcome Attainments: `CO1: 10.0 | PO1: 10.0`
4. **Answer Script Detailed Breakdown & Certified PDF Download**:
   - Student clicks on `Midterm Examination - CSE 4383`.
   - Views question-wise feedback:
     - Question 1: `20.0 / 25.0` — *"Excellent explanation of transformation matrices; minor syntax error in translation homogeneous vector."*
     - Question 2: `21.25 / 25.0` — *"Accurate derivation of midpoint decision parameter."*
   - Clicks **"Download Evaluated PDF Script"** $\rightarrow$ Downloads official watermarked PDF with institutional header, signature stamp, and criteria marks.

---

## 3. Database Schema & Data Relationship Specification

```mermaid
erDiagram
    College ||--o{ School : "has"
    School ||--o{ Department : "has"
    Department ||--o{ Course : "offers"
    Course ||--o{ Examination : "schedules"
    Course ||--o{ CourseTabulation : "tabulates"
    CourseTabulation ||--o{ StudentGradeRecord : "contains"
    Examination ||--o{ Question : "contains"
    Question ||--|| Rubric : "defines"
    Question ||--o{ QuestionFigure : "attaches"
    Question ||--o{ QuestionTable : "attaches"
    Question ||--o{ QuestionFormula : "attaches"
    Examination ||--o{ StudentSubmission : "evaluates"
    StudentSubmission ||--o{ SubmissionPage : "has"
    StudentSubmission ||--o{ SubmissionImage : "stores"
    StudentSubmission ||--o{ SubmissionAnswer : "segments"
    SubmissionAnswer ||--|| EvaluationResult : "scores"
    EvaluationResult ||--o{ EvaluationFeedback : "details"
    EvaluationResult ||--o{ TeacherReview : "logs"
    EvaluationResult ||--o{ EvaluationHistory : "records"
    StudentSubmission ||--|| SubmissionPDF : "compiles"
```

### Complete Database Models Catalog:

```text
====================================================================================================
MODEL NAME             PRIMARY FIELDS & TYPES                             RELATIONSHIPS & PURPOSE
====================================================================================================
Profile                user (OneToOne User), role (Enum),                 Extends Django auth User with
                       department (FK Dept), phone_number, is_approved    RBAC roles and approval flags
College                name, code, description, created_at                Top-level university college entity
School                 name, code, college (FK), created_at               Academic school (e.g. SET, SOB)
Department             name, code, school (FK), is_active                 Department offering degree programs
Course                 code (Unique), title, department (FK), instructors Academic course entity
Examination            course (FK), title, exam_date, total_marks,        Scheduled examination instance with
                       status, question_paper_file, master_solution_file  uploaded question & master files
Question               examination (FK), question_number, prompt_text,    23-taxonomy OBE question model
                       max_marks, bloom_level, co_mapping, po_mapping     with figures, tables, LaTeX tags
Rubric                 question (OneToOne), criteria, ideal_answer,       Grading criteria, keywords, common
                       mark_distribution (JSON), common_mistakes (JSON)   mistakes, and deduction levels
QuestionFigure         question (FK), page_number, image, bounding_box    Diagrams attached to exam questions
QuestionTable          question (FK), cell_json, rows, cols, bounding_box Tabular data / matrix attachments
QuestionFormula        question (FK), raw_latex, is_matrix, bounding_box  LaTeX equations with syntax repair
StudentSubmission      examination (FK), student (FK User), student_name, Student answer script instance with
                       student_roll_no, status, total_obtained_marks      total scores and finalization lock
SubmissionPage         submission (FK), page_number, page_image,          Individual rasterized script page
                       working_image_path, version, ocr_raw_text          with working copy version tracking
SubmissionImage        submission (FK), original_file, processed_file,    Raw uploaded image assets with
                       working_image_path, version, sequence_order        rotation angles and delete flags
OCRResult              submission_page (FK), engine_name, page_confidence Multi-engine OCR extraction with
                       word_boxes_json (JSON), line_boxes_json (JSON)     word/line coordinate bounding boxes
QuestionDetection      submission_page (FK), question_number_raw,         Start-of-line regex detected question
                       question_number_normalized, bbox_json, confidence  headers with detection method
QuestionMapping        submission (FK), question (FK), page_numbers_json, Association pairing questions to
                       regions_json, mapping_status, is_confirmed         script pages and crop boundaries
EvaluationResult       submission_answer (OneToOne), obtained_marks,      AI/Teacher score record with confidence
                       maximum_marks, strengths_json, mistakes_json       rating and mandatory review flags
EvaluationFeedback     evaluation_result (FK), criteria_name,             Detailed criterion-level score
                       allocated_marks, awarded_marks, comments           breakdown and deduction notes
TeacherReview          evaluation_result (FK), teacher (FK), action,      Immutable teacher score override audit
                       previous_marks, new_marks, review_comments         log with timestamps
CourseTabulation       course (FK), semester, section, weightage_config   Course-wide OBE grade register
StudentGradeRecord     tabulation (FK), student_id, student_name,         Individual student OBE grade record
                       exam_scores (JSON), co_scores, po_scores,          with CT, Mid, Final, Assignment,
                       attendance_marks (5%), overall_score, letter_grade Attendance, and manual edit lock
SubmissionPDF          submission (OneToOne), pdf_file, page_count        Final compiled & certified PDF script
====================================================================================================
```

---

## 4. Complete System API Catalog

```text
====================================================================================================================================
HTTP METHOD & URL PATH                         VIEW FUNCTION                      AUTH REQUIRED       DESCRIPTION & PAYLOAD
====================================================================================================================================
GET  /                                         views.landing_page                 Public              Institutional Landing Page
GET  /controller/login/                        views.exam_controller_login        Public              Chief Exam Controller Login
GET  /dept-head/login/                         views.dept_head_login              Public              Department Head Login
GET  /teacher/login/                           views.teacher_login                Public              Faculty / Examiner Login
GET  /student/login/                           views.student_login                Public              Student Portal Login
POST /student/register/                        views.student_register             Public              Student Self-Registration
GET  /logout/                                  views.logout_view                  Authenticated       Session Logout & Destroy
GET  /dashboard/exam-controller/               views.exam_controller_dashboard    ADMIN               Controller Governance Dashboard
POST /controller/add-department/               views.add_structure                ADMIN               Create College/School/Department
POST /controller/approve-student/<id>/         views.approve_student              ADMIN               Approve student admission
POST /controller/scan-routine-ai/              views.scan_routine_ai              ADMIN               AI Routine Scanner (PDF upload)
GET  /controller/ai-config/                    views.ai_config_view               ADMIN               Configure AI Provider Keys
GET  /dashboard/dept-head/                     views.dept_head_dashboard          DEPT_HEAD           Department Head Dashboard
GET  /dashboard/teacher/                       views.teacher_dashboard            TEACHER             Faculty Workspace Dashboard
GET  /dashboard/student/                       views.student_dashboard            STUDENT             Student Real-Time Grade Portal
GET  /teacher/questions-rubric/                views.question_rubric_manage       TEACHER             23-Taxonomy Rubric Studio
POST /api/scan-question-paper/                 views.api_scan_question_paper      TEACHER             AI Question Paper Scanner
POST /api/exam/<id>/upload-master-solution/    views.api_upload_master_solution   TEACHER             Upload Master Benchmark Solution
POST /api/exam/<id>/upload-raw-images/         views.api_upload_raw_images        TEACHER             Batch Upload Student Scripts
POST /api/submission/<id>/analyze-mapping/     views.api_analyze_question_mapping TEACHER             Auto-Detect Question Boundaries
POST /api/submission/<id>/confirm-mapping/     views.api_confirm_question_mapping TEACHER             Confirm Page & BBox Mapping
POST /api/submission/<id>/run-evaluation-v3/   views.api_run_evaluation_v3        TEACHER             Trigger Multi-Provider AI Eval
GET  /teacher/submission/<id>/workspace/       views.evaluation_workspace         TEACHER             Split-Screen Grading Workbench
POST /api/evaluation-result/<id>/review/       views.review_evaluation_answer     TEACHER             Teacher Score Override / Approve
POST /api/submission/<id>/finalize/            views.api_finalize_evaluation      TEACHER             Finalize & Stamp Certified PDF
GET  /api/submission/<id>/download-evaluated-pdf/ views.api_download_evaluated_pdf Authenticated     Download Certified Watermarked PDF
GET  /course/<id>/tabulation/                  views.course_tabulation_view       TEACHER / HEAD      OBE Course Tabulation Table
POST /api/tabulation/grade-record/<id>/update/ views.api_update_student_grade_record TEACHER          Live Tabulation Edit & Sync
GET  /course/<id>/export-tabulation/           views.export_course_tabulation     TEACHER / HEAD      Export 8-Sheet OBE Excel (.xlsx)
POST /course/<id>/email-tabulation/            views.email_course_tabulation_report TEACHER           Email OBE Summary Spreadsheet
POST /api/auth/forgot-password/                views.api_forgot_password          Public              Dispatch 6-digit OTP Email
POST /api/auth/verify-reset-otp/               views.api_verify_reset_otp         Public              Verify OTP & Reset Password
====================================================================================================================================
```
