from typing import Dict, Any, List, Union, Optional


def evaluate_quiz_submission(
    detected_results: Dict[str, Dict[str, Any]], 
    answer_key: Dict[str, Union[str, List[str]]], 
    marks_per_question: float = 1.0,
    negative_marking: float = 0.0
) -> Dict[str, Any]:
    """
    Evaluates detected MCQ/Quiz option choices against an authoritative answer key.
    
    Args:
        detected_results: Dict mapping question ID (e.g., 'Q1') to detection output:
            {
               "Q1": {"detected": ["ii"], "status": "VALID", "mark_type": "Tick (✓)"},
               "Q2": {"detected": ["1", "3"], "status": "REJECTED_MULTIPLE_MARKS", "mark_type": "Multi-Fill"},
               "Q3": {"detected": ["B"], "status": "VALID", "mark_type": "Filled Bubble (⬤)"},
               "Q4": {"detected": [], "status": "NOT_ATTEMPTED", "mark_type": "None"}
            }
        answer_key: Dict mapping question ID to correct answer (e.g. {'Q1': 'ii', 'Q2': '1', 'Q3': 'B', 'Q4': 'C'})
        marks_per_question: Marks awarded for each correct answer (default: 1.0)
        negative_marking: Marks deducted for incorrect or rejected answers (default: 0.0)
        
    Returns:
        Dict summary containing aggregate metrics, accuracy percentage, and detailed question_breakdown.
    """
    total_questions = len(answer_key)
    total_attempted = 0
    total_correct = 0
    total_incorrect = 0
    total_rejected = 0
    total_not_attempted = 0
    total_score = 0.0

    question_breakdown = {}

    for q_id, correct_ans in answer_key.items():
        det_info = detected_results.get(q_id, {"detected": [], "status": "NOT_ATTEMPTED", "mark_type": "None"})
        if isinstance(det_info, list):
            det_list = det_info
            det_status = "VALID" if det_list else "NOT_ATTEMPTED"
            mark_type = "Checkmark" if det_list else "None"
        elif isinstance(det_info, dict):
            det_status = det_info.get("status", "NOT_ATTEMPTED")
            det_list = det_info.get("detected", [])
            mark_type = det_info.get("mark_type", "None")
        else:
            det_status = "NOT_ATTEMPTED"
            det_list = []
            mark_type = "None"

        # Normalize correct answer to a set of strings for exact matching
        if isinstance(correct_ans, (list, tuple, set)):
            target_set = {str(a).strip().lower() for a in correct_ans}
            target_display = [str(a).strip() for a in correct_ans]
        else:
            target_set = {str(correct_ans).strip().lower()}
            target_display = str(correct_ans).strip()

        det_set = {str(a).strip().lower() for a in det_list}

        is_correct = False
        obtained_marks = 0.0
        final_q_status = "NOT_ATTEMPTED"

        if det_status == "REJECTED_MULTIPLE_MARKS":
            total_rejected += 1
            total_attempted += 1
            final_q_status = "REJECTED_MULTIPLE_MARKS"
            obtained_marks = -abs(float(negative_marking)) if negative_marking > 0 else 0.0

        elif det_status == "NOT_ATTEMPTED" or not det_list:
            total_not_attempted += 1
            final_q_status = "NOT_ATTEMPTED"
            obtained_marks = 0.0

        elif det_status == "VALID":
            total_attempted += 1
            if det_set == target_set:
                is_correct = True
                total_correct += 1
                final_q_status = "CORRECT"
                obtained_marks = float(marks_per_question)
            else:
                total_incorrect += 1
                final_q_status = "INCORRECT"
                obtained_marks = -abs(float(negative_marking)) if negative_marking > 0 else 0.0

        total_score += obtained_marks

        question_breakdown[q_id] = {
            "question_id": q_id,
            "correct_answer": target_display,
            "detected_answer": det_list,
            "status": final_q_status,
            "is_correct": is_correct,
            "marks_obtained": round(obtained_marks, 2),
            "max_marks": float(marks_per_question),
            "mark_type": mark_type
        }

    max_possible_score = float(total_questions * marks_per_question)
    percentage = round((max(0.0, total_score) / max(1.0, max_possible_score)) * 100.0, 2)

    return {
        "total_questions": total_questions,
        "total_attempted": total_attempted,
        "total_correct": total_correct,
        "total_incorrect": total_incorrect,
        "total_rejected": total_rejected,
        "total_not_attempted": total_not_attempted,
        "total_score": round(total_score, 2),
        "max_possible_score": max_possible_score,
        "percentage": percentage,
        "question_breakdown": question_breakdown
    }


class QuizEvaluator:
    """
    Class wrapper for Quiz/MCQ Evaluation pipeline operations.
    """
    @staticmethod
    def evaluate(
        detected_results: Dict[str, Dict[str, Any]], 
        answer_key: Dict[str, Union[str, List[str]]], 
        marks_per_question: float = 1.0,
        negative_marking: float = 0.0
    ) -> Dict[str, Any]:
        return evaluate_quiz_submission(detected_results, answer_key, marks_per_question, negative_marking)
