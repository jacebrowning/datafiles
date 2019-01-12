# Builtin Types

## Booleans

| Type Annotation | Python Value | YAML Data |
| --- | --- | --- |
| `foobar: bool` | `foobar = True` | `foobar: true` |
| `foobar: bool` | `foobar = False` | `foobar: false` |
| `foobar: bool` | `foobar = None` | `foobar: false` |
| `foobar: Optional[bool]` | `foobar = False` | `foobar: null` |

## Integers

| Type Annotation | Python Value | YAML Data |
| --- | --- | --- |
| `foobar: int` | `foobar = 42` | `foobar: 42` |
| `foobar: int` | `foobar = 1.23` | `foobar: 1` |
| `foobar: int` | `foobar = None` | `foobar: 0` |
| `foobar: Optional[int]` | `foobar = None` | `foobar: null` |

## Floats

| Type Annotation | Python Value | YAML Data |
| --- | --- | --- |
| `foobar: float` | `foobar = 1.23` | `foobar: 1.23` |
| `foobar: float` | `foobar = 42` | `foobar: 42.0` |
| `foobar: float` | `foobar = None` | `foobar: 0.0` |
| `foobar: Optional[float]` | `foobar = None` | `foobar: null` |

## Strings

| Type Annotation | Python Value | YAML Data |
| --- | --- | --- |
| `foobar: str` | `foobar = "Hello, world!"` | `foobar: Hello, world!` |
| `foobar: str` | `foobar = 42` | `foobar: '42'` |
| `foobar: str` | `foobar = None` | `foobar: ''` |
| `foobar: Optional[str]` | `foobar = None` | `foobar: null` |

# Extended Types

## Numbers

```python
from datafiles.converters import Number
```

| Type Annotation | Python Value | YAML Data |
| --- | --- | --- |
| `foobar: Number` | `foobar = 42` | `foobar: 42` |
| `foobar: Number` | `foobar = 1.23` | `foobar: 1.23` |
| `foobar: Number` | `foobar = None` | `foobar: 0.0` |
| `foobar: Optional[Number]` | `foobar = None` | `foobar: null` |

## Text

```python
from datafiles.converters import Text
```

| Type Annotation | Python Value | YAML Data |
| --- | --- | --- |
| `foobar: str` | `foobar = "Hello, world!"` | `foobar: Hello, world!` |
| `foobar: str` | `foobar = "First\nSecond\n"` | `foobar: | `<br>&nbsp;&nbsp;&nbsp;&nbsp;`First`<br>&nbsp;&nbsp;&nbsp;&nbsp;`Second` |
| `foobar: str` | `foobar = None` | `foobar: ''` |
| `foobar: Optional[str]` | `foobar = None` | `foobar: null` |
