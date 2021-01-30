"""Tests for extended converters."""

# pylint: disable=unused-variable


import pytest

from datafiles import datafile
from datafiles.converters import Number, Text
from datafiles.utils import dedent, read, write


@datafile('../tmp/sample.yml')
class Sample:
    number: Number = Number(0)
    text: Text = Text("")


def describe_number():
    @pytest.fixture
    def sample():
        return Sample()

    def with_float_to_integer(sample, expect):
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

    @pytest.mark.flaky
    def with_integer_to_float(sample, expect):
        write(
            'tmp/sample.yml',
            """
            number: 5
            """,
        )
        sample.datafile._last_load = 0.0

        expect(sample.number) == 5

        write(
            'tmp/sample.yml',
            """
            number: 6.78
            """,
        )
        sample.datafile._last_load = 0.0

        sample.number = 6.7


def describe_text():
    @pytest.fixture
    def sample():
        return Sample()

    def with_single_line(sample, expect):
        sample.text = "Hello, world!"

        expect(read('tmp/sample.yml')) == dedent(
            """
            text: Hello, world!
            """
        )

    @pytest.mark.flaky
    def with_multiple_lines(sample, expect):
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
        sample.datafile._last_load = 0.0

        expect(sample.text) == "Line 4\nLine 5\nLine 6\n"

    def with_extra_newlines(sample, expect):
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
