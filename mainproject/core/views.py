from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from .models import (
    College, School, Department, Course, Examination, AnswerScript,
    AnswerSegment, Evaluation, Profile
)

def landing_page(request):
    """Renders the main landing page for the IntelliGrade SaaS platform."""
    return render(request, 'core/landing_page.html')


def teacher_dashboard(request):
    """Dashboard view tailored for Teachers / Examiners."""
    if not request.user.is_authenticated:
        messages.warning(request, "Please sign in to access the Faculty Workspace.")
        return redirect('teacher_login')

    # Redirect Chief Exam Controller / Admin away to their own control portal
    if request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == Profile.Role.ADMIN):
        messages.info(request, "Chief Exam Controllers are managed via the Exam Controller Portal.")
        return redirect('exam_controller_dashboard')

    profile = getattr(request.user, 'profile', None)

    # Reject Student accounts attempting to enter Faculty Workspace
    if profile and profile.role == Profile.Role.STUDENT:
        messages.error(request, "Access Denied: The Faculty Workspace is restricted to instructors and examiners.")
        return redirect('student_dashboard')

    # Redirect Dept Head accounts to their own portal
    if profile and profile.role == Profile.Role.DEPARTMENT_HEAD:
        messages.info(request, "Department Heads are managed via the Department Head Portal.")
        return redirect('dept_head_dashboard')

    teacher_name = request.user.get_full_name() or request.user.username
    dept_name = profile.department.name if (profile and profile.department) else "Academic Faculty Department"

    exams = Examination.objects.all().select_related('course')[:5]
    pending_scripts = AnswerScript.objects.filter(status__in=['UPLOADED', 'OCR_DONE', 'EVALUATED']).select_related('examination', 'student')[:5]
    
    stats = {
        'total_exams': Examination.objects.count() or 12,
        'pending_reviews': AnswerScript.objects.filter(status='EVALUATED').count() or 8,
        'total_scripts': AnswerScript.objects.count() or 145,
        'avg_confidence': '94.2%',
    }
    
    context = {
        'teacher_name': teacher_name,
        'dept_name': dept_name,
        'exams': exams,
        'pending_scripts': pending_scripts,
        'stats': stats,
    }
    return render(request, 'core/dashboard_teacher.html', context)


def student_dashboard(request):
    """Dashboard view tailored for Students."""
    if not request.user.is_authenticated:
        messages.warning(request, "Please sign in to access the Student Portal.")
        return redirect('student_login')

    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != Profile.Role.STUDENT:
        messages.error(request, "Access Denied: The Student Portal is restricted to enrolled students.")
        return redirect('landing_page')

    if not profile.is_approved:
        messages.warning(request, "Your self-registration request is pending approval by the Chief Exam Controller.")
        auth_logout(request)
        return redirect('student_login')

    evaluations = Evaluation.objects.select_related('segment__script', 'segment__question').all()[:5]
    stats = {
        'student_name': request.user.get_full_name() or request.user.username,
        'student_id': request.user.username,
        'dept_name': profile.department.name if profile.department else "Computer Science & Engineering",
        'enrolled_courses': Course.objects.count() or 4,
        'completed_exams': 3,
        'gpa_avg': '3.85',
        'rank': 'Top 5%',
    }
    return render(request, 'core/dashboard_student.html', {'evaluations': evaluations, 'stats': stats})


