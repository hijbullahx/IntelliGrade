"""
Phusion Passenger WSGI entry point when the cPanel application root is configured as mainproject/.
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainproject.settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
