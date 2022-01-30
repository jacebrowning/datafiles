# pylint: disable=unused-argument,not-callable

from ._bases import Converter


class Enumeration(Converter):

    ENUM: type = NotImplemented

    @classmethod
    def of_type(cls, enum: type):
        name = f"{enum.__name__}Converter"
        bases = (cls,)
        attributes = {"ENUM": enum}
        return type(name, bases, attributes)

    @classmethod
    def to_python_value(cls, deserialized_data, *, target_object=None):
        return cls.ENUM(deserialized_data)

    @classmethod
    def to_preserialization_data(cls, python_value, *, default_to_skip=None):
        return python_value.value
