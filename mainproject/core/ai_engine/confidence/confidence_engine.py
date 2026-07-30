from typing import Dict, Any

class ConfidenceEngine:
    """
    Confidence Evaluation & Decision Routing Engine for IntelliGrade Script Grading:
    - > 95% Confidence: Auto-Accepted
    - 90% - 95% Confidence: Faculty Review Recommended
    - < 90% Confidence: Mandatory Manual Review Required
    """

    @staticmethod
    def categorize_confidence(score: float) -> Dict[str, Any]:
        normalized_score = float(score)
        if normalized_score > 1.0:
            normalized_score = normalized_score / 100.0

        if normalized_score >= 0.95:
            action = "AUTO_ACCEPTED"
            message = "High AI Confidence (>95%). Marks automatically accepted."
            requires_manual = False
        elif normalized_score >= 0.90:
            action = "REVIEW_RECOMMENDED"
            message = "Good AI Confidence (90-95%). Faculty review recommended."
            requires_manual = False
        else:
            action = "MANDATORY_MANUAL_REVIEW"
            message = "Low AI Confidence (<90%). Mandatory manual faculty review required."
            requires_manual = True

        return {
            "score": round(normalized_score, 4),
            "percentage": f"{round(normalized_score * 100, 1)}%",
            "action": action,
            "message": message,
            "requires_manual_review": requires_manual
        }
