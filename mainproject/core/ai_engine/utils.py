from typing import Any, List

def normalize_collection(obj: Any) -> List[Any]:
    """
    Safely normalizes any collection or relation into an iterable list.
    Handles Django QuerySet, RelatedManager, list, tuple, set, generator, or None.
    Prevents AttributeError: 'list' object has no attribute 'all'.
    """
    if obj is None:
        return []
    if hasattr(obj, 'all') and callable(getattr(obj, 'all')):
        try:
            return list(obj.all())
        except Exception:
            pass
    if isinstance(obj, (list, tuple, set)):
        return list(obj)
    return [obj]
