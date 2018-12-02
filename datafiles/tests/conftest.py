from shutil import get_terminal_size

import log
import pytest

from datafiles import hooks


hooks.HIDE = False


@pytest.fixture
def logbreak():
    def _():
        width = get_terminal_size().columns - 40
        line = '-' * width
        log.info(line)

    return _
