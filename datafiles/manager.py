"""Defines object-relational mapping (ORM) methods to manipulate models."""

from __future__ import annotations

import dataclasses
import inspect
import os
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


class HasDatafile(Protocol):
    datafile: Mapper


class Splats:
    def __getattr__(self, name):
        return '*'


class Manager:
    def __init__(self, cls):
        self.model = cls

    def get(self, *args, **kwargs) -> HasDatafile:
        fields = dataclasses.fields(self.model)
        missing_args = [Missing] * (len(fields) - len(args) - len(kwargs))
        args = (*args, *missing_args)

        with hooks.disabled():
            instance = self.model(*args, **kwargs)
            instance.datafile.load()

        return instance

    def get_or_none(self, *args, **kwargs) -> Optional[HasDatafile]:
        try:
            return self.get(*args, **kwargs)
        except FileNotFoundError:
            log.info("File not found")
            return None

    def get_or_create(self, *args, **kwargs) -> HasDatafile:
        try:
            return self.get(*args, **kwargs)
        except FileNotFoundError:
            log.info(f"File not found, creating '{self.model.__name__}' object")
            return self.model(*args, **kwargs)

    def all(self) -> Iterator[HasDatafile]:
        path = Path(self.model.Meta.datafile_pattern)

        if path.is_absolute() or self.model.Meta.datafile_pattern.startswith('./'):
            pattern = str(path.resolve())
        else:
            try:
                root = Path(inspect.getfile(self.model)).parent
            except TypeError:
                level = log.DEBUG if '__main__' in str(self.model) else log.WARNING
                log.log(level, f'Unable to determine module for {self.model}')
                root = Path.cwd()
            pattern = str(root / self.model.Meta.datafile_pattern)

        splatted = pattern.format(self=Splats()).replace(
            f'{os.sep}*{os.sep}', f'{os.sep}**{os.sep}'
        )
        log.info(f'Finding files matching pattern: {splatted}')
        for filename in iglob(splatted, recursive=True):
            log.debug(f'Found matching path: {filename}')
            result = parse(pattern, filename)
            if result:
                values = list(result.named.values())
                if len(values) > 1 and os.sep in values[-1]:
                    parts = values[-1].rsplit(os.sep, 1)
                    values[-2] = values[-2] + os.sep + parts[0]
                    values[-1] = parts[1]
                yield self.get(*values)

    def filter(self, **query):
        for item in self.all():
            match = True
            for key, value in query.items():
                if getattr(item, key) != value:
                    match = False
            if match:
                yield item
