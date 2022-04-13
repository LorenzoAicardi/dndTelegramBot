import Wealth


class Armor:

    name = None
    cost = Wealth.Wealth()
    armorClass = 0
    strength = 0
    weight = 0

    def __init__(self, name):
        self.name = name

