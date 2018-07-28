class Field:
    pass


class String(Field, str):
    pass


def map_type(builtin_class):
    """Infer the field type from the type annotation."""
    for field_class in Field.__subclasses__():
        if issubclass(field_class, builtin_class):
            return field_class