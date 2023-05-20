from dataclasses import dataclass
from enum import IntEnum


class CellType(IntEnum):
    EMPTY = 0
    EMPTY_HIT = 1
    SHIP_HIT = 2
    SHIP = 3
    HIDDEN = 4


@dataclass
class Cell:
    x: int
    y: int
    type: CellType
