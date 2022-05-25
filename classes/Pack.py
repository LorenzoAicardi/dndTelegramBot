from classes import Wealth
# import Wealth


class Pack:

    def __init__(self, name, cost: Wealth, gear_category, contents):
        self.name = name
        self.cost = cost
        self.gear_category = gear_category
        cont = []
        for i in range(len(contents)):
            if isinstance(contents[i], dict):
                cont.append(contents[i]["item"]["name"])  # if it's a new campaign
            else:
                cont.append(contents[i])  # if I'm loading the campaign
        self.contents = cont
