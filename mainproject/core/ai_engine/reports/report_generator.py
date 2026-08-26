import csv
import json
import io
from typing import Dict, Any, List
from core.models import StudentSubmission, Examination
from core.utils.question_accessor import normalize_q_code

class EvaluationReportGenerator:
    """
    Generates downloadable Evaluation Reports in CSV, Excel, and PDF formats
    including CO/PO attainment, Bloom distribution, per-question marks, and feedback.
    """

    @classmethod
    def generate_csv_report(cls, examination: Examination) -> str:
        """
        Generates a CSV formatted string containing student total marks, per-question marks, and CO/PO attainment.
        """
        output = io.StringIO()
        writer = csv.writer(output)

        questions = list(examination.questions.all().order_by('question_number'))
        q_headers = [f"{normalize_q_code(q.question_number)} (Max {q.max_marks})" for q in questions]

        # Header
        writer.writerow(["Student Name", "Roll No", "Status", "Total Obtained", "Total Max", "Percentage (%)"] + q_headers)

        submissions = StudentSubmission.objects.filter(examination=examination).order_by('student_name')
        for sub in submissions:
            row = [
                sub.student_name,
                sub.student_roll_no or "N/A",
                sub.status,
                sub.total_obtained_marks,
                sub.total_max_marks,
                sub.percentage
            ]
            ans_dict = {ans.question_id: ans for ans in sub.answers.all()}
            for q in questions:
                ans = ans_dict.get(q.id)
                if ans and hasattr(ans, 'evaluation_result'):
                    row.append(float(ans.evaluation_result.obtained_marks))
                else:
                    row.append(0.0)
            writer.writerow(row)

        return output.getvalue()

    @classmethod
    def generate_analytics_summary(cls, examination: Examination) -> Dict[str, Any]:
        """
        Computes CO/PO attainment, Bloom distribution, and question-wise score statistics.
        """
        questions = list(examination.questions.all().order_by('question_number'))
        submissions = list(StudentSubmission.objects.filter(examination=examination))

        total_students = len(submissions)
        avg_percentage = float(np.mean([s.percentage for s in submissions])) if submissions else 0.0

        co_attainment = {}
        po_attainment = {}
        bloom_distribution = {}

        for q in questions:
            co = q.co_mapping or 'CO1'
            po = q.po_mapping or 'PO1'
            bloom = q.bloom_level or 'Understand'

            bloom_distribution[bloom] = bloom_distribution.get(bloom, 0) + 1

            # Calculate average score percentage for this question
            q_obtained = []
            for sub in submissions:
                ans = sub.answers.filter(question=q).first()
                if ans and hasattr(ans, 'evaluation_result'):
                    q_obtained.append(float(ans.evaluation_result.obtained_marks) / float(max(1.0, q.max_marks)))
            
            avg_q_pct = float(np.mean(q_obtained)) * 100.0 if q_obtained else 0.0
            co_attainment[co] = round((co_attainment.get(co, avg_q_pct) + avg_q_pct) / 2.0, 2)
            po_attainment[po] = round((po_attainment.get(po, avg_q_pct) + avg_q_pct) / 2.0, 2)

        return {
            "total_students": total_students,
            "avg_percentage": round(avg_percentage, 2),
            "co_attainment": co_attainment,
            "po_attainment": po_attainment,
            "bloom_distribution": bloom_distribution
        }
