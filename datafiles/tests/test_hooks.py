# pylint: disable=unused-variable,unsubscriptable-object

from typing import List

import datafiles
from datafiles import datafile, field, hooks, settings


@datafile
class Item:
    name: str


@datafile
class Sample:
    key: int = 1
    items: List[Item] = field(default_factory=list)


def describe_apply():
    def it_can_be_called_twice(expect, mocker):
        instance = Sample()
        setattr(instance, "datafile", mocker.MagicMock(attrs=["key", "items"]))

        hooks.apply(instance, None)
        expect(hasattr(instance.__setattr__, "_patched")).is_(True)

        hooks.apply(instance, None)
        expect(hasattr(instance.__setattr__, "_patched")).is_(True)

    def it_patches_list_elements(expect, mocker):
        instance = Sample(items=[Item("a"), Item("b")])
        setattr(instance, "datafile", mocker.MagicMock(attrs=["key", "items"]))

        hooks.apply(instance, None)
        expect(hasattr(instance.items[0].__setattr__, "_patched")).is_(True)


def describe_disabled():
    def when_nested(expect):
        expect(settings.HOOKS_ENABLED).is_(True)

        with hooks.disabled():
            expect(settings.HOOKS_ENABLED).is_(False)

            with hooks.disabled():
                expect(settings.HOOKS_ENABLED).is_(False)

            expect(settings.HOOKS_ENABLED).is_(False)

        expect(settings.HOOKS_ENABLED).is_(True)

    def with_alias(expect):
        expect(settings.HOOKS_ENABLED).is_(True)

        with datafiles.frozen():
            expect(settings.HOOKS_ENABLED).is_(False)

        expect(settings.HOOKS_ENABLED).is_(True)
