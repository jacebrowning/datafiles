# pylint: disable=unused-variable

from dataclasses import dataclass, field
from typing import List

import pytest

from datafiles import sync


@sync('../tmp/sample.yml')
@dataclass
class Sample:
    item: str = 'a'
    items: List[int] = field(default_factory=lambda: [1])

    def __getitem__(self, key):
        print('__getitem__')
        return self.items[key]  # pylint: disable=unsubscriptable-object


def describe_automatic_load():
    @pytest.mark.xfail
    def with_getattribute(write, expect):
        sample = Sample()
        assert hasattr(sample.__getattribute__, '_patched')

        write(
            'tmp/sample.yml',
            """
            item: b
            """,
        )

        expect(sample.item) == 'b'

    @pytest.mark.xfail
    def with_getitem(write, expect):
        sample = Sample()
        assert hasattr(sample.__getitem__, '_patched')

        write(
            'tmp/sample.yml',
            """
            items: [2]
            """,
        )

        expect(sample[0]) == 2
