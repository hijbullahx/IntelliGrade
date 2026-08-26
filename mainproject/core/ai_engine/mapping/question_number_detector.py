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

    BENGALI_TO_ENG = {'০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4', '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'}
    ROMAN_TO_INT = {
        'I': '1', 'II': '2', 'III': '3', 'IV': '4', 'V': '5', 'VI': '6', 'VII': '7', 'VIII': '8', 'IX': '9', 'X': '10',
        'XI': '11', 'XII': '12', 'XIII': '13', 'XIV': '14', 'XV': '15', 'XVI': '16', 'XVII': '17', 'XVIII': '18', 'XIX': '19', 'XX': '20'
    }

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

    # Cover page and exam metadata keywords
    COVER_PAGE_KEYWORDS = [
        'student name', 'name of student', 'student id', 'roll no', 'roll number', 'id no', 'id number',
        'registration no', 'reg no', 'course code', 'course title', 'semester', 'department',
        'examination', 'midterm exam', 'final exam', 'quiz', 'assigned faculty', 'instructor',
        'section', 'batch', 'session', 'date of exam', 'total marks', 'iubat', 'university', 'college'
    ]

    # ABSOLUTELY INVALID QUESTION MARKERS — MUST NEVER START A QUESTION
    ROMAN_SUBPOINT_PATTERN = re.compile(
        r'^\s*[\(\[\{]?\s*(?:i|ii|iii|iv|v|vi|vii|viii|ix|x)\s*[\)\}\]\:\.\-]?\s*(?:$|\b|\s+[a-zA-Z0-9])', re.IGNORECASE
    )
    LETTER_SUBPOINT_PATTERN = re.compile(
        r'^\s*[\(\[\{]?\s*[a-dA-D]\s*[\)\}\]\:\.\-]?\s*(?:$|\b|\s+[a-zA-Z0-9])'
    )
    ORDINARY_NUMBERING_PATTERN = re.compile(
        r'^\s*(?:[\(\[\{]?\s*[0-9]{1,2}\s*[\)\}\]\:\.\-]|[\•\*\-]\s*[0-9]{1,2})\s*(?![a-zA-Z0-9\s]*\b(?:Ans|Question|Q|Solution|Soln)\b)', re.IGNORECASE
    )
    STEP_NUMBER_PATTERN = re.compile(
        r'^\s*(?:Step|Part|Point|Section|Item)\s*[0-9]{1,2}\b', re.IGNORECASE
    )

    # Universal student question heading patterns supporting ANY question count (1, 2, 5, 10, 20+)
    HEADING_REGEX_PATTERNS = [
        # "Ans to the question no. N" / "Answer to Question No. N" / "Ans to the qs no N" / "Ans to N" / "Answer to N" / "Ans to QN" / "Ans to Q.N" / "Ans - N" / "Ans: N" / "Answer No N" / "Ans. 1(a)"
        re.compile(
            r'(?:ans(?:wer)?|sol(?:ution)?|soln)\s*(?:to\s*(?:the\s*)?)?(?:(?:q(?:uestion|s)?\s*\.?\s*)?(?:no\s*\.?\s*)?)[:\-\.]?\s*([0-9]{1,2}(?:\s*[\(\[]?[a-zA-Z][\)\]]?)?|[০-৯]{1,2}(?:\s*[\(\[]?[a-zA-Z][\)\]]?)?|\b[ivxlcdm]{1,5}\b)',
            re.IGNORECASE
        ),
        # "Question No N" / "Q. No N" / "Q.N" / "QN" / "Question N" / "Q No: 5" / "Q 2(b)"
        re.compile(
            r'(?:q(?:uestion|s)?\s*\.?\s*(?:no\s*\.?\s*)?)[:\-\.]?\s*([0-9]{1,2}(?:\s*[\(\[]?[a-zA-Z][\)\]]?)?|[০-৯]{1,2}(?:\s*[\(\[]?[a-zA-Z][\)\]]?)?|\b[ivxlcdm]{1,5}\b)',
            re.IGNORECASE
        ),
        # "N নং প্রশ্নের উত্তর" / "N নং সমাধান" / "N নং উত্তর"
        re.compile(
            r'([0-9]{1,2}(?:\s*[\(\[]?[a-zA-Z][\)\]]?)?|[০-৯]{1,2}(?:\s*[\(\[]?[a-zA-Z][\)\]]?)?|\b[ivxlcdm]{1,5}\b)\s*(?:নং\s*)?(?:প্রশ্নের\s*)?(?:উত্তর|সমাধান)',
            re.IGNORECASE
        ),
        # "উত্তর নং N" / "প্রশ্ন নং N" / "সমাধান নং N" / "উত্তর: N"
        re.compile(
            r'(?:উত্তর|প্রশ্ন|সমাধান)\s*(?:নং\s*)?[:\-\.]?\s*([0-9]{1,2}(?:\s*[\(\[]?[a-zA-Z][\)\]]?)?|[০-৯]{1,2}(?:\s*[\(\[]?[a-zA-Z][\)\]]?)?|\b[ivxlcdm]{1,5}\b)',
            re.IGNORECASE
        ),
    ]
    SUBCONTINENTAL_HEADING_PATTERNS = HEADING_REGEX_PATTERNS

    NUMBER_WORDS = {
        'one': '1', 'two': '2', 'three': '3', 'four': '4', 'foutr': '4', 'five': '5',
        'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10'
    }

    ANSWER_TOKENS = [
        'answer', 'ans', 'ans.', 'ang', 'angto', 'ansto', 'answe', 'ansr', 'answ', 'solution', 'soln', 'sol',
        'ami', 'amilo', "am'", 'উত্তর', 'সমাধান'
    ]

    QUESTION_TOKENS = [
        'question', 'questions', 'ques', 'quest', 'qs', 'q', 'q.', 'no', 'no.', 'number', 'n0', 'no!', "no'", 'nd',
        '0n', '0no', '0nq', '9nd', '9no', "9'no", '9.no', 'q.no', "q'no", "q'nd", 'প্রশ্ন', 'নং'
    ]

    @classmethod
    def find_answer_context_token(cls, text: str) -> Tuple[bool, str]:
        """Tolerant search for answer context tokens (ans, answer, angto, solution, উত্তর, সমাধান, etc.)."""
        lower = text.lower()
        for tok in ['উত্তর', 'সমাধান', 'answer', 'ans.', 'ans', 'solution', 'soln', 'sol', 'angto', 'ansto', 'amilo', "am'"]:
            if tok in lower:
                return True, tok
        if re.search(r'\b(?:ans(?:wer)?s?|ang(?:to)?|ansto|amilo|am\'|sol(?:ution|n)?)\b', lower):
            return True, 'ans'
        words = re.findall(r'[\w\.\—\–\−]+', lower, re.UNICODE)
        for w in words:
            w_clean = w.strip('.')
            if w_clean in cls.ANSWER_TOKENS:
                return True, w
        return False, ""

    @classmethod
    def find_question_context_token(cls, text: str) -> Tuple[bool, str]:
        """Tolerant search for question context tokens (question, Q, Q1..QN, No, NO!, N0, ND, নং, প্রশ্ন, etc.)."""
        lower = text.lower()
        for tok in ['প্রশ্ন', 'নং', 'question', 'quest', 'ques', 'qs', 'q.', 'no.', 'number', '0nq', '0no', '0n', "q'no", "9'no", '9.no', 'q.no', 'no!', "no'"]:
            if tok in lower:
                return True, tok
        if re.search(r'\bQ\s*[\.\:\-\'\`]?\s*[0-9]', text, re.IGNORECASE):
            return True, 'Q'
        if re.search(r'\b(?:question|questions|quest|ques|qs|q\.|q|no\.|no|number|n0|no!|no\'|0nq|0no|0n|q[\.\'\`]?no|9[\.\'\`]?no)\b', lower):
            return True, 'Q'
        if re.search(r'#\s*[0-9]', text):
            return True, '#'
        if re.search(r'[@\xa9]\s*[\,\.\s]*no\b', lower):
            return True, 'No'
        words = re.findall(r'[\w\!\#\.\'\`\@]+', text, re.UNICODE)
        for w in words:
            w_lower = w.lower().strip('.!\'`')
            if w_lower in cls.QUESTION_TOKENS:
                return True, w
        return False, ""

    @classmethod
    def extract_question_number_candidates(cls, text: str) -> List[Tuple[str, str]]:
        """Extracts candidate question numbers from text string, returning (raw_num, normalized_num)."""
        results = []
        for pat in cls.SUBCONTINENTAL_HEADING_PATTERNS:
            for m in pat.finditer(text):
                if m and m.group(1):
                    raw = m.group(1).strip()
                    norm = cls.normalize_question_number(raw)
                    if norm and (raw, norm) not in results:
                        results.append((raw, norm))

        raw_matches = re.findall(r'\b0*([1-9][0-9]{0,1})\b|[১-৯][০-৯]?|\b[IVXLCDM]{1,6}\b', text, re.IGNORECASE)
        for m in raw_matches:
            tok = m[0] if isinstance(m, tuple) and m[0] else (m if isinstance(m, str) else "")
            if not tok:
                continue
            norm = cls.normalize_question_number(tok)
            if norm and (tok, norm) not in results:
                results.append((tok, norm))

        # Check for word numbers (e.g. "four", "three", "two", "one")
        for word, num_str in cls.NUMBER_WORDS.items():
            if re.search(rf'\b{word}\b', text, re.IGNORECASE):
                if (word, num_str) not in results:
                    results.append((word, num_str))

        # Check for OCR pipes/special characters like `0|` -> 1, `0I` -> 1
        pipe_match = re.search(r'0[\`\'\|\/I1]\b|0[\`\'\|\/I1](?=\s|$)', text)
        if pipe_match:
            results.append((pipe_match.group(0), '1'))

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
        """Normalizes Bengali, Roman, OCR typos ('l', 'I'), and leading zero strings ('01' -> '1', '02' -> '2') into standard integer/subpart string ('1', '2', '1(a)')."""
        if not raw_num:
            return ""
        clean = raw_num.strip().upper()
        if clean in ['L', 'I', 'L.']:
            return '1'

        # Translate all Bengali digits (handles single & multi-digit Bengali numbers: ১ -> 1, ১২ -> 12, ২০ -> 20)
        translated = "".join(cls.BENGALI_TO_ENG.get(ch, ch) for ch in clean)
        clean = translated

        # Check Roman numerals
        roman_key = re.sub(r'[\.\:\-\s]', '', clean)
        if roman_key in cls.ROMAN_TO_INT:
            return cls.ROMAN_TO_INT[roman_key]

        clean_sub = re.sub(r'^(?:Q(?:UESTION|S)?|ANS(?:WER)?|SOLN|SOLUTION|NO|NUMBER)?[\.\:\-\#\s]*', '', clean, flags=re.IGNORECASE)
        # Check if subpart format like 1(a), 1a, 2(b)
        subpart_m = re.match(r'^([0-9]{1,3})\s*[\(\[]?([A-Za-z])[\)\]]?$', clean_sub)
        if subpart_m:
            num_part = str(int(subpart_m.group(1)))
            letter_part = subpart_m.group(2).lower()
            return f"{num_part}({letter_part})"

        clean_num = re.sub(r'[^0-9A-ZA-Z]', '', clean_sub)
        if clean_num in ['L', 'I']:
            return '1'
        if clean_num.isdigit():
            return str(int(clean_num))
        return clean_num if clean_num else clean

    @classmethod
    def is_roman_subpoint(cls, text: str) -> bool:
        """Checks if text begins with a bracketed/standalone Roman subpoint like (i), (ii), (iii), [iv], i., ii."""
        clean = text.strip()
        if cls.ROMAN_SUBPOINT_PATTERN.match(clean):
            # Only allow if explicitly prefixed with question/answer header command like "Ans to (i)", "Q. (i)"
            if not re.search(r'\b(?:ans(?:wer)?|question|ques|q\b|q\.|নং|উত্তর|সমাধান|to\s+(?:the|tha)\s+no|no)\b', clean, re.IGNORECASE):
                return True
        return False

    @classmethod
    def is_letter_subpoint(cls, text: str) -> bool:
        """Checks if text begins with a bracketed/standalone Letter subpoint like (a), (b), (c), [d], a., b."""
        clean = text.strip()
        if cls.LETTER_SUBPOINT_PATTERN.match(clean):
            if not re.search(r'\b(?:ans(?:wer)?|question|ques|q\b|q\.|নং|উত্তর|সমাধান|to\s+(?:the|tha)\s+no|no)\b', clean, re.IGNORECASE):
                return True
        return False

    @classmethod
    def detect_cover_page_or_metadata(
        cls,
        ocr_text: str,
        line_boxes: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyzes page text and bounding boxes for exam cover / student metadata.
        Returns:
          - 'is_pure_cover_page': bool
          - 'has_metadata_header': bool
          - 'metadata_bottom_ymin': float
        """
        if not ocr_text:
            return {'is_pure_cover_page': False, 'has_metadata_header': False, 'metadata_bottom_ymin': 0.0}

        text_lower = ocr_text.lower()
        lines = [l.strip() for l in ocr_text.splitlines() if l.strip()]

        meta_lines_idx = []
        for idx, l in enumerate(lines):
            l_low = l.lower()
            if any(kw in l_low for kw in cls.COVER_PAGE_KEYWORDS):
                meta_lines_idx.append(idx)
            elif re.search(r'\b(?:name|id|roll|course|dept|batch|section|sem|date)\s*[:\-\=]', l_low):
                meta_lines_idx.append(idx)

        has_metadata = len(meta_lines_idx) >= 1 or any(kw in text_lower for kw in ['student name', 'roll no', 'course code', 'student id', 'registration no'])

        metadata_bottom_ymin = 0.0
        if meta_lines_idx and len(lines) > 0:
            last_meta_idx = max(meta_lines_idx)
            metadata_bottom_ymin = round((last_meta_idx + 1) / float(len(lines)), 3)
            if line_boxes and last_meta_idx < len(line_boxes):
                lb = line_boxes[last_meta_idx]
                bbox = lb.get('bbox', lb)
                if isinstance(bbox, dict) and 'ymax' in bbox:
                    ymax = bbox['ymax']
                    metadata_bottom_ymin = round(ymax / 1000.0 if ymax > 1.0 else ymax, 3)

        return {
            'is_pure_cover_page': has_metadata,
            'has_metadata_header': has_metadata,
            'metadata_bottom_ymin': min(0.95, max(0.10, metadata_bottom_ymin))
        }

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

        line_lower = line_str.lower()
        if any(kw in line_lower for kw in ['examination', 'student name', 'course number', 'course name', 'id no', 'record of score', 'marks obtained', 'semester:', 'section:']):
            return {
                'is_question_heading': False,
                'question_number': None,
                'heading_text': line_str,
                'confidence': 0.99,
                'heading_type': 'BODY_TEXT',
                'raw_text': text,
                'reason': 'COVER_PAGE_METADATA'
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

        # 3. High Priority Subcontinental / Verbose Heading Pattern Detection
        for pat in cls.SUBCONTINENTAL_HEADING_PATTERNS:
            m = pat.search(line_str)
            if m and m.group(1):
                raw_num = m.group(1).strip()
                norm_num = cls.normalize_question_number(raw_num)

                is_valid = True
                if valid_nums_clean:
                    base_norm = re.sub(r'\D', '', norm_num)
                    is_valid = (
                        (norm_num in valid_nums_clean) or
                        (norm_num.lower() in [v.lower() for v in valid_nums_clean]) or
                        (base_norm and any(re.sub(r'\D', '', v) == base_norm for v in valid_nums_clean if v))
                    )

                if is_valid:
                    boosted_score = 90
                    if has_ans_ctx and has_q_ctx:
                        boosted_score += 5
                    if ymin_pct <= 0.25:
                        boosted_score += 4

                    conf = min(0.99, round(boosted_score / 100.0, 2))
                    return {
                        'is_question_heading': True,
                        'question_number': norm_num,
                        'normalized_number': norm_num,
                        'heading_text': line_str,
                        'confidence': conf,
                        'score': boosted_score,
                        'heading_type': 'EXPLICIT_SUBCONTINENTAL_HEADING',
                        'raw_text': text,
                        'ans_token': ans_token if has_ans_ctx else 'NO',
                        'q_token': q_token if has_q_ctx else 'NO',
                        'raw_num': raw_num,
                        'norm_num': norm_num,
                        'reason': 'VERBOSE_SUBCONTINENTAL_PATTERN_MATCH'
                    }

        best_cand = None
        best_score = 0

        for raw_num, norm_num in num_candidates:
            # Validate question number against exam questions
            base_norm = re.sub(r'\D', '', norm_num)
            is_cand_valid = True
            if valid_nums_clean:
                is_cand_valid = (
                    (norm_num in valid_nums_clean) or
                    (norm_num.lower() in [v.lower() for v in valid_nums_clean]) or
                    (base_norm and any(re.sub(r'\D', '', v) == base_norm for v in valid_nums_clean if v))
                )

            if not is_cand_valid:
                continue

            # Multi-Factor Score Calculation:
            score = 0
            if has_ans_ctx:
                score += 40
            if has_q_ctx:
                score += 35
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
                'normalized_number': norm_num,
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
            'normalized_number': None,
            'heading_text': line_str,
            'confidence': 0.0,
            'heading_type': 'BODY_TEXT',
            'raw_text': text,
            'ans_token': ans_token if has_ans_ctx else 'NO',
            'q_token': q_token if has_q_ctx else 'NO',
            'reason': 'HEADING_SCORE_TOO_LOW'
        }

    @classmethod
    def is_potential_heading_line(cls, text: str, ymin_pct: float) -> bool:
        """
        Fast-Reject Body Lines:
        - Do NOT test formulas (=, +, *, numbers, single letters like F, a+0, 210.) as heading candidates.
        - Reject standalone subpoints: (i), (ii), (iii), (a), (b), (c) unless prefixed with explicit question keywords.
        - Reject metadata lines: Name, Roll, Course Code, Student ID.
        - Only evaluate lines containing explicit heading trigger tokens OR isolated numeral anchors at top 40%.
        """
        clean = text.strip()
        if not clean or len(clean) > 140:
            return False

        lower = clean.lower()

        # Reject pure metadata lines
        if any(kw in lower for kw in ['student name', 'roll no', 'course code', 'course title', 'student id', 'registration no', 'reg no', 'semester', 'department']):
            return False

        # Fast check for explicit heading trigger tokens
        trigger_tokens = [
            'ans', 'answer', 'q', 'ques', 'quest', 'question', 'q.', 'qno', 'qs', 'no.', 'no', 'নং', 'উত্তর', 'সমাধান',
            'solution', 'soln', 'sol', 'ang', 'am', 'ami', "am'", 'amilo', 'nd', 'n0', 'no!', "no'", '0n', '0no', '0nq',
            "9'n", "9'nd", "q'nd", "q'no", "9.no", "q.no", "no'"
        ]
        for tok in trigger_tokens:
            if tok in lower:
                return True

        if re.search(r'\b(?:ans(?:wer)?|a[mn][sgi\'\`\~]*|sol(?:ution|n)?|q(?:uestion|ues|s)?|no|nd|n0|0n[oq]?|#|নং|উত্তর|প্রশ্ন)\b', lower, re.UNICODE):
            return True

        if re.search(r'\b(?:Q|9|NO|ND|N0)\s*[\.\:\-\'\`]?\s*(?:NO|ND|N0)?\s*[\.\:\-\'\`]?\s*[0-9]{1,3}', clean, re.IGNORECASE):
            return True

        # Top 40% of page check for isolated numerals or anchor patterns
        if ymin_pct < 0.40:
            if re.match(r'^(?:[Qq9][\.\s\'\-]*)?[0-9]{1,3}[\.\:\)\-]?$', clean):
                return True
            if re.match(r'^[IVXLCDM]{1,6}[\.\:\)\-]?$', clean, re.IGNORECASE):
                return True

        return False

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
        Reconstructs visual lines using LineReconstructor, performs fast-rejection candidate filtering,
        multi-signal scoring, and returns all candidate answer headings found across the page.
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

        # 1. Single reconstructed lines with Fast Rejection
        for r_line in reconstructed_lines:
            line_str = cls.normalize_ocr_text(r_line['text'])
            ymin_pct = r_line['ymin_pct']
            if not cls.is_potential_heading_line(line_str, ymin_pct):
                continue

            candidates.append({
                'text': line_str,
                'line_index': r_line['line_index'],
                'ymin_pct': ymin_pct,
                'ymax_pct': r_line['ymax_pct'],
                'bbox': r_line['bbox'],
                'whitespace_above': r_line.get('whitespace_above', 0.0),
                'whitespace_below': r_line.get('whitespace_below', 0.0),
                'is_isolated': r_line.get('is_isolated', False),
                'is_multiline': False
            })

        # 2. Multiline sliding windows (2, 3, 4 lines) for split headings
        n_lines = len(reconstructed_lines)
        for w_size in [2, 3, 4]:
            for i in range(n_lines - w_size + 1):
                window_slice = reconstructed_lines[i:i + w_size]
                r_first = window_slice[0]
                r_last = window_slice[-1]
                if r_first['ymin_pct'] >= 0.40 and not any(cls.is_potential_heading_line(cls.normalize_ocr_text(r['text']), r['ymin_pct']) for r in window_slice):
                    continue
                combined_text = " ".join(cls.normalize_ocr_text(r['text']) for r in window_slice)
                if cls.is_potential_heading_line(combined_text, r_first['ymin_pct']):
                    candidates.append({
                        'text': combined_text,
                        'line_index': r_first['line_index'],
                        'ymin_pct': r_first['ymin_pct'],
                        'ymax_pct': r_last['ymax_pct'],
                        'bbox': {
                            'ymin': r_first['bbox'].get('ymin', 0),
                            'xmin': min(r['bbox'].get('xmin', 0) for r in window_slice),
                            'ymax': r_last['bbox'].get('ymax', 0),
                            'xmax': max(r['bbox'].get('xmax', 0) for r in window_slice)
                        },
                        'whitespace_above': r_first.get('whitespace_above', 0.0),
                        'whitespace_below': r_last.get('whitespace_below', 0.0),
                        'is_isolated': r_first.get('is_isolated', False),
                        'is_multiline': True
                    })

        seen_q_nums = set()
        for cand in candidates:
            text = cand['text']
            ymin_pct = cand['ymin_pct']

            decision = cls.detect_explicit_question_heading(
                text=text,
                ymin_pct=ymin_pct,
                stored_question_numbers=stored_question_numbers
            )

            if decision['is_question_heading']:
                norm_q = decision['question_number']
                if norm_q in seen_q_nums:
                    continue
                seen_q_nums.add(norm_q)

                detections.append({
                    'raw_text': decision['raw_text'],
                    'heading_text': text,
                    'normalized_number': norm_q,
                    'confidence': decision['confidence'],
                    'score': decision.get('score', 0),
                    'line_index': cand['line_index'],
                    'ymin_pct': ymin_pct,
                    'ymax_pct': cand['ymax_pct'],
                    'bbox': cand['bbox'],
                    'classification': decision['heading_type'],
                    'method': decision['heading_type']
                })

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
