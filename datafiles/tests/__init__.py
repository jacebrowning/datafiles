"""Unit tests for the package."""

import sys

import pytest

xfail_without_pep_604 = pytest.mark.xfail(
    sys.version_info < (3, 10),
    reason="Union types (PEP 604) are not available in Python 3.9 and earlier",
)

xfail_without_type_names = pytest.mark.xfail(
    sys.version_info < (3, 10),
    reason="Types lack a __name__ in Python 3.9 and earlier",
)
