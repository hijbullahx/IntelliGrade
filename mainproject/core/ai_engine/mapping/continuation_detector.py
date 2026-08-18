"""
IntelliGrade Continuation Detector Module v4.0.
Determines whether an unlabelled page is a continuation of the previous answer page
based on explicit sentence flow, text continuity, semantic overlap, and previous page confidence.
"""

from typing import List, Dict, Any, Optional

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
        mid_sentence = bool(prev_clean and not prev_clean.endswith(('.', '?', '!', '}', ')', ']')))

        # Check leading characters on current page (lowercase, math operator, or subpoint)
        leading_continuation = bool(curr_clean and (
            curr_clean[0].islower() or
            curr_clean[0] in ['=', '+', '-', '*', '/'] or
            curr_clean.startswith(('(i)', '(ii)', '(iii)', '(a)', '(b)', '1.', '2.'))
        ))

        # Check common word overlap (jaccard similarity between page ends/starts)
        prev_words = set(prev_clean.lower().split()[-30:]) if prev_clean else set()
        curr_words = set(curr_clean.lower().split()[:30]) if curr_clean else set()
        common_words = prev_words.intersection(curr_words) - {'the', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'are'}

        if mid_sentence and leading_continuation:
            return {'is_continuation': True, 'confidence': 0.92, 'reason': 'STRONG_TEXT_FLOW_CONTINUATION'}

        if mid_sentence or leading_continuation or len(common_words) >= 2:
            return {'is_continuation': True, 'confidence': 0.85, 'reason': 'TEXT_FLOW_CONTINUATION'}

        # Default sequential page without clear text flow continuity markers
        return {'is_continuation': False, 'confidence': 0.45, 'reason': 'WEAK_CONTINUATION_NO_FLOW_EVIDENCE'}

    @classmethod
    def is_continuation_page(
        cls,
        prev_page_text: str,
        current_page_text: str,
        current_has_new_header: bool
    ) -> bool:
        res = cls.evaluate_continuation(prev_page_text, current_page_text, current_has_new_header)
        return res['is_continuation'] and res['confidence'] >= 0.70
