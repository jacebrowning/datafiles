# pylint: disable=no-self-argument,protected-access,attribute-defined-outside-init

import dataclasses
from contextlib import suppress
from typing import Dict, Optional

from classproperties import classproperty

from .converters import Converter, map_type
from .managers import InstanceManager, ModelManager


@dataclasses.dataclass
class ModelMeta:
    datafile_pattern: Optional[str] = None
    datafile_attrs: Optional[Dict[str, Converter]] = None


class Model:

    Meta: ModelMeta

    def __post_init__(self):
        if self.datafile.exists:
            self.datafile.load(first_load=True)

    @classproperty
    def datafiles(cls) -> ModelManager:
        return ModelManager(cls)

    @property
    def datafile(self) -> InstanceManager:
        return self._get_datafile()

    def _get_datafile(self) -> InstanceManager:
        with suppress(AttributeError):
            return getattr(self, '_datafile')

        m = getattr(self, 'Meta', None)
        pattern = getattr(m, 'datafile_pattern', None)
        attrs = getattr(m, 'datafile_attrs', None)

        if attrs is None:
            attrs = {}
            for field in dataclasses.fields(self):
                self_name = f'self.{field.name}'
                if pattern is None or self_name not in pattern:
                    attrs[field.name] = map_type(field.type, patch_dataclass)

        manager = InstanceManager(instance=self, pattern=pattern, attrs=attrs)
        self._datafile = manager
        return manager


def patch_dataclass(cls, pattern, attrs):
    """Patch datafile attributes on to an existing dataclass."""

    if not dataclasses.is_dataclass(cls):
        raise ValueError(f'{cls} must be a dataclass')

    # Patch Meta

    m = getattr(cls, 'Meta', ModelMeta())
    m.datafile_pattern = getattr(m, 'datafile_pattern', None) or pattern
    m.datafile_attrs = getattr(m, 'datafile_attrs', None) or attrs
    cls.Meta = m

    # Patch datafile

    cls.datafile = property(Model._get_datafile)

    # Patch __init__

    init = cls.__init__

    def modified_init(self, *args, **kwargs):
        init(self, *args, **kwargs)
        if self.datafile.exists:
            self.datafile.load(first_load=True)

    cls.__init__ = modified_init
    cls.__init__.__doc__ = init.__doc__

    return cls
