"""Tests that represent usage as an ORM."""

import platform
from typing import List, Optional

import pytest

from datafiles import datafile
from datafiles.utils import logbreak, write

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


@pytest.mark.parametrize("method", ["all", "filter"])
def test_pattern_fields_can_be_declared_in_reverse_order(expect, tmp_path, method):
    @datafile(str(tmp_path / "{self.environment}" / "{self.name}.yml"))
    class Server:
        name: str
        environment: str
        value: int = 0

    path = tmp_path / "dev" / "server.yml"
    path.parent.mkdir()
    path.write_text("value: 7\n")

    query = {"environment": "dev"} if method == "filter" else {}
    items = list(getattr(Server.objects, method)(**query))

    expect(len(items)) == 1
    expect((items[0].name, items[0].environment, items[0].value)) == (
        "server",
        "dev",
        7,
    )
    expect(items[0].datafile.path) == path
    expect(path.read_text()) == "value: 7\n"


@pytest.mark.parametrize("method", ["all", "filter"])
def test_pattern_fields_can_follow_other_fields(expect, tmp_path, method):
    @datafile(str(tmp_path / "{self.environment}" / "{self.name}.yml"))
    class Server:
        value: int
        environment: str
        name: str

    path = tmp_path / "dev" / "server.yml"
    path.parent.mkdir()
    path.write_text("value: 7\n")

    query = {"value": 7} if method == "filter" else {}
    items = list(getattr(Server.objects, method)(**query))

    expect(len(items)) == 1
    expect((items[0].name, items[0].environment, items[0].value)) == (
        "server",
        "dev",
        7,
    )
    expect(path.read_text()) == "value: 7\n"


def test_reversed_pattern_fields_keep_recursive_paths_and_exclusions(expect, tmp_path):
    @datafile(str(tmp_path / "{self.path}" / "{self.name}.yml"))
    class Route:
        name: str
        path: str
        value: int = 0

    for folder, name in [
        ("foo/bar", "public"),
        ("foo/bar", "private"),
        ("skip", "other"),
    ]:
        path = tmp_path / folder / f"{name}.yml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("value: 2\n")

    items = list(Route.objects.all(_exclude="skip"))

    expect(sorted(item.name for item in items)) == ["private", "public"]
    expect({item.path for item in items}) == {
        str(tmp_path.joinpath("foo", "bar").relative_to(tmp_path))
    }
    expect([item.name for item in Route.objects.filter(_exclude="foo")]) == ["other"]
    expect(Route.objects.get("public", items[0].path).name) == "public"
    expect(Route.objects.get(path=items[0].path, name="private").name) == "private"


def test_pattern_fields_keep_defaults_for_alternate_patterns(expect, tmp_path):
    @datafile(str(tmp_path / "{self.prefix}{self.name}.yml"))
    class Item:
        name: str
        prefix: str = ""
        value: int = 0

    path = tmp_path / "x.yml"
    path.write_text("value: 3\n")

    items = list(Item.objects.all())

    expect(len(items)) == 1
    expect((items[0].name, items[0].prefix, items[0].value)) == ("x", "", 3)
    expect(path.read_text()) == "value: 3\n"


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
