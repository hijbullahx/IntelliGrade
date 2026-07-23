from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('controller/login/', views.exam_controller_login, name='exam_controller_login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/exam-controller/', views.exam_controller_dashboard, name='exam_controller_dashboard'),
    path('controller/add-faculty/', views.add_faculty, name='add_faculty'),
    path('controller/add-student/', views.add_student, name='add_student'),
    path('controller/rechecks/', views.rechecks_list, name='rechecks_list'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/dept-head/', views.dept_head_dashboard, name='dept_head_dashboard'),
    path('exams/create/', views.exam_create, name='exam_create'),
    path('scripts/upload/', views.script_upload, name='script_upload'),
    path('evaluation/<int:script_id>/review/', views.grading_workbench, name='grading_workbench'),
    path('evaluation/review/', views.grading_workbench, name='grading_workbench_default'),
]
