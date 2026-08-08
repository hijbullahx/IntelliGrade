"""
IntelliGrade Continuation Detector Module v3.0.
Determines whether an unlabelled page is a continuation of the previous answer page
based on absence of new question headers, sentence flow, text continuity, and previous page confidence.
"""

from typing import List, Dict, Any

class ContinuationDetector:
    """
    Analyzes page continuity between sequential script pages.
    """

    @classmethod
    def evaluate_continuation(
        cls,
        prev_page_text: str,
        current_page_text: str,
        current_has_new_header: bool,
        prev_page_conf: float = 0.90
    ) -> Dict[str, Any]:
        """
        Evaluates whether current page is a continuation of the previous page's answer.
        Returns dictionary with 'is_continuation', 'confidence', and 'reason'.
        """
        if current_has_new_header:
            return {'is_continuation': False, 'confidence': 0.0, 'reason': 'NEW_QUESTION_HEADER_PRESENT'}

        if prev_page_conf < 0.70:
            return {'is_continuation': False, 'confidence': 0.30, 'reason': 'PREVIOUS_PAGE_CONFIDENCE_LOW'}

        if not current_page_text or len(current_page_text.strip()) < 10:
            return {'is_continuation': True, 'confidence': 0.85, 'reason': 'EMPTY_OR_SHORT_PAGE_CONTINUATION'}

        prev_clean = (prev_page_text or "").strip()
        curr_clean = current_page_text.strip()

        # Check trailing sentence ending on previous page (no terminal punctuation)
        mid_sentence = prev_clean and not prev_clean.endswith(('.', '?', '!', '}', ')', ']'))

        # Check leading characters on current page (lowercase, math operator, or subpoint)
        leading_continuation = curr_clean and (
            curr_clean[0].islower() or
            curr_clean[0] in ['=', '+', '-', '*', '/'] or
            curr_clean.startswith(('(i)', '(ii)', '(iii)', '(a)', '(b)', '1.', '2.'))
        )

        if mid_sentence or leading_continuation:
            conf = 0.91 if (mid_sentence and leading_continuation) else 0.85
            return {'is_continuation': True, 'confidence': conf, 'reason': 'STRONG_TEXT_FLOW_CONTINUATION'}

        return {'is_continuation': True, 'confidence': 0.78, 'reason': 'SEQUENTIAL_PAGE_NO_NEW_HEADER'}

    @classmethod
    def is_continuation_page(
        cls,
        prev_page_text: str,
        current_page_text: str,
        current_has_new_header: bool
    ) -> bool:
        res = cls.evaluate_continuation(prev_page_text, current_page_text, current_has_new_header)
        return res['is_continuation']
