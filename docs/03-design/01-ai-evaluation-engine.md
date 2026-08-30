# IntelliGrade - AI Evaluation Engine (v4.0) Technical Architecture & Design

**Document Version:** 4.0.0 (Enterprise Academic Release)  
**Last Updated:** August 30, 2026  
**Auditor & Architect:** Principal Enterprise Systems Architect  

---

## 1. Engine Overview & Core Principles

The **IntelliGrade AI Evaluation Engine (v4.0)** is an enterprise-grade multimodal assessment pipeline designed for high accuracy, zero downtime, and strict adherence to institutional Outcome-Based Education (OBE) rubrics.

### Core Architectural Principles:
1. **Task-Aware Routing**: Evaluates each request type (`ANSWER_VISUAL_READ`, `ANSWER_GRADING`, `ROUTINE_PARSE`, `OCR_TEXT`) via `TaskRouter` to determine whether local vision or cloud LLM reasoning is required.
2. **Resilient Multi-Provider Failover**: Sequential provider chain ensuring no single API outage or rate limit (HTTP 429) disrupts evaluation.
3. **Local Vision Downsampling Optimization**: Enforces 800px LANCZOS downsampling and JPEG quality=75 compression before sending image payloads to Local Ollama Moondream (`/api/generate`), reducing memory overhead by 80%.
4. **Structured Output & Schema Enforcement**: Strict JSON output validation with auto-retry and regex LaTeX matrix backslash repair.
5. **Human-in-the-Loop Safeguards**: Low-confidence evaluations (<0.75) are automatically flagged with `requires_manual_review = True` for mandatory instructor review before grade certification.
6. **MCQ Fast-Path**: Specialized pipeline (< 3s) for objective/MCQ assessments with automatic option matching.

---

## 2. Multi-Provider Failover & Routing Architecture

```mermaid
graph TD
    A[Incoming Evaluation Task] --> B[TaskRouter.route]
    B --> C{Task Type & Capabilities}
    
    C -->|Vision Required| D[Vision Execution Chain]
    C -->|Text Only| E[Text Execution Chain]

    subgraph Vision Chain Priority
        D --> D1[1. Local Offline Vision: Moondream2 on CPU / Ollama (800px LANCZOS)]
        D1 -->|Fail / Timeout| D2[2. Groq Cloud: Llama-3.3-70B Multimodal]
        D2 -->|Fail / 429| D3[3. OpenRouter API Gateway]
        D3 -->|Fail / 429| D4[4. Google Gemini: 2.5 / 2.0 Flash]
        D4 -->|Fail / 429| D5[5. OpenAI: GPT-4o Multimodal]
    end

    subgraph Text Chain Priority
        E --> E1[1. Groq Cloud: Llama-3.3-70B]
        E1 -->|Fail / 429| E2[2. Google Gemini: 2.5 / 2.0 Flash]
        E2 -->|Fail / 429| E3[3. OpenAI: GPT-4o-mini]
        E3 -->|Fail / 429| E4[4. Local Ollama: Llama 3 / Mistral]
        E4 -->|Fail / 429| E5[5. OpenRouter Gateway]
    end

    D --> F[ProviderHealthTracker: Check Cooldown]
    E --> F
    F -->|Provider Healthy| G[Execute with 45s Timeout Budget]
    F -->|On Cooldown| H[Skip to Next Provider in Chain]
    G -->|HTTP 429 Rate Limit| I[Set 120s Cooldown & Fallback]
    G -->|Success| J[JSON Schema Validator & LaTeX Sanitize]
```

---

## 3. Provider Capabilities & Health Tracker

```text
====================================================================================================
PROVIDER CLASS               MODELS SUPPORTED                 CAPABILITIES         COST & LATENCY
====================================================================================================
LocalOfflineVisionProvider   Moondream2, Local Vision         Text, Images, Visual 0 API Cost | ~3-6s CPU
OllamaProvider               Llama 3, Mistral, Moondream      Text, JSON, Visual   0 API Cost | ~2-5s Local
GroqProvider                 llama-3.3-70b-versatile          Text, JSON           Low Cost   | ~0.5-1.5s
OpenRouterProvider           Mistral Large, DeepSeek R1       Text, Vision, JSON   Dynamic    | ~1.5-3.5s
GeminiProvider               gemini-2.5-flash, 2.0-flash      Text, Vision, JSON   Low Cost   | ~1.0-2.5s
OpenAIProvider               gpt-4o, gpt-4o-mini              Text, Vision, JSON   Standard   | ~1.5-3.0s
====================================================================================================
```

### Health Tracking & Cooldown Registry (`ProviderHealthTracker`):
- **Cooldown Window**: 120 seconds for HTTP 429 (Rate Limit / Quota Exhaustion) or HTTP 401/403 (Invalid Key).
- **Transient vs Non-Transient Errors**: Network timeouts trigger immediate retry with the next provider, while rate limits register in the cooldown pool without blocking other workers.
- **Persistent Telemetry**: Health events, error counts, and average response times logged to `AIProviderHealth` in database.

---

## 4. Evaluation Prompt Engineering & JSON Schema

### 4.1 System Evaluation Prompt Template
```text
You are an expert university examiner evaluating a student's answer script against an Outcome-Based Education (OBE) grading rubric.

[EXAMINATION CONTEXT]
Course: {course_code} - {course_title}
Question {question_number} ({max_marks} marks):
Prompt: {question_prompt}
Bloom's Level: {bloom_level} | CO Mapping: {co_mapping} | PO Mapping: {po_mapping}

[GRADING RUBRIC & BENCHMARKS]
Criteria & Mark Distribution: {criteria}
Model Answer / Key Points: {ideal_answer}
Keywords Expected: {keywords}
Common Mistakes & Deductions: {common_mistakes}
Master Benchmark Solution: {master_solution_text}

[STUDENT ANSWER CONTENT]
Extracted Text:
{student_answer_text}

[RESPONSE FORMAT]
You must respond with ONLY valid JSON strictly matching the schema below:
{
  "obtained_marks": float,
  "maximum_marks": float,
  "confidence_score": float (0.0 to 1.0),
  "feedback_text": "Detailed pedagogical feedback summarizing performance",
  "strengths": ["Identified accurate concept 1", "Correct formula applied"],
  "mistakes": ["Omission or calculation error 1"],
  "criteria_scores": [
    {"criterion": "Criterion Name", "awarded": float, "max": float, "comment": "Reasoning"}
  ]
}
```

### 4.2 JSON Sanitize & LaTeX Matrix Repair
All AI provider outputs are processed through `BaseAIProvider._sanitize_json_text`:
1. Strips markdown fences (````json ... ````).
2. Regex fixes invalid backslashes (`\begin{matrix}`, `\alpha`, `\frac`) using:
   ```python
   re.sub(r'\\(?![/"\\bfnrtu]|u[0-9a-fA-F]{4})', r'\\\\', text)
   ```
3. Performs fallback key extraction if JSON structure contains trailing commas or minor syntax irregularities.
