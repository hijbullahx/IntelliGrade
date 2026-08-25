#!/usr/bin/env python
"""
IntelliGrade All-Roles Password Reset Verification Suite
Comprehensive end-to-end test verifying password reset lifecycle for:
1. Student
2. Faculty / Examiner
3. Department Head
4. Chief Exam Controller / Admin
5. Security Edge Cases (Tamper, wrong OTP, unverified access)
"""

import os
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MAINPROJECT_DIR = REPO_ROOT / 'mainproject'
sys.path.insert(0, str(MAINPROJECT_DIR))
sys.path.insert(0, str(REPO_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainproject.settings')

import django
django.setup()

from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import User
from django.test import Client

from core.models import Profile, Department

print("=" * 75)
print("INTELLIGRADE ALL-ROLES FORGOT PASSWORD RESET VERIFICATION")
print("=" * 75)

dept, _ = Department.objects.get_or_create(code="CSE", defaults={"name": "Computer Science & Engineering", "is_active": True})

roles_config = [
    {
        'role_code': Profile.Role.STUDENT,
        'role_name': 'Student',
        'username': f'std_reset_{int(time.time())}',
        'email': f'student_reset_{int(time.time())}@iubat.edu',
        'initial_pass': 'InitialStudent123!',
        'new_pass': 'NewStudentPass2026!#',
        'expected_redirect': '/student/login/'
    },
    {
        'role_code': Profile.Role.TEACHER,
        'role_name': 'Faculty Member / Examiner',
        'username': f'fac_reset_{int(time.time())}',
        'email': f'faculty_reset_{int(time.time())}@iubat.edu',
        'initial_pass': 'InitialFaculty123!',
        'new_pass': 'NewFacultyPass2026!#',
        'expected_redirect': '/teacher/login/'
    },
    {
        'role_code': Profile.Role.DEPARTMENT_HEAD,
        'role_name': 'Department Head',
        'username': f'head_reset_{int(time.time())}',
        'email': f'depthead_reset_{int(time.time())}@iubat.edu',
        'initial_pass': 'InitialDeptHead123!',
        'new_pass': 'NewDeptHeadPass2026!#',
        'expected_redirect': '/dept-head/login/'
    },
    {
        'role_code': Profile.Role.ADMIN,
        'role_name': 'Chief Exam Controller',
        'username': f'admin_reset_{int(time.time())}',
        'email': f'controller_reset_{int(time.time())}@iubat.edu',
        'initial_pass': 'InitialAdmin123!',
        'new_pass': 'NewAdminPass2026!#',
        'expected_redirect': '/controller/login/'
    }
]

benchmarks = []

for idx, conf in enumerate(roles_config, start=1):
    t0 = time.perf_counter()
    
    # 1. Create user in DB
    User.objects.filter(username=conf['username']).delete()
    user = User.objects.create_user(
        username=conf['username'],
        email=conf['email'],
        password=conf['initial_pass'],
        first_name=f"Test {conf['role_name']}"
    )
    if conf['role_code'] == Profile.Role.ADMIN:
        user.is_superuser = True
        user.is_staff = True
        user.save()
    Profile.objects.update_or_create(
        user=user,
        defaults={'role': conf['role_code'], 'department': dept, 'is_approved': True}
    )

    client = Client()

    # Step A: POST /auth/forgot-password/ using Username / ID
    resp_forgot = client.post('/auth/forgot-password/', {'identifier': conf['username']})
    assert resp_forgot.status_code in (200, 302), f"Forgot password failed for {conf['role_name']}"
    assert client.session.get('reset_user_id') == user.id, "Session reset_user_id not saved!"

    # Retrieve cached OTP
    otp_code = cache.get(f"password_reset_otp_{user.id}")
    assert otp_code is not None, f"OTP not generated in cache for {conf['role_name']}"
    assert len(otp_code) == 6, f"OTP length invalid: {otp_code}"

    # Step B: POST /auth/verify-otp/ with correct OTP
    resp_verify = client.post('/auth/verify-otp/', {'otp': otp_code})
    assert client.session.get('otp_verified') is True, f"OTP verification failed for {conf['role_name']}"

    # Step C: POST /auth/reset-password/ with new password
    resp_reset = client.post('/auth/reset-password/', {
        'new_password': conf['new_pass'],
        'confirm_password': conf['new_pass']
    })
    assert resp_reset.status_code == 302, f"Reset password did not redirect: {resp_reset.status_code}"
    assert resp_reset.url == conf['expected_redirect'], f"Redirect mismatch for {conf['role_name']}: expected {conf['expected_redirect']}, got {resp_reset.url}"

    # Step D: Verify Database password changed
    user.refresh_from_db()
    assert user.check_password(conf['new_pass']), f"Password in DB not updated for {conf['role_name']}!"
    assert not user.check_password(conf['initial_pass']), "Old password still valid!"

    # Step E: Verify new password allows login to their specific login endpoint
    login_client = Client()
    login_resp = login_client.post(conf['expected_redirect'], {
        'username': conf['username'],
        'password': conf['new_pass']
    })
    assert login_resp.status_code in (200, 302), f"Login failed with new password for {conf['role_name']}"
    assert login_client.session.get('_auth_user_id') == str(user.id), f"User was not authenticated into session after reset for {conf['role_name']}!"

    dt = (time.perf_counter() - t0) * 1000
    benchmarks.append({
        'name': f"{idx}. {conf['role_name']} Reset Flow",
        'duration_ms': dt,
        'status': 'PASSED',
        'details': f"Redirected to {conf['expected_redirect']}, Authenticated with new pass"
    })
    print(f"[{idx}/5] {conf['role_name']} Password Reset Flow: PASSED ({dt:.2f} ms)")


# ----------------------------------------------------------------------
# Test 5: Security Edge Cases
# ----------------------------------------------------------------------
t0 = time.perf_counter()
sec_client = Client()

# 5.1 Direct access to reset-password without OTP verification -> should redirect to forgot_password
resp_unauth = sec_client.get('/auth/reset-password/')
assert resp_unauth.status_code == 302 and resp_unauth.url == '/auth/forgot-password/', "Direct access without OTP was not blocked!"

# 5.2 Invalid OTP code validation
test_u = User.objects.first()
sec_client.post('/auth/forgot-password/', {'identifier': test_u.username})
resp_bad_otp = sec_client.post('/auth/verify-otp/', {'otp': '000000'})
assert sec_client.session.get('otp_verified') is not True, "Bad OTP accepted!"

# 5.3 Password mismatch validation
otp_good = cache.get(f"password_reset_otp_{test_u.id}")
sec_client.post('/auth/verify-otp/', {'otp': otp_good})
assert sec_client.session.get('otp_verified') is True

resp_mismatch = sec_client.post('/auth/reset-password/', {
    'new_password': 'ValidPassword123!',
    'confirm_password': 'DifferentPassword456!'
})
assert resp_mismatch.status_code == 200, "Password mismatch did not stay on reset page!"
assert test_u.check_password('ValidPassword123!') is False, "Mismatched password was incorrectly saved!"

t_sec = (time.perf_counter() - t0) * 1000
benchmarks.append({
    'name': "5. Security Edge Cases (Tamper/Bad OTP/Mismatch)",
    'duration_ms': t_sec,
    'status': 'PASSED',
    'details': 'Direct access blocked, bad OTP rejected, mismatch handled'
})
print(f"[5/5] Security Edge Cases: PASSED ({t_sec:.2f} ms)")

print("")
print("=" * 75)
print("EXECUTION BENCHMARKS & DELIVERY STATUSES")
print("=" * 75)
print(f"{'Test Case':<50} | {'Latency':<10} | {'Status':<12}")
print("-" * 75)
for b in benchmarks:
    print(f"{b['name']:<50} | {b['duration_ms']:>7.2f} ms | {b['status']:<12}")
print("=" * 75)
print(f"ALL {len(benchmarks)} USER ROLE PASSWORD RESET FLOWS PASSED 100% SUCCESSFULLY.")
print("=" * 75)
