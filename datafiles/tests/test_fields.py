# pylint: disable=unused-variable

from datafiles import fields


class UnknownType:
    pass


def describe_map_type():
    def it_raises_exception_when_unmapped(expect):
        with expect.raises(ValueError):
            fields.map_type(UnknownType)
