import json
import os


class Spell:
    def __init__(self, name):
        self.name = name
        with open(os.path.dirname(os.getcwd()) + "/resources/5e-SRD-Spells.json", "r") as read_file:
            req_eq = json.load(read_file)
        spell = next((spell for spell in req_eq if spell['index'] == name), None)
        if spell:
            self.level = spell["level"]
            self.classes = spell["classes"]  # array of dict of all classes that can be used

    # ritual, cstTime, range, components, duration, aoe
    # TODO: add saving throws, attack rolls
