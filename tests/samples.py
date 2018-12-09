from dataclasses import dataclass, field
from typing import List, Optional

from datafiles import sync
from datafiles.converters import String


@sync('../tmp/sample.yml', manual=True)
@dataclass
class Sample:
    bool_: bool
    int_: int
    float_: float
    str_: str


@sync('../tmp/sample.json', manual=True)
@dataclass
class SampleAsJSON:
    bool_: bool
    int_: int
    float_: float
    str_: str


@sync('../tmp/sample.yml', manual=True)
@dataclass
class SampleWithCustomFields:
    included: str
    exluced: str

    class Meta:
        datafile_attrs = {'included': String}


@sync('../tmp/sample.yml', manual=True)
@dataclass
class SampleWithDefaults:
    without_default: str
    with_default: str = 'foo'


@dataclass
class _NestedSample1:
    name: str
    score: float


@sync('../tmp/sample.yml', manual=True)
@dataclass
class SampleWithNesting:
    name: str
    score: float
    nested: _NestedSample1


@dataclass
class _NestedSample2:
    name: str = 'b'
    score: float = 3.4


@sync('../tmp/sample.yml', manual=True)
@dataclass
class SampleWithNestingAndDefaults:
    name: str
    score: float = 1.2
    nested: _NestedSample2 = field(default_factory=_NestedSample2)


@sync('../tmp/sample.yml', manual=True)
@dataclass
class SampleWithList:
    items: List[float]


@sync('../tmp/sample.yml', manual=True)
@dataclass
class SampleWithListAndDefaults:
    items: List[float] = field(default_factory=list)


@sync('../tmp/sample.yml', manual=True)
@dataclass
class SampleWithListOfDataclasses:
    items: List[_NestedSample1] = field(default_factory=list)


@sync('../tmp/sample.yml', manual=True)
@dataclass
class SampleWithOptionals:
    required: float
    optional: Optional[float]
