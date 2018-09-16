import shutil
from pathlib import Path

import log
import pytest


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
        shutil.rmtree(path)
    path.mkdir(exist_ok=True)


@pytest.fixture(scope='session')
def dedent():
    return lambda text: text.replace(' ' * 4, '').strip() + '\n'


@pytest.fixture(scope='session')
def write(dedent):
    def _(path: str, text: str) -> None:
        _path = Path(path).resolve()
        _text = dedent(text)
        message = f'Writing: {_path}'
        log.info('=' * len(message))
        log.info(message + '\n\n' + _text)
        _path.write_text(_text)
        log.info('=' * len(message))

    return _


@pytest.fixture(scope='session')
def read():
    def _(path: str) -> str:
        _path = Path(path).resolve()
        message = f'Reading: {_path}'
        log.info('=' * len(message))
        text = _path.read_text()
        log.info(message + '\n\n' + text)
        log.info('=' * len(message))
        return text

    return _
