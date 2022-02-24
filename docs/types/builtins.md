# Builtin Types

When Python builtin types are used as type annotations they are automatically mapped to the corresponding type in the chosen file format. Any of these types will accept `None` as a value when made optional.

```python
from typing import Optional
```

## Booleans

| Type Annotation          | Python Value     | YAML Content    |
| ------------------------ | ---------------- | --------------- |
| `foobar: bool`           | `foobar = True`  | `foobar: true`  |
| `foobar: bool`           | `foobar = False` | `foobar: false` |
| `foobar: bool`           | `foobar = None`  | `foobar: false` |
| `foobar: Optional[bool]` | `foobar = False` | `foobar:`       |

## Integers

| Type Annotation         | Python Value    | YAML Content |
| ----------------------- | --------------- | ------------ |
| `foobar: int`           | `foobar = 42`   | `foobar: 42` |
| `foobar: int`           | `foobar = 1.23` | `foobar: 1`  |
| `foobar: int`           | `foobar = None` | `foobar: 0`  |
| `foobar: Optional[int]` | `foobar = None` | `foobar:`    |

## Floats

| Type Annotation           | Python Value    | YAML Content   |
| ------------------------- | --------------- | -------------- |
| `foobar: float`           | `foobar = 1.23` | `foobar: 1.23` |
| `foobar: float`           | `foobar = 42`   | `foobar: 42.0` |
| `foobar: float`           | `foobar = None` | `foobar: 0.0`  |
| `foobar: Optional[float]` | `foobar = None` | `foobar:`      |

## Strings

| Type Annotation         | Python Value               | YAML Content            |
| ----------------------- | -------------------------- | ----------------------- |
| `foobar: str`           | `foobar = "Hello, world!"` | `foobar: Hello, world!` |
| `foobar: str`           | `foobar = 42`              | `foobar: "42"`          |
| `foobar: str`           | `foobar = None`            | `foobar: ""`            |
| `foobar: Optional[str]` | `foobar = None`            | `foobar:`               |
