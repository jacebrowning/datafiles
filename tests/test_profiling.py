"""Tests used to profile the library."""

from dataclasses import dataclass, field
from typing import List, Optional

from datafiles import datafile
from datafiles.utils import logbreak


def get_sample():
    @dataclass
    class Item:

        required: int
        optional: Optional[int]
        default: int = 42

    @datafile('../tmp/{self.key}.yml', defaults=True)
    class Sample:

        key: str

        item_required: Item
        item_optional: Optional[Item]
        items_required: List[Item]
        item_default: Item = Item(1, None)
        items_default: List[Item] = field(default_factory=list)

    return Sample('profiling', Item(2, None), None, [Item(3, None)])


def test_init():
    get_sample()


def test_load():
    sample = get_sample()
    logbreak("Loading")
    sample.datafile.load()  # pylint: disable=no-member


def test_save():
    sample = get_sample()
    logbreak("Saving")
    sample.datafile.save()  # pylint: disable=no-member
