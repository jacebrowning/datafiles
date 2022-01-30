"""Internal helper functions."""

import dataclasses
import time
from contextlib import suppress
from functools import lru_cache
from pathlib import Path
from pprint import pformat
from shutil import get_terminal_size
from typing import Any, Dict, Union

import log

from . import settings
from .types import Missing

cached = lru_cache()


def subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in subclasses(c)]
    )


def get_default_field_value(instance, name):
    for field in dataclasses.fields(instance):
        if field.name == name:
            if not isinstance(field.default, Missing):
                return field.default

            if not isinstance(field.default_factory, Missing):  # type: ignore
                return field.default_factory()  # type: ignore

            if not field.init and hasattr(instance, "__post_init__"):
                return getattr(instance, name)

    return Missing


def prettify(value) -> str:
    """Ensure value is a dictionary pretty-format it."""
    return pformat(dictify(value))


def dictify(value):
    """Ensure value is a dictionary."""
    with suppress(AttributeError):
        return {k: dictify(v) for k, v in value.items()}

    if isinstance(value, str):
        return value

    with suppress(TypeError):
        return [dictify(x) for x in value]

    return value


def recursive_update(old: Dict, new: Dict) -> Dict:
    """Recursively update a dictionary, keeping equivalent objects."""
    return _merge(old, new)


def _merge(old: Any, new: Any) -> Any:
    if old is None:
        return new

    if isinstance(new, dict):
        for key, value in new.items():
            old[key] = _merge(old.get(key), value)

        for key in list(old.keys()):
            if key not in new:
                old.pop(key)

        return old

    if isinstance(new, list):
        for index, new_item in enumerate(new):
            try:
                old_item = old[index]
            except IndexError:
                old_item = None
                old.append(old_item)
            old[index] = _merge(old_item, new_item)

        while len(old) > len(new):
            old.pop()

        return old

    return new


def dedent(text: str) -> str:
    """Remove indentation from a multiline string."""
    text = text.strip("\n")
    indent = text.split("\n")[0].count("    ")
    return text.replace("    " * indent, "")


def write(filename_or_path: Union[str, Path], text: str, *, display=False) -> None:
    """Write text to a given file and optionally log it."""
    if isinstance(filename_or_path, Path):
        path = filename_or_path
    else:
        path = Path(filename_or_path).resolve()
        text = dedent(text)

    message = f"Writing file: {path}"
    line = "=" * (31 + len(message))
    if text:
        content = text.replace(" \n", "␠\n")
    else:
        content = "∅\n"
    if display:
        log.debug(message + "\n" + line + "\n" + content + line)
    else:
        log.critical(message)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    time.sleep(settings.WRITE_DELAY)  # ensure the file modification time changes


def read(filename: str, *, display=False) -> str:
    """Read text from a file and optionally log it."""
    path = Path(filename).resolve()
    message = f"Reading file: {path}"
    line = "=" * (31 + len(message))
    text = path.read_text()
    if text:
        content = text.replace(" \n", "␠\n")
    else:
        content = "∅\n"
    if display:
        log.debug(message + "\n" + line + "\n" + content + line)
    else:
        log.critical(message)
    return text


def display(path: Path, data: Dict) -> None:
    """Display data read from a file."""
    message = f"Data from file: {path}"
    line = "=" * (31 + len(message))
    content = prettify(data)
    log.debug(message + "\n" + line + "\n" + content + "\n" + line)


def logbreak(message: str = "") -> None:
    """Insert a noticeable logging record for debugging."""
    width = get_terminal_size().columns - 31
    if message:
        line = "-" * (width - len(message) - 1) + " " + message
    else:
        line = "-" * width
    log.critical(line)
