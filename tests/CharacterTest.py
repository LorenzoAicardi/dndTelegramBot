import unittest
from classes import Character, Weapon, Wealth


class MyTestCase(unittest.TestCase):  # IT WORKS!!!!!!!!!
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

    def test_useWeapon(self):
        character = Character.Character("223", "Orphos")
        character.addItem("Club")
        testlist = [0, "Bludgeoning"]
        self.assertEqual(testlist[1], character.useWeapon("Club", 0)[1])
        character.rmItem("Club")
        self.assertEqual("No such weapon in inventory.", character.useWeapon("Club", 0))

    def testAddSpell(self):
        character = Character.Character("223", "Orphos")
        character.setInitialStats("human", "wizard")
        self.assertEqual("Spell has been added successfully!", character.addSpell("alarm"))
        self.assertEqual("The chosen spell can't be added to a character of this class!", character.addSpell("hellish-rebuke"))
        self.assertEqual("Spell has been added successfully!", character.addSpell("identify"))
        self.assertEqual("You can't add that many spells!", character.addSpell("magic-missile"))

    def testShortRest(self):
        character = Character.Character("223", "Orphos")
        character.setInitialStats("human", "cleric")
        self.assertEqual("Rest was successful.", character.stats.shortRest(0))


if __name__ == '__main__':
    unittest.main()
