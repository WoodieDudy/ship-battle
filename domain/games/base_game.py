import abc

from domain.board import Board
from domain.cell import Cell, CellType
from domain.player import Player
from helpers.utils import generate_random_string


class Game(abc.ABC):
    def __init__(
            self,
            player1: Player,
            player2: Player,
            board1: Board,
            board2: Board,
    ):
        assert board1.size == board2.size
        self.id = Game.generate_id()
        self.boards: tuple[Board, Board] = (board1, board2)
        self.player_id_to_board: dict[str, Board] = {
            player1.id: board1,
            player2.id: board2
        }
        self.players_ids: tuple[str, str] = (player1.id, player2.id)
        self.players: list[Player] = [player1, player2]
        self._current_player_id = 0

        self.started = False

    @staticmethod
    def generate_id():
        return generate_random_string(10)

    @abc.abstractmethod
    def give_turn_to_next_player(self): ...

    @staticmethod
    def _shoot(x: int, y: int, board: Board) -> list[Cell]:
        if board.field[y][x].type == CellType.SHIP:
            board.field[y][x].type = CellType.SHIP_HIT
            ship = board.get_ship_by_coords(x, y)
            if ship is not None and ship.is_sunk(board.field):
                return board.get_cells_of_sunken_ship(x, y)
            else:
                return [board.field[y][x]]
        else:
            board.field[y][x].type = CellType.EMPTY_HIT
            return [board.field[y][x]]

    def win_condition(self, board: Board) -> bool:
        return board.all_ships_sunk()

    def get_enemy(self, player_id: str) -> Player:
        return self.players[1 - self.players_ids.index(player_id)]

    def is_current_player(self, player_id: str) -> bool:
        return player_id == self.players_ids[self._current_player_id]

    def make_turn(self, player_id: str, x: int, y: int) -> tuple[list[Cell], bool]:
        enemy_id = self.get_enemy(player_id).id
        board = self.player_id_to_board[enemy_id]
        cells_to_reveal = self._shoot(x, y, board)
        win = self.win_condition(board)
        self.give_turn_to_next_player()
        return cells_to_reveal, win
