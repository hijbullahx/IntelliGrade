"""
Django settings for mainproject project.
"""

import os
from pathlib import Path

from config.runtime_config import (
    build_database_config,
    build_default_allowed_hosts,
    build_default_csrf_trusted_origins,
    detect_runtime_environment,
    get_env_bool,
    get_env_list,
    get_env_origin_list,
    get_env_value,
    load_environment_variables,
)

BASE_DIR = Path(__file__).resolve().parent.parent

load_environment_variables(base_dir=BASE_DIR)

RUNTIME_ENVIRONMENT = detect_runtime_environment()
DEBUG = get_env_bool('DJANGO_DEBUG', default=get_env_bool('DEBUG', default=True), fallback_names=('DEBUG',))
SECRET_KEY = get_env_value(
    'DJANGO_SECRET_KEY',
    default=os.environ.get('SECRET_KEY', 'django-insecure-%%-1)(=bufg&63^uk#*atap+qjp6pgv@q&2s12vh#9wsydiedz'),
    fallback_names=('SECRET_KEY',),
)

ALLOWED_HOSTS = get_env_list(
    'DJANGO_ALLOWED_HOSTS',
    default=build_default_allowed_hosts(DEBUG, RUNTIME_ENVIRONMENT),
    fallback_names=('ALLOWED_HOSTS',),
)

DJANGO_SITE_URL = get_env_value('DJANGO_SITE_URL', fallback_names=('SITE_URL', 'BASE_URL', 'APP_URL', 'PUBLIC_URL'))
DJANGO_PUBLIC_URL = get_env_value('DJANGO_PUBLIC_URL', fallback_names=('PUBLIC_URL', 'APP_URL', 'BASE_URL', 'SITE_URL'))
SITE_URL = os.getenv('SITE_URL', DJANGO_SITE_URL or DJANGO_PUBLIC_URL or 'http://127.0.0.1:8000')
PUBLIC_URL = DJANGO_PUBLIC_URL or DJANGO_SITE_URL or ''
BASE_URL = PUBLIC_URL or SITE_URL
APP_URL = PUBLIC_URL or SITE_URL

CSRF_TRUSTED_ORIGINS = get_env_origin_list(
    'DJANGO_CSRF_TRUSTED_ORIGINS',
    default=build_default_csrf_trusted_origins(DEBUG, RUNTIME_ENVIRONMENT, site_url=SITE_URL, public_url=PUBLIC_URL),
    fallback_names=('CSRF_TRUSTED_ORIGINS',),
)

CORS_ALLOWED_ORIGINS = get_env_origin_list(
    'DJANGO_CORS_ALLOWED_ORIGINS',
    default=[],
    fallback_names=('CORS_ALLOWED_ORIGINS',),
)

USE_X_FORWARDED_HOST = RUNTIME_ENVIRONMENT in {'CODESPACES', 'PYTHONANYWHERE'}
USE_X_FORWARDED_PORT = USE_X_FORWARDED_HOST
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') if USE_X_FORWARDED_HOST else None
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = get_env_bool('DJANGO_SECURE_SSL_REDIRECT', default=False, fallback_names=('SECURE_SSL_REDIRECT',))

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
DEFAULT_AI_PROVIDER = os.environ.get('DEFAULT_AI_PROVIDER', 'GROQ')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core.apps.CoreConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mainproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mainproject.wsgi.application'

DATABASES = build_database_config(BASE_DIR)

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Production & Institutional Email Configuration (intelligrade@dsr.iubat.ac.bd)
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', os.getenv('DJANGO_EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend' if os.getenv('EMAIL_HOST_USER') else 'django.core.mail.backends.console.EmailBackend'))
EMAIL_HOST = os.getenv('EMAIL_HOST', 'mail.dsr.iubat.ac.bd')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 465))
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'True').lower() in ('true', '1')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'False').lower() in ('true', '1')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'intelligrade@dsr.iubat.ac.bd')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'IntelliGrade Support <intelligrade@dsr.iubat.ac.bd>')
SERVER_EMAIL = os.getenv('SERVER_EMAIL', 'intelligrade@dsr.iubat.ac.bd')

# Cache configuration for Security OTP Lifecycle
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'intelligrade-security-cache',
    }
}

# Production Security & Session Hardening
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() in ('true', '1')
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost,*').split(',') if h.strip()]
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.getenv('CSRF_TRUSTED_ORIGINS', 'http://127.0.0.1:8000,http://localhost:8000').split(',') if o.strip()]

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

