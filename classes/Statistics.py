import random


class Statistics:

    def __init__(self, lvl, xp, ins, profBonus, initiative, speed, hp, hd):
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

    def setModifiers(self):  # redo
        if self.strength >= 0:
            self.strMod = self.strMod + 3
        else:
            self.strMod = self.strMod - 3
        if self.dex >= 0:
            self.dexMod = self.dexMod + 3
        else:
            self.dexMod = self.dexMod - 3
        if self.const >= 0:
            self.constMod = self.constMod + 3
        else:
            self.constMod = self.constMod - 3
