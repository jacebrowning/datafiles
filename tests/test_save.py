# pylint: disable=unused-variable
import pytest


def describe_nominal():
    @pytest.fixture
    def sample(Sample):
        return Sample(None, None, None, None)

    def without_initial_values(sample, expect, dedent):
        sample.datafile.save()

        with open('tmp/sample.yml') as f:
            expect(f.read()) == dedent(
                """
                bool_: false
                int_: 0
                float_: 0.0
                str_: ''
                """
            )

    def with_convertable_initial_values(Sample, expect, dedent):
        sample = Sample(1, 2, 3, 4)

        sample.datafile.save()

        with open('tmp/sample.yml') as f:
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

        with open('tmp/sample.yml') as f:
            expect(f.read()).excludes('extra')

    def with_custom_fields(SampleWithCustomFields, expect, dedent):
        sample = SampleWithCustomFields('foo', 'bar')

        sample.datafile.save()

        with open('tmp/sample.yml') as f:
            expect(f.read()) == dedent(
                """
                included: foo
                """
            )


def describe_lists():
    def with_conversion(SampleWithList, expect, dedent):
        sample = SampleWithList([1, 2.3, '4.5'])

        sample.datafile.save()

        with open('tmp/sample.yml') as f:
            expect(f.read()) == dedent(
                """
                items:
                - 1.0
                - 2.3
                - 4.5
                """
            )


def describe_nesting():
    def without_initial_values(SampleWithNesting, expect, dedent):
        sample = SampleWithNesting(None, None, None)

        sample.datafile.save()

        with open('tmp/sample.yml') as f:
            expect(f.read()) == dedent(
                """
                name: ''
                score: 0.0
                nested:
                  name: ''
                  score: 0.0
                """
            )

    def with_initial_values(SampleWithNesting, expect, dedent):
        sample = SampleWithNesting('foo', 1.2, {'name': 'bar', 'score': 3.4})

        sample.datafile.save()

        with open('tmp/sample.yml') as f:
            expect(f.read()) == dedent(
                """
                name: foo
                score: 1.2
                nested:
                  name: bar
                  score: 3.4
                """
            )

    def with_default_values(SampleWithNestingAndDefaults, expect, dedent):
        sample = SampleWithNestingAndDefaults('a')

        sample.datafile.save()

        with open('tmp/sample.yml') as f:
            expect(f.read()) == dedent(
                """
                name: a
                nested: {}
                """
            )

    def with_missing_keys(SampleWithNesting, expect, dedent):
        sample = SampleWithNesting('foo', 1.2, {'name': 'bar'})

        sample.datafile.save()

        with open('tmp/sample.yml') as f:
            expect(f.read()) == dedent(
                """
                name: foo
                score: 1.2
                nested:
                  name: bar
                  score: 0.0
                """
            )

    def when_manually_setting_none(SampleWithNesting, expect, dedent):
        sample = SampleWithNesting('foo', 1.2, {'name': 'bar', 'score': 3.4})
        sample.nested = None

        sample.datafile.save()

        with open('tmp/sample.yml') as f:
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
    def with_values(SampleWithOptionals, expect, read, dedent):
        sample = SampleWithOptionals(1, 2)

        sample.datafile.save()

        expect(read('tmp/sample.yml')) == dedent(
            """
            required: 1.0
            optional: 2.0
            """
        )

    def with_nones(SampleWithOptionals, expect, read, dedent):
        sample = SampleWithOptionals(None, None)

        sample.datafile.save()

        expect(read('tmp/sample.yml')) == dedent(
            """
            required: 0.0
            optional:
            """
        )


def describe_defaults():
    def with_custom_values(SampleWithDefaults, expect, read, dedent):
        sample = SampleWithDefaults('a', 'b')

        sample.datafile.save()

        expect(read('tmp/sample.yml')) == dedent(
            """
            without_default: a
            with_default: b
            """
        )

    def with_default_values(SampleWithDefaults, expect, read, dedent):
        sample = SampleWithDefaults('a')

        sample.datafile.save()

        expect(read('tmp/sample.yml')) == dedent(
            """
            without_default: a
            """
        )

    def with_default_values_and_full_save(
        SampleWithDefaults, expect, read, dedent
    ):
        sample = SampleWithDefaults('a', 'foo')

        sample.datafile.save(include_default_values=True)

        expect(read('tmp/sample.yml')) == dedent(
            """
            without_default: a
            with_default: foo
            """
        )


def describe_preservation():
    def with_extra_lines(SampleWithOptionals, write, expect, read, dedent):
        sample = SampleWithOptionals(1, 2)

        write(
            'tmp/sample.yml',
            """
            required: 1.0

            optional: 2.0
            """,
        )

        sample.datafile.load()
        sample.optional = 3
        sample.datafile.save()

        expect(read('tmp/sample.yml')) == dedent(
            """
            required: 1.0

            optional: 3.0
            """
        )

    def with_comments(SampleWithOptionals, write, expect, read, dedent):
        sample = SampleWithOptionals(1, 2)

        write(
            'tmp/sample.yml',
            """
            # Heading
            required: 1.0  # Line
            optional: 2.0
            """,
        )

        sample.datafile.load()
        sample.required = 3
        sample.datafile.save()

        expect(read('tmp/sample.yml')) == dedent(
            """
            # Heading
            required: 3.0  # Line
            optional: 2.0
            """
        )

    def with_comments_in_nested_objects(
        SampleWithNestingAndDefaults, write, expect, read, dedent
    ):
        sample = SampleWithNestingAndDefaults(None)

        write(
            'tmp/sample.yml',
            """
            # Heading
            name: a
            score: 1.0  # Line

            nested:
              # Nested heading
              name: n
              score: 2
            """,
        )

        sample.datafile.load()
        sample.score = 3
        sample.nested.score = 4
        sample.datafile.save()

        expect(read('tmp/sample.yml')) == dedent(
            """
            # Heading
            name: a
            score: 3.0  # Line

            nested:
              # Nested heading
              name: n
              score: 4.0
            """
        )

    @pytest.mark.xfail
    def with_comments_on_nested_lines(
        SampleWithNestingAndDefaults, write, expect, read, dedent
    ):
        sample = SampleWithNestingAndDefaults(None)

        write(
            'tmp/sample.yml',
            """
            # Heading
            name: a
            score: 1  # Line

            nested:
              # Nested heading
              name: n
              score: 2  # Nested line
            """,
        )

        sample.datafile.load()
        sample.score = 3
        sample.nested.score = 4
        sample.datafile.save()

        expect(read('tmp/sample.yml')) == dedent(
            """
            # Heading
            name: a
            score: 3.0  # Line

            nested:
              # Nested heading
              name: n
              score: 4.0  # Nested line
            """
        )
