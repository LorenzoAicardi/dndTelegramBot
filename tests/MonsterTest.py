import unittest
from classes import Character
from classes import Monster


class MyTestCase(unittest.TestCase):
    def test_takeDamage(self):  # TODO: COMPLETE
        dmg = [10, "bludgeoning"]
        monster = Monster.Monster("ape")
        monster.takeDamage(dmg)
        self.assertEqual(9, monster.hp)

    def test_attack(self):
        monster2 = Monster.Monster("balor")
        damage2 = monster2.attack("Whip")
        expected_dmg2 = [14, 15, "slashing", 12, "fire"]
        self.assertEqual(expected_dmg2, damage2)


if __name__ == '__main__':
    unittest.main()
