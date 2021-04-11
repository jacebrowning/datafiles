"""Defines object-relational mapping (ORM) methods to manipulate models."""

from __future__ import annotations

import dataclasses
import inspect
import os
from glob import iglob
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, Optional

import log
from parse import parse

from . import hooks


if TYPE_CHECKING:
    from .mapper import Mapper
    from .model import Model


Trilean = Optional[bool]
Missing = dataclasses._MISSING_TYPE


class Splats:
    def __getattr__(self, name):
        return '*'


class Manager:
    def __init__(self, cls):
        self.model = cls

    def get(self, *args, **kwargs) -> Model:
        fields = dataclasses.fields(self.model)
        missing_args = [Missing] * (len(fields) - len(args) - len(kwargs))
        args = (*args, *missing_args)

        with hooks.disabled():
            instance = self.model(*args, **kwargs)
            instance.datafile.load()

        return instance

    def get_or_none(self, *args, **kwargs) -> Optional[Model]:
        try:
            return self.get(*args, **kwargs)
        except FileNotFoundError:
            log.info("File not found")
            return None

    def get_or_create(self, *args, **kwargs) -> Model:
        try:
            return self.get(*args, **kwargs)
        except FileNotFoundError:
            log.info(f"File not found, creating '{self.model.__name__}' object")
            instance = self.model(*args, **kwargs)
            instance.datafile.save()
            instance.datafile.load()
            return instance

    def all(self, *, _exclude: str = '') -> Iterator[Model]:
        path = Path(self.model.Meta.datafile_pattern)
        if path.is_absolute():
            log.debug(f"Detected absolute pattern: {path}")
        elif self.model.Meta.datafile_pattern[:2] == './':
            log.debug(f"Detected relative pattern: {path}")
        else:
            try:
                root = Path(inspect.getfile(self.model)).parent
            except TypeError:
                level = log.DEBUG if '__main__' in str(self.model) else log.WARNING
                log.log(level, f'Unable to determine module for {self.model}')
                root = Path.cwd()
            path = root / self.model.Meta.datafile_pattern

        pattern = str(path.resolve())
        splatted = pattern.format(self=Splats()).replace(
            f'{os.sep}*{os.sep}', f'{os.sep}**{os.sep}'
        )

        log.info(f'Finding files matching pattern: {splatted}')
        for index, filename in enumerate(iglob(splatted, recursive=True)):

            log.debug(f'Found matching path {index + 1}: {filename}')
            result = parse(pattern, filename)
            if result:
                values = list(result.named.values())

                if len(values) > 1 and os.sep in values[-1]:
                    parts = values[-1].rsplit(os.sep, 1)
                    values[-2] = values[-2] + os.sep + parts[0]
                    values[-1] = parts[1]

                if _exclude and values[0].startswith(_exclude):
                    log.debug(f'Skipped loading of excluded value: {values[0]}')
                    continue

                yield self.get(*values)

    def filter(self, *, _exclude: str = '', **query):
        for item in self.all(_exclude=_exclude):
            match = True
            for key, value in query.items():
                if getattr(item, key) != value:
                    match = False
            if match:
                yield item
