"""Tests for saving to a file."""

# pylint: disable=unused-variable,assigning-non-slot,unsubscriptable-object

from dataclasses import FrozenInstanceError
from typing import Optional

import pytest

from datafiles import datafile
from datafiles.utils import dedent, logbreak, read, write

from . import xfail_with_pep_563
from .samples import (
    Sample,
    SampleFrozen,
    SampleWithCustomFields,
    SampleWithDefaults,
    SampleWithList,
    SampleWithListOfDataclasses,
    SampleWithNesting,
    SampleWithNestingAndDefaults,
    SampleWithOptionals,
    SampleWithSet,
    SampleWithSetOfDataclasses,
    _FrozenNestedSample1,
    _NestedSample1,
)


def describe_nominal():
    @pytest.fixture
    def sample():
        return Sample(None, None, None, None)

    def without_initial_values(sample, expect):
        sample.datafile.save()

        with open("tmp/sample.yml") as f:
            expect(f.read()) == dedent(
                """
                bool_: false
                int_: 0
                float_: 0.0
                str_: ''
                """
            )

    def with_convertable_initial_values(expect):
        sample = Sample(1, 2, 3, 4)

        sample.datafile.save()

        with open("tmp/sample.yml") as f:
            expect(f.read()) == dedent(
                """
                bool_: true
                int_: 2
                float_: 3.0
                str_: '4'
                """
            )

    def with_extra_attributes(sample, expect):
        sample.extra = 5

        sample.datafile.save()

        with open("tmp/sample.yml") as f:
            expect(f.read()).excludes("extra")

    def with_custom_fields(expect):
        sample = SampleWithCustomFields("foo", "bar")

        sample.datafile.save()

        with open("tmp/sample.yml") as f:
            expect(f.read()) == dedent(
                """
                included: foo
                """
            )


def describe_frozen():
    def with_already_existing(expect):
        write(
            "tmp/sample.yml",
            """
            bool_: true
            int_: 1
            float_: 2.3
            str_: 'foobar'
            """,
        )
        sample = SampleFrozen(True, 1, 2.3, "foobar")
        with expect.raises(FrozenInstanceError):
            sample.datafile.save()


def describe_lists():
    def when_empty(expect):
        sample = SampleWithList([])

        sample.datafile.save()

        with open("tmp/sample.yml") as f:
            expect(f.read()) == dedent(
                """
                items:
                  -
                """
            )

    def with_conversion(expect):
        sample = SampleWithList([1, 2.3, "4.5"])

        logbreak("Saving")
        sample.datafile.save()

        with open("tmp/sample.yml") as f:
            expect(f.read()) == dedent(
                """
                items:
                  - 1.0
                  - 2.3
                  - 4.5
                """
            )

    def with_dataclasses(expect):
        sample = SampleWithListOfDataclasses([_NestedSample1("foobar", 42)])

        logbreak("Saving")
        sample.datafile.save()

        with open("tmp/sample.yml") as f:
            expect(f.read()) == dedent(
                """
                items:
                  - name: foobar
                    score: 42.0
                """
            )


def describe_sets():
    def when_empty(expect):
        sample = SampleWithSet({})

        sample.datafile.save()

        with open("tmp/sample.yml") as f:
            expect(f.read()) == dedent(
                """
                items:
                  -
                """
            )

    def with_conversion(expect):
        sample = SampleWithSet({1, 2.3, "4.5"})

        logbreak("Saving")
        sample.datafile.save()

        with open("tmp/sample.yml") as f:
            expect(f.read()) == dedent(
                """
                items:
                  - 1.0
                  - 2.3
                  - 4.5
                """
            )

    def with_dataclasses(expect):
        sample = SampleWithSetOfDataclasses({_FrozenNestedSample1("foobar", 42)})

        logbreak("Saving")
        sample.datafile.save()

        with open("tmp/sample.yml") as f:
            expect(f.read()) == dedent(
                """
                items:
                  - name: foobar
                    score: 42.0
                """
            )


def describe_nesting():
    def without_initial_values(expect):
        sample = SampleWithNesting(None, None, None)

        sample.datafile.save()

        with open("tmp/sample.yml") as f:
            expect(f.read()) == dedent(
                """
                name: ''
                score: 0.0
                nested:
                  name: ''
                  score: 0.0
                """
            )

    def with_initial_values(expect):
        sample = SampleWithNesting("foo", 1.2, {"name": "bar", "score": 3.4})

        sample.datafile.save()

        with open("tmp/sample.yml") as f:
            expect(f.read()) == dedent(
                """
                name: foo
                score: 1.2
                nested:
                  name: bar
                  score: 3.4
                """
            )

    def with_default_values(expect):
        sample = SampleWithNestingAndDefaults("a")

        sample.datafile.save()

        with open("tmp/sample.yml") as f:
            expect(f.read()) == dedent(
                """
                name: a
                nested: {}
                """
            )

    def with_missing_keys(expect):
        sample = SampleWithNesting("foo", 1.2, {"name": "bar"})

        sample.datafile.save()

        with open("tmp/sample.yml") as f:
            expect(f.read()) == dedent(
                """
                name: foo
                score: 1.2
                nested:
                  name: bar
                  score: 0.0
                """
            )

    def when_manually_setting_none(expect):
        sample = SampleWithNesting("foo", 1.2, {"name": "bar", "score": 3.4})
        sample.nested = None

        sample.datafile.save()

        with open("tmp/sample.yml") as f:
            expect(f.read()) == dedent(
                """
                name: foo
                score: 1.2
                nested:
                  name: ''
                  score: 0.0
                """
            )


