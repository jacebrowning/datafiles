from collections.abc import Iterable
from typing import Dict

import log

from ..utils import Missing
from ._bases import Converter


class List(Converter):
    """Base converter for homogeneous lists of another converter."""

    CONVERTER = None

    @classmethod
    def subclass(cls, converter: type):
        name = f'{converter.__name__}List'  # type: ignore
        bases = (cls,)
        attributes = {'CONVERTER': converter}
        return type(name, bases, attributes)

    @classmethod
    def to_python_value(cls, deserialized_data, *, target_object):
        if target_object is None:
            value = []  # type: ignore
        else:
            value = target_object
            value.clear()

        convert = cls.CONVERTER.to_python_value

        if deserialized_data is None:
            pass

        elif isinstance(deserialized_data, Iterable) and all(
            (item is None for item in deserialized_data)
        ):
            pass

        elif isinstance(deserialized_data, str):
            for item in deserialized_data.split(','):
                value.append(convert(item))
        else:
            try:
                items = iter(deserialized_data)
            except TypeError:
                value.append(convert(deserialized_data, target_object=None))
            else:
                for item in items:
                    value.append(convert(item, target_object=None))

        return value

    @classmethod
    def to_preserialization_data(cls, python_value, *, default_to_skip=Missing):
        data = []

        convert = cls.CONVERTER.to_preserialization_data

        if python_value is None:
            pass

        elif isinstance(python_value, Iterable):

            if isinstance(python_value, str):
                data.append(convert(python_value, default_to_skip=Missing))

            elif isinstance(python_value, set):
                data.extend(
                    sorted(
                        convert(item, default_to_skip=Missing) for item in python_value
                    )
                )

            else:
                for item in python_value:
                    data.append(convert(item, default_to_skip=Missing))
        else:
            data.append(convert(python_value, default_to_skip=Missing))

        if data == default_to_skip:
            data.clear()

        return data or [None]


class Dictionary(Converter):
    """Base converter for raw dictionaries."""

    @classmethod
    def subclass(cls, key: type, value: type):
        name = f'{key.__name__}{value.__name__}Dict'
        bases = (cls,)
        return type(name, bases, {})

    @classmethod
    def to_python_value(cls, deserialized_data, *, target_object):
        if isinstance(deserialized_data, dict):
            data = deserialized_data.copy()
        else:
            data = {}

        if target_object is None:
            value = data
        else:
            value = target_object
            value.clear()
            value.update(data)

        return value

    @classmethod
    def to_preserialization_data(cls, python_value, *, default_to_skip=Missing):
        data = dict(python_value)

        if data == default_to_skip:
            data.clear()

        return data


class Object(Converter):
    """Base converter for dataclasses."""

    DATACLASS = None
    CONVERTERS = None

    @classmethod
    def subclass(cls, dataclass, converters: Dict[str, type]):
        name = f'{dataclass.__name__}Converter'
        bases = (cls,)
        attributes = {'DATACLASS': dataclass, 'CONVERTERS': converters}
        return type(name, bases, attributes)

    @classmethod
    def to_python_value(cls, deserialized_data, *, target_object):
        if isinstance(deserialized_data, dict):
            data = deserialized_data.copy()
        else:
            data = {}

        for name, converter in cls.CONVERTERS.items():
            if name not in data:
                data[name] = converter.to_python_value(None)

        new_value = cls.DATACLASS(**data)  # pylint: disable=not-callable

        if target_object is None:
            value = new_value
        else:
            value = target_object
            value.__dict__ = new_value.__dict__

        return value

    @classmethod
    def to_preserialization_data(cls, python_value, *, default_to_skip=Missing):
        data = {}

        for name, converter in cls.CONVERTERS.items():

            if isinstance(python_value, dict):
                try:
                    value = python_value[name]
                except KeyError as e:
                    log.debug(e)
                    value = None
            else:
                try:
                    value = getattr(python_value, name)
                except AttributeError as e:
                    log.debug(e)
                    value = None

            if default_to_skip is not Missing:
                if value == getattr(default_to_skip, name):
                    log.debug(f"Skipped default value for '{name}' attribute")
                    continue

            data[name] = converter.to_preserialization_data(value)

        return data
