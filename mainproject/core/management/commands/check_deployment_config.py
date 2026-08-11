from urllib.parse import urlparse

from django.conf import settings
from django.core.management.base import BaseCommand

from config.runtime_config import detect_runtime_environment


def _format_list(values):
    return '[%s]' % ', '.join(values) if values else '[]'


def _get_detected_host():
    for candidate in (getattr(settings, 'PUBLIC_URL', ''), getattr(settings, 'SITE_URL', '')):
        if candidate:
            parsed = urlparse(candidate)
            if parsed.hostname:
                return parsed.hostname

    if getattr(settings, 'RUNTIME_ENVIRONMENT', '') == 'CODESPACES':
        return 'localhost'

    return '127.0.0.1'


class Command(BaseCommand):
    help = 'Prints IntelliGrade deployment and origin configuration without secrets.'

    def handle(self, *args, **options):
        runtime_environment = getattr(settings, 'RUNTIME_ENVIRONMENT', detect_runtime_environment())
        self.stdout.write('=' * 50)
        self.stdout.write('INTELLIGRADE DEPLOYMENT CONFIG')
        self.stdout.write('=' * 50)

        self.stdout.write(f'\nDEBUG: {settings.DEBUG}')
        self.stdout.write(f'Environment: {runtime_environment}')
        self.stdout.write(f'Detected host: {_get_detected_host()}')
        self.stdout.write(f'Detected site URL: {getattr(settings, "SITE_URL", "") or "<not set>"}')
        self.stdout.write(f'Detected public URL: {getattr(settings, "PUBLIC_URL", "") or "<not set>"}')
        self.stdout.write(f'ALLOWED_HOSTS: {_format_list(getattr(settings, "ALLOWED_HOSTS", []))}')
        self.stdout.write(f'CSRF_TRUSTED_ORIGINS: {_format_list(getattr(settings, "CSRF_TRUSTED_ORIGINS", []))}')
        self.stdout.write(f'CORS_ALLOWED_ORIGINS: {_format_list(getattr(settings, "CORS_ALLOWED_ORIGINS", []))}')
        self.stdout.write(f'CSRF_COOKIE_SECURE: {getattr(settings, "CSRF_COOKIE_SECURE", False)}')
        self.stdout.write(f'SESSION_COOKIE_SECURE: {getattr(settings, "SESSION_COOKIE_SECURE", False)}')
        self.stdout.write(f'SECURE_SSL_REDIRECT: {getattr(settings, "SECURE_SSL_REDIRECT", False)}')
        self.stdout.write(f'Proxy SSL: {getattr(settings, "SECURE_PROXY_SSL_HEADER", None) or "<disabled>"}')
        self.stdout.write(f'Use X-Forwarded Host: {getattr(settings, "USE_X_FORWARDED_HOST", False)}')
        self.stdout.write(f'Use X-Forwarded Port: {getattr(settings, "USE_X_FORWARDED_PORT", False)}')

        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('Deployment configuration check completed.'))
        self.stdout.write('=' * 50 + '\n')