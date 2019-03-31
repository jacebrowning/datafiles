import dataclasses

import log

from .converters import map_type
from .managers import Datafile
from .meta import ModelMeta


def build_datafile(obj, root=None) -> Datafile:
    try:
        return object.__getattribute__(obj, 'datafile')
    except AttributeError:
        log.debug(f"Building 'datafile' for {obj.__class__} object")

    m = getattr(obj, 'Meta', None)
    pattern = getattr(m, 'datafile_pattern', None)
    attrs = getattr(m, 'datafile_attrs', None)
    manual = getattr(m, 'datafile_manual', ModelMeta.datafile_manual)
    defaults = getattr(m, 'datafile_defaults', ModelMeta.datafile_defaults)
    auto_load = getattr(m, 'datafile_auto_load', ModelMeta.datafile_auto_load)
    auto_save = getattr(m, 'datafile_auto_save', ModelMeta.datafile_auto_save)
    auto_attr = getattr(m, 'datafile_auto_attr', ModelMeta.datafile_auto_attr)

    if attrs is None and dataclasses.is_dataclass(obj):
        attrs = {}
        log.debug(f'Mapping attributes for {obj.__class__} object')
        for field in dataclasses.fields(obj):
            self_name = f'self.{field.name}'
            if pattern is None or self_name not in pattern:
                attrs[field.name] = map_type(field.type, name=field.name)

    return Datafile(
        obj,
        attrs=attrs,
        pattern=pattern,
        manual=manual,
        defaults=defaults,
        auto_load=auto_load,
        auto_save=auto_save,
        auto_attr=auto_attr,
        root=root,
    )
