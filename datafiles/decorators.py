from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional

from .config import Meta
from .model import create_model


if TYPE_CHECKING:
    from .converters import Converter


def datafile(
    pattern: str,
    attrs: Optional[Dict[str, Converter]] = None,
    manual: bool = Meta.datafile_manual,
    defaults: bool = Meta.datafile_defaults,
    auto_load: bool = Meta.datafile_auto_load,
    auto_save: bool = Meta.datafile_auto_save,
    auto_attr: bool = Meta.datafile_auto_attr,
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
            auto_attr=auto_attr,
        )

    return decorator


def auto(filename: str, **kwargs):
    kwargs['auto_attr'] = True

    path = Path.cwd() / filename

    cls = type(path.stem.strip('.'), (), {})

    return datafile(str(path), **kwargs)(cls)()
