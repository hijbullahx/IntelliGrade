from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrator'
        TEACHER = 'TEACHER', 'Teacher / Examiner'
        STUDENT = 'STUDENT', 'Student'
        DEPARTMENT_HEAD = 'DEPT_HEAD', 'Department Head'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.TEACHER)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_approved = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"


class College(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class School(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=30, unique=True)
    college = models.ForeignKey(College, on_delete=models.SET_NULL, null=True, blank=True, related_name='schools')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.college:
            return f"{self.name} [{self.college.code}]"
        return f"{self.name} ({self.code})"


class Department(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=30, unique=True)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True, related_name='departments')
    college = models.ForeignKey(College, on_delete=models.SET_NULL, null=True, blank=True, related_name='departments')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"



class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    instructors = models.ManyToManyField(User, related_name='assigned_courses', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.title}"


class Examination(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PUBLISHED = 'PUBLISHED', 'Published'
        EVALUATING = 'EVALUATING', 'Evaluating'
        COMPLETED = 'COMPLETED', 'Completed'

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='examinations')
    title = models.CharField(max_length=200)
    exam_date = models.DateField()
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    assigned_faculty = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_examinations')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_exams')
    
    # Uploaded Reference Documents
    question_paper_file = models.FileField(upload_to='exam_questions/%Y/%m/', blank=True, null=True, help_text="Uploaded Question Paper document or image.")
    rubric_file = models.FileField(upload_to='exam_rubrics/%Y/%m/', blank=True, null=True, help_text="Uploaded Grading Rubric document or image.")
    course_outline_file = models.FileField(upload_to='course_outlines/%Y/%m/', blank=True, null=True, help_text="Uploaded Course Syllabus / Outline document.")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.code} - {self.title}"


class Question(models.Model):
    examination = models.ForeignKey(Examination, on_delete=models.CASCADE, related_name='questions')
    question_number = models.CharField(max_length=10)
    prompt_text = models.TextField()
    max_marks = models.DecimalField(max_digits=5, decimal_places=2)

    # IUBAT Academic Hierarchy & Classification Fields
    question_type = models.JSONField(default=list, blank=True, help_text="Categories (e.g. Theory, Numerical, Algorithm, Scenario)")
    command_verbs = models.JSONField(default=list, blank=True, help_text="Instructional verbs (e.g. Explain, Calculate, Design)")
    scenario = models.TextField(blank=True, help_text="Optional case scenario or context")
    bloom_level = models.CharField(max_length=50, default='Understand', help_text="Bloom Taxonomy Level")
    co_mapping = models.CharField(max_length=50, blank=True, help_text="Course Outcome Mapping (e.g. CO1)")
    po_mapping = models.JSONField(default=list, blank=True, help_text="Program Outcome Mappings (e.g. ['PO(a)', 'PO(c)'])")
    kp_mapping = models.JSONField(default=list, blank=True, help_text="Knowledge Profile (e.g. ['KP1', 'KP3'])")
    cep_mapping = models.JSONField(default=list, blank=True, help_text="Complex Engineering Problems (e.g. ['CEP1'])")
    cea_mapping = models.JSONField(default=list, blank=True, help_text="Complex Engineering Activities (e.g. ['CEA1'])")
    difficulty = models.CharField(max_length=30, default='Medium', help_text="Easy, Medium, Hard, Very Hard")
    estimated_time = models.CharField(max_length=50, default='15 mins', help_text="Estimated Solving Time")
    figures = models.JSONField(default=list, blank=True, help_text="Attached Figures, Diagrams, Equations")
    teacher_notes = models.TextField(blank=True, help_text="Private teacher notes (not visible to students)")

    class Meta:
        ordering = ['question_number']
        unique_together = ('examination', 'question_number')

    def __str__(self):
        return f"Q{self.question_number} ({self.max_marks} marks) - {self.examination.title}"


