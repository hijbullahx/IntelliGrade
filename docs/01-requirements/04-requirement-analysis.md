# Requirement Analysis

| Document Information | |
|----------------------|-----------------------------|
| Project | IntelliGrade |
| Full Name | AI-Assisted Examination Script Evaluation System |
| Version | 1.0 |
| Status | Draft |
| Prepared By | Md. Taher Bin Omar Hijbullah |
| Phase | Requirement Engineering |

---

# Actor 1: Teacher (Examiner)

---

## User Requirement 1

The teacher wants to create examinations and define grading rubrics before evaluating answer scripts.

### System Requirements

1.1 The system shall provide a "Create Examination" page.

1.2 The teacher shall be able to enter examination details including title, course, semester, section, and total marks.

1.3 The system shall allow uploading the question paper in PDF format.

1.4 The teacher shall be able to create grading rubrics for each question.

1.5 Each rubric shall contain:

- Marks
- Keywords
- Expected Concepts
- Evaluation Notes

1.6 The system shall save examinations as Draft or Published.

---

### Functional Requirements

1. The system shall allow teachers to create new examinations.

2. The system shall allow uploading question papers.

3. The system shall allow defining question-wise rubrics.

4. The system shall store examination information.

5. The system shall allow editing examinations before publication.

---

## User Requirement 2

The teacher wants to upload answer scripts and receive AI-assisted grading suggestions.

### System Requirements

2.1 The system shall provide an "Upload Scripts" page.

2.2 The teacher shall upload one or multiple answer scripts.

2.3 The system shall automatically perform OCR.

2.4 AI shall evaluate answers according to the predefined rubric.

2.5 The system shall display:

- Suggested Marks
- Confidence Score
- AI Explanation
- Suggested Feedback

2.6 Teachers shall review AI-generated marks before approval.

---

### Functional Requirements

1. The system shall allow uploading answer scripts.

2. The system shall extract text using OCR.

3. The system shall evaluate answers using AI.

4. The system shall compare answers with grading rubrics.

5. The system shall generate suggested marks.

6. The system shall generate feedback.

7. The teacher shall approve or modify marks.

---

## User Requirement 3

The teacher wants to analyze examination performance.

### System Requirements

3.1 The system shall provide an Analytics Dashboard.

3.2 The dashboard shall display:

- Average Marks
- Highest Marks
- Lowest Marks
- Question-wise Performance
- AI Accuracy Statistics

3.3 Reports shall be exportable as PDF and Excel.

---

### Functional Requirements

1. The system shall generate examination analytics.

2. The system shall display graphical reports.

3. The system shall export reports.

---

# Actor 2: Student

---

## User Requirement 1

The student wants to view examination results and AI-generated feedback.

### System Requirements

1.1 Students shall log in securely.

1.2 The Result Dashboard shall list completed examinations.

1.3 Selecting an examination shall display:

- Marks
- Teacher Remarks
- AI Feedback
- Question-wise Marks

1.4 Students shall be able to download result reports.

---

### Functional Requirements

1. The system shall authenticate students.

2. The system shall display examination results.

3. The system shall display AI-generated feedback.

4. The system shall allow downloading reports.

---

## User Requirement 2

The student wants to request re-evaluation if dissatisfied with the result.

### System Requirements

2.1 A "Request Re-evaluation" button shall be available.

2.2 Students shall provide a reason.

2.3 Teachers shall receive notification.

2.4 The request status shall be visible.

---

### Functional Requirements

1. The system shall accept re-evaluation requests.

2. The system shall notify teachers.

3. The system shall update request status.

---

# Actor 3: Administrator

---

## User Requirement 1

The administrator wants to manage users and academic information.

### System Requirements

1.1 The Admin Dashboard shall provide:

- User Management
- Department Management
- Course Management
- Semester Management

1.2 The administrator shall assign teacher roles.

---

### Functional Requirements

1. The system shall create users.

2. The system shall edit users.

3. The system shall deactivate users.

4. The system shall assign user roles.

---

## User Requirement 2

The administrator wants to monitor AI evaluation activities.

### System Requirements

2.1 The system shall provide an AI Monitoring Dashboard.

2.2 The dashboard shall display:

- Number of Evaluated Scripts
- Average AI Confidence
- Processing Time
- Failed OCR Jobs

---

### Functional Requirements

1. The system shall monitor AI performance.

2. The system shall generate system statistics.

3. The system shall display OCR status.

---

# Actor 4: Department Head (Optional)

---

## User Requirement 1

The department head wants to monitor examination quality and instructor performance.

### System Requirements

1.1 The dashboard shall display:

- Examination Statistics

- Course-wise Performance

- Teacher Workload

- Result Distribution

1.2 Reports shall be exportable.

---

### Functional Requirements

1. The system shall provide department-level analytics.

2. The system shall generate summary reports.

3. The system shall export reports.

---

# Non-Functional Requirements

## Performance

1. The system shall process one answer script within an acceptable response time under normal load.

2. AI evaluation should complete without blocking other users.

---

## Availability

1. The system shall maintain at least 99% availability during examination periods.

---

## Security

1. User passwords shall be securely hashed.

2. All communications shall use HTTPS.

3. Role-Based Access Control (RBAC) shall be implemented.

---

## Reliability

1. OCR failures shall not crash the system.

2. AI evaluation failures shall be logged for review.

---

## Scalability

1. The system shall support multiple departments.

2. The system shall support concurrent evaluations.

---

## Maintainability

1. The software architecture shall support future AI model integration.

2. New examination types shall be easily added.

---

## Usability

1. The interface shall be intuitive.

2. Teachers shall require minimal training.

---

## Data Integrity

1. AI shall never overwrite teacher-approved marks.

2. All evaluation changes shall be logged.

---

## Privacy

1. Student answer scripts shall only be accessible to authorized users.

2. AI processing shall comply with institutional privacy policies.

---

## Backup & Recovery

1. Examination data shall be backed up regularly.

2. Recovery mechanisms shall be available.

---

## Auditability

1. Every grading action shall be recorded.

2. AI suggestions and teacher modifications shall be traceable.
