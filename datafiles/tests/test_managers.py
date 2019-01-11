# pylint: disable=unused-variable,protected-access

from dataclasses import dataclass
from pathlib import Path

import pytest

from datafiles import managers


@dataclass
class MyModel:
    foobar: int


class MyField:
    @classmethod
    def to_preserialization_data(cls, python_value):
        return python_value


def describe_instance_manager():
    @pytest.fixture
    def manager():
        return managers.InstanceManager(
            instance=MyModel(foobar=42),
            attrs={},
            pattern=None,
            manual=False,
            defaults=False,
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
