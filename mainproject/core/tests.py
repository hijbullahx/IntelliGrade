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

    @patch('core.ai_engine.routine_parser.routine_parser.RoutineParser.parse_routine')
    def test_scan_routine_ai_nazir_ahmed_fuzzy_matching_and_reassign(self, mock_parse):
        # Create a teacher named 'Nazir Ahmed'
        nazir_user = User.objects.create_user(
            username='nazir_ahmed',
            password='testpassword123',
            first_name='Nazir',
            last_name='Ahmed'
        )
        Profile.objects.create(user=nazir_user, role=Profile.Role.TEACHER, department=self.dept)

        # Mock routine parser with title prefixed faculty name 'Engr. Nazir Ahmed'
        mock_parse.return_value = {
            'routine_schedule': [
                {
                    'course_code': 'CSE 411',
                    'course_title': 'Software Engineering',
                    'exam_date': '2026-08-15',
                    'exam_time': '10:00 AM - 01:00 PM',
                    'faculty_name': 'Engr. Nazir Ahmed'
                }
            ]
        }
        self.client.login(username='controller_admin', password='testpassword123')
        response = self.client.post(reverse('scan_routine_ai'), {'routine_text': 'CSE 411 Software Engineering Engr. Nazir Ahmed'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        item = data['routine_items'][0]
        self.assertTrue(item['faculty_found'])
        self.assertEqual(item['faculty_id'], nazir_user.id)

        # Test assigning and publishing with custom faculty selection
        publish_res = self.client.post(reverse('api_publish_exam'), {
            'course_id': self.course.id,
            'faculty_id': nazir_user.id,
            'exam_date': '2026-08-15',
            'total_marks': 100.0,
            'title': 'CSE 411 Final Exam'
        })
        self.assertEqual(publish_res.status_code, 200)
        pub_data = publish_res.json()
        self.assertTrue(pub_data['success'])
        self.assertEqual(pub_data['faculty_id'], nazir_user.id)

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
        from core.models import AIProviderHealth
        AIProviderHealth.objects.all().delete()

        from core.ai_engine.providers.gemini import GeminiProvider
        from core.ai_engine.providers.groq import GroqProvider
        from core.ai_engine.providers.failover import FailoverAIProvider
        from core.ai_engine.routing.task_router import ProviderHealthTracker
        ProviderHealthTracker.clear_cooldowns()
        self.gemini = GeminiProvider(api_key="test_gemini_key")
        self.groq = GroqProvider(api_key="test_groq_key")
        self.failover_provider = FailoverAIProvider(primary_provider=self.gemini)
        # Explicitly configure chain with Gemini -> Groq
        self.failover_provider._chain = [self.gemini, self.groq]

    def tearDown(self):
        from core.ai_engine.routing.task_router import ProviderHealthTracker
        ProviderHealthTracker.clear_cooldowns()

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

        result = self.failover_provider.analyze_academic_exam_paper("Question 1: Explain Software Design Patterns. [10 marks]", image_bytes=b'fake_png')
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

        result = self.failover_provider.analyze_academic_exam_paper("Question 1: Derive the quadratic formula. [15 marks]", image_bytes=b'fake_png')
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

        result = self.failover_provider.analyze_academic_exam_paper("Question 1: Explain Database Normalization. [20 marks]", image_bytes=b'fake_png')
        self.assertIn('questions', result)
        self.assertEqual(result['questions'][0]['question_number'], 'Q1')

    def test_vision_and_text_failover_chain_order(self):
        from core.ai_engine.providers.gemini import GeminiProvider
        from core.ai_engine.providers.groq import GroqProvider
        from core.ai_engine.providers.openai import OpenAIProvider
        from core.ai_engine.providers.ollama import OllamaProvider
        from core.ai_engine.providers.failover import FailoverAIProvider

        gemini = GeminiProvider(api_key="gemini_key")
        groq = GroqProvider(api_key="groq_key")
        openai = OpenAIProvider(api_key="openai_key")
        ollama = OllamaProvider()

        failover = FailoverAIProvider(primary_provider=gemini)

        # Vision chain order: Gemini -> Groq -> OpenAI (Ollama excluded)
        vision_chain = failover._get_execution_chain(has_images=True)
        vision_types = [p.__class__ for p in vision_chain]
        self.assertTrue(GeminiProvider in vision_types and GroqProvider in vision_types and OpenAIProvider in vision_types and OllamaProvider not in vision_types)

        # Text chain: must include Groq, Gemini, OpenAI, Ollama (OpenRouter may also be present)
        text_chain = failover._get_execution_chain(has_images=False)
        text_types = [p.__class__ for p in text_chain]
        self.assertIn(GroqProvider, text_types)
        self.assertIn(GeminiProvider, text_types)
        self.assertIn(OpenAIProvider, text_types)
        self.assertIn(OllamaProvider, text_types)
        # Groq must come before Gemini which must come before OpenAI
        self.assertLess(text_types.index(GroqProvider), text_types.index(GeminiProvider))
        self.assertLess(text_types.index(GeminiProvider), text_types.index(OpenAIProvider))

    def test_provider_capability_declarations(self):
        from core.ai_engine.providers.gemini import GeminiProvider
        from core.ai_engine.providers.groq import GroqProvider
        from core.ai_engine.providers.openai import OpenAIProvider
        from core.ai_engine.providers.ollama import OllamaProvider

        self.assertTrue(GroqProvider(api_key="k").get_capabilities()['supports_images'])
        self.assertTrue(GeminiProvider(api_key="k").get_capabilities()['supports_images'])
        self.assertTrue(OpenAIProvider(api_key="k").get_capabilities()['supports_images'])
        self.assertFalse(OllamaProvider().get_capabilities()['supports_images'])

    def test_groq_vision_and_text_model_selection(self):
        from core.ai_engine.providers.groq import GroqProvider
        groq = GroqProvider(api_key="test_key")
        self.assertEqual(groq.model_name, "qwen/qwen3.6-27b")

        with patch('urllib.request.urlopen') as mock_url:
            mock_url.return_value = self._mock_http_response({'choices': [{'message': {'content': 'ok'}}]})
            groq.generate_completion("Text prompt")
            req = mock_url.call_args[0][0]
            payload = json.loads(req.data.decode('utf-8'))
            self.assertEqual(payload['model'], 'qwen/qwen3.6-27b')

        with patch('urllib.request.urlopen') as mock_url:
            mock_url.return_value = self._mock_http_response({'choices': [{'message': {'content': 'ok'}}]})
            groq.generate_completion("Vision prompt", image_bytes=b'fake_bytes')
            req = mock_url.call_args[0][0]
            payload = json.loads(req.data.decode('utf-8'))
            self.assertEqual(payload['model'], 'qwen/qwen3.6-27b')

    def test_groq_sanitize_thinking_output(self):
        import re
        from core.ai_engine.providers.groq import GroqProvider

        # a. response with <think>...</think>
        resp_a = "<think>\nThinking process...\n</think>\nINTELLIGRADE_GROQ_QWEN_OK"
        self.assertEqual(GroqProvider.sanitize_thinking_output(resp_a), "INTELLIGRADE_GROQ_QWEN_OK")

        # b. response without think tags
        resp_b = "INTELLIGRADE_GROQ_QWEN_OK"
        self.assertEqual(GroqProvider.sanitize_thinking_output(resp_b), "INTELLIGRADE_GROQ_QWEN_OK")

        # c. malformed/missing closing tag
        resp_c = "<think>\nUnclosed thinking block without closing tag"
        self.assertEqual(GroqProvider.sanitize_thinking_output(resp_c), "")

        # d. JSON wrapped after a think block
        resp_d = "<think>\nAnalyzing JSON...\n</think>\n```json\n{\"status\": \"OK\"}\n```"
        sanitized_d = GroqProvider.sanitize_thinking_output(resp_d)
        cleaned_json = re.sub(r'```json\s*', '', sanitized_d)
        cleaned_json = re.sub(r'```\s*', '', cleaned_json).strip()
        parsed = json.loads(cleaned_json)
        self.assertEqual(parsed.get('status'), 'OK')

        # e. empty response after sanitization
        resp_e = "<think>only thinking process</think>"
        self.assertEqual(GroqProvider.sanitize_thinking_output(resp_e), "")

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

            self.assertLess(elapsed, 4.0) # Total execution finished rapidly
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

        # Gemini fails on both candidate models with 500, OpenAI succeeds
        err1 = urllib.error.HTTPError("https://generativelanguage.googleapis.com", 500, "Internal Server Error", {}, io.BytesIO(b'{"error":{"message":"Internal Server Error"}}'))
        err2 = urllib.error.HTTPError("https://generativelanguage.googleapis.com", 500, "Internal Server Error", {}, io.BytesIO(b'{"error":{"message":"Internal Server Error"}}'))

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

        mock_urlopen.side_effect = [err1, err2, openai_resp]

        result = failover.analyze_academic_exam_paper("Question 1: What is Dynamic Programming? [10 marks]", image_bytes=b'fake_png')
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


class MultimodalVisualEvaluationTestCase(TestCase):
    """Regression test suite for isolated multimodal visual answer evaluation and safe fallbacks."""

    def setUp(self):
        import numpy as np
        import cv2
        import tempfile
        from core.models import Department, Course, Examination, Question, StudentSubmission, SubmissionPage, SubmissionAnswer, QuestionMapping

        self.temp_dir = tempfile.mkdtemp()
        self.synth_page = np.full((1200, 800, 3), 255, dtype=np.uint8)
        cv2.putText(self.synth_page, 'Handwritten Q1 Work', (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
        self.page_1_path = os.path.join(self.temp_dir, 'page_1.png')
        cv2.imwrite(self.page_1_path, self.synth_page)

        self.synth_page_2 = np.full((1200, 800, 3), 245, dtype=np.uint8)
        cv2.putText(self.synth_page_2, 'Handwritten Q1 Continued', (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
        self.page_2_path = os.path.join(self.temp_dir, 'page_2.png')
        cv2.imwrite(self.page_2_path, self.synth_page_2)

        self.dept = Department.objects.create(name='Computer Science', code='CSE')
        self.course = Course.objects.create(code='CSE4385', title='Software Testing', department=self.dept)
        self.exam = Examination.objects.create(course=self.course, title='Midterm Exam', exam_date='2026-08-15', total_marks=100.0)
        self.question = Question.objects.create(
            examination=self.exam,
            question_number='1',
            prompt_text='Explain Dynamic Programming and state the Bellman Equation.',
            max_marks=10.0
        )
        self.submission = StudentSubmission.objects.create(examination=self.exam, student_name='Alice Student')
        self.sp1 = SubmissionPage.objects.create(submission=self.submission, page_number=1, working_image_path=self.page_1_path)
        self.sp2 = SubmissionPage.objects.create(submission=self.submission, page_number=2, working_image_path=self.page_2_path)
        self.answer = SubmissionAnswer.objects.create(
            submission=self.submission,
            question=self.question,
            extracted_text='Dynamic programming breaks down problems into subproblems.'
        )

    def tearDown(self):
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch('core.ai_engine.providers.factory.AIProviderFactory.get_provider')
    def test_single_image_crop_multimodal_evaluation_called(self, mock_get_provider):
        from core.models import QuestionMapping
        from core.ai_engine.evaluation.script_evaluator import AIScriptEvaluator

        QuestionMapping.objects.create(
            submission=self.submission,
            question=self.question,
            page_numbers_json=[1],
            regions_json=[{'page_number': 1, 'region_id': 'p1_r1', 'bbox': {'ymin': 0.1, 'xmin': 0.0, 'ymax': 0.8, 'xmax': 1.0}}]
        )

        mock_provider = MagicMock()
        mock_provider.__class__.__name__ = 'GeminiProvider'
        mock_provider.generate_completion.return_value = json.dumps({
            "question_id": str(self.question.id),
            "obtained_marks": 8.5,
            "maximum_marks": 10.0,
            "percentage": 85.0,
            "strengths": ["Clear Bellman equation"],
            "mistakes": [],
            "missing_points": [],
            "expected_points": ["Optimal substructure"],
            "rubric_breakdown": [{"criteria": "Concept", "allocated": 10.0, "awarded": 8.5, "comments": "Good"}],
            "feedback": "Well written solution.",
            "confidence": 0.92,
            "requires_manual_review": False
        })
        mock_get_provider.return_value = mock_provider

        res = AIScriptEvaluator._evaluate_answer_v3(self.answer, options={'strictness': 'Balanced'})
        self.assertEqual(res.obtained_marks, 8.5)
        self.assertEqual(res.maximum_marks, 10.0)
        self.assertFalse(res.requires_manual_review)
        self.assertEqual(res.confidence, 0.92)

        # Verify image_bytes was passed
        mock_provider.generate_completion.assert_called()
        call_kwargs = mock_provider.generate_completion.call_args[1]
        self.assertIsNotNone(call_kwargs.get('image_bytes'))
        self.assertGreater(len(call_kwargs['image_bytes']), 100)

    @patch('core.ai_engine.providers.factory.AIProviderFactory.get_provider')
    def test_multi_page_answer_multiple_images_sent(self, mock_get_provider):
        from core.models import QuestionMapping
        from core.ai_engine.evaluation.script_evaluator import AIScriptEvaluator

        QuestionMapping.objects.create(
            submission=self.submission,
            question=self.question,
            page_numbers_json=[1, 2],
            regions_json=[
                {'page_number': 1, 'region_id': 'p1_r1', 'bbox': {'ymin': 0.2, 'xmin': 0.0, 'ymax': 1.0, 'xmax': 1.0}},
                {'page_number': 2, 'region_id': 'p2_r1', 'bbox': {'ymin': 0.0, 'xmin': 0.0, 'ymax': 0.5, 'xmax': 1.0}}
            ]
        )

        mock_provider = MagicMock()
        mock_provider.__class__.__name__ = 'GeminiProvider'
        mock_provider.generate_completion.return_value = json.dumps({
            "question_id": str(self.question.id),
            "obtained_marks": 9.0,
            "maximum_marks": 10.0,
            "feedback": "Complete 2-page answer.",
            "confidence": 0.95,
            "requires_manual_review": False
        })
        mock_get_provider.return_value = mock_provider

        res = AIScriptEvaluator._evaluate_answer_v3(self.answer, options={})
        self.assertEqual(res.obtained_marks, 9.0)

        call_kwargs = mock_provider.generate_completion.call_args[1]
        self.assertIsNotNone(call_kwargs.get('image_bytes'))
        self.assertIsNotNone(call_kwargs.get('extra_files'))
        self.assertEqual(len(call_kwargs['extra_files']), 1)
        self.assertEqual(call_kwargs['extra_files'][0]['page_number'], 2)

    @patch('core.ai_engine.providers.factory.AIProviderFactory.get_provider')
    def test_vision_provider_receives_image_payload(self, mock_get_provider):
        from core.models import QuestionMapping
        from core.ai_engine.evaluation.script_evaluator import AIScriptEvaluator

        QuestionMapping.objects.create(
            submission=self.submission,
            question=self.question,
            page_numbers_json=[1],
            regions_json=[{'page_number': 1, 'region_id': 'p1_r1', 'bbox': {'ymin': 0.0, 'xmin': 0.0, 'ymax': 1.0, 'xmax': 1.0}}]
        )

        mock_provider = MagicMock()
        mock_provider.__class__.__name__ = 'GroqProvider'
        mock_provider.generate_completion.return_value = json.dumps({
            "obtained_marks": 7.0,
            "feedback": "Correct overview.",
            "confidence": 0.88,
            "requires_manual_review": False
        })
        mock_get_provider.return_value = mock_provider

        res = AIScriptEvaluator._evaluate_answer_v3(self.answer, options={})
        self.assertEqual(res.obtained_marks, 7.0)
        call_kwargs = mock_provider.generate_completion.call_args[1]
        self.assertIn('image_bytes', call_kwargs)
        self.assertEqual(call_kwargs.get('mime_type'), 'image/png')

    def test_ollama_is_skipped_for_image_evaluation(self):
        from core.ai_engine.providers.failover import FailoverAIProvider
        from core.ai_engine.providers.gemini import GeminiProvider
        from core.ai_engine.providers.ollama import OllamaProvider

        gemini_mock = MagicMock(spec=GeminiProvider)
        gemini_mock.get_capabilities.return_value = {'supports_images': True, 'supports_text': True}
        gemini_mock.generate_completion.return_value = '{"obtained_marks": 8.0, "feedback": "Valid", "confidence": 0.90}'

        ollama_mock = MagicMock(spec=OllamaProvider)
        ollama_mock.get_capabilities.return_value = {'supports_images': False, 'supports_text': True}

        failover = FailoverAIProvider(primary_provider=gemini_mock)
        failover._chain = [ollama_mock, gemini_mock]

        res = failover.generate_completion("Test prompt", image_bytes=b'fake_png_data')
        # Ollama must not have been called because it lacks supports_images
        ollama_mock.generate_completion.assert_not_called()
        gemini_mock.generate_completion.assert_called_once()

    @patch('core.ai_engine.providers.factory.AIProviderFactory.get_provider')
    def test_all_vision_providers_fail_text_fallback(self, mock_get_provider):
        from core.models import QuestionMapping
        from core.ai_engine.evaluation.script_evaluator import AIScriptEvaluator

        QuestionMapping.objects.create(
            submission=self.submission,
            question=self.question,
            page_numbers_json=[1],
            regions_json=[{'page_number': 1, 'region_id': 'p1_r1', 'bbox': {'ymin': 0.0, 'xmin': 0.0, 'ymax': 1.0, 'xmax': 1.0}}]
        )

        mock_provider = MagicMock()
        mock_provider.__class__.__name__ = 'FailoverAIProvider'

        # First call (vision with image_bytes) fails; second call (text-only) succeeds
        def side_effect(*args, **kwargs):
            if kwargs.get('image_bytes'):
                raise Exception("Vision quota exhausted on all vision providers")
            return json.dumps({
                "obtained_marks": 6.0,
                "feedback": "Evaluated via text-only fallback.",
                "confidence": 0.75,
                "requires_manual_review": False
            })

        mock_provider.generate_completion.side_effect = side_effect
        mock_get_provider.return_value = mock_provider

        res = AIScriptEvaluator._evaluate_answer_v3(self.answer, options={})
        self.assertEqual(res.obtained_marks, 6.0)
        # Because visual grading was unavailable, manual review is flagged
        self.assertTrue(res.requires_manual_review)

    @patch('core.ai_engine.providers.factory.AIProviderFactory.get_provider')
    def test_no_crop_text_fallback_with_manual_review(self, mock_get_provider):
        from core.ai_engine.evaluation.script_evaluator import AIScriptEvaluator

        # No QuestionMapping exists for this question
        mock_provider = MagicMock()
        mock_provider.__class__.__name__ = 'GroqProvider'
        mock_provider.generate_completion.return_value = json.dumps({
            "obtained_marks": 7.5,
            "feedback": "Text-only evaluation.",
            "confidence": 0.80,
            "requires_manual_review": False
        })
        mock_get_provider.return_value = mock_provider

        res = AIScriptEvaluator._evaluate_answer_v3(self.answer, options={})
        self.assertEqual(res.obtained_marks, 7.5)
        # Requires manual review because no image crop was available
        self.assertTrue(res.requires_manual_review)

    @patch('core.ai_engine.providers.factory.AIProviderFactory.get_provider')
    def test_score_is_clamped_to_max_marks(self, mock_get_provider):
        from core.ai_engine.evaluation.script_evaluator import AIScriptEvaluator

        mock_provider = MagicMock()
        mock_provider.__class__.__name__ = 'GeminiProvider'
        # Return 25.0 marks for a 10.0 max mark question
        mock_provider.generate_completion.return_value = json.dumps({
            "obtained_marks": 25.0,
            "feedback": "Overly generous AI.",
            "confidence": 0.90,
            "requires_manual_review": False
        })
        mock_get_provider.return_value = mock_provider
    @patch('core.ai_engine.providers.factory.AIProviderFactory.get_provider')
    def test_score_is_clamped_to_max_marks(self, mock_get_provider):
        from core.ai_engine.evaluation.script_evaluator import AIScriptEvaluator

        mock_provider = MagicMock()
        mock_provider.__class__.__name__ = 'GeminiProvider'
        # Return 25.0 marks for a 10.0 max mark question
        mock_provider.generate_completion.return_value = json.dumps({
            "obtained_marks": 25.0,
            "feedback": "Overly generous AI.",
            "confidence": 0.90,
            "requires_manual_review": False
        })
        mock_get_provider.return_value = mock_provider

        res = AIScriptEvaluator._evaluate_answer_v3(self.answer, options={})
        self.assertEqual(res.obtained_marks, 10.0)  # Clamped strictly to max_marks
        self.assertEqual(res.percentage, 100.0)

    @patch('core.ai_engine.providers.factory.AIProviderFactory.get_provider')
    def test_low_confidence_flags_manual_review(self, mock_get_provider):
        from core.models import QuestionMapping
        from core.ai_engine.evaluation.script_evaluator import AIScriptEvaluator

        QuestionMapping.objects.create(
            submission=self.submission,
            question=self.question,
            page_numbers_json=[1],
            regions_json=[{'page_number': 1, 'region_id': 'p1_r1', 'bbox': {'ymin': 0.0, 'xmin': 0.0, 'ymax': 1.0, 'xmax': 1.0}}]
        )

        mock_provider = MagicMock()
        mock_provider.__class__.__name__ = 'GeminiProvider'
        mock_provider.generate_completion.return_value = json.dumps({
            "obtained_marks": 4.0,
            "feedback": "Handwriting is partially unreadable.",
            "confidence": 0.45,
            "requires_manual_review": False
        })
        mock_get_provider.return_value = mock_provider

        res = AIScriptEvaluator._evaluate_answer_v3(self.answer, options={})
        self.assertEqual(res.obtained_marks, 4.0)
        self.assertEqual(res.confidence, 0.45)
        self.assertTrue(res.requires_manual_review)  # Low confidence (< 0.70) forces manual review


class VisualGradingCalibrationTestCase(TestCase):
    """Unit tests verifying rubric-grounded visual grading calibration across 7 required evaluation scenarios."""

    def setUp(self):
        import numpy as np
        import cv2
        import tempfile
        from core.models import Department, Course, Examination, Question, StudentSubmission, SubmissionPage, SubmissionAnswer, QuestionMapping, Rubric

        self.temp_dir = tempfile.mkdtemp()
        self.synth_page = np.full((1200, 800, 3), 255, dtype=np.uint8)
        cv2.putText(self.synth_page, 'Handwritten Q4 Work', (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
        self.page_path = os.path.join(self.temp_dir, 'page_1.png')
        cv2.imwrite(self.page_path, self.synth_page)

        self.dept = Department.objects.create(name='CS Dept', code='CSD')
        self.course = Course.objects.create(code='CSE4383', title='Digital Image Processing', department=self.dept)
        self.exam = Examination.objects.create(course=self.course, title='DIP Final Exam', exam_date='2026-08-15', total_marks=100.0)
        self.question = Question.objects.create(
            examination=self.exam,
            question_number='4',
            prompt_text='Explain image transformation, scaling, and feature selection steps.',
            max_marks=25.0
        )
        Rubric.objects.create(
            question=self.question,
            criteria='1. Image Transformation (10m)\n2. Feature Selection Steps (10m)\n3. Numerical Scaling (5m)',
            ideal_answer='Correct transformation matrix, 5-step feature selection, and normalized scaling [0,1].',
            alternative_answers='Valid matrix translation or PCA feature reduction method.',
            common_mistakes=['Missing scaling normalization step']
        )
        self.submission = StudentSubmission.objects.create(examination=self.exam, student_name='Calibrated Student')
        self.sp1 = SubmissionPage.objects.create(submission=self.submission, page_number=1, working_image_path=self.page_path)
        self.answer = SubmissionAnswer.objects.create(
            submission=self.submission,
            question=self.question,
            extracted_text='Image transformation and scaling equations.'
        )
        QuestionMapping.objects.create(
            submission=self.submission,
            question=self.question,
            page_numbers_json=[1],
            regions_json=[{'page_number': 1, 'region_id': 'p1_r1', 'bbox': {'ymin': 0.0, 'xmin': 0.0, 'ymax': 1.0, 'xmax': 1.0}}]
        )

    def tearDown(self):
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch('core.ai_engine.providers.factory.AIProviderFactory.get_provider')
    def test_full_correct_answer_calibration(self, mock_get_provider):
        from core.ai_engine.evaluation.script_evaluator import AIScriptEvaluator

        mock_provider = MagicMock()
        mock_provider.generate_completion.return_value = json.dumps({
            "obtained_marks": 25.0,
            "maximum_marks": 25.0,
            "rubric_breakdown": [
                {"criteria": "Image Transformation", "allocated": 10.0, "awarded": 10.0, "evidence_found": "Complete transformation matrix shown."},
                {"criteria": "Feature Selection Steps", "allocated": 10.0, "awarded": 10.0, "evidence_found": "All 5 feature steps listed correctly."},
                {"criteria": "Numerical Scaling", "allocated": 5.0, "awarded": 5.0, "evidence_found": "Scaling normalized between 0 and 1."}
            ],
            "feedback": "Perfect solution.",
            "confidence": 0.95,
            "requires_manual_review": False
        })
        mock_get_provider.return_value = mock_provider

        res = AIScriptEvaluator._evaluate_answer_v3(self.answer, options={})
        self.assertEqual(res.obtained_marks, 25.0)
        self.assertEqual(res.percentage, 100.0)
        self.assertEqual(res.confidence, 0.95)
        self.assertFalse(res.requires_manual_review)

    @patch('core.ai_engine.providers.factory.AIProviderFactory.get_provider')
    def test_mostly_correct_with_minor_omission(self, mock_get_provider):
        from core.ai_engine.evaluation.script_evaluator import AIScriptEvaluator

        mock_provider = MagicMock()
        mock_provider.generate_completion.return_value = json.dumps({
            "obtained_marks": 22.0,
            "maximum_marks": 25.0,
            "rubric_breakdown": [
                {"criteria": "Image Transformation", "allocated": 10.0, "awarded": 10.0, "evidence_found": "Complete matrix."},
                {"criteria": "Feature Selection Steps", "allocated": 10.0, "awarded": 8.0, "evidence_found": "4 of 5 steps shown.", "missing_or_incorrect": "Step 5 omitted."},
                {"criteria": "Numerical Scaling", "allocated": 5.0, "awarded": 4.0, "evidence_found": "Scaling calculation completed."}
            ],
            "feedback": "Mostly correct with minor step omission.",
            "confidence": 0.90,
            "requires_manual_review": False
        })
        mock_get_provider.return_value = mock_provider

        res = AIScriptEvaluator._evaluate_answer_v3(self.answer, options={})
        self.assertEqual(res.obtained_marks, 22.0)
        self.assertEqual(res.percentage, 88.0)
        self.assertFalse(res.requires_manual_review)

    @patch('core.ai_engine.providers.factory.AIProviderFactory.get_provider')
    def test_partially_correct_answer(self, mock_get_provider):
        from core.ai_engine.evaluation.script_evaluator import AIScriptEvaluator

        mock_provider = MagicMock()
        mock_provider.generate_completion.return_value = json.dumps({
            "obtained_marks": 12.0,
            "maximum_marks": 25.0,
            "rubric_breakdown": [
                {"criteria": "Image Transformation", "allocated": 10.0, "awarded": 6.0, "evidence_found": "Partial matrix derivation."},
                {"criteria": "Feature Selection Steps", "allocated": 10.0, "awarded": 4.0, "evidence_found": "2 steps listed."},
                {"criteria": "Numerical Scaling", "allocated": 5.0, "awarded": 2.0, "evidence_found": "Formula stated without calculation."}
            ],
            "feedback": "Partial credit awarded for core concepts.",
            "confidence": 0.85,
            "requires_manual_review": False
        })
        mock_get_provider.return_value = mock_provider

        res = AIScriptEvaluator._evaluate_answer_v3(self.answer, options={})
        self.assertEqual(res.obtained_marks, 12.0)
        self.assertEqual(res.percentage, 48.0)

    @patch('core.ai_engine.providers.factory.AIProviderFactory.get_provider')
    def test_wrong_answer(self, mock_get_provider):
        from core.ai_engine.evaluation.script_evaluator import AIScriptEvaluator

        mock_provider = MagicMock()
        mock_provider.generate_completion.return_value = json.dumps({
            "obtained_marks": 0.0,
            "maximum_marks": 25.0,
            "rubric_breakdown": [
                {"criteria": "Image Transformation", "allocated": 10.0, "awarded": 0.0, "missing_or_incorrect": "Irrelevant text."},
                {"criteria": "Feature Selection Steps", "allocated": 10.0, "awarded": 0.0, "missing_or_incorrect": "Incorrect concepts."},
                {"criteria": "Numerical Scaling", "allocated": 5.0, "awarded": 0.0, "missing_or_incorrect": "No scaling shown."}
            ],
            "feedback": "Answer does not address question.",
            "confidence": 0.90,
            "requires_manual_review": False
        })
        mock_get_provider.return_value = mock_provider

        res = AIScriptEvaluator._evaluate_answer_v3(self.answer, options={})
        self.assertEqual(res.obtained_marks, 0.0)
        self.assertEqual(res.percentage, 0.0)

    @patch('core.ai_engine.providers.factory.AIProviderFactory.get_provider')
    def test_correct_alternative_method(self, mock_get_provider):
        from core.ai_engine.evaluation.script_evaluator import AIScriptEvaluator

        mock_provider = MagicMock()
        mock_provider.generate_completion.return_value = json.dumps({
            "obtained_marks": 25.0,
            "maximum_marks": 25.0,
            "rubric_breakdown": [
                {"criteria": "Alternative Approach", "allocated": 25.0, "awarded": 25.0, "evidence_found": "Valid PCA feature reduction alternative approach."}
            ],
            "feedback": "Valid alternative solution.",
            "confidence": 0.92,
            "requires_manual_review": False
        })
        mock_get_provider.return_value = mock_provider

        res = AIScriptEvaluator._evaluate_answer_v3(self.answer, options={})
        self.assertEqual(res.obtained_marks, 25.0)
        self.assertEqual(res.percentage, 100.0)

    @patch('core.ai_engine.providers.factory.AIProviderFactory.get_provider')
    def test_incomplete_image_triggers_manual_review(self, mock_get_provider):
        from core.ai_engine.evaluation.script_evaluator import AIScriptEvaluator

        mock_provider = MagicMock()
        mock_provider.generate_completion.return_value = json.dumps({
            "obtained_marks": 10.0,
            "maximum_marks": 25.0,
            "rubric_breakdown": [
                {"criteria": "Image Transformation", "allocated": 10.0, "awarded": 10.0, "evidence_found": "Top derivation visible."}
            ],
            "feedback": "Lower half of answer crop cut off.",
            "confidence": 0.50,
            "requires_manual_review": True
        })
        mock_get_provider.return_value = mock_provider

        res = AIScriptEvaluator._evaluate_answer_v3(self.answer, options={})
        self.assertTrue(res.requires_manual_review)
        self.assertEqual(res.confidence, 0.50)

    @patch('core.ai_engine.providers.factory.AIProviderFactory.get_provider')
    def test_low_confidence_case_triggers_manual_review(self, mock_get_provider):
        from core.ai_engine.evaluation.script_evaluator import AIScriptEvaluator

        mock_provider = MagicMock()
        mock_provider.generate_completion.return_value = json.dumps({
            "obtained_marks": 15.0,
            "maximum_marks": 25.0,
            "rubric_breakdown": [
                {"criteria": "Overall Work", "allocated": 25.0, "awarded": 15.0, "evidence_found": "Partially readable handwriting."}
            ],
            "feedback": "Handwriting ambiguous.",
            "confidence": 0.65,
            "requires_manual_review": True
        })
        mock_get_provider.return_value = mock_provider

        res = AIScriptEvaluator._evaluate_answer_v3(self.answer, options={})
        self.assertTrue(res.requires_manual_review)
        self.assertLess(res.confidence, 0.70)


class QuestionMappingContinuationTests(TestCase):
    """Regression tests for question mapping continuation validation and semantic topic transitions."""

    def test_continuation_detector_weak_flow_returns_low_confidence(self):
        from core.ai_engine.mapping.continuation_detector import ContinuationDetector
        prev_text = "The final result is shown above."
        curr_text = "Digital image file formats are stored as pixels."


class AcademicEvaluatorFallbackTestCase(TestCase):
    """Regression tests proving AcademicEvaluator does not fabricate 80%/85% scores on AI failures."""

    @patch('core.ai_engine.providers.factory.AIProviderFactory.get_provider')
    def test_ai_failure_does_not_produce_fabricated_scores(self, mock_get_provider):
        from core.ai_engine.evaluator.academic_evaluator import AcademicEvaluator

        mock_provider = MagicMock()
        mock_provider.generate_completion.side_effect = Exception("API connection failure")
        mock_get_provider.return_value = mock_provider

        evaluator = AcademicEvaluator()
        result = evaluator.evaluate(
            question_id=1,
            question_text="Explain microservice architecture.",
            rubric_criteria="Definition and benefits",
            student_answer="Microservice architecture uses decoupled services.",
            max_marks=10.0
        )

        self.assertNotEqual(result['ai_suggested_marks'], 8.0)
        self.assertNotEqual(result['ai_suggested_marks'], 8.5)
        self.assertEqual(result['ai_suggested_marks'], 0.0)
        self.assertEqual(result['confidence_score'], 0.0)
        self.assertTrue(result['requires_manual_review'])

    @patch('core.ai_engine.providers.factory.AIProviderFactory.get_provider')
    def test_ai_malformed_json_returns_zero_and_requires_manual_review(self, mock_get_provider):
        from core.ai_engine.evaluator.academic_evaluator import AcademicEvaluator

        mock_provider = MagicMock()
        mock_provider.generate_completion.return_value = "Invalid raw text without JSON braces."
        mock_get_provider.return_value = mock_provider

        evaluator = AcademicEvaluator()
        result = evaluator.evaluate(
            question_id=1,
            question_text="Explain database indexing.",
            rubric_criteria="Index structures",
            student_answer="B-trees are used for database indexing.",
            max_marks=20.0
        )

        self.assertEqual(result['ai_suggested_marks'], 0.0)
        self.assertEqual(result['confidence_score'], 0.0)
        self.assertTrue(result['requires_manual_review'])

    @patch('core.ai_engine.providers.factory.AIProviderFactory.get_provider')
    def test_successful_ai_response_returns_real_score_unchanged(self, mock_get_provider):
        from core.ai_engine.evaluator.academic_evaluator import AcademicEvaluator

        mock_provider = MagicMock()
        mock_provider.generate_completion.return_value = json.dumps({
            "ai_suggested_marks": 17.5,
            "confidence_score": 0.92,
            "reason": "Clear explanation with good technical detail.",
            "strengths": ["Correct terminology"],
            "missing_points": ["Minor trade-off detail omitted"],
            "incorrect_points": [],
            "ai_feedback": "Good answer overall.",
            "partial_marking_breakdown": {"concept": 10.0, "details": 7.5}
        })
        mock_get_provider.return_value = mock_provider

        evaluator = AcademicEvaluator()
        result = evaluator.evaluate(
            question_id=1,
            question_text="Explain REST API constraints.",
            rubric_criteria="6 REST constraints",
            student_answer="Stateless, Cacheable, Client-Server, Layered System, Uniform Interface.",
            max_marks=20.0
        )

        self.assertEqual(result['ai_suggested_marks'], 17.5)
        self.assertEqual(result['confidence_score'], 0.92)
        self.assertFalse(result.get('requires_manual_review', False))


class OpenRouterProviderTestCase(TestCase):
    """
    Unit Tests for OpenRouterProvider using mocks.
    Guarantees no real external API calls are made during tests.
    """

    def setUp(self):
        from core.ai_engine.providers.openrouter import OpenRouterProvider
        self.provider = OpenRouterProvider(api_key="sk-or-v1-mock-test-key", model_name="openrouter/free")

    def test_missing_api_key_raises_value_error(self):
        from core.ai_engine.providers.openrouter import OpenRouterProvider
        no_key_provider = OpenRouterProvider(api_key="")
        with self.assertRaises(ValueError) as ctx:
            no_key_provider.generate_completion("Hello")
        self.assertIn("OpenRouter API Key is not configured", str(ctx.exception))

    @patch('urllib.request.urlopen')
    def test_text_request_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "model": "dots-studio/dots-3-note-preview:free",
            "choices": [{"message": {"content": "Hello from OpenRouter!"}}]
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        res = self.provider.generate_completion("Say hello")
        self.assertEqual(res, "Hello from OpenRouter!")
        self.assertTrue(mock_urlopen.called)

    @patch('urllib.request.urlopen')
    def test_image_request_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "model": "dots-studio/dots-3-note-preview:free",
            "choices": [{"message": {"content": "Handwritten answer text extracted."}}]
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        res = self.provider.generate_completion("Read this crop", image_bytes=b"dummy_bytes", mime_type="image/png")
        self.assertEqual(res, "Handwritten answer text extracted.")

        # Verify request structure
        req = mock_urlopen.call_args[0][0]
        payload = json.loads(req.data.decode('utf-8'))
        self.assertEqual(payload['model'], 'openrouter/free')
        self.assertEqual(len(payload['messages']), 1)
        self.assertEqual(payload['messages'][0]['content'][0]['type'], 'text')
        self.assertEqual(payload['messages'][0]['content'][1]['type'], 'image_url')

    @patch('urllib.request.urlopen')
    def test_multi_image_request_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "model": "dots-studio/dots-3-note-preview:free",
            "choices": [{"message": {"content": "Multi-crop text extracted."}}]
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        extra_files = [{'bytes': b"extra_crop_bytes", 'mime_type': 'image/png'}]
        res = self.provider.generate_completion("Read crops", image_bytes=b"main_crop", extra_files=extra_files)
        self.assertEqual(res, "Multi-crop text extracted.")

        req = mock_urlopen.call_args[0][0]
        payload = json.loads(req.data.decode('utf-8'))
        self.assertEqual(len(payload['messages'][0]['content']), 3)

    @patch('urllib.request.urlopen')
    def test_valid_json_evaluation(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "choices": [{"message": {"content": "```json\n{\"ai_suggested_marks\": 22.5, \"confidence_score\": 0.95, \"ai_feedback\": \"Excellent answer.\", \"partial_marking_breakdown\": {}}\n```"}}]
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        res = self.provider.evaluate_answer(
            question_text="Q4 proof",
            rubric_criteria="Rubric",
            student_answer="Ans",
            max_marks=25.0
        )
        self.assertEqual(res['ai_suggested_marks'], 22.5)
        self.assertEqual(res['confidence_score'], 0.95)

    @patch('urllib.request.urlopen')
    def test_malformed_json_raises_exception(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "choices": [{"message": {"content": "Not valid JSON response text"}}]
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        with self.assertRaises(Exception):
            self.provider.evaluate_answer(
                question_text="Q4 proof",
                rubric_criteria="Rubric",
                student_answer="Ans",
                max_marks=25.0
            )

    @patch('urllib.request.urlopen')
    def test_http_failure_raises_exception(self, mock_urlopen):
        from urllib.error import HTTPError
        mock_urlopen.side_effect = HTTPError("url", 429, "Rate limit exceeded", {}, io.BytesIO(b"Rate limit exceeded"))

        with self.assertRaises(Exception) as ctx:
            self.provider.generate_completion("Test")
        self.assertIn("OpenRouter API Error 429", str(ctx.exception))

    def test_thinking_output_sanitization(self):
        raw = "<think>Thinking about derivation...</think>\n{\"ai_suggested_marks\": 20.0}"
        cleaned = self.provider.sanitize_thinking_output(raw)
        self.assertEqual(cleaned, "{\"ai_suggested_marks\": 20.0}")


class TaskBasedRoutingTestCase(TestCase):
    """
    Comprehensive Unit Tests for Task-Based AI Routing, Capability Selection,
    Cooldown Management, Transient Retries, and Non-Fabrication Policy (Scenarios A through P).
    """

    def setUp(self):
        from core.ai_engine.routing.task_router import ProviderHealthTracker
        ProviderHealthTracker.clear_cooldowns()

    def tearDown(self):
        from core.ai_engine.routing.task_router import ProviderHealthTracker
        ProviderHealthTracker.clear_cooldowns()

    def test_scenario_a_local_success(self):
        """Scenario A: Local deterministic parsing succeeds without calling AI."""
        from core.ai_engine.providers.base import BaseAIProvider
        text = "Question 1: Explain Digital Signals. [10 marks]"
        res = BaseAIProvider.extract_deterministic_regex_questions(text)
        self.assertTrue(len(res.get("questions", [])) > 0)

    def test_scenario_b_local_failure_ai_success(self):
        """Scenario B: Local deterministic failure falls back to AI success."""
        from core.ai_engine.providers.failover import FailoverAIProvider
        from core.ai_engine.providers.groq import GroqProvider

        mock_p1 = MagicMock(spec=GroqProvider)
        mock_p1.get_capabilities.return_value = {'supports_text': True, 'supports_images': False}
        mock_p1.generate_completion.return_value = "AI Parsed Question"

        orchestrator = FailoverAIProvider(primary_provider=mock_p1)
        orchestrator._chain = [mock_p1]
        res = orchestrator.generate_completion("Unstructured content")
        self.assertEqual(res, "AI Parsed Question")

    def test_scenario_c_provider_1_success_provider_2_skipped(self):
        """Scenario C: Provider 1 succeeds -> Provider 2 and 3 skipped."""
        from core.ai_engine.providers.failover import FailoverAIProvider
        from core.ai_engine.providers.groq import GroqProvider
        from core.ai_engine.providers.gemini import GeminiProvider

        m1 = MagicMock(spec=GroqProvider)
        m1.get_capabilities.return_value = {'supports_text': True, 'supports_images': False}
        m1.generate_completion.return_value = "P1 Output"

        m2 = MagicMock(spec=GeminiProvider)
        m2.get_capabilities.return_value = {'supports_text': True, 'supports_images': False}

        orchestrator = FailoverAIProvider(primary_provider=m1)
        orchestrator._chain = [m1, m2]

        res = orchestrator.generate_completion("Prompt")
        self.assertEqual(res, "P1 Output")
        self.assertTrue(m1.generate_completion.called)
        self.assertFalse(m2.generate_completion.called)

    def test_scenario_d_provider_1_failure_provider_2_success(self):
        """Scenario D: Provider 1 fails -> Provider 2 succeeds."""
        from core.ai_engine.providers.failover import FailoverAIProvider
        from core.ai_engine.providers.groq import GroqProvider
        from core.ai_engine.providers.gemini import GeminiProvider

        m1 = MagicMock(spec=GroqProvider)
        m1.get_capabilities.return_value = {'supports_text': True, 'supports_images': False}
        m1.generate_completion.side_effect = Exception("P1 Rate Limit 429")

        m2 = MagicMock(spec=GeminiProvider)
        m2.get_capabilities.return_value = {'supports_text': True, 'supports_images': False}
        m2.generate_completion.return_value = "P2 Output"

        orchestrator = FailoverAIProvider(primary_provider=m1)
        orchestrator._chain = [m1, m2]

        res = orchestrator.generate_completion("Prompt")
        self.assertEqual(res, "P2 Output")
        self.assertTrue(m1.generate_completion.called)
        self.assertTrue(m2.generate_completion.called)

    def test_scenario_e_provider_1_2_failure_provider_3_success(self):
        """Scenario E: Provider 1 & 2 fail -> Provider 3 succeeds."""
        from core.ai_engine.providers.failover import FailoverAIProvider
        from core.ai_engine.providers.groq import GroqProvider
        from core.ai_engine.providers.openrouter import OpenRouterProvider
        from core.ai_engine.providers.gemini import GeminiProvider

        m1 = MagicMock(spec=GroqProvider)
        m1.get_capabilities.return_value = {'supports_text': True, 'supports_images': False}
        m1.generate_completion.side_effect = Exception("P1 429")

        m2 = MagicMock(spec=OpenRouterProvider)
        m2.get_capabilities.return_value = {'supports_text': True, 'supports_images': False}
        m2.generate_completion.side_effect = Exception("P2 Timeout")

        m3 = MagicMock(spec=GeminiProvider)
        m3.get_capabilities.return_value = {'supports_text': True, 'supports_images': False}
        m3.generate_completion.return_value = "P3 Output"

        orchestrator = FailoverAIProvider(primary_provider=m1)
        orchestrator._chain = [m1, m2, m3]

        res = orchestrator.generate_completion("Prompt")
        self.assertEqual(res, "P3 Output")

    def test_scenario_f_all_providers_fail_manual_review(self):
        """Scenario F: All vision providers fail -> Controlled failure for manual review."""
        from core.ai_engine.providers.failover import FailoverAIProvider
        from core.ai_engine.providers.groq import GroqProvider

        m1 = MagicMock(spec=GroqProvider)
        m1.get_capabilities.return_value = {'supports_text': True, 'supports_images': True}
        m1.generate_completion.side_effect = Exception("P1 Failed")

        orchestrator = FailoverAIProvider(primary_provider=m1)
        orchestrator._chain = [m1]

        with self.assertRaises(Exception) as ctx:
            orchestrator.generate_completion("Prompt", image_bytes=b"crop")
        self.assertIn("All AI Providers in the failover chain failed", str(ctx.exception))

    def test_scenario_g_429_cooldown(self):
        """Scenario G: 429 error triggers provider cooldown."""
        from core.ai_engine.routing.task_router import ProviderHealthTracker
        from core.ai_engine.providers.groq import GroqProvider

        ProviderHealthTracker.mark_cooldown(GroqProvider, duration_seconds=60.0)
        self.assertTrue(ProviderHealthTracker.is_on_cooldown(GroqProvider))

    def test_scenario_h_quota_skipping(self):
        """Scenario H: Quota error skips provider on subsequent calls."""
        from core.ai_engine.routing.task_router import ProviderHealthTracker, TaskRouter
        from core.ai_engine.routing.task_types import TaskType
        from core.ai_engine.providers.openai import OpenAIProvider

        ProviderHealthTracker.mark_cooldown(OpenAIProvider, duration_seconds=60.0)
        strategy = TaskRouter.route(TaskType.ANSWER_GRADING, has_images=True)
        self.assertNotIn(OpenAIProvider, strategy.execution_chain)

    def test_scenario_i_401_no_retry(self):
        """Scenario I: 401 Auth failure is classified as non-transient (no retry)."""
        from core.ai_engine.routing.task_router import TaskRouter
        self.assertFalse(TaskRouter.is_transient_error("HTTP Error 401: Unauthorized"))

    def test_scenario_j_timeout_retry(self):
        """Scenario J: Timeout is classified as transient (eligible for retry)."""
        from core.ai_engine.routing.task_router import TaskRouter
        self.assertTrue(TaskRouter.is_transient_error("The read operation timed out"))

    def test_scenario_k_image_batching(self):
        """Scenario K: 5 images with max_images=3 splits into 2 batches (3 and 2)."""
        from core.ai_engine.routing.task_router import TaskRouter
        crops = [b"crop1", b"crop2", b"crop3", b"crop4", b"crop5"]
        batches = TaskRouter.batch_images(crops, max_images=3)
        self.assertEqual(len(batches), 2)
        self.assertEqual(len(batches[0]), 3)
        self.assertEqual(len(batches[1]), 2)
        self.assertEqual(sum(len(b) for b in batches), 5)

    def test_scenario_l_malformed_json(self):
        """Scenario L: Malformed JSON raises exception without score fabrication."""
        from core.ai_engine.providers.groq import GroqProvider
        provider = GroqProvider(api_key="mock_key")
        with patch.object(provider, '_call_api', return_value="Plain text non-JSON response"):
            with self.assertRaises(Exception):
                provider.evaluate_answer("Q", "Rubric", "Ans", 25.0)

    def test_scenario_m_valid_json_score_preservation(self):
        """Scenario M: Valid JSON preserves exact score."""
        from core.ai_engine.providers.groq import GroqProvider
        provider = GroqProvider(api_key="mock_key")
        valid_json = json.dumps({
            "ai_suggested_marks": 21.5,
            "confidence_score": 0.94,
            "ai_feedback": "Great derivation.",
            "partial_marking_breakdown": {}
        })
        with patch.object(provider, '_call_api', return_value=valid_json):
            res = provider.evaluate_answer("Q", "Rubric", "Ans", 25.0)
            self.assertEqual(res['ai_suggested_marks'], 21.5)
            self.assertEqual(res['confidence_score'], 0.94)

    def test_scenario_n_image_task_excludes_text_only_ollama(self):
        """Scenario N: Vision image tasks exclude text-only Ollama provider."""
        from core.ai_engine.providers.failover import FailoverAIProvider
        from core.ai_engine.providers.ollama import OllamaProvider
        m_vision = MagicMock()
        m_vision.get_capabilities.return_value = {'supports_text': True, 'supports_images': True}

        m_ollama = OllamaProvider()
        orchestrator = FailoverAIProvider(primary_provider=m_vision)
        orchestrator._chain = [m_vision, m_ollama]

        chain = orchestrator._get_execution_chain(has_images=True)
        self.assertNotIn(m_ollama, chain)

    def test_scenario_o_openrouter_provider_routing(self):
        """Scenario O: OpenRouter Provider is included in vision and text chains."""
        from core.ai_engine.providers.failover import FailoverAIProvider
        from core.ai_engine.providers.openrouter import OpenRouterProvider

        m_openrouter = OpenRouterProvider(api_key="sk-or-v1-test")
        orchestrator = FailoverAIProvider(primary_provider=m_openrouter)
        chain = orchestrator._get_execution_chain(has_images=True)
        self.assertTrue(any(isinstance(p, OpenRouterProvider) for p in chain))

    def test_scenario_p_no_fabricated_marks(self):
        """Scenario P: Evaluation failure sets obtained_marks=0.0 and requires_manual_review=True."""
        from core.ai_engine.evaluator.academic_evaluator import AcademicEvaluator
        evaluator = AcademicEvaluator()
        with patch('core.ai_engine.providers.factory.AIProviderFactory.get_provider') as mock_get:
            mock_p = MagicMock()
            mock_p.generate_completion.side_effect = Exception("API Unavailable")
            mock_get.return_value = mock_p

            res = evaluator.evaluate(
                question_id=1,
                question_text="Q",
                rubric_criteria="R",
                student_answer="A",
                max_marks=25.0
            )
            self.assertEqual(res['ai_suggested_marks'], 0.0)
            self.assertEqual(res['confidence_score'], 0.0)
            self.assertTrue(res['requires_manual_review'])

    # =========================================================================
    # STEP 40 REGRESSION TESTS: ENFORCE PROVIDER IMAGE LIMITS BEFORE API CALL
    # =========================================================================

    def test_step40_regression_a_2_images_groq_allowed(self):
        """Step 40 Regression A: 2 images -> Groq allowed."""
        from core.ai_engine.routing.task_router import TaskRouter, ProviderHealthTracker
        from core.ai_engine.routing.task_types import TaskType
        from core.ai_engine.providers.groq import GroqProvider
        from core.ai_engine.providers.failover import FailoverAIProvider
        from core.ai_engine.providers.openrouter import OpenRouterProvider

        ProviderHealthTracker.clear_cooldowns()
        strategy = TaskRouter.route(TaskType.ANSWER_VISUAL_READ, has_images=True, image_count=2)
        self.assertIn(GroqProvider, strategy.execution_chain)
        self.assertEqual(strategy.execution_chain[0], GroqProvider)

        groq = GroqProvider(api_key="test_key")
        openrouter = OpenRouterProvider(api_key="test_key")
        failover = FailoverAIProvider(primary_provider=groq)
        failover._chain = [groq, openrouter]

        chain = failover._get_execution_chain(has_images=True, task_type=TaskType.ANSWER_VISUAL_READ, image_count=2)
        self.assertIn(groq, chain)
        self.assertEqual(chain[0], groq)

    def test_step40_regression_b_3_images_groq_allowed(self):
        """Step 40 Regression B: 3 images -> Groq allowed."""
        from core.ai_engine.routing.task_router import TaskRouter, ProviderHealthTracker
        from core.ai_engine.routing.task_types import TaskType
        from core.ai_engine.providers.groq import GroqProvider
        from core.ai_engine.providers.failover import FailoverAIProvider
        from core.ai_engine.providers.openrouter import OpenRouterProvider

        ProviderHealthTracker.clear_cooldowns()
        strategy = TaskRouter.route(TaskType.ANSWER_VISUAL_READ, has_images=True, image_count=3)
        self.assertIn(GroqProvider, strategy.execution_chain)
        self.assertEqual(strategy.execution_chain[0], GroqProvider)

        groq = GroqProvider(api_key="test_key")
        openrouter = OpenRouterProvider(api_key="test_key")
        failover = FailoverAIProvider(primary_provider=groq)
        failover._chain = [groq, openrouter]

        chain = failover._get_execution_chain(has_images=True, task_type=TaskType.ANSWER_VISUAL_READ, image_count=3)
        self.assertIn(groq, chain)
        self.assertEqual(chain[0], groq)

    def test_step40_regression_c_4_images_groq_compacted(self):
        """Step 40/46 Regression C: 4 images -> Groq routed with compaction capability."""
        from core.ai_engine.routing.task_router import TaskRouter, ProviderHealthTracker
        from core.ai_engine.routing.task_types import TaskType
        from core.ai_engine.providers.groq import GroqProvider
        from core.ai_engine.providers.failover import FailoverAIProvider
        from core.ai_engine.providers.openrouter import OpenRouterProvider

        ProviderHealthTracker.clear_cooldowns()
        strategy = TaskRouter.route(TaskType.ANSWER_VISUAL_READ, has_images=True, image_count=4)
        self.assertIn(GroqProvider, strategy.execution_chain)

        groq = GroqProvider(api_key="test_key")
        openrouter = OpenRouterProvider(api_key="test_key")
        failover = FailoverAIProvider(primary_provider=groq)
        failover._chain = [groq, openrouter]

        chain = failover._get_execution_chain(has_images=True, task_type=TaskType.ANSWER_VISUAL_READ, image_count=4)
        self.assertIn(groq, chain)

        # Direct call to Groq with 4 images without compaction raises ValueError
        with self.assertRaises(ValueError) as ctx:
            groq._call_api(
                prompt="Test prompt",
                image_bytes=b"img1",
                extra_files=[{'bytes': b"img2"}, {'bytes': b"img3"}, {'bytes': b"img4"}]
            )
        self.assertIn("Too many images provided", str(ctx.exception))

    def test_step40_regression_d_5_images_groq_compacted(self):
        """Step 40/46 Regression D: 5 images -> Groq routed with compaction capability."""
        from core.ai_engine.routing.task_router import TaskRouter, ProviderHealthTracker
        from core.ai_engine.routing.task_types import TaskType
        from core.ai_engine.providers.groq import GroqProvider
        from core.ai_engine.providers.failover import FailoverAIProvider
        from core.ai_engine.providers.openrouter import OpenRouterProvider

        ProviderHealthTracker.clear_cooldowns()
        strategy = TaskRouter.route(TaskType.ANSWER_VISUAL_READ, has_images=True, image_count=5)
        self.assertIn(GroqProvider, strategy.execution_chain)

        groq = GroqProvider(api_key="test_key")
        openrouter = OpenRouterProvider(api_key="test_key")
        failover = FailoverAIProvider(primary_provider=groq)
        failover._chain = [groq, openrouter]

        chain = failover._get_execution_chain(has_images=True, task_type=TaskType.ANSWER_VISUAL_READ, image_count=5)
        self.assertIn(groq, chain)

        # Direct call to Groq with 5 images without compaction raises ValueError
        with self.assertRaises(ValueError) as ctx:
            groq._call_api(
                prompt="Test prompt",
                image_bytes=b"img1",
                extra_files=[{'bytes': b"img2"}, {'bytes': b"img3"}, {'bytes': b"img4"}, {'bytes': b"img5"}]
            )
        self.assertIn("Too many images provided", str(ctx.exception))

    def test_step40_regression_e_non_image_provider_skipped_for_visual_task(self):
        """Step 40/46 Regression E: Non-image capable provider skipped for visual task."""
        from core.ai_engine.routing.task_router import TaskRouter, ProviderHealthTracker
        from core.ai_engine.routing.task_types import TaskType
        from core.ai_engine.providers.groq import GroqProvider
        from core.ai_engine.providers.openrouter import OpenRouterProvider
        from core.ai_engine.providers.ollama import OllamaProvider
        from core.ai_engine.providers.failover import FailoverAIProvider

        ProviderHealthTracker.clear_cooldowns()
        strategy_4 = TaskRouter.route(TaskType.ANSWER_VISUAL_READ, has_images=True, image_count=4)
        self.assertNotIn(OllamaProvider, strategy_4.execution_chain)

        groq = GroqProvider(api_key="test_key")
        openrouter = OpenRouterProvider(api_key="test_key")
        ollama = OllamaProvider()
        failover = FailoverAIProvider(primary_provider=groq)
        failover._chain = [ollama, groq, openrouter]

        chain = failover._get_execution_chain(has_images=True, task_type=TaskType.ANSWER_VISUAL_READ, image_count=4)
        self.assertNotIn(ollama, chain)

    def test_step40_regression_f_no_image_is_dropped(self):
        """Step 40 Regression F: No image is dropped when routing to compatible provider."""
        from core.ai_engine.providers.openrouter import OpenRouterProvider
        from core.ai_engine.providers.groq import GroqProvider
        from core.ai_engine.providers.failover import FailoverAIProvider
        from core.ai_engine.routing.task_router import ProviderHealthTracker

        ProviderHealthTracker.clear_cooldowns()
        groq = GroqProvider(api_key="test_key")
        openrouter = OpenRouterProvider(api_key="test_key")
        failover = FailoverAIProvider(primary_provider=groq)
        failover._chain = [groq, openrouter]

        with patch.object(openrouter, 'generate_completion', return_value='{"obtained_marks": 22.0}') as mock_gen:
            primary_crop = b"crop_primary"
            extra_crops = [
                {'bytes': b"crop_2", 'mime_type': 'image/png'},
                {'bytes': b"crop_3", 'mime_type': 'image/png'},
                {'bytes': b"crop_4", 'mime_type': 'image/png'},
                {'bytes': b"crop_5", 'mime_type': 'image/png'}
            ]
            res = failover.generate_completion(
                prompt="Evaluate script",
                image_bytes=primary_crop,
                extra_files=extra_crops
            )
            self.assertEqual(res, '{"obtained_marks": 22.0}')
            mock_gen.assert_called_once()
            call_kwargs = mock_gen.call_args[1]
            self.assertEqual(call_kwargs['image_bytes'], primary_crop)
            self.assertEqual(len(call_kwargs['extra_files']), 4)
            # Total images preserved = 1 + 4 = 5
            total_images_passed = (1 if call_kwargs.get('image_bytes') else 0) + len(call_kwargs.get('extra_files', []))
            self.assertEqual(total_images_passed, 5)

    def test_step40_regression_g_all_providers_incompatible_manual_review(self):
        """Step 40 Regression G: All providers incompatible -> triggers safe manual review."""
        from core.ai_engine.evaluator.academic_evaluator import AcademicEvaluator
        evaluator = AcademicEvaluator()
        with patch('core.ai_engine.providers.factory.AIProviderFactory.get_provider') as mock_get:
            mock_p = MagicMock()
            mock_p.generate_completion.side_effect = Exception("No compatible active AI providers available (image limit exceeded across all providers).")
            mock_get.return_value = mock_p

            res = evaluator.evaluate(
                question_id=1,
                question_text="Derive Navier-Stokes equations.",
                rubric_criteria="Complete derivation.",
                student_answer="Attached 20 visual crops.",
                max_marks=20.0
            )
            self.assertEqual(res['ai_suggested_marks'], 0.0)
            self.assertEqual(res['confidence_score'], 0.0)
            self.assertTrue(res['requires_manual_review'])
            self.assertIn("manual teacher review", res['ai_feedback'].lower())

    def test_step40_regression_h_text_only_tasks_unaffected(self):
        """Step 40 Regression H: Text-only tasks unaffected by image limit rules."""
        from core.ai_engine.routing.task_router import TaskRouter, ProviderHealthTracker
        from core.ai_engine.routing.task_types import TaskType
        from core.ai_engine.providers.groq import GroqProvider
        from core.ai_engine.providers.openrouter import OpenRouterProvider
        from core.ai_engine.providers.gemini import GeminiProvider
        from core.ai_engine.providers.openai import OpenAIProvider

        ProviderHealthTracker.clear_cooldowns()
        # Text only routine parsing
        strategy_routine = TaskRouter.route(TaskType.ROUTINE_PARSE, has_images=False, image_count=0)
        self.assertIn(GroqProvider, strategy_routine.execution_chain)
        self.assertEqual(strategy_routine.execution_chain[0], GroqProvider)

        # Text only answer grading
        strategy_grading = TaskRouter.route(TaskType.ANSWER_GRADING, has_images=False, image_count=0)
        self.assertIn(GroqProvider, strategy_grading.execution_chain)
        self.assertEqual(strategy_grading.execution_chain[0], GroqProvider)

        # Text only feedback gen
        strategy_feedback = TaskRouter.route(TaskType.FEEDBACK_GENERATION, has_images=False, image_count=0)
        self.assertIn(GroqProvider, strategy_feedback.execution_chain)
        self.assertEqual(strategy_feedback.execution_chain[0], GroqProvider)


class Step46CompactionTests(TestCase):
    """
    Step 46 Regression & Validation Test Suite for 650px Bounded Vertical Image Compaction.
    """

    def setUp(self):
        import cv2
        import numpy as np
        # Create small valid PNG byte snippets (values <= 255)
        self.dummy_imgs = []
        for i in range(1, 7):
            canvas = np.full((120, 100, 3), 30 * i, dtype=np.uint8)
            cv2.putText(canvas, f"P{i}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            _, buf = cv2.imencode('.png', canvas)
            self.dummy_imgs.append(buf.tobytes())

    def test_test_a_1_to_3_crops_unchanged(self):
        """Test A: 1-3 crops -> originals unchanged without compaction."""
        from core.ai_engine.evaluation.answer_crop_service import AnswerCropService

        crops_3 = [
            {'page_number': 1, 'region_id': 'r1', 'image_bytes': self.dummy_imgs[0]},
            {'page_number': 2, 'region_id': 'r2', 'image_bytes': self.dummy_imgs[1]},
            {'page_number': 3, 'region_id': 'r3', 'image_bytes': self.dummy_imgs[2]}
        ]
        res = AnswerCropService.compact_crops_into_composites(crops_list=crops_3, max_composites=3)
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0]['image_bytes'], self.dummy_imgs[0])
        self.assertEqual(res[1]['image_bytes'], self.dummy_imgs[1])
        self.assertEqual(res[2]['image_bytes'], self.dummy_imgs[2])

    def test_test_b_4_crops_groq_gets_leq_3_composites(self):
        """Test B: 4 crops -> compacted into <=3 composites (exactly 2 composites)."""
        from core.ai_engine.evaluation.answer_crop_service import AnswerCropService

        crops_4 = [
            {'page_number': 1, 'region_id': 'r1', 'image_bytes': self.dummy_imgs[0]},
            {'page_number': 2, 'region_id': 'r2', 'image_bytes': self.dummy_imgs[1]},
            {'page_number': 3, 'region_id': 'r3', 'image_bytes': self.dummy_imgs[2]},
            {'page_number': 4, 'region_id': 'r4', 'image_bytes': self.dummy_imgs[3]}
        ]
        res = AnswerCropService.compact_crops_into_composites(crops_list=crops_4, max_composites=3, target_width=650)
        self.assertTrue(len(res) <= 3)
        self.assertEqual(len(res), 2)
        # All composites must have width 650
        for comp in res:
            self.assertEqual(comp['crop_width'], 650)

    def test_test_c_5_crops_groq_gets_leq_3_composites(self):
        """Test C: 5 crops -> compacted into <=3 composites (exactly 3 composites)."""
        from core.ai_engine.evaluation.answer_crop_service import AnswerCropService

        crops_5 = [
            {'page_number': 1, 'region_id': 'r1', 'image_bytes': self.dummy_imgs[0]},
            {'page_number': 2, 'region_id': 'r2', 'image_bytes': self.dummy_imgs[1]},
            {'page_number': 3, 'region_id': 'r3', 'image_bytes': self.dummy_imgs[2]},
            {'page_number': 4, 'region_id': 'r4', 'image_bytes': self.dummy_imgs[3]},
            {'page_number': 5, 'region_id': 'r5', 'image_bytes': self.dummy_imgs[4]}
        ]
        res = AnswerCropService.compact_crops_into_composites(crops_list=crops_5, max_composites=3, target_width=650)
        self.assertTrue(len(res) <= 3)
        self.assertEqual(len(res), 3)

    def test_test_d_page_order_preserved(self):
        """Test D: Page order is strictly preserved across composites."""
        from core.ai_engine.evaluation.answer_crop_service import AnswerCropService

        crops_4 = [
            {'page_number': 4, 'region_id': 'p4', 'image_bytes': self.dummy_imgs[0]},
            {'page_number': 6, 'region_id': 'p6', 'image_bytes': self.dummy_imgs[1]},
            {'page_number': 7, 'region_id': 'p7', 'image_bytes': self.dummy_imgs[2]},
            {'page_number': 8, 'region_id': 'p8', 'image_bytes': self.dummy_imgs[3]}
        ]
        res = AnswerCropService.compact_crops_into_composites(crops_list=crops_4, max_composites=3, target_width=650)
        self.assertEqual(res[0]['pages'], [4, 6])
        self.assertEqual(res[1]['pages'], [7, 8])

    def test_test_e_no_crop_dropped(self):
        """Test E: All source crops are accounted for with zero crops dropped."""
        from core.ai_engine.evaluation.answer_crop_service import AnswerCropService

        crops_5 = [
            {'page_number': i, 'region_id': f'r{i}', 'image_bytes': self.dummy_imgs[i-1]}
            for i in range(1, 6)
        ]
        res = AnswerCropService.compact_crops_into_composites(crops_list=crops_5, max_composites=3, target_width=650)
        all_accounted_pages = []
        for comp in res:
            all_accounted_pages.extend(comp['pages'])
        self.assertEqual(all_accounted_pages, [1, 2, 3, 4, 5])

    def test_test_f_no_duplicate_crops(self):
        """Test F: No duplicate crops are generated in the output."""
        from core.ai_engine.evaluation.answer_crop_service import AnswerCropService

        crops_5 = [
            {'page_number': i, 'region_id': f'r{i}', 'image_bytes': self.dummy_imgs[i-1]}
            for i in range(1, 6)
        ]
        res = AnswerCropService.compact_crops_into_composites(crops_list=crops_5, max_composites=3, target_width=650)
        all_pages = [p for comp in res for p in comp['pages']]
        self.assertEqual(len(all_pages), len(set(all_pages)))

    def test_test_g_provider_with_high_max_images_no_compaction(self):
        """Test G: Provider with max_images >= crop_count receives original crops without compaction."""
        from core.ai_engine.providers.failover import FailoverAIProvider
        from core.ai_engine.providers.openrouter import OpenRouterProvider

        openrouter = OpenRouterProvider(api_key="sk-test-key")
        failover = FailoverAIProvider(primary_provider=openrouter)
        failover._chain = [openrouter]

        with patch.object(openrouter, 'generate_completion', return_value='{"obtained_marks": 18.0}') as mock_gen:
            primary_crop = self.dummy_imgs[0]
            extra_crops = [
                {'bytes': self.dummy_imgs[1], 'mime_type': 'image/png'},
                {'bytes': self.dummy_imgs[2], 'mime_type': 'image/png'},
                {'bytes': self.dummy_imgs[3], 'mime_type': 'image/png'}
            ]
            res = failover.generate_completion(
                prompt="Evaluate script",
                image_bytes=primary_crop,
                extra_files=extra_crops
            )
            self.assertEqual(res, '{"obtained_marks": 18.0}')
            mock_gen.assert_called_once()
            call_kwargs = mock_gen.call_args[1]
            # Must remain uncompacted 4 original images
            self.assertEqual(call_kwargs['image_bytes'], primary_crop)
            self.assertEqual(len(call_kwargs['extra_files']), 3)

    def test_test_h_invalid_or_unreadable_image_controlled_fallback(self):
        """Test H: Invalid/unreadable image triggers safe manual review."""
        from core.ai_engine.evaluator.academic_evaluator import AcademicEvaluator
        evaluator = AcademicEvaluator()
        with patch('core.ai_engine.providers.factory.AIProviderFactory.get_provider') as mock_get:
            mock_p = MagicMock()
            mock_p.generate_completion.side_effect = ValueError("Corrupted image format")
            mock_get.return_value = mock_p

            res = evaluator.evaluate(
                question_id=1,
                question_text="Explain Fourier Transform.",
                rubric_criteria="Full explanation.",
                student_answer="Attached corrupted images.",
                max_marks=10.0
            )
            self.assertEqual(res['ai_suggested_marks'], 0.0)
            self.assertTrue(res['requires_manual_review'])
            self.assertIn("manual teacher review", res['ai_feedback'].lower())

    def test_test_i_score_remains_bounded(self):
        """Test I: Evaluated scores are strictly bounded 0.0 <= marks <= max_marks."""
        from core.ai_engine.evaluator.academic_evaluator import AcademicEvaluator
        evaluator = AcademicEvaluator()
        with patch('core.ai_engine.providers.factory.AIProviderFactory.get_provider') as mock_get:
            mock_p = MagicMock()
            mock_p.generate_completion.return_value = '{"obtained_marks": 999.0, "confidence_score": 1.5}'
            mock_get.return_value = mock_p

            res = evaluator.evaluate(
                question_id=1,
                question_text="Explain DCT.",
                rubric_criteria="DCT formula.",
                student_answer="Student answer text",
                max_marks=10.0
            )
            self.assertTrue(0.0 <= res['ai_suggested_marks'] <= 10.0)
            self.assertTrue(0.0 <= res['confidence_score'] <= 1.0)

    def test_test_j_malformed_provider_json_no_fabricated_score(self):
        """Test J: Malformed provider JSON does not fabricate scores and triggers manual review."""
        from core.ai_engine.evaluator.academic_evaluator import AcademicEvaluator
        evaluator = AcademicEvaluator()
        with patch('core.ai_engine.providers.factory.AIProviderFactory.get_provider') as mock_get:
            mock_p = MagicMock()
            mock_p.generate_completion.return_value = 'INVALID NOT JSON {Broken'
            mock_get.return_value = mock_p

            res = evaluator.evaluate(
                question_id=1,
                question_text="Explain Wavelet.",
                rubric_criteria="Wavelet basics.",
                student_answer="Student answer text",
                max_marks=15.0
            )
            self.assertEqual(res['ai_suggested_marks'], 0.0)
            self.assertEqual(res['confidence_score'], 0.0)
            self.assertTrue(res['requires_manual_review'])
            self.assertIn("manual teacher review", res['ai_feedback'].lower())


class ScanProgressPollingTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='teacher_user', password='password123')
        self.profile = Profile.objects.create(user=self.user, role=Profile.Role.TEACHER)

    def test_get_scan_progress_unauthenticated(self):
        response = self.client.get(reverse('api_get_scan_progress', kwargs={'exam_id': 99}))
        self.assertEqual(response.status_code, 401)

    def test_get_scan_progress_authenticated_idle(self):
        self.client.login(username='teacher_user', password='password123')
        response = self.client.get(reverse('api_get_scan_progress', kwargs={'exam_id': 99}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'idle')

    def test_get_scan_progress_cache_updates(self):
        from django.core.cache import cache
        from core.views import _update_scan_progress_cache
        _update_scan_progress_cache(99, 50, "Extracting text...", "processing", "info")
        
        self.client.login(username='teacher_user', password='password123')
        response = self.client.get(reverse('api_get_scan_progress', kwargs={'exam_id': 99}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('progress'), 50)
        self.assertEqual(data.get('msg'), "Extracting text...")
        self.assertEqual(data.get('status'), "processing")

