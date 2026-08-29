# IntelliGrade — Requirements Traceability Matrix (RTM)

**Document Version:** 3.5.0 (Enterprise Academic Edition)  
**Last Updated:** August 29, 2026  
**Auditor:** Principal Enterprise Systems Architect  

---

## 1. Traceability Matrix Table

```text
============================================================================================================================================
REQ ID  USER NEED / USE CASE       PRIMARY DB MODELS                     CORE VIEWS / API ENDPOINTS                 CORE TEST SUITE STATUS
============================================================================================================================================
FR-01   UC-01: RBAC Auth           User, Profile                         views.landing_page, views.*_login          core/tests.py (100% Pass)
FR-02   UC-02: Student Sign-up     User, Profile                         views.student_register                     core/tests.py (100% Pass)
FR-03   UC-03: OTP Password Reset  User                                  views.forgot_password, views.verify_otp    core/tests.py (100% Pass)
FR-04   UC-04: Academic Structure  College, School, Department, Course   views.exam_controller_dashboard            core/tests.py (100% Pass)
FR-05   UC-05: Account Toggling    User, Profile                         views.toggle_user_status                   core/tests.py (100% Pass)
FR-06   UC-08: AI Routine Ingest   Examination, Course                   views.scan_routine_ai                      core/tests.py (100% Pass)
FR-07   UC-08: Routine Course MatchCourse                                views.scan_routine_ai                      core/tests.py (100% Pass)
FR-08   UC-07: AI Configuration    AIConfiguration, AIProviderHealth     views.ai_config_view                       core/tests.py (100% Pass)
FR-09   UC-09: Dept Head Metrics   Department, Course, Examination       views.dept_head_dashboard                  core/tests.py (100% Pass)
FR-10   UC-10: Dept Head Audit     CourseTabulation, StudentGradeRecord  views.course_tabulation_view               core/tests.py (100% Pass)
FR-11   UC-11: 23-Taxonomy Studio  Question                              views.question_rubric_manage               core/tests.py (100% Pass)
FR-12   UC-11: Rubric Criteria     Rubric                                views.question_rubric_manage               core/tests.py (100% Pass)
FR-13   UC-11: Figures & Tables    QuestionFigure, Table, Formula        views.question_rubric_manage               core/tests.py (100% Pass)
FR-14   UC-11: LaTeX Sanitization  QuestionFormula                       ai_engine/providers/base.py                core/tests.py (100% Pass)
FR-15   UC-13: Master Solution     Examination, Question                 views.api_upload_master_solution           core/tests.py (100% Pass)
FR-16   UC-14: 300 DPI Preprocess  SubmissionImage, SubmissionPage       views.api_upload_raw_images                core/tests.py (100% Pass)
FR-17   UC-14: Working Copy Vers.  SubmissionImage, SubmissionPage       image_processor.py                         core/tests.py (100% Pass)
FR-18   UC-15: Hybrid Multi-OCR    OCRResult, SubmissionPage             ai_engine/ocr/                             core/tests.py (100% Pass)
FR-19   UC-16: Boundary Detection  QuestionDetection                     question_number_detector.py                core/tests.py (100% Pass)
FR-20   UC-16: Mapping ConfirmationQuestionMapping, MappingHistory       views.api_confirm_question_mapping         core/tests.py (100% Pass)
FR-21   UC-17: AI Failover Chain   AIConfiguration                       ai_engine/providers/failover.py            core/tests.py (100% Pass)
FR-22   UC-17: 429 Cooldown Health ProviderHealthTracker                 ai_engine/routing/task_router.py           core/tests.py (100% Pass)
FR-23   UC-17: 45s Timeout Budget  AIConfiguration                       ai_engine/providers/failover.py            core/tests.py (100% Pass)
FR-24   UC-17: Criteria Evaluation EvaluationResult, Feedback            script_evaluator.py                        core/tests.py (100% Pass)
FR-25   UC-17: Low Conf. Flagging  StudentSubmission, EvaluationResult   script_evaluator.py                        core/tests.py (100% Pass)
FR-26   UC-18: Split-Screen View   StudentSubmission, SubmissionPage     views.evaluation_workspace                 core/tests.py (100% Pass)
FR-27   UC-19: Mark Overrides      TeacherReview, EvaluationHistory      views.review_evaluation_answer             core/tests.py (100% Pass)
FR-28   UC-20: Certified PDF Stamp SubmissionPDF                         evaluated_pdf_service.py                   core/tests.py (100% Pass)
FR-29   UC-21: OBE Tabulation      CourseTabulation, StudentGradeRecord  tabulation_service.py                      core/tests.py (100% Pass)
FR-30   UC-22: Live Web-Excel Sync StudentGradeRecord, StudentSubmission views.api_update_student_grade_record         core/tests.py (100% Pass)
FR-31   UC-23: 8-Sheet Excel ExportCourseTabulation, StudentGradeRecord  tabulation_exporter.py                     core/tests.py (100% Pass)
FR-32   UC-24: Async Email Service StudentSubmission                     email_service.py                           core/tests.py (100% Pass)
FR-33   UC-25: Student Dashboard   StudentGradeRecord, StudentSubmission views.student_dashboard                    core/tests.py (100% Pass)
============================================================================================================================================
```