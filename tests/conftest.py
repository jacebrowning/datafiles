import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List

import log
import pytest

from datafiles import sync
from datafiles.converters import String


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
    def _(path, text):
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


@pytest.fixture
def Sample():
    @sync('../tmp/sample.yml')
    @dataclass
    class Sample:
        bool_: bool
        int_: int
        float_: float
        str_: str

    return Sample


@pytest.fixture
def SampleAsJSON():
    @sync('../tmp/sample.json')
    @dataclass
    class Sample:
        bool_: bool
        int_: int
        float_: float
        str_: str

    return Sample


@pytest.fixture
def SampleWithCustomFields():
    @sync('../tmp/sample.yml')
    @dataclass
    class Sample:
        included: str
        exluced: str

        class Meta:
            datafile_attrs = {'included': String}

    return Sample


@pytest.fixture
def SampleWithDefaultValues():
    @sync('../tmp/sample.yml')
    @dataclass
    class Sample:
        str_without_default: str
        str_with_default: str = 'foo'

    return Sample


@pytest.fixture
def SampleWithNesting():
    @dataclass
    class Sample2:
        name: str
        score: float

    @sync('../tmp/sample.yml')
    @dataclass
    class Sample:
        name: str
        score: float
        nested: Sample2

    return Sample


@pytest.fixture
def SampleWithNestingAndDefaultValues():
    @dataclass
    class Sample2:
        name: str = 'b'
        score: float = 3.4

    @sync('../tmp/sample.yml')
    @dataclass
    class Sample:
        name: str
        score: float = 1.2
        nested: Sample2 = Sample2()

    return Sample


@pytest.fixture
def SampleWithFloatList():
    @sync('../tmp/sample.yml')
    @dataclass
    class Sample:
        items: List[float]

    return Sample
