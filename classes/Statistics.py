import json
import random
import json
import dataclasses

from classes import Dice
import colorama
from collections import OrderedDict


@dataclasses.dataclass()
class Statistics:

    def __init__(self, lvl, xp, ins, profBonus, initiative, speed, hp, hd):
        # the reason why I don't immediately set level, xp and profBonus to 0 is so that a character can
        # later be added not necessarily at lvl 1, so that he can keep up with the state of the campaign.
        self.lvl = lvl
        self.xp = xp
        self.ins = ins
        self.profBonus = profBonus
        self.initiative = initiative
        self.speed = speed
        self.hp = hp
        self.max_hp = hp
        self.hd = hd
        self.max_hd = 1
        self.strMod = 0
        self.dexMod = 0
        self.constMod = 0
        self.intlMod = 0
        self.wisMod = 0
        self.chaMod = 0
        self.hd_number = 1
        self.lvlUpPoints = 0
        self.armClass = 0
        self.strength = random.randint(1, 20)
        self.dex = random.randint(1, 20)
        self.const = random.randint(1, 20)
        self.intl = random.randint(1, 20)
        self.wis = random.randint(1, 20)
        self.cha = random.randint(1, 20)
        self.spell_slots = {}
        self.curr_used_spell_slots = {}
        self.damage_vulnerabilities = []
        self.damage_resistances = []
        self.damage_immunities = []
        self.setModifiers()

    @classmethod
    def loadStats(cls,
                  lvl, xp, ins, profBonus, initiative, speed, hp, hd,
                  max_hd, strMod, dexMod, constMod, intlMod, wisMod, chaMod, hd_number,
                  lvlUpPoints, strength, dex, const, intl, wis, cha, spell_slots, curr_used_spell_slots,
                  damage_vulnerabilities, damage_resistances, damage_immunities
                  ):
        stats = cls(lvl, xp, ins, profBonus, initiative, speed, hp, hd)
        stats.max_hd = max_hd
        stats.strMod = strMod
        stats.dexMod = dexMod
        stats.constMod = constMod
        stats.intlMod = intlMod
        stats.wisMod = wisMod
        stats.chaMod = chaMod
        stats.hd_number = hd_number
        stats.lvlUpPoints = lvlUpPoints
        stats.strength = strength
        stats.dex = dex
        stats.const = const
        stats.intl = intl
        stats.wis = wis
        stats.cha = cha
        stats.spell_slots = spell_slots
        stats.curr_used_spell_slots = curr_used_spell_slots
        stats.damage_vulnerabilities = damage_vulnerabilities
        stats.damage_resistances = damage_immunities
        stats.damage_immunities = damage_resistances
        return stats

    def setStats(self, race: str, _class: str):
        if race == "human":
            self.strength += 1
            self.dex += 1
            self.const += 1
            self.intl += 1
            self.wis += 1
            self.cha += 1
            self.speed = 30
        elif race == "dwarf":
            self.const = self.const + 2
            self.speed = 25
        elif race == "elf":
            self.dex = self.dex + 2
            self.speed = 30
        elif race == "halfling":
            self.dex = self.dex + 2
            self.speed = 25

        if _class == "fighter":
            self.strength = self.strength + 2
            self.const = self.const + 2
            self.hp = 10 + self.constMod
            self.max_hp = 10 + self.constMod
            self.hd = "d10"
        elif _class == "cleric":
            self.wis = self.wis + 3
            self.hp = 8 + self.constMod
            self.max_hp = 8 + self.constMod
            self.hd = "d8"
            self.spell_slots = {"0": 3, "1": 2, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0}
            self.curr_used_spell_slots = {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0,
                                          "9": 0}
        elif _class == "rogue":
            self.hp = 8 + self.constMod
            self.max_hp = 8 + self.constMod
            self.dex = self.dex + 2
            self.hd = "d8"
        elif _class == "wizard":
            self.intl = self.intl + 2
            self.wis = self.wis + 2
            self.hp = 6 + self.constMod
            self.max_hp = 6 + self.constMod
            self.hd = "d6"
            self.spell_slots = {"0": 3, "1": 2, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0}
            self.curr_used_spell_slots = {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0,
                                          "9": 0}

    def shortRest(self, hd_num: int):
        if hd_num > self.hd_number:
            return "You can't throw more hit dice than you currently have!"
        self.hd_number -= hd_num
        hp = self.constMod
        for i in range(hd_num):
            hp += Dice.roll(self.hd, 0)
        self.hp += hp
        return "Rest was successful."

    def longRest(self, hd_num: int):
        self.hp = self.max_hp  # restore all hp
        if hd_num > self.max_hd / 2:
            return "You can't restore that many hit dice!"
        self.hd_number += hd_num

    def takeDamage(self, damage: []):
        # for now, just takes into account the damage value. If needed, put damage
        # type too (with respective modifier).
        attempt = Dice.roll("d20", 0)
        message = "D20 result: " + str(attempt) + " Player Armor Class: " + str(self.armClass) + "."
        if attempt < self.armClass:
            message += "The attack missed."
            return message
        base_damage = damage[0]
        total_damage = 0
        for i in range(1, len(damage), 2):
            if damage[i + 1] in self.damage_immunities:
                message += " The player is immune to this kind of damage (" + damage[i + 1] + ")."
                pass
            elif damage[i + 1] in self.damage_vulnerabilities:
                message += " Critical damage! The monster is weak to this kind of damage (" + damage[i + 1] + ")."
                total_damage += damage[i] * 2
            elif damage[i + 1] in self.damage_resistances:
                message += " The player is resistant to this kind of damage (" + damage[i + 1] + ")."
                total_damage += damage[i] / 2
            else:
                total_damage += damage[i]
        self.hp = self.hp - (base_damage + total_damage)
        message += " The attack landed. Player remaining health: " + str(self.hp)
        return message

    def heal(self, heal: int):
        self.hp = self.hp + heal

    def addXp(self, xp: int):
        oldXp = self.xp
        self.xp = self.xp + xp

        milestones = [300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000, 100000, 120000,
                      140000, 165000, 195000, 225000, 265000, 305000, 355000]
        for i in milestones:
            if oldXp < i <= self.xp:
                self.lvlUp()

    def lvlUp(self):  # everything that happens when a character levels up.
        self.lvl += 1
        self.hd_number += 1  # player gains one hit die
        self.max_hp += + Dice.roll("d8", 0) + self.constMod  # hp buff from level up
        self.hp += + Dice.roll("d8", 0) + self.constMod
        self.lvlUpPoints += 2

        # every 4 levels from the first, profBonus increases by one. (5/4 = 1 with 1 spare, 9/4 = 2 with 1 spare, ...)
        if self.lvl % 4 == 1:
            self.profBonus += 1

    def lvlUpStats(self, statsUp: []):
        if self.lvlUpPoints == 0:
            return "You can't level up any stats right now!"
        else:
            self.lvlUpPoints -= 2
            for i in range(2):
                if statsUp[i] == "strength":
                    self.strength += 1
                elif statsUp[i] == "dexterity":
                    self.dex += 1
                elif statsUp[i] == "constitution":
                    self.const += 1
                elif statsUp[i] == "intelligence":
                    self.intl += 1
                elif statsUp[i] == "wisdom":
                    self.wis += 1
                elif statsUp[i] == "charisma":
                    self.cha += 1

            self.setModifiers()

    def setModifiers(self):
        self.strMod = int((self.strength - 10) / 2)
        self.dexMod = int((self.dex - 10) / 2)
        self.constMod = int((self.const - 10) / 2)
        self.intlMod = int((self.intl - 10) / 2)
        self.wisMod = int((self.wis - 10) / 2)
        self.chaMod = int((self.cha - 10) / 2)
        self.armClass = 10 + self.dexMod

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value

    def toJson(self):
        return json.dumps(self.__dict__, indent=0, ensure_ascii=False)

    def ordered(self):
        ordered = OrderedDict(self.__dict__)
        return ordered


