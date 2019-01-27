# pylint: disable=unused-variable

import os

import pytest

from datafiles import datafile


@datafile('../tmp/{self.name}.yml', auto_attr=True, auto_save=False)
class Sample:
    name: str


def describe_automatic_attributes():
    @pytest.mark.xfail(bool(os.getenv('CI')), reason="Flaky on CI")
    def with_builtin(expect, logbreak):
        sample = Sample('abc')

        sample.datafile.text = "count: 1"

        logbreak("Getting attribute")
        expect(sample.count) == 1

        logbreak("Setting attribute")
        sample.count = 4.2

        logbreak("Getting attribute")
        expect(sample.count) == 4
