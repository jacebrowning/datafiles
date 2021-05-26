# pylint: disable=arguments-differ,unused-argument

from typing import Generic, List, TypeVar

from datafiles import Missing, converters, datafile
from datafiles.utils import dedent

from . import xfail_with_pep_563


@xfail_with_pep_563
def test_generic_converters(expect):
    S = TypeVar("S")
    T = TypeVar("T")

    class Pair(Generic[S, T], converters.Converter):
        first: S
        second: T

        def __init__(self, first: S, second: T) -> None:
            self.first = first
            self.second = second

        @classmethod
        def to_python_value(cls, deserialized_data, *, target_object=None):
            paired = zip(cls.CONVERTERS, deserialized_data)  # type: ignore
            values = [convert.to_python_value(val) for convert, val in paired]
            return cls(*values)

        @classmethod
        def to_preserialization_data(cls, python_value, *, default_to_skip=None):
            values = [python_value.first, python_value.second]
            paired = zip(cls.CONVERTERS, values)  # type: ignore
            return [convert.to_preserialization_data(val) for convert, val in paired]

    @datafile("../tmp/sample.yml")
    class Dictish:
        contents: List[Pair[str, converters.Number]]

    d = Dictish([Pair[str, converters.Number]("pi", 3.14)])  # type: ignore
    expect(d.datafile.text) == dedent(
        """
        contents:
          -   - pi
              - 3.14
        """
    )

    d = Dictish(Missing)  # type: ignore
    expect(d.contents[0].first) == "pi"
    expect(d.contents[0].second) == 3.14

    d.datafile.text = dedent(
        """
        contents:
          -   - degrees
              - 360
        """
    )
    expect(d.contents[0].first) == "degrees"
    expect(d.contents[0].second) == 360
