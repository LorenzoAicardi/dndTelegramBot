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

    # def addXp(self, xp: int):
    #     oldXp = self.stats.xp
    #     self.stats.xp = self.stats.xp + xp
    #
    #     milestones = [300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000, 100000, 120000,
    #                   140000, 165000, 195000, 225000, 265000, 305000, 355000]
    #     for i in milestones:
    #         if oldXp < i <= self.stats.xp:
    #             self.lvlUp()
    #
    # def lvlUp(self):  # everything that happens when a character levels up.
    #     self.stats.lvl += 1
    #     self.stats.hd_number += 1  # player gains one hit die
    #     self.stats.max_hp += + Dice.roll("d8", 0) + self.stats.constMod  # hp buff from level up
    #     self.stats.hp += + Dice.roll("d8", 0) + self.stats.constMod
    #     self.stats.lvlUpPoints += 2
    #
    #     # every 4 levels from the first, profBonus increases by one. (5/4 = 1 with 1 spare, 9/4 = 2 with 1 spare, ...)
    #     if self.stats.lvl % 4 == 1:
    #         self.stats.profBonus += 1
    #
    #     # TODO: ADD SPELL SLOTS PER LEVEL
    #
    # def lvlUpStats(self, statsUp: []):
    #     if self.stats.lvlUpPoints == 0:
    #         return "You can't level up any stats right now!"
    #     else:  # TODO: LOOKS AWFUL WITH AN IF ELSE BUT I DON'T KNOW ANOTHER WAY OF DOING IT
    #         self.stats.lvlUpPoints -= 2
    #         for i in range(2):
    #             if statsUp[i] == "Strength":
    #                 self.stats.strength += 1
    #             elif statsUp[i] == "Dexterity":
    #                 self.stats.dex += 1
    #             elif statsUp[i] == "Constitution":
    #                 self.stats.const += 1
    #             elif statsUp[i] == "Intelligence":
    #                 self.stats.intl += 1
    #             elif statsUp[i] == "Wisdom":
    #                 self.stats.wis += 1
    #             elif statsUp[i] == "Charisma":
    #                 self.stats.cha += 1
    #
    #         self.stats.setModifiers()

    # def shortRest(self, hd_num: int):
    #     if hd_num > self.stats.hd_number:
    #         return "You can't throw more hit dice than you currently have!"
    #     self.stats.hd_number -= hd_num
    #     hp = self.stats.constMod
    #     for i in range(hd_num):
    #         hp += Dice.roll(self.stats.hd, 0)
    #     self.stats.hp += hp
    #     return "Rest was successful."

    # def longRest(self, hd_num: int):
    #     self.stats.hp = self.stats.max_hp  # restore all hp
    #     if hd_num > self.stats.max_hd/2:
    #         return "You can't restore that many hit dice!"
    #     self.stats.hd_number += hd_num

    # def takeDamage(self, damage: []):
    #     # for now, just takes into account the damage value. If needed, put damage
    #     # type too (with respective modifier).
    #     attempt = Dice.roll("d20", 0)
    #     if attempt < self.stats.armClass:
    #         return "The attack missed."
    #     base_damage = damage[0]
    #     total_damage = 0
    #     for i in range(1, len(damage), 2):
    #         if damage[i+1] in self.damage_immunities:
    #             pass
    #         elif damage[i+1] in self.damage_vulnerabilities:
    #             total_damage += damage[i]*2
    #         elif damage[i + 1] in self.damage_resistances:
    #             total_damage += damage[i]/2
    #         else:
    #             total_damage += damage[i]
    #     self.stats.hp = self.stats.hp - (base_damage + total_damage)
    #     # TODO: make the character react accordingly in case the hp becomes <= 0.
    #     if self.stats.hp <= 0:
    #         msg = "Oh no! " + self.name + " has died!"
    #         return msg

    # def heal(self, heal: int):
    #     self.stats.hp = self.stats.hp + heal

    def getStats(self):
        return self.stats

    def json(self):
        return json.dumps(self.__dict__)  # returns the attributes of the class Character as a dictionary. Useful for
        # saving the character attributes on the json file for the campaign.
