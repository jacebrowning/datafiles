"""Tests that represent usage as an ORM."""

import platform
from typing import List, Optional

import pytest

from datafiles import datafile
from datafiles.utils import logbreak, write

from . import xfail_with_pep_563
from .samples import SampleWithNestingAndOptionals


# This model is based on the example dataclass from:
# https://docs.python.org/3/library/dataclasses.html
@datafile("../tmp/inventory/{self.pk}.yml")
class InventoryItem:
    pk: int
    name: str
    unit_price: float
    quantity_on_hand: int = 0

    def total_cost(self) -> float:
        return self.unit_price * self.quantity_on_hand


def test_multiple_instances_are_distinct(expect):
    item_1 = InventoryItem.objects.get_or_create(1, "Nuts", 0.23)
    item_2 = InventoryItem.objects.get_or_create(2, "Bolts", 0.45, quantity_on_hand=100)

    expect(item_1.datafile.data) == {"name": "Nuts", "unit_price": 0.23}
    expect(item_2.datafile.data) == {
        "name": "Bolts",
        "unit_price": 0.45,
        "quantity_on_hand": 100,
    }

    item_1.quantity_on_hand = 200
    item_2.unit_price = 0.34

    expect(item_1.datafile.data) == {
        "name": "Nuts",
        "unit_price": 0.23,
        "quantity_on_hand": 200,
    }
    expect(item_2.datafile.data) == {
        "name": "Bolts",
        "unit_price": 0.34,
        "quantity_on_hand": 100,
    }


@xfail_with_pep_563
def test_classes_can_share_a_nested_dataclass(expect):
    @datafile
    class Nested:
        value: int

    @datafile("../tmp/sample.json")
    class Foo:
        nested: Nested

    logbreak("Initialize Foo")
    foo = Foo(Nested(1))

    expect(foo.nested.value) == 1

    @datafile("../tmp/sample.toml")
    class Bar:
        nested: Nested

    logbreak("Initialize Bar")
    bar = Bar(Nested(2))

    expect(bar.nested.value) == 2


@pytest.mark.xfail(reason="https://github.com/jacebrowning/datafiles/issues/147")
def test_values_are_filled_from_disk(expect):
    InventoryItem.objects.get_or_create(42, "Things", 0.99)

    items = list(InventoryItem.objects.all())

    expect(items[0]) == InventoryItem(42, "Things", 0.99)


def test_partial_load_from_disk(expect):
    write(
        "tmp/inventory/42.yml",
        """
        name: Things"
        """,
    )

    items = list(InventoryItem.objects.all())

    expect(items[0].unit_price) == 0
    expect(items[0].quantity_on_hand) == 0


def test_partial_nested_load_from_disk(expect):
    write(
        "tmp/sample.yml",
        """
            name: foo
            score: 7
            nested:
                name: bar
            """,
    )

    items = list(SampleWithNestingAndOptionals.objects.all())

    expect(items[0].nested.name) == "bar"
    expect(items[0].nested.score) == 0.0
    expect(items[0].nested.weight).is_(None)


@xfail_with_pep_563
def test_missing_optional_fields_are_loaded(expect):
    @datafile
    class Name:
        value: str

    @datafile("../tmp/samples/{self.key}.json")
    class Sample:

        key: int
        name: Optional[Name]
        value: float = 0.0

    sample = Sample(42, None)

    logbreak("get key=42")
    sample2 = Sample.objects.get(42)
    expect(sample2.name) == sample.name


def test_comments_in_matched_files(expect):
    @datafile("../tmp/templates/{self.key}/config.yml")
    class LegacyTemplate:
        key: str
        name: str
        link: str
        default: List[str]
        aliases: List[str]

    write(
        "tmp/templates/foo/config.yml",
        """
        link: # placeholder
        default:
          - # placeholder
          - # placeholder
        aliases:
          - # placeholder
        """,
    )
    write(
        "tmp/templates/bar/config.yml",
        """
        link: http://example.com
        default:
          - abc
          - def
        aliases:
          - qux
        """,
    )

    items = list(LegacyTemplate.objects.all())
    expect(len(items)) == 2


def test_paths_in_pattern(expect):
    @datafile("../tmp/routes/{self.path}/{self.variant}.yml")
    class LegacyTemplate:
        path: str
        variant: str
        value: int

    write(
        "tmp/routes/foo/public.yml",
        """
        value: 2
        """,
    )
    write(
        "tmp/routes/foo/bar/public.yml",
        """
        value: 2
        """,
    )
    write(
        "tmp/routes/foo/bar/private.yml",
        """
        value: 2
        """,
    )

    items = list(LegacyTemplate.objects.all())
    expect(len(items)) == 3
    if platform.system() == "Windows":
        expect(items[-1].path) == "foo\\bar"
    else:
        expect(items[-1].path) == "foo/bar"
