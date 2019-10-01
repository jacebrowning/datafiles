# pylint: disable=arguments-differ,no-member

from __future__ import annotations  # this breaks custom converter lookup

from typing import Optional

import pytest

from datafiles import datafile

from .test_custom_converters import MyDateTime


@pytest.mark.flaky
def test_extension(expect):
    @datafile("../tmp/sample.yml")
    class MyObject:
        value: MyDateTime

    x = MyObject(MyDateTime(2019, 1, 29))
    expect(x.datafile.text) == "value: '2019-01-29T00:00:00'\n"


@pytest.mark.xfail(reason='https://github.com/jacebrowning/datafiles/issues/131')
def test_optional(expect):
    @datafile("../tmp/sample.yml")
    class MyObject:
        value: Optional[int]

    x = MyObject(42)
    expect(x.datafile.text) == "value: 42'\n"
