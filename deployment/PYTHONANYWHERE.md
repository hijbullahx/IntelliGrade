# Deploying IntelliGrade on PythonAnywhere

IntelliGrade uses a single codebase architecture. The exact same project code running locally and on Codespaces runs seamlessly on PythonAnywhere.

## 1. Clone & Environment Setup

In the PythonAnywhere Console:

```bash
cd ~
git clone https://github.com/hijbullahx/IntelliGrade.git
cd IntelliGrade/mainproject

# Create virtualenv and install dependencies
mkvirtualenv --python=python3.10 intelligrade-env
pip install -r requirements.txt
```

## 2. Environment Variable Configuration

On PythonAnywhere, you can configure your environment variables in your WSGI file or in `mainproject/.env`:

Create `mainproject/.env`:
```bash
cat << 'EOF' > .env
GEMINI_API_KEY="your-gemini-key"
GROQ_API_KEY="your-groq-key"
OPENAI_API_KEY="your-openai-key"
DEFAULT_AI_PROVIDER="GROQ"
EOF
```

Alternatively, specify an external environment file using:
```bash
export INTELLIGRADE_ENV_FILE=/home/yourusername/secure_keys.env
```

## 3. WSGI File Configuration

In the PythonAnywhere Web Tab, set the WSGI configuration file:

```python
import os
import sys

path = '/home/yourusername/IntelliGrade/mainproject'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'mainproject.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 4. Diagnostics & Verification

Run the configuration diagnostic:
```bash
python manage.py check_ai_config
```

Verify that all providers output `READY` and EasyOCR CPU fallback initializes cleanly.
