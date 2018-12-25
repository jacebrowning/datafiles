import dataclasses
from typing import Dict, Optional

from .converters import Converter
from .models import create_model


def datafile(
    pattern: str,
    attrs: Optional[Dict[str, Converter]] = None,
    manual: bool = False,
    defaults: bool = False,
):
    """Synchronize a data class to the specified path."""

    def decorator(cls):
        if dataclasses.is_dataclass(cls):
            dataclass = cls
        else:
            dataclass = dataclasses.dataclass(cls)

        return create_model(
            dataclass, attrs=attrs, pattern=pattern, manual=manual, defaults=defaults
        )

    return decorator
