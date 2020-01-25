import json
from abc import ABCMeta, abstractmethod
from contextlib import suppress
from io import StringIO
from pathlib import Path
from typing import IO, Any, Dict, List

import log
import tomlkit
from ruamel import yaml

from . import settings


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
    def deserialize(cls, file_object: IO[Any]) -> Dict:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def serialize(cls, data: Dict) -> str:
        raise NotImplementedError


class JSON(Formatter):
    """Formatter for JavaScript Object Notation."""

    @classmethod
    def extensions(cls):
        return {'.json'}

    @classmethod
    def deserialize(cls, file_object):
        return json.load(file_object) or {}

    @classmethod
    def serialize(cls, data):
        return json.dumps(data, indent=2)


class TOML(Formatter):
    """Formatter for (round-trip) Tom's Obvious Minimal Language."""

    @classmethod
    def extensions(cls):
        return {'.toml'}

    @classmethod
    def deserialize(cls, file_object):
        return tomlkit.loads(file_object.read()) or {}

    @classmethod
    def serialize(cls, data):
        return tomlkit.dumps(data)


class YAML(Formatter):
    """Formatter for (safe, round-trip) YAML Ain't Markup Language."""

    @classmethod
    def extensions(cls):
        return {'.yml', '.yaml'}

    @classmethod
    def deserialize(cls, file_object):
        try:
            return yaml.YAML(typ='rt').load(file_object) or {}
        except NotImplementedError as e:
            log.error(str(e))
            return {}

    @classmethod
    def serialize(cls, data):
        if settings.INDENT_YAML_BLOCKS:
            f = StringIO()
            y = yaml.YAML()
            y.indent(mapping=2, sequence=4, offset=2)
            y.dump(data, f)
            text = f.getvalue().strip() + '\n'
        else:
            text = yaml.round_trip_dump(data) or ""
            text = text.replace('- \n', '-\n')
        return "" if text == "{}\n" else text


def deserialize(path: Path, extension: str) -> Dict:
    formatter = _get_formatter(extension)
    with path.open('r') as file_object:
        return formatter.deserialize(file_object)


def serialize(data: Dict, extension: str = '.yml') -> str:
    formatter = _get_formatter(extension)
    return formatter.serialize(data)


def _get_formatter(extension: str):
    with suppress(KeyError):
        return _REGISTRY[extension]

    for formatter in Formatter.__subclasses__():
        if extension in formatter.extensions():
            return formatter

    raise ValueError(f'Unsupported file extension: {extension!r}')
