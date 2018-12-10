# pylint: disable=unused-variable

from dataclasses import dataclass

import pytest

from datafiles import sync
from datafiles.converters import Number, Text


@sync('../tmp/sample.yml')
@dataclass
class Sample:
    number: Number = 0
    text: Text = ""


@pytest.fixture
def sample():
    return Sample()


def describe_number():
    def with_float_to_integer(sample, expect, read, dedent):
        sample.number = 1.23

        expect(read('tmp/sample.yml')) == dedent(
            """
            number: 1.23
            """
        )

        sample.number = 4

        expect(read('tmp/sample.yml')) == dedent(
            """
            number: 4
            """
        )

    def with_integer_to_float(sample, write, expect):
        write(
            'tmp/sample.yml',
            """
            number: 5
            """,
        )

        expect(sample.number) == 5

        write(
            'tmp/sample.yml',
            """
            number: 6.78
            """,
        )

        sample.number = 6.7


def describe_text():
    def with_single_line(sample, expect, read, dedent):
        sample.text = "Hello, world!"

        expect(read('tmp/sample.yml')) == dedent(
            """
            text: Hello, world!
            """
        )

    def with_multiple_lines(sample, expect, read, dedent, write):
        sample.text = '\n'.join(f'Line {i+1}' for i in range(3))

        expect(read('tmp/sample.yml')) == dedent(
            """
            text: |
              Line 1
              Line 2
              Line 3
            """
        )

        write(
            'tmp/sample.yml',
            """
            text: |
              Line 4
              Line 5
              Line 6
            """,
        )

        expect(sample.text) == "Line 4\nLine 5\nLine 6\n"

    def with_extra_newlines(sample, expect, read, dedent):
        sample.text = "\nabc\ndef\n\n"

        expect(read('tmp/sample.yml')) == dedent(
            """
            text: |
              abc
              def
            """
        )

        sample.datafile.load()
        sample.datafile.save()

        expect(sample.text) == "abc\ndef\n"
