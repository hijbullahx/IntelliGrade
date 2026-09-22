"""
IntelliGrade Evaluated Script PDF Generator Service.
Generates an annotated, high-resolution PDF document for an evaluated student submission,
featuring page-by-page question headers, mark distributions, rubric breakdowns, AI feedback stamps,
official security watermarking, and strict mapping-driven page overlays.
"""

import os
import fitz  # PyMuPDF
from typing import Optional, List, Dict, Any
from django.conf import settings

from core.models import StudentSubmission, SubmissionPage, SubmissionAnswer, EvaluationResult, QuestionMapping
from core.utils.question_accessor import QuestionAccessor, safe_getattr, safe_normalize_collection, normalize_q_code

class EvaluatedScriptPDFService:
    """
    Generates annotated PDFs of evaluated answer scripts with page-by-page mark distribution overlays
    and tamper-evident anti-tamper security watermarks.
    """

    @classmethod
    def _apply_official_watermark(
        cls,
        page: fitz.Page,
        examination: Any = None,
        angle: float = -45.0,
        opacity: float = 0.12
    ):
        """
        Applies a tamper-evident, multi-layer diagonal security watermark across the PDF page.
        Uses semi-transparent drawing with PyMuPDF shape so student handwriting remains 100% legible.
        """
        try:
            shape = page.new_shape()
            m = fitz.Matrix(angle)
            w, h = page.rect.width, page.rect.height

            course_code = getattr(getattr(examination, 'course', None), 'code', '') or 'IUBAT'
            primary_text = "INTELLIGRADE CERTIFIED EVALUATION"
            secondary_text = f"OFFICIALLY EVALUATED | {course_code}"

            # Band 1: Upper-middle diagonal
            p1 = fitz.Point(w * 0.08, h * 0.38)
            shape.insert_text(p1, primary_text, fontsize=26, color=(0.10, 0.55, 0.30), fontname="helv", morph=(p1, m))
            p1_sub = fitz.Point(w * 0.11, h * 0.41)
            shape.insert_text(p1_sub, secondary_text, fontsize=14, color=(0.15, 0.45, 0.25), fontname="helv", morph=(p1_sub, m))

            # Band 2: Lower-middle diagonal
            p2 = fitz.Point(w * 0.22, h * 0.75)
            shape.insert_text(p2, primary_text, fontsize=26, color=(0.10, 0.55, 0.30), fontname="helv", morph=(p2, m))
            p2_sub = fitz.Point(w * 0.25, h * 0.78)
            shape.insert_text(p2_sub, secondary_text, fontsize=14, color=(0.15, 0.45, 0.25), fontname="helv", morph=(p2_sub, m))

            shape.finish(fill_opacity=opacity, stroke_opacity=opacity + 0.05)
            shape.commit()
        except Exception as e_wm:
            print(f"[WATERMARK WARNING] Failed applying watermark: {e_wm}")

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
        answers = safe_normalize_collection(
            submission.answers.select_related('question', 'evaluation_result', 'page').all().order_by('question__question_number')
        )
        
        # Build strict QuestionMapping registry for this submission (manual teacher override or AI detected)
        q_mappings = {qm.question_id: qm for qm in QuestionMapping.objects.filter(submission=submission)}

        answer_pages_map: Dict[int, List[int]] = {}
        for ans in answers:
            qm = q_mappings.get(ans.question.id)
            if qm and qm.page_numbers_json:
                pgs = [int(p) for p in qm.page_numbers_json if str(p).isdigit() or isinstance(p, (int, float))]
            elif ans.page and ans.page.page_number:
                pgs = [ans.page.page_number]
            else:
                pgs = []
            answer_pages_map[ans.id] = pgs

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

        # Build Annotated Pages using strict question mapping
        if pages:
            total_pages = len(pages)
            for sp in pages:
                img_path = _resolve_page_img(sp.page_number, sp)
                cls._append_annotated_page(
                    doc, img_path, sp.page_number, total_pages,
                    answers, answer_pages_map, submission, examination, page_width, page_height
                )
        elif submission.raw_images.filter(is_deleted=False).exists():
            raw_list = list(submission.raw_images.filter(is_deleted=False).order_by('sequence_order'))
            total_pages = len(raw_list)
            for r_idx, r_img in enumerate(raw_list, 1):
                img_path = r_img.original_file.path if r_img.original_file and os.path.exists(r_img.original_file.path) else None
                cls._append_annotated_page(
                    doc, img_path, r_idx, total_pages,
                    answers, answer_pages_map, submission, examination, page_width, page_height
                )
        elif submission.script_file and os.path.exists(submission.script_file.path):
            orig_doc = fitz.open(submission.script_file.path)
            total_pages = len(orig_doc)
            for p_num in range(total_pages):
                orig_page = orig_doc[p_num]
                pix = orig_page.get_pixmap(dpi=150)
                img_path = os.path.join(output_dir, f'temp_p{p_num+1}_{submission.id}.png')
                pix.save(img_path)
                cls._append_annotated_page(
                    doc, img_path, p_num + 1, total_pages,
                    answers, answer_pages_map, submission, examination, page_width, page_height
                )
                if os.path.exists(img_path):
                    os.remove(img_path)
            orig_doc.close()
        else:
            cls._append_annotated_page(
                doc, None, 1, 1,
                answers, answer_pages_map, submission, examination, page_width, page_height
            )

        # Always append a final comprehensive Scorecard & Rubric Breakdown Page
        cls._append_summary_page(doc, submission, examination, answers, answer_pages_map, page_width, page_height)

        doc.save(pdf_path)
        doc.close()
        return pdf_path

    @classmethod
    def _append_annotated_page(
        cls,
        doc: fitz.Document,
        img_path: Optional[str],
        page_num: int,
        total_pages: int,
        answers: List[SubmissionAnswer],
        answer_pages_map: Dict[int, List[int]],
        submission: StudentSubmission,
        examination: Any,
        w: float,
        h: float
    ):
        """Appends an annotated A4 page containing header banner, student image, security watermark, and mark overlays."""
        pdf_page = doc.new_page(width=w, height=h)

        # 1. Header Banner Box
        header_rect = fitz.Rect(0, 0, w, 55)
        pdf_page.draw_rect(header_rect, color=(0.09, 0.15, 0.28), fill=(0.09, 0.15, 0.28))

        exam_title = examination.title if examination else 'Examination'
        pdf_page.insert_text(
            fitz.Point(15, 20),
            f"IntelliGrade AI Evaluated Script  |  {exam_title}",
            fontsize=10.5,
            color=(1, 1, 1),
            fontname="helv"
        )

        student_info = f"Student: {submission.student_name} (Roll: {submission.student_roll_no or 'N/A'})  |  Script Page {page_num} of {total_pages}"
        pdf_page.insert_text(
            fitz.Point(15, 38),
            student_info,
            fontsize=8.5,
            color=(0.7, 0.8, 0.9),
            fontname="helv"
        )

        score_badge = f"Total Score: {submission.total_obtained_marks} / {submission.total_max_marks} ({submission.percentage}%)"
        pdf_page.insert_text(
            fitz.Point(w - 240, 28),
            score_badge,
            fontsize=9.5,
            color=(0.2, 0.9, 0.5),
            fontname="helv"
        )

        # 2. Identify all answers strictly mapped to THIS specific page
        page_answers = [ans for ans in answers if page_num in answer_pages_map.get(ans.id, [])]

        # Determine dynamic footer height based on number of mapped questions
        if not page_answers:
            footer_h = 70
        elif len(page_answers) == 1:
            footer_h = 130
        elif len(page_answers) == 2:
            footer_h = 165
        else:
            footer_h = min(220, 65 + len(page_answers) * 36)

        footer_top = h - footer_h - 15
        img_top = 60
        img_bottom = footer_top - 6

        # 3. Main Student Answer Script Page Image Placement
        if img_path and os.path.exists(img_path):
            img_rect = fitz.Rect(15, img_top, w - 15, img_bottom)
            pdf_page.insert_image(img_rect, filename=img_path)
            pdf_page.draw_rect(img_rect, color=(0.85, 0.85, 0.85), width=0.5)
        else:
            placeholder_rect = fitz.Rect(15, img_top, w - 15, img_bottom)
            pdf_page.draw_rect(placeholder_rect, color=(0.9, 0.9, 0.9), fill=(0.98, 0.98, 0.99), width=0.5)
            pdf_page.insert_text(fitz.Point(w/2 - 90, img_top + 100), "[Student Script Page Image]", fontsize=12, color=(0.5, 0.5, 0.5), fontname="helv")

        # 4. Anti-Tamper Security Watermark (Floating on top of image with semi-transparency)
        cls._apply_official_watermark(pdf_page, examination=examination)

        # 5. Bottom Footer Banner: Page Mark Distribution & Feedback Overlay
        footer_rect = fitz.Rect(15, footer_top, w - 15, h - 15)
        pdf_page.draw_rect(footer_rect, color=(0.08, 0.35, 0.22), fill=(0.95, 0.98, 0.96), width=1.5)

        # Footer Title Bar
        f_head_rect = fitz.Rect(15, footer_top, w - 15, footer_top + 18)
        pdf_page.draw_rect(f_head_rect, color=(0.08, 0.35, 0.22), fill=(0.08, 0.35, 0.22))

        if page_answers:
            pdf_page.insert_text(
                fitz.Point(22, footer_top + 13),
                f"PAGE {page_num} MAPPED QUESTION EVALUATION & MARKS OVERLAY ({len(page_answers)} Question{'s' if len(page_answers)>1 else ''})",
                fontsize=8.5,
                color=(1, 1, 1),
                fontname="helv"
            )

            y = footer_top + 32
            for idx_q, ans in enumerate(page_answers):
                q = ans.question
                q_num = QuestionAccessor.get_question_number(q)
                q_text = QuestionAccessor.get_text(q)
                if len(q_text) > 75:
                    q_text = q_text[:72] + "..."

                eval_res = getattr(ans, 'evaluation_result', None)
                obtained = float(eval_res.obtained_marks) if eval_res else 0.0
                max_m = float(eval_res.maximum_marks) if eval_res else QuestionAccessor.get_marks(q)

                pg_list = answer_pages_map.get(ans.id, [])
                multi_badge = ""
                if len(pg_list) > 1:
                    try:
                        curr_idx = pg_list.index(page_num) + 1
                        multi_badge = f" [Part {curr_idx}/{len(pg_list)} | Pages: {', '.join(map(str, pg_list))}]"
                    except ValueError:
                        multi_badge = f" [Pages: {', '.join(map(str, pg_list))}]"

                # Question statement
                pdf_page.insert_text(fitz.Point(22, y), f"{normalize_q_code(q_num)}: {q_text}", fontsize=8.5, color=(0.08, 0.08, 0.08), fontname="helv")

                # Marks badge
                pct = (obtained / max_m * 100) if max_m > 0 else 0
                marks_str = f"MARKS: {obtained:.1f} / {max_m:.1f} ({pct:.0f}%){multi_badge}"
                pdf_page.insert_text(fitz.Point(w - 245, y), marks_str, fontsize=8.5, color=(0.05, 0.45, 0.2), fontname="helv")

                # Feedback & Breakdown
                if eval_res and eval_res.feedback_text:
                    fb = eval_res.feedback_text.strip().replace('\n', ' ')
                    if len(page_answers) == 1:
                        fb1 = fb[:110]
                        fb2 = fb[110:220] if len(fb) > 110 else ""
                        pdf_page.insert_text(fitz.Point(30, y + 13), f"Feedback: {fb1}", fontsize=7.5, color=(0.25, 0.25, 0.25), fontname="helv")
                        if fb2:
                            pdf_page.insert_text(fitz.Point(70, y + 23), f"{fb2}...", fontsize=7.5, color=(0.25, 0.25, 0.25), fontname="helv")

                        rb = eval_res.rubric_breakdown_json if isinstance(eval_res.rubric_breakdown_json, list) else []
                        if rb:
                            rb_parts = []
                            for item in rb[:4]:
                                if isinstance(item, dict):
                                    c_name = item.get('criterion') or item.get('step') or 'Criteria'
                                    c_marks = item.get('awarded_marks') if item.get('awarded_marks') is not None else item.get('marks', 0)
                                    rb_parts.append(f"{c_name}: {c_marks}")
                            if rb_parts:
                                pdf_page.insert_text(fitz.Point(30, y + 36), f"Breakdown: {' | '.join(rb_parts)}", fontsize=7.0, color=(0.35, 0.45, 0.40), fontname="helv")
                        y += 50
                    else:
                        fb_short = fb[:85] + ("..." if len(fb) > 85 else "")
                        pdf_page.insert_text(fitz.Point(30, y + 12), f"Feedback: {fb_short}", fontsize=7.5, color=(0.25, 0.25, 0.25), fontname="helv")
                        y += 26
                else:
                    y += 20
        else:
            pdf_page.insert_text(
                fitz.Point(22, footer_top + 13),
                f"PAGE {page_num} GENERAL SCRIPT RECORD (COVER / UNMAPPED PAGE)",
                fontsize=8.5,
                color=(1, 1, 1),
                fontname="helv"
            )
            pdf_page.insert_text(
                fitz.Point(25, footer_top + 32),
                "No evaluated questions are mapped to this page in manual or AI question mapping.",
                fontsize=8.5,
                color=(0.3, 0.3, 0.3),
                fontname="helv"
            )
            pdf_page.insert_text(
                fitz.Point(25, footer_top + 48),
                f"Total Submission Score: {submission.total_obtained_marks} / {submission.total_max_marks} marks ({submission.percentage}%)  |  Status: {submission.status}",
                fontsize=8.0,
                color=(0.08, 0.45, 0.22),
                fontname="helv"
            )

    @classmethod
    def _append_summary_page(
        cls,
        doc: fitz.Document,
        submission: StudentSubmission,
        examination: Any,
        answers: List[SubmissionAnswer],
        answer_pages_map: Dict[int, List[int]],
        w: float,
        h: float
    ):
        """Appends a final Scorecard & Rubric Breakdown summary page with security watermark and mapped pages column."""
        summary_page = doc.new_page(width=w, height=h)

        # Header Box
        summary_page.draw_rect(fitz.Rect(0, 0, w, 70), color=(0.09, 0.15, 0.28), fill=(0.09, 0.15, 0.28))
        summary_page.insert_text(
            fitz.Point(20, 28),
            "FINAL EVALUATION SCORECARD & RUBRIC BREAKDOWN",
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

        # Total Marks Scorebox
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
            f"Evaluation Mode: AI Script Engine  |  Status: {submission.status}  |  Manual Review Needed: {submission.requires_manual_review}",
            fontsize=8,
            color=(0.3, 0.3, 0.3),
            fontname="helv"
        )

        # Table Header
        table_top = 155
        summary_page.draw_rect(fitz.Rect(20, table_top, w - 20, table_top + 22), color=(0.2, 0.2, 0.3), fill=(0.2, 0.2, 0.3))
        summary_page.insert_text(fitz.Point(28, table_top + 15), "Q#", fontsize=8.5, color=(1, 1, 1), fontname="helv")
        summary_page.insert_text(fitz.Point(55, table_top + 15), "Question Statement", fontsize=8.5, color=(1, 1, 1), fontname="helv")
        summary_page.insert_text(fitz.Point(310, table_top + 15), "Script Pages", fontsize=8.5, color=(1, 1, 1), fontname="helv")
        summary_page.insert_text(fitz.Point(385, table_top + 15), "Allocated", fontsize=8.5, color=(1, 1, 1), fontname="helv")
        summary_page.insert_text(fitz.Point(445, table_top + 15), "Obtained", fontsize=8.5, color=(1, 1, 1), fontname="helv")
        summary_page.insert_text(fitz.Point(505, table_top + 15), "Confidence", fontsize=8.5, color=(1, 1, 1), fontname="helv")

        # Table Rows
        y = table_top + 22
        for idx, ans in enumerate(answers, 1):
            q = ans.question
            q_num = QuestionAccessor.get_question_number(q)
            q_text = QuestionAccessor.get_text(q)
            if len(q_text) > 42:
                q_text = q_text[:39] + "..."

            eval_res = getattr(ans, 'evaluation_result', None)
            obtained = float(eval_res.obtained_marks) if eval_res else 0.0
            max_m = float(eval_res.maximum_marks) if eval_res else QuestionAccessor.get_marks(q)
            conf = float(eval_res.confidence) if eval_res else 0.0

            pg_list = answer_pages_map.get(ans.id, [])
            pg_str = ", ".join(map(str, pg_list)) if pg_list else "Unmapped"

            bg_color = (0.96, 0.96, 0.97) if idx % 2 == 0 else (1, 1, 1)
            row_rect = fitz.Rect(20, y, w - 20, y + 22)
            summary_page.draw_rect(row_rect, color=(0.85, 0.85, 0.85), fill=bg_color, width=0.5)

            summary_page.insert_text(fitz.Point(28, y + 15), f"{normalize_q_code(q_num)}", fontsize=8, color=(0.1, 0.1, 0.1), fontname="helv")
            summary_page.insert_text(fitz.Point(55, y + 15), q_text, fontsize=8, color=(0.2, 0.2, 0.2), fontname="helv")
            summary_page.insert_text(fitz.Point(310, y + 15), f"Page {pg_str}", fontsize=8, color=(0.1, 0.3, 0.6), fontname="helv")
            summary_page.insert_text(fitz.Point(385, y + 15), f"{max_m:.1f}", fontsize=8, color=(0.1, 0.1, 0.1), fontname="helv")
            summary_page.insert_text(fitz.Point(445, y + 15), f"{obtained:.1f}", fontsize=8, color=(0.05, 0.45, 0.2), fontname="helv")
            summary_page.insert_text(fitz.Point(505, y + 15), f"{conf:.2f}", fontsize=8, color=(0.3, 0.3, 0.3), fontname="helv")

            y += 22

        # Anti-Tamper Security Watermark on Scorecard Page
        cls._apply_official_watermark(summary_page, examination=examination)

        # Footer Signature Strip
        summary_page.draw_rect(fitz.Rect(20, h - 60, w - 20, h - 20), color=(0.9, 0.9, 0.9), fill=(0.97, 0.97, 0.98))
        summary_page.insert_text(fitz.Point(30, h - 40), "Verified by IntelliGrade AI Engine & Academic Evaluator", fontsize=8, color=(0.4, 0.4, 0.4), fontname="helv")
        summary_page.insert_text(fitz.Point(w - 210, h - 40), "Teacher Signature: __________________", fontsize=8, color=(0.3, 0.3, 0.3), fontname="helv")
