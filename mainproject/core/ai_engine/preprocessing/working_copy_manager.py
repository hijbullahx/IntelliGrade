"""
IntelliGrade Working Copy Manager Service.
Maintains working image copies (sub_<id>_p<num>_v<ver>.png) in media/submission_working/
as the single source of truth for OCR, Preview PDF, and LLM Evaluation.
Enforces image edit version control and runtime logging.
"""

import os
import cv2
import fitz  # PyMuPDF
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from django.conf import settings
from django.db import transaction

from core.models import StudentSubmission, SubmissionPage, SubmissionImage, SubmissionPDF

class WorkingCopyManager:
    """
    Manages the lifecycle of working image copies and preview PDFs.
    """

    # Directory constants
    TEMP_DIR = os.path.join(settings.MEDIA_ROOT, 'submission_temp')
    WORKING_DIR = os.path.join(settings.MEDIA_ROOT, 'submission_working')
    PREVIEW_DIR = os.path.join(settings.MEDIA_ROOT, 'submission_preview')
    FINAL_DIR = os.path.join(settings.MEDIA_ROOT, 'submission_final')
    ARCHIVE_DIR = os.path.join(settings.MEDIA_ROOT, 'submission_archive')

    @classmethod
    def ensure_directories(cls):
        """Creates all standard working directories if they do not exist."""
        for d in [cls.TEMP_DIR, cls.WORKING_DIR, cls.PREVIEW_DIR, cls.FINAL_DIR, cls.ARCHIVE_DIR]:
            os.makedirs(d, exist_ok=True)

    @classmethod
    def get_working_image_path(cls, submission_id: int, page_num: int, version: int = 1) -> str:
        """Returns standard path for a working image copy."""
        cls.ensure_directories()
        return os.path.join(cls.WORKING_DIR, f"sub_{submission_id}_p{page_num}_v{version}.png")

    @classmethod
    def get_latest_working_image_path(cls, submission_id: int, page_num: int) -> Optional[str]:
        """Finds the path to the latest working image version for a page."""
        sp = SubmissionPage.objects.filter(submission_id=submission_id, page_number=page_num).first()
        if sp and sp.working_image_path and os.path.exists(sp.working_image_path):
            return sp.working_image_path

        # Fallback to checking disk for matching files
        cls.ensure_directories()
        version = 1
        best_path = None
        while True:
            candidate = cls.get_working_image_path(submission_id, page_num, version)
            if os.path.exists(candidate):
                best_path = candidate
                version += 1
            else:
                break

        return best_path

    @classmethod
    def create_initial_working_copies(cls, submission_id: int) -> List[str]:
        """
        Creates v1 working image copies from original uploaded images or PDF script.
        """
        cls.ensure_directories()
        submission = StudentSubmission.objects.get(id=submission_id)
        working_paths = []

        images = list(submission.raw_images.filter(is_deleted=False).order_by('sequence_order'))
        if images:
            for idx, img_obj in enumerate(images, 1):
                raw_path = img_obj.original_file.path
                bgr = cv2.imread(raw_path)
                if img_obj.rotation_angle != 0 and bgr is not None:
                    rot_code = {90: cv2.ROTATE_90_CLOCKWISE, 180: cv2.ROTATE_180, 270: cv2.ROTATE_90_COUNTERCLOCKWISE}.get(img_obj.rotation_angle % 360)
                    if rot_code is not None:
                        bgr = cv2.rotate(bgr, rot_code)

                out_path = cls.get_working_image_path(submission_id, idx, version=1)
                if bgr is not None:
                    cv2.imwrite(out_path, bgr)
                else:
                    import shutil
                    shutil.copy(raw_path, out_path)

                img_obj.working_image_path = out_path
                img_obj.version = 1
                img_obj.save()

                sp, _ = SubmissionPage.objects.get_or_create(submission=submission, page_number=idx)
                sp.working_image_path = out_path
                sp.version = 1
                sp.save()

                working_paths.append(out_path)

        elif submission.script_file and os.path.exists(submission.script_file.path):
            doc = fitz.open(submission.script_file.path)
            for page_idx, page in enumerate(doc, 1):
                pix = page.get_pixmap(dpi=300, colorspace=fitz.csRGB)
                out_path = cls.get_working_image_path(submission_id, page_idx, version=1)
                pix.save(out_path)

                sp, _ = SubmissionPage.objects.get_or_create(submission=submission, page_number=page_idx)
                sp.working_image_path = out_path
                sp.version = 1
                sp.save()

                working_paths.append(out_path)
            doc.close()

        from core.ai_engine.services.workflow import SubmissionWorkflow
        SubmissionWorkflow.advance(submission, StudentSubmission.Status.WORKING_COPY_CREATED, force=True)

        print(f"\n==================================================")
        print(f"WORKING COPY CREATED")
        print(f"{len(working_paths)} pages initialized in submission_working/")
        print(f"==================================================\n")

        cls.rebuild_preview_pdf(submission_id)
        return working_paths

    @classmethod
    def apply_image_edit(
        cls,
        submission_id: int,
        page_num: int,
        edited_bgr: np.ndarray,
        edit_description: str = "ROTATION / CROP APPLIED"
    ) -> Tuple[str, int]:
        """
        Saves updated working image copy, bumps version (v1 -> v2), updates DB, and rebuilds preview PDF.
        """
        cls.ensure_directories()
        sp = SubmissionPage.objects.filter(submission_id=submission_id, page_number=page_num).first()
        current_version = sp.version if sp else 1
        new_version = current_version + 1

        out_path = cls.get_working_image_path(submission_id, page_num, version=new_version)
        cv2.imwrite(out_path, edited_bgr)

        if sp:
            sp.working_image_path = out_path
            sp.version = new_version
            sp.save()

        img_obj = SubmissionImage.objects.filter(submission_id=submission_id, sequence_order=page_num).first()
        if img_obj:
            img_obj.working_image_path = out_path
            img_obj.version = new_version
            img_obj.save()

        print(f"\n==================================================")
        print(f"{edit_description.upper()}")
        print(f"Page {page_num} Version v{new_version}")
        print(f"Saved: {out_path}")
        print(f"==================================================\n")

        cls.rebuild_preview_pdf(submission_id)
        return out_path, new_version

    @classmethod
    def rebuild_preview_pdf(cls, submission_id: int) -> str:
        """
        Compiles working copy images into media/submission_preview/submission_<id>_preview.pdf.
        This preview PDF comes from the EXACT SAME working images as evaluation.
        """
        cls.ensure_directories()
        submission = StudentSubmission.objects.get(id=submission_id)
        pages = list(submission.pages.all().order_by('page_number'))

        preview_pdf_path = os.path.join(cls.PREVIEW_DIR, f"submission_{submission.id}_preview.pdf")

        doc = fitz.open()
        page_count = 0

        for sp in pages:
            img_path = sp.working_image_path if (sp.working_image_path and os.path.exists(sp.working_image_path)) else cls.get_latest_working_image_path(submission.id, sp.page_number)
            if img_path and os.path.exists(img_path):
                pix = fitz.Pixmap(img_path)
                w, h = float(pix.width), float(pix.height)
                pdf_page = doc.new_page(width=w, height=h)
                pdf_page.insert_image(fitz.Rect(0, 0, w, h), filename=img_path)
                pix = None

        if len(doc) > 0:
            doc.save(preview_pdf_path)
            page_count = len(doc)
            doc.close()

            sub_pdf, _ = SubmissionPDF.objects.get_or_create(submission=submission)
            with open(preview_pdf_path, 'rb') as f_pdf:
                from django.core.files.base import ContentFile
                sub_pdf.pdf_file.save(f"submission_{submission.id}_preview.pdf", ContentFile(f_pdf.read()), save=False)
                sub_pdf.page_count = page_count
                sub_pdf.file_size_bytes = os.path.getsize(preview_pdf_path)
                sub_pdf.save()
        else:
            doc.close()

        from core.ai_engine.services.workflow import SubmissionWorkflow
        SubmissionWorkflow.advance(submission, StudentSubmission.Status.PDF_GENERATED)

        print(f"\n==================================================")
        print(f"PREVIEW PDF GENERATED")
        print(f"{page_count} pages compiled from submission_working/")
        print(f"==================================================\n")

        return preview_pdf_path

    @classmethod
    def cleanup_temporary_files(cls, submission_id: int):
        """
        Automatically removes unneeded temporary upload files (in submission_temp/)
        and obsolete working image versions for a submission after evaluation.
        """
        try:
            cls.ensure_directories()
            submission = StudentSubmission.objects.filter(id=submission_id).first()
            if not submission:
                return

            # 1. Clean up submission_temp directory for this submission
            if os.path.exists(cls.TEMP_DIR):
                for fname in os.listdir(cls.TEMP_DIR):
                    if f"sub_{submission_id}_" in fname or f"submission_{submission_id}_" in fname:
                        fpath = os.path.join(cls.TEMP_DIR, fname)
                        if os.path.isfile(fpath):
                            try:
                                os.remove(fpath)
                            except Exception:
                                pass

            # 2. Clean up obsolete image versions in submission_working (keep latest active version per page)
            active_paths = set(
                SubmissionPage.objects.filter(submission=submission)
                .exclude(working_image_path='')
                .values_list('working_image_path', flat=True)
            )

            if os.path.exists(cls.WORKING_DIR):
                for fname in os.listdir(cls.WORKING_DIR):
                    if fname.startswith(f"sub_{submission_id}_p"):
                        fpath = os.path.join(cls.WORKING_DIR, fname)
                        if fpath not in active_paths and os.path.isfile(fpath):
                            try:
                                os.remove(fpath)
                            except Exception:
                                pass

            print(f"[CLEANUP SUCCESS] Temporary & obsolete files cleaned up for Submission #{submission_id}.")
        except Exception as e:
            print(f"[CLEANUP WARNING] Failed cleaning temporary files for Submission #{submission_id}: {e}")

    @classmethod
    def cleanup_all_working_artifacts(cls, submission_id: int):
        """
        Removes all working copies, preview PDFs, compiled PDFs, and temp files for a submission.
        """
        try:
            cls.ensure_directories()
            target_dirs = [cls.TEMP_DIR, cls.WORKING_DIR, cls.PREVIEW_DIR, os.path.join(settings.MEDIA_ROOT, 'submission_pdfs'), cls.FINAL_DIR]
            prefixes = [f"sub_{submission_id}_", f"submission_{submission_id}_", f"submission_{submission_id}."]
            for d in target_dirs:
                if os.path.exists(d):
                    for fname in os.listdir(d):
                        if any(fname.startswith(p) for p in prefixes):
                            fpath = os.path.join(d, fname)
                            if os.path.isfile(fpath):
                                try:
                                    os.remove(fpath)
                                except Exception:
                                    pass
            print(f"[CACHE FLUSH] All working disk artifacts purged for Submission #{submission_id}.")
        except Exception as e:
            print(f"[CACHE FLUSH WARNING] Failed purging disk artifacts for Submission #{submission_id}: {e}")

    @classmethod
    def flush_submission_pipeline_cache(cls, submission_id: int):
        """
        Centralized cache flush and pipeline reset when images are uploaded, deleted, or reordered.
        """
        from core.models import StudentSubmission, SubmissionPDF
        try:
            sub = StudentSubmission.objects.get(id=submission_id)
            sub.status = StudentSubmission.Status.UPLOADED
            sub.total_obtained_marks = 0.0
            sub.total_max_marks = 0.0
            sub.percentage = 0.0
            sub.requires_manual_review = False
            sub.save(update_fields=['status', 'total_obtained_marks', 'total_max_marks', 'percentage', 'requires_manual_review'])

            sub.pages.all().delete()
            sub.answers.all().delete()
            sub.question_mappings.all().delete()
            SubmissionPDF.objects.filter(submission=sub).delete()
            cls.cleanup_all_working_artifacts(submission_id)
            print(f"[CACHE FLUSH SUCCESS] Pipeline cache completely flushed for Submission #{submission_id}.")
        except Exception as e:
            print(f"[CACHE FLUSH ERROR] Error flushing pipeline cache for Submission #{submission_id}: {e}")

