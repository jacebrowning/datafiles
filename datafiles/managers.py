"""Defines object-relational mapping (ORM) methods to manipulate models."""

from __future__ import annotations

import dataclasses
from typing import Optional
from typing_extensions import Protocol

from .mappers import Mapper


Trilean = Optional[bool]
Missing = dataclasses._MISSING_TYPE


class HasDatafile(Protocol):

    datafile: Mapper


class Manager:
    def __init__(self, cls):
        self.model = cls

    def all(self):
        raise NotImplementedError

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
