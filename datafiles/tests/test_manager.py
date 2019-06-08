# pylint: disable=unused-variable

from dataclasses import dataclass
from unittest.mock import patch

import pytest

from datafiles.manager import Manager
from datafiles.model import create_model


@dataclass
class MyClass:
    foobar: int


@dataclass
class MyClass2:
    foo: int
    bar: int


def describe_manager():
    @pytest.fixture
    def manager():
        model = create_model(MyClass, pattern='files/{self.foobar}.yml')
        return Manager(model)

    def describe_all():
        @patch('datafiles.mapper.Mapper.exists', False)
        def when_no_files_exist(expect, manager):
            items = list(manager.all())
            expect(items) == []

    def describe_get_or_none():
        @patch('datafiles.mapper.Mapper.load')
        @patch('datafiles.mapper.Mapper.exists', True)
        @patch('datafiles.mapper.Mapper.modified', False)
        def when_file_exists(mock_load, expect, manager):
            expect(manager.get_or_none(foobar=1)) == MyClass(foobar=1)
            expect(mock_load.called) == True

        @patch('datafiles.mapper.Mapper.exists', False)
        def when_file_missing(expect, manager):
            expect(manager.get_or_none(foobar=2)) == None

    def describe_get_or_create():
        @patch('datafiles.mapper.Mapper.load')
        @patch('datafiles.mapper.Mapper.save')
        @patch('datafiles.mapper.Mapper.exists', True)
        @patch('datafiles.mapper.Mapper.modified', False)
        def when_file_exists(mock_load, mock_save, expect, manager):
            expect(manager.get_or_create(foobar=1)) == MyClass(foobar=1)
            expect(mock_load.called) == False
            expect(mock_save.called) == True

        @patch('datafiles.mapper.Mapper.save')
        @patch('datafiles.mapper.Mapper.exists', False)
        def when_file_missing(mock_save, expect, manager):
            expect(manager.get_or_create(foobar=2)) == MyClass(foobar=2)
            expect(mock_save.called) == True

    def describe_filter():
        @patch('datafiles.mapper.Mapper.exists', False)
        def when_no_files_exist(expect, manager):
            items = list(manager.filter())
            expect(items) == []

        @patch('datafiles.mapper.Mapper.exists', False)
        def with_partial_positional_arguments(expect):
            model = create_model(MyClass2, pattern='files/{self.foobar}.yml')
            manager = Manager(model)
            items = list(manager.filter(foo=1))
            expect(items) == []
