from dataclasses import dataclass
from typing import Callable
from classes import Wealth
# import Wealth


@dataclass
class Armor:
    name: str
    cost: Wealth
    armorClass: int
    strength: int
    weight: int
