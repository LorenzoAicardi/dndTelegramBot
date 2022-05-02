from . import Dice
import os
import json


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

    def __init__(self, name):
        self.name = name
        with open(os.path.dirname(os.getcwd()) + "/resources/5e-SRD-Monsters.json", "r") as read_file:
            req_eq = json.load(read_file)
        monster = next((monster for monster in req_eq if monster['index'] == name), None)
        if monster:
            self.hp = monster["hit_points"]
            self.hd = monster["hit_dice"]
            self.speed = monster["speed"]
            self.strength = monster["strength"]
            self.dex = monster["constitution"]
            self.const = monster["dexterity"]
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

    def takeDamage(self, damage: []):
        attempt = Dice.roll("d20", 0)
        if attempt < self.armorClass:  # if a player rolls an attack role below the target's AC, the attack fails
            return "Your attack missed."
        if damage[1] in self.damage_vulnerabilities:
            self.hp = self.hp - (damage[0]*2)
        elif damage[1] in self.damage_resistances:
            self.hp = self.hp - (damage[0]/2)
        elif damage[1] in self.damage_immunities:
            pass
        else:
            self.hp = self.hp - damage[0]

    def heal(self, heal: int):
        self.hp = self.hp + heal

    def attack(self, action: str):
        act = next((act for act in self.actions if act['name'] == action), None)
        if act:
            initial_damage = act["attack_bonus"]
            bonus_damage = []
            damage_type = []
            damage_dice = []
            damage = []
            for i in range(act["damage"]):
                damage_type += act["damage"][i]["damage_type"]["index"]
                damage_dice += act["damage"][i]["damage_dice"]
            for i in range(len(damage_dice)):
                bonus_damage[i] = 0
                tmp = damage_dice[i].split("+")
                mod = int(tmp[1])
                tmp2 = tmp.split("d")
                numOfTimes = int(tmp2[0])
                dice = "d".join(tmp2[1])
                for j in range(numOfTimes):
                    bonus_damage[i] += Dice.roll(dice, mod)
            damage += initial_damage
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

    def json(self):
        return json.dumps(self.__dict__)

    # def dealDamage
