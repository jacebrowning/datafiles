import dataclasses
from inspect import isclass
from typing import Any, Dict, Optional, Union

import log

from ..utils import cached
from ._bases import Converter
from .builtins import Boolean, Float, Integer, String
from .containers import Dataclass, Dictionary, List
from .extensions import *  # pylint: disable=unused-wildcard-import


_REGISTRY: Dict[Union[type, str], type] = {}


def register(cls: type, converter: type):
    _REGISTRY[cls] = converter
    _REGISTRY[cls.__name__] = converter


register(Integer.TYPE, Integer)
register(Float.TYPE, Float)
register(Boolean.TYPE, Boolean)
register(String.TYPE, String)


@cached
def map_type(cls, *, name: str = '', item_cls: Optional[type] = None):
    """Infer the converter type from a dataclass, type, or annotation."""
    if name:
        log.debug(f'Mapping {name!r} of {cls!r} to converter')
    else:
        log.debug(f'Mapping {cls!r} to converter')

    if cls in _REGISTRY:
        converter: Any = _REGISTRY[cls]
        log.debug(f'Mapped {cls!r} to existing converter: {converter}')
        return converter

    if dataclasses.is_dataclass(cls):
        converters = {}
        for field in dataclasses.fields(cls):
            converters[field.name] = map_type(field.type, name=field.name)
        converter = Dataclass.subclass(cls, converters)
        log.debug(f'Mapped {cls!r} to new converter: {converter}')
        return converter

    if hasattr(cls, '__origin__'):
        converter = None

        if cls.__origin__ == list:
            try:
                converter = map_type(item_cls or cls.__args__[0])
            except TypeError as e:
                if '~T' in str(e):
                    e = TypeError(f"Type is required with 'List' annotation")
                raise e from None
            else:
                converter = List.subclass(converter)

        elif cls.__origin__ == dict:
            if item_cls:
                key = map_type(str)
                value = map_type(item_cls)
            else:
                log.warn("Schema enforcement not possible with 'Dict' annotation")
                key = map_type(cls.__args__[0])
                value = map_type(cls.__args__[1])

            converter = Dictionary.subclass(key, value)

        elif cls.__origin__ == Union:
            converter = map_type(cls.__args__[0])
            assert len(cls.__args__) == 2
            assert cls.__args__[1] == type(None)
            converter = converter.as_optional()

        if converter:
            log.debug(f'Mapped {cls!r} to new converter: {converter}')
            return converter

        raise TypeError(f'Unsupported container type: {cls.__origin__}')

    if not isclass(cls):
        raise TypeError(f'Annotation is not a type: {cls!r}')

    if issubclass(cls, Converter):
        log.debug(f'Mapped {cls!r} to existing converter (itself)')
        return cls

    raise TypeError(f'Could not map type: {cls}')