class Rubric(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='rubric')
    criteria = models.TextField(help_text="Detailed grading criteria and key concepts expected.")
    ideal_answer = models.TextField(blank=True, help_text="Sample or model answer.")
    mark_distribution = models.JSONField(default=dict, blank=True, help_text="JSON mapping criteria/steps to specific marks.")
    
    # Extended Academic Rubric & Evaluation Fields
    expected_answer = models.TextField(blank=True, help_text="Structured expected answer format")
    rubric_levels = models.JSONField(default=dict, blank=True, help_text="Grading levels (Excellent, Good, Average, Poor, Fail)")
    keywords = models.JSONField(default=list, blank=True, help_text="Expected key terms/concepts")
    alternative_answers = models.TextField(blank=True, help_text="Alternative valid solutions")
    common_mistakes = models.JSONField(default=list, blank=True, help_text="Common student pitfalls and deductions")

    def __str__(self):
        return f"Rubric for Q{self.question.question_number} ({self.question.examination.title})"


class QuestionFigure(models.Model):
    """Stores visual figures, diagrams, and images attached to specific exam questions with layout bounding boxes."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='figures_rel')
    page_number = models.IntegerField(default=1)
    caption = models.CharField(max_length=255, blank=True, help_text="e.g. Figure 1: 8-bit Grayscale Matrix")
    image = models.ImageField(upload_to='exam_figures/%Y/%m/')
    thumbnail = models.ImageField(upload_to='exam_figures/thumbs/%Y/%m/', blank=True, null=True)
    bounding_box = models.JSONField(default=list, blank=True, help_text="[xmin, ymin, xmax, ymax]")
    display_order = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['page_number', 'display_order', 'id']

    def __str__(self):
        return f"Figure '{self.caption or 'Diagram'}' for Q{self.question.question_number} (Page {self.page_number})"


class QuestionTable(models.Model):
    """Stores structured tabular data / matrices extracted from exam questions."""
    ELEMENT_TYPE_CHOICES = [
        ('TABLE', 'Table'),
        ('MATRIX', 'Matrix'),
        ('GRID', 'Grid'),
    ]

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='tables_rel')
    page_number = models.IntegerField(default=1)
    element_type = models.CharField(max_length=20, choices=ELEMENT_TYPE_CHOICES, default='TABLE')
    caption = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='exam_tables/%Y/%m/', blank=True, null=True)
    bounding_box = models.JSONField(default=list, blank=True, help_text="[xmin, ymin, xmax, ymax]")
    rows = models.IntegerField(default=0)
    columns = models.IntegerField(default=0)
    cell_json = models.JSONField(default=list, help_text="2D array of cell text e.g. [['50','56'], ['52','72']]")
    table_data = models.JSONField(default=dict, blank=True)
    display_order = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['page_number', 'display_order', 'id']

    def __str__(self):
        return f"Table '{self.caption or 'Data Table'}' for Q{self.question.question_number} (Page {self.page_number})"


class QuestionFormula(models.Model):
    """Stores mathematical formulas and LaTeX matrix representations."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='formulas_rel')
    page_number = models.IntegerField(default=1)
    caption = models.CharField(max_length=255, blank=True)
    raw_latex = models.TextField(blank=True, help_text="LaTeX equation representation")
    image = models.ImageField(upload_to='exam_formulas/%Y/%m/', blank=True, null=True)
    bounding_box = models.JSONField(default=list, blank=True, help_text="[xmin, ymin, xmax, ymax]")
    is_matrix = models.BooleanField(default=False)
    display_order = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"Formula for Q{self.question.question_number} (Page {self.page_number})"


class DocumentDOM(models.Model):
    """Stores complete Document Object Model (DOM) layout tree per examination paper."""
    examination = models.OneToOneField(Examination, on_delete=models.CASCADE, related_name='document_dom')
    elements_json = models.JSONField(default=list, help_text="Hierarchical DOM tree (headings, questions, figures, tables, boxes)")
    total_pages = models.IntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Document DOM for {self.examination.title} ({self.total_pages} pages)"


