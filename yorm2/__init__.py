__version__ = "0.1.0"

from . import fields

import dataclasses, inspect

import log


class Manager:
    def __init__(self, synchronized_object, field_mapping, path_pattern):
        self._object = synchronized_object
        self._fields = field_mapping
        self._pattern = path_pattern

    @property
    def fields(self):
        return self._fields

    @property
    def path(self):
        log.debug(f"Formatting path {self._pattern!r} using {self._object!r}")
        return self._pattern.format(self=self._object)

    @property
    def data(self):
        data = dataclasses.asdict(self._object)
        for key in list(data.keys()):
            if key not in self.fields:
                data.pop(key)
        return data


class Model:
    @property
    def form(self):
        fields = {
            k: v
            for k, v in self.Meta.__dict__.items()
            if not k.startswith("_")
        }
        path = fields.pop("path")
        return Manager(self, fields, path)
