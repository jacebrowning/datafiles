import logging
from shutil import get_terminal_size

import pytest

from datafiles import settings


settings.HIDE_TRACEBACK_IN_HOOKS = False

log = logging.getLogger(__name__)


@pytest.fixture
def logbreak():
    def _():
        width = get_terminal_size().columns - 40
        line = '-' * width
        log.info(line)

    return _
