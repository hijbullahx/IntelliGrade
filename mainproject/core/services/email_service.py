import os
import logging
import threading
from typing import List, Optional
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

class EmailService:
    """
    Centralized Institutional Email Service for IntelliGrade.
    Sender: intelligrade@dsr.iubat.ac.bd
    Dispatches emails asynchronously using background threads for non-blocking responses.
    """

    @classmethod
    def _get_base_url(cls) -> str:
        """Dynamically resolves the base application URL from settings.SITE_URL."""
        return getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')

    @classmethod
    def _send_async_email(
        cls,
        subject: str,
        recipient_list: List[str],
        template_name: str,
        context: dict,
        attachment_path: Optional[str] = None,
        sync: bool = False,
    ):
        """Internal helper to dispatch email asynchronously in a background thread or synchronously."""
        def _dispatch():
            try:
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'IntelliGrade Support <intelligrade@dsr.iubat.ac.bd>')
                html_content = render_to_string(template_name, context)
                text_content = strip_tags(html_content)

                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=from_email,
                    to=recipient_list
                )
                msg.attach_alternative(html_content, "text/html")

                if attachment_path and os.path.exists(attachment_path):
                    msg.attach_file(attachment_path)

                msg.send(fail_silently=False)
                print(f"[EMAIL SERVICE OK] Dispatched '{subject}' to {recipient_list}")
                return True
            except Exception as e:
                logger.error(f"[EMAIL SERVICE ERROR] Failed to send '{subject}' to {recipient_list}: {e}")
                print(f"[EMAIL SERVICE ERROR] Failed to send '{subject}' to {recipient_list}: {e}")
                if sync:
                    raise
                return False

        if sync:
            return _dispatch()

        # Start non-blocking background thread
        thread = threading.Thread(target=_dispatch, daemon=True)
        thread.start()
        return thread

    @classmethod
    def send_account_creation_email(cls, user, raw_password: Optional[str] = None, activation_token: Optional[str] = None, sync: bool = False):
        """Sends account welcome & provisioning email."""
        recipient = getattr(user, 'email', None) or getattr(user, 'username', None)
        if not recipient or '@' not in recipient:
            return None

        subject = "Welcome to IntelliGrade Institutional Academic Portal"
        context = {
            'user': user,
            'raw_password': raw_password,
            'activation_token': activation_token,
            'login_url': f"{cls._get_base_url()}/",
        }
        return cls._send_async_email(subject, [recipient], 'emails/account_welcome.html', context, sync=sync)

    @classmethod
    def send_password_reset_otp_email(cls, user, otp_code: str, sync: bool = False):
        """Sends 6-digit security OTP email for password reset."""
        recipient = getattr(user, 'email', None) or getattr(user, 'username', None)
        if not recipient or '@' not in recipient:
            return None

        subject = f"[Password Reset] Your OTP Code: {otp_code} - IntelliGrade"
        context = {
            'user': user,
            'otp_code': otp_code,
            'reset_url': f"{cls._get_base_url()}/auth/verify-otp/",
            'login_url': f"{cls._get_base_url()}/",
        }
        return cls._send_async_email(subject, [recipient], 'emails/otp_password_reset.html', context, sync=sync)

    @classmethod
    def send_exam_assigned_notification(cls, student_email: str, student_name: str, exam_title: str, course_code: str, exam_date: str, sync: bool = False):
        """Sends notification when a new exam is published."""
        if not student_email or '@' not in student_email:
            return None

        subject = f"[Exam Scheduled] {course_code} - {exam_title}"
        context = {
            'student_name': student_name,
            'exam_title': exam_title,
            'course_code': course_code,
            'exam_date': str(exam_date),
            'portal_url': f"{cls._get_base_url()}/",
        }
        return cls._send_async_email(subject, [student_email], 'emails/exam_assigned.html', context, sync=sync)

    @classmethod
    def send_evaluation_published_notification(cls, student_email: str, student_name: str, exam_title: str, score: str, grade: str, remarks: Optional[str] = None, sync: bool = False):
        """Sends notification when answer script evaluation results are published."""
        if not student_email or '@' not in student_email:
            return None

        subject = f"[Result Published] {exam_title} (Score: {score}) - IntelliGrade"
        context = {
            'student_name': student_name,
            'exam_title': exam_title,
            'score': score,
            'grade': grade,
            'remarks': remarks,
            'script_url': f"{cls._get_base_url()}/",
        }
        return cls._send_async_email(subject, [student_email], 'emails/evaluation_published.html', context, sync=sync)

    @classmethod
    def send_faculty_report_summary_email(cls, faculty_email: str, course_code: str, section: str, export_file_path: Optional[str] = None, sync: bool = False):
        """Sends faculty / department summary report with Excel spreadsheet attachment."""
        if not faculty_email or '@' not in faculty_email:
            return None

        subject = f"[OBE Report] {course_code} Section {section} - Official Tabulation Sheet"
        context = {
            'course_code': course_code,
            'section': section,
            'portal_url': f"{cls._get_base_url()}/",
        }
        return cls._send_async_email(subject, [faculty_email], 'emails/faculty_report_summary.html', context, attachment_path=export_file_path, sync=sync)