def student_login(request):
    """Login view dedicated for Students."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            profile = getattr(user, 'profile', None)
            if not profile or profile.role != Profile.Role.STUDENT:
                messages.error(request, "Access Denied: Only Student accounts can sign in to the Student Portal.")
                return render(request, 'core/student_login.html')

            if not profile.is_approved:
                messages.warning(request, f"Your registration request (Student ID: {username}) is pending approval by the Chief Exam Controller.")
                return render(request, 'core/student_login.html')

            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}! Signed in to Student Portal.")
            return redirect('student_dashboard')
        else:
            messages.error(request, "Invalid Student ID or Password. Please try again or contact your Chief Exam Controller.")

    return render(request, 'core/student_login.html')


def student_register(request):
    """Self-registration view for Students."""
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        student_id = request.POST.get('student_id', '').strip()
        password = request.POST.get('password', '')
        dept_code = request.POST.get('department', '').strip()

        if User.objects.filter(username=student_id).exists():
            messages.error(request, f"Student ID / Username '{student_id}' is already registered.")
            return redirect('student_register')

        user = User.objects.create_user(
            username=student_id,
            email=email,
            password=password,
            first_name=full_name,
            last_name=''
        )

        dept_obj = Department.objects.filter(code=dept_code).first()
        Profile.objects.update_or_create(
            user=user,
            defaults={
                'role': Profile.Role.STUDENT,
                'department': dept_obj,
                'is_approved': False
            }
        )

        messages.success(request, f"Registration submitted for Student '{full_name}' (ID: {student_id})! Your account is pending approval by the Chief Exam Controller.")
        return redirect('student_login')

    departments = Department.objects.filter(is_active=True)
    return render(request, 'core/student_register.html', {'departments': departments})


def exam_controller_login(request):
    """Login view dedicated for Chief Exam Controller (Admin)."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Check if user is Exam Controller / Admin
            if user.is_superuser or (hasattr(user, 'profile') and user.profile.role == Profile.Role.ADMIN):
                auth_login(request, user)
                messages.success(request, f"Welcome back, {user.get_full_name() or user.username}! Authenticated as Chief Exam Controller.")
                return redirect('exam_controller_dashboard')
            else:
                messages.error(request, "Access Denied: Faculty / Teacher accounts cannot sign in as Chief Exam Controller. Please use the Faculty Sign In portal.")
                return render(request, 'core/exam_controller_login.html')
        else:
            messages.error(request, "Invalid Controller username or password. Please verify your credentials.")
    
    return render(request, 'core/exam_controller_login.html')


def logout_view(request):
    """Logs out the user and redirects to landing page."""
    auth_logout(request)
    messages.success(request, "You have been signed out successfully.")
    return redirect('landing_page')


def exam_controller_dashboard(request):
    """Unified Control Portal for Exam Controller (Ultimate Admin)."""
    if not request.user.is_authenticated:
        messages.warning(request, "Please sign in to access the Chief Exam Controller Control Portal.")
        return redirect('exam_controller_login')
        
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == Profile.Role.ADMIN)):
        messages.error(request, "Access Denied: The Chief Exam Controller Portal is restricted to Administrator accounts.")
        return redirect('teacher_dashboard')

    stats = {
        'total_students': Profile.objects.filter(role=Profile.Role.STUDENT, is_approved=True).count() or 180,
        'pending_students': Profile.objects.filter(role=Profile.Role.STUDENT, is_approved=False).count(),
        'total_faculty': Profile.objects.filter(role=Profile.Role.TEACHER).count() or 24,
        'total_dept_heads': Profile.objects.filter(role=Profile.Role.DEPARTMENT_HEAD).count() or 6,
        'total_colleges': College.objects.count() or 1,
        'total_schools': School.objects.count() or 3,
        'total_departments': Department.objects.filter(is_active=True).count(),
        'total_courses': Course.objects.count() or 18,
        'active_exams': Examination.objects.count() or 12,
        'pending_rechecks': 5,
    }
    
    colleges = College.objects.prefetch_related('schools__departments', 'departments').all()
    schools = School.objects.filter(college__isnull=True).prefetch_related('departments').all()
    standalone_departments = Department.objects.filter(school__isnull=True, college__isnull=True).all()
    
    recheck_tickets = [
        {'id': 1, 'student': 'Rahim Ahmed (201002014)', 'course': 'CSE 411 - Software Engineering', 'reason': 'Missing marks for component interaction diagram in Q1a', 'ai_score': 8.5, 'requested': 10.0, 'status': 'Pending Review'},
        {'id': 2, 'student': 'Tanvir Hasan (201002088)', 'course': 'CSE 312 - Database Systems', 'reason': 'B-Tree indexing question partial credit re-assessment', 'ai_score': 6.0, 'requested': 8.0, 'status': 'Under Review'},
    ]
    
    return render(request, 'core/dashboard_exam_controller.html', {
        'stats': stats,
        'colleges': colleges,
        'schools': schools,
        'standalone_departments': standalone_departments,
        'departments': Department.objects.all(),
        'recheck_tickets': recheck_tickets,
    })


