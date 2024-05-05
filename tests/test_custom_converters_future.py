"""Tests demonstrating failures caused by the PEP 563 behavior."""

from __future__ import annotations

from typing import Optional

import pytest

from datafiles import datafile


def test_optional_type(expect):
    @datafile("../tmp/sample.yml")
    class MyObject:

        # This will fail because the annotation is evaluated as 'Optional[int]'
        # rather than `Union[int, None]` as when evaluated eagerly.
        value1: Optional[int]

    x = MyObject(42)
    expect(x.datafile.text) == "value1: 42\n"


@pytest.mark.xfail(reason="https://github.com/jacebrowning/datafiles/issues/131")
def test_nested_type(expect):
    class Nested:
        pass

    @datafile("../tmp/sample.yml")
    class MyObject:
        value1: int

        # This will fail even if `get_type_hints()`` is provided this module
        # as `globals` because `Nested` is defined below module scope.
        value2: Nested = Nested()

    x = MyObject(42)
    expect(x.datafile.text) == "value1: 42\n"
