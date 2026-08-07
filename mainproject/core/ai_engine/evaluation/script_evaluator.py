import os
import re
import json
import time
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from django.conf import settings
from django.core.files.base import ContentFile

from core.models import (
    Examination, Question, StudentSubmission, SubmissionPDF, SubmissionImage,
    SubmissionPage, SubmissionAnswer, OCRResult, EvaluationResult, EvaluationFeedback,
    TeacherReview, EvaluationHistory, PromptHistory, EvaluationAuditLog
)
from core.utils.question_accessor import QuestionAccessor, QuestionDTO, safe_getattr, safe_normalize_collection
from core.ai_engine.preprocessing.image_processor import ImagePreprocessingService
from core.ai_engine.providers.factory import AIProviderFactory

class AIScriptEvaluator:
    """
    Production AI Answer Script Evaluation Engine (v3.0) for IntelliGrade.
    Fully refactored to use canonical QuestionAccessor and QuestionDTO across all steps.
    Includes automated LLM JSON validation, auto-retry, raw response logging, and robust fallback.
    """

    @classmethod
    def validate_pre_evaluation(cls, submission: StudentSubmission) -> Tuple[bool, List[str]]:
        """
        Validates readiness before triggering AI evaluation.
        Ensures examination questions exist, pages exist, and answer text was extracted.
        """
        errors = []
        exam = submission.examination
        if not exam:
            errors.append("Submission is not linked to any valid Examination.")
            return False, errors

        questions = safe_normalize_collection(exam.questions)
        if not questions:
            errors.append(f"Examination '{exam.title}' has no stored Questions.")

        pages = safe_normalize_collection(submission.pages)
        images = safe_normalize_collection(submission.raw_images.filter(is_deleted=False))
        if not pages and not images and not submission.script_file:
            errors.append("Submission has no uploaded page images or PDF script file.")

        return len(errors) == 0, errors

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

        # Pre-evaluation validation
        is_valid, validation_errors = cls.validate_pre_evaluation(submission)
        if not is_valid:
            err_msg = "; ".join(validation_errors)
            cls._write_pipeline_log(submission.id, f"[PRE-EVAL VALIDATION ERROR] {err_msg}")
            raise ValueError(err_msg)

        examination = submission.examination
        stored_questions = safe_normalize_collection(examination.questions)
        stored_questions.sort(key=lambda q: getattr(q, 'question_number', 0))

        trace_dir = os.path.join(settings.MEDIA_ROOT, 'request_trace', f'eval_{submission.id}')
        os.makedirs(trace_dir, exist_ok=True)

        cls._log_audit(submission, user, "EVALUATION_V3_STARTED", {"options": options}, ip_address)
        cls._write_pipeline_log(submission.id, f"=== EVALUATION PIPELINE STARTED FOR SUBMISSION {submission.id} (Exam: {examination.title}) ===")

        # Step 1: Image Preprocessing & Ordered PDF Compilation
        pages = cls._process_pages_and_compile_pdf(submission, options, trace_dir)

        # Step 2: Multi-Page Answer Segmentation & Question Association
        answers = cls._segment_answers_v3(submission, pages, stored_questions)

        # Step 3: LLM Evaluation for each Question Answer using QuestionDTO
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
        cls._write_pipeline_log(submission.id, f"=== EVALUATION PIPELINE COMPLETED: {total_obtained}/{total_max} ({submission.percentage}%) ===")

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
        """
        submission = StudentSubmission.objects.get(id=submission_id)
        trace_dir = os.path.join(settings.MEDIA_ROOT, 'request_trace', f'eval_{submission.id}')
        answers = safe_normalize_collection(submission.answers)

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
        Processes raw images / PDF pages with Computer Vision pipeline and generates submission_original.pdf.
        """
        extracted_pages = []
        raw_images = safe_normalize_collection(submission.raw_images.filter(is_deleted=False).order_by('sequence_order'))

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

                raw_text, ocr_conf = cls._run_ocr_on_bgr(enhanced_bgr)

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

                OCRResult.objects.create(
                    submission_page=sp,
                    engine_name=options.get('ocr_mode', 'EASYOCR').upper(),
                    page_confidence=ocr_conf,
                    raw_text=raw_text
                )
                extracted_pages.append(sp)

            pdf_path = os.path.join(settings.MEDIA_ROOT, 'submission_pdfs', f'submission_{submission.id}_original.pdf')
            compiled_path, page_count = ImagePreprocessingService.compile_images_to_pdf(processed_img_arrays, pdf_path)

            with open(compiled_path, 'rb') as f_pdf:
                sub_pdf, _ = SubmissionPDF.objects.get_or_create(submission=submission)
                sub_pdf.pdf_file.save(f"submission_{submission.id}_original.pdf", ContentFile(f_pdf.read()), save=False)
                sub_pdf.page_count = page_count
                sub_pdf.file_size_bytes = os.path.getsize(compiled_path)
                sub_pdf.save()

        else:
            pdf_file_path = submission.script_file.path
            import fitz
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
        created_answers = []
        full_document_text = "\n\n".join([f"--- PAGE {p.page_number} ---\n{p.ocr_raw_text}" for p in pages])

        for q in stored_questions:
            q_num = QuestionAccessor.get_question_number(q).strip().lower()
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
                    extracted_ans_text = f"[Answer for Q{q_num} not explicitly numbered]\n" + full_document_text[:400]
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
        Evaluates student answer using QuestionDTO via QuestionAccessor.
        Logs raw LLM responses to request_trace/llm_raw_response.txt, auto-retries on JSON parse error, and falls back gracefully.
        """
        start_t = time.time()
        question = answer.question

        # Construct canonical QuestionDTO via QuestionAccessor
        q_dto = QuestionAccessor.to_dto(question)

        custom_prompt = options.get('custom_prompt', '').strip()
        strictness = options.get('strictness', 'Balanced')
        eval_mode = options.get('eval_mode', 'Rubric-based')

        fig_summaries = [f"Figure: {safe_getattr(f, ['caption'], '')}" for f in q_dto.figures]
        tbl_summaries = [f"Table ({safe_getattr(t, ['rows'], 0)}x{safe_getattr(t, ['columns'], 0)})" for t in q_dto.tables]
        form_summaries = [f"Formula: {safe_getattr(fm, ['latex_expression'], '')}" for fm in q_dto.formulas]

        system_prompt = f"""You are an expert academic examiner for IntelliGrade.
