# Datafiles: A file-based ORM for Python dataclasses

Datafiles is a bidirectional serialization library for Python [dataclasses](https://docs.python.org/3/library/dataclasses.html) to synchronize objects to the filesystem using type annotations. It supports a variety of file formats with round-trip preservation of formatting and comments, where possible. Object changes are automatically saved to disk and only include the minimum data needed to restore each object.

[![Linux Build](https://img.shields.io/github/actions/workflow/status/jacebrowning/datafiles/main.yml?branch=main&label=linux)](https://github.com/jacebrowning/datafiles/actions)
[![Windows Build](https://img.shields.io/appveyor/ci/jacebrowning/datafiles/main.svg?label=windows)](https://ci.appveyor.com/project/jacebrowning/datafiles)
[![Code Coverage](https://img.shields.io/codecov/c/github/jacebrowning/datafiles)
](https://codecov.io/gh/jacebrowning/datafiles)
[![PyPI License](https://img.shields.io/pypi/l/datafiles.svg)](https://pypi.org/project/datafiles)
[![PyPI Version](https://img.shields.io/pypi/v/datafiles.svg?label=version)](https://pypi.org/project/datafiles)
[![PyPI Downloads](https://img.shields.io/pypi/dm/datafiles.svg?color=orange)](https://pypistats.org/packages/datafiles)
[![Gitter](https://img.shields.io/gitter/room/jacebrowning/datafiles?color=D0164E)](https://gitter.im/jacebrowning/datafiles)

Some common use cases include:

- Coercing user-editable files into the proper Python types
- Storing program configuration and state in version control
- Loading data fixtures for demonstration or testing purposes
- Synchronizing application state using file sharing services
- Prototyping data models agnostic of persistence backends

Watch [my lightning talk](https://www.youtube.com/watch?v=moYkuNrmc1I&feature=youtu.be&t=1225) for a demo of this in action!

## Overview

Take an existing dataclass such as [this example](https://docs.python.org/3/library/dataclasses.html#module-dataclasses) from the documentation:

```python
from dataclasses import dataclass

@dataclass
class InventoryItem:
    """Class for keeping track of an item in inventory."""

    name: str
    unit_price: float
    quantity_on_hand: int = 0

    def total_cost(self) -> float:
        return self.unit_price * self.quantity_on_hand
```

and decorate it with a directory pattern to synchronize instances:

```python
from datafiles import datafile

@datafile("inventory/items/{self.name}.yml")
class InventoryItem:
    ...
```

Then, work with instances of the class as normal:

```python
>>> item = InventoryItem("widget", 3)
```

```yaml
# inventory/items/widget.yml

unit_price: 3.0
```

Changes to the object are automatically saved to the filesystem:

```python
>>> item.quantity_on_hand += 100
```

```yaml
# inventory/items/widget.yml

unit_price: 3.0
quantity_on_hand: 100
```

Changes to the filesystem are automatically reflected in the object:

```yaml
# inventory/items/widget.yml

unit_price: 2.5 # <= manually changed from "3.0"
quantity_on_hand: 100
```

```python
>>> item.unit_price
2.5
```

Objects can also be restored from the filesystem:

```python
>>> from datafiles import Missing
>>> item = InventoryItem("widget", Missing)
>>> item.unit_price
2.5
>>> item.quantity_on_hand
100
```

## Installation

Install this library directly into an activated virtual environment:

```
$ pip install datafiles
```

or add it to your [Poetry](https://poetry.eustace.io/) project:

```
$ poetry add datafiles
```

## Documentation

To see additional synchronization and formatting options, please consult the [full documentation](https://datafiles.readthedocs.io).
