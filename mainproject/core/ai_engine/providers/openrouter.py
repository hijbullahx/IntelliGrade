import os
import time
import json
import urllib.request
import urllib.error
import re
import base64
from typing import Dict, Any, Optional, List
from .base import BaseAIProvider

class OpenRouterProvider(BaseAIProvider):
    """
    OpenRouter AI Provider Implementation using OpenAI-compatible REST API.
    Supports text, images (multimodal vision), extra_files, and structured JSON output.
    Default model is 'openrouter/free' to allow OpenRouter edge router to pick free vision models dynamically.
    """

    capabilities = {
        "supports_text": True,
        "supports_images": True,
        "supports_pdf": False,
        "supports_json": True,
        "supports_function_calling": False,
        "max_images": 5  # OpenRouter Free verified for up to 5 real images
    }

    def __init__(self, api_key: Optional[str] = None, model_name: str = "openrouter/free"):
        try:
            from django.conf import settings
            settings_key = getattr(settings, 'OPENROUTER_API_KEY', '')
        except Exception:
            settings_key = ''

        if api_key is None:
            raw_key = (settings_key or os.environ.get('OPENROUTER_API_KEY') or '').strip()
        else:
            raw_key = str(api_key).strip()

        self.api_key = raw_key.strip('"').strip("'").strip()
        self.model_name = model_name or "openrouter/free"

    @staticmethod
    def sanitize_thinking_output(text: str) -> str:
        """
        Sanitizes model outputs containing reasoning/thinking blocks such as <think>...</think>.
        """
        if not text or not isinstance(text, str):
            return ""

        if "</think>" in text:
            after_think = text.split("</think>")[-1].strip()
            if after_think and "{" in after_think:
                m_after = re.search(r'\{.*\}', after_think, re.DOTALL)
                if m_after:
                    return m_after.group(0).strip()
                return after_think

        cleaned = re.sub(r'(?i)<think>.*?</think>', '', text, flags=re.DOTALL)

        if re.search(r'(?i)<think>', cleaned):
            cleaned = re.sub(r'(?i)<think>.*$', '', cleaned, flags=re.DOTALL)

        cleaned = re.sub(r'(?i)</think>', '', cleaned).strip()

        if not cleaned and '{' in text and '}' in text:
            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                cleaned = m.group(0).strip()

        return cleaned

    def _call_api(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        mime_type: str = 'image/png',
        extra_files: Optional[List[Dict[str, Any]]] = None,
        timeout: Optional[float] = None
    ) -> str:
        if not self.api_key:
            raise ValueError("OpenRouter API Key is not configured.")

        total_images = (1 if image_bytes else 0) + (len(extra_files) if extra_files and isinstance(extra_files, list) else 0)
        max_allowed = self.capabilities.get('max_images', 5)
        if total_images > max_allowed:
            raise ValueError(f"Too many images provided ({total_images}). OpenRouter supports up to {max_allowed} images.")

        url = "https://openrouter.ai/api/v1/chat/completions"
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})

        selected_model = self.model_name or "openrouter/free"

        if image_bytes:
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
                'HTTP-Referer': 'https://intelligrade.app',
                'X-Title': 'IntelliGrade'
            },
            method='POST'
        )

        # Free-tier vision models are slow with large payloads — use generous defaults
        has_images_in_call = bool(image_bytes or extra_files)
        if timeout is not None:
            timeout_sec = float(timeout)
        else:
            env_timeout = float(os.environ.get('AI_REQUEST_TIMEOUT', 0) or 0)
            if env_timeout > 0:
                timeout_sec = env_timeout
            elif has_images_in_call:
                timeout_sec = float(os.environ.get('AI_OPENROUTER_VISION_TIMEOUT', 6.0))
            else:
                timeout_sec = float(os.environ.get('AI_OPENROUTER_TEXT_TIMEOUT', 6.0))
        start_t = time.monotonic()
        print(f"[AI TIMING] OpenRouter model {selected_model} START (timeout={timeout_sec:.1f}s)")
        import socket
        old_timeout = socket.getdefaulttimeout()
        try:
            socket.setdefaulttimeout(timeout_sec)
            with urllib.request.urlopen(req, timeout=timeout_sec) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                choices = res_data.get('choices', [])
                elapsed = time.monotonic() - start_t
                if choices and choices[0].get('message', {}).get('content'):
                    raw_content = choices[0]['message']['content']
                    sanitized_content = self.sanitize_thinking_output(raw_content)
                    print(f"[AI TIMING] OpenRouter model {selected_model} END: {elapsed:.2f}s (SUCCESS)")
                    return sanitized_content
                print(f"[AI TIMING] OpenRouter model {selected_model} END: {elapsed:.2f}s (EMPTY CHOICES)")
                raise ValueError("OpenRouter returned empty response choices.")
        except urllib.error.HTTPError as e:
            elapsed = time.monotonic() - start_t
            error_body = e.read().decode('utf-8', errors='ignore')
            print(f"[AI TIMING] OpenRouter model {selected_model} END: {elapsed:.2f}s (HTTP {e.code} ERROR: {error_body[:120]})")
            raise Exception(f"OpenRouter API Error {e.code}: {error_body}")
        except Exception as e:
            elapsed = time.monotonic() - start_t
            print(f"[AI TIMING] OpenRouter model {selected_model} END: {elapsed:.2f}s (FAILED: {str(e)[:120]})")
            raise Exception(f"OpenRouter API Request Failed: {str(e)}")
        finally:
            socket.setdefaulttimeout(old_timeout)

    def generate_completion(self, prompt: str, system_instruction: Optional[str] = None, timeout: Optional[float] = None, **kwargs) -> str:
        return self._call_api(
            prompt,
            system_instruction=system_instruction,
            image_bytes=kwargs.get('image_bytes'),
            mime_type=kwargs.get('mime_type', 'image/png'),
            extra_files=kwargs.get('extra_files'),
            timeout=timeout
        )

    def extract_ocr_text(self, image_bytes: bytes, mime_type: str = 'image/png', timeout: Optional[float] = None, **kwargs) -> str:
        eff_timeout = timeout if timeout is not None else kwargs.get('timeout')
        prompt = "Perform accurate OCR on this document image. Transcribe all text verbatim line-by-line."
        return self._call_api(prompt, image_bytes=image_bytes, mime_type=mime_type, timeout=eff_timeout)

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

    def analyze_question_paper(self, paper_text_or_image: Any, timeout: Optional[float] = None) -> Dict[str, Any]:
        prompt = f"Extract routine or exam schedule from text:\n{str(paper_text_or_image)}\nReturn JSON with key 'routine_schedule'."
        res = self._call_api(prompt, timeout=timeout)
        try:
            return json.loads(re.sub(r'```[a-z]*', '', res).strip())
        except Exception:
            return {"routine_schedule": []}

    def generate_rubric(self, question_text: str, max_marks: float, sample_answer: Optional[str] = None, timeout: Optional[float] = None) -> Dict[str, Any]:
        return {
            "criteria": f"Criteria for: {question_text}",
            "ideal_answer": sample_answer or "Model answer",
            "mark_distribution": {"concept": max_marks}
        }
