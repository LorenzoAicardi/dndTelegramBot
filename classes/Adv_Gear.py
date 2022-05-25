from . import Wealth
# import Wealth


class Adv_Gear:

    def __init__(self, name, gear_cat: str, cost: Wealth, weight):
        self.name = name
        self.gear_category = gear_cat
        self.cost = cost
        self.weight = weight

    def __eq__(self, other):
        if not isinstance(other, Adv_Gear):
            return NotImplemented

        return (
            self.name == other.name and
            self.gear_category == other.gear_category and
            self.cost == other.cost and
            self.weight == other.weight
        )
