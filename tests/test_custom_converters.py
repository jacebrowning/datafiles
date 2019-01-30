# pylint: disable=arguments-differ,unused-argument

from datetime import datetime

import pytest

from datafiles import converters, datafile


class MyDateTimeConverter(converters.Converter):
    """A converter to serialize a custom class."""

    @classmethod
    def to_preserialization_data(cls, python_value, **kwargs):
        return python_value.isoformat()

    @classmethod
    def to_python_value(cls, deserialized_data, **kwargs):
        return MyDateTime.fromisoformat(deserialized_data)


class MyDateTime(converters.Converter, datetime):
    """A custom class modified to support serialization."""

    @classmethod
    def to_preserialization_data(cls, python_value, **kwargs):
        return python_value.isoformat()

    @classmethod
    def to_python_value(cls, deserialized_data, **kwargs):
        return MyDateTime.fromisoformat(deserialized_data)


@pytest.mark.flaky
def test_extensiion(expect):
    @datafile("../tmp/sample.yml")
    class Timestamp:
        dt: MyDateTime

    ts = Timestamp(datetime(2019, 1, 29))

    expect(ts.datafile.text) == "dt: '2019-01-29T00:00:00'\n"

    ts.datafile.text = "dt: '2019-01-11T00:00:00'\n"

    expect(ts.dt.day) == 11


@pytest.mark.flaky
def test_registration(expect):

    converters.register(datetime, MyDateTimeConverter)

    @datafile("../tmp/sample.yml")
    class Timestamp:
        dt: datetime

    ts = Timestamp(datetime(2019, 1, 29))

    expect(ts.datafile.text) == "dt: '2019-01-29T00:00:00'\n"

    ts.datafile.text = "dt: '2019-01-22T00:00:00'\n"

    expect(ts.dt.day) == 22
