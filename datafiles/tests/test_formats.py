# pylint: disable=unused-variable

from pathlib import Path

import pytest

from datafiles import formats, settings
from datafiles.utils import dedent


@pytest.fixture(autouse=True, scope='session')
def format_example():
    path = Path.cwd() / 'docs' / 'settings.md'
    example = path.read_text()
    example = example.replace("  - 4", "- 4")
    example = example.replace("  - 5", "- 5")
    example = example.replace("  - 6", "- 6")
    path.write_text(example)


def describe_serialize():
    @pytest.fixture
    def data():
        return {'key': "value", 'items': [1, 'a', None]}

    def describe_ruamel_yaml():
        def it_indents_blocks_by_default(expect, data):
            text = formats.serialize(data, '.yaml')
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
            text = formats.serialize(data, '.yaml')
            expect(text) == dedent(
                """
            key: value
            items:
            - 1
            - a
            -
            """
            )

    def describe_pyyaml():
        def it_indents_blocks_by_default(expect, data):
            text = formats.serialize(data, '.yaml', formatter=formats.PyYAML)
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
            text = formats.serialize(data, '.yaml', formatter=formats.PyYAML)
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

    def describe_ruamel_yaml():
        def with_empty_file(expect, path):
            data = formats.deserialize(path, '.yaml')
            expect(data) == {}

    def describe_pyyaml():
        def with_empty_file(expect, path):
            data = formats.deserialize(path, '.yaml', formatter=formats.PyYAML)
            expect(data) == {}

    def describe_json():
        def with_empty_file(expect, path):
            path.write_text("{}")
            data = formats.deserialize(path, '.json')
            expect(data) == {}

    def describe_toml():
        def with_empty_file(expect, path):
            data = formats.deserialize(path, '.toml')
            expect(data) == {}

    def with_unknown_extension(expect, path):
        with expect.raises(ValueError):
            formats.deserialize(path, '.xyz')
