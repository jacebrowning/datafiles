import dataclasses
import inspect
import types
from enum import Enum
from inspect import isclass
from typing import Any, Dict, Mapping, Optional, Union

import log
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.scalarfloat import ScalarFloat
from ruamel.yaml.scalarstring import DoubleQuotedScalarString

from ..utils import cached, subclasses
from ._bases import Converter
from .builtins import Boolean, Float, Integer, String
from .containers import Dataclass, Dictionary, List, Set
from .enumerations import Enumeration
from .extensions import *  # pylint: disable=unused-wildcard-import

_REGISTRY: Dict[Union[type, str], type] = {}


def register(cls: Union[type, str], converter: type):
    """Associate the given type signature with a converter class."""
    _REGISTRY[cls] = converter
    if not isinstance(cls, str):
        _REGISTRY[cls.__name__] = converter


register(Integer.TYPE, Integer)
register(Float.TYPE, Float)
register(ScalarFloat, Float)
register(Boolean.TYPE, Boolean)
register(String.TYPE, String)
register(DoubleQuotedScalarString, String)
register(CommentedMap, Dictionary)
register(list, List)
register(dict, Dictionary)


def resolve(annotation, obj=None):
    if isinstance(annotation, str):
        log.debug(f"Attempting to eval {annotation!r} using {obj}")
        annotation = annotation.replace("List", "list").replace("Dict", "list")
        namespace = inspect.getmodule(obj).__dict__ if obj else None
        try:
            return eval(annotation, namespace)  # pylint: disable=eval-used
        except NameError as e:
            log.warn(f"Unable to eval: {e}")
    return annotation


@cached
def map_type(cls, *, name: str = "", item_cls: Optional[type] = None):
    """Infer the converter type from a dataclass, type, or annotation."""
    if name:
        log.debug(f"Mapping {name!r} of {cls!r} to converter")
    else:
        log.debug(f"Mapping {cls!r} to converter")

    if cls in _REGISTRY:
        converter: Any = _REGISTRY[cls]
        log.debug(f"Mapped {cls!r} to existing converter: {converter}")
        return converter

    if dataclasses.is_dataclass(cls):
        converters = {}
        for field in dataclasses.fields(cls):
            converters[field.name] = map_type(resolve(field.type), name=field.name)  # type: ignore
        converter = Dataclass.of_mappings(cls, converters)
        log.debug(f"Mapped {cls!r} to new converter: {converter}")
        return converter

    if hasattr(types, "UnionType") and isinstance(cls, types.UnionType):  # type: ignore
        # Python 3.10 behavior
        converter = map_type(cls.__args__[0])
        assert len(cls.__args__) == 2
        assert cls.__args__[1] == type(None)
        converter = converter.as_optional()
        return converter

    cls = resolve(cls)

    if hasattr(cls, "__origin__"):
        converter = None

        if cls.__origin__ == list:
            try:
                converter = map_type(item_cls or cls.__args__[0])
            except TypeError as e:  # Python 3.8 behavior
                assert "~T" in str(e), f"Unhandled error: {e}"
                raise TypeError("Type is required with 'List' annotation") from None
            except AttributeError as e:  # Python 3.9 behavior
                assert "__args__" in str(e), f"Unhandled error: {e}"
                raise TypeError("Type is required with 'List' annotation") from None
            else:
                converter = List.of_type(converter)

        elif cls.__origin__ == set:
            try:
                converter = map_type(item_cls or cls.__args__[0])
            except TypeError as e:  # Python 3.8 behavior
                assert "~T" in str(e), f"Unhandled error: {e}"
                raise TypeError("Type is required with 'Set' annotation") from None
            except AttributeError as e:  # Python 3.9 behavior
                assert "__args__" in str(e), f"Unhandled error: {e}"
                raise TypeError("Type is required with 'Set' annotation") from None
            else:
                converter = Set.of_type(converter)

        elif isclass(cls.__origin__) and issubclass(cls.__origin__, Mapping):
            if item_cls:
                key = map_type(str)
                value = map_type(item_cls)
            else:
                log.warn("Schema enforcement not possible with 'Dict' annotation")
                try:
                    key = map_type(cls.__args__[0])
                    value = map_type(cls.__args__[1])
                except TypeError as e:  # Python 3.8 behavior
                    assert "~" in str(e), f"Unhandled error: {e}"
                    raise TypeError(
                        "Types are required with 'Dict' annotation"
                    ) from None
                except AttributeError as e:  # Python 3.9 behavior
                    assert "__args__" in str(e), f"Unhandled error: {e}"
                    raise TypeError(
                        "Types are required with 'Dict' annotation"
                    ) from None

            converter = Dictionary.of_mapping(key, value)

        elif cls.__origin__ == Union:
            if str in cls.__args__:
                converter = map_type(str)
                if type(None) in cls.__args__:
                    converter = converter.as_optional()
            elif cls.__args__ in {(int, float), (float, int)}:
                converter = Number
            else:
                assert len(cls.__args__) == 2
                assert cls.__args__[1] == type(None)
                converter = map_type(cls.__args__[0]).as_optional()

        elif issubclass(cls.__origin__, Converter):
            subtypes = [map_type(t) for t in cls.__args__]
            converter = cls.__origin__.as_generic(subtypes)

        if converter:
            log.debug(f"Mapped {cls!r} to new converter: {converter}")
            return converter

        raise TypeError(f"Unsupported container type: {cls.__origin__}")

    if isinstance(cls, str):
        log.debug(f"Searching for class matching {cls!r} annotation")
        for cls2 in subclasses(Converter):
            if cls2.__name__ == cls:
                register(cls, cls2)
                log.debug(f"Registered {cls2} as new converter")
                return cls2

    if not isclass(cls):
        raise TypeError(f"Annotation is not a type: {cls!r}")

    if issubclass(cls, Converter):
        log.debug(f"Mapped {cls!r} to existing converter (itself)")
        return cls

    if issubclass(cls, Enum):
        return Enumeration.of_type(cls)

    if issubclass(cls, dict):
        log.warn("Schema enforcement not possible with 'TypedDict' annotation")
        key = map_type(str)
        value = Any
        return Dictionary.of_mapping(key, value)

    raise TypeError(f"Could not map type: {cls}")
