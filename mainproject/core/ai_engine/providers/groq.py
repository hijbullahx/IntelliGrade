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
    Supports Llama3, Qwen Vision, and fast inference models.
    """

    capabilities = {
        "supports_text": True,
        "supports_images": True,
        "supports_pdf": False,
        "supports_json": True,
        "supports_function_calling": False
    }

    def __init__(self, api_key: str, model_name: str = "qwen/qwen3.6-27b"):
        self.api_key = api_key
        self.model_name = model_name

    @staticmethod
    def sanitize_thinking_output(text: str) -> str:
        """
        Sanitizes model outputs containing reasoning/thinking blocks such as:
        <think>
        ...
        </think>
        Returns clean content with thinking blocks stripped out.
        Handles malformed tags, missing closing tags, multiple blocks gracefully.
        """
        if not text or not isinstance(text, str):
            return ""

        # First, if there is text after </think>, check if it contains JSON
        if "</think>" in text:
            after_think = text.split("</think>")[-1].strip()
            if after_think and "{" in after_think:
                m_after = re.search(r'\{.*\}', after_think, re.DOTALL)
                if m_after:
                    return m_after.group(0).strip()
                return after_think

        # Remove complete <think>...</think> blocks (case-insensitive, dotall)
        cleaned = re.sub(r'(?i)<think>.*?</think>', '', text, flags=re.DOTALL)

        # Handle unclosed <think> tag: if <think> remains without closing </think>
        if re.search(r'(?i)<think>', cleaned):
            cleaned = re.sub(r'(?i)<think>.*$', '', cleaned, flags=re.DOTALL)

        # Strip remaining orphan </think> tags if any
        cleaned = re.sub(r'(?i)</think>', '', cleaned).strip()

        # Fallback: if cleaning stripped everything but raw text contains JSON object
        if not cleaned and '{' in text and '}' in text:
            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                cleaned = m.group(0).strip()

        return cleaned

    def _call_api(self, prompt: str, system_instruction: Optional[str] = None, image_bytes: Optional[bytes] = None, mime_type: str = 'image/jpeg', extra_files: Optional[List[Dict[str, Any]]] = None, timeout: Optional[float] = None) -> str:
        if not self.api_key:
            raise ValueError("Groq API Key is not configured.")

        url = "https://api.groq.com/openai/v1/chat/completions"
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})

        selected_model = self.model_name
        if image_bytes:
            selected_model = "qwen/qwen3.6-27b"
            import base64
            b64 = base64.b64encode(image_bytes).decode('utf-8')
            content_list = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64}"}}
            ]
            if extra_files and isinstance(extra_files, list):
                for ef in extra_files:
                    ef_b = ef.get('bytes') if isinstance(ef, dict) else (ef.get('image_bytes') if isinstance(ef, dict) else ef)
                    ef_m = ef.get('mime_type', 'image/png') if isinstance(ef, dict) else 'image/png'
                    if ef_b:
                        b64_ef = base64.b64encode(ef_b).decode('utf-8')
                        content_list.append({"type": "image_url", "image_url": {"url": f"data:{ef_m};base64,{b64_ef}"}})
            messages.append({"role": "user", "content": content_list})
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
                    raw_content = choices[0]['message']['content']
                    sanitized_content = self.sanitize_thinking_output(raw_content)
                    print(f"[AI TIMING] Groq model {selected_model} END: {elapsed:.2f}s (SUCCESS)")
                    return sanitized_content
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

    def generate_completion(self, prompt: str, system_instruction: Optional[str] = None, timeout: Optional[float] = None, **kwargs) -> str:
        return self._call_api(
            prompt,
            system_instruction=system_instruction,
            image_bytes=kwargs.get('image_bytes'),
            mime_type=kwargs.get('mime_type', 'image/png'),
            extra_files=kwargs.get('extra_files'),
            timeout=timeout
        )

    def evaluate_answer(
        self,
        question_text: str,
        rubric_criteria: str,
        student_answer: str,
        max_marks: float,
        exemplars: Optional[List[Dict[str, Any]]] = None,
        custom_instructions: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        mime_type: str = "image/png",
        extra_files: Optional[List[Dict[str, Any]]] = None,
        timeout: Optional[float] = None,
        **kwargs
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
        res = self._call_api(
            prompt,
            system_instruction="Return ONLY raw JSON.",
            image_bytes=image_bytes,
            mime_type=mime_type,
            extra_files=extra_files,
            timeout=timeout
        )
        cleaned = re.sub(r'```json\s*', '', res)
        cleaned = re.sub(r'```\s*', '', cleaned).strip()
        parsed = json.loads(cleaned)
        marks = float(parsed.get('ai_suggested_marks', 0.0))
        parsed['ai_suggested_marks'] = min(max(0.0, marks), float(max_marks))
        return parsed

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

CRITICAL INSTRUCTIONS:
1. Extract the EXACT physical wording of each question statement without rewriting, shortening, or inventing text.
2. Extract every question and sub-question (e.g. "1(a)", "1(b)", "2(a)", "Q1", "Q2") as a separate item.
3. Escape all backslashes in mathematical formulas or LaTeX equations (e.g. write \\\\begin{{bmatrix}} instead of \\begin{{bmatrix}}).

Question Paper Document Content:
{doc_text}

Return ONLY a valid JSON object in this exact schema without any markdown or commentary:
{{
  "questions": [
    {{
      "question_number": "e.g. 1(a) or Q1",
      "prompt_text": "Exact verbatim text of the question statement from the paper",
      "allocated_marks": 10.0,
      "question_type": ["Theory", "Explanation"],
      "command_verbs": ["Explain", "Calculate"],
      "scenario": "Optional scenario context if present",
      "bloom_level": "Understand",
      "co_mapping": "CO1",
      "po_mapping": ["PO(a)"],
      "kp_mapping": ["KP1"],
      "cep_mapping": ["CEP1"],
      "cea_mapping": ["CEA1"],
      "difficulty": "Medium",
      "estimated_time": "15 mins",
      "criteria": "Detailed step-by-step grading criteria with mark breakdown",
      "ideal_answer": "Sample or model answer",
      "expected_answer": "Structured expected answer summary",
      "keywords": ["Key Term 1", "Key Term 2"],
      "alternative_answers": "Alternative valid formulations",
      "common_mistakes": ["Common error 1"]
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

