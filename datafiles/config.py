"""Configuration defaults for each model."""

from contextlib import suppress
from dataclasses import dataclass
from typing import Dict, Optional

from .converters import Converter


@dataclass
class Meta:
    datafile_attrs: Optional[Dict[str, Converter]] = None
    datafile_pattern: Optional[str] = None
    datafile_manual: bool = False
    datafile_defaults: bool = False
    datafile_infer: bool = False


def load(obj) -> Meta:
    meta = Meta()

    with suppress(AttributeError):
        meta.datafile_attrs = obj.Meta.datafile_attrs
    with suppress(AttributeError):
        meta.datafile_pattern = obj.Meta.datafile_pattern
    with suppress(AttributeError):
        meta.datafile_manual = obj.Meta.datafile_manual
    with suppress(AttributeError):
        meta.datafile_defaults = obj.Meta.datafile_defaults
    with suppress(AttributeError):
        meta.datafile_infer = obj.Meta.datafile_infer

    return meta
