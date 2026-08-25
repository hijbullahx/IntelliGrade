import os
import io
import re
import zipfile
import tempfile
import fitz  # PyMuPDF
from typing import List, Dict, Any, Optional, Tuple, Union
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction

from core.models import Examination, StudentSubmission, SubmissionPage, SubmissionImage
from core.ai_engine.preprocessing.working_copy_manager import WorkingCopyManager
from core.ai_engine.services.workflow import SubmissionWorkflow


class SubmissionProcessor:
    """
    Universal Answer Script Ingestion & Processing Service for IntelliGrade.
    Seamlessly handles:
    1. Multi-page PDFs: Renders each page to 300 DPI high-res RGB image bytes.
    2. Standalone Images (PNG / JPG / JPEG / WEBP): Direct ingestion into SubmissionPages.
    3. Batch ZIP Archives: Unpacks nested student scripts, extracts Roll/ID from filenames, and creates batch submissions.
    """

    ALLOWED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp'}
    ALLOWED_SCRIPT_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.webp'}

    @classmethod
    def extract_student_info_from_filename(cls, filename: str) -> Tuple[str, str]:
        """
        Extracts student name and roll/ID from filenames such as:
        - 190104055.pdf -> Name: "Student (190104055)", Roll: "190104055"
        - Rahim_Ahmed_CSE4385_045.jpg -> Name: "Rahim Ahmed", Roll: "CSE4385-045"
        - CSE-2026-045.pdf -> Name: "Student (CSE-2026-045)", Roll: "CSE-2026-045"
        """
        base_name = os.path.splitext(os.path.basename(filename))[0]
        cleaned = base_name.replace('_', ' ').replace('-', ' ').strip()

        # Find roll number pattern (digits, or department-year-roll)
        roll_match = re.search(r'\b([A-Za-z]{2,5}[-_ ]?\d{4,8}|\d{4,10}|[A-Za-z0-9]+[-_]\d+)\b', base_name)
        roll_no = roll_match.group(1).replace(' ', '-').replace('_', '-') if roll_match else ""

        # Extract name by removing roll_no and course tags
        name_candidate = cleaned
        if roll_no:
            name_candidate = re.sub(re.escape(roll_match.group(1).replace('-', ' ').replace('_', ' ')), '', name_candidate, flags=re.IGNORECASE)
        name_candidate = re.sub(r'\b(script|submission|midterm|final|exam|quiz|sheet|paper|student)\b', '', name_candidate, flags=re.IGNORECASE).strip()

        if name_candidate and len(name_candidate) >= 3:
            student_name = " ".join([word.capitalize() for word in name_candidate.split()])
        elif roll_no:
            student_name = f"Student ({roll_no})"
        else:
            student_name = f"Student ({base_name})"

        return student_name, roll_no

    @classmethod
    def process_uploaded_file(
        cls,
        examination: Examination,
        uploaded_file,
        student_name: Optional[str] = None,
        roll_no: Optional[str] = None,
        user=None,
        ip_address: Optional[str] = None
    ) -> List[StudentSubmission]:
        """
        Entry point: Detects file type (ZIP / PDF / Image) and creates StudentSubmission records.
        """
        filename = getattr(uploaded_file, 'name', 'script_file.pdf')
        ext = os.path.splitext(filename)[1].lower()

        if ext == '.zip':
            return cls._process_zip_archive(examination, uploaded_file, user, ip_address)
        else:
            sub = cls._process_single_script(
                examination=examination,
                uploaded_file=uploaded_file,
                student_name=student_name,
                roll_no=roll_no,
                filename=filename,
                user=user,
                ip_address=ip_address
            )
            return [sub]

    @classmethod
    def _process_single_script(
        cls,
        examination: Examination,
        uploaded_file,
        student_name: Optional[str],
        roll_no: Optional[str],
        filename: str,
        user=None,
        ip_address: Optional[str] = None
    ) -> StudentSubmission:
        """
        Ingests a single multi-page PDF or standalone image script.
        """
        fn_name, fn_roll = cls.extract_student_info_from_filename(filename)
        final_roll = (roll_no or fn_roll or "").strip()
        final_name = (student_name or "").strip()
        if not final_name or final_name.lower() in ["student", "pending ocr extraction"]:
            final_name = fn_name

        sub = StudentSubmission.objects.create(
            examination=examination,
            student_name=final_name,
            student_roll_no=final_roll,
            script_file=uploaded_file
        )

        # Ingest pages and initialize high-resolution 300 DPI working copies
        WorkingCopyManager.create_initial_working_copies(sub.id)
        return sub

    @classmethod
    def _process_zip_archive(
        cls,
        examination: Examination,
        zip_file,
        user=None,
        ip_address: Optional[str] = None
    ) -> List[StudentSubmission]:
        """
        Unpacks batch ZIP archive in-memory, extracting nested student answer scripts.
        """
        created_submissions = []

        # Read zip bytes
        if hasattr(zip_file, 'read'):
            zip_bytes = zip_file.read()
        else:
            with open(zip_file, 'rb') as f:
                zip_bytes = f.read()

        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zf:
            namelist = zf.namelist()
            valid_entries = [
                n for n in namelist
                if not n.startswith('__MACOSX/') and not os.path.basename(n).startswith('.')
                and os.path.splitext(n)[1].lower() in cls.ALLOWED_SCRIPT_EXTENSIONS
            ]

            valid_entries.sort()
            print(f"[SubmissionProcessor] Unpacked ZIP with {len(valid_entries)} valid student script(s).")

            for entry_name in valid_entries:
                file_data = zf.read(entry_name)
                entry_filename = os.path.basename(entry_name)
                content_file = ContentFile(file_data, name=entry_filename)

                fn_name, fn_roll = cls.extract_student_info_from_filename(entry_filename)

                sub = StudentSubmission.objects.create(
                    examination=examination,
                    student_name=fn_name,
                    student_roll_no=fn_roll,
                    script_file=content_file
                )

                # Initialize working copies and 300 DPI pages
                WorkingCopyManager.create_initial_working_copies(sub.id)
                created_submissions.append(sub)

        return created_submissions

    @classmethod
    def process_and_evaluate(
        cls,
        examination: Examination,
        uploaded_file,
        student_name: Optional[str] = None,
        roll_no: Optional[str] = None,
        user=None,
        ip_address: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Ingests and immediately runs the end-to-end evaluation pipeline for all submissions.
        """
        from core.ai_engine.evaluation.script_evaluator import AIScriptEvaluator
        submissions = cls.process_uploaded_file(
            examination=examination,
            uploaded_file=uploaded_file,
            student_name=student_name,
            roll_no=roll_no,
            user=user,
            ip_address=ip_address
        )

        results = []
        for sub in submissions:
            evaluated_sub = AIScriptEvaluator.process_and_evaluate_submission(
                submission_id=sub.id,
                options=options,
                user=user,
                ip_address=ip_address
            )
            results.append({
                'submission_id': evaluated_sub.id,
                'student_name': evaluated_sub.student_name,
                'student_roll_no': evaluated_sub.student_roll_no,
                'total_obtained': float(evaluated_sub.total_obtained_marks or 0.0),
                'total_max': float(evaluated_sub.total_max_marks or 0.0),
                'percentage': float(evaluated_sub.percentage or 0.0),
                'requires_manual_review': evaluated_sub.requires_manual_review,
                'status': evaluated_sub.status
            })

        return results
