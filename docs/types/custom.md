# Registration

Custom types can be saved and loaded by registering a new converter class:

```python
from datafiles import converters, datafile

from .my_models import MyDateTime


class MyDateTimeConverter(converters.String):

    @classmethod
    def to_preserialization_data(cls, python_value, **kwargs):
        # Convert `MyDateTime` to custom string format
        return python_value.to_custom_string_format()

    @classmethod
    def to_python_value(cls, deserialized_data, **kwargs):
        value = super().to_python_value(deserialized_data, **kwargs)
        # Convert custom string format back to `MyDateTime`
        return MyDateTime.from_custom_string_format(value)

converters.register(MyDateTime, MyDateTimeConverter)


@datafile("sample.yml")
class MyTimestamp:
    my_datetime: MyDateTime
```
