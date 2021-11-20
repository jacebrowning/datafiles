# Custom Types

Additional types are supported though custom type as annotations.

## Single Inheritance

Custom types can be saved and loaded by extending one of the included converter classes:

| Class                  | Description                               |
| ---------------------- | ----------------------------------------- |
| `converters.Converter` | Base class for all converters.            |
| `converters.Boolean`   | Converts to `bool` before serialization.  |
| `converters.Integer`   | Converts to `int` before serialization.   |
| `converters.Float`     | Converts to `float` before serialization. |
| `converters.String`    | Converts to `str` before serialization.   |

For example, here is a custom converter that ensures floating point numbers are always rounded to two decimal places:

```python hl_lines="7"
from datafiles import converters


class RoundedFloat(converters.Float):

    @classmethod
    def to_preserialization_data(cls, python_value, **kwargs):
        number = super().to_preserialization_data(python_value, **kwargs)
        return round(number, 2)


@datafile("sample.yml")
class Result:
    total: RoundedFloat = 0.0
```

which can be constructed like so:

```python
result = Result(1.2345)
```

to save this `sample.yml` file:

```yaml
total: 1.23
```

that can be loaded as follows:

```python
>>> result = Result()
>>> result.total
1.23
```

## Multiple Inheritance

It's also possible to extend an existing class in order to have instances inherit the functionality of that class. For example, here is a custom converter based on the `datetime` class that serializes using the ISO format:

```python hl_lines="9 14"
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
class Timestamp:
    my_datetime: MyDateTime = None
```

which can be constructed like so:

```python
timestamp = Timestamp(datetime.now())
```

to save this `sample.yml` file:

```yaml
my_datetime: 2019-01-30T23:17:45
```

that can be loaded as follows:

```python
>>> timestamp = Timestamp()
>>> timestamp.my_datetime
datetime.datetime(2019, 1, 30, 23, 17, 45)
```

## Converter Registration

Finally, if you'd rather not have to modify your own classes (or don't have control over the source of a class), you can also register a custom converter for any class:

```python hl_lines="9 14"
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
class Timestamp:
    my_datetime: datetime = None
```

which can be constructed like so:

```python
timestamp = Timestamp(datetime.now())
```

to save this `sample.yml` file:

```yaml
my_datetime: 2019-01-30T23:18:30
```

that can be loaded as follows:

```python
>>> timestamp = Timestamp()
>>> timestamp.my_datetime
datetime.datetime(2019, 1, 30, 23, 18, 30)
```
