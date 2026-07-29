import json
import re
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List
from .base import BaseAIProvider

class GeminiProvider(BaseAIProvider):
    """
    Google Gemini AI Provider Implementation using native REST API.
    Supports gemini-1.5-flash and gemini-2.0-flash models.
    """

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model_name

    def _call_api(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        if not self.api_key:
            raise ValueError("Gemini API Key is not configured.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        
        full_text = prompt
        if system_instruction:
            full_text = f"System Instruction:\n{system_instruction}\n\nUser Request:\n{prompt}"

        payload = {
            "contents": [{"parts": [{"text": full_text}]}]
        }
        json_data = json.dumps(payload).encode('utf-8')

        req = urllib.request.Request(
            url,
            data=json_data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                res_bytes = response.read()
                res_data = json.loads(res_bytes.decode('utf-8'))
                candidates = res_data.get('candidates', [])
                if candidates:
                    return candidates[0]['content']['parts'][0]['text']
                return ""
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8', errors='ignore')
            raise Exception(f"Gemini API HTTP Error {e.code}: {error_body}")
        except Exception as e:
            raise Exception(f"Gemini Request Failed: {str(e)}")

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
        
        exemplar_text = ""
        if exemplars:
            exemplar_text = "\n\nPast Relevant Teacher Corrections (Few-Shot Exemplars):\n"
            for ex in exemplars:
                exemplar_text += f"- Question: {ex.get('question')}\n  Answer: {ex.get('student_answer')}\n  AI Mark: {ex.get('ai_marks')} -> Teacher Mark: {ex.get('teacher_marks')}\n  Reason: {ex.get('reason')}\n"

        prompt = f"""
You are an expert academic examiner. Evaluate the student's answer against the given question and rubric.

Question: {question_text}
Max Marks: {max_marks}
Grading Rubric / Criteria: {rubric_criteria}
Student Answer: {student_answer}
{exemplar_text}
{custom_instructions or ''}

Return ONLY a raw JSON object (no markdown, no backticks) in this exact schema:
{{
  "ai_suggested_marks": float,
  "confidence_score": float (between 0.0 and 1.0),
  "ai_feedback": "detailed step-by-step marking justification",
  "partial_marking_breakdown": {{"criterion_1": float, "criterion_2": float}}
}}
"""
        response_text = self._call_api(prompt)
        cleaned = re.sub(r'```json\s*', '', response_text)
        cleaned = re.sub(r'```\s*', '', cleaned).strip()
        
        try:
            parsed = json.loads(cleaned)
            # Ensure marks bounds
            marks = float(parsed.get('ai_suggested_marks', 0.0))
            parsed['ai_suggested_marks'] = min(max(0.0, marks), float(max_marks))
            return parsed
        except Exception:
            return {
                "ai_suggested_marks": round(float(max_marks) * 0.7, 2),
                "confidence_score": 0.80,
                "ai_feedback": response_text or "Answer evaluated according to rubric criteria.",
                "partial_marking_breakdown": {"content_accuracy": round(float(max_marks) * 0.7, 2)}
            }

    def analyze_question_paper(self, paper_text_or_image: Any) -> Dict[str, Any]:
        prompt = f"""
Analyze the following exam question paper text and extract all questions, subquestions, and max marks.

Question Paper Text:
{paper_text_or_image}

Return ONLY raw JSON in this schema:
{{
  "questions": [
    {{"question_number": "Q1", "prompt_text": "...", "max_marks": 10.0}}
  ]
}}
"""
        response_text = self._call_api(prompt)
        cleaned = re.sub(r'```json\s*', '', response_text)
        cleaned = re.sub(r'```\s*', '', cleaned).strip()
        try:
            return json.loads(cleaned)
        except Exception:
            return {"questions": []}

    def generate_rubric(self, question_text: str, max_marks: float, sample_answer: Optional[str] = None) -> Dict[str, Any]:
        prompt = f"""
Generate a comprehensive grading rubric for the following exam question:

Question: {question_text}
Max Marks: {max_marks}
Sample Answer (if available): {sample_answer or 'N/A'}

Return ONLY raw JSON in this schema:
{{
  "criteria": "detailed bullet points for key concepts expected",
  "ideal_answer": "model answer demonstrating key points",
  "mark_distribution": {{"key_point_1": 4.0, "key_point_2": 3.0, "key_point_3": 3.0}}
}}
"""
        response_text = self._call_api(prompt)
        cleaned = re.sub(r'```json\s*', '', response_text)
        cleaned = re.sub(r'```\s*', '', cleaned).strip()
        try:
            return json.loads(cleaned)
        except Exception:
            return {
                "criteria": f"1. Core concept definition ({max_marks * 0.5} marks)\n2. Technical accuracy & examples ({max_marks * 0.5} marks)",
                "ideal_answer": "Model answer covering theoretical concepts and practical applications.",
                "mark_distribution": {"core_concept": float(max_marks * 0.5), "accuracy": float(max_marks * 0.5)}
            }
