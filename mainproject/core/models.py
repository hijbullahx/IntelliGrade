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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.code} - {self.title}"


class Question(models.Model):
    examination = models.ForeignKey(Examination, on_delete=models.CASCADE, related_name='questions')
    question_number = models.CharField(max_length=10)
    prompt_text = models.TextField()
    max_marks = models.DecimalField(max_digits=5, decimal_places=2)

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

    def __str__(self):
        return f"Rubric for Q{self.question.question_number} ({self.question.examination.title})"


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
        OPENAI = 'OPENAI', 'OpenAI GPT-4o'
        MOCK = 'MOCK', 'Mock Testing Provider'

    class OCREngine(models.TextChoices):
        PADDLE = 'PADDLE', 'PaddleOCR Primary'
        TESSERACT = 'TESSERACT', 'PyTesseract Fallback'
        AUTO = 'AUTO', 'Auto-Detect Hybrid'

    provider = models.CharField(max_length=20, choices=Provider.choices, default=Provider.GEMINI)
    gemini_model_name = models.CharField(max_length=50, default='gemini-1.5-flash')
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


