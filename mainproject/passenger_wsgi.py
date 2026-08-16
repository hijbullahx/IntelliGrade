"""
Phusion Passenger WSGI entry point when the cPanel application root is configured as mainproject/.
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Detect virtual environment Python interpreter
VENV_PYTHON = None
for venv_name in ('venv', '.venv', 'env'):
    for candidate_dir in (BASE_DIR.parent, BASE_DIR):
        py_candidate = candidate_dir / venv_name / 'bin' / 'python'
        if py_candidate.exists():
            VENV_PYTHON = str(py_candidate.resolve())
            break
    if VENV_PYTHON:
        break

# Re-execute under the virtual environment interpreter if currently running under system Python
if VENV_PYTHON:
    current_python = str(Path(sys.executable).resolve())
    if current_python != VENV_PYTHON:
        os.execl(VENV_PYTHON, VENV_PYTHON, *sys.argv)

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainproject.settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

