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

    def test_digital_pdf_skips_easyocr(self):
        from core.ai_engine.document_service import DocumentService
        import fitz

        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 72), "Question 1: Explain the MVC architecture pattern in detail. [10 marks]\nQuestion 2: What is the purpose of ORM in modern web frameworks? [15 marks]")
        pdf_bytes = doc.tobytes()
        doc.close()

        with patch('core.ai_engine.document_service.DocumentService.extract_easyocr_text') as mock_easyocr:
            ocr_res = DocumentService.extract_deterministic_ocr(pdf_bytes, page_renders=[b'dummy_png'], mime_type='application/pdf')
            self.assertEqual(ocr_res['engine'], 'PyMuPDF Native Extractor')
            self.assertGreaterEqual(len(ocr_res['text']), 50)
            mock_easyocr.assert_not_called()

    def test_easyocr_disabled_prevents_easyocr_invocation(self):
        from config.ocr_config import is_easyocr_enabled, get_ocr_reader
        from core.ai_engine.document_service import DocumentService

        with patch.dict('os.environ', {'EASYOCR_ENABLED': 'False'}):
            self.assertFalse(is_easyocr_enabled())
            self.assertIsNone(get_ocr_reader())
            res = DocumentService.extract_easyocr_text(b'fake_image_bytes')
            self.assertEqual(res['engine'], 'EasyOCR Disabled')
            self.assertEqual(res['text'], '')

    @patch('core.ai_engine.document_service.DocumentService.extract_tesseract_text')
    def test_scanned_pdf_uses_pytesseract_fallback(self, mock_tesseract):
        from core.ai_engine.document_service import DocumentService
        mock_tesseract.return_value = {"text": "Question 1: Explain Dijkstra Shortest Path Algorithm. [15 marks]", "confidence": 0.85, "engine": "PyTesseract"}

        # Create scanned/empty text PDF
        import fitz
        doc = fitz.open()
        doc.new_page() # blank page
        pdf_bytes = doc.tobytes()
        doc.close()

        with patch.dict('os.environ', {'EASYOCR_ENABLED': 'False'}):
            with patch('core.ai_engine.document_service.DocumentService.extract_easyocr_text') as mock_easyocr:
                ocr_res = DocumentService.extract_deterministic_ocr(pdf_bytes, page_renders=[b'dummy_page_render'], mime_type='application/pdf')
                self.assertEqual(ocr_res['engine'], 'PyTesseract Engine')
                self.assertIn('Dijkstra', ocr_res['text'])
                mock_easyocr.assert_not_called()

    @patch('urllib.request.urlopen')
    def test_ai_failover_groq_to_gemini(self, mock_urlopen):
        from core.ai_engine.providers.gemini import GeminiProvider
        from core.ai_engine.providers.groq import GroqProvider
        from core.ai_engine.providers.failover import FailoverAIProvider
        import urllib.error

        groq = GroqProvider(api_key="test_groq_key")
        gemini = GeminiProvider(api_key="test_gemini_key")
        failover = FailoverAIProvider(primary_provider=groq)
        failover._chain = [groq, gemini]

        # Groq fails with 429, Gemini succeeds
        fp = io.BytesIO(b'{"error":{"message":"Rate limit reached"}}')
        groq_err = urllib.error.HTTPError("https://api.groq.com", 429, "Too Many Requests", {}, fp)

        gemini_resp = self._mock_http_response({
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': json.dumps({
                            'questions': [{
                                'question_number': 'Q1',
                                'prompt_text': 'Explain Dijkstra Algorithm.',
                                'allocated_marks': 15.0,
                                'question_type': ['Theory'],
                                'command_verbs': ['Explain'],
                                'bloom_level': 'Understand',
                                'co_mapping': 'CO1',
                                'po_mapping': ['PO1'],
                                'criteria': 'Shortest path explanation.',
                                'ideal_answer': 'Graph search algorithm finding single-source shortest paths.'
                            }]
                        })
                    }]
                }
            }]
        })

        mock_urlopen.side_effect = [groq_err, gemini_resp]

        result = failover.analyze_academic_exam_paper("Question 1: Explain Dijkstra Algorithm. [15 marks]")
        self.assertIn('questions', result)
        self.assertEqual(result['questions'][0]['question_number'], 'Q1')
        self.assertEqual(result['questions'][0]['prompt_text'], 'Explain Dijkstra Algorithm.')

    @patch('urllib.request.urlopen')
    def test_ai_failover_gemini_to_openai(self, mock_urlopen):
        from core.ai_engine.providers.gemini import GeminiProvider
        from core.ai_engine.providers.openai import OpenAIProvider
        from core.ai_engine.providers.failover import FailoverAIProvider
        import urllib.error

        gemini = GeminiProvider(api_key="test_gemini_key")
        openai = OpenAIProvider(api_key="test_openai_key")
        failover = FailoverAIProvider(primary_provider=gemini)
        failover._chain = [gemini, openai]

        # Gemini fails with 500, OpenAI succeeds
        fp = io.BytesIO(b'{"error":{"message":"Internal Server Error"}}')
        gemini_err = urllib.error.HTTPError("https://generativelanguage.googleapis.com", 500, "Internal Server Error", {}, fp)

        openai_resp = self._mock_http_response({
            'choices': [{
                'message': {
                    'content': json.dumps({
                        'questions': [{
                            'question_number': 'Q1',
                            'prompt_text': 'What is Dynamic Programming?',
                            'allocated_marks': 10.0,
                            'question_type': ['Theory'],
                            'command_verbs': ['Explain'],
                            'bloom_level': 'Understand',
                            'co_mapping': 'CO2',
                            'po_mapping': ['PO1'],
                            'criteria': 'Optimal substructure and overlapping subproblems.',
                            'ideal_answer': 'Algorithmic technique breaking problems into subproblems.'
                        }]
                    })
                }
            }]
        })

        mock_urlopen.side_effect = [gemini_err, openai_resp]

        result = failover.analyze_academic_exam_paper("Question 1: What is Dynamic Programming? [10 marks]")
        self.assertIn('questions', result)
        self.assertEqual(result['questions'][0]['question_number'], 'Q1')
        self.assertEqual(result['questions'][0]['prompt_text'], 'What is Dynamic Programming?')

    @patch('subprocess.run')
    def test_easyocr_subprocess_success(self, mock_subproc):
        from config.ocr_config import run_easyocr_isolated
        proc_mock = MagicMock()
        proc_mock.returncode = 0
        proc_mock.stdout = json.dumps({
            "success": True,
            "text": "Question 1: Explain Process Synchronization in Operating Systems. [10 marks]",
            "confidence": 0.89,
            "boxes": [{"bbox": [50, 50, 300, 100], "text": "Question 1"}]
        }).encode('utf-8')
        mock_subproc.return_value = proc_mock

        res = run_easyocr_isolated(b'fake_image_bytes')
        self.assertTrue(res['success'])
        self.assertIn('Process Synchronization', res['text'])
        self.assertEqual(res['confidence'], 0.89)

    @patch('subprocess.run')
    def test_easyocr_subprocess_timeout(self, mock_subproc):
        import subprocess
        from config.ocr_config import run_easyocr_isolated
        mock_subproc.side_effect = subprocess.TimeoutExpired(cmd=['python', 'runner.py'], timeout=15.0)

        res = run_easyocr_isolated(b'fake_image_bytes')
        self.assertFalse(res['success'])
        self.assertEqual(res['engine'], 'EasyOCR Subprocess Timeout')
        self.assertEqual(res['text'], '')

    @patch('subprocess.run')
    def test_easyocr_subprocess_sigill_simulation(self, mock_subproc):
        from config.ocr_config import run_easyocr_isolated
        proc_mock = MagicMock()
        proc_mock.returncode = -4  # SIGILL (Signal 4) - Illegal instruction
        proc_mock.stdout = b""
        proc_mock.stderr = b"Illegal instruction (core dumped)"
        mock_subproc.return_value = proc_mock

        res = run_easyocr_isolated(b'fake_image_bytes')
        self.assertFalse(res['success'])
        self.assertIn('code -4', res['engine'])
        self.assertEqual(res['text'], '')

    def test_multiple_figure_candidates_survive_into_final_figures(self):
        from core.ai_engine.document_service import DocumentService
        import numpy as np

        # Create two distinct figures in candidate union
        candidate_figs = [
            {
                "source": "figure",
                "element_type": "FIGURE",
                "page_number": 1,
                "caption": "Figure 1",
                "bounding_box": [50, 100, 250, 300], # Area 40000
                "image_path": "exam_figures/fig1.png"
            },
            {
                "source": "figure",
                "element_type": "FIGURE",
                "page_number": 1,
                "caption": "Figure 2",
                "bounding_box": [50, 400, 250, 600], # Area 40000, non-overlapping
                "image_path": "exam_figures/fig2.png"
            }
        ]

        nms_res = DocumentService.apply_nms_deduplication(candidate_figs, iou_threshold=0.50)
        self.assertEqual(len(nms_res['accepted']), 2)
        self.assertEqual(len(nms_res['rejected']), 0)

    def test_figure_question_spatial_mapping(self):
        from core.ai_engine.parser.academic_parser import AcademicParserService

        questions = [
            {"question_number": "Q1", "prompt_text": "Describe diagram below", "start_y": 200.0, "page_number": 1},
            {"question_number": "Q2", "prompt_text": "Explain next concept", "start_y": 800.0, "page_number": 1}
        ]

        figures = [
            {"page_number": 1, "bounding_box": [100, 300, 400, 600], "caption": "Figure 1"}
        ]

        mapped_q = AcademicParserService.associate_figures_with_questions(
            questions=questions,
            figures=figures,
            tables=[],
            formulas=[],
            dom_elements=[]
        )

        self.assertEqual(len(mapped_q[0]['associated_figures']), 1)
        self.assertEqual(mapped_q[0]['associated_figures'][0]['caption'], 'Figure 1')
        self.assertEqual(mapped_q[0]['associated_figures'][0]['owner_question'], 'Q1')
        self.assertEqual(len(mapped_q[1]['associated_figures']), 0)

    @patch('urllib.request.urlopen')
    def test_groq_vision_and_figure_payload(self, mock_urlopen):
        from core.ai_engine.providers.groq import GroqProvider
        groq = GroqProvider(api_key="test_groq_key")

        groq_resp = self._mock_http_response({
            'choices': [{
                'message': {
                    'content': json.dumps({
                        'questions': [{
                            'question_number': 'Q1',
                            'prompt_text': 'Explain diagram in Figure 1.',
                            'allocated_marks': 10.0,
                            'question_type': ['Theory'],
                            'command_verbs': ['Explain'],
                            'bloom_level': 'Understand',
                            'co_mapping': 'CO1',
                            'po_mapping': ['PO1'],
                            'criteria': 'Correct diagram analysis.',
                            'ideal_answer': 'Full analysis.'
                        }]
                    })
                }
            }]
        })
        mock_urlopen.return_value = groq_resp

        extra_figs = [{"caption": "Figure 1 Architecture Diagram", "page_number": 1}]
        res = groq.analyze_academic_exam_paper(
            "Question 1: Explain diagram in Figure 1. [10 marks]",
            image_bytes=b'fake_png_bytes',
            extra_files=extra_figs
        )
        self.assertIn('questions', res)
        self.assertEqual(res['questions'][0]['question_number'], 'Q1')

    @patch('urllib.request.urlopen')
    def test_openai_vision_and_figure_payload(self, mock_urlopen):
        from core.ai_engine.providers.openai import OpenAIProvider
        openai = OpenAIProvider(api_key="test_openai_key")

        openai_resp = self._mock_http_response({
            'choices': [{
                'message': {
                    'content': json.dumps({
                        'questions': [{
                            'question_number': 'Q1',
                            'prompt_text': 'Explain data flow in Figure 1.',
                            'allocated_marks': 10.0,
                            'question_type': ['Theory'],
                            'command_verbs': ['Explain'],
                            'bloom_level': 'Understand',
                            'co_mapping': 'CO1',
                            'po_mapping': ['PO1'],
                            'criteria': 'Correct data flow.',
                            'ideal_answer': 'Full answer.'
                        }]
                    })
                }
            }]
        })
        mock_urlopen.return_value = openai_resp

        extra_figs = [{"caption": "Figure 1 Flowchart", "page_number": 1}]
        res = openai.analyze_academic_exam_paper(
            "Question 1: Explain data flow in Figure 1. [10 marks]",
            image_bytes=b'fake_png_bytes',
            extra_files=extra_figs
        )
        self.assertIn('questions', res)
        self.assertEqual(res['questions'][0]['question_number'], 'Q1')


