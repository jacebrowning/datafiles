# pylint: disable=no-self-argument,protected-access,attribute-defined-outside-init

import dataclasses
from dataclasses import dataclass
from typing import Dict, Optional

import log
from classproperties import classproperty

from .converters import Converter, map_type
from .hooks import patch_methods
from .managers import InstanceManager, ModelManager


@dataclass
class ModelMeta:
    datafile_attrs: Optional[Dict[str, Converter]] = None
    datafile_pattern: Optional[str] = None

    datafile_manual: bool = False
    datafile_defaults: bool = False

    datafile_root: Optional[InstanceManager] = None


class Model:

    Meta: ModelMeta

    def __post_init__(self):
        log.debug(f'Initializing {self.__class__} instance')


        self.datafile = get_datafile(self)

        path = self.datafile.path
        exists = self.datafile.exists
        automatic = not self.datafile.manual

        if self.datafile.nested:
            log.debug(f'Initializing nested {self.__class__} instance')
        else:
            log.debug(f'Initializing {self.__class__} instance')
            log.debug(f'Datafile path: {path}')
            log.debug(f'Datafile exists: {exists}')

            if exists:
                self.datafile.load(first_load=True)
            elif path:
                self.datafile.save()

        if automatic:
            patch_methods(self)

        if self.datafile.nested:
            log.debug(f'Initialized nested {self.__class__} instance')
        else:
            log.debug(f'Initialized {self.__class__} instance')

    @classproperty
    def datafiles(cls) -> ModelManager:
        return ModelManager(cls)


def get_datafile(obj, root=None) -> InstanceManager:
    m = getattr(obj, 'Meta', None)
    pattern = getattr(m, 'datafile_pattern', None)
    attrs = getattr(m, 'datafile_attrs', None)
    manual = getattr(m, 'datafile_manual', False)
    defaults = getattr(m, 'datafile_defaults', False)

    if attrs is None:
        attrs = {}
        log.debug(f'Mapping attributes for {obj.__class__} instance')
        for field in dataclasses.fields(obj):
            self_name = f'self.{field.name}'
            if pattern is None or self_name not in pattern:
                attrs[field.name] = map_type(
                    field.type,
                    create_model=create_model,
                    manual=manual,
                    defaults=defaults,
                )

    return InstanceManager(
        self,
        attrs=attrs,
        pattern=pattern,
        manual=manual,
        defaults=defaults,
        root=root,
    )


def create_model(
    cls, *, attrs=None, pattern=None, manual=False, defaults=False
):
    """Patch datafile attributes on to an existing dataclass."""

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
