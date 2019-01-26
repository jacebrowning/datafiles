# Lists

```python
from typing import List, Optional
```

| Type Annotation | Python Value | YAML Data |
| --- | --- | --- |
| `foobar: List[int]` | `foobar = []` | `foobar:`<br>&nbsp;&nbsp;&nbsp;&nbsp;`-` |
| `foobar: List[int]` | `foobar = [1.23]` | `foobar:`<br>&nbsp;&nbsp;&nbsp;&nbsp;`- 1` |
| `foobar: List[int]` | `foobar = None` | `foobar:`<br>&nbsp;&nbsp;&nbsp;&nbsp;`-` |
| `foobar: Optional[List[int]]` | `foobar = None` | `foobar: ` |

More examples can be found in this [Jupyter Notebook](https://github.com/jacebrowning/datafiles/blob/develop/notebooks/patched_containers.ipynb).

# Dictionaries

```python
from typing import Dict, Optional
```

| Type Annotation | Python Value | YAML Data |
| --- | --- | --- |
| `foobar: Dict[str, int]` | `foobar = {}` | `foobar: {}` |
| `foobar: Dict[str, int]` | `foobar = {'a': 42}` | `foobar:`<br>&nbsp;&nbsp;&nbsp;&nbsp;`a: 42` |
| `foobar: Dict[str, int]` | `foobar = None` | `foobar: {}` |
| `foobar: Optional[Dict[str, int]]` | `foobar = None` | `foobar: ` |

**NOTE:** Schema enforcement is not available with the `Dict` annotation.

# Dataclasses

Dataclasses can also be nested as shown in this [Jupyter Notebook](https://github.com/jacebrowning/datafiles/blob/develop/notebooks/nested_dataclass.ipynb).
