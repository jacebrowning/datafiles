import shutil
from dataclasses import dataclass

import pytest

from datafiles import sync


@pytest.fixture
def clean_tmp():
    shutil.rmtree('tmp', ignore_errors=True)


@pytest.fixture(scope='session')
def dedent():
    return lambda text: text.replace(' ' * 4, '').strip() + '\n'


@pytest.fixture
def Sample():
    """A decorated data class with builtin types"""

    @sync('tmp/sample.yml')
    @dataclass
    class Sample:
        bool_: bool
        int_: int
        float_: float
        str_: str

    return Sample
