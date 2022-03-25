import utils
import json


class Weapon:
    def __init__(self, name, cost, damage, weight, properties):
        self.name = name
        self.cost = cost
        self.damage = damage,
        self.weight = weight,
        self.properties = properties

    def getDamage(self, damage):
        return self.damage

    #def property(self, properties):


with open("C:/Users/loren/Desktop/Università/3° anno/Progetto di ingegneria "
          "informatica/dndTelegramBot/resources/equipment.json", "r") as read_file:
    data = json.load(read_file)


weapon = Weapon("club", data["simpleMeleeWeapons"]["club"]["cost"],
                data["simpleMeleeWeapons"]["club"]["damage"], data["simpleMeleeWeapons"]["club"]["weight"],
                data["simpleMeleeWeapons"]["club"]["properties"])


#OK!