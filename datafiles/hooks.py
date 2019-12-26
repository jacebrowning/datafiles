import dataclasses
from contextlib import contextmanager, suppress
from functools import wraps

import log

from . import settings
from .mapper import create_mapper


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


def apply(instance, mapper):
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
            attr.datafile = create_mapper(attr, root=mapper)
            apply(attr, mapper)


def load_before(cls, method):
    """Decorate methods that should load before call."""

    if hasattr(method, FLAG):
        return method

    @wraps(method)
    def wrapped(self, *args, **kwargs):
        __tracebackhide__ = settings.HIDE_TRACEBACK_IN_HOOKS

        mapper = get_mapper(self)
        if enabled(mapper, args):
            if mapper.exists and mapper.modified:
                log.debug(f"Loading automatically before '{method.__name__}' call")
                mapper.load()
                if mapper.auto_save:
                    log.debug("Saving automatically after load")
                    mapper.save(_log=False)

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

        mapper = get_mapper(self)
        if enabled(mapper, args):
            if mapper.exists and mapper.modified:
                log.debug(f"Loading automatically before '{method.__name__}' call")
                mapper.load()

        result = method(self, *args, **kwargs)

        if enabled(mapper, args):
            log.debug(f"Saving automatically after '{method.__name__}' call")
            mapper.save()
            if mapper.auto_load:
                log.debug("Loading automatically after save")
                mapper.load(_log=False)

        return result

    log.debug(f'Patched method to save after call: {cls.__name__}.{method.__name__}')
    setattr(wrapped, FLAG, True)

    return wrapped


def get_mapper(obj):
    try:
        return object.__getattribute__(obj, 'datafile')
    except AttributeError:
        return None


def enabled(mapper, args) -> bool:
    """Determine if hooks are enabled for the current method."""
    if not settings.HOOKS_ENABLED:
        return False

    if mapper is None:
        return False

    if mapper.manual:
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
    enabled = settings.HOOKS_ENABLED
    if enabled:
        settings.HOOKS_ENABLED = False
    try:
        yield
    finally:
        settings.HOOKS_ENABLED = enabled
