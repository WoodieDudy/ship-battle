from domain.board import Board
from domain.cell import Cell, CellType
from domain.games.base_game import Game
from domain.player import Player


PLAYER = 0
ENEMY = 1


class ClientGame(Game):
    def __init__(
            self,
            player1: Player,
            board_size: int = 10
    ):
        self.board_size = board_size
        player2 = Player([], '2')
        board1 = Board(player1.ships, size=board_size)
        board2 = Board([], CellType.HIDDEN, size=board_size)
        super().__init__(
            player1, player2,
            board1, board2,
        )
        self.player_id = self.players_ids[PLAYER]
        self.enemy_id = self.players_ids[ENEMY]

    def give_turn_to_next_player(self):
        self._current_player_id = 1 - self._current_player_id

    def player_shoot(self, x: int, y: int) -> list[Cell]:
        return self._shoot(x, y, self.player_id_to_board[self.enemy_id])

    def enemy_shoot(self, x: int, y: int) -> list[Cell]:
        return self._shoot(x, y, self.player_id_to_board[self.player_id])

    def make_player_turn(self, x: int, y: int) -> list[Cell]:
        cells_to_reveal = self.player_shoot(x, y)
        self.give_turn_to_next_player()
        return cells_to_reveal

    def make_enemy_turn(self, x: int, y: int) -> list[Cell]:
        cells_to_reveal = self.enemy_shoot(x, y)
        self.give_turn_to_next_player()
        return cells_to_reveal

    def reveal_enemy_hit_cells(self, cells: list[Cell]):
        for cell in cells:
            self.player_id_to_board[self.enemy_id][cell.y][cell.x].type = cell.type

    def reveal_my_cells(self, cells: list[Cell]):
        for cell in cells:
            self.player_id_to_board[self.player_id][cell.y][cell.x].type = cell.type