class AnswerCropServiceTestCase(TestCase):
    """Regression test suite for robust answer region image cropping and coordinate normalization."""

    def setUp(self):
        import numpy as np
        import cv2
        import tempfile

        self.temp_dir = tempfile.mkdtemp()
        self.synth_page = np.full((2000, 1000, 3), 255, dtype=np.uint8)
        cv2.putText(self.synth_page, 'Top Question 1', (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
        cv2.putText(self.synth_page, 'Student Handwritten Body', (50, 1000), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 180), 2)
        cv2.putText(self.synth_page, 'Bottom Question 2', (50, 1900), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

        self.page_path = os.path.join(self.temp_dir, 'synth_page_1.png')
        cv2.imwrite(self.page_path, self.synth_page)

        self.synth_page_2 = np.full((2000, 1000, 3), 240, dtype=np.uint8)
        cv2.putText(self.synth_page_2, 'Continuation Page 2', (50, 500), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 180), 2)
        self.page_2_path = os.path.join(self.temp_dir, 'synth_page_2.png')
        cv2.imwrite(self.page_2_path, self.synth_page_2)

    def tearDown(self):
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_normal_single_page_answer_crop(self):
        from core.ai_engine.evaluation.answer_crop_service import AnswerCropService
        regions = [{
            'page_number': 1,
            'region_id': 'p1_r1',
            'bbox': {'ymin': 0.10, 'xmin': 0.0, 'ymax': 0.60, 'xmax': 1.0}
        }]
        crops = AnswerCropService.extract_answer_region_crops(self.page_path, regions, min_crop_height_px=100)
        self.assertEqual(len(crops), 1)
        c = crops[0]
        self.assertEqual(c['page_number'], 1)
        self.assertEqual(c['crop_width'], 1000)
        self.assertEqual(c['crop_height'], 1000)
        self.assertGreater(len(c['image_bytes']), 1000)
        self.assertEqual(c['mime_type'], 'image/png')

    def test_zero_height_bbox_recovery(self):
        from core.ai_engine.evaluation.answer_crop_service import AnswerCropService
        regions = [{
            'page_number': 1,
            'region_id': 'p1_r_degenerate',
            'bbox': {'ymin': 0.20, 'xmin': 0.0, 'ymax': 0.20, 'xmax': 1.0}
        }]
        crops = AnswerCropService.extract_answer_region_crops(self.page_path, regions, min_crop_height_px=100)
        self.assertEqual(len(crops), 1)
        c = crops[0]
        self.assertGreaterEqual(c['crop_height'], 100)
        self.assertGreater(len(c['image_bytes']), 500)

    def test_out_of_range_bbox_clamping(self):
        from core.ai_engine.evaluation.answer_crop_service import AnswerCropService
        regions = [{
            'page_number': 1,
            'region_id': 'p1_r_out_of_range',
            'bbox': {'ymin': -0.5, 'xmin': -0.2, 'ymax': 1.8, 'xmax': 1.5}
        }]
        crops = AnswerCropService.extract_answer_region_crops(self.page_path, regions, min_crop_height_px=100)
        self.assertEqual(len(crops), 1)
        c = crops[0]
        self.assertEqual(c['crop_width'], 1000)
        self.assertEqual(c['crop_height'], 2000)
        self.assertEqual(c['bbox']['ymin'], 0.0)
        self.assertEqual(c['bbox']['ymax'], 1.0)
        self.assertEqual(c['bbox']['xmin'], 0.0)
        self.assertEqual(c['bbox']['xmax'], 1.0)

    def test_multi_page_answer_sequence_preservation(self):
        from core.ai_engine.evaluation.answer_crop_service import AnswerCropService
        from core.models import StudentSubmission, SubmissionPage, QuestionMapping, Question, Examination, Department, Course

        dept = Department.objects.create(name='Test Dept Crop', code='TDC')
        course = Course.objects.create(code='TDC101', title='Test Course Crop', department=dept)
        exam = Examination.objects.create(course=course, title='Test Exam Crop', exam_date='2026-01-01', total_marks=100.0)
        q = Question.objects.create(examination=exam, question_number='1', prompt_text='Test Q', max_marks=20.0)
        sub = StudentSubmission.objects.create(examination=exam, student_name='Test Student Crop')

        sp1 = SubmissionPage.objects.create(submission=sub, page_number=1, working_image_path=self.page_path)
        sp2 = SubmissionPage.objects.create(submission=sub, page_number=2, working_image_path=self.page_2_path)

        q_map = QuestionMapping.objects.create(
            submission=sub,
            question=q,
            page_numbers_json=[1, 2],
            regions_json=[
                {'page_number': 1, 'region_id': 'p1_r1', 'bbox': {'ymin': 0.30, 'xmin': 0.0, 'ymax': 1.0, 'xmax': 1.0}},
                {'page_number': 2, 'region_id': 'p2_r1', 'bbox': {'ymin': 0.0, 'xmin': 0.0, 'ymax': 0.70, 'xmax': 1.0}}
            ]
        )

        crops = AnswerCropService.extract_crops_for_question(sub, q_map, min_crop_height_px=100)
        self.assertEqual(len(crops), 2)
        self.assertEqual(crops[0]['page_number'], 1)
        self.assertEqual(crops[0]['crop_height'], 1400)
        self.assertEqual(crops[1]['page_number'], 2)
        self.assertEqual(crops[1]['crop_height'], 1400)
        self.assertGreater(len(crops[0]['image_bytes']), 1000)
        self.assertGreater(len(crops[1]['image_bytes']), 1000)

    def test_question_heading_at_bottom_of_page(self):
        from core.ai_engine.evaluation.answer_crop_service import AnswerCropService
        regions = [{
            'page_number': 1,
            'region_id': 'p1_r_bottom',
            'bbox': {'ymin': 0.98, 'xmin': 0.0, 'ymax': 1.0, 'xmax': 1.0}
        }]
        crops = AnswerCropService.extract_answer_region_crops(self.page_path, regions, min_crop_height_px=100)
        self.assertEqual(len(crops), 1)
        c = crops[0]
        self.assertGreaterEqual(c['crop_height'], 100)
        self.assertGreater(len(c['image_bytes']), 500)

    def test_no_empty_crop_returned_on_missing_or_invalid_regions(self):
        from core.ai_engine.evaluation.answer_crop_service import AnswerCropService
        crops_empty_regions = AnswerCropService.extract_answer_region_crops(self.page_path, [], min_crop_height_px=100)
        self.assertEqual(len(crops_empty_regions), 1)
        self.assertEqual(crops_empty_regions[0]['crop_height'], 2000)
        self.assertGreater(len(crops_empty_regions[0]['image_bytes']), 1000)




