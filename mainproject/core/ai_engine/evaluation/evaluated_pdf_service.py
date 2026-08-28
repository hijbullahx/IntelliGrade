"""
IntelliGrade Evaluated Script PDF Generator Service.
Generates an annotated, high-resolution PDF document for an evaluated student submission,
featuring page-by-page question headers, mark distributions, rubric breakdowns, and AI feedback stamps.
"""

import os
import fitz  # PyMuPDF
from typing import Optional, List, Dict, Any
from django.conf import settings

from core.models import StudentSubmission, SubmissionPage, SubmissionAnswer, EvaluationResult
from core.utils.question_accessor import QuestionAccessor, safe_getattr, safe_normalize_collection, normalize_q_code

class EvaluatedScriptPDFService:
    """
    Generates annotated PDFs of evaluated answer scripts with page-by-page mark distribution overlays.
    """

    @classmethod
    def generate_evaluated_pdf(cls, submission_id: int) -> str:
        """
        Creates or updates an evaluated script PDF for the given StudentSubmission.
        Returns the absolute path to the generated PDF file.
        """
        submission = StudentSubmission.objects.get(id=submission_id)
        examination = submission.examination
        
        output_dir = os.path.join(settings.MEDIA_ROOT, 'evaluated_pdfs')
        os.makedirs(output_dir, exist_ok=True)
        pdf_path = os.path.join(output_dir, f'evaluated_submission_{submission.id}.pdf')

        doc = fitz.open()

        pages = safe_normalize_collection(submission.pages.all().order_by('page_number'))
        answers = safe_normalize_collection(submission.answers.select_related('question', 'evaluation_result').all())
        
        page_width, page_height = 595.0, 842.0

        # Self-healing: ensure working copy images exist on disk
        try:
            from core.ai_engine.preprocessing.working_copy_manager import WorkingCopyManager
            WorkingCopyManager.ensure_working_copies(submission.id)
        except Exception as e_wc:
            print(f"[PDF GENERATOR WARNING] Failed ensuring working copies: {e_wc}")

        def _resolve_page_img(p_num: int, sp_obj: Optional[SubmissionPage] = None) -> Optional[str]:
            """Resolves the best available high-res image path for a submission page."""
            # 1. Check SubmissionPage working_image_path
            if sp_obj and sp_obj.working_image_path and os.path.exists(sp_obj.working_image_path):
                return sp_obj.working_image_path

            # 2. Check WorkingCopyManager active working copy
            from core.ai_engine.preprocessing.working_copy_manager import WorkingCopyManager
            wc_path = WorkingCopyManager.get_working_copy_path(submission.id, p_num)
            if wc_path and os.path.exists(wc_path):
                return wc_path

            # 3. Check SubmissionPage page_image field
            if sp_obj and sp_obj.page_image and os.path.exists(sp_obj.page_image.path):
                return sp_obj.page_image.path

            # 4. Check Raw Images (SubmissionImage)
            raw_img = submission.raw_images.filter(sequence_order=p_num, is_deleted=False).first()
            if not raw_img:
                raw_imgs = list(submission.raw_images.filter(is_deleted=False).order_by('sequence_order'))
                if p_num - 1 < len(raw_imgs):
                    raw_img = raw_imgs[p_num - 1]
            if raw_img and raw_img.original_file and os.path.exists(raw_img.original_file.path):
                return raw_img.original_file.path

            # 5. Search media/submission_working/ pattern
            import glob
            working_patterns = [
                os.path.join(WorkingCopyManager.WORKING_DIR, f"sub_{submission.id}_p{p_num}*"),
                os.path.join(WorkingCopyManager.WORKING_DIR, f"sub_{submission.id}_page_{p_num}*"),
                os.path.join(WorkingCopyManager.WORKING_DIR, f"working_sub_{submission.id}_page_{p_num}*")
            ]
            for pat in working_patterns:
                matched = glob.glob(pat)
                if matched and os.path.exists(matched[0]):
                    return matched[0]

            # 6. Extract on-the-fly from script_file PDF if available
            if submission.script_file and os.path.exists(submission.script_file.path):
                try:
                    s_doc = fitz.open(submission.script_file.path)
                    if p_num - 1 < len(s_doc):
                        p = s_doc[p_num - 1]
                        pix = p.get_pixmap(dpi=150)
                        temp_path = os.path.join(output_dir, f'temp_ext_{submission.id}_p{p_num}.png')
                        pix.save(temp_path)
                        s_doc.close()
                        return temp_path
                    s_doc.close()
                except Exception:
                    pass

            return None

        # Build Annotated Pages
        if pages:
            for sp in pages:
                img_path = _resolve_page_img(sp.page_number, sp)
                cls._append_annotated_page(doc, img_path, sp.page_number, answers, submission, examination, page_width, page_height)
        elif submission.raw_images.filter(is_deleted=False).exists():
            for r_idx, r_img in enumerate(submission.raw_images.filter(is_deleted=False).order_by('sequence_order'), 1):
                img_path = r_img.original_file.path if r_img.original_file and os.path.exists(r_img.original_file.path) else None
                cls._append_annotated_page(doc, img_path, r_idx, answers, submission, examination, page_width, page_height)
        elif submission.script_file and os.path.exists(submission.script_file.path):
            orig_doc = fitz.open(submission.script_file.path)
            for p_num in range(len(orig_doc)):
                orig_page = orig_doc[p_num]
                pix = orig_page.get_pixmap(dpi=150)
                img_path = os.path.join(output_dir, f'temp_p{p_num+1}_{submission.id}.png')
                pix.save(img_path)
                cls._append_annotated_page(doc, img_path, p_num + 1, answers, submission, examination, page_width, page_height)
                if os.path.exists(img_path):
                    os.remove(img_path)
            orig_doc.close()
        else:
            cls._append_annotated_page(doc, None, 1, answers, submission, examination, page_width, page_height)

        # Always append a final comprehensive Scorecard & Rubric Breakdown Page
        cls._append_summary_page(doc, submission, examination, answers, page_width, page_height)

        doc.save(pdf_path)
        doc.close()
        return pdf_path

    @classmethod
    def _append_annotated_page(
        cls,
        doc: fitz.Document,
        img_path: Optional[str],
        page_num: int,
        answers: List[SubmissionAnswer],
        submission: StudentSubmission,
        examination: Any,
        w: float,
        h: float
    ):
        """Appends an annotated A4 page containing header banner, student image, and mark overlays."""
        pdf_page = doc.new_page(width=w, height=h)

        # 1. Header Banner Box
        header_rect = fitz.Rect(0, 0, w, 60)
        pdf_page.draw_rect(header_rect, color=(0.09, 0.15, 0.28), fill=(0.09, 0.15, 0.28))

        pdf_page.insert_text(
            fitz.Point(15, 22),
            f"IntelliGrade AI Evaluated Script - {examination.title if examination else 'Examination'}",
            fontsize=11,
            color=(1, 1, 1),
            fontname="helv"
        )

        student_info = f"Student: {submission.student_name} (Roll: {submission.student_roll_no or 'N/A'})  |  Page {page_num}"
        pdf_page.insert_text(
            fitz.Point(15, 42),
            student_info,
            fontsize=8.5,
            color=(0.7, 0.8, 0.9),
            fontname="helv"
        )

        score_badge = f"Total Score: {submission.total_obtained_marks} / {submission.total_max_marks} ({submission.percentage}%)"
        pdf_page.insert_text(
            fitz.Point(w - 230, 30),
            score_badge,
            fontsize=9.5,
            color=(0.2, 0.9, 0.5),
            fontname="helv"
        )

        # 2. Main Student Answer Script Page Image Placement
        img_top = 65
        img_height = h - 210

        if img_path and os.path.exists(img_path):
            img_rect = fitz.Rect(15, img_top, w - 15, img_top + img_height)
            pdf_page.insert_image(img_rect, filename=img_path)
            pdf_page.draw_rect(img_rect, color=(0.8, 0.8, 0.8), width=0.5)
        else:
            pdf_page.insert_text(fitz.Point(w/2 - 80, img_top + 100), "[Student Script Page Image]", fontsize=12, color=(0.5, 0.5, 0.5), fontname="helv")

        # 3. Bottom Footer Banner: Page Mark Distribution & Feedback Overlay
        footer_top = h - 140
        footer_rect = fitz.Rect(15, footer_top, w - 15, h - 15)
        pdf_page.draw_rect(footer_rect, color=(0.1, 0.4, 0.3), fill=(0.95, 0.98, 0.96), width=1.5)

        pdf_page.insert_text(
            fitz.Point(25, footer_top + 16),
            f"PAGE {page_num} QUESTION MARK DISTRIBUTION & AI FEEDBACK",
            fontsize=9.5,
            color=(0.05, 0.4, 0.25),
            fontname="helv"
        )

        relevant_answers = [ans for ans in answers if safe_getattr(ans.page, ['page_number'], 0) == page_num]
        if not relevant_answers and answers:
            idx = min(page_num - 1, len(answers) - 1)
            relevant_answers = [answers[idx]]

        y_offset = footer_top + 32
        for ans in relevant_answers[:2]:
            q = ans.question
            q_num = QuestionAccessor.get_question_number(q)
            q_text = QuestionAccessor.get_text(q)
            if len(q_text) > 70:
                q_text = q_text[:67] + "..."

            eval_res = getattr(ans, 'evaluation_result', None)
            obtained = float(eval_res.obtained_marks) if eval_res else 0.0
            max_m = float(eval_res.maximum_marks) if eval_res else QuestionAccessor.get_marks(q)

            q_line = f"{normalize_q_code(q_num)}: {q_text}  -->  MARKS: {obtained} / {max_m}"
            pdf_page.insert_text(fitz.Point(25, y_offset), q_line, fontsize=8.5, color=(0.1, 0.1, 0.1), fontname="helv")

            if eval_res and eval_res.feedback_text:
                fb = eval_res.feedback_text
                if len(fb) > 100:
                    fb = fb[:97] + "..."
                pdf_page.insert_text(fitz.Point(35, y_offset + 12), f"Feedback: {fb}", fontsize=7.5, color=(0.3, 0.3, 0.3), fontname="helv")
            y_offset += 28

    @classmethod
    def _append_summary_page(
        cls,
        doc: fitz.Document,
        submission: StudentSubmission,
        examination: Any,
        answers: List[SubmissionAnswer],
        w: float,
        h: float
    ):
        """Appends a final Scorecard & Rubric Breakdown summary page."""
        summary_page = doc.new_page(width=w, height=h)

        summary_page.draw_rect(fitz.Rect(0, 0, w, 70), color=(0.09, 0.15, 0.28), fill=(0.09, 0.15, 0.28))
        summary_page.insert_text(
            fitz.Point(20, 28),
            f"FINAL EVALUATION SCORECARD & RUBRIC BREAKDOWN",
            fontsize=13,
            color=(1, 1, 1),
            fontname="helv"
        )
        summary_page.insert_text(
            fitz.Point(20, 48),
            f"Exam: {examination.title if examination else 'N/A'}  |  Student: {submission.student_name} ({submission.student_roll_no})",
            fontsize=9,
            color=(0.7, 0.8, 0.9),
            fontname="helv"
        )

        summary_page.draw_rect(fitz.Rect(20, 85, w - 20, 135), color=(0.1, 0.6, 0.3), fill=(0.93, 0.98, 0.95), width=1.5)
        summary_page.insert_text(
            fitz.Point(35, 110),
            f"TOTAL OBTAINED SCORE: {submission.total_obtained_marks} / {submission.total_max_marks}  ({submission.percentage}%)",
            fontsize=12,
            color=(0.05, 0.45, 0.2),
            fontname="helv"
        )
        summary_page.insert_text(
            fitz.Point(35, 125),
            f"Evaluation Mode: AI Script Engine v3.0  |  Status: {submission.status}  |  Manual Review Needed: {submission.requires_manual_review}",
            fontsize=8,
            color=(0.3, 0.3, 0.3),
            fontname="helv"
        )

        table_top = 155
        summary_page.draw_rect(fitz.Rect(20, table_top, w - 20, table_top + 22), color=(0.2, 0.2, 0.3), fill=(0.2, 0.2, 0.3))
        summary_page.insert_text(fitz.Point(30, table_top + 15), "Q#", fontsize=8.5, color=(1, 1, 1), fontname="helv")
        summary_page.insert_text(fitz.Point(60, table_top + 15), "Question Statement", fontsize=8.5, color=(1, 1, 1), fontname="helv")
        summary_page.insert_text(fitz.Point(340, table_top + 15), "Allocated", fontsize=8.5, color=(1, 1, 1), fontname="helv")
        summary_page.insert_text(fitz.Point(410, table_top + 15), "Obtained", fontsize=8.5, color=(1, 1, 1), fontname="helv")
        summary_page.insert_text(fitz.Point(480, table_top + 15), "Confidence", fontsize=8.5, color=(1, 1, 1), fontname="helv")

        y = table_top + 22
        for idx, ans in enumerate(answers, 1):
            q = ans.question
            q_num = QuestionAccessor.get_question_number(q)
            q_text = QuestionAccessor.get_text(q)
            if len(q_text) > 45:
                q_text = q_text[:42] + "..."

            eval_res = getattr(ans, 'evaluation_result', None)
            obtained = float(eval_res.obtained_marks) if eval_res else 0.0
            max_m = float(eval_res.maximum_marks) if eval_res else QuestionAccessor.get_marks(q)
            conf = float(eval_res.confidence) if eval_res else 0.0

            bg_color = (0.96, 0.96, 0.97) if idx % 2 == 0 else (1, 1, 1)
            row_rect = fitz.Rect(20, y, w - 20, y + 22)
            summary_page.draw_rect(row_rect, color=(0.85, 0.85, 0.85), fill=bg_color, width=0.5)

            summary_page.insert_text(fitz.Point(30, y + 15), f"{normalize_q_code(q_num)}", fontsize=8, color=(0.1, 0.1, 0.1), fontname="helv")
            summary_page.insert_text(fitz.Point(60, y + 15), q_text, fontsize=8, color=(0.2, 0.2, 0.2), fontname="helv")
            summary_page.insert_text(fitz.Point(340, y + 15), f"{max_m:.1f}", fontsize=8, color=(0.1, 0.1, 0.1), fontname="helv")
            summary_page.insert_text(fitz.Point(410, y + 15), f"{obtained:.1f}", fontsize=8, color=(0.05, 0.45, 0.2), fontname="helv")
            summary_page.insert_text(fitz.Point(480, y + 15), f"{conf:.2f}", fontsize=8, color=(0.3, 0.3, 0.3), fontname="helv")

            y += 22

        summary_page.draw_rect(fitz.Rect(20, h - 60, w - 20, h - 20), color=(0.9, 0.9, 0.9), fill=(0.97, 0.97, 0.98))
        summary_page.insert_text(fitz.Point(30, h - 40), "Verified by IntelliGrade AI Engine v3.0 & Academic Evaluator", fontsize=8, color=(0.4, 0.4, 0.4), fontname="helv")
        summary_page.insert_text(fitz.Point(w - 210, h - 40), "Teacher Signature: __________________", fontsize=8, color=(0.3, 0.3, 0.3), fontname="helv")
