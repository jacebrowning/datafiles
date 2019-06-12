<h1>Model API</h1>

A model is created by either extending the `Model` class or using the `datafile()` decorator.

## Decorator

Given this example dataclass:

```
#!python"
from dataclasses import dataclass

@dataclass
class Item:
    name: str
    count: int
    available: bool
```

Synchronization is enabled by add the `@datafile(<pattern>)` decorator:

```
#!python hl_lines="5"
from dataclasses import dataclass

from datafiles import datafile

@datafile("items/{self.name}.yml")
@dataclass
class Item:
    name: str
    count: int
    available: bool
```

or by replacing the `@dataclass` decorator entirely:

```
#!python hl_lines="3"
from datafiles import datafile

@datafile("items/{self.name}.yml")
class Item:
    name: str
    count: int
    available: bool
```

<h3>Filename</h3>

Instances of the class are synchronized to disk according to the `<pattern>` string:

```python
Item("abc")  # <=> items/abc.yml
Item("def")  # <=> items/def.yml
```

Attributes included in the filename pattern are automatically excluded from the file contents.
Filename patterns are relative to the file in which models are defined unless `<pattern>` is an absolute path.

<h3>Options</h3>

The following options can be passed to the `@datafile()` decorator:

| Name | Type | Description | Default
| --- | --- | --- | --- |
| `attrs` | `dict` | Attributes to synchronize mapped to `datafile.converters` classes for serialization. | `{}` <sup>1</sup> |
| `manual` | `bool` | Synchronize object and file changes manually. | `False` |
| `defaults` | `bool` | Include default values in files. | `False` |
| `auto_load` | `bool` | Load automatically after saving.<br>If `manual=True` this option is ignored. | `True` |
| `auto_save` | `bool` | Save automatically after loading.<br>If `manual=True` this option is ignored. | `True` |
| `auto_attr` | `bool` | Automatically infer new attributes from the file. | `False` |

<sup>1</sup> _By default, synchronized attributes are inferred from the type annotations._

For example:

```
#!python hl_lines="3 9"
from datafiles import datafile

@datafile("items/{self.name}.yml", manual=True, defaults=True)
class Item:
    name: str
    count: int
    available: bool

@datafile("config.yml", auto_save=False)
class Config:
    default_count: int = 42
```

## Meta class

Alternatively, any of the above options can be configured through code by setting `datafile_<option>` in a `Meta` class:

```
#!python hl_lines="9 10 11 12 13 14"
from datafiles import datafile, converters

@datafile("items/{self.name}.yml")
class Item:
    name: str
    count: int
    available: bool

    class Meta:
        datafile_attrs = {'count': converters.Integer}
        datafile_manual = True
        datafile_defaults = True
        datafiles_auto_load = False
        datafiles_auto_save = False
```

## Base class

Finally, a datafile can explicitly extend `datafiles.Model` and set the pattern in the `Meta` class:

```
#!python hl_lines="11 12 13 14 15"
from dataclasses import dataclass

from datafiles import Model, converters

@dataclass
class Item(Model):
    name: str
    count: int
    available: bool

    class Meta:
        datafile_pattern = "items/{self.name}.yml"
        datafile_attrs = {'count': converters.Integer}
        datafile_manual = True
        datafile_defaults = True
```
