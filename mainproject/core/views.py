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

    # Fetch examinations assigned to this specific faculty examiner
    assigned_exams = Examination.objects.filter(assigned_faculty=request.user).select_related('course')
    if not assigned_exams.exists():
        assigned_exams = Examination.objects.all().select_related('course')[:5]

    pending_scripts = AnswerScript.objects.filter(status__in=['UPLOADED', 'OCR_DONE', 'EVALUATED']).select_related('examination', 'student')[:5]
    
    stats = {
        'total_exams': assigned_exams.count() if hasattr(assigned_exams, 'count') else len(assigned_exams),
        'pending_reviews': AnswerScript.objects.filter(status='EVALUATED').count(),
        'total_scripts': AnswerScript.objects.count(),
        'avg_confidence': '94.2%',
    }
    
    context = {
        'teacher_name': teacher_name,
        'dept_name': dept_name,
        'exams': assigned_exams,
        'assigned_exams': assigned_exams,
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
        'dept_name': profile.department.name if profile.department else "Academic Faculty Department",
        'enrolled_courses': Course.objects.filter(department=profile.department).count() if profile.department else Course.objects.count(),
        'completed_exams': 0,
        'gpa_avg': 'N/A',
        'rank': 'Enrolled',
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
        'total_students': Profile.objects.filter(role=Profile.Role.STUDENT, is_approved=True).count(),
        'pending_students': Profile.objects.filter(role=Profile.Role.STUDENT, is_approved=False).count(),
        'total_faculty': Profile.objects.filter(role=Profile.Role.TEACHER).count(),
        'total_dept_heads': Profile.objects.filter(role=Profile.Role.DEPARTMENT_HEAD).count(),
        'total_colleges': College.objects.count(),
        'total_schools': School.objects.count(),
        'total_departments': Department.objects.filter(is_active=True).count(),
        'total_courses': Course.objects.count(),
        'active_exams': Examination.objects.count(),
        'pending_rechecks': 0,
    }
    
    colleges = College.objects.prefetch_related('schools__departments', 'departments').all()
    schools = School.objects.filter(college__isnull=True).prefetch_related('departments').all()
    standalone_departments = Department.objects.filter(school__isnull=True, college__isnull=True).all()
    
    recheck_tickets = [
        {'id': 1, 'student': 'Rahim Ahmed (201002014)', 'course': 'CSE 411 - Software Engineering', 'reason': 'Missing marks for component interaction diagram in Q1a', 'ai_score': 8.5, 'requested': 10.0, 'status': 'Pending Review'},
        {'id': 2, 'student': 'Tanvir Hasan (201002088)', 'course': 'CSE 312 - Database Systems', 'reason': 'B-Tree indexing question partial credit re-assessment', 'ai_score': 6.0, 'requested': 8.0, 'status': 'Under Review'},
    ]
    
    from core.models import AIConfiguration
    ai_config = AIConfiguration.get_config()

    return render(request, 'core/dashboard_exam_controller.html', {
        'stats': stats,
        'colleges': colleges,
        'schools': schools,
        'standalone_departments': standalone_departments,
        'departments': Department.objects.all(),
        'recheck_tickets': recheck_tickets,
        'ai_config': ai_config,
    })


def ai_config_view(request):
    """View to update AI Engine Configuration Settings from Chief Exam Controller Dashboard."""
    if not request.user.is_authenticated or not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == Profile.Role.ADMIN)):
        messages.error(request, "Access Denied: Restricted to Chief Exam Controller.")
        return redirect('landing_page')

    from core.ai_engine.config.manager import AIConfigManager
    config = AIConfigManager.get_settings()

    if request.method == 'POST':
        provider = request.POST.get('provider', 'GEMINI')
        selected_model = request.POST.get('model_version', '').strip()
        ocr_engine = request.POST.get('ocr_engine', 'AUTO')
        preprocess_image = request.POST.get('preprocess_image') == 'on'
        enable_rag_learning = request.POST.get('enable_rag_learning') == 'on'
        prompt_template = request.POST.get('prompt_template', '').strip()

        gemini_model = config.gemini_model_name
        openai_model = config.openai_model_name

        if provider == 'GEMINI' and selected_model:
            gemini_model = selected_model
        elif provider == 'OPENAI' and selected_model:
            openai_model = selected_model

        AIConfigManager.update_settings(
            provider=provider,
            gemini_model=gemini_model,
            openai_model=openai_model,
            ocr_engine=ocr_engine,
            preprocess=preprocess_image,
            enable_rag=enable_rag_learning,
            prompt_template=prompt_template
        )

        messages.success(request, f"AI Engine Settings updated! Active Provider: {provider} ({selected_model or 'Default'}).")
        return redirect('exam_controller_dashboard')

    return redirect('exam_controller_dashboard')


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


