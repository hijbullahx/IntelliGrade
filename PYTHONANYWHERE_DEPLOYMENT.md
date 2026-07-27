# PythonAnywhere Free Account Deployment Guide for IntelliGrade

This document guides you step-by-step through deploying the IntelliGrade Django application completely free on [PythonAnywhere](https://www.pythonanywhere.com).

---

## 🛠️ Step 0: Commit and Push Workspace Changes to GitHub

Before deploying, ensure your local changes (`requirements.txt`, `.gitignore`, and `settings.py`) are pushed to your GitHub repository:

```bash
git add .
git commit -m "Configure workspace for PythonAnywhere deployment"
git push origin main
```

---

## 🚀 Step 1: Open Bash Console on PythonAnywhere

1. Log in to your [PythonAnywhere Account](https://www.pythonanywhere.com).
2. Go to your **Dashboard**.
3. Under **Consoles**, click on **Bash**.

---

## 📂 Step 2: Clone Your GitHub Repository

In the PythonAnywhere Bash console, clone your repo:

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

> Replace `YOUR_GITHUB_USERNAME` and `YOUR_REPO_NAME` with your GitHub username and repository name.

---

## 🐍 Step 3: Create & Activate Virtual Environment

Inside your repository directory on PythonAnywhere, run:

```bash
python3.10 -m venv myenv
source myenv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🗄️ Step 4: Run Migrations & Collect Static Files

Navigate into `mainproject` directory (where `manage.py` resides):

```bash
cd mainproject
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

Follow the prompts to set up your superuser username, email, and password.

---

## 🌐 Step 5: Create a Web App on PythonAnywhere

1. Click on the **Web** tab in the top navigation bar of PythonAnywhere.
2. Click **Add a new web app**.
3. Click **Next** (accepting `yourusername.pythonanywhere.com`).
4. Select **Manual configuration** *(Do NOT select Django here as we are using a custom virtualenv)*.
5. Choose **Python 3.10** and click **Next**.

---

## ⚙️ Step 6: Configure Paths and Virtualenv

On your Web App setup page:

1. **Source code**: Set to:
   `/home/yourusername/YOUR_REPO_NAME/mainproject`
2. **Working directory**: Set to:
   `/home/yourusername/YOUR_REPO_NAME/mainproject`
3. **Virtualenv**: Set to:
   `/home/yourusername/YOUR_REPO_NAME/myenv`

> Replace `yourusername` with your PythonAnywhere username and `YOUR_REPO_NAME` with your GitHub repository name.

---

## 📝 Step 7: Configure WSGI File

1. On the Web App configuration tab, click the link next to **WSGI configuration file** (e.g., `/var/www/yourusername_pythonanywhere_com_wsgi.py`).
2. **Delete everything** inside the file.
3. Paste the following configuration:

```python
import os
import sys

# Path to the directory containing manage.py
path = '/home/yourusername/YOUR_REPO_NAME/mainproject'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'mainproject.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

4. Click **Save** in the top-right corner.

---

## 🎨 Step 8: Set Up Static Files Mapping

1. Go back to the **Web** tab.
2. Scroll down to the **Static files** section.
3. Add a new static file mapping:
   - **URL**: `/static/`
   - **Directory**: `/home/yourusername/YOUR_REPO_NAME/mainproject/staticfiles`

---

## 🔄 Step 9: Reload and Launch Your App!

1. At the top of the **Web** tab, click the green **Reload yourusername.pythonanywhere.com** button.
2. Visit `https://yourusername.pythonanywhere.com` in your browser.

🎉 **Your IntelliGrade Django web application is now live on PythonAnywhere!**
