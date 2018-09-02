# pylint: disable=unused-variable

from dataclasses import dataclass

import pytest

from datafiles import sync


@pytest.fixture
def SampleWithDefaults():
    @sync('../tmp/sample.yml')
    @dataclass
    class Sample:
        foo: int = 1
        bar: str = 'a'

    return Sample


def describe_existing_file():
    def it_wins_when_no_init_values(write, SampleWithDefaults, expect):
        write(
            'tmp/sample.yml',
            """
            foo: 2
            bar: 'b'
            """,
        )

        sample = SampleWithDefaults()

        expect(sample.foo) == 2
        expect(sample.bar) == 'b'

    def it_loses_against_init_values(write, SampleWithDefaults, expect):
        write(
            'tmp/sample.yml',
            """
            foo: 3
            bar: 'c'
            """,
        )

        sample = SampleWithDefaults(4, 'd')

        expect(sample.foo) == 4
        expect(sample.bar) == 'd'
