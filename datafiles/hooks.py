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


def patch_methods(instance):
    log.debug("Patching methods on: %r", instance)
    cls = instance.__class__

    for name in LOAD_BEFORE_METHODS:
        try:
            method = getattr(cls, name)
        except AttributeError:
            log.debug("No method: %s", name)
        else:
            modified_method = load_before(method)
            setattr(cls, name, modified_method)
            log.debug("Patched to load before call: %s", name)

    # for name in SAVE_AFTER_METHODS:
    #     try:
    #         method = getattr(cls, name)
    #     except AttributeError:
    #         log.trace("No method: %s", name)
    #     else:
    #         modified_method = save_after(method)
    #         setattr(cls, name, modified_method)
    #         log.trace("Patched to save after call: %s", name)


def load_before(method):
    """Decorate methods that should load before call."""

    if getattr(method, '_patched', False):
        return method

    log.debug(f"Patching '{method.__name__}' to load automatically")

    @wraps(method)
    def wrapped(self, *args, **kwargs):
        __tracebackhide__ = True  # pylint: disable=unused-variable

        if not private_call(method, args):
            datafile = object.__getattribute__(self, 'datafile')
            if datafile.exists and datafile.modified:
                log.debug(
                    f"Loading automatically before '{method.__name__}' call"
                )
                datafile.load()
                datafile.modified = False
                # if mapper.auto_save_after_load:
                #     mapper.save()
                #     mapper.modified = False

        return method(self, *args, **kwargs)

    setattr(wrapped, '_patched', True)

    return wrapped


def private_call(method, args):
    """Determine if a call's first argument is a private variable name."""
    if method.__name__ in ('__getattribute__', '__setattr__'):
        assert isinstance(args[0], str)
        if args[0] == 'Meta':
            return True
        return args[0].startswith('_')
    return False
