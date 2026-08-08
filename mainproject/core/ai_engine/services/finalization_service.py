"""
IntelliGrade Finalization & Lifecycle Cleanup Service.
Handles final submission approval, final evaluated report archiving, and automatic deletion of temporary processing artifacts (working images, preview PDFs, temporary crops, OCR cache).
Also includes an automatic cleanup job for abandoned draft submissions older than 24 hours.
"""

import os
import glob
import shutil
from datetime import timedelta
from typing import Dict, Any, Tuple
from django.conf import settings
from django.utils import timezone
from django.db import transaction, close_old_connections, IntegrityError, DatabaseError, OperationalError

from core.models import StudentSubmission, EvaluationResult, EvaluationAuditLog, QuestionMapping
from core.ai_engine.evaluation.evaluated_pdf_service import EvaluatedScriptPDFService
from core.ai_engine.preprocessing.working_copy_manager import WorkingCopyManager

class FinalizationService:
    """
    Manages final submission approval and temporary file cleanup.
    """

    @classmethod
    def finalize_submission(cls, submission_id: int, teacher_user=None, ip_address: str = None) -> Dict[str, Any]:
        """
        Finalizes an evaluated student submission:
        1. Saves final marks & updates status to REVIEWED and is_finalized = True.
        2. Generates final evaluated PDF report.
        3. Saves EvaluationAuditLog audit trail.
        4. Automatically deletes temporary working images, preview PDFs, and OCR cache.
        """
        submission = StudentSubmission.objects.get(id=submission_id)

        print(f"\n==================================================")
        print(f"Teacher Confirmed Submission #{submission.id}")
        print(f"==================================================")

        # 1. Generate Final Evaluated PDF Report
        final_pdf_path = EvaluatedScriptPDFService.generate_evaluated_pdf(submission.id)

        # Copy final PDF to media/submission_final/
        final_dir = WorkingCopyManager.FINAL_DIR
        os.makedirs(final_dir, exist_ok=True)
        archived_final_pdf = os.path.join(final_dir, f"evaluated_final_submission_{submission.id}.pdf")
        shutil.copy(final_pdf_path, archived_final_pdf)

        # 2. Update Submission Database State using Centralized Workflow
        from core.ai_engine.services.workflow import SubmissionWorkflow
        SubmissionWorkflow.advance(
            submission,
            StudentSubmission.Status.FINALIZED,
            user=teacher_user,
            details={
                'total_obtained_marks': float(submission.total_obtained_marks),
                'total_max_marks': float(submission.total_max_marks),
                'percentage': submission.percentage,
                'final_pdf_path': archived_final_pdf
            }
        )

        # 3. Purge Temporary Files (Working images, preview PDFs, temporary crops, OCR cache)
        deleted_files = cls._purge_temporary_artifacts(submission.id)

        print(f"==================================================")
        print(f"Temporary Files Deleted: {deleted_files['count']} file(s)")
        print(f"Working Images Deleted: {deleted_files['working_count']}")
        print(f"OCR Cache & Preview Deleted: True")
        print(f"==================================================")
        print(f"SUCCESS: Submission #{submission.id} Finalized")
        print(f"==================================================\n")

        return {
            'success': True,
            'submission_id': submission.id,
            'final_pdf_path': archived_final_pdf,
            'deleted_artifacts_count': deleted_files['count'],
            'message': 'Submission finalized successfully and temporary processing artifacts deleted.'
        }

    @classmethod
    def _purge_temporary_artifacts(cls, submission_id: int) -> Dict[str, int]:
        """
        Deletes working images (media/submission_working/), preview PDFs (media/submission_preview/),
        temporary crops, and OCR trace files for a submission.
        Does NOT touch EvaluationResult, StudentSubmission, QuestionMapping, final PDF report, or audit logs.
        """
        count = 0
        working_count = 0

        # Delete working image files (media/submission_working/sub_<id>_*)
        working_pattern = os.path.join(WorkingCopyManager.WORKING_DIR, f"sub_{submission_id}_*")
        for f in glob.glob(working_pattern):
            try:
                if os.path.isfile(f):
                    os.remove(f)
                    count += 1
                    working_count += 1
            except Exception as e:
                print(f"[CLEANUP WARNING] Failed deleting {f}: {e}")

        # Delete preview PDF files (media/submission_preview/submission_<id>_*)
        preview_pattern = os.path.join(WorkingCopyManager.PREVIEW_DIR, f"submission_{submission_id}_*")
        for f in glob.glob(preview_pattern):
            try:
                if os.path.isfile(f):
                    os.remove(f)
                    count += 1
            except Exception as e:
                print(f"[CLEANUP WARNING] Failed deleting {f}: {e}")

        # Delete temporary request trace files
        trace_dir = os.path.join(settings.MEDIA_ROOT, 'request_trace', f'eval_{submission_id}')
        if os.path.exists(trace_dir):
            try:
                shutil.rmtree(trace_dir)
                count += 1
            except Exception as e:
                print(f"[CLEANUP WARNING] Failed deleting trace dir {trace_dir}: {e}")

        return {'count': count, 'working_count': working_count}

    @classmethod
    def cleanup_abandoned_drafts(cls, hours: int = 24) -> int:
        """
        Automatic cleanup job: Finds draft/unfinished submissions created > 24 hours ago
        that are not finalized and purges their temporary working files.
        """
        cutoff_time = timezone.now() - timedelta(hours=hours)
        abandoned_subs = StudentSubmission.objects.filter(is_finalized=False, created_at__lt=cutoff_time)

        purged_count = 0
        for sub in abandoned_subs:
            res = cls._purge_temporary_artifacts(sub.id)
            purged_count += res['count']

        print(f"[AUTO CLEANUP JOB] Purged temporary files for {abandoned_subs.count()} abandoned draft submission(s) (total {purged_count} files cleaned).")
        return purged_count
