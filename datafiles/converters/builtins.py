# pylint: disable=unused-argument

import log

from ._bases import Converter


class Boolean(Converter):
    """Converter for `bool` literals."""

    TYPE = bool
    DEFAULT = False
    _FALSY = {'false', 'f', 'no', 'n', 'disabled', 'off', '0'}

    @classmethod
    def to_python_value(cls, deserialized_data, *, target_object=None):
        if isinstance(deserialized_data, str):
            value = deserialized_data.lower() not in cls._FALSY
        else:
            value = cls.TYPE(deserialized_data)
        return value


class Float(Converter):
    """Converter for `float` literals."""

    TYPE = float
    DEFAULT = 0.0


class Integer(Converter):
    """Converter for `int` literals."""

    TYPE = int
    DEFAULT = 0

    @classmethod
    def to_preserialization_data(cls, python_value, *, default_to_skip=None):
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
                log.warn(f'Precision lost in conversion to int: {python_value}')
                return data


class String(Converter):
    """Converter for `str` literals."""

    TYPE = str
    DEFAULT = ""
