# pylint: disable=unused-variable

import platform
from dataclasses import dataclass
from pathlib import Path

import pytest

from datafiles.config import Meta
from datafiles.mapper import Mapper, create_mapper


@dataclass
class MyClass:
    foobar: int


class MyField:
    @classmethod
    def to_preserialization_data(cls, python_value):
        return python_value


def describe_mapper():
    @pytest.fixture
    def mapper():
        return Mapper(
            instance=MyClass(foobar=42),
            attrs={},
            pattern=None,
            manual=Meta.datafile_manual,
            defaults=Meta.datafile_defaults,
            auto_load=Meta.datafile_auto_load,
            auto_save=Meta.datafile_auto_save,
            auto_attr=Meta.datafile_auto_attr,
        )

    def describe_path():
        def is_none_when_no_pattern(expect, mapper):
            expect(mapper.path).is_(None)

        def is_relative_to_file_by_default(expect, mapper):
            mapper._pattern = '../../tmp/sample.yml'
            root = Path(__file__).parents[2]
            expect(mapper.path) == root / 'tmp' / 'sample.yml'

        def is_absolute_when_specified(expect, mapper):
            mapper._pattern = '/private/tmp/sample.yml'
            if platform.system() == 'Windows':
                path = Path('C:/private/tmp/sample.yml')
            else:
                path = Path('/private/tmp/sample.yml')
            expect(mapper.path) == path

        def is_relative_to_cwd_when_specified(expect, mapper):
            mapper._pattern = './foobar/sample.yml'
            if platform.system() == 'Windows':
                path = Path('foobar/sample.yml')
            else:
                path = Path.cwd() / 'foobar' / 'sample.yml'
            expect(mapper.path) == path

    def describe_relpath():
        def when_cwd_is_parent(expect, mapper):
            mapper._pattern = '../../tmp/sample.yml'
            expect(mapper.relpath) == Path('tmp', 'sample.yml')

        def when_cwd_is_sibling(expect, mapper):
            mapper._pattern = '../../../tmp/sample.yml'
            expect(mapper.relpath) == Path('..', 'tmp', 'sample.yml')

    def describe_text():
        def is_blank_when_no_attrs(expect, mapper):
            expect(mapper.text) == ""

        def is_yaml_by_default(expect, mapper):
            mapper.attrs = {'foobar': MyField}
            expect(mapper.text) == "foobar: 42\n"

        def with_json_format(expect, mapper):
            mapper._pattern = '_.json'
            mapper.attrs = {'foobar': MyField}
            expect(mapper.text) == '{\n  "foobar": 42\n}'

        def with_toml_format(expect, mapper):
            mapper._pattern = '_.toml'
            mapper.attrs = {'foobar': MyField}
            expect(mapper.text) == "foobar = 42\n"

        def with_no_format(expect, mapper):
            mapper._pattern = '_'
            mapper.attrs = {'foobar': MyField}
            expect(mapper.text) == "foobar: 42\n"

        def with_unknown_format(expect, mapper):
            mapper._pattern = '_.xyz'
            mapper.attrs = {'foobar': MyField}
            with expect.raises(ValueError):
                print(mapper.text)

    def describe_load():
        def it_requires_path(expect, mapper):
            with expect.raises(RuntimeError):
                mapper.load()

    def describe_save():
        def it_requires_path(expect, mapper):
            with expect.raises(RuntimeError):
                mapper.save()


def describe_create_mapper():
    def it_reuses_existing_datafile(mocker, expect):
        obj = mocker.Mock()
        mapper = mocker.Mock()
        obj.datafile = mapper

        new_mapper = create_mapper(obj)

        expect(new_mapper) == obj.datafile
