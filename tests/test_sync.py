# pylint: disable=unused-variable

from dataclasses import dataclass

import pytest

import form


@pytest.fixture
def sample():
    """A decorated data class with a single key."""

    @form.sync('tmp/{self.key}.yml')
    @dataclass
    class Sample:
        key: int
        name: str

    return Sample(42, "foobar")


def describe_sync():
    def it_populates_metadata(expect, sample):
        expect(sample.form.fields) == {"name": form.fields.String}
        expect(sample.form.path) == "tmp/42.yml"
        expect(sample.form.data) == {"name": "foobar"}

    def it_requires_dataclasses(expect):
        with expect.raises(ValueError):

            @dataclass
            @form.sync('tmp/{self.key}.yml')
            class Sample:
                key: int
                name: str
