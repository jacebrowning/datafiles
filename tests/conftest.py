import os
from pathlib import Path
from shutil import get_terminal_size, rmtree

import log
import pytest

from datafiles import settings


settings.HIDE_TRACEBACK_IN_HOOKS = False


xfail_on_ci = pytest.mark.xfail(bool(os.getenv('CI')), reason="Flaky on CI")


def pytest_configure(config):
    terminal = config.pluginmanager.getplugin('terminal')
    terminal.TerminalReporter.showfspath = False


def pytest_collection_modifyitems(items):
    for item in items:
        for marker in item.iter_markers():
            if marker.name == 'flaky':
                item.add_marker(xfail_on_ci)


@pytest.fixture(autouse=True)
def create_tmp():
    path = Path('tmp')
    if path.exists():
        rmtree(path)
    path.mkdir(exist_ok=True)


@pytest.fixture
def logbreak():
    def _(message=""):
        width = get_terminal_size().columns - 31
        if message:
            line = '-' * (width - len(message) - 1) + ' ' + message
        else:
            line = '-' * width
        log.info(line)

    return _


@pytest.fixture(scope='session')
def dedent():
    return lambda text: text.replace(' ' * 4, '').strip() + '\n'


# TODO: Move these utilities into the library


@pytest.fixture(scope='session')
def write(dedent):
    def _(path: str, text: str) -> None:
        _path = Path(path).resolve()
        _text = dedent(text)
        message = f'Writing file: {_path}'
        log.info(message)
        log.debug('=' * len(message) + '\n\n' + (_text or '<nothing>\n'))
        _path.write_text(_text)

    return _


@pytest.fixture(scope='session')
def read():
    def _(path: str) -> str:
        _path = Path(path).resolve()
        message = f'Reading file: {_path}'
        log.info(message)
        text = _path.read_text()
        log.debug('=' * len(message) + '\n\n' + (text or '<nothing>\n'))
        return text

    return _
