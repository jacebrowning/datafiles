from pathlib import Path
from shutil import get_terminal_size, rmtree

import log
import pytest

from datafiles import settings


settings.HIDE_TRACEBACK_IN_HOOKS = False


def pytest_configure(config):
    terminal = config.pluginmanager.getplugin('terminal')

    class QuietReporter(terminal.TerminalReporter):  # type: ignore
        """Reporter that only shows dots when running tests."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.verbosity = 0
            self.showlongtestinfo = False
            self.showfspath = False

    terminal.TerminalReporter = QuietReporter


@pytest.fixture(autouse=True)
def create_tmp():
    path = Path('tmp')
    if path.exists():
        rmtree(path)
    path.mkdir(exist_ok=True)


@pytest.fixture
def logbreak():
    def _():
        width = get_terminal_size().columns - 30
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
        message = f'Writing: {_path}'
        frame = '=' * len(message)
        log.info(message)
        log.debug(frame + '\n\n' + (_text or '<nothing>\n'))
        _path.write_text(_text)
        log.debug(frame)

    return _


@pytest.fixture(scope='session')
def read():
    def _(path: str) -> str:
        _path = Path(path).resolve()
        message = f'Reading: {_path}'
        frame = '=' * len(message)
        log.info(message)
        text = _path.read_text()
        log.debug(frame + '\n\n' + (text or '<nothing>\n'))
        log.debug(frame)
        return text

    return _
