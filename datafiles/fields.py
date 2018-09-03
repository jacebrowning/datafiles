import dataclasses

import log


class Field:
    @classmethod
    def to_python_value(cls, deserialized_data):
        return cls.to_preserialization_data(deserialized_data)

    @classmethod
    def to_preserialization_data(cls, python_value):
        raise NotImplementedError


class Boolean(Field):

    FALSY = {'false', 'f', 'no', 'n', 'disabled', 'off', '0'}

    @classmethod
    def to_python_value(cls, deserialized_data):
        if isinstance(deserialized_data, str):
            return deserialized_data.lower() not in cls.FALSY
        return bool(deserialized_data)

    @classmethod
    def to_preserialization_data(cls, python_value):
        return bool(python_value)


class Float(Field, float):
    @classmethod
    def to_preserialization_data(cls, python_value):
        if python_value is None:
            return 0.0
        return float(python_value)


class Integer(Field, int):
    @classmethod
    def to_preserialization_data(cls, python_value):
        if python_value is None:
            return 0
        try:
            return int(python_value)
        except ValueError as exc:
            try:
                data = int(float(python_value))
            except ValueError:
                raise exc from None
            else:
                msg = f'Precision lost in conversion to int: {python_value}'
                log.warn(msg)
                return data


class String(Field, str):
    @classmethod
    def to_preserialization_data(cls, python_value):
        if python_value is None:
            return ''
        return str(python_value)


class List(Field, list):

    __field__ = None

    @classmethod
    def of_field_type(cls, field: Field):
        name = field.__name__ + cls.__name__  # type: ignore
        new_class = type(name, (cls,), {'__field__': field})
        return new_class

    @classmethod
    def to_python_value(cls, deserialized_data):
        value = []
        convert = cls.__field__.to_python_value

        if deserialized_data is None:
            pass

        elif isinstance(deserialized_data, str):
            for item in deserialized_data.split(','):
                value.append(convert(item))

        elif isinstance(deserialized_data, list):
            for item in deserialized_data:
                value.append(convert(item))

        else:
            value.append(convert(deserialized_data))

        return value

    @classmethod
    def to_preserialization_data(cls, python_value):
        data = []
        convert = cls.__field__.to_preserialization_data

        if python_value is None:
            pass
        elif isinstance(python_value, list):
            for item in python_value:
                data.append(convert(item))
        else:
            data.append(convert(python_value))

        return data


def map_type(cls, patch_dataclass=None):
    """Infer the field type from the type annotation."""

    if dataclasses.is_dataclass(cls):
        assert patch_dataclass, "'patch_dataclass' required to map dataclass"
        return patch_dataclass(cls, None, None)

    if hasattr(cls, '__origin__'):
        log.debug(f'Mapping container type annotation: {cls}')
        if cls.__origin__ == list:
            try:
                field_class = map_type(cls.__args__[0])
            except TypeError:
                exc = TypeError(f"Type is required with 'List' annotation")
                raise exc from None
            else:
                return List.of_field_type(field_class)
        raise TypeError(f'Unsupported container type: {cls.__origin__}')

    for field_class in Field.__subclasses__():
        if issubclass(field_class, cls):
            return field_class

    if cls == bool:
        return Boolean

    raise TypeError(f'Could not map type: {cls}')
