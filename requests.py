from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from domain.ships import Ship


@dataclass
class BaseRequest:
    game_id: Optional[str]
    player_id: int


@dataclass
class BaseResponse:
    error: Optional[str]


@dataclass
class CreateGameRequest(BaseRequest):
    ships: List[Ship]


@dataclass
class CreateGameResponse(BaseResponse):
    game_id: Optional[int]
    error: Optional[str]


@dataclass
class MoveRequest(BaseRequest):
    game_id: str
    x: int
    y: int


class MoveResult(Enum):
    MISS = 0
    HIT = 1
    SUNK = 2


@dataclass
class MoveResponse:
    result: MoveResult
    updated_field: Optional[List[List[int]]]
    error: Optional[str]
