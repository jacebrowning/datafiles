import dataclasses
from collections.abc import Iterable
from contextlib import suppress
from typing import Callable, Dict

import log

from .. import settings
from ..utils import Missing, get_default_field_value
from ._bases import Converter


class List(Converter):
    """Base converter for homogeneous lists of another converter."""

    CONVERTER: Converter = NotImplemented

    @classmethod
    def of_type(cls, converter: type):
        name = f"{converter.__name__}{cls.__name__}"
        bases = (cls,)
        attributes = {"CONVERTER": converter}
        return type(name, bases, attributes)

    @classmethod
    def to_python_value(cls, deserialized_data, *, target_object=None):
        if target_object is None or target_object is Missing:
            value = []
        else:
            value = target_object
            value.clear()

        convert = cls.CONVERTER.to_python_value

        if deserialized_data is None:
            pass

        elif isinstance(deserialized_data, Iterable) and all(
            (item is None for item in deserialized_data)
        ):
            pass

        elif isinstance(deserialized_data, str):
            for item in deserialized_data.split(","):
                value.append(convert(item))
        else:
            try:
                items = iter(deserialized_data)
            except TypeError:
                value.append(convert(deserialized_data, target_object=None))
            else:
                for item in items:
                    value.append(convert(item, target_object=None))

        return value

    @classmethod
    def to_preserialization_data(cls, python_value, *, default_to_skip=None):
        data = []

        convert = cls.CONVERTER.to_preserialization_data

        if python_value is None:
            pass

        elif isinstance(python_value, Iterable):

            if isinstance(python_value, str):
                data.append(convert(python_value, default_to_skip=None))

            elif isinstance(python_value, set):
                data.extend(
                    sorted(convert(item, default_to_skip=None) for item in python_value)
                )

            else:
                for item in python_value:
                    data.append(convert(item, default_to_skip=None))
        else:
            data.append(convert(python_value, default_to_skip=None))

        if data == default_to_skip:
            data.clear()

        if settings.MINIMAL_DIFFS:
            return data or [None]

        return data


class Set(List):
    """Base converter for sets."""

    @classmethod
    def to_python_value(cls, deserialized_data, *, target_object=None):
        if target_object is None or target_object is Missing:
            value = set()
        else:
            value = target_object
            value.clear()

        convert = cls.CONVERTER.to_python_value

        if deserialized_data is None:
            pass

        elif isinstance(deserialized_data, Iterable) and all(
            (item is None for item in deserialized_data)
        ):
            pass

        elif isinstance(deserialized_data, str):
            for item in deserialized_data.split(","):
                value.add(convert(item))
        else:
            try:
                items = iter(deserialized_data)
            except TypeError:
                value.add(convert(deserialized_data, target_object=None))
            else:
                for item in items:
                    value.add(convert(item, target_object=None))

        return value


class Dictionary(Converter):
    """Base converter for raw dictionaries."""

    @classmethod
    def of_mapping(cls, key: type, value: type):
        try:
            name = f"{key.__name__}{value.__name__}Dict"
        except AttributeError:  # Python < 3.10
            name = "UntypedDict"
        bases = (cls,)
        return type(name, bases, {})

    @classmethod
    def to_python_value(cls, deserialized_data, *, target_object=None):
        if isinstance(deserialized_data, dict):
            data = deserialized_data.copy()
        else:
            data = {}

        if target_object is None or target_object is Missing:
            value = data
        else:
            value = target_object
            value.clear()
            value.update(data)

        return value

    @classmethod
    def to_preserialization_data(cls, python_value, *, default_to_skip=None):
        data = dict(python_value) if python_value else {}

        if data == default_to_skip:
            data.clear()

        return data


class Dataclass(Converter):
    """Base converter for dataclasses."""

    DATACLASS: Callable = NotImplemented
    CONVERTERS: Dict = NotImplemented

    @classmethod
    def of_mappings(cls, dataclass, converters: Dict[str, type]):
        name = f"{dataclass.__name__}Converter"
        bases = (cls,)
        attributes = {"DATACLASS": dataclass, "CONVERTERS": converters}
        return type(name, bases, attributes)

    @classmethod
    def to_python_value(cls, deserialized_data, *, target_object=None):
        if dataclasses.is_dataclass(deserialized_data):
            data = dataclasses.asdict(deserialized_data)
        elif isinstance(deserialized_data, dict):
            data = deserialized_data.copy()
        else:
            data = {}

        if deserialized_data is None and cls.DEFAULT is None:
            return None

        for name, value in list(data.items()):
            if name not in cls.CONVERTERS:
                log.debug(f"Removed unmapped nested file attribute: {name}")
                data.pop(name)

        for name, converter in cls.CONVERTERS.items():
            log.debug(f"Converting '{name}' data with {converter}")
            if name in data:
                converted = converter.to_python_value(data[name], target_object=None)
            else:
                if target_object is None or target_object is Missing:
                    converted = converter.to_python_value(None, target_object=None)
                else:
                    converted = get_default_field_value(target_object, name)
                    if converted is Missing:
                        converted = getattr(target_object, name)

            data[name] = converted

        new_value = cls.DATACLASS(**data)  # pylint: disable=not-callable

        if target_object is None or target_object is Missing:
            value = new_value
        else:
            value = target_object
            value.__dict__ = new_value.__dict__

        return value

    @classmethod
    def to_preserialization_data(cls, python_value, *, default_to_skip=None):
        data = {}

        if python_value is None and cls.DEFAULT is None:
            return None

        for name, converter in cls.CONVERTERS.items():

            if isinstance(python_value, dict):
                try:
                    value = python_value[name]
                except KeyError:
                    log.debug(f"Added missing nested attribute: {name}")
                    value = None
            else:
                try:
                    value = getattr(python_value, name)
                except AttributeError:
                    log.debug(f"Added missing nested attribute: {name}")
                    value = None

            with suppress(AttributeError):
                if value == getattr(default_to_skip, name):
                    log.debug(
                        f"Skipped default value of {value!r} for {name!r} attribute"
                    )
                    continue

            data[name] = converter.to_preserialization_data(value)

        return data
