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

    # 3. Aggregate Question-level Marks & CO/PO Distributions for latest submissions of each distinct exam
    raw_subs = StudentSubmission.objects.filter(
        examination__course=course,
        student_roll_no=student_id
    ).select_related('examination').order_by('examination_id', '-updated_at', '-id')

    # Deduplicate: pick only the latest active submission per distinct examination
    unique_exam_subs = {}
    for s in raw_subs:
        if s.examination_id not in unique_exam_subs:
            unique_exam_subs[s.examination_id] = s

    if not unique_exam_subs and submission.examination_id:
        unique_exam_subs[submission.examination_id] = submission

    active_subs = list(unique_exam_subs.values())

    co_scores = {}
    po_scores = {}
    exam_scores = {}
    category_percentages = {
        'class_test': [],
        'midterm': [],
        'final': [],
        'assignment': []
    }

    for sub in active_subs:
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
        q_metadata = {}
        total_sub_obtained = 0.0
        total_sub_max = 0.0

        answers = sub.answers.all().select_related('question__rubric', 'evaluation_result').order_by('question_id', 'id')
        if answers.exists():
            import re
            for idx, sa in enumerate(answers, start=1):
                q = sa.question
                er = getattr(sa, 'evaluation_result', None)
                marks = float(er.obtained_marks if (er and er.obtained_marks is not None) else 0.0)
                max_m = float(er.maximum_marks if (er and er.maximum_marks is not None) else (getattr(q, 'max_marks', None) or getattr(q, 'marks', None) or 10.0))

                total_sub_obtained += marks
                total_sub_max += max_m

                raw_q_num = str(getattr(q, 'question_number', '') or getattr(q, 'number', '') or f"{idx}").strip()
                num_match = re.search(r'\d+', raw_q_num)
                q_num_int = int(num_match.group()) if num_match else idx

                # Store by multiple access keys for bulletproof retrieval
                q_breakdown[str(q_num_int)] = marks
                q_breakdown[f"Q{q_num_int}"] = marks
                q_breakdown[str(idx)] = marks
                q_breakdown[raw_q_num] = marks

                # CO Mapping
                co_tag = (getattr(q, 'co_mapping', None) or getattr(q, 'co', None) or getattr(q, 'co_mapped', None) or 'CO1')
                if isinstance(co_tag, (list, tuple, set)):
                    co_tag = ", ".join(str(c).strip(" '\"[]") for c in co_tag if str(c).strip())
                co_tag = str(co_tag).upper().strip().replace("'", "").replace("[", "").replace("]", "")
                co_scores[co_tag] = round(co_scores.get(co_tag, 0.0) + marks, 2)

                # PO Mapping
                po_tags = getattr(q, 'po_mapping', None) or getattr(q, 'po', None) or getattr(q, 'po_mapped', None) or ['PO1']
                if not isinstance(po_tags, list):
                    po_tags = [po_tags]
                clean_po_list = []
                for p_item in po_tags:
                    p_tag = str(p_item).upper().strip().replace("'", "").replace("[", "").replace("]", "")
                    if p_tag:
                        clean_po_list.append(p_tag)
                        po_scores[p_tag] = round(po_scores.get(p_tag, 0.0) + marks, 2)

                q_metadata[str(q_num_int)] = {
                    'num': q_num_int,
                    'obtained': marks,
                    'max_marks': max_m,
                    'co': co_tag,
                    'po': clean_po_list
                }

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
            'breakdown': q_breakdown,
            'q_metadata': q_metadata
        }

    # 4. Get or Create StudentGradeRecord
    record, created = StudentGradeRecord.objects.get_or_create(
        tabulation=tabulation,
        student_id=student_id,
        defaults={'student_name': student_name}
    )

    # If the faculty has manually edited and locked this grade record, preserve their custom values
    if not created and getattr(record, 'is_manually_edited', False):
        return record

    record.student_name = student_name
    record.exam_scores = exam_scores
    record.co_scores = co_scores
    record.po_scores = po_scores

    # 5. Calculate Exact Institutional Weighted Total Score & Letter Grade
    weights = tabulation.weightage_config or {
        'class_test': 10.0, 'midterm': 25.0, 'final': 50.0, 'assignment': 10.0, 'attendance': 5.0
    }
    w_ct = float(weights.get('class_test', 10.0))
    w_mid = float(weights.get('midterm', 25.0))
    w_fn = float(weights.get('final', 50.0))
    w_as = float(weights.get('assignment', 10.0))
    w_att = float(weights.get('attendance', 5.0))

    ct_pct = (sum(category_percentages['class_test']) / len(category_percentages['class_test'])) if category_percentages['class_test'] else 0.0
    mid_pct = (sum(category_percentages['midterm']) / len(category_percentages['midterm'])) if category_percentages['midterm'] else 0.0
    fn_pct = (sum(category_percentages['final']) / len(category_percentages['final'])) if category_percentages['final'] else 0.0
    as_pct = (sum(category_percentages['assignment']) / len(category_percentages['assignment'])) if category_percentages['assignment'] else 0.0

    # Institutional standard weighted sum
    weighted_total = (ct_pct * (w_ct / 100.0)) + (mid_pct * (w_mid / 100.0)) + (fn_pct * (w_fn / 100.0)) + (as_pct * (w_as / 100.0))
    
    # If any academic assessment is evaluated, attendance is added
    att_marks = float(getattr(record, 'attendance_marks', 5.0) or 5.0)
    if category_percentages['final'] or category_percentages['midterm'] or category_percentages['class_test']:
        weighted_total += att_marks

    overall = round(min(100.0, max(0.0, weighted_total)), 2)
    record.overall_score = overall
    record.attendance_marks = att_marks

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

    # 6. Clean up any stale / duplicate ghost records for this course that have no matching active submission
    try:
        active_ids = set()
        course_subs = StudentSubmission.objects.filter(examination__course=course)
        for s in course_subs:
            s_id = (s.student_roll_no or s.student_name or f"STU-{s.id}").strip()
            if s_id:
                active_ids.add(s_id)
        
        stale_records = StudentGradeRecord.objects.filter(tabulation=tabulation).exclude(student_id__in=active_ids)
        if stale_records.exists():
            print(f"[TABULATION CLEANUP] Purging {stale_records.count()} orphaned/renamed grade record(s) from {course.code} tabulation.")
            stale_records.delete()
    except Exception as e_clean:
        print(f"[TABULATION CLEANUP WARNING] {e_clean}")

    return record


class TabulationService:
    @staticmethod
    def sync_submission_to_tabulation(submission_or_id):
        return sync_submission_to_tabulation(submission_or_id)
