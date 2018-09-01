# pylint: disable=unused-variable

from dataclasses import dataclass

import pytest

from datafiles import sync


@pytest.fixture
def SampleWithDefaults():
    @sync('../tmp/sample.yml')
    @dataclass
    class Sample:
        foo: int = 123
        bar: str = 'abc'

    return Sample


def describe_existing_file():
    def it_wins_when_no_values_specified(write, SampleWithDefaults, expect):
        write(
            'tmp/sample.yml',
            """
            foo: 456
            bar: 'def'
            """,
        )

        sample = SampleWithDefaults()

        expect(sample.foo) == 456
        expect(sample.bar) == 'def'
