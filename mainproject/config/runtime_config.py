import os
from pathlib import Path
from typing import Iterable, List, Optional
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[1]

def load_environment_variables():
    """
    Loads environment variables from:
    1. Custom path specified via INTELLIGRADE_ENV_FILE environment variable.
    2. Default .env file in BASE_DIR if it exists.
    3. Keeps existing os.environ variables intact.
    Does not crash if .env does not exist physically.
    """
    custom_env_path = os.environ.get('INTELLIGRADE_ENV_FILE')
    target_env_file = None

    if custom_env_path and os.path.exists(custom_env_path):
        target_env_file = Path(custom_env_path)
    else:
        default_env = PROJECT_ROOT / '.env'
        if default_env.exists():
            target_env_file = default_env

    if target_env_file and target_env_file.exists():
        try:
            with open(target_env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
        except Exception as e:
            print(f"[RUNTIME CONFIG WARNING] Error reading env file {target_env_file}: {e}")

def detect_runtime_environment() -> str:
    """Returns detected runtime environment: 'CODESPACES', 'PYTHONANYWHERE', or 'LOCAL'."""
    if os.environ.get('CODESPACES') == 'true' or 'GITHUB_CODESPACE_TOKEN' in os.environ:
        return 'CODESPACES'
    if 'PYTHONANYWHERE_DOMAIN' in os.environ or 'PYTHONANYWHERE_SITE' in os.environ:
        return 'PYTHONANYWHERE'
    return 'LOCAL'


def get_env_value(name: str, default: Optional[str] = None, fallback_names: Iterable[str] = ()) -> Optional[str]:
    for candidate_name in (name, *fallback_names):
        value = os.environ.get(candidate_name)
        if value is not None and value.strip() != '':
            return value.strip()
    return default


def get_env_bool(name: str, default: bool = False, fallback_names: Iterable[str] = ()) -> bool:
    raw_value = get_env_value(name, None, fallback_names)
    if raw_value is None:
        return default
    return raw_value.lower() in {'1', 'true', 'yes', 'on'}


def split_csv_value(raw_value: Optional[str]) -> List[str]:
    if not raw_value:
        return []
    return [item.strip() for item in raw_value.split(',') if item.strip()]


def dedupe_preserving_order(values: Iterable[str]) -> List[str]:
    seen = set()
    ordered_values: List[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            ordered_values.append(value)
    return ordered_values


def get_env_list(name: str, default: Optional[Iterable[str]] = None, fallback_names: Iterable[str] = ()) -> List[str]:
    raw_value = get_env_value(name, None, fallback_names)
    if raw_value is None:
        return dedupe_preserving_order(default or [])
    return dedupe_preserving_order(split_csv_value(raw_value))


def normalize_origin(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    candidate = value.strip().rstrip('/')
    if '://' not in candidate:
        return None
    parsed = urlparse(candidate)
    if not parsed.scheme or not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}"


def get_env_origin_list(name: str, default: Optional[Iterable[str]] = None, fallback_names: Iterable[str] = ()) -> List[str]:
    raw_value = get_env_value(name, None, fallback_names)
    if raw_value is None:
        normalized_defaults = [normalize_origin(value) for value in (default or [])]
        return dedupe_preserving_order(origin for origin in normalized_defaults if origin)

    origins = []
    for item in split_csv_value(raw_value):
        origin = normalize_origin(item)
        if origin:
            origins.append(origin)
    return dedupe_preserving_order(origins)


def build_default_allowed_hosts(debug: bool, runtime_environment: Optional[str] = None) -> List[str]:
    runtime_environment = runtime_environment or detect_runtime_environment()
    hosts: List[str] = []

    if debug:
        hosts.extend(['localhost', '127.0.0.1'])

    if runtime_environment == 'CODESPACES':
        hosts.append('.app.github.dev')
    elif runtime_environment == 'PYTHONANYWHERE':
        hosts.append('.pythonanywhere.com')

    return dedupe_preserving_order(hosts)


def build_default_csrf_trusted_origins(
    debug: bool,
    runtime_environment: Optional[str] = None,
    site_url: Optional[str] = None,
    public_url: Optional[str] = None,
) -> List[str]:
    runtime_environment = runtime_environment or detect_runtime_environment()
    origins: List[str] = []

    if debug:
        origins.extend([
            'http://localhost:8000',
            'http://127.0.0.1:8000',
            'https://localhost:8000',
            'https://127.0.0.1:8000',
            'http://localhost:3000',
            'http://127.0.0.1:3000',
        ])

    if runtime_environment == 'CODESPACES':
        origins.extend([
            'https://*.app.github.dev',
            'https://*.githubpreview.dev',
        ])

    for candidate in (site_url, public_url):
        origin = normalize_origin(candidate)
        if origin:
            origins.append(origin)

    return dedupe_preserving_order(origins)


def get_effective_public_origin() -> Optional[str]:
    for candidate_name in ('DJANGO_PUBLIC_URL', 'PUBLIC_URL', 'DJANGO_SITE_URL', 'SITE_URL', 'APP_URL', 'BASE_URL'):
        origin = normalize_origin(os.environ.get(candidate_name))
        if origin:
            return origin
    return None

def is_cuda_available() -> bool:
    """Checks whether PyTorch CUDA GPU acceleration is available."""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def build_database_config(base_dir: Path) -> dict:
    """
    Builds environment-aware Django DATABASES configuration.
    Supports:
      - DB_ENGINE=sqlite (default): uses SQLite at BASE_DIR / 'db.sqlite3'
      - DB_ENGINE=postgresql / postgres: uses PostgreSQL with environment variables
    
    If PostgreSQL is selected, validates that required variables (DB_NAME, DB_USER, DB_PASSWORD, DB_HOST) exist.
    Raises ImproperlyConfigured with a clear error message if any are missing.
    """
    from django.core.exceptions import ImproperlyConfigured

    raw_engine = get_env_value('DB_ENGINE', default='sqlite', fallback_names=('DATABASE_ENGINE',)).lower()

    if raw_engine in ('postgres', 'postgresql', 'django.db.backends.postgresql'):
        db_name = get_env_value('DB_NAME', fallback_names=('DATABASE_NAME', 'POSTGRES_DB'))
        db_user = get_env_value('DB_USER', fallback_names=('DATABASE_USER', 'POSTGRES_USER'))
        db_password = get_env_value('DB_PASSWORD', fallback_names=('DATABASE_PASSWORD', 'POSTGRES_PASSWORD'))
        db_host = get_env_value('DB_HOST', default='localhost', fallback_names=('DATABASE_HOST', 'POSTGRES_HOST'))
        db_port = get_env_value('DB_PORT', default='5432', fallback_names=('DATABASE_PORT', 'POSTGRES_PORT'))
        conn_max_age_str = get_env_value('DB_CONN_MAX_AGE', default='60', fallback_names=('DATABASE_CONN_MAX_AGE',))

        missing = []
        if not db_name:
            missing.append('DB_NAME')
        if not db_user:
            missing.append('DB_USER')
        if not db_password:
            missing.append('DB_PASSWORD')
        if not db_host:
            missing.append('DB_HOST')

        if missing:
            raise ImproperlyConfigured(
                f"PostgreSQL selected (DB_ENGINE={raw_engine}) but required configuration is missing: {', '.join(missing)}."
            )

        try:
            conn_max_age = int(conn_max_age_str)
        except (TypeError, ValueError):
            conn_max_age = 60

        print(f"[DATABASE CONFIG] Database backend: PostgreSQL | Database: {db_name} | User: {db_user} | Host: {db_host}:{db_port}")

        return {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': db_name,
                'USER': db_user,
                'PASSWORD': db_password,
                'HOST': db_host,
                'PORT': str(db_port),
                'CONN_MAX_AGE': conn_max_age,
            }
        }
    else:
        # SQLite (default)
        sqlite_db_path = base_dir / 'db.sqlite3'
        print(f"[DATABASE CONFIG] Database backend: SQLite | Database file: {sqlite_db_path.name}")
        return {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': sqlite_db_path,
                'OPTIONS': {
                    'timeout': 30,
                },
            }
        }

