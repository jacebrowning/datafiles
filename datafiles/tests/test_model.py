# pylint: disable=unused-variable

from datafiles import model


def describe_create_model():
    def it_requires_dataclass(expect):
        class NonDataclass:
            pass

        with expect.raises(ValueError):
            model.create_model(NonDataclass)
