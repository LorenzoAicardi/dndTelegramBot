from . import Adv_Gear, Spell
from . import Armor
from . import Tool
from . import Wealth
from . import Weapon
import json
import os
import random
from . import Dice
from . import Description
from . import Equipment
from . import Statistics


# Most of the methods of the class are called by the DM: the player can't really decide on his own to upgrade his level
# or give himself an item.

class Character:
    playerID = None
    name = None
    stats = Statistics.Statistics(1, 0, 0, 2, 0, 0, 0, 0)
    # description = Description.Description("", "", "", "", "", "", "", "") don't know if I have to add this
    equipment = Equipment.Equipment()
    race = None
    _class = None

    def __init__(self, playerID: str, name: str):
        self.playerID = playerID
        self.name = name

    def setInitialStats(self, race: str, _class: str):  # later on armorClass will be defined
        self.race = race
        self._class = _class
        self.stats.lvl = 1  # stuff to be done immediately after char creation
        self.stats.setStats(race, _class)
        self.stats.setModifiers()

    def setInitialEquipment(self, equipment: str):  # the order is: armor, melee weapon, ranged weapons, trinkets
        eq_list = equipment.split(", ")  # still don't know whether or not the arg passed is a str or a list
        self.equipment.setInitialEquipment(self.race, self._class, eq_list)

    def setInitialSpells(self, spells: []):
        for i in range(len(spells)):
            spell = Spell.Spell(spells[i])
            if spell.level != 0 or spell.level != 1:
                return "The level of the spell is too high!"
            tmp = self.stats.curr_used_spell_slots[str(spell.level)] + 1
            if tmp > self.stats.spell_slots[str(spell.level)]:
                return "You can't add that many spells!"
            self.equipment.spells.append(spell)
            self.stats.curr_used_spell_slots[str(spell.level)] += 1

    def addSpell(self, spell: str):
        spell = Spell.Spell(spell)
        tmp = self.stats.curr_used_spell_slots[str(spell.level)] + 1
        if tmp > self.stats.spell_slots[str(spell.level)]:
            return "You can't add that many spells!"

        for obj in spell.classes:
            if self._class == obj["index"]:
                self.equipment.spells.append(spell)
                self.stats.curr_used_spell_slots[str(spell.level)] += 1
                return "Spell has been added successfully!"

        return "The chosen spell can't be added to a character of this class!"

    def addItem(self, item_name: str):
        with open(os.path.dirname(os.getcwd()) + "/resources/5e-SRD-Equipment.json", "r") as read_file:
            req_eq = json.load(read_file)

        item = next((item for item in req_eq if item['name'] == item_name), None)
        if item:
            if item["equipment_category"]["index"] == 'armor':
                armor = Armor.Armor(item["name"], Wealth.Wealth(0, 0, 0, item["cost"]["quantity"], 0),
                                    item["armor_class"]["base"], item["str_minimum"], item["weight"])
                self.equipment.armor.append(armor)  # create method that appends the armor piece
            elif item["equipment_category"]["index"] == 'weapon':  # TODO: redo according to how weapon is in the json
                properties = []
                for prop in item["properties"]:
                    properties.append(prop["name"])
                weapon = Weapon.Weapon(item["name"], Wealth.Wealth(0, item["cost"]["quantity"], 0, 0, 0),
                                       item["damage"]["damage_dice"], item["damage"]["damage_type"]["name"],
                                       item["weight"], properties)
                self.equipment.weapons.append(weapon)  # same thing here
            elif item["equipment_category"]["index"] == 'adventuring-gear':
                adv_g = Adv_Gear.Adv_Gear(item["name"], item["gear_category"]["name"],
                                          Wealth.Wealth(0, 0, 0, item["cost"]["quantity"], 0), item["weight"])
                self.equipment.advGear.append(adv_g)
            elif item["equipment_category"]["index"] == 'tools':
                tool = Tool.Tool(item["name"], item["tool_category"]["name"],
                                 Wealth.Wealth(0, 0, 0, item["cost"]["quantity"], 0),
                                 item["weight"])
                self.equipment.tools.append(tool)

    def rmItem(self, item_name: str):  # TODO: DEL FROM MEMORY REQ_EQ, OR MAKE IT GLOBAL ONCE AND FOR ALL
        with open(os.path.dirname(os.getcwd()) + "/resources/5e-SRD-Equipment.json", "r") as read_file:
            req_eq = json.load(read_file)

        item = next((item for item in req_eq if item['name'] == item_name), None)
        if item:
            if item["equipment_category"]["index"] == 'armor':
                a: Armor
                for a in self.equipment.armor:
                    if a.name == item["name"]:
                        self.equipment.weapons.remove(a)
                        return "Armor piece has been removed successfully!"
                return "No such armor piece has been found."
            elif item["equipment_category"]["index"] == 'weapon':
                w: Weapon
                for w in self.equipment.weapons:
                    if w.name == item["name"]:
                        self.equipment.weapons.remove(w)
                        return "Weapon has been removed successfully!"
                return "No such weapon has been found."
            elif item["equipment_category"]["index"] == 'adventuring-gear':
                ad: Adv_Gear
                for ad in self.equipment.advGear:
                    if ad.name == item["name"]:
                        self.equipment.weapons.remove(ad)
                        return "Adventuring gear has been removed successfully!"
                return "No such gear has been found."
            elif item["equipment_category"]["index"] == 'tools':
                t: Tool
                for t in self.equipment.tools:
                    if t.name == item["name"]:
                        self.equipment.weapons.remove(t)
                        return "Tool has been removed successfully!"
                return "No such tool has been found."

    def useSpell(self, spell):  # TODO: COMPLETE
        pass

    def useWeapon(self, weapon_name: str, mod: int):
        w: Weapon
        for w in self.equipment.weapons:
            if w.name == weapon_name:
                dmg = w.calcDamage()
                dmg[0] += mod  # increases the module of the damage by the modifier.
                return dmg  # THIS IS A LIST, THE FIRST ELEMENT IS THE AMOUNT OF DAMAGE DEALT, THE SECOND ELEMENT IS
                # THE TYPE OF DAMAGE DEALT
        return "No such weapon in inventory."

    def getStats(self):
        return self.stats

    def json(self):
        return json.dumps(self.__dict__)  # returns the attributes of the class Character as a dictionary. Useful for
        # saving the character attributes on the json file for the campaign.
