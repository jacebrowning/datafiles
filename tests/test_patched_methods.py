"""Tests for automatic saving and loading through patched methods."""

# pylint: disable=unused-variable

from dataclasses import dataclass, field
from typing import Dict, List

import pytest

from datafiles import datafile


@datafile('../tmp/sample.yml')
class Sample:
    item: str = 'a'
    items: List[int] = field(default_factory=lambda: [1])
    data: Dict[str, int] = field(default_factory=lambda: {'a': 1})


@dataclass
class Nested:
    name: str = 'b'
    score: float = 3.4
    items: List[int] = field(default_factory=list)


@datafile('../tmp/sample.yml')
class SampleWithNesting:
    item: int
    nested: Nested = field(default_factory=Nested)


def describe_automatic_load():
    @pytest.mark.flaky
    def with_getattribute(logbreak, write, expect):
        sample = Sample()

        write(
            'tmp/sample.yml',
            """
            item: b
            """,
        )

        logbreak("Getting attribute")
        expect(sample.item) == 'b'


def describe_automatic_save():
    @pytest.mark.flaky
    def with_setattr(logbreak, expect, read, dedent):
        sample = Sample()

        logbreak("Setting attribute")
        sample.item = 'b'

        expect(read('tmp/sample.yml')) == dedent(
            """
            item: b
            """
        )

    def with_setattr_on_nested_dataclass(logbreak, expect, read, dedent):
        sample = SampleWithNesting(2)

        logbreak("Setting nested attribute")
        sample.nested.name = 'd'

        logbreak("Reading file")
        expect(read('tmp/sample.yml')) == dedent(
            """
            item: 2
            nested:
              name: d
            """
        )

    def with_setitem(expect, read, dedent):
        sample = Sample()

        sample.items[0] = 2

        expect(read('tmp/sample.yml')) == dedent(
            """
            items:
            - 2
            """
        )

    def with_delitem(expect, read):
        sample = Sample()

        del sample.items[0]

        expect(read('tmp/sample.yml')) == "items:\n- \n"

    def with_append(logbreak, expect, read, dedent):
        sample = Sample()

        logbreak("Appending to list")
        sample.items.append(2)

        expect(read('tmp/sample.yml')) == dedent(
            """
            items:
            - 1
            - 2
            """
        )

        sample.datafile.load()

        logbreak("Appending to list")
        sample.items.append(3)

        expect(read('tmp/sample.yml')) == dedent(
            """
            items:
            - 1
            - 2
            - 3
            """
        )

    def with_append_on_nested_dataclass(logbreak, expect, read, dedent):
        sample = SampleWithNesting(1)

        logbreak("Appending to nested list")
        sample.nested.items.append(2)

        expect(read('tmp/sample.yml')) == dedent(
            """
            item: 1
            nested:
              items:
              - 2
            """
        )

        logbreak("Appending to nested list")
        sample.nested.items.append(3)

        expect(read('tmp/sample.yml')) == dedent(
            """
            item: 1
            nested:
              items:
              - 2
              - 3
            """
        )

    def with_update(logbreak, expect, read, dedent):
        sample = Sample()

        logbreak()
        sample.data.update({'b': 2})

        expect(read('tmp/sample.yml')) == dedent(
            """
            data:
              a: 1
              b: 2
            """
        )

        sample.datafile.load()

        logbreak()
        sample.data.update({'c': 3})

        expect(read('tmp/sample.yml')) == dedent(
            """
            data:
              a: 1
              b: 2
              c: 3
            """
        )


def describe_automatic_load_before_save():
    @pytest.mark.flaky
    def with_setattr(write, expect, dedent):
        sample = Sample()

        write(
            'tmp/sample.yml',
            """
            item: 42
            """,
        )

        expect(sample.item) == '42'

        expect(sample.datafile.text) == dedent(
            """
            item: '42'
            """
        )


def describe_automatic_load_after_save():
    def with_setattr(expect, dedent):
        sample = Sample()

        sample.item = 42

        expect(sample.datafile.text) == dedent(
            """
            item: '42'
            """
        )

        expect(sample.item) == '42'
