import re
from typing import List, Dict, Any
from core.models import AnswerScript, AnswerSegment, Question

class ScriptSegmenter:
    """
    Parses OCR text of an AnswerScript and splits/matches content into AnswerSegments for each Question.
    """

    @staticmethod
    def segment_script(script: AnswerScript, ocr_text: str, ocr_confidence: float = 0.85) -> List[AnswerSegment]:
        """
        Segments script OCR text by matching question headers (e.g. Q1, Question 1, 1(a)) and creates AnswerSegments.
        """
        questions = script.examination.questions.all()
        created_segments = []

        if not questions.exists():
            return created_segments

        # Map questions by number pattern
        for q in questions:
            pattern = rf"(?:Q|Question|\b){re.escape(q.question_number)}[:\)\.\s\n]+(.*?)(?=(?:Q|Question|\b)\d+|$)"
            match = re.search(pattern, ocr_text, re.IGNORECASE | re.DOTALL)
            
            if match:
                extracted = match.group(1).strip()
            else:
                extracted = ocr_text.strip()

            segment, _ = AnswerSegment.objects.get_or_create(
                script=script,
                question=q,
                defaults={
                    'extracted_text': extracted,
                    'ocr_confidence': ocr_confidence
                }
            )
            if segment.extracted_text != extracted:
                segment.extracted_text = extracted
                segment.ocr_confidence = ocr_confidence
                segment.save()

            created_segments.append(segment)

        return created_segments
