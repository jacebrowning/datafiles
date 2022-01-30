from pathlib import Path
from shutil import rmtree

import log
import pytest

from datafiles import settings

settings.HIDDEN_TRACEBACK = False
settings.WRITE_DELAY = 0.1


def pytest_configure(config):
    terminal = config.pluginmanager.getplugin("terminal")
    terminal.TerminalReporter.showfspath = False
    log.init(debug=True)


@pytest.fixture(autouse=True)
def create_tmp():
    path = Path("tmp")
    if path.exists():
        rmtree(path)
    path.mkdir(exist_ok=True)
