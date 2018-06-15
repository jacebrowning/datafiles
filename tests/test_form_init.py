from dataclasses import dataclass

import pytest

import yorm2


def describe_zero_fields():
    @dataclass
    class Sample(yorm2.Model):
        key: int
        name: str

        class Meta:
            path = "tmp/{self.key}.yml"

    @pytest.fixture
    def sample(clean_tmp):
        return Sample(42, "foobar")

    def test_attrs(expect, sample):
        expect(sample.form.fields) == {}

    def test_path(expect, sample):
        expect(sample.form.path) == "tmp/42.yml"

    def test_data(expect, sample):
        expect(sample.form.data) == {}


def describe_builtin_fields():
    @dataclass
    class Sample(yorm2.Model):
        key: int
        name: str

        class Meta:
            name = yorm2.fields.String
            path = "tmp/{self.key}.yml"

    @pytest.fixture
    def sample(clean_tmp):
        return Sample(42, "foobar")

    def test_attrs(expect, sample):
        expect(sample.form.fields) == {"name": yorm2.fields.String}

    def test_path(expect, sample):
        expect(sample.form.path) == "tmp/42.yml"

    def test_data(expect, sample):
        expect(sample.form.data) == {"name": "foobar"}