def toggle_user_status(request, user_id):
    """Toggles active/blocked status for a User account (Student, Faculty, or Dept Head)."""
    if not request.user.is_authenticated or not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == Profile.Role.ADMIN)):
        messages.error(request, "Access Denied: Restricted to Chief Exam Controller.")
        return redirect('landing_page')

    target_user = get_object_or_404(User, id=user_id)
    target_user.is_active = not target_user.is_active
    target_user.save()

    profile = getattr(target_user, 'profile', None)
    if profile and profile.role == Profile.Role.STUDENT:
        profile.is_approved = target_user.is_active
        profile.save()

    status_str = "Active / Approved" if target_user.is_active else "Blocked / Deactivated"
    messages.success(request, f"User account '{target_user.get_full_name() or target_user.username}' status updated to {status_str}.")

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('exam_controller_dashboard')


def toggle_exam_status(request, exam_id):
    """Toggles status of an Examination between PUBLISHED (Active) and DRAFT (Frozen)."""
    if not request.user.is_authenticated or not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == Profile.Role.ADMIN)):
        messages.error(request, "Access Denied: Restricted to Chief Exam Controller.")
        return redirect('landing_page')

    exam = get_object_or_404(Examination, id=exam_id)
    if exam.status == Examination.Status.PUBLISHED:
        exam.status = Examination.Status.DRAFT
    else:
        exam.status = Examination.Status.PUBLISHED
    exam.save()

    messages.success(request, f"Examination '{exam.title}' status updated to {exam.status}.")

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('exams_list')


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


def add_faculty(request):
    """Interface for Exam Controller to add new Faculty Member / Examiner with credentials."""
    if not request.user.is_authenticated or not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == Profile.Role.ADMIN)):
        messages.error(request, "Access Denied: Restricted to Chief Exam Controller.")
        return redirect('landing_page')

    preset_name = request.GET.get('name', '').strip()
    next_url = request.GET.get('next', '').strip()

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        dept_code = request.POST.get('department', '').strip()
        redirect_after = request.POST.get('next', '').strip()

        if User.objects.filter(username=username).exists():
            messages.error(request, f"User with ID / Username '{username}' already exists.")
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

        messages.success(request, f"Faculty Examiner '{full_name}' ({username}) registered successfully! Credentials activated.")
        if redirect_after:
            return redirect(redirect_after)
        return redirect('faculty_list')

    departments = Department.objects.filter(is_active=True)
    suggested_username = preset_name.lower().replace('dr.', '').replace('prof.', '').replace(' ', '_').strip('_') if preset_name else ''

    return render(request, 'core/add_faculty.html', {
        'departments': departments,
        'preset_name': preset_name,
        'suggested_username': suggested_username,
        'next_url': next_url,
    })


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

    dept_name = profile.department.name if (profile and profile.department) else "Academic Faculty Department"
    stats = {
        'dept_name': dept_name,
        'faculty_count': Profile.objects.filter(role=Profile.Role.TEACHER, department=profile.department).count() if (profile and profile.department) else 0,
        'active_courses': Course.objects.filter(department=profile.department).count() if (profile and profile.department) else 0,
        'pass_rate': 'N/A',
        'ai_approval_rate': 'N/A',
    }
    courses = Course.objects.filter(department=profile.department)[:5] if (profile and profile.department) else Course.objects.all()[:5]
    return render(request, 'core/dashboard_dept_head.html', {'stats': stats, 'courses': courses, 'head_name': request.user.get_full_name() or request.user.username})


import base64
import json
import os
import re
import urllib.request
import urllib.error
from django.http import JsonResponse

