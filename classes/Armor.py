from . import Wealth


class Armor:

    name = None
    cost = Wealth.Wealth(0, 0, 0, 0, 0)
    armorClass = 0
    strength = 0
    weight = 0

    def __init__(self, name, cost: Wealth, armorClass, strength, weight):
        self.name = name
        self.cost = cost
        self.armorClass = armorClass
        self.strength = strength
        self.weight = weight

    def __eq__(self, other):
        if not isinstance(other, Armor):
            return NotImplemented

        return (self.name == other.name and
                self.cost == other.cost and
                self.armorClass == other.armorClass and
                self.strength == other.strength and
                self.weight == other.weight)

