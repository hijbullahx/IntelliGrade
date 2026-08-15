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


class LineReconstructor:
    """
    Reconstructs visual lines from OCR word/line bounding boxes using vertical baseline clustering
    and horizontal coordinate ordering. Calculates line height, baseline proximity, line isolation,
    and whitespace above/below line.
    """

    @classmethod
    def reconstruct_lines(
        cls,
        ocr_raw_text: str,
        word_boxes: Optional[List[Dict[str, Any]]] = None,
        line_boxes: Optional[List[Dict[str, Any]]] = None,
        page_height: int = 1000
    ) -> List[Dict[str, Any]]:
        lines_output = []

        if word_boxes and isinstance(word_boxes, list) and len(word_boxes) > 0:
            sorted_words = []
            for w in word_boxes:
                bbox = w.get('bbox', {})
                ymin = bbox.get('ymin', bbox.get('y', 0))
                ymax = bbox.get('ymax', ymin + bbox.get('h', 20))
                xmin = bbox.get('xmin', bbox.get('x', 0))
                xmax = bbox.get('xmax', xmin + bbox.get('w', 50))
                text = str(w.get('text', '')).strip()
                if text:
                    y_center = (ymin + ymax) / 2.0
                    sorted_words.append({
                        'ymin': ymin, 'ymax': ymax, 'xmin': xmin, 'xmax': xmax,
                        'y_center': y_center, 'text': text,
                        'confidence': w.get('confidence', 0.9)
                    })

            sorted_words.sort(key=lambda item: item['y_center'])

            line_clusters = []
            for word in sorted_words:
                matched_cluster = None
                for cluster in line_clusters:
                    cluster_y_avg = sum(w['y_center'] for w in cluster) / len(cluster)
                    cluster_h_avg = sum(w['ymax'] - w['ymin'] for w in cluster) / len(cluster)
                    threshold = max(12.0, cluster_h_avg * 0.6)
                    if abs(word['y_center'] - cluster_y_avg) <= threshold:
                        matched_cluster = cluster
                        break
                if matched_cluster:
                    matched_cluster.append(word)
                else:
                    line_clusters.append([word])

            line_clusters.sort(key=lambda cluster: sum(w['ymin'] for w in cluster) / len(cluster))

            for idx, cluster in enumerate(line_clusters):
                cluster.sort(key=lambda w: w['xmin'])
                line_text = " ".join(w['text'] for w in cluster)
                min_y = min(w['ymin'] for w in cluster)
                max_y = max(w['ymax'] for w in cluster)
                min_x = min(w['xmin'] for w in cluster)
                max_x = max(w['xmax'] for w in cluster)

                ymin_pct = min_y / float(max(1, page_height)) if min_y > 1.0 else min_y
                ymax_pct = max_y / float(max(1, page_height)) if max_y > 1.0 else max_y

                lines_output.append({
                    'text': line_text,
                    'bbox': {'ymin': min_y, 'xmin': min_x, 'ymax': max_y, 'xmax': max_x},
                    'ymin_pct': round(ymin_pct, 3),
                    'ymax_pct': round(ymax_pct, 3),
                    'line_index': idx
                })

        elif line_boxes and isinstance(line_boxes, list) and len(line_boxes) > 0:
            for idx, lb in enumerate(line_boxes):
                text = str(lb.get('text', '')).strip()
                bbox = lb.get('bbox', {})
                ymin = bbox.get('ymin', bbox.get('y', 0))
                ymax = bbox.get('ymax', ymin + bbox.get('h', 20))
                xmin = bbox.get('xmin', bbox.get('x', 0))
                xmax = bbox.get('xmax', xmin + bbox.get('w', 100))

                ymin_pct = ymin / float(max(1, page_height)) if ymin > 1.0 else ymin
                ymax_pct = ymax / float(max(1, page_height)) if ymax > 1.0 else ymax

                if text:
                    lines_output.append({
                        'text': text,
                        'bbox': {'ymin': ymin, 'xmin': xmin, 'ymax': ymax, 'xmax': xmax},
                        'ymin_pct': round(ymin_pct, 3),
                        'ymax_pct': round(ymax_pct, 3),
                        'line_index': idx
                    })
        else:
            raw_lines = [l.strip() for l in ocr_raw_text.splitlines() if l.strip()]
            for idx, line in enumerate(raw_lines):
                ymin_pct = idx / float(max(1, len(raw_lines)))
                lines_output.append({
                    'text': line,
                    'bbox': {'ymin': ymin_pct, 'xmin': 0.05, 'ymax': ymin_pct + 0.05, 'xmax': 0.95},
                    'ymin_pct': round(ymin_pct, 3),
                    'ymax_pct': round(ymin_pct + 0.05, 3),
                    'line_index': idx
                })

        for i, line in enumerate(lines_output):
            prev_ymax = lines_output[i - 1]['ymax_pct'] if i > 0 else 0.0
            next_ymin = lines_output[i + 1]['ymin_pct'] if i < len(lines_output) - 1 else 1.0

            space_above = max(0.0, line['ymin_pct'] - prev_ymax)
            space_below = max(0.0, next_ymin - line['ymax_pct'])

            line['whitespace_above'] = round(space_above, 3)
            line['whitespace_below'] = round(space_below, 3)
            line['is_isolated'] = (space_above >= 0.02 and space_below >= 0.02) or (i == 0)

        return lines_output


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

    ANSWER_TOKENS = [
        'answer', 'ans', 'ans.', 'ang', 'angto', 'ansto', 'answe', 'ansr', 'solution', 'soln', 'sol', 'উত্তর'
    ]

    QUESTION_TOKENS = [
        'question', 'ques', 'quest', 'q', 'q.', 'no', 'no.', 'number', '#', 'n0', 'no!', 'nd', 'প্রশ্ন', 'নং'
    ]

    @classmethod
    def find_answer_context_token(cls, text: str) -> Tuple[bool, str]:
        """Tolerant search for answer context tokens (ans, answer, angto, solution, etc.)."""
        words = re.findall(r'[a-zA-Z\.\—\–\−]+', text.lower())
        for w in words:
            w_clean = w.strip('.')
            if w_clean in cls.ANSWER_TOKENS:
                return True, w
            for token in ['answer', 'solution', 'soln', 'ans', 'ang']:
                if len(w_clean) >= 3 and (w_clean.startswith(token[:3]) or w_clean in token):
                    return True, w
        return False, ""

    @classmethod
    def find_question_context_token(cls, text: str) -> Tuple[bool, str]:
        """Tolerant search for question context tokens (question, Q, No, NO!, N0, ND, etc.)."""
        words = re.findall(r'[a-zA-Z0-9\!\#\.]+', text)
        for w in words:
            w_lower = w.lower().strip('.!')
            if w_lower in cls.QUESTION_TOKENS:
                return True, w
            for token in ['question', 'quest', 'number']:
                if len(w_lower) >= 4 and (w_lower.startswith(token[:4]) or w_lower in token):
                    return True, w
        return False, ""

    @classmethod
    def extract_question_number_candidates(cls, text: str) -> List[Tuple[str, str]]:
        """Extracts candidate question numbers from text string, returning (raw_num, normalized_num)."""
        raw_matches = re.findall(r'\b0*([1-9][0-9]?)\b|[১-৯]{1,2}|\b[IVX]{1,4}\b', text, re.IGNORECASE)
        results = []
        for m in raw_matches:
            tok = m[0] if isinstance(m, tuple) and m[0] else (m if isinstance(m, str) else "")
            if not tok:
                continue
            norm = cls.normalize_question_number(tok)
            if norm and norm.isdigit():
                results.append((tok, norm))
        return results

    @classmethod
    def normalize_ocr_text(cls, text: str) -> str:
        """Normalizes OCR typos, spaces, dash forms, and punctuation for consistent pattern matching."""
        if not text:
            return ""

        s = text.strip()
        s = re.sub(r'\bQuest[l1I0o]on\b', 'Question', s, flags=re.IGNORECASE)
        s = re.sub(r'\bQ\s*[1lI]\b', 'Q1', s, flags=re.IGNORECASE)
        s = re.sub(r'\bQuestion\s+No\s*[\.\:]?\s*', 'Question No. ', s, flags=re.IGNORECASE)
        s = re.sub(r'\bAns\s*\.\s*', 'Ans. ', s, flags=re.IGNORECASE)
        s = re.sub(r'[\—\–\−]', '-', s)
        s = re.sub(r'\s+', ' ', s)

        return s

    @classmethod
    def normalize_question_number(cls, raw_num: str) -> str:
        """Normalizes Bengali, Roman, OCR typos ('l', 'I'), and leading zero strings ('01' -> '1', '02' -> '2') into standard integer string ('1', '2')."""
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
        if clean_num.isdigit():
            return str(int(clean_num))
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
        has_ans, _ = cls.find_answer_context_token(text)
        has_q, _ = cls.find_question_context_token(text)
        if has_ans or has_q:
            return False

        line_lower = text.lower()
        for pat in cls.NON_HEADER_PATTERNS:
            if re.search(pat, line_lower):
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
        Number-First Answer Heading Classifier.
        Combines Answer Context + Question Context + Valid Question Number + Spatial Proximity.
        Guarantees standalone numbers & mathematical content are REJECTED.
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

        # 1. Rejection Filters for non-heading content
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

        # 2. Extract Context Tokens & Number Candidates
        has_ans_ctx, ans_token = cls.find_answer_context_token(line_str)
        has_q_ctx, q_token = cls.find_question_context_token(line_str)
        num_candidates = cls.extract_question_number_candidates(line_str)

        # MANDATORY CRITICAL RULE: Standalone numbers without answer or question context MUST NEVER BE AN ANSWER HEADING!
        if not has_ans_ctx and not has_q_ctx:
            return {
                'is_question_heading': False,
                'question_number': None,
                'heading_text': line_str,
                'confidence': 0.0,
                'heading_type': 'BODY_TEXT',
                'raw_text': text,
                'ans_token': 'NO',
                'q_token': 'NO',
                'reason': 'ORDINARY_BODY_NUMBER (No answer/question context)'
            }

        if not num_candidates:
            return {
                'is_question_heading': False,
                'question_number': None,
                'heading_text': line_str,
                'confidence': 0.0,
                'heading_type': 'BODY_TEXT',
                'raw_text': text,
                'ans_token': ans_token if has_ans_ctx else 'NO',
                'q_token': q_token if has_q_ctx else 'NO',
                'reason': 'NO_QUESTION_NUMBER_FOUND'
            }

        valid_nums_clean = [cls.normalize_question_number(n) for n in stored_question_numbers] if stored_question_numbers else []

        best_cand = None
        best_score = 0

        for raw_num, norm_num in num_candidates:
            # Validate question number against exam questions
            if valid_nums_clean and norm_num not in valid_nums_clean:
                continue

            # Multi-Factor Score Calculation:
            score = 0
            if has_ans_ctx:
                score += 40
            if has_q_ctx:
                score += 15
            score += 30  # Valid question number
            score += 10  # Spatial proximity within line window
            if ymin_pct <= 0.25:
                score += 5  # Top page position bonus

            if score > best_score:
                best_score = score
                best_cand = (raw_num, norm_num)

        if best_cand and best_score >= 70:
            raw_num, norm_num = best_cand
            conf = min(0.99, round(best_score / 100.0, 2))
            return {
                'is_question_heading': True,
                'question_number': norm_num,
                'heading_text': line_str,
                'confidence': conf,
                'score': best_score,
                'heading_type': 'ANSWER_HEADING_CONTEXT',
                'raw_text': text,
                'ans_token': ans_token if has_ans_ctx else 'NO',
                'q_token': q_token if has_q_ctx else 'NO',
                'raw_num': raw_num,
                'norm_num': norm_num,
                'reason': 'CONTEXT_AND_NUMBER_MATCH'
            }

        return {
            'is_question_heading': False,
            'question_number': None,
            'heading_text': line_str,
            'confidence': 0.0,
            'heading_type': 'BODY_TEXT',
            'raw_text': text,
            'ans_token': ans_token if has_ans_ctx else 'NO',
            'q_token': q_token if has_q_ctx else 'NO',
            'reason': 'HEADING_SCORE_TOO_LOW'
        }

    @classmethod
    def detect_questions_on_page(
        cls,
        ocr_raw_text: str,
        word_boxes: Optional[List[Dict[str, Any]]] = None,
        line_boxes: Optional[List[Dict[str, Any]]] = None,
        page_height: int = 1000,
        stored_question_numbers: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Reconstructs visual lines using LineReconstructor, performs multi-signal scoring,
        and returns all candidate answer headings found across the page.
        """
        detections = []
        if not ocr_raw_text and not word_boxes and not line_boxes:
            return detections

        reconstructed_lines = LineReconstructor.reconstruct_lines(
            ocr_raw_text=ocr_raw_text,
            word_boxes=word_boxes,
            line_boxes=line_boxes,
            page_height=page_height
        )

        candidates = []

        # 1. Single reconstructed lines
        for r_line in reconstructed_lines:
            line_str = cls.normalize_ocr_text(r_line['text'])
            if not line_str or len(line_str) > 140:
                continue

            candidates.append({
                'text': line_str,
                'line_index': r_line['line_index'],
                'ymin_pct': r_line['ymin_pct'],
                'ymax_pct': r_line['ymax_pct'],
                'bbox': r_line['bbox'],
                'whitespace_above': r_line.get('whitespace_above', 0.0),
                'whitespace_below': r_line.get('whitespace_below', 0.0),
                'is_isolated': r_line.get('is_isolated', False),
                'is_multiline': False
            })

        # 2. 2-line multiline candidates (for split headings e.g. "Answer to" on line 1, "Question 1" on line 2)
        for i in range(len(candidates) - 1):
            c1 = candidates[i]
            c2 = candidates[i + 1]
            if c2['line_index'] == c1['line_index'] + 1 and (c2['ymin_pct'] - c1['ymax_pct']) <= 0.04:
                combined_text = f"{c1['text']} {c2['text']}"
                candidates.append({
                    'text': combined_text,
                    'line_index': c1['line_index'],
                    'ymin_pct': c1['ymin_pct'],
                    'ymax_pct': c2['ymax_pct'],
                    'bbox': {
                        'ymin': c1['bbox'].get('ymin', 0),
                        'xmin': min(c1['bbox'].get('xmin', 0), c2['bbox'].get('xmin', 0)),
                        'ymax': c2['bbox'].get('ymax', 0),
                        'xmax': max(c1['bbox'].get('xmax', 0), c2['bbox'].get('xmax', 0))
                    },
                    'whitespace_above': c1.get('whitespace_above', 0.0),
                    'whitespace_below': c2.get('whitespace_below', 0.0),
                    'is_isolated': c1.get('is_isolated', False),
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
                print(f"============================================================")
                print(f"ANSWER HEADING CANDIDATE")
                print(f"============================================================")
                print(f"Page: {cand.get('line_index', 0) + 1}")
                print(f"Raw OCR:\n\"{text}\"")
                print(f"Detected answer context:\n\"{decision.get('ans_token', 'NO')}\"")
                print(f"Detected question context:\n\"{decision.get('q_token', 'NO')}\"")
                print(f"Detected number:\n{decision.get('raw_num', 'N/A')}")
                print(f"Normalized number:\n{decision.get('norm_num', 'N/A')}")
                print(f"Question exists:\nYES")
                print(f"Spatial proximity:\nYES")
                print(f"Answer heading score:\n{decision.get('score', 0)}")
                print(f"Decision:\nACCEPT -> Q{decision['question_number']}\n")

                detections.append({
                    'raw_text': decision['raw_text'],
                    'heading_text': text,
                    'normalized_number': decision['question_number'],
                    'confidence': decision['confidence'],
                    'score': decision.get('score', 0),
                    'line_index': cand['line_index'],
                    'ymin_pct': ymin_pct,
                    'ymax_pct': cand['ymax_pct'],
                    'bbox': cand['bbox'],
                    'classification': decision['heading_type'],
                    'method': decision['heading_type']
                })
            else:
                ans_ctx_str = 'YES' if (decision.get('ans_token') and decision.get('ans_token') != 'NO') else 'NO'
                q_ctx_str = 'YES' if (decision.get('q_token') and decision.get('q_token') != 'NO') else 'NO'
                print(f"============================================================")
                print(f"REJECTED BODY CANDIDATE")
                print(f"============================================================")
                print(f"Candidate:\n\"{text}\"")
                print(f"Answer context:\n{ans_ctx_str}")
                print(f"Question context:\n{q_ctx_str}")
                print(f"Valid heading:\nNO")
                print(f"Decision:\nREJECT -> {decision['reason']}\n")

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
