from collections import defaultdict


class OpposingTraitController:
    def __init__(self):
        self._oppositions = defaultdict(list)

    def addPair(self, value_1, value_2):
        self._oppositions[value_1].append(value_2)
        self._oppositions[value_2].append(value_1)

    def areOpposed(self, value_1, value_2):
        return value_2 in self._oppositions.get(value_1, [])