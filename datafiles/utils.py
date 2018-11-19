import dataclasses
from contextlib import suppress
from functools import wraps
from pprint import pformat
from typing import Any, Dict

import log


Missing = dataclasses._MISSING_TYPE  # pylint: disable=protected-access


def prettify(data: Dict) -> str:
    return pformat(dictify(data))


def dictify(value: Any) -> Dict:
    with suppress(AttributeError):
        return {k: dictify(v) for k, v in value.items()}

    if isinstance(value, str):
        return value

    with suppress(TypeError):
        return [dictify(x) for x in value]

    return value


def prevent_recursion(method):
    """Decorate methods to prevent indirect recursive calls."""

    @wraps(method)
    def wrapped(self, *args, **kwargs):

        if getattr(self, '_activity', False):
            log.debug(f"Skipped recursive '{method.__name__}' method call")
            return None

        setattr(self, '_activity', True)

        result = method(self, *args, **kwargs)

        delattr(self, '_activity')

        return result

    return wrapped