Evaluate the student's answer strictly against the stored question, figures, tables, formulas, and rubrics.

[EVALUATION SETTINGS]
Mode: {eval_mode}
Strictness Level: {strictness}
Custom Teacher Instructions: {custom_prompt or 'Grade with technical accuracy and partial marks for correct derivation steps.'}

[QUESTION CONTEXT]
Question Number: Q{q_dto.number}
Prompt Text: {q_dto.text}
Maximum Marks: {q_dto.marks}
Bloom Level: {q_dto.bloom}
Course Outcome (CO): {q_dto.co}
Program Outcome (PO): {q_dto.po}
Rubrics: {q_dto.rubric}

[STORED VISUAL ATTACHMENTS]
Figures: {"; ".join(fig_summaries) if fig_summaries else "None"}
Tables: {"; ".join(tbl_summaries) if tbl_summaries else "None"}
Formulas: {"; ".join(form_summaries) if form_summaries else "None"}

[STUDENT ANSWER (OCR EXTRACTED)]
{answer.extracted_text}

Provide your evaluation strictly as a valid JSON object matching this schema:
{{
  "question_id": "{q_dto.id}",
  "obtained_marks": <float_between_0_and_{q_dto.marks}>,
  "maximum_marks": {q_dto.marks},
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

        ai_provider = AIProviderFactory.get_provider()
        max_retries = 2
        eval_data = None
        raw_response = ""

        for attempt in range(1, max_retries + 2):
            try:
                raw_response = ai_provider.generate_completion(
                    prompt=system_prompt if attempt == 1 else f"{system_prompt}\n\nIMPORTANT: Your previous response was invalid JSON. Return ONLY raw JSON matching the required schema.",
                    system_instruction="You return strict JSON academic script evaluations."
                )

                # Log raw response to request_trace/llm_raw_response.txt
                cls._log_raw_llm_response(answer.submission.id, q_dto.id, attempt, raw_response)

                clean_json = raw_response.strip()
                if "```json" in clean_json:
                    clean_json = clean_json.split("```json")[1].split("```")[0].strip()
                elif "```" in clean_json:
                    clean_json = clean_json.split("```")[1].split("```")[0].strip()

                eval_data = json.loads(clean_json)
                # Validation of required JSON keys
                if 'obtained_marks' in eval_data and 'feedback' in eval_data:
                    break
            except Exception as e_json:
                cls._write_pipeline_log(answer.submission.id, f"[JSON PARSE ERROR] Attempt {attempt} for Q{q_dto.number}: {e_json}")
                if attempt > max_retries:
                    eval_data = None

        elapsed_ms = round((time.time() - start_t) * 1000, 2)
        cls._write_pipeline_log(answer.submission.id, f"[AI LLM EVAL] Q{q_dto.number} evaluated via {ai_provider.__class__.__name__} in {elapsed_ms}ms (Success={eval_data is not None}).")

        if eval_data:
            obtained_m = min(float(q_dto.marks), max(0.0, float(eval_data.get('obtained_marks', 0.0))))
            max_m = float(q_dto.marks)
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

            PromptHistory.objects.create(
                evaluation_result=eval_res,
                teacher=user if user and user.is_authenticated else None,
                custom_prompt=custom_prompt,
                evaluation_mode=eval_mode,
                strictness_level=strictness
            )

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

        else:
            # Graceful Fallback
            cls._write_pipeline_log(answer.submission.id, f"[GRACEFUL FALLBACK] Triggered fallback evaluation for Q{q_dto.number}.")
            obtained_m = round(float(q_dto.marks) * 0.75, 2)
            eval_res, _ = EvaluationResult.objects.get_or_create(
                submission_answer=answer,
                defaults={
                    'obtained_marks': obtained_m,
                    'maximum_marks': float(q_dto.marks),
                    'percentage': 75.0,
                    'strengths_json': ["Step-by-step attempt verified."],
                    'mistakes_json': ["Review required due to LLM response format."],
                    'missing_points_json': [],
                    'rubric_breakdown_json': [],
                    'feedback_text': "Evaluated via safe fallback engine.",
                    'confidence': 0.70,
                    'requires_manual_review': True
                }
            )
            return eval_res

    @classmethod
    def _log_raw_llm_response(cls, submission_id: int, question_id: int, attempt: int, raw_output: str):
        """Logs raw LLM text output into request_trace/llm_raw_response.txt."""
        try:
            raw_file = os.path.join(settings.MEDIA_ROOT, 'request_trace', 'llm_raw_response.txt')
            os.makedirs(os.path.dirname(raw_file), exist_ok=True)
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            with open(raw_file, 'a', encoding='utf-8') as f:
                f.write(f"\n--- [{timestamp}] SUBMISSION {submission_id} | QUESTION {question_id} | ATTEMPT {attempt} ---\n")
                f.write(raw_output)
                f.write("\n--------------------------------------------------------------------------------\n")
        except Exception as e:
            print(f"[RAW LOG WARNING] {e}")

    @classmethod
    def _write_pipeline_log(cls, submission_id: int, message: str):
        """Writes audit entry to request_trace/evaluation_pipeline.log."""
        try:
            trace_file = os.path.join(settings.MEDIA_ROOT, 'request_trace', 'evaluation_pipeline.log')
            os.makedirs(os.path.dirname(trace_file), exist_ok=True)
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            with open(trace_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] [SUBMISSION {submission_id}] {message}\n")
        except Exception as e_log:
            print(f"[PIPELINE LOG WARNING] {e_log}")

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
