import dataclasses
from typing import Dict, Optional

from .fields import Field
from .models import Metadata, Model


def sync(path_pattern: str, mapped_fields: Optional[Dict[str, Field]] = None):
    """Decorator to synchronize a data class to the specified path."""

    def decorator(cls):
        if not dataclasses.is_dataclass(cls):
            raise ValueError(f'{cls} must be a data class')

        meta = getattr(cls, 'Meta', Metadata())
        meta.form_path = getattr(meta, 'form_path', None) or path_pattern
        meta.form_fields = getattr(meta, 'form_fields', None) or mapped_fields
        cls.Meta = meta

        cls.form = property(Model.get_form)

        return cls

    return decorator
