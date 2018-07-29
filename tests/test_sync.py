# pylint: disable=unused-variable

from dataclasses import dataclass

import pytest

from datafiles import sync
from datafiles.fields import String


@pytest.fixture
def sample():
    """A decorated data class with a single key."""

    @sync('tmp/{self.key}.yml')
    @dataclass
    class Sample:
        key: int
        name: str

    return Sample(42, "foobar")


def describe_sync():
    def it_populates_metadata(expect, sample):
        expect(sample.datafile.fields) == {'name': String}
        expect(sample.datafile.path) == 'tmp/42.yml'
        expect(sample.datafile.data) == {'name': "foobar"}

    def it_requires_dataclasses(expect):
        with expect.raises(ValueError):

            @dataclass
            @sync('tmp/{self.key}.yml')
            class Sample:
                key: int
                name: str
