# pylint: disable=unused-variable,unused-argument

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from unittest.mock import patch

import pytest

from datafiles.manager import Manager, Missing
from datafiles.model import create_model


@dataclass
class Nested:
    name: str


@dataclass
class MyClass:
    foo: int
    bar: int
    nested: Optional[Nested] = None


@dataclass
class MyClassDefaults:
    foo: int
    bar: int = 2


def describe_manager():
    @pytest.fixture
    def files():
        return Path(__file__).parent / "files"

    @pytest.fixture
    def manager(files: Path):
        shutil.rmtree(files, ignore_errors=True)
        model = create_model(MyClass, pattern="files/{self.foo}.yml")
        return Manager(model)

    @pytest.fixture
    def manager_at_home():
        model = create_model(Nested, pattern="~/.{self.name}.json")
        return Manager(model)

    @pytest.fixture
    def manager_with_files(files: Path):
        files.mkdir(exist_ok=True)
        model = create_model(MyClass, pattern="files/{self.foo}.yml")
        model(foo=1, bar=2).datafile.save()
        return Manager(model)

    @pytest.fixture
    def manager_with_defaults(files: Path):
        shutil.rmtree(files, ignore_errors=True)
        model = create_model(MyClassDefaults, pattern="files/{self.foo}/{self.bar}.yml")
        return Manager(model)

    def describe_get():
        @patch("datafiles.mapper.Mapper.load")
        @patch("datafiles.mapper.Mapper.exists", True)
        @patch("datafiles.mapper.Mapper.modified", False)
        def when_absent_pattern_arg(mock_load, expect, manager):
            instance = manager.get(1)
            expect(instance.foo) == 1
            expect(instance.bar) is Missing
            expect(mock_load.called).is_(True)

            with expect.raises(
                TypeError,
                "Manager.get() missing required placeholder field argument: 'foo'",
            ):
                manager.get(bar=2)

        @patch("datafiles.mapper.Mapper.load")
        @patch("datafiles.mapper.Mapper.exists", True)
        @patch("datafiles.mapper.Mapper.modified", False)
        def when_absent_pattern_arg_has_default_value(
            mock_load, expect, manager_with_defaults: Manager
        ):
            expect(manager_with_defaults.get(0, 1)) == MyClassDefaults(foo=0, bar=1)
            expect(manager_with_defaults.get(1)) == MyClassDefaults(foo=1, bar=2)
            expect(mock_load.called).is_(True)

        @patch("datafiles.mapper.Mapper.exists", True)
        @patch("datafiles.mapper.Mapper.modified", False)
        def when_partial_args_match_file(expect, manager_with_files: Manager):
            expect(manager_with_files.get(1)) == MyClass(foo=1, bar=2)

        @patch("datafiles.mapper.Mapper.exists", True)
        @patch("datafiles.mapper.Mapper.modified", False)
        def when_partial_kwargs_match_file(expect, manager_with_files: Manager):
            expect(manager_with_files.get(foo=1)) == MyClass(foo=1, bar=2)

    def describe_get_or_none():
        @patch("datafiles.mapper.Mapper.load")
        @patch("datafiles.mapper.Mapper.exists", True)
        @patch("datafiles.mapper.Mapper.modified", False)
        def when_file_exists(mock_load, expect, manager: Manager):
            expect(manager.get_or_none(foo=1, bar=2)) == MyClass(foo=1, bar=2)
            expect(mock_load.called).is_(True)

        @patch("datafiles.mapper.Mapper.exists", False)
        def when_file_missing(expect, manager: Manager):
            expect(manager.get_or_none(foo=3, bar=4)).is_(None)

        def when_file_corrupt(expect, manager: Manager):
            instance = manager.get_or_create(foo=2, bar=1)
            instance.datafile.path.write_text("{")
            instance2 = manager.get_or_none(foo=2, bar=2)
            expect(instance2).is_(None)
            expect(instance.datafile.path.is_file()).is_(False)

    def describe_get_or_create():
        @patch("datafiles.mapper.Mapper.save")
        @patch("datafiles.mapper.Mapper.load")
        @patch("datafiles.mapper.Mapper.exists", True)
        @patch("datafiles.mapper.Mapper.modified", False)
        def when_file_exists(mock_save, mock_load, expect, manager: Manager):
            expect(manager.get_or_create(foo=1, bar=2)) == MyClass(foo=1, bar=2)
            expect(mock_save.called).is_(True)
            expect(mock_load.called).is_(False)

        @patch("datafiles.mapper.Mapper.save")
        @patch("datafiles.mapper.Mapper.load")
        @patch("datafiles.mapper.Mapper.exists", False)
        def when_file_missing(mock_save, mock_load, expect, manager: Manager):
            expect(manager.get_or_create(foo=1, bar=2)) == MyClass(foo=1, bar=2)
            expect(mock_save.called).is_(True)
            expect(mock_load.called).is_(True)

        def when_file_corrupt(expect, manager: Manager):
            instance = manager.get_or_create(foo=2, bar=1)
            instance.datafile.path.write_text("{")
            instance2 = manager.get_or_create(foo=2, bar=2)
            expect(instance2.bar) == 2  # type: ignore[attr-defined]

    def describe_all():
        @patch("datafiles.mapper.Mapper.exists", False)
        def when_no_files_exist(expect, manager: Manager):
            items = list(manager.all())
            expect(items) == []

        def with_home_directory(expect, manager_at_home: Manager):
            items = list(manager_at_home.all())
            if "CI" not in os.environ:
                expect(len(items)) > 0

    def describe_filter():
        @patch("datafiles.mapper.Mapper.exists", False)
        def when_no_files_exist(expect, manager: Manager):
            items = list(manager.filter())
            expect(items) == []

        @patch("datafiles.mapper.Mapper.exists", False)
        def with_partial_positional_arguments(expect, manager: Manager):
            items = list(manager.filter(foo=1))
            expect(items) == []

        @patch("datafiles.mapper.Mapper.exists", False)
        def with_nested_key_query(expect, manager: Manager):
            items = list(manager.filter(nested__name="John Doe"))
            expect(items) == []