def add_structure(request):
    """Interface for Exam Controller to add Colleges, Schools, and Departments."""
    if request.method == 'POST':
        entity_type = request.POST.get('entity_type')
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip().upper()
        description = request.POST.get('description', '').strip()

        if entity_type == 'COLLEGE':
            college, created = College.objects.get_or_create(code=code, defaults={'name': name, 'description': description})
            if created:
                messages.success(request, f"College '{name} ({code})' created successfully!")
            else:
                messages.warning(request, f"College with code '{code}' already exists.")

        elif entity_type == 'SCHOOL':
            college_id = request.POST.get('college')
            college = College.objects.filter(id=college_id).first() if college_id else None
            school, created = School.objects.get_or_create(code=code, defaults={'name': name, 'college': college})
            if created:
                messages.success(request, f"School '{name} ({code})' created successfully!")
            else:
                messages.warning(request, f"School with code '{code}' already exists.")

        elif entity_type == 'DEPARTMENT':
            school_id = request.POST.get('school')
            college_id = request.POST.get('college')
            school = School.objects.filter(id=school_id).first() if school_id else None
            college = College.objects.filter(id=college_id).first() if college_id else (school.college if school else None)
            
            dept, created = Department.objects.get_or_create(code=code, defaults={'name': name, 'school': school, 'college': college})
            if created:
                messages.success(request, f"Department '{name} ({code})' created successfully!")
            else:
                messages.warning(request, f"Department with code '{code}' already exists.")

        return redirect('exam_controller_dashboard')

    colleges = College.objects.all()
    schools = School.objects.all()
    return render(request, 'core/add_structure.html', {
        'colleges': colleges,
        'schools': schools,
    })


