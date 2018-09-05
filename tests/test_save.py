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

    def with_default_values(SampleWithNestingAndDefaultValues, expect, dedent):
        sample = SampleWithNestingAndDefaultValues('a')

        sample.datafile.save()

        with open('tmp/sample.yml') as f:
            expect(f.read()) == dedent(
                """
                name: a
                score: 1.2
                nested:
                  name: b
                  score: 3.4
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


def describe_lists():
    def with_conversion(SampleWithFloatList, expect, dedent):
        sample = SampleWithFloatList([1, 2.3, '4.5'])

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
