"""Integration tests for the package."""

import sys

import pytest

xfail_with_pep_563 = pytest.mark.xfail(
    sys.version_info >= (3, 12),
    reason="Postponed evaluations (PEP 563) are unable to resolve locally-defined types",
)
