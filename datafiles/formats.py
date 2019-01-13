import json
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import IO, Any, Dict, List

import tomlkit
from ruamel import yaml


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
        return yaml.YAML(typ='rt').load(file_object) or {}

    @classmethod
    def serialize(cls, data):
        text = yaml.round_trip_dump(data)
        return "" if text == "{}\n" else text


def deserialize(path: Path, extension: str) -> Dict:
    for formatter in Formatter.__subclasses__():
        if extension in formatter.extensions():
            with path.open('r') as file_object:
                return formatter.deserialize(file_object)

    raise ValueError(f'Unsupported file extension: {extension}')


def serialize(data: Dict, extension: str = '.yml') -> str:
    for formatter in Formatter.__subclasses__():
        if extension in formatter.extensions():
            return formatter.serialize(data)

    raise ValueError(f'Unsupported file extension: {extension!r}')
