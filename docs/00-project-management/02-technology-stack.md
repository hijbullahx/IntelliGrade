# IntelliGrade — Technology Stack & Infrastructure Specification

**Document Version:** 3.5.0 (Enterprise Academic Release)  
**Last Updated:** August 29, 2026  
**Auditor:** Principal Enterprise Systems Architect  

---

## 1. Complete Technology Stack Matrix

```text
====================================================================================================
SYSTEM LAYER          TECHNOLOGY / LIBRARY                VERSION        FUNCTION & IMPLEMENTATION
====================================================================================================
Backend Core          Python                              3.11 / 3.13+   Core runtime execution
                      Django                              5.2.x          Monolithic web framework & ORM
                      Django REST Framework (DRF)         3.15.x         JSON API serialization & endpoints

Database Layer        SQLite (Dev / Local)                3.45+          Fast local development DB
                      PostgreSQL (Production)             16.x           Enterprise transactional relational DB
                      Django ORM (with JSONFields)        5.2.x          Stores dynamic rubrics, BBoxes, OBE

Document & PDF Engine PyMuPDF (`fitz`)                    1.24.x         300 DPI high-res rendering & glyph parsing
                      ReportLab                           4.2.x          Certified PDF generation & watermarking
                      PyPDF2                              3.0.x          PDF concatenation and metadata extraction

Vision & Preprocess   OpenCV (`opencv-python`)            4.10.x         Deskewing, thresholding, noise removal
                      Pillow (`PIL`)                      10.4.x         Image format conversion, cropping, thumbs
                      NumPy                               1.26.x         Matrix manipulation for BBox coordinates

OCR Engines           PyTesseract                         0.3.10+        Printed text optical character recognition
                      Tesseract OCR Engine (Binary)       v5.3+          Native C++ OCR backend
                      EasyOCR                             1.7.x          Deep learning OCR (handwriting fallback)
                      PyTorch CPU (`torch`, `torchvision`) 2.4.x         PyTorch runtime powering EasyOCR models

AI Provider Matrix    Local Offline Vision (Moondream2)   v2.0           Local lightweight vision model (0 API cost)
                      Ollama API                          0.3.x          Local LLM inference server (Llama 3 / Mistral)
                      Groq API (`groq`)                   0.9.x          Ultra-low latency LLM (Llama-3.3 70B)
                      Google GenAI (`google-generativeai`) 0.8.x         Gemini 2.5 Flash, Gemini 2.0 Flash
                      OpenRouter API                      v1 REST        Multi-model cloud aggregator & gateway
                      OpenAI API (`openai`)               1.40.x         GPT-4o, GPT-4o-mini multimodal reasoning

Excel & Spreadsheet   openpyxl                            3.1.x          8-sheet OBE Excel generation & formulas

Email & Background    Django Core Mail                    5.2.x          SMTP Multi-part HTML & text dispatch
                      Python `threading.Thread`           Standard Lib   Non-blocking background email/task runner
                      Institutional SMTP Server           dsr.iubat.ac.bd Official email gateway (Port 587 / TLS)

Frontend & UI         HTML5 / CSS3 / Vanilla JavaScript   ES6+           Component layout and client-side logic
                      TailwindCSS                         3.4.x          Utility-first design system & dark mode
                      Inter / Google Fonts                Web Fonts      Modern enterprise typography
                      Heroicons / FontAwesome             6.x            Vector icons & UI badges

Development Tools     Visual Studio Code / Cursor IDE     Latest         IDE environment
                      Git / GitHub                        2.45+          Distributed version control (branch: dev)
====================================================================================================
```

---

## 2. Architectural Layer Details

