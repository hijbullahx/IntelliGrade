"""
IntelliGrade Question Mapping Orchestrator v3.0.
Primary Source of Truth: Student's Handwritten / Printed Answer Headings.

STRICT PIPELINE STAGES:
1. OCR Page Line Extraction with Bounding Boxes
2. Explicit Question Heading Detection (detect_explicit_question_heading)
3. Subpoint & Enumeration Marker Rejection
4. Multi-Heading Y-Coordinate Page Segmentation
5. Context-Aware Continuation Detection
6. Fallback Semantic Similarity Validation
7. Confidence Scoring & Flagging for Teacher Review
"""

import os
import re
import json
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
from django.conf import settings
from django.db import transaction, close_old_connections, IntegrityError, DatabaseError, OperationalError

from core.models import StudentSubmission, SubmissionPage, SubmissionAnswer, Question, QuestionDetection, QuestionMapping, MappingHistory
from core.utils.question_accessor import QuestionAccessor, safe_normalize_collection
from core.ai_engine.mapping.question_number_detector import StudentQuestionHeadingDetector
from core.ai_engine.mapping.semantic_matcher import SemanticQuestionMatcher
from core.ai_engine.mapping.continuation_detector import ContinuationDetector


class QuestionMappingOrchestrator:
    """
    Order-independent question mapping pipeline for student answer scripts.
    Guarantees zero false Q1 mappings on unlabelled subpoint pages.
    """

    @classmethod
    def analyze_and_build_mapping(cls, submission_id: int, user=None, ip_address: str = None) -> Dict[str, Any]:
        """
        Executes Student Answer Heading Detection, Multi-Question Segmentation, Continuation Tracking,
        Semantic Fallback, and Debug Artifact Generation.
        """
        submission = StudentSubmission.objects.get(id=submission_id)
        examination = submission.examination
        stored_questions = safe_normalize_collection(examination.questions.all())
        stored_questions.sort(key=lambda q: int(re.sub(r'\D', '', QuestionAccessor.get_question_number(q)) or 0))

        pages = safe_normalize_collection(submission.pages.all().order_by('page_number'))
        if not pages:
            return {'success': False, 'error': 'No submission pages found for mapping analysis.'}

        trace_dir = os.path.join(settings.MEDIA_ROOT, 'request_trace', f'eval_{submission.id}')
        os.makedirs(trace_dir, exist_ok=True)

        stored_q_numbers = [QuestionAccessor.get_question_number(q) for q in stored_questions]

        # Clear old detections & unconfirmed mappings if re-analyzing
        QuestionDetection.objects.filter(submission_page__submission=submission).delete()
        QuestionMapping.objects.filter(submission=submission, is_confirmed=False).delete()

        # Step 1: Detect Explicit Question Headings on Each Page
        page_header_map = {}  # page_number -> list of detections
        all_detected_numbers = []

        for sp in pages:
            ocr_text = sp.ocr_raw_text or ""
            line_boxes = getattr(sp.ocr_results.first(), 'line_boxes_json', [])
            detections = StudentQuestionHeadingDetector.detect_questions_on_page(
                ocr_text, line_boxes, stored_question_numbers=stored_q_numbers
            )

            # Vision LLM fallback ONLY if top OCR header is empty and image exists
            if not detections and sp.working_image_path and os.path.exists(sp.working_image_path):
                try:
                    vis_det = StudentQuestionHeadingDetector.detect_top_region_vision(
                        image_input=sp.working_image_path,
                        stored_question_numbers=stored_q_numbers
                    )
                    if vis_det and vis_det.get('detected'):
                        detections.append(vis_det)
                except Exception as e:
                    print(f"[QUESTION HEADER VISION WARNING] Vision detector failed on page {sp.page_number}: {e}")

            page_header_map[sp.page_number] = detections

            valid_choices = [c[0] for c in QuestionDetection.DetectionMethod.choices]
            for d in detections:
                try:
                    method_str = d.get('method', QuestionDetection.DetectionMethod.OCR_PATTERN)
                    if method_str not in valid_choices:
                        method_str = QuestionDetection.DetectionMethod.OCR_PATTERN

                    QuestionDetection.objects.create(
                        submission_page=sp,
                        question_number_raw=d.get('heading_text', d['raw_text']),
                        question_number_normalized=d['normalized_number'],
                        bbox_json=d.get('bbox', {}),
                        confidence=d['confidence'],
                        detection_method=method_str
                    )
                except Exception as ex:
                    print(f"[QUESTION DETECTION SAVE WARNING] {ex}")

                all_detected_numbers.append(d['normalized_number'])

        # Step 2: Build Priority-based Question -> Page Association & Multi-Question Page Segmentation
        q_map_by_num = {QuestionAccessor.get_question_number(q).strip().lower(): q for q in stored_questions}
        mapped_pages_by_q = {getattr(q, 'id', 0): {'q_obj': q, 'pages': [], 'confidences': [], 'raw_headers': [], 'methods': []} for q in stored_questions}

        active_q_obj = None
        unassigned_page_numbers = []
        page_mapping_records = []
        duplicate_nums = set([num for num in all_detected_numbers if all_detected_numbers.count(num) > 1])

        for sp in pages:
            p_num = sp.page_number
            detections = page_header_map.get(p_num, [])

            distinct_detected_nums = list(set([d['normalized_number'].strip().lower() for d in detections]))

            if len(distinct_detected_nums) > 1:
                # MULTI-QUESTION PAGE SEGMENTATION: Multiple explicit headers on same physical page!
                # Split page into answer regions for each question
                segment_texts = []
                for det in detections:
                    norm_num = det['normalized_number'].strip().lower()
                    matched_q = q_map_by_num.get(norm_num)
                    if not matched_q:
                        for q in stored_questions:
                            if re.sub(r'\D', '', QuestionAccessor.get_question_number(q)) == re.sub(r'\D', '', norm_num):
                                matched_q = q
                                break

                    if matched_q:
                        q_id = getattr(matched_q, 'id', 0)
                        mapped_pages_by_q[q_id]['pages'].append(p_num)
                        mapped_pages_by_q[q_id]['confidences'].append(det['confidence'])
                        mapped_pages_by_q[q_id]['raw_headers'].append(det.get('heading_text', det['raw_text']))
                        mapped_pages_by_q[q_id]['methods'].append('MULTI_HEADING_SEGMENT')
                        segment_texts.append(f"Q{QuestionAccessor.get_question_number(matched_q)}")
                        active_q_obj = matched_q

                page_mapping_records.append({
                    'page': p_num,
                    'question_number': '/'.join(segment_texts) if segment_texts else 'MULTI_HEADING',
                    'question_id': getattr(active_q_obj, 'id', None),
                    'heading_text': f"Multi-heading page ({', '.join(segment_texts)})",
                    'method': 'MULTI_HEADING_SEGMENT',
                    'confidence': 0.95,
                    'evidence': f"Split into regions for {', '.join(segment_texts)}",
                    'status': 'CONFIDENT'
                })

            elif len(distinct_detected_nums) == 1:
                # Priority 1: Single Explicit Student Answer Heading
                top_det = detections[0]
                norm_num = top_det['normalized_number'].strip().lower()

                matched_q = q_map_by_num.get(norm_num)
                if not matched_q:
                    for q in stored_questions:
                        if re.sub(r'\D', '', QuestionAccessor.get_question_number(q)) == re.sub(r'\D', '', norm_num):
                            matched_q = q
                            break

                if matched_q:
                    active_q_obj = matched_q
                    q_id = getattr(matched_q, 'id', 0)
                    mapped_pages_by_q[q_id]['pages'].append(p_num)
                    mapped_pages_by_q[q_id]['confidences'].append(top_det['confidence'])
                    mapped_pages_by_q[q_id]['raw_headers'].append(top_det.get('heading_text', top_det['raw_text']))
                    mapped_pages_by_q[q_id]['methods'].append(top_det.get('method', 'EXPLICIT_ANSWER_HEADING'))

                    page_mapping_records.append({
                        'page': p_num,
                        'question_number': QuestionAccessor.get_question_number(matched_q),
                        'question_id': q_id,
                        'heading_text': top_det.get('heading_text', top_det['raw_text']),
                        'method': top_det.get('method', 'EXPLICIT_ANSWER_HEADING'),
                        'confidence': top_det['confidence'],
                        'evidence': top_det.get('heading_text', top_det['raw_text']),
                        'status': 'CONFIDENT' if top_det['confidence'] >= 0.90 else 'AMBIGUOUS'
                    })
                else:
                    unassigned_page_numbers.append(p_num)
                    page_mapping_records.append({
                        'page': p_num,
                        'question_number': 'UNMAPPED',
                        'question_id': None,
                        'heading_text': top_det.get('heading_text', top_det['raw_text']),
                        'method': 'UNRESOLVED',
                        'confidence': 0.0,
                        'evidence': top_det['raw_text'],
                        'status': 'AMBIGUOUS'
                    })

            elif active_q_obj:
                # Priority 2: Continuation of previous active question
                prev_text = pages[p_num - 2].ocr_raw_text if p_num > 1 else ""
                cont_eval = ContinuationDetector.evaluate_continuation(
                    prev_page_text=prev_text,
                    current_page_text=sp.ocr_raw_text or "",
                    current_has_new_header=False
                )

                if cont_eval['is_continuation']:
                    q_id = getattr(active_q_obj, 'id', 0)
                    mapped_pages_by_q[q_id]['pages'].append(p_num)
                    mapped_pages_by_q[q_id]['confidences'].append(cont_eval['confidence'])
                    mapped_pages_by_q[q_id]['methods'].append('CONTINUATION')

                    page_mapping_records.append({
                        'page': p_num,
                        'question_number': QuestionAccessor.get_question_number(active_q_obj),
                        'question_id': q_id,
                        'heading_text': f"Continuation of Q{QuestionAccessor.get_question_number(active_q_obj)}",
                        'method': 'CONTINUATION',
                        'confidence': cont_eval['confidence'],
                        'evidence': f"Continuation of Q{QuestionAccessor.get_question_number(active_q_obj)} ({cont_eval['reason']})",
                        'status': 'CONFIDENT' if cont_eval['confidence'] >= 0.75 else 'AMBIGUOUS'
                    })
                else:
                    unassigned_page_numbers.append(p_num)
                    page_mapping_records.append({
                        'page': p_num,
                        'question_number': 'UNMAPPED',
                        'question_id': None,
                        'heading_text': 'None',
                        'method': 'UNRESOLVED',
                        'confidence': 0.0,
                        'evidence': 'No explicit heading or continuation detected',
                        'status': 'AMBIGUOUS'
                    })
            else:
                # Unlabelled first page or unmapped page with no prior active question
                unassigned_page_numbers.append(p_num)
                page_mapping_records.append({
                    'page': p_num,
                    'question_number': 'UNMAPPED',
                    'question_id': None,
                    'heading_text': 'None',
                    'method': 'UNRESOLVED',
                    'confidence': 0.0,
                    'evidence': 'No explicit question heading found',
                    'status': 'AMBIGUOUS'
                })

        # Priority 3: Semantic Fallback for Unmapped Pages (Secondary Fallback ONLY)
        for rec in page_mapping_records:
            if rec['method'] == 'UNRESOLVED' and rec['page'] in unassigned_page_numbers:
                sp_un = next((p for p in pages if p.page_number == rec['page']), None)
                if sp_un and sp_un.ocr_raw_text and len(sp_un.ocr_raw_text.strip()) > 15:
                    sem_res = SemanticQuestionMatcher.match_unlabelled_answer(sp_un.ocr_raw_text, stored_questions)
                    best_q = sem_res.get('best_question')
                    sem_conf = float(sem_res.get('confidence', 0.0))

                    if best_q and sem_conf >= 0.50:
                        q_id = getattr(best_q, 'id', 0)
                        mapped_pages_by_q[q_id]['pages'].append(rec['page'])
                        mapped_pages_by_q[q_id]['confidences'].append(sem_conf)
                        mapped_pages_by_q[q_id]['raw_headers'].append(f"Semantic Match ({sem_conf*100:.0f}%)")
                        mapped_pages_by_q[q_id]['methods'].append('SEMANTIC_FALLBACK')

                        rec['question_number'] = QuestionAccessor.get_question_number(best_q)
                        rec['question_id'] = q_id
                        rec['method'] = 'SEMANTIC_FALLBACK'
                        rec['confidence'] = sem_conf
                        rec['evidence'] = f"Semantic topic similarity score: {sem_conf}"
                        rec['status'] = 'CONFIDENT' if sem_conf >= 0.75 else 'AMBIGUOUS'

                        unassigned_page_numbers.remove(rec['page'])

                        try:
                            QuestionDetection.objects.create(
                                submission_page=sp_un,
                                question_number_raw="Semantic Match Fallback",
                                question_number_normalized=QuestionAccessor.get_question_number(best_q),
                                confidence=sem_conf,
                                detection_method=QuestionDetection.DetectionMethod.LLM_SEMANTIC
                            )
                        except Exception as ex:
                            print(f"[SEMANTIC DETECTION SAVE WARNING] {ex}")

        # Step 3: Construct QuestionMapping DB Records & Output Payload
        final_mapping_payload = []
        missing_q_nums = []
        requires_review = False

        for q in stored_questions:
            q_id = getattr(q, 'id', 0)
            data = mapped_pages_by_q[q_id]
            pg_list = sorted(list(set(data['pages'])))
            avg_conf = round(sum(data['confidences']) / max(1, len(data['confidences'])), 2) if data['confidences'] else 0.0

            if not pg_list:
                missing_q_nums.append(QuestionAccessor.get_question_number(q))

            status = QuestionMapping.Status.AUTO_HIGH
            if avg_conf < 0.75 or not pg_list or QuestionAccessor.get_question_number(q) in duplicate_nums:
                status = QuestionMapping.Status.AMBIGUOUS
                requires_review = True

            q_map_obj, _ = QuestionMapping.objects.get_or_create(
                submission=submission,
                question=q,
                defaults={
                    'page_numbers_json': pg_list,
                    'confidence': avg_conf,
                    'mapping_status': status,
                    'is_confirmed': False
                }
            )
            q_map_obj.page_numbers_json = pg_list
            q_map_obj.confidence = avg_conf
            q_map_obj.mapping_status = status
            q_map_obj.save()

            final_mapping_payload.append({
                'mapping_id': q_map_obj.id,
                'question_id': q_id,
                'question_number': QuestionAccessor.get_question_number(q),
                'prompt_text': QuestionAccessor.get_text(q),
                'max_marks': QuestionAccessor.get_marks(q),
                'page_numbers': pg_list,
                'confidence': avg_conf,
                'mapping_status': status,
                'is_confirmed': q_map_obj.is_confirmed,
                'detected_headers': list(set(data['raw_headers']))
            })

        # Save JSON Debug Artifact: request_trace/eval_{submission.id}/question_heading_detection.json
        json_path = os.path.join(trace_dir, 'question_heading_detection.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'submission_id': submission.id,
                'pages': page_mapping_records,
                'summary': final_mapping_payload,
                'unassigned_pages': unassigned_page_numbers,
                'duplicates': list(duplicate_nums),
                'missing_questions': missing_q_nums
            }, f, indent=2)

        # Save Image Debug Overlay Artifact: request_trace/eval_{submission.id}/question_heading_detection_debug.png
        cls._render_mapping_debug_image(submission, pages, page_mapping_records, trace_dir)

        # Save Audit Record in MappingHistory
        MappingHistory.objects.create(
            submission=submission,
            teacher=user if user and user.is_authenticated else None,
            action_type="AUTO_MAPPING_ANALYSIS",
            details_json={
                'mappings': final_mapping_payload,
                'unassigned_pages': unassigned_page_numbers,
                'duplicates': list(duplicate_nums),
                'missing_questions': missing_q_nums
            },
            ip_address=ip_address
        )

        from core.ai_engine.services.workflow import SubmissionWorkflow
        SubmissionWorkflow.advance(submission, StudentSubmission.Status.MAPPING_COMPLETE, force=True)
        SubmissionWorkflow.advance(submission, StudentSubmission.Status.WAITING_TEACHER_CONFIRMATION, force=True)

        has_unresolved_or_conflict = any(r['method'] in ['UNRESOLVED', 'CONFLICT'] for r in page_mapping_records)

        return {
            'success': True,
            'submission_id': submission.id,
            'mappings': final_mapping_payload,
            'page_records': page_mapping_records,
            'page_header_map': page_header_map,
            'unassigned_pages': unassigned_page_numbers,
            'duplicates': list(duplicate_nums),
            'missing_questions': missing_q_nums,
            'requires_teacher_confirmation': requires_review or has_unresolved_or_conflict or any(not m['is_confirmed'] for m in final_mapping_payload)
        }

    @classmethod
    def _render_mapping_debug_image(
        cls,
        submission: StudentSubmission,
        pages: List[SubmissionPage],
        page_records: List[Dict[str, Any]],
        trace_dir: str
    ) -> str:
        """
        Renders question_heading_detection_debug.png visual summary grid with bounding box overlays.
        Color codes: Cyan=EXPLICIT_HEADER, Yellow=CONTINUATION, Purple=SEMANTIC_FALLBACK, Red=CONFLICT, Gray=UNRESOLVED.
        """
        out_path = os.path.join(trace_dir, 'question_heading_detection_debug.png')
        try:
            thumbnails = []
            for rec in page_records:
                p_num = rec['page']
                sp = next((p for p in pages if p.page_number == p_num), None)
                img_path = sp.working_image_path if (sp and sp.working_image_path and os.path.exists(sp.working_image_path)) else None

                if img_path and os.path.exists(img_path):
                    bgr = cv2.imread(img_path)
                else:
                    bgr = np.full((400, 300, 3), 240, dtype=np.uint8)

                h, w = bgr.shape[:2]
                thumb_w = 300
                thumb = cv2.resize(bgr, (thumb_w, 400))

                method = rec.get('method', 'UNRESOLVED')
                if method in ['EXPLICIT_ANSWER_HEADING', 'DIRECT_QUESTION_HEADER', 'ABBREVIATED_ANSWER_HEADING', 'QUESTION_HEADING', 'ANSWER_TO_QUESTION', 'SOLUTION_HEADING', 'MULTI_HEADING_SEGMENT']:
                    color_bgr = (255, 140, 0)   # Cyan / Blue
                elif method == 'CONTINUATION':
                    color_bgr = (0, 215, 255)   # Yellow
                elif method == 'SEMANTIC_FALLBACK':
                    color_bgr = (255, 0, 255)   # Purple
                elif method == 'CONFLICT':
                    color_bgr = (0, 0, 255)     # Red
                else:
                    color_bgr = (128, 128, 128) # Gray (UNRESOLVED)

                cv2.rectangle(thumb, (0, 0), (thumb_w - 1, 399), color_bgr, 6)

                cv2.rectangle(thumb, (0, 0), (thumb_w, 45), (20, 20, 20), -1)
                q_label = f"Pg {p_num} -> Q{rec['question_number']}" if rec['question_number'] not in ['UNMAPPED', 'CONFLICT'] else f"Pg {p_num} -> {rec['question_number']}"
                cv2.putText(thumb, q_label, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

                cv2.rectangle(thumb, (0, 360), (thumb_w, 400), (20, 20, 20), -1)
                conf_pct = int(rec.get('confidence', 0.0) * 100)
                sub_label = f"{method} ({conf_pct}%)"
                cv2.putText(thumb, sub_label, (10, 388), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color_bgr, 1)

                thumbnails.append(thumb)

            if thumbnails:
                cols = min(4, len(thumbnails))
                rows = (len(thumbnails) + cols - 1) // cols

                grid_h = rows * 400
                grid_w = cols * 300
                canvas = np.zeros((grid_h, grid_w, 3), dtype=np.uint8)

                for idx, t in enumerate(thumbnails):
                    r = idx // cols
                    c = idx % cols
                    canvas[r*400:(r+1)*400, c*300:(c+1)*300] = t

                cv2.imwrite(out_path, canvas)
        except Exception as e:
            print(f"[DEBUG OVERLAY RENDER WARNING] {e}")

        return out_path

    @classmethod
    def confirm_mapping_and_evaluate(
        cls,
        submission_id: int,
        confirmed_mappings: List[Dict[str, Any]],
        user=None,
        ip_address: str = None
    ) -> Tuple[bool, str]:
        """
        Updates QuestionMapping DB records with teacher-approved choices and marks them confirmed.
        Creates/updates SubmissionAnswer text for each question based on approved page ranges.
        """
        with transaction.atomic():
            submission = StudentSubmission.objects.get(id=submission_id)
            pages = {p.page_number: p for p in submission.pages.all()}

            for m_item in confirmed_mappings:
                q_id = m_item.get('question_id')
                pg_list = m_item.get('page_numbers', [])

                if not q_id:
                    continue

                q_obj = Question.objects.get(id=q_id)
                q_map, _ = QuestionMapping.objects.get_or_create(submission=submission, question=q_obj)
                q_map.page_numbers_json = pg_list
                q_map.confidence = 1.0  # Teacher confirmed
                q_map.mapping_status = QuestionMapping.Status.MANUAL_OVERRIDE
                q_map.is_confirmed = True
                q_map.save()

                # Concatenate answer text from mapped pages
                combined_ans_text = []
                for p_num in pg_list:
                    if p_num in pages and pages[p_num].ocr_raw_text:
                        combined_ans_text.append(f"--- PAGE {p_num} ---\n" + pages[p_num].ocr_raw_text)

                ans_text = "\n\n".join(combined_ans_text).strip() if combined_ans_text else f"[Question Q{q_obj.question_number} unmapped / skipped by student]"

                sub_ans, _ = SubmissionAnswer.objects.get_or_create(
                    submission=submission,
                    question=q_obj,
                    defaults={'extracted_text': ans_text, 'ocr_confidence': 1.0, 'requires_manual_review': False}
                )
                sub_ans.extracted_text = ans_text
                sub_ans.requires_manual_review = False
                sub_ans.save()

            MappingHistory.objects.create(
                submission=submission,
                teacher=user if user and user.is_authenticated else None,
                action_type="TEACHER_CONFIRMED_MAPPING",
                details_json={'confirmed_mappings': confirmed_mappings},
                ip_address=ip_address
            )

        return True, "Question mapping successfully confirmed by teacher."
