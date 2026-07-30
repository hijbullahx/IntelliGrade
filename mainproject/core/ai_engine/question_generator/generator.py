import re
import json
from typing import Dict, Any, List, Optional
from core.ai_engine.providers.factory import AIProviderFactory

class QuestionGenerator:
    """
    Intelligent Academic Question Generator following IUBAT examination standards.
    Generates questions strictly aligned with Course Outline, CO, PO, Bloom Taxonomy,
    Weekly Topics, Exam Mode (Quiz/Mid/Final/Lab), and Question Type.
    """

    def generate_question(
        self,
        exam_type: str = "Final",
        question_type: str = "Theory",
        bloom_level: str = "Understand",
        co_mapping: str = "CO1",
        po_mapping: str = "PO1",
        difficulty: str = "Medium",
        allocated_marks: float = 10.0,
        topic_context: Optional[str] = None
    ) -> Dict[str, Any]:
        provider = AIProviderFactory.get_provider()
        topic = topic_context or "Software Architecture, Microservices, and Relational Database Design"

        prompt = f"""
You are an expert University Academic Question Generator following IUBAT examination standards.
Generate a structured examination question with complete grading rubric and expected model answer based on:

Exam Type: {exam_type}
Question Category: {question_type}
Target Topic: {topic}
Bloom Taxonomy Level: {bloom_level}
Course Outcome (CO): {co_mapping}
Program Outcome (PO): {po_mapping}
Difficulty: {difficulty}
Allocated Marks: {allocated_marks}

Return ONLY a valid JSON object matching this schema:
{{
  "question_number": "Q1 (a)",
  "prompt_text": "Complete statement of the generated question...",
  "allocated_marks": {allocated_marks},
  "question_type": ["{question_type}"],
  "command_verbs": ["Explain", "Design"],
  "bloom_level": "{bloom_level}",
  "co_mapping": "{co_mapping}",
  "po_mapping": ["{po_mapping}"],
  "difficulty": "{difficulty}",
  "estimated_time": "15 mins",
  "criteria": "Detailed criteria for partial mark allocation...",
  "ideal_answer": "Comprehensive model answer...",
  "keywords": ["Microservices", "REST API", "Schema"],
  "alternative_answers": "Valid alternative architectural approaches...",
  "common_mistakes": ["Confusing monolithic with microservice boundaries"]
}}
"""
        try:
            raw_res = provider.generate_completion(prompt, system_instruction="Return ONLY raw JSON.")
            cleaned = re.sub(r'```json\s*', '', raw_res)
            cleaned = re.sub(r'```\s*', '', cleaned).strip()
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict) and 'prompt_text' in parsed:
                return parsed
        except Exception:
            pass

        return {
            "question_number": "Q1 (a)",
            "prompt_text": f"Explain the core architectural principles of {topic}. Compare monolithic and microservices implementations with neat block diagrams.",
            "allocated_marks": allocated_marks,
            "question_type": [question_type],
            "command_verbs": ["Explain", "Compare"],
            "bloom_level": bloom_level,
            "co_mapping": co_mapping,
            "po_mapping": [po_mapping],
            "difficulty": difficulty,
            "estimated_time": "15 mins",
            "criteria": "1. Explanation of core architectural principles (5 marks)\n2. Comparative analysis & diagram (5 marks)",
            "ideal_answer": "Microservices decompose applications into independently deployable services communicating via lightweight APIs...",
            "keywords": ["Microservices", "Monolith", "REST API", "Scalability"],
            "alternative_answers": "Event-driven architecture with message queues (e.g. RabbitMQ/Kafka).",
            "common_mistakes": ["Confusing process isolation with module packaging."]
        }
