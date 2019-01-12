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