def call_gemini_vision_api(api_key, text_content, file_obj=None):
    """Calls Google Gemini API (gemini-1.5-flash) to extract structured JSON routine details using standard library urllib."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt_text = """
    You are an expert AI exam routine scanner. Extract official exam routine details from the provided text or document/image.
    Return ONLY a raw JSON object (without markdown code blocks, backticks, or extra commentary) with these exact keys:
    {
      "course_code": "e.g. CSE 411",
      "course_title": "e.g. Software Engineering",
      "faculty_name": "e.g. Dr. Alan Turing",
      "exam_date": "YYYY-MM-DD",
      "total_marks": 100.0
    }
    If any field is missing or uncertain, set its value to null.
    """
    
    parts = []
    if text_content:
        parts.append({"text": f"{prompt_text}\n\nExam Routine Content:\n{text_content}"})
    else:
        parts.append({"text": prompt_text})
        
    if file_obj:
        try:
            file_bytes = file_obj.read()
            b64_data = base64.b64encode(file_bytes).decode('utf-8')
            mime_type = getattr(file_obj, 'content_type', 'image/jpeg')
            if not mime_type or mime_type == 'application/octet-stream':
                filename = getattr(file_obj, 'name', '').lower()
                if filename.endswith('.pdf'):
                    mime_type = 'application/pdf'
                elif filename.endswith('.png'):
                    mime_type = 'image/png'
                else:
                    mime_type = 'image/jpeg'

            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": b64_data
                }
            })
        except Exception:
            pass

    payload = {"contents": [{"parts": parts}]}
    json_data = json.dumps(payload).encode('utf-8')

    req = urllib.request.Request(
        url,
        data=json_data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            res_bytes = response.read()
            res_data = json.loads(res_bytes.decode('utf-8'))
            raw_output = res_data['candidates'][0]['content']['parts'][0]['text']
            raw_output = re.sub(r'```json\s*', '', raw_output)
            raw_output = re.sub(r'```\s*', '', raw_output).strip()
            return json.loads(raw_output)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8', errors='ignore')
        raise Exception(f"Gemini API HTTP {e.code}: {error_body}")
    except Exception as e:
        raise Exception(f"Gemini Request Failed: {str(e)}")


from django.conf import settings

from core.ai_engine.providers.factory import AIProviderFactory
from core.ai_engine.ocr.engine import OCREngineManager

def scan_routine_ai(request):
    """AI Routine Auto-Reader: Scans uploaded/pasted exam routine text/file using active AI Provider (Gemini/OpenAI/Mock) and matches DB."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required.'}, status=401)

    if request.method == 'POST':
        routine_text = request.POST.get('routine_text', '').strip()
        routine_file = request.FILES.get('routine_file')
        image_bytes = None
        mime_type = 'image/jpeg'
        file_name = ''

        if routine_file:
            try:
                image_bytes = routine_file.read()
                file_name = routine_file.name
                fn_lower = file_name.lower()
                if fn_lower.endswith('.png'):
                    mime_type = 'image/png'
                elif fn_lower.endswith('.pdf'):
                    mime_type = 'application/pdf'
                elif fn_lower.endswith('.webp'):
                    mime_type = 'image/webp'
                else:
                    mime_type = 'image/jpeg'

                # Attempt local OCR text extraction as helper text
                ocr_result = OCREngineManager().extract_text(image_bytes)
                if ocr_result and ocr_result.get('text'):
                    routine_text = ocr_result.get('text')
            except Exception:
                pass

        provider = AIProviderFactory.get_provider()
        ai_used = True
        ai_error = None
        extracted_schedule = []

        try:
            # Delegate multimodal image & text scanning to active LLM Provider
            if hasattr(provider, 'analyze_question_paper'):
                try:
                    ai_result = provider.analyze_question_paper(routine_text, image_bytes=image_bytes, mime_type=mime_type)
                except TypeError:
                    ai_result = provider.analyze_question_paper(routine_text or "Exam Routine Document")
            else:
                ai_result = {}

            if isinstance(ai_result, dict):
                extracted_schedule = ai_result.get('routine_schedule', [])
                if not extracted_schedule and ai_result.get('course_code'):
                    extracted_schedule = [ai_result]
        except Exception as e:
            ai_error = str(e)

        # Fallback raw text representation
        display_raw_text = routine_text
        if not display_raw_text and file_name:
            display_raw_text = f"📷 Uploaded Image/Document File: {file_name}\n(Direct Google Gemini Multimodal Vision Scan Applied)"

        # Fallback local pattern extraction if no structured list returned
        if not extracted_schedule:
            course_match = re.search(r'([A-Z]{2,4}\s*\d{3,4})', routine_text, re.IGNORECASE)
            date_match = re.search(r'(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})', routine_text)
            faculty_match = re.search(r'(?:Faculty|Teacher|Examiner|Instructor)[:\s]+([A-Za-z\.\s]+)', routine_text, re.IGNORECASE)
            
            extracted_schedule = [{
                'course_code': course_match.group(1).upper().strip() if course_match else None,
                'course_title': None,
                'faculty_name': faculty_match.group(1).strip() if faculty_match else None,
                'exam_date': date_match.group(1) if date_match else None,
                'exam_time': "10:00 AM - 01:00 PM",
                'total_marks': 100.0
            }]

        # Process & DB Match Each Extracted Routine Item
        routine_items = []
        all_teachers = list(Profile.objects.filter(role=Profile.Role.TEACHER).select_related('user'))

        for item in extracted_schedule:
            c_code = item.get('course_code')
            c_title = item.get('course_title')
            f_name = item.get('faculty_name')
            e_date = item.get('exam_date')
            e_time = item.get('exam_time', '10:00 AM - 01:00 PM')
            t_marks = item.get('total_marks', 100.0)

            # Match Course
            course_obj = None
            if c_code:
                course_obj = Course.objects.filter(code__iexact=c_code).first()
            if not course_obj and c_title:
                course_obj = Course.objects.filter(title__icontains=c_title).first()
            if not course_obj and routine_text:
                for c in Course.objects.all():
                    if c.code.lower() in routine_text.lower():
                        course_obj = c
                        c_code = c.code
                        break

            # Match Faculty
            faculty_user = None
            if f_name:
                for prof in all_teachers:
                    full_n = prof.user.get_full_name() or prof.user.username
                    if f_name.lower() in full_n.lower() or prof.user.username.lower() in f_name.lower():
                        faculty_user = prof.user
                        break

            routine_items.append({
                'course_code': c_code or (course_obj.code if course_obj else 'Unknown Course'),
                'course_title': course_obj.title if course_obj else (c_title or ''),
                'faculty_name': f_name or (faculty_user.get_full_name() if faculty_user else 'Unassigned'),
                'exam_date': e_date,
                'exam_time': e_time,
                'total_marks': t_marks,
                'course_found': bool(course_obj),
                'course_id': course_obj.id if course_obj else None,
                'faculty_found': bool(faculty_user),
                'faculty_id': faculty_user.id if faculty_user else None,
            })

        first_item = routine_items[0] if routine_items else {}

        return JsonResponse({
            'success': True,
            'raw_extracted_text': display_raw_text or "Exam Routine Document Scanned",
            'routine_items': routine_items,
            'gemini_used': ai_used,
            'ai_error': ai_error,
            'provider_name': provider.__class__.__name__,
            'detected_course_code': first_item.get('course_code'),
            'course_found': first_item.get('course_found', False),
            'course_id': first_item.get('course_id'),
            'course_title': first_item.get('course_title'),
            'detected_date': first_item.get('exam_date'),
            'detected_faculty_name': first_item.get('faculty_name'),
            'faculty_found': first_item.get('faculty_found', False),
            'faculty_id': first_item.get('faculty_id'),
            'total_marks': first_item.get('total_marks', 100.0),
        })


