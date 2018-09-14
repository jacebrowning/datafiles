from functools import wraps

import log


LOAD_BEFORE_METHODS = ['__getattribute__', '__iter__', '__getitem__']

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


def patch_load(obj, load):
    for name in LOAD_BEFORE_METHODS:
        try:
            method = getattr(obj, name)
        except AttributeError:
            continue

        if getattr(method, '_patched', False):
            return

        log.debug(f"Patching '{name}' to load automatically")

        @wraps(method)
        def patched_method(self, *args, **kwargs):
            __tracebackhide__ = True  # pylint: disable=unused-variable
            assert 0
            method(self, *args, **kwargs)  # pylint: disable=cell-var-from-loop
            load()

        setattr(patched_method, '_patched', True)

        setattr(obj, name, patched_method)
