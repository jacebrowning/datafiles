<h1>Manager API</h1>

Object-relational mapping (ORM) methods are available on all model classes via the `objects` proxy. The following sections assume an empty filesystem and the following sample datafile definition:

```python
from datafiles import datafile

@datafile("my_models/{self.my_key}.yml")
class MyModel:

    my_key: str
    my_value: int = 0
```

Many of the following examples are also shown in this [Jupyter Notebook](https://github.com/jacebrowning/datafiles/blob/develop/notebooks/manager_api.ipynb).

# `get_or_none()`

Instantiate an object from an existing file or return `None` if no matching file exists:

```python
>>> MyModel.objects.get_or_none('foobar')
None
```

```python
>>> m = MyModel('foobar', 42)
```

```python
>>> MyModel.objects.get_or_none('foobar')
MyModel(my_key='foobar', my_value=42)
```

# `get_or_create()`

Instantiate an object from an existing file or create one if no matching file exists:

```python
>>> m = MyModel('foo', 42)
```

```python
>>> MyModel.objects.get_or_create('foo')
MyModel(my_key='foo', my_value=42)
```

```python
>>> MyModel.objects.get_or_create('bar')
MyModel(my_key='bar', my_value=0)
```

# `all()`

Iterate over all objects matching the pattern:

```python
>>> generator = MyModel.objects.all()
>>> list(generator)
[]
```

```python
>>> m1 = MyModel('foo')
>>> m2 = MyModel('bar', 42)
```

```python
>>> for m in MyModel.objects.all():
...     print(m)
...
MyModel(my_key='foo' my_value=0)
MyModel(my_key='bar', my_value=42)
```

# `filter()`

Iterate all objects matching the pattern with additional required attribute values:

```python
>>> generator = MyModel.objects.filter(my_value=42)
>>> list(generator)
[MyModel(my_key='foo', my_value=42)]
```
