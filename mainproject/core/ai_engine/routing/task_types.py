from enum import Enum
from dataclasses import dataclass
from typing import Type, Optional, List, Dict, Any
from core.ai_engine.providers.base import BaseAIProvider

class TaskType(Enum):
    OCR_TEXT = "ocr_text"                     # Document OCR text extraction
    ROUTINE_PARSE = "routine_parse"           # Exam schedule parsing
    QUESTION_MAPPING = "question_mapping"     # Mapping student script crops to questions
    ANSWER_VISUAL_READ = "answer_visual_read" # Reading handwritten student script crops
    ANSWER_GRADING = "answer_grading"         # Rubric-grounded academic score evaluation
    FEEDBACK_GENERATION = "feedback_gen"      # Textual student feedback generation
    REPORT_SUMMARY = "report_summary"         # Class performance summary reports
    COMPLEX_REASONING = "complex_reasoning"   # Deep multi-step academic proofs

@dataclass
class ProviderStrategy:
    task_type: TaskType
    execution_chain: List[Type[BaseAIProvider]]  # Preferred provider priority classes
    requires_local_deterministic: bool           # True if local deterministic code takes precedence
    max_images: int                              # Max images per single API request for candidate providers
    requires_json: bool                          # True if structured JSON response is required
    timeout_seconds: float                       # Timeout budget for individual provider attempt
    manual_review_threshold: float               # Confidence score threshold triggering manual review
