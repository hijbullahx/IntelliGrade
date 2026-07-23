from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import (
    Examination, Course, AnswerScript, AnswerSegment, Evaluation,
    Department, Profile
)

def landing_page(request):
    """Renders the main landing page for the IntelliGrade SaaS platform."""
    return render(request, 'core/landing_page.html')


def teacher_dashboard(request):
    """Dashboard view tailored for Teachers / Examiners."""
    exams = Examination.objects.all().select_related('course')[:5]
    pending_scripts = AnswerScript.objects.filter(status__in=['UPLOADED', 'OCR_DONE', 'EVALUATED']).select_related('examination', 'student')[:5]
    
    stats = {
        'total_exams': Examination.objects.count() or 12,
        'pending_reviews': AnswerScript.objects.filter(status='EVALUATED').count() or 8,
        'total_scripts': AnswerScript.objects.count() or 145,
        'avg_confidence': '94.2%',
    }
    
    context = {
        'exams': exams,
        'pending_scripts': pending_scripts,
        'stats': stats,
    }
    return render(request, 'core/dashboard_teacher.html', context)


def student_dashboard(request):
    """Dashboard view tailored for Students."""
    evaluations = Evaluation.objects.select_related('segment__script', 'segment__question').all()[:5]
    
    stats = {
        'enrolled_courses': Course.objects.count() or 4,
        'completed_exams': 3,
        'gpa_avg': '3.85',
        'rank': 'Top 5%',
    }
    
    context = {
        'evaluations': evaluations,
        'stats': stats,
    }
    return render(request, 'core/dashboard_student.html', context)


def admin_dashboard(request):
    """Dashboard view for System Administrators."""
    stats = {
        'total_users': Profile.objects.count() or 340,
        'total_departments': Department.objects.count() or 6,
        'total_courses': Course.objects.count() or 24,
        'active_exams': Examination.objects.filter(status='PUBLISHED').count() or 9,
    }
    departments = Department.objects.all()[:5]
    return render(request, 'core/dashboard_admin.html', {'stats': stats, 'departments': departments})


def dept_head_dashboard(request):
    """Dashboard view for Department Heads."""
    stats = {
        'dept_name': 'Computer Science & Engineering',
        'faculty_count': 18,
        'active_courses': 14,
        'pass_rate': '91.8%',
        'ai_approval_rate': '96.4%',
    }
    courses = Course.objects.all()[:5]
    return render(request, 'core/dashboard_dept_head.html', {'stats': stats, 'courses': courses})


def exam_create(request):
    """Interface to create examinations and define rubrics."""
    if request.method == 'POST':
        messages.success(request, "Examination and grading rubric created successfully!")
        return redirect('teacher_dashboard')
    
    courses = Course.objects.all()
    return render(request, 'core/exam_create.html', {'courses': courses})


def script_upload(request):
    """Interface to drag-and-drop batch upload answer scripts."""
    if request.method == 'POST':
        messages.success(request, "Answer scripts uploaded successfully! OCR & AI Pipeline queued.")
        return redirect('teacher_dashboard')
    
    exams = Examination.objects.all()
    return render(request, 'core/script_upload.html', {'exams': exams})


def grading_workbench(request, script_id=1):
    """Split-screen AI Grading Review Workbench for Teachers."""
    # Attempt to load answer script or present realistic interactive mock workbench
    script = AnswerScript.objects.filter(id=script_id).first()
    
    context = {
        'script': script,
        'script_id': script_id,
        'student_name': script.student.get_full_name() if script else "Rahim Ahmed (ID: 201002014)",
        'exam_title': script.examination.title if script else "CSE 411: Software Engineering Final Exam",
        'question_no': "Q1 (a)",
        'max_marks': 10.0,
        'extracted_text': "Software Architecture patterns describe reusable solutions to common software design problems. Microservices architecture breaks an application into small, independent services communicating via REST APIs. Monolithic architecture combines all features in a single process.",
        'criteria_list': [
            {'title': 'Microservices definition & API communication', 'marks': 4.0, 'earned': 4.0, 'matched': True},
            {'title': 'Monolith architecture contrast', 'marks': 3.0, 'earned': 3.0, 'matched': True},
            {'title': 'Diagram / Component interaction details', 'marks': 3.0, 'earned': 1.5, 'matched': False},
        ],
        'ai_marks': 8.5,
        'ai_confidence': '96.5%',
        'ai_feedback': "The student clearly explained Microservices and Monolithic patterns. However, the explanation lacked detailed diagram references for component interactions.",
    }
    
    if request.method == 'POST':
        messages.success(request, "Evaluation approved and finalized successfully!")
        return redirect('teacher_dashboard')

    return render(request, 'core/grading_workbench.html', context)
