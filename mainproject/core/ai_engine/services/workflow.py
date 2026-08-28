"""
IntelliGrade Centralized Submission Workflow Engine.
Enforces the 13-stage assessment state machine, validates state transitions,
prevents invalid status jumping, and records audit logs.
"""

from typing import Optional, Dict, Any
from django.db import transaction, close_old_connections
from core.models import StudentSubmission, EvaluationAuditLog

class ConfigurationError(Exception):
    """Raised when an invalid status or illegal workflow transition is attempted."""
    pass


class SubmissionWorkflow:
    """
    Centralized State Machine & Workflow Orchestrator for Student Submissions.
    """

    Status = StudentSubmission.Status

    ALLOWED_TRANSITIONS: Dict[str, list] = {
        Status.UPLOADED: [Status.PREVIEW_READY, Status.WORKING_COPY_CREATED, Status.PDF_GENERATED, Status.OCR_COMPLETE, Status.FAILED],
        Status.PREVIEW_READY: [Status.WORKING_COPY_CREATED, Status.PDF_GENERATED, Status.OCR_COMPLETE, Status.FAILED],
        Status.WORKING_COPY_CREATED: [Status.PDF_GENERATED, Status.OCR_COMPLETE, Status.FAILED],
        Status.PDF_GENERATED: [Status.OCR_COMPLETE, Status.SEGMENTED, Status.FAILED],
        Status.OCR_COMPLETE: [Status.SEGMENTED, Status.MAPPING_COMPLETE, Status.FAILED],
        Status.SEGMENTED: [Status.MAPPING_COMPLETE, Status.WAITING_TEACHER_CONFIRMATION, Status.FAILED],
        Status.MAPPING_COMPLETE: [Status.WAITING_TEACHER_CONFIRMATION, Status.AI_EVALUATED, Status.FAILED],
        Status.WAITING_TEACHER_CONFIRMATION: [Status.AI_EVALUATED, Status.UNDER_REVIEW, Status.MAPPING_COMPLETE, Status.FAILED],
        Status.AI_EVALUATED: [Status.UNDER_REVIEW, Status.REVIEWED, Status.FINALIZED, Status.FAILED],
        Status.UNDER_REVIEW: [Status.REVIEWED, Status.FINALIZED, Status.AI_EVALUATED, Status.MAPPING_COMPLETE, Status.OCR_COMPLETE, Status.FAILED],
        Status.REVIEWED: [Status.FINALIZED, Status.UNDER_REVIEW, Status.AI_EVALUATED, Status.FAILED],
        Status.FINALIZED: [Status.ARCHIVED, Status.FAILED],
        Status.ARCHIVED: [Status.FAILED],
        Status.FAILED: [Status.UPLOADED, Status.PREVIEW_READY, Status.WORKING_COPY_CREATED]
    }

    @classmethod
    def can_transition(cls, current_status: str, target_status: str, force: bool = False) -> bool:
        """Checks if transitioning from current_status to target_status is valid."""
        if force:
            return True
        if current_status == target_status:
            return True
        allowed = cls.ALLOWED_TRANSITIONS.get(current_status, [])
        return target_status in allowed

    @classmethod
    def advance(
        cls,
        submission: StudentSubmission,
        target_status: str,
        user=None,
        details: Optional[Dict[str, Any]] = None,
        force: bool = False
    ) -> StudentSubmission:
        """
        Centralized state transition method.
        Validates target status, enforces state transition rules, performs atomic update,
        logs audit trail, and prints runtime state log.
        """
        # 1. Verify target status exists in enum
        valid_statuses = [choice[0] for choice in cls.Status.choices]
        if target_status not in valid_statuses:
            raise ConfigurationError(
                f"[WORKFLOW ERROR] Invalid status '{target_status}'. Must be one of: {valid_statuses}"
            )

        current_status = submission.status

        # 2. Validate state transition
        if not cls.can_transition(current_status, target_status, force=force):
            raise ConfigurationError(
                f"[WORKFLOW ILLEGAL TRANSITION] Cannot advance Submission #{submission.id} "
                f"from '{current_status}' to '{target_status}'. Allowed transitions: {cls.ALLOWED_TRANSITIONS.get(current_status, [])}"
            )

        # 3. Perform Atomic Database Update & Audit Log
        close_old_connections()
        with transaction.atomic():
            submission.status = target_status
            if target_status == cls.Status.FINALIZED:
                submission.is_finalized = True
            submission.save()

            EvaluationAuditLog.objects.create(
                submission=submission,
                user=user if user and user.is_authenticated else None,
                action=f"WORKFLOW_TRANSITION_{target_status}",
                details_json=details or {'from': current_status, 'to': target_status}
            )

        close_old_connections()

        print(f"\n==================================================")
        print(f"WORKFLOW ADVANCED: Submission #{submission.id}")
        print(f"State: {current_status} -> {target_status}")
        print(f"==================================================\n")

        return submission
