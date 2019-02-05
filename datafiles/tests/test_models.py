# pylint: disable=unused-variable

from datafiles.models import create_model


def describe_create_model():
    def it_requires_dataclass(expect):
        class NonDataclass:
            pass

        with expect.raises(ValueError):
            create_model(NonDataclass)
