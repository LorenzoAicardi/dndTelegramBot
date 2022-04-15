from . import Wealth
from . import Armor
from . import Weapon


class Equipment:

    def __init__(self):
        self.wealth = Wealth.Wealth(0, 0, 0, 0, 0)
        self.armor = []
        self.weapons = []
        self.spellCast = []
        self.advGear = []
        self.tools = []
        self.mounts = []
        self.trinkets = []

    #def appendArmor, appendWeapon
