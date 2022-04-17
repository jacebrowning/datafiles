import dataclasses
from pathlib import Path
from typing import Callable, Dict, Optional, Union

from .config import Meta
from .converters import Converter
from .model import create_model


def datafile(
    pattern: Union[str, Callable, None] = None,
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
            dataclass = dataclasses.dataclass(cls)

        return create_model(
            dataclass,
            attrs=attrs,
            pattern=pattern,
            manual=manual,
            defaults=defaults,
            infer=infer,
        )

    return decorator


def auto(filename: str, **kwargs):
    kwargs["infer"] = True

    path = Path.cwd() / filename
    name = path.stem.strip(".").capitalize()

    def auto_repr(self):
        items = (f"{k}={v!r}" for k, v in self.__dict__.items() if k != "datafile")
        params = ", ".join(items)
        return f"{name}({params})"

    cls = type(name, (), {"__repr__": auto_repr})

    return datafile(str(path), **kwargs)(cls)()