### 2.1 Backend Framework & Architecture
- **Framework**: Django 5.2.x utilizing Model-View-Template (MVT) architecture combined with RESTful JSON API endpoints for AJAX/Fetch workflows.
- **ORM & Data Persistence**: Leverages relational models with advanced `JSONField` columns for dynamic semi-structured data:
  - 23-section IUBAT question metadata (Bloom taxonomy, CO/PO/KP/CEP/CEA arrays).
  - Multi-page OCR word and line bounding boxes (`OCRResult.word_boxes_json`).
  - Answer region crops (`SubmissionAnswer.bounding_box_json`).
  - Dynamic OBE Course Tabulation scores (`StudentGradeRecord.exam_scores`, `co_scores`, `po_scores`).

### 2.2 Document Processing & Image Preprocessing Pipeline
- **PyMuPDF (`fitz`)**: Reads multi-page PDF documents, extracts embedded font text directly, and renders rasterized pages at 300 DPI (`zoom = 300 / 72 = 4.166`).
- **Skia/PDF Glyph Noise Cleaner**: Employs regex filters (`r'node\d{6,}'`) to remove PostScript font glyph artifacts produced by certain PDF printer drivers.
- **OpenCV & NumPy**:
  - Image deskewing via Hough Line Transforms.
  - Adaptive Gaussian thresholding and Otsu binarization.
  - Crop coordinate normalization (`[ymin, xmin, ymax, xmax]`) for visual answer segmentation.

### 2.3 Hybrid Multi-Engine OCR Architecture
```mermaid
graph LR
    A[Scanned Document Page] --> B{PyMuPDF Font Text Exists?}
    B -->|Yes (High Confidence)| C[Native Font Glyph Extraction]
    B -->|No (Scanned / Image)| D[OpenCV Image Preprocessor]
    D --> E[PyTesseract Engine (Fast Printed OCR)]
    E --> F{Confidence >= 75%?}
    F -->|Yes| G[Output Text & Word Boxes]
    F -->|No| H[EasyOCR Deep Learning Engine (Handwriting Fallback)]
    H --> G
```

### 2.4 Multimodal AI Engine & Failover Orchestrator
- **Failover Chain**: Designed with a prioritized failover hierarchy:
  1. `LocalOfflineVisionProvider` (Moondream2 on CPU / Ollama) $\rightarrow$ Zero API cost, operates offline.
  2. `GroqProvider` (`llama-3.3-70b-versatile`) $\rightarrow$ Instant text evaluation with sub-second latency.
  3. `OpenRouterProvider` $\rightarrow$ Cloud aggregator fallback to Mistral, Claude, or DeepSeek models.
  4. `GeminiProvider` (`gemini-2.5-flash` / `gemini-2.0-flash`) $\rightarrow$ High-accuracy multimodal vision evaluation.
  5. `OpenAIProvider` (`gpt-4o` / `gpt-4o-mini`) $\rightarrow$ Ultimate high-reasoning fallback.
- **Resilience Engine**:
  - `ProviderHealthTracker`: Tracks HTTP 429 rate limit events, placing providers on non-blocking cooldown timers.
  - `LaTeX Repair Utility`: Sanitizes unescaped backslashes in mathematical formulas before JSON decoding.
  - `TaskRouter`: Inspects task types (`ANSWER_VISUAL_READ`, `ANSWER_GRADING`, `ROUTINE_PARSE`) to select optimal providers.

### 2.5 Tabulation & 8-Sheet Excel Engine (`openpyxl`)
- Compiles real-time student grade records into an institutional OBE spreadsheet:
  - `HOME`: Main tabulation sheet with normalized 100-mark question distributions and formula `= (J*0.1) + (R*0.25) + (AN*0.5) + (AP*0.1) + Attendance`.
  - `ASSIGNMENT`: Continuous assessment and assignment breakdown.
  - `CO_ATTAINMENT` & `PO_ATTAINMENT`: Individual student Course and Program Outcome attainment percentages.
  - `CO_CLASS_ATTAINED` & `PO_CLASS_ATTAINED`: Class-wide OBE attainment thresholds (e.g. % of students scoring $\ge 50\%$).
  - `CQI`: Continuous Quality Improvement reflection sheet for accreditation reporting.