def describe_optionals():
    def with_values(expect):
        sample = SampleWithOptionals(1, 2)

        sample.datafile.save()

        expect(read("tmp/sample.yml")) == dedent(
            """
            required: 1.0
            optional: 2.0
            """
        )

    def with_nones(expect):
        sample = SampleWithOptionals(None, None)

        sample.datafile.save()

        expect(read("tmp/sample.yml")) == dedent(
            """
            required: 0.0
            optional:
            """
        )

    @xfail_with_pep_563
    def when_nested_dataclass_is_none(expect):
        @datafile
        class Name:
            value: str

        @datafile("../tmp/samples/{self.key}.yml")
        class Sample:

            key: int
            name: Optional[Name]
            value: float = 0.0

        sample = Sample(42, None)

        expect(read("tmp/samples/42.yml")) == dedent(
            """
            name:
            """
        )


def describe_defaults():
    def with_custom_values(expect):
        sample = SampleWithDefaults("a", "b")

        sample.datafile.save()

        expect(read("tmp/sample.yml")) == dedent(
            """
            without_default: a
            with_default: b
            """
        )

    def with_default_values(expect):
        sample = SampleWithDefaults("a")

        sample.datafile.save()

        expect(read("tmp/sample.yml")) == dedent(
            """
            without_default: a
            """
        )

    def with_default_values_and_full_save(expect):
        sample = SampleWithDefaults("a", "foo")

        sample.datafile.save(include_default_values=True)

        expect(read("tmp/sample.yml")) == dedent(
            """
            without_default: a
            with_default: foo
            """
        )


def describe_preservation():
    def with_extra_lines(expect):
        sample = SampleWithOptionals(1, 2)

        write(
            "tmp/sample.yml",
            """
            required: 1.0

            optional: 2.0
            """,
        )

        sample.datafile.load()
        sample.optional = 3
        sample.datafile.save()

        expect(read("tmp/sample.yml")) == dedent(
            """
            required: 1.0

            optional: 3.0
            """
        )

    def with_comments(expect):
        sample = SampleWithOptionals(1, 2)

        write(
            "tmp/sample.yml",
            """
            # Header
            required: 1.0       # Line
            optional: 2.0
            """,
        )

        sample.datafile.load()
        sample.required = 3
        sample.datafile.save()

        expect(read("tmp/sample.yml")) == dedent(
            """
            # Header
            required: 3.0       # Line
            optional: 2.0
            """
        )

    def with_comments_in_nested_objects(expect):
        sample = SampleWithNestingAndDefaults(None)

        write(
            "tmp/sample.yml",
            """
            # Header
            name: a
            score: 1.0      # Line

            nested:
              # Nested header
              name: n
              score: 2
            """,
        )

        sample.datafile.load()
        sample.score = 3
        sample.nested.score = 4
        sample.datafile.save()

        expect(read("tmp/sample.yml")) == dedent(
            """
            # Header
            name: a
            score: 3.0      # Line

            nested:
              # Nested header
              name: n
              score: 4.0
            """
        )

    def with_comments_on_nested_lines(expect):
        sample = SampleWithNestingAndDefaults(None)

        write(
            "tmp/sample.yml",
            """
            # Header
            name: a
            score: 1        # Line

            nested:
              # Nested header
              name: n
              score: 2      # Nested line
            """,
        )

        sample.datafile.load()
        sample.score = 3
        sample.nested.score = 4
        sample.datafile.save()

        expect(read("tmp/sample.yml")) == dedent(
            """
            # Header
            name: a
            score: 3.0      # Line

            nested:
              # Nested header
              name: n
              score: 4.0    # Nested line
            """
        )

    @pytest.mark.xfail(reason="https://github.com/jacebrowning/datafiles/issues/171")
    def with_comments_on_list_items(expect):
        sample = SampleWithListOfDataclasses()

        write(
            "tmp/sample.yml",
            """
            # Header

            items:  # Subheader

              # Section

              - name: a     # Item
                score: 1

              # Section

              - name: b     # Item
                score: 2
            """,
        )

        sample.datafile.load()
        sample.items[1].name = "c"
        sample.datafile.save()

        expect(read("tmp/sample.yml")) == dedent(
            """
            # Header

            items:  # Subheader

              # Section

              - name: a     # Item
                score: 1

              # Section

              - name: c     # Item
                score: 2
            """
        )

    def with_quotes(expect):
        @datafile("../tmp/sample.yml", manual=True)
        class Sample:
            s1: str = ""
            s2: str = ""
            s3: str = ""

        sample = Sample()

        write(
            "tmp/sample.yml",
            """
            s1: a
            s2: 'b'
            s3: "c"
            """,
        )

        sample.datafile.load()
        sample.s1 = "d"
        sample.s2 = "e"
        sample.s3 = "f"
        sample.datafile.save()

        expect(read("tmp/sample.yml")) == dedent(
            """
            s1: d
            s2: 'e'
            s3: "f"
            """
        )
