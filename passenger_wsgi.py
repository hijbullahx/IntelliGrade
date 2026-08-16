"""
Phusion Passenger WSGI entry point for IntelliGrade on cPanel / Cloud environments.
Dynamically resolves paths and re-executes itself under the project virtualenv Python
interpreter prior to importing Django.
"""
import os
import sys
from pathlib import Path

# Resolve paths relative to this entry point file
REPO_ROOT = Path(__file__).resolve().parent
MAINPROJECT_DIR = REPO_ROOT / 'mainproject'

# Detect virtual environment Python interpreter (supports venv, .venv, env)
VENV_PYTHON = None
for venv_name in ('venv', '.venv', 'env'):
    py_candidate = REPO_ROOT / venv_name / 'bin' / 'python'
    if py_candidate.exists():
        VENV_PYTHON = str(py_candidate)
        break

# Re-execute under the virtual environment interpreter if currently running under system Python
if VENV_PYTHON and sys.executable != VENV_PYTHON:
    if sys.argv and sys.argv[0] != '-c':
        os.execl(VENV_PYTHON, VENV_PYTHON, *sys.argv)
    else:
        os.execl(VENV_PYTHON, VENV_PYTHON, __file__)

# Ensure mainproject and repository root are on the Python path
for path_entry in (str(MAINPROJECT_DIR), str(REPO_ROOT)):
    if path_entry not in sys.path:
        sys.path.insert(0, path_entry)

# Ensure Django settings module is configured
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainproject.settings')

# Load and expose the WSGI application callable
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

