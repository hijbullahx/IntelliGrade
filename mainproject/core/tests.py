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

    from unittest.mock import patch

    @patch('core.ai_engine.ocr.engine.OCREngineManager.extract_text')
    @patch('core.ai_engine.routine_parser.routine_parser.RoutineParser.parse_routine')
    def test_scan_routine_ai_multi_file_support(self, mock_parse, mock_ocr):
        from django.core.files.uploadedfile import SimpleUploadedFile
        mock_ocr.return_value = {'text': 'CSE 411 Software Engineering Exam Date: 2026-08-15 Examiner: Dr. Alan Turing'}
        mock_parse.return_value = {
            'routine_schedule': [
                {
                    'course_code': 'CSE 411',
                    'course_title': 'Software Engineering',
                    'exam_date': '2026-08-15',
                    'exam_time': '10:00 AM - 01:00 PM',
                    'faculty_name': 'Dr. Alan Turing'
                },
                {
                    'course_code': 'CSE 4383',
                    'course_title': 'Advanced DB',
                    'exam_date': '2026-08-18',
                    'exam_time': '02:00 PM - 05:00 PM',
                    'faculty_name': 'Drs Ferdaus'
                }
            ]
        }
        self.client.login(username='controller_admin', password='testpassword123')
        file1 = SimpleUploadedFile("page1.png", b"fake_png_data_1", content_type="image/png")
        file2 = SimpleUploadedFile("page2.png", b"fake_png_data_2", content_type="image/png")
        
        response = self.client.post(reverse('scan_routine_ai'), {'routine_files': [file1, file2]})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertEqual(len(data.get('routine_items', [])), 2)

    def test_question_rubric_manage_renders_modal(self):
        from core.models import Examination
        from django.utils import timezone
        exam = Examination.objects.create(
            course=self.course,
            title='Midterm Exam',
            exam_date=timezone.now().date(),
            total_marks=100.00,
            assigned_faculty=self.user
        )
        self.client.login(username='controller_admin', password='testpassword123')
        response = self.client.get(reverse('question_rubric_manage', kwargs={'exam_id': exam.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'scanProgressModal')
        self.assertContains(response, 'scanModalProgressView')
        self.assertContains(response, 'runAIQuestionScanFromModal')
        self.assertContains(response, 'openScanQuestionModal')