class AIProviderHealth(models.Model):
    """Real-time health status, capabilities, error logs, and metrics per AI Provider."""
    class HealthStatus(models.TextChoices):
        HEALTHY = 'HEALTHY', 'Healthy'
        RATE_LIMITED = 'RATE_LIMITED', 'Rate Limited (429)'
        EXPIRED = 'EXPIRED', 'API Key Expired / Unauthorized'
        OFFLINE = 'OFFLINE', 'Offline / Unavailable'

    provider_name = models.CharField(max_length=100, unique=True)
    current_model = models.CharField(max_length=100, default='AUTO')
    status = models.CharField(max_length=30, choices=HealthStatus.choices, default=HealthStatus.HEALTHY)
    capabilities_json = models.JSONField(default=dict, help_text="Declared capabilities (vision, pdf, json, function_calling)")
    last_success_at = models.DateTimeField(null=True, blank=True)
    last_failure_at = models.DateTimeField(null=True, blank=True)
    last_error_message = models.TextField(blank=True)
    error_count = models.IntegerField(default=0)
    avg_response_time_ms = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.provider_name} [{self.status}] - Model: {self.current_model}"


class AnswerScript(models.Model):
    class Status(models.TextChoices):
        UPLOADED = 'UPLOADED', 'Uploaded'
        OCR_DONE = 'OCR_DONE', 'OCR Processed'
        EVALUATED = 'EVALUATED', 'AI Evaluated'
        REVIEWED = 'REVIEWED', 'Teacher Reviewed & Finalized'

    examination = models.ForeignKey(Examination, on_delete=models.CASCADE, related_name='scripts')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scripts')
    script_file = models.FileField(upload_to='answer_scripts/%Y/%m/')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UPLOADED)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Script: {self.student.username} - {self.examination.title}"


class AnswerSegment(models.Model):
    script = models.ForeignKey(AnswerScript, on_delete=models.CASCADE, related_name='segments')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='segments')
    extracted_text = models.TextField(blank=True)
    ocr_confidence = models.FloatField(default=0.0)

    def __str__(self):
        return f"Segment Q{self.question.question_number} for {self.script.student.username}"


class Evaluation(models.Model):
    class ReviewStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending Teacher Review'
        APPROVED = 'APPROVED', 'Approved by Teacher'
        MODIFIED = 'MODIFIED', 'Modified by Teacher'

    segment = models.OneToOneField(AnswerSegment, on_delete=models.CASCADE, related_name='evaluation')
    ai_suggested_marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ai_feedback = models.TextField(blank=True)
    confidence_score = models.FloatField(default=0.0)

    teacher_final_marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    teacher_notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=ReviewStatus.choices, default=ReviewStatus.PENDING)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def get_effective_marks(self):
        if self.teacher_final_marks is not None:
            return self.teacher_final_marks
        return self.ai_suggested_marks or 0.0

    def __str__(self):
        return f"Eval Q{self.segment.question.question_number}: {self.get_effective_marks()}/{self.segment.question.max_marks}"


# ==========================================
# AI Engine Configuration, Memory & RAG Models
# ==========================================

class AIConfiguration(models.Model):
    class Provider(models.TextChoices):
        GEMINI = 'GEMINI', 'Google Gemini AI'
        GROQ = 'GROQ', 'Groq AI (Llama-3 / Mixtral)'
        OPENAI = 'OPENAI', 'OpenAI GPT-4o'
        OLLAMA = 'OLLAMA', 'Local Ollama LLM'
        MOCK = 'MOCK', 'Mock Testing Provider'

    class OCREngine(models.TextChoices):
        PADDLE = 'PADDLE', 'PaddleOCR Primary'
        TESSERACT = 'TESSERACT', 'PyTesseract Fallback'
        AUTO = 'AUTO', 'Auto-Detect Hybrid'

    provider = models.CharField(max_length=20, choices=Provider.choices, default=Provider.GEMINI)
    gemini_model_name = models.CharField(max_length=50, default='gemini-flash-latest')
    openai_model_name = models.CharField(max_length=50, default='gpt-4o-mini')
    ocr_engine = models.CharField(max_length=20, choices=OCREngine.choices, default=OCREngine.AUTO)
    preprocess_image = models.BooleanField(default=True, help_text="Enable deskewing, noise removal, and contrast enhancement.")
    confidence_threshold = models.FloatField(default=0.75, help_text="Threshold below which AI marks require mandatory review.")
    enable_rag_learning = models.BooleanField(default=True, help_text="Retrieve past teacher corrections as few-shot exemplars.")
    prompt_template = models.TextField(blank=True, help_text="Custom prompt instructions for the evaluation engine.")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"AI System Config ({self.get_provider_display()} - {self.get_ocr_engine_display()})"

    @classmethod
    def get_config(cls):
        config, _ = cls.objects.get_or_create(id=1)
        return config


