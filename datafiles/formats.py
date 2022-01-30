# pylint: disable=import-outside-toplevel

import json
from abc import ABCMeta, abstractmethod
from contextlib import suppress
from io import StringIO
from pathlib import Path
from typing import IO, Dict, List, Union

import log

from . import types, utils

_REGISTRY: Dict[str, type] = {}


def register(extension: str, formatter: type):
    """Associate the given file extension with a formatter class."""
    _REGISTRY[extension] = formatter


class Formatter(metaclass=ABCMeta):
    """Base class for object serialization and text deserialization."""

    @classmethod
    @abstractmethod
    def extensions(cls) -> List[str]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def deserialize(cls, file_object: IO) -> Dict:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def serialize(cls, data: Dict) -> str:
        raise NotImplementedError


class JSON(Formatter):
    """Formatter for JavaScript Object Notation."""

    @classmethod
    def extensions(cls):
        return {".json"}

    @classmethod
    def deserialize(cls, file_object):
        return json.load(file_object)

    @classmethod
    def serialize(cls, data):
        return json.dumps(data, indent=2)


class TOML(Formatter):
    """Formatter for (round-trip) Tom's Obvious Minimal Language."""

    @classmethod
    def extensions(cls):
        return {".toml"}

    @classmethod
    def deserialize(cls, file_object):
        import tomlkit

        return utils.dictify(tomlkit.loads(file_object.read()))

    @classmethod
    def serialize(cls, data):
        import tomlkit

        return tomlkit.dumps(data)


class YAML(Formatter):
    """Formatter for (round-trip) YAML Ain't Markup Language."""

    @classmethod
    def extensions(cls):
        return {"", ".yml", ".yaml"}

    @classmethod
    def deserialize(cls, file_object):
        from ruamel.yaml import YAML as _YAML

        yaml = _YAML()
        yaml.preserve_quotes = True  # type: ignore
        try:
            return yaml.load(file_object)
        except NotImplementedError as e:
            log.error(str(e))
            return {}

    @classmethod
    def serialize(cls, data):
        from ruamel.yaml import YAML as _YAML

        yaml = _YAML()
        yaml.register_class(types.List)
        yaml.register_class(types.Dict)
        yaml.indent(mapping=2, sequence=4, offset=2)

        stream = StringIO()
        yaml.dump(data, stream)
        text = stream.getvalue()

        if text.startswith("  "):
            return text[2:].replace("\n  ", "\n")

        if text == "{}\n":
            return ""

        return text.replace("- \n", "-\n")


def deserialize(path: Path, extension: str, *, formatter=None) -> Dict:
    if formatter is None:
        formatter = _get_formatter(extension)
    with path.open("r") as file_object:
        data = formatter.deserialize(file_object)
        if data is None:
            log.debug(f"No data in {path}")
            data = {}
        elif not isinstance(data, dict):
            log.error(f"Invalid data in {path}: {data!r}")
            data = {}
        return data


def serialize(
    data: Union[Dict, List], extension: str = ".yml", *, formatter=None
) -> str:
    if formatter is None:
        formatter = _get_formatter(extension)
    return formatter.serialize(data)


def _get_formatter(extension: str):
    with suppress(KeyError):
        return _REGISTRY[extension]

    for formatter in Formatter.__subclasses__():
        if extension in formatter.extensions():
            return formatter

    raise ValueError(f"Unsupported file extension: {extension!r}")
