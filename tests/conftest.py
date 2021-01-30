from pathlib import Path
from shutil import rmtree

import log
import pytest

from datafiles import settings


settings.HIDE_TRACEBACK_IN_HOOKS = False
settings.WRITE_DELAY = 0.1


def pytest_configure(config):
    terminal = config.pluginmanager.getplugin('terminal')
    terminal.TerminalReporter.showfspath = False
    log.init()  # TODO: determine why the 'relpath' filter wasn't added automatically


@pytest.fixture(autouse=True)
def create_tmp():
    path = Path('tmp')
    if path.exists():
        rmtree(path)
    path.mkdir(exist_ok=True)
