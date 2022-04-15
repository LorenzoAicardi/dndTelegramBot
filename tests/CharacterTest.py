import unittest
from classes import Character, Weapon, Wealth


class MyTestCase(unittest.TestCase): # IT WORKS!!!!!!!!!
    def test_addItem(self):
        character = Character.Character("123", "Orphos")
        weapon = Weapon.Weapon("Club", Wealth.Wealth(0, 1, 0, 0, 0), "1d4", "Bludgeoning", 2, ["Light", "Monk"])
        character.addItem("Club")
        self.assertEqual(character.equipment.weapons[0].name, "Club")

    def test_rmItem(self):
        character = Character.Character("223", "Orphos")
        character.addItem("Club")
        self.assertEqual(character.rmItem("Club"), "Weapon has been removed successfully!")
        self.assertEqual(character.rmItem("Club"), "No such weapon has been found.")


if __name__ == '__main__':
    unittest.main()
