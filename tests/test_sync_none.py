from dataclasses import dataclass

import pytest

import yorm2


@dataclass
@yorm2.sync(attrs={}, path="tmp/{self.key}.yml")
class Sample:
    key: int
    name: str


def describe_defaults():
    @pytest.fixture
    def sample(clean_tmp):
        return Sample(42, "foobar")

    @pytest.fixture
    def mapper(sample):
        return yorm2.get_mapper(sample)

    def test_attrs(expect, mapper):
        expect(mapper.attrs) == {}

    def test_path(expect, mapper):
        expect(mapper.path) == "tmp/42.yml"

    def test_data(expect, mapper):
        expect(mapper.data) == {}
