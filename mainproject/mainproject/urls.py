from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static('/exam_questions/', document_root=settings.MEDIA_ROOT / 'exam_questions')
    urlpatterns += static('/course_outlines/', document_root=settings.MEDIA_ROOT / 'course_outlines')
    urlpatterns += static('/answer_scripts/', document_root=settings.MEDIA_ROOT / 'answer_scripts')
    urlpatterns += static('/routines/', document_root=settings.MEDIA_ROOT / 'routines')
