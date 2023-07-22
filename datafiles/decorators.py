import dataclasses
from pathlib import Path
from typing import Callable, Dict, Optional, Union

import log

from .config import Meta
from .converters import Converter
from .model import Model, create_model


def datafile(
    pattern: Union[str, Callable, None] = None,
    *,
    attrs: Optional[Dict[str, Converter]] = None,
    manual: bool = Meta.datafile_manual,
    defaults: bool = Meta.datafile_defaults,
    infer: bool = Meta.datafile_infer,
    **kwargs,
):
    """Synchronize a data class to the specified path."""

    if pattern is None:
        return dataclasses.dataclass(**kwargs)

    if callable(pattern):
        return dataclasses.dataclass(pattern)  # type: ignore

    def decorator(cls=None):
        if dataclasses.is_dataclass(cls):
            dataclass = cls
        else:
            dataclass = dataclasses.dataclass(cls, **kwargs)

        return create_model(
            dataclass,
            attrs=attrs,
            pattern=pattern,
            manual=manual,
            defaults=defaults,
            infer=infer,
        )

    return decorator


def sync(
    instance: object,
    pattern: str,
    *,
    attrs: Optional[Dict[str, Converter]] = None,
    manual: bool = Meta.datafile_manual,
    defaults: bool = Meta.datafile_defaults,
    infer: bool = Meta.datafile_infer,
):
    """Synchronize an object to the specified path."""
    cls = instance.__class__
    if hasattr(instance, "datafile"):
        pattern = cls.Meta.datafile_pattern  # type: ignore[attr-defined]
        log.error(f"{cls} was already synchronized to {pattern!r}")
        delattr(cls, "Meta")
        delattr(instance, "datafile")
    instance.__class__ = create_model(
        cls, attrs=attrs, pattern=pattern, manual=manual, defaults=defaults, infer=infer
    )
    Model.__post_init__(instance)  # type: ignore[arg-type]


def auto(filename: str, **kwargs):
    """Map an arbitrary file to a synchronized Python object."""
    kwargs["infer"] = True

    path = Path.cwd() / filename
    name = path.stem.strip(".").capitalize()

    def auto_repr(self):
        items = (f"{k}={v!r}" for k, v in self.__dict__.items() if k != "datafile")
        params = ", ".join(items)
        return f"{name}({params})"

    cls = type(name, (), {"__repr__": auto_repr})

    return datafile(str(path), **kwargs)(cls)()
