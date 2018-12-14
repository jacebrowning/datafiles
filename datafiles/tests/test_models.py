# pylint: disable=unused-variable

from datafiles.models import get_datafile


def describe_get_datafile():
    def it_reuses_existing_datafile(mocker, expect):
        obj = mocker.Mock()
        datafile = mocker.Mock()
        obj.datafile = datafile

        new_datafile = get_datafile(obj)

        expect(new_datafile) == obj.datafile
