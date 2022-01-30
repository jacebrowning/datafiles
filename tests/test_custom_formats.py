from datafiles import datafile, formats


def test_registration(expect):

    formats.register(".conf", formats.JSON)

    @datafile("../tmp/sample.conf")
    class Sample:
        count: int

    sample = Sample(42)
    expect(sample.datafile.text) == '{\n  "count": 42\n}'