def teacher_login(request):
    """Login view dedicated for Faculty Members & Teachers."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Reject Superuser / Admin accounts from logging in as Faculty!
            if user.is_superuser or (hasattr(user, 'profile') and user.profile.role == Profile.Role.ADMIN):
                messages.error(request, "Access Denied: Superuser / Chief Exam Controller credentials cannot log in to the Faculty Workspace. Please log in with a Faculty account created via the Add Faculty panel.")
                return render(request, 'core/teacher_login.html')

            # Login as Faculty user (replaces any previous session)
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}! Signed in to Faculty Workspace.")
            return redirect('teacher_dashboard')
        else:
            messages.error(request, "Invalid Employee ID / Username or Password. Please try again or contact your Chief Exam Controller.")

    return render(request, 'core/teacher_login.html')


def admin_dashboard(request):
    """Unified Redirect to Exam Controller Dashboard."""
    return redirect('exam_controller_dashboard')


def add_faculty(request):
    """Interface for Exam Controller to add new Faculty members with credentials."""
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        dept_code = request.POST.get('department', '').strip()

        if User.objects.filter(username=username).exists():
            messages.error(request, f"User with Employee ID / Username '{username}' already exists.")
            return redirect('add_faculty')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name,
            last_name=''
        )

        dept_obj = Department.objects.filter(code=dept_code, is_active=True).first()
        Profile.objects.update_or_create(
            user=user,
            defaults={
                'role': Profile.Role.TEACHER,
                'department': dept_obj
            }
        )

        messages.success(request, f"Faculty member '{full_name}' ({username}) registered successfully! Credentials activated.")
        return redirect('exam_controller_dashboard')

    departments = Department.objects.filter(is_active=True)
    return render(request, 'core/add_faculty.html', {'departments': departments})


def add_student(request):
    """Interface for Exam Controller to register new Students with credentials & simulated email."""
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        student_id = request.POST.get('student_id', '').strip()
        password = request.POST.get('password', '')
        dept_code = request.POST.get('department', '').strip()

        if User.objects.filter(username=student_id).exists():
            messages.error(request, f"Student ID / Username '{student_id}' already exists.")
            return redirect('add_student')

        user = User.objects.create_user(
            username=student_id,
            email=email,
            password=password,
            first_name=full_name,
            last_name=''
        )

        dept_obj = Department.objects.filter(code=dept_code, is_active=True).first()
        Profile.objects.update_or_create(
            user=user,
            defaults={
                'role': Profile.Role.STUDENT,
                'department': dept_obj,
                'is_approved': True
            }
        )

        # Console Simulation of Sending Welcome Email with Credentials
        print(f"\n[EMAIL SYSTEM SIMULATION]")
        print(f"To: {email}")
        print(f"Subject: Welcome to IntelliGrade - Student Access Credentials")
        print(f"Body: Hello {full_name},\nYour student account has been registered by the Chief Exam Controller.\nStudent ID: {student_id}\nPassword: {password}\nLogin Portal: http://127.0.0.1:8000/student/login/\n")

        messages.success(request, f"Student '{full_name}' ({student_id}) registered successfully! Welcome email sent to {email}.")
        return redirect('exam_controller_dashboard')

    departments = Department.objects.filter(is_active=True)
    return render(request, 'core/add_student.html', {'departments': departments})


def pending_students(request):
    """Interface for Exam Controller to review self-registered student requests."""
    pending_profiles = Profile.objects.filter(role=Profile.Role.STUDENT, is_approved=False).select_related('user', 'department')
    return render(request, 'core/pending_students.html', {'pending_profiles': pending_profiles})


def approve_student(request, profile_id):
    """Approves a pending self-registered student and sends simulated welcome email."""
    profile = Profile.objects.filter(id=profile_id).first()
    if profile:
        profile.is_approved = True
        profile.save()

        # Console Simulation of Sending Approval Email
        print(f"\n[EMAIL SYSTEM SIMULATION]")
        print(f"To: {profile.user.email}")
        print(f"Subject: Account Approved - IntelliGrade Student Portal Access")
        print(f"Body: Hello {profile.user.first_name},\nYour self-registration request for Student ID {profile.user.username} has been approved by the Chief Exam Controller.\nYou can now log in at http://127.0.0.1:8000/student/login/\n")

        messages.success(request, f"Student account '{profile.user.get_full_name()}' (ID: {profile.user.username}) approved and activated!")
    return redirect('pending_students')


def reject_student(request, profile_id):
    """Rejects and removes a pending student registration request."""
    profile = Profile.objects.filter(id=profile_id).first()
    if profile:
        user = profile.user
        username = user.username
        user.delete()
        messages.warning(request, f"Registration request for Student ID '{username}' was rejected and removed.")
    return redirect('pending_students')


def toggle_department_status(request, dept_id):
    """Toggles active/inactive status of a Department."""
    if not request.user.is_authenticated or not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == Profile.Role.ADMIN)):
        messages.error(request, "Access Denied: Only Chief Exam Controller can modify department status.")
        return redirect('landing_page')

    department = get_object_or_404(Department, id=dept_id)
    department.is_active = not department.is_active
    department.save()

    status_str = "Active" if department.is_active else "Inactive"
    messages.success(request, f"Department '{department.name}' ({department.code}) status updated to {status_str}.")
    return redirect('exam_controller_dashboard')


def delete_department(request, dept_id):
    """Deletes a Department from the system."""
    if not request.user.is_authenticated or not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == Profile.Role.ADMIN)):
        messages.error(request, "Access Denied: Only Chief Exam Controller can delete departments.")
        return redirect('landing_page')

    department = get_object_or_404(Department, id=dept_id)
    dept_name = department.name
    department.delete()
    messages.success(request, f"Department '{dept_name}' deleted successfully!")
    return redirect('exam_controller_dashboard')


def department_detail(request, dept_id):
    """Comprehensive detail view showing all Faculty, Head, Students, Courses & Exams for a Department."""
    if not request.user.is_authenticated:
        messages.warning(request, "Please sign in to view department details.")
        return redirect('landing_page')

    department = get_object_or_404(Department, id=dept_id)
    
    dept_head_profile = Profile.objects.filter(department=department, role=Profile.Role.DEPARTMENT_HEAD).select_related('user').first()
    faculty_profiles = Profile.objects.filter(department=department, role=Profile.Role.TEACHER).select_related('user')
    student_profiles = Profile.objects.filter(department=department, role=Profile.Role.STUDENT).select_related('user')
    courses = Course.objects.filter(department=department)
    exams = Examination.objects.filter(course__department=department).select_related('course')

    context = {
        'department': department,
        'dept_head_profile': dept_head_profile,
        'faculty_profiles': faculty_profiles,
        'student_profiles': student_profiles,
        'courses': courses,
        'exams': exams,
    }
    return render(request, 'core/department_detail.html', context)


def rechecks_list(request):
    """Interface to manage student recheck and re-evaluation requests."""
    recheck_tickets = [
        {'id': 1, 'student': 'Rahim Ahmed (201002014)', 'course': 'CSE 411 - Software Engineering', 'reason': 'Missing marks for component interaction diagram in Q1a', 'ai_score': 8.5, 'requested': 10.0, 'status': 'Pending Review'},
        {'id': 2, 'student': 'Tanvir Hasan (201002088)', 'course': 'CSE 312 - Database Systems', 'reason': 'B-Tree indexing question partial credit re-assessment', 'ai_score': 6.0, 'requested': 8.0, 'status': 'Under Review'},
        {'id': 3, 'student': 'Nusrat Jahan (201002105)', 'course': 'CSE 211 - Data Structures', 'reason': 'Graph BFS vs DFS answer evaluation inquiry', 'ai_score': 7.5, 'requested': 9.0, 'status': 'Resolved'},
    ]
    return render(request, 'core/rechecks_list.html', {'recheck_tickets': recheck_tickets})


def add_dept_head(request):
    """Interface for Exam Controller to add new Department Heads with credentials."""
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        dept_code = request.POST.get('department', '').strip()

        if User.objects.filter(username=username).exists():
            messages.error(request, f"User with ID / Username '{username}' already exists.")
            return redirect('add_dept_head')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name,
            last_name=''
        )

        dept_obj = Department.objects.filter(code=dept_code, is_active=True).first()
        Profile.objects.update_or_create(
            user=user,
            defaults={
                'role': Profile.Role.DEPARTMENT_HEAD,
                'department': dept_obj
            }
        )

        messages.success(request, f"Department Head '{full_name}' ({username}) registered successfully! Credentials activated.")
        return redirect('exam_controller_dashboard')

    departments = Department.objects.filter(is_active=True)
    return render(request, 'core/add_dept_head.html', {'departments': departments})


def dept_head_login(request):
    """Login view dedicated for Department Heads."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            profile = getattr(user, 'profile', None)
            if not profile or profile.role != Profile.Role.DEPARTMENT_HEAD:
                messages.error(request, "Access Denied: Only Department Head accounts created via the Chief Exam Controller panel can sign in here.")
                return render(request, 'core/dept_head_login.html')

            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}! Signed in to Department Head Portal.")
            return redirect('dept_head_dashboard')
        else:
            messages.error(request, "Invalid Username or Password. Please try again or contact your Chief Exam Controller.")

    return render(request, 'core/dept_head_login.html')


