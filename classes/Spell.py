import json
import os


class Spell:
    def __init__(self, name: str):
        name = name.capitalize()
        self.name = name
        with open(os.path.dirname(os.getcwd()) + "/resources/5e-SRD-Spells.json", "r") as read_file:
            req_eq = json.load(read_file)
        spell = next((spell for spell in req_eq if spell['name'] == name), None)
        if spell:
            self.level = spell["level"]
            self.classes = spell["classes"]  # array of dict of all classes that can be used
            self.desc = spell["desc"]
            if "damage" in spell:
                self.damage_type = spell["damage"]["damage_type"]["name"]
                self.damage_dice = spell["damage"]["damage_at_slot_level"]["3"]

    @classmethod
    def loadSpell(cls, name, level, classes, desc, damage_type, damage_dice):
            spell = Spell(name)
            spell.level = level
            spell.classes = classes
            spell.desc = desc
            if damage_type is not None:
                spell.damage_type = damage_type
            if damage_dice is not None:
                spell.damage_dice = damage_dice
            return spell


def loadSpell(name, level, classes, desc, damage_type, damage_dice):
    return Spell.loadSpell(name, level, classes, desc, damage_type, damage_dice)

    # ritual, cstTime, range, components, duration, aoe

