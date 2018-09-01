# pylint: disable=unused-variable

from dataclasses import dataclass
from pathlib import Path

import pytest

import datafiles
from datafiles import sync


def describe_automatic():
    """Tests to create a data file using the decorator."""

    @pytest.fixture
    def sample():
        """A decorated data class with a single key."""

        @sync('../tmp/{self.key}.yml')
        @dataclass
        class Sample:
            key: int
            name: str
            score: float = 1 / 2

        return Sample(1, "a")

    def it_inferrs_fields(expect, sample):
        expect(sample.datafile.fields) == {
            'name': datafiles.fields.String,
            'score': datafiles.fields.Float,
        }

    def it_formats_path_from_pattern(expect, sample):
        root = Path(__file__).parents[1]
        expect(sample.datafile.path) == root / 'tmp' / '1.yml'

    def it_converts_attributes(expect, sample):
        expect(sample.datafile.data) == {'name': "a", 'score': 0.5}

    def it_requires_dataclasses(expect):
        with expect.raises(ValueError):

            @dataclass
            @sync('tmp/{self.key}.yml')
            class Sample:
                key: int
                name: str


def describe_manual():
    """Tests to create a data file using the model class."""

    @pytest.fixture
    def sample():
        @dataclass
        class Sample(datafiles.Model):
            key: int
            name: str
            score: float = 1 / 4

        return Sample(2, "b")

    def it_inferrs_fields(expect, sample):
        expect(sample.datafile.fields) == {
            'key': datafiles.fields.Integer,
            'name': datafiles.fields.String,
            'score': datafiles.fields.Float,
        }

    def it_has_no_path(expect, sample):
        expect(sample.datafile.path) == None

    def it_converts_attributes(expect, sample):
        expect(sample.datafile.data) == {'key': 2, 'name': "b", 'score': 0.25}


def describe_manual_with_fields():
    """Tests to create a data file with explicit fields."""

    @pytest.fixture
    def sample():
        @dataclass
        class Sample(datafiles.Model):
            key: int
            name: str
            score: float = 1 / 8

            class Meta:
                datafile_fields = {'name': datafiles.fields.String}

        return Sample(3, "c")

    def it_uses_fields_from_meta(expect, sample):
        expect(sample.datafile.fields) == {'name': datafiles.fields.String}

    def it_has_no_path(expect, sample):
        expect(sample.datafile.path) == None

    def it_converts_attributes(expect, sample):
        expect(sample.datafile.data) == {'name': "c"}


def describe_manual_with_fields_and_pattern():
    """Tests to create a data file with explicit fields and pattern."""

    @pytest.fixture
    def sample():
        @dataclass
        class Sample(datafiles.Model):
            key: int
            name: str
            score: float = 1 / 16

            class Meta:
                datafile_fields = {'name': datafiles.fields.String}
                datafile_pattern = '../tmp/{self.key}.yml'

        return Sample(4, "d")

    def it_uses_fields_from_meta(expect, sample):
        expect(sample.datafile.fields) == {'name': datafiles.fields.String}

    def it_formats_path_from_pattern(expect, sample):
        root = Path(__file__).parents[1]
        expect(sample.datafile.path) == root / 'tmp' / '4.yml'

    def it_converts_attributes(expect, sample):
        expect(sample.datafile.data) == {'name': "d"}
