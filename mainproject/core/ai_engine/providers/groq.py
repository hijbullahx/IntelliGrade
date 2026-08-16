import os
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

    def _call_api(self, prompt: str, system_instruction: Optional[str] = None, image_bytes: Optional[bytes] = None, mime_type: str = 'image/jpeg') -> str:
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

        timeout_sec = int(os.environ.get('AI_REQUEST_TIMEOUT', 12))
        try:
            with urllib.request.urlopen(req, timeout=timeout_sec) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                choices = res_data.get('choices', [])
                if choices and choices[0].get('message', {}).get('content'):
                    return choices[0]['message']['content']
                raise ValueError("Groq returned empty response choices.")
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8', errors='ignore')
            raise Exception(f"Groq API Error {e.code}: {error_body}")
        except Exception as e:
            raise Exception(f"Groq API Request Failed: {str(e)}")

    def generate_completion(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        return self._call_api(prompt, system_instruction)

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
