# pylint: disable=unused-variable

from typing import Dict

from datafiles.utils import recursive_update


def describe_recursive_update():
    def describe_id_preservation():
        def with_dict(expect):
            old = {"my_dict": {"a": 1}}
            new = {"my_dict": {"a": 2}}
            previous_id = id(old["my_dict"])

            recursive_update(old, new)

            expect(old) == new
            expect(id(old["my_dict"])) == previous_id

        def with_dict_value(expect):
            old = {"my_dict": {"my_nested_dict": {"a": 1}}}
            new = {"my_dict": {"my_nested_dict": {"a": 2}}}
            previous_id = id(old["my_dict"]["my_nested_dict"])

            recursive_update(old, new)

            expect(old) == new
            expect(id(old["my_dict"]["my_nested_dict"])) == previous_id

        def with_list(expect):
            old = {"my_list": [1]}
            new = {"my_list": [2]}
            previous_id = id(old["my_list"])

            recursive_update(old, new)

            expect(old) == new
            expect(id(old["my_list"])) == previous_id

        def with_list_item(expect):
            old = {"my_list": [{"name": "John"}]}
            new = {"my_list": [{"name": "Jane"}]}
            previous_id = id(old["my_list"][0])

            recursive_update(old, new)

            expect(old) == new
            expect(id(old["my_list"][0])) == previous_id

        def with_nested_list(expect):
            old = {"my_dict": {"my_list": [{"name": "John"}]}}
            new = {"my_dict": {"my_list": [{"name": "Jane"}]}}
            previous_id = id(old["my_dict"]["my_list"][0])

            recursive_update(old, new)

            expect(old) == new
            expect(id(old["my_dict"]["my_list"][0])) == previous_id

    def describe_merge():
        def with_shoreter_list_into_longer(expect):
            old = {"my_list": [1, 2, 3]}
            new = {"my_list": [5, 6]}

            recursive_update(old, new)

            expect(old) == new

        def with_longer_list_into_shorter(expect):
            old = {"my_list": [1, 2]}
            new = {"my_list": [3, 4, 5]}

            recursive_update(old, new)

            expect(old) == new

    def describe_missing():
        def with_dict(expect):
            old: Dict = {}
            new = {"my_dict": {"a": 1}}

            recursive_update(old, new)

            expect(old) == new

        def with_list(expect):
            old: Dict = {}
            new = {"my_list": [1]}

            recursive_update(old, new)

            expect(old) == new

    def describe_extra():
        def with_dict(expect):
            old = {"my_dict": {"a": 1, "b": 2}}
            new = {"my_dict": {"a": 1}}

            recursive_update(old, new)

            expect(old) == new
