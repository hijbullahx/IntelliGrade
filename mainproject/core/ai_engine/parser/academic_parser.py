import os
import json
from typing import Dict, Any, List
from django.conf import settings


class PipelineValidationError(Exception):
    """Custom exception raised when pipeline assertions or document quality checks fail."""
    pass


class AcademicParserService:
    """
    Academic Parser Service responsible for:
    1. Parsing structured academic questions, sub-parts, allocated marks, CO/PO mappings
    2. Associating extracted figures with specific questions using layout coordinates
    3. Enforcing strict fail-fast validation assertions before database commit
    """

    @staticmethod
    def associate_figures_with_questions(questions: List[Dict[str, Any]], figures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Maps figures to questions using spatial bounding box layout and page reading order.
        ENFORCES STRICT SINGLE-OWNERSHIP: Each figure belongs to ONLY ONE question (no duplicates across questions).
        """
        for q in questions:
            q['associated_figures'] = []

        if not figures or not questions:
            return questions

        claimed_figure_indices = set()

        for fig_idx, fig in enumerate(figures):
            fig_page = fig.get('page_number', 1)
            bbox = fig.get('bounding_box', [0, 0, 0, 0])
            fig_center_y = (bbox[1] + bbox[3]) / 2.0 if len(bbox) >= 4 else bbox[1]

            target_q_idx = None
            fig_q_num = fig.get('question_number')
            if fig_q_num:
                for idx, q in enumerate(questions):
                    if str(q.get('question_number', '')).strip().lower() == str(fig_q_num).strip().lower():
                        target_q_idx = idx
                        break

            # Task 6 Rule: Question.start_y <= Figure.center_y < NextQuestion.start_y
            if target_q_idx is None:
                page_q_list = [(idx, q) for idx, q in enumerate(questions) if q.get('page_number', 1) == fig_page or len(questions) == 1]
                if page_q_list:
                    for i, (q_idx, q_item) in enumerate(page_q_list):
                        q_start_y = q_item.get('start_y', i * (3500 // max(len(page_q_list), 1)))
                        next_q_start_y = page_q_list[i+1][1].get('start_y', 99999) if i + 1 < len(page_q_list) else 99999
                        if q_start_y <= fig_center_y < next_q_start_y:
                            target_q_idx = q_idx
                            break
                    if target_q_idx is None:
                        # Nearest preceding question on same page
                        target_q_idx = page_q_list[0][0]

            if target_q_idx is not None and fig_idx not in claimed_figure_indices:
                claimed_figure_indices.add(fig_idx)
                questions[target_q_idx]['associated_figures'].append(fig)

        return questions

    @classmethod
    def validate_and_parse(
        cls,
        ocr_result: Dict[str, Any],
        graphics_result: Dict[str, Any],
        ai_response_data: Dict[str, Any],
        min_ocr_chars: int = 50
    ) -> Dict[str, Any]:
        """
        Executes strict fail-fast validation assertions.
        If ANY validation assertion fails, raises PipelineValidationError to abort transaction.
        """
        ocr_text = ocr_result.get('text', '').strip()
        char_count = len(ocr_text)

        # Assertion 1: OCR Character Count Validation
        if char_count < min_ocr_chars:
            raise PipelineValidationError(
                f"[STRICT PIPELINE FAILURE] OCR Quality Failure: Extracted text length ({char_count} chars) "
                f"is below required minimum ({min_ocr_chars} chars). Document scan aborted."
            )

        extracted_questions = ai_response_data.get('questions', [])
        if not extracted_questions:
            raise PipelineValidationError(
                "[STRICT PIPELINE FAILURE] Question Parser Failure: Zero academic questions were extracted by the AI Engine."
            )

        extracted_figures = graphics_result.get('figures', [])

        # Assertion 2: Figure File Existence Validation
        for fig in extracted_figures:
            img_path = os.path.join(settings.MEDIA_ROOT, fig.get('image_path', ''))
            if fig.get('image_path') and not os.path.exists(img_path):
                raise PipelineValidationError(
                    f"[STRICT PIPELINE FAILURE] Figure Storage Failure: Extracted image file '{img_path}' was not persisted to disk."
                )

        # Associate figures with questions
        parsed_questions = cls.associate_figures_with_questions(extracted_questions, extracted_figures)

        return {
            "parsed_questions": parsed_questions,
            "figures": extracted_figures,
            "ocr_text": ocr_text,
            "ocr_confidence": ocr_result.get('confidence', 0.0),
            "ocr_engine": ocr_result.get('engine', 'Unknown'),
            "total_pages": graphics_result.get('total_pages', 1),
            "dom_elements": graphics_result.get('dom_elements', [])
        }
