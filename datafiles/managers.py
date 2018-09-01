import dataclasses
import inspect
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
    def path(self) -> Optional[Path]:
        return self.get_path()

    @cached
    def get_path(self) -> Optional[Path]:
        if not self._pattern:
            log.debug(f'{self!r} has no path pattern')
            return None

        log.debug(f'Formatting pattern: {self._pattern}')
        relpath = self._pattern.format(self=self._instance)

        root = Path(inspect.getfile(self._instance.__class__)).parent
        log.debug(f'Datafile root directory: {root}')

        path = (root / relpath).resolve()
        log.debug(f'Path: {path}')
        return path

    @property
    def exists(self) -> bool:
        if not self.path:
            log.debug("'pattern' not set so datafile will never exist")
            return False

        log.debug(f'{self.path} exists: {self.path.exists()}')
        return self.path.exists()

    @property
    def data(self) -> Dict:
        return self.get_data()

    def get_data(self) -> Dict:
        class_name = self._instance.__class__.__name__
        log.debug(f'Converting {class_name} to data')
        data: Dict = dataclasses.asdict(self._instance)

        for key in list(data.keys()):
            if key not in self.fields:
                log.debug(f'Removed unmapped field: {key}')
                data.pop(key)

        for name, field in self.fields.items():
            value = data[name]
            log.debug(f"Converting '{name}' as {field.__name__}: {value!r}")
            if dataclasses.is_dataclass(field):
                if value is None:
                    value = {}
                for f in dataclasses.fields(field):
                    if f.name not in value:
                        log.debug(f'Added missing nested attribute: {f.name}')
                        value[f.name] = None

                data[name] = field(**value).datafile.get_data()
            else:
                data[name] = field.to_data(value)

        log.debug(f'Data: {data}')
        return data

    @property
    def text(self) -> str:
        return self.get_text()

    def get_text(self, extension='.yml') -> str:
        log.debug(f'Converting data to text ({extension}): {self.data}')

        text = None
        if extension in {'.yml', '.yaml'}:
            text = yaml.round_trip_dump(self.data) if self.fields else ""
        elif extension in {'.json'}:
            text = json.dumps(self.data)

        if text is None:
            raise ValueError(f'Unsupported file extension: {extension!r}')

        log.debug(f'Text ({extension}): {text!r}')
        return text

    def load(self) -> None:
        if not self.path:
            raise RuntimeError("'pattern' must be set to load the model")

        with self.path.open('r') as infile:

            data = None
            if self.path.suffix in {'.yml', '.yaml'}:
                data = yaml.YAML(typ='safe').load(infile) or {}
            elif self.path.suffix in {'.json'}:
                data = json.load(infile) or {}

        if data is None:
            raise ValueError(
                f'Unsupported file extension: {self.path.suffix!r}'
            )

        for name, field in self.fields.items():
            if dataclasses.is_dataclass(field):
                # TODO: Support nesting unlimited levels
                data2 = data.get(name)
                log.debug(f'Converting nested data to Python: {data2}')

                value = getattr(self._instance, name)
                if value is None:
                    for f in dataclasses.fields(field):
                        if f.name not in data2:  # type: ignore
                            data2[f.name] = None  # type: ignore
                    value = field(**data2)

                manager2 = value.datafile
                for name2, field2 in manager2.fields.items():
                    _value2 = data2.get(  # type: ignore
                        # pylint: disable=protected-access
                        name2,
                        manager2._get_default_field_value(name2),
                    )
                    value2 = field2.to_python(_value2)
                    log.debug(f"'{name2}' as Python: {value2}")
                    setattr(value, name2, value2)

                setattr(self._instance, name, value)

            else:
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

        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(self.text)
