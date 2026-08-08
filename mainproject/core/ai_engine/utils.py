"""
IntelliGrade AI Engine Utilities.
Imports canonical QuestionAccessor and QuestionDTO from core.utils.question_accessor.
"""

from typing import Any, List
from core.utils.question_accessor import (
    safe_getattr,
    safe_normalize_collection as normalize_collection,
    QuestionAccessor,
    QuestionDTO
)

__all__ = [
    'safe_getattr',
    'normalize_collection',
    'QuestionAccessor',
    'QuestionDTO'
]
