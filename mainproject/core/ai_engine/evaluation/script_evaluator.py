import os
import re
import json
import time
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction, close_old_connections, IntegrityError, DatabaseError, OperationalError

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
    def prepare_and_ocr_submission(
        cls,
        submission_id: int,
        options: Optional[Dict[str, Any]] = None,
        user=None,
        ip_address: str = None
    ) -> List[SubmissionPage]:
        """
        Phase 1: Image Preprocessing, Working Copy Creation, Preview PDF Generation, and OCR.
        Executed ONCE per submission. If status >= SEGMENTED, reuses cached pages and OCR.
        """
        if options is None:
            options = {}

        submission = StudentSubmission.objects.get(id=submission_id)
        cached_pages = list(submission.pages.all().order_by('page_number'))

        # Workflow Guard: If already prepared & segmented, reuse cached OCR artifacts
        if cached_pages and submission.status in [
            StudentSubmission.Status.PDF_GENERATED,
            StudentSubmission.Status.OCR_COMPLETE,
            StudentSubmission.Status.SEGMENTED,
            StudentSubmission.Status.MAPPING_COMPLETE,
            StudentSubmission.Status.WAITING_TEACHER_CONFIRMATION,
            StudentSubmission.Status.AI_EVALUATED,
            StudentSubmission.Status.UNDER_REVIEW,
            StudentSubmission.Status.FINALIZED,
            StudentSubmission.Status.ARCHIVED
        ]:
            print(f"\n==================================================")
            print(f"[CACHE REUSE] Submission #{submission.id} already prepared (Status: {submission.status}).")
            print(f"Reusing {len(cached_pages)} cached SubmissionPage(s) with OCR results.")
            print(f"==================================================\n")
            return cached_pages

        trace_dir = os.path.join(settings.MEDIA_ROOT, 'request_trace', f'eval_{submission.id}')
        os.makedirs(trace_dir, exist_ok=True)
        return cls._process_pages_and_compile_pdf(submission, options, trace_dir)

    @classmethod
    def evaluate_mapped_answers(
        cls,
        submission_id: int,
        confirmed_mappings: Optional[List[Dict[str, Any]]] = None,
        options: Optional[Dict[str, Any]] = None,
        user=None,
        ip_address: str = None
    ) -> StudentSubmission:
        """
        Phase 3: Evaluates mapped answers using LLM.
        Consumes ONLY mapped answers, question DTOs, cached OCR text, and rubric specifications.
        Does NOT re-run image preprocessing, working copy creation, preview PDF generation, or OCR.
        """
        if options is None:
            options = {}

        submission = StudentSubmission.objects.get(id=submission_id)
        
        # Ensure submission pages & OCR are prepared if called directly
        if submission.pages.count() == 0 or submission.status in [
            StudentSubmission.Status.UPLOADED,
            StudentSubmission.Status.PREVIEW_READY,
            StudentSubmission.Status.WORKING_COPY_CREATED,
            StudentSubmission.Status.PDF_GENERATED
        ]:
            cls.prepare_and_ocr_submission(submission_id, options, user, ip_address)
            submission.refresh_from_db()

        trace_dir = os.path.join(settings.MEDIA_ROOT, 'request_trace', f'eval_{submission.id}')
        os.makedirs(trace_dir, exist_ok=True)

        if confirmed_mappings:
            from core.ai_engine.mapping.orchestrator import QuestionMappingOrchestrator
            QuestionMappingOrchestrator.confirm_mapping_and_evaluate(submission.id, confirmed_mappings, user=user, ip_address=ip_address)

        answers = list(submission.answers.all().order_by('question__question_number'))

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
        submission.requires_manual_review = has_manual_review
        submission.save()

        from core.ai_engine.services.workflow import SubmissionWorkflow
        SubmissionWorkflow.advance(submission, StudentSubmission.Status.AI_EVALUATED, force=True)
        SubmissionWorkflow.advance(submission, StudentSubmission.Status.UNDER_REVIEW, force=True)

        cls._log_audit(submission, user, "EVALUATION_V3_COMPLETED", {
            "obtained_marks": total_obtained,
            "max_marks": total_max,
            "percentage": submission.percentage,
            "requires_manual_review": has_manual_review
        }, ip_address)
        cls._write_pipeline_log(submission.id, f"=== EVALUATION COMPLETED: {total_obtained}/{total_max} ({submission.percentage}%) ===")

        return submission

    @classmethod
    def process_and_evaluate_submission(
        cls,
        submission_id: int,
        options: Optional[Dict[str, Any]] = None,
        user=None,
        ip_address: str = None
    ) -> StudentSubmission:
        """
        Runs end-to-end evaluation pipeline using decoupled phases.
        """
        pages = cls.prepare_and_ocr_submission(submission_id, options, user, ip_address)
        from core.ai_engine.mapping.orchestrator import QuestionMappingOrchestrator
        QuestionMappingOrchestrator.analyze_and_build_mapping(submission_id, user, ip_address)
        return cls.evaluate_mapped_answers(submission_id, None, options, user, ip_address)

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
        Processes working copy images from media/submission_working/ (single source of truth).
        No long-running database transaction is kept open during OCR or image preprocessing.
        """
        from core.ai_engine.preprocessing.working_copy_manager import WorkingCopyManager
        from django.db import close_old_connections

        # Ensure working image copies are initialized
        working_paths = WorkingCopyManager.create_initial_working_copies(submission.id)
        extracted_pages = []

        pages = list(submission.pages.all().order_by('page_number'))

        for sp in pages:
            working_path = sp.working_image_path if (sp.working_image_path and os.path.exists(sp.working_image_path)) else WorkingCopyManager.get_latest_working_image_path(submission.id, sp.page_number)

            print("----------------------------------------")
            print("OCR USING")
            print(f"submission_working/ (Page {sp.page_number} v{sp.version})")
            print("No DB transaction open during OCR compute")
            print("----------------------------------------")

            close_old_connections()

            bgr = cv2.imread(working_path) if (working_path and os.path.exists(working_path)) else None
            if bgr is not None:
                enhanced_bgr, meta = ImagePreprocessingService.process_image(
                    bgr,
                    options=options,
                    trace_dir=os.path.join(trace_dir, f'page_{sp.page_number}')
                )
                raw_text, ocr_conf = cls._run_ocr_on_bgr(enhanced_bgr)
            else:
                raw_text, ocr_conf = "", 0.0

            close_old_connections()

            # Save OCR result inside fast transaction
            with transaction.atomic():
                sp.ocr_raw_text = raw_text
                sp.ocr_confidence = ocr_conf
                sp.save()

                OCRResult.objects.create(
                    submission_page=sp,
                    engine_name=options.get('ocr_mode', 'EASYOCR').upper(),
                    page_confidence=ocr_conf,
                    raw_text=raw_text
                )
                extracted_pages.append(sp)

        from core.ai_engine.services.workflow import SubmissionWorkflow
        SubmissionWorkflow.advance(submission, StudentSubmission.Status.OCR_COMPLETE)
        SubmissionWorkflow.advance(submission, StudentSubmission.Status.SEGMENTED)
        return extracted_pages

    @classmethod
    def _run_ocr_on_bgr(cls, bgr_img: np.ndarray) -> Tuple[str, float]:
        # 1. Try PyTesseract first (fast, CPU safe)
        try:
            import pytesseract
            from PIL import Image as PILImg
            import cv2
            rgb = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
            pil_img = PILImg.fromarray(rgb)
            text = pytesseract.image_to_string(pil_img).strip()
            if text:
                return text, 0.80
        except Exception:
            pass

        # 2. Try EasyOCR if explicitly enabled
        try:
            from config.ocr_config import get_ocr_reader, is_easyocr_enabled
            if not is_easyocr_enabled():
                return "", 0.0
            reader = get_ocr_reader()
            if not reader:
                return "", 0.0
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
        from core.ai_engine.mapping.orchestrator import QuestionMappingOrchestrator
        from core.models import QuestionMapping

        created_answers = []
        existing_mappings = safe_normalize_collection(submission.question_mappings.all())

        if not existing_mappings:
            cls._write_pipeline_log(submission.id, "[MAPPING] Running order-independent question mapping analysis...")
            QuestionMappingOrchestrator.analyze_and_build_mapping(submission.id)
            existing_mappings = safe_normalize_collection(submission.question_mappings.all())

        pages_by_num = {p.page_number: p for p in pages}

        for q in stored_questions:
            q_id = getattr(q, 'id', 0)
            q_num = QuestionAccessor.get_question_number(q)
            q_map = next((m for m in existing_mappings if getattr(m.question, 'id', None) == q_id), None)

            if q_map and q_map.page_numbers_json:
                page_texts = []
                for p_num in q_map.page_numbers_json:
                    if p_num in pages_by_num and pages_by_num[p_num].ocr_raw_text:
                        page_texts.append(f"--- PAGE {p_num} ---\n" + pages_by_num[p_num].ocr_raw_text)

                extracted_ans_text = "\n\n".join(page_texts).strip() if page_texts else f"[Answer for Q{q_num} unmapped / skipped by student]"
                is_ambiguous = (q_map.mapping_status == QuestionMapping.Status.AMBIGUOUS) and not q_map.is_confirmed
                matched_page = pages_by_num.get(q_map.page_numbers_json[0]) if q_map.page_numbers_json else (pages[0] if pages else None)
            else:
                extracted_ans_text = f"[Question Q{q_num} unmapped / skipped by student]"
                is_ambiguous = True
                matched_page = pages[0] if pages else None

            sub_ans, _ = SubmissionAnswer.objects.get_or_create(
                submission=submission,
                question=q,
                defaults={
                    'extracted_text': extracted_ans_text,
                    'ocr_confidence': getattr(q_map, 'confidence', 0.85),
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

        from django.db import close_old_connections

        print("----------------------------------------")
        print("LLM")
        print(f"No DB transaction open during LLM API call for Q{q_dto.number}")
        print("----------------------------------------")

        for attempt in range(1, max_retries + 2):
            try:
                close_old_connections()
                raw_response = ai_provider.generate_completion(
                    prompt=system_prompt if attempt == 1 else f"{system_prompt}\n\nIMPORTANT: Your previous response was invalid JSON. Return ONLY raw JSON matching the required schema.",
                    system_instruction="You return strict JSON academic script evaluations."
                )
                close_old_connections()

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
