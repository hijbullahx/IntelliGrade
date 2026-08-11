import os
from pathlib import Path
from .paths import get_base_dir

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
        default_env = get_base_dir() / '.env'
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

def is_cuda_available() -> bool:
    """Checks whether PyTorch CUDA GPU acceleration is available."""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False
