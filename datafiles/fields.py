class Field:
    @classmethod
    def to_python(cls, value):
        return cls.to_data(value)

    @classmethod
    def to_data(cls, value):
        raise NotImplementedError


class Boolean(Field):
    @classmethod
    def to_data(cls, value):
        return bool(value)


class Integer(Field, int):
    @classmethod
    def to_data(cls, value):
        if value is None:
            return 0
        return value


class Float(Field, float):
    @classmethod
    def to_data(cls, value):
        if value is None:
            return 0.0
        return float(value)


class String(Field, str):
    @classmethod
    def to_data(cls, value):
        if value is None:
            return ''
        return str(value)


def map_type(builtin_class):
    """Infer the field type from the type annotation."""

    for field_class in Field.__subclasses__():
        if issubclass(field_class, builtin_class):
            return field_class

    if builtin_class == bool:
        return Boolean

    raise ValueError(f'Could not map type: {builtin_class}')
