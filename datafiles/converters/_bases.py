from typing import Any


class Optional:
    """Class to mixin for Optional[] types."""

    @classmethod
    def to_python_value(cls, deserialized_data, **kwargs):
        if deserialized_data is None:
            return None

        return super().to_python_value(deserialized_data, **kwargs)  # type: ignore

    @classmethod
    def to_preserialization_data(cls, python_value, **kwargs):
        if python_value is None:
            return None

        return super().to_preserialization_data(python_value, **kwargs)  # type: ignore


class Converter:  # pylint: disable=unused-argument
    """Base class for immutable attribute conversion."""

    TYPE: type = object
    DEFAULT: Any = NotImplemented

    @classmethod
    def as_generic(cls, subtypes):
        name = "Generic"
        for t in subtypes:
            name += t.__name__
        name += cls.__name__
        bases = (cls,)
        attributes = {'CONVERTERS': subtypes}
        return type(name, bases, attributes)

    @classmethod
    def as_optional(cls):
        name = 'Optional' + cls.__name__
        bases = (Optional, cls)
        attributes = {'DEFAULT': None}
        return type(name, bases, attributes)

    @classmethod
    def to_python_value(cls, deserialized_data, *, target_object=None):
        return cls.to_preserialization_data(deserialized_data)

    @classmethod
    def to_preserialization_data(cls, python_value, *, default_to_skip=None):
        if python_value is None:
            return cls.DEFAULT

        if cls.TYPE is object:
            return python_value

        return cls.TYPE(python_value)
