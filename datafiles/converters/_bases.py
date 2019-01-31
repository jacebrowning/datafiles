# pylint: disable=unused-argument

from typing import Any

from ..utils import Missing


class Converter:
    """Base class for immutable attribute conversion."""

    TYPE: type = object
    DEFAULT: Any = None

    @classmethod
    def as_optional(cls):
        name = 'Optional' + cls.__name__
        bases = (cls,)
        attributes = {'DEFAULT': None}
        return type(name, bases, attributes)

    @classmethod
    def to_python_value(cls, deserialized_data, *, target_object=None):
        return cls.to_preserialization_data(deserialized_data)

    @classmethod
    def to_preserialization_data(cls, python_value, *, default_to_skip=Missing):
        if python_value is None:
            return cls.DEFAULT
        assert cls.TYPE is not object, f"'TYPE' must be set on {cls}"
        return cls.TYPE(python_value)
