import json
import os
from random import randint
import yaml

from classes import Wealth
from classes import Adv_Gear
from classes import Tool
from classes import Armor
from classes import Weapon
from classes import Spell
from classes import JSONEncoder
from classes.JSONEncoder import MyEncoder
from classes import Pack
# import Wealth
# import Adv_Gear
# import Tool
# import Armor
# import Weapon
# import Spell
# import JSONEncoder
# from JSONEncoder import MyEncoder
# import Pack


class Equipment:
    # wealth: Wealth = Wealth.Wealth(0, 0, 0, 0, 0)
    # armor: list[Armor] = field(default_factory=list)
    # weapons: list[Weapon] = field(default_factory=list)
    # spellCast: list[Spell] = field(default_factory=list)
    # advGear: list[Adv_Gear] = field(default_factory=list)
    # tools: list[Tool] = field(default_factory=list)
    # spells: list[Spell] = field(default_factory=list)

    # trinkets: list[Weapon] = field(default_factory=list)

    def __init__(self, wealth: Wealth, armor, weapons, spellCast, advGear, tools, spells):
        self.wealth = wealth
        self.armor = armor
        self.weapons = weapons
        self.spellCast = spellCast
        self.advGear = advGear
        self.tools = tools
        self.spells = spells

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

        noItem = ""

        for i in range(len(eq_list)):
            item = next(iter(item for item in req_eq if item['name'] == eq_list[i]), None)
            if item:
                if item["equipment_category"]["index"] == 'armor':
                    armor = Armor.Armor(item["name"], Wealth.Wealth(0, 0, 0, item["cost"]["quantity"], 0),
                                        item["armor_class"]["base"], item["str_minimum"], item["weight"])
                    self.armor.append(armor)  # create method that appends the armor piece
                elif item["equipment_category"]["index"] == 'weapon':
                    properties = []
                    for prop in item["properties"]:
                        properties.append(prop["name"])
                    weapon = Weapon.Weapon(item["name"], Wealth.Wealth(0, 0, 0, item["cost"]["quantity"], 0),
                                           item["damage"]["damage_dice"], item["damage"]["damage_type"]["name"],
                                           item["weight"], properties)
                    self.weapons.append(weapon)  # same thing here
                elif item["equipment_category"]["index"] == 'adventuring-gear':
                    if item["gear_category"]["name"] == "Equipment Packs":
                        adv_g = Pack.Pack(item["name"], Wealth.Wealth(0, 0, 0, item["cost"]["quantity"], 0), item["gear_category"]["name"],
                                          item["contents"])
                    else:
                        adv_g = Adv_Gear.Adv_Gear(item["name"], item["gear_category"]["name"],
                                              Wealth.Wealth(0, 0, 0, item["cost"]["quantity"], 0), item["weight"])
                    self.advGear.append(adv_g)
                elif item["equipment_category"]["index"] == 'tools':
                    tool = Tool.Tool(item["name"], item["tool_category"]["name"],
                                     Wealth.Wealth(0, 0, 0, item["cost"]["quantity"], 0),
                                     item["weight"])
                    self.tools.append(tool)
            else:
                noItem = "It seems that in your starting equipment choice you picked a 'generic' item. " \
                       "The DM will provide you the right type of item."

        return noItem

    def toJson(self):
        return json.dumps(self.__dict__, sort_keys=True, indent=4, ensure_ascii=False)


def toString(equipment):
    e = json.loads(MyEncoder().encode(equipment).replace("\"", '"'))
    for k in list(e["wealth"]):
        if e["wealth"][k] == 0:
            del e["wealth"][k]

    for item in list(e["armor"]):
        if len(e["armor"]) != 0:
            for k in list(item["cost"]):
                if item["cost"][k] == 0:
                    del item["cost"][k]

    for item in list(e["weapons"]):
        if len(e["weapons"]) != 0:
            for k in list(item["cost"]):
                if item["cost"][k] == 0:
                    del item["cost"][k]

    for item in list(e["advGear"]):
        if len(e["advGear"]) != 0:
            for k in list(item["cost"]):
                if item["cost"][k] == 0:
                    del item["cost"][k]

    for item in list(e["tools"]):
        if len(e["tools"]) != 0:
            for k in list(item["cost"]):
                if item["cost"][k] == 0:
                    del item["cost"][k]

    e = yaml.safe_dump(e, sort_keys=False, allow_unicode=True, default_flow_style=False)
    e = e.replace("wealth", "<b>Wealth</b>")
    e = e.replace("armor", "\n<b>Armor</b>", 1)
    e = e.replace("name", "<i>Name</i>")
    e = e.replace("armorClass", "<i>Armor class</i>")
    e = e.replace("strength", "<i>Strength</i>")
    e = e.replace("weight", "<i>Weight</i>")
    e = e.replace("spellCast", "<b>\nSpell Cast</b>")
    e = e.replace("advGear", "\n<b>Adventuring gear</b>")
    e = e.replace("tools", "\n<b>Tools</b>")
    e = e.replace("spells", "\n<b>Spells</b>")
    e = e.replace("gear_category", "<i>Gear category</i>")
    e = e.replace("contents", "<i>Contents</i>")
    e = e.replace("cost", "<i>Cost</i>")
    e = e.replace("weapons", "<b>\nWeapons</b>")
    e = e.replace("[]", "None")
    return e


def main():
    equipment = Equipment(Wealth.Wealth(0, 0, 0, 0, 0), ["asd"], ["sdsa"], ["dfsd"], ["fdsfsd"], ["dsfdss"], ["dfdsfs"])
    e = toString(equipment)
    print(e)

if __name__ == "__main__":
    main()