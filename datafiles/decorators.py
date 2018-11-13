from typing import Dict, Optional

from .converters import Converter
from .models import patch_dataclass


def sync(
    pattern: str,
    attrs: Optional[Dict[str, Converter]] = None,
    manual: bool = False,
):
    """Decorator to synchronize a data class to the specified path."""

    def decorator(cls):
        return patch_dataclass(cls, pattern, attrs, manual=manual)

    return decorator
