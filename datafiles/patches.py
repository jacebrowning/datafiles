from functools import wraps

import log


LOAD_BEFORE_METHODS = [
    # '__getattribute__',
    '__iter__',
    '__getitem__',
]

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


def patch_load(obj):
    cls = obj.__class__
    for name in LOAD_BEFORE_METHODS:
        try:
            method = getattr(cls, name)
        except AttributeError:
            continue

        if getattr(method, '_patched', False):
            return

        log.debug(f"Patching '{name}' to load automatically")

        @wraps(method)
        def patched_method(self, *args, **kwargs):
            # pylint: disable=unused-variable,cell-var-from-loop
            # __tracebackhide__ = True
            # object.__getattribute__(self, 'datafile').load()
            log.debug(f"Loading automatically before '{method.__name__}' call")
            self.datafile.load()
            return method(self, *args, **kwargs)

        setattr(patched_method, '_patched', True)

        setattr(cls, name, patched_method)
