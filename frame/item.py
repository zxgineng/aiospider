from typing import List
from collections import OrderedDict


class Item:
    row: List[str] = list()

    def __init__(self):
        self.value_map = OrderedDict()
        for r in self.row:
            self.value_map[r] = None

    def __getitem__(self, item):
        return self.value_map[item]

    def __setitem__(self, key, value):
        assert key in self.value_map
        self.value_map[key] = value

    def __iter__(self):
        return iter(self.value_map)
