import dataclasses
from contextlib import contextmanager, suppress
from functools import wraps

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
FLAG = '_patched'


class List(list):
    """Mutable `list` type."""


class Dict(dict):
    """Mutable `dict` type."""


def apply(instance, datafile, get_datafile):
    """Path methods that get or set attributes."""
    cls = instance.__class__
    log.debug(f'Patching methods on {cls}')

    for method_name in LOAD_BEFORE_METHODS:
        with suppress(AttributeError):
            method = getattr(cls, method_name)
            modified_method = load_before(cls, method)
            setattr(cls, method_name, modified_method)

    for method_name in SAVE_AFTER_METHODS:
        with suppress(AttributeError):
            method = getattr(cls, method_name)
            modified_method = save_after(cls, method)
            setattr(cls, method_name, modified_method)

    # pylint: disable=unidiomatic-typecheck,attribute-defined-outside-init
    if dataclasses.is_dataclass(instance):
        for attr_name in instance.datafile.attrs:
            attr = getattr(instance, attr_name)
            if dataclasses.is_dataclass(attr):
                attr.datafile = get_datafile(attr, root=datafile)
                apply(attr, datafile, get_datafile)
            elif type(attr) == list:
                attr = List(attr)
                attr.datafile = datafile
                setattr(instance, attr_name, attr)
                apply(attr, datafile, get_datafile)
            elif type(attr) == dict:
                attr = Dict(attr)
                attr.datafile = datafile
                setattr(instance, attr_name, attr)
                apply(attr, datafile, get_datafile)


def load_before(cls, method):
    """Decorate methods that should load before call."""

    if hasattr(method, FLAG):
        return method

    @wraps(method)
    def wrapped(self, *args, **kwargs):
        __tracebackhide__ = settings.HIDE_TRACEBACK_IN_HOOKS

        if settings.HOOKS_ENABLED:
            datafile = object.__getattribute__(self, 'datafile')
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
    setattr(wrapped, FLAG, True)

    return wrapped


def save_after(cls, method):
    """Decorate methods that should save after call."""

    if hasattr(method, FLAG):
        return method

    @wraps(method)
    def wrapped(self, *args, **kwargs):
        __tracebackhide__ = settings.HIDE_TRACEBACK_IN_HOOKS

        if settings.HOOKS_ENABLED:
            datafile = object.__getattribute__(self, 'datafile')
            if enabled(datafile, args):
                if datafile.exists and datafile.modified:
                    log.debug(f"Loading automatically before '{method.__name__}' call")
                    with disabled():  # TODO: remove redundancy
                        datafile.load()

        result = method(self, *args, **kwargs)

        if settings.HOOKS_ENABLED:
            datafile = object.__getattribute__(self, 'datafile')
            if enabled(datafile, args):
                log.debug(f"Saving automatically after '{method.__name__}' call")
                with disabled():
                    datafile.save()

        return result

    log.debug(f'Patched method to save after call: {cls.__name__}.{method.__name__}')
    setattr(wrapped, FLAG, True)

    return wrapped


def enabled(datafile, args) -> bool:
    """Determine if hooks are enabled for the current method."""
    if datafile.manual:
        return False

    # TODO: Investigate performance impact of removing this code
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
