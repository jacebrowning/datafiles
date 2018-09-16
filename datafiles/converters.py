import dataclasses
from abc import ABCMeta, abstractmethod
from collections import Iterable  # pylint: disable=no-name-in-module
from typing import Any, Union

import log

from .utils import cached


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
    def to_python_value(cls, deserialized_data):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def to_preserialization_data(cls, python_value):
        raise NotImplementedError


class Boolean(Converter):

    TYPE = bool
    DEFAULT = False
    _FALSY = {'false', 'f', 'no', 'n', 'disabled', 'off', '0'}

    @classmethod
    def to_python_value(cls, deserialized_data):
        if isinstance(deserialized_data, str):
            return deserialized_data.lower() not in cls._FALSY
        return cls.TYPE(deserialized_data)

    @classmethod
    def to_preserialization_data(cls, python_value):
        if python_value is None:
            return cls.DEFAULT
        return cls.TYPE(python_value)


class Float(Converter):

    TYPE = float
    DEFAULT = 0.0

    @classmethod
    def to_python_value(cls, deserialized_data):
        return cls.to_preserialization_data(deserialized_data)

    @classmethod
    def to_preserialization_data(cls, python_value):
        if python_value is None:
            return cls.DEFAULT
        return cls.TYPE(python_value)


class Integer(Converter):

    TYPE = int
    DEFAULT = 0

    @classmethod
    def to_python_value(cls, deserialized_data):
        return cls.to_preserialization_data(deserialized_data)

    @classmethod
    def to_preserialization_data(cls, python_value):
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


class String(Converter):

    TYPE = str
    DEFAULT = ''

    @classmethod
    def to_python_value(cls, deserialized_data):
        return cls.to_preserialization_data(deserialized_data)

    @classmethod
    def to_preserialization_data(cls, python_value):
        if python_value is None:
            return cls.DEFAULT
        return cls.TYPE(python_value)


class List:

    ELEMENT_CONVERTER = None

    @classmethod
    def of_converters(cls, converter: Converter):
        name = converter.__name__ + cls.__name__  # type: ignore
        return type(name, (cls,), {'ELEMENT_CONVERTER': converter})

    @classmethod
    def to_python_value(cls, deserialized_data):
        value = []
        convert = cls.ELEMENT_CONVERTER.to_python_value

        if deserialized_data is None:
            pass

        elif isinstance(deserialized_data, str):
            for item in deserialized_data.split(','):
                value.append(convert(item))
        else:
            try:
                items = iter(deserialized_data)
            except TypeError:
                value.append(convert(deserialized_data))
            else:
                for item in items:
                    value.append(convert(item))

        return value

    @classmethod
    def to_preserialization_data(cls, python_value):
        data = []
        convert = cls.ELEMENT_CONVERTER.to_preserialization_data

        if python_value is None:
            pass

        elif isinstance(python_value, Iterable):

            if isinstance(python_value, str):
                data.append(convert(python_value))

            elif isinstance(python_value, set):
                data.extend(sorted(convert(item) for item in python_value))

            else:
                for item in python_value:
                    data.append(convert(item))
        else:
            data.append(convert(python_value))

        return data


@cached
def map_type(cls, patch_dataclass=None):
    """Infer the converter type from the type annotation."""

    if dataclasses.is_dataclass(cls):
        assert patch_dataclass, "'patch_dataclass' required to map dataclass"
        return patch_dataclass(cls, None, None)

    if hasattr(cls, '__origin__'):
        log.debug(f'Mapping container type annotation: {cls}')
        converter = None

        if cls.__origin__ == list:
            try:
                converter = map_type(cls.__args__[0])
            except TypeError:
                exc = TypeError(f"Type is required with 'List' annotation")
                raise exc from None
            else:
                converter = List.of_converters(converter)

        elif cls.__origin__ == Union:
            converter = map_type(cls.__args__[0])
            assert len(cls.__args__) == 2
            assert cls.__args__[1] == type(None)
            converter = converter.as_optional()

        if converter:
            log.debug(f'Created new converter: {converter}')
            return converter

        raise TypeError(f'Unsupported container type: {cls.__origin__}')

    for converter in Converter.__subclasses__():
        if converter.TYPE == cls:
            return converter

    raise TypeError(f'Could not map type: {cls}')
