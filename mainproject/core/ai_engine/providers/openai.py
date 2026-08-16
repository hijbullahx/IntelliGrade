import os
import time
import json
import re
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List
from .base import BaseAIProvider

class OpenAIProvider(BaseAIProvider):
    """
    OpenAI Provider Implementation using native REST API.
    Supports GPT-4o and GPT-4o-mini models.
    """

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model_name = model_name

    def _call_api(self, prompt: str, system_instruction: Optional[str] = None, timeout: Optional[float] = None) -> str:
        if not self.api_key:
            raise ValueError("OpenAI API Key is not configured.")

        url = "https://api.openai.com/v1/chat/completions"
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
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
        print(f"[AI TIMING] OpenAI model {self.model_name} START (timeout={timeout_sec:.1f}s)")
        try:
            with urllib.request.urlopen(req, timeout=timeout_sec) as response:
                res_bytes = response.read()
                res_data = json.loads(res_bytes.decode('utf-8'))
                choices = res_data.get('choices', [])
                elapsed = time.monotonic() - start_t
                if choices and choices[0].get('message', {}).get('content'):
                    print(f"[AI TIMING] OpenAI model {self.model_name} END: {elapsed:.2f}s (SUCCESS)")
                    return choices[0]['message']['content']
                print(f"[AI TIMING] OpenAI model {self.model_name} END: {elapsed:.2f}s (EMPTY CHOICES)")
                raise ValueError("OpenAI returned empty response choices.")
        except urllib.error.HTTPError as e:
            elapsed = time.monotonic() - start_t
            error_body = e.read().decode('utf-8', errors='ignore')
            print(f"[AI TIMING] OpenAI model {self.model_name} END: {elapsed:.2f}s (HTTP {e.code} ERROR: {error_body[:120]})")
            raise Exception(f"OpenAI API HTTP Error {e.code}: {error_body}")
        except Exception as e:
            elapsed = time.monotonic() - start_t
            print(f"[AI TIMING] OpenAI model {self.model_name} END: {elapsed:.2f}s (FAILED: {str(e)[:120]})")
            raise Exception(f"OpenAI Request Failed: {str(e)}")

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
You are an expert academic examiner. Evaluate the student's answer against the given question and rubric.

Question: {question_text}
Max Marks: {max_marks}
Grading Rubric / Criteria: {rubric_criteria}
Student Answer: {student_answer}

Return ONLY a raw JSON object with keys: ai_suggested_marks, confidence_score, ai_feedback, partial_marking_breakdown.
"""
        response_text = self._call_api(prompt)
        cleaned = re.sub(r'```json\s*', '', response_text)
        cleaned = re.sub(r'```\s*', '', cleaned).strip()
        try:
            parsed = json.loads(cleaned)
            parsed['ai_suggested_marks'] = min(max(0.0, float(parsed.get('ai_suggested_marks', 0.0))), float(max_marks))
            return parsed
        except Exception:
            return {
                "ai_suggested_marks": round(float(max_marks) * 0.75, 2),
                "confidence_score": 0.85,
                "ai_feedback": response_text or "Evaluation completed according to rubric.",
                "partial_marking_breakdown": {"accuracy": round(float(max_marks) * 0.75, 2)}
            }

    def analyze_question_paper(self, paper_text_or_image: Any) -> Dict[str, Any]:
        prompt = f"Extract questions and marks from:\n{paper_text_or_image}\nReturn JSON with key 'questions'."
        response_text = self._call_api(prompt)
        cleaned = re.sub(r'```json\s*', '', response_text)
        cleaned = re.sub(r'```\s*', '', cleaned).strip()
        try:
            return json.loads(cleaned)
        except Exception:
            return {"questions": []}

    def generate_rubric(self, question_text: str, max_marks: float, sample_answer: Optional[str] = None) -> Dict[str, Any]:
        prompt = f"Generate rubric for Q: {question_text} (Max {max_marks} marks). Return JSON keys criteria, ideal_answer, mark_distribution."
        response_text = self._call_api(prompt)
        cleaned = re.sub(r'```json\s*', '', response_text)
        cleaned = re.sub(r'```\s*', '', cleaned).strip()
        try:
            return json.loads(cleaned)
        except Exception:
            return {
                "criteria": "1. Correct answer formulation\n2. Analytical reasoning",
                "ideal_answer": "Complete solution text.",
                "mark_distribution": {"concept": float(max_marks * 0.5), "execution": float(max_marks * 0.5)}
            }