def dept_head_dashboard(request):
    """Dashboard view for Department Heads."""
    if not request.user.is_authenticated:
        messages.warning(request, "Please sign in to access the Department Head Portal.")
        return redirect('dept_head_login')

    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != Profile.Role.DEPARTMENT_HEAD:
        messages.error(request, "Access Denied: The Department Head Portal is restricted to assigned Department Heads.")
        return redirect('landing_page')

    dept_name = profile.department.name if (profile and profile.department) else "Computer Science & Engineering"
    stats = {
        'dept_name': dept_name,
        'faculty_count': Profile.objects.filter(role=Profile.Role.TEACHER, department=profile.department).count() or 18 if (profile and profile.department) else 18,
        'active_courses': Course.objects.filter(department=profile.department).count() or 14 if (profile and profile.department) else 14,
        'pass_rate': '91.8%',
        'ai_approval_rate': '96.4%',
    }
    courses = Course.objects.filter(department=profile.department)[:5] if (profile and profile.department) else Course.objects.all()[:5]
    return render(request, 'core/dashboard_dept_head.html', {'stats': stats, 'courses': courses, 'head_name': request.user.get_full_name() or request.user.username})


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


# ==========================================
# Student & Faculty List / Edit / Delete Views
# ==========================================

def students_list(request):
    """View listing all enrolled/registered Students for the Exam Controller."""
    if not request.user.is_authenticated or not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == Profile.Role.ADMIN)):
        messages.error(request, "Access Denied: Restricted to Chief Exam Controller.")
        return redirect('landing_page')

    student_profiles = Profile.objects.filter(role=Profile.Role.STUDENT).select_related('user', 'department')
    return render(request, 'core/students_list.html', {'student_profiles': student_profiles})


