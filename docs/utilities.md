# Utilities

The following functions exist to provide additional high-level functionality.

## `auto()`

Given an arbitrary file, this library can attempt to map its structure into a Python object synchronized back to that file. For example, a YAML file named `sample.yml` containing the following:

```yaml
names:
  - Alice
  - Bob
numbers:
  - 1
  - 2
```

can be loaded into an object:

```python
>>> from datafiles import auto
>>> sample = auto("sample.yml")
>>> sample.names
["Alice", "Bob"]
```

where modified attributes:

```python
>>> sample.numbers.append(3)
```

are automatically reflected in the file:

```yaml hl_lines='7'
names:
  - Alice
  - Bob
numbers:
  - 1
  - 2
  - 3
```

Additional examples can be found in this [Jupyter Notebook](https://github.com/jacebrowning/datafiles/blob/main/notebooks/file_inference.ipynb).

## `frozen()`

This context manager can be used to temporarily disable saving objects to the filesystem:

```python
import datafiles

from .models import MyModel

instance = MyModel()

with datafiles.frozen():
    instance.a = 1
    instance.b = 2
    instance.c = 3

instance.d = 4

```

This is useful when changes manipulate a complex object's structure in such a way that references to synchronized attributes are lost or to improve performance when making lots of changes.

### Thawing Objects

Unless `manual=True` is set, the next modification outside of the context manager will trigger a save. To do this automatically, include the objects as arguments:

```python
...

with datafiles.frozen(instance):
    instance.a = 1
    instance.b = 2
    instance.c = 3
```

## `sync()`

This helper can be used to enable file synchronization on an arbitrary object:

```python
from dataclasses import dataclass

@dataclass
class InventoryItem:
    name: str
    unit_price: float
    quantity_on_hand: int = 0
```

by providing it a path or directory pattern:

```python
>>> from datafiles import sync
>>> item = InventoryItem("widget", 3)
>>> sync(item, "inventory/items/{self.name}.yml")
```
