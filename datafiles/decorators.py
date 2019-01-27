import dataclasses
from typing import Dict, Optional

from .converters import Converter
from .models import ModelMeta, create_model


def datafile(
    pattern: str,
    attrs: Optional[Dict[str, Converter]] = None,
    manual: bool = ModelMeta.datafile_manual,
    defaults: bool = ModelMeta.datafile_defaults,
    auto_load: bool = ModelMeta.datafile_auto_load,
    auto_save: bool = ModelMeta.datafile_auto_save,
):
    """Synchronize a data class to the specified path."""

    def decorator(cls):
        if dataclasses.is_dataclass(cls):
            dataclass = cls
        else:
            dataclass = dataclasses.dataclass(cls)

        return create_model(
            dataclass,
            attrs=attrs,
            pattern=pattern,
            manual=manual,
            defaults=defaults,
            auto_load=auto_load,
            auto_save=auto_save,
        )

    return decorator
