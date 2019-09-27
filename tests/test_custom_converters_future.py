# pylint: disable=arguments-differ

from __future__ import annotations  # this breaks custom converter lookup

from datetime import datetime

import pytest

from datafiles import Missing, datafile

from .test_custom_converters import MyDateTime


@pytest.mark.flaky
def test_extension(expect):
    @datafile("../tmp/sample.yml")
    class Timestamp:
        dt: MyDateTime

    ts = Timestamp(MyDateTime(2019, 1, 29))
    expect(ts.datafile.text) == "dt: '2019-01-29T00:00:00'\n"

    ts = Timestamp(Missing)  # type: ignore
    expect(ts.dt) == datetime(2019, 1, 29)

    ts.datafile.text = "dt: '2019-01-11T00:00:00'\n"
    expect(ts.dt.day) == 11
