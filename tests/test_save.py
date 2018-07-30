# pylint: disable=unused-variable

from dataclasses import dataclass

import pytest

from datafiles import sync


@pytest.fixture
def Sample():
    """A decorated data class with builtin types"""

    @sync('tmp/sample.yml')
    @dataclass
    class Sample:
        bool_: bool
        int_: int
        float_: float
        str_: str

    return Sample


def describe_save():
    def with_defaults(expect, Sample):
        sample = Sample(None, None, None, None)
        sample.datafile.save()
        with open('tmp/sample.yml') as f:
            expect(
                f.read()
            ) == """bool_: false
int_: 0
float_: 0.0
str_: ''
"""
