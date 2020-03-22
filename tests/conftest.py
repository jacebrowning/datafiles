import os
from pathlib import Path
from shutil import rmtree

import pytest

from datafiles import settings


settings.HIDE_TRACEBACK_IN_HOOKS = False


xfail_on_ci = pytest.mark.xfail(bool(os.getenv('CI')), reason="Flaky on CI")


def pytest_configure(config):
    # import log
    # log.init(debug=True)
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
