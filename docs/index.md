# Datafiles

Datafiles is a bidirectional serialization library for Python [dataclasses](https://docs.python.org/3/library/dataclasses.html) to synchronizes objects to the filesystem using type annotations. It supports a variety of file formats with round-trip preservation of formatting and comments, where possible. Object changes are automatically saved to disk and only include the minimum data needed to restore each object.

Some common use cases include:

- Coercing user-editable files into the proper Python types
- Storing program configuration and state in version control
- Loading data fixtures for demonstration or testing purposes
- Synchronizing application state using file sharing services
- Prototyping data models agnostic of persistence backends

## Installation

Install it directly into an activated virtual environment:

```text
$ pip install datafiles
```

or add it to your [Poetry](https://poetry.eustace.io/) project:

```text
$ poetry add datafiles
```

## Quick Start

Decorate a [type-annotated](https://docs.python.org/3/library/typing.html) class with a directory pattern to synchronize instances:

```python
from datafiles import datafile

@datafile("samples/{self.key}.yml")
class Sample:

    key: int
    name: str
    value: float = 0.0
```

By default, all member variables will be included in the serialized file except for those:

- Included in the directory pattern
- Set to default values

So, the following instantiation:

```python
>>> sample = Sample(42, "Widget")
```

produces `samples/42.yml` containing:

```yaml
name: Widget
```

and the following instantiation restores the object:

```python
>>> from datafiles import Missing
>>> sample = Sample(42, Missing)
>>> sample.name
Widget
```

## Type Checking

If using mypy, enable the plugin via `pyproject.toml` settings:

```toml
[tool.mypy]

plugins = "datafiles.plugins:mypy"
```

or `mypy.ini` configuration file:

```ini
[mypy]

plugins = datafiles.plugins:mypy
```

## Resources

- [Source code](https://github.com/jacebrowning/datafiles)
- [Issue tracker](https://github.com/jacebrowning/datafiles/issues)
- [Release history](https://github.com/jacebrowning/datafiles/blob/main/CHANGELOG.md)
