# IntelliGrade — Functional Requirements Specification (FRS)

**Document Version:** 3.5.0 (Enterprise Academic Edition)  
**Last Updated:** August 29, 2026  
**Auditor:** Principal Enterprise Systems Architect  

---

## 1. Functional Requirements Catalog

```text
====================================================================================================
REQ ID    MODULE / AREA               REQUIREMENT STATEMENT & BEHAVIORAL SPECIFICATION
====================================================================================================
FR-01     Authentication              The system SHALL support unified role-based authentication redirecting
                                      users to their respective dashboards based on Profile.role.
FR-02     Authentication              The system SHALL support student self-registration with default is_approved=False
                                      requiring Exam Controller approval before portal access.
FR-03     Authentication              The system SHALL support 6-digit OTP password reset via background SMTP email
                                      with a 10-minute expiry window.
FR-04     Controller Governance       The system SHALL allow Exam Controllers to manage Colleges, Schools,
                                      Departments, Courses, Faculty, and Department Heads.
FR-05     Controller Governance       The system SHALL allow Exam Controllers to toggle active/blocked status
                                      for any institutional user account.
FR-06     AI Routine Parsing          The system SHALL parse multi-page examination routine schedules (PDF/Images)
                                      and extract exam dates, times, course codes, titles, and assigned examiners.
FR-07     AI Routine Parsing          The system SHALL perform 0ms local DB lookups to match extracted course codes
                                      and provide 1-click batch examination creation.
FR-08     AI Config Management       The system SHALL allow administrators to configure API keys for Gemini, Groq,
                                      OpenAI, OpenRouter, and Ollama, and set OCR confidence thresholds.
FR-09     Dept Head Monitoring        The system SHALL display live departmental pass rates, active course counts,
                                      enrolled students, and assigned faculty workloads on /dashboard/dept-head/.
FR-10     Dept Head Audit             The system SHALL allow Department Heads to audit course OBE tabulation sheets
                                      and review Course Outcome and Program Outcome attainment matrices.
FR-11     23-Taxonomy Authoring       The system SHALL store 23-section IUBAT OBE metadata per Question: prompt,
                                      max marks, Bloom's level, CO (CO1-CO5), PO (PO1-PO12), KP, CEP, and CEA tags.
FR-12     Rubric Management           The system SHALL store structured Rubrics with criteria, ideal answer, mark
                                      distribution, rubric levels, keywords, and common mistakes.
FR-13     Visual Asset Extraction     The system SHALL extract and store bounding box coordinates for attached
                                      Question Figures, Tables, and LaTeX mathematical formulas.
FR-14     LaTeX Formula Repair        The system SHALL sanitize unescaped backslashes in mathematical matrices
                                      to prevent JSON decode errors during AI prompt compilation.
FR-15     Master Solution Service     The system SHALL allow teachers to upload master solution scripts and
                                      automatically link solution steps to corresponding questions.
FR-16     Script Preprocessing        The system SHALL render uploaded PDF answer scripts at 300 DPI high resolution
                                      and apply OpenCV deskewing, noise reduction, and thresholding.
FR-17     Working Copy Versioning     The system SHALL generate versioned working copies in submission_working/
                                      incrementing version numbers upon rotation, cropping, or contrast edits.
FR-18     Hybrid Multi-Engine OCR     The system SHALL execute PyMuPDF font extraction -> PyTesseract -> EasyOCR
                                      (PyTorch CPU fallback) to extract text with line/word bounding boxes.
FR-19     Question Boundary Detection The system SHALL detect question header patterns (e.g. 'Question 1', 'Ans to Q.1')
                                      using a strict start-of-line regex state machine.
FR-20     Interactive Mapping Modal   The system SHALL present an interactive visual mapping tool allowing teachers
                                      to adjust answer page numbers and bounding box crop regions before AI eval.
FR-21     AI Failover Orchestration   The system SHALL route evaluation requests through a prioritized failover chain:
                                      Local Vision -> Groq -> OpenRouter -> Gemini -> OpenAI.
FR-22     429 Rate Limit Cooldown     The system SHALL track HTTP 429 events and place affected AI providers on
                                      exponential backoff cooldowns without dropping pending evaluations.
FR-23     Timeout Budget Enforcement  The system SHALL enforce a 45-second timeout per AI evaluation request,
                                      failing over instantly to the next provider upon timeout.
FR-24     Criteria-Based Scoring      The system SHALL evaluate student answers against rubric criteria and return
                                      obtained marks, maximum marks, confidence ratings, strengths, and mistakes.
FR-25     Mandatory Review Flagging   The system SHALL automatically set requires_manual_review=True for any answer
                                      scoring below the system-configured confidence threshold (default 0.75).
FR-26     Split-Screen Workbench      The system SHALL render a split-screen workbench displaying the original scanned
                                      script on the left and AI scores, criteria, and feedback on the right.
FR-27     Teacher Mark Override       The system SHALL allow teachers to override AI marks and edit feedback, logging
                                      every adjustment in TeacherReview and EvaluationHistory audit tables.
FR-28     Certified PDF Generation    The system SHALL stamp finalized submissions with institutional headers,
                                      awarded marks, teacher comments, and digital watermarks.
FR-29     OBE Course Tabulation       The system SHALL aggregate assessment components: Class Test (10%), Midterm (25%),
                                      Final Exam (50%), Assignment (10%), Attendance (5%).
FR-30     Real-Time Tabulation Sync   The system SHALL synchronize teacher edits made in the tabulation modal
                                      instantly to StudentGradeRecord, StudentSubmission, Excel, and Student Dashboard.
FR-31     8-Sheet Excel Export        The system SHALL generate official 8-sheet Excel workbooks (openpyxl) containing
                                      HOME, ASSIGNMENT, CO_ATTAINMENT, PO_ATTAINMENT, and CQI formulas.
FR-32     Institutional Email Service The system SHALL dispatch non-blocking background emails via SMTP from
                                      intelligrade@dsr.iubat.ac.bd for results, credentials, and OTPs.
FR-33     Student Dashboard           The system SHALL display real-time course grades, cumulative GPA (4.00 scale),
                                      question-wise score feedback, and certified PDF download links.
====================================================================================================
```
