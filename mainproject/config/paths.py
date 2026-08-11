import os
from pathlib import Path
from django.conf import settings

def get_base_dir() -> Path:
    """Returns the Django BASE_DIR path object."""
    if hasattr(settings, 'BASE_DIR') and settings.BASE_DIR:
        return Path(settings.BASE_DIR)
    # Fallback if Django settings not loaded yet
    return Path(__file__).resolve().parent.parent

def get_media_root() -> str:
    """Returns the Django MEDIA_ROOT path as string."""
    if hasattr(settings, 'MEDIA_ROOT') and settings.MEDIA_ROOT:
        return str(settings.MEDIA_ROOT)
    return str(get_base_dir() / 'media')

def get_static_root() -> str:
    """Returns the Django STATIC_ROOT path as string."""
    if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
        return str(settings.STATIC_ROOT)
    return str(get_base_dir() / 'staticfiles')

def get_trace_dir(subfolder: str = None) -> str:
    """
    Returns cross-platform trace directory path.
    Guarantees no hardcoded OS drives (D:\ or /home/) are used.
    """
    base_trace = os.path.join(get_media_root(), 'request_trace')
    if subfolder:
        base_trace = os.path.join(base_trace, subfolder)
    os.makedirs(base_trace, exist_ok=True)
    return base_trace
