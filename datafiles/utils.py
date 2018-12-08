import dataclasses
from contextlib import suppress
from functools import lru_cache, wraps
from pprint import pformat
from typing import Any, Dict


Missing = dataclasses._MISSING_TYPE  # pylint: disable=protected-access

cached = lru_cache()


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

    FLAG = '_activity'

    @wraps(method)
    def wrapped(self, *args, **kwargs):
        if getattr(self, FLAG, False):
            return None

        setattr(self, FLAG, True)
        try:
            return method(self, *args, **kwargs)
        finally:
            delattr(self, FLAG)

    return wrapped
