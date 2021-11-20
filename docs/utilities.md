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
>>> sample = auto('sample.yml')
>>> sample.names
['Alice', 'Bob']
```

where modified attributes:

```python
>>> sample.numbers.append(3)
```

are automatically reflected in the file:

```
#!text hl_lines="9"
$ cat sample.yml

names:
  - Alice
  - Bob
numbers:
  - 1
  - 2
  - 3
```

Additional examples can be found in this [Jupyter Notebook](https://github.com/jacebrowning/datafiles/blob/main/notebooks/file_inference.ipynb).
