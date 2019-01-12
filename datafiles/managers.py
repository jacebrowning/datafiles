from __future__ import annotations

import dataclasses
import inspect
import os
from pathlib import Path
from typing import Any, Dict, Optional

import log
from cached_property import cached_property

from . import formats
from .converters import List
from .utils import Missing, prettify, prevent_recursion


Trilean = Optional[bool]


class ModelManager:
    def __init__(self, cls):
        self.model = cls

    def all(self):
        raise NotImplementedError


class InstanceManager:
    def __init__(
        self,
        instance: Any,
        *,
        attrs: Dict,
        pattern: Optional[str],
        manual: bool,
        defaults: bool,
        root: Optional[InstanceManager] = None,
    ) -> None:
        assert manual is not None
        assert defaults is not None
        self._instance = instance
        self.attrs = attrs
        self._pattern = pattern
        self.manual = manual
        self.defaults = defaults
        self._last_load = 0.0
        self._last_data: Dict = {}
        self._root = root

    @property
    def classname(self) -> str:
        return self._instance.__class__.__name__

    @cached_property
    def path(self) -> Optional[Path]:
        if not self._pattern:
            return None

        cls = self._instance.__class__
        try:
            root = Path(inspect.getfile(cls)).parent
        except TypeError:  # pragma: no cover
            level = log.DEBUG if '__main__' in str(cls) else log.WARNING
            log.log(level, f'Unable to determine module for {cls}')
            root = Path.cwd()

        relpath = self._pattern.format(self=self._instance)
        return (root / relpath).resolve()

    @property
    def relpath(self) -> Path:
        return Path(os.path.relpath(self.path, Path.cwd()))

    @property
    def exists(self) -> bool:
        if self.path:
            return self.path.exists()
        return False

    @property
    def modified(self) -> bool:
        if self.path:
            return self._last_load != self.path.stat().st_mtime
        return True

    @modified.setter
    def modified(self, modified: bool):
        if modified:
            self._last_load = 0.0
        else:
            assert self.path, 'Cannot mark a missing file as unmodified'
            self._last_load = self.path.stat().st_mtime

    @property
    def data(self) -> Dict:
        return self._get_data()

    def _get_data(self, include_default_values: Trilean = None) -> Dict:
        log.debug(f'Preserializing object to data: {self._instance!r}')
        if include_default_values is None:
            include_default_values = self.defaults

        self._last_data.update(dataclasses.asdict(self._instance))
        data = self._last_data

        for name in list(data.keys()):
            if name not in self.attrs:
                log.debug(f'Removed unmapped attribute: {name}')
                data.pop(name)

        for name, converter in self.attrs.items():
            value = data[name]

            if getattr(converter, 'DATACLASS', None):
                log.debug(f"Converting '{name}' dataclass with {converter}")
                if value is None:
                    value = {}

                for field in dataclasses.fields(converter.DATACLASS):
                    if field.name not in value:
                        log.debug(f'Added missing nested attribute: {field.name}')
                        value[field.name] = None

                data[name] = converter.to_preserialization_data(
                    value,
                    skip=Missing
                    if include_default_values
                    else self._get_default_field_value(name),
                )

            elif (
                value == self._get_default_field_value(name)
                and not include_default_values
            ):
                log.debug(f"Skipped default value for '{name}' attribute")
                data.pop(name)

            else:
                log.debug(f"Converting '{name}' value with {converter}: {value!r}")
                data[name] = converter.to_preserialization_data(value)

        log.debug(f'Preserialized object data: {data}')
        return data

    @property
    def text(self) -> str:
        return self._get_text()

    def _get_text(self, **kwargs):
        extension = self.path.suffix if self.path else '.yml'
        data = self._get_data(**kwargs)
        text = formats.serialize(data, extension)
        log.debug(f'Serialized data to text ({extension}): {text!r}')
        return text

    @prevent_recursion
    def load(self, *, first_load=False) -> None:
        if self._root:
            self._root.load(first_load=first_load)
            return

        if self.path:
            log.info(f"Loading '{self.classname}' object from '{self.relpath}'")
        else:
            raise RuntimeError("'pattern' must be set to load the model")

        message = f'Reading file: {self.path}'
        log.debug(message)
        data = formats.deserialize(self.path, self.path.suffix)
        self._last_data = data
        log.debug('=' * len(message) + '\n\n' + prettify(data) + '\n')

        for name, converter in self.attrs.items():
            log.debug(f"Converting '{name}' data with {converter}")

            if getattr(converter, 'DATACLASS', None):
                self._set_dataclass_value(data, name, converter)
            else:
                self._set_attribute_value(data, name, converter, first_load)

        self.modified = False

    def _set_dataclass_value(self, data, name, converter):
        # TODO: Support nesting unlimited levels
        # https://github.com/jacebrowning/datafiles/issues/22
        nested_data = data.get(name)
        if nested_data is None:
            return

        log.debug(f'Converting nested data to Python: {nested_data}')

        dataclass = getattr(self._instance, name)
        if dataclass is None:
            for field in dataclasses.fields(converter.DATACLASS):
                if field.name not in nested_data:  # type: ignore
                    nested_data[field.name] = None  # type: ignore
            dataclass = converter.to_python_value(nested_data, target=dataclass)

        # TODO: Figure out why datafile wasn't set
        if not hasattr(dataclass, 'datafile'):
            from .models import get_datafile

            log.warn(f"{dataclass} was missing 'datafile'")
            dataclass.datafile = get_datafile(dataclass)

        for name2, converter2 in dataclass.datafile.attrs.items():
            _value = nested_data.get(  # type: ignore
                # pylint: disable=protected-access
                name2,
                dataclass.datafile._get_default_field_value(name2),
            )
            value = converter2.to_python_value(_value, target=getattr(dataclass, name2))
            log.debug(f"'{name2}' as Python: {value!r}")
            setattr(dataclass, name2, value)

        log.debug(f"Setting '{name}' value: {dataclass!r}")
        setattr(self._instance, name, dataclass)

    def _set_attribute_value(self, data, name, converter, first_load):
        file_value = data.get(name, Missing)
        init_value = getattr(self._instance, name)
        default_value = self._get_default_field_value(name)

        if first_load:
            log.debug(
                'First load values: file=%r, init=%r, default=%r',
                file_value,
                init_value,
                default_value,
            )

            if init_value != default_value and not issubclass(converter, List):
                log.debug(f"Keeping non-default '{name}' init value: {init_value!r}")
                return

        if file_value is Missing:
            if default_value is Missing:
                value = converter.to_python_value(None, target=init_value)
            else:
                value = converter.to_python_value(default_value, target=init_value)
        else:
            value = converter.to_python_value(file_value, target=init_value)

        log.debug(f"Setting '{name}' value: {value!r}")
        setattr(self._instance, name, value)

    def _get_default_field_value(self, name):
        for field in dataclasses.fields(self._instance):
            if field.name == name:
                if not isinstance(field.default, Missing):
                    return field.default

                if not isinstance(field.default_factory, Missing):  # type: ignore
                    return field.default_factory()  # type: ignore

                if not field.init and hasattr(self._instance, '__post_init__'):
                    return getattr(self._instance, name)

        return Missing

    @prevent_recursion
    def save(self, include_default_values: Trilean = None) -> None:
        if self._root:
            self._root.save(include_default_values=include_default_values)
            return

        if self.path:
            log.info(f"Saving '{self.classname}' object to '{self.relpath}'")
        else:
            raise RuntimeError(f"'pattern' must be set to save the model")

        text = self._get_text(include_default_values=include_default_values)

        message = f'Writing file: {self.path}'
        log.debug(message)
        log.debug('=' * len(message) + '\n\n' + (text or '<nothing>\n'))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(text)

        self.modified = False
