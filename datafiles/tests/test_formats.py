# pylint: disable=unused-variable


import pytest

from datafiles import formats


def describe_deserialize():
    @pytest.fixture
    def path(tmp_path):
        path = tmp_path / "sample"
        path.write_text("")
        return path

    def with_empty_yaml_file(expect, path):
        data = formats.deserialize(path, '.yaml')
        expect(data) == {}

    def with_empty_json_file(expect, path):
        path.write_text("{}")
        data = formats.deserialize(path, '.json')
        expect(data) == {}

    def with_empty_toml_file(expect, path):
        data = formats.deserialize(path, '.toml')
        expect(data) == {}

    def with_unknown_extension(expect, path):
        with expect.raises(ValueError):
            formats.deserialize(path, '.xyz')
