# pylint: disable=unused-variable
import dataclasses

from datafiles import model


def describe_create_model():
    def it_requires_dataclass(expect):
        class NonDataclass:
            pass

        with expect.raises(ValueError):
            model.create_model(NonDataclass)

    def it_is_compatible_with_frozen_dataclass(expect):
        @dataclasses.dataclass(frozen=True)
        class FrozenDataclass:
            a: int

        frozen_model = model.create_model(FrozenDataclass)
        expect(hasattr(frozen_model, "Meta")).is_(True)
        expect(hasattr(frozen_model, "objects")).is_(True)
