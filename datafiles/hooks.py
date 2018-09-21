from functools import wraps

import log


LOAD_BEFORE_METHODS = ['__getattribute__', '__getitem__', '__iter__']

SAVE_AFTER_METHODS = [
    # '__setattr__',
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


def patch_methods(instance):
    cls = instance.__class__
    log.debug(f'Patching methods on {cls}')

    for name in LOAD_BEFORE_METHODS:
        try:
            method = getattr(cls, name)
        except AttributeError:
            log.debug("No method: %s", name)
        else:
            modified_method = load_before(method)
            setattr(cls, name, modified_method)

    for name in SAVE_AFTER_METHODS:
        try:
            method = getattr(cls, name)
        except AttributeError:
            log.debug("No method: %s", name)
        else:
            modified_method = save_after(method)
            setattr(cls, name, modified_method)


def load_before(method):
    """Decorate methods that should load before call."""
    name = method.__name__

    if getattr(method, '_patched_load_before', False):
        log.debug(f'Already patched method to load before call: {name}')
        return method

    log.debug(f'Patching method to load before call: {name}')

    @wraps(method)
    def wrapped(self, *args, **kwargs):
        __tracebackhide__ = True  # pylint: disable=unused-variable

        if not private_call(method, args):
            datafile = object.__getattribute__(self, 'datafile')
            if datafile.exists and datafile.modified:
                log.debug(f"Loading automatically before '{name}' call")
                datafile.load()
                datafile.modified = False
                # if mapper.auto_save_after_load:
                #     mapper.save()
                #     mapper.modified = False

        return method(self, *args, **kwargs)

    setattr(wrapped, '_patched_load_before', True)

    return wrapped


def save_after(method):
    """Decorate methods that should save after call."""
    name = method.__name__

    if getattr(method, '_patched_save_after', False):
        log.debug(f'Already patched method to save after call: {name}')
        return method

    log.debug(f'Patching method to save after call: {name}')

    @wraps(method)
    def wrapped(self, *args, **kwargs):
        __tracebackhide__ = True  # pylint: disable=unused-variable

        result = method(self, *args, **kwargs)

        if not private_call(method, args):
            datafile = object.__getattribute__(self, 'datafile')
            log.debug(f"Saving automatically after '{name}' call")
            datafile.save()

        return result

    setattr(wrapped, '_patched_save_after', True)

    return wrapped


def private_call(method, args):
    """Determine if a call's first argument is a private variable name."""
    if method.__name__ in ('__getattribute__', '__setattr__'):
        assert isinstance(args[0], str)
        if args[0] == 'Meta':
            return True
        return args[0].startswith('_')
    return False
