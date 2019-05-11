# pylint: disable=unused-variable

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

import pytest

from datafiles import managers
from datafiles.models import ModelMeta, create_model


@dataclass
class MyClass:
    foobar: int


class MyField:
    @classmethod
    def to_preserialization_data(cls, python_value):
        return python_value


def describe_model_manager():
    @pytest.fixture
    def manager():
        return managers.Manager(create_model(MyClass, manual=True))

    def describe_get_or_none():
        @patch('datafiles.managers.Datafile.exists', True)
        def when_file_exists(expect, manager):
            expect(manager.get_or_none(foobar=1)) == MyClass(foobar=1)

        @patch('datafiles.managers.Datafile.exists', False)
        def when_file_missing(expect, manager):
            expect(manager.get_or_none(foobar=2)) == None

    def describe_get_or_create():
        @patch('datafiles.managers.Datafile.save')
        @patch('datafiles.managers.Datafile.exists', True)
        def when_file_exists(mock_save, expect, manager):
            expect(manager.get_or_create(foobar=1)) == MyClass(foobar=1)
            expect(mock_save.call_count) == 0

        @patch('datafiles.managers.Datafile.save')
        @patch('datafiles.managers.Datafile.exists', False)
        def when_file_missing(mock_save, expect, manager):
            expect(manager.get_or_create(foobar=2)) == MyClass(foobar=2)
            expect(mock_save.call_count) == 1


def describe_instance_manager():
    @pytest.fixture
    def manager():
        return managers.Datafile(
            instance=MyClass(foobar=42),
            attrs={},
            pattern=None,
            manual=ModelMeta.datafile_manual,
            defaults=ModelMeta.datafile_defaults,
            auto_load=ModelMeta.datafile_auto_load,
            auto_save=ModelMeta.datafile_auto_save,
            auto_attr=ModelMeta.datafile_auto_attr,
        )

    def describe_path():
        def is_none_when_no_pattern(expect, manager):
            expect(manager.path) == None

        def is_absolute_based_on_the_file(expect, manager):
            manager._pattern = '../../tmp/sample.yml'
            root = Path(__file__).parents[2]
            expect(manager.path) == root / 'tmp' / 'sample.yml'

    def describe_relpath():
        def when_cwd_is_parent(expect, manager):
            manager._pattern = '../../tmp/sample.yml'
            expect(manager.relpath) == Path('tmp', 'sample.yml')

        def when_cwd_is_sibling(expect, manager):
            manager._pattern = '../../../tmp/sample.yml'
            expect(manager.relpath) == Path('..', 'tmp', 'sample.yml')

    def describe_text():
        def is_blank_when_no_attrs(expect, manager):
            expect(manager.text) == ""

        def is_yaml_by_default(expect, manager):
            manager.attrs = {'foobar': MyField}
            expect(manager.text) == "foobar: 42\n"

        def with_json_format(expect, manager):
            manager._pattern = '_.json'
            manager.attrs = {'foobar': MyField}
            expect(manager.text) == '{\n  "foobar": 42\n}'

        def with_toml_format(expect, manager):
            manager._pattern = '_.toml'
            manager.attrs = {'foobar': MyField}
            expect(manager.text) == "foobar = 42\n"

        def with_no_format(expect, manager):
            manager._pattern = '_'
            manager.attrs = {'foobar': MyField}
            expect(manager.text) == "foobar: 42\n"

        def with_unknown_format(expect, manager):
            manager._pattern = '_.xyz'
            manager.attrs = {'foobar': MyField}
            with expect.raises(ValueError):
                print(manager.text)

    def describe_load():
        def it_requires_path(expect, manager):
            with expect.raises(RuntimeError):
                manager.load()

    def describe_save():
        def it_requires_path(expect, manager):
            with expect.raises(RuntimeError):
                manager.save()
