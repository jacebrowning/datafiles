from datafiles import auto


def test_auto(write, logbreak, expect):

    write(
        'tmp/sample.yml',
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
    sample = auto('tmp/sample.yml')

    logbreak("Reading attributes")
    expect(sample.homogeneous_list) == [1, 2]
    expect(sample.heterogeneous_list) == [1, 'abc']
    expect(sample.empty_list) == []