def exam_create(request):
    """Interface to create examinations and assign faculty examiners."""
    if not request.user.is_authenticated:
        messages.warning(request, "Please sign in to create examinations.")
        return redirect('landing_page')

    if request.method == 'POST':
        course_id = request.POST.get('course')
        assigned_faculty_id = request.POST.get('assigned_faculty')
        title = request.POST.get('title', '').strip()
        exam_date = request.POST.get('exam_date')
        total_marks = request.POST.get('total_marks', 100.00)

        if not course_id:
            messages.error(request, "Please select a valid course created in the system.")
            return redirect('exam_create')

        course = get_object_or_404(Course, id=course_id)
        assigned_faculty = User.objects.filter(id=assigned_faculty_id).first() if assigned_faculty_id else None

        exam = Examination.objects.create(
            course=course,
            title=title if title else f"Examination for {course.code}",
            exam_date=exam_date if exam_date else '2026-07-20',
            total_marks=total_marks,
            status=Examination.Status.PUBLISHED,
            assigned_faculty=assigned_faculty,
            created_by=request.user
        )

        faculty_str = f" (Assigned Examiner: {assigned_faculty.get_full_name() or assigned_faculty.username})" if assigned_faculty else ""
        messages.success(request, f"Examination '{exam.title}' for {course.code} created successfully!{faculty_str}")

        profile = getattr(request.user, 'profile', None)
        if (profile and profile.role == Profile.Role.ADMIN) or request.user.is_superuser:
            return redirect('exams_list')
        return redirect('teacher_dashboard')

    courses = Course.objects.select_related('department').all()
    faculty_members = Profile.objects.filter(role=Profile.Role.TEACHER).select_related('user', 'department')
    return render(request, 'core/exam_create.html', {
        'courses': courses,
        'faculty_members': faculty_members,
    })


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

    preset_code = request.GET.get('code', '').strip()
    preset_title = request.GET.get('title', '').strip()
    next_url = request.GET.get('next', '').strip()

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        code = request.POST.get('code', '').strip()
        dept_code = request.POST.get('department', '').strip()
        redirect_after = request.POST.get('next', '').strip()

        if Course.objects.filter(code=code).exists():
            messages.error(request, f"Course code '{code}' already exists.")
            return redirect('add_course')

        dept_obj = Department.objects.filter(code=dept_code).first()
        Course.objects.create(title=title, code=code, department=dept_obj)
        messages.success(request, f"Course '{title}' ({code}) registered successfully!")
        if redirect_after:
            return redirect(redirect_after)
        return redirect('courses_list')

    departments = Department.objects.filter(is_active=True)
    return render(request, 'core/add_course.html', {
        'departments': departments,
        'preset_code': preset_code,
        'preset_title': preset_title,
        'next_url': next_url,
    })


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


