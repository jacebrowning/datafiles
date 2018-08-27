# pylint: disable=unused-variable


def describe_save():
    def with_defaults(sample, expect, dedent):
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
