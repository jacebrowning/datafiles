"""Tests for instantiating new synchronized objects."""

# pylint: disable=unused-variable,singleton-comparison

from dataclasses import dataclass, field
from typing import Dict

from datafiles import Missing, datafile
from datafiles.utils import logbreak, write

from . import xfail_with_pep_563


@datafile("../tmp/sample.yml", manual=True)
class SampleWithDefaults:
    foo: int = 1
    bar: str = "a"


@dataclass
class NestedSample:
    name: str
    score: float


@datafile("../tmp/sample.yml", manual=True)
class SampleWithDefaultsAndNesting:
    nested: NestedSample
    name: str = ""
    score: float = 0.0


@datafile("../tmp/sample.yml", manual=True)
class SampleWithFactoryDefaults:
    a: float
    b: float
    c: float = field(default_factory=lambda: 42)


@datafile("../tmp/sample.yml", manual=True)
class SampleWithComputedDefaults:
    a: float
    b: float
    c: float = field(init=False)

    def __post_init__(self):
        self.c = self.a + self.b


def describe_existing_file():
    def it_wins_when_no_init_values(expect):
        write(
            "tmp/sample.yml",
            """
            foo: 2
            bar: b
            """,
        )

        sample = SampleWithDefaults()

        expect(sample.foo) == 2
        expect(sample.bar) == "b"

    def it_loses_against_init_values(expect):
        write(
            "tmp/sample.yml",
            """
            foo: 3
            bar: c
            """,
        )

        sample = SampleWithDefaults(4, "d")

        expect(sample.foo) == 4
        expect(sample.bar) == "d"

    def it_wins_against_default_init_values(expect):
        write(
            "tmp/sample.yml",
            """
            bar: e
            """,
        )

        sample = SampleWithDefaults(foo=5)

        expect(sample.foo) == 5
        expect(sample.bar) == "e"

    def it_merges_with_nested_value(expect):
        write(
            "tmp/sample.yml",
            """
            name: foo
            score: 7
            """,
        )

        sample = SampleWithDefaultsAndNesting(
            name="", score=0.0, nested=NestedSample(name="bar", score=8)
        )

        expect(sample.name) == "foo"
        expect(sample.score) == 7.0
        expect(sample.nested.name) == "bar"
        expect(sample.nested.score) == 8.0


def describe_nonexisting_file():
    @datafile("../tmp/sample.yml")
    class SampleAutomatic:
        pass

    SampleManual = SampleWithDefaults

    def it_is_created_automatically_by_default(expect):
        sample = SampleAutomatic()

        expect(sample.datafile.exists).is_(True)

    def it_is_not_created_automatically_when_manual(expect):
        sample = SampleManual()

        expect(sample.datafile.exists).is_(False)


def describe_factory_defaults():
    def when_no_file(expect):
        sample = SampleWithFactoryDefaults(1.2, 3.4)

        expect(sample.a) == 1.2
        expect(sample.b) == 3.4
        expect(sample.c) == 42.0

    def when_file_exists(expect):
        write(
            "tmp/sample.yml",
            """
            a: 1.0
            b: 2.0
            c: 9.9
            """,
        )

        sample = SampleWithFactoryDefaults(1.2, 3.4)

        expect(sample.a) == 1.2
        expect(sample.b) == 3.4
        expect(sample.c) == 9.9


def describe_missing_attributes():
    @xfail_with_pep_563
    def when_dataclass(expect):
        @dataclass
        class Name:
            value: str

        @datafile("../tmp/samples/{self.key}.yml")
        @dataclass
        class Sample:

            key: int
            name: Name
            value: float = 0.0

        sample = Sample(42, Name("Widget"))

        logbreak("Loading missing 'name' dataclass")

        sample2 = Sample(42, Missing)  # type: ignore

        expect(sample2.name.value) == "Widget"

    def with_none_defaults(expect):
        @datafile("../tmp/sample.yml")
        class Config:
            name: str = None  # type: ignore
            channels: Dict[str, str] = None  # type: ignore

        config = Config.objects.get_or_create()
        expect(config.name) == ""
        expect(config.channels) == {}
        expect(config.datafile.path.exists()) == True
