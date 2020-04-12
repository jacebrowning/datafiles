import dataclasses
from typing import Optional


Trilean = Optional[bool]
Missing = dataclasses._MISSING_TYPE


class List(list):
    """Patchable `list` type."""


class Dict(dict):
    """Patchable `dict` type."""
