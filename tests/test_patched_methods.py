"""Tests for automatic saving and loading through patched methods."""

# pylint: disable=unused-variable

from dataclasses import dataclass, field
from typing import Dict, List

from datafiles import datafile
from datafiles.utils import dedent, logbreak, read, write


@datafile("../tmp/sample.yml")
class Sample:
    item: str = "a"
    items: List[int] = field(default_factory=lambda: [1])
    data: Dict[str, int] = field(default_factory=lambda: {"a": 1})


@dataclass
class Nested:
    name: str = "b"
    score: float = 3.4
    items: List[int] = field(default_factory=list)


@datafile("../tmp/sample.yml")
class SampleWithNesting:
    item: int
    nested: Nested = field(default_factory=Nested)


def describe_automatic_load():
    def with_getattribute(expect):
        sample = Sample()

        write(
            "tmp/sample.yml",
            """
            item: b
            """,
        )

        logbreak("Getting attribute")
        expect(sample.item) == "b"


def describe_automatic_save():
    def with_setattr(expect):
        sample = Sample()

        logbreak("Setting attribute")
        sample.item = "b"

        expect(read("tmp/sample.yml")) == dedent(
            """
            item: b
            """
        )

    def with_setattr_on_nested_dataclass(expect):
        sample = SampleWithNesting(2)

        logbreak("Setting nested attribute")
        sample.nested.name = "d"

        logbreak("Reading file")
        expect(read("tmp/sample.yml")) == dedent(
            """
            item: 2
            nested:
              name: d
            """
        )

    def with_setitem(expect):
        sample = Sample()

        sample.items[0] = 2

        expect(read("tmp/sample.yml")) == dedent(
            """
            items:
              - 2
            """
        )

    def with_delitem(expect):
        sample = Sample()

        del sample.items[0]

        expect(read("tmp/sample.yml")) == dedent(
            """
            items:
              -
            """
        )

    def with_append(expect):
        sample = Sample()

        logbreak("Appending to list: 2")
        sample.items.append(2)

        expect(read("tmp/sample.yml")) == dedent(
            """
            items:
              - 1
              - 2
            """
        )

        sample.datafile.load()

        logbreak("Appending to list: 3")
        sample.items.append(3)

        expect(read("tmp/sample.yml")) == dedent(
            """
            items:
              - 1
              - 2
              - 3
            """
        )

    def with_append_on_nested_dataclass(expect):
        sample = SampleWithNesting(1)

        logbreak("Appending to nested list: 2")
        sample.nested.items.append(2)

        expect(read("tmp/sample.yml")) == dedent(
            """
            item: 1
            nested:
              items:
                - 2
            """
        )

        logbreak("Appending to nested list: 3")
        sample.nested.items.append(3)

        expect(read("tmp/sample.yml")) == dedent(
            """
            item: 1
            nested:
              items:
                - 2
                - 3
            """
        )

    def with_update(expect):
        sample = Sample()

        logbreak()
        sample.data.update({"b": 2})

        expect(read("tmp/sample.yml")) == dedent(
            """
            data:
              a: 1
              b: 2
            """
        )

        sample.datafile.load()

        logbreak()
        sample.data.update({"c": 3})

        expect(read("tmp/sample.yml")) == dedent(
            """
            data:
              a: 1
              b: 2
              c: 3
            """
        )


def describe_automatic_load_before_save():
    def with_setattr(expect):
        sample = Sample()

        write(
            "tmp/sample.yml",
            """
            item: 42
            """,
        )

        expect(sample.item) == "42"

        expect(sample.datafile.text) == dedent(
            """
            item: '42'
            """
        )


def describe_automatic_load_after_save():
    def with_setattr(expect):
        sample = Sample()

        sample.item = 42  # type: ignore

        expect(sample.datafile.text) == dedent(
            """
            item: '42'
            """
        )

        expect(sample.item) == "42"
