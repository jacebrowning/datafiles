from dataclasses import dataclass
from pathlib import Path

import pytest

from datafiles import sync


@pytest.fixture(scope='session', autouse=True)
def create_tmp():
    Path('tmp').mkdir(exist_ok=True)


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


@pytest.fixture
def sample(Sample):
    return Sample(None, None, None, None)