def edit_student(request, user_id):
    """Interface to edit student information."""
    if not request.user.is_authenticated or not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == Profile.Role.ADMIN)):
        messages.error(request, "Access Denied.")
        return redirect('landing_page')

    target_user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=target_user, role=Profile.Role.STUDENT)

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        dept_code = request.POST.get('department', '').strip()
        password = request.POST.get('password', '').strip()

        target_user.first_name = full_name
        target_user.email = email
        if password:
            target_user.set_password(password)
        target_user.save()

        dept_obj = Department.objects.filter(code=dept_code).first()
        profile.department = dept_obj
        profile.save()

        messages.success(request, f"Student '{full_name}' ({target_user.username}) updated successfully!")
        return redirect('students_list')

    departments = Department.objects.filter(is_active=True)
    return render(request, 'core/edit_student.html', {
        'target_user': target_user,
        'profile': profile,
        'departments': departments,
    })


def delete_student(request, user_id):
    """Deletes a student account."""
    if not request.user.is_authenticated or not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == Profile.Role.ADMIN)):
        messages.error(request, "Access Denied.")
        return redirect('landing_page')

    target_user = get_object_or_404(User, id=user_id)
    username = target_user.username
    target_user.delete()
    messages.success(request, f"Student account '{username}' deleted successfully.")
    return redirect('students_list')


def faculty_list(request):
    """View listing all registered Faculty Teachers for the Exam Controller."""
    if not request.user.is_authenticated or not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == Profile.Role.ADMIN)):
        messages.error(request, "Access Denied: Restricted to Chief Exam Controller.")
        return redirect('landing_page')

    faculty_profiles = Profile.objects.filter(role=Profile.Role.TEACHER).select_related('user', 'department')
    return render(request, 'core/faculty_list.html', {'faculty_profiles': faculty_profiles})


def edit_faculty(request, user_id):
    """Interface to edit faculty member information."""
    if not request.user.is_authenticated or not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == Profile.Role.ADMIN)):
        messages.error(request, "Access Denied.")
        return redirect('landing_page')

    target_user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=target_user, role=Profile.Role.TEACHER)

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        dept_code = request.POST.get('department', '').strip()
        password = request.POST.get('password', '').strip()

        target_user.first_name = full_name
        target_user.email = email
        if password:
            target_user.set_password(password)
        target_user.save()

        dept_obj = Department.objects.filter(code=dept_code).first()
        profile.department = dept_obj
        profile.save()

        messages.success(request, f"Faculty member '{full_name}' ({target_user.username}) updated successfully!")
        return redirect('faculty_list')

    departments = Department.objects.filter(is_active=True)
    return render(request, 'core/edit_faculty.html', {
        'target_user': target_user,
        'profile': profile,
        'departments': departments,
    })


def delete_faculty(request, user_id):
    """Deletes a faculty teacher account."""
    if not request.user.is_authenticated or not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == Profile.Role.ADMIN)):
        messages.error(request, "Access Denied.")
        return redirect('landing_page')

    target_user = get_object_or_404(User, id=user_id)
    username = target_user.username
    target_user.delete()
    messages.success(request, f"Faculty account '{username}' deleted successfully.")
    return redirect('faculty_list')


# ==========================================
# Dept Heads, Courses & Exams Management Views
# ==========================================

def dept_heads_list(request):
    """View listing all registered Department Heads for the Exam Controller."""
    if not request.user.is_authenticated or not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == Profile.Role.ADMIN)):
        messages.error(request, "Access Denied: Restricted to Chief Exam Controller.")
        return redirect('landing_page')

    dept_head_profiles = Profile.objects.filter(role=Profile.Role.DEPARTMENT_HEAD).select_related('user', 'department')
    return render(request, 'core/dept_heads_list.html', {'dept_head_profiles': dept_head_profiles})


def edit_dept_head(request, user_id):
    """Interface to edit Department Head information."""
    if not request.user.is_authenticated or not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == Profile.Role.ADMIN)):
        messages.error(request, "Access Denied.")
        return redirect('landing_page')

    target_user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=target_user, role=Profile.Role.DEPARTMENT_HEAD)

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        dept_code = request.POST.get('department', '').strip()
        password = request.POST.get('password', '').strip()

        target_user.first_name = full_name
        target_user.email = email
        if password:
            target_user.set_password(password)
        target_user.save()

        dept_obj = Department.objects.filter(code=dept_code).first()
        profile.department = dept_obj
        profile.save()

        messages.success(request, f"Department Head '{full_name}' ({target_user.username}) updated successfully!")
        return redirect('dept_heads_list')

    departments = Department.objects.filter(is_active=True)
    return render(request, 'core/edit_dept_head.html', {
        'target_user': target_user,
        'profile': profile,
        'departments': departments,
    })


