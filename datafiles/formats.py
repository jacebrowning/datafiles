# pylint: disable=import-outside-toplevel

import json
from abc import ABCMeta, abstractmethod
from contextlib import suppress
from io import StringIO
from pathlib import Path
from typing import IO, Dict, List

import log

from . import settings, types


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
        return {'.json'}

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
        return {'.toml'}

    @classmethod
    def deserialize(cls, file_object):
        import tomlkit

        return tomlkit.loads(file_object.read())

    @classmethod
    def serialize(cls, data):
        import tomlkit

        return tomlkit.dumps(data)


class RuamelYAML(Formatter):
    """Formatter for (round-trip) YAML Ain't Markup Language."""

    @classmethod
    def extensions(cls):
        return {'.yml', '.yaml'}

    @classmethod
    def deserialize(cls, file_object):
        from ruamel.yaml import YAML

        yaml = YAML()
        yaml.preserve_quotes = True  # type: ignore
        try:
            return yaml.load(file_object)
        except NotImplementedError as e:
            log.error(str(e))
            return {}

    @classmethod
    def serialize(cls, data):
        from ruamel.yaml import YAML

        yaml = YAML()
        yaml.register_class(types.List)
        yaml.register_class(types.Dict)
        if settings.INDENT_YAML_BLOCKS:
            yaml.indent(mapping=2, sequence=4, offset=2)

        stream = StringIO()
        yaml.dump(data, stream)
        text = stream.getvalue().strip() + '\n'

        if text == "{}\n":
            return ""

        return text.replace('- \n', '-\n')


class PyYAML(Formatter):
    """Formatter for YAML Ain't Markup Language."""

    @classmethod
    def extensions(cls):
        return {'.yml', '.yaml'}

    @classmethod
    def deserialize(cls, file_object):
        import yaml

        return yaml.safe_load(file_object)

    @classmethod
    def serialize(cls, data):
        import yaml

        def represent_none(self, _):
            return self.represent_scalar('tag:yaml.org,2002:null', '')

        yaml.add_representer(type(None), represent_none)

        class Dumper(yaml.Dumper):
            def increase_indent(self, flow=False, indentless=False):
                return super().increase_indent(
                    flow=flow,
                    indentless=False if settings.INDENT_YAML_BLOCKS else indentless,
                )

        text = yaml.dump(data, Dumper=Dumper, sort_keys=False, default_flow_style=False)

        return text


def deserialize(path: Path, extension: str, *, formatter=None) -> Dict:
    if formatter is None:
        formatter = _get_formatter(extension)
    with path.open('r') as file_object:
        data = formatter.deserialize(file_object)
        if data is None:
            log.debug(f"No data in {path}")
            data = {}
        elif not isinstance(data, dict):
            log.error(f"Invalid data in {path}: {data!r}")
            data = {}
        return data


def serialize(data: Dict, extension: str = '.yml', *, formatter=None) -> str:
    if formatter is None:
        formatter = _get_formatter(extension)
    return formatter.serialize(data)


def _get_formatter(extension: str):
    if settings.YAML_LIBRARY == 'PyYAML':  # pragma: no cover
        register('.yml', PyYAML)

    with suppress(KeyError):
        return _REGISTRY[extension]

    for formatter in Formatter.__subclasses__():
        if extension in formatter.extensions():
            return formatter

    raise ValueError(f'Unsupported file extension: {extension!r}')
