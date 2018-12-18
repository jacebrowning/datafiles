import dataclasses
from abc import ABCMeta, abstractmethod
from collections.abc import Iterable
from typing import Any, Dict, Union

import log
from ruamel.yaml.scalarstring import LiteralScalarString

from .utils import Missing, cached


class Converter(metaclass=ABCMeta):
    """Base class for attribute conversion."""

    TYPE: Any = None
    DEFAULT: Any = None

    @classmethod
    def as_optional(cls):
        name = 'Optional' + cls.__name__
        return type(name, (cls,), {'DEFAULT': None})

    @classmethod
    @abstractmethod
    def to_python_value(cls, deserialized_data, *, target):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def to_preserialization_data(cls, python_value, *, skip=Missing):
        raise NotImplementedError


class Boolean(Converter):
    """Converter for `bool` literals."""

    TYPE = bool
    DEFAULT = False
    _FALSY = {'false', 'f', 'no', 'n', 'disabled', 'off', '0'}

    # pylint: disable=unused-argument

    @classmethod
    def to_python_value(cls, deserialized_data, *, target=None):
        if isinstance(deserialized_data, str):
            value = deserialized_data.lower() not in cls._FALSY
        else:
            value = cls.TYPE(deserialized_data)
        return value

    @classmethod
    def to_preserialization_data(cls, python_value, *, skip=Missing):
        if python_value is None:
            return cls.DEFAULT
        return cls.TYPE(python_value)


class Float(Converter):
    """Converter for `float` literals."""

    TYPE = float
    DEFAULT = 0.0

    # pylint: disable=unused-argument

    @classmethod
    def to_python_value(cls, deserialized_data, *, target=None):
        value = cls.to_preserialization_data(deserialized_data)
        return value

    @classmethod
    def to_preserialization_data(cls, python_value, *, skip=Missing):
        if python_value is None:
            return cls.DEFAULT
        return cls.TYPE(python_value)


class Integer(Converter):
    """Converter for `int` literals."""

    TYPE = int
    DEFAULT = 0

    # pylint: disable=unused-argument

    @classmethod
    def to_python_value(cls, deserialized_data, *, target=None):
        value = cls.to_preserialization_data(deserialized_data)
        return value

    @classmethod
    def to_preserialization_data(cls, python_value, *, skip=Missing):
        if python_value is None:
            return cls.DEFAULT
        try:
            return cls.TYPE(python_value)
        except ValueError as exc:
            try:
                data = cls.TYPE(float(python_value))
            except ValueError:
                raise exc from None
            else:
                msg = f'Precision lost in conversion to int: {python_value}'
                log.warn(msg)
                return data


class Number(Float):
    """Converter for integers or floats."""

    DEFAULT = 0

    # pylint: disable=unused-argument

    @classmethod
    def to_preserialization_data(cls, python_value, *, skip=Missing):
        data = super().to_preserialization_data(python_value)
        if int(data) == data:
            return int(data)
        return data


class String(Converter):
    """Converter for `str` literals."""

    TYPE = str
    DEFAULT = ""

    # pylint: disable=unused-argument

    @classmethod
    def to_python_value(cls, deserialized_data, *, target=None):
        value = cls.to_preserialization_data(deserialized_data)
        return value

    @classmethod
    def to_preserialization_data(cls, python_value, *, skip=Missing):
        if python_value is None:
            return cls.DEFAULT
        return cls.TYPE(python_value)


class Text(String):
    """Converter for multiline strings."""

    DEFAULT = ""

    # pylint: disable=unused-argument

    @classmethod
    def to_python_value(cls, deserialized_data, *, target=None):
        value = cls.to_preserialization_data(deserialized_data).strip()
        if '\n' in value:
            value = value + '\n'
        return value

    @classmethod
    def to_preserialization_data(cls, python_value, *, skip=Missing):
        data = super().to_preserialization_data(python_value).strip()
        if '\n' in data:
            return LiteralScalarString(data + '\n')
        return data


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
    def to_python_value(cls, deserialized_data, *, target):
        if target is None:
            value = []  # type: ignore
        else:
            value = target
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
                value.append(convert(deserialized_data, target=None))
            else:
                for item in items:
                    value.append(convert(item, target=None))

        return value

    @classmethod
    def to_preserialization_data(cls, python_value, *, skip=Missing):
        data = []

        convert = cls.CONVERTER.to_preserialization_data

        if python_value is None:
            pass

        elif isinstance(python_value, Iterable):

            if isinstance(python_value, str):
                data.append(convert(python_value, skip=Missing))

            elif isinstance(python_value, set):
                data.extend(
                    sorted(convert(item, skip=Missing) for item in python_value)
                )

            else:
                for item in python_value:
                    data.append(convert(item, skip=Missing))
        else:
            data.append(convert(python_value, skip=Missing))

        if data == skip:
            data.clear()

        return data


class Dictionary(Converter):
    """Base converter for raw dictionaries."""

    @classmethod
    def subclass(cls, key: type, value: type):
        name = f'{key.__name__}{value.__name__}Dict'
        bases = (cls,)
        return type(name, bases, {})

    @classmethod
    def to_python_value(cls, deserialized_data, *, target):
        if isinstance(deserialized_data, dict):
            data = deserialized_data.copy()
        else:
            data = {}

        if target is None:
            value = data
        else:
            value = target
            value.clear()
            value.update(data)

        return value

    @classmethod
    def to_preserialization_data(cls, python_value, *, skip=Missing):
        data = dict(python_value)

        if data == skip:
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
    def to_python_value(cls, deserialized_data, *, target):
        if isinstance(deserialized_data, dict):
            data = deserialized_data.copy()
        else:
            data = {}

        for name, converter in cls.CONVERTERS.items():
            if name not in data:
                data[name] = converter.to_python_value(None)

        new_value = cls.DATACLASS(**data)  # pylint: disable=not-callable

        if target is None:
            value = new_value
        else:
            value = target
            value.__dict__ = new_value.__dict__

        return value

    @classmethod
    def to_preserialization_data(cls, python_value, *, skip=Missing):
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

            if skip is not Missing:
                if value == getattr(skip, name):
                    log.debug(f"Skipped default value for '{name}' attribute")
                    continue

            data[name] = converter.to_preserialization_data(value)

        return data


@cached
def map_type(cls):
    """Infer the converter type from a dataclass, type, or annotation."""
    log.debug(f'Mapping {cls} to converter')

    if dataclasses.is_dataclass(cls):
        converters = {}
        for field in dataclasses.fields(cls):
            converters[field.name] = map_type(field.type)
        converter = Object.subclass(cls, converters)
        log.debug(f'Mapped {cls} to new converter: {converter}')
        return converter

    if hasattr(cls, '__origin__'):
        converter = None

        if cls.__origin__ == list:
            try:
                converter = map_type(cls.__args__[0])
            except TypeError as exc:
                log.debug(exc)
                exc = TypeError(f"Type is required with 'List' annotation")
                raise exc from None
            else:
                converter = List.subclass(converter)

        if cls.__origin__ == dict:
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
            log.debug(f'Mapped {cls} to new converter: {converter}')
            return converter

        raise TypeError(f'Unsupported container type: {cls.__origin__}')

    else:
        for converter in Converter.__subclasses__():
            if converter.TYPE == cls:
                log.debug(f'Mapped {cls} to existing converter: {converter}')
                return converter

    if issubclass(cls, Converter):
        log.debug(f'Mapped {cls} to existing converter (itself)')
        return cls

    raise TypeError(f'Could not map type: {cls}')
