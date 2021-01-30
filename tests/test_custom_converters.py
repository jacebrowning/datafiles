# pylint: disable=arguments-differ

from datetime import datetime

from datafiles import Missing, converters, datafile


class MyDateTime(converters.Converter, datetime):
    """A custom class modified to support serialization."""

    @classmethod
    def to_preserialization_data(cls, python_value, **_kwargs):
        return python_value.isoformat()

    @classmethod
    def to_python_value(cls, deserialized_data, **_kwargs):
        return MyDateTime.fromisoformat(deserialized_data)


class DateTimeConverter(converters.Converter):
    """A converter to serialize a custom class."""

    @classmethod
    def to_preserialization_data(cls, python_value, **_kwargs):
        return python_value.isoformat()

    @classmethod
    def to_python_value(cls, deserialized_data, **_kwargs):
        return datetime.fromisoformat(deserialized_data)


def test_extension(expect):
    @datafile("../tmp/sample.yml")
    class Timestamp:
        dt: MyDateTime

    ts = Timestamp(datetime(2019, 1, 29))
    expect(ts.datafile.text) == "dt: '2019-01-29T00:00:00'\n"

    ts = Timestamp(Missing)
    expect(ts.dt) == datetime(2019, 1, 29)

    ts.datafile.text = "dt: '2019-01-11T00:00:00'\n"
    expect(ts.dt.day) == 11


def test_extension_with_default(expect):
    @datafile("../tmp/sample.yml")
    class Timestamp:
        dt: MyDateTime = None

    ts = Timestamp(datetime(2019, 1, 29))
    expect(ts.datafile.text) == "dt: '2019-01-29T00:00:00'\n"

    ts = Timestamp()
    expect(ts.dt) == datetime(2019, 1, 29)

    ts.datafile.text = "dt: '2019-01-11T00:00:00'\n"
    expect(ts.dt.day) == 11


def test_registration(expect):

    converters.register(datetime, DateTimeConverter)

    @datafile("../tmp/sample.yml")
    class Timestamp:
        dt: datetime

    ts = Timestamp(datetime(2019, 1, 29))
    expect(ts.datafile.text) == "dt: '2019-01-29T00:00:00'\n"

    ts = Timestamp(Missing)
    expect(ts.dt) == datetime(2019, 1, 29)

    ts.datafile.text = "dt: '2019-01-22T00:00:00'\n"
    expect(ts.dt.day) == 22


def test_registration_with_default(expect):

    converters.register(datetime, DateTimeConverter)

    @datafile("../tmp/sample.yml")
    class Timestamp:
        dt: datetime = None

    ts = Timestamp(datetime(2019, 1, 29))
    expect(ts.datafile.text) == "dt: '2019-01-29T00:00:00'\n"

    ts = Timestamp()
    expect(ts.dt) == datetime(2019, 1, 29)

    ts.datafile.text = "dt: '2019-01-22T00:00:00'\n"
    expect(ts.dt.day) == 22
