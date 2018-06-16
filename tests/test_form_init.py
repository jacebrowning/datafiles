from dataclasses import dataclass

import pytest

import form


@dataclass
class Sample_NoMeta(form.Model):
    key: int
    name: str


@dataclass
class Sample_NoFields(form.Model):
    key: int
    name: str

    class Meta:
        form_path = "tmp/{self.key}.yml"


@dataclass
class Sample_BuiltinFields(form.Model):
    key: int
    name: str

    class Meta:
        form_path = "tmp/{self.key}.yml"
        form_fields = {"name": form.fields.String}


def describe_no_meta():
    @pytest.fixture
    def sample(clean_tmp):
        return Sample_NoMeta(42, "foobar")

    def test_fields(expect, sample):
        expect(sample.form.fields) == {}

    def test_path(expect, sample):
        expect(sample.form.path) == None

    def test_data(expect, sample):
        expect(sample.form.data) == {}


def describe_no_fields():
    @pytest.fixture
    def sample(clean_tmp):
        return Sample_NoFields(42, "foobar")

    def test_fields(expect, sample):
        expect(sample.form.fields) == {}

    def test_path(expect, sample):
        expect(sample.form.path) == "tmp/42.yml"

    def test_data(expect, sample):
        expect(sample.form.data) == {}


def describe_builtin_fields():
    @pytest.fixture
    def sample(clean_tmp):
        return Sample_BuiltinFields(42, "foobar")

    def test_fields(expect, sample):
        expect(sample.form.fields) == {"name": form.fields.String}

    def test_path(expect, sample):
        expect(sample.form.path) == "tmp/42.yml"

    def test_data(expect, sample):
        expect(sample.form.data) == {"name": "foobar"}
