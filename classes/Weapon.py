import utils
import json
from classes import Wealth
from classes import Dice


class Weapon:
    name = None
    cost = Wealth.Wealth(0, 0, 0, 0, 0)
    damage_dice = None
    damage_type = None
    weight = 0
    properties = None

    def __init__(self, name, cost, damage_dice: str, damage_type: str, weight, properties):
        self.name = name
        self.cost = cost
        self.damage_dice = damage_dice
        self.damage_type = damage_type
        self.weight = weight
        self.properties = properties

    def __eq__(self, other):
        if not isinstance(other, Weapon):
            return NotImplemented

        return (self.name == other.name and self.cost == other.cost and self.damage_dice == other.damage_dice
                and self.damage_type == other.damage_type and self.weight == other.weight and self.properties == other.properties)

    def calcDamage(self):
        damage_amount = 0
        tmp = self.damage_dice.split("d")  # tmp = [numofTimes, damage type]
        numOfDices = int(tmp[0])
        dice = "d" + tmp[1]
        for i in range(numOfDices):
            damage_amount += Dice.roll(dice, 0)
        damage = [damage_amount, self.damage_type]
        return damage


