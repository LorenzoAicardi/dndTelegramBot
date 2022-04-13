import collections
import json
import os
import random
import Armor
import Statistics
import Description
import Equipment


class Character:
    playerID = None
    name = None
    stats = Statistics.Statistics(1, 0, 0, 0, 0, 0, 0, 0)
    description = Description.Description("", "", "", "", "", "", "", "")
    equipment = Equipment.Equipment()  # TODO: add parameters
    race = None
    _class = None

    def __init__(self, playerID, name):
        self.playerID = playerID
        self.name = name

    def setInitialStats(self, race: str, _class: str):  # senza ArmorClass, definito dopo
        self.race = race
        self._class = _class
        if race == "human":
            self.stats.str = self.stats.str + 1
            self.stats.dex = self.stats.dex + 1
            self.stats.const = self.stats.const + 1
            self.stats.intl = self.stats.intl + 1
            self.stats.wis = self.stats.wis + 1
            self.stats.cha = self.stats.cha + 1
            self.stats.speed = 30
        elif race == "dwarf":
            self.stats.const = self.stats.const + 2
            self.stats.speed = 25
        elif race == "elf":
            self.stats.dex = self.stats.dex + 2
            self.stats.speed = 30
        elif race == "halfling":
            self.stats.dex = self.stats.dex + 2
            self.stats.speed = 25

        self.stats.setModifiers()

        if _class == "fighter":
            self.stats.str = self.stats.str + 2
            self.stats.const = self.stats.const + 2
            self.stats.hp = 10 + self.stats.constMod
            self.stats.hd = "d10"
        elif _class == "cleric":
            self.stats.wis = self.stats.wis + 3
            self.stats.hp = 8 + self.stats.constMod
            self.stats.hd = "d8"
        elif _class == "rogue":
            self.stats.hp = 8 + self.stats.constMod
            self.stats.dex = self.stats.dex + 2
            self.stats.hd = "d8"
        elif _class == "wizard":
            self.stats.intl = self.stats.intl + 2
            self.stats.wis = self.stats.wis + 2
            self.stats.hp = 6 + self.stats.constMod
            self.stats.hd = "d6"

    def setInitialEquipment(self, equipment: str):  # the order is: armor, melee weapon, ranged weapons, trinkets
        eq_list = equipment.split(", ")
        if self._class == "cleric" or self._class == "fighter":  # set initial wealth
            s = 0
            for i in range(5):
                s = s + random.randint(1, 4)
            self.equipment.wealth.addGp(10 * s)
        elif self._class == "cleric" or self._class == "fighter":
            s = 0
            for i in range(4):
                s = s + random.randint(1, 4)
            self.equipment.wealth.addGp(10 * s)

        with open(os.path.dirname(os.getcwd()) + "/resources/5e-SRD-Equipment.json", "r") as read_file:  # set init
            # equip
            req_eq = json.load(read_file)

        for i in range(len(eq_list)):
            # for each item in the list of items the player wants to begin with, I insert
            # every piece of equipment inside the player's inventory
            item = next((item for item in req_eq if item["name"] == eq_list[i]), None)
            if item:
                match item["equipment_category"]["index"]:
                    case 'armor':
                        self.equipment.armor.name = item["name"]
                        self.equipment.armor.cost = item["cost"]["quantity"]
                        self.equipment.armor.armClass = item["armor_class"]["base"]
                        self.equipment.armor.strength = item["str_minimum"]
                        self.equipment.armor.weight = item["weight"]
                    case 'weapon':
                        self.equipment.weapons.name = item["name"]
                        self.equipment.weapons.cost = item["cost"]["quantity"]
                        self.equipment.weapons.damage = item["damage"]
                        self.equipment.weapons.weight = item["weight"]
                        prop = []
                        for property in item["properties"]:
                            prop = prop + property["name"]
                        self.equipment.weapons.properties = prop
                    case 'adventuring-gear':
                        return  # TODO: complete with adv gear
                    case 'tools':
                        return  # TODO: complete with tools (still deciding whether or not to add mounts)

    def takeDamage(self, damage: int):
        self.stats.hp = self.stats.hp - damage

    def heal(self, heal: int):
        self.stats.hp = self.stats.hp + heal

    def getStats(self):
        return self.stats

    def json(self):
        return json.dumps(self.__dict__)
