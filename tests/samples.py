from dataclasses import dataclass, field
from typing import List, Optional, Set

from datafiles import datafile
from datafiles.converters import String


@datafile("../tmp/sample.yml", manual=True)
class Sample:
    bool_: bool
    int_: int
    float_: float
    str_: str


@datafile("../tmp/sample.yml", manual=True, frozen=True)
class SampleFrozen:
    bool_: bool
    int_: int
    float_: float
    str_: str


@datafile("../tmp/sample.json", manual=True)
class SampleAsJSON:
    bool_: bool
    int_: int
    float_: float
    str_: str


@datafile("../tmp/sample.yml", manual=True)
class SampleWithCustomFields:
    included: str
    exluced: str

    class Meta:
        datafile_attrs = {"included": String}


@datafile("../tmp/sample.yml", manual=True)
class SampleWithDefaults:
    without_default: str
    with_default: str = "foo"


@dataclass
class _NestedSample1:
    name: str
    score: float


@dataclass(frozen=True)
class _FrozenNestedSample1:
    name: str
    score: float


@datafile("../tmp/sample.yml", manual=True)
class SampleWithNesting:
    name: str
    score: float
    nested: _NestedSample1


@dataclass
class _NestedSample2:
    name: str = "b"
    score: float = 3.4


@datafile("../tmp/sample.yml", manual=True)
class SampleWithNestingAndDefaults:
    name: str
    score: float = 1.2
    nested: _NestedSample2 = field(default_factory=_NestedSample2)


@dataclass
class _NestedSample3:
    name: str
    score: float
    weight: Optional[int]


@datafile("../tmp/sample.yml", manual=True)
class SampleWithNestingAndOptionals:
    name: str
    score: float
    nested: _NestedSample3


@datafile("../tmp/sample.yml", manual=True)
class SampleWithList:
    items: List[float]


@datafile("../tmp/sample.yml", manual=True)
class SampleWithListAndDefaults:
    items: List[float] = field(default_factory=list)


@datafile("../tmp/sample.yml", manual=True)
class SampleWithListOfDataclasses:
    items: List[_NestedSample1] = field(default_factory=list)


@datafile("../tmp/sample.yml", manual=True)
class SampleWithSet:
    items: Set[float]


@datafile("../tmp/sample.yml", manual=True)
class SampleWithSetAndDefaults:
    items: Set[float] = field(default_factory=set)


@datafile("../tmp/sample.yml", manual=True)
class SampleWithSetOfDataclasses:
    items: Set[_FrozenNestedSample1] = field(default_factory=set)


@datafile("../tmp/sample.yml", manual=True)
class SampleWithOptionals:
    required: float
    optional: Optional[float]
