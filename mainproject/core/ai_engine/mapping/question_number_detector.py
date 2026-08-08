"""
IntelliGrade Strict Student Question Header Detection Engine v3.0.
Rebuilds question boundary detection into a deterministic, multi-stage classifier.

ABSOLUTE RULES:
1. ONLY explicit question keywords (Q, Question, Answer to Question, Ans to Q, Solution to Question) can establish a question boundary.
2. Subpoints ((i), (ii), (iii), (a), (b), 1., 2., 1), 2), 1:, • 1) are strictly classified as SUBPOINT/LIST_ITEM/ENUMERATION and REJECTED.
3. OCR numbers, marks, sizes (3x3, 8-bit, 25 marks, 120, 1st, 2nd) are REJECTED.
4. Pages with no explicit heading NEVER default to Q1.
"""

import os
import re
import json
import cv2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple


class StudentQuestionHeadingDetector:
    """
    Scans page OCR text, line bounding boxes, and multi-line candidates for student answer headings.
    Primary Source of Truth for student script answer segment creation.
    """

    BENGALI_TO_ENG = {'১': '1', '২': '2', '৩': '3', '৪': '4', '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'}
    ROMAN_TO_INT = {'I': '1', 'II': '2', 'III': '3', 'IV': '4', 'V': '5', 'VI': '6', 'VII': '7', 'VIII': '8', 'IX': '9', 'X': '10'}

    # Academic metadata patterns (e.g. Course Outcomes, Program Outcomes, Bloom Taxonomy)
    ACADEMIC_METADATA_PATTERNS = [
        r'\bCO\s*[0-9]{1,2}\b',
        r'\bPO\s*[0-9]{1,2}\b',
        r'\bC\s*[1-6]\b',
        r'\bPLO\s*[0-9]{1,2}\b',
        r'\bCLO\s*[0-9]{1,2}\b',
    ]

    # Non-header unit & formula suppression patterns
    NON_HEADER_PATTERNS = [
        r'\b(?:mark|marks|full\s*marks|total\s*marks)\b',
        r'\b(?:hour|hours|hr|hrs|min|minutes|sec|seconds)\b',
        r'\b(?:202[0-9]|19[0-9]{2})\b',                 # Years
        r'\b(?:fig|figure|table|page)\s*[0-9]{1,2}\b',    # Figure 3, Table 3, Page 3
        r'\b[0-9]{1,2}\s*[\*\x78\xd7]\s*[0-9]{1,2}\b',       # Matrix 3x3
        r'\b[0-9]{1,2}\s*\-\s*bit\b',                  # 8-bit
        r'\b(?:1st|2nd|3rd|[0-9]{1,2}th)\b',            # 1st, 2nd, 3rd
        r'[\+\-\*\/\=\>\<\^\%]',                        # Math equations: 3 + 5 = 8
        r'\[\s*[0-9]{1,2}\s*\]',                        # Bracketed marks: [25]
        r'\b[0-9]{3,}\b'                                # Large numbers like 120, 2026
    ]

    # Reference phrases (NOT answer headers)
    REFERENCE_PATTERNS = [
        r'\b(?:discussed|learned|shown|refer|see|given|stated|explained|derived)\s+(?:in|under|for|by)\s+(?:question|q)\s*[0-9]{1,2}\b',
        r'\b(?:question|q)\s*[0-9]{1,2}\s+(?:is|was|shows|explains|discusses|states)\b',
    ]

    # ABSOLUTELY INVALID QUESTION MARKERS — MUST NEVER START A QUESTION
    ROMAN_SUBPOINT_PATTERN = re.compile(
        r'^\s*[\(\[\{]?\s*(?:i|ii|iii|iv|v|vi|vii|viii|ix|x)\s*[\)\}\]\:\.\-]?\s*(?:$|\b|\s+[a-zA-Z])', re.IGNORECASE
    )
    LETTER_SUBPOINT_PATTERN = re.compile(
        r'^\s*[\(\[\{]?\s*[a-dA-D]\s*[\)\}\]\:\.\-]?\s*(?:$|\b|\s+[a-zA-Z])'
    )
    ORDINARY_NUMBERING_PATTERN = re.compile(
        r'^\s*(?:[\(\[\{]?\s*[0-9]{1,2}\s*[\)\}\]\:\.\-]|[\•\*\-]\s*[0-9]{1,2})\s*(?![a-zA-Z0-9\s]*\b(?:Ans|Question|Q|Solution|Soln)\b)', re.IGNORECASE
    )
    STEP_NUMBER_PATTERN = re.compile(
        r'^\s*(?:Step|Part|Point|Section|Item)\s*[0-9]{1,2}\b', re.IGNORECASE
    )

    # STRICT HEADING PATTERN RULES: REQUIRES EXPLICIT ANSWER-TO-QUESTION SIGNAL (STANDALONE Q1/Q2 DISABLED)
    HEADING_PATTERNS = [
        # CATEGORY 1: "Answer to Question 1", "Answer to Question No. 1", "Answer of Question No. 1", "Answer for Question 1", "Answer: Question 1", "Answer - Question 1"
        (re.compile(r'(?:^|\b)(?:Ans(?:wer)?|Solution|Soln)\b[\.\:\-\s]*(?:to|of|for|\:\s*|\-\s*|\—\s*)?\s*(?:the\s+)?Q(?:uestion)?[\.\#\-]?\s*(?:No|Number|\#)?[\.\:\-\s]*([0-9]{1,2}|[IVXLCDM]{1,4}|[১-৯]{1,2})\b', re.IGNORECASE), 100, "ANSWER_TO_QUESTION"),
        
        # CATEGORY 2: "Ans. to Q1", "Ans to Question 1", "Solution of Q1", "Soln to Q1", "Ans for Q1"
        (re.compile(r'(?:^|\b)(?:Ans|Soln)[\.\s]+(?:to|of|for)\s*Q\s*[\.\#\-]?\s*([0-9]{1,2}|[IVXLCDM]{1,4}|[১-৯]{1,2})\b', re.IGNORECASE), 95, "SOLUTION_HEADING"),
        
        # CATEGORY 3: "Question No. 1", "Question No 1", "Question No: 1", "Question #1", "Question Number 1"
        (re.compile(r'(?:^|\b)Q(?:uestion)?\s*(?:No|Number|\#)[\.\:\-\s]+([0-9]{1,2}|[IVXLCDM]{1,4}|[১-৯]{1,2})\b', re.IGNORECASE), 90, "QUESTION_HEADING"),
        (re.compile(r'(?:^|\b)(?:প্রশ্ন|উত্তর)\s*(?:নং)?[\.\:\-\s]*([১-৯]{1,2}|[0-9]{1,2})\b', re.IGNORECASE), 92, "QUESTION_HEADING"),

        # CATEGORY 4: "Question 1 Answer", "Question No. 1 Answer", "Q1 Answer", "Q.1 Answer", "Question 1:", "Q1:"
        (re.compile(r'(?:^|\b)Q(?:uestion)?[\.\#\-\s]?\s*([0-9]{1,2}|[IVXLCDM]{1,4})\s*[\:\-\s]\s*(?:Ans(?:wer)?|Solution)\b', re.IGNORECASE), 85, "QUESTION_ANSWER_HEADING"),
        (re.compile(r'(?:^|\b)Q(?:uestion)?[\.\#\-\s]?\s*([0-9]{1,2}|[IVXLCDM]{1,4})\s*(?:Ans(?:wer)?|Solution)\b', re.IGNORECASE), 85, "QUESTION_ANSWER_HEADING"),
        (re.compile(r'(?:^|\b)Q(?:uestion)?\s*([0-9]{1,2}|[IVXLCDM]{1,4})\s*[\:]', re.IGNORECASE), 85, "QUESTION_ANSWER_HEADING"),
    ]

    # OCR TYPO REPAIR PATTERNS (Q I -> Q1, Q l -> Q1, Question l -> Question 1)
    OCR_TYPO_HEADING_PATTERNS = [
        (re.compile(r'(?:^|\b)Q(?:uestion)?\s*(?:No|Number|\#)?[\.\:\-\s]+[lI]\b', re.IGNORECASE), 85, "QUESTION_HEADING_OCR_TYPO", "1"),
        (re.compile(r'(?:^|\b)(?:Ans(?:wer)?|Solution|Soln)\s+(?:to|of|for)\s+Q(?:uestion)?\s*(?:No|Number|\#)?[\.\:\-\s]+[lI]\b', re.IGNORECASE), 95, "ANSWER_TO_QUESTION_OCR_TYPO", "1")
    ]

    @classmethod
    def normalize_ocr_text(cls, text: str) -> str:
        """Normalizes OCR typos, spaces, dash forms, and punctuation for consistent pattern matching."""
        if not text:
            return ""

        s = text.strip()
        s = re.sub(r'\bQuestion\s+No\s*\.\s*', 'Question No. ', s, flags=re.IGNORECASE)
        s = re.sub(r'\bQuestion\s+No\s*\:\s*', 'Question No: ', s, flags=re.IGNORECASE)
        s = re.sub(r'\bAns\s*\.\s*', 'Ans. ', s, flags=re.IGNORECASE)
        s = re.sub(r'[\—\–\−]', '-', s)
        s = re.sub(r'\s+', ' ', s)

        return s

    @classmethod
    def normalize_question_number(cls, raw_num: str) -> str:
        """Normalizes Bengali, Roman, OCR typos ('l', 'I'), or integer strings into clean standard integer string ('1', '2')."""
        if not raw_num:
            return ""
        clean = raw_num.strip().upper()
        if clean in ['L', 'I', 'L.']:
            return '1'
        if clean in cls.BENGALI_TO_ENG:
            return cls.BENGALI_TO_ENG[clean]
        if clean in cls.ROMAN_TO_INT:
            return cls.ROMAN_TO_INT[clean]

        clean_sub = re.sub(r'^(?:Q(?:UESTION)?|ANS(?:WER)?|SOLN|SOLUTION|NO|NUMBER)?[\.\:\-\#\s]*', '', clean)
        clean_num = re.sub(r'[^0-9A-ZA-Z]', '', clean_sub)
        if clean_num in ['L', 'I']:
            return '1'
        return clean_num if clean_num else clean

    @classmethod
    def is_roman_subpoint(cls, text: str) -> bool:
        return bool(cls.ROMAN_SUBPOINT_PATTERN.search(text))

    @classmethod
    def is_letter_subpoint(cls, text: str) -> bool:
        return bool(cls.LETTER_SUBPOINT_PATTERN.search(text))

    @classmethod
    def is_ordinary_numbering(cls, text: str) -> bool:
        return bool(cls.ORDINARY_NUMBERING_PATTERN.search(text))

    @classmethod
    def is_step_number(cls, text: str) -> bool:
        return bool(cls.STEP_NUMBER_PATTERN.search(text))

    @classmethod
    def is_academic_metadata(cls, text: str) -> bool:
        for pat in cls.ACADEMIC_METADATA_PATTERNS:
            if re.search(pat, text, re.IGNORECASE):
                return True
        return False

    @classmethod
    def is_non_header_number(cls, text: str) -> bool:
        line_lower = text.lower()
        for pat in cls.NON_HEADER_PATTERNS:
            if re.search(pat, line_lower):
                if re.search(r'\b(?:Ans(?:wer)?|Solution|Q(?:uestion)?\s*No)\b', text, re.IGNORECASE):
                    continue
                return True
        return False

    @classmethod
    def is_reference_phrase(cls, text: str) -> bool:
        for pat in cls.REFERENCE_PATTERNS:
            if re.search(pat, text, re.IGNORECASE):
                return True
        return False

    @classmethod
    def detect_explicit_question_heading(
        cls,
        text: str,
        ymin_pct: float = 0.0,
        stored_question_numbers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Dedicated heading classifier.
        Evaluates a candidate string and returns structured classification decision.
        """
        line_str = cls.normalize_ocr_text(text)
        if not line_str or len(line_str) > 140:
            return {
                'is_question_heading': False,
                'question_number': None,
                'heading_text': text,
                'confidence': 0.0,
                'heading_type': 'BODY_TEXT',
                'raw_text': text,
                'reason': 'TOO_LONG_OR_EMPTY'
            }

        # 1. Check Subpoint & Enumeration Rejections
        if cls.is_roman_subpoint(line_str):
            return {
                'is_question_heading': False,
                'question_number': None,
                'heading_text': line_str,
                'confidence': 0.99,
                'heading_type': 'SUBPOINT',
                'raw_text': text,
                'reason': 'ROMAN_SUBPOINT'
            }

        if cls.is_letter_subpoint(line_str):
            return {
                'is_question_heading': False,
                'question_number': None,
                'heading_text': line_str,
                'confidence': 0.99,
                'heading_type': 'SUBPOINT',
                'raw_text': text,
                'reason': 'LETTER_SUBPOINT'
            }

        if cls.is_step_number(line_str):
            return {
                'is_question_heading': False,
                'question_number': None,
                'heading_text': line_str,
                'confidence': 0.95,
                'heading_type': 'ENUMERATION',
                'raw_text': text,
                'reason': 'STEP_NUMBER'
            }

        if cls.is_ordinary_numbering(line_str):
            return {
                'is_question_heading': False,
                'question_number': None,
                'heading_text': line_str,
                'confidence': 0.98,
                'heading_type': 'LIST_ITEM',
                'raw_text': text,
                'reason': 'ORDINARY_NUMBERING'
            }

        if cls.is_academic_metadata(line_str):
            return {
                'is_question_heading': False,
                'question_number': None,
                'heading_text': line_str,
                'confidence': 0.95,
                'heading_type': 'BODY_TEXT',
                'raw_text': text,
                'reason': 'ACADEMIC_METADATA'
            }

        if cls.is_non_header_number(line_str):
            return {
                'is_question_heading': False,
                'question_number': None,
                'heading_text': line_str,
                'confidence': 0.95,
                'heading_type': 'BODY_TEXT',
                'raw_text': text,
                'reason': 'NON_HEADER_NUMBER'
            }

        if cls.is_reference_phrase(line_str):
            return {
                'is_question_heading': False,
                'question_number': None,
                'heading_text': line_str,
                'confidence': 0.90,
                'heading_type': 'BODY_TEXT',
                'raw_text': text,
                'reason': 'QUESTION_REFERENCE'
            }

        # 2. Check Explicit Pattern Matches
        valid_nums_clean = [cls.normalize_question_number(n) for n in stored_question_numbers] if stored_question_numbers else []

        # Standard explicit heading patterns
        for pattern, base_score, class_name in cls.HEADING_PATTERNS:
            match = pattern.search(line_str)
            if match:
                raw_extracted = match.group(0).strip()
                num_group = match.group(1).strip() if match.lastindex and match.group(1) else raw_extracted
                norm_num = cls.normalize_question_number(num_group)

                if not norm_num or not norm_num.isalnum():
                    continue

                if valid_nums_clean and norm_num not in valid_nums_clean:
                    return {
                        'is_question_heading': False,
                        'question_number': norm_num,
                        'heading_text': line_str,
                        'confidence': 0.0,
                        'heading_type': 'UNKNOWN',
                        'raw_text': text,
                        'reason': f'QUESTION_NOT_IN_EXAM ({valid_nums_clean})'
                    }

                spatial_bonus = 20 if ymin_pct <= 0.15 else (10 if ymin_pct <= 0.25 else (5 if ymin_pct <= 0.40 else 0))
                total_score = base_score + spatial_bonus
                final_conf = min(0.99, round(total_score / 120.0, 2))

                return {
                    'is_question_heading': True,
                    'question_number': norm_num,
                    'heading_text': line_str,
                    'confidence': final_conf,
                    'score': total_score,
                    'heading_type': class_name,
                    'raw_text': raw_extracted,
                    'reason': 'EXPLICIT_KEYWORD_MATCH'
                }

        # OCR Typo Repair fallback (e.g., Q I, Q l, Question No. l)
        for pattern, base_score, class_name, default_num in cls.OCR_TYPO_HEADING_PATTERNS:
            match = pattern.search(line_str)
            if match:
                raw_extracted = match.group(0).strip()
                norm_num = default_num
                if valid_nums_clean and norm_num not in valid_nums_clean:
                    continue

                total_score = base_score + (15 if ymin_pct <= 0.20 else 0)
                final_conf = min(0.95, round(total_score / 120.0, 2))

                return {
                    'is_question_heading': True,
                    'question_number': norm_num,
                    'heading_text': line_str,
                    'confidence': final_conf,
                    'score': total_score,
                    'heading_type': class_name,
                    'raw_text': raw_extracted,
                    'reason': 'OCR_TYPO_HEADING_MATCH'
                }

        return {
            'is_question_heading': False,
            'question_number': None,
            'heading_text': line_str,
            'confidence': 0.0,
            'heading_type': 'BODY_TEXT',
            'raw_text': text,
            'reason': 'NO_HEADING_PATTERN_MATCHED'
        }

    @classmethod
    def detect_questions_on_page(
        cls,
        ocr_raw_text: str,
        line_boxes: Optional[List[Dict[str, Any]]] = None,
        page_height: int = 1000,
        stored_question_numbers: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Scans a page's text lines and multi-line candidates for student-written answer headings.
        Invokes detect_explicit_question_heading for every candidate line.
        """
        detections = []
        if not ocr_raw_text:
            return detections

        lines = ocr_raw_text.splitlines()
        candidates = []

        # 1. Single-line candidates
        for idx, line in enumerate(lines):
            line_str = cls.normalize_ocr_text(line)
            if not line_str or len(line_str) > 140:
                continue

            ymin_pct = 0.0
            bbox = {}
            if line_boxes and idx < len(line_boxes):
                bbox = line_boxes[idx].get('bbox', {})
                ymin = bbox.get('ymin', bbox.get('y', 0))
                ymin_pct = (ymin / float(max(1, page_height))) if ymin > 1.0 else float(ymin)
            else:
                ymin_pct = idx / float(max(1, len(lines)))

            candidates.append({
                'text': line_str,
                'line_index': idx,
                'ymin_pct': round(ymin_pct, 2),
                'bbox': bbox,
                'is_multiline': False
            })

        # 2. 2-line multiline candidates in top 40%
        for i in range(len(candidates) - 1):
            c1 = candidates[i]
            c2 = candidates[i + 1]
            if c1['ymin_pct'] <= 0.40 and c2['line_index'] == c1['line_index'] + 1:
                combined_text = f"{c1['text']} {c2['text']}"
                candidates.append({
                    'text': combined_text,
                    'line_index': c1['line_index'],
                    'ymin_pct': c1['ymin_pct'],
                    'bbox': c1['bbox'],
                    'is_multiline': True
                })

        print(f"\n============================================================")
        print(f"QUESTION HEADER ANALYSIS LOG")
        print(f"============================================================")

        for cand in candidates:
            text = cand['text']
            ymin_pct = cand['ymin_pct']

            decision = cls.detect_explicit_question_heading(
                text=text,
                ymin_pct=ymin_pct,
                stored_question_numbers=stored_question_numbers
            )

            if decision['is_question_heading']:
                print(f"Candidate: '{text}'")
                print(f"  Position: Top {int(ymin_pct*100)}%")
                print(f"  Detected Question: Q{decision['question_number']}")
                print(f"  Classification: {decision['heading_type']}")
                print(f"  Score: {decision.get('score', 0)} (Conf: {decision['confidence']})")
                print(f"  Decision: ACCEPT -> Q{decision['question_number']}\n")

                detections.append({
                    'raw_text': decision['raw_text'],
                    'heading_text': text,
                    'normalized_number': decision['question_number'],
                    'confidence': decision['confidence'],
                    'score': decision.get('score', 0),
                    'line_index': cand['line_index'],
                    'ymin_pct': ymin_pct,
                    'bbox': cand['bbox'],
                    'classification': decision['heading_type'],
                    'method': decision['heading_type']
                })
            else:
                print(f"Candidate: '{text}' | Classification: {decision['heading_type']} | Decision: REJECT — {decision['reason']}")

        return detections

    @classmethod
    def detect_top_region_vision(
        cls,
        image_input: Any,
        ai_provider: Optional[Any] = None,
        stored_question_numbers: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Vision Model Fallback for top 35% region of student answer page image.
        Crops top region, extracts text via vision provider, and evaluates explicit question headings.
        Guarantees subpoints ((i), (ii), (iii), (a), 1.) are strictly rejected.
        Returns normalized dictionary if an explicit question heading is detected, or None.
        """
        try:
            top_crop = None
            if isinstance(image_input, np.ndarray):
                h, w = image_input.shape[:2]
                top_crop = image_input[0:int(h * 0.35), 0:w]
            elif isinstance(image_input, str) and os.path.exists(image_input):
                bgr = cv2.imread(image_input)
                if bgr is not None:
                    h, w = bgr.shape[:2]
                    top_crop = bgr[0:int(h * 0.35), 0:w]

            if top_crop is None:
                return None

            img_bytes = None
            success, buf = cv2.imencode('.jpg', top_crop)
            if success:
                img_bytes = buf.tobytes()

            if not img_bytes:
                return None

            if not ai_provider:
                from core.ai_engine.providers.factory import AIProviderFactory
                ai_provider = AIProviderFactory.get_provider()

            ocr_text = ""
            if hasattr(ai_provider, 'extract_ocr_text'):
                try:
                    ocr_text = ai_provider.extract_ocr_text(img_bytes)
                except Exception as e:
                    print(f"[QUESTION HEADER VISION WARNING] Vision extract_ocr_text failed: {e}")

            if not ocr_text and hasattr(ai_provider, 'generate_completion'):
                try:
                    prompt = "Extract student answer heading at top of image (e.g. 'Answer to Question No. 3', 'Q1'). Do not include subpoints (i, ii, a, b)."
                    ocr_text = ai_provider.generate_completion(prompt)
                except Exception:
                    pass

            if ocr_text:
                for line in ocr_text.splitlines():
                    det = cls.detect_explicit_question_heading(
                        text=line,
                        ymin_pct=0.05,
                        stored_question_numbers=stored_question_numbers
                    )
                    if det and det.get('is_question_heading'):
                        return {
                            'detected': True,
                            'raw_text': det['raw_text'],
                            'heading_text': det['heading_text'],
                            'normalized_number': det['question_number'],
                            'confidence': det['confidence'],
                            'heading_type': 'VISION_TOP_REGION',
                            'classification': 'VISION_TOP_REGION',
                            'method': 'VISION_TOP_REGION',
                            'bbox': {}
                        }
        except Exception as e:
            print(f"[QUESTION HEADER VISION WARNING] Vision detector failed: {e}")

        return None
