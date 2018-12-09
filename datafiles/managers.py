import dataclasses
import inspect
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

    @cached_property
    def path(self) -> Optional[Path]:
        if not self._pattern:
            return None

        cls = self._instance.__class__
        try:
            root = Path(inspect.getfile(cls)).parent
        except TypeError:
            level = log.DEBUG if '__main__' in str(cls) else log.WARNING
            log.log(level, f'Unable to determine module for {cls}')
            root = Path.cwd()

        relpath = self._pattern.format(self=self._instance)
        return (root / relpath).resolve()

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

            if hasattr(converter, 'DATACLASS'):
                log.debug(f"Converting '{name}' dataclass with {converter}")
                if value is None:
                    value = {}

                for field in dataclasses.fields(converter.DATACLASS):
                    if field.name not in value:
                        log.debug(
                            f'Added missing nested attribute: {field.name}'
                        )
                        value[field.name] = None

                data[name] = converter.to_preserialization_data(
                    value,
                    default=Missing
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
                log.debug(
                    f"Converting '{name}' value with {converter}: {value!r}"
                )
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
        log.info(f'Serialized data to text ({extension}): {text!r}')
        return text

    @prevent_recursion
    def load(self, *, first_load=False) -> None:
        log.info(f'Loading values for {self._instance.__class__} instance')

        if not self.path:
            raise RuntimeError("'pattern' must be set to load the model")

        message = f'Deserializing: {self.path}'
        frame = '=' * len(message)
        log.info(message)
        data = formats.deserialize(self.path, self.path.suffix)
        self._last_data = data
        log.debug(frame + '\n\n' + prettify(data) + '\n')
        log.debug(frame)

        for name, converter in self.attrs.items():
            log.debug(f"Converting '{name}' data with {converter}")

            if hasattr(converter, 'DATACLASS'):
                self._set_container_value(data, name, converter, first_load)
            else:
                self._set_attribute_value(data, name, converter, first_load)

        log.info(f'Loaded values for object: {self._instance}')

    def _set_container_value(self, data, name, converter, first_load):
        # TODO: Support nesting unlimited levels
        # https://github.com/jacebrowning/datafiles/issues/22
        data2 = data.get(name)
        if data2 is None:
            return

        log.debug(f'Converting nested data to Python: {data2}')

        value = getattr(self._instance, name)
        if value is None:
            for field in dataclasses.fields(converter.DATACLASS):
                if field.name not in data2:  # type: ignore
                    data2[field.name] = None  # type: ignore
            value = converter.to_python_value(data2)
        elif first_load:
            return

        try:
            manager2 = value.datafile
        except AttributeError:
            # TODO: Figure out why datafile wasn't set
            from .models import get_datafile

            manager2 = get_datafile(value)

        for name2, converter2 in manager2.attrs.items():
            _value2 = data2.get(  # type: ignore
                # pylint: disable=protected-access
                name2,
                manager2._get_default_field_value(name2),
            )
            value2 = converter2.to_python_value(_value2)
            log.debug(f"'{name2}' as Python: {value2!r}")
            setattr(value, name2, value2)

        log.debug(f"Setting '{name}' value: {value!r}")
        setattr(self._instance, name, value)

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
                log.debug(
                    f"Keeping non-default '{name}' init value: {init_value!r}"
                )
                return

        if file_value is Missing:
            if default_value is Missing:
                value = converter.to_python_value(None)
            else:
                value = converter.to_python_value(default_value)
        else:
            value = converter.to_python_value(file_value)

        log.info(f"Setting '{name}' value: {value!r}")
        setattr(self._instance, name, value)

    def _get_default_field_value(self, name):
        for field in dataclasses.fields(self._instance):
            if field.name == name:
                if not isinstance(field.default, Missing):
                    return field.default

                if not isinstance(
                    field.default_factory, Missing  # type: ignore
                ):
                    return field.default_factory()  # type: ignore

                if not field.init and hasattr(self._instance, '__post_init__'):
                    return getattr(self._instance, name)

        return Missing

    @prevent_recursion
    def save(self, include_default_values: Trilean = None) -> None:
        log.info(f'Saving data for object: {self._instance}')

        if not self.path:
            raise RuntimeError(f"'pattern' must be set to save the model")

        text = self._get_text(include_default_values=include_default_values)

        self.path.parent.mkdir(parents=True, exist_ok=True)

        message = f'Writing: {self.path}'
        frame = '=' * len(message)
        log.info(message)
        log.debug(frame + '\n\n' + (text or '<nothing>\n'))
        self.path.write_text(text)
        log.debug(frame)

        self.modified = False
