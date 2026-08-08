"""
IntelliGrade Canonical Question Accessor & Data Transfer Object (DTO) Module.
Provides a single canonical interface for accessing Question properties across views, templates, and AI engines.
Prevents database schema coupling and AttributeError / VariableDoesNotExist crashes.
"""

from typing import Any, List, Dict, Optional
from dataclasses import dataclass, field, asdict

def safe_getattr(obj: Any, fields: List[str], default: Any = "") -> Any:
    """
    Safely retrieves the first existing non-None attribute from a list of candidate field names.
    Supports Django ORM models, dictionaries, DTO objects, and generic Python classes.
    """
    if obj is None:
        return default
    if isinstance(obj, dict):
        for f in fields:
            if f in obj and obj[f] is not None:
                return obj[f]
        return default
    for f in fields:
        if hasattr(obj, f):
            val = getattr(obj, f)
            if val is not None:
                return val
    return default


def safe_normalize_collection(obj: Any) -> List[Any]:
    """
    Safely normalizes any collection or relation into an iterable list.
    Handles Django QuerySet, RelatedManager, list, tuple, set, generator, or None.
    Prevents AttributeError: 'list' object has no attribute 'all'.
    """
    if obj is None:
        return []
    if hasattr(obj, 'all') and callable(getattr(obj, 'all')):
        try:
            return list(obj.all())
        except Exception:
            pass
    if isinstance(obj, (list, tuple, set)):
        return list(obj)
    return [obj]


@dataclass
class QuestionDTO:
    """
    Canonical Question Data Transfer Object (DTO).
    Normalized, decoupled representation consumed by templates, views, and AI evaluators.
    """
    id: int
    number: str
    text: str
    marks: float
    bloom: str = "Understand"
    co: str = "CO1"
    po: str = "PO1"
    rubric: str = ""
    figures: List[Any] = field(default_factory=list)
    tables: List[Any] = field(default_factory=list)
    formulas: List[Any] = field(default_factory=list)

    @property
    def prompt_text(self) -> str:
        return self.text

    @classmethod
    def from_model(cls, q: Any) -> 'QuestionDTO':
        """Converts a Django Question model instance, dict, or DTO into a QuestionDTO."""
        if isinstance(q, QuestionDTO):
            return q
        return QuestionAccessor.to_dto(q)

    def to_dict(self) -> Dict[str, Any]:
        """Converts DTO to dictionary for JSON serialization or template context."""
        return {
            'id': self.id,
            'number': self.number,
            'question_number': self.number,
            'text': self.text,
            'question_display_text': self.text,
            'marks': self.marks,
            'max_marks': self.marks,
            'bloom': self.bloom,
            'bloom_level': self.bloom,
            'co': self.co,
            'co_mapping': self.co,
            'po': self.po,
            'po_mapping': self.po,
            'rubric': self.rubric,
            'rubric_text': self.rubric,
            'figures': self.figures,
            'tables': self.tables,
            'formulas': self.formulas
        }


class QuestionAccessor:
    """
    Canonical accessor class for Django Question models.
    All components (evaluators, services, views) must access question attributes via this class.
    """

    @classmethod
    def get_text(cls, question: Any) -> str:
        """Retrieves question body text statement using safe fallback inspection."""
        val = safe_getattr(question, ['prompt_text', 'question_text', 'text', 'body', 'question', 'description', 'content'], default="")
        return str(val).strip()

    @classmethod
    def get_marks(cls, question: Any) -> float:
        """Retrieves maximum marks as float."""
        val = safe_getattr(question, ['max_marks', 'marks', 'maximum_marks'], default=0.0)
        try:
            return float(val)
        except (ValueError, TypeError):
            return 0.0

    @classmethod
    def get_question_number(cls, question: Any) -> str:
        """Retrieves question number identifier string (e.g., '1', 'Q1')."""
        val = safe_getattr(question, ['question_number', 'number', 'q_num', 'id'], default="1")
        return str(val).strip()

    @classmethod
    def get_co(cls, question: Any) -> str:
        """Retrieves Course Outcome (CO) mapping."""
        val = safe_getattr(question, ['co_mapping', 'co', 'course_outcome'], default="CO1")
        return str(val).strip()

    @classmethod
    def get_po(cls, question: Any) -> str:
        """Retrieves Program Outcome (PO) mapping."""
        val = safe_getattr(question, ['po_mapping', 'po', 'program_outcome'], default="PO1")
        return str(val).strip()

    @classmethod
    def get_bloom(cls, question: Any) -> str:
        """Retrieves Bloom's Taxonomy level."""
        val = safe_getattr(question, ['bloom_level', 'bloom', 'bloom_taxonomy'], default="Understand")
        return str(val).strip()

    @classmethod
    def get_rubric(cls, question: Any) -> str:
        """Retrieves rubric criteria text safely."""
        rubric_obj = safe_getattr(question, ['rubric'], default=None)
        if rubric_obj:
            r_text = safe_getattr(rubric_obj, ['criteria_text', 'rubric_text', 'text', 'content'], default="")
            if r_text:
                return str(r_text).strip()
        val = safe_getattr(question, ['rubric_text', 'rubrics', 'rubric_content'], default="Grade based on accuracy and complete steps.")
        return str(val).strip()

    @classmethod
    def get_figures(cls, question: Any) -> List[Any]:
        """Safely retrieves question figures relation or list. Returns [] if missing."""
        figs = safe_getattr(question, ['figures_rel', 'figures'], default=[])
        return safe_normalize_collection(figs)

    @classmethod
    def get_tables(cls, question: Any) -> List[Any]:
        """Safely retrieves question tables relation or list. Returns [] if missing."""
        tbls = safe_getattr(question, ['tables_rel', 'tables'], default=[])
        return safe_normalize_collection(tbls)

    @classmethod
    def get_formulas(cls, question: Any) -> List[Any]:
        """Safely retrieves question formulas relation or list. Returns [] if missing."""
        forms = safe_getattr(question, ['formulas_rel', 'formulas'], default=[])
        return safe_normalize_collection(forms)

    @classmethod
    def to_dto(cls, question: Any) -> QuestionDTO:
        """Converts raw Question model instance into canonical QuestionDTO."""
        q_id = safe_getattr(question, ['id'], default=0)
        q_num = cls.get_question_number(question)
        q_text = cls.get_text(question)
        q_marks = cls.get_marks(question)
        q_bloom = cls.get_bloom(question)
        q_co = cls.get_co(question)
        q_po = cls.get_po(question)
        q_rubric = cls.get_rubric(question)

        figs = cls.get_figures(question)
        tbls = cls.get_tables(question)
        forms = cls.get_formulas(question)

        return QuestionDTO(
            id=q_id,
            number=q_num,
            text=q_text,
            marks=q_marks,
            bloom=q_bloom,
            co=q_co,
            po=q_po,
            rubric=q_rubric,
            figures=figs,
            tables=tbls,
            formulas=forms
        )
