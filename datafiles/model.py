import dataclasses

import log
from classproperties import classproperty

from . import config, hooks, settings
from .manager import Manager
from .mapper import Mapper, create_mapper


class Model:

    Meta: config.Meta = config.Meta()
    datafile: Mapper

    def __post_init__(self):
        log.debug(f"Initializing {self.__class__} object")

        # Using object.__setattr__ in case of frozen dataclasses
        object.__setattr__(self, "datafile", create_mapper(self))

        if settings.HOOKS_ENABLED:
            with hooks.disabled():

                path = self.datafile.path
                exists = self.datafile.exists
                create = not self.datafile.manual

                if path:
                    log.debug(f"Datafile path: {path}")
                    log.debug(f"Datafile exists: {exists}")

                    if exists:
                        self.datafile.load(_first_load=True)
                    elif path and create:
                        self.datafile.save()

                    hooks.apply(self, self.datafile)

        log.debug(f"Initialized {self.__class__} object")

    @classproperty
    def objects(cls) -> Manager:  # pylint: disable=no-self-argument
        return Manager(cls)


def create_model(
    cls, *, attrs=None, manual=None, pattern=None, defaults=None, infer=None
):
    """Patch model attributes on to an existing dataclass."""
    log.debug(f"Converting {cls} to a datafile model")

    if not dataclasses.is_dataclass(cls):
        raise ValueError(f"{cls} must be a dataclass")

    # Patch meta

    meta = getattr(cls, "Meta", config.Meta())

    if attrs is not None:
        meta.datafile_attrs = attrs
    if pattern is not None:
        meta.datafile_pattern = pattern

    if not hasattr(cls, "Meta") and manual is not None:
        meta.datafile_manual = manual
    if not hasattr(cls, "Meta") and defaults is not None:
        meta.datafile_defaults = defaults
    if not hasattr(cls, "Meta") and infer is not None:
        meta.datafile_infer = infer

    cls.Meta = meta

    # Patch manager

    cls.objects = Manager(cls)

    # Patch __init__

    init = cls.__init__

    def modified_init(self, *args, **kwargs):
        with hooks.disabled():
            init(self, *args, **kwargs)
        Model.__post_init__(self)

    cls.__init__ = modified_init
    cls.__init__.__doc__ = init.__doc__

    return cls