class FeedbackCorrection(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='feedback_corrections')
    evaluation = models.OneToOneField(Evaluation, on_delete=models.CASCADE, related_name='correction', null=True, blank=True)
    student_answer = models.TextField()
    ai_suggested_marks = models.DecimalField(max_digits=5, decimal_places=2)
    teacher_final_marks = models.DecimalField(max_digits=5, decimal_places=2)
    correction_reason = models.TextField(blank=True, help_text="Explanation for why teacher adjusted AI score.")
    embedding = models.JSONField(default=list, blank=True, help_text="Vector embedding for semantic similarity search.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Correction Q{self.question.question_number}: {self.ai_suggested_marks} -> {self.teacher_final_marks}"


class AIMemoryLog(models.Model):
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='ai_memory_logs', null=True, blank=True)
    provider = models.CharField(max_length=50)
    model_version = models.CharField(max_length=50)
    prompt_snapshot = models.TextField()
    raw_response_json = models.JSONField(default=dict)
    confidence_score = models.FloatField(default=0.0)
    latency_ms = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AIMemoryLog [{self.provider}/{self.model_version}] - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


# ==========================================
# Production AI Answer Script Evaluation Models
# ==========================================

class StudentSubmission(models.Model):
    class Status(models.TextChoices):
        UPLOADED = 'UPLOADED', 'Uploaded'
        PREVIEW_READY = 'PREVIEW_READY', 'Preview Ready'
        WORKING_COPY_CREATED = 'WORKING_COPY_CREATED', 'Working Copy Created'
        PDF_GENERATED = 'PDF_GENERATED', 'PDF Generated'
        OCR_COMPLETE = 'OCR_COMPLETE', 'OCR Complete'
        SEGMENTED = 'SEGMENTED', 'Answer Segmented'
        MAPPING_COMPLETE = 'MAPPING_COMPLETE', 'Question Mapping Complete'
        WAITING_TEACHER_CONFIRMATION = 'WAITING_TEACHER_CONFIRMATION', 'Waiting for Teacher Confirmation'
        AI_EVALUATED = 'AI_EVALUATED', 'AI Evaluated'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Teacher Review'
        FINALIZED = 'FINALIZED', 'Finalized & Locked'
        ARCHIVED = 'ARCHIVED', 'Archived'
        FAILED = 'FAILED', 'Evaluation Failed'

    examination = models.ForeignKey(Examination, on_delete=models.CASCADE, related_name='student_submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_submissions', null=True, blank=True)
    student_name = models.CharField(max_length=200, default='Anonymous Student')
    student_roll_no = models.CharField(max_length=100, blank=True)
    script_file = models.FileField(upload_to='student_submissions/%Y/%m/')
    total_obtained_marks = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    total_max_marks = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    percentage = models.FloatField(default=0.0)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.UPLOADED)
    requires_manual_review = models.BooleanField(default=False)
    is_finalized = models.BooleanField(default=False, help_text="Set to True after teacher clicks Finalize Evaluation. Triggers temp file cleanup.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Submission: {self.student_name} ({self.student_roll_no}) - {self.examination.title}"


class SubmissionPage(models.Model):
    submission = models.ForeignKey(StudentSubmission, on_delete=models.CASCADE, related_name='pages')
    page_number = models.IntegerField(default=1)
    page_image = models.ImageField(upload_to='submission_pages/%Y/%m/')
    working_image_path = models.CharField(max_length=500, blank=True, help_text="Path to active working copy in submission_working/")
    version = models.IntegerField(default=1, help_text="Version incremented on each image edit (rotation, crop, contrast)")
    ocr_raw_text = models.TextField(blank=True)
    ocr_confidence = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Page {self.page_number} (v{self.version}) for {self.submission.student_name}"


class SubmissionAnswer(models.Model):
    submission = models.ForeignKey(StudentSubmission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='submission_answers')
    extracted_text = models.TextField(blank=True)
    ocr_confidence = models.FloatField(default=0.0)
    bounding_box_json = models.JSONField(default=dict, blank=True)
    page = models.ForeignKey(SubmissionPage, on_delete=models.SET_NULL, null=True, blank=True, related_name='answers')
    requires_manual_review = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer Q{self.question.question_number} - {self.submission.student_name}"


class EvaluationResult(models.Model):
    class ReviewStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending Teacher Review'
        APPROVED = 'APPROVED', 'Approved by Teacher'
        OVERRIDDEN = 'OVERRIDDEN', 'Overridden by Teacher'
        REJECTED = 'REJECTED', 'Rejected / Re-evaluate'

    submission_answer = models.OneToOneField(SubmissionAnswer, on_delete=models.CASCADE, related_name='evaluation_result')
    obtained_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    maximum_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    percentage = models.FloatField(default=0.0)
    strengths_json = models.JSONField(default=list, blank=True)
    mistakes_json = models.JSONField(default=list, blank=True)
    missing_points_json = models.JSONField(default=list, blank=True)
    rubric_breakdown_json = models.JSONField(default=list, blank=True)
    feedback_text = models.TextField(blank=True)
    confidence = models.FloatField(default=0.0)
    requires_manual_review = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=ReviewStatus.choices, default=ReviewStatus.PENDING)
    evaluated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Result Q{self.submission_answer.question.question_number}: {self.obtained_marks}/{self.maximum_marks}"


