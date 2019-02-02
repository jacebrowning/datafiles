# pylint: disable=unused-variable


import pytest

from datafiles import datafile


@datafile('../tmp/{self.name}.yml', auto_attr=True, auto_save=False)
class Sample:
    name: str


def describe_automatic_attributes():
    @pytest.mark.flaky
    def with_builtin(expect, logbreak):
        sample = Sample('abc')

        sample.datafile.text = "count: 1"

        logbreak("Getting attribute")
        expect(sample.count) == 1

        logbreak("Setting attribute")
        sample.count = 4.2

        logbreak("Getting attribute")
        expect(sample.count) == 4

    @pytest.mark.flaky
    def with_homogeneous_list(expect, logbreak):
        sample = Sample('abc')

        sample.datafile.text = "items: [1, 2]"

        logbreak("Getting attribute")
        expect(sample.items) == [1, 2]

        logbreak("Setting attribute")
        sample.items.append(3.2)

        logbreak("Getting attribute")
        expect(sample.items) == [1, 2, 3]
