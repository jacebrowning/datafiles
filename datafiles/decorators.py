import dataclasses
from typing import Dict, Optional

from .fields import Field
from .models import Model, ModelMeta


def sync(pattern: str, fields: Optional[Dict[str, Field]] = None):
    """Decorator to synchronize a data class to the specified path."""

    def decorator(cls):
        if not dataclasses.is_dataclass(cls):
            raise ValueError(f'{cls} must be a data class')

        m = getattr(cls, 'Meta', ModelMeta)
        m.datafile_pattern = getattr(m, 'datafile_pattern', None) or pattern
        m.datafile_fields = getattr(m, 'datafile_fields', None) or fields

        cls.Meta = m
        cls.datafile = property(Model.get_datafile)

        return cls

    return decorator
