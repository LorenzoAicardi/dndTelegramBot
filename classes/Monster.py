import yaml

from . import Dice
import os
import json
import re

from .JSONEncoder import MyEncoder


class Monster:
    # needs a size to determine hit die
    armorClass = 0
    hp = 0
    hd = 0
    speed = []
    strength = 0
    dex = 0
    const = 0
    intl = 0
    wis = 0
    cha = 0
    proficiencies = dict()
    senses = []
    languages = []
    challenge = 0
    damage_vulnerabilities = []
    damage_resistances = []
    damage_immunities = []
    actions = []  # array of dictionaries, one for each action

    def __init__(self, name: str):
        name = name.capitalize()
        self.name = name
        with open(os.path.dirname(os.getcwd()) + "/resources/5e-SRD-Monsters.json", "r") as read_file:
            req_eq = json.load(read_file)
        monster = next((monster for monster in req_eq if monster['name'] == name), None)
        if monster:
            self.hp = monster["hit_points"]
            self.hd = monster["hit_dice"]
            self.speed = monster["speed"]
            self.strength = monster["strength"]
            self.dex = monster["dexterity"]
            self.const = monster["constitution"]
            self.intl = monster["intelligence"]
            self.wis = monster["wisdom"]
            self.cha = monster["charisma"]
            self.proficiencies = monster["proficiencies"]
            self.senses = monster["senses"]
            self.languages = monster["languages"]
            self.challenge = monster["challenge_rating"]
            self.actions = monster["actions"]
            self.damage_vulnerabilities = monster["damage_vulnerabilities"]
            self.damage_resistances = monster["damage_resistances"]
            self.damage_immunities = monster["damage_immunities"]
        else:
            pass

    @classmethod
    def loadMonster(cls, name, hp, hd, speed, strength, dex, const, intl, wis, cha, proficiencies, senses,
                    languages, challenge, actions, damage_vulnerabilities, damage_resistances, damage_immunities):
        monster = cls(name)
        monster.hp = hp
        monster.hd = hd
        monster.speed = speed
        monster.strength = strength
        monster.dex = dex
        monster.const = const
        monster.intl = intl
        monster.wis = wis
        monster.cha = cha
        monster.proficiencies = proficiencies
        monster.senses = senses
        monster.languages = languages
        monster.challenge = challenge
        monster.actions = actions
        monster.damage_vulnerabilities = damage_vulnerabilities
        monster.damage_resistances = damage_resistances
        monster.damage_immunities = damage_immunities
        return monster

    def takeDamage(self, damage: []):
        attempt = Dice.roll("d20", 0)
        message = "D20 result: " + str(attempt) + " " +  self.name + " Armor Class: " + str(self.armorClass) + "."
        if attempt < self.armorClass:  # if a player rolls an attack role below the target's AC, the attack fails
            message += " Your attack missed."
            return message
        message += " Previous hp: " + str(self.hp)
        if damage[1] in self.damage_vulnerabilities:
            self.hp = self.hp - (damage[0] * 2)
            message += " Critical damage! The monster is weak to this kind of damage (" + damage[1] + ")."
        elif damage[1] in self.damage_resistances:
            self.hp = self.hp - (damage[0] / 2)
            message += " The monster is resistant to this kind of damage (" + damage[1] + ")."
        elif damage[1] in self.damage_immunities:
            message += " The monster is immune to this kind of damage (" + damage[1] + ")."
            pass
        else:
            self.hp = self.hp - damage[0]
        message += " The attack landed. Monster remaining health: " + str(self.hp) + "."
        return message

    def takeDamageAdv(self, damage: [], adv: bool):
        # True for advantage, False for disadvantage.
        if adv:
            attempt1 = Dice.roll("d20", 0)
            attempt2 = Dice.roll("d20", 0)
            message = "First roll result: " + str(attempt1) + ", second roll result: " + str(attempt2) + "."
            if attempt2 > attempt1:
                attempt = attempt2
                message += " Using " + str(attempt) + ". "
            else:
                attempt = attempt1
                message += " Using " + str(attempt) + ". "
            message += "D20 result: " + str(attempt) + " " + self.name + " Monster Armor Class: " + str(self.armorClass) + "."
            if attempt < self.armorClass:  # if a player rolls an attack role below the target's AC, the attack fails
                message += " Your attack missed."
                return message
        else:
            attempt1 = Dice.roll("d20", 0)
            attempt2 = Dice.roll("d20", 0)
            message = " First roll result: " + str(attempt1) + ", second roll result: " + str(attempt2) + ". "
            if attempt2 < attempt1:
                attempt = attempt2
                message += "Using " + str(attempt) + ". "
            else:
                attempt = attempt1
                message += "Using " + str(attempt) + ". "
            message += "D20 result: " + str(attempt) + self.name + " Armor Class: " + str(self.armorClass) + "."
            if attempt < self.armorClass:  # if a player rolls an attack role below the target's AC, the attack fails
                message += " Your attack missed."
                return message

        if damage[1] in self.damage_vulnerabilities:
            message += " Critical damage! The monster is weak to this kind of damage (" + damage[1] + ")."
            self.hp = self.hp - (damage[0] * 2)
        elif damage[1] in self.damage_resistances:
            self.hp = self.hp - (damage[0] / 2)
            message += " The monster is resistant to this kind of damage (" + damage[1] + ")."
        elif damage[1] in self.damage_immunities:
            message += " The monster is immune to this kind of damage (" + damage[1] + ")."
            pass
        else:
            self.hp = self.hp - damage[0]
        message += " Monster remaining health: " + str(self.hp) + "."
        return message

    def heal(self, heal: int):
        self.hp = self.hp + heal

    def attack(self, action: str):
        act = next((act for act in self.actions if act['name'] == action), None)
        if act:
            initial_damage = act["attack_bonus"]
            bonus_damage = []
            damage_type = []
            damage_dice = []
            damage = [initial_damage]
            for i in range(len(act["damage"])):
                dmg_type = act["damage"][i]["damage_type"]["index"]
                damage_type.append(dmg_type)  # list that has all the damage types dealt
                dmg_dice = act["damage"][i]["damage_dice"]
                damage_dice.append(dmg_dice)  # list that has all the damage dice.
            for i in range(len(damage_dice)):  # I iterate over all the instances of damage dealt.
                bonus_damage.append(0)
                tmp = damage_dice[i].split("+")
                if len(tmp) == 2:
                    mod = int(tmp[1])
                else:
                    mod = 0
                tmp2 = tmp[0].split("d")
                numOfTimes = int(tmp2[0])  # numOfTimes is 3
                dice = "d" + str(tmp2[1])  # the dice is the number after the d
                for j in range(numOfTimes):  # I roll the dice numberOfTimes times.
                    bonus_damage[i] += Dice.roll(dice, 0)
                bonus_damage[i] += mod
            for i in range(len(damage_type)):
                damage += [bonus_damage[i], damage_type[i]]
            if len(damage) % 2 == 0:
                return "Something went wrong: list has an even number of items!"
            else:
                return damage

    def multiAttack(self, attacks: []):  # inputs the same action twice in a row if necessary
        multiAttack = next((act for act in self.actions if act['name'] == "Multiattack"), None)
        if multiAttack:
            if len(attacks) != multiAttack["options"]["choose"]:
                return "You can't do that many attacks."
            else:
                damage = []
                for i in range(multiAttack["options"]["choose"]):
                    damage += self.attack(attacks[i]) + "***"  # end of first attack
                return damage

    def roll(self, dice: str, mod: int):
        res = Dice.roll(dice, mod)
        return res

    def toJson(self):
        return json.dumps(self.__dict__, sort_keys=True, indent=4, ensure_ascii=False)


