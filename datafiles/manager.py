"""Defines object-relational mapping (ORM) methods to manipulate models."""

from __future__ import annotations

import dataclasses
from glob import iglob
from typing import TYPE_CHECKING, Iterator, Optional
from typing_extensions import Protocol

import log
from parse import parse


if TYPE_CHECKING:
    from .mapper import Mapper


Trilean = Optional[bool]
Missing = dataclasses._MISSING_TYPE


class Manager:
    def __init__(self, cls):
        self.model = cls

    def all(self) -> Iterator[HasDatafile]:
        pattern = self.model.Meta.datafile_pattern
        splatted = pattern.format(self=Splats())
        log.info(f'Finding files matching pattern: {splatted}')
        for filename in iglob(splatted):
            log.debug(f'Found matching path: {filename}')
            results = parse(pattern, filename)
            args = list(results.named.values())
            for _ in range(9):
                try:
                    yield self.model(*args)
                except TypeError:
                    args.append(Missing)
                else:
                    break

    def get_or_none(self, *args, **kwargs) -> Optional[HasDatafile]:
        original_manual = self.model.Meta.datafile_manual

        self.model.Meta.datafile_manual = True
        instance = self.model(*args, **kwargs)
        self.model.Meta.datafile_manual = original_manual

        if instance.datafile.exists:
            instance.datafile._manual = original_manual
            return instance

        return None

    def get_or_create(self, *args, **kwargs) -> HasDatafile:
        instance = self.model(*args, **kwargs)

        if not instance.datafile.exists:
            instance.datafile.save()

        return instance

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
