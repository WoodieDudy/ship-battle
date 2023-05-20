import dataclasses

from domain.ships import Ship


@dataclasses.dataclass
class Player:
    ships: list[Ship]
    id: str = None
