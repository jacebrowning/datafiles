import dataclasses
import inspect
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

import log

from . import formats


cached = lru_cache()


class ModelManager:
    def __init__(self, cls):
        self.model = cls

    def all(self):
        raise NotImplementedError


class InstanceManager:
    def __init__(
        self, *, instance: Any, pattern: Optional[str], attrs: Dict
    ) -> None:
        self._instance = instance
        self._pattern = pattern
        self.attrs = attrs

    @property
    def path(self) -> Optional[Path]:
        return self._get_path()

    @cached
    def _get_path(self) -> Optional[Path]:
        if not self._pattern:
            log.debug(f'{self!r} has no path pattern')
            return None

        log.debug(f'Formatting pattern: {self._pattern}')
        relpath = self._pattern.format(self=self._instance)

        root = Path(inspect.getfile(self._instance.__class__)).parent
        log.debug(f'Root directory: {root}')

        path = (root / relpath).resolve()
        log.info(f'Path: {path}')
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
        class_name = self._instance.__class__.__name__
        log.debug(f'Converting object ({class_name}) to data')
        data: Dict = dataclasses.asdict(self._instance)

        for name in list(data.keys()):
            if name not in self.attrs:
                log.debug(f'Removed unmapped attribute: {name}')
                data.pop(name)

        for name, converter in self.attrs.items():
            value = data[name]
            log.debug(f"Converting '{name}' as {converter}: {value!r}")
            if dataclasses.is_dataclass(converter):
                if value is None:
                    value = {}
                for field in dataclasses.fields(converter):
                    if field.name not in value:
                        log.debug(
                            f'Added missing nested attribute: {field.name}'
                        )
                        value[field.name] = None

                data[name] = converter(**value).datafile.data
            else:
                data[name] = converter.to_preserialization_data(value)

        log.info(f'Data: {data}')
        return data

    @property
    def text(self) -> str:
        extension = self.path.suffix if self.path else '.yml'
        log.debug(f'Converting data to text ({extension}): {self.data}')

        text = formats.serialize(self.data, extension)
        log.info(f'Text ({extension}): {text!r}')

        return text

    def load(self, *, initial=False) -> None:
        log.info(f'Loading values for {self._instance}')

        if self.path:
            data = formats.deserialize(self.path, self.path.suffix)
        else:
            raise RuntimeError("'pattern' must be set to load the model")

        for name, converter in self.attrs.items():

            if dataclasses.is_dataclass(converter):
                # TODO: Support nesting unlimited levels
                data2 = data.get(name)
                log.debug(f'Converting nested data to Python: {data2}')

                value = getattr(self._instance, name)
                if value is None:
                    for field in dataclasses.fields(converter):
                        if field.name not in data2:  # type: ignore
                            data2[field.name] = None  # type: ignore
                    value = converter(**data2)
                elif initial:
                    continue  # TODO: Test this

                manager2 = value.datafile
                for name2, converter2 in manager2.attrs.items():
                    _value2 = data2.get(  # type: ignore
                        # pylint: disable=protected-access
                        name2,
                        manager2._get_default_field_value(name2),
                    )
                    value2 = converter2.to_python_value(_value2)
                    log.debug(f"'{name2}' as Python: {value2}")
                    setattr(value, name2, value2)

                log.debug(f"Setting '{name}' value: {value!r}")
                setattr(self._instance, name, value)

            else:
                default_value = self._get_default_field_value(name)
                initial_value = getattr(self._instance, name)
                file_value = data.get(name, default_value)

                if initial and file_value == default_value:
                    log.debug(
                        f"Ignoring default '{name}' value: {default_value!r}"
                    )
                    continue

                if initial and initial_value != default_value:
                    log.debug(
                        f"Ignoring default '{name}' value: {default_value!r}"
                    )
                    continue

                value = converter.to_python_value(file_value)
                log.debug(f"Setting '{name}' value: {file_value!r}")
                setattr(self._instance, name, value)

    def _get_default_field_value(self, name):
        for field in dataclasses.fields(self._instance):
            if field.name == name:
                # pylint: disable=protected-access
                if not isinstance(field.default, dataclasses._MISSING_TYPE):
                    return field.default
        return None

    def save(self) -> None:
        log.info(f'Saving data for {self._instance}')

        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(self.text)
        else:
            raise RuntimeError(f"'pattern' must be set to save the model")
