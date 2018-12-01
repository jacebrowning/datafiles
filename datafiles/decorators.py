from typing import Dict, Optional

from .converters import Converter
from .models import create_model


def sync(
    pattern: str,
    attrs: Optional[Dict[str, Converter]] = None,
    manual: bool = False,
    defaults: bool = False,
):
    """Decorator to synchronize a data class to the specified path."""

    def decorator(cls):
        return create_model(
            cls, attrs=attrs, pattern=pattern, manual=manual, defaults=defaults
        )

    return decorator
