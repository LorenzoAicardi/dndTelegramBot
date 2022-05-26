from classes import Wealth
# import Wealth


class Tool:

    def __init__(self, name, tool_cat, cost: Wealth, weight):
        self.name = name
        self.tool_cat = tool_cat
        self.cost = cost
        self.weight = weight

    def __eq__(self, other):
        if not isinstance(other, Tool):
            return NotImplemented

        return (
            self.name == other.name and
            self.tool_cat == other.tool_cat and
            self.cost == other.cost and
            self.weight == other.weight
        )
