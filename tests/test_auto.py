# pylint: disable=unused-variable

from dataclasses import dataclass

import pytest

from datafiles import sync


@sync('../tmp/sample.yml')
@dataclass
class Sample:
    value: str


def describe_automatic_load():
    @pytest.mark.xfail
    def with_getattribute(write, expect):
        sample = Sample('a')

        write(
            'tmp/sample.yml',
            """
            value: b
            """,
        )

        assert hasattr(sample.__getattribute__, '_patched')

        expect(sample.value) == 'b'
