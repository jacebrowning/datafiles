"""Configuration defaults for each model."""

from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Optional


if TYPE_CHECKING:
    from .converters import Converter


@dataclass
class Meta:
    datafile_attrs: Optional[Dict[str, Converter]] = None
    datafile_pattern: Optional[str] = None

    datafile_manual: bool = False
    datafile_defaults: bool = False
    datafile_auto_load: bool = True
    datafile_auto_save: bool = True
    datafile_auto_attr: bool = False


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
        meta.datafile_auto_load = obj.Meta.datafile_auto_load
    with suppress(AttributeError):
        meta.datafile_auto_save = obj.Meta.datafile_auto_save
    with suppress(AttributeError):
        meta.datafile_auto_attr = obj.Meta.datafile_auto_attr

    return meta
