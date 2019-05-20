# pylint: disable=unused-variable

from dataclasses import dataclass
from unittest.mock import patch

import pytest

from datafiles import managers
from datafiles.models import create_model


@dataclass
class MyClass:
    foobar: int


def describe_manager():
    @pytest.fixture
    def manager():
        model = create_model(MyClass, pattern='files/{self.foobar}.yml')
        return managers.Manager(model)

    def describe_all():
        @patch('datafiles.mappers.Mapper.exists', False)
        def when_no_files_exist(expect, manager):
            items = list(manager.all())
            expect(items) == []

    def describe_get_or_none():
        @patch('datafiles.mappers.Mapper.load')
        @patch('datafiles.mappers.Mapper.exists', True)
        @patch('datafiles.mappers.Mapper.modified', False)
        def when_file_exists(mock_load, expect, manager):
            expect(manager.get_or_none(foobar=1)) == MyClass(foobar=1)
            expect(mock_load.called) == True

        @patch('datafiles.mappers.Mapper.exists', False)
        def when_file_missing(expect, manager):
            expect(manager.get_or_none(foobar=2)) == None

    def describe_get_or_create():
        @patch('datafiles.mappers.Mapper.load')
        @patch('datafiles.mappers.Mapper.save')
        @patch('datafiles.mappers.Mapper.exists', True)
        @patch('datafiles.mappers.Mapper.modified', False)
        def when_file_exists(mock_load, mock_save, expect, manager):
            expect(manager.get_or_create(foobar=1)) == MyClass(foobar=1)
            expect(mock_load.called) == False
            expect(mock_save.called) == True

        @patch('datafiles.mappers.Mapper.save')
        @patch('datafiles.mappers.Mapper.exists', False)
        def when_file_missing(mock_save, expect, manager):
            expect(manager.get_or_create(foobar=2)) == MyClass(foobar=2)
            expect(mock_save.called) == True
