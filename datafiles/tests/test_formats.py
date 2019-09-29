# pylint: disable=unused-variable

import pytest

from datafiles import formats, settings
from datafiles.utils import dedent


def describe_serialize():
    @pytest.fixture
    def data():
        return {'key': "value", 'items': [1, 'a', None]}

    def describe_yaml():
        def it_indents_blocks_by_default(expect, data):
            text = formats.YAML.serialize(data)
            expect(text) == dedent(
                """
            key: value
            items:
              - 1
              - a
              -
            """
            )

        def it_can_render_lists_inline(expect, data, monkeypatch):
            monkeypatch.setattr(settings, 'INDENT_YAML_BLOCKS', False)
            text = formats.YAML.serialize(data)
            expect(text) == dedent(
                """
            key: value
            items:
            - 1
            - a
            -
            """
            )


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
