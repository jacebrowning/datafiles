import dataclasses
from contextlib import contextmanager, suppress
from functools import wraps

import log


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


ENABLED = True
HIDE = True

FLAG = '_patched_method'


def enable(instance, datafile, get_datafile):
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

    for name in instance.datafile.attrs:
        attr = getattr(instance, name)
        if dataclasses.is_dataclass(attr):
            if not hasattr(attr, 'datafile'):
                attr.datafile = get_datafile(attr)
            enable(attr, datafile, get_datafile)


@contextmanager
def disabled():
    global ENABLED
    if ENABLED:
        ENABLED = False
        yield
        ENABLED = True
    else:
        yield


def load_before(cls, method, datafile):
    """Decorate methods that should load before call."""

    name = method.__name__
    log.debug(f'Patching method to load before call: {cls.__name__}.{name}')

    @wraps(method)
    def wrapped(self, *args, **kwargs):
        __tracebackhide__ = HIDE  # pylint: disable=unused-variable

        if ENABLED and external_method_call(method.__name__, args):
            if datafile.manual:
                log.debug('Automatic loading is disabled')
            elif datafile.exists and datafile.modified:
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
        __tracebackhide__ = HIDE  # pylint: disable=unused-variable

        if ENABLED and external_method_call(method.__name__, args):
            if datafile.exists and datafile.modified:
                log.debug(f"Loading modified datafile before '{name}' call")
                with disabled():
                    datafile.load()

        result = method(self, *args, **kwargs)

        if ENABLED and external_method_call(method.__name__, args):
            if datafile.manual:
                log.debug(f'Automatic saving is disabled')
            else:
                log.debug(f"Saving automatically after '{name}' call")
                with disabled():
                    datafile.save()

        return result

    return wrapped


def external_method_call(name, args):
    """Determine if a call accesses private attributes or variables."""

    if name in {'__init__', '__post_init__'}:
        return False

    if args and args[0] in {'Meta', 'datafile', '_datafile'}:
        return False

    if name in {'__getattribute__', '__setattr__'}:
        return not args[0].startswith('_')

    return True
