"""
Phusion Passenger WSGI entry point for IntelliGrade on cPanel / Cloud environments.
Dynamically resolves paths so that the Django application works reliably without
hardcoded paths or manual environment overrides.
"""
import os
import sys
from pathlib import Path

# Resolve paths relative to this entry point file
REPO_ROOT = Path(__file__).resolve().parent
MAINPROJECT_DIR = REPO_ROOT / 'mainproject'

# Ensure mainproject and repository root are on the Python path
for path_entry in (str(MAINPROJECT_DIR), str(REPO_ROOT)):
    if path_entry not in sys.path:
        sys.path.insert(0, path_entry)

# Ensure Django settings module is configured
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainproject.settings')

# Load and expose the WSGI application callable
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
