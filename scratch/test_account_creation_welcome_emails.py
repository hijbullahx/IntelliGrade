#!/usr/bin/env python
"""
Test Suite: User Account Creation & Welcome Email Automation Verification
Verifies:
1. Faculty creation by Admin -> Welcome email with credentials & /teacher/login/ link
2. Dept Head creation by Admin -> Welcome email with credentials & /dept-head/login/ link
3. Student direct creation by Chief Exam Controller -> Welcome email with credentials & /student/login/ link
4. Student self-registration -> is_approved=False
5. Student approval by Chief Exam Controller -> Welcome approval email with /student/login/ link
6. HTML rendering quality & verification of credentials box in account_welcome.html
"""

import os
import sys
import time
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
MAINPROJECT_DIR = REPO_ROOT / 'mainproject'
sys.path.insert(0, str(MAINPROJECT_DIR))
sys.path.insert(0, str(REPO_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainproject.settings')

import django
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client
from django.template.loader import render_to_string

from core.models import Profile, Department, College, School
from core.services.email_service import EmailService

print("=" * 75)
print("INTELLIGRADE USER CREATION & WELCOME EMAIL VERIFICATION SUITE")
print("=" * 75)

# Setup initial test department
dept, _ = Department.objects.get_or_create(
    code="CSE_TEST",
    defaults={"name": "Computer Science and Engineering (Test)", "is_active": True}
)

admin_user, _ = User.objects.get_or_create(
    username="test_admin_controller",
    defaults={"email": "controller@dsr.iubat.ac.bd", "is_superuser": True, "is_staff": True}
)
admin_user.set_password("AdminPass123!")
admin_user.save()
Profile.objects.update_or_create(
    user=admin_user,
    defaults={"role": Profile.Role.ADMIN, "is_approved": True}
)

client = Client()
client.login(username="test_admin_controller", password="AdminPass123!")

benchmarks = []

def record_test(name, duration_ms, status, details=""):
    benchmarks.append({'name': name, 'duration_ms': duration_ms, 'status': status, 'details': details})

# ----------------------------------------------------------------------
# Test 1: Direct Student Creation by Chief Exam Controller
# ----------------------------------------------------------------------
t0 = time.perf_counter()
test_student_id = f"std_{int(time.time())}"
test_student_email = f"{test_student_id}@iubat.edu"
test_student_pass = "StdPass2026!"

# Clean any preexisting
User.objects.filter(username=test_student_id).delete()

with patch.object(EmailService, '_send_async_email') as mock_send:
    resp = client.post('/controller/add-student/', {
        'full_name': 'Hasan Mahmud Student',
        'email': test_student_email,
        'student_id': test_student_id,
        'password': test_student_pass,
        'department': dept.code
    })

    assert resp.status_code in (200, 302), f"add_student returned {resp.status_code}"
    created_std = User.objects.filter(username=test_student_id).first()
    assert created_std is not None, "Student user not created in DB!"
    assert created_std.profile.is_approved is True, "Direct created student should be is_approved=True!"
    assert created_std.profile.role == Profile.Role.STUDENT, "Profile role should be STUDENT!"

    # Verify EmailService was called
    assert mock_send.called, "EmailService._send_async_email was not called for add_student!"
    call_args = mock_send.call_args
    subject, recipient_list, template_name, context = call_args[0]
    assert test_student_email in recipient_list, f"Recipient list mismatch: {recipient_list}"
    assert context['raw_password'] == test_student_pass, "Password not in email context!"
    assert "/student/login/" in context['login_url'], f"Login URL mismatch: {context['login_url']}"
    assert context['role_name'] == "Student", f"Role mismatch: {context['role_name']}"

t1 = (time.perf_counter() - t0) * 1000
record_test("1. Direct Student Creation by Controller", t1, "PASSED", f"Email dispatched with credentials to {test_student_email}")
print(f"[1/5] Direct Student Creation: PASSED ({t1:.2f} ms)")


# ----------------------------------------------------------------------
# Test 2: Student Self-Registration & Subsequent Controller Approval
# ----------------------------------------------------------------------
t0 = time.perf_counter()
self_student_id = f"self_{int(time.time())}"
self_student_email = f"{self_student_id}@iubat.edu"
self_student_pass = "SelfPass2026!"

User.objects.filter(username=self_student_id).delete()

# Unauthenticated student self-registers
guest_client = Client()
with patch.object(EmailService, '_send_async_email') as mock_send_self:
    resp_reg = guest_client.post('/student/register/', {
        'full_name': 'Self Registered Student',
        'email': self_student_email,
        'student_id': self_student_id,
        'password': self_student_pass,
        'department': dept.code
    })
    # Upon self-registration, user is pending approval -> NO welcome email yet
    self_std = User.objects.filter(username=self_student_id).first()
    assert self_std is not None, "Self-registered student not created!"
    assert self_std.profile.is_approved is False, "Self-registered student should have is_approved=False!"
    assert not mock_send_self.called, "Welcome email should NOT be sent before controller approval!"

# Now Chief Exam Controller approves the pending student
with patch.object(EmailService, '_send_async_email') as mock_send_approve:
    resp_approve = client.get(f'/controller/approve-student/{self_std.profile.id}/')
    self_std.refresh_from_db()
    assert self_std.profile.is_approved is True, "Student profile is_approved should be True after approval!"
    assert mock_send_approve.called, "Welcome approval email was not dispatched upon controller approval!"
    
    call_args = mock_send_approve.call_args
    subject, recipient_list, template_name, context = call_args[0]
    assert self_student_email in recipient_list
    assert "/student/login/" in context['login_url']
    assert context['is_approval'] is True
    assert "Approved" in subject

t2 = (time.perf_counter() - t0) * 1000
record_test("2. Student Self-Registration & Approval", t2, "PASSED", f"Approval email dispatched to {self_student_email}")
print(f"[2/5] Student Self-Registration & Approval Flow: PASSED ({t2:.2f} ms)")


# ----------------------------------------------------------------------
# Test 3: Faculty Creation by Chief Exam Controller
# ----------------------------------------------------------------------
t0 = time.perf_counter()
faculty_username = f"fac_{int(time.time())}"
faculty_email = f"{faculty_username}@iubat.edu"
faculty_pass = "FacPass2026!"

User.objects.filter(username=faculty_username).delete()

with patch.object(EmailService, '_send_async_email') as mock_send_fac:
    resp_fac = client.post('/controller/add-faculty/', {
        'full_name': 'Prof. Dr. Tariqul Islam',
        'email': faculty_email,
        'username': faculty_username,
        'password': faculty_pass,
        'department': dept.code
    })
    created_fac = User.objects.filter(username=faculty_username).first()
    assert created_fac is not None, "Faculty user not created!"
    assert created_fac.profile.role == Profile.Role.TEACHER, "Role should be TEACHER!"
    assert mock_send_fac.called, "Welcome email not sent to new faculty member!"

    call_args = mock_send_fac.call_args
    subject, recipient_list, template_name, context = call_args[0]
    assert faculty_email in recipient_list
    assert context['raw_password'] == faculty_pass
    assert "/teacher/login/" in context['login_url']
    assert "Faculty" in context['role_name']

t3 = (time.perf_counter() - t0) * 1000
record_test("3. Faculty Creation by Controller", t3, "PASSED", f"Credentials & teacher login link dispatched to {faculty_email}")
print(f"[3/5] Faculty Creation: PASSED ({t3:.2f} ms)")


# ----------------------------------------------------------------------
# Test 4: Department Head Creation by Chief Exam Controller
# ----------------------------------------------------------------------
t0 = time.perf_counter()
depthead_username = f"head_{int(time.time())}"
depthead_email = f"{depthead_username}@iubat.edu"
depthead_pass = "HeadPass2026!"

User.objects.filter(username=depthead_username).delete()

with patch.object(EmailService, '_send_async_email') as mock_send_head:
    resp_head = client.post('/controller/add-dept-head/', {
        'full_name': 'Dr. Department Head',
        'email': depthead_email,
        'username': depthead_username,
        'password': depthead_pass,
        'department': dept.code
    })
    created_head = User.objects.filter(username=depthead_username).first()
    assert created_head is not None, "Dept head user not created!"
    assert created_head.profile.role == Profile.Role.DEPARTMENT_HEAD, "Role should be DEPT_HEAD!"
    assert mock_send_head.called, "Welcome email not sent to new dept head!"

    call_args = mock_send_head.call_args
    subject, recipient_list, template_name, context = call_args[0]
    assert depthead_email in recipient_list
    assert context['raw_password'] == depthead_pass
    assert "/dept-head/login/" in context['login_url']
    assert "Department Head" in context['role_name']

t4 = (time.perf_counter() - t0) * 1000
record_test("4. Department Head Creation by Controller", t4, "PASSED", f"Credentials & dept-head login link dispatched to {depthead_email}")
print(f"[4/5] Department Head Creation: PASSED ({t4:.2f} ms)")


# ----------------------------------------------------------------------
# Test 5: Template Rendering Verification for All Roles
# ----------------------------------------------------------------------
t0 = time.perf_counter()
roles_to_test = [
    {"role": "Student", "url": "http://127.0.0.1:8000/student/login/", "raw_pass": "StdPass!", "is_appr": False},
    {"role": "Student", "url": "http://127.0.0.1:8000/student/login/", "raw_pass": None, "is_appr": True},
    {"role": "Faculty Member / Examiner", "url": "http://127.0.0.1:8000/teacher/login/", "raw_pass": "FacPass!", "is_appr": False},
    {"role": "Department Head", "url": "http://127.0.0.1:8000/dept-head/login/", "raw_pass": "HeadPass!", "is_appr": False},
]

for item in roles_to_test:
    html = render_to_string('emails/account_welcome.html', {
        'user': admin_user,
        'raw_password': item['raw_pass'],
        'role_name': item['role'],
        'department_name': 'Computer Science and Engineering',
        'login_url': item['url'],
        'is_approval': item['is_appr']
    })
    assert "INTELLIGRADE" in html, "Branding header missing!"
    assert "Sign-In Credentials" in html or "Account Credentials" in html, "Credentials card missing!"
    assert item['url'] in html, f"Login URL {item['url']} not rendered in template!"
    if item['raw_pass']:
        assert item['raw_pass'] in html, f"Password {item['raw_pass']} not rendered in template!"
    if item['is_appr']:
        assert "Approved" in html, "Approval banner not rendered for approved student!"

t5 = (time.perf_counter() - t0) * 1000
record_test("5. Multi-Role Email HTML UI Validation", t5, "PASSED", "Verified Student, Faculty, Dept Head & Approval templates")
print(f"[5/5] Multi-Role Email HTML UI Validation: PASSED ({t5:.2f} ms)")


# ----------------------------------------------------------------------
# Execution Benchmark & Summary Report
# ----------------------------------------------------------------------
print("")
print("=" * 75)
print("EXECUTION BENCHMARKS & DELIVERY STATUSES")
print("=" * 75)
print(f"{'Test Case':<45} | {'Latency':<10} | {'Status':<12}")
print("-" * 75)
for b in benchmarks:
    print(f"{b['name']:<45} | {b['duration_ms']:>7.2f} ms | {b['status']:<12}")
print("=" * 75)
print(f"ALL {len(benchmarks)} USER CREATION & WELCOME EMAIL TESTS PASSED WITH 100% SUCCESS.")
print("=" * 75)
