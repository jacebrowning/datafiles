# pylint: disable=unused-variable,no-member

from dataclasses import dataclass, field
from typing import Dict, List

import log

from datafiles import datafile


@datafile('../tmp/sample.yml')
class Sample:
    item: str = 'a'
    items: List[int] = field(default_factory=lambda: [1])
    data: Dict[str, int] = field(default_factory=lambda: {'a': 1})

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


@datafile('../tmp/sample.yml')
class SampleWithIter:
    items: List[int] = field(default_factory=lambda: [1])

    def __iter__(self):
        return iter(self.items)


@dataclass
class NestedSample:
    name: str = 'b'
    score: float = 3.4
    items: List[int] = field(default_factory=list)


@datafile('../tmp/sample.yml')
class SampleWithNesting:
    item: int
    nested: NestedSample = field(default_factory=NestedSample)


def describe_automatic_load():
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

    def with_getitem(logbreak, write, expect):
        sample = Sample()

        logbreak()
        write(
            'tmp/sample.yml',
            """
            items: [2]
            """,
        )

        expect(sample[0]) == 2

    def with_iter(write, expect):
        sample = SampleWithIter()

        write(
            'tmp/sample.yml',
            """
            items: [3]
            """,
        )

        expect([x for x in sample]) == [3]

    def describe_nesting():
        def with_getattr(logbreak, write, expect):
            sample = SampleWithNesting(1)

            logbreak("Modifying nested file")
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


def describe_automatic_save():
    def with_setattr(logbreak, expect, read, dedent):
        sample = Sample()

        logbreak()
        sample.item = 'b'

        expect(read('tmp/sample.yml')) == dedent(
            """
            item: b
            """
        )

    def with_setattr_on_nested_dataclass(logbreak, expect, read, dedent):
        sample = SampleWithNesting(2)

        logbreak()
        sample.nested.name = 'd'
        logbreak()

        expect(read('tmp/sample.yml')) == dedent(
            """
            item: 2
            nested:
              name: d
            """
        )

    def with_setitem(expect, read, dedent):
        sample = Sample()

        sample[0] = 2

        expect(read('tmp/sample.yml')) == dedent(
            """
            items:
            - 2
            """
        )

    def with_delitem(expect, read, dedent):
        sample = Sample()

        del sample[0]

        expect(read('tmp/sample.yml')) == dedent(
            """
            items: []
            """
        )

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
