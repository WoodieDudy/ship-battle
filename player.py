import dataclasses

from domain.ships import Ship
from classes import ResponseIterator


@dataclasses.dataclass
class Player:
    ships: list[Ship]
    id: str = None
