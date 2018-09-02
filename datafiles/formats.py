import json
from pathlib import Path
from typing import IO, Any, Dict, List, Text

from ruamel import yaml


class Formatter:
    @classmethod
    def extensions(cls) -> List[Text]:
        raise NotImplementedError

    @classmethod
    def deserialize(cls, file_object: IO[Any]) -> Dict:
        raise NotImplementedError

    @classmethod
    def serialize(cls, data: Dict) -> Text:
        raise NotImplementedError


class YAML(Formatter):
    @classmethod
    def extensions(cls):
        return {'.yml', '.yaml'}

    @classmethod
    def deserialize(cls, file_object):
        return yaml.YAML(typ='safe').load(file_object) or {}

    @classmethod
    def serialize(cls, data):
        text = yaml.round_trip_dump(data)
        return "" if text == "{}\n" else text


class JSON(Formatter):
    @classmethod
    def extensions(cls):
        return {'.json'}

    @classmethod
    def deserialize(cls, file_object):
        return json.load(file_object) or {}

    @classmethod
    def serialize(cls, data):
        return json.dumps(data)


def deserialize(path: Path, extension: Text) -> Dict:
    for formatter in Formatter.__subclasses__():
        if extension in formatter.extensions():
            with path.open('r') as file_object:
                return formatter.deserialize(file_object)

    raise ValueError(f'Unsupported file extension: {extension}')


def serialize(data: Dict, extension: Text) -> Text:
    for formatter in Formatter.__subclasses__():
        if extension in formatter.extensions():
            return formatter.serialize(data)

    raise ValueError(f'Unsupported file extension: {extension}')
