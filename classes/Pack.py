from classes import Wealth


class Pack:

    def __init__(self, name, cost: Wealth, gear_category, contents):
        self.name = name
        self.cost = cost
        self.gear_category = gear_category
        self.contents = contents