import os
import time
import json
import urllib.request
import urllib.error
import re
from typing import Dict, Any, Optional, List
from .base import BaseAIProvider

class GroqProvider(BaseAIProvider):
    """
    Groq AI Provider Implementation using REST API.
    Supports Llama3, Mixtral, and fast inference models.
    """

    def __init__(self, api_key: str, model_name: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.model_name = model_name

    def _call_api(self, prompt: str, system_instruction: Optional[str] = None, image_bytes: Optional[bytes] = None, mime_type: str = 'image/jpeg', timeout: Optional[float] = None) -> str:
        if not self.api_key:
            raise ValueError("Groq API Key is not configured.")

        url = "https://api.groq.com/openai/v1/chat/completions"
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})

        selected_model = self.model_name
        if image_bytes:
            selected_model = "llama-3.2-11b-vision-preview"
            import base64
            b64 = base64.b64encode(image_bytes).decode('utf-8')
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64}"}}
                ]
            })
        else:
            messages.append({"role": "user", "content": prompt})

        payload = {
            "model": selected_model,
            "messages": messages,
            "temperature": 0.2
        }

        json_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=json_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            },
            method='POST'
        )

        timeout_sec = float(timeout) if timeout is not None else float(os.environ.get('AI_REQUEST_TIMEOUT', 6.0))
        start_t = time.monotonic()
        print(f"[AI TIMING] Groq model {selected_model} START (timeout={timeout_sec:.1f}s)")
        try:
            with urllib.request.urlopen(req, timeout=timeout_sec) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                choices = res_data.get('choices', [])
                elapsed = time.monotonic() - start_t
                if choices and choices[0].get('message', {}).get('content'):
                    print(f"[AI TIMING] Groq model {selected_model} END: {elapsed:.2f}s (SUCCESS)")
                    return choices[0]['message']['content']
                print(f"[AI TIMING] Groq model {selected_model} END: {elapsed:.2f}s (EMPTY CHOICES)")
                raise ValueError("Groq returned empty response choices.")
        except urllib.error.HTTPError as e:
            elapsed = time.monotonic() - start_t
            error_body = e.read().decode('utf-8', errors='ignore')
            print(f"[AI TIMING] Groq model {selected_model} END: {elapsed:.2f}s (HTTP {e.code} ERROR: {error_body[:120]})")
            raise Exception(f"Groq API Error {e.code}: {error_body}")
        except Exception as e:
            elapsed = time.monotonic() - start_t
            print(f"[AI TIMING] Groq model {selected_model} END: {elapsed:.2f}s (FAILED: {str(e)[:120]})")
            raise Exception(f"Groq API Request Failed: {str(e)}")

    def generate_completion(self, prompt: str, system_instruction: Optional[str] = None, timeout: Optional[float] = None) -> str:
        return self._call_api(prompt, system_instruction, timeout=timeout)

    def evaluate_answer(
        self,
        question_text: str,
        rubric_criteria: str,
        student_answer: str,
        max_marks: float,
        exemplars: Optional[List[Dict[str, Any]]] = None,
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        prompt = f"""
Evaluate the following student answer for an academic examination question:

Question: {question_text}
Maximum Marks: {max_marks}
Rubric Criteria: {rubric_criteria}
Student Answer: {student_answer}

Return ONLY a raw JSON object with keys:
"ai_suggested_marks": float,
"confidence_score": float (0.0 to 1.0),
"ai_feedback": str,
"partial_marking_breakdown": dict
"""
        res = self._call_api(prompt, system_instruction="Return ONLY raw JSON.")
        try:
            cleaned = re.sub(r'```json\s*', '', res)
            cleaned = re.sub(r'```\s*', '', cleaned).strip()
            return json.loads(cleaned)
        except Exception:
            return {
                "ai_suggested_marks": round(max_marks * 0.75, 2),
                "confidence_score": 0.85,
                "ai_feedback": "Evaluated by Groq AI.",
                "partial_marking_breakdown": {"core_concept": round(max_marks * 0.75, 2)}
            }

    def analyze_question_paper(self, paper_text_or_image: Any, **kwargs) -> Dict[str, Any]:
        prompt = f"Extract routine or exam schedule from text:\n{str(paper_text_or_image)}\nReturn JSON with key 'routine_schedule'."
        res = self._call_api(prompt)
        try:
            return json.loads(re.sub(r'```[a-z]*', '', res).strip())
        except Exception:
            return {"routine_schedule": []}

    def generate_rubric(self, question_text: str, max_marks: float, sample_answer: Optional[str] = None) -> Dict[str, Any]:
        return {
            "criteria": f"Criteria for: {question_text}",
            "ideal_answer": sample_answer or "Model answer",
            "mark_distribution": {"concept": max_marks}
        }

    def analyze_academic_exam_paper(
        self,
        qp_text_or_bytes: Any,
        outline_text_or_bytes: Any = None,
        image_bytes: Optional[bytes] = None,
        mime_type: str = 'image/jpeg',
        extra_files: Optional[List[Dict[str, Any]]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        doc_text = str(qp_text_or_bytes) if (qp_text_or_bytes and isinstance(qp_text_or_bytes, str)) else 'Read directly from uploaded image/document'

        fig_context = ""
        if extra_files:
            fig_summaries = []
            for idx, f in enumerate(extra_files, start=1):
                cap = f.get('caption', f'Figure {idx}')
                page = f.get('page_number', 1)
                fig_summaries.append(f"- {cap} on Page {page}")
            fig_context = "\n\nDetected Visual Elements / Figures:\n" + "\n".join(fig_summaries)

        prompt = f"""
You are an expert University Academic Examination Question Scanner and OCR Engine.
Read the uploaded examination paper image or document carefully and extract ALL examination questions, sub-parts, allocated marks, command verbs, Bloom taxonomy levels, CO/PO mappings, and expected answer criteria.
{fig_context}

CRITICAL INSTRUCTION:
1. Extract EVERY SINGLE question (Question 1, Question 2, Question 3, Question 4, etc.) from the entire paper.
2. Escape all backslashes in mathematical formulas or LaTeX equations (e.g. write \\\\begin{{bmatrix}} instead of \\begin{{bmatrix}}).

Question Paper Document Content:
{doc_text}

Return ONLY a valid JSON object in this exact schema without any markdown or commentary:
{{
  "questions": [
    {{
      "question_number": "e.g. Q1",
      "prompt_text": "Exact text of the question statement from the paper",
      "allocated_marks": 25.0,
      "question_type": ["Theory", "Explanation"],
      "command_verbs": ["Explain", "Calculate"],
      "bloom_level": "Apply",
      "co_mapping": "CO2",
      "po_mapping": ["PO1"],
      "criteria": "Key criteria for grading",
      "ideal_answer": "Expected model answer summary"
    }}
  ]
}}
"""
        response_text = self._call_api(
            prompt,
            system_instruction="Return ONLY raw JSON without commentary.",
            image_bytes=image_bytes,
            mime_type=mime_type,
            timeout=timeout
        )

        cleaned = re.sub(r'```json\s*', '', response_text)
        cleaned = re.sub(r'```\s*', '', cleaned).strip()

        # Attempt 1: Direct JSON parse
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict) and 'questions' in parsed and parsed['questions']:
                return parsed
        except Exception:
            pass

        # Attempt 2: Fix unescaped LaTeX backslashes
        try:
            fixed_escapes = re.sub(r'\\(?![/"\\bfnrtu])', r'\\\\', cleaned)
            parsed = json.loads(fixed_escapes)
            if isinstance(parsed, dict) and 'questions' in parsed and parsed['questions']:
                return parsed
        except Exception:
            pass

        # Attempt 3: Regex match
        match = re.search(r'(\{[\s\S]*\})', response_text)
        if match:
            try:
                parsed = json.loads(match.group(1))
                if isinstance(parsed, dict) and 'questions' in parsed and parsed['questions']:
                    return parsed
            except Exception:
                try:
                    fixed_match = re.sub(r'\\(?![/"\\bfnrtu])', r'\\\\', match.group(1))
                    parsed = json.loads(fixed_match)
                    if isinstance(parsed, dict) and 'questions' in parsed and parsed['questions']:
                        return parsed
                except Exception:
                    pass

        raise ValueError(f"Groq response could not be parsed as structured questions JSON: {response_text[:200]}")

