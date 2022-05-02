import json
import os
from dataclasses import dataclass
from dataclasses import field
from random import random
from random import randint

from . import Wealth, Adv_Gear, Tool
from . import Armor
from . import Weapon
from . import Spell


@dataclass()
class Equipment:

    wealth: Wealth = Wealth.Wealth(0, 0, 0, 0, 0)
    armor: list[Armor] = field(default_factory=list)
    weapons: list[Weapon] = field(default_factory=list)
    spellCast: list[Spell] = field(default_factory=list)
    advGear: list[Adv_Gear] = field(default_factory=list)
    tools: list[Tool] = field(default_factory=list)
    spells: list[Spell] = field(default_factory=list)
    # trinkets: list[Weapon] = field(default_factory=list)

    def setInitialEquipment(self, race: str, _class: str, eq_list: []):
        if _class == "cleric" or _class == "fighter":  # set initial wealth
            s = 0
            for i in range(5):
                s = s + randint(1, 4)
            self.wealth.addGp(10 * s)
        elif _class == "wizard" or _class == "rogue":
            s = 0
            for i in range(4):
                s = s + randint(1, 4)
            self.wealth.addGp(10 * s)

        with open(os.path.dirname(os.getcwd()) + "/resources/5e-SRD-Equipment.json", "r") as read_file:
            req_eq = json.load(read_file)  # THIS IS AN ARRAY OF DICTS

        for i in range(len(eq_list)):
            item = next(iter(item for item in req_eq if item['name'] == eq_list[i]), None)
            if item:
                if item["equipment_category"]["index"] == 'armor':
                    armor = Armor.Armor(item["name"], Wealth.Wealth(0, 0, 0, item["cost"]["quantity"], 0),
                                        item["armor_class"]["base"], item["str_minimum"], item["weight"])
                    self.armor.append(armor)  # create method that appends the armor piece
                elif item["equipment_category"]["index"] == 'weapon':
                    properties = []  # TODO: redo according to how weapon is in the json
                    for prop in item["properties"]:
                        properties = properties + prop["name"]
                    weapon = Weapon.Weapon(item["name"], Wealth.Wealth(0, 0, 0, item["cost"]["quantity"], 0),
                                           item["damage"]["damage_dice"], item["damage"]["damage_type"]["name"],
                                           item["weight"], properties)
                    self.weapons.append(weapon)  # same thing here
                elif item["equipment_category"]["index"] == 'adventuring-gear':
                    adv_g = Adv_Gear.Adv_Gear(item["name"], item["gear_category"]["name"],
                                              Wealth.Wealth(0, 0, 0, item["cost"]["quantity"], 0), item["weight"])
                    self.advGear.append(adv_g)
                elif item["equipment_category"]["index"] == 'tools':
                    tool = Tool.Tool(item["name"], item["tool_category"]["name"],
                                     Wealth.Wealth(0, 0, 0, item["cost"]["quantity"], 0),
                                     item["weight"])
                    self.tools.append(tool)

    # def appendArmor, appendWeapon
