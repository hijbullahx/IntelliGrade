import re
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class BaseAIProvider(ABC):
    """
    Abstract Base Class for all AI LLM Providers in IntelliGrade.
    Enforces SOLID principles (Interface Segregation & Dependency Inversion).
    """

    capabilities = {
        "supports_text": True,
        "supports_images": True,
        "supports_pdf": True,
        "supports_json": True,
        "supports_function_calling": False,
        "supports_streaming": False,
        "max_images": 5
    }

    def get_capabilities(self) -> Dict[str, Any]:
        """Returns declared capability matrix for provider routing."""
        return getattr(self, 'capabilities', {
            "supports_text": True, "supports_images": False, "supports_pdf": False, "supports_json": True, "max_images": 0
        })

    @staticmethod
    def log_health_event(provider_name: str, status: str, model_name: str = "AUTO", error_msg: str = "", response_time_ms: int = 0):
        """Logs provider health metrics, status changes, and rate limits to DB."""
        try:
            from django.utils import timezone
            from core.models import AIProviderHealth
            now = timezone.now()
            obj, _ = AIProviderHealth.objects.get_or_create(provider_name=provider_name)
            obj.current_model = model_name
            obj.status = status
            if status == AIProviderHealth.HealthStatus.HEALTHY:
                obj.last_success_at = now
                if response_time_ms > 0:
                    obj.avg_response_time_ms = int((obj.avg_response_time_ms + response_time_ms) / 2) if obj.avg_response_time_ms else response_time_ms
            else:
                obj.last_failure_at = now
                obj.error_count += 1
                obj.last_error_message = str(error_msg)[:500]
            obj.save()
        except Exception:
            pass

    @abstractmethod
    def generate_completion(self, prompt: str, system_instruction: Optional[str] = None, timeout: Optional[float] = None) -> str:
        """Generates raw text completion from prompt."""
        pass

    @abstractmethod
    def evaluate_answer(
        self,
        question_text: str,
        rubric_criteria: str,
        student_answer: str,
        max_marks: float,
        exemplars: Optional[List[Dict[str, Any]]] = None,
        custom_instructions: Optional[str] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Evaluates a student's answer segment against rubric criteria and returns structured JSON.
        """
        pass

    @abstractmethod
    def analyze_question_paper(self, paper_text_or_image: Any, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Analyzes a question paper to extract structured questions, marks, and subquestions.
        """
        pass

    @abstractmethod
    def generate_rubric(self, question_text: str, max_marks: float, sample_answer: Optional[str] = None, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Generates a suggested grading rubric, key points, and mark distribution for a question.
        """
        pass

    def extract_ocr_text(self, image_bytes: bytes, mime_type: str = "image/jpeg", timeout: Optional[float] = None) -> str:
        """Extracts text from document image via multimodal vision."""
        return ""

    def analyze_academic_exam_paper(self, qp_text_or_bytes: Any, outline_text_or_bytes: Any = None, image_bytes: Optional[bytes] = None, mime_type: str = 'image/jpeg', extra_files: Optional[List[Dict[str, Any]]] = None, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Base implementation for analyzing academic question papers across all providers."""
        doc_text = str(qp_text_or_bytes) if (qp_text_or_bytes and isinstance(qp_text_or_bytes, str)) else 'Academic Examination Paper'
        
        prompt = f"""
You are an expert University Academic Examination Question Scanner and OCR Engine.
Read the examination paper document text carefully and extract ALL examination questions, sub-parts, allocated marks, command verbs, Bloom taxonomy levels, CO/PO mappings, and expected answer criteria.

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
        response_text = self.generate_completion(prompt, system_instruction="Return ONLY raw JSON without commentary.", timeout=timeout)
        cleaned = re.sub(r'```json\s*', '', response_text)
        cleaned = re.sub(r'```\s*', '', cleaned).strip()

        # Direct JSON parse
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict) and 'questions' in parsed and parsed['questions']:
                return parsed
        except Exception:
            pass

        # Fix unescaped LaTeX backslashes
        try:
            fixed_escapes = re.sub(r'\\(?![/"\\bfnrtu])', r'\\\\', cleaned)
            parsed = json.loads(fixed_escapes)
            if isinstance(parsed, dict) and 'questions' in parsed and parsed['questions']:
                return parsed
        except Exception:
            pass

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

        return cls.extract_deterministic_regex_questions(doc_text)

    @classmethod
    def extract_deterministic_regex_questions(cls, doc_text: str) -> Dict[str, Any]:
        """
        Pure deterministic regex question extraction fallback that operates directly on document text
        without calling external AI network APIs.
        """
        fallback_questions = []
        pattern = re.compile(
            r'(?i)(?:\b(?:question|ans|answer|sol|solution)\s*(?:no\.?|number|#)?\s*[:.-]?\s*\d+|\bq\s*[-.]?\s*\d+\b|^\s*\d+[\.\)]\s+(?:consider|a\b|digital|explain|calculate|derive|find|what|how|describe|discuss|solve|state|write|analyze|compare|contrast))',
            re.MULTILINE
        )

        matches = list(pattern.finditer(doc_text))
        if matches:
            for idx, match in enumerate(matches):
                start_pos = match.start()
                end_pos = matches[idx + 1].start() if idx + 1 < len(matches) else len(doc_text)
                block_text = doc_text[start_pos:end_pos].strip()

                # Filter out header instructions
                b_lower = block_text.lower()[:100]
                if "answer all" in b_lower or "marks allocated" in b_lower or "instructions:" in b_lower:
                    continue

                if len(block_text) > 15:
                    q_num_match = re.search(r'(?i)(question\s*(?:no\.?)?\s*\d+|q\s*[-.]?\s*\d+|\b\d+)', match.group(0))
                    raw_num = q_num_match.group(1).upper() if q_num_match else f"{len(fallback_questions)+1}"
                    q_num_clean = re.sub(r'[^0-9]', '', raw_num)
                    q_num_formatted = f"Q{q_num_clean}" if q_num_clean else f"Q{len(fallback_questions)+1}"

                    marks_match = re.search(r'\[.*?(\d+(?:\.\d+)?)\s*marks?.*?\]', block_text, re.IGNORECASE)
                    allocated_marks = float(marks_match.group(1)) if marks_match else 25.0

                    fallback_questions.append({
                        "question_number": q_num_formatted,
                        "prompt_text": block_text[:1000],
                        "allocated_marks": allocated_marks,
                        "question_type": ["Theory"],
                        "command_verbs": ["Explain"],
                        "bloom_level": "Understand",
                        "co_mapping": f"CO{len(fallback_questions)+1}",
                        "po_mapping": ["PO1"],
                        "criteria": "Accurate response covering key concepts.",
                        "ideal_answer": "Model answer covering core concepts."
                    })

        return {"questions": fallback_questions}

    def analyze_question_full(
        self,
        question_prompt: str,
        max_marks: float = 10.0,
        course_outline_text: Optional[str] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyzes a question statement or generates a full examination question from a prompt/topic.
        Auto-generates comprehensive academic metadata:
        - Refined/Generated Question Statement
        - Question Category (Theory, Explanation, Numerical, etc.)
        - Command Verbs (Explain, Apply, Calculate, etc.)
        - Bloom Taxonomy Level (Remember, Understand, Apply, Analyze, Evaluate, Create)
        - OBE Course Outcome (CO1..CO4) & Program Outcomes (PO(a)..PO(d))
        - Expected / Model Solution Answer
        - Marking Criteria & Step-by-Step Partial Marks Rubric Breakdown
        - Common Mistakes & Key Technical Keywords
        """
        prompt = f"""
You are an expert Academic Examiner and University Curriculum Specialist.
Your goal is to synthesize a complete university examination question and marking rubric.

Input Request / Topic / Question:
"{question_prompt}"

Allocated Maximum Marks: {max_marks}
Course / Subject Context: {course_outline_text or "Computer Science / University Course"}

INSTRUCTIONS:
1. If the input is an instruction or topic (e.g. 'make a sample question', 'deadlocks', 'binary search tree', 'explain polymorphism'):
   Craft a complete, rigorous examination question with parts (a) and (b), diagrams and analytical trade-offs. Put this in "question_prompt".
2. If the input is already a question statement: refine it in "question_prompt".
3. Provide comprehensive criteria, ideal answer, master benchmark solution, Bloom's level, Course Outcome (CO1..CO4), Program Outcomes (PO(a)..PO(d)), Knowledge Profile (KP), Complex Engineering Problem (CEP), Complex Engineering Activity (CEA), keywords, and common student mistakes.

Output strictly valid JSON with keys:
- "question_prompt": (string: the complete synthesized or polished question statement)
- "question_type": (list of strings: e.g. ["Theory", "Explanation"])
- "command_verbs": (list of strings: e.g. ["Explain", "Compare"])
- "predicted_bloom": (string: Remember, Understand, Apply, Analyze, Evaluate, or Create)
- "predicted_CO": (string: CO1, CO2, CO3, or CO4)
- "predicted_PO": (list of strings: e.g. ["PO(a)", "PO(c)"])
- "predicted_KP": (list of strings: e.g. ["KP1"])
- "predicted_CEP": (list of strings: e.g. ["CEP1"])
- "predicted_CEA": (list of strings: e.g. ["CEA1"])
- "difficulty": (string: Easy, Medium, Hard, or Very Hard)
- "estimated_time": (string: e.g. "15 mins")
- "criteria": (string: detailed step-by-step marking breakdown with marks)
- "ideal_answer": (string: full comprehensive model answer)
- "expected_answer": (string: expected student response summary)
- "master_solution": (string: golden benchmark solution)
- "keywords": (list of strings: key technical terms)
- "alternative_answers": (string: acceptable variations)
- "common_mistakes": (list of strings: common errors)
- "rubric_levels": (object with Excellent, Good, Average, Poor, Fail keys and mark ranges)
"""
        try:
            response_text = self.generate_completion(prompt, system_instruction="You are an academic curriculum specialist. Return ONLY a single raw JSON object without commentary or markdown codeblocks.", timeout=timeout)
            
            # 1. Clean markdown codeblocks
            cleaned = re.sub(r'```(?:json)?\s*', '', response_text)
            cleaned = re.sub(r'```\s*', '', cleaned).strip()
            
            # Helper to validate parsed dict
            def is_substantive(d):
                if not isinstance(d, dict):
                    return False
                q_p = d.get('question_prompt', '')
                if not q_p or q_p.strip() in ['...', '…', '']:
                    return False
                return bool(d.get('criteria') or d.get('ideal_answer') or d.get('predicted_bloom'))

            # Direct parse
            try:
                parsed = json.loads(cleaned)
                if is_substantive(parsed):
                    return parsed
            except Exception:
                pass

            # Scan all JSON candidate blocks (from last to first)
            matches = list(re.finditer(r'\{[\s\S]*?\}', response_text))
            for m in reversed(matches):
                raw_candidate = m.group(0)
                for candidate in [raw_candidate, re.sub(r'\\(?![/"\\bfnrtu])', r'\\\\', raw_candidate)]:
                    try:
                        parsed = json.loads(candidate)
                        if is_substantive(parsed):
                            return parsed
                    except Exception:
                        pass

            # Largest JSON block fallback
            match = re.search(r'(\{[\s\S]*\})', response_text)
            if match:
                for candidate in [match.group(1), re.sub(r'\\(?![/"\\bfnrtu])', r'\\\\', match.group(1))]:
                    try:
                        parsed = json.loads(candidate)
                        if isinstance(parsed, dict) and ('criteria' in parsed or 'ideal_answer' in parsed):
                            return parsed
                    except Exception:
                        pass
        except Exception as e:
            print(f"[ANALYZE QUESTION AI ERROR] {e}")

        return self._fallback_analyze_question_prompt(question_prompt, max_marks, course_outline_text)

    @classmethod
    def _fallback_analyze_question_prompt(cls, prompt_text: str, max_marks: float = 10.0, course_context: Optional[str] = None) -> Dict[str, Any]:
        """Deterministic heuristic fallback when LLM is unavailable."""
        p_lower = prompt_text.lower().strip()
        
        # Check if the user is asking to synthesize / generate a sample question
        is_generation_request = any(p in p_lower for p in [
            'make a sample', 'sample question', 'create a question', 'generate a question',
            'create question', 'generate question', 'give me a question', 'sample', 'demo question'
        ]) or len(p_lower) < 15

        if is_generation_request:
            subject = course_context or "Computer Science / Engineering"
            synthesized_prompt = f"(a) Explain the fundamental architecture and principles of core concepts in {subject}. (b) Analyze the performance trade-offs, advantages, and limitations with illustrative diagrams and real-world examples."
            actual_prompt = synthesized_prompt
        else:
            actual_prompt = prompt_text

        p_eval = actual_prompt.lower()
        
        bloom = "Understand"
        if any(w in p_eval for w in ['define', 'list', 'state', 'name', 'what is', 'recall']):
            bloom = "Remember"
        elif any(w in p_eval for w in ['calculate', 'compute', 'solve', 'apply', 'implement', 'execute']):
            bloom = "Apply"
        elif any(w in p_eval for w in ['analyze', 'differentiate', 'compare', 'contrast', 'distinguish']):
            bloom = "Analyze"
        elif any(w in p_eval for w in ['evaluate', 'justify', 'critique', 'judge', 'assess']):
            bloom = "Evaluate"
        elif any(w in p_eval for w in ['design', 'create', 'formulate', 'develop', 'construct']):
            bloom = "Create"

        verbs = []
        for v in ['Explain', 'Define', 'Calculate', 'Analyze', 'Compare', 'Design', 'Apply', 'Evaluate', 'Justify']:
            if v.lower() in p_eval:
                verbs.append(v)
        if not verbs:
            verbs = ['Explain']

        q_types = []
        if any(w in p_eval for w in ['calculate', 'compute', 'solve', 'numerical', 'matrix']):
            q_types.append("Numerical")
        if any(w in p_eval for w in ['code', 'program', 'algorithm', 'function', 'class']):
            q_types.append("Programming")
        if any(w in p_eval for w in ['compare', 'contrast', 'difference', 'versus', 'vs']):
            q_types.append("Comparative")
        if any(w in p_eval for w in ['design', 'architecture', 'diagram']):
            q_types.append("Design")
        if not q_types:
            q_types = ["Theory", "Explanation"]

        return {
            "question_prompt": actual_prompt,
            "question_type": q_types,
            "command_verbs": verbs,
            "predicted_bloom": bloom,
            "predicted_CO": "CO1",
            "predicted_PO": ["PO(a)", "PO(c)"],
            "predicted_KP": ["KP1"],
            "predicted_CEP": ["CEP1"],
            "predicted_CEA": ["CEA1"],
            "difficulty": "Medium",
            "estimated_time": f"{max(5, int(max_marks * 1.5))} mins",
            "criteria": f"1. Core concepts & accuracy ({max_marks * 0.5:.1f} marks)\n2. Logical explanation & structure ({max_marks * 0.3:.1f} marks)\n3. Technical presentation & terminology ({max_marks * 0.2:.1f} marks)",
            "ideal_answer": f"Model solution addressing '{actual_prompt[:120]}...' with complete conceptual clarity.",
            "expected_answer": f"Standard academic response meeting all criteria for {max_marks} marks.",
            "master_solution": f"Benchmark solution for: {actual_prompt}",
            "keywords": [w.capitalize() for w in re.findall(r'\b[a-zA-Z]{5,}\b', actual_prompt)[:5]],
            "alternative_answers": "Alternative valid technical formulations and notations accepted.",
            "common_mistakes": ["Incomplete explanation", "Missing key formulas or definitions"],
            "rubric_levels": {
                "Excellent": {"marks": f"{max_marks*0.9:.1f}-{max_marks}", "criteria": "Flawless reasoning, thorough explanation."},
                "Good": {"marks": f"{max_marks*0.7:.1f}-{max_marks*0.85:.1f}", "criteria": "Good conceptual response with minor omissions."},
                "Average": {"marks": f"{max_marks*0.5:.1f}-{max_marks*0.65:.1f}", "criteria": "Basic understanding demonstrated."},
                "Poor": {"marks": f"{max_marks*0.2:.1f}-{max_marks*0.45:.1f}", "criteria": "Major gaps in explanation."},
                "Fail": {"marks": "0.0-{max_marks*0.15:.1f}", "criteria": "Incorrect response."}
            }
        }


