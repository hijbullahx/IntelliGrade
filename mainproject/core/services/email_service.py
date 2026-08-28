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
    def send_account_creation_email(
        cls,
        user,
        raw_password: Optional[str] = None,
        role_name: Optional[str] = None,
        department_name: Optional[str] = None,
        login_url_path: Optional[str] = None,
        is_approval: bool = False,
        activation_token: Optional[str] = None,
        sync: bool = False,
    ):
        """Sends account welcome & provisioning email with credentials and direct portal login link."""
        recipient = getattr(user, 'email', None) or getattr(user, 'username', None)
        if not recipient or '@' not in recipient:
            return None

        base_url = cls._get_base_url()
        path = (login_url_path or '/').lstrip('/')
        resolved_login_url = f"{base_url}/{path}" if path else f"{base_url}/"

        if not role_name:
            profile = getattr(user, 'profile', None)
            if profile:
                if profile.role == 'STUDENT':
                    role_name = 'Student'
                elif profile.role == 'TEACHER':
                    role_name = 'Faculty Member / Examiner'
                elif profile.role == 'DEPARTMENT_HEAD':
                    role_name = 'Department Head'
                elif profile.role == 'ADMIN':
                    role_name = 'Chief Exam Controller'

        if not department_name:
            profile = getattr(user, 'profile', None)
            if profile and profile.department:
                department_name = profile.department.name

        if is_approval:
            subject = f"[Account Approved] Welcome to IntelliGrade Student Portal ({user.username})"
        else:
            subject = f"[Account Created] Your IntelliGrade {role_name or 'Portal'} Credentials ({user.username})"

        context = {
            'user': user,
            'raw_password': raw_password,
            'role_name': role_name or 'Academic Portal User',
            'department_name': department_name or '',
            'login_url': resolved_login_url,
            'is_approval': is_approval,
            'activation_token': activation_token,
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
            'script_url': f"{cls._get_base_url()}/dashboard/student/",
        }
        return cls._send_async_email(subject, [student_email], 'emails/evaluation_published.html', context, sync=sync)

    @classmethod
    def send_submission_evaluated_email(
        cls,
        submission,
        final_pdf_path: Optional[str] = None,
        sync: bool = False
    ):
        """
        Extracts student email, calculates letter grade, aggregates question breakdowns,
        and dispatches official evaluation email with optional evaluated script PDF attachment.
        """
        student_user = getattr(submission, 'student', None)
        recipient_email = None
        student_name = submission.student_name or "Student"
        student_roll = submission.student_roll_no or ""

        if student_user and getattr(student_user, 'email', None):
            recipient_email = student_user.email
            if not student_name or student_name in ["Student", "Anonymous Student", "Pending OCR Extraction"]:
                student_name = student_user.get_full_name() or student_user.username
        elif student_roll:
            from django.contrib.auth.models import User
            matched_user = User.objects.filter(username__iexact=student_roll).first()
            if matched_user and matched_user.email:
                recipient_email = matched_user.email
                if not student_name or student_name in ["Student", "Anonymous Student", "Pending OCR Extraction"]:
                    student_name = matched_user.get_full_name() or matched_user.username
            elif '@' in student_roll:
                recipient_email = student_roll

        if not recipient_email or '@' not in recipient_email:
            print(f"[EMAIL SERVICE INFO] No registered email address associated with Submission #{submission.id} (Roll: '{student_roll}'). Email skipped.")
            return None

        obtained = float(submission.total_obtained_marks or 0.0)
        max_marks = float(submission.examination.total_marks if (submission.examination and submission.examination.total_marks) else (submission.total_max_marks or 100.0))
        pct = round((obtained / max(1.0, max_marks)) * 100.0, 1)

        def _calc_letter_grade(p):
            if p >= 80: return 'A+'
            elif p >= 75: return 'A'
            elif p >= 70: return 'A-'
            elif p >= 65: return 'B+'
            elif p >= 60: return 'B'
            elif p >= 55: return 'B-'
            elif p >= 50: return 'C+'
            elif p >= 45: return 'C'
            elif p >= 40: return 'D'
            else: return 'F'

        letter_grade = _calc_letter_grade(pct)

        answers = submission.answers.select_related('question', 'evaluation_result').all().order_by('question__question_number')
        breakdowns = []
        for ans in answers:
            er = getattr(ans, 'evaluation_result', None)
            q_num = ans.question.formatted_number if hasattr(ans.question, 'formatted_number') else (ans.question.question_number or 'Q')
            breakdowns.append({
                'question_number': q_num,
                'question_text': ans.question.prompt_text if hasattr(ans.question, 'prompt_text') else getattr(ans.question, 'question_text', ''),
                'obtained_marks': float(er.obtained_marks) if er else 0.0,
                'maximum_marks': float(er.maximum_marks) if er else float(getattr(ans.question, 'max_marks', 0.0)),
                'feedback_text': er.feedback_text if er else 'Evaluated.',
            })

        course_code = submission.examination.course.code if (submission.examination and submission.examination.course) else 'GEN'
        course_title = submission.examination.course.title if (submission.examination and submission.examination.course) else 'Course'
        exam_title = submission.examination.title if submission.examination else 'Examination'

        subject = f"[Result Published] {course_code}: {exam_title} - Grade: {letter_grade} ({obtained}/{max_marks})"

        context = {
            'student_name': student_name,
            'student_id': student_roll,
            'course_code': course_code,
            'course_title': course_title,
            'exam_title': exam_title,
            'score': f"{obtained} / {max_marks}",
            'percentage': pct,
            'grade': letter_grade,
            'answers': breakdowns,
            'script_url': f"{cls._get_base_url()}/dashboard/student/",
        }

        # Resolve PDF attachment path if exists
        pdf_path = final_pdf_path
        if not pdf_path and hasattr(submission, 'pdf_document') and submission.pdf_document.pdf_file:
            try:
                pdf_path = submission.pdf_document.pdf_file.path
            except Exception:
                pass

        return cls._send_async_email(
            subject=subject,
            recipient_list=[recipient_email],
            template_name='emails/evaluation_published.html',
            context=context,
            attachment_path=pdf_path,
            sync=sync
        )

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

    @classmethod
    def send_course_assigned_to_teacher_notification(
        cls,
        teacher_user,
        course_code: str,
        course_title: str,
        department_name: Optional[str] = None,
        sync: bool = False,
    ):
        """Sends notification to a teacher when assigned as an instructor/examiner for a course."""
        recipient = getattr(teacher_user, 'email', None) or getattr(teacher_user, 'username', None)
        if not recipient or '@' not in recipient:
            return None

        teacher_name = teacher_user.get_full_name() or teacher_user.username
        subject = f"[Course Assigned] You are assigned as Instructor for {course_code} - {course_title}"
        context = {
            'teacher_name': teacher_name,
            'course_code': course_code,
            'course_title': course_title,
            'department_name': department_name or '',
            'workspace_url': f"{cls._get_base_url()}/teacher/login/",
        }
        return cls._send_async_email(subject, [recipient], 'emails/course_assigned_teacher.html', context, sync=sync)

    @classmethod
    def send_exam_assigned_to_teacher_notification(
        cls,
        teacher_user,
        exam_title: str,
        course_code: str,
        course_title: str,
        exam_date: str,
        total_marks: str = "100",
        exam_id: Optional[int] = None,
        sync: bool = False,
    ):
        """Sends notification to a teacher when assigned as the examiner for an examination with direct link to Setup Paper & Rubrics."""
        recipient = getattr(teacher_user, 'email', None) or getattr(teacher_user, 'username', None)
        if not recipient or '@' not in recipient:
            return None

        base_url = cls._get_base_url()
        teacher_name = teacher_user.get_full_name() or teacher_user.username
        subject = f"[Examiner Assigned] {course_code} - {exam_title}"

        rubric_url = f"{base_url}/teacher/exam/{exam_id}/questions-rubric/" if exam_id else f"{base_url}/teacher/questions-rubric/"

        context = {
            'teacher_name': teacher_name,
            'exam_id': exam_id,
            'exam_title': exam_title,
            'course_code': course_code,
            'course_title': course_title,
            'exam_date': str(exam_date),
            'total_marks': str(total_marks),
            'rubric_url': rubric_url,
            'workspace_url': rubric_url,
        }
        return cls._send_async_email(subject, [recipient], 'emails/exam_assigned_teacher.html', context, sync=sync)

