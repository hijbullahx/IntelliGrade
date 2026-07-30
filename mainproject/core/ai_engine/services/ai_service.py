from typing import Dict, Any, Optional, List
from core.ai_engine.providers.factory import AIProviderFactory
from core.ai_engine.ocr.engine import OCREngineManager
from core.ai_engine.layout.academic_layout import AcademicLayoutAnalyzer
from core.ai_engine.parser.academic_parser import AcademicDocumentParser
from core.ai_engine.routine_parser.routine_parser import RoutineParser
from core.ai_engine.question_parser.question_paper_parser import QuestionPaperParser
from core.ai_engine.course_outline_parser.outline_parser import CourseOutlineParser
from core.ai_engine.question_generator.generator import QuestionGenerator
from core.ai_engine.manual_builder.predictor import ManualQuestionAIPredictor
from core.ai_engine.evaluator.academic_evaluator import AcademicEvaluator
from core.ai_engine.confidence.confidence_engine import ConfidenceEngine
from core.ai_engine.retrieval.rag_retriever import RAGRetriever
from core.ai_engine.analytics.analytics_engine import AcademicAnalyticsEngine

class AIService:
    """
    Master AI Façade & Orchestrator for IntelliGrade.
    Connects all AI sub-packages cleanly into Django views and models.
    """

    def __init__(self):
        self.provider = AIProviderFactory.get_provider()
        self.ocr_manager = OCREngineManager()
        self.layout_analyzer = AcademicLayoutAnalyzer()
        self.doc_parser = AcademicDocumentParser()
        self.routine_parser = RoutineParser()
        self.qp_parser = QuestionPaperParser()
        self.outline_parser = CourseOutlineParser()
        self.question_generator = QuestionGenerator()
        self.manual_predictor = ManualQuestionAIPredictor()
        self.evaluator = AcademicEvaluator()
        self.rag_retriever = RAGRetriever()
        self.analytics_engine = AcademicAnalyticsEngine()

    def process_document_ocr(self, image_bytes: bytes) -> Dict[str, Any]:
        """Runs OCR + Layout Analysis + Academic Parser on document bytes."""
        ocr_result = self.ocr_manager.extract_text(image_bytes)
        parsed_clean_json = self.doc_parser.parse_document(ocr_result.get('text', ''))
        ocr_result['parsed_json'] = parsed_clean_json
        return ocr_result

    def parse_routine(self, document_text_or_bytes: Any) -> Dict[str, Any]:
        """Parses exam routine document into clean structured JSON."""
        return self.routine_parser.parse_routine(document_text_or_bytes)

    def parse_question_paper(self, examination: Any, document_text_or_bytes: Any) -> Dict[str, Any]:
        """Parses uploaded question paper document and automatically populates DB."""
        return self.qp_parser.parse_and_store_paper(examination, document_text_or_bytes)

    def parse_course_outline(self, doc_text_or_bytes: Any) -> Dict[str, Any]:
        """Extracts structured syllabus, CO/PO, and KPAs from Course Outline."""
        return self.outline_parser.parse_course_outline(doc_text_or_bytes)

    def generate_question(self, **kwargs) -> Dict[str, Any]:
        """Generates structured question, rubric, and model answer."""
        return self.question_generator.generate_question(**kwargs)

    def predict_question_metadata(self, question_text: str, max_marks: float = 10.0) -> Dict[str, Any]:
        """Predicts Bloom level, CO/PO, rubrics as teacher types."""
        return self.manual_predictor.predict_metadata(question_text, max_marks)

    def evaluate_student_script(
        self,
        question_id: Optional[int],
        question_text: str,
        rubric_criteria: str,
        student_answer: str,
        max_marks: float,
        expected_answer: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates a student script answer using AcademicEvaluator, RAG exemplars & active AI provider.
        """
        return self.evaluator.evaluate(
            question_id=question_id,
            question_text=question_text,
            rubric_criteria=rubric_criteria,
            student_answer=student_answer,
            max_marks=max_marks,
            expected_answer=expected_answer
        )

    def get_course_analytics(self, course_id: int) -> Dict[str, Any]:
        """Computes CO/PO attainment, difficulty, and AI accuracy metrics."""
        return self.analytics_engine.generate_course_analytics(course_id)
