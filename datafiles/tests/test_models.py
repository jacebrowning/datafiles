# pylint: disable=unused-variable

from datafiles.models import build_datafile, create_model


def describe_build_datafile():
    def it_reuses_existing_datafile(mocker, expect):
        obj = mocker.Mock()
        datafile = mocker.Mock()
        obj.datafile = datafile

        new_datafile = build_datafile(obj)

        expect(new_datafile) == obj.datafile


def describe_create_model():
    def it_requires_dataclass(expect):
        class NonDataclass:
            pass

        with expect.raises(ValueError):
            create_model(NonDataclass)
