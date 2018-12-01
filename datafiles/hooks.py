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

FLAG = '_patched'
ENABLED = True


def enable(instance):
    """Path methods that get or set attributes."""
    cls = instance.__class__

    if getattr(cls, FLAG, False):
        return

    log.debug(f'Patching methods on {cls}')

    for name in LOAD_BEFORE_METHODS:
        with suppress(AttributeError):
            method = getattr(cls, name)
            modified_method = load_before(method)
            setattr(cls, name, modified_method)

    for name in SAVE_AFTER_METHODS:
        with suppress(AttributeError):
            method = getattr(cls, name)
            modified_method = save_after(method)
            setattr(cls, name, modified_method)

    setattr(cls, FLAG, True)


@contextmanager
def disabled():
    global ENABLED
    ENABLED = False
    yield
    ENABLED = True


def load_before(method):
    """Decorate methods that should load before call."""
    name = method.__name__
    log.debug(f'Patching method to load before call: {name}')

    @wraps(method)
    def wrapped(self, *args, **kwargs):
        __tracebackhide__ = True  # pylint: disable=unused-variable

        if ENABLED and external_method_call(method.__name__, args):
            datafile = object.__getattribute__(self, 'datafile')
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


def save_after(method):
    """Decorate methods that should save after call."""
    name = method.__name__
    log.debug(f'Patching method to save after call: {name}')

    @wraps(method)
    def wrapped(self, *args, **kwargs):
        __tracebackhide__ = True  # pylint: disable=unused-variable

        if ENABLED and external_method_call(method.__name__, args):
            datafile = object.__getattribute__(self, 'datafile')
            if datafile.exists and datafile.modified:
                log.debug(f"Loading modified datafile before '{name}' call")
                datafile.load()

        result = method(self, *args, **kwargs)

        if ENABLED and external_method_call(method.__name__, args):
            datafile = object.__getattribute__(self, 'datafile')
            if datafile.manual:
                log.debug(f'Automatic saving is disabled')
            else:
                log.debug(f"Saving automatically after '{name}' call")
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
