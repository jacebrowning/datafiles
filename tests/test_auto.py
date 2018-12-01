# pylint: disable=unused-variable,no-member

from dataclasses import dataclass, field
from typing import List

import log
import pytest

from datafiles import sync


@sync('../tmp/sample.yml')
@dataclass
class Sample:
    item: str = 'a'
    items: List[int] = field(default_factory=lambda: [1])

    # pylint: disable=unsubscriptable-object
    def __getitem__(self, key):
        log.info(f'__getitem__: {key}')
        return self.items[key]

    # pylint: disable=unsupported-assignment-operation
    def __setitem__(self, key, value):
        log.info(f'__setitem__: {key}={value}')
        self.items[key] = value

    # pylint: disable=unsupported-delete-operation
    def __delitem__(self, key):
        log.info(f'__delitem__: {key}')
        del self.items[key]


@sync('../tmp/sample.yml')
@dataclass
class SampleWithIter:
    items: List[int] = field(default_factory=lambda: [1])

    def __iter__(self):
        return iter(self.items)


@dataclass
class NestedSample:
    name: str = 'b'
    score: float = 3.4


@sync('../tmp/sample.yml')
@dataclass
class SampleWithNesting:
    item: int
    nested: NestedSample = field(default_factory=NestedSample)


def describe_automatic_load():
    @pytest.mark.skip
    def with_getattribute(write, expect):
        sample = Sample()

        write(
            'tmp/sample.yml',
            """
            item: b
            """,
        )

        expect(sample.item) == 'b'

    @pytest.mark.skip
    def with_getitem(write, expect):
        sample = Sample()

        write(
            'tmp/sample.yml',
            """
            items: [2]
            """,
        )

        expect(sample[0]) == 2

    @pytest.mark.skip
    def with_iter(write, expect):
        sample = SampleWithIter()

        write(
            'tmp/sample.yml',
            """
            items: [3]
            """,
        )

        expect([x for x in sample]) == [3]


def describe_automatic_save():
    @pytest.mark.skip
    def with_setattr(expect, read, dedent):
        sample = Sample()

        sample.item = 'b'

        expect(read('tmp/sample.yml')) == dedent(
            """
            item: b
            """
        )

    @pytest.mark.skip
    def with_setitem(expect, read, dedent):
        sample = Sample()

        sample[0] = 2

        expect(read('tmp/sample.yml')) == dedent(
            """
            items:
            - 2
            """
        )

    @pytest.mark.skip
    def with_delitem(expect, read, dedent):
        sample = Sample()

        del sample[0]

        expect(read('tmp/sample.yml')) == dedent(
            """
            items: []
            """
        )


def describe_automatic_load_with_nesting():
    @pytest.mark.skip
    def with_getattr(write, expect):
        sample = SampleWithNesting(1)

        log.info("Modifying nested file")
        write(
            'tmp/sample.yml',
            """
            item: 1
            nested:
              name: c
            """,
        )

        expect(sample.nested.name) == 'c'
        expect(sample.nested.score) == 3.4


def describe_automatic_save_with_nesting():
    @pytest.mark.skip
    def with_setattr(expect, read, dedent):
        sample = SampleWithNesting(2)

        log.info("Modifying nested object")
        sample.nested.name = 'd'

        expect(read('tmp/sample.yml')) == dedent(
            """
            item: 2
            nested:
              name: d
            """
        )


def describe_automatic_load_before_save():
    @pytest.mark.skip
    def with_setattr(write, expect, dedent):
        sample = Sample()

        write(
            'tmp/sample.yml',
            """
            item: b  # Comment
            """,
        )

        sample.item = 'c'

        expect(sample.datafile.text) == dedent(
            """
        item: c  # Comment
        """
        )
