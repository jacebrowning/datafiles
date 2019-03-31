import dataclasses
from contextlib import contextmanager, suppress
from functools import wraps

import log

from . import settings
from .builders import build_datafile


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
    """Patchable `list` type."""


class Dict(dict):
    """Patchable `dict` type."""


def apply(instance, datafile):
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

    if dataclasses.is_dataclass(instance):
        for attr_name in instance.datafile.attrs:
            attr = getattr(instance, attr_name)
            if not dataclasses.is_dataclass(attr):
                # pylint: disable=unidiomatic-typecheck
                if type(attr) == list:
                    attr = List(attr)
                    setattr(instance, attr_name, attr)
                elif type(attr) == dict:
                    attr = Dict(attr)
                    setattr(instance, attr_name, attr)
                else:
                    continue
            attr.datafile = build_datafile(attr, root=datafile)
            apply(attr, datafile)


def load_before(cls, method):
    """Decorate methods that should load before call."""

    if hasattr(method, FLAG):
        return method

    @wraps(method)
    def wrapped(self, *args, **kwargs):
        __tracebackhide__ = settings.HIDE_TRACEBACK_IN_HOOKS

        datafile = get_datafile(self)
        if enabled(datafile, args):
            if datafile.exists and datafile.modified:
                log.debug(f"Loading automatically before '{method.__name__}' call")
                datafile.load()
                if datafile.auto_save:
                    log.debug("Saving automatically after load")
                    datafile.save(_log=False)

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

        datafile = get_datafile(self)
        if enabled(datafile, args):
            if datafile.exists and datafile.modified:
                log.debug(f"Loading automatically before '{method.__name__}' call")
                datafile.load()

        result = method(self, *args, **kwargs)

        if enabled(datafile, args):
            log.debug(f"Saving automatically after '{method.__name__}' call")
            datafile.save()
            if datafile.auto_load:
                log.debug("Loading automatically after save")
                datafile.load(_log=False)

        return result

    log.debug(f'Patched method to save after call: {cls.__name__}.{method.__name__}')
    setattr(wrapped, FLAG, True)

    return wrapped


def get_datafile(obj):
    try:
        return object.__getattribute__(obj, 'datafile')
    except AttributeError:
        return None


def enabled(datafile, args) -> bool:
    """Determine if hooks are enabled for the current method."""
    if not settings.HOOKS_ENABLED:
        return False

    if datafile is None:
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
