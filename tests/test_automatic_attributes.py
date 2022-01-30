# pylint: disable=unused-variable


from datafiles import datafile
from datafiles.utils import logbreak


@datafile("../tmp/{self.name}.yml", infer=True)
class Sample:
    name: str


def describe_infer():
    def with_builtin(expect):
        sample = Sample("abc")

        sample.datafile.text = "count: 1"

        logbreak("Getting attribute")
        expect(sample.count) == 1

        logbreak("Setting attribute")
        sample.count = 4.2

        logbreak("Getting attribute")
        expect(sample.count) == 4

    def with_empty_list(expect):
        sample = Sample("abc")

        sample.datafile.text = "empty_items: []"

        logbreak("Getting attribute")
        expect(sample.empty_items) == []

        logbreak("Setting attribute")
        sample.empty_items.append(4.2)
        sample.empty_items.append("abc")

        logbreak("Getting attribute")
        expect(sample.empty_items) == [4.2, "abc"]

    def with_homogeneous_list(expect):
        sample = Sample("abc")

        sample.datafile.text = "same_items: [1, 2]"

        logbreak("Getting attribute")
        expect(sample.same_items) == [1, 2]

        logbreak("Setting attribute")
        sample.same_items.append(3.2)

        logbreak("Getting attribute")
        expect(sample.same_items) == [1, 2, 3]

    def with_heterogeneous_list(expect):
        sample = Sample("abc")

        sample.datafile.text = "mixed_items: [1, 'abc']"

        logbreak("Getting attribute")
        expect(sample.mixed_items) == [1, "abc"]

        logbreak("Setting attribute")
        sample.mixed_items.append(3.2)

        logbreak("Getting attribute")
        expect(sample.mixed_items) == [1, "abc", 3.2]

    def with_dict(expect):
        sample = Sample("abc")

        sample.datafile.text = "data: {'a': 1}"

        logbreak("Getting attribute")
        expect(sample.data) == {"a": 1}

        logbreak("Setting attribute")
        sample.data["b"] = 2.3

        logbreak("Getting attribute")
        expect(sample.data) == {"a": 1, "b": 2.3}
