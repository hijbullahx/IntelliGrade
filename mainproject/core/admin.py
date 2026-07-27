from django.contrib import admin
from .models import (
    Profile, College, School, Department, Course, Examination,
    Question, Rubric, AnswerScript, AnswerSegment, Evaluation
)

@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'college', 'created_at')
    list_filter = ('college',)
    search_fields = ('name', 'code')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'school', 'college', 'created_at')
    list_filter = ('school', 'college')
    search_fields = ('name', 'code')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'department', 'created_at')
    list_filter = ('department',)
    search_fields = ('code', 'title')

@admin.register(Examination)
class ExaminationAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'exam_date', 'total_marks', 'status', 'created_by')
    list_filter = ('status', 'course__department', 'exam_date')
    search_fields = ('title', 'course__code', 'course__title')

class RubricInline(admin.StackedInline):
    model = Rubric
    extra = 0

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('examination', 'question_number', 'max_marks')
    list_filter = ('examination',)
    search_fields = ('question_number', 'prompt_text')
    inlines = [RubricInline]

@admin.register(Rubric)
class RubricAdmin(admin.ModelAdmin):
    list_display = ('question', 'criteria')
    search_fields = ('question__question_number', 'criteria', 'ideal_answer')

class AnswerSegmentInline(admin.TabularInline):
    model = AnswerSegment
    extra = 0

@admin.register(AnswerScript)
class AnswerScriptAdmin(admin.ModelAdmin):
    list_display = ('student', 'examination', 'status', 'uploaded_at')
    list_filter = ('status', 'examination')
    search_fields = ('student__username', 'examination__title')
    inlines = [AnswerSegmentInline]

@admin.register(AnswerSegment)
class AnswerSegmentAdmin(admin.ModelAdmin):
    list_display = ('script', 'question', 'ocr_confidence')
    list_filter = ('question__examination',)

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('segment', 'ai_suggested_marks', 'teacher_final_marks', 'status', 'confidence_score')
    list_filter = ('status',)
    search_fields = ('segment__script__student__username', 'ai_feedback', 'teacher_notes')

