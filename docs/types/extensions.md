# Extended Types

## Numbers

```python
from typing import Optional

from datafiles.converters import Number
```

| Type Annotation | Python Value | YAML Data |
| --- | --- | --- |
| `foobar: Number` | `foobar = 42` | `foobar: 42` |
| `foobar: Number` | `foobar = 1.23` | `foobar: 1.23` |
| `foobar: Number` | `foobar = None` | `foobar: 0.0` |
| `foobar: Optional[Number]` | `foobar = None` | `foobar: ` |

## Text

```python
from typing import Optional

from datafiles.converters import Text
```

| Type Annotation | Python Value | YAML Data |
| --- | --- | --- |
| `foobar: Text` | `foobar = "Hello, world!"` | `foobar: Hello, world!` |
| `foobar: Text` | `foobar = "First\nSecond\n"` | `foobar: | `<br>&nbsp;&nbsp;&nbsp;&nbsp;`First`<br>&nbsp;&nbsp;&nbsp;&nbsp;`Second` |
| `foobar: Text` | `foobar = None` | `foobar: ''` |
| `foobar: Optional[Text]` | `foobar = None` | `foobar: ` |
