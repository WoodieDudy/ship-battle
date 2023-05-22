from domain.board import Board
from domain.cell import Cell
from domain.games.base_game import Game
from domain.player import Player


class ServerGame(Game):
    def __init__(
            self,
            player1: Player,
            player2: Player,
            board_size: int = 10
    ):
        self.board_size = board_size
        board1 = Board(player1.ships, size=board_size)
        board2 = Board(player2.ships, size=board_size)
        super().__init__(
            player1, player2,
            board1, board2,
        )

    def get_enemy(self, player_id: str) -> Player:
        return self.players[1 - self.players_ids.index(player_id)]

    def is_current_player(self, player_id: str) -> bool:
        return player_id == self.players_ids[self._current_player_id]

    def give_turn_to_next_player(self, revealed_cells: list[Cell]):
        if len(revealed_cells) <= 1:
            self._current_player_id = 1 - self._current_player_id
