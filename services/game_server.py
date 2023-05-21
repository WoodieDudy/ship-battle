import threading
from typing import Optional

from domain.games.server_game import ServerGame
from helpers.grpc_parser import python_cell_to_proto_cell
from domain.player import Player
from helpers.log import Logger
from proto_stuff.ShipBattle_pb2 import *


class Server:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.enemy_moves_q: dict[str, list[EnemyMoveResponse]] = {}
        self._games: dict[str, ServerGame] = {}
        self._players_q: list[tuple[str, Player]] = []
        self._waiting_for_friend: list[Player] = []

        self.lock = threading.Lock()

    # def get_player_game_from_q(self, player_id: str) -> Optional[Game]:
    #     with self.lock:
    #         for i in range(len(self._players_q)):
    #             if self._players_q[i].id == player_id:
    #                 return self._players_q.pop(i)
    #         return None

    def get_game_by_id(self, game_id: str) -> Optional[ServerGame]:
        with self.lock:
            if game_id in self._games:
                return self._games[game_id]
        return None

    def create_game(self, player1: Player, wait_for_friend: bool, game_id_to_connect: Optional[str] = None):
        if game_id_to_connect:
            game = self.get_game_by_id(game_id_to_connect)
            if game is None:
                return None, None

        if wait_for_friend:
            game_id = ServerGame.generate_id()
            with self.lock:
                self._players_q.append((game_id, player1))
            return player1.id, game_id

        with self.lock:
            if len(self._players_q) == 0:
                game_id = ServerGame.generate_id()
                self._players_q.append((game_id, player1))
                return player1.id, game_id

        game_id, player2 = self._players_q.pop(0)

        game = ServerGame(
            player1,
            player2,
            board_size=10,
        )
        game.id = game_id
        with self.lock:
            self._games[game.id] = game
        return player1.id, game.id

    def make_move(self, game_id: str, player_id: str, x: int, y: int) -> MoveResponse:
        game = self._games.get(game_id)
        if game is None:
            return MoveResponse(status=MoveStatus.Value("GAME_NOT_STARTED"))

        if not game.is_current_player(player_id):
            return MoveResponse(status=MoveStatus.Value("NOT_YOUR_TURN"))

        cells_to_reveal, win = game.make_turn(player_id, x, y)
        if win:
            status = MoveStatus.Value("WIN")
            status_for_enemy = EnemyMoveStatus.Value("ENEMY_WIN")
        else:
            status = MoveStatus.Value("TURN")
            status_for_enemy = EnemyMoveStatus.Value("ENEMY_TURN")

        enemy_id = game.get_enemy(player_id).id
        key = f'{game_id}{enemy_id}'
        if key not in self.enemy_moves_q:
            self.enemy_moves_q[key] = []
        self.enemy_moves_q[key].append(
            EnemyMoveResponse(
                status=status_for_enemy,
                point=Point(x=x, y=y),
            )
        )
        return MoveResponse(
            status=status,
            revealed_cells=[
                python_cell_to_proto_cell(cell)
                for cell in cells_to_reveal
            ]
        )
