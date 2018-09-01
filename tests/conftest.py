from dataclasses import dataclass
from pathlib import Path

import pytest

from datafiles import sync
from datafiles.fields import String


@pytest.fixture(scope='session', autouse=True)
def create_tmp():
    Path('tmp').mkdir(exist_ok=True)


@pytest.fixture(scope='session')
def dedent():
    return lambda text: text.replace(' ' * 4, '').strip() + '\n'


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
def sample(Sample):
    return Sample(None, None, None, None)


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
def sample_json(SampleAsJSON):
    return SampleAsJSON(None, None, None, None)


@pytest.fixture
def SampleWithCustomFields():
    @sync('../tmp/sample.yml')
    @dataclass
    class Sample:
        included: str
        exluced: str

        class Meta:
            datafile_fields = {'included': String}

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
    class Nested:
        name: str
        score: float

    @sync('../tmp/sample.yml')
    @dataclass
    class Sample:
        name: str
        score: float
        nested: Nested

    return Sample


@pytest.fixture
def sample_nesting(SampleWithNesting):
    return SampleWithNesting(None, None, None)
