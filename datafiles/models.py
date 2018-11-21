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
    datafile_pattern: Optional[str] = None
    datafile_attrs: Optional[Dict[str, Converter]] = None


class Model:

    Meta: ModelMeta

    def __post_init__(self):
        path = self.datafile.path
        exists = self.datafile.exists
        nested = bool(self.datafile._root_instance)
        automatic = not self.datafile.manual

        if nested:
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

        if nested:
            log.debug(f'Initialized nested {self.__class__} instance')
        else:
            log.debug(f'Initialized {self.__class__} instance')

    @classproperty
    def datafiles(cls) -> ModelManager:
        return ModelManager(cls)

    @property
    def datafile(self) -> InstanceManager:
        return self._get_datafile()

    @cached(cache={}, key=id)
    def _get_datafile(self) -> InstanceManager:
        # TODO: Maybe these attributes should be enforced?
        m = getattr(self, 'Meta', None)
        pattern = getattr(m, 'datafile_pattern', None)
        attrs = getattr(m, 'datafile_attrs', None)
        manual = getattr(m, 'datafile_manual', False)
        defaults = getattr(m, 'datafile_defaults', False)
        root = getattr(m, 'datafile_root', None)

        if attrs is None:
            attrs = {}
            for field in dataclasses.fields(self):
                self_name = f'self.{field.name}'
                if pattern is None or self_name not in pattern:
                    attrs[field.name] = map_type(
                        field.type,
                        create_model=create_model,
                        manual=manual,
                        defaults=defaults,
                        root=self,
                    )

        return InstanceManager(
            self, pattern, attrs, manual=manual, defaults=defaults, root=root
        )


def create_model(
    cls, *, pattern=None, attrs=None, manual=False, defaults=False, root=None
):
    """Patch datafile attributes on to an existing dataclass."""

    if not dataclasses.is_dataclass(cls):
        raise ValueError(f'{cls} must be a dataclass')

    # Patch Meta

    m = getattr(cls, 'Meta', ModelMeta())
    m.datafile_pattern = getattr(m, 'datafile_pattern', None) or pattern
    m.datafile_attrs = getattr(m, 'datafile_attrs', None) or attrs
    m.datafile_manual = getattr(m, 'datafile_manual', manual)
    m.datafile_defaults = getattr(m, 'datafile_defaults', defaults)
    m.datafile_root = root
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
