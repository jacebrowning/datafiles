# Overview

Datafiles is a bidirectional serialization library for Python [dataclasses](https://docs.python.org/3/library/dataclasses.html) that automatically synchronizes object instances to the filesystem using type annotations. It supports a variety of file formats with round-trip preservation of formatting and comments, where possible.

# Installation

Install it directly into an activated virtual environment:

```
$ pip install datafiles
```

or add it to your [Poetry](https://poetry.eustace.io/) project:

```
$ poetry add datafiles
```

# Quick Start

Decorate a dataclass with a directory pattern to synchronize instances:

```python
from dataclasses import dataclass

from datafiles import sync

@sync("samples/{self.key}.yml")
@dataclass
class Sample:
    
    key: int
    name: str
    value: float = 0.0
```

By default, all member variables will be included in the serialized file except for those:

- Included in the directory pattern
- Set to default values

So the following instantiation:

```python
>>> sample = Sample(42, "Widget")
```

produces `samples/42.yml` containing:

```yaml
name: Widget
```
