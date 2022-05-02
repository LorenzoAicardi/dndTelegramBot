import unittest
from classes import Character
from classes import Monster


class MyTestCase(unittest.TestCase):
    def test_takeDamage(self):  # TODO: COMPLETE
        character = Character.Character("123", "Orphos")
        character.addItem("club")
        monster = Monster.Monster("ape")
        dmg = character.useWeapon("club", 0)
        monster.takeDamage(dmg)
        self.assertEqual()


if __name__ == '__main__':
    unittest.main()
