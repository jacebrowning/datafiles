# Mapper API

Instances of datafile models have an additional `datafile` proxy to manually interact with the filesystem. The following sections assume an empty filesystem and use the following sample datafile definition:

```python
from datafiles import datafile

@datafile("my_models/{self.my_key}.yml", manual=True)
class MyModel:

    my_key: str
    my_value: int = 1
```

```python
>>> model = MyModel("foo")
```

Many of the following examples are also shown in this [Jupyter Notebook](https://github.com/jacebrowning/datafiles/blob/main/notebooks/mapper_api.ipynb).

## `path`

Get the full path to the mapped file:

```python
>>> model.datafile.path
PosixPath("/Projects/Demo/my_models/foo.yml")
```

## `exists`

Determine if the mapped file exists:

```python
>>> model.datafile.exists
False
```

_By default, the file is created automatically. Set `manual=True` to disable this behavior._

## `save()`

Manually save an object to the filesystem:

```python
>>> model.datafile.save()
```

_By default, this method is called automatically. Set `manual=True` to disable this behavior._

## `load()`

Manually load an object from the filesystem:

```python
>>> model.datafile.load()
```

_By default, this method is called automatically. Set `manual=True` to disable this behavior._

## `modified`

Determine if there are any unsynchronized changes on the filesystem:

```
$ echo "my_value: 42" > my_models/foo.yml
```

```python
>>> model.datafile.modified
True
```

## `data`

Access the parsed model attributes directly:

```python
>>> model.datafile.data
ordereddict([("my_value", 1)])
```
