# IntelliGrade — Comprehensive Requirement Analysis

**Document Version:** 3.5.0 (Enterprise Academic Edition)  
**Last Updated:** August 29, 2026  
**Auditor:** Principal Enterprise Systems Architect  

---

## 1. Domain Modeling & Stakeholder Needs Analysis

IntelliGrade addresses the complex institutional domain of university examination management and Outcome-Based Education (OBE) accreditation.

```mermaid
classDiagram
    class College {
        +String name
        +String code
    }
    class Department {
        +String name
        +String code
        +Boolean is_active
    }
    class Course {
        +String code
        +String title
    }
    class Examination {
        +String title
        +Date exam_date
        +Decimal total_marks
        +Status status
    }
    class Question {
        +String question_number
        +String prompt_text
        +Decimal max_marks
        +String bloom_level
        +String co_mapping
        +List po_mapping
        +List kp_mapping
    }
    class Rubric {
        +String criteria
        +String ideal_answer
        +JSON mark_distribution
        +JSON common_mistakes
    }
    class StudentSubmission {
        +String student_name
        +String student_roll_no
        +Decimal total_obtained_marks
        +Float percentage
        +Status status
    }
    class CourseTabulation {
        +String semester
        +String section
        +JSON weightage_config
    }
    class StudentGradeRecord {
        +String student_id
        +String student_name
        +Float attendance_marks
        +Float overall_score
        +String letter_grade
        +Boolean is_manually_edited
    }

    College "1" --> "*" Department
    Department "1" --> "*" Course
    Course "1" --> "*" Examination
    Course "1" --> "*" CourseTabulation
    CourseTabulation "1" --> "*" StudentGradeRecord
    Examination "1" --> "*" Question
    Examination "1" --> "*" StudentSubmission
    Question "1" --> "1" Rubric
```

---

## 2. Stakeholder Need vs. System Capability Mapping

| Stakeholder Role | Core Academic Need | Architectural Capability Delivered |
| :--- | :--- | :--- |
| **Chief Exam Controller** | Centralized governance of university academic hierarchy and semester exam schedules. | Administrative CRUD portal with multi-page AI exam routine parser and 0ms local course matcher. |
| **Department Head** | Real-time visibility into department-level pass rates, teacher grading progress, and accreditation compliance. | Dedicated Department Head dashboard with live pass rate analytics, course tabulation review, and faculty oversight. |
| **Faculty / Examiner** | Rapid, consistent script evaluation without manual calculation errors; full control over final marks. | Split-screen grading workbench with AI suggestions, criterion scoring, manual override, and 8-sheet OBE Excel export. |
| **Student** | Transparent, timely evaluation feedback; detailed breakdown of mistakes; certified scripts for review. | Self-service student portal with real-time grade cards, question-by-question feedback, and certified watermarked PDF downloads. |

---

## 3. High-Priority Functional Requirement Clusters

1. **Academic Governance & Security**: Multi-tier institutional hierarchy with strict RBAC decorators, Argon2 password hashing, and session management.
2. **AI Multimodal Ingestion**: High-resolution 300 DPI PDF rendering, hybrid OCR (PyMuPDF $\rightarrow$ PyTesseract $\rightarrow$ EasyOCR on PyTorch CPU), and LaTeX formula sanitation.
3. **OBE Taxonomy & Accreditation**: Complete 23-section IUBAT metadata (CO1–CO5, PO1–PO12, Bloom's levels, KP/CEP/CEA engineering tags).
4. **Resilient AI Evaluation Pipeline**: Multi-provider failover orchestrator with TaskRouter, 429 rate limit cooldown registries, and JSON schema repair.
5. **Human-in-the-Loop Verification**: Split-screen grading workbench with immutable audit logging (`TeacherReview`, `EvaluationHistory`, `EvaluationAuditLog`).
6. **Real-Time Bi-Directional OBE Tabulation**: Dynamic calculation of Class Test (10%), Midterm (25%), Final Exam (50%), Assignment (10%), and Attendance (5%), synchronized in real-time between Web UI, Database, Excel, and Student Portals.
