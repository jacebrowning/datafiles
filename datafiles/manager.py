"""Defines object-relational mapping (ORM) methods to manipulate models."""

from __future__ import annotations

import dataclasses
import inspect
from glob import iglob
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, Optional
from typing_extensions import Protocol

import log
from parse import parse

from . import hooks


if TYPE_CHECKING:
    from .mapper import Mapper


Trilean = Optional[bool]
Missing = dataclasses._MISSING_TYPE


class Manager:
    def __init__(self, cls):
        self.model = cls

    def all(self) -> Iterator[HasDatafile]:
        root = Path(inspect.getfile(self.model)).parent
        pattern = str(root / self.model.Meta.datafile_pattern)
        splatted = pattern.format(self=Splats())
        log.info(f'Finding files matching pattern: {splatted}')
        for filename in iglob(splatted):
            log.debug(f'Found matching path: {filename}')
            results = parse(pattern, filename)
            yield self.get(*results.named.values())

    def get(self, *args, **kwargs) -> HasDatafile:
        fields = dataclasses.fields(self.model)
        args = list(args)
        args += [Missing] * (len(fields) - len(args) - len(kwargs))

        with hooks.disabled():
            instance = self.model(*args, **kwargs)
            instance.datafile.load()

        return instance

    def get_or_none(self, *args, **kwargs) -> Optional[HasDatafile]:
        try:
            return self.get(*args, **kwargs)
        except FileNotFoundError:
            return None

    def get_or_create(self, *args, **kwargs) -> HasDatafile:
        try:
            return self.get(*args, **kwargs)
        except FileNotFoundError:
            return self.model(*args, **kwargs)

    def filter(self, **query):
        for item in self.all():
            match = True
            for key, value in query.items():
                if getattr(item, key) != value:
                    match = False
            if match:
                yield item


class HasDatafile(Protocol):
    datafile: Mapper


class Splats:
    def __getattr__(self, name):
        return '*'
