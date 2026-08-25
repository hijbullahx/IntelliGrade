import re
from typing import Dict, Any, List
from django.db import transaction
from core.models import StudentSubmission, CourseTabulation, StudentGradeRecord, Examination, SubmissionAnswer, EvaluationResult

class TabulationService:

    @classmethod
    def get_letter_grade(cls, score: float) -> str:
        """Assigns letter grade based on percentage score standard."""
        if score >= 80.0:
            return 'A+'
        elif score >= 75.0:
            return 'A'
        elif score >= 70.0:
            return 'A-'
        elif score >= 65.0:
            return 'B+'
        elif score >= 60.0:
            return 'B'
        elif score >= 55.0:
            return 'B-'
        elif score >= 50.0:
            return 'C+'
        elif score >= 45.0:
            return 'C'
        elif score >= 40.0:
            return 'D'
        else:
            return 'F'

    @classmethod
    def sync_submission_to_tabulation(cls, submission_id: int) -> StudentGradeRecord:
        """
        Synchronizes a student's evaluated submission into the CourseTabulation and StudentGradeRecord.
        Aggregates question-level scores into CO and PO buckets and recomputes continuous overall marks & grades.
        """
        try:
            submission = StudentSubmission.objects.select_related('examination__course').get(id=submission_id)
        except StudentSubmission.DoesNotExist:
            return None

        exam = submission.examination
        if not exam or not exam.course:
            return None

        course = exam.course
        student_roll = (submission.student_roll_no or '').strip()
        student_name = (submission.student_name or '').strip()

        if not student_roll:
            student_roll = f"STU-{submission.id}"

        # 1. Get or create CourseTabulation
        default_weightages = {
            'class_test': 10.0,
            'midterm': 25.0,
            'final': 50.0,
            'assignment': 10.0,
            'attendance': 5.0
        }
        tabulation, _ = CourseTabulation.objects.get_or_create(
            course=course,
            semester='Spring 2026',
            section='C',
            defaults={'weightage_config': default_weightages}
        )

        # 2. Get or create StudentGradeRecord
        grade_record, _ = StudentGradeRecord.objects.get_or_create(
            tabulation=tabulation,
            student_id=student_roll,
            defaults={'student_name': student_name or student_roll}
        )
        if student_name and grade_record.student_name != student_name:
            grade_record.student_name = student_name

        # 3. Aggregate all evaluated submissions for this student in this course
        all_submissions = StudentSubmission.objects.filter(
            examination__course=course,
            student_roll_no=student_roll
        ).select_related('examination')

        exam_scores = grade_record.exam_scores or {}
        co_scores = {}
        po_scores = {}

        category_totals = {
            'class_test': [],
            'midterm': [],
            'final': [],
            'assignment': []
        }

        for sub in all_submissions:
            sub_exam = sub.examination
            exam_key = f"exam_{sub_exam.id}"
            
            # Map exam title/type to category
            ex_type = (getattr(sub_exam, 'exam_type', '') or sub_exam.title or '').upper()
            if 'MID' in ex_type:
                cat = 'midterm'
            elif 'FINAL' in ex_type:
                cat = 'final'
            elif 'ASSIGN' in ex_type:
                cat = 'assignment'
            else:
                cat = 'class_test'

            sub_pct = float(sub.percentage or 0.0)
            category_totals[cat].append(sub_pct)

            q_breakdown = {}
            for sa in sub.answers.all().select_related('question', 'evaluation_result'):
                q = sa.question
                er = getattr(sa, 'evaluation_result', None)
                marks_obtained = float(er.obtained_marks) if er else 0.0
                max_marks = float(er.maximum_marks) if er else float(q.max_marks or 10.0)

                q_num = q.question_number or f"Q{q.id}"
                q_breakdown[q_num] = {
                    'obtained': marks_obtained,
                    'max': max_marks,
                    'co': q.co_mapping or 'CO1',
                    'po': q.po_mapping or ['PO1']
                }

                # CO Bucket
                co_tag = (q.co_mapping or 'CO1').upper().strip()
                co_scores[co_tag] = round(co_scores.get(co_tag, 0.0) + marks_obtained, 2)

                # PO Bucket
                po_tags = q.po_mapping if isinstance(q.po_mapping, list) else [q.po_mapping or 'PO1']
                for po_item in po_tags:
                    p_tag = str(po_item).upper().strip()
                    po_scores[p_tag] = round(po_scores.get(p_tag, 0.0) + marks_obtained, 2)

            exam_scores[exam_key] = {
                'exam_id': sub_exam.id,
                'exam_title': sub_exam.title,
                'category': cat,
                'total_obtained': float(sub.total_obtained_marks or 0.0),
                'total_max': float(sub.total_max_marks or 100.0),
                'percentage': sub_pct,
                'questions': q_breakdown
            }

        # 4. Compute overall weighted score (normalized to evaluated categories)
        weights = tabulation.weightage_config or default_weightages
        weighted_sum = 0.0
        active_weight_sum = 0.0

        for cat_name, scores in category_totals.items():
            if scores:
                avg_pct = sum(scores) / len(scores)
                w_factor = float(weights.get(cat_name, 0.0))
                weighted_sum += (avg_pct * (w_factor / 100.0))
                active_weight_sum += w_factor

        if active_weight_sum > 0:
            overall_score = (weighted_sum / (active_weight_sum / 100.0))
        else:
            overall_score = 0.0

        # Add attendance bonus (default 5% if configured)
        attendance_bonus = float(weights.get('attendance', 5.0))
        overall_score = round(min(100.0, overall_score), 2)

        letter_grade = cls.get_letter_grade(overall_score)

        grade_record.exam_scores = exam_scores
        grade_record.co_scores = co_scores
        grade_record.po_scores = po_scores
        grade_record.overall_score = overall_score
        grade_record.letter_grade = letter_grade
        grade_record.save()

        return grade_record
