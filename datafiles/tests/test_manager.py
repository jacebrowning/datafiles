# pylint: disable=unused-variable

from dataclasses import dataclass
from unittest.mock import patch

import pytest

from datafiles.manager import Manager
from datafiles.model import create_model


@dataclass
class MyClass:
    foo: int
    bar: int


def describe_manager():
    @pytest.fixture
    def manager():
        model = create_model(MyClass, pattern='files/{self.foo}.yml')
        return Manager(model)

    def describe_get_or_none():
        @patch('datafiles.mapper.Mapper.load')
        @patch('datafiles.mapper.Mapper.exists', True)
        @patch('datafiles.mapper.Mapper.modified', False)
        def when_file_exists(mock_load, expect, manager):
            expect(manager.get_or_none(foo=1, bar=2)) == MyClass(foo=1, bar=2)
            expect(mock_load.called).is_(True)

        @patch('datafiles.mapper.Mapper.exists', False)
        def when_file_missing(expect, manager):
            expect(manager.get_or_none(foo=3, bar=4)).is_(None)

    def describe_get_or_create():
        @patch('datafiles.mapper.Mapper.save')
        @patch('datafiles.mapper.Mapper.load')
        @patch('datafiles.mapper.Mapper.exists', True)
        @patch('datafiles.mapper.Mapper.modified', False)
        def when_file_exists(mock_save, mock_load, expect, manager):
            expect(manager.get_or_create(foo=1, bar=2)) == MyClass(foo=1, bar=2)
            expect(mock_save.called).is_(True)
            expect(mock_load.called).is_(False)

        @patch('datafiles.mapper.Mapper.save')
        @patch('datafiles.mapper.Mapper.load')
        @patch('datafiles.mapper.Mapper.exists', False)
        def when_file_missing(mock_save, mock_load, expect, manager):
            expect(manager.get_or_create(foo=1, bar=2)) == MyClass(foo=1, bar=2)
            expect(mock_save.called).is_(True)
            expect(mock_load.called).is_(True)

    def describe_all():
        @patch('datafiles.mapper.Mapper.exists', False)
        def when_no_files_exist(expect, manager):
            items = list(manager.all())
            expect(items) == []

    def describe_filter():
        @patch('datafiles.mapper.Mapper.exists', False)
        def when_no_files_exist(expect, manager):
            items = list(manager.filter())
            expect(items) == []

        @patch('datafiles.mapper.Mapper.exists', False)
        def with_partial_positional_arguments(expect, manager):
            items = list(manager.filter(foo=1))
            expect(items) == []
