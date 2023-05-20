import threading

from domain.game import Game
from helpers.grpc_parser import python_cell_to_proto_cell
from domain.player import Player
from helpers.utils import generate_random_string
from proto_stuff.ShipBattle_pb2 import *


class Server:
    def __init__(self, grpc_server):
        self.grpc_server = grpc_server
        self._games: dict[str, Game] = {}
        self._games_queue: list[Game] = []
        self._waiting_for_friend: list[Player] = []

        self.lock = threading.Lock()

    def get_game_from_queue(self, player_id: str) -> Game:
        with self.lock:
            for i in range(len(self._games_queue)):
                if self._games_queue[i].id == player_id:
                    return self._games_queue.pop(i)
            return None

    def get_game_by_id(self, game_id: str) -> Game:
        with self.lock:
            if game_id in self._games:
                return self._games[game_id]
            return None

    def create_game(self, player1: Player, wait_for_friend: bool, game_id: str | None = None):
        player1.id = generate_random_string(10)
        if game_id:
            game = self.get_game_by_id(game_id)
            if game is None:
                return 'no_game_id', None  # TODO

        game = Game(
            player1,
            None,
            10,
        )

        if wait_for_friend:
            with self.lock:
                self._games[game.id] = game
            return player1.id, game.id

        if len(self._games_queue) == 0:
            with self.lock:
                self._games_queue.append(game)
            return player1.id, game.id

        game = self._games_queue.pop(0)

        game.add_second_player(player1)
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
        if key not in self.grpc_server.enemy_moves:
            self.grpc_server.enemy_moves[key] = []
        self.grpc_server.enemy_moves[key].append(
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
