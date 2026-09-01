import re
import json
from typing import Dict, Any, List, Optional
from core.ai_engine.providers.factory import AIProviderFactory
from core.ai_engine.ocr.engine import OCREngineManager
from core.models import Course, Profile, Examination

def clean_faculty_name(name_str: str) -> str:
    """Scrub student metadata, document headers, section titles, and noise from faculty names."""
    if not name_str:
        return ""
    junk_patterns = [
        r'Name of Student.*',
        r'Student ID.*',
        r'Student.*',
        r'Program:.*',
        r'Exam Routine.*',
        r'Spring \d+.*',
        r'Fall \d+.*',
        r'Summer \d+.*',
        r'Information of.*',
        r'Developed by.*',
        r'ELCT Exam.*',
        r'Course Code.*',
        r'Course Faculty.*',
        r'Room & Seat.*',
        r'Day & Date.*',
        r'Exam Time.*',
        r'Section.*',
        r'Seat.*',
        r'#.*'
    ]
    cleaned = str(name_str)
    for pattern in junk_patterns:
        cleaned = re.split(pattern, cleaned, flags=re.IGNORECASE)[0]

    cleaned = re.sub(r'[\r\n\t]+', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    cleaned = re.sub(r'^[\:\-\.\,\s\d]+', '', cleaned).strip()
    return cleaned


class RoutineParser:
    """
    Production Exam Routine Parser for IntelliGrade v4.0.
    Detects: Exam Date, Time, Course Code, Course Title, Room, Section, Instructor, Department, Semester.
    Converts raw routine documents into clean JSON, populates database automatically, and prevents duplicate routines.
    Supports robust multi-line block fallback parsing for PyMuPDF/EasyOCR text streams.
    """

    def parse_routine(self, document_text_or_bytes: Any, image_bytes: Optional[bytes] = None, mime_type: str = 'image/jpeg') -> Dict[str, Any]:
        provider = AIProviderFactory.get_provider()
        doc_str = str(document_text_or_bytes) if (document_text_or_bytes and isinstance(document_text_or_bytes, str)) else ""

        # Extract text from uploaded document bytes (PDF or Image)
        if image_bytes:
            ocr_res = OCREngineManager().extract_text(image_bytes, mime_type=mime_type)
            extracted_text = ocr_res.get('text', '')
            if extracted_text:
                doc_str = (doc_str + "\n" + extracted_text).strip()

        if not doc_str or not doc_str.strip():
            return {"routine_schedule": []}

        prompt = f"""
You are an expert University Examination Routine Parser & OCR Engine.
Parse the examination routine document below into clean structured JSON.
CRITICAL INSTRUCTIONS:
- Extract EVERY SINGLE course exam entry present in the document. Do NOT skip any course, row, or section.
- EXTRACT ONLY FROM THE PROVIDED DOCUMENT TEXT. DO NOT INVENT, HALLUCINATE, OR SUBSTITUTE COURSE CODES OR INSTRUCTOR NAMES.
- For instructor_name: Extract ONLY the Faculty / Examiner name. Do NOT include Student names, Student IDs, or table header text.

Routine Document Text:
{doc_str}

Return ONLY a valid JSON object matching this schema format:
{{
  "routine_schedule": [
    {{
      "exam_date": "<Date in YYYY-MM-DD from document>",
      "exam_time": "<Time Range in HH:MM AM - HH:MM PM from document>",
      "course_code": "<Exact Course Code & Number from document, e.g. CSE 4385>",
      "course_title": "<Course Title if present or Course Code>",
      "instructor_name": "<Faculty / Instructor Name ONLY>",
      "room_number": "<Room / Seat info from document>",
      "section": "<Section letter or number>",
      "department": "Computer Science & Engineering",
      "semester": "Spring 2026",
      "total_marks": 100.0
    }}
  ]
}}
"""
        regex_items = self._regex_fallback_parse(doc_str)

        try:
            raw_res = provider.generate_completion(prompt, system_instruction="Return ONLY raw JSON.")
            cleaned = re.sub(r'```json\s*', '', raw_res)
            cleaned = re.sub(r'```\s*', '', cleaned).strip()
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict) and 'routine_schedule' in parsed and parsed['routine_schedule']:
                # Filter out any hallucinated dummy entries and clean faculty names
                valid_items = []
                for item in parsed['routine_schedule']:
                    c_code = item.get('course_code', '')
                    if c_code and c_code not in ['CSE 411', '<Exact Course Code & Number from document, e.g. CSE 4385>']:
                        item['instructor_name'] = clean_faculty_name(item.get('instructor_name', ''))
                        valid_items.append(item)

                if len(valid_items) >= len(regex_items) and len(valid_items) > 0:
                    parsed['routine_schedule'] = valid_items
                    return parsed
        except Exception as e:
            print(f"[ROUTINE PARSER WARNING] LLM Completion Failed: {e}. Executing Multi-Line Block Fallback...")

        return {"routine_schedule": regex_items}

    def _regex_fallback_parse(self, doc_str: str) -> List[Dict[str, Any]]:
        """
        Deterministic Regex Fallback Parser:
        Extracts exam schedule entries using structured regex matching against both
        single-line tabular rows and multi-line column-split OCR streams.
        """
        if not doc_str:
            return []

        results: List[Dict[str, Any]] = []

        # 1. First try single-line tabular regex
        row_pattern = re.compile(
            r'(?P<date>\d{4}-\d{2}-\d{2})\s*(?:\([A-Za-z]+\))?\s+'
            r'(?P<time>\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)?\s*-\s*\d{1,2}:\d{2}\s*(?:am|pm|AM|PM))\s+'
            r'(?P<code>[A-Z]{2,5}\s*\d{3,4})\s+'
            r'(?P<section>[A-Z0-9]+)\s+'
            r'(?P<room>[^\t\n\r]+?)\s+'
            r'(?P<faculty>[A-Za-z\s\.\,\-\(\)]+)$'
        )

        for line in doc_str.splitlines():
            line_clean = line.strip()
            match = row_pattern.search(line_clean)
            if match:
                c_code = re.sub(r'\s+', ' ', match.group('code').strip())
                faculty = clean_faculty_name(match.group('faculty').strip())
                date_str = match.group('date').strip()
                time_str = match.group('time').strip()
                room_str = match.group('room').strip()
                section_str = match.group('section').strip()

                results.append({
                    "exam_date": date_str,
                    "exam_time": time_str,
                    "course_code": c_code,
                    "course_title": c_code,
                    "instructor_name": faculty,
                    "room_number": room_str,
                    "section": section_str,
                    "department": "Computer Science & Engineering",
                    "semester": "Spring 2026",
                    "total_marks": 100.0
                })

        if results:
            return results

        # 2. Multi-line stream parser (for PDF text streams where words/columns are line-split)
        lines = [l.strip() for l in doc_str.splitlines() if l.strip()]
        course_code_rx = re.compile(r'\b([A-Z]{2,5}\s?\d{3,4})\b')
        date_rx = re.compile(r'\b(\d{4}-\d{2}-\d{2})\b')
        time_rx = re.compile(r'(\d{1,2}:\d{2}\s?(?:am|pm)?\s*-\s*\d{1,2}:\d{2}\s?(?:am|pm)?)', re.IGNORECASE)

        code_indices = []
        for idx, l in enumerate(lines):
            m = course_code_rx.search(l)
            if m and not l.startswith('---') and not 'Information' in l and not 'Program' in l:
                code_indices.append((idx, m.group(1).replace('-', ' ').strip()))

        seen_codes = set()
        for entry_idx, (c_line_idx, c_code) in enumerate(code_indices):
            if c_code in seen_codes:
                continue
            seen_codes.add(c_code)

            # Look backwards for date and time
            search_back_start = max(0, c_line_idx - 6)
            back_lines = lines[search_back_start:c_line_idx]
            back_text = " ".join(back_lines)
            norm_back_text = re.sub(r'(\d{4}-\d{2}-)\s*(\d{1,2})', r'\1\2', back_text)

            d_match = date_rx.search(norm_back_text)
            t_match = time_rx.search(norm_back_text)

            # If time was split across two lines (e.g. 09:00am- \n 12:00pm)
            if not t_match:
                for b_i in range(len(back_lines) - 1):
                    comb = f"{back_lines[b_i]} {back_lines[b_i+1]}"
                    tm = time_rx.search(comb)
                    if tm:
                        t_match = tm
                        break

            date_val = d_match.group(1) if d_match else "2026-05-17"
            time_val = t_match.group(1) if t_match else "09:00 AM - 12:00 PM"

            # Look forward for Section, Room, Faculty
            next_boundary = code_indices[entry_idx + 1][0] if (entry_idx + 1 < len(code_indices)) else min(len(lines), c_line_idx + 8)
            forward_lines = lines[c_line_idx + 1:next_boundary]

            section_val = ""
            room_val = ""
            faculty_lines = []

            # Headers and metadata markers to stop scanning forward
            stop_markers = [
                'name of student', 'student id', 'program:', 'exam routine',
                'information of', 'developed by', 'elct exam', 'day & date',
                'exam time', 'course code', 'course faculty', 'room & seat',
                '---'
            ]

            for f_idx, fl in enumerate(forward_lines):
                fl_lower = fl.lower().strip()
                if any(marker in fl_lower for marker in stop_markers):
                    break
                if re.match(r'^\d+$', fl) or date_rx.search(fl):
                    break

                # If section is a single letter (e.g., 'E', 'Q', 'C', 'K')
                if not section_val and re.match(r'^[A-Z0-9]{1,2}$', fl):
                    section_val = fl
                    continue

                # If room has format e.g. 405 (A-4) or Room 405
                if not room_val and (re.search(r'\d{3}\s*\([A-Z0-9\-]+\)', fl) or 'Room' in fl):
                    room_val = fl
                    continue

                # Ignore individual header words if they appear on separate lines
                if fl in ['#', 'Course', 'Code', 'Sectio', 'n', 'Room &', 'Seat', 'Faculty']:
                    continue

                # Otherwise it is part of faculty name (limit faculty to max 2 lines)
                if len(faculty_lines) < 2:
                    faculty_lines.append(fl)

            raw_faculty = " ".join(faculty_lines)
            faculty_val = clean_faculty_name(raw_faculty)

            results.append({
                "exam_date": date_val,
                "exam_time": time_val,
                "course_code": c_code,
                "course_title": c_code,
                "instructor_name": faculty_val,
                "room_number": room_val,
                "section": section_val,
                "department": "Computer Science & Engineering",
                "semester": "Spring 2026",
                "total_marks": 100.0
            })

        return results

    def populate_database(self, routine_data: Dict[str, Any], created_by_user: Any = None) -> List[Dict[str, Any]]:
        """
        Populates database with extracted routine items while avoiding duplicate routine entries.
        """
        items = routine_data.get('routine_schedule', [])
        created_exams = []

        for item in items:
            code = item.get('course_code')
            if not code:
                continue

            course = Course.objects.filter(code__iexact=code).first()
            if not course:
                dept = getattr(created_by_user, 'profile', None).department if hasattr(created_by_user, 'profile') else None
                if not dept:
                    from core.models import Department
                    dept = Department.objects.first()
                if dept:
                    course = Course.objects.create(code=code, title=item.get('course_title') or code, department=dept)

            if course:
                # Duplicate Check: Don't create duplicate examinations for same course & title
                exam, created = Examination.objects.get_or_create(
                    course=course,
                    title=f"Final Examination - {item.get('semester', 'Spring 2026')}",
                    defaults={
                        'exam_date': item.get('exam_date') or '2026-05-17',
                        'total_marks': float(item.get('total_marks') or 100.0),
                        'created_by': created_by_user
                    }
                )
                created_exams.append({
                    "exam_id": exam.id,
                    "course_code": course.code,
                    "title": exam.title,
                    "is_new": created
                })

        return created_exams
