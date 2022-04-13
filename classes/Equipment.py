import Wealth
import Armor
import Weapon


class Equipment:

    wealth = Wealth.Wealth()
    armor = Armor.Armor(None)

    def __init__(self, armor, spellCast, weapons, advGear, tools, mounts, trinkets):
        self.armor = armor,
        self.spellCast = spellCast
        self.weapons = weapons,
        self.advGear = advGear,
        self.tools = tools,
        self.mounts = mounts,
        self.trinkets = trinkets