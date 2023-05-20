from board import Board
from core import Cell, CellType
from player import Player
from utils import generate_random_string


class Game:
    def __init__(
            self,
            player1: Player,
            player2: Player,
            board_size: int = 10
    ):
        self.id = generate_random_string(10)
        if player2 is None:
            player2 = Player([], '2')
            board2 = Board(player2.ships, CellType.HIDDEN, board_size, )
        else:
            board2 = Board(player2.ships, size=10)

        self.players_ids: tuple[str, str] = (player1.id, player2.id)
        self.players: tuple[Player, Player] = (player1, player2)
        self.boards = (Board(player1.ships, size=board_size), board2)
        self._current_player_id = 0

        self.player_id = None
        self.start = False  # TODO

    def get_enemy(self, player_id: str) -> Player:
        return self.players[1 - self.players_ids.index(player_id)]

    def is_current_player(self, player_id: str) -> bool:
        return player_id == self.players_ids[self._current_player_id]

    def give_turn_to_next_player(self):
        self._current_player_id = 1 - self._current_player_id

    # вынести
    @staticmethod
    def _win_condition(board: Board) -> bool:
        return board.all_ships_sunk()

    def make_player_turn(self, x: int, y: int) -> tuple[list[Cell], bool]:
        board = self.boards[1]
        cells_to_reveal = board.shoot(x, y)
        win = self._win_condition(board)
        self.give_turn_to_next_player()
        return cells_to_reveal, win

    def make_enemy_turn(self, x: int, y: int):
        board = self.boards[0]
        cells_to_reveal = board.shoot(x, y)
        win = self._win_condition(board)
        self.give_turn_to_next_player()
        return cells_to_reveal, win

    def reveal_enemy_hit_cells(self, cells: list[Cell]):
        for cell in cells:
            self.boards[1][cell.y][cell.x].type = cell.type

    def reveal_my_cells(self, cells: list[Cell]):
        for cell in cells:
            self.boards[0][cell.y][cell.x].type = cell.type

    def make_turn(self, player_id: str, x: int, y: int) -> tuple[list[Cell], bool]:
        if self.players_ids.index(player_id) == 0:
            cells_to_reveal, win = self.make_player_turn(x, y)
            return cells_to_reveal, win
        else:
            cells_to_reveal, win = self.make_enemy_turn(x, y)
            return cells_to_reveal, win

    def add_second_player(self, player: Player):
        self.players_ids = (self.players_ids[0], player.id)
        self.players = (self.players[0], player)
        self.boards = (self.boards[0], Board(player.ships, size=10))