def loadStats(lvl, xp, ins, profBonus, initiative, speed, hp, hd,
              max_hd, strMod, dexMod, constMod, intlMod, wisMod, chaMod, hd_number,
              lvlUpPoints, strength, dex, const, intl, wis, cha, spell_slots, curr_used_spell_slots,
              damage_vulnerabilities, damage_resistances, damage_immunities) -> Statistics:
    return Statistics.loadStats(lvl, xp, ins, profBonus, initiative, speed, hp, hd,
                                max_hd, strMod, dexMod, constMod, intlMod, wisMod, chaMod, hd_number,
                                lvlUpPoints, strength, dex, const, intl, wis, cha, spell_slots, curr_used_spell_slots,
                                damage_vulnerabilities, damage_resistances, damage_immunities)


def toString(statistics) -> str:
    # Str, Dex, etc... are ABILITIES
    # their modifiers are MODIFIERS
    # ins is INSPIRATION
    # profBonus is proficiency bonus
    oldStats = statistics.ordered()
    new_names = ["Level", "Level up points", "Exp", "Inspiration", "Proficiency bonus", "Initiative", "Speed",
                 "Current health", "Maximum health", "Hit die", "Max amount of hit dice",
                 "Current amount of hit dice held",
                 "Armor class", "Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma",
                 "Strength modifier", "Dexterity modifier", "Constitution modifier", "Intelligence modifier",
                 "Wisdom modifier", "Charisma modifier", "Max spell slots", "Currently used spell slots",
                 "Damage vulnerabilities", "Damage resistances", "Damage immunities"]
    pref_order = ["lvl", "lvlUpPoints", "xp", "ins", "profBonus", "initiative", "speed", "hp", "max_hp", "hd", "max_hd",
                  "hd_number", "armClass",
                  "strength", "dex", "const", "intl", "wis", "cha", "strMod", "dexMod",
                  "constMod", "intlMod", "wisMod", "chaMod", "spell_slots", "curr_used_spell_slots",
                  "damage_vulnerabilities", "damage_resistances", "damage_immunities"]

    stats = dict.fromkeys(new_names)

    for k in pref_order:
        oldStats.move_to_end(k)

    oldStatsItems = list(oldStats.items())
    i = 0
    while i < len(new_names):
        stats[new_names[i]] = oldStatsItems[i][1]
        i += 1

    level = stats["Level"]
    stren = stats["Strength"]
    strMod = stats["Strength modifier"]

    stats = json.dumps(stats, indent=0, ensure_ascii=False)
    stats = stats.replace("{", "")
    stats = stats.replace("}", "")
    stats = stats.replace('"', '')
    stats = stats.replace("[", "")
    stats = stats.replace("]", "")
    stats = stats.replace("Level: " + str(level) + ",", "<b>Base statistics:</b>\nLevel: " + str(level) + ",")
    stats = stats.replace("Strength: " + str(stren) + ",", "\n<b>Abilities:</b>\nStrength: " + str(stren) + ",")
    stats = stats.replace("Strength modifier: " + str(strMod) + ",", "\n<b>Modifiers:</b>\nStrength modifier: " + str(strMod) + ",")
    stats = stats.replace("Max spell slots: ", "\n<b>Spells:</b>\nMax spell slots: ")
    stats = stats.replace("Damage vulnerabilities: ", "\n<b>Damage modifiers:</b>\nDamage vulnerabilities: ")
    return stats


def main():
    stats = Statistics(0, 0, 0, 0, 0, 0, 0, 0)
    stats = toString(stats)
    print(stats)


if __name__ == "__main__":
    main()
