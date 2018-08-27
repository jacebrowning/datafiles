# pylint: disable=unused-variable


def describe_load():
    def with_matching_types(Sample, dedent, expect):
        sample = Sample(None, None, None, None)

        with open('tmp/sample.yml', 'w') as f:
            f.write(
                dedent(
                    """
                    bool_: true
                    int_: 1
                    float_: 2.3
                    str_: 'foobar'
                    """
                )
            )

        sample.datafile.load()

        expect(sample.bool_) == True
        expect(sample.int_) == 1
        expect(sample.float_) == 2.3
        expect(sample.str_) == 'foobar'

    def with_convertable_types(Sample, dedent, expect):
        sample = Sample(None, None, None, None)

        with open('tmp/sample.yml', 'w') as f:
            f.write(
                dedent(
                    """
                    bool_: 1
                    int_: 2
                    float_: 3
                    str_: 4
                    """
                )
            )

        sample.datafile.load()

        expect(sample.bool_) == True
        expect(sample.int_) == 2
        expect(sample.float_) == 3.0
        expect(sample.str_) == '4'
