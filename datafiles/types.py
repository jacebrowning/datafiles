import dataclasses
from typing import Optional

Trilean = Optional[bool]
Missing = dataclasses._MISSING_TYPE


class List(list):
    """Patchable `list` type."""

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_list(node)


class Dict(dict):
    """Patchable `dict` type."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            return super().__getattribute__(name)

    def __setattr__(self, name, value):
        if name == "datafile":
            super().__setattr__(name, value)
        else:
            self[name] = value

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_dict(node)
