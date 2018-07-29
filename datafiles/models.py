import dataclasses
from typing import Dict, Optional

from .fields import Field, map_type
from .managers import Manager


@dataclasses.dataclass
class ModelMeta:
    datafile_pattern: Optional[str] = None
    datafile_fields: Optional[Dict[str, Field]] = None


class Model:

    Meta: ModelMeta

    @property
    def datafile(self) -> Manager:
        return self.get_datafile()

    def get_datafile(self) -> Manager:
        meta = getattr(self, 'Meta', None)

        pattern = getattr(meta, 'datafile_pattern', None)

        fields = getattr(meta, 'datafile_fields', None)
        if fields is None:
            fields = {}
            for f in dataclasses.fields(self):
                self_name = f'self.{f.name}'
                if pattern is None or self_name not in pattern:
                    fields[f.name] = map_type(f.type)

        return Manager(self, pattern, fields)
