from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import Profile, Department, Course

class RoutineScanUITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='controller_admin', password='testpassword123')
        self.profile = Profile.objects.create(user=self.user, role=Profile.Role.ADMIN)
        self.dept = Department.objects.create(name='Computer Science & Engineering', code='CSE')
        self.course = Course.objects.create(code='CSE 411', title='Software Engineering', department=self.dept)

    def test_exam_create_renders_modal(self):
        self.client.login(username='controller_admin', password='testpassword123')
        response = self.client.get(reverse('exam_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'routineScanModal')
        self.assertContains(response, 'routineModalProgressView')
        self.assertContains(response, 'runAIRoutineScanFromModal')
        self.assertContains(response, 'closeAIRoutineModal')

    def test_scan_routine_ai_requires_auth(self):
        client = Client()
        response = client.post(reverse('scan_routine_ai'), {'routine_text': 'CSE 411 Exam'})
        self.assertEqual(response.status_code, 401)
