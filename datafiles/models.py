# pylint: disable=no-self-argument,protected-access,attribute-defined-outside-init

import dataclasses
from typing import Dict, Optional

import log
from cachetools import cached
from classproperties import classproperty

from .converters import Converter, map_type
from .hooks import patch_methods
from .managers import InstanceManager, ModelManager


@dataclasses.dataclass
class ModelMeta:
    datafile_attrs: Optional[Dict[str, Converter]] = None
    datafile_pattern: Optional[str] = None

    datafile_manual: bool = False
    datafile_defaults: bool = False


class Model:

    Meta: ModelMeta

    def __post_init__(self):
        log.debug(f'Initializing {self.__class__} instance')

        path = self.datafile.path
        exists = self.datafile.exists
        automatic = not self.datafile.manual
        log.c(f'manual={self.datafile.manual}')

        if path:
            log.debug(f'Datafile path: {path}')
            log.debug(f'Datafile exists: {exists}')

            if exists:
                self.datafile.load(first_load=True)
            elif path:
                self.datafile.save()

            if automatic:
                patch_methods(self, self.datafile)

        log.debug(f'Initialized {self.__class__} instance')

    @classproperty
    def datafiles(cls) -> ModelManager:
        return ModelManager(cls)

    @property
    def datafile(self) -> InstanceManager:
        return self._get_datafile()

    @cached(cache={}, key=id)
    def _get_datafile(self) -> InstanceManager:
        m = getattr(self, 'Meta', None)
        pattern = getattr(m, 'datafile_pattern', None)
        attrs = getattr(m, 'datafile_attrs', None)
        manual = getattr(m, 'datafile_manual', False)
        defaults = getattr(m, 'datafile_defaults', False)

        if attrs is None:
            attrs = {}
            log.debug(f'Mapping attributes for {self.__class__} instance')
            for field in dataclasses.fields(self):
                self_name = f'self.{field.name}'
                if pattern is None or self_name not in pattern:
                    attrs[field.name] = map_type(
                        field.type, create_model=create_model, manual=True
                    )

        return InstanceManager(
            self,
            attrs=attrs,
            pattern=pattern,
            manual=manual,
            defaults=defaults,
        )


def create_model(cls, *, attrs=None, pattern=None, manual=None, defaults=None):
    """Patch datafile attributes on to an existing dataclass."""
    log.debug(f'Converting {cls} to a datafile model')

    if not dataclasses.is_dataclass(cls):
        raise ValueError(f'{cls} must be a dataclass')

    # Patch Meta

    m = getattr(cls, 'Meta', ModelMeta())
    if attrs is not None:
        m.datafile_attrs = attrs
    if pattern is not None:
        m.datafile_pattern = pattern
    if manual is not None:
        m.datafile_manual = manual
    if defaults is not None:
        m.datafile_defaults = defaults
    cls.Meta = m

    # Patch datafile

    cls.datafile = property(Model._get_datafile)

    # Patch __init__

    init = cls.__init__

    def modified_init(self, *args, **kwargs):
        backup = self.datafile.manual
        self.datafile.manual = True
        init(self, *args, **kwargs)
        self.datafile.manual = backup
        Model.__post_init__(self)

    cls.__init__ = modified_init
    cls.__init__.__doc__ = init.__doc__

    return cls
