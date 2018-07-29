# pylint: disable=unused-variable

from dataclasses import dataclass

import pytest

from datafiles import managers


@dataclass
class MyModel:
    foobar: int


class MyField:
    pass


def describe_instance_manager():
    @pytest.fixture
    def manager():
        return managers.InstanceManager(
            instance=MyModel(foobar=42), pattern=None, fields={}
        )

    def describe_text():
        def is_blank_when_no_fields(expect, manager):
            expect(manager.text) == ""

        def is_yaml_by_default(expect, manager):
            manager.fields = {'foobar', MyField}
            expect(manager.text) == "foobar: 42\n"

        def can_specify_a_format(expect, manager):
            manager.fields = {'foobar', MyField}
            expect(manager.get_text('json')) == '{"foobar": 42}'

        def raises_an_exception_for_unknown_formats(expect, manager):
            with expect.raises(ValueError):
                manager.get_text('xyz')
