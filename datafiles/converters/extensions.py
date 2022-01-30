# pylint: disable=unused-argument

from ruamel.yaml.scalarstring import LiteralScalarString

from .builtins import Float, String


class Number(Float):
    """Converter for integers or floats."""

    DEFAULT = 0

    @classmethod
    def to_preserialization_data(cls, python_value, *, default_to_skip=None):
        data = super().to_preserialization_data(python_value)
        if int(data) == data:
            return int(data)
        return data


class Text(String):
    """Converter for multiline strings."""

    DEFAULT = ""

    @classmethod
    def to_python_value(cls, deserialized_data, *, target_object=None):
        value = cls.to_preserialization_data(deserialized_data).strip()
        if "\n" in value:
            value = value + "\n"
        return value

    @classmethod
    def to_preserialization_data(cls, python_value, *, default_to_skip=None):
        data = super().to_preserialization_data(python_value).strip()
        if "\n" in data:
            return LiteralScalarString(data + "\n")
        return data
