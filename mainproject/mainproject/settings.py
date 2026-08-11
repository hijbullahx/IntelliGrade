"""
Django settings for mainproject project.
"""

import os
from pathlib import Path

from config.runtime_config import (
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

load_environment_variables()

<<<<<<< HEAD
CSRF_TRUSTED_ORIGINS = [
    'https://*.app.github.dev',
    'https://*.githubpreview.dev',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

# ==========================================
# AI Engine Credentials Configuration (Auto-loads .env)
# ==========================================
env_path = BASE_DIR / '.env'
if env_path.exists():
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except Exception:
        pass
=======
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
SITE_URL = DJANGO_SITE_URL or DJANGO_PUBLIC_URL or ''
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
>>>>>>> 08da691 (feat: update deployment configurations and enhance environment variable management)

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 30,
        }
    }
}

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
