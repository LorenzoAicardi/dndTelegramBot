import random


class Statistics:

    def __init__(self, lvl, xp, ins, profBonus, initiative, speed, hp, hd):
        # the reason why I don't immediately set level, xp and profBonus to 0 is so that a character can
        # later be added not necessarily at lvl 1, so that he can keep up with the state of the campaign.
        self.lvl = lvl,
        self.xp = xp,
        self.ins = ins,
        self.profBonus = profBonus,
        self.initiative = initiative,
        self.speed = speed,
        self.hp = hp,
        self.hd = hd,
        self.armClass = 0,
        self.strMod = 0,
        self.dexMod = 0,
        self.constMod = 0,
        self.intlMod = 0,
        self.wisMod = 0,
        self.chaMod = 0
        self.strength = random.randint(1, 20)
        self.dex = random.randint(1, 20)
        self.const = random.randint(1, 20)
        self.intl = random.randint(1, 20)
        self.wis = random.randint(1, 20)
        self.cha = random.randint(1, 20)

    def setModifiers(self):
        self.strMod = int((self.strength - 10)/2)
        self.dexMod = int((self.dex - 10)/2)
        self.constMod = int((self.const - 10)/2)
        self.intlMod = int((self.intl - 10)/2)
        self.wisMod = int((self.wis - 10)/2)
        self.chaMod = int((self.cha - 10)/2)
