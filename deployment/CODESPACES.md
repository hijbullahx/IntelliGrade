# Deploying IntelliGrade on GitHub Codespaces

IntelliGrade runs out-of-the-box on GitHub Codespaces using the exact same global codebase, provider failover engine, and scanner algorithms as your local environment.

## 1. Environment Variable Setup

In your GitHub repository settings, navigate to **Settings -> Secrets and variables -> Codespaces** and set the following secrets:

- `GEMINI_API_KEY`: Your Google Gemini API Key
- `GROQ_API_KEY`: Your Groq Cloud API Key
- `OPENAI_API_KEY`: Your OpenAI API Key
- `DEFAULT_AI_PROVIDER`: `GROQ` (or `GEMINI`)

Optional deployment settings for custom origins:

- `DJANGO_ALLOWED_HOSTS`: Comma-separated host list, for example `localhost,127.0.0.1,.app.github.dev`
- `DJANGO_CSRF_TRUSTED_ORIGINS`: Comma-separated full origins, for example `https://localhost:8000,https://*.app.github.dev`
- `DJANGO_PUBLIC_URL`: Your external Codespaces URL when you want an explicit public origin

Alternatively, inside your active Codespace terminal, create a `.env` file in `mainproject/.env`:

```bash
cd mainproject
cp ../deployment/.env.example .env
# Edit .env and paste your API keys
```

## 2. Installation & Verification

Run the following commands in the Codespace terminal:

```bash
cd mainproject
pip install -r requirements.txt
python manage.py check
python manage.py check_deployment_config
python manage.py check_ai_config
```

## 3. Running the Server

```bash
python manage.py runserver 0.0.0.0:8000
```
Codespaces will automatically forward port 8000. Open the forwarded port in your browser.
