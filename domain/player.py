import dataclasses

from domain.ships import Ship
from helpers.utils import generate_random_string


@dataclasses.dataclass
class Player:
    ships: list[Ship]
    id: str = None

    def __post_init__(self):
        if self.id is None:
            self.id = generate_random_string(10)
