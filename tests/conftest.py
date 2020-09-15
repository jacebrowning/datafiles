import os
from pathlib import Path
from shutil import rmtree

import log
import pytest

from datafiles import settings


settings.HIDE_TRACEBACK_IN_HOOKS = False


xfail_on_ci = pytest.mark.xfail(bool(os.getenv('CI')), reason="Flaky on CI")


def pytest_configure(config):
    terminal = config.pluginmanager.getplugin('terminal')
    terminal.TerminalReporter.showfspath = False
    log.init()  # TODO: determine why the 'relpath' filter wasn't added automatically


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
