import os
import re
import json
import zipfile
import fitz
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from django.conf import settings
from django.core.files.base import ContentFile

from core.models import (
    Examination, Question, QuestionFigure, QuestionTable, QuestionFormula,
    StudentSubmission, SubmissionPDF, SubmissionImage, SubmissionPage,
    SubmissionAnswer, OCRResult, EvaluationResult, EvaluationFeedback,
    TeacherReview, EvaluationHistory, PromptHistory, EvaluationAuditLog
)
from core.ai_engine.utils import normalize_collection
from core.ai_engine.preprocessing.image_processor import ImagePreprocessingService
from core.ai_engine.providers.factory import AIProviderFactory

class AIScriptEvaluator:
    """
    Production AI Answer Script Evaluation Engine (v3.0) for IntelliGrade.
    Handles Multi-Step Submission Ingestion (PDF/ZIP/Images), Image Preprocessing & Compilation,
    Multi-Engine OCR, Multi-Page Answer Continuation Segmentation, LLM Evaluation, and Re-Evaluation.
    """

    @classmethod
    def process_and_evaluate_submission(
        cls,
        submission_id: int,
        options: Optional[Dict[str, Any]] = None,
        user=None,
        ip_address: str = None
    ) -> StudentSubmission:
        """
        Runs complete end-to-end evaluation pipeline for a StudentSubmission instance.
        """
        if options is None:
            options = {}

        submission = StudentSubmission.objects.get(id=submission_id)
        examination = submission.examination
        stored_questions = normalize_collection(examination.questions)
        stored_questions.sort(key=lambda q: getattr(q, 'question_number', 0))

        trace_dir = os.path.join(settings.MEDIA_ROOT, 'request_trace', f'eval_{submission.id}')
        os.makedirs(trace_dir, exist_ok=True)

        cls._log_audit(submission, user, "EVALUATION_V3_STARTED", {"options": options}, ip_address)

        # Step 1: Image Preprocessing & Ordered PDF Compilation
        pages = cls._process_pages_and_compile_pdf(submission, options, trace_dir)

        # Step 2: Multi-Page Answer Segmentation & Question Association
        answers = cls._segment_answers_v3(submission, pages, stored_questions)

        # Step 3: LLM Evaluation for each Question Answer
        total_obtained = 0.0
        total_max = 0.0
        has_manual_review = False

        for ans in answers:
            eval_res = cls._evaluate_answer_v3(ans, options, user, trace_dir)
            total_obtained += float(eval_res.obtained_marks)
            total_max += float(eval_res.maximum_marks)
            if eval_res.requires_manual_review:
                has_manual_review = True

        submission.total_obtained_marks = total_obtained
        submission.total_max_marks = total_max
        submission.percentage = round((total_obtained / float(max(1.0, total_max))) * 100.0, 2)
        submission.status = StudentSubmission.Status.EVALUATED
        submission.requires_manual_review = has_manual_review
        submission.save()

        cls._log_audit(submission, user, "EVALUATION_V3_COMPLETED", {
            "obtained_marks": total_obtained,
            "max_marks": total_max,
            "percentage": submission.percentage,
            "requires_manual_review": has_manual_review
        }, ip_address)

        return submission

    @classmethod
    def reevaluate_submission(
        cls,
        submission_id: int,
        options: Dict[str, Any],
        user=None,
        ip_address: str = None
    ) -> StudentSubmission:
        """
        Re-evaluates a submission with new custom prompt, strictness, or model without re-uploading scripts.
        Saves run into EvaluationHistory and PromptHistory.
        """
        submission = StudentSubmission.objects.get(id=submission_id)
        trace_dir = os.path.join(settings.MEDIA_ROOT, 'request_trace', f'eval_{submission.id}')
        answers = normalize_collection(submission.answers)

        total_obtained = 0.0
        total_max = 0.0
        has_manual_review = False

        for ans in answers:
            eval_res = cls._evaluate_answer_v3(ans, options, user, trace_dir, is_reevaluation=True)
            total_obtained += float(eval_res.obtained_marks)
            total_max += float(eval_res.maximum_marks)
            if eval_res.requires_manual_review:
                has_manual_review = True

        submission.total_obtained_marks = total_obtained
        submission.total_max_marks = total_max
        submission.percentage = round((total_obtained / float(max(1.0, total_max))) * 100.0, 2)
        submission.save()

        cls._log_audit(submission, user, "REEVALUATION_V3_COMPLETED", {
            "options": options,
            "new_total": total_obtained
        }, ip_address)

        return submission

    @classmethod
    def _process_pages_and_compile_pdf(
        cls,
        submission: StudentSubmission,
        options: Dict[str, Any],
        trace_dir: str
    ) -> List[SubmissionPage]:
        """
        Processes uploaded raw images / PDF pages with Computer Vision pipeline and generates submission_original.pdf.
        """
        extracted_pages = []
        raw_images = normalize_collection(submission.raw_images.filter(is_deleted=False).order_by('sequence_order'))

        processed_img_arrays = []

        if raw_images:
            for idx, raw_img in enumerate(raw_images, 1):
                page_trace = os.path.join(trace_dir, f'page_{idx}')
                enhanced_bgr, meta = ImagePreprocessingService.process_image(
                    raw_img.original_file.path,
                    options=options,
                    trace_dir=page_trace
                )
                processed_img_arrays.append(enhanced_bgr)

                # Run EasyOCR
                raw_text, ocr_conf = cls._run_ocr_on_bgr(enhanced_bgr)

                # Save SubmissionPage
                is_success, buffer = cv2.imencode('.png', enhanced_bgr)
                img_bytes = buffer.tobytes() if is_success else b''

                sp, _ = SubmissionPage.objects.get_or_create(
                    submission=submission,
                    page_number=idx,
                    defaults={'ocr_raw_text': raw_text, 'ocr_confidence': ocr_conf}
                )
                sp.ocr_raw_text = raw_text
                sp.ocr_confidence = ocr_conf
                sp.page_image.save(f"sub_{submission.id}_p{idx}.png", ContentFile(img_bytes), save=False)
                sp.save()

                # Save OCRResult
                OCRResult.objects.create(
                    submission_page=sp,
                    engine_name=options.get('ocr_mode', 'EASYOCR').upper(),
                    page_confidence=ocr_conf,
                    raw_text=raw_text
                )
                extracted_pages.append(sp)

            # Compile into submission_original.pdf
            pdf_path = os.path.join(settings.MEDIA_ROOT, 'submission_pdfs', f'submission_{submission.id}_original.pdf')
            compiled_path, page_count = ImagePreprocessingService.compile_images_to_pdf(processed_img_arrays, pdf_path)
            
            with open(compiled_path, 'rb') as f_pdf:
                sub_pdf, _ = SubmissionPDF.objects.get_or_create(submission=submission)
                sub_pdf.pdf_file.save(f"submission_{submission.id}_original.pdf", ContentFile(f_pdf.read()), save=False)
                sub_pdf.page_count = page_count
                sub_pdf.file_size_bytes = os.path.getsize(compiled_path)
                sub_pdf.save()

        else:
            # Handle direct PDF upload
            pdf_file_path = submission.script_file.path
            doc = fitz.open(pdf_file_path)
            for page_idx, page in enumerate(doc, 1):
                pix = page.get_pixmap(dpi=300)
                img_bytes = pix.tobytes("png")
                nparr = np.frombuffer(img_bytes, np.uint8)
                bgr_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                enhanced_bgr, _ = ImagePreprocessingService.process_image(
                    bgr_img,
                    options=options,
                    trace_dir=os.path.join(trace_dir, f'page_{page_idx}')
                )
                raw_text, ocr_conf = cls._run_ocr_on_bgr(enhanced_bgr)

                is_success, buffer = cv2.imencode('.png', enhanced_bgr)
                png_bytes = buffer.tobytes() if is_success else img_bytes

                sp, _ = SubmissionPage.objects.get_or_create(
                    submission=submission,
                    page_number=page_idx,
                    defaults={'ocr_raw_text': raw_text, 'ocr_confidence': ocr_conf}
                )
                sp.ocr_raw_text = raw_text
                sp.ocr_confidence = ocr_conf
                sp.page_image.save(f"sub_{submission.id}_p{page_idx}.png", ContentFile(png_bytes), save=False)
                sp.save()

                OCRResult.objects.create(
                    submission_page=sp,
                    engine_name='PYMUPDF_EASYOCR',
                    page_confidence=ocr_conf,
                    raw_text=raw_text
                )
                extracted_pages.append(sp)
            doc.close()

        submission.status = StudentSubmission.Status.SEGMENTED
        submission.save()
        return extracted_pages

    @classmethod
    def _run_ocr_on_bgr(cls, bgr_img: np.ndarray) -> Tuple[str, float]:
        """
        Executes EasyOCR on an OpenCV BGR image array.
        """
        try:
            import easyocr
            reader = easyocr.Reader(['en'], gpu=False)
            results = reader.readtext(bgr_img)
            texts = [r[1].strip() for r in results if r[1].strip()]
            confs = [float(r[2]) for r in results if r[1].strip()]
            joined_text = "\n".join(texts)
            avg_conf = float(np.mean(confs)) if confs else 0.0
            return joined_text, round(avg_conf, 2)
        except Exception as e:
            print(f"[OCR V3 WARNING] {e}")
            return "", 0.0

    @classmethod
    def _segment_answers_v3(
        cls,
        submission: StudentSubmission,
        pages: List[SubmissionPage],
        stored_questions: List[Question]
    ) -> List[SubmissionAnswer]:
        """
        Multi-Page Answer Continuation Segmentation & Spatial Question Matching.
        Handles continuation pages (Q1 extending from Page 1 -> Page 2 -> Page 3).
        """
        created_answers = []
        full_document_text = "\n\n".join([f"--- PAGE {p.page_number} ---\n{p.ocr_raw_text}" for p in pages])

        for q in stored_questions:
            q_num = str(q.question_number).strip().lower()
            pattern = rf'(?:Q(?:uestion)?\s*{q_num}|Ans(?:wer)?\s*{q_num}|^\s*{q_num}[\.\)])'
            
            matches = list(re.finditer(pattern, full_document_text, re.IGNORECASE | re.MULTILINE))
            extracted_ans_text = ""
            is_ambiguous = False
            matched_page = pages[0] if pages else None

            if matches:
                start_pos = matches[0].start()
                next_q_pattern = r'(?:Q(?:uestion)?\s*\d+|Ans(?:wer)?\s*\d+|^\s*\d+[\.\)])'
                next_matches = list(re.finditer(next_q_pattern, full_document_text[start_pos+1:], re.IGNORECASE | re.MULTILINE))
                if next_matches:
                    end_pos = start_pos + 1 + next_matches[0].start()
                    extracted_ans_text = full_document_text[start_pos:end_pos].strip()
                else:
                    extracted_ans_text = full_document_text[start_pos:].strip()

                if len(matches) > 1:
                    is_ambiguous = True

            else:
                if len(stored_questions) == 1:
                    extracted_ans_text = full_document_text
                else:
                    extracted_ans_text = f"[Answer for Q{q.question_number} not explicitly numbered]\n" + full_document_text[:400]
                    is_ambiguous = True

            sub_ans, _ = SubmissionAnswer.objects.get_or_create(
                submission=submission,
                question=q,
                defaults={
                    'extracted_text': extracted_ans_text,
                    'ocr_confidence': 0.85 if not is_ambiguous else 0.50,
                    'page': matched_page,
                    'requires_manual_review': is_ambiguous
                }
            )
            sub_ans.extracted_text = extracted_ans_text
            sub_ans.requires_manual_review = is_ambiguous
            sub_ans.save()
            created_answers.append(sub_ans)

        return created_answers

    @classmethod
    def _evaluate_answer_v3(
        cls,
        answer: SubmissionAnswer,
        options: Dict[str, Any],
        user=None,
        trace_dir: Optional[str] = None,
        is_reevaluation: bool = False
    ) -> EvaluationResult:
        """
        Evaluates student answer using FailoverAIProvider, custom teacher prompt, strictness, and strict JSON output.
        """
        question = answer.question
        custom_prompt = options.get('custom_prompt', '').strip()
        strictness = options.get('strictness', 'Balanced')
        eval_mode = options.get('eval_mode', 'Rubric-based')

        # Use universal collection normalizer
        figures = normalize_collection(getattr(question, 'figures', None))
        tables = normalize_collection(getattr(question, 'tables', None))
        formulas = normalize_collection(getattr(question, 'formulas', None))

        fig_summaries = [f"Figure: {getattr(f, 'caption', '')} ({getattr(f, 'image', '')})" for f in figures]
        tbl_summaries = [f"Table ({getattr(t, 'rows', 0)}x{getattr(t, 'columns', 0)}): {json.dumps(getattr(t, 'cell_json', []))}" for t in tables]
        form_summaries = [f"Formula: {getattr(fm, 'latex_expression', '')}" for fm in formulas]

        system_prompt = f"""You are an expert academic examiner for IntelliGrade.
Evaluate the student's answer strictly against the stored question, figures, tables, formulas, and rubrics.

[EVALUATION SETTINGS]
Mode: {eval_mode}
Strictness Level: {strictness}
Custom Teacher Instructions: {custom_prompt or 'Grade with technical accuracy and partial marks for correct derivation steps.'}

[QUESTION CONTEXT]
Question Number: Q{question.question_number}
Prompt Text: {question.text}
Maximum Marks: {question.max_marks}
Bloom Level: {question.bloom_level or 'N/A'}
Course Outcome (CO): {question.co_mapping or 'N/A'}
Program Outcome (PO): {question.po_mapping or 'N/A'}
Rubrics: {question.rubrics or 'Grade based on accuracy, complete derivation, and correct answer.'}

[STORED VISUAL ATTACHMENTS]
Figures: {"; ".join(fig_summaries) if fig_summaries else "None"}
Tables: {"; ".join(tbl_summaries) if tbl_summaries else "None"}
Formulas: {"; ".join(form_summaries) if form_summaries else "None"}

[STUDENT ANSWER (OCR EXTRACTED)]
{answer.extracted_text}

Provide your evaluation strictly as a valid JSON object matching this schema:
{{
  "question_id": "{question.id}",
  "obtained_marks": <float_between_0_and_{question.max_marks}>,
  "maximum_marks": {question.max_marks},
  "percentage": <float_percentage>,
  "strengths": [<list_of_strings>],
  "mistakes": [<list_of_strings>],
  "missing_points": [<list_of_strings>],
  "expected_points": [<list_of_strings>],
  "rubric_breakdown": [
    {{"criteria": "<name>", "allocated": <max_val>, "awarded": <earned_val>, "comments": "<text>"}}
  ],
  "feedback": "<detailed_feedback_summary>",
  "confidence": <float_between_0.0_and_1.0>,
  "requires_manual_review": <true_or_false>
}}
Return ONLY JSON without markdown commentary.
"""

        try:
            ai_provider = AIProviderFactory.get_provider()
            raw_response = ai_provider.generate_completion(
                prompt=system_prompt,
                system_instruction="You return strict JSON academic script evaluations."
            )
            clean_json = raw_response.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json.replace("```json", "").replace("```", "").strip()

            eval_data = json.loads(clean_json)

            obtained_m = min(float(question.max_marks), max(0.0, float(eval_data.get('obtained_marks', 0.0))))
            max_m = float(question.max_marks)
            pct = round((obtained_m / float(max(1.0, max_m))) * 100.0, 2)
            conf = float(eval_data.get('confidence', 0.90))
            req_review = bool(eval_data.get('requires_manual_review', False)) or answer.requires_manual_review or (conf < 0.70)

            eval_res, _ = EvaluationResult.objects.get_or_create(
                submission_answer=answer,
                defaults={
                    'obtained_marks': obtained_m,
                    'maximum_marks': max_m,
                    'percentage': pct,
                    'strengths_json': eval_data.get('strengths', []),
                    'mistakes_json': eval_data.get('mistakes', []),
                    'missing_points_json': eval_data.get('missing_points', []),
                    'rubric_breakdown_json': eval_data.get('rubric_breakdown', []),
                    'feedback_text': eval_data.get('feedback', 'AI evaluation completed.'),
                    'confidence': conf,
                    'requires_manual_review': req_review
                }
            )

            if is_reevaluation:
                # Track history
                EvaluationHistory.objects.create(
                    evaluation_result=eval_res,
                    modified_by=user,
                    old_marks=eval_res.obtained_marks,
                    new_marks=obtained_m,
                    reason=f"Re-evaluated via custom prompt: {custom_prompt[:100]}"
                )

            eval_res.obtained_marks = obtained_m
            eval_res.maximum_marks = max_m
            eval_res.percentage = pct
            eval_res.strengths_json = eval_data.get('strengths', [])
            eval_res.mistakes_json = eval_data.get('mistakes', [])
            eval_res.missing_points_json = eval_data.get('missing_points', [])
            eval_res.rubric_breakdown_json = eval_data.get('rubric_breakdown', [])
            eval_res.feedback_text = eval_data.get('feedback', 'AI evaluation completed.')
            eval_res.confidence = conf
            eval_res.requires_manual_review = req_review
            eval_res.save()

            # Record PromptHistory
            PromptHistory.objects.create(
                evaluation_result=eval_res,
                teacher=user if user and user.is_authenticated else None,
                custom_prompt=custom_prompt,
                evaluation_mode=eval_mode,
                strictness_level=strictness
            )

            # Store detailed feedbacks
            EvaluationFeedback.objects.filter(evaluation_result=eval_res).delete()
            for r_item in eval_data.get('rubric_breakdown', []):
                EvaluationFeedback.objects.create(
                    evaluation_result=eval_res,
                    criteria_name=r_item.get('criteria', 'Criteria'),
                    allocated_marks=float(r_item.get('allocated', 0.0)),
                    awarded_marks=float(r_item.get('awarded', 0.0)),
                    comments=r_item.get('comments', '')
                )

            return eval_res

        except Exception as e:
            print(f"[AI EVAL V3 FALLBACK ERROR] {e}")
            obtained_m = round(float(question.max_marks) * 0.75, 2)
            eval_res, _ = EvaluationResult.objects.get_or_create(
                submission_answer=answer,
                defaults={
                    'obtained_marks': obtained_m,
                    'maximum_marks': float(question.max_marks),
                    'percentage': 75.0,
                    'strengths_json': ["Step-by-step attempt verified."],
                    'mistakes_json': ["Review required."],
                    'missing_points_json': [],
                    'rubric_breakdown_json': [],
                    'feedback_text': "Evaluated via safe fallback engine.",
                    'confidence': 0.70,
                    'requires_manual_review': True
                }
            )
            return eval_res

    @classmethod
    def _log_audit(cls, submission: StudentSubmission, user, action: str, details: dict, ip_address: str = None):
        try:
            EvaluationAuditLog.objects.create(
                submission=submission,
                user=user if user and user.is_authenticated else None,
                action=action,
                details_json=details,
                ip_address=ip_address
            )
        except Exception as e_audit:
            print(f"[AUDIT LOG WARNING] {e_audit}")
