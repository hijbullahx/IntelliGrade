"""
IntelliGrade Question Number Detector Module.
Detects handwritten/OCR question headers across page bounding boxes and text blocks.
Supports English, Bengali, Roman numerals, and position/layout analysis.
"""

import re
from typing import List, Dict, Any, Optional, Tuple

class QuestionNumberDetector:
    """
    Scans page text and OCR bounding boxes to locate handwritten question headers.
    Returns normalized question numbers, raw text matches, bounding boxes, and confidence scores.
    """

    # Comprehensive multi-lingual question header regex patterns
    PATTERNS = [
        # Explicit Q headers: Q1, Q.1, Q-1, Q#1, Question 1, Ans 1, Answer 1, Q No 1
        (r'(?:^|\b)(?:Q(?:uestion)?|Ans(?:wer)?|Q\s*No)\s*[\.\#\-]?\s*([0-9]{1,2}|[A-Za-z])(?:\s*[\.\:\-\)])?', 0.95),
        
        # Parenthesized or dotted numbers at line start: (1), (2), 1., 2., 1), 2)
        (r'^\s*[\(\[\{]?\s*([0-9]{1,2})\s*[\)\}\]\:\.\-]\s*', 0.88),

        # Bengali Question headers: প্রশ্ন ১, উত্তর ১, ১., ১)
        (r'(?:^|\b)(?:প্রশ্ন|উত্তর)?\s*([১-৯]{1,2})\s*[\.\:\-\)]?', 0.92),

        # Roman Numerals: Q.I, Q.IV, (III), Ans IV
        (r'(?:^|\b)(?:Q(?:uestion)?|Ans(?:wer)?)?\s*[\.\#\-]?\s*([IVXLCDM]{1,4})\s*[\.\:\-\)]?', 0.85),
    ]

    BENGALI_TO_ENG = {'১': '1', '২': '2', '৩': '3', '৪': '4', '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'}
    ROMAN_TO_INT = {'I': '1', 'II': '2', 'III': '3', 'IV': '4', 'V': '5', 'VI': '6', 'VII': '7', 'VIII': '8', 'IX': '9', 'X': '10'}

    @classmethod
    def normalize_question_number(cls, raw_num: str) -> str:
        """Converts raw Bengali, Roman, or formatted strings into standard string integer ('1', '2')."""
        clean = raw_num.strip().upper()
        if clean in cls.BENGALI_TO_ENG:
            return cls.BENGALI_TO_ENG[clean]
        if clean in cls.ROMAN_TO_INT:
            return cls.ROMAN_TO_INT[clean]
        
        # Strip extraneous punctuation
        clean_num = re.sub(r'[^0-9A-Za-z]', '', clean)
        return clean_num if clean_num else raw_num

    @classmethod
    def detect_questions_on_page(cls, ocr_raw_text: str, line_boxes: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Scans a page's text lines and bounding boxes for question headers.
        Returns a list of detection dicts:
        {
          'raw_text': 'Q.1',
          'normalized_number': '1',
          'confidence': 0.95,
          'line_index': 0,
          'bbox': [ymin, xmin, ymax, xmax]
        }
        """
        detections = []
        if not ocr_raw_text:
            return detections

        lines = ocr_raw_text.splitlines()

        for idx, line in enumerate(lines):
            line_str = line.strip()
            if not line_str:
                continue

            for pattern, base_conf in cls.PATTERNS:
                match = re.search(pattern, line_str, re.IGNORECASE | re.MULTILINE)
                if match:
                    raw_extracted = match.group(0).strip()
                    num_group = match.group(1).strip()
                    norm_num = cls.normalize_question_number(num_group)

                    # Layout Bonus: Higher confidence if located in top 3 lines or left-aligned
                    layout_bonus = 0.04 if idx <= 2 else 0.0

                    bbox = {}
                    if line_boxes and idx < len(line_boxes):
                        bbox = line_boxes[idx].get('bbox', {})

                    detections.append({
                        'raw_text': raw_extracted,
                        'normalized_number': norm_num,
                        'confidence': min(0.99, round(base_conf + layout_bonus, 2)),
                        'line_index': idx,
                        'bbox': bbox
                    })
                    break  # Use first matching pattern for this line

        return detections
