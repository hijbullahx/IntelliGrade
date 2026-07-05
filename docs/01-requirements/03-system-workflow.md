# System Workflow

Version: 1.0

---

# High-Level Workflow

```text
Administrator

↓

Create Teachers

↓

Create Courses

↓

Teacher Login

↓

Create Examination

↓

Upload Question Paper

↓

Create Rubric

↓

Students Complete Examination

↓

Teacher Uploads Answer Scripts

        ↓

OCR Service Extracts Text

        ↓

Text Cleaning & Preprocessing

        ↓

Answer Segmentation

        ↓

Rubric Engine Matches Answer to Rubric

        ↓

Prompt Builder Creates Structured Prompt

        ↓

LLM Provider Layer Generates Evaluation

        ↓

Score Normalization & Confidence Validation

↓

Teacher Reviews Evaluation

↓

Teacher Modifies 

↓

Final Approval

↓

Generate Reports

↓

Publish Results
```

---

# Workflow Description

1. Administrator creates academic structure.
2. Teachers create examinations.
3. Teachers prepare grading rubrics.
4. Students complete examinations.
5. Teachers upload scanned answer scripts.
6. OCR extracts textual content.
7. The AI Evaluation Engine processes the text through a multi-stage pipeline (preprocessing, segmentation, rubric matching, LLM analysis).
8. The system generates suggested marks, confidence scores, and explanations.
9. Teachers review the detailed AI-assisted evaluation.
10. Teachers approve or modify marks.
11. Final reports are generated.
12. Results are published.