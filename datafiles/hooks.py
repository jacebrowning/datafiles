import dataclasses
from contextlib import contextmanager, suppress
from functools import wraps
from types import new_class

import log

from . import settings


LOAD_BEFORE_METHODS = ['__getattribute__', '__getitem__', '__iter__']
SAVE_AFTER_METHODS = [
    '__setattr__',
    '__setitem__',
    '__delitem__',
    'append',
    'extend',
    'insert',
    'remove',
    'pop',
    'clear',
    'sort',
    'reverse',
    'popitem',
    'update',
]


def apply(instance, datafile, get_datafile):
    """Path methods that get or set attributes."""
    cls = instance.__class__

    for name in LOAD_BEFORE_METHODS:
        with suppress(AttributeError):
            method = getattr(cls, name)
            modified_method = load_before(cls, method, datafile)
            setattr(cls, name, modified_method)

    for name in SAVE_AFTER_METHODS:
        with suppress(AttributeError):
            method = getattr(cls, name)
            modified_method = save_after(cls, method, datafile)
            setattr(cls, name, modified_method)

    if hasattr(instance, 'datafile'):
        for name in instance.datafile.attrs:
            attr = getattr(instance, name)
            if dataclasses.is_dataclass(attr):
                apply(attr, datafile, get_datafile)
            elif type(attr) == list:  # pylint: disable=unidiomatic-typecheck
                attr = new_class('List', (list,))(attr)
                setattr(instance, name, attr)
                apply(attr, datafile, get_datafile)


def load_before(cls, method, datafile):
    """Decorate methods that should load before call."""

    name = method.__name__
    log.debug(f'Patching method to load before call: {cls.__name__}.{name}')

    @wraps(method)
    def wrapped(self, *args, **kwargs):
        __tracebackhide__ = settings.HIDE_TRACEBACK_IN_HOOKS

        if enabled(datafile, args):
            if datafile.exists and datafile.modified:
                log.debug(f"Loading automatically before '{name}' call")

                with disabled():
                    datafile.load()
                    datafile.modified = False
                    # TODO: Implement this?
                    # if mapper.auto_save_after_load:
                    #     mapper.save()
                    #     mapper.modified = False

        return method(self, *args, **kwargs)

    return wrapped


def save_after(cls, method, datafile):
    """Decorate methods that should save after call."""

    name = method.__name__
    log.debug(f'Patching method to save after call: {cls.__name__}.{name}')

    @wraps(method)
    def wrapped(self, *args, **kwargs):
        __tracebackhide__ = settings.HIDE_TRACEBACK_IN_HOOKS

        if enabled(datafile, args):
            if datafile.exists and datafile.modified:
                log.debug(f"Loading modified datafile before '{name}' call")
                with disabled():
                    datafile.load()

        result = method(self, *args, **kwargs)

        if enabled(datafile, args):
            log.debug(f"Saving automatically after '{name}' call")
            with disabled():
                datafile.save()

        return result

    return wrapped


def enabled(datafile, args) -> bool:
    """Determine if hooks are enabled for the current method."""
    if not settings.HOOKS_ENABLED:
        return False

    if datafile.manual:
        return False

    if args and args[0] in {'Meta', 'datafile'}:
        return False

    if args and isinstance(args[0], str) and args[0].startswith('_'):
        return False

    return True


@contextmanager
def disabled():
    """Globally disable method hooks, temporarily."""
    if settings.HOOKS_ENABLED:
        settings.HOOKS_ENABLED = False
        yield
        settings.HOOKS_ENABLED = True
    else:
        yield
