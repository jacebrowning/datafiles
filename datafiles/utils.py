"""Internal helper functions."""

from contextlib import suppress
from functools import lru_cache
from pathlib import Path
from pprint import pformat
from shutil import get_terminal_size
from typing import Any, Dict

import log


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


def dedent(text: str) -> str:
    """Remove indentation from a multiline string."""
    text = text.strip('\n')
    indent = text.split('\n')[0].count('    ')
    return text.replace('    ' * indent, '')


def write(filename: str, text: str) -> None:
    """Write text to a file with logging."""
    path = Path(filename).resolve()
    text = dedent(text)
    message = f'Writing file: {path}'
    log.info(message)
    log.debug('=' * len(message) + '\n\n' + (text or '<nothing>\n'))
    path.write_text(text)


def read(filename: str) -> str:
    """Read text from a file with logging."""
    path = Path(filename).resolve()
    message = f'Reading file: {path}'
    log.info(message)
    text = path.read_text()
    log.debug('=' * len(message) + '\n\n' + (text or '<nothing>\n'))
    return text


def logbreak(message: str = "") -> None:
    """Insert a noticeable logging record for debugging."""
    width = get_terminal_size().columns - 31
    if message:
        line = '-' * (width - len(message) - 1) + ' ' + message
    else:
        line = '-' * width
    log.info(line)
