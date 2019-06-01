Finally, it's possible to use any custom types as annotations.

# Extension

Custom types can be saved and loaded by extending one of the included converter classes:

| Class | Description |
| --- | --- |
| `converters.Converter` | Base class for all converters. |
| `converters.Boolean` | Converts to `bool` before serialization. |
| `converters.Integer` | Converts to `int` before serialization. |
| `converters.Float` | Converts to `float` before serialization. |
| `converters.String` | Converts to `str` before serialization. |

For example, here is a custom `datetime` class that serializes using the ISO format:

```
#!python hl_lines="9 14"
from datetime import datetime

from datafiles import converters, datafile


class MyDateTime(converters.Converter, datetime):

    @classmethod
    def to_preserialization_data(cls, python_value, **kwargs):
        # Convert `MyDateTime` to a value that can be serialized
        return python_value.isoformat()

    @classmethod
    def to_python_value(cls, deserialized_data, **kwargs):
        # Convert file value back into a `MyDateTime` object
        return MyDateTime.fromisoformat(deserialized_data)

    # Any additional methods could go here...


@datafile("sample.yml")
class MyTimestamp:
    my_datetime: MyDateTime = None
```

which can be constructed like so:

```python
my_timestamp = MyTimestamp(datetime.now())
```

to save this `sample.yml` file:

```yaml
my_datetime: 2019-01-30T23:17:45
```

that can be loaded as follows:

```python
>>> my_timestamp = MyTimestamp()
>>> my_timestamp.my_datetime
datetime.datetime(2019, 1, 30, 23, 17, 45)
```

# Registration

If you'd rather not have to modify your own classes (or don't have control over the source of a class), you can also register a custom converter for any class:

```
#!python hl_lines="9 14"
from datetime import datetime

from datafiles import converters, datafile


class DateTimeConverter(converters.Converter):

    @classmethod
    def to_preserialization_data(cls, python_value, **kwargs):
        # Convert `datetime` to a value that can be serialized
        return python_value.isoformat()

    @classmethod
    def to_python_value(cls, deserialized_data, **kwargs):
        # Convert file value back into a `datetime` object
        return datetime.fromisoformat(deserialized_data)


converters.register(datetime, DateTimeConverter)


@datafile("sample.yml")
class MyTimestamp:
    my_datetime: datetime = None
```

which can be constructed like so:

```python
my_timestamp = MyTimestamp(datetime.now())
```

to save this `sample.yml` file:

```yaml
my_datetime: 2019-01-30T23:18:30
```

that can be loaded as follows:

```python
>>> my_timestamp = MyTimestamp()
>>> my_timestamp.my_datetime
datetime.datetime(2019, 1, 30, 23, 18, 30)
```
