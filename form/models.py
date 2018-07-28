import dataclasses
from typing import Dict, Optional

from . import fields
from .managers import Manager


@dataclasses.dataclass
class Metadata:
    form_path: Optional[str] = None
    form_fields: Optional[Dict[str, fields.Field]] = None


class Model:

    meta: Metadata

    @property
    def form(self) -> Manager:
        return self.get_form()

    def get_form(self) -> Manager:
        meta = getattr(self, 'Meta', Metadata())

        path_pattern = getattr(meta, 'form_path', None)

        mapped_fields = getattr(meta, 'form_fields', None)
        if mapped_fields is None:
            mapped_fields = {}
            for f in dataclasses.fields(self):
                self_name = f'self.{f.name}'
                if self_name not in path_pattern:
                    mapped_fields[f.name] = fields.map_type(f.type)

        return Manager(self, path_pattern, mapped_fields)