class EvaluationFeedback(models.Model):
    evaluation_result = models.ForeignKey(EvaluationResult, on_delete=models.CASCADE, related_name='detailed_feedbacks')
    criteria_name = models.CharField(max_length=255)
    allocated_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    awarded_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    comments = models.TextField(blank=True)

    def __str__(self):
        return f"{self.criteria_name}: {self.awarded_marks}/{self.allocated_marks}"


class TeacherReview(models.Model):
    class Action(models.TextChoices):
        APPROVE = 'APPROVE', 'Approved AI Score'
        OVERRIDE = 'OVERRIDE', 'Overrode Marks'
        REJECT = 'REJECT', 'Rejected Score'
        RE_EVALUATE = 'RE_EVALUATE', 'Requested AI Re-evaluation'

    evaluation_result = models.ForeignKey(EvaluationResult, on_delete=models.CASCADE, related_name='reviews')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=Action.choices)
    previous_marks = models.DecimalField(max_digits=5, decimal_places=2)
    new_marks = models.DecimalField(max_digits=5, decimal_places=2)
    review_comments = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.teacher.username}: {self.previous_marks} -> {self.new_marks} ({self.action})"


class EvaluationHistory(models.Model):
    evaluation_result = models.ForeignKey(EvaluationResult, on_delete=models.CASCADE, related_name='history')
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    old_marks = models.DecimalField(max_digits=5, decimal_places=2)
    new_marks = models.DecimalField(max_digits=5, decimal_places=2)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History: {self.old_marks} -> {self.new_marks} at {self.created_at}"


class EvaluationAttachment(models.Model):
    evaluation_result = models.ForeignKey(EvaluationResult, on_delete=models.CASCADE, related_name='attachments')
    file_name = models.CharField(max_length=255)
    attachment_file = models.FileField(upload_to='evaluation_attachments/%Y/%m/')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment: {self.file_name}"


