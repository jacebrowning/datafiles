# Decorators

## Synchronization

The simplest way to turn a dataclass into a datafile is to replace the `@dataclass` decorator with `@datafile`:

```python
# BEFORE

from dataclasses import dataclass

@dataclass
class Item:
    name: str
    count: int
    available: bool
```

```python
# AFTER

from datafiles import datafile

@datafile('items/{self.name}.yml')
class Item:
    name: str
    count: int
    available: bool
```

But you can also decorate an existing dataclass:

```python
# BEFORE

from dataclasses import dataclass

@dataclass
class Item:
    name: str
    count: int
    available: bool
```

```python
# AFTER

from dataclasses import dataclass

from datafiles import datafile

@datafile('items/{self.name}.yml')
@dataclass
class Item:
    name: str
    count: int
    available: bool
```

## Options

The following options can be passed to `@datafile()` decorator:

| Name | Type | Description | Default
| --- | --- | --- | --- |
| `attrs` | `dict` | Attributes to synchronize mapped to `datafile.converters` classes for serialization. | _Inferred from type annotations._ |
| `manual` | `bool` | Synchronize object and file changes manually. | `False` |
| `defaults` | `bool` | Include default values in files. | `False` | 

For example:

```python
from datafiles import datafile

@datafile('items/{self.name}.yml', manual=True, defaults=True)
class Item:
    name: str
    count: int
    available: bool
```

## Meta class

Alternatively, any of the above options can be configured through code by setting `datafile_<option>` in a `Meta` class:

```python
from datafiles import datafile, converters

@datafile('items/{self.name}.yml')
class Item:
    name: str
    count: int
    available: bool

    class Meta:
        datafile_attrs = {'count': converters.Integer}
        datafile_manual = True
        datafile_defaults = True

```

## Base class

Finally, a datafile can explicitly extend `datafiles.Model` to set all options in the `Meta` class:

```python
from dataclasses import dataclass

from datafiles import Model, converters

@dataclass
class Item(Model):
    name: str
    count: int
    available: bool

    class Meta:
        datafile_pattern = 'items/{self.name}.yml'
        datafile_attrs = {'count': converters.Integer}
        datafile_manual = True
        datafile_defaults = True

```

