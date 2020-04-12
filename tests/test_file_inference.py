from datafiles import auto
from datafiles.utils import dedent, logbreak, read, write


def test_auto_with_sample_file(expect):
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

    logbreak("Updating attribute")
    sample.homogeneous_list.append(3.4)
    sample.heterogeneous_list.append(5.6)
    sample.empty_list.append(7.8)

    logbreak("Reading file")
    expect(read('tmp/sample.yml')) == dedent(
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


def test_float_inference(expect):
    write(
        'tmp/sample.yml',
        """
        language: python
        python:
          - 3.7
          - 3.8
        """,
    )

    logbreak("Inferring object")
    sample = auto('tmp/sample.yml')

    logbreak("Updating attribute")
    sample.python.append(4)

    logbreak("Reading file")
    expect(read('tmp/sample.yml')) == dedent(
        """
        language: python
        python:
          - 3.7
          - 3.8
          - 4.0
        """
    )
