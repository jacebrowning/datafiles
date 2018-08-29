from typing import Dict, Optional

from .fields import Field
from .models import patch_dataclass


def sync(pattern: str, fields: Optional[Dict[str, Field]] = None):
    """Decorator to synchronize a data class to the specified path."""

    def decorator(cls):
        return patch_dataclass(cls, pattern, fields)

    return decorator
