from contextlib import suppress
from functools import lru_cache
from pprint import pformat
from typing import Any, Dict


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


def recursive_update(old: Dict, new: Dict):
    """Recursively update a dictionary."""

    for key, value in new.items():
        if isinstance(value, dict):
            if key in old:
                recursive_update(old[key], value)
            else:
                old[key] = value
        elif isinstance(value, list):
            if key in old:
                old[key][:] = value
            else:
                old[key] = value
        else:
            old[key] = value

    return old
