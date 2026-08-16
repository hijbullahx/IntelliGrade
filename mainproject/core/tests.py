import io
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
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


class DatabaseConfigurationTestCase(TestCase):
    def test_default_sqlite_configuration(self):
        from pathlib import Path
        from unittest.mock import patch
        from config.runtime_config import build_database_config

        base_dir = Path('/fake/base/dir')
        with patch.dict('os.environ', {}, clear=True):
            db_cfg = build_database_config(base_dir)
            self.assertEqual(db_cfg['default']['ENGINE'], 'django.db.backends.sqlite3')
            self.assertEqual(db_cfg['default']['NAME'], base_dir / 'db.sqlite3')

    def test_postgresql_valid_configuration(self):
        from pathlib import Path
        from unittest.mock import patch
        from config.runtime_config import build_database_config

        base_dir = Path('/fake/base/dir')
        env_vars = {
            'DB_ENGINE': 'postgresql',
            'DB_NAME': 'test_prod_db',
            'DB_USER': 'test_user',
            'DB_PASSWORD': 'supersecretpassword',
            'DB_HOST': 'db.internal.example.com',
            'DB_PORT': '5432',
        }
        with patch.dict('os.environ', env_vars, clear=True):
            db_cfg = build_database_config(base_dir)
            self.assertEqual(db_cfg['default']['ENGINE'], 'django.db.backends.postgresql')
            self.assertEqual(db_cfg['default']['NAME'], 'test_prod_db')
            self.assertEqual(db_cfg['default']['USER'], 'test_user')
            self.assertEqual(db_cfg['default']['PASSWORD'], 'supersecretpassword')
            self.assertEqual(db_cfg['default']['HOST'], 'db.internal.example.com')
            self.assertEqual(db_cfg['default']['PORT'], '5432')

    def test_postgresql_missing_credentials_raises_error(self):
        from pathlib import Path
        from unittest.mock import patch
        from django.core.exceptions import ImproperlyConfigured
        from config.runtime_config import build_database_config

        base_dir = Path('/fake/base/dir')
        env_vars = {
            'DB_ENGINE': 'postgresql',
            # Missing DB_NAME, DB_USER, DB_PASSWORD
        }
        with patch.dict('os.environ', env_vars, clear=True):
            with self.assertRaises(ImproperlyConfigured) as ctx:
                build_database_config(base_dir)
            self.assertIn('PostgreSQL selected', str(ctx.exception))
            self.assertIn('DB_NAME', str(ctx.exception))

    def test_env_file_loaded_before_database_config(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        from config.runtime_config import build_database_config

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            env_file = temp_path / '.env'
            env_file.write_text(
                "DB_ENGINE=postgresql\n"
                "DB_NAME=dsriubatac_intelligrade\n"
                "DB_USER=dsriubatac_intelligrade_db\n"
                "DB_PASSWORD=test_secret_pass\n"
                "DB_HOST=localhost\n"
                "DB_PORT=5432\n"
            )

            # Clear environment to prove .env file is read and loaded before database configuration
            with patch.dict('os.environ', {}, clear=True):
                db_cfg = build_database_config(temp_path)
                self.assertEqual(db_cfg['default']['ENGINE'], 'django.db.backends.postgresql')
                self.assertEqual(db_cfg['default']['NAME'], 'dsriubatac_intelligrade')
                self.assertEqual(db_cfg['default']['USER'], 'dsriubatac_intelligrade_db')
                self.assertEqual(db_cfg['default']['PASSWORD'], 'test_secret_pass')
                self.assertEqual(db_cfg['default']['HOST'], 'localhost')
                self.assertEqual(db_cfg['default']['PORT'], '5432')


class AIFailoverResilienceTestCase(TestCase):
    """
    Test suite for AI Provider failover, timeout handling, error propagation,
    and graceful deterministic regex fallback during Question Paper Scanning.
    """

    def setUp(self):
        from core.ai_engine.providers.gemini import GeminiProvider
        from core.ai_engine.providers.groq import GroqProvider
        from core.ai_engine.providers.failover import FailoverAIProvider
        self.gemini = GeminiProvider(api_key="test_gemini_key")
        self.groq = GroqProvider(api_key="test_groq_key")
        self.failover_provider = FailoverAIProvider(primary_provider=self.gemini)
        # Explicitly configure chain with Gemini -> Groq
        self.failover_provider._chain = [self.gemini, self.groq]

    def _mock_http_response(self, data_dict):
        resp = MagicMock()
        resp.__enter__.return_value = resp
        resp.read.return_value = json.dumps(data_dict).encode('utf-8')
        return resp

    @patch('urllib.request.urlopen')
    def test_provider_timeout_triggers_failover(self, mock_urlopen):
        import socket
        groq_resp = self._mock_http_response({
            'choices': [{
                'message': {
                    'content': json.dumps({
                        'questions': [{
                            'question_number': 'Q1',
                            'prompt_text': 'Explain Software Design Patterns.',
                            'allocated_marks': 10.0,
                            'question_type': ['Theory'],
                            'command_verbs': ['Explain'],
                            'bloom_level': 'Understand',
                            'co_mapping': 'CO1',
                            'po_mapping': ['PO1'],
                            'criteria': 'Correct definition and example.',
                            'ideal_answer': 'Patterns are reusable architectural solutions.'
                        }]
                    })
                }
            }]
        })

        # Gemini times out on both attempts/models, then Groq succeeds
        mock_urlopen.side_effect = [
            socket.timeout("The read operation timed out"),
            socket.timeout("The read operation timed out"),
            groq_resp
        ]

        result = self.failover_provider.analyze_academic_exam_paper("Question 1: Explain Software Design Patterns. [10 marks]")
        self.assertIn('questions', result)
        self.assertEqual(len(result['questions']), 1)
        self.assertEqual(result['questions'][0]['question_number'], 'Q1')

    @patch('urllib.request.urlopen')
    def test_provider_http_error_triggers_failover(self, mock_urlopen):
        import urllib.error
        fp = io.BytesIO(b'{"error": {"message": "Resource exhausted / Rate limit exceeded"}}')
        http_err = urllib.error.HTTPError("https://generativelanguage.googleapis.com", 429, "Too Many Requests", {}, fp)

        groq_resp = self._mock_http_response({
            'choices': [{
                'message': {
                    'content': json.dumps({
                        'questions': [{
                            'question_number': 'Q1',
                            'prompt_text': 'Derive the quadratic formula.',
                            'allocated_marks': 15.0
                        }]
                    })
                }
            }]
        })

        mock_urlopen.side_effect = [
            http_err,
            http_err,
            groq_resp
        ]

        result = self.failover_provider.analyze_academic_exam_paper("Question 1: Derive the quadratic formula. [15 marks]")
        self.assertIn('questions', result)
        self.assertEqual(result['questions'][0]['question_number'], 'Q1')

    @patch('urllib.request.urlopen')
    def test_empty_or_non_json_provider_response_triggers_failover(self, mock_urlopen):
        bad_resp = MagicMock()
        bad_resp.__enter__.return_value = bad_resp
        bad_resp.read.return_value = b"Internal Provider Error - Non JSON"

        groq_resp = self._mock_http_response({
            'choices': [{
                'message': {
                    'content': json.dumps({
                        'questions': [{
                            'question_number': 'Q1',
                            'prompt_text': 'Explain Database Normalization.',
                            'allocated_marks': 20.0
                        }]
                    })
                }
            }]
        })

        mock_urlopen.side_effect = [
            bad_resp,
            bad_resp,
            groq_resp
        ]

        result = self.failover_provider.analyze_academic_exam_paper("Question 1: Explain Database Normalization. [20 marks]")
        self.assertIn('questions', result)
        self.assertEqual(result['questions'][0]['question_number'], 'Q1')

    @patch('urllib.request.urlopen')
    def test_complete_provider_failure_graceful_fallback(self, mock_urlopen):
        # All providers fail / throw exceptions
        mock_urlopen.side_effect = Exception("All network connections refused")

        doc_text = """
        Question 1: Discuss the advantages of Convolutional Neural Networks over Fully Connected Networks. [10 marks]
        Question 2: Calculate the output dimensions of a 3x3 convolution layer with stride 1 and padding 0. [15 marks]
        """

        result = self.failover_provider.analyze_academic_exam_paper(doc_text)
        # Should gracefully extract questions via deterministic regex without raising an unhandled exception
        self.assertIn('questions', result)
        self.assertGreaterEqual(len(result['questions']), 2)
        q_nums = [q['question_number'] for q in result['questions']]
        self.assertIn('Q1', q_nums)
        self.assertIn('Q2', q_nums)

    @patch('core.ai_engine.providers.factory.AIProviderFactory.get_provider')
    def test_api_scan_question_paper_endpoint_with_failover(self, mock_get_provider):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from core.models import Examination
        from django.utils import timezone
        import fitz

        mock_get_provider.return_value = self.failover_provider

        # Create a simple PDF document with fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 72), "Question 1: Explain the MVC architecture pattern. [10 marks]\nQuestion 2: What is the purpose of ORM? [15 marks]")
        pdf_bytes = doc.tobytes()
        doc.close()

        user = User.objects.create_user(username='faculty_tester', password='testpassword123')
        Profile.objects.create(user=user, role=Profile.Role.TEACHER)
        dept = Department.objects.create(name='CSE Dept', code='CSED')
        course = Course.objects.create(code='CSE 4385', title='Software Engg', department=dept)
        exam = Examination.objects.create(
            course=course,
            title='Midterm Examination CSE 4385',
            assigned_faculty=user,
            total_marks=25.0,
            exam_date=timezone.now().date()
        )

        client = Client()
        client.login(username='faculty_tester', password='testpassword123')

        uploaded_pdf = SimpleUploadedFile("Midterm_Questions_CSE4385.pdf", pdf_bytes, content_type="application/pdf")

        # Force mock urlopen inside failover provider to fail Gemini and pass Groq
        groq_resp = self._mock_http_response({
            'choices': [{
                'message': {
                    'content': json.dumps({
                        'questions': [
                            {
                                'question_number': 'Q1',
                                'prompt_text': 'Explain the MVC architecture pattern.',
                                'allocated_marks': 10.0,
                                'question_type': ['Theory'],
                                'command_verbs': ['Explain'],
                                'bloom_level': 'Understand',
                                'co_mapping': 'CO1',
                                'po_mapping': ['PO1'],
                                'criteria': 'Model-View-Controller definition.',
                                'ideal_answer': 'Architectural pattern decoupling UI from data.'
                            },
                            {
                                'question_number': 'Q2',
                                'prompt_text': 'What is the purpose of ORM?',
                                'allocated_marks': 15.0,
                                'question_type': ['Theory'],
                                'command_verbs': ['Explain'],
                                'bloom_level': 'Understand',
                                'co_mapping': 'CO2',
                                'po_mapping': ['PO1'],
                                'criteria': 'Object-relational mapping definition.',
                                'ideal_answer': 'Maps object-oriented models to relational schemas.'
                            }
                        ]
                    })
                }
            }]
        })

        with patch('urllib.request.urlopen') as mock_urlopen:
            # Gemini fails with 429, Groq succeeds
            import urllib.error
            fp = io.BytesIO(b'{"error": {"message": "Gemini 429 Rate Limit"}}')
            http_err = urllib.error.HTTPError("https://generativelanguage.googleapis.com", 429, "Too Many Requests", {}, fp)
            mock_urlopen.side_effect = [http_err, http_err, groq_resp]

            response = client.post(reverse('api_scan_question_paper'), {
                'examination_id': str(exam.id),
                'question_paper_files': [uploaded_pdf]
            })

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data.get('success'))
            self.assertEqual(data.get('extracted_count'), 2)
            self.assertEqual(len(data['data']['questions']), 2)
            self.assertEqual(data['data']['questions'][0]['question_number'], 'Q1')
            self.assertEqual(data['data']['questions'][1]['question_number'], 'Q2')

    def test_global_failover_budget_exhaustion_skips_next_provider(self):
        import time

        def slow_failing_gemini(*args, **kwargs):
            time.sleep(1.2)
            raise Exception("Gemini timed out slowly")

        def should_not_be_called_groq(*args, **kwargs):
            raise AssertionError("Groq should NOT have been called because global budget was exhausted!")

        self.gemini.analyze_academic_exam_paper = slow_failing_gemini
        self.groq.analyze_academic_exam_paper = should_not_be_called_groq

        doc_text = """
        Question 1: Explain the principles of Distributed Systems. [10 marks]
        Question 2: Describe the Byzantine Generals Problem. [15 marks]
        """

        # Set strict global budget of 1.5s
        with patch.dict('os.environ', {'AI_TOTAL_TIMEOUT_BUDGET': '1.5', 'AI_REQUEST_TIMEOUT': '2.0'}):
            start_t = time.monotonic()
            result = self.failover_provider.analyze_academic_exam_paper(doc_text)
            elapsed = time.monotonic() - start_t

            self.assertLess(elapsed, 2.5) # Total execution finished rapidly
            self.assertIn('questions', result)
            self.assertGreaterEqual(len(result['questions']), 2)
            q_nums = [q['question_number'] for q in result['questions']]
            self.assertIn('Q1', q_nums)
            self.assertIn('Q2', q_nums)

    @patch('urllib.request.urlopen')
    def test_successful_provider_response_within_budget(self, mock_urlopen):
        # Gemini succeeds immediately within budget
        gemini_resp = self._mock_http_response({
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': json.dumps({
                            'questions': [{
                                'question_number': 'Q1',
                                'prompt_text': 'What is ACID in Databases?',
                                'allocated_marks': 10.0,
                                'question_type': ['Theory'],
                                'command_verbs': ['Explain'],
                                'bloom_level': 'Understand',
                                'co_mapping': 'CO1',
                                'po_mapping': ['PO1'],
                                'criteria': 'Atomicity, Consistency, Isolation, Durability.',
                                'ideal_answer': 'ACID guarantees database transaction reliability.'
                            }]
                        })
                    }]
                }
            }]
        })
        mock_urlopen.return_value = gemini_resp

        result = self.failover_provider.analyze_academic_exam_paper("Question 1: What is ACID in Databases? [10 marks]")
        self.assertIn('questions', result)
        self.assertEqual(len(result['questions']), 1)
        self.assertEqual(result['questions'][0]['question_number'], 'Q1')
        self.assertEqual(result['questions'][0]['prompt_text'], 'What is ACID in Databases?')





