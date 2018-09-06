import shutil
from pathlib import Path

import log
import pytest

from . import samples


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
        message = f'Writing: {_path}'
        log.info('=' * len(message))
        log.info(message)
        _text = dedent(text)
        for index, line in enumerate(_text.splitlines()):
            log.info(f'Line {index+1}: {line}')
        _path.write_text(_text)
        log.info('=' * len(message))

    return _


@pytest.fixture(scope='session')
def read():
    def _(path: str) -> str:
        _path = Path(path).resolve()
        message = f'Reading: {_path}'
        log.info('=' * len(message))
        log.info(message)
        text = _path.read_text()
        for index, line in enumerate(text.splitlines()):
            log.info(f'Line {index+1}: {line}')
        log.info('=' * len(message))
        return text

    return _


@pytest.fixture
def Sample():
    return samples.Sample


@pytest.fixture
def SampleAsJSON():
    return samples.SampleAsJSON


@pytest.fixture
def SampleWithCustomFields():
    return samples.SampleWithCustomFields


@pytest.fixture
def SampleWithDefaults():
    return samples.SampleWithDefaults


@pytest.fixture
def SampleWithNesting():
    return samples.SampleWithNesting


@pytest.fixture
def SampleWithNestingAndDefaults():
    return samples.SampleWithNestingAndDefaults


@pytest.fixture
def SampleWithList():
    return samples.SampleWithList


@pytest.fixture
def SampleWithListAndDefaults():
    return samples.SampleWithListAndDefaults


@pytest.fixture
def SampleWithOptionals():
    return samples.SampleWithOptionals
