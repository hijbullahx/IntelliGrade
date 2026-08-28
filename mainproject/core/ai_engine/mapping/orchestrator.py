"""
IntelliGrade Region-Based Question Mapping & Answer Segmentation Engine v4.0.

ARCHITECTURE:
DOCUMENT -> PAGE -> ANSWER REGIONS -> QUESTION HEADING -> QUESTION OWNERSHIP -> CONTINUATION

STATE MACHINE:
NO_ACTIVE_QUESTION -> VALID_ANSWER_HEADING -> QUESTION_ACTIVE -> CONTINUATION -> NEW_ANSWER_HEADING / AMBIGUOUS_PAGE / TEACHER_REVIEW
"""

import os
import re
import json
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from django.conf import settings
from django.db import transaction, close_old_connections, IntegrityError, DatabaseError, OperationalError

from core.models import StudentSubmission, SubmissionPage, SubmissionAnswer, Question, QuestionDetection, QuestionMapping, MappingHistory
from core.utils.question_accessor import QuestionAccessor, safe_normalize_collection, normalize_q_code
from core.ai_engine.mapping.question_number_detector import StudentQuestionHeadingDetector, LineReconstructor
from core.ai_engine.mapping.semantic_matcher import SemanticQuestionMatcher
from core.ai_engine.mapping.continuation_detector import ContinuationDetector


def normalize_question_code(q: Any) -> str:
    """Canonical question code normalizer: prevents 'QQ' duplication."""
    return normalize_q_code(q)


class AnswerRegion:
    """
    Represents an atomic answer region within a physical SubmissionPage.
    A page can contain 1 or more AnswerRegions.
    """

    def __init__(
        self,
        page_number: int,
        region_id: str,
        bbox: Dict[str, float],
        question_id: Optional[int],
        question_number: str,
        heading_text: str = "",
        heading_bbox: Optional[Dict[str, float]] = None,
        heading_confidence: float = 0.0,
        semantic_confidence: float = 0.0,
        mapping_method: str = "UNRESOLVED",
        confidence_level: str = "UNKNOWN",
        requires_review: bool = False,
        conflict: bool = False,
        possible_missed_heading: bool = False,
        reason: str = ""
    ):
        self.page_number = page_number
        self.region_id = region_id
        self.bbox = bbox  # {'ymin': 0.0, 'xmin': 0.0, 'ymax': 1.0, 'xmax': 1.0}
        self.question_id = question_id
        self.question_number = question_number
        self.heading_text = heading_text
        self.heading_bbox = heading_bbox or {}
        self.heading_confidence = heading_confidence
        self.semantic_confidence = semantic_confidence
        self.mapping_method = mapping_method
        self.confidence_level = confidence_level  # HIGH, MEDIUM, LOW, UNKNOWN
        self.requires_review = requires_review
        self.conflict = conflict
        self.possible_missed_heading = possible_missed_heading
        self.reason = reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            'page_number': self.page_number,
            'region_id': self.region_id,
            'bbox': self.bbox,
            'question_id': self.question_id,
            'question_number': self.question_number,
            'heading_text': self.heading_text,
            'heading_bbox': self.heading_bbox,
            'heading_confidence': self.heading_confidence,
            'semantic_confidence': self.semantic_confidence,
            'mapping_method': self.mapping_method,
            'confidence_level': self.confidence_level,
            'requires_review': self.requires_review,
            'conflict': self.conflict,
            'possible_missed_heading': self.possible_missed_heading,
            'reason': self.reason
        }


