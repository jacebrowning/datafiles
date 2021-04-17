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

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_dict(node)
