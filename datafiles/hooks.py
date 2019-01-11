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
    log.debug(f'Patching methods on {cls}')

    for method_name in LOAD_BEFORE_METHODS:
        with suppress(AttributeError):
            method = getattr(cls, method_name)
            modified_method = load_before(cls, method, datafile)
            setattr(cls, method_name, modified_method)

    for method_name in SAVE_AFTER_METHODS:
        with suppress(AttributeError):
            method = getattr(cls, method_name)
            modified_method = save_after(cls, method, datafile)
            setattr(cls, method_name, modified_method)

    if dataclasses.is_dataclass(instance):
        for attr_name in instance.datafile.attrs:
            attr = getattr(instance, attr_name)
            if dataclasses.is_dataclass(attr):
                attr.datafile = get_datafile(attr)
                apply(attr, datafile, get_datafile)
            elif type(attr) == list:  # pylint: disable=unidiomatic-typecheck
                attr = new_class(f'list:{attr_name}', (list,))(attr)
                setattr(instance, attr_name, attr)
                apply(attr, datafile, get_datafile)
            elif type(attr) == dict:  # pylint: disable=unidiomatic-typecheck
                attr = new_class(f'dict:{attr_name}', (dict,))(attr)
                setattr(instance, attr_name, attr)
                apply(attr, datafile, get_datafile)


def load_before(cls, method, datafile):
    """Decorate methods that should load before call."""

    @wraps(method)
    def wrapped(self, *args, **kwargs):
        __tracebackhide__ = settings.HIDE_TRACEBACK_IN_HOOKS

        if enabled(datafile, args):
            if datafile.exists and datafile.modified:
                log.debug(f"Loading automatically before '{method.__name__}' call")

                with disabled():
                    datafile.load()
                    datafile.modified = False
                    # TODO: Implement this?
                    # if mapper.auto_save_after_load:
                    #     mapper.save()
                    #     mapper.modified = False

        return method(self, *args, **kwargs)

    log.debug(f'Patched method to load before call: {cls.__name__}.{method.__name__}')

    return wrapped


def save_after(cls, method, datafile):
    """Decorate methods that should save after call."""

    @wraps(method)
    def wrapped(self, *args, **kwargs):
        __tracebackhide__ = settings.HIDE_TRACEBACK_IN_HOOKS

        if enabled(datafile, args):
            if datafile.exists and datafile.modified:
                log.debug(f"Loading automatically before '{method.__name__}' call")
                with disabled():
                    datafile.load()

        result = method(self, *args, **kwargs)

        if enabled(datafile, args):
            log.debug(f"Saving automatically after '{method.__name__}' call")
            with disabled():
                datafile.save()

        return result

    log.debug(f'Patched method to save after call: {cls.__name__}.{method.__name__}')

    return wrapped


def enabled(datafile, args) -> bool:
    """Determine if hooks are enabled for the current method."""
    if not settings.HOOKS_ENABLED:
        return False

    if datafile.manual:
        return False

    if args and isinstance(args[0], str):
        if args[0] in {'Meta', 'datafile'}:
            return False
        if args[0].startswith('_'):
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
