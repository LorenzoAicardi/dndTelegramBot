import utils
import json


class Weapon:
    def __init__(self, name, cost, damage, weight, properties):
        self.name = name
        self.cost = cost
        self.damage = damage,
        self.weight = weight,
        self.properties = properties

    def prints(self):
        print(self.name)
        print(self.cost)
        print(self.damage)
        print(self.weight)
        print(self.properties)


with open("../resources/equipment.json", "r") as read_file:
    data = json.load(read_file)


weapon = Weapon("club", data["simpleMeleeWeapons"]["club"]["cost"],
                data["simpleMeleeWeapons"]["club"]["damage"], data["simpleMeleeWeapons"]["club"]["weight"],
                data["simpleMeleeWeapons"]["club"]["properties"])

weapon.prints()

#OK!