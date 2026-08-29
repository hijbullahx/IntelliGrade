# IntelliGrade — Non-Functional Requirements Specification (NFRS)

**Document Version:** 3.5.0 (Enterprise Academic Edition)  
**Last Updated:** August 29, 2026  
**Auditor:** Principal Enterprise Systems Architect  

---

## 1. Non-Functional Requirements Catalog

```text
====================================================================================================
REQ ID    CATEGORY             NON-FUNCTIONAL REQUIREMENT STATEMENT & METRIC TARGET
====================================================================================================
NFR-01    Performance (Web)    The web application SHALL render dashboard pages and tabulation tables
                               within <= 1.5 seconds under standard institutional network loads.
NFR-02    Performance (OCR)    The system SHALL complete 300 DPI image rendering, deskewing, and PyTesseract
                               OCR extraction within <= 4.0 seconds per script page.
NFR-03    Performance (AI)     AI evaluation requests via Groq/Gemini SHALL return structured evaluations
                               within <= 8.0 seconds per question answer.
NFR-04    Failover Latency     In the event of a provider timeout (45s) or HTTP 429 rate limit, the failover
                               orchestrator SHALL transition to the next provider within <= 500 ms.
NFR-05    Scalability          The database and storage layer SHALL support concurrent batch uploads of up to
                               100 multi-page student scripts per examination without deadlock.
NFR-06    Availability         The system architecture SHALL achieve >= 99.5% uptime during examination and
                               grading periods, supported by local offline vision and LLM fallbacks.
NFR-07    Security (Auth)      All user passwords SHALL be salted and hashed using Argon2 / PBKDF2 with SHA-256;
                               plaintext passwords SHALL never be persisted.
NFR-08    Security (RBAC)      Every view and API endpoint SHALL enforce strict role checking decorators
                               (@admin_required, @teacher_required, @student_required, @dept_head_required).
NFR-09    Security (CSRF)      All mutating HTTP POST/PUT/DELETE requests SHALL mandate valid CSRF tokens
                               validated via Django CSRF middleware.
NFR-10    Data Integrity       All grade updates, submission states, and review audit entries SHALL execute
                               within atomic database transactions (django.db.transaction.atomic).
NFR-11    Auditability         All manual mark overrides, prompt alterations, and evaluation deletions SHALL
                               record immutable audit entries with teacher ID, timestamp, and IP address.
NFR-12    Compliance (OBE)     All Course Outcome and Program Outcome calculations SHALL strictly adhere to
                               IUBAT and BAETE OBE engineering accreditation standards.
NFR-13    Spreadsheet Fidelity The generated 8-sheet Excel workbooks SHALL strictly preserve openpyxl formulas,
                               data validation rules, and cell color formatting across all sheets.
NFR-14    Email Reliability    Institutional email dispatches SHALL execute asynchronously in background threads
                               so that slow SMTP handshake latency never blocks user HTTP responses.
NFR-15    Usability (UI/UX)    The web UI SHALL support full responsive design, dark/light theme switching,
                               and split-screen synchronized PDF viewing on standard desktop screens.
====================================================================================================
```
