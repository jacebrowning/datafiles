"""Tests for setting up a new class."""

# pylint: disable=unused-variable

import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

import datafiles
from datafiles import datafile

from . import xfail_with_pep_563


def describe_automatic():
    """Test creating a datafile using the decorator."""

    @pytest.fixture
    def sample():
        @datafile("../tmp/{self.key}.yml")
        class Sample:
            key: int
            name: str
            score: float = 1 / 2

        return Sample(1, "a")

    def it_inferrs_attrs(expect, sample):
        expect(sample.datafile.attrs) == {
            "name": datafiles.converters.String,
            "score": datafiles.converters.Float,
        }

    def it_formats_path_from_pattern(expect, sample):
        root = Path(__file__).parents[1]
        expect(sample.datafile.path) == root / "tmp" / "1.yml"

    def it_converts_attributes(expect, sample):
        expect(sample.key) == 1
        expect(sample.name) == "a"
        expect(sample.score) == 0.5
        expect(sample.datafile.data) == {"name": "a"}


def describe_automatic_with_defaults():
    """Test creating a datafile using the decorator with defaults."""

    def describe_flat():
        @pytest.fixture
        def sample():
            @datafile("../tmp/{self.key}.yml", defaults=True)
            class Sample:
                key: int
                name: str
                score: float = 1 / 2

            return Sample(1, "a")

        def it_converts_attributes(expect, sample):
            expect(sample.datafile.data) == {"name": "a", "score": 0.5}

    def describe_nested():
        @pytest.fixture
        def sample():
            @dataclass
            class Nested:
                name: str
                score: float = 1 / 4

            @datafile("../tmp/{self.key}.yml", defaults=True)
            class Sample:
                key: int
                nested: Nested
                name: str
                score: float = 1 / 2

            return Sample(1, Nested(name="b"), "a")

        @xfail_with_pep_563
        def it_converts_attributes(expect, sample):
            expect(sample.datafile.data) == {
                "name": "a",
                "score": 0.5,
                "nested": {"name": "b", "score": 0.25},
            }

    def describe_nested_override():
        @pytest.fixture
        def sample():
            @dataclass
            class Nested:
                name: str
                score: float = 1 / 4

                class Meta:
                    datafile_defaults = False

            @datafile("../tmp/{self.key}.yml", defaults=True)
            class Sample:
                key: int
                nested: Nested
                name: str
                score: float = 1 / 2

            return Sample(1, Nested(name="b"), "a")

        @pytest.mark.xfail(reason="https://github.com/jacebrowning/datafiles/issues/64")
        def it_converts_attributes(expect, sample):
            expect(sample.datafile.data) == {
                "name": "a",
                "score": 0.5,
                "nested": {"name": "b"},
            }


def describe_manual():
    """Test creating a datafile using the model class."""

    @pytest.fixture
    def sample():
        @dataclass
        class Sample(datafiles.Model):
            key: int
            name: str
            score: float = 1 / 4

        return Sample(2, "b")

    def it_inferrs_attrs(expect, sample):
        expect(sample.datafile.attrs) == {
            "key": datafiles.converters.Integer,
            "name": datafiles.converters.String,
            "score": datafiles.converters.Float,
        }

    def it_has_no_path(expect, sample):
        expect(sample.datafile.path).is_(None)

    def it_converts_attributes(expect, sample):
        expect(sample.key) == 2
        expect(sample.name) == "b"
        expect(sample.score) == 0.25
        expect(sample.datafile.data) == {"key": 2, "name": "b"}


def describe_manual_with_attrs():
    """Test creating a datafile with explicit attrs."""

    @pytest.fixture
    def sample():
        @dataclass
        class Sample(datafiles.Model):
            key: int
            name: str
            score: float = 1 / 8
            extra: bool = True

            class Meta:
                datafile_attrs = {"name": datafiles.converters.String}

        return Sample(3, "c")

    def it_uses_attrs_from_meta(expect, sample):
        expect(sample.datafile.attrs) == {"name": datafiles.converters.String}

    def it_has_no_path(expect, sample):
        expect(sample.datafile.path).is_(None)

    def it_converts_attributes(expect, sample):
        expect(sample.datafile.data) == {"name": "c"}


def describe_manual_with_attrs_and_pattern():
    """Test creating a datafile with explicit attrs and pattern."""

    @pytest.fixture
    def sample():
        @dataclass
        class Sample(datafiles.Model):
            key: int
            name: str
            score: float = 1 / 16

            class Meta:
                datafile_attrs = {"name": datafiles.converters.String}
                datafile_pattern = "../tmp/{self.key}.yml"

        return Sample(4, "d")

    def it_uses_attrs_from_meta(expect, sample):
        expect(sample.datafile.attrs) == {"name": datafiles.converters.String}

    def it_formats_path_from_pattern(expect, sample):
        root = Path(__file__).parents[1]
        expect(sample.datafile.path) == root / "tmp" / "4.yml"

    def it_converts_attributes(expect, sample):
        expect(sample.datafile.data) == {"name": "d"}


def describe_absolute_pattern():
    """Test creating a datafile using the decorator with an absolute path."""

    @pytest.fixture
    def sample():
        @datafile("/private/tmp/{self.key}.yml")
        class Sample:
            key: int
            name: str
            score: float = 1 / 2

        return Sample(5, "a")

    @pytest.mark.skipif(sys.platform != "darwin", reason="Test only valid on macOS")
    def it_formats_path_from_pattern(expect, sample):
        expect(sample.datafile.path) == Path("/private/tmp") / "5.yml"
