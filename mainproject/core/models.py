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

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
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

