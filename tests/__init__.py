"""Integration tests for the package."""

import sys

import pytest


xfail_on_latest = pytest.mark.xfail(
    sys.version_info >= (3, 10),
    reason="Python 3.10+ cannot annotations for locally-defined types",
)