def loadMonster(name, hp, hd, speed, strength, dex, const, intl, wis, cha, proficiencies, senses,
                languages, challenge, actions, damage_vulnerabilities, damage_resistances,
                damage_immunities) -> Monster:
    return Monster.loadMonster(name, hp, hd, speed, strength, dex, const, intl, wis, cha, proficiencies, senses,
                               languages, challenge, actions, damage_vulnerabilities, damage_resistances,
                               damage_immunities)


def toString(monster: Monster):
    m = json.loads(MyEncoder().encode(monster).replace("\"", '"'))
    for item in m["actions"]:
        if "damage" in item:
            for i in item["damage"]:
                del i["damage_type"]["index"]
                del i["damage_type"]["url"]

    if "proficiencies" in m:
        for item in m["proficiencies"]:
            # for i in item["proficiency"]:
            #     del i["index"]
            #     del i["url"]
            del item["proficiency"]["index"]
            del item["proficiency"]["url"]
    m = yaml.safe_dump(m, sort_keys=False, allow_unicode=True, default_flow_style=False)
    m = m.replace("name", "Name")
    m = m.replace("desc", "<i>Description</i>")
    m = m.replace("speed", "Speed")
    m = m.replace("damage", "Damage")
    m = m.replace("damage_type", "Damage type")
    m = m.replace("damage_dice", "Damage dice")
    m = m.replace("damage_vulnerabilities", "Damage vulnerabilities")
    m = m.replace("damage_resistances", "Damage resistances")
    m = m.replace("damage_immunities", "Damage immunities")
    m = m.replace("hp", "Hit points")
    m = m.replace("hd", "Hit dice")
    m = m.replace("strength", "\nStrength")
    m = m.replace("dex", "Dexterity")
    m = m.replace("proficiencies", "\n<b>Proficiencies</b>")
    m = m.replace("senses", "<b>Senses</b>")
    m = m.replace("languages", "<b>Languages</b>")
    m = m.replace("challenge", "<b>Challenge</b>")
    m = m.replace("const", "Constitution")
    m = m.replace("actions", "\n<b>Actions</b>")
    m = m.replace("intl", "Intelligence")
    m = m.replace("wis", "Wisdom")
    m = m.replace("cha", "Charisma", 1)
    m = m.replace("[]", "None")
    return m
