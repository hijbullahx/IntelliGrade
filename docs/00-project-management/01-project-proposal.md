# Project Proposal

| Field | Details |
|-------|---------|
| Project Name | IntelliGrade |
| Full Title | IntelliGrade: AI-Assisted Examination Script Evaluation System |
| Version | 1.0 |
| Status | Draft |
| Prepared By | Md. Taher Bin Omar Hijbullah |
| Date | 2026-07-04 |

---

# 1. Project Overview

IntelliGrade is a web-based AI-assisted examination evaluation platform designed to support instructors in grading descriptive answer scripts more efficiently, consistently, and transparently.
 
Rather than replacing human examiners, IntelliGrade acts as an intelligent assistant. It features a modular **AI Evaluation Engine** that processes answers against predefined rubrics to suggest marks, explanations, and feedback. The system is built on an "instructor-in-the-loop" philosophy, ensuring that educators have full authority to review, modify, and approve every AI-assisted assessment.

---

# 2. Problem Statement

Manual evaluation of descriptive examination scripts is time-consuming, labor-intensive, and susceptible to inconsistencies caused by examiner fatigue and subjective judgment.

Current examination systems rarely provide intelligent assistance during grading, making it difficult to maintain consistent evaluation standards while providing timely feedback to students.

---

# 3. Proposed Solution

Develop an AI-assisted web application capable of:

- Managing examinations
- Managing marking rubrics
- Uploading answer scripts
- Processing scripts through a modular AI pipeline:
  - OCR and Text Preprocessing
  - Answer Segmentation and Rubric Matching
  - Prompt Generation and LLM-based analysis
  - Score Normalization and Confidence Validation
- Allowing comprehensive instructor review and approval
- Publishing final grades
- Producing reports and analytics

---

# 4. Project Objectives

## Primary Objective

Develop an AI-assisted examination evaluation platform that improves grading efficiency while maintaining instructor authority over final grading.

## Specific Objectives

- Reduce grading time
- Improve grading consistency
- Generate AI-assisted, rubric-aligned feedback
- Support rubric-based evaluation
- Produce grading analytics
- Improve transparency
- Reduce manual workload

---

# 5. Target Users

- Administrator
- Teacher
- Student (Result & Feedback View)
- Department Head 

---

# 6. Expected Technologies

## Backend

- Django
- Django REST Framework

## Frontend

- Tailwind CSS

## Database

- PostgreSQL

## Artificial Intelligence

- Gemini API / OpenAI API

## OCR

- Tesseract OCR
- Google Vision API (Future)

## Deployment

- Docker
- Render / VPS

---

# 7. Expected Outcome

A professional AI-assisted examination evaluation platform that improves grading quality, reduces instructor workload, and maintains transparency through instructor-controlled assessment.