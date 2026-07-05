# Software Requirements Specification (SRS)

| Field | Details |
|-------|---------|
| Project Name | IntelliGrade |
| Full Title | IntelliGrade: AI-Assisted Examination Script Evaluation System |
| Version | 1.0 |
| Status | Draft |
| Prepared By | Md. Taher Bin Omar Hijbullah |
| Date | 2026-07-04 |

---

# 1. Introduction

This document provides a detailed specification of the requirements for the IntelliGrade system. It outlines the purpose, scope, functions, and constraints of the software, serving as a foundational agreement between stakeholders and the development team.

## 1.1 Purpose

The purpose of IntelliGrade is to develop an AI-assisted examination evaluation platform that enhances grading efficiency, consistency, and transparency. The system is designed to augment, not replace, human examiners by providing intelligent, rubric-based scoring suggestions and feedback.

For a complete project vision, see the [Project Initiation Document](./01-project-initiation.md#1-project-vision).

## 1.2 Scope

The project scope includes the development of a web-based platform for managing the entire post-examination workflow, from answer script upload to final grade publication.

Key features include:
- User and Course Management
- Examination and Rubric Creation
- OCR-based text extraction from answer scripts
- AI-powered evaluation against rubrics
- An instructor review and approval workflow
- Analytics and reporting dashboards

For a detailed breakdown of included and excluded features, refer to the [Project Scope](./01-project-initiation.md#7-project-scope).

## 1.3 Definitions, Acronyms, and Abbreviations

This document uses specific terminology related to the project domain. All terms, acronyms, and abbreviations are defined in the project glossary.

See the complete [Glossary](./10-glossary.md).

## 1.4 References

| Document | Path |
|---|---|
| Project Proposal | `../00-project-management/01-project-proposal.md` |
| Technology Stack | `../00-project-management/02-technology-stack.md` |
| Project Initiation | `./01-project-initiation.md` |
| System Modules | `./02-system-modules.md` |
| System Workflow | `./03-system-workflow.md` |
| Requirement Analysis | `./04-requirement-analysis.md` |
| Use Case List | `./05-use-case-list.md` |
| User Stories | `./06-user-stories.md` |
| Functional Requirements | `./07-functional-requirements.md` |
| Business Rules | `./09-business-rules.md` |
| Requirements Traceability Matrix | `./11-requirements-traceability-matrix.md` |

## 1.5 Overview

This SRS is organized into four main sections.
- **Section 1 (Introduction)** provides an overview of the project's purpose, scope, and referenced documents.
- **Section 2 (Overall Description)** describes the product perspective, user classes, operating environment, and key constraints.
- **Section 3 (Specific Requirements)** details the functional, non-functional, and interface requirements for the system.
- **Section 4 (Appendices)** contains supplementary information, including the requirements traceability matrix.

---

# 2. Overall Description

## 2.1 Product Perspective

IntelliGrade is a new, self-contained web application designed to address inefficiencies in the manual grading process. It integrates with external AI services (like Gemini or OpenAI APIs) for evaluation but operates as a standalone platform. It is not an extension of an existing system.
 
The core of the system is a modular **AI Evaluation Engine** that orchestrates a multi-step pipeline from OCR to rubric-based scoring suggestions. This architecture ensures that the core logic is decoupled from specific external services, allowing for future extensibility.

## 2.2 Product Functions

The major functions of the IntelliGrade system are organized into distinct modules. These include user and course management, examination setup, and a sophisticated AI Evaluation Engine composed of sub-modules for OCR, text processing, answer segmentation, rubric matching, prompt building, LLM interaction, and score validation.

For a complete list of system modules and their features, see the [System Modules](./02-system-modules.md).

## 2.3 User Classes and Characteristics

The system will be used by different user roles, each with specific needs and permissions.

| User Class | Description |
|---|---|
| **Teacher (Examiner)** | Creates examinations, defines rubrics, uploads scripts, and reviews AI-suggested grades. |
| **Student** | Views published results and feedback. Can request re-evaluation. |
| **Administrator** | Manages users, courses, and system-level settings. Monitors system health. |
| **Department Head** | Monitors examination statistics and performance at the department level. |

Detailed user requirements for each class are available in the Requirement Analysis.

## 2.4 Operating Environment

IntelliGrade is a web application that will be deployed in a containerized environment using Docker.
- **Backend:** Django / Django REST Framework
- **Database:** PostgreSQL
- **Frontend:** Browser-rendered HTML/CSS (via Tailwind CSS)
- **Deployment:** Nginx, Gunicorn on a cloud server (e.g., Render, VPS)

For more details, see the Technology Stack.

## 2.5 Design and Implementation Constraints

- **OCR Accuracy:** System performance is dependent on the quality of handwriting in scanned scripts.
- **AI Validation:** All AI-generated scores and feedback require mandatory review and approval by a teacher.
- **Data Privacy:** Student data and answer scripts must be handled in compliance with academic privacy regulations.
- **External APIs:** The system relies on third-party AI services, which may have associated costs and rate limits.

A full list of constraints is documented in the Project Initiation Document.

## 2.6 User Documentation

As per the project's development rules, every feature must include documentation. This will be compiled into user guides for each user role (Administrator, Teacher) and a help section for students.

## 2.7 Assumptions and Dependencies

- Instructors are responsible for creating high-quality, detailed grading rubrics.
- The AI's role is to assist, not replace, the instructor, who retains final authority.
- A stable internet connection is required for uploading scripts and for the system to communicate with AI services.

A full list of assumptions is available in the Project Initiation Document.

---

# 3. Specific Requirements

## 3.1 Functional Requirements

The system's functional requirements define the specific behaviors and functions it must perform. These are derived from the user requirements and use cases.

- A summary list is available at Functional Requirements.
- A detailed breakdown tied to user needs is in the Requirement Analysis.
- The corresponding use cases are listed in the Use Case List.

### 3.1.1 Business Rules

All functional requirements are subject to the following business rules:

See the complete list of Business Rules.

## 3.2 Non-Functional Requirements

Non-functional requirements define the quality attributes of the system, such as performance, security, and reliability.

A complete list is available in the Non-Functional Requirements section of the Requirement Analysis document.

## 3.3 External Interface Requirements

The system will interface with external AI services for natural language processing and evaluation.

- **LLM Provider Layer:** The system will connect to external Large Language Model APIs (e.g., Gemini, OpenAI) via a dedicated provider layer. This layer abstracts the specific API implementation, allowing for future extensibility to other providers (e.g., Claude, local models). The initial implementation will use the Gemini API. All communication will be via RESTful HTTP requests.

- **File Storage:** In production, the system will interface with a cloud storage service (e.g., AWS S3) for storing uploaded scripts and generated reports.

---

# 4. Appendices

## 4.1 Requirements Traceability Matrix

The Requirements Traceability Matrix (RTM) links functional requirements to their corresponding use cases and test cases, ensuring that all requirements are covered.

See the Requirements Traceability Matrix.