import dataclasses
import inspect
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

import log
from cachetools import cached

from . import formats
from .converters import List
from .utils import Missing, prettify, prevent_recursion


class ModelManager:
    def __init__(self, cls):
        self.model = cls

    def all(self):
        raise NotImplementedError


class BaseInstanceManager(metaclass=ABCMeta):

    _kind: str
    _instance: Any
    _last_data: Dict[str, Any]

    attrs: Dict[str, Any]
    defaults: bool

    @abstractmethod
    def load(self, *, first_load=False) -> None:
        raise NotImplementedError

    @abstractmethod
    def save(self, include_default_values=None) -> None:
        raise NotImplementedError

    def _get_data(self, include_default_values=None) -> Dict:
        log.debug(f'Preserializing {self._kind} to data: {self._instance!r}')
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

            if dataclasses.is_dataclass(converter):
                log.debug(f"Converting '{name}' dataclass with {converter}")
                if value is None:
                    value = {}

                for field in dataclasses.fields(converter):
                    if field.name not in value:
                        log.debug(
                            f'Added missing nested attribute: {field.name}'
                        )
                        value[field.name] = None

                data[name] = converter(**value).datafile.data

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

        log.debug(f'Preserialized {self._kind} data: {data}')
        return data

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


class InstanceManager(BaseInstanceManager):

    _kind = "object"

    def __init__(
        self,
        instance: Any,
        *,
        attrs: Dict,
        pattern: Optional[str],
        # TODO: Should these be required?
        manual: bool = False,
        defaults: bool = False,
    ) -> None:
        self._instance = instance
        self._pattern = pattern
        self.attrs = attrs
        self.manual = manual
        self.defaults = defaults
        self._last_load = 0.0
        self._last_data: Dict = {}

    def __repr__(self):
        obj = object.__repr__(self._instance)
        location = f"'{self.path}'" if self._pattern else '(nowhere)'
        return f'{obj} => {location}'

    @property
    def path(self) -> Optional[Path]:
        return self._get_path()

    @cached(cache={})
    @prevent_recursion
    def _get_path(self) -> Optional[Path]:
        if not self._pattern:
            return None

        try:
            root = Path(inspect.getfile(self._instance.__class__)).parent
        except TypeError:
            log.warn(f'Unable to determine module for {self._instance}')
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
        frame = '=' * (len(message) - 1)  # "DEBUG" has an extra letter
        log.info(message)
        data = formats.deserialize(self.path, self.path.suffix)
        self._last_data = data
        log.debug(frame + '\n\n' + prettify(data) + '\n')
        log.debug(frame)

        for name, converter in self.attrs.items():
            log.debug(f"Converting '{name}' data with {converter}")

            if dataclasses.is_dataclass(converter):
                self._set_container_value(data, name, converter)
            else:
                self._set_attribute_value(data, name, converter, first_load)

        log.info(f'Loaded values for object: {self._instance}')

        self.modified = False

    def _set_container_value(self, data, name, converter):
        # TODO: Support nesting unlimited levels
        # https://github.com/jacebrowning/datafiles/issues/22
        data2 = data.get(name)
        if data2 is None:
            return

        log.debug(f'Converting nested data to Python: {data2}')

        value = getattr(self._instance, name)
        if value is None:
            for field in dataclasses.fields(converter):
                if field.name not in data2:  # type: ignore
                    data2[field.name] = None  # type: ignore
            value = converter(**data2)

        manager2 = value.datafile
        for name2, converter2 in manager2.attrs.items():
            _value2 = data2.get(  # type: ignore
                # pylint: disable=protected-access
                name2,
                manager2._get_default_field_value(name2),
            )
            if dataclasses.is_dataclass(converter2):
                value2 = converter2(**_value2)
            else:
                # TODO: Consider patching this method onto dataclasses
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

    @prevent_recursion
    def save(self, include_default_values=None) -> None:
        log.info(f'Saving data for object: {self._instance}')

        if not self.path:
            raise RuntimeError(f"'pattern' must be set to save the model")

        text = self._get_text(include_default_values=include_default_values)

        message = f'Writing: {self.path}'
        frame = '=' * (len(message) - 1)  # "DEBUG" has an extra letter
        log.info(message)
        log.debug(frame + '\n\n' + (text or '<nothing>\n'))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(text)
        log.debug(frame)

        self.modified = False


class NestedInstanceManager(BaseInstanceManager):

    _kind = "nested object"

    def __init__(
        self,
        instance: Any,
        *,
        root: InstanceManager,
        attrs: Dict,
        # TODO: Should these be required?
        manual: bool = False,
        defaults: bool = False,
    ) -> None:
        self._instance = instance
        self.attrs = attrs
        self.manual = manual
        self.defaults = defaults
        self._root = root

    def load(self, *, first_load=False) -> None:
        self._root.load(first_load=first_load)

    def save(self, include_default_values=None) -> None:
        self._root.save(include_default_values=include_default_values)

    # TODO: should this have data? text?

    # TODO: Leave default repr?
    # def __repr__(self):
    #     obj = object.__repr__(self._instance)
    #     root = object.__repr__(self._root)
    #     location = f"'{self._root.path}'" if self._root._pattern else '(nowhere)'
    #     return f'{obj} => {location}'
