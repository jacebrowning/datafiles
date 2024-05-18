# pylint: disable=unused-variable

import pytest

from datafiles import auto
from datafiles.utils import dedent, logbreak, read, write


def describe_auto():
    def it_implements_repr(expect):
        write(
            "tmp/sample.yml",
            """
            items:
              - 1
              - 2
            value: abc
            """,
        )

        logbreak("Inferring object")
        sample = auto("tmp/sample.yml")

        expect(repr(sample)) == "Sample(items=[1, 2], value='abc')"

    @pytest.mark.parametrize(
        ("filename", "count"),
        [
            (".appveyor.yml", 6),
            (".github/workflows/main.yml", 3),
            ("mkdocs.yml", 8),
            ("pyproject.toml", 2),
        ],
    )
    def with_real_file(expect, filename, count):
        logbreak("Inferring object")
        sample = auto(filename)

        logbreak("Reading attributes")
        expect(len(sample.datafile.data)) == count

    def with_sample_file(expect):
        write(
            "tmp/sample.yml",
            """
            homogeneous_list:
              - 1
              - 2
            heterogeneous_list:
              - 1
              - 'abc'
            empty_list: []
            """,
        )

        logbreak("Inferring object")
        sample = auto("tmp/sample.yml")

        logbreak("Reading attributes")
        expect(sample.homogeneous_list) == [1, 2]
        expect(sample.heterogeneous_list) == [1, "abc"]
        expect(sample.empty_list) == []

        logbreak("Updating attribute")
        sample.homogeneous_list.append(3.4)
        sample.heterogeneous_list.append(5.6)
        sample.empty_list.append(7.8)

        logbreak("Reading file")
        expect(read("tmp/sample.yml")) == dedent(
            """
            homogeneous_list:
              - 1
              - 2
              - 3
            heterogeneous_list:
              - 1
              - 'abc'
              - 5.6
            empty_list:
              - 7.8
            """
        )

    def with_floats(expect):
        write(
            "tmp/sample.yml",
            """
            language: python
            python:
              - 3.7
              - 3.8
            """,
        )

        logbreak("Inferring object")
        sample = auto("tmp/sample.yml")

        logbreak("Updating attribute")
        sample.python.append(4)

        logbreak("Reading file")
        expect(read("tmp/sample.yml")) == dedent(
            """
            language: python
            python:
              - 3.7
              - 3.8
              - 4.0
            """
        )

    def with_nested_mutables(expect):
        write(
            "tmp/sample.yml",
            """
            name: Test
            roles:
              category1:
                - value1
                - value2
              category2:
                - something
                - else
            """,
        )

        logbreak("Inferring object")
        sample = auto("tmp/sample.yml")

        logbreak("Updating attributes")
        sample.roles.category1.append("value3")

        logbreak("Reading file")
        expect(read("tmp/sample.yml")) == dedent(
            """
            name: Test
            roles:
              category1:
                - value1
                - value2
                - value3
              category2:
                - something
                - else
            """
        )
