#!/bin/bash
# ==============================================================================
#  IntelliGrade PythonAnywhere Deployment / Update Helper Script
# ==============================================================================

echo "🚀 Starting PythonAnywhere update..."

# 1. Pull latest changes from GitHub
git pull origin main

# 2. Activate Virtual Environment
if [ -d "../myenv" ]; then
    source ../myenv/bin/activate
elif [ -d "myenv" ]; then
    source myenv/bin/activate
fi

# 3. Enter Django project directory
cd mainproject

# 4. Run migrations & collect static files
python manage.py migrate
python manage.py collectstatic --noinput

# 5. Automatically reload PythonAnywhere Web Server
WSGI_FILE=$(ls /var/www/*_pythonanywhere_com_wsgi.py 2>/dev/null | head -n 1)
if [ -n "$WSGI_FILE" ]; then
    touch "$WSGI_FILE"
    echo "✅ Success! PythonAnywhere web app has been updated and reloaded."
else
    echo "✅ Success! Please click 'Reload' in PythonAnywhere Web Tab if needed."
fi