class EvaluationAuditLog(models.Model):
    submission = models.ForeignKey(StudentSubmission, on_delete=models.CASCADE, related_name='audit_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    details_json = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AuditLog: {self.action} on {self.submission.id} at {self.timestamp}"


class SubmissionPDF(models.Model):
    submission = models.OneToOneField(StudentSubmission, on_delete=models.CASCADE, related_name='pdf_document')
    pdf_file = models.FileField(upload_to='submission_pdfs/%Y/%m/')
    page_count = models.IntegerField(default=1)
    file_size_bytes = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission PDF for {self.submission.student_name} ({self.page_count} pages)"


class SubmissionImage(models.Model):
    submission = models.ForeignKey(StudentSubmission, on_delete=models.CASCADE, related_name='raw_images')
    original_file = models.ImageField(upload_to='submission_raw_images/%Y/%m/')
    processed_file = models.ImageField(upload_to='submission_processed_images/%Y/%m/', null=True, blank=True)
    working_image_path = models.CharField(max_length=500, blank=True, help_text="Path to active working copy in submission_working/")
    version = models.IntegerField(default=1, help_text="Version incremented on each image edit (rotation, crop, contrast)")
    sequence_order = models.IntegerField(default=1)
    rotation_angle = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SubmissionImage #{self.sequence_order} (v{self.version}) for {self.submission.student_name}"


class OCRResult(models.Model):
    submission_page = models.ForeignKey(SubmissionPage, on_delete=models.CASCADE, related_name='ocr_results')
    engine_name = models.CharField(max_length=50, default='EASYOCR')
    page_confidence = models.FloatField(default=0.0)
    word_boxes_json = models.JSONField(default=list, help_text="Per-word bbox, text, and confidence ratings")
    line_boxes_json = models.JSONField(default=list, help_text="Per-line bbox and text")
    raw_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OCRResult ({self.engine_name}) Page {self.submission_page.page_number} - Conf: {self.page_confidence}"


class PromptHistory(models.Model):
    evaluation_result = models.ForeignKey(EvaluationResult, on_delete=models.CASCADE, related_name='prompt_history')
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    custom_prompt = models.TextField(blank=True)
    evaluation_mode = models.CharField(max_length=50, default='Rubric-based')
    strictness_level = models.CharField(max_length=30, default='Balanced')
    ai_provider = models.CharField(max_length=50, default='GEMINI')
    model_name = models.CharField(max_length=100, default='AUTO')
    temperature = models.FloatField(default=0.2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PromptHistory for Result #{self.evaluation_result.id} at {self.created_at}"


class QuestionDetection(models.Model):
    class DetectionMethod(models.TextChoices):
        OCR_PATTERN = 'OCR_PATTERN', 'OCR Pattern Matching'
        LAYOUT_POSITION = 'LAYOUT_POSITION', 'Layout & Position Analysis'
        LLM_SEMANTIC = 'LLM_SEMANTIC', 'LLM Semantic Classification'
        MANUAL_TEACHER = 'MANUAL_TEACHER', 'Manual Teacher Entry'

    submission_page = models.ForeignKey(SubmissionPage, on_delete=models.CASCADE, related_name='question_detections')
    question_number_raw = models.CharField(max_length=50, help_text="Exact string detected, e.g. Q.1, (1), ১")
    question_number_normalized = models.CharField(max_length=20, help_text="Normalized number string, e.g. 1, 2, 3")
    bbox_json = models.JSONField(default=dict, blank=True, help_text="Bounding box coordinates [ymin, xmin, ymax, xmax]")
    confidence = models.FloatField(default=0.0)
    detection_method = models.CharField(max_length=30, choices=DetectionMethod.choices, default=DetectionMethod.OCR_PATTERN)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Detection '{self.question_number_raw}' on Page {self.submission_page.page_number} (Conf: {self.confidence})"


class QuestionMapping(models.Model):
    class Status(models.TextChoices):
        AUTO_HIGH = 'AUTO_HIGH', 'High Confidence Auto Match'
        AMBIGUOUS = 'AMBIGUOUS', 'Ambiguous / Requires Teacher Review'
        MANUAL_OVERRIDE = 'MANUAL_OVERRIDE', 'Teacher Override Confirmed'

    submission = models.ForeignKey(StudentSubmission, on_delete=models.CASCADE, related_name='question_mappings')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='script_mappings')
    page_numbers_json = models.JSONField(default=list, help_text="Array of page numbers attached to this question answer")
    confidence = models.FloatField(default=0.0)
    mapping_status = models.CharField(max_length=30, choices=Status.choices, default=Status.AUTO_HIGH)
    is_confirmed = models.BooleanField(default=False)
    review_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('submission', 'question')

    def __str__(self):
        return f"Mapping Submission #{self.submission.id} Q{self.question.question_number} -> Pages {self.page_numbers_json} ({self.mapping_status})"


class MappingHistory(models.Model):
    submission = models.ForeignKey(StudentSubmission, on_delete=models.CASCADE, related_name='mapping_history')
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=50, help_text="e.g. AUTO_DETECTED, SEMANTIC_FALLBACK, TEACHER_OVERRIDE, CONFIRMED")
    details_json = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"MappingHistory #{self.id} for Submission {self.submission.id} - {self.action_type}"




