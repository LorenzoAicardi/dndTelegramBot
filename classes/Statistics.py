class Statistics:
    def __init__(self, lvl, xp, str, dex, const, intl, wis, cha, ins, profBonus, initiative, armClass, speed, hp, hd, deathSaves):
        self.lvl = lvl,
        self.xp = xp,
        self.str = str,
        self.dex = dex,
        self.const = const,
        self.intl = intl,
        self.wis = wis,
        self.cha = cha,
        self.ins = ins,
        self.armClass = armClass,
        self.profBonus = profBonus,
        self.initiative = initiative,
        self.speed = speed,
        self.hp = hp,
        self.hd = hd,
        self.deathSaves = deathSaves

    def getSpeed(self):
        return self.speed
