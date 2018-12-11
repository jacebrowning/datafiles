# pylint: disable=unused-variable

from datafiles import hooks, settings


def describe_disabled():
    def when_nested(expect):
        expect(settings.HOOKS_ENABLED) == True

        with hooks.disabled():
            expect(settings.HOOKS_ENABLED) == False

            with hooks.disabled():
                expect(settings.HOOKS_ENABLED) == False

            expect(settings.HOOKS_ENABLED) == False

        expect(settings.HOOKS_ENABLED) == True
