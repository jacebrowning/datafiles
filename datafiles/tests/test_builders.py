# pylint: disable=unused-variable

from datafiles.builders import build_datafile


def describe_build_datafile():
    def it_reuses_existing_datafile(mocker, expect):
        obj = mocker.Mock()
        datafile = mocker.Mock()
        obj.datafile = datafile

        new_datafile = build_datafile(obj)

        expect(new_datafile) == obj.datafile
