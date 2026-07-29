# IntelliGrade AI Engine Architecture & Module Documentation

The **IntelliGrade AI Engine** (`core/ai_engine/`) is a modular, production-ready, extensible subsystem for AI-assisted examination evaluation, OCR text recognition, question paper analysis, rubric generation, and feedback RAG learning.

---

## 🏛️ Architecture & SOLID Principles

The AI Engine follows **SOLID principles** and clean architecture design:

1. **Single Responsibility Principle (SRP)**:
   - `providers/`: Deals solely with LLM communication.
   - `ocr/`: Deals solely with image preprocessing and OCR extraction.
   - `rubric/`: Deals solely with rubric generation and criteria parsing.
   - `script_analysis/`: Deals solely with student answer segmentation.
   - `evaluation/`: Deals solely with score calculation and evaluation formatting.
   - `feedback_learning/`: Deals solely with recording teacher corrections and RAG retrieval.
   - `memory/`: Deals solely with audit logging and latency tracking.

2. **Open/Closed Principle (OCP)**:
   - New AI Providers (e.g., Anthropic Claude, Mistral, Llama 3) can be added by creating a subclass of `BaseAIProvider` without modifying existing provider code.

3. **Liskov Substitution Principle (LSP)**:
   - All AI Providers (`GeminiProvider`, `OpenAIProvider`, `MockProvider`) implement `BaseAIProvider` and can be used interchangeably by the evaluation engine.

4. **Interface Segregation Principle (ISP)**:
   - `BaseAIProvider` exposes clean, dedicated methods (`evaluate_answer`, `analyze_question_paper`, `generate_rubric`).

5. **Dependency Inversion Principle (DIP)**:
   - High-level evaluation workflows depend on the `BaseAIProvider` abstract interface via `AIProviderFactory`, not on concrete LLM SDK implementations.

---

## 📂 Package Directory Structure

```
core/ai_engine/
├── __init__.py
├── providers/
│   ├── __init__.py
│   ├── base.py          # Abstract BaseAIProvider contract
│   ├── gemini.py        # Google Gemini 1.5/2.0 REST implementation
│   ├── openai.py        # OpenAI GPT-4o REST implementation
│   ├── mock.py          # Zero-dependency Mock provider for testing
│   └── factory.py       # AIProviderFactory for dynamic provider resolution
├── ocr/
│   ├── __init__.py
│   ├── preprocessor.py  # PIL image grayscale, contrast, noise filtering
│   └── engine.py        # OCREngineManager (PaddleOCR primary, PyTesseract fallback)
├── rubric/
│   ├── __init__.py
│   └── engine.py        # RubricEngine for generating mark distributions
├── script_analysis/
│   ├── __init__.py
│   └── segmenter.py     # ScriptSegmenter for QA block matching
├── evaluation/
│   ├── __init__.py
│   ├── prompt_builder.py# Few-shot RAG prompt generator
│   └── evaluator.py     # AIEvaluationEngine orchestrator
├── feedback_learning/
│   ├── __init__.py
│   └── rag.py           # FeedbackRAGStore (Teacher corrections memory)
├── memory/
│   ├── __init__.py
│   └── audit.py         # AIMemoryLogger (Audit logs & performance telemetry)
└── config/
    ├── __init__.py
    └── manager.py       # AIConfigManager settings controller
```

---

## ⚙️ Configuration & Database Models

- `AIConfiguration`: System configuration model storing active Provider (`GEMINI`, `OPENAI`, `MOCK`), Model Names, OCR Engine, Confidence Thresholds, and Prompt Templates.
- `FeedbackCorrection`: RAG memory table storing teacher mark corrections and vector embeddings.
- `AIMemoryLog`: Telemetry audit log recording prompt snapshots, model responses, confidence scores, and latency.
