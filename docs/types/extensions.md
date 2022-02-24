# Extended Types

For convenience, additional types are defined to handle common scenarios.

## Numbers

The `Number` converter should be used for values that can be both integers or floats, but should not be coerced into either type during serialization.

```python
from typing import Optional

from datafiles.converters import Number
```

| Type Annotation            | Python Value    | YAML Content   |
| -------------------------- | --------------- | -------------- |
| `foobar: Number`           | `foobar = 42`   | `foobar: 42`   |
| `foobar: Number`           | `foobar = 1.23` | `foobar: 1.23` |
| `foobar: Number`           | `foobar = None` | `foobar: 0.0`  |
| `foobar: Optional[Number]` | `foobar = None` | `foobar:`      |

## Text

The `Text` converter should be used for strings that contain lines of text, which are optimally serialized across multiple lines in a file.

```python
from typing import Optional

from datafiles.converters import Text
```

| Type Annotation          | Python Value                 | YAML Content                                                                       |
| ------------------------ | ---------------------------- | ---------------------------------------------------------------------------------- |
| `foobar: Text`           | `foobar = "Hello, world!"`   | `foobar: Hello, world!`                                                            |
| `foobar: Text`           | `foobar = "First\nSecond\n"` | `foobar: |`<br>&nbsp;&nbsp;&nbsp;&nbsp;`First`<br>&nbsp;&nbsp;&nbsp;&nbsp;`Second` |
| `foobar: Text`           | `foobar = None`              | `foobar: ""`                                                                       |
| `foobar: Optional[Text]` | `foobar = None`              | `foobar:`                                                                          |

## Enumerations

Subclasses of `enum.Enum` can also be used as type annotations:

```python
from enum import Enum

class Color:
    RED = 1
    GREEN = 2
    BLUE = 3
```

| Type Annotation | Python Value         | YAML Content |
| --------------- | -------------------- | ------------ |
| `color: Color`  | `color = Color.BLUE` | `color: 3`   |