class QuestionMappingOrchestrator:
    """
    Region-Based Question Mapping & Answer Segmentation Pipeline for Student Answer Scripts.
    Supports multiple answer regions per page, missed-heading detection, semantic transition detection,
    and visual debug artifact generation.
    """

    @classmethod
    def analyze_and_build_mapping(cls, submission_id: int, user=None, ip_address: str = None) -> Dict[str, Any]:
        """
        Executes Region-Based Answer Segmentation, Line Reconstruction, Multi-Heading Scoring,
        Continuation Analysis, Semantic Transition Detection, and Debug Image Generation.
        """
        if isinstance(submission_id, StudentSubmission):
            submission = submission_id
        else:
            submission = StudentSubmission.objects.get(id=int(submission_id))
        examination = submission.examination
        stored_questions = safe_normalize_collection(examination.questions.all())
        stored_questions.sort(key=lambda q: int(re.sub(r'\D', '', QuestionAccessor.get_question_number(q)) or 0))

        pages = safe_normalize_collection(submission.pages.all().order_by('page_number'))
        if not pages:
            return {'success': False, 'error': 'No submission pages found for mapping analysis.'}

        trace_dir = os.path.join(settings.MEDIA_ROOT, 'request_trace', f'eval_{submission.id}')
        os.makedirs(trace_dir, exist_ok=True)

        stored_q_numbers = [QuestionAccessor.get_question_number(q) for q in stored_questions]
        q_map_by_num = {QuestionAccessor.get_question_number(q).strip().lower(): q for q in stored_questions}

        # Clear old detections & unconfirmed mappings if re-analyzing
        QuestionDetection.objects.filter(submission_page__submission=submission).delete()
        QuestionMapping.objects.filter(submission=submission, is_confirmed=False).delete()

        page_regions_map = {}  # page_number -> list of AnswerRegion objects
        all_detected_numbers = []
        mapped_regions_by_q = {getattr(q, 'id', 0): {'q_obj': q, 'regions': []} for q in stored_questions}

        active_q_obj = None
        unassigned_page_numbers = []
        page_mapping_records = []

        print(f"\n==================================================")
        print(f"INTELLIGRADE REGION-BASED QUESTION MAPPING PIPELINE v4.0")
        print(f"Submission #{submission.id} ({len(pages)} pages)")
        print(f"==================================================\n")



        # PASS 1: Evidence Gathering (Global Ownership Evidence Matrix)
        evidence_matrix = {}

        for sp in pages:
            p_num = sp.page_number
            ocr_text = sp.ocr_raw_text or ""
            ocr_res = sp.ocr_results.first()
            
            word_boxes = []
            line_boxes = []
            if ocr_res:
                wb_json = getattr(ocr_res, 'word_boxes_json', None)
                lb_json = getattr(ocr_res, 'line_boxes_json', None)
                if wb_json and isinstance(wb_json, list):
                    word_boxes = wb_json
                if lb_json and isinstance(lb_json, list):
                    line_boxes = lb_json

            # Step 1: Detect explicit question headings using reconstructed visual lines
            detections = StudentQuestionHeadingDetector.detect_questions_on_page(
                ocr_raw_text=ocr_text,
                word_boxes=word_boxes,
                line_boxes=line_boxes,
                page_height=1000,
                stored_question_numbers=stored_q_numbers
            )

            # Vision LLM fallback ONLY if OCR text is completely empty and working image exists
            if not detections and (not ocr_text or len(ocr_text.strip()) == 0) and sp.working_image_path and os.path.exists(sp.working_image_path):
                try:
                    vis_det = StudentQuestionHeadingDetector.detect_top_region_vision(
                        image_input=sp.working_image_path,
                        stored_question_numbers=stored_q_numbers
                    )
                    if vis_det and vis_det.get('detected'):
                        detections.append(vis_det)
                except Exception as e:
                    print(f"[QUESTION HEADER VISION WARNING] Vision detector failed on page {p_num}: {e}")

            # Save QuestionDetection DB records
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

            # Calculate evidence scores for the Matrix
            explicit_heading_score = max([d.get('confidence', 0.0) for d in detections], default=0.0)

            cover_info = StudentQuestionHeadingDetector.detect_cover_page_or_metadata(
                ocr_text,
                line_boxes=line_boxes
            )
            is_cover_page = (p_num == 1 and (cover_info.get('is_pure_cover_page') or cover_info.get('has_metadata_header')) and not detections)

            sem_best_q = None
            semantic_match_score = 0.0
            # Only invoke SemanticQuestionMatcher on unlabelled pages with NO explicit headings detected
            if not detections and not is_cover_page and ocr_text and len(ocr_text.strip()) > 20:
                try:
                    sem_match = SemanticQuestionMatcher.match_unlabelled_answer(ocr_text, stored_questions)
                    sem_best_q = sem_match.get('best_question')
                    semantic_match_score = float(sem_match.get('confidence', 0.0))
                except Exception as ex_sem:
                    print(f"[SEMANTIC MATCHER WARNING] Page {p_num}: {ex_sem}")

            evidence_matrix[p_num] = {
                'page': sp,
                'ocr_text': ocr_text,
                'detections': detections,
                'explicit_heading_score': explicit_heading_score,
                'semantic_match_score': semantic_match_score,
                'sem_best_q': sem_best_q,
            }

        # PASS 2: Order-Independent Global Optimization & Answer Region Construction
        active_q_obj = None
        active_q_conf = 0.90   # Fix 3: track last-set heading confidence for ContinuationDetector
        prev_page_ocr = ""     # Fix 3: track previous page text for text-flow validation

        for sp in pages:
            p_num = sp.page_number
            ev = evidence_matrix[p_num]
            detections = ev['detections']
            explicit_heading_score = ev['explicit_heading_score']
            semantic_match_score = ev['semantic_match_score']
            sem_best_q = ev['sem_best_q']
            ocr_text = ev['ocr_text']

            page_regions = []

            # Check for cover page / metadata
            cover_info = StudentQuestionHeadingDetector.detect_cover_page_or_metadata(
                ocr_text,
                line_boxes=getattr(sp, 'line_boxes_json', None)
            )
            is_cover_page = (p_num == 1 and cover_info['has_metadata_header'] and not detections)

            if is_cover_page:
                # Page 1 is pure exam cover / student metadata page (Name, Roll, ID)
                # DO NOT force any dummy Q1 or question region on it
                reg = AnswerRegion(
                    page_number=1,
                    region_id="p1_cover",
                    bbox={'ymin': 0.0, 'xmin': 0.0, 'ymax': 1.0, 'xmax': 1.0},
                    question_id=None,
                    question_number="COVER_PAGE",
                    heading_text="Exam Cover / Metadata Page",
                    heading_confidence=0.99,
                    semantic_confidence=0.0,
                    mapping_method="COVER_PAGE",
                    confidence_level="HIGH",
                    requires_review=False,
                    reason="Exam cover page / student metadata (No question answered)"
                )
                page_regions.append(reg)
                # Note: Not added to mapped_regions_by_q so 0 exam questions are assigned to cover page

            elif detections and explicit_heading_score >= 0.75:
                # Fix 5: Gate was previously `or len(detections) > 0` which is tautologically True
                # and bypassed the >= 0.80 confidence threshold entirely. Now requires the top
                # detection confidence to actually meet the minimum bar before page-splitting.
                detections.sort(key=lambda d: d.get('ymin_pct', 0.0))
                first_det_ymin = float(detections[0].get('ymin_pct', 0.0))

                # Handle top metadata offset if page 1 has metadata at top and heading below
                if p_num == 1 and cover_info['has_metadata_header']:
                    top_offset = max(cover_info['metadata_bottom_ymin'], first_det_ymin)
                else:
                    top_offset = 0.0

                if first_det_ymin > 0.20 and active_q_obj and top_offset == 0.0:
                    # Substantial top region prior to explicit heading belongs to active_q_obj as continuation
                    top_bbox = {'ymin': 0.0, 'xmin': 0.0, 'ymax': round(first_det_ymin, 4), 'xmax': 1.0}
                    active_q_id = getattr(active_q_obj, 'id', None)
                    formatted_active_q = normalize_q_code(QuestionAccessor.get_formatted_number(active_q_obj))
                    top_reg = AnswerRegion(
                        page_number=p_num,
                        region_id=f"p{p_num}_r0",
                        bbox=top_bbox,
                        question_id=active_q_id,
                        question_number=normalize_q_code(QuestionAccessor.get_question_number(active_q_obj)),
                        heading_text=f"Continuation of {formatted_active_q}",
                        heading_confidence=0.85,
                        semantic_confidence=0.0,
                        mapping_method="CONTINUATION",
                        confidence_level="HIGH",
                        requires_review=False,
                        reason=f"Top region continuation of {formatted_active_q} prior to explicit heading"
                    )
                    page_regions.append(top_reg)
                    mapped_regions_by_q[active_q_id]['regions'].append(top_reg)

                for r_idx, det in enumerate(detections, 1):
                    norm_num = normalize_q_code(det['normalized_number'])
                    matched_q = q_map_by_num.get(norm_num.lower())
                    if not matched_q:
                        for q in stored_questions:
                            if re.sub(r'\D', '', QuestionAccessor.get_question_number(q)) == re.sub(r'\D', '', norm_num):
                                matched_q = q
                                break

                    # Compute vertical start
                    if r_idx == 1:
                        if p_num == 1 and top_offset > 0.0:
                            y_start = top_offset
                        elif first_det_ymin <= 0.25:
                            y_start = 0.0
                        else:
                            y_start = max(0.0, min(1.0, first_det_ymin))
                    else:
                        y_start = max(0.0, min(1.0, float(det.get('ymin_pct', 0.0))))

                    next_y = float(detections[r_idx]['ymin_pct']) if r_idx < len(detections) else 1.0
                    next_y = max(0.0, min(1.0, next_y))

                    # Ensure y_end is strictly greater than y_start to avoid zero-height regions
                    if next_y <= y_start + 0.02:
                        y_end = 1.0 if r_idx >= len(detections) else max(y_start + 0.08, next_y)
                        y_end = min(1.0, y_end)
                    else:
                        y_end = next_y

                    if y_end <= y_start:
                        y_end = min(1.0, y_start + 0.10) if y_start < 0.90 else 1.0
                        if y_end <= y_start:
                            y_start = max(0.0, y_end - 0.10)

                    region_bbox = {'ymin': round(y_start, 4), 'xmin': 0.0, 'ymax': round(y_end, 4), 'xmax': 1.0}
                    q_id = getattr(matched_q, 'id', None) if matched_q else None
                    q_num_str = normalize_q_code(QuestionAccessor.get_question_number(matched_q) if matched_q else norm_num)

                    reg = AnswerRegion(
                        page_number=p_num,
                        region_id=f"p{p_num}_r{r_idx}",
                        bbox=region_bbox,
                        question_id=q_id,
                        question_number=q_num_str,
                        heading_text=det.get('heading_text', det['raw_text']),
                        heading_bbox=det.get('bbox', {}),
                        heading_confidence=det['confidence'],
                        semantic_confidence=0.0,
                        mapping_method=det.get('method', 'EXPLICIT_ANSWER_HEADING'),
                        confidence_level='HIGH' if det['confidence'] >= 0.85 else 'MEDIUM',
                        requires_review=(det['confidence'] < 0.85 or not matched_q),
                        reason=f"Explicit Answer Heading: '{det.get('heading_text', det['raw_text'])}'"
                    )
                    page_regions.append(reg)
                    if matched_q:
                        mapped_regions_by_q[q_id]['regions'].append(reg)
                        # Switch active question to newly detected question (Order-Agnostic!)
                        active_q_obj = matched_q
                        active_q_conf = det['confidence']  # Fix 3: record confidence of new heading

            else:
                # 0 explicit headings detected on this page

                # Fix 4: Blank Page Guard — pages with no OCR text AND no detections are blank
                # or unscanned pages. They must NOT be silently chained to active_q_obj at HIGH
                # confidence. Tag as BLANK_PAGE and skip all state mutation (do not update
                # active_q_obj, do not add to mapped_regions_by_q).
                ocr_is_empty = not ocr_text or len(ocr_text.strip()) < 15
                if ocr_is_empty and not detections and not sem_best_q:
                    reg = AnswerRegion(
                        page_number=p_num,
                        region_id=f"p{p_num}_r1",
                        bbox={'ymin': 0.0, 'xmin': 0.0, 'ymax': 1.0, 'xmax': 1.0},
                        question_id=None,
                        question_number="BLANK_PAGE",
                        heading_text="Blank / Unscanned Page",
                        heading_confidence=0.0,
                        semantic_confidence=0.0,
                        mapping_method="BLANK_PAGE",
                        confidence_level="UNKNOWN",
                        requires_review=True,
                        reason="Empty OCR + no heading + no semantic signal — blank or unscanned page"
                    )
                    page_regions.append(reg)
                    unassigned_page_numbers.append(p_num)
                    # Skip all downstream state mutation for blank pages

                # Check for semantic question transition if topic has distinctly changed
                elif sem_best_q and (sem_best_q != active_q_obj) and (semantic_match_score >= 0.50 or (cover_info.get('has_metadata_header') and p_num > 1)):
                    # A clear semantic topic transition or practical answer script section
                    sem_q_id = getattr(sem_best_q, 'id', None)
                    q_num_str = normalize_q_code(QuestionAccessor.get_question_number(sem_best_q))
                    formatted_sem_q = normalize_q_code(QuestionAccessor.get_formatted_number(sem_best_q))
                    reg = AnswerRegion(
                        page_number=p_num,
                        region_id=f"p{p_num}_r1",
                        bbox={'ymin': 0.0, 'xmin': 0.0, 'ymax': 1.0, 'xmax': 1.0},
                        question_id=sem_q_id,
                        question_number=q_num_str,
                        heading_text=f"Semantic Match: {formatted_sem_q}",
                        heading_confidence=0.0,
                        semantic_confidence=semantic_match_score,
                        mapping_method="SEMANTIC_TOPIC_MATCH",
                        confidence_level="HIGH" if semantic_match_score >= 0.75 else "MEDIUM",
                        requires_review=(semantic_match_score < 0.75),
                        possible_missed_heading=True,
                        reason=f"Semantic topic match to {formatted_sem_q} ({semantic_match_score*100:.0f}%)"
                    )
                    page_regions.append(reg)
                    mapped_regions_by_q[sem_q_id]['regions'].append(reg)
                    active_q_obj = sem_best_q

                elif active_q_obj:
                    # Fix 3: Validate continuation via ContinuationDetector text-flow analysis.
                    # Previously this branch was a blind state-machine: any page without a heading
                    # was silently chained to active_q_obj at HIGH confidence with no validation.
                    # Now we call ContinuationDetector and only assign CONTINUATION if the text
                    # flow evidence supports it (confidence >= 0.70).
                    active_q_id = getattr(active_q_obj, 'id', None)
                    q_num_str = normalize_q_code(QuestionAccessor.get_question_number(active_q_obj))
                    formatted_active_q = normalize_q_code(QuestionAccessor.get_formatted_number(active_q_obj))

                    cont_result = ContinuationDetector.evaluate_continuation(
                        prev_page_text=prev_page_ocr,
                        current_page_text=ocr_text,
                        current_has_new_header=bool(detections),
                        prev_page_conf=active_q_conf
                    )

                    if cont_result['is_continuation'] and cont_result['confidence'] >= 0.70:
                        reg = AnswerRegion(
                            page_number=p_num,
                            region_id=f"p{p_num}_r1",
                            bbox={'ymin': 0.0, 'xmin': 0.0, 'ymax': 1.0, 'xmax': 1.0},
                            question_id=active_q_id,
                            question_number=q_num_str,
                            heading_text=f"Continuation of {formatted_active_q}",
                            heading_confidence=round(cont_result['confidence'], 2),
                            semantic_confidence=semantic_match_score if sem_best_q == active_q_obj else 0.0,
                            mapping_method="CONTINUATION",
                            confidence_level="HIGH" if cont_result['confidence'] >= 0.85 else "MEDIUM",
                            requires_review=False,
                            reason=f"Continuation of {formatted_active_q}: {cont_result['reason']}"
                        )
                        page_regions.append(reg)
                        mapped_regions_by_q[active_q_id]['regions'].append(reg)
                    else:
                        # Weak or absent text-flow evidence — flag for teacher review
                        reg = AnswerRegion(
                            page_number=p_num,
                            region_id=f"p{p_num}_r1",
                            bbox={'ymin': 0.0, 'xmin': 0.0, 'ymax': 1.0, 'xmax': 1.0},
                            question_id=active_q_id,
                            question_number=q_num_str,
                            heading_text=f"Possible continuation of {formatted_active_q} (unconfirmed)",
                            heading_confidence=round(cont_result['confidence'], 2),
                            semantic_confidence=0.0,
                            mapping_method="UNRESOLVED",
                            confidence_level="LOW",
                            requires_review=True,
                            reason=f"Continuation uncertain ({cont_result['reason']}) — teacher review needed"
                        )
                        page_regions.append(reg)
                        mapped_regions_by_q[active_q_id]['regions'].append(reg)

                elif sem_best_q and semantic_match_score >= 0.20:
                    # Initial match if no active question
                    sem_q_id = getattr(sem_best_q, 'id', None)
                    q_num_str = normalize_q_code(QuestionAccessor.get_question_number(sem_best_q))
                    formatted_sem_q = normalize_q_code(QuestionAccessor.get_formatted_number(sem_best_q))
                    reg = AnswerRegion(
                        page_number=p_num,
                        region_id=f"p{p_num}_r1",
                        bbox={'ymin': 0.0, 'xmin': 0.0, 'ymax': 1.0, 'xmax': 1.0},
                        question_id=sem_q_id,
                        question_number=q_num_str,
                        heading_text=f"Semantic Match: {formatted_sem_q}",
                        heading_confidence=0.0,
                        semantic_confidence=semantic_match_score,
                        mapping_method="SEMANTIC_TOPIC_MATCH",
                        confidence_level="HIGH" if semantic_match_score >= 0.75 else "MEDIUM",
                        requires_review=(semantic_match_score < 0.75),
                        possible_missed_heading=True,
                        reason=f"Semantic topic match to {formatted_sem_q} ({semantic_match_score*100:.0f}%)"
                    )
                    page_regions.append(reg)
                    mapped_regions_by_q[sem_q_id]['regions'].append(reg)
                    active_q_obj = sem_best_q

                elif stored_questions:
                    # Default first question if completely unlabelled and no prior active question
                    active_q_obj = stored_questions[0]
                    active_q_id = getattr(active_q_obj, 'id', None)
                    q_num_str = normalize_q_code(QuestionAccessor.get_question_number(active_q_obj))
                    formatted_active_q = normalize_q_code(QuestionAccessor.get_formatted_number(active_q_obj))
                    reg = AnswerRegion(
                        page_number=p_num,
                        region_id=f"p{p_num}_r1",
                        bbox={'ymin': 0.0, 'xmin': 0.0, 'ymax': 1.0, 'xmax': 1.0},
                        question_id=active_q_id,
                        question_number=q_num_str,
                        heading_text=f"Assigned {formatted_active_q}",
                        heading_confidence=0.70,
                        semantic_confidence=0.0,
                        mapping_method="DEFAULT_FALLBACK",
                        confidence_level="MEDIUM",
                        requires_review=True,
                        reason=f"Default assignment to {formatted_active_q}"
                    )
                    page_regions.append(reg)
                    mapped_regions_by_q[active_q_id]['regions'].append(reg)

                else:
                    reg = AnswerRegion(
                        page_number=p_num,
                        region_id=f"p{p_num}_r1",
                        bbox={'ymin': 0.0, 'xmin': 0.0, 'ymax': 1.0, 'xmax': 1.0},
                        question_id=None,
                        question_number="UNMAPPED",
                        heading_text="None",
                        heading_confidence=0.0,
                        semantic_confidence=0.0,
                        mapping_method="UNRESOLVED",
                        confidence_level="UNKNOWN",
                        requires_review=True,
                        reason="No active question, explicit heading, or semantic match"
                    )
                    page_regions.append(reg)
                    unassigned_page_numbers.append(p_num)

            # Store answer_regions_json on SubmissionPage
            regions_dict_list = [r.to_dict() for r in page_regions]
            SubmissionPage.objects.filter(id=sp.id).update(answer_regions_json=regions_dict_list)
            sp.answer_regions_json = regions_dict_list
            page_regions_map[p_num] = page_regions
            prev_page_ocr = ocr_text  # Fix 3: advance sliding window for ContinuationDetector

            # Create summary mapping record for page
            q_nums_on_page = [normalize_q_code(r.question_number) if r.question_number not in ['COVER_PAGE', 'UNMAPPED'] else r.question_number for r in page_regions]
            q_ids_on_page = [r.question_id for r in page_regions if r.question_id]
            primary_reg = page_regions[0]

            page_mapping_records.append({
                'page': p_num,
                'question_number': '/'.join(q_nums_on_page),
                'question_id': q_ids_on_page[0] if q_ids_on_page else None,
                'heading_text': primary_reg.heading_text,
                'method': primary_reg.mapping_method,
                'confidence': primary_reg.heading_confidence,
                'confidence_level': primary_reg.confidence_level,
                'requires_review': any(r.requires_review for r in page_regions),
                'regions': [r.to_dict() for r in page_regions],
                'evidence': primary_reg.reason,
                'status': 'CONFIDENT' if not any(r.requires_review for r in page_regions) else 'AMBIGUOUS'
            })

        # Step 3: Construct QuestionMapping DB Records & Payload
        final_mapping_payload = []
        missing_q_nums = []
        duplicate_nums = set([num for num in all_detected_numbers if all_detected_numbers.count(num) > 1])
        requires_review = False

        for q in stored_questions:
            q_id = getattr(q, 'id', 0)
            reg_list = mapped_regions_by_q[q_id]['regions']
            pg_list = sorted(list(set([r.page_number for r in reg_list])))
            reg_dicts = [r.to_dict() for r in reg_list]

            confidences = [r.heading_confidence for r in reg_list if r.heading_confidence > 0]
            avg_conf = round(sum(confidences) / max(1, len(confidences)), 2) if confidences else 0.0

            if not pg_list:
                missing_q_nums.append(QuestionAccessor.get_question_number(q))

            status = QuestionMapping.Status.AUTO_HIGH if (avg_conf >= 0.75 and pg_list and not any(r.requires_review for r in reg_list) and QuestionAccessor.get_question_number(q) not in duplicate_nums) else QuestionMapping.Status.AMBIGUOUS
            if status == QuestionMapping.Status.AMBIGUOUS:
                requires_review = True

            q_map_obj, _ = QuestionMapping.objects.get_or_create(
                submission=submission,
                question=q,
                defaults={
                    'page_numbers_json': pg_list,
                    'regions_json': reg_dicts,
                    'confidence': avg_conf,
                    'mapping_status': status,
                    'is_confirmed': False
                }
            )
            q_map_obj.page_numbers_json = pg_list
            q_map_obj.regions_json = reg_dicts
            q_map_obj.confidence = avg_conf
            q_map_obj.mapping_status = status
            q_map_obj.save()

            final_mapping_payload.append({
                'mapping_id': q_map_obj.id,
                'question_id': q_id,
                'question_number': normalize_q_code(QuestionAccessor.get_question_number(q)),
                'prompt_text': QuestionAccessor.get_text(q),
                'max_marks': QuestionAccessor.get_marks(q),
                'page_numbers': pg_list,
                'regions': reg_dicts,
                'confidence': avg_conf,
                'mapping_status': status,
                'is_confirmed': q_map_obj.is_confirmed,
                'detected_headers': list(set([r.heading_text for r in reg_list if r.heading_text]))
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

        # Save Image Debug Overlay Artifact: request_trace/eval_{submission.id}/question_heading_detection_debug.png & layout_debug.png
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

        has_unresolved_or_conflict = any(r.get('requires_review') for r in page_mapping_records)

        return {
            'success': True,
            'submission_id': submission.id,
            'mappings': final_mapping_payload,
            'summary': final_mapping_payload,
            'page_records': page_mapping_records,
            'page_regions_map': {p: [r.to_dict() for r in regs] for p, regs in page_regions_map.items()},
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
        Renders question_heading_detection_debug.png and layout_debug.png visual summary grid
        with AnswerRegion bounding box overlays.
        Color codes:
        Blue (255, 140, 0) = Q1 regions
        Green (0, 200, 0)  = Q2 regions
        Orange (0, 140, 255) = Q3 regions
        Purple (255, 0, 255) = Q4 regions
        Red (0, 0, 255)     = Conflict / Ambiguous
        Yellow (0, 255, 255) = Possible Missed Heading / Transition
        """
        out_path = os.path.join(trace_dir, 'question_heading_detection_debug.png')
        layout_debug_path = os.path.join(trace_dir, 'layout_debug.png')

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
                regions = rec.get('regions', [])

                # Draw region bounding boxes on high-res image before thumbnail resize
                for reg in regions:
                    bbox = reg.get('bbox', {})
                    ymin = int(bbox.get('ymin', 0.0) * h)
                    ymax = int(bbox.get('ymax', 1.0) * h)
                    xmin = int(bbox.get('xmin', 0.0) * w)
                    xmax = int(bbox.get('xmax', 1.0) * w)

                    q_num = reg.get('question_number', 'UNMAPPED')
                    method = reg.get('mapping_method', 'UNRESOLVED')
                    level = reg.get('confidence_level', 'UNKNOWN')

                    if q_num == '1':
                        color_bgr = (255, 140, 0)  # Blue
                    elif q_num == '2':
                        color_bgr = (0, 200, 0)    # Green
                    elif q_num == '3':
                        color_bgr = (0, 140, 255)  # Orange
                    elif q_num == '4':
                        color_bgr = (255, 0, 255)  # Purple
                    elif method == 'POSSIBLE_MISSED_HEADING':
                        color_bgr = (0, 255, 255)  # Yellow
                    else:
                        color_bgr = (0, 0, 255) if reg.get('requires_review') else (128, 128, 128)

                    cv2.rectangle(bgr, (xmin, ymin), (xmax - 1, ymax - 1), color_bgr, 4)
                    clean_q_lbl = f"Q{re.sub(r'^[Qq]+', '', str(q_num))}" if str(q_num) != 'UNMAPPED' else 'UNMAPPED'
                    lbl = f"{clean_q_lbl} [{method}] ({level})"
                    cv2.putText(bgr, lbl, (xmin + 10, ymin + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_bgr, 2)

                thumb_w = 300
                thumb = cv2.resize(bgr, (thumb_w, 400))

                primary_q = rec.get('question_number', 'UNMAPPED')
                cv2.rectangle(thumb, (0, 0), (thumb_w, 45), (20, 20, 20), -1)
                clean_primary_q = f"Q{re.sub(r'^[Qq]+', '', str(primary_q))}" if str(primary_q) != 'UNMAPPED' else 'UNMAPPED'
                q_label = f"Pg {p_num} -> {clean_primary_q}"
                cv2.putText(thumb, q_label, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

                cv2.rectangle(thumb, (0, 360), (thumb_w, 400), (20, 20, 20), -1)
                conf_pct = int(rec.get('confidence', 0.0) * 100)
                sub_label = f"{rec.get('method', 'UNRESOLVED')} ({conf_pct}%)"
                cv2.putText(thumb, sub_label, (10, 388), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 215, 255), 1)

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
                cv2.imwrite(layout_debug_path, canvas)
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
        Creates/updates SubmissionAnswer text for each question using region-scoped extraction.
        """
        with transaction.atomic():
            submission = StudentSubmission.objects.get(id=submission_id)
            pages = {p.page_number: p for p in submission.pages.all()}

            for m_item in confirmed_mappings:
                q_id = m_item.get('question_id')
                raw_pg_list = m_item.get('page_numbers') or m_item.get('pages', [])
                reg_list = m_item.get('regions') or m_item.get('regions_json', [])

                if not q_id:
                    continue

                # Ensure strict ascending integer sorting on page numbers
                sorted_pg_list = sorted([int(p) for p in raw_pg_list if str(p).isdigit() or isinstance(p, (int, float))])

                q_obj = Question.objects.get(id=q_id)
                q_map, _ = QuestionMapping.objects.get_or_create(submission=submission, question=q_obj)
                
                # If explicit bounding boxes are provided, use them; otherwise reconstruct clean full-page regions
                if reg_list:
                    q_map.regions_json = reg_list
                else:
                    new_regions = [
                        {
                            "page_number": int(p),
                            "region_id": f"p{p}_q{normalize_q_code(q_obj.question_number)}_confirmed",
                            "bbox": {"ymin": 0.0, "xmin": 0.0, "ymax": 1.0, "xmax": 1.0},
                            "confidence": 1.0,
                            "source": "TEACHER_CONFIRMED"
                        }
                        for p in sorted_pg_list
                    ]
                    q_map.regions_json = new_regions

                q_map.page_numbers_json = sorted_pg_list
                q_map.confidence = 1.0  # Teacher confirmed
                q_map.mapping_status = QuestionMapping.Status.MANUAL_OVERRIDE
                q_map.is_confirmed = True
                q_map.save()

                # Concatenate region-scoped answer text from mapped pages in ascending order
                combined_ans_text = []
                for p_num in sorted_pg_list:
                    if p_num in pages and pages[p_num].ocr_raw_text:
                        combined_ans_text.append(f"--- PAGE {p_num} --- \n" + pages[p_num].ocr_raw_text)

                ans_text = "\n\n".join(combined_ans_text).strip() if combined_ans_text else f"[Question {normalize_q_code(q_obj.question_number)} unmapped / skipped by student]"

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
