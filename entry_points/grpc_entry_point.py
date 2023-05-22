from concurrent import futures
from time import sleep
import traceback

import grpc

from helpers.grpc_parser import *
from domain.player import Player
from helpers.log import Logger
from proto_stuff.ShipBattle_pb2 import *
from proto_stuff import ShipBattle_pb2_grpc
from services.game_server import Server
from entry_points.base_entry_point import EntryPoint


class BattleshipServiceServicer(ShipBattle_pb2_grpc.BattleshipServiceServicer):
    def __init__(self, logger: Logger, server: Server):
        super().__init__()
        self.logger = logger
        self.server = server

    def listenEvents(self, request_iterator, context):
        for request in request_iterator:
            self.logger.info(request)
            event = request.WhichOneof('event')
            if event == 'create_game_request':
                request = request.create_game_request
                player = Player(
                    ships=[
                        proto_ship_to_python_ship(ship)
                        for ship in request.ships
                    ],
                )
                game_id = request.game_id
                player_id, game_id = self.server.create_game(player, request.wait_for_friend, game_id)
                if player_id is None:
                    yield EventResponse(
                        create_game_response=CreateGameResponse(
                            status=ShipBattle_pb2.CreateGameStatus.Value("GAME_ID_DOENT_EXIST")))
                else:
                    yield EventResponse(
                        create_game_response=CreateGameResponse(
                            game_id=game_id,
                            player_id=player_id,
                            status=ShipBattle_pb2.CreateGameStatus.Value("ADDED_TO_Q")))
                while True:
                    game = self.server.get_game_by_id(game_id)
                    if game is not None:
                        break
                    sleep(1)

                if game.is_current_player(player_id):
                    status = "GAME_STARTED_YOUR_TURN"
                else:
                    status = "GAME_STARTED_ENEMY_TURN"
                yield EventResponse(
                    create_game_response=ShipBattle_pb2.CreateGameResponse(
                        game_id=game_id,
                        player_id=player_id,
                        status=ShipBattle_pb2.CreateGameStatus.Value(status)
                    )
                )

            elif event == 'move_request':
                request = request.move_request
                yield EventResponse(
                    move_response=self.server.make_move(request.game_id, request.player_id, request.point.x,
                                                        request.point.y)
                )

            elif event == 'quit_request':
                request = request.quit_request
                key = f'{request.game_id}{request.player_id}'
                self.server.enemy_moves_q[key].append(
                    EnemyMoveResponse(status=ShipBattle_pb2.EnemyMoveStatus.Value('ENEMY_LEAVE')))
            else:
                raise Exception(f"Unknown event: {event}")

    def listenEnemyMoves(self, request, context) -> EnemyMoveResponse:
        key = f'{request.game_id}{request.player_id}'
        while True:
            while not self.server.enemy_moves_q.get(key):  # TODO брать безопасно
                sleep(1)
            enemy_move = self.server.enemy_moves_q[key].pop(0)
            print(enemy_move)
            yield enemy_move


class GrpcEntryPoint(EntryPoint):
    def __init__(self, logger: Logger, server: Server):
        self.logger = logger
        self.server = server

    def run(self) -> None:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        ShipBattle_pb2_grpc.add_BattleshipServiceServicer_to_server(
            BattleshipServiceServicer(
                self.logger,
                self.server
            ), server
        )
        server.add_insecure_port('[::]:50051')
        server.start()
        self.logger.info("Server started")
        server.wait_for_termination()

    def get_name(self) -> str:
        return 'GrpcEntryPoint'
