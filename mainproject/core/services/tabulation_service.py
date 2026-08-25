from typing import Dict, Any, List, Union
from django.db import transaction
from core.models import Examination, StudentSubmission, CourseTabulation, StudentGradeRecord

def sync_submission_to_tabulation(submission_or_id: Union[StudentSubmission, int]) -> StudentGradeRecord:
    """
    Synchronizes a student's evaluated submission into CourseTabulation and StudentGradeRecord.
    Supports receiving either a StudentSubmission instance or an integer submission ID.
    Aggregates question-level scores, CO/PO distributions, overall score, and letter grade.
    """
    if isinstance(submission_or_id, StudentSubmission):
        submission = submission_or_id
    else:
        try:
            submission = StudentSubmission.objects.select_related('examination__course').get(id=submission_or_id)
        except StudentSubmission.DoesNotExist:
            return None

    exam = submission.examination
    if not exam or not exam.course:
        return None

    course = exam.course

    # 1. Get or Create CourseTabulation for this course
    semester = getattr(exam, 'semester', None) or getattr(course, 'semester', None) or 'Spring 2026'
    section = getattr(exam, 'section', None) or getattr(course, 'section', None) or 'C'

    tabulation, _ = CourseTabulation.objects.get_or_create(
        course=course,
        semester=semester,
        section=section,
        defaults={
            'weightage_config': {
                'class_test': 10,
                'midterm': 25,
                'final': 50,
                'assignment': 10,
                'attendance': 5
            }
        }
    )

    # 2. Extract Student Identity
    student_id = (submission.student_roll_no or submission.student_name or f"STU-{submission.id}").strip()
    student_name = (submission.student_name or "Unknown Student").strip()

    # 3. Aggregate Question-level Marks & CO/PO Distributions for ALL submissions of this student in this course
    all_subs = StudentSubmission.objects.filter(
        examination__course=course
    ).filter(
        student_roll_no=student_id
    ).select_related('examination')

    if not all_subs.exists():
        all_subs = [submission]

    co_scores = {}
    po_scores = {}
    exam_scores = {}
    category_percentages = {
        'class_test': [],
        'midterm': [],
        'final': [],
        'assignment': []
    }

    for sub in all_subs:
        sub_exam = sub.examination
        ex_title = (sub_exam.title or '').upper()
        if 'MID' in ex_title:
            exam_type_key = 'midterm'
        elif 'QUIZ' in ex_title or 'TEST' in ex_title or 'CLASS' in ex_title or 'CT' in ex_title:
            exam_type_key = 'class_test'
        elif 'ASSIGN' in ex_title or 'HW' in ex_title or 'PROJECT' in ex_title:
            exam_type_key = 'assignment'
        elif 'FINAL' in ex_title:
            exam_type_key = 'final'
        else:
            exam_type_key = 'final'

        q_breakdown = {}
        total_sub_obtained = 0.0
        total_sub_max = 0.0

        # Try sub.answers.all() first
        answers = sub.answers.all().select_related('question', 'evaluation_result')
        if answers.exists():
            for sa in answers:
                q = sa.question
                er = getattr(sa, 'evaluation_result', None)
                marks = float(er.obtained_marks or 0.0) if er else 0.0
                max_m = float(er.maximum_marks or 10.0) if er else float(q.max_marks or 10.0)

                total_sub_obtained += marks
                total_sub_max += max_m

                q_num = q.question_number or f"Q{q.id}"
                q_breakdown[q_num] = marks

                # CO Mapping
                co_tag = (getattr(q, 'co_mapping', None) or getattr(q, 'co', None) or getattr(q, 'co_mapped', None) or 'CO1')
                co_tag = str(co_tag).upper().strip()
                co_scores[co_tag] = round(co_scores.get(co_tag, 0.0) + marks, 2)

                # PO Mapping
                po_tags = getattr(q, 'po_mapping', None) or getattr(q, 'po', None) or getattr(q, 'po_mapped', None) or ['PO1']
                if not isinstance(po_tags, list):
                    po_tags = [po_tags]
                for p_item in po_tags:
                    p_tag = str(p_item).upper().strip()
                    po_scores[p_tag] = round(po_scores.get(p_tag, 0.0) + marks, 2)

        if total_sub_max <= 0:
            total_sub_obtained = float(sub.total_obtained_marks or 0.0)
            total_sub_max = float(sub.total_max_marks or getattr(sub_exam, 'total_marks', 100.0) or 100.0)

        sub_pct = round((total_sub_obtained / max(1.0, total_sub_max)) * 100.0, 2)
        category_percentages[exam_type_key].append(sub_pct)

        exam_scores[str(sub_exam.id)] = {
            'exam_title': sub_exam.title,
            'exam_type': exam_type_key,
            'category': exam_type_key,
            'obtained': total_sub_obtained,
            'max_marks': total_sub_max,
            'percentage': sub_pct,
            'breakdown': q_breakdown
        }

    # 4. Get or Create StudentGradeRecord
    record, _ = StudentGradeRecord.objects.get_or_create(
        tabulation=tabulation,
        student_id=student_id,
        defaults={'student_name': student_name}
    )
    record.student_name = student_name
    record.exam_scores = exam_scores
    record.co_scores = co_scores
    record.po_scores = po_scores

    # 5. Calculate Weighted Overall Marks & Letter Grade
    weights = tabulation.weightage_config or {
        'class_test': 10, 'midterm': 25, 'final': 50, 'assignment': 10, 'attendance': 5
    }

    weighted_sum = 0.0
    active_weights = 0.0

    for cat_key, pct_list in category_percentages.items():
        if pct_list:
            avg_cat_pct = sum(pct_list) / len(pct_list)
            w = float(weights.get(cat_key, 0.0))
            weighted_sum += (avg_cat_pct * (w / 100.0))
            active_weights += w

    if active_weights > 0:
        overall = (weighted_sum / (active_weights / 100.0))
    else:
        overall = 0.0

    overall = round(min(100.0, overall), 2)
    record.overall_score = overall

    if overall >= 80: record.letter_grade = 'A+'
    elif overall >= 75: record.letter_grade = 'A'
    elif overall >= 70: record.letter_grade = 'A-'
    elif overall >= 65: record.letter_grade = 'B+'
    elif overall >= 60: record.letter_grade = 'B'
    elif overall >= 55: record.letter_grade = 'B-'
    elif overall >= 50: record.letter_grade = 'C+'
    elif overall >= 45: record.letter_grade = 'C'
    elif overall >= 40: record.letter_grade = 'D'
    else: record.letter_grade = 'F'

    record.save()
    return record


class TabulationService:
    @staticmethod
    def sync_submission_to_tabulation(submission_or_id):
        return sync_submission_to_tabulation(submission_or_id)
