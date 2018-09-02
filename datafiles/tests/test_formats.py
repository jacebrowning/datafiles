# pylint: disable=unused-variable

from pathlib import Path

from datafiles import formats


def describe_deserialize():
    def it_rejects_unknown_extensions(expect):
        with expect.raises(ValueError):
            formats.deserialize(Path(), '.xyz')
