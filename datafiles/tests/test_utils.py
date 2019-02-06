# pylint: disable=unused-variable

from datafiles.utils import recursive_update


def describe_recursive_update():
    def it_preserves_root_id(expect):
        old = {}  # type: ignore
        new = {'a': 1}
        id_ = id(old)

        old = recursive_update(old, new)

        expect(old) == new
        expect(id(old)) == id_

    def it_preserves_nested_dict_id(expect):
        old = {'a': {'b': 1}}
        new = {'a': {'b': 2}}
        id_ = id(old['a'])

        old = recursive_update(old, new)

        expect(old) == new
        expect(id(old['a'])) == id_

    def it_preserves_nested_list_id(expect):
        old = {'a': [1]}
        new = {'a': [2]}
        id_ = id(old['a'])

        old = recursive_update(old, new)

        expect(old) == new
        expect(id(old['a'])) == id_

    def it_adds_missing_dict(expect):
        old = {}  # type: ignore
        new = {'a': {'b': 2}}

        old = recursive_update(old, new)

        expect(old) == new

    def it_adds_missing_list(expect):
        old = {}  # type: ignore
        new = {'a': [1]}

        old = recursive_update(old, new)

        expect(old) == new
