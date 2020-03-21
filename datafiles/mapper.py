"""Defines methods to synchronize model instances to the filesystem."""

from __future__ import annotations

import dataclasses
import inspect
import os
from pathlib import Path
from typing import Any, Dict, Optional

import log
from cached_property import cached_property

from . import config, formats, hooks
from .converters import Converter, List, map_type
from .utils import display, recursive_update, write


Trilean = Optional[bool]
Missing = dataclasses._MISSING_TYPE


class Mapper:
    def __init__(
        self,
        instance: Any,
        *,
        attrs: Dict,
        pattern: Optional[str],
        manual: bool,
        defaults: bool,
        auto_load: bool,
        auto_save: bool,
        auto_attr: bool,
        root: Optional[Mapper] = None,
    ) -> None:
        assert manual is not None
        assert defaults is not None
        self._instance = instance
        self.attrs = attrs
        self._pattern = pattern
        self._manual = manual
        self.defaults = defaults
        self._auto_load = auto_load
        self._auto_save = auto_save
        self._auto_attr = auto_attr
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

        path = Path(self._pattern.format(self=self._instance))
        if path.is_absolute() or self._pattern.startswith('./'):
            return path.resolve()

        cls = self._instance.__class__
        try:
            root = Path(inspect.getfile(cls)).parent
        except TypeError:
            level = log.DEBUG if '__main__' in str(cls) else log.WARNING
            log.log(level, f'Unable to determine module for {cls}')
            root = Path.cwd()

        return (root / path).resolve()

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
    def manual(self) -> bool:
        return self._root.manual if self._root else self._manual

    @property
    def auto_load(self) -> bool:
        return self._root.auto_load if self._root else self._auto_load

    @property
    def auto_save(self) -> bool:
        return self._root.auto_save if self._root else self._auto_save

    @property
    def auto_attr(self) -> bool:
        return self._root.auto_attr if self._root else self._auto_attr

    @property
    def data(self) -> Dict:
        return self._get_data()

    def _get_data(self, include_default_values: Trilean = None) -> Dict:
        log.debug(f'Preserializing object to data: {self._instance!r}')
        if include_default_values is None:
            include_default_values = self.defaults

        if self.auto_attr:
            data = recursive_update(self._last_data, self._instance.__dict__)
        else:
            data = recursive_update(self._last_data, dataclasses.asdict(self._instance))

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
                    default_to_skip=Missing
                    if include_default_values
                    else self._get_default_field_value(name),
                )

            elif (
                value == self._get_default_field_value(name)
                and not include_default_values
            ):
                log.debug(f"Skipped default value of {value!r} for {name!r} attribute")
                data.pop(name)

            else:
                log.debug(f"Converting '{name}' value with {converter}: {value!r}")
                data[name] = converter.to_preserialization_data(value)

        log.debug(f'Preserialized object data: {data}')
        return data

    @property
    def text(self) -> str:
        return self._get_text()

    def _get_text(self, **kwargs) -> str:
        data = self._get_data(**kwargs)
        if self.path and self.path.suffix:
            return formats.serialize(data, self.path.suffix)
        return formats.serialize(data)

    @text.setter  # type: ignore
    def text(self, value: str):
        write(self.path, value.strip() + '\n')

    def load(self, *, _log=True, _first=False) -> None:
        if self._root:
            self._root.load(_log=_log, _first=_first)
            return

        if self.path:
            if _log:
                log.info(f"Loading '{self.classname}' object from '{self.relpath}'")
        else:
            raise RuntimeError("'pattern' must be set to load the model")

        data = formats.deserialize(self.path, self.path.suffix)
        self._last_data = data
        display(self.path, data)

        with hooks.disabled():

            for name, value in data.items():
                if name not in self.attrs and self.auto_attr:
                    cls: Any = type(value)
                    if issubclass(cls, list):
                        cls.__origin__ = list

                        if value:
                            item_cls = type(value[0])
                            for item in value:
                                if not isinstance(item, item_cls):
                                    log.warn(f'{name!r} list type cannot be inferred')
                                    item_cls = Converter
                                    break
                        else:
                            log.warn(f'{name!r} list type cannot be inferred')
                            item_cls = Converter

                        log.debug(f'Inferring {name!r} type: {cls} of {item_cls}')
                        self.attrs[name] = map_type(cls, name=name, item_cls=item_cls)
                    elif issubclass(cls, dict):
                        cls.__origin__ = dict

                        log.debug(f'Inferring {name!r} type: {cls}')
                        self.attrs[name] = map_type(cls, name=name, item_cls=Converter)
                    else:
                        log.debug(f'Inferring {name!r} type: {cls}')
                        self.attrs[name] = map_type(cls, name=name)

            for name, converter in self.attrs.items():
                log.debug(f"Converting '{name}' data with {converter}")

                if getattr(converter, 'DATACLASS', None):
                    self._set_dataclass_value(data, name, converter)
                else:
                    self._set_attribute_value(data, name, converter, _first)

            hooks.apply(self._instance, self)

        self.modified = False

    def _set_dataclass_value(self, data, name, converter):
        nested_data = data.get(name)
        if nested_data is None:
            return

        log.debug(f'Converting nested data to Python: {nested_data}')

        dataclass = getattr(self._instance, name)
        if dataclass is None:
            for field in dataclasses.fields(converter.DATACLASS):
                if field.name not in nested_data:
                    nested_data[field.name] = None
            dataclass = converter.to_python_value(nested_data, target_object=dataclass)

        mapper = create_mapper(dataclass)
        for name2, converter2 in mapper.attrs.items():
            _value = nested_data.get(name2, mapper._get_default_field_value(name2))
            value = converter2.to_python_value(
                _value, target_object=getattr(dataclass, name2)
            )
            log.debug(f"'{name2}' as Python: {value!r}")
            setattr(dataclass, name2, value)

        log.debug(f"Setting '{name}' value: {dataclass!r}")
        setattr(self._instance, name, dataclass)

    def _set_attribute_value(self, data, name, converter, first_load):
        file_value = data.get(name, Missing)
        init_value = getattr(self._instance, name, Missing)
        default_value = self._get_default_field_value(name)

        if first_load:
            log.debug(
                'Initial load values: file=%r, init=%r, default=%r',
                file_value,
                init_value,
                default_value,
            )

            if init_value != default_value and not issubclass(converter, List):
                log.debug(f"Keeping non-default '{name}' init value: {init_value!r}")
                return

        if file_value is Missing:
            if default_value is Missing:
                value = converter.to_python_value(None, target_object=init_value)
            else:
                value = converter.to_python_value(
                    default_value, target_object=init_value
                )
        else:
            value = converter.to_python_value(file_value, target_object=init_value)

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

    def save(self, *, include_default_values: Trilean = None, _log=True) -> None:
        if self._root:
            self._root.save(include_default_values=include_default_values, _log=_log)
            return

        if self.path:
            if _log:
                log.info(f"Saving '{self.classname}' object to '{self.relpath}'")
        else:
            raise RuntimeError(f"'pattern' must be set to save the model")

        with hooks.disabled():
            text = self._get_text(include_default_values=include_default_values)

        write(self.path, text)

        self.modified = False


def create_mapper(obj, root=None) -> Mapper:
    try:
        return object.__getattribute__(obj, 'datafile')
    except AttributeError:
        log.debug(f"Building 'datafile' for {obj.__class__} object")

    meta = config.load(obj)
    attrs = meta.datafile_attrs
    pattern = meta.datafile_pattern

    if attrs is None and dataclasses.is_dataclass(obj):
        attrs = {}
        log.debug(f'Mapping attributes for {obj.__class__} object')
        for field in dataclasses.fields(obj):
            self_name = f'self.{field.name}'
            if pattern is None or self_name not in pattern:
                attrs[field.name] = map_type(field.type, name=field.name)

    return Mapper(
        obj,
        attrs=attrs or {},
        pattern=pattern,
        manual=meta.datafile_manual,
        defaults=meta.datafile_defaults,
        auto_load=meta.datafile_auto_load,
        auto_save=meta.datafile_auto_save,
        auto_attr=meta.datafile_auto_attr,
        root=root,
    )
