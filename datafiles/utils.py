"""Internal helper functions."""

from contextlib import suppress
from functools import lru_cache
from pathlib import Path
from pprint import pformat
from shutil import get_terminal_size
from typing import Any, Dict, Union

import log


cached = lru_cache()


def prettify(value: Any) -> str:
    """Ensure value is a dictionary pretty-format it."""
    return pformat(dictify(value))


def dictify(value: Any) -> Dict:
    """Ensure value is a dictionary."""
    with suppress(AttributeError):
        return {k: dictify(v) for k, v in value.items()}

    if isinstance(value, str):
        return value  # type: ignore

    with suppress(TypeError):
        return [dictify(x) for x in value]  # type: ignore

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


def write(filename_or_path: Union[str, Path], text: str) -> None:
    """Write text to a given file with logging."""
    if isinstance(filename_or_path, Path):
        path = filename_or_path
    else:
        path = Path(filename_or_path).resolve()
        text = dedent(text)

    message = f'Writing file: {path}'
    log.debug(message)
    line = '=' * len(message)
    if text:
        content = text.replace(' \n', '␠\n')
    else:
        content = '∅\n'
    log.debug(line + '\n' + content + line)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def read(filename: str) -> str:
    """Read text from a file with logging."""
    path = Path(filename).resolve()
    message = f'Reading file: {path}'
    log.info(message)
    line = '=' * len(message)
    text = path.read_text()
    if text:
        content = text.replace(' \n', '␠\n')
    else:
        content = '∅\n'
    log.debug(line + '\n' + content + line)
    return text


def display(path: Path, data: Dict) -> None:
    """Display data read from a file."""
    message = f'Data from file: {path}'
    log.debug(message)
    line = '=' * len(message)
    log.debug(line + '\n' + prettify(data) + '\n' + line)


def logbreak(message: str = "") -> None:
    """Insert a noticeable logging record for debugging."""
    width = get_terminal_size().columns - 31
    if message:
        line = '-' * (width - len(message) - 1) + ' ' + message
    else:
        line = '-' * width
    log.info(line)
