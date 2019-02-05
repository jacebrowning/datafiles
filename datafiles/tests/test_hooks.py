# pylint: disable=unused-variable

from datafiles import hooks, settings


class Sample:
    foobar = 1


def describe_apply():
    def it_can_be_called_twice(mocker):
        instance = Sample()
        setattr(instance, 'datafile', mocker.Mock())

        hooks.apply(instance, None)
        hooks.apply(instance, None)


def describe_disabled():
    def when_nested(expect):
        expect(settings.HOOKS_ENABLED) == True

        with hooks.disabled():
            expect(settings.HOOKS_ENABLED) == False

            with hooks.disabled():
                expect(settings.HOOKS_ENABLED) == False

            expect(settings.HOOKS_ENABLED) == False

        expect(settings.HOOKS_ENABLED) == True
