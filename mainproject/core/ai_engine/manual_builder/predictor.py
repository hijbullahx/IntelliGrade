import re
import json
from typing import Dict, Any
from core.ai_engine.providers.factory import AIProviderFactory

class ManualQuestionAIPredictor:
    """
    Real-time AI Assistant for Manual Question Builder.
    Predicts Bloom level, CO/PO mappings, command verbs, difficulty, criteria,
    keywords, alternative answers, and common mistakes as teacher types.
    """

    def predict_metadata(self, question_text: str, max_marks: float = 10.0) -> Dict[str, Any]:
        if not question_text or len(question_text.strip()) < 5:
            return {
                "bloom_level": "Understand",
                "co_mapping": "CO1",
                "po_mapping": ["PO1"],
                "command_verbs": ["Explain"],
                "question_type": ["Theory"],
                "difficulty": "Medium",
                "criteria": "1. Correct understanding of key principles (100%)",
                "ideal_answer": "Expected model answer for the question.",
                "keywords": ["Concept"],
                "alternative_answers": "None",
                "common_mistakes": ["Incomplete explanation"]
            }

        provider = AIProviderFactory.get_provider()
        prompt = f"""
As an Academic AI Assistant, analyze this examination question text and predict its academic classification:

Question Text: {question_text}
Allocated Marks: {max_marks}

Return ONLY a valid JSON object matching this schema:
{{
  "bloom_level": "Understand/Apply/Analyze/Evaluate/Create",
  "co_mapping": "CO1",
  "po_mapping": ["PO1"],
  "command_verbs": ["Explain"],
  "question_type": ["Theory/Numerical/Algorithm/Design"],
  "difficulty": "Easy/Medium/Hard",
  "criteria": "Grading breakdown criteria...",
  "ideal_answer": "Suggested model answer...",
  "keywords": ["Key", "Terms"],
  "alternative_answers": "Alternative valid approaches...",
  "common_mistakes": ["Pitfalls"]
}}
"""
        try:
            raw_res = provider.generate_completion(prompt, system_instruction="Return ONLY raw JSON.")
            cleaned = re.sub(r'```json\s*', '', raw_res)
            cleaned = re.sub(r'```\s*', '', cleaned).strip()
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict) and 'bloom_level' in parsed:
                return parsed
        except Exception:
            pass

        # Rule-based fast fallback
        text_lower = question_text.lower()
        bloom = "Understand"
        verb = "Explain"
        if any(w in text_lower for w in ['calculate', 'compute', 'find', 'solve']):
            bloom = "Apply"
            verb = "Calculate"
        elif any(w in text_lower for w in ['design', 'build', 'create', 'develop']):
            bloom = "Create"
            verb = "Design"
        elif any(w in text_lower for w in ['compare', 'contrast', 'analyze']):
            bloom = "Analyze"
            verb = "Compare"

        return {
            "bloom_level": bloom,
            "co_mapping": "CO1",
            "po_mapping": ["PO1"],
            "command_verbs": [verb],
            "question_type": ["Theory"],
            "difficulty": "Medium",
            "criteria": f"1. Accurate response to {verb} prompt ({max_marks} marks)",
            "ideal_answer": f"Model solution addressing: {question_text}",
            "keywords": [verb, "Core Concept"],
            "alternative_answers": "Alternative valid formulations",
            "common_mistakes": ["Omitting essential steps"]
        }
