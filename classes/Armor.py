from dataclasses import dataclass
from typing import Callable
from . import Wealth


@dataclass
class Armor:
    name: str
    cost: Wealth
    armorClass: int
    strength: int
    weight: int

