import dataclasses
from typing import Dict, Optional

from classproperties import classproperty

from .fields import Field, map_type
from .managers import InstanceManager, ModelManager


@dataclasses.dataclass
class ModelMeta:
    datafile_pattern: Optional[str] = None
    datafile_fields: Optional[Dict[str, Field]] = None


class Model:

    Meta: ModelMeta

    @classproperty
    def datafiles(cls) -> ModelManager:  # pylint: disable=no-self-argument
        return ModelManager(cls)

    @property
    def datafile(self) -> InstanceManager:
        return self.get_datafile()

    def get_datafile(self) -> InstanceManager:
        meta = getattr(self, 'Meta', None)

        pattern = getattr(meta, 'datafile_pattern', None)

        fields = getattr(meta, 'datafile_fields', None)
        if fields is None:
            fields = {}
            for f in dataclasses.fields(self):
                self_name = f'self.{f.name}'
                if pattern is None or self_name not in pattern:
                    fields[f.name] = map_type(f.type)

        return InstanceManager(instance=self, pattern=pattern, fields=fields)