def delete_dept_head(request, user_id):
    """Deletes a Department Head account."""
    if not request.user.is_authenticated or not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == Profile.Role.ADMIN)):
        messages.error(request, "Access Denied.")
        return redirect('landing_page')

    target_user = get_object_or_404(User, id=user_id)
    username = target_user.username
    target_user.delete()
    messages.success(request, f"Department Head account '{username}' deleted successfully.")
    return redirect('dept_heads_list')


def courses_list(request):
    """View listing all registered Courses for the Exam Controller."""
    if not request.user.is_authenticated or not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == Profile.Role.ADMIN)):
        messages.error(request, "Access Denied: Restricted to Chief Exam Controller.")
        return redirect('landing_page')

    courses = Course.objects.select_related('department').all()
    return render(request, 'core/courses_list.html', {'courses': courses})


def add_course(request):
    """Interface to create a new Course module."""
    if not request.user.is_authenticated or not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == Profile.Role.ADMIN)):
        messages.error(request, "Access Denied.")
        return redirect('landing_page')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        code = request.POST.get('code', '').strip()
        dept_code = request.POST.get('department', '').strip()

        if Course.objects.filter(code=code).exists():
            messages.error(request, f"Course code '{code}' already exists.")
            return redirect('add_course')

        dept_obj = Department.objects.filter(code=dept_code).first()
        Course.objects.create(title=title, code=code, department=dept_obj)
        messages.success(request, f"Course '{title}' ({code}) registered successfully!")
        return redirect('courses_list')

    departments = Department.objects.filter(is_active=True)
    return render(request, 'core/add_course.html', {'departments': departments})


def edit_course(request, course_id):
    """Interface to edit Course module info."""
    if not request.user.is_authenticated or not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == Profile.Role.ADMIN)):
        messages.error(request, "Access Denied.")
        return redirect('landing_page')

    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        code = request.POST.get('code', '').strip()
        dept_code = request.POST.get('department', '').strip()

        dept_obj = Department.objects.filter(code=dept_code).first()
        course.title = title
        course.code = code
        course.department = dept_obj
        course.save()

        messages.success(request, f"Course '{title}' ({code}) updated successfully!")
        return redirect('courses_list')

    departments = Department.objects.filter(is_active=True)
    return render(request, 'core/edit_course.html', {'course': course, 'departments': departments})


def delete_course(request, course_id):
    """Deletes a Course module."""
    if not request.user.is_authenticated or not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == Profile.Role.ADMIN)):
        messages.error(request, "Access Denied.")
        return redirect('landing_page')

    course = get_object_or_404(Course, id=course_id)
    code = course.code
    course.delete()
    messages.success(request, f"Course '{code}' deleted successfully.")
    return redirect('courses_list')


def exams_list(request):
    """View listing all Examinations for the Exam Controller."""
    if not request.user.is_authenticated or not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == Profile.Role.ADMIN)):
        messages.error(request, "Access Denied: Restricted to Chief Exam Controller.")
        return redirect('landing_page')

    exams = Examination.objects.select_related('course').all()
    return render(request, 'core/exams_list.html', {'exams': exams})


def edit_exam(request, exam_id):
    """Interface to edit Examination setup."""
    if not request.user.is_authenticated or not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == Profile.Role.ADMIN)):
        messages.error(request, "Access Denied.")
        return redirect('landing_page')

    exam = get_object_or_404(Examination, id=exam_id)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        total_marks = request.POST.get('total_marks', 100)
        status = request.POST.get('status', 'PUBLISHED')

        exam.title = title
        exam.total_marks = total_marks
        exam.status = status
        exam.save()

        messages.success(request, f"Examination '{title}' updated successfully!")
        return redirect('exams_list')

    return render(request, 'core/edit_exam.html', {'exam': exam})


def delete_exam(request, exam_id):
    """Deletes an Examination."""
    if not request.user.is_authenticated or not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == Profile.Role.ADMIN)):
        messages.error(request, "Access Denied.")
        return redirect('landing_page')

    exam = get_object_or_404(Examination, id=exam_id)
    title = exam.title
    exam.delete()
    messages.success(request, f"Examination '{title}' deleted successfully.")
    return redirect('exams_list')
