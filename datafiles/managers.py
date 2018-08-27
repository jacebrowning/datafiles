import dataclasses
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

import log
from ruamel import yaml


cached = lru_cache()


class ModelManager:
    def __init__(self, cls):
        self.model = cls

    def all(self):
        raise NotImplementedError


class InstanceManager:
    def __init__(
        self, *, instance: Any, pattern: Optional[str], fields: Dict
    ) -> None:
        self._instance = instance
        self._pattern = pattern
        self.fields = fields

    @property
    def path(self) -> Optional[str]:
        return self.get_path()

    @property
    def data(self) -> Dict:
        return self.get_data()

    @property
    def text(self) -> str:
        return self.get_text()

    @cached
    def get_path(self) -> Optional[str]:
        if not self._pattern:
            log.debug(f'{self!r} has no path pattern')
            return None

        log.debug(f'Formatting pattern: {self._pattern}')
        path = self._pattern.format(self=self._instance)
        log.debug(f'Path: {path}')
        return path

    def get_data(self) -> Dict:
        data: Dict = dataclasses.asdict(self._instance)

        for key in list(data.keys()):
            if key not in self.fields:
                log.debug(f'Removed unmapped field: {key}')
                data.pop(key)

        print(repr(self.fields))
        for name, field in self.fields.items():
            data[name] = field.to_data(data[name])

        return data

    def get_text(self, extension='yaml') -> str:
        log.debug(f'Converting to {extension}: {self.data}')

        text = None
        if extension in {'yml', 'yaml'}:
            text = yaml.round_trip_dump(self.data) if self.fields else ""
        elif extension in {'json'}:
            text = json.dumps(self.data)

        if text is None:
            raise ValueError(f'Unsupported file extension: {extension!r}')

        log.debug(f'Text: {text!r}')
        return text

    def load(self, extension='yaml') -> None:
        if not self.path:
            raise RuntimeError(f"'pattern' must be set to load the model")

        path = Path(self.path)
        with path.open('r') as infile:

            data = None
            if extension in {'yml', 'yaml'}:
                data = yaml.YAML(typ='safe').load(infile) or {}
            elif extension in {'json'}:
                data = json.load(infile) or {}

        if data is None:
            raise ValueError(f'Unsupported file extension: {extension!r}')

        for name, field in self.fields.items():
            value = data.get(name, self._get_default_field_value(name))
            setattr(self._instance, name, field.to_python(value))

    def _get_default_field_value(self, name):
        for field in dataclasses.fields(self._instance):
            if field.name == name:
                # pylint: disable=protected-access
                if not isinstance(field.default, dataclasses._MISSING_TYPE):
                    return field.default
        return None

    def save(self) -> None:
        if not self.path:
            raise RuntimeError(f"'pattern' must be set to save the model")

        path = Path(self.path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w') as outfile:
            outfile.write(self.text)
