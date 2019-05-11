Object-relational mapper (ORM) methods are available on all model classes via the `datafiles` proxy. The following examples are based on this sample datafile:

```python
from datafiles import datafile

@datafile("my_models/{self.my_key}.yml")
class MyModel:

    my_key: str
    my_value: int = 0
```

# `get_or_none`

Instantiate an object from an existing file or return `None` if no matching file exists:

```python
>>> MyModel.datafiles.get_or_none('existing')
MyModel(my_key='existing')
```

```python
>>> MyModel.datafiles.get_or_none('unknown')
None
```

# `get_or_create`

Instantiate an object from an existing file or create one if no matching file exists:

```python
>>> MyModel.datafiles.get_or_none('existing')
MyModel(my_key='existing')
```

```python
>>> MyModel.datafiles.get_or_none('unknown')
MyModel(my_key='unknown')
```
