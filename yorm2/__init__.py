__version__ = "0.1.0"

from . import fields

import dataclasses, inspect

import log


class Manager:
    def __init__(self, synchronized_object, path_pattern):
        self._object = synchronized_object
        self._pattern = path_pattern

    @property
    def fields(self):
        mapped_fields = {}
        for data_field in dataclasses.fields(self._object):
            print(data_field)
            if issubclass(data_field.type, fields.Field):
                mapped_fields[data_field.name] = data_field.type
        return mapped_fields

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
        return Manager(self, self.Meta.path)
