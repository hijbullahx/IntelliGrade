# IntelliGrade - Academic Business Rules & Evaluation Policy

**Document Version:** 3.5.0 (Enterprise Academic Edition)  
**Last Updated:** August 30, 2026  
**Auditor:** Principal Enterprise Systems Architect  

---

## 1. Academic Grading & Assessment Business Rules

### BR-01: University Assessment Weightage Distribution
The standard overall course assessment total is calculated out of 100% with the following mandatory component weightages (configurable per course in `CourseTabulation.weightage_config`):

$$\text{Overall Total} = (\text{CT} \times 0.10) + (\text{Midterm} \times 0.25) + (\text{Final} \times 0.50) + (\text{Assignment} \times 0.10) + \text{Attendance (5%)}$$

| Assessment Component | Standard Weightage (%) | Maximum Marks Base |
| :--- | :--- | :--- |
| **Class Test (CT)** | 10.0% | Normalized to 100 base |
| **Midterm Examination** | 25.0% | Normalized to 100 base |
| **Final Examination** | 50.0% | Normalized to 100 base |
| **Assignments & Quizzes** | 10.0% | Normalized to 100 base |
| **Class Attendance** | 5.0% | Direct marks (0.0 to 5.0) |
| **Total Course Score** | **100.0%** | **100.0** |

---

### BR-02: IUBAT Academic Letter Grade & GPA Conversion Scale

$$\text{Overall Percentage } (P) \longrightarrow \text{Letter Grade \& Grade Point Average (GPA)}$$

```text
====================================================================================================
PERCENTAGE RANGE (%)          LETTER GRADE     GPA POINT (4.00 SCALE)    ACADEMIC STANDING
====================================================================================================
80.0% - 100.0%               A+               4.00                      Outstanding / Excellent
75.0% - 79.9%                A                3.75                      Very Good
70.0% - 74.9%                A-               3.50                      Good
65.0% - 69.9%                B+               3.25                      Above Average
60.0% - 64.9%                B                3.00                      Average
55.0% - 59.9%                B-               2.75                      Below Average
50.0% - 54.9%                C+               2.50                      Pass
45.0% - 49.9%                C                2.25                      Marginal Pass
40.0% - 44.9%                D                2.00                      Poor Pass
Below 40.0%                  F                0.00                      Fail
====================================================================================================
```

---

### BR-03: Outcome-Based Education (OBE) Attainment Rules
1. **Course Outcome (CO) Calculation**:
   - Each examination question is mapped to a specific Course Outcome (e.g. `CO1`, `CO2`).
   - Student CO attainment is the percentage of obtained marks relative to the maximum marks allocated to that CO across all assessments.
2. **Program Outcome (PO) Calculation**:
   - Course Outcomes are mapped to Program Outcomes (e.g. `PO1` to `PO12`).
   - PO attainment is calculated via the weighted contribution of constituent CO scores.
3. **Class OBE Attainment Threshold**:
   - Standard institutional benchmark: A Course Outcome is considered **"Attained by the Class"** if >= 50% of enrolled students score >= 50% on that specific CO.

---

### BR-04: Human-in-the-Loop & Evaluation Authority Rules
1. **Zero Unsupervised Auto-Publishing**: AI evaluation results remain in `AI_EVALUATED` or `UNDER_REVIEW` status until a faculty examiner reviews and clicks **"Finalize Evaluation"**.
2. **Mandatory Manual Review Threshold**: If an evaluation confidence rating falls below 0.75 (75%), the submission is flagged with `requires_manual_review = True`, and the teacher is prompted with an explicit visual warning banner.
3. **Instructor Overrule Precedence**: Teacher final marks (`teacher_final_marks` or `StudentGradeRecord.is_manually_edited`) strictly supersede all AI-generated scores. Backfill synchronization will never overwrite a record marked `is_manually_edited = True`.
4. **Immutable Audit History**: Every score alteration, reason, and teacher timestamp is immutably recorded in `TeacherReview`, `EvaluationHistory`, and `EvaluationAuditLog`.

---

### BR-05: Multi-Provider AI Failover & Timeout Rules
1. **Timeout Budget**: Each AI evaluation request is allocated a hard timeout budget of **45 seconds**. If no response is received within 45s, the request immediately fails over to the next provider in the chain.
2. **HTTP 429 Rate Limit Cooldown**: When an AI provider returns HTTP 429 (Rate Limited / Quota Exhausted), it is placed on a **120-second non-transient cooldown** in `ProviderHealthTracker`, routing subsequent requests to alternate providers without thread blocking.
3. **LaTeX Formula Sanitization**: All mathematical matrices and LaTeX formulas must pass through regex backslash escaping before JSON decoding.
