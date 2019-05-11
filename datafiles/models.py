import dataclasses

import log
from classproperties import classproperty

from . import hooks
from .builders import build_datafile
from .managers import Manager
from .meta import ModelMeta


class Model:

    Meta: ModelMeta = ModelMeta()

    def __post_init__(self):
        with hooks.disabled():
            log.debug(f'Initializing {self.__class__} object')

            self.datafile = build_datafile(self)

            path = self.datafile.path
            exists = self.datafile.exists
            create = not self.datafile.manual

            if path:
                log.debug(f'Datafile path: {path}')
                log.debug(f'Datafile exists: {exists}')

                if exists:
                    self.datafile.load(_first=True)
                elif path and create:
                    self.datafile.save()

                hooks.apply(self, self.datafile)

        log.debug(f'Initialized {self.__class__} object')

    @classproperty
    def datafiles(cls) -> Manager:  # pylint: disable=no-self-argument
        return Manager(cls)


def create_model(
    cls,
    *,
    attrs=None,
    manual=None,
    pattern=None,
    defaults=None,
    auto_load=None,
    auto_save=None,
    auto_attr=None,
):
    """Patch datafile attributes on to an existing dataclass."""
    log.debug(f'Converting {cls} to a datafile model')

    if not dataclasses.is_dataclass(cls):
        raise ValueError(f'{cls} must be a dataclass')

    # Patch meta

    m = getattr(cls, 'Meta', ModelMeta())

    if attrs is not None:
        m.datafile_attrs = attrs
    if pattern is not None:
        m.datafile_pattern = pattern

    if not hasattr(cls, 'Meta') and manual is not None:
        m.datafile_manual = manual
    if not hasattr(cls, 'Meta') and defaults is not None:
        m.datafile_defaults = defaults
    if not hasattr(cls, 'Meta') and auto_load is not None:
        m.datafile_auto_load = auto_load
    if not hasattr(cls, 'Meta') and auto_save is not None:
        m.datafile_auto_save = auto_save
    if not hasattr(cls, 'Meta') and auto_attr is not None:
        m.datafile_auto_attr = auto_attr

    cls.Meta = m

    # Patch manager

    cls.datafiles = Manager(cls)

    # Patch __init__

    init = cls.__init__

    def modified_init(self, *args, **kwargs):
        with hooks.disabled():
            init(self, *args, **kwargs)
        Model.__post_init__(self)

    cls.__init__ = modified_init
    cls.__init__.__doc__ = init.__doc__

    return cls
