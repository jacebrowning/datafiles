from dataclasses import dataclass, field
from typing import List, Optional

from datafiles import datafile


def test_init():
    @dataclass
    class Item:

        required: int
        optional: Optional[int]
        default: int = 42

    @datafile('../tmp/{self.key}.yml', defaults=True)
    class Sample:

        key: str

        item_required: Item
        item_optional: Optional[Item]
        items_required: List[Item]
        item_default: Item = Item(1, None)
        items_default: List[Item] = field(default_factory=list)

    Sample('profiling', Item(2, None), None, [Item(3, None)])