def api_get_courses_and_faculty(request):
    """API endpoint returning updated list of courses and faculty for dynamic dropdown auto-sync."""
    courses = list(Course.objects.select_related('department').values('id', 'code', 'title', 'department__name'))
    faculty = []
    for prof in Profile.objects.filter(role=Profile.Role.TEACHER).select_related('user', 'department'):
        faculty.append({
            'id': prof.user.id,
            'name': prof.user.get_full_name() or prof.user.username,
            'username': prof.user.username,
            'dept_code': prof.department.code if prof.department else ''
        })
    return JsonResponse({'courses': courses, 'faculty': faculty})


def api_publish_exam(request):
    """AJAX endpoint to publish an examination instantly without page reload."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required.'}, status=401)

    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        faculty_id = request.POST.get('faculty_id')
        exam_date = request.POST.get('exam_date')
        total_marks = request.POST.get('total_marks', 100.0)
        title = request.POST.get('title', '').strip()

        course = Course.objects.filter(id=course_id).first()
        faculty_user = User.objects.filter(id=faculty_id).first()

        if not course:
            return JsonResponse({'error': 'Invalid Course selected.'}, status=400)

        exam_title = title if title else f"{course.code} Examination"
        date_val = exam_date if (exam_date and exam_date != 'N/A') else '2026-08-15'

        exam = Examination.objects.create(
            course=course,
            title=exam_title,
            exam_date=date_val,
            total_marks=float(total_marks) if total_marks else 100.0,
            status=Examination.Status.PUBLISHED,
            assigned_faculty=faculty_user,
            created_by=request.user
        )

        faculty_name = faculty_user.get_full_name() or faculty_user.username if faculty_user else "Examiner"
        return JsonResponse({
            'success': True,
            'exam_id': exam.id,
            'message': f"Examination '{exam.title}' published successfully for {course.code} and assigned to {faculty_name}!"
        })
    return JsonResponse({'error': 'Invalid HTTP method.'}, status=405)
