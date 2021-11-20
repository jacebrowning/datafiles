# Generic Types

Python generic types are supported, but require `to_python_value` and
`to_preserialization_data` implementations similar to custom types. The
class's `CONVERTERS` attribute will have the appropriate datafile
converters placed in it for the specified generic types. You should use
these in your implementation to convert the marshalled data.

```python
from typing import Generic, List, TypeVar

from datafiles import Missing, converters, datafile
from datafiles.utils import dedent


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
        paired = zip(cls.CONVERTERS, deserialized_data)
        values = [convert.to_python_value(val) for convert, val in paired]
        return cls(*values)

    @classmethod
    def to_preserialization_data(cls, python_value, *, default_to_skip=None):
        values = [python_value.first, python_value.second]
        paired = zip(cls.CONVERTERS, values)
        return [
            convert.to_preserialization_data(val)
            for convert, val in paired
        ]

@datafile("sample.yml")
class Dictish:
    contents: List[Pair[str, converters.Number]]
```

which can be constructed like so:

```python
dictish = Dictish([Pair("a", 1), Pair("pi", 3.14)])
```

to save this `sample.yml` file:

```yaml
contents:
  -   - a
      - 1
  -   - pi
      - 3.14
```

An example of using generic types can be found in this [Jupyter Notebook](https://github.com/jacebrowning/datafiles/blob/main/notebooks/generic_types.ipynb).